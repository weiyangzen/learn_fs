<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestCustomizedCallbackHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestCustomizedCallbackHandler.java

Purpose: Verifies SASL server callback handling can delegate unsupported callbacks to configured custom handlers or handler methods.

Important APIs/types/functions: `CustomizedCallbackHandler`, `CustomizedCallbackHandler.Cache`, `SaslDataTransferServer.SaslServerCallbackHandler`, `SaslRpcServer.SaslDigestCallbackHandler`, `HADOOP_SECURITY_SASL_CUSTOMIZEDCALLBACKHANDLER_CLASS_KEY`, and `LambdaTestUtils.intercept`.

Control flow: Static helpers reset callback state and assert exact callback object identity. `testCustomizedCallbackHandler` first verifies no handler causes `UnsupportedCallbackException`, then configures a class implementing `CustomizedCallbackHandler` and confirms callbacks are delegated for both data-transfer and RPC digest handlers. `testCustomizedCallbackMethod` configures plain objects with a reflective `handleCallbacks` method and verifies success and wrapped failure behavior.

State and persistence behavior: Uses static `AtomicReference<List<Callback>>` and clears the callback-handler cache between scenarios. No filesystem state.

Dependencies and integration points: Guards Hadoop security extensibility used by SASL data transfer and RPC callback stacks.

Risks: Relies on reflection/cache behavior and exact object identity. Exceptions from custom methods are observed as `IOException` in the data-transfer wrapper.

Test signals: Passing means custom callback classes and callback-method objects are discovered, cached, invoked, and failure-propagated as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestCustomizedCallbackHandler.java -->
