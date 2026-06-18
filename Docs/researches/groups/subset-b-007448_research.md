<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncRpcClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncRpcClient.java

## Purpose
`RouterAsyncRpcClient` is the asynchronous `RouterRpcClient` implementation used by the HDFS Router-Based Federation router to proxy client protocol calls to NameNodes without tying router handler threads to blocking downstream RPCs. It keeps the base router routing semantics, including active/standby/observer selection and fairness permits, but composes operations through the router async utilities and Hadoop IPC asynchronous mode.

## Important APIs, Types, And Functions
The class overrides `invokeAll`, `invokeMethod`, `invokeSequential`, `invokeConcurrent`, `getRemoteResults`, and both `invokeSingle` forms. `invokeMethod` schedules the real work on the namespace async executor, transfers `ThreadLocalContext`, acquires a `RouterRpcFairnessPolicyController` permit, and releases it in `asyncFinally`. `invokeMethodAsync` iterates ordered `FederationNamenodeContext` entries and drives failover. `invoke` flips `Client.setAsynchronousMode(true)`, invokes the reflected protocol method, and attaches an async catch for downstream failures. It depends heavily on `AsyncUtil` functions such as `asyncTry`, `asyncForEach`, `asyncApply`, `asyncCatch`, `asyncFinally`, `asyncCompleteWith`, and `asyncReturn`.

## Control Flow
Simple multi-location calls start a base-style concurrent or sequential invocation, then transform the current future into the desired return shape. `invokeMethod` validates NameNode availability, creates an initial completed future, then submits an `AsyncApplyFunction` to `router.getRpcServer().getAsyncExecutorForNamespace(nsid)`. Inside the executor, `invokeMethodAsync` adds caller context, emits monitor signals, skips observers unless observer reads are requested, opens a `ConnectionContext`, invokes the proxy method, post-processes success, breaks the loop, and releases the connection in `asyncFinally`. On `IOException`, it records the per-NameNode error and asks inherited logic whether to retry, fail over, or continue. If all NameNodes fail, it delegates to inherited `handlerAllNamenodeFail`. Concurrent calls collect futures from the base callables and complete with `CompletableFuture.allOf(...).handle(...)`, then process all per-location results.

## State, Persistence, And Dependencies
This class does not persist records itself. Its state is transient: references to `Router`, `ActiveNamenodeResolver`, `RouterRpcMonitor`, per-call `ExecutionStatus`, per-call exception maps, current connections, and futures in `Async.CUR_COMPLETABLE_FUTURE`. It depends on resolver-provided NameNode metadata, router RPC server namespace executors, Hadoop IPC async client behavior, fairness controllers, and the inherited connection pool.

## Integration Points
The async protocol modules call this client through the same `RouterRpcClient` API used by synchronous router modules. It integrates with `RouterRpcServer` for remote user lookup, namespace executor selection, location resolution, and operation checks; with `ActiveNamenodeResolver` for HA state; with `RouterRpcMonitor` for proxy operation accounting; and with inherited `RouterRpcClient` logic for exception localization, observer eligibility, result post-processing, and NameNode ordering.

## Risks
The implementation relies on a thread-local current future, so missed `asyncComplete`/`asyncCompleteWith` updates or thread hops without context transfer can silently corrupt async chains. `Client.setAsynchronousMode` is toggled around reflection and must remain balanced on exceptions. A shared single-element `ConnectionContext[]` is used inside iteration to allow finally cleanup, which is safe only because the foreach chain is sequential. Executor saturation is converted to a `StandbyException`, so operational diagnosis depends on the message. Generic casts around `RemoteResult`, `List`, and `Map` are unchecked and rely on callers passing the correct class token.

## Test Signals
Useful tests cover observer-read routing, standby failover, connection release on success and failure, namespace executor rejection, fairness permit release after downstream exceptions, `invokeSequential` first-success semantics, and concurrent result aggregation where some locations fail. Integration tests should assert that async callers observe real results through the router async response path despite Java methods returning placeholder values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncRpcClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncSnapshot.java

## Purpose
`RouterAsyncSnapshot` implements the snapshot-related `ClientProtocol` surface for the async router. It mirrors `RouterSnapshot` behavior while composing remote calls through the async RPC client and translating paths between global mount paths and destination NameNode paths.

## Important APIs, Types, And Functions
The module overrides `createSnapshot`, `getSnapshottableDirListing`, `getSnapshotListing`, `getSnapshotDiffReport`, and `getSnapshotDiffReportListing`. It uses `RemoteMethod`, `RemoteParam`, `RemoteLocation`, `RemoteResult`, `SnapshotStatus`, `SnapshottableDirectoryStatus`, `SnapshotDiffReport`, and `SnapshotDiffReportListing`. `DFSUtil.bytes2String` and `DFSUtil.string2Bytes` are used when rewriting snapshot listing parent paths.

## Control Flow
Each public method first calls `rpcServer.checkOperation` with the correct NameNode operation category. Path-scoped methods resolve remote locations with `getLocationsForPath`. If the path is configured for concurrent invocation, the method calls `rpcClient.invokeConcurrent` and transforms the returned map; otherwise it calls `invokeSequential` and transforms the chosen `RemoteResult`. Snapshot creation rewrites the returned destination path back to the source mount path. Listing calls merge namespace arrays or select the first routed result depending on operation semantics.

## State, Persistence, And Dependencies
The class keeps references to `RouterRpcServer`, `RouterRpcClient`, and `ActiveNamenodeResolver`. Snapshot state itself is persisted by destination NameNodes, not by this module. The module depends on router mount-table resolution and on NameNode snapshot APIs.

## Integration Points
It is plugged into the async `RouterRpcServer` client protocol implementation. It uses the resolver for all namespaces in `getSnapshottableDirListing`, router merge utilities for array responses, and `RemoteParam` to inject per-location destination paths into reflected NameNode calls.

## Risks
Concurrent path rewrites assume a representative first result and location, which is correct only when the resolved operation maps to equivalent destinations. `replaceFirst` treats the first argument as a regex, so unusual path characters could matter. `getSnapshotListing` has different replacement directions in concurrent and sequential branches, making regression tests important.

## Test Signals
Snapshot tests should cover mount-path rewriting for create and list, concurrent versus sequential invocation, empty or multi-namespace snapshottable listings, diff report listing pagination, and failure behavior when one namespace lacks snapshot support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncStoragePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncStoragePolicy.java

## Purpose
`RouterAsyncStoragePolicy` provides async router implementations for storage policy reads from HDFS client protocol.

## Important APIs, Types, And Functions
It overrides `getStoragePolicy(String)` and `getStoragePolicies()`. It uses `BlockStoragePolicy`, `RemoteMethod`, `RemoteParam`, `RemoteLocation`, `RouterRpcServer`, and `RouterRpcClient`.

## Control Flow
`getStoragePolicy` checks a READ operation with path resolution enabled, resolves the target path to remote locations, builds a `getStoragePolicy` remote method with a per-location path parameter, invokes sequentially, and returns the async placeholder for `BlockStoragePolicy`. `getStoragePolicies` checks READ, builds a no-argument remote method, invokes any available namespace asynchronously through the RPC server helper, and returns the async placeholder array.

## State, Persistence, And Dependencies
No local persistence exists. Storage policy data lives in NameNodes. The class holds only RPC server/client references and depends on router path resolution and available-namespace selection.

## Integration Points
The module is selected by the async router protocol path in place of `RouterStoragePolicy`. It delegates all downstream communication to `RouterRpcClient` or `RouterRpcServer.invokeAtAvailableNsAsync`.

## Risks
Callers must retrieve the actual result through the async response machinery because public methods return `asyncReturn` placeholders. Multi-destination paths use sequential semantics, so first valid location selection and error localization should match the synchronous parent.

## Test Signals
Tests should verify single-path storage policy lookup across mounted paths, no-namespace behavior for `getStoragePolicies`, permission/category checks, and parity with synchronous router responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncStoragePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncUserProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncUserProtocol.java

## Purpose
`RouterAsyncUserProtocol` implements async refresh and user-group mapping protocol calls for the router.

## Important APIs, Types, And Functions
It overrides `refreshUserToGroupsMappings`, `refreshSuperUserGroupsConfiguration`, and `getGroupsForUser`. It uses `RefreshUserMappingsProtocol`, `GetUserMappingsProtocol`, `Groups`, `ProxyUsers`, `UserGroupInformation`, `FederationNamespaceInfo`, and `RouterRpcServer.merge`.

## Control Flow
Each method checks an UNCHECKED operation category. Refresh calls query all resolver namespaces; when none exist, they refresh the router-local JVM state and complete the current future with null, otherwise they invoke the corresponding refresh method concurrently on all namespaces. `getGroupsForUser` resolves locally when there are no namespaces; otherwise it invokes all namespaces concurrently and merges `String[]` responses.

## State, Persistence, And Dependencies
The class does not persist state. It updates local Hadoop security caches only when the router has no downstream namespaces. With namespaces present, downstream NameNodes own the refresh and group mapping results.

## Integration Points
This module integrates with the async router protocol server, namespace resolver, `RefreshUserMappingsProtocol`, and `GetUserMappingsProtocol`. It depends on `RouterRpcClient.invokeConcurrent` to fan out refreshes and reads.

## Risks
Concurrent refresh success semantics depend on `invokeConcurrent`; partial namespace failures may surface differently depending on require-response overloads. Merging group arrays may duplicate values unless the router merge utility de-duplicates. Local fallback behavior differs from federated behavior and needs explicit coverage.

## Test Signals
Tests should cover local no-namespace refresh, federated concurrent refresh, group merge from multiple namespaces, downstream exceptions, and async placeholder return behavior for `String[]` and void methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncUserProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/package-info.java

## Purpose
This package descriptor marks the router async package as private and evolving and documents its role as the non-blocking operation layer for HDFS Federation router RPCs.

## Important APIs, Types, And Functions
The file declares package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` for `org.apache.hadoop.hdfs.server.federation.router.async`.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no state or persistence. The only dependencies are Hadoop classification annotations.

## Integration Points
The annotations communicate compatibility expectations to downstream Hadoop developers and generated docs.

## Risks
The package is explicitly not a stable public API, so external users should not depend on these implementation classes.

## Test Signals
No direct tests are required beyond compilation and annotation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/ApplyFunction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/ApplyFunction.java

## Purpose
`ApplyFunction` adapts a synchronous, IOException-throwing transformation into a `CompletableFuture` continuation used by the router async DSL.

## Important APIs, Types, And Functions
The functional method is `R apply(T t) throws IOException`. Default overloads apply the function to a `CompletableFuture<T>` via `thenApply` or `thenApplyAsync` with an `Executor`, wrapping `IOException` with `Async.warpCompletionException`.

## Control Flow
When the input future completes normally, the supplied transformation runs and returns a new result. If it throws `IOException`, the future completes exceptionally with a `CompletionException`.

## State, Persistence, And Dependencies
The interface has no state. It depends on `CompletableFuture`, optional executors, and the shared exception wrapping helper.

## Integration Points
`AsyncUtil.asyncApply` and `asyncApplyUseExecutor` are the main callers. Async router modules use this interface for post-processing RPC results.

## Risks
Only `IOException` is explicitly caught; unchecked exceptions propagate through `CompletableFuture` naturally. Continuations without an executor run on the completing thread, so expensive transformations can delay IPC completion.

## Test Signals
Tests should cover normal mapping, checked exception wrapping, executor dispatch, and compatibility with `AsyncUtil.asyncReturn` chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/ApplyFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/Async.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/Async.java

## Purpose
`Async` is the base interface for the router async utility DSL. It centralizes the thread-local current `CompletableFuture` and common completion-exception wrapping helpers.

## Important APIs, Types, And Functions
`CUR_COMPLETABLE_FUTURE` is a `ThreadLocal<CompletableFuture<Object>>`. Default methods include `setCurCompletableFuture`, `getCurCompletableFuture`, and blocking `result()`. Static helpers `unWarpCompletionException` and `warpCompletionException` normalize `CompletionException` wrapping.

## Control Flow
Implementations set the current future after starting async work. `result()` blocks on the thread-local future and unwraps `IOException` from `ExecutionException`, returning null on interruption.

## State, Persistence, And Dependencies
The sole state is thread-local, process-local future state. There is no external persistence. The interface depends on Java concurrency primitives and `IOException`.

## Integration Points
Every utility functional interface extends `Async`, and `AsyncUtil` manipulates the same thread-local. Router async RPC code relies on this implicit state to make Java method returns compatible with Hadoop IPC async responses.

## Risks
The misspelled `warp/unWarp` names are API details. Thread-local state can leak or be stale when reused threads do not overwrite it. `result()` returns null on interruption without restoring interrupt status. Assertions guard null futures, so production runs without assertions can fail later with null dereferences.

## Test Signals
Tests should verify future set/get isolation across threads, exception unwrapping, `IOException` propagation from `result()`, and cleanup/overwrite behavior on executor thread reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/Async.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncApplyFunction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncApplyFunction.java

## Purpose
`AsyncApplyFunction` adapts an asynchronous transformation into a composable `CompletableFuture` continuation.

## Important APIs, Types, And Functions
The functional method is `void applyAsync(T t) throws IOException`; implementations must set the current future. `apply(T)` starts async work and blocks via `result()`. `async(T)` starts work and returns the current future. Future overloads use `thenCompose` or `thenComposeAsync`.

## Control Flow
When chained to a completed input future, `async(t)` is called and the returned current future is flattened into the parent chain. Checked setup errors are wrapped as completion exceptions.

## State, Persistence, And Dependencies
No direct state exists; the contract relies on `Async.CUR_COMPLETABLE_FUTURE`. There is no persistence.

## Integration Points
`RouterAsyncRpcClient.invokeMethod` uses this form when a continuation itself initiates an async RPC. `AsyncUtil.asyncApplyUseExecutor` can dispatch it onto namespace executors.

## Risks
Implementations that forget to set the current future will trip assertions or produce null chains. The synchronous `apply` method can block if used in the wrong context. Thread-local current future must be set on the same thread that calls `async`.

## Test Signals
Tests should cover flattening behavior, executor use, missing-current-future failures, checked exceptions during initiation, and non-blocking composition with nested RPC calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncApplyFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncBiFunction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncBiFunction.java

## Purpose
`AsyncBiFunction` is the two-argument asynchronous function abstraction used by async foreach workflows.

## Important APIs, Types, And Functions
The functional method is `void applyAsync(T t, P p) throws IOException`. The default `async(T, P)` invokes it and returns the current thread-local future.

## Control Flow
Callers pass contextual state and one input element. Implementations start async work and set `CUR_COMPLETABLE_FUTURE`; the default method returns that future for chaining.

## State, Persistence, And Dependencies
No direct state or persistence exists. The interface depends on the `Async` thread-local future contract.

## Integration Points
`AsyncForEachRun` uses this interface to process each iterator element with access to the loop controller, enabling `breakNow()` from inside async callbacks.

## Risks
The same missing-current-future risk applies. Because it passes mutable loop state, implementations must avoid retaining and using the controller after the loop has progressed unexpectedly.

## Test Signals
Tests should cover normal two-argument composition, IOException propagation, and interaction with `AsyncForEachRun.breakNow`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncBiFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncCatchFunction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncCatchFunction.java

## Purpose
`AsyncCatchFunction` is the asynchronous exception-handler counterpart to `CatchFunction`, allowing recovery logic to initiate new async work.

## Important APIs, Types, And Functions
It defines `void applyAsync(R r, E e) throws IOException`, synchronous `apply`, `async(R, E)`, and an override of `apply(CompletableFuture<R>, Class<E>)` that uses `handle` and `thenCompose` to flatten a recovery future.

## Control Flow
If the input future completes normally, the implementation returns the original future. If the unwrapped exception matches the requested class, it calls async recovery and composes its future. Nonmatching exceptions are rewrapped and propagated.

## State, Persistence, And Dependencies
The interface holds no state and relies on the thread-local future set by recovery implementations. It depends on completion-exception unwrapping/wrapping.

## Integration Points
`AsyncUtil.asyncCatch` accepts both sync and async catch functions. `RouterAsyncRpcClient.invoke` uses an async catch around reflected IPC calls so exception handling can continue through inherited async failover logic.

## Risks
Returning the original input future on normal completion means the generic handle stage temporarily has nested futures; the final `thenCompose` is critical. Recovery code must set the current future. Catch matching uses the unwrapped exception, but nonmatching propagation wraps the original wrapper, which can deepen nesting.

## Test Signals
Tests should cover matching and nonmatching exception types, async recovery success, async recovery failure, normal completion pass-through, and nested `CompletionException` unwrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncCatchFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncForEachRun.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncForEachRun.java

## Purpose
`AsyncForEachRun` implements sequential asynchronous iteration over an `Iterator`, with optional early break.

## Important APIs, Types, And Functions
Key methods are `run()`, private `doOnce(I)`, `breakNow()`, `forEach(Iterator<I>)`, and `asyncDo(AsyncBiFunction<AsyncForEachRun<I,R>, I, R>)`. It implements `AsyncRun<R>`.

## Control Flow
`run` completes immediately with null for an empty iterator. Otherwise it invokes `doOnce` on the first element and stores the returned future. `doOnce` calls the async function and then composes the next iteration after the current future completes, stopping when `breakNow` was called or the iterator is exhausted.

## State, Persistence, And Dependencies
The class stores the iterator, callback, and a boolean break flag. There is no persistence. It depends on `CompletableFuture` and the async utility interfaces.

## Integration Points
`AsyncUtil.asyncForEach` constructs this class. `RouterAsyncRpcClient` uses it for ordered NameNode failover and ordered remote-location invocation.

## Risks
Iteration is sequential, not parallel; naming can be misleading. The break flag is mutable and not synchronized, relying on callback ordering. Exceptions thrown while starting the first or later iteration are wrapped as completion exceptions.

## Test Signals
Tests should verify empty iterators, ordered execution, early break after a successful callback, exception propagation from first and later elements, and that later elements are not invoked after break.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncForEachRun.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncRun.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncRun.java

## Purpose
`AsyncRun` is the zero-input async task abstraction used by `AsyncUtil.asyncTry` and custom async runners.

## Important APIs, Types, And Functions
It defines `void run() throws IOException` and default `CompletableFuture<R> async()`, which runs the task and returns the current thread-local future.

## Control Flow
Implementations run setup logic and must set `CUR_COMPLETABLE_FUTURE`. The default `async` method returns that future to callers for composition.

## State, Persistence, And Dependencies
No local state exists. It depends on the `Async` thread-local future contract.

## Integration Points
`AsyncUtil.asyncTry` calls `async()` and records the resulting future. `AsyncForEachRun` implements this interface to make foreach loops composable.

## Risks
The interface does not enforce future completion; incorrect implementations fail at runtime. The `run` name may be confused with synchronous `Runnable` behavior despite the future contract.

## Test Signals
Tests should cover successful future setup, IOException during run, missing future assertions, and chaining through `asyncTry`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncRun.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncUtil.java

## Purpose
`AsyncUtil` is the static helper facade for building router async workflows around the current thread-local `CompletableFuture`.

## Important APIs, Types, And Functions
Important methods include `asyncReturn`, `syncReturn`, `asyncComplete`, `asyncCompleteWith`, `asyncThrowException`, `asyncApply`, `asyncApplyUseExecutor`, `asyncTry`, `asyncCatch`, `asyncFinally`, `asyncForEach`, `asyncCurrent`, and `getCompletableFuture`. `asyncReturn` supplies placeholder Java return values: false for booleans, -1 for integer/long, and null otherwise.

## Control Flow
Async router methods call one method to seed or update `CUR_COMPLETABLE_FUTURE`, then chain transformations and catches. `asyncCurrent` starts an async operation for every collection element, waits for all futures with `CompletableFuture.allOf`, and invokes a supplied aggregator over the future array.

## State, Persistence, And Dependencies
All state is the shared `Async.CUR_COMPLETABLE_FUTURE` thread-local. There is no persistence. Dependencies are Java futures, executors, the utility functional interfaces, and completion-exception wrapping.

## Integration Points
Every async router protocol method uses this class to bridge normal Java method signatures to asynchronous Hadoop IPC handling. `RouterAsyncRpcClient` also exposes the current future to aggregate downstream RPCs.

## Risks
The global thread-local design is fragile around executor boundaries. `asyncReturn` placeholders are intentionally not real results and must only be used where the IPC layer reads the future. `syncReturn` casts and rethrows `ExecutionException` causes as `Exception`, which can fail if the cause is an `Error`. `asyncCurrent` calls the aggregator even when `allOf` sees an exception, so aggregator code must inspect futures carefully.

## Test Signals
Tests should cover every helper in normal and exceptional cases, placeholder return values for primitive-compatible signatures, executor-based apply, foreach behavior, `asyncCurrent` partial failures, and thread-local isolation under reused router executors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/CatchFunction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/CatchFunction.java

## Purpose
`CatchFunction` adapts synchronous exception recovery to `CompletableFuture` chains.

## Important APIs, Types, And Functions
It defines `R apply(R r, E e) throws IOException` and default `CompletableFuture<R> apply(CompletableFuture<R>, Class<E>)`.

## Control Flow
The default method calls `CompletableFuture.handle`. Normal completion returns the result. Exceptional completion is unwrapped and matched against the requested class. Matching exceptions invoke recovery; nonmatching exceptions are rewrapped and propagated.

## State, Persistence, And Dependencies
The interface has no state or persistence. It depends on `Async` exception helpers and Java futures.

## Integration Points
`AsyncUtil.asyncCatch` uses this interface for synchronous recovery logic. It is the parent of `AsyncCatchFunction`.

## Risks
Recovery only catches exceptions assignable to the specified class. A recovery `IOException` replaces the original failure. Non-IOException unchecked recovery failures propagate through future handling.

## Test Signals
Tests should cover normal pass-through, matching recovery, nonmatching propagation, checked recovery failure, and nested completion-exception unwrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/CatchFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/FinallyFunction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/FinallyFunction.java

## Purpose
`FinallyFunction` provides cleanup/finalization behavior for async chains while preserving prior failures.

## Important APIs, Types, And Functions
It defines `R apply(R r) throws IOException` and a default `apply(CompletableFuture<R>)` that uses `handle`.

## Control Flow
The cleanup function runs for both normal and exceptional completion. If the original future had an exception, the default method rethrows that exception after cleanup. If cleanup itself throws `IOException`, that cleanup error becomes the completion exception.

## State, Persistence, And Dependencies
No state or persistence exists. The interface depends on `CompletableFuture` and `Async.warpCompletionException`.

## Integration Points
`AsyncUtil.asyncFinally` wraps this interface. `RouterAsyncRpcClient` uses it to release fairness permits and connection contexts.

## Risks
Cleanup exceptions can mask an original successful result and, depending on ordering, can also mask original failures. Cleanup receives null when the prior stage failed, so implementations must tolerate null inputs.

## Test Signals
Tests should verify cleanup on success, cleanup on failure, original exception preservation, cleanup exception behavior, and resource-release usage in RPC failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/FinallyFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/package-info.java

## Purpose
This package descriptor documents the async utility package and marks it private/evolving.

## Important APIs, Types, And Functions
It applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.router.async.utils`.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no state or persistence. Dependencies are Hadoop classification annotations.

## Integration Points
The descriptor applies compatibility metadata to the DSL classes used by async router modules.

## Risks
The package is not a public stable API, so external consumers should avoid binding to it.

## Test Signals
Compilation and generated API documentation are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/package-info.java

## Purpose
This package descriptor documents the core HDFS Federation router package, where `Router` acts as a transparent proxy and `RouterRpcServer` exposes NameNode client protocol to DFS clients.

## Important APIs, Types, And Functions
It applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.router`.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no local state or persistence. The file depends only on classification annotations and package-level Javadoc references.

## Integration Points
The descriptor sets compatibility expectations for the router package containing the RPC server, heartbeat services, quota manager, refresh services, and async/sync protocol modules.

## Risks
The package is private/evolving, so implementation details may change between Hadoop versions.

## Test Signals
Compilation and package Javadoc generation are the relevant checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/RouterSecurityManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/RouterSecurityManager.java

## Purpose
`RouterSecurityManager` owns the router delegation token secret manager and exposes token issue, renew, cancel, credential creation, and verification operations.

## Important APIs, Types, And Functions
Constructors either create a secret manager through `FederationUtil.newSecretManager(conf)` when Kerberos authentication is configured or accept one for tests. Public methods include `getSecretManager`, `stop`, `getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`, static `createCredentials`, and `verifyToken`. Internal helpers inspect remote-user authentication and audit token operations.

## Control Flow
Initialization only starts token management for Kerberos-configured routers. Token issue and renewal first verify that the connection auth method is Kerberos, Kerberos SSL, or certificate when security is enabled. Issue constructs a `DelegationTokenIdentifier` from owner, renewer, and real user, then creates a `Token` backed by the secret manager. Renewal and cancel delegate to the secret manager and decode token identifiers for audit logging on success or access-control failure.

## State, Persistence, And Dependencies
The manager stores one `AbstractDelegationTokenSecretManager<DelegationTokenIdentifier>`. Actual token/key persistence is delegated to the configured secret manager implementation, such as SQL or ZooKeeper. It depends on `RouterRpcServer.getRemoteUser`, Hadoop security classes, `DFSUtil`, and router RPC address for token service setup.

## Integration Points
Router RPC token protocol methods call this manager. WebHDFS uses `createCredentials` and `verifyToken` for URL-token flows. `FederationUtil.newSecretManager` selects the backing implementation.

## Risks
If security is enabled but the secret manager is absent or stopped, token issue returns null or initialization fails. Audit logging is debug-only and local. Auth checks depend on correctly unwrapping proxy users. `cancelDelegationToken` does not call `isAllowedDelegationTokenOp`, relying on secret-manager authorization instead.

## Test Signals
Tests should cover Kerberos and non-Kerberos initialization, token issue for proxy and non-proxy users, rejected simple-auth operations, renew/cancel access-control failures with audit token IDs, WebHDFS credential token service assignment, and `stop` calling `stopThreads`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/RouterSecurityManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/package-info.java

## Purpose
This descriptor documents the router security package, including the security manager and token store implementations.

## Important APIs, Types, And Functions
It applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.router.security`.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no state or persistence. Dependencies are Hadoop classification annotations.

## Integration Points
The descriptor covers the security manager package consumed by router RPC and WebHDFS security paths.

## Risks
The package is private/evolving and may change without public compatibility guarantees.

## Test Signals
Compilation and package documentation generation are adequate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/DistributedSQLCounter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/DistributedSQLCounter.java

## Purpose
`DistributedSQLCounter` coordinates monotonically allocated integer values across routers using a single-row SQL table.

## Important APIs, Types, And Functions
Public methods are `selectCounterValue`, `updateCounterValue(int)`, `updateCounterValue(int, Connection)`, and `incrementCounterValue(int)`. It stores the counter field name, table name, and `SQLConnectionFactory`.

## Control Flow
Reads execute `SELECT field FROM table`, optionally with `FOR UPDATE`. Updates execute `UPDATE table SET field = ?`. Increment disables autocommit, raises isolation to at least repeatable read, selects the row for update, calculates the new value, handles integer overflow by resetting from zero, updates the table, commits, and rolls back on failure.

## State, Persistence, And Dependencies
The durable state is the SQL table row. The class itself keeps only configuration strings and the connection factory. It depends on JDBC `Connection`, `Statement`, `PreparedStatement`, and `ResultSet`.

## Integration Points
`SQLDelegationTokenSecretManagerImpl` uses two counters for delegation token sequence numbers and delegation key IDs.

## Risks
The table and one initial row must already exist. SQL strings interpolate table and field names, so those names must be trusted constants. `FOR UPDATE` and isolation behavior are database-dependent. Overflow resets can reuse low values if not coordinated with existing records.

## Test Signals
Tests should cover missing row initialization errors, transaction rollback on update failure, concurrent increments, overflow behavior, autocommit modes, and database compatibility for `FOR UPDATE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/DistributedSQLCounter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/HikariDataSourceConnectionFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/HikariDataSourceConnectionFactory.java

## Purpose
`HikariDataSourceConnectionFactory` adapts Hadoop configuration into a HikariCP JDBC connection pool for the SQL token secret manager.

## Important APIs, Types, And Functions
The constructor reads connection URL, username, password, driver class, and all properties under the Hikari prefix. Public methods implement `getConnection()` and `shutdown()`. `getDataSource()` is visible for tests.

## Control Flow
Construction builds a `Properties` object, resolves the configured password via `DFSUtil.getPassword`, merges Hikari-specific properties, creates `HikariConfig`, and creates `HikariDataSource`. Calls to `getConnection` delegate to the pool; shutdown closes it.

## State, Persistence, And Dependencies
State is the in-process Hikari data source and pooled JDBC connections. Persistence is provided by the external SQL database. Dependencies include HikariCP, Hadoop `Configuration`, and SQL token-manager config keys.

## Integration Points
`SQLDelegationTokenSecretManagerImpl` uses this factory by default. `SQLConnectionFactory.getConnection(boolean)` wraps it to set autocommit for transactional counter operations.

## Risks
Missing or bad JDBC config fails at construction or first connection. Password handling depends on Hadoop credential provider resolution. Pool sizing and timeouts are entirely configuration-driven.

## Test Signals
Tests should verify property mapping, password resolution, Hikari prefix passthrough, connection acquisition, autocommit adjustment through the interface default, and datasource closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/HikariDataSourceConnectionFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLConnectionFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLConnectionFactory.java

## Purpose
`SQLConnectionFactory` defines the connection-provider contract for SQL-backed router delegation token persistence.

## Important APIs, Types, And Functions
It declares config key constants for URL, username, password, and driver. Required methods are `Connection getConnection()` and `shutdown()`. The default `getConnection(boolean autocommit)` sets autocommit on a new connection.

## Control Flow
Implementations return a JDBC connection. The default autocommit overload obtains a connection and mutates its autocommit mode before returning it.

## State, Persistence, And Dependencies
The interface has no state. Persistence is external SQL database state. It depends on JDBC and Hadoop SQL delegation token configuration prefixes.

## Integration Points
`HikariDataSourceConnectionFactory`, `DistributedSQLCounter`, and `SQLDelegationTokenSecretManagerImpl` use this contract.

## Risks
If `setAutoCommit` fails, callers receive an exception but the newly opened connection may need implementation-level cleanup. Implementations must define shutdown semantics carefully to avoid leaking pools.

## Test Signals
Tests should cover factory implementations, autocommit true/false behavior, shutdown idempotence, and exception handling when connection setup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLConnectionFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLDelegationTokenSecretManagerImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLDelegationTokenSecretManagerImpl.java

## Purpose
`SQLDelegationTokenSecretManagerImpl` persists router delegation tokens and delegation keys in SQL tables and coordinates distributed sequence allocation.

## Important APIs, Types, And Functions
It extends `SQLDelegationTokenSecretManager<AbstractDelegationTokenIdentifier>`. Overrides include `createIdentifier`, `stopThreads`, token insert/update/delete/select/stale-select methods, delegation-key insert/update/delete/select methods, and sequence/key counter select/update/increment methods. It owns a `SQLConnectionFactory`, `DistributedSQLCounter` instances, and a `SQLSecretManagerRetriableHandler`.

## Control Flow
Construction creates the connection factory and retry handler, initializes two distributed counters, starts superclass token-manager threads, and logs startup. Each SQL operation delegates through the retry handler, obtains a connection, prepares a statement, binds parameters, and executes. Token cleanup selects stale token rows by `modifiedTime`. Counter operations delegate to `DistributedSQLCounter`.

## State, Persistence, And Dependencies
Durable state lives in SQL tables: `Tokens`, `DelegationKeys`, `LastSequenceNum`, and `LastDelegationKeyId`. Process state includes superclass token caches and background threads plus the connection pool. Dependencies include JDBC, Hadoop delegation token classes, and the retry handler.

## Integration Points
`RouterSecurityManager` reaches this implementation through `FederationUtil.newSecretManager`. It plugs into Hadoop's `SQLDelegationTokenSecretManager` abstract persistence hooks.

## Risks
Required schema must exist and column names/types must match. Constructor wraps thread-start `IOException` in `RuntimeException`, so configuration failures can fail router startup hard. `selectStaleTokenInfos` uses `setMaxRows` rather than SQL `LIMIT`, which depends on driver behavior. Retry wraps all SQLExceptions as retryable before the retry policy decides, which may retry non-transient SQL errors.

## Test Signals
Tests should exercise full token/key CRUD, stale-token selection, distributed counter reservation, retry policy behavior, schema-missing failures, stop closing the connection factory, and interoperability across two manager instances sharing one database.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLDelegationTokenSecretManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLSecretManagerRetriableHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLSecretManagerRetriableHandler.java

## Purpose
This file defines the retry abstraction used by SQL token persistence and its `RetryProxy`-based implementation.

## Important APIs, Types, And Functions
`SQLSecretManagerRetriableHandler` exposes `execute(SQLCommandVoid)` and `<T> execute(SQLCommand<T>)`. Nested functional interfaces represent SQL commands. Package-private `SQLSecretManagerRetriableHandlerImpl` defines `MAX_RETRIES`, `RETRY_SLEEP_TIME_MS`, `getInstance`, execution methods, and `SQLSecretManagerRetriableException`.

## Control Flow
`getInstance` builds an exponential-backoff retry policy for `SQLSecretManagerRetriableException` and a try-once policy for all other exceptions, then wraps the implementation in a Hadoop `RetryProxy`. Execution methods run the command and convert any `SQLException` into the retryable subclass.

## State, Persistence, And Dependencies
No persistent state exists. Runtime state is the proxy and retry policy. Dependencies include Hadoop retry utilities, `Configuration`, and SQL token-manager config prefixes.

## Integration Points
`SQLDelegationTokenSecretManagerImpl` wraps every JDBC persistence operation with this handler.

## Risks
All SQLExceptions are treated as retryable at the implementation boundary, so permanent syntax/schema/auth errors may be retried until the configured budget is exhausted. Defaults allow zero retries. Because the implementation class is package-private, tests in other packages need to use the interface or same package.

## Test Signals
Tests should verify zero-retry default, configured retry counts and sleep, retry on wrapped SQLExceptions, no retry for non-SQL runtime exceptions, return values from generic commands, and logging of failed SQL commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLSecretManagerRetriableHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/ZKDelegationTokenSecretManagerImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/ZKDelegationTokenSecretManagerImpl.java

## Purpose
`ZKDelegationTokenSecretManagerImpl` is the ZooKeeper-backed router delegation token secret manager, with additional local token-cache synchronization for configurations where token watchers are disabled.

## Important APIs, Types, And Functions
It extends `ZKDelegationTokenSecretManager<AbstractDelegationTokenIdentifier>`. Important members include sync interval config, a single-thread scheduler, `localTokenCache`, `TOKEN_PATH`, and `checkAgainstZkBeforeDeletion`. Overrides include `startThreads`, `stopThreads`, `createIdentifier`, `cancelToken`, `removeStoredToken`, and `addOrUpdateToken`.

## Control Flow
Construction calls `startThreads` and logs startup. `startThreads` calls the superclass and, if token watchers are disabled, ensures the token root znode exists, rebuilds the local cache immediately, and schedules periodic cache rebuilds. Rebuild reads token child names through the raw ZooKeeper client, fetches token data via Curator, processes each token into `currentTokens`, and removes local tokens no longer present in ZooKeeper on non-initial runs. `cancelToken` temporarily disables extra ZK deletion checks because it is an explicit cancel path.

## State, Persistence, And Dependencies
Durable state lives in ZooKeeper znodes under the token root. Process-local state includes superclass token maps, `localTokenCache`, the scheduler, and a thread-local deletion-check flag. Dependencies include Hadoop ZK delegation token manager, Curator/ZooKeeper APIs, and Hadoop `Time`.

## Integration Points
Selected by router security configuration through `FederationUtil.newSecretManager`. It feeds `RouterSecurityManager` token operations and synchronizes token state among multiple routers.

## Risks
Constructor logs `startThreads` failures instead of failing construction, which can leave an unusable manager. `currentTokens` is mutated while iterating key sets during rebuild; concurrency depends on superclass map behavior. Scheduler exceptions are swallowed, so cache sync can silently stall. Raw ZooKeeper child listing avoids Curator sorting for scale but bypasses some Curator conveniences.

## Test Signals
Tests should cover watcher-enabled and watcher-disabled startup, root znode creation, initial and periodic cache rebuild, removal of deleted tokens, cancellation deletion-check behavior, scheduler shutdown, and failure modes when ZooKeeper is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/ZKDelegationTokenSecretManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/package-info.java

## Purpose
This descriptor documents token secret-manager implementations for router security.

## Important APIs, Types, And Functions
It applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.router.security.token` and notes that implementations should extend Hadoop's abstract delegation token secret manager.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no local state or persistence. The Javadoc references Hadoop delegation token secret manager contracts.

## Integration Points
The package contains SQL and ZooKeeper token persistence implementations selected by router security configuration.

## Risks
The package is private/evolving and not intended for stable external use.

## Test Signals
Compilation and generated package docs are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/CachedRecordStore.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/CachedRecordStore.java

## Purpose
`CachedRecordStore` is the base class for state-store APIs that keep an in-memory cache of persistent records.

## Important APIs, Types, And Functions
It extends `RecordStore<R>` and implements `StateStoreCache`. Important methods are `loadCache(boolean)`, `overrideExpiredRecords`, `overrideExpiredRecord`, `getCachedRecords`, and `getCachedRecordsAndTimeStamp`. It uses read/write locks to protect cached record lists and tracks cache timestamp, initialization, and last update.

## Control Flow
`loadCache` throttles refreshes to at most once every 500 ms unless forced. It fetches all records through the driver, optionally commits expired-record overrides/deletions, atomically replaces the cache under the write lock, updates metrics, and records local update time. Reads validate driver readiness and initialization, then copy cached records under the read lock.

## State, Persistence, And Dependencies
In-memory state includes cached records, the driver timestamp, initialized flag, update timestamps, locks, and the override-expired flag. Persistent state is owned by the `StateStoreDriver`; this class writes only when overriding expired/deletable records. It depends on `QueryResult`, `BaseRecord` expiration methods, metrics, and driver overwrite/delete handling.

## Integration Points
`MembershipStore`, `RouterStore`, `MountTableStore`, and `DisabledNameserviceStore` inherit this cache behavior. `StateStoreCacheUpdateService` calls `loadCache` periodically.

## Risks
`getCachedRecordsAndTimeStamp` returns the internal list object rather than a copy, unlike `getCachedRecords`. Async driver override mode returns null and leaves stale records until a later refresh. Cache refresh failures return false but keep old data. The 500 ms throttle can surprise explicit callers unless `force` is true.

## Test Signals
Tests should cover forced and throttled refresh, unavailable cache exceptions, expired-record override/delete behavior in sync and async driver modes, metrics updates, concurrent readers during refresh, and copy versus internal-list exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/CachedRecordStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/DisabledNameserviceStore.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/DisabledNameserviceStore.java

## Purpose
`DisabledNameserviceStore` defines the cached state-store API for nameservices administratively disabled in the federation.

## Important APIs, Types, And Functions
The abstract methods are `disableNameservice`, `enableNameservice`, and `getDisabledNameservices`. It stores `DisabledNameservice` records through `CachedRecordStore`.

## Control Flow
Concrete implementations perform record insert/delete/query operations through the state-store driver and cache inherited from `CachedRecordStore`.

## State, Persistence, And Dependencies
Persistent state is a set of `DisabledNameservice` records in the configured state-store backend. In-memory cache state comes from the base class.

## Integration Points
Router admin and resolver paths use this store to avoid routing to disabled namespaces. `StateStoreService` registers `DisabledNameserviceStoreImpl` as one of the built-in record stores.

## Risks
As an abstract contract, correctness depends on implementations refreshing cache after enable/disable changes and handling unavailable state-store errors consistently.

## Test Signals
Tests should cover disable, enable, idempotence, cache refresh visibility, unavailable store exceptions, and integration with resolver routing decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/DisabledNameserviceStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/MembershipStore.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/MembershipStore.java

## Purpose
`MembershipStore` defines the state-store management API for federated NameNode membership and HA state records.

## Important APIs, Types, And Functions
It extends `CachedRecordStore<MembershipState>` with expired-record override enabled. Abstract methods include `namenodeHeartbeat`, `getNamenodeRegistrations`, `getExpiredNamenodeRegistrations`, `getNamespaceInfo`, and `updateNamenodeRegistration`.

## Control Flow
Implementations receive heartbeat requests from router heartbeat services, write membership records, query cached registrations, aggregate namespace info, identify expired entries, and override specific NameNode registration state.

## State, Persistence, And Dependencies
Persistent state is `MembershipState` records in the driver backend. Cache state is periodically refreshed and expired membership records can be overridden or deleted by the base class using configured expiration/deletion intervals.

## Integration Points
`RouterHeartbeatService` writes NameNode observations. `ActiveNamenodeResolver` and router RPC routing read membership state. `StateStoreService` registers `MembershipStoreImpl` and configures membership expiration.

## Risks
Federation correctness depends on timely cache refresh and consistent quorum/aggregation in implementations. Expiration overrides may race with fresh heartbeats from other routers. Abstract requests/responses need compatible protocol implementations.

## Test Signals
Tests should cover heartbeat upserts, HA state updates, expired and deleted membership handling, namespace info aggregation, cache refresh, concurrent router observations, and unavailable state-store behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/MembershipStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/MountTableStore.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/MountTableStore.java

## Purpose
`MountTableStore` defines the cached management API for mount-table records that map global router paths to destination nameservices and paths.

## Important APIs, Types, And Functions
It extends `CachedRecordStore<MountTable>` and implements `MountTableManager`. Additional methods set `MountTableRefresherService` and `RouterQuotaManager`, expose the quota manager, and call `updateCacheAllRouters`.

## Control Flow
Concrete manager operations are inherited from `MountTableManager` and implemented by subclasses. After a mount-table mutation, implementations can call `updateCacheAllRouters`, which asks the refresher service to refresh this and peer routers.

## State, Persistence, And Dependencies
Persistent state is `MountTable` records in the state-store backend. Local state includes optional refresh service and quota manager references plus inherited cache state.

## Integration Points
Router path resolution, admin APIs, quota management, and `MountTableRefresherService` depend on this store. `StateStoreService` registers `MountTableStoreImpl`.

## Risks
If `refreshService` is null, mutations may not proactively refresh router caches. Refresh failure on state-store unavailability is logged but not thrown by `updateCacheAllRouters`. Quota manager coordination depends on implementation use.

## Test Signals
Tests should cover mount-table CRUD through the concrete implementation, cache refresh after mutation, refresh-service failure logging, quota-manager propagation, and router path resolution against cached records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/MountTableStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/RecordStore.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/RecordStore.java

## Purpose
`RecordStore` is the base abstraction for typed state-store API wrappers over a `StateStoreDriver`.

## Important APIs, Types, And Functions
It stores a record class and driver, exposes `getRecordClass` and `getDriver`, and provides static reflective factory `newInstance(Class<T>, StateStoreDriver)`.

## Control Flow
Subclasses call the protected constructor. `newInstance` looks for a public constructor taking `StateStoreDriver`, invokes it, logs errors, and returns null on failure.

## State, Persistence, And Dependencies
The class stores only the record type and driver reference. Persistence is handled by the driver and concrete stores.

## Integration Points
`StateStoreService.addRecordStore` uses `newInstance` to create `MembershipStoreImpl`, `MountTableStoreImpl`, `RouterStoreImpl`, and `DisabledNameserviceStoreImpl`.

## Risks
Factory failure returns null, and callers must avoid dereferencing without checks. Implementations need the expected constructor signature. Reflection errors are logged but not distinguished.

## Test Signals
Tests should cover factory success, missing constructor failure, driver/reference retention, and `StateStoreService` handling of factory failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/RecordStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/RouterStore.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/RouterStore.java

## Purpose
`RouterStore` defines the state-store API for router registration and heartbeat records.

## Important APIs, Types, And Functions
It extends `CachedRecordStore<RouterState>` with expired-record override enabled. Abstract methods are `getRouterRegistration`, `getRouterRegistrations`, and `routerHeartbeat`.

## Control Flow
Concrete implementations write router heartbeat state, query one router registration, or query all router registrations from cached/persistent state.

## State, Persistence, And Dependencies
Persistent state is `RouterState` records in the driver backend. Cache behavior and expired/deleted router-state overrides are inherited.

## Integration Points
Router heartbeat, admin status views, mount-table refresh across routers, and `StateStoreService` registration use this store.

## Risks
Stale router records can cause peers to target dead routers until expiration/deletion runs. The class Javadoc says no data is cached, but the class extends `CachedRecordStore`, so implementation behavior should be checked for consistency.

## Test Signals
Tests should cover heartbeat upsert, single/all registration queries, expiration and deletion, cache refresh, and peer-router discovery behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/RouterStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreCache.java

## Purpose
`StateStoreCache` is the minimal interface for components whose in-memory state can be refreshed from the state store.

## Important APIs, Types, And Functions
It declares `boolean loadCache(boolean force) throws IOException`.

## Control Flow
`StateStoreService` and cache update services call `loadCache`, optionally forcing refresh despite internal throttles.

## State, Persistence, And Dependencies
The interface has no state. Implementations decide what state to cache and how to read persistent store data.

## Integration Points
All cached record stores implement it, and external router components can register with `StateStoreService.registerCacheExternal`.

## Risks
The boolean result and thrown exception are both failure channels; callers must handle both. The interface does not define partial refresh semantics.

## Test Signals
Tests should cover service behavior when caches return false, throw `IOException`, and honor forced refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreCacheUpdateService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreCacheUpdateService.java

## Purpose
`StateStoreCacheUpdateService` periodically refreshes state-store-backed caches in the router.

## Important APIs, Types, And Functions
It extends `PeriodicService`, stores a `StateStoreService`, sets its interval from `DFS_ROUTER_CACHE_TIME_TO_LIVE_MS`, and implements `periodicInvoke`.

## Control Flow
During service initialization it reads the TTL configuration and sets the periodic interval. Each tick logs a debug message and calls `stateStore.refreshCaches()`.

## State, Persistence, And Dependencies
The service holds only a reference to `StateStoreService` and the inherited periodic-service schedule. It does not persist data directly.

## Integration Points
`StateStoreService` creates and registers it as a child service. It keeps membership, mount-table, router, disabled-nameservice, and external caches fresh.

## Risks
A too-long TTL increases stale routing information; a too-short TTL increases backend load. Refresh failures are handled inside `StateStoreService`.

## Test Signals
Tests should verify configured interval, periodic invocation, service lifecycle under `StateStoreService`, and behavior when refresh throws internally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreCacheUpdateService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreConnectionMonitorService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreConnectionMonitorService.java

## Purpose
`StateStoreConnectionMonitorService` periodically checks whether the state-store driver is ready and reopens it when needed.

## Important APIs, Types, And Functions
It extends `PeriodicService`, stores a `StateStoreService`, sets its interval from `FEDERATION_STORE_CONNECTION_TEST_MS`, and implements `periodicInvoke`.

## Control Flow
On each tick, it checks `stateStore.isDriverReady()`. If the driver is not ready, it logs and calls `stateStore.loadDriver()`.

## State, Persistence, And Dependencies
The service holds only a `StateStoreService` reference and inherited scheduling state. It does not persist data directly.

## Integration Points
`StateStoreService` registers this as a child service so routers can recover from backend connection loss without restart.

## Risks
`loadDriver` failures are logged inside `StateStoreService`; repeated failures can keep the router in a degraded or safe-mode state. The interval controls recovery latency.

## Test Signals
Tests should cover interval configuration, no-op when ready, driver load when not ready, repeated failure behavior, and service lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreConnectionMonitorService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreService.java

## Purpose
`StateStoreService` is the router service that creates, owns, monitors, and refreshes the pluggable state-store driver and its typed record stores.

## Important APIs, Types, And Functions
Important methods include `serviceInit`, `serviceStart`, `serviceStop`, private `addRecordStore`, `getRegisteredRecordStore`, `getRecordStores`, `getSupportedRecords`, `loadDriver`, `isDriverReady`, `closeDriver`, `getDriver`, `getIdentifier`, `setIdentifier`, `getCacheUpdateTime`, `stopCacheUpdateService`, `registerCacheExternal`, `refreshCaches`, `refreshCaches(boolean)`, `loadCache(Class<?>)`, `loadCache(Class<?>, boolean)`, and `getMetrics`.

## Control Flow
Initialization selects the driver class from configuration, instantiates it, registers built-in record stores, adds connection-monitor and cache-update child services, configures membership/router expiration intervals, and creates metrics/JMX if enabled. Service start calls `loadDriver`, which initializes the driver with supported records and refreshes caches on success. Periodic services monitor connections and refresh caches. Service stop closes the driver and metrics before stopping children.

## State, Persistence, And Dependencies
Process state includes configuration, identifier, driver, metrics, record-store map, cache updater, monitor service, last successful cache update time, and internal/external cache lists. Durable state is entirely in the configured driver backend. Dependencies include Hadoop service lifecycle, reflection, metrics/MBeans, router config keys, record implementations, and state-store driver APIs.

## Integration Points
The router uses this service for membership, mount table, router registration, disabled nameservice state, and external caches. Driver implementations include file, filesystem, MySQL, and ZooKeeper. Router services depend on `getRegisteredRecordStore` and cache freshness.

## Risks
`addRecordStore` assumes `RecordStore.newInstance` returns non-null; reflection failure can become a null dereference. `loadDriver` synchronizes on the driver object and calls `refreshCaches` inside the lock. External cache registration is unsynchronized. Metrics MBean registration failures can be fatal only for compliance errors, while metrics exceptions are logged. Cache update time uses local monotonic time rather than driver time.

## Test Signals
Tests should cover driver class selection, failed driver initialization and later recovery, record store registration, metrics enabled/disabled, expiration config propagation, cache refresh success/failure, external cache registration, targeted cache loading, and service start/stop resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreUnavailableException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreUnavailableException.java

## Purpose
`StateStoreUnavailableException` signals that the state-store backend or cache is not ready for an operation.

## Important APIs, Types, And Functions
It extends `IOException`, defines `serialVersionUID`, and has a message constructor.

## Control Flow
There is no internal control flow beyond exception construction.

## State, Persistence, And Dependencies
No state beyond the exception message exists. There is no persistence.

## Integration Points
`StateStoreDriver.verifyDriverReady` and `CachedRecordStore.checkCacheAvailable` throw this exception. Router callers can treat it as retryable state-store unavailability.

## Risks
Because it is an `IOException`, generic IO handling may hide the specific retry signal unless callers check the type.

## Test Signals
Tests should verify specific exception propagation from unavailable driver/cache paths and client retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreUnavailableException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreUtils.java

## Purpose
`StateStoreUtils` provides helper methods for record-class normalization, record filtering, and address string formatting.

## Important APIs, Types, And Functions
Methods include `getRecordClass(Class<T>)`, `getRecordClass(T)`, `getRecordName(Class<T>)`, `filterMultiple(Query<T>, Iterable<T>)`, `getHostPortString`, and `getIpPortString`.

## Control Flow
Record-class normalization walks superclasses while class names end in `Impl`, stopping before `BaseRecord`. Filtering iterates records and applies `Query.matches`. Host formatting converts wildcard `0.0.0.0` to local host name; IP formatting uses `NetUtils.getConnectAddress`.

## State, Persistence, And Dependencies
The utility is stateless. It depends on `BaseRecord`, `Query`, network address classes, `NetUtils`, and logging.

## Integration Points
Drivers and stores use record-name normalization for storage names and query behavior. Address formatting is used in router state/registration paths.

## Risks
The `Impl` suffix heuristic depends on naming conventions and may fail for differently named generated classes. `getHostPortString` can return an empty string on local host resolution failure. `getIpPortString` assumes the connect address has a resolved `InetAddress`.

## Test Signals
Tests should cover PB implementation class normalization, accidental `BaseRecord` over-walk, query filtering, wildcard host replacement, unresolved addresses, and IP formatting through `NetUtils`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreDriver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreDriver.java

## Purpose
`StateStoreDriver` is the abstract base for pluggable state-store backend implementations and the bridge between typed record stores and persistence.

## Important APIs, Types, And Functions
It implements `StateStoreRecordOperations`. Core methods include `init`, `initDriver`, `initRecordStorage`, `isDriverReady`, `verifyDriverReady`, `close`, `getTime`, `getIdentifier`, `getMetrics`, and `handleOverwriteAndDelete`. It can create an optional thread pool for asynchronous expired-record override/delete work.

## Control Flow
`init` stores configuration, identifier, and metrics, calls backend-specific `initDriver`, initializes storage for every supported record class, and configures sync or async override mode based on thread-count config. `verifyDriverReady` throws a state-store unavailable exception with driver and host context. `handleOverwriteAndDelete` writes expired overrides through `putAll` and deletes records through `removeMultiple`, either synchronously or by submitting runnables to the executor.

## State, Persistence, And Dependencies
Driver state includes configuration, identifier, metrics, and optional executor. Backend subclasses own actual connection state and persistence. Dependencies include router config keys, metrics, record utilities, Java executors, and Hadoop time.

## Integration Points
`StateStoreService` initializes and owns the driver. `CachedRecordStore` uses `handleOverwriteAndDelete` during expiration override. Concrete drivers extend this class for file, filesystem, MySQL, ZooKeeper, and serializer-backed storage.

## Risks
Async override mode submits tasks without surfacing later failures to cache refresh callers. `close` shuts down the executor but does not await termination. `handleOverwriteAndDelete` uses a lambda that mutates a local `result` variable in sync mode; behavior must be compiled/verified in this source version. Backend readiness and storage initialization must be consistent or routers may stay in safe mode.

## Test Signals
Tests should cover initialization success/failure, per-record storage setup, readiness verification error messages, sync and async override/delete behavior, executor shutdown, metrics access, and backend driver recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreDriver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreOperationResult.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreOperationResult.java

## Purpose
`StateStoreOperationResult` represents the outcome of bulk state-store operations, including failed record keys.

## Important APIs, Types, And Functions
It stores `failedRecordsKeys` and `isOperationSuccessful`, provides constructors from a list or single failed key, getters, and a static shared default success result.

## Control Flow
The single-key constructor treats a non-empty key as failure and an empty/null key as success. `getDefaultSuccessResult` returns an immutable success instance with no failed keys.

## State, Persistence, And Dependencies
State is immutable per instance, though the list passed to the main constructor is not defensively copied. There is no persistence.

## Integration Points
`StateStoreRecordOperations.putAll` returns this result, and `StateStoreBaseImpl.put` checks `isOperationSuccessful`.

## Risks
Callers can mutate a list passed into the constructor after construction. The shared success result should remain safe because it uses `Collections.emptyList`.

## Test Signals
Tests should cover list and single-key constructors, empty key success, default success singleton, and behavior when failed key lists are mutable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreOperationResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreRecordOperations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreRecordOperations.java

## Purpose
`StateStoreRecordOperations` defines the CRUD contract that every state-store driver must expose for `BaseRecord` types.

## Important APIs, Types, And Functions
The interface declares `get`, single-query `get`, `getMultiple`, `put`, `putAll`, `remove(record)`, `removeMultiple`, `removeAll`, query-based `remove`, and multi-query `remove`. Methods are annotated with Hadoop retry semantics: reads are `@Idempotent`, writes/removes are `@AtMostOnce`.

## Control Flow
Implementations fetch records by class, optionally filter by `Query`, create/update records with conflict flags, and remove records by object, class, or query.

## State, Persistence, And Dependencies
The interface has no state. Persistent behavior is defined by concrete drivers. It depends on `BaseRecord`, `Query`, `QueryResult`, and `StateStoreOperationResult`.

## Integration Points
`StateStoreDriver` implements this interface. Record stores use it to persist memberships, mount tables, router state, and disabled nameservices.

## Risks
Default implementations in `StateStoreBaseImpl` require `get` to return fresh record instances. Backend-specific filtering and atomicity vary by driver. `allowUpdate` and `errorIfExists` semantics must be implemented consistently.

## Test Signals
Driver compliance tests should cover all CRUD methods, query filtering, duplicate single-query detection, conflict flags, bulk partial failures, retry annotations, and freshness of returned records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreRecordOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreSerializer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreSerializer.java

## Purpose
`StateStoreSerializer` abstracts record instantiation and serialization/deserialization for state-store backends.

## Important APIs, Types, And Functions
Static methods include `getSerializer()`, `getSerializer(Configuration)`, private `newSerializer`, and `newRecord`. Abstract methods include `newRecordInstance`, `serialize(BaseRecord)`, `serializeString(BaseRecord)`, and byte/string `deserialize`.

## Control Flow
`getSerializer(null)` lazily initializes a singleton using a new default configuration. `getSerializer(conf)` creates a new configured serializer instance. `newSerializer` reads the serializer class from configuration and instantiates it through `ReflectionUtils`.

## State, Persistence, And Dependencies
The only state is the static default serializer singleton. There is no persistence. Dependencies include router config keys, Hadoop reflection utilities, and `BaseRecord`.

## Integration Points
State-store drivers use serializers to create PB-backed records and convert records to backend storage formats. `StateStoreSerializerPBImpl` is the default implementation in this module.

## Risks
The singleton default ignores later configuration changes. Serializer implementations must be thread-safe if shared. Deserialization errors are surfaced as `IOException`.

## Test Signals
Tests should cover default singleton creation, configured serializer override, `newRecord`, byte and string round trips, invalid data failures, and concurrent access to the default serializer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreSerializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/impl/StateStoreBaseImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/impl/StateStoreBaseImpl.java

## Purpose
`StateStoreBaseImpl` provides default, backend-agnostic implementations for optional `StateStoreDriver` record operations.

## Important APIs, Types, And Functions
It implements single-query `get`, `getMultiple`, `put`, `remove(record)`, `removeMultiple`, and multi-query `remove`. It uses `StateStoreUtils.filterMultiple`, `StateStoreUtils.getRecordClass`, `Query`, and Java streams.

## Control Flow
Single-query `get` delegates to `getMultiple` and requires zero or one result. `getMultiple` fetches all records for a class and filters in memory. `put` wraps one record and calls `putAll`. `remove(record)` builds a query from the record and delegates to query removal. `removeMultiple` either iterates per record when classes differ or builds queries and calls multi-query removal for same-class records. Multi-query removal loops over queries by default.

## State, Persistence, And Dependencies
The class adds no state beyond `StateStoreDriver`. Persistence behavior is inherited from concrete drivers, especially their implementations of `get`, `putAll`, `removeAll`, and query `remove`.

## Integration Points
Concrete state-store drivers extend this class when their backend can rely on read/filter/write-all defaults or override only performance-sensitive methods.

## Risks
The defaults are inefficient for large stores because they read all records and filter in memory. Correctness depends on `get` returning fresh object instances and `Query` matching primary keys accurately. Mixed-class bulk removal falls back to iterative calls with weaker batching.

## Test Signals
Tests should cover zero/one/multiple query results, in-memory filtering, put delegation, same-class and mixed-class `removeMultiple`, query result counts, and performance-sensitive drivers overriding defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/impl/StateStoreBaseImpl.java -->
