# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestFunctionalIO.java

Purpose: Unit tests for functional wrappers that convert checked `IOException`-throwing lambdas into unchecked Java functional interfaces and back. It protects helper behavior used when IO operations must pass through APIs that cannot throw checked IOExceptions.

Important APIs/types/functions: Tests statically import `FunctionalIO.uncheckIOExceptions()`, `toUncheckedIOExceptionSupplier()`, `extractIOExceptions()`, and `toUncheckedFunction()`. They use `UncheckedIOException`, `FileNotFoundException`, and Hadoop `LambdaTestUtils.intercept()`.

Control flow: `testUncheckIOExceptions()` throws a checked `IOException` inside a lambda and asserts it is wrapped with the same cause. `testUncheckIOExceptionsUnchecked()` verifies an existing `UncheckedIOException` is propagated rather than double-wrapped. Supplier and function tests verify conversion of throwing suppliers/functions to unchecked forms. `testUncheckAndExtract()` wraps an IO exception then extracts it back as the original checked exception.

State and persistence behavior: Stateless functional tests with only local exception instances. Cause identity is asserted where important.

Dependencies and integration points: Depends on Hadoop functional IO interfaces, Java `Function`, JUnit, AssertJ, and `LambdaTestUtils`. These utilities integrate IO-heavy Hadoop operations with Java streams, reflection, suppliers, and callbacks.

Risks: Wrapper code must preserve original causes and avoid double wrapping; otherwise callers lose exception identity/type. The tests cover IOExceptions only and do not deeply exercise non-IO runtime exceptions or interrupted operations.

Test signals: Same-cause assertions, same unchecked exception instance propagation, expected message matching, and `FileNotFoundException` wrapping through a `Function` are the key signals.
