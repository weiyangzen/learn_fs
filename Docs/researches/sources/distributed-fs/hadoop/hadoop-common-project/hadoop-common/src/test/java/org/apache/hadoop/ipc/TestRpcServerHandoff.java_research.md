# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcServerHandoff.java

## Purpose

`TestRpcServerHandoff` verifies Hadoop IPC server support for deferring a handler response and completing it later, either with a normal response payload or with a remote exception. This protects the handoff path used when a handler must release itself while another thread eventually finishes the RPC.

## Important APIs, Types, And Functions

`ServerForHandoffTest` subclasses `Server` with `BytesWritable` parameters and overrides `call()` to capture the current `Server.Call`, call `deferResponse()`, signal invocation, and return `null`. Its `sendResponse()` calls `setDeferredResponse(request)` and `sendError()` calls `setDeferredError(new IOException("DeferredError"))`. `ClientCallable` uses low-level `Client.call()` with `RPC.RpcKind.RPC_BUILTIN`.

## Control Flow

Each test starts the custom server, launches a client call in a `FutureTask` on a `SubjectInheritingThread`, waits until the server handler has captured and deferred the call, then repeatedly confirms the future does not complete for roughly three seconds. `testDeferredResponse()` then injects the original request as the deferred response and asserts the client receives the same bytes. `testDeferredException()` injects a deferred error and asserts the client future fails with a `RemoteException` containing `DeferredError`.

## State And Persistence Behavior

The server stores the current request and deferred `Call` in volatile fields, uses an `AtomicBoolean`, `ReentrantLock`, and `Condition` to coordinate handler invocation, and has no persisted state. The important state transition is handler-owned call to externally completed deferred call.

## Dependencies And Integration Points

The test directly exercises `Server.Call.deferResponse()`, `setDeferredResponse()`, `setDeferredError()`, low-level `Client.ConnectionId`, `BytesWritable`, and `NetUtils` address resolution. It complements the protobuf-level postponed response tests in `TestRpcBase` and `TestSaslRPC`.

## Risks And Test Signals

The main risks are handler leaks, premature client completion, missing wakeups, and error serialization mismatches. Test signals are timeout-guarded futures that must block before handoff, equality of `BytesWritable` response payloads, and `RemoteException` propagation for deferred failures.
