# Research Group subset-b-008396

This grouped report covers the FoundationDB metadata audit corruption checker and its vendored Python binding entrypoint files. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/check_krm_corruption.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/check_krm_corruption.py

## Purpose
`check_krm_corruption.py` is an operational diagnostic and repair utility for FoundationDB metadata corruption around `keyServers`, `serverKeys`, and `serverList` system keyspaces. It is focused on failure modes that can leave Data Distribution or storage servers stuck: uncoalesced KeyRangeMap entries, stale/dead server references, `keyServers`/`serverKeys` ownership disagreement, storage servers missing shards they are supposed to own, orphaned `serverKeys`, and mismatches between metadata and currently running storage roles.

The script is designed to be run from a FoundationDB cluster operator environment. It can run read-only scans, call `fdbcli status json`, integrate JSON from the C++ `audit_ss_shards` tool, probe ranges with Python client reads or metrics calls, and, behind explicit flags plus confirmation, delete selected stale metadata.

## Important APIs, Types, And Functions
The file is a flat Python CLI module. It imports the local vendored `fdb` binding plus metadata constants and lock helpers from `fdb_metadata_utils`: `KEY_SERVERS_PREFIX`, `SERVER_KEYS_PREFIX`, `SERVER_LIST_PREFIX`, matching end keys, `strinc`, transaction option helper, and MoveKeys lock functions.

Binary encoding helpers include `decode_compressed_int`, `encode_compressed_int`, `decode_key_servers_value`, `decode_key_servers_value_simple`, and `encode_key_servers_value`. They understand both old compressed-int `keyServers` values and versioned FDB 6.2+ / 7.2+ values with protocol versions, source/destination server UID vectors, and optional shard IDs. Constants such as `FDB_PROTOCOL_VERSION_62`, `FDB_PROTOCOL_VERSION_72`, `FDB_PROTOCOL_VERSION_73`, and `ANONYMOUS_SHARD_ID` drive re-encoding.

Diagnostics for raw values and round-trip safety are handled by `hex_dump`, `analyze_keyservers_value_format`, `test_keyservers_encoding_roundtrip`, and `test_serverkeys_encoding_roundtrip`. Server identity and status conversion helpers include `status_id_to_serverlist_prefix`, `serverlist_uid_to_status_format`, `uid_cpp_to_raw`, and `uid_raw_to_cpp`, reflecting the different byte orders used by `serverList`, status JSON, and C++ `UID::toString()`.

Metadata readers and analyzers include `get_server_list`, `check_serverlist_vs_running`, `extract_storage_servers_from_status`, `get_cluster_status`, `check_key_servers`, `check_server_keys`, `check_keyservers_serverkeys_mismatch`, `check_wrong_shard_server`, `build_serverkeys_map_for_servers`, `get_serverkeys_ranges_for_orphan_servers`, `compare_server_sets`, and `attempt_server_id_mapping`.

Audit integration is centered on `run_audit_ss_shards`, `load_audit_json`, `is_keyservers_audit`, `generate_audit_comparison_report`, `process_keyservers_audit`, `correlate_audit_with_metadata`, `correlate_stale_serverkeys_with_keyservers`, and `three_way_metadata_correlation`. Repair entrypoints are `repair_serverkeys_from_audit`, `repair_keyservers_from_audit`, and `repair_keyservers_phantom_shards`, with `main()` wiring all CLI modes.

## Control Flow
Startup parses many flags in `main()`. If `--report-audit` is supplied, audit JSON is loaded first and later folded into the full diagnostic run. If `--repair-from-audit` is supplied, the script validates that the requested repair matches the audit mode, opens the database, chooses dry-run unless `--execute-repair` is present, optionally takes the MoveKeys lock, invokes the selected repair routine, releases the lock, and exits.

The standalone `--range-probe-keyservers` mode opens FDB, scans `keyServers` into ranges, separates user ranges from `\xff` system ranges, probes user ranges with `verify_ranges_with_get_range`, and exits.

The default path opens FDB, prints read-only mode, gets cluster status through `fdbcli`, and optionally runs `check_serverlist_vs_running`. It then executes `run_checks` as an `@fdb.transactional` function with read-system-keys and lock-aware options. `run_checks` reads `serverList`, scans `keyServers`, scans `serverKeys`, counts blog keyspace entries, reports KRM and server-reference findings, optionally samples `keyServers`/`serverKeys` mismatches, and by default runs the full `wrong_shard_server` metadata check.

After the transactional checks, `main()` compares server sets against running status data, can run encoding round-trip tests, analyzes orphan servers, attempts storage-server discovery through special keys and address mapping, optionally probes all `keyServers` ranges with point reads, integrates preloaded or freshly executed C++ audit output, performs audit/metadata correlations, and prints an executive DD-impact summary. Nonzero findings exit with status 1; FDB and unexpected errors exit with status 2.

## State And Persistence Behavior
Most diagnostic paths are read-only, but they deliberately access system keyspaces and sometimes use special keyspace reads. Transactions commonly set `set_read_system_keys`, `set_lock_aware`, and explicit timeouts; repair transactions set `set_access_system_keys`, lock-aware mode, system-immediate priority, and call `update_movekeys_lock_write`.

State observed from FDB includes `\xff/keyServers/`, `\xff/serverKeys/`, `\xff/serverList/`, special keys under `\xff\xff/metrics/`, live status JSON from `fdbcli`, and audit JSON produced by a C++ RPC tool. The script also reads local audit JSON files and may run external binaries with `subprocess.run`.

Dry-run repair only prints planned deletion ranges. Live `serverKeys` repair clears ranges under `SERVER_KEYS_PREFIX + server_id + b'/'`, including the begin boundary key. Live keyServers phantom repair clears specific `\xff/keyServers/<begin>` entries. Before live repair, `main()` disables Data Distribution and acquires the MoveKeys lock through `take_movekeys_lock`; the lock is released and DD restored in a `finally` block.

## Dependencies And Integration Points
The script integrates with FoundationDB's Python API, the local vendored binding in `contrib/metadata_audit/fdb`, `fdb_metadata_utils.py`, `fdbcli`, and the C++ `audit_ss_shards` binary. It assumes FDB metadata key layouts for `keyServers`, `serverKeys`, and `serverList`, and it depends on error-code meanings such as `1037` for `wrong_shard_server`, timeout codes `1007`, `1009`, and `1031`, and `2004` for illegal key ranges.

It also integrates conceptually with FDB Data Distribution internals: KeyRangeMap coalescing invariants, serverKeys ownership transitions, `waitStorageMetrics`, storage server `getShardState` RPC results surfaced by the C++ audit, and MoveKeys lock ownership. The CLI documentation explicitly points operators to `audit_ss_shards -C fdb.cluster --json`, `--report-audit`, `--repair-serverkeys`, and `--repair-keyservers` workflows.

## Risks And Edge Cases
This file is operationally risky because it can mutate core system metadata. The strongest safety gates are explicit repair flags, dry-run default, interactive confirmation for live repair, and MoveKeys locking, but the repair logic still clears metadata ranges based on audit JSON and UID conversions. Incorrect audit files, byte-order assumptions, stale status information, or partial scans could delete valid ownership records.

Several analyses use heuristics: extracting IP addresses from serialized serverList values, matching by UID prefixes, classifying blog/backup/system ranges by key prefix, assuming servers not listed in audit missing ranges have data, and using overlap checks rather than exact range equality. Some scans have fixed limits, so results can be incomplete if metadata exceeds the configured `--limit`.

The Python probing paths can misclassify timeouts as likely missing shards or skip system key ranges that clients cannot probe normally. `verify_all_missing_ranges` samples endpoints and explicitly notes that it can miss gaps in the middle, while `verify_ranges_with_get_range` bounds iteration after reading up to 100 KVs. There is also a possible format pitfall in `repair_serverkeys_from_audit`: it converts `server_id_hex` directly with `hex_to_bytes`, while other audit correlation functions convert C++ UID strings with `uid_cpp_to_raw`; correctness depends on the audit JSON server ID format matching the expected raw bytes.

## Test Signals
Built-in test signals are operational rather than unit-test based. `--test-encoding` round-trips sampled `keyServers` values and reports failures with protocol/shard metadata details. `test_serverkeys_encoding_roundtrip` summarizes observed serverKeys value encodings. `--check-mismatch`, the default wrong-shard scan, direct point probes, metrics probes, and range probes provide independent signals for metadata consistency and DD impact.

Audit JSON integration provides the strongest validation signal because the C++ tool directly asks storage servers for shard state and can include the same metrics path DD uses. Useful regression indicators include no decode errors, no uncoalesced adjacent KRM entries, no empty keyServers source server vectors except the sentinel, no dead live references, no `wrong_shard_server` ranges, successful UID/serverList/running-server correlation, and dry-run repair counts matching audit discrepancies.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/check_krm_corruption.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/__init__.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/__init__.py

## Purpose
This file is the vendored FoundationDB Python API package entrypoint used by the metadata audit tools. It delays access to the real binding symbols until the caller selects an API version, and it customizes upstream behavior so the selected version is checked against the loaded `libfdb_c` runtime rather than a hardcoded generated maximum.

The header documents that it is vendored from `bindings/python/fdb/` at commit `2d2a2144f4` and modified for runtime max API version discovery. In this folder it allows the audit scripts to ship with a local binding shim instead of relying entirely on the host Python package.

## Important APIs, Types, And Functions
Module globals expose `__version__` from `fdb.apiversion.FDB_VERSION` and `LATEST_API_VERSION` from `fdb.apiversion.LATEST_API_VERSION`. Before initialization, `open`, `init`, and `transactional` are placeholder functions that raise `RuntimeError` instructing callers to call `api_version()` first.

`is_api_version_selected()` reports whether `_version` has been recorded in module globals, and `get_api_version()` returns it or raises. `_add_symbols(module, symbols)` copies named attributes from implementation modules into this package namespace.

`api_version(ver)` is the central initializer. It prevents selecting two different API versions, rejects versions below 13, imports `fdb.impl`, obtains `header_version` from `fdb.impl._capi.fdb_get_max_api_version()`, validates `ver <= header_version`, calls `fdb_select_api_version_impl(ver, header_version)`, initializes the C API, and then injects core symbols such as `FDBError`, `Future`, `Database`, `Transaction`, `open`, `transactional`, `options`, and `StreamingMode`.

## Control Flow
Importing the package only imports `fdb.apiversion`, sets version constants, and installs guard placeholders. A caller must call `fdb.api_version(version)` before using `fdb.open`, decorators, or transaction classes. On first successful selection, the function loads C API support, publishes binding symbols, handles legacy API compatibility branches, records `_version`, and finally imports and publishes directory and subspace helpers.

For old API versions, `api_version` branches further. Versions below 610 restore legacy `init`, `open_v609`, cluster creation, and `Cluster`; version 13 maps `open_v13`/`init_v13`, restores `Future.get`, and makes `FDBRange` act like an iterator through a local `next` method. Versions above 22 import `fdb.locality`.

## State And Persistence Behavior
The file maintains process-global API selection state through the `_version` global and mutates the package namespace by assigning imported symbols into `globals()`. After selection, repeated calls with the same version are idempotent; calls with a different version raise. There is no file or database persistence here, but the C library selection is effectively process-global and must happen before any FDB operations.

## Dependencies And Integration Points
This module depends on sibling vendored modules `fdb.apiversion`, `fdb.impl`, `fdb.directory_impl`, `fdb.subspace_impl`, and optionally `fdb.locality`. The metadata audit scripts import `fdb` from this package and use `fdb.open`, `fdb.transactional`, `fdb.FDBError`, locality helpers, transaction options, and streaming modes after initialization elsewhere in the vendored binding stack.

The key integration detail is its runtime call to `libfdb_c` for maximum API version. This is intended to keep the bundled Python files usable across installed FoundationDB C libraries rather than being pinned to a generated `LATEST_API_VERSION` value.

## Risks And Edge Cases
The initializer trusts private `fdb.impl._capi` attributes and the exact signature of `fdb_select_api_version_impl`, so vendored file drift against `impl.py` or `libfdb_c` can break initialization. Because symbols are copied into the package namespace, partial initialization failures can leave confusing globals if an unexpected exception occurs after some assignments.

The global API version policy mirrors upstream behavior: choosing the wrong version first cannot be corrected in-process. The high `LATEST_API_VERSION` value in `apiversion.py` is only an advertised upper bound; actual support depends on the loaded C library. Legacy compatibility branches for very old APIs are present but likely unexercised by the metadata audit scripts.

## Test Signals
Simple import tests should confirm that pre-initialization `fdb.open()` and `fdb.transactional()` raise the expected guidance errors, `is_api_version_selected()` is false before selection, and `api_version(ver)` succeeds when `ver` is within the runtime C library max. Negative tests should verify rejection of `ver < 13`, rejection above runtime max, idempotence for repeated same-version calls, and failure for conflicting second versions.

Integration tests for this repository should run at least one audit script far enough to call `fdb.open` against a selected API version, proving that runtime symbol injection, transaction decorators, options, and `FDBError` all resolve from the vendored package.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/apiversion.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/apiversion.py

## Purpose
`apiversion.py` supplies version constants for the vendored FoundationDB Python binding used by the metadata audit tools. It intentionally sets a generous upper-bound `LATEST_API_VERSION` while documenting that the real maximum is obtained from the loaded C library at runtime by `fdb.__init__.api_version()`.

## Important APIs, Types, And Functions
The file contains two constants and no functions or classes:

`LATEST_API_VERSION = 740` is a high upper-bound value meant not to block current or near-future FDB versions before the runtime C library is queried.

`FDB_VERSION = "7.3"` is the package version string exported through `fdb.__version__`.

## Control Flow
There is no dynamic control flow. `fdb/__init__.py` imports this module during package import and copies the constants into package-level `__version__` and `LATEST_API_VERSION`.

## State And Persistence Behavior
The module has no mutable state and performs no persistence. Its values are process constants after import. Runtime API compatibility is not decided here; this file only provides a loose advertised ceiling and display version.

## Dependencies And Integration Points
The only direct integration point is `sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/__init__.py`, which imports `FDB_VERSION` and `LATEST_API_VERSION`. The comment aligns with the modified initializer behavior that calls `fdb.impl._capi.fdb_get_max_api_version()` before selecting an API version.

## Risks And Edge Cases
Because `LATEST_API_VERSION` is deliberately higher than the nominal `FDB_VERSION` string, callers that treat it as authoritative rather than as a pre-check ceiling could be misled. The local initializer mitigates this by comparing requested API versions to `libfdb_c` at runtime. If FoundationDB API versions advance past 740, this file could again become a blocker unless updated.

## Test Signals
Tests should verify that importing `fdb` exposes `__version__ == "7.3"` and `LATEST_API_VERSION == 740`, and that selecting an API version above the installed C library maximum fails in `api_version()` despite this high constant. This confirms that runtime C-library discovery, not this static file, controls actual compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/apiversion.py -->
