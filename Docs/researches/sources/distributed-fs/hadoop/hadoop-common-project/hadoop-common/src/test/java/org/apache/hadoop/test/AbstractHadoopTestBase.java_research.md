# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/AbstractHadoopTestBase.java

Purpose: JUnit 5 base class that applies a default timeout and names test threads without extending assertion classes.

Important APIs/types/functions: `@Timeout`, `PROPERTY_TEST_DEFAULT_TIMEOUT`, `TEST_DEFAULT_TIMEOUT_VALUE`, static `retrieveTestTimeout`, `@RegisterExtension TestName`, `getMethodName`, `nameTestThread`, and `nameThreadToMethod`.

Control flow: class-level timeout uses the default value constant. `retrieveTestTimeout` parses system property `test.default.timeout`, falling back to 100000 ms on absence or parse failure. Before all tests, the thread is named `JUnit`; before each method, it becomes `JUnit-<method>`.

State and persistence behavior: uses system properties for timeout configuration and in-memory thread names. No persistence.

Dependencies and integration points: integrates with Hadoop's `TestName` extension and JUnit 5 lifecycle. Intended for tests that prefer AssertJ or custom assertion bases.

Risks and test signals: naming improves diagnostics in thread dumps and logs. Risk is duplicated timeout constants with `HadoopTestBase`; parse fallback is explicit.
