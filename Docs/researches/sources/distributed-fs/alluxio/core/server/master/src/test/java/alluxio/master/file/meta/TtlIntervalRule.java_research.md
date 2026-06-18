# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlIntervalRule.java

## Purpose
`TtlIntervalRule` is a JUnit rule that temporarily overrides the static TTL bucket interval for deterministic TTL tests.

## Important APIs, Types, and Functions
The class implements `TestRule`, stores `mIntervalMs`, and returns a `Statement` from `apply`. During `evaluate`, it reads `TtlBucket.getTtlIntervalMs`, uses PowerMock `Whitebox.setInternalState` to set `TtlBucket.sTtlIntervalMs`, runs the wrapped statement, and restores the previous value in `finally`.

## Control Flow, State, and Persistence
The rule mutates static process state only for the duration of a test or class rule. The `finally` block is the persistence boundary preventing interval leakage into later tests.

## Dependencies and Integration Points
It depends on JUnit rules/statements, PowerMock reflection, and the private static field name in `TtlBucket`.

## Risks
The rule is brittle to renaming `sTtlIntervalMs` or removing mutable static state. Parallel TTL tests would share the global interval and could interfere.

## Test Signals
Its primary signal is indirect: TTL bucket tests can assert exact bucket boundaries without depending on production configuration.
