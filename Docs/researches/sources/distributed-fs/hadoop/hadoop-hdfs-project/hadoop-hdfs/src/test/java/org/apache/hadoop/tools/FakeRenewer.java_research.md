# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/FakeRenewer.java

## Purpose
`FakeRenewer` is a test `TokenRenewer` that records the last renewed and canceled token for tests of delegation-token tooling.

## Important APIs, types, and functions
- `KIND` is the token kind handled by this renewer.
- `handleKind(Text)` returns true only for `KIND`.
- `isManaged(Token<?>)` always returns true.
- `renew(Token<?>, Configuration)` records `lastRenewed` and returns `0`.
- `cancel(Token<?>, Configuration)` records `lastCanceled`.
- `reset`, `getLastRenewed`, and `getLastCanceled` expose static test state.

## Control flow
The renewer is invoked by Hadoop token-renewal service discovery. It accepts a test token kind, records side effects on renew/cancel, and otherwise performs no real external operation.

## State and persistence behavior
State is held in static fields `lastRenewed` and `lastCanceled`. `reset()` must be called by tests to avoid cross-test leakage.

## Dependencies and integration points
It integrates Hadoop security token APIs: `TokenRenewer`, `Token`, `Text`, and `Configuration`. It is typically discovered through service-provider configuration in tests.

## Risks and edge cases
The static fields are not synchronized, so parallel tests using this renewer can race. Since `renew` returns zero and `isManaged` always returns true, it is a behavior stub rather than a realistic renewer.

## Test signals
Consumers can assert that command-line token tools or token-management code invoked renew/cancel on the expected token by checking the static recorded values.
