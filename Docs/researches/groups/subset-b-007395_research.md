# Research Report: subset-b-007395

Grouped research for Hadoop HA and HTTP test sources. Each section is bounded for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/MiniZKFCCluster.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/MiniZKFCCluster.java

Purpose: `MiniZKFCCluster` is a test harness for running multiple dummy `ZKFailoverController` instances against a real in-process ZooKeeper server. It models HA services, ZKFC threads, shared-resource ownership, health changes, transition failures, fencing failures, and ZooKeeper session loss.

Important APIs and types: the public harness API includes `start()`, `start(int)`, `stop()`, `getService()`, `getElector()`, `getZkfc()`, health and failure setters, `waitForHAState()`, `waitForHealthState()`, `waitForElectorState()`, `expireActiveLockHolder()`, `waitForActiveLockHolder()`, and `expireAndVerifyFailover()`. The nested `DummyZKFCThread` runs a controller under `MultithreadedTestUtil.TestContext`; nested `DummyZKFC` adapts `ZKFailoverController` to `DummyHAService`, serializing targets as four-byte indexes via Guava `Ints`.

Control flow: construction configures fast health-monitor intervals, clears `DummyHAService.instances`, and creates two services. `start(int)` formats the scoped ZK parent through service 0, starts its ZKFC, waits for it to become active, then starts the rest and waits for standby. Failover tests mutate `DummyHAService` flags and use polling waits that also surface thread exceptions through `ctx.checkException()`.

State and persistence: persistent state lives in ZooKeeper under `ZKFailoverController.ZK_PARENT_ZNODE_DEFAULT/dummy-cluster`, with lock and breadcrumb znodes managed by the elector. Local state is held in `svcs`, `thrs`, `sharedResource`, and mutable dummy-service flags. `stop()` interrupts all ZKFC threads, stops the context, and asserts no shared-resource split-brain violation.

Dependencies and integration points: integrates HA service protocol stubs, `ActiveStandbyElector`, `HealthMonitor`, ZooKeeper server internals, RPC server setup, and `DummySharedResource`. It intentionally bypasses login and admin access checks for tests.

Risks: polling loops rely on external test timeouts; stale `DummyHAService.instances` would corrupt target decoding, so the constructor clears it. Session-expiration tests read ZK internals directly and assume lock data equals service index bytes.

Test signals: downstream tests use this harness to verify automatic failover, graceful failover, observer handling, fencing, session re-establishment, and stress conditions while enforcing single ownership of the shared resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/MiniZKFCCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElector.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElector.java

Purpose: this unit test exercises `ActiveStandbyElector` against a mocked `ZooKeeper` client, focusing on election state transitions, asynchronous callback handling, retry behavior, ACL setup, parent znode creation, active-data lookup, and optional SSL ZooKeeper client configuration.

Important APIs and types: `ActiveStandbyElectorTester` overrides `connectToZooKeeper()` to return `mockZK` and `sleepFor()` to accumulate retry delay without blocking. Tests drive `joinElection()`, `processResult()` for create/stat callbacks, `processWatchEvent()`, `quitElection()`, `getActiveData()`, `ensureParentZNode()`, `createZooKeeper()`, and callback methods on `ActiveStandbyElectorCallback`.

Control flow: setup builds an elector rooted at `/parent/node`. Tests manually inject ZooKeeper result codes such as `OK`, `NODEEXISTS`, `CONNECTIONLOSS`, `NONODE`, `SESSIONEXPIRED`, and fatal codes. Create success fences prior breadcrumb data before `becomeActive`; node-exists causes standby and monitor watch setup; deletion causes re-election; disconnect moves to neutral and reconnect monitors; expiration creates a new session and rejoins only if app data is known.

State and persistence: the tested state is elector role, pending monitor flag, retry count, session identity, lock znode data, breadcrumb znode data, and parent znode ACL/version behavior. Persistence is simulated through `ZooKeeper.create`, `exists`, `getData`, `setData`, `delete`, `getACL`, and `setACL` verification.

Dependencies and integration points: uses Mockito, JUnit 5, ZooKeeper watcher and callback APIs, Hadoop `CommonConfigurationKeys`, `SecurityUtil.TruststoreKeystore`, and ZooKeeper `ZKClientConfig`/`ClientX509Util`.

Risks: tests assert exact fatal-error strings and exact retry thresholds, so production changes to diagnostics or default retry policy can break them. Because callbacks are driven manually, they validate elector logic more than real ZooKeeper ordering.

Test signals: covers null app data validation, duplicate standby suppression, breadcrumb deletion on quit, parent ACL updates when nodes already exist, `ActiveNotFoundException`, no-election-before-health, and SSL vs non-SSL ZK client property propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElectorRealZK.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElectorRealZK.java

Purpose: this integration test validates `ActiveStandbyElector` behavior against a real ZooKeeper server from `ClientBaseWithFixes`, complementing the mocked unit coverage with actual sessions, ephemeral nodes, watches, and ACL updates.

Important APIs and types: creates two `ActiveStandbyElector` instances with mocked `ActiveStandbyElectorCallback`s, unique `PARENT_DIR`, byte-array app data, and real `ZooKeeperServer`. Helpers include `checkFatalsAndReset()`, `ActiveStandbyElectorTestUtil.waitForActiveLockData()`, and `waitForElectorState()`.

Control flow: `setUp()` starts ZooKeeper and initializes electors. `testActiveStandbyTransition()` walks through parent creation, first active, second standby, quit-based takeover, rejoin as standby, session expiration of each elector, fencing callbacks, and eventual standby recovery. Additional tests expire active and standby sessions, verify `quitElection(false)` suppresses accidental rejoin after an expired event, and ensure reconnect without prior election participation does not start an election.

State and persistence: real persistent parent znodes and ephemeral lock znodes are used. Session IDs are invalidated through `ZooKeeperServer.closeSession()`, and active lock data is inspected from ZooKeeper. ACL state is tested by precreating a parent znode, mutating its data/version, and calling `ensureParentZNode()` with read-only ACLs.

Dependencies and integration points: depends on ZooKeeper server internals, Mockito timeout verification, Hadoop elector utilities, Guava `Ints`, and JUnit timeouts to bound asynchronous behavior.

Risks: timing-sensitive waits and `Thread.sleep()` make this more integration-flaky than pure unit tests. Shared static `PARENT_DIR` is UUID-based, reducing collision risk but tying all methods in the class to one path.

Test signals: verifies no fatal callbacks, correct active/standby role callbacks, fencing of old active data after session loss, safe no-rejoin behavior after explicit quit, and parent ACL update compatibility with existing znodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElectorRealZK.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestFailoverController.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestFailoverController.java

Purpose: this unit test covers `FailoverController.failover()` using `DummyHAService` targets. It validates manual failover, forced fencing, readiness and health checks, rollback/failback behavior, unreachable services, permission failures, and self-failover rejection.

Important APIs and types: `doFailover()` creates a `FailoverController` with `RequestSource.REQUEST_BY_USER`. Tests use `DummyHAService`, `HAServiceProtocol`, `HAServiceStatus`, `AlwaysSucceedFencer`, `AlwaysFailFencer`, and Mockito stubs for `transitionToStandby`, `transitionToActive`, `monitorHealth`, `getServiceStatus`, and proxy acquisition.

Control flow: successful cases transition source to standby and target to active without fencing when graceful transitions work. Failure cases inject access denial, not-ready status, failed health checks, transition failures, dead source proxies, dead target proxies, and fencer failures. The controller either aborts, fences the source, proceeds to target activation, or tries to fail back depending on whether the source cooperated or was fenced.

State and persistence: state is in-memory HA service state and fencer counters. There is no durable persistence. The tests check final `HAServiceState`, fencer call counts, and which service object was fenced.

Dependencies and integration points: integrates failover controller logic with HA RPC protocol semantics, fencer configuration from `NodeFencer`, Hadoop configuration defaults, and service readiness/health checks.

Risks: some assertions depend on dummy fencer static state and `DummyHAService` side effects, so setup isolation matters. The test name `NonExistant` mirrors existing spelling but covers real behavior: proxy calls may fail after proxy creation, not during creation.

Test signals: covers active-to-standby, standby-to-active, active-to-active refusal, access-control failure propagation, force-active bypass of readiness, graceful fencing timeout use, no failback after forced fencing, fencing during failed failback, and zero fencing on self-failover rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestFailoverController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHAAdmin.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHAAdmin.java

Purpose: this test verifies command-line usage and help behavior for `HAAdmin`, using an anonymous subclass that resolves every target to a dummy standby service.

Important APIs and types: the test captures `HAAdmin.errOut` and `HAAdmin.out` in `ByteArrayOutputStream`s, calls `tool.run(args)`, and checks text through `assertOutputContains()`. `resolveTarget()` returns `DummyHAService` bound to a fixed socket.

Control flow: setup initializes the tool and output streams. `testAdminUsage()` runs no args, an unknown bare command, an unknown dash command, and bad arity for `-transitionToActive`, expecting return `-1` and diagnostic text. `testHelp()` checks generic and command-specific help return `0`.

State and persistence: no durable state is touched. Test state is captured output and return codes. Output is reset for each `runTool()` invocation.

Dependencies and integration points: depends on `HAAdmin` command parsing, dummy HA target resolution, Hadoop `Configuration`, and Guava `Joiner` for logging command strings.

Risks: assertions search substrings rather than whole output, which is resilient to formatting changes but still sensitive to key wording. It does not exercise actual HA transitions or target-specific resolution failures.

Test signals: validates user-facing CLI contract for usage, help, bad commands, and argument-count validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHAAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitor.java

Purpose: this test verifies `HealthMonitor` state transitions and failure handling against a `DummyHAService`.

Important APIs and types: setup constructs a `HealthMonitor` with short intervals, overrides `createProxy()` to count attempts and optionally throw `OutOfMemoryError`, starts the monitor, and waits for `SERVICE_HEALTHY`. Tests drive `DummyHAService.isHealthy` and `actUnreachable`, add `HealthMonitor.Callback`, and use `shutdown()`/`join()`.

Control flow: `testMonitor()` moves from healthy to unhealthy, back to healthy, then to not responding via simulated unreachable RPC, verifies repeated proxy recreation, and finally recovers. `testHealthMonitorDies()` injects an uncaught error in proxy creation and waits for `HEALTH_MONITOR_FAILED`. `testCallbackThrowsRTE()` proves a throwing callback terminates the monitor into failed state.

State and persistence: state is thread-local/in-memory: monitor thread liveness, `HealthMonitor.State`, dummy service flags, `createProxyCount`, and `throwOOMEOnCreate`. No external persistence exists.

Dependencies and integration points: integrates HA service protocol proxy creation, Hadoop IPC retry configuration, monitor interval configuration, and JUnit timeouts.

Risks: waits poll for up to two seconds and assume short configured intervals are enough on loaded machines. The intentional `OutOfMemoryError` path tests broad failure capture and should not be confused with real heap exhaustion.

Test signals: verifies healthy/unhealthy/not-responding/recovered transitions, retry behavior on disconnection, clean shutdown, monitor failure on uncaught thread errors, and callback exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitorWithDedicatedHealthAddress.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitorWithDedicatedHealthAddress.java

Purpose: this subclass reuses all `TestHealthMonitor` cases with a `DummyHAService` that has a separate health-check RPC address, ensuring monitor behavior is identical when health probes are routed to a dedicated endpoint.

Important APIs and types: it overrides only `createDummyHAService()`, returning a `DummyHAService` with service address, health address, and auto-failover enabled.

Control flow: inherited setup and tests start the monitor, mutate service health/unreachability, and validate state transitions. The only control-flow difference is the target address chosen by `HealthMonitor` proxy creation.

State and persistence: all state comes from the inherited test: monitor thread state, dummy service flags, and proxy count. No durable state is introduced.

Dependencies and integration points: integrates dedicated health-address support in `HAServiceTarget`/`DummyHAService` with the generic `HealthMonitor` test suite.

Risks: because it inherits all tests, failures can be caused either by dedicated-address routing or base monitor behavior; debugging requires comparing against `TestHealthMonitor`.

Test signals: a pass confirms health monitoring, retries, failure-state propagation, and callback failure handling work when the HA service exposes a separate health RPC address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitorWithDedicatedHealthAddress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestNodeFencer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestNodeFencer.java

Purpose: this test validates parsing and execution sequencing for `NodeFencer` configurations, including custom fencer classes, comments/whitespace, no-argument methods, and short-name aliases for shell and SSH fencing.

Important APIs and types: `setupFencer()` builds a `NodeFencer` from a raw configuration string. Nested `AlwaysSucceedFencer` and `AlwaysFailFencer` implement `FenceMethod`, record static call counts, last fenced target, and arguments. Tests use a mocked `HAServiceTarget`.

Control flow: setup resets static mock fencer state and target behavior. Single and multiple fencer tests verify first success stops the chain. Whitespace/comment tests verify ignored lines and fallback from failing to succeeding fencer. Short-name tests resolve `shell` and `sshfence` forms; SSH variants return false in this environment rather than throwing.

State and persistence: state is in static counters and argument lists on the nested fencer classes. No files or network state are required except platform shell behavior for the shell alias.

Dependencies and integration points: integrates `NodeFencer`, `FenceMethod`, Hadoop `Configuration`, `Configured`, platform detection through `Shell.WINDOWS`, and short-name resolution to `ShellCommandFencer`/`SshFenceByTcpPort`.

Risks: static fencer state must be cleared before each test. Shell alias success differs between Windows and Unix, hence the platform-specific command constants.

Test signals: validates config parsing, arg extraction including null arg, ordered fallback semantics, comment stripping, target propagation, and alias recognition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestNodeFencer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestShellCommandFencer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestShellCommandFencer.java

Purpose: this test covers `ShellCommandFencer` command execution, configuration validation, subprocess IO handling, logging, environment variable injection, peer-aware variables, and command abbreviation.

Important APIs and types: a `ShellCommandFencer` is configured with a test property. `TEST_TARGET` is a `DummyHAService`. The test temporarily replaces static `ShellCommandFencer.LOG` with a Mockito logger using `LogAnswer` to delegate real log methods while enabling verification.

Control flow: tests run commands that succeed, return nonzero, or do not exist; construct invalid `NodeFencer` configs for missing shell args; verify stdout maps to info logs and stderr to warn logs; run platform-specific environment echo commands; and verify `read` exits because subprocess stdin is closed. Peer tests set transition target statuses so target/source environment variables are selected by role.

State and persistence: state is process environment built from Hadoop `Configuration` keys and target metadata. No persistent files are written. The static logger is restored in `AfterAll`.

Dependencies and integration points: depends on local shell semantics, Hadoop `Shell`, `NodeFencer` parser, `DummyHAService`, Mockito, and JUnit timeout for subprocess blocking detection.

Risks: shell behavior is platform-dependent, so tests branch on `Shell.WINDOWS`. Logger replacement is static and must be restored to avoid cross-test pollution.

Test signals: confirms exit-code-based fencing result, bad config diagnostics, stdout/stderr log routing with abbreviated command names, configuration-to-env key normalization, target/source host-port variables, closed stdin, and abbreviation boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestShellCommandFencer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestSshFenceByTcpPort.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestSshFenceByTcpPort.java

Purpose: this test covers SSH-based fencing through `SshFenceByTcpPort`, especially argument parsing and timeout behavior. The real fencing test is gated by system properties for host, port, and key file.

Important APIs and types: uses `SshFenceByTcpPort`, nested `Args`, `BadFencingConfigurationException`, `DummyHAService`, and JUnit assumptions. Configuration keys include identity file and connect timeout.

Control flow: `testFence()` runs only when configured and expects `tryFence()` to return true for the configured target. `testConnectTimeout()` points at an unfenceable address and verifies a false result within timeout. Parsing tests construct `Args` for null, empty, user-only, port-only, and user:port forms; bad parsing cases assert configuration exceptions.

State and persistence: test configuration comes from system properties. No persistent state is modified; network behavior depends on external host reachability for the gated real SSH case.

Dependencies and integration points: integrates JSch/SSH fencing behavior indirectly, Hadoop configuration, service target address extraction, and local user-name defaults.

Risks: the real SSH test is environment-sensitive and skipped unless properties are set. The timeout case uses a public IP and fixed port, so network policy can influence duration or result.

Test signals: confirms default user/port parsing, custom user and port parsing, bad arg rejection, configured identity use, and graceful false return on connection timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestSshFenceByTcpPort.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverController.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverController.java

Purpose: this integration suite validates `ZKFailoverController` end-to-end with `MiniZKFCCluster` and a real ZooKeeper server. It covers formatting, ACL/auth, fencer requirements, automatic failover, graceful failover, observer handling, ZooKeeper outages, RPC security policy, and multi-node election.

Important APIs and types: setup configures digest auth/ACL, `ZKFailoverController.ZK_QUORUM_KEY`, and `MiniZKFCCluster`. Tests use `DummyZKFC`, `DummyHAService`, `ActiveStandbyElector`, `ZKFCProtocol`, `ZKFCRpcServer`, `PolicyProvider`, `RefreshAuthorizationPolicyProtocol`, and `LambdaTestUtils`.

Control flow: command-line tests run `DummyZKFC.run()` with `-formatZK`, `-force`, and `-nonInteractive`. Runtime tests start two or three ZKFCs, mutate health/state/failure flags, expire sessions, stop and restart ZooKeeper, invoke `cedeActive()` and `gracefulFailover()`, and wait for lock-holder or HA/elector states. Graceful failover cases validate success, unhealthy target rejection, observer rejection, active transition failure rollback, standby transition failure fencing, and fence failure propagation.

State and persistence: persistent state is ZooKeeper parent, lock, breadcrumb, ACLs, and auth. Runtime state includes HA service state, health monitor state, elector state, fencer counts, transition counts, and ZK sessions. ACL formatting is verified by unauthenticated ZooKeeper read failure.

Dependencies and integration points: integrates ZooKeeper, ZKFC command parsing, automatic failover enablement, fencer checks, HA RPC, service authorization policy, digest ACLs, and the mini harness.

Risks: heavy asynchronous coverage is bounded by a class-level timeout but can be sensitive to scheduling. ACL tests depend on digest auth correctness. Some cases rely on exact exception text fragments.

Test signals: verifies expected error codes for no parent, no ZK, denied format, disabled auto-failover, and missing fencer; correct failover on bad health/state/lost sessions; no failover during ZK outage; cede-active delay semantics; no fencing on clean graceful failover; fencing when graceful standby fails; and three-ZKFC transition counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverControllerStress.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverControllerStress.java

Purpose: this stress test repeatedly perturbs `ZKFailoverController` clusters to catch race conditions, fatal thread exceptions, and shared-resource split-brain during rapid automatic failovers.

Important APIs and types: uses `MiniZKFCCluster`, real ZooKeeper server from `ClientBaseWithFixes`, `ActiveStandbyElector`, `ServerCnxn.DisconnectReason`, Mockito `Answer`, and `RandomlyThrow` to inject intermittent health failures.

Control flow: setup creates a cluster with `ZK_QUORUM_KEY`. `testExpireBackAndForth()` repeatedly expires active sessions in alternating directions and verifies failover. `testRandomExpirations()` randomly expires any current elector session and checks the test context for exceptions. `testRandomHealthAndDisconnects()` configures high elector retry count, randomly fails health checks, starts the cluster after mocking, then closes all ZooKeeper server connections every 50 ms.

State and persistence: state includes ZK sessions, health monitor results, random health-check exceptions, HA roles, and shared-resource ownership checked during cluster stop. ZooKeeper lock state is continuously recreated through elections.

Dependencies and integration points: depends on real ZooKeeper connection management, HA health monitor callbacks, `MiniZKFCCluster` wait/exception propagation, and Mockito partial real-method invocation.

Risks: intentionally nondeterministic random behavior can expose races but may be flaky under slow CI. Runtime is fixed at 30 seconds plus timeout cushion, making this expensive relative to unit tests.

Test signals: no uncaught exceptions, successful repeated failovers, and no shared-resource violations on teardown indicate the ZKFC system tolerates repeated session expiration, health instability, and disconnect storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverControllerStress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ZKFCTestUtil.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ZKFCTestUtil.java

Purpose: `ZKFCTestUtil` provides a small wait helper for ZK failover controller tests.

Important APIs and types: `waitForHealthState(ZKFailoverController zkfc, HealthMonitor.State state, MultithreadedTestUtil.TestContext ctx)` polls `zkfc.getLastHealthState()` until it equals the expected state.

Control flow: the method loops, optionally calls `ctx.checkException()` to surface background-thread failures, then sleeps 50 ms between checks. It has no internal timeout and relies on the caller's test timeout or surrounding harness.

State and persistence: no state is mutated except thread sleep timing. The observed state is the ZKFC's last health monitor state.

Dependencies and integration points: used by `MiniZKFCCluster.waitForHealthState()` and tests that need background ZKFC exceptions propagated while waiting.

Risks: lack of timeout can hang if callers omit a JUnit timeout or context cancellation. It intentionally favors simple polling over richer synchronization.

Test signals: enables deterministic-ish waits for health state transitions while preserving failure visibility from `MultithreadedTestUtil.TestContext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ZKFCTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/HttpServerFunctionalTest.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/HttpServerFunctionalTest.java

Purpose: this base class centralizes helpers for `HttpServer2` functional tests: creating local test servers, preparing webapp directories, stopping servers, deriving base URLs, reading responses, and testing large request headers.

Important APIs and types: exposes `LongHeaderServlet`, `createTestServer()` overloads, `createServer()` overloads, `createAndStartTestServer()`, `stop()`, `getServerURL()`, `readOutput()`, and `testLongHeader()`. It extends JUnit `Assertions`.

Control flow: creation helpers call `prepareTestWebapp()` when needed, then configure `HttpServer2.Builder` with localhost endpoint, find-port behavior, optional configuration, ACL, path specs, or X-Frame options. `readOutput()` streams a URL response into a string. `testLongHeader()` sends a 63 KiB header and expects HTTP 200.

State and persistence: creates the test webapp directory under `test.build.webapps` or `build/test/webapps`. Static `baseUrl` is shared by subclasses. Servers bind ephemeral local ports.

Dependencies and integration points: integrates `HttpServer2.Builder`, Jetty servlet API, Hadoop `Configuration`, `AccessControlList`, and `NetUtils`.

Risks: `prepareTestWebapp()` swallows `IOException` after mkdir attempts, so canonical-path failures may be hidden unless mkdir itself returns false. Static `baseUrl` can be overwritten by subclasses.

Test signals: used throughout HTTP tests to guarantee consistent local server construction, cleanup, URL derivation, and 64 KiB header coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/HttpServerFunctionalTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestAuthenticationSessionCookie.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestAuthenticationSessionCookie.java

Purpose: this test verifies `AuthenticationFilter.createAuthCookie()` behavior as surfaced through `HttpServer2` filters, distinguishing session cookies from persistent cookies.

Important APIs and types: defines `DummyAuthenticationFilter`, `DummyFilterInitializer`, `Dummy2AuthenticationFilter`, and `Dummy2FilterInitializer`. `startServer(boolean)` configures filter initializer, temporary keystores, HTTP and HTTPS endpoints, SSL key/trust stores, and an `/echo` servlet.

Control flow: session-cookie mode initializes `isCookiePersistent=false`; persistent mode sets `isCookiePersistent=true` and `expires` to current time plus a token validity interval. Both tests request `/echo`, parse the `Set-Cookie` header with `HttpCookie.parse()`, and assert token value plus presence or absence of `Expires`.

State and persistence: temporary SSL material is created under `GenericTestUtils.getTempPath(...)` and removed in `cleanup()`. Static fields hold server, SSL paths, persistence flag, and expiry value.

Dependencies and integration points: integrates Hadoop authentication filter cookie creation, `HttpServer2` filter initialization, `KeyStoreTestUtil`, Jetty/servlet filtering, and `TestHttpServer.EchoServlet`.

Risks: exception handling in tests prints stack traces but continues, which can obscure setup failures until later null/server assertions. Static mutable cookie flags couple filter initialization and request handling.

Test signals: asserts session cookies omit `Expires`, persistent cookies include it, and both carry the expected token value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestAuthenticationSessionCookie.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestDisabledProfileServlet.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestDisabledProfileServlet.java

Purpose: this test covers the default disabled `/prof` endpoint when async profiling is not enabled.

Important APIs and types: uses `HttpServerFunctionalTest` helpers, `ProfileServlet.ACCESS_CONTROL_ALLOW_METHODS`, `ACCESS_CONTROL_ALLOW_ORIGIN`, and `HttpServletResponse` status constants.

Control flow: class setup starts a default test server and records `baseUrl`. `testQuery()` expects reading `/prof` to fail with an internal-server-error URL message, then separately opens a connection to assert CORS headers. `testRequestMethods()` sends PUT, POST, DELETE, and GET to `/prof` and verifies method-not-allowed for mutating verbs and internal server error for GET.

State and persistence: only an in-process `HttpServer2` is started and stopped. No profiler files are expected because profiling is disabled.

Dependencies and integration points: integrates `ProfileServlet` registration in default `HttpServer2` webapp and CORS header behavior.

Risks: asserting the IOException message contains a specific URL/status fragment may vary across JDK URLConnection implementations. The GET failure is expected behavior for disabled profiling, not a test infrastructure failure.

Test signals: validates disabled profile servlet status codes and CORS metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestDisabledProfileServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestGlobalFilter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestGlobalFilter.java

Purpose: this test verifies that a global `FilterInitializer` applies a servlet filter to all relevant `HttpServer2` paths, including static, servlet, JSP-like, and default endpoints.

Important APIs and types: nested `RecordingFilter` implements `Filter` and records request URIs in static `RECORDS`. Its `Initializer` calls `container.addGlobalFilter(...)`. The static `access()` helper opens URLs and drains or ignores responses.

Control flow: `testServletFilter()` configures the initializer, starts a test server, accesses a list of paths, stops the server, then removes each expected URI from `RECORDS`. It expects one extra `/index.html` record because `/` redirects.

State and persistence: static `RECORDS` is the main state; it is a `TreeSet` of observed URIs. The server is local and ephemeral. No durable files are written.

Dependencies and integration points: integrates servlet filters, `FilterContainer.addGlobalFilter`, default Hadoop HTTP endpoints, static content serving, redirects, and `NetUtils`.

Risks: static `RECORDS` is not cleared inside the test, so repeated execution in the same JVM could retain prior entries. The test tolerates HTTP errors when paths are missing because it only needs filter invocation.

Test signals: confirms global filters see all configured URL classes and root redirect handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestGlobalFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHtmlQuoting.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHtmlQuoting.java

Purpose: this unit test validates HTML escaping/unescaping utilities and request-parameter quoting used by `HttpServer2.QuotingInputFilter`.

Important APIs and types: tests `HtmlQuoting.needsQuoting()`, `quoteHtmlChars()`, `unquoteHtmlChars()`, and `HttpServer2.QuotingInputFilter.RequestQuoter`. Mockito supplies a mock `HttpServletRequest`.

Control flow: quoting tests cover all escapable characters (`<`, `>`, `&`, apostrophe, quote), empty strings, newline-only strings, and nulls. Round-trip tests quote then unquote representative strings and all ASCII characters below 127. Request quoting verifies single parameter and array parameter escaping plus null behavior.

State and persistence: no external state or persistence. State is local strings and mocked request return values.

Dependencies and integration points: integrates utility escaping with the request wrapper used by HTTP server filters to protect servlet consumers from raw HTML metacharacters.

Risks: expected escaping format is strict, so any change from named entities to numeric entities would require test updates even if semantically equivalent.

Test signals: confirms no NPE on missing params, arrays are quoted element-wise, non-quotable input remains stable through round trip, and dangerous HTML characters are escaped consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHtmlQuoting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpCookieFlag.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpCookieFlag.java

Purpose: this functional test verifies authentication cookie flags over HTTP and HTTPS: all auth cookies should be `HttpOnly`, and HTTPS cookies should also be secure.

Important APIs and types: nested `DummyAuthenticationFilter` creates an auth cookie based on `request.getScheme()`. `DummyFilterInitializer` registers it. Setup creates HTTP and HTTPS endpoints with generated SSL material and a client `SSLFactory`.

Control flow: `setUp()` builds the server, adds `/echo`, and starts it. `testHttpCookie()` requests HTTP `/echo`, parses `Set-Cookie`, and asserts `HttpOnly` and token value. `testHttpsCookie()` requests HTTPS `/echo` with the client SSL socket factory and additionally asserts `HttpCookie.getSecure()`.

State and persistence: temporary keystore/truststore files live under a test temp path and are cleaned in `AfterAll`. Static server and SSL factory are shared across methods.

Dependencies and integration points: integrates Hadoop auth cookie generation, servlet filters, `HttpServer2` dual-protocol endpoint setup, `KeyStoreTestUtil`, and `SSLFactory`.

Risks: relies on generated local certificates and Java HTTPS behavior. Header string inspection checks `HttpOnly` literally, while secure flag uses parsed cookie state.

Test signals: validates expected cookie hardening for both cleartext and TLS endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpCookieFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpRequestLog.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpRequestLog.java

Purpose: this small unit test verifies the request-log factory for `HttpServer2`.

Important APIs and types: calls `HttpRequestLog.getRequestLog("test")` and asserts the returned Jetty `RequestLog` is a `CustomRequestLog` using a `Slf4jRequestLogWriter` and `CustomRequestLog.EXTENDED_NCSA_FORMAT`.

Control flow: single test method obtains the log and checks type and format. No server is started.

State and persistence: no persistent state. The test only inspects constructed logging objects.

Dependencies and integration points: integrates Hadoop `HttpRequestLog` with Jetty request-log APIs and SLF4J writer selection.

Risks: tightly coupled to Jetty implementation classes and the exact selected log format. Jetty upgrades that change class names or defaults can break it.

Test signals: confirms request logging is configured and uses extended NCSA format through SLF4J.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpRequestLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServer.java

Purpose: this broad functional suite validates core `HttpServer2` behavior: servlet registration, parameter quoting, static content types, max threads, connector configuration, metrics, security headers, X-Frame options, default servlet authorization, Jersey resources, bind/find-port behavior, port ranges, backlog, idle timeout, and custom headers.

Important APIs and types: nested servlets include `EchoServlet`, `EchoMapServlet`, and `HtmlContentServlet`. Security helpers include `DummyServletFilter`, `DummyFilterInitializer`, `getHttpStatusCode()`, and `MyGroupsProvider`. Tests use `HttpServer2.Builder`, `HttpServer2Metrics`, `RequestQuoter`, `AccessControlList`, Jetty `ServerConnector`, `StatisticsHandler`, and Jersey `JerseyResource`.

Control flow: `BeforeAll` creates a server with max threads and metrics enabled, registers servlets and Jersey package, and starts it. Tests then perform concurrent requests, bad acceptor/selector config, echo/echomap quoting checks, long headers, MIME checks, metrics increments, X-Frame header enabled/disabled/invalid cases, admin authorization matrix for `/conf`, `/logs`, `/stacks`, `/logLevel`, Jersey JSON parsing, bind reuse and find-port checks, port-range allocation, socket backlog/idle timeout reflection, and default/custom header checks.

State and persistence: state includes a shared static server/base URL, custom group mapping static map, server metrics counters, Jetty connector state, and servlet context attributes. No durable application data is written.

Dependencies and integration points: integrates servlet filters, Hadoop security groups and ACLs, Jetty connectors/thread pool/statistics, JSON parsing, JAX-RS resources, Hadoop configuration keys, and network port utilities.

Risks: this file touches many shared server behaviors; failures may be environmental (ports, thread scheduling) or behavior regressions. Static `server` is reused and reassigned in `testAddConnectors`, so lifecycle care matters. Some tests rely on reflection into private listener fields.

Test signals: strong coverage for server construction, request handling, security and cache headers, authorization behavior, resource packages, connector lifecycle, metrics, and configuration-driven network behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLifecycle.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLifecycle.java

Purpose: this test verifies `HttpServer2` lifecycle state reporting and context cleanup.

Important APIs and types: helper assertions use `HttpServer2.isAlive()` and `toString()` state descriptions `STATE_DESCRIPTION_ALIVE` and `STATE_DESCRIPTION_NOT_LIVE`. It uses inherited server creation and `stop()` helpers.

Control flow: tests check a created but unstarted server is not live, stopping an unstarted server is allowed, a started server reports live, a stopped server reports not live, stopping twice is idempotent, and servlet-context attributes are cleared after stop.

State and persistence: state is in the server instance and webapp context attributes. No durable files are written beyond inherited test webapp preparation.

Dependencies and integration points: integrates lifecycle methods of `HttpServer2`, context attribute access, and textual `toString()` diagnostics.

Risks: string-based assertions on `toString()` can break if diagnostics are reworded while behavior remains correct. The method name `testWepAppContextAfterServerStop` contains a typo but tests webapp context cleanup.

Test signals: validates idempotent stop behavior, live/not-live reporting, and cleanup of context state after shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLifecycle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLogs.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLogs.java

Purpose: this functional test checks whether the `/logs` servlet is registered according to `HADOOP_HTTP_LOGS_ENABLED`.

Important APIs and types: `startServer(Configuration)` creates and starts a test server, sets `baseUrl`, and uses `HttpServerFunctionalTest` helpers. Tests use Apache `HttpStatus`, `CommonConfigurationKeysPublic.HADOOP_HTTP_LOGS_ENABLED`, and `NetUtils`.

Control flow: `testLogsEnabled()` enables logs, starts the server, requests `/logs`, and expects HTTP 200. `testLogsDisabled()` disables logs, starts the server, requests `/logs`, and expects HTTP 404. Cleanup stops a live server after all tests.

State and persistence: static `server` and `baseUrl` are overwritten by each test. No log files are inspected; the test only checks endpoint availability.

Dependencies and integration points: integrates `HttpServer2` default servlet registration with public configuration keys.

Risks: because `server` is static and each test calls `startServer()`, a prior started server must be stopped by cleanup or test isolation. The tests do not verify log content, only servlet routing.

Test signals: confirms `/logs` is present or absent based on configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLogs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWebapps.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWebapps.java

Purpose: this test validates webapp resource resolution for `HttpServer2`.

Important APIs and types: uses `createServer(String webapp)` and `stop()` from `HttpServerFunctionalTest`, with `FileNotFoundException` expected for missing resources.

Control flow: `testValidServerResource()` creates the standard `test` webapp server and stops it. `testMissingServerResource()` attempts to create `NoSuchWebapp`, expects `FileNotFoundException`, and fails if a server is returned.

State and persistence: no persistent server state; inherited helper may prepare the test webapp directory. Missing-webapp test only observes classpath/resource lookup.

Dependencies and integration points: integrates `HttpServer2` webapp lookup with test resource packaging.

Risks: depends on build/test resources being available on the classpath. If an invalid webapp is accidentally added, the negative test would fail.

Test signals: confirms valid webapp resources load and missing webapp names fail fast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWebapps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWithSpnego.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWithSpnego.java

Purpose: this integration test validates `HttpServer2` with SPNEGO/Kerberos authentication, proxy-user authorization, admin ACLs, and authentication endpoint allow-list behavior.

Important APIs and types: uses `MiniKdc`, Kerberos test utilities, `AuthenticationFilterInitializer`, `ProxyUserAuthenticationFilterInitializer`, `AuthenticatedURL`, signed `AuthenticationToken`s, `Signer`, `SignerSecretProvider`, `ProxyUsers`, `AccessControlList`, and `HttpServer2.Builder`.

Control flow: `BeforeAll` starts a MiniKDC, creates an HTTP service principal/keytab, and writes a signer secret file. `testAuthenticationWithProxyUser()` configures proxy-user SPNEGO, creates users/groups, allows userA to impersonate groupB, starts a server with admin ACL, signs tokens for userA and userB, and checks impersonated access to default servlets plus admin-only access to `/logs` and `/logLevel`. `testAuthenticationToAllowList()` configures a whitelist for `/jmx` and `/prom`, enables Prometheus, starts a security-enabled server, and verifies whitelisted endpoints skip Kerberos while others return unauthorized.

State and persistence: writes keytab and secret file under target test root; MiniKDC holds Kerberos state; system property `hadoop.log.dir` points at the test root. Server state is local and stopped in finally blocks.

Dependencies and integration points: integrates Hadoop auth filters, Kerberos, proxy-user configuration, signed cookie/token authentication, admin ACL checks, default servlet security, and Prometheus endpoint exposure.

Risks: MiniKDC setup is environment-sensitive and uses a broad `assertTrue(false)` on setup failure. Tokens are manually signed, so the test bypasses live Kerberos exchange after server setup while still testing server-side filter behavior.

Test signals: validates allowed and denied proxy impersonation, admin vs non-admin access to sensitive servlets, and whitelist bypass for selected endpoints under SPNEGO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWithSpnego.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestIsActiveServlet.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestIsActiveServlet.java

Purpose: this unit test validates `IsActiveServlet` response behavior for active and inactive services.

Important APIs and types: uses an anonymous `IsActiveServlet` overriding `isActive()`, mocked `HttpServletRequest` and `HttpServletResponse`, `ByteArrayOutputStream`, and `PrintWriter`.

Control flow: setup wires the mocked response writer to a byte buffer. `testSucceedsOnActive()` returns true from `isActive()`, calls `doGet()`, verifies no error response, and asserts the active response body. `testFailsOnInactive()` returns false and verifies `sendError(SC_METHOD_NOT_ALLOWED, RESPONSE_NOT_ACTIVE)`.

State and persistence: all state is in mocks and an in-memory response buffer. No server is started and no files are written.

Dependencies and integration points: validates the servlet contract consumed by HTTP health/readiness probes for HA-aware services.

Risks: direct servlet invocation avoids container behavior, so it only tests servlet method logic and response interactions.

Test signals: confirms active requests produce the expected response body and inactive requests return method-not-allowed with the expected message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestIsActiveServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestPathFilter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestPathFilter.java

Purpose: this test is intended to verify that non-global filters are applied only to configured path specs.

Important APIs and types: nested `RecordingFilter` records request URIs in static `RECORDS`, and its initializer calls `container.addFilter(...)`. `testPathSpecFilters()` builds a test server with path specs `"/path"` and `"/path/*"`.

Control flow: the test starts a server, accesses filtered paths and unfiltered paths, stops the server, then asserts only filtered paths were recorded. The access helper drains successful responses and ignores IOExceptions for missing pages.

State and persistence: static `RECORDS` tracks observed filtered URIs. The server is local and temporary; no durable state is touched.

Dependencies and integration points: integrates `HttpServer2` path-spec handling, filter initializers, servlet filter dispatch, and URL access through `NetUtils`.

Risks: the method lacks a visible `@Test` annotation in the source, so under JUnit 5 it may not execute unless another mechanism discovers it. Static `RECORDS` is not cleared before use.

Test signals: when executed, it proves filters registered with path specs apply to `/path` and descendants but not `/` or wildcard literal paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestPathFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestProfileServlet.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestProfileServlet.java

Purpose: this functional test covers the enabled/test-run behavior of async profiler servlets `/prof` and `/prof-output-hadoop`.

Important APIs and types: setup calls `ProfileServlet.setIsTestRun(true)`, sets `async.profiler.home` to a random UUID string, starts a test server, and uses profile servlet CORS and refresh headers.

Control flow: `testQuery()` reads `/prof` and expects a started-profiling message plus async-profiler guidance. It opens `/prof` again to assert allowed methods, HTTP 202 Accepted, CORS origin, and a refresh header pointing at a generated profiler output path. It then reads and checks `/prof-output-hadoop` returns HTTP 200.

State and persistence: global test-run flag and JVM property are modified in setup and restored in cleanup. The server is local and stopped after all tests. Profiler output is simulated by test-run mode rather than requiring a real async-profiler installation.

Dependencies and integration points: integrates `ProfileServlet`, `ProfileOutputServlet`, default server registration, CORS headers, and refresh/redirect behavior.

Risks: depends on global static servlet test mode and a JVM system property, so cleanup is essential. Assertions include output text and header prefix details.

Test signals: validates enabled profile endpoint response, CORS metadata, accepted status, refresh target, and output endpoint availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestProfileServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServer.java

Purpose: this functional suite validates HTTPS support in `HttpServer2`: generated keystores, SSL client connectivity, echo servlet behavior, long headers, excluded/included cipher suites, and enabled protocol negotiation.

Important APIs and types: setup uses `KeyStoreTestUtil`, `SSLFactory`, `HttpServer2.Builder`, `EchoServlet`, `LongHeaderServlet`, and custom inner `PreferredCipherSSLSocketFactory`/`PreferredProtocolSSLSocketFactory`. Constants define excluded cipher lists, one-enabled cipher sets for TLS 1.2 and TLS 1.3, and enabled protocols.

Control flow: `BeforeAll` clears JVM `https.cipherSuites`, enables `javax.net.debug`, creates SSL material, initializes a client `SSLFactory`, builds an HTTPS server, registers servlets, and starts it. Tests request `/echo`, send a 63 KiB header, try excluded-only ciphers expecting `SSLHandshakeException`, verify negotiated TLS protocol based on Java version, and verify successful connections with at least one mutually enabled cipher. Cleanup stops the server, deletes SSL material, destroys the client factory, and restores JVM properties.

State and persistence: temporary keystore/truststore files are written under a test temp path. JVM SSL-related system properties are saved and restored. The preferred protocol socket factory records the last `SSLSocket` to inspect negotiated protocol.

Dependencies and integration points: integrates Jetty HTTPS connectors, Hadoop SSL config generation, Java TLS stack, cipher/protocol filtering, Hadoop IO utilities, and platform Java version detection.

Risks: TLS cipher availability varies by JDK and security policy; the test branches for Java 11+ TLS 1.3 but still depends on supported cipher names. Turning on global SSL debug logging can produce large logs and must be restored.

Test signals: validates secure servlet serving, request quoting over HTTPS, large headers over TLS, exclusion of insecure ciphers, protocol inclusion, and successful mutually compatible cipher negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServer.java -->
