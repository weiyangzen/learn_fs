# subset-b-009979 research

Grouped research for Samba raw torture sources under `sources/user-network-fs/samba/source4/torture/raw`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/lock.c -->
# sources/user-network-fs/samba/source4/torture/raw/lock.c

## Purpose
`lock.c` defines the `RAW-LOCK` smb-torture suite for SMB1 byte-range locking semantics. It probes legacy `SMBlock`/`SMBunlock`, `LOCKING_ANDX`, lock cancellation, status-code caching, zero-byte lock behavior, unlock ordering, shared/exclusive stacking, zero-byte reads against locked ranges, and multi-range blocking queue precedence. The tests are protocol conformance checks rather than reusable production logic.

## Important APIs, Types, and Functions
- Uses Samba raw client primitives from `libcli/raw`: `smb_raw_lock`, `smb_raw_lock_send`, `smbcli_request_simple_recv`, `smb_raw_open`, `smb_raw_exit`, `smb_raw_ulogoff`, `smb_tree_disconnect`, `smb_raw_tcon`, and raw read helpers.
- Uses high-level torture helpers: `torture_suite_create`, `torture_suite_add_1smb_test`, `torture_setup_dir`, `torture_assert*`, `torture_result`, `torture_comment`, and target feature settings such as `samba3`, `smbexit_pdu_support`, and `range_not_locked_on_file_close`.
- Main test functions are `test_lock`, `test_lockx`, `test_pidhigh`, `test_async`, `test_errorcode`, `test_changetype`, `test_zerobytelocks`, `test_unlock`, `test_multiple_unlock`, `test_stacking`, `test_zerobyteread`, and `test_multilock` through `test_multilock6`.
- `struct double_lock_test` and `zero_byte_tests[]` encode the zero-byte lock overlap matrix.
- `torture_raw_lock()` registers all subtests in the `lock` suite.

## Control Flow
Each subtest creates `\\testlock`, opens one or more files, builds a `union smb_lock` with `struct smb_lock_entry` ranges, performs raw synchronous or asynchronous locking operations, validates exact NT status results, and tears down with `smb_raw_exit()` plus `smbcli_deltree()`. The async tests send pending lock requests with timeouts, then cancel by explicit `LOCKING_ANDX_CANCEL_LOCK`, unlock, file close, `SMBexit`, user logoff, or tree disconnect and assert that pending requests complete immediately with Windows-compatible statuses.

The `test_errorcode` path is the densest status-code test. It opens two fnums for the same file, demonstrates per-handle error-code cache behavior for `NT_STATUS_LOCK_NOT_GRANTED` versus `NT_STATUS_FILE_LOCK_CONFLICT`, repeats the matrix with `timeout = 0` and `timeout > 0`, and checks that pending timed locks only update the cache when the error is reported to the client.

The multi-lock tests encode queue ordering rules. `test_multilock` checks that a two-range blocked lock completes only after both original ranges are unlocked. `test_multilock2` through `test_multilock6` vary shared/exclusive modes and independent ranges to prove that pending requests have precedence by arrival order while unrelated ranges can proceed.

## State and Persistence Behavior
The tests create transient files below `\\testlock`; no persistent configuration is written. State is held in local `union smb_lock`, `struct smb_lock_entry`, fnum, pid, request, and tree/session objects. Several tests deliberately mutate `cli->session->pid` or lock-entry `pid` to validate server PID semantics. Cleanup relies on `smb_raw_exit()` to release locks and `smbcli_deltree()` to delete the test directory.

## Dependencies and Integration Points
This file integrates with the Samba4 torture runner through `torture_raw_lock()`. It depends on SMB1 raw client behavior, the torture context settings system, command-line credentials for secondary session setup, and server support for old SMB PDUs. It uses `lpcfg_smbcli_session_options`, `smb_composite_sesssetup`, and `RAW_TCON_TCONX` to create additional sessions/tree connects inside cancellation tests.

## Risks and Edge Cases
- Many assertions depend on server-specific compatibility switches. Incorrect target settings can turn expected Windows/Samba divergences into false failures.
- Async tests are timing-sensitive and use two-second immediacy checks; slow virtualized or remote environments may cause flakes.
- Tests intentionally leave requests pending while manipulating session/tree state, so cleanup regressions can leak locks until connection teardown.
- The multi-lock cases protect subtle lock queue semantics; simplifying them risks losing coverage for deadlock, starvation, or wrong ordering bugs.
- `CHECK_STATUS` macros jump to common cleanup labels; changes must keep fnums initialized before cleanup paths.

## Test Signals
Primary pass/fail signals are exact NT status matches, immediate completion timing checks, request state checks such as `req->state <= SMBCLI_REQUEST_RECV`, successful zero-byte read counts, and successful cleanup of the test tree. Suite registration names are `lockx`, `lock`, `pidhigh`, `async`, `errorcode`, `changetype`, `stacking`, `unlock`, `multiple_unlock`, `zerobytelocks`, `zerobyteread`, and `multilock*`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/lockbench.c -->
# sources/user-network-fs/samba/source4/torture/raw/lockbench.c

## Purpose
`lockbench.c` implements `torture_bench_lock()`, an asynchronous SMB1 byte-range lock benchmark. It opens multiple client connections to a shared file, continuously alternates lock and unlock requests over a small offset ring, reports per-client throughput, and attempts to reconnect when a server connection is lost.

## Important APIs, Types, and Functions
- `struct benchlock_state` stores each client lane: torture context, event loop, tree, fnum, stage, offsets, operation counters, reconnect metadata, outstanding request, and reconnect timer.
- `enum lock_stage` drives the sequence `LOCK_INITIAL`, `LOCK_LOCK`, and `LOCK_UNLOCK`.
- `lock_send()` builds a `RAW_LOCK_LOCKX` request with `LOCKING_ANDX_LARGE_FILES` and sends it using `smb_raw_lock_send()`.
- `lock_completion()` consumes replies, advances the stage, counts operations, and schedules reconnects on EOF/local disconnect/connection reset.
- `reopen_connection()`, `reopen_connection_complete()`, and `reopen_file()` rebuild a lost tree connection and reopen `\\benchlock\\lock.dat`.
- `report_rate()` prints one-second deltas and sends SMB echo keepalives.

## Control Flow
The benchmark reads `timelimit`, `progress`, `nprocs`, and `initial_locks` settings, opens `nprocs` SMB connections, captures remote address/name metadata for reconnects, creates `\\benchlock`, opens `lock.dat` per connection, optionally seeds high-offset locks, then sends the first async lock per state. The main loop runs `tevent_loop_once()` until the time limit expires or `lock_failed` becomes non-zero. On completion it prints aggregate counts, verifies that no lane is severely under-balanced, exits sessions, deletes the test directory, and frees memory.

## State and Persistence Behavior
All benchmark state is in process-global counters (`nprocs`, `lock_failed`, `num_connected`) and per-client `benchlock_state` arrays. The only server-side persistence is the temporary benchmark directory and file plus byte-range locks, which are released by session exit and directory deletion.

## Dependencies and Integration Points
The file uses raw SMB locking, composite async connect APIs, `tevent`, command-line credentials, resolver and loadparm configuration, `smbXcli_conn_remote_sockaddr`, and torture connection helpers. It is a benchmark entry point exposed by `torture/raw/proto.h`, not a suite registration file.

## Risks and Edge Cases
- Reconnect logic assumes the share and remote endpoint are recoverable from the original connection index and captured socket address.
- `lock_send()` increments `lock_failed` if request allocation fails but then dereferences `state->req`; that path would be unsafe if allocation actually returned `NULL`.
- Global counters make concurrent benchmark instances in one process unsafe.
- The printed total ops/second uses `total` without accumulating it from state counts, so the headline rate can be misleading even though per-client counts are printed.
- Timing and balance checks may be noisy on slow servers or during failover.

## Test Signals
Useful signals are the per-client one-second operation deltas, `lock_failed`, reconnect debug messages, final per-client operation counts, and the unbalanced-locking failure when the minimum lane count is below half of the average.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/lockbench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/lookuprate.c -->
# sources/user-network-fs/samba/source4/torture/raw/lookuprate.c

## Purpose
`lookuprate.c` implements `torture_bench_lookup()`, a benchmark/regression test for missing-name lookup scalability. It verifies that lookup rates for a non-existent path remain roughly constant as the containing directory grows from empty to large entry counts.

## Important APIs, Types, and Functions
- `struct rate_record records[]` defines directory sizes and stores measured `TRANS2_QUERY_PATH_INFORMATION` and `TRANS2_FIND_FIRST2` rates.
- `fill_directory()` creates the test directory and fills it with randomly named files.
- `querypath_lookup()` calls `smbcli_qpathinfo()`, while `findfirst_lookup()` calls `smbcli_list()`.
- `squash_lookup_error()` treats expected missing-file/path statuses as success.
- `lookup_rate_convert()` loops for two seconds and converts operation count into lookups per second.
- `remove_working_directory()` retries `smbcli_deltree()` up to five times for very large directories.

## Control Flow
The test opens one SMB connection, removes any prior `\\lookuprate`, then iterates through the configured record sizes. For each size it creates and fills the directory, measures missing `\\lookuprate\\foo` lookup rate with query-path and find-first methods, prints the rates, and deletes the directory. After all samples it compares every sample to the empty-directory baseline using a ten-percent fuzz threshold.

## State and Persistence Behavior
Measurements are stored in the static `records[]` array for the life of the process. Server-side state is the temporary `\\lookuprate` tree and generated filler files, removed between each sample and again at exit.

## Dependencies and Integration Points
The benchmark uses `torture_open_connection`, classic `smbcli_*` helper APIs, timeval helpers, and `torture/raw/proto.h`. It exercises server directory lookup/indexing behavior through normal SMB path and search operations.

## Risks and Edge Cases
- The largest sample creates 100,000 files; this is expensive and cleanup can fail on some servers.
- The ten-percent threshold can be too strict on noisy networks or cold caches.
- `random()` names are not seeded here, so reproducibility depends on process state.
- `usec_to_sec()` truncates integer microseconds before double division, reducing precision for short periods, though the loop runs for about two seconds.

## Test Signals
Signals are fill rates, measured querypath/findfirst lookups per second, failure statuses from fill or lookup, cleanup retry messages, and final deviations beyond `FUZZ_PERCENT`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/lookuprate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/mkdir.c -->
# sources/user-network-fs/samba/source4/torture/raw/mkdir.c

## Purpose
`mkdir.c` defines the raw SMB mkdir/rmdir torture test. It validates `RAW_MKDIR_MKDIR`, `RAW_MKDIR_T2MKDIR`, `RAW_RMDIR`, path validation, file-versus-directory errors, and extended attribute creation behavior.

## Important APIs, Types, and Functions
- `test_mkdir()` is the full test body.
- `torture_raw_mkdir()` is the exported entry point.
- Uses `union smb_mkdir`, `struct smb_rmdir`, `smb_raw_mkdir()`, `smb_raw_rmdir()`, `create_complex_file()`, `torture_check_ea()`, `smbcli_unlink()`, `smb_raw_exit()`, and `smbcli_deltree()`.
- `CHECK_STATUS` validates exact NT status codes and jumps to cleanup.

## Control Flow
The test creates `\\mkdirtest`, creates `\\mkdirtest\\mkdir.dir`, verifies duplicate mkdir collision, removes it, verifies missing rmdir, creates a file at the same path and verifies mkdir collision plus `rmdir` returning `NT_STATUS_NOT_A_DIRECTORY`, tests invalid relative traversal path syntax, creates via T2 mkdir, checks a bad nested path, then creates a directory with three EAs and validates those EAs unless Samba3 reports EAs unsupported.

## State and Persistence Behavior
All state is temporary under `\\mkdirtest`. EA values are allocated from the torture context with `data_blob_talloc()`. Cleanup exits the SMB session and deletes the whole test directory.

## Dependencies and Integration Points
This file integrates with the raw torture harness via `torture_raw_mkdir()`. It relies on raw SMB mkdir/rmdir marshalling and shared torture utility functions for directory setup, complex file creation, and EA verification.

## Risks and Edge Cases
- EA support is server-dependent; Samba3 `NT_STATUS_EAS_NOT_SUPPORTED` is explicitly non-fatal.
- The invalid path expectation is exact (`NT_STATUS_OBJECT_PATH_SYNTAX_BAD`) and may expose server dialect differences.
- `create_complex_file()` failure would feed an invalid fnum to `smbcli_close()` if not guarded by the helper's contract.

## Test Signals
Pass/fail is dominated by exact status checks for create, collision, removal, invalid path, T2 mkdir, and EA verification. Diagnostic prints identify each scenario.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/mux.c -->
# sources/user-network-fs/samba/source4/torture/raw/mux.c

## Purpose
`mux.c` tests SMB1 request multiplexing around delayed operations. It verifies that blocking open, write, and lock requests interact correctly with close, unlock, cancel, and exit while multiple outstanding requests share one connection.

## Important APIs, Types, and Functions
- `test_mux_open()` checks delayed sharing-violation opens and `smb_raw_ntcancel()` behavior.
- `test_mux_write()` sends an async write into a locked range and expects `NT_STATUS_FILE_LOCK_CONFLICT`.
- `test_mux_lock()` checks blocking lock retry, cancel idempotence, and lock cancellation through session exit.
- `torture_raw_mux()` sets up `\\test_mux`, runs all subtests, exits the session, and deletes the directory.
- Uses raw `NTCREATEX`, `WRITEX`, `LOCKX`, close, cancel, and request receive APIs.

## Control Flow
The open test creates a file with restrictive share access, verifies a synchronous conflicting open delays about one second, sends two async conflicting opens, closes existing handles, cancels one request, and checks that one async open succeeds while the canceled one times out with sharing violation. The write test locks a byte range as one PID, sends a write as another PID, unlocks, then verifies the write reply remains a lock conflict. The lock test establishes conflicts, sends pending lock requests, unlocks or cancels them, and validates immediate completion semantics including repeated cancel and exit-driven cancellation.

## State and Persistence Behavior
State is limited to file handles, session PID mutations, raw request objects, and temporary files under `\\test_mux`. Locks are released through explicit unlocks or `smb_raw_exit()`.

## Dependencies and Integration Points
The file is registered through the raw torture entry point `torture_raw_mux()`. It uses the same SMB client session for most operations, intentionally relying on multiplexed outstanding requests over one transport.

## Risks and Edge Cases
- Timing assertions use narrow thresholds around expected one-second server delays and sub-250ms immediate completions.
- The test mutates `cli->session->pid` in place; later code must reset or understand PID ownership.
- Canceled requests are still received, so changes must not free request objects prematurely.

## Test Signals
Signals include exact NT statuses, elapsed-time checks for delayed and immediate operations, harmless duplicate cancel behavior, and successful cleanup after `smb_raw_exit()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/notify.c -->
# sources/user-network-fs/samba/source4/torture/raw/notify.c

## Purpose
`notify.c` defines the raw SMB change-notify torture suite. It validates directory change notification delivery, buffering, cancellation, recursive watching, completion-filter masks, teardown behavior, secondary tree-connect behavior, overflow semantics, base-directory exclusion, and reply alignment.

## Important APIs, Types, and Functions
- Central raw API is `smb_raw_changenotify_send()`/`smb_raw_changenotify_recv()` using `union smb_notify` at `RAW_NOTIFY_NTTRANS`.
- Directory handles are opened with raw `NTCREATEX` directory options.
- `CHECK_WSTR` validates Unicode names and wire flags.
- `check_rename_reply()` tolerates non-deterministic ordering among rename-related add/remove/modify events.
- `secondary_tcon()` creates another tree connect on the same session with `RAW_TCON_TCONX`.
- `timeout_cb()` is used by the alignment test to bound a pending notify receive.
- `torture_raw_notify()` registers tests `tcon`, `dir`, `mask`, `recursive`, `mask_change`, `file`, `tdis`, `exit`, `ulogoff`, `tcp_dis`, `double`, `tree`, `overflow`, `basedir`, and `alignment`.

## Control Flow
Most subtests create a dedicated `\\test_notify_*` directory, open a directory handle, arm a notify request, perform filesystem operations through one or two SMB clients, receive the notify reply, and assert count, action, and name. `test_notify_dir()` covers cancellation, mkdir/rmdir, buffered creates/unlinks, wildcard unlink propagation, per-handle buffers, and close-triggered zero-change replies. `test_notify_recursive()` compares recursive and non-recursive buffers across nested mkdir/create/rename/delete operations. `test_notify_mask()` iterates every completion-filter bit for operations such as create, unlink, rename, attribute/time change, write, and truncate.

Teardown tests arm a notify then issue `tdis`, `SMBexit`, `ulogoff`, or forced TCP disconnect and assert the resulting completion status. `test_notify_tree()` opens many watched directories at different depths, generates create/delete events, polls until each watcher sees its expected count, and validates recursive filtering. `test_notify_alignment()` creates names of lengths one through four and relies on the receive parser to validate four-byte alignment of multiple `CHANGE_NOTIFY_INFO` records.

## State and Persistence Behavior
Server-side state is a set of temporary test directories and files. Notify buffers are deliberately primed by sending and canceling requests before generating events. The suite uses multiple clients or tree connects to test cross-connection delivery and clustered server propagation. Cleanup exits sessions and deletes each dedicated base directory.

## Dependencies and Integration Points
The suite integrates with the Samba torture framework through `torture_raw_notify()`, using one-SMB or two-SMB test registration depending on whether cross-client operations are required. It depends on raw SMB notify marshalling, string wire validation, event-loop timers for timeout protection, and standard SMB filesystem helpers.

## Risks and Edge Cases
- Notify ordering can vary, so rename checks intentionally accept action/name triples in a small window.
- Several tests use sleeps or propagation polling; clustered, cloud, or slow filesystems can be flaky.
- Exact notify mask expectations vary by server family; the code already skips one Samba3 create-time case.
- Overflow behavior expects an OK reply with zero changes when the server-side buffer exceeds response capacity.
- Close, disconnect, and TCP failure paths are sensitive to request lifetime and transport error propagation.

## Test Signals
Signals include exact NT statuses (`OK`, `CANCELLED`, `INVALID_PARAMETER`, `LOCAL_DISCONNECT`), expected notification counts, action constants such as `NOTIFY_ACTION_ADDED` and `NOTIFY_ACTION_REMOVED`, Unicode name checks, depth-specific event totals, duplicate/unexpected name detection in alignment tests, and timeout failure if delayed notify replies do not arrive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/offline.c -->
# sources/user-network-fs/samba/source4/torture/raw/offline.c

## Purpose
`offline.c` implements `torture_test_offline()`, a stress benchmark for SMB offline-file handling. It repeatedly performs asynchronous load, save, set-offline-attribute, and get-attribute operations across multiple connections and tracks throughput plus worst latency.

## Important APIs, Types, and Functions
- `enum offline_op` defines `OP_LOADFILE`, `OP_SAVEFILE`, `OP_SETOFFLINE`, and `OP_GETOFFLINE`.
- `struct offline_state` tracks each concurrent operation lane: tree, file number, operation counters, file name, composite request objects, raw request, current op, and start time.
- `filename()` maps an integer to `\\testoffline\\fileN.dat`.
- `loadfile_callback()`, `savefile_callback()`, `setoffline_callback()`, and `getoffline_callback()` validate async completions and resubmit work.
- `test_offline()` chooses a random operation and random file, sends the corresponding composite or raw async request, and records latency.
- `report_rate()` prints ops/sec, online/offline counts, current and worst latencies, and sends echo keepalives.

## Control Flow
The test reads `timelimit`, `progress`, `nprocs`, global `torture_entries`, and global `torture_numops`. It opens `nprocs` connections, creates `numstates = nconnections * torture_entries` lanes, reuses connection trees across lanes, extends SMB request timeout for offline file delays, creates `\\testoffline`, pre-creates `torture_numops` files with deterministic 8 KiB contents, starts one async random operation per lane, and runs the event loop until the time limit expires or a callback marks failure. After the timed run it sets `test_finished`, drains all outstanding requests, prints worst latencies, deletes the tree, and frees memory.

## State and Persistence Behavior
Global counters store connection count, lane count, test failure, finish flag, current latencies, and worst latencies. Each lane stores its outstanding request and counters. Server-side state is the temporary file corpus plus offline attributes; contents are checked against `1 + (file_number % 255)` after each load.

## Dependencies and Integration Points
The file depends on composite SMB helpers `smb_composite_loadfile_send/recv` and `smb_composite_savefile_send/recv`, raw path info and set path info APIs, `tevent`, torture global operation settings, and SMB echo keepalive. It is a benchmark-style torture entry point rather than a suite factory.

## Risks and Edge Cases
- Globals make repeated runs in the same process sensitive unless state is reinitialized by process lifetime.
- `test_failed` is an int but sometimes assigned boolean-style values.
- Offline/HSM systems can legitimately have long latencies; the transport timeout is raised to 200 seconds but the benchmark still depends on event-loop responsiveness.
- Callbacks resubmit recursively until `test_finished`, so any missed completion can stall drain.
- Failed setup paths free memory without deleting `\\testoffline`, leaving cleanup to later runs.

## Test Signals
Signals are callback status failures, data integrity mismatches, online/offline attribute counts, per-second throughput, latency maxima per operation type, echo disconnect failures, and successful final drain of all outstanding load/save/raw requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/offline.c -->
