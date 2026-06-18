# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/bloom/BloomFilterCommonTester.java

Purpose: Reusable strategy harness for Hadoop bloom-filter tests. It parameterizes filter implementations, hash type, insertion count, expected false positives, and common behavioral checks across `BloomFilter`, `CountingBloomFilter`, `RetouchedBloomFilter`, and `DynamicBloomFilter`.

Important APIs/types/functions: `optimalNumOfBits(int, double)` calculates bit-vector size from expected insertions and false-positive probability. Fluent methods `of()`, `withFilterInstance()`, and `withTestCases()` build a tester. `test()` runs each `BloomFilterTestStrategy`, recreating a symmetric fresh filter after each strategy. `getSymmetricFilter()` maps filter classes to constructors. The enum strategies cover add overloads, `Key` equality/weight/serialization, exception contracts, odd/even membership false positives, write/read serialization, XOR, AND, and OR.

Control flow: The tester builds immutable filter and strategy sets, obtains known false positives for Jenkins or Murmur hashes under 1000 insertions, then applies each strategy. Strategies mutate their filter, assert membership or exceptions, and rely on `getSymmetricFilter()` to reset state before the next strategy. Read/write tests serialize to `DataOutputBuffer`, reset a `DataInputBuffer`, and read into a fresh filter.

State and persistence behavior: The harness carries `hashType`, `numInsertions`, filter builders, and known false-positive tables. Bloom-filter persistence is exercised through Hadoop Writable serialization, not disk files. Random slots in `WRITE_READ_STRATEGY` make exact elements non-deterministic, but only round-trip membership for written keys is asserted.

Dependencies and integration points: Depends on Hadoop bloom classes, Hadoop hash classes, Hadoop IO buffers, Guava-shaded immutable collections, JUnit assertions, and Log4J. It is the central integration point for repeated filter semantics in `TestBloomFilters`.

Risks: Expected false positives are hard-coded for specific algorithms and vector sizing; hash algorithm changes can legitimately alter these sets and break tests. `FILTER_AND_STRATEGY` computes an intersection range that effectively covers `100..900`, so any off-by-one in the helper changes membership expectations. Unsupported XOR is tolerated, making cross-filter feature coverage uneven.

Test signals: Passing shared strategies signal add overload compatibility, null/illegal argument handling, serialization stability, deterministic hash false positives, logical operations, and `Key` weight/equality behavior.
