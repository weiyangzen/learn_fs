# subset-b-010003 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/notify.c -->
# sources/user-network-fs/samba/source4/torture/smb2/notify.c

## Purpose

`notify.c` is the main Samba torture suite for SMB2 `CHANGE_NOTIFY`. It opens SMB2 directory handles, posts asynchronous notify requests, mutates the share through the same or a second tree connection, and asserts the exact NT status, action list, relative wire names, and cleanup behavior returned by the server. The suite is intentionally behavioral rather than unit-level: it verifies protocol compatibility around buffering, recursion, completion filters, cancellation, session/tree teardown, backend overflow, inotify rename shape, ACL updates, and permissions.

Two suite entry points are exported. `torture_smb2_notify_init()` registers the normal `notify` suite, while `torture_smb2_notify_inotify_init()` registers the narrower `notify-inotify` suite for backend-specific rename behavior.

## Important APIs, Types, and Helpers

- The test code uses Samba's torture framework types: `struct torture_context`, `struct torture_suite`, and registration helpers such as `torture_suite_add_1smb2_test()` and `torture_suite_add_2smb2_test()`.
- SMB2 protocol operations are issued through `struct smb2_tree`, `struct smb2_session`, `struct smb2_transport`, `struct smb2_handle`, `struct smb2_request`, `struct smb2_create`, `struct smb2_notify`, `union smb_open`, `union smb_notify`, `union smb_setfileinfo`, `union smb_close`, and `union smb_fileinfo`.
- Core client APIs include `smb2_create()`, `smb2_notify_send()`, `smb2_notify_recv()`, `smb2_cancel()`, `smb2_close()`, `smb2_tdis()`, `smb2_logoff()`, `smb2_setinfo_file()`, `smb2_getinfo_file()`, `smb2_session_setup_spnego()`, `smb2_transport_idle_handler()`, and `smb2_transport_dead()`.
- Utility helpers such as `smb2_util_mkdir()`, `smb2_util_rmdir()`, `smb2_util_unlink()`, `smb2_deltree()`, `smb2_util_close()`, `smb2_util_setatr()`, `smb2_util_write()`, `smb2_util_roothandle()`, `torture_setup_simple_file()`, `torture_smb2_testdir()`, `torture_smb2_testfile()`, `torture_smb2_testdir_access()`, and `smb2_create_complex_file()` set up server-side filesystem state.
- Local assertion macros `CHECK_STATUS`, `CHECK_VAL`, and `CHECK_WIRE_STR` convert mismatches into torture failures and jump to each test's cleanup label. `WAIT_FOR_ASYNC_RESPONSE` advances the `tevent` loop until a notify request can be cancelled or has progressed beyond the receive state.
- `custom_smb2_create()` wraps `smb2_create()` after deleting any existing path and returns a zero handle on failure. It relies on the surrounding `CHECK_STATUS` macro and is used heavily by mask and overflow tests.
- `notify_timeout()` is a `tevent` timer callback that cancels a pending notify request. `tcp_dis_handler()` simulates a local transport disconnect by marking the SMB2 transport dead.

## Test Coverage and Control Flow

`test_valid_request()` checks baseline request validity. It posts a notify on the root handle, creates `smb2-notify01.dat`, expects `NOTIFY_ACTION_ADDED`, then probes zero and undersized output buffers. It verifies `NT_STATUS_NOTIFY_ENUM_DIR` when changes do not fit, that an overflow state can persist across later notifies on the same directory handle, and that a buffer larger than the negotiated max transaction size yields `NT_STATUS_INVALID_PARAMETER`.

`torture_smb2_notify_dir()` exercises normal directory notifications. It creates a directory, posts cancelable requests, verifies mkdir/rmdir events, checks buffered create and unlink behavior across two directory handles, confirms that pre-existing buffered events are handle-specific, and expects `NT_STATUS_NOTIFY_CLEANUP` when the watched directory handle is closed. It uses `torture_numops` to scale the buffered create/unlink portion.

`torture_smb2_notify_recursive()` builds nested directories and files, performs renames and removals, and compares recursive versus non-recursive delivery. The expected recursive result is a fixed ordered list of add, old-name, new-name, remove, and add/rename events using paths relative to the watched base directory.

`torture_smb2_notify_mask_change()` demonstrates that once a directory handle's notify mask is initialized, later attempts to expand the completion filter on that same handle do not retroactively change the active backend mask. It first watches attributes only, then asks for name and creation changes too, yet still expects modified events associated with attribute/timestamp side effects rather than a full name-change stream.

`torture_smb2_notify_mask()` is the most systematic completion-filter test. Its `NOTIFY_MASK_TEST` macro iterates all 32 single-bit masks for each operation, posts an initial cancelled request to initialize buffering, performs one filesystem operation, cancels after a short wait, and validates whether a change arrived. Covered operations include mkdir, file create, unlink, rmdir, file rename, directory rename, path attribute update, write time, create time, access time, change time, and data write. Some expected masks are explicitly zero because Samba or Windows behavior maps those operations through broader modified events rather than the nominal mask bit.

`torture_smb2_notify_file()` verifies that a notify request on a non-directory file handle is rejected with `NT_STATUS_INVALID_PARAMETER`.

Tree, handle, session, and transport lifetime tests cover pending notify cleanup. `torture_smb2_notify_tree_disconnect()` cancels before tree disconnect, `torture_smb2_notify_tree_disconnect_1()` disconnects with a pending async request and expects `NT_STATUS_NOTIFY_CLEANUP`, `torture_smb2_notify_close()` closes the watched handle and expects cleanup, `torture_smb2_notify_ulogoff()` logs off the session and expects cleanup, `torture_smb2_notify_session_reconnect()` reauthenticates with the previous session id and verifies the old pending notify is cleaned up, `torture_smb2_notify_invalid_reauth()` attempts failed SPNEGO reauth and then verifies the session is deleted, and `torture_smb2_notify_tcp_disconnect()` simulates a local TCP disconnect and expects `NT_STATUS_LOCAL_DISCONNECT`.

`torture_smb2_notify_double()` posts two notify requests against one directory handle and verifies they complete on successive events rather than both consuming the same event. `torture_smb2_notify_tree()` builds a matrix of watched directories at different depths with recursive and non-recursive flags, triggers two events in every listed path, polls/cancels notifies for up to 20 seconds, and compares counted events against a hard-coded expected table.

`torture_smb2_notify_overflow()` pre-initializes a notify buffer, creates 100 directories, and expects `NT_STATUS_NOTIFY_ENUM_DIR` with zero returned changes once cached server-side events exceed the response packet capacity. `torture_smb2_notify_basedir()` confirms that attribute changes to the watched base directory itself are not reported, while a child file attribute change is reported.

`torture_smb2_notify_tcon()` verifies simple mkdir/rmdir notifications first on one tree connection, then with mutations from a secondary tree connection on the same session, and finally after disconnecting the secondary tree. This proves notification visibility is share-wide rather than limited to one tree id.

`torture_smb2_notify_rmdir()` and wrappers `rmdir1` through `rmdir4` cover delete-pending behavior when a watched directory is removed directly or marked delete-on-close, using either one tree or two trees. The pending notify must receive `NT_STATUS_DELETE_PENDING`.

`torture_smb2_inotify_rename()` is the backend-oriented rename test. It watches a directory with `SEC_RIGHTS_DIR_ALL` minus delete, renames a subdirectory from another tree, and accepts either a single response containing two changes or two one-change responses. The accepted action pairs are old-name/new-name or removed/added, with names `subdir-name` and `subdir-name-r`.

`torture_smb2_notify_handle_permissions()` opens a directory with only `SEC_FILE_READ_ATTRIBUTE`, posts and cancels a notify, and expects `NT_STATUS_ACCESS_DENIED` because the handle lacks ChangeNotify permission. `torture_smb2_notify_acl_args()` and `torture_smb2_notify_acl()` test security descriptor notifications by optionally copying the existing DACL or adding an ACE, setting `SECINFO_DACL`, and requiring one modified event under both `FILE_NOTIFY_CHANGE_SECURITY` and `FILE_NOTIFY_CHANGE_ALL`.

## State and Persistence Behavior

The tests create temporary trees under `test_notify`-prefixed directories and remove them with `smb2_deltree()` and `smb2_util_rmdir()` in setup/cleanup paths. They do not persist local state; all meaningful state is server-side SMB state: open directory handles, per-handle notify masks, pending async requests, server notify buffers, session identities, tree connections, and security descriptors.

Several tests intentionally depend on server-side buffering across request boundaries. Initial cancelled notify requests can initialize backend buffers; later requests may consume cached events. The mask-change test depends on a handle-persistent completion mask. Overflow tests depend on a server-side overflow/enum-dir condition. Lifetime tests depend on correct cancellation and cleanup when handles, trees, sessions, or transports are torn down.

## Dependencies and Integration Points

This file integrates with the Samba SMB2 torture harness and low-level SMB client libraries. It depends on event-loop progress through `tevent`, NDR/security descriptor support for ACL tests, credentials APIs for invalid reauth, command-line torture settings such as `samba3`, and negotiated SMB2 transport limits through `smb2cli_conn_max_trans_size()`.

The exported suite functions are the only external interface. The normal suite registers test names including `valid-req`, `tcon`, `dir`, `mask`, `tdis`, `tdis1`, `mask-change`, `close`, `logoff`, `session-reconnect`, `invalid-reauth`, `tree`, `basedir`, `double`, `file`, `tcp`, `rec`, `overflow`, `rmdir1` to `rmdir4`, `handle-permissions`, and `security`. The inotify suite registers `inotify-rename`.

## Risks and Edge Cases

- Timing sensitivity is significant. The suite uses `smb_msleep()`, event-loop polling, timers, and a 20-second propagation loop. Slow backends or overloaded CI can create false negatives or mask ordering differences.
- Many checks assert exact event counts and ordering. That is useful for protocol compatibility but fragile across backend implementations that legally coalesce, split, or reorder some events.
- `NOTIFY_MASK_TEST` cancels pending requests after a fixed 200 ms. If an expected event has not propagated by then, the status may remain cancelled and the test may under-report support for that mask.
- The mask-change and overflow tests intentionally depend on per-handle backend state. Reusing handles or changing cleanup sequencing can alter results.
- `torture_smb2_notify_tree_disconnect()` stores the status from `smb2_tdis()` and then calls `smb2_notify_recv()` without assigning its return value before rechecking `status`; the test therefore primarily verifies that the tree disconnect succeeded and that no changes are recorded, not the actual post-disconnect notify receive status.
- `custom_smb2_create()` uses the file-local `CHECK_STATUS` macro from a helper with its own `ret` and `done` label. This works but couples the helper to the macro convention and makes failures less obvious than explicit returns.
- Tests often continue cleanup after failed operations; cleanup failures are mostly ignored, which is normal for torture cleanup but can leave temporary server objects after severe failures.

## Test Signals

Passing this suite signals that SMB2 change notify implements the important Windows-compatible semantics for request validation, name/attribute/security filters, recursion, buffering, overflow, handle permissions, directory-only constraints, delete-pending, base-directory suppression, and cleanup on close/tree disconnect/logoff/reconnect/transport loss. Failures are usually high-signal because each assertion includes an expected NT status, action code, change count, or relative path name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/notify_disabled.c -->
# sources/user-network-fs/samba/source4/torture/smb2/notify_disabled.c

## Purpose

`notify_disabled.c` is a small Samba torture suite that verifies the server behavior when SMB2 change notify support is disabled or unavailable. Instead of expecting a pending async request and later filesystem-triggered completion, it opens a directory, submits one `CHANGE_NOTIFY` request, and requires `NT_STATUS_NOT_IMPLEMENTED`.

The exported entry point `torture_smb2_notify_disabled_init()` creates the `change_notify_disabled` suite and registers a single one-tree SMB2 test named `notfiy_disabled` (the spelling appears in the source).

## Important APIs, Types, and Functions

- `torture_smb2_notify_disabled()` is the sole test body. It uses `struct torture_context`, `struct smb2_tree`, `union smb_open`, `union smb_notify`, `struct smb2_handle`, and `struct smb2_request`.
- SMB2 calls are limited to directory setup and notify probing: `smb2_deltree()`, `smb2_util_rmdir()`, `smb2_create()`, `smb2_notify_send()`, `smb2_notify_recv()`, and `smb2_util_close()`.
- Assertions use `torture_assert_ntstatus_equal_goto()` instead of the custom macros used in `notify.c`.
- The test creates a temporary directory under `test_notify_disabled`, using `SEC_FILE_ALL`, directory create options, normal attributes, and read/write sharing.

## Control Flow

The test removes any stale `test_notify_disabled` directory, creates the directory with `NTCREATEX_DISP_CREATE`, and stores the returned directory handle. It then initializes an SMB2 notify request with a 1000-byte buffer, `FILE_NOTIFY_CHANGE_NAME`, the directory handle, and recursive mode enabled.

Unlike the normal notify suite, it does not create or remove a child object to trigger completion. It immediately calls `smb2_notify_recv()` after `smb2_notify_send()` and asserts that the server returns `NT_STATUS_NOT_IMPLEMENTED`. If that status is observed, it closes the directory handle, asserts close success, and deletes the temporary directory in the shared cleanup block.

## State and Persistence Behavior

The file has no persistent local state. The only server-side state is the temporary directory and its open handle. Cleanup always calls `smb2_deltree()` on `test_notify_disabled`, and the handle is closed on the success path before cleanup. If creation fails before a valid handle exists, the cleanup path still removes the directory tree.

Because the expected notify result is immediate `NT_STATUS_NOT_IMPLEMENTED`, this test does not rely on event-loop progress, backend buffering, second tree connections, or asynchronous cancellation.

## Dependencies and Integration Points

The file includes the same broad Samba SMB2 torture and security headers as the full notify test, but its practical dependencies are the SMB2 client call layer and the torture registration API. The suite integrates through `torture_suite_create()` and `torture_suite_add_1smb2_test()`, making it selectable as `change_notify_disabled`.

This suite complements `notify.c`: `notify.c` validates enabled notify semantics, while this file validates the expected status when the feature is intentionally disabled.

## Risks and Edge Cases

- The registered test name is spelled `notfiy_disabled`; callers and dashboards may need to use that exact typo unless the source is changed.
- The code assumes disabled notify returns `NT_STATUS_NOT_IMPLEMENTED` synchronously enough for direct receive. A backend that leaves the request pending, returns `NT_STATUS_INVALID_DEVICE_REQUEST`, or reports another feature-disabled status would fail.
- On the path where `smb2_notify_recv()` fails with an unexpected status, the handle is not explicitly closed before `smb2_deltree()`. The tree cleanup may still remove server objects, but the test does not validate close behavior in failure cleanup.
- The broad include list mirrors the main notify suite and is larger than this file needs; this is harmless but increases compile coupling.

## Test Signals

Passing this test is a clear signal that a disabled change-notify configuration rejects SMB2 notify requests with the expected protocol status. Failing it means either the feature is unexpectedly enabled, the disabled path returns a different status, or the server mishandles the simple directory setup needed before the notify probe.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/notify_disabled.c -->
