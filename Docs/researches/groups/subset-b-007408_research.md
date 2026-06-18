# subset-b-007408 research

Grouped source-tree-aligned research for Hadoop `org.apache.hadoop.util` test files. Each section is delimited for deterministic splitting into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestHttpExceptionUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestHttpExceptionUtils.java

Purpose: JUnit coverage for `HttpExceptionUtils`, the helper that serializes server-side exceptions into HTTP/Jersey JSON responses and reconstructs/normalizes failed HTTP client responses.

Important APIs and types: tests call `createServletExceptionResponse(HttpServletResponse,int,Exception)`, `createJerseyExceptionResponse(Response.Status,Exception)`, and `validateResponse(HttpURLConnection,int)`. They assert the JSON envelope fields `ERROR_JSON`, `ERROR_CLASSNAME_JSON`, `ERROR_EXCEPTION_JSON`, and `ERROR_MESSAGE_JSON`, and use Jackson `ObjectMapper`, Jersey `Response`, servlet response mocks, and `LambdaTestUtils`.

Control flow: the servlet test writes to a mocked response writer, verifies status/content type, and parses JSON. The Jersey test inspects status, metadata, and entity map. Validation tests cover expected status passthrough, no error stream, non-JSON error stream, known exception class reconstruction, unknown exception fallback, and class names that are not exceptions.

State and persistence: no persistent state; state is in mock responses, byte-array streams, and JSON maps. The stream position matters because `validateResponse` consumes the error stream once.

Dependencies and integration points: integrates HTTP status handling, Jackson parsing, Jersey media types, servlet writers, reflection-based exception loading, and Hadoop test intercept utilities.

Risks: regressions may leak raw parser errors, lose the original remote exception class/message, throw non-IOException types unexpectedly, or fail when the remote class is absent/non-Throwable. Test signals are precise exception type/message assertions and response metadata verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestHttpExceptionUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIdentityHashStore.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIdentityHashStore.java

Purpose: verifies `IdentityHashStore`, a small identity-keyed multimap-like store that uses object identity rather than `equals()` or `hashCode()` for keys.

Important APIs and types: `IdentityHashStore<K,V>`, `put`, `get`, `remove`, `visitAll`, `isEmpty`, `numElements`, `capacity`, and `IdentityHashStore.Visitor`. The nested `Key` deliberately throws from `hashCode()` and implements value equality to prove that neither Java hash nor equality is used.

Control flow: tests start with zero and nonzero initial capacity, visit empty stores, insert values, look them up by the same object, attempt lookup with a value-equal but distinct key, insert duplicate entries for the same identity key, remove each duplicate, and bulk insert/remove 1000 unique keys.

State and persistence: all state is in-memory open-addressed identity storage. Capacity grows from zero on demand; after 1000 additions/removals the test expects capacity 1024, so resizing behavior is part of the contract.

Dependencies and integration points: depends only on Hadoop's store class, JUnit assertions, timeouts, and SLF4J debug logging.

Risks: replacing identity comparison with `equals`, collapsing duplicate identity-key inserts, invoking user `hashCode`, or mishandling tombstones/resize would break core assumptions. Test signals include `assertNull` for equal-but-distinct key lookup, visitor checks, empty-state checks, and final capacity assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIdentityHashStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIndexedSort.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIndexedSort.java

Purpose: exercises Hadoop `IndexedSorter` implementations (`QuickSort` and `HeapSort`) over integer and Hadoop `Writable`-encoded records.

Important APIs and types: `IndexedSorter.sort`, `IndexedSortable.compare/swap`, `QuickSort`, `HeapSort`, `WritableComparator`, `Text`, `DataOutputBuffer`, and `DataInputBuffer`. Helper sortables include `SampleSortable`, `MeasuredSortable`, and `WritableSortable`.

Control flow: common helpers run random, single-record, sequential, already sorted, all-equal, and writable-string sort cases. `testQuickSort` also constructs a median-of-three degenerate pattern and wraps it in `MeasuredSortable` to assert comparison count stays below an expected worst-case bound. `testHeapSort` runs the common battery without the quicksort-specific degeneration check.

State and persistence: sort state is represented by index arrays rather than moving source values. Writable state is a packed byte buffer plus offsets; sorted output rehydrates `Text` instances after index swaps.

Dependencies and integration points: validates sorters used by Hadoop components that sort external record indexes without copying payloads. It also verifies compatibility with Hadoop's binary writable comparator semantics.

Risks: off-by-one ranges, unstable index indirection, bad comparator length calculations, quicksort degeneration, or swap mistakes can silently corrupt ordered streams. Test signals compare sorted projections with Java `Arrays.sort` baselines and fail fast on excessive comparisons/swaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIndexedSort.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestInstrumentedLock.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestInstrumentedLock.java

Purpose: validates `InstrumentedLock`, a wrapper around `Lock` that preserves mutual exclusion while logging long hold and wait times with suppression statistics.

Important APIs and types: `InstrumentedLock`, `AutoCloseableLock`, `Timer`, `SuppressedSnapshot`, `ReentrantLock`, `SubjectInheritingThread`, and overridden `logWarning`/`logWaitWarning` hooks.

Control flow: one test proves a competing thread cannot `tryLock` while the lock is held. Another wraps the lock in `AutoCloseableLock` and verifies try-with-resources acquisition/release updates thread-local ownership. Hold-time reporting uses a fake monotonic timer and mocked lock to trigger below-threshold, first warning, suppressed warning, and later warning-with-suppressed-count cases. Wait-time reporting uses a fair `ReentrantLock`, a blocking competitor, and timer advances to exercise the same suppression window.

State and persistence: lock ownership is transient; test-visible state is held in atomics recording warning count, suppressed count, max suppressed wait, and current owner thread.

Dependencies and integration points: integrates Java concurrency locks, Hadoop timer abstraction, logging throttling, and subject-inheriting test threads.

Risks: logging on every unlock, missing wait warnings, incorrect suppression counters, or broken try-with-resources release would create noisy or unsafe synchronization behavior. Test signals use timed JUnit tests, fake time, and competing threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestInstrumentedLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestInstrumentedReadWriteLock.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestInstrumentedReadWriteLock.java

Purpose: tests read/write variants of Hadoop instrumented locks, including exclusivity, shared-read behavior, warning throttling, and reentrant hold accounting.

Important APIs and types: `InstrumentedReadWriteLock`, `InstrumentedReadLock`, `InstrumentedWriteLock`, `AutoCloseableLock`, `ReentrantReadWriteLock`, `Timer`, and `SuppressedSnapshot`.

Control flow: `testWriteLock` holds a write lock and confirms neither competing writers nor readers can acquire. `testReadLock` proves concurrent readers can acquire while writers cannot. Separate hold-report tests use fake monotonic time to verify no warning below threshold, first warning above threshold, suppression inside the log gap, and later warning carrying the suppressed count. Reentrant tests acquire the same read or write lock three times and require only the outermost release to produce one warning with total held time.

State and persistence: no persisted state; relevant state is lock hold count, read/write ownership, fake clock value, and atomic warning counters.

Dependencies and integration points: ties Hadoop's instrumented wrappers to Java `ReentrantReadWriteLock`, try-with-resource adapters, and logging diagnostics used by services.

Risks: incorrectly treating nested reentrant releases as independent holds, allowing writers during reads, blocking concurrent reads, or losing suppression stats. Test signals include timed concurrency checks and exact warning-count/held-time assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestInstrumentedReadWriteLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIntrusiveCollection.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIntrusiveCollection.java

Purpose: behavior-driven tests for `IntrusiveCollection`, where list linkage is stored inside each element to reduce per-node allocation.

Important APIs and types: `IntrusiveCollection<T>`, `IntrusiveCollection.Element`, `add`, `remove`, `clear`, `contains`, `isEmpty`, and iteration. `SimpleElement` implements the intrusive callbacks and stores per-collection prev/next/membership maps.

Control flow: scenarios cover adding a single element, removing that element, clearing multiple elements, and iterating three inserted elements in insertion order. Each operation verifies collection membership through the public API rather than inspecting internal pointers directly.

State and persistence: state is in memory and split between the collection and each element's per-list linkage maps. The test model supports membership in multiple intrusive collections because maps are keyed by collection instance.

Dependencies and integration points: extends `HadoopTestBase` for assertion helpers and tests the element callback contract required by any production intrusive element.

Risks: stale element membership flags, broken prev/next updates, iterator order changes, or clear not invoking element cleanup would lead to memory retention or corrupted intrusive lists. Test signals are simple add/remove/clear/iteration assertions over concrete callback state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIntrusiveCollection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestJarFinder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestJarFinder.java

Purpose: verifies `JarFinder`, which locates the containing jar for a class or creates a jar from an expanded classpath directory.

Important APIs and types: `JarFinder.getJar`, `JarFinder.jarDir`, `GenericTestUtils.getTestDir`, `JarOutputStream`, `JarInputStream`, `Manifest`, and Java `Properties`.

Control flow: `testJar` asks for the jar containing `LoggerFactory`, expected to be classpath-provided. `testExpandedClasspath` asks for the test class itself and expects an on-the-fly jar. Manifest tests create temporary directories with and without `META-INF/MANIFEST.MF`, add a properties file, call `jarDir`, then reopen the byte-array jar and assert a manifest is present either way.

State and persistence: uses temporary filesystem directories under Hadoop's test dir and in-memory jar byte arrays. The helper `delete` recursively removes test directories with a path-length guard.

Dependencies and integration points: integrates classloader resource lookup, jar stream writing, manifests, and Hadoop test directory conventions.

Risks: missing manifests, unsafe recursive deletion, classpath directory packaging failures, or inability to locate dependency jars. Test signals are filesystem existence checks and `JarInputStream.getManifest()` assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestJarFinder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestJsonSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestJsonSerialization.java

Purpose: validates `JsonSerialization<T>`, Hadoop's Jackson-backed helper for object JSON round trips across strings, bytes, local files, and Hadoop `FileSystem` APIs.

Important APIs and types: `JsonSerialization<KeyVal>`, `toJson`, `fromJson`, `toBytes`, `fromBytes`, `fromInstance`, `save`, `load`, `FileSystem`, `LocalFileSystem`, `FileStatus`, `PathIOException`, and `LambdaTestUtils`.

Control flow: tests round-trip a serializable `KeyVal` bean through JSON string, UTF-8 bytes, clone-via-JSON, plain `File`, and `FileSystem` paths. Negative tests feed bad bytes, empty local files, empty `Path` loads with and without status, and deleted paths to verify exception mapping.

State and persistence: persisted state is temporary JSON files in local filesystem storage. The bean's equality and hash code are used as the oracle after deserialization.

Dependencies and integration points: covers Jackson parser behavior, Hadoop local filesystem status APIs, file create/delete semantics, and wrapped filesystem exception contracts.

Risks: empty-file handling differs between direct file and FS-status load paths, parser exceptions can be wrapped differently, and overwrite flags matter. Test signals are exact equality checks and intercepted `JsonParseException`, `EOFException`, `PathIOException`, and `FileNotFoundException` outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestJsonSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightCache.java

Purpose: randomized differential tests for `LightWeightCache`, a memory-conscious expiring cache backed by lightweight linked entries.

Important APIs and types: `LightWeightCache<K,E>`, `LightWeightCache.Entry`, `GSet`, `GSetByHashMap`, `FakeTimer`, `Time`, `put`, `get`, `contains`, `remove`, `clear`, `iterator`, `isExpired`, and entry expiration accessors.

Control flow: the main test runs combinations of table length, creation expiration, access expiration, data size, modulus, and size limit. `check` performs staged put, remove-and-put, remove, and repopulate cycles. `LightWeightCacheTestCase` mirrors cache operations into a non-evicting `GSetByHashMap`, advances fake time randomly, occasionally iterates the cache, and checks contains/get semantics against expired entries.

State and persistence: all state is in memory. Expiration state lives on each `IntEntry`; fake monotonic time controls eviction deterministically enough for assertions while random data exercises collision paths.

Dependencies and integration points: integrates Hadoop lightweight `GSet` contracts, fake timers, comparable entries, and randomized test data.

Risks: eviction can drop live entries, retain expired entries incorrectly, exceed size limits, corrupt linked buckets, or return stale replacements. Test signals include differential assertions against the reference map, cache size bounds, iterator/get consistency, and explicit zero-size checks after removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightGSet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightGSet.java

Purpose: verifies iterator removal behavior for `LightWeightGSet`, Hadoop's linked-element hash set.

Important APIs and types: `LightWeightGSet<K,E>`, `LightWeightGSet.LinkedElement`, `put`, `iterator`, `Iterator.remove`, and `size`. `TestElement` stores an integer value and the bucket-chain `next` pointer required by the collection.

Control flow: deterministic random input is inserted into a set of capacity 16. `testRemoveAllViaIterator` walks the iterator and removes every element, then expects size zero. `testRemoveSomeViaIterator` first sums all values, computes a threshold, removes elements above that threshold during iteration, then iterates again to verify all remaining values satisfy the predicate.

State and persistence: state is in-memory bucket chains and iterator cursor/removal state. No external persistence or global state is used.

Dependencies and integration points: tests the `LinkedElement` callback contract used by many Hadoop lightweight collections and caches.

Risks: iterator removal can skip elements, corrupt chain links, fail when removing bucket heads, or leave the size counter wrong. Test signals include complete removal to zero and predicate validation after selective removals under a timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightGSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightResizableGSet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightResizableGSet.java

Purpose: tests `LightWeightResizableGSet`, the resizable variant of Hadoop's lightweight linked-element set, under large insert/update/remove workloads.

Important APIs and types: `LightWeightResizableGSet<K,E>`, `LinkedElement`, `put`, `get`, `contains`, `remove`, `values`, `clear`, `iterator`, and random `TestKey`/`TestElement` helpers.

Control flow: `testBasicOperations` generates 65,536 unique long keys, inserts all elements, validates size and retrieval, creates replacement elements with the same keys and new data, inserts them as updates, verifies values changed without size growth, checks `values()`, and removes every key. `testRemoveAll` validates both `clear()` and iterator-based removal after repopulating the set.

State and persistence: all state is in-memory hash table capacity, linked bucket nodes, and element `next` pointers. Test data uniqueness is maintained by a `HashSet<Long>`.

Dependencies and integration points: uses AssertJ assertions and SLF4J logging; validates the collection contract relied on by memory-sensitive Hadoop structures.

Risks: resizing can lose entries, replacement can inflate size, `values()` can omit elements, iterator removal can corrupt buckets, and clear can leave stale linked nodes. Test signals cover large cardinality, key-equality lookup with separate key objects, and full removal checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightResizableGSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLimitInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLimitInputStream.java

Purpose: tests `LimitInputStream`, an `InputStream` wrapper that stops reads after a configured byte limit.

Important APIs and types: `LimitInputStream`, `InputStream.read()`, `read(byte[],int,int)`, `reset`, and a deterministic `RandomInputStream`.

Control flow: `testRead` verifies a zero limit returns EOF immediately and a positive limit delegates the first byte to the wrapped stream. `testResetWithoutMark` confirms reset without a mark raises `IOException`. `testReadBytes` reads four bytes and compares them to bytes generated from the same seeded random stream.

State and persistence: state is the remaining-byte counter and any mark/reset state inside the wrapper. No persistence is used.

Dependencies and integration points: extends `HadoopTestBase` for assertions and uses Java stream semantics.

Risks: off-by-one limit handling can allow extra bytes or premature EOF; byte-array reads can ignore limits; reset can incorrectly restore state without mark support. Test signals are EOF, exception, and deterministic byte equality checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLimitInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLineReader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLineReader.java

Purpose: validates `LineReader` custom delimiter handling, especially delimiter prefixes split across buffer boundaries or overlapping with input text.

Important APIs and types: `LineReader(InputStream, byte[] delimiter)`, `readLine(Text)`, Hadoop `Text`, byte-array streams, and UTF-8 encoding.

Control flow: the first test intends to place a delimiter-prefix-like token at a 64 KiB buffer edge and verify the next record includes unmatched prefix bytes rather than dropping them. The second test uses delimiter `record` with leading delimiters, adjacent delimiters, and EOF fragments like `ecordrecorcore` to check empty records and partial delimiter retention. The third test uses data `aaaabccc` with delimiter `aaab` to cover overlapping delimiter prefixes.

State and persistence: parser state is in-memory buffer position plus delimiter-match progress. No files are created.

Dependencies and integration points: covers Hadoop text input splitting semantics used by record readers with non-newline delimiters.

Risks: partial delimiter matches can lose bytes, create extra records, or hang at EOF. Buffer-boundary bugs are particularly likely for multi-byte delimiters. Test signals are exact `Text.toString()` assertions for every returned record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLineReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLists.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLists.java

Purpose: simple coverage for Hadoop `Lists` collection factory helpers and partitioning.

Important APIs and types: `Lists.newArrayList()`, `newLinkedList()`, varargs/iterable overloads, `newArrayListWithCapacity`, and `Lists.partition(List,int)`.

Control flow: tests create empty array and linked lists, add records, verify insertion order, build array/linked lists from varargs and `HashSet` iterables, partition a five-item list by sizes 2, 1, and 6, and verify partition counts and tail sizes. Capacity helper tests ensure a list with requested capacity behaves as a normal list after adding three entries.

State and persistence: all state is temporary Java collection contents.

Dependencies and integration points: wraps Java `ArrayList`, `LinkedList`, `HashSet`, and AssertJ/JUnit assertions. The partition helper mirrors Guava-style list partition behavior used by callers that batch work.

Risks: partition off-by-one errors, unexpected empty partitions, unsupported mutation behavior, or incorrect factory overload selection. Test signals are list sizes, element positions, and partition dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLists.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestMachineList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestMachineList.java

Purpose: verifies `MachineList`, which matches client machines against wildcard, IP, hostname, CIDR, and mixed allow-list expressions.

Important APIs and types: `MachineList`, `MachineList.InetAddressFactory`, `includes(String)`, `includes(InetAddress)`, `getCollection`, `StringUtils.getTrimmedStringCollection`, and Guava `InetAddresses` through Hadoop's shaded dependency.

Control flow: a fake address factory maps hostnames/IPs deterministically and can simulate unresolved names. Tests cover wildcard matching, raw IP lists with spaces/duplicates, static host collections, hostname reverse/IP matching, CIDR boundaries for /16 and /24 ranges, invalid CIDR rejection, mixed IP/CIDR lists, mixed hostname/IP/CIDR lists, null include arguments, and collection preservation.

State and persistence: all state is in-memory parsed list entries and fake DNS cache mappings. The factory makes PTR-style IP lookups deterministic.

Dependencies and integration points: exercises configuration-style allow-list parsing used by Hadoop services and host/IP security checks.

Risks: DNS resolution variability, CIDR boundary mistakes, duplicate handling, null input exceptions, and loss of original collection entries. Test signals are boundary include/exclude assertions, invalid CIDR exception handling, and collection-size/content checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestMachineList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeCodeLoader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeCodeLoader.java

Purpose: environment-gated verification that Hadoop native code loading is available when the test run explicitly requires it.

Important APIs and types: `NativeCodeLoader.isNativeCodeLoaded`, `getLibraryName`, `buildSupportsOpenssl`, `ZlibFactory.getLibraryName`, `OpensslCipher.getLibraryName`, and system property `require.test.libhadoop`.

Control flow: if `require.test.libhadoop` is absent or false, the test logs and returns. If required, it fails when libhadoop is not loaded, then asserts native Hadoop and zlib library names are non-empty and OpenSSL library name is available when the build reports OpenSSL support.

State and persistence: reads JVM system properties and native loader static state; no files are written.

Dependencies and integration points: validates native library integration for compression and crypto paths without making the whole suite require native artifacts by default.

Risks: CI environments differ in native library availability, names are platform-specific, and forcing the property can expose build/linker issues. Test signals are a conditional `fail` plus non-empty library-name assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeCodeLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeCrc32.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeCrc32.java

Purpose: parameterized tests for native CRC32/CRC32C chunk verification and calculation entry points.

Important APIs and types: `NativeCrc32`, `DataChecksum.Type.CRC32`, `DataChecksum.Type.CRC32C`, `DataChecksum.newDataChecksum`, direct and heap `ByteBuffer`, `ChecksumException`, and JUnit `@ParameterizedTest`.

Control flow: setup skips all cases unless native CRC is available, reads bytes-per-checksum from configuration, and creates a checksum object. Tests verify success and failure for direct-buffer verification, odd bytes-per-checksum verification, heap-array verification, direct/array calculation APIs, and deprecated `nativeVerifyChunkedSums`. Helpers fill data buffers with monotonic byte values and write either matching or deliberately shifted checksum ints.

State and persistence: state is per-test data and checksum buffers. `flip()` boundaries and buffer positions are part of the tested contract.

Dependencies and integration points: covers native code paths used by HDFS checksum verification with both CRC algorithms and both memory layouts.

Risks: native availability makes coverage conditional; direct-buffer offsets, odd-size chunk tails, checksum type IDs, and byte-array positions are common bug sites. Test signals are no-exception success cases and `ChecksumException` for invalid checksums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeCrc32.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeLibraryChecker.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeLibraryChecker.java

Purpose: tests the command-line `NativeLibraryChecker` utility without allowing it to terminate the JVM.

Important APIs and types: `NativeLibraryChecker.main`, `ExitUtil.disableSystemExit`, `ExitUtil.ExitException`, `ExitUtil.resetFirstExitException`, `NativeCodeLoader.isNativeCodeLoaded`, `Shell.WINDOWS`, and captured `System.out`.

Control flow: help (`-h`) should return normally; illegal argument combinations and unknown args should call exit. With no arguments, the utility returns only if native Hadoop is loaded, otherwise exits. Output tests run `-a` and no-arg modes, capture stdout, and assert platform-relevant lines such as `winutils: true` on Windows and `hadoop:  true` when native code is loaded.

State and persistence: mutates global `ExitUtil` state and temporarily replaces `System.out`; it restores output in `finally`.

Dependencies and integration points: validates admin-facing diagnostics for native Hadoop, zlib, OpenSSL, and Windows support.

Risks: global exit/out state can leak across tests if reset/restore is missed; output text is formatting-sensitive. Test signals are trapped `ExitException`s and substring checks in captured output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeLibraryChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestOptions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestOptions.java

Purpose: small tests for Hadoop `Options`, a helper for prepending command-line options and extracting typed option objects from varargs arrays.

Important APIs and types: `Options.prependOptions` and `Options.getOption(Class<T>, Object...)`.

Control flow: `testAppend` prepends two and three option strings to existing arrays and asserts exact resulting order. `testFind` scans a heterogenous object array and returns the first matching `Integer`, `String`, and `Boolean`.

State and persistence: no persistent state; arrays are local immutable test fixtures.

Dependencies and integration points: used by callers that layer default options before user options and pass typed optional parameters through object arrays.

Risks: order reversal, array allocation length mistakes, returning later values instead of first typed match, or primitive/wrapper confusion. Test signals are exact array equality and typed value equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPreconditions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPreconditions.java

Purpose: exhaustive message-formatting tests for Hadoop `Preconditions` null, argument, and state checks.

Important APIs and types: `checkNotNull`, `checkArgument`, `checkState`, default-message getters, string messages, format-string overloads, and `Supplier<String>` message overloads.

Control flow: success tests call each precondition with valid input while providing null suppliers, null messages, null format strings, null args, bad format specifiers, insufficient args, and supplier formatting failures to prove success paths do not eagerly evaluate or throw. Failure tests intercept `NullPointerException`, `IllegalArgumentException`, and `IllegalStateException`, checking explicit messages when formatting succeeds and default messages when formatting fails or suppliers are null/bad.

State and persistence: only a reusable `errorMessage` field; no external state.

Dependencies and integration points: protects a shared utility used widely across Hadoop from Guava-version drift and message-evaluation side effects.

Risks: eager supplier evaluation, leaking `IllegalFormatException`, null formatter crashes, wrong default message, or exception-type mismatch. Test signals are `LambdaTestUtils.intercept` assertions on type and message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPreconditions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestProgress.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestProgress.java

Purpose: verifies `Progress` clamps invalid or out-of-range progress values.

Important APIs and types: `Progress.set(float)` and `Progress.getProgress()`.

Control flow: the test sets `NaN`, negative infinity, and `-1` and expects reported progress `0`. It sets `1.1` and positive infinity and expects reported progress `1`.

State and persistence: state is the single in-memory progress float. No persistence or dependencies beyond JUnit.

Dependencies and integration points: progress values are surfaced by Hadoop task/reporting code, so normalization prevents invalid telemetry from propagating.

Risks: accepting NaN can poison downstream calculations; not clamping can render progress UI or scheduling math invalid. Test signals are exact floating-point equality with zero delta.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestProgress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestProtoUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestProtoUtil.java

Purpose: tests protobuf utility compatibility for raw varint decoding and RPC request header client IDs.

Important APIs and types: `ProtoUtil.readRawVarint32`, `ProtoUtil.makeRpcRequestHeader`, protobuf `CodedOutputStream`, `RpcRequestHeaderProto`, `RpcKind`, `OperationProto`, `RpcConstants.INVALID_RETRY_COUNT`, and `ClientId`.

Control flow: `testVarInt` encodes fixed positive/negative boundary values and bit-pattern sweeps using protobuf's own writer, then decodes with Hadoop's reader and expects the original int. `testRpcClientId` obtains a client UUID and asserts `makeRpcRequestHeader` preserves it byte-for-byte in the protobuf header.

State and persistence: in-memory byte arrays and protobuf objects only.

Dependencies and integration points: validates Hadoop IPC's protobuf framing and client identity propagation against the third-party protobuf implementation.

Risks: varint sign/overflow handling, stream termination mistakes, and client-ID truncation would break RPC compatibility. Test signals compare decoded ints and client-id bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestProtoUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPureJavaCrc32.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPureJavaCrc32.java

Purpose: verifies Hadoop's `PureJavaCrc32` matches `java.util.zip.CRC32` and carries benchmark/table-generation utilities for manual performance work.

Important APIs and types: `PureJavaCrc32`, `CRC32`, `Checksum`, single-byte and byte-array `update`, `reset`, `getValue`, nested `Table`, and nested `PerformanceTest`.

Control flow: `testCorrectness` compares initial/reset state, one-byte updates, fixed byte arrays, UTF-8 text, and 10,000 random byte arrays up to 2048 bytes. `checkOnBytes` verifies equality after every single-byte update, after bulk update, and after a partial slice when long enough. `Table` can generate CRC lookup tables from a polynomial. `PerformanceTest` compares throughput across sizes and thread counts while checking resulting CRC values match.

State and persistence: unit state is two checksum instances. Manual table generation can write `table8.txt`; benchmark state is local arrays/threads.

Dependencies and integration points: provides fallback checksum correctness for environments without native CRC acceleration.

Risks: slice handling, reset state, signed byte updates, or table constants can diverge from JDK CRC32. Test signals are repeated value equality against the JDK implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPureJavaCrc32.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPureJavaCrc32C.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPureJavaCrc32C.java

Purpose: validates initial/reset behavior for Hadoop's `PureJavaCrc32C` and includes a manual benchmark against JDK `CRC32C`.

Important APIs and types: `PureJavaCrc32C`, `CRC32C`, `Checksum`, nested `PerformanceTest`, reflection constructors, and `SubjectInheritingThread`.

Control flow: the active JUnit test creates a checksum, records its initial value, resets it, and verifies the reset value matches initialization. The nested benchmark generates random data up to 32 MiB, warms both implementations, measures multiple chunk sizes and thread counts, and checks the pure-Java checksum value equals the JDK baseline for every run.

State and persistence: no persisted state; benchmark state is local buffers and thread result arrays.

Dependencies and integration points: supports Hadoop's CRC32C fallback path where native CRC is unavailable and lets maintainers compare performance manually.

Risks: this unit file has minimal active correctness coverage beyond reset equivalence; arithmetic correctness is mainly guarded elsewhere. Test signals are the reset assertion and benchmark runtime value checks when manually executed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPureJavaCrc32C.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestReadWriteDiskValidator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestReadWriteDiskValidator.java

Purpose: tests `ReadWriteDiskValidator` and its metrics by exercising successful read/write checks and failure accounting.

Important APIs and types: `DiskValidatorFactory.getInstance`, `ReadWriteDiskValidator.checkStatus`, `ReadWriteDiskValidatorMetrics`, `DefaultMetricsSystem`, `MetricsCollectorImpl`, `MetricsRecords`, `DiskChecker.DiskErrorException`, and `Shell.getSetPermissionCommand`.

Control flow: the success test runs 100 checks against the test build directory, verifies read/write quantile estimator counts, fetches the metrics source, and asserts failure metrics are zero and latency metrics exist. The failure test creates a temp directory, chmods it to `000`, expects `DiskErrorException` twice, collects metrics after each failure, and verifies failure count increments and last-failure timestamp increases.

State and persistence: uses filesystem test directories and metrics-system singleton state. Permissions are mutated to simulate disk access failure.

Dependencies and integration points: validates Hadoop disk-health probing and metrics publication used by datanode/local storage health checks.

Risks: platform permissions can behave differently, metrics source names are path-derived, and global metrics state may retain prior registrations. Test signals are metric values, metric existence checks, and failure message assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestReadWriteDiskValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestReflectionUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestReflectionUtils.java

Purpose: tests `ReflectionUtils` constructor caching, cache clearing, thread safety, classloader leak resistance, inherited member discovery, thread-dump logging, and non-default constructor support.

Important APIs and types: `ReflectionUtils.newInstance`, `clearCache`, `getCacheSize`, `getDeclaredFieldsIncludingInherited`, `getDeclaredMethodsIncludingInherited`, `logThreadInfo`, `URLClassLoader`, and `GenericTestUtils.LogCapturer`.

Control flow: setup clears the cache. Cache tests instantiate several classes twice and verify cache size, then clear it. Thread-safety launches 32 threads doing the same construction. Negative construction checks a no-default-constructor class. Leak testing repeatedly loads a child class via fresh classloaders, instantiates it, forces GC, and expects cache size below iterations. Member tests use an anonymous subclass to require parent and child fields/methods. Other tests capture thread dump logs and validate non-default constructor argument validation.

State and persistence: state is global reflection constructor cache and captured logs. Child classloaders are intentionally made collectible.

Dependencies and integration points: foundational for configuration-driven instantiation across Hadoop.

Risks: cache synchronization bugs, classloader leaks, poor diagnostics, and confusing constructor argument errors. Test signals include cache size, multithread failure capture, log substring, and exact exception text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestReflectionUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestRunJar.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestRunJar.java

Purpose: tests `RunJar`, Hadoop's jar unpacking and application launching utility, including extraction filtering, timestamp preservation, client classloader behavior, and path traversal defense.

Important APIs and types: `RunJar.unJar`, `unJarAndSave`, `createWorkDirectory`, `run`, `MATCH_ANY`, `ApplicationClassLoader`, `JarFinder.makeClassLoaderTestJar`, Mockito spy/stubbing, `FileUtil`, and Java jar streams.

Control flow: setup creates a jar with two entries and fixed modification times. Tests unjar all entries, unjar by regex, generate a larger jar and verify `unJarAndSave` preserves saved jar length plus extracted file sizes, assert extracted modification times equal entry times, create/delete a work directory, run a generated classloader test jar with client classloader enabled, verify optional skip-unjar avoids unpacking, and create a malicious `../outside.path` entry that must fail for both file and stream unjar APIs.

State and persistence: extensive temporary filesystem and jar state under a per-test root, cleaned in `tearDown`.

Dependencies and integration points: covers job jar handling, classloader isolation, and archive security for Hadoop launch paths.

Risks: zip-slip path traversal, lost timestamps, partial extraction, classloader parent/child mistakes, and temporary directory leaks. Test signals are file existence/absence, size/timestamp equality, Mockito call counts, and exception message checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestRunJar.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestShell.java

Purpose: broad tests for Hadoop `Shell`, including interval throttling, command execution formatting/timeouts/env handling, process control commands, Hadoop home/winutils resolution, bash quoting, process cleanup, Java version checks, and bash availability.

Important APIs and types: `Shell`, `ShellCommandExecutor`, `getCheckProcessIsAliveCommand`, `getSignalKillCommand`, `checkHadoopHomeInner`, `getQualifiedBinInner`, `getWinUtilsFile`, `getWinUtilsPath`, `bashQuote`, `destroyAllShellProcesses`, and platform constants.

Control flow: a nested command counts executions to test intervals. Other tests inspect command `toString`, run a timed-out shell script, compare inherited/non-inherited env maps, detect timer-thread leaks after timed-out commands, construct platform-specific process liveness/kill commands, validate many Hadoop home and winutils error cases via temp files/dirs, assert Unix winutils failures, quote strings with embedded quotes, start two sleep processes then destroy all shell processes, check Java version >= 8, and assume bash support.

State and persistence: uses temp directories/files, process handles, global platform/static shell state, and thread snapshots.

Dependencies and integration points: shell execution underpins Hadoop native commands, permission operations, Windows utilities, and service process cleanup.

Risks: platform-specific assumptions, lingering processes/timer threads, bad env isolation, command injection through quoting, and fragile path validation. Test signals include timeout flags, exact command arrays, exception text substrings, thread counts, and process termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestShutdownHookManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestShutdownHookManager.java

Purpose: validates `ShutdownHookManager` registration, priority ordering, duplicate handling, timeout execution, configuration parsing, and removal/clear behavior.

Important APIs and types: `ShutdownHookManager`, `HookEntry`, `addShutdownHook`, `removeShutdownHook`, `hasShutdownHook`, `getShutdownHooksInOrder`, `executeShutdown`, `clearShutdownHooks`, `getShutdownTimeout`, `Configuration`, and `SERVICE_SHUTDOWN_TIMEOUT`.

Control flow: the main test registers hooks with different priorities and timeouts, verifies ordering/default timeout, removes one long hook to avoid slow execution, runs `executeShutdown`, expects one timeout, checks every remaining hook was invoked, asserts the timed-out hook did not complete and did not block later hooks for its full sleep, then clears all hooks. Other tests cover configured shutdown timeout, too-low timeout clamping to `TIMEOUT_MINIMUM`, ignored duplicate registration preserving original priority/timeout, and removal failures/success.

State and persistence: manager state is isolated by constructing a new instance. Hook state tracks invocation order, start time, completion, interruption, and assertion errors.

Dependencies and integration points: service shutdown ordering and bounded hook execution across Hadoop daemons.

Risks: duplicate hooks changing priority, long hooks blocking shutdown, bad timeout units, and shared global hook state in tests. Test signals are ordered hook lists, timeout count, timing comparisons, and hook state assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestShutdownHookManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestShutdownThreadsHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestShutdownThreadsHelper.java

Purpose: tests helper methods that interrupt/shutdown threads and executor services within bounded wait periods.

Important APIs and types: `ShutdownThreadsHelper.shutdownThread`, `shutdownExecutorService`, `SHUTDOWN_WAIT_MS`, `SubjectInheritingThread`, and `ScheduledThreadPoolExecutor`.

Control flow: a sample runnable sleeps for twice the helper wait and prints when interrupted. `testShutdownThread` starts a thread, calls shutdown helper, and verifies the returned boolean matches actual liveness and that the thread is terminated. `testShutdownThreadPool` submits the same runnable to a scheduled executor, calls shutdown helper, and verifies return value matches `isTerminated`.

State and persistence: transient thread/executor lifecycle state only.

Dependencies and integration points: service shutdown utilities used by Hadoop components to stop background workers reliably.

Risks: helpers can return success before termination, fail to interrupt sleepers, or leave executor pools alive. Test signals are boolean/termination equality and final termination assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestShutdownThreadsHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSignalLogger.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSignalLogger.java

Purpose: verifies Unix-only registration semantics for `SignalLogger`.

Important APIs and types: `SignalLogger.INSTANCE.register(Logger)`, SLF4J `Logger`, Apache Commons `SystemUtils.IS_OS_UNIX`, and JUnit assumptions.

Control flow: the test runs only on Unix. It registers the singleton signal logger once, then attempts a second registration and expects `IllegalStateException`.

State and persistence: mutates singleton signal-handler registration state for the JVM process. No files are involved.

Dependencies and integration points: integrates JVM signal handling with Hadoop logging for diagnostics on Unix platforms.

Risks: global singleton state means test ordering can matter if another test registers signals first; non-Unix platforms skip coverage. Test signals are assumption gating and the double-registration exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSignalLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStopWatch.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStopWatch.java

Purpose: tests `StopWatch`, a closeable timing helper with explicit running-state transitions.

Important APIs and types: `StopWatch.start`, `stop`, `reset`, `isRunning`, and `AutoCloseable.close` through try-with-resources.

Control flow: `testStartAndStop` verifies a new watch is not running, becomes running after `start`, and stops after `stop`. `testStopInTryWithResource` creates a watch in try-with-resources and expects no exception on close without start. `testExceptions` verifies stopping before start and starting twice both throw `IllegalStateException`.

State and persistence: state is in-memory start/running fields. No external dependencies beyond JUnit.

Dependencies and integration points: utility is used by code paths that need scoped duration measurement.

Risks: invalid state transitions can hide timing bugs or throw in cleanup blocks. Test signals are running-state assertions and caught exception-type checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStopWatch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStringInterner.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStringInterner.java

Purpose: tests strong and weak string interning helpers in `StringInterner`.

Important APIs and types: `StringInterner.strongIntern`, `StringInterner.weakIntern`, Java string literals, substrings, and heap-created strings.

Control flow: `testNoIntern` proves three equal strings are distinct references before interning. `testStrongIntern` interns literal, substring, and heap string and expects all returned references to be the same. `testWeakIntern` repeats the same identity assertion for the weak interner.

State and persistence: strong and weak interners keep process-local caches; weak cache entries may be GC-sensitive, but this test holds strong references during assertions.

Dependencies and integration points: interning reduces memory use and enables identity sharing for common Hadoop strings.

Risks: returning distinct instances breaks memory-sharing assumptions; weak interner implementation must still canonicalize while entries are live. Test signals are `assertNotSame` before interning and `assertSame` after each interning mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStringInterner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStringUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStringUtils.java

Purpose: broad coverage for `StringUtils` parsing, escaping, formatting, locale-stable case conversion, token replacement, collection splitting, time formatting, stack trace capture, and concurrency-sensitive date formatting.

Important APIs and types: `escapeString`, `split`, `unEscapeString`, `TraditionalBinaryPrefix.string2long/long2String`, `byteDesc`, `formatPercent`, `join`, `getTrimmedStrings`, `camelize`, `stringToURI`, `simpleHostname`, token patterns, `getTrimmedStringCollection`, `toLowerCase`, `toUpperCase`, `equalsIgnoreCase`, `getFormattedTimeWithDiff`, `formatTimeSortable`, `isAlpha`, `escapeHTML`, `createStartupShutdownMessage`, `getTrimmedStringCollectionSplitByEquals`, and `getStackTrace`.

Control flow: tests cover null/empty/special-character escaping, comma splitting with escapes, simple char splitting, invalid unescape input, binary prefix parsing/overflow/error messages and formatting around powers of two, percent/byte formatting, joins, trimmed string arrays, camelize including ASCII under locale concerns, bad URI conversion, hostname simplification, shell/Windows token replacement, unique trimmed collections, Turkish-locale case conversion, multithreaded formatted-time consistency through a barrier, sortable time cap output, alpha/HTML/startup message helpers, split-by-equals success and failure cases, and stack trace line counts.

State and persistence: mostly stateless; temporarily changes default JVM locale and uses a fixed `FastDateFormat` concurrently.

Dependencies and integration points: string helpers feed configuration parsing, logging, UI text, resource sizes, env substitution, and diagnostics.

Risks: locale bugs, escaping reversibility failures, overflow handling, race conditions in date formatting, invalid key-value parsing, and format regressions. Test signals are exact string/array/map assertions and intercepted invalid-argument failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStringUtils.java -->
