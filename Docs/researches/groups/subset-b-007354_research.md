# Research: subset-b-007354

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/IOUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/IOUtils.java

Purpose: `IOUtils` is Hadoop common's general-purpose I/O helper class. It centralizes byte-copy loops, exact-read/skip behavior, cleanup helpers, channel write loops, directory listing with propagated errors, durable fsync helpers, exception wrapping, and conversion of `DataInput` content to a byte array.

Important APIs and types: `copyBytes(...)` has overloads for explicit buffer sizes, `Configuration`-driven buffer sizes, optional close semantics, and bounded byte counts. `readFully()` and `skipFully()` enforce exact consumption or throw. `wrappedReadForCompressedData()` normalizes decompressor/runtime failures into `IOException`. `cleanupWithLogger()`, `closeStream()`, `closeStreams()`, and `closeSocket()` suppress cleanup failures. `NullOutputStream` discards writes. `writeFully(WritableByteChannel, ByteBuffer)` and `writeFully(FileChannel, ByteBuffer, long)` handle short writes. `listDirectory()`, `fsync(File)`, `fsync(FileChannel, boolean)`, `wrapException()`, and `readFullyToByteArray()` cover filesystem and diagnostic utility behavior.

Control flow: copy helpers loop until EOF or the requested byte count is consumed, optionally closing both streams in a `finally` path. Exact-read/skip helpers repeatedly read or skip and detect premature EOF. `fsync(File)` verifies existence, skips directory fsync on Windows, opens a channel with directory/read or file/write mode, then delegates to channel force. `wrapException()` preserves interrupted/path exceptions, otherwise tries to recreate the original exception class with a richer message before falling back to `PathIOException`.

State and persistence: the class is stateless except for its logger. Persistence effects are side effects on caller-owned streams, channels, sockets, directories, and files. `fsync` explicitly attempts to flush file or directory metadata/data to storage.

Dependencies and integration points: integrates with Hadoop `Configuration`, common IO buffer config keys, `PathIOException`, platform detection via `Shell`, Java NIO files/channels, and SLF4J. It is used by many Hadoop IO classes for cleanup, exact reads, and safe copying.

Risks and test signals: risks include infinite loops if a nonblocking channel reports zero bytes while `ByteBuffer` remains, close-suppression hiding primary cleanup failures when misused outside exception paths, `copyBytes` closing caller streams unexpectedly through the close overloads, and `readFullyToByteArray` being unsafe for unbounded inputs. Test signals should cover short reads/writes, `PrintStream.checkError`, premature EOF, skip returning zero, directory iterator exceptions, platform-specific fsync behavior, and exception wrapping for subclasses with and without string constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/IOUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/InputBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/InputBuffer.java

Purpose: `InputBuffer` is a reusable `FilterInputStream` over caller-supplied byte arrays. It avoids allocating a new `ByteArrayInputStream` for repeated in-memory reads.

Important APIs and types: the private `Buffer` subclass extends `ByteArrayInputStream` and exposes `reset(byte[] input, int start, int length)`, `getPosition()`, and `getLength()`. Public `InputBuffer.reset(byte[], int)` and `reset(byte[], int, int)` retarget the stream to new data, while `getPosition()` and `getLength()` expose the underlying `pos` and `count`.

Control flow: construction creates an empty `Buffer` and passes it to `FilterInputStream`. Each reset swaps the `ByteArrayInputStream` backing `buf`, sets `count` to `start + length`, and resets `mark` and `pos` to `start`, so subsequent inherited `read`, `skip`, `available`, and mark/reset behavior operates on the new byte range.

State and persistence: state is in-memory only: the current backing array reference, start/mark, position, and limit. It does not copy input bytes, so later mutation of the caller's byte array affects reads. There is no persistence or close-owned resource beyond the filter stream wrapper.

Dependencies and integration points: depends only on Java IO plus Hadoop audience/stability annotations. It is paired with `DataInputBuffer` and `OutputBuffer` and is suitable for HDFS/MapReduce internal serialization paths that repeatedly decode transient byte arrays.

Risks and test signals: risks include exposing mutable input without copying, accepting invalid `start + length` combinations until inherited read paths encounter array bounds behavior, and confusing `getLength()` because it returns the absolute limit (`count`), not remaining bytes. Tests should cover resets with nonzero starts, position movement after reads/skips, reuse across multiple arrays, and caller mutation visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/InputBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/IntWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/IntWritable.java

Purpose: `IntWritable` is Hadoop's stable `WritableComparable` wrapper for a Java `int`, used as a serialized key or value in Hadoop IO, SequenceFile, MapReduce, and RPC-facing data structures.

Important APIs and types: the mutable `value` field is managed through constructors, `set(int)`, and `get()`. `readFields(DataInput)` reads one four-byte integer and `write(DataOutput)` writes one four-byte integer. `equals`, `hashCode`, `compareTo`, and `toString` implement value semantics. Nested `Comparator` extends `WritableComparator` to compare serialized forms directly with `readInt`.

Control flow: normal object serialization is a direct `readInt`/`writeInt` pair. Sorting can bypass object creation through the registered raw comparator, which reads the two integer values from byte slices and returns the same ordering as `compareTo`.

State and persistence: the only state is the mutable primitive value. Persistence is Hadoop Writable binary format: exactly four bytes in `DataOutput` order. Static initialization registers the optimized comparator globally with `WritableComparator`.

Dependencies and integration points: depends on `WritableComparable` and `WritableComparator`. It is a common key type for SequenceFile/MapFile and MapReduce sort/shuffle paths where raw comparators matter for performance.

Risks and test signals: risks are low but include mutation after insertion into hash collections, comparator misuse with slices shorter than four bytes, and hash distribution matching integer identity. Tests should check binary round trips, raw comparator ordering for negative/positive/boundary values, equality/hash consistency, and registration with `WritableComparator.get`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/IntWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/LongWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/LongWritable.java

Purpose: `LongWritable` is Hadoop's stable `WritableComparable` wrapper for a Java `long`, providing binary serialization and optimized raw comparison for long-valued keys and values.

Important APIs and types: mutable `value` is controlled by constructors, `set(long)`, and `get()`. `readFields`/`write` use `DataInput.readLong` and `DataOutput.writeLong`. `compareTo`, `equals`, `hashCode`, and `toString` provide object semantics. Nested `Comparator` reads long values directly from serialized bytes; `DecreasingComparator` reverses both object and raw byte ordering.

Control flow: serialization writes or reads one eight-byte value. Default sort paths use the registered `Comparator`. Callers needing descending order can explicitly use `DecreasingComparator`, which swaps operands before delegating to the normal comparator.

State and persistence: state is a single mutable `long`. Persistent representation is exactly eight bytes. Static initialization registers the ascending comparator as the default for `LongWritable`.

Dependencies and integration points: integrates with `WritableComparable`, `WritableComparator`, SequenceFile/MapFile ordering, and MapReduce sort/grouping. It is also used internally by `MapFile` index entries to store byte positions.

Risks and test signals: notable risk is `hashCode()` truncating to the low 32 bits, which is compatible but collision-prone for patterned long values. Mutation after map/set insertion has the usual mutable-key hazard. Tests should cover round trips, raw and object comparison equivalence, decreasing comparator behavior, boundary values, and hash/equality consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/LongWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MD5Hash.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MD5Hash.java

Purpose: `MD5Hash` is a stable `WritableComparable` representation of a 16-byte MD5 digest, with helpers for digest creation, hex conversion, partial numeric digest extraction, equality, hashing, and raw byte comparison.

Important APIs and types: `MD5_LEN` fixes digest length. A thread-local `MessageDigest` avoids repeated MD5 construction. Constructors create zeroed, hex-derived, or byte-array-backed hashes. `readFields`, `write`, and static `read` implement Writable format. `digest(...)` overloads hash byte arrays, `InputStream`, `String`, `UTF8`, and arrays of byte arrays. `halfDigest()` and `quarterDigest()` expose the first 8 or 4 bytes as numeric values. Nested `Comparator` compares serialized digest bytes directly.

Control flow: digest helpers reset a thread-local `MessageDigest`, update it with the requested data, and wrap the resulting 16 bytes. Hex parsing validates 32 characters and converts each nibble; `toString()` emits lowercase hex. Writable reads fill the existing digest array and writes emit the raw 16 bytes.

State and persistence: each instance holds a mutable `byte[] digest`; the byte-array constructor stores the caller's array rather than copying it, and `getDigest()` exposes that array. Persistent representation is exactly the 16 digest bytes. The static comparator registration affects Hadoop's global Writable comparator registry.

Dependencies and integration points: depends on Java security `MessageDigest`, Hadoop `UTF8`, `WritableComparator`, and `WritableComparable`. It is suitable for file checksums, partitioning keys, and compact hash IDs inside Hadoop serialization.

Risks and test signals: MD5 is not collision-resistant for adversarial security use, so callers must not use it as a modern trust primitive. Additional risks include mutable digest aliasing, unchecked `RuntimeException` for bad hex characters, and `digest(byte[][], start, len)` applying the same slice to every array. Tests should cover hex round trips, invalid length/characters, stream hashing, comparator ordering, exposed-array mutation, and digest equality/hash behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MD5Hash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MapFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MapFile.java

Purpose: `MapFile` implements a persistent sorted map stored as a directory with a `data` `SequenceFile` containing all key/value pairs and an `index` `SequenceFile` containing sparse key-to-byte-position entries. It supports sorted append, indexed lookup, closest-key search, repair of missing indexes, merge of compatible map files, rename/delete utilities, and a copy-style CLI.

Important APIs and types: constants `INDEX_FILE_NAME` and `DATA_FILE_NAME` define the on-disk layout. `Writer` owns data/index `SequenceFile.Writer`s, comparator/key class options, index interval state, last-key order checks, and index position tracking. `Reader` owns data/index readers, comparator, lazy in-memory index arrays, seek cache, and lookup methods (`seek`, `next`, `get`, `getClosest`, `midKey`, `finalKey`, `reset`). Static `rename`, `delete`, and `fix` manage map directories. `Merger` merges multiple sorted MapFiles with identical key/value classes.

Control flow: `Writer` creates the map directory, opens data and block-compressed index files, verifies appended keys are nondecreasing by serializing a copy of the last key, writes an index entry every configured interval when the data byte position advances, then appends to the data file. `Reader` opens data and index files, lazily reads the index into memory, optionally skipping configured index entries, checks index ordering, then uses binary search to seek to the closest indexed position before linearly scanning data records to satisfy exact or closest lookups. `fix` rebuilds a missing index by scanning data and following the writer's index interval/position rules. `Merger` keeps one current key/value per reader, repeatedly chooses the smallest key, appends it, and advances that reader.

State and persistence: persistent state is the directory containing `data` and `index`. The index is sparse and fully loaded into reader memory on first indexed operation. Reader seek state (`seekIndex`, `seekPosition`, `nextKey`) caches locality between seeks. Writer state tracks append count, last index position, and copied last key. No transactional metadata is added beyond SequenceFile contents.

Dependencies and integration points: tightly integrates with `SequenceFile`, `Writable`, `WritableComparable`, `WritableComparator`, `LongWritable`, `DataInputBuffer`, `DataOutputBuffer`, Hadoop `FileSystem`/`Path`, compression options, `Options`, `ReflectionUtils`, and common config keys `io.map.index.interval` and `io.map.index.skip`. It is a storage primitive for older Hadoop components needing sorted local or distributed key/value files.

Risks and test signals: risks include corrupted or missing index/data divergence, high memory use from loading large indexes, comparator/key-class mismatch, mutable key reuse errors, duplicate keys producing ambiguous lookup semantics, suppressed truncation exceptions in `fix`, non-atomic directory create/rename workflows, and merge output ordering when inputs contain overlapping keys. Tests should cover sorted and out-of-order appends, first/middle/final key lookup, `getClosest` before/after edges, index skip behavior, block-compressed files with repeated positions, missing-index repair dry run and write modes, merge class validation, empty MapFiles, and delete/rename failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MapFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MapWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MapWritable.java

Purpose: `MapWritable` is a stable Writable `Map<Writable, Writable>` implementation that serializes heterogeneous Writable key and value classes by pairing map entries with class IDs maintained by `AbstractMapWritable`.

Important APIs and types: the class wraps a `HashMap<Writable, Writable>` and implements normal `Map` operations. `put` registers both key and value classes before insertion. `write` emits the superclass class table, entry count, then for each entry writes key class ID, key payload, value class ID, and value payload. `readFields` reads the class table, clears existing entries, instantiates key/value objects by ID via `ReflectionUtils`, reads their fields, and inserts them.

Control flow: mutations generally delegate to the backing map, with `put` and `putAll` adding class metadata. Serialization always starts with the class mapping inherited from `AbstractMapWritable`; deserialization rebuilds the mapping first, then reconstructs each object from class IDs embedded in the stream.

State and persistence: state includes the backing `HashMap` plus inherited class-ID mappings and optional configuration. Persistent representation is class mapping metadata followed by all entries in backing-map iteration order. Entry order is not stable because `HashMap` does not preserve order.

Dependencies and integration points: depends on `AbstractMapWritable`, `Writable`, `ReflectionUtils`, and Hadoop configuration propagation. It integrates with Hadoop RPC and serialization paths that need maps containing multiple Writable implementations.

Risks and test signals: risks include mutable Writable keys breaking hash lookups, nondeterministic serialized entry order, failure on unknown or non-instantiable classes, and class table drift if entries are mutated through collection views in ways that bypass `put`. Tests should cover heterogeneous round trips, copy construction, clearing before repeated reads, class registration through `putAll`, equality/hash behavior, and malformed class IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MapWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MultipleIOException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MultipleIOException.java

Purpose: `MultipleIOException` packages several `IOException` instances into one `IOException` so callers can report all cleanup or multi-resource failures without losing every error after the first.

Important APIs and types: the private constructor stores a final `List<IOException>` and builds a summary message. `getExceptions()` exposes the underlying list. `createIOException(List<IOException>)` returns `null` for no failures, the single exception for one failure, or a `MultipleIOException` for multiple failures. Nested `Builder` lazily accumulates throwables, wrapping non-IO throwables in `IOException`, and exposes `build()` and `isEmpty()`.

Control flow: callers add failures as they occur, then call `build()` at the end of the aggregate operation. The factory preserves single-exception identity to avoid unnecessary wrapping and only allocates a multiple wrapper when needed.

State and persistence: state is in-memory exception list storage only. The list reference is not defensively copied, so later list mutation affects `getExceptions()` and potentially the exception's logical contents.

Dependencies and integration points: depends only on Java `IOException`, `ArrayList`, and `List`, plus Hadoop annotations. It is useful for close/delete/cleanup paths across Hadoop IO and filesystem code.

Risks and test signals: risks include returning `null` from `build()`/`createIOException`, which callers must handle, and exposing a mutable list. Tests should cover null/empty/single/multiple factory cases, non-IO throwable wrapping, message contents, and builder `isEmpty` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MultipleIOException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/NullWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/NullWritable.java

Purpose: `NullWritable` is Hadoop's singleton zero-byte `WritableComparable`, used when a key or value position is semantically empty but APIs require a Writable object.

Important APIs and types: `get()` returns the single private instance. `readFields` and `write` are no-ops. `compareTo` always returns zero, `equals` accepts any `NullWritable`, `hashCode` returns zero, and `toString` returns `(null)`. Nested `Comparator` asserts both serialized lengths are zero and returns equality.

Control flow: all serialization paths consume or emit no bytes. Static initialization registers the raw comparator with `WritableComparator`, so sort paths can compare zero-length serialized values without instantiation.

State and persistence: no per-instance state exists. Persistent representation is empty. Singleton construction keeps object identity stable for normal use, though equality is type-based rather than identity-based.

Dependencies and integration points: integrates with Hadoop Writable APIs and MapReduce jobs that use no meaningful key or value, for example output values where only keys matter.

Risks and test signals: risks are mostly API misuse: expecting payload bytes, using assertions as runtime validation for serialized length, or relying on object identity after reflective construction. Tests should cover singleton access, zero-byte round trip, comparator behavior with zero lengths, equality/hash semantics, and use as a MapReduce key/value placeholder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/NullWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ObjectWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ObjectWritable.java

Purpose: `ObjectWritable` is a polymorphic Hadoop Writable wrapper that serializes the declared class name and an instance payload. It handles Writable implementations, strings, primitives, enums, arrays, compact primitive arrays, protobuf messages, and typed null values.

Important APIs and types: instance fields store `declaredClass`, `instance`, and `Configuration`. Constructors and `set/get/getDeclaredClass` manage wrapper contents. Static `writeObject` overloads encode an object with optional compact primitive-array support. Static `readObject` overloads decode a value and optionally populate an `ObjectWritable`. `NullInstance` records the declared class for null payloads. `PRIMITIVE_NAMES`, `loadClass`, `tryInstantiateProtobuf`, and `getStaticProtobufMethod` support class resolution and special formats.

Control flow: writing substitutes `NullInstance` for nulls, optionally wraps primitive arrays in `ArrayPrimitiveWritable.Internal`, writes the declared class name, then dispatches by declared class: arrays recurse element by element, primitive wrappers write their primitive value, strings use `UTF8`, enums write their name, Writables write the runtime instance class then delegate `write`, and protobufs write a delimited message. Reading reverses the process by reading the declared class name, resolving primitives through a fixed map or Hadoop configuration, dispatching to matching type-specific reads, reflectively instantiating Writables, and unwrapping `NullInstance`.

State and persistence: state is the wrapped object and declared class plus configuration for class loading. Persistent bytes include class names, so compatibility depends on stable Java class names and available classes. Compact primitive arrays are always accepted on read, but only written when explicitly allowed.

Dependencies and integration points: depends on Hadoop `Writable`, `WritableFactories`, `UTF8`, `ArrayPrimitiveWritable`, `Configuration`, `Configurable`, `Configured`, `ProtoUtil`, protobuf `Message`, Java reflection, and arrays. It is central to older Hadoop RPC and generic serialization code.

Risks and test signals: risks include arbitrary class loading from serialized data, runtime exceptions for missing classes, reflective protobuf method assumptions, class-name compatibility across versions, recursion/large allocation from malicious array lengths, and `set(null)` throwing because it calls `instance.getClass()`. Tests should cover null declared classes, primitive/string/enum/writable/protobuf round trips, compact and noncompact primitive arrays, configuration class loading, malformed class names, invalid array lengths, and `ObjectWritable` population during `readFields`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ObjectWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/OutputBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/OutputBuffer.java

Purpose: `OutputBuffer` is a reusable in-memory `FilterOutputStream` that exposes its backing byte array and valid length for repeated serialization without creating new `ByteArrayOutputStream` instances.

Important APIs and types: the private `Buffer` extends `ByteArrayOutputStream`, exposing `getData()`, `getLength()`, an overridden `reset()`, and `write(InputStream, int)` for direct bulk reads into the buffer. Public `OutputBuffer` exposes `getData`, `getLength`, chainable `reset`, and `write(InputStream, int)`.

Control flow: normal writes go through inherited `FilterOutputStream` behavior into the backing `Buffer`. `write(InputStream, int)` computes the new count, grows the backing array by doubling or exact fit, uses `IOUtils.readFully` to read exactly the requested number of bytes at the current count, then advances count.

State and persistence: state is an in-memory byte array and count. `reset` drops the count to zero but retains capacity. `getData()` returns the mutable internal buffer, valid only up to `getLength()`. There is no external resource persistence.

Dependencies and integration points: depends on `IOUtils.readFully` and Java IO. It is paired with `InputBuffer` and `DataOutputBuffer` for Hadoop internal serialization loops.

Risks and test signals: risks include exposed mutable internal storage, retained large buffers after spikes, exact-read failure leaving partial bytes in the buffer before count advances, and integer overflow for very large `count + len`. Tests should cover growth behavior, exact input length enforcement, reuse after reset, visible data length, and mutation through `getData`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/OutputBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/RawComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/RawComparator.java

Purpose: `RawComparator<T>` extends Java `Comparator<T>` with a method for comparing serialized byte representations directly, enabling Hadoop sort paths to avoid object deserialization.

Important APIs and types: the sole additional method `compare(byte[] b1, int s1, int l1, byte[] b2, int s2, int l2)` compares two objects encoded as byte ranges. Implementations also provide normal object comparison through `Comparator<T>`.

Control flow: Hadoop sorting, grouping, and lookup components can call raw comparison when they have serialized key bytes, and object comparison when actual key instances are present. Implementations must keep both orderings consistent.

State and persistence: the interface has no state and no persistence behavior. It defines a contract for consumers of serialized data.

Dependencies and integration points: depends on Java `Comparator` and references `DeserializerComparator`. It is implemented by `WritableComparator` and specialized comparators such as `IntWritable.Comparator`, `LongWritable.Comparator`, and `MD5Hash.Comparator`; MapFile and SequenceFile sorting rely on this contract.

Risks and test signals: risks include inconsistent raw/object ordering, invalid handling of offsets and lengths, and comparators reading beyond slice boundaries. Tests should compare raw and object results for the same values, exercise nonzero offsets, truncated or malformed encodings where applicable, and verify sort/group behavior with custom comparators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/RawComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ReadaheadPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ReadaheadPool.java

Purpose: `ReadaheadPool` manages a singleton daemon thread pool that issues asynchronous POSIX readahead hints on file descriptors through Hadoop native IO, helping sequential readers warm the OS page cache.

Important APIs and types: `getInstance()` lazily returns a singleton only when `NativeIO.isAvailable()`. `resetInstance()` shuts down the singleton for tests. `readaheadStream(...)` decides when to submit the next request based on current position, configured readahead length, maximum offset, and the previous request. `submitReadahead(...)` enqueues a `ReadaheadRequestImpl`. The `ReadaheadRequest` interface exposes `cancel`, `getOffset`, and `getLength`.

Control flow: callers repeatedly pass their current read position and prior request. If readahead is disabled or no bytes remain, no request is made. Once the reader reaches halfway through the prior readahead window, the prior request is canceled and a new request is submitted for `min(readaheadLength, maxOffsetToRead - curPos)`. Worker threads call `posixFadviseIfPossible(..., POSIX_FADV_WILLNEED)` unless canceled or the descriptor is invalid.

State and persistence: process-wide state is the singleton and its `ThreadPoolExecutor` with a bounded queue and discard-oldest rejection policy. Each request stores identifier, file descriptor, offset, length, and volatile cancellation flag. There is no durable persistence.

Dependencies and integration points: depends on `NativeIO.POSIX`, POSIX fadvise constants, Guava `ThreadFactoryBuilder`, Hadoop `Preconditions`, SLF4J, and Java executors. It integrates with local file readers that can expose `FileDescriptor`s.

Risks and test signals: risks include queue pressure silently discarding oldest work, races with descriptor close/reuse, native IO unavailability returning null singleton, cancellation not removing queued tasks, and precondition failure if caller passes `curPos > maxOffsetToRead`. Tests should cover singleton availability/reset, trigger threshold behavior, max-offset clipping, cancellation before close, native failure logging, disabled/zero lengths, and executor rejection under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ReadaheadPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SecureIOUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SecureIOUtils.java

Purpose: `SecureIOUtils` provides local-file open/create helpers that reduce symlink traversal and ownership-substitution attacks when Hadoop security is enabled. It validates opened file descriptors with native `fstat` and uses native create-with-permissions when available.

Important APIs and types: static initialization checks `UserGroupInformation.isSecurityEnabled()` and `NativeIO.isAvailable()`, fails fast if secure mode requires unavailable native code, caches a raw local filesystem, and sets `skipSecurity`. Public `openForRandomRead`, `openFSDataInputStream`, and `openForRead` perform insecure direct opens when Hadoop security is disabled and secure force-open paths otherwise. `createForWrite` creates a non-existing file with requested permissions via native IO or an insecure fallback. `AlreadyExistsException` reports create collisions. Visible-for-testing force methods run secure checks regardless of global security mode.

Control flow: secure open methods open the file first, call native `fstat` on the returned descriptor, compare actual owner/group metadata with expected values via `checkStat`, and close the stream/file if validation fails. This avoids checking a path before open and then following a swapped symlink. `createForWrite` uses native atomic create when possible; fallback checks existence, opens a `FileOutputStream`, then chmods through the raw filesystem.

State and persistence: state is static process configuration (`skipSecurity`) and cached raw local filesystem. Persistent effects are opened descriptors/streams and newly created local files with requested permissions. The insecure fallback is explicitly race-prone when native support is absent.

Dependencies and integration points: depends on Hadoop `UserGroupInformation`, `NativeIO.POSIX.Stat`, `FileSystem`, `FSDataInputStream`, `Path`, `FsPermission`, and Java file streams. It is used by local disk paths where logs, tokens, or task files need owner validation.

Risks and test signals: risks include group validation being effectively absent despite expectedGroup parameters, security disabled paths skipping ownership checks, fallback create race vulnerability, Windows administrator-owner special handling, static initialization failure when raw local filesystem cannot be obtained, and native dependency differences across platforms. Tests should cover secure and insecure modes, owner mismatch, Windows administrator allowance, force methods with security disabled, create existing-file failure, permission setting, cleanup on failed validation, and behavior when native IO is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SecureIOUtils.java -->
