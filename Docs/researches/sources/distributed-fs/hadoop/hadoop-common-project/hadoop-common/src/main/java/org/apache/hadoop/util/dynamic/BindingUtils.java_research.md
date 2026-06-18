# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/BindingUtils.java

Purpose: `BindingUtils` helps Hadoop code bind optional APIs through reflection while preserving clear availability checks and IOException unwrapping.

Important APIs/types/functions: `loadClass`, `loadClassSafely`, and `loadClass(ClassLoader,String)` resolve classes. `loadInvocation` builds a `DynMethods.UnboundMethod` or no-op method for optional instance/static invocation. `loadStaticMethod` requires the resolved method to be static. `noop`, `implemented`, `checkAvailable`, and `available` inspect method bindings. `extractIOEs(Supplier<T>)` unwraps `UncheckedIOException` into checked `IOException`.

Control flow: class loading catches `ClassNotFoundException` and returns null except for `loadClassSafely`, which wraps it in `RuntimeException`. Method loading uses `DynMethods.Builder(...).impl(...).orNoop().build()`, logs found/missing at debug, and returns a no-op when source class is absent. Static loading verifies `method.isStatic()` with `checkState`. `implemented` returns false on the first no-op.

State and persistence behavior: stateless utility class with static logger.

Dependencies and integration points: depends on `DynMethods` in the same dynamic package, SLF4J, Hadoop `Preconditions.checkState`, and Java `UncheckedIOException`. It supports compatibility layers that must run across multiple Hadoop/API versions.

Risks: missing optional methods become no-ops unless callers explicitly call `checkAvailable`, which can hide integration gaps. `loadStaticMethod` calls `isStatic` even for no-op methods; behavior depends on `DynMethods` no-op implementation. `extractIOEs` only unwraps `UncheckedIOException`, not other runtime wrappers.

Test signals: tests should cover absent classes, absent methods returning no-ops, static/non-static enforcement, `implemented` with mixed methods, `checkAvailable` failures, and IOException extraction.
