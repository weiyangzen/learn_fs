# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/LambdaTestUtils.java

Purpose: Java-8-friendly test utilities for lambda-based retries, eventual assertions, exception interception, optional assertions, checked-exception wrapping, UGI `doAs`, future exception unwrapping, and retry policies.

Important APIs/types/functions: `await`, `eventually`, many overloads of `intercept`, `interceptAndValidateMessageContains`, `assertOptionalEquals`, `assertOptionalUnset`, `eval`, `notNull`, `doAs`, `interceptFuture`, `verifyCause`, `TimeoutHandler`, `GenerateTimeout`, `FixedRetryInterval`, `ProportionalRetryInterval`, `FailFastException`, `VoidCallable`, `VoidCaller`, `PrivilegedOperation`, and `PrivilegedVoidOperation`.

Control flow: `await` repeatedly evaluates a boolean callable with pluggable retry and timeout exception generation. `eventually` retries a value/void closure until it succeeds or timeout expires. Intercept helpers execute callables and return expected exceptions, rethrowing wrong types and validating text. Future helpers unwrap `ExecutionException` causes before applying intercept logic.

State and persistence behavior: retry policy classes keep invocation/current interval counters in memory. No persistent state.

Dependencies and integration points: integrates JUnit assertions, `GenericTestUtils.assertExceptionContains`, Hadoop `Preconditions`, `Time`, and `UserGroupInformation.doAs`.

Risks and test signals: central to async/flaky-condition tests. Risks include masking non-retryable errors if callers do not use `FailFastException`; code explicitly rethrows interruption, virtual machine errors, and fail-fast exceptions. Signals include robust assertion messages and nested-future cause validation.
