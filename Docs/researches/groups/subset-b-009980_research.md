# subset-b-009980 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/open.c -->
# sources/user-network-fs/samba/source4/torture/raw/open.c

## Purpose
This file implements the `raw.open` torture suite for SMB1 open and create semantics. It is a compatibility oracle for legacy open calls (`RAW_OPEN_OPEN`, `RAW_OPEN_OPENX`, `RAW_OPEN_T2OPEN`, `RAW_OPEN_MKNEW`, `RAW_OPEN_CREATE`, `RAW_OPEN_CTEMP`) and NT-style create paths (`RAW_OPEN_NTCREATEX`, `RAW_OPEN_NTTRANS_CREATE`, and chained open/read calls). The tests verify status codes, returned metadata, open dispositions, share and access masks, directory handling, byte-range-lock interactions, delete/truncate behavior, and several historical Samba or server-specific edge cases.

## Important APIs, types, and functions
The main suite entry point is `torture_raw_open()`, which registers one-SMB tests such as `open`, `openx`, `ntcreatex`, `nttrans-create`, `t2open`, `brlocked`, `open-multi`, `opendisp-dir`, `ntcreatedir`, `open-for-truncate`, and `ntcreatex_supersede`. Local helpers include `check_rdwr()` and `rdwr_string()`, which translate actual read/write probes into `enum rdwr_mode` values. The file relies heavily on `union smb_open`, `union smb_fileinfo`, `union smb_setfileinfo`, `union smb_lock`, `struct smb_lock_entry`, `NTSTATUS`, and raw SMB calls including `smb_raw_open()`, `smb_raw_open_send()`, `smb_raw_open_recv()`, `smb_raw_pathinfo()`, `smb_raw_fileinfo()`, `smb_raw_setpathinfo()`, `smb_raw_setfileinfo()`, and `smb_raw_lock()`.

## Control flow
Most tests follow the same pattern: create or clean `BASEDIR` (`\rawopen`), initialize a `union smb_open` variant, perform an open/create operation, compare the returned status and fields through local macros, then close and remove any test objects. `test_open()` covers old `SMBopen` access and deny modes and validates the returned write time, size, and attributes. `test_openx()` iterates a disposition table, checks return fields and hidden/system attributes, exercises timeout behavior, and verifies odd compatibility behavior such as execute access creating a file and `.exe` execute mapping to read-only access.

`test_t2open()` mirrors `OPENX` coverage through Trans2 open, adding extended attributes and Samba3 fallback when EAs are unsupported. `test_ntcreatex()` and `test_nttrans_create()` exercise NT create disposition matrices, returned timestamps and allocation data, directory creation, create-option masks, `NO_RECALL`, ignored option bits, unsupported option bits, and invalid-parameter classification. The NTTRANS variant also checks masks for create options that should be OK, not supported, invalid, or not-a-directory.

The remaining tests target narrower regressions: `test_ntcreatex_brlocked()` verifies an overwrite-if open succeeds on a byte-range-locked file in a Windows-compatible pattern; `test_mknew()`, `test_create()`, and `test_ctemp()` cover legacy file creation, timestamps, attributes, and server-generated temporary names; `test_chained()` and `test_chained_ntcreatex_readx()` verify chained open-and-read responses; `test_no_leading_slash()` checks paths without a leading slash; `test_openx_over_dir()` verifies directory-open error mapping; `test_raw_open_multi()` sends concurrent async `NTCREATEX_DISP_CREATE` requests and expects exactly one success; `test_open_for_delete()` checks delete-only opens against read-only files; `test_ntcreatex_opendisp_dir()` and `test_ntcreatexdir()` distinguish file attributes from mandatory directory create options; `test_open_for_truncate()` ensures a failed sharing open does not truncate; and `test_ntcreatex_supersede()` verifies supersede responses report size zero.

## State and persistence
All ordinary tests keep server-side artifacts under `\rawopen` and remove them with `smbcli_deltree()` on completion. The concurrent create race test uses `\test_oplock.dat` outside `BASEDIR`, opens multiple independent connections, and explicitly closes those connections. Persistent state under test is server-side only: open handles, share-mode tables, file attributes, timestamps, allocation size, byte-range locks, delete-on-close state, directory/file object type, and extended attributes. Local state is stack-scoped except for temporary talloc contexts and arrays used by multi-open.

## Dependencies and integration points
The file integrates with Samba's raw SMB client layer (`libcli/raw/libcliraw.h`), torture harness helpers, talloc allocation, the tevent event loop for async opens, filesystem/time conversion helpers, and `torture/raw/proto.h` registration. It depends on `create_complex_file()`, `create_directory_handle()`, `torture_setup_dir()`, `torture_open_connection_share()`, `torture_close_connection()`, `torture_check_ea()`, and `dump_all_info()` from the wider torture utility layer.

## Risks
These tests encode very specific Windows and Samba compatibility semantics, so expected status changes may be legitimate only when a compatibility baseline changes. Time checks mask low bits and allow small tolerances, but slow filesystems or clock-conversion differences can still produce noisy failures. Several paths close fnums after failed operations, which is idiomatic in this suite but can obscure invalid-handle cleanup issues. `test_raw_open_multi()` is intentionally race-sensitive and depends on event-loop progress, request timeout, and server atomicity for create collisions. NT create-option masks are brittle because a single bit classification change affects aggregate expected masks.

## Test signals
Primary failure signals are mismatched `NTSTATUS` values, incorrect returned action codes such as created/existed/superseded, bad read/write capability from `check_rdwr()`, wrong timestamps or attributes from `RAW_FILEINFO_ALL_INFO`, unexpected create-option mask bits, incorrect directory versus file behavior, failed chained read data comparison, failure to preserve size after a sharing violation, and race outcomes where concurrent create returns more than one success or any status other than collision for losers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/openbench.c -->
# sources/user-network-fs/samba/source4/torture/raw/openbench.c

## Purpose
This file implements `torture_bench_open()`, an asynchronous benchmark for SMB `NTCREATEX` open/close throughput. It opens multiple client connections, repeatedly cycles through a shared pool of filenames, keeps one current open per worker, asynchronously closes the previous handle after each successful open, and reports per-worker and aggregate operations per second. It is both a performance benchmark and a stress test for share-mode contention, reconnect handling, and event-loop-driven raw SMB request sequencing.

## Important APIs, types, and functions
The central state container is `struct benchopen_state`, which tracks the torture context, event context, client/tree pointers, current and pending fnums, file indices, request pointers, reconnect parameters, counters, retry counts, and timer handles. The key local functions are `next_open()`, `next_close()`, `open_completed()`, `close_completed()`, `reopen_connection()`, `reopen_connection_complete()`, `echo_completion()`, and `report_rate()`. Important APIs include `smb_raw_open_send()`, `smb_raw_open_recv()`, `smb_raw_close_send()`, `smbcli_request_simple_recv()`, `smb_composite_connect_send()`, `smb_composite_connect_recv()`, `smb_raw_echo_send()`, `tevent_add_timer()`, `tevent_loop_once()`, and `torture_open_connection_ev()`.

## Control flow
`torture_bench_open()` reads settings (`timelimit`, `nprocs`, `progress`), allocates one `benchopen_state` per worker, opens the initial SMB connections, records remote address and called-name data for later reconnects, prepares `\benchopen`, and builds `3 * nprocs` filenames. Each worker starts at file index zero and calls `next_open()`.

`next_open()` increments the worker operation count, advances the circular file index, fills an `RAW_OPEN_NTCREATEX` request with `SEC_RIGHTS_FILE_ALL`, share access zero, and `NTCREATEX_DISP_OVERWRITE_IF`, then sends it asynchronously. `open_completed()` receives the response. Disconnect-like statuses free the old tree/client, decrement `num_connected`, and schedule a one-second reconnect. Sharing violations are retried immediately and counted. Successful opens rotate the newly opened fnum into `open_fnum`, move the old open fnum into `close_fnum`, optionally starts `next_close()`, and immediately schedules another open to keep pressure on the server.

`next_close()` sends an async raw close for the previous fnum. `close_completed()` handles disconnect-like statuses similarly to open completion and increments a global close-failure counter on other errors. `report_rate()` prints per-worker delta counts once per second and sends async SMB echo requests on live connections so idle paths remain active, especially during IP takeover scenarios. After the time limit, the benchmark cancels the report timer, prints per-worker counts and retries, checks that the slowest worker is not less than half the average, exits sessions, removes `\benchopen`, and frees benchmark memory.

## State and persistence
Global state includes `nprocs`, `open_failed`, `close_failed`, `fnames`, `num_connected`, and `report_te`. Per-worker state is talloc-owned under the benchmark context. Server-side state consists of the `\benchopen` directory, a rotating set of `fileN.dat` files, open handles, share-mode conflicts, and live SMB connections. Cleanup removes `\benchopen` on the success path; failure paths free the talloc context but may leave server-side files if the benchmark aborts early.

## Dependencies and integration points
The benchmark sits in the raw torture layer but uses several broader Samba facilities: command-line credentials, `lpcfg_*` client/session/gensec options, resolver context, composite SMB connect APIs, SMB echo keepalive, socket-address formatting, and `smbXcli_conn_*` accessors. It expects the torture harness to provide an event loop and indexed connection settings through `torture_get_conn_index()` and `torture_open_connection_ev()`.

## Risks
This code intentionally runs indefinitely until the configured time limit and can generate heavy open/close contention. The global failure counters are not reset inside the function, so repeated in-process invocations could inherit failure state. In `next_open()`, the returned request is assumed non-NULL before assigning callback fields. Reconnect paths mix talloc ownership of `tree` and `cli`; freeing one while callbacks are outstanding would be risky if future code changes allowed overlapping reconnect and request completion. Failure exits do not run full server cleanup. The balance check is a benchmark heuristic and can fail on real scheduling imbalance rather than protocol malfunction.

## Test signals
Useful signals are `open_failed` or `close_failed`, unexpectedly high `open_retries`, reconnect churn, unbalanced worker operation counts, low aggregate ops/sec, failure to create or clean `\benchopen`, and disconnect-like status handling (`NT_STATUS_END_OF_FILE`, `NT_STATUS_LOCAL_DISCONNECT`, `NT_STATUS_CONNECTION_RESET`) during open, close, or echo completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/openbench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/oplock.c -->
# sources/user-network-fs/samba/source4/torture/raw/oplock.c

## Purpose
This file implements the raw SMB oplock torture suite, an oplock benchmark, and a manual oplock-hold tool. It validates exclusive, level-II, and batch oplock behavior across conflicting opens, share modes, deletes, renames, path/file information updates, byte-range locks, alternate data streams, delete-on-close, clients without level-II support, and timeout paths. The registered `raw.oplock` suite is a dense compatibility baseline for how Samba and Windows servers should grant, break, downgrade, acknowledge, or time out oplocks.

## Important APIs, types, and functions
The suite entry point is `torture_raw_oplock()`, which registers two-connection tests `exclusive1` through `exclusive9`, `level_ii_1`, `batch1` through `batch26`, `stream1`, `doc1`, `brl1`, `brl4`, and one-connection tests `brl2` and `brl3`. Additional exported entry points are `test_trans2rename()`, `test_nttransrename()`, `torture_bench_oplock()`, and `torture_hold_oplock()`.

Global `break_info` records the last break fnum, break level, count, and failures. Oplock handlers include `oplock_handler_ack_to_given()`, `oplock_handler_ack_to_none()`, `oplock_handler_timeout()`, `oplock_handler_close()`, and `oplock_handler_hold()`. Support helpers include `open_connection_no_level2_oplocks()`, `timeout_cb()`, `torture_wait_for_oplock_break()`, `get_break_level1_to_none_count()`, and `get_setinfo_break_count()`. Key APIs are `smbcli_oplock_handler()`, `smbcli_oplock_ack()`, `smb_raw_open()`, `smb_raw_close_send()`, `smb_raw_unlink()`, `smb_raw_rename()`, `smb_raw_setpathinfo()`, `smb_raw_setfileinfo()`, `smb_raw_pathinfo()`, `smb_raw_fileinfo()`, `smbcli_lock()`, `smbcli_write()`, and `tevent_loop_once()`.

## Control flow
The test functions share a common scaffold: set up `\test_oplock`, unlink test files, install oplock handlers on one or more transports, issue `RAW_OPEN_NTCREATEX` requests with oplock request flags, perform a second operation that may contend with the cached handle, run `torture_wait_for_oplock_break()`, and compare `break_info` plus returned oplock levels and statuses.

The exclusive tests cover share-none versus share-all behavior, second opens that should or should not break, unlink/rename behavior, `setpathinfo` EOF and rename updates, attribute-only opens, delete-access opens, create-disposition-specific break levels, and conversion from exclusive to level-II. The level-II test specifically verifies that an unacknowledged break to none happens once and that later writes do not generate duplicate breaks.

The batch tests cover the broadest surface. They verify unlink and open contention, handler choices that ack to none or close the file, self reads and writes, attribute-only opens, second and third level-II opens, set EOF/allocation updates, `qpathinfo`, ordinary rename and NT rename, setfileinfo/setpathinfo rename, delete-on-close behavior, client support for level-II oplocks, timeout timing, and path attribute updates that should not break. Target-specific branches encode known Windows and Samba differences for XP, Windows Server 2003/2008/2012, Samba3, and Samba4.

Specialized tests include `test_raw_oplock_stream1()`, which is skipped for Samba3/4 and checks named stream/default stream oplock grant and break behavior; `test_raw_oplock_doc()`, which expects a second open to return `DELETE_PENDING` without an oplock break after delete-on-close; and BRL tests that exercise interaction between batch/exclusive oplocks and byte-range lock acquisition with one handle, two handles on one connection, and two clients.

`torture_bench_oplock()` opens a configurable number of connections, installs a close-on-break handler, and repeatedly opens the same file with a batch oplock from each connection for a configured time limit to measure and stress oplock handoff. `torture_hold_oplock()` opens four files with different share-access and close-on-break behavior, writes one byte to each, then waits in the event loop for manual external oplock experiments.

## State and persistence
Server state is concentrated under `\test_oplock`, plus individual files for each test. The persistent behavior under test includes open-handle state, share-mode state, cached oplock levels, break delivery, break acknowledgements, file rename identity, byte-range lock state, alternate stream state, delete-on-close state, and client capability negotiation. Local process state is mostly `break_info`; the manual hold mode also uses the static `hold_info[]` table to map fnums to close-on-break behavior. Cleanup generally exits sessions and deletes the test tree, but benchmark/manual modes are intentionally long-running or externally driven.

## Dependencies and integration points
The file depends on Samba's raw SMB client API, tevent, command-line credentials, resolver and loadparm configuration, torture target-detection macros (`TARGET_IS_*`), and raw rename tests that call `test_trans2rename()` and `test_nttransrename()` from this file because oplock handling is required. `open_connection_no_level2_oplocks()` exercises client option integration by creating a special connection with `use_level2_oplocks = false`.

## Risks
Oplock tests are timing-sensitive: `torture_wait_for_oplock_break()` waits only about 100 ms for most breaks, while timeout tests rely on the configured server oplock timeout. Slow transports can cause false negatives. `break_info` is global and must be zeroed before each expected event; missing resets would make tests order-dependent. Several branches intentionally encode known server-version quirks, making the suite brittle when target detection is wrong or server behavior changes. Async close from inside a break handler can race with later explicit close calls. The manual hold mode loops indefinitely and leaves files open by design.

## Test signals
Strong signals are wrong `oplock_level` returns (`BATCH_OPLOCK_RETURN`, `EXCLUSIVE_OPLOCK_RETURN`, `LEVEL_II_OPLOCK_RETURN`, `NO_OPLOCK_RETURN`), wrong `break_info.count`, fnum, or break level, unexpected handler failures, wrong status codes (`SHARING_VIOLATION`, `DELETE_PENDING`, `LOCK_NOT_GRANTED`, `OK`), duplicate breaks after timeout, missing rename visibility through fileinfo, and benchmark throughput or handoff failures in `torture_bench_oplock()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/oplock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/pingpong.c -->
# sources/user-network-fs/samba/source4/torture/raw/pingpong.c

## Purpose
This file implements `torture_ping_pong()`, a long-running byte-range-lock coordination benchmark. Multiple clients can run against the same file and lock ring, passing exclusive ownership from byte offset to byte offset. Optional reads and writes make each participant observe and advance per-slot counters while lock throughput is reported once per second.

## Important APIs, types, and functions
Local helpers are `lock_byte()`, `unlock_byte()`, `write_byte()`, and `read_byte()`. The exported entry point is `torture_ping_pong()`. The code uses `union smb_lock`, `struct smb_lock_entry`, `union smb_write`, `union smb_read`, `RAW_LOCK_LOCKX`, `LOCKING_ANDX_LARGE_FILES`, `RAW_WRITE_WRITEX`, `RAW_READ_READX`, `smb_raw_lock()`, `smb_raw_write()`, `smb_raw_read()`, `smbcli_open()`, `torture_open_connection()`, and torture settings accessors.

## Control flow
`torture_ping_pong()` requires `torture:filename` and `torture:num_locks` settings. It also reads `read`, `write`, and `lock_timeout`, defaulting to no reads/writes and a 100-second lock timeout. It opens one SMB connection and creates or opens the selected file read/write. It writes a zero byte at offset `num_locks` to establish file length, then locks byte zero.

The main loop advances index `i` around the ring. For each slot it locks `(i + 1) % num_locks`, optionally reads byte `i` and computes how much that byte changed since this process last saw it, optionally writes `val[i] + 1` to byte `i`, then unlocks byte `i`. This creates a handoff where the next byte is locked before the current byte is released. Once per second it prints `2 * count / elapsed` as locks per second because each loop iteration performs one lock and one unlock.

`lock_byte()` sends a single large-file LockingX lock. If `lock_timeout` is zero, file-lock conflicts and lock-not-granted statuses are handled by busy retrying until the lock succeeds. Otherwise the server-side timeout is used and any non-OK result exits the process. `unlock_byte()` sends a single unlock with a fixed 100-second timeout. `write_byte()` and `read_byte()` perform one-byte raw write/read operations and exit on failure.

## State and persistence
Server state is the user-specified shared file and byte-range locks over offsets `0..num_locks-1`. If writes are enabled, each byte stores a modulo-256 counter updated by whichever process currently owns that slot. Local state includes a talloc-allocated `val[]` shadow array of last observed byte values, increment tracking, loop counters, and the current ring index. There is no cleanup path because this benchmark is designed to run until externally stopped.

## Dependencies and integration points
The test depends on a configured SMB torture target and externally coordinated settings so multiple processes use the same filename and lock count. It is modeled on `lockbench.c` and integrates only with the raw SMB client/torture utility layer. It assumes strict byte-range lock enforcement and uses `cli->tree->session->pid` as the lock owner PID.

## Risks
This is an infinite benchmark loop with `exit(1)` on helper failures, so it does not provide normal teardown. With `lock_timeout=0`, conflicting locks cause a busy retry loop that can consume CPU. Invalid `num_locks` values are only checked for missing `-1`; zero would lead to modulo-by-zero behavior in the main loop. Multiple participants must agree on file and lock count or the ring protocol becomes meaningless. Optional writes use byte counters and naturally wrap at 255.

## Test signals
Operational signals are sustained locks-per-second output, periodic `data increment = N` changes when reads are enabled, absence of lock/unlock/read/write fatal messages, and coordinated progress among all participating clients. Failures indicate broken byte-range-lock conflict handling, lock timeout behavior, raw read/write errors, or configuration mismatches between participants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/pingpong.c -->
