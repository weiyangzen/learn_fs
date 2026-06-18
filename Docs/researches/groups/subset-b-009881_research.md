# Research: subset-b-009881

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_smb2.c -->
# sources/user-network-fs/samba/source3/torture/test_smb2.c

## Purpose

`test_smb2.c` is a Samba source3 torture module that exercises SMB2 and SMB3 client/server behavior through the low-level `smb2cli_*` APIs and the higher-level `cli_*` wrappers. It is not a generic unit-test file; each exported `run_*` function is an integration-style torture entry point that creates real SMB sessions, tree connections, handles, files, directories, alternate data streams, DFS paths, and named pipe opens against the configured torture server/share.

The file validates protocol correctness around negotiation, session setup, reconnect, reauthentication, multichannel, tree/session invalidation, directory fsync permissions, truncation, path normalization, SACL and stream ACL handling, quota edge cases, delete-on-close semantics, DFS pathname parsing, and named pipe error behavior. Several tests encode Windows-compatible status expectations and Samba bug regressions.

## Important APIs, Types, and Functions

Primary state types:

- `struct cli_state`: Samba source3 client state, including `conn`, `timeout`, `smb2.session`, `smb2.tcon`, and share metadata.
- `struct smbXcli_session` and `struct smbXcli_tcon`: SMB2 session and tree-connect handles stored inside `cli_state`, sometimes deliberately replaced or forged to test invalid IDs.
- `struct tevent_context` and `struct tevent_req`: async request context for manual SMB2 session setup and pipe read tests.
- `DATA_BLOB`, `struct iovec`, and `struct auth_generic_state`: GENSEC/NTLMSSP security token exchange and session/channel key extraction.
- `struct security_descriptor`: DACL/SACL descriptors used for SACL and stream ACL tests.
- `SMB_NTQUOTA_STRUCT`: quota query result container.

Major Samba APIs exercised:

- Connection/session setup: `torture_init_connection`, `torture_close_connection`, `smbXcli_negprot`, `cli_session_setup_creds`, `cli_tree_connect`, `cli_tree_connect_creds`, `smb2cli_session_setup_send`, `smb2cli_session_setup_recv`, `smb2cli_session_set_session_key`, `smb2cli_session_create_channel`, `smb2cli_session_set_channel_key`.
- SMB2 file operations: `smb2cli_create`, `smb2cli_write`, `smb2cli_read`, `smb2cli_flush`, `smb2cli_close`, `smb2cli_query_directory`, `smb2cli_query_info`, `smb2cli_set_info`, `smb2cli_tdis`, `smb2cli_logoff`.
- Source3 convenience wrappers over SMB2: `cli_ntcreate`, `cli_smb2_create_fnum`, `cli_smb2_close_fnum`, `cli_writeall`, `cli_ftruncate`, `cli_qfileinfo_basic`, `cli_set_security_descriptor`, `cli_query_security_descriptor`, `cli_smb2_get_user_quota`, `cli_nt_delete_on_close`, `cli_list`, `cli_mkdir`, `cli_rmdir`, `cli_unlink`, `cli_close`.
- Security helpers: `auth_generic_client_prepare`, `auth_generic_set_creds`, `auth_generic_client_start`, `gensec_update`, `gensec_want_feature`, `gensec_session_key`, `security_descriptor_sacl_create`.
- DFS/path helpers: `smbXcli_conn_dfs_supported`, `smbXcli_tcon_is_dfs_share`, `smbXcli_conn_remote_name`, `smb2cli_tcon_set_values`, `smb2cli_tcon_current_id`, `smb2cli_tcon_flags`, `smb2cli_tcon_capabilities`, `push_ucs2_talloc`, `PULL_LE_U64`, `PUSH_LE_U8`, `PUSH_LE_U32`.

Exported torture entry points:

- `run_smb2_basic`: basic SMB2 negotiate, authenticated session, tree connect, create/write/flush/read/close, directory query, duplicate tree-disconnect, and duplicate logoff behavior.
- `run_smb2_negprot`: negotiates from CORE to latest, verifies SMB2 support, and asserts a second negotiation disconnects.
- `run_smb2_anonymous`: validates anonymous SMB2 session setup and ensures it is not marked as guest.
- `run_smb2_session_reconnect`: manually reconnects a session with `previous_session_id`, verifies old session invalidation, signing behavior, and successful operations after a new tree connect.
- `run_smb2_tcon_dependence`: proves file access is tied to the correct tree ID by trying a forged next TID.
- `run_smb2_multi_channel`: creates SMB3 channels with a shared client GUID, authenticates channel keys, performs IO across channels, and validates invalid-handle behavior after non-channel reauth/close.
- `run_smb2_session_reauth`: performs SMB2.10 reauthentication mid-session and checks which operations fail before the final auth leg and recover after it.
- `run_smb2_ftruncate`: writes a 1 MiB file through SMB2-backed `cli_*` APIs and repeatedly truncates it while checking size.
- `run_smb2_dir_fsync` and `test_dir_fsync`: verify directory flush access rules on a subdirectory and share root.
- `run_smb2_path_slash`: checks trailing backslash versus slash behavior for directory and file creates.
- `run_smb2_sacl`: validates SMB2-only SACL access rules requiring `SEC_FLAG_SYSTEM_SECURITY` plus appropriate write/read rights.
- `run_smb2_quota1`: checks SMB2 quota wrapper behavior against a root directory handle.
- `run_smb2_stream_acl`: creates an alternate data stream, reads/modifies/writes its DACL, then verifies the change.
- `run_list_dir_async_test`: checks directory listing returns directory attributes under async DOS mode.
- `run_delete_on_close_non_empty`: verifies a directory marked delete-on-close fails to close with `NT_STATUS_DIRECTORY_NOT_EMPTY` if a child file appears.
- `run_delete_on_close_nonwrite_delete_yes_test` and `run_delete_on_close_nonwrite_delete_no_test`: verify `hide unwritable`/`delete veto files` share-option behavior.
- DFS helpers `get_smb2_inode`, `smb2_inode_matches`, `smb2_dfs_delete`, `smb2_dfs_setinfo_name`, `smb2_dfs_rename`, `smb2_dfs_hlink`, and `test_smb2_dfs_sharenames` support the DFS tests.
- `run_smb2_dfs_paths`, `run_smb2_non_dfs_share`, `run_smb2_dfs_share_non_dfs_path`, and `run_smb2_dfs_filename_leading_backslash`: validate DFS path parsing, DFS flags, share capability handling, relative rename/link names, and leading backslash semantics.
- `run_smb2_pipe_read_async_disconnect`: starts an async named pipe read and disconnects, relying on the outer no-crash harness to detect server crashes.
- `run_smb2_invalid_pipename`: verifies unknown and Unix-separator-containing pipe names return `NT_STATUS_OBJECT_NAME_NOT_FOUND`.

## Control Flow

Most tests follow the same integration-test skeleton: initialize a client connection, negotiate an SMB2 or SMB3 dialect range, authenticate with `torture_creds`, tree-connect to `share` or `IPC$`, perform protocol operations, compare exact `NTSTATUS` values, clean up created remote objects, and return `true` only on all expected outcomes. Error reporting is direct `printf`/`d_printf` with `nt_errstr(status)`.

The session reconnect, multichannel, and reauth tests are the most stateful. They manually drive NTLMSSP/GENSEC token exchange with `smb2cli_session_setup_send/recv`, poll `tevent_req` objects synchronously, then install session or channel keys from `gensec_session_key`. These flows intentionally issue operations in intermediate states to assert expected server rejection, such as `NT_STATUS_USER_SESSION_DELETED`, `NT_STATUS_INVALID_HANDLE`, `NT_STATUS_FILE_CLOSED`, `NT_STATUS_NETWORK_NAME_DELETED`, or `NT_STATUS_ACCESS_DENIED`.

The DFS tests use low-level SMB2 APIs instead of `cli_*` wrappers so they test server pathname behavior rather than client-side path normalization. They first establish whether the server and share advertise DFS, derive a canonical `server\share` root name, query file IDs/inodes using `FSCC_FILE_ALL_INFORMATION`, and compare multiple syntactic paths against the same root inode. Rename and hardlink tests construct raw SMB2 set-info buffers and intentionally distinguish full DFS destination paths from relative names.

Several tests use helper callbacks:

- `list_fn` marks a directory entry as matched when a listed result has `FILE_ATTRIBUTE_DIRECTORY`.
- `check_empty_fn` allows only `.` and `..`, returning `NT_STATUS_DIRECTORY_NOT_EMPTY` for any other entry.
- `check_size` wraps `cli_qfileinfo_basic` and translates size mismatch into `NT_STATUS_END_OF_FILE`.

## State and Persistence Behavior

The tests create remote files/directories such as `smb2-basic.txt`, `session-reconnect.txt`, `multi-channel.txt`, `session-reauth.txt`, `smb2_ftruncate.txt`, `fsync_test_dir`, `smb2_dir_slash`, `smb2_file_slash`, `sacl_test_file`, `stream_acl_test_file`, `ASYNC_DIR`, `DEL_ON_CLOSE_DIR`, `file`, DFS test files, and stream names like `stream_acl_test_file:streamname`. Most are opened with `FILE_DELETE_ON_CLOSE`, explicitly unlinked/rmdir'd, or deleted through `smb2_dfs_delete` at test exit.

Session and tree state is deliberately mutated. Examples include saving and replacing `cli->smb2.tcon` to forge a TID, recreating `cli->smb2.session` with a stale UID, changing `cli_state_client_guid` to enable multichannel setup, and changing `smb2cli_tcon_set_values` capabilities to force or clear `SMB2_SHARE_CAP_DFS`. These mutations are central to the tests and create risk if cleanup paths do not restore handles before subsequent calls.

Memory is managed mostly with Samba's talloc hierarchy (`talloc_tos`, `talloc_asprintf`, `data_blob_talloc`, `TALLOC_FREE`). Handles are closed explicitly. Some early-return paths do not close every successfully opened object, but most tests either use delete-on-close semantics or cleanup labels to remove remote state.

## Dependencies and Integration Points

This file depends on the Samba source3 torture harness and runtime globals declared externally: `host`, `workgroup`, `share`, `password`, `username`, `myname`, and `torture_creds`. It integrates with SMB client libraries from `client.h`, `libsmb/proto.h`, `libsmb/clirap.h`, `libsmb/cli_smb2_fnum.h`, SMBX base transport/session code, GENSEC authentication, credentials, NDR/security descriptor support, and trans2/FSCC constants.

The tests require a live SMB server configured for the relevant scenario. Some entry points need specific share/server properties: SMB2/SMB3 dialect support, DFS-enabled or non-DFS shares, `SeSecurityPrivilege` for SACL testing, alternate data streams and ACL persistence for stream ACL testing, `smbd async dosmode = yes` for async DOS attribute listing, `hide unwritable` and `delete veto files` combinations for delete-on-close tests, and an accessible `IPC$` SAMR named pipe for pipe tests.

Outer Samba test scripts provide additional validation for some cases. For example, `run_smb2_pipe_read_async_disconnect` only confirms the client-side setup/disconnect path; the containing no-crash script checks that the server did not crash.

## Risks and Edge Cases

- The tests encode exact Windows-compatible statuses, but some comments note version differences such as Windows 2008 versus Windows 2022 DFS empty-server behavior and Win8 pre-release SMB2.22 reauth quirks.
- Several tests intentionally tamper with client state (`cli->smb2.tcon`, session IDs, DFS capability bits). Future client library changes that assume these fields are immutable could break the tests or hide server regressions.
- Cleanup is best-effort on many failure paths. Failed runs can leave files or directories on the target share, though most tests pre-clean their known names.
- SACL, DFS, delete-veto, async DOS mode, stream ACL, and named pipe tests are environment-sensitive and can fail because the test server is not configured for the scenario rather than because protocol code regressed.
- The DFS helpers extract inode/file IDs from a fixed offset in `FSCC_FILE_ALL_INFORMATION`; layout changes or server-specific response differences could affect comparisons.
- `run_smb2_multi_channel` temporarily changes the global `cli_state_client_guid`; it restores after three connections are initialized, but early failures before restoration would be risky if future edits move the restore point.

## Test Signals

Strong pass signals include exact `NT_STATUS_OK` for successful creates/reads/writes/flushes/closes, exact negative statuses for invalid handles or invalid paths, byte-for-byte readback of `"Hello, world\n"`, file-size checks after truncation, inode equality for DFS aliases, DACL bit changes on streams, and expected delete-on-close results. The tests print the failing API and observed `NTSTATUS`, making failures actionable in torture logs.

Regression signals are especially tied to historic Samba bugs documented in comments: async DOS attribute listing, delete-on-close race/nonwrite behavior, DFS leading backslash parsing, and async pipe read disconnect no-crash behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_smb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_smbsock_any_connect.c -->
# sources/user-network-fs/samba/source3/torture/test_smbsock_any_connect.c

## Purpose

`test_smbsock_any_connect.c` provides a focused torture entry point for `smbsock_any_connect`, Samba's helper for attempting SMB connections across a list of candidate socket addresses and configured SMB transports. The test is intentionally tolerant: it prints the returned status but always returns `true`, so it acts more like a smoke/coverage probe than a strict connectivity assertion.

## Important APIs, Types, and Functions

- `run_smb_any_connect`: the sole exported torture test function.
- `struct sockaddr_storage addrs[5]`: fixed candidate address list populated with unroutable/test IPv4 addresses `192.168.99.5` through `192.168.99.9`.
- `struct smb_transports`: parsed transport configuration from `lp_client_smb_transports()`.
- `struct loadparm_context`: loadparm context created with `loadparm_init_s3`.
- `struct smbXcli_transport *xtp`: output transport returned by a successful connection.
- `smb_transports_parse`, `interpret_string_addr`, `smbsock_any_connect`, `nt_errstr`, and `TALLOC_FREE` are the key calls.

## Control Flow

The function initializes an s3 loadparm context, converts five string IP addresses into `sockaddr_storage` values, and calls `smbsock_any_connect` with the address array, no explicit names or socket options, the parsed client transport set, zero flags, and output pointers for the chosen transport and chosen address index. It frees the loadparm context immediately after the call, prints the resulting `NTSTATUS`, frees the returned transport only if the status is OK, and returns `true`.

There is only one hard failure path: if `loadparm_init_s3` returns `NULL`, the test returns `false`. Connection failure itself is not considered a failed torture result.

## State and Persistence Behavior

The test has no filesystem persistence. Runtime state is limited to stack-allocated socket addresses, the temporary loadparm context, parsed transport configuration, and a possible talloc-owned `smbXcli_transport`. The selected address index is captured but not inspected.

## Dependencies and Integration Points

The file depends on Samba parameter/loading code (`lib/param/param.h`, `source3/param/loadparm.h`), the socket connection helper (`libsmb/smbsock_connect.h`), and torture registration declarations (`torture/proto.h`). It consumes global Samba client transport configuration via `lp_client_smb_transports`.

Because the addresses are fixed, the observed status depends on the worker host network, routing, firewall behavior, and configured SMB transports. The current implementation is designed not to fail the test suite merely because the addresses are unreachable.

## Risks and Edge Cases

- Since the result is always success after initialization, regressions in failure status selection, timeout behavior, or chosen-index semantics may only be visible in logs.
- If any of the nominally test-only addresses become reachable in a local environment, the test will allocate and then free a live transport, but it still does not verify that the chosen index or transport matches expectations.
- The parsed transport configuration is passed by address from a stack variable; this is fine for the synchronous call but would be unsafe if future connection code retained it beyond the call.

## Test Signals

The primary signal is the printed line `smbsock_any_connect returned <status>`. A strict failure only indicates loadparm initialization failure. Useful manual signals include whether the status is a reasonable connection failure for unreachable addresses and whether a successful connection path frees `xtp` without leaks or crashes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_smbsock_any_connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_tdb_validate.c -->
# sources/user-network-fs/samba/source3/torture/test_tdb_validate.c

## Purpose

`test_tdb_validate.c` is a small negative test for Samba's `tdb_validate` wrapper. It verifies that validation fails when the caller-supplied validation callback rejects a record, and that the failure is propagated to the caller.

## Important APIs, Types, and Functions

- `validate_fn`: callback passed to `tdb_validate`; it receives the TDB context, key, value, and private data, marks `struct tdb_validation_status->success` false, prints a trace line, and returns `-1`.
- `run_tdb_validate`: exported torture entry point that creates a temporary database, stores one record, invokes validation, and expects failure.
- `struct tdb_context`, `TDB_DATA`, `tdb_open`, `tdb_store`, `tdb_validate`, and `tdb_close` are the core TDB APIs.
- `struct tdb_validation_status` comes from `source3/lib/tdb_validate.h` and is used by the validation implementation's private data path.

## Control Flow

`run_tdb_validate` unlinks `tdb_validate.tdb`, creates a new exclusive read/write TDB with mode `0600`, stores a single key/value pair where both key and value are the local `"data"` buffer including its terminating NUL, then calls `tdb_validate(tdb, validate_fn)`. If `tdb_validate` returns `0`, the test reports that validation unexpectedly succeeded and fails. If `tdb_validate` returns nonzero, the function marks the result true, closes the database, unlinks the file, and returns success.

Every setup failure jumps to the shared cleanup block after printing with `perror` or `fprintf`.

## State and Persistence Behavior

The test creates a local temporary file named `tdb_validate.tdb` in the current working directory. It unlinks that file before opening to avoid stale state, and unlinks it again during cleanup. The only record stored is a small stack-buffer-backed `TDB_DATA` value copied into the database by `tdb_store`.

The validation callback mutates only the `tdb_validation_status` object passed by `tdb_validate` as private data. There is no long-lived in-memory state.

## Dependencies and Integration Points

This file integrates with the source3 torture harness through `source3/torture/proto.h`, with the public TDB library through `<tdb.h>`, and with Samba's validation wrapper through `source3/lib/tdb_validate.h`. It is designed to confirm that the wrapper honors callback failure rather than silently accepting corrupt or policy-rejected data.

## Risks and Edge Cases

- `tdb_close(tdb)` is called in the cleanup block even if `tdb_open` failed and `tdb` is `NULL`; this depends on the TDB close API tolerating a null pointer or on the test environment not hitting that path.
- The fixed filename can collide if multiple instances run in the same working directory.
- The callback's assignment to `state->success` assumes `tdb_validate` always passes a valid `struct tdb_validation_status` as private data.
- The test validates failure propagation, not detection of structural database corruption.

## Test Signals

Expected success is a nonzero return from `tdb_validate` after `validate_fn called` is printed. Unexpected signals include inability to create/store in the temporary TDB, `tdb_validate` returning success despite the callback returning `-1`, or cleanup problems caused by the fixed temporary filename.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_tdb_validate.c -->
