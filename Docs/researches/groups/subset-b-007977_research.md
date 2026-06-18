# subset-b-007977 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGPFile.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGPFile.hh

Purpose: declares the get/put-file plugin interface used by XRootD to hand whole-file copy requests to an optional external implementation. The header defines the request argument/callback carrier and the abstract `XrdXrootdGPFile` service with `getFile()` and `putFile()` entry points.

Important APIs/types/functions: `XrdXrootdGPFileInfo` carries checksum type/value, source and destination strings, CGI fragments, ping interval, and stream count. Its `Completed()` callback reports terminal success or an errno/message pair, while `Update()` reports transferred bytes and status (`isPending`, `isCopying`, `isProving`). `XrdXrootdGPFile` is the plugin base class, and `XrdOfsgetPrepare_t` plus `XrdOfsgetPrepareArguments` define the shared-library factory ABI.

Control flow: the xrootd command path constructs an info object bound to an `XrdXrootdGPFAgent`, loads a plugin factory, calls either `getFile()` or `putFile()`, and expects the plugin to signal all acceptance, progress, and final outcomes through the `XrdXrootdGPFileInfo` callbacks. The call may be accepted asynchronously; completion must delete or retire the info object after `Completed()`.

State and persistence behavior: this header owns no persistent storage. State is request-scoped in `XrdXrootdGPFileInfo` and plugin-owned after dispatch. Persistent effects are external file transfers and optional checksum verification performed by the plugin.

Dependencies: forward-declares `XrdOucEnv`, `XrdOucErrInfo`, `XrdSecEntity`, `XrdSfs`, and `XrdXrootdGPFAgent`; the factory ABI also uses `XrdSysError`. It integrates with the server filesystem plugin and security identity passed to copy plugins.

Integration points: loaded by xrootd configuration/plugin machinery. Implementers are expected to export a C factory and `XrdVERSIONINFO` so server/plugin ABI mismatches can be detected.

Risks: the listed source contains apparent declaration inconsistencies: `srcCgi` is declared twice where the second field is documented as destination CGI, the constructor initializes `dstCgi`, and `pingsec`/`pingSec` spelling differs. As written, that is a compile/API risk unless a local patch or preprocessor context fixes it. Callback lifetime is also delicate because the object must survive asynchronous transfer but be deleted after completion.

Test signals: compile a minimal plugin against the header; load success/failure paths for the factory; rejected transfer calls `Completed(errno)`; progress pings at `pingsec`; checksum requested and omitted cases; disconnected client causing callback false returns; ABI version mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGPFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGSReal.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGSReal.cc

Purpose: implements the concrete generic monitoring stream, or G-Stream, used by plugins to emit monitoring records in binary, CGI, or JSON form to either a private UDP destination or the normal xrootd monitor routing layer.

Important APIs/types/functions: constructor `XrdXrootdGSReal(GSParms,bool&)`, `Flush()`, `GetDictID()`, `HasHdr()`, `Ident()`, `Insert()` overloads, `Reserve()`, `SetAutoFlush()`, `GetAutoFlush()`, and `Space()`. Private helpers `AutoFlush()`, `Expel()`, `hdrBIN()`, `hdrCGI()`, and `hdrJSN()` manage scheduled flushing and header formatting.

Control flow: construction clamps and aligns the UDP buffer size, formats an optional monitor header, creates an `XrdNetMsg` for per-stream destinations, configures autoflush, and registers a synthetic monitor user. `Insert(data,dlen)` validates a null-terminated payload, flushes if the next record will not fit, copies the record with newline termination, timestamps the packet window, and advances the buffer. `Reserve()` locks the stream and returns writable space; `Insert(dlen)` validates the reserved data, normalizes the recursive lock, timestamps, and releases. `DoIt()` is scheduler-driven and flushes aged non-empty packets before rescheduling.

State and persistence behavior: state is in memory: aligned UDP buffer pointers, packet sequence counters for data/identity/dictionary packets, timestamp window, reserved-byte flag, auto-flush state, header substitution pointers, optional `XrdNetMsg`, and registered monitor user. Persistence is only emitted UDP monitor traffic.

Dependencies: `XrdScheduler`, `XrdNetMsg`, `XrdSysRecMutex`, monitor globals in `XrdXrootdMonInfo`, `XrdXrootdMonitor`, and `XrdXrootdMonData` structures. It uses `posix_memalign`, `iovec`, network byte-order helpers, and legacy `index()`.

Integration points: backs the public `XrdXrootdGStream` facade and the `XrdXrootdMonitor::Hello` identity hail list. Plugins such as cache, TCP, TPC, throttle, OSS, and HTTP monitoring can reserve/insert payloads through the facade.

Risks: `GetDictID()` sends text dictionary records through `udpDest` without a null check after checking only `dictHdr`; header-enabled streams without a private destination need scrutiny. Reservation holds the recursive mutex across plugin code until `Insert()`, so missing completion can block all stream producers. Text headers rely on fixed placeholder locations and buffer size assumptions. `SetAutoFlush()` here accepts any positive value, while the facade clamps values below 60 seconds.

Test signals: binary/CGI/JSON header generation; hdrNone behavior; dictionary map path/info emission; identity suppression via `optNoID`; reserve/insert cancellation (`dlen == 0`); packet flush on size boundary; auto-flush scheduler firing; stream with and without private destination; invalid lengths and non-null-terminated payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGSReal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGSReal.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGSReal.hh

Purpose: declares the real G-Stream implementation that combines `XrdJob` scheduling, public `XrdXrootdGStream` insertion APIs, and `XrdXrootdMonitor::Hello` identity reporting.

Important APIs/types/functions: public stream methods mirror the facade: `Flush`, `GetDictID`, `HasHdr`, `Ident`, `Insert`, `Reserve`, `SetAutoFlush`, `GetAutoFlush`, and `Space`. `GSParms` defines plugin name, destination, monitor mode, max packet length, flush interval, stream type, options, format, and header detail. Format constants include `fmtNone`, `fmtBin`, `fmtCgi`, `fmtJson`; header constants range from `hdrNone` to `hdrFull`.

Control flow: callers instantiate this class with validated monitor options, then pass its base `XrdXrootdGStream` reference to plugins. Scheduler calls `DoIt()` for auto-flush. The `Hello` base calls `Ident()` during monitor hails.

State and persistence behavior: owns process-resident packet buffers, header strings, sequence counters, timestamp fields, reservation state, destination socket object, and monitor user identity. No durable data is kept; all persistence is monitor packets sent externally.

Dependencies: `XrdJob`, `XrdSysPthread`, `XrdXrootdGStream`, `XrdXrootdMonData`, `XrdXrootdMonitor`, and forward-declared `XrdNetMsg`/`XrdSysError`.

Integration points: created by monitor configuration for generic stream modes and consumed by internal/external plugins that need structured monitoring output.

Risks: destructor intentionally does not free several allocated buffers because these objects are normally process-lifetime; tests that create many instances may leak unless isolated. The private state is tightly coupled to implementation assumptions about packet layout and header placeholders. Recursive locking plus external plugin writes must be handled carefully.

Test signals: construction with every format/header pair, max-length clamping, `optNoID`, `HasHdr()` results, `Space()` after inserts and flushes, auto-flush scheduling state, and identity hail behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGSReal.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGStream.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGStream.cc

Purpose: implements the public G-Stream facade by forwarding all calls to the referenced `XrdXrootdGSReal` implementation.

Important APIs/types/functions: `Flush()`, `GetDictID()`, `HasHdr()`, `Insert()` overloads, `Reserve()`, `SetAutoFlush()`, `GetAutoFlush()`, and `Space()`.

Control flow: each method delegates directly to `gStream`. The only local behavior is `SetAutoFlush()`, which converts negative values to disabled (`0`) and clamps positive values below 60 seconds up to 60 before calling the real implementation.

State and persistence behavior: no owned state beyond the reference stored in the header. Runtime side effects are whatever the real stream performs: buffer mutation, locks, scheduled flush, and monitor sends.

Dependencies: `XrdXrootdGStream.hh` and `XrdXrootdGSReal.hh`.

Integration points: this file keeps plugin-facing ABI small and hides implementation details. Plugins can receive an `XrdXrootdGStream` rather than the concrete monitor object.

Risks: all safety depends on the referenced real object outliving the facade. The auto-flush clamp only applies through the facade; internal calls to `XrdXrootdGSReal::SetAutoFlush()` bypass it.

Test signals: facade methods produce identical effects to direct implementation calls, especially auto-flush clamping, `Reserve()`/`Insert()` lock release, and invalid payload rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGStream.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGStream.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGStream.hh

Purpose: defines the plugin-facing interface for writing generic monitoring records into the XRootD G-Stream.

Important APIs/types/functions: `Flush`, `GetDictID`, `HasHdr`, `Insert(const char*,int)`, `Reserve`, `Insert(int)`, `SetAutoFlush`, `GetAutoFlush`, `Space`, and `MaxDataLen` (`65280`). The constructor binds the facade to an `XrdXrootdGSReal` reference.

Control flow: callers either insert a complete null-terminated record or reserve a buffer, fill it, then call `Insert(dlen)` to commit or `Insert(0)` to cancel. Dictionary mapping can be requested for paths or generic info and is automatically emitted when headers are enabled.

State and persistence behavior: the facade has no mutable storage except the implementation reference. State and monitor persistence are delegated to `XrdXrootdGSReal`.

Dependencies: C integer types and the forward declaration of `XrdXrootdGSReal`.

Integration points: this is the stable ABI passed to monitoring-capable plugins, insulating them from UDP buffer/header details.

Risks: reserve semantics lock the underlying stream until commit/cancel, so plugin misuse can starve other producers. The API requires the length to include a terminal null byte and be at least 8 bytes, which is easy to violate in small JSON/CGI snippets. `MaxDataLen` must remain compatible with the real buffer and UDP packet limits.

Test signals: null termination validation, max/min length checks, reserve cancellation, multiple plugin producers, dictionary IDs with and without headers, and manual flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGStream.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdJob.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdJob.cc

Purpose: implements a keyed external-program job scheduler for xrootd administrative or helper operations. It coalesces duplicate jobs, limits concurrent executions, supports synchronous wait and asynchronous wait-response clients, and cancels/prunes abandoned jobs.

Important APIs/types/functions: local class `XrdXrootdJob2Do` represents one queued/running job. Its `DoIt()`, `addClient()`, `delClient()`, `lstClient()`, `verClient()`, `Redrive()`, and `sendResult()` manage execution and client fan-out. Public `XrdXrootdJob` methods are `Schedule()`, `Cancel()`, `List()`, `DoIt()`, `CleanUp()`, and `sendResult()` for completed cached results.

Control flow: `Schedule()` validates the job key, finds an existing job unless `JOB_Unique` is set, attaches the caller as a sync or async client, or allocates a new table slot and schedules it immediately if below `maxJobs`. Async clients receive `kXR_waitresp`; sync/fallback callers receive `kXR_wait`. `XrdXrootdJob2Do::DoIt()` runs `XrdOucProg`, captures a line of output, translates success/failure/cancellation, sends async results, redrives one waiting job if capacity opens, and removes itself when no polling clients remain. The scheduler job periodically marks jobs and removes clients whose links disappeared.

State and persistence behavior: all state is in memory: `JobTable`, per-job argv copies, client link/instance/stream IDs, job status atomics, result line pointer, max/current job counters, and cleanup marks. Persistent effects are the external program’s side effects and protocol responses sent to clients.

Dependencies: `XrdScheduler`, `XrdOucProg`, `XrdOucStream`, `XrdOucTable`, `XrdOucTList`, `XrdLink`, `XrdXrootdResponse`, xrootd protocol types, tracing, and `XProtocol::mapError`.

Integration points: used by xrootd command paths that need long-running helper programs while preserving client protocol semantics. `List()` produces XML-like fragments for administrative inspection.

Risks: lock scope is complex because job threads execute external programs and then re-enter shared tables. `theResult` points to stream-owned data whose lifetime must outlive polling responses. `sendResult()` sends to links captured earlier; link instance validation is only pruned periodically or when client arrays are full. The fixed client limit of 8 forces sync fallback. Redrive logic depends on `numJobs`, `maxJobs`, and `doRedrive` staying consistent under cancellation.

Test signals: duplicate non-unique jobs share one execution; unique jobs do not coalesce; async client result delivery; sync fallback when max clients/table slots exhausted; cancellation before run, during run, and after completion; disconnected client pruning; redrive ordering when `maxJobs` is exceeded; `List()` status XML for active/waiting/done/cancelled jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdJob.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdJob.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdJob.hh

Purpose: declares the keyed job scheduler used to execute external programs behind xrootd requests with concurrency limits and client wait semantics.

Important APIs/types/functions: option flags `JOB_Sync` and `JOB_Unique`; public methods `Schedule`, `Cancel`, `List`, and `DoIt`; constructor `XrdXrootdJob(XrdScheduler*,XrdOucProg*,const char*,int)`; private `CleanUp` and `sendResult`; `reScan` interval of 15 minutes.

Control flow: callers schedule by job key and argv vector, optionally requiring uniqueness or synchronous waiting. The object itself is also an `XrdJob` scheduled periodically to scan job/client state.

State and persistence behavior: maintains an `XrdOucTable<XrdXrootdJob2Do>`, a mutex, scheduler/program pointers, duplicated job name, maximum running jobs, and current job count. State is volatile and process-local.

Dependencies: `XrdJob`, `XrdOucProg`, `XrdOucTList`, `XrdOucTable`, `XrdSysPthread`, `XrdLink`, `XrdScheduler`, and `XrdXrootdResponse`.

Integration points: consumed by request handlers that need queued helper execution and by administrative list/cancel commands.

Risks: destructor notes there is no reliable deletion because unsynchronized worker threads may still reference the object. Consumers should treat instances as process-lifetime services. Job keys must be stable and non-empty or scheduling fails.

Test signals: constructor schedules rescans, max-job enforcement, table allocation failure, list output under lock, cancel-by-key and cancel-all, and shutdown/destructor behavior in controlled tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdLoadLib.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdLoadLib.cc

Purpose: loads core xrootd runtime plugins from shared libraries: the filesystem implementation and the redirect plugin.

Important APIs/types/functions: `XrdXrootdloadFileSystem()` and `XrdXrootdloadRedirLib()`. The filesystem loader resolves `?XrdSfsGetFileSystem2` first and falls back to `XrdSfsGetFileSystem`; the redirect loader resolves `XrdXrootGetdRedirPI`.

Control flow: each function creates an `XrdOucPinLoader` with version information, resolves the expected factory symbol, invokes it with previous plugin instance and configuration/environment parameters, logs an error if no object is returned, and returns the plugin pointer. The filesystem loader exports `XRDOFSLIB` only when loading the first filesystem layer.

State and persistence behavior: no durable state beyond environment export and pinned shared-library handles held by `XrdOucPinLoader` machinery. Plugin instances may wrap or replace previous instances.

Dependencies: `XrdVersion`, `XrdOucEnv`, `XrdOucPinLoader`, `XrdSfsInterface`, `XrdSysError`, and `XrdXrootdRedirPI`.

Integration points: called during server configuration/startup to construct the active SFS/OFS stack and optional redirect policy plugin.

Risks: factory symbol spelling is ABI-critical; redirect symbol name `XrdXrootGetdRedirPI` must match plugins. Failure logs but returns null, so callers must abort or handle disabled functionality. Preferential v2 filesystem loading changes constructor signature and environment visibility.

Test signals: missing library, missing factory symbol, v2 and v1 filesystem factories, previous-filesystem chaining, redirect plugin load, version mismatch, and `XRDOFSLIB` export only for the first layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdLoadLib.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonData.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonData.hh

Purpose: defines the wire-format data structures, stream codes, operation codes, masks, and file-stat record layouts used by XRootD monitoring packets.

Important APIs/types/functions: packet structs include `XrdXrootdMonHeader`, `XrdXrootdMonTrace`, `XrdXrootdMonBuff`, `XrdXrootdMonRedir`, `XrdXrootdMonBurr`, `XrdXrootdMonGS`, and `XrdXrootdMonMap`. File-stat structs include `XrdXrootdMonFileHdr`, `XrdXrootdMonFileTOD`, `XrdXrootdMonFileLFN`, `XrdXrootdMonFileOPN`, `XrdXrootdMonStatPRW`, `XrdXrootdMonStatOPS`, `XrdXrootdMonStatSSQ`, `XrdXrootdMonStatXFR`, `XrdXrootdMonFileCLS`, `XrdXrootdMonFileDSC`, and `XrdXrootdMonFileXFR`.

Control flow: this header has no executable flow; producers fill these structures in network byte order and consumers decode based on stream `code`, record `recType`, flags, and variable `recSize`.

State and persistence behavior: no local state. The structures define persisted UDP payloads as observed by collectors and downstream monitoring systems.

Dependencies: `XProtocol/XPtypes.hh` for fixed protocol integer aliases. Producers rely on byte-order helpers from platform headers.

Integration points: used by `XrdXrootdMonitor`, `XrdXrootdMonFile`, `XrdXrootdGSReal`, redirect monitoring, dictionary mapping, and external collectors.

Risks: ABI/wire compatibility is fragile: field sizes, signedness, and endianness must stay stable. Several structures are variable-length despite C declarations with placeholder arrays, so producers must use `recSize` and computed lengths rather than `sizeof` blindly. Comments mention spelling/semantic quirks such as `hasSSQ`/`hasCSE` sharing a value.

Test signals: binary packet decoding against known fixtures; endianness on big- and little-endian hosts; variable close/open records with and without LFN/OPS/SSQ; redirect records with host/path truncation; G-Stream SID encoding; collector compatibility across versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonData.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFMap.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFMap.cc

Purpose: implements a small fixed-size slot map that stores active `XrdXrootdFileStats` pointers for periodic file-transfer monitoring.

Important APIs/types/functions: `Init()` allocates and chains slots, `Insert()` takes a free slot and stores a stats pointer, `Free()` returns a slot to the free list, and `Next()` iterates valid slots.

Control flow: the first `Insert()` lazily calls `Init()` if there is no free list. Free slots are marked by setting low-bit `invVal` in the union storage and linked through `cPtr`. `Insert()` pops the head, clears the invalid bit, stores `vPtr`, and returns the slot index. `Free()` validates bounds and current validity, then pushes the slot back to `free`. `Next()` scans forward until it finds a valid slot and advances the caller's cursor.

State and persistence behavior: owns one aligned `fMap` array per map object and a free-list head. No durable state; pointers refer to live file-stat objects owned elsewhere.

Dependencies: `posix_memalign`, `getpagesize`, `XrdSysPlatform`, `XrdXrootdFileStats`, and the declaration in `XrdXrootdMonFMap.hh`.

Integration points: `XrdXrootdMonFile` keeps an array of these maps to register files that need interval transfer records.

Risks: validity marking uses pointer/long punning and assumes pointer alignment leaves the low bit free. `Next()` loops while `slotNum < fmSize-1`, which can skip the final slot. The map itself is not internally synchronized; callers must hold `fmMutex`. Memory is never freed by the destructor.

Test signals: first insert initializes all slots; insert/free/reinsert returns reusable indices; invalid free rejection; iteration sees all active slots including boundary indices; concurrent access only under external lock; full-map insert returns `-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFMap.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFMap.hh

Purpose: declares the active-file slot map used by file-stat monitoring to track `XrdXrootdFileStats` objects efficiently.

Important APIs/types/functions: `cvPtr` union stores either a raw long, next-free pointer, or stats pointer. Constants define `mapNum` (`128` maps), per-map `fmSize` (`512` slots), lock-yield hold count, masks, and shift values. Public methods are `Insert`, `Free`, and `Next`.

Control flow: callers use the returned slot number with `fmShft`/`fmMask` to encode a map/slot cookie in file stats. Iteration is cursor-driven by an integer reference.

State and persistence behavior: each instance owns an optional allocated slot array plus a free-list head. State is process-memory only and mirrors currently open monitored files.

Dependencies: forward declaration of `XrdXrootdFileStats`.

Integration points: embedded as the static `fmMap` array in `XrdXrootdMonFile`; encoded entries are stored in `XrdXrootdFileStats::MonEnt`.

Risks: callers must use the constants consistently when packing/unpacking `MonEnt`. No copy prevention is declared, so accidental copying would duplicate pointer/free-list state. The class relies on external synchronization.

Test signals: cookie packing/unpacking across map boundaries, map capacity at 512 slots, high-water behavior in `XrdXrootdMonFile`, and accidental duplicate/free handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFMap.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFile.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFile.cc

Purpose: implements the `"f"` monitor stream for per-file open, close, disconnect, and periodic transfer-stat records.

Important APIs/types/functions: static API `Defaults()`, `Init()`, `Open()`, `Close()`, and `Disc()`; scheduled `DoIt()`; private `DoXFR()` overloads, `Flush()`, and `GetSlot()`. Static state includes the report buffer, header/TOD pointers, file-stat maps, record counters, option flags, and preformatted record sizes.

Control flow: `Defaults()` derives monitoring level and record-detail flags from configuration. `Init()` allocates the UDP report buffer, formats the stream header and initial time record, computes close/XFR record layouts, and schedules a singleton job. `Open()` assigns a dictionary ID, optionally registers the file in the active transfer map, builds an open record with optional user/path LFN, and appends it to the buffer. `Close()` deregisters active transfer monitoring, emits final byte/operation/sum-of-squares stats, and marks forced closes for disconnects. `DoIt()` periodically emits XFR records for active files when the configured counter expires, flushes any buffered records, and reschedules itself.

State and persistence behavior: all state is static and process-global. The report buffer is double-used for all producer threads under `bfMutex`; active files are tracked under `fmMutex`. Persistence is UDP monitor output via `XrdXrootdMonitor::Send(XROOTD_MON_FSTA, ...)`.

Dependencies: `XrdScheduler`, `XrdSysError`, `XrdSysPlatform`, `XrdXrootdMonData`, `XrdXrootdMonitor`, and `XrdXrootdFileStats`.

Integration points: invoked from file open/close/disconnect paths and from `XrdXrootdMonitor::Init()` when fstat monitoring is enabled. It reads counters maintained by file I/O paths.

Risks: the single shared buffer serializes all file-monitor producers and comments note double buffering would be better. `Open()` sets `MonEnt` even if XFR monitoring is disabled or insertion fails, yielding encoded negative/invalid values that must be understood by close logic. LFN records use `strncpy` with padded computed length; path length has been sized but exact termination behavior depends on padding. XFR scanning drops and reacquires `fmMutex`, so file close/free can race unless map cursors and stats lifetime are safe.

Test signals: open records with and without LFN/user/read-write flag; close records with XFR only, OPS, and SSQ; forced close on disconnect; periodic XFR only for active `xfrXeq` files; buffer flush on size boundary and time interval; high-water map shrink on close; fstat disabled path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFile.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFile.hh

Purpose: declares the static file-stat monitoring producer for the XRootD monitor `"f"` stream.

Important APIs/types/functions: public static `Close`, `Defaults`, `Disc`, `Init`, and `Open`; scheduled `DoIt`; private static `DoXFR`, `Flush`, and `GetSlot`. Static data covers buffer locks, file-map locks, active-file maps, report buffer pointers, record counters, report interval, transfer interval, buffer size, preformatted transfer/close records, and option flags.

Control flow: external file events call `Open`, `Close`, and `Disc`; the scheduler calls `DoIt` for periodic transfer snapshots and flushing.

State and persistence behavior: process-global static state only. It mirrors currently open monitored files and accumulated packet contents until flushed to collectors.

Dependencies: `XrdJob`, `XrdSysPthread`, `XrdXrootdMonFMap`, `XrdXrootdMonitor`, and forward declarations for file stats and monitor packet structures.

Integration points: friend-accessed from `XrdXrootdMonitor`; called by xrootd file handling code that updates `XrdXrootdFileStats`.

Risks: static global state makes test isolation and reconfiguration difficult. Consumers must call `Defaults()` before `Init()` so sizes/options are coherent. Lock ordering between file-map and buffer locks must remain consistent to avoid stalls.

Test signals: static initialization order, reinitialization attempts, scheduler lifecycle, fstat option combinations, and multi-threaded open/close/XFR stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonitor.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonitor.cc

Purpose: implements the central XRootD monitoring subsystem for user/info/path dictionaries, I/O trace packets, file-event duplication, redirect monitoring, identity announcements, clock windows, and destination routing.

Important APIs/types/functions: `Defaults()` overloads configure modes, sizes, intervals, and destinations; `Init()` overloads construct server identity and initialize destinations; `Alloc()`/`unAlloc()` manage per-user monitors; `User::Register`, `Enable`, `Disable`, and `Report` handle monitor users; event methods `Open`, `Close`, `Disc`, `appID`, `Map`, `Redirect`, `Tick`, `Send`, `Flush`, and `Mark` emit packets. Nested `Hello` registers generic-stream identity callbacks.

Control flow: startup calls `Defaults()` then `Init(sp,errp,host,prog,name,port)` to build SID/identity strings, and later `Init()` to open destinations, schedule identity jobs, allocate alternate file-only monitor, start the clock, initialize fstat, and allocate redirect buffers. Runtime users call `Register()` to obtain monitor identity and optionally an `Agent`. I/O events append trace entries to per-agent buffers, inserting window marks or flushing when windows/buffers roll. `Tick()` advances the global window, flushes alt/redirect buffers as needed, and stops in selective mode when no monitors remain. `Send()` routes packets to up to two destinations based on mode masks with independent packet sequences.

State and persistence behavior: extensive static process state: destinations and sockets, monitor mode flags, identity record/string variants, SID, current window, buffer sizes, redirect buffer ring, alt monitor, counters, and scheduler pointers. Per-agent state includes a monitor buffer, next-entry cursor, and last-window marker. Persistence is monitor UDP traffic and environment export `XRDMONRDR` when redirect monitoring is active.

Dependencies: `XrdNetMsg`, `XrdOucEnv`, `XrdOucUtils`, `XrdScheduler`, `XrdSysError`, `XrdXrootdMonData`, `XrdXrootdMonFile`, `XrdXrootdTrace`, `XrdSecMonitor`, platform byte-order helpers, and `XrdVersion`.

Integration points: used throughout xrootd request/file/session handling, by security monitor reporting through `XrdSecMonitor`, by redirect paths, by generic G-Stream identity hails, and by fstat monitoring.

Risks: this is global, mutable, and timing-sensitive. Selective-mode clock start/stop depends on `numMonitor`; sequence numbers are per destination under a send mutex; I/O event paths intentionally avoid heavy locking and rely on atomic-enough simple memory reads. `Map()` copies user name plus path into a fixed `info` buffer and must rely on bounded path copy. Redirect buffers use a shared free ring and per-buffer locks. `User::Register()` allocates `Name` without clearing any previous value, so object reuse must call `Clear()` first.

Test signals: one and two destination routing masks; identity record content and periodic schedule; monitor disabled, all, and selective modes; map user/path/info/token packets; I/O open/read/write/readv/close/disc trace ordering; auto-flash/auto-flush windows; redirect record truncation and buffer flushing; fstat init failure; alt monitor duplication for file/user modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonitor.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonitor.hh

Purpose: declares the central monitor API and configuration flags used by xrootd sessions, files, security, redirects, and G-Stream components.

Important APIs/types/functions: mode bits `XROOTD_MON_*`; fstat options `XROOTD_MON_FSLFN`, `FSOPS`, `FSSSQ`, `FSXFR`; public event methods `Add_rd`, `Add_rv`, `Add_wr`, `Open`, `Close`, `Disc`, `appID`; static configuration/utility methods `Defaults`, `Init`, `Send`, `GetDictID`, `Ident`, `ModeEnabled`, `Redirect`, `Tick`, and `Flushing`. Nested `Hello` models identity callbacks; nested `User` extends `XrdSecMonitor`.

Control flow: users register a monitor identity, use inline event helpers for hot I/O paths, and rely on private `Mark()`/`Flush()` when windows or buffers fill. Static methods configure global monitor modes before runtime use.

State and persistence behavior: declares static global state for destinations, sockets, window timing, buffer sizes, flags, identity record, redirect buffers, and alternate monitor. Per-instance state is a monitor buffer and cursors.

Dependencies: `XrdSecMonitor`, `XrdSysPthread`, `XrdXrootdMonData`, `XProtocol/XPtypes`, POSIX time/types, and `XrdNetMsg`/`XrdScheduler` forward declarations.

Integration points: the API is called by request handlers and file/session objects without needing to know destination routing. Security code can call `User::Report(WhatInfo, ...)`.

Risks: many methods assume arguments are already in network byte order. Inline hot-path methods mutate buffers directly and must match implementation invariants (`lastWindow`, `nextEnt`, `lastEnt`). The private destructor prevents ordinary stack allocation cleanup assumptions. Global configuration flags are chars/ints rather than type-safe enums.

Test signals: compile-time use of inline helpers, byte-order contract tests, monitor mode mask combinations, `User` lifecycle (`Register`, `Clear`, `Enable`, `Disable`), and redirect/fstat flag enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonitor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdNormAio.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdNormAio.cc

Purpose: implements asynchronous normal read/write tasks that copy data between an `XrdSfs` file and a client link while preserving protocol response ordering and request accounting.

Important APIs/types/functions: static `Alloc()`, `Read()`, `Write()`, `DoIt()`, `Recycle()`, private read path `CopyF2L_Add2Q()`/`CopyF2L()`, write path `CopyL2F()` overloads, and `Send()`. A local free list caches up to 64 task objects.

Control flow: `Read()` initializes offsets/length/state, refs the link and file, increments protocol AIO request count, and schedules through the file AIO fob. `CopyF2L_Add2Q()` issues file `read(XrdSfsAio*)` requests until data or buffer limits are reached. `CopyF2L()` consumes completed buffers, validates results, queues out-of-order completions by offset, sends in-order chunks as `kXR_oksofar`, saves a final buffer to avoid an extra response, then sends final `kXR_ok`. `Write()` starts a socket-bound transfer; `CopyL2F()` reads data from the client into AIO buffers, issues file writes, processes completions, and sends the final response.

State and persistence behavior: per-task state inherited from `XrdXrootdAioTask` includes file/link/protocol, offsets, remaining length, in-flight count, final read, pending write, state flags, and response object. `XrdXrootdNormAio` adds send queue, next expected send offset, reorder count, and scheduling flag. Persistent effects are file reads/writes and client responses.

Dependencies: `XrdXrootdAioBuff`, `XrdXrootdAioFob`, `XrdXrootdFile`, `XrdSfsInterface`, `XrdScheduler`, `XrdLink`, `XrdXrootdResponse`, tracing, and protocol `as_maxperreq`.

Integration points: used by xrootd file read/write request handling when normal asynchronous I/O is available. It cooperates with the file AIO fob for scheduling and with the protocol for socket reads and outstanding request accounting.

Risks: read completions can arrive out of order, making the sorted send queue critical; a missing offset triggers an `ENODEV` error. Writes cannot relinquish the socket-handling thread in the same way reads can, so blocking behavior differs. Reference counts must be decremented exactly once via `aioHeld`. Link-send errors mark `aioDead` and reset pending AIO for the protocol.

Test signals: multi-buffer reads with out-of-order completion, final-response optimization, missing completion/gap error, max in-flight throttling, read link disconnect, write socket short/error returns, file read/write `SFS_OK` and error mapping, recycle free-list cap, and request/refcount accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdNormAio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdNormAio.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdNormAio.hh

Purpose: declares the normal asynchronous I/O task type used for standard xrootd reads and writes.

Important APIs/types/functions: `Alloc`, `DoIt`, `Read`, `Write`, `Recycle`, private `CopyF2L`, `CopyL2F`, `CopyF2L_Add2Q`, `Send`, and state fields `sendQ`, `sendOffset`, `reorders`, and `didSched`.

Control flow: the class overrides the `XrdXrootdAioTask` virtual hooks so the shared AIO task framework can call back for file-to-link and link-to-file movement.

State and persistence behavior: task objects are pooled and reset by `Init()`. No durable state is owned; writes persist through the underlying SFS file object.

Dependencies: `XrdXrootdAioTask`, forward declarations for AIO buffers and xrootd file objects.

Integration points: selected by protocol/file code for non-page-based asynchronous operations.

Risks: private constructor/destructor enforce factory/recycle ownership. Derived state must be fully reset on reuse; `didSched` is declared but the implementation primarily uses inherited `aioState` scheduling flags.

Test signals: factory reuse, virtual dispatch from base callbacks, state reset between read and write reuse, and destructor behavior when free-list overflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdNormAio.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgrwAio.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgrwAio.cc

Purpose: implements asynchronous page-read/page-write tasks, including page checksum calculation/verification and pgread/pgwrite protocol response framing.

Important APIs/types/functions: static `Alloc()`, `Read()`, `Write()`, `DoIt()`, `Recycle()`, read helpers `CopyF2L_Add2Q()`/`CopyF2L()`/`SendData()`, write helpers `CopyL2F()` overloads/`SendDone()`, and checksum verifier `VerCks()`. It pools up to 64 task objects and uses `XrdXrootdAioPgrw` buffers.

Control flow: `Read()` sets page-AIO read state, refs file/link, increments request count, and schedules through the AIO fob. Read dispatch uses `Setup2Send()` and file `pgRead()`. Completed buffers are validated, simulated checksum vectors are calculated when needed, and chunks are sent with pgread partial/final response headers plus offset. `Write()` uses socket `getData()` with an iovec layout generated by `XrdXrootdAioPgrw`, verifies received checksums page by page, records bad pages through `badCSP`, writes good data through file `pgWrite()`, and ends with a pgwrite final response that can include correction information.

State and persistence behavior: per-task state includes inherited AIO offsets/counts and `badCSP`, a pointer to the per-request bad-checksum recorder. Persistent effects are page writes to the SFS layer and correction offsets stored in the file page-write fob for later repair tracking.

Dependencies: `XrdOucPgrwUtils`, `XrdOucCRC`, `XrdSfsInterface`, `XrdXrootdAioFob`, `XrdXrootdAioPgrw`, `XrdXrootdFile`, `XrdXrootdPgwBadCS`, `XrdXrootdResponse`, xrootd protocol structs, and tracing.

Integration points: used by protocol handlers for `kXR_pgread` and `kXR_pgwrite`. It connects protocol framing, checksum utilities, file-level uncorrected checksum tracking, and asynchronous SFS page I/O.

Risks: unlike normal AIO, page-read completions are sent as they are processed; correctness depends on the page AIO layer returning suitable ordering or self-contained offsets. `badCSP` must be valid for every write and is dereferenced in `SendDone()`. Checksum verification mutates checksum values from network to host order before use. Too many per-request or per-file checksum errors aborts with `ETOOMANYREFS`.

Test signals: pgread aligned and unaligned ranges, simulated checksum calculation when backend omits checksums, pgwrite checksum success, single and multiple checksum failures, correction vector response CRC, too-many error limits, link failure reset, request/refcount accounting, and task free-list reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgrwAio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgrwAio.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgrwAio.hh

Purpose: declares the asynchronous page read/write task type for pgread/pgwrite protocol operations.

Important APIs/types/functions: `Alloc`, `DoIt`, `Read`, `Write`, `Recycle`, `aioSZ` (`64 KiB`), private `CopyF2L`, `CopyL2F`, `SendData`, `SendDone`, `VerCks`, and `badCSP`.

Control flow: overrides the common AIO task hooks while specializing buffers, protocol response framing, and checksum handling for page-granular I/O.

State and persistence behavior: task objects are pooled; request state is reset through base `Init()` plus `badCSP`. Durable effects occur through file `pgWrite()` and bad-checksum tracking.

Dependencies: `XrdXrootdAioTask`, forward declarations for `XrdXrootdAioPgrw` and `XrdXrootdPgwBadCS`.

Integration points: selected by protocol code for page-based I/O and used with `XrdXrootdPgwCtl`/`XrdXrootdPgwBadCS` in write paths.

Risks: factory ownership and lifetime of `badCSP` are external. Any mismatch between `aioSZ`, page size, and `XrdXrootdAioPgrw` layout can break framing.

Test signals: factory with and without bad-checksum recorder, state reset across pooled tasks, page-size boundary ranges, virtual callback dispatch, and final response payload generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgrwAio.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwBadCS.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwBadCS.cc

Purpose: implements per-request bad-checksum collection for pgwrite and formats correction information returned to clients.

Important APIs/types/functions: `boAdd()` records one bad data extent and `boInfo()` returns an optional `ServerResponseBody_pgWrCSE` plus bad-offset vector.

Control flow: `boAdd()` traces the checksum error, initializes or updates first/last bad-data lengths, rejects the request if the per-request maximum would be exceeded, stores the bad file offset in network order, and inserts the extent into the file-level `pgwFob` uncorrected-offset set. `boInfo()` returns no payload when no bad offsets were recorded; otherwise it computes the correction-extension CRC and returns a pointer to the packed response body.

State and persistence behavior: per-request `boCount`, `badOffs[]`, and `cse` response struct are in memory. File-level uncorrected checksum state persists for the life of `XrdXrootdPgwFob` and is logged at file close/destruction.

Dependencies: `XrdOucCRC`, `XrdSysPlatform`, `XrdXrootdFile`, `XrdXrootdPgwFob`, protocol page-write response structs, and tracing.

Integration points: called from `XrdXrootdPgrwAio::VerCks()` and from `SendDone()` to include correction data in pgwrite final responses.

Risks: limit check uses `boCount+1 >= kXR_pgMaxEpr`, which permits one fewer stored offset than a strict `< max` interpretation. `boInfo()` returns a pointer to internal mutable storage, so callers must send before reset/destruction. File-level `addOffs()` failure turns into a request error even if the current page write otherwise proceeds.

Test signals: zero-error response, one and many bad offsets, first/last data-length encoding for unaligned pages, correction CRC validation, per-request limit, per-file uncorrected-offset limit, and trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwBadCS.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwBadCS.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwBadCS.hh

Purpose: declares a compact helper for tracking bad checksum offsets during one pgwrite request.

Important APIs/types/functions: `boAdd`, `boInfo`, `boReset`, constructor with path ID, internal `ServerResponseBody_pgWrCSE`, fixed `badOffs[kXR_pgMaxEpr]`, `boCount`, and `pathID`.

Control flow: users reset at request setup, call `boAdd()` for each failed page/segment, then call `boInfo()` once when building the final response.

State and persistence behavior: per-object in-memory request state only; file-level state is updated indirectly by `boAdd()`.

Dependencies: `XProtocol/XProtocol.hh` and forward-declared `XrdXrootdFile`.

Integration points: base class for `XrdXrootdPgwCtl` and optional collaborator for `XrdXrootdPgrwAio`.

Risks: fixed offset capacity requires protocol and implementation limits to stay aligned. `boReset()` clears only the count, leaving old bytes in arrays but making them ignored.

Test signals: reset reuse, offset capacity boundaries, response length calculation, and path ID propagation into traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwBadCS.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwCtl.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwCtl.cc

Purpose: implements pgwrite control framing: it maps client checksum+data stream layout into iovec frames that can be read from the socket and verified/written in bounded chunks.

Important APIs/types/functions: constructor preinitializes response status and iovec checksum/data slots. `Setup()` computes total layout for a pgwrite request using `XrdOucPgrwUtils::recvLayout()`. `Advance()` moves to the next frame when the request is larger than the current buffer.

Control flow: `Setup()` clears any previous short-read iovec length, validates the requested offset/length layout, computes maximum iovec elements supported by the current `XrdBuffer`, refreshes data buffer pointers when the buffer changes, sets the first data pointer for unaligned leading data, initializes frame counters and response offset, and resets bad-checksum state. `Advance()` restores the first data slot to a full page, consumes remaining iovec entries, applies short final segment length when needed, and recomputes the socket read length for the next frame.

State and persistence behavior: state is per-control object: current buffer pointer/size, iovec counts and remaining entries, current frame length, end segment length, index needing reset, checksum vector, and response status/body. No durable storage is owned; inherited bad-checksum state may update file-level tracking during verification elsewhere.

Dependencies: `XrdOucPgrwUtils`, `XrdSysPlatform`, `XrdXrootdFile`, `XrdXrootdPgwFob`, `XrdBuffer`, protocol constants, and `XrdXrootdPgwBadCS`.

Integration points: used by pgwrite request handlers to produce `getData()` iovecs and later expose checksum vector/data pointers through `FrameInfo()` and `FrameLeft()`.

Risks: assumes caller-provided buffers are at least 4 KiB and sizes are power-of-1K; too-small buffers produce logic errors. `fixSRD` must be reset or short final-page lengths leak into later requests. `iovMax` calculation floors by page size, so non-page-sized buffers waste tail space. Layout must remain synchronized with `XrdOucPgrwUtils`.

Test signals: aligned and unaligned writes, request larger than 1 MiB, short last page, small buffer rejection, repeated reuse with different buffers, `Advance()` frame lengths, and checksum/data pointer extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwCtl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwCtl.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwCtl.hh

Purpose: declares the pgwrite control object that combines bad-checksum tracking with socket iovec layout and final response metadata.

Important APIs/types/functions: constants `crcSZ`, `maxBSize` (`1 MiB`), and `maxIOVN`; response fields `resp` and `info`; methods `Setup`, `Advance`, `FrameInfo()` overloads, and `FrameLeft()`. Internal arrays `csVec` and `ioVec` hold checksums and alternating checksum/data iovecs.

Control flow: a handler calls `Setup()` for a request, uses `FrameInfo(iovn,rdlen)` to read checksum+data from the socket, verifies/writes the frame, then calls `Advance()` until all frames are consumed. The second `FrameInfo()` exposes decoded checksum vector and contiguous data when the caller still owns the expected buffer.

State and persistence behavior: per-object transient request state, with inherited bad-checksum collection. Persistent effects are external file writes and bad-offset tracking.

Dependencies: `sys/uio.h`, `XProtocol`, `XrdBuffer`, `XrdSysPageSize`, and `XrdXrootdPgwBadCS`.

Integration points: used by synchronous pgwrite paths and related AIO helpers to avoid hand-building iovec layouts at each call site.

Risks: the overload returning checksum/data pointers validates buffer identity; callers that pass a recycled/different `XrdBuffer` get null. `FrameLeft()` arithmetic depends on the alternating iovec layout. The fixed max buffer/iovec sizing must be kept in step with protocol page size.

Test signals: `FrameInfo` null when buffer mismatches, partial-frame `FrameLeft()` lengths, max buffer layout, page-size constant changes, and response status fields for pgwrite final result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwCtl.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwFob.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwFob.cc

Purpose: implements destructor-time diagnostics for the per-file pgwrite checksum-tracking object.

Important APIs/types/functions: `XrdXrootdPgwFob::~XrdXrootdPgwFob()` logs warnings and optional trace details about outstanding checksum errors, fixed counts, and remaining bad extents.

Control flow: on destruction, it counts uncorrected bad offsets. If any remain, it logs a warning with the file key. When page-checksum tracing is enabled, it formats each bad extent as length/page-index and emits either a detailed remaining-area trace or a summary trace when all errors were fixed.

State and persistence behavior: reads `badOffs`, `numErrs`, `numFixd`, and `fileP`. The destructor itself does not persist repairs; it emits log/trace diagnostics at file-object teardown.

Dependencies: `XrdOucString`, `XrdSysError`, `XrdXrootdFile`, `XrdXrootdPgwFob`, `XrdXrootdTrace`, protocol page-size constants, and global `XrdXrootd::eLog`.

Integration points: file objects owning `pgwFob` get final diagnostics when closed/destroyed after pgwrite checksum activity. `XrdXrootdPgwBadCS::boAdd()` populates this object.

Risks: destructor assumes `fileP` and `fileP->FileKey` are still valid. Diagnostic formatting can become large for many bad offsets but is gated by trace for detailed output. Warnings on outstanding errors are operationally important and should not be suppressed accidentally.

Test signals: destruction with no errors, fixed errors only, outstanding errors, trace enabled/disabled, offset length encoding for full and partial pages, and file key lifetime during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwFob.cc -->
