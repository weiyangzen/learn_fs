# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocolTranslatorPB.java

This client-side test translator implements `TestClientProtocol` over `TestRpcBase.TestRpcService`. It is a compact facade for exercising `AsyncRpcProtocolPBUtil.asyncIpcClient`.

`ping()`, `echo(String)`, `error()`, and `add(int,int)` build the corresponding protobuf request messages, call the underlying RPC proxy, and provide response mappers to convert protobuf responses into `Void`, `String`, or `Integer`. `close()` stops the RPC proxy through `RPC.stopProxy`.

State is the final `TestRpcService rpcProxy`. Dependencies include Hadoop IPC RPC, protobuf test message classes, Java `Closeable`, and `AsyncRpcProtocolPBUtil`.

Integration points are the async IPC utility and the delayed server translator. In asynchronous mode, return values are retrieved later through `AsyncUtil.syncReturn`; in synchronous mode the same wrapper still returns mapped values. Risks are mostly test-harness risks: mapper type mismatches would surface at sync-return time, and the translator assumes the proxy implements the protobuf service contract. Test signal comes from `TestAsyncRpcProtocolPBUtil`, which exercises every method and proxy cleanup.
