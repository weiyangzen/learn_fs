# Research Group subset-b-008397

This grouped report covers FoundationDB contrib metadata audit bindings/tools, monitoring helpers, mTLS benchmark wrappers, and Splunk dashboard XML. Each section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/directory_impl.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/directory_impl.py

## Purpose
This module is the local FoundationDB Python directory layer implementation vendored for the metadata audit tools. It maps human directory paths to binary key prefixes, allocates short unique prefixes under contention, supports directory creation/open/list/move/remove, and exposes opened directories as `Subspace` objects.

## Important APIs, Types, And Functions
`HighContentionAllocator.allocate()` chooses a unique tuple-packed integer prefix using counter windows under `hca` metadata, snapshot reads, no-conflict writes to recent candidate keys, and explicit write conflict keys for winners. `Directory` is the user-facing wrapper with transactional `create_or_open`, `open`, `create`, `list`, `move`, `move_to`, `remove`, `remove_if_exists`, and `exists` methods that delegate into a `DirectoryLayer`.

`DirectoryLayer` owns node metadata and implements `_create_or_open_internal`, `move`, `_remove_internal`, `list`, `exists`, `_find`, `_remove_recursive`, `_is_prefix_free`, and version initialization. `DirectorySubspace` combines content prefix packing with directory operations. `DirectoryPartition` creates a nested `DirectoryLayer` under a directory prefix and intentionally disables packing on the partition root. `_Node` caches metadata for lookup and partition dispatch.

## Control Flow
Opening or creating starts with `_check_version`, normalizes paths through `_to_unicode_path`, walks node metadata from the root via `_find`, and either returns existing contents, delegates into a partition, or allocates/writes a new node. Automatic prefix allocation uses `content_subspace.key() + allocator.allocate(tr)` and then checks both actual database keys and directory prefix metadata for collisions. Parent directories are created recursively through `create_or_open(path[:-1])` when needed.

Move validates that the destination is not a subdirectory of the source, resolves both endpoints, rejects cross-partition moves, writes the old node prefix into the new parent's subdir map, and removes the old parent entry. Remove recursively clears child nodes, clears all keys under the content prefix, and deletes node metadata.

## State And Persistence Behavior
Directory layer state is stored in system-neutral user keyspace: root node metadata under the default node subspace `b"\xfe"`, directory node metadata keyed by physical content prefix, child name-to-prefix mappings under subkey `0`, layer labels under `b"layer"`, and a packed version tuple in `b"version"`. Directory contents live at the allocated physical prefixes. Removing a directory clears both content data and metadata, but already-open clients can continue writing to the removed prefix because the returned subspace is just bytes.

The allocator stores counters and recent candidate markers under the root node's `b"hca"` subspace. It advances windows when counters show a window is more than half full, then suppresses some write conflict ranges while adding conflict only on the chosen candidate.

## Dependencies And Integration Points
The module depends on `fdb.impl.transactional`, `fdb.tuple`, and `Subspace`. It is a compatibility layer for Python bindings used by metadata scripts or other tools that expect `fdb.directory`. It integrates with tuple ordering for paths and prefix allocation, transaction conflict semantics for allocator correctness, and `impl.strinc` for prefix-range checks.

## Risks And Edge Cases
This is low-level prefix management: manual prefixes can overlap real data if `_allow_manual_prefixes` is enabled or if callers supply stale prefixes. Recursive remove is destructive over the entire content prefix. Partition roots intentionally reject subspace packing, which can surprise code treating every directory as a key prefix. Prefix allocation depends on randomized retries and transaction conflict behavior; changes to no-conflict range semantics can break uniqueness assumptions. Version checks only guard major/minor directory layer compatibility, not schema corruption inside metadata keys.

## Test Signals
Useful tests cover creating/opening nested directories, layer mismatch rejection, automatic and manual prefix collision rejection, move within and across partitions, recursive remove clearing metadata and contents, allocator uniqueness under concurrent transactions, and path normalization from bytes/strings. Partition tests should verify delegation and root operation restrictions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/directory_impl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/fdboptions.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/fdboptions.py

## Purpose
This generated-style module is the data table behind the local FDB Python binding. It defines numeric option, enum, mutation, and error-predicate constants plus documentation and parameter type metadata used by `impl.py` to create methods dynamically.

## Important APIs, Types, And Functions
The primary objects are dictionaries: `NetworkOption`, `DatabaseOption`, `TransactionOption`, `StreamingMode`, `MutationType`, `ConflictRangeType`, and `ErrorPredicate`. Each entry maps a symbolic name to `(code, description, parameter_type, parameter_description)`.

Notable options include TLS configuration, external client libraries, client threading, transaction timeouts/retry limits/size limits, system-key and lock-aware access, read priority, special key space writes, tracing tags, GRV cache, authorization token, and replica consistency check settings. `MutationType` includes arithmetic/bitwise atomics, byte min/max, compare-and-clear, and versionstamped key/value operations.

## Control Flow
There is no runtime control flow beyond module import. `impl.fill_options`, `impl.make_enum`, and `impl.fill_operations` iterate over these dictionaries to attach `set_*` methods to network/database/transaction option wrappers, expose streaming/conflict constants as properties, attach error predicate helpers, and add mutation helpers to `Database` and `Transaction`.

## State And Persistence Behavior
The module itself is stateless, but its constants control persistent and network-affecting behavior in the FDB C API. Several options directly enable system-key writes, lock awareness, transaction durability modes, timeouts, retries, tracing, TLS files, and mutation opcodes that alter database values at commit time.

## Dependencies And Integration Points
It is imported by `fdb.impl`. The `paramType` values must match the wrapper conversion logic in `option_wrap*`; a mismatch causes generated methods to pass incorrectly encoded C API parameters. The option codes must match the linked `libfdb_c` version.

## Risks And Edge Cases
Because this file is a hand/generated compatibility table, stale numeric codes are dangerous: wrong codes can silently set unrelated options or mutation types. Some keys include deprecated aliases, duplicate code values, or options gated by API version, so callers can see runtime C API errors despite method presence. System-key and lock-aware options are intentionally powerful and must not be exposed casually in high-level tools.

## Test Signals
Tests should import the binding, confirm expected methods are generated, verify parameter type validation for no-arg/string/bytes/int options, and exercise a small set of known C API options against a compatible client library. Static tests can compare codes with generated binding metadata from the same FDB version.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/fdboptions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/impl.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/impl.py

## Purpose
This is a vendored FoundationDB Python binding implemented with `ctypes` over `libfdb_c`. It loads the client library, initializes the C API, starts/stops the network thread, exposes database/transaction/future abstractions, implements transactional retry wrappers, and dynamically attaches options, predicates, enums, and atomic mutation methods.

## Important APIs, Types, And Functions
Dynamic method generation is handled by `fill_options`, `make_enum`, and `fill_operations` using `fdboptions.py`. `transactional` wraps functions so calls with a `Database` create a transaction, retry on `FDBError` through `on_error`, commit, and return the function result; calls with an existing `TransactionRead` compose without committing.

Core types include `FDBError`, `FDBRange`, `TransactionRead`, `Transaction`, `Future` and specialized futures (`FutureVoid`, `FutureInt64`, `FutureKeyValueArray`, `FutureKeyArray`, `FutureStringArray`, `FutureString`, `Value`, `Key`), `_TransactionCreator`, `Database`, `Cluster`, `KeySelector`, and `KeyValue`. Public open/init helpers are `init`, `open`, `open_v609`, `open_v13`, `create_database`, `create_cluster`, and `strinc`.

`init_c_api()` declares C function signatures and error checking for network, future, database, tenant compatibility shims, transaction reads/writes, watches, conflict ranges, approximate size, versionstamps, and range split APIs.

## Control Flow
At import, the module selects a platform-specific library name, tries a colocated library, a `.pth` pointer, then dynamic loader lookup, and assigns it to `_FDBBase.capi`. Dynamic option and mutation methods are installed. Callers select an API version outside this file, then `open()` initializes the network if needed, caches a `Database` by cluster file, and returns it.

Transactions flow through `Database.create_transaction()` to a `Transaction` sharing one C pointer with its snapshot `TransactionRead`. Reads return futures or `FDBRange` iterators. `FDBRange` eagerly dispatches the first range read and lazily requests additional batches using key selectors. Mutations call direct C API methods and commits return `FutureVoid`.

Futures block in Python using callbacks and per-thread semaphores rather than native blocking, so Python signals can still be handled. Optional event models replace blocking behavior for gevent, debug polling, or asyncio.

## State And Persistence Behavior
Persistent database changes happen only through transaction mutations: `set`, `clear`, `clear_range`, atomic ops, conflict range operations, watches, commits, and versionstamp operations. Module-level runtime state includes the global network thread, `open_databases` cache, callback pinning state, and a thread-local semaphore. `open()` reuses database handles for each cluster file; `_stop_on_exit` stops the global network and joins the thread.

The wrapper enforces bytes-only keys/values through `keyToBytes` and `valueToBytes`, while option parameters may encode strings to UTF-8. Snapshot reads share the transaction pointer but set the snapshot flag in C API calls.

## Dependencies And Integration Points
This file depends on a 64-bit Python runtime, `ctypes`, `fdb.tuple`, `fdboptions`, and a compatible `libfdb_c`. Metadata audit tools depend on `fdb.api_version`, `fdb.open`, `fdb.transactional`, transaction option helpers, and system-key access exposed here. It also integrates with asyncio/gevent by monkey-patching future behavior and `_TransactionCreator` methods.

## Risks And Edge Cases
The binding is tightly coupled to C API symbol availability and exact signatures; a mismatched client library can fail at import or behave incorrectly. `Database.open_tenant` is a temporary compatibility shim that returns `None`, so tenant callers cannot rely on it. `transactional` may rerun user code multiple times, making side effects outside FDB unsafe. `open_databases` never evicts handles. The destructor-based cleanup of C objects depends on Python GC timing. Async code references `asyncio` only after event-model setup.

## Test Signals
Strong tests load a known `libfdb_c`, set an API version, open a test cluster, execute get/set/clear/range operations, verify retry behavior through injected retryable errors, and validate future callbacks and `wait_for_any`. Compatibility tests should exercise system-key options used by metadata tools, `strinc`, dynamic option/mutation method presence, and import failure paths for missing libraries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/impl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/locality.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/locality.py

## Purpose
This module provides locality helpers for the Python binding: boundary-key iteration for key ranges and storage-server address lookup for a key. These are low-level inspection utilities used to understand data placement.

## Important APIs, Types, And Functions
`get_boundary_keys(db_or_tr, begin, end)` returns a generator over boundary keys in `[begin, end)`. `_get_boundary_keys` performs the actual scan of `\xff/keyServers/<user-key>` system metadata. `get_addresses_for_key(tr, key)` is transactional and wraps `fdb_transaction_get_addresses_for_key` in a `FutureStringArray`.

## Control Flow
Boundary-key reads create a new transaction. If called with a transaction, the helper starts a separate transaction and copies the caller's read version to approximate consistency. It sets `read_system_keys` and `lock_aware`, scans the keyServers system subspace, yields `None` once to dispatch the first range before returning the generator, then yields stripped user boundary keys and advances by appending `b"\x00"`. Retryable errors are handled with `on_error`; a `transaction_too_old` after partial progress starts a new transaction and loses strict transactionality.

## State And Persistence Behavior
The module is read-only. It reads system keys under `\xff/keyServers/` and uses transaction options that permit system-key reads on locked databases. No persistent writes are issued.

## Dependencies And Integration Points
It depends on `fdb.impl` transaction classes, `keyToBytes`, and `FutureStringArray`. It integrates with the FDB C locality API for address lookups and with the keyServers metadata layout for boundary-key enumeration.

## Risks And Edge Cases
Boundary-key iteration is explicitly not guaranteed transactional after some `transaction_too_old` cases. It assumes the keyServers prefix string length when stripping `kv.key[13:]`; layout changes would break results. The generator returns no values when `begin >= end`. System-key reads require sufficient API version and transaction options.

## Test Signals
Tests should verify boundary keys for known split ranges, behavior with both `Database` and `Transaction` inputs, retry behavior across transaction-too-old cases, byte validation for begin/end, and address lookup returning a string array future for a populated key.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/locality.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/subspace_impl.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/subspace_impl.py

## Purpose
This module implements the Python tuple subspace abstraction: a stable byte prefix plus helpers for packing/unpacking tuple keys and ranges under that prefix.

## Important APIs, Types, And Functions
`Subspace.__init__(prefixTuple=(), rawPrefix=b"")` computes `rawPrefix` with `fdb.tuple.pack`. `__getitem__` and `subspace()` derive child subspaces. `key`, `pack`, `pack_with_versionstamp`, `unpack`, `range`, `contains`, and `as_foundationdb_key` provide the key-building API used by directory and metadata code.

## Control Flow
The class is simple and immutable in practice. Construction packs a tuple under a raw prefix. Packing appends a tuple encoding to `rawPrefix`; unpacking first checks that the key starts with the prefix, then calls `fdb.tuple.unpack` with a prefix offset. Range construction delegates to `fdb.tuple.range` and then prepends `rawPrefix` to the resulting start/stop.

## State And Persistence Behavior
`Subspace` holds only an in-memory byte prefix. It does not read or write FDB, but its output controls which persistent keys callers read, write, or clear. Incorrect prefixes can redirect destructive operations to the wrong key range.

## Dependencies And Integration Points
It depends entirely on `fdb.tuple`. `DirectoryLayer`, application code, and transaction helpers can pass `Subspace` instances wherever `as_foundationdb_key` is accepted by `impl.keyToBytes`.

## Risks And Edge Cases
`unpack` raises when the key is outside the subspace. `range()` returns all tuple extensions of a tuple, not arbitrary prefix bytes, which matters for callers expecting raw byte prefix behavior. Versionstamp packing requires exactly one incomplete versionstamp through the tuple layer.

## Test Signals
Tests should cover nested subspaces, byte prefix containment, round-trip pack/unpack, range start/stop correctness, rejection of keys outside the subspace, and versionstamp packing behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/subspace_impl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/tuple.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/tuple.py

## Purpose
This module implements FoundationDB tuple layer encoding for Python. It converts Python values into lexicographically ordered byte strings suitable for keys, decodes tuple keys, supports versionstamp packing, computes tuple subranges, and compares tuples using FDB tuple ordering.

## Important APIs, Types, And Functions
Public APIs are `pack`, `pack_with_versionstamp`, `unpack`, `has_incomplete_versionstamp`, `range`, and `compare`. Public value types are `SingleFloat` for 32-bit float encoding and `Versionstamp` for complete or incomplete transaction versionstamps.

Internal helpers include `_encode`, `_decode`, `_pack_maybe_with_versionstamp`, `_find_terminator`, `_float_adjust`, `_reduce_children`, `_code_for`, `_compare_floats`, and `_compare_values`. Type codes cover null, bytes, string, nested tuple/list, integers, floats/doubles, booleans, UUIDs, and versionstamps.

## Control Flow
Encoding dispatches by Python type. Bytes and strings escape embedded nulls and terminate with null. Integers encode around `INT_ZERO_CODE` with variable-width positive/negative encodings, including extended 9-255 byte forms. Floats flip sign bits or invert negative bytes to preserve numeric order. Nested tuples recursively encode children and use a special nested-null representation. Versionstamp packing tracks the single incomplete position and appends a little-endian offset of two bytes for old API versions or four bytes for newer versions.

Decoding reads one type code at a time from the byte stream and reconstructs values until the key ends. `range(t)` returns the slice between packed tuple plus `0x00` and packed tuple plus `0xff`, matching tuple-extension range semantics. `compare` uses tuple type code ordering and special float handling for negative zero, NaN, and infinities.

## State And Persistence Behavior
The module is stateless. Its encoded bytes define persistent key ordering for all higher-level code using tuple/subspace/directory abstractions. Versionstamp packing is intended for FDB atomic versionstamp mutations where the final offset bytes are interpreted at commit time.

## Dependencies And Integration Points
It depends on `ctypes`, `uuid`, `struct`, `math`, and the top-level `fdb` module for API-version behavior and `fdb.impl.Value` coercion in `Versionstamp.to_bytes`. `subspace_impl.py` and `directory_impl.py` rely on these encodings for all logical-to-physical key mapping.

## Risks And Edge Cases
Tuple encoding is compatibility-critical; any code-point or ordering change corrupts range scans and directory keys. Boolean handling changes with API version before 500. Only one incomplete versionstamp is allowed. Float comparison handles unusual values but can differ from Python's native NaN semantics. `_decode` raises on unknown type codes and can fail on malformed/truncated keys. The module shadows built-in `range` with tuple range after saving `_range`.

## Test Signals
Tests should include FDB tuple spec vectors, round trips for all supported types, ordering comparisons against packed byte order, nested tuples containing `None`, embedded null bytes, very large positive/negative integers, `SingleFloat`, NaN/negative-zero cases, UUIDs, complete and incomplete versionstamps, API-version gated boolean behavior, and prefix range boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/tuple.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb_metadata_utils.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb_metadata_utils.py

## Purpose
This module centralizes shared constants and safety helpers for metadata audit scripts that read or write FoundationDB system metadata. It selects an API version, defines key prefixes for `serverKeys`, `serverList`, and `keyServers`, and implements MoveKeysLock management required before modifying key-range metadata.

## Important APIs, Types, And Functions
Constants include `SERVER_KEYS_PREFIX`, `SERVER_LIST_PREFIX`, `KEY_SERVERS_PREFIX`, matching end keys, `DD_MODE_KEY`, `MOVEKEYS_LOCK_OWNER_KEY`, `MOVEKEYS_LOCK_WRITE_KEY`, `SERVER_KEYS_TRUE`, and `SERVER_KEYS_FALSE`.

`take_movekeys_lock(db)` disables data distribution, records the previous DD mode, writes a random owner UID and write key, and returns the owner plus previous mode. `release_movekeys_lock(db, prev_dd_mode_value)` restores DD mode and randomizes lock keys. `update_movekeys_lock_write(tr)` updates the write key inside metadata write transactions. `set_write_transaction_options` and `set_read_transaction_options` apply access-system/read-system, lock-aware, timeout, and priority options. `_encode_dd_mode`, `_decode_dd_mode`, `_encode_uid`, and `strinc` support serialization and range boundaries.

## Control Flow
At import, the module attempts API versions `[740, 730, 720, 710, 700]` until one succeeds, failing hard if none do. Lock acquisition and release are transactional functions with system-key access and system-immediate priority. Metadata writers call `take_movekeys_lock`, perform batches while updating the lock write key, and call `release_movekeys_lock` in a `finally` path.

## State And Persistence Behavior
This module writes critical system keys: `\xff/dataDistributionMode`, `\xff/moveKeysLock/Owner`, and `\xff/moveKeysLock/Write`. Disabling DD has cluster-wide operational impact. It does not write KRM entries directly, but it prepares transactions that repair/restore scripts use to mutate `serverKeys`, `serverList`, and `keyServers`.

## Dependencies And Integration Points
It depends on the local `fdb` Python binding, `struct`, and `uuid`. `repair_coalesce.py` and `restore_metadata.py` import it. The comments tie behavior to FDB internal `MoveKeys.actor.cpp`, so correctness depends on current internal lock semantics.

## Risks And Edge Cases
Import-time API selection can mask version mismatches until a later operation fails. If a process dies after `take_movekeys_lock` and before release, DD may remain disabled or lock ownership stale. `_decode_dd_mode` is unused by current scripts but documents default handling. The custom `strinc` returns `key + b"\x00"` for all-0xff keys, which differs from some strict prefix-end expectations but is not used on all-0xff metadata prefixes.

## Test Signals
Unit tests can validate encoders, UID byte length, prefix end keys, and transaction option calls with fakes. Integration tests should run dry-run paths and, in an isolated cluster, verify lock acquisition disables DD, release restores previous mode, and each metadata write batch updates the lock write key.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb_metadata_utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/metadata-audit.sh -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/metadata-audit.sh

## Purpose
This shell wrapper provides a single entry point for metadata audit, backup, restore, and coalesce repair commands. It locates `libfdb_c`, finds an importable Python `fdb` package, ensures a cluster file is supplied or discoverable, then `exec`s the selected Python script.

## Important APIs, Types, And Functions
The command map supports `check`, `backup`, `restore`, and `repair-coalesce`, dispatching to `check_krm_corruption.py`, `backup_metadata.py`, `restore_metadata.py`, and `repair_coalesce.py`. Wrapper options are `--fdb-lib`, `--fdb-python`, and help. Environment inputs are `FDB_CLUSTER_FILE`, `FDB_LIB_PATH`, and `FDB_PYTHON_PATH`.

`find_fdb_lib` searches explicit flags, env vars, existing loader paths, build outputs, and standard library dirs for `libfdb_c.so` or `libfdb_c.dylib`. `find_fdb_python` searches explicit paths, env vars, current importability, build output bindings, lib-adjacent Python dirs, the script directory, and site-packages.

## Control Flow
The script uses `set -euo pipefail`, parses wrapper options before the command, maps command to script, locates and exports the dynamic library path, locates and prepends the Python binding path, prepends `SCRIPT_DIR` so shared utilities import, checks whether `-C/--cluster-file` appears in remaining args, and if not looks for `FDB_CLUSTER_FILE`, `/etc/foundationdb/fdb.cluster`, or `$HOME/.fdb/fdb.cluster`. It ends with `exec python3 "$SCRIPT" "$@"`.

## State And Persistence Behavior
The wrapper itself writes no persistent state. It changes process environment variables (`LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH`, `PYTHONPATH`) for the executed Python process. The selected Python command may read or mutate FDB metadata.

## Dependencies And Integration Points
It depends on Bash, `python3`, FoundationDB build/install layouts, and the sibling metadata audit Python scripts. It is the operational integration layer for users who may have built libraries rather than installed Python packages.

## Risks And Edge Cases
Wrapper options must precede the command; command-specific options after the command are not validated by the wrapper. The cluster-file check only detects presence of `-C` or `--cluster-file`, not whether the following value is valid. `DYLD_LIBRARY_PATH` can be restricted by macOS SIP for some child processes. The default search can accidentally pick a system `fdb` Python package incompatible with the selected `libfdb_c`.

## Test Signals
Shell tests should cover help, unknown wrapper option, unknown command, explicit and env library/Python paths, default cluster-file discovery, missing library/module/cluster diagnostics, and final `exec` argument preservation. Integration tests can run `check --dry`-style commands if available against a test cluster.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/metadata-audit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/repair_coalesce.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/repair_coalesce.py

## Purpose
This script repairs uncoalesced `serverKeys` or `keyServers` metadata by deleting adjacent redundant entries while preserving the first key in each run. It is designed to be idempotent and supports dry-run inspection before destructive system-key edits.

## Important APIs, Types, And Functions
`decode_key_servers_value(v)` extracts source and destination storage server UID sets from serialized `keyServers` values after an 8-byte protocol header. `get_value_key(entry_type, value)` normalizes values for equality checks. `get_live_server_uids(db)` reads `serverList`. `read_entries_batched` scans metadata ranges in batches. `find_redundant_entries(entries, entry_type)` implements the coalescing algorithm. `delete_keys_batched` clears redundant keys. `coalesce_serverkeys` and `coalesce_keyservers` drive each repair type. `main` handles CLI, confirmation, lock acquisition, and summary.

## Control Flow
The CLI requires `--type serverKeys|keyServers` and either `--dry-run` or `--yes-i-am-sure`. Non-dry-run mode disables DD and takes MoveKeysLock via `fdb_metadata_utils`. For `serverKeys`, it reads live server UIDs, optionally filters by `--server`, scans each `\xff/serverKeys/<uid>` range, and deletes duplicate adjacent TRUE/FALSE entries. For `keyServers`, it scans `\xff/keyServers/` or a hex prefix and deletes adjacent entries whose decoded source/destination server sets match. A `finally` block releases the lock unless `--keep-dd-disabled` is set.

## State And Persistence Behavior
Dry-run mode reads only. Write mode mutates FDB system keys by clearing redundant entries under `serverKeys` or `keyServers`, and also writes MoveKeysLock/DD mode keys during lock lifecycle. Deletions are batched in transactions of 100 keys and each write transaction updates the MoveKeysLock write key.

## Dependencies And Integration Points
It depends on `fdb`, `argparse`, `struct`, `sys`, and shared metadata utility functions/constants. It integrates with FDB KRM semantics where each metadata key marks the start of a range and adjacent equal-value records are redundant.

## Risks And Edge Cases
This is destructive system-key repair. If `decode_key_servers_value` returns empty sets for malformed values, distinct corrupt entries may compare equal and be deleted. `serverKeys` processing only scans UIDs from `serverList` unless `--server` is supplied, so stale serverKeys for absent servers are not coalesced by default. `read_entries_batched` stores all entries in memory despite batching transactions. `--keep-dd-disabled` intentionally leaves cluster-wide DD disabled for chained repairs.

## Test Signals
Unit tests should validate duplicate-run detection, first-entry preservation, keyServers value decoding, malformed decode behavior, and batching range advancement. Integration tests should run dry-run and real repair on synthetic metadata in an isolated cluster, verify idempotency on second run, and confirm lock release/restored DD mode after success and exceptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/repair_coalesce.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/restore_metadata.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/restore_metadata.py

## Purpose
This script restores FoundationDB metadata JSON backups created by the companion backup tool. It is framed as a rollback/safety-net tool for repair operations, not disaster recovery, because `serverKeys` restoration can destabilize live storage servers and cannot restore to clusters with different server UIDs.

## Important APIs, Types, And Functions
`restore_entries(db, entries, name, prefix, end, dry_run=False, batch_size=100)` validates each hex key is inside the expected metadata range and writes batches. `clear_range(db, prefix, end, name, dry_run=False)` removes current metadata before restore. `verify_backup(args, manifest, db)` loads JSON files, validates entry shape and hex encoding, and spot-checks samples against current FDB. `main` manages CLI flags, manifest loading, confirmation, target selection, MoveKeysLock lifecycle, clear-and-restore flow, and summary.

## Control Flow
`main` requires `--backup-dir` and expects `backup_manifest.json`. `--verify` exits through the verification path. Real restore requires `--yes-i-am-sure`; `--dry-run` previews without writes. The target list is either one of `serverList`, `keyServers`, `serverKeys` or all three. Non-dry-run mode takes MoveKeysLock and disables DD. For each target, it loads `<name>.json`, computes the allowed prefix/end, clears the existing range, validates all backup keys, and writes all entries in batches.

## State And Persistence Behavior
Dry-run and verify modes read only. Restore mode clears and rewrites FDB system-key ranges under `\xff/serverList/`, `\xff/keyServers/`, and/or `\xff/serverKeys/`. It also writes DD mode and MoveKeysLock keys through the shared utility module. The script restores entry bytes exactly from hex JSON after range validation.

## Dependencies And Integration Points
It depends on `fdb`, JSON backup files, `argparse`, `os`, `sys`, and `fdb_metadata_utils`. It integrates with backup manifest counts and with FDB internal metadata layouts. The long module docstring documents operational constraints and known serverKeys privatization behavior.

## Risks And Edge Cases
The workflow intentionally overwrites current metadata. `clear_range` happens before `restore_entries`; if validation fails after clearing, that metadata type can be skipped after data has already been removed in real mode. The script takes MoveKeysLock even for `serverList`-only restore, although the strict requirement is emphasized for `serverKeys/keyServers`. Spot-check verification samples at most 20 entries and is not a full equality check. ServerKeys restore can destabilize clusters or fail for dead/different server UIDs.

## Test Signals
Unit tests should cover manifest absence, JSON/hex validation, out-of-range key rejection, dry-run no-write behavior, and target prefix selection. Integration tests in disposable clusters should verify verify-mode output, restore-only `serverList`, dry-run all-target restore, lock release after exceptions, and failure behavior when restore data contains an out-of-range key.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/restore_metadata.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/monitoring/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/monitoring/CMakeLists.txt

## Purpose
This CMake fragment builds the `actor_flamegraph` monitoring helper executable from `actor_flamegraph.cpp`.

## Important APIs, Types, And Functions
It declares `add_executable(actor_flamegraph actor_flamegraph.cpp)` and links `Threads::Threads` privately.

## Control Flow
The parent CMake project includes this directory, then this fragment contributes one executable target and its thread-library dependency.

## State And Persistence Behavior
No runtime state is defined here. The persistent build artifact is the `actor_flamegraph` executable.

## Dependencies And Integration Points
It depends on the parent project having found or declared `Threads::Threads`. It integrates the standalone parser into FoundationDB contrib monitoring builds.

## Risks And Edge Cases
If the parent CMake file has not called `find_package(Threads)`, target generation can fail. The file does not set C++ standard requirements even though the source uses `unordered_map::contains`, which requires C++20.

## Test Signals
Build configuration should confirm `actor_flamegraph` is generated and linked. A compile test should verify the active C++ standard supports the source.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/monitoring/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/monitoring/actor_flamegraph.cpp -->
# sources/storage-engines/foundationdb/contrib/monitoring/actor_flamegraph.cpp

## Purpose
This standalone C++ tool converts actor trace event files into folded stack samples suitable for flamegraph-style visualization. It reconstructs actor parent stacks and accumulates run time per stack/name path.

## Important APIs, Types, And Functions
`Actor` stores an actor id, name, inherited stack, accumulated `runTime`, and `lastStart`; its destructor calls `collect()` to add a folded stack line into shared `results`. `Traces` parses files, maintains the active `currentStack`, maps actor ids to `Actor` objects, and prints aggregate results. `usage` and `main` implement the CLI.

Input event opcodes are `OP_CREATE=0`, `OP_DESTROY=1`, `OP_ENTER=2`, and `OP_EXIT=3`. Each input line must split into four semicolon-separated fields: timestamp, op, name, id.

## Control Flow
For create events, the tool creates an actor and copies the current top actor's stack plus name as parent context. Destroy erases the actor, causing destructor aggregation. Enter creates an actor if missing, pushes it on the current stack, and records start timestamp. Exit verifies the top id, accumulates elapsed time, and pops. At end-of-file, it prints `DONE`, clears active stacks and actors, then `main` prints all folded stacks and weights.

## State And Persistence Behavior
All state is in memory: actor map, active stack, and aggregate folded-stack result map. The tool reads input trace files and writes text to stdout. It does not modify input files.

## Dependencies And Integration Points
It depends on the C++ standard library and is built by the adjacent CMake file. Output format is compatible with folded stack consumers such as flamegraph scripts, where each line is `frame;frame;leaf weight`.

## Risks And Edge Cases
The source uses `std::unordered_map::contains`, requiring C++20. It includes `<stack>` but uses `std::deque` without directly including `<deque>`, relying on transitive includes. `-h` works, but the parser treats `--` as help in one branch and as end-of-args in another depending on position. Empty file list prints an error but continues and returns success after printing empty output. Malformed lines throw nonfatal `Error`, so later files may still process. Unbalanced exits only warn and may leave timing incomplete.

## Test Signals
Tests should feed create/enter/exit/destroy traces and verify folded output weights, parent stack inheritance, repeated identical frames collapsed with `(n)`, malformed-line diagnostics, unbalanced stack warnings, missing file failure, and multi-file aggregation. Build tests should enforce C++20 or avoid `contains`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/monitoring/actor_flamegraph.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/monitoring/fdb_c_version.py -->
# sources/storage-engines/foundationdb/contrib/monitoring/fdb_c_version.py

## Purpose
This script prints version information for an FDB C client library. It is a small diagnostic helper for confirming which `libfdb_c`/`fdb_c.dll`/`libfdb_c.dylib` is being loaded.

## Important APIs, Types, And Functions
`get_version_string(library_path)` loads the library with `ctypes`, selects API version 410, calls `fdb_get_client_version`, parses comma-separated version components, and returns a formatted client/source/protocol string. `error(message)` prints and exits. The CLI accepts an optional `library_path`.

## Control Flow
At startup, the script selects the default library name and loader terminology for Linux, Windows, or macOS, rejecting unsupported platforms. It parses the optional path, validates explicit files, defaults to the platform library name if omitted, and prints `get_version_string`.

## State And Persistence Behavior
The script is read-only. It loads a dynamic library into the process and calls C API functions but does not open a database or write files.

## Dependencies And Integration Points
It depends on Python `ctypes`, `argparse`, `platform`, `os`, and a compatible FDB C library. It integrates with monitoring or troubleshooting workflows where operators need to verify client binaries.

## Risks And Edge Cases
The selected API version 410 must be supported by the library. The version string parser assumes at least three comma-separated components. Loading by default name follows platform dynamic loader rules, which can find an unintended library from the environment. Error messages print byte strings directly for API selection failures.

## Test Signals
Tests should cover unsupported platform handling with mocks, explicit missing path rejection, load failure diagnostics, mocked C API version string parsing, and successful output formatting for representative client version strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/monitoring/fdb_c_version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/mtlsbenchmark/client.sh -->
# sources/storage-engines/foundationdb/contrib/mtlsbenchmark/client.sh

## Purpose
This shell script runs the client side of an mTLS handshake benchmark using `fdbserver -r unittests -f :/network/p2ptest`. It connects to a server at `127.0.0.1:4500:tls` for a fixed duration.

## Important APIs, Types, And Functions
The script invokes `/root/build_output/bin/fdbserver` under `taskset -c 0-0`. Important test arguments are `--test_remoteAddresses=127.0.0.1:4500:tls`, `--test_targetDuration=10`, `--test_connectionsOut=10`, `--knob_disable_mainthread_tls_handshake=true`, and `--knob_tls_handshake_flowlock_priority=8900`. TLS arguments point at `keys/ca_file.crt`, `keys/certificate_file.crt`, `keys/key_file.key`, and verify peers with `Root.CN=dummy-ca`.

## Control Flow
There is no argument parsing. Running the script immediately starts one pinned `fdbserver` unittest process configured as the p2ptest client. The command exits when the 10-second target duration completes or the process fails.

## State And Persistence Behavior
The script writes no files directly. The invoked `fdbserver` may emit logs depending on defaults and environment. It reads TLS key material from the relative `keys/` directory.

## Dependencies And Integration Points
It depends on Linux `taskset`, a hard-coded build output at `/root/build_output/bin/fdbserver`, the FoundationDB p2ptest unittest role, a running matching server, and local TLS files. It pairs with `server.sh`.

## Risks And Edge Cases
Hard-coded paths and CPU affinity make it non-portable. Relative TLS paths require running from the benchmark directory. The peer verification pattern is tied to dummy test certificates. No `set -e` or parameterization exists, so failures are only the child command's exit behavior.

## Test Signals
Operational tests should verify the script starts against `server.sh`, completes after roughly 10 seconds, reports successful TLS handshakes, and fails clearly when certificates, server, or `fdbserver` are missing. Static tests can check the hard-coded paths and required certificate files.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/mtlsbenchmark/client.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/mtlsbenchmark/server.sh -->
# sources/storage-engines/foundationdb/contrib/mtlsbenchmark/server.sh

## Purpose
This shell script runs the server side of the mTLS handshake benchmark using FoundationDB's p2ptest unittest mode. It listens indefinitely on TLS port 4500.

## Important APIs, Types, And Functions
The script invokes `/root/build_output/bin/fdbserver` under `taskset -c 1-1` with `--test_listenerAddresses=0.0.0.0:4500:tls`, `--test_targetDuration=0`, `--knob_tls_handshake_limit=1000`, `--knob_tls_server_handshake_threads=1`, `--knob_disable_mainthread_tls_handshake=true`, `--knob_tls_handshake_flowlock_priority=8900`, and `--knob_tls_handshake_timeout_seconds=3.0`. It uses the same CA, certificate, key, and verify-peers pattern as the client.

## Control Flow
Running the script immediately starts a pinned p2ptest server. With target duration 0, it runs until interrupted or until the process exits due to an error.

## State And Persistence Behavior
The script itself is stateless. The child process listens on all interfaces at port 4500 and reads TLS files from `keys/`. Logs/output are inherited from the shell environment.

## Dependencies And Integration Points
It depends on Linux `taskset`, hard-coded `/root/build_output/bin/fdbserver`, p2ptest support, available port 4500, and local test certificates. It is intended to be started before `client.sh`.

## Risks And Edge Cases
Listening on `0.0.0.0` exposes the test TLS endpoint beyond localhost if firewall rules allow it. Hard-coded root build paths and CPU pinning limit reuse. The script has no cleanup, readiness probe, or parameterization. The dummy peer verification pattern is not production-safe.

## Test Signals
Tests should verify the server binds to port 4500, accepts the client benchmark, enforces certificate presence, respects the handshake thread/timeout knobs, and exits nonzero when the port is occupied or `fdbserver` is missing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/mtlsbenchmark/server.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/details.xml -->
# sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/details.xml

## Purpose
This Splunk Simple XML dashboard provides detailed operational views for a FoundationDB log group. It focuses on storage queues, process/network load, connection failures, roles, slow tasks, errors, recoveries, disk space, data movement, and failed clients with filterable index/log group/time/role/host/machine inputs.

## Important APIs, Types, And Functions
The dashboard is a `<form version="1.1" theme="dark">` named `FoundationDB - Details`. Inputs define tokens `Index`, `LogGroup`, `TimeRange`, `Span`, `Roles`, `Host`, and `Machine`. Panels use Splunk searches against FDB trace event types including `StorageMetrics`, `ProcessMetrics`, `NetworkMetrics`, `TLogMetrics`, `ConnectionTimeout`, `ConnectionTimedOut`, `SpringCleaningMetrics`, `SlowTask`, `MasterRecoveryState`, `ProgramStart`, `FailureDetectionStatus`, `MovingData`, and `WaitFailureClient`.

## Control Flow
Splunk fills tokens from the fieldset, then each row/panel runs its `<search>` over `$TimeRange.earliest$` and `$TimeRange.latest$`. Most charts use `timechart $Span$ ... by Machine/Roles`; tables use `stats`, `sort`, and `table`. Several panels derive metrics with `rex`, `eval`, `streamstats`, `join`, `makemv`, and `mvexpand`.

## State And Persistence Behavior
The XML is declarative dashboard configuration. It stores no runtime state beyond Splunk dashboard tokens and does not mutate FDB or Splunk indexes.

## Dependencies And Integration Points
It depends on Splunk Simple XML 1.1, FDB trace logs indexed with fields such as `Type`, `LogGroup`, `Machine`, `host`, `Roles`, and `TrackLatestType`, and a convention where rolled/original metric events are searchable. It integrates with operators' Splunk app import/deployment process.

## Risks And Edge Cases
The broad token substitution can create expensive searches, especially joins and high-cardinality `timechart by Machine`. Filters such as `host=$Host$` assume token defaults like `*` are present and safe. Some panels explicitly ignore filters, which may surprise users. The long recovery query is complex and fragile against field name changes. The file has no explicit tests or dashboard validation metadata.

## Test Signals
Validation should load the XML in Splunk, confirm all tokens resolve, and run representative searches on sample FDB trace data. Search tests should cover default wildcard filters, role filtering, machine filtering, empty result sets, and performance of connection timeout/recovery panels over large time ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/details.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/historgram.xml -->
# sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/historgram.xml

## Purpose
This Splunk dashboard, despite the misspelled filename, displays FoundationDB CommitProxy and TLog latency histograms plus commit latency summary charts. It gives operators bucketed views of transaction pipeline stages.

## Important APIs, Types, And Functions
The form label is `FoundationDB - Histograms` and uses tokens `Index`, `LogGroup`, and `TimeSpan`. Panels chart `CommitLatencyMetrics` summary fields and `Histogram` events for CommitProxy operations `CommitBatchQueuing`, `GetCommitVersion`, `Resolution`, `PostResolutionQueuing`, `ProcessingMutation`, `ReplyCommit`, `TlogLogging`, and `ToTlog_*`, plus TLog operations `QueueWait`, `TimeUntilDurable`, and `commit`.

## Control Flow
The fieldset defaults `Index` to `iffdb` and `TimeSpan` to the last hour, with `autoRun=false`. Each histogram query filters by tokens, event type, group, and operation, runs `foreach LessThan*`, and charts `avg(LessThan*)` over time. Histogram panels are stacked column charts; commit latency summary is a line chart over max/mean/P95/P99/P99.9.

## State And Persistence Behavior
The file is static dashboard configuration and writes no state. Runtime state is limited to Splunk tokens and chart rendering.

## Dependencies And Integration Points
It depends on Splunk Simple XML and FDB trace events that emit `Histogram` fields named `LessThan*`. It integrates with the same observability dashboard set as details and performance overview.

## Risks And Edge Cases
The filename typo `historgram.xml` can break automation expecting `histogram.xml`. The `foreach LessThan* [eval newfield=<<FIELD>>]` command appears to create a generic `newfield` without using it, so it may be redundant or misleading. Averaging cumulative histogram buckets across machines can obscure per-machine outliers. `autoRun=false` means users must submit or change inputs before searches run.

## Test Signals
Tests should import the dashboard in Splunk, verify searches compile, confirm histogram fields render as stacked columns with sample data, check empty data handling, and decide whether the filename typo is intentionally referenced elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/historgram.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/performance_overview.xml -->
# sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/performance_overview.xml

## Purpose
This Splunk Simple XML dashboard provides a high-level FoundationDB performance overview. It charts transaction/read/write rates, latency percentiles, ratekeeper throttling, disk overhead, KV/disk size, roles, storage engine, and recovery generations.

## Important APIs, Types, And Functions
The form label is `FoundationDB - Performance Overview (Dev WiP)`. Inputs define `Index`, `LogGroup`, `TimeSpan`, `UpdateRateTypeToken` for normal vs batch ratekeeper updates, and `ChartBinSizeToken` for binning. Panels query `ProxyMetrics`, `GrvProxyMetrics`, `StorageMetrics`, `GRVLatencyMetrics`, `CommitLatencyMetrics`, `ReadLatencyMetrics`, `RkUpdate*`, `DDTrackerStats`, `ProcessMetrics`, `Role`, and `TLogMetrics`.

## Control Flow
With `autoRun=true`, panels execute when the dashboard loads and token changes trigger refreshes. Searches use `bin _time span=$ChartBinSizeToken$`, `stats`, `timechart`, `eval`, `foreach`, and `table` to aggregate rates and sizes. Ratekeeper panels select event type dynamically with `RkUpdate$UpdateRateTypeToken$`; disk overhead combines storage metrics with DD tracker logical size; role/storage-engine panels summarize recent process/role events.

## State And Persistence Behavior
The XML is static dashboard state only. It does not write to Splunk indexes or FDB. User-selected tokens determine runtime search state.

## Dependencies And Integration Points
It depends on Splunk Simple XML, FDB trace logs with expected metric fields, and consistent `TrackLatestType="Original"` event semantics. It complements the detailed and histogram dashboards by giving first-screen cluster health/performance signals.

## Risks And Edge Cases
`autoRun=true` can trigger many searches immediately, which is expensive for large indexes. Tokenized event type construction for ratekeeper searches can fail silently if values do not match available event types. Some queries aggregate across all hosts/machines and may hide skew. The dashboard is marked Dev WiP, so panel definitions may not be production-hardened. Log-scale or capped axes can hide zero/missing data and extreme values.

## Test Signals
Validation should confirm XML imports cleanly, all token defaults produce valid searches, charts populate on representative trace data, normal/batch ratekeeper selection works, bin-size token changes affect aggregation, and high-cardinality log groups do not exceed Splunk search limits.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/performance_overview.xml -->
