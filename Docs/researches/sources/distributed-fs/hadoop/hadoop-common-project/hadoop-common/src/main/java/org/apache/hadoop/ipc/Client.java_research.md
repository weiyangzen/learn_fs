# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Client.java

## Purpose

`Client` is Hadoop's core writable IPC client. It multiplexes RPC `Writable` requests over reusable socket connections, handles connection setup, SASL negotiation, pings, retries, asynchronous responses, alignment context propagation, and response demultiplexing by call ID.

## Important APIs, control flow, and state

Static thread-locals carry explicit call IDs, retry counts, external handlers, async response futures, and asynchronous mode. Each `Client` has a generated UUID-style `clientId`, a `ConcurrentMap<ConnectionId, Connection>`, `putLock` to prevent new connections after stop, `emptyCondition` for shutdown, socket factory, response value class, configuration, reference count, and async call counter/limit.

`call()` creates a `Call`, attaches any `AlignmentContext`, obtains or creates a `Connection`, checks async limits, serializes and queues the request, and either returns a synchronous response from `CompletableFuture.get()` or stores a handled async future in `ASYNC_RPC_RESPONSE`. Failures are wrapped with remote address context unless they are already `RemoteException` or `SaslException`.

`Connection` owns the socket, `IpcStreams`, active call table, retry policy, auth protocol, ping settings, receiver thread, and a separate request-sender thread connected by a fair `SynchronousQueue`. Setup resolves DNS changes, creates sockets with TCP options, optionally binds Kerberos clients to a local address, connects with retry policy, writes the Hadoop RPC header, negotiates SASL, wraps streams, writes the connection context, starts the receiver, and then sends serialized call buffers through the sender thread. The receiver reads length-prefixed response buffers, validates client IDs, removes matching calls, updates alignment state on success, completes futures, or closes the connection on fatal errors. Shutdown interrupts receiver/sender/connecting threads, closes streams and SASL state, removes the connection conditionally from the map, and completes outstanding calls exceptionally.

`ConnectionId` is the pool key over address, protocol, UGI ticket, timeout, retry policy, ping, idle time, and TCP options. Its hash uses hostname and port rather than resolved IP so `setAddress()` can update DNS changes without changing the map key hash.

## Dependencies and integration points

`Client` is used by `ProtobufRpcEngine`, `ProtobufRpcEngine2`, and `ClientCache`. It integrates with `Server` wire protocol constants, `RpcWritable`, `ProtoUtil`, `SaslRpcClient`, `UserGroupInformation`, `RetryPolicy`, tracing spans, `NetUtils`, `CallerContext` indirectly through server headers, and `AlignmentContext`.

## Risks and test signals

Concurrency is the main risk: active calls must be inserted before setup, request sending must avoid partial socket writes on caller interruption, and connection removal must be conditional so a newer replacement is not removed. Async call counting must decrement on completion and on send/setup failures; exceeding the limit throws `AsyncCallLimitExceededException`. Response handling assumes a success header has a matching call; unexpected or duplicate call IDs could cause null dereference. SASL fallback must reject SIMPLE fallback when security requires it. `IpcStreams.readResponse()` enforces positive and maximum response length and handles pre-rpcv9 errors. Existing broader IPC tests, `ClientCache` usage in RPC engines, async RPC tests, SASL tests, and alignment-context integration tests are the relevant signals.
