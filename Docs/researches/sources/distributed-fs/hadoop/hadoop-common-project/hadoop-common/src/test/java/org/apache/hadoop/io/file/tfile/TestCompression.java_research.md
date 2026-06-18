
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestCompression.java

Purpose: Regression tests for configurable LZO codec loading in TFile compression support, including valid alternate codec and invalid class behavior.

Important APIs and types: Uses `Compression.Algorithm.LZO.conf`, `Compression.Algorithm.CONF_LZO_CLASS`, `Compression.Algorithm.LZO.getCodec()`, `LambdaTestUtils.intercept()`, and JUnit lifecycle hooks.

Control flow: `@BeforeAll` enables test reload behavior for the LZO codec and `@AfterAll` disables it. One test sets the configured LZO class to Hadoop `DefaultCodec` and asserts the loaded codec class name. The other sets an invalid class, expects an `IOException` containing the class name, and rethrows if the cause is not `ClassNotFoundException`.

State and persistence: Mutates static compression configuration shared by the JVM, then resets reload flag after all tests.

Dependencies and integration points: Guards HADOOP-11418 behavior in the TFile compression layer.

Risks: Static configuration mutation can leak if lifecycle cleanup fails. The test uses DefaultCodec as a dummy LZO substitute.

Test signals: Covers custom codec class resolution and misconfiguration diagnostics.
