# Research Group subset-b-007678

This grouped report covers the MooseFS chunkserver files assigned to `subset-b-007678`. Each source file has its own source-tree-preserving section for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/Makefile.am -->
# sources/distributed-fs/moosefs/mfschunkserver/Makefile.am

## Purpose
`Makefile.am` is the Automake source for the MooseFS chunkserver directory. It declares the programs installed into `sbin` and the source/link composition for `mfschunkserver`, `mfschunktool`, `mfscsstatsdump`, and `mfschunkdbdump`. It is the maintainable build contract that generates the much larger `Makefile.in`.

## Important Build Targets and Variables
The key exported target set is `sbin_PROGRAMS = mfschunkserver mfschunktool mfscsstatsdump mfschunkdbdump`. `AM_CPPFLAGS` points all local targets at `$(top_srcdir)/mfscommon`, while target-specific flags add dependency libraries. `mfschunkserver_CPPFLAGS` defines `MFSMAXFILES=16384`, `_USE_PTHREADS`, `APPNAME=mfschunkserver`, `USE_CONNCACHE`, and `USE_IONICE`; its CFLAGS/LDFLAGS pull in pthread, dynamic linker, zlib, and math libraries through configure substitutions.

`mfschunkserver_SOURCES` is the integration inventory for the daemon: local chunkserver modules (`bgjobs`, `csserv`, `mainserv`, `hddspacemgr`, `masterconn`, `busychunks`, `replicator`, `chartsdata`, `chartsdefs`, `init`) plus many `mfscommon` support modules for event-loop startup, config, queues, threading, CRC, sockets, connection cache, charts, memory and CPU accounting, logging, and protocol definitions. `mfscsstatsdump_SOURCES` reuses `chartsdefs.h` and common chart/stat dump helpers so the stats dump tool uses the same chart schema as the daemon.

## Control Flow and Integration
Automake consumes this file to produce `Makefile.in`; configure then instantiates a concrete `Makefile`. Runtime control flow is not here, but build-time dependency flow is: adding a chunkserver module without listing it in `mfschunkserver_SOURCES` excludes it from the daemon, while adding chart metrics without `chartsdefs.h` in the stats dump target would desynchronize dump tooling from daemon persistence.

## State and Persistence
The file does not persist runtime state. Its persistent effect is generated build metadata and installed binaries. `distclean-local` removes `./$(DEPDIR)` and `Makefile`, matching Automake cleanup expectations.

## Dependencies
This file depends on Autoconf/Automake substitutions for `PTHREAD_*`, `ZLIB_LIBS`, `MATH_LIBS`, and `DYNLINKER_FLAGS`. It depends structurally on `../mfscommon` for common daemon infrastructure and on local chunkserver modules for the daemon itself.

## Risks
The main risk is build drift: `Makefile.am` must remain the source of truth, or regenerated `Makefile.in` will overwrite manual generated-file edits. Target-specific CPPFLAGS are behaviorally important; dropping `_USE_PTHREADS`, `USE_CONNCACHE`, or `USE_IONICE` can alter threading, connection cache, or I/O scheduling paths. The stats dump tool depends on the exact chart definitions, so chart schema changes should update both daemon and tool source lists.

## Test Signals
Useful signals are a successful `autoreconf`/Automake regeneration, `./configure && make` in this subtree or repository, target link success for all four `sbin_PROGRAMS`, and `make distclean` removing generated dependency directories without leaving stale `Makefile` state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/Makefile.in -->
# sources/distributed-fs/moosefs/mfschunkserver/Makefile.in

## Purpose
`Makefile.in` is the Automake-generated template for building and installing the MooseFS chunkserver programs. It expands the concise `Makefile.am` into portable make rules for configure substitution, compilation, dependency tracking, installation, distribution packaging, tags, clean/distclean/maintainer-clean, and per-target object naming.

## Important Rules and Variables
The generated file preserves the same `sbin_PROGRAMS`: `mfschunkserver`, `mfschunktool`, `mfscsstatsdump`, and `mfschunkdbdump`. It defines object lists such as `am_mfschunkserver_OBJECTS`, including prefixed objects like `mfschunkserver-bgjobs.$(OBJEXT)` and common-module objects under `../mfscommon/mfschunkserver-*.o`. Target-specific compile/link commands use `mfschunkserver_CPPFLAGS`, `mfschunkserver_CFLAGS`, and `mfschunkserver_LDFLAGS`, while generic `COMPILE`, `LTCOMPILE`, and `LINK` rules handle common C compilation.

The file contains dependency-remake logic for `$(srcdir)/Makefile.in`, `Makefile`, `config.status`, `configure`, `aclocal.m4`, and generated `.Po` dependency files. Installation is handled through `install-sbinPROGRAMS` and `uninstall-sbinPROGRAMS`; distribution uses `DISTFILES`, `distdir`, `tags`, `ctags`, `cscopelist`, and generated source enumeration.

## Control Flow
Build flow starts with configure substituting `@...@` variables into `Makefile`. `all-am` depends on `Makefile` and `$(PROGRAMS)`. Each program target links its object set after pattern or explicit compile rules produce objects. The explicit rules for chunkserver modules use the target-prefixed object names and source fallback logic (`test -f 'bgjobs.c' || echo '$(srcdir)/'`) to support separate build directories.

Clean flow is layered: `clean` removes binaries and libtool artifacts, `distclean` also removes dependency files and `Makefile`, and `distclean-local` removes the local dependency directory. `maintainer-clean` repeats distclean-level removals and advertises that generated files may need maintainer tools to rebuild.

## State and Persistence
Runtime state is not involved. Build state includes generated object files, dependency files under `$(DEPDIR)`, libtool directories, installed binaries under `$(sbindir)`, and generated `Makefile`. The stats schema file `chartsdefs.h` is included in both daemon and stats dump distribution source sets, which keeps persisted chart file interpretation aligned.

## Dependencies and Integration Points
The template integrates with the top-level Autoconf/Automake system through `config.status`, `aclocal.m4`, m4 macro dependencies (`ax_pthread`, libtool macros), and configure-substituted paths and libraries. It integrates with `mfscommon` by compiling common C sources with target-specific prefixes so the same common modules can be built with chunkserver-specific preprocessor options.

## Risks
Manual edits to this generated file are fragile because Automake refresh rules can regenerate it from `Makefile.am`. Incorrect dependency tracking substitutions can break parallel or out-of-tree builds. Because the generated object lists are long and duplicated across `.o` and `.obj` rules, stale `Makefile.in` content after changing `Makefile.am` can cause source omission or platform-specific build failures.

## Test Signals
The strongest signals are successful `./configure`, `make all-am`, and target links for all four programs. Additional signals are successful VPATH builds, `make install DESTDIR=...`, `make distcheck` or `make distdir`, and clean/distclean runs that remove generated objects and dependency files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/bgjobs.c -->
# sources/distributed-fs/moosefs/mfschunkserver/bgjobs.c

## Purpose
`bgjobs.c` implements the chunkserver background job subsystem. It keeps slow or blocking work out of the main event loop by dispatching disk operations, client read/write service calls, replication, chunk-info queries, and disk moves to worker threads. It also reports load, high-load status, per-task timing counters, and stalled jobs.

## Important Types and APIs
The file defines operation codes (`OP_CHUNKOP`, `OP_SERV_READ`, `OP_SERV_WRITE`, replication modes, `OP_GETINFO`, `OP_CHUNKMOVE`) and task categories (`TASK_READ`, `TASK_WRITE`, `TASK_REPLICATE`, `TASK_CHUNKOP`, `TASK_INFO`, `TASK_MOVE`). Argument structs hold per-operation parameters: `chunk_op_args`, `chunk_rw_args`, `chunk_rp_args`, `chunk_ij_args`, and `chunk_mv_args`.

`job` records the public job id, callback, callback extra pointer, operation arguments, state (`JSTATE_ENABLED`, `DISABLED`, `INPROGRESS`), task type, start timestamp, and debug chunk id. `jobpool` owns a pipe pair for poll-loop wakeups, worker counts and watermarks, mutexes/condition variable, pcqueue job/status queues, a job hash table, and timing counters.

Public entry points include `job_chunkop`, `job_serv_read`, `job_serv_write`, `job_replicate_simple`, `job_replicate_split`, `job_replicate_recover`, `job_replicate_join`, `job_get_chunk_info`, `job_chunk_move`, `job_pool_disable_job`, `job_pool_change_callback`, `job_get_load_and_hlstatus`, and `job_init`.

## Control Flow
`job_init` creates high-priority and low-priority pools, reloads worker limits from config, and registers destruct, can-exit, reload, each-loop, poll, info, periodic counter-shift, and stalled-job callbacks with the common `main` framework. Each pool starts with one worker. `job_new` allocates a `job`, assigns a nonzero id, inserts it into the pool hash, checks queue pressure against `workers_max`, and either queues the job, returns zero for limited-return callers, or emits an immediate error status.

`job_worker` waits on the job queue, marks enabled jobs in progress, may spawn another worker when all workers become busy and the pool is below its max, dispatches to `hdd_chunkop`, `mainserv_read`, `mainserv_write`, `replicate`, `hdd_get_chunk_info`, or `hdd_move`, records timing statistics, then enqueues completion status. The main poll loop watches pool pipes through `job_desc` and calls `job_serve`; `job_pool_check_jobs_in_pool` receives statuses, invokes callbacks, removes hash entries, frees args, and frees jobs.

## State and Persistence
State is in-memory: two global pools, job hash tables, queues, counters, worker counts, high-load status, and pipe readability. No durable state is written. Worker settings come from configuration keys `WORKERS_MAX`, `WORKERS_HLOAD_HIMARK`, `WORKERS_HLOAD_LOMARK`, and `WORKERS_MAX_IDLE`; reload updates both pools.

## Dependencies and Integration Points
This module depends on `pcqueue` for cross-thread queues, `lwthread` and pthread primitives for workers, `main` for event-loop registration, `hddspacemgr` for disk/chunk work, `replicator` for chunk replication, `mainserv` for client I/O serving, `masterconn` for load reporting, `cfg` for tuning, `ionice` for low-priority workers, and `clocks` for monotonic timing.

## Risks
Callbacks run from the main poll context while job execution runs in workers, so callback ownership and lifetime must be clear. Disabled jobs still occupy queue/hash state until completed or drained. `job_new` allocates before checking queue pressure; it carefully removes limited-return jobs, but any future path must preserve that cleanup. `job_pool_disable_job` and `job_pool_change_callback` search both pools by job id, so job ids are not globally unique by construction; a rare id collision across pools could affect both. Worker growth is opportunistic and controlled only by counts/watermarks, so bad config can create resource pressure despite validation warnings.

## Test Signals
Useful tests include queue-full behavior for `JOB_MODE_LIMITED_RETURN` and `JOB_MODE_LIMITED_QUEUE`, cancellation before and during execution, callback replacement, worker high/low watermark transitions and `masterconn_reportload`, stalled-job logging after the 600-second threshold, graceful shutdown waiting for workers, and integration tests where client read/write and replication jobs complete through the poll pipe path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/bgjobs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/bgjobs.h -->
# sources/distributed-fs/moosefs/mfschunkserver/bgjobs.h

## Purpose
`bgjobs.h` is the public interface for the chunkserver background job subsystem. It exposes asynchronous job submission APIs, cancellation/callback mutation, load reporting, chunk operation convenience macros, and initialization.

## Important APIs
`job_stats` returns and resets the maximum observed job count for charting. `job_get_load_and_hlstatus` returns current total queued/running load and high-load status. `job_pool_disable_job` disables a pending job, while `job_pool_change_callback` changes its completion callback and extra pointer.

`job_chunkop` is the generic disk chunk mutation submission function, parameterized by `chunkid`, current version, new version, optional copy chunk/version, and length. Macros map common operations to that shape: `job_delete`, `job_create`, `job_test`, `job_version`, `job_truncate`, `job_duplicate`, `job_duptrunc`, and `job_split`. Some macros validate arguments and route invalid requests to `job_inval`.

Client service work is submitted with `job_serv_read` and `job_serv_write`; replication work with `job_replicate_simple`, `job_replicate_split`, `job_replicate_recover`, and `job_replicate_join`; metadata/info work with `job_get_chunk_info` and convenience macros for blocks, checksum, and checksum tables; disk relocation with `job_chunk_move`. `job_init` starts the subsystem and registers it with the main event loop.

## Control Flow and Integration
Callers enqueue jobs and receive a numeric job id. Completion is asynchronous through `void (*callback)(uint8_t status, void *extra)`. The callback status uses MooseFS protocol status/error constants from `MFSCommunication.h`. The service layer (`csserv.c`) stores returned job ids so it can disable jobs when a connection closes. Master and disk-management code use chunk-operation and replication APIs to avoid blocking the event loop.

## State and Persistence
This header declares no state; all state is owned by `bgjobs.c`. Jobs are volatile and not replayed after process restart. The pointer arguments passed as callback extras remain caller-owned unless the implementation explicitly frees its internal argument blocks.

## Dependencies
The header includes `MFSCommunication.h` for constants such as `MAX_EC_PARTS`, `REQUEST_BLOCKS`, `REQUEST_CHECKSUM`, and error/status codes. It includes `<inttypes.h>` for fixed-width integer types.

## Risks
The macros encode sentinel values (`0xFFFFFFFF`, `0x80000000`) that must match `hdd_chunkop` semantics. Callers must check for job id zero on limited-return APIs such as service read/write because zero means the job was not queued. Callback extras must remain valid until callback or explicit callback removal. Replication arrays must contain at least `parts` valid entries and must not exceed `MAX_EC_PARTS`.

## Test Signals
Compilation across all include sites is a basic API compatibility signal. Runtime tests should assert invalid macro inputs produce `MFS_ERROR_EINVAL`, service APIs return zero under configured saturation, and cancellation/callback mutation through a stored job id prevents callbacks from dereferencing closed connection state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/bgjobs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/busychunks.c -->
# sources/distributed-fs/moosefs/mfschunkserver/busychunks.c

## Purpose
`busychunks.c` maintains a small in-memory hash table of chunks that are currently busy, associating each busy chunk with an opaque packet pointer. It is a lightweight guard/helper for code that needs to prevent duplicate or conflicting handling for the same chunk id.

## Important Types and Functions
`busy_chunk` stores the opaque `packet`, normalized `chunkid`, and intrusive linked-list pointers (`next`, `prev`). `bchashmap` is a static array of 1024 bucket heads. `busychunk_hashfn` maps a normalized chunk id to a bucket by modulo.

`busychunk_start(packet, chunkid)` masks the chunk id with `0x00FFFFFFFFFFFFFF`, allocates a `busy_chunk`, inserts it at the head of the relevant bucket, and returns the entry pointer as an opaque handle. `busychunk_end(vbc)` unlinks the entry, frees it, and returns the original packet pointer. `busychunk_isbusy(chunkid)` scans one bucket for a normalized chunk id and returns `1` or `0`. `busychunk_init` clears all bucket heads.

## Control Flow
The expected lifecycle is start, optional repeated busy checks, then end with the handle returned by start. The module does not reject duplicate starts for the same normalized chunk id; callers must call `busychunk_isbusy` first if duplicates should be suppressed.

## State and Persistence
All state is process-local and volatile. There is no locking, persistence, or reference counting. The stored packet pointer is opaque and not freed by this module.

## Dependencies and Integration
Only libc allocation and fixed-width types are used. The chunk-id mask is an important integration detail for MooseFS chunk-id encoding: high bits are ignored for busy tracking, matching code that treats the lower 56 bits as the chunk identity.

## Risks
The module is not thread-safe. If called from worker threads without external serialization, bucket links can corrupt. Allocation failures are not checked. Duplicate starts for the same chunk id are allowed, so `busychunk_end` on one handle may leave the chunk still busy if another entry exists. Passing an invalid or already-ended handle to `busychunk_end` will corrupt memory.

## Test Signals
Focused tests should cover initialization, start/isbusy/end, hash collisions, high-byte masking equivalence, duplicate starts, and returning the original packet pointer on end. Concurrency tests only make sense if callers intend to use it outside the single-threaded event-loop context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/busychunks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/busychunks.h -->
# sources/distributed-fs/moosefs/mfschunkserver/busychunks.h

## Purpose
`busychunks.h` declares the small busy-chunk tracking API used by chunkserver code to mark chunk ids as in-use and recover an associated packet pointer when the busy period ends.

## Important APIs
`busychunk_start(void *packet, uint64_t chunkid)` starts tracking a chunk and returns an opaque handle. `busychunk_end(void *vbc)` ends tracking for that handle and returns the `packet` pointer supplied at start. `busychunk_isbusy(uint64_t chunkid)` checks whether a normalized chunk id is present. `busychunk_init(void)` clears the internal hash table.

## Control Flow and State
The header exposes a strict handle lifecycle: callers should store the return value from `busychunk_start` and pass that exact value to `busychunk_end`. The implementation stores only in-memory state and treats `packet` as opaque caller-owned data.

## Dependencies
The only dependency is `<inttypes.h>` for `uint64_t` and `uint8_t`. There are no MooseFS protocol dependencies in the public header.

## Risks
The API does not expose errors for allocation failure, duplicate chunk starts, or invalid handles. It also does not communicate thread-safety constraints; callers need to know from the implementation or usage context that external serialization is required.

## Test Signals
Tests should verify that start returns a non-null handle, `isbusy` observes the normalized chunk id, end returns the same packet pointer, and `isbusy` clears after end. Include tests around chunk ids that differ only in the high byte because the implementation masks those bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/busychunks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/chartsdata.c -->
# sources/distributed-fs/moosefs/mfschunkserver/chartsdata.c

## Purpose
`chartsdata.c` is the chunkserver metrics collection bridge. It periodically samples CPU, memory, master traffic, client service traffic, disk I/O, replication, chunk operations, space usage, disk health, and chunk layout counters, then writes those samples into the common MooseFS charts subsystem.

## Important Functions
`chartsdata_refresh` fills a `uint64_t data[CHARTS]` array initialized to `CHARTS_NODATA`. It samples CPU with `cpu_used`, memory with `mem_used`, master traffic with `masterconn_stats`, background load with `job_stats`, service traffic with `csserv_stats` and `mainserv_stats`, disk metrics with `hdd_stats`, replication with `replicator_stats`, operation counts with `hdd_op_stats`, space with `hdd_get_space`, and disk/chart detail with `hdd_get_chart_data`. It then calls `charts_add(data, main_time() - 60)`.

`chartsdata_store` calls `charts_store`. `chartsdata_term` forces one final refresh, stores chart data, and terminates the charts subsystem. `chartsdata_init` initializes CPU tracking, registers refresh every 60 seconds, store every 3600 seconds offset by 30 seconds, registers destruct handling, and calls `charts_init` with `CALCDEFS`, `STATDEFS`, `ESTATDEFS`, and `CHARTS_FILENAME`.

## Control Flow
The module is passive after initialization. The common main loop invokes registered time callbacks. Each refresh consumes delta-style counters from contributing modules; several stats functions reset their counters after returning, so refresh cadence controls aggregation windows. The timestamp uses `main_time() - 60`, indicating the sample represents the preceding minute.

## State and Persistence
Persistent chart data is managed by `charts.c` using `CHARTS_FILENAME` (`csstats.mfs`) from `chartsdefs.h`. This file itself holds only static definitions generated from macros. Termination explicitly stores data to reduce loss on shutdown.

## Dependencies and Integration
This module integrates almost every chunkserver subsystem that exposes counters: `bgjobs`, `csserv`, `mainserv`, `masterconn`, `hddspacemgr`, and `replicator`. It also depends on common `charts`, `main`, `cpuusage`, and `memusage`. The numeric indexes in `chartsdefs.h` must match the positions filled here.

## Risks
Metric ordering is brittle: a mismatch between `CHARTS_*` indexes and `STATDEFS` corrupts chart meaning. Counter reset semantics mean accidental double refresh or missing refresh changes observed rates. Some fields are added together, such as `CHARTS_CSSERVIN/OUT` including both `csserv` and `mainserv` bytes; changing one source can affect historical interpretation. `data[CHARTS_CHANGE]` is derived from several operation counters and must be updated when chunk-changing operations expand.

## Test Signals
Signals include successful `chartsdata_init`, creation/loading of `csstats.mfs`, periodic samples with non-`CHARTS_NODATA` values after simulated activity, final store on destruct, and stats dump compatibility through `mfscsstatsdump`. Unit-style tests can stub provider stats and assert exact `CHARTS_*` array positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/chartsdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/chartsdata.h -->
# sources/distributed-fs/moosefs/mfschunkserver/chartsdata.h

## Purpose
`chartsdata.h` declares the initialization entry point for chunkserver chart collection.

## Important API
`int chartsdata_init(void)` initializes CPU usage tracking, registers periodic chart refresh and store callbacks, registers chart shutdown handling, and initializes the common charts subsystem through the implementation.

## Control Flow and Integration
The header is consumed by startup code that initializes chunkserver modules. After `chartsdata_init` succeeds, the module operates via callbacks registered with the common `main` loop. Callers do not drive refresh directly through this header.

## State and Persistence
No state is declared in the header. The implementation persists chart samples through the common chart store file named by `chartsdefs.h`.

## Dependencies
The header includes `<inttypes.h>`, although this particular declaration does not expose fixed-width integer arguments. The implementation depends on the chart schema and many counter providers.

## Risks
Because only init is public, failure handling at startup is important: if callers ignore a nonzero return, chart files may not be loaded or stored even though the daemon continues serving data. Direct refresh/store functions exist in the implementation but are intentionally not public.

## Test Signals
Compile-time inclusion from startup code and runtime startup logs or chart file creation are the primary signals. A test harness should call `chartsdata_init` in a configured main-loop environment and verify registered timed callbacks execute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/chartsdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/chartsdefs.h -->
# sources/distributed-fs/moosefs/mfschunkserver/chartsdefs.h

## Purpose
`chartsdefs.h` defines the chunkserver chart schema: the persisted filename, numeric chart indexes, stat ids, aggregation modes, scaling rules, calculated metrics, and exported multi-series chart definitions. It is shared by the daemon and stats dump tool.

## Important Definitions
`CHARTS_FILENAME` is `csstats.mfs`. `CHARTS_*` constants assign indexes `0..47` for CPU, master traffic, replication traffic, client traffic, HDD read/write bytes and operations, high-level operations, read/write time, replication count, chunk operation counts, load, memory, movement, space, chunk counts, chunk layout categories, disk state counts, and usage difference. `CHARTS` is `48`.

`STRID(a,b,c,d)` packs four characters into a 32-bit stat id. `STATDEFS` maps each raw chart name to stat id, aggregation mode (`CHARTS_MODE_ADD` or `CHARTS_MODE_MAX`), percent flag, scale, multiplier, and divisor. `CALCDEFS` defines calculated series for virtual-minus-RSS memory and free space (`TSPACE - USPACE`) clamped at zero. `ESTATDEFS` defines exported aggregate charts such as `cpu`, `bwin`, `bwout`, `hddread`, `hddwrite`, `hddopsr`, `hddopsw`, `mem`, `move`, `space`, `chunks`, and `hddcnt`.

## Control Flow and Integration
This header has no executable flow, but its macros instantiate `statdef`, `estatdef`, and calculation arrays in `chartsdata.c`; `Makefile.am` also includes it in the stats dump utility. The index constants are used by `chartsdata_refresh` to fill the data array.

## State and Persistence
The schema defines the meaning of persisted `csstats.mfs` samples. Any reordering or id/name change affects compatibility with existing chart history and tools. Adding a metric requires increasing `CHARTS`, assigning a new index, extending `STATDEFS`, and updating producers.

## Dependencies
The macro bodies use chart subsystem constants and macros such as `CHARTS_MODE_ADD`, `CHARTS_SCALE_MICRO`, `CHARTS_CALCDEF`, `CHARTS_MAX`, `CHARTS_SUB`, `CHARTS_DIRECT`, and `CHARTS_DEFS_END`, so includers must include or otherwise know the common chart definitions.

## Risks
The largest risk is positional drift. `CHARTS_*` indexes, `CHARTS` count, `STATDEFS`, and `chartsdata_refresh` must evolve together. Scale multipliers/divisors encode units and rates; a wrong divisor can silently produce misleading operational dashboards. The `STRID` macro casts characters to `uint8_t`, so it relies on fixed-width types being visible in includers.

## Test Signals
Signals include successful compilation of `chartsdata.c` and `mfscsstatsdump`, chart dump output with all expected names, persisted chart files readable after upgrades, and tests that compare the number of raw definitions against `CHARTS`. Adding metrics should include a compatibility check for old `csstats.mfs` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/chartsdefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/csserv.c -->
# sources/distributed-fs/moosefs/mfschunkserver/csserv.c

## Purpose
`csserv.c` implements the chunkserver client/administrative TCP service. It accepts client connections on `CSSERV_LISTEN_HOST`/`CSSERV_LISTEN_PORT`, parses MooseFS packet headers and bodies, dispatches read/write work to background jobs, answers administrative and monitoring requests, and exposes byte counters for charting.

## Important Types and APIs
`csserventry` is the per-connection state: connection state (`IDLE`, `READ`, `WRITE`, `CLOSE`), parse mode (`HEADER`, `DATA`), socket, poll descriptor position, last read/write timestamps, header buffer, current input packet, output packet queue, active read/write job id, and a list of idle metadata jobs. `packetstruct` represents queued output buffers. `idlejob` tracks asynchronous chunk-info requests with a flexible `buff[1]` payload.

Public APIs are `csserv_stats`, `csserv_getlistenip`, `csserv_getlistenport`, and `csserv_init`. Internal handlers include version/config replies, read/write initialization, chunk blocks/checksum/checksum-tab/info, HDD listing, chart PNG/data, monotonic data, module info, error clearing, connection close cleanup, packet dispatch, reload, read/write I/O, poll descriptor registration, and serving.

## Control Flow
`csserv_init` reads listen config, creates a nonblocking TCP socket, enables nodelay/reuseaddr, resolves and listens, optionally sets an accept filter, then registers exit, reload, destruct, and poll callbacks with the main loop. `csserv_desc` adds the listening socket and idle client sockets to the poll set. `csserv_serve` accepts new sockets, handles poll errors, reads packets, sends keepalive `ANTOAN_NOP` packets after idle write intervals, writes queued output, closes timed-out idle connections after `CSSERV_TIMEOUT`, and frees closed entries.

`csserv_read` is a two-phase parser: read 8-byte header, validate body length against `CSTOCS_MAXPACKETSIZE`, allocate body, read body, then dispatch through `csserv_gotpacket`. Dispatch only accepts most commands while the connection is `IDLE`; data operations set state to `READ` or `WRITE` and call `job_serv_read`/`job_serv_write`. If those jobs cannot queue, the service sends immediate `MFS_ERROR_NOTDONE` status when packet size validates. Completion callback `csserv_iothread_finished` returns the connection to `IDLE` or closes it, clears `jobid`, and frees the input packet.

Idle metadata operations allocate `idlejob` records, call `job_get_chunk_*`, and build protocol replies in `csserv_idlejob_finished`. Connection close disables outstanding jobs and removes callbacks to avoid callbacks touching freed connection state.

## State and Persistence
Service state is in-memory: connection list, output queues, active jobs, listen socket, listen address, and byte counters. No durable client-service state is stored here. It reads configuration through `cfg`, and reload can replace the listening socket and force master reconnect so the master learns the new address.

## Dependencies and Integration
The module depends on `MFSCommunication.h` packet types/statuses, `datapack` for endian-safe packing, common `sockets`, `main`, `cfg`, `clocks`, `charts`, and `mfslog`, `bgjobs` for offloaded work, `mainserv` for actual client read/write processing, `hddspacemgr` for disk info and error clearing, and `masterconn` for module identity and reconnects.

## Risks
Connection lifetime is coupled to background callbacks; `csserv_close` must disable jobs and null callbacks before freeing entries. `idlejob` cleanup intentionally leaves detached jobs to complete with `eptr == NULL`, so future changes must preserve that safety. Packet size checks protect allocations, but many handlers allocate based on request flags and assume `malloc` succeeds. `csserv_reload` logs the old address in some failure/success messages even while handling new address values, which can confuse diagnostics. The timeout is short (5 seconds), so slow clients or blocked write buffers may be dropped quickly.

## Test Signals
Strong tests include packet parser behavior for partial headers/bodies, maximum packet rejection, malformed-size closure for each command, queue-full read/write immediate status, callback completion returning state to idle, closing a connection with outstanding jobs, idle chunk-info replies for success and error statuses, chart/HDD/admin command responses, listen reload with `masterconn_forcereconnect`, and byte counters resetting through `csserv_stats`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/csserv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/csserv.h -->
# sources/distributed-fs/moosefs/mfschunkserver/csserv.h

## Purpose
`csserv.h` declares the public surface of the chunkserver client service module. It lets other modules initialize the service, query its listen address, and collect/reset byte counters.

## Important APIs
`void csserv_stats(uint64_t *bin, uint64_t *bout)` returns bytes read and written by the service since the last call and resets those counters. `uint32_t csserv_getlistenip(void)` returns the numeric listen IP selected during initialization or reload. `uint16_t csserv_getlistenport(void)` returns the numeric listen port. `int csserv_init(void)` starts listening and registers the module with the common main-loop framework.

## Control Flow and Integration
Startup code calls `csserv_init`; after that, service activity is driven by poll callbacks registered inside the implementation. `chartsdata.c` calls `csserv_stats` during periodic refresh. `masterconn` can use the listen IP/port accessors when reporting this chunkserver to the master.

## State and Persistence
The header exposes no state. The implementation maintains the listen socket, connection list, and counters in process memory. Listen host and port are configuration-derived and may change on reload.

## Dependencies
Only `<inttypes.h>` is required by the header. The implementation has broader dependencies on sockets, packet definitions, background jobs, disk management, charts, and master connection code.

## Risks
`csserv_stats` is destructive by design because it resets counters. Callers that sample too frequently or from multiple places will alter chart semantics. Listen address accessors depend on successful init/reload; callers should not assume meaningful values before `csserv_init` succeeds.

## Test Signals
Compile-time signals come from inclusion by startup, chart, and master modules. Runtime signals include successful service initialization, nonzero byte counters after traffic, counter reset after `csserv_stats`, and listen IP/port reflecting configuration and reload changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfschunkserver/csserv.h -->
