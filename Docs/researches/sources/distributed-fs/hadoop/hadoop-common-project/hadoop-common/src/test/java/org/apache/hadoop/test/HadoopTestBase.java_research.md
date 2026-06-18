# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/HadoopTestBase.java

Purpose: assertion-enabled Hadoop JUnit 5 base class that applies a default timeout and test-thread naming.

Important APIs/types/functions: extends `Assertions`; class-level `@Timeout`; constants `PROPERTY_TEST_DEFAULT_TIMEOUT` and `TEST_DEFAULT_TIMEOUT_VALUE`; instance `retrieveTestTimeout`; `@RegisterExtension TestName`; `getMethodName`; lifecycle hooks `nameTestThread` and `nameThreadToMethod`.

Control flow: timeout uses 100000 ms by default. `retrieveTestTimeout` reads system property `test.default.timeout` and falls back on parse errors. JUnit lifecycle methods rename the current thread to `JUnit` and then `JUnit-<method>`.

State and persistence behavior: only in-memory timeout field and thread name; reads JVM system property. No durable state.

Dependencies and integration points: common base for Hadoop tests wanting inherited JUnit assertions, unlike `AbstractHadoopTestBase`.

Risks and test signals: helps diagnose hung tests and gives consistent timeouts. The `defaultTimeout` field is stored but not otherwise used beyond construction-era retrieval, so class-level annotation is the real enforcement.
