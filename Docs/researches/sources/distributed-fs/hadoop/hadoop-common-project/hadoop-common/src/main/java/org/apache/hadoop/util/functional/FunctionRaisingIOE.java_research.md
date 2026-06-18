# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/FunctionRaisingIOE.java

`FunctionRaisingIOE<T, R>` is the one-argument checked-IO counterpart to `java.util.function.Function`. It is central to this utility package because mapping and filtering remote filesystem iterators often need to throw `IOException`.

The abstract `apply(T)` returns `R` or throws `IOException`. The default `unchecked(T)` wraps only `IOException` in `UncheckedIOException` and otherwise preserves runtime failures. No state is held. Dependencies are Java IO exception classes.

Integration is concrete: `RemoteIterators.mappingRemoteIterator()` uses it to transform each source value, `filteringRemoteIterator()` uses `FunctionRaisingIOE<? super S, Boolean>` as its predicate, and `FunctionalIO.toUncheckedFunction()` adapts it to a standard Java `Function`. This lets code keep checked exceptions while inside Hadoop APIs and convert only at boundaries that require unchecked functions. Risks include nullable Boolean results in filters causing unboxing failures, wrapped IO failures being easy to mishandle in stream APIs, and lambda overload ambiguity with other package interfaces. Test signals include `TestFunctionalIO.testUncheckedFunction()` and `TestRemoteIterators` mapping/filtering cases.
