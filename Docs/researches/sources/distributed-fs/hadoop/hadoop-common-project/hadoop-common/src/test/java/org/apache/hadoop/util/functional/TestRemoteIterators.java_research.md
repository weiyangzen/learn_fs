# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestRemoteIterators.java

Purpose: Tests `RemoteIterators` adapters and combinators for Hadoop `RemoteIterator`. It validates array/singleton/range/iterator/iterable adapters, mapping, filtering, foreach iteration, close passthrough, halt predicates, and IOStatistics propagation.

Important APIs/types/functions: Static helpers under test include `remoteIteratorFromArray()`, `remoteIteratorFromSingleton()`, `mappingRemoteIterator()`, `filteringRemoteIterator()`, `remoteIteratorFromIterator()`, `remoteIteratorFromIterable()`, `closingRemoteIterator()`, `haltableRemoteIterator()`, `rangeExcludingIterator()`, `foreach()`, and statistics extraction. Local fixtures include `CloseCounter`, `IOStatsInstance`, `CountdownRemoteIterator`, `CountdownIterator`, and `CountdownIterable`.

Control flow: Tests iterate through adapters with `verifyInvoked()`, which calls `foreach()` and asserts count. Mapping increments a counter while preserving values; filtering accepts even numbers, none, or all. Close tests verify `foreach()` closes closeable iterators once and explicit close is idempotent. Iterable close tests wrap an iterable so exhaustion in `hasNext()` or `next()` closes the source and prevents later iterator creation. Haltable tests stop before source exhaustion when a predicate flips false. Range tests verify empty and 100-element ranges plus `NoSuchElementException` on exhausted `next()`.

State and persistence behavior: Counters track consumer invocations and close counts. Countdown fixtures mutate their limit during iteration. `CountdownIterable` refuses new iterators after close by checking close count. IO statistics are exposed through `IOStatisticsSource` fixtures and wrappers.

Dependencies and integration points: Depends on Hadoop `RemoteIterator`, IO statistics APIs, functional iterator helpers, AssertJ, SLF4J, JUnit, and Hadoop test interception helpers. These adapters are used when filesystem listings and other remote scans need functional transformations while preserving IO semantics.

Risks: Close semantics are subtle: singleton close should not close the singleton value, while mapping/closing wrappers must close the source exactly once. Filtering must handle internal lookahead without skipping or double-consuming. The tests do not simulate `IOException` from `hasNext()`/`next()` except through API signatures.

Test signals: Iteration counts, counter values, close-count assertions, `toString()` content, IO statistics extraction success, halt-at-limit behavior, and exhausted range exceptions are the meaningful signals.
