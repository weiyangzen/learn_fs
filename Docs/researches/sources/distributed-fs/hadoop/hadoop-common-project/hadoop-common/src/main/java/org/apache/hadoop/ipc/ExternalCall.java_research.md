# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ExternalCall.java

## Purpose

`ExternalCall<T>` adapts a `PrivilegedExceptionAction<T>` into a `Server.Call` so work initiated outside the normal RPC request path can run through IPC handler and response machinery.

## Important APIs, control flow, and state

The class stores an action, an `AtomicBoolean done`, result, and error. Subclasses provide `getRemoteUser()`. `run()` executes the action, stores the result, and calls `sendResponse()`, or calls `abortResponse(t)` on failure. Completion is signaled through overridden `doResponse(Throwable, RpcStatusProto)`, which records any error, sets `done`, and notifies waiters. `get()` waits until completion and returns the result or throws `ExecutionException`.

## Dependencies and integration points

It extends `Server.Call`, uses `RpcStatusProto`, and depends on `UserGroupInformation`. It is intended for postponed or externally triggered server-side calls that still need handler accounting and response notification.

## Risks and test signals

`waitForCompletion()` catches `InterruptedException` from `wait()` and only rethrows if `Thread.interrupted()` is true after the catch, which clears interrupt status and can make interruption handling subtle. `notify()` wakes one waiter, which matches expected single `get()` use but is not a broadcast. Since `run()` catches `Throwable`, severe errors are routed to `abortResponse()`. Tests should cover success, action failure, postponed response completion, interruption, and remote user propagation.
