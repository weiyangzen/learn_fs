# subset-b-008381 Research

Grouped research for FoundationDB binding tester directory/tuple/script tests and C binding/API tester sources. Each section is source-tree aligned and intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory.py

## Purpose
`directory.py` defines `DirectoryTest`, a randomized bindingtester workload for the FoundationDB directory layer. It generates stack-machine instructions that exercise directory creation, opening, moving, removal, listing, subspace operations, directory partitions, database-level directory operations, and optional snapshot directory reads. The test is designed for cross-binding comparison: generated instructions run against each binding, then logged stack/directory/subspace outputs are compared.

## Important APIs, Types, And Functions
- `DirectoryTest(Test)` owns test subspaces: `stack_subspace`, `directory_log`, `subspace_log`, and `prefix_log`.
- `setup(args)` initializes `dir_index` and a `test_util.RandomGenerator` parameterized by max integer bits, API version, and enabled tuple types.
- `generate(args, thread_number)` is the core workload generator. It emits `InstructionSet` commands such as `NEW_TRANSACTION`, `DIRECTORY_CHANGE`, `DIRECTORY_CREATE`, `DIRECTORY_CREATE_OR_OPEN`, `DIRECTORY_MOVE`, `DIRECTORY_REMOVE`, `DIRECTORY_PACK_KEY`, `DIRECTORY_RANGE`, and `LOG_STACK`.
- `ensure_default_directory_subspace()` recreates and records the default directory subspace after destructive operations that may remove or move it.
- `generate_layer()` chooses directory layer bytes, including empty layer, `b"partition"`, `b"test_layer"`, or random bytes.
- `pre_run(db, args)` prepopulates several directories using Python's directory implementation to verify other bindings can interoperate with existing directory metadata.
- `get_result_specifications()` declares comparison rules over the stack, directory log, and subspace log, filtering common retry/conflict errors.
- Utility functions `generate_path()` and `generate_prefix()` produce intentionally small, collision-prone paths and prefixes, with special handling for partitions and single-threaded uniqueness.

## Control Flow
Generation starts by creating a transaction, bootstrapping standard directory layers through `directory_util.setup_directories()`, switching to the default directory, and predeclaring directories to be created in `pre_run`. For each random operation, the generator may switch the current directory index, computes the available operation set from the modeled directory state, chooses one operation, pushes arguments, appends an opcode, and updates the in-memory `DirectoryStateTreeNode` model. Some operations force blocking commits when single-threaded comparison would otherwise become nondeterministic due to high-contention prefix allocation. Finalization commits outstanding work, iterates every known directory entry to log directory/subspace metadata, logs the stack, and commits again.

## State And Persistence Behavior
The persistent database effects are directory-layer metadata, created/moved/removed directories, generated subspace keys, and log keys under the test subspace. The local state model is `self.dir_list`, `self.dir_index`, `self.root`, `self.prepopulated_dirs`, and the shared `DirectoryStateTreeNode` graph. Prefix allocation nondeterminism is mitigated by known-prefix tracking and by serial commits around selected database operations when `args.concurrency == 1`.

## Dependencies And Integration Points
This file depends on the Python `fdb` bindings, `bindingtester` base classes, `test_util`, `directory_util`, and `DirectoryStateTreeNode`. It integrates with the bindingtester stack interpreter through instruction names and with the comparison harness through `ResultSpecification`. It assumes directory layer semantics from `fdb.directory`.

## Risks And Edge Cases
The generated workload intentionally creates ambiguous outcomes: failed opens, moves of empty path, partition prefixes, unknown allocated prefixes, and default-directory fallback. The directory-state model is conservative, so false assumptions there could either skip useful operations or log entries that are not comparable. Duplicate prefix validation is disabled here because removed partitions can make later allocation collisions legitimate under this workload. API-version and concurrency constraints matter because older high-contention allocator behavior can be more deterministic-sensitive.

## Test Signals
Strong signals come from comparing the stack log, directory log, and subspace log across bindings, plus prepopulated directory compatibility. `global_error_filter=[1007,1009,1021]` tolerates expected transaction/retry errors. The disabled duplicate-prefix check documents a known limitation around partitions and removed directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_hca.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_hca.py

## Purpose
`directory_hca.py` defines `DirectoryHcaTest`, a bindingtester workload focused on the directory layer's high-contention allocator (HCA). It creates many directories concurrently and validates that allocated prefixes are unique and that the HCA's internal counters remain consistent.

## Important APIs, Types, And Functions
- `DirectoryHcaTest(Test)` uses `coordination` keys for barriers and `prefix_log` for allocated-prefix evidence.
- `setup(args)` configures a `RandomGenerator`, three transaction names (`tr0`..`tr2`), barrier numbering, and maximum directories per transaction. It rejects `args.concurrency > 8` for API versions before 300.
- `commit_transactions()` randomly commits named transactions, forcing commits for older API versions.
- `barrier()` uses database instructions `SET_DATABASE`, `CLEAR_DATABASE`, and `WAIT_EMPTY` to synchronize concurrent bindingtester threads around HCA pressure phases.
- `generate(args, thread_number)` creates the default directory setup, then loops until `args.num_ops` directory create operations have been emitted.
- `pre_run(tr, args)` seeds the first barrier keys when concurrency is enabled.
- `validate(db, args)` calls `directory_util.check_for_duplicate_prefixes()` and `directory_util.validate_hca_state()`.

## Control Flow
After bootstrapping a default directory, each loop iteration optionally enters a barrier, switches to a random named transaction, emits one or more `DIRECTORY_CREATE` operations with random Unicode one-component paths and no explicit prefix, records allocated prefixes, optionally enters a second barrier, and lets thread zero commit transactions. Barriers arrange overlapping allocator pressure across worker threads while preserving enough ordering to know when all participants have reached a phase.

## State And Persistence Behavior
Persistent state includes created directories, prefix-log records, and coordination keys. Local state includes `transactions`, `barrier_num`, and `num_dirs`. The HCA state under the directory layer is not modified directly but is inspected in validation through its counters and recent allocation subspaces.

## Dependencies And Integration Points
This test depends on `directory_util.setup_directories()` and `push_instruction_and_record_prefix()` for directory setup and prefix logging. It relies on instruction semantics for named transactions and database-level waits, and uses `fdb.transactional` for pre-run coordination initialization.

## Risks And Edge Cases
The test is highly concurrency-sensitive. If barriers are misordered or named transactions are not isolated by a binding implementation, prefix collisions may be misattributed. Older API versions reduce the per-transaction directory count to avoid known HCA/concurrency limits. Thread zero receives a special one-directory path under concurrency to keep global progress/commit behavior controlled.

## Test Signals
The primary signals are absence of duplicate non-default prefixes in `prefix_log` and `validate_hca_state()` confirming the current HCA window's actual recent allocation count does not exceed its reported counter. Barrier completion also indirectly tests database wait/empty semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_hca.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_state_tree.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_state_tree.py

## Purpose
`directory_state_tree.py` implements a conservative in-memory model of possible directory state for bindingtester directory workloads. It lets the random generator reason about whether a directory entry is probably a directory, subspace, partition, deleted, or has a known prefix after operations whose success may be uncertain.

## Important APIs, Types, And Functions
- `TreeNodeState` stores shared mutable state for one logical directory identity: `dir_id`, booleans for directory/subspace/known-prefix/root/partition, parent node aliases, child map, and deletion flag.
- `DirectoryStateTreeNode` wraps `TreeNodeState` and can share state across multiple node wrappers after merges.
- Class state `layers` caches root directory-layer nodes by prefix; `default_directory` models fallback behavior; `dir_id` produces debug identifiers.
- `reset()`, `set_default_directory()`, and `get_layer()` manage global model state for a test run.
- `get_descendent()`, `add_child()`, `_merge()`, and `delete()` are the main state-transition APIs.
- `run_test()` is a standalone assertion-heavy regression test for merges, default-directory interactions, moves, and child propagation.

## Control Flow
Lookups recurse through `_get_descendent()`, merging the current node with the default-directory branch when relevant. Adds first route through `default_directory._add_child_impl()` when a default exists, then add into the current node, merging if the path is empty or creating intermediate directory/subspace nodes as needed. `_merge()` collapses two possible states by taking conservative conjunction for positive capabilities (`is_directory`, `is_subspace`, `has_known_prefix`), disjunction for deletion and partition flags, reassigning all parent wrappers to the same state object, and recursively merging child names.

## State And Persistence Behavior
This module has no database persistence. Its state is process-local and reset at test setup. Shared `TreeNodeState` objects allow aliases caused by moves or uncertain operations to stay synchronized. Deletion is recursive and sticky once observed.

## Dependencies And Integration Points
The directory tests use this model to decide which instruction families are safe to emit and which directory/subspace entries should be logged. It has no FoundationDB imports; integration is purely through Python object state.

## Risks And Edge Cases
The model deliberately sacrifices precision for comparability. Once two possible states merge, capabilities are downgraded when either branch lacks them, which may reduce operation coverage. Incorrect default-directory merging would cause directory tests to choose invalid operations or skip valid ones. `_merge()` contains a suspicious assignment to `self.dir_id` even though the wrapper usually reads `self.state.dir_id`; behavior still depends on `state.dir_id`.

## Test Signals
`run_test()` exercises representative default merge cases, child state merges, prefix-known downgrades, subspace downgrades, moves, and root validation. Bindingtester directory workloads provide higher-level integration coverage by depending on this model during random generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_state_tree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_util.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_util.py

## Purpose
`directory_util.py` provides shared helpers for bindingtester directory workloads: initial directory-layer setup, default-directory creation, prefix logging, duplicate-prefix validation, and high-contention allocator validation.

## Important APIs, Types, And Functions
- Constants: `DEFAULT_DIRECTORY_INDEX = 4`, `DEFAULT_DIRECTORY_PREFIX = b"default"`, and `DIRECTORY_ERROR_STRING = b"DIRECTORY_ERROR"`.
- `setup_directories(instructions, default_path, random)` resets `DirectoryStateTreeNode`, creates root subspaces/layers through instructions, creates a default directory subspace, sets the bindingtester error directory index, and returns the initial directory list.
- `create_default_directory_subspace()` forces a commit, switches to the generated layer, creates a database directory with a random `default-*` prefix, and restores directory index 4.
- `push_instruction_and_record_prefix()` emits a directory create/open instruction and records a packed key under the prefix log so later validation can detect duplicate allocations.
- `check_for_duplicate_prefixes(db, subspace)` scans recorded prefix keys in batches, filters default/error prefixes, and reports adjacent duplicate prefixes.
- `validate_hca_state(db)` inspects the directory layer's HCA counter/recent allocation subspaces and reports if actual recent allocations exceed the reported count.

## Control Flow
Setup creates two subspaces, wraps them into a directory layer, creates a default directory, and records that default in the state tree. Prefix recording optionally checks directory existence first, runs the target directory operation, switches to the new directory entry, packs a random key inside it, reorders stack values so existence and packed key become part of the tuple key, writes to the prefix log, and switches back to the default directory index.

## State And Persistence Behavior
The helper persists directory metadata, the default test directory, and prefix-log keys. Its validation functions read persistent test artifacts and internal HCA keys. Local state is mostly the returned `dir_list` plus the class-level `DirectoryStateTreeNode` model.

## Dependencies And Integration Points
This module depends on `fdb`, `struct`, bindingtester `util`, `test_util`, and `DirectoryStateTreeNode`. It is used by both `DirectoryTest` and `DirectoryHcaTest`, and its instruction names must match the bindingtester interpreter.

## Risks And Edge Cases
Duplicate detection assumes prefix-log keys sort by packed prefix and only compares adjacent prefixes across paged scans, so correct `last_prefix` handling is important. Prefixes with `DEFAULT_DIRECTORY_PREFIX` and `DIRECTORY_ERROR_STRING` are intentionally ignored. `validate_hca_state()` assumes current HCA layout under `fdb.Subspace((b"\xfe", b"hca"), b"\xfe")`; a directory-layer metadata layout change would require updates.

## Test Signals
Duplicate-prefix reports and HCA counter consistency are direct validation signals. The helpers also contribute setup correctness to every directory bindingtester workload.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/scripted.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/tests/scripted.py

## Purpose
`scripted.py` defines `ScriptedTest`, a fixed bindingtester scenario that exercises a broad cross-section of the stack-machine API: transaction lifecycle, reads/writes, range reads, key selectors, database-level operations, tuple packing/unpacking/ranges, atomic operations, versionstamps, unit tests, and optional thread instructions.

## Important APIs, Types, And Functions
- `ScriptedTest(Test)` uses `workspace` for data and `results_subspace` for expected result comparison.
- `setup(args)` forbids concurrency above 1 and bisection because the generated script is fixed and not designed for partial operation counts.
- `generate(args, thread_number)` creates a `ThreadedInstructionSet`, emits the long deterministic instruction script, and records expected results.
- `get_result_specifications()` compares result keys under `results_subspace`, filtering common retry/conflict errors.
- `get_expected_results()` returns the expected `Result` objects accumulated by `add_result()`.
- `append_range_test()` bulk-loads random key/value pairs and verifies range APIs across normal, starts-with, and selector variants.
- `add_result()` writes one result key with `SET_DATABASE`, appends the expected `Result`, then pops the live result value off the stack.

## Control Flow
The script begins with `ON_ERROR`, read-version, set/get/commit/reset scenarios; proceeds through snapshot and database reads, range clears, key selector queries, range-starts-with variants, tuple operations, integer arithmetic, tuple range boundaries, versionstamped key/value atomic operations, and `UNIT_TESTS`. If threads are enabled, it creates two thread specs, coordinates through wait keys, mutates a shared key, and accepts either thread's final value as expected.

## State And Persistence Behavior
The test persists workspace keys and result keys. Results are deterministic except for sections with accepted alternatives such as thread race outcomes. Versionstamp tests persist keys/values whose final location/content is only known after commit. Range tests clear and repopulate the workspace to avoid contamination from previous phases.

## Dependencies And Integration Points
It depends on `ThreadedInstructionSet`, `Result`, `ResultSpecification`, `test_util`, and the Python `fdb.tuple` implementation for expected packed values/ranges. It is one of the strongest compatibility contracts for bindingtester instruction semantics across languages.

## Risks And Edge Cases
Because the script is monolithic, small instruction semantic changes can affect many later expectations. It cannot be bisected by current harness assumptions. Versionstamp operations are API-version-sensitive (`SET_VERSIONSTAMPED_VALUE` with explicit index is gated at API >= 520). Threaded section intentionally has nondeterministic final value and must list both acceptable outputs.

## Test Signals
Expected results under `results_subspace` are precise behavioral assertions. The test covers error strings, empty results, range ordering/reversal, exact-mode invalid range limits, tuple encoding, versionstamp commit errors, and cross-thread database waits.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/scripted.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/test_util.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/tests/test_util.py

## Purpose
`test_util.py` provides random data generation and stack-instruction helpers for bindingtester workloads. It centralizes generation of tuple-compatible values, random range/key-selector parameters, error tuple encoding, blocking commit instruction sequences, stack reordering, and length-prefixed argument lists.

## Important APIs, Types, And Functions
- `RandomGenerator` is configured by `max_int_bits`, `api_version`, and enabled type names.
- `random_int()`, `random_float()`, `random_tuple()`, `random_tuple_list()`, `random_range_params()`, `random_selector_params()`, `random_string()`, and `random_unicode_char()` generate edge-heavy data.
- `error_string(error_code)` encodes `(b"ERROR", b"<code>")` using `fdb.tuple.pack`.
- `blocking_commit(instructions)` emits `COMMIT`, `WAIT_FUTURE`, and `RESET`.
- `to_front(instructions, index)` recursively emits `SWAP` instructions to bring a stack entry to the front.
- `with_length(tup)` produces `(len(tup),) + tup` for stack-machine instructions that take counted argument lists.

## Control Flow
Random tuple generation selects enabled type names and recursively creates nested tuples, versionstamps, UUIDs, booleans with API-version compatibility, bytes, Unicode strings, and floats. Range/selectors bias toward common values while still sampling large limits and unusual offsets. Helper functions emit stack-machine operations but do not execute database calls directly.

## State And Persistence Behavior
This module has no persistent state. `RandomGenerator` holds only configuration; all data generation uses the process-global `random` module. Outputs become persistent only when caller workloads write generated keys/values to FoundationDB.

## Dependencies And Integration Points
It depends on `fdb`, `fdb.tuple`, `COMMON_TYPES`, Python `uuid`, `unicodedata`, `ctypes`, and `math`. It is used across bindingtester tests, especially tuple, directory, and scripted workloads.

## Risks And Edge Cases
Generated floats include NaN, infinities, negative zero, and wide exponent values, which can expose binding-specific encoding differences. Unicode generation includes multi-codepoint and private-use cases. `to_front()` emits multiple swaps recursively, so stack depth assumptions must match the interpreter. API-version handling for bool and versionstamp affects expected cross-version compatibility.

## Test Signals
The helper itself is not a test, but it creates high-value edge coverage for tuple encoding, range parameters, and stack behavior. `blocking_commit()` makes transaction boundaries explicit and repeatable in higher-level tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/test_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/tuple.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/tests/tuple.py

## Purpose
`tuple.py` defines `TupleTest`, a focused bindingtester workload for FoundationDB tuple integer encoding boundaries. It writes packed integer tuples for values around powers of two and compares resulting keys/values across bindings.

## Important APIs, Types, And Functions
- `TupleTest(Test)` owns a persistent `workspace` subspace for packed integer results and a `stack_subspace` for final stack logging.
- `setup(args)` records `max_int_bits` and `api_version`.
- `generate(args, thread_number)` iterates signs, bit positions, and offsets around powers of two, packs each value with `TUPLE_PACK`, stores it under a descriptive workspace key, commits periodically, logs the stack, and returns instructions.
- `get_result_specifications()` compares workspace contents and stack log, filtering common retry/conflict errors.

## Control Flow
Generation starts one transaction, computes min/max values from `max_int_bits`, and for every valid `sign * 2**i + offset` where offset is -10 through 10, it pushes a one-element tuple, packs it, pushes a label key, and stores. Every 5000 mutations it commits and resets to avoid oversized transactions. Finalization commits, logs stack, and commits again.

## State And Persistence Behavior
Persistent state is the workspace key/value set containing labels mapped to encoded tuple bytes, plus a stack log. The test intentionally uses deterministic labels so repeated runs with the same settings compare the same integer boundary cases.

## Dependencies And Integration Points
It depends on `fdb.tuple`, `InstructionSet`, `ResultSpecification`, and `test_util.blocking_commit()`. It integrates with bindingtester result comparison by exposing workspace and stack subspaces.

## Risks And Edge Cases
Coverage is intentionally integer-specific; other tuple types are tested elsewhere. Transaction size is controlled by periodic commits, but very high `max_int_bits` still expands operation count. Labels are strings packed into the workspace subspace, while values are binary tuple encodings, so both key and value encoding paths are exercised.

## Test Signals
Cross-binding equality of workspace contents is the direct signal for integer tuple packing compatibility near length/sign boundary transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/tuple.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/util.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/util.py

## Purpose
`bindingtester/util.py` contains small process-level utilities for the bindingtester: logger configuration/access, signal name lookup, dynamic import of test subclasses, and conversion of an `fdb.Subspace` raw key back to a tuple.

## Important APIs, Types, And Functions
- `initialize_logger_level(logging_level)` maps string levels `DEBUG`, `INFO`, `WARNING`, and `ERROR` to Python logging constants and applies them to the bindingtester logger.
- `get_logger()` returns `logging.getLogger("foundationdb.bindingtester")`.
- `signal_number_to_name(signal_num)` scans the `signal` module for matching signal constants and returns the sole name or the numeric string.
- `import_subclasses(filename, module_path)` imports all sibling `.py` modules except `__init__.py`.
- `subspace_to_tuple(subspace)` unpacks `subspace.key()` with `fdb.tuple.unpack()` and raises a bindingtester-specific error if the prefix is not tuple-encoded.

## Control Flow
Most functions are direct helpers. `import_subclasses()` computes a directory from `filename`, iterates Python files with `glob`, derives module names, and imports them for side-effect class registration. `subspace_to_tuple()` logs the original exception before raising a clearer limitation message.

## State And Persistence Behavior
There is no database persistence. Logger level changes persist process-wide. Importing subclasses mutates Python module/import state.

## Dependencies And Integration Points
It depends on Python `logging`, `signal`, `os`, `glob`, and `fdb`. Directory tests use `subspace_to_tuple()` to build tuple-encoded prefix-log keys; harness startup can use `import_subclasses()` to discover tests.

## Risks And Edge Cases
`initialize_logger_level()` accepts only uppercase level names and raises `ValueError` otherwise. `signal_number_to_name()` can return a number if aliases match multiple constants. `subspace_to_tuple()` prevents tests from using raw prefixes that are not valid tuple encodings, which is an explicit bindingtester limitation.

## Test Signals
Indirect signals appear through test discovery, logging, and directory prefix logging. Failures in `subspace_to_tuple()` surface quickly when a workload tries to use unsupported subspace prefixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/CMakeLists.txt -->
# sources/storage-engines/foundationdb/bindings/c/CMakeLists.txt

## Purpose
This CMake file builds FoundationDB's C client binding (`fdb_c`), generated API-version trampolines, option/version headers, unit and API tests, shim library, external workload libraries, and install/package metadata. It is the integration hub for the C binding.

## Important APIs, Types, And Functions
- `FDB_C_SRCS` lists the core C API implementation and public/internal headers.
- A custom command runs `generate_asm.py` to produce `fdb_c.g.S`/`.asm` and `fdb_c_function_pointers.g.h`.
- `vexillographer_compile()` generates `foundationdb/fdb_c_options.g.h`.
- `configure_file()` generates `fdb_c_apiversion.g.h` from `fdb_c_apiversion.h.cmake` and `FDB_API_VERSION_FILE`.
- `fdb_c` is built as `SHARED` outside `OPEN_FOR_IDE`.
- Non-Windows test targets include unit tests, API tester, Mako/performance tools, C90 header compatibility test, unavailable-cluster tests, client config tests, and upgrade tests.
- Linux builds generate and test `fdb_c_shim` through `Implib.so`.
- Install rules export `FoundationDB-Client`, headers, pkg-config/cmake config, direct library, and Linux shim.

## Control Flow
Configuration chooses OS/CPU, generated assembly output, platform-specific linker options, and test target shapes. Build flow generates headers/assembly before compiling `fdb_c`, links against `fdbclient`, optionally constrains exported symbols, then builds tests and external workload libraries. Test registration loops over TOML API-test files and creates Python venv tests, with ASAN and architecture filters.

## State And Persistence Behavior
Generated build artifacts include assembly trampoline source, function pointer header, generated option/version headers, copied external client library, shim generated sources, and package configuration files. Installation persists libraries and headers under client package locations.

## Dependencies And Integration Points
It integrates with repository CMake helpers (`vexillographer_compile`, `add_fdbclient_test`, `add_python_venv_test`, `fdb_install`), `fdbclient`, `flow`, `toml11`, `fmt`, `boost`, `SimpleOpt`, doctest, Python, and platform linkers. It also drives the API tester files in this subset.

## Risks And Edge Cases
Generated trampoline correctness is architecture-sensitive. Linker options differ for Apple/Linux/Windows, UBSAN, Clang 19, and portable static-libstdc++ builds. The Linux shim is not built on Windows or Apple. API tester registration depends on TOML globbing and explicit skip patterns. Installation must keep generated headers aligned with compiled library API versions.

## Test Signals
Configured tests include setup/unit tests, external-client unit tests, disconnected timeout tests, C API TOML workload tests, upgrade tests, shim library tests, C90 header compilation, and client config tests. These are strong signals for ABI, API-version compatibility, dynamic loading, and behavior under upgrades.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/fdb_c.cpp -->
# sources/storage-engines/foundationdb/bindings/c/fdb_c.cpp

## Purpose
`fdb_c.cpp` implements FoundationDB's exported C API over the internal C++ `IClientApi`, `IDatabase`, `ITransaction`, and thread-safe future/result abstractions. It also handles API-version selection and compatibility dispatch for changed/removed functions.

## Important APIs, Types, And Functions
- Global `g_api_version` records the selected runtime API version.
- Cast macros map opaque C handles to internal types: `FDBFuture`/`FDBResult` to `ThreadSingleAssignmentVarBase`, `FDBDatabase` to `IDatabase`, `FDBTransaction` to `ITransaction`, and legacy `FDBCluster` to a stored cluster path.
- Error macros `RETURN_FUTURE_ON_ERROR`, `RETURN_RESULT_ON_ERROR`, `RETURN_ON_ERROR`, `CATCH_AND_RETURN`, and `CATCH_AND_DIE` convert C++ exceptions to C API error codes or error futures/results.
- Network/database functions include `fdb_network_set_option`, `fdb_setup_network_impl`, `fdb_run_network`, `fdb_stop_network`, `fdb_create_database`, and `fdb_create_database_from_connection_string`.
- Future/result functions expose cancellation, destruction, blocking, callbacks, error/value/key/range/string/key-array accessors, and synchronous `FDBResult` range access.
- Transaction functions implement read version, get/getKey/getRange/mapped range, set/clear/atomic/watch/commit, versionstamp, options, retry `on_error`, reset, conflict ranges, estimated size, and split points.
- `validate_and_update_parameters()` normalizes range limits, target bytes, streaming mode, iteration, and legacy reverse limit behavior.
- `fdb_select_api_version_impl()` enforces single selection, validates runtime/header versions, initializes platform/error state, and binds generated function pointers for compatibility variants.

## Control Flow
Most exported functions cast opaque handles, invoke the matching internal API method, and return either `fdb_error_t` or an extracted future pointer. API-version selection must happen once; after internal `selectApiVersion`, it applies `FDB_API_CHANGED` and `FDB_API_REMOVED` macros from newest to oldest so generated assembly trampolines dispatch each public symbol to the correct implementation for the selected header/runtime version.

## State And Persistence Behavior
Persistent database state is modified only through transaction/database operations. Process-local state includes `g_api_version`, generated function pointer globals, and the multi-version API singleton. Futures own result memory until the caller destroys/releases them. Database and transaction handles are reference-counted internal objects exposed as opaque pointers.

## Dependencies And Integration Points
This file depends on `fdbclient/FDBTypes.h`, `flow/ProtocolVersion.h`, multi-version transaction/client headers, `foundationdb/fdb_c.h`, `fdb_c_internal.h`, and generated `fdb_c_function_pointers.g.h`. It is compiled into `libfdb_c` and is the ABI consumed by all C bindings and many higher-level language bindings.

## Risks And Edge Cases
Memory lifetime is central: returned `uint8_t const*` arrays point into future/result-owned storage. Calling public API functions from removed-function implementations can accidentally resolve to a primary library under multi-version loading, which the file explicitly warns against. Range parameter compatibility for API <= 13, exact streaming with unlimited limits, iterator mode iteration bounds, tenant functions removed in 8.0 but still loaded by old Python bindings, and API selection after first call are all compatibility-sensitive. Several functions abort on unexpected deleted experimental tenant calls.

## Test Signals
Signals come from C unit tests, external-client tests, shim tests, C90 header tests, API tester workloads, binding tests, and upgrade tests configured by `CMakeLists.txt`. Static assertions check C/C++ layout compatibility for key-value and blob granule mutation enum values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/fdb_c.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/fdb_c_shim.cpp -->
# sources/storage-engines/foundationdb/bindings/c/fdb_c_shim.cpp

## Purpose
`fdb_c_shim.cpp` supplies the custom dynamic-loading callback and override API used by the Linux/Unix C shim library. The shim lets an application link to a stable shim while selecting the actual `libfdb_c` implementation at runtime.

## Important APIs, Types, And Functions
- `fdb_shim_set_local_client_library_path(const char* filePath)` stores a process-global override path.
- `fdb_shim_dlopen_callback(const char* libName)` chooses the library path from the explicit override, `FDB_LOCAL_CLIENT_LIBRARY_PATH`, or the generated import library's default name, then calls `dlopen(..., RTLD_LAZY | RTLD_GLOBAL)`.
- `FDB_LOCAL_CLIENT_LIBRARY_PATH_ENVVAR` names the environment override.

## Control Flow
At runtime, generated shim trampoline code calls `fdb_shim_dlopen_callback()` when it needs to load the real client library. The callback gives precedence to the setter, then environment variable, then original library name. Unsupported platforms hit a compile-time `#error`.

## State And Persistence Behavior
The only state is process-local `g_fdbLocalClientLibraryPath`; no database state is touched. The loaded shared object remains managed by the dynamic loader.

## Dependencies And Integration Points
It depends on `foundationdb/fdb_c_shim.h`, `<dlfcn.h>`, and `std::string`. CMake wires it into `fdb_c_shim` together with generated sources from `Implib.so`.

## Risks And Edge Cases
The setter writes a global string with no synchronization, so callers should configure it before concurrent API use. `dlopen` failures are returned as null and must be handled by generated shim/import-library code. `RTLD_GLOBAL` intentionally exposes symbols, which helps client loading but can create symbol-interposition concerns.

## Test Signals
`fdb_c_shim_tests.py`, shim unit tests, shim API tester, and `shim_lib_tester` exercise path selection and behavior against both current and alternate client libraries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/fdb_c_shim.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/CWorkload.h -->
# sources/storage-engines/foundationdb/bindings/c/foundationdb/CWorkload.h

## Purpose
`CWorkload.h` defines the pure-C external workload ABI for FoundationDB simulation/client testing. It mirrors the C++ workload API in `CppWorkload.h` using opaque pointers and virtual-table structs so workloads can be implemented in C.

## Important APIs, Types, And Functions
- `FDB_WORKLOAD_API_VERSION` identifies the ABI version.
- Opaque types include `OpaquePromise`, `OpaqueWorkload`, `OpaqueWorkloadContext`, and `OpaqueMetrics`.
- `FDBSeverity`, `FDBStringPair`, and `FDBMetric` model trace severity, detail key/values, and metric entries.
- `FDBString`, `FDBMetrics`, and `FDBPromise` wrap owned/borrowed C++ objects with function tables.
- `FDBWorkloadContext` exposes trace, process id, simulated time, random numbers, options, client identity, shared random seed, and delay future creation.
- `FDBWorkload` exposes workload lifecycle methods `setup`, `start`, `check`, `getMetrics`, and `getCheckTimeout`.
- `workloadCFactory(const char* name, FDBWorkloadContext context)` is the required entrypoint.

## Control Flow
The simulator loads a C workload shared library, calls `workloadCFactory()`, then drives setup/start/check stages sequentially. Each stage receives a promise and must resolve it asynchronously or free it. Workloads must not block; they should register callbacks around database futures and return.

## State And Persistence Behavior
The header defines ownership rules rather than state. Workload implementations own their `inner` workload pointer and must free it through the vtable. `FDBPromise` represents a pending simulation stage; leaking or not resolving it can hang the simulation. Database persistence occurs through `FDBDatabase` and C API functions invoked by implementations.

## Dependencies And Integration Points
It forward-declares C API `FDBFuture` and `FDBDatabase`, and is built/installed for external workloads. CMake builds a sample `c_workloads` shared library that includes this interface.

## Risks And Edge Cases
No function pointer in a returned workload may be null. Pointer arguments are mostly borrowed, so C workloads must not retain them beyond valid lifetimes unless documented. Blocking in callbacks or stages can stall simulation. ABI evolution must append to virtual tables to preserve compatibility.

## Test Signals
External workload libraries built in CMake provide compile/link coverage. Simulation/client workload tests validate lifecycle behavior when these interfaces are loaded.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/CWorkload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/CppWorkload.h -->
# sources/storage-engines/foundationdb/bindings/c/foundationdb/CppWorkload.h

## Purpose
`CppWorkload.h` defines the C++ external workload interface for FoundationDB client/simulation testing. It gives workload authors abstract classes for logging, context access, promises, workload lifecycle, metrics, and factories.

## Important APIs, Types, And Functions
- Forward declarations expose `FDBFuture`, `FDBResult`, `FDBDatabase`, and `FDBTransaction`.
- `FDBSeverity` enumerates trace severities.
- `FDBLogger::trace()` is the abstract logging hook.
- `FDBWorkloadContext` provides process identity, simulated time, randomness, typed option getters, client ids, shared random number, and delayed futures.
- `FDBPromise` and templated `GenericPromise<T>` wrap asynchronous stage completion.
- `FDBPerfMetric` describes metrics with name, value, averaged flag, and format.
- `FDBWorkload` declares `init`, `setup`, `start`, `check`, `getMetrics`, and default `getCheckTimeout()`.
- `FDBWorkloadFactory::create()` constructs workloads by name.

## Control Flow
External C++ workload libraries implement `FDBWorkloadFactory`, create workloads, initialize them with context, and resolve `GenericPromise<bool>` objects as each stage finishes. `getCheckTimeout()` defaults to 3000 simulated seconds unless overridden.

## State And Persistence Behavior
This header owns no state. Implementations manage workload state and database effects. `GenericPromise<T>` stores a shared `FDBPromise` and forwards `send()` by pointer to the value.

## Dependencies And Integration Points
It depends on the C++ standard library and the C API opaque types. CMake builds `cpp_workloads` from sample workload sources and links them against `fdb_c`.

## Risks And Edge Cases
ABI stability is a concern because this is a C++ virtual interface, not a C ABI. Implementations must respect asynchronous lifecycle expectations and avoid blocking. `GenericPromise::send()` passes an address of a local `T` to the underlying promise implementation, so the implementation must copy synchronously.

## Test Signals
Compile/link coverage comes from `cpp_workloads`; runtime signals come from simulation/client-testing workloads loaded through this interface.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/CppWorkload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c.h -->
# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c.h

## Purpose
`fdb_c.h` is the public FoundationDB C API header. It defines API-version selection macros, public structs and opaque handles, exported function declarations, compatibility gates for legacy APIs, key selector helper macros, and removed-function compile-time traps.

## Important APIs, Types, And Functions
- API macros require `FDB_API_VERSION` or `FDB_USE_LATEST_API_VERSION`/`FDB_USE_LATEST_BINDINGS_API_VERSION` and reject versions below 13 or above the generated latest version.
- `fdb_select_api_version(v)` and `fdb_select_api_version_capped(v)` wrap `fdb_select_api_version_impl`.
- Core structs include `FDBKey`, `FDBKeyValue`, `FDBKeySelector`, `FDBGetRangeReqAndResult`, `FDBMappedKeyValue`, `FDBKeyRange`, blob-granule compatibility structs, and `FDBTenant`.
- Future/result APIs include destroy/cancel/block/callback and typed result extractors.
- Database APIs include create/destroy/set option/create transaction, status/protocol/admin operations, and removed tenant stubs.
- Transaction APIs include get/getKey/getRange/mapped range, mutations, watch, commit, metrics/cost futures, versionstamp, on_error, reset, conflict ranges, estimated size, and split points.
- Legacy API blocks expose pre-610 cluster APIs, pre-23 future error APIs, and pre-14 transaction variants only when the selected API version allows them.

## Control Flow
This header controls compile-time visibility based on `FDB_API_VERSION`. Removed functions expand to an intentionally invalid macro so accidental calls fail at compile time. Runtime API selection still flows through `fdb_select_api_version_impl()` implemented in `fdb_c.cpp`.

## State And Persistence Behavior
The header documents pointer-lifetime and struct-layout contracts but owns no state. Returned pointers from future getters refer to future-owned memory. Transaction/database functions mutate FoundationDB state through the implementation library.

## Dependencies And Integration Points
It includes generated `fdb_c_apiversion.g.h`, generated `fdb_c_options.g.h`, and `fdb_c_types.h`. It is installed for external clients and is consumed by language bindings, C/C++ tests, and application code.

## Risks And Edge Cases
ABI layout is critical, especially packed `FDBKeyValue` and compatibility structures that mirror C++ internals. Some blob granule and tenant-related structs remain despite feature removal for compatibility. Consumers must select an API version exactly once before using the API. Compile-time API gates must stay synchronized with implementation-side function pointer changes.

## Test Signals
The C90 test verifies broad C compatibility. Unit/API/shim/upgrade tests exercise function declarations and runtime compatibility. Static assertions in `fdb_c.cpp` backstop selected layout assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_apiversion.h.cmake -->
# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_apiversion.h.cmake

## Purpose
`fdb_c_apiversion.h.cmake` is the template for generated `fdb_c_apiversion.g.h`. It publishes the latest C API version and specific option-introduction API versions to public headers.

## Important APIs, Types, And Functions
- `FDB_LATEST_API_VERSION` is substituted from `@FDB_AV_LATEST_VERSION@`.
- `FDB_LATEST_BINDINGS_API_VERSION` is substituted from `@FDB_AV_LATEST_BINDINGS_VERSION@`.
- `FDB_API_VERSION_CLIENT_TMP_DIR` and `FDB_API_VERSION_DISABLE_CLIENT_BYPASS` mark option introduction versions.

## Control Flow
CMake includes the repository API-version file, configures this template, and places the generated header under the build `foundationdb` include directory. `fdb_c.h` includes that generated file.

## State And Persistence Behavior
No runtime state exists. The generated header is a build artifact and installed header, so its values become part of the client compile-time contract.

## Dependencies And Integration Points
It depends on `CMakeLists.txt` providing the substitution variables through `FDB_API_VERSION_FILE`. It integrates directly with API-version validation in `fdb_c.h`.

## Risks And Edge Cases
If generated values lag or mismatch the compiled implementation, clients may compile with unsupported APIs or fail to access supported options. The template warns not to include the generated file directly, but consumers can still rely on macros through `fdb_c.h`.

## Test Signals
Build configuration and all C API compile tests indirectly validate this file. API-version selection tests catch mismatches between generated constants and implementation support.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_apiversion.h.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_internal.h -->
# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_internal.h

## Purpose
`fdb_c_internal.h` declares non-public C API hooks used internally by FoundationDB components for shared database state and future protocol-version testing.

## Important APIs, Types, And Functions
- Forward declaration `DatabaseSharedState`.
- `fdb_database_create_shared_state(FDBDatabase* db)` returns a future for database shared state.
- `fdb_database_set_shared_state(FDBDatabase* db, DatabaseSharedState* p)` installs shared state on a database.
- `fdb_future_get_shared_state(FDBFuture* f, DatabaseSharedState** outPtr)` extracts shared state from a future.
- `fdb_use_future_protocol_version()` switches the client API into future protocol-version mode.

## Control Flow
Callers include this header when they need internal-only hooks. Implementations in `fdb_c.cpp` cast the opaque database/future handles and call internal `IDatabase`/API methods.

## State And Persistence Behavior
The functions affect client process state and database shared state references, not user key/value persistence. `fdb_use_future_protocol_version()` affects protocol selection behavior in the client process.

## Dependencies And Integration Points
It includes `flow/ProtocolVersion.h` and `fdb_c_types.h`, and is passed to `symbolify.py` on Apple so internal exported `fdb_` symbols can be included when required.

## Risks And Edge Cases
These functions are not part of the public stable surface. Misuse can cross database/shared-state lifetimes or force unsupported protocol behavior. Error handling is thin in `fdb_database_set_shared_state()`, which swallows exceptions.

## Test Signals
Internal and upgrade tests using future protocol versions or shared database state provide coverage. Apple exported-symbol generation also validates declaration format.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_shim.h -->
# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_shim.h

## Purpose
`fdb_c_shim.h` declares the public shim-only API for overriding which local `libfdb_c` library the generated shim loads at runtime.

## Important APIs, Types, And Functions
- `fdb_shim_set_local_client_library_path(const char* filePath)` sets an explicit client library path that overrides `FDB_LOCAL_CLIENT_LIBRARY_PATH`.
- `DLLEXPORT` is defined as empty unless provided by the build.

## Control Flow
Applications include this header and call the setter before selecting/using the C API through the shim. The implementation's `fdb_shim_dlopen_callback()` consults the stored path.

## State And Persistence Behavior
The header has no state. The implementation stores a process-global path. No database state is touched.

## Dependencies And Integration Points
It is installed only on Linux builds that include `fdb_c_shim`. CMake exports the shim target along with `FoundationDB-Client`.

## Risks And Edge Cases
The override must be set before the shim loads the real library to be effective. Passing null would be unsafe for the current `std::string` assignment implementation.

## Test Signals
Shim library tests and `shim_lib_tester` provide coverage for path override and dynamic loading behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_shim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_types.h -->
# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_types.h

## Purpose
`fdb_c_types.h` defines the minimal opaque handle and scalar typedefs shared by public and internal C API headers.

## Important APIs, Types, And Functions
- Opaque structs: `FDBFuture`, `FDBResult`, `FDBCluster`, `FDBDatabase`, and `FDBTransaction`.
- Scalar aliases: `fdb_error_t` and `fdb_bool_t`, both `int`.
- `DLLEXPORT` guard and `extern "C"` wrapping for C++ consumers.

## Control Flow
There is no control flow; this header centralizes type declarations so other headers can refer to opaque API handles without including the full public API.

## State And Persistence Behavior
The opaque types represent runtime objects managed by `fdb_c.cpp`; this header owns no state.

## Dependencies And Integration Points
It is included by `fdb_c.h` and `fdb_c_internal.h`, and is installed as part of the C client headers.

## Risks And Edge Cases
Changing scalar typedef widths or opaque type names would break ABI/source compatibility. `FDBCluster` remains declared for legacy compatibility even though cluster APIs are removed for newer API versions.

## Test Signals
Compile coverage from all C API consumers and the C90 test validates that these declarations remain compatible.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/generate_asm.py -->
# sources/storage-engines/foundationdb/bindings/c/generate_asm.py

## Purpose
`generate_asm.py` scans `fdb_c.cpp` for versioned API-change macros and generates assembly trampolines plus a C++ header of function pointer globals. The trampolines make public C symbols dispatch to the selected API-version implementation at runtime.

## Important APIs, Types, And Functions
- The script takes `os`, `cpu`, `source`, `asm`, and `h` arguments.
- Regex `func_re` captures `FDB_API_CHANGED(func, ver)` and `FDB_API_REMOVED(func, ver)` lines.
- `write_windows_asm()` emits MASM procedures that jump through `fdb_api_ptr_<func>`.
- `write_unix_asm()` emits Linux/FreeBSD/macOS assembly for x86_64, aarch64, and ppc64le.
- The header defines `fdb_api_ptr_unimpl()`, `fdb_api_ptr_removed()`, `void* fdb_api_ptr_<func>`, and `<func>_v<ver>_PREV` macros.

## Control Flow
The script builds an ordered mapping of functions to API-change versions, opens output assembly and header files, writes platform-specific trampolines for each function, then emits pointer variables initialized to `fdb_api_ptr_unimpl` and compatibility macros pointing each changed function to its previous implementation name.

## State And Persistence Behavior
Generated files are build artifacts consumed by `fdb_c.cpp` and the assembler. No runtime state exists until the generated pointer variables are compiled into `libfdb_c`; those variables are updated by `fdb_select_api_version_impl()`.

## Dependencies And Integration Points
It depends only on Python `re` and `sys`, but semantically depends on macro formatting in `fdb_c.cpp` and platform calling conventions. CMake invokes it before building `fdb_c`.

## Risks And Edge Cases
Regex parsing is intentionally narrow; formatting changes to `FDB_API_CHANGED/REMOVED` lines could drop trampolines. Assembly correctness is architecture-sensitive, especially tail-call behavior and register preservation for arbitrary function signatures. ppc64le has custom stack/register handling that is higher risk than x86_64/aarch64.

## Test Signals
Build success on each platform is the first signal. Runtime API-version tests, legacy API tests, and upgrade/shim tests validate that generated trampolines dispatch to correct implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/generate_asm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/symbolify.py -->
# sources/storage-engines/foundationdb/bindings/c/symbolify.py

## Purpose
`symbolify.py` generates an Apple `exported_symbols_list` file by extracting exported `fdb_` function names from C API headers.

## Important APIs, Types, And Functions
- Regex `^DLLEXPORT[^(]*(fdb_[^(]*)[(].*$` finds exported `fdb_` function declarations.
- CLI arguments are one or more header files followed by the output symbols file.
- Output symbols are prefixed with `_`, sorted, and written one per line.

## Control Flow
When run as a script, it reads all header files, accumulates matching symbols in a set, sorts them, and writes the output file with a trailing newline.

## State And Persistence Behavior
No runtime state exists. The generated symbols file is a build artifact consumed by the Apple linker.

## Dependencies And Integration Points
CMake invokes this script on Apple with `foundationdb/fdb_c.h` and `foundationdb/fdb_c_internal.h`, then passes the generated file through `-exported_symbols_list`.

## Risks And Edge Cases
The regex requires declarations beginning with `DLLEXPORT`; formatting changes or macro indirection could omit symbols. It only emits `fdb_` names, so non-`fdb_` exported APIs would need script changes.

## Test Signals
Apple build/link success verifies symbol extraction. Missing symbols would surface as runtime link failures or failed C API tests on Apple.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/symbolify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterApiWorkload.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterApiWorkload.cpp

## Purpose
`TesterApiWorkload.cpp` implements `ApiWorkload`, the reusable base class for C API tester workloads. It handles setup sequencing, random key/value generation, initial data population, workload progress control, tenant selection stubs, and common insert/clear/range-clear operations while maintaining an in-memory expected-value model.

## Important APIs, Types, And Functions
- Constructor reads workload options such as key/value lengths, max keys per transaction, initial size, existing-key read ratio, run-until-stop mode, operation counts, progress-check counts, key prefix, tenant count, and API version.
- `start()` schedules the workflow: clear data, create tenants if needed, workload-specific setup, populate initial data, then run tests.
- `getControlIfc()`, `stop()`, and `checkProgress()` support long-running workloads controlled by the manager.
- `runTests()` and `randomOperations()` execute either a fixed number of operations or until stopped.
- Random helpers generate keys, values, existing/non-existing keys, non-empty key ranges, tenants, and debug tenant strings.
- `populateDataTx()`, `populateTenantData()`, `clearData()`, and `clearTenantData()` seed and clear database state.
- `randomInsertOp()`, `randomClearOp()`, and `randomClearRangeOp()` are common transaction helpers used by derived workloads.

## Control Flow
All work is asynchronous through the workload scheduler and transaction executor. Methods call `execTransaction()` with a transaction body and success continuation. After commit succeeds, the local `stores[tenantId]` model is updated and the next continuation is scheduled. `randomOperations()` decrements counters atomically and loops through `randomOperation()`, which derived classes override.

## State And Persistence Behavior
Persistent state is restricted to keys under `keyPrefix` for this workload id, optionally per tenant. Local expected state lives in `stores`, an `unordered_map` from optional tenant id to `KeyValueStore`. Self-conflicting writes are used where needed so retries/timeouts do not leave older attempts in flight after a successful commit.

## Dependencies And Integration Points
It depends on `TesterApiWorkload.h`, `TesterUtil.h`, `test/fdb_api.hpp`, `fmt`, `WorkloadBase`, and `KeyValueStore`. Derived workloads in this subset rely on its helpers and local model.

## Risks And Edge Cases
Tenant support is partially stubbed: `createTenantsIfNecessary()` asserts false when tenants are configured, so tests with tenants cannot use this path yet. Random existing-key selection falls back to a generated key if the store is empty or selectors hit sentinels. Run-until-stop progress checks rely on atomics and scheduler ordering. Local model updates only occur after successful transaction callbacks.

## Test Signals
Derived workloads provide the direct behavior checks. `ApiWorkload` contributes setup/populate/clear correctness and progress confirmation for long-running tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterApiWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterApiWorkload.h -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterApiWorkload.h

## Purpose
`TesterApiWorkload.h` declares `ApiWorkload`, the base class for randomized C API tester workloads. It exposes lifecycle hooks, progress-control integration, random data helpers, common mutation operations, tenant helpers, and the in-memory expected-state stores.

## Important APIs, Types, And Functions
- `ApiWorkload : public WorkloadBase, IWorkloadControlIfc`.
- Public overrides: `start()`, `getControlIfc()`, `stop()`, and `checkProgress()`.
- Extension points: `setup(TTaskFct cont)`, `runTests()`, and `randomOperation(TTaskFct cont)`.
- Protected configuration fields include API version, key/value lengths, max keys per transaction, initial size, existing-key ratio, operation counts, stop/progress atomics, key prefix, tenant names, and `stores`.
- Protected helpers cover random key/value generation, data population/clearing, common random insert/clear/clear-range operations, and tenant mapping.

## Control Flow
The header defines the contract implemented by `TesterApiWorkload.cpp`: derived classes override `randomOperation()` or `runTests()`, and call protected helpers with continuations to keep the scheduler-driven asynchronous flow alive.

## State And Persistence Behavior
The declared fields define both persistent key scope (`keyPrefix`, tenants) and local state (`stores`, atomics, operation counters). Persistent effects are performed by implementation methods and derived workloads.

## Dependencies And Integration Points
It includes `TesterWorkload.h`, `TesterKeyValueStore.h`, and `<atomic>`. API tester workload files register concrete factories against this base.

## Risks And Edge Cases
Because `ApiWorkload` also implements `IWorkloadControlIfc`, callers must only request the control interface when `runUntilStop` is true. Derived classes must always schedule or invoke their continuation, or the workload stalls.

## Test Signals
Header correctness is compile-tested by all API tester workloads. Runtime signals come from derived workload progress checks and expected-state assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterApiWorkload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterAtomicOpsCorrectnessWorkload.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterAtomicOpsCorrectnessWorkload.cpp

## Purpose
`TesterAtomicOpsCorrectnessWorkload.cpp` defines `AtomicOpsCorrectnessWorkload`, a randomized API tester workload for FoundationDB atomic mutation semantics, including integer operations, byte min/max, append-if-fits, compare-and-clear, and versionstamped key/value operations.

## Important APIs, Types, And Functions
- `OpType` enumerates atomic operations from add/bitwise ops through compare-and-clear.
- `randomOperation()` chooses one operation type and dispatches to the appropriate test helper.
- `testIntAtomicOp()` encodes random integers to little-endian byte strings and compares output using an integer function.
- `testAtomicOp()` sets an initial value, conditionally applies an atomic op exactly once, reads the final value, and checks it against a local function.
- `testAtomicVersionstampedKeyOp()` validates `SET_VERSIONSTAMPED_KEY`.
- `testAtomicVersionstampedValueOp()` validates `SET_VERSIONSTAMPED_VALUE`.
- `testAtomicCompareAndClearOp()` verifies the key is removed when param equals current value.
- `WorkloadFactory<AtomicOpsCorrectnessWorkload>` registers `"AtomicOpsCorrectness"`.

## Control Flow
Every operation is a sequence of asynchronous transactions. The generic atomic path first writes `val1`, then starts a transaction that reads the key and only applies the atomic mutation if it still equals `val1`; this guards against applying non-idempotent atomic operations multiple times after `commit_unknown_result`. A final transaction reads and validates the result.

## State And Persistence Behavior
Each test uses random keys under the workload prefix. Persistent state is the atomic-operation target key and any resulting versionstamped key/value. The workload generally does not update `stores`; it validates directly against read-back values.

## Dependencies And Integration Points
It depends on `ApiWorkload`, `TesterUtil` integer conversion helpers, `fdb_c_options.g.h`, `fmt`, and the C++ C API wrapper in `test/fdb_api.hpp`.

## Risks And Edge Cases
Atomic operation idempotency under retry is explicitly handled for the generic path. Versionstamp tests depend on correct ten-byte placeholder plus four-byte offset encoding. `APPEND_IF_FITS` expectations assume generated values fit within FoundationDB value limits. Integer operations depend on little-endian conversion helpers.

## Test Signals
Failures are logged with expected/actual values and asserted. Coverage includes operations whose correctness is easy to regress in binding wrappers because they use raw mutation type enums and byte-level parameters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterAtomicOpsCorrectnessWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterCancelTransactionWorkload.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterCancelTransactionWorkload.cpp

## Purpose
`TesterCancelTransactionWorkload.cpp` defines `CancelTransactionWorkload`, a randomized API tester workload for transaction cancellation and outstanding read futures. It starts concurrent reads and completes transactions without committing, checking that cancellation/cleanup does not corrupt returned data or scheduler flow.

## Important APIs, Types, And Functions
- `OpType` includes `OP_CANCEL_GET` and `OP_CANCEL_AFTER_FIRST_GET`.
- `randomCancelGetTx()` starts multiple `get()` futures then immediately marks the context done.
- `randomCancelAfterFirstResTx()` starts multiple `get()` futures and registers continuations that compare returned values against `stores`.
- `randomOperation()` chooses a tenant and cancel operation.
- Factory registration name is `"CancelTransaction"`.

## Control Flow
The workload uses `execTransaction()` with transaction bodies that issue reads but do not commit. In the first mode it abandons outstanding read futures by calling `done()`. In the second mode each future continuation validates one read and calls `done()`, effectively completing after the first ready callback path.

## State And Persistence Behavior
This workload does not mutate persistent state; it reads from data populated by `ApiWorkload`. Expected state is the inherited `stores` model.

## Dependencies And Integration Points
It depends on `ApiWorkload`, `TesterUtil`, `test/fdb_api.hpp`, and the transaction executor's behavior when a context is completed while futures are outstanding.

## Risks And Edge Cases
The name suggests cancellation, but explicit transaction cancel calls are encapsulated by context completion/destruction rather than direct calls here. Multiple continuations may race to call `ctx->done()` in `randomCancelAfterFirstResTx()`, so executor idempotence matters. Expected value comparisons require the local store to remain in sync with populated data.

## Test Signals
The workload detects mismatches for futures that complete before cancellation and relies on absence of crashes, leaks, or scheduler stalls for abandoned futures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterCancelTransactionWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterCorrectnessWorkload.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterCorrectnessWorkload.cpp

## Purpose
`TesterCorrectnessWorkload.cpp` defines `ApiCorrectnessWorkload`, the main randomized C API correctness workload for basic transaction operations: insert, get, getKey, clear, getRange, clearRange, and commit-then-read behavior.

## Important APIs, Types, And Functions
- `OpType` enumerates operation families.
- `randomCommitReadOp()` writes key/value pairs with read conflict ranges, updates the local store, then reads them back in a separate transaction, optionally using GRV cache for API >= 710.
- `randomGetOp()` issues concurrent gets and compares each result with `stores`.
- `randomGetKeyOp()` tests key selectors and adjusts results that fall outside the current workload key prefix.
- `getRangeLoop()` repeatedly calls `getRange()` using `more` and `firstGreaterThan(lastKey)` until exhausted.
- `randomGetRangeOp()` compares FDB range results with the local `KeyValueStore`.
- `randomOperation()` chooses a random operation, forcing insert when the local store is empty.
- Factory registration name is `"ApiCorrectness"`.

## Control Flow
Each operation uses asynchronous `execTransaction()` calls and scheduler continuations. Reads gather futures and continue after all complete; range reads loop across pages if `more` is true. Mutations update `stores` only after commit success through inherited helpers or explicit callbacks.

## State And Persistence Behavior
Persistent data is confined to the inherited workload key prefix. Local expected state is `stores[tenantId]`. `randomGetKeyOp()` acknowledges that real FDB contains data from other clients and maps results outside the workload prefix to start/end sentinels before comparing with the local model.

## Dependencies And Integration Points
It depends on `ApiWorkload`, `TesterUtil`, `fmt`, and `test/fdb_api.hpp`. It relies heavily on `TesterKeyValueStore` matching FoundationDB selector and range semantics for keys inside the workload prefix.

## Risks And Edge Cases
Range operations choose begin and end independently; if begin > end, the local comparison path may expose API assumptions depending on wrapper behavior. `getRangeLoop()` must clear results on retry to avoid duplicate accumulation. Key selector offsets are limited to 0..4 here, so negative selector coverage is elsewhere. GRV cache testing is API-version-gated.

## Test Signals
Logs and assertions report mismatches for get, getKey, getRange, and commit-read cases. This is a broad behavioral signal for C API transaction wrappers, future aggregation, retry handling, and local model consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterCorrectnessWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterExampleWorkload.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterExampleWorkload.cpp

## Purpose
`TesterExampleWorkload.cpp` defines `SetAndGetWorkload`, a minimal example API tester workload that writes one random key/value pair and reads it back.

## Important APIs, Types, And Functions
- `SetAndGetWorkload : public WorkloadBase` stores `keyPrefix` and a `Random`.
- `start()` calls `setAndGet(NO_OP_TASK)`.
- `setAndGet(cont)` writes a random key/value in one transaction, commits, then reads the key in a second transaction and logs an error if the value differs.
- Factory registration name is `"SetAndGet"`.

## Control Flow
The workload generates a key and value, calls `execTransaction()` to set and commit, then in the success continuation calls another `execTransaction()` to `get()` and compare the result before completing the provided continuation.

## State And Persistence Behavior
It persists one key/value under a workload-specific prefix. It does not clear prior data or maintain a local model beyond captured key/value variables.

## Dependencies And Integration Points
It depends on `TesterWorkload.h`, `TesterUtil.h`, `fmt`, the transaction executor inherited through `WorkloadBase`, and factory registration.

## Risks And Edge Cases
This is intentionally simple and not a stress workload. It logs mismatches but does not explicitly assert in the shown code path, so it is more demonstrative than comprehensive. Random keys can leave data behind unless surrounding harness cleanup handles it.

## Test Signals
The signal is a successful set/commit/get comparison through the C API tester framework, useful as a smoke test and example for new workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterExampleWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterKeyValueStore.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterKeyValueStore.cpp

## Purpose
`TesterKeyValueStore.cpp` implements the thread-safe in-memory ordered key/value model used by API tester workloads to compute expected FoundationDB results.

## Important APIs, Types, And Functions
- `get()` returns an optional value for a key.
- `exists()` checks key presence.
- `getKey()` models FoundationDB key-selector semantics over the ordered map.
- `getRange()` returns ordered or reverse key/value slices with a limit.
- `set()`, `clear(key)`, and `clear(begin,end)` mutate the model.
- `size()`, `startKey()`, `endKey()`, and `printContents()` provide support/debug APIs.

## Control Flow
All methods take a mutex. Selector logic starts at `lower_bound(keyName)`, adjusts for `orEqual` and offset direction, walks the map, and returns either a real key or start/end sentinel. Range logic scans from `lower_bound(begin)` forward until `end` or limit, or backward from `lower_bound(end)` for reverse mode.

## State And Persistence Behavior
State is local process memory: `std::map<fdb::Key, fdb::Value, std::less<>> store` plus a mutex. It mirrors expected persistent database contents for a workload prefix but is not itself persisted.

## Dependencies And Integration Points
It includes `TesterKeyValueStore.h` and uses FoundationDB C++ wrapper types from `TesterUtil.h`. `ApiWorkload` owns one store per optional tenant id.

## Risks And Edge Cases
`getKey()` must match FDB key selector semantics; subtle off-by-one differences can create false test failures or miss real API bugs. Reverse `getRange()` is implemented but noted as not currently tested because reverse range queries are disallowed at the API level in that context. `printContents()` assumes keys are printable C strings, which may not hold for arbitrary binary keys.

## Test Signals
It is an oracle rather than a test target. Correctness workloads compare live C API results against this model, so its behavior directly determines test quality.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterKeyValueStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterKeyValueStore.h -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterKeyValueStore.h

## Purpose
`TesterKeyValueStore.h` declares the thread-safe ordered in-memory key/value store used as the expected-state oracle by C API tester workloads.

## Important APIs, Types, And Functions
- Query methods: `get`, `exists`, `getKey`, and `getRange`.
- Mutation methods: `set`, `clear(key)`, and `clear(begin,end)`.
- Metadata/debug methods: `size`, `startKey`, `endKey`, and `printContents`.
- Private members: `std::map<fdb::Key, fdb::Value, std::less<>> store` and mutable `std::mutex`.

## Control Flow
The header only declares the interface. Implementations lock internally, so callers do not manage synchronization.

## State And Persistence Behavior
The declared map holds local expected state. Sentinels returned by `startKey()`/`endKey()` model selector results before the first key and after the last key.

## Dependencies And Integration Points
It depends on STL containers, mutexes, optionals, and `TesterUtil.h` for FDB wrapper types. `TesterApiWorkload.h` includes it and stores per-tenant instances.

## Risks And Edge Cases
Because it is used as an oracle, semantic drift from FoundationDB selector/range behavior affects many tests. Methods accepting `fdb::KeyRef`/`ValueRef` must copy data into owning strings before refs expire; the implementation does this through `fdb::Key`/`Value`.

## Test Signals
Compile coverage comes from all API tester workloads. Runtime signal is indirect through comparisons in correctness and cancellation workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterKeyValueStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterOptions.h -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterOptions.h

## Purpose
`TesterOptions.h` defines the aggregate command-line/configuration state for the C API tester executable.

## Important APIs, Types, And Functions
- `TesterOptions` fields include API version, cluster file, tracing options, external/future client library paths, temp directory, local-client disable flag, test file path, pipe names, transaction retry limit, thread/database/client counts, stats interval, parsed `TestSpec`, blob granule base path, TLS files, and retain-client-library-copy flag.

## Control Flow
There is no method logic here. Argument parsing and test runner code populate the struct, then downstream setup uses it to configure network options, workloads, clients, and tests.

## State And Persistence Behavior
The struct is process-local configuration. Fields such as trace directory, temp directory, external client library, and TLS paths affect filesystem/network behavior elsewhere.

## Dependencies And Integration Points
It includes `TesterTestSpec.h`, whose `FDB_API_VERSION` default is used for `apiVersion`. It is consumed by `fdb_c_api_tester.cpp` and related runner code.

## Risks And Edge Cases
Uninitialized integer fields (`numFdbThreads`, `numClientThreads`, `numDatabases`, `numClients`) rely on parser/defaulting elsewhere before use. Path fields must be validated by consumers. Retaining client library copies can intentionally leave files for debugging.

## Test Signals
Compile coverage validates the option aggregate. Runtime command-line tests and API tester invocations validate that fields are populated and honored.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterOptions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterScheduler.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterScheduler.cpp

## Purpose
`TesterScheduler.cpp` implements the API tester scheduler using Boost.Asio. It provides asynchronous task posting, delayed timers, scheduler start/stop, and thread joining for workload execution.

## Important APIs, Types, And Functions
- `NO_OP_TASK` is an empty task function.
- `AsioTimer : ITimer` wraps `boost::asio::steady_timer` and cancels it through `cancel()`.
- `AsioScheduler : IScheduler` owns an `io_context`, worker threads, outstanding-work executor, and thread count.
- `start()` creates tracked work and starts `io_context.run()` threads.
- `schedule()` posts tasks to the context.
- `scheduleWithDelay()` creates a timer and runs the task if the wait is not canceled.
- `stop()` releases outstanding work; `join()` joins worker threads.
- `createScheduler(numThreads)` asserts a range of 1..1000 and returns an `AsioScheduler`.

## Control Flow
Clients create a scheduler, call `start()`, then post tasks or delayed tasks. Timers run callbacks on scheduler threads unless canceled. `stop()` does not immediately stop running tasks; it lets the context drain once no work remains, and `join()` waits for threads to exit.

## State And Persistence Behavior
All state is process-local scheduler state: threads, `io_context`, outstanding work, and timers. It does not touch FoundationDB or the filesystem directly.

## Dependencies And Integration Points
It depends on `TesterScheduler.h`, `TesterUtil.h` for `ASSERT`, Boost.Asio, and C++ threads. Workload and transaction executor code schedule continuations through this abstraction.

## Risks And Edge Cases
The returned `ITimer` owns the actual timer; if destroyed without cancel semantics considered, behavior depends on Boost.Asio timer destruction. `stop()` only clears the work guard, so callers must ensure no infinite task repost loop. The 1000-thread upper bound is asserted but still high.

## Test Signals
API tester workloads indirectly validate scheduler correctness by requiring continuations, delayed tasks, progress checks, and shutdown to complete without deadlock.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterScheduler.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterScheduler.h -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterScheduler.h

## Purpose
`TesterScheduler.h` declares the asynchronous scheduler abstraction used by the C API tester framework.

## Important APIs, Types, And Functions
- `TTaskFct` is `std::function<void(void)>`.
- `NO_OP_TASK` is declared as a reusable empty continuation.
- `ITimer` declares `cancel()`.
- `IScheduler` declares lifecycle methods `start`, `schedule`, `scheduleWithDelay`, `stop`, and `join`.
- `createScheduler(int numThreads)` constructs an implementation.

## Control Flow
The header defines the interface; implementations post tasks and timers asynchronously. Workloads use `TTaskFct` continuations throughout the framework.

## State And Persistence Behavior
No state is held in the header. Implementations manage scheduler threads/timers. There is no persistent database behavior.

## Dependencies And Integration Points
It depends on `<functional>` and `<memory>`. It is implemented by `TesterScheduler.cpp` and used by workload manager/executor code to decouple tests from a specific async backend.

## Risks And Edge Cases
Callers must respect scheduler lifecycle: tasks should not be posted after shutdown, and timers must be canceled or allowed to fire before destruction depending on desired behavior. A task that never schedules its continuation can stall a workload.

## Test Signals
Indirect runtime coverage comes from every API tester workload. Compile coverage validates the abstraction boundary.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterScheduler.h -->
