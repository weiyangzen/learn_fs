# Research: subset-b-010008

Grouped research for Samba torture utility and VFS ACL xattr sources.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/util_smb.c -->
# sources/user-network-fs/samba/source4/torture/util_smb.c

## Purpose

This file is a shared SMB1-oriented support library for Samba torture tests. It provides reusable helpers for preparing test directories and files, creating deliberately feature-rich file system objects, checking wire encodings and extended attributes, opening and closing SMB client connections, running tests with one, two, or many SMB connections, opening a second tree connect on an existing session, checking privileges, and building alternate credentials from torture settings.

The file is not a standalone test suite. Its exported functions are consumed by many torture suites that need consistent setup, connection lifecycle, and registration wrappers around `struct torture_suite` and `struct torture_test`.

## Important APIs, Types, and Functions

- `torture_setup_dir()` exits the current SMB session state, deletes a directory tree, and recreates the named directory for a clean test root.
- `create_directory_handle()` opens or creates a directory with `RAW_OPEN_NTCREATEX`, full file rights, directory create options, and broad share access, returning the opened file number through `fnum`.
- `create_complex_file()` and `create_complex_dir()` create test objects with extended attributes and deliberately distinct create, access, and write timestamps. The file variant also writes a small payload.
- `wire_bad_flags()` validates the marshalled byte length of an `smb_wire_string` against string flags, negotiated Unicode capability, client Unicode options, and `CLI_FORCE_ASCII`.
- `dump_all_info()` and `torture_all_info()` print `RAW_FILEINFO_ALL_INFO` fields for debugging path-based query results.
- `torture_set_file_attribute()` sets path attributes through `RAW_SFILEINFO_BASIC_INFORMATION`.
- `torture_set_sparse()` sends `FSCTL_SET_SPARSE` through the raw NT IOCTL layer for an open file number.
- `torture_check_ea()` queries one EA by name and validates name matching, value length, and value bytes.
- `torture_open_connection_share()`, `torture_get_conn_index()`, `torture_open_connection_ev()`, `torture_open_connection()`, and `torture_close_connection()` centralize SMB1 client connection setup using loadparm settings, command-line credentials, resolver context, event context, and per-test options.
- `check_error()` compares the most recent tree error against either DOS class/code or an expected `NTSTATUS`.
- `torture_create_procs()` forks multiple SMB clients, synchronizes their start through shared memory and `SIGCONT`, runs a callback per child, and aggregates torture results.
- `torture_suite_add_smb_multi_test()`, `torture_suite_add_2smb_test()`, and `torture_suite_add_1smb_test()` register callbacks with wrappers that supply multiple, two, or one open SMB connection.
- `torture_second_tcon()` performs an additional `TCONX` on an existing SMB session and protects the session key if extended signatures are negotiated.
- `torture_check_privilege()` checks a SID's LSA privilege, with a local shortcut that treats the built-in Administrator RID as having all privileges.
- `torture_user2_credentials()` creates a second credential set from `torture:user2*` settings or falls back to anonymous credentials.

Key local state includes the static `current_cli` used by forked child tests and `struct child_status`, a shared-memory record containing child PID, start flag, result, and failure reason.

## Control Flow

Setup helpers follow a direct cleanup-then-create pattern. `torture_setup_dir()` calls `smb_raw_exit()` before `smbcli_deltree()` and `smbcli_mkdir()`, ensuring pending SMB state is cleared before a test root is recreated. `create_directory_handle()` builds a raw `NTCREATEX` open request under a temporary talloc context, frees that context after `smb_raw_open()`, and only writes `*fnum` if the status is OK.

The complex object helpers first remove or create the target, then optionally set EAs when the name is not an alternate data stream path containing `:`. They assign two named EAs, set staggered timestamps relative to the current even second, query the object back with `RAW_FILEINFO_BASIC_INFO`, and print diagnostic messages if the server does not return the requested times. They return the open file number even if EA or timestamp setup only emitted warnings.

Connection setup begins with `torture_get_conn_index()`. By default it copies the `host` and `share` torture settings. If `torture:unclist` points to a file, it loads all lines and selects `conn_index % num_unc_names`; entries without a leading slash are treated as hostnames, while UNC-like entries are parsed into host/share pairs. `torture_open_connection_share()` then obtains SMB client and session options from loadparm, overlays `use_oplocks` and `use_level2_oplocks` from torture settings, and calls `smbcli_full_connection()` with command-line credentials and gensec settings.

The one- and two-connection registration wrappers open the requested clients, invoke the callback stored in `test->fn`, and release the client talloc objects at the `fail:` label. The multi-process path is more involved: the parent allocates a shared `child_status` array, forks `torture:nprocs` children, and waits until each child has opened a connection and stored its PID. Each child sets a unique NetBIOS name, retries connection establishment briefly, pauses until the parent sets its `start` flag and sends `SIGCONT`, runs the callback, stores any torture failure result and reason, and exits. The parent starts all children together with `kill(0, SIGCONT)`, waits for exits, and replays each child failure into the parent torture context.

`torture_second_tcon()` has its own small lifecycle: allocate a temporary context, initialize a new `smbcli_tree` against the existing session, submit a raw `TCONX` request with extended response and signatures flags, store the returned TID, optionally calls `smb1cli_session_protect_session_key()`, then steals the tree onto the caller context.

## State and Persistence Behavior

Most state is remote SMB server state created for tests: directories, files, EAs, attributes, timestamps, sparse-file flags, and extra tree connects. `torture_setup_dir()` and the complex object helpers are intentionally destructive for the named paths. They can remove existing trees or files on the configured test share.

Local persistent state is minimal. The file reads an optional UNC list from disk but does not write files. `torture_create_procs()` uses anonymous shared memory for child coordination and process-local signal handlers. `torture_user2_credentials()` returns a talloc-owned shallow copy of the command-line credentials with mutable username/domain/password or anonymous state.

Resource cleanup is mixed. Many helper paths free temporary talloc contexts and close tree connections. Some wrappers release `smbcli_state` objects with `talloc_free()` rather than calling `torture_close_connection()`, relying on underlying destructors and process teardown. Failed or interrupted tests may leave remote test files, directories, EAs, or open server-side handles until session cleanup.

## Dependencies and Integration Points

This file sits at the intersection of the torture framework and the SMB1 raw client stack. It depends on raw SMB protocol unions and constants, SMB client connection APIs, loadparm configuration, command-line credential handling, resolver and event contexts, security SID and privilege helpers, talloc, Samba debug/printing utilities, process and shared-memory system wrappers, and torture assertion/result infrastructure.

It integrates upward through `torture/util.h` declarations and exported helper functions used by other torture suites. It integrates downward with server-visible SMB operations: create/open, pathinfo/fileinfo, setfileinfo, IOCTL, deltree, mkdir, tree disconnect, and TCONX. Authentication integration is through `samba_cmdline_get_creds()`, optional `torture:user2*` settings, and gensec settings from the active torture context.

## Risks and Edge Cases

Several helpers return success-like handles after partial setup failures. For example, complex file and directory creation prints failures for EA or timestamp setup but still returns the open file number. Callers that require exact EA or timestamp state need to verify it explicitly.

Alternate data stream names skip EA setup by checking for `:` anywhere in the name. This is pragmatic for SMB tests but can produce different object complexity based solely on path spelling. Timestamp comparisons are exact, which can be sensitive to server timestamp resolution, timezone conversion bugs, or filesystem rounding.

`wire_bad_flags()` intentionally approximates wire-string length rules. It may reject or accept edge cases around Unicode negotiation, terminators, or client-forced ASCII that a deeper marshalling test would handle differently.

The multi-process runner has process-control hazards. `kill(0, SIGCONT)` signals the whole process group, not only the forked children. Child failure collection uses shared-memory fields without locks and parent exit checks are coarse. `WEXITSTATUS(status)` is read without first checking `WIFEXITED()`, so signal exits can be under-reported. The child retry counter is initialized before forking and then decremented independently in each child copy, which is acceptable but easy to misread.

`torture_check_privilege()` returns immediately for Administrator RID without freeing `tmp_ctx`, creating a small leak on that path. `torture_get_conn_index()` returns false without freeing `unc_list` on some parse failures. These leaks are usually bounded in torture process lifetimes but matter for long-running in-process test harnesses.

## Test Signals

Useful signals from this file are indirect: downstream torture suites pass when these helpers create clean directories, set attributes/EAs/times consistently, open the expected number of connections, synchronize multi-client starts, and report exact SMB errors. Diagnostics printed by `create_complex_file()`, `create_complex_dir()`, `wire_bad_flags()`, `torture_check_ea()`, `check_error()`, and child result aggregation are important failure breadcrumbs. Regressions commonly appear as setup failures, mismatched `NTSTATUS` or DOS errors, bad EA contents, unexpected wire string lengths, inability to create sparse files, failed multi-client startup, or inconsistent cleanup after test failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/util_smb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/acl_xattr.c -->
# sources/user-network-fs/samba/source4/torture/vfs/acl_xattr.c

## Purpose

This file defines the `acl_xattr` VFS torture suite. It is a focused SMB2 regression test for `vfs_acl_xattr` behavior when the share is configured to ignore the underlying system ACL and synthesize default ACLs in either POSIX-style or Windows-style mode.

The suite creates a directory, replaces its DACL with a non-inheritable owner-only ACE, creates a child file, reads the child's security descriptor, and checks that the resulting descriptor matches the configured default ACL style. It validates Samba's security descriptor persistence and defaulting behavior as observed over SMB2 rather than testing the VFS module internally.

## Important APIs, Types, and Functions

- `BASEDIR` is the fixed test root `smb2-testsd`.
- `CHECK_SECURITY_DESCRIPTOR(_sd1, _sd2)` compares descriptors with `security_descriptor_equal()`, prints both descriptors with `NDR_PRINT_DEBUG(security_descriptor, ...)` on mismatch, records `TORTURE_FAIL`, and flips the local `ret` flag.
- `test_default_acl_posix()` connects to share `acl_xattr_ign_sysacl_posix` and expects a child file default descriptor containing owner full control, owning group generic read/write/execute, world generic read/write/execute, and system full control.
- `test_default_acl_win()` connects to share `acl_xattr_ign_sysacl_windows` and expects a child file default descriptor containing only owner full control and system full control.
- `torture_acl_xattr()` builds the suite and registers `default-acl-style-posix` and `default-acl-style-windows` as SMB2 tests through `torture_suite_add_1smb2_test()`.

The file uses `struct smb2_tree`, `struct smb2_handle`, `union smb_fileinfo`, `union smb_setfileinfo`, and `struct security_descriptor` as its main protocol-facing types.

## Control Flow

Both test functions share the same structure. They ignore the incoming `tree_unused` parameter and explicitly connect to the share variant under test with `torture_smb2_con_share()`. They call `smb2_util_setup_dir()` to recreate `BASEDIR`, open `BASEDIR\testdir` with `torture_smb2_testdir()`, and query the directory security descriptor using `RAW_FILEINFO_SEC_DESC` with `SECINFO_DACL | SECINFO_OWNER | SECINFO_GROUP`.

The owner and group SIDs from the original directory descriptor are converted to strings with `dom_sid_string()`. The test then builds a new security descriptor with `security_descriptor_dacl_create()` containing one non-inheritable `SEC_ACE_TYPE_ACCESS_ALLOWED` ACE for the owner SID with `SEC_RIGHTS_DIR_ALL`. That descriptor is written back to the directory with `RAW_SFILEINFO_SEC_DESC` and `SECINFO_DACL`.

After closing the directory handle, the test creates `BASEDIR\testdir\testfile` with `torture_smb2_testfile()`, queries the file security descriptor with owner, group, and DACL information, closes the file handle, and constructs the expected descriptor. The POSIX test includes owner, group, world, and system ACEs. The Windows test includes only owner and system ACEs. `CHECK_SECURITY_DESCRIPTOR()` performs the final comparison.

Both tests jump to a common `done:` block on assertion failure. The cleanup block closes any non-empty file or directory handle, deletes `BASEDIR` with `smb2_deltree()`, disconnects the tree with `smb2_tdis()`, and returns the accumulated boolean result.

## State and Persistence Behavior

The test mutates only the configured SMB share. It creates and deletes the fixed tree `smb2-testsd`, creates `testdir` and `testfile`, and writes a DACL onto the directory. Successful cleanup removes the test root at the end of each test. If the process crashes or the server disconnects before `done:`, stale test paths or ACL xattrs can remain on the share.

There is no local file persistence. All security descriptors are talloc-owned under the torture context. The queried owner and group SID strings are derived from the live server response so the expected descriptor is anchored to the actual share identity rather than hard-coded domain SIDs.

## Dependencies and Integration Points

The suite depends on the SMB2 torture utilities, SMB2 getinfo/setinfo calls, security descriptor construction/comparison helpers, generated NDR security printing, Samba loadparm/cmdline plumbing, and the VFS torture registration header. It requires test environment shares named `acl_xattr_ign_sysacl_posix` and `acl_xattr_ign_sysacl_windows`, with configurations that exercise `vfs_acl_xattr` and differ in default ACL style.

Integration is through the global torture registry: `torture_acl_xattr()` creates a suite named `acl_xattr` with description `vfs_acl_xattr tests`. At runtime the tests validate behavior across SMB2, the VFS ACL xattr module, the underlying filesystem ACL/xattr storage, and Samba's NT security descriptor mapping.

## Risks and Edge Cases

The expected descriptors are exact. ACE order, owner/group preservation, generic rights expansion, and default ACL synthesis must match precisely. Any legitimate implementation change that preserves effective access but changes descriptor shape can fail the test.

The test relies on fixed share names. If those shares are absent or not configured with the intended `acl_xattr` options, the test fails at connection setup or reports misleading descriptor differences. Because the initial directory owner and group are captured dynamically, failures usually point to DACL construction/defaulting rather than domain-specific SID values.

The `CHECK_SECURITY_DESCRIPTOR` macro assumes local variables named `tctx` and `ret`, so it is tightly coupled to the test function shape. The tests close handles before comparing descriptors, which is fine for the current flow but can make later debugging slightly less direct if a mismatch depends on live handle state.

## Test Signals

The primary pass signal is an exact `security_descriptor_equal()` match for each share's expected child-file descriptor. Secondary signals include successful setup of `BASEDIR`, successful directory and file creation, successful SMB2 security descriptor query and set calls, and clean deletion of the test tree. Failures indicate regressions in ignored-system-ACL behavior, default ACL style selection, descriptor inheritance/defaulting, SMB2 security descriptor get/set handling, or test share configuration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/acl_xattr.c -->
