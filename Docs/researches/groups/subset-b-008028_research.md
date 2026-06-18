# Research: subset-b-008028

Grouped source research for Apache Ozone RocksDB checkpoint differ, SST file iteration, compaction log serialization, and related tests. Each section preserves the original source path in its title and is wrapped for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/TestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/TestUtils.java

Purpose: Test-only helper for generating representative optional lower/upper bound values from a sorted key set. It supports RocksDB SST iterator tests that need many boundary combinations without enumerating every key.

Important APIs/types/functions: `TestUtils` is a final utility class with a private constructor. `getTestingBounds(SortedMap<String, Integer>)` returns `List<Optional<String>>` containing a key below the first key, the first key, decile samples from the sorted key set, a key above the last key, and `Optional.empty()` to represent an unbounded side. It depends on `StringUtils.getLexicographicallyLowerString` and `getLexicographicallyHigherString`.

Control flow and state: The method is stateless. For non-empty maps it copies keys into an ordered list, samples ten positions with `(i * size / 10) - 1`, converts each boundary to `Optional.of`, then appends an empty optional. Empty input produces only the unbounded marker.

Dependencies and integration points: Used by native/raw SST iterator tests and checkpoint differ SST set tests to exercise RocksDB iterate bounds. The helper assumes the sorted map order matches the string comparison used by RocksDB/string codecs.

Risks: For very small maps, decile arithmetic repeats indexes, but the intermediate `HashSet` deduplicates. Boundary output order is not stable because the set is unordered; tests must treat it as a sampling set, not as a deterministic sequence.

Test signals: Coverage comes indirectly through `TestManagedRawSSTFileIterator` and `TestSstFileSetReader`, which use all lower/upper bound pairs and validate emitted keys against map filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/TestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/db/TestManagedRawSSTFileIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/db/TestManagedRawSSTFileIterator.java

Purpose: Native-only parameterized tests for `ManagedRawSSTFileReader` and `ManagedRawSSTFileIterator`, validating raw SST iteration across key/value formats, tombstones, large strings, special characters, iterator modes, and lower/upper bounds.

Important APIs/types/functions: The class is enabled only when the `rocks_tools_native` system property is true. `init()` loads the native raw SST library. `createSSTFileWithKeys` writes a temporary SST with sorted keys, using operation type `0` for deletes and non-zero for puts. `keyValueFormatArgs` combines multiple key/value format cases with every `IteratorType`.

Control flow and state: Each test builds a `TreeMap<Pair<String,Integer>,String>`, writes it as an SST file, opens a raw reader, generates sampled bounds via `TestUtils.getTestingBounds`, and for every lower/upper pair compares iterator output with an independently filtered expected map. The assertions honor `IteratorType`: keys or values may be intentionally null when the mode does not read them.

Dependencies and integration points: Relies on RocksDB native tooling, managed RocksDB option/env wrappers, `ManagedSlice` bounds, `StringCodec`, and Apache Commons `Pair`/random string helpers. It tests the raw iterator used by checkpoint differ pruning code and `SstFileSetReader.getKeyStreamWithTombstone`.

Risks: Tests are skipped unless native tooling is enabled, so CI lanes without the property do not cover raw tombstone iteration. Large random prefix cases increase confidence in buffer handling and escaping, but expected ordering still depends on RocksDB's byte/string ordering matching Java `TreeMap` ordering for the generated data.

Test signals: Strong signals include all `IteratorType` modes, null/newline/quote content, long key/value prefixes, delete and put entries, and exhaustive sampled bound pairs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/db/TestManagedRawSSTFileIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs exclusion filter for the `rocksdb-checkpoint-differ` Maven module.

Important APIs/types/functions: The file contains a valid XML `FindBugsFilter` root and no exclusion entries.

Control flow and state: There is no runtime control flow. Build tooling reads the file from the module POM's `spotbugs-maven-plugin` configuration.

Dependencies and integration points: Integrated by `pom.xml` through `${basedir}/dev-support/findbugsExcludeFile.xml`. It establishes a module-local place for future static-analysis suppressions.

Risks: Empty filters are low risk, but future suppressions here could hide real native resource leaks, iterator contract problems, or RocksDB exception handling defects if added too broadly.

Test signals: Build/static-analysis validation should confirm the file remains parseable XML and that SpotBugs runs with the expected filter path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/pom.xml

Purpose: Maven module descriptor for Apache Ozone's RocksDB checkpoint differ jar, which packages compaction DAG tracking, compaction log entities, SST utilities, and tests.

Important APIs/types/functions: The artifact is `org.apache.ozone:rocksdb-checkpoint-differ:2.3.0-SNAPSHOT`, parented by `hdds`. Dependencies include Guava graph utilities, protobuf, commons libraries, HDDS common/config/interface/managed-rocksdb/rocks-native, Ratis common, RocksDB JNI, and SLF4J. Test dependencies include Hadoop common, the `hdds-rocks-native` test jar, and HDDS test utilities.

Control flow and state: Build configuration points SpotBugs at the module-local empty exclude filter and disables annotation processing via `maven-compiler-plugin` `<proc>none</proc>`. The `native-testing` profile activates on the `rocks_tools_native` property and extends Surefire's `java.library.path` to the built native RocksDB tooling.

Dependencies and integration points: This POM binds the module to Ozone's managed RocksDB wrappers and native raw SST tooling. Tests that require raw SST support depend on the native profile and system property.

Risks: Native tests can silently skip when the property/library path is missing. The module depends on generated protobuf classes from HDDS interfaces, so schema changes must stay compatible with `CompactionFileInfo` and `CompactionLogEntry` codecs.

Test signals: Run normal module tests plus the `native-testing` profile to cover both managed RocksDB iterator paths and native raw SST tombstone paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedSstFileIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedSstFileIterator.java

Purpose: Package-private abstract iterator that wraps RocksDB `SstFileReader` iteration in HDDS managed-resource types and exposes a `ClosableIterator<T>` contract.

Important APIs/types/functions: The constructor opens a `ManagedSstFileReader`, creates a `ManagedSstFileReaderIterator`, seeks to first, stores an `IteratorType`, and initializes reusable key/value `Buffer` instances backed by `CodecBuffer` capacity hints. `getIteratorValue(CodecBuffer key, CodecBuffer value)` is abstract and lets callers decode only the requested fields. `hasNext`, `next`, and `close` implement iteration and cleanup.

Control flow and state: `hasNext` delegates to RocksDB iterator validity. `next` reads key/value buffers only when the `IteratorType` requests them, calls subclass decoding, then advances the RocksDB iterator. `close` is synchronized and idempotently closes the iterator and reader and releases buffers.

Dependencies and integration points: Used by `SstFileSetReader.getKeyStream` to read regular SST keys without tombstones. Depends on managed RocksDB reader/read options, `Buffer`, `CodecBuffer`, `IteratorType`, and Ozone `ClosableIterator`.

Risks: `next` does not check `hasNext`; callers should obey iterator protocol. Resource safety depends on consumers closing the iterator, though higher-level merge iterators close exhausted iterators. Buffer lifetime is shared per iterator, so decoded values should not hold mutable buffer references beyond the call unless copied.

Test signals: Covered through `TestSstFileSetReader` regular key stream cases and merge iterator cleanup tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedSstFileIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/MinHeapMergeIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/MinHeapMergeIterator.java

Purpose: Generic closable merge iterator that combines multiple already-sorted closeable iterators into sorted groups using a priority queue.

Important APIs/types/functions: Type parameters are key `K`, iterator `I extends Iterator<K> & Closeable`, and output `V`. Subclasses implement `getIterator(int)` and `merge(Map<Integer,K>)`. `hasNext` lazily initializes all iterators and heap entries. `next` polls every heap entry whose current key compares equal and passes the per-source key map to `merge`. `HeapEntry` stores iterator index, current key, and comparator.

Control flow and state: Initialization creates and stores one iterator per index, advances each once, and closes empty iterators. If initialization throws, already-opened iterators are closed. During iteration, exhausted iterators are closed immediately. `close` closes all registered iterators and wraps the last `IOException` in `UncheckedIOException`.

Dependencies and integration points: Used by `SstFileSetReader.MultipleSstFileIterator` to merge keys across SST files and suppress duplicates. Its comparator determines ordering and grouping semantics.

Risks: `HeapEntry.equals` and `hashCode` are based on current key rather than iterator identity; this is acceptable for priority queue use but would be risky in hash collections. Duplicate grouping requires all source iterators to be sorted under the same comparator. Only the last close exception is retained.

Test signals: `TestMinHeapMergeIterator` covers sorted merge order, duplicate source grouping, empty iterator closure, idempotent close, initialization exception cleanup, and no-element behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/MinHeapMergeIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileWriter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileWriter.java

Purpose: Closeable wrapper around RocksDB's `SstFileWriter` for writing new SST files from byte arrays or `CodecBuffer` instances, including tombstone entries.

Important APIs/types/functions: The constructor opens a new managed SST writer for a target `File`. Public methods are `put(byte[], byte[])`, `put(CodecBuffer, CodecBuffer)`, `delete(byte[])`, `delete(CodecBuffer)`, and `close()`. `keyCounter` tracks whether `finish()` should be called. `closeOnFailure` closes native resources when RocksDB operations fail.

Control flow and state: Each successful put/delete increments `keyCounter`. `close` calls `finish()` only for non-empty files because RocksDB rejects finishing empty SSTs, then closes writer/options/env options and resets the counter. CodecBuffer deletes wrap the key in `ManagedDirectSlice`.

Dependencies and integration points: Used by `RocksDBCheckpointDiffer.removeValueFromSSTFile` to rewrite backed-up SSTs with keys and empty values or tombstones while pruning OMKeyInfo payloads. Depends on managed RocksDB native wrappers and `RocksDatabaseException`.

Risks: Writer order requirements are inherited from RocksDB; callers must write sorted keys. The class is single-use after close because resources are nulled/closed. Exceptions during close are propagated as `RocksDatabaseException`.

Test signals: `TestRDBSstFileWriter` exercises CodecBuffer reuse, put/delete tombstone creation, empty value writing, native raw readback, and file existence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/SstFileSetReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/SstFileSetReader.java

Purpose: High-level reader for a collection of SST files that exposes merged key streams and estimated key counts across files.

Important APIs/types/functions: `getEstimatedTotalKeys()` sums RocksDB table property entry counts and caches the result. `getKeyStream(lower, upper)` reads regular keys through `ManagedSstFileIterator` and managed `ReadOptions` bounds. `getKeyStreamWithTombstone(lower, upper)` uses native `ManagedRawSSTFileReader` and raw iterator so delete records are included. Nested `MultipleSstFileIterator<T>` extends `MinHeapMergeIterator` and returns one representative value per merged duplicate key.

Control flow and state: Estimated count is lazily computed with double-checked synchronization. Key stream constructors create per-stream options and optional lower/upper `ManagedSlice`s, then lazily open per-file iterators during heap initialization. Close releases iterators, options, read options, and slices.

Dependencies and integration points: This class bridges snapshot diff SST file lists to key iteration. It depends on string codecs, managed RocksDB SST readers, raw native reader support for tombstones, and `MinHeapMergeIterator`.

Risks: Duplicate merge returns an arbitrary value from equal keys because `merge` uses `findAny`; this is fine for key-only streams but would not preserve newest-file value semantics. Native tombstone mode requires optional native library availability. Bounds must be encoded consistently with SST key encoding.

Test signals: `TestSstFileSetReader` covers zero/multiple file counts, lower/upper bounds, tombstone-including native mode, overlapping SST files, duplicate suppression, sorted output, and large binary-ish key prefixes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/SstFileSetReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/TablePrefixInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/TablePrefixInfo.java

Purpose: Immutable holder for table/column-family prefix strings used to filter SST files during snapshot diff.

Important APIs/types/functions: Constructor wraps the provided `Map<String,String>` with `Collections.unmodifiableMap`. Public methods are `getTablePrefix(String)`, `size()`, `getTableNames()`, and `toString()`.

Control flow and state: There is no mutation after construction. Missing table names return the empty string, allowing callers to treat absent prefixes as broad/no-prefix lookups.

Dependencies and integration points: Used by `RocksDiffUtils.filterRelevantSstFiles` and `RocksDBCheckpointDiffer.getSSTDiffList` to remove SST files whose key range cannot contain requested table prefixes.

Risks: The constructor does not make a defensive copy, so later mutation of the original map can affect the unmodifiable view. Empty prefix fallback can make filters permissive if table names are missing.

Test signals: Filter behavior is indirectly testable through RocksDiffUtils and snapshot diff tests with table-specific key ranges.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/TablePrefixInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java

Purpose: Package-level documentation for RocksDB utility classes in `org.apache.hadoop.hdds.utils.db`.

Important APIs/types/functions: Declares the package and documents it as a utility package for RocksDB.

Control flow and state: No runtime behavior or state.

Dependencies and integration points: Groups `ManagedSstFileIterator`, `MinHeapMergeIterator`, `RDBSstFileWriter`, `SstFileSetReader`, and `TablePrefixInfo` under HDDS DB utilities.

Risks: Minimal. If package responsibilities grow, this terse documentation may become too vague to guide API users.

Test signals: Compile/package documentation validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionFileInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionFileInfo.java

Purpose: Persistent compaction-log representation of an SST file, extending `SstFileInfo` with a mutable `pruned` flag.

Important APIs/types/functions: Constructors accept file name, optional start/end key range, column family, and prune status. `getProtobuf()` serializes to `HddsProtos.CompactionFileInfoProto`; `getFromProtobuf` deserializes. `Builder` requires non-null file name, can populate metadata from RocksDB `LiveFileMetaData`, and enforces all-or-none presence for start range, end range, and column family.

Control flow and state: `setPruned()` mutates the flag after construction. Serialization includes optional range fields only when present and always writes file name/pruned. Equality and hash code include base SST metadata and prune state.

Dependencies and integration points: Used by `CompactionLogEntry`, `CompactionDag.populateCompactionDAG`, and `RocksDBCheckpointDiffer` event listeners/pruning queue. The pruned bit records whether OMKeyInfo values have already been stripped from backed-up source SST files.

Risks: Mutability of `pruned` means objects shared from a log entry can change while referenced elsewhere. The all-or-none validation protects prefix filtering from partial metadata, but older legacy entries may intentionally lack all range fields.

Test signals: `TestCompactionFileInfo` covers valid/invalid builder combinations, pruned flag mutation, protobuf optional fields, and pruned deserialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionFileInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionLogEntry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionLogEntry.java

Purpose: DAO and codec target for one RocksDB compaction event persisted in the compaction log table.

Important APIs/types/functions: Fields are DB sequence number, compaction time, input file info list, output file info list, and optional compaction reason. `CODEC` is a `DelegatedCodec` over `CompactionLogEntryProto`. Public APIs include getters, `getProtobuf`, `getFromProtobuf`, `toBuilder`, `equals`, `hashCode`, and `copyObject`. `Builder` constructs entries and can replace the input file list during value-pruning updates.

Control flow and state: The entry object stores list references as provided and is otherwise immutable. Serialization writes sequence/time, optional reason, and file-info protos. Deserialization rebuilds `CompactionFileInfo` lists before constructing the entry.

Dependencies and integration points: Written by `RocksDBCheckpointDiffer.addToCompactionLogTable`, loaded from RocksDB during DAG reconstruction, and updated after SST value pruning marks input files as pruned.

Risks: `copyObject` is shallow for lists and file info objects, so callers needing isolation must copy nested objects. Persisted key ordering is external to this class and must remain compatible with pruning scans.

Test signals: `TestCompactionLogEntry` covers protobuf round trip with and without compaction reason and equality of nested file info lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionLogEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/package-info.java

Purpose: Package-level documentation for compaction information POJOs.

Important APIs/types/functions: Declares `org.apache.ozone.compaction.log`.

Control flow and state: No runtime logic.

Dependencies and integration points: Documents the package containing `CompactionFileInfo` and `CompactionLogEntry`, the persisted data model for compaction DAG reconstruction and SST pruning.

Risks: Minimal, though the package description does not mention protobuf persistence or pruning metadata.

Test signals: Compile/package validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/RdbUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/RdbUtil.java

Purpose: Utility methods for collecting live RocksDB SST metadata by column family, primarily for snapshot-diff comparison support.

Important APIs/types/functions: `getLiveSSTFilesForCFs(ManagedRocksDB, Set<String>)` filters RocksDB live file metadata by column family. `getSSTFilesForComparison` maps those entries to `SstFileInfo` set values. `getSSTFilesWithInodesForComparison` maps filesystem inode values to `SstFileInfo` using `IOUtils.getINode`.

Control flow and state: The class is stateless. Each method calls RocksDB live metadata at invocation time, filters by decoded column-family name, and builds fresh collections.

Dependencies and integration points: Depends on `ManagedRocksDB`, RocksDB `LiveFileMetaData`, HDDS string conversion, filesystem inode lookup, and `SstFileInfo`. It can be used to compare snapshot hard links or live SST identities.

Risks: The class comment says it is temporary. Inode-based comparison depends on filesystem support and can throw `IOException`. Live metadata is a point-in-time view and can race with RocksDB compaction unless callers coordinate.

Test signals: `TestSstFileInfo` validates `SstFileInfo` construction from mocked live metadata; broader integration should test live DB metadata and inode behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/RdbUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/SstFileInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/SstFileInfo.java

Purpose: Base value object describing an SST file by extensionless file name, key range, and column family.

Important APIs/types/functions: Constructors accept explicit fields or RocksDB `LiveFileMetaData`. The metadata constructor strips `.sst` via `FilenameUtils.getBaseName` and decodes smallest/largest keys and column family bytes. Methods expose fields, equality/hash code, `copyObject`, `toString`, and `getFilePath(Path)` which appends `.sst`.

Control flow and state: Instances are immutable. Equality requires all four metadata fields to match, so file name alone is not considered sufficient identity.

Dependencies and integration points: Extended by `CompactionFileInfo` and `CompactionNode`; used in snapshot version maps, diff results, and path lookup for backup/source SSTs.

Risks: Key ranges are decoded as strings, so binary key encodings must be compatible with the string conversion used elsewhere. Equality including key range and column family means the same file name with changed metadata is treated as different in set comparison.

Test signals: `TestSstFileInfo` verifies conversion from mocked `LiveFileMetaData`, including base-name extraction and byte-to-string decoding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/SstFileInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/package-info.java

Purpose: Package-level documentation for Ozone RocksDB utility classes.

Important APIs/types/functions: Declares `org.apache.ozone.rocksdb.util`.

Control flow and state: No runtime behavior.

Dependencies and integration points: Covers utility classes such as `RdbUtil` and `SstFileInfo`, which bridge RocksDB live metadata to checkpoint differ data structures.

Risks: Minimal. The description is intentionally broad and does not document snapshot-diff-specific constraints.

Test signals: Compile/package validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionDag.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionDag.java

Purpose: In-memory representation of SST compaction history as paired directed graphs plus a file-name-to-node map.

Important APIs/types/functions: `populateCompactionDAG` creates/reuses `CompactionNode`s for input/output `CompactionFileInfo` values and draws edges. `forwardCompactionDAG` stores edges from output SST to input SST. `backwardCompactionDAG` stores edges from input SST to output SST. `pruneNodesFromDag`, `pruneBackwardDag`, and `pruneForwardDag` remove connected history around old snapshot levels. Accessors expose both graphs, the map, and node lookup.

Control flow and state: Nodes are inserted with `computeIfAbsent`; output files are outer-looped, input files inner-looped, and self-edges are skipped. Pruning walks level by level through predecessors or successors, removing nodes and collecting file names. `pruneNodesFromDag` prunes both graph directions and removes start nodes from the node map.

Dependencies and integration points: Used by `RocksDBCheckpointDiffer` to populate history from live compaction events and persisted compaction log entries, traverse diffs, and prune old history.

Risks: Guava `MutableGraph` is not inherently thread-safe; callers synchronize in `RocksDBCheckpointDiffer` during mutation/traversal-sensitive operations. `CompactionNode.equals` is identity-based while hash code uses file name, so node reuse through the map is important.

Test signals: `TestCompactionDag` validates forward/backward prune scenarios and end-to-end pruning after log/table reconstruction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionDag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionNode.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionNode.java

Purpose: Graph node representing one SST file in the compaction DAG, extending SST metadata with snapshot generation and traversal counters.

Important APIs/types/functions: Constructors accept raw fields or `CompactionFileInfo`. Public methods expose `snapshotGeneration`, `totalNumberOfKeys`, `cumulativeKeysReverseTraversal`, and mutators for cumulative reverse traversal. `equals` is final and identity-only; `hashCode` hashes file name.

Control flow and state: The main constructor stores inherited file metadata and initializes total/cumulative key counts to zero. `snapshotGeneration` is immutable. Cumulative traversal state is mutable but not used heavily in the current differ path.

Dependencies and integration points: Created by `CompactionDag`; returned as `SstFileInfo`-compatible diff entries in `RocksDBCheckpointDiffer.internalGetSSTDiffList` when traversal reaches different files.

Risks: Identity equality with filename hash code violates the usual equals/hashCode expectation for separately constructed nodes with the same file name. The DAG relies on canonical nodes in `compactionNodeMap` to avoid duplicate logical nodes.

Test signals: DAG pruning and diff traversal tests exercise node identity through graph membership and file-name extraction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/DifferSnapshotInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/DifferSnapshotInfo.java

Purpose: Snapshot descriptor used by the checkpoint differ to map snapshot versions to DB paths and SST file metadata.

Important APIs/types/functions: Stores snapshot UUID, generation, a version-to-DB-path function, and a `NavigableMap<Integer,List<SstFileInfo>>`. Public methods return DB path, UUID, generation, and max version. Package-private `getSstFiles(version, tablesToLookup)` filters SST metadata by requested column families. Test-visible `getSstFile` finds one named file.

Control flow and state: The object is immutable by field reference, but it does not defensively copy the supplied map/lists. `getMaxVersion` delegates to `lastKey`, so version maps must be non-empty.

Dependencies and integration points: Used by `RocksDBCheckpointDiffer.DifferSnapshotVersion` and `getSSTDiffListWithFullPath` to build source/destination version views for DAG or full-name diffing.

Risks: Missing versions, empty maps, or null column-family values can cause runtime errors. External mutation of `versionSstFiles` can affect diff behavior.

Test signals: Diff tests should cover multi-version snapshots, table filtering, missing version maps, and path function correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/DifferSnapshotInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/RocksDBCheckpointDiffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/RocksDBCheckpointDiffer.java

Purpose: Core checkpoint differ service for Ozone Manager RocksDB. It listens to RocksDB compaction events, persists compaction history, builds/reconstructs an SST compaction DAG, computes SST diff candidates between snapshots, and prunes old history/backup SST data.

Important APIs/types/functions: Public setup methods attach RocksDB event listeners, column-family handles, and active DB. Compaction listeners call `shouldSkipCompaction`, hard-link input SSTs to backup on begin, and on completion persist a `CompactionLogEntry`, populate `CompactionDag`, and enqueue entries for value pruning. `loadAllCompactionLogs` migrates legacy text logs and loads the compaction log table. `getSSTDiffList` and `getSSTDiffListWithFullPath` compute diff candidates. Pruning APIs include `pruneOlderSnapshotsWithCompactionHistory`, `pruneSstFiles`, `pruneSstFileValues`, and DAG prune helpers.

Control flow and state: The constructor creates metadata subdirectories, configures scheduler intervals, optional native raw-SST pruning queue, metrics, and compaction DAG state. Compaction log table keys are zero-padded sequence numbers plus compaction time for lexicographic chronological scans. DAG traversal starts from source snapshot SSTs, follows output-to-input graph edges, marks files as same when a destination SST is reached, and returns empty optional if destination files cannot be accounted for. Pruning scans old log-table entries, removes graph nodes/files under bootstrap read lock, and rewrites backed-up SST files with key-only data when native tooling is available.

Dependencies and integration points: Integrates RocksDB JNI listeners, HDDS managed RocksDB wrappers, protobuf compaction log entities, native raw SST reader/writer utilities, Ozone configuration keys, bootstrap state locking, scheduler, metrics, and table-prefix filtering.

Risks: Event listener races are acknowledged through `inflightCompactions` fallback logging. Graph mutation requires synchronization. Native value pruning is optional and failures update metrics but leave queue/data state to retry semantics. Legacy text log parsing is permissive for deletion lines but malformed lines are mostly logged. Full diff fallback occurs when DAG traversal cannot account for destination SSTs.

Test signals: `TestCompactionDag` validates log migration, table loading, pruning, and bootstrap lock behavior. Additional tests should cover compaction listener skip cases, prefix filtering, `getSSTDiffListWithFullPath`, native prune updates, and scheduler suspension/resume.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/RocksDBCheckpointDiffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/RocksDiffUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/RocksDiffUtils.java

Purpose: Static helper methods for filtering SST diff candidates by table/column-family prefix coverage.

Important APIs/types/functions: `isKeyWithPrefixPresent(prefix, firstDbKey, lastDbKey)` checks whether a prefix falls within an SST key range using first-N-character comparisons. `filterRelevantSstFiles` overloads mutate a map or set of `SstFileInfo` by removing nodes for which `shouldSkipNode` returns true. `shouldSkipNode` is test-visible and handles missing metadata, empty prefix info, column-family mismatch, and key-range prefix exclusion.

Control flow and state: The filters iterate with mutable iterators and remove irrelevant entries in place. Missing start/end/column-family metadata returns false for backward compatibility, keeping the file rather than risking false exclusion.

Dependencies and integration points: Called by `RocksDBCheckpointDiffer.getSSTDiffList` after DAG/full diff candidate computation. Depends on `TablePrefixInfo` and `SstFileInfo`.

Risks: String-prefix comparison assumes keys are ordered compatibly with Java string comparison and table prefixes map exactly to encoded RocksDB keys. Missing metadata makes filtering conservative, increasing diff work.

Test signals: Useful tests include prefix within/outside range, missing metadata, empty prefix info, column-family exclusion, and map/set mutation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/RocksDiffUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/SSTFilePruningMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/SSTFilePruningMetrics.java

Purpose: Hadoop metrics source for monitoring SST backup value-pruning activity in `RocksDBCheckpointDiffer`.

Important APIs/types/functions: `create(dbLocation)` registers a metrics source named from the class plus sanitized DB location. Metrics include total files pruned, files pruned in last batch, total skipped/removed files, compactions processed, prune queue size, and pruning failures. Public update/getter methods mutate and read these counters/gauges. `getMetrics` snapshots all metrics to a collector.

Control flow and state: Metrics are registered through `DefaultMetricsSystem`. Batch updates increment counters/gauges after pruning runs. `unRegister` removes the source during differ close.

Dependencies and integration points: Used by `RocksDBCheckpointDiffer` constructor, `close`, compaction queue updates, successful pruning batches, and pruning failure handling.

Risks: Source-name sanitization replaces path separators, colon, and whitespace, but very long DB paths can still produce long metric names. Metrics fields are initialized by Hadoop metrics injection/registration; using an instance before registration would be unsafe.

Test signals: Should verify registration/unregistration, sanitized names, queue updates, batch counter increments, and failure counter increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/SSTFilePruningMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/package-info.java

Purpose: Package-level documentation for Ozone RocksDB checkpoint differ classes.

Important APIs/types/functions: Declares `org.apache.ozone.rocksdiff`.

Control flow and state: No runtime logic.

Dependencies and integration points: Groups `RocksDBCheckpointDiffer`, DAG/node structures, snapshot info, filtering utilities, and pruning metrics.

Risks: Minimal. Documentation could be expanded to state that this package owns compaction DAG history and snapshot diff candidate selection.

Test signals: Compile/package validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestMinHeapMergeIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestMinHeapMergeIterator.java

Purpose: Unit tests for generic min-heap merging and resource cleanup behavior in `MinHeapMergeIterator`.

Important APIs/types/functions: Defines `TrackingCloseableIterator` to count closes, `MergeResult` to record merged key and source indexes, and `TestIterator` as a concrete `MinHeapMergeIterator<byte[], TrackingCloseableIterator<byte[]>, MergeResult>` using unsigned byte lexicographic comparison.

Control flow and state: Tests create sorted iterator inputs, trigger lazy initialization via `hasNext`, consume outputs, inspect merged source sets, and verify close counts. Exception tests inject `IOException` or `RocksDatabaseException` from `getIterator` and assert wrapping in `UncheckedIOException` plus cleanup of already-opened iterators.

Dependencies and integration points: Validates the primitive used by `SstFileSetReader` for multi-SST key merging.

Risks: The tests intentionally close never-registered iterators manually in exception cases, confirming the production iterator can only clean registered resources. They do not test comparator inconsistency or unsorted input because those are caller contract violations.

Test signals: Strong coverage of sorted ordering, duplicate grouping across three sources, empty iterator close on init, idempotent close, initialization failure cleanup, and `NoSuchElementException` on empty iteration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestMinHeapMergeIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBSstFileWriter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBSstFileWriter.java

Purpose: Native-only test for writing SST entries from reusable `CodecBuffer` instances and reading back tombstone/value entries.

Important APIs/types/functions: `testSstFileTombstoneCreationWithCodecBufferReuse` loads the raw SST native library, opens `RDBSstFileWriter`, uses a `CodecBuffer` fed by a `PutToByteBuffer` lambda, writes alternating delete and put entries, then reads the SST with `ManagedRawSSTFileReader`.

Control flow and state: The test verifies buffer readable length and content before/after clearing, writes keys in sorted order expected by RocksDB, closes the writer, checks file existence, then iterates raw key/value records and validates operation type and empty value bytes.

Dependencies and integration points: Covers the writer path used by `RocksDBCheckpointDiffer.removeValueFromSSTFile` during key-only SST rewriting.

Risks: Enabled only when native RocksDB tooling is available. The assertion comparing `keys.get(idx)` to itself appears ineffective for validating read key content, so operation type and empty value checks carry most of the signal.

Test signals: Confirms writer close produces a file, CodecBuffer reuse does not corrupt written entries, raw iterator sees tombstone/value operation types, and empty values are preserved.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBSstFileWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestSstFileSetReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestSstFileSetReader.java

Purpose: Parameterized integration-style tests for reading and merging keys from multiple SST files with and without tombstone inclusion.

Important APIs/types/functions: Helpers create deterministic sorted SST files with alternating put/delete operation values and a long `KEY_PREFIX` containing all byte values modulo 256. `testGetKeyStream` validates regular RocksDB iterator output excludes tombstones. `testGetKeyStreamWithTombstone` validates raw native mode includes all keys. Overlap tests validate duplicate suppression and sorted order across multiple SSTs.

Control flow and state: `createDummyData` distributes a sorted key space round-robin over `numberOfFiles`, writes each file, then every sampled lower/upper bound pair is checked by filtering the original key map. Tests run for 0, 1, 2, 3, 7, and 10 files where applicable.

Dependencies and integration points: Exercises `SstFileSetReader`, `ManagedSstFileIterator`, native raw reader mode, `MinHeapMergeIterator`, `TestUtils.getTestingBounds`, and RocksDB SST writer wrappers.

Risks: Some comments say latest file precedence, but the key-only merge only guarantees one key per duplicate and sorted output, not value precedence. Native tombstone coverage is skipped when the native property/library is unavailable.

Test signals: Broad coverage of bounds, empty inputs, multiple file counts, tombstone inclusion/exclusion, large encoded keys, duplicate suppression, and sorted merge behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestSstFileSetReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionFileInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionFileInfo.java

Purpose: Parameterized tests for `CompactionFileInfo` builder validation, prune state, and protobuf serialization.

Important APIs/types/functions: Scenario providers define valid all-fields and file-name-only cases plus invalid partial metadata combinations. Tests cover `Builder`, `setPruned`, `getProtobuf`, and `getFromProtobuf`.

Control flow and state: Valid scenarios build objects, verify initial and mutated pruned state, and then verify protobuf optional field presence. Invalid scenarios assert exact exception messages for null file name or incomplete start/end/column-family triples. From-protobuf tests also check explicit false and true pruned flags.

Dependencies and integration points: Protects the persisted file-info contract consumed by `CompactionLogEntry`, DAG population, and prefix filtering.

Risks: Exact exception message assertions can be brittle under message refactors. Duplicate valid scenario entries add no new coverage.

Test signals: Strong validation for all-or-none metadata, optional protobuf fields, and pruned flag round trip.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionFileInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionLogEntry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionLogEntry.java

Purpose: Parameterized tests for `CompactionLogEntry` protobuf serialization and deserialization.

Important APIs/types/functions: Scenario provider builds common input/output `CompactionFileInfo` lists and runs cases with and without `compactionReason`. Tests use `CompactionLogEntry.Builder`, `getProtobuf`, and `getFromProtobuf`.

Control flow and state: The serialization test builds an entry, converts it to proto, checks sequence/time, maps nested file-info protos back to objects, and verifies optional reason presence. The deserialization test manually builds the proto, deserializes, and checks all fields and nested lists.

Dependencies and integration points: Protects the compaction log table value format used by `RocksDBCheckpointDiffer` for DAG reconstruction and pruning metadata updates.

Risks: Does not cover `toBuilder`, `copyObject`, equality/hash code, or updated input list after pruning. Lists are reused across scenarios, so deep-copy behavior is not tested.

Test signals: Confirms nested file info lists and optional compaction reason survive proto round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionLogEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestSstFileInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestSstFileInfo.java

Purpose: Unit test for constructing `SstFileInfo` from RocksDB `LiveFileMetaData`.

Important APIs/types/functions: The test mocks `LiveFileMetaData.fileName`, `columnFamilyName`, `smallestKey`, and `largestKey`, builds an expected `SstFileInfo`, and compares it to `new SstFileInfo(lfm)`.

Control flow and state: No persistent state. Mockito supplies byte arrays through `StringUtils.string2Bytes`; the constructor under test decodes them and strips the `.sst` basename from `/1.sst` to `1`.

Dependencies and integration points: Verifies the metadata conversion used by `RdbUtil`, `CompactionFileInfo.Builder.setValues`, and compaction listener file-info generation.

Risks: Only one happy path is covered. It does not cover null metadata, binary/non-UTF key bytes, or paths with unusual names.

Test signals: Confirms file-name basename extraction and string decoding of RocksDB metadata fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestSstFileInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestCompactionDag.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestCompactionDag.java

Purpose: End-to-end and structural tests for compaction DAG pruning, legacy compaction log migration, compaction log table loading, and bootstrap-lock interaction.

Important APIs/types/functions: The fixture creates temp-ish active DB, metadata, compaction log, and SST backup directories; configures a `RocksDBCheckpointDiffer` with mocked configuration and a `ReadWriteLock`-backed bootstrap lock; opens a managed RocksDB with checkpoint-differ listeners and compaction log column family. Helpers build synthetic forward/backward Guava graphs from SST levels, count compaction log table entries, and assert lock blocking behavior.

Control flow and state: Parameterized prune scenarios construct expected graph states after removing levels from backward or forward DAGs. End-to-end scenarios write legacy text log files or direct compaction table entries, call `loadAllCompactionLogs`, assert pre-prune table counts, run `pruneOlderSnapshotsWithCompactionHistory` while verifying it waits for a held write lock, then assert remaining graph nodes, deleted legacy log files, and post-prune table counts.

Dependencies and integration points: Covers `CompactionDag`, `RocksDBCheckpointDiffer`, `CompactionLogEntry`, managed RocksDB column families, native library load mocking, Ozone config keys, and bootstrap state locking.

Risks: Uses fixed relative directory names under the test working directory, so cleanup correctness matters. The graph factories encode expected direction conventions; if direction names change, test readability could suffer even if behavior remains.

Test signals: Strong coverage of forward/backward graph pruning, old text log formats with snapshot lines and missing snapshots, direct table entries, aged compaction time pruning, legacy log deletion after migration, table entry deletion, and lock acquisition semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestCompactionDag.java -->
