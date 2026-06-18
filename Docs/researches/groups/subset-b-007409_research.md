# Research Report: subset-b-007409

Grouped research for Hadoop common utility tests and test protobuf schemas. Each source file section is delimited for deterministic reconciliation into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSysInfoLinux.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSysInfoLinux.java

Purpose: JUnit coverage for `SysInfoLinux`, using synthetic `/proc` files to verify Linux system-information parsing without depending on the host machine. The test exercises CPU topology, jiffy-based CPU usage, memory/swap accounting, network counters, and disk-sector counters.

Important APIs/types/functions: `FakeLinuxResourceCalculatorPlugin` extends `SysInfoLinux`, overrides `getCurrentTime()` and `readDiskBlockInformation()`, and exposes `advanceTime()` for deterministic CPU samples. Test methods include `parsingProcStatAndCpuFile()`, `parsingProcMemFile()`, `parsingProcMemFile2()`, `parsingProcMemFileWithBadValues()`, `testCoreCounts()`, `parsingProcNetFile()`, and `parsingProcDisksFile()`. Helper `updateStatFile()` rewrites fake `/proc/stat`; `writeFakeCPUInfoFile()` resets cached CPU-info parsing through `setReadCpuInfoFile(false)`.

Control flow: Static initialization creates randomized temp file names under `GenericTestUtils.getTestDir()` and one shared plugin configured with those paths and a fake jiffy length. Each test writes one fake proc file, then calls the public `SysInfoLinux` accessors that trigger parsing or refresh. CPU-usage tests first assert unavailable usage on the initial sample, then advance fake time and increase user jiffies to validate percentage and vcore calculations, including a one-jiffy interval that should not update cached usage.

State and persistence behavior: The shared plugin persists parser cache and fake time across method calls, while each test rewrites its target fake file. `deleteOnExit()` marks temp files for cleanup but does not isolate all static plugin state, so test methods deliberately reset CPU info where needed. Memory tests validate that huge pages and hardware-corrupted memory are deducted from total physical/virtual sizes, and that oversized unsigned-looking free-memory values are treated as zero.

Dependencies and integration points: Depends on Hadoop `SysInfoLinux`, `CpuTimeTracker`, `GenericTestUtils`, JUnit 5, Java `FileWriter`, and Linux `/proc` text formats. It is an integration-style parser contract for the resource calculator used by Hadoop services that report or enforce system resource capacity.

Risks: The fake formats encode specific kernel field ordering, so parser changes must preserve compatibility with both older `Inactive` and newer `Inactive(file)` memory fields. The static plugin may make tests order-sensitive if future cases mutate shared flags without resetting them. Disk tests force a non-default sector size, which is useful but assumes all selected disk rows should use the same overridden block size.

Test signals: Strong signals are exact assertions on processor count/frequency, core deduplication by physical/core id, CPU usage/vcore deltas, memory totals after deductions, network byte summation across non-loopback devices, and disk byte conversion from sector counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSysInfoLinux.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSysInfoWindows.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSysInfoWindows.java

Purpose: Tests `SysInfoWindows` parsing and refresh behavior using a mock subclass instead of invoking Windows shell commands. It validates the comma-separated `winutils`/shell system-info contract, cache refresh intervals, and CPU usage normalization for single-core and multi-core systems.

Important APIs/types/functions: `SysInfoWindowsMock` overrides `getSystemInfoInfoFromShell()` and `now()`, stores a mutable `infoStr`, and advances mock time through `advance(long)`. Test methods cover `parseSystemInfoString()`, `refreshAndCpuUsage()`, `refreshAndCpuUsageMulticore()`, and `errorInGetSystemInfo()`.

Control flow: Tests inject a CSV line with virtual memory, physical memory, available memory, processor/core count, CPU frequency, cumulative CPU time, storage bytes, and network bytes. Accessor calls trigger refresh if the mock clock exceeds `SysInfoWindows.REFRESH_INTERVAL_MS`; otherwise cached values are reused. CPU usage is unavailable until two valid samples exist, then computed from cumulative CPU-time deltas over elapsed wall time and normalized by core count for percentages.

State and persistence behavior: `SysInfoWindows` retains the last parsed metrics and last refresh timestamp, while the mock controls both the next shell output and clock. The no-refresh assertions verify that changed shell output does not leak into public values before the refresh interval. Bad/null shell output is intentionally tolerated without assertions on metric changes, indicating defensive parsing should not throw on malformed command output.

Dependencies and integration points: Depends on Hadoop `SysInfoWindows`, `CpuTimeTracker`, JUnit 5, and `@Timeout` to prevent hanging shell-like paths. It protects Hadoop resource reporting on Windows where values originate from native utilities.

Risks: The CSV positional ABI is fragile: adding/removing fields in the native command requires synchronized parser and tests. CPU calculations assume cumulative CPU time units are milliseconds and core count is the denominator for percentage only. The test does not assert exact fallback values after malformed output, so regressions that silently preserve stale metrics may need additional coverage.

Test signals: Exact parsed numeric values, first-sample unavailable CPU usage, unchanged cached memory before refresh, recalculated memory and CPU after advancing mock time, and absence of exceptions for null/empty shell output are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSysInfoWindows.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestTime.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestTime.java

Purpose: Minimal JUnit coverage for Hadoop `Time.formatTime(long)`. It asserts that the helper uses the same date/time rendering as the expected Java `SimpleDateFormat` pattern.

Important APIs/types/functions: The test owns a `ThreadLocal<SimpleDateFormat>` initialized with pattern `yyyy-MM-dd HH:mm:ss,SSSZ`. `testFormatTime()` obtains `Time.now()` and compares `Time.formatTime(time)` with the formatter output for the same millisecond timestamp.

Control flow: There is one direct assertion and no setup/teardown. The `ThreadLocal` avoids sharing a non-thread-safe `SimpleDateFormat` if the test runner executes tests in parallel or the helper is reused.

State and persistence behavior: No persistent state beyond the thread-local formatter. The result depends on the JVM default timezone and locale, but both sides of the assertion run in the same process, so the test checks formatting contract rather than a fixed UTC string.

Dependencies and integration points: Depends on Hadoop `Time`, Java text formatting, and JUnit 5. This guards log/timestamp presentation utilities used across Hadoop common code.

Risks: Because it compares against local default timezone behavior, it will not catch accidental changes that still match a formatter created with the same default environment. It also does not test monotonic time helpers or duration formatting.

Test signals: A passing assertion confirms the visible timestamp pattern and millisecond input handling remain consistent with the documented format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestTime.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestUTF8ByteArrayUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestUTF8ByteArrayUtils.java

Purpose: Unit tests for byte-level search helpers in `UTF8ByteArrayUtils`. Despite the class name, the tests focus on ASCII byte arrays and index/range behavior for single bytes, byte sequences, and nth-byte lookup.

Important APIs/types/functions: Tests call `findByte(byte[], int, int, byte)`, `findBytes(byte[], int, int, byte[])`, `findNthByte(byte[], int, int, byte, int)`, and the overload `findNthByte(byte[], byte, int)`. It extends `HadoopTestBase`, using its assertion conveniences.

Control flow: Each method builds `"Hello, world!"` as bytes and asserts both hit and miss results. Search ranges are varied to ensure `findBytes()` respects the start offset, while nth-byte tests verify second and third matches and return `-1` when the requested occurrence is absent.

State and persistence behavior: Stateless pure-function tests. No mutable global state, filesystem state, or encoding-sensitive persistence is involved beyond `String.getBytes()` using the platform default encoding for ASCII content.

Dependencies and integration points: Depends on Hadoop utility search functions and JUnit. These byte-search helpers are typically used by text parsers that operate on UTF-8 buffers without materializing strings.

Risks: Default charset use is harmless for ASCII literals but would be risky for non-ASCII UTF-8 cases; this test does not cover multibyte code points, empty patterns, negative offsets, or upper-bound edge cases. It also does not verify behavior when pattern length exceeds the search window.

Test signals: Expected hit indexes `4`, `1`, `3`, and `10`, plus `-1` misses, provide simple regression signals for range scanning and occurrence counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestUTF8ByteArrayUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestVersionUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestVersionUtil.java

Purpose: Compatibility tests for `VersionUtil.compareVersions()`, especially Maven-like comparable-version ordering. It verifies equality normalization, numeric ordering, qualifier ordering, alpha shorthand normalization, and snapshot-versus-release precedence.

Important APIs/types/functions: `testCompareVersions()` contains the matrix of equality and ordering assertions. Helper `assertExpectedValues(String lower, String higher)` asserts both forward negative and reverse positive comparisons.

Control flow: The test first asserts equal pairs such as `1`, `1.0`, and `1.0.0`, plus alpha spellings like `alpha-1`, `a1`, and `alpha1`. It then runs ordered pairs spanning numeric version increments, multi-digit numeric comparison, alphabetic suffixes, alpha/beta qualifiers, and `SNAPSHOT` versions.

State and persistence behavior: Stateless comparison contract with no external state. The comparison algorithm's parsed-token semantics are the implicit persistent compatibility surface because Hadoop components may gate features or compatibility based on version ordering.

Dependencies and integration points: Depends on Hadoop `VersionUtil` and JUnit. The comments explicitly align behavior with Maven `ComparableVersion`, which is relevant for dependency and Hadoop component version comparisons.

Risks: Version comparison is notoriously subtle; the test covers many common forms but not every Maven qualifier (`rc`, `milestone`, timestamped snapshots, build metadata). The alpha shorthand behavior is delicate: `1.a` is greater than `1.0`, while `1.a0`/`1a0` are treated as alpha-zero and lower than `1.0`.

Test signals: Symmetric lower/higher assertions and equality normalization protect against tokenization, numeric-vs-lexical comparison, and snapshot precedence regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestVersionUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestWeakReferenceMap.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestWeakReferenceMap.java

Purpose: Tests `WeakReferenceMap` and `WeakReferenceThreadMap` basic behavior without trying to force garbage collection. It validates explicit puts/removes, pruning of null weak-reference values, demand creation, lost-reference callbacks, and thread-id keyed convenience methods.

Important APIs/types/functions: `setup()` builds a `WeakReferenceMap<Integer, String>` from `factory()` and `referenceLost()`. Test methods cover `testBasicOperationsWithValidReferences()`, `testPruneNullEntries()`, `testDemandCreateEntries()`, `testFactoryReturningNull()`, and `testWeakReferenceThreadMapAssignment()`. Assertion helpers wrap `get()`, `containsKey()`, `size()`, `prune()`, and callback count checks.

Control flow: The tests insert entries, overwrite key `1`, remove and clear entries, then simulate collected weak references by explicitly storing `null`. A `get()` of absent or null-valued entries invokes the factory and optionally records a lost-reference callback. The thread-map test binds values to the current thread, verifies repeated set/remove behavior, forbids explicit null set, then simulates collection by putting null at the current thread id and requiring recreation.

State and persistence behavior: Each test gets a fresh map and lost-reference list via `@BeforeEach`. `WeakReferenceThreadMap` keeps values keyed by thread id and tracks factory/lost counters through `AtomicLong`. No GC-dependent timing is used, making the tests deterministic but limited to explicit null simulation.

Dependencies and integration points: Depends on Hadoop `WeakReferenceMap`, `WeakReferenceThreadMap`, `LambdaTestUtils.intercept`, AssertJ, and JUnit. These utilities support per-key or per-thread cached resources that should be recreated after weak references clear.

Risks: Not forcing GC means real weak-reference clearing races, reference-queue behavior, and concurrent access are not covered. The callback count contract is important: replacing a null reference via `get()` increments lost count, while normal demand creation does not.

Test signals: Map size/contains assertions, callback list size, null-factory `NullPointerException`, current-thread set/remove return values, and recreation counters are the meaningful regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestWeakReferenceMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestWinUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestWinUtils.java

Purpose: Windows-only integration tests for Hadoop's `winutils.exe` helper commands. The file validates filesystem permissions, ownership, symlinks/readlink behavior, group lookup, and Windows job/task creation through `Shell.execCommand()`.

Important APIs/types/functions: `setUp()` calls `assumeWindows()`, creates `TEST_DIR`, and resolves `Shell.getWinUtilsPath()`. Helpers include `requireWinutils()`, `writeFile()`, `readFile()`, `chmod()`, `chmodR()`, `ls()`, `lsF()`, `assertPermissions()`, `testChmodInternal()`, `testNewFileChmodInternal()`, `testChmodInternalR()`, `chown()`, and `assertOwners()`. Test methods cover `ls`, `groups`, `chmod`, directory permission behavior, `chown`, symlink rejection, `readlink`, and task creation with resource limits.

Control flow: Each test shells out to `winutils` with a temporary file tree, then parses command output or filesystem side effects. Permission tests set ACL-like modes and verify read/write/execute failures or formatted `ls` permissions. Recursive chmod constructs nested directories/files and checks directory execute handling. Task tests create command scripts or direct commands, then assert output files/strings or expected `Shell.ExitCodeException` codes for bad parameters and resource-limit failures.

State and persistence behavior: Test state is under a per-class temp directory from `GenericTestUtils`; `tearDown()` deletes it with `FileUtil.fullyDelete()`. The tests mutate real Windows ACLs, owner/group metadata, symlinks, and scheduled/job-object behavior. Some assertions rely on Windows-specific semantics, such as deletion succeeding without parent write permission and traverse-check bypassing execute permission.

Dependencies and integration points: Depends on `Shell`, `FileUtil`, Commons IO `FileUtils`, AssertJ, JUnit timeouts, and the native `winutils.exe` binary. It is a broad integration gate for Hadoop-on-Windows compatibility and native helper packaging.

Risks: Platform and environment sensitivity is high: tests require Windows, functional `winutils.exe`, appropriate privileges for symlink/chown/task operations, and localized group names matching expectations. The test parses command output with simple delimiters, so output format changes in `winutils` are breaking. Some resource-limit checks depend on Java command availability and OS behavior.

Test signals: Successful command output tokens, exact permission strings, expected access-denied IOExceptions, owner/group formatted values, symlink path echoes, `readlink` exit code `1` for invalid inputs, task proof-file creation, and exit code `1639` for bad task parameters provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestWinUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestXMLUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestXMLUtils.java

Purpose: Security-focused tests for `XMLUtils` factory methods. The file verifies that Hadoop-created DOM, SAX, Transformer, and SAX Transformer factories parse simple XML but reject external DTD/entity inputs, reducing XXE-style exposure.

Important APIs/types/functions: Tests call `XMLUtils.newSecureDocumentBuilderFactory()`, `newSecureSAXParserFactory()`, `newSecureTransformerFactory()`, `newSecureSAXTransformerFactory()`, and `bestEffortSetAttribute()`. `getResourceStream()` loads `/xml/external-dtd.xml` and `/xml/entity-dtd.xml` test resources.

Control flow: Positive tests parse or transform `<root/>` and assert a document/output exists. Negative tests wrap parser or transformer use in `assertThrows()`, expecting `SAXException` for DOM/SAX DTD/entity parsing and `TransformerException` for external-DTD transformation. `testBestEffortSetAttribute()` mutates `AtomicBoolean` flags based on whether setting an attribute succeeds and whether the incoming flag was already false.

State and persistence behavior: No durable state. Factory instances hold security attributes/features for the life of each test. Resource streams are closed with try-with-resources in negative cases.

Dependencies and integration points: Depends on JAXP DOM/SAX/Transformer APIs, XML constants, Hadoop `XMLUtils`, AssertJ, and JUnit. The factories are integration points for any Hadoop code parsing XML configuration or test resources in a hardened way.

Risks: XML security features vary by JAXP provider; `bestEffortSetAttribute()` intentionally degrades gracefully for unsupported attributes, so platform differences are expected. These tests verify failure on included resources but do not inspect which exact feature blocks the attack or cover all entity expansion vectors.

Test signals: Successful simple parse/transform, expected exceptions for external/entity DTD inputs, and correct `AtomicBoolean` state transitions for supported/unsupported attributes are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestXMLUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestZKUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestZKUtil.java

Purpose: Unit tests for ZooKeeper utility parsing in `ZKUtil`. The file covers ACL string parsing, auth string parsing, permission removal, and configuration indirection through `@file` references.

Important APIs/types/functions: Tests call `ZKUtil.parseACLs()`, `parseAuth()`, `removeSpecificPerms()`, and `resolveConfIndirection()`. `badAcl()` verifies `BadAclFormatException` message text. `ZKAuthInfo` and ZooKeeper `ACL`/`Perms` are the primary returned types.

Control flow: Empty and null ACL/auth strings must produce empty lists. Invalid ACL forms are passed to `badAcl()` to assert exact diagnostics. Valid ACLs parse comma-separated SASL identities with permission characters into `ACL` objects. Valid auth strings split only the first scheme/data separator so `scheme2:user:pass` preserves `user:pass`. Conf indirection reads a UTF-8 test file when the value starts with `@`, while plain strings and null are returned unchanged.

State and persistence behavior: `TEST_FILE` is under `GenericTestUtils.getTempPath("TestZKUtil")`; the test creates parent directories and writes content through Guava `Files.asCharSink`. No ZooKeeper server state is used. Permission state is represented only by integer bitmasks.

Dependencies and integration points: Depends on Hadoop `ZKUtil`, ZooKeeper ACL classes, Hadoop common configuration defaults, Guava-shaded file helpers, and JUnit. The parsing behavior feeds ZooKeeper-backed Hadoop coordination services and security configuration.

Risks: Exact exception-message assertions make diagnostics part of the test contract. `resolveConfIndirection()` reads local files from config values, so path handling and file-not-found messages matter. The ACL parser tests only SASL-style examples and a small invalid set, not digest/world/ip schemes.

Test signals: Empty-list returns, exact ACL permissions and identity fields, auth byte data preservation, removed `CREATE` bit, resolved file content, and `FileNotFoundException` prefix for missing indirection files are core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestZKUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/bloom/BloomFilterCommonTester.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/bloom/BloomFilterCommonTester.java

Purpose: Reusable strategy harness for Hadoop bloom-filter tests. It parameterizes filter implementations, hash type, insertion count, expected false positives, and common behavioral checks across `BloomFilter`, `CountingBloomFilter`, `RetouchedBloomFilter`, and `DynamicBloomFilter`.

Important APIs/types/functions: `optimalNumOfBits(int, double)` calculates bit-vector size from expected insertions and false-positive probability. Fluent methods `of()`, `withFilterInstance()`, and `withTestCases()` build a tester. `test()` runs each `BloomFilterTestStrategy`, recreating a symmetric fresh filter after each strategy. `getSymmetricFilter()` maps filter classes to constructors. The enum strategies cover add overloads, `Key` equality/weight/serialization, exception contracts, odd/even membership false positives, write/read serialization, XOR, AND, and OR.

Control flow: The tester builds immutable filter and strategy sets, obtains known false positives for Jenkins or Murmur hashes under 1000 insertions, then applies each strategy. Strategies mutate their filter, assert membership or exceptions, and rely on `getSymmetricFilter()` to reset state before the next strategy. Read/write tests serialize to `DataOutputBuffer`, reset a `DataInputBuffer`, and read into a fresh filter.

State and persistence behavior: The harness carries `hashType`, `numInsertions`, filter builders, and known false-positive tables. Bloom-filter persistence is exercised through Hadoop Writable serialization, not disk files. Random slots in `WRITE_READ_STRATEGY` make exact elements non-deterministic, but only round-trip membership for written keys is asserted.

Dependencies and integration points: Depends on Hadoop bloom classes, Hadoop hash classes, Hadoop IO buffers, Guava-shaded immutable collections, JUnit assertions, and Log4J. It is the central integration point for repeated filter semantics in `TestBloomFilters`.

Risks: Expected false positives are hard-coded for specific algorithms and vector sizing; hash algorithm changes can legitimately alter these sets and break tests. `FILTER_AND_STRATEGY` computes an intersection range that effectively covers `100..900`, so any off-by-one in the helper changes membership expectations. Unsupported XOR is tolerated, making cross-filter feature coverage uneven.

Test signals: Passing shared strategies signal add overload compatibility, null/illegal argument handling, serialization stability, deterministic hash false positives, logical operations, and `Key` weight/equality behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/bloom/BloomFilterCommonTester.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/bloom/TestBloomFilters.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/bloom/TestBloomFilters.java

Purpose: Concrete unit tests for Hadoop bloom-filter implementations. It combines the shared `BloomFilterCommonTester` with implementation-specific checks for dynamic, counting, retouched, large-vector, and bitwise-not behavior.

Important APIs/types/functions: Fields set `numInsertions = 1000`, `bitSize = optimalNumOfBits(..., 0.03)`, and `hashFunctionNumber = 5`. `FALSE_POSITIVE_UNDER_1000` maps Jenkins and Murmur hash ids to false-positive `Key` collections. Tests include `testDynamicBloomFilter()`, `testCountingBloomFilter()`, `testRetouchedBloomFilterSpecific()`, `testFiltersWithJenkinsHash()`, `testFiltersWithMurmurHash()`, `testFiltersWithLargeVectorSize()`, and `testNot()`.

Control flow: Common tests instantiate filters and request strategy sets from the harness. Counting-filter-specific flow adds the same key twice, checks approximate count increments/decrements through `delete()`, and validates membership clearing after both deletes. Retouched-filter flow iterates both hash algorithms and odd/even inserted populations, records known false positives, then calls `selectiveClearing()` for `MAXIMUM_FP`, `MINIMUM_FN`, and `RATIO` schemes.

State and persistence behavior: Filters are mutated in memory and, through the shared harness, serialized/deserialized via Writable buffers. `testNot()` directly sets the package-visible `bits` field on a small `BloomFilter` to a known `BitSet`, clones it, calls `not()`, and asserts no intersection with the original bits.

Dependencies and integration points: Depends on all Hadoop bloom implementations, `Key`, `RemoveScheme`, `Hash`, Guava-shaded immutable collections, `BitSet`, and JUnit. It exercises the filter API consumed by Hadoop data structures and probabilistic membership callers.

Risks: Known false-positive expectations are algorithm- and bit-size-specific. The large-vector test creates a `BloomFilter(Integer.MAX_VALUE, ...)`, so memory-efficient serialization/read behavior is important; changes to eager bit allocation could make it impractical. `testNot()` touches implementation detail `bits`, coupling the test to field visibility and representation.

Test signals: Membership and approximate-count changes, strategy harness pass/fail across hash algorithms, retouched selective-clearing absence checks, large vector write/read success, and zero intersection after bitwise not are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/bloom/TestBloomFilters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/concurrent/TestSubjectPropagation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/concurrent/TestSubjectPropagation.java

Purpose: Tests security `Subject` propagation into Hadoop thread wrappers and ordinary Java threads. It documents why `SubjectInheritingThread` and `Daemon` preserve caller subject context even when plain thread inheritance behavior differs by Java runtime/security configuration.

Important APIs/types/functions: Tests use `SubjectUtil.callAs()`, `SubjectUtil.current()`, `SubjectInheritingThread`, `Daemon`, plain `Thread`, and `SubjectUtil.THREAD_INHERITS_SUBJECT`. `childSubject` captures what the child observes.

Control flow: Each test creates a parent `Subject`, enters it with `SubjectUtil.callAs()`, starts a child thread variant, joins up to one second, and asserts the captured subject. Wrapper tests use both override-style `work()` implementations and `Runnable` constructors. Plain `Thread` tests branch: if the runtime inherits subjects, assert equality; otherwise assert null.

State and persistence behavior: Only the instance field `childSubject` persists between parent and child execution. There is no durable state, but the tests rely on thread-local or inherited security context managed by `SubjectUtil`.

Dependencies and integration points: Depends on JAAS `Subject`, Hadoop `Daemon`, `SubjectInheritingThread`, and authentication `SubjectUtil`. These classes are central to Hadoop authorization behavior in background worker threads.

Risks: Tests call `join(1000)` without explicitly failing on timeout before subject assertion, so a stalled child produces null/equality failures rather than direct timeout diagnostics. Runtime behavior for plain threads changes across Java versions and SecurityManager settings; the branch intentionally captures that compatibility surface.

Test signals: Wrapper thread cases must always see the parent subject. Plain thread cases must match `THREAD_INHERITS_SUBJECT`, protecting both Hadoop-managed propagation and documentation of JVM-dependent behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/concurrent/TestSubjectPropagation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/curator/TestSecureZKCuratorManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/curator/TestSecureZKCuratorManager.java

Purpose: Tests `ZKCuratorManager` and `HadoopZookeeperFactory` behavior when ZooKeeper client/server communication is configured for SSL/TLS. It also verifies Hadoop's `SecurityUtil.TruststoreKeystore` default and explicit configuration handling.

Important APIs/types/functions: `setup()` builds an Apache Curator `TestingServer` with secure client port settings, creates Hadoop secure config via `setUpSecureConfig()`, and starts a `ZKCuratorManager` with secure mode. `testSecureZKConfiguration()` creates a raw `ZooKeeper` through `HadoopZookeeperFactory`; `validateSSLConfiguration()` inspects `ZKClientConfig`. `testTruststoreKeystoreConfiguration()` validates empty-string normalization and explicit keystore/truststore values.

Control flow: Static secure setup writes ZooKeeper system properties for Netty server connection factory, server-side keystore/truststore, request timeout, `jute.maxbuffer`, SSL debugging, and X509 auth provider, then sets Hadoop `CommonConfigurationKeys` for client truststore/keystore paths. The test creates a secure ZooKeeper client and asserts both configured file/password properties and hard-coded secure-client properties such as `SECURE_CLIENT=true` and Netty client socket class.

State and persistence behavior: Test state includes a temporary ZooKeeper data directory, global JVM system properties, a live Curator testing server, and a `ZKCuratorManager`. `teardown()` closes curator and server, but system properties set in `setUpSecureConfig()` are process-global and may affect later ZooKeeper tests unless overwritten.

Dependencies and integration points: Depends on Apache Curator test server, ZooKeeper Netty server/client classes, Hadoop `Configuration`, `CommonConfigurationKeys`, and `SecurityUtil.TruststoreKeystore`. It validates the TLS configuration bridge from Hadoop config to ZooKeeper client config.

Risks: The test is sensitive to certificate resource paths and uses hard-coded secure port `2281`, which can conflict on shared hosts. Process-global ZooKeeper SSL properties and `javax.net.debug=ssl` can be noisy or leak between tests. Secure startup depends on Netty classes and local test keystore/truststore files being present.

Test signals: Successful secure server startup, exact ZooKeeper client config property values for keystore/truststore, secure client flag and Netty socket class, plus empty-string/default truststore-keystore behavior are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/curator/TestSecureZKCuratorManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/curator/TestZKCuratorManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/curator/TestZKCuratorManager.java

Purpose: Integration tests for non-TLS `ZKCuratorManager` operations and its ZooKeeper factory configuration. It covers znode CRUD, child listing, string data, safe transactions, JAAS configuration, and Curator builder integration.

Important APIs/types/functions: `setup()` starts a Curator `TestingServer`, creates `ZKCuratorManager`, and calls `start(zkHostPort)`. Tests invoke `exists()`, `create()`, `delete()`, `setData()`, `getData()`, `getStringData()`, `getChildren()`, `createTransaction()`, and `ZKCuratorManager.HadoopZookeeperFactory`. `validateJaasConfiguration()` checks `ZKClientConfig.LOGIN_CONTEXT_NAME_KEY` and JAAS `AppConfigurationEntry` options.

Control flow: CRUD tests create znodes, mutate byte/string payloads, and assert existence/children counts. Transaction tests create a `SafeTransaction`, queue create/set/delete operations, assert no pre-commit changes, then commit and verify atomic effects. JAAS tests construct multiple factories with different principals/keytabs, create ZooKeeper clients, and verify the selected login context; one branch sets a global JAAS configuration and login-context system property to confirm it overrides factory principals. Curator factory test builds a `CuratorFramework` with the Hadoop factory and validates the resulting client.

State and persistence behavior: A live in-process ZooKeeper server persists znodes for each test until teardown. JAAS configuration and `ZKClientConfig.LOGIN_CONTEXT_NAME_KEY` are process-global; the test clears the property in a `finally` block for the global override path. Transaction state is local until `commit()`.

Dependencies and integration points: Depends on Apache Curator framework/test, ZooKeeper, Hadoop `Configuration`, `CommonConfigurationKeys`, `SecurityUtil`, `JaasConfiguration`, and `ZKUtil` ACL parsing. It validates coordination-service integration used by Hadoop HA and service fencing paths.

Risks: In-process ZooKeeper tests can be flaky if ports or background server cleanup fail. Process-global JAAS state is a cross-test hazard. Children-count assertions include ZooKeeper's default root child, so Curator/ZooKeeper version behavior can affect expected counts.

Test signals: Existence/data assertions, children-count changes, pre/post-commit transaction visibility, matching byte arrays, JAAS principal/keytab values, and Curator-created ZooKeeper config are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/curator/TestZKCuratorManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/Concatenator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/Concatenator.java

Purpose: Test fixture class for `DynMethods` and `DynConstructors`. It supplies overloaded constructors, overloaded instance methods, a private constructor, a private setter, checked-exception throwing paths, varargs methods, and a static factory-like method.

Important APIs/types/functions: Public constructors include no-arg, `Concatenator(String sep)`, and `Concatenator(Exception e) throws Exception`; a private `Concatenator(char sep)` tests hidden constructor access. `SomeCheckedException` is a checked marker. Methods include private `setSeparator(String)`, overloads `concat(String,String)`, `concat(String,String,String)`, `concat(Exception)`, varargs `concat(String...)`, static `cat(String...)`, and static `newConcatenator(String)`.

Control flow: Constructors set the separator or throw the supplied exception. `concat` overloads join arguments using `sep`; the varargs version returns null for zero arguments and otherwise loops through the array. The exception overload rethrows the supplied exception to test reflective checked exception propagation.

State and persistence behavior: The only state is instance field `sep`, initialized to empty string and mutated by constructors or private `setSeparator()`. No external persistence exists. Hidden-access tests rely on reflective accessibility rather than public API.

Dependencies and integration points: Depends only on Java language/runtime features and is consumed by `TestDynMethods` and `TestDynConstructors`. It is derived from Parquet utility tests, serving as a stable reflection target for Hadoop dynamic invocation helpers.

Risks: Because this fixture intentionally exposes private members for tests, changing visibility or signatures can break dynamic helper coverage. Overload resolution tests depend on argument count and type erasure/varargs behavior matching the fixture exactly.

Test signals: Expected concatenated strings with different separators, private separator mutation, static varargs invocation, constructor selection, and checked exception propagation are all derived from this fixture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/Concatenator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/TestDynConstructors.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/TestDynConstructors.java

Purpose: Unit tests for reflective constructor discovery and invocation in `DynConstructors`. The tests verify missing implementation behavior, first matching implementation selection, string class-name lookup, hidden constructor access, argument validation, and checked exception wrapping.

Important APIs/types/functions: Tests use `DynConstructors.Builder`, `impl()`, `hiddenImpl()`, `buildChecked()`, `build()`, and `DynConstructors.Ctor.newInstanceChecked()/newInstance()`. They use `Concatenator` as the target and `LambdaTestUtils.intercept()` for expected exceptions.

Control flow: Missing-builder, missing-class, and missing-constructor tests assert `NoSuchMethodException` from checked builds and runtime failures from unchecked builds. First-match tests add a fake class before valid constructors and assert the first valid constructor wins. Exception tests build the `Exception` constructor and require checked invocation to rethrow the original checked exception while unchecked invocation wraps it. Hidden-constructor tests demonstrate that normal method lookup cannot find private members, but `hiddenImpl()` can find the private char constructor.

State and persistence behavior: No persistent state beyond constructed `Concatenator` instances and their separators. Builder state is ordered; implementation registration order is part of the contract.

Dependencies and integration points: Depends on Hadoop dynamic reflection helpers, JUnit, and Hadoop test interception helpers. These utilities support optional dependency/version compatibility where code attempts multiple reflective constructors.

Risks: Tests are sensitive to reflection access restrictions in newer Java runtimes and module boundaries. The unchecked build path intentionally wraps failures in runtime exceptions, so exact wrapper type/message coverage is limited. Builder order changes would alter first-implementation behavior.

Test signals: Expected `NoSuchMethodException`, `RuntimeException`, `IllegalArgumentException`, original checked exception propagation, non-null hidden constructor, and correct separator output demonstrate the constructor helper contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/TestDynConstructors.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/TestDynMethods.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/TestDynMethods.java

Purpose: Comprehensive tests for `DynMethods` reflective method discovery and invocation. It covers ordered implementation selection, overload/varargs invocation, hidden methods, bound methods, static methods, constructor adapters, no-op fallback, incorrect arguments, and checked exception propagation.

Important APIs/types/functions: Tests use `DynMethods.Builder`, `impl()`, `hiddenImpl()`, `ctorImpl()`, `orNoop()`, `buildChecked()`, `build()`, `buildStaticChecked()`, `buildStatic()`, `UnboundMethod.invoke()/invokeChecked()/bind()/isStatic()/isNoop()/asStatic()`, `BoundMethod`, and `StaticMethod`. `Concatenator` is the reflection target.

Control flow: The test suite first verifies failure paths for no implementations, missing classes, and missing methods. First-match tests register fake and real overloads, proving earlier valid implementations win, extra arguments are ignored, and missing arguments are null-padded. Other tests invoke varargs through an `Object` array, verify wrong argument types raise `IllegalArgumentException`, rethrow checked exceptions through checked invocation, remap method names, look up methods by string class name, access private `setSeparator()` through `hiddenImpl()`, bind methods to different target instances, and enforce static/non-static constraints.

State and persistence behavior: State exists only in target `Concatenator` separators and builder method lists. No-op methods are stateless and can be unbound, bound to null or an object, or treated as static while always returning null. Constructor adapter state creates new `Concatenator` instances through `ctorImpl()`.

Dependencies and integration points: Depends on Hadoop dynamic reflection helpers, the `Concatenator` fixture, JUnit, and Hadoop `LambdaTestUtils`. Dynamic methods are used for optional APIs and cross-version compatibility where Hadoop must reflectively call methods when present.

Risks: Reflection behavior may vary with Java access controls, especially private hidden methods. The helper's argument trimming/null padding is powerful but risky because wrong arity may not fail in some cases. Static binding constraints protect misuse but require accurate method modifier detection.

Test signals: Correct concatenated strings, private separator update, expected exceptions for bad discovery/invocation/binding, static status checks, constructor adapter behavior, and no-op null returns are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/TestDynMethods.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestFunctionalIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestFunctionalIO.java

Purpose: Unit tests for functional wrappers that convert checked `IOException`-throwing lambdas into unchecked Java functional interfaces and back. It protects helper behavior used when IO operations must pass through APIs that cannot throw checked IOExceptions.

Important APIs/types/functions: Tests statically import `FunctionalIO.uncheckIOExceptions()`, `toUncheckedIOExceptionSupplier()`, `extractIOExceptions()`, and `toUncheckedFunction()`. They use `UncheckedIOException`, `FileNotFoundException`, and Hadoop `LambdaTestUtils.intercept()`.

Control flow: `testUncheckIOExceptions()` throws a checked `IOException` inside a lambda and asserts it is wrapped with the same cause. `testUncheckIOExceptionsUnchecked()` verifies an existing `UncheckedIOException` is propagated rather than double-wrapped. Supplier and function tests verify conversion of throwing suppliers/functions to unchecked forms. `testUncheckAndExtract()` wraps an IO exception then extracts it back as the original checked exception.

State and persistence behavior: Stateless functional tests with only local exception instances. Cause identity is asserted where important.

Dependencies and integration points: Depends on Hadoop functional IO interfaces, Java `Function`, JUnit, AssertJ, and `LambdaTestUtils`. These utilities integrate IO-heavy Hadoop operations with Java streams, reflection, suppliers, and callbacks.

Risks: Wrapper code must preserve original causes and avoid double wrapping; otherwise callers lose exception identity/type. The tests cover IOExceptions only and do not deeply exercise non-IO runtime exceptions or interrupted operations.

Test signals: Same-cause assertions, same unchecked exception instance propagation, expected message matching, and `FileNotFoundException` wrapping through a `Function` are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestFunctionalIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestLazyReferences.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestLazyReferences.java

Purpose: Tests lazy single-evaluation references and lazy auto-closeable references. It verifies supplier integration, cached evaluation, exception wrapping/retry behavior, close idempotency, closed-state guards, and cleanup when close itself fails.

Important APIs/types/functions: Tests use `LazyAtomicReference`, `LazyAutoCloseableReference`, `lazyAtomicReferenceFromSupplier()`, `lazyAutoCloseablefromSupplier()`, `eval()`, `apply()`, `get()`, `isSet()`, `isClosed()`, `getReference()`, and `close()`. Fixtures `CloseableClass` and `CloseableRaisingException` implement `AutoCloseable`.

Control flow: Lazy atomic tests assert constructors do not invoke suppliers, first `eval()`/`get()` increments the counter once, and later `apply()` returns the cached value. Failure handling throws `UnknownHostException` from the supplier, verifies it is wrapped in `UncheckedIOException`, leaves the reference unset, and retries on the next call. Auto-closeable tests evaluate the reference, close it, assert the underlying object is closed and the inner reference cleared, then verify later eval/get/apply calls fail with "Reference is closed". Failure-close tests assert the first close reports the IO failure but clears state so a second close is harmless.

State and persistence behavior: `AtomicInteger counter` records supplier invocations. Lazy references persist either an evaluated value, unset state after failure, or closed state after close. Auto-closeable references clear their internal atomic reference on close, even when the resource close throws.

Dependencies and integration points: Depends on Hadoop functional lazy reference classes, Hadoop `Preconditions.checkState`, AssertJ, JUnit, and `LambdaTestUtils`. These references support delayed initialization of resources that may throw IO-related failures and need deterministic cleanup.

Risks: Concurrency is implied by `LazyAtomicReference` but not stress-tested across multiple racing threads. Exception wrapping leaves the reference unset, which is useful for retry but can repeatedly trigger expensive failing suppliers. Closing after failed resource close deliberately suppresses future close attempts because the reference has been nulled.

Test signals: Counter values, `isSet()` transitions, cause verification for `UnknownHostException`, closed flags on wrapper and underlying resource, cleared inner reference, and first-close-only exception behavior are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestLazyReferences.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestRemoteIterators.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestRemoteIterators.java

Purpose: Tests `RemoteIterators` adapters and combinators for Hadoop `RemoteIterator`. It validates array/singleton/range/iterator/iterable adapters, mapping, filtering, foreach iteration, close passthrough, halt predicates, and IOStatistics propagation.

Important APIs/types/functions: Static helpers under test include `remoteIteratorFromArray()`, `remoteIteratorFromSingleton()`, `mappingRemoteIterator()`, `filteringRemoteIterator()`, `remoteIteratorFromIterator()`, `remoteIteratorFromIterable()`, `closingRemoteIterator()`, `haltableRemoteIterator()`, `rangeExcludingIterator()`, `foreach()`, and statistics extraction. Local fixtures include `CloseCounter`, `IOStatsInstance`, `CountdownRemoteIterator`, `CountdownIterator`, and `CountdownIterable`.

Control flow: Tests iterate through adapters with `verifyInvoked()`, which calls `foreach()` and asserts count. Mapping increments a counter while preserving values; filtering accepts even numbers, none, or all. Close tests verify `foreach()` closes closeable iterators once and explicit close is idempotent. Iterable close tests wrap an iterable so exhaustion in `hasNext()` or `next()` closes the source and prevents later iterator creation. Haltable tests stop before source exhaustion when a predicate flips false. Range tests verify empty and 100-element ranges plus `NoSuchElementException` on exhausted `next()`.

State and persistence behavior: Counters track consumer invocations and close counts. Countdown fixtures mutate their limit during iteration. `CountdownIterable` refuses new iterators after close by checking close count. IO statistics are exposed through `IOStatisticsSource` fixtures and wrappers.

Dependencies and integration points: Depends on Hadoop `RemoteIterator`, IO statistics APIs, functional iterator helpers, AssertJ, SLF4J, JUnit, and Hadoop test interception helpers. These adapters are used when filesystem listings and other remote scans need functional transformations while preserving IO semantics.

Risks: Close semantics are subtle: singleton close should not close the singleton value, while mapping/closing wrappers must close the source exactly once. Filtering must handle internal lookahead without skipping or double-consuming. The tests do not simulate `IOException` from `hasNext()`/`next()` except through API signatures.

Test signals: Iteration counts, counter values, close-count assertions, `toString()` content, IO statistics extraction success, halt-at-limit behavior, and exhausted range exceptions are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestRemoteIterators.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestTaskPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestTaskPool.java

Purpose: Parameterized tests for Hadoop `TaskPool`, covering sequential and executor-backed execution with failure handling, suppression, stop-on-failure, abort, revert, and failure callbacks. The file was pulled from S3A-style task pool tests.

Important APIs/types/functions: Tests use `TaskPool.foreach(items).executeWith(submitter)` and builder options `suppressExceptions()`, `stopOnFailure()`, `abortWith()`, `revertWith()`, `onFailure()`, and `stopAbortsOnFailure()`. `PoolSubmitter` adapts `ExecutorService` to `TaskPool.Submitter`. Fixtures `Item`, `BaseCounter`, `CounterTask`, and `FailureCounter` track committed/aborted/reverted/failed state and controlled IO failures.

Control flow: Parameter source runs each test with thread counts `0`, `1`, `3`, `8`, and `16`; zero threads means direct execution with no submitter. Setup creates 16 items and, for positive thread counts, a daemon fixed pool. Simple invocation commits all items. Failure tests use a task that throws on invocation `8` and vary builder policy: continue through failures, stop fast, abort uncommitted work, revert committed work, suppress or propagate exceptions, and stop aborts on abort failure. Parallel tests use at-least assertions where concurrency can schedule extra work after a failure.

State and persistence behavior: Each test recreates `items`, counters, and optionally an executor. Item flags are volatile because parallel worker threads mutate them. Teardown shuts down the thread pool but does not await termination; tests rely on `TaskPool.run()` to complete submitted work before returning or throwing.

Dependencies and integration points: Depends on Hadoop `TaskPool`, Guava-shaded `ThreadFactoryBuilder`, Java executors/futures/streams, JUnit parameterized tests, SLF4J, and Hadoop test helpers. TaskPool is a reusable utility for batch operations that need rollback/abort behavior.

Risks: Parallel scheduling makes exact invocation counts brittle; the test accounts for this with `isParallel()` branches. Failure callback stores only the last item/exception and is not deeply asserted beyond count in most cases. Shutdown without await could leave lingering threads if a regression returns before work settles.

Test signals: Boolean run success/failure, propagated `IOException` when suppression is absent, invocation counts or minimum counts, item state invariants for committed/failed/aborted/reverted work, and single failure callback invocation are the core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestTaskPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/hash/TestHash.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/hash/TestHash.java

Purpose: Unit tests for Hadoop hash algorithm selection and deterministic hashing. It verifies string-to-hash-type parsing, configuration-based instance selection, id-based singleton retrieval, invalid hash handling, and repeatability for Jenkins and Murmur hashes.

Important APIs/types/functions: Tests call `Hash.parseHashType()`, `Hash.getInstance(Configuration)`, `Hash.getInstance(int)`, `MurmurHash.getInstance()`, `JenkinsHash.getInstance()`, and `hash(byte[])`/`hash(byte[], int)`. The constant `LINE` is a stable byte input for repeatability checks.

Control flow: The test asserts known parse ids for `"jenkins"`, `"murmur"`, and an undefined string. It sets `hadoop.util.hash.type` in `Configuration` to select Murmur and Jenkins, checks default configuration falls back to Murmur, and verifies invalid id returns null. It then computes one hash value for each algorithm with and without seed `67`, repeating each computation 30 times to assert equality.

State and persistence behavior: No external state. Hash implementation instances are expected to be singleton objects. Configuration only lives inside the test.

Dependencies and integration points: Depends on Hadoop `Configuration`, `Hash`, `MurmurHash`, `JenkinsHash`, and JUnit. Hash selection is consumed by bloom filters and other utility code requiring stable hashing.

Risks: Tests assert repeatability but not specific numeric hash outputs, so algorithm changes that remain deterministic may pass while altering cross-version serialized structures or bloom false positives. String parsing appears case-specific in tested examples; other casing/aliases are not covered.

Test signals: Correct parse constants, singleton identity equality, null invalid lookup, default Murmur selection, and repeated deterministic hashes are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/hash/TestHash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/mini_rpc_benchmark.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/mini_rpc_benchmark.proto

Purpose: Protobuf schema for `MiniRPCBenchmark`, mirroring a legacy Writable RPC mini protocol so benchmarks can exercise delegation-token RPC connection establishment over `ProtobufRpcEngine2`.

Important APIs/types/functions: The file uses `syntax = "proto2"`, Java package `org.apache.hadoop.ipc.protobuf`, outer class `MiniRPCBenchmarkProtos`, generic services, and generated equals/hash. Messages are `MiniGetDelegationTokenRequestProto`, `MiniDelegationTokenProto`, and `MiniGetDelegationTokenResponseProto`. Service `MiniProtocolService` exposes `getDelegationToken()`.

Control flow: There is no runtime control flow in the schema. Generated code will serialize a request with required `renewer`, optionally return a delegation token response, and dispatch the service method through protobuf RPC bindings.

State and persistence behavior: Serialized message state includes token identifier/password bytes and token kind/service strings. Required proto2 fields make missing fields invalid at build/serialization time for initialized messages. The response token is optional to allow absent-token responses.

Dependencies and integration points: It intentionally inlines token messages instead of importing security protos to keep benchmark proto-path setup simple. Generated Java integrates with Hadoop IPC protobuf benchmark code and service stubs.

Risks: Required proto2 fields are strict and can break compatibility if benchmark callers construct partial messages. Since this is a benchmark-specific mirror, drift from the legacy MiniProtocol shape would undermine comparative results. Field numbers are wire ABI and must remain stable.

Test signals: Successful protoc generation, service stub availability, and benchmark RPC calls that request and return delegation token messages validate this schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/mini_rpc_benchmark.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test.proto

Purpose: Core protobuf message schema for Hadoop common IPC tests. It defines request/response payloads used by test RPC services for ping, echo, add, exchange, auth, user identity, and sleep/timing scenarios.

Important APIs/types/functions: Uses `syntax = "proto2"`, Java package `org.apache.hadoop.ipc.protobuf`, outer class `TestProtos`, and generated equals/hash. Messages include empty request/response, required and optional echo messages, sleep requests/responses, slow ping, repeated-string echo, add requests/responses, exchange value lists, auth method response, user response, and extended sleep timing messages.

Control flow: The schema itself has no executable control flow; generated builders/messages are consumed by RPC service definitions in `test_rpc_service.proto` and corresponding Java test code. Required fields enforce initialized messages for core request/response types, while optional fields support compatibility tests around evolving RPC signatures.

State and persistence behavior: Proto2 wire state is field-numbered and package-scoped under `hadoop.common`. Repeated fields preserve ordered lists of strings or integers for echo/exchange/add2 tests. Optional sleep timing fields allow request/response timestamps to be omitted.

Dependencies and integration points: Imported by `test_rpc_service.proto`. Generated Java classes are used by Hadoop IPC unit/integration tests for protobuf engines, compatibility, authentication, postponed responses, and handoff timing.

Risks: Message names and field numbers are shared test ABI with service schemas; changing them breaks generated stubs and tests. Required fields can make compatibility evolution harder, which is why optional variants are present for some RPC compatibility cases.

Test signals: Protoc generation, successful import by service proto, generated builders enforcing required fields, and RPC tests exercising each message family validate the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_legacy.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_legacy.proto

Purpose: Legacy variant of the common IPC test protobuf messages. It mirrors `test.proto` message content and Java options but omits an explicit `syntax = "proto2"` line, preserving older protoc/default-syntax behavior for compatibility tests.

Important APIs/types/functions: Java package is `org.apache.hadoop.ipc.protobuf`, outer class is `TestProtosLegacy`, and generated equals/hash is enabled. It defines the same message set as `test.proto`: empty, echo, optional echo, sleep, slow ping, repeated echo, add, exchange, auth method, user, and sleep timing request/response messages.

Control flow: No executable control flow. Generated legacy message classes are imported by `test_rpc_service_legacy.proto` and used to test legacy protobuf service generation and RPC compatibility.

State and persistence behavior: Wire fields and required/optional/repeated declarations match the non-legacy schema, but generated Java class names differ. Because syntax is omitted, the file relies on proto2 defaults in older protobuf tooling.

Dependencies and integration points: Imported by `test_rpc_service_legacy.proto`. It integrates with Hadoop IPC tests that need both current and legacy generated protobuf classes available side by side.

Risks: Omitting `syntax` can produce warnings or different behavior under newer protobuf toolchains if defaults change or enforcement tightens. The schema must stay synchronized with `test.proto` for meaningful legacy/current comparisons while retaining distinct outer class names.

Test signals: Successful legacy protoc generation, import by legacy service proto, and side-by-side IPC tests comparing current and legacy generated classes validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_legacy.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_rpc_service.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_rpc_service.proto

Purpose: Protobuf service schema for Hadoop IPC tests using the current `test.proto` message classes. It defines multiple test services for normal calls, multi-protocol behavior, protocol compatibility, custom protocol naming, and sleep handoff timing.

Important APIs/types/functions: Uses `syntax = "proto2"`, Java package `org.apache.hadoop.ipc.protobuf`, outer class `TestRpcServiceProtos`, generic services, generated equals/hash, and imports `test.proto`. Services include `TestProtobufRpcProto`, `TestProtobufRpc2Proto`, `OldProtobufRpcProto`, `NewProtobufRpcProto`, `NewerProtobufRpcProto`, `CustomProto`, and `TestProtobufRpcHandoffProto`.

Control flow: Generated service interfaces dispatch RPC methods such as `ping`, `echo`, `error`, `slowPing`, `add`, `exchange`, `sleep`, `lockAndSleep`, auth/user lookup, postponed echo/send, current/remote user lookup, and handoff sleep. Compatibility services intentionally vary the `echo` signature across old/new/newer protocols.

State and persistence behavior: No schema-local persistent state. Runtime state is in generated request/response messages and test service implementations. RPC method names and request/response types form the service ABI used by Hadoop IPC test servers and clients.

Dependencies and integration points: Depends on `test.proto` messages and protobuf generic service generation. It integrates directly with Hadoop IPC protobuf engine tests, server/client authentication tests, exception propagation tests, and protocol version compatibility checks.

Risks: Service and method names are test protocol ABI; renaming or changing signatures breaks generated stubs and reflection-based protocol mapping. Generic services are legacy protobuf Java behavior, so toolchain upgrades must preserve support or migrate tests. Compatibility services must remain intentionally distinct.

Test signals: Successful protoc service generation, RPC calls across all methods, expected server-side errors, auth/user responses, postponed response behavior, and old/new protocol compatibility tests validate this schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_rpc_service.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_rpc_service_legacy.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_rpc_service_legacy.proto

Purpose: Legacy service schema for Hadoop IPC tests using `test_legacy.proto` messages and a distinct generated outer class. It mirrors the current service schema while preserving a legacy generated-code path.

Important APIs/types/functions: Uses `syntax = "proto2"`, Java package `org.apache.hadoop.ipc.protobuf`, outer class `TestRpcServiceProtosLegacy`, generic services, generated equals/hash, and imports `test_legacy.proto`. It declares the same service set and RPC methods as `test_rpc_service.proto`.

Control flow: Generated legacy service interfaces dispatch the same ping, echo, error, slow ping, add, exchange, sleep, auth/user, postponed response, protocol compatibility, custom protocol, and handoff sleep methods. The practical control flow is in test implementations that bind these generated services to Hadoop IPC.

State and persistence behavior: No persistent state in the schema. Wire-level method and message definitions are intended to parallel the current schema while generating separate Java classes, allowing side-by-side compatibility tests.

Dependencies and integration points: Depends on `test_legacy.proto` and protobuf generic service generation. It integrates with Hadoop IPC tests that need legacy class names and service descriptors separate from the current message/service artifacts.

Risks: The file must remain synchronized with `test_rpc_service.proto`; divergence should be intentional and documented because it affects compatibility assertions. It also relies on generic service support and legacy generated-code behavior.

Test signals: Protoc generation of `TestRpcServiceProtosLegacy`, successful imports from `TestProtosLegacy`, and legacy IPC service/client tests exercising the mirrored method set validate this schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_rpc_service_legacy.proto -->
