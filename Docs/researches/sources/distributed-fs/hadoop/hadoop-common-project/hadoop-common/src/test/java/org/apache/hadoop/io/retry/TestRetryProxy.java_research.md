# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestRetryProxy.java

## Purpose
`TestRetryProxy` exercises `RetryProxy` and `RetryInvocationHandler` behavior for fixed, forever, exponential, exception-mapped, interruptible, and security-sensitive retry policies.

## Important APIs, Types, and Functions
The test creates proxies for `UnreliableInterface` backed by `UnreliableImplementation`. `setupMockPolicy()` wraps a mocked `RetryPolicy` so calls delegate to a real policy while capturing the returned `RetryAction`. It uses `RetryPolicies` factories, `RetryInvocationHandler.isRpcInvocation()`, `ProtocolTranslator`, `RemoteException`, `SaslException`, and `AccessControlException`.

## Control Flow
Each policy test invokes fixture methods with known failure counters and verifies success, failure, retry-call counts, and action reasons. Exception-mapping tests route fatal or remote exceptions to specific policies. `testRetryInterruptible()` runs a long-sleep retry in an executor, interrupts the sleeping thread, and expects `InterruptedIOException`. Security tests assert SASL and access-control failures do not retry beyond the initial decision.

## State and Persistence
Per-test state is a fresh `UnreliableImplementation` plus captured `caughtRetryAction`. Thread and executor state is created only for interrupt handling. No filesystem persistence is used.

## Dependencies and Integration Points
The suite depends on Mockito, Java reflection proxy behavior, Hadoop retry policies, `ProtocolTranslator` unwrapping, IPC `RemoteException`, and Hadoop security exceptions. It protects client retry semantics used throughout Hadoop RPC clients.

## Risks and Edge Cases
Mockito verification ties tests to exact `shouldRetry()` call counts. Interrupt timing includes a one-second sleep before interruption. Some fixture methods are annotated idempotent for retry testing even when not truly idempotent.

## Test Signals
Signals include correct retry/fail decisions and reason strings, successful retry for transient fixture failures, no retry for SASL/access-control exceptions, correct RPC proxy detection including translator wrappers, and immediate interrupt conversion to `InterruptedIOException`.
