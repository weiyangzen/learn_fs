# subset-b-007913 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLink.cc -->
## sources/distributed-fs/xrootd/src/Xrd/XrdLink.cc

Purpose: implements the public `XrdLink` facade used by protocols and pollers to operate a client connection without exposing the full `XrdLinkXeq` implementation. Most methods are small delegates, but this file owns TLS/non-TLS dispatch, reference-count coordination, link serialization, termination arbitration, and low-level readiness checks.

Important APIs/types/functions: `Activate()` attaches `linkXQ.PollInfo` to `XrdPoll`; `Recv`, `RecvAll`, `Peek`, and `Send` select TLS or raw executor methods based on `isTLS`; `setProtocol()` installs a protocol and optionally invokes `DoIt()`; `Serialize()` waits for `InUse <= 1`; `setRef()` updates `XrdLinkInfo::InUse` and releases serialization waiters; `Terminate()` implements owner-checked remote termination; `Stats()` delegates to `XrdLinkXeq::Stats`.

Control flow: accepted links are allocated by `XrdLinkCtl`, assigned a protocol by `XrdProtLoad` or the main acceptor, then `Activate()` places them into a poller. Poll callbacks run the protocol through `DoIt()` in `XrdLinkXeq`; public reads and writes return through this facade. Termination first resolves a target fd/instance, checks owner and host identity, then runs in the target link context to disable polling and wait for close notification.

State/persistence: no durable persistence. Runtime state is held in `HostName`, `Instance`, `isBridged`, `isTLS`, `ID`, and executor-owned `LinkInfo`/statistics. `ResetLink()` frees the host name and clears transient flags before fd reuse.

Dependencies/integration: depends on `XrdLinkXeq`, `XrdLinkCtl`, `XrdPoll`, `XrdProtocol`, `XrdTlsContext`, `XrdTlsPeerCerts`, and global logging/tracing. It is the stable API consumed by protocol implementations.

Risks: `setRef()` repairs zero or negative use counts after logging, which can hide upstream lifecycle bugs. `Terminate()` relies on caller-supplied `owner`, `ID`, host comparison, fd, and instance checks; regressions here could kill the wrong reused fd. `Wait4Data()` and raw `Peek()` must not be used incorrectly on TLS links.

Test signals: exercise protocol processing over TLS and non-TLS links, fd reuse with mismatched `Instance`, owner-denied termination, deferred close with active users, and XML link stats after `syncStats()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLink.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLink.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdLink.hh

Purpose: declares the public connection object for XRootD protocol code. `XrdLink` inherits `XrdJob` so links can be scheduled, but it presents a connection-centric API for address identity, I/O, TLS, protocol binding, statistics, and administrative termination.

Important APIs/types/functions: exported methods include `Activate`, `Close`, `Enable`, `Find`, `getName`, `Recv`, `RecvAll`, `Send`, `Serialize`, `setID`, `setProtocol`, `setTLS`, `Shutdown`, `Stats`, `Terminate`, and identity accessors such as `Host`, `Name`, `NetAddr`, `FDnum`, `Inst`, `UseCnt`, and `hasTLS`. `sfVec` aliases `XrdOucSFVec` for sendfile vectors, and static `sfOK` advertises sendfile support.

Control flow: callers receive `XrdLink*` from network accept or link lookup, then interact with it through this facade. Protocols call `Recv`/`Send` during `Process()`, may upgrade with `setTLS()`, can switch protocol objects with `setProtocol()`, and can close or terminate links. Static scans route to `XrdLinkCtl`.

State/persistence: exposes public `ID` for fast protocol/log access and stores protected identity/lifecycle fields `HostName`, `Instance`, `isBridged`, and `isTLS`. Persistent storage is absent; link objects are reused in memory and `ResetLink()` prepares them for new connections.

Dependencies/integration: includes network address types, scheduler job base class, sendfile vector support, pthread wrappers, `XrdLinkXeq`, `XrdPollInfo`, `XrdProtocol`, and TLS types.

Risks: the public `ID` pointer is intentionally mutable legacy state and must remain valid across protocol logging. The destructor is protected and link objects are "never deleted", so allocation/reuse invariants in `XrdLinkCtl` are essential. API comments define blocking behavior; incorrect timeout expectations can deadlock protocol code.

Test signals: compile-time consumers should cover raw I/O, vectored I/O, sendfile gated by `sfOK`, TLS upgrade/downgrade, static link iteration, and protocol replacement with `push=true`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLink.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkCtl.cc -->
## sources/distributed-fs/xrootd/src/Xrd/XrdLinkCtl.cc

Purpose: manages the global fd-indexed table of reusable link objects, allocates links for accepted sockets, scans active links, schedules idle timeouts, and reconciles aggregate link statistics.

Important APIs/types/functions: `Alloc()` validates the accepted fd, lazily allocates blocks of `XrdLinkCtl` objects, assigns a monotonically increasing `Instance`, initializes host/client identity, fd state, read-lock/non-close options, and link counters. `Find()` and `getName()` iterate active table slots with optional `XrdLinkMatch`. `idleScan()` disables idle enabled links. `Setup()` creates `LinkTab`/`LinkBat` and schedules `LinkScan`. `Unhook()` marks an fd free. `RegisterCloseRequestCb()` forwards callback registration to `XrdLinkXeq`.

Control flow: configuration calls `Setup(maxfds, idlewait)`. The network layer accepts a socket and calls `Alloc(peer, opts)`. Polling uses `LinkTab`/`LinkBat` for fd lookup and close paths call `Unhook()` before fd close. If idle scanning is configured, `LinkScan::DoIt()` repeatedly schedules itself through `XrdScheduler`.

State/persistence: maintains process-global `LinkTab`, `LinkBat`, `LTLast`, `maxFD`, `myInstance`, kill wait constants, and idle scan intervals. Link objects are never freed during normal operation; slots are marked free for reuse.

Dependencies/integration: integrates with `XrdInet` for hostname trimming, `XrdScheduler` for idle scan jobs, `XrdPoll` for disabling timed-out links, `XrdLinkXeq` statistics, and global logging/tracing.

Risks: fd table size must match configured connection limits; out-of-range or reused fds are rejected. `Find()` increments a link reference after releasing `LTMutex` and validates `Instance`, which is the main protection against fd reuse races. `idleScan()` increments a signed `char isIdle`; long intervals or unexpected overflow would affect idle detection.

Test signals: test fd allocation/reuse, table block allocation boundaries, instance mismatch during concurrent close/find, idle timeout disabling, `XRDLINK_RDLOCK` and `XRDLINK_NOCLOSE` options, and `LTLast` shrink after unhooking the highest fd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkCtl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkCtl.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdLinkCtl.hh

Purpose: declares the static control plane for `XrdLink` lifecycle management. The class is a protected subclass of `XrdLinkXeq`, allowing allocated table entries to be used as public `XrdLink` objects while exposing only static management APIs.

Important APIs/types/functions: `Alloc()` creates/reuses a link for an accepted peer. `fd2link()` and `fd2PollInfo()` translate active fds to runtime objects. `Find()` and `getName()` scan active links. `idleScan()`, `setKWT()`, `Setup()`, `SyncAll()`, and `Unhook()` manage runtime maintenance. `RegisterCloseRequestCb()` allows a protocol to intercept self-close requests. `XRDLINK_RDLOCK` and `XRDLINK_NOCLOSE` tune read serialization and fd ownership.

Control flow: setup initializes tables before network accepts. Accept paths allocate links, pollers use `fd2PollInfo`, protocols/admin tools use `Find`, and close paths call `Unhook`.

State/persistence: declares static table state: `LTMutex`, `LinkTab`, `LinkBat`, `LinkAlloc`, `LTLast`, `maxFD`, and kill timing constants. State is memory-only and process-wide.

Dependencies/integration: depends on `XrdLinkXeq`, `XrdSysPthread`, and `XrdLinkMatch`; it is tightly coupled to the executor object layout because table entries are actual `XrdLinkCtl` instances.

Risks: inheritance and casts depend on stable class layout. Inline fd lookup accepts negative fds by taking absolute value; callers must avoid passing sentinel negatives that should not resolve. `LinkBat` is the authoritative active flag, so every close path must call `Unhook()`.

Test signals: compile and runtime tests should validate fd lookup, fd+instance lookup, poll info lookup, close callback registration failure for null links, and kill wait configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkCtl.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkInfo.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdLinkInfo.hh

Purpose: defines the small mutable state bundle used to coordinate link closure, serialization, error reporting, and per-link lifecycle fields.

Important APIs/types/functions: `XrdLinkInfo` contains `KillcvP`, `IOSemaphore`, `conTime`, `Etext`, recursive `opMutex`, `InUse`, `doPost`, `FD`, and `KillCnt`. `Reset()` initializes connection time, clears error text, sets `InUse` to one, clears waiters, and marks the fd invalid.

Control flow: `XrdLinkXeq::Reset()` calls `LinkInfo.Reset()` for reused objects. `XrdLink::Serialize()`, `setRef()`, `Terminate()`, and `XrdLinkXeq::Close()` coordinate through `opMutex`, `InUse`, `doPost`, `IOSemaphore`, and `KillcvP`.

State/persistence: memory-only connection state. `Etext` is heap-owned and freed on reset or close. `conTime` is sampled with `time(0)` and later contributes to aggregate connection-time stats.

Dependencies/integration: depends on `XrdSysCondVar`, `XrdSysSemaphore`, and `XrdSysRecMutex`.

Risks: `KillcvP` is protected by `opMutex`, but the pointed condvar has its own lock ordering requirements. Misordered locking can deadlock termination. `KillCnt` is a `char`; masking in `XrdLink.cc` assumes narrow counter semantics.

Test signals: verify reset frees prior `Etext`, close signals `KillcvP`, serialization posts `IOSemaphore`, and connection duration is reflected in stats on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkMatch.cc -->
## sources/distributed-fs/xrootd/src/Xrd/XrdLinkMatch.cc

Purpose: implements parsing and matching for user/host target patterns used when scanning or terminating links.

Important APIs/types/functions: `Set(target)` parses target strings of the form `[user][*][@[host-prefix][*][host-suffix]]` into buffer-backed user and host components. `Match(uname, unlen, hname, hnlen)` checks optional username prefix, exact host, host prefix, and host suffix matches.

Control flow: callers construct or reset an `XrdLinkMatch`, then `XrdLinkCtl::Find()` and `getName()` call `Match()` for each active link's `ID` and `HostName`. A null, empty, or `"*"` target clears all filters and matches everything.

State/persistence: parsed target state is held in an internal fixed `Buff[256]` plus pointers into that buffer. There is no allocation and no durable persistence.

Dependencies/integration: uses `XrdSysPlatform` for `strlcpy` portability and is consumed by link control scans.

Risks: suffix parsing and suffix matching look suspicious: after replacing `*` with `'\0'`, `Set()` calls `strlen(theast)`, which will always be zero; `Match()` compares the host suffix pointer to `hname` rather than to `HnameR`. These paths should be tested before relying on suffix wildcards. `strlcpy(Buff, target, sizeof(Buff)-1)` leaves one byte unused and silently truncates long targets.

Test signals: unit cases should cover `*`, user-only, `user*`, host exact, `user@host`, `@prefix*`, `@*suffix`, and combined prefix/suffix patterns, including long target truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkMatch.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkMatch.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdLinkMatch.hh

Purpose: declares `XrdLinkMatch`, the lightweight matcher used to select active links by client user and host pattern.

Important APIs/types/functions: public `Set()` parses a target expression, and `Match()` has overloads for host strings with explicit or inferred length. Private fields include `Buff`, `Uname`, `HnameL`, `HnameR`, and their lengths.

Control flow: management code creates the matcher from administrative criteria, then passes it into `XrdLink::Find()` or `XrdLink::getName()` for repeated scans.

State/persistence: all parsed data is stored in-place in `Buff`; pointers are invalidated by a later `Set()` call but remain valid for the object lifetime otherwise.

Dependencies/integration: only depends on C string functions and integrates with `XrdLinkCtl`.

Risks: fixed buffer size constrains pattern length. The class is not synchronized; callers must not call `Set()` while another thread is using `Match()` on the same object.

Test signals: compile users should verify both overloads, reset-to-match-all behavior, and match failures for short usernames or hostnames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkMatch.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkXeq.cc -->
## sources/distributed-fs/xrootd/src/Xrd/XrdLinkXeq.cc

Purpose: implements the concrete link executor: protocol dispatch, blocking and nonblocking output, raw and TLS reads/writes, sendfile fast paths, close/recycle semantics, identity updates, and aggregate link statistics.

Important APIs/types/functions: `Reset()` initializes reusable objects; `Close()` tears down send queues, waits for use count serialization, recycles protocols, detaches from polling, unhooks fd table entries, reports TCP monitoring, and closes the fd unless kept. `DoIt()` runs `Protocol->Process()` until scheduler stickiness ends and reenables or closes the link. `Recv`, `RecvAll`, `Send`, `SendIOV`, and `Send(sfVec)` implement raw I/O. `setNB()` creates `XrdSendQ` on Linux. `setTLS()` initializes and accepts TLS. TLS methods wrap `XrdTlsSocket`. `syncStats()` transfers local counters to globals.

Control flow: accepted links start with a loader protocol. Once matched and activated, poll events schedule `DoIt()`. Protocol return codes control whether the link is reenabled, left disabled for `-EINPROGRESS`, or closed. Close paths serialize users, notify terminators, detach from pollers, unhook the fd table, and recycle protocol objects.

State/persistence: per-link counters accumulate in atomics until `syncStats()`. Global counters track active, max, total, bytes, timeouts, stalls, connection time, and sendfile interruptions. TLS state lives in `tlsIO`; optional `sendQ` owns queued writes.

Dependencies/integration: integrates with `XrdLinkCtl`, `XrdPoll`, `XrdScheduler`, `XrdSendQ`, `XrdTcpMonPin`, `XrdTls`, global `tlsCtx`, `devNull`, logging, and protocol plugins.

Risks: lock ordering is delicate across `opMutex`, `rdMutex`, `wrMutex`, and `statsMutex`. `TLS_Send(sfVec)` appears to add each file segment size to `totamt` before the loop and then adds `retc` again, risking overcounted return/stat values. Linux sendfile corking returns early on errors without uncorking because close is expected; reuse assumptions must hold. Deferred close with negative `LinkInfo.FD` must avoid fd reuse races.

Test signals: integration tests should cover protocol return codes, close callback veto, deferred close with queued sends, raw/TLS partial reads, vector limits above `maxIOV`, sendfile on Linux and TLS fallback, stats synchronization, and TCP monitor notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkXeq.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkXeq.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdLinkXeq.hh

Purpose: declares the protected implementation behind `XrdLink`. It inherits from `XrdLink` and exposes executor operations to `XrdLinkCtl` while keeping protocol-facing callers on the facade.

Important APIs/types/functions: public executor methods mirror link operations plus TLS-specific methods. Public members `LinkInfo` and `PollInfo` are the embedded lifecycle and poll state. Protected helpers include `RecvIOV`, `sendData`, `SendIOV`, `SFError`, `TLS_Error`, and `TLS_Write`. Static counters back link XML stats.

Control flow: `XrdLinkCtl` allocates concrete `XrdLinkXeq`/`XrdLinkCtl` objects, `XrdLink` delegates to these methods, and pollers schedule the inherited job interface.

State/persistence: stores protocol pointers (`Protocol`, `ProtoAlt`), close callback, TLS socket, network address, read/write mutexes, optional `sendQ`, host length, read-lock/fd-keep flags, idle marker, and fixed username/link-name buffers. No durable persistence.

Dependencies/integration: includes `XrdLink`, `XrdLinkInfo`, `XrdPollInfo`, `XrdProtocol`, `XrdNetAddr`, `XrdTls`, and `XrdTlsSocket`.

Risks: `Uname` and `Lname` adjacency is documented as required for client name formatting; layout changes could break `Client()`. The destructor is intentionally unused, so member resources must be reset/recycled manually. Exposing `LinkInfo` and `PollInfo` publicly makes invariants dependent on cooperating classes.

Test signals: ABI-sensitive tests should cover `Client()` formatting, link reset, protocol push/pop behavior, TLS version reporting, and close callback registration only for the active protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdLinkXeq.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMain.cc -->
## sources/distributed-fs/xrootd/src/Xrd/XrdMain.cc

Purpose: provides the xrootd server entry point, early process setup, configuration, listener thread creation, and accept-loop scheduling.

Important APIs/types/functions: local class `XrdMain` is an `XrdJob` whose `DoIt()` accepts a connection and assigns the protocol loader. `mainAccept()` creates an `XrdProtLoad` for a port and continuously schedules accept jobs, waiting on a semaphore after each accept. `mainAdmin()` contains placeholder admin accept handling. `main()` sets timezone/signal/thread defaults, configures the server, starts admin and extra port accept threads, and runs the primary accept loop.

Control flow: process startup blocks signals, lowers default stack size, calls `XrdConfig::Configure`, then spawns one accept thread per configured network beyond the first. Each accept job calls `XrdInet::Accept()`; accepted links receive `XrdProtLoad` and immediately run `setProtocol(..., true)`.

State/persistence: startup state is in `XrdMain::Config` and per-thread `XrdMain` instances. No persistent storage is written here.

Dependencies/integration: integrates with `XrdConfig`, `XrdInet`, `XrdLink`, `XrdProtLoad`, `XrdScheduler`, `XrdSysThread`, and `XrdSysUtils`.

Risks: `mainAccept()` constructs `XrdProtLoad ProtSelect` on the accept thread stack and stores its address in `Parms->theProt`; this is valid only because the function loops forever. Admin handling is explicitly superfluous and uses an `int` cast as protocol placeholder, so enabling it without real implementation would be unsafe. The process exits with `_exit()` on configuration/thread failures.

Test signals: server smoke tests should verify config parsing, multi-port accept startup, TLS and non-TLS protocol matching per port, signal blocking, and behavior when admin network is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMain.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMonRoll.cc -->
## sources/distributed-fs/xrootd/src/Xrd/XrdMonRoll.cc

Purpose: implements the small registration facade for monitor roll-up counter sets.

Important APIs/types/functions: static `EOV` terminates deprecated `setMember` arrays. The constructor stores a reference to `XrdMonitor` and clears reserved pointers. `Register(rollType, setName, vector<Item>&)` forwards the vector backing array to `XrdMonitor::Register`. Deprecated `Register(..., setMember[])` converts legacy atomic counter arrays into a heap-allocated `std::vector<Item>` and registers that.

Control flow: plugins or addons create static item vectors or legacy arrays, then call `XrdMonRoll::Register()`. Successful registration leaves item storage available for later formatting by `XrdMonitor`.

State/persistence: no durable persistence. For deprecated arrays, a vector is intentionally leaked on successful registration so the `Item` backing storage remains alive for process lifetime.

Dependencies/integration: depends on `XrdMonitor` for validation and formatting, and on `XrdMonRoll.hh` item definitions.

Risks: vector-based registration requires the caller's vector storage to remain valid until process exit; stack vectors would leave dangling `iVec` pointers. Legacy conversion leaks on success by design but deletes on failure.

Test signals: register vector and legacy sets, verify duplicate names fail in `XrdMonitor`, and ensure formatted output can still read registered items after the registration call returns for static vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMonRoll.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMonRoll.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdMonRoll.hh

Purpose: defines the public API for registering addon/plugin counter sets that are included in summary statistics emitted by `xrootd.report`.

Important APIs/types/functions: nested `Item` represents numeric, text, mutex, or schema tokens. `Schema` marks array/object begin and end. `Family` and `Trait` classify values for `XrdMonitor`. Constructors accept float, double, char text, string, schema, mutex lock/unlock markers, native `RAtomic` values, and bit-width `RAtomic` values. `rollType` maps deprecated `Misc`/`Protocol` to `AddOn`/`Plugin`. `Register()` overloads support modern `std::vector<Item>` and deprecated `setMember` arrays.

Control flow: a component defines an item list describing JSON/XML shape and variable references, then registers it through an `XrdMonRoll` instance. `XrdMonitor` later validates and formats the list.

State/persistence: item objects hold pointers or references to live variables; the item vector must outlive monitoring. `EOV` is the sentinel for legacy arrays. No data is persisted beyond process memory.

Dependencies/integration: depends on `XrdSysRAtomic` and `XrdMonitor`.

Risks: pointer lifetime is the main hazard. Text values are emitted without escaping in the formatter, so arbitrary strings containing JSON/XML metacharacters can produce invalid output. Mutex items allow monitor formatting to lock component state, but incorrect lock/unlock ordering is rejected only at registration validation.

Test signals: validate nested arrays/objects, mutex lock pairs, all atomic variants, text/string output, deprecated registration, duplicate set rejection, and XML tag defaults for array items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMonRoll.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMonitor.cc -->
## sources/distributed-fs/xrootd/src/Xrd/XrdMonitor.cc

Purpose: validates registered monitor roll-up descriptions and formats registered addon/plugin counter sets as JSON or XML.

Important APIs/types/functions: `RegInfo` stores set metadata, headers, templates, and item pointers. `Register()` maps roll types, rejects bad/duplicate sets, validates item syntax, builds JSON/XML headers, and stores the registry. `Format()` emits by index or set name. `FormJSON()` and `FormXML()` walk item vectors, handling schema and mutex items. `V2S()` formats atomics/floats/doubles, `V2T()` formats text, and `Validate()` checks keys, schema nesting, and mutex lock pairing.

Control flow: registration happens during component initialization. Reporting calls `Format()` repeatedly with an item cursor or a named set; only sets matching requested plugin/addon flags are emitted. Formatting directly reads the registered variable pointers.

State/persistence: `regVec` owns `RegInfo` objects for process lifetime. Each `RegInfo` references item vectors owned externally or intentionally leaked by legacy conversion.

Dependencies/integration: uses global `XrdSysError Log`, `XrdSysMutex`, standard containers, and `XrdMonRoll::Item`.

Risks: `Register()` assigns `regInfo->eTmplt = strdup(buff)` before `buff` is initialized for that purpose and leaks the constructor-created template; this likely corrupts later validation messages after successful registration. JSON/XML text is not escaped. `FormJSON()` resets comma anchor inside nested containers in a simplistic way; complex nested schemas need coverage. Formatting can deadlock if registered mutex items conflict with locks held by the reporting path.

Test signals: unit tests should cover invalid schemas, unbalanced mutex markers, duplicate sets, named and cursor formatting, buffer-too-small returns, text escaping expectations, and nested JSON/XML arrays and objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMonitor.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdMonitor.hh

Purpose: declares the monitor registry and formatter that backs `XrdMonRoll` summary statistics.

Important APIs/types/functions: `Mopts` combines format and set filters: `F_JSON`, `X_PLUG`, and `X_ADON`. Public `Format()` overloads format by cursor or set name. `Register()` accepts a roll type, set name, item array, and item count. Private `RegInfo` stores headers, template, type, count, and item vector pointer. Private helpers validate and format values.

Control flow: `XrdMonRoll` calls `Register()`, then the report machinery calls `Format()` to serialize selected sets in JSON or XML form.

State/persistence: `regVec` holds registered sets for the life of the monitor. `Registered()` reports whether any set has been registered.

Dependencies/integration: includes `XrdMonRoll.hh` and standard containers. It is not internally synchronized around `regVec`, implying registration should occur during configuration before concurrent reporting.

Risks: lack of registry locking makes concurrent register/format unsafe. `RegInfo` destructor frees metadata but not item storage, so ownership must remain external. Output format flags are bit masks; passing `F_JSON` without `X_PLUG` or `X_ADON` will skip all sets in cursor formatting.

Test signals: compile tests for option combinations, registration lifetime, cursor advancement across filtered sets, and named-set lookup across plugin/addon categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdMonitor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdObject.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdObject.hh

Purpose: provides generic singly linked queue templates used by XRootD package objects. Queues can push at the front, pop from the front, and optionally age out queued objects through scheduler jobs implemented in `XrdObject.icc`.

Important APIs/types/functions: `XrdObject<T>` wraps an item pointer, next pointer, and queue timestamp. `XrdObjectQ<T>` inherits `XrdJob` and provides `Pop()`, `Push()`, `Set(inQMax, agemax)`, scheduler/trace `Set()`, and `DoIt()`. Queue limits use `MaxinQ`, `MininQ`, and `Maxage`.

Control flow: producers allocate `XrdObject<T>` nodes and `Push()` them. If the queue is above `MaxinQ`, pushed item payloads are deleted. Consumers call `Pop()` to retrieve payload pointers. Time-managed cleanup is configured through `Set()` and runs as a scheduled job.

State/persistence: queue state is memory-only: `First`, `Count`, current age, size limits, scheduler pointer, trace pointer, and trace flag. Payload ownership transfers to queue on push.

Dependencies/integration: depends on `XrdJob`, `XrdSysMutex`, `XrdScheduler`, `XrdSysTrace`, and the inline implementation file `XrdObject.icc`.

Risks: overflow behavior deletes `Node->Item` but not obviously the node in the inline `Push()` body shown here, so callers must understand ownership. The queue is LIFO despite comments about adding to either end; details may be in `XrdObject.icc`. Cleanup requires `Set()` at least once.

Test signals: test push/pop ordering, max queue deletion behavior, scheduled age cleanup, trace integration, and empty pop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdObject.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPoll.cc -->
## sources/distributed-fs/xrootd/src/Xrd/XrdPoll.cc

Purpose: implements common poller infrastructure and selects the platform poll backend. It starts poller threads, balances link attachment, detaches links, formats poll stats, and defines termination protocol behavior.

Important APIs/types/functions: `XrdPoll` constructor creates a command pipe. `Attach()` chooses the poller with the fewest attached fds and calls backend `Include()`. `Detach()` calls backend `Exclude()` and decrements counters. `Finish()` swaps in a local `XrdPoll_End` protocol and records error text. `getRequest()` reads backend commands from the pipe. `Setup()` creates `XRD_NUMPOLLERS` pollers and starts threads. `Stats()` emits XML counters.

Control flow: configuration calls `Setup(numfd)`. `XrdLink::Activate()` calls `Attach()`. Backends receive fd events and schedule link jobs. `Disable()`/`Enable()` are backend-specific. On fatal events `Finish()` marks a link for termination before scheduling close behavior.

State/persistence: static `Pollers[3]`, `doingAttach`, per-poller pipe fds, attached/enabled/event/interrupt counters, and pipe read buffer state. No durable persistence.

Dependencies/integration: uses `XrdPollE` on Linux and `XrdPollPoll` elsewhere, plus `XrdLink`, `XrdProtocol`, `XrdScheduler`, `XrdSysFD`, and logging/tracing.

Risks: `Setup()` reuses one stack `XrdPollArg` per poller thread and relies on semaphore synchronization before the next iteration mutates it. `Poll2Text()` returns heap strings, so callers must handle ownership if needed. `Attach()` assumes all `Pollers` are initialized.

Test signals: run with Linux epoll and non-Linux poll backends, attach balancing across three pollers, detach underflow detection, termination idempotence, partial command pipe reads, and stats formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPoll.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPoll.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdPoll.hh

Purpose: declares the abstract poller interface and common state for event backends that drive active links.

Important APIs/types/functions: static APIs `Attach`, `Detach`, `Finish`, `Poll2Text`, `Setup`, and `Stats` provide backend-independent operations. Virtual APIs `Disable`, `Enable`, `Start`, `Exclude`, and `Include` are implemented by `XrdPollE` or `XrdPollPoll`. `PipeData` encodes command-pipe requests (`EnFD`, `DiFD`, `RmFD`, `Post`).

Control flow: link activation attaches `XrdPollInfo` to a backend. Backends wait for fd readiness and command-pipe requests, disable links while work is scheduled, and reenable links after protocol processing succeeds.

State/persistence: each poller stores thread identity, command/request pipe fds, pipe buffers, attached counts, and event counters. Static `Pollers` holds the active backend objects.

Dependencies/integration: depends on POSIX `pollfd`, pthreads, `XrdSysSemaphore`, and `XrdPollInfo`.

Risks: subclass correctness depends on honoring command-pipe semantics and maintaining `numEnabled`, `numEvents`, and `numInterrupts`. `XRD_NUMPOLLERS` is fixed at three; scaling changes require reviewing attachment balancing and stats sizing.

Test signals: backend conformance tests should verify include/exclude, enable/disable, pipe posts, thread startup synchronization, and stats length when called with null buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPoll.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPollE.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdPollE.hh

Purpose: declares the Linux epoll-backed `XrdPoll` implementation.

Important APIs/types/functions: public overrides `Disable`, `Enable`, and `Start` implement event masking and poller thread execution. Protected `Exclude` and `Include` manipulate epoll membership. Private helpers `AddWaitFd`, `HandleWaitFd`, `remFD`, and `Wait4Poller` coordinate fd removal and poll-loop quiescence. `x2Text()` formats epoll event flags.

Control flow: `XrdPoll::newPoller()` constructs `XrdPollE` with an epoll event table, epoll descriptor, and wait fd. `Start()` runs the event loop. Enable/disable and include/exclude are invoked by common link and poll control paths.

State/persistence: stores epoll event table, epoll descriptor, table capacity, wait fd, and two semaphores used to prove an `epoll_wait` loop has completed before link reset can reuse `XrdPollInfo`.

Dependencies/integration: Linux-only `<sys/epoll.h>`, common `XrdPoll`, and `XrdPollInfo`.

Risks: the header explicitly documents a use-after-reset protection mechanism around `WaitFdSem`/`WaitFdSem2`; backend changes must preserve it. `EPOLLONESHOT` support is conditional, so behavior differs by platform headers.

Test signals: Linux integration tests should cover add/remove while events are pending, disable reason propagation, one-shot reenable, hangup/error events, and wait-fd synchronization during close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPollE.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPollInfo.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdPollInfo.hh

Purpose: defines the per-link poll attachment record shared between link objects and poll backends.

Important APIs/types/functions: fields include `Next` for poll queue chaining, immutable `Link` reference, backend `PollEnt`, owning `Poller`, fd number, `inQ`, `isEnabled`, and reserved flags. `Zorch()` resets the record to detached/disabled fd `-1`.

Control flow: `XrdLinkXeq` embeds `PollInfo`. `XrdLinkCtl::Alloc()` sets `FD`; `XrdLink::Activate()` attaches it to a poller; poll backends toggle `isEnabled` and queue state; close paths detach and reset state.

State/persistence: runtime-only attachment state. The `Link` reference is stable for the object lifetime.

Dependencies/integration: forward declares `XrdLink`, `XrdPoll`, and `pollfd`; used by every poll backend and link executor.

Risks: because `PollInfo` is embedded in reusable link objects, backends must not retain pointers after detach/reset. Queue flags must remain consistent to avoid double scheduling or missed events.

Test signals: attach/detach/reset tests should assert fd, poller, enabled, queue, and `PollEnt` transitions, especially under close while events are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPollInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPollPoll.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdPollPoll.hh

Purpose: declares the portable `poll(2)` backend for platforms that do not use the Linux epoll implementation.

Important APIs/types/functions: public overrides `Disable`, `Enable`, and `Start`; protected `doDetach`, `Exclude`, and `Include`; private helpers `doRequests`, `dqLink`, `LogEvent`, `Recover`, and `Restart`. State includes `PollTab`, active count `PollTNum`, pending `PollQ`, `PollMutex`, and `maxent`.

Control flow: the common `XrdPoll` layer attaches links through `Include()`. The backend event loop waits on the poll table and command pipe, queues ready links, disables them during processing, and recovers/restarts after poll errors.

State/persistence: runtime-only poll table and queued link state.

Dependencies/integration: POSIX `poll`, `XrdPoll`, `XrdPollInfo`, and mutex support through the included common header.

Risks: `class XrdPollPoll : XrdPoll` uses private inheritance by default, unlike the public epoll backend; construction through `newPoller()` may still work internally, but external substitutability is limited. Poll table compaction and queued `XrdPollInfo` pointers must avoid stale references after link close.

Test signals: non-Linux CI should cover include/exclude, recovery after `poll()` errors, command processing limits, queue dequeue behavior, and restart logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdPollPoll.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdProtLoad.cc -->
## sources/distributed-fs/xrootd/src/Xrd/XrdProtLoad.cc

Purpose: loads built-in or shared-library protocol implementations, maps protocols to ports, selects the matching protocol for a new link, handles optional TLS-first matching, and aggregates protocol statistics.

Important APIs/types/functions: static `Load()` obtains a protocol object and registers it. `Port()` overloads query or record protocol-port mappings. Constructor builds `myProt` for one listening port, inserting `-1` as a TLS negotiation marker before TLS protocols. `Process()` negotiates TLS when requested, calls each protocol's `Match()`, installs the matched protocol/name, activates the link, and processes the first request. `Statistics()` concatenates protocol stats. `getProtocol()` and `getProtocolPort()` resolve built-in or plugin entry points.

Control flow: configuration asks each protocol for its port, loads it, and maps it. Accept loops attach an `XrdProtLoad` instance to new links. The loader probes protocols in port order; on match it replaces itself with the real protocol and activates polling.

State/persistence: static arrays store up to eight protocol names/objects and plugin handles. `portVec` records port/protocol/TLS mappings. Loader instances keep a signed-char protocol sequence for their port.

Dependencies/integration: depends on `XrdOucPinLoader`, `XrdProtocol`, `XrdLink`, version checks, global logging, and TLS link upgrade support.

Risks: protocol index handling is one-based in `Load()`/`Port()` and zero-based in arrays; off-by-one regressions would misroute ports. `myProt` uses `signed char`, limiting sentinel/index values to the small `ProtoMax`. Failed TLS negotiation sets link error text and closes. Plugin symbol resolution must match `XrdgetProtocol` and optional `XrdgetProtocolPort`.

Test signals: load built-in and plugin protocols, duplicate/max protocol counts, port mapping for TLS and non-TLS on the same port, failed TLS negotiation, no-match close reason, first-request processing shortcut, and stats concatenation buffer accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdProtLoad.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdProtLoad.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdProtLoad.hh

Purpose: declares the protocol-loader `XrdProtocol` implementation that temporarily owns new links while deciding which real protocol should handle them.

Important APIs/types/functions: public static `Load`, `Port`, `Statistics`, constants `ProtoMax` and `PortoMax`, and protocol overrides `Match`, `Process`, `Recycle`, and `Stats`. Private static helpers resolve protocol objects and ports. Static arrays `ProtName`, `Protocol`, and `ProtoCnt` hold loaded protocols; instance fields `myPort` and `myProt` hold per-port selection order.

Control flow: `XrdMain` creates an `XrdProtLoad` for each accept port. `Process()` then performs protocol matching and handoff.

State/persistence: process-global protocol registry and per-loader port mapping sequence. No durable storage.

Dependencies/integration: extends `XrdProtocol` and depends on `XrdProtocol_Config` during configuration.

Risks: `PortoMax` is declared but not used in this file set; actual port vector growth is controlled elsewhere by `ProtoMax` and memory. `Match()` always returns null because this object is not itself a selectable protocol.

Test signals: compile plugin API users, validate loader construction with no mappings, TLS marker ordering, and `Statistics()` behavior when no protocols are loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdProtLoad.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdProtocol.hh -->
## sources/distributed-fs/xrootd/src/Xrd/XrdProtocol.hh

Purpose: defines the abstract protocol interface and configuration structure used by XRootD core to load, configure, match, run, recycle, and report protocol implementations.

Important APIs/types/functions: `XrdProtocol_Config` passes stable services (`eDest`, `NetTCP`, `BPool`, `Sched`, `Stats`, `theEnv`, `tlsCtx`, `totalCF`) and unstable configuration values that protocols must copy if retained. `XrdProtocol` derives from `XrdJob` and requires `Match(XrdLink*)`, `Process(XrdLink*)`, `Recycle(XrdLink*, int, const char*)`, and `Stats(char*, int, int)`. Comments define required `extern "C"` plugin entry points `XrdgetProtocol` and `XrdgetProtocolPort`.

Control flow: configuration creates a protocol object via the entry point. For each accepted link, the loader calls `Match()`; poll events call `Process()`; close calls `Recycle()`; report paths call `Stats()`.

State/persistence: the config object is transient except for documented stable pointers. Protocol implementations own their own persistent runtime state.

Dependencies/integration: includes `XrdJob` and forward-declares core services, network address types, scheduler, stats, TLS context, and environment objects.

Risks: the copy constructor is deleted to prevent accidental whole-object retention, but protocols can still store unstable pointers manually. ABI compatibility matters for shared-library plugins. `Stats()` snprintf semantics are part of the contract and must be honored for aggregation.

Test signals: plugin tests should verify port discovery, protocol construction, match failure/success, process return-code semantics with `XrdLinkXeq::DoIt()`, recycle reason propagation, and stats sizing with null buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdProtocol.hh -->
