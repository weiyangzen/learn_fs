# subset-b-009999 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/durable_v2_open.c -->
# sources/user-network-fs/samba/source4/torture/smb2/durable_v2_open.c

## Purpose

This file defines Samba torture suites for SMB2 durable handle v2, persistent handle, lease, oplock, reconnect, and reconnect-delay behavior. It is not production server code; it is a protocol conformance and regression test harness that drives `smb2_create`, reconnects sessions or transports, and asserts that server-side open state is preserved, rejected, downgraded, purged, or timed out according to SMB2 durable v2 semantics.

The file exports three suite initializers: `torture_smb2_durable_v2_open_init()`, `torture_smb2_durable_v2_delay_init()`, and `torture_smb2_durable_v2_regressions_init()`. These register individual tests under the `durable-v2-open`, `durable-v2-delay`, and `durable-v2-regressions` suite names.

## Important APIs, Types, And Helpers

The tests are built around Samba's SMB2 client/torture APIs:

- `smb2_create`, `smb2_close_send`, `smb2_util_close`, `smb2_util_unlink`, `smb2_deltree`, `smb2_lock`, `smb2_write`, `smb2_setinfo_file`, and `smb2_util_write` perform protocol operations against a test share.
- `torture_smb2_connection()` and `torture_smb2_connection_ext()` establish fresh connections, optionally reusing a previous session id and customized `smbcli_options`.
- `smb2_oplock_create_share()`, `smb2_lease_create()`, `smb2_lease_create_share()`, `smb2_lease_v2_create()`, `smb2_generic_create()`, and `smb2_generic_create_share()` populate `struct smb2_create` requests for the relevant open style.
- `smb2cli_tcon_capabilities()` and `smb2cli_conn_server_capabilities()` gate behavior on share capabilities such as continuous availability, scaleout, and leasing.
- `torture_lease_handler`, `lease_break_info`, `CHECK_NO_BREAK`, `CHECK_BREAK_INFO_V2`, and `torture_reset_lease_break_info()` integrate with `lease_break_handler.h` to validate lease break side effects.

Local assertion macros centralize expected protocol results:

- `CHECK_STATUS(status, correct)` and `CHECK_VAL(v, correct)` fail the current test through the `done:` cleanup path.
- `CHECK_CREATED(io, created, attr)` validates `create_action`, size, file attributes, and reserved fields.
- `CHECK_LEASE_V2(io, state, oplevel, key, flags, parent, epoch)` validates v2 lease response shape, key, state, flags, parent lease key, duration, and epoch.

The local `break_info` object plus `torture_oplock_handler()` and `torture_oplock_close_callback()` capture an oplock break path for the AppInstanceId test. The handler increments a counter and asynchronously closes the broken handle.

The main table-driven types are `struct durable_open_vs_oplock` and `struct durable_open_vs_lease`. Their tables encode combinations of requested oplock/lease level, share mode, and expected durable or persistent grant. Separate continuous-availability tables expect persistent handles when the share advertises `SMB2_SHARE_CAP_CONTINUOUS_AVAILABILITY`.

## Control Flow

The suite starts with table-driven grant checks. `test_durable_v2_open_create_blob()` verifies durable v2 create contexts, scaleout-share differences, default timeout normalization, and invalid combinations of durable-request and durable-reconnect blobs. `test_durable_v2_open_oplock()` and `test_durable_v2_open_lease()` iterate all encoded share/access combinations. They assert that durable v2 is granted only with batch oplocks or handle-capable leases, with scaleout shares downgrading batch to level II and suppressing non-persistent durable handles.

The reconnect tests then exercise progressively more realistic failure and recovery paths:

- `reopen1` proves reconnecting a still-live open on the same connection fails.
- `reopen1a` and `reopen1a-lease` reconnect sessions using `previous_session_id`; oplock durable reconnects tolerate a different client GUID, while lease-based durable reconnects require the original client GUID.
- `reopen2`, `reopen2b`, and `reopen2c` simulate TCP disconnects and test the v2/v1 reconnect matrix. V2 reconnect requires the original create GUID, while v1 reconnect can recover a v2-created durable handle in one compatibility path. A v1-created durable handle cannot be recovered through the v2 reconnect path.
- `reopen2-lease` and `reopen2-lease-v2` add lease key validation, required filename validation, and show that many create parameters are ignored during reconnect once the durable handle, create GUID, filename, and lease key are correct.

The lock and lease-state tests add durable state with byte-range locks and competing opens. `lock-oplock` and `lock-lease` prove a byte-range lock survives disconnect and can be unlocked after reconnect. `lock-noW-lease` demonstrates that a durable reconnect after a byte-range lock fails when the lease lacks write caching. `stat-and-lease`, `nonstat-and-lease`, and `statRH-and-lease` check how preexisting opens and stat-like access affect lease downgrades from `RWH` to `RH`.

The multi-handle tests validate disconnected handle retention and purging:

- `two-same-lease` and `two-different-lease` keep multiple durable opens through disconnect and reconnect.
- `keep-disconnected-rh-with-*` cases show disconnected read/handle leases can remain reconnectable when a second connection does a stat open, an `RH` durable open, an `RWH` open downgraded to `RH`, or an `RWH` disconnected handle coexists with a stat open.
- `purge-disconnected-rwh-with-*` and `purge-disconnected-rh-with-*` cases show when later opens, share-none opens, writes, or renames purge disconnected durable handles and make reconnect return `NT_STATUS_OBJECT_NAME_NOT_FOUND`.

The remaining suite entries cover special cases. `test_durable_v2_open_app_instance()` verifies that a second durable open with the same AppInstanceId replaces the first server-side open and the first close returns `NT_STATUS_FILE_CLOSED`. `test_persistent_open_oplock()` and `test_persistent_open_lease()` reuse the durable table runners with persistent requests and switch expectations based on continuous availability and scaleout capabilities. `test_durable_v2_setinfo()` is a regression test for reconnect after setting end-of-file information. `test_reconnect_twice()` verifies that reconnecting a durable handle twice refreshes the scavenger timeout rather than letting the first disconnect timer purge the second disconnected handle.

The delay and regression suites are registered separately. `test_durable_v2_reconnect_delay()` checks a zero timeout durable v2 open can reconnect immediately. `test_durable_v2_reconnect_delay_msec()` uses a one millisecond timeout, sleeps, and expects reconnect failure. `test_durable_v2_reconnect_bug15624()` requires `--option=torture:bug15624=yes` and a configured `error_inject` VFS module, then asserts a failed reconnect does not deadlock later unlink cleanup.

## State And Persistence Behavior

The persistent state under test is server durable-open state, not local file content alone. Each test creates a unique randomized filename or per-test directory, records the returned durable handle and create GUID, frees the SMB tree to simulate disconnect, and later attempts reconnect with the saved handle material. Success is detected by `NT_STATUS_OK`, `NTCREATEX_ACTION_EXISTED`, preserved oplock or lease response, and continued ability to close, unlock, write, or delete.

Lease tests also persist client-side `struct smb2_lease` values across reconnect. Correct lease key, create GUID, filename, and sometimes original client GUID are required to recover the server-side durable handle. The tests deliberately mutate lease keys, filenames, create GUIDs, and requested lease states to prove which fields are authoritative and which are ignored.

Cleanup is explicit and defensive. Most tests track handles through pointer variables set to `NULL` when a handle is intentionally invalidated or transferred. `done:` blocks close non-null handles, unlink test files, remove per-test directories, send keepalives where needed to drain break handling, and free SMB trees and talloc contexts. Random filenames reduce collisions if a previous run left state behind.

## Dependencies And Integration Points

This file depends on Samba torture infrastructure and SMB2 client libraries from `includes.h`, `libcli/smb2/smb2.h`, `libcli/smb2/smb2_calls.h`, `smbXcli_base.h`, `torture/torture.h`, `torture/smb2/proto.h`, `librpc/ndr/libndr.h`, and `lease_break_handler.h`.

The suites integrate with the broader torture runner through `torture_suite_add_1smb2_test()`, `torture_suite_add_2smb2_test()`, and `torture_suite_create()`. Several tests require server capabilities: leasing tests skip without `SMB2_CAP_LEASING`; persistent-handle expectations depend on `SMB2_SHARE_CAP_CONTINUOUS_AVAILABILITY`; scaleout shares alter oplock and durable-handle expectations through `SMB2_SHARE_CAP_SCALEOUT`.

The regression test for bug 15624 integrates with a special server setup using `vfs objects = error_inject` and `error_inject:durable_reconnect=st_ex_nlink`; without the `torture:bug15624` setting it skips rather than producing a false failure.

## Risks And Edge Cases

The tests rely on timing in delay and scavenger cases. `sleep(4)`, `sleep(2)`, and `sleep(10)` make the tests sensitive to slow servers, scheduler delays, and durable-handle cleanup implementation details. The intent is clear, but failures in these cases may require examining timing before assuming protocol logic is wrong.

Several scenarios depend on exact server capability advertisement. A share configured as scaleout or continuous availability changes the expected durable/persistent outcome. Running the same test matrix against a differently configured share can produce expected divergences.

The tests intentionally free `tree` to simulate disconnect and later may use another tree for cleanup. Incorrect cleanup tree selection can leave files behind, especially after tests that set pointers to `NULL` because a reconnect attempt should have invalidated a handle. Most paths are careful, but interrupted runs can still leave randomized files.

Lease break tests assume the registered lease handler sees and records breaks in the expected order and that `smb2_keepalive()` drains pending notifications. Races in notification delivery could surface as test flakiness rather than durable-open logic errors.

The file is large and repetitive. Many tests differ only by lease state, competing open type, or expected status. Changes to helper macros or table entries can affect a broad test surface.

## Test Signals

Strong pass signals include exact NTSTATUS matches for invalid reconnect combinations, preservation of returned handle state after disconnect, correct absence of durable-query response blobs on reconnect, expected lease epoch increments, and correct lease break records for writes and renames.

Important negative signals include unexpected durable grants for non-batch oplocks, missing persistent grants on continuous-availability shares, reconnect success with wrong create GUID or lease key, reconnect failure after a valid durable disconnect, stale timeout purge after a successful intermediate reconnect, and deadlock or timeout during bug 15624 cleanup.

Capability-sensitive skips are expected for leasing-disabled servers and for the bug 15624 regression unless the required torture option and VFS error injection are configured.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/durable_v2_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/ea.c -->
# sources/user-network-fs/samba/source4/torture/smb2/ea.c

## Purpose

This file defines the `SMB2-EA` torture suite for extended attribute behavior, currently focused on ensuring Samba's NT ACL backing xattr is not exposed or writable through SMB2 EA operations. The test protects the boundary between internal server metadata stored in xattrs and client-visible SMB extended attributes.

## Important APIs, Types, And Functions

`find_returned_ea()` scans a `union smb_fileinfo` result from `RAW_FILEINFO_SMB2_ALL_EAS` and returns true when the requested EA name appears. It handles null EA names and uses `strequal()` because Windows may capitalize returned EA names.

`torture_smb2_acl_xattr()` is the only test case. It uses `torture_setting_string(tctx, "acl_xattr_name", NULL)` to obtain the server's configured ACL xattr name, creates a test directory and file, sets a normal EA named `void`, lists all EAs, verifies the ACL xattr name is absent, and then attempts to set the protected ACL xattr directly.

The test uses `struct ea_struct` for EA name/value pairs, `union smb_setfileinfo` with `RAW_SFILEINFO_FULL_EA_INFORMATION` for setting EAs, and `union smb_fileinfo` with `RAW_FILEINFO_SMB2_ALL_EAS` for listing EAs. It relies on `data_blob_string_const()` for test EA payloads and `smb2_getinfo_file()` / `smb2_setinfo_file()` for SMB2 query and set operations.

## Control Flow

The test deletes `BASEDIR`, recreates it through `torture_smb2_testdir()`, creates `BASEDIR\\test_acl_xattr`, and writes a benign EA named `void` so the all-EA query has data to enumerate. It then queries `RAW_FILEINFO_SMB2_ALL_EAS` and fails if `find_returned_ea()` sees the configured ACL xattr name. Finally it builds a new full-EA set request for the protected ACL xattr name and expects `NT_STATUS_ACCESS_DENIED`.

All assertions use `torture_assert_*_goto()` so failures jump to a shared cleanup block. The cleanup closes the handle if it is non-empty and deletes `BASEDIR`.

## State And Persistence Behavior

The only persistent filesystem state is a temporary directory named `test_ea`, a test file, and a benign EA value. The suite must not persist the protected ACL xattr through SMB2. The core persistence assertion is negative: server-private NT ACL xattr storage must remain invisible in all-EA enumeration and must reject client writes.

The required `acl_xattr_name` torture setting couples the test to the server configuration. Missing configuration is a hard assertion failure because the test cannot know which EA name to protect without it.

## Dependencies And Integration Points

This file depends on Samba's SMB2 torture helpers, NTSTATUS definitions, SMB2 call wrappers, and talloc-backed data blobs. The suite is registered by `torture_smb2_ea()` with `torture_suite_add_1smb2_test(suite, "acl_xattr", torture_smb2_acl_xattr)`.

The test integrates with server configurations that store NT ACLs in an xattr, typically using an `acl_xattr_name` torture option aligned with the VFS module's actual private xattr name. It exercises the SMB2 EA query/set path, not direct POSIX xattr APIs.

## Risks And Edge Cases

The test's accuracy depends on `acl_xattr_name` matching the server-side private metadata name. A wrong or missing option can either fail setup or check the wrong EA. Case handling is intentionally tolerant through `strequal()`, but namespace prefixes and server-specific xattr name formats still matter.

The assertion message for the benign EA set says "Setting EA should fail" even though the expected status is OK; this is only a misleading message string and not the asserted behavior.

Because the test first sets a normal EA, environments that disallow user EAs entirely will fail before reaching the ACL leak checks. Such a failure indicates the test share is not suitable for this case rather than proving ACL xattr exposure.

## Test Signals

Passing signals are: normal EA set succeeds, all-EA query succeeds, the configured ACL xattr name is absent from returned EAs, and direct set of that ACL xattr returns `NT_STATUS_ACCESS_DENIED`.

Failure signals are especially important if the ACL xattr appears in `RAW_FILEINFO_SMB2_ALL_EAS` output or if `smb2_setinfo_file()` can write that protected name. Either result would expose or corrupt server-private security metadata through the SMB2 EA interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/ea.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/getinfo.c -->
# sources/user-network-fs/samba/source4/torture/smb2/getinfo.c

## Purpose

This file defines the SMB2 getinfo torture suite. It verifies SMB2 file information, filesystem information, security information buffer sizing, normalized-name handling, granted-access reporting, and per-information-level access requirements. The suite exercises both ordinary query paths through typed wrappers such as `smb2_getinfo_file()` and raw `SMB2_GETINFO` buffer behavior through `smb2_getinfo()`.

## Important APIs, Types, And Tables

The static `file_levels[]` table lists file information classes tested against both a file and a directory, including basic, standard, internal, EA, access, position, mode, alignment, all, alternate name, stream, compression, network open, attribute tag, all EAs, SMB2 all information, and security descriptor queries.

The static `fs_levels[]` table lists filesystem information classes: volume, size, device, attribute, quota, full size, object id, and sector size. Each row stores the queried `union smb_fsinfo` and status.

`file_levels_access[]` maps information classes to access behavior. It distinguishes classes that are effectively unrestricted with a minimal synchronize-style open from classes that require `SEC_FILE_READ_ATTRIBUTE`, `SEC_FILE_READ_EA`, or `SEC_STD_READ_CONTROL`.

Key functions are:

- `torture_smb2_fileinfo()` creates a test file and directory, runs `torture_smb2_all_info()`, then queries every file info class for both handles.
- `torture_smb2_fileinfo_grant_read()` verifies `RAW_FILEINFO_ALL_INFORMATION` reports granted access exactly as opened when the handle has execute plus read-attribute access.
- `torture_smb2_fileinfo_normalized()` verifies `RAW_FILEINFO_NORMALIZED_NAME_INFORMATION` for mixed-case paths, streams, default data streams, and SMB dialect support.
- `torture_smb2_fsinfo()` queries every filesystem info class against the root handle.
- `torture_smb2_buffercheck_err()` is the common raw-buffer validator for fixed-size minimum, overflow, and exact-size behavior.
- `torture_smb2_qfs_buffercheck()`, `torture_smb2_qfile_buffercheck()`, and `torture_smb2_qsec_buffercheck()` validate buffer-length error codes for filesystem, file, and security getinfo.
- `torture_smb2_getfinfo_access()` verifies expected access-denied and success results for each file information class in `file_levels_access[]`.

## Control Flow

`torture_smb2_getinfo()` is the "complex" entry point. It connects, deletes stale `FNAME` and `DNAME`, creates complex test file and directory data including alternate streams, and then delegates to `torture_smb2_fileinfo()`.

`torture_smb2_fileinfo()` opens a test file and directory, runs a broad all-info helper for each, and iterates `file_levels[]`. Before querying security descriptors it sets `secinfo_flags = 0x7`; before querying all EAs it sets `SMB2_CONTINUE_FLAG_RESTART`. Each query is expected to return OK.

The normalized-name test constructs a nested mixed-case directory tree and stream paths. It first checks the root handle. Protocols below SMB 3.1.1 must return `NT_STATUS_NOT_SUPPORTED`; servers that do not implement the feature may skip. Once supported, it creates and reopens each path in lower and upper case, then asserts that normalized names return the canonical original case and strip default `:$DATA` suffixes where expected. It also opens a second connection capped at SMB 3.0.2 and verifies normalized-name queries are not supported there.

The buffer-check tests first issue a large-output query to capture the full response, then loop every output length from zero through the full length. Lengths below the fixed structure minimum must return `NT_STATUS_INFO_LENGTH_MISMATCH`; lengths at or above the fixed minimum but below the full response must return `STATUS_BUFFER_OVERFLOW`; the exact full length must return `NT_STATUS_OK`. The security buffer test is special: zero and one byte both must return `NT_STATUS_BUFFER_TOO_SMALL`.

`torture_smb2_getfinfo_access()` loops `file_levels_access[]` twice per row. It first opens with the listed unrestricted/minimal access and expects either OK or access denied depending on the row. It then reopens with the required access and expects the query to succeed.

## State And Persistence Behavior

The suite creates deterministic names `testsmb2_file.dat`, `testsmb2_dir`, `bufsize.txt`, and `torture_smb2_getfinfo_access`, plus a mixed-case nested tree rooted at `torture_dIr1N` for normalized-name checks. It uses `smb2_deltree()` to clear stale paths before setup and after the access test. Some helper-created handles are closed inline, but the tests primarily rely on short-lived torture connections and talloc lifetimes.

The normalized-name test intentionally persists multiple simultaneously open handles to the same objects through differently cased names. This preserves enough state to compare server canonicalization across file, directory, stream, default stream, lower-case, and upper-case opens.

The query result tables store status and output unions statically for the duration of the process. They are test result storage rather than durable filesystem state.

## Dependencies And Integration Points

This file depends on Samba's SMB2 client library, `smbXcli_base` protocol helpers, `torture/torture.h`, `torture/smb2/proto.h`, and `torture/util.h`. It uses helper functions such as `torture_setup_complex_file()`, `torture_setup_complex_dir()`, `torture_smb2_testfile_access()`, `torture_smb2_get_allinfo_access()`, `smb2_util_roothandle()`, and `torture_smb2_open()`.

The suite is registered by `torture_smb2_getinfo_init()` under suite name `getinfo`, with tests `complex`, `fsinfo`, `qfs_buffercheck`, `qfile_buffercheck`, `qsec_buffercheck`, `granted`, `normalized`, and `getinfo_access`.

The normalized-name behavior integrates with SMB dialect negotiation through `smbXcli_conn_protocol()` and an explicit second connection with `options3_0.max_protocol = PROTOCOL_SMB3_02`. Filesystem buffer checks contain Samba-specific skips for info classes 6 and 11 when targeting Samba3 or Samba4.

## Risks And Edge Cases

The normalized-name test is sensitive to server support and dialect. It correctly skips unsupported implementations, but a failure after support is detected indicates subtle canonical-name, stream-name, or default-data-stream behavior. Case-insensitive filesystems, stream support, and server normalization policy all matter.

The buffer-size tests assume specific fixed-size minima for numeric info classes, noted in comments as lacking proper defines. Changes in parser structures, protocol constants, or server response layout can require updating these hard-coded minima.

Some raw buffer comparisons are intentionally not performed for overflow responses because variable-length fields and reserved bytes are difficult to compare. The test validates status-code behavior, not byte-for-byte overflow payload shape.

The access tests rely on expected distinctions between unrestricted info classes and classes requiring read attributes, read EAs, or read control. Server-side permission model changes can affect these statuses and should be reviewed against MS-SMB2 semantics rather than treated as generic failures.

## Test Signals

Passing signals include OK statuses for all listed file and filesystem info levels, exact granted-access values for execute/read-attribute opens, correct normalized names for lower/upper/mixed-case and stream paths, expected `NT_STATUS_NOT_SUPPORTED` below SMB 3.1.1, correct buffer-length status transitions, and access denied only for classes queried without their required rights.

High-value failure signals include security descriptor queries succeeding without `SEC_STD_READ_CONTROL`, all-EA queries succeeding without `SEC_FILE_READ_EA`, normalized names returning the client-supplied casing rather than canonical casing, full-size buffer queries returning overflow, and undersized raw getinfo queries returning a generic failure instead of the expected SMB2 length status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/getinfo.c -->
