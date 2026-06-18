# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/ExceptionAsserts.java

## Purpose
`ExceptionAsserts` is a tiny prefetch-test helper that wraps Hadoop's `LambdaTestUtils.intercept()` for exception assertions.

## Important APIs, Types, And Functions
It is a final utility class with a private constructor and two overloaded `assertThrows()` methods: one checks exception type plus partial message, the other checks only type.

## Control Flow
Both methods delegate directly to `intercept()`. There is no additional branching beyond overload selection.

## State And Persistence
The class has no state and no side effects except throwing assertion failures through the underlying test utility.

## Dependencies And Integration Points
Prefetch unit tests use this helper for concise argument/state validation. It depends on `LambdaTestUtils.VoidCallable`.

## Risks
The comment references older JUnit migration concerns while the file is now in JUnit 5 era; behavior still depends on Hadoop's intercept implementation rather than JUnit assertions.

## Test Signals
Signals are precise exception class and message substring matching in prefetch tests.
