# subset-b-007912 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/XProtocol.hh -->
# sources/distributed-fs/xrootd/src/XProtocol/XProtocol.hh

Purpose: defines the public XRoot binary wire protocol: protocol version constants, handshake layouts, all client request structures, all server response structures, feature flags, limits, response/error codes, and the small `XProtocol` utility class. It is a contract header shared by clients, servers, plugins, and external reimplementations, so layout stability and numeric compatibility are more important than local abstraction.

Important APIs/types/functions: `ClientInitHandShake`, `ServerInitHandShake`, `XRequestTypes`, `ClientRequestHdr`, request structs for auth/bind/chmod/checkpoint/clone/close/dirlist/endsess/fattr/gpfile/locate/login/mkdir/mv/open/pgread/pgwrite/ping/protocol/prepare/query/read/readv/rm/rmdir/set/sigver/stat/sync/truncate/write/writev, `ClientRequest`, `SecurityRequest`, `XResponseType`, `ServerResponseHeader`, all response body structs, `ServerResponse`, `ServerResponseV2`, and `XProtocol::{mapError,toErrno,errName,reqName}`. `XrdProto` holds newer extension structs/constants such as clone/readv/writev item layouts, page-read/write sizes, protocol security/bind response aliases, and `RespType`.

Control flow: this file has no runtime protocol parser. Its executable behavior is inline error translation: `mapError()` normalizes negative errno values, then maps POSIX errors to XRootD `kXR_*` response errors; `toErrno()` performs the reverse mapping and returns `ENOMSG` for unknown protocol errors. The rest of the file controls runtime behavior indirectly because dispatch tables and serializers elsewhere interpret `requestid`, `dlen`, option bits, and status codes according to these definitions.

State and persistence behavior: the header declares only wire state, not process-owned persistent state. State crosses the network in fixed-size headers plus variable payloads indicated by `dlen`. Persistent compatibility is encoded in constants such as `kXR_PROTOCOLVERSION`, TLS/signing/clone version gates, max vector sizes, page sizes, and request/response numeric fences.

Dependencies: depends on `XProtocol/XPtypes.hh` for fixed-width protocol aliases and `<cerrno>` for error mapping. It conditionally normalizes missing errno names on Windows or platforms missing `ENOATTR`, `EBADRQC`, or `EAUTH`.

Integration points: central to XRootD request decoding, response encoding, protocol negotiation, TLS and signing policy exchange, vector I/O, page checksummed I/O, file attributes, redirects, async responses, and status streaming. Any plugin or client that includes this file relies on exact numeric values and binary field ordering. `ALIGN_CHECK` intentionally enforces expected request/header sizes at compile time by making invalid layouts fail.

Risks: ABI/wire compatibility is the main risk. Changing struct fields, enum order, numeric constants, or alias sizes can break old clients or external implementations. The comments note network byte order but the structs do not enforce conversion, so callers must consistently marshal/unmarshal. Some response bodies include large fixed arrays as convenience buffers even when actual wire length is `dlen`, so consumers must validate lengths before copying. Error mappings are lossy and default many unknown errors to filesystem/server failures.

Test signals: compile-time size checks for request and response headers; protocol interoperability tests for login/protocol/open/read/write/readv/writev/page I/O/TLS/signing; round-trip tests for `mapError()`/`toErrno()` on supported errnos; fuzz/negative tests for `dlen`, vector limits, and status response lengths; compatibility tests against older protocol versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/XProtocol.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/XPtypes.hh -->
# sources/distributed-fs/xrootd/src/XProtocol/XPtypes.hh

Purpose: supplies the protocol integer and byte typedefs used by `XProtocol.hh` and `YProtocol.hh`. It exists to keep on-the-wire field sizes stable across historical C/C++ data models.

Important APIs/types/functions: `kXR_char`, `kXR_int16`, `kXR_unt16`, `kXR_int32`, `kXR_unt32`, `kXR_int64`, and `kXR_unt64`. It also defines compatibility probes `XR__INT16` and `XR__INT64` for LP32/ILP64-like environments.

Control flow: no functions. Preprocessor branches select a 32-bit signed/unsigned type based on detected platform model. Most normal platforms use `int`/`unsigned int` for 32-bit fields and `long long`/`unsigned long long` for 64-bit fields.

State and persistence behavior: all state is type-level. Persistence impact is high because these typedefs determine serialized XRootD and CMS protocol field widths.

Dependencies: no project includes beyond compiler/platform macros. It assumes platform types such as `int32`/`unsigned int32` exist in the ILP64 branch.

Integration points: every protocol struct in `XProtocol.hh` and `YProtocol.hh` is built from these aliases. Serialization, byte swapping, and protocol compatibility depend on these aliases matching the documented sizes.

Risks: unusual platform models may select rarely tested typedef paths. The header says only char and short are truly portable, but the protocol still depends on 32-bit and 64-bit aliases being exact. Any compiler where `int`, `long`, or `long long` widths differ from expectations can corrupt wire layouts.

Test signals: compile-time `sizeof` checks for all aliases; protocol struct size checks; cross-compilation sanity on LP32, LP64, and any supported ILP64 targets; serialization tests that compare known byte fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/XPtypes.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/YProtocol.hh -->
# sources/distributed-fs/xrootd/src/XProtocol/YProtocol.hh

Purpose: defines the XRootD CMS/manager-server "Y" protocol in namespace `XrdCms`. It provides common request/response headers, request codes, response codes, modifiers, error codes, login payload state, and per-operation request skeletons for cluster management, location, staging, load, filesystem state, and redirect coordination.

Important APIs/types/functions: `kYR_Version`, `CmsRRHdr`, `CmsReqCode`, `CmsFwdModifier`, `CmsReqModifier`, `CmsRspCode`, `YErrorCode`, `CmsResponse`, and request structs including `CmsAvailRequest`, `CmsChmodRequest`, `CmsDiscRequest`, `CmsGoneRequest`, `CmsHaveRequest`, `CmsLocateRequest`, `CmsLoginData`, `CmsLoginRequest`, `CmsLoginResponse`, `CmsLoadRequest`, `CmsMkdirRequest`, `CmsMkpathRequest`, `CmsMvRequest`, `CmsPingRequest`, `CmsPongRequest`, `CmsPrepAddRequest`, `CmsPrepDelRequest`, `CmsRmRequest`, `CmsRmdirRequest`, `CmsSelectRequest`, `CmsSpaceRequest`, `CmsStateRequest`, `CmsStatfsRequest`, `CmsStatsRequest`, `CmsStatusRequest`, `CmsTruncRequest`, `CmsTryRequest`, `CmsUpdateRequest`, and `CmsUsageRequest`.

Control flow: no executable code. Runtime CMS control flow is encoded in `rrCode`, `modifier`, `datalen`, and operation-specific option bits. Forwarding behavior is represented by high modifier bits (`kYR_hopcount` and `kYR_hopincr`), with comments naming which operations may be forwarded.

State and persistence behavior: request state is serialized into `CmsRRHdr` plus PUP/string-encoded variable data described in comments. `CmsLoginData` carries persistent cluster identity and capacity state: mode bits, hold time, total/free/min space, filesystem count/utilization, data/subscription ports, server ID, exported paths, interfaces, and environment CGI.

Dependencies: includes `XProtocol/XPtypes.hh`. Comments say binary values use network byte order and variable data is serialized as explained in `XrdOucPup`, so the concrete packing logic lives elsewhere.

Integration points: used by cmsd/managers/supervisors/data servers for namespace location, availability, staging preparation, file operation forwarding, load propagation, status control, and retry/selection decisions. Option bits mirror client-visible behavior such as IPv4/IPv6 preference, private networks, online-only selection, affinity, retry reason, and staging mode.

Risks: header comments say structures need packing for network use, but the structs are not explicitly annotated here; compatibility depends on field choices avoiding padding or being packed by surrounding serializers. Many variable fields are comments rather than C members, so encoder/decoder code must stay in sync with these documented layouts. Modifier bit overlap means new modifiers must preserve hop-count semantics.

Test signals: CMS interoperability tests for login, locate/select, have/gone, load, status, and forwarding; serializer tests for `CmsRRHdr` byte order and `CmsLoginData`; option-mask tests for retry reasons, IP-family return flags, and affinity; negative tests for malformed lengths and unknown request codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/YProtocol.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/Xrd/CMakeLists.txt

Purpose: declares the build membership for the core Xrd utility/server sources and the `xrootd` executable.

Important APIs/types/functions: not a C++ API, but it adds sources to `XrdUtils`, conditionally stops when `XRDCL_ONLY` is enabled, creates executable `xrootd` from `XrdConfig`, `XrdProtLoad`, `XrdStats`, and `XrdMain`, links runtime libraries, and installs the binary to `${CMAKE_INSTALL_BINDIR}`.

Control flow: CMake first appends many Xrd runtime sources to `XrdUtils`. If building client-only (`XRDCL_ONLY`), it returns before defining the server executable. Otherwise it defines and links `xrootd`.

State and persistence behavior: build-system state only. It controls which object files are linked into `XrdUtils` and whether the installed server binary exists.

Dependencies: depends on prior CMake definitions of `XrdUtils`, `XrdServer`, CMake install dirs, dynamic loader/thread/socket/extra libraries, and project option `XRDCL_ONLY`.

Integration points: integrates buffer, network, scheduler, poll, link, monitor, object, and trace code into `XrdUtils`; integrates daemon configuration and protocol loading into the executable. This file is the source of truth for whether changes in these `.cc`/`.hh` files are compiled into the server.

Risks: missing a source in `target_sources` can compile on some targets but fail link/runtime elsewhere. Header-only entries are useful for IDE visibility but not compilation. `XRDCL_ONLY` can hide server build failures in client-only CI lanes.

Test signals: configure/build both default and `XRDCL_ONLY`; verify `xrootd` links with `XrdServer`/`XrdUtils`; packaging/install tests check `${CMAKE_INSTALL_BINDIR}/xrootd`; CI should build server lanes after source-list changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.cc

Purpose: implements `XrdBuffXL`, the large-buffer extension pool used when requested buffers exceed the normal `XrdBuffManager` maximum. It caches power-of-two-aligned buffers from roughly 4 MiB up to a configurable cap, with a hard 1 GiB maximum.

Important APIs/types/functions: constructor, `Init(int maxMSZ)`, `Obtain(int sz)`, `Recalc(int sz)`, `Release(XrdBuffer*)`, `Stats(char*,int,int)`, and `Trim()`. Local constants define `maxBuffSz`, `iniBuffSz`, `minBuffSz`, `minBShift`, and `isBigBuff`.

Control flow: `Init()` resets any existing bucket vector, clamps the max size, rounds it to power-of-two bucket coverage, and allocates `BuckVec` slots. `Obtain()` validates size, maps it to a bucket index, pops an existing buffer under `slotXL`, or allocates page-aligned memory with `posix_memalign` and wraps it in `XrdBuffer` with the big-buffer marker in `bindex`. `Release()` pushes the buffer back to its bucket. `Trim()` frees excess cached buffers when free count exceeds recent requests, then resets per-bucket request counters.

State and persistence behavior: process-memory state only: bucket freelists, per-bucket buffer/request counts, total allocated bytes, total requests, total buffers, max size, and slot count. It intentionally is singleton-like and never deleted in normal operation.

Dependencies: uses `XrdBuffer`, `XrdSysMutex`, `XrdOucUtils::Log2`, page size from `getpagesize()`, `posix_memalign`, and standard allocation/free. It is referenced through `XrdGlobal::xlBuff` from `XrdBuffer.cc` and configured by `XrdConfig::xbuf`.

Integration points: `XrdBuffManager::Obtain()` delegates oversized requests to this pool; `XrdBuffManager::Release()` sends marked buffers back here; stats are embedded under normal buffer stats; reshape trims this pool after normal pool pressure handling.

Risks: all callers must release buffers to the correct manager; the `isBigBuff` marker protects this but depends on `bindex` integrity. `Init()` can delete and replace buckets without freeing buffers currently checked out or cached in old buckets, so reconfiguration timing matters. `Trim()` frees while holding the mutex, which can extend lock hold time for many large buffers.

Test signals: allocation/release tests across bucket boundaries and max-size rejection; `Recalc()` expected-size tests; stats tests after obtain/release/trim; concurrency stress for obtain/release; config tests for `buffers maxbsz`; memory-pressure tests that verify trim returns large buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.hh

Purpose: declares the large-buffer pool class used alongside `XrdBuffManager`.

Important APIs/types/functions: `XrdBuffXL::Init`, `Obtain`, `Recalc`, `Release`, `MaxSize`, `Trim`, `Stats`, constructor/destructor, private `BuckVec`, mutex `slotXL`, bucket vector, totals, page size, slots, max size, request count, and buffer count.

Control flow: the header exposes lifecycle/configuration, buffer acquisition/release, sizing, trimming, and stats methods. Actual bucket selection and memory allocation live in `XrdBuffXL.cc`.

State and persistence behavior: owns in-memory freelists and counters. No disk persistence. Destructor is intentionally empty because the global buffer manager is not expected to be deleted.

Dependencies: includes `XrdBuffer.hh` and `XrdSys/XrdSysPthread.hh` for `XrdSysMutex`. It grants no public direct bucket access.

Integration points: paired with `XrdBuffManager` and global `XrdGlobal::xlBuff`; configured by xrd `buffers maxbsz`; reported through buffer statistics; used for large read/write/vector I/O allocations.

Risks: class is designed as a singleton and is not copy-protected in the header. Consumers should not create multiple independent pools unless they understand memory accounting. `MaxSize()` is simple state, so callers must ensure `Init()` has run before relying on configured maximums.

Test signals: compile/link tests against `XrdBuffer`; API tests for max-size reporting before/after init; concurrent pool use tests through `XrdBuffManager`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.cc

Purpose: implements the normal server buffer pool, including fixed power-of-two buckets, aligned allocation, recycling, memory accounting, XML-like stats, and a background reshaper thread that trims cached buffers under memory pressure or periodic review.

Important APIs/types/functions: external thread entry `XrdReshaper`, `XrdBuffManager` constructor/destructor, `Init()`, `Obtain(int)`, `Recalc(int)`, `Release(XrdBuffer*)`, `Reshape()`, `Set(int,int)`, and `Stats(char*,int,int)`.

Control flow: `Init()` starts a reshaper thread. `Obtain()` rejects non-positive sizes, delegates oversized requests to `xlBuff`, computes a bucket by `Log2`, pops a cached buffer under the condition-variable lock, or allocates aligned memory and updates counters; if allocation pushes total memory over `maxalo`, it signals the reshaper. `Release()` returns normal buffers to bucket freelists and delegates large marked buffers to `xlBuff`. `Reshape()` loops forever, waiting on pressure or interval, computing a target profile from recent request counts, freeing surplus buffers from largest buckets down to an 80% target, resetting counters, and trimming `xlBuff`.

State and persistence behavior: process-memory-only cache. Persistent effects are indirect: buffer limits affect daemon throughput and memory footprint. State includes bucket freelists, counts, request history, total allocated bytes, target max allocation, reshape interval, reshape-in-progress flag, total adjustments, and global `XrdGlobal::xlBuff`.

Dependencies: `XrdOucUtils::Log2`, `XrdSysError`, `XrdSysThread`, `XrdSysCondVar`, `XrdSysTimer`, `XrdTrace`, `XrdBuffXL`, page size and `sysconf(_SC_PHYS_PAGES)`, `posix_memalign`.

Integration points: exported globally as `XrdGlobal::BuffPool` and passed into `XrdProtocol_Config`. Protocol implementations obtain transient I/O buffers through this manager. `XrdConfig::xbuf` changes memory/reshape settings, and `XrdStats` reports `Stats()`.

Risks: the reshaper thread never exits, matching daemon lifetime assumptions. Memory accounting can drift if external code tampers with `XrdBuffer` internals, though friendship limits access. `Obtain()` uses `posix_memalign` alignment of `mk` for sub-page buffers and page size otherwise; platform-specific allocation behavior matters. Under high churn, freeing buffers while reshaping can race only through the lock, so lock contention is the main performance risk.

Test signals: bucket sizing tests for `Obtain()`/`Recalc()`; release/reuse tests; oversized delegation tests to `XrdBuffXL`; stats formatting tests; reshape tests with low `maxalo`; stress tests with many threads; startup test ensuring reshaper thread creation failures are logged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.hh

Purpose: declares `XrdBuffer`, the memory wrapper handed to protocol/runtime code, and `XrdBuffManager`, the normal buffer pool.

Important APIs/types/functions: `XrdBuffer::{buff,bsize}`, constructor/destructor, private `bindex`/`next`, `XrdBuffManager::{Init,Obtain,Recalc,Release,MaxSize,Reshape,Set,Stats}`, constants `XRD_BUCKETS` and `XRD_BUSHIFT`, and private bucket/counter/state members.

Control flow: header exposes the pool contract: initialize background reshaping, obtain a buffer of at least requested size, calculate actual allocation size, release a buffer, reshape/retune memory limits, and emit stats. `XrdBuffer` frees owned memory in its destructor.

State and persistence behavior: buffers own heap memory, not persisted data. `buff` and `bsize` are public for fast I/O use, while `bindex` and freelist linkage are private to the buffer managers.

Dependencies: standard allocation/unistd/sys/types and `XrdSysPthread` for `XrdSysCondVar`. `XrdBuffManager` friends `XrdBuffer`; `XrdBuffXL` is a friend for large-buffer handling.

Integration points: central allocator used by `XrdProtocol_Config::BPool`, stats, protocol I/O, and buffer tuning directives. `XRD_BUCKETS`/`XRD_BUSHIFT` define the normal pool range and drive `XrdBuffXL` thresholds.

Risks: public mutable `buff` and `bsize` are performance-oriented but allow accidental misuse; callers must not free `buff` directly or change `bsize` inconsistently. The manager destructor exists but comments say it is never deleted, so cleanup assumptions are daemon-oriented.

Test signals: compile tests for consumers; ownership tests that destructor frees memory exactly once; pool API tests; integration tests through protocol reads/writes and stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdConfig.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdConfig.cc

Purpose: implements startup and configuration for the `xrootd` daemon: command-line parsing, environment setup, root/drop-privilege handling, config-file directive dispatch, admin/home/pid/manifest setup, TLS context creation, network binding, protocol loading, scheduler/buffer/poll startup, stats/reporting, and runtime tunables.

Important APIs/types/functions: local `TlsError`, helper class `XrdConfigProt`, helper class `XrdTcpMonInfo`, `XrdConfig` constructor, `Configure`, `ConfigXeq`, `ASocket`, `ConfigProc`, `getNet`, `getUG`, `Manifest`, `PidFile`, `setCFG`, `setFDL`, `Setup`, `SetupAPath`, `SetupTLS`, `Usage`, and directive parsers `xapath`, `xallow`, `xhpath`, `xbuf`, `xmaxfd`, `xnet`, `xnkap`, `xpidf`, `xport`, `xprot`, `xrep`, `xsched`, `xsit`, `xtcpmon`, `xtls`, `xtlsca`, `xtlsci`, `xtmo`, and `xtrace`.

Control flow: construction sets defaults and fills `ProtInfo` pointers to global log, scheduler, buffer pool, environment, and format. `Configure()` reconstructs the command line, derives default protocol name, captures passthrough options, parses daemon options, validates absolute paths, selects IP mode, optionally drops privileges, daemonizes, resolves host/instance environment, configures logging, opens `/dev/null`, processes config records through `ConfigProc()`, sets admin path, initializes TLS, exports max buffer/interface data, makes home/pid/manifest state, calls `Setup()`, optionally loads tcpmon, signals the parent process in background mode, and logs final status. `Setup()` raises fd/core limits, probes sendfile/TCP_CORK support, starts buffers/scheduler/link/poll, resolves protocol ports, creates stats, binds networks through `getNet()`, loads protocols with `XrdProtLoad`, adds extra protocol ports, and initializes reporting.

State and persistence behavior: modifies process environment (`XRDINSTANCE`, `XRDHOST`, `XRDNAME`, `XRDPROG`, `XRDCONFIGFN`, `XRDADMINPATH`, `XRDPORT`, optional certificate vars), global objects (`BuffPool`, `Sched`, `XrdTrace`, `tlsCtx`, `XrdNetTCP`, `TcpMonPin`, `devNull`, socket keepalive globals), resource limits, current directory/home, pid files, admin `.xrd` directory, manifest/env file and symlinks, log files, network sockets, TLS context, and protocol loader registry. Config capture is stored in `XrdGlobal::totalCF`.

Dependencies: broad integration with Xrd core (`XrdBuffer`, `XrdBuffXL`, `XrdInet`, `XrdLink`, `XrdLinkCtl`, `XrdPoll`, `XrdScheduler`, `XrdStats`, `XrdTrace`, `XrdProtLoad`), network utilities/security/interface refresh, Ouc parsing/logging/env/site/plugin helpers, Sys logging/fd/thread utilities, TLS context, OS resource/socket APIs, and optional Linux/Apple features.

Integration points: this is the central boot coordinator for `xrootd`. Protocol plugins receive `XrdProtocol_Config` with network, scheduler, buffer, stats, TLS, environment, host, port, and config references. Config directives update lower layers before sockets and protocols are activated. `Xrd/CMakeLists.txt` builds it only into the server executable, not client-only builds.

Risks: startup order is delicate: logging, privilege drop, config capture, TLS, network routing, and protocol loading all depend on earlier state. Many values are raw `char*` with manual ownership; reconfiguration paths must avoid leaks/use-after-free. `PidFile()` logs errors but returns true even after old-style pid write failure. `ASocket()` contains disabled admin-socket code, so admin path creation does not imply a usable socket. Dynamic config only supports a restricted directive set. Root safety depends on `-R` parsing and effective UID checks. TLS without CA data fails unless `noverify` is explicit.

Test signals: daemon startup tests for foreground/background, invalid root execution, `-R` privilege drop, missing/relative paths, bad config, pid/manifest files, and logging; directive parser tests for buffers/network/protocol/report/sched/tls/timeout/trace; TLS setup tests with certdir/certfile/noverify/ciphers; protocol-loading tests with multiple ports and TLS-only ports; resource-limit tests; smoke test binding ephemeral ports and accepting connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdConfig.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdConfig.hh

Purpose: declares `XrdConfig`, the configuration/startup orchestrator for the Xrd server.

Important APIs/types/functions: public `Configure(int,char**)`, `ConfigXeq(char*,XrdOucStream&,XrdSysError*)`, constructor, `ProtInfo`, `NetADM`, and `NetTCP`. Private helpers and directive parsers match the implementation in `XrdConfig.cc`. State fields track identity, paths, TLS files/options, reporting, protocol list, network options, ports, permissions, strict fd handling, and max file descriptors.

Control flow: the public API gives callers one main startup entry point and a directive execution function used by config processing and dynamic updates. Private methods separate command parsing, config processing, network acquisition, TLS setup, protocol setup, pid/manifest work, and directive-specific parsing.

State and persistence behavior: the class stores all mutable startup configuration before it is committed to global runtime objects, filesystem paths, sockets, environment variables, and protocol configuration. `ProtInfo` is the handoff structure consumed by protocol loaders.

Dependencies: includes `XrdProtLoad.hh` and `XrdProtocol.hh`, uses `std::vector`, system types, and forward declarations for logging, networking, security, stream, monitor, and protocol helper types.

Integration points: instantiated by the server main path; owns `NetTCP` vector of bound networks; feeds `XrdProtLoad` and protocol plugins; coordinates with global log/scheduler/buffer/TLS state through implementation.

Risks: many private fields are raw pointers with ownership managed manually in implementation. Adding directives requires updating both header declaration and `ConfigXeq()` dispatch. Public `ProtInfo` and `NetTCP` expose mutable startup/runtime objects to consumers, so invariants are convention-based.

Test signals: compile tests when adding directive helpers; startup tests through `Configure()`; dynamic directive tests through `ConfigXeq()`; static analysis for pointer ownership and uninitialized fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdGlobals.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdGlobals.cc

Purpose: defines global singleton-style objects required by the Xrd package.

Important APIs/types/functions: namespace `XrdGlobal` defines `Logger`, `Log`, `XrdTrace`, `Sched`, `BuffPool`, `tlsCtx`, `XrdNetTCP`, external `xlBuff`, and `devNull`.

Control flow: no functions; initialization happens during static object construction before daemon startup. `Log` and `XrdTrace` are wired to `Logger`, and `Sched` receives `Log`/`XrdTrace`.

State and persistence behavior: process-global runtime state. These objects persist for daemon lifetime and are intentionally not torn down. `tlsCtx` and `XrdNetTCP` start null and are set by configuration; `devNull` starts `-1` and is opened during configuration.

Dependencies: includes buffer, large-buffer, inet, scheduler, trace, logger, and error headers. Forward declares `XrdTlsContext`.

Integration points: most Xrd runtime modules reference these globals for logging, tracing, scheduling, buffer allocation, default TCP network, TLS context, and `/dev/null` fd. `XrdConfig.cc` is the main initializer of the mutable pointers/fd.

Risks: static initialization order across translation units can be fragile if other globals depend on these before construction. Global mutable state complicates tests and multi-instance embedding. `extern XrdBuffXL xlBuff` is defined elsewhere, so link order/source inclusion matters.

Test signals: link tests for globals; startup smoke tests verifying `Log`, `Sched`, `BuffPool`, and `XrdNetTCP` are initialized before protocol loading; tests should isolate global state between daemon instances where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdGlobals.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInet.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdInet.cc

Purpose: implements `XrdInet`, a server/client TCP network wrapper over `XrdNet` that returns `XrdLink` objects, supports optional security authorization, systemd socket activation, scalable accept/connect behavior, and listener setup.

Important APIs/types/functions: static `AssumeV4`, `TraceID`, `netIF`, methods `Accept`, `BindSD`, `Connect`, private `Listen`, and `Secure`.

Control flow: `Accept()` loops on `XrdNet::Accept()` until success unless a timeout is specified, posts an optional semaphore after accept, optionally resolves the peer name, checks `XrdNetSecurity::Authorize`, closes unauthorized sockets, and wraps accepted sockets via `XrdLinkCtl::Alloc`. `BindSD()` uses systemd-provided sockets when available and matching requested port/type; otherwise it falls back to `Bind()`. For stream sockets it calls `Listen()`. `Connect()` opens an outbound connection and wraps it in `XrdLink`. `Secure()` merges or installs security policy.

State and persistence behavior: instance state is the inherited bound socket and `Patrol` pointer; class state holds interface routing object and IPv4 assumption flag. Runtime side effects include accepted/connected sockets, closed unauthorized sockets, systemd fd adoption, UDP buffer queues in inherited state, and trace/log messages.

Dependencies: `XrdNet`, `XrdNetAddr`, `XrdNetOpts`, `XrdNetSecurity`, `XrdLinkCtl`, `XrdTrace`, optional systemd `sd-daemon`, optional `XrdNetBuffer`/`XrdNetSocket`, POSIX sockets, DNS/name lookup, and logging.

Integration points: created by `XrdConfig::getNet()` for listening ports and exposed through `XrdProtocol_Config::NetTCP`. Accepted sockets become `XrdLink` instances managed by link control and protocol dispatch. `XrdConfig::xallow` supplies `Patrol`; `xnet` configures routing/name behavior through shared network/interface classes.

Risks: the accept loop sleeps and logs every 60 failures for non-timeout accepts, so persistent accept errors can delay shutdown/error handling. Authorization may require name resolution if reverse lookup is enabled, affecting latency. Systemd socket matching must align with port, address family, and stream/datagram type. `unkown.endpoint` typo is harmless but visible in logs.

Test signals: accept/connect smoke tests, authorization allow/deny tests, timeout accept behavior, systemd socket activation tests when built with `HAVE_SYSTEMD`, listen backlog error tests, DNS/no-reverse-lookup tests, and trace/log assertions for accepted/connected links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInet.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInet.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdInet.hh

Purpose: declares `XrdInet`, the Xrd-specific network class layered on `XrdNet`.

Important APIs/types/functions: public `Accept`, `BindSD`, `Connect`, `Secure`, constructor/destructor, static `SetAssumeV4`, `GetAssumeV4`, static `netIF`, private `Listen`, `Patrol`, `TraceID`, and static `AssumeV4`.

Control flow: the interface exposes high-level socket lifecycle operations that return `XrdLink` rather than raw fds. Implementation adds security, systemd socket activation, and listen handling.

State and persistence behavior: owns/uses inherited network socket state and a security policy pointer; static flags/interface state affect all instances.

Dependencies: includes `XrdNet/XrdNet.hh` and `XrdNet/XrdNetIF.hh`; forward declares logging, semaphores, security, and link types.

Integration points: server configuration creates one `XrdInet` per bound port; protocol code accepts client links from it; routing and private-address behavior are controlled through static `netIF`.

Risks: static `netIF` and `AssumeV4` are global knobs. `Secure()` accepts a raw pointer and ownership semantics are not obvious from the header. Multiple networks sharing one security object must coordinate lifetime.

Test signals: compile tests for inheritance contract; unit/integration tests through `XrdConfig::getNet()`, `Accept()`, and `Connect()`; global setting tests for `AssumeV4`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInet.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInfo.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdInfo.cc

Purpose: embeds the project license text into the `XrdLicense` string used by command-line help/license output.

Important APIs/types/functions: global `const char *XrdLicense`, initialized by including `../../LICENSE` as a string literal.

Control flow: no functions. The compiler expands the license file into a C string at build time.

State and persistence behavior: static read-only process data. It persists for the lifetime of the binary and is printed by `XrdConfig::Usage(-1)`.

Dependencies: includes `Xrd/XrdInfo.hh` and the relative `../../LICENSE` file, which must be formatted as includable string-literal content.

Integration points: `XrdConfig.cc` declares `extern const char *XrdLicense` and prints it for the `-H` option.

Risks: build breaks if the relative license path changes or the file is not valid for textual inclusion. License output can become stale if build packaging substitutes a different license without updating this include path.

Test signals: build test ensuring `XrdInfo.cc` compiles; CLI `xrootd -H` smoke test; packaging tests checking license file availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInfo.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdInfo.hh

Purpose: defines basic Xrd format/version/banner constants used by startup and informational output.

Important APIs/types/functions: includes `XrdVersion.hh`, defines `XrdFORMAT`, `XrdFORMATB`, and `XrdBANNER`.

Control flow: no runtime flow.

State and persistence behavior: compile-time constants only. `XrdFORMATB` is assigned to `XrdProtocol_Config::Format` during configuration, and `XrdBANNER` is logged during startup.

Dependencies: `XrdVersion.hh` supplies `XrdVSTRING` and related version macros.

Integration points: used by `XrdConfig.cc` for banner logging and protocol config format compatibility. Any protocol plugin receiving `ProtInfo` may inspect the format.

Risks: version/format constants must change only with compatible runtime expectations. `XrdBANNER` contains a fixed copyright range and dynamic version string.

Test signals: compile tests; startup log assertions; plugin compatibility checks on `ProtInfo.Format`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdJob.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdJob.hh

Purpose: declares the minimal abstract job base class used by `XrdScheduler` queues.

Important APIs/types/functions: public `NextJob`, `Comment`, pure virtual `DoIt()`, constructor, virtual destructor, private `SchedTime`, and friendship with `XrdScheduler`.

Control flow: scheduler code links jobs through `NextJob`, schedules by private `SchedTime`, and invokes `DoIt()` polymorphically when work is due. The class itself contains no scheduling logic.

State and persistence behavior: in-memory queue node state only. `Comment` is a static-description pointer for debugging, not owned text. `SchedTime` is managed by the scheduler.

Dependencies: standard C headers for allocation/string/time and no Xrd-specific includes by design; comments state it should remain independent for queue-processing efficiency.

Integration points: any component that wants scheduled work derives from `XrdJob` and implements `DoIt()`. `XrdScheduler` is the only class allowed to manipulate private schedule time.

Risks: derived jobs must manage their own lifetime and thread-safety. Public `NextJob` is optimized for queues but can be corrupted by accidental external writes. `Comment` must outlive the job if it points to static text as intended.

Test signals: scheduler unit tests with derived jobs; queue integrity tests; delayed execution tests; sanitizer tests for job lifetime and virtual destructor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdJob.hh -->
