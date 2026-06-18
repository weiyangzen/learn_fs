# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/bloom/TestBloomFilters.java

Purpose: Concrete unit tests for Hadoop bloom-filter implementations. It combines the shared `BloomFilterCommonTester` with implementation-specific checks for dynamic, counting, retouched, large-vector, and bitwise-not behavior.

Important APIs/types/functions: Fields set `numInsertions = 1000`, `bitSize = optimalNumOfBits(..., 0.03)`, and `hashFunctionNumber = 5`. `FALSE_POSITIVE_UNDER_1000` maps Jenkins and Murmur hash ids to false-positive `Key` collections. Tests include `testDynamicBloomFilter()`, `testCountingBloomFilter()`, `testRetouchedBloomFilterSpecific()`, `testFiltersWithJenkinsHash()`, `testFiltersWithMurmurHash()`, `testFiltersWithLargeVectorSize()`, and `testNot()`.

Control flow: Common tests instantiate filters and request strategy sets from the harness. Counting-filter-specific flow adds the same key twice, checks approximate count increments/decrements through `delete()`, and validates membership clearing after both deletes. Retouched-filter flow iterates both hash algorithms and odd/even inserted populations, records known false positives, then calls `selectiveClearing()` for `MAXIMUM_FP`, `MINIMUM_FN`, and `RATIO` schemes.

State and persistence behavior: Filters are mutated in memory and, through the shared harness, serialized/deserialized via Writable buffers. `testNot()` directly sets the package-visible `bits` field on a small `BloomFilter` to a known `BitSet`, clones it, calls `not()`, and asserts no intersection with the original bits.

Dependencies and integration points: Depends on all Hadoop bloom implementations, `Key`, `RemoveScheme`, `Hash`, Guava-shaded immutable collections, `BitSet`, and JUnit. It exercises the filter API consumed by Hadoop data structures and probabilistic membership callers.

Risks: Known false-positive expectations are algorithm- and bit-size-specific. The large-vector test creates a `BloomFilter(Integer.MAX_VALUE, ...)`, so memory-efficient serialization/read behavior is important; changes to eager bit allocation could make it impractical. `testNot()` touches implementation detail `bits`, coupling the test to field visibility and representation.

Test signals: Membership and approximate-count changes, strategy harness pass/fail across hash algorithms, retouched selective-clearing absence checks, large vector write/read success, and zero intersection after bitwise not are the primary signals.
