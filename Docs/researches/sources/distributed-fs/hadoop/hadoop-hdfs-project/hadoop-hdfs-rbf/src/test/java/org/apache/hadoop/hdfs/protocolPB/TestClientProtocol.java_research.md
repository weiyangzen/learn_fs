# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocol.java

This small interface defines the test protocol used by the async protobuf RPC utility tests. Its methods are `ping()`, `echo(String)`, `error()`, and `add(int, int)`, each declared to throw `IOException`.

There is no implementation, state, or persistence in this file. `TestClientProtocolTranslatorPB` implements the interface on the client side by wrapping protobuf RPC calls in `AsyncRpcProtocolPBUtil.asyncIpcClient`; `TestClientProtocolServerSideTranslatorPB` supplies delayed server behavior through Hadoop's protobuf test service implementation.

Dependencies are only Java `IOException` and the surrounding test classes. Integration is as a simple typed facade over protobuf RPC test calls. Risks are low; any method-signature change must be reflected in the translator and tests. Test signal comes from `TestAsyncRpcProtocolPBUtil`, which exercises all four methods.
