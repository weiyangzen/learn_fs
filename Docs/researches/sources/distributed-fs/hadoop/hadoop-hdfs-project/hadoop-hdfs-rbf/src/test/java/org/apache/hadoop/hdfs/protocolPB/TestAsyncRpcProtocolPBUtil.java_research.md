# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestAsyncRpcProtocolPBUtil.java

This test verifies the asynchronous protobuf RPC utility used by Router protocol translators. It creates a one-handler protobuf RPC server backed by a delayed test implementation, enables client asynchronous mode, and verifies that calls return before server processing completes while `AsyncUtil.syncReturn` later yields the result or exception.

Important methods are `setUp()`, `clear()`, `testAsyncIpcClient()`, and `checkResult()`. Setup configures `AsyncRpcProtocolPBUtil` with `ForkJoinPool.commonPool()`, installs `ProtobufRpcEngine2` for `TestRpcBase.TestRpcService`, starts an RPC server with `TestClientProtocolServerSideTranslatorPB`, creates a proxy, wraps it in `TestClientProtocolTranslatorPB`, and turns on `Client.setAsynchronousMode(true)`. The test calls `add`, `echo`, and `error`; successful calls assert that client call cost is below the server delay and that synced results match; error calls expect a `RemoteException` containing the server-side standby message.

State is per-test RPC server/client state plus global Hadoop IPC asynchronous mode and async responder executor. Dependencies include Hadoop IPC, protobuf test services, `AsyncUtil`, `LambdaTestUtils`, and `Time`.

Risks include global async mode not being restored in this test, common-pool scheduling variability, and timing assertions being sensitive on slow CI machines. The test signal is direct coverage for async RPC result and exception propagation.
