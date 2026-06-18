# subset-b-008155 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/evtree.c -->
# sources/object-store/daos/src/vos/evtree.c

## Purpose
Implements DAOS VOS epoch/extent tree storage for versioned array-value extents. It stores rectangles keyed by logical extent plus major/minor epoch, tracks persistent `umem` nodes/descriptors, finds visible data for reads/iteration, inserts overwrites or punches, deletes exact records, drains/destroys trees, and maintains checksum metadata attached to extent descriptors.

## Important APIs, Types, And Functions
Public entry points include `evt_create`, `evt_open`, `evt_close`, `evt_destroy`, `evt_insert`, `evt_find`, `evt_delete`, `evt_remove_all`, `evt_drain`, `evt_debug`, `evt_has_data`, `evt_feats_set`, checksum helpers, and overhead/validation helpers. Internal flow is organized around `struct evt_context`, `struct evt_trace`, policy ops (`evt_soff_pol_ops`, `evt_sdist_pol_ops`, `evt_sdist_even_pol_ops`), durable `struct evt_root`, persistent `struct evt_node`, `struct evt_node_entry`, and `struct evt_desc`. `evt_ent_array_fill` and `evt_ent_array_sort` are central to query results and visibility calculation.

## Control Flow
Creation initializes a context, selects a tree policy from feature bits, initializes the root in a transaction, and returns a handle. Insert first probes for same-epoch overwrite/uncertainty, then begins a transaction, activates an empty root if needed, and calls `evt_insert_entry`. Tree descent chooses the child with the smallest MBR weight growth; `evt_insert_or_split` inserts into a leaf or splits nodes upward, possibly creating a new root. Finds traverse MBRs with `evt_filter_rect`, overlap checks, DTX availability callbacks, and then sort/split candidates to produce visible extents. Removal inserts hole/removal records for visible ranges; exact delete locates one record and bubbles node removal/MBR updates upward.

## State And Persistence
Persistent state is in the caller-owned root and `umem` allocated nodes/descriptors. Mutations use `evt_tx_begin`, `evt_root_tx_add`, `evt_node_tx_add`, `umem_tx_add_ptr`, `vos_obj_alloc`, and `umem_free`. The tree stores fixed `tr_inob`, checksum configuration, feature bits, order/max order, depth, pool UUID, and root node offset. Descriptors persist bio addresses, checksums, versions, and DTX state through callbacks.

## Dependencies And Integration
Depends on `evt_priv.h`, DAOS checksum helpers, VOS object allocation, `umem`, bio address semantics, DTX availability/log callbacks, and VOS tree callers in `vos_tree.c`/`vos_io.c`. Policy operations isolate sort/split behavior from generic tree mutation.

## Risks
The implementation is transaction-sensitive and relies on trace correctness across splits/deletes. Same-epoch partial overwrite is intentionally rejected. Large non-hole extents above durable length encoding are rejected; large hole insertion is decomposed through a query pass. Visibility splitting can allocate up to a computed upper bound and returns `-DER_AGAIN` on reallocation to restart safely. Data-loss handling depends on `evt_desc_log_status` returning `-DER_DATA_LOSS`. Source has suspicious duplicated lines in a few places, so future edits should compile-check carefully.

## Test Signals
Direct tests are not in this subset. Integration signals are DAOS VOS tests (`run_ilog_tests` and broader VOS suites), VOS IO paths that call `evt_find`/checksum helpers, and storage estimator tests that model related VOS structure overhead. High-value tests are insert/find visibility overlap cases, same-epoch overwrite rejection, hole/removal aggregation, checksum slicing, node split/delete, DTX unavailable/data-loss statuses, and dynamic-root order growth.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/evtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/ilog.c -->
# sources/object-store/daos/src/vos/ilog.c

## Purpose
Implements VOS incarnation logs for object/key create/update/punch history. It records epoch plus DTX/minor-epoch identity, resolves committed/uncommitted/removed status through callbacks, persists/aborts transaction entries, fetches cached log state for visibility checks, and aggregates obsolete entries.

## Important APIs, Types, And Functions
Public APIs include `ilog_init`, `ilog_create`, `ilog_open`, `ilog_close`, `ilog_destroy`, `ilog_update`, `ilog_set_flags`, `ilog_persist`, `ilog_abort`, `ilog_fetch_*`, `ilog_aggregate`, `ilog_is_corrupted`, `ilog_ts_idx_get`, `ilog_version_get`, `ilog_root_is_valid`, and `ilog_is_valid`. Key internals are `struct ilog_context`, `struct ilog_array_cache`, `struct ilog_priv`, `ilog_modify`, `ilog_tree_modify`, `ilog_root_migrate`, `update_inplace`, `remove_entry`, `reset_root`, `ilog_status_refresh`, and aggregation helpers.

## Control Flow
`ilog_create` writes a valid magic/version root. `ilog_open` wraps a root and callbacks in a handle. Updates build an `ilog_id` and call `ilog_modify`, which handles flag updates, empty inline insert, inline update/remove, migration to an allocated sorted array on the second distinct entry, and array insertion/removal for larger logs. Persist clears the transaction id for the matching entry; abort removes it. Fetch initializes or reuses `ilog_entries` cache when root pointer and version match, refreshing statuses by intent. Aggregation fetches entries, classifies them with parent punch/discard/in-progress state, marks removals, collapses arrays, and may reduce the root back to inline or empty.

## State And Persistence
The durable root is exactly `struct ilog_df` sized and stores magic/version/flags, timestamp index, and either inline `ilog_id` or an allocated `ilog_array`. Version bits change on mutations so callers can cache safely. All persistent writes go through `umem` transactions and undo logging. DTX registration/deregistration is delegated through callback hooks.

## Dependencies And Integration
Depends on DAOS/VOS types, `umem`, `vos_layout`, `vos_ts`, DTX helpers, and `ilog_internal.h`. Higher layers wrap it through `vos_ilog.h` for object/key visibility, punches, timestamp cache entries, and corruption failout.

## Risks
The header comment still says B+tree fallback, but the current implementation uses a dynamically resized array; readers should not infer B-tree behavior. Correctness depends on sorted epoch order, version updates, callback status semantics, and no same-epoch conflicting DTX mutations. Fixed-epoch mode intentionally relaxes equality checks for rebuild/aggregation-style operations. `ilog_fetch_finish` frees dynamic status arrays but not root-owned ids. Aggregation aborts on uncommitted entries unless discarding in-progress entries.

## Test Signals
VOS test harness references `run_ilog_tests`. Expected test coverage includes inline-empty/one-entry/multi-entry transitions, persist/abort callback behavior, fetch cache invalidation by version and intent, discard/in-progress aggregation, corrupted flag handling, and `ilog_is_valid` recovery checks.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/ilog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/ilog.h -->
# sources/object-store/daos/src/vos/ilog.h

## Purpose
Public interface for VOS incarnation logs. It exposes the durable root placeholder, log entry identity/status types, callback contract for DTX integration, fetch result containers, iteration macros, mutation APIs, aggregation API, timestamp-index access, version access, and validation helpers.

## Important APIs, Types, And Functions
`struct ilog_id` packs DTX id, punch/update minor epochs, and major epoch. `struct ilog_df` is an opaque 24-byte durable root. `enum ilog_status` describes invalid, committed, uncommitted, and removed states. `struct ilog_desc_cbs` bridges to transaction status/add/delete logic. `struct ilog_entry`, `struct ilog_info`, and `struct ilog_entries` model fetched logs. APIs cover lifecycle (`ilog_init/create/open/close/destroy`), mutation (`ilog_update`, `ilog_set_flags`, `ilog_persist`, `ilog_abort`), aggregation/fetch, and validation.

## Control Flow
Callers create a root in persistent memory, open it with callbacks and fixed-epoch mode, update/punch with epoch range and minor epoch, persist/abort DTX-backed entries, fetch entries for visibility checks, aggregate stale ranges, then close/destroy. Fetch callers use `ilog_fetch_init`, optional `ilog_fetch_move`, iteration macros, and `ilog_fetch_finish`.

## State And Persistence
The header intentionally hides the real root layout behind `ilog_df`; `ilog_internal.h` defines the inline/array layout. `ILOG_PRIV_SIZE` reserves private cache space inside `ilog_entries`, so callers allocate one structure while implementation stores embedded cache state.

## Dependencies And Integration
Depends only on DAOS public types and an opaque `umem_instance`; implementation links to VOS/DTX. Used by `vos_ilog.h` wrappers and VOS object/key trees.

## Risks
The API requires nonzero epochs/minor epochs for meaningful updates. Callback omissions default some behavior to committed/no-op, useful for tests but risky if a production caller forgets DTX hooks. Iteration macros assume `ilog_fetch_init` has set up internal storage. Comments contain typos and one duplicated parameter name, but API intent is clear.

## Test Signals
Tests should validate lifecycle error returns, callback ordering, iteration forward/reverse behavior, cache move/finalization, aggregation return value `1` for empty logs, and validation/corruption helpers.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/ilog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/ilog_internal.h -->
# sources/object-store/daos/src/vos/ilog_internal.h

## Purpose
Defines the private durable layout and bit packing for incarnation logs. It is shared by `ilog.c` and recovery/validation code but hidden from normal callers.

## Important APIs, Types, And Functions
Macros partition `lr_magic` into 4 magic bits, 24 version bits, and 4 flag bits. `ILOG_MAGIC_VALID`, version/flag masks, and increment constants drive mutation-version tracking. `struct ilog_tree` holds an allocated array offset plus an `it_embedded` discriminator. `struct ilog_root` overlays inline `ilog_id` and tree metadata, adds `lr_ts_idx`, and stores packed magic. `ilog_empty` checks both embedded and array offset fields. `struct ilog_array` is a flexible-array durable sorted list.

## Control Flow
New roots start with valid magic/version and empty tree fields. First entry is stored inline in `lr_id` and indicated by nonzero `lr_tree.it_embedded` through the union. Multiple entries use `lr_tree.it_root` pointing to an `ilog_array`. Removal can reset to empty or collapse back to inline.

## State And Persistence
All structures are durable ABI. `D_CASSERT` in `ilog.c` ensures `ilog_id` and `ilog_tree` share size and `ilog_root` matches public `ilog_df`. Version wrap preserves magic/flags while cycling version bits.

## Dependencies And Integration
Requires `ilog.h` definitions and `umem_off_t`. Timestamp cache integration uses `lr_ts_idx` via `ilog_ts_idx_get` and VOS timestamp-set wrappers.

## Risks
The union means consumers must respect the embedded/root discriminator; reading the wrong union member can misclassify state. Bit-field packing leaves only four flag bits. Any durable layout change must preserve `sizeof(struct ilog_df)` or migrate data.

## Test Signals
Validation should cover magic recognition, empty/inline/array state transitions, version increment wrap, flags such as corruption, and ABI size assertions.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/ilog_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/lru_array.c -->
# sources/object-store/daos/src/vos/lru_array.c

## Purpose
Implements a generic fixed-index LRU cache/allocator backed by one or more lazily allocated subarrays. It provides allocation, lookup support through header inlines, explicit eviction, memory accounting callbacks, and aggregation of empty subarrays.

## Important APIs, Types, And Functions
Exports `lrua_array_alloc_one`, `lrua_find_free`, `lrua_evictx`, `lrua_array_alloc`, `lrua_array_free`, and `lrua_array_aggregate`. Internal callbacks wrap user `lru_callbacks` for init/fini/evict/alloc/free. `sub_find_free`, `manual_find_free`, and `array_free_one` manage circular free/LRU lists.

## Control Flow
Allocation validates power-of-two entry and subarray counts, aligns payload size, allocates the top-level array, initializes unused/free lists, then allocates the first subarray. Lookup is inline in the header. Allocation first removes an entry from a free list and inserts it as MRU; if automatic eviction is enabled and no free entry remains, it evicts the current LRU. Manual eviction mode searches subarrays with free entries or allocates an unused subarray, returning `-DER_BUSY` when capacity is exhausted.

## State And Persistence
State is in heap memory, not persistent storage. Each `lru_entry` stores key, payload pointer, and circular prev/next indexes. Each subarray tracks active LRU head, free head, payload/table pointers, and list membership. `la_evicting` prevents reentrant lookup from moving an entry while its eviction callback runs.

## Dependencies And Integration
Depends on DAOS allocation/list/assertion utilities and `vos_internal.h`. Consumers supply typed payload sizes and callbacks; header macros cast payload pointers.

## Risks
Requires `nr_ent` and `nr_arrays` powers of two and `nr_ent > nr_arrays`; these are assertions, not runtime recovery. Multi-subarray mode forces manual eviction because no global LRU exists. Key zero is invalid and marks free entries. Callback implementations must tolerate eviction/reset timing. A duplicated line appears in `lrua_lookup_idx` in the provided source and should be compile-checked.

## Test Signals
Useful tests cover allocation/free callbacks, automatic eviction order, manual eviction `-DER_BUSY`, explicit `lrua_evictx`, in-place allocation, multi-subarray aggregation, reuse-unique free ordering, and invalid stale key lookup.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/lru_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/lru_array.h -->
# sources/object-store/daos/src/vos/lru_array.h

## Purpose
Declares and partially implements the generic LRU array abstraction. The header contains public types, flags, index helpers, lookup/peek/allocation inline APIs, and internal circular-list helpers used by the C file.

## Important APIs, Types, And Functions
`struct lru_callbacks` defines lifecycle hooks. `struct lru_entry`, `struct lru_sub`, and `struct lru_array` define the cache layout. Flags are `LRU_FLAG_EVICT_MANUAL` and `LRU_FLAG_REUSE_UNIQUE`; `LRU_NO_IDX` marks empty lists. Public macros include `lrua_lookupx`, `lrua_lookup`, `lrua_peekx`, `lrua_peek`, `lrua_allocx`, `lrua_alloc`, and `lrua_allocx_inplace`; C-file APIs allocate, free, evict, and aggregate arrays.

## Control Flow
Header lookups compute subarray and entry index via bit masks, validate key match, optionally promote to MRU, and return typed payloads. Allocation macros call `lrua_find_free`; in-place allocation allocates the subarray if absent, verifies the target slot is free, removes it from the free list, inserts it in the active list, and returns the payload.

## State And Persistence
All state is volatile. Payload memory is colocated after the `lru_entry` table in each subarray allocation. Circular lists use entry indexes, not pointers, so entries remain stable within a subarray.

## Dependencies And Integration
Depends on `daos/common.h` list and assertion utilities. Designed for VOS caches that need stable integer handles and callback-driven cleanup.

## Risks
The inline-heavy API means misuse can compile but corrupt list state if callers pass stale indexes or wrong keys. `lrua_alloc` uses the address of the index variable as a default key, so persistent indexes must be logged before mutation as documented. Manual mode requires explicit eviction by the owner.

## Test Signals
Header behavior should be tested via typed callers: lookup vs peek MRU effects, allocation key matching, in-place duplicate rejection, and subarray index/mask conversions.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/lru_array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/pmdk_log.c -->
# sources/object-store/daos/src/vos/pmdk_log.c

## Purpose
Bridges PMDK/libpmemobj logging into DAOS logging when built with persistent-memory support. It registers a PMDK log callback that maps PMDK severity levels to DAOS log levels and formats messages with PMDK source location.

## Important APIs, Types, And Functions
`pmdk_log_attach` is the exported entry point. Under `DAOS_PMEM_BUILD`, `pmdk_log_function` is registered with `pmemobj_log_set_function`. The severity table maps `PMEMOBJ_LOG_LEVEL_*` values to DAOS `DLOG_*` levels and saved masks. `PMDK_LOG_NOCHECK` adapts DAOS logging internals to use callback-provided file, line, and function data.

## Control Flow
At attach time, DAOS asks PMDK to use `pmdk_log_function`. For each PMDK message, the callback normalizes leading `../` and `src/../src` path patterns, prefixes the filename with `pmdk/`, then emits through DAOS logging with the mapped severity and saved mask.

## State And Persistence
No persistent state. Runtime state is the static mapping table and PMDK's registered callback pointer.

## Dependencies And Integration
Compiled only with `DAOS_PMEM_BUILD`; depends on `daos/debug.h`, `daos/common.h`, `libpmemobj/log.h`, and `libpmemobj.h`. The path prefix is intentionally used by DAOS pipeline/NLT log filtering.

## Risks
The non-PMEM stub contains only `;` in an `int` function, which relies on compiler behavior and should return a value for strict builds. The callback indexes the severity table by PMDK enum value; new/out-of-range PMDK levels would be unsafe unless PMDK guarantees the enum range. It uses DAOS internal logging macros, so logging API changes could break it.

## Test Signals
Build tests should cover both PMEM and non-PMEM configurations. Runtime tests can inject PMDK messages and verify DAOS severity, filename normalization, and `pmdk/` prefix.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/pmdk_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/pmdk_log.h -->
# sources/object-store/daos/src/vos/pmdk_log.h

## Purpose
Public declaration for attaching DAOS logging to PMDK logging.

## Important APIs, Types, And Functions
Declares `int pmdk_log_attach(void);` behind include guard `__PMDK_LOG__`.

## Control Flow
Callers include the header and invoke `pmdk_log_attach` during PMDK/VOS initialization to register the PMDK log callback if the build supports it.

## State And Persistence
No state is defined here.

## Dependencies And Integration
Implemented by `pmdk_log.c`; integration depends on DAOS initialization order and PMDK build configuration.

## Risks
The header exposes no build-configuration indication, so callers must rely on implementation behavior in non-PMEM builds.

## Test Signals
Compile coverage is the primary signal; runtime attach behavior is tested through `pmdk_log.c`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/pmdk_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/__init__.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/__init__.py

## Purpose
Package initializer for the storage estimator common Python modules. It declares the modules intended for wildcard export.

## Important APIs, Types, And Functions
`__all__` lists `dfs_sb`, `explorer`, `parse_csv`, `vos_size`, `vos_structures`, and `util`.

## Control Flow
No runtime control flow beyond module import.

## State And Persistence
No state or persistence.

## Dependencies And Integration
Used when importing `storage_estimator` common modules from CLI scripts and tests.

## Risks
If modules are renamed or added without updating `__all__`, wildcard import behavior diverges from package contents.

## Test Signals
Import tests and CLI smoke tests indirectly validate it.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/dfs_sb.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/dfs_sb.py

## Purpose
Discovers DFS superblock and VOS structure metadata from installed DAOS shared libraries and converts it into storage-estimator YAML or `vos_structures` objects.

## Important APIs, Types, And Functions
Helper functions render or parse DFS dkeys/akeys (`_print_akey`, `_print_dkey`, `_print_dfs_inode`, `_create_akey`, `_parse_dfs_sb_dkey`, `_parse_dfs_akey_inode`). `STR_BUFFER` models C string ownership. `BASE_CLASS` loads shared libraries. `VOS_SIZE` calls `get_vos_structure_sizes_yaml`; `DFS_SB` calls `dfs_get_sb_layout` and frees it through `FREE_DFS_SB`. Public helpers include `print_daos_version`, `get_dfs_sb_obj`, `get_dfs_inode_akey`, `get_dfs_sb`, and `get_dfs_example`.

## Control Flow
`DFS_SB` lazily calls the C library on first getter, then caches readiness. YAML-generation functions format returned C IOV/IOD data into estimator configuration fragments. Object-generation functions convert the same data into `DKey`, `AKey`, `VosValue`, and `VosObject` instances. `get_dfs_example` concatenates a static header, live superblock YAML, and sample file/dir template.

## State And Persistence
State is in Python wrapper objects and C-allocated memory freed in destructors. No files are written here, except callers may persist returned YAML.

## Dependencies And Integration
Depends on `ctypes`, `pydaos.raw.daos_cref`, `libdfs.so`, `daos_srv/libvos_size.so`, DAOS `VERSION`, and `storage_estimator.vos_structures`.

## Risks
Library paths are relative to this source file and require a built/installed DAOS tree. Destructor-based freeing may be fragile during interpreter shutdown. `iod_type` handling assumes values 1 and 2. YAML is assembled with string formatting rather than a YAML emitter, so unusual key bytes could break output.

## Test Signals
Tests mock comparable superblock objects in `storage_estimator_test.py`; shell smoke tests call `create_example`. Full coverage requires an environment with DAOS shared libraries.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/dfs_sb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/explorer.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/explorer.py

## Purpose
Models filesystem contents as DAOS DFS/VOS storage-estimator structures. It can build detailed structures from an actual directory walk or average structures from aggregate counts and sizes.

## Important APIs, Types, And Functions
`FileInfo` and `Entry` abstract Python version differences in directory entries. `CellStats` tracks payload/parity cells. `DFS` builds `VosObject`/`DKey`/`AKey` representations for directories, files, symlinks, replicated data, and erasure-coded layouts. `AverageFS` creates a summarized DFS model from counts/averages. `FileSystemExplorer` walks the filesystem, collects stats, and exposes detailed or average DFS models.

## Control Flow
`FileSystemExplorer.explore` resets stats, enqueues the root, creates one directory object per visited directory, and processes entries with `os.scandir` on Python 3.5+ or `os.listdir` fallback. File entries add metadata to the current directory object and create file data objects. Directories enqueue traversal. Symlinks add inode values sized by link length. `DFS.create_file_obj` splits file sizes by chunk, IO size, object class replication/parity, EC cell size, and optional aggregation assumption.

## State And Persistence
All structures are in memory until callers dump YAML. Explorer state tracks queue, counts, sizes, current object id, and generated `DFS`. No persistent writes occur in this module.

## Dependencies And Integration
Depends on `storage_estimator.util.ObjectClass/CommonBase` and `vos_structures`. Consumed by CLI commands for `explore_fs`, CSV processing through `AverageFS`, and tests.

## Risks
There are user-visible typo/debug issues (`Gloabal`, swapped labels in `print_stats`, `self.dfs` instead of `_dfs` in `set_dfs_file_meta`). Empty directories remove the just-created object. EC math has several branches where edge cases around partial chunks/cells should be regression-tested. Directory traversal follows real paths for queued directories, which may collapse symlinked paths.

## Test Signals
`FSTestCase` builds a mock filesystem and compares aggregate object/dkey/akey/value stats for SX, RP_3GX, and EC_16P2GX classes. More direct tests should cover zero-length files, empty directories, symlinks, permission errors, EC partial chunks, and average model calculations.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/explorer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/parse_csv.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/parse_csv.py

## Purpose
Implements the storage estimator CSV ingestion command. It converts one-row CSV summary data into an `AverageFS` model, dumps YAML, and runs the normal YAML processing pipeline.

## Important APIs, Types, And Functions
`FILE_SIZES` defines supported size buckets. `ProcessCSV` extends `ProcessBase`; `run` coordinates ingest, YAML dump, output creation, and processing. `_ingest_csv` parses fields, computes average directory/symlink/file sizes, configures `AverageFS`, reads live DFS inode metadata through `get_dfs_inode_akey`, and adds file buckets.

## Control Flow
The parser reads exactly two CSV lines: header and values. It validates equal field/value counts, extracts known fields with defaults, computes unknown item count for logging, initializes `AverageFS` from CLI object class/settings, and iterates `FILE_SIZES` to add average file objects for nonzero buckets.

## State And Persistence
`run` writes the generated YAML to `args.output` through `ProcessBase._create_file`; ingest itself returns an in-memory `AverageFS`.

## Dependencies And Integration
Depends on `dfs_sb.get_dfs_inode_akey`, `explorer.AverageFS`, and `util.ProcessBase`. Used by `daos_storage_estimator.py read_csv` and tests.

## Risks
Only one row of values is accepted. `items_per_dir` is computed but unused. `count_dir` defaults to one but a CSV value of zero causes division by zero. Live DFS inode discovery requires DAOS libraries unless tests patch/provide an environment. Error message concatenation lacks spaces before count details.

## Test Signals
`CSVTestCase` validates generated aggregate stats for SX, RP_3GX, and EC_16P2GX using `test_data.csv` and golden YAML files. Shell smoke tests run read_csv with multiple object classes, checksums, and aggregation.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/parse_csv.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/__init__.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/__init__.py

## Purpose
Package initializer for storage-estimator common tests.

## Important APIs, Types, And Functions
Exports `util` through `__all__`, making local test helpers importable as `storage_estimator.common.tests.util` or relative `.util`.

## Control Flow
No runtime control flow beyond package import.

## State And Persistence
No state or persistence.

## Dependencies And Integration
Supports `storage_estimator_test.py`, which imports `FileGenerator` from `.util`.

## Risks
If additional test helper modules are added, wildcard exports will not include them until this list is updated.

## Test Signals
Validated indirectly by pytest collecting and importing the test package.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/pytest.ini -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/pytest.ini

## Purpose
Pytest configuration for storage-estimator tests.

## Important APIs, Types, And Functions
Defines markers `ut`, `sx`, `rp3gx`, and `ec16p2` for data-structure unit tests and object-class-specific estimator scenarios.

## Control Flow
Pytest reads this file during collection to register marker names and avoid unknown-marker warnings.

## State And Persistence
No state or persistence.

## Dependencies And Integration
Used by `storage_estimator.sh`, which invokes pytest separately for each marker.

## Risks
Marker names must match decorators in `storage_estimator_test.py` and shell invocations. New object-class scenarios need marker additions.

## Test Signals
Running `python -m pytest -m ut/sx/rp3gx/ec16p2` exercises the configured markers.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/pytest.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/storage_estimator.sh -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/storage_estimator.sh

## Purpose
Smoke and unit-test driver for the DAOS storage estimator CLI and Python model tests.

## Important APIs, Types, And Functions
Shell functions `print_header` and `check_retcode` provide readable sections and cleanup-on-exit. The script creates a temporary directory, sources `utils/sl/setup_local.sh`, runs pytest marker groups when pytest exists, and then exercises `daos_storage_estimator.py` commands.

## Control Flow
The script sets `set -e` and an EXIT trap. It runs unit/object-class pytest suites, then CLI help and smoke flows for `create_example`, `read_csv`, `read_yaml`, and `explore_fs`. It tests object classes SX, RP_3GX, EC_16P2GX, checksum mode, aggregation mode, IO-size overrides, EC cell/chunk overrides, and YAML round trips.

## State And Persistence
Writes all generated files under a temporary directory and removes it in the exit trap. It depends on the caller's DAOS project setup to provide CLI and library paths.

## Dependencies And Integration
Depends on bash, pytest, Python CLI `daos_storage_estimator.py`, sample CSV/test files, and `setup_local.sh`.

## Risks
If pytest is missing, unit tests are skipped but smoke tests still run. The trap passes `${BASH_COMMAND}` unquoted, so command strings with spaces are lossy in the status message. Environment setup is mandatory and failures abort early. The script mutates no repository files.

## Test Signals
Successful completion indicates importability, marker tests, command help, sample generation, CSV ingestion, YAML ingestion, filesystem exploration, checksum paths, and EC aggregation smoke coverage.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/storage_estimator.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/storage_estimator_test.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/storage_estimator_test.py

## Purpose
Pytest/unittest suite for storage-estimator data structures, filesystem exploration, and CSV ingestion.

## Important APIs, Types, And Functions
`MockArgs` supplies CLI-like options. The `vos_test_data` fixture builds reusable expected dictionaries and mock DFS superblock objects. Test classes cover `VosValue`, `AKey`, `DKey`, `VosObject`, `Container`, `Containers`, filesystem exploration (`FSTestCase`), and CSV ingestion (`CSVTestCase`).

## Control Flow
Unit tests verify constructors, default values, invalid parameter exceptions, `add_value`, and `dump` output. Filesystem tests create a mock tree through `FileGenerator`, configure `FileSystemExplorer`, add a mock DFS superblock object, summarize generated container stats, and compare to golden YAML. CSV tests run `ProcessCSV._ingest_csv`, build DFS structures, add a mock superblock object, and compare aggregate stats against golden files.

## State And Persistence
Tests create temporary mock files through `FileGenerator` and read golden YAML/CSV under `test_files`. They do not modify source state.

## Dependencies And Integration
Depends on pytest, unittest, yaml, `storage_estimator` modules, and local `.util.FileGenerator`. Markers align with `pytest.ini` and shell invocations.

## Risks
Stats comparison aggregates object/dkey/akey/value counts and sizes, so structural differences that preserve totals may pass. Some helper code duplicates production `_process_stats`, including the same `values += total_akeys` style, which may encode expected behavior rather than independent verification. Tests call private `_ingest_csv`, so CLI argument parsing is not covered here.

## Test Signals
Strong signal for schema validation and aggregate estimator math across SX, RP_3GX, and EC_16P2GX. Additional tests should cover direct CLI output files, malformed CSV, zero directories, missing DAOS libraries in `dfs_sb`, and edge EC partial-stripe cases.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/storage_estimator_test.py -->
