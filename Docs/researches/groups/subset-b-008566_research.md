# subset-b-008566 research

Grouped research report for the requested RocksDB cache, CMake/build, iterator, coverage, crash-test, and blob-file files. Each section is wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/tiered_secondary_cache.h -->
# sources/storage-engines/rocksdb/cache/tiered_secondary_cache.h

## Purpose
Defines `TieredSecondaryCache`, a `SecondaryCacheWrapper` that stacks a compressed secondary cache above an NVM/local-flash secondary cache. Its policy is asymmetric: blocks read directly from SSTs can warm the NVM tier through `InsertSaved`, and hits in NVM can be promoted toward compressed secondary and primary block caches, but evictions from upper tiers are not demoted.

## Important APIs and Types
The constructor accepts compressed and NVM `SecondaryCache` instances plus a `TieredAdmissionPolicy`; debug builds assert the three-queue admission policy. `Insert` is intentionally a no-op returning OK, while `InsertSaved` forwards saved compressed bytes to `nvm_sec_cache_`. `Lookup` and `WaitAll` are declared here and coordinate the multi-tier read path. Private `CreateContext` carries key, erase advice, helper, inner create context/handle, compressed-cache pointer, and statistics. `ResultHandle` wraps an inner async handle and exposes `IsReady`, `Wait`, `Size`, and `Value`.

## Control Flow and State
`ResultHandle::IsReady` completes when the inner handle becomes ready, transferring size/value and dropping the inner handle. The helper returned by `GetHelper()` installs `MaybeInsertAndCreate` as a create callback while other callbacks assert, because this helper should only bridge creation/promotion behavior. Persistent state is not owned here; the durable-like state lives in the underlying NVM cache. Risks include relying on callback assertions to catch invalid helper use, debug-only policy enforcement, and careful lifetime management of the nested result handle. Test coverage is in `tiered_secondary_cache_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/tiered_secondary_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/tiered_secondary_cache_test.cc -->
# sources/storage-engines/rocksdb/cache/tiered_secondary_cache_test.cc

## Purpose
Exercises tiered cache behavior through DB-level reads, MultiGet, iteration, admission policies, and filesystem buffer ownership. It uses a fake NVM `SecondaryCache` to count inserts, hits, and misses while validating interactions between primary cache, compressed secondary cache, and an NVM secondary tier.

## Important APIs and Test Fixtures
`TestSecondaryCache` stores serialized saved blocks in an LRU cache using `BasicTypedSharedCacheInterface<char[]>`; saved entries include payload size, compression type, cache tier, and bytes. Its `Lookup` decodes the saved record and invokes the caller's `create_cb`, returning a `TestSecondaryCacheResultHandle` that can be ready immediately or after `WaitAll`. `DBTieredSecondaryCacheTest::NewCache` builds a tiered cache with primary/compressed/NVM capacities and exposes helper accessors for NVM counters and compressed secondary usage.

## Control Flow and State
`BasicTest` validates warming NVM on SST misses, NVM hits, placeholder promotion, primary hits, and later compressed-secondary hits. `BasicMultiGetTest`, `WaitAllTest`, and `ReadyBeforeWaitAllTest` cover async lookup, wait aggregation, readiness before wait, and block-cache miss tickers. `IterateTest` validates readahead iteration warms and reuses NVM blocks. `VolatileTierTest` verifies `lowest_used_cache_tier == kVolatileTier` bypasses secondary cache. Parameterized tests compare admission policies for compressed-only cache. `FSBufferTest` wraps `MultiRead` to exercise `FSAllocationPtr` scratch ownership. Risks are timing-sensitive async assumptions and small cache-capacity math; tests skip when LZ4 is unavailable.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/tiered_secondary_cache_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/typed_cache.h -->
# sources/storage-engines/rocksdb/cache/typed_cache.h

## Purpose
Provides type-safe C++ wrappers around RocksDB's low-level `Cache` API. The wrappers centralize typed handles, value deletion, secondary-cache serialization callbacks, guard construction, placeholder entries, and shared-cache ownership variants.

## Important APIs and Types
`BaseCacheInterface` stores either a raw or shared cache pointer and exposes release/cleanup helpers. `PlaceholderCacheInterface` reserves cache charge with null values and a role-only helper. `BasicTypedCacheHelperFns` upcasts/downcasts object pointers and deletes typed values, including array types. `BasicTypedCacheInterface<TValue>` implements typed `Insert`, `Lookup`, async lookup, `Guard`, `SharedGuard`, and `Value`. `FullTypedCacheHelperFns` adds `Size`, `SaveTo`, and `Create` callbacks for secondary-cache-compatible values. `FullTypedCacheInterface` adds `InsertFull`, `InsertSaved`, `LookupFull`, and `StartAsyncLookupFull`.

## Control Flow and State
The wrapper chooses basic versus full helpers based on `lowest_used_cache_tier`; volatile-only lookups avoid secondary-cache helper overhead. `InsertSaved` materializes a value through the full helper create callback before inserting it. The create path rejects non-volatile source tiers. State remains in the underlying `Cache`; this header contributes static `CacheItemHelper` singletons and typed ownership rules. Risks include reinterpret-casting typed handles, helper callbacks assuming `TValue::ContentSlice()`, and disabled custom-allocator object deletion. Integration points include blob value cache, secondary cache adapters, block cache users, and tests that use typed cache for in-memory fake caches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/typed_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/RocksDBConfig.cmake.in -->
# sources/storage-engines/rocksdb/cmake/RocksDBConfig.cmake.in

## Purpose
Template for the installed CMake package configuration consumed by downstream `find_package(RocksDB)`. It reconstructs RocksDB's optional dependency graph based on configured build options and imports `RocksDBTargets.cmake`.

## Important APIs and Control Flow
The file starts with `@PACKAGE_INIT@`, extends `CMAKE_MODULE_PATH` with installed custom modules, and includes `CMakeFindDependencyMacro`. It sets `GFLAGS_USE_TARGET_NAMESPACE`, then conditionally calls `find_dependency` for JeMalloc, gflags, Snappy, ZLIB, BZip2, lz4, zstd, NUMA, and TBB according to `@WITH_*@` substitutions. gflags and Snappy prefer CONFIG packages and fall back to module mode. Threads is always required. Finally it includes exported targets and calls `check_required_components(RocksDB)`.

## Dependencies, Risks, and Test Signals
This file depends on the custom `cmake/modules/Find*.cmake` files being installed beside the package config. It persists no runtime state, but it encodes build-time feature state into the installed package contract. Risks include mismatches between exported target link interfaces and the conditional dependencies, and casing differences such as `lz4`/`zstd` target names. Validation usually comes from downstream CMake package tests or install/package CI.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/RocksDBConfig.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/CxxFlags.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/CxxFlags.cmake

## Purpose
Defines one macro, `get_cxx_std_flags`, to recover the compiler flag associated with the current `CMAKE_CXX_STANDARD` and whether strict standard mode is required.

## Important APIs and Control Flow
`get_cxx_std_flags(FLAGS_VARIABLE)` sets the caller-provided variable to either `CMAKE_CXX${CMAKE_CXX_STANDARD}_STANDARD_COMPILE_OPTION` when `CMAKE_CXX_STANDARD_REQUIRED` is true, or to `CMAKE_CXX${CMAKE_CXX_STANDARD}_EXTENSION_COMPILE_OPTION` otherwise. This mirrors CMake's internal standard flag selection but exposes the selected flag for RocksDB build logic.

## Dependencies, Risks, and Test Signals
It relies on CMake-populated standard option variables and caller configuration of `CMAKE_CXX_STANDARD`. There is no persistence. The main risk is empty output if CMake does not define the chosen standard option for the active compiler/generator, or if `CMAKE_CXX_STANDARD` is unset. Test signal is build-system configuration coverage across compilers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/CxxFlags.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/FindJeMalloc.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/FindJeMalloc.cmake

## Purpose
Finds jemalloc headers and library for RocksDB builds and exports an imported target for link consumers.

## Important APIs and Control Flow
`find_path(JeMalloc_INCLUDE_DIRS NAMES jemalloc/jemalloc.h HINTS ${JEMALLOC_ROOT_DIR}/include)` locates headers, and `find_library(JeMalloc_LIBRARIES NAMES jemalloc HINTS ${JEMALLOC_ROOT_DIR}/lib)` locates the library. `find_package_handle_standard_args(JeMalloc ...)` defines `JeMalloc_FOUND`. On success, the module creates `JeMalloc::JeMalloc` as an UNKNOWN IMPORTED target with `IMPORTED_LOCATION` and `INTERFACE_INCLUDE_DIRECTORIES`.

## Dependencies, Risks, and Test Signals
Depends on CMake's `FindPackageHandleStandardArgs` and optional `JEMALLOC_ROOT_DIR`. It persists no state beyond CMake cache variables marked advanced. Risks are static/shared selection being delegated to `find_library`, no version checking, and imported target creation only if another target with the same name does not exist. Build CI with `WITH_JEMALLOC` provides coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/FindJeMalloc.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/FindNUMA.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/FindNUMA.cmake

## Purpose
Finds Linux NUMA support headers and library and exposes a CMake imported target for RocksDB's optional NUMA-aware features.

## Important APIs and Control Flow
`find_path(NUMA_INCLUDE_DIRS NAMES numa.h numaif.h HINTS ${NUMA_ROOT_DIR}/include)` and `find_library(NUMA_LIBRARIES NAMES numa HINTS ${NUMA_ROOT_DIR}/lib)` locate the dependency. `find_package_handle_standard_args` sets `NUMA_FOUND`. When found, `NUMA::NUMA` is created as an UNKNOWN IMPORTED target with include directories and library path.

## Dependencies, Risks, and Test Signals
The module uses optional `NUMA_ROOT_DIR` and CMake cache variables. It does not validate ABI or platform semantics. Risk is false positives on systems with partial NUMA headers/libraries or nonstandard library names. Coverage comes from CMake builds with `WITH_NUMA` enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/FindNUMA.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/FindSnappy.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/FindSnappy.cmake

## Purpose
Finds the Snappy compression library when package-config mode is unavailable or not selected.

## Important APIs and Control Flow
The module searches for `snappy.h` under `${snappy_ROOT_DIR}/include` and the `snappy` library under `${snappy_ROOT_DIR}/lib`. `find_package_handle_standard_args(Snappy ...)` sets `Snappy_FOUND`. On success it creates `Snappy::snappy` as an UNKNOWN IMPORTED target with include directories and imported location.

## Dependencies, Risks, and Test Signals
This file integrates with `RocksDBConfig.cmake.in`, which first tries `find_dependency(Snappy CONFIG)` and then this module. It has no runtime persistence. Risks include no version/feature checks and target-name casing compatibility. Test signals include compression-enabled CMake builds and install-consumer package tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/FindSnappy.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/FindTBB.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/FindTBB.cmake

## Purpose
Finds Intel/oneAPI Threading Building Blocks for optional RocksDB parallelism support.

## Important APIs and Control Flow
If `TBB_ROOT_DIR` is unset, it is initialized from `$ENV{TBBROOT}`. The module searches for `tbb/tbb.h` and library `tbb`, with library hints including `${TBB_ROOT_DIR}/lib` and `ENV LIBRARY_PATH`. `find_package_handle_standard_args(TBB ...)` defines `TBB_FOUND`. On success, it creates imported target `TBB::TBB`.

## Dependencies, Risks, and Test Signals
State is confined to CMake variables and cache entries. Risks include modern TBB package layouts that prefer CONFIG packages, platform-specific library suffixes, and lack of version checks. Build coverage comes from `WITH_TBB` CMake configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/FindTBB.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/Findgflags.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/Findgflags.cmake

## Purpose
Finds gflags headers and library for RocksDB tools/tests when a gflags CONFIG package is unavailable.

## Important APIs and Control Flow
`find_path(GFLAGS_INCLUDE_DIR NAMES gflags/gflags.h)` and `find_library(GFLAGS_LIBRARIES NAMES gflags)` locate dependency files. `find_package_handle_standard_args(gflags ...)` sets `gflags_FOUND`. If successful, it creates `gflags::gflags` as an UNKNOWN IMPORTED target with include directories, imported location, and `IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"`.

## Dependencies, Risks, and Test Signals
The installed RocksDB config tries config mode before falling back to this module. No runtime state exists. Risks include namespace selection mismatches with `GFLAGS_USE_TARGET_NAMESPACE`, missing multithreaded/static library variants, and no version validation. CI with gflags-enabled tools is the main test signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/Findgflags.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/Findlz4.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/Findlz4.cmake

## Purpose
Finds the LZ4 compression dependency and provides a target named `lz4::lz4`.

## Important APIs and Control Flow
The module locates `lz4.h` using `${lz4_ROOT_DIR}/include`, locates library `lz4` using `${lz4_ROOT_DIR}/lib`, and calls `find_package_handle_standard_args(lz4 ...)`. When `lz4_FOUND` is true and the target is absent, it creates an UNKNOWN IMPORTED target with `IMPORTED_LOCATION` and `INTERFACE_INCLUDE_DIRECTORIES`.

## Dependencies, Risks, and Test Signals
It participates in `WITH_LZ4` CMake builds and installed package dependency discovery. Risks include no version checking and lowercase package variable/target naming that must match the rest of the build. Functional test signal comes from LZ4-dependent tests such as tiered secondary cache tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/Findlz4.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/Finduring.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/Finduring.cmake

## Purpose
Finds liburing for optional io_uring support and exports an imported target.

## Important APIs and Control Flow
The module searches for `liburing.h` and library names `liburing.a` or `liburing`. `find_package_handle_standard_args(uring ...)` sets `uring_FOUND`. On success, it creates `uring::uring` as an UNKNOWN IMPORTED target with include directories, C link-interface language, and imported location.

## Dependencies, Risks, and Test Signals
No runtime state is persisted; only CMake variables and target definitions are produced. Risks include preferring a static archive when both static and shared libraries exist, no version checks for io_uring feature availability, and Linux-specific assumptions. Build/test coverage comes from io_uring-enabled RocksDB configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/Finduring.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/Findzstd.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/Findzstd.cmake

## Purpose
Finds the Zstandard compression library for RocksDB's optional zstd support.

## Important APIs and Control Flow
The module searches for `zstd.h` under `${zstd_ROOT_DIR}/include` and library `zstd` under `${zstd_ROOT_DIR}/lib`. `find_package_handle_standard_args(zstd ...)` sets `zstd_FOUND`. On success, it creates imported target `zstd::zstd` with location and include directory properties.

## Dependencies, Risks, and Test Signals
It integrates with `RocksDBConfig.cmake.in` through `find_dependency(zstd)`. Risks include no version validation and target naming compatibility with other zstd CMake packages. Compression-enabled build CI and downstream package discovery are the relevant tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/Findzstd.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/ReadVersion.cmake -->
# sources/storage-engines/rocksdb/cmake/modules/ReadVersion.cmake

## Purpose
Extracts RocksDB's semantic version from the public `include/rocksdb/version.h` header during CMake configuration.

## Important APIs and Control Flow
`get_rocksdb_version(version_var)` reads the version header from `CMAKE_CURRENT_SOURCE_DIR`, loops over `MAJOR`, `MINOR`, and `PATCH`, matches `#define ROCKSDB_<component> ([0-9]+)`, and builds `<major>.<minor>.<patch>` into the caller's variable with `PARENT_SCOPE`.

## Dependencies, Risks, and Test Signals
It depends on the exact macro spelling in `version.h` and a source-root-relative configure context. It persists only a CMake variable. Risks include silently using empty `CMAKE_MATCH_1` if a regex does not match and source layout assumptions in embedded builds. Package-version generation and CMake configure tests are the validation points.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cmake/modules/ReadVersion.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/common.mk -->
# sources/storage-engines/rocksdb/common.mk

## Purpose
Shared Makefile fragment for Python selection and test temporary-directory setup across RocksDB make targets.

## Important APIs and Control Flow
If `PYTHON` is undefined, it chooses `python3`, then `python`, then literal `python3`, and exports the result. For temporary directories, `TEST_TMPDIR` falls back from `TMPD`, then `BASE_TMPDIR`, then `TMPDIR`, then `/tmp`. If no explicit test tmp dir exists, it prefers `/dev/shm` only when it has the sticky bit, then creates a random `rocksdb.XXXX` directory with Perl `File::Temp` and `CLEANUP => 0`.

## State, Dependencies, and Risks
This fragment persists environment variables for child make commands and creates a real filesystem directory used by tests/tools. Risks include dependency on Perl, unremoved temp directories because cleanup is disabled, and `/dev/shm` capacity/permission surprises. It integrates with `crash_test.mk` and other make targets that use `TEST_TMPDIR`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/common.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/coverage/coverage_test.sh -->
# sources/storage-engines/rocksdb/coverage/coverage_test.sh

## Purpose
Shell driver for generating textual and optional HTML code coverage reports from GCC/gcov output.

## Important APIs and Control Flow
The script exits on error and rejects `USE_CLANG`, because it supports GCC coverage only. It selects `gcov` from Meta-internal GCC when present or from `PATH`. It creates `COVERAGE_REPORT`, finds all `*.gcno` files under `..`, runs gcov with `--preserve-paths --relative-only --no-output`, pipes output through `parse_gcov_output.py`, and writes `coverage_report_all.txt`. It also derives files from `git show --name-only HEAD`, filters the parsed report with `-interested-files`, and writes `coverage_report_recent.txt`. If `HTML` is set and a supported `lcov` exists, it captures `coverage.info` and runs `genhtml`.

## State, Dependencies, and Risks
Persistent outputs are report files under `COVERAGE_REPORT`. Dependencies include gcov, Python, git, optionally lcov/genhtml. Risks include unquoted variables, legacy lcov version check expectations, and recent-file filtering based only on HEAD. Coverage validation is the script's own report generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/coverage/coverage_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/coverage/parse_gcov_output.py -->
# sources/storage-engines/rocksdb/coverage/parse_gcov_output.py

## Purpose
Parses raw gcov text into a compact, human-readable table, optionally restricted to a comma-separated set of interested files.

## Important APIs and Control Flow
`parse_gcov_report` scans stdin for `File '...'` lines followed by `Lines executed:<pct>% of <lines>` lines, building `per_file_coverage` and a final `total_coverage` when no current file is active. `get_option_parser` defines `--interested-files/-i`. `display_file_coverage` computes max filename width, prints header/separator/body, and optionally prints total. `report_coverage` parses args, filters requested files, suppresses totals for filtered reports, and prints a stderr message when no matching coverage exists.

## State, Dependencies, and Risks
The script holds coverage in memory only and writes to stdout/stderr. It depends on gcov output formatting and Python's deprecated `optparse`. Risks include `current_file` not being initialized before unusual input, `max()` failing on empty coverage if not guarded, unordered dictionary output in older Python expectations, and exact regex sensitivity. It is invoked by `coverage_test.sh`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/coverage/parse_gcov_output.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/crash_test.mk -->
# sources/storage-engines/rocksdb/crash_test.mk

## Purpose
Makefile for RocksDB crash-test orchestration. It supports direct `make -f crash_test.mk` use and inclusion from the main Makefile.

## Important APIs and Control Flow
`DB_STRESS_CMD` defaults to `./db_stress`, and `common.mk` supplies `PYTHON` and `TEST_TMPDIR`. TSAN runs export suppressions. `CRASHTEST_PY` invokes `tools/db_crashtest.py` with stress command, cleanup command, and `--destroy_db_initially=1`. Phony aggregate targets run whitebox and blackbox variants for atomic flush, transaction write policies, timestamp support, optimistic transactions, tiered storage, multi-ops transactions, and best-efforts recovery. Whitebox tests add `--random_kill_odd`, defaulting to `888887`. `crash_test_db_cleanup` delegates deletion to `db_stress`.

## State, Dependencies, and Risks
The file creates and destroys DB state under `TEST_TMPDIR`, relies on a built `db_stress`, and forwards `CRASH_TEST_EXT_ARGS`. Risks include accidental parallelization of sequences marked "Do not parallelize", old deprecated target aliases, shell quoting of cleanup command, and feature coverage depending on `db_stress` options staying compatible. Test signal is successful blackbox/whitebox crash-test execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/crash_test.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/arena_wrapped_db_iter.cc -->
# sources/storage-engines/rocksdb/db/arena_wrapped_db_iter.cc

## Purpose
Implements `ArenaWrappedDBIter`, the public iterator wrapper that owns an arena and lazily installs the internal iterator tree beneath `DBIter`. It also implements explicit refresh and auto-refresh when superversions change.

## Important APIs and Control Flow
`EnsureInternalIteratorInitialized` builds the internal iterator through `DBImpl::NewInternalIterator`, optionally with bounded MultiScan pruning, clears deferred state, and attaches it to `DBIter`. `Init` normalizes read options, disables async I/O if unsupported, accounts for prefix seek settings, and creates the `DBIter` in the arena. `DoRefresh` destroys the old DBIter/arena, obtains a referenced superversion, refreshes read callbacks, reinitializes DBIter, and installs a new internal iterator. `Refresh` handles same-superversion snapshot sequence changes and mutable-memtable range tombstone refresh; if the superversion changes mid-refresh, it retries with full reinit. `MaybeAutoRefresh` detects relaxed superversion-number changes after seeks or movement and reconciles non-seek cursor position.

## State, Dependencies, and Risks
State includes deferred `SuperVersion`, referenced `ColumnFamilyData`, read options, sequence number, refresh flags, and optional memtable range-tombstone iterator pointer. It depends on DBImpl, ColumnFamilyData locking, DBIter, arenas, snapshots, range tombstones, and filesystem async feature checks. Risks are lifetime-sensitive destructor/manual arena destruction, refresh not preserving `Prepare` scan options, relaxed superversion detection, and consistency subtleties with WritePrepared snapshots. Test signals are iterator refresh, MultiScan, range deletion, and snapshot tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/arena_wrapped_db_iter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/arena_wrapped_db_iter.h -->
# sources/storage-engines/rocksdb/db/arena_wrapped_db_iter.h

## Purpose
Declares `ArenaWrappedDBIter`, an `Iterator` implementation that wraps `DBIter` plus an arena so the iterator hierarchy can be allocated compactly and lazily.

## Important APIs and Types
The class forwards the public iterator API (`Seek`, `Next`, `Prev`, `key`, `value`, `columns`, `status`, `timestamp`, `PrepareValue`) to the inner `DBIter` after ensuring the internal iterator exists. `Init` constructs DBIter from immutable/mutable CF options, version, sequence, callback, CF handle, blob-index exposure, refresh allowance, and active memtable. `StoreDeferredInitInfo` references the column family, remembers `SuperVersion`, sequence, and flush-mark permission for lazy internal iterator creation. `Refresh`, `Refresh(snapshot)`, `Prepare`, `SetIterUnderDBIter`, and property access provide advanced behavior.

## State, Dependencies, and Risks
The header owns an `Arena`, raw `DBIter*`, refresh metadata, deferred DB state, read options, and range-tombstone iterator pointer. `ColumnFamilyDataUnrefDeleter` unrefs under DB mutex. Risks include requiring `DestroyDBIter` in the destructor, invalid state when deferred DB state is missing, and users calling methods after failed initialization. Integration points are DB iterator creation, SstFileReader, MultiScan, snapshots, blob-index exposure, and auto-refresh iterator support.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/arena_wrapped_db_iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/attribute_group_iterator_impl.cc -->
# sources/storage-engines/rocksdb/db/attribute_group_iterator_impl.cc

## Purpose
Implements minimal storage population for attribute-group iteration across multiple column families.

## Important APIs and Control Flow
Defines empty constants `kNoAttributeGroups` and `kNoIteratorAttributeGroups`. `AttributeGroupIteratorImpl::AddToAttributeGroups` iterates over `autovector<MultiCfIteratorInfo>` items and appends `(ColumnFamilyHandle*, WideColumns*)` pairs to `attribute_groups_`, referencing each child iterator's `columns()`.

## State, Dependencies, and Risks
The method stores pointers into child iterator column data, so validity is tied to the current iterator position and the wrapped `MultiCfIteratorImpl` lifecycle. It depends on `MultiCfIteratorInfo`, `Iterator::columns()`, and `rocksdb/attribute_groups.h` types. Risks include stale references if callers retain `attribute_groups()` after movement/reset, although the wrapper clears and repopulates on position changes. Tests are likely in multi-CF/attribute-group iterator suites.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/attribute_group_iterator_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/attribute_group_iterator_impl.h -->
# sources/storage-engines/rocksdb/db/attribute_group_iterator_impl.h

## Purpose
Declares the concrete `AttributeGroupIterator` implementation built on top of `MultiCfIteratorImpl`, plus an error/empty iterator implementation.

## Important APIs and Types
`AttributeGroupIteratorImpl` constructs `impl_` with reset and populate functors bound to `this`. It forwards validity, seeking, movement, key, status, and `PrepareValue` to `MultiCfIteratorImpl`. `attribute_groups()` asserts validity and returns the populated groups. `ResetFunc` clears `attribute_groups_`; `PopulateFunc` delegates to `AddToAttributeGroups`. `EmptyAttributeGroupIterator` always invalidly reports a fixed status, no-ops seeks, asserts on movement/key access, and returns `kNoIteratorAttributeGroups`. `NewAttributeGroupErrorIterator` creates the empty error iterator.

## State, Dependencies, and Risks
State is a `MultiCfIteratorImpl` plus current `IteratorAttributeGroups`. The main risk is reference lifetime for wide-column pointers and assertion-only protection on invalid access. Integration points include multi-CF iteration, wide-column/attribute-group APIs, and callers needing a status-carrying iterator when construction fails.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/attribute_group_iterator_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_constants.h -->
# sources/storage-engines/rocksdb/db/blob/blob_constants.h

## Purpose
Defines blob subsystem constants shared by metadata and manifest record classes.

## Important APIs and State
The file declares `constexpr uint64_t kInvalidBlobFileNumber = 0` inside the RocksDB namespace. It is used as the default sentinel for classes such as `BlobFileAddition` and `BlobFileGarbage`.

## Dependencies, Risks, and Test Signals
There is no control flow or persistence. The dependency surface is intentionally tiny: `<cstdint>` and namespace declaration. The key invariant is that valid blob file numbers must not be zero. Tests in metadata/addition/garbage files assert default objects use this sentinel.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_contents.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_contents.cc

## Purpose
Implements memory accounting for cached uncompressed blob values.

## Important APIs and Control Flow
`BlobContents::ApproximateMemoryUsage` adds allocation memory if `allocation_` exists. If a custom `MemoryAllocator` is attached to the deleter, it asks `allocator->UsableSize`; otherwise it uses `malloc_usable_size` when available or `data_.size()` as a fallback. It also accounts for the `BlobContents` object itself using `malloc_usable_size(this)` when available or `sizeof(*this)`.

## State, Dependencies, and Risks
The method depends on `CacheAllocationPtr`, allocator deleter state, and `ROCKSDB_MALLOC_USABLE_SIZE`. It persists no data, but it determines cache charge estimates for blob values. Risks are platform-dependent allocator reporting, `const_cast` use for `malloc_usable_size`, and fallback undercounting/overcounting. It integrates with typed cache insertion through `BlobContentsCreator`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_contents.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_contents.h -->
# sources/storage-engines/rocksdb/db/blob/blob_contents.h

## Purpose
Declares `BlobContents`, the in-memory representation of a single uncompressed value read from a blob file, and its cache creation context.

## Important APIs and Types
`BlobContents` owns a `CacheAllocationPtr` and exposes a `Slice` over the allocated bytes. It is moveable but not copyable, provides `data()`, `size()`, `ApproximateMemoryUsage()`, and `ContentSlice()` for `FullTypedCacheInterface`. Its cache role is `CacheEntryRole::kBlobValue`. `BlobContentsCreator::Create` copies a saved slice into cache allocation, constructs `BlobContents`, and returns the approximate memory charge.

## State, Dependencies, and Risks
The persisted value for cache serialization is the content slice; object lifetime is tied to allocation ownership. Dependencies include memory allocator helpers, advanced cache interfaces, slices, and compression type signatures. Risks include cache charge accuracy and assuming the input slice already represents uncompressed blob contents. Integration points are blob cache reads and typed secondary-cache-compatible cache insertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_contents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_counting_iterator.h -->
# sources/storage-engines/rocksdb/db/blob/blob_counting_iterator.h

## Purpose
Wraps an `InternalIterator` to measure blob inflow during compaction by passing each visited key/value to `BlobGarbageMeter`.

## Important APIs and Control Flow
The constructor stores the child iterator and meter, then immediately calls `UpdateAndCountBlobIfNeeded`. All positioning and movement methods delegate to the child and then call the update method. `Valid()` requires both child validity and local `status_.ok()`. Data accessors forward to the child under `Valid()` assertions. `NextAndGetResult`, bounds checks, pinning methods, properties, and delete-range sentinel checks mostly pass through.

## State, Dependencies, and Risks
State is a non-owning child iterator pointer, a non-owning `BlobGarbageMeter*`, and a local status. `UpdateAndCountBlobIfNeeded` copies child status when invalid and otherwise calls `ProcessInFlow(key(), value())`, which can turn the wrapper invalid on corrupt blob indexes. Risks include double-counting if the same entry is revisited by seeks, which is intended for measurement semantics in tests, and relying on child status being OK while valid. `blob_counting_iterator_test.cc` directly covers forward/backward/seek and corruption behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_counting_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_counting_iterator_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_counting_iterator_test.cc

## Purpose
Unit tests for `BlobCountingIterator` and its integration with `BlobGarbageMeter`.

## Important Test Flow
`CountBlobs` builds a `VectorIterator` over two blob-index values and one plain value. It encodes blob references with different file numbers and sizes, computes expected bytes including blob log record header adjustment, and verifies inflow counts/bytes after `SeekToFirst`, `Next`, `NextAndGetResult`, `SeekToLast`, `Prev`, `Seek`, and `SeekForPrev`. `CheckInFlow` inspects `blob_garbage_meter.flows()` and handles absent entries as zero. `CorruptBlobIndex` uses an invalid blob-index payload and verifies the wrapper becomes invalid with non-OK status.

## Dependencies, Risks, and Test Signals
The tests depend on `BlobIndex`, `BlobLogRecord`, internal key encoding, and `VectorIterator`. They intentionally demonstrate that revisiting entries increments inflow again. The main risk under test is corruption propagation from `ProcessInFlow`. The file is itself the direct signal that counting behavior matches compaction accounting expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_counting_iterator_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_fetcher.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_fetcher.cc

## Purpose
Implements blob retrieval routing for decoded and encoded blob indexes.

## Important APIs and Control Flow
`FetchBlob(user_key, blob_index_slice, ...)` decodes a `BlobIndex` from the provided slice, then delegates to the overload taking `const BlobIndex&`. The second overload either calls `version_->GetBlob` when write-path fallback is disabled, or calls `BlobFilePartitionManager::ResolveBlobDirectWriteIndex` when fallback is allowed. The fallback path can resolve direct-write blob files not yet visible in the manifest using the optional `BlobFileCache`.

## State, Dependencies, and Risks
The class stores `Version*`, copied `ReadOptions`, optional `BlobFileCache*`, and a fallback flag. Dependencies include `BlobIndex`, `Version`, `BlobFilePartitionManager`, `FilePrefetchBuffer`, and `PinnableSlice`. Risks include requiring non-null `version_` in normal path, handling decode corruption, and ensuring fallback does not bypass visibility/consistency constraints. Test coverage is likely through blob read and write-path direct-write tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_fetcher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_fetcher.h -->
# sources/storage-engines/rocksdb/db/blob/blob_fetcher.h

## Purpose
Declares `BlobFetcher`, a thin read helper that abstracts whether a blob value should be read through a manifest-visible `Version` or through a direct-write fallback path.

## Important APIs and State
The constructor stores a `const Version*`, `ReadOptions`, optional `BlobFileCache*`, and `allow_write_path_fallback_`. Two `FetchBlob` overloads accept either a serialized blob-index slice or a decoded `BlobIndex`, plus prefetch buffer, output `PinnableSlice`, and optional bytes-read counter.

## Dependencies, Risks, and Integration
The header forward-declares blob/read support types and includes options/status. It persists no data itself but participates in read-path state resolution. Risks include caller-supplied pointer lifetime for `Version` and `BlobFileCache`, and ambiguity if fallback is enabled without the necessary cache. Integration points are DB read paths that encounter blob indexes and need to materialize values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_fetcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_addition.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_addition.cc

## Purpose
Implements manifest-log encoding, decoding, equality, and debug rendering for blob-file addition records.

## Important APIs and Control Flow
`EncodeTo` writes blob file number, total blob count, total blob bytes, checksum method, checksum value, optional custom fields via sync point, and an end marker. `DecodeFrom` reads the same fields and then loops over custom field tags. Unknown forward-compatible tags are skipped after reading a length-prefixed value; tags with `kForwardIncompatibleMask` set return corruption. `DebugString`, `DebugJSON`, equality operators, stream output, and `JSONWriter` output expose diagnostic forms with checksum value rendered as hex.

## State, Persistence, and Risks
The binary format is persisted in the manifest, so tag values are compatibility-critical. Dependencies include varint/length-prefixed coding, `Slice`, `Status`, `JSONWriter`, and sync points for test injection. Risks include malformed manifests, checksum method/value consistency only asserted by constructor, and forward-incompatible tag handling. Tests cover empty/non-empty records, decode truncation, and custom-field compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_addition.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_addition.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_addition.h

## Purpose
Declares `BlobFileAddition`, the manifest record describing a newly generated blob file.

## Important APIs and State
The class stores blob file number, total blob count, total blob bytes, checksum method, and checksum value. The default file number is `kInvalidBlobFileNumber`. The value constructor asserts checksum method/value are both empty or both non-empty. Accessors expose all fields. `EncodeTo`, `DecodeFrom`, `DebugString`, and `DebugJSON` provide persistence and diagnostics. Equality, inequality, stream, and JSON operators are declared.

## Dependencies, Risks, and Integration
It depends on blob constants, `Slice`, `Status`, and `JSONWriter`. The object is used by `BlobFileBuilder` when a blob file closes successfully and by version/manifest logic that applies blob-file additions. Risks are persisted-format compatibility and callers treating default records as valid additions. Tests in `blob_file_addition_test.cc` cover the public contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_addition.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_addition_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_addition_test.cc

## Purpose
Tests binary compatibility and error handling for `BlobFileAddition`.

## Important Test Flow
`TestEncodeDecode` round-trips an addition and compares equality. `Empty` checks default sentinel and zero counts. `NonEmpty` validates explicit fields including checksum bytes. `DecodeErrors` incrementally appends fields to a string and verifies corruption messages for missing blob file number, total count, total bytes, checksum method, checksum value, custom field tag, and custom field value. `ForwardCompatibleCustomField` injects an unknown compatible tag through sync point and expects decode success. `ForwardIncompatibleCustomField` injects a masked tag and expects corruption.

## Dependencies, Risks, and Test Signals
The tests depend on coding utilities and sync points. They are a strong signal for persisted manifest compatibility, especially around extension tags. Remaining risk is that they do not test extra trailing bytes after the end marker or constructor assertion behavior in release builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_addition_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_builder.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_builder.cc

## Purpose
Implements blob-file creation for flush/compaction paths: decide whether a value becomes a blob, open blob files, optionally compress values, write records, close files with footer/checksum metadata, optionally prepopulate blob cache, and return blob indexes.

## Important APIs and Control Flow
The `VersionSet*` constructor delegates to a file-number generator. `Add` ignores empty or below-`min_blob_size_` values, opens a file if needed, compresses via builtin compressor when configured, writes a blob record, closes the file if size limit is reached, warms blob cache if configured, and encodes a `BlobIndex` with file number, offset, stored size, and compression type. `OpenBlobFileIfNeeded` allocates a file number, builds a `BlobFileName`, notifies callback, creates a writable file with no-reopen/no-readers contract, configures IO priority/hints, wraps it in `WritableFileWriter` and `BlobLogWriter`, and writes a header. `CloseBlobFile` appends footer, calls completion callback, records `BlobFileAddition`, logs, and resets counters. `Abandon` reports completion with error and drops open writer.

## State, Dependencies, and Risks
State includes file generator, options, compression objects, callback, output vectors, writer, and per-file count/byte counters. Persistent outputs are blob files and manifest additions. Dependencies include filesystem, checksum handoff, IO tracing, compression, blob log format/writer, blob cache typed interface, and event callbacks. Risks include always storing compressed output even if larger, callback/reporting failures, partial file cleanup relying on `blob_file_paths_`, cache prepopulation using original uncompressed value while blob index size records stored bytes, and sync-point-tested I/O failure paths. `blob_file_builder_test.cc` covers core behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_builder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_builder.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_builder.h

## Purpose
Declares `BlobFileBuilder`, the stateful helper that writes one or more blob log files and produces blob indexes plus manifest-addition metadata.

## Important APIs and State
Constructors accept either a `VersionSet` or explicit file-number generator, filesystem/options, DB/session/job/column-family identifiers, write lifetime hint, IO tracer, completion callback, creation reason, and output vectors for paths/additions. Public methods are `Add(key, value, blob_index)`, `Finish()`, and `Abandon(status)`. Private helpers manage file-open state, compression, record writing, close-if-needed, close, and cache prepopulation.

## Dependencies, Risks, and Integration
Members cache mutable options such as `min_blob_size_`, `blob_file_size_`, compression type, compressor working area, and prepopulate policy. Integration points are flush/compaction builders, version-edit generation, blob cache warming, event listeners, and file checksums. Risks include non-copyable state, required empty output vectors, pointer lifetime for options, and correct finalization on error. Tests exercise construction with a mock filesystem and injected failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_builder_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_builder_test.cc

## Purpose
Unit tests for `BlobFileBuilder` output files, blob indexes, metadata, compression, checksums, threshold inlining, and error paths.

## Important Test Flow
`BlobFileBuilderTest` uses `MockEnv`, a deterministic file-number generator, and `VerifyBlobFile`, which opens blob files, reads headers/records/footer with `BlobLogSequentialReader`, and validates blob indexes point to the correct file number and offset. `BuildAndCheckOneFile` writes multiple blobs into one file; `BuildAndCheckMultipleFiles` forces one blob per file; `InlinedValues` verifies below-threshold values create no files/additions. `Compression` validates Snappy-compressed records and metadata byte counts. `CompressionError` injects a compression corruption and checks path tracking without addition. `Checksum` uses a dummy checksum factory. Parameterized `BlobFileBuilderIOErrorTest` injects errors at file creation, header write, record write, and footer append.

## Dependencies, Risks, and Test Signals
The tests depend on mock env, blob log reader/writer, file naming, compression support, sync points, and checksum factories. They provide strong file-format and metadata signals but do not deeply test cache prepopulation or completion callback side effects.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_builder_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_cache.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_cache.cc

## Purpose
Implements a typed cache for `BlobFileReader` objects so blob reads can share open file readers and coordinate refreshes for direct-write active blob files.

## Important APIs and Control Flow
`GetBlobFileReader` looks up a cache key derived from blob file number, returns a guarded handle on hit, otherwise locks a per-key stripe, double-checks, records `NO_FILE_OPENS`, creates a `BlobFileReader`, optionally retries footer-validation corruption with `skip_footer_validation`, inserts it with charge 1, releases ownership to cache, and returns a guard. `OpenBlobFileReaderUncached` opens without insertion. `InsertBlobFileReader` installs an uncached reader unless another thread already cached one. `RefreshBlobFileReader` compares cached and new reader file sizes; it preserves the larger observed size, otherwise erases/replaces under the stripe mutex. `Evict` erases a blob reader under lock.

## State, Dependencies, and Risks
State includes a `BasicTypedCacheInterface<BlobFileReader>`, 128 mutex stripes, immutable/file options, column family id, histogram, and IO tracer. Dependencies include `BlobFileReader::Create`, cache handle guards, statistics tickers, logging, and hash-derived cache keys. Risks include shared cache capacity failures, reader replacement races if file size is not a sufficient freshness proxy, and optional footer-skip retry for active/incomplete files. Tests cover cache hits, race double-checking, refresh preserving largest file size, missing-file errors, and strict-capacity failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_cache.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_cache.h

## Purpose
Declares `BlobFileCache`, the cache facade for opening, caching, refreshing, and evicting blob file readers.

## Important APIs and State
`GetBlobFileReader` returns a cached reader, opening and caching on miss. `OpenBlobFileReaderUncached` opens without cache insertion. `InsertBlobFileReader` transfers a unique reader into the cache unless one already exists. `RefreshBlobFileReader` replaces an existing reader only when the new reader has seen a larger file size. `Evict` removes obsolete file readers. `GetHelper` exposes the typed cache helper. Members include the typed cache interface, striped mutexes, immutable/file options, column family id, read histogram, and IO tracer.

## Dependencies, Risks, and Integration
It depends on `typed_cache.h`, `BlobFileReader`, and RocksDB cache APIs. State is in the shared cache and mutex stripes, not persisted on disk. Risks include requiring caller-provided `CacheHandleGuard` emptiness, ownership transfer via raw pointer release, and shared cache collisions/capacity with table cache. Integration points are blob reads, direct-write blob fallback, file obsoletion, and tests in `blob_file_cache_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_cache_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_cache_test.cc

## Purpose
Tests `BlobFileCache` open/cache/refresh/error behavior using mock filesystem blob files.

## Important Test Flow
`WriteBlobFile` creates a valid blob log with one record and footer. `GetBlobFileReader` verifies first read opens and caches, second read reuses the same reader, and statistics show one open and no errors. `GetBlobFileReader_Race` uses a sync point to recursively open the same file between initial miss and lock acquisition, validating double-check behavior. `RefreshBlobFileReaderPrefersLargestObservedFileSize` creates an active blob file, opens stale and fresh uncached readers with footer-skip retry, refreshes cache with the larger observed size, and confirms a later stale refresh preserves the larger cached reader. Error tests cover missing blob file I/O error and zero-capacity strict cache memory-limit failure.

## Dependencies, Risks, and Test Signals
The tests depend on mock env, blob log writer, file naming, cache implementation, statistics, and sync points. They directly signal concurrency and active-file refresh correctness. They do not cover explicit `Evict` or `InsertBlobFileReader` separately.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_cache_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_completion_callback.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_completion_callback.h

## Purpose
Defines callback behavior around blob file creation start and finish, tying blob files into event listeners, event logging, SST file manager accounting, and background error handling.

## Important APIs and Control Flow
The constructor stores `SstFileManager`, DB mutex, error handler, event logger, listeners, and DB name. `OnBlobFileCreationStarted` notifies listeners through `EventHelpers::NotifyBlobFileCreationStarted`. `OnBlobFileCompleted` casts the manager to `SstFileManagerImpl`, calls `OnAddFile`, checks max allowed space, and if exceeded sets a flush background error under mutex. It then logs/notifies creation finished, using reported status if non-OK, otherwise the file-manager status, and substituting unknown checksum names/values when empty.

## State, Dependencies, and Risks
State is non-owning manager/mutex/error-handler/logger pointers plus copied listener vector and DB name. It persists no data directly but affects space accounting and background error state. Risks include static cast assumptions, null pointer assumptions, space-limit side effects only for `SstFileManagerImpl`, and completion callback errors being propagated to builder close. Integration points are blob file builder, event listeners, and SstFileManager quotas.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_completion_callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_garbage.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_garbage.cc

## Purpose
Implements manifest encoding, decoding, comparison, and debug output for blob-file garbage records.

## Important APIs and Control Flow
`EncodeTo` writes blob file number, garbage blob count, garbage blob bytes, optional custom fields via sync point, and an end marker. `DecodeFrom` reads required fields and then loops over custom tags, ignoring unknown forward-compatible fields after reading their length-prefixed value and rejecting tags with `kForwardIncompatibleMask`. `DebugString`, `DebugJSON`, equality operators, stream output, and JSON output provide diagnostics.

## State, Persistence, and Risks
The encoded form is manifest-persisted, making tag stability important. Dependencies include coding utilities, `Slice`, `Status`, `JSONWriter`, and sync points. Risks mirror addition records: truncated data corruption, future extension compatibility, and default invalid blob file number use. Tests cover round-trips, decode errors, and custom-field compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_garbage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_garbage.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_garbage.h

## Purpose
Declares `BlobFileGarbage`, the manifest record that accumulates garbage blob count and bytes for a blob file.

## Important APIs and State
The class stores blob file number, garbage blob count, and garbage blob bytes. Defaults use `kInvalidBlobFileNumber` and zero counts. Accessors expose fields. `EncodeTo`, `DecodeFrom`, `DebugString`, and `DebugJSON` provide persistence and diagnostics. Equality, inequality, stream, and JSON operators are declared.

## Dependencies, Risks, and Integration
It depends on blob constants, `Slice`, `Status`, and `JSONWriter`. It integrates with version edit/application logic that tracks blob garbage from compactions. Risks include persisted-format compatibility and callers constructing garbage counts beyond total file counts; that cross-check is likely enforced by higher-level metadata/version code. Tests in `blob_file_garbage_test.cc` validate the record-level contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_garbage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_garbage_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_garbage_test.cc

## Purpose
Tests serialization compatibility and corruption handling for `BlobFileGarbage`.

## Important Test Flow
`TestEncodeDecode` round-trips a record and verifies equality. `Empty` checks invalid default file number and zero garbage counts. `NonEmpty` validates explicit file number/count/bytes. `DecodeErrors` builds a truncated payload step by step and expects corruption messages for missing blob file number, garbage count, garbage bytes, custom field tag, and custom field value. `ForwardCompatibleCustomField` injects an unknown compatible tag and expects successful decode. `ForwardIncompatibleCustomField` injects a masked tag and expects corruption.

## Dependencies, Risks, and Test Signals
The tests use coding helpers and sync points. They strongly cover manifest extension behavior. Remaining risks are semantic validation of garbage values against blob-file totals and trailing bytes after end marker, which are outside this record-level test.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_garbage_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_meta.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_meta.cc

## Purpose
Implements derived size calculation and debug formatting for blob file metadata objects.

## Important APIs and Control Flow
`SharedBlobFileMetaData::GetBlobFileSize` returns `BlobLogHeader::kSize + total_blob_bytes_ + BlobLogFooter::kSize`. `SharedBlobFileMetaData::DebugString` and stream output render file number, total count/bytes, checksum method, and checksum value as hex. `BlobFileMetaData::DebugString` and stream output render the shared metadata, linked SST file numbers, garbage blob count, and garbage blob bytes.

## State, Dependencies, and Risks
This file does not mutate metadata; it exposes derived and diagnostic views. It depends on blob log format sizes and `Slice` hex rendering. Risks include derived file size assuming fixed header/footer and `total_blob_bytes_` already including record headers/key/value bytes as maintained elsewhere. Integration points include version/debug logging and metadata inspection.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_meta.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_meta.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_meta.h

## Purpose
Declares shared and version-specific blob file metadata models used by RocksDB versions.

## Important APIs and State
`SharedBlobFileMetaData` is immutable, non-copyable/non-movable, and intended to be shared across versions for the same blob file. Static `Create` overloads construct shared pointers, optionally with a custom deleter used to mark obsolescence on destruction. It stores file number, total blob count/bytes, checksum method, and checksum value. `BlobFileMetaData` wraps shared metadata with version-specific `linked_ssts_`, garbage blob count, and garbage blob bytes. It asserts garbage does not exceed total counts/bytes and forwards shared accessors.

## Dependencies, Risks, and Integration
The metadata is in-memory version state derived from manifest additions/garbage records and blob file lifecycle. Dependencies are C++ shared ownership and unordered sets. Risks include non-deterministic linked-SST debug ordering, custom deleter side effects, and invariant checks being assertions rather than runtime status. Integration points are VersionSet/version edits, blob garbage collection, obsolete-file deletion, and debug logging.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_meta.h -->
