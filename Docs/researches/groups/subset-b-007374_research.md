# subset-b-007374 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/DynConstructors.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/DynConstructors.java

`DynConstructors` is a limited-private, unstable reflection helper copied from Parquet for locating and invoking constructors dynamically. Its main type is `DynConstructors.Ctor<C>`, a constructor wrapper that extends `DynMethods.UnboundMethod` so constructor invocations can be used through the same dynamic invocation surface as methods. `Ctor` exposes `getConstructedClass()`, `newInstanceChecked()`, `newInstance()`, `invoke()`, and `invokeChecked()`. Binding is explicitly forbidden because constructors have no receiver, while `isStatic()` returns true to fit the method abstraction.

The `Builder` accumulates candidate constructors and keeps the first successful match. Public constructors are found with `Class.getConstructor()`, while hidden constructors are found with `getDeclaredConstructor()` and made accessible through a privileged action. String class names are loaded with a configurable `ClassLoader`, defaulting to the current thread context loader. Failures are stored in a `Map<String, Throwable>` and formatted into build failures, which is useful when a caller probes several optional implementations.

There is no persistence beyond builder fields and no synchronization; builders are intended for one-thread construction. The class depends on Java reflection, `AccessController`, Hadoop `Preconditions`, and `DynMethods.throwIfInstance()` for exception unwrapping. Important integrations include `NetUtils` and `SignalUtil`, where Hadoop constructs optional platform-specific exception or JDK signal objects without hard dependencies. Risks are reflective access restrictions under newer JVM/module policies, unchecked raw `Ctor` storage inside `Builder`, and the fact that invocation arity/type errors surface at runtime. Test signals are `TestDynConstructors`, covering missing classes/constructors, first-match semantics, hidden constructors, thrown checked exceptions, and constructor invocation through `invoke()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/DynConstructors.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/DynMethods.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/DynMethods.java

`DynMethods` is the companion dynamic method invocation utility for optional APIs and compatibility shims. `UnboundMethod` wraps a `java.lang.reflect.Method`, records a display name, caches fixed arity for non-varargs methods, and exposes checked and unchecked invocation. `BoundMethod` binds an unbound method to an instance receiver, while `StaticMethod` invokes with a null receiver. A singleton `NOOP` method provides an optional no-operation implementation returning null.

Control flow centers on `Builder`: candidates are tried in declaration order and the first loadable method wins. Public methods use `Class.getMethod()`, hidden methods use `getDeclaredMethod()` plus privileged `setAccessible(true)`, constructors can be adapted through `DynConstructors.Builder`, and string class names are resolved through a configurable loader. `orNoop()` is terminal in practice because once it sets the method subsequent `impl()` calls are skipped. `buildChecked()` and `build()` fail if no candidate was found; `buildChecked(receiver)`/`build(receiver)` and static build variants add receiver/static validation.

State is builder-local and unsynchronized. Invocation unwraps `InvocationTargetException` by rethrowing checked `Exception`, `RuntimeException`, or wrapping other causes in `RuntimeException`. Fixed-arity invocation truncates extra arguments with `Arrays.copyOfRange()` and only logs arity mismatch, so incorrect calls may fail later through reflection. Dependencies include SLF4J logging, Hadoop `Preconditions`, reflection, and `DynConstructors`. Integration points include `SignalUtil`, `BindingUtils`, `DynamicWrappedIO`, and `DynamicWrappedStatistics`, where optional Hadoop/Java methods are loaded without compile-time coupling. Risks include reflective access failures, null-sensitive `toString()` for non-NOOP null methods, runtime-only signature checks, and module-system restrictions. `TestDynMethods` covers missing candidates, first-match behavior, varargs, bad arguments, exceptions, renamed methods, string class lookup, hidden methods, binding/static checks, constructor adaptation, and NOOP behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/DynMethods.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/package-info.java

This package descriptor marks `org.apache.hadoop.util.dynamic` as limited-private to testing and unstable. Its purpose is dynamic class loading and instantiation, with code lineage from Apache Parquet and a related fork in Apache Iceberg. The package-level API promise is therefore intentionally narrow: Hadoop uses it internally for optional compatibility layers rather than as a stable user-facing reflection framework.

There are no executable functions, persistent fields, or control-flow branches in this file. The important behavior is metadata: `@InterfaceAudience.LimitedPrivate("testing")` and `@InterfaceStability.Unstable` apply to package documentation and communicate that consumers should not assume long-term binary/source compatibility.

Dependencies are limited to Hadoop classification annotations. Integration is through the package classes `DynMethods`, `DynConstructors`, and neighboring helpers such as `BindingUtils`; real callers include JDK signal support and wrapped IO/statistics compatibility code. The main risk is accidental external adoption of unstable reflection helpers, especially because the classes are generally useful and similar to Parquet/Iceberg utilities. Test signals are indirect through `TestDynMethods` and `TestDynConstructors`; the package descriptor itself has no dedicated tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/BiFunctionRaisingIOE.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/BiFunctionRaisingIOE.java

`BiFunctionRaisingIOE<T, U, R>` is a checked-IO equivalent of a two-argument Java function. Its single abstract method `apply(T, U)` returns `R` and may throw `IOException`, making it usable as a lambda target for Hadoop filesystem operations that naturally fail with checked IO errors.

The default `unchecked(T, U)` method is the whole control-flow wrapper: it invokes `apply()`, returns the result on success, and converts any `IOException` into `UncheckedIOException`. Runtime exceptions are not caught and propagate as-is. The interface has no state, persistence, synchronization, or dependencies beyond Java `IOException` and `UncheckedIOException`.

The integration point is package-wide: it lets APIs that need Java functional composition preserve IO-specific checked signatures until they cross into APIs such as streams, suppliers, or futures that only accept unchecked failures. It complements `FunctionRaisingIOE`, `CallableRaisingIOE`, and `FunctionalIO`. Risks are modest but important: once callers use `unchecked()`, downstream code must know to unwrap `UncheckedIOException` if it wants original IO types; API overloads between similar functional interfaces can become ambiguous for lambdas. Test coverage is mostly indirect through `TestFunctionalIO`, which validates the package wrapping/extraction pattern for checked IO lambdas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/BiFunctionRaisingIOE.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/CallableRaisingIOE.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/CallableRaisingIOE.java

`CallableRaisingIOE<R>` is Hadoop's zero-argument callable form for lambdas that return a value and may throw `IOException`. It deliberately narrows the checked exception type compared with `java.util.concurrent.Callable`, which makes filesystem and remote-IO call chains easier to type and reason about.

The primary API is `apply()`. The default `unchecked()` adapter runs `apply()` and wraps `IOException` in `UncheckedIOException`; unchecked exceptions pass through. There is no internal state or persistence. Dependencies are only Java IO exception classes.

This interface is heavily integrated across the package. `LazyAtomicReference` uses it as a lazy constructor, `FutureIO.eval()` evaluates it into a `CompletableFuture`, `FunctionalIO` wraps it into suppliers, and `RemoteIterators.haltableRemoteIterator()` uses it as a continuation predicate. Its main risk is semantic conversion: checked IO failures can become unchecked at API boundaries and must be unwrapped intentionally. Another risk is lambda overload ambiguity; `InvocationRaisingIOE` explicitly warns implementors not to overload purely to distinguish these interfaces. Test signals include `TestFunctionalIO` for wrapping behavior, `TestLazyReferences` for lazy evaluation and repeated construction failures, and `TestFutureIO`/caller tests for future evaluation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/CallableRaisingIOE.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/CloseableTaskPoolSubmitter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/CloseableTaskPoolSubmitter.java

`CloseableTaskPoolSubmitter` is a small public unstable adapter from `ExecutorService` to `TaskPool.Submitter` with lifecycle management. It lets callers pass an executor to `TaskPool` and close the adapter when the pool should be shut down.

The API consists of a constructor requiring a non-null `ExecutorService`, `getPool()`, `submit(Runnable)`, and `close()`. `submit()` delegates directly to `pool.submit(task)`. `close()` calls `ExecutorService.shutdown()` and then sets the field to null; it is idempotent in the sense that repeated close calls do nothing after the first.

The object has one mutable state field, `pool`, with no synchronization or volatile semantics. It does not await termination, force shutdown, reject submissions after close with a custom error, or guard against `submit()` after close; post-close submission will fail with a null dereference. Dependencies are Java concurrency and Hadoop audience/stability annotations. It integrates with `TaskPool.Builder.executeWith()` and appears in S3A IO statistics integration tests, where listing tasks execute in a pool while preserving the caller's statistics context. Risks are lifecycle-related: callers must own the executor policy, await termination if needed, and avoid concurrent close/submit races. Test signals are indirect through `TestTaskPool` and S3A tests such as `ITestS3AIOStatisticsContext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/CloseableTaskPoolSubmitter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/CommonCallableSupplier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/CommonCallableSupplier.java

`CommonCallableSupplier<T>` bridges `Callable<T>` into `Supplier<T>` for use with `CompletableFuture.supplyAsync()` while preserving Hadoop's IO exception conventions. It is final and stores a single callable supplied at construction.

`get()` invokes `call.call()`. Runtime exceptions are rethrown unchanged, `IOException` becomes `UncheckedIOException`, and other checked exceptions become `UncheckedIOException(new IOException(e))`. `submit(Executor, Callable<T>)` builds a `CompletableFuture` by wrapping the callable in this supplier. `waitForCompletion(List<CompletableFuture<T>>)` converts a list to `CompletableFuture.allOf()` and delegates to the single-future method. `waitForCompletion(CompletableFuture<T>)` uses `join()` inside a `DurationInfo` logging scope, converts cancellation to `IOException`, and delegates `CompletionException` unwrapping to `FutureIO.raiseInnerCause()`. `waitForCompletionIgnoringExceptions()` swallows and logs at debug, while `maybeAwaitCompletion()` treats null as no-op.

The only persistent state is the callable reference; there is no synchronization. Dependencies include `CompletableFuture`, `Executor`, SLF4J, Hadoop `DurationInfo`, and `FutureIO`. Integration is visible in Hadoop test utilities and S3A asynchronous helper code. Risks include cancellation being normalized to generic `IOException` here, unlike `FutureIO.awaitFuture()` which preserves `CancellationException`; `waitForCompletionIgnoringExceptions()` logs without including the exception as a parameter; and wrapping non-IO checked exceptions as IO can obscure original type unless callers inspect causes. Test signals are indirect through async utility callers and `FutureIO` exception-unwrapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/CommonCallableSupplier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/ConsumerRaisingIOE.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/ConsumerRaisingIOE.java

`ConsumerRaisingIOE<T>` is a checked-IO version of `java.util.function.Consumer`. Its `accept(T)` method allows `IOException`, making it a natural callback type for operations over `RemoteIterator`, file statuses, stream entries, and other Hadoop FS values.

The default `andThen()` composes two checked consumers. Its control flow first invokes the current consumer, then invokes `next.accept(t)` only if the first call succeeds. Either stage may throw `IOException`; unchecked exceptions also pass through. The implementation does not null-check `next`, so null composition fails when the chain is invoked.

There is no state or persistence. The interface depends only on `IOException` and is integrated most visibly through `RemoteIterators.foreach()`, where each iterator element is passed to a consumer and the iterator is cleaned up in a `finally` block. Risks are the usual callback risks: side effects in the first consumer are not rolled back if the second fails, and exception propagation determines whether iterator cleanup happens at the calling utility layer. Test signals are indirect through `TestRemoteIterators`, which exercises `foreach()` conversion to lists and checked iterator handling, and broader S3A listing tests that use `RemoteIterators.foreach()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/ConsumerRaisingIOE.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/Function4RaisingIOE.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/Function4RaisingIOE.java

`Function4RaisingIOE<I1, I2, I3, I4, R>` is a four-argument functional interface whose `apply()` method can throw `IOException`. It fills a gap left by `java.util.function`, which has neither checked exceptions nor a standard arity-four function.

There is no default unchecked adapter, state, persistence, synchronization, or control flow beyond the single abstract method. The dependency surface is only `java.io.IOException`. Its intended role is API shape support: Hadoop code can accept a lambda involving several IO-related inputs without broadening the signature to `Exception` or inventing local functional interfaces.

Integration is package-level rather than strongly coupled in this source subset. It belongs to the same family as `FunctionRaisingIOE` and `BiFunctionRaisingIOE`, allowing utility code to remain explicit about IO failures. Risks are mostly API ergonomics: without an unchecked helper, callers crossing into Java stream/future APIs need their own wrapper; with four generic inputs, lambda target typing can be harder to read and overloads should be avoided. Test signals are indirect through compile-time usage and package tests for neighboring checked-IO functional adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/Function4RaisingIOE.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FunctionRaisingIOE.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FunctionRaisingIOE.java

`FunctionRaisingIOE<T, R>` is the one-argument checked-IO counterpart to `java.util.function.Function`. It is central to this utility package because mapping and filtering remote filesystem iterators often need to throw `IOException`.

The abstract `apply(T)` returns `R` or throws `IOException`. The default `unchecked(T)` wraps only `IOException` in `UncheckedIOException` and otherwise preserves runtime failures. No state is held. Dependencies are Java IO exception classes.

Integration is concrete: `RemoteIterators.mappingRemoteIterator()` uses it to transform each source value, `filteringRemoteIterator()` uses `FunctionRaisingIOE<? super S, Boolean>` as its predicate, and `FunctionalIO.toUncheckedFunction()` adapts it to a standard Java `Function`. This lets code keep checked exceptions while inside Hadoop APIs and convert only at boundaries that require unchecked functions. Risks include nullable Boolean results in filters causing unboxing failures, wrapped IO failures being easy to mishandle in stream APIs, and lambda overload ambiguity with other package interfaces. Test signals include `TestFunctionalIO.testUncheckedFunction()` and `TestRemoteIterators` mapping/filtering cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FunctionRaisingIOE.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FunctionalIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FunctionalIO.java

`FunctionalIO` is a private utility class for converting between Hadoop's checked-IO functional interfaces and standard Java functional types. It has no instance state and a private constructor.

`uncheckIOExceptions(CallableRaisingIOE<T>)` delegates to `CallableRaisingIOE.unchecked()`. `toUncheckedIOExceptionSupplier()` converts a checked callable to a `Supplier<T>` that throws `UncheckedIOException`. `extractIOExceptions(Supplier<T>)` reverses that boundary by catching `UncheckedIOException` and throwing its `IOException` cause. `toUncheckedFunction(FunctionRaisingIOE<T, R>)` converts a checked IO function into a standard `Function<T, R>`.

There is no persistence or synchronization. Dependencies are Java `Supplier`, `Function`, `IOException`, `UncheckedIOException`, and Hadoop `InterfaceAudience.Private`. Integration points include `LazyAtomicReference.get()`, S3A utility code, wrapped IO helpers, upload content providers, and tests that need to flow IO operations through Java APIs that do not allow checked exceptions. The main risk is that `extractIOExceptions()` only catches `UncheckedIOException`; other runtime wrappers remain runtime failures. This is intentional but requires callers to know which wrapper was used. Test signals are strong in `TestFunctionalIO`: IO wrapping, no double-wrapping of existing `UncheckedIOException`, supplier conversion, wrap-and-extract identity, and function conversion are all covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FunctionalIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FutureIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FutureIO.java

`FutureIO` provides public unstable helpers for bridging futures, async filesystem APIs, and checked `IOException` semantics. It was promoted from filesystem implementation support so application code can wait on async IO without losing original IO failures.

`awaitFuture(Future<T>)` and the timeout overload call `Future.get()`, preserve `CancellationException`, convert thread interruption into `InterruptedIOException`, and unwrap `ExecutionException` through `raiseInnerCause()`. `awaitAllFutures()` evaluates a collection sequentially and returns results. `cancelAllFuturesAndAwaitCompletion()` cancels every future, then waits within a shrinking duration budget, swallowing cancellation, IO, and timeout failures while returning any successful results. `unwrapInnerException(Throwable)` recursively unwraps `ExecutionException` and `CompletionException`, returns `IOException`, extracts causes from `UncheckedIOException`, rethrows runtime exceptions/errors, and wraps other causes in new `IOException`.

The builder option helpers propagate configuration keys with a prefix into `FSBuilder` as optional or mandatory options. `eval(CallableRaisingIOE<T>)` runs a checked callable in the current thread, immediately rethrowing `UnsupportedOperationException` and `IllegalArgumentException`, but completing a `CompletableFuture` exceptionally for other throwables.

State is purely local. Dependencies include Java futures, `Duration`, Hadoop `Configuration`, `FSBuilder`, `Time`, and SLF4J. Integration is broad in S3A input streams, block output streams, audit manager, wrapped IO, contract tests, and multipart/vector read tests. Risks include sequential waiting in collection methods, `Duration.toMillis()` truncation, cancellation semantics differing from `CommonCallableSupplier`, and potential null-cause wrapping behavior. Test signals include `TestFutureIO`, contract tests using async reads, and S3A tests for `awaitFuture`, cancellation, and async IO paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FutureIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/InvocationRaisingIOE.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/InvocationRaisingIOE.java

`InvocationRaisingIOE` is the void-returning, zero-argument checked-IO lambda type. It represents an operation that may throw `IOException` without returning a value.

The API is a single `apply()` method. There are no default wrappers, fields, persistence, or synchronization. Dependencies are limited to `IOException`. The Javadoc explains the design motivation: Hadoop has several historical void-callable interfaces, and this package aims to consolidate the pattern. It also warns API implementors not to rely on overloads to distinguish functional interface types, because lambda target typing can become ambiguous.

Integration is conceptual with `RunnableRaisingIOE` and `CallableRaisingIOE`: use this interface when the call should remain checked and not implement `Runnable`; use `RunnableRaisingIOE` when Java executor APIs are the target. Risks are low but include caller inconvenience when crossing into Java APIs because there is no built-in unchecked adapter on this interface. Test coverage is indirect through package compilation and neighboring functional wrapper tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/InvocationRaisingIOE.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/LazyAtomicReference.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/LazyAtomicReference.java

`LazyAtomicReference<T>` is a lazy, caching reference whose constructor is a `CallableRaisingIOE<? extends T>`. It implements both `CallableRaisingIOE<T>` and `Supplier<T>`, so it can participate in Hadoop checked-IO chains and standard Java supplier APIs.

The state is an `AtomicReference<T>` and a non-null constructor callback. `eval()` is synchronized: if the reference is already non-null it returns it; otherwise it invokes the constructor, requires a non-null result, stores it, and returns the stored value. `apply()` delegates to `eval()` with checked IO semantics. `get()` delegates to `FunctionalIO.uncheckIOExceptions()` and therefore converts `IOException` to `UncheckedIOException`. `isSet()` reports whether a value is cached. `lazyAtomicReferenceFromSupplier()` adapts a standard `Supplier<T>`.

Persistence is in-memory only. The synchronized `eval()` makes construction single-threaded, while `AtomicReference` lets subclasses and `isSet()` read state safely. The null result prohibition is important because null is the sentinel for “not evaluated.” Integration points include S3A encryption/client availability checks and lazy AWS client construction. Risks include repeated constructor invocation after failures because failures do not cache, inability to cache null, and subclasses needing care with protected `getReference()`. `TestLazyReferences` covers lazy single evaluation, supplier integration, `UncheckedIOException` wrapping, failure retry behavior, and state reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/LazyAtomicReference.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/LazyAutoCloseableReference.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/LazyAutoCloseableReference.java

`LazyAutoCloseableReference<T extends AutoCloseable>` extends `LazyAtomicReference` for lazily constructed resources that must be closed. It is used where heavyweight clients or stream factories should be created on demand and released with their owner.

State adds an `AtomicBoolean closed`. `eval()` is synchronized, checks that the reference is not closed, and then delegates to the superclass lazy evaluation. `close()` is synchronized and idempotent: `closed.getAndSet(true)` prevents repeated work. If a value exists, it calls `close()` on that value and clears the underlying atomic reference in a `finally` block, even if resource close fails. Closing an unevaluated reference is allowed. `isClosed()` exposes the closed flag. `lazyAutoCloseablefromSupplier()` adapts standard suppliers.

There is no external persistence. Dependencies are `LazyAtomicReference`, `CallableRaisingIOE`, `AtomicBoolean`, `Supplier`, and Hadoop `Preconditions.checkState`. Integration appears in S3A `ClientManagerImpl` and analytics stream factories for lazy AWS clients/transfer managers. Risks are lifecycle oriented: once closed, all `eval()`, `get()`, and `apply()` attempts fail; close failures are only reported on the first close because the closed flag remains set and the reference is nulled; concurrent users can still hold a previously returned resource while another thread closes it. `TestLazyReferences` covers evaluated/unevaluated close, repeated close, post-close access failures, and close failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/LazyAutoCloseableReference.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/RemoteIterators.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/RemoteIterators.java

`RemoteIterators` is a public unstable utility class for creating, transforming, filtering, consuming, and cleaning Hadoop `RemoteIterator` instances while preserving `IOStatisticsSource` and close behavior through wrapper chains.

Factory methods create iterators from a singleton, Java `Iterator`, `Iterable`, array, long range, mapper, type cast, filter predicate, closeable side resource, and halt predicate. `toList()` and `toArray()` consume iterators through `foreach()`. `foreach()` loops while `hasNext()`, calls `next()`, invokes a `ConsumerRaisingIOE`, counts processed entries, and always calls `cleanupRemoteIterator()` in `finally`. Cleanup logs IO statistics at debug and closes the iterator if it is `Closeable`.

Internal classes carry most control flow. `SingletonIterator` treats null as empty and exposes statistics from the singleton. `WrappedJavaIterator` adapts Java iterators and closes them if possible. `WrappingRemoteIterator` is the base for wrappers, passing through stats/close and auto-closing when the source is exhausted or errors. `MappingRemoteIterator` maps source values, `TypeCastingRemoteIterator` performs unchecked casts, `FilteringRemoteIterator` prefetches the next accepted value in `hasNext()`, `CloseRemoteIterator` closes both source and extra resource once, `MaybeClose` idempotently closes optional closeables, `HaltableRemoteIterator` stops when a checked predicate returns false, and `RangeExcludingLongIterator` emits `[start, excludedFinish)`.

State is per-iterator and not thread-safe. Dependencies include Hadoop `RemoteIterator`, IO statistics support, `IOUtils`, SLF4J, and checked-IO functional interfaces. Integration is extensive in S3A listing, committers, contract tests, directory performance tests, and `TaskPool` range/listing workflows. Risks include unchecked type casts, null-filter Boolean unboxing, auto-close side effects from `hasNext()`, source cleanup on `NoSuchElementException`, and consumers needing to understand that `foreach()` closes but simple manual iteration may not. `TestRemoteIterators` covers array/singleton/null/range iterators, mapping/filtering, stats passthrough, close passthrough, Java iterator/iterable support, halt behavior, and close during next-loop paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/RemoteIterators.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/RunnableRaisingIOE.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/RunnableRaisingIOE.java

`RunnableRaisingIOE` is a Java `Runnable` variant whose primary operation can throw `IOException`. It is useful when code should be passable to executor APIs while still being implemented in checked-IO form.

The abstract method is `apply()`. The inherited `run()` method is implemented as a default method: it invokes `apply()` and wraps any `IOException` in `UncheckedIOException`. Runtime exceptions from `apply()` pass through unchanged. There is no object state or persistence.

Dependencies are Java `IOException`, `UncheckedIOException`, and `Runnable`. It integrates with the package's broader checked-IO lambda strategy and is an executor-friendly counterpart to `InvocationRaisingIOE`. Risks are straightforward: executor/future callers see unchecked IO wrappers and must unwrap them if the original IO type matters; because it implements `Runnable`, lambdas may be target-typed differently than `InvocationRaisingIOE` in overloaded APIs. Test signals are indirect through the package's wrapping tests and any executor callers that observe `UncheckedIOException` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/RunnableRaisingIOE.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/TaskPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/TaskPool.java

`TaskPool` is a private unstable utility for applying checked tasks to iterable or `RemoteIterator` inputs, optionally in parallel through a caller-provided `Submitter`. It originated in S3A committer work and was generalized so remote listings can feed work incrementally without pre-materializing all entries.

`Task<I,E>` processes an item, `FailureTask<I,E>` handles per-item failures, `Submitter` abstracts task submission, and `Builder<I>` configures execution. Builder options include `executeWith()`, `onFailure()`, `stopOnFailure()`, exception suppression, revert and abort tasks, stop-on-revert/abort-failure flags, and sleep interval. `foreach()` overloads create builders from `Iterable`, `RemoteIterator`, or arrays.

Single-threaded execution loops through the iterator, records succeeded items and exceptions, runs `onFailure`, optionally breaks on failure, then in `finally` runs revert over successes and abort over remaining items if needed. Iterator `IOException` is never suppressible. Parallel execution submits one runnable per item, tracks successes/exceptions with concurrent queues and failure flags, aborts not-yet-started items when stop-on-failure is active, waits with a spin/sleep loop, then optionally submits revert tasks for successes. It captures the caller's `IOStatisticsContext` and sets/resets it in worker threads.

State is builder-local; parallel collections are concurrent but the builder itself is not reusable/thread-safe. Dependencies include Hadoop `RemoteIterator`, `IOStatisticsContext`, `RemoteIterators`, Java futures/queues/atomics, and SLF4J. Integration is strong in S3A committers, commit contexts, partitioned staging, and IO statistics tests. Risks include busy-waiting, all futures being queued before failure is known, interrupted waits cancelling futures without throwing, suppressed exception selection that only adds differently typed exceptions as suppressed, and complex revert/abort ordering. `TestTaskPool` covers simple invocation, suppressed/non-suppressed failures, fail-fast/fail-slow behavior, onFailure, abort, revert, and stop flags across thread-count variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/TaskPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/Tuples.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/Tuples.java

`Tuples` provides a tiny public tuple facility without adding a third-party tuple dependency. The exposed API is `pair(K, V)`, returning a `Map.Entry<K, V>`.

The returned implementation is private immutable `Tuple<K,V>`. It stores final `key` and `value`, returns them through `getKey()` and `getValue()`, rejects mutation through `setValue()` with `UnsupportedOperationException`, formats as `(key, value)`, and implements value equality/hash code using `Objects.equals()` and `Objects.hash()`. There is no mutable state, persistence, synchronization, or external resource behavior.

Dependencies are Java `Map.Entry`, `Objects`, and Hadoop `InterfaceStability.Unstable`. Integration is as a lightweight API return/container type where callers need a pair without coupling Hadoop APIs to external libraries or newer Java tuple-like constructs. Risks are mostly API expectations: because it is returned as `Map.Entry`, some callers may expect `setValue()` to work; equality requires the same private `Tuple` class rather than accepting arbitrary `Map.Entry` implementations, so equality is not fully interface-polymorphic. Test signals are likely indirect through users of `pair()`; this file has no dedicated test surfaced in the scanned subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/Tuples.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/package-info.java

This package descriptor defines `org.apache.hadoop.util.functional` as public but unstable support for functional programming inside Hadoop APIs. Its central rationale is Java's checked exception mismatch: standard `java.util.function` types cannot throw checked `IOException`, while most Hadoop filesystem APIs can.

There is no executable code or stored state. The documentation highlights two design pillars. First, the package provides checked-IO functional interfaces and adapters so IO failures can be preserved or deliberately wrapped. Second, `RemoteIterators` go beyond Java iterators by supporting `Closeable` and `IOStatisticsSource`, allowing wrapper chains to expose inner iterator statistics and encourage cleanup.

Dependencies are Hadoop audience/stability annotations and documentation references to `RemoteIterators` and filesystem statistics. Integration spans the rest of the package plus S3A, wrapped IO, contract tests, and committers. The package-level risk is stability: it is public but explicitly unstable, so downstream users should expect API evolution. Another risk is mixed checked/unchecked exception boundaries; utilities make the boundary explicit, but callers must choose correctly. Test signals are broad: `TestFunctionalIO`, `TestRemoteIterators`, `TestTaskPool`, `TestLazyReferences`, and `TestFutureIO` exercise the package's documented themes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/hash/Hash.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/hash/Hash.java

`Hash` is the abstract common API and factory for Hadoop's non-cryptographic 32-bit hash implementations. It is private, unstable, and used where Hadoop needs configurable hash functions for data structures such as bloom filters.

The public constants are `INVALID_HASH`, `JENKINS_HASH`, and `MURMUR_HASH`. `parseHashType(String)` maps case-insensitive names `"jenkins"` and `"murmur"` to constants, otherwise returning invalid. `getHashType(Configuration)` reads `hadoop.util.hash.type` via `CommonConfigurationKeysPublic` defaulting to the configured default. `getInstance(int)` returns singleton `JenkinsHash` or `MurmurHash`, or null for invalid input. `getInstance(Configuration)` composes config parsing and factory lookup. Instance convenience overloads hash a full byte array with seed `-1` or a supplied seed; subclasses implement `hash(byte[], int length, int initval)`.

There is no mutable state in `Hash` itself. Dependencies include Hadoop `Configuration`, common configuration keys, and classification annotations. Integration is visible in `org.apache.hadoop.util.bloom.HashFunction`, which stores a configured `Hash` instance and applies it repeatedly. Risks include `getInstance()` returning null for invalid values, callers needing to validate byte-array length bounds, and the hashes being unsuitable for cryptographic/security use. `TestHash` covers parsing, configuration defaults, singleton factories, invalid handling, and deterministic repeated output for both implementations and seeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/hash/Hash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/hash/JenkinsHash.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/hash/JenkinsHash.java

`JenkinsHash` implements Bob Jenkins' lookup3/hashlittle-style 32-bit non-cryptographic hash for hash table lookup. It extends `Hash`, exposes a singleton through `getInstance()`, and also has a `main()` utility that hashes a file incrementally from 512-byte chunks.

The main `hash(byte[] key, int nbytes, int initval)` treats Java signed bytes and ints as unsigned using long masks. It initializes `a`, `b`, and `c` with `0xdeadbeef + length + seed`, processes 12-byte blocks into little-endian words, applies the lookup3 mix sequence, then handles the 0-12 byte tail with intentional switch fallthrough. If length is zero after block processing, it returns `c`; otherwise it applies final avalanche-style mixing and returns the low 32 bits as an `int`. `rot()` uses `Integer.rotateLeft()` masked to 32 bits.

Persistent state is only the static singleton; the hash calculation itself is local and thread-safe. Dependencies are Java file IO for `main()` and Hadoop annotations. Integration is through `Hash.getInstance()` and bloom/hash utilities. Risks include lack of input bounds checks for `nbytes`, non-cryptographic collision properties, intentional switch fallthrough that must not be “fixed,” and `Math.abs(value)` in the command-line utility still being negative for `Integer.MIN_VALUE`. `TestHash` validates factory selection and deterministic output across repeated evaluations and seeds, but does not lock known golden hash values or boundary lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/hash/JenkinsHash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/hash/MurmurHash.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/hash/MurmurHash.java

`MurmurHash` implements a Java port of MurmurHash 2.0, a fast non-cryptographic 32-bit hash suitable for general hash-based lookup. It extends `Hash` and exposes a singleton through `getInstance()`.

`hash(byte[] data, int length, int seed)` delegates to `hash(data, 0, length, seed)`. The offset overload initializes `h` as `seed ^ length`, processes four-byte little-endian chunks with Murmur's multiply/xor/multiply mix (`m = 0x5bd1e995`, `r = 24`), handles one to three trailing bytes without modulo, multiplies once more for tails, and finishes with two xor-shift/multiply avalanche steps. All arithmetic uses Java int overflow intentionally.

State is only the static singleton; hash execution is local and thread-safe. Dependencies are minimal: Hadoop annotations and the `Hash` base class. Integration is via `Hash.getInstance()` and configuration defaulting; `TestHash` shows Murmur is the default hash type for an empty configuration in this source tree. Risks include no offset/length bounds validation, signed-byte handling in the tail path where bytes are cast directly before shifting, and non-cryptographic collision/security limitations. Test coverage verifies parsing/factory behavior and deterministic repeated output for default and seeded calls, but does not compare against external Murmur2 golden vectors or offset-specific cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/hash/MurmurHash.java -->
