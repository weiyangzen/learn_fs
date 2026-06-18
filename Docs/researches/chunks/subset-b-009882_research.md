# sources/user-network-fs/samba/source3/torture/torture.c lines 1-10421

## Scope

This chunk covers the first 10,421 lines of Samba's `source3/torture/torture.c`. It starts with global torture harness setup and SMB1 client connection helpers, then covers a large collection of SMB1 behavioral tests: read/write stress, NetBench replay, tree connect/session/fid isolation, byte-range locking, oplock break/cancel paths, delete-on-close and stream delete semantics, rename/share-mode behavior, security descriptor checks, POSIX CIFS extension behavior, open attribute matrices, directory listing, IOCTL probing, chkpath, and extended attributes. The assigned range ends in the middle of `run_dirtest1()`, after the old directory listing count check and before the rest of that function's filtering validation.

## Purpose

The visible code is a standalone SMB torture test driver for exercising server behavior through Samba's SMB client APIs. Most functions are `run_*` test bodies that open one or more SMB connections, create controlled files/directories on the target share, issue protocol operations, validate NT/DOS status codes or state changes, and clean up artifacts before returning a boolean result.

The chunk focuses heavily on edge cases where an SMB server can diverge from Windows behavior:

- connection negotiation flags, signing, encryption, SPNEGO, Kerberos, SMB1 forcing, and multishare UNC selection;
- read/write integrity under repeated operations and concurrent clients;
- tree ID, user ID, process ID, and file ID isolation;
- byte-range lock stacking, timeouts, cancellation, strict lock enforcement, and POSIX/OFD lock interaction;
- oplock breaks across ordinary opens, hardlinks, ACL access, and Linux kernel leases;
- delete-on-close, stream delete, hardlink delete, print-share delete, unlink while open, and rename with/without `FILE_SHARE_DELETE`;
- DOS/NT attributes, timestamps, trans2 file info levels, `open` disposition attribute results, EAs, security descriptors, owner-rights ACEs, and SMB1 `SEC_FLAG_SYSTEM_SECURITY`;
- UNIX extension operations such as POSIX open/mkdir/unlink/hardlink/symlink/readlink/stat/chmod/getacl/setacl and case-sensitive mkdir behavior.

## Important APIs, Types, And Functions

Connection and harness helpers:

- Global configuration includes `host`, `workgroup`, `share`, `password`, `username`, `myname`, `torture_creds`, `sockops`, `torture_nprocs`, `torture_numops`, `torture_blocksize`, `use_oplocks`, `use_level_II_oplocks`, `disable_spnego`, `use_kerberos`, `force_dos_errors`, `use_multishare_conn`, `do_encrypt`, `local_path`, and `signing_state`.
- `force_cli_encryption()` verifies UNIX CIFS encryption capability and calls `cli_smb1_setup_encryption()`.
- `open_nbt_connection()` creates a NetBIOS SMB transport using `cli_connect_nb()`, applying SPNEGO/oplock/DOS-error flags.
- `smbcli_parse_unc()`, `terminate_path_at_separator()`, `torture_open_connection_share()`, `torture_open_connection_flags()`, and `torture_open_connection()` parse share names and create authenticated SMB1 share connections via `cli_full_connection_creds()`.
- `torture_init_connection()`, `torture_cli_session_setup2()`, `torture_close_connection()`, and `torture_conn_set_sockopt()` centralize session setup, secondary session creation, tree disconnect/shutdown, and socket option application.

Protocol utility wrappers:

- `cli_smbwrite()` sends legacy `SMBwrite` requests in chunks and preserves zero-byte write behavior.
- `cli_smb()` synchronously sends a raw SMB request with `cli_smb_send()`/`cli_smb_recv()` and rejects use while async calls are pending.
- `cli_bad_session_request()` writes a deliberately malformed RFC1002 session request and expects a NetBIOS negative session response with error `0x82`.
- `torture_deltree()` and `torture_delete_fn()` recursively delete a subtree through `cli_list()`, `cli_unlink()`, and `cli_rmdir()`.
- `check_error()` and `check_both_error()` validate either DOS-class/coded errors or NTSTATUS values.
- `cli_qpathinfo1()` reads `SMB_INFO_STANDARD` via `cli_qpathinfo()` and decodes DOS dates and file size/attributes.
- `cli_raw_ioctl()` sends raw `SMBioctl` requests and returns an empty `DATA_BLOB` on success.

Major test bodies visible in this chunk include `run_torture()`, `run_readwritetest()`, `run_readwritemulti()`, `run_readwritelarge()`, `run_readwritelarge_signtest()`, `run_nbench()`, `run_locktest1()` through `run_locktest13()`, `run_fdpasstest()`, `run_fdsesstest()`, `run_unlinktest()`, `run_maxfidtest()`, `run_negprot_nowait()`, `run_bad_nbt_session()`, `run_randomipc()`, `run_browsetest()`, `run_attrtest()`, `run_trans2test()`, `run_w2ktest()`, `run_oplock1()`, `run_oplock2()`, `run_oplock4()`, optional Linux `run_oplock5()`, `run_deletetest()`, `run_delete_stream()`, `run_delete_print_test()`, `run_deletetest_ln()`, `run_properties()`, `run_xcopy()`, `run_rename()`, `run_rename_access()`, `run_owner_rights()`, `run_smb1_system_security()`, `run_pipe_number()`, `run_opentest()`, `torture_setup_unix_extensions()`, `run_simple_posix_open_test()`, `run_acl_symlink_test()`, `run_posix_stream_delete()`, `run_ea_symlink_test()`, `run_posix_ofd_lock_test()`, `run_posix_blocking_lock()`, `run_posix_mkdir_test()`, `run_posix_acl_oplock_test()`, `run_posix_acl_shareroot_test()`, `run_openattrtest()`, `run_dirtest()`, `torture_ioctl_test()`, `torture_chkpath_test()`, `run_eatest()`, and the opening of `run_dirtest1()`.

Important local async state types:

- `locktest10_state`, `deferred_close_state`, `lockread_state`, `lock12_state`, and `lock_ntcancel_state` coordinate tevent-driven lock/read/close/cancel tests.
- `oplock4_state`, optional `oplock5_state`, and `posix_acl_oplock_state` coordinate oplock break waiters with competing opens or POSIX ACL fetches.
- `delete_stream_state` ensures an async base-file unlink sees `NT_STATUS_SHARING_VIOLATION` after a stream close reply ordering condition.
- `posix_blocking_state` chains POSIX lock acquisition, a blocking second lock, an echo ordering barrier, and unlock.
- `trunc_open_results` plus `open_attrs_table` and `attr_results` define expected file attribute results for truncate/open disposition combinations.

## Control Flow

Most tests follow a common control pattern:

1. Open one or more SMB connections with `torture_open_connection()`, usually forcing SMB1 and applying `sockops`.
2. Reset test files/directories with `cli_unlink()`, `cli_rmdir()`, `torture_deltree()`, `cli_setatr()`, or POSIX unlink/rmdir helpers.
3. Issue SMB operations for the scenario under test.
4. Compare status codes with explicit expected NTSTATUS/DOS errors, or compare resulting data, attributes, timestamps, sizes, ACLs, EA lists, oplock break flags, and directory counts.
5. Close fids, remove artifacts, disconnect tree/session state, and return `true` only if all checks passed.

Read/write tests use repeated deterministic or random data flows. `rw_torture()` serializes random file operations through a lock file. `rw_torture2()` writes from one connection and reads through another. `rw_torture3()` uses `procnum` to split writer/reader behavior when run under the process fan-out harness. The large-write test compares file sizes after both normal `cli_writeall()` and legacy `cli_smbwrite()`, with a variant requiring SMB signing.

Lock tests are the densest control-flow area. `run_locktest1()` checks retained locks over close and lock timeout behavior. `run_locktest2()` changes SMB PID values to verify separate lock contexts and failed unlocks from the wrong PID. `run_locktest3()` scans the 32-bit offset range. `run_locktest4()` and `run_locktest5()` test overlapping locks, recursive read locks, lock overlays, strict read/write lock enforcement, lock stack ordering, and the "NT byte range lock bug". `run_locktest6()` probes unusual `LOCKING_ANDX_CHANGE_LOCKTYPE` and `LOCKING_ANDX_CANCEL_LOCK` bits. `run_locktest7()` verifies read/write access under read and write locks from different PIDs. `run_locktest8()` reproduces a GPFS share-mode/pending-close case. `run_locktest9a()` and `run_locktest9b()` fork a local process to take a filesystem `fcntl()` lock under `local_path`, then verify the SMB lock blocks until release. `run_locktest10()` chains a short-timeout lockingX request with a read and expects the lock to conflict and the chained read to abort. `run_locktest11()` verifies lock cancel without active locks succeeds. `run_locktest12()` defers close while a chained lock/read waits on the same connection. `run_locktest13()` schedules an async blocking lock then cancels it through `tevent_req_cancel()`, requiring a quick `NT_STATUS_FILE_LOCK_CONFLICT`.

Oplock tests combine asynchronous waiters with competing operations. `run_oplock4()` first proves hardlink paths share deny-mode state, then opens one path with an oplock and asynchronously opens the hardlink path, expecting an oplock break and successful open after `cli_oplock_ack_send()`. Optional Linux `run_oplock5()` forks a child that takes a kernel lease with `F_SETLEASE`; the parent uses an SMB async open plus `cli_echo_send()` to prove the server is blocked by the kernel oplock before closing a pipe to let the child drop it. `run_posix_acl_oplock_test()` uses a Windows open with oplock and a POSIX `getacl` on a second connection to require a break.

Delete/rename/open-share tests exercise Windows-compatible lifecycle semantics. `run_deletetest()` has twelve subtests covering initial `FILE_DELETE_ON_CLOSE`, setting/unsetting delete-on-close, delete access requirements, share-delete compatibility, multiple handles and connections, read-only files, and initial delete-on-close persistence. `run_delete_stream()` intentionally races unlink of a base file against closing an alternate data stream handle and requires a sharing violation. `run_posix_stream_delete()` performs a similar stream-handle sharing check through POSIX unlink. `run_deletetest_ln()` verifies deleting one hardlink path does not remove the remaining link. `run_rename()` tests rename with different share modes and checks the renamed file gets the archive bit. `run_rename_access()` creates a destination directory with a deny ACE and confirms file and directory renames into it fail even after POSIX `chmod 0777`.

POSIX extension tests first call `torture_setup_unix_extensions()`, which verifies UNIX CIFS support and sets negotiated capabilities back on the session. `run_simple_posix_open_test()` then covers POSIX mkdir, open modes, ftruncate, stat mode/size, unlink while open, directory open errors, hardlink/symlink/readlink, POSIX lock/unlock, and interaction with a Windows-open file. `run_acl_symlink_test()` and `run_ea_symlink_test()` verify ACL and EA operations are rejected or empty on symlinks. `run_posix_ofd_lock_test()` checks POSIX locks are file-description scoped. `run_posix_blocking_lock()` uses async POSIX lock calls plus an echo barrier to show a blocking lock really waits until the original lock is released. `run_posix_mkdir_test()` checks POSIX mkdir is case-sensitive and returns `NT_STATUS_OBJECT_PATH_NOT_FOUND` for missing parent components.

The chunk ends in `run_dirtest1()`. The visible part creates `\\LISTDIR`, populates 1000 files and 1000 directories, uses `cli_list_old()` with `FILE_ATTRIBUTE_DIRECTORY`, and expects 2002 entries including `.` and `..`. The rest of the filtering and cleanup logic is in the next chunk.

## State And Persistence Behavior

The tests persist temporary server-side state on the target SMB share: files such as `\\torture.*`, lock files, `\\large.dat`, `\\delete.file`, streams like `:Zone.Identifier:$DATA`, POSIX test names, EA-bearing files, `\\LISTDIR`, and temporary names returned from `cli_ctemp()`. Most functions clean up with `cli_unlink()`, `cli_rmdir()`, `cli_posix_unlink()`, `cli_posix_rmdir()`, or `torture_deltree()` on success and failure paths, but some early returns can leave files, handles, directories, attributes, or POSIX locks behind if an intermediate operation fails.

Client-side state is mostly global or process-local:

- `current_cli`, `procnum`, `randomfname`, and `torture_nprocs` tie several tests to the external process fan-out harness.
- `use_oplocks`, `use_level_II_oplocks`, `signing_state`, `force_dos_errors`, and `do_encrypt` mutate connection behavior globally; tests that modify them usually restore saved values, but early returns can be risky.
- `local_path` is required for tests that coordinate SMB operations with local filesystem locks or kernel leases.
- `line_count` and `nbio_id` track NetBench replay progress.
- Several async tests store request completion flags in stack variables referenced by tevent callbacks, making lifetime tied to the event loop completing before function exit.
- `anonymous_shared_allocate()` in `run_oplock2()` stores child result state across `fork()`.

The code also deliberately manipulates SMB protocol identity state: `cli_state_set_uid()`, `cli_state_set_tid()`, and `cli_setpid()` are used to prove session/tree/PID isolation. Mis-restoring these fields can poison later operations on the same `cli_state`.

## Dependencies And Integration Points

This chunk depends on Samba's source3 SMB client stack and utility layers:

- SMB connection and session APIs: `cli_connect_nb()`, `cli_full_connection_creds()`, `cli_session_setup_creds()`, `cli_tree_connect_creds()`, `cli_tdis()`, `cli_shutdown()`, `smbXcli_conn_*`, and transport parsing from `lp_client_smb_transports()`.
- File protocol APIs: `cli_openx()`, `cli_ntcreate()`, `cli_close()`, `cli_writeall()`, `cli_read()`, `cli_lock32()`, `cli_locktype()`, `cli_lockingx_*`, `cli_unlink()`, `cli_rename()`, `cli_hardlink()`, `cli_getatr()`, `cli_setatr()`, `cli_qpathinfo*()`, `cli_qfileinfo*()`, `cli_list()`, `cli_list_old()`, `cli_chkpath()`, `cli_trans()`, and raw `cli_smb()`.
- POSIX/UNIX extension APIs: `SERVER_HAS_UNIX_CIFS()`, `cli_unix_extensions_version()`, `cli_set_unix_extensions_capabilities()`, `cli_posix_open()`, `cli_posix_mkdir()`, `cli_posix_stat()`, `cli_posix_unlink()`, `cli_posix_lock()`, `cli_posix_getacl()`, `cli_posix_setacl()`, `cli_chmod()`, `cli_readlink()`, and related helpers.
- Async/event APIs: `tevent_context`, `tevent_req`, `tevent_wakeup_send()`, `tevent_req_poll_ntstatus()`, `tevent_loop_once()`, async SMB create/read/close/unlink/echo/oplock helpers, and chained SMB1 request submission.
- Security APIs: `security_descriptor_dacl_create()`, `security_acl_concatenate()`, `cli_query_secdesc()`, `cli_set_secdesc()`, well-known SIDs such as `SID_WORLD`, `SID_OWNER_RIGHTS`, and `SID_NT_AUTHENTICATED_USERS`.
- Local OS integration: `fork()`, `pipe()`, `fcntl()` byte-range locks, optional Linux `F_SETLEASE`, signals, `alarm()`, `open()`, `unlink()`, and local path construction with `local_path`.
- NetBench integration: `client_oplocks.txt` and `nb_*` helpers simulate a dbench/netbench workload.
- Browser/IPC integration: `cli_NetServerEnum()` and random `\\PIPE\\LANMAN` transactions probe legacy RAP/IPC behavior.

## Risks And Maintenance Notes

- This file is a broad legacy SMB1 torture harness with many global flags. Adding tests that mutate globals must restore them on all exits or subsequent tests can run with wrong signing/oplock/SPNEGO/encryption behavior.
- Many cleanup paths use best-effort deletes and some early error returns skip cleanup or connection shutdown. Failed runs can leave share state that changes later test results.
- `run_deletetest()` contains an explicit FIXME about potential crashes if failure occurs before `cli2` initialization; its cleanup assumes partially initialized state.
- Async tests rely on strict event ordering and stack-backed callback state. If an async helper changes completion ordering or cancellation status, these tests may report failures that are timing-sensitive.
- Several tests depend on precise Windows-compatible error mapping, including distinction between DOS `ERRbadshare`/`ERRnoaccess`/`ERRbadpath` and NT status values. Protocol changes that alter status mapping can break compatibility even if the local filesystem operation succeeded.
- Tests using `local_path`, local `fcntl()` locks, or Linux kernel leases are environment-sensitive and require the SMB share to map to the supplied local path. They are not portable to all test deployments.
- Oplock and locking tests use sleeps, alarms, process forking, and timeouts. Slow or heavily loaded systems can create flaky timing signals, especially around lock timeout validation, pending close behavior, and oplock break delivery.
- Tests that open thousands of fids, pipes, files, or directories can stress server resource limits and may be unsuitable for small CI environments without isolation.
- POSIX extension tests are gated only by server capability checks; running against SMB2-only servers or SMB1 disabled environments will skip/fail these paths.
- The chunk boundary splits `run_dirtest1()`, so final per-file synthesis must merge this report with the next chunk before treating directory-list filtering behavior as fully researched.

## Test Signals

Strong signals from this chunk are explicit pass/fail returns plus printed diagnostics naming the failed operation and status. Useful regression coverage includes:

- connection helpers successfully opening encrypted, signed, SMB1-forced, oplock-capable, and multishare sessions where configured;
- read/write tests preserving data integrity across single-connection, dual-connection, multi-process, legacy `SMBwrite`, and signed large-write paths;
- lock tests returning the expected `NT_STATUS_LOCK_NOT_GRANTED`, `NT_STATUS_FILE_LOCK_CONFLICT`, `NT_STATUS_RANGE_NOT_LOCKED`, `NT_STATUS_REQUEST_ABORTED`, or timeout/cancel behavior for each scenario;
- tree/session/fid tests proving wrong TID/VUID/PID/fnum use fails rather than leaking access across contexts;
- delete and rename tests matching Windows share-delete and delete-on-close rules, including streams and hardlinks;
- POSIX extension tests validating mode/size/stat/readlink/ACL/EA/lock semantics and expected symlink denials;
- security descriptor tests enforcing deny ACEs and owner-rights ACE ordering;
- attribute/trans2/open tests returning expected timestamps, inode behavior, file attributes, open disposition outcomes, and EA counts;
- directory tests producing expected listing counts and cleanup behavior for generated trees;
- IOCTL, bad NBT session, random IPC, browser enumeration, pipe count, and maxfid tests completing without crashes or unexpected successful access.

Because this is only chunk 1 of a two-chunk oversized file, the merge lane should treat unresolved cross-chunk references as expected for `run_dirtest1()` continuation and for the final test registry/main harness that appears later in the file.
