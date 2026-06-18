# Research: subset-b-009982

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/setfileinfo.c -->
# sources/user-network-fs/samba/source4/torture/raw/setfileinfo.c

## Purpose
`setfileinfo.c` is the RAW SMB1 set-file-information torture suite. It validates `smb_raw_setfileinfo()` by handle and `smb_raw_setpathinfo()` by path across metadata levels, rename semantics, EOF/allocation changes, disposition/delete-on-close, archive attributes, and known Windows compatibility quirks.

## Important APIs, types, and functions
The suite entry point is `torture_raw_sfileinfo()`. The main tests are `torture_raw_sfileinfo_base()`, `torture_raw_sfileinfo_rename()`, `torture_raw_sfileinfo_bug()`, `torture_raw_sfileinfo_eof()`, `torture_raw_sfileinfo_eof_access()`, and `torture_raw_sfileinfo_archive()`. It uses `union smb_setfileinfo`, `union smb_fileinfo`, `union smb_open`, `RAW_SFILEINFO_*`, `RAW_FILEINFO_*`, `smb_raw_setfileinfo()`, `smb_raw_setpathinfo()`, `smb_raw_fileinfo()`, `smb_raw_pathinfo()`, `smb_raw_open()`, `create_complex_file()`, and `create_directory_handle()`.

## Control flow
The base test creates separate path-based and fnum-based files under `\testsfileinfo`, sets metadata at many information levels, and immediately queries `ALL_INFO` or the corresponding query level to verify the effect. It covers DOS `SETATTR`/`SETATTRE`, standard/basic timestamps, zero-time "do not change" semantics, invalid directory attributes on files, disposition info, allocation size, EOF size, current byte offset, and mode info. The rename test creates file and directory targets, checks collision and overwrite behavior, validates relative names, rejects `root_fid`, tests open-destination conflicts and delete-on-close conflicts, and skips some handle-directory cases under the `samba3` setting. EOF tests use two SMB connections to verify share-mode blocking for path-based EOF changes, the documented and pass-through EOF levels, Windows W2K8/Win7 exceptions, and handle-based EOF changes. EOF access iterates access masks and requires `SEC_FILE_WRITE_DATA` for handle EOF modification. Archive testing verifies default archive behavior for files, directory archive toggling, and `FILE_ATTRIBUTE_NONINDEXED` masking.

## State and persistence behavior
The file mutates only temporary objects in `\testsfileinfo` and removes them with `smbcli_unlink()` or `smbcli_deltree()`. Per-test state is in SMB handles, delete-on-close bits, timestamps, allocation/EOF sizes, and DOS attributes. Some tests intentionally leave name state changed across assertions to confirm handle identity and path lookup behavior after renames. No server configuration is persisted, but dangerous mode can trigger the legacy W2K3 pathinfo bug probe.

## Dependencies and integration points
This file integrates with the raw SMB torture harness and exercises server implementations behind `libcli/raw`. It depends on Samba status helpers, time conversion helpers, test utilities, target feature flags (`TARGET_IS_W2K8`, `TARGET_IS_WIN7`), and torture settings such as `samba3` and `dangerous`. It is directly relevant to PVFS setfileinfo, SMB1 trans2 passthrough levels, and metadata compatibility behavior shared with SMB2 equivalents.

## Risks and edge cases
The assertion macros reuse local variables and jump to shared cleanup, so changes must preserve variable names and handle lifetimes. Several expected statuses encode Windows bugs or Samba3 exceptions rather than ideal protocol behavior. Path rename tests change `path_fname` and `fnum_fname` aliases temporarily, which is easy to break. EOF tests depend on share-mode timing across two connections. The dangerous bug test is intentionally opt-in because it can leave a problematic file on affected servers.

## Test signals
Passing signals include exact NTSTATUS results for each set-info level, unchanged timestamps when zero values are supplied, correct `delete_pending` and `nlink` transitions, path/handle rename name-info agreement, share violations for blocked EOF changes, access-denied without write-data permission, and correct archive-bit state on files and directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/setfileinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/streams.c -->
# sources/user-network-fs/samba/source4/torture/raw/streams.c

## Purpose
`streams.c` is the raw SMB torture suite for Windows alternate data streams. It tests stream creation, I/O, stream enumeration, share modes, delete pending behavior, stream naming rules, stream rename variants, create disposition effects, attribute propagation, summary-information update patterns, and base-file permission enforcement on streams.

## Important APIs, types, and functions
The suite entry point is `torture_raw_streams()`. Helpers include `check_stream()`, `check_stream_list()`, `qsort_string()`, `qsort_stream()`, and `create_file_with_stream()`. Test cases include `test_stream_dir()`, `test_stream_io()`, `test_stream_sharemodes()`, `test_stream_delete()`, `test_stream_names()`, `test_stream_names2()`, `test_stream_rename()`, `test_stream_rename2()`, `test_stream_rename3()`, `test_stream_create_disposition()`, `test_stream_attributes()`, `test_stream_summary_tab()`, and `test_stream_permissions()`. It uses `RAW_OPEN_NTCREATEX`, `RAW_FILEINFO_STREAM_INFO`, `RAW_FILEINFO_ALL_INFO`, `RAW_SFILEINFO_RENAME_INFORMATION`, `RAW_SFILEINFO_EA_SET`, `RAW_SFILEINFO_SEC_DESC`, `RAW_RENAME_NTRENAME`, and `RAW_RENAME_RENAME`.

## Control flow
Each test creates `\teststreams`, performs a focused stream scenario, then deletes the tree. Directory tests reject ADS opens on directories and expect no stream list on the base directory. I/O tests create streams on missing and existing base files, write and modify contents, verify case-insensitive `$DATA` naming, enumerate streams, delete streams by unlink and delete-on-close, and confirm deleting the base removes streams. Share-mode tests show different streams do not conflict while the same stream does. Delete tests verify how stream opens with and without `FILE_SHARE_DELETE` control base-file deletion and `DELETE_PENDING` name-based access. Name tests cover control characters, wildcards, invalid stream type syntax, EA rejection on streams, stream metadata equivalence with the base file, per-stream EOF and write-time mutation, and handle-based stream renames. Additional rename tests compare NT rename and trans2 rename forms using `:<stream>`, `<base>:<stream>`, default stream targets, overwrite behavior, and Samba-specific exceptions. Create-disposition tests verify that overwriting, overwrite-if, and supersede of the base file remove non-default streams, while overwriting the stream itself preserves stream list structure. Permission tests make the base file read-only and add a DACL deny ACE for Everyone to prove stream writes are checked against base-file permissions.

## State and persistence behavior
State is confined to the test directory but exercises persistent server metadata: stream names and contents, stream list records, base-file attributes, EAs, security descriptors, delete-on-close flags, and stream EOF sizes. Stream info is sorted before comparison to avoid depending on server enumeration order. Some tests intentionally leave open handles while performing path operations to observe share-mode and delete-pending state.

## Dependencies and integration points
The file depends on raw SMB create, pathinfo/fileinfo, unlink, rename, setfileinfo, security descriptor helpers, SID constants, talloc, typed sort helpers, and target settings for Samba/Windows differences. It is an integration test for ADS backends such as xattr/EADB implementations and their coupling to open-file/share-mode and security descriptor code.

## Risks and edge cases
ADS semantics are full of compatibility exceptions. The tests encode different expected behavior for Samba3/Samba4 versus Windows in timestamp/name reporting and stream overwrite rename cases. Stream names include nonprintable bytes and wildcard characters, so path normalization changes can alter outcomes. Permission and delete tests depend on exact ordering of open handles and close calls. The disabled large stream-info test indicates a potential buffer-overflow/status path that is not normally exercised.

## Test signals
Strong signals are exact stream lists such as `::$DATA` plus named streams, correct content reads after partial overwrites, correct `OBJECT_NAME_INVALID` versus `OBJECT_NAME_NOT_FOUND` for invalid names, delete-pending behavior after base unlink with an open stream, base overwrite removing ADS entries, stream attribute changes reflecting on the base file, summary stream rename behavior, and access denial when base attributes or DACLs forbid stream writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/streams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/tconrate.c -->
# sources/user-network-fs/samba/source4/torture/raw/tconrate.c

## Purpose
`tconrate.c` is a benchmark-style torture worker that measures the rate at which an SMB server accepts tree connections. It repeatedly creates full SMB client connections to the configured host/share from multiple child processes and prints per-second and total connection rates.

## Important APIs, types, and functions
The exported entry point is `torture_bench_treeconnect()`. Helpers are `map_count_buffer()` for shared counters, `fork_tcon_client()` for child workers, `children_remain()` for nonblocking child reaping, and `rate_convert_secs()` for throughput calculation. It uses `smbcli_full_connection()`, `smbcli_tdis()`, `talloc_free()`, `lpcfg_smbcli_options()`, `lpcfg_smbcli_session_options()`, `samba_cmdline_get_creds()`, and resolve/gensec settings from the torture context.

## Control flow
The benchmark reads `host`, `share`, `timelimit`, and `nprocs` torture settings, maps shared integer counters, forks `nprocs` children, and has each child loop until its end time. Each child opens a full connection, disconnects the tree, frees the client state, increments its shared counter, and repeats. The parent wakes once per second, reaps finished children, computes the delta since the previous sample, prints connections per second, then prints total throughput after all children exit.

## State and persistence behavior
No filesystem data is intentionally created. State is process-local plus an anonymous/shared mmap counter array visible to forked children. Server-side effects are transient session/tree-connect churn, authentication load, and logs. The child exits directly with `exit(0)` after its loop or first connection failure.

## Dependencies and integration points
The file depends on POSIX `fork()`, `waitpid()`, `mmap()`, page-size APIs, Samba command-line credentials, loadparm, resolver context, GENSEC settings, and raw torture registration through `torture/raw/proto.h`. It is a benchmark rather than a pass/fail protocol validator, but it exercises connection setup, authentication, tree connect, and tree disconnect paths.

## Risks and edge cases
`map_count_buffer()` appears to round the buffer size with `(bufsz + pagesz) % pagesz`, which does not round up correctly and can produce a too-small mapping for some sizes. Counter updates are unsynchronized plain integer writes; approximate rates are acceptable, but strict accounting is not guaranteed. Failed child connections print an error and exit without propagating failure to the parent. Start times are intentionally unsynchronized, making runs noisy.

## Test signals
Useful signals are stable per-second output, successful child completion without connection failures, and plausible total connection rate over the configured time limit. Stress runs with larger `nprocs` should reveal authentication bottlenecks, connection leaks, or server-side tree-connect scalability problems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/tconrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/unlink.c -->
# sources/user-network-fs/samba/source4/torture/raw/unlink.c

## Purpose
`unlink.c` is the raw SMB unlink/delete torture suite. It validates plain unlink status codes, hidden-file attribute matching, directory rejection, bad path syntax, delete-on-close behavior for files and directories, non-empty directory semantics, and unlink deferral around oplock breaks.

## Important APIs, types, and functions
The suite entry point is `torture_raw_unlink()`. Test cases are `test_unlink()`, `test_delete_on_close()`, and `test_unlink_defer()`. The oplock callback is `oplock_handler_ack_to_none()`, with `struct unlink_defer_cli_state` carrying context and client state. The file uses `union smb_unlink`, `union smb_open`, `union smb_setfileinfo`, `struct smb_rmdir`, `smb_raw_unlink()`, `smb_raw_rmdir()`, `smb_raw_open()`, `smb_raw_setfileinfo()`, `smb_raw_setfileinfo_send()`, `smbcli_oplock_handler()`, and `smbcli_oplock_ack()`.

## Control flow
The plain unlink test creates `\testunlink`, verifies missing files return `OBJECT_NAME_NOT_FOUND`, deletes a normal file, requires hidden-file attribute matching, rejects directories through unlink even with directory attributes, and checks several `..` path forms for syntax or directory errors. The delete-on-close test sets `RAW_SFILEINFO_DISPOSITION_INFO` on file and directory handles with both false and true values, closes handles, then verifies whether subsequent unlink/rmdir sees the object. It also checks non-empty directory delete-on-close behavior, skipping a known Samba3 deficiency, and exercises delete-on-close create options on directories with child files. The deferred unlink test installs an oplock handler, opens a file with a batch oplock on one client, then unlinks from a second client so the server must break the oplock; the handler marks delete-on-close and acknowledges to none.

## State and persistence behavior
All persistent objects are temporary under `\testunlink`. The tests create files, directories, and inside-directory files, mutate disposition flags, and rely on handle close to commit deletion. The oplock deferral path temporarily stores callback state in `unlink_defer_cli_state` and issues an async setfileinfo request from inside the oplock handler.

## Dependencies and integration points
This file integrates raw unlink/rmdir, raw open, disposition setfileinfo, oplock break dispatch, and SMB session cleanup. It depends on test helpers for complex file creation and directory handles, and uses the `samba3` setting for compatibility skips. It is relevant to share-mode, delete-on-close, open-file database, and oplock break implementations.

## Risks and edge cases
The oplock handler closes the file before acknowledging the break and starts an async setfileinfo without receiving it, so it specifically probes ordering-sensitive server behavior. Some directory delete-on-close cases are expected to keep non-empty directories alive even after close. Path syntax expectations for `..` are protocol compatibility-sensitive. Cleanup uses `smbcli_deltree()`, which must handle partially deleted state.

## Test signals
Expected signals include exact hidden-file and directory NTSTATUS values, delete-on-close removing files/directories only when allowed, `DIRECTORY_NOT_EMPTY` for non-empty directory disposition attempts, and successful handling of an unlink that is deferred by an oplock break and races with delete-on-close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/write.c -->
# sources/user-network-fs/samba/source4/torture/raw/write.c

## Purpose
`write.c` is the raw SMB1 write torture suite. It verifies legacy write variants (`SMBwrite`, `SMBwriteX`, write-unlock, write-close), data integrity, bad handles, locked regions, sparse/large-file offsets, and one deliberately malformed SMB write request.

## Important APIs, types, and functions
The suite entry point is `torture_raw_write()`. Test cases are `test_write()`, `test_writex()`, `test_writeunlock()`, `test_writeclose()`, and `test_bad_write()`. Helpers are `setup_buffer()` and `check_buffer()`, which produce deterministic pseudo-random data from a seed. It uses `union smb_write`, `union smb_fileinfo`, `smb_raw_write()`, `smbcli_read()`, `smbcli_lock()`, `torture_set_sparse()`, `smbcli_request_setup()`, `smbcli_request_send()`, `smbcli_request_receive()`, and raw packet field writers.

## Control flow
Each write-variant test creates `\testwrite\test.txt`, allocates a 90 KB buffer, performs a zero-length write, writes small and large buffers, reads data back, and compares deterministic content. `test_write()` covers basic `RAW_WRITE_WRITE` and a near-4 GB offset when `CAP_LARGE_FILES` is set. `test_writex()` additionally verifies write mode values, lock conflict behavior by manipulating the session PID around a write lock, and optionally probes offsets from `2^33` up to `2^63` when dangerous mode is enabled. `test_writeunlock()` verifies that write-unlock writes data but requires a matching lock to return success, returning `RANGE_NOT_LOCKED` otherwise. `test_writeclose()` confirms the write closes the handle, so repeated use returns `INVALID_HANDLE`, then reopens to verify contents and large offsets. `test_bad_write()` manually constructs an `SMBwrite` with an impossible length and accepts `INVALID_PARAMETER` or `UNSUCCESSFUL`.

## State and persistence behavior
State is temporary file content, file size, sparse-file state, byte-range locks, and handle validity under `\testwrite`. The deterministic random buffer avoids storing fixtures. Large-offset tests can create sparse logical sizes far beyond the physical write size. Each test removes the directory and exits the raw session during cleanup.

## Dependencies and integration points
The file depends on negotiated server capabilities (`CAP_LARGE_FILES`, `lockread_supported`), torture settings (`dangerous`, `writeclose_support`), raw write marshalling, lock handling, sparse-file setup, and pathinfo `ALL_INFO` size queries. It exercises both high-level raw APIs and low-level SMB request construction.

## Risks and edge cases
Dangerous writex can probe extremely large offsets and should remain opt-in. `srandom()`/`random()` global state makes helper output deterministic but process-global. Large sparse writes depend on filesystem/server support and can be skipped. Some tests call `torture_skip()` after resources have been opened, relying on harness behavior. The malformed write test validates error tolerance but can expose disconnect behavior on strict servers.

## Test signals
Passing signals are exact byte counts, byte-for-byte readback of pseudo-random data, zero-filled gaps before offset writes, `INVALID_HANDLE` on bad or closed handles, `FILE_LOCK_CONFLICT` on locked writex regions, `RANGE_NOT_LOCKED` for write-unlock without locks, correct `ALL_INFO.size` after large writes, and accepted error codes for malformed write length.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/alter_context.c -->
# sources/user-network-fs/samba/source4/torture/rpc/alter_context.c

## Purpose
`alter_context.c` tests DCE/RPC alter-context behavior. It checks that a pipe can alter its existing presentation context, create a secondary context for another interface, reject an unsupported interface version, and preserve or fault operations according to the active abstract syntax.

## Important APIs, types, and functions
The exported test is `torture_rpc_alter_context()`. It uses `dcerpc_alter_context()`, `dcerpc_secondary_context()`, `dcerpc_binding_handle_get_binding()`, `dcerpc_binding_get_abstract_syntax()`, `dcerpc_binding_get_flags()`, `test_lsa_OpenPolicy2()`, `test_lsa_OpenPolicy2_ex()`, `test_lsa_Close()`, `test_DsRoleGetPrimaryDomainInformation()`, and `test_DsRoleGetPrimaryDomainInformation_ext()`. Interfaces involved are `ndr_table_lsarpc` and `ndr_table_dssetup`.

## Control flow
The test opens an LSARPC connection, extracts its abstract syntax and transfer syntax (`NDR` or `NDR64`), and alters the primary context back to that syntax. It verifies LSA open/close still works, opens a DSSETUP secondary context, alters that context, then attempts a bad secondary context with a deliberately invalid DSSETUP version and expects `RPC_UNSUPPORTED_NAME_SYNTAX`. It then alternates LSA and DSSETUP calls through the primary and secondary pipes. Finally it attempts to alter the primary LSA pipe to DSSETUP syntax; some servers disconnect with protocol error, while others accept the context but DSSETUP calls on the original binding should fault with bad stub data before LSA is verified again.

## State and persistence behavior
The state is DCE/RPC connection state: presentation contexts, association state, binding handles, and policy handles opened and closed during the test. It persists no server data. A protocol-error path may intentionally disconnect the binding handle and ends the test early after checking disconnected state.

## Dependencies and integration points
The file depends on generated NDR tables for LSA and DSSETUP, generic RPC torture helpers, DCE/RPC binding syntax metadata, and transport support for alter-context PDUs. It integrates with LSA and DSSETUP test helper functions from the broader torture RPC suite.

## Risks and edge cases
Expected behavior differs by server when an existing context is altered to a different abstract syntax. The test must preserve transfer syntax choice when NDR64 is negotiated. Policy handles must be closed only when opened. The bad-version test depends on the NDR table copy being modified without corrupting the original global table.

## Test signals
Signals include successful repeated alter-context calls on valid syntax, successful LSA operations after altering, successful DSSETUP operations through a secondary context, `RPC_UNSUPPORTED_NAME_SYNTAX` for a bad secondary version, and either clean protocol disconnect or `RPC_BAD_STUB_DATA` for intentionally mismatched primary-context calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/alter_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/async_bind.c -->
# sources/user-network-fs/samba/source4/torture/rpc/async_bind.c

## Purpose
`async_bind.c` tests concurrent asynchronous DCE/RPC bind setup. It sends multiple LSARPC pipe connect requests before receiving any of them, then verifies that each bind completes successfully.

## Important APIs, types, and functions
The exported function is `torture_async_bind()`. It uses `dcerpc_pipe_connect_send()`, `dcerpc_pipe_connect_recv()`, `samba_cmdline_get_creds()`, generated `ndr_table_lsarpc`, the torture `binding` setting, and external `torture_numasync` for request count. Request state is stored in arrays of `struct composite_context *`, `struct dcerpc_pipe *`, and `const struct ndr_interface_table *`.

## Control flow
The test is disabled unless the `async` torture setting is true. When enabled, it reads the binding string, creates a temporary talloc context, allocates arrays sized by `torture_numasync`, obtains command-line credentials, and loops once to send every LSARPC async connect. A second loop receives each connection result and fails immediately if any status is not OK. On success it frees the temporary context and returns true.

## State and persistence behavior
State is client-side only: outstanding composite contexts and connected pipe objects owned by the temporary talloc context. No remote objects are created beyond transient RPC associations and binds. The test intentionally overlaps bind operations on the same event context.

## Dependencies and integration points
It depends on the composite async RPC API, event loop in the torture context, command-line credentials, and generated LSARPC NDR metadata. It is an integration test for transport connection setup, bind sequencing, and event-driven completion.

## Risks and edge cases
Allocation failures return false without freeing earlier allocations. The test assumes the same binding string is valid for all concurrent binds and does not throttle request count. Disabled-by-default behavior means it gives no coverage unless explicitly configured. If one receive fails, already connected pipes are left to context cleanup.

## Test signals
The primary signal is all `torture_numasync` `dcerpc_pipe_connect_recv()` calls returning OK. Failures indicate async transport, event-loop, server bind fanout, or authentication scalability problems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/async_bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/atsvc.c -->
# sources/user-network-fs/samba/source4/torture/rpc/atsvc.c

## Purpose
`atsvc.c` is the RPC torture suite for the ATSVC scheduled-job interface. It enumerates jobs, fetches job information, adds a sample scheduled command, verifies it can be queried, and deletes it.

## Important APIs, types, and functions
The suite entry point is `torture_rpc_atsvc()`. Test helpers are `test_JobEnum()`, `test_JobAdd()`, `test_JobGetInfo()`, and `test_JobDel()`. It uses generated calls `dcerpc_atsvc_JobEnum_r()`, `dcerpc_atsvc_JobAdd_r()`, `dcerpc_atsvc_JobGetInfo_r()`, and `dcerpc_atsvc_JobDel_r()`, plus `struct atsvc_JobInfo`, `struct atsvc_enum_ctr`, and `ndr_table_atsvc`.

## Control flow
`test_JobEnum()` calls `JobEnum` with max buffer `0xffffffff`, resume handle zero, and an empty enum container, then iterates returned entries and calls `JobGetInfo` on each job ID. `test_JobAdd()` builds a periodic non-interactive Tuesday job for `foo.exe` at a fixed `job_time`, submits it with `JobAdd`, runs enumeration again, queries the returned job ID, and deletes exactly that ID with `JobDel`. The suite registers both `JobEnum` and `JobAdd` under an ATSVC RPC interface test case.

## State and persistence behavior
Enumeration is read-only, but `JobAdd` creates a scheduled job on the remote server and `JobDel` removes it. The persistent mutation is intended to be short-lived. If the test aborts between add and delete, a `foo.exe` job may remain on the target scheduler.

## Dependencies and integration points
The file depends on the generated ATSVC client stubs, DCE/RPC binding from the torture harness, server name resolution via `dcerpc_server_name()`, and scheduler service support on the target. It tests both transport-level NTSTATUS and ATSVC result status.

## Risks and edge cases
Adding scheduled jobs may require privileges and may be disabled or unsupported on modern targets. The hard-coded command and time are not intended to execute but still create real scheduler state. Cleanup is not protected by a `finally` style block if an assertion aborts after successful `JobAdd`. Existing jobs are queried during enum, so permission or corrupted job records can fail the read-only test.

## Test signals
Signals are successful ATSVC bind, OK transport and operation statuses for enum/add/get/delete, returned job IDs that can be queried, and no residual test job after deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/atsvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/backupkey.c -->
# sources/user-network-fs/samba/source4/torture/rpc/backupkey.c

## Purpose
`backupkey.c` is the comprehensive RPC torture suite for the Microsoft BackupKey Remote Protocol (BKRP). It validates client-side wrapped secret restore for v2 and v3, server-side wrapped backup/restore, domain controller backup-key certificate properties, required privacy authentication, access-check SID/hash behavior, and a large set of malformed request/error-code cases.

## Important APIs, types, and functions
The suite entry point is `torture_rpc_backupkey()`. Core builders are `get_user_sid()`, `create_unencryptedsecret()`, `create_access_check()`, `encrypt_blob()`, `get_cert_guid()`, `encrypt_blob_pk()`, `createRetrieveBackupKeyGUIDStruct()`, and `createRestoreGUIDStruct()`. Client-side tests include `test_RetrieveBackupKeyGUID()`, `test_RetrieveBackupKeyGUID_validate()`, `test_RestoreGUID()`, `test_RestoreGUID_v3()`, and wrong-input variants for non-reversed secret, wrong user, wrong version, bad secret magic, bad access-check magic/hash, bad cert GUID, and empty requests. Server-wrap tests include `test_ServerWrap_encrypt_decrypt()`, `test_ServerWrap_decrypt_wrong_keyGUID()`, empty/short request tests, `test_ServerWrap_encrypt_decrypt_manual()`, and wrappers around `test_ServerWrap_decrypt_wrong_stuff()`. It uses generated BKRP, LSA, and security NDR types, `dcerpc_bkrp_BackupKey_r()`, LSA secret APIs, GnuTLS X.509/public-key/cipher/HMAC/hash APIs, `sess_decrypt_blob()`, GUID helpers, and SID helpers.

## Control flow
Client-side retrieve builds a `BACKUPKEY_RETRIEVE_BACKUP_KEY_GUID` request and expects the DC certificate only when the RPC auth level is privacy. Restore first retrieves that certificate, creates an unencrypted secret structure for v2 or v3, creates an access-check structure for the caller SID with SHA-1 or SHA-512 depending on version, encrypts the secret using the certificate public key, reverses the RSA ciphertext as BKRP expects, derives a symmetric key and IV from the secret tail, encrypts the access-check blob with 3DES-CBC or AES-256-CBC, and submits `BACKUPKEY_RESTORE_GUID`. Successful responses are unmarshalled as `bkrp_client_side_unwrapped` and compared with the static secret. Malformed variants perturb version, user SID, magic fields, hash bytes, certificate GUID bytes, or request length and assert precise WERROR/NTSTATUS behavior.

Server-side tests call `BACKUPKEY_BACKUP_GUID` to wrap the static secret, then restore with both normal and Win2K restore GUIDs. Wrong-key-GUID and length/magic mutations pull the returned `bkrp_server_side_wrapped` blob, modify fields, repush when possible, and verify failure codes. The manual test opens LSA secrets `G$BCKUPKEY_P` and `G$BCKUPKEY_<guid>`, decrypts them with the transport session key, derives HMAC-SHA1 RC4 keys from the server key and BKRP nonces, decrypts the wrapped payload, validates MAC/SID/plaintext, then re-encrypts with the right key, wrong key, or wrong SID for restore tests.

## State and persistence behavior
Most state is temporary request/response blobs allocated under the torture context. The test reads persistent domain LSA secrets for backup keys but does not intentionally modify them. It sends real backup/restore RPCs and validates remote certificate material. It obtains the caller SID through an LSARPC lookup. Sensitive data includes the static test secret, backup key material read from LSA, session keys, symmetric keys, HMAC keys, and decrypted payloads in process memory.

## Dependencies and integration points
The file depends on BKRP, LSARPC, generated NDR marshalling, command-line credentials, GnuTLS algorithms (RSA, 3DES-CBC, AES-256-CBC, ARCFOUR-128, SHA-1, SHA-512, HMAC-SHA1), Samba auth/session-key helpers, security descriptors/SIDs, and DCE/RPC privacy sealing. It integrates with domain controller secret storage and certificate generation for backup keys, so it is an end-to-end interoperability test rather than a pure unit test.

## Risks and edge cases
The suite encodes protocol quirks, including reversed RSA ciphertext, certificate GUID placement in unique IDs and serial numbers, exact 2048-bit RSA expectations, and Windows-specific error-code anomalies. Tests require privacy auth; without it many calls expect disconnect/access-denied behavior. Manual LSA secret reads require privileges and named-pipe LSARPC. Crypto buffer lengths and NDR blob mutation offsets are brittle. The static secret and decrypted backup keys are not scrubbed. A few diagnostic dumps can print key material under debug helpers.

## Test signals
Signals include successful certificate retrieval under privacy, certificate v3/RSA-2048/GUID consistency, v2 and v3 client-side restore returning the original secret, expected invalid-parameter/access/data errors for malformed client wraps, successful server-side backup and restore through both restore GUIDs, invalid-data for wrong key GUID, invalid-parameter for empty/short requests, and correct behavior when server-side wrapped payloads are altered by magic, nonce, lengths, key, or SID.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/backupkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/bench.c -->
# sources/user-network-fs/samba/source4/torture/rpc/bench.c

## Purpose
`bench.c` is a simple RPC benchmark for SRVSVC share enumeration. It repeatedly calls `NetShareEnumAll` at several information levels for a configured time and reports queries per second.

## Important APIs, types, and functions
The exported entry point is `torture_bench_rpc()`. Helpers are `test_NetShareEnumAll()` and `bench_NetShareEnumAll()`. It uses `dcerpc_srvsvc_NetShareEnumAll_r()`, `struct srvsvc_NetShareEnumAll`, `struct srvsvc_NetShareInfoCtr`, share container types for levels 0, 1, 2, 501, and 502, `ndr_table_srvsvc`, and `timeval_elapsed()`.

## Control flow
`torture_bench_rpc()` opens a SRVSVC RPC pipe and calls the benchmark helper. The benchmark reads the `timelimit` setting, then loops until elapsed time exceeds that limit. Each iteration creates a temporary talloc context, calls `test_NetShareEnumAll()`, frees the context, increments a count, and optionally prints progress every 50 iterations. `test_NetShareEnumAll()` builds a server UNC from the RPC server name and calls `NetShareEnumAll` for levels 0, 1, 2, 501, and 502, resetting the resume handle and union arm for each level.

## State and persistence behavior
No server data is changed. Client state is the open SRVSVC pipe, per-iteration temporary allocations, resume handle values, and benchmark counters. Server state observed is the share list.

## Dependencies and integration points
The benchmark depends on SRVSVC generated stubs, DCE/RPC connection setup, talloc, and torture settings `timelimit` and `progress`. It exercises share-enumeration marshalling, server share database access, and RPC throughput.

## Risks and edge cases
The helper sets `ret = false` only for transport failures; WERROR failures print and continue without changing `ret`, so benchmark success can mask per-level operation failures. Share level 502 may require privileges or return access errors on some servers. The denominator uses elapsed wall time and can be noisy for very short timelimits.

## Test signals
Useful signals are successful SRVSVC bind, no transport failures for all tested levels, stable progress output, and final queries-per-second numbers. For correctness, logs should be checked for per-level WERROR failures even if the benchmark returns true.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/bind.c -->
# sources/user-network-fs/samba/source4/torture/rpc/bind.c

## Purpose
`bind.c` is the DCE/RPC bind torture suite. It verifies authenticated LSARPC binds with NTLM/SPNEGO, signing, sealing, optional big-endian NDR, and endpoint mapper association-group handle sharing across TCP connections.

## Important APIs, types, and functions
The suite entry point is `torture_rpc_bind()`. Helpers are `test_openpolicy()`, `test_bind()`, `test_assoc_group_handles_external()`, and `test_bind_op()`. It uses `dcerpc_binding_set_flags()`, `dcerpc_pipe_connect_b()`, `dcerpc_binding_set_transport()`, `dcerpc_binding_set_string_option()`, `dcerpc_binding_get_assoc_group_id()`, `dcerpc_binding_set_assoc_group_id()`, LSARPC policy helpers, and EPM calls `dcerpc_epm_Lookup_r()` and `dcerpc_epm_LookupHandleFree_r()`.

## Control flow
For each authentication flag combination, `test_bind()` parses the configured binding, applies auth/sign/seal flags, connects to LSARPC with command-line credentials, opens and closes an LSA policy handle, then frees the pipe. The suite registers NTLM sign, NTLM sign/seal, SPNEGO sign, SPNEGO sign/seal, and big-endian variants of each. The association-group test opens an endpoint mapper TCP pipe on port 135, starts an EPM lookup to obtain a context handle, opens a second pipe in a different association group and expects `RPC_SS_CONTEXT_MISMATCH` when using that handle, then reconnects the second pipe with the first pipe's association group ID and expects the handle to work. It finally frees the EPM lookup handle.

## State and persistence behavior
State is RPC association/binding state and transient LSA/EPM context handles. No server data is persisted. The association-group test deliberately carries an EPM context handle across connections only when the same association group is requested.

## Dependencies and integration points
The file depends on generated LSARPC and EPMAPPER stubs, command-line credentials, DCE/RPC binding parsing, TCP endpoint 135, auth option flags, and torture helper policy functions. It validates client and server support for authentication flavors, sealing, byte order, and association group semantics.

## Risks and edge cases
Big-endian push support can expose NDR marshalling assumptions. Association group behavior is interface/process dependent; the comment avoids LSARPC for handle sharing because preforked selftests can put interfaces in different processes. The cleanup assertion after `LookupHandleFree` checks `r.out.result` instead of `f.out.result`, which may miss a cleanup failure. Port 135 may be unavailable for non-TCP bindings or restricted environments.

## Test signals
Signals are successful bind and LSA open/close for every auth/sign/seal/endian combination, context mismatch for a handle used in a different association group, success after reusing the original association group ID, and successful EPM handle cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/browser.c -->
# sources/user-network-fs/samba/source4/torture/rpc/browser.c

## Purpose
`browser.c` tests the Browser RPC interface, specifically `BrowserrQueryOtherDomains`. It validates accepted level 100 calls and error handling for missing containers and unsupported levels.

## Important APIs, types, and functions
The suite entry point is `torture_rpc_browser()`, and the test function is `test_BrowserrQueryOtherDomains()`. It uses generated `dcerpc_BrowserrQueryOtherDomains_r()`, `struct BrowserrQueryOtherDomains`, `struct BrowserrSrvInfo`, `BrowserrSrvInfo100Ctr`, `BrowserrSrvInfo101Ctr`, `srvsvc_NetSrvInfo100`, `srvsvc_NetSrvInfo101`, and `ndr_table_browser`.

## Control flow
The test builds `\\server` from the RPC pipe server name, initializes a `BrowserrSrvInfo` union, and calls level 100 first with an empty container and then with a preallocated one-entry container. Both should succeed and report zero total entries. It then sets the level 100 pointer to NULL and expects `WERR_INVALID_PARAMETER`. For level 101 with and without a container, and levels 102 and 0, it expects successful RPC transport but `WERR_INVALID_LEVEL`.

## State and persistence behavior
The test is read-only. It only allocates request/response containers and observes the browser service response. No browser database or domain state is changed.

## Dependencies and integration points
The file depends on generated Browser and SRVSVC-related NDR types, DCE/RPC torture interface registration, and browser service behavior on the target. It validates both NDR union arm handling and server-side level validation.

## Risks and edge cases
The test assumes no "other domains" are returned and asserts total entries zero. That is suitable for Samba's expected behavior but may be environment-sensitive if a server exposes browser domain entries. It also assumes invalid levels are reported as WERRORs with OK transport status.

## Test signals
Passing signals are OK transport for every call, WERR_OK and zero entries for valid level 100 calls, `WERR_INVALID_PARAMETER` for a NULL level 100 container, and `WERR_INVALID_LEVEL` for levels 101, 102, and 0.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/browser.c -->
