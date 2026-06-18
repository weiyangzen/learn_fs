# Research: subset-b-009997

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/create.c -->
# sources/user-network-fs/samba/source4/torture/smb2/create.c

## Purpose

`create.c` is a large SMB2 torture-suite source file that validates SMB2 CREATE/open semantics, create-context blobs, security descriptor handling, directory creation races, time-warp snapshot behavior, file-id stability, quota fake file metadata, path length limits, and no-stream behavior. It registers four suites: `create`, `twrp`, `fileid`, and `create_no_streams`.

## Important APIs, Types, and Functions

- Core SMB2 calls: `smb2_create`, `smb2_create_send`, `smb2_create_recv`, `smb2_getinfo_file`, `smb2_setinfo_file`, `smb2_read`, `smb2_find_level`, `smb2_lock`, `smb2_util_write`, `smb2_util_close`, `smb2_util_unlink`, `smb2_deltree`, `smb2_util_mkdir`, and `smb2_util_rmdir`.
- Low-level async client calls: `smb2cli_create_send`, `smb2cli_create_recv`, `tevent_req_set_callback`, `tevent_req_poll`, and `tevent_loop_once`.
- Security APIs: `security_descriptor_dacl_create`, `security_descriptor_dacl_add`, `security_descriptor_copy`, `security_ace_create`, `security_descriptor_dacl_insert`, `dom_sid_parse_talloc`, and `dom_sid_string`.
- Test assertion and reporting helpers: `torture_assert_*`, `torture_fail_goto`, `torture_result`, `torture_comment`, and local macros such as `CHECK_STATUS`, `CHECK_EQUAL`, `CHECK_NTTIME`, `CHECK_ALL_INFO`, `SET_ATTRIB`, and `CHECK_ACCESS_FLAGS`.
- Important state structs include `struct smb2_create`, `union smb_open`, `union smb_fileinfo`, `union smb_setfileinfo`, `struct smb2_handle`, and the async directory-visibility structs `test_mkdir_visible_state` and `test_mkdir_visible_open`.

## Control Flow

The file is organized as independent static test functions that each construct SMB2 request structs, perform operations against a test share, verify returned status and metadata, then clean up paths and handles. `torture_smb2_create_init()` registers the main create tests, `torture_smb2_twrp_init()` registers snapshot/time-warp tests, `torture_smb2_fileid_init()` registers file-id tests, and `torture_smb2_create_no_streams_init()` registers invalid stream-name tests for shares without streams support.

The create tests begin with protocol edge cases in `test_create_gentest()` and `test_create_blob()`: invalid create options, invalid attributes, desired-access bit masks, stream creates, maximal-access output, allocation size, durable open, timewarp context, query-on-disk-id context, and create-blob tag length handling. `test_smb2_open()` then walks create disposition behavior, validates create response timestamps/sizes/attributes against getinfo, and repeats the checks for directories.

Concurrency and race coverage is implemented with multi-connection tests. `test_smb2_open_multi()` fires concurrent create requests for the same filename and expects exactly one success plus name collisions. `test_mkdir_dup()` performs the same style of race for directory `OPEN_IF`, expecting one `CREATED` and one `EXISTED`. `test_mkdir_visible()` uses 50 async low-level create loops that repeatedly try to create files inside a directory before the directory create completes; after the directory appears with inherited deny ACEs, each loop must resolve to `NT_STATUS_ACCESS_DENIED` rather than a stale path-not-found or unauthorized success.

The TWRP suite parses `twrp_snapshot` in `@GMT-YYYY.MM.DD-HH.MM.SS` form, converts it to an NT time, and sends SMB2 create requests with `io.in.timewarp`. It verifies read-only snapshot behavior: opens of existing objects succeed, attempts to write, delete, truncate, rename, hardlink, change ACLs, or create new files/directories fail with write-protection or cross-device status. It also validates stream reads, root opens, and directory-listing file IDs under a snapshot.

The file-id suite uses `query_on_disk_id` and `RAW_FILEINFO_SMB2_ALL_INFORMATION` to ensure file IDs are stable across create/open/overwrite, base file writes, stream creates/opens/overwrites, metadata setinfo operations, directory stream operations, and directory listings. `test_fileid_unique_object()` creates 100 files or directories and checks all returned IDs are unique with a brute-force pairwise comparison.

## State and Persistence Behavior

Tests persist only temporary share objects such as `test_create.dat`, `smb2_open`, `mkdir_dup`, `mkdir_visible`, and file-id test trees. The normal pattern is cleanup before and after each test with `smb2_deltree`, `smb2_util_unlink`, or `smb2_util_rmdir`. Handles are closed explicitly, often guarded with `smb2_util_handle_empty`.

Security descriptor tests persist ACL changes long enough to verify inheritance and access behavior. `test_create_acl_ext()` creates files and directories with initial DACLs and attributes, then verifies them with helper APIs. `test_create_null_dacl()` deliberately mutates a file between inherited DACL, NULL DACL, zero-ACE DACL, and empty descriptor states, validating the resulting access rules before cleanup and disconnect/logoff. `test_mkdir_visible()` persists a deny ACE on a base directory to exercise visibility and inherited denial under concurrent requests.

TWRP tests are stateful against pre-existing snapshot fixtures supplied through torture settings (`twrp_file`, `twrp_stream`, `twrp_snapshot`, `twrp_stream_size`). They do not create the snapshot data; they verify server behavior when historical views are opened with the timewarp create context.

## Dependencies and Integration Points

The source depends on Samba's SMB2 client library, torture harness, tevent event loop, security descriptor/NDR types, command-line credentials, and filesystem/system helpers. It integrates into the SMB2 torture test registry through exported suite initializers, which are discovered by the wider torture framework. Several tests depend on runtime settings: `samba4`, `hide_on_access_denied`, `interactive`, `twrp_*`, and the target platform checks such as `TARGET_IS_WIN7`.

The tests assert Windows-compatible semantics in many places. The expected masks in `test_create_gentest()`, the stream/base-file file-id expectations, the snapshot write-protection statuses, and the quota fake-file timestamps/attributes are all integration signals for server compatibility and regressions in create processing, VFS allocation reporting, stream support, ACL mapping, durable/timewarp create contexts, and file-id derivation.

## Risks and Edge Cases

- Several expected masks and status codes are exact and platform-sensitive; server behavior changes may require conditional expectations rather than blanket updates.
- Async race tests depend on event-loop progress and timing; failures can indicate real races but may also expose transport timeouts or overloaded test hosts.
- Cleanup is broad (`smb2_deltree`) and uses fixed names, so parallel execution against the same share namespace can interfere.
- `test_path_length_test()` is interactive-only because it probes path limits destructively and can leave deep directory trees if interrupted.
- TWRP tests depend on correctly provisioned snapshot fixtures and GMT parsing; missing settings intentionally skip or fail.
- Security descriptor tests rely on the server accepting owner/DACL updates and on share configuration such as `hide_on_access_denied`.

## Test Signals

Strong pass signals include exact NT status matches for create dispositions and invalid inputs, response metadata matching `RAW_FILEINFO_*` queries, successful ACL/attribute verification, correct race outcome counts, expected snapshot write-protection failures, stable file IDs across streams and metadata changes, unique IDs for 100 created objects, quota fake-file zero timestamps and hidden/system/directory/archive attributes, and `NT_STATUS_OBJECT_NAME_INVALID` on stream names when streams are disabled.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/credits.c -->
# sources/user-network-fs/samba/source4/torture/smb2/credits.c

## Purpose

`credits.c` implements the SMB2 crediting torture suite. It validates credit grants during session setup and ordinary requests, MID-window recovery after a skipped message ID, and the server's max-async-credit enforcement for IPC named-pipe reads and change-notify requests across one connection, two connections, and SMB3 multichannel.

## Important APIs, Types, and Functions

- Credit and transport APIs: `smb2cli_conn_get_cur_credits`, `smb2cli_conn_set_max_credits`, `smb2cli_conn_get_mid`, `smb2cli_conn_set_mid`, `smb2_transport_credits_ask_num`, and `smbXcli_conn_disconnect`.
- Connection/session APIs: `torture_smb2_connection_ext`, `smb2_connect`, `smb2_session_channel`, `smb2_session_setup_spnego`, `smb2_tree_channel`, `smb2_logoff`, and `torture_smb2_tree_connect` patterns through the torture harness.
- Async request APIs: `smb2cli_read_send`, `smb2cli_read_recv`, `smb2cli_read_set_notify_async`, `smb2cli_notify_send`, `smb2cli_notify_recv`, `smb2cli_notify_set_notify_async`, `tevent_create_immediate`, `tevent_schedule_immediate`, `tevent_wakeup_send`, `tevent_req_cancel`, and `tevent_req_poll`.
- IPC setup calls: low-level `smb2cli_create` for `NDR_LSARPC_NAME`, `smb2cli_ioctl` with `FSCTL_NAMED_PIPE_READ_WRITE`, and a static DCERPC LSA bind byte sequence.
- Main state carriers are `test_ipc_async_credits_state`, `test_ipc_async_credits_loop`, `test_notify_async_credit_state`, and `test_notify_async_credit_loop`.

## Control Flow

The suite begins with direct credit grant tests. `test_session_setup_credits_granted()` logs off the initial session, reconnects with `options.max_credits = 65535`, and requires at least 8192 granted credits. `test_single_req_credits_granted()` reconnects with one credit, raises the client-side max to 65535, sends a create, and requires the server to grant at least 8192 credits. `test_crediting_skipped_mid()` reconnects with 8192 credits, deliberately skips a MID, sends many writes without advancing the client credit window, then reuses the skipped MID on close and verifies the full 8192-credit window is restored.

IPC max-async-credit tests are driven by `test_ipc_max_async_credits()`. It verifies each tree starts with `num_loops` credits, opens `num_loops` LSA named-pipe handles per tree, sends a DCERPC bind ioctl on each handle, then schedules async pipe reads. Completion callbacks count `NT_STATUS_PENDING`, `NT_STATUS_INSUFFICIENT_RESOURCES`, and cancellation results. The expected steady state is `max_async_credits - 1` pending operations and the remaining over-limit operations rejected with insufficient resources. Wrappers create one IPC connection, two IPC connections, multichannel IPC, and a zero-length max-data variant.

Notify max-async-credit tests mirror the IPC shape through `test_notify_max_async_credits()`. The wrappers create or reuse `TESTDIR`, ask for `max_async_credits + 2` credits, open directory handles, issue async notify requests, verify the same pending/insufficient-resource split, close handles to cancel pending notifies, and check that pending requests end with `NT_STATUS_NOTIFY_CLEANUP`.

## State and Persistence Behavior

The tests mutate transport credit configuration and sometimes intentionally disconnect the original connection at the end. They create temporary files such as `single_req_credits_granted.dat` and `skipped_mid.dat`, and a temporary directory `test_max_async_credits` for notify tests. IPC tests open named-pipe handles and leave them scoped to per-test state allocations; cleanup frees state, closes/cancels requests, unlinks temporary files, removes `TESTDIR`, and disconnects transports.

The async state objects persist counters across callbacks: started operations, received statuses, pending statuses, insufficient-resource statuses, stop flags, request pointers, FIDs, and per-loop status. These counters are the authoritative test state for deciding whether the server enforces the async-credit limit.

## Dependencies and Integration Points

This file depends on the SMB2 client stack, SMBXCLI base credit accounting, tevent, command-line credentials, resolver and loadparm context, NDR LSA constants, and the torture SMB2 harness. It integrates as `torture_smb2_crediting_init()` with one-tree and two-tree tests. Runtime settings include `host`, `share`, `maxasynccredits`, and `samba4`; the two-connection and IPC multichannel tests skip against Samba4 source4 RPC server due to open-file pressure.

The tests are integration-heavy: they exercise server-side credit grant policy, MID window accounting, async pending limits, named-pipe RPC behavior, notify cancellation, and multichannel session binding.

## Risks and Edge Cases

- Expected values assume a default max async credits of 512 unless overridden; mismatched server configuration should use `maxasynccredits`.
- Tests intentionally stress many pending handles and requests, so resource limits, timeouts, and source4 RPC server file descriptor pressure can produce environmental failures.
- MID manipulation bypasses normal client-side sequencing and can disconnect nonconforming servers; cleanup resets the MID to avoid client-side confusion.
- The async loops use a 10-second wakeup and require tevent progress; slow systems may fail due to timing rather than semantic credit bugs.
- Multichannel tests require server and client support for channel binding and SPNEGO setup.

## Test Signals

Pass signals are exact credit counts after reconnect or request crediting, successful recovery after skipped MID reuse, exact pending and insufficient-resource counts for IPC reads and notify operations, correct cancellation statuses (`NT_STATUS_CANCELLED` for pipe reads and `NT_STATUS_NOTIFY_CLEANUP` for notify), successful cleanup closes, and no unexpected async stop flags.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/credits.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/delete-on-close.c -->
# sources/user-network-fs/samba/source4/torture/smb2/delete-on-close.c

## Purpose

`delete-on-close.c` is a focused SMB2 torture suite for delete-on-close behavior under different create dispositions, file existence states, directory permissions, read-only attributes, directory enumeration, and a regression scenario for Samba bug 14427. It registers the `delete-on-close-perms` suite.

## Important APIs, Types, and Functions

- SMB2 create/open and cleanup APIs: `smb2_create`, `smb2_close`, `smb2_util_close`, `smb2_util_unlink`, `smb2_deltree`, `torture_smb2_testdir`, and `torture_setup_simple_file`.
- Metadata and security APIs: `smb2_getinfo_file`, `smb2_setinfo_file`, `security_descriptor_dacl_create`, `dom_sid_string`, `RAW_FILEINFO_SEC_DESC`, `RAW_SFILEINFO_SEC_DESC`, and `RAW_SFILEINFO_DISPOSITION_INFORMATION`.
- Directory enumeration APIs: `smb2_find_level` with `SMB2_FIND_BOTH_DIRECTORY_INFO`.
- Helper functions: `create_dir()` creates `test_dir` with a DACL that allows many file operations but not delete/delete-child; `set_dir_delete_perms()` reopens the directory and grants delete and delete-child permissions.

## Control Flow

Each disposition test resets permissions, removes `test_dir`, creates a controlled directory, then sends an SMB2 create for `test_dir\test_create.dat` with `NTCREATEX_OPTIONS_DELETE_ON_CLOSE | NTCREATEX_OPTIONS_NON_DIRECTORY_FILE`. The non-existing cases for `OVERWRITE_IF`, `CREATE`, and `OPEN_IF` expect `NT_STATUS_OK`, close the handle, and verify a later open returns `NT_STATUS_OBJECT_NAME_NOT_FOUND`. The existing-file cases first create the file without delete-on-close and then expect `NT_STATUS_ACCESS_DENIED` for `OVERWRITE_IF` and `OPEN_IF`, or `NT_STATUS_OBJECT_NAME_COLLISION` for `CREATE`.

`test_doc_find_and_set_doc()` opens a directory, performs a find, sets disposition delete-on-close on the directory handle, and closes it. This checks that enumeration does not prevent setting delete-on-close when permissions allow it.

`test_doc_read_only()` checks read-only interactions. It uses the `delete_readonly` torture setting to decide whether the expected status is `NT_STATUS_OK` or `NT_STATUS_CANNOT_DELETE`. It tests create-time delete-on-close for a new read-only file, delete-on-close open of an existing read-only file, and setting disposition information on an already opened read-only file.

`test_doc_bug14427()` creates a random file through one tree connection, unlinks it through a second tree connection on the same session, and verifies the unlink succeeds. The comment notes it is a regression test and not strictly delete-on-close specific.

## State and Persistence Behavior

The suite uses fixed temporary paths `test_dir` and `test_dir\test_create.dat`, plus a randomized `doc_bug14427_*.dat`. It repeatedly changes the DACL on `test_dir` to model parent directories with and without delete rights. Per-test cleanup removes `test_dir`; the bug regression also unlinks the randomized file if the second tree connection remains allocated.

Security descriptor state is important: `create_dir()` builds an inheritable ACE without `SEC_STD_DELETE` or `SEC_DIR_DELETE_CHILD`, while `set_dir_delete_perms()` grants both. The tests are validating how create disposition and delete-on-close interact with both the requested file access mask and parent directory delete rights.

## Dependencies and Integration Points

This file depends on Samba's SMB2 torture harness, security descriptor helpers, NDR security flags, and SMB2 file-information set/query APIs. The suite initializer `torture_smb2_doc_init()` registers nine tests under `delete-on-close-perms`. Runtime behavior is affected by the Samba `delete readonly` server option, exposed to the test as the `delete_readonly` torture setting.

Integration points include filesystem authorization, DACL inheritance/owner handling, disposition-information setinfo, read-only attribute semantics, directory enumeration lifetime, multi-tree unlink behavior, and SMB2 create disposition handling.

## Risks and Edge Cases

- Several tests close `io.out.file.handle` even after expected create failures; this relies on the utility close path tolerating empty or invalid handles.
- Fixed path names can conflict with parallel runs on the same share.
- Read-only expected behavior is configuration-dependent; running without the correct `delete_readonly` setting can make a valid server appear to fail.
- DACL tests assume the connected user can set owner/DACL metadata on the test directory.
- The bug 14427 test frees `tree1` before returning, which is unusual for one-tree torture tests and may matter to harness lifetime assumptions.

## Test Signals

Pass signals are exact NT status results for each create disposition/existence combination, confirmed deletion after successful delete-on-close, successful set-disposition after a directory find, expected `NT_STATUS_CANNOT_DELETE` or `NT_STATUS_OK` for read-only cases based on configuration, successful unlink through a second tree connection, and successful cleanup of the controlled directory tree.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/delete-on-close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/deny.c -->
# sources/user-network-fs/samba/source4/torture/smb2/deny.c

## Purpose

`deny.c` implements the SMB2 deny/share-mode matrix tests. It opens the same file through one or two SMB2 tree connections with many combinations of desired access and share access, then verifies whether the second open can read, write, both, neither, or cannot open. It registers the `deny` suite with single-connection and two-connection variants.

## Important APIs, Types, and Functions

- `enum deny_result` encodes expected behavior: `A_X` for first-open failure, `A_0` for no read/write access by the second handle, `A_R`, `A_W`, and `A_RW`.
- `denytable[]` is the central expectation table. Each row includes whether the target is `.exe` or `.dat`, first desired access/share access, second desired access/share access, and expected outcome.
- Formatting helpers `denystr()`, `openstr()`, and `resultstr()` turn table values into readable torture output.
- `torture_smb2_denytest2()` runs the two-tree matrix; `torture_smb2_denytest1()` calls it with the same tree for both arguments.
- SMB2 operations used are `smb2_create`, `smb2_read`, `smb2_write`, `smb2_util_write`, `smb2_util_close`, and `smb2_util_unlink`.

## Control Flow

The test creates two seed files, `denytest2.dat` and `denytest2.exe`, writes a small payload into each, and then iterates over every row in `denytable`. For each row it opens the target file once with `mode1` and `deny1`, then attempts a second open with `mode2` and `deny2`. If the first open fails, the result is `A_X`; if the second open fails, the result is `A_0`; otherwise the test attempts a one-byte read and one-byte write through the second handle and combines successful operations into `A_R`, `A_W`, or `A_RW`.

The observed result is compared against the row's expected `deny_result`. If `showall` is enabled, or when a mismatch occurs, the test prints elapsed time, filename, share modes, access modes, observed result, and expected result. It closes both handles after each row and unlinks the seed files during cleanup.

## State and Persistence Behavior

Persistent state is limited to two temporary files with known names and one-byte/short-string content. The deny matrix mutates file content when rows allow writes through the second handle, but the test only needs read/write success status, not stable content. Handles are opened and closed for each row to avoid carrying share-mode state between combinations.

The expectation table is static and source-controlled. It acts as the persistent specification for Windows-compatible SMB2 share-mode behavior across executable and non-executable names.

## Dependencies and Integration Points

The source depends on SMB2 client calls and the torture SMB2 registration helpers. `torture_smb2_deny_init()` registers `deny1` via `torture_suite_add_1smb2_test()` and `deny2` via `torture_suite_add_2smb2_test()`, integrating with the harness's ability to provide one or two tree connections.

The test is an integration point for server share-mode enforcement, desired-access mapping, executable-file special cases, same-connection versus cross-connection behavior, and read/write I/O authorization after opens have succeeded.

## Risks and Edge Cases

- The large static table is hard to audit manually; table drift or a single mistaken row can create broad compatibility noise.
- The same filenames are used for every run, so parallel runs in one share namespace can interfere.
- Some rows write through the second handle; if a server's share-mode behavior depends on file content or oplocks outside this test, failures may be hard to diagnose from the matrix alone.
- Progress output is enabled by default through the `progress` setting and uses carriage returns, which can be noisy in non-interactive logs.
- The expected behavior distinguishes `.exe` and `.dat`, so filesystems or servers without executable-name-specific handling may intentionally differ.

## Test Signals

Pass signals are successful seed-file creation, completion of every `denytable` row without mismatches, exact read/write/open result classification per row, and successful cleanup. Failure output includes the mismatched row's share/access modes and observed versus expected symbolic result, making this suite useful for pinpointing share-mode regressions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/deny.c -->
