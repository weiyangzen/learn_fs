# Research: subset-b-007403 Hadoop common tests

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TestDomainSocket.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TestDomainSocket.java

Purpose: JUnit 5 integration coverage for Hadoop's native `DomainSocket` AF_UNIX wrapper. It validates socket lifecycle, path expansion, EOF, async close, socket attributes, client/server byte exchange, socketpair behavior, file descriptor passing, socket-path security, and shutdown semantics.

Important APIs/types/functions: `DomainSocket.bindAndListen`, `connect`, `socketpair`, `accept`, `close(true)`, `shutdown`, `getInputStream`, `getOutputStream`, `getChannel`, `sendFileDescriptors`, `recvFileInputStreams`, `validateSocketPathSecurity0`, `TemporarySocketDirectory`, `DomainChannel`, `SubjectInheritingThread`, and helper strategies `OutputStreamWriteStrategy`, `InputStreamReadStrategy`, `DirectByteBufferReadStrategy`, `ArrayBackedByteBufferReadStrategy`.

Control flow: setup creates a temporary socket directory and disables bind path validation; each test assumes native domain sockets loaded. The tests either bind/listen/connect, use socketpairs, or run two threads coordinating through `ArrayBlockingQueue`/`Future`. Descriptor passing creates real temporary files, sends their FDs with a byte payload, and validates received `FileInputStream`s. Path-security coverage mutates directory modes and checks expected exceptions.

State and persistence: uses temporary socket files, temporary data files, file descriptors, process umask/permission state, and global `DomainSocket` validation toggles. Resources are closed explicitly, though `PassedFile.finalize` is a fallback.

Dependencies/integration points: native Hadoop domain socket library, Unix filesystem permissions, `Shell.execCommand`, Hadoop `IOUtils`, Guava `Files`, JUnit assumptions/timeouts, and `SubjectInheritingThread`.

Risks: platform-sensitive and skipped when native loading fails; timing sleeps can be flaky; descriptor and socket leaks would affect later tests; permissions checks assume Unix semantics; direct and array-backed channel reads exercise buffer-position edge cases.

Test signals: success means AF_UNIX I/O, async close exceptions, receive timeout behavior, socketpair bidirectional messaging, FD passing, insecure path rejection, and half-shutdown EOF all work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TestDomainSocket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TestDomainSocketWatcher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TestDomainSocketWatcher.java

Purpose: Stress and lifecycle tests for `DomainSocketWatcher`, the background watcher that monitors domain sockets for close/readability notifications and invokes handlers.

Important APIs/types/functions: `DomainSocketWatcher`, `DomainSocketWatcher.Handler`, `DomainSocket.socketpair`, `watcher.add`, `watcher.remove`, `watcher.close`, `watcher.watcherThread`, `CountDownLatch`, `ReentrantLock`, `AtomicInteger`, and `SubjectInheritingThread`.

Control flow: each test is skipped if native domain sockets are unavailable. Simple cases create/close the watcher, add one side of a socketpair, close the peer, and wait for handler notification. Interruption tests interrupt the internal watcher thread. Stress tests concurrently add 250 sockets while another thread randomly closes peer sockets or removes watched sockets until every handler has fired.

State and persistence: state is in the native socket descriptors, watcher thread, watched-socket registry, `trappedException`, and local socketpair list. The `@AfterEach` hook turns any uncaught watcher-thread exception into a test failure.

Dependencies/integration points: native `DomainSocket`, watcher interrupt polling, Guava `Uninterruptibles`, SLF4J logging, and thread inheritance helper.

Risks: inherently concurrent and timing-sensitive; random removal/close order can expose races; native resource cleanup must be reliable; interruption must not leave the watcher thread hanging.

Test signals: verifies notifications are delivered, watched sockets close when watcher closes, thread interruption exits cleanly, and concurrent add/remove/close does not crash the watcher.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TestDomainSocketWatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestFrameDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestFrameDecoder.java

Purpose: Tests ONC/RPC TCP record-marking frame decoding and server-side integration with `RpcProgram` port monitoring.

Important APIs/types/functions: `RpcUtil.RpcFrameDecoder`, Netty `ByteBuf`, `XDR.isLastFragment`, `XDR.fragmentSize`, `SimpleTcpServer`, `SimpleTcpClient`, custom `TestRpcProgram`, `RpcCall`, `RpcAcceptedReply`, `RpcResponse`, and helpers `startRpcServer`, `createPortmapXDRheader`, `createGetportMount`.

Control flow: unit tests feed partial and complete record fragments directly to the decoder, checking that incomplete headers or bodies do not emit decoded frames and multiple fragments emit expected buffers. Integration tests start a random local RPC TCP server, send a large XDR request, and inspect static `resultSize` recorded by the program. The insecure-port test rejects non-null procedures when `allowInsecurePorts` is false but permits NULL procedure calls.

State and persistence: static `resultSize` is reset per client request. Server binding uses random ports with retry on `BindException`. Netty buffers are manually released in decoder unit tests.

Dependencies/integration points: Netty channel pipeline, Hadoop ONC/RPC framing, `RpcProgram` authorization/port monitoring, localhost TCP sockets, Mockito, and `GenericTestUtils` log-level control.

Risks: random port selection and live server threads can be flaky; static state makes parallel execution sensitive; direct buffer release must avoid leaks; the insecure-port assertion depends on client source port being unprivileged.

Test signals: confirms record fragments are buffered until complete, large requests preserve payload size, rejected calls do not reach handler data, and NULL procedure bypasses port monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestFrameDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcAcceptedReply.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcAcceptedReply.java

Purpose: Unit coverage for accepted ONC/RPC reply metadata and accept-state enum mapping.

Important APIs/types/functions: `RpcAcceptedReply`, `RpcAcceptedReply.AcceptState.fromValue`, `RpcReply.ReplyState`, `Verifier`, and `VerifierNone`.

Control flow: tests map wire values 0 through 5 to `SUCCESS`, `PROG_UNAVAIL`, `PROG_MISMATCH`, `PROC_UNAVAIL`, `GARBAGE_ARGS`, and `SYSTEM_ERR`; value 6 must throw. Constructor coverage verifies xid, message type, reply state, verifier reference, and accept state.

State and persistence: no persistent state; all objects are local immutable-style message instances.

Dependencies/integration points: ONC/RPC reply serialization model and JUnit assertions.

Risks: enum ordinal mapping is wire-protocol-sensitive; adding enum values without adjusting invalid-value tests can hide protocol drift.

Test signals: validates accepted-reply wire constants and constructor invariants for downstream RPC response handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcAcceptedReply.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcCall.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcCall.java

Purpose: Unit tests for construction and validation rules of ONC/RPC call headers.

Important APIs/types/functions: `RpcCall`, `RpcCall.RPC_VERSION`, `RpcMessage.Type.RPC_CALL`, `CredentialsNone`, `VerifierNone`, and getter methods for xid/program/version/procedure/auth fields.

Control flow: a valid constructor call is created and every exposed field is asserted. Two negative tests assert `IllegalArgumentException` for unsupported RPC version and for message type `RPC_REPLY` passed to a call constructor.

State and persistence: local message objects only; no external state.

Dependencies/integration points: ONC/RPC call validation used by frame decoding, clients, and server programs.

Risks: protocol validation must stay strict; allowing a wrong message type or version would corrupt server dispatch and error handling.

Test signals: confirms call headers enforce version/type invariants and preserve authentication verifier objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcCall.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcCallCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcCallCache.java

Purpose: Tests duplicate-request cache behavior for ONC/RPC calls, including size validation, in-progress/completed entries, and eviction order.

Important APIs/types/functions: `RpcCallCache`, `RpcCallCache.CacheEntry`, `RpcCallCache.ClientRequest`, `checkOrAddToCache`, `callCompleted`, `iterator`, `size`, mocked `RpcResponse`, and `InetAddress`.

Control flow: constructor tests reject zero and negative sizes. Add/remove coverage inserts a client/xid, expects first lookup to create and return null, second lookup to show in-progress, then `callCompleted` to store a response. Cache functionality loops through 20 client addresses with max size 10 and validates that only the most recent 10 entries remain in iterator order.

State and persistence: in-memory cache keyed by client address and xid; entries transition from in-progress to completed with a response reference.

Dependencies/integration points: ONC/RPC duplicate suppression for idempotency/retransmit handling.

Risks: eviction ordering is observable; address resolution of synthetic IPs must be stable; cache entry state must not conflate in-progress duplicate calls with completed replay responses.

Test signals: verifies capacity bounds, insertion semantics, completed-response retention, and FIFO-style eviction of old client requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcCallCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcDeniedReply.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcDeniedReply.java

Purpose: Unit coverage for denied ONC/RPC replies and reject-state wire mapping.

Important APIs/types/functions: `RpcDeniedReply`, `RpcDeniedReply.RejectState.fromValue`, `RpcReply.ReplyState`, `RpcMessage.Type.RPC_REPLY`, and `VerifierNone`.

Control flow: maps reject values 0 and 1 to `RPC_MISMATCH` and `AUTH_ERROR`, checks value 2 throws, then constructs a denied reply and verifies xid, message type, reply state, and reject state.

State and persistence: no persistent state.

Dependencies/integration points: server-side rejected responses emitted by RPC authorization/version checks.

Risks: constructor uses `ReplyState.MSG_ACCEPTED` in the test despite a denied reply type, so the test checks fields rather than semantic consistency; enum mapping remains wire-sensitive.

Test signals: confirms invalid reject codes fail and reply metadata remains accessible for decoding/serialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcDeniedReply.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcMessage.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcMessage.java

Purpose: Unit tests for the abstract base `RpcMessage`.

Important APIs/types/functions: anonymous `RpcMessage` subclass, `getXid`, `getMessageType`, `validateMessageType`, and `XDR write` contract.

Control flow: helper creates an anonymous message with a no-op `write`. Tests assert constructor fields, successful validation for matching type, and `IllegalArgumentException` for mismatched expected type.

State and persistence: local message instance only.

Dependencies/integration points: common base for `RpcCall` and `RpcReply` hierarchy.

Risks: validation is a core guardrail; weak tests around `write` mean serialization correctness belongs to concrete subclasses.

Test signals: verifies basic identity fields and type-check failure behavior for protocol message dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcMessage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcReply.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcReply.java

Purpose: Unit coverage for base RPC reply state mapping and constructor behavior.

Important APIs/types/functions: `RpcReply`, `RpcReply.ReplyState.fromValue`, `VerifierNone`, anonymous `RpcReply` subclass, and `RpcMessage.Type.RPC_REPLY`.

Control flow: maps values 0 and 1 to `MSG_ACCEPTED` and `MSG_DENIED`, checks value 2 throws, and constructs an anonymous reply to assert xid, message type, and state.

State and persistence: no external state.

Dependencies/integration points: base class for accepted and denied RPC replies.

Risks: enum ordinal mapping is protocol-sensitive; serialization is not tested here.

Test signals: validates reply-state constants and base constructor invariants used by concrete reply classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcReply.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestXDR.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestXDR.java

Purpose: Serialization stress/performance-style test for XDR integer and hyper-long read/write loops.

Important APIs/types/functions: `XDR`, `writeInt`, `readInt`, `writeLongAsHyper`, `readHyper`, `asReadOnlyWrap`, and constant `WRITE_VALUE`.

Control flow: `testPerformance` writes and reads `8 << 20` integers, then writes and reads the same count of hyper longs, asserting every decoded value equals 23.

State and persistence: large in-memory XDR buffers only.

Dependencies/integration points: Hadoop ONC/RPC XDR encoding layer.

Risks: heavy memory/CPU for a unit test; named as performance but asserts correctness; lacks edge cases for negative values, padding, and variable opaque fields.

Test signals: catches bulk buffer growth, wrapping, and repeated primitive serialization/deserialization regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestXDR.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/security/TestCredentialsSys.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/security/TestCredentialsSys.java

Purpose: Unit tests for AUTH_SYS credential XDR serialization and credential-length padding behavior.

Important APIs/types/functions: `CredentialsSys`, setters/getters for UID/GID/stamp/hostName, `write`, `read`, `getCredentialLength`, and `XDR.asReadOnlyWrap`.

Control flow: one test round-trips UID/GID/stamp through XDR. Two hostname tests write/read hostnames whose lengths are not and are multiples of four, asserting UID/GID/stamp and credential length of 32.

State and persistence: local credential objects and in-memory XDR buffers.

Dependencies/integration points: ONC/RPC AUTH_SYS credential encoding for NFS/portmap requests.

Risks: XDR padding/length calculation is wire-compatible behavior; tests do not assert hostName after read, group list behavior, or maximum host size.

Test signals: validates basic credential field persistence and fixed opaque padding alignment for hostnames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/security/TestCredentialsSys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/security/TestRpcAuthInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/security/TestRpcAuthInfo.java

Purpose: Tests authentication flavor mapping for ONC/RPC auth metadata.

Important APIs/types/functions: `RpcAuthInfo.AuthFlavor.fromValue`, `AUTH_NONE`, `AUTH_SYS`, `AUTH_SHORT`, `AUTH_DH`, and `RPCSEC_GSS`.

Control flow: asserts known wire values 0, 1, 2, 3, and 6 map to the expected flavors; value 4 must throw `IllegalArgumentException`.

State and persistence: none.

Dependencies/integration points: credential/verifier decoding for ONC/RPC requests and replies.

Risks: sparse enum mapping means ordinal-based implementations can be incorrect; tests cover value 4 gap but not other invalid values.

Test signals: confirms accepted auth flavors and invalid-flavor rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/security/TestRpcAuthInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/portmap/TestPortmap.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/portmap/TestPortmap.java

Purpose: Integration tests for Hadoop's ONC/RPC portmap service over TCP and UDP.

Important APIs/types/functions: `Portmap`, `pm.start`, `pm.shutdown`, `getTcpServerLocalAddress`, `getUdpServerLoAddress`, `RpcCall.getInstance`, `RpcProgramPortmap`, `PortmapMapping`, `DatagramSocket`, `RpcReply.read`, and `PortmapMapping.key`.

Control flow: `@BeforeAll` starts a `Portmap` with short timeout on ephemeral localhost TCP/UDP addresses. `testIdle` connects a TCP socket and expects the server to disconnect idle clients. `testRegistration` sends a UDP PMAPPROC_SET request with a serialized mapping, reads the UDP reply, checks `MSG_ACCEPTED`, sleeps briefly, and verifies the handler map contains the registered mapping.

State and persistence: live portmap server, handler mapping table, UDP/TCP sockets, and per-instance xid counter.

Dependencies/integration points: Netty/simple RPC server internals, localhost networking, XDR, ONC/RPC security `CredentialsNone` and `VerifierNone`.

Risks: live network timing and fixed short timeouts can be flaky; handler map is inspected directly; UDP receive timeout is environmental.

Test signals: confirms idle TCP cleanup, UDP registration response, and mutation of the portmap registry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/portmap/TestPortmap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ManualTestKeytabLogins.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ManualTestKeytabLogins.java

Purpose: Manual regression driver for HADOOP-6947, verifying two different keytab/principal logins can be performed in one JVM.

Important APIs/types/functions: `main`, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, `getUserName`, and JUnit `assertTrue` used in a command-line context.

Control flow: requires exactly four arguments: principal/keytab pairs. It logs in the first UGI, prints it, asserts username equals the first principal, then repeats for the second pair.

State and persistence: uses Kerberos keytab files and mutates UGI/Kerberos login state in the JVM; no test framework setup.

Dependencies/integration points: external Kerberos environment, valid keytabs, Hadoop CLI classpath.

Risks: not an automated unit test; exits process on bad arguments; depends on real KDC/keytabs; assertions may be disabled only if run outside normal test settings.

Test signals: when run manually, proves separate keytab logins return distinct expected UGIs without overwriting each other incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ManualTestKeytabLogins.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/NetUtilsTestResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/NetUtilsTestResolver.java

Purpose: Test DNS resolver for `SecurityUtil.QualifiedHostResolver` behavior with deterministic search domains and host mappings.

Important APIs/types/functions: `install`, `addResolvedHost`, overridden `getInetAddressByName`, exposed `getByExactName`, `getByNameWithSearch`, `getHostSearches`, and `reset`.

Control flow: `install` creates a resolver with search domains `a.b`, `b`, `c`, seeds three fully qualified hosts, and assigns it to global `SecurityUtil.hostResolver`. Resolution records every attempted host string and returns configured `InetAddress` instances or throws `UnknownHostException`.

State and persistence: mutable `resolvedHosts`, `hostSearches`, and global `SecurityUtil.hostResolver`.

Dependencies/integration points: Hadoop security token service host resolution and Java `InetAddress`.

Risks: global resolver mutation can leak between tests if not restored; host search ordering is captured as mutable state; not thread-safe.

Test signals: consumers can verify exact DNS search attempts and deterministic address results without relying on external DNS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/NetUtilsTestResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/SecurityUtilTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/SecurityUtilTestHelper.java

Purpose: Small test helper exposing package/private-adjacent security utility controls.

Important APIs/types/functions: `setTokenServiceUseIp(boolean)` and `isExternalKdcRunning()`.

Control flow: `setTokenServiceUseIp` delegates to `SecurityUtil.setTokenServiceUseIp`. `isExternalKdcRunning` checks JVM properties `externalKdc` equals `true` and `java.security.krb5.conf` is set.

State and persistence: mutates global `SecurityUtil` token-service behavior; reads system properties.

Dependencies/integration points: security token service construction and tests that optionally use an external Kerberos KDC.

Risks: global toggle can affect later tests if not reset; external KDC detection is property-based and does not validate the KDC itself.

Test signals: enables tests to force host/IP token service choices and conditionally run external-KDC scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/SecurityUtilTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestAuthenticationFilter.java

Purpose: Unit test for `AuthenticationFilterInitializer` configuration extraction and filter registration.

Important APIs/types/functions: `AuthenticationFilterInitializer.initFilter`, `FilterContainer.addFilter`, `AuthenticationFilter`, `HttpServer2.BIND_ADDRESS`, and Hadoop `Configuration`.

Control flow: builds a configuration with `hadoop.http.authentication.foo=bar` and bind address `barhost`, mocks `FilterContainer`, and intercepts `addFilter`. The answer asserts filter name/class and parameters such as cookie path, auth type, token validity, anonymous flag, synthesized Kerberos principal, default keytab, and copied custom property.

State and persistence: no persistent state; uses system `user.home` for default keytab path.

Dependencies/integration points: Hadoop HTTP server filter initialization and Mockito.

Risks: default config expectations are brittle if authentication defaults change; unchecked raw `Answer` casting.

Test signals: verifies initializer prefixes and default authentication parameters are wired into the servlet filter container.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestAuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestAuthorizationContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestAuthorizationContext.java

Purpose: Tests thread-local storage of current authorization header bytes.

Important APIs/types/functions: `AuthorizationContext.setCurrentAuthorizationHeader`, `getCurrentAuthorizationHeader`, `clear`, and `SubjectInheritingThread`.

Control flow: tests set/get in the same thread, clear behavior, isolation between main and child thread, and null/empty byte-array handling. The child thread asserts it starts without the main thread's header, sets its own, clears it, and leaves main state unchanged.

State and persistence: thread-local authorization header state.

Dependencies/integration points: security/RPC code that needs per-thread authorization metadata and Hadoop subject-inheriting thread wrapper.

Risks: byte arrays are mutable; tests do not check defensive copying. Thread-local cleanup is essential to avoid leakage in pooled threads.

Test signals: confirms basic lifecycle, null semantics, and cross-thread isolation of authorization context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestAuthorizationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestCompositeGroupMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestCompositeGroupMapping.java

Purpose: Tests `CompositeGroupsMapping` with multiple configured providers, provider-specific configuration, and combined/non-combined lookup modes.

Important APIs/types/functions: `CompositeGroupsMapping`, `Groups`, `GroupMappingServiceProvider`, `Configurable`, `CommonConfigurationKeys.HADOOP_SECURITY_GROUP_MAPPING`, custom `UserProvider`, `ClusterProvider`, and provider config prefixes.

Control flow: static configuration registers two providers. Provider base classes validate that provider-specific config was rewritten into each provider's `Configuration`. Tests lookup John and hdfs from different providers, then lookup Jack with combined mode true expecting two groups and combined mode false expecting only the first provider's group.

State and persistence: static shared `Configuration` mutated by tests; provider implementations are stateless aside from injected conf.

Dependencies/integration points: Hadoop `Groups` service and composite mapping provider configuration.

Risks: shared static `conf` can leak combined flag between tests if execution order changes; provider lookup order matters; assertions use `assertTrue` rather than exact list equality.

Test signals: verifies provider discovery, provider-specific config propagation, ordered lookup, and combined aggregation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestCompositeGroupMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestCredentials.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestCredentials.java

Purpose: Tests Hadoop `Credentials` token/secret-key serialization, merge semantics, and adding credentials to UGI.

Important APIs/types/functions: `Credentials`, `Token`, `TokenIdentifier`, `Text`, `write`, `readFields`, `writeProto`, `readProto`, `writeTokenStorageToStream`, `readTokenStorageStream`, `addAll`, `mergeAll`, `UserGroupInformation.addCredentials`, and `KeyGenerator`.

Control flow: setup creates a temp dir. Tests write/read legacy writable storage with two tokens and ten HMAC keys, proto empty/non-empty credentials, stream empty/non-empty credentials, sequential proto records for writable compatibility, duplicate handling in `addAll` and `mergeAll`, and token transfer into a remote UGI.

State and persistence: temporary files under `GenericTestUtils.getTestDir("mapred")`, in-memory token maps and secret-key maps, static token/service/secret arrays.

Dependencies/integration points: Hadoop security token storage formats, Java crypto HMAC key generation, filesystem streams, UGI credential container.

Risks: temp directory cleanup only deletes the directory, not recursively; random generated keys require byte equality; serialization compatibility is broad but does not test malformed input.

Test signals: confirms token/key counts and values survive all supported encodings, overwrite vs preserve semantics differ between `addAll` and `mergeAll`, and UGI stores exact token instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestCredentials.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestDoAsEffectiveUser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestDoAsEffectiveUser.java

Purpose: Integration tests for proxy-user/doAs behavior over Hadoop protobuf RPC, including IP/group authorization and token-auth interactions.

Important APIs/types/functions: `UserGroupInformation.createProxyUser`, `createProxyUserForTesting`, `doAs`, `ProxyUsers.refreshSuperUserGroupsConfiguration`, `DefaultImpersonationProvider`, `RPC.setProtocolEngine`, `ProtobufRpcEngine2`, `TestRpcBase` server/client helpers, `SecurityUtil.setAuthenticationMethod`, and test tokens.

Control flow: setup resets UGI config and proxy-user conf. Helper `configureSuperUserIPAddresses` whitelists local interface addresses. Tests assert local `doAs` string form, successful remote real/proxy calls, expected failures for bad/missing IP or group config, and token-auth cases where the server reports token owner/renewer rather than proxy user.

State and persistence: global UGI configuration, global proxy-user configuration, live in-process RPC servers, client field, authentication method in conf, and token service address.

Dependencies/integration points: Hadoop IPC, protobuf RPC engine, proxy-user authorization, network interfaces, token secret manager.

Risks: live networking and 4-second timeouts can be flaky; local IP enumeration is environment-dependent; several failure tests catch any exception and print stack traces, so they mainly assert that an RPC failed.

Test signals: verifies proxy identity propagation to server, enforcement of superuser host/group policy, and precedence of token identity during RPC authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestDoAsEffectiveUser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestFixKerberosTicketOrder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestFixKerberosTicketOrder.java

Purpose: MiniKDC regression coverage for HADOOP-13433, ensuring `UserGroupInformation.fixKerberosTicketOrder` keeps the TGT first and removes destroyed TGTs.

Important APIs/types/functions: `KerberosSecurityTestcase`, `MiniKdc` via `getKdc`, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, `fixKerberosTicketOrder`, `reloginFromKeytab`, `Subject.getPrivateCredentials`, `KerberosTicket`, `Sasl.createSaslClient`, and `LambdaTestUtils.intercept`.

Control flow: setup creates client and server principals in a keytab and enables Kerberos. The main test obtains a service ticket, manually moves the TGT to the end, confirms a new service ticket request fails, calls `fixKerberosTicketOrder`, verifies the TGT is first, then obtains another service ticket. The destroyed-TGT test destroys the TGT, fixes order, expects no ticket, verifies service-ticket acquisition fails, relogs in, and succeeds.

State and persistence: MiniKDC principals/keytab, UGI subject private credentials, Kerberos tickets, SASL properties, and global immediate-renew test flag.

Dependencies/integration points: Kerberos, JAAS/SASL, Hadoop UGI ticket management.

Risks: highly JDK/Kerberos-implementation sensitive; mutates private credential collection directly; assumes first KerberosTicket ordering matters.

Test signals: catches regressions where service tickets precede TGT or destroyed TGTs remain and break future Kerberos service-ticket acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestFixKerberosTicketOrder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestGroupFallback.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestGroupFallback.java

Purpose: Integration tests for shell, netgroup, JNI-with-fallback group mapping implementations against the current OS user.

Important APIs/types/functions: `Groups`, `ShellBasedUnixGroupsMapping`, `ShellBasedUnixGroupsNetgroupMapping`, `JniBasedUnixGroupsMappingWithFallback`, `JniBasedUnixGroupsNetgroupMappingWithFallback`, and `CommonConfigurationKeys.HADOOP_SECURITY_GROUP_MAPPING`.

Control flow: each test configures a group mapping class, creates `Groups`, looks up `System.getProperty("user.name")`, logs the result, and asserts at least one group is returned.

State and persistence: uses OS group database and optional native code; no file state.

Dependencies/integration points: Unix shell commands, netgroup lookup path, native JNI group mapper when available, Hadoop fallback wrappers.

Risks: environment-dependent: users without groups or platforms without netgroup support may fail; tests validate non-empty output rather than exact parity.

Test signals: indicates configured mapping classes can resolve the current user and fallback implementations return usable groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestGroupFallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestGroupsCaching.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestGroupsCaching.java

Purpose: Broad unit/concurrency coverage for the `Groups` cache: positive/negative caching, static overrides, request coalescing, expiration, background reload, counters, and exception handling.

Important APIs/types/functions: `Groups`, `FakeGroupMapping`, `ExceptionalGroupMapping`, `FakeTimer`, `CommonConfigurationKeys` group cache settings, `cacheGroupsAdd`, `refresh`, `getGroups`, `getNegativeCache`, background counter getters, `CountDownLatch`, and `SubjectInheritingThread`.

Control flow: setup resets fake mapping state and configures it as the group provider. Tests populate fake groups, blacklist users, advance fake time, run concurrent lookup threads, pause/resume mapping calls with a latch, and assert request counts/counter values. Background-refresh cases verify stale values are returned immediately when enabled, blocking reload happens when disabled, failures are counted, old values survive some failures, and entries eventually expire.

State and persistence: static fake provider state (`allGroups`, blacklist, request counters, delay, exception flag, latch), per-test `Configuration`, `Groups` caches, fake time, and background reload executor state.

Dependencies/integration points: Hadoop group mapping cache, shell mapping superclass, AssertJ/JUnit, and thread scheduling.

Risks: many static mutable fields require setup discipline; timing sleeps and background counters can be flaky; static override config bypasses provider calls; exceptions should not poison negative cache.

Test signals: strong signal for cache correctness under concurrency, cache expiry, negative-cache TTL, refresh clearing, stale-value policy, and background reload metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestGroupsCaching.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestHttpCrossOriginFilterInitializer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestHttpCrossOriginFilterInitializer.java

Purpose: Unit test for extracting CORS filter parameters from Hadoop configuration.

Important APIs/types/functions: `HttpCrossOriginFilterInitializer.getFilterParameters`, `HttpCrossOriginFilterInitializer.PREFIX`, and `Configuration`.

Control flow: sets two keys under the initializer prefix and one unrelated key. Calls `getFilterParameters` and verifies prefix-stripped keys are present while the out-of-scope key is absent.

State and persistence: local configuration map only.

Dependencies/integration points: Hadoop HTTP CORS filter initialization.

Risks: only tests extraction, not actual filter registration or CORS behavior.

Test signals: confirms prefix scoping and key stripping for CORS filter parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestHttpCrossOriginFilterInitializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestIngressPortBasedResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestIngressPortBasedResolver.java

Purpose: Unit test for SASL QOP selection by inbound server port.

Important APIs/types/functions: `IngressPortBasedResolver`, `setConf`, `getServerProperties`, `Sasl.QOP`, and configuration keys `ingress.port.sasl.*`.

Control flow: configures ports 444, 555, 666, and 777, with explicit QOP values for three of them. Assertions verify `authentication` maps to `auth`, `authentication,privacy` to `auth,auth-conf`, `privacy` to `auth-conf`, configured port without property defaults to privacy, and unknown port defaults to authentication.

State and persistence: resolver configuration only.

Dependencies/integration points: Hadoop RPC/SASL server property resolution.

Risks: string mapping is brittle; no invalid property or malformed port tests.

Test signals: confirms per-port QOP policy resolution and defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestIngressPortBasedResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestJNIGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestJNIGroupsMapping.java

Purpose: Compares JNI and shell-based Unix group lookup implementations.

Important APIs/types/functions: `NativeCodeLoader.isNativeCodeLoaded`, `JniBasedUnixGroupsMapping`, `ShellBasedUnixGroupsMapping`, `UserGroupInformation.getCurrentUser`, and helper `testForUser`.

Control flow: `@BeforeEach` skips unless native code is loaded. The test compares sorted group arrays for the current user and a deliberately nonexistent user.

State and persistence: reads OS user/group database through shell and JNI paths.

Dependencies/integration points: native Hadoop library, Unix group APIs, shell group command implementation.

Risks: environment-dependent; group database changes during test can fail parity; skipped without native code, leaving JNI path untested.

Test signals: validates native group lookup returns the same groups as shell fallback for existing and missing users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestJNIGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestKDiag.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestKDiag.java

Purpose: MiniKDC-backed tests for the `KDiag` Kerberos diagnostics command.

Important APIs/types/functions: `MiniKdc`, `KDiag.exec`, `KerberosDiagsFailure`, CLI constants such as `ARG_KEYLEN`, `ARG_KEYTAB`, `ARG_PRINCIPAL`, `ARG_RESOURCE`, `ARG_OUTPUT`, `ARG_JAAS`, category constants, `UserGroupInformation.reset`, and `SecurityUtil.getAuthenticationMethod`.

Control flow: `@BeforeAll` starts MiniKDC, creates a keytab for `foo`, and configures Kerberos authentication. Helpers run KDiag expecting success or a failure category. Tests cover missing login, skipped login, secure config validation, missing keytab/principal, successful keytab+principal, Kerberos name/short-name validation, output file generation, resource loading, invalid resource, and JAAS requirement.

State and persistence: MiniKDC process, work directory, keytab file, `target/kdiag.txt`, global UGI state reset before each test, and configuration.

Dependencies/integration points: Kerberos runtime, Hadoop diagnostic CLI, resource loading, filesystem output.

Risks: 30-second class timeout; MiniKDC and JVM Kerberos config sensitivity; output file under `target` is not isolated by temp dir.

Test signals: verifies KDiag success/failure categorization and key Kerberos diagnostic options in a controlled KDC environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestKDiag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestKDiagNoKDC.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestKDiagNoKDC.java

Purpose: Tests `KDiag` behavior when no MiniKDC is started.

Important APIs/types/functions: `KDiag.exec`, `KerberosDiagsFailure`, `ARG_KEYLEN`, `ARG_NOLOGIN`, `ARG_NOFAIL`, `HADOOP_TOKEN_FILES`, `UserGroupInformation.reset`, and category constants `CAT_LOGIN` and `CAT_TOKEN`.

Control flow: resets UGI before each test. Tests expect login-category failures for standalone and no-login invocations, success/nonthrowing return for `--nofail`, usage return code `-1`, and token-category failure when `HADOOP_TOKEN_FILES` points at a nonexistent file.

State and persistence: shared static `Configuration`, temporarily sets/unsets token files config.

Dependencies/integration points: KDiag command path without Kerberos service, token-file loading.

Risks: behavior can vary on hosts with default Kerberos configuration; shared static conf must be cleaned for token-file test.

Test signals: confirms KDiag remains usable and categorizes failures even without a local test KDC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestKDiagNoKDC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMapping.java

Purpose: Main test suite for `LdapGroupsMapping`, covering user/group searches, base DN configuration, dynamic filters, hierarchy lookup, reconnect/retry behavior, password sources, LDAP timeouts, and setConf error handling.

Important APIs/types/functions: `LdapGroupsMapping`, config keys for LDAP URL/base DNs/search filters/timeouts/passwords, inherited mock context helpers, `CredentialProviderFactory`, `JavaKeyStoreProvider`, `ServerSocket`, `SubjectInheritingThread`, `doGetGroups`, and Mockito verification.

Control flow: mock tests configure `DirContext.search` sequences for user then group enumeration, validate base DN trimming/defaults, dynamic filter argument resolution, parent group lookup, reconnect after `CommunicationException`, and empty result when LDAP remains down. Password tests read from a file and Java keystore aliases. Timeout tests create minimal local sockets that accept but do not respond or stop after bind success to trigger connection/read timeouts. `testSetConf` injects `Configuration.getPassword` IOException and ensures no NPE.

State and persistence: mock LDAP context, temporary secret files, temporary JKS credential provider files, local server sockets, and mapping configuration.

Dependencies/integration points: Java Naming LDAP APIs, Hadoop credential provider, filesystem, local sockets, Mockito.

Risks: timeout tests are timing/network sensitive; credential provider files in generic test dir can collide; mock search call counts encode implementation details.

Test signals: verifies LDAP group resolution correctness, resilience to connection failures, secure password retrieval, and timeout diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingBase.java

Purpose: Shared Mockito fixture and dummy LDAP context factory for LDAP group mapping tests.

Important APIs/types/functions: mocked `DirContext`, `NamingEnumeration<SearchResult>`, `SearchResult`, `Attributes`, spy `LdapGroupsMapping`, `getBaseConf`, `DummyLdapCtxFactory`, and `InitialContextFactory.getInitialContext`.

Control flow: `setupMocksBase` resets dummy factory, initializes Mockito annotations, stubs user search to return one user, group enumeration to return two group names, parent group enumeration to return one parent, and exposes helper getters. `getBaseConf` installs `DummyLdapCtxFactory` and expected LDAP URL. The dummy factory asserts provider URL, bind user, and bind password if configured, then returns the mocked context or a real `InitialLdapContext`.

State and persistence: per-test mocks plus static dummy factory expectations/context.

Dependencies/integration points: JNDI LDAP context creation path used by `LdapGroupsMapping`.

Risks: static dummy factory state must be reset every test; shared spy can accumulate interactions if not reset by Mockito init; assertions inside factory couple tests to context environment keys.

Test signals: provides deterministic LDAP search results and verifies LDAP context construction parameters for derived test classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithBindUserSwitch.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithBindUserSwitch.java

Purpose: Tests LDAP bind-user cycling when authentication failures occur.

Important APIs/types/functions: `LdapGroupsMapping` bind-user config keys, `BIND_USERS_KEY`, bind username/password/plaintext/alias/file suffixes, `LDAP_NUM_ATTEMPTS_KEY`, `DummyLdapCtxFactory`, Hadoop credential provider, and `AuthenticationException`.

Control flow: one test validates missing bind credentials fail with a runtime error. Other tests configure multiple bind users with plaintext passwords, credential-provider aliases, or password files. Shared helper sets expected bind user/password in the dummy factory, stubs LDAP search to throw a configured number of `AuthenticationException`s while advancing expected credentials, then returns user and group enumerations and asserts final groups and search-call count.

State and persistence: temporary password files, temporary Java keystore credential provider, static dummy factory expected bind credentials, mocked context failures, and atomic failure counter.

Dependencies/integration points: LDAP context creation, Hadoop credential providers, password file extraction, retry/bind switching logic.

Risks: cycles expected credentials with Guava `Iterators.cycle`; static factory expectations must align exactly with reconnect timing; password files/JKS live in generic test dir.

Test signals: confirms configuration validation and that authentication failures rotate through configured bind users across plaintext, alias, and file password sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithBindUserSwitch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithFailover.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithFailover.java

Purpose: Tests LDAP URL failover policy under repeated communication failures.

Important APIs/types/functions: `LdapGroupsMapping`, `LDAP_URL_KEY`, `LDAP_NUM_ATTEMPTS_KEY`, `LDAP_NUM_ATTEMPTS_BEFORE_FAILOVER_KEY`, `DummyLdapCtxFactory.setExpectedLdapUrl`, `CommunicationException`, and Mockito `Answer`.

Control flow: disabled-failover test configures three LDAP URLs but sets attempts-before-failover equal to total attempts, expecting all attempts against the first URL. Failover test configures 12 attempts and failover every 2 attempts, uses a queue of URLs to update expected provider URL before each switch, throws `CommunicationException` every search, and verifies total attempts.

State and persistence: static dummy expected URL, queue of URL strings, atomic per-server attempt counter, and mock context invocation count.

Dependencies/integration points: LDAP context recreation/failover logic.

Risks: validates attempts and URL selection through factory side effects rather than returned groups; all paths end empty, so success path after failover is not covered.

Test signals: confirms retry budget and cyclic LDAP server failover behavior on communication errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithFailover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithOneQuery.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithOneQuery.java

Purpose: Tests `LdapGroupsMapping` single-query lookup using a user's `memberOf` attribute and fallback to secondary lookup when DN parsing fails.

Important APIs/types/functions: `LdapGroupsMapping.MEMBEROF_ATTR_KEY`, mocked `Attribute.getAll`, `NamingEnumeration`, custom inner `TestLdapGroupsMapping` overriding `lookupGroup`, and Mockito `verify`.

Control flow: `setupMocks` stubs the user's `memberOf` attribute to return a list of group DNs. The primary scenario enables `memberOf`, resolves CN values `abc`, `xyz`, and `sss`, asserts no secondary query, and verifies one LDAP search. The fallback scenario includes an invalid DN with `ipaUniqueID`, expects empty groups, sets attempts to one, and asserts overridden `lookupGroup` was called.

State and persistence: mock enumerations and a boolean `secondaryQueryCalled` in the custom mapping.

Dependencies/integration points: LDAP DN parsing and optimized group lookup path.

Risks: invocation count spans two sub-scenarios in one test; fallback expected empty result is tied to invalid DN behavior; custom subclass tracks only method entry, not fallback result quality.

Test signals: verifies one-query optimization avoids extra search for valid `memberOf` data and falls back when memberOf parsing cannot produce groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithOneQuery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithPosixGroup.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithPosixGroup.java

Purpose: Tests LDAP group lookup configured for POSIX account/group schemas.

Important APIs/types/functions: `LdapGroupsMapping` POSIX config keys, `GROUP_SEARCH_FILTER_KEY`, `USER_SEARCH_FILTER_KEY`, `GROUP_MEMBERSHIP_ATTR_KEY`, `POSIX_UID_ATTR_KEY`, `POSIX_GID_ATTR_KEY`, `GROUP_NAME_ATTR_KEY`, mocked LDAP attributes, and inherited base fixtures.

Control flow: setup mocks user attributes `uid`, `uidNumber`, and `gidNumber`. The test stubs searches containing `posix` to return user then group enumerations, configures POSIX filters and attributes, gets groups for `some_user`, then changes `POSIX_UID_ATTR_KEY` from `uidNumber` to `uid` and asserts the same groups.

State and persistence: mock LDAP attributes/search results and mutable mapping configuration.

Dependencies/integration points: POSIX LDAP schema support in `LdapGroupsMapping`.

Risks: search verification expects only two calls even after a second `getGroups` path may use cached context/state; does not validate exact filter arguments beyond containing `posix`.

Test signals: confirms POSIX UID/GID attributes can drive group lookup and alternate UID attribute configuration remains valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithPosixGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestNetgroupCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestNetgroupCache.java

Purpose: Unit tests for static `NetgroupCache` membership tracking.

Important APIs/types/functions: `NetgroupCache.add`, `getNetgroups`, `clear`, `@AfterEach teardown`, and helper `verifyGroupMembership`.

Control flow: membership test adds two groups with overlapping users and verifies users map to expected group counts. User-removal test clears and re-adds a group without one user, checking removal. Group-removal test clears two groups and re-adds one, checking removed group/user no longer appears.

State and persistence: global static netgroup cache cleared after each test.

Dependencies/integration points: netgroup-aware group mapping implementations.

Risks: static cache must be cleared to avoid cross-test contamination; tests assert membership presence but not exact group ordering.

Test signals: validates user-to-netgroup reverse mapping updates correctly when cache content changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestNetgroupCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestNullGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestNullGroupsMapping.java

Purpose: Ensures `NullGroupsMapping` always returns no groups and ignores cache mutation hooks.

Important APIs/types/functions: `NullGroupsMapping`, `getGroups`, `cacheGroupsAdd`, `cacheGroupsRefresh`, and JUnit setup.

Control flow: creates a new mapper, checks `getGroups("user")` returns an empty list, calls `cacheGroupsAdd` with two groups and checks still empty, calls `cacheGroupsRefresh` and checks still empty.

State and persistence: mapper instance only; no persistent cache state.

Dependencies/integration points: `GroupMappingServiceProvider` no-op implementation for deployments/tests that disable group lookup.

Risks: only validates list path, not `getGroupsSet` if implemented separately.

Test signals: confirms the null provider remains side-effect-free for add/refresh operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestNullGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestProxyUserFromEnv.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestProxyUserFromEnv.java

Purpose: Tests login-user proxying via the `HADOOP_PROXY_USER` system property.

Important APIs/types/functions: `UserGroupInformation.HADOOP_PROXY_USER`, `UserGroupInformation.getLoginUser`, `getRealUser`, `Runtime.exec("whoami")`, and username normalization for Windows domain prefixes.

Control flow: sets the proxy-user system property to `foo.bar`, obtains login UGI, asserts proxy username, reads the real OS username from `whoami`, strips any domain prefix after backslash, and asserts the real UGI username matches.

State and persistence: mutates a JVM system property and UGI login-user singleton/cache.

Dependencies/integration points: process environment/OS user identity and UGI proxy-user initialization.

Risks: system property is not cleared in the test; `whoami` process and username formatting are platform-dependent; UGI login cache can leak into later tests.

Test signals: confirms environment/system-property proxy user is reflected as login user with a real underlying UGI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestProxyUserFromEnv.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestRaceWhenRelogin.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestRaceWhenRelogin.java

Purpose: Concurrency regression test for HADOOP-13433, ensuring repeated Kerberos relogin keeps the TGT as the first ticket while other threads acquire service tickets.

Important APIs/types/functions: `KerberosSecurityTestcase`, `UserGroupInformation.reloginFromKeytab`, `getSubject().getPrivateCredentials`, `KerberosTicket`, `Sasl.createSaslClient`, `ThreadLocalRandom`, `AtomicBoolean`, and MiniKDC principal creation.

Control flow: setup creates a keytab with client and multiple server principals, enables Kerberos, and logs in the client UGI. The test starts one relogin thread that calls relogin 100 times and verifies first ticket starts with `krbtgt`; ten service-ticket threads repeatedly create SASL clients for different server protocols until stopped. Final assertion requires no relogin iteration observed wrong ticket order.

State and persistence: MiniKDC/keytab, shared UGI subject credentials, Kerberos ticket collection, many threads, and global immediate-renew flag.

Dependencies/integration points: Kerberos ticket renewal, SASL service-ticket acquisition, concurrent UGI credential mutation.

Risks: race/timing-dependent by design; exceptions inside service-ticket threads are swallowed; test duration includes sleeps up to roughly five seconds plus service-thread delays.

Test signals: catches synchronization regressions where concurrent service-ticket acquisition reorders credentials so TGT is no longer first after relogin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestRaceWhenRelogin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestRuleBasedLdapGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestRuleBasedLdapGroupsMapping.java

Purpose: Tests case-conversion rules layered on top of LDAP group mapping.

Important APIs/types/functions: `RuleBasedLdapGroupsMapping`, `RuleBasedLdapGroupsMapping.CONVERSION_RULE_KEY`, `LdapGroupsMapping.doGetGroups`, `getGroups`, `getGroupsSet`, Mockito spy/stubbing, and `Configuration`.

Control flow: each test spies a mapping and stubs `doGetGroups("admin", anyInt())` to return a `LinkedHashSet`. With `to_upper`, `getGroups` returns uppercase groups; with `to_lower`, it returns lowercase groups; with invalid rule `none`, `getGroupsSet` returns the original set unchanged.

State and persistence: local configuration and mocked group set only.

Dependencies/integration points: LDAP groups mapping extension used where group names require normalization.

Risks: stubs the LDAP lookup, so only conversion logic is tested; invalid rule behavior is pass-through rather than error.

Test signals: confirms supported conversion rules preserve order while changing case and unsupported rules leave group names unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestRuleBasedLdapGroupsMapping.java -->
