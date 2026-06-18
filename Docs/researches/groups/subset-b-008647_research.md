# subset-b-008647 Research

Grouped research report for RocksDB public write-batch/wide-column APIs, Java JNI build and benchmark support, cross-build scripts, JMH microbenchmarks, PMD rules, and selected Java native bridge files. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/types_util.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/types_util.h

Purpose: Declares helper APIs for converting between user-facing keys and raw-table internal key records, plus parsing internal table iterator keys back into structured entry metadata. This is a small public utility surface for tools that need to inspect SST/raw table contents without depending on internal headers.

Important APIs/types/functions: `GetInternalKeyForSeek`, `GetInternalKeyForSeekForPrev`, and `ParseEntry` all return `Status`, accept the column-family/table `Comparator`, and use `Slice`/`std::string`/`ParsedEntryInfo` from RocksDB public types.

Control flow: The header only declares functions; implementations are expected to encode a seek boundary for forward or reverse raw-table iteration, or decode an internal key from a table iterator. Callers pass the same comparator used to create the column family or SST writer so timestamp or custom-comparator semantics match the table.

State and persistence behavior: No persistent state is owned here. The generated internal key is written into caller-owned `buf`; `ParseEntry` fills caller-owned `ParsedEntryInfo`. Misusing a comparator can make seek boundaries or parsed entries disagree with persisted table encoding.

Dependencies and integration points: Depends on `rocksdb/comparator.h`, `slice.h`, `status.h`, and `types.h`. It integrates with raw table iterators, `SstFileWriter`, and offline table inspection/repair tools.

Risks and edge cases: Comparator mismatch is the main correctness risk, especially with custom comparators or user-defined timestamps. Since these utilities handle internal key bytes, malformed input should be expected to return non-OK status rather than be trusted.

Test signals: Useful coverage would seek raw table iterators using generated keys, validate reverse seek behavior, and feed valid/corrupt internal keys into `ParseEntry` under bytewise and custom comparator configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/types_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/write_batch_with_index.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/write_batch_with_index.h

Purpose: Defines `WriteBatchWithIndex`, an indexed wrapper around `WriteBatch` that keeps a searchable in-memory index of pending writes. It enables read-your-writes behavior, iteration over batch contents by key, and merging batch results with DB reads before the batch is committed.

Important APIs/types/functions: `WriteType`, `WriteEntry`, `WBWIIterator`, and `WriteBatchWithIndex` are the core types. Public operations include `Put`, timestamped `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, `PutLogData`, `Clear`, `GetWriteBatch`, `NewIterator`, `NewIteratorWithBase`, `GetFromBatch`, `GetEntityFromBatch`, `GetFromBatchAndDB`, `MultiGetFromBatchAndDB`, entity variants, savepoint operations, `SetMaxBytes`, `GetDataSize`, `GetCFStats`, `GetWBWIOpCount`, and `GetOverwriteKey`.

Control flow: Each mutation delegates to the underlying `WriteBatch` and updates the index keyed by column family and comparator. Iterators seek and walk the indexed entries, ordering duplicate key updates by recency unless `overwrite_key` collapses non-merge updates. Read APIs first inspect batch entries and then optionally query the DB and resolve merge operands with the DB merge operator.

State and persistence behavior: State is transient until the underlying `WriteBatch` is written to a DB. `rep` hides internal index, stats, savepoints, comparator metadata, and the wrapped serialized batch. Savepoint rollback invalidates open iterators. `PutLogData` is included in the WAL batch but not indexed as key data.

Dependencies and integration points: Depends on public comparator, iterator, status, `WriteBatch`, `WriteBatchBase`, `DB`, `ReadOptions`, `DBOptions`, wide-column result types, and transaction internals through friend classes. It integrates with pessimistic/prepared/unprepared transactions and WBWI memtable support.

Risks and edge cases: `DeleteRange`, timed puts, merge with user timestamps, and attribute-group `PutEntity` are unsupported. Iterator entries are invalidated by later mutations. Merge results can be `MergeInProgress` if the batch alone cannot determine a value. `overwrite_key` changes duplicate-key visibility and single-delete accounting.

Test signals: `WriteBatchWithIndexTest` and transaction tests should cover duplicate ordering, iterator/base-iterator merge behavior, savepoint rollback, wide-column `PutEntity`, `GetFromBatchAndDB`, multi-get statuses, unsupported operation statuses, and overwritten single-delete stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/write_batch_with_index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/version.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/version.h

Purpose: Exposes RocksDB compile-time version macros and runtime build-information helpers. Consumers use it for conditional compilation, artifact labeling, diagnostics, and command-line build banners.

Important APIs/types/functions: `ROCKSDB_MAJOR`, `ROCKSDB_MINOR`, `ROCKSDB_PATCH`, `ROCKSDB_MAKE_VERSION_INT`, `ROCKSDB_VERSION_INT`, and `ROCKSDB_VERSION_GE` provide macro-level version checks. `GetRocksBuildProperties`, `GetRocksVersionAsString`, and `GetRocksBuildInfoAsString` provide runtime strings and property maps.

Control flow: Macro expansion computes an integer version as major * 1,000,000 + minor * 1,000 + patch. Runtime functions are declarations whose implementations return immutable build properties and formatted version/build-info text.

State and persistence behavior: No persistent state is created. The property map returned by reference is process state owned by the implementation. Version macros affect build outputs and Java Makefile version extraction.

Dependencies and integration points: Depends on `rocksdb_namespace.h`, `string`, and `unordered_map`. Java Makefile reads this file to derive `ROCKSDB_MAJOR`, `ROCKSDB_MINOR`, and `ROCKSDB_PATCH`. Build info appears in tools, logs, and release artifacts.

Risks and edge cases: The note says main branch should carry the next planned release number, so downstream packagers must align these macros with released artifacts. Macro arithmetic assumes reasonably bounded major/minor/patch values and numeric literals.

Test signals: Build tests can verify `ROCKSDB_VERSION_GE` around boundary versions, and integration tests can check formatted version strings and build-info banners include the expected version.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/wal_filter.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/wal_filter.h

Purpose: Defines `WalFilter`, a customizable recovery hook that lets applications inspect, modify, skip, stop, or reject WAL records during replay. It is a public extension point for recovery-time policy and migration logic.

Important APIs/types/functions: `WalFilter::Type`, `CreateFromString`, `WalProcessingOption`, `ColumnFamilyLogNumberMap`, `LogRecordFound`, legacy `LogRecord`, and pure virtual `Name` are the key surface. `WalProcessingOption` distinguishes continue, ignore current record, stop replay/discard later logs, and corrupted record.

Control flow: During recovery, RocksDB can first provide column-family log-number/name-id maps, then calls `LogRecordFound` for each WAL record with log metadata, the original `WriteBatch`, an optional replacement batch, and a `batch_changed` flag. The default `LogRecordFound` delegates to the older `LogRecord` overload for compatibility.

State and persistence behavior: The filter does not persist state itself, but its return value directly affects recovered DB state. `kIgnoreCurrentRecord` skips one batch; `kStopReplay` discards logs from the current record onward; a replacement batch changes replayed contents and must not contain more records than the original.

Dependencies and integration points: Inherits `Customizable`, uses `ConfigOptions`, `WriteBatch`, and column-family id/name maps. It integrates with DB recovery, configuration string parsing, WAL replay, and logging through `Name`.

Risks and edge cases: Exceptions must not escape into RocksDB because the code is not exception-safe. Returning a replacement batch with too many records fails recovery. Incorrect log-number/column-family filtering can silently drop required data or replay stale records.

Test signals: `WalFilterTest`, `WALRecoveryModeTest`, and recovery tests should verify skip/stop/corruption behavior, replacement batches, column-family log-number routing, and the legacy `LogRecord` fallback path.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/wal_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/wide_columns.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/wide_columns.h

Purpose: Defines public data structures for RocksDB wide-column entities: individual named columns, non-owning column collections used for writes, and self-contained/pinnable result storage used for reads.

Important APIs/types/functions: `WideColumn`, `WideColumns`, `kDefaultWideColumnName`, `kNoWideColumns`, `PinnableWideColumns`, equality/inequality operators, and stream output are the main elements. `PinnableWideColumns` provides `SetPlainValue`, `SetWideColumnValue`, `Reset`, move construction/assignment, `columns`, and `serialized_size`.

Control flow: `WideColumn` forwards constructor inputs into non-owning `Slice` members. `PinnableWideColumns` either copies, pins, or moves a serialized value into a `PinnableSlice`, then builds an index of `WideColumn` views over that storage. Plain values become one anonymous default column; serialized wide-column values are parsed by `CreateIndexForWideColumns`.

State and persistence behavior: `WideColumn` owns no bytes and depends on caller-managed backing storage. `PinnableWideColumns` owns or pins `value_` and stores `columns_` slices into that buffer. `unresolved_blob_column_indices_` tracks internal blob-index-backed columns for DB internals.

Dependencies and integration points: Depends on `Slice`, `Status`, `PinnableSlice`, `Cleanable`, `DBImpl`, and column-family APIs using `PutEntity`/`GetEntity`. It is referenced by `WriteBatch`, `WriteBatchBase`, and `WriteBatchWithIndex`.

Risks and edge cases: Passing temporary strings to `WideColumn` is unsafe because slices outlive the temporaries. Move logic must rebuild column indexes when pinned data changes address. Parse failures in `SetWideColumnValue` reset the object to avoid exposing invalid column slices.

Test signals: Wide-column tests should verify non-owning lifetime expectations, plain value conversion to the default column, serialized entity parsing, move assignment after copy/pin/move sources, equality/output formatting, and blob-column resolution paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/wide_columns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_batch.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/write_batch.h

Purpose: Defines `WriteBatch`, the standard serialized container for applying an ordered set of updates atomically to a RocksDB database and WAL. It also defines handler callbacks for replaying or inspecting serialized batch records.

Important APIs/types/functions: `SavePoint`, `WriteBatch`, and nested `WriteBatch::Handler` are central. Mutation APIs cover `Put`, timestamped `Put`, `SliceParts` variants, `TimedPut`, `PutEntity`, attribute-group `PutEntity`, `Delete`, `SingleDelete`, `DeleteRange`, `Merge`, and `PutLogData`. Management APIs include `Clear`, savepoint rollback/pop, `Iterate`, `Data`, `Release`, `GetDataSize`, `Count`, `Has*` content flags, `UpdateTimestamps`, checksum verification, WAL termination, constructors from serialized data, copy/move, and `SetMaxBytes`.

Control flow: Mutations append encoded records to `rep_` in insertion order and update count/content metadata. `Iterate` decodes `rep_` and dispatches each record to `Handler` callbacks, whose default implementations preserve old single-column-family behavior or return errors for unimplemented newer record kinds. Savepoints capture serialized size/count/flags and rollback truncates to a prior state.

State and persistence behavior: `rep_` is the durable serialized batch payload used for DB writes and WAL records. `PutLogData` persists only in WAL and does not consume a sequence number. Timestamp state tracks whether in-place timestamp update is needed and maps column-family ids to timestamp sizes when requested. Optional per-key protection bytes support checksum verification.

Dependencies and integration points: Implements `WriteBatchBase`; integrates with DB write path, WAL replay, transaction prepare/commit markers, `WriteBatchInternal`, Java JNI write batch bindings, and `WriteBatchWithIndex`.

Risks and edge cases: Multiple threads need external synchronization for mutations. Handler subclasses must implement non-default column-family callbacks or iteration returns errors. User-defined timestamp APIs require correctly appended timestamp bytes. `TimedPut` is experimental and can break snapshot immutability. `Release` transfers serialized data and clears the batch.

Test signals: `WriteBatchTest`, `WriteBatchHandlerTest`, threaded write batch tests, transaction tests, timestamp tests, checksum tests, and WAL recovery tests should validate encoding order, content flags, savepoints, handler dispatch, timestamp updates, WAL-only log data, protection checksums, and serialized constructor compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_batch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_batch_base.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/write_batch_base.h

Purpose: Defines the abstract write-batch interface shared by `WriteBatch` and indexed or transactional batch implementations. It gives DB-facing code a common mutation surface independent of concrete batch storage.

Important APIs/types/functions: `WriteBatchBase` declares pure virtual `Put`, timestamped `Put`, `TimedPut`, `PutEntity`, attribute-group `PutEntity`, `Merge`, timestamped `Merge`, `Delete`, timestamped `Delete`, `SingleDelete`, timestamped `SingleDelete`, `DeleteRange`, timestamped `DeleteRange`, `PutLogData`, `Clear`, `GetWriteBatch`, savepoint methods, and `SetMaxBytes`. `SliceParts` overloads are virtual with out-of-line default implementations.

Control flow: Concrete subclasses implement the primary `Slice` APIs. The base class supplies common overload structure so clients can call through one type. `GetWriteBatch` bridges abstract implementations back to a concrete serialized `WriteBatch` for DB write submission.

State and persistence behavior: The base class owns no state. Persistence semantics are inherited from implementations: a concrete `WriteBatch` serializes operations directly, while `WriteBatchWithIndex` additionally tracks searchable transient indexes.

Dependencies and integration points: Depends on `attribute_groups.h`, `rocksdb_namespace.h`, `Slice`, `Status`, `ColumnFamilyHandle`, `WriteBatch`, and `SliceParts`. It is used throughout APIs that accept generic batches or transaction write buffers.

Risks and edge cases: The comment contains a spelling typo, but the behavioral risk is API drift: new write record types must be added here and implemented by every subclass. Feature availability differs by subclass, so callers must handle `NotSupported` statuses from indexed or specialized batches.

Test signals: Cross-implementation tests should exercise the same operation set through `WriteBatchBase*`, including unsupported operations, savepoints, max-byte limits, `SliceParts` defaults, and conversion via `GetWriteBatch`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_batch_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_buffer_manager.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/write_buffer_manager.h

Purpose: Declares `WriteBufferManager`, which coordinates memory accounting and optional write stalls across one or more DB instances' memtables. It can also charge memtable memory to a shared cache through dummy reservations.

Important APIs/types/functions: `StallInterface` exposes `Block` and `Signal` callbacks for DB instances. `WriteBufferManager` provides `enabled`, `cost_to_cache`, `memory_usage`, `mutable_memtable_memory_usage`, `dummy_entries_in_cache_usage`, `buffer_size`, `SetBufferSize`, `SetAllowStall`, `ShouldFlush`, `ShouldStall`, `IsStallActive`, `IsStallThresholdExceeded`, `ReserveMem`, `ScheduleFreeMem`, `FreeMem`, `BeginWriteStall`, `MaybeEndWriteStall`, and `RemoveDBFromQueue`.

Control flow: Memtable allocations call `ReserveMem`; pending frees can be moved out of active accounting by `ScheduleFreeMem` and finalized by `FreeMem`. Writers query `ShouldFlush` to trigger flushes when mutable or total memory crosses thresholds. If `allow_stall` is enabled and total usage exceeds the buffer size, DBs enter a queue and are blocked until `MaybeEndWriteStall` signals them.

State and persistence behavior: All state is in-memory: atomic buffer limits, memory-used counters, cache reservation manager, stall queue, mutexes, and stall-active flag. It affects flush timing and write admission, but does not persist data itself.

Dependencies and integration points: Depends on `Cache`, `CacheReservationManager`, atomics, mutexes, condition coordination through `StallInterface`, and internal DB write/flush scheduling. It integrates with shared cache memory budgets and multi-DB deployments.

Risks and edge cases: A zero buffer size disables enforcement and makes memory usage invalid for limiting decisions. Stall state combines lock-protected queue updates with atomic reads, so implementation must avoid lost signals. Charging to cache requires reservation/free paths to stay balanced.

Test signals: `WriteBufferManager` and memtable tests should verify flush thresholds, active versus scheduled-free memory, cache dummy usage, runtime buffer-size changes, stall begin/end signaling, DB queue removal, and disabled/allow-stall toggles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_buffer_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/CMakeLists.txt -->
# Research: sources/storage-engines/rocksdb/java/CMakeLists.txt

Purpose: Defines the CMake-based Java/JNI build for RocksDB. It compiles Java classes, generates JNI headers, builds native `rocksdbjni` libraries, packages platform-specific JARs, generates javadocs/source jars, downloads Java test dependencies, and registers JUnit tests.

Important APIs/types/functions: Key variables include dependency versions, `JNI_NATIVE_SOURCES`, `JAVA_MAIN_CLASSES`, `JAVA_TEST_CLASSES`, `JAVA_TEST_RUNNING_CLASSES`, `JAVA_TESTCLASSPATH`, `JNI_OUTPUT_DIR`, `ROCKSDBJNI_STATIC_LIB`, `ROCKSDBJNI_SHARED_LIB`, `ROCKSDB_JAVADOC_JAR`, `ROCKSDB_SOURCES_JAR`, and `ROCKSDB_JAR`. Important CMake commands are `find_package(JNI)`, `add_jar`, `create_javah`, `add_library`, `target_link_libraries`, `create_javadoc`, `add_custom_target`, and `add_test`.

Control flow: The script validates Java/CMake compatibility, builds the main/test Java jars and native headers, downloads test jars when missing, handles old CMake/JDK header generation separately, builds native JNI shared libraries from the listed C++ sources, derives platform-specific names, packages native library plus `HISTORY-JAVA.md` into the Java jar, then registers each test class with `ctest`.

State and persistence behavior: Outputs are generated under the CMake build tree and `java/include`; test jars are cached under `java/test-libs`. The script mutates build artifacts only, but downloaded jars and generated headers affect subsequent incremental builds.

Dependencies and integration points: Depends on CMake Java support, JNI, RocksDB static/shared libraries, Java 8+, platform naming conventions, JUnit/Hamcrest/Mockito/CGLIB/AssertJ jars, and every Java/JNI file named in the large source lists. It complements the Java Makefile path.

Risks and edge cases: Source lists are manually maintained and can drift from the tree. Old CMake/JDK combinations need `javah`; Java 10+ requires CMake 3.11.4+. Test dependency downloads rely on an S3 mirror or `CUSTOM_DEPS_URL` without checksum checks in this file. Duplicate test class entries can cause redundant work.

Test signals: Successful `rocksdbjava`, `rocksdb_javadocs_jar`, and `rocksdb_sources_jar` targets; platform jar contents containing the correct native library; generated JNI headers; and passing `ctest` `jtest_*` entries with `-Xcheck:jni`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/Makefile -->
# Research: sources/storage-engines/rocksdb/java/Makefile

Purpose: Provides the Make-based Java build, JNI header generation, dependency resolution, samples, tests, benchmarks, and static JNI packaging support for RocksDB's Java API.

Important APIs/types/functions: Major variables include `NATIVE_JAVA_CLASSES`, `NATIVE_JAVA_TEST_CLASSES`, `ROCKSDB_MAJOR/MINOR/PATCH`, `JAVA_TESTS`, source/class output directories, dependency jar paths and SHA256 values, Java command variables, plugin roots, and `ALL_JAVA_TESTS`. Targets include `java-version`, `clean`, `javadocs`, `javalib`, `java`, samples, dependency jar targets, `resolve_test_deps`, `java_test`, `test`, `run_test`, `run_plugin_test`, `db_bench`, and `pmd`.

Control flow: The Makefile discovers Java version/commands, includes plugin `.mk` files, expands core and plugin sources, downloads or copies test dependencies with checksum validation, compiles main classes with `javac -h` to generate JNI headers, compiles tests, runs JUnit via `RocksJunitRunner`, and compiles benchmark classes.

State and persistence behavior: Build products live in `target`, `benchmark/target`, `samples/target`, `include`, and `test-libs`. Dependency downloads are cached and checksum-verified. Sample targets create and remove temporary `/tmp/rocksdbjni` directories.

Dependencies and integration points: Depends on Java 8+, `javac`, `javadoc`, Maven for PMD, curl, SHA256 tool, local Maven repository fallback, plugin-provided Java sources/tests, and top-level RocksDB native build outputs. Version values are parsed from `../include/rocksdb/version.h`.

Risks and edge cases: Manual native class and test lists can lag new Java classes. Dependency downloads use `--insecure`, so checksum validation is essential. Java version parsing depends on `javac -version` token shape. Sample targets remove hard-coded temp paths.

Test signals: `make -C java java`, `java_test`, `test`, `db_bench`, `pmd`, dependency checksum failures, and JUnit output from `RocksJunitRunner` are the main health signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/benchmark/src/main/java/org/rocksdb/benchmark/DbBenchmark.java -->
# Research: sources/storage-engines/rocksdb/java/benchmark/src/main/java/org/rocksdb/benchmark/DbBenchmark.java

Purpose: Implements a standalone Java benchmark driver for RocksDB JNI, modeled after `db_bench` workloads. It opens a configurable DB, runs write/read workloads, and prints throughput/latency summaries.

Important APIs/types/functions: `Stats` records per-task timing, counts, bytes, found keys, and reporting. `DbBenchmark` defines `BenchmarkTask`, `WriteTask`, `WriteSequentialTask`, `WriteRandomTask`, `WriteUniqueRandomTask`, `ReadRandomTask`, `ReadSequentialTask`, `RandomGenerator`, and the large `Flag` enum. Key methods include `prepareOptions`, `prepareReadOptions`, `prepareWriteOptions`, `run`, `open`, `stop`, `generateKeyFromLong`, `main`, and `Flag.parseValue`.

Control flow: `main` seeds defaults from `Flag`, parses `--flag=value` arguments, constructs `DbBenchmark`, and calls `run`. `run` optionally destroys the DB, prepares options, opens RocksDB, loops through requested benchmark names, builds foreground/background `Callable<Stats>` tasks, invokes them through executors, stops background work, and reports aggregate stats. Write tasks generate sequential/random/unique-random keys and optionally batch writes; read tasks use `get` or iterator scans.

State and persistence behavior: The benchmark writes to a RocksDB path from `--db`, using configurable WAL, sync, memtable, cache, compaction, mmap, and env settings. `destroyDb` currently closes the DB but does not delete files, so "fresh" behavior is incomplete. `RandomGenerator` reuses a compressible byte buffer for value generation.

Dependencies and integration points: Depends on RocksDB Java API classes, memtable/table config classes, `RocksMemEnv`, `SizeUnit`, Java reflection for custom comparators, Java executors, and `jdb_bench.sh`. It exercises many JNI option setters and `RocksDB.put/get/write/newIterator`.

Risks and edge cases: `destroyDb` is a TODO and can leave stale data. `getTempDir` uses `File.pathSeparator` when falling back, likely producing a bad path separator for directory construction. Some flags are parsed but not implemented. `WriteOptions` objects are shared across concurrent tasks; correctness depends on native wrapper thread-safety for const use. Batches are manually disposed inside loops.

Test signals: Running `make db_bench` then `java ... DbBenchmark --benchmarks=...` should report ops/sec and MB/s. Useful checks include comparing found counts, ensuring no unknown benchmark names, validating custom comparator construction, and confirming temporary DB cleanup expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/benchmark/src/main/java/org/rocksdb/benchmark/DbBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux-alpine.sh -->
# Research: sources/storage-engines/rocksdb/java/crossbuild/build-linux-alpine.sh

Purpose: Builds portable RocksDB Java artifacts inside an Alpine Linux environment and copies JNI native libraries/JARs to `/rocksdb-build`.

Important APIs/types/functions: The script uses `apk`, repository edits for edge/community, OpenJDK 7 setup, source build of gflags v2.0, `make jclean clean`, `PORTABLE=1 make -j8 rocksdbjavastatic`, and `cp` commands for target artifacts.

Control flow: With `set -e`, it upgrades the Alpine system, installs certificates, build tools, RocksDB compression/dependency packages, Java 7 with certificate symlink repair, removes apk cache, builds gflags from GitHub, enters `/rocksdb`, cleans, builds the static Java artifact, and copies `librocksdbjni-*` plus `rocksdbjni-*`.

State and persistence behavior: Mutates container package state, `/tmp`, `/usr`, `/rocksdb/java/target`, and `/rocksdb-build`. It assumes a disposable build image and removes `/tmp/*` after gflags installation.

Dependencies and integration points: Integrates with cross-build container workflows and Java Makefile/native target `rocksdbjavastatic`. Depends on Alpine package names, OpenJDK 7 path, network access, and `/rocksdb`/`/rocksdb-build` mounts.

Risks and edge cases: Edge repositories and OpenJDK 7 are fragile over time. Building gflags from an old branch can fail if upstream or toolchain assumptions change. `rm -rf /tmp/*` is broad but likely acceptable only inside a dedicated container.

Test signals: Successful artifact copies into `/rocksdb-build`, `make` completion, and loadable `librocksdbjni` on Alpine/musl-compatible targets indicate success.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux-alpine.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux-centos.sh -->
# Research: sources/storage-engines/rocksdb/java/crossbuild/build-linux-centos.sh

Purpose: Builds portable RocksDB Java artifacts on CentOS using old-toolchain compatibility packages and copies outputs to `/rocksdb-build`.

Important APIs/types/functions: Uses `yum`, EPEL, `cmake3` alternatives, `devtoolset-2`, gflags v2.0 source build, `JAVA_HOME=/usr/lib/jvm/java-1.7.0`, `scl enable devtoolset-2`, `make clean-not-downloaded`, and `PORTABLE=1 make -j8 rocksdbjavastatic`.

Control flow: The script removes a fixed `releasever` override, installs dependencies, configures CMake alternatives, enables an older GCC toolchain, downloads/builds gflags, sets Java and library paths, then runs clean/build targets under the software collection and copies native/JAR outputs.

State and persistence behavior: Mutates system package repositories, alternatives, `/usr/local`, current gflags source directory, `/rocksdb/java/target`, and `/rocksdb-build`. It is intended for disposable build images.

Dependencies and integration points: Depends on CentOS yum repositories, `people.centos.org` devtools repo, OpenJDK 7, gflags source archive, and Makefile `rocksdbjavastatic`. It supports legacy Linux binary compatibility for Java artifacts.

Risks and edge cases: The devtools-2 repo and Java 7 are obsolete and likely brittle. `sudo` is required inside the environment. The comment has typos but the operational risk is external repo availability and old compiler/library ABI expectations.

Test signals: Build success under `scl`, artifact copies to `/rocksdb-build`, and later JNI loading/tests on target CentOS-compatible systems.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux-centos.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux.sh -->
# Research: sources/storage-engines/rocksdb/java/crossbuild/build-linux.sh

Purpose: Provides a simple Debian/Ubuntu-style Linux build script for RocksDB Java artifacts and powers down the VM when complete.

Important APIs/types/functions: Uses `apt-get`, installs compiler and compression dependencies, sets `JAVA_HOME` to `java-7-openjdk*`, runs `make jclean clean`, `make -j 4 rocksdbjavastatic`, copies artifacts to `/rocksdb-build`, and calls `sudo shutdown -h now`.

Control flow: Install packages, select Java home, enter `/rocksdb`, clean, build static Java artifacts, copy native libraries/JARs, then halt the machine.

State and persistence behavior: Mutates host package state and build output directories. The final shutdown is a strong side effect indicating this script is designed for ephemeral VM automation rather than interactive use.

Dependencies and integration points: Depends on apt repositories, default JDK/OpenJDK 7 path, Makefile native Java build target, `/rocksdb` source mount, and `/rocksdb-build` artifact mount.

Risks and edge cases: OpenJDK 7 path/package availability is unlikely on modern distributions. The unconditional shutdown is hazardous outside a dedicated build VM. No `set -e` means early failures may not stop later copy/shutdown commands.

Test signals: Presence of copied `librocksdbjni-*` and `rocksdbjni-*` in `/rocksdb-build`, plus VM lifecycle logs showing clean shutdown after a successful build.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/docker-build-linux.sh -->
# Research: sources/storage-engines/rocksdb/java/crossbuild/docker-build-linux.sh

Purpose: Builds RocksDB Java Linux artifacts inside Docker from a mounted host checkout, supporting optional software collection toolchains and copying final files to a mounted target directory.

Important APIs/types/functions: Uses environment variable `J`, `/rocksdb-host`, `/rocksdb-local-build`, `/rocksdb-java-target`, `scl --list`, `devtoolset-8/7/2`, `make clean-not-downloaded`, `PORTABLE=1 J=$J make -j$J rocksdbjavastatic`, and copies `.so`, `.jar`, and `.jar.sha1` files.

Control flow: With `set -e`, it defaults `J=1`, creates a local build directory, copies the host tree into it, chooses the newest supported devtoolset if `scl` is available, otherwise uses the system compiler, runs clean/build, and copies Linux Java artifacts to `/rocksdb-java-target`.

State and persistence behavior: It deletes and recreates `/rocksdb-local-build/*` every run and writes artifacts to `/rocksdb-java-target`. The source mount is read and copied, not built in place, reducing host tree mutation.

Dependencies and integration points: Integrates with Docker cross-build images, RocksDB Makefile, and artifact publishing scripts. Depends on mounted paths, toolchain packages, and the target naming convention `java/target/rocksdbjni-*-linux*.jar`.

Risks and edge cases: Copying the entire checkout can be expensive and may include untracked files from the host. If no recognized devtoolset exists the script exits. Artifact glob mismatches fail under `set -e`, which is good for detecting packaging drift.

Test signals: Successful creation of Linux `.so`, `.jar`, and `.jar.sha1` files in `/rocksdb-java-target`, plus build logs showing selected compiler path and parallelism.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/docker-build-linux.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jdb_bench.sh -->
# Research: sources/storage-engines/rocksdb/java/jdb_bench.sh

Purpose: Launches the Java `DbBenchmark` class with the built RocksDB JNI jar and benchmark classes on the classpath.

Important APIs/types/functions: Determines bitness using `getconf LONG_BIT`, discovers `ROCKS_JAR` with `find target -name rocksdbjni*.jar`, and runs `java -server -d$PLATFORM -XX:NewSize=4m -XX:+AggressiveOpts -Djava.library.path=target -cp ... org.rocksdb.benchmark.DbBenchmark "$@"`.

Control flow: Choose 64-bit or 32-bit mode, locate the jar in `target`, print the bitness, then forward all command-line arguments to `DbBenchmark`.

State and persistence behavior: The script does not persist state directly. The benchmark it launches may create/write a RocksDB database and benchmark output according to its flags.

Dependencies and integration points: Depends on a prior Java/native build that populated `target` and `benchmark/target/classes`, a JVM accepting the supplied flags, and `DbBenchmark.java`.

Risks and edge cases: `-d32/-d64` and `-XX:+AggressiveOpts` are obsolete/unsupported on many modern JVMs. `find` can return multiple jars, yielding an invalid classpath. The shellcheck-disabled `$@` expansion intentionally forwards arguments but may preserve legacy behavior.

Test signals: A successful run prints "Running benchmark" and `DbBenchmark` workload summaries. JVM option errors or class-not-found errors indicate target/JDK drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jdb_bench.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/pom.xml -->
# Research: sources/storage-engines/rocksdb/java/jmh/pom.xml

Purpose: Defines a Maven project that builds an executable JMH benchmark jar for the RocksDB Java API.

Important APIs/types/functions: Project coordinates are `org.rocksdb:rocksdbjni-jmh:1.0-SNAPSHOT`. Properties set Java source/target 17, UTF-8 encoding, JMH 1.22, and shaded jar classifier naming. Dependencies are `org.rocksdb:rocksdbjni:9.0.0`, `jmh-core`, and `jmh-generator-annprocess`. Plugins include `maven-compiler-plugin`, `license-maven-plugin`, and `maven-shade-plugin`.

Control flow: Maven compiles Java 17 benchmark sources with annotation processing, enforces license headers outside `pom.xml`, and shades dependencies into a runnable jar whose manifest main class is `org.openjdk.jmh.Main`. Signature metadata is stripped to avoid invalid signature errors in shaded artifacts.

State and persistence behavior: Build products land in Maven `target`. It does not use the local source tree's freshly built RocksDB JNI unless dependency resolution is overridden; by default it benchmarks RocksDB JNI version 9.0.0 from Maven repositories.

Dependencies and integration points: Integrates with JMH benchmark classes under `java/jmh/src/main/java`, Maven Central/local repository, license header file, and the RocksDB JNI binary dependency.

Risks and edge cases: The pinned RocksDB JNI dependency can lag the checked-out source version. JMH 1.22 is old relative to Java 17. License plugin strictness can fail generated or new files without headers.

Test signals: `mvn package` should produce the shaded benchmark jar; running it should list/execute the JMH benchmark classes. Dependency version mismatch is visible in benchmark logs and classpath resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/ComparatorBenchmarks.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/ComparatorBenchmarks.java

Purpose: Benchmarks RocksDB put performance under native and Java comparator implementations, including direct/non-direct buffer and reused-buffer synchronization modes for Java comparators.

Important APIs/types/functions: JMH annotations `@State`, `@Param`, `@Setup`, `@TearDown`, and `@Benchmark`; RocksDB `Options`, `BuiltinComparator`, `ComparatorOptions`, `AbstractComparator`, `BytewiseComparator`, `ReverseBytewiseComparator`; `Counter` state; and `put`.

Control flow: Trial setup loads RocksDB, creates a temporary DB directory, builds options, parses `comparatorName` to choose native bytewise/reverse comparators or construct Java comparator options, opens the DB, and the benchmark repeatedly puts incrementing key/value pairs. Tear down closes DB/comparator/options and recursively deletes the directory.

State and persistence behavior: Each trial creates a real temporary RocksDB instance and persists benchmark writes until teardown deletes it. `Counter` is benchmark-scoped and atomically generates unique integer suffixes.

Dependencies and integration points: Depends on JMH, RocksDB JNI comparator APIs, `FileUtils.delete`, and `KVUtils.ba`. It exercises JNI callback comparator overhead and buffer reuse modes.

Risks and edge cases: Comparator-name parsing is string-fragment based, so ambiguous substrings could select unintended options. Writes grow the DB for the trial duration and can include compaction effects. Temporary cleanup relies on all native handles closing first.

Test signals: JMH throughput/latency by `comparatorName`, absence of cleanup failures, and successful runs across all Java comparator synchronization modes indicate coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/ComparatorBenchmarks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/GetBenchmarks.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/GetBenchmarks.java

Purpose: Benchmarks several RocksDB Java `get` paths across different column-family counts, key counts, key sizes, and value sizes.

Important APIs/types/functions: Parameters include `columnFamilyTestType`, `keyCount`, `keySize`, and `valueSize`. Important fields include `DBOptions`, `ReadOptions`, `ColumnFamilyHandle[]`, direct `ByteBuffer` key/value buffers, and reusable byte arrays. Benchmarks are `get`, `preallocatedGet`, and `preallocatedByteBufferGet`.

Control flow: Trial setup loads RocksDB, creates requested column families, writes padded key/value pairs into every CF, flushes, then prepares reusable array and direct-buffer inputs. Each benchmark selects a column family, advances an atomic key index, fills the key representation, and calls a different `RocksDB.get` overload.

State and persistence behavior: The temporary DB is populated and flushed to storage for repeatable reads, then deleted during teardown. The mutable key/value arrays and direct buffers are reused across invocations, making buffer position/reset behavior part of benchmark correctness.

Dependencies and integration points: Depends on RocksDB JNI `open`, `put`, `flush`, and get overloads, JMH, `FileUtils`, `KVUtils.ba`, Java NIO direct buffers, and column-family APIs.

Risks and edge cases: `getColumnFamily` reset logic can briefly return index 0 when wrapping multi-CF tests, skewing distribution. `keyArr` and buffers are benchmark-scoped mutable state, so JMH threading configuration matters. The return value of byte-buffer get is not asserted in benchmark mode.

Test signals: JMH results for the three get modes, no `RocksDBException`, correct value-size assertions when enabled, and cleanup without open-handle errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/GetBenchmarks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/MultiGetBenchmarks.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/MultiGetBenchmarks.java

Purpose: Benchmarks Java multi-get APIs using byte-array key lists, explicit column-family handle lists, random column-family handle lists, and direct `ByteBuffer` result buffers.

Important APIs/types/functions: Parameters include `columnFamilyTestType`, `keyCount`, `multiGetSize`, `valueSize`, and `keySize`. Key methods are `setup`, `cleanup`, `next`, `allocateSliceBuffers`, `multiGetList10`, `multiGetListExplicitCF20`, `multiGetListRandomCF30`, `multiGetBB200`, and `main`.

Control flow: Trial setup creates the DB and optional column families, writes padded values for keys, builds repeated/default/random CF-handle lists, and flushes. Per-invocation setup allocates direct buffers and slices. Each benchmark reserves a key range atomically, builds key lists or buffer slices, calls a `multiGet` variant, and validates returned status/value lengths.

State and persistence behavior: The trial DB contains flushed benchmark data until teardown. `keysBuffer`/`valuesBuffer` and slice lists are per-thread state. `keyIndex` advances through key ranges and wraps by multi-get size.

Dependencies and integration points: Depends on RocksDB JNI multi-get APIs, `ByteBufferGetStatus`, JMH, `KVUtils.keys`, `FileUtils.delete`, and column-family handles. It directly tests high-throughput JNI marshalling paths.

Risks and edge cases: When `cfs` is zero, building `randomCFHandles` with `Math.random() * cfs` would always select index 0 only because the loop still runs; with zero optional CFs that is the default handle from the descriptor list, so behavior is not random but valid. The `main` uses parameter names with trailing `=`, which may not match intended JMH API usage. Direct buffer allocation size can be very large.

Test signals: JMH results plus the explicit status/value-size runtime checks in benchmarks. Failures show as `RuntimeException` for wrong status/size or native exceptions for API misuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/MultiGetBenchmarks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/PutBenchmarks.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/PutBenchmarks.java

Purpose: Benchmarks Java put paths for byte arrays and direct `ByteBuffer`s across different column-family counts, key counts, key sizes, and value sizes.

Important APIs/types/functions: Parameters include `columnFamilyTestType`, `keyCount`, `keySize`, `valueSize`, and `bufferListSize`. Key methods are `setup`, `cleanup`, `getColumnFamily`, `borrow`, `repay`, `put`, `putByteArrays`, and `putByteBuffers`; `Counter` produces unique key suffixes.

Control flow: Setup creates a temporary DB with requested column families and preallocates pools of byte-array and direct-buffer key/value storage. Each benchmark borrows buffers, writes `keyN`/`valueN` prefixes into padded storage, calls a RocksDB `put` overload, and returns buffers to the pool.

State and persistence behavior: Benchmark writes persist in the temporary RocksDB directory until teardown. Buffer pools are benchmark-scoped mutable lists guarded by `synchronized`; direct buffers are reused after `clear`/`flip`.

Dependencies and integration points: Depends on RocksDB JNI `put` overloads, `WriteOptions`, JMH state, `FileUtils`, and `KVUtils.ba`. It exercises JNI marshalling and column-family handle paths.

Risks and edge cases: `putByteArrays` and `putByteBuffers` create new `WriteOptions` per operation and never close them, which can distort benchmarks and leak native resources. Borrow sleeps for one second if pools are empty, affecting high-concurrency results. CF wrap logic can return default CF unexpectedly.

Test signals: JMH output by put mode and parameter set, absence of native resource warnings, and cleanup success. Profiling should highlight allocation impact from per-operation `WriteOptions`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/PutBenchmarks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/FileUtils.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/FileUtils.java

Purpose: Provides a small recursive delete utility for JMH benchmarks so temporary RocksDB directories are removed after each trial.

Important APIs/types/functions: `FileUtils.delete(Path)` and private `DeleteDirVisitor` extending `SimpleFileVisitor<Path>` are the core. Visitor methods override `visitFile` and `postVisitDirectory`.

Control flow: `delete` checks whether the path is a directory. Non-directories are deleted with `Files.deleteIfExists`; directories are traversed with `Files.walkFileTree`, deleting files as visited and deleting directories after their children.

State and persistence behavior: This utility destructively removes filesystem paths. Deletion of a directory is not atomic, and partial deletion can occur before an `IOException` is thrown.

Dependencies and integration points: Depends on Java NIO `Files`, `Path`, `SimpleFileVisitor`, and `BasicFileAttributes`. It is used by the JMH benchmark teardown methods.

Risks and edge cases: It follows normal `walkFileTree` behavior and does not include retry logic for open files, permissions, or Windows delayed deletion. If benchmark handles remain open, directory removal can fail.

Test signals: Successful benchmark teardown with no leftover temporary directories. Unit tests could create nested files/directories and verify full deletion plus error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/FileUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/KVUtils.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/KVUtils.java

Purpose: Provides simple key/value helper conversions for JMH benchmarks, including UTF-8 string-to-byte conversion and generated key lists.

Important APIs/types/functions: `ba(String)`, `str(byte[])`, `keys(int from, int to)`, and `keys(List<ByteBuffer> keyBuffers, int from, int to)` are the public helpers.

Control flow: `ba` and `str` convert using UTF-8. The byte-array `keys` method allocates a list and fills it with `keyN` byte arrays. The ByteBuffer overload reuses provided buffers by clearing, writing `keyN`, flipping, and returning a sublist-like newly allocated list of prepared buffers.

State and persistence behavior: No persistent state is owned. The ByteBuffer overload mutates caller-provided buffers, including position/limit, so those buffers are stateful inputs to later RocksDB JNI calls.

Dependencies and integration points: Used by JMH comparator/get/multiget/put benchmarks. Depends on Java `StandardCharsets.UTF_8`, `ByteBuffer`, and collection classes.

Risks and edge cases: Generated keys are not padded here, so callers that stored fixed-width padded keys must ensure lookup keys match. The ByteBuffer helper does not check capacity, so too-small buffers will throw `BufferOverflowException`.

Test signals: Conversion round trips, expected key list contents, and ByteBuffer position/limit after `flip` are useful low-level checks. Benchmark value-size assertions indirectly test key generation consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/KVUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/pmd-rules.xml -->
# Research: sources/storage-engines/rocksdb/java/pmd-rules.xml

Purpose: Defines a custom PMD ruleset for RocksDB Java code, enabling broad PMD categories while carving out exceptions that match the JNI-heavy API style.

Important APIs/types/functions: The ruleset references `category/java/codestyle.xml`, `category/java/errorprone.xml`, `AvoidLiteralsInIfCondition`, `category/java/bestpractices.xml`, and `CloseResource`. It configures excluded rule names, ignored magic numbers/expressions, close-resource types, allowed resource types, and finally behavior.

Control flow: PMD loads the ruleset, applies the referenced categories, removes excluded checks, and uses custom properties for literal and resource-close detection. The Java Makefile target `pmd` invokes Maven PMD/CPD/check phases.

State and persistence behavior: This file does not persist runtime state. It controls static-analysis pass/fail behavior and generated PMD reports.

Dependencies and integration points: Depends on PMD ruleset schema, Maven PMD plugin configuration, and the Java source tree. It is intentionally permissive around native code, naming, short variables, and resource patterns common in JNI wrappers.

Risks and edge cases: Broad exclusions can hide maintainability issues indefinitely. Allowed resource types and close-resource configuration must stay synchronized with RocksDB wrapper ownership conventions. The description contains a typo but does not affect parsing.

Test signals: `make -C java pmd` or Maven PMD checks should parse this ruleset and report only accepted findings. Adding a deliberately unclosed non-allowed resource should still fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/pmd-rules.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/backup_engine_options.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/backup_engine_options.cc

Purpose: Implements JNI bindings for Java `BackupEngineOptions`, exposing construction, getters, setters, and native disposal for C++ `ROCKSDB_NAMESPACE::BackupEngineOptions`.

Important APIs/types/functions: Native methods include `newBackupEngineOptions`, `backupDir`, setters/getters for `backup_env`, `share_table_files`, `info_log`, `sync`, `destroy_old_data`, `backup_log_files`, `backup_rate_limit`, backup/restore `RateLimiter`, `restore_rate_limit`, `share_files_with_checksum`, `max_background_operations`, `callback_trigger_interval_size`, and `disposeInternalJni`.

Control flow: JNI functions reinterpret Java long handles as C++ pointers, copy Java strings where needed, mutate fields on `BackupEngineOptions`, and return primitive values or new Java strings. Construction allocates with `new`; disposal deletes the native object.

State and persistence behavior: Native state lives behind the Java object's long handle. Options influence later backup/restore persistence behavior: directory, file sharing/checksum policy, log backup, sync, rate limits, background work, and old-data destruction. The options object itself is not persisted.

Dependencies and integration points: Depends on generated JNI headers, `rocksdb/utilities/backup_engine.h`, JNI conversion helpers, `portal.h`, `Env`, `RateLimiter`, and logger callback types. It is used by Java `BackupEngineOptions`.

Risks and edge cases: `setInfoLog` appears to reinterpret `jhandle` rather than the logger handle, which is a suspicious ownership/pointer bug. Raw pointer fields such as `backup_env` require Java-side lifetime discipline. String allocation failure returns early as JNI exception state.

Test signals: `BackupEngineOptionsTest` should verify each setter/getter, native disposal, rate limiter/logger behavior, and backup/restore integration. ASAN/JNI checks are useful for handle misuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/backup_engine_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/backupenginejni.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/backupenginejni.cc

Purpose: Implements JNI bindings for Java `BackupEngine`, forwarding Java backup and restore operations to C++ `ROCKSDB_NAMESPACE::BackupEngine`.

Important APIs/types/functions: Native methods include `open`, `createNewBackup`, `createNewBackupWithMetadata`, `getBackupInfo`, `getCorruptedBackups`, `garbageCollect`, `purgeOldBackups`, `deleteBackup`, `restoreDbFromBackup`, `restoreDbFromLatestBackup`, and `disposeInternalJni`.

Control flow: `open` converts env/options handles and calls `BackupEngine::Open`, returning a native pointer or throwing `RocksDBException`. Backup/restore calls reinterpret DB/engine/options handles, convert Java strings to C strings or std::string, invoke C++ methods, release JNI strings, and throw Java exceptions on non-OK `Status`. Info methods convert C++ vectors into Java lists or int arrays.

State and persistence behavior: The native `BackupEngine` handle owns backup engine state until deleted. Operations create backup files, metadata, garbage-collect obsolete data, delete backup ids, and restore DB/WAL directories according to C++ backup engine semantics.

Dependencies and integration points: Depends on generated JNI headers, backup engine utilities, `RocksDBExceptionJni`, `BackupInfoListJni`, Java `DB`, `Env`, `BackupEngineOptions`, and `RestoreOptions` handles.

Risks and edge cases: Backup IDs are converted to `jint`, with a comment acknowledging possible precision loss from wider native ids. JNI string acquisition failures must release already-acquired strings, which restore paths handle. Java-side handle lifetime must ensure DB/options/env remain valid during calls.

Test signals: `BackupEngineTest` should cover open failure propagation, backup creation with/without metadata, corrupted backup list conversion, purge/delete, restore by id/latest, and native handle disposal under `-Xcheck:jni`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/backupenginejni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cache.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/cache.cc

Purpose: Implements JNI accessors for Java `Cache` usage metrics backed by C++ `std::shared_ptr<rocksdb::Cache>`.

Important APIs/types/functions: `Java_org_rocksdb_Cache_getUsage` and `Java_org_rocksdb_Cache_getPinnedUsage` reinterpret the handle as `std::shared_ptr<Cache>*` and call `GetUsage` or `GetPinnedUsage`.

Control flow: Each function performs a pointer cast, dereferences the shared pointer, calls the native cache metric, and returns the value as `jlong`.

State and persistence behavior: The functions only read in-memory cache accounting. They do not mutate cache contents or persistent DB state.

Dependencies and integration points: Depends on generated `org_rocksdb_Cache.h`, `rocksdb/advanced_cache.h`, and Java cache wrapper objects such as LRU/clock cache classes that own shared pointers.

Risks and edge cases: Invalid or disposed handles cause undefined behavior. Metric values are cast to signed Java long; extremely large usage values would need to fit in `jlong`.

Test signals: Cache-related Java tests should allocate cache-backed options, perform reads/writes, compare usage/pinned usage trends, and run under JNI checking to catch disposed-handle calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cassandra_compactionfilterjni.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/cassandra_compactionfilterjni.cc

Purpose: Implements the JNI factory for Java `CassandraCompactionFilter`, creating the C++ Cassandra compaction filter used by RocksDB's Cassandra-format utilities.

Important APIs/types/functions: `Java_org_rocksdb_CassandraCompactionFilter_createNewCassandraCompactionFilter0` allocates `cassandra::CassandraCompactionFilter` with `purge_ttl_on_expiration` and `gc_grace_period_in_seconds`, then returns the native pointer.

Control flow: The factory receives Java boolean/int parameters, constructs the C++ filter with those values, and returns the pointer using `GET_CPLUSPLUS_POINTER`.

State and persistence behavior: The returned compaction filter object is native heap state owned through the Java wrapper. It affects future compaction output by purging/retaining expired Cassandra cells according to TTL and grace-period policy.

Dependencies and integration points: Depends on generated JNI headers, `utilities/cassandra/cassandra_compaction_filter.h`, and JNI pointer conversion helpers. It integrates with Java `CassandraCompactionFilter` and RocksDB compaction configuration.

Risks and edge cases: Ownership and disposal must be handled by the Java base filter wrapper; this file only allocates. Incorrect TTL/grace settings can change persisted data during compaction.

Test signals: Java compaction-filter tests should verify native handle creation, disposal, and compaction behavior for expired/non-expired Cassandra values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cassandra_compactionfilterjni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cassandra_value_operator.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/cassandra_value_operator.cc

Purpose: Implements JNI bindings for Java `CassandraValueMergeOperator`, creating and disposing a shared C++ Cassandra merge operator.

Important APIs/types/functions: `Java_org_rocksdb_CassandraValueMergeOperator_newSharedCassandraValueMergeOperator` allocates a `std::shared_ptr<MergeOperator>` wrapping `cassandra::CassandraValueMergeOperator`; `disposeInternalJni` deletes the shared pointer wrapper.

Control flow: The factory converts Java `gcGracePeriodInSeconds` and `operands_limit` to the C++ constructor, returns the heap-allocated shared-pointer handle, and disposal reinterprets/deletes that handle.

State and persistence behavior: The merge operator is native process state referenced by DB options. It affects persisted values when merge operands are resolved or compacted under Cassandra value semantics, including garbage-collection grace and operand limits.

Dependencies and integration points: Depends on generated JNI headers, RocksDB DB/options/merge operator headers, Cassandra merge utilities, and Java merge-operator wrapper ownership.

Risks and edge cases: The Java options object must keep the shared operator alive for as long as the DB uses it. Misconfigured operand limits or grace periods can affect merge correctness and compaction output. Disposed handles must not be reused.

Test signals: Java merge-operator tests should exercise construction, DB option installation, merge/read/compaction outcomes, operand-limit behavior, and native disposal under JNI checking.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cassandra_value_operator.cc -->
