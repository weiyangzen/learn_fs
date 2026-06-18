<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryUtils.java

## Purpose
`RetryUtils` builds configured default retry policies, especially `MultipleLinearRandomRetry` wrappers that selectively retry IO, protobuf service, retriable, and configured remote exceptions.

## Important APIs and Types
`getDefaultRetryPolicy` reads enable/spec configuration and returns either `TRY_ONCE_THEN_FAIL` or a `WrapperRetryPolicy`. `getMultipleLinearRandomRetry` returns the parsed configured policy, the parsed default policy on parse failure, or null when disabled. `WrapperRetryPolicy` unwraps `ServiceException`, picks the nested policy, and defines equality/hash based on the multiple-linear policy.

## Control Flow
The utility first checks the enable flag. If enabled, it parses the policy spec string of sleep/retry pairs. The wrapper chooses multiple-linear retry for `RetriableException`, wrapped retriable remote exceptions, a configured remote exception class name, non-remote IOExceptions, and ServiceExceptions; otherwise it chooses `TRY_ONCE_THEN_FAIL`.

## State and Persistence
The class is stateless except logger. Wrapper instances store the selected multiple-linear policy and remote exception class name. No persistent state exists.

## Dependencies and Integration Points
It integrates with `Configuration`, `RetryPolicies.MultipleLinearRandomRetry`, Hadoop IPC `RemoteException`/`RetriableException`, protobuf `ServiceException`, and retry users that define configuration keys.

## Risks and Edge Cases
If both configured and default policy specs fail to parse, `getMultipleLinearRandomRetry` can return null even when enabled. `WrapperRetryPolicy.equals` ignores `remoteExceptionToRetry`, which is documented for connection-failure handling but can surprise if comparing full semantics. Logging format includes retry count and policy class. ServiceException unwrapping only occurs when cause is an `Exception`.

## Test Signals
Tests should cover disabled policies, valid and invalid specs, fallback parsing, remote-exception class matching, service exception unwrapping, wrapped retriable exceptions, equality/hash behavior with different remote exception names, and non-IO fail-fast behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryUtils.java -->
