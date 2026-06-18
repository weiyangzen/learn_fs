# subset-b-008497 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Net2.cpp -->
# sources/storage-engines/foundationdb/flow/Net2.cpp research

## Purpose

`Net2.cpp` is the concrete, non-simulated Flow network implementation for FoundationDB. It binds the `INetwork` and `INetworkConnections` interfaces to Boost.Asio sockets, TLS contexts, UDP sockets, timers, main-thread task scheduling, DNS resolution, run-loop metrics, slow-task detection, and platform reactor integration. The file is the production path behind `newNet2(...)`, creating a global `N2::Net2` instance that owns the Asio `io_context`, the Flow `TaskQueue`, TLS handshaker side threads, metrics, DNS cache refresh actor, and the state used by `delay`, `yield`, `onMainThread`, `connect`, and `listen`.

## Important APIs, types, and functions

The central type is `N2::Net2 final : public INetwork, public INetworkConnections`. Public methods implement connection creation (`connect`, `connectExternal`, `connectExternalWithHostname`), UDP creation (`createUDPSocket`), listening (`listen`), DNS lookup (`resolveTCPEndpoint*`), scheduling (`delay`, `orderedDelay`, `yield`, `check_yield`, `onMainThread`), lifecycle (`run`, `stop`, `addStopCallback`, `checkRunnable`), and platform services (`getDiskBytes`, `isAddressOnThisHost`, `startThread`, `protocolVersion`, `global`/`setGlobal`).

`Connection` implements plaintext `IConnection` with a `tcp::socket`, nonblocking `read`/`write`, null-buffer readiness probes, and socket setup for `TCP_NODELAY`, optional Linux `TCP_QUICKACK`, and close-on-exec. `SSLConnection` wraps a `tcp::socket` in `boost::asio::ssl::stream`, applies `TLSPolicy`, tracks whether the peer verified, supports client SNI via `connectWithHostname`, and gates TLS handshakes with `networkInfo.handshakeLock` plus client/server throttling maps. `Listener` and `SSLListener` are `IListener` acceptors that construct the corresponding connection type. `UDPSocket` implements `IUDPSocket` for connected or unconnected UDP sockets and exposes `receive`, `receiveFrom`, `send`, `sendTo`, `bind`, `localAddress`, and `native_handle`.

`BindPromise` and `ReadPromise` adapt Boost.Asio callbacks into Flow `Promise`/`Future` results while translating errors to `connection_failed`, `bind_failed`, `address_in_use`, `invalid_local_address`, or `lookup_failed`. `SSLHandshakerThread` is an `IThreadPoolReceiver` used to run blocking TLS handshakes on background threads when configured or when the main-thread handshake pool is saturated. `ASIOReactor` wraps `io_context::run_one`, `poll_one`, and a timer used for sleeping. `SendBufferIterator` adapts Flow `SendBuffer` chains into Boost.Asio `const_buffer` ranges for scatter/gather writes.

## Control flow

Construction initializes Flow globals for metrics, `INetworkConnections`, the Asio service, blob credential files, proxy state, and Linux eventfd when present. `run()` marks the network thread, starts the coordinator DNS refresh actor, optionally starts Flow profiling, and enters a loop until `stopped` becomes true. Each iteration optionally invokes the global run-cycle function, computes sleep time from the task queue, sleeps through the reactor, polls Asio events, updates `currentTime`, processes timers and thread-ready tasks, then executes ready `PromiseTask`s until the queue empties or `check_yield` forces a break. Metrics and starvation trackers are updated around run-cycle, reactor, idle, and task priorities. Stop callbacks and a final simple-counter report run after the loop exits.

Connection control flow is actor-shaped. Plain TCP `Connection::connect` starts `async_connect`, awaits the callback future, then calls `init`; failed or cancelled connects close the socket. `Listener::doAccept` starts `async_accept`, converts the peer endpoint to `NetworkAddress`, calls `Connection::accept`, and returns the connection. TLS uses the same socket accept/connect setup but separates TCP establishment from `connectHandshake`/`acceptHandshake`. The handshake wrappers acquire the shared handshake lock, start either an async main-thread handshake or a blocking side-thread handshake, enforce `CONNECTION_MONITOR_TIMEOUT`, update success/timeout counters, and add failures to throttling state.

DNS lookup is split into `resolveTCPEndpoint_impl`, which owns a local resolver and maps endpoints to Flow `NetworkAddress`, and cache-aware wrappers. `coordinatorDNSCacheRefresh` periodically refreshes or evicts cache entries when `ENABLE_COORDINATOR_DNS_CACHE` is set. `isAddressOnThisHost` probes routing by connecting a temporary UDP socket to the target IP and comparing the selected local endpoint; results are cached and bounded.

## State and persistence behavior

Most state is in-memory runtime state. `Net2` keeps task queues, `currentTime`, TLS policy/context, TLS background actors, DNS cache, address-on-host cache, Flow globals, metric handles, starvation trackers, stop callbacks, and optional blob/proxy configuration. TLS certificate refresh uses `watchFileForChanges` on configured certificate/key/CA paths and replaces `sslContextVar` plus `activeTlsPolicy` after a successful reload, so new TLS connections pick up refreshed credentials. No durable application data is written here; persistent effects are trace logs, metrics, possible TLS file watches, and OS socket/resource state.

The global singleton `N2::g_net2`, thread-local `thread_network`, and Linux profiling globals are process-lifetime state. `stopImmediately` clears queued tasks and marks the network stopped, but intentionally does not perform deep resource cleanup for every process-lifetime object. The DNS and address caches are opportunistic and may be cleared or evicted without persistence.

## Dependencies and integration points

This file depends heavily on Boost.Asio (`io_context`, TCP/UDP sockets, resolver, timers, SSL stream/context), Flow actor/future primitives, `TaskQueue`, `IConnection`, `IUDPSocket`, `IThreadPool`, `TLSConfig`/`TLSPolicy`, `WatchFile`, `ProtocolVersion`, `SendBufferIterator`, `ChaosMetrics`, `TDMetric`, `SimpleCounter`, and `TraceEvent`. It calls platform helpers from `Platform.cpp` for timers, disk bytes, threads, close-on-exec, yielding, and profiling toggles. Network-wide state comes through `g_network->networkInfo`, including TLS throttling maps, metrics, and handshake flow locks.

Integration is broad: storage/server layers call `g_network` methods for scheduling, timers, connections, and listener creation; TLS configuration is supplied at `newNet2`; Swift jobs are optionally enqueued through `_swiftEnqueue`; profiler setup in `Platform.cpp` consumes `net2RunLoopIterations`, `net2RunLoopSleeps`, and the backtrace buffers initialized in this file.

## Risks and edge cases

Run-loop behavior is latency critical. Regressions in `check_yield`, `TaskQueue` ordering, or `reactor.sleep` can starve higher-priority actors or inflate latency. `currentTime` is atomic but many other fields assume network-thread ownership. `onMainThread` is cross-thread and relies on `TaskQueue::addReadyThreadSafe` plus `reactor.wake`; missed wakes can hang callbacks.

TLS behavior has several risk points: handshakes may run on the main thread when side-thread capacity is full, throttling maps must be keyed consistently for client versus server paths, failed handshakes must close sockets without double-completing promises, and certificate reload swaps context/policy for future accepts while existing connections continue with their original context. SNI setup calls both `SSL_set_tlsext_host_name` and hostname verification flags; failures are traced but not explicitly rejected before the handshake result.

Boost.Asio null-buffer readiness probes and nonblocking `read_some`/`write_some` rely on correct translation of `would_block` to zero-byte progress. The code asserts that successful reads/writes send nonzero bytes, so empty buffer chains or unexpected EOF semantics are fatal in debug builds. DNS filtering excludes IPv6 loopback in async resolution but not in the blocking resolver, which is a subtle behavior difference. `isAddressOnThisHost` can log warnings and cache false on routing/socket errors.

## Test signals

Inline tests cover `ThreadSafeQueue` basic behavior, multi-threaded queue ordering, and FIFO behavior for `onMainThread` scheduling. Comments suggest running random unit tests with `fdbserver -r test -f tests/noSim/RandomUnitTests.toml` or `fdbserver -r unittests -f noSim`. Additional useful signals are TLS connect/listen tests, DNS-cache refresh/eviction tests, socket failure injection, noSim latency/slow-task profiling checks, and metrics assertions for `CountReads`, `CountWrites`, `CountYields`, TLS handshake counters, and run-loop callback counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Net2.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Net2Packet.cpp -->
# sources/storage-engines/foundationdb/flow/Net2Packet.cpp research

## Purpose

`Net2Packet.cpp` implements packet-buffer bookkeeping for Flow's network serialization path. It is concerned with writing serialized bytes across chained `PacketBuffer` objects, reserving split write space, tracking unsent buffers, and maintaining a list of reliable packets that can be compacted or discarded. The code is low-level infrastructure used by packet-oriented network layers rather than user-facing protocol logic.

## Important APIs, types, and functions

`PacketWriter::init` attaches a writer to a `PacketBuffer` and optional `ReliablePacket`, initializes length accounting relative to current `bytes_written`, and addrefs the buffer for reliable resend tracking. `PacketWriter::finish` finalizes length and reliable-packet end offsets. `serializeBytesAcrossBoundary` copies a byte range over as many buffers as needed. `nextBuffer` allocates a new `PacketBuffer` and extends the reliable `cont` chain when reliability is enabled. `writeAhead` reserves exactly a requested number of bytes, possibly split between current and next buffer, and returns a `SplitBuffer` describing the writable spans.

`SplitBuffer::write`, `write(data, len, offset)`, and `writeAndShrink` copy bytes into one or two reserved spans. `ReliablePacket::insertBefore` and `remove` manage the circular reliable-packet list and delete a packet plus its continuation chain while dropping buffer references. `UnsentPacketQueue::sent` advances `bytes_sent`, removes fully sent buffers, samples queue latency, and delrefs completed buffers. `UnsentPacketQueue::discardAll` drops all unsent buffers. `ReliablePacketList::compact` copies already-sent reliable ranges into a new packet-buffer chain and rewrites reliable packet metadata to point at compacted buffers. `ReliablePacketList::discardAll` repeatedly removes reliable packets from the sentinel list.

## Control flow

The normal write path starts with `UnsentPacketQueue::getWriteBuffer`, then `PacketWriter::init`, serialization calls, and `PacketWriter::finish`. If serialization exceeds the current buffer, `nextBuffer` appends a new buffer and, when reliable tracking is active, creates a continuation `ReliablePacket` for the new buffer segment. Later, socket write completion calls `UnsentPacketQueue::sent(bytes)`, which consumes bytes from the front buffer and releases whole buffers as they become fully sent. For reliable data, connection close/retry code can use `ReliablePacketList::compact(into, stopAt)` to copy sent reliable bytes into a compact chain while stopping before the still-unsent range.

## State and persistence behavior

All state is in memory and reference-counted through `PacketBuffer::addref`/`delref`. `PacketWriter` temporarily owns current buffer, reliable pointer, and length accounting. `UnsentPacketQueue` owns a linked range of packet buffers from `unsent_first` to `unsent_last`; the last buffer may still have writable capacity. Reliable state is a circular linked list with a sentinel `ReliablePacket`, and each reliable packet may have a `cont` chain for bytes split across buffers. There is no durable persistence, but incorrect reference counting here can leak or prematurely free packet memory.

## Dependencies and integration points

The file depends on `flow/Net2Packet.h`, `PacketBuffer` from the serialization infrastructure, `Histogram` for queue latency, and Flow allocation/assertion helpers. It integrates with network connection send queues and resend/reconnect behavior. `SendBuffer`/packet serialization code writes into these buffers; socket completion code reports sent byte counts back into `UnsentPacketQueue`.

## Risks and edge cases

The code assumes byte counts are exact and positive where required. `writeAhead` handles only one boundary crossing because it allocates a next buffer sized for the remaining bytes; callers must respect the returned `SplitBuffer` size. `SplitBuffer` performs raw `memcpy` without bounds checks beyond caller-provided lengths. Reliable compaction mutates packet metadata while iterating and splits packets if the destination buffer has insufficient unwritten space; bugs there would corrupt resend data or leak references. `UnsentPacketQueue::sent` treats a fully written buffer that still has unwritten capacity and no next buffer specially, preserving the tail write buffer instead of dropping it.

## Test signals

There are no inline unit tests in this file. Useful tests should exercise serialization that exactly fills a buffer, crosses one boundary, crosses multiple boundaries through `serializeBytesAcrossBoundary`, uses `writeAhead` plus `SplitBuffer::writeAndShrink`, partially and fully drains `UnsentPacketQueue::sent`, and compacts reliable packets with and without packet splits. Histogram sampling on sent buffers is an observable metric signal for queue latency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Net2Packet.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/PKey.cpp -->
# sources/storage-engines/foundationdb/flow/PKey.cpp research

## Purpose

`PKey.cpp` implements Flow wrappers around OpenSSL `EVP_PKEY` public and private keys. It provides PEM/DER decode and encode, public-key extraction from private keys, algorithm identification, digital signing, and signature verification. The wrapper converts OpenSSL failures into FoundationDB `Error` types and rate-limited trace events while storing native key handles in `std::shared_ptr<EVP_PKEY>` with `EVP_PKEY_free` cleanup.

## Important APIs, types, and functions

The public API comes from `PKey.h`: `PKeyAlgorithm`, `pkeyAlgorithmName`, marker structs `PemEncoded` and `DerEncoded`, `PublicKey`, and `PrivateKey`. `PublicKey(PemEncoded, StringRef)` uses `PEM_read_bio_PUBKEY`; `PublicKey(DerEncoded, StringRef)` uses `d2i_PUBKEY`; `writePem` and `writeDer` use `PEM_write_bio_PUBKEY` and `i2d_PUBKEY`; `verify` delegates to `EVP_DigestVerify*`. `PrivateKey` constructors use `PEM_read_bio_PrivateKey` and `d2i_AutoPrivateKey`; `writePem` can optionally encrypt with `EVP_aes_256_cbc` when a password is supplied; `writeDer`, `writePublicKeyPem`, `writePublicKeyDer`, `sign`, `verify`, and `toPublic` expose private-key serialization and signing.

Private helpers `traceAndThrowDecode`, `traceAndThrowEncode`, and `traceAndThrowDsa` read one OpenSSL error from `ERR_get_error`, trace a warning with a suppressed event type, and throw `pkey_decode_error`, `pkey_encode_error`, or `digital_signature_ops_error`. `getPKeyAlgorithm` maps `EVP_PKEY_base_id` to RSA, EC, or unsupported. `doWritePublicKeyPem`, `doWritePublicKeyDer`, and `doVerifyStringSignature` centralize shared public/private operations.

## Control flow

Decode constructors assert non-empty input, create either a memory BIO or DER pointer, ask OpenSSL to parse the key, wrap the returned raw pointer, and reject unsupported algorithms. Encode methods allocate output in a Flow `Arena` after asking OpenSSL or a memory BIO for the encoded size. Signing initializes an `EVP_MD_CTX`, calls digest sign init/update, calls final once to compute signature length, allocates arena bytes, then calls final again to write the signature. Verification follows digest verify init/update/final and returns false for signature mismatch while throwing only for setup/update operational failures.

## State and persistence behavior

Each `PublicKey` or `PrivateKey` object holds shared ownership of an OpenSSL key. Encoded strings and signatures returned from write/sign operations are arena-backed `StringRef`s; callers must keep the `Arena` alive. The code does not persist keys itself. Password-protected private-key PEM output is generated only when the caller passes a non-empty password; the password bytes are copied into a local `std::vector<unsigned char>` for OpenSSL.

## Dependencies and integration points

This file depends on OpenSSL BIO, ERR, EVP, PEM, X509, object, and version headers; Flow `Arena`, `StringRef`, `AutoCPointer`, `Error`, and `TraceEvent`; and the error codes declared elsewhere in Flow. It integrates with TLS/certificate and token/signature code that needs key serialization, public-key distribution, or signature verification. Because it exposes `nativeHandle()`, lower layers can interoperate directly with OpenSSL when necessary.

## Risks and edge cases

Only RSA and EC keys are accepted; Ed25519, DSA, and other OpenSSL key types decode but are rejected as unsupported. `ERR_get_error` consumes a single error from OpenSSL's queue, so traces may omit deeper error stacks. Signature verification deliberately returns `false` for `EVP_DigestVerifyFinal` failure, which is correct for invalid signatures but may also hide some OpenSSL finalization errors if they are reported through the same return path. Arena lifetime is critical for all returned `StringRef` values. `PrivateKey::writePem` uses AES-256-CBC for password encryption; interoperability depends on OpenSSL defaults and caller expectations.

## Test signals

No inline unit tests are present in this file. Useful coverage includes RSA and EC PEM/DER round trips, unsupported algorithm rejection, encrypted and unencrypted private-key PEM writes, sign/verify success and tampered-signature failure across configured digests, `PrivateKey::toPublic` independence from the private key, and trace/error behavior for malformed PEM/DER input.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/PKey.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Platform.cpp -->
# sources/storage-engines/foundationdb/flow/Platform.cpp research

## Purpose

`Platform.cpp` is Flow's cross-platform OS abstraction and diagnostics implementation. It covers CPU, memory, disk, network, timer, random, file, path, directory, thread, allocation, temporary-file, crash, backtrace, dynamic-library, executable-path, and run-loop profiling services. It is shared infrastructure under the networking/runtime layer and hides platform differences among Linux, FreeBSD, macOS, and Windows.

## Important APIs, types, and functions

Resource-stat APIs include `getProcessorTimeThread`, `getProcessorTimeProcess`, `getResidentMemoryUsage`, `getMemoryUsage`, `getMachineRAMInfo`, `getDiskBytes`, `getNetworkTraffic`, `getMachineLoad`, `getDiskStatistics`, `getDeviceId`, and `getSystemStatistics`. Linux-specific helpers parse `/proc/self/statm`, `/proc/meminfo`, `/proc/zoneinfo`, `/proc/net/dev`, `/proc/net/snmp`, `/proc/stat`, and `/proc/diskstats`; Windows uses PDH counters; macOS uses Mach, sysctl, and IOKit.

Time APIs are `timer_monotonic`, `timer`, `timer_int`, `getLocalTime`, and `epochsToGMTString`, backed by platform-specific `OffsetTimer` implementations. Memory and allocation APIs include `setMemoryQuota`, `allocate`, `allocateInternal`, `mmapSafe`, `mprotectSafe`, large-page enablement, `platform::outOfMemory`, and allocation instrumentation initialization.

Filesystem/path APIs include `joinPath`, `renameFile`, `atomicReplace`, `deleteFile`, `platform::createDirectory`, `cleanPath`, `popPath`, `abspath`, `parentDirectory`, `basename`, `getUserHomeDirectory`, `findFiles`, `platform::listFiles`, `platform::listDirectories`, `platform::findFilesRecursively`, `platform::findFilesRecursivelyAsync`, `fileExists`, `directoryExists`, `fileSize`, `fileModifiedTime`, `readFileBytes`, `writeFileBytes`, and `writeFile`. `platform::TmpFile` manages a temporary file lifecycle.

Process/thread APIs include `threadSleep`, `threadYield`, `platform::setCloseOnExec`, `startThread`, `waitThread`, `setThreadPriority`, `platform::getEnvironmentVar`, `platform::setEnvironmentVar`, `platform::getWorkingDirectory`, `platform::getDefaultConfigPath`, `platform::getDefaultClusterFilePath`, `criticalError`, `flushAndExit`, `platformInit`, crash-handler registration, backtrace formatting, dynamic library load/unload/symbol lookup, `exePath`, `getExecPath`, `setupRunLoopProfiler`, and `stopRunLoopProfiler`.

## Control flow

`getSystemStatistics` is stateful across calls. It lazily allocates `SystemStatisticsState`, samples wall time and CPU clocks, computes deltas when initialized, records memory and disk capacity, then uses platform-specific counters to compute machine network, disk, and CPU deltas. On Unix, current counters are read from kernel interfaces and compared with the previous state. On Windows, PDH counters are initialized once and queried thereafter.

File replacement flow in `atomicReplace` creates a random temp file in the target directory, preserves ownership and mode on Unix when replacing an existing file, writes text or binary content, flushes, fsyncs/FlushFileBuffers outside simulation, closes, and renames/replaces atomically. Directory creation recursively creates missing path components. Path resolution uses `realpath` for existing prefixes and `cleanPath` for non-existing suffixes when `mustExist` is false.

Thread creation on Unix wraps user functions in `runFunc` so uncaught `std::exception`s print a backtrace and exit instead of silently killing the thread. Run-loop profiling on Linux installs a `SIGPROF` handler for the profiled network thread and starts a monitor thread that watches `net2RunLoopIterations` and `net2RunLoopSleeps`; it sends signals when the loop appears blocked or saturated, and `Net2::run` later harvests sampled backtraces.

Crash handling on Linux registers signal handlers for fatal signals, optionally `SIGTERM` under coverage builds, prints/traces the signal and stack, runs registered callbacks, flushes traces, restores the default action, and re-sends the signal. `criticalError` and `flushAndExit` provide explicit fatal exits with trace/stdout flushing and optional abort for core dumps.

## State and persistence behavior

Most state is process-local: static timers, PDH query handles, last sampled system-stat counters, large-page fallback flags, allocation-instrumentation buffers, crash-handler callbacks, profiling thread state, profiling counters, and temporary file names. Persistent side effects include file creation/replacement/deletion, directory tree deletion, temporary files, environment variable mutation, thread creation, memory quotas, and dynamic library loads. `atomicReplace` is the most persistence-sensitive function because it promises durable replacement outside simulation and preserves file metadata on Unix.

## Dependencies and integration points

The file depends on the platform C APIs (`pthread`, `mmap`, `getrusage`, `statvfs`, `getifaddrs`, `/proc`, `sysctl`, Mach, IOKit, Windows PDH/Win32), Boost filesystem/format/asio, Abseil stacktrace on non-Apple Unix, `fmt`, and many Flow helpers: `TraceEvent`, `Error`, `FaultInjection`, `Knobs`, `ScopeExit`, `SimpleCounter`, `StreamCipher`, `UnitTest`, and `Util`. `Net2.cpp` integrates with this file for timers, disk capacity, close-on-exec, thread start/wait, yielding, profiling toggles, and shared Linux profiling globals.

## Risks and edge cases

This file has high portability risk. Different platforms return different statistics and units, and some paths are explicitly less tested, such as FreeBSD disk stats. Kernel pseudo-file parsing can break if formats change or if containers expose partial cgroup/proc data. Several functions intentionally throw `platform_error` or `io_error` after tracing, so callers must be ready for system-level failures.

Filesystem correctness is subtle: `abspath(resolveLinks=false)` is asserted incomplete, `atomicReplace` must avoid leaving temp files or losing permissions, `createDirectory` handles races and historical kernel bugs, and recursive deletion uses `nftw`/`remove`. The crash and profiling signal handlers knowingly use operations that are not fully async-signal-safe because they run during fatal or diagnostic paths. `allocate` aborts through `platform::outOfMemory` when mmap/VirtualAlloc fails; guard pages change the returned pointer relative to the mapped region and must match deallocation expectations elsewhere.

## Test signals

Inline tests cover Linux memory-info parsing and extensive path/directory operations, including symlink resolution on Unix. Additional useful signals are platform-specific noSim tests for `atomicReplace` durability and permissions, temp-file lifecycle, directory recursion, environment access, random byte generation, thread wrapper exception behavior, memory quota failure paths, disk/network stat deltas, crash-handler smoke tests under controlled signals, dynamic library load/symbol lookup, and run-loop profiler enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Platform.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ProcessEvents.cpp -->
# sources/storage-engines/foundationdb/flow/ProcessEvents.cpp research

## Purpose

`ProcessEvents.cpp` implements a small process-local event registry for Flow. Callers can register RAII `ProcessEvents::Event` callbacks for one or more `StringRef` event names, trigger events with arbitrary `std::any` data and a Flow `Error`, and create uncancellable callbacks that intentionally live for process lifetime. The implementation is designed to be safe when callbacks add or remove events during a trigger, including reentrant triggers.

## Important APIs, types, and functions

The public API is `ProcessEvents::Event`, `ProcessEvents::uncancellableEvent`, and `ProcessEvents::trigger`. `EventImpl` stores the subscribed names and callback and uses its object address as a stable `Id`. `ProcessEventsImpl` owns `events`, an `unordered_map<StringRef, unordered_map<EventImpl::Id, EventImpl*>>`, plus deferred mutation maps `toRemove` and `toInsert`. The nested `Triggering` RAII helper increments the trigger depth on construction and, when the outermost trigger exits, applies pending removals and insertions back to `events`.

## Control flow

Constructing an `Event` allocates `EventImpl`, which immediately registers itself for every name. Destroying an `Event` removes the implementation from the registry and deletes it. If no trigger is active, add/remove operations mutate `events` directly. If a trigger is active, adds go to `toInsert`, and removes either erase a not-yet-visible pending insertion or record the event id/name list in `toRemove`.

`trigger(name, data, e)` creates a `Triggering` guard, finds callbacks registered for the name, and invokes each callback unless its id is already in `toRemove`. Callback exceptions are forbidden; any exception trips `UNSTOPPABLE_ASSERT(false)`. When nested triggers unwind to depth zero, `Triggering::~Triggering` removes deferred ids from each named event map, clears `toRemove`, merges all `toInsert` callbacks into `events`, and clears `toInsert`.

## State and persistence behavior

All state is process-local in the static `processEventsImpl`. There is no durable persistence. `uncancellableEvent` intentionally leaks an `EventImpl` by allocating it without a returned owner, making the callback live until process termination. Normal `Event` objects are RAII-managed and non-copyable. `StringRef` names are stored by value as references to external bytes, so callers must use stable string storage such as string literals or other lifetime-safe strings.

## Dependencies and integration points

The implementation depends on `flow/ProcessEvents.h`, Flow `StringRef`, `Error`, `NonCopyable`, assertions, and `UnitTest`. It uses STL `std::any`, `std::function`, `std::vector`, `std::unordered_map`, and `std::map`. It can be integrated by subsystems that need lifecycle hooks or process-wide notifications without introducing actor scheduling.

## Risks and edge cases

The biggest risk is lifetime: registered event names are `StringRef`s, not owning strings. Using temporary strings as event names would leave dangling references in the registry. The registry is not synchronized; it assumes single-threaded or externally serialized use. Mutating the callback map while iterating is handled through deferred maps, but callback ordering is unspecified because callbacks are stored in unordered maps. Exceptions in callbacks are fatal by assertion. `events[name].erase(id)` in removal paths can create empty maps for missing names; this is harmless but may leave empty event-name entries.

## Test signals

The inline unit test covers basic trigger delivery, adding callbacks during a trigger and verifying they do not run until later triggers, callbacks registered for multiple names, self-removal during a trigger, non-deleted callbacks continuing to run, and reentrant triggering with a temporary callback that must not run during the active trigger. Additional tests should cover destruction before first trigger, removal of a pending inserted event, uncancellable lifetime behavior, and invalid callback exception handling in debug builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ProcessEvents.cpp -->
