# subset-b-008391 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/impl.py -->
# sources/storage-engines/foundationdb/bindings/python/fdb/impl.py

Purpose: This is the main Python binding implementation for FoundationDB. It loads `libfdb_c` with `ctypes`, selects and initializes C API signatures, starts the network thread, exposes database and transaction objects, and adapts native futures into Python-friendly lazy values, ranges, callbacks, and transactional helpers.

Important APIs and types: Key public surfaces are `transactional`, `open`, `open_v609`, `open_v13`, `create_database`, `create_cluster`, `Database`, `Cluster`, `Transaction`, `TransactionRead`, `FDBRange`, `Future` subclasses, `KeySelector`, `KeyValue`, `options`, `predicates`, `StreamingMode`, `ConflictRangeType`, and `strinc`. Dynamic option and mutation methods are generated from `fdboptions` through `fill_options` and `fill_operations`, so API coverage depends on the generated option metadata.

Control flow: Import-time code builds option/predicate wrappers, resolves the platform C library, assigns `_FDBBase.capi`, and defines `ctypes` structs. `init_c_api` binds every C function's argument and return types and errcheck behavior. `open` lazily calls `init`, which configures optional event models, calls `fdb_setup_network`, and starts a daemon network thread running `fdb_run_network`. `transactional` detects whether its argument is already a transaction; otherwise it creates a transaction, invokes the wrapped function, commits, and retries through `on_error`.

State and persistence behavior: Persistent database state is owned by FoundationDB through C API calls; this module holds process-local state such as `_network_thread`, cached `open_databases`, thread-local future semaphores, pinned callbacks, and Python wrapper lifetimes. Destructors destroy native database, transaction, and future pointers. `open_tenant` is a compatibility stub that loads tenant symbols but intentionally returns `None`.

Dependencies and integration points: It depends on `fdb.__version__/api_version` selection, generated `fdboptions`, `fdb.tuple.pack`, platform dynamic-library lookup, Python threading/multiprocessing, optional `gevent` or `asyncio`, and native `libfdb_c`. `locality.py`, directory layers, subspaces, tests, and user code all route through this module.

Risks: The FFI boundary is sensitive to incorrect signatures, pointer lifetime, callback pinning, and platform library loading. `transactional` may rerun user code and rejects generators only for API versions at or after 630. Async support mutates class methods globally. Future blocking avoids native blocking for signal handling but depends on callback delivery. Database caching is keyed only by cluster file.

Test signals: `unit_tests.py`, `tester.py`, `cancellation_timeout_tests.py`, and `size_limit_tests.py` exercise options, watches, retry/timeout/cancel semantics, range reads, atomic ops, conflict ranges, client status, approximate transaction size, and future handling. Cross-language binding testers stress stack-machine operations and error encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/impl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/locality.py -->
# sources/storage-engines/foundationdb/bindings/python/fdb/locality.py

Purpose: This module exposes Python locality helpers for shard boundary discovery and storage-server address lookup.

Important APIs and types: `get_boundary_keys(db_or_tr, begin, end)` returns an iterator over shard boundary keys. `get_addresses_for_key(tr, key)` is transactional and returns a `FutureStringArray` from `fdb_transaction_get_addresses_for_key`. The private `_get_boundary_keys` generator implements retry and paging behavior.

Control flow: Inputs are normalized with `_impl.keyToBytes`. If called with a transaction, boundary scanning creates a separate transaction at the caller's read version; otherwise it creates a new transaction from the database. The scan reads system key range `\xff/keyServers/<begin>` to `\xff/keyServers/<end>` with read-system-keys and lock-aware options, yields once early to dispatch asynchronously, then yields decoded boundary suffixes.

State and persistence behavior: It does not persist user state. It reads FoundationDB system keys and may create replacement transactions after `transaction_too_old` if progress has already been made, which can make a long scan non-transactional after retry.

Dependencies and integration points: It depends directly on `fdb.impl` transaction, key conversion, `FDBError`, and future wrappers. `unit_tests.py` validates locality consistency by comparing addresses for shard starts and preceding end keys.

Risks: Boundary scans require system-key access and assume system key encodings with a fixed 13-byte prefix. The retry path can trade strict transactionality for progress. Address lookup requires an initialized C API symbol and valid transaction pointer.

Test signals: Python unit tests call `get_boundary_keys` and `get_addresses_for_key` with read-system-keys enabled and assert address sets are internally consistent across adjacent boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/locality.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/subspace_impl.py -->
# sources/storage-engines/foundationdb/bindings/python/fdb/subspace_impl.py

Purpose: This file implements the Python `Subspace` abstraction, which gives tuple-encoded namespaces a stable raw key prefix.

Important APIs and types: `Subspace` exposes `key`, `pack`, `pack_with_versionstamp`, `unpack`, `range`, `contains`, `as_foundationdb_key`, `subspace`, and `__getitem__`. It composes raw prefixes with `fdb.tuple` encoding.

Control flow: Construction packs an optional prefix tuple over a raw prefix. Indexing or `subspace` creates child subspaces by appending tuple elements. `pack` and `range` prepend `rawPrefix`; `unpack` first validates prefix containment and then decodes with `prefix_len`.

State and persistence behavior: The only state is immutable-by-convention `rawPrefix`. No database operations occur here, but generated keys are used by directory layers and user code for persistent key layout.

Dependencies and integration points: It depends on `fdb.tuple` and integrates with `impl.keyToBytes` through `as_foundationdb_key`. Directory and tester extensions use subspaces to map logical names to key ranges.

Risks: `contains` uses raw prefix matching, so callers must avoid overlapping prefixes unless intentionally modeling nested spaces. Manual raw prefixes must be valid FoundationDB keys and must match tuple encoding expectations.

Test signals: Directory extension and binding tester operations cover subspace creation, key packing/unpacking, range generation, containment, and prefix stripping.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/subspace_impl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/tuple.py -->
# sources/storage-engines/foundationdb/bindings/python/fdb/tuple.py

Purpose: This module implements FoundationDB tuple layer encoding for Python. It turns typed tuples into byte strings whose lexicographic order matches tuple order and decodes those byte strings back into Python values.

Important APIs and types: Public APIs are `pack`, `pack_with_versionstamp`, `unpack`, `range`, `compare`, `has_incomplete_versionstamp`, `SingleFloat`, `Versionstamp`, and `int2byte`. Supported encoded types include `None`, `bytes`, UTF-8 `str`, signed integers, single and double floats, booleans, UUIDs, nested tuples/lists, and versionstamps.

Control flow: `_encode` dispatches by Python type, assigns FoundationDB tuple type codes, escapes embedded null bytes, encodes integers with length-sensitive positive/negative forms, adjusts float sign bits for sortability, and tracks incomplete versionstamp position. `_pack_maybe_with_versionstamp` appends the little-endian versionstamp position when needed. `_decode` reverses each type-code encoding. `compare` mirrors tuple ordering without packing.

State and persistence behavior: The module is stateless apart from constants. Its byte output is persistent key format, so changes are compatibility-sensitive. Versionstamp packing differs for API versions before 520 versus newer APIs, and boolean treatment is API-version-aware.

Dependencies and integration points: It depends on `ctypes`, `uuid`, `struct`, `math`, `bisect`, and `fdb` version state. `Subspace`, directory layers, binding testers, and user schemas rely on its ordering and binary stability.

Risks: Edge cases include NaN ordering, negative zero, large integer bounds, nested `None` terminator escaping, API-version-specific boolean/versionstamp behavior, and incomplete versionstamp multiplicity. A bug changes persistent key order and can corrupt higher-level abstractions.

Test signals: `tuple_tests.py` performs randomized pack/unpack/order/range checks over bytes, strings, large integers, floats, booleans, UUIDs, and nested values. `tester.py` also exercises tuple packing, sorting, ranges, float encode/decode, and versionstamp packing behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/tuple.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/pycodestyle.cfg -->
# sources/storage-engines/foundationdb/bindings/python/pycodestyle.cfg

Purpose: This configuration defines local pycodestyle behavior for the Python FoundationDB binding.

Important APIs and types: It is a `[pycodestyle]` config file with `max-line-length = 150`, excludes generated `fdboptions.py`, and ignores selected E/W rules including comment style, import position, comparisons to `None`/booleans/types, bare except, and line-break operator variants.

Control flow: There is no runtime control flow. Tooling reads this file when pycodestyle runs in the bindings tree.

State and persistence behavior: It does not affect runtime state or database persistence. It affects developer feedback and CI lint acceptance.

Dependencies and integration points: It integrates with Python style tooling and with generated option files produced elsewhere in the build.

Risks: Several ignores permit legacy idioms that modern linters would flag. Excluding `fdboptions.py` is intentional because it is generated, but it means generated API surface style is not validated here.

Test signals: The signal is lint/tool success under this configuration, not unit-test behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/pycodestyle.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/pyproject.toml -->
# sources/storage-engines/foundationdb/bindings/python/pyproject.toml

Purpose: This file declares packaging metadata for the Python FoundationDB binding using setuptools as the PEP 517 build backend.

Important APIs and types: It defines `setuptools.build_meta`, project name `foundationdb`, dynamic version from `fdb.__version__`, authors, description, keywords, URLs, Python requirement `>=3.8`, classifiers, and package discovery restricted to `fdb`.

Control flow: Build tools read the metadata, import `fdb.__version__` for the dynamic version, and find only the `fdb` package to avoid accidental modules in CMake build directories.

State and persistence behavior: It affects generated package metadata and distribution contents, not runtime database state.

Dependencies and integration points: It integrates with pip/build/setuptools and the binding package layout. The comment about restricting package discovery is tied to CMake out-of-source or in-build-tree usage.

Risks: Dynamic version import can execute package import-time code if not carefully isolated by setuptools. The package discovery include list is narrow and must be updated if new top-level Python packages are added.

Test signals: Packaging tests or install builds should confirm that only intended binding modules are included and the version matches `fdb.__version__`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/pyproject.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/cancellation_timeout_tests.py -->
# sources/storage-engines/foundationdb/bindings/python/tests/cancellation_timeout_tests.py

Purpose: This file is a focused Python binding test suite for transaction cancellation, retry-limit, timeout, database-default retry/timeout, and combined behavior.

Important APIs and types: It uses `fdb.FDBError`, transaction options `set_timeout` and `set_retry_limit`, database options `set_transaction_timeout` and `set_transaction_retry_limit`, `cancel`, `reset`, `on_error`, `commit`, and basic mutation/read operations. `retry_with_timeout` wraps individual checks with a guard transaction timeout.

Control flow: Each test defines small transactional scenarios that deliberately trigger cancellation, retryable `transaction_too_old` errors, future-version errors, or timeout expiry. Assertions inspect exact FoundationDB error codes such as `1025` canceled, `1031` timed out, `1007` retryable, and `1009` future version.

State and persistence behavior: Tests write simple keys such as `foo` but mainly validate transaction-local state: whether cancellation survives `on_error`, whether reset clears cancellation/timeouts/retry counts, and whether database defaults are reapplied after reset. The suite resets database-level options to defaults at the end of affected tests.

Dependencies and integration points: It depends on the Python binding option wrappers generated in `impl.py`, C API transaction state, time-based behavior, and `unit_tests.py` as the orchestrator.

Risks: Time-based sleeps can be slow or flaky on overloaded systems. The retry wrapper creates a timeout transaction but retries the tested transaction separately, so unexpected errors can loop until timeout. Exact error-code expectations bind tightly to FoundationDB C API semantics.

Test signals: Strong signals are exact error-code matches across cancellation, retry-limit exhaustion, transaction reset, database-default override, timeout retroactivity, timeout unset behavior, and combined cancellation/retry-limit cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/cancellation_timeout_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/directory_extension.py -->
# sources/storage-engines/foundationdb/bindings/python/tests/directory_extension.py

Purpose: This module adapts the language-agnostic binding tester stack machine to Python directory-layer and subspace operations.

Important APIs and types: `DirectoryExtension` maintains `dir_list`, active `dir_index`, and `error_index`. `process_instruction` handles `DIRECTORY_CREATE_SUBSPACE`, `DIRECTORY_CREATE_LAYER`, create/open/move/remove/list/exists operations, pack/unpack/range/contains, logging, subspace opening, and prefix stripping.

Control flow: Instructions pop tuple-encoded paths and parameters from the tester stack, invoke the selected directory or subspace object, append new directory handles when operations create or open one, and push results back as raw values or tuple-packed data. Exceptions push `DIRECTORY_ERROR`; operations that would create a directory append `None` so later indexed operations remain deterministic.

State and persistence behavior: The extension stores only in-memory handles, but operations mutate persistent FoundationDB directory metadata through `fdb.directory_impl` calls. Logging operations write directory state into caller-provided subspaces.

Dependencies and integration points: It depends on `fdb`, `fdb.directory_impl`, `fdb.Subspace`, and the `Instruction`/`Stack` protocol in `tester.py`. It mirrors the Ruby directory extension to support cross-binding conformance tests.

Risks: Stack order and path tuple decoding must match the tester spec exactly. Exceptions are intentionally flattened to `DIRECTORY_ERROR`, which is good for conformance but can hide diagnostic detail unless logging flags are enabled.

Test signals: Binding tester directory op streams validate creation, manual-prefix behavior, partitions, moves, removals, list/existence, key packing, range boundaries, containment, logging, and error handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/directory_extension.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/size_limit_tests.py -->
# sources/storage-engines/foundationdb/bindings/python/tests/size_limit_tests.py

Purpose: This suite validates Python binding exposure of transaction size-limit options and approximate transaction size reporting.

Important APIs and types: It uses `@fdb.transactional`, database option `set_transaction_size_limit`, transaction option `set_size_limit`, `get_approximate_size`, conflict-key helpers, and direct item assignment.

Control flow: `test_size_limit_option` writes a 1 KiB value successfully, then expects error `2101` when database or transaction size limits are set below the operation size. It also verifies that database defaults survive `on_error`. `test_get_approximate_size` mutates a transaction and asserts approximate size grows after set, clear, read conflict, and write conflict operations.

State and persistence behavior: Tests write keys `t1` through `t4` and small conflict keys. They explicitly reset the database transaction size limit after testing to avoid contaminating later tests.

Dependencies and integration points: The file depends on option-generation in `impl.py`, C API approximate-size futures, and is called from `unit_tests.py`; it can also be run standalone with a cluster file.

Risks: Exact byte-limit behavior depends on C API accounting, and approximate size is only asserted monotonically rather than by exact values. Failure to reset database defaults would affect unrelated tests.

Test signals: Error code `2101`, successful override behavior, survival of database defaults through `on_error`, and monotonic approximate-size growth are the core signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/size_limit_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/tester.py -->
# sources/storage-engines/foundationdb/bindings/python/tests/tester.py

Purpose: This is the Python binding tester runner. It reads tuple-encoded instructions from FoundationDB, executes them against the Python binding, and writes or stacks normalized results for cross-language conformance.

Important APIs and types: `Stack` resolves futures and normalizes missing results/errors. `Instruction` wraps the current target object and stack. `Tester` manages transactions, instruction iteration, thread spawning, range result packing, stack logging, directory extension dispatch, and embedded unit tests.

Control flow: At startup it selects the requested API version, opens a database, and loads instructions under a tuple range prefix. `Tester.run` decodes each op, chooses database/current transaction/snapshot target based on suffixes, executes operations such as get/range/set/clear/conflict/commit/reset/cancel/tuple/locality/directory/unit-tests, catches `FDBError`, and pushes tuple-packed error markers. `START_THREAD` creates nested testers over other prefixes.

State and persistence behavior: It keeps in-memory stacks and a shared transaction map protected by `RLock`. Persistent effects are the actual database mutations requested by instruction streams plus optional `LOG_STACK` output truncated to 40,000 bytes per value.

Dependencies and integration points: It integrates `fdb.impl`, `fdb.tuple`, `DirectoryExtension`, and `run_unit_tests`. It is designed to be driven by FoundationDB's binding tester infrastructure.

Risks: Randomized choices among equivalent API forms are seeded, but failures can still depend on instruction ordering and concurrent tester threads. Stack future resolution must classify value absence consistently. Legacy APIs such as `sorted(..., cmp=compare)` in related tuple tests indicate version sensitivity.

Test signals: The tester validates broad binding behavior: futures, transactions, snapshot reads, range selectors, atomic ops, conflict ranges, versionstamps, tuple order, directory layer semantics, threading, waits, and the embedded Python unit suite.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/tester.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/tuple_tests.py -->
# sources/storage-engines/foundationdb/bindings/python/tests/tuple_tests.py

Purpose: This randomized test validates Python tuple-layer encoding, decoding, lexicographic ordering, comparison, and range behavior.

Important APIs and types: It imports `pack`, `unpack`, `compare`, `int2byte`, `SingleFloat`, and `fdb.tuple.range`. Helpers generate random Unicode, binary strings, integers up to tuple-layer limits, floating edge cases, booleans, UUIDs, and nested lists.

Control flow: `tupleTest` generates random tuples, compares sorting by tuple comparator with sorting by packed bytes, checks pack/unpack identity, verifies prefix ranges include extended tuples but exclude unrelated tuples, and ensures packed-byte ordering matches `compare`.

State and persistence behavior: It is pure in-memory testing; no database state is touched. Its target is persistent key-format compatibility of `fdb.tuple`.

Dependencies and integration points: It depends on Python `random`, `struct`, `ctypes`, `unicodedata`, `uuid`, and tuple-layer implementation details. It can be run as a standalone script.

Risks: The test is probabilistic and seeded only by default runtime state, so it may miss rare edge cases. It uses Python 2-era `sorted(..., cmp=compare)` syntax, which is not valid in modern Python 3 without adaptation.

Test signals: Sort equivalence, pack/unpack identity, prefix range inclusion/exclusion, and comparison parity across thousands of generated tuples are the important signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/tuple_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/unit_tests.py -->
# sources/storage-engines/foundationdb/bindings/python/tests/unit_tests.py

Purpose: This file orchestrates Python binding unit tests against a live FoundationDB cluster.

Important APIs and types: It imports cancellation/timeout tests, size-limit tests, `fdb.transactional`, database and transaction option methods, watches, locality helpers, predicates, and client status retrieval. `run_unit_tests(db)` is the main entry point.

Control flow: Standalone mode selects latest API version, parses a cluster file, opens the database, and runs `run_unit_tests`. The test sequence covers database options, transaction options, watches, cancellation, retry limits, timeouts, locality, predicates, size limits, approximate transaction size, and client status JSON. It also checks generator rejection behavior for `@transactional` at API version 630+.

State and persistence behavior: Tests write and mutate keys such as `w0` through `w3`, use watches, set database-level defaults, and read system keys for locality. Some tests sleep and retry until watch/locality behavior is stable.

Dependencies and integration points: It integrates most Python binding modules and is also invoked by `tester.py` through the `UNIT_TESTS` instruction. Client status parsing depends on JSON returned by the C API.

Risks: Requires a live cluster and may be timing-sensitive for watches and locality. Options and timeout defaults must be reset by subtests. Generator behavior assertions depend on selected API version.

Test signals: Successful full sequence, exact option invocation coverage, watch readiness transitions, locality consistency, predicate truth values, client status with `Healthy: true`, and propagated failure descriptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/tests/unit_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/CMakeLists.txt -->
# sources/storage-engines/foundationdb/bindings/ruby/CMakeLists.txt

Purpose: This CMake file builds and packages the Ruby FoundationDB binding.

Important APIs and types: It uses `vexillographer_compile` to generate `lib/fdboptions.rb`, `configure_file` to produce `fdb.gemspec` and copy `LICENSE`, custom copy commands for Ruby source files, `ruby_binding` and `gem_package` targets, and the parent `packages` target dependency.

Control flow: CMake generates options, configures gem metadata, copies listed source files into the binary bindings tree, then builds a `.gem` with `GEM_COMMAND build` and copies it to the packages directory with a snapshot suffix when not a release.

State and persistence behavior: It writes generated option code in the source dir for debugging, copies binding files into the build dir, and writes package artifacts under `${CMAKE_BINARY_DIR}/packages`.

Dependencies and integration points: It depends on the FoundationDB CMake build, `GEM_COMMAND`, generated option metadata, package target conventions, and the Ruby source file list.

Risks: The source list must stay synchronized with gemspec file lists and actual library files. Generating into the source directory can dirty worktrees. Snapshot naming depends on `FDB_RELEASE`.

Test signals: A successful build should produce copied Ruby library files, generated `fdboptions.rb`, configured gemspec, and a gem package target that participates in `packages`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/fdb.gemspec.cmake -->
# sources/storage-engines/foundationdb/bindings/ruby/fdb.gemspec.cmake

Purpose: This is the CMake-configured Ruby gemspec template used during build packaging.

Important APIs and types: It defines `Gem::Specification` fields including name `fdb`, version `${FDB_VERSION}`, current date, summary/description, authors/email, file list, homepage, Apache-2.0 license, dependency on `ffi`, Ruby version `>= 1.9.3`, and a client-library requirement note.

Control flow: CMake substitutes `${FDB_VERSION}` and writes `fdb.gemspec`; RubyGems then reads it during `gem build`.

State and persistence behavior: It affects gem metadata and packaged file list, not runtime behavior.

Dependencies and integration points: It must match `CMakeLists.txt` source copying and Ruby library `require_relative` paths. It depends on RubyGems and the `ffi` gem.

Risks: The file list must be updated when Ruby binding files change. The broad `ffi` version range reflects legacy support and may need review for newer Ruby/platform combinations.

Test signals: `gem build fdb.gemspec` should include all runtime files and expose the substituted FoundationDB version.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/fdb.gemspec.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/fdb.gemspec.in -->
# sources/storage-engines/foundationdb/bindings/ruby/fdb.gemspec.in

Purpose: This is a Ruby gemspec input with placeholder version text for the FoundationDB Ruby binding.

Important APIs and types: It mirrors the configured gemspec fields but uses `VERSION` instead of the CMake `${FDB_VERSION}` variable.

Control flow: Packaging or release tooling can substitute the placeholder before building a gem. Runtime code does not read this file.

State and persistence behavior: It only controls package metadata and included files.

Dependencies and integration points: It must remain aligned with `fdb.gemspec.cmake`, `CMakeLists.txt`, Ruby source file names, and the dependency on `ffi`.

Risks: Divergence between `.in` and `.cmake` variants can create inconsistent package metadata. The fixed file list can omit new library files if not maintained.

Test signals: Gem build validation should confirm version substitution and complete file inclusion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/fdb.gemspec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdb.rb -->
# sources/storage-engines/foundationdb/bindings/ruby/lib/fdb.rb

Purpose: This is the Ruby binding entry point. It enforces API-version selection, loads the FFI implementation, selects the C API version, initializes function bindings, and conditionally loads tuple, directory, legacy, and locality modules.

Important APIs and types: Public module methods are `FDB.is_api_version_selected?`, `FDB.get_api_version`, and `FDB.api_version(version)`. The file uses header version `800` and handles C API error `2203` with a detailed max-supported-version message.

Control flow: `api_version` rejects multiple conflicting selections, versions below 14, and versions above the binding header. It requires `fdbimpl`, calls `FDBC.fdb_select_api_version_impl`, initializes `FDBC`, requires tuple and directory layers, loads `fdbimpl_v609` for versions below 610, and loads locality for versions above 22.

State and persistence behavior: It stores selected API version in class variable `@@chosen_version`. No database persistence occurs, but the chosen version controls all subsequent binding behavior.

Dependencies and integration points: It depends on `fdbimpl.rb`, `fdbtuple.rb`, `fdbdirectory.rb`, optional `fdbimpl_v609.rb`, optional `fdblocality.rb`, and native C API version support.

Risks: API version must be selected before normal use, and changing it later is forbidden. Header-version mismatch with installed client libraries produces startup failures.

Test signals: Ruby tester `UNIT_TESTS` verifies repeated same-version selection succeeds and conflicting selections fail with the expected message.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdb.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbdirectory.rb -->
# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbdirectory.rb

Purpose: This file implements the Ruby FoundationDB directory layer, including high-contention prefix allocation, directory metadata management, directory subspaces, and partitions.

Important APIs and types: Core classes are `HighContentionAllocator`, `DirectoryLayer`, `DirectorySubspace`, `DirectoryPartition`, and `Internal::Node`. Public directory operations include `create_or_open`, `open`, `create`, `move`, `move_to`, `remove`, `remove_if_exists`, `list`, `exists?`, and subspace methods inherited from `Subspace`.

Control flow: Directory operations run inside `db_or_tr.transact`, check or initialize directory layer version metadata, locate nodes through subdir tables, allocate prefixes with the high-contention allocator when no manual prefix is supplied, validate prefix freedom, update parent subdirectory mappings, and recurse into partitions when needed. Removal recursively clears content and node metadata.

State and persistence behavior: Persistent state lives under node subspace `\xfe` by default and content prefixes allocated by the HCA. It stores version metadata, child-name to prefix mappings, layer strings, partition metadata, and user content ranges. Runtime state includes directory paths, layer names, allocator locks, and transaction-local allocator state.

Dependencies and integration points: It depends on `fdbimpl`, `fdbsubspace`, tuple packing, atomic add mutation, transaction conflict ranges, and Ruby binding transaction semantics. `FDB.directory` exposes a singleton default layer.

Risks: Directory metadata compatibility is version-sensitive. Manual prefixes can conflict with existing content if validation fails or is bypassed. Partition routing is subtle, especially for moves and root partition operations. HCA uses randomness and transaction-local locking to reduce conflicts.

Test signals: Ruby and Python directory tester extensions cover creation/opening, layers, manual prefixes, moves, recursive removal, partitions, list/existence, packing/unpacking, range behavior, logging, and expected error flattening.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbdirectory.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbimpl.rb -->
# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbimpl.rb

Purpose: This is the main Ruby FFI implementation for FoundationDB. It loads `libfdb_c`, attaches C API functions, runs the network thread, exposes database/transaction/future abstractions, and dynamically defines options and mutations.

Important APIs and types: It defines module `FDB::FDBC`, `Error`, `Future`, `FutureNil`, `LazyFuture`, `LazyString`, `Int64Future`, `FutureKeyValueArray`, `FutureKeyArray`, `FutureStringArray`, `Database`, `TransactionRead`, `Transaction`, `KeySelector`, `KeyValue`, option classes, `FDB.open`, `FDB.options`, `FDB.stop`, `FDB.key_to_bytes`, `FDB.value_to_bytes`, and `FDB.strinc`.

Control flow: `FDBC` validates CPU/OS, loads the native client library, and attaches functions in `init_c_api`. Option classes and mutation methods are generated from `fdboptions.rb`. `FDB.open` lazily starts the network thread and caches databases by cluster file. `Database#transact` retries a yielded transaction until commit succeeds or `on_error` handles retry. Range reads use an enumerable that fetches additional batches based on `more`, limit, and reverse state.

State and persistence behavior: Runtime state includes callback arrays, network thread monitor, open database cache, native pointer finalizers, and lazy future values. Persistent state is only affected through C API database operations. Finalizers destroy native database/future/transaction pointers.

Dependencies and integration points: It depends on the `ffi` gem, generated `fdboptions`, Ruby threading/monitor primitives, native `libfdb_c`, and entrypoint version selection from `fdb.rb`. Tuple, locality, directory, and tester code build on it.

Risks: FFI signatures, pointer ownership, finalizer timing, and callback lifetime are critical. `FutureKeyArray#wait` appears to allocate `ks` but calls `fdb_future_get_key_array` with `kvs`, a likely bug if this path is exercised. Network startup must avoid races between setup and run. The database cache keying and finalizers are process-local.

Test signals: Ruby tester operations cover reads/writes/ranges, atomic ops, futures, watches, options, transaction retry, locality, directory layer, and API-version guards.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbimpl.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbimpl_v609.rb -->
# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbimpl_v609.rb

Purpose: This compatibility shim restores pre-6.1 Ruby binding APIs for older selected API versions.

Important APIs and types: It aliases `FDB.open` to accept an optional database name, exposes `create_cluster`, defines `ClusterOptions`, and defines `Cluster#open_database`.

Control flow: When loaded for API versions below 610, it wraps `FDB.open` so database names other than `DB` raise error `2013`, and cluster objects delegate opening back to `FDB.open`.

State and persistence behavior: It stores a cluster file path in `Cluster`; no additional persistence is introduced.

Dependencies and integration points: Loaded conditionally by `fdb.rb` after `fdbimpl`. It preserves old binding code that expects clusters and named database calls.

Risks: It deliberately supports only the default database name. Publicly exposing `init` for legacy behavior can widen lifecycle control.

Test signals: Compatibility is covered indirectly by binding tester runs at older API versions and by attempts to open non-default database names.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbimpl_v609.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdblocality.rb -->
# sources/storage-engines/foundationdb/bindings/ruby/lib/fdblocality.rb

Purpose: This module implements Ruby locality helpers for storage-server address lookup and shard boundary iteration.

Important APIs and types: `FDB::Locality.get_addresses_for_key(db_or_tr, key)` returns a `FutureStringArray`. `get_boundary_keys(db_or_tr, bkey, ekey)` returns an `Enumerator` over decoded boundary keys.

Control flow: Address lookup wraps the call in `transact`. Boundary lookup creates a transaction or read-version-aligned transaction, sets system-key and lock-aware options, scans `\xff/keyServers/`, yields suffixes, and handles `transaction_too_old` by creating a new transaction after partial progress or calling `on_error` otherwise.

State and persistence behavior: It reads system-key metadata but does not persist user data. Long boundary scans can lose strict transactionality after progress and retry.

Dependencies and integration points: It depends on `fdbimpl` C functions, transaction options, `FutureStringArray`, and `FDB.strinc`-style key handling. Ruby tester locality tests exercise it.

Risks: The fixed system key prefix length and system-key access assumptions must match FoundationDB internals. In the transaction branch, `tr.set_read_version db_or_tr.get_read_version` passes a future-like object unless coercion is implicit, so this path is sensitive to Ruby lazy future conversion.

Test signals: Ruby tester `test_locality` verifies boundary key addresses are consistent across shard start/end points.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdblocality.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbsubspace.rb -->
# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbsubspace.rb

Purpose: This file implements Ruby subspaces: tuple-encoded key prefixes with helper methods for packing, unpacking, ranges, and nesting.

Important APIs and types: `FDB::Subspace` exposes `raw_prefix`, `[]`, `key`, `pack`, `unpack`, `range`, `contains?`, `as_foundationdb_key`, and `subspace`.

Control flow: Initialization concatenates a binary raw prefix with packed tuple prefix. Child subspaces append one tuple element. `pack` concatenates raw prefix with tuple packing; `unpack` validates prefix containment and decodes the suffix; `range` prepends prefix to tuple-layer range bounds.

State and persistence behavior: Only `@raw_prefix` is stored. Generated prefixes and keys define persistent application key layout.

Dependencies and integration points: It depends on `fdbtuple` and is used heavily by the Ruby directory layer and binding tester directory operations.

Risks: Prefix overlap and encoding mismatches can cause logical namespace collisions. Ruby string encoding must remain binary for raw key correctness.

Test signals: Directory tester operations cover subspace creation, nested opening, pack/unpack, range, containment, and use as FoundationDB keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbsubspace.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbtuple.rb -->
# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbtuple.rb

Purpose: This module implements the Ruby FoundationDB tuple layer, preserving sortable binary encoding for common Ruby values.

Important APIs and types: Public surface includes `FDB::Tuple.pack`, `unpack`, `range`, `compare`, `UUID`, and `SingleFloat`. It supports nil, binary/ASCII strings, UTF-8 strings, integers, booleans, single and double floats, UUIDs, and nested arrays.

Control flow: `encode` dispatches by Ruby class and string encoding, escapes null bytes, encodes variable-length integers, adjusts floats for lexicographic order, and recursively encodes arrays. `decode` parses type codes and reconstructs Ruby values. `compare` orders tuples element-by-element using type codes and special float comparison.

State and persistence behavior: The module is stateless except class variables for constants and size limits. Its packed bytes are persistent keys, so compatibility with other bindings is critical.

Dependencies and integration points: It is required by `fdbsubspace`, `fdbdirectory`, and `tester.rb`. It must remain compatible with Python and other binding tuple layers.

Risks: Ruby string encodings distinguish bytes and UTF-8 strings, so callers must force binary where needed. Versionstamp support is absent here compared with the Python tuple layer. Float edge cases and integer bounds are compatibility-sensitive.

Test signals: Ruby tester tuple operations pack/unpack/sort/range values and encode/decode floats. Cross-binding tester comparisons validate ordering and binary compatibility for supported types.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/lib/fdbtuple.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/tests/directory_extension.rb -->
# sources/storage-engines/foundationdb/bindings/ruby/tests/directory_extension.rb

Purpose: This is the Ruby binding tester adapter for directory-layer and subspace instructions.

Important APIs and types: `DirectoryExtension::DirectoryTester` maintains a directory handle list, active index, and error index. It processes directory create/open/move/remove/list/exists, subspace creation/opening, pack/unpack/range/contains, logging, and prefix stripping instructions.

Control flow: Each instruction pops values from the tester stack using `wait_and_pop`, invokes the current directory/subspace object, pushes normalized results, and appends new handles for operations that create or open directories. Exceptions append `nil` for create-like operations and push `DIRECTORY_ERROR`.

State and persistence behavior: Runtime state is the directory handle table. Persistent state is mutated through `FDB::DirectoryLayer` operations and log writes requested by the instruction stream.

Dependencies and integration points: It depends on `fdb`, `FDB::Tuple`, `FDB::Subspace`, `FDB::DirectoryLayer`, and the `Instruction` protocol in `ruby/tests/tester.rb`. It mirrors Python's directory extension for conformance testing.

Risks: Stack pop order, tuple path conversion, and error normalization must match the tester spec exactly. Throwing versus raising in prefix-strip failure is a minor Ruby-specific behavior to watch.

Test signals: Directory instruction streams validate Ruby directory semantics against other bindings, including manual prefixes, partitions, moves, removals, listing, key conversion, and error cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/tests/directory_extension.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/tests/tester.rb -->
# sources/storage-engines/foundationdb/bindings/ruby/tests/tester.rb

Purpose: This is the Ruby binding tester runner. It executes tuple-encoded test instructions stored in FoundationDB and normalizes Ruby binding behavior for cross-language comparison.

Important APIs and types: `Stack` resolves futures and errors, `Instruction` wraps operation context, and `Tester` manages instruction iteration, transactions, threads, range packing, stack logging, watch/locality unit tests, and directory extension dispatch.

Control flow: Startup loads local library files, selects the requested API version, opens the database, then reads instructions under a tuple range. `Tester#run` decodes each operation, selects database/current transaction/snapshot target by suffix, executes database, transaction, tuple, directory, threading, and embedded unit-test operations, and catches `FDB::Error` as packed error tuples.

State and persistence behavior: It keeps in-memory stacks, a transaction map protected by a monitor, last read/committed version, child threads, and directory tester state. Persistent effects are whatever the instruction stream requests plus `LOG_STACK` output.

Dependencies and integration points: It depends on `fdb`, `fdbtuple`, `fdblocality`, `directory_extension`, Ruby threads/monitor, and the live FoundationDB cluster. It is the primary broad integration test for the Ruby binding.

Risks: Requires a live cluster and exact agreement with the binding tester instruction spec. Some operations rely on Ruby lazy futures converting through `to_s`/numeric methods. Embedded unit tests are timing-sensitive for watches and locality.

Test signals: It covers API-version guards, options, reads/writes/ranges/selectors, atomic ops, conflict ranges, commits/resets/cancel, approximate size, versionstamps, tuple operations, directory semantics, watches, locality, stack logging, and concurrent tester threads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/ruby/tests/tester.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/AddFdbServerLinkTest.cmake -->
# sources/storage-engines/foundationdb/cmake/AddFdbServerLinkTest.cmake

Purpose: This CMake helper defines reusable functions for FoundationDB server link tests and unit-test executables.

Important APIs and types: `add_fdbserver_link_test(target_name ...)` creates a Flow target using `fdbclient/LinkTest.cpp` and links the primary library with whole-archive semantics plus remaining libraries and `rapidxml`. `add_fdbserver_unit_test(target_name source_subdir ...)` creates an executable target using `fdbserver/FDBServerUnitTestMain.cpp`, sets `EXCLUDE_FROM_ALL`, defines `FDBSERVER_UNIT_TEST_SUITE`, and links similarly.

Control flow: Both functions treat the first variadic library argument as `primary_lib`, remove it from the list, compute a relative source path from the current source directory, create a target, then link with `$<LINK_LIBRARY:WHOLE_ARCHIVE,...>`.

State and persistence behavior: It creates CMake targets and compile definitions only; no runtime persistence.

Dependencies and integration points: It depends on the project `add_flow_target` macro, server/client test source files, whole-archive linker support through CMake generator expressions, and `rapidxml`.

Risks: Calls without at least one library will fail at `list(GET)`. Whole-archive behavior is linker/platform-sensitive. Unit-test suite selection depends on `source_subdir` matching registration in server unit-test code.

Test signals: Configure/build success for generated link-test and unit-test targets, correct source resolution, and successful link against whole-archived primary libraries are the key signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/AddFdbServerLinkTest.cmake -->
