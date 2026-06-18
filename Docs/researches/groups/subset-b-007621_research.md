# Research Group: subset-b-007621

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hddspacemgr.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/hddspacemgr.cc

## Purpose
`hddspacemgr.cc` is the chunkserver's local disk and chunk registry manager. It owns configured HDD folders, scans chunk directories, tracks available/used space, opens and caches chunk file descriptors, validates and updates chunk CRC metadata, performs chunk lifecycle operations requested by the master, and queues damaged/lost/new chunk reports. It is the persistence boundary between network/master jobs and actual chunk files on disk.

## Important APIs, Types, and Functions
The file implements the public `hdd_*` API declared in `hddspacemgr.h`: statistics (`hdd_stats`, `hdd_op_stats`, `hdd_errorcounter`), master report drains (`hdd_get_damaged_chunks`, `hdd_get_lost_chunks`, `hdd_get_new_chunks`), disk info serialization (`hdd_diskinfo_v1_*`, `hdd_diskinfo_v2_*`), space/load (`hdd_get_space`, `hdd_get_load_factor`), I/O (`hdd_open`, `hdd_close`, `hdd_read`, `hdd_write`, `hdd_prefetch_blocks`), chunk operations (`hdd_chunkop`, `hdd_int_create`, `hdd_int_delete`, `hdd_int_version`), background testing (`hdd_test_chunk`), and lifecycle (`hdd_init`, `hdd_late_init`, `hdd_reload`, `hdd_term`).

Central state includes `gChunkRegistry`, an unordered map keyed by `(chunkid, ChunkPartType)` and storing `std::unique_ptr<Chunk>` subclasses; `folderhead`, a linked list of configured disk folders; `gOpenChunks`, an `IndexedResourcePool<OpenChunk>` used as an LRU descriptor/CRC-cache pool; report queues for damaged/lost/new chunks; and multiple atomics for chart counters, reload flags, test cadence, and scan/termination state.

## Control Flow
Startup runs `hdd_init`, which parses `HDD_LEAVE_SPACE_DEFAULT`, reads `mfshdd.cfg` via `hdd_folders_reinit`, initializes CRC constants, reload hooks, chart timers, destructor hooks, and chunk format configuration. `hdd_late_init` starts background threads: periodic folder check, delayed open-resource cleanup, chunk tester, and client-triggered test queue processing.

Folder control flows through `hdd_check_folders`. It starts scans for folders in `SCST_SCANNEEDED`, joins completed scan/migration threads, refreshes space, removes deleted folders, sends chunk state to the master, and marks folders damaged after repeated recent `EIO`/`EROFS` errors. `hdd_folder_scan` creates current subdirectories for writable disks, scans old and current layouts, registers chunks with `hdd_add_chunk`, starts layout migration, and updates progress. Migration uses `hdd_folder_migrate_directories` to rename old-layout chunk files into the current layout.

Chunk access flows through `hdd_chunk_get` and `hdd_chunk_release`. `hdd_chunk_get` finds or creates registry entries, waits on locked/deleting chunks with `cntcond`, validates file attributes, recreates invalid chunks when allowed, and returns locked chunks. `hdd_io_begin` opens files, reads MooseFS CRC headers into the open chunk cache, and increments `refcount`; `hdd_io_end` writes dirty CRC blocks, optionally fsyncs, records stats, and releases descriptors into the LRU pool.

Reads validate request size, version, block bounds, optionally prefetch/read-behind, and return a CRC plus data through `OutputBuffer`. Writes validate version, block/offset/size, recompute CRC for partial writes, expand/truncate files when needed, update MooseFS or interleaved CRC layout, optionally punch holes in zero ranges, and mark chunks dirty. Mutating operations implement create, delete, version rename, duplicate, truncate, duplicate-truncate, and test behind the dispatching `hdd_chunkop`.

## State and Persistence Behavior
Persistent state is chunk files under configured HDD paths, their directory layout, file names containing IDs/versions/types, MooseFS chunk signatures/CRC headers, interleaved block CRC/data layout, and per-folder `.lock` files. Runtime state caches folder availability, chunk counts, last errors, scan progress, current chunk object states, file descriptor CRC buffers, and pending master reports. Reload re-parses disk config and can mark folders for removal/rescan/resend without process restart. Termination joins background workers, flushes dirty MooseFS CRC data when possible, closes descriptors, clears the registry, unlocks folder state, and frees condition nodes.

## Dependencies and Integration Points
This file depends on chunk abstractions (`Chunk`, `MooseFSChunk`, `InterleavedChunk`), filename parsing, signatures, CRC utilities, config/event-loop facilities, socket/common serialization helpers, `IoStat`, `IndexedResourcePool`, `OpenChunk`, and protocol structs. It integrates upward with `masterconn.cc` for chunk inventory, space, damaged/lost/new reports, and master-requested jobs; with `network_worker_thread.cc` via bgjob wrappers that call hdd read/write/open/close/get-blocks; with legacy and modern replicators for creating and filling chunks; and with charts via periodic statistics snapshots.

## Risks and Edge Cases
The highest-risk areas are concurrency and recovery around chunk state transitions. `gChunkRegistryLock`, `folderlock`, and `testlock` are used in several orders; changes must preserve existing lock ordering to avoid deadlocks. Partial failures during duplicate/truncate/version operations can leave renamed files, updated headers, or created destination chunks that must be cleaned carefully. CRC behavior differs between MooseFS and interleaved formats, and sparse-file compatibility has special zero-block handling. Descriptor recycling relies on `OpenChunk::canRemove` and on correct `refcount`/release sequencing. Folder scan/migration races with reload/removal are controlled by scan/migration states but remain sensitive.

## Test Signals
Useful tests include unit coverage for `hdd_size_parse`, CRC recomputation on sparse/partial blocks, version mismatch handling, chunk create/delete/duplicate/truncate dispatch, and old/new layout filename parsing. Integration tests should exercise startup scanning, reload of HDD paths, disk damage reporting, ENFILE descriptor pressure, fsync/hole-punch toggles, concurrent read/write/close operations, and master report draining. Fault injection around `pread`, `pwrite`, `fsync`, `rename`, `unlink`, and `ftruncate` would give strong regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hddspacemgr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hddspacemgr.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/hddspacemgr.h

## Purpose
`hddspacemgr.h` is the public interface for the chunkserver disk-space manager. It exposes statistics, disk inventory, space usage, chunk I/O, chunk mutation, background test, initialization, and a small set of low-level chunk operations used by specialized code such as `ChunkFileCreator`.

## Important APIs, Types, and Functions
The header exports stats collection (`hdd_stats`, `hdd_op_stats`, `hdd_errorcounter`), master-facing report drains (`hdd_get_damaged_chunks`, `hdd_get_lost_chunks`, `hdd_get_new_chunks`), disk info packet sizing/serialization for v1/v2, chunk enumeration in bulks, space/load queries, chunk lock/release helpers, and I/O operations (`hdd_open`, `hdd_close`, `hdd_read`, `hdd_write`, `hdd_prefetch_blocks`). `hdd_chunkop` is the general mutation dispatcher. Macros map common master operations such as create/delete/version/duplicate/truncate onto `hdd_chunkop`. Low-level functions include `hdd_int_create_chunk`, `hdd_int_create`, `hdd_int_delete`, and `hdd_int_version`.

The API is built around `Chunk`, `ChunkPartType`, `ChunkWithType`, `ChunkWithVersionAndType`, `OutputBuffer`, and protocol chunk containers.

## Control Flow
Callers normally use the high-level API. Master jobs call create/delete/version/duplicate/truncate through `hdd_chunkop` or wrappers. Network/HDD worker jobs call open/read/write/close and get-blocks operations. Master connection code periodically calls stats, space, and chunk-report drains. Startup uses `hdd_init` before network/master components and `hdd_late_init` after thread-capable initialization.

## State and Persistence Behavior
The header itself stores no state, but its functions operate on persistent chunk files and runtime disk-manager state inside `hddspacemgr.cc`. The lock/release pairing in the API is part of the concurrency contract: callers receiving a locked `Chunk*` from low-level creation or lookup paths must release it correctly.

## Dependencies and Integration Points
Includes tie this interface to chunk file creation, output buffering, chunk type/version records, and MFS protocol definitions. Consumers include background job wrappers, master connection command handlers, client/chunkserver network workers, legacy and modern replicators, chart/stat modules, and initialization tables.

## Risks and Edge Cases
The macro wrappers are brittle because they encode operation modes through magic `length` and `chunkNewVersion` values. Two macros in this snapshot show suspicious argument lists for `hdd_truncate`/`hdd_duptrunc` that should be compile-checked in context. The low-level API exposes locked chunk pointers and therefore can leak locks or descriptors if misused. Version `0` is treated as wildcard in several operations, so callers must avoid accidental version bypass.

## Test Signals
Compile tests should cover all macros and overloads. Integration tests should confirm that each master-level operation maps to the expected `hdd_chunkop` branch and that low-level create returns a locked chunk only on success. Static analysis should flag mismatched macro argument counts and any caller that fails to release returned chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/hddspacemgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/indexed_resource_pool.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/indexed_resource_pool.h

## Purpose
`indexed_resource_pool.h` defines `IndexedResourcePool`, a small template used to keep integer-indexed resources accessible by ID while also maintaining an LRU-style release list. In this subset it backs the open chunk descriptor pool, allowing descriptors to be retained after close and later freed when old or under pressure.

## Important APIs, Types, and Functions
`IndexedResourcePool<Resource, DefaultCapacity, ReleaseThreshold_s, PopUnusedCount>` stores `Entry` nodes in a vector indexed by resource ID. ID `0` is a sentinel list node. `acquire(id)` removes an existing resource from the unused list. `acquire(id, Resource&&)` installs or replaces resource data, resizing the vector when necessary. `release(id, timestamp)` moves a resource to the LRU tail. `purge(id)` calls `resource.purge()`, moves it to `purge_list_`, and removes it from the list. `freeUnused(now, extra_lock, count)` frees old removable resources by moving them into a local candidate vector whose destructors run outside the pool. `getResource(id)` returns a reference by index.

The `Resource` type must support default construction, move operations, `purge()`, `canRemove()`, and destructor-based release semantics.

## Control Flow
Resources are acquired while active, released with a timestamp when idle, and later scanned from the list front by `freeUnused`. The pool first flushes pending purge resources, snapshots the current front into `garbage_collector_head_`, then repeatedly takes an external lock and the pool mutex before checking age and `canRemove()`. Removable resources are moved to local candidates and erased from the linked list; non-removable entries advance the scan head.

## State and Persistence Behavior
All state is in memory: the indexed vector, sentinel-based doubly linked list, purge list, mutex, and current garbage collector cursor. Persistence effects happen only through the `Resource` destructor or `purge()` implementation, such as closing file descriptors.

## Dependencies and Integration Points
The template uses `common/small_vector.h`, standard mutex/vector machinery, and the chunkserver `Chunk` include for local resource types. `hddspacemgr.cc` uses `IndexedResourcePool<OpenChunk>` to cache and retire open chunk descriptors while coordinating with the global chunk registry lock.

## Risks and Edge Cases
`purge(id)` does not bounds-check `id` before indexing, unlike `acquire` resize behavior. `contains(id)` assumes a valid positive ID. The list implementation relies on sentinel node `data_[0]`; corruption of `prev`/`next` values can affect later erases. `freeUnused` intentionally locks `extra_lock` before `mutex_` inside the loop; callers must ensure this ordering is compatible with the rest of the subsystem. Resource destruction is delayed by `purge_list_` and candidate vectors, so tests must account for destructor timing.

## Test Signals
Unit tests should cover acquire/release order, resize on high IDs, purge and destructor behavior, `freeUnused` age threshold, `canRemove=false` skipping, sentinel front/back updates, and invalid IDs. Concurrency tests should stress acquire/release/freeUnused with a mock resource that records destructor and purge calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/indexed_resource_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/init.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/init.h

## Purpose
`init.h` defines the chunkserver module initialization order through three `run_tab` arrays. It is included by the generic server startup machinery to run early, normal, and late initialization functions with human-readable names.

## Important APIs, Types, and Functions
The file defines `typedef int (*runfn)(void)` and `struct run_tab { runfn fn; const char *name; }`. `RunTab` initializes the random generator, HDD space manager, main network server module, master connection module, and charts. `LateRunTab` starts master connection threads, HDD space manager threads, and network worker threads. `EarlyRunTab` is currently empty except for its sentinel.

## Control Flow
Normal initialization runs `rnd_init`, `hdd_init`, `mainNetworkThreadInit`, `masterconn_init`, and `chartsdata_init`. The comment notes that main network initialization must precede master connection so registration can advertise the listening address. Late initialization then creates job pools/background threads for master, HDD, and network serving.

## State and Persistence Behavior
This file stores only static initialization tables. It indirectly controls persistent behavior by ensuring HDD folders are parsed and scanned before threads begin and by registering event-loop destructors/reload hooks in the initialized modules.

## Dependencies and Integration Points
Includes pull in charts, HDD manager, master connection, network main thread, and random initialization. The arrays are consumed by the chunkserver's process bootstrap code outside this file.

## Risks and Edge Cases
Ordering is the key risk. Moving `masterconn_init` before `mainNetworkThreadInit` can break registration address reporting. Starting late threads before normal init finishes can expose uninitialized globals or missing event-loop hooks. The arrays use a null function sentinel, so consumers must stop on `(runfn)0`.

## Test Signals
Startup/integration tests should assert initialization order, successful registration after network listen setup, and clean shutdown after all modules register destructors. A compile-time or small runtime test can verify each table remains sentinel-terminated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/iostat.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/iostat.h

## Purpose
`iostat.h` provides the chunkserver's disk load estimator. On non-Linux systems it is a no-op. On Linux it samples `/proc/diskstats` for devices backing configured HDD paths and computes a weighted load factor that can be reported to the master.

## Important APIs, Types, and Functions
The public class `IoStat` has `resetPaths(const std::vector<std::string>&)` and `getLoadFactor()`. The Linux implementation maps `dev_t` to `StatEntry { ticks, size }`, where `ticks` is the previous total I/O tick count and `size` is filesystem block count from `statfs`. Constants define diskstats parsing limits and expected field count.

## Control Flow
`resetPaths` clears cached timestamp/load, stats each configured path, obtains filesystem size, and records the path's device. `getLoadFactor` returns cached load if called more than once in the same second, opens `/proc/diskstats`, scans all devices, and for matching devices accumulates `(current_tot_ticks - previous_ticks) * filesystem_size`. It divides by total size, elapsed seconds, and `10` to convert milliseconds of I/O time into a percentage-like factor, clamps to `100`, updates previous ticks and timestamp, and returns the result.

## State and Persistence Behavior
The class is runtime-only and keeps a previous sample per device plus cached load/timestamp. It reads kernel procfs state but does not persist anything. Missing paths, failed `statfs`, empty device maps, and failed `/proc/diskstats` reads produce a zero load factor.

## Dependencies and Integration Points
`hddspacemgr.cc` owns a global `IoStat gIoStat`, calls `resetPaths` after HDD config reload, and exposes `hdd_get_load_factor`. `masterconn.cc` optionally sends changed load factors in `masterconn_send_status` when `ENABLE_LOAD_FACTOR` is configured.

## Risks and Edge Cases
The calculation assumes Linux `/proc/diskstats` field semantics and total tick monotonicity. Device mapper, partitions, bind mounts, or multiple paths on one device can skew weighting. The first sample after reset uses `prev_timestamp_ = 0`, which makes the first computed load mostly a baseline reset rather than an accurate recent window. Integer arithmetic and one-second caching can hide short spikes.

## Test Signals
Unit tests can use a factored parser or fixture text for diskstats, checking matching devices, clamp-to-100, same-second caching, and zero behavior. Integration tests should verify `resetPaths` ignores invalid paths and that enabling load-factor reporting sends status changes without flooding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/iostat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/legacy_replicator.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/legacy_replicator.cc

## Purpose
`legacy_replicator.cc` implements the old MooseFS/LizardFS chunk replication protocol. It connects to one or more source chunkservers, asks for block counts, streams full blocks with CRCs, writes them into a newly created local standard chunk, and finally changes the local chunk to the requested version.

## Important APIs, Types, and Functions
The exported functions are `legacy_replicator_stats` and `legacy_replicate`. Internal structs `repsrc` and `replication` track source sockets, packet buffers, chunk identity/version, block counts, poll descriptors, destination state, and an optional XOR buffer. Helpers include `rep_read`, `rep_receive_all_packets`, `rep_create_packet`, `rep_write`, `rep_send_all_packets`, `rep_wait_for_connection`, and `rep_cleanup`.

## Control Flow
`legacy_replicate` validates `srccnt`, increments replication stats, creates a local chunk with version `0`, parses each source record `(chunkid, version, ip, port)`, opens nonblocking TCP connections, waits for connect completion, opens the local chunk, and sends `CSTOCS_GET_CHUNK_BLOCKS` to all sources. It validates each `CSTOCS_GET_CHUNK_BLOCKS_STATUS`, determines the maximum block count, sends `CLTOCS_READ` requests, waits for replication bandwidth limiter approval, then receives each block's `CSTOCL_READ_DATA` packet. For each block it validates chunk ID, block number, offset, and size, then writes the block via `hdd_write`. After final read statuses are OK, it closes the local chunk and updates its version with `hdd_version`.

## State and Persistence Behavior
The destination chunk is persistent on disk once `hdd_create` succeeds. `rep_cleanup` closes sockets, frees packet buffers, closes the local chunk if opened, and deletes the destination chunk if replication did not reach the final version step. The implementation uses runtime counters guarded by a pthread mutex. It does not persist protocol progress separately.

## Dependencies and Integration Points
The code depends on socket wrappers, datapack helpers, CRC/protocol constants, `hddspacemgr` operations, and `replicationBandwidthLimiter`. `masterconn.cc` schedules it through background jobs for legacy `MATOCS_REPLICATE` requests.

## Risks and Edge Cases
The code is synchronous and poll-based, so large or slow replications occupy a bgjob worker. Packet size and exact type/length checks are strict. Current logic asserts `vbuffs <= 1`, so the old XOR multi-source behavior is effectively not used despite allocation of `xorbuff`. Cleanup correctness is critical because failures after create/open must remove incomplete chunks. Timeouts are fixed at 5 seconds per connect/send/receive phase, which can be brittle on slow links.

## Test Signals
Protocol tests should simulate source chunkservers returning block counts, data, early statuses, wrong IDs/versions, disconnects, malformed packet sizes, and final status errors. Disk-side tests should verify incomplete destination cleanup and successful version update. Rate-limit tests should cover limiter denial before sending reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/legacy_replicator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/legacy_replicator.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/legacy_replicator.h

## Purpose
`legacy_replicator.h` exposes the legacy chunk replication entry points used by background jobs and master command handling.

## Important APIs, Types, and Functions
`legacy_replicator_stats(uint32_t *repl)` drains and resets the replication operation counter. `legacy_replicate(uint64_t chunkid, uint32_t version, uint8_t srccnt, const uint8_t *srcs)` performs a replication from a packed source list. The source list format is documented as `srccnt * (chunkid:64 version:32 ip:32 port:16)`.

## Control Flow
Callers pass a destination chunk ID/version and one or more packed source descriptors. The implementation creates the destination chunk, pulls block data from sources, writes it, and returns a LizardFS status byte.

## State and Persistence Behavior
The header itself has no state. Its implementation persists the replicated chunk on local HDD storage only after successful completion; failed runs attempt cleanup.

## Dependencies and Integration Points
It includes platform and integer types. `masterconn.cc` uses this API indirectly through job-pool functions for `MATOCS_REPLICATE`. `legacy_replicator.cc` depends on `hddspacemgr` and socket/protocol helpers.

## Risks and Edge Cases
The packed `srcs` buffer has no length parameter in this API, so caller-side validation of `srccnt` and packet length is mandatory. It only represents legacy standard chunk replication; newer EC/chunk-type-aware replication is handled elsewhere.

## Test Signals
Tests should verify master packet handlers compute `srccnt` correctly before calling this function and reject malformed lengths. ABI/compile tests should ensure the function remains available for legacy job wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/legacy_replicator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/masterconn.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/masterconn.cc

## Purpose
`masterconn.cc` owns the chunkserver's single connection to the master. It registers the chunkserver and its chunks, sends disk/health/chunk reports, receives master commands, schedules HDD and replication jobs, and manages reconnection/reload behavior in the event loop.

## Important APIs, Types, and Functions
The file exports `masterconn_stats`, `masterconn_init`, and `masterconn_init_threads`. Internal `masterconn` stores connection mode, socket, poll position, timers, `InputPacket`, queued `OutputPacket`s, bind/master addresses, and address validity. Packet helpers create/attach/delete output packets. Registration/report functions include `masterconn_sendregister`, `masterconn_sendregisterlabel`, and `masterconn_check_hdd_reports`. Command handlers include create/delete/set-version/duplicate/truncate/duptrunc, generic `MATOCS_CHUNKOP`, modern and legacy replication, plus completion callbacks that patch status fields into queued response packets.

## Control Flow
Initialization reads master/bind config, timeout, label, and load-factor setting, creates the singleton, initiates a nonblocking connection, and registers event-loop callbacks for polling, reconnect, report checks, load status, reload, and destruction. On connect, `masterconn_connected` enables TCP_NODELAY, sends host registration, bulk chunk inventory from `hdd_foreach_chunk_in_bulks`, space data, and label.

The event loop calls `masterconn_desc` to add the master socket and job-pool fd to `poll`. `masterconn_serve` handles connect completion, job completions, reads, writes, timeout NOPs, and KILL cleanup. `masterconn_read` parses packets until the watchdog expires or the job queue is near full, dispatching by packet type in `masterconn_gotpacket`. Command handlers deserialize protocol messages, allocate response packets, and schedule background jobs against `jpool`. `masterconn_check_hdd_reports` drains disk-space changes, error counters, damaged/lost/new chunks, and queues master notifications.

## State and Persistence Behavior
Connection state and queued packets are runtime-only. Persistent effects occur through scheduled `hddspacemgr` jobs and replication jobs. Config reload can change master address, bind address, timeout, reconnection delay, label, and load-factor reporting. If connection state becomes `KILL`, all active jobs have callbacks changed to an unwanted-job cleanup callback, the socket closes, packet queues clear, and the mode returns to `FREE` for later reconnect.

## Dependencies and Integration Points
Dependencies include bgjobs, HDD manager, network listener address APIs, event loop, config, loop watchdog, packet serializers/deserializers, and cstoma/matocs protocol builders. It is initialized after the main network listener so it can advertise the chunkserver service address. It initializes its job pool in `masterconn_init_threads`.

## Risks and Edge Cases
Backpressure is tied to `BGJOBSCNT`; reads stop when jobs reach 90% to avoid unbounded work. Packet status callbacks mutate fixed offsets in legacy packets, so packet layout changes are risky. Label validation can fail initialization. Reconnect/reload paths must avoid using freed `MasterHost`, `MasterPort`, and `BindHost`. Master localhost addresses are rejected. Replication is refused while HDD scans are in progress.

## Test Signals
Integration tests should cover registration contents, chunk bulking, report drains, command dispatch for each packet type, job completion status serialization, reconnect after timeout/KILL, reload with changed bind/master/label, and job queue saturation. Protocol fuzzing should assert malformed packets set `KILL` without leaking packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/masterconn.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/masterconn.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/masterconn.h

## Purpose
`masterconn.h` declares the small public surface of the master connection module.

## Important APIs, Types, and Functions
`masterconn_stats(uint64_t *bin, uint64_t *bout, uint32_t *maxjobscnt)` drains byte and max-job counters. `masterconn_init()` initializes config, singleton connection state, event-loop hooks, and starts connecting. `masterconn_init_threads()` creates the background job pool used for master-directed HDD and replication work.

## Control Flow
Startup calls `masterconn_init` during normal module initialization and `masterconn_init_threads` during late/thread initialization. Runtime behavior is then event-loop driven inside the implementation.

## State and Persistence Behavior
The header itself has no state. The implementation maintains connection and job-pool runtime state and causes persistent chunk changes by scheduling HDD operations.

## Dependencies and Integration Points
It includes only platform and integer headers. `init.h` references both init functions. Stats consumers can call `masterconn_stats` for charts/monitoring.

## Risks and Edge Cases
The API hides most lifecycle details, so call order matters: `masterconn_init_threads` assumes normal initialization has prepared the singleton/config. Stats are drain-and-reset, so multiple consumers would race semantically.

## Test Signals
Startup tests should assert `masterconn_init` precedes `masterconn_init_threads`. Stats tests should verify drain/reset behavior through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/masterconn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_main_thread.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/network_main_thread.cc

## Purpose
`network_main_thread.cc` owns the chunkserver listening socket and dispatches accepted client/peer connections to worker threads. It also reloads listener and replication/read-ahead settings and starts/stops `NetworkWorkerThread` instances.

## Important APIs, Types, and Functions
Public functions are `mainNetworkThreadInit`, `mainNetworkThreadInitThreads`, `mainNetworkThreadGetListenIp`, and `mainNetworkThreadGetListenPort`. Internal functions include `mainNetworkThreadReload`, `mainNetworkThreadDesc`, `mainNetworkThreadServe`, `mainNetworkThreadTerm`, `chunkReplicatorReload`, and `replicationBandwidthLimitReload`. Global state tracks `lsock`, listener poll position, worker thread/object lists, round-robin iterator, listen IP/port, and worker/job/read-ahead configuration.

## Control Flow
`mainNetworkThreadInit` reads listen host/port and worker counts, configures read-ahead, creates a nonblocking TCP listening socket, resolves/listens, registers event-loop poll/reload/destructor hooks, initializes replication bandwidth limiting, and reloads chunk replicator timeouts. The poll descriptor callback adds the listen socket. The serve callback accepts one pending connection, checks the next worker's job queue, either closes on saturation or hands the socket to that worker, and advances round-robin.

`mainNetworkThreadInitThreads` constructs configured `NetworkWorkerThread` objects and starts one `std::thread` per object. Reload can replace the listening socket if address changes, update bandwidth/read-ahead/replicator settings, and warn that worker-count settings require restart.

## State and Persistence Behavior
This module is runtime-only. It does not persist data, but accepted sockets drive persistent chunk operations in workers. Reload changes the active listen socket without restarting the process. Destruction closes the listener, frees config strings, asks all workers to terminate, and joins their threads.

## Dependencies and Integration Points
It depends on bgjobs, HDD readahead, network stats, worker thread definitions, chunk replicator globals, config/event-loop helpers, and socket wrappers. `masterconn.cc` queries listen IP/port during registration. `init.h` requires this module to initialize before master connection.

## Risks and Edge Cases
Reload swaps `lsock` while the event loop is active, so descriptor registration must see the new value next poll cycle. Only one accept is attempted per serve call, which can throttle bursts. Worker selection uses job-pool occupancy as admission control; a worker with many idle connections but low jobs can still receive more sockets. Worker-count changes are not applied live.

## Test Signals
Integration tests should cover listen creation, address reload success/failure rollback, connection round-robin, saturation close behavior, clean worker termination, and master registration using the resolved listen address. Config reload tests should verify read-ahead and replication limits update live.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_main_thread.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_main_thread.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/network_main_thread.h

## Purpose
`network_main_thread.h` declares the chunkserver network listener module API.

## Important APIs, Types, and Functions
`mainNetworkThreadInit()` sets up listener configuration and event-loop callbacks. `mainNetworkThreadInitThreads()` creates worker objects and threads. `mainNetworkThreadGetListenIp()` and `mainNetworkThreadGetListenPort()` expose the advertised chunkserver service address.

## Control Flow
The init table calls normal initialization before master connection, then calls thread initialization in the late phase. Master registration later queries the listen address through this header.

## State and Persistence Behavior
No state is stored in the header. The implementation owns runtime sockets and workers and does not persist data directly.

## Dependencies and Integration Points
This header includes platform and integer types only. It is consumed by `init.h` and `masterconn.cc`.

## Risks and Edge Cases
The address getters are only meaningful after successful `mainNetworkThreadInit`. Calling them too early could expose default/uninitialized globals from the implementation.

## Test Signals
Startup-order tests should verify listener initialization precedes master registration. Address tests should verify configured host/port resolution is reflected by getters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_main_thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_stats.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/network_stats.cc

## Purpose
`network_stats.cc` defines global atomic counters for client/peer network traffic and high-level operation counts, plus a drain function for chart/status consumers.

## Important APIs, Types, and Functions
It defines `stats_bytesin`, `stats_bytesout`, `stats_hlopr`, `stats_hlopw`, and `stats_maxjobscnt`. `networkStats` atomically exchanges each counter with zero and writes the drained values to caller-provided pointers.

## Control Flow
Network worker code increments byte counters on socket reads/writes, increments high-level read/write operation counters on request start, and updates max job count during polling. Consumers call `networkStats` periodically to obtain deltas.

## State and Persistence Behavior
All state is in atomic process memory and is reset on each drain. There is no persistence.

## Dependencies and Integration Points
The file includes `network_stats.h`. `network_worker_thread.cc` and `network_main_thread.cc` use these counters; charts or monitoring code can call `networkStats`.

## Risks and Edge Cases
`stats_maxjobscnt` is updated racily in worker code and drained with exchange, so it is approximate. Drain-and-reset means multiple consumers would split counts. Atomic increments avoid data races but do not make multi-counter snapshots consistent.

## Test Signals
Unit tests can set counters and verify `networkStats` returns values and resets them. Stress tests can increment concurrently and verify no torn reads or crashes, accepting approximate max-job behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_stats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_stats.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/network_stats.h

## Purpose
`network_stats.h` declares shared atomic network/stat counters and the drain API used by the chunkserver network subsystem.

## Important APIs, Types, and Functions
The header declares extern atomics for bytes in/out, high-level read/write operation counts, and maximum observed job count. `networkStats` drains these into output pointers.

## Control Flow
Worker code updates the extern counters directly. Monitoring/chart code calls `networkStats` to obtain interval deltas and reset counters.

## State and Persistence Behavior
The header declares runtime-only process counters. They are not persisted and are reset through exchange in the implementation.

## Dependencies and Integration Points
It depends on platform, integer, and atomic headers. It is included by worker/main network code and any chart/stat collector.

## Risks and Edge Cases
Direct extern counter access makes it easy for future code to update the wrong metric or bypass desired aggregation rules. Drain semantics require a single logical consumer.

## Test Signals
Compile tests should ensure exactly one definition exists. Stats tests should verify counter increments in worker read/write paths become visible through `networkStats`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.cc

## Purpose
`network_worker_thread.cc` implements per-connection chunkserver protocol handling. Each `NetworkWorkerThread` owns a poll loop, a background HDD job pool, and a list of client/peer connections. It serves reads, writes, prefetches, HDD info, charts, chunk tests, get-blocks requests, and chained write forwarding to another chunkserver.

## Important APIs, Types, and Functions
The file defines protocol serializers (`MessageSerializer`, `MooseFsMessageSerializer`, `LizardFsMessageSerializer`), packet allocation/attachment helpers, read handlers (`worker_read_init`, `worker_read_continue`, `worker_read_finished`), write handlers (`worker_write_init`, `worker_write_data`, `worker_write_status`, `worker_write_end`, `worker_write_finished`), forwarding handlers (`worker_initconnect`, `worker_fwdwrite`, `worker_forward`, `worker_fwdread`), misc handlers for ping/HDD list/chart/test/get-blocks, and the `NetworkWorkerThread` methods declared in the header.

## Control Flow
Accepted sockets arrive through `NetworkWorkerThread::addConnection`, which sets TCP options, creates a `csserventry`, and wakes the worker pipe. The thread loop calls `preparePollFds`, polls with a short timeout, drains job completions, and calls `servePoll`. Each connection has a state machine: `IDLE` accepts new commands; `READ` schedules block reads and queues read-data/status packets; `GET_BLOCK` waits for `job_get_blocks`; `WRITELAST` writes locally; `CONNECTING`/`WRITEINIT`/`WRITEFWD` set up and operate a chained write to another chunkserver; `WRITEFINISH` sends final error/success status before closing; close states disable or wait for jobs and release resources.

Read requests are split at block boundaries. The worker builds a response prefix, schedules `job_read` with optional open/read-ahead/read-behind, then sends each output buffer and finally an OK read status while closing the chunk. Write init deserializes a chain, optionally connects to the next chunkserver and forwards the remaining chain init, opens the local chunk, and transitions to local or forwarded write mode. Write data is preserved from the input packet while an HDD write job runs; local completion and forwarded status are matched with `partiallyCompletedWrites` before the upstream client is acked.

## State and Persistence Behavior
Per-connection runtime state includes sockets, packet buffers, output queues, active job IDs, forwarded socket buffers, write IDs awaiting local/remote completion, open chunk flag, chunk identity/type/version, read offset/size, and serializer selection. Persistent effects happen through bgjob calls into `hddspacemgr` for open/read/write/close/prefetch/get-blocks and through forwarded write chains on peer chunkservers. Termination closes open chunks, sockets, and allocated buffers, and deletes the job pool.

## Dependencies and Integration Points
The implementation depends on bgjobs, HDD manager and read-ahead settings, network stats, chart generation, protocol serializers for MooseFS and LizardFS packet variants, socket wrappers, event-loop time helpers, and request logging. `network_main_thread.cc` owns worker creation and dispatch. Legacy replication uses get-blocks/read protocol paths served here.

## Risks and Edge Cases
This is a high-risk state machine. Packet ownership alternates between raw `malloc` buffers, preserved input packets, linked output packets, and `OutputBuffer` objects. Write-chain correctness depends on matching local HDD completion with downstream status by write ID. Closing while a bgjob is active changes callbacks to delayed close, so callback identity and `chunkisopen` must stay consistent. Forwarded packets include headers for write data/end but local processing consumes payloads differently in forwarded vs non-forwarded paths. Timeout/retry logic can close slow but valid clients after `CSSERV_TIMEOUT`.

## Test Signals
Protocol tests should cover legacy and LizardFS read/write variants, EC chunk type deserialization, block-boundary read splitting, partial write validation, write-chain success and downstream failure, premature `WRITE_END`, get-blocks responses, prefetch fire-and-forget, HDD list serialization, and chart requests. Stress tests should exercise connection close during active read/write/get-block jobs, forwarded reconnect retries, packet-too-large rejection, network stats accounting, and leak checks for all packet ownership paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.cc -->
