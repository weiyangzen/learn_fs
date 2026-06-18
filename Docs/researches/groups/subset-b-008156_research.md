# subset-b-008156 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_16p2gx.yaml -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_16p2gx.yaml

## Purpose
Fixture YAML for the storage estimator's detailed DFS sample when regular file data uses `EC_16P2GX`. It models a small POSIX-like tree with two directories, four regular files, one symlink, and DFS superblock metadata, using the VOS estimator schema consumed by `MetaOverhead`.

## Important APIs, types, and functions
- Top-level `num_shards: 1000` drives how many VOS pools/targets the estimator distributes dkeys across.
- YAML anchors define reusable VOS records: DFS superblock akeys, `dfs_inode`, directory dkeys, file dkeys, and per-file object definitions.
- Keys use `type: hashed` for named DFS metadata/directory entries and `type: integer` for file layout dkeys/akeys.
- Akeys declare `value_type: single_value` for inode-like scalar metadata and `value_type: array` for file/symlink data extents.

## Control flow
There is no executable control flow. When loaded by `read_yaml`, `Common._process_yaml` passes the parsed `containers` list to `MetaOverhead.load_container`. The estimator then walks container -> object -> dkey -> akey -> values, with counts multiplying tree and record overhead. The EC fixture differs from the SX/RP variants by inflating per-file integer dkey counts according to EC 16+2 data/parity layout rather than raw logical chunk counts.

## State and persistence behavior
The file is declarative and persists no runtime state. Its state model mirrors DFS/VOS persistence: one container contains superblock metadata, directory objects contain filename dkeys with `DFS_INODE` values, and regular file objects contain metadata dkeys plus array extents at 128 KiB I/O size. `overhead: meta` assigns key/value bytes to metadata, while `overhead: user` attributes named directory/file bytes to user metadata.

## Dependencies and integration points
It depends on the estimator schema implemented by `vos_size.py` and object builders in `vos_structures.py`: required keys include `containers`, `objects`, `dkeys`, `akeys`, `values`, `value_type`, and `size` for hashed keys/values. The fixture is used by storage-estimator tests comparing generated DFS exploration/CSV output for `EC_16P2GX` against known YAML.

## Risks and edge cases
Because anchors are reused heavily, a changed anchor affects many object sections. Counts encode EC placement assumptions; changes to chunk size, I/O size, EC cell handling, or DAOS object class semantics require coordinated fixture updates. The sample contains the historical spelling `very_importan_file.txt`, so tests relying on exact key sizes should preserve it.

## Test signals
Useful signals are successful YAML parsing, stable estimator totals for the EC_16P2GX object class, and expected differences from SX/RP fixtures in integer dkey counts for data extents and parity-influenced layout.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_16p2gx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_3gx.yaml -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_3gx.yaml

## Purpose
Fixture YAML for the same detailed DFS sample as the SX and EC files, but with regular file data modeled for `RP_3GX` three-way replicated placement. It lets tests verify that replicated object classes expand dkey/value counts differently from spreading or erasure coding.

## Important APIs, types, and functions
- Uses the same estimator schema and anchors as `test_data_sx.yaml`.
- `num_shards: 1000` gives the placement simulator a large target set.
- File metadata dkeys and remainder/data dkeys are integer-keyed, with replicated counts such as larger `driver_dkey1`, `secret_plan_dkey1`, and `very_important_dkey1`.
- DFS metadata and directory records remain hashed and mostly identical across object classes.

## Control flow
The file is read by PyYAML, then `MetaOverhead` recursively initializes objects and distributes dkeys across target pools. Replication is pre-modeled by larger dkey counts in the fixture rather than by runtime object-class parsing in `read_yaml`.

## State and persistence behavior
The persisted model is a single DFS container with one superblock object, directory entry objects, symlink data, and four file data objects. Counts represent repeated VOS records for replicated data: metadata dkeys for file inodes are tripled, and array dkey counts scale to three copies.

## Dependencies and integration points
It integrates with storage-estimator test cases that compare an explored/generated filesystem model against static YAML for `RP_3GX`. It relies on `check_key_type` accepting `hashed` and `integer`, and on estimator checksum defaults (`csum_size: 0`, `csum_gran: 16384`).

## Risks and edge cases
The fixture can silently become stale if the replication/object-class accounting changes. It also depends on exact UTF-8 byte lengths in `size` fields for file names and DFS keys. Because replicated count changes are local to selected integer dkeys, tests should compare structure, not only total bytes, when debugging failures.

## Test signals
Expected signals include parseability, stable metadata/user/NVMe totals for a three-way replicated layout, and larger data dkey counts than the SX fixture while preserving identical directory and DFS superblock sections.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_3gx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_16p2gx.yaml -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_16p2gx.yaml

## Purpose
Aggregated large-filesystem fixture for the storage estimator using `EC_16P2GX`. Instead of enumerating each directory and file, it summarizes a large DFS population into object buckets for directories, symlinks, and representative file-size classes.

## Important APIs, types, and functions
- Header comments record source aggregate counts: total objects, total size, directory count, link count, and file buckets for 4 KiB, 256 KiB, 8 MiB, 500 GiB, and 10 TiB.
- `dir_obj` uses `count: 4931` and average dkeys for symlinks, subdirectories, and files per directory.
- Representative file objects (`4k_obj`, `256k_obj`, `8m_obj`, `500g_obj`, `10t_obj`) multiply by file count.
- EC-specific counts model full 1 MiB dkeys plus parity/remainder dkeys; large objects include comments showing EC count formulas for 500 GiB and 10 TiB.

## Control flow
The fixture is consumed as ordinary YAML. `MetaOverhead` multiplies each representative object by its `count`, then each dkey/akey/value by its local counts. The file buckets are therefore an averaged approximation of a huge filesystem, not an exact per-file listing.

## State and persistence behavior
No runtime state is stored. The model persists aggregate VOS shape: one superblock, many similar directory objects, and file data represented by repeated full-chunk dkeys plus remainder dkeys. `csum_size: 0` means checksum overhead is disabled in this fixture.

## Dependencies and integration points
This file supports tests of the estimator's `-x` average/massive-filesystem path and CSV-to-YAML logic. It depends on the same schema as the detailed fixtures and on object-class accounting used by `ProcessCSV`/DFS exploration when EC_16P2GX is selected.

## Risks and edge cases
The bucketed model hides variance inside each class; it is useful for totals but not for exact tree topology. Very large dkey counts stress dynamic tree-order calculations in `MetaOverhead.get_dynamic`; stale counts can produce large total differences. Object names beginning with digits are valid YAML anchors here but may be awkward for manual tools.

## Test signals
Expected signals are successful parse, stable aggregate totals, correct handling of millions of repeated dkeys, and EC totals that are larger than SX but not simply 3x like RP_3GX.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_16p2gx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_3gx.yaml -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_3gx.yaml

## Purpose
Aggregated large-filesystem fixture for `RP_3GX`, used to validate estimator behavior for three-way replicated data at scale. It shares the same bucketed filesystem summary as the big SX and EC fixtures.

## Important APIs, types, and functions
- Uses the standard estimator YAML hierarchy under `containers`.
- `file_dkey0` and every data/remainder dkey count are tripled compared with SX, reflecting three replicas.
- Directory object counts and superblock metadata are unchanged from other big fixtures.
- Representative objects encode file-size buckets rather than individual files.

## Control flow
The estimator reads this file and recursively applies counts. Replication is represented directly in YAML counts: for example full-data dkeys for 8 MiB, 500 GiB, and 10 TiB files are 3x the SX counts.

## State and persistence behavior
The file has no mutable state. It approximates VOS persistence for a large DFS namespace: one container, repeated directory objects, and repeated file data objects. Since data values are arrays with 128 KiB records, NVMe/SCM attribution depends on `scm_cutoff` during estimator execution.

## Dependencies and integration points
The fixture integrates with storage estimator tests that validate CSV/average generation for `RP_3GX`. It depends on the PyYAML anchor mechanism and on `vos_size.py` treating `overhead` and `value_type` fields consistently.

## Risks and edge cases
Large replicated counts can overflow assumptions in downstream code if totals are held in narrow types outside Python. The fixture’s aggregate nature means a change in average file-size bucketing or replication math requires coordinated updates across all big fixtures.

## Test signals
Signals include parseability, stable totals under `read_yaml`, and expected 3x-style expansion of file data dkey counts relative to the SX big fixture while namespace metadata remains comparable.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_3gx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_sx.yaml -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_sx.yaml

## Purpose
Baseline aggregated large-filesystem fixture for `SX` spreading. It provides the non-replicated, non-EC reference for the big filesystem model used by estimator tests.

## Important APIs, types, and functions
- Header comments define the source aggregate dataset and bucket counts.
- Directory population is represented through `dir_obj count: 4931` with average symlink, subdirectory, and file dkeys.
- File objects represent size classes and use full 1 MiB data dkeys plus remainder dkeys.
- `containers: [*posix]` is the only top-level executable input for `MetaOverhead`.

## Control flow
Loaded YAML is walked by the estimator. Counts multiply through the tree: container count, object count, dkey count, akey count, and value count. `SX` baseline counts encode logical data once, so other object-class fixtures can be compared against it.

## State and persistence behavior
The file encodes static aggregate VOS state: DFS superblock metadata, repeated directory inode records, symlink arrays, and representative file arrays. It disables checksums with `csum_size: 0`.

## Dependencies and integration points
It is a reference input for storage-estimator average mode and for validating `ProcessCSV`/filesystem exploration output. It depends on `MetaOverhead` dynamic tree sizing to scale metadata records for huge dkey counts.

## Risks and edge cases
Because this is the baseline, errors here propagate into expectations for replicated and EC comparisons. Counts are averages and ceilings, so they should not be used as proof of exact per-directory layout. Huge counts exercise estimator performance and integer arithmetic.

## Test signals
Expected signals are stable baseline totals, successful handling of large dkey counts, and lower data/storage totals than RP_3GX or EC_16P2GX variants.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_sx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_sx.yaml -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_sx.yaml

## Purpose
Baseline detailed DFS fixture for `SX` object class. It enumerates the small sample tree explicitly and is the reference for comparing RP_3GX and EC_16P2GX detailed fixtures.

## Important APIs, types, and functions
- Defines DFS superblock metadata akeys (`dfs_magic`, `dfs_sb_version`, `dfs_layout_version`, `dfs_chunk_size`, `dfs_obj_class`).
- Defines one `dfs_inode` array akey reused by directory entries.
- File objects use integer dkeys for metadata, full data chunks, and remainder chunks.
- `count` values reflect non-replicated SX logical layout.

## Control flow
The fixture is loaded by `read_yaml` and handed to `MetaOverhead`. It contains no behavior but drives estimator recursion exactly: one POSIX container, nine objects, and nested dkeys/akeys/values.

## State and persistence behavior
It models a single DFS namespace with explicit directory objects and regular-file data objects. Directory names and symlink target length contribute user/meta key sizes. Values larger than the SCM cutoff are counted toward NVMe by the estimator.

## Dependencies and integration points
This file anchors storage-estimator unit tests for filesystem exploration and YAML generation. It depends on exact key sizes, chunk size of 1 MiB, I/O size of 128 KiB, directory object class `S1`, and file object class `SX`.

## Risks and edge cases
The exact dkey counts are sensitive to chunking and remainder calculations. Symlink modeling has both inode-sized metadata and symlink target bytes in a single array akey. A typo or key-size mismatch can shift metadata totals without obvious YAML syntax errors.

## Test signals
Signals include successful parsing, stable estimator report totals for SX, and expected lower counts than replicated/EC fixtures for the same file tree.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_sx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/util.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/tests/util.py

## Purpose
Small filesystem fixture helper for storage-estimator tests. `FileGenerator` creates a temporary mock DFS-like directory tree containing directories, sparse files, and symlinks, then cleans it up.

## Important APIs, types, and functions
- `FileGenerator.__init__(prefix="")` creates a temp directory and sets `_mock_root` to `<tmp>/daos`.
- `get_root()` returns the mock root path.
- `crete_mock_fs(files)` prints the temp path and delegates to `_create_files`; the method name is misspelled but is likely part of local test API.
- `_create_files()` dispatches dictionaries with `type` equal to `dir`, `file`, or `symlink`.
- `generate_file()` creates parent directories and writes one byte at `size - 1`, producing sparse files.
- `clean()` and `__del__()` remove the mock root.

## Control flow
Tests instantiate `FileGenerator`, pass a list of file descriptors, and then run estimator exploration against `get_root()`. Each descriptor is handled independently. Files cause parent directory creation before sparse write; symlinks are created directly at target path.

## State and persistence behavior
State is limited to temporary filesystem contents under `_mock_root`. Generated files are sparse and store only one byte at the end, so apparent file size is controlled without allocating full data. Cleanup deletes the whole mock root; double cleanup can raise if `__del__` runs after manual `clean()` removed it.

## Dependencies and integration points
Depends on Python `tempfile`, `os`, and `shutil`. Integrates with `FileSystemExplorer` tests by providing realistic `os.walk`/stat/symlink targets.

## Risks and edge cases
`generate_file` with size 0 seeks to `-1`, which would fail. `_create_symlink` does not ensure parent directories exist, so callers must list directory creation before symlinks. `__del__` unconditionally calls `clean()`, so tests that call `clean()` manually may need to tolerate cleanup errors.

## Test signals
Signals are correct directory tree creation, sparse file sizes visible to stat, symlink presence and target string length, and cleanup after estimator tests.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/tests/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/util.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/util.py

## Purpose
Shared utility layer for the DAOS VOS storage estimator. It handles logging/formatting, object-class validation, metadata loading, CLI numeric parsing, checksum/chunk/scm-cutoff processing, conversion from DFS exploration to estimator YAML, and invoking `MetaOverhead`.

## Important APIs, types, and functions
- `CommonBase` provides verbose output, human-readable size parsing/formatting, positive integer checks, and suffix handling.
- `ObjectClass` validates supported object classes (`S1`, `SX`, `RP_3GX`, `EC_16P2GX`, etc.) and exposes target/stripe/parity/replica parameters.
- `Common` loads VOS metadata from `VOS_SIZE`, reads/writes YAML, and runs `_process_yaml`.
- `ProcessBase` combines `Common` with object-class and DFS/CSV processing: block sizes, checksum selection, shard validation, aggregation assumptions, and `Containers` construction.
- Integration objects include `MetaOverhead`, `get_dfs_sb_obj`, and `VOS_SIZE`.

## Control flow
CLI command classes inherit `Common` or `ProcessBase`. Construction loads VOS metadata, parses object class and sizing options, validates EC constraints, applies optional metadata override, then later `run()` either loads user YAML or converts an explored/CSV model to YAML. `_process_yaml` instantiates `MetaOverhead`, loads every container, and prints a report.

## State and persistence behavior
Instances hold parsed args, verbosity, VOS metadata YAML, object-class state, checksum size, SCM cutoff, I/O size, chunk size, EC cell size, and shard count. `_create_file` persists generated YAML/metadata files. The estimator itself is read-only except for optional output files.

## Dependencies and integration points
Depends on PyYAML, `storage_estimator.dfs_sb`, `storage_estimator.vos_size`, `storage_estimator.vos_structures`, and generated VOS metadata from a DAOS storage path. It is the common integration point for `daos_storage_estimator.py`, filesystem exploration, CSV processing, and direct YAML reads.

## Risks and edge cases
`_from_human` accepts loose suffixes by stripping suffix letters, which can parse surprising strings. `ObjectClass._update_oclass` ignores its `default_value` parameter and requires the arg value to already be supported. EC validation is strict about chunk/stripe/cell divisibility. `_load_yaml_from_file` opens without an explicit context manager. Some checks use `'average' in self._args`, which is not normal for `argparse.Namespace` unless customized elsewhere.

## Test signals
Signals include correct parsing of human sizes, rejection of invalid object classes/shard counts/EC arguments/checksum names, successful YAML loading and report printing, and stable generated YAML for filesystem or CSV inputs.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/vos_size.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/vos_size.py

## Purpose
Core VOS metadata overhead calculator. It converts estimator YAML into per-pool tree structures and accumulates metadata, user metadata, user values, SCM, and NVMe totals using VOS metadata-size definitions.

## Important APIs, types, and functions
- `convert()` and `print_total()` format byte counts.
- `check_key_type()` validates hashed/integer key specs and requires `size` for hashed keys.
- `Stats` stores counters for pool, container, object, dkey, akey, arrays, single values, user bytes, and physical totals.
- `MetaOverhead` builds internal pool/container/object/dkey/akey/value trees and calculates overhead with `init_container`, `init_object`, `init_dkeys`, `init_akey`, `init_value`, `calc_tree`, and `print_report`.

## Control flow
`MetaOverhead` starts with one logical tree per pool. Loading a container appends a container tree to every pool, then each object distributes dkeys across selected targets. Values update akey value/meta/NVMe counters. Reporting adds fixed pool/container roots, recursively computes B-tree overhead based on metadata YAML tree orders, applies duplication counts, and prints a breakdown.

## State and persistence behavior
State is in-memory only: pool trees, next object/container ids, SCM cutoff, checksum size, and accumulated stats. Values above `_scm_cutoff` contribute to `nvme_size`; value bytes still count in logical `total`. Checksum overhead is added per value, with arrays scaled by `ceil(size / csum_gran)`.

## Dependencies and integration points
Consumes metadata from `VOS_SIZE.get_vos_size_str()` or a user-supplied metadata YAML. Used by `Common._process_yaml` for all estimator modes. It depends on tree metadata fields such as `record_msize`, `order`, `leaf_node_size`, `int_node_size`, `num_dynamic`, and `dynamic`.

## Risks and edge cases
Dkey distribution uses `random.randint`, so per-pool layout can be nondeterministic, though aggregate totals should usually remain stable. `get_dynamic` raises a string on impossible state, which is invalid in modern Python. `Stats.merge` assumes every key exists in the child. Dynamic tree sizing is approximate for large counts and assumes 50 percent capacity when values exceed order.

## Test signals
Signals include validation errors for malformed YAML, stable aggregate totals for fixtures, correct SCM/NVMe split around cutoff, checksum overhead scaling, and sensible metadata growth as dkey/akey/value counts increase.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/vos_size.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/vos_structures.py -->
# sources/object-store/daos/src/vos/storage_estimator/common/vos_structures.py

## Purpose
Object-builder classes for constructing valid storage-estimator YAML payloads in Python. They enforce a typed hierarchy of containers, objects, dkeys, akeys, and values.

## Important APIs, types, and functions
- Enums: `KeyType`, `Overhead`, `ValType`, and `StrBool`.
- `VosBase` stores `_payload`, validates integer `count`, and converts enum values.
- `VosValue` requires integer `size` and optional `aligned`.
- `VosItems` handles lists of child values and raises `VosValueError` when empty.
- `VosKey`, `AKey`, `DKey`, `VosObject`, and `Container` model estimator YAML nodes.

## Control flow
Constructors populate `_payload` dictionaries immediately. Higher-level nodes call `_add_values` to validate and dump child objects. `dump()` returns the underlying nested dictionaries only after non-empty child lists are verified.

## State and persistence behavior
State is transient Python dictionaries that can be serialized as YAML by callers. Hashed keys derive `size` from UTF-8 byte length when a key string is supplied; integer keys omit size. Defaults mark key overhead as user, values as aligned, and object/container counts as one.

## Dependencies and integration points
Used by DFS and CSV conversion code to generate YAML accepted by `MetaOverhead`. It integrates with `util.ProcessBase._get_yaml_from_dfs`, which creates `Containers`, adds DFS superblock/container data, sets checksum fields, and dumps the resulting payload.

## Risks and edge cases
Several constructors use mutable default arguments (`values=[]`, `akeys=[]`, `dkeys=[]`, `objects=[]`), which is normally risky even though the code only iterates over them. `_set_aligned` uses identity checks against strings, which can be unreliable. `_check_value_type` formats `type(self._values_type)` instead of the class itself, producing less useful error text.

## Test signals
Signals include exceptions on missing sizes/value types, rejected wrong child types, non-empty child enforcement, correct UTF-8 key-size calculation, and generated dictionaries matching fixture YAML schema.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/common/vos_structures.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/daos_storage_estimator.py -->
# sources/object-store/daos/src/vos/storage_estimator/daos_storage_estimator.py

## Purpose
Command-line entry point for the DAOS storage estimator. It exposes subcommands to create sample metadata/YAML, estimate from a live filesystem tree, estimate from existing YAML, or estimate from CSV.

## Important APIs, types, and functions
- `CreateExample.run()` writes VOS metadata and a DFS sample YAML.
- `ProcessFS.run()` explores a path with `FileSystemExplorer`, converts results to YAML, optionally writes it, and prints overhead.
- `ProcessYAML.run()` loads a user YAML file and processes it.
- `process_csv()` delegates to `ProcessCSV`.
- `argparse` subcommands: `create_example`, `explore_fs`, `read_yaml`, and `read_csv`.

## Control flow
The module creates an argparse parser at import/execution time, configures subcommands, parses args, and calls `args.func(args)`. Each wrapper prints the DAOS version, constructs the appropriate processor, runs it, catches exceptions, prints an error, and exits with `-1` on failure.

## State and persistence behavior
State is mostly CLI arguments and generated estimator objects. `create_example` and `explore_fs` can persist YAML/metadata output files. `read_yaml` and `read_csv` are read-only except optional output. The default DAOS storage path is `/mnt/daos`.

## Dependencies and integration points
Integrates `storage_estimator.dfs_sb`, `FileSystemExplorer`, `ProcessCSV`, and utility classes from `storage_estimator.util`. It is the user-facing bridge from DAOS/DFS filesystem observations or CSV summaries to `MetaOverhead`.

## Risks and edge cases
The module assumes a subcommand is provided; otherwise `args.func` is absent. `ProcessFS.run()` and `ProcessYAML.run()` reference the global `args` rather than `self._args`, making reuse harder and tests more coupled to module state. All failures collapse to process exit `-1`, which limits programmatic error handling.

## Test signals
Signals include correct help/subcommand parsing, sample file creation, expected rejection of invalid object classes/EC sizing/checksum names, and stable printed estimates from YAML/CSV/filesystem inputs.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/storage_estimator/daos_storage_estimator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/sys_db.c -->
# sources/object-store/daos/src/vos/sys_db.c

## Purpose
Implements the VOS-backed system database used by DAOS server metadata. It stores key/value tables inside a reserved VOS pool/container and exports the generic `struct sys_db` interface.

## Important APIs, types, and functions
- Reserved UUIDs `SYS_DB_POOL` and `SYS_DB_CONT`, directory `daos_sys`, and file name `sys_db`.
- `struct vos_sys_db` wraps public `struct sys_db` with paths, handles, mutex, UUIDs, object id, and umem instance.
- Public functions: `vos_db_init`, `vos_db_init_ex`, `vos_db_fini`, `vos_db_get`, `vos_db_pool_uuid`.
- Interface methods: `db_fetch`, `db_upsert`, `db_delete`, `db_traverse`, `db_tx_begin`, `db_tx_end`, `db_lock`, `db_unlock`.

## Control flow
Initialization builds the sysdb directory/file paths, creates a recursive Argobots mutex, installs method pointers, parses reserved UUIDs, optionally unlinks existing storage, then tries open-first/create-second unless forced. `db_open_create` creates or opens the VOS pool, creates/opens the container, initializes `db_umm`, and writes or validates the metadata version. CRUD methods map table names to dkeys and user keys to akeys in a fixed VOS object at epoch 1.

## State and persistence behavior
Persistent state lives in a 128 MiB VOS pool file under `<db_path>/daos_sys/<db_name>`. Table names are dkeys; keys are akeys; values are single-value IODs. Version metadata is stored in table `metadata`, key `version`. Deletion calls `vos_gc_pool_tight` because `vos_obj_del_key` alone does not free space. `destroy_db_on_fini` controls whether finalization destroys the pool file.

## Dependencies and integration points
Depends on VOS pool/container/object APIs, sys_db headers, UUID parsing, umem transactions, Argobots mutexes, and DAOS error/logging helpers. It is the backing store for DAOS system metadata consumers that call the generic `sys_db` callbacks.

## Risks and edge cases
Failure paths must close partially opened handles and free allocated paths/mutex attributes. Version incompatibility returns `-DER_DF_INCOMPT`. `db_fetch` treats zero-length returned values as nonexistence. Force-create unlinks the file before open/create, so callers must be explicit. The global singleton means concurrent init/fini must be externally controlled.

## Test signals
Signals include create/open idempotence, version read/write and incompatibility handling, correct fetch/upsert/delete/traverse behavior, transaction nesting over umem, mutex recursion, and cleanup with or without pool destruction.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/sys_db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/bio_ut.c -->
# sources/object-store/daos/src/vos/tests/bio_ut.c

## Purpose
Standalone entry point for BIO/WAL unit tests. It initializes DAOS debug and a self-contained VOS instance, then runs WAL tests.

## Important APIs, types, and functions
- Global `ut_args` holds BIO unit-test context and seed.
- `ut_init()` calls `daos_debug_init`, `vos_self_init`, and stores `vos_xsctxt_get()`.
- `ut_fini()` calls `vos_self_fini` and `daos_debug_fini`.
- `main()` parses `--db_path`, `--seed`, and `--help`, then calls `run_wal_tests()`.

## Control flow
The program registers cmocka-style alternative assertions, chooses a random seed from time unless supplied, defaults `db_path` to `/mnt/daos`, prints the seed, and runs all WAL tests. `ut_init`/`ut_fini` are exported for test suites rather than called directly by `main`.

## State and persistence behavior
State includes the configured DB/storage path, random seed, and VOS xstream context. Persistent effects are whatever WAL tests create under the selected path through VOS/BIO.

## Dependencies and integration points
Depends on `bio_ut.h`, VOS TLS, DAOS debug, `vos_self_init`, and the WAL test implementation (`run_wal_tests`). It is a narrower binary than the full `vos_tests` launcher.

## Risks and edge cases
`db_path` is a fixed 100-byte buffer; long input is truncated. The main path does not call `ut_init` itself, so WAL tests must manage fixture initialization through exported helpers. Defaulting to `/mnt/daos` requires an appropriate test environment.

## Test signals
Signals are successful option parsing, printed seed reproducibility, successful VOS initialization in WAL fixtures, and `run_wal_tests()` return code.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/bio_ut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/bio_ut.h -->
# sources/object-store/daos/src/vos/tests/bio_ut.h

## Purpose
Shared header for BIO/WAL unit tests. It defines common includes, fault-injection skip behavior, and the test argument structure exported by `bio_ut.c`.

## Important APIs, types, and functions
- `FAULT_INJECTION_REQUIRED()` either no-ops when built with fault injection or prints a skip message and calls `skip()`.
- `struct bio_ut_args` carries xstream BIO context, metadata context, pool UUID, and random seed.
- Exports `ut_args`, `ut_init`, `ut_fini`, and `run_wal_tests`.

## Control flow
The header provides macros and declarations only. Test files include it to access common initialization and conditional skipping.

## State and persistence behavior
It declares shared state but does not own persistence. The struct fields represent runtime BIO/VOS contexts and seed values.

## Dependencies and integration points
Includes cmocka, DAOS common/test libraries, sys_db, and server BIO headers. It is the glue between the BIO test launcher and WAL test implementation.

## Risks and edge cases
Tests requiring fault injection must use the macro or they may produce false failures in builds without fault injection. Consumers must ensure `ut_init`/`ut_fini` are paired and must not assume all struct fields are initialized by every test.

## Test signals
Signals are build-time availability of declarations, correct skip behavior without fault injection, and shared seed/context propagation into WAL tests.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/bio_ut.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/daos_nvme.conf -->
# sources/object-store/daos/src/vos/tests/daos_nvme.conf

## Purpose
SPDK JSON configuration for VOS tests needing a simple NVMe/bdev backend. It configures bdev options and creates one AIO block device backed by `/tmp/aio_file`.

## Important APIs, types, and functions
- Top-level `subsystems` entry for `bdev`.
- `bdev_set_options` sets I/O pool/cache sizes.
- `bdev_nvme_set_options` sets retry, timeout, admin queue polling, and timeout action.
- `bdev_nvme_set_hotplug` disables hotplug.
- `bdev_aio_create` creates `AIO_1` with 4096-byte block size and `/tmp/aio_file`.

## Control flow
This is declarative JSON consumed by SPDK/DAOS initialization. Methods are applied by the bdev subsystem in listed order.

## State and persistence behavior
The config can cause `/tmp/aio_file` to be used as backing storage for an AIO bdev. It stores no runtime state itself. Tests using it may create or mutate that file.

## Dependencies and integration points
Integrates DAOS/VOS NVMe test startup with SPDK bdev RPC/config machinery. The AIO backend allows tests to run without a physical NVMe device.

## Risks and edge cases
The hard-coded `/tmp/aio_file` can collide between tests or stale runs. Timeout and hotplug settings are test-oriented and not production defaults. Missing SPDK AIO support or insufficient permissions will break consumers.

## Test signals
Signals include successful SPDK config load, creation of `AIO_1`, and VOS tests observing an NVMe-capable backend.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/daos_nvme.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/evt_ctl.c -->
# sources/object-store/daos/src/vos/tests/evt_ctl.c

## Purpose
Command-line and cmocka test driver for the DAOS extent tree (`evtree`). It supports scripted tree operations, interactive command parsing, drain tests, sorting variants, and a substantial internal regression suite.

## Important APIs, types, and functions
- CLI helpers: `ts_open_create`, `ts_close_destroy`, `ts_add_rect`, `ts_delete_rect`, `ts_remove_rect`, `ts_find_rect`, `ts_list_rect`, `ts_many_add`, `ts_drain`, and `ts_cmd_run`.
- Parsing uses extent syntax like `lo-hi@epoch[.minor][-epr_hi][:value]`, with optional leading `-` for expected failure.
- Built-in tests cover iterator flags/deletion, find, variable data sizes, node order limits, aggregation checks, overlap splitting, root deactivate/allocation bugs, outer punch behavior, and dynamic root yield.
- Memory helpers allocate fake SCM addresses through `utest_alloc` and free via evtree descriptor callbacks.

## Control flow
`main` initializes logging, creates a PMEM-backed utest pool/root, then chooses interactive mode, internal tests (`-t`), or scripted command execution. Scripted execution maps getopt operations to `ts_cmd_run`, mutating a global tree handle. Internal tests use cmocka setup/teardown to create separate PMEM pools per test and then call evtree APIs directly.

## State and persistence behavior
Global state includes the utest context, umem attributes, evtree root, tree handle, selected feature flags, tree order, and command argv. Persistent test state is a PMEM file at `/mnt/daos/evtree-utest` for CLI mode and per-test `/mnt/daos/evtree-test-N` pools for internal tests. Inserted values are stored through fake BIO/SCM offsets and freed through callbacks unless the no-free callback is selected.

## Dependencies and integration points
Depends on `daos_srv/evtree.h`, BIO address helpers, `utest_common`, cmocka, command parser utilities, and DAOS logging/assertion helpers. Shell/Python wrappers invoke this binary for long scripted and stress patterns.

## Risks and edge cases
The parser is compact and permissive; malformed strings can produce confusing failures. Global CLI state makes operation ordering important. Some tests use random hole epochs and current time, so reproduction may require logs. Large data-size tests intentionally drive `-DER_NOSPACE`; environment pool size matters. Sorting feature selection is global and affects subsequent tree creation.

## Test signals
Signals include cmocka assertions, iterator-visible/covered/embedded ordering checks, find/delete result validation, memory increase/decrease tracking, expected aggregation return value `1`, node-order rejection, drain completion, and regression counts for historical allocation/root bugs.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/evt_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/evt_ctl.sh -->
# sources/object-store/daos/src/vos/tests/evt_ctl.sh

## Purpose
Shell harness that runs `evt_ctl` through a long deterministic scripted evtree workload, then runs built-in tests and drain tests. It also wraps the command with valgrind when requested.

## Important APIs, types, and functions
- Environment `USE_VALGRIND` selects memcheck or pmemcheck command prefixes.
- Sources `.build_vars.sh` to locate `$SL_PREFIX/bin/evt_ctl`.
- `word_set()` appends repeated add/find/delete/list patterns with overlapping extents and epochs.
- `check_max()` appends boundary-style max-extent checks.
- Final phases run scripted sequence, internal `-t` suite, and a drain command.

## Control flow
The script builds one long shell command string starting with `evt_ctl --start-test ... -C o:4`, appends loops of generated options, appends hand-written regression scenarios, executes it, checks status, then runs internal tests and drain tests similarly.

## State and persistence behavior
Runtime state is in the `cmd` shell variable and the PMEM/test files created by `evt_ctl`. The script itself persists no data, but valgrind memcheck may emit XML files named `unit-test-evt_ctl-%p.memcheck.xml`.

## Dependencies and integration points
Depends on bash, `.build_vars.sh`, the built `evt_ctl` binary, optional valgrind suppressions, and evt_ctl option grammar. It is a higher-level test entry used by DAOS test automation.

## Risks and edge cases
It uses `eval "$cmd"`, so command construction must remain controlled. Long command lines may hit shell/system limits if expanded further. `PIPESTATUS[0]` is used even though no explicit pipe is present; it still works in bash but is unusual. Paths depend on build variables being present.

## Test signals
Signals are nonzero exit on scripted workload failure, internal test failure, or drain failure; printed commands aid reproduction.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/evt_ctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/evt_stress.py -->
# sources/object-store/daos/src/vos/tests/evt_stress.py

## Purpose
Python stress wrapper for a specific `evt_ctl` pattern related to DAOS-11894. It generates hundreds of overlapping add operations to exercise evtree sort algorithms that previously segfaulted.

## Important APIs, types, and functions
- `EVTStress` parses `--algo` with choices `dist`, `dist_even`, and `soff`.
- Constructor walks upward from the script directory to find `.build_vars.json` and loads build paths.
- `run_cmd()` constructs an `evt_ctl` command using `${PREFIX}/bin/evt_ctl`, optional `-s <algo>`, creates order 23 tree, adds extents for starts 1 through 706, then debugs/destroys.

## Control flow
The script loads build configuration, formats a command string, appends a deterministic sequence of `-a start-1024@start` operations, and executes it with `os.system`.

## State and persistence behavior
No Python-side persistent state beyond loaded build config. The invoked `evt_ctl` creates and destroys its test tree/pool. Process exit is not explicitly propagated from `os.system` by `run_cmd`.

## Dependencies and integration points
Depends on Python stdlib, `.build_vars.json`, and the built `evt_ctl` binary. It integrates with evtree sorting feature flags through `evt_ctl -s`.

## Risks and edge cases
`os.system` return code is ignored, so callers may need to inspect process status externally. Command is string-built rather than argument-vector-based. Missing `.build_vars.json` raises `FileNotFoundError`.

## Test signals
Primary signal is whether `evt_ctl` completes without segfault for each sorting algorithm; output command/test name identifies the algorithm.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/evt_stress.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/pool_scrubbing_tests.c -->
# sources/object-store/daos/src/vos/tests/pool_scrubbing_tests.c

## Purpose
Cmocka integration tests for VOS pool checksum scrubbing. They verify that the scrubber detects corrupted checksummed data, respects lazy/timed modes, handles concurrent aggregation/deletion, and triggers target drain when corruption exceeds threshold.

## Important APIs, types, and functions
- `ms_between_periods_tests()` validates scrub pacing helper math.
- `struct sts_context` owns a test VOS pool/container, scrub context, csummer, callbacks, sizes, and expected rc.
- Setup helpers create pool/container, initialize CRC16 csummer, write/fetch VOS data, corrupt payloads after checksum calculation, and configure `scrub_ctx`.
- Test cases cover single values, arrays with 1/2/4 recxs, multiple epochs/akeys/objects, overlapping extents, dkey/container deletion races, drain threshold, and lazy-mode transition.

## Control flow
Each test uses `sts_setup` to initialize VOS under `/mnt/daos/vos_scrubbing.pmem`, writes data via `vos_obj_update`, optionally corrupts the data buffer after checksum generation, calls `vos_scrub_pool`, then verifies later `vos_obj_fetch` either succeeds or returns `-DER_CSUM`/`-DER_NONEXIST`. Some tests inject yield/sleep callbacks that aggregate or punch data during scrubbing.

## State and persistence behavior
Persistent state is a temporary VOS pool file/container plus VOS object records containing checksum metadata. Corruption is persisted by writing payload bytes that no longer match the stored checksum. Scrub context tracks current pool/container/object/key/epoch traversal and corruption count. Teardown closes/destroys the pool and csummer.

## Dependencies and integration points
Depends on DAOS checksum APIs, VOS object update/fetch/punch/aggregate/scrub APIs, server scrub structures, cmocka, DAOS test utilities, and the self VOS instance initialized in `main`. It exercises real VOS storage rather than pure mocks, with callbacks standing in for pool/container lookup and target drain.

## Risks and edge cases
Tests are environment-sensitive because they use `/mnt/daos` and create a 1 GiB SCM file by default. Race-style tests rely on callback timing. Fetch immediately after a corrupted update is expected to succeed before scrubbing, so changing checksum verification timing would alter assumptions. Some duplicate test labels could make filtering ambiguous.

## Test signals
Signals include expected `-DER_CSUM`, `-DER_NONEXIST`, `-DER_SHUTDOWN`, drain callback count, no hang when lazy mode changes to timed, and successful fetches for uncorrupted/covered/current data.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/pool_scrubbing_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vos_cmd.c -->
# sources/object-store/daos/src/vos/tests/vos_cmd.c

## Purpose
Implements the `vos_tests -r` command mini-language for creating/opening VOS pools, writing and removing extents, punching dkeys, iterating data, aggregating, discarding, querying size, and running randomized stress operations.

## Important APIs, types, and functions
- `struct known_pool` tracks pool name/path/UUID and open pool/container handles.
- `struct cmd_info` stores parsed key, start, length, operation type, and status.
- Operations include `create_pool`, `open_pool`, `close_pool`, `write_key`, `punch_key`, `discard`, `aggregate`, `iterate`, `visible_iterate`, `print_size`, and `run_many_tests`.
- Argobots helpers `abit_start`, `handle_op`, and `ult_func` run operations in ULTs.

## Control flow
`run_vos_command` splits the command string into argv, parses long/short options into an array of `cmd_info`, starts Argobots, then runs a single cmocka test executing commands sequentially. Synchronous operations are joined immediately; randomized stress launches async ULTs for 30 seconds, periodically joins completed operations, and asserts every status is zero.

## State and persistence behavior
State includes global known pool list, current open pool, newest write epoch, operation share table, write buffer, and ULT lists. Pool files are created under `vos_path` with deterministic UUIDs derived from pool names. `--destroy_all` controls whether created/opened pool files are destroyed at cleanup.

## Dependencies and integration points
Depends on VOS object/pool/container/iterator APIs, Argobots, DAOS list/atomic/error helpers, `vts_io.h`, and the full `vos_tests.c` launcher. It exercises VOS API behavior through user-specified scenarios and randomized aggregation/yield interleavings.

## Risks and edge cases
The command splitter is whitespace-based and does not support quoting inside command values. `create_pool` preallocates 4 GiB files, which may be expensive or fail on constrained filesystems. Randomized tests are time-based and seed-logged but nondeterministic. Global `current_open` permits only one open pool/container at a time.

## Test signals
Signals include cmocka assertion success, zero VOS return codes, visible/covered iteration output, operation-count table for randomized runs, and cleanup of pool handles/files when requested.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vos_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vos_size_input.yaml -->
# sources/object-store/daos/src/vos/tests/vos_size_input.yaml

## Purpose
Human-readable sample input for the VOS storage-size estimator. It documents the YAML schema and provides a small nested example with containers, objects, dkeys, akeys, and values.

## Important APIs, types, and functions
- `num_shards: 30` sets VOS pool count.
- Example value anchors define extent and single-value records.
- Example akeys demonstrate array and single-value `value_type`, hashed/integer key types, and multiple values.
- Example dkey/object/container anchors demonstrate count multiplication and checksum settings.

## Control flow
No executable flow. The estimator reads this file through `read_yaml`, validates required fields, loads it into `MetaOverhead`, and prints totals.

## State and persistence behavior
Declarative only. It models 10 identical containers, each with 100 objects, each with 200 integer dkeys, and akeys/values multiplied by their counts. Container checksum size/granularity is set to 64 and 4096.

## Dependencies and integration points
It is sample documentation and an input fixture for `daos_storage_estimator.py read_yaml`. It depends on the schema enforced by `vos_size.py`.

## Risks and edge cases
Because it is both documentation and input, comments must stay aligned with code defaults. Counts multiply quickly, so small edits can have large output impact. It does not demonstrate every field, such as explicit `overhead` on each node.

## Test signals
Signals are successful parse and a plausible estimator breakdown that exercises array values, single values, checksum overhead, integer keys, and count multiplication.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vos_size_input.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vos_tests.c -->
# sources/object-store/daos/src/vos/tests/vos_tests.c

## Purpose
Main launcher for the broader VOS unit-test suite. It initializes a standalone VOS instance, parses command-line options, dispatches selected test groups, or runs all VOS tests by default.

## Important APIs, types, and functions
- `FOREACH_OTYPE` enumerates object types used by I/O tests.
- `print_usage()` documents test selectors and common filters.
- `run_all_tests(keys)` runs timestamp, MVCC, punch model, pool/container, discard, aggregation, GC, DTX, ilog, checksum, WAL, evtree, tree, mark, and I/O suites.
- `main()` handles options such as `--pool`, `--container`, `--io`, `--all`, `--run_vos_cmd`, `--storage`, `--filter`, `--exclude`, `--force_csum`, and `--force_no_zero_copy`.

## Control flow
The program initializes DAOS debug, first parses global options affecting storage/filter/feature flags, defaults `vos_path` to `/mnt/daos`, initializes VOS, then resets option parsing and dispatches selected tests. If no specific suite is selected, it runs all tests. Finally it optionally runs a `vos_cmd` command, reports failures, finalizes VOS and debug, and returns failure count.

## State and persistence behavior
Global test state includes `vos_path`, checksum/no-zero-copy flags, GC setting, and the VOS self instance. Test suites create their own pools/containers and may persist files under the configured storage path during execution.

## Dependencies and integration points
Depends on cmocka, VOS internals, `vts_common.h`, DAOS debug, and many suite entry points implemented elsewhere. It also integrates `run_vos_command` from `vos_cmd.c`.

## Risks and edge cases
The filter code uses a stack buffer sized from `sizeof(optarg)`, which is pointer-size rather than string length and can be too small. Option parsing happens twice, so new options must be handled consistently in both passes. `otype` is compared to array size but negative values are not explicitly rejected.

## Test signals
Signals are nonzero failure count, per-suite cmocka output, successful VOS initialization/finalization, and final success or error message.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vos_tests.c -->
