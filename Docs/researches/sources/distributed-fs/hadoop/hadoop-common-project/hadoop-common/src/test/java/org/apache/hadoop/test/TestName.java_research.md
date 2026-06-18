<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestName.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestName.java

## Purpose

`TestName.java` is a small JUnit 5 extension that captures the currently executing test method name for Hadoop test base classes.

## Important APIs, Types, and Functions

The class implements `BeforeEachCallback`, stores a volatile `String name`, implements `beforeEach(ExtensionContext)`, and exposes `getMethodName()`.

## Control Flow

JUnit invokes `beforeEach` before each test method; the extension reads `extensionContext.getTestMethod().get().getName()` and stores it. Tests or base classes later call `getMethodName()`.

## State and Persistence Behavior

The only state is the volatile method-name field. It is per-extension-instance state and is not persisted.

## Dependencies and Integration Points

It depends on JUnit Jupiter extension APIs and is used by Hadoop test infrastructure such as `HadoopTestBase` for thread naming and diagnostics.

## Risks and Edge Cases

`getTestMethod().get()` assumes a method-backed context. The volatile field helps visibility but does not prevent stale reads if a single extension instance were shared unusually across concurrent tests.

## Test Signals

Coverage should confirm method-name capture for ordinary JUnit 5 tests and registration through `@RegisterExtension`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestName.java -->
