# subset-b-007933 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsFinder.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsFinder.cc

Purpose: implements the CMS client finder entry points for two deployment roles. `XrdCmsFinderRMT` is the redirector/proxy/client-facing finder that translates SFS operations into CMS protocol requests sent to remote managers. `XrdCmsFinderTRG` is the target/server-side finder that maintains a local admin socket to `cmsd`, reports file and performance events, and executes local requests from `cmsd` against the storage plugin.

Important APIs/types/functions: `XrdCmsFinderRMT::{Configure,Forward,Locate,Prepare,Space,SelectManager,send2Man,StartManagers,VCheck}` and `XrdCmsFinderTRG::{Configure,Added,Removed,Locate,PutInfo,Reserve,Release,Resource,Resume,Suspend,RunAdmin,RunPM,Start,Hookup,Process,VCheck}`. Local thread wrappers start manager connection threads, async reply workers, perfmon, and cmsd-interface loops.

Control flow: remote configuration reads `XrdCmsClientConfig`, obtains `XrdInet*` and security hooks from `XrdOucEnv`, starts `XrdCmsClientMan` objects, and optionally starts a hidden target responder when a normal manager has a meta-manager. `Forward()` maps named file operations to `kYR_*` request codes, packs `XrdCmsRRData` with `Parser.Pack`, throttles multi-manager destructive broadcasts, and either sends a two-way request through `send2Man()` or sends to one manager and informs the rest. `Locate()` maps SFS flags, IP-family capabilities, affinity, and retry metadata into `CmsLocateRequest` or `CmsSelectRequest` bits. `Prepare()` handles cancel (`prepdel`) and per-path `prepadd` messages with optional notification and co-location priority. Target mode connects repeatedly to a Unix-domain cmsd path, writes a text login line, reads binary `CmsRRHdr` requests, parses `mv/rm/rmdir`, and calls `XrdOss`.

State and persistence behavior: no disk persistence. Process state includes circular manager chains, per-manager hash table, timing/rate-limit fields, wait intervals, saved path tracing, local cmsd stream state, resource reservation counters, and active/suspended reporting. Network and socket state is long-lived and auto-reconnected. `Resp` may carry delayed error info, redirect data, or external buffers.

Dependencies: CMS client config/manager/message/response/parser/security/RRData, SFS and OSS interfaces, `XrdOucEnv`, `XrdOucStream`, `XrdNetSocket`, `XrdSysThread/Timer/Plugin`, and protocol definitions from `YProtocol.hh`.

Integration points: `XrdCmsClient.cc` constructs these classes for remote or target clients. Remote mode is the bridge from xrootd SFS calls to cmsd managers. Target mode is the bridge from local xrootd file events and OSS mutations back to cmsd. Perfmon plugins call `PutInfo()` through the `XrdCmsPerfMon` API.

Risks: request packing has fixed iovec capacities and returns generic internal errors on overflow. `SelectManager()` returns no manager when the hashed/first manager is suspended even if later managers may be active. Target `Suspend()` calls `myData.UnLock()` without taking `myData.Lock()` in the visible code, unlike `Resume()`, which is a high-risk locking bug if this source is current. `StartManagers()` caps managers at `MaxMan` and logs ignored extras. cmsd local requests are limited to 16 KiB and loss of framing forces reconnect. Manual ownership of config lists, notification buffers, and streams requires careful cleanup.

Test signals: tests should cover flag-to-option translation for locate/select, two-way reply timeout and retry delays, all-manager forwarding for `mv/rm/rmdir`, prepare notification/co-location packing, local locate output, cmsd reconnect, local `mv/rm/rmdir` execution with mocked `XrdOss`, manager suspension/failover, and thread sanitizer coverage for `Resume/Suspend` locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsFinder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsFinder.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsFinder.hh

Purpose: declares the two concrete CMS finder classes used through the `XrdCmsClient` interface: remote manager-facing finder `XrdCmsFinderRMT` and target cmsd-facing finder `XrdCmsFinderTRG`.

Important APIs/types/functions: `XrdCmsFinderRMT` exposes file-location, prepare, forwarding, space, manager listing, and version-check methods. Its private surface contains manager selection, two-way sends, local locate formatting, manager startup, and broadcast inform helpers. `XrdCmsFinderTRG` exposes file add/remove notifications, local locate, perf/resource reporting, suspend/resume, resource reservation, admin startup, and performance monitor execution while privately handling cmsd hookup and request processing.

Control flow: the header separates client roles at type level. Remote instances configure outbound `XrdCmsClientMan` manager connections and submit packed CMS requests. Target instances configure a local cmsd admin channel and report state/load/file changes upward. Both provide `Managers()` for configuration consumers and static `VCheck()` for plugin compatibility.

State and persistence behavior: `XrdCmsFinderRMT` owns manager tables/lists, configuration wait intervals, mode flags, and selector behavior. `XrdCmsFinderTRG` owns an `XrdOss*`, cmsd socket stream, login line, active state, resource counters, and optional perfmon pointer/interval. State is in-memory and tied to daemon lifetime.

Dependencies: depends on `XrdCmsClient`, `XrdCmsPerfMon`, pthread mutexes, SFS prep types, OSS, OUC env/error/list types, and version info. It forward-declares most heavy types to reduce include pressure.

Integration points: included by client factory code, local redirector support, and components needing CMS manager lists or target perfmon reporting. The class methods implement the public CMS client contract used by xrootd storage and redirector logic.

Risks: header exposes raw pointers and manual ownership semantics for manager lists, `CMSPath`, `Login`, and stream pointers. The two classes share method names but very different semantics, so callers must instantiate the right role. `MaxMan` is a hard cap. Resource counters are protected by `rrMutex`, but active stream writes require consistent `myData` locking in the implementation.

Test signals: compile tests for plugin ABI, construction in all role modes, manager list ownership, local/remote `Locate()` behavior, `Managers()` lifetime, and version compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsFinder.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsJob.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsJob.cc

Purpose: implements pooled scheduler jobs that execute a CMS protocol request asynchronously against an `XrdCmsProtocol` instance.

Important APIs/types/functions: static `XrdCmsJob::Alloc()`, `DoIt()`, and `Recycle()`, plus static pool state `JobMutex` and `JobStack`. It uses global `XrdCms::Sched`.

Control flow: `Alloc()` pops a job from `JobStack` under `JobMutex` or creates a new one, stores the protocol/data pointers, sets the scheduler comment to the protocol role, and increments the link reference. `DoIt()` calls `theProto->Execute(*theData)`. If execution returns `-EINPROGRESS`, it reschedules the same job for `theData->waitVal + time(0)`. Otherwise it releases the protocol reference and recycles. `Recycle()` decrements the link ref, objectifies/releases the RR data buffer, and pushes the job back on the free stack.

State and persistence behavior: state is an in-memory freelist of reusable job objects. Link/protocol references are used as lifetime guards while scheduled work is pending. No disk persistence.

Dependencies: `XrdScheduler`, `XrdJob`, `XrdLink`, `XrdCmsProtocol`, `XrdCmsRRData`, CMS tracing, and errno/time APIs.

Integration points: `XrdCmsProtocol` schedules request processing through these jobs when immediate inline handling is undesirable or a request must sleep and resume.

Risks: correctness depends on balanced protocol and link reference updates. A job rescheduled for `-EINPROGRESS` keeps the same data pointer and must not be recycled elsewhere. Allocation failure logs but leaves caller to handle null. The object pool never shrinks, matching daemon lifetime assumptions.

Test signals: unit tests with fake protocol returns for success, error, and `-EINPROGRESS`; reference-count assertions around `Alloc()`/`Recycle()`; scheduler tests verifying delayed reschedule; leak/race tests under concurrent allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsJob.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsJob.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsJob.hh

Purpose: declares `XrdCmsJob`, the `XrdJob` subclass used to run CMS protocol request execution on the scheduler and recycle job objects.

Important APIs/types/functions: `Alloc(XrdCmsProtocol*, XrdCmsRRData*)`, `DoIt()`, `Recycle()`, constructor, and private pool members `JobMutex`, `JobStack`, `JobLink`, `theProto`, and `theData`.

Control flow: the interface promises a lifecycle of allocate, schedule/execute, optionally reschedule, then recycle. `DoIt()` is the scheduler callback inherited from `XrdJob`.

State and persistence behavior: instances hold transient protocol and request data pointers. Static state holds a process-local freelist. There is no persistent state.

Dependencies: includes CMS protocol wire definitions indirectly through `YProtocol.hh`, `XrdJob`, and pthread mutexes. It forward-declares the protocol and RR data classes.

Integration points: used by `XrdCmsProtocol` and `XrdScheduler` as the async request work item for CMS connections.

Risks: raw pointers mean ownership is implicit and enforced only by implementation discipline. Copying is not disabled in the header, so accidental copies would be unsafe, though normal use allocates dynamically through `Alloc()`.

Test signals: compile integration with scheduler, pool reuse tests, and static analysis for copy misuse/reference lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsKey.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsKey.cc

Purpose: implements hashing and pooled allocation/unload/recycle for CMS cache key items. These objects back `XrdCmsCache` and the `XrdCmsNash` hash table.

Important APIs/types/functions: `XrdCmsKey::setHash()`, `XrdCmsKeyItem::{Alloc,Recycle,Reload,Replenish,Stats,Unload}` and static state `TockTable`, `Free`, `numFree`, `numHave`, `numNull`.

Control flow: `setHash()` computes CRC32 over the key path and coerces zero to one. `Alloc()` pops a free item, stamps it into the current tick bucket, bumps the key reference byte away from zero, clears pending counters, and returns it; if the free list is empty, it repeatedly calls `Replenish()` to allocate `minAlloc` objects. `Recycle()` frees the key string, clears hash state, increments the ref byte, and pushes the item to `Free`. `Reload()` reinserts an existing item into its tick bucket. `Unload(tock)` removes a tick bucket, moves entries whose `TOD` changed to the correct bucket, and makes remaining entries unfindable by moving the hash into `Loc.HashSave`. `Unload(item)` removes one item from its tick chain and similarly saves/clears its hash.

State and persistence behavior: all state is process-memory cache state. Tick buckets provide time-based grouping for cache unload/recycle. Items are allocated in large arrays and normally never individually deleted.

Dependencies: `XrdOucCRC`, `XrdCmsTypes`, CMS tracing and error logging, C allocation/free.

Integration points: `XrdCmsNash::Add()` obtains items here, and `XrdCmsNash::Recycle()` expects `Unload()` to have saved the original hash in `Loc.HashSave`. `XrdCmsCache` uses key location fields for file/server presence and pending redirect state.

Risks: there is no internal locking in this file; callers must serialize access. `operator=` in the header duplicates `Val`, so `Recycle()` must own/free that memory. Tick/ref wraparound is mitigated by avoiding zero ref but still relies on cache discipline. `Unload()` temporarily clears hashes, so recycling without saved hashes breaks hash-table removal.

Test signals: hash determinism, zero-hash fallback, allocation after replenish, recycle string ownership, unload-by-tick bucket movement, unload-by-item hash save, stats reset of `numNull`, and concurrency tests at the cache layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsKey.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsKey.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsKey.hh

Purpose: declares the key, location, and item structures used by the CMS namespace-location cache.

Important APIs/types/functions: `XrdCmsKey` stores path value, length, CRC hash, tick/ref fields, and equivalence operators. `XrdCmsKeyLoc` stores server masks for have/pending/query, server currency, nil-entry lifetime, saved hash/deadline, and pending redirect counts. `XrdCmsKeyItem` combines a key and location with hash/freelist links and exposes pooled allocation, reload, unload, recycle, replenish, and stats.

Control flow: the header defines fast inline equality by hash/path and approximate equivalence by hash/ref. `XrdCmsKeyItem` lifecycle is allocate from pool, insert into cache/hash, unload from tick tracking, recycle back to free list.

State and persistence behavior: cache entries are transient in memory. `hfvec`, `pfvec`, and `qfvec` persist file-location knowledge within the running cmsd. `lifeline` and `deadline` encode time-based validity, not durable state.

Dependencies: `XrdCmsTypes.hh` for `SMask_t`, C string helpers.

Integration points: used by `XrdCmsCache`, `XrdCmsNash`, cluster selection, state query dispatch, and redirect wait queues.

Risks: manual memory ownership of `Val` is subtle: constructors can wrap non-owned input, but assignment duplicates. No destructor frees `Val`; recycling does. Inline `Equiv()` ignores `Val` and relies on hash/ref uniqueness. No built-in locking.

Test signals: copy/equality behavior, location assignment preserving masks/counters, item pool lifecycle, and cache-level tests for stale key invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsKey.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsLogin.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsLogin.cc

Purpose: implements the CMS login handshake between cmsd peers/managers and clients, including packed login exchange, optional security challenge/response, blacklist rejection/redirect, and login error handling.

Important APIs/types/functions: `XrdCmsLogin::Admit()`, static `Login()`, `sendData()`, `Emsg()`, and blacklist helpers `SendErrorBL()`.

Control flow: `Admit()` reads the full request with `XrdCmsTalk::Attend`, authenticates if a token is configured, initializes response login data, parses the incoming login payload through `Parser.Parse`, checks blacklist status for non-directors, fills SID/env CGI for compatible versions, and sends a packed login response. `Login()` sets the blacklist-redirect capability, sends packed login data, clears outbound pointer fields, receives a response header/body, handles `kYR_xauth` by identifying through `XrdCmsSecurity`, handles `kYR_try` redirects by unpacking hosts into `Data.Paths`, handles `kYR_error`, and parses normal login data. `sendData()` packs login fields into iovecs and splits sends around `IOV_MAX`.

State and persistence behavior: state is per-handshake. Returned `SID`, `envCGI`, and redirect path strings are duplicated for caller ownership. Login mode bits and protocol version affect cross-version persistent compatibility.

Dependencies: `XrdLink`, `YProtocol.hh`, `XrdCmsParser`, `XrdCmsTalk`, `XrdCmsSecurity`, `XrdCmsBlackList`, `XrdOucPup`, network byte-order helpers, and CMS logging.

Integration points: used by manager/client connection setup (`XrdCmsClientMan`) and server admission paths. Blacklist redirects can trigger manager rerouting and permanent topology changes.

Risks: fixed 4096-byte login response buffer rejects larger replies. Error handling returns a mix of CMS error codes, `-1`, and `kYR_EINVAL`, so callers must interpret carefully. Packed pointer fields are manually cleared/duplicated. Security depends on external token/identify functions. `sendData()` ignores the return value of `Link->Send()`.

Test signals: successful login parse/pack round trip, xauth challenge, blacklist hard error, blacklist redirect, malformed try host data, oversized replies, IOV splitting, and version compatibility with/without SID/env CGI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsLogin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsLogin.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsLogin.hh

Purpose: declares the CMS login helper for admitting inbound links and initiating outbound CMS login handshakes.

Important APIs/types/functions: instance `Admit(XrdLink*, CmsLoginData&, const char *sid, const char *envP)`, static `Login(XrdLink*, CmsLoginData&, int timeout)`, constructor with optional parse buffer, and private helpers for authentication, error logging, packing/sending login data, and blacklist errors.

Control flow: inbound code constructs an `XrdCmsLogin` around a receive buffer and calls `Admit()`. Outbound code calls `Login()` with filled `CmsLoginData`. Private helpers keep wire packing and rejection logic out of connection setup code.

State and persistence behavior: object state is only the receive buffer pointer/length. Login payload fields describe persistent runtime identity such as SID, paths, environment, hold time, space, ports, and mode, but this class does not store them beyond the call.

Dependencies: `XProtocol/XPtypes.hh`, `YProtocol.hh`, `sys/uio.h`, and `XrdLink` forward declaration.

Integration points: protocol admission and manager/client connection setup rely on this class for CMS wire compatibility and authentication/blacklist behavior.

Risks: raw buffer pointers require caller-managed lifetime. `Authenticate()` is declared but implementation delegates through security helpers rather than this symbol in the current file, so declarations and definitions should be kept audited. Timeout default `-1` means blocking behavior depends on `XrdLink`.

Test signals: header/API compile tests, buffer lifetime tests around `Admit()`, outbound default-timeout behavior, and ABI checks for use from client manager code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsLogin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManList.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManList.cc

Purpose: implements a thread-safe alternate-manager list used when managers redirect nodes to other managers or supervisor levels.

Important APIs/types/functions: local `XrdCmsManRef`, `XrdCmsManList::{Add(netAddr,redList,port,lvl),Add(ref,manager,port,lvl),Del,getRef,Next}`.

Control flow: public `Add()` gets or creates a reference id for the source network address, deletes any previous entries for that ref, tokenizes the redirect list, and adds each target. Private `Add()` parses optional ports, canonicalizes addresses to names, rejects duplicates, and inserts by manager level. `Del()` removes all entries with a reference id and repairs the iteration pointer. `getRef()` formats an address, looks it up in `refList`, or inserts a new negative reference number. `Next()` returns the current manager/port/level and advances the round-robin pointer, resetting to the head when exhausted.

State and persistence behavior: in-memory linked lists only: `refList` maps source addresses to refs, `allMans` stores alternate managers, and `nextMan` is iteration state. Entries own duplicated manager names.

Dependencies: `XrdNetAddr`, `XrdNetAddrInfo`, `XrdOucTList`, `XrdOucTokenizer`, `XrdSysMutex`, and platform string helpers.

Integration points: `XrdCmsManager` owns an `XrdCmsManList` and `XrdCmsNode::do_Try()` adds alternates from redirect hints. Protocol connection code can call `Next()` to attempt alternate managers.

Risks: `refList` is not freed in the destructor, while `allMans` is. `Next()` returns level zero both for no entry and for a root-level manager, so callers need buffer/port side effects to distinguish if necessary. `Add()` mutates the token buffer temporarily when parsing ports. Insertion-by-level logic is fragile around head ordering.

Test signals: duplicate suppression, IPv4/IPv6 host:port parsing, address canonicalization, deletion by ref while iterating, level ordering, round-robin wraparound, and leak checks for ref list ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManList.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManList.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManList.hh

Purpose: declares the alternate manager list abstraction that stores redirect-derived manager endpoints and returns them one at a time.

Important APIs/types/functions: `Add()`, `Del()`, `getRef()`, `haveAlts()`, `Next()`, constructor/destructor, and private `XrdCmsManRef` linked-list state guarded by separate ref and manager-list mutexes.

Control flow: callers add all redirect targets for a source address, delete by source, and iterate with `Next()` until it returns no manager; the next call restarts at the list head.

State and persistence behavior: process-local manager endpoint cache only. `refList` tracks which source address created which manager entries; `allMans` and `nextMan` hold manager list and cursor.

Dependencies: `XrdSysPthread`, `XrdNetAddr`, `XrdOucTList`, and private implementation class `XrdCmsManRef`.

Integration points: manager reconfiguration and try/redirect processing use this list to discover alternative manager routes.

Risks: raw `char *` endpoint input is parsed in implementation. Thread safety is per-method, not per-iteration transaction. The class is linked-list based and not copy-protected.

Test signals: API compile tests, concurrent add/delete/next stress, and redirect workflow tests from node try handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManTree.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManTree.cc

Purpose: coordinates concurrent manager connection attempts so a server forms a minimal manager tree: either connections to all root nodes or one interior supervisor, avoiding phantom arcs.

Important APIs/types/functions: constructor, `Abort()`, `Connect()`, `Disc()`, `Register()`, and `Trying()`, plus private semaphore helpers `Pause()` and `Redrive()` from the header.

Control flow: `Register()` assigns each manager connection worker a table slot. `Trying()` records the level being attempted and enforces rules: aborted workers stop; if already connected to an interior node, later workers wait; root-level attempts wake waiting workers and force them back to root discovery; only one non-root attempt may proceed at a time. `Connect()` accepts a root connection only when all max connections are root, but an interior connection disbands other connected root nodes by sending `kYR_disc` and marks the tree connected to that supervisor. `Disc()` marks a lost connection active again and reopens connection attempts if the root set or selected interior connection was lost. `Abort()` wakes all waiters with level zero and permanently marks the tree aborted.

State and persistence behavior: all state is in-memory connection coordination: per-slot status, level, node pointer, counts of connected/waiting workers, selected connection level/id, root flag, and overall status.

Dependencies: `XrdCmsManager::MTMax`, `XrdCmsNode::Send()`, `YProtocol.hh` for `kYR_disc`, mutex/semaphore primitives, and CMS logging/tracing.

Integration points: `XrdCmsManager::Run()` creates a fresh tree per manager-site run. Connection workers consult it during topology discovery and manager redirects/reconfiguration abort it.

Risks: semaphore wakeups and status transitions are delicate; missing `Redrive()` can strand workers. `Register()` assumes at most `MTMax` callers and performs no bounds check. `Connect()` sends disconnects while holding the tree mutex, so blocking send behavior would be dangerous if `Send()` can stall. Aborted state is terminal.

Test signals: simulated parallel root/interior attempts, wake/retry behavior, disconnect of selected supervisor, abort with waiters, max-slot bounds under stress, and topology invariants after non-deterministic connection order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManTree.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManTree.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManTree.hh

Purpose: declares the manager-connection tree coordinator used to serialize and validate root versus interior manager connection attempts.

Important APIs/types/functions: `Abort()`, `Connect()`, `Disc()`, `Register()`, `Trying()`, enum `connStat`, constructor, private `TreeInfo` slots with semaphore/node/status/level, and counters for active topology state.

Control flow: callers register once, call `Trying()` before attempting a level, call `Connect()` after successful connection, and call `Disc()` after loss. Private `Pause()` and `Redrive()` implement wait/wake transitions.

State and persistence behavior: fixed-size per-process coordination table sized by `XrdCmsManager::MTMax`; no durable persistence.

Dependencies: `XrdCmsManager.hh` for `MTMax`, `XrdCmsNode` forward declaration, and pthread mutex/semaphore wrappers.

Integration points: owned by `XrdCmsManager` for each site-manager connection group and consulted by CMS protocol connection setup.

Risks: no explicit copy prevention and fixed `tmInfo` capacity. The header inlines lock-unlock behavior in `Pause()`; callers must follow the expected lock-held protocol.

Test signals: compile/API tests, status transition unit tests, and thread sanitizer tests for wait/wake paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManTree.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManager.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManager.cc

Purpose: implements the global manager-connection controller for cmsd: starting outbound manager connections, registering active manager nodes, broadcasting protocol messages to managers, handling redirects/reconfiguration, and verifying consistent cluster identity.

Important APIs/types/functions: `XrdCmsManager::{Add,Delete,Finished,Inform,Remove,Rerun,Reset,Run,Start,Verify}` and local scheduler job `XrdCmsDelNode`. Static shared state is `MTMutex`, `MastTab`, `MastSID`, and `MTHi`.

Control flow: `Start()` groups configured managers by site id, creates one `XrdCmsManager` per site, and calls `Run()`. `Run()` skips circular self-connections, allocates `XrdCmsProtocol` jobs for each target, resets `XrdCmsManList` and `XrdCmsManTree`, clears saved site identity, and schedules connection jobs. `Add()` registers a connected manager node in the static table unless reconfiguration is pending or `MTMax` is full. `Inform()` iterates active manager nodes, temporarily drops `MTMutex` while sending under node locks, and supports raw buffers, iovecs, or header+payload helpers. `Rerun()` parses a new manager list from a blacklist redirect, aborts the tree, marks current site nodes doomed/blacklisted, and sends disconnects. `Finished()` waits until all current manager connections drain, swaps in the pending list, clears old table entries, and restarts. `Verify()` stores the first seen site SID/name and rejects later managers for the same site with different cluster identity.

State and persistence behavior: in-memory topology state only. Static tables are shared across manager instances and persist for daemon lifetime. Per-instance state tracks current/pending manager lists, site id, current count, redirect flag, and first verified SID/site/host.

Dependencies: scheduler, CMS config/protocol/node/man-list/man-tree/routing/utils, `XrdOucTList`, `XrdNetAddr`, tokenizer, timers, and logging.

Integration points: `XrdCmsNode` uses `Inform()`, `Reset()`, and manager pointers. Protocol connection setup calls `Add()`, `Remove()`, `Finished()`, and `Verify()`. File/state/load notifications propagate upward through this class.

Risks: manager objects are intentionally never deleted. Static table operations require strict `MTMutex` discipline. `MastSID` is a `char` but site IDs are handled as ints up to `MTMax`; keeping values within range is essential. `Rerun()` mutates global connection state and marks nodes doomed while active sends may still be in progress. `Finished()` calls `Run()` while holding `MTMutex`, so nested lock behavior must remain safe.

Test signals: startup with multiple sites, self-connection filtering, max manager limit, broadcast under node removal, pending reconfiguration drain/restart, blacklist redirect flow, SID mismatch rejection, and race tests for add/remove/inform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManager.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManager.hh

Purpose: declares the single-instance-style manager controller that tracks outbound manager nodes and broadcasts CMS events to them.

Important APIs/types/functions: public `myMans`, `ManTree`, `MTMax`, `Add()`, `Delete()`, `Finished()`, four `Inform()` overloads, `Present()`, `Remove()`, `Rerun()`, `Reset()`, `Start()`, `Verify()`, constructor, and private `Run()`. Static table fields hold active manager nodes.

Control flow: the public API supports manager startup, node admission/removal, topology reconfiguration, reset propagation, and message broadcast.

State and persistence behavior: static active-manager table and per-site current/pending manager lists live for daemon lifetime. No disk persistence.

Dependencies: `YProtocol.hh`, `XrdCmsManList`, `XrdCmsTypes`, pthread mutexes, and forward-declared link/node/list/tree types.

Integration points: central dependency for node command handling, protocol connection jobs, manager tree construction, and cluster event propagation.

Risks: public raw pointers expose owned helper objects. Static shared state means multiple `XrdCmsManager` instances are coordinated manually by site id. Destructor intentionally does not free resources.

Test signals: API compile tests, static table bounds, `Present()` behavior, and integration tests with `XrdCmsProtocol` manager connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsMeter.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsMeter.cc

Purpose: implements the global CMS load/space meter. It monitors local filesystem capacity, consumes external or plugin performance metrics, computes weighted load, and reports usage/space changes to managers.

Important APIs/types/functions: global `XrdCms::Meter`, `XrdCmsMeter::{Init,Monitor,Run,RunFS,RunPM,PutInfo,Update,Record,Report,FreeSpace,TotalSpace,calcLoad,calcSpace,SpaceMsg,UpdtSpace}`.

Control flow: construction sets all counters to neutral values. `Init()` reads initial `XrdOssVSInfo`, computes minimum/high-water free thresholds from config, calls `calcSpace()`, updates `CmsState::Space`, starts an FS meter thread, and logs capacity. `Monitor(char*,int)` validates and starts an external program, while `Monitor(int)` loads/configures a perfmon plugin and optionally starts a polling thread. `Run()` repeatedly execs the external program and parses metric lines through `Update()`. `RunFS()` sleeps at `dsk_calc` intervals, recalculates space, toggles no-space state based on min/high-water hysteresis, and sends state updates. `PutInfo()` and `Update()` clamp/parse metrics, compute weighted load, and trigger `XrdCmsNode::Report_Usage(0)` when load changes exceed fuzz. `FreeSpace()` and `TotalSpace()` return physical or virtual cluster-space values.

State and persistence behavior: in-memory current metrics, disk totals/free/utilization, threshold displays, monitor process/thread state, virtual filesystem cache, and reporting timestamps. No durable persistence, but it drives cluster-visible state.

Dependencies: `XrdCmsConfig`, `XrdCmsCluster`, `XrdCmsState`, `XrdCmsNode`, `XrdCmsUtils`, `XrdOss`, `XrdOucStream`, thread/timer/platform APIs, and perfmon plugin interface.

Integration points: `XrdCmsNode::do_Load()`, `do_Space()`, and `Report_Usage()` call into the meter. Cluster managers use these reports for selection and staging decisions. Perfmon plugins can call `PutInfo()`.

Risks: `Monitor(int)` declares a local `monPerf` that shadows the member and then `RunPM()` uses the member, which appears to leave the member null in this source and would crash if the polling thread runs. The condition `if (monint)` likely intended `if (itv)`, so plugin polling may not start as expected. External monitor output must be exactly five unsigned values. The destructor kills only the monitor thread, not the FS thread. Disk totals are cached initially and may be stale if filesystems are added/removed.

Test signals: threshold/hysteresis tests for min/high-water transitions, mocked `StatVS()` failures and zero-total retries, external monitor parse tests, plugin monitor polling tests that catch the shadowing bug, virtual FS update tests, load fuzz alert tests, and thread cleanup/leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsMeter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsMeter.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsMeter.hh

Purpose: declares `XrdCmsMeter`, the CMS performance and filesystem-space monitor, and the global `XrdCms::Meter` instance.

Important APIs/types/functions: load calculators, `FreeSpace()`, `TotalSpace()`, `Init()`, `Monitor()` overloads, `PutInfo()`, `Record()`, `Report()`, `Run()`/`RunFS()`/`RunPM()`, virtual filesystem controls `setVirtual()`/`setVirtUpdt()`, and private helpers for space calculation and display scaling.

Control flow: callers initialize disk monitoring, optionally start an external or plugin perf monitor, then query/report current load and space through the public API. Background threads use the `Run*` methods.

State and persistence behavior: stores current disk and load metrics, thresholds, monitor program/plugin state, mutexes, virtual FS flags, and thread id. All state is volatile daemon memory.

Dependencies: `XrdCmsPerfMon`, `XrdSysError`, pthread mutexes, and `XrdOucStream`.

Integration points: global meter is used by node command handlers and cluster state reporting. It also implements `XrdCmsPerfMon` so plugins can feed performance data.

Risks: many fields are manually synchronized with `cfsMutex` and `repMutex`; callers must avoid lock inversions. The class assumes singleton lifetime. Virtual FS state changes require `setVirtUpdt()` to refresh cached cluster space.

Test signals: API compile tests, concurrent `Report()`/`PutInfo()`/`FreeSpace()` stress, virtual FS mode behavior, and monitor lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsMeter.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNash.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNash.cc

Purpose: implements the physical hash table used by the CMS cache to map `XrdCmsKey` path keys to pooled `XrdCmsKeyItem` entries.

Important APIs/types/functions: constructor, `Add()`, `Expand()`, `Find()`, and `Recycle()`. `LoadMax` is 80 percent.

Control flow: construction allocates a zeroed table with a configured Fibonacci pair of previous/current sizes and threshold. `Add()` allocates a key item, expands if the load threshold is exceeded, ensures the key has a hash, copies the key into the item, and prepends it in the hash bucket. `Expand()` allocates a new table whose size is previous plus current, redistributes all items by saved hash modulo new size, frees the old table, and recomputes the threshold. `Find()` computes hash if needed and walks the bucket by key equality. `Recycle()` expects an unloaded item with its original hash in `Loc.HashSave`, unlinks it from the corresponding bucket, recycles the item, and decrements the count.

State and persistence behavior: process-local table only. Table size grows but does not shrink. Entries are owned by `XrdCmsKeyItem` pool.

Dependencies: `XrdCmsNash.hh`, `XrdCmsKey`, C allocation/memset/free.

Integration points: used by `XrdCmsCache` as the fast physical map. It relies on `XrdCmsKeyItem::Alloc()` and `Recycle()` semantics.

Risks: constructor does not check `malloc()` before `memset()`. `Add()` increments `nashnum` before expansion; if expansion allocation fails the table continues at a higher load. No locking. `Recycle()` depends on prior `Unload()` storing `HashSave`; using it on a normal item can search the wrong bucket.

Test signals: add/find with collisions, expansion redistribution, allocation-failure handling, recycle after unload, table load threshold behavior, and cache-level concurrency serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNash.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNash.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNash.hh

Purpose: declares `XrdCmsNash`, the non-shrinking hash table for CMS cache key items.

Important APIs/types/functions: `Add(XrdCmsKey&)`, `Find(XrdCmsKey&)`, `Recycle(XrdCmsKeyItem*)`, constructor with previous/current Fibonacci sizes, private `Expand()`, table pointer, sizes, item count, and expansion threshold.

Control flow: the public API supports insert, lookup, and removal/recycle. Expansion is internal and based on `LoadMax`.

State and persistence behavior: owns the hash bucket array and count/threshold metadata for daemon lifetime. It does not own durable state.

Dependencies: `XrdCmsKey.hh`.

Integration points: embedded in `XrdCmsCache` and paired with `XrdCmsKeyItem` pool/tick unload logic.

Risks: no copy prevention, no locking, and destructor intentionally does nothing because normal usage does not delete the global cache. Constructor comments require caller to pass correct Fibonacci antecedents for desired growth behavior.

Test signals: header compile tests, constructor sizing tests, and integration with key item lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNash.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNode.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNode.cc

Purpose: implements the central CMS node command handler and node lifecycle object. A node represents a server, manager, peer, or supervisor connection and processes CMS protocol requests such as locate/select, have/gone, state, load/space, status, filesystem mutations, prepare, and disconnect.

Important APIs/types/functions: lifecycle `XrdCmsNode::{constructor,destructor,setName,Delete,Disc,SyncSpace}`, protocol handlers `do_Avail`, `do_Chmod`, `do_Disc`, `do_Gone`, `do_Have`, `do_Load`, `do_Locate`, `do_LocFmt`, `do_Mkdir`, `do_Mkpath`, `do_Mv`, `do_Ping`, `do_Pong`, `do_PrepAdd`, `do_PrepDel`, `do_Rm`, `do_Rmdir`, `do_SelAvoid`, `do_Select`, `do_SelPrep`, `do_Space`, `do_State`, `do_StateDFS`, `do_StateFWD`, `do_StatFS`, `do_Stats`, `do_Status`, `do_Trunc`, `do_Try`, `do_Update`, `do_Usage`, `Report_Usage`, and helpers `fsExec`, `fsFail`, `getMode`, `getSize`, `setHash`.

Control flow: construction binds a link/address/interface and assigns instance id/mask. Deletion marks `isGone`, waits under a global lock until `refCnt` drains, then deletes or logs a timeout. File notifications update `Cache` and optionally back-propagate to managers. Locate builds a `XrdCmsSelect`, calls `Cluster.Locate()`, formats selected servers through `do_LocFmt()`, or returns wait/error. Select maps request option bits into selection flags, handles affinity/packing/private-network/avoid-list behavior, calls `Cluster.Select()`, and replies with wait/error/redirect. State requests either query local baseFS or forward/broadcast through cache and cluster. Mutating operations call configured callouts or `Config.ossFS`. Prepare queues async `XrdCmsPrepArgs`, with `do_SelPrep()` doing cluster selection and scheduler delay. Usage/space handlers query `Meter` and send `load`/`avail`. Status toggles staging/service availability and updates `CmsState`.

State and persistence behavior: node state is volatile but cluster-critical: identity strings, network masks, online/bad/RW/staging flags, disk totals/free/utilization, config id, per-node load/mass/cost, ref counters, share counters, route slot, timezone, and manager pointer. Static `LastFree` tracks supervisor free-space changes for allocation reporting.

Dependencies: `XrdCmsCache`, `Cluster`, `baseFS`, `Config`, `Meter`, `PrepQ`, `CmsState`, `XrdCmsManager`, `XrdCmsSelect`, `XrdCmsRRQ`, `XrdOss`, `XrdOucPup`, `XrdOucProg`, `XrdOucCRC`, `XrdNetIF`, `XrdLink`, timers, and protocol definitions.

Integration points: `XrdCmsRouting.cc` maps CMS request codes directly to these handlers. `XrdCmsManager` stores manager nodes. `XrdCmsRRQ` uses `do_LocFmt()` for async locate replies. `XrdCmsProtocol` owns/executes node requests.

Risks: this file is a high-concurrency hub with mixed global, cluster, and node locks. Some load fields intentionally use single-writer relaxed updates. `do_Stats()` appears to refresh stats only when `statlast+9 >= now`, which is the reverse of the usual stale-cache test. `getSize()` rejects zero sizes, so truncating to zero may be impossible through this path. `do_SelAvoid()` mutates the avoid string in-place. Filesystem callouts depend on correct LFN-to-PFN translation. `Delete()` can leak node objects on reference stalls. Fixed response buffers bound locate/statfs/error payload size.

Test signals: routing table coverage for every handler, locate/select success/wait/error/redirect, DFS versus shared-nothing state handling, have/gone cache propagation, avoid-list retry limits and multi-source policy, filesystem callout/OSS mutation errors, prepare delay and co-location, status count updates, load/space reporting, delete ref drain behavior, and sanitizer tests for lock/ref races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNode.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNode.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNode.hh

Purpose: declares `XrdCmsNode`, the core per-connection/per-server state object and CMS request handler surface.

Important APIs/types/functions: public state flags for offline/bad/RW/staging/manager/peer/bound/known/connected/gone, disk/config fields, all `do_*` protocol handlers, lock/ref helpers, identity/network helpers, send wrappers, manager assignment, share/timezone/version/slot setters, `SyncSpace()`, static bad/RW bit constants, and private lifecycle/filesystem/hash helpers.

Control flow: protocol dispatch invokes `do_*` methods. Cluster selection and manager code use lock/ref helpers to move between global and node locks safely. Send wrappers guard against offline links.

State and persistence behavior: node objects hold process-memory cluster membership and selection state. `refCnt` protects lifetime; `NodeMask` identifies the node in server masks. No durable persistence, but state is continuously propagated by CMS messages.

Dependencies: `XrdLink`, `YProtocol.hh`, `XrdCmsTypes`, `XrdCmsRRQ`, `XrdNetIF`, `XrdNetAddr`, pthread primitives, and atomics. Many implementation dependencies are forward-declared.

Integration points: used by cluster, manager, protocol, routing, request queue, prepare, and cache subsystems. The header is one of the main internal contracts for CMS behavior.

Risks: many public mutable fields make invariants easy to violate outside the class. Lock helpers require callers to hold the documented global lock. Raw identity strings are manually owned. The class is not copy-safe and assumes pointer identity.

Test signals: compile/API dispatch coverage, lock/ref transition tests, identity matching tests, send-offline behavior, state flag transition tests, and integration with routing/cluster selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNode.hh -->
