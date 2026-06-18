# Research: subset-b-007680

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/hddspacemgr.h -->
# sources/distributed-fs/moosefs/mfschunkserver/hddspacemgr.h

## Purpose
`hddspacemgr.h` is the public chunkserver storage interface. It hides disk layout, chunk metadata scanning, damaged/lost/new/changed chunk queues, and all local chunk I/O behind a compact API consumed by `masterconn.c`, `mainserv.c`, `replicator.c`, background jobs, and startup code. The header is intentionally broad: it is both the synchronous data plane for client reads/writes and the control plane for master registration and disk-health reporting.

## Important APIs, types, and functions
The statistics group exposes byte counters, operation counters, chart data, error counts, and `hdd_sendingchunks()`. Master integration uses lock-paired query/fill calls such as `hdd_get_damaged_chunk_count()` plus `hdd_get_damaged_chunk_data()`, `hdd_get_lost_chunk_count()` plus `hdd_get_lost_chunk_data()`, and similar pairs for new, changed, nonexistent, and disk-info reports. The comments are important: these calls must be paired because the count call acquires state that the data call fills and releases.

Data-plane APIs are `hdd_open()`, `hdd_close()`, `hdd_read()`, `hdd_write()`, `hdd_precache_data()`, `hdd_emergency_read()`, and `hdd_get_chunk_info()`. Chunk mutation is centralized through `hdd_chunkop()`, with macros for delete, create, test, replication-local create/delete, version change, truncate, duplicate, and duplicate-truncate. Replication has a special `hdd_rep_setversion()` promotion path.

## Control flow and state
The header implies three storage lifecycles. Startup calls `hdd_init()`, optional `hdd_restore()`, then `hdd_late_init()` for storage worker threads. Master registration calls `hdd_get_chunks_begin()`, repeated next-list calls, then `hdd_get_chunks_end()`. Client/replication I/O opens a chunk, reads/writes blocks, then closes with optional fsync.

## Persistence behavior
Persistent state includes chunk files, chunk versions, on-disk metadata IDs via `hdd_setmetaid()`, disk-space accounting, damaged/lost/new/changed queues, and restored chunk metadata. Macros intentionally encode mutation semantics into one operation call, which reduces exported surface but makes argument validation critical.

## Dependencies and integration points
The only included MooseFS protocol dependency is `MFSCommunication.h`, mainly for block/chunk constants and status codes. `masterconn.c` consumes registration/reporting APIs, `mainserv.c` consumes client read/write APIs, and `replicator.c` consumes replication create/delete/version/write APIs.

## Risks and test signals
The lock-pair contract is easy to misuse: failing to call the paired data function can leave storage-report state locked. Tests should exercise every report path with zero and nonzero counts. Mutation macros should be tested for invalid sentinel combinations, especially `0xFFFFFFFF` length and zero/nonzero `newversion`. Data-plane tests should verify close behavior with and without fsync, error propagation from `hdd_open/read/write`, and that replication-created version-0 chunks are cleaned or promoted correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/hddspacemgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/init.h -->
# sources/distributed-fs/moosefs/mfschunkserver/init.h

## Purpose
`init.h` defines the chunkserver module startup order through three static run tables: normal init, late init, and restore. It is not a conventional declaration-only header; it includes module headers and instantiates `RunTab`, `LateRunTab`, and `RestoreRunTab` arrays for the shared MooseFS main framework.

## Important APIs, types, and functions
The local `runfn` type is `int (*)(void)`. `RunTab` calls, in order, `rnd_init`, `hdd_init`, `mainserv_init`, `job_init`, `csserv_init`, `masterconn_init`, and `chartsdata_init`. A comment notes `csserv_init` must run before `masterconn_init`, which is necessary because registration advertises the chunkserver listen address. `LateRunTab` starts `hdd_late_init`, and `RestoreRunTab` calls `hdd_restore`.

## Control flow and state
Startup is table-driven: the common daemon launcher iterates these arrays until the sentinel `{0, "****"}`. The order makes storage available before client/master serving, creates internal main-server support before the acceptor, and registers with the master after the acceptor can report its listen endpoint.

## Persistence behavior
Persistence is delegated to `hdd_init`, `hdd_restore`, and `hdd_late_init`. This file's key persistence role is sequencing: restore happens via a dedicated restore run table and storage threads start late rather than during the initial storage scan.

## Dependencies and integration points
This file includes `bgjobs`, `random`, `hddspacemgr`, `masterconn`, `csserv`, `mainserv`, and `chartsdata`. It also defines empty module option macros, so option handling is inherited from shared infrastructure without module-specific getopt entries.

## Risks and test signals
Order regressions are the main risk. If `masterconn_init` runs before `csserv_init`, registration can advertise invalid listen data. If `job_init` is too late, master-issued work may not enqueue. Startup tests should verify module order, failure propagation when any init returns error, restore-mode behavior, and that late init runs after normal init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/mainserv.c -->
# sources/distributed-fs/moosefs/mfschunkserver/mainserv.c

## Purpose
`mainserv.c` implements the chunkserver-to-client and chunkserver-to-chunkserver data path used for direct reads, chained writes, and write forwarding. It wraps socket I/O with statistics, keepalive NOP handling, bounded packet sizes, optional `mmap` packet allocation, and calls into `hddspacemgr` for local chunk access.

## Important APIs, types, and functions
Public entry points are `mainserv_stats()`, `mainserv_read()`, `mainserv_write()`, and `mainserv_init()`. Internal helpers include `mainserv_create_packet()`, `mainserv_send_and_free()`, `mainserv_connect()`, and socket accounting wrappers around `tcptoread`, `tcptowrite`, and `tcptoforward`.

Protocol keepalives are tracked with `sock_nops` objects and the `mainserv_sock_nop_sender()` thread, which periodically writes `ANTOAN_NOP` packets to sockets registered during long operations. Write forwarding uses `write_job` and `write_xchg`; `mainserv_write_thread()` performs local HDD writes while the main thread forwards packets and reads downstream status.

## Control flow
`mainserv_read()` validates request size, optional protocol version, chunk id, version, offset, and size. It returns immediate status for zero-length reads and bounds errors. For real reads, it opens the chunk, precaches data, then emits one `CSTOCL_READ_DATA` packet per block segment, followed by `CSTOCL_READ_STATUS` with `MFS_STATUS_OK`. During streaming it tolerates incoming `ANTOAN_NOP` packets from the peer and aborts on other input.

`mainserv_write()` parses `CLTOCS_WRITE`, optional protover 1, chunk/version, and an optional chain of downstream chunkservers. If forwarding is required, it connects to the next peer with retries, sends a shortened write-init packet, opens the local chunk, and enters `mainserv_write_middle()`. The middle-node path forwards incoming write-data/finish/NOP packets downstream, enqueues local disk writes to a worker thread, matches downstream `CSTOCL_WRITE_STATUS` packets by write id, and only acknowledges upstream when both local and downstream outcomes are known. If no downstream peer exists, `mainserv_write_last()` writes locally and acknowledges each write id directly.

## State and persistence behavior
The file maintains process-local counters for bytes in/out and high-level read/write operation counts. Persistent mutation happens through `hdd_open`, `hdd_write`, and `hdd_close`; `mainserv_write()` currently closes with `forcefsync` set to zero and a TODO notes fsync should be controllable. Forwarded writes can reuse downstream connections through `conncache` only when the operation fully completes under protover 1.

## Dependencies and integration points
Major dependencies are `MFSCommunication.h` command/status constants, `sockets` timeout helpers, `cfg`, `mfslog`, `datapack`, `hddspacemgr`, `lwthread`, `clocks`, `portable`, optional `conncache`, and optional `mmap`. It is initialized from `init.h` before `csserv`, while the acceptor dispatches client packets to `mainserv_read()` and `mainserv_write()`.

## Risks and test signals
The write-middle path is high risk because it coordinates three event sources: upstream socket, downstream socket, and local HDD worker pipe. Tests should cover mismatched chunk id/version, downstream status before/after local status, partial forward failure, timeout, NOP interleaving, and worker-thread error propagation. Read tests should cover boundary offsets, multi-block reads, zero-length reads, and injected `hdd_read` failures. Build tests should also cover `HAVE_MMAP` because the fallback `myunalloc` macro uses `free(size)` in the non-mmap branch, which looks suspicious and should be compiled or statically checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/mainserv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/mainserv.h -->
# sources/distributed-fs/moosefs/mfschunkserver/mainserv.h

## Purpose
`mainserv.h` exposes the small public surface of the chunkserver main data service: stats collection, packet-level read/write handlers, and initialization.

## Important APIs
`mainserv_stats()` returns and resets byte and high-level operation counters. `mainserv_read()` and `mainserv_write()` accept a connected socket plus a parsed packet payload and length; they return a boolean-like `uint8_t` success indicator. `mainserv_init()` starts service-level state such as connection cache and NOP sender support.

## Control flow and integration
The header is used by `init.h` for startup and by the chunkserver acceptor/dispatcher for client commands. It deliberately does not expose write-chain internals, packet allocation helpers, or socket keepalive machinery.

## State and persistence behavior
The header itself owns no state. Its functions operate against `mainserv.c` process globals and the persistent chunk store exposed by `hddspacemgr`.

## Risks and test signals
Because `mainserv_read()` and `mainserv_write()` return only success/failure, callers must rely on sent protocol status packets for detailed errors. Integration tests should verify that caller disconnect behavior matches these return values and that stats reset semantics are documented for charts consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/mainserv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/masterconn.c -->
# sources/distributed-fs/moosefs/mfschunkserver/masterconn.c

## Purpose
`masterconn.c` is the chunkserver's single connection state machine for the MooseFS master. It handles discovery, nonblocking connect, authentication, registration, periodic load/space/report traffic, master-issued chunk operations, replication commands, idle checksum/block queries, reconnect/reload, and graceful unregister on shutdown.

## Important APIs, types, and functions
The central `masterconn` struct stores socket mode, poll position, input/output queues, resolved master address, timeout, connection counter, master version, registration state, and authentication challenge data. Packet queues are represented by `in_packetstruct` and `out_packetstruct`. Long-running query state is held in linked `idlejob` nodes.

Public functions include `masterconn_stats()`, `masterconn_getcsid()`, `masterconn_getmetaid()`, `masterconn_gethddmetaid()`, `masterconn_sethddmetaid()`, master address accessors, `masterconn_reportload()`, `masterconn_forcereconnect()`, and `masterconn_init()`. Internal handlers include `masterconn_master_ack()`, `masterconn_sendregister()`, `masterconn_sendnextchunks()`, report senders, operation handlers (`create`, `delete`, `setversion`, `duplicate`, `truncate`, `duptrunc`, `chunkop`, local split), replication handlers, idle checksum handlers, and poll-loop functions.

## Control flow
Initialization loads persisted `chunkserverid.mfs`, reads config (`MASTER_HOST`, `MASTER_PORT`, `BIND_HOST`, `MASTER_TIMEOUT`, `AUTH_CODE`, labels, registration batch size), allocates a singleton, starts a nonblocking connection, and registers main-loop hooks. On connect, `masterconn_connected()` initializes queues and sends `CSTOMA_REGISTER` type 60 with version, listen address, timeout, chunkserver id, and disk-space counters, optionally with an MD5 challenge response.

`masterconn_master_ack()` drives registration. ACK type 0 accepts registration progress: it validates master version and metadata id, persists chunkserver id/meta id when supplied, starts partial chunk listing with `hdd_get_chunks_begin(1)`, sends labels for new masters, and streams chunk lists as `CSTOMA_REGISTER` type 61 until type 62 marks completion and `REGISTERED`. ACK type 2 moves to `WAITING`, and type 3 carries an auth random blob.

The poll loop is split into `masterconn_desc()` and `masterconn_serve()`. Reads assemble framed packets into an input queue, `masterconn_parse()` processes queued packets for up to about 10 ms per loop, writes drain output packets via `writev` when available, and idle connections send `ANTOAN_NOP`. Timeouts and socket errors transition to `KILL`, while `CLOSE` flushes queued unregister output.

## State and persistence behavior
`chunkserverid.mfs` persists the 16-bit chunkserver id and 64-bit metadata id. Metadata id mismatches against either the persisted id or HDD-discovered id are fatal to prevent cross-cluster attachment. HDD persistent state is reported through space, damaged, lost, new, changed, and nonexistent chunk queues. Master-issued operations are delegated to background jobs, guarded with `busychunk_start/end`, and replies are dropped if the connection counter no longer matches, preventing stale callbacks from writing to a new session.

## Dependencies and integration points
The module integrates with `hddspacemgr`, `bgjobs`, `busychunks`, `csserv`, `main` hooks, `cfg`, `sockets`, `datapack`, `random`, `md5`, `mfsalloc`, and `MFSCommunication` protocol constants. Master packet handlers schedule `job_*` calls, including `job_replicate_simple/split/recover/join`, which use `replicator.c` behind the job layer.

## Risks and test signals
High-risk areas include registration state transitions, metadata-id validation, reconnect after config reload, and cleanup of idle jobs on disconnect. Packet-size validation exists, but every handler has strict length expectations that should be fuzzed with short, long, and malformed packets. Tests should simulate master ACK variants, auth required without configured password, in-progress registration disconnect, changed labels with and without reconnect, periodic HDD reports with zero/nonzero queues, and stale background callbacks after reconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/masterconn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/masterconn.h -->
# sources/distributed-fs/moosefs/mfschunkserver/masterconn.h

## Purpose
`masterconn.h` exposes the chunkserver's master-connection service to other modules without revealing the singleton state machine or packet queues.

## Important APIs
The stats accessor returns/reset bytes in and out. ID accessors expose the persistent chunkserver id and metadata ids. `masterconn_getmasterip()` and `masterconn_getmasterport()` return nonzero values only when registered and connected. `masterconn_reportload()` can be called by chart/load paths, `masterconn_forcereconnect()` asks the state machine to reconnect, and `masterconn_init()` installs the module into the main loop.

## Control flow and integration
`init.h` calls `masterconn_init()` after `csserv_init()` so registration can advertise a usable chunkserver endpoint. Storage code can set HDD metadata id through `masterconn_sethddmetaid()`. Other commented-out senders show older or internal notification APIs that are now handled by periodic report checks.

## State and persistence behavior
The header exposes getters/setters for metadata identity but no direct persistence functions. Persistence is implemented in `masterconn.c` through `chunkserverid.mfs` and by forwarding meta id to `hdd_setmetaid()`.

## Risks and test signals
Callers must treat returned master address values as valid only when nonzero. Tests should cover getter behavior before connection, during registration, after registration, and after forced reconnect. Since stats reset on read, chart tests should avoid double-sampling assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/masterconn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/mfschunkdbdump.c -->
# sources/distributed-fs/moosefs/mfschunkserver/mfschunkdbdump.c

## Purpose
`mfschunkdbdump.c` is a standalone diagnostic utility for reading and validating MooseFS `.chunkdb` files. It prints the disk path and each chunk record in human-readable form, while also checking record layout, path ids, block counts, and terminator correctness.

## Important APIs and functions
`chunkdb_dump()` is the main parser. It opens a supplied file, loads the entire file into memory, verifies the `MFS CHUNKDB` header and version mode, parses a length-prefixed path, validates all fixed-size records once, then rewinds to print them. `main()` only enforces one argument and maps parser failure to exit code 1.

## Control flow and format handling
Supported modes 1 through 4 map to record sizes 16, 18, 19, and 23 bytes. Every record includes chunk id, version, block count, and path id. Mode 2 adds header size, mode 3 adds tested flag, and mode 4 adds disk usage. The parser expects a zero chunk-id terminator with zeroed remaining fields and flags any trailing or malformed ending data.

## State and persistence behavior
This utility is read-only. It does not repair or rewrite `.chunkdb`; it loads a snapshot and reports inconsistencies. It prints chunk file paths as `pathid/chunk_<id>_<version>.mfs` when path id is valid, otherwise prints raw fields.

## Dependencies and integration points
It depends on `datapack.h` for endian-safe field extraction and standard POSIX file APIs. It is operationally aligned with the chunkserver disk manager's `.chunkdb` persistence but is not linked into daemon runtime.

## Risks and test signals
The header check uses a compound condition that appears intended to reject bad signatures or unsupported versions; tests should cover all supported modes plus bad magic, short files, truncated path, truncated records, invalid path id, invalid block count, and malformed terminators. Since it reads the whole file into memory using `st_size`, very large or corrupt files should be tested for allocation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/mfschunkdbdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/mfschunktool.c -->
# sources/distributed-fs/moosefs/mfschunkserver/mfschunktool.c

## Purpose
`mfschunktool.c` is a standalone filesystem repair/check utility for MooseFS chunk files and chunkserver disk trees. It verifies chunk filename/header consistency, validates or repairs CRC tables, optionally fixes names from headers, and can move damaged chunks to a separate directory.

## Important APIs, types, and functions
Mode flags are `MODE_FAST`, `MODE_EMPTY`, `MODE_NAME`, and `MODE_REPAIR`. Name classification values distinguish arbitrary paths, MooseFS two-hex-digit disk directories, and chunk files. `hdd_check_filename()` validates `chunk_XXXXXXXXXXXXXXXX_YYYYYYYY.mfs` names and extracts chunk id/version. `chunk_repair()` performs per-file validation and optional repair. `recursive_scan()` walks directories while respecting MooseFS disk naming conventions and `.lock` files. `move_file()` handles cross-filesystem movement when rename fails with `EXDEV`.

## Control flow
The CLI accepts `-f`, `-r`, `-n`, `-e`, `-x`, and `-m damaged_dir`. `main()` resolves each input path, initializes CRC tables, allocates a block buffer, and calls `recursive_scan()`. Directory scans create and lock `.lock` to avoid checking active chunkserver disks, skip `.lock`, `.metaid`, and `.chunkdb`, and descend only into valid MooseFS path shapes unless name-repair mode permits broader scanning.

For files, `chunk_repair()` opens read-only or read-write, verifies filename and header, optionally renames files based on header chunk id/version, repairs header fields from filename when requested, determines header size from file length, reads the 4096-byte CRC area, and then checks CRCs. Fast mode validates only the last data block and possibly the first empty block. Full mode reads all 1024 blocks, compares CRCs, and in repair mode rewrites the CRC table.

## State and persistence behavior
In check mode the utility is read-only. With `-r`, it may rewrite chunk headers and CRC blocks. With `-n`, it may rename a badly named chunk file using header data. With `-m`, it moves damaged chunks into a configured directory, copying and unlinking when crossing filesystems. It avoids moving files it already repaired in place by clearing `newname` after header or CRC repair.

## Dependencies and integration points
The tool uses `crc.h`, `datapack.h`, `clocks.h`, `MFSCommunication.h`, and `idstr.h`. It understands MooseFS chunk signatures, block sizes, CRC-table size, and disk-tree conventions but runs outside the daemon.

## Risks and test signals
Because this tool can mutate chunk files, tests should cover repair vs check-only behavior carefully. Important cases include bad file names, bad headers, mismatched header chunk id/version, 1024-byte vs 4096-byte header layout, truncated files, chunk 1.0/1.1 empty-block CRC handling, fast mode false negatives, active `.lock` detection, `-m` movement including `EXDEV`, and recursion that skips `.chunkdb` even though a TODO notes future comparison with actual chunk lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/mfschunktool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/replicator.c -->
# sources/distributed-fs/moosefs/mfschunkserver/replicator.c

## Purpose
`replicator.c` implements chunkserver-side chunk replication and erasure-code transformations. It can copy a full chunk (`SIMPLE`), split one chunk into erasure-code parts (`SPLIT`), recover a missing part by XORing available parts (`RECOVER`), or join parts back into a full chunk (`JOIN`). It talks to source chunkservers using normal MooseFS read/checksum protocol packets and writes a local version-0 chunk through `hddspacemgr` before promoting it.

## Important APIs, types, and functions
The public API is `replicator_stats()` and `replicate()`. `repmodeenum` is declared in `replicator.h`. Internal state is split between `repsrc`, one per remote source, and `replication`, the operation aggregate. Helpers include `xordata()`, `rep_read()`, `rep_receive_all_packets()`, `rep_create_packet()`, `rep_create_read_request()`, `rep_write()`, `rep_send_all_packets()`, `rep_concurrent_connect()`, `rep_reconnect()`, and `rep_cleanup()`.

## Control flow
`replicate()` derives source count from mode, validates split part number and EC part count, increments stats, creates a local replica chunk with `hdd_rep_create(chunkid,0)`, connects concurrently to all sources, opens the local chunk, and requests `ANTOCS_GET_CHUNK_BLOCKS` from each source. It validates `CSTOAN_CHUNK_BLOCKS` responses for chunk id, version, status, and block count.

The main loop processes destination block groups. It builds `CLTOCS_READ` requests, sends them to all necessary sources, receives `CSTOCL_READ_DATA` packets, validates chunk id/block/offset/size, receives final `CSTOCL_READ_STATUS` packets when required, then writes local blocks. `SIMPLE` writes sequential blocks from one source. `SPLIT` reads every Nth four-block group from a full chunk. `RECOVER` XORs same-position blocks from all sources plus the zero-block CRC to reconstruct missing data and skips a final all-zero block. `JOIN` interleaves part data back into a full chunk.

On send/receive timeout the code can reconnect and retry up to `REP_RETRY_CNT`. It also enforces a total replication timeout and a progress-based timeout estimate.

## State and persistence behavior
The destination chunk starts as version 0. On any failure, `rep_cleanup()` closes the opened chunk and deletes the version-0 replica with `hdd_rep_delete()`. On success, `hdd_rep_setversion(chunkid,version)` promotes the chunk, then `hdd_close(chunkid,1)` fsync-closes it. Remote source sockets and packet buffers are always cleaned after completion.

## Dependencies and integration points
The module depends on `hddspacemgr`, `sockets`, `crc`, `mfslog`, `datapack`, `massert`, `mfsstrerr`, `clocks`, and `MFSCommunication` constants. It is invoked indirectly from `masterconn.c` through `job_replicate_*` background jobs.

## Risks and test signals
This file is sensitive to protocol framing and EC block math. Tests should cover every mode, part counts 4 and 8, last partial groups, zero-tail recovery, source overload status, wrong chunk id/version/block/offset/size responses, retry after reconnect, total and progress timeout, and cleanup after failures at every stage. Poll/NOP behavior in `rep_receive_all_packets()` should also be tested because it writes keepalive NOPs to every source while waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/replicator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/replicator.h -->
# sources/distributed-fs/moosefs/mfschunkserver/replicator.h

## Purpose
`replicator.h` declares the public replication interface used by chunkserver background jobs.

## Important APIs and types
`repmodeenum` defines `SIMPLE`, `SPLIT`, `RECOVER`, and `JOIN`. `replicator_stats()` returns/reset network byte counters and replication-operation count. `replicate()` accepts the mode, destination chunk id/version, split part number/count, and arrays of source IPs, ports, and source chunk ids sized to `MAX_EC_PARTS`.

## Control flow and integration
Master packet handlers in `masterconn.c` schedule background jobs that eventually call `replicate()`. The function blocks for a complete operation and returns an MooseFS status code, so job-layer callers must run it off the main poll loop.

## State and persistence behavior
The header exposes no state directly. Its implementation creates and promotes local chunks through `hddspacemgr`, while stats are process-local counters protected by a mutex.

## Risks and test signals
Callers must provide valid arrays for all source slots used by the mode. Split mode requires a valid `partno < parts`; recover/join require a sane part count. Tests should verify status-code propagation through the job layer and stats reset behavior after sampling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/replicator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/Makefile.am -->
# sources/distributed-fs/moosefs/mfsmaster/Makefile.am

## Purpose
`mfsmaster/Makefile.am` defines Automake build targets for the MooseFS master-side programs: `mfsmaster`, `mfsstatsdump`, and `mfssupervisor`. It is the build manifest that ties master modules to shared `mfscommon` support code and per-target compiler/linker flags.

## Important targets and variables
`sbin_PROGRAMS` lists the installed binaries. `AM_CPPFLAGS` adds `mfscommon` includes globally. `mfsstatsdump_SOURCES` contains chart/stat dump support and links zlib via `mfsstatsdump_LDFLAGS`. `mfsmaster_SOURCES` is the largest list, covering metadata structures, filesystem logic, sessions, locks, chunk management, master-to-client/server/listener protocols, background saving, topology, storage classes, common utilities, and protocol headers. `mfsmaster_CPPFLAGS` defines `MFSMAXFILES=16384` and `APPNAME=mfsmaster`; `mfsmaster_CFLAGS` uses `DYNLINKER_FLAGS`; `mfsmaster_LDFLAGS` links zlib. `mfssupervisor_SOURCES` builds the supervisor with shared socket/clock/log/protocol code and `MFSSUPERVISOR=1`.

## Control flow and integration
This file does not implement runtime control flow, but it determines which modules become part of each binary. `init.h` is included in the master source list so the common `main.c` can use the master module run tables. Shared code is included by relative paths rather than a separate library target.

## State and persistence behavior
Persistence-related master modules in the source list include `metadata`, `changelog`, `restore`, `bgsaver`, `missinglog`, and filesystem/chunk/session modules. Build omissions here can remove runtime persistence behavior entirely, so the manifest is part of the persistence surface.

## Dependencies and integration points
The file depends on Automake conventions, zlib variables, dynamic linker flags, and source-tree-relative common code. `EXTRA_DIST` includes `sbin_SCRIPTS`, and `mfsmetarestore` is installed as a script. `distclean-local` removes dependency/build products.

## Risks and test signals
Build risks include missing source/header entries, stale generated dependency directories, and inconsistent target-specific flags. Tests should include `make distcheck` or equivalent Automake distribution validation, clean-tree builds, builds with and without dynamic linker flags, and packaging checks that `mfsmetarestore` is included and installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/Makefile.am -->
