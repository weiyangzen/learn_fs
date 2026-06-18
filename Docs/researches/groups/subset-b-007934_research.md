# subset-b-007934 research

Grouped research for the XRootD CMS files in `sources/distributed-fs/xrootd/src/XrdCms`. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPList.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPList.cc

Purpose: implements the mutable path-prefix list used by CMS cache/path ownership tracking. The list is sorted by decreasing path length so longest-prefix matches win for `Find()` and `Type()`, and so mask propagation can handle subpaths before parent paths.

Important APIs/functions: `XrdCmsPList_Anchor::Add()` inserts a unique path without mask inheritance; `Find()` returns the first prefix match into an `XrdCmsPInfo`; `Insert()` merges read-only/read-write/staging masks for an advertised path and adjusts subset/superset masks; `Remove()` clears a server mask from all entries and deletes empty entries; `Type()` reports `w`, `r`, or `?`; `XrdCmsPList::PType()` returns `w`, `r`, `ws`, or `rs`.

Control flow: all public anchor mutations lock the anchor mutex, traverse the singly linked list, and unlock before returning. `Insert()` first walks entries with length greater than or equal to the new path, merging incoming masks into subset entries, then either updates the exact path or creates a new node and inherits masks from matching shorter parent prefixes.

State and persistence: state is in-memory only: linked `XrdCmsPList` nodes with duplicated path strings and `XrdCmsPInfo` bitmasks. There is no disk persistence; path state is rebuilt from logins/configuration and removed by server mask.

Dependencies/integration: uses `SMask_t` from `XrdCmsTypes.hh` and `XrdSysMutex`. It is used through `Cache.Paths` by protocol admission and forwarding (`XrdCmsProtocol::AddPath`, `ConfigCheck`, `Reissue`) to determine which servers handle a path.

Risks: prefix matching uses raw `strncmp` over path length, so callers must normalize paths and avoid ambiguous prefixes such as `/a` matching `/abc` unless that is an accepted CMS convention. `new XrdCmsPList` is unchecked. `First()` exposes the list without locking, so callers need external discipline. Misspelling in comments is harmless.

Test signals: exercise insertion order, duplicate `Add()`, exact/superset/subset mask merging, `Remove()` deleting empty entries, and longest-prefix `Find()` behavior with read-only, read-write, and staging masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPList.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPList.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPList.hh

Purpose: declares the path-list data structures that associate exported path prefixes with server availability masks. It is the public interface for path ownership lookup and mutation.

Important APIs/types: `XrdCmsPInfo` carries `rovec`, `rwvec`, and `ssvec` masks and exposes inline `And()`, `Or()`, and `Set()` helpers. `XrdCmsPList` stores one path entry and exposes `Next()`, `Path()`, and `PType()`. `XrdCmsPList_Anchor` owns the mutex and head pointer and provides `Add()`, `Empty()`, `Find()`, `First()`, `Insert()`, `NotEmpty()`, `Remove()`, `Type()`, and `Zorch()`.

Control flow: callers interact mostly with the anchor, which serializes mutation and lookup. `Empty()` and `Zorch()` support whole-list replacement or transfer, while `First()` is a raw head accessor.

State and persistence: path entries own `strdup()`-allocated pathnames and free them in their destructor. `pathtype` and `reserved` are present but unused in this subset. The structure persists only for the process lifetime.

Dependencies/integration: includes C string allocation helpers, `XrdCmsTypes.hh` for masks, and `XrdSysPthread.hh` for locking. It is a low-level dependency of CMS cache path tracking.

Risks: constructors do not handle `strdup()` failure. `XrdCmsPInfo::And()` mutates masks and returns whether anything remains, which can be misread as a pure predicate. `First()` and returned node pointers can race if used without anchor locking.

Test signals: compile tests should catch mask type width changes; unit-level tests should verify copy assignment, destructor cleanup under sanitizers, and anchor whole-list operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsParser.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsParser.cc

Purpose: defines CMS request/response serialization schemas and response decoding. It binds `kYR_*` protocol codes to `XrdOucPupArgs` layouts for login, locate/select, prepare, forwarding operations, load, availability, and simple path requests.

Important APIs/functions: static initializer `XrdCmsParseInit` builds PUP argument names; `XrdCmsParser::XrdCmsParser()` populates `vecArgs`; `Decode()` maps manager/redirector responses into `SFS_REDIRECT`, `SFS_STALL`, `SFS_STARTED`, `SFS_DATA`, or `SFS_ERROR`; `mapError(const char *)` and `mapError(int)` translate CMS/string errors to `errno`; `Pack()` serializes a request into iovecs using the selected schema.

Control flow: request schemas are arrays with `Fence`, `End`, `Datlen`, and `EndFill` markers. `Decode()` reads an optional network-order integer followed by message bytes, switches on `hdr.rrCode`, populates `XrdOucErrInfo`, and hijacks oversized data buffers for `SFS_DATA`.

State and persistence: global static parser state includes the PUP name table, PUP instance, schema arrays, vector table, and global `XrdCms::Parser`. No persistent state is written.

Dependencies/integration: depends on `YProtocol.hh` CMS constants, `XrdCmsRRData`, `XrdOucPup`, `XrdOucBuffer`, `XrdOucErrInfo`, and SFS return codes. `XrdCmsProtocol` uses it to parse inbound requests; `XrdCmsResp` uses `Decode()` for asynchronous replies.

Risks: schema and `XrdCmsRRData::ArgName` order must stay synchronized. `Decode()` trusts response header codes and buffer length after minimal checks. Unknown error strings/values collapse to `EINVAL`, which can hide semantic failures. The constructor uses a non-atomic static `Done`, though this is normally initialized during startup.

Test signals: round-trip pack/unpack for every populated `kYR_*` route, malformed payload coverage, large `kYR_data` buffer handoff, and `mapError` coverage for all protocol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsParser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsParser.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsParser.hh

Purpose: declares the CMS parser facade around `XrdOucPup`. It exposes static helpers for decoding redirector responses, mapping errors, packing outbound requests, and parsing login/general request payloads.

Important APIs/types: `Decode()`, both `mapError()` overloads, `Pack()`, `Parse(CmsLoginData *)`, `Parse(int, ..., XrdCmsRRData *)`, static `Pup`, `PupArgs()`, and the global `XrdCms::Parser`. Private static schema arrays map protocol request codes to unpacking layouts.

Control flow: inline `Parse()` zeros selected pointer fields before unpacking so recycled POD objects do not retain stale pointers. `PupArgs()` bounds-checks request codes before indexing `vecArgs`.

State and persistence: all parser schemas are static and process-wide. Parsed string pointers reference the request buffer owned by `XrdCmsRRData`; no copies are made here.

Dependencies/integration: includes `YProtocol.hh`, `XrdCmsRRData.hh`, and `XrdOucPup.hh`. It is embedded in `XrdCmsProtocol` as `ProtArgs` and exported as `XrdCms::Parser`.

Risks: parse success depends on caller-owned buffers living long enough. `rnum` is checked only against the upper bound, not negative values, though protocol codes are normally unsigned/small. Adding a new CMS request requires updating this header and the `.cc` schema vector.

Test signals: static analyzer checks for negative indexing risk, tests for recycled `XrdCmsRRData` pointer reset, and compilation coverage when `kYR_MaxReq` or `ArgName` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsParser.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPerfMon.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPerfMon.hh

Purpose: defines the plugin ABI for CMS performance monitoring. Runtime-loaded libraries inherit `XrdCmsPerfMon` to supply load metrics and optionally receive asynchronous reporting callbacks.

Important APIs/types: virtual `Configure()` receives config filename, directive parameters, logger, CMS monitor callback object, environment, and an `isCMS` flag. `PerfInfo` carries eight one-byte load fields with `Clear()`. `GetInfo()` is polled for metrics; `PutInfo()` reports metrics asynchronously to the CMS monitor.

Control flow: default implementations are no-ops except `Configure()` returns `false`, requiring plugins to override it. Plugin authors expose a file-level `XrdCmsPerfMonitor` pointer and version metadata.

State and persistence: the base class holds no state. `PerfInfo` is transient, with load values expected in the 0-100 range.

Dependencies/integration: forward declares `XrdOucEnv` and `XrdSysLogger`. It integrates with `cms.perf` dynamic loading and CMS scheduler/load reporting.

Risks: ABI stability matters because external plugins compile against this header. Load values are not range-enforced. The documentation says plugin `PutInfo()` will never be called, so implementers must understand directionality.

Test signals: plugin load smoke tests, ABI/version checks, and metric boundary tests for 0, 100, and out-of-range provider behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPerfMon.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepArgs.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepArgs.cc

Purpose: implements a static producer/consumer queue for prepare requests and converts parsed `XrdCmsRRData` into a durable `XrdCmsPrepArgs` job object that owns the request buffer.

Important APIs/functions: constructor steals `Arg.Buff`, copies protocol header and parsed pointers, computes co-location path when stage+coloc options are present, and prepares a two-element iovec. `getRequest()` waits on `PAReady` and dequeues. `Process()` is the worker loop. `Queue()` appends and wakes the worker when idle.

Control flow: prepare request producers call `Queue()`. The single static worker loop either calls `PrepQ.Prepare()` when disk services are enabled or `DoIt()` to perform server selection/forwarding when local disk is unavailable.

State and persistence: static queue state is `First`, `Last`, `isIdle`, `PAQueue`, and `PAReady`. Each object owns `Data` and frees it in the destructor. No disk persistence occurs here.

Dependencies/integration: depends on `XrdCmsConfig`, `XrdCmsPrepare`, `XrdCmsNode::do_SelPrep`, `XrdJob`, and CMS protocol request structures.

Risks: `Next` is not initialized in the constructor before queueing, relying on later assignment discipline. `Process()` has an apparent leak/ownership issue in the `!Config.DiskOK` branch: `getRequest()->DoIt()` calls `DoIt()`, which deletes only when `do_SelPrep()` returns false; otherwise ownership is external and must be verified. `isIdle` is manually maintained and sensitive to missed posts.

Test signals: thread sanitizer queue tests, destructor ownership tests after buffer stealing, stage+coloc parsing cases, and worker behavior with `Config.DiskOK` both true and false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepArgs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepArgs.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepArgs.hh

Purpose: declares the prepare request job container used to defer or stage CMS prepare operations.

Important APIs/types: public fields mirror parsed request data (`Request`, `Ident`, `reqid`, `notify`, `prty`, `mode`, `path`, `opaque`, `clPath`, `options`, `pathlen`, `ioV`). `DoIt()` delegates selection to `XrdCmsNode::do_SelPrep`. Static `Process()`, `Queue()`, and `getRequest()` manage the global queue. `iovNum` fixes forwarded prepare messages at header plus payload.

Control flow: instances are constructed from `XrdCmsRRData`, queued, then consumed by the static worker. `DoIt()` may delete the object depending on downstream return behavior.

State and persistence: the object owns a single stolen `Data` allocation from `XrdCmsRRData`; pointer fields refer into that buffer. Static queue fields hold pending work process-wide.

Dependencies/integration: includes CMS node/request data, `XrdJob`, and `XrdSysPthread`. It bridges parser/protocol request data to `XrdCmsPrepare` and node selection.

Risks: public mutable fields expose internals to many consumers. Buffer ownership is non-obvious because pointers are aliases into `Data`. Queue state is global, making isolated tests require cleanup or process isolation.

Test signals: construction should leave source `XrdCmsRRData` buffer null; queued objects should be processed FIFO; sanitizer tests should catch use-after-free of aliased fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepArgs.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepare.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepare.cc

Purpose: implements the CMS prepare/staging manager. It tracks pending staged files, dispatches add/delete requests to either the built-in FRM proxy or an external prepare scheduler, sends UDP notifications, and periodically scrubs/reset staging state.

Important APIs/functions: global `XrdCms::PrepQ`; `Add()` submits a prepare request and records pending path; `Del()` cancels by request id; `Exists()` and `Gone()` query/update the pending hash; `Prepare()` stages only when a file is not online; `Inform()` sends `avail` notifications; `Reset()` initializes and refreshes FRM/external scheduler state; `setParms()` configures scrub/reset intervals, external command, message substitutions, and name translation; private `isOnline()`, `Scrub()`, and `startIF()` drive health.

Control flow: `Prepare()` uses OSS `Stat()` with resource-only/access-time flags. Offline files are submitted if staging is allowed, online files notify requestors. `Scrub()` alternates between applying `XrdCmsScrubScan` to remove now-online entries and full scheduler reset after `resetcnt` scans. External scheduler protocol writes `+`, `-`, and `?` command lines and reads pending paths.

State and persistence: in-memory `PTable` tracks pending LFNs and `NumFiles`. External persistence belongs to FRM or the prepare program. Administrative state includes `prepif`, `prepMsg`, `Relay`, `PrepFrm`, `prepOK`, scrub counters, and last error timestamp.

Dependencies/integration: depends on `Config.ossFS`, `Config.DiskSS`, `XrdFrcProxy`, `XrdOucStream`, `XrdOucMsubs`, `XrdNetMsg`, `XrdOss`, scheduler `Sched`, and trace/error logging.

Risks: comments note `Reset()` and `startIF()` must be called with `PTMutex`; public `Reset(const...)` calls private `Reset()` without taking `PTMutex`, so initialization-time single-thread assumptions matter. External scheduler command construction depends on valid, non-null prepare fields. `strcpy(baseAP, aPath)` can overflow if `aPath` exceeds 1023 bytes. UDP notify mutates `notify` temporarily by replacing `/` with null and does not restore it, which is acceptable only because the object is soon discarded.

Test signals: fake OSS plus fake prepare stream tests for add/delete/reset/scrub; FRM proxy integration tests; long path/config fuzzing; notification formatting tests for `udp://host/arg`; and lock-order/thread sanitizer checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepare.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepare.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepare.hh

Purpose: declares the process-wide prepare queue manager object that coordinates staging requests and pending-file bookkeeping.

Important APIs/types: public methods `Add`, `Del`, `Exists`, `Gone`, `DoIt`, `Init`, `Inform`, `isOK`, `Pending`, `Prepare`, `Reset`, and `setParms` cover queue submission, cancellation, status, initialization, and configuration. Private members include `PTMutex`, `PTable`, `prepSched`, `N2N`, `prepMsg`, `Relay`, `PrepFrm`, `prepif`, and scrub counters.

Control flow: as an `XrdJob`, `DoIt()` can be scheduled periodically for scrub work. The public `Prepare()` entry is used by `XrdCmsPrepArgs::Process()`.

State and persistence: `PTable` and counters are in-memory mirrors of pending staged paths. External scheduler or FRM maintains durable staging work outside this class.

Dependencies/integration: includes `XrdJob`, `XrdScheduler`, `XrdCmsPrepArgs`, `XrdOucHash`, `XrdOucStream`, and pthread wrappers. Exports global `XrdCms::PrepQ`.

Risks: destructor intentionally does nothing, so process-lifetime ownership is assumed. Public methods expose char pointers rather than const-correct strings. The class has both external-program and FRM modes, increasing configuration and test matrix complexity.

Test signals: compile coverage for both FRM-enabled and external scheduler paths, pending count invariants, and scheduled scrub behavior over several intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepare.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsProtocol.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsProtocol.cc

Purpose: implements the CMS wire protocol plugin and connection lifecycle. It covers protocol loading, port discovery, outbound manager connections, inbound login admission, request dispatch, async job scheduling, forwarding/reissue, redirector handling, ping timeouts, and protocol object pooling.

Important APIs/functions: exported `XrdgetProtocol()` and `XrdgetProtocolPort()` integrate with Xrd protocol loading. `Execute()` routes a parsed request to `XrdCmsNode` methods and optionally forwards it. `Match()` recognizes CMS logins. `Pander()` maintains outgoing manager/supervisor sessions. `Process()` handles inbound sessions. `Admit()` validates login roles, builds `XrdCmsNode`, registers paths, updates cluster/meter state, and chooses response routing. `Admit_Redirector()` registers redirectors in `RTable`. `Dispatch()` reads headers/payloads, validates route options, parses arguments, and runs sync or scheduled async work. `Reissue()`, `Reply_Delay()`, `Reply_Error()`, `SendPing()`, and `Sync()` handle downstream protocol responses and thread quiescence.

Control flow: phase 0/1/2 configuration flows through `XrdgetProtocolPort()` then `XrdgetProtocol()`. Inbound links first `Match()`, then `Process()` calls `Admit()` and dispatches until timeout or disconnect. Outbound manager links use `Pander()` in a reconnect loop with alternate managers, redirection handling, login mode updates, and cleanup after `Dispatch()`. Async requests allocate `XrdCmsJob` and increment protocol refs so `Sync()` can wait before node deletion.

State and persistence: static state includes `ProtStack`, `ProtMutex`, `readWait`, and `ProtArgs`. Per-connection state includes `Link`, `Routing`, `myNode`, manager pointer, redirector slot, ref count/semaphore, login flag, and nonblocking send queue state. Persistent cluster state is external to this file; this file mutates in-memory cluster/path/meter state.

Dependencies/integration: this is a central integration point for `Config`, `Cluster`, `Cache`, `Manager`, `ManTree`, `Meter`, `CmsState`, `RTable`, `XrdCmsLogin`, `XrdCmsRouting`, `XrdCmsRole`, `XrdCmsNode`, `XrdCmsJob`, Xrd networking/link APIs, and `XrdOucPup` parsing.

Risks: `Dispatch()` bounds payloads to 16 KiB but relies on route tables and parser schemas staying synchronized. `AddPath()` accepts path type characters and mutates node write/stage flags; bad exported path types fail login. Protocol object pooling requires `Init()` to reset every field. Ref counting is manual across async jobs. Login role compatibility is dense and should be regression-tested for proxy/peer/meta-manager cases. `ConfigCheck()` removes path masks and bounces cache on CRC changes, so path string normalization matters.

Test signals: integration tests for login roles, redirector admission limits, payload size rejection, malformed request parsing, async job ref synchronization, manager redirection, suspend/delay behavior, forwarded operation TTL, and path reconfiguration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsProtocol.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsProtocol.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsProtocol.hh

Purpose: declares the CMS `XrdProtocol` implementation and its connection state. It is the class used both for accepted CMS links and scheduled outbound manager connections.

Important APIs/types: public `Alloc`, `DoIt`, `Execute`, `Match`, `Process`, `Recycle`, `Ref`, and `Stats`. Private helpers include `Admit`, `Admit_Redirector`, `AddPath`, `ConfigCheck`, `Dispatch`, `Init`, `Login_Failed`, `Pander`, `Reissue`, `Reply_Delay`, `Reply_Error`, `SendPing`, and `Sync`. `Bearing` distinguishes down/lateral/up connection timeout behavior.

Control flow: `Alloc()` pulls from a static freelist and calls `Init()`. `DoIt()` is the job entry for outbound manager pander roles. `Process()` is the accepted-link entry. `Ref()`/`Sync()` coordinate async jobs with link teardown.

State and persistence: static freelist/parser/read-wait plus per-instance link, node, routing, manager, redirector slot, ref count, and flags. No persistent data is stored in the class directly.

Dependencies/integration: includes `XrdProtocol`, `XrdCmsParser`, `XrdCmsTypes`, and pthread wrappers. It forward-declares CMS manager/node/request/routing types to reduce header coupling.

Risks: header declares `Admit_DataServer`, `Admit_Supervisor`, and `Authenticate()` although this `.cc` subset does not define/use them, likely legacy declarations. Manual pooling and raw pointers make initialization completeness important. `maxReqSize` is fixed at 16 KiB.

Test signals: object-pool reuse tests should assert fields reset by `Init()`; ABI/compile tests should catch stale private declarations; dispatch tests should verify `maxReqSize`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsProtocol.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRData.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRData.cc

Purpose: implements buffer allocation and object pooling for CMS request/response data containers used by protocol dispatch.

Important APIs/functions: `getBuff(size_t)` frees any existing buffer, chooses an alignment based on page size and requested size, uses `posix_memalign`, stores `Buff` and `Blen`, and returns success. `Objectify()` either recycles an object into a static free list or returns an initialized object from that list/new allocation.

Control flow: callers request an object with no argument and return it by passing the pointer back. A static mutex protects the free list. Reused objects reset `Ident` and `Next`, but not every field, so parsers/protocol code must clear relevant fields before use.

State and persistence: static free list is process-local. Each object owns an aligned `Buff` until stolen by `XrdCmsPrepArgs`, replaced by `getBuff()`, or held for reuse. No disk persistence.

Dependencies/integration: uses `sysconf(_SC_PAGESIZE)`, `posix_memalign`, `XrdSysMutex`, and `XrdCmsRRData.hh`. Used heavily by `XrdCmsProtocol::Dispatch()`.

Risks: `getBuff(0)` would request questionable alignment/size behavior; callers currently use positive datalen. The free list never shrinks, so peak request pressure determines retained memory. Partial reset in `Objectify()` can leave stale scalar fields if callers forget to overwrite them.

Test signals: allocation size/alignment tests, repeated recycle tests under thread sanitizer, and parser reuse tests for stale fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRData.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRData.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRData.hh

Purpose: declares POD-style containers for parsed CMS request data and redirector login data.

Important APIs/types: `XrdCmsRLData` holds auth/SID/path strings and total length. `XrdCmsRRData` contains the request header, parsed string fields for operation arguments, options, path length, disk/load values, a union for `dskUtil`/`waitVal`, backing buffer metadata, routing flags, `ArgName` enum used by parser schemas, static `Objectify()`, `getBuff()`, and free-list `Next`.

Control flow: parser schemas fill fields by offset into this POD. Protocol dispatch reads headers/payloads into `Buff`, then `XrdCmsParser` points fields into that buffer.

State and persistence: object state is transient and mostly references the owned buffer. Comments intentionally omit constructors/destructors so the type behaves like POD for `XrdOucPup`.

Dependencies/integration: includes `YProtocol.hh` for CMS headers/constants. `ArgName` must align with `XrdCmsParser` PUP name definitions.

Risks: POD design means no automatic cleanup of `Buff`; ownership is manual. String fields become invalid if `Buff` is freed or stolen. Adding fields can break parser offset assumptions.

Test signals: schema offset/ArgName sync tests, memory sanitizer tests for buffer lifetime, and compile warnings around POD assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRData.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRQ.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRQ.cc

Purpose: implements the fast redirect/locate response queue. It waits for server response masks, piggybacks compatible requests, times out unresolved requests, and sends either direct redirect/location data or wait replies back to redirectors.

Important APIs/functions: global `XrdCms::RRQ`; `Add()` allocates a slot and queues/piggybacks by key; `Del()` marks a slot ready with zero masks; `Init()` builds response templates and starts responder/timeout threads; `Ready()` accumulates masks and moves a slot to ready when enough responses arrive; `Respond()` drains ready slots; `sendLocResp()`, `sendLwtResp()`, and `sendRedResp()` format and send response variants; `TimeOut()` advances a logical clock and expires wait queue slots; `XrdCmsRRQSlot::Alloc()`/`Recycle()` manage slot free lists and piggyback chains.

Control flow: `Add()` queues a pending slot with `Expire=myClock+1`. `Ready()` updates masks and either waits for additional responders (`minR`) or moves to ready. The responder separates locate piggybacks from redirect piggybacks because they require different wire formats. The timeout thread wakes when wait queue transitions from empty and periodically moves expired slots to ready.

State and persistence: fixed `Slot[1024]` pool, separate wait/ready doubly linked lists, global slot free list, shared response buffers, stats counters, timeout slice/delay, and logical `myClock`. State is in-memory and concurrent.

Dependencies/integration: depends on `Cluster.List`, `Cluster.Select`, `XrdCmsNode::do_LocFmt`, `RTable.Find`, network byte order helpers, timers, and CMS protocol response structs.

Risks: slot 0 is reserved/unusable; running out of free slots causes `Add()` to return 0. Shared `hostbuff/databuff` and response templates are used by the single responder thread; additional responder threads would race. Timeout precision is logical and coarse. Piggyback chains rely on correct key/slot validity and `Recycle()` cleanup.

Test signals: stress tests for 1023 concurrent slots, piggyback locate/select combinations, timeout-to-wait behavior, multi-response `minR`, redirector disconnect during `RTable.Find`, and stats consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRQ.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRQ.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRQ.hh

Purpose: declares the fast-response queue types used to coordinate redirector requests awaiting server/cluster results.

Important APIs/types: `XrdCmsRRQInfo` identifies a waiting request by cache key, stream id, redirector slot/instance, access mode, locate mode, response quorum, lookup options, interface preference, and rw server vector. `XrdCmsRRQSlot` stores one queued request plus piggyback chains. `XrdCmsRRQ` exposes `Add`, `Del`, `Init`, `Ready`, `Respond`, `Statistics`, and `TimeOut`, plus `Info` counters.

Control flow: callers add slots and later call `Ready()` when server masks are known; background threads perform response and timeout work.

State and persistence: fixed-size slot pool (`numSlots=1024`), wait/ready queues, response iovecs/templates, shared buffers, counters, timeout configuration, and semaphore/mutex synchronization.

Dependencies/integration: includes protocol integer types, CMS masks, `XrdOucDLlist`, and pthread wrappers. Exports global `XrdCms::RRQ`.

Risks: public statistics are snapshot-copied under lock but per-interval counters are folded in the responder. Fixed buffer sizes (`hostbuff[288]`, locate data from `RHLen*STMax`) must match formatter output. Static slot free list is separate from queue mutex, so lock ordering must remain stable.

Test signals: compile coverage when `STMax` or locate response size changes, concurrency tests for add/ready/timeout/recycle, and stats reset/reporting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRQ.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRTable.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRTable.cc

Purpose: implements the redirector table, a process-wide slot map from short redirector numbers to `XrdCmsNode` objects.

Important APIs/functions: global `XrdCms::RTable`; `Add()` finds a free slot from 1 to `maxRD-1`, updates high-water mark, and returns the slot; `Del()` removes a node and shrinks high-water mark; `Find()` validates slot and node instance; `Send()` broadcasts a message to all redirectors.

Control flow: `Add`, `Del`, and `Send` take the internal mutex. `Find()` intentionally does not lock; callers must hold `Lock()`/`UnLock()` around find plus node use to prevent deletion races.

State and persistence: `Rtable[maxRD]` stores raw node pointers and `Hwm` tracks scan range. No persistent state.

Dependencies/integration: depends on `XrdCmsNode`, CMS mask constants, and trace logging. Used by `XrdCmsProtocol::Admit_Redirector`, `XrdCmsRRQ` fast responses, and `XrdCmsState` status broadcasts.

Risks: manual locking contract for `Find()` is easy to violate. Slot exhaustion returns 0 and rejects redirector login. Raw pointers require redirector deletion to remove the table entry first.

Test signals: add/delete/hwm edge cases, slot reuse, instance mismatch on stale slot, and lock-order checks with RRQ/state send paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRTable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRTable.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRTable.hh

Purpose: declares the redirector slot table used for fast replies and state broadcast.

Important APIs/types: `Add`, `Del`, `Find`, `Send`, explicit `Lock` and `UnLock`, private `Rtable[maxRD]`, and `Hwm`. Exports global `XrdCms::RTable`.

Control flow: the explicit lock methods are part of the API because `Find()` must be called while holding the lock and the caller may need to send while the node cannot be deleted.

State and persistence: process-local table initialized to null with high-water mark `-1`.

Dependencies/integration: includes `XrdCmsNode`, `XrdCmsTypes`, and `XrdSysPthread`.

Risks: raw pointer table and external lock discipline are fragile. `maxRD` controls scale and must fit into `short` slot ids used elsewhere.

Test signals: static assertions or compile checks around `maxRD`, and unit tests for table initialization and broadcast selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRTable.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRedirLocal.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRedirLocal.cc

Purpose: implements a CMS client plugin that can convert eligible redirects to local `file://` redirects when both client and selected target are on private networks.

Important APIs/functions: exported `XrdCmsGetClient()` constructs the plugin. Constructor wraps a native remote CMS finder. `Configure()` loads local redirect settings and configures the native finder. `loadConfig()` parses `xrdcmsredirlocal.readonlyredirect`, `xrdcmsredirlocal.httpredirect`, `xrdcmsredirlocal.localroot`, and fallback `oss.localroot`. `Locate()` delegates normal locate, then conditionally rewrites the response to a local file URL. `Space()` delegates.

Control flow: `Locate()` first detects possible localroot redirect loops and falls back to regular CMS locate after stripping localroot if `tried=localhost` is present. It then calls native locate, blocks HTTP unless enabled, requires private target and private client, checks client URL/local redirect capabilities for non-HTTP, filters unsafe write flags when read-only mode is configured, and sets `Resp` to `file://localroot + path` before returning `SFS_REDIRECT`.

State and persistence: plugin state is `nativeCmsFinder`, `readOnlyredirect`, `httpRedirect`, `localroot`, and logger. Config is read from the xrootd config file only at configure time.

Dependencies/integration: wraps `XrdCmsFinderRMT` through `XrdCmsClient`; uses `XrdOucStream`, `XrdNetAddr`, `XrdOucEnv` security environment, SFS flags, and version metadata.

Risks: `EnvInfo` and `secEnv()->addrInfo` are assumed non-null. Config boolean parsing treats any value containing `true` as true. Flag filtering uses numeric thresholds and a hard-coded HTTP stat flag (`0x20000000`), which can drift from SFS definitions. Loop handling depends on `tried=localhost` string presence.

Test signals: plugin configure tests with missing/relative localroot, private/public client-target matrix, HTTP enabled/disabled behavior, read-only flag filtering, localroot loop handling, and delegated `Space`/forwarding methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRedirLocal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRedirLocal.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRedirLocal.hh

Purpose: declares the local redirect CMS client plugin and forwards most `XrdCmsClient` behavior to a native remote finder.

Important APIs/types: constructor/destructor, `Configure`, `loadConfig`, `Locate`, `Space`, forwarding wrappers for `Added`, `Forward`, `isRemote`, `Managers`, `Prepare`, `Removed`, `Resume`, `Suspend`, `Resource`, `Reserve`, and `Release`. Public state includes the wrapped `nativeCmsFinder`, configuration flags, `localroot`, and logger.

Control flow: only `Locate()` and configuration are custom; all other CMS client functions delegate to the native finder to preserve normal CMS behavior.

State and persistence: plugin instance owns `nativeCmsFinder` and configuration values. No persistent data is written.

Dependencies/integration: includes CMS finder/client, network address, OSS, OUC env/stream/string, SFS flags, version metadata, C++ `string`, and `fcntl.h`.

Risks: wrapper methods assume `nativeCmsFinder` is non-null. Public data members make mutation possible outside the class. Header README says readonly default is false, while constructor initializes `readOnlyredirect(true)`, so documentation/config expectations should be reconciled.

Test signals: compile/plugin ABI tests, null native finder defensive tests if construction fails, and configuration default tests to pin readonly behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRedirLocal.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsResp.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsResp.cc

Purpose: implements asynchronous response callback handling for redirector responses. It captures original caller error/callback state, queues network replies for decoding, invokes the original callback after `waitresp` synchronization, and pools response objects.

Important APIs/functions: `XrdCmsResp::Alloc()` obtains/reuses a response object and installs a synchronization callback into the caller's `XrdOucErrInfo`; `Recycle()` returns objects to a capped free list; instance `Reply()` queues a decoded network response; static `Reply()` runs the consumer loop; `ReplyXeq()` decodes and invokes the original callback; `XrdCmsRespQ::Add`, `Purge`, and `Rem` manage response lookup by message id.

Control flow: a request that expects delayed callback allocates an `XrdCmsResp`, stores it in a queue, and replaces the original callback with `SyncCB`. When a network reply arrives, `Reply()` enqueues it on the ready queue and posts `isReady`. The reply thread decodes with `XrdCmsParser::Decode()`, waits for `SyncCB` to confirm `waitresp` reached the client, then calls the original callback and arranges for `Done()` to recycle the object.

State and persistence: static ready queue, static object free list capped at 300, per-object response header/buffer/manager name/user id/callback state, and `XrdCmsRespQ` hash buckets. No disk persistence.

Dependencies/integration: depends on `XrdCmsParser`, `XrdOucErrInfo`, `XrdOucBuffer`, SFS return codes, semaphores/mutexes, and client message flow.

Risks: callback lifetime and semaphore ordering are subtle; missing `SyncCB.Post()` can deadlock `ReplyXeq()`. `Alloc()` manually copies selected `XrdOucErrInfo` state and depends on stable path/user storage. `XrdCmsRespQ::Rem()` hashes `msgid % mqSize`; negative ids would be unsafe if ever passed.

Test signals: callback synchronization tests, delayed response decode tests for redirect/wait/data/error, object pool cap tests, purge/rem hash collision tests, and deadlock detection when callback is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsResp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsResp.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsResp.hh

Purpose: declares asynchronous response callback objects and the message-id response queue.

Important APIs/types: `XrdCmsRespCB` is a semaphore-backed callback used to signal that a `waitresp` was sent. `XrdCmsResp` inherits `XrdOucEICB` and `XrdOucErrInfo`, exposes `Alloc`, `Done`, `ID`, instance/static `Reply`, `Same`, and `setDelay`, and stores callback/buffer state. `XrdCmsRespQ` provides `Add`, `Purge`, and `Rem` over 512 buckets.

Control flow: `XrdCmsResp` acts as both error info and callback object during different phases. `XrdCmsRespCB::Init()` drains stale semaphore posts before reuse.

State and persistence: all state is process-local: ready queue, freelist, response queue buckets, and per-response fields. `RepDelay` is configurable but not used in this `.cc` subset.

Dependencies/integration: includes `XrdOucErrInfo`, pthread wrappers, and CMS protocol headers.

Risks: private inheritance from `XrdOucEICB` in `XrdCmsRespCB` is intentional but unusual. `Same()` always returns 0, so callback matching does not filter. Raw pointers to buffers/callbacks require strict lifecycle control.

Test signals: response queue bucket collision tests, semaphore drain tests, and ABI/compile checks for callback signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsResp.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRole.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRole.hh

Purpose: centralizes CMS role identifiers, display names, and compact type codes.

Important APIs/types: `RoleID` enumerates meta manager, manager, supervisor, server, proxy manager/supervisor/server, peer manager, peer, and noRole. `Convert()` maps config tokens to role ids. `Name()` returns human-readable names. `Type(RoleID)` returns compact codes such as `MM`, `M`, `R`, `S`, `PM`, `PR`, `PS`, `EM`, and `E`. `Type(const char *)` maps compact prefixes back to broad role categories.

Control flow: functions are static inline and table driven. `Convert()` supports one-token standard roles and two-token `proxy`/`meta` forms.

State and persistence: no mutable state; static const name arrays live in function scope.

Dependencies/integration: includes `<cstring>`. Used by protocol admission to label links and assign role IDs to nodes.

Risks: token matching is case-sensitive and exact. `Type(const char *)` maps any `P*` to `proxy` and any `E*` to `peer`, losing manager/server specificity. Comments require type strings to fit in four bytes including null.

Test signals: role token parsing matrix, name/type table bounds, and config parser tests for invalid roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRole.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRouting.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRouting.cc

Purpose: instantiates CMS routing tables: request-code-to-node-method dispatch plus per-role validation/behavior flags for manager, redirector, response, server, and supervisor connections.

Important APIs/data: `initRouter` maps request names to `XrdCmsNode::do_*` handlers for login, metadata operations, locate/select, prepare, server status, load, ping/pong, space/state/status/update/usage. `initMANrouting`, `initRDRrouting`, `initRSProuting`, `initSRVrouting`, and `initSUProuting` define `isSync`, `Forward`, `noArgs`, `Delayable`, `Repliable`, `AsyncQ0`, and `AsyncQ1` permissions. Globals `Router`, `manVOps`, `rdrVOps`, `rspVOps`, `srvVOps`, and `supVOps` are constructed from these arrays.

Control flow: `XrdCmsProtocol::Dispatch()` uses the active `XrdCmsRouting` to validate each incoming request and decide sync/async/parse behavior. `Execute()` uses `Router` to invoke the node method and checks `Forward`/`Repliable`/`Delayable`.

State and persistence: static process-wide lookup tables; no runtime mutation after construction.

Dependencies/integration: depends on `XrdCmsNode` handler declarations and `XrdCmsRouting.hh`. It is tightly coupled to protocol constants in `YProtocol.hh`.

Risks: missing or mismatched route entries can silently reject valid requests or allow wrong behavior for a role. `kYR_login` has no handler by design. Adding a request code requires updates in parser schemas and every applicable routing table.

Test signals: table completeness tests comparing protocol constants, route flag tests per role, and integration tests ensuring destructive operations are not accepted from meta-manager roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRouting.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRouting.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRouting.hh

Purpose: declares route flag lookup and node-method dispatch table helpers for CMS protocol request codes.

Important APIs/types: `XrdCmsRouting` flags include invalid, sync, forward, no args, delayable, repliable, and two async queues. `getRoute()` returns flags for a request code. `XrdCmsRouter` maps request codes to display names and `XrdCmsNode` member-function handlers via `getMethod()` and `getName()`. Namespace exports the global router and per-role routing tables.

Control flow: constructors zero arrays and consume sentinel-terminated init arrays. Lookups return invalid/null/`?` for out-of-range or missing codes.

State and persistence: fixed arrays sized by `XrdCms::kYR_MaxReq`; immutable after initialization.

Dependencies/integration: includes `YProtocol.hh` and forward declares `XrdCmsNode`/`XrdCmsRRData`. Used by `XrdCmsProtocol` dispatch and diagnostics.

Risks: constructors do not guard init array request codes against `kYR_MaxReq`, so bad initializer data could write out of bounds. Route flags are bitmasks that can be combined incorrectly without compiler help.

Test signals: initializer bounds tests/static assertions, route table sentinel tests, and request-name coverage checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRouting.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSecurity.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSecurity.cc

Purpose: implements CMS security handshake helpers, security service loading, virtual node id creation, token retrieval, and system id export.

Important APIs/functions: `Authenticate()` is server-side authentication over CMS `kYR_xauth` request/response loops using `XrdSecService`; `Configure()` loads the security service and protocol factory; `getVnId()` obtains a virtual node id from a file, literal value, or plugin; `getToken()` returns outbound security parameters; `Identify()` is client-side credential exchange; `setSecFunc()` injects a protocol factory; `setSystemID()` builds and exports `XRDCMSVNID`, `XRDCMSCLUSTERID`, and `XRDCMSSYSID`; private `chkVnId()` validates length/characters.

Control flow: authentication loops exchange CMS auth messages until the XrdSec protocol succeeds or fails. `getVnId()` dispatches by leading character: `<` file, `=` literal, `@` plugin. `setSystemID()` derives an instance and cluster id from `XRDINSTANCE`, optional vnid/tag, and manager list suffix differences.

State and persistence: static `DHS` security service and module-level `getProtocol`. Environment variables are exported for CMS system identity. No files are written except reading vnid input.

Dependencies/integration: uses `XrdCmsTalk`, `XrdSecLoadSecurity`, `XrdSecProtocol`, `XrdOucPinLoader`, `XrdOucTList`, `XrdNetAddrInfo`, `XrdLink`, and `XrdSysFD`.

Risks: `chkVnId()` allows most punctuation except `&` and space; security policy depends on that being acceptable. `setSystemID()` returns string-literal error markers cast as `char *` for some failures and heap strings for success, so callers must distinguish ownership. `Configure()` serializes service load with a static mutex but global `DHS` replacement semantics need care. `Authenticate()` sends `Toksz+1`, including null terminator.

Test signals: mock XrdSec handshake success/failure loops, vnid file/literal/plugin validation, invalid characters/length tests, environment export tests, and ownership tests for `setSystemID()` return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSecurity.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSecurity.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSecurity.hh

Purpose: declares static CMS security helper APIs used by login/authentication and configuration code.

Important APIs/types: `Authenticate`, `Configure`, `getVnId`, `getToken`, `Identify`, `setSecFunc`, and `setSystemID`. Private static `DHS` holds the loaded security service, and `chkVnId()` validates virtual node ids.

Control flow: all operations are static, so no instance state is required. The class acts as a namespace with access to private static service state.

State and persistence: static process-wide security service pointer; generated system id strings/environment are handled in the implementation.

Dependencies/integration: includes `XrdSecInterface.hh` and references CMS headers through `XrdCms::CmsRRHdr` in method signatures.

Risks: because `XrdNetAddrInfo` and `XrdCms::CmsRRHdr` are used without local forward declarations/includes in this header, transitive include order matters. Static global security state complicates tests and reload behavior.

Test signals: header self-sufficiency compile test, repeated configure tests, and API smoke tests with security disabled/enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSecurity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSelect.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSelect.hh

Purpose: declares selection request/response data structures used by cache, locate, select, and prepare paths to choose CMS nodes.

Important APIs/types: `XrdCmsSelect` carries input path, optional fast RRQ info, avoid mask, selected mask, prepare iovec, options, alternate hash, output vectors, and response data. Option flags encode write/create/truncate/online/defer/peers/refresh/asap/noBind/meta/freshen/replica/retry/multiwrite/advisory/pending/interface and packed/reference/directory/alternate-hash modes. `XrdCmsSelected` describes one candidate node for locate/list output. `XrdCmsSelector` records selection failure reasons and exclusion booleans.

Control flow: selectors fill `Vec`, `smask`, and `Resp` based on options. `XrdCmsSelected` linked lists are returned by cluster list/select operations and formatted for locate responses.

State and persistence: these are transient stack/heap request containers. `XrdCmsSelect::Path` wraps the caller-provided path buffer; no persistent storage.

Dependencies/integration: includes `netinet/in.h` and `XrdCmsKey.hh`; forward declares `XrdCmsRRQInfo`. Used by `XrdCmsNode`, `Cluster`, `Cache`, `RRQ`, and prepare selection code.

Risks: dense bitmask values include overlaps by design (`Create = 0x000A0` combines create/truncate semantics), so consumers must mask correctly. Fixed `SelDSZ=256` response buffer must hold host/error data. Constructor does not initialize every field (`nmask`, `iovP`, `iovN`, vectors, flags), so callers must set required fields before use.

Test signals: option bitmask regression tests, constructor initialization tests, locate formatting length tests, and selection failure reason tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSelect.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsState.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsState.cc

Purpose: implements global CMS state monitoring for suspend and staging availability. It computes aggregate state from admin files, node counts, frontend health, disk space, and staging count, then broadcasts status changes to managers/redirectors.

Important APIs/functions: global `XrdCms::CmsState`; constructor initializes suspended/no-stage defaults. `Enable()` samples admin files and forces first notification. `Monitor()` waits for state changes and sends `kYR_status` updates through `RTable` and `XrdCmsManager::Inform`. `Port()` returns the frontend data port. `sendState()` sends current suspend/stage state to a link. `Set()` configures minimum node count and admin file paths. `Status()` converts bit changes into protocol modifiers and logs transitions. `Update()` changes state inputs for active counts, staging counts, frontend status, space, and admin stage/suspend controls.

Control flow: state changes call `Update()`, which recomputes `currState`, `Suspended`, and `NoStaging`; if enabled and changed, it posts the monitor semaphore. `Monitor()` calculates deltas from `prevState`, formats modifiers, optionally embeds the data port on resume, broadcasts to redirectors when appropriate, and informs managers.

State and persistence: in-memory counters/flags plus admin sentinel files `NOSTAGE` and `SUSPEND` under configured admin path. `Update(Stage/Active)` creates or unlinks those files to reflect administrative state. `NoStageFile` and `SuspendFile` are allocated strings.

Dependencies/integration: uses CMS protocol status structs, `XrdLink`, `XrdCmsManager`, `RTable`, trace logging, POSIX `stat/open/unlink`, and semaphores/mutexes.

Risks: `Set(ncount,isman,AdminPath)` uses fixed `fnbuff[1048]` with `strcpy`; long admin paths can overflow. `Update(Active)` has duplicated unlink branches that may be intentional but should be reviewed. `sendState()` sends only the header size rather than the full `CmsStatusRequest`, matching its zero-datalen header but worth preserving in tests. Monitor is an infinite loop with process-lifetime ownership.

Test signals: admin file creation/removal tests, state transition matrix for suspend/no-stage/frontend/space/counts, redirector broadcast tests, initial `Enable()` notification, and long admin path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsState.cc -->
