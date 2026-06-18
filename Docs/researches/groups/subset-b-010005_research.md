# subset-b-010005 Research

Grouped research for Samba SMB2 torture sources under `sources/user-network-fs/samba/source4/torture/smb2`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/replay.c -->
# sources/user-network-fs/samba/source4/torture/smb2/replay.c

## Purpose
`replay.c` is the SMB2/SMB3 torture suite for replay semantics: how a server handles `SMB2_FLAGS_REPLAY_OPERATION`, DurableHandleReqV2 create GUID matching, persistent handle reconnect, multi-channel channel sequence numbers, lease/oplock break interactions, and corner cases where a replay arrives while an original create is still pending. The suite is intentionally both a conformance probe and a regression test for Samba bugs such as bug 14449, with paired "sane" and "windows" expectations where Windows behavior diverges from Samba's intended semantics.

## Important APIs, Types, And Functions
The core helpers are local macros `CHECK_VAL`, `CHECK_STATUS`, `CHECK_CREATED`, `CHECK_HANDLE`, `CHECK_CREATE_OUT`, and `WAIT_FOR_ASYNC_RESPONSE`; they convert protocol mismatches into torture failures and make replayed create responses comparable to earlier reference responses. The tests are registered from `torture_smb2_replay_init()` using `torture_suite_add_1smb2_test()` and `torture_suite_add_2smb2_test()`.

The high-level test families are:

- `test_replay_commands()` toggles replay mode on the current SMB2 session and verifies ordinary create, write, flush, read, setinfo, getinfo, ioctl, and lock operations still return expected statuses.
- `test_replay_regular()` proves regular creates without a create GUID are not de-duplicated by the replay flag.
- `test_replay_dhv2_oplock*()` and `test_replay_dhv2_lease*()` cover DurableHandleReqV2 single-channel replay with batch oplocks, leases, changed requested oplock/lease state, changed share modes, and mismatched lease keys.
- `_test_dhv2_pending1_vs_violation()`, `_test_dhv2_pending1_vs_hold()`, `_test_dhv2_pending2_vs_hold()`, and `_test_dhv2_pending3_vs_hold()` are matrix drivers for pending creates blocked behind lease or oplock breaks, including single-channel, disconnected multi-channel, and blocked-transport multi-channel cases.
- `test_channel_sequence_table()` and `test_channel_sequence()` exercise channel sequence number windows for write, ioctl, and setinfo with and without replay.
- `test_replay3()` through `test_replay7()` cover multi-channel durable create replay, I/O ordering, persistent handles, error-code behavior for duplicate create GUIDs, and a notify/cancel channel sequence regression.
- `test_durable_reconnect_replay1()`, `test_durable_reconnect_replay2()`, `test_durable_reconnect_replay3()`, and `test_replay_twice_durable()` cover reconnection and repeated replay behavior for durable or persistent lease-backed handles.

The file depends heavily on Samba SMB2 client structures and helpers: `struct smb2_tree`, `struct smb2_transport`, `struct smb2_session`, `struct smb2_create`, `struct smb2_handle`, `struct smb2_lease`, `struct smb2_lease_break_ack`, `struct smb2_break`, `struct smb2_request`, `union smb_fileinfo`, `union smb_setfileinfo`, `union smb_ioctl`, `smb2_create()`, `smb2_create_send()/recv()`, `smb2_lease_v2_create()`, `smb2_oplock_create_share()`, `smb2_session_channel()`, `smb2_session_setup_spnego()`, `smb2cli_session_start_replay()`, `smb2cli_session_stop_replay()`, `smb2cli_session_reset_channel_sequence()`, `smb2cli_session_increment_channel_sequence()`, and connection/tcon capability accessors.

## Control Flow
Most tests first require SMB 3.x because replay semantics, durable v2 opens, channel sequence checks, and multi-channel are SMB3-era behavior. Tests then create `replaytestdir`, unlink any target file, set oplock and lease break handlers, build a `struct smb2_create`, issue an original create, and either replay it immediately or force a conflicting server state before replaying.

Single-channel durable replay tests follow this pattern: create a file with `durable_open_v2 = true`, `persistent_open` as needed, and a random `create_guid`; save the successful output; call `smb2cli_session_start_replay()`; resend a create with the same GUID; stop replay; then verify either an exact replay response, an access-denied response for invalid oplock/lease substitution, or a duplicate-object status when the replay flag is absent. Share capability checks adjust expectations for scale-out shares, which may downgrade oplocks and deny durable handles.

The pending-create matrix drivers are more involved. Client 1 opens a file with a batch oplock or RWH lease and often with full sharing. Client 2 sends an asynchronous durable v2 create with a new create GUID and requested level of none, batch oplock, or lease. The driver waits until the create is pending behind an oplock or lease break, sends replayed creates on the same or other channels, observes the expected immediate rejection (`NT_STATUS_FILE_NOT_AVAILABLE` for Samba's sane behavior or `NT_STATUS_ACCESS_DENIED`/`NT_STATUS_SHARING_VIOLATION` in Windows-mode variants), releases the blocker by close or break acknowledgement, and then verifies the original pending create and a later replay either complete with matching handle/lease state or preserve the expected failure.

Multi-channel tests bind additional transports to the same session with `smb2_session_channel()`, manipulate channel sequence numbers, disconnect or block transports, and validate replay behavior as the server's notion of current and stale channel sequence changes. `test_channel_sequence_table()` walks explicit low, high, wraparound, and random channel sequence values around the allowed window and checks write/ioctl/setinfo acceptance.

Reconnect tests intentionally free or disconnect trees while durable or persistent opens remain server-side. They reconnect using saved transport options and sometimes a previous session id, then retry the create under replay and verify that the resurrected handle is usable with a write. `test_replay_twice_durable()` confirms a second replay after the handle has been used is treated as a normal open rather than a second durable reconnect.

## State And Persistence
The suite creates and deletes files below `replaytestdir` or random `lease_break-*.dat` paths. Durable and persistent handle state persists on the server across client-side tree/session teardown, connection loss, and reconnect. Replay identity is carried by create GUIDs plus SMB session/client identity, and replay mode is client-side state toggled on `smbXcli` sessions before selected requests.

Lease, oplock, and channel sequence state are central. The tests install global torture break handlers, set skip-ack flags to deliberately hold breaks pending, and track `break_info`/`lease_break_info` counts, transport identity, break level, lease key, lease epoch, and acknowledgement payloads. Multi-channel tests also mutate per-session channel sequence numbers and, in blocked-transport cases, manipulate transport blocking via the torture transport-blocking helpers.

Cleanup is explicit but complex: handles are closed when non-null, test directories are removed with `smb2_deltree()`, sessions/transports are disconnected in matrix tests, and replay mode is stopped in `done` paths where needed. Some tests call `talloc_free(tree)` or `TALLOC_FREE(tree)` because the torture registration hands in owned tree instances.

## Dependencies And Integration Points
This file integrates with the Samba torture harness, SMB2 client library, command-line credentials, resolver and loadparm configuration, event loop, security constants, and the SMB2 oplock and lease break handler test utilities. It requires working SMB3 negotiation and selectively requires server capabilities: `SMB2_CAP_LEASING`, `SMB2_CAP_MULTI_CHANNEL`, and `SMB2_CAP_PERSISTENT_HANDLES`; persistent handle tests also require continuously available shares, while several hold tests skip scale-out shares.

The suite is registered as the `smb2.replay` torture suite and is meant to run against Samba and Windows servers. The "windows" variants act as compatibility documentation rather than Samba's preferred behavior.

## Risks
These tests are timing-sensitive because they depend on asynchronous create requests reaching pending state, lease/oplock breaks not being auto-acknowledged too early, server request timeouts, and transport disconnect or blocking behavior. A slow or unusual server can turn expected statuses into timeouts. The matrix functions intentionally free or disconnect trees and transports; cleanup ordering is important to avoid use-after-free in the harness.

Expected status depends on negotiated dialect, share capabilities, persistent-handle support, leasing support, and whether the server follows Windows quirks. Scale-out and continuously available share behavior changes durable/persistent grant expectations. Random filenames, GUIDs, lease keys, and generated strings reduce collision risk but make failures harder to reproduce unless torture logs are kept.

## Test Signals
Important pass signals include exact replayed create output matching the original where required; no unexpected lease/oplock breaks during pure replay; correct `NT_STATUS_FILE_NOT_AVAILABLE`, `NT_STATUS_ACCESS_DENIED`, `NT_STATUS_SHARING_VIOLATION`, `NT_STATUS_DUPLICATE_OBJECTID`, or `NT_STATUS_OK` status in the documented scenario; stable handle equality or inequality where asserted; correct durable/persistent output flags and 300-second durable timeout; correct lease key, epoch, and state; successful writes after durable reconnect; and no stale-channel writes, ioctls, or setinfo calls succeeding outside the allowed sequence window.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/replay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/samba3misc.c -->
# sources/user-network-fs/samba/source4/torture/smb2/samba3misc.c

## Purpose
`samba3misc.c` provides SMB2 coverage for Samba3-specific miscellaneous behavior. Its current test, `localposixlock1`, verifies that an SMB2 byte-range lock conflicts correctly with a local POSIX lock taken directly on the underlying exported file, and that a blocking SMB2 lock completes once the local POSIX lock is released.

## Important APIs, Types, And Functions
The file defines `CHECK_STATUS`, `BASEDIR`, and a local `WAIT_FOR_ASYNC_RESPONSE` loop. `torture_smb2_tree_disconnect_timer()` is a tevent timer callback that disconnects the tree's underlying `smbXcli_conn` with `NT_STATUS_CTX_CLIENT_QUERY_TIMEOUT` if the blocking lock never completes. `torture_samba3_localposixlock1()` is the actual test, and `torture_smb2_samba3misc_init()` registers it as `smb2.samba3misc.localposixlock1`.

The test uses Samba SMB2 helpers (`torture_smb2_testdir()`, `torture_smb2_testfile()`, `smb2_lock()`, `smb2_lock_send()`, `smb2_lock_recv()`, `smb2_util_close()`, `smb2_deltree()`), POSIX calls (`open()`, `fcntl(F_SETLK)`, `close()`), `struct flock`, `struct smb2_lock`, `struct smb2_lock_element`, and the event loop/timer APIs.

## Control Flow
The test creates `samba3misc.smb2`, opens a test file over SMB2, and computes the corresponding local filesystem path from `--option=torture:localdir=<LOCALDIR>`. It opens that local path and takes a one-byte write lock at offset zero with `fcntl(F_SETLK)`.

It then sends an SMB2 exclusive byte-range lock with `SMB2_LOCK_FLAG_FAIL_IMMEDIATELY` and expects `NT_STATUS_LOCK_NOT_GRANTED`. Next it sends a blocking SMB2 exclusive lock asynchronously, arms a five-second disconnect timer, waits until the async request reaches a cancelable/pending state, closes the local file descriptor to release the POSIX lock, and expects `smb2_lock_recv()` to return `NT_STATUS_OK`.

## State And Persistence
State is split between server-side SMB2 open/lock state and a direct local POSIX byte-range lock on the same backing file. The test depends on the server honoring local POSIX lock conflicts for ordinary SMB2 clients when `posix locking = yes`. Persistent filesystem artifacts are removed with `smb2_deltree()` at the end, and the local descriptor is closed on all cleanup paths.

## Dependencies And Integration Points
The test requires a Samba share whose server-side path is also locally accessible to the torture process through `torture:localdir`. It depends on POSIX locking support in the underlying filesystem and Samba3 locking integration. It integrates with the SMB2 torture suite as `SMB2 Samba3 MISC`.

## Risks
The test will fail or be skipped by assertion if `torture:localdir` is not configured, if the local path does not match the SMB share path, if the filesystem does not implement advisory locks as expected, or if `posix locking = no`. The timer disconnect is a safety net, but timeout behavior may mask whether the failure was a missing lock conflict, an event-loop issue, or an unexpectedly long blocking lock.

## Test Signals
Expected signals are successful directory/file setup, successful local `open()` and `fcntl()` locking, immediate `NT_STATUS_LOCK_NOT_GRANTED` for the non-blocking SMB2 lock, pending behavior for the blocking SMB2 lock, and `NT_STATUS_OK` after closing the local descriptor. The final cleanup should close the SMB2 handle and remove `samba3misc.smb2`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/samba3misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/scan.c -->
# sources/user-network-fs/samba/source4/torture/smb2/scan.c

## Purpose
`scan.c` is an SMB2 probing suite rather than a normal pass/fail behavioral test. It scans SMB2 opcode, getinfo, setinfo, and find information spaces to discover which values a target server accepts, rejects, or handles unusually. Its suite description explicitly says "scan target (not a test)".

## Important APIs, Types, And Functions
The suite contains `torture_smb2_getinfo_scan()`, `torture_smb2_setinfo_scan()`, `torture_smb2_find_scan()`, `torture_smb2_scan()`, and `torture_smb2_scan_init()`. It uses `struct smb2_tree`, `struct smb2_getinfo`, `struct smb2_setinfo`, `struct smb2_find`, `struct smb2_request`, `struct smb2_handle`, `smb2_getinfo()`, `smb2_setinfo()`, `smb2_find()`, `smb2_request_init_tree()`, `smb2_transport_send()`, `smb2_request_receive()`, and `smb2_request_destroy()`.

Setup helpers include `torture_smb2_connection()`, `smb2_connect()`, `torture_setup_complex_file()`, `torture_setup_complex_dir()`, `torture_smb2_testfile()`, `torture_smb2_testdir()`, `smb2_util_roothandle()`, and simple unlink/rmdir cleanup helpers. The scanner reads host/share settings, command-line credentials, resolver configuration, socket options, GENSEC settings, and SMB client options.

## Control Flow
`torture_smb2_getinfo_scan()` connects to the target, creates a complex file, stream, directory, and directory stream, opens file and directory handles, then loops `info_type` from 1 to 4 and `info_class` from 0 to 255. For both file and directory handles it calls `smb2_getinfo()` and logs any response that is not `NT_STATUS_INVALID_INFO_CLASS`, including returned blob length and a data dump.

`torture_smb2_setinfo_scan()` creates a complex file and alternate stream, opens the file, allocates a 1024-byte zero blob, and probes level values formed as `(info_class << 8) | info_type` for info types 1 through 4 and classes 0 through 255. It logs levels that are not rejected as `NT_STATUS_INVALID_INFO_CLASS`.

`torture_smb2_find_scan()` opens the share root, sets pattern `*`, restart continuation, and a 64 KiB response buffer, then scans find levels 1 through 255. It suppresses ordinary invalid, invalid-parameter, and not-supported statuses, logging and dumping any other responses.

`torture_smb2_scan()` connects manually, sets request timeout to three seconds, and sends raw SMB2 request bodies for opcodes 0 through 999. If the connection drops or times out, it reconnects and continues; otherwise it destroys the request and logs the returned status.

## State And Persistence
The getinfo and setinfo scanners create temporary `scan-getinfo.*` and `scan-setinfo.*` files and streams; find scans use the root handle only; opcode scanning maintains only connection/session state. Cleanup removes the main file and directory names, but alternate stream cleanup is mostly incidental to removing the base object.

## Dependencies And Integration Points
This file integrates with the SMB2 torture harness, low-level SMB2 transport constructors, Samba command-line credentials, resolver and loadparm contexts, and debug dumping. It is useful for protocol exploration, server fingerprinting, and regression investigation when a server starts accepting or rejecting a level differently.

## Risks
The opcode scan is intentionally aggressive and can disconnect the server, trigger unusual error paths, or produce noisy logs. It sends minimally initialized request bodies, so results are not always meaningful as standards conformance. The getinfo/setinfo/find scans can expose server bugs in information-level parsing and may produce large binary dumps. Because it treats many nonstandard responses as interesting rather than fatal, it is best run manually or in controlled diagnostics, not as a stable CI pass/fail suite.

## Test Signals
Primary signals are the logged "active opcode" statuses and the non-default info/find levels with blob lengths and dumps. Unexpected crashes, reconnect loops, hangs beyond the configured request timeout, or sudden changes in accepted info classes are the useful regression indicators.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/secleak.c -->
# sources/user-network-fs/samba/source4/torture/smb2/secleak.c

## Purpose
`secleak.c` is an SMB2 security memory leak torture helper. It repeatedly attempts failed session setup with deliberately invalid credentials and prints talloc allocation reports, allowing developers to inspect whether failed authentication leaks client-side or security-related allocations over time.

## Important APIs, Types, And Functions
`try_failed_login()` creates a new SMB2 session on the existing transport, builds invalid `struct cli_credentials`, and calls `smb2_session_setup_spnego()`. `torture_smb2_sec_leak()` is the exported test entry point used by the SMB2 torture suite. Important APIs and types include `struct smb2_tree`, `struct smb2_session`, `smb2_session_init()`, `smb2cli_session_current_id()`, `cli_credentials_init()`, `cli_credentials_set_conf()`, `cli_credentials_set_domain()`, `cli_credentials_set_username()`, `cli_credentials_set_password()`, `smb2_session_setup_spnego()`, `talloc_steal()`, `talloc_report()`, and `time_mono()`.

## Control Flow
`torture_smb2_sec_leak()` reads `torture:timelimit`, defaulting to 20 seconds, and loops until monotonic time reaches that deadline. Each iteration calls `try_failed_login()` and asserts the result. After every failed login attempt it prints a talloc report to stdout.

Inside `try_failed_login()`, a temporary SMB2 session is initialized against the tree's transport and uses the current session id as the previous/session context. Invalid domain, username, and password values are specified. The expected result of SPNEGO session setup is `NT_STATUS_LOGON_FAILURE`; success or a different status is treated as a test failure. Before freeing the temporary session, the transport is stolen back to the original tree session because `smb2_session_init()` takes ownership of it.

## State And Persistence
The test does not create files. It repeatedly mutates client-side session/transport ownership and authentication state. The crucial persistent pointer is `tree->session->transport`; without stealing it back before freeing the temporary session, later iterations would hold an invalid transport pointer. The allocation reports expose whether repeated failure paths grow talloc trees.

## Dependencies And Integration Points
The file depends on Samba's SMB2 session setup, GENSEC settings, credential handling, talloc ownership model, and torture context settings. It is meant to run against a live authenticated SMB2 tree while probing failed secondary session setup behavior.

## Risks
Because the test intentionally performs many failed logins, it can trigger account lockout or audit noise on real authentication backends if invalid attempts are counted. It is also sensitive to the talloc ownership contract around transports; future changes to `smb2_session_init()` ownership semantics could make the steal-back workaround wrong. The output is diagnostic rather than a precise automated leak detector unless compared externally.

## Test Signals
Expected behavior is repeated `NT_STATUS_LOGON_FAILURE` with no crash and stable talloc report shape over the configured time window. A successful login with invalid credentials, growing allocation reports, transport invalidation on the next iteration, or statuses other than logon failure indicate a regression or environment issue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/secleak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/sessid.c -->
# sources/user-network-fs/samba/source4/torture/smb2/sessid.c

## Purpose
`sessid.c` verifies SMB2 server handling of requests sent with an invalid session id. It opens a file under a valid session, temporarily corrupts the SMB2 session id in the client, attempts a file information query, and expects the server to reject it with `NT_STATUS_USER_SESSION_DELETED`.

## Important APIs, Types, And Functions
The local helper `smb2cli_session_set_id()` preserves existing session flags while calling `smb2cli_session_set_id_and_flags()`. The exported test function is `run_sessidtest()`. It uses `struct smb2_tree`, `struct smb2_create`, `struct smb2_handle`, `union smb_fileinfo`, `smb2_util_unlink()`, `smb2_create()`, `smb2cli_session_current_id()`, `smb2_getinfo_file()`, and `smb2_util_close()`.

## Control Flow
The test removes `sessid.tst`, creates or overwrites it with read/write access and broad share access, and saves the returned handle. It records the current SMB2 session id from the tree's `smbXcli` session, sets the session id to `session_id + 1234`, then calls `smb2_getinfo_file()` for `RAW_FILEINFO_SMB2_ALL_INFORMATION` on the still-valid file handle.

If the query succeeds, the test fails immediately. Otherwise it asserts the exact status is `NT_STATUS_USER_SESSION_DELETED`. It restores the original session id before closing the handle and unlinking the file.

## State And Persistence
The only filesystem state is `sessid.tst`, which is removed before and after the test. The important mutable client state is the session id stored in the `smbXcli` session; it is deliberately corrupted for one request and restored before cleanup so the close can use the valid session again.

## Dependencies And Integration Points
This test is part of the SMB2 torture suite and uses the low-level SMB2 client session id setter from `smbXcli_base`. It validates server session lookup behavior independent of filename parsing or access checks because the handle is already valid but the session id is wrong.

## Risks
The helper stores the current session id in a `uint32_t` even though SMB2 session ids are 64-bit in the underlying API. If test environments ever use ids that do not fit in 32 bits, the saved/restored id could be truncated. The test also assumes adding 1234 creates a definitely invalid id, which is extremely likely but not formally impossible if ids are reused or truncated in unusual test harnesses.

## Test Signals
The expected signal is a failed `smb2_getinfo_file()` returning exactly `NT_STATUS_USER_SESSION_DELETED`, followed by successful restoration of the original session id, successful close, and cleanup unlink. Any success with the wrong id or a different error status is a server behavior difference worth investigating.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/sessid.c -->
