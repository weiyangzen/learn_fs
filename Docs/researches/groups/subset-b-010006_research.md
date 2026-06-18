# subset-b-010006 Research

Grouped research report for Samba SMB2 torture sources. Each file section is bounded for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/session.c -->
# sources/user-network-fs/samba/source4/torture/smb2/session.c

## Purpose

`session.c` is the SMB2 torture suite for session setup, reauthentication, Kerberos ticket expiry, multichannel session binding, signing/encryption negotiation, anonymous session edge cases, and targeted session regressions. It is client-side test code: it opens SMB2 trees, mutates client/session state, sends SMB2 requests, and asserts server status codes and connection state. Its exported integration points are `torture_smb2_session_init()` and `torture_smb2_session_req_sign_init()`, which register many named tests into the `smb2.session` and `smb2.session-require-signing` suites.

## Important APIs, Types, and Functions

The file is built around Samba torture and SMB2 client APIs: `struct torture_context`, `struct smb2_tree`, `struct smb2_session`, `struct smb2_transport`, `struct smbcli_options`, `struct cli_credentials`, `struct smb2_create`, `union smb_fileinfo`, and `union smb_setfileinfo`. It uses `smb2_connect()`, `torture_smb2_connection_ext()`, `torture_smb2_session_setup()`, `smb2_session_setup_spnego()`, `smb2_session_channel()`, `smb2_session_init()`, `smb2_tree_init()`, `smb2cli_tcon_send()/recv()`, `smb2cli_session_current_id()`, `smb2cli_session_set_id_and_flags()`, `smb2cli_session_encryption_on()`, `smb2cli_tcon_is_encryption_on()`, `smb2cli_conn_server_capabilities()`, `smb2cli_conn_server_signing_algo()`, `smbXcli_conn_disconnect()`, and `smbXcli_conn_is_connected()`.

`CHECK_CREATED` validates create responses and `WAIT_FOR_ASYNC_RESPONSE` drives tevent until an async request is cancellable or no longer receiving. `sleep_remaining()` sleeps until a calculated Kerberos-expiry time. The constants `KRB5_TICKET_LIFETIME`, `KRB5_CLOCKSKEW`, and `GENSEC_GSSAPI_REQUESTED_LIFETIME()` force short-lived GSSAPI credentials for expiry tests.

Core test families:

- `test_session_reconnect1/2()` validate reconnect behavior with previous session ids and old-handle invalidation.
- `test_session_reauth1` through `test_session_reauth6()` validate same-session reauth, anonymous reauth, security descriptor access, rename authorization after reauth, and failed reauth session teardown.
- `test_session_expire1i()`, `test_session_expire2i()`, and wrappers exercise Kerberos expiry under normal, signed, and encrypted operation.
- `test_session_bind1()`, `test_session_bind2()`, `test_session_bind_auth_mismatch()`, and the many `test_session_bind_negative_*()` functions cover multichannel binding and dialect/signing/encryption capability mismatches.
- `test_session_sign_enc()` plus signing/encryption wrappers validates negotiated algorithms against normal IO and async notify cancellation.
- Anonymous tests manipulate `anonymous_session_key`, forced session keys, encryption/signing torture knobs, and IPC tree connect behavior.
- `test_session_ntlmssp_bug14932()` and `test_session_require_sign_bug15397()` cover specific regressions.

## Control Flow

Most tests follow the same pattern: build a random file name, clean it with `smb2_util_unlink()`, create it through `smb2_create()`, assert the create action/oplock/attributes, perform a session operation, then verify follow-up SMB2 calls return exactly the expected `NTSTATUS`. Cleanup closes handles, deletes created files or trees, frees talloc parents, and restores altered config such as the requested GSSAPI lifetime.

Reconnect tests capture the current session id and reconnect with that id. They then verify old handles on the old session return `NT_STATUS_USER_SESSION_DELETED`, while new or rebound sessions can reopen or clean up state. Reauth tests call `smb2_session_setup_spnego()` on an existing session with original, anonymous, or deliberately corrupted credentials, then test whether file handles and security descriptors still behave as expected.

Expiry tests require `--use-kerberos=required`. They invalidate the credential cache, request a five-second ticket lifetime, sleep past the expiry window, then assert that most session-bound operations fail with `NT_STATUS_NETWORK_SESSION_EXPIRED`. `test_session_expire2i()` is a broad matrix over getinfo, setinfo, flush, read, write, ioctl, oplock/lease ack, directory find, compound create/find/close, notify cancellation, tree connect, root handle create, tree disconnect, unlock, close, echo, and logoff. Its important distinction is that unlock, close, echo, and logoff are still allowed after expiry, while normal file and tree operations are not.

Multichannel tests first check `SMB2_CAP_MULTI_CHANNEL` and then build multiple transports with controlled `client_guid`, protocol range, signing, encryption, and `only_negprot` settings. Positive bind tests verify one session can be used over another transport. Negative bind tests call the shared `test_session_bind_negative_smbXtoX()` helper to attempt invalid binds, check exact rejection status, check behavior when the bind flag or session keys are missing, and ensure the original session remains usable. The large matrix intentionally varies SMB 2.02, SMB 2.10, SMB 3.x, SMB 3.1.1 signing algorithms, encryption algorithms, same/different client GUIDs, and required encryption state.

Signing/encryption algorithm tests use a helper that connects with a narrow algorithm list, creates a file, issues a pending notify, cancels it, and verifies the session still works. Anonymous security tests force anonymous session-key behavior and verify whether encrypted or signed IPC tree connects are accepted, reset, or access-denied depending on the key and signing setup.

## State and Persistence Behavior

This file creates temporary files and sometimes directories on the SMB share, almost always with random suffixes and often `DELETE_ON_CLOSE`. It also mutates client-side session state directly: `tree->session` is swapped among channel sessions, options structures are copied and modified, credentials are shallow-copied and altered, session ids/flags are injected, and connections are deliberately disconnected. Kerberos tests mutate global loadparm state by setting `gensec_gssapi:requested_life_time` and then reset it to `0` in cleanup. Credential caches are invalidated before and after expiry tests.

Server-visible persistent state should be limited to transient files, share handles, locks, and security descriptor changes during test execution. Cleanup paths unlink files, close handles, delete trees, and free talloc contexts. Risks remain where assertion jumps skip some disconnect cleanup or where helper tests free the incoming `tree0`/`tree1`, which is expected by the wrapper but important for callers.

## Dependencies and Integration Points

The file depends on Samba SMB2 client calls (`libcli/smb2`), low-level `smbXcli` session/transport primitives, torture assertions, credentials and Kerberos support, security descriptor manipulation, tevent async handling, resolver/loadparm config, and NT status helpers. It integrates with `smb2.c` through `torture_smb2_session_init()` and `torture_smb2_session_req_sign_init()`. Tests require a configured host/share, valid credentials, sometimes `user2` credentials, Kerberos infrastructure, SMB3/multichannel support, SMB 3.1.1 algorithm negotiation support, and server capabilities such as leasing or encryption depending on the case.

## Risks

The main risk is brittleness from timing and environment: the Kerberos expiry tests rely on a five-second ticket lifetime plus skew and can fail on slow systems, clock skew, KDC behavior, or credential-cache quirks. The multichannel and algorithm tests are capability-sensitive and intentionally skip when the negotiated protocol or server feature set is insufficient. The code also reaches into session internals (`needs_bind`, forced session keys, session ids, anonymous flags), so changes to client internals can affect tests even if wire behavior is unchanged.

Because tests swap `tree->session`, deliberately disconnect transports, and free trees passed by wrappers, cleanup correctness is essential. A missed restore can make later cleanup use the wrong session or transport. Negative status expectations are protocol-contract assertions; server changes that return different but plausible errors will surface as regressions and should be checked against MS-SMB2 expectations and Samba bug references before updating tests.

## Test Signals

Strong signals are exact `NTSTATUS` assertions, connection-state checks, authenticated/anonymous state checks, create action and oplock assertions, successful post-error reuse of original sessions, and skip messages tied to missing capabilities. The suite names registered at the end map directly to runnable torture tests such as `smb2.session.reauth6`, `smb2.session.expire2e`, `smb2.session.bind_negative_smb3signGtoH2Xd`, and `smb2.session-require-signing.bug15397`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/setinfo.c -->
# sources/user-network-fs/samba/source4/torture/smb2/setinfo.c

## Purpose

`setinfo.c` is a focused SMB2 torture test for individual `SETINFO` file information classes. It verifies that Samba/SMB2 servers accept, reject, and persist file metadata changes according to protocol expectations by setting values with `smb2_setinfo_file()` and reading them back with `smb2_getinfo_file()` or security/EA helpers. The exported test entry point is `torture_smb2_setinfo()`, registered by the top-level SMB2 suite as the simple test `smb2.setinfo`.

## Important APIs, Types, and Functions

The file uses `struct smb2_tree`, `struct smb2_handle`, `union smb_fileinfo`, `union smb_setfileinfo`, `struct security_descriptor`, `struct security_ace`, `struct dom_sid`, and `struct ea_struct`. SMB2 helper APIs include `torture_smb2_connection()`, `smb2_create_complex_file()`, `smb2_setinfo_file()`, `smb2_getinfo_file()`, `torture_smb2_all_info()`, `smb2_util_verify_sd()`, `smb2_util_close()`, and `smb2_util_unlink()`.

`find_returned_ea()` scans `SMB2_ALL_EAS` results, comparing EA names case-insensitively because Windows capitalizes returned EA names. Local assertion macros drive the test: `RECREATE_FILE` opens a fresh file handle, `CHECK_CALL` sets `RAW_SFILEINFO_*` and checks the expected status, `CHECK1` reads a matching `RAW_FILEINFO_*` level, `CHECK_VALUE` and `CHECK_TIME` compare returned fields, and `CHECK_STATUS` validates security descriptor mutation helpers.

## Control Flow

The test creates a temporary file name from the current time and opens it once through `RECREATE_BOTH`. It first dumps all info for diagnostics, then walks through set-info classes:

- `BASIC_INFORMATION` sets create/access/write/change times and attributes, verifies them via `SMB2_ALL_INFORMATION`, confirms zero times mean "do not change", confirms zero attributes mean "do not change", rejects changing a file into a directory, and restores normal attributes.
- `DISPOSITION_INFORMATION` toggles `delete_on_close` and verifies `delete_pending` and link count changes.
- `ALLOCATION_INFORMATION` and `END_OF_FILE_INFORMATION` set allocation and EOF sizes and verify returned all-info size fields.
- `POSITION_INFORMATION` sets the file pointer and checks both direct position info and all-info position.
- `MODE_INFORMATION` accepts valid modes, rejects an invalid mode value, and verifies returned mode.
- `SEC_DESC` reads owner/group/DACL, adds an `Authenticated Users` ACE, writes the descriptor, verifies it, then removes the ACE and verifies again.
- `FULL_EA_INFORMATION` sets, deletes, and attempts a zero-length EA while validating returned EAs.

All failures report the location and either jump to `done` or mark `ret = false`. Cleanup closes the handle and unlinks the file.

## State and Persistence Behavior

This test deliberately mutates on-disk file metadata: timestamps, DOS attributes, delete disposition, allocation size, EOF, current position, mode flags, DACL contents, and extended attributes. It expects changes to be immediately visible through subsequent `GETINFO` calls on the same handle. The security descriptor changes are restored by deleting the added ACE before cleanup. The EA section verifies SMB2-specific behavior: setting a non-empty EA creates it, setting the same EA with a null blob deletes it, and creating a zero-length EA should not leave a visible `ZeroEA` entry while pre-existing EAs such as `EAONE` and `SECONDEA` remain visible.

## Dependencies and Integration Points

The test depends on SMB2 get/set-info marshalling, security descriptor NDR types, Samba SID helpers, DACL mutation helpers, EA data blob handling, NT time conversions, and torture reporting. It is invoked from `torture_smb2_init()` in `smb2.c`. It assumes the target share supports setting file metadata, security descriptors, and EAs; filesystems or VFS modules without EA/security-descriptor support may produce meaningful failures or need environment-specific skips elsewhere.

## Risks

The test is sensitive to filesystem timestamp precision and semantics, though the base time is even-aligned to reduce rounding issues. Security descriptor verification can vary with share ACL configuration, filesystem ACL backends, inherited ACE behavior, or privilege restrictions. EA expectations are protocol-specific and include Windows name capitalization behavior; backend EA normalization or missing EA support can create false failures. The time-derived file name is less collision-resistant than the random names used elsewhere, but the collision window is small and cleanup unlinks the file.

## Test Signals

Useful signals are exact success/failure statuses per `RAW_SFILEINFO_*` level, read-after-write comparisons through `SMB2_ALL_INFORMATION`, security descriptor round-trip verification, and the positive/negative EA presence checks. Diagnostic calls to `torture_smb2_all_info()` and location-aware failure messages make regressions easier to isolate.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/setinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/sharemode.c -->
# sources/user-network-fs/samba/source4/torture/smb2/sharemode.c

## Purpose

`sharemode.c` implements SMB2 torture tests for share-mode conflict behavior and includes two manual harnesses for cross-filesystem or external-access experiments. Automated tests verify that the interaction between a first open's share access and a second open's desired access matches SMB semantics, and vice versa. The file exports `torture_smb2_sharemode_init()` for the `smb2.sharemode` suite plus simple manual tests `torture_smb2_hold_sharemode()` and `torture_smb2_check_sharemode()` that are registered by the top-level suite.

## Important APIs, Types, and Functions

Important types are `struct hold_sharemode_info`, `struct sharemode_info`, `struct smb2_tree`, `struct smb2_create`, `struct smb2_handle`, `union smb_setfileinfo`, and tevent signal types. The file relies on `torture_smb2_connection()`, `torture_smb2_testdir()`, `smb2_create()`, `smb2_read()`, `smb2_util_write()`, `smb2_setinfo_file()`, `smb2_util_close()`, `smb2_util_unlink()`, `smb2_deltree()`, `smb2_util_share_access()`, `torture_setting_string()`, and `smb_strtoul()`.

`hold_sharemode_table` lists all share-mode combinations for files held open in `sharemode_hold_test`: none, R, W, D, RW, RD, WD, and RWD. `sharemode_table` is a large expected-result matrix mapping share-mode strings to desired access masks and whether a second create should succeed.

## Control Flow

`torture_smb2_hold_sharemode()` is a manual test. It connects, registers a SIGINT handler, creates a directory, opens one file for each share mode with `SEC_RIGHTS_FILE_ALL`, then waits in `tevent_loop_wait()` until interrupted. On exit it marks each file `delete_on_close`, closes handles, tolerates `NT_STATUS_OBJECT_NAME_NOT_FOUND` when an external client deleted a file, and deletes the directory tree.

`torture_smb2_check_sharemode()` is also manual/config-driven. It reads torture settings `sharemode`, `access`, `filename`, and `operation`, opens a file with the requested share/access values, then optionally performs read, write, and delete operations based on operation letters R/W/D. It is useful when another process has already opened the file outside Samba.

`test_smb2_sharemode_access()` is automated. For each `sharemode_table` entry, it first opens `test_sharemode` with full access and the entry's share mode, then attempts a second open from another SMB2 tree with the entry's desired access and full sharing. It expects `NT_STATUS_OK` when `expect_ok` is true and `NT_STATUS_SHARING_VIOLATION` otherwise. It closes the first handle every iteration and closes the second only when the second open succeeded.

`test_smb2_access_sharemode()` reverses the matrix. The first open uses the entry's desired access and full sharing; the second open requests full access with the entry's share mode. It expects the same OK/sharing-violation result, exercising both directions of Samba share-mode compatibility checks.

`test_smb2_bug14375()` covers a regression where an initial stat-like open with `SEC_FILE_READ_ATTRIBUTE` and share-none must not poison later opens. It checks both orders: stat/share-none first followed by data opens, then data open first followed by stat/share-none and another data open.

## State and Persistence Behavior

Automated tests create and unlink a single `test_sharemode` file repeatedly. Manual hold mode creates a persistent directory and keeps handles open until SIGINT so external clients can probe behavior; cleanup attempts to delete all files and the directory. `check-sharemode` can intentionally delete the configured file when operation includes D. No repository state is changed; all persistence is on the target SMB share.

## Dependencies and Integration Points

The automated suite integrates through `torture_smb2_sharemode_init()` and uses `torture_suite_add_2smb2_test()` for two-tree conflict tests and `torture_suite_add_1smb2_test()` for the regression. The manual functions are registered in `smb2.c` as top-level simple SMB2 tests. The file depends on tevent for SIGINT handling and on Samba security access-mask constants to express desired access. It assumes the server and backend enforce share-mode semantics consistently across separate SMB2 tree connections.

## Risks

The matrix encodes subtle protocol policy: some metadata-oriented rights such as EA, attributes, read-control, write-DAC, write-owner, and synchronize are expected to pass despite R/W/D sharing restrictions, while data read/write/delete bits are expected to conflict based on the share flags. Regressions can be caused by server share-mode logic, VFS/open-file-description behavior, or backend filesystems that enforce or bypass share modes differently. Manual tests intentionally block until interrupted, so they are unsuitable for unattended runs unless explicitly selected.

## Test Signals

The strongest signals are exact `NT_STATUS_OK` versus `NT_STATUS_SHARING_VIOLATION` on the second create for every matrix entry, successful cleanup closes, and bug14375's absence of unexpected sharing violations. Manual tests signal through successful open/read/write/delete operations and comments printed while waiting or cleaning up.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/sharemode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/smb2.c -->
# sources/user-network-fs/samba/source4/torture/smb2/smb2.c

## Purpose

`smb2.c` is the registration and wrapper module for Samba's SMB2 torture tests. It provides helper functions for adding tests that need one or two SMB2 tree connections, and `torture_smb2_init()` builds the top-level `smb2` suite by adding simple tests and child suites from many SMB2 torture modules. It does not implement protocol behavior itself; it is the integration point that makes the individual SMB2 test files runnable through the torture framework.

## Important APIs, Types, and Functions

The key local helpers are `wrap_simple_1smb2_test()`, `torture_suite_add_1smb2_test()`, `wrap_simple_2smb2_test()`, and `torture_suite_add_2smb2_test()`. They use `struct torture_context`, `struct torture_suite`, `struct torture_tcase`, `struct torture_test`, and `struct smb2_tree`. They allocate `struct torture_test` records, set `test->run` to a wrapper, store the real function pointer in `test->fn`, and append the test with `DLIST_ADD_END()`.

The central exported function is `NTSTATUS torture_smb2_init(TALLOC_CTX *ctx)`. It creates the `smb2` suite, calls many `torture_smb2_*_init()` child-suite factories, adds simple tests such as `connect`, `setinfo`, `dosmode`, `hold-sharemode`, and `check-sharemode`, sets the suite description, and calls `torture_register_suite()`.

## Control Flow

The one-tree wrapper opens an SMB2 connection with `torture_smb2_connection()`, steals the returned `tree1` under a local `mem_ctx`, invokes the stored test function, and frees `mem_ctx`. The comment explains the ownership trick: some tests close or free their connection, so stealing the tree and freeing the parent avoids double-free patterns. The two-tree wrapper repeats the same setup for `tree1` and `tree2`, handles connection failures with `torture_fail()`, invokes a two-tree function pointer, and frees the shared context on exit.

`torture_suite_add_1smb2_test()` and `torture_suite_add_2smb2_test()` both create a testcase named after the test, allocate and initialize a `struct torture_test`, set `dangerous = false`, and attach it to the testcase list. `torture_smb2_init()` is then a long declarative registration sequence. Registration order matters for how tests appear and run in the torture suite but does not create runtime coupling between child suites beyond shared command-line settings and target connection configuration.

## State and Persistence Behavior

This file maintains no durable application state. It allocates suite/test metadata under the provided talloc context and temporary connection wrappers under per-test memory contexts. Runtime state consists of SMB2 connections created for wrapper tests; freeing the wrapper memory context is expected to release any still-owned connections. The wrappers deliberately tolerate tests that consume or free their own tree connections.

## Dependencies and Integration Points

This is a central integration file. It depends on the torture framework (`torture/smbtorture.h`), SMB2 connection helpers from `torture/smb2/proto.h`, the SMB2 client type definitions, and Samba's linked-list helper. It references a broad set of test factories and test functions implemented in sibling SMB2 torture files, including session, sharemode, setinfo, getinfo, lock, read, create, notify, durable opens, leases, compound operations, oplocks, IOCTLs, rename, crediting, multichannel, timestamps, ACLs, EAs, and more.

## Risks

The wrappers depend on `test->fn` holding function pointers with signatures that match the wrapper selected by registration. A test registered with the wrong helper would compile via the generic storage but fail at runtime due to an invalid call signature. Ownership is also subtle: because individual tests may free connections, changing the talloc-steal/free pattern can reintroduce leaks or double frees. Adding new suites here without including the right prototype can create build failures; adding long-running or manual tests as normal automated tests can affect CI behavior.

## Test Signals

The main signals are structural: the SMB2 suite should register successfully with `NT_STATUS_OK`, one-tree and two-tree tests should establish their required connections before calling test logic, and failures should be reported as torture failures when connection setup fails. Downstream test results come from the registered modules; this file's own correctness is visible when named SMB2 tests appear in the suite and receive the expected number of SMB2 tree connections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/smb2.c -->
