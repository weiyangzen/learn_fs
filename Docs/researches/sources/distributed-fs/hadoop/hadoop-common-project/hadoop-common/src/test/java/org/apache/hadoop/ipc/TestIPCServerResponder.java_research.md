# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIPCServerResponder.java

Purpose: stresses IPC server response writing, especially partial socket writes and deferred response handling. It proves the responder can serve many clients with small send buffers and that handlers are released when responses are postponed.

Important APIs/types/functions: local `TestServer extends Server`, `Caller extends SubjectInheritingThread`, static `call(Client, Writable, InetSocketAddress)`, `Server.Call.postponeResponse()`, `Call.sendResponse()`, `BytesWritable`, `IntWritable`, `Client.ConnectionId`, and `Server.getCurCall()`.

Control flow: responder stress tests construct a server returning variable-size `BytesWritable` payloads while socket send buffer size is forced below the maximum payload, then spawn caller threads that repeatedly send random byte arrays. `testDeferResponse()` uses a one-handler server whose call method postpones a response zero, one, or two times based on an integer request; futures verify the client remains blocked until enough `sendResponse()` calls occur, while intervening immediate calls prove the handler is free.

State and persistence behavior: uses static byte arrays and mutable static `Configuration`; `testResponseBuffer()` mutates `Server.INITIAL_RESP_BUF_SIZE` and `IPC_SERVER_RPC_MAX_RESPONSE_SIZE_KEY` to force tiny response buffers, then resets configuration. Deferred-response state lives in `Server.Call` objects retained by test references until explicitly released.

Dependencies and integration points: integrates with the low-level writable IPC client/server path, response buffer sizing configuration, responder thread behavior, executor futures, latches, and Hadoop socket utilities. It is an integration point between handler execution and responder-side asynchronous write completion.

Risks and test signals: partial-write behavior is timing/socket-buffer sensitive. The strongest signal is that response ordering and sequence numbers remain correct while deferred calls are pending, and that one handler can continue processing new calls after `postponeResponse()`. Missing cleanup of executor/client/server resources would make failures noisy.
