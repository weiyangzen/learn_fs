# subset-b-007935 research

Grouped research for XRootD CMS supervisor/talk/util headers and the XrdCrypto abstract, lite, RSA, digest, X.509, CRL, request, and GSI chain components. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsState.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsState.hh

## Purpose

`XrdCmsState` is the cluster-manager state publisher for CMS/olbd state. The header declares a process-global state object (`XrdCms::CmsState`) that tracks whether a server or front-end is suspended, whether staging is disabled, the data port, active subscriber counts, staging-capable subscriber counts, and manager/front-end/space health. Its public API is intentionally small because the implementation is used by protocol and monitor code to report state transitions to redirectors and subscribers.

## Important APIs and Types

The core state API is `Enable()`, `Monitor()`, `Port()`, `sendState(XrdLink *)`, two `Set()` overloads, and `Update(StateType, int, int)`. `StateType` distinguishes updates for aggregate activity, subscriber counts, front-end state, free-space state, and staging state. The public constants `SRV_Suspend`, `FES_Suspend`, `All_Suspend`, and `All_NoStage` encode state-control bits likely transmitted in CMS state messages or derived from admin files.

## Control Flow

Callers initialize thresholds and admin paths with `Set()`, enable reporting, then call `Update()` as cluster conditions change. `Status()` is private and computes the outbound status byte from state-change flags and current state. `Monitor()` is exposed as a thread entry point or long-running watcher that observes state changes and admin-control files; `sendState()` writes the current state to an `XrdLink`.

## State and Persistence Behavior

State is process-local but guarded by `XrdSysMutex` and signaled with `XrdSysSemaphore`, indicating concurrent producer/consumer updates. Persistence is indirect through `NoStageFile` and `SuspendFile` paths, which allow admin state to be represented by filesystem sentinels. The class tracks current and previous state to report changes only when meaningful.

## Dependencies and Integration Points

It depends on `XrdSys` threading primitives, `XrdCmsTypes.hh`, and `XrdLink`. It integrates with CMS configuration/protocol code that maintains subscriber counts and sends state to manager or redirector peers.

## Risks and Edge Cases

The interface exposes mutable `Suspended` and `NoStaging` fields, so callers can bypass the mutex if they write directly. Correct behavior depends on the unseen implementation consistently locking around all state transitions and respecting admin file state. Off-by-one or stale `minNodeCnt`/subscriber counts can incorrectly suspend a cluster.

## Test Signals

Useful tests would drive `Set()`, `Update()`, and admin-file changes while asserting state bytes emitted by `sendState()`, port reporting, and semaphore wakeups. Concurrency tests should stress simultaneous count, space, and staging updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsState.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSupervisor.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSupervisor.cc

## Purpose

`XrdCmsSupervisor.cc` implements the supervisor endpoint used by a supervisor node to communicate with exactly one redirector through a Unix-domain socket named `olbd.super`. It creates an `XrdInet` listener, normalizes supervisor-specific configuration, and accepts redirector connections for CMS protocol processing.

## Important APIs and Functions

`XrdCmsSupervisor::Init(const char *AdminPath, int AdminMode)` prepares the socket and listener. It uses `XrdNetSocket::socketPath()` to build an admin socket path, creates `NetTCPr`, applies `Config.myDomain`, binds the path, and forces supervisor subscription/drop behavior. `Start()` accepts connections forever, allocates an `XrdCmsProtocol` for `"redirector"`, attaches it to the `XrdLink`, calls `Process()`, and closes the link.

## Control Flow

Initialization fails early if the socket path cannot be created, if `XrdInet` allocation fails, or if bind fails. On success it sets `Config.SUPCount = 1`, `SUPLevel = 0`, and `DRPDelay = 0`, then flips `superOK`. Runtime flow is a single infinite accept loop; each connection is handled synchronously before the next accept.

## State and Persistence Behavior

State is static: `superOK` records readiness and `NetTCPr` owns the listener. The Unix socket path is persistent in the admin filesystem namespace until cleaned by socket/bind handling. There is no explicit shutdown or listener deletion in this file.

## Dependencies and Integration Points

The code depends on `XrdInet`, `XrdLink`, `XrdCmsConfig`, `XrdCmsProtocol`, tracing/error globals, and `XrdNetSocket`. It integrates supervisor nodes with redirector protocol processing and mutates global CMS config to match supervisor semantics.

## Risks and Edge Cases

The accept loop has no exit path, backoff, or error logging for repeated accept failures. It assumes only one redirector is allowed but enforces that mostly by serial synchronous processing, not explicit peer identity. Configuration mutation in `Init()` has broad process impact and must happen before other code relies on the original drop-delay or subscriber-count settings.

## Test Signals

Integration tests should verify socket path creation, listener bind failures, forced config values, successful allocation/processing of a redirector protocol, and cleanup/close behavior after a client disconnects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSupervisor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSupervisor.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSupervisor.hh

## Purpose

`XrdCmsSupervisor.hh` declares the static supervisor facade used to initialize and run a supervisor-side CMS listener for redirector communication. It exposes no per-instance behavior; all meaningful state is static.

## Important APIs and Types

`superOK` is a public readiness flag. `Init()` creates and binds the supervisor socket. `Start()` enters the accept/process loop. `NetTCPr` is a private static `XrdInet *` listener shared by those methods.

## Control Flow

Callers are expected to call `Init()` once and then `Start()` if initialization succeeded. Constructor/destructor are trivial and unused for lifecycle management.

## State and Persistence Behavior

The class persists process state in static members only. Socket persistence and configuration changes are handled by the implementation file.

## Dependencies and Integration Points

The only declaration dependency is the forward declaration of `XrdInet`, but implementation links it to Xrd network and CMS protocol subsystems.

## Risks and Edge Cases

The header advertises public static mutable state with no synchronization. Multiple `Init()` calls could leak or overwrite listener state unless external startup code prevents reinitialization.

## Test Signals

Tests should assert that `superOK` changes only after successful initialization and that `Start()` is not called before `NetTCPr` is created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSupervisor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTalk.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTalk.cc

## Purpose

`XrdCmsTalk.cc` implements low-level CMS request/response framing over `XrdLink`. It serializes `CmsRRHdr` headers, length-prefixed payloads, and CMS response/error records using network byte order and vectored writes.

## Important APIs and Functions

`Attend()` receives a complete header, decodes `Hdr.datalen` with `ntohs`, validates caller buffer capacity, and receives the payload. `Complain()` sends a `kYR_error` response with an integer error code and NUL-terminated message. `Request()` sets `Hdr.datalen` and sends header plus body. `Respond()` sends a `CmsResponse` with response code and a four-byte value overhead followed by optional payload.

## Control Flow

Receive flow is strict: header must arrive fully, length must fit, and payload must arrive fully before success. Send flow uses two-entry `iovec` arrays and treats negative `Send()` return as failure. Error methods return string literals for callers to log or act on.

## State and Persistence Behavior

This file is stateless. It mutates the supplied header's length field and writes protocol messages to the link.

## Dependencies and Integration Points

It depends on `XProtocol/YProtocol.hh` for CMS wire structures and response codes, `XrdLink` for I/O, and C networking byte-order helpers. It is used by CMS protocol participants that need a compact request/response helper independent of the full protocol class.

## Risks and Edge Cases

`Request()` casts payload length to `unsigned short`, so callers must not pass bodies above 65535 bytes. `Respond()` includes a fixed four-byte overhead in `datalen`; mismatches with protocol readers would desynchronize framing. `Attend()` does not validate null buffers for nonzero data and treats partial reads as generic failures without preserving errno.

## Test Signals

Tests should round-trip headers and payloads with boundary lengths, oversized payload rejection, partial read/write simulation, and exact wire layout for `Complain()` and `Respond()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTalk.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTalk.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTalk.hh

## Purpose

`XrdCmsTalk.hh` declares a static helper class for CMS link-level message exchange. It centralizes request, response, complaint, and receive operations around `CmsRRHdr`.

## Important APIs and Types

The public methods are `Attend()`, `Complain()`, `Request()`, and `Respond()`. `Attend()` returns a nullable error string and fills response length. `Complain()` returns an integer status after sending an error response. `Request()` and `Respond()` return nullable error strings after link sends.

## Control Flow

The header's API makes callers responsible for allocating payload buffers, selecting timeouts, and interpreting string errors. The default receive timeout is 5000 milliseconds.

## State and Persistence Behavior

The class has no member state. It mutates caller-supplied headers and communicates through an `XrdLink`.

## Dependencies and Integration Points

It includes `XProtocol/YProtocol.hh` for CMS wire types and forward-declares `XrdLink`. It integrates with CMS protocol code that already owns links and buffers.

## Risks and Edge Cases

The static API has no type-level protection for buffer size versus header length and no support for payloads above the 16-bit protocol length. Callers must check returned error strings consistently.

## Test Signals

Mock-link tests can assert timeout forwarding, length encoding, and correct handling of short reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTalk.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTrace.hh

## Purpose

`XrdCmsTrace.hh` defines CMS tracing masks and macros that wrap `XrdSysTrace`/`XrdSysError` logging. It provides compile-time no-op behavior under `NODEBUG` and category-gated runtime tracing otherwise.

## Important APIs and Types

Trace masks include `TRACE_Debug`, `TRACE_Stage`, `TRACE_Defer`, `TRACE_Forward`, `TRACE_Redirect`, `TRACE_Files`, and `TRACE_Space`, plus `TRACE_ALL`. Macros include `QTRACE`, `DEBUG`, `DEBUGR`, `TRACE`, `TRACER`, `TRACEX`, and `EPNAME`. Namespace globals `XrdCms::Trace` and `XrdCms::Say` are declared for shared logging.

## Control Flow

Call sites declare `EPNAME()` and invoke category macros. If tracing is enabled for a category, macros route through `SYSTRACE`; the `R` variants include `Arg.Ident`, so they are intended for contexts where an `Arg` object is in scope.

## State and Persistence Behavior

Runtime state lives in the global `Trace.What` mask and global error object. No persistent state is managed here.

## Dependencies and Integration Points

It integrates with XrdSys logging and is included throughout CMS source files. Macro names are short and become part of local compilation context.

## Risks and Edge Cases

Macros assume local variables such as `epname` and sometimes `Arg` exist. The no-debug branch removes statements entirely, so trace expressions must not have side effects needed for correctness.

## Test Signals

Build tests should compile representative files with and without `NODEBUG`. Runtime checks can set `Trace.What` and assert that only selected categories emit logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTypes.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTypes.hh

## Purpose

`XrdCmsTypes.hh` defines shared CMS constants and scalar types used across the CMS manager, server, and redirector code.

## Important APIs and Types

`SMask_t` is an unsigned 64-bit mask type with `FULLMASK` set to all bits. `STMax` sets the maximum subscriber cell size to 64. `maxRD` is 65, one greater than the real maximum redirector count because slot zero is unused. `XrdCmsMAX_PATH_LEN` is 1024 and `XrdCmsVERSION` is `1.0.0`.

## Control Flow

There is no executable control flow; the header provides compile-time constants.

## State and Persistence Behavior

There is no runtime state. The constants shape in-memory masks, array sizes, path buffers, and version reporting elsewhere.

## Dependencies and Integration Points

Many CMS headers and implementations include this file to agree on mask width, subscriber limits, redirector slots, and path-length assumptions.

## Risks and Edge Cases

The 64-bit mask and `STMax` must stay aligned; increasing subscriber counts without changing mask representation would break bitset logic. Fixed path length may truncate or reject longer admin/config paths depending on consumers.

## Test Signals

Compile-time/static tests should assert `STMax <= sizeof(SMask_t) * 8` and redirector arrays account for unused slot zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTypes.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsUtils.cc

## Purpose

`XrdCmsUtils.cc` implements CMS utility functions for loading performance-monitor plugins, parsing manager host/port/site specifications, displaying resolved manager addresses, and mapping site numbers to names.

## Important APIs and Functions

`loadPerfMon()` pins a plugin with `XrdOucPinLoader` and resolves `XrdCmsPerfMonitor`. `ParseMan()` parses manager host specifications, optional `@site` tags, optional `%instance` scope, trailing `+` address expansion, numeric or service-name ports, dynamic DNS behavior, duplicate suppression, and sorted insertion into an `XrdOucTList`. `ParseManPort()` extracts a port from `host:port` syntax or the next config token. `SiteName()` returns a registered site name or `anonymous`. Private `Display()` logs DNS-to-address mappings and `SInsert()` inserts managers in a deterministic order.

## Control Flow

`ParseMan()` first lazily initializes `siteList` from `XRDSITE` or `local`, then strips site and instance qualifiers from `hPort`. It detects trailing `+` in `hSpec` for multi-address expansion, rejects hostname globbing with dynamic DNS, resolves/validates the port, resolves hosts unless dynamic DNS defers resolution, optionally updates `sPort` for local-address matches, and merges non-duplicates into the existing list.

## State and Persistence Behavior

The file maintains static `siteList` and `siteIndex` for process-lifetime site IDs. It mutates input strings in place by replacing delimiters such as `@`, `%`, `+`, and `:` with NUL bytes. Returned manager lists and port strings are caller-owned. Plugin loading pins shared libraries for process lifetime.

## Dependencies and Integration Points

Dependencies include `XrdNetAddr`, `XrdNetUtils`, `XrdOuca2x`, `XrdOucPinLoader`, `XrdOucStream`, `XrdOucTList`, and `XrdSysError`. The functions are called by CMS configuration parsing and performance-monitor setup.

## Risks and Edge Cases

Callers must pass mutable buffers; passing string literals would be unsafe. `SInsert()` sorts with a non-obvious condition and should be tested for intended host/port ordering. Static site state is not synchronized, so concurrent configuration parsing could race. Dynamic DNS mode stores unresolved hostnames and changes duplicate/local-port semantics.

## Test Signals

Tests should cover numeric and service ports, IPv6 bracket parsing, missing port errors, `@site` registration, `%instance` filtering against `XRDNAME`, trailing `+` multi-host expansion, dynamic DNS paths, duplicate manager warnings, and `SiteName()` fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsUtils.hh

## Purpose

`XrdCmsUtils.hh` declares CMS configuration and plugin utility functions used by manager/server setup code.

## Important APIs and Types

The static API consists of `loadPerfMon()`, `ParseMan()`, `ParseManPort()`, and `SiteName()`. Private helpers `Display()` and `SInsert()` support implementation-only DNS display and sorted manager-list insertion.

## Control Flow

The declared functions are intended for configuration parse time: load optional perf monitor, parse manager endpoint and port tokens, merge manager list entries, and later translate numeric site IDs back to text.

## State and Persistence Behavior

Although the header does not expose member state, implementation maintains process-global site mappings and returns caller-owned allocations/lists. `ParseMan()` may modify its `hSpec` and `hPort` arguments in place.

## Dependencies and Integration Points

It forward-declares `XrdCmsPerfMon`, `XrdOucStream`, `XrdOucTList`, `XrdSysError`, and `XrdVersionInfo`, limiting include churn for configuration users.

## Risks and Edge Cases

The API contract requires mutable C strings and caller-managed memory, which is easy to misuse. Optional output `sPort` can be updated even when no manager list is returned.

## Test Signals

Header-level integration tests should compile consumers with only forward declarations, while implementation tests validate ownership and in-place parsing expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsVnId.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsVnId.hh

## Purpose

`XrdCmsVnId.hh` documents and defines the ABI for CMS virtual node-identification plugins loaded through the `all.vnidlib` directive. It supports container/VM deployments where hostnames or IP addresses change and are unsuitable for stable node tracking.

## Important APIs and Types

The macro `XrdCmsgetVnIdArgs` expands to the required `extern "C" std::string XrdCmsgetVnId(...)` signature: an `XrdSysError` reference, configuration file path, plugin parameters, node role character, and maximum allowed return length. The role values are `m`, `s`, and `u` for manager, server, and supervisor, with uppercase variants for proxy roles.

## Control Flow

During initialization, CMS loads the plugin and calls `XrdCmsgetVnId` once. Returning a non-empty string within `mlen` succeeds; returning an empty/null-equivalent string or an overlong ID aborts initialization.

## State and Persistence Behavior

The plugin ABI is called only once and need not be thread-safe. The returned ID becomes part of the virtual-network identity used to track nodes instead of host/IP identity.

## Dependencies and Integration Points

Plugins include this header, `XrdSysError`, and usually `XrdVersion.hh` to declare `XrdVERSIONINFO`. The ABI integrates with CMS node-registration and identity tracking.

## Risks and Edge Cases

The documentation contains typos but the ABI is clear. Plugins must use the exact unmangled C symbol and respect maximum length. Non-deterministic IDs would defeat stable tracking.

## Test Signals

Plugin-loading tests should verify symbol lookup, role propagation, parameter string handling, max-length enforcement, and initialization failure on empty ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsVnId.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdCrypto/CMakeLists.txt

## Purpose

This CMake file defines how XRootD crypto components are built and installed. It separates low-level utility-linked crypto objects, a lightweight OpenSSL-dependent crypto library, the abstract `XrdCrypto` facade library, and the OpenSSL implementation plugin.

## Important APIs and Targets

`target_sources(XrdUtils PRIVATE ...)` adds base X.509/RSA/auxiliary and OpenSSL concrete utility sources to `XrdUtils` to avoid linking all of `libXrdCryptossl` into utility users. `XrdCryptoLite` is a shared library built from `XrdCryptoLite.cc`, `XrdCryptoLite.hh`, and `XrdCryptoLite_bf32.cc`, linked to `XrdUtils` and `OpenSSL::Crypto`. `XrdCrypto` is a shared abstract facade built from basic/cipher/factory/digest/GSI-chain sources. `${XrdCryptossl}` is a module plugin named `XrdCryptossl-${PLUGIN_VERSION}`.

## Control Flow

Configure-time flow declares sources, links dependencies, sets `SOVERSION`/`VERSION`, adds the plugin to the aggregate `plugins` target, and installs all three library/module targets under `${CMAKE_INSTALL_LIBDIR}`.

## State and Persistence Behavior

Build state is target-level. Installed artifacts persist ABI boundaries: `XrdCrypto` and `XrdCryptoLite` are shared libraries while the OpenSSL implementation is a loadable module.

## Dependencies and Integration Points

Targets integrate with `XrdUtils`, OpenSSL crypto/SSL imported targets, CMake thread libs, dynamic-loader libs, and the repository's plugin versioning scheme.

## Risks and Edge Cases

Moving concrete OpenSSL sources into `XrdUtils` widens what utility consumers compile/link, so symbol/ABI changes there have broad impact. Plugin naming must match runtime factory loader expectations (`libXrdCrypto<factory>.so`). OpenSSL provider behavior affects `XrdCryptoLite_bf32`.

## Test Signals

Build tests should verify all targets link, install names match runtime loader names, `plugins` depends on the SSL module, and consumers can load `XrdCryptossl` through `XrdCryptoFactory`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoAux.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoAux.cc

## Purpose

`XrdCryptoAux.cc` implements common crypto tracing setup and timezone correction helpers shared by the abstract crypto layer and plugins.

## Important APIs and Functions

`XrdCryptoSetTrace(kXR_int32 trace)` initializes a static logger/error destination, lazily creates global `cryptoTrace`, and maps notification/debug/dump flags to `cryptoTrace->What`. `XrdCryptoTZCorr()` computes and caches the local timezone offset relative to UTC using `localtime_r`, `gmtime_r`, and `mktime`.

## Control Flow

Trace setup always resets the trace mask before enabling progressively more verbose categories. Timezone correction computes once on first successful call and returns the cached offset thereafter.

## State and Persistence Behavior

Static process state includes `Logger`, `eDest`, global `cryptoTrace`, `TZCorr`, and `TZInitialized`. The trace object persists for the life of the process. Timezone offset assumes no daylight-saving correction changes after initialization.

## Dependencies and Integration Points

It depends on `XrdSysLogger`, `XrdSysError`, `XrdCryptoAux.hh`, and `XrdCryptoTrace.hh`. The global `cryptoTrace` is consumed by trace macros in the crypto subsystem.

## Risks and Edge Cases

Trace initialization is not synchronized, so concurrent first calls can race. `XrdCryptoTZCorr()` caches offset and ignores later timezone/DST changes. The comment says no DST; callers must not use it for precise civil-time conversion across DST transitions.

## Test Signals

Tests should verify trace flag mapping, idempotent repeated calls, and timezone correction under controlled `TZ` settings. Thread-safety tests would expose first-call races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoAux.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoAux.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoAux.hh

## Purpose

`XrdCryptoAux.hh` provides shared crypto macros, tracing flags, RSA defaults, key-derivation function typedefs, and utility declarations used across the XRootD crypto abstraction.

## Important APIs and Types

`ABSTRACTMETHOD(x)` logs that a virtual method must be overridden. Trace flags are `cryptoTRACE_Notify`, `cryptoTRACE_Debug`, `cryptoTRACE_Dump`, and `cryptoTRACE_ALL`. RSA constants enforce/default to 2048-bit keys and exponent `0x10001`. `XrdCryptoKDFunLen_t` and `XrdCryptoKDFun_t` define plugin KDF hooks. Declarations include `XrdCryptoKDFunLen()`, `XrdCryptoKDFun()`, `XrdCryptoSetTrace()`, and `XrdCryptoTZCorr()`.

## Control Flow

The header supplies declarations and macros only. Runtime behavior comes from concrete functions and plugin overrides.

## State and Persistence Behavior

No state is declared here except constants. Implementations use the trace and timezone declarations for process-global behavior.

## Dependencies and Integration Points

It includes C stdio/time, `XrdSysHeaders` on non-Windows, and `XProtocol/XProtocol.hh`. Almost all crypto base classes depend on this header for abstract-method diagnostics and constants.

## Risks and Edge Cases

`ABSTRACTMETHOD` writes to `std::cerr` but this header does not directly include `<iostream>`; it relies on transitive includes. Default RSA parameters are policy-bearing constants and should be updated cautiously.

## Test Signals

Compile tests should include this header independently across supported platforms. Policy tests should assert RSA defaults meet current security expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoAux.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoBasic.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoBasic.cc

## Purpose

`XrdCryptoBasic.cc` implements a generic owned byte buffer plus optional type string used as the base for crypto objects such as ciphers and message digests.

## Important APIs and Functions

The constructor copies an optional type string and initializes an optional byte buffer. `AsBucket()` copies the current buffer into an `XrdSutBucket`. `AsHexString()` converts up to `XrdSutMAXBUF / 2 - 1` bytes to a static hex string. `FromHex()` decodes a hex string into a new owned buffer. `SetLength()`, `SetBuffer()`, and `SetType()` mutate the owned fields, while `UseBuffer()` from the header transfers raw pointer ownership without copying.

## Control Flow

Mutation methods allocate new buffers first, copy or zero-fill data, then replace the old buffer. `FromHex()` computes output size, decodes through `XrdSutFromHex`, and swaps ownership only on success.

## State and Persistence Behavior

Each instance owns `type` and `membuf` and deletes them in the destructor. `AsHexString()` uses a static output buffer, so the returned pointer is overwritten by later calls and is not thread-safe.

## Dependencies and Integration Points

It depends on `XrdSutAux` hex helpers, `XrdSutBucket`, and `XrdCryptoAux.hh`. Derived classes rely on its buffer/type ownership semantics.

## Risks and Edge Cases

`SetLength()` copies `l` bytes from the old buffer even when shrinking or when old `membuf` is null; if `l > lenbuf`, it can read past the old allocation before zero-filling the extension. `UseBuffer()` takes a `const char *` but later deletes it with `delete[]`, so callers must pass heap memory allocated compatibly and must not pass literals or stack memory. Static hex output is unsafe across threads.

## Test Signals

Tests should cover construction with null/empty buffers, `FromHex()` odd-length input, `SetLength()` grow/shrink from null and non-null buffers, ownership transfer with `UseBuffer()`, and concurrent `AsHexString()` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoBasic.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoBasic.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoBasic.hh

## Purpose

`XrdCryptoBasic.hh` declares the base buffer abstraction shared by crypto facade classes. It stores an optional type label and a mutable binary buffer.

## Important APIs and Types

Public getters include `AsBucket()`, `AsHexString()`, `Length()`, `Buffer()`, and `Type()`. Setters include `FromHex()`, `SetLength()`, `SetBuffer()`, `SetType()`, and `UseBuffer()`. The class owns `lenbuf`, `membuf`, and `type`.

## Control Flow

Derived classes use this as a common serialization and buffer-management layer. `UseBuffer()` bypasses allocation to install caller-provided memory directly.

## State and Persistence Behavior

Instance state is heap-owned and released by the virtual destructor. `Length()` returns a `kXR_int32` value as `int`, so consumers treat buffer lengths as signed 32-bit quantities.

## Dependencies and Integration Points

It depends on XRootD protocol integer types and `XrdSutBucket`. `XrdCryptoCipher` and `XrdCryptoMsgDigest` inherit from it.

## Risks and Edge Cases

The ownership contract for `UseBuffer()` is dangerous because the input is typed as `const char *` but becomes owned mutable storage. The class does not define copy/move constructors, so default copying would double-free pointers if used.

## Test Signals

Compile and runtime tests should prevent accidental value copying and validate bucket/hex conversion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoBasic.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoCipher.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoCipher.cc

## Purpose

`XrdCryptoCipher.cc` provides the abstract symmetric-cipher base implementation and bucket-level convenience wrappers for encryption and decryption.

## Important APIs and Functions

Most virtual methods (`Finalize`, `IsValid`, `SetIV`, `RefreshIV`, `IV`, `Public`, `AsBucket`, raw `Encrypt`/`Decrypt`, output-length queries, default-length check, and max-IV query) log `ABSTRACTMETHOD` and return failure defaults. The concrete logic is in `Encrypt(XrdSutBucket &, bool)` and `Decrypt(XrdSutBucket &, bool)`, which allocate output buffers, optionally prepend/extract IVs, call raw virtual methods, and update buckets.

## Control Flow

For bucket encryption, the wrapper refreshes an IV when requested, allocates `EncOutLength(size) + liv`, copies the IV prefix, encrypts into the remaining buffer, and updates the bucket when raw encryption succeeds. For bucket decryption, it treats `MaxIVLength()` bytes as the IV prefix, calls `SetIV()`, decrypts the rest, and updates the bucket on success.

## State and Persistence Behavior

The base class has no cipher state beyond inherited `XrdCryptoBasic` storage. Concrete subclasses are responsible for key, IV, padding, and public key-agreement state.

## Dependencies and Integration Points

It depends on `XrdCryptoAux.hh`, `XrdCryptoCipher.hh`, and `XrdSutBucket`. Crypto factory implementations return concrete subclasses through the abstract interface.

## Risks and Edge Cases

On encryption, if raw `Encrypt()` fails after allocation, `newbck` is not deleted, creating a leak. On decryption, `bck.size - liv` can become negative if the bucket is shorter than the IV length, which can produce bad output-length requests. Wrapper ownership relies on `XrdSutBucket::Update()` taking ownership of `newbck`.

## Test Signals

Mock cipher subclasses should test IV prefix handling, update ownership, failure paths, short bucket decryption, and output-length calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoCipher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoCipher.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoCipher.hh

## Purpose

`XrdCryptoCipher.hh` declares the abstract interface for symmetric ciphers and key-agreement ciphers in the plugin crypto architecture.

## Important APIs and Types

The interface exposes key-agreement finalization, validity checks, output sizing, bucket serialization, IV getters/setters, public key material, encryption/decryption on raw buffers and `XrdSutBucket`, and IV refresh. It inherits buffer/type behavior from `XrdCryptoBasic`.

## Control Flow

Concrete plugin classes override the virtual methods. Consumers can use either raw buffer APIs or bucket wrappers that handle IV packing.

## State and Persistence Behavior

The abstract class itself persists only inherited buffer state. Concrete implementations own cryptographic context and IV/key state.

## Dependencies and Integration Points

It depends on `XrdSutBucket` and `XrdCryptoBasic`. `XrdCryptoFactory` constructs instances and authentication/protocol code uses them for encrypted buckets.

## Risks and Edge Cases

The API mixes raw pointer ownership, mutable IV state, and signed lengths. Implementations must document whether returned `IV()`/`Public()` buffers are borrowed or owned.

## Test Signals

Interface conformance tests should verify concrete ciphers support both raw and bucket modes, padding behavior, and default length reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoCipher.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoFactory.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoFactory.cc

## Purpose

`XrdCryptoFactory.cc` implements the abstract crypto factory defaults and the runtime plugin loader that locates concrete factories such as OpenSSL-backed `XrdCryptossl`.

## Important APIs and Functions

The constructor stores a truncated factory name and ID. Almost all virtual construction/hook methods (`Cipher`, `MsgDigest`, `RSA`, `X509`, CRL/REQ constructors, verification/parsing/export hooks, proxy hooks, KDF hooks, and trace setup) are abstract stubs. `operator==` compares factory names. `GetCryptoFactory(const char *factoryid)` is the substantive method: it validates the name, checks a static factory cache, records failed attempts, loads `libXrdCrypto<factoryid>.so` with `XrdOucPinLoader`, resolves `XrdCrypto<factoryid>FactoryObject`, calls it, and caches the returned factory.

## Control Flow

`GetCryptoFactory()` runs under a static mutex. For a new factory ID it grows a static `FactoryEntry` array, initializes a failed-status entry, creates or reuses a pinned loader from a static hash, resolves the factory-object creator, invokes it, then marks the entry successful. Subsequent calls return the cached factory or immediately fail if the prior attempt failed.

## State and Persistence Behavior

The loader cache, factory array, and factory objects are static process-lifetime state. Plugins are pinned through `XrdOucPinLoader`, so shared libraries remain loaded. Failed load attempts are remembered and suppress retry.

## Dependencies and Integration Points

It depends on dynamic loading, `XrdOucHash`, `XrdOucPinLoader`, `XrdSysMutex`, version metadata, and crypto trace macros. The plugin symbol and library naming must match CMake/install output and concrete plugin code.

## Risks and Edge Cases

`factoryname` has a fixed 10-byte buffer but `strcpy(newfactorylist[i].factoryname, factoryid)` copies unbounded input into it, so long factory IDs can overflow. Failed attempts are cached forever, which prevents recovery if a plugin appears later. If `plugins.Add()` stores a null loader after allocation failure, later lookups may behave unexpectedly. Stub methods return null/failure, so using the base factory directly is a runtime error.

## Test Signals

Tests should cover null/empty IDs, overlong IDs, successful plugin load, missing library, missing symbol, failed factory creation, repeated successful lookups, repeated failed lookups, and concurrent first loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoFactory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoFactory.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoFactory.hh

## Purpose

`XrdCryptoFactory.hh` declares the central abstract factory and function-pointer hook types that decouple XRootD crypto consumers from concrete implementations such as OpenSSL.

## Important APIs and Types

The file defines KDF hook types, X.509 certificate/chain parsing and verification hook types, proxy certificate OIDs and proxy hook types, `XrdProxyOpt_t`, and the `XrdCryptoFactory` class. The factory constructs ciphers, message digests, RSA keys, X.509 certs, CRLs, and requests, and returns implementation-specific hooks for chain parsing/export/proxy operations.

## Control Flow

Consumers call `GetCryptoFactory()` to load a named implementation, then use virtual constructors and hook accessors. Concrete factories override base methods; base methods are abstract diagnostics.

## State and Persistence Behavior

Factory instances expose a fixed-length name and integer ID. Static loader/cache state is hidden in the `.cc` file.

## Dependencies and Integration Points

It depends on `XrdCryptoAux.hh` plus forward declarations for XRootD crypto classes, `XrdOucString`, and TLS peer cert wrappers. It defines the ABI that concrete crypto plugins must satisfy.

## Risks and Edge Cases

Function-pointer hooks make null checks essential: some implementations may not support optional features such as VOMS or proxy creation. `MAXFACTORYNAMELEN` constrains names but callers can pass longer names unless the implementation validates them.

## Test Signals

ABI tests should compile a minimal factory plugin and verify every required symbol and hook type matches. Runtime tests should exercise optional hook absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite.cc

## Purpose

`XrdCryptoLite.cc` implements the static factory for the lightweight crypto interface, currently dispatching only the `bf32` algorithm.

## Important APIs and Functions

`XrdCryptoLite::Create(int &rc, const char *Name, const char Type)` declares the external constructor `XrdCryptoLite_New_bf32()`, compares `Name` with `"bf32"`, creates the implementation, sets `rc` to zero on success or `EPROTONOSUPPORT` on failure, and returns the pointer.

## Control Flow

The function is a simple name-dispatch table. Adding an algorithm requires declaring its constructor and adding a comparison branch.

## State and Persistence Behavior

No persistent state is maintained here. The returned object is caller-owned.

## Dependencies and Integration Points

It depends on `<cerrno>`, `<cstring>`, and `XrdCryptoLite.hh`. `XrdCryptoLite_bf32.cc` supplies the concrete external constructor.

## Risks and Edge Cases

`Name` is passed directly to `strcmp()` with no null check, so a null algorithm name crashes. Unsupported algorithms all map to `EPROTONOSUPPORT`.

## Test Signals

Tests should verify `bf32` creation, unsupported name failure, null-name handling expectations, type echoing, and caller deletion of returned objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite.hh

## Purpose

`XrdCryptoLite.hh` declares a minimal stream-crypto abstraction for simple encryption algorithms with built-in decryption validation. It is intentionally lighter than the full plugin-based `XrdCryptoBasic` hierarchy.

## Important APIs and Types

`Create()` constructs named algorithms and associates an arbitrary type byte. Pure virtual `Encrypt()` and `Decrypt()` operate on caller buffers. `Overhead()` returns the extra output bytes required by the concrete algorithm and `Type()` returns the assigned type code. Protected fields store `Extra` and `myType`.

## Control Flow

Consumers select an algorithm by string, allocate destination buffers using `Overhead()`, and call raw encrypt/decrypt with keys and lengths.

## State and Persistence Behavior

Instances persist only overhead and type metadata in the base class; concrete implementations hold no required base-managed cryptographic state.

## Dependencies and Integration Points

The header has no external includes. `XrdCryptoLite` is built as a shared library linked with OpenSSL for the `bf32` implementation.

## Risks and Edge Cases

The interface uses raw pointers and signed lengths, so callers must enforce `srcLen`, `dstLen`, and key validity. The comments contain a likely typo in the encrypt requirement (`srclen <= dstlen + Overhead()` should conceptually ensure destination is large enough for source plus overhead).

## Test Signals

Tests should verify buffer-size contracts, overhead reporting, and validation failure on corrupted ciphertext for each algorithm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite_bf32.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite_bf32.cc

## Purpose

`XrdCryptoLite_bf32.cc` implements the lightweight `bf32` algorithm: Blowfish CFB64 encryption with a CRC32 appended to plaintext for validation after decryption.

## Important APIs and Functions

`XrdCryptoLite_bf32::Encrypt()` validates buffer sizes, appends a network-byte-order CRC32 to the plaintext, encrypts with OpenSSL `EVP_bf_cfb64()` using a zero IV, and returns plaintext length plus four bytes. `Decrypt()` decrypts with the same cipher/zero IV, extracts and verifies the trailing CRC32, and returns decrypted data length or `-EPROTO`. `XrdCryptoLite_New_bf32()` constructs the object and, on OpenSSL 3, attempts to load the legacy provider after fetching a common default digest.

## Control Flow

Encryption uses a stack buffer for messages up to 4096 bytes and `malloc()` for larger plaintext plus CRC. Decryption requires `dstLen > sizeof(crc32)` and `dstLen >= srcLen`, decrypts the entire source, then validates the CRC over all but the trailing four bytes.

## State and Persistence Behavior

The implementation has no per-message persistent state. `XrdCryptoLite_New_bf32()` contains a static provider-loader object so OpenSSL provider loading runs once per process. The cipher IV is always all zeros, making encryption deterministic for the same key/plaintext.

## Dependencies and Integration Points

It depends on OpenSSL EVP/provider APIs, `XrdOucCRC`, byte-order helpers, and `XrdSysHeaders`. It is selected by `XrdCryptoLite::Create("bf32")`.

## Risks and Edge Cases

The code does not check `EVP_CIPHER_CTX_new()` or EVP call return values before use. A fixed zero IV and Blowfish are legacy choices and should not be treated as modern confidentiality protection. If OpenSSL 3 legacy provider loading fails, cipher initialization may fail silently. `EVP_DecryptFinal_ex()` writes to `dst` rather than `dst + wLen`, though CFB mode with padding disabled normally produces no final bytes.

## Test Signals

Tests should cover encrypt/decrypt round trips, CRC corruption detection, short destination rejection, large-message heap path, OpenSSL 3 provider availability, unsupported/invalid key lengths, and deterministic ciphertext behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite_bf32.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoMsgDigest.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoMsgDigest.cc

## Purpose

`XrdCryptoMsgDigest.cc` provides the abstract message-digest base implementation and equality comparison for digest buffers.

## Important APIs and Functions

`IsValid()`, `Reset()`, `Update()`, and `Final()` are abstract stubs that log diagnostics and return failure defaults. `operator==` compares two digest objects by length and byte content using inherited `Length()` and `Buffer()`.

## Control Flow

Concrete digest implementations perform actual digest lifecycle operations. The base equality method succeeds only when lengths match and `memcmp()` over the digest buffer is zero.

## State and Persistence Behavior

Digest bytes and type state are inherited from `XrdCryptoBasic`; concrete implementations may maintain additional hash context.

## Dependencies and Integration Points

It depends on `XrdCryptoAux.hh` and `XrdCryptoMsgDigest.hh`. Factories construct concrete digest implementations for protocol/authentication code.

## Risks and Edge Cases

`operator==` takes its parameter by value, but `XrdCryptoMsgDigest` inherits raw owning pointers and lacks a safe copy constructor; passing by value can trigger shallow-copy double-free or other lifetime bugs if the default copy is used. The comparison is not constant-time.

## Test Signals

Tests should avoid value-copy hazards by changing/covering the operator contract, compare equal and unequal digest buffers, and verify concrete digest lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoMsgDigest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoMsgDigest.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoMsgDigest.hh

## Purpose

`XrdCryptoMsgDigest.hh` declares the abstract interface for message digest implementations in the crypto plugin architecture.

## Important APIs and Types

The class inherits `XrdCryptoBasic` and declares `IsValid()`, `Reset(const char *)`, `Update(const char *, int)`, `Final()`, and `operator==`.

## Control Flow

Consumers reset a digest to a named algorithm, feed data with `Update()`, finalize into the inherited buffer, and compare or inspect the result.

## State and Persistence Behavior

Base state is inherited buffer/type storage; concrete implementations add hash context and validity state.

## Dependencies and Integration Points

It depends on `XrdCryptoBasic.hh` and is constructed through `XrdCryptoFactory::MsgDigest()`.

## Risks and Edge Cases

The equality operator's by-value parameter is unsafe for a raw-pointer-owning hierarchy and can cause accidental copies. Implementations must specify whether `Reset()` can be called after `Final()`.

## Test Signals

Tests should verify common digest algorithms, reset/update/final sequencing, and object-copy prevention or safe semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoMsgDigest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoRSA.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoRSA.cc

## Purpose

`XrdCryptoRSA.cc` implements the abstract RSA base defaults plus bucket/string convenience wrappers for public/private key export and encryption/decryption.

## Important APIs and Functions

The base virtual methods (`Dump`, `Opaque`, output length queries, import/export, and raw encrypt/decrypt methods) log `ABSTRACTMETHOD` and fail. `ExportPublic(XrdOucString &)`, `ExportPrivate(XrdOucString &)`, and bucket wrappers allocate temporary buffers based on concrete output lengths, call raw virtual methods, and update the target string or bucket on success.

## Control Flow

Export wrappers request a concrete length, allocate one extra byte for NUL termination, zero-fill, call concrete export, copy into `XrdOucString`, and delete the temporary. Bucket wrappers allocate `GetOutlen(bck.size)`, perform the selected raw RSA operation, and update the bucket if the result size is nonnegative.

## State and Persistence Behavior

The base class stores only `status`, with static string names `Invalid`, `Public`, and `Complete`. Concrete subclasses own key material and opaque backend objects.

## Dependencies and Integration Points

It depends on `XrdCryptoRSA.hh`, `XrdSutBucket`, and `XrdOucString`. Factories create concrete RSA objects for key exchange, signing-like operations, and certificate handling.

## Risks and Edge Cases

The bucket wrappers rely on `GetOutlen()` returning positive sane lengths; zero or negative lengths can lead to bad allocation behavior. On raw operation failure, wrappers delete the temporary buffer; on success they assume `XrdSutBucket::Update()` assumes ownership. RSA operation naming exposes private-key encryption/public-key decryption patterns that need careful use as signature primitives rather than confidentiality.

## Test Signals

Concrete RSA tests should cover key generation/import/export, public-only versus complete status, all bucket wrappers, failure cleanup, and max input size behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoRSA.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoRSA.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoRSA.hh

## Purpose

`XrdCryptoRSA.hh` declares the abstract RSA public-key interface used by XRootD crypto plugins.

## Important APIs and Types

`XrdCryptoRSAdata` is an opaque backend pointer. `ERSAStatus` tracks invalid, public-only, and complete key states. The interface exposes opaque access, dumping, output lengths, import/export of public/private keys, string export helpers, raw public/private encrypt/decrypt methods, and bucket wrappers.

## Control Flow

Consumers obtain an RSA object from a factory, import or generate key material, then use raw or bucket APIs depending on protocol serialization needs.

## State and Persistence Behavior

The base stores `status`; concrete implementations own backend key state. Status strings are exposed through `Status()`.

## Dependencies and Integration Points

It depends on `XrdSutBucket`, `XrdOucString`, and `XrdCryptoAux.hh`. X.509 objects expose certificate public keys as `XrdCryptoRSA`.

## Risks and Edge Cases

The class is non-copy-safe by default because concrete subclasses may own opaque resources. The interface uses signed lengths and raw buffers, so callers must respect implementation limits.

## Test Signals

Tests should verify status transitions, export/import round trips, and error behavior for using private operations on public-only keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoRSA.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoTrace.hh

## Purpose

`XrdCryptoTrace.hh` defines tracing macros for the crypto subsystem around the global `cryptoTrace` pointer and trace masks from `XrdCryptoAux.hh`.

## Important APIs and Types

Macros include `QTRACE`, `PRINT`, `TRACE`, `DEBUG`, and `EPNAME` when `NODEBUG` is not defined. In no-debug builds they expand to no-ops. `cryptoTrace` is declared as an external `XrdOucTrace *`.

## Control Flow

Call sites set `EPNAME()` and then use trace macros. `PRINT()` writes through `cryptoTrace->Beg()`/`End()` and `std::cerr` when tracing is initialized.

## State and Persistence Behavior

Runtime trace state is process-global through `cryptoTrace` and its `What` mask. This header itself owns no state.

## Dependencies and Integration Points

It depends on `XrdOucTrace`, `XrdCryptoAux.hh`, and `XrdSysHeaders` in debug builds. It is used by factory, X.509, and request/chain code.

## Risks and Edge Cases

Trace expressions must not carry side effects because they disappear under `NODEBUG`. `PRINT()` silently does nothing when `cryptoTrace` has not been initialized by `XrdCryptoSetTrace()`.

## Test Signals

Build tests should compile with both debug and `NODEBUG`. Runtime tests should initialize trace flags and verify category filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509.cc

## Purpose

`XrdCryptoX509.cc` implements common abstract X.509 certificate behavior: type names, generic validity checks, diagnostic dumping, hostname wildcard matching, and default stubs for implementation-specific operations.

## Important APIs and Functions

`Dump()` prints certificate file, type, serial, subject/issuer names and hashes, validity interval, and PKI status. `IsValid(int when)` checks current or supplied time against `NotBefore() - 600 seconds` and `NotAfter()`. `IsExpired()` checks only `NotAfter()`. Most accessors (`BitStrength`, time/name/hash/key/extension/export/verify methods) are abstract stubs. `MatchHostnames()` lowercases pattern and hostname, supports wildcard matching in the first DNS label, and requires remaining labels to match exactly.

## Control Flow

Generic validity delegates certificate-specific times to concrete subclasses. Dumping calls multiple virtual methods and formats local-time strings. Hostname matching first checks exact equality, then tokenizes the first label and applies `XrdOucString::matches()` to that label only.

## State and Persistence Behavior

The base stores `type` only. It uses static type-name strings and a fixed allowed clock skew of 600 seconds.

## Dependencies and Integration Points

It depends on `XrdCryptoX509.hh`, `XrdCryptoTrace.hh`, `XrdCryptoRSA`, `XrdSutBucket`, and `XrdOucString`. Concrete OpenSSL implementations provide the cryptographic data.

## Risks and Edge Cases

`Dump()` assumes validity times can be converted and that `asctime_r` output is nonempty before trimming the trailing newline. `MatchHostnames()` allows patterns such as `F*.com`, which may be broader than modern certificate hostname rules. Abstract stubs return failure values that can mask missing overrides until runtime.

## Test Signals

Tests should cover validity skew, expired/not-yet-valid certs, wildcard SAN hostname matching, exact case-insensitive matches, and concrete override completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509.hh

## Purpose

`XrdCryptoX509.hh` declares the abstract representation of one X.509 certificate in the XRootD crypto layer.

## Important APIs and Types

`EX509Type` distinguishes CA, end-entity certificate, proxy, and unknown. The interface exposes validity/expiration, opaque backend access, RSA key access, export, dump/extension dump, parent file, proxy type, bit strength, serial number, validity interval, issuer/subject names and hashes, SAN hostname matching, extension lookup, signature verification, and static hostname matching.

## Control Flow

Consumers and chain validators call generic base methods where possible and rely on concrete plugin overrides for backend-specific certificate parsing and cryptographic verification.

## State and Persistence Behavior

The base stores only the certificate type. Concrete implementations manage certificate handles and associated key objects.

## Dependencies and Integration Points

It depends on XRootD protocol integer types, `XrdSutBucket`, and `XrdCryptoRSA`. `XrdCryptoX509Chain`, CRLs, requests, and factories all depend on this interface.

## Risks and Edge Cases

The abstract interface exposes many borrowed `const char *` values whose lifetime depends on concrete implementations. `MatchesSAN()` is pure virtual, so all concrete cert classes must implement SAN parsing correctly for TLS hostname verification.

## Test Signals

Tests should validate concrete certificate parsing, SAN matching, serial string handling, extension lookup, export/import, and signature verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Chain.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Chain.cc

## Purpose

`XrdCryptoX509Chain.cc` implements a lightweight singly linked list of `XrdCryptoX509` certificates plus generic chain ordering, CA discovery, validity checking, and signature verification.

## Important APIs and Functions

Constructors initialize empty or single-certificate chains and copy chain node topology without copying certificates. `Cleanup()` deletes nodes and optionally certificate objects. `CheckCA()` finds a valid CA, verifies self-signature unless configured otherwise, moves it to the front, and records CA name/hash/status. `PutInFront()`, `InsertAfter()`, `PushBack()`, and `Remove()` mutate list topology. `SearchByIssuer()`/`SearchBySubject()` and their private finders support exact, prefix, and suffix modes. `Reorder()` arranges certificates so each node signs the next. `Verify()` reorders, checks path depth, validates a CA, then verifies each subsequent certificate against the previous signer. Internal `Verify()` enforces presence, type, CRL revocation if supplied, time validity, and signature verification. `CAname()`, `EECname()`, `CAhash()`, and `EEChash()` lazily derive cached names.

## Control Flow

Generic verification starts by reordering the chain, interpreting `x509ChainVerifyOpt_t` options, checking path depth, finding/verifying the CA, then walking signer/certificate pairs from top to bottom. `Reorder()` first finds a top-most certificate whose issuer is not present, moves it to the front, then repeatedly finds children whose issuer matches the current subject.

## State and Persistence Behavior

The chain owns nodes but not necessarily certificates unless `Cleanup()` is called. It caches iterator state (`current`, `previous`), endpoints (`begin`, `end`), effective CA, size, last error text, CA/EEC names and hashes, and CA status. Copy construction shares certificate pointers, so ownership must be external or carefully managed.

## Dependencies and Integration Points

It depends on `XrdCryptoX509`, `XrdCryptoX509Crl`, `XrdSutBucket`, `XrdOucString`, and crypto trace macros. `XrdCryptogsiX509Chain` subclasses it to enforce GSI proxy rules.

## Risks and Edge Cases

`InsertAfter()` does not unlink an existing node before inserting it after a new parent, so moving existing certificates can corrupt list topology. `PushBack()` deletes duplicate certificate pointers passed by caller, creating surprising ownership behavior. Suffix matching computes `strlen(pi) - strlen(issuer)` without guarding negative values. Generic `Verify()` sets a path-depth error but does not immediately return, so later checks can overwrite or ignore it. Iterator state makes concurrent iteration unsafe.

## Test Signals

Tests should cover unordered chains, sub-CA chains, duplicate insertion, remove while iterating, absent/invalid CA, CRL revocation, expired certs, path depth failures, prefix/suffix searches with short strings, and copy/cleanup ownership scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Chain.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Chain.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Chain.hh

## Purpose

`XrdCryptoX509Chain.hh` declares the certificate-chain container and generic verification API used by XRootD crypto code.

## Important APIs and Types

`x509ChainVerifyOpt_t` carries option bits, verification time, max path length, and optional CRL. Option bits include `kOptsCheckSelfSigned` and `kOptsCheckSubCA`. `XrdCryptoX509ChainNode` stores one certificate pointer and next node. `XrdCryptoX509Chain` exposes CA status, error codes, dump/accessors, list modifiers, CA checking, cleanup, subject/issuer search, validity checking, reordering, verification, and pseudo-iterator methods.

## Control Flow

Users build a chain, optionally reorder/check validity, and call `Verify()` with options. Iterator methods use internal state instead of external iterator objects.

## State and Persistence Behavior

Protected members store linked-list pointers, iterator state, effective CA, size, last error, cached names/hashes, and CA status. Node destructors do not delete certificates; cleanup semantics are explicit.

## Dependencies and Integration Points

It depends on `XrdSutBucket`, `XrdCryptoX509`, and `XrdCryptoX509Crl`. It is the base for GSI-specific validation and uses concrete certificate implementations provided by crypto plugins.

## Risks and Edge Cases

Ownership is ambiguous: destructor deletes nodes only, while `Cleanup()` can delete certificate contents. Copy construction shares certificate pointers. The internal iterator is not reentrant.

## Test Signals

Tests should validate ownership expectations, iterator behavior, error-code mapping, and verification options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Chain.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Crl.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Crl.cc

## Purpose

`XrdCryptoX509Crl.cc` provides abstract default behavior for X.509 certificate revocation lists.

## Important APIs and Functions

Most methods (`Dump`, `IsValid`, update time accessors, parent file, issuer/hash, opaque access, signature verification, and serial revocation checks) are abstract stubs. `IsExpired(int when)` is implemented generically by comparing the current or supplied time with `NextUpdate()`.

## Control Flow

Concrete CRL implementations supply parsing, validity, issuer, and revocation behavior. Generic expiration is a simple time comparison.

## State and Persistence Behavior

The base class stores no state. Concrete subclasses own backend CRL handles.

## Dependencies and Integration Points

It depends on `XrdCryptoX509Crl.hh` and `XrdCryptoX509`. Chain verification can pass a CRL to reject revoked certificates.

## Risks and Edge Cases

The default `IsRevoked()` stubs return true, a fail-closed behavior if a concrete override is missing. `IsExpired()` depends on `NextUpdate()` returning a valid epoch value; the abstract default returns `-1`, making the base appear expired.

## Test Signals

Tests should verify concrete CRL parsing, expiration, issuer signature verification, serial-number string/int revocation checks, and fail-closed behavior when revocation cannot be determined.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Crl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Crl.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Crl.hh

## Purpose

`XrdCryptoX509Crl.hh` declares the abstract X.509 CRL interface used for revocation checking in certificate-chain validation.

## Important APIs and Types

`XrdCryptoX509Crldata` is an opaque backend pointer. The class exposes validity/expiration, opaque access, dumping, parent file, update times, issuer name/hash, serial-number revocation checks by integer or string, and signature verification against a certificate.

## Control Flow

Chain verification supplies a CRL to generic or GSI verification, which calls `IsRevoked()` for certificates under examination.

## State and Persistence Behavior

No base state is stored. Concrete implementations manage parsed CRL data and backend resources.

## Dependencies and Integration Points

It depends on `XrdCryptoX509.hh`. Factories construct CRL instances from files or CA certificates.

## Risks and Edge Cases

Implementations must define serial-number string formats consistently with certificate `SerialNumberString()`. Expired CRLs must be rejected by callers or `IsValid()`.

## Test Signals

Tests should cover CRL validity intervals, revoked/non-revoked serials, issuer matching, and signature verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Crl.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Req.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Req.cc

## Purpose

`XrdCryptoX509Req.cc` implements shared behavior and abstract defaults for X.509 certificate-signing requests.

## Important APIs and Functions

`Dump()` prints subject, subject hash, and PKI status through trace macros. `IsValid()`, `Subject()`, `SubjectHash()`, `Opaque()`, `PKI()`, `GetExtension()`, `Export()`, and `Verify()` are abstract stubs returning failure or null defaults.

## Control Flow

Concrete request implementations supply parsing, export, key retrieval, extension lookup, and signature verification. Dumping delegates to those virtual methods and handles missing PKI.

## State and Persistence Behavior

The base class stores a plugin/request `version` value via the header constructor. Concrete subclasses own backend request data.

## Dependencies and Integration Points

It depends on `XrdCryptoX509Req.hh` and `XrdCryptoTrace.hh`. Proxy creation hooks in `XrdCryptoFactory` create and sign request objects.

## Risks and Edge Cases

`Dump()` assumes `Subject()` and `SubjectHash()` are safe to stream even if concrete methods return null. Missing overrides fail only at runtime via diagnostics.

## Test Signals

Tests should cover concrete request validity, subject/hash extraction, export/import bucket behavior, version propagation, and signature verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Req.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Req.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Req.hh

## Purpose

`XrdCryptoX509Req.hh` declares the abstract interface for certificate-signing requests used mainly by proxy certificate workflows.

## Important APIs and Types

`XrdCryptoX509Reqdata` is an opaque backend pointer. The class exposes validity, opaque access, request public key access, bucket export, dump, subject and subject hash, extension lookup, signature verification, and a simple integer version field.

## Control Flow

Consumers obtain request objects through factory hooks, inspect/export them, and pass them into proxy-signing functions.

## State and Persistence Behavior

The base stores only `version`, initialized by the constructor and managed by `Version()`/`SetVersion()`. Concrete implementations manage backend request data.

## Dependencies and Integration Points

It depends on `XrdSutBucket` and `XrdCryptoRSA`. Factory proxy hooks use this type for create/sign request operations.

## Risks and Edge Cases

The interface exposes borrowed string pointers and opaque backend data. Implementations must keep these valid for the request lifetime.

## Test Signals

Tests should verify version metadata, request export, extension access, and interoperability with proxy signing hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Req.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptogsiX509Chain.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptogsiX509Chain.cc

## Purpose

`XrdCryptogsiX509Chain.cc` implements GSI-specific certificate-chain verification on top of the generic X.509 chain, including sub-CA handling, end-entity certificate requirements, proxy certificate rules, RFC 3820 extension checks, and proxy path-length enforcement.

## Important APIs and Functions

`Verify(EX509ChainErr &, x509ChainVerifyOpt_t *)` overrides generic verification. It requires at least CA plus EEC/subCA, reorders the chain, reads options (`kOptsRfc3820`, `kOptsCheckSubCA`, path length, CRL, verification time), verifies the top CA, verifies any sub-CAs, optionally returns for sub-CA-only validation, verifies a single EEC, rejects multiple EECs, then walks proxy certificates. `SubjectOK()` enforces proxy subject naming: subject must start with issuer or issuer without the trailing proxy CN, must append exactly one `CN=`.

## Control Flow

Proxy verification checks certificate type, subject naming, optional RFC 3820 `ProxyCertInfo` extension via factory hook, path-length constraints, and then generic signature/time/type verification. Path length is decremented across CA/subCA/EEC/proxy traversal and tightened by proxy extension constraints when present.

## State and Persistence Behavior

The subclass reuses protected chain state (`begin`, `size`, `statusCA`, `lastError`) and stores a non-owning `XrdCryptoFactory *cfact` used to query proxy extension hooks. It mutates CA status and last-error text during verification.

## Dependencies and Integration Points

It depends on `XrdCryptoFactory`, proxy OID constants and hook typedefs, `XrdCryptoX509Chain`, CRLs, and trace macros. It is used by GSI authentication/proxy validation paths.

## Risks and Edge Cases

If `kOptsRfc3820` is set and `cfact` or `ProxyCertInfo()` is null, the code can dereference a null function pointer because the compound condition calls `(*(cfact->ProxyCertInfo()))` after only checking `cfact`. Path-depth errors are recorded but not returned immediately before later validation. The proxy loop exits when `plen == 0` even if unprocessed nodes remain, then returns success, so tests should verify over-depth proxies are rejected as intended. Subject parsing uses substring searches for `/CN=` and `CN=` and may accept malformed distinguished names.

## Test Signals

Tests should cover CA+EEC, sub-CA-only mode, multiple EEC rejection, non-proxy after EEC rejection, RFC 3820 extension missing/present, path-length constraints from options and extensions, proxy subject naming variants, CRL revocation, and null factory hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptogsiX509Chain.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptogsiX509Chain.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptogsiX509Chain.hh

## Purpose

`XrdCryptogsiX509Chain.hh` declares the GSI policy-enforcing subclass of `XrdCryptoX509Chain`.

## Important APIs and Types

`kOptsRfc3820` enables required proxy-certificate extension validation. `XrdCryptogsiX509Chain` constructors accept an optional initial certificate or chain plus an optional `XrdCryptoFactory *`. The class overrides `Verify()` and keeps `SubjectOK()` private for proxy naming rules.

## Control Flow

Users build or copy a chain, provide a factory capable of proxy extension parsing, and call `Verify()` with GSI options. The subclass delegates generic cryptographic checks to the base and adds GSI sequencing/proxy checks.

## State and Persistence Behavior

The only new state is the non-owning `cfact` pointer. All list and cache state is inherited from `XrdCryptoX509Chain`.

## Dependencies and Integration Points

It depends on `XrdCryptoX509Chain.hh` and forward-declares `XrdCryptoFactory`. It integrates with GSI authentication and OpenSSL plugin proxy hooks.

## Risks and Edge Cases

The factory pointer lifetime must outlive verification calls. Without a proxy-info-capable factory, RFC 3820 checks cannot be performed.

## Test Signals

Tests should instantiate the subclass with null and real factories, verify option handling, and ensure inherited chain ownership rules remain clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptogsiX509Chain.hh -->
