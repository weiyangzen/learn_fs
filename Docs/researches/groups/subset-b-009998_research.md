# subset-b-009998 Research

Grouped research for Samba SMB2 torture sources. Each section preserves the source path and is bounded for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/dir.c -->
# sources/user-network-fs/samba/source4/torture/smb2/dir.c

## Purpose
`dir.c` implements the `smb2.dir` torture suite for SMB2 directory enumeration. It creates controlled directory trees, issues SMB2 FIND requests at multiple information levels, validates returned names and metadata against SMB2 GETINFO, exercises continuation behavior, and probes edge cases where directories are modified during enumeration. The tests are primarily about correctness of `SMB2_FIND_*` output, resume semantics, ordering assumptions, file-index behavior, scalability with large directories, and behavior while files are renamed or deleted.

## Important APIs, Types, And Functions
The file relies on Samba SMB2 client APIs from `libcli/smb2/smb2.h` and `smb2_calls.h`, raw SMB search/fileinfo unions, torture assertion helpers, talloc allocation, and `TYPESAFE_QSORT` from `lib/util/tsort.h`.

Key local types are:

- `struct file_elem`, which stores a generated filename, creation time, and a `found` flag used by enumeration validation.
- The static `levels[]` table, mapping SMB2 find information classes to raw search data levels and offsets for name and resume-key fields.
- `struct multiple_result`, a talloc-backed accumulator for non-dot search results.
- `enum continue_type`, which models the continuation modes tested by `multiple_smb2_search()`: single, file-index resume, restart, and reopen.

Important functions are:

- `populate_tree()`: removes and recreates `smb2_dir`, creates a requested number of unique files, stores their names and create times, closes and reopens the directory handle so smbd's later `readdir()` view is fresh, and returns the reopened directory handle.
- `test_find()`: validates simple enumeration with `SMB2_FIND_BOTH_DIRECTORY_INFO`, a small first response, and later larger responses. It checks that all generated files appear and that create times match the values returned by create.
- `test_fixed()`: starts enumeration on one directory handle, deletes files through a second handle, then ensures the first enumeration does not return stale deleted entries.
- `torture_single_file_search()` and `test_one_file()`: issue one-file searches for every level in `levels[]`, then compare returned fields with `RAW_FILEINFO_SMB2_ALL_INFORMATION`, alternate name info, and internal file ID information.
- `multiple_smb2_search()`: common multi-call enumeration helper that changes `continue_flags` after the first response, optionally copying the previous returned `file_index` into the next request.
- `test_many_files()`: creates 700 files and validates all information levels under all continuation modes, sorting the result client-side before comparing names.
- `test_modify_search()`: mutates attributes, deletes files, creates new names, and sets delete-on-close during a search, then restarts enumeration and checks final visibility and attributes.
- `test_sorted()`: observes whether returned names are case-insensitively sorted, but treats unsorted responses as non-fatal.
- `test_file_index()`: probes optional server support for honoring resume-by-file-index.
- `test_large_files()`: creates 2,000 files with names from 1 to 200 characters and times full enumeration.
- `test_1k_files_rename()`: repeatedly enumerates 1,000 files while renaming one file per iteration, optionally reopening the directory each iteration through the `1k_files_rename_reopendir` torture setting.
- `torture_smb2_dir_init()`: registers the suite as `dir` with tests `find`, `fixed`, `one`, `many`, `modify`, `sorted`, `file-index`, `large-files`, and `1kfiles_rename`.

## Control Flow
Most tests follow the same pattern: delete the test directory, create it with directory access, create files with `SEC_RIGHTS_FILE_ALL`, reopen the directory handle when the server-side directory stream must be refreshed, issue one or more `smb2_find_level()` calls, validate the returned `union smb_search_data` array, then close handles and remove the tree.

For single-file metadata validation, `test_one_file()` creates `torture_search.txt`, stores one response per find level in `levels[i].data`, queries the same file by handle with SMB2 GETINFO, and runs a set of field-comparison macros. The macros compare attributes, NTTIME fields, sizes, EA size, names, short name, and file IDs where the information class exposes them.

For repeated enumeration, `multiple_smb2_search()` starts with `SMB2_CONTINUE_FLAG_RESTART` unless the caller asks for reopen. It accumulates results via `fill_result()`, then sets the next continuation behavior: `SMB2_CONTINUE_FLAG_INDEX` with the last result's file index, `SMB2_CONTINUE_FLAG_SINGLE`, or no continuation flag. This helper is the center of the many-file, sorted, and rename stress tests.

The mutation tests deliberately alter server state mid-enumeration. `test_fixed()` deletes all files after beginning a search on another handle. `test_modify_search()` creates additional files, changes DOS attributes, unlinks one file, sets another file delete-on-close, restarts enumeration, and checks the final directory contents. `test_1k_files_rename()` turns this into a repeated stress pattern, validating that every enumeration still maps cleanly to the current expected `fname_list`.

## State And Persistence Behavior
The remote persistent state is confined to the `smb2_dir` test directory and test files under it. Each test starts with `smb2_deltree(tree, DNAME)` or equivalent cleanup and ends by closing handles and deleting the tree. Directory handles are intentionally closed and reopened in `populate_tree()` and `test_large_files()` to make sure later enumeration sees the freshly created entries through smbd's directory stream.

Client-side state is talloc-scoped. `levels[]` is file-static and stores per-level search data for `test_one_file()`, so it is reused across invocations but refreshed before comparison. `compare_data_level` and `level_sort` are file-static globals used by the qsort comparator; this design is fine for serial torture execution but not reentrant. `struct multiple_result` owns a growing `union smb_search_data` array under its `tctx`.

The tests distinguish hard protocol requirements from optional server behavior. Sorted directory order and honoring file-index resume are reported as informational when unsupported, not as failures. Windows NTFS behavior around zero file indices is explicitly treated as a skip for the file-index test.

## Dependencies
The file depends on SMB2 create, close, unlink, set attribute, setinfo, getinfo, directory find, tree cleanup, and test-directory helpers. It also depends on Samba string and time utilities such as `generate_unique_strs()`, `generate_random_str()`, `nt_time_string()`, `timespec_elapsed2()`, `strcasecmp_m()`, and `strcmp_safe()`.

The search-level machinery depends on the shape of `union smb_search_data` and the `RAW_SEARCH_DATA_*` enum remaining aligned with the corresponding `SMB2_FIND_*` levels. The offset-based `extract_name()` helper is sensitive to structure layout changes. The rename stress test depends on `RAW_SFILEINFO_RENAME_INFORMATION` via `smb2_setinfo_file()`.

## Integration Points
`torture_smb2_dir_init()` is added into the top-level SMB2 torture suite from `smb2.c`, exposing these tests as `smb2.dir.*`. The exported helper `torture_single_file_search()` is non-static and can be reused by other torture code that needs one-file SMB2 search validation.

The tests exercise server directory enumeration paths, filename normalization/case behavior, DOS attribute mapping, file ID and alternate-name reporting, allocation and timestamp propagation, and handling of directory stream invalidation after mutation. Results are useful for Samba server changes in smbd directory listing, VFS backends, durable directory handles, and metadata mapping.

## Risks
The file contains two suspicious missing-file validation loops: both `test_find()` and `test_large_files()` iterate `i` but check `files[j].found` and report `files[j].name`. Because `j` is reused from earlier inner loops, this can mask or misreport missing entries. This is a test-code risk rather than a production-server risk.

`extract_name()` uses `memcpy()` from a computed offset into a union to recover a `char *`; this is compact but fragile if the union layout changes or if a level is paired with the wrong `data_level`. `multiple_smb2_search()` returns failure when a response has zero entries or the accumulated result is empty, which can make unusual but legal empty responses hard to distinguish from protocol errors. The global qsort state means the comparator is not thread-safe.

Performance-oriented tests create 700, 1,000, or 2,000 files and can be slow on high-latency shares or backends with expensive directory operations. Cleanup is best-effort; a process abort can leave `smb2_dir` behind. Some tests assume create-time stability and attribute semantics that may vary across filesystem backends.

## Test Signals
Strong pass signals are exact file counts including `.` and `..` where expected, successful comparison of every find information class against SMB2 GETINFO, stable behavior after deletion or attribute mutation, and no missing/extra names in large enumerations. Informational signals include comments about unsorted directory listings and skipped file-index resume when the server returns zero file indices.

Regression-sensitive outputs include `STATUS_NO_MORE_FILES` termination, `NT_STATUS_OK` on all create/find/getinfo/setinfo operations, correct `FILE_ATTRIBUTE_HIDDEN`, `FILE_ATTRIBUTE_SYSTEM`, `FILE_ATTRIBUTE_ARCHIVE`, and `FILE_ATTRIBUTE_NORMAL` visibility in `test_modify_search()`, and successful repeated rename/enumerate loops in `1kfiles_rename`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/dosmode.c -->
# sources/user-network-fs/samba/source4/torture/smb2/dosmode.c

## Purpose
`dosmode.c` contains two top-level SMB2 torture tests for DOS attribute behavior around hidden files. It verifies that explicit `FILE_ATTRIBUTE_HIDDEN`, Samba `hide files` behavior, and `hide dot files` behavior are visible through SMB2 metadata and directory enumeration. It also checks an overwrite edge case: overwriting a file that was made hidden explicitly must fail with an attribute mismatch, while overwriting files hidden by configured name rules should succeed.

## Important APIs, Types, And Functions
The file uses SMB2 connection, create, setinfo, getinfo, find, close, and deltree helpers. There are no local structs or suite initializer in this file; both functions are registered as simple top-level SMB2 tests by `smb2.c`.

Important functions are:

- `torture_smb2_dosmode()`: creates a test directory, creates `file`, explicitly sets its basic attributes to `FILE_ATTRIBUTE_HIDDEN`, validates the hidden bit by `RAW_FILEINFO_BASIC_INFORMATION`, checks that `NTCREATEX_DISP_OVERWRITE_IF` with normal attributes fails for that explicit hidden file, then creates and overwrites `hidefile` and `.dotfile` while expecting the hidden bit to be set by server configuration.
- `torture_smb2_async_dosmode()`: creates a hidden `file`, closes it, then uses `SMB2_FIND_BOTH_DIRECTORY_INFO` against the containing directory to verify the hidden bit appears in directory enumeration results. Despite the name, the code uses the normal `smb2_find_level()` wrapper rather than an explicit async request API.

Key request/response unions are `struct smb2_create`, `union smb_setfileinfo`, `union smb_fileinfo`, `struct smb2_find`, and `union smb_search_data`.

## Control Flow
Both tests establish their own SMB2 connection with `torture_smb2_connection()`, delete `torture_dosmode`, create it with `torture_smb2_testdir()`, and clean up in a shared `done:` path.

`torture_smb2_dosmode()` first creates `torture_dosmode\file` with normal attributes. It sends `RAW_SFILEINFO_BASIC_INFORMATION` by handle to set `FILE_ATTRIBUTE_HIDDEN`, then queries `RAW_FILEINFO_BASIC_INFORMATION` and asserts the bit is present. After closing, it attempts to reopen the same file with `NTCREATEX_DISP_OVERWRITE_IF` and normal attributes and expects `NT_STATUS_ACCESS_DENIED`. It then creates `torture_dosmode\hidefile`, expects the hidden bit to be present immediately, closes it, and verifies overwrite-if succeeds. The same create/query/overwrite sequence is repeated for `torture_dosmode\.dotfile`.

`torture_smb2_async_dosmode()` creates `file`, sets `FILE_ATTRIBUTE_HIDDEN`, closes the file handle, then issues a find request with pattern `file`, `SMB2_CONTINUE_FLAG_RESTART`, 0x1000 max response size, and `SMB2_FIND_BOTH_DIRECTORY_INFO`. It closes the directory handle before asserting the returned directory-info attributes include `FILE_ATTRIBUTE_HIDDEN`.

## State And Persistence Behavior
The remote state is the `torture_dosmode` directory and three files under it. Both tests delete the tree before and after execution. The tests intentionally persist a hidden attribute long enough to validate it by both handle-based query and directory enumeration.

The behavior under test depends on server-side persisted DOS attribute state and on configured name-based hiding rules. A file explicitly changed to hidden is expected to behave differently from files hidden by `hide files` or `hide dot files`: explicit hidden state causes the overwrite-if with normal attributes to fail, while rule-hidden files can be overwritten successfully.

Client-side state is minimal and stack-based. Handles are initialized to zeroed SMB2 handles and closed conditionally if still non-empty.

## Dependencies
The tests depend on Samba SMB2 client calls and torture assertions. Semantically, they depend on the target share being configured so that `hidefile` matches a `hide files` rule and `.dotfile` is hidden by `hide dot files`; otherwise the hidden-bit assertions for those names will fail. They also depend on DOS attribute storage/mapping in the server and VFS backend.

The file includes `system/time.h` but does not use time APIs directly. The actual integration comes through `torture/smb2/proto.h`, where these functions are declared and registered by the larger SMB2 suite.

## Integration Points
`smb2.c` registers these as `smb2.dosmode` and `smb2.async_dosmode`. They complement broader SMB2 create, setinfo, getinfo, and directory tests by focusing on the DOS mode rules that are often controlled by Samba share parameters rather than raw protocol fields alone.

These tests touch server code paths for create disposition handling, basic-info set/query, hidden attribute synthesis during create and find, and name-rule based DOS attribute evaluation. They are useful when changing VFS modules, DOS attribute backends, `hide files`, `hide dot files`, or SMB2 create overwrite checks.

## Risks
The tests are configuration-sensitive. If the test environment does not configure `hide files` to match `hidefile` and does not enable dotfile hiding, `torture_smb2_dosmode()` will fail even if generic SMB2 attribute handling works. The source comments assume those settings are present but the file itself does not skip when they are absent.

`torture_smb2_async_dosmode()` does not check `count` before dereferencing `d->both_directory_info`; it relies on `smb2_find_level()` returning at least one matching result for the created file. A server returning success with zero entries would cause invalid result handling. Cleanup calls `smb2_deltree(tree, dname)` even if connection setup partially failed, but the function returns early when connection setup fails.

The overwrite status expectation is specific: explicit hidden overwrite with normal attributes must return `NT_STATUS_ACCESS_DENIED`. Server behavior that returns a different attribute-mismatch status would be reported as a failure.

## Test Signals
Pass signals are successful basic-info set/query for `FILE_ATTRIBUTE_HIDDEN`, `NT_STATUS_ACCESS_DENIED` on overwrite-if of the explicitly hidden file, successful overwrite-if of `hidefile` and `.dotfile`, and a directory enumeration entry whose `both_directory_info.attrib` includes `FILE_ATTRIBUTE_HIDDEN`.

Useful failure signals distinguish attribute synthesis from overwrite policy: missing hidden bit on `hidefile` or `.dotfile` points to share configuration or name-rule mapping, while failure on explicit set/query points to DOS attribute persistence. A failure in `async_dosmode` but not `dosmode` points specifically to FIND result attribute propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/dosmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/durable_open.c -->
# sources/user-network-fs/samba/source4/torture/smb2/durable_open.c

## Purpose
`durable_open.c` implements the SMB2 durable-handle torture suites. It verifies when durable opens are granted, how durable handles reconnect after TCP disconnects, session reconnects, tree disconnects, logoff, alternate users, conflicting opens, oplock or lease breaks, byte-range locks, delete-on-close, file position, allocation size, read-only attributes, and stat-only opens. It covers both oplock-backed durable handles and lease-backed durable handles, including lease v2 reconnect request/response paths.

The file is test code, but it encodes important protocol expectations: durable state is only granted for a batch oplock or handle lease, reconnect is driven by the durable handle blob plus lease identity where applicable, many create fields are ignored during reconnect, and some reconnect failures must preserve the original durable state.

## Important APIs, Types, And Functions
The file uses SMB2 create, close, write, lock, setinfo/getinfo, logoff, tree disconnect, tree connect, session setup, and connection extension helpers. It also uses `smb2cli_conn_server_capabilities()` for lease support detection, `smb2cli_session_current_id()` for previous-session reconnects, `smb2_connect()` for reconnecting as another user, and loadparm/resolve/credential helpers for alternate-user tests.

Assertion and response-checking macros are central:

- `CHECK_STATUS()` asserts exact NTSTATUS values.
- `CHECK_CREATED()` validates create action, zero size, file attributes, and reserved fields.
- `CHECK_CREATED_SIZE()` also validates allocation size and file size.
- `CHECK_VAL()`, `CHECK_NOT_VAL()`, and `CHECK_NOT_NULL()` keep repeated checks compact.

Important data tables are:

- `durable_open_vs_oplock_table`, covering no oplock, shared, exclusive, and batch oplocks against all share-mode combinations. Only batch oplocks are expected to grant durable state.
- `durable_open_vs_lease_table`, covering no lease, read, read/write, read/handle, and read/handle/write leases against all share-mode combinations. Only handle leases (`RH` and `RHW`) are expected to grant durable state.

Representative test groups are:

- Open grant matrix: `test_durable_open_open_oplock()`, `test_durable_open_open_lease()`.
- Basic reconnect behavior: `reopen1`, `reopen1a`, `reopen1a_lease`, `reopen2`, `reopen2_lease`, `reopen2_lease_v2`, `reopen2a`, `reopen3`, `reopen4`, `reopen5`, and `reopen6`.
- Persistent handle state: `delete_on_close1`, `delete_on_close2`, `file_position`, `alloc_size`, and `read_only`.
- Conflict and locking cases: `oplock`, `lease`, `lock_oplock`, `lock_lease`, `lock_noW_lease`, `open2_lease`, and `open2_oplock`.
- Other coverage: `oplock_disconnect` leaves a disconnected durable handle behind for disconnect-specific testing, and `stat_open` verifies a read-attribute durable open with a lease.

Suite registration is split between `torture_smb2_durable_open_init()` for the normal `durable-open` suite and `torture_smb2_durable_open_disconnect_init()` for the one-test `durable-open-disconnect` suite.

## Control Flow
Most tests allocate a talloc context, generate a randomized filename to avoid stale state, remove any previous file of that name, create a file with either `smb2_oplock_create*()` or `smb2_lease_create*()`, set `io.in.durable_open = true`, validate the create response, then intentionally destroy or replace SMB2 connection objects to simulate disconnect scenarios.

The open-grant matrix tests are table-driven. Each row builds a create request with a specific oplock or lease state and share mode, requests durable open, and checks `io.out.durable_open` against the expected boolean while also verifying the granted oplock/lease state.

The reconnect tests vary the way the original connection is interrupted:

- `reopen1` attempts a durable reconnect on the same live connection while the original handle is still active and expects `NT_STATUS_OBJECT_NAME_NOT_FOUND`.
- `reopen1a` reconnects a session on another TCP connection with previous session ID; the old session is deleted and durable reconnect succeeds on the new session. For oplocks, a different client GUID is allowed.
- `reopen1a_lease` performs the same pattern for leases but requires the original client GUID for successful durable reconnect; a different GUID fails.
- `reopen2` frees the tree to simulate TCP disconnect, reconnects normally, and reclaims the durable handle. It then demonstrates that filename and most create fields are ignored for oplock durable v1 reconnect and that an extra durable-open request context is ignored.
- `reopen2_lease` and `reopen2_lease_v2` require the lease request and lease key for reconnect; missing lease context, wrong lease key, or wrong filename fails, while the requested lease state is irrelevant.
- `reopen2a` reconnects using the previous session ID and then reclaims the durable handle.
- `reopen3` tree-disconnects and reconnects a new tree on the same session, expecting durable reconnect failure.
- `reopen4` logs off, creates a new session and tree on the same transport, and expects durable reconnect success.
- `reopen5` verifies that a failed durable reconnect from another process does not clobber a later valid reconnect of the original durable open state.
- `reopen6` reconnects as a different user and expects `NT_STATUS_ACCESS_DENIED`, then reconnects with the original credentials and succeeds.

State-preservation tests create a durable handle, mutate handle or file state, disconnect, reconnect, and verify state after durable reopen. `file_position` sets `RAW_SFILEINFO_POSITION_INFORMATION` to `0x1000` and checks it survives. `alloc_size` checks initial allocation, one-byte write, and expansion beyond the allocation step. `read_only` creates a read-only durable file, writes through the existing handle, reconnects, confirms read-only attributes and size, then restores attributes for cleanup.

Conflict tests use two tree connections. They disconnect the original durable owner, allow a second connection to open the file or take a new oplock/lease, then verify the original durable owner can no longer reclaim the stale handle. Lock tests take byte-range locks before disconnect and verify reconnect either preserves unlockability (`lock_oplock`, `lock_lease`) or fails when the lease lacks write caching (`lock_noW_lease`).

## State And Persistence Behavior
Durable open state is remote server state. The tests intentionally free client-side `struct smb2_tree` objects with `TALLOC_FREE()` or `talloc_free()` to simulate lost TCP transports while leaving durable server handles eligible for reconnect. The durable handle value is kept in a local `struct smb2_handle` and reused as `io.in.durable_handle` or `io.in.durable_handle_v2`.

Lease-backed durable reconnects persist identity through both the durable handle and lease key. The tests check `lease_key.data[0]`, `lease_key.data[1]`, lease state, lease flags, and lease duration after reconnect. Lease v2 tests use `lease_response_v2` and `lease_request_v2` but retain the same behavioral expectations.

Several tests validate persistence of associated handle/file state: delete-on-close should delete disconnected handles in one path but survive until close after successful reconnect in another; current file position survives durable reconnect; byte-range locks remain attached to the durable handle; allocation and size are preserved across reconnects; read-only attributes remain visible while an existing handle can still write.

Client object ownership is intentionally unusual. Many tests consume the passed `tree` by freeing it and replacing it with a new connection. Cleanup paths must therefore check whether `tree`, `tree1`, `tree2`, or `tree3` is non-NULL before closing handles and unlinking. Random filenames reduce stale-state collision risk, and most tests unlink before and after execution.

## Dependencies
The file depends on SMB2 server support for durable handles, batch oplocks, leases, session reconnect, tree disconnect, logoff, byte-range locks, delete-on-close, allocation-size reporting, DOS attributes, and reconnect semantics. Lease tests skip when `SMB2_CAP_LEASING` is absent. `reopen6` skips when secondary user credentials are anonymous or unavailable.

Important helper dependencies include `smb2_oplock_create()`, `smb2_oplock_create_share()`, `smb2_lease_create()`, `smb2_lease_create_share()`, `smb2_lease_v2_create()`, `smb2_util_share_access()`, `smb2_util_oplock_level()`, `smb2_util_lease_state()`, `torture_smb2_connection()`, `torture_smb2_connection_ext()`, `torture_smb2_tree_connect()`, and `torture_smb2_session_setup()`.

The alternate-user test depends on `torture_setting_string()` for `host` and `share`, `torture_user2_credentials()`, `smb2_connect()`, resolve context, socket options, and GENSEC settings.

## Integration Points
`torture_smb2_durable_open_init()` registers the suite as `smb2.durable-open` via the top-level SMB2 suite. It includes one-connection tests and two-connection tests using `torture_suite_add_1smb2_test()` and `torture_suite_add_2smb2_test()`. `torture_smb2_durable_open_disconnect_init()` registers `smb2.durable-open-disconnect.open-oplock-disconnect`, a targeted disconnect case.

These tests integrate with server code paths for SMB2 create contexts (`DURABLE_HANDLE_REQUEST`, reconnect contexts, lease contexts), session lifetime, tree lifetime, share-mode and oplock/lease arbitration, persistent open records, VFS open state, byte-range lock state, and file metadata persistence. They are high-value regression tests for changes in SMB2 handle databases and clustered or persistent-handle storage.

## Risks
The tests are precise about Windows/Samba-compatible status codes. Small server changes that preserve broad behavior but return a different error such as `INVALID_PARAMETER` versus `OBJECT_NAME_NOT_FOUND` will fail these tests. That strictness is useful for protocol compatibility but can make backend-specific behavior visible.

Some cleanup paths are fragile because the tests deliberately free and replace connection objects. For example, there are paths that may attempt to close or unlink through a tree pointer selected after earlier frees, and several tests assign `h = io.out.file.handle` after an expected failing create even though the handle may be empty. The common pattern works under expected server behavior but should be reviewed carefully if adding new early exits.

`test_durable_open_open2_oplock()` appears to call `CHECK_CREATED(&io1, CREATED, FILE_ATTRIBUTE_ARCHIVE)` after creating the second open with `io2`; this looks like a copy/paste mistake in the assertion target. `reopen5` includes an explicit `sleep(3)` to wait for record/destructor behavior, making it timing-sensitive and slow. Lease tests use `random()` lease keys without explicitly seeding in this file, relying on surrounding process behavior.

Durable-handle tests can leave server-side durable state behind if the process aborts at the wrong point. Random filenames reduce collision risk but do not replace cleanup. The suite also assumes support for batch oplocks or leases depending on the test; lease tests skip on missing capability, but oplock behavior differences across servers may still produce failures.

## Test Signals
Core pass signals include `io.out.durable_open` being true only for batch oplocks or handle leases, exact create actions (`CREATED` versus `EXISTED`), correct file attributes and sizes after reconnect, correct lease key/state echoes, and exact reconnect failure statuses for same-session, wrong-GUID, wrong-lease-key, wrong-user, tree-disconnect, and conflicting-open cases.

Important persistence signals are successful durable reopen after TCP disconnect, `NT_STATUS_FILE_CLOSED` when querying an old handle before reconnect, preserved file position `0x1000`, successful unlock of a byte-range lock after reconnect, delete-on-close behavior matching whether the handle was reconnected, allocation-size growth after writes, and read-only attributes preserved after reconnect.

Operational signals include skips for missing leasing capability or missing user2 credentials, warnings when reconnect setup fails, and clean removal of randomized test files. The disconnect-specific suite intentionally leaves the server to handle a disconnected durable open without a normal reconnect path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/durable_open.c -->
