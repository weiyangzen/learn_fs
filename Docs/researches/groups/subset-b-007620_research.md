# subset-b-007620 Research

Grouped research report for LizardFS CGI and chunkserver files. Each section is source-tree aligned and can be split into its mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/mfs.cgi.in -->
# sources/distributed-fs/lizardfs/src/cgi/mfs.cgi.in

## Purpose
`mfs.cgi.in` is the Python 3 CGI dashboard template for the LizardFS web UI. CMake substitutes protocol constants such as `@PROTO_BASE@` and chart identifiers, then the script connects directly to the master and chunkservers over LizardFS binary protocols to render XHTML status tables, controls, and chart image links.

## Important APIs, Types, And Functions
- Protocol command constants cover older MooseFS-style messages, LizardFS-specific master requests, chunkserver HDD list requests, metadata-server discovery, chunk health, custom goals, and server removal.
- The mini serialization/deserialization DSL is built from `Primitive`, `Tuple`, `String`, `List`, `Dict`, and `deserialize`. It consumes a mutable `bytearray` in network byte order and supports nested lists/dicts for newer LizardFS packets.
- `make_liz_message` builds modern LizardFS packets with type, payload length including version, and version.
- `send_and_receive`, `mysend`, and `myrecv` provide blocking socket I/O, exact byte reads/writes, response type checks, and optional response version checks.
- `cltoma_list_goals`, `cltoma_chunks_health`, `cltoma_metadataservers_list`, `cltoma_hostname`, and `cltoma_metadataserver_status` are higher-level protocol helpers.
- `createlink` and `createorderlink` preserve CGI query parameters and construct sort/toggle URLs for every table.
- `LessThanComparableNone` mimics Python 2 sortable `None` behavior so rows with absent limits can be sorted with concrete values.

## Control Flow
On startup the script reads CGI fields for `masterhost`, `masterport`, and `mastername`, falling back to DNS name `mfsmaster`, port `9421`, and display name `LizardFS`. It probes the master using `CLTOMA_INFO`; response length determines historical master versions, while newer responses embed version bytes. Failure renders a standalone connection-error page with an address form and exits.

After version detection, command handling runs before normal rendering. The only mutating command in this file is `CSremove`, which parses `ip:port`, sends `CLTOMA_CSSERV_REMOVESERV`, and either redirects back to the same page without the command parameter or shows an error page with optional traceback.

The page then chooses visible sections from the `sections` query parameter. Available sections vary by master version: older masters expose `IN`, `CS`, `HD`, `ML`, charts, and help; newer masters add chunks, exports/config, mount parameters, and mount operations. Each active section appends a self-contained table, usually inside a `try` block that renders Python tracebacks into an exception table instead of aborting the page.

The `IN` section renders master info for multiple protocol-era record sizes, chunk matrix status, chunk operation loop status, and filesystem check status. The `CH` section uses `LIZ_CLTOMA_CHUNKS_HEALTH` plus goal definitions to render availability, replication, and deletion summaries. The `CS` section renders metadata servers when supported, chunkserver capacity/status, and metadata backup loggers. The `HD` section first discovers live chunkservers from the master, then queries each chunkserver's HDD list protocol, selecting V1 or V2 by chunkserver version and deriving throughput/time/space columns. `EX`, `ML`, `MS`, and `MO` decode exports and client sessions in several historical layouts. `MC` and `CC` mostly generate JavaScript and `chart.cgi` image URLs for master and chunkserver charts.

## State And Persistence
The script itself persists no server-side state. All state is per-request CGI input, transient sockets, and local variables. It reads live state from master/chunkserver processes and links chart images served by `chart.cgi`, whose backing data is maintained elsewhere. The mutating `CSremove` path changes master-managed chunkserver state by asking the master to remove a disconnected server.

## Dependencies And Integration Points
It depends only on Python standard library modules, the CGI runtime, generated CMake substitutions, `mfs.css`, static images, and `chart.cgi`. Its protocol contracts must stay aligned with LizardFS master/chunkserver packet layouts in C++ protocol code. It integrates with web servers as a CGI script and assumes direct TCP access to the master and chunkservers.

## Risks
- The file performs raw binary decoding with many version/length branches; a protocol layout drift can silently misrender rows or consume offsets incorrectly.
- Most socket calls are blocking and have no explicit timeout, so slow or unreachable chunkservers can stall a CGI request.
- Query fields are generally escaped for output with `htmlentities` or URL-escaped for links, but some decoded protocol strings and traceback paths are inserted directly in places; XSS risk depends on whether those values can be attacker controlled.
- `print_file` opens arbitrary names but is unused in production help output. It would be risky if reconnected to query-driven input.
- The script uses deprecated `cgi`/`cgitb` APIs in modern Python, so future interpreter upgrades may require replacement.
- One sorting branch in exports sets `EXorder == 14` to `mapalluid` instead of `mapallgid`, which looks like a display/sort bug.

## Test Signals
No direct unit tests are present for this CGI script in the listed files. Practical validation should include master-version compatibility tests, packet fixture decoding for each historical branch, CGI rendering smoke tests with escaped strings, and integration tests against a test master/chunkserver pair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/mfs.cgi.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/chunkserver/CMakeLists.txt

## Purpose
This CMake file defines how the LizardFS chunkserver component is built, tested, linked, and installed.

## Important APIs, Types, And Functions
- `include_directories(${CMAKE_CURRENT_SOURCE_DIR})` exposes chunkserver local headers to this target tree.
- `add_definitions` sets `LIZARDFS_MAX_FILES=10000`, `APPNAME=mfschunkserver`, and `APP_EXAMPLES_SUBDIR`.
- `collect_sources(CHUNKSERVER)` populates `${CHUNKSERVER_SOURCES}`, `${CHUNKSERVER_TESTS}`, and `${MAIN_SRC}` through repository-local CMake helpers.
- `add_library(chunkserver ...)` builds the reusable chunkserver library.
- `create_unittest` and `link_unittest` wire chunkserver tests against `chunkserver` and `mfscommon`.
- `add_executable(mfschunkserver ${MAIN_SRC})` produces the daemon binary.

## Control Flow
CMake first applies compile definitions, collects sources, creates the library, registers tests, then creates the executable. The executable links the chunkserver library and PAM libraries, and conditionally links systemd libraries when detected.

## State And Persistence
There is no runtime state here. Build state is represented in generated build-system files and install output. Installation places `mfschunkserver` into `${SBIN_SUBDIR}`.

## Dependencies And Integration Points
The chunkserver library links `lzfsprotocol`, `mfscommon`, and `${ADDITIONAL_LIBS}`. The executable links PAM and optionally systemd. The file depends on project-specific CMake functions/macros such as `collect_sources`, `create_unittest`, and `link_unittest`.

## Risks
Because `collect_sources` is opaque in this file, adding or renaming chunkserver source files depends on that helper discovering the files correctly. Global `add_definitions` applies to everything below this directory and can have wider compile effects than target-scoped definitions.

## Test Signals
The explicit `create_unittest` and `link_unittest` calls show the chunkserver target has an associated test suite compiled from `${CHUNKSERVER_TESTS}`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/bgjobs.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/bgjobs.cc

## Purpose
`bgjobs.cc` implements the chunkserver background job pool. It lets event-loop/network code enqueue HDD and replication operations onto worker pthreads, then wake the main loop through a pipe when status callbacks are ready.

## Important APIs, Types, And Functions
- `jobpool` owns the wake pipe, worker threads, locks, job queue, status queue, hash table of live jobs, and the next job id.
- `job` stores job id, callback, callback context, operation-specific arguments, state, and hash-chain link.
- `OP_*` operation constants cover invalid jobs, chunk create/delete/version/truncate/duplicate-style operations, open/close/read/prefetch/write, legacy replication, modern replication, and block-count lookup.
- `job_worker` is the worker-thread loop. It dequeues work, snapshots/disables state under `jobslock`, calls the matching `hddspacemgr`, legacy replicator, or `ChunkReplicator` operation, and sends completion status.
- `job_new` allocates and hashes a job, puts it on the producer/consumer queue, and returns a nonzero job id.
- Public `job_*` functions allocate typed argument structs and enqueue specific operations.
- `job_pool_check_jobs` drains completion statuses, invokes callbacks, removes jobs from the hash table, and frees job/argument memory.
- `job_pool_disable_job`, `job_pool_disable_and_change_callback_all`, and `job_pool_change_callback` provide cancellation/callback retargeting used by higher-level connection teardown.

## Control Flow
`job_pool_new` creates a pipe, initializes queues/locks, starts worker threads, and returns the read descriptor as a wakeup handle. A producer calls a public `job_*` function, which packages arguments and calls `job_new`. A worker blocks on `queue_get`, marks enabled jobs as `JSTATE_INPROGRESS`, dispatches the operation, and calls `job_send_status`. `job_send_status` writes one byte only when the status queue transitions from empty to non-empty, so the event loop can select/poll the pipe. The main thread calls `job_pool_check_jobs`, which drains status records until the queue is empty, reads the wake byte, invokes callbacks, and releases memory.

For reads, optional `performHddOpen` opens the chunk before `hdd_read` and closes it after read errors. Modern replication deserializes `ChunkTypeWithAddress` sources, constructs a `ChunkFileCreator`, and calls global `gReplicator.replicate`; `Exception` status becomes the job status. Legacy replication passes the packed source list directly to `legacy_replicate`.

## State And Persistence
Runtime state is in heap-allocated `jobpool`, worker threads, queues, job hash chains, and malloced argument buffers. No state is persisted to disk by the job layer itself, but enqueued operations mutate chunk files and HDD state through `hddspacemgr` and replication helpers. Job ids wrap around but skip zero.

## Dependencies And Integration Points
The implementation depends on `common/pcqueue`, pthreads, Unix pipes, `hddspacemgr`, `legacy_replicator`, `ChunkReplicator`, `ChunkFileCreator`, `ChunkTypeWithAddress` serialization, LizardFS error/status constants, syslog, and tracing/request-log helpers. It exposes a C-compatible API declared in `bgjobs.h` for other chunkserver modules.

## Risks
- Callback changes and disable operations mostly walk hash chains without holding the lock for the entire lookup, so correctness relies on only the main thread mutating/removing completed jobs while workers only change state under lock.
- Argument structs keep raw pointers for write buffers, read output buffers, and block output pointers; callers must guarantee lifetime until callback completion.
- `job_prefetch` does not honor disabled job state in the worker branch and has no callback, so failures are effectively fire-and-forget.
- The wake-pipe byte represents queue non-emptiness, not per-status count. Bugs in drain logic can desynchronize the event-loop wakeup.
- `job_pool_delete` joins workers after sending `OP_EXIT`, but outstanding completed statuses can still invoke callbacks during deletion.
- The modern replication branch catches `Exception&` but not non-LizardFS exceptions from STL or logic errors.

## Test Signals
No direct unit test is listed for `bgjobs.cc`. Coverage is likely indirect through chunkserver integration tests. Useful tests would exercise cancellation before start, cancellation during in-progress work, callback retargeting, wake-pipe drain behavior, raw pointer lifetime expectations, and replication exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/bgjobs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/bgjobs.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/bgjobs.h

## Purpose
`bgjobs.h` declares the public background job pool API used by chunkserver code to offload blocking HDD and replication work.

## Important APIs, Types, And Functions
- Pool lifecycle: `job_pool_new`, `job_pool_jobs_count`, `job_pool_check_jobs`, and `job_pool_delete`.
- Job management: `job_pool_disable_and_change_callback_all`, `job_pool_disable_job`, and `job_pool_change_callback`.
- Generic/compound chunk operation enqueueing: `job_inval` and `job_chunkop`.
- Convenience macros: `job_delete`, `job_create`, `job_test`, `job_version`, `job_truncate`, `job_duplicate`, and `job_duptrunc`; invalid inputs become `job_inval`.
- I/O jobs: `job_open`, `job_close`, `job_read`, `job_prefetch`, `job_write`, and `job_get_blocks`.
- Replication jobs: `job_replicate`, `job_legacy_replicate`, and `job_legacy_replicate_simple`.

## Control Flow
Callers create a pool with a worker count and queue capacity, then use returned `wakeupdesc` in their event loop. Each submitter receives a job id and later receives `callback(status, extra)` when `job_pool_check_jobs` drains completions. Macro wrappers validate required version/copy/length parameters before enqueueing state-changing chunk operations.

## State And Persistence
The header exposes opaque `void *jpool` handles and raw callback/context pointers. Persistence is delegated to the underlying HDD operations; the API itself only manages asynchronous state.

## Dependencies And Integration Points
It includes `OutputBuffer` for reads and `ChunkPartType` via `common/chunk_type_with_address.h`. It is the integration boundary between connection/master command handling and chunkserver storage operations.

## Risks
- The API is C-style and pointer-heavy; buffer and output-pointer lifetimes are caller responsibility.
- Macros evaluate some arguments more than once in conditions or function arguments, so side-effect expressions would be unsafe.
- `void *` erases type safety for pools and callback context.

## Test Signals
No direct header tests are listed. API behavior is verified only if implementation/integration tests cover all job macros and callback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/bgjobs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chartsdata.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/chartsdata.cc

## Purpose
`chartsdata.cc` periodically collects chunkserver runtime counters and feeds the shared LizardFS chart storage engine, persisting data to `csstats.mfs`.

## Important APIs, Types, And Functions
- `CHARTS_*` constants define 30 raw chart slots: CPU, master traffic, chunkserver network traffic, HDD overhead/total I/O, high-level ops, read/write time, replication, chunk operations, tests, and queue depths.
- `STATDEFS` defines chart names, join modes, percentage flags, scale, multipliers, and divisors for raw charts.
- `ESTATDEFS` defines derived aggregate charts such as CPU, data traffic, total bytes with overhead, low-level ops with overhead, and job totals.
- `chartsdata_refresh` gathers one sample and calls `charts_add`.
- `chartsdata_store` persists chart state.
- `chartsdata_term` refreshes, stores, and terminates the chart subsystem.
- `chartsdata_init` initializes CPU timers, registers event-loop refresh/store/destructor callbacks, and calls `charts_init`.

## Control Flow
Initialization arms virtual/profiling timers with large countdown values, registers a 60-second refresh and an hourly store, then initializes charts. Each refresh computes elapsed user and system CPU from timer deltas, gathers master connection stats, network stats, HDD stats, legacy and modern replication counts, and HDD operation counts. The sample is timestamped as `eventloop_time() - 60`, matching the just-finished interval.

## State And Persistence
Chart state is maintained by the shared `common/charts` module and persisted in `csstats.mfs`. CPU accounting state is held in process timers `ITIMER_VIRTUAL` and `ITIMER_PROF`. Replication count from `gReplicator.getStats()` is reset when sampled.

## Dependencies And Integration Points
This file integrates with `masterconn_stats`, `networkStats`, `hdd_stats`, `legacy_replicator_stats`, `gReplicator.getStats`, `hdd_op_stats`, `eventloop_timeregister`, `eventloop_destructregister`, and `common/charts`.

## Risks
- CPU accounting uses process interval timers and includes comments noting Linux timer oddities; incorrect timer behavior can distort CPU charts.
- The modern replication stat is reset during sampling, so skipped refreshes can change observed granularity.
- New chart ids must stay aligned with the CGI chart names and `chart.cgi` expectations.
- `chartsdata_term` performs a final refresh, which can double count if shutdown occurs close to a scheduled refresh.

## Test Signals
No direct unit tests are listed. Existing signals are integration-oriented: chart files should be created/stored and the CGI chart views reference ids matching this chart definition table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chartsdata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chartsdata.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/chartsdata.h

## Purpose
`chartsdata.h` exposes the chunkserver chart subsystem initialization entry point.

## Important APIs, Types, And Functions
- `int chartsdata_init(void)` initializes timers, event-loop hooks, and chart storage for chunkserver metrics.

## Control Flow
Callers invoke `chartsdata_init` during chunkserver startup. Refresh, store, and termination are registered internally by the implementation.

## State And Persistence
The header owns no state. The implementation persists samples through the chart subsystem.

## Dependencies And Integration Points
It includes `common/platform.h` and integer types, and it is consumed by chunkserver startup code.

## Risks
The narrow API hides initialization side effects. Callers must know that cleanup is registered with the event loop rather than manually exposed.

## Test Signals
No direct tests are listed for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chartsdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk.cc

## Purpose
`chunk.cc` implements chunk metadata and disk layout behavior for MooseFS-compatible and LizardFS interleaved chunk formats, including filenames, subfolder placement, block offsets, file-size validation, and header sizing.

## Important APIs, Types, And Functions
- `Chunk::Chunk` initializes common runtime metadata: owner folder, fd, version, block count, state, refcount, layout, deletion flags, and read-ahead expectation.
- `Chunk::generateFilenameForVersion` builds disk paths from owner path, subfolder, chunk type prefix, chunk id/version, and extension.
- `Chunk::renameChunkFile` renames the on-disk file and updates version/layout on success.
- `Chunk::maxBlocksInFile` maps standard/XOR/EC data part counts to per-slice block counts.
- `Chunk::getSubfolderNumber`, `getSubfolderNameGivenNumber`, and `getSubfolderNameGivenChunkId` implement current and older directory layouts.
- `MooseFSChunk` implements header-aware offsets, header size, CRC/signature offsets, header readahead, and MooseFS file-size validation.
- `InterleavedChunk` implements block records of data plus CRC with `.liz` file format semantics.

## Control Flow
File naming starts with `owner->path`, then a layout-specific subdirectory (`chunksXX` for current layout), then `chunk_` plus optional XOR or EC prefix. Standard chunks have no prefix. MooseFS format keeps `.mfs`; interleaved format replaces the extension with `.liz`. Rename first computes old/new names, calls POSIX `rename`, then updates in-memory layout and version only after success.

MooseFS chunks place a signature block and CRC array before data. Standard chunks use the exact required signature-plus-CRC size; XOR/EC chunks round the header up to a 4 KiB disk block. Interleaved chunks store each block as `MFSBLOCKSIZE` data plus a 4-byte CRC, so offsets and file sizes are simple multiples of `kHddBlockSize`.

## State And Persistence
The `Chunk` object mirrors persisted chunk files. Persistent effects occur through filename generation and `renameChunkFile`. Header/layout methods determine how other storage code reads and writes chunk contents. In-memory state includes owner folder, fd, chunk id/version, block count, type, layout version, flags, and linked-list fields for scans/tests.

## Dependencies And Integration Points
The file depends on `folder` from `chunk.h`, `ChunkPartType`, `slice_traits`, `ChunkFormat`, POSIX `rename`, `posix_fadvise` or macOS `F_RDADVISE`, and protocol constants such as `MFSBLOCKSIZE` and `MFSBLOCKSINCHUNK`. It is used by HDD space manager, filename parser/signature code, tests, and replication file creation.

## Risks
- `generateFilenameForVersion` assumes `owner` and `owner->path` are valid.
- Filename generation and parser rules must remain in lockstep across standard, XOR, EC, `.mfs`, and `.liz` formats.
- `sprintf` writes into fixed buffers, currently sized for known hexadecimal strings; future format expansion would need care.
- Header size math is format-critical; changing `ChunkPartType` or block-count rules can break compatibility with existing chunks.

## Test Signals
`chunk_unittest.cc` covers `maxBlocksInFile`, generated filenames for standard and XOR chunks, and current subfolder naming. It does not cover EC filenames, old directory layout names, `renameChunkFile`, or file-size validation edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk.h

## Purpose
`chunk.h` declares chunkserver disk chunk types, folder/disk state structures, and the `Chunk` class hierarchy used by storage, scanning, replication, and I/O code.

## Important APIs, Types, And Functions
- Constants: `STATSHISTORY`, `LASTERRSIZE`, and `kHddBlockSize`.
- `ChunkState` enumerates availability/deletion lifecycle states: available, locked, deleted, and to-be-deleted.
- `cntcond` and `ioerror` are support structures for waiters and recent disk errors.
- `folder` stores path, scan/migration states, capacity, statistics history, last errors, chunk counts, device/lock data, scan/migration threads, test chunk lists, and linked-list linkage.
- `Chunk` declares naming, rename, layout, block offset/size validation, chunk format, subfolder helpers, and shared fields.
- `MooseFSChunk` declares header/CRC/signature behavior for `.mfs`.
- `InterleavedChunk` declares `.liz` interleaved block behavior.
- `IF_MOOSEFS_CHUNK` and `IF_INTERLEAVED_CHUNK` are dynamic-cast convenience macros.

## Control Flow
Storage code creates a concrete `Chunk` subtype based on parsed chunk format or desired output format. It uses virtual methods to translate block numbers to file offsets and validate persisted file sizes. Folder scan/migration code updates `folder` scan and migration bitfields and links chunks through the public intrusive pointers.

## State And Persistence
This header defines much of the chunkserver's in-memory representation of persisted storage: folder paths/capacity/statistics and chunk ids, versions, fds, block counts, owners, layout, deletion flags, and scan/test links. Persistent chunk files are named and interpreted through the `Chunk` methods declared here.

## Dependencies And Integration Points
It integrates with `chunk_format.h`, `ChunkPartType`, `DiskInfo`, `MFSCommunication` constants, condition variables, threads, and POSIX device/inode types. Many chunkserver modules include this header through HDD manager, parser, creator, and tests.

## Risks
- Public mutable fields make invariants spread across modules rather than enforced by methods.
- Bitfield state constants for scans/migration/removal must remain consistent with all scanner code.
- `setBlockCountFromFizeSize` contains a misspelling in the API name, which is harmless but sticky ABI/source surface.
- The folder struct combines persistence, statistics, scanning, migration, and locking concerns, increasing accidental coupling.

## Test Signals
`chunk_unittest.cc` directly covers some virtual behavior and naming. Broader folder state and scan/migration fields are not covered in listed tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_file_creator.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_file_creator.cc

## Purpose
`chunk_file_creator.cc` implements an RAII helper for safely creating a new chunk file during replication. If creation is not committed, the destructor removes the partial chunk.

## Important APIs, Types, And Functions
- Constructor stores target chunk id, version, and type, and initializes lifecycle flags.
- Destructor closes an open chunk, deletes an uncommitted created chunk, and releases the chunk reference.
- `create` calls `hdd_int_create_chunk` with temporary version `0`, opens the chunk, and marks it created/open.
- `write` maps absolute chunk offset to block number plus block-local offset and calls `hdd_write` with temporary version `0`.
- `commit` closes the chunk and changes version from `0` to the requested final version through `hdd_int_version`.

## Control Flow
The expected sequence is `create`, zero or more `write` calls, then `commit`. Any failure throws `Exception` with the LizardFS status code. If a failure interrupts the sequence, destruction closes and deletes the temporary chunk so partial replicated data is not left as a valid chunk.

## State And Persistence
Persistent state is a newly created chunk file on disk. It is initially version `0` and becomes durable under the requested version only after successful close and version change. Object state tracks `chunk_`, `is_created_`, `is_open_`, and `is_commited_`.

## Dependencies And Integration Points
This helper wraps internal HDD manager APIs: `hdd_int_create_chunk`, `hdd_open`, `hdd_write`, `hdd_close`, `hdd_int_version`, `hdd_int_delete`, and `hdd_chunk_release`. `ChunkReplicator` uses it to materialize replicated blocks.

## Risks
- The destructor calls HDD operations but cannot report failures, so cleanup failure can be silent.
- `write` assumes offsets are in chunk data space and uses `MFSBLOCKSIZE` block math; callers must provide aligned/valid ranges.
- Assertions enforce lifecycle sequencing in debug builds only.

## Test Signals
No direct unit tests are listed. Replication tests, if present elsewhere, should verify rollback on thrown errors and successful version commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_file_creator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_file_creator.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_file_creator.h

## Purpose
`chunk_file_creator.h` declares the safe chunk creation helper used to create a complete chunk and delete it automatically unless committed.

## Important APIs, Types, And Functions
- `ChunkFileCreator(uint64_t chunkId, uint32_t chunkVersion, ChunkPartType chunkType)` stores target identity.
- `create`, `write`, and `commit` form the lifecycle API.
- Accessors `chunkId`, `chunkVersion`, and `chunkType` expose target identity to replication planning.
- Protected fields hold target identity, the owned `Chunk *`, and lifecycle booleans.

## Control Flow
Consumers construct the object on the stack, call `create`, write data blocks, and call `commit`. Stack unwinding before commit triggers cleanup in the implementation destructor.

## State And Persistence
The header describes ownership of one in-progress chunk file. Persistence becomes permanent only after commit.

## Dependencies And Integration Points
It includes `ChunkPartType` and `chunk.h`, tying it to chunkserver disk abstractions. `ChunkReplicator` is the primary listed consumer.

## Risks
The class is copyable by default unless disabled elsewhere by compiler rules from members; copying would be unsafe because both instances would point at the same `Chunk *`. The header does not explicitly delete copy/move operations.

## Test Signals
No direct tests are listed for this class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_file_creator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser.cc

## Purpose
`chunk_filename_parser.cc` parses chunk file basenames into chunk format, chunk type, chunk id, and version. It supports standard, XOR, and EC naming, plus `.mfs` and `.liz` formats.

## Important APIs, Types, And Functions
- `ChunkFilenameParser::parse` parses the full filename and rejects trailing characters.
- `parseChunkType` detects `ec2_`, legacy `ec_`, `xor_`, or default standard chunk type.
- `parseECChunkType` parses `part_of_data_parity_` and validates EC data/parity counts and part index.
- `parseXorChunkType` parses data parts like `xor_1_of_3_` and parity parts like `xor_parity_of_3_`.
- `isUpperCaseHexDigit` enforces uppercase hexadecimal ids/versions.
- Accessors return `ChunkFormat`, `ChunkPartType`, version, and id after parsing.

## Control Flow
Parsing starts by assuming `ChunkFormat::INTERLEAVED`, consumes `chunk_`, parses an optional type prefix, then consumes exactly 16 uppercase hex digits for chunk id, an underscore, exactly 8 uppercase hex digits for version, and either `.liz` or `.mfs`. `.mfs` switches format to MooseFS. Any bad consume, invalid numeric range, leading zero in type counts, overlong XOR count, invalid EC part, lowercase hex, or trailing data returns `ERROR_INVALID_FILENAME`.

## State And Persistence
The parser holds parsed values in object fields. It does not persist state, but its acceptance rules define which on-disk files the chunkserver recognizes during scans.

## Dependencies And Integration Points
It depends on `common/parser.h`, `ChunkFormat`, `ChunkPartType`, `Goal`, and `slice_traits`. It must stay aligned with `Chunk::generateFilenameForVersion` and the storage scanner.

## Risks
- There are two accepted EC prefixes, `ec2_` and `ec_`, but filename generation currently emits `ec2_`; compatibility intent should remain clear.
- Parser strictness around uppercase hex and leading zeroes can cause valid-looking manual files to be ignored.
- C library character functions are used through predicates; inputs outside plain ASCII should not be expected.
- The exception catch has `std:: invalid_argument` spacing that compiles as `std::invalid_argument`, but it is visually odd.

## Test Signals
`chunk_filename_parser_unittest.cc` extensively covers standard, XOR, XOR parity, EC, `.mfs`, `.liz`, high unsigned chunk ids, and many invalid filename cases. Tests do not appear to cover the legacy `ec_` prefix directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser.h

## Purpose
`chunk_filename_parser.h` declares the parser class for chunk file basenames.

## Important APIs, Types, And Functions
- `Status` reports `OK` or `ERROR_INVALID_FILENAME`.
- Constructor accepts a filename string and initializes the base `Parser`.
- `parse` performs full parsing.
- Accessors expose parsed `chunkFormat`, `chunkType`, `chunkVersion`, and `chunkId`.
- Private constants enforce 16 hex digits for chunk id and 8 for version.
- Private helpers split XOR, EC, and top-level type parsing.

## Control Flow
The class is stateful: construct, call `parse`, then read accessors if status is `OK`.

## State And Persistence
State is the parser cursor inherited from `Parser` plus parsed chunk fields. No persistence is performed, but the parsed output drives persisted chunk discovery.

## Dependencies And Integration Points
It includes `chunk_format.h`, `ChunkPartType`, and `Parser`. It is part of the storage scan/file-discovery path and is validated by its unit test.

## Risks
Accessors can be called after a failed parse and will return partially initialized/default values. Callers must check `Status`.

## Test Signals
The matching unittest covers the public parser behavior across valid and invalid names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser_unittest.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser_unittest.cc

## Purpose
This GoogleTest file verifies `ChunkFilenameParser` behavior for valid standard/XOR/EC chunk names and invalid filename variants.

## Important APIs, Types, And Functions
- `TEST(ChunkFilenameParser, ParseStandardChunkFilename)` checks standard `.liz` parsing and unsigned 64-bit chunk ids.
- `ParseXorChunkFilename`, `ParseXorChunkFilenameMaxLevel`, `ParseXorParityFilename`, and `ParseXorParityFilenameMaxLevel` validate XOR data/parity naming and format detection.
- `ParseECChunkFilename` and `ParseECChunkFilenameMaxLevel` validate EC naming.
- `ParseWrongFilenames` enumerates malformed names and expects `ERROR_INVALID_FILENAME`.

## Control Flow
Each test constructs a parser with one filename, calls `parse`, and asserts parsed format/id/version/type or error status. The invalid test runs a sequence of independent parser constructions.

## State And Persistence
No persistent state. Tests validate parsing rules that affect disk scan recognition.

## Dependencies And Integration Points
It depends on GoogleTest, `chunk_filename_parser.h`, and `slice_traits` constructors/constants for expected `ChunkPartType` values.

## Risks
The invalid EC leading-zero parity case duplicates the same string as the data-count case, so one intended invalid parity variation may be untested. The legacy `ec_` prefix accepted by implementation is not directly tested.

## Test Signals
This is the direct test signal for filename parsing. It has strong negative coverage for casing, length, trailing data, XOR ranges, missing parts, illegal characters, and EC ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_format.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_format.h

## Purpose
`chunk_format.h` defines the enum describing on-disk chunk file format.

## Important APIs, Types, And Functions
- `enum class ChunkFormat { IMPROPER, MOOSEFS, INTERLEAVED }`.

## Control Flow
The enum is used as a value returned by chunk classes and parsers. `MOOSEFS` corresponds to header-plus-data `.mfs` files; `INTERLEAVED` corresponds to data-plus-CRC block `.liz` files; `IMPROPER` is the base/default invalid format.

## State And Persistence
This enum directly models persisted file layout. Storage code uses it to choose offsets, validation, and filename extension.

## Dependencies And Integration Points
It includes `common/platform.h` and is included by `chunk.h`, `chunk.cc`, and `chunk_filename_parser`.

## Risks
Adding formats requires coordinated changes in parser, filename generation, chunk subclass behavior, signature/header handling, and tests.

## Test Signals
`chunk_filename_parser_unittest.cc` and `chunk_unittest.cc` indirectly validate format values for parsed/generated filenames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_replicator.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_replicator.cc

## Purpose
`chunk_replicator.cc` implements modern chunk replication and slice recovery for the chunkserver. It reads source chunk parts from remote chunkservers, reconstructs the requested local chunk type, writes it with `ChunkFileCreator`, and records replication statistics.

## Important APIs, Types, And Functions
- Global `ConnectionPool`, `ChunkConnectorUsingPool`, and `ChunkReplicator gReplicator` provide the default process-wide replicator.
- Constructor stores a `ChunkConnector` and default timeouts.
- `getStats` returns and resets the completed replication counter under a mutex.
- `getChunkBlocks` overload for one source sends version-aware get-blocks requests and validates responses.
- `getChunkBlocks` overload for many sources tries preferred sources first and falls back to `MFSBLOCKSINCHUNK`.
- `replicate` is the main algorithm: determine block count, build available locations, create output chunk, plan/read/write batches, commit, and increment stats.
- `incStats` increments the protected replication counter.

## Control Flow
Replication first asks sources for the number of blocks. For EC-capable sources it serializes modern EC-aware `cstocs::getChunkBlocks`; for XOR-capable pre-EC sources it serializes legacy chunk type; for old standard-only sources it serializes a MooseFS packet. Response validation checks id, version, chunk type, and OK status. Block count is adjusted for parity and data part indexing.

The main `replicate` method converts full-chunk blocks to target-slice blocks, rounds batch size to a data-part multiple, records available chunk types and network locations, and calls `fileCreator.create()`. For each batch it asks `SliceRecoveryPlanner` for a read plan, waits on `replicationBandwidthLimiter`, executes reads with `ReadPlanExecutor`, computes CRC per block, writes blocks into the output creator, and finally commits.

## State And Persistence
Persistent state is the newly replicated chunk file created through `ChunkFileCreator`. Runtime state includes pooled network connections, timeouts, per-run planner/location maps/buffers, and the replication stat counter reset by charts sampling.

## Dependencies And Integration Points
It integrates with `ChunkConnector`, connection pooling, `protocol/cstocs`, MooseFS packet helpers, `ReadPlanExecutor`, `SliceRecoveryPlanner`, `replicationBandwidthLimiter`, CRC utilities, `ChunkFileCreator`, version constants (`kFirstECVersion`, `kFirstXorVersion`), sockets, and LizardFS exceptions.

## Risks
- If all sources fail block-count probing, the fallback assumes a full chunk, which may over-read or replicate extra zero/invalid data depending on lower layers.
- Network operations use fixed 1000 ms write/read waits in `getChunkBlocks`, separate from configurable connection timeout.
- `static const SteadyDuration max_wait_time` inside `replicate` is initialized from `total_timeout_ms_` only once, so later timeout changes may not affect that static duration as intended.
- The code closes a connection on unexpected response before throwing, but other exceptions around network I/O rely on connector/socket cleanup behavior.
- The function assumes `ReadPlanExecutor` fills exactly enough bytes for `nrOfBlocks * MFSBLOCKSIZE`.

## Test Signals
No direct replicator test is listed here. Indirect signals include chart replication counts and background `job_replicate` integration. High-value tests would cover version-specific block-count protocols, partial source failure fallback, timeout setters, bandwidth limiter errors, and rollback through `ChunkFileCreator`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_replicator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_replicator.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_replicator.h

## Purpose
`chunk_replicator.h` declares the `ChunkReplicator` class and the global `gReplicator` used by chunkserver background jobs and chart collection.

## Important APIs, Types, And Functions
- Default timeout constants for total replication, per-wave execution, and connection setup.
- Constructor takes a `ChunkConnector&` for dependency injection.
- `replicate(ChunkFileCreator&, const std::vector<ChunkTypeWithAddress>&)` performs replication.
- `getStats` returns/reset replication count.
- Timeout setters adjust total, wave, and connection timeouts.
- Private `getChunkBlocks` overloads determine source block count.
- Private `incStats` records successful replication.
- Fields include `ChunkserverStats`, connector reference, stats counter, mutex, and timeouts.

## Control Flow
Callers create or use a global replicator, optionally set timeouts, then call `replicate` with an output creator and source locations. Stats are sampled separately through `getStats`.

## State And Persistence
The class owns no chunk file directly; persistence is delegated to `ChunkFileCreator`. Runtime mutable state is the stats counter and timeout values.

## Dependencies And Integration Points
It includes creator, recovery planner, connector, chunk type/address, chunkserver stats, and exception headers. `bgjobs.cc` uses `gReplicator` for `job_replicate`, and `chartsdata.cc` samples its stats.

## Risks
The class stores a connector reference, so connector lifetime must outlive the replicator. Timeout setters are unsynchronized relative to concurrent replication calls.

## Test Signals
No direct tests are listed for this header/class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_replicator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature.cc

## Purpose
`chunk_signature.cc` implements reading and serializing chunk file signatures for MooseFS-compatible, legacy LizardFS XOR, and current LizardFS EC-capable chunk headers.

## Important APIs, Types, And Functions
- Signature ids: MooseFS `"MFSSIGNATURE C 1.0"` via macro composition, LizardFS 1.0 `"LIZC 1.0"`, and LizardFS 1.1 `"LIZC 1.1"`.
- Default constructor creates an uninitialized signature for `readFromDescriptor`.
- Value constructor creates a serializable current-format signature.
- `readFromDescriptor` reads fixed signature bytes at an offset, extracts id/version/type, and validates signature id.
- `serializedSize` returns current serialized size.
- `serialize` writes the current `LIZC 1.1` id, chunk id, version, and current `ChunkPartType`.

## Control Flow
Reading uses `pread` to fetch `kSignatureSize` bytes. It always decodes chunk id and version after the 8-byte signature id, defaults type to standard, and then branches by signature id. MooseFS signatures have no type payload. LIZC 1.0 deserializes a legacy one-byte chunk part type and converts it. LIZC 1.1 deserializes current `ChunkPartType`. Unknown ids set `hasValidSignatureId_` false but still return true if the fixed read succeeded.

## State And Persistence
The class mirrors signature state persisted inside chunk headers: signature id, chunk id, version, and chunk type. Serialization always writes the current 1.1 format.

## Dependencies And Integration Points
It uses POSIX `pread`, protocol serialization helpers, `slice_traits`, `ChunkPartType`, legacy chunk type conversion, and `MFSCommunication` signature constants. It integrates with chunk scanning and validation code.

## Risks
- `readFromDescriptor` returns true for an unknown signature id after setting `hasValidSignatureId_` false, so callers must check both return value and `hasValidSignatureId`.
- The read size is the current maximum signature size; files containing only shorter historical signatures must still have enough bytes readable at that offset.
- Serialization compatibility depends on `ChunkPartType` binary size and encoding remaining stable.

## Test Signals
`chunk_signature_unittest.cc` covers reading LIZC 1.0 legacy signatures, reading LIZC 1.1 signatures, serialized size, and serialized bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature.h

## Purpose
`chunk_signature.h` declares the chunk signature value object used to read and write chunk header identity.

## Important APIs, Types, And Functions
- Static offsets and sizes define signature id, chunk id, version, chunk type, and total fixed signature size.
- Constructors support read-then-initialize and direct serialization.
- `readFromDescriptor` initializes from a file descriptor and offset.
- Accessors expose validity, chunk id, version, and type.
- `serializedSize` and `serialize` integrate with repository serialization helpers.
- Static signature id arrays document MooseFS, LizardFS 1.0, and LizardFS 1.1 ids.

## Control Flow
Typical scan flow constructs a default object, calls `readFromDescriptor`, checks return and validity, then compares id/version/type to filename or expected metadata. Write flow constructs from values and serializes.

## State And Persistence
Object fields store persisted signature data. The fixed offsets define on-disk header compatibility.

## Dependencies And Integration Points
It includes `ChunkPartType` and serialization macros. The tests use it with temporary files and serialization helpers.

## Risks
Changing `kSignatureSize`, offset constants, or `ChunkPartType` size breaks compatibility with existing chunk files unless migration logic is added.

## Test Signals
The matching unittest asserts the 22-byte serialized current size and exact byte layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature_unittest.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature_unittest.cc

## Purpose
This GoogleTest file verifies chunk signature read and serialization compatibility.

## Important APIs, Types, And Functions
- `ReadingOldSignatureFromFile` creates a temp file with `LIZC 1.0` signature bytes and a legacy XOR type id, then validates converted `ChunkPartType`.
- `ReadingFromFile` validates current `LIZC 1.1` two-byte type id parsing.
- `SerializedSize` asserts current signatures serialize to 22 bytes.
- `Serialize` asserts exact serialized bytes for a known id/version/type.

## Control Flow
Tests write byte vectors to temporary files, open them, read signatures at offset 5, and assert parsed fields. Serialization tests use repository `serialize` helpers and compare vectors.

## State And Persistence
Temporary files simulate persisted chunk headers. No repository state is changed.

## Dependencies And Integration Points
It depends on GoogleTest, `TemporaryDirectory`, Unix file APIs, `ChunkSignature`, `slice_traits`, and `unittests/chunk_type_constants.h`.

## Risks
Tests do not cover MooseFS signature id, invalid signature ids, short reads, corrupt type payloads, or EC current type examples.

## Test Signals
This is strong compatibility coverage for legacy/current LizardFS signature formats and exact binary layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_unittest.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/chunk_unittest.cc

## Purpose
This GoogleTest file verifies selected `Chunk`, `MooseFSChunk`, and `InterleavedChunk` behavior.

## Important APIs, Types, And Functions
- Fixture `ChunkTests` constructs standard and XOR MooseFS/interleaved chunks.
- `MaxBlocksInFile` validates slice block capacity for standard, 2-of-XOR, and 3-of-XOR chunks.
- `GetFileName` validates generated standard, XOR data, and XOR parity filenames and extensions.
- `GetSubfolderName` validates current `chunksXX` subfolder naming from numbers and chunk ids.

## Control Flow
Tests instantiate chunks in memory, create a minimal `folder` with `/mnt/`, set owner/chunk ids, and compare generated strings.

## State And Persistence
No disk state is modified. The tests validate functions that determine persisted chunk paths and capacity.

## Dependencies And Integration Points
It depends on GoogleTest, `chunk.h`, and `slice_traits`.

## Risks
Coverage does not include EC filenames, interleaved standard filenames, MooseFS/interleaved file-size validation, header size, old directory layout, or rename behavior.

## Test Signals
This is direct evidence for core chunk naming and max-block math but not for the full disk lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/chunk_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/g_limiters.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/g_limiters.cc

## Purpose
`g_limiters.cc` defines the process-global replication bandwidth limiter singleton accessor.

## Important APIs, Types, And Functions
- `replicationBandwidthLimiter()` returns a function-local static `ReplicationBandwidthLimiter`.

## Control Flow
The first call constructs the static limiter, and later calls return the same object. C++11 thread-safe local static initialization is relied on.

## State And Persistence
Runtime state lives inside the singleton limiter. There is no persistence in this file.

## Dependencies And Integration Points
`ChunkReplicator` calls this limiter before reading/writing replication batches. Configuration code elsewhere likely adjusts limiter policy through the returned reference.

## Risks
Global mutable state can make tests and concurrent configuration harder. Lifetime lasts until process exit, so shutdown ordering must not use it after dependent static objects have gone away.

## Test Signals
No direct tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/g_limiters.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/g_limiters.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/g_limiters.h

## Purpose
`g_limiters.h` declares the global accessor for chunkserver replication bandwidth limiting.

## Important APIs, Types, And Functions
- `ReplicationBandwidthLimiter& replicationBandwidthLimiter();`

## Control Flow
Consumers call the accessor when they need to wait for or configure replication bandwidth budget.

## State And Persistence
No state in the header. The implementation returns a process-global limiter.

## Dependencies And Integration Points
It includes `replication_bandwidth_limiter.h`. `chunk_replicator.cc` depends on it directly.

## Risks
The accessor exposes mutable global state by non-const reference. Misconfiguration in one module affects all replication operations.

## Test Signals
No direct tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/g_limiters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead.cc

## Purpose
`hdd_readahead.cc` defines the global `HDDReadAhead` configuration object used by chunkserver HDD read operations.

## Important APIs, Types, And Functions
- `HDDReadAhead gHDDReadAhead;`

## Control Flow
The object is default-constructed at process startup and accessed through the extern declaration in the header.

## State And Persistence
Runtime read-behind/read-ahead settings live in atomic fields inside `gHDDReadAhead`. There is no direct persistence; configuration reload code elsewhere likely sets values.

## Dependencies And Integration Points
`bgjobs.cc` passes readahead/readbehind values into `hdd_read`; other code can read or update `gHDDReadAhead`.

## Risks
Default atomic values are not explicitly initialized in `HDDReadAhead`, so unless default construction value-initializes them elsewhere or configuration sets them before use, startup defaults may be unclear.

## Test Signals
`hdd_readahead_unittest.cc` tests conversion behavior using local `HDDReadAhead` instances, not the global object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead.h

## Purpose
`hdd_readahead.h` declares the read-ahead/read-behind configuration class for chunkserver HDD reads.

## Important APIs, Types, And Functions
- `HDDReadAhead::maxBlocksToBeReadBehind` and `blocksToBeReadAhead` return current atomic block counts.
- `setMaxReadBehind_kB` and `setReadAhead_kB` convert kilobytes to MFS block counts and store them.
- `kBToBlocks` computes `(kB * 1024) / MFSBLOCKSIZE`.
- `extern HDDReadAhead gHDDReadAhead` declares the process-global instance.

## Control Flow
Configuration code sets values in KiB. Read paths fetch block counts and pass them into HDD I/O functions to decide prefetch/read-behind windows.

## State And Persistence
State is two `std::atomic<uint16_t>` fields. The class does not persist settings itself.

## Dependencies And Integration Points
It depends on `MFSBLOCKSIZE` from `protocol/MFSCommunication.h` and is consumed by HDD read code and tests.

## Risks
- `kBToBlocks` multiplies `uint32_t kB` by 1024 before dividing, so extremely large inputs can overflow before truncation to `uint16_t`.
- Atomic fields lack explicit default initializers in the class definition.
- Conversion truncates partial blocks by design; callers must understand that sub-block KiB values become zero.

## Test Signals
`hdd_readahead_unittest.cc` covers conversion boundaries around one and two block sizes and a larger value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead_unittest.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead_unittest.cc

## Purpose
This GoogleTest file verifies KiB-to-block conversion and setter/getter behavior for `HDDReadAhead`.

## Important APIs, Types, And Functions
- Helper `testHDDReadAhead` tests both max read-behind and read-ahead setters for one input.
- `TEST(HDDReadAheadTests, HDDReadAhead)` checks zero, just-under-one-block, exact one block, just-under-two-blocks, exact two blocks, and 17 blocks.

## Control Flow
Each helper invocation creates fresh `HDDReadAhead` instances, sets one value, and checks the corresponding getter.

## State And Persistence
No persistent state. Tests use local instances and do not touch `gHDDReadAhead`.

## Dependencies And Integration Points
It depends on GoogleTest, `hdd_readahead.h`, and `MFSBLOCKSIZE`.

## Risks
The test does not cover overflow, default constructor values, concurrent reads/writes, or the global instance.

## Test Signals
This is direct evidence that truncating KiB-to-block conversion is expected for common boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead_unittest.cc -->
