# subset-b-007399 research

This grouped report covers Hadoop common test and benchmark files under `org.apache.hadoop.io` and `org.apache.hadoop.ipc`. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestVLong.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestVLong.java

## Purpose
`TestVLong` verifies TFile variable-length long encoding and decoding through `Utils.writeVLong()` and `Utils.readVLong()`. It checks exact encoded sizes for edge ranges and performs a large randomized round trip.

## Important APIs, Types, and Functions
The test uses Hadoop `FileSystem`, `Path`, `FSDataOutputStream`, and `FSDataInputStream` over a `GenericTestUtils` test directory. `writeAndVerify(int shift)` serializes every `short` value shifted by a byte-aligned amount and then reads the sequence back. `verifySixOrMoreBytes(int bytes)` covers larger encodings. Test methods cover byte, short, 3- through 8-byte encodings, and random long masks.

## Control Flow
`setUp()` creates a local test path and removes any stale output; `tearDown()` removes it again. Each deterministic test writes a contiguous range, closes the stream, reopens it, validates all decoded values in order, and asserts the final file length against a formula for the expected encoding width. `testVLongRandom()` creates one million random masked longs, writes them sequentially, and validates the full stream round trip.

## State and Persistence
Persistent state is limited to a temporary file named `TestVLong` under the test directory. There is no shared static mutable state beyond `ROOT`; every test deletes the file to avoid cross-test contamination.

## Dependencies and Integration Points
The file integrates with Hadoop local filesystem streams and the TFile `Utils` encoding implementation. The encoded-size assertions are a compatibility signal for TFile binary format behavior.

## Risks and Edge Cases
The tests assume exact byte-length formulas for signed values around byte and short boundaries. Random generation uses an unseeded `Random`, so failures may be less reproducible. `1L << 64` in the random mask path effectively wraps Java shift distance, which makes the full-64-bit case behave as a one-bit mask rather than all bits.

## Test Signals
Strong signals are exact encoded file lengths for each width, no read/write mismatch across negative and positive ranges, and successful randomized round trips over one million values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestVLong.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/Timer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/Timer.java

## Purpose
`Timer` is a small test utility for measuring elapsed wall-clock time and printing timestamped messages in TFile tests.

## Important APIs, Types, and Functions
The class stores `startTimeEpoch` and `finishTimeEpoch` fields. `startTime()` and `stopTime()` capture `Time.now()`, `getIntervalMillis()` subtracts them, `formatTime(long)` delegates to `Time.formatTime()`, `getIntervalString()` formats elapsed time, and `printlnWithTimestamp(String)` writes to standard output with the current formatted time.

## Control Flow
Callers start the timer, run the measured operation, stop the timer, and then ask for raw or formatted elapsed time. Timestamp printing is independent from the start/stop interval.

## State and Persistence
All state is in two mutable long fields on the instance. The class has no filesystem persistence, synchronization, reset validation, or monotonic-time protection.

## Dependencies and Integration Points
It depends on `org.apache.hadoop.util.Time`, which centralizes Hadoop time formatting. It integrates only as a helper for tests and benchmarks in the TFile package.

## Risks and Edge Cases
The API declares `IOException` even though current operations do not throw it. Calling `getIntervalMillis()` before both timestamps are set returns a value based on zero defaults. Because it uses wall-clock time rather than monotonic time, clock adjustments can affect intervals.

## Test Signals
Useful validation is direct construction, expected positive interval after start/stop, correct `Time.formatTime()` formatting, and no accidental dependency on global state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/Timer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestNativeIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestNativeIO.java

## Purpose
`TestNativeIO` exercises Hadoop native I/O wrappers across POSIX, Windows, memory mapping, file-copy, and persistent-memory paths. It verifies JNI/native method availability, error translation, platform-specific semantics, and concurrency safety.

## Important APIs, Types, and Functions
The tests use `NativeIO.POSIX.getFstat()`, `getStat()`, `open()`, `chmod()`, `posix_fadvise()`, `sync_file_range()`, `getUserName()`, `getGroupName()`, `mlock()`, `munmap()`, POSIX constants, and `NativeIO.POSIX.Pmem` mapping/copy/sync APIs. Windows paths use `NativeIO.Windows.createFile()`, `setFilePointer()`, and `access()`. Cross-platform helpers include `NativeIO.renameTo()`, `NativeIO.copyFileUnbuffered()`, and `NativeIO.getMemlockLimit()`. `doStatTest()` centralizes stat validation against `StatUtils.getPermissionFromProcess()`.

## Control Flow
Two `@BeforeEach` hooks skip tests unless native code is loaded and reset `TEST_DIR`. The suite then branches by platform assumptions: POSIX-only tests cover open/chmod/fadvise/user lookup/constants; Windows-only tests cover file pointer, share-delete create, long-path access checks; common tests cover stat, rename, sync range, memory lock, unbuffered copy, and PMDK-gated persistent memory. Multi-threaded stat and fstat tests repeatedly issue native calls from thread pools or `SubjectInheritingThread`s and propagate any observed exception.

## State and Persistence
State is temporary filesystem state under `testnativeio`, `renameTest`, `/dev/zero`, and PMDK paths such as `/mnt/pmem0/...` when PMDK is available. Native file descriptors are opened and closed through Java streams. Persistent-memory tests create mapped files and explicitly delete some error-path files.

## Dependencies and Integration Points
The file integrates with Hadoop `NativeCodeLoader`, `NativeIOException`/`Errno`, local `FileSystem`, `FsPermission`, `PathIOException`, `StatUtils`, Apache Commons IO cleanup, and platform assumption helpers. It directly tests Hadoop's bridge to OS syscalls and native libraries.

## Risks and Edge Cases
Many tests are platform and environment sensitive. PMDK tests assume a configured `/mnt/pmem0` device and 16 GB volume model when `isPmdkAvailable()` is true. `testCopyFileUnbuffered()` allocates and maps a 128 MB file. Error assertions differ for Windows messages versus POSIX `Errno`. Concurrency tests may reveal native library thread-safety problems in user/group lookup.

## Test Signals
Signals include matching stat owner/group/mode with OS commands, expected `Errno` for closed or missing descriptors, no descriptor leaks over 10,000 opens, correct Windows access behavior including long paths, successful mlock/copy/PMDK byte round trips, and all native constants being initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestNativeIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestNativeIoInit.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestNativeIoInit.java

## Purpose
`TestNativeIoInit` is a focused regression test for native I/O class initialization deadlocks, especially the static initializer interaction described by HADOOP-14451.

## Important APIs, Types, and Functions
The tests call `NativeIO.isAvailable()`, `NativeIO.POSIX.isAvailable()`, and on Windows `NativeIO.Windows.extendWorkingSetSize(100)`. Threads are `SubjectInheritingThread`s to preserve Hadoop subject context.

## Control Flow
`testDeadlockLinux()` starts two threads that touch the outer `NativeIO` class and the nested `NativeIO.POSIX` class concurrently, then joins both under a 10-second timeout. `testDeadlockWindows()` is Windows-gated and races `NativeIO.isAvailable()` against a Windows native call, swallowing expected `IOException`s from the working-set extension.

## State and Persistence
The only state is JVM class initialization state and thread execution. The test creates no files and persists nothing.

## Dependencies and Integration Points
It depends on the native I/O initialization path, `Path.WINDOWS`, JUnit timeouts, and Hadoop's subject-inheriting thread utility. It intentionally lives in a separate class so forked test execution reloads static blocks.

## Risks and Edge Cases
The signal is timeout-based; a deadlock manifests as the test exceeding its timeout rather than an assertion failure. The Windows branch only runs on Windows and ignores `IOException` from the native call because the concern is deadlock, not permission.

## Test Signals
Passing means both initialization threads finish within 10 seconds on POSIX and Windows-specific class initialization also completes without hanging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestNativeIoInit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestSharedFileDescriptorFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestSharedFileDescriptorFactory.java

## Purpose
`TestSharedFileDescriptorFactory` validates creation, cleanup, and directory fallback behavior for Hadoop's shared file descriptor factory.

## Important APIs, Types, and Functions
The suite uses `SharedFileDescriptorFactory.getLoadingFailureReason()`, `SharedFileDescriptorFactory.create(prefix, paths)`, `createDescriptor(name, length)`, and `getPath()`. Helpers create temporary remainder files and use `FileUtil.fullyDelete()`.

## Control Flow
`setup()` skips when the factory failed to load. `testReadAndWrite()` creates a descriptor-backed input stream, wraps the same descriptor in an output stream, writes a byte, seeks the input channel to zero, and verifies readback. `testCleanupRemainders()` creates stale prefixed files and asserts factory construction removes them on Unix native I/O. `testDirectoryFallbacks()` first verifies all-bad directories fail, then supplies a good fallback path and checks it is selected.

## State and Persistence
Temporary directories live under the common test directory. Created descriptor files and stale remainder files are deleted by the factory or explicit cleanup. No durable state is intended.

## Dependencies and Integration Points
The file depends on `NativeIO.isAvailable()`, Apache Commons `SystemUtils.IS_OS_UNIX`, Hadoop `Path.SEPARATOR`, `FileUtil`, and the native shared descriptor implementation used by components needing shared memory or mmap-backed descriptors.

## Risks and Edge Cases
Tests assume root directory is permission denied for descriptor creation. Cleanup behavior is Unix-gated. Descriptor lifecycle must avoid closing one stream before the other in a way that invalidates the shared FD unexpectedly.

## Test Signals
Signals are successful byte write/read through a shared descriptor, removal of stale prefix remainders, correct IOException when all paths are unusable, and selection of the first usable fallback directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestSharedFileDescriptorFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestConnectionRetryPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestConnectionRetryPolicy.java

## Purpose
`TestConnectionRetryPolicy` verifies equality and hash-code behavior for connection-level retry policies built by `RetryUtils.getDefaultRetryPolicy()` and for `TryOnceThenFail`.

## Important APIs, Types, and Functions
The helper `getDefaultRetryPolicy(...)` constructs policies from `Configuration`, enable flags, retry specs, and remote exception class names. `verifyRetryPolicyEquivalence()` checks pairwise equality and hash code equality. `newTryOnceThenFail()` exposes a new `RetryPolicies.TryOnceThenFail` instance for equality testing.

## Control Flow
`testDefaultRetryPolicyEquivalence()` builds policies with same and different specs, enabled and disabled modes, and varying `RemoteException` class names. It asserts enabled policies with different specs are unequal, while disabled policies are equal regardless of spec. `testTryOnceThenFailEquivalence()` verifies separate instances compare equal.

## State and Persistence
The test is stateless outside local policy objects and `Configuration` instances. No files or global retry state are persisted.

## Dependencies and Integration Points
It depends on `RetryUtils`, `RetryPolicy`, `RetryPolicies`, Hadoop IPC exception classes, and `PathIOException`. It protects retry policy use in connection-level caching, maps, or comparisons.

## Risks and Edge Cases
The helper accepts a `remoteExceptionToRetry` argument but currently passes an empty string to `RetryUtils`, so remote-exception variation does not influence constructed policies in this test. Equality assertions are sensitive to policy implementation internals.

## Test Signals
Expected signals are stable equality/hash behavior for equivalent policies, inequality when enabled specs differ, and disabled policy equality independent of retry spec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestConnectionRetryPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestDefaultRetryPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestDefaultRetryPolicy.java

## Purpose
`TestDefaultRetryPolicy` validates the default retry policy's action ordering and its handling of `RetriableException` directly or wrapped in `RemoteException`.

## Important APIs, Types, and Functions
The tests use `RetryPolicy.RetryAction.RetryDecision`, `RetryUtils.getDefaultRetryPolicy()`, `RetriableException`, and `RemoteException`. Assertions use AssertJ to inspect the returned `RetryAction.action`.

## Control Flow
`testRetryDecisionOrdering()` asserts enum ordering from `FAIL` to `RETRY` to `FAILOVER_AND_RETRY`. `testWithRetriable()` and `testWithWrappedRetriable()` construct an enabled default policy with spec `10000,6` and assert retry. `testWithRetriableAndRetryDisabled()` constructs the same spec with the enable flag false and asserts fail.

## State and Persistence
All state is local `Configuration` and policy instances. There is no filesystem or static mutation.

## Dependencies and Integration Points
This file tests retry decisions that are consumed by IPC and client code using Hadoop's default retry policy configuration. It integrates with `RemoteException` class-name unwrapping behavior.

## Risks and Edge Cases
The tests use retry count and failover count zero and idempotent flag true, so they do not cover exhaustion behavior across repeated attempts. They rely on enum ordering as a semantic contract.

## Test Signals
Signals are action ordering consistency, `RETRY` for direct/wrapped retriable exceptions when enabled, and `FAIL` when the default retry policy is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestDefaultRetryPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestFailoverProxy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestFailoverProxy.java

## Purpose
`TestFailoverProxy` validates dynamic proxy failover behavior when operations fail with ordinary exceptions, standby exceptions, IO exceptions, and remote exceptions.

## Important APIs, Types, and Functions
`FlipFlopProxyProvider<T>` alternates between two implementations and counts failovers. `FailOverOnceOnAnyExceptionPolicy` returns `FAILOVER_AND_RETRY` only before the first failover. Tests use `RetryProxy.create()`, `RetryPolicies.failoverOnNetworkException()`, `UnreliableInterface`, and `UnreliableImplementation.TypeOfExceptionToFailWith`. Nested `SynchronizedUnreliableImplementation` and `ConcurrentMethodThread` coordinate concurrent failure paths with `CountDownLatch`.

## Control Flow
Basic tests call methods that succeed once or ten times and then fail, proving policies either fail over or propagate. Network/standby tests verify failover only happens for standby exceptions or idempotent IO operations. The concurrency test forces two threads to fail on the same active proxy and asserts only one provider failover occurs. The multi-standby test repeatedly flips between two standby services until one implementation changes identifier after a delay.

## State and Persistence
State is in proxy provider active pointer, failover count, unreliable implementation invocation counters, latches, and thread results. No external persistence exists.

## Dependencies and Integration Points
The file integrates with Hadoop retry dynamic proxies, `FailoverProxyProvider`, idempotence annotations from `UnreliableInterface`, `StandbyException`, and retry policies used by HA clients.

## Risks and Edge Cases
Concurrency coverage depends on timing and latch coordination. The multi-standby test sleeps up to 10 seconds and depends on retry policy delay behavior. Non-idempotent IO failures must not be retried across failover because the operation may have side effects.

## Test Signals
Signals include expected active implementation strings, propagated exception messages when no failover should occur, exactly one failover under concurrent failures, eventual success after standby recovery, and IO exception propagation for expected non-failover cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestFailoverProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestRetryProxy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestRetryProxy.java

## Purpose
`TestRetryProxy` exercises `RetryProxy` and `RetryInvocationHandler` behavior for fixed, forever, exponential, exception-mapped, interruptible, and security-sensitive retry policies.

## Important APIs, Types, and Functions
The test creates proxies for `UnreliableInterface` backed by `UnreliableImplementation`. `setupMockPolicy()` wraps a mocked `RetryPolicy` so calls delegate to a real policy while capturing the returned `RetryAction`. It uses `RetryPolicies` factories, `RetryInvocationHandler.isRpcInvocation()`, `ProtocolTranslator`, `RemoteException`, `SaslException`, and `AccessControlException`.

## Control Flow
Each policy test invokes fixture methods with known failure counters and verifies success, failure, retry-call counts, and action reasons. Exception-mapping tests route fatal or remote exceptions to specific policies. `testRetryInterruptible()` runs a long-sleep retry in an executor, interrupts the sleeping thread, and expects `InterruptedIOException`. Security tests assert SASL and access-control failures do not retry beyond the initial decision.

## State and Persistence
Per-test state is a fresh `UnreliableImplementation` plus captured `caughtRetryAction`. Thread and executor state is created only for interrupt handling. No filesystem persistence is used.

## Dependencies and Integration Points
The suite depends on Mockito, Java reflection proxy behavior, Hadoop retry policies, `ProtocolTranslator` unwrapping, IPC `RemoteException`, and Hadoop security exceptions. It protects client retry semantics used throughout Hadoop RPC clients.

## Risks and Edge Cases
Mockito verification ties tests to exact `shouldRetry()` call counts. Interrupt timing includes a one-second sleep before interruption. Some fixture methods are annotated idempotent for retry testing even when not truly idempotent.

## Test Signals
Signals include correct retry/fail decisions and reason strings, successful retry for transient fixture failures, no retry for SASL/access-control exceptions, correct RPC proxy detection including translator wrappers, and immediate interrupt conversion to `InterruptedIOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestRetryProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/UnreliableImplementation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/UnreliableImplementation.java

## Purpose
`UnreliableImplementation` is a deterministic failure fixture for retry and failover tests. It implements `UnreliableInterface` with counters that fail or succeed in predictable sequences.

## Important APIs, Types, and Functions
The class tracks invocation counts for one-time, ten-time, SASL, access-control, and succeed-then-fail methods. `TypeOfExceptionToFailWith` selects `UNRELIABLE_EXCEPTION`, `STANDBY_EXCEPTION`, `IO_EXCEPTION`, or `REMOTE_EXCEPTION`. `throwAppropriateException()` maps that enum to the corresponding checked exception. `setIdentifier()` mutates the identifier used by failover tests.

## Control Flow
Methods either no-op, always throw, throw only until a counter threshold is crossed, or compare an incoming identifier to the instance identifier. Succeed-then-fail methods return the identifier until their success budget is exhausted, then throw the configured exception type.

## State and Persistence
All behavior depends on mutable in-memory counters, `identifier`, and `exceptionToFailWith`. There is no synchronization, persistence, or reset method beyond constructing a new instance.

## Dependencies and Integration Points
It depends on Hadoop `RemoteException`, `StandbyException`, `AccessControlException`, and Java `SaslException`/`IOException`. It is package-private and intended only for retry tests.

## Risks and Edge Cases
The fixture is not thread-safe except where subclasses add coordination. Counter state persists across method calls on the same instance, so tests must create fresh instances or account for prior calls. `failsWithWrappedAccessControlException()` wraps access control two layers deep, matching special unwrapping paths.

## Test Signals
Useful signals are predictable transition after first or tenth invocation, configured exception type and message, identifier comparison behavior, and mutable identifier recovery in failover tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/UnreliableImplementation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/UnreliableInterface.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/UnreliableInterface.java

## Purpose
`UnreliableInterface` defines the method surface used by retry and failover tests to simulate controlled transient, fatal, remote, security, and idempotent failures.

## Important APIs, Types, and Functions
Nested `UnreliableException` carries an optional identifier message. `FatalException` extends it for exception-mapping tests. Methods cover always-success, fatal failures, remote fatal failures, one-time IO/remote/unreliable failures, ten-time failures, SASL failures, access-control failures, succeed-then-fail string methods, identifier matching, and non-idempotent void failure.

## Control Flow
The interface itself has no flow, but its method signatures and `@Idempotent` annotations drive `RetryInvocationHandler` decisions in tests. Annotated methods include access-control cases, wrapped access control, idempotent succeed-then-fail, and identifier matching.

## State and Persistence
The interface declares no state. Implementations supply counters and identifiers.

## Dependencies and Integration Points
It depends on `Idempotent`, Hadoop IPC `RemoteException` and `StandbyException`, Hadoop security `AccessControlException`, and Java `SaslException`/`IOException`. It is the core contract used by `TestRetryProxy` and `TestFailoverProxy`.

## Risks and Edge Cases
Comments explicitly note that some annotated methods are not actually idempotent; the annotation is used to test retry decisions. `UnreliableException.getMessage()` returns the identifier and may be null.

## Test Signals
Signals are correct reflection of `@Idempotent` annotations, exception typing in proxy invocation, and method signatures that let retry handlers distinguish safe failover from unsafe retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/UnreliableInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/SerializationTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/SerializationTestUtil.java

## Purpose
`SerializationTestUtil` provides a generic round-trip helper for Hadoop serialization tests.

## Important APIs, Types, and Functions
`testSerialization(Configuration conf, K before)` builds a `SerializationFactory`, obtains a `Serializer` and `Deserializer` for `GenericsUtil.getClass(before)`, writes into `DataOutputBuffer`, reads from `DataInputBuffer`, and returns the deserialized object.

## Control Flow
The helper opens the serializer, serializes the input, closes it, resets an input buffer over the output bytes, opens the deserializer, deserializes into a null reuse object, closes it, and returns the result.

## State and Persistence
All state is in heap buffers and local serializer/deserializer instances. No files are created.

## Dependencies and Integration Points
It integrates with Hadoop `SerializationFactory`, `Serializer`, `Deserializer`, `DataOutputBuffer`, `DataInputBuffer`, and `GenericsUtil`. Tests for Writable and Avro serialization reuse it.

## Risks and Edge Cases
The method assumes the factory can resolve both serializer and deserializer; otherwise null dereferences will fail the caller. It uses the runtime class of `before`, so null inputs are unsupported.

## Test Signals
Success means factory lookup, stream lifecycle, serialized bytes, and deserialization all produce an object equal to the original in caller tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/SerializationTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/TestSerializationFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/TestSerializationFactory.java

## Purpose
`TestSerializationFactory` verifies robust construction and lookup behavior for `SerializationFactory` under empty, unset, invalid, and whitespace-padded configuration values.

## Important APIs, Types, and Functions
The suite uses `CommonConfigurationKeys.IO_SERIALIZATIONS_KEY`, `SerializationFactory.getSerializer()`, `getDeserializer()`, `Writable`, `LongWritable`, and `WritableSerialization`. A static block sets factory logging to trace for diagnostics.

## Control Flow
`setup()` creates a default configuration and factory once. Individual tests construct factories with empty, unset, or invalid serialization keys and expect no construction error. Serializer/deserializer lookup tests assert default Writable support and null results for unsupported test classes. The trimming test sets the serialization class name with surrounding spaces and verifies lookup still works.

## State and Persistence
State is limited to static test `Configuration` and `SerializationFactory` instances. No persistent files are used.

## Dependencies and Integration Points
It protects configuration parsing for Hadoop's `io.serializations` setting and default Writable serialization registration.

## Risks and Edge Cases
The invalid-key test only asserts construction does not throw; it does not assert logging or lookup behavior after invalid entries. Static factory reuse means later changes to `conf` would affect shared state if added.

## Test Signals
Signals are no construction failures for malformed serialization config, non-null Writable serializer/deserializer, null unsupported lookup, and trimming of configured class names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/TestSerializationFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/TestWritableSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/TestWritableSerialization.java

## Purpose
`TestWritableSerialization` validates Hadoop Writable serialization, Configurable propagation, and Java serialization of a `WritableComparator` subclass.

## Important APIs, Types, and Functions
The tests use `SerializationTestUtil`, `Text`, `TestGenericWritable.FooGenericWritable`, `Baz`, `CONF_TEST_KEY`, `CONF_TEST_VALUE`, `JavaSerialization`, `DataOutputBuffer`, `DataInputBuffer`, and nested `TestWC extends WritableComparator implements Serializable`.

## Control Flow
`testWritableSerialization()` round-trips a `Text`. `testWritableConfigurable()` sets a configuration value, creates a configurable generic writable fixture, then round-trips `Baz` and asserts equality plus non-null configuration on the result. `testWritableComparatorJavaSerialization()` manually serializes and deserializes `TestWC` through `JavaSerialization` and compares equality.

## State and Persistence
State is an in-memory static `Configuration` and byte buffers. No files are created.

## Dependencies and Integration Points
The file integrates Writable serialization, Configurable object initialization, Java object serialization, and comparator serializability.

## Risks and Edge Cases
The static `Configuration` is mutated in one test and shared across the class. `TestWC` equality depends only on `val`, and the default constructor gives a different value to ensure deserialized state is actually read.

## Test Signals
Signals are equal round-tripped `Text` and `Baz`, configuration propagation into deserialized configurable writables, and Java serialization preserving custom comparator field state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/TestWritableSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/avro/Record.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/avro/Record.java

## Purpose
`Record` is a simple public POJO used by Avro reflection serialization tests.

## Important APIs, Types, and Functions
The class exposes one public integer field `x`, defaulting to 7. `hashCode()` returns `x`, and `equals(Object)` compares class equality and `x` value.

## Control Flow
There is no active control flow beyond equality checks. Test code mutates `x` and uses equality after serialization round trips.

## State and Persistence
State is the public `x` field. Persistence is only through external serializers in tests.

## Dependencies and Integration Points
It lives in the Avro serializer test package so `AvroReflectSerialization.AVRO_REFLECT_PACKAGES` can include its package name and accept it for reflection serialization.

## Risks and Edge Cases
The public mutable field and no-arg default shape are intentionally simple for Avro reflection. Equality rejects subclasses through exact class comparison.

## Test Signals
The main signal is equality after Avro reflection serialization when `x` is changed from its default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/avro/Record.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/avro/TestAvroSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/avro/TestAvroSerialization.java

## Purpose
`TestAvroSerialization` validates Hadoop Avro serialization for specific records, reflection-configured POJOs, inner classes, and marker-interface reflect serializables.

## Important APIs, Types, and Functions
Tests use `AvroRecord`, `Record`, `AvroReflectSerialization.AVRO_REFLECT_PACKAGES`, `SerializationTestUtil`, `SerializationFactory`, nested `InnerRecord`, and nested `RefSerializable implements AvroReflectSerializable`.

## Control Flow
`testSpecific()` round-trips a generated specific Avro record. `testReflectPkg()` sets the reflect package configuration and round-trips `Record`. `testAcceptHandlingPrimitivesAndArrays()` asserts byte arrays and primitive byte do not get serializers. `testReflectInnerClass()` verifies reflect package matching for a nested class. `testReflect()` verifies marker-interface-based reflect serialization without package configuration.

## State and Persistence
The static `Configuration` is mutated to set reflect packages and reused across tests. Serialization state stays in memory through `SerializationTestUtil`.

## Dependencies and Integration Points
The file integrates Hadoop serialization factory lookup with Avro specific and reflect serialization modes. It tests primitive/array rejection to avoid inappropriate Avro acceptance.

## Risks and Edge Cases
Static configuration reuse can leak reflect package settings across tests, though all tests remain compatible with that setting. Equality for reflect classes compares exact class and `x`.

## Test Signals
Signals are equality after specific and reflect round trips, null serializers for unsupported primitive/array types, and successful reflect handling for nested and marker-interface classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/avro/TestAvroSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/wrappedio/impl/TestWrappedIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/wrappedio/impl/TestWrappedIO.java

## Purpose
`TestWrappedIO` validates dynamic/reflection-based access to newer Hadoop filesystem APIs through `DynamicWrappedIO`, ensuring callers can use open-file, stream capability, byte-buffer positioned reads, and bulk delete features while degrading safely when methods are absent.

## Important APIs, Types, and Functions
The test uses `DynamicWrappedIO`, `DynamicWrappedStatistics`, `WrappedIO.streamCapabilities_hasCapability()`, `FileSystem.openFile` wrappers, `CommonPathCapabilities.BULK_DELETE`, `FS_OPTION_OPENFILE_LENGTH`, `FS_OPTION_OPENFILE_READ_POLICY`, `ByteBufferPositionedReadable` wrappers, and local filesystem contract utilities. Helper `openFile()` delegates to `io.fileSystem_openFile()`, and `map()` builds string option maps.

## Control Flow
Setup initializes the local filesystem contract, wrapped I/O, statistics wrapper, and statistics context. `testOpenFileOperations()` creates a file, opens it through multiple wrapper paths, checks read policy and length options, validates EOF behavior beyond file length, probes stream capabilities, aggregates I/O stats, and performs bulk delete. `testByteBufferPositionedReadable()` verifies direct and wrapped positioned byte-buffer reads when available, otherwise expects unsupported operation. Fallback tests bind to nonexistent or incompatible classes and assert probes return false or operations throw expected exceptions.

## State and Persistence
Temporary files are created through the local filesystem contract and deleted by test cleanup or bulk delete. I/O statistics snapshots are created, aggregated, optionally saved, and logged. Thread-local IOStatisticsContext is reset during setup.

## Dependencies and Integration Points
It integrates local FS contract testing, dynamic binding utilities, stream capabilities, filesystem bulk delete APIs, open-file builder options, and wrapped statistics. This protects compatibility shims used by downstream code that must run against multiple Hadoop versions.

## Risks and Edge Cases
Reflection binding must distinguish missing methods, non-static methods, and unavailable class names. Local filesystem may not support byte-buffer positioned reads, so that branch intentionally accepts unsupported behavior. The EOF validation depends on stream semantics around seeking past known length.

## Test Signals
Signals include successful dynamic method discovery, correct first-byte reads from wrapped open calls, matching stream capability probes, expected EOF and FileNotFound exceptions, positive bulk delete page size, empty bulk delete failures list, and safe fallback behavior when wrapped classes or methods are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/wrappedio/impl/TestWrappedIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/wrappedio/impl/TestWrappedStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/wrappedio/impl/TestWrappedStatistics.java

## Purpose
`TestWrappedStatistics` verifies dynamic access to Hadoop IOStatistics, IOStatisticsSnapshot, JSON persistence, and IOStatisticsContext operations through `DynamicWrappedStatistics`.

## Important APIs, Types, and Functions
The suite uses `DynamicWrappedStatistics`, `IOStatisticsContext`, `IOStatisticsSnapshot`, `IOStatisticsStore`, `IOStatisticsBinding.iostatisticsStore()`, `trackDurationOfInvocation()`, `FileSystem.getLocal()`, and local JSON paths. It exercises wrapper methods for availability probes, type predicates, snapshot create/retrieve/aggregate, JSON string conversion, save/load, pretty printing, maps of counters/gauges/minimums/maximums/means, and context set/reset/snapshot/aggregate.

## Control Flow
Setup creates a local filesystem and a `snapshot.json` path. Tests first validate method availability and error handling for null or wrong serializable types. Context tests get the current context, snapshot it, JSON round-trip it, reset and restore thread-local context, and aggregate snapshots. Extraction tests build a statistics store with counters, gauges, and duration tracking, then verify persisted JSON and extracted metric maps. Missing-method tests bind to an empty stub class and assert probes downgrade while operations throw `UnsupportedOperationException`.

## State and Persistence
Temporary JSON snapshots are saved to and loaded from the local filesystem. IOStatisticsContext is thread-local and is reset or replaced in tests. Statistics store state is in-memory until serialized.

## Dependencies and Integration Points
The file integrates dynamic reflection wrappers with Hadoop filesystem statistics APIs, local filesystem persistence, and duration tracking. It protects compatibility for code that optionally uses IOStatistics when present.

## Risks and Edge Cases
Tests intentionally pass wrong types to validate argument checking. Duration minimums and maximums depend on wall-clock sleep timing and may vary, so assertions focus on positive and relational values. Missing-method simulation must not accidentally bind inherited methods.

## Test Signals
Signals include true availability on current runtime, correct type predicates, JSON equality after round trip, expected exceptions for bad inputs and overwrite/load failures, doubled counter aggregation in context, extracted counter/gauge/duration maps, and clean unsupported-operation behavior for missing bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/wrappedio/impl/TestWrappedStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/MiniRPCBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/MiniRPCBenchmark.java

## Purpose
`MiniRPCBenchmark` is a standalone benchmark that measures the time to establish Hadoop RPC sessions under simple, Kerberos, or delegation-token authentication.

## Important APIs, Types, and Functions
The file defines `MiniProtocol`, a protobuf RPC interface annotated with `@KerberosInfo`, `@TokenInfo`, and `@ProtocolInfo`; `MiniServer`, a one-handler RPC server using `ProtobufRpcEngine2`; and `TestDelegationTokenSelector`. Benchmark methods include `connectToServer()`, `connectToServerAndGetDelegationToken()`, `connectToServerUsingDelegationToken()`, `runMiniBenchmark()`, `runMiniBenchmarkWithDelegationToken()`, and `configureSuperUserIPAddresses()`.

## Control Flow
`main()` parses iteration count, optional keytab, principal, token mode, and log level. Non-token mode starts `MiniServer`, warms up one connection, then repeatedly creates and stops RPC proxies while summing elapsed time. Token mode configures proxy-user groups/IPs, starts the server, obtains a delegation token as a proxy user, adds it to `currentUgi`, then times connections under that token identity.

## State and Persistence
Runtime state includes `currentUgi`, benchmark log level, RPC server instance, delegation token secret manager threads, and configuration entries. No benchmark results are persisted; they are printed to standard output.

## Dependencies and Integration Points
It integrates Hadoop RPC, Protobuf services, UGI login/keytab handling, delegation token secret manager/test identifier, impersonation provider configuration, token service binding, network interface enumeration, and Hadoop logging utilities.

## Risks and Edge Cases
Kerberos mode requires valid keytab/principal configuration. Delegation token mode depends on proxy-user IP enumeration and local host naming. `connectToServerUsingDelegationToken()` prints interrupted exceptions instead of failing hard, which can hide interruption. Average connect time includes proxy creation and server-side authentication but not application RPC payload work.

## Test Signals
Signals are successful server startup, proxy creation and shutdown across all iterations, token acquisition and token-authenticated proxy creation, printed average connection time, and absence of authentication/impersonation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/MiniRPCBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/RPCCallBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/RPCCallBenchmark.java

## Purpose
`RPCCallBenchmark` is a command-line protobuf RPC throughput benchmark. It can run a server, clients, or both, and reports calls per second plus CPU time per call.

## Important APIs, Types, and Functions
`MyOptions` parses CLI flags for server handlers, reader threads, client threads, message size, runtime, host, port, and RPC engine. `startServer()` builds a protobuf `RPC.Server` with `TestRpcService`. `setupClientTestContext()` creates one proxy per client thread identity and repeating test threads. `RpcServiceWrapper` abstracts the echo call. `createRpcClient()` builds a `TestRpcService` proxy and sends `EchoRequestProto`.

## Control Flow
`run()` parses options, sets the protocol engine, starts a server if requested, starts client test threads if requested, prints per-second throughput for the configured duration, then prints aggregate throughput and client/server CPU nanoseconds per call. If only a server is requested, it sleeps indefinitely until externally stopped. `main()` invokes the tool through `ToolRunner`.

## State and Persistence
State includes `Configuration`, an atomic per-second `callCount`, server handler threads, client proxy array, generated echo message, and thread CPU counters from `ThreadMXBean`. Results are printed, not persisted.

## Dependencies and Integration Points
The benchmark depends on Apache Commons CLI, Hadoop `Tool`, `RPC`, `ProtobufRpcEngine2`, test protobuf services, `MultithreadedTestUtil`, UGI test users, and `NetUtils` free-port selection.

## Risks and Edge Cases
At least one of server or client threads must be specified. Server-only mode never exits by itself. CPU time reporting depends on JVM thread CPU support and can be affected by thread lifecycle. The only accepted engine option is `protobuf`.

## Test Signals
Signals are successful option validation, server bind/start, client echo loops, increasing call counts, per-second and aggregate throughput output, and clean server stop when clients finish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/RPCCallBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestAsyncIPC.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestAsyncIPC.java

## Purpose
`TestAsyncIPC` verifies Hadoop IPC client's asynchronous call modes, async call limit enforcement, response future reuse, timeout handling, call-id/retry propagation, and `CompletableFuture` integration.

## Important APIs, Types, and Functions
The tests use `Client.setAsynchronousMode()`, `Client.getAsyncRpcResponse()`, `Client.getResponseFuture()`, `AsyncGetFuture`, `AsyncCallLimitExceededException`, `Client.setCallIdAndRetryCount()`, `Server.getCallId()`, `Server.getCallRetryCount()`, and `TestIPC.TestServer`. Nested caller classes are `AsyncCaller`, `AsyncCompletableFutureCaller`, and `AsyncLimitlCaller`.

## Control Flow
`setupConf()` enables high async-call capacity and async mode on the main thread. `internalTestAsyncCall()` starts a test server, creates clients, starts callers that issue async RPCs and store futures, then validates returned `LongWritable` values. Limit tests catch `AsyncCallLimitExceededException`, wait for prior futures, and resume. Call-id tests override `Client.createCall()` or install server listeners to validate retry counts in request and response headers. The CompletableFuture test delays server handling and verifies sending ten async calls is faster than sequential processing.

## State and Persistence
State is in client async counters, per-caller future maps/lists, expected value maps/lists, server listener callbacks, call-id maps, and temporary server/client threads. No files are persisted.

## Dependencies and Integration Points
The file integrates core IPC `Client`, `Server`, RPC headers, `TestIPC` test server, Hadoop `LongWritable`, `AsyncGetFuture`, `CompletableFuture`, `SubjectInheritingThread`, and IPC config key `IPC_CLIENT_ASYNC_CALLS_MAX_KEY`.

## Risks and Edge Cases
Async mode is thread-local, so caller threads explicitly re-enable it. Limit tests depend on server and handler timing. Sequential call-id validation sorts server-observed IDs because execution order is not guaranteed. `AsyncLimitlCaller` name contains a typo but behavior is clear.

## Test Signals
Signals are all futures resolving to sent values, async counter returning to its original count, timeout polling eventually completing, limit exceptions handled without lost calls, matching retry counts on server and response, unique sequential call IDs across 10,000 concurrent calls, and fast non-blocking CompletableFuture submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestAsyncIPC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestCallQueueManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestCallQueueManager.java

## Purpose
`TestCallQueueManager` validates queue capacity, scheduler compatibility, queue swapping under contention, fair-call-queue capacity weights, constructor error propagation, overflow exception semantics, and failover-on-overflow configuration.

## Important APIs, Types, and Functions
The test defines `FakeCall implements Schedulable`, `Putter`, and `Taker`. It uses `CallQueueManager`, `LinkedBlockingQueue`, `FairCallQueue`, `DefaultRpcScheduler`, `DecayRpcScheduler`, `RpcScheduler`, `CallQueueOverflowException`, and `Server.getSchedulerClass()`. Helpers `assertCanPut()` and `assertCanTake()` test bounded queue behavior.

## Control Flow
Basic tests construct managers with different queue/scheduler classes and assert capacity or empty-consume behavior. Compatibility tests ensure selecting `FairCallQueue` without an explicit scheduler defaults to `DecayRpcScheduler`, and that `DecayRpcScheduler` also works with `LinkedBlockingQueue`. `testSwapUnderContention()` runs 1000 producers and 100 consumers while swapping queues five times, then verifies no calls were dropped. Overflow tests use Mockito to verify backoff, add/put paths, and failover-triggering exceptions.

## State and Persistence
State is entirely in in-memory queues, fake call priority levels, producer/consumer counters, and manager flags. No persistent state is used.

## Dependencies and Integration Points
The suite integrates server IPC configuration keys, scheduler and queue reflection conversion helpers, UGI on schedulable calls, fair queue capacity weights, and client backoff/failover signaling used by RPC servers.

## Risks and Edge Cases
The contention test is timing-heavy and starts many threads. Capacity assertions use short joins and interrupts to infer blocking behavior. Overflow tests rely on exact Mockito interactions with `put()` versus `add()`.

## Test Signals
Signals include exact number of accepted puts/takes under capacity, correct default scheduler selection, no lost calls across queue swaps, expected priority dequeue order under capacity weights, constructor exceptions preserving causes, overflow exception class selection, and namespace/global failover config flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestCallQueueManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestCallerContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestCallerContext.java

## Purpose
`TestCallerContext` verifies construction of caller context strings, key/value append behavior, append-if-absent semantics, and separator validation.

## Important APIs, Types, and Functions
The tests use `CallerContext.Builder`, `CallerContext.getContext()`, and configuration key `HADOOP_CALLER_CONTEXT_SEPARATOR_KEY`. They exercise `append(String)`, `append(String, String)`, `appendIfAbsent(String, String)`, and `build()`.

## Control Flow
Tests configure `$` as the separator, append raw context entries and key/value entries, split the resulting context, and verify expected order. `appendIfAbsent` first refuses to replace an existing key, then appends missing keys including a key that is a substring of existing keys. The final test sets a tab separator and expects `IllegalArgumentException` during build.

## State and Persistence
State is local to the builder and resulting `CallerContext`. No filesystem or global state is persisted.

## Dependencies and Integration Points
Caller contexts are propagated through Hadoop IPC for audit and tracing. This test protects separator parsing and duplicate-key behavior configured through core-site keys.

## Risks and Edge Cases
The separator can itself appear in appended values; the test documents the raw concatenation behavior by appending `$$`. Append-if-absent must match whole keys, not substrings.

## Test Signals
Signals are exact context strings, correct number of separated items, preservation of original key values, append of substring keys as distinct entries, and rejection of illegal separators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestCallerContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestDecayRpcScheduler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestDecayRpcScheduler.java

## Purpose
`TestDecayRpcScheduler` validates configuration parsing, decaying call-volume accounting, priority assignment, metrics/JMX summaries, weighted cost providers, service-user exemptions, and initialization safety for `DecayRpcScheduler`.

## Important APIs, Types, and Functions
The file uses `DecayRpcScheduler`, `Schedulable`, `IdentityProvider`, `CostProvider`, `WeightedTimeCostProvider`, `ProcessingDetails`, `DefaultMetricsSystem`, JMX `MBeanServer`, and JSON parsing. Helpers include `mockCall(String)`, `TestIdentityProvider`, `TestCostProvider`, `getSchedulerWithWeightedTimeCostProvider()`, and `getPriorityIncrementCallCount()`.

## Control Flow
Constructor tests reject nonpositive priority levels. Parsing tests validate default and namespace-specific period, factor, thresholds, and port-less provider configuration. Accumulation and decay tests add calls by identity, force decay, and assert call snapshots shrink and remove zero entries. Priority tests verify threshold-based levels and JMX call-volume summaries before and after decay. Weighted-cost tests rank callers by lock timing cost, then verify decay restores high priority after many cycles. Service-user tests assert configured service users remain priority zero and are accounted separately from normal users.

## State and Persistence
Scheduler state includes decaying per-identity call-cost maps, raw totals, service-user totals, priority cache after decay, metrics registration, and background periodic decay timers. No filesystem persistence is used.

## Dependencies and Integration Points
The tests integrate RPC scheduling config keys, metrics system initialization, JMX MBean attributes, Jetty JSON parsing, UGI identity extraction, and processing-detail timing categories used by server call accounting.

## Risks and Edge Cases
Periodic decay uses real sleeps and a two-second timeout. Metrics/JMX object names depend on namespace uniqueness. Some tests use deprecated FCQ-prefixed config keys to protect backward compatibility. Weighted duration assertions avoid exact timings but still depend on relative cost formulas.

## Test Signals
Signals include expected parse defaults and overrides, exact decayed totals, threshold-derived priority levels, valid JMX JSON summaries, no initialization `NullPointerException` with metrics already monitoring, weighted-cost priority ordering, zero-cost calls staying equal, service users excluded from normal-user totals, and service users always receiving priority zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestDecayRpcScheduler.java -->
