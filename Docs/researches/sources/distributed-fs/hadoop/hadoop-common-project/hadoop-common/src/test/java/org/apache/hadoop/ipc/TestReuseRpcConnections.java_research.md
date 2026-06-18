# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestReuseRpcConnections.java

Purpose: verifies RPC connection reuse behavior across retry policies, especially that normal retry paths reuse the same client connection while `TRY_ONCE_THEN_FAIL` does not perform extra retries.

Important APIs/types/functions: `TestRpcBase`, `RetryProxy`, `RetryPolicies`, `UnreliableInterface`, `UnreliableImplementation`, `UnreliableException`, `TestRpcService`, `ProtobufRpcEngine2`, and `Client.getConnectionIds()`.

Control flow: setup configures protobuf RPC and resets `UnreliableImplementation` counters. `testDefaultRetryPolicyReuseConnections()` delegates to `verifyRetryPolicyReuseConnections()` with the default retry policy; the helper creates server/proxy, wraps a failover/retry proxy around an unreliable implementation, triggers failing/succeeding calls, and checks the protobuf client's connection ID set size to ensure connection reuse. `testRetryPolicyTryOnceThenFail()` verifies a no-retry policy fails after one unreliable invocation.

State and persistence behavior: connection reuse state lives in the protobuf engine client cache and connection ID set; unreliable operation counters are static/test-local and reset before each test. Servers/proxies are stopped after use.

Dependencies and integration points: ties retry proxy behavior to RPC client connection cache behavior and unreliable protocol semantics.

Risks and test signals: important signal for avoiding connection churn during retries. It is sensitive to shared client cache cleanup; failure to clear/stop proxies could make connection counts misleading.
