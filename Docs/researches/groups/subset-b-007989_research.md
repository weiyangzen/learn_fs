# subset-b-007989 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBuffer.java

## Purpose

`ChunkBuffer` is the common abstraction Ozone uses for block chunk payload buffers. It deliberately presents a `ByteBuffer`-like API while hiding whether data is stored in one direct buffer, a list of buffers, or an incrementally allocated sequence. It also extends `ChunkBufferToByteString` for protobuf/Ratis conversion and `UncheckedAutoCloseable` so direct `CodecBuffer` resources can be released.

## APIs and control flow

Static factories choose the backing implementation: `allocate(capacity)` allocates one direct `CodecBuffer`; `allocate(capacity, increment)` uses `IncrementalChunkBuffer` when the increment is positive and smaller than the capacity; `wrap(ByteBuffer)` and `wrap(List<ByteBuffer>)` adapt existing buffers. The core API mirrors `position`, `remaining`, `limit`, `rewind`, `clear`, `put`, `duplicate`, `iterate`, `asByteBufferList`, and `writeTo`.

## State, dependencies, and integration

The interface owns no state, but its contracts are position-sensitive. Default `put` overloads convert byte arrays and Ratis `ByteString` into `ByteBuffer` writes. It depends on HDDS `CodecBuffer`, Ratis `ByteString`, and `GatheringByteChannel`, and is integrated by container IO and checksum paths that need efficient chunk transfer.

## Risks and test signals

The main risk is callers assuming immutable or thread-safe behavior. Implementations mutate backing buffer positions during writes and iteration. Tests should cover allocation choice, duplicate bounds, list wrapping, close/release behavior, and preservation of buffer position during ByteString conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferImplWithByteBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferImplWithByteBuffer.java

## Purpose

This package-private `ChunkBuffer` implementation wraps a single `ByteBuffer`. It is the simplest backing strategy and is used when a full chunk buffer is allocated up front or when an existing single buffer is adapted.

## APIs and control flow

The implementation delegates `position`, `remaining`, `limit`, `rewind`, `clear`, `put`, equality, and hash code to the wrapped `ByteBuffer`. `iterate(bufferSize)` returns duplicated slices from the current position to the limit, advancing the original buffer by the emitted slice size. `duplicate(newPosition, newLimit)` returns a new wrapper over a duplicated `ByteBuffer`. `writeTo` drains the buffer through `BufferUtils.writeFully`.

## State, dependencies, and integration

State is the mutable `ByteBuffer` plus an optional `UncheckedAutoCloseable` `underlying`, normally the direct `CodecBuffer` allocated by `ChunkBuffer.allocate`. `close()` releases only when that underlying resource exists. ByteString conversion passes the live buffer through the supplied converter, relying on `ChunkBufferToByteString` to enforce position and limit preservation.

## Risks and test signals

Because `asByteBufferList()` exposes the live buffer, callers can mutate position and limit outside the wrapper. Iteration is destructive with respect to position. Tests should check that close releases direct buffers once, iteration chunking is correct, duplicate views have independent positions, and conversion functions do not disturb the underlying buffer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferImplWithByteBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferImplWithByteBufferList.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferImplWithByteBufferList.java

## Purpose

`ChunkBufferImplWithByteBufferList` adapts multiple `ByteBuffer` instances into one logical `ChunkBuffer`. It supports chunk data that is already segmented, avoiding an immediate copy into a single contiguous buffer. The class is explicitly not thread-safe.

## APIs and control flow

Construction stores an immutable copy of the buffer list, substitutes a zero-length buffer for an empty list, computes total logical limit from component limits, and finds the current component by scanning positions. `put(ByteBuffer)` checks logical remaining capacity and writes across component boundaries. `duplicate(newPosition, newLimit)` creates per-buffer duplicates whose positions and limits are clipped to the requested logical range. `iterate(bufferSize)` returns a duplicate of the current component when possible, otherwise allocates a temporary buffer to bridge multiple components. `writeTo` drains the list via gathering writes and then rescans current state.

## State, dependencies, and integration

State is the immutable list of mutable component buffers, total logical limit, `currentIndex`, and `limitPrecedingCurrent`. It depends on Guava preconditions/immutable lists, `BufferUtils`, and Ratis `ByteString`. It integrates with reads or network paths that naturally produce multiple buffers.

## Risks and test signals

The implementation temporarily changes source buffer limits while copying across components in `put` and `iterate`; incorrect reset or external mutation can corrupt later positions. `asByteBufferList()` exposes live buffers. Tests should cover empty lists, current detection invariants, cross-buffer writes, range duplication at component boundaries, gathering write position updates, and iteration when requested size spans buffers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferImplWithByteBufferList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferToByteString.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferToByteString.java

## Purpose

`ChunkBufferToByteString` defines the conversion contract from chunk-backed buffers to Ratis protobuf `ByteString` values. It exists to keep zero-copy or safe-wrap conversion choices outside the concrete chunk buffer classes while enforcing that conversion functions do not mutate buffer cursor state.

## APIs and control flow

`wrap(List<ByteBuf>)` adapts Netty `ByteBuf` instances with `ChunkBufferToByteStringByByteBufs`. `toByteString(function)` and `toByteStringList(function)` wrap the supplied converter with `applyAndAssertFunction`, which records a buffer's position and limit, applies the converter, and throws an `IllegalStateException` if either value changes. `toByteString()` is a test convenience using `ByteStringConversion.safeWrap`.

## State, dependencies, and integration

The interface owns no persistent state. It depends on HDDS `ByteStringConversion`, Ratis shaded `ByteString`, and Ratis shaded Netty `ByteBuf`. It is integrated by chunk IO and Ratis replication code that needs either concatenated payloads or per-buffer `ByteString` lists.

## Risks and test signals

The converter can still retain references to mutable buffers if it performs unsafe wrapping; the interface only checks cursor preservation. Tests should cover rejecting converters that alter position/limit, empty conversion, list conversion shape, and release semantics for `ByteBuf` wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferToByteString.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferToByteStringByByteBufs.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferToByteStringByByteBufs.java

## Purpose

This implementation converts a list of Netty `ByteBuf` instances into one concatenated `ByteString` or a list of per-NIO-buffer `ByteString` values. It provides a bridge from Netty-backed RPC/network buffers to protobuf payloads.

## APIs and control flow

Construction stores an unmodifiable view of the supplied list or an empty list. `release()` calls `release()` on every `ByteBuf`. `toByteStringImpl` and `toByteStringListImpl` lazily initialize cached conversion results. `initByteStrings` is synchronized and double-checks the cache so concurrent callers produce only one converted list. `convert` iterates every `ByteBuf.nioBuffers()` component, applies the converter, appends each result to the list, and concatenates them into a single result.

## State, dependencies, and integration

State is the original `ByteBuf` list plus volatile caches for the list and concatenated `ByteString`. It depends on Ratis shaded Netty and protobuf classes. It integrates wherever Ratis/Netty buffers need to be retained until conversion and then released.

## Risks and test signals

The class does not retain `ByteBuf`s, so callers must define ownership clearly; calling `release()` before conversion can break later reads, and calling it repeatedly can over-release. Concatenation is O(number of components) but repeated `ByteString.concat` can become costly for many buffers. Tests should cover empty input, multi-component `ByteBuf`s, cache reuse, concurrent conversion, and release ownership.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferToByteStringByByteBufs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/InconsistentStorageStateException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/InconsistentStorageStateException.java

## Purpose

`InconsistentStorageStateException` is an `IOException` subtype for unrecoverable local filesystem or storage metadata inconsistencies. It is annotated private/evolving and is intended for internal HDDS/Ozone storage initialization and validation paths.

## APIs and control flow

The string constructor passes a description directly to `IOException`. The file constructor builds a message in the form `Directory <path> is in an inconsistent state: <descr>`. `getFilePath(File)` prefers `getCanonicalPath()` and falls back to `getPath()` if canonicalization fails.

## State, dependencies, and integration

The class has no mutable state beyond standard exception fields. It depends only on `java.io.File`, `IOException`, and HDDS audience/stability annotations. It integrates with callers that need a typed signal that storage layout/state cannot be safely recovered.

## Risks and test signals

The canonical-path failure is silently ignored, which is appropriate for error reporting but can hide path resolution issues. Tests should check message formatting, canonical fallback behavior, and that callers do not swallow this exception in paths requiring manual intervention.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/InconsistentStorageStateException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/IncrementalChunkBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/IncrementalChunkBuffer.java

## Purpose

`IncrementalChunkBuffer` implements a logical fixed-limit `ChunkBuffer` backed by direct `CodecBuffer`s allocated only as data is written. This reduces memory pressure for large chunk capacities when producers may not fill the whole buffer.

## APIs and control flow

Construction records the logical limit, increment size, last index, buffer list, and release list. `getAndAllocateAtIndex` allocates direct buffers up to the requested component. `position()` finds the first non-full buffer and asserts that later allocated buffers remain empty. `put(ByteBuffer)` checks overflow, then writes across increment-sized components, temporarily narrowing the source buffer limit. `duplicate(newPosition, newLimit)` creates a read-only-style duplicated `IncrementalChunkBuffer` containing duplicates of already allocated buffers over the requested range. `iterate(bufferSize)` only supports a buffer size equal to the increment and returns the backing list. `close()` releases all owned `CodecBuffer`s.

## State, dependencies, and integration

Mutable state includes allocated buffers, underlying direct buffers, and `firstNonFullIndex`. Duplicated instances have no owned underlying buffers and reject allocation. The class depends on Guava preconditions, HDDS `CodecBuffer`, `BufferUtils`, and Ratis `ByteString`. It is selected by `ChunkBuffer.allocate(capacity, increment)`.

## Risks and test signals

The code assumes sequential writes: full buffers, one partially filled buffer, then empty/unallocated buffers. Random external mutation through `asByteBufferList()` can violate invariants. Duplicate ranges require all referenced buffers to already exist. Tests should cover incremental allocation count, boundary capacities, full-capacity writes, overflow, close release, duplicate across increments, unsupported iteration sizes, and position invariants after rewind/clear.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/IncrementalChunkBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/OzoneChecksumException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/OzoneChecksumException.java

## Purpose

`OzoneChecksumException` is a private/evolving `IOException` subtype used to report checksum validation failures in Ozone data paths.

## APIs and control flow

The class provides a message-only constructor and a message-plus-cause constructor. There is no special control flow or extra fields; the type itself is the meaningful signal.

## State, dependencies, and integration

It depends only on Java `IOException` and HDDS audience/stability annotations. It integrates with checksum computation and chunk/block read validation code so callers can distinguish data-integrity failures from generic IO failures.

## Risks and test signals

The class carries no structured checksum details, so diagnostics depend on caller-provided messages. Tests should assert that checksum mismatches throw this specific type and preserve causal exceptions when lower-level checksum code fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/OzoneChecksumException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/PureJavaCrc32ByteBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/PureJavaCrc32ByteBuffer.java

## Purpose

`PureJavaCrc32ByteBuffer` is a static utility retaining the precomputed table-backed `mod(long)` helper for CRC-32. Earlier checksum update methods have been removed; production and tests now use this class only for polynomial modular reduction.

## APIs and control flow

The class is non-instantiable and exposes only `mod(long x)`. The method splits the low 32 bits into bytes, uses four table slices offset by `0x000`, `0x100`, `0x200`, and `0x300`, XORs those lookups, and combines them with the high 32 bits. The table is generated for the CRC-32 polynomial `0xEDB88320`.

## State, dependencies, and integration

State is a large immutable static lookup table. There are no external dependencies beyond Java. It integrates with checksum combination or comparison logic that needs CRC polynomial arithmetic without an object-oriented checksum updater.

## Risks and test signals

The lookup table is opaque and easy to break with mechanical edits. Tests should compare `mod(long)` against known CRC-32 polynomial arithmetic vectors, especially values that exercise each byte lookup and high-bit behavior. Performance tests can confirm the table path remains allocation-free.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/PureJavaCrc32ByteBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/PureJavaCrc32CByteBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/PureJavaCrc32CByteBuffer.java

## Purpose

`PureJavaCrc32CByteBuffer` is the CRC-32C counterpart of `PureJavaCrc32ByteBuffer`. It keeps a table-backed `mod(long)` helper after removal of older `ChecksumByteBuffer` update behavior.

## APIs and control flow

The only public API is `mod(long x)`. It computes `x mod p` for the CRC-32C polynomial by XORing the high 32 bits with four table lookups derived from the low 32-bit value's bytes. The table is generated for polynomial `0x82F63B78`, with a note preserving Intel BSD-license attribution for portions of the file.

## State, dependencies, and integration

The class has no mutable state and no external dependencies. It integrates with CRC-32C checksum combination or validation code that needs polynomial modular reduction.

## Risks and test signals

Correctness depends entirely on the static table and byte-index expression. Regression tests should compare `mod(long)` to independent CRC-32C polynomial calculations, include high-bit and zero cases, and protect the table from accidental reformatting or truncation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/PureJavaCrc32CByteBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/package-info.java

## Purpose

This package descriptor marks `org.apache.hadoop.ozone.common` as the home for common HDDS/Ozone classes. In this work item the package contains chunk-buffer abstractions, checksum exception types, CRC helpers, and storage-state exceptions.

## APIs and integration

There are no executable APIs. The JavaDoc package comment is consumed by generated documentation and by developers navigating the module. It anchors shared code that is used by container helpers, checksum code, and replication/serialization paths.

## State, dependencies, risks, and test signals

The file has no state, persistence, or runtime dependencies. The only risk is documentation drift if the package's role changes. Tests are not needed for this file, but documentation checks can ensure package descriptors remain valid and compile with JavaDoc.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/InvalidStateTransitionException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/InvalidStateTransitionException.java

## Purpose

`InvalidStateTransitionException` is the typed failure thrown when a generic Ozone state machine receives an event that has no transition from the current state.

## APIs and control flow

The constructor records the current state and event, both as `Enum<?>`, and builds a message in the form `Invalid event: <event> at <state> state.`. `getCurrentState()` and `getEvent()` expose the stored values.

## State, dependencies, and integration

State is immutable by convention but the fields are not declared `final`. The class has no external dependencies. It integrates with `StateMachine.getNextState`, which throws it for missing transition table entries.

## Risks and test signals

Because state and event are stored as raw enums, consumers must know the concrete enum types from context. Tests should verify thrown messages and accessors for missing transitions, and ensure valid transitions do not allocate or throw.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/InvalidStateTransitionException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/StateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/StateMachine.java

## Purpose

`StateMachine<STATE, EVENT>` is a small reusable event-driven transition table for enum states and events. It stores an initial state, optional final states, and mappings from `(event, fromState)` to `toState`.

## APIs and control flow

Construction copies final states into an immutable set or uses an empty set. `addTransition(from, to, event)` inserts into a per-event map held in a Guava `LoadingCache`, which lazily creates `HashMap` instances. `getNextState(from, event)` looks up the target state and throws `InvalidStateTransitionException` when absent. Accessors expose initial and final states.

## State, dependencies, and integration

State is mutable transition maps plus immutable initial/final metadata. The class depends on Guava cache and immutable set utilities. It integrates with Ozone components that want declarative transition validation without building a component-specific state engine.

## Risks and test signals

The transition maps are mutable and not synchronized; callers should configure them before concurrent use. Final states are only stored, not enforced by `addTransition` or `getNextState`. Tests should cover transition lookup, absent events, null final-state input, duplicate transition replacement, and concurrency assumptions if used after startup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/StateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.common.statemachine` as a template state-machine package for Ozone.

## APIs and integration

It has no runtime API. It groups `StateMachine` and `InvalidStateTransitionException`, which provide a generic enum transition table and typed invalid-transition failure.

## State, dependencies, risks, and test signals

The file has no state or persistence behavior. The only risk is stale documentation if the package expands beyond a generic state-machine template. Compilation and JavaDoc generation are sufficient test signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/utils/BufferUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/utils/BufferUtils.java

## Purpose

`BufferUtils` centralizes common ByteBuffer and ByteString helper operations for Ozone chunk IO. It handles buffer allocation, read-only views, length calculations, concatenation, bin counts, and complete gathering-channel writes.

## APIs and control flow

`assignByteBuffers(totalLen, bufferCapacity)` allocates an array sized by `getNumberOfBins`, using full-size buffers except the last. `getReadOnlyByteBuffers` adapts `ByteString` lists or `ByteBuffer[]` into read-only buffers. `concatByteStrings` concatenates a list in order. `getBuffersLen` sums sizes. `getNumberOfBins` implements ceiling division with overflow detection. The three `writeFully` overloads loop until each buffer's remaining bytes are written, throwing if a channel reports a negative write.

## State, dependencies, and integration

The class is stateless and depends on Guava preconditions, Ratis `ByteString`, `GatheringByteChannel`, and SLF4J. It is used by all `ChunkBuffer` implementations for reliable writes.

## Risks and test signals

`writeFully` can spin on a non-blocking channel returning zero repeatedly; callers should use appropriate channel types. `concatByteStrings` can be costly for many components. Tests should cover zero/negative argument rejection, exact last-buffer sizing, integer overflow, read-only protection, and partial-write channels.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/utils/BufferUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/utils/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.common.utils` as common HDDS utility code. In this work item it contains `BufferUtils`.

## APIs and integration

There is no executable API. The package integrates with chunk-buffer and IO code by housing shared buffer helper functionality.

## State, dependencies, risks, and test signals

The file has no state or persistence behavior. Documentation drift is the main risk. Java compilation and JavaDoc generation validate it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/conf/OzoneServiceConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/conf/OzoneServiceConfig.java

## Purpose

`OzoneServiceConfig` defines service-level configuration shared by Ozone services, currently focused on shutdown-hook timeout behavior.

## APIs and control flow

The class is annotated `@ConfigGroup(prefix = "ozone.service")`. It exposes constants for minimum shutdown timeout, default time unit, default hook priority, and the `ozone.service.shutdown.timeout` key with default `60s`. The configured field is annotated as a time config tagged for Ozone, OM, SCM, datanode, Recon, and S3 Gateway. Getters and setters expose the resolved timeout in seconds.

## State, dependencies, and integration

State is the mutable `serviceShutdownTimeout` field populated by the HDDS configuration framework. The class depends on HDDS `@Config`, `@ConfigGroup`, `ConfigType`, and config tags. `ShutdownHookManager` and `HddsUtils.getShutDownTimeOut` use these values to bound hook execution and executor termination.

## Risks and test signals

The description string has no space between sentences, but runtime behavior is unaffected. Tests should cover default binding, parsing of time units, minimum timeout enforcement in consumers, and compatibility across all service tags.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/conf/OzoneServiceConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/conf/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/conf/package-info.java

## Purpose

This package descriptor marks `org.apache.hadoop.ozone.conf` as the package for Ozone configuration classes.

## APIs and integration

It has no executable API. In this subset it groups `OzoneServiceConfig`, which is consumed by shutdown management and HDDS configuration binding.

## State, dependencies, risks, and test signals

No state or persistence behavior exists. JavaDoc/compile validation is sufficient; the only practical risk is stale package documentation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/BlockData.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/BlockData.java

## Purpose

`BlockData` is the Java helper and DB codec wrapper for `ContainerProtos.BlockData`. It records a `BlockID`, metadata, chunk list, block size, and block commit sequence ID while preserving protobuf compatibility.

## APIs and control flow

`getCodec()` returns a `DelegatedCodec` over a proto3 codec with backward compatibility for schema-one parsing. `getFromProtoBuf` converts metadata and chunks, then validates any proto `size` field against computed chunk length. `getProtoBufMessage` recomputes chunk length and throws `CodecException` if it differs from the stored size. `addMetadata` rejects duplicate keys. `addChunk`, `removeChunk`, and `setChunks` maintain size as chunks change. `getChunks` uses a memory-saving internal representation: null for none, a single proto object for one chunk, and a list for many.

## State, dependencies, and integration

State includes mutable `BlockID`, sorted metadata, compact `chunkList`, and `size`. It depends on HDDS `BlockID`, container protobufs, HDDS codec classes, `OzoneConsts`, and Ratis `TextFormat`. It integrates with datanode container metadata tables and block commit/read paths.

## Risks and test signals

The compact `Object` chunk representation is efficient but type-sensitive. External chunk lists passed to `setChunks` can be retained directly when size is greater than one. Tests should cover codec round trips, duplicate metadata rejection, size mismatch failures, single-to-list transitions, removal size updates, and block group length metadata parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/BlockData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ChunkInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ChunkInfo.java

## Purpose

`ChunkInfo` is the Java helper for `ContainerProtos.ChunkInfo`. It represents a physical chunk name, offset, length, checksum data, metadata, optional stripe checksum, and a compatibility flag for older read wire formats.

## APIs and control flow

Construction sets immutable chunk identity fields and a sorted metadata map. `addMetadata` synchronizes on the map and rejects duplicate keys. `getFromProtoBuf` requires a non-null proto, copies metadata, converts checksum data with `ChecksumData.getFromProtoBuf`, and captures `stripeChecksum` when present. `getProtoBufMessage` writes chunk identity, metadata, and checksum data, using `Checksum.getNoChecksumDataProto()` when no checksum is set.

## State, dependencies, and integration

State is mostly immutable chunk identity plus mutable checksum, metadata, stripe checksum, and `readDataIntoSingleBuffer`. It depends on container protobufs, Ozone `Checksum`/`ChecksumData`, and Ratis `ByteString`. It integrates with container protocol messages and chunk read/write helpers.

## Risks and test signals

The current `getProtoBufMessage` does not write `stripeChecksum` back into the builder, while `getFromProtoBuf` reads it. That asymmetry is a persistence risk if callers expect round-trip preservation. Tests should cover duplicate metadata, null checksum fallback, proto conversion, stripe checksum round trip, and old-client single-buffer flag behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ChunkInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ChunkInfoList.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ChunkInfoList.java

## Purpose

`ChunkInfoList` is an immutable wrapper and codec target for a list of `ContainerProtos.ChunkInfo` messages.

## APIs and control flow

The constructor stores `Collections.unmodifiableList(chunks)`. `getCodec()` returns a shallow-copy `DelegatedCodec` over `ContainerProtos.ChunkInfoList`. `getFromProtoBuf` wraps `chunksProto.getChunksList()`, and `getProtoBufMessage` builds a proto by adding all wrapped chunks.

## State, dependencies, and integration

State is the unmodifiable chunk list reference. Dependencies are container protobufs and HDDS codec utilities. It integrates with metadata tables or protocol helpers that persist chunk lists as a single value.

## Risks and test signals

The constructor does not null-check or defensively copy, so mutations to a caller-owned mutable list can affect the wrapper despite the unmodifiable view. Tests should cover codec round trips, null rejection expectations, shallow-copy behavior, and immutability through the public accessor surface.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ChunkInfoList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/package-info.java

## Purpose

This package descriptor identifies `org.apache.hadoop.ozone.container.common.helpers` as helper classes for container protocol communication.

## APIs and integration

It has no runtime API. The package contains helpers such as `BlockData`, `ChunkInfo`, and `ChunkInfoList` that convert between Java objects, protobufs, and DB codec values.

## State, dependencies, risks, and test signals

The descriptor has no state. Its role is documentation and package organization. Compile and JavaDoc generation are sufficient test signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ha/ConfUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ha/ConfUtils.java

## Purpose

`ConfUtils` contains HA-related configuration-key helpers, mainly for deriving and applying node-specific keys such as `<key>.<serviceId>.<nodeId>`.

## APIs and control flow

`addSuffix` appends a non-empty suffix with a dot separator and asserts the suffix is not already dotted. `addKeySuffixes` concatenates suffixes and appends them to a base key. `concatSuffixes` uses Guava `Joiner` with skipped nulls. `getConfSuffixedWithServiceId` reads a trimmed node-specific config and returns null for empty values. `setNodeSpecificConfigs` loops over configured keys, reads node-specific values, logs the mapping, and writes the generic key into `OzoneConfiguration`.

## State, dependencies, and integration

The class is stateless. It depends on Guava, Apache Commons `StringUtils`, HDDS configuration interfaces, `OzoneConfiguration`, and SLF4J. It integrates with HA service startup code that resolves OM/SCM node-specific settings.

## Risks and test signals

`addSuffix` uses Java `assert`, so dotted-suffix validation is disabled unless assertions are enabled. Empty strings from skipped suffixes can produce unexpected keys. Tests should cover null suffixes, multiple suffix joins, missing config fallback, and mutation of generic keys during service initialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ha/ConfUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ha/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ha/package-info.java

## Purpose

This descriptor documents `org.apache.hadoop.ozone.ha` as the package for Ozone high-availability related classes.

## APIs and integration

There is no executable API. In this subset it groups `ConfUtils`, which helps resolve service/node-suffixed HA configuration keys.

## State, dependencies, risks, and test signals

The file has no state or persistence. Documentation drift is the only risk; compile and JavaDoc validation are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ha/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/BootstrapStateHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/BootstrapStateHandler.java

## Purpose

`BootstrapStateHandler` defines a component interface for exposing a bootstrap-state lock. The nested `Lock` wrapper standardizes read/write acquisition through `UncheckedAutoCloseable` resources.

## APIs and control flow

Implementers return a `Lock` from `getBootstrapStateLock()`. `Lock` is constructed with a `Function<Boolean, UncheckedAutoCloseable>` where `true` means read lock and `false` means write lock. `acquireWriteLock()` and `acquireReadLock()` delegate to the supplier. The comment notes the bootstrap lock should be acquired before opening snapshots to avoid deadlocks.

## State, dependencies, and integration

State is the lock supplier function. It depends on Java `Function` and Ratis `UncheckedAutoCloseable`. Integration points are bootstrap/snapshot workflows that need consistent lock ordering.

## Risks and test signals

The methods declare `InterruptedException`, but the supplier signature cannot throw checked exceptions; implementations must encode interruption in the supplier or wrap it. Tests should verify read/write boolean mapping, close-based unlock behavior, and lock ordering in snapshot-open paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/BootstrapStateHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/ReadWriteLockable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/ReadWriteLockable.java

## Purpose

`ReadWriteLockable` is a minimal interface for objects that expose explicit read and write lock/unlock methods.

## APIs and control flow

The API consists of `readLock`, `readUnlock`, `writeLock`, and `writeUnlock`. It does not define ownership, reentrancy, interruption, or closeable guard semantics.

## State, dependencies, and integration

The interface has no state or dependencies. Implementations integrate with Ozone components that want to expose locking without leaking their concrete lock type.

## Risks and test signals

The API is easy to misuse because lock and unlock are separate calls rather than scoped resources. Tests should focus on implementations: balanced unlocks, writer exclusion, reader concurrency, and behavior when exceptions occur inside protected sections.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/ReadWriteLockable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.lock` as the package for lock-related classes.

## APIs and integration

No executable API exists in the descriptor. It groups interfaces such as `BootstrapStateHandler` and `ReadWriteLockable`.

## State, dependencies, risks, and test signals

The file has no state. Compile and JavaDoc generation are sufficient; documentation drift is the only risk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/package-info.java

## Purpose

This package descriptor describes the top-level `org.apache.hadoop.ozone` package in this module as containing datanode-side implementation support, especially container classes for persisting Ozone objects.

## APIs and integration

The file has no executable API. It provides JavaDoc context for the broader package and points readers toward container-related subpackages.

## State, dependencies, risks, and test signals

There is no state or persistence behavior. The main risk is outdated wording as the package grows beyond datanode/container support. Compile and JavaDoc checks validate syntax.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutFeature.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutFeature.java

## Purpose

`LayoutFeature` is the generic Ozone interface for versioned layout features used during upgrades. It connects feature metadata, layout versioning, and optional upgrade actions.

## APIs and control flow

Implementations provide `name`, `layoutVersion`, and `description`. The default `action()` returns `Optional.empty()`, allowing features without prerequisite work. The nested `UpgradeAction<T>` interface exposes a default action name from the implementation class and an `execute(T arg)` method that can throw any exception. `version()` satisfies `Versioned` by returning `layoutVersion()`.

## State, dependencies, and integration

The interface has no state. It depends on Java `Optional` and Ozone `Versioned`. It integrates with layout-version managers and finalization flows that enumerate features, compare versions, and execute feature-specific actions before finalization.

## Risks and test signals

`UpgradeAction` is generic but `action()` erases the argument type as `Optional<? extends UpgradeAction>`, so runners must coordinate argument types carefully. Tests should cover feature ordering by version, optional action execution, action failure propagation, and compatibility between feature enums and layout-version managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeException.java

## Purpose

`UpgradeException` is the structured `IOException` used by Ozone upgrade and finalization flows. It carries a `ResultCodes` enum so callers and clients can distinguish validation, finalization, and layout-version failures.

## APIs and control flow

Constructors support result-only, message, message-plus-cause, and cause-only forms. `getResult()` exposes the result code. `toString()` prefixes the standard exception string with the result code. `STATUS_CODE` is a string constant used for status-code serialization or parsing in adjacent code.

## State, dependencies, and integration

State is the final `ResultCodes result`. The enum includes `OK`, `INVALID_REQUEST`, layout update failure, feature finalization failure, pre-finalize action validation failure, first-upgrade-start action failure, and pre-finalize validation failure. It integrates with `UpgradeFinalization` and service-side upgrade managers.

## Risks and test signals

The result-only constructor has no message, so logs may depend on `toString()` to retain context. Tests should verify result preservation through all constructors, causal chain preservation, `toString()` format, and client handling for each result code.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalization.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalization.java

## Purpose

`UpgradeFinalization` is a client-side utility holder for Ozone upgrade finalization status, default status messages, and CLI/error handling helpers.

## APIs and control flow

Static `StatusAndMessages` constants represent starting, in-progress, required, and finalized states. The `Status` enum models finalization lifecycle states: already finalized, starting, in progress, done, and required. `StatusAndMessages` is an immutable tuple of status and message collection. `handleInvalidRequestAfterInitiatingFinalization(force, e)` suppresses `INVALID_REQUEST` only when forced; otherwise it prints guidance and throws `IOException("Exiting...")`. Helper methods classify statuses and emit standard CLI messages.

## State, dependencies, and integration

The class has only static immutable constants. It depends on `UpgradeException`, Java collections/IO, and HDDS annotations. It integrates with CLI and RPC clients monitoring upgrade finalization.

## Risks and test signals

The class writes directly to `System.out` and `System.err`, which complicates library-style reuse and tests. `isFinalized` only treats `ALREADY_FINALIZED` as finalized, while `FINALIZATION_DONE` is separate. Tests should cover forced takeover behavior, emitted messages, status predicates, and RPC translation of `StatusAndMessages`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.upgrade` as the package for Ozone upgrade and layout-version management.

## APIs and integration

It has no executable API. It groups layout feature contracts, upgrade exceptions, and finalization status helpers.

## State, dependencies, risks, and test signals

No runtime state exists. JavaDoc drift is the only risk; compile and documentation checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/CacheMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/CacheMetrics.java

## Purpose

`CacheMetrics` is a reusable Hadoop metrics2 `MetricsSource` for publishing Guava cache statistics.

## APIs and control flow

`create(Cache, Object)` derives a source name from the owner class and identity hash; `create(Cache, String)` registers a new source with `DefaultMetricsSystem`. `getMetrics` emits a record tagged by cache name and gauges for size, hit/miss counts and rates, load success/exception counts, and eviction count. `unregister()` removes the source by the generated source name.

## State, dependencies, and integration

State is the observed `Cache`, display name, and metrics source name. Dependencies include Guava cache stats, Hadoop metrics2, `DefaultMetricsSystem`, and Ratis `JavaUtils`. It integrates with services that need cache observability without writing custom metrics sources.

## Risks and test signals

Metrics source names include object hash codes for owner-based creation; repeated registration for the same owner string can collide or fail depending on metrics-system behavior. Cache stats require Guava caches created with `recordStats()`. Tests should cover registration/unregistration, emitted gauge names, and behavior with caches that do not record stats.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/CacheMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ClosableIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ClosableIterator.java

## Purpose

`ClosableIterator<E>` marks iterators that hold resources and must be closed after use.

## APIs and control flow

The interface extends `Iterator<E>` and `Closeable`, narrowing `close()` to a no-throws method. It does not define automatic close behavior on exhaustion.

## State, dependencies, and integration

The interface has no state and depends only on Java `Iterator` and `Closeable`. It integrates with metadata table scanners, DB iterators, and any Ozone iterator wrapper around native or IO-backed resources.

## Risks and test signals

Callers must use try/finally or try-with-resources even though `close()` has no checked exception. Tests belong on implementations and should check resource release on early exit, exhaustion, and repeated close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ClosableIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/MetricUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/MetricUtil.java

## Purpose

`MetricUtil` contains helper methods for latency capture and quantile lifecycle management in Ozone metrics code.

## APIs and control flow

Four `captureLatencyNs` overloads wrap checked suppliers or runnables, record `Time.monotonicNowNanos()` before execution, and add or pass elapsed nanoseconds in a `finally` block so failures are still measured. `createQuantiles` validates that the interval array is non-null, returns an empty list for zero intervals, and registers one `MutableQuantiles` per interval using a `<name><interval>s` naming convention. `stop` overloads safely stop non-null quantile instances.

## State, dependencies, and integration

The class is stateless. It depends on Hadoop metrics2, Hadoop `Time`, Ratis checked functional interfaces, and Java collections/consumers. It integrates with metrics sources and `PerformanceMetrics`.

## Risks and test signals

Latency capture changes exception timing but preserves exception propagation. Quantile names can collide if callers reuse the same base name and interval. Tests should cover successful and failing blocks, null and empty intervals, quantile registration names, and stopping nullable collections.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/MetricUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/MutableMinMax.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/MutableMinMax.java

## Purpose

`MutableMinMax` is a custom metrics2 `MutableMetric` tracking interval minimum and maximum values for a named metric.

## APIs and control flow

Construction derives metrics names from the base name, description, and value name, then registers placeholder gauges in the supplied registry for annotation compatibility. `add(value)` updates the current interval min/max and marks the metric changed. `snapshot(builder, all)` emits either current interval or previous interval values, then rolls the current interval into `prevMinMax`, resets the interval, and clears the changed flag when appropriate.

## State, dependencies, and integration

State is two `SampleStat.MinMax` instances and two `MetricsInfo` descriptors. The class is synchronized around mutation and snapshotting. It depends on Commons `StringUtils`, HDDS annotations, and Hadoop metrics2. `PerformanceMetrics` uses it beside stats and quantiles.

## Risks and test signals

Description strings concatenate `"description" + "in"` without an inserted space. Empty intervals use previous values when unchanged, which is intentional but should be understood by dashboards. Tests should cover min/max rollovers, `all=true` snapshots, no-data behavior, and thread-safe add/snapshot interaction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/MutableMinMax.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/OzoneNetUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/OzoneNetUtils.java

## Purpose

`OzoneNetUtils` contains network utility methods for local-address detection and JVM DNS cache control, especially for Kubernetes deployments where pod FQDNs may not resolve at service startup.

## APIs and control flow

`disableJvmNetworkAddressCacheIfRequired` reads `ozone.jvm.network.address.cache.enabled` and, when disabled, sets JVM security properties for positive and negative DNS TTL to `0`. `isAddressHostNameLocal` compares the first label of an address host name to Hadoop `NetUtils.getLocalHostname()`. `getAddressWithHostNameLocal` rewrites an FQDN socket address to first-label hostname plus original port. `isAddressLocal` checks resolved local addresses. The boolean overloads switch behavior based on flexible FQDN resolution.

## State, dependencies, and integration

The class is stateless but mutates JVM-wide `Security` DNS cache properties. It depends on Ozone config keys, `OzoneConfiguration`, Hadoop `NetUtils`, and SLF4J. It integrates with service endpoint validation and HA/FQDN handling.

## Risks and test signals

Changing DNS cache properties is JVM-global and can affect unrelated code. Hostname matching by first label can misclassify hosts in unusual naming schemes. Tests should cover nulls, unresolved addresses, flexible-resolution branches, FQDN rewriting, and DNS property changes under configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/OzoneNetUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/PerformanceMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/PerformanceMetrics.java

## Purpose

`PerformanceMetrics` groups a `MutableStat`, optional interval quantiles, and `MutableMinMax` under one metric name so callers can update and snapshot a full latency/performance metric consistently.

## APIs and control flow

`initializeMetrics(source, registry, sampleName, valueName, intervals)` delegates reflection-based initialization to `PerformanceMetricsInitializer` and wraps `IllegalAccessException` in a runtime exception. The constructor registers the stat, quantiles, and min/max metric. `add(value)` updates all three families. `snapshot(recordBuilder, all)` emits all component snapshots. `close()` stops quantile threads/resources.

## State, dependencies, and integration

State is the three metrics components. Dependencies are Hadoop metrics2 and local `MetricUtil`/`MutableMinMax`. It integrates with metrics sources that declare `PerformanceMetrics` fields annotated with `@Metric`.

## Risks and test signals

Each quantile interval consumes additional resources and must be stopped. Reflection initialization mutates private fields. Tests should cover annotated-field initialization, add/snapshot propagation, close idempotence expectations, and behavior when no intervals are supplied.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/PerformanceMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/PerformanceMetricsInitializer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/PerformanceMetricsInitializer.java

## Purpose

`PerformanceMetricsInitializer` is the reflection helper that initializes annotated `PerformanceMetrics` fields in a metrics source.

## APIs and control flow

`initialize(source, registry, sampleName, valueName, intervals)` scans declared fields on the source's concrete class. For fields whose type is exactly `PerformanceMetrics` and that carry a Hadoop `@Metric` annotation, it creates a `PerformanceMetrics` instance using the field name and annotation description, sets the field accessible, writes the instance into the source object, and records it in a map keyed by field name.

## State, dependencies, and integration

The class is stateless. It depends on Java reflection, Hadoop metrics annotations, and `MetricsRegistry`. It integrates with `PerformanceMetrics.initializeMetrics`.

## Risks and test signals

Only declared fields on the concrete class are scanned; inherited fields are ignored. Existing field values are overwritten. Tests should cover private field injection, multiple fields, ignored unannotated or subclassed fields, inherited-field behavior, and access failure propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/PerformanceMetricsInitializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ProtobufUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ProtobufUtils.java

## Purpose

`ProtobufUtils` provides small helpers for converting common Java types to HDDS protobuf types and for computing protobuf serialized sizes.

## APIs and control flow

`toProtobuf(UUID)` builds `HddsProtos.UUID` from most and least significant bits. `fromProtobuf` reverses the conversion. `computeRepeatedStringSize` wraps protobuf `computeStringSizeNoTag` for repeated string element sizing. `computeLongSizeWithTag` delegates to `CodedOutputStream.computeInt64Size`.

## State, dependencies, and integration

The class is stateless. It depends on Google protobuf `CodedOutputStream`, Java `UUID`, and HDDS protobufs. It integrates with serialization code that needs exact protobuf size estimates or UUID wire conversion.

## Risks and test signals

Null inputs are not guarded and will throw `NullPointerException`. Tests should cover UUID round trips, known serialized size values, field-number handling, and negative long sizing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ProtobufUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/SeekableIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/SeekableIterator.java

## Purpose

`SeekableIterator<K, E>` extends `ClosableIterator<E>` with explicit repositioning support.

## APIs and control flow

The single added method is `seek(K position) throws IOException`, allowing an implementation to move to a key or logical position before continuing iteration.

## State, dependencies, and integration

The interface has no state and depends on Java `IOException` plus the local `ClosableIterator`. It integrates with DB/table scanners that can seek to a key prefix or resume point.

## Risks and test signals

The semantics of inclusive/exclusive seek are not defined by the interface and must be specified by implementations. Tests should cover implementation-specific seek positioning, seeking before/after bounds, resource closure, and iteration after seek.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/SeekableIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ShutdownHookManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ShutdownHookManager.java

## Purpose

`ShutdownHookManager` is Ozone's forked Hadoop-style shutdown coordinator. It registers one JVM shutdown hook and executes registered hooks deterministically by priority, with per-hook timeouts and an Ozone-specific timeout configuration.

## APIs and control flow

A static singleton installs a JVM hook at class load. During JVM shutdown, it atomically marks shutdown in progress, calls `executeShutdown()`, logs timing, and then shuts down the single-thread executor. Hooks are stored as `HookEntry` objects in a synchronized set and sorted highest priority first at execution. `addShutdownHook` overloads reject null hooks and additions during shutdown. `removeShutdownHook` and `hasShutdownHook` compare by runnable identity. `clearShutdownHooks` exists for tests. `shutdownExecutor` waits for configured timeout, then forces shutdown if needed.

## State, dependencies, and integration

Global state includes the singleton manager, static daemon executor, synchronized hook set, and `AtomicBoolean shutdownInProgress`. It depends on Guava thread factories, HDDS config utilities, `OzoneConfiguration`, Hadoop `Time`, and SLF4J. It integrates with every service component registering cleanup hooks.

## Risks and test signals

Because the executor is static and shut down after JVM shutdown, tests using reflective execution need careful cleanup. Same-priority hooks run in nondeterministic order. Timed-out hooks are interrupted but may ignore interruption. Tests should cover priority ordering, timeout cancellation, duplicate runnable identity, removal, shutdown-in-progress guards, configured minimum timeout, and exception logging without stopping later hooks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ShutdownHookManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/StringWithByteString.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/StringWithByteString.java

## Purpose

`StringWithByteString` is an immutable value object that stores a Java `String` alongside its UTF-8 protobuf `ByteString` representation.

## APIs and control flow

The constructor requires non-null string and byte values. `valueOf(String)` returns null for null input or creates a new instance using `ByteString.copyFromUtf8`. Accessors return the stored string and bytes. `toString()` returns the string value.

## State, dependencies, and integration

State is final and immutable. The class depends on Google protobuf `ByteString` and JCIP `@Immutable`. It integrates with code that repeatedly needs both string and serialized forms without repeated conversion.

## Risks and test signals

The public constructor permits inconsistent string/bytes pairs if callers provide mismatched values; `valueOf` is the safe path. Tests should cover null behavior, UTF-8 conversion, constructor null checks, and `toString`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/StringWithByteString.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/UUIDUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/UUIDUtil.java

## Purpose

`UUIDUtil` generates random RFC 4122 version 4 UUID bytes without constructing a `UUID` object.

## APIs and control flow

`randomUUIDBytes()` allocates 16 bytes, fills them from a thread-local `SecureRandom`, then sets version bits in byte 6 and variant bits in byte 8. The constructor is private.

## State, dependencies, and integration

State is a `ThreadLocal<SecureRandom>`. The class depends only on Java security APIs. It integrates with ID-generation paths that need raw UUID bytes for storage or protobuf fields.

## Risks and test signals

Thread-local secure random instances avoid contention but can be heavier per thread. Tests should verify length, RFC 4122 version/variant bits, non-constant output, and no shared mutable returned arrays.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/UUIDUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/UUIDv7.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/UUIDv7.java

## Purpose

`UUIDv7` generates time-ordered UUID version 7 values using the current millisecond timestamp and random trailing bytes.

## APIs and control flow

`randomBytes()` fills 16 bytes with secure random data, writes the low 48 bits of `System.currentTimeMillis()` into bytes 0 through 5, then sets version 7 and RFC variant bits. `randomUUID()` wraps the byte array in a `ByteBuffer`, reads two longs, and constructs a Java `UUID`.

## State, dependencies, and integration

State is a thread-local `SecureRandom`. Dependencies are Java `ByteBuffer`, `SecureRandom`, and `UUID`. It integrates with ID-generation paths that benefit from roughly sortable UUIDs.

## Risks and test signals

UUIDv7 monotonicity within the same millisecond is not guaranteed because the random tail is not incremented. Clock rollback can break ordering. Tests should validate version/variant bits, timestamp placement, UUID-byte round trip, and ordering only across distinct milliseconds.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/UUIDv7.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.util` as utility classes required for Ozone.

## APIs and integration

It has no executable API. In this subset the package contains metrics helpers, iterator contracts, network utilities, shutdown management, protobuf utilities, and UUID helpers.

## State, dependencies, risks, and test signals

No runtime state exists in the descriptor. Compile and JavaDoc checks are sufficient; stale package documentation is the only risk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/utils/FormattingCLIUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/utils/FormattingCLIUtils.java

## Purpose

`FormattingCLIUtils` renders centered ASCII tables for Ozone CLI output. It supports an optional title, header rows, and data rows with computed column widths.

## APIs and control flow

Construction initializes an internal `StringBuilder`, row list, and max-column map. `addHeaders` and `addLine` append rows after converting values to strings and updating column widths. `appendRows` rejects a row with fewer columns than previously seen, but it permits more columns and expands the table. `render()` calls `buildTable`, which emits title, borders, headers, and data lines. `StrUtils` provides center, left-pad, right-pad, and repeat helpers.

## State, dependencies, and integration

State is mutable table content and a builder reused during rendering. There are no external dependencies. It integrates with command-line tools that need human-readable table output.

## Risks and test signals

`render()` is not idempotent because it appends to the same builder each call. All padding uses Java string length, not display width, so wide Unicode or ANSI escape sequences will misalign. Tests should cover title truncation, column mismatch behavior, null values, multiple headers, no rows, and repeated render calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/utils/FormattingCLIUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/utils/package-info.java

## Purpose

This descriptor marks `org.apache.hadoop.ozone.utils` as a utility package for Ozone.

## APIs and integration

There is no executable API. In this subset it contains `FormattingCLIUtils`, the ASCII table renderer used by CLI paths.

## State, dependencies, risks, and test signals

The file has no state. Compile and JavaDoc validation are sufficient. The only risk is ambiguity with the similarly named `org.apache.hadoop.ozone.util` package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/CustomizedCallbackHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/CustomizedCallbackHandler.java

## Purpose

`CustomizedCallbackHandler` is an extension point for handling SASL callbacks not recognized by the forked Hadoop RPC SASL server code.

## APIs and control flow

The main method is `handleCallbacks(List<Callback>, String name, char[] password)`. The nested `Cache` resolves a configured class by key, caches it, and falls back to `DefaultHandler` if instantiation fails or the configured class is default. Non-interface objects are adapted reflectively by looking for a `handleCallbacks(List, String, char[])` method. `DefaultHandler` throws `UnsupportedCallbackException` for the first unknown callback.

## State, dependencies, and integration

Global state is a synchronized static map from config key to handler. Dependencies include Hadoop `Configuration`, Java callback APIs, reflection, and SLF4J. `SaslRpcServer.SaslDigestCallbackHandler` uses it for unknown DIGEST callbacks after resolving token username and password.

## Risks and test signals

The cache key is only the config key, not the configured class or configuration instance, so class changes can be hidden until `clear()` is called. Reflection wraps invocation failures as `IOException`. Tests should cover default fallback, custom interface implementation, reflective delegate, instantiation failure, cache clearing, and unknown callback propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/CustomizedCallbackHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslMechanismFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslMechanismFactory.java

## Purpose

`SaslMechanismFactory` centralizes the effective SASL mechanism used for Hadoop token/digest authentication in this forked security package.

## APIs and control flow

`getMechanism()` lazily resolves the mechanism from `HADOOP_SASL_MECHANISM` environment variable, then Hadoop configuration key `hadoop.security.sasl.mechanism`, then default `DIGEST-MD5`, caching the result in a volatile field. `getMechanismName(AuthMethod)` returns the configured mechanism for `DIGEST` and `TOKEN`, otherwise the mechanism name built into Hadoop's `AuthMethod`. Helpers identify default and digest mechanisms. `main` prints the effective value.

## State, dependencies, and integration

State is the cached effective mechanism. Dependencies include Hadoop `Configuration`, Hadoop `SaslRpcServer.AuthMethod`, and SLF4J. Both `SaslRpcClient` and `SaslRpcServer` use it when validating advertised auth types and creating clients/servers.

## Risks and test signals

The cached value cannot be refreshed except by classloader reset, so tests that change env/config need isolation. Creating a new `Configuration` ignores service-specific config objects. Tests should cover env precedence, default fallback, TOKEN/DIGEST mapping, non-digest auth method passthrough, and client/server agreement when a custom mechanism is configured.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslMechanismFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslRpcClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslRpcClient.java

## Purpose

`SaslRpcClient` encapsulates client-side SASL negotiation for the forked Hadoop IPC package. It supports SIMPLE fallback, token-based DIGEST-style authentication, Kerberos/GSSAPI authentication, principal validation, and optional stream wrapping for integrity/privacy QoP.

## APIs and control flow

Construction records UGI, protocol, server address, configuration, and SASL properties resolver. `saslConnect` sends a NEGOTIATE request, reads SASL RPC packets, handles server ERROR/FATAL responses, selects the first supported auth type, creates a `SaslClient`, evaluates challenges, handles SUCCESS, and returns the negotiated `AuthMethod`. `selectSaslClient` filters advertised auths through `isValidAuthType`, supports SIMPLE without creating a SASL client, and throws `AccessControlException` if no usable auth remains. `createSaslClient` resolves token credentials or validates Kerberos principals before calling `Sasl.createSaslClient`. `getInputStream` and `getOutputStream` wrap streams when negotiated QoP is not `auth`.

## State, dependencies, and integration

State includes `saslClient`, `authMethod`, UGI, protocol, server address, configuration, and resolver. Dependencies include Hadoop security APIs, token selectors, Kerberos annotations, forked IPC protobufs, Ratis/Hadoop RPC helpers, protobuf `ByteString`, RE2/J glob patterns, and the local `SaslMechanismFactory`. It integrates directly with `Client.IpcStreams` and RPC connection setup.

## Risks and test signals

Principal validation is strict unless a `<serverKey>.pattern` override is configured. Wrapped input requires every post-negotiation packet to be SASL WRAP, otherwise it throws. `useWrap()` assumes negotiation completed and `saslClient` exists. Tests should cover SIMPLE negotiation, token selection failure, Kerberos principal mismatch, challenge/response token presence, malformed packet detection, QoP wrapping/unwrapping, disposal, and auth method reporting after failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslRpcClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslRpcServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslRpcServer.java

## Purpose

`SaslRpcServer` encapsulates server-side SASL setup for the forked Hadoop IPC layer. It maps Hadoop `AuthMethod` values to configured SASL mechanisms, creates SASL servers for token and Kerberos modes, and provides token encoding/decoding and callback handlers.

## APIs and control flow

Construction records auth method, mechanism, protocol, and server ID. SIMPLE returns without SASL setup; TOKEN uses an empty protocol and default realm; KERBEROS parses the current user's service principal. `create(connection, saslProperties, secretManager)` builds a token or Kerberos callback handler, optionally runs creation as the current UGI, and errors if no `SaslServer` implementation exists. `init` installs the PLAIN security provider and builds a cached `FastSaslServerFactory`. Token helpers base64-encode identifiers and passwords and reconstruct token identifiers from serialized bytes.

## State, dependencies, and integration

Static state is the cached `SaslServerFactory`. Instance state describes the selected auth method and SASL service identity. Dependencies include Hadoop UGI, token `SecretManager`, forked IPC server connection, Hadoop `SaslPlainServer`, local customized callbacks, Java SASL APIs, and Commons Base64. It integrates with RPC server connection authentication.

## Risks and test signals

`init` must run before `create`, or `saslFactory` is null. Kerberos construction assumes principal parsing by splitting on `/` and `@`. The digest callback sets `connection.attemptingUser` before authorization completes, so caller handling must treat it carefully. Tests should cover factory initialization, token password lookup, invalid token deserialization, authorization ID mismatch, customized unknown callbacks, Kerberos missing host part, and mechanism cache contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslRpcServer.java -->
