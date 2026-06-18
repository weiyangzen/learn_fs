# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestFrameDecoder.java

Purpose: Tests ONC/RPC TCP record-marking frame decoding and server-side integration with `RpcProgram` port monitoring.

Important APIs/types/functions: `RpcUtil.RpcFrameDecoder`, Netty `ByteBuf`, `XDR.isLastFragment`, `XDR.fragmentSize`, `SimpleTcpServer`, `SimpleTcpClient`, custom `TestRpcProgram`, `RpcCall`, `RpcAcceptedReply`, `RpcResponse`, and helpers `startRpcServer`, `createPortmapXDRheader`, `createGetportMount`.

Control flow: unit tests feed partial and complete record fragments directly to the decoder, checking that incomplete headers or bodies do not emit decoded frames and multiple fragments emit expected buffers. Integration tests start a random local RPC TCP server, send a large XDR request, and inspect static `resultSize` recorded by the program. The insecure-port test rejects non-null procedures when `allowInsecurePorts` is false but permits NULL procedure calls.

State and persistence: static `resultSize` is reset per client request. Server binding uses random ports with retry on `BindException`. Netty buffers are manually released in decoder unit tests.

Dependencies/integration points: Netty channel pipeline, Hadoop ONC/RPC framing, `RpcProgram` authorization/port monitoring, localhost TCP sockets, Mockito, and `GenericTestUtils` log-level control.

Risks: random port selection and live server threads can be flaky; static state makes parallel execution sensitive; direct buffer release must avoid leaks; the insecure-port assertion depends on client source port being unprivileged.

Test signals: confirms record fragments are buffered until complete, large requests preserve payload size, rejected calls do not reach handler data, and NULL procedure bypasses port monitoring.
