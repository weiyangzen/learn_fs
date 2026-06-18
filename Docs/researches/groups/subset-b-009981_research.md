# subset-b-009981 Research

Grouped research for Samba raw SMB torture sources. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/qfileinfo.c -->
# sources/user-network-fs/samba/source4/torture/raw/qfileinfo.c

## Purpose
This file implements raw SMB file-information torture tests. It exercises a broad matrix of `RAW_FILEINFO_*` and path-info levels against both a normal disk file and an IPC named pipe, then checks that equivalent protocol information levels agree on timestamps, size, allocation, attributes, names, streams, EAs, file IDs, position, and device-specific behavior. The exported entry points are `torture_raw_qfileinfo()` and `torture_raw_qfileinfo_pipe()`.

## Important APIs, Types, And Functions
The central state is the static `levels[]` table. Each row names an SMB file-info level, records whether it is handle-only or path-only, declares required capabilities such as `CAP_UNIX`, stores expected IPC failure behavior, and keeps both handle (`fnum_finfo`) and path (`fname_finfo`) query results.

`torture_raw_qfileinfo_internals()` drives the suite. It calls `smb_raw_fileinfo()` for handle-capable levels and `smb_raw_pathinfo()` for path-capable levels, then uses helper lookups `fnum_find()` and `fname_find()` plus comparison macros to validate relationships across levels. `dos_nt_time_cmp()` tolerates DOS two-second timestamp resolution. `torture_raw_qfileinfo()` creates a complex disk file with `create_complex_file()`, while `torture_raw_qfileinfo_pipe()` opens `\lsass` on IPC using `RAW_OPEN_NTCREATEX`.

## Control Flow
The internal test first probes every level and records NTSTATUS results. It then filters by negotiated capabilities and IPC/non-IPC mode to distinguish unsupported levels from real failures. After that broad liveness check, it performs consistency checks: aliases such as `BASIC_INFO` versus `BASIC_INFORMATION`, `STANDARD_INFO` versus `STANDARD_INFORMATION`, and `ALL_INFO` versus `ALL_INFORMATION`; NT versus DOS timestamp encodings; size and allocation values; attributes; file names and alternate names; stream metadata; EA size accounting; and handle/path agreement for file ID, position, mode, alignment, attributes, and reparse tags.

If alternate-name information is available, the test closes and reopens the file by its short name to verify the returned name is usable. If stream information is missing or empty, stream checks are skipped rather than failing the whole suite. The public disk-file test closes and unlinks the file; the pipe test only closes the pipe handle.

## State And Persistence Behavior
The disk-file case creates `\torture_qfileinfo.txt` and removes it at the end. The IPC case opens a named pipe and does not create filesystem state. The `levels[]` array is static and mutable: every run overwrites each row's status and result unions. That is acceptable inside the single test flow but means the table is not reentrant or thread-local. Handle position is explicitly checked but most queries are metadata-only.

## Dependencies And Integration Points
This file depends on Samba's raw SMB client API (`smb_raw_fileinfo`, `smb_raw_pathinfo`, `smb_raw_open`), torture helpers (`create_complex_file`, `torture_assert_ntstatus_ok`, `torture_comment`), negotiated transport capabilities, talloc allocation, and wire string validation through `wire_bad_flags()`. It is registered by `raw.c` as `qfileinfo` and `qfileinfo.ipc`.

## Risks And Edge Cases
The static table retains results between probes, so future parallelization or nested invocation would need isolation. Some compatibility behavior is intentionally loose: unsupported or unimplemented levels may warn and continue, and stream checks are skipped when stream metadata is absent. The IPC branch has distinct expected statuses (`INVALID_DEVICE_REQUEST`, `ACCESS_DENIED`, `INVALID_PARAMETER`, `delete_pending` expectations), so changes in named-pipe semantics can fail this test even when normal files pass. Timestamp checks depend on resolution conversions, and alternate-name reopening can mutate the handle under test.

## Test Signals
Strong pass signals are all capability-advertised levels returning expected statuses and all alias/value comparisons matching. Failures print the level name, field names, actual and expected values, source line, and NTSTATUS. More than 35 broken levels triggers an immediate torture failure to avoid cascading noise.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/qfileinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/qfsinfo.c -->
# sources/user-network-fs/samba/source4/torture/raw/qfsinfo.c

## Purpose
This file implements `torture_raw_qfsinfo()`, a raw SMB filesystem-information suite. It probes many `RAW_QFS_*` levels and verifies that equivalent levels report consistent volume, allocation, device, attribute, quota, full-size, and string-encoding data.

## Important APIs, Types, And Functions
The static `levels[]` table maps human-readable names to `enum smb_fsinfo_level` values and stores capability masks, NTSTATUS results, and `union smb_fsinfo` output. `find()` returns a successful level by name. Local macros compare scalar, approximate scalar, string, structure, and unknown fields. The test uses `smb_raw_fsinfo()` to fetch all levels and `wire_bad_flags()` to validate returned string termination/encoding.

## Control Flow
`torture_raw_qfsinfo()` iterates through every table entry, sets `fsinfo.generic.level`, and calls `smb_raw_fsinfo()`. It then checks that all capability-advertised levels succeed, with `CAP_UNIX` gating the Unix level. After the status pass, it validates aliases such as `SIZE_INFO`/`SIZE_INFORMATION`, `DEVICE_INFO`/`DEVICE_INFORMATION`, `VOLUME_INFO`/`VOLUME_INFORMATION`, and `ATTRIBUTE_INFO`/`ATTRIBUTE_INFORMATION`.

The test compares disk size and free-space values between legacy `DSKATTR` and `ALLOCATION`, accepts approximately equal available units where live filesystems can change, checks `VOLUME` against `VOLUME_INFO`, checks `SIZE_INFO` against `FULL_SIZE_INFORMATION`, verifies quota/object-id unknown fields are zero when present, and finally checks correct string wire termination for volume and filesystem type fields.

## State And Persistence Behavior
The test creates no files and mutates no server state. It reads live filesystem state, so free-space-related values can change while the test is running. Like `qfileinfo.c`, it stores probe results in a static mutable `levels[]` table, making the implementation simple but not reentrant.

## Dependencies And Integration Points
Dependencies include `libcli` raw SMB APIs, the torture framework, NTSTATUS helpers, math functions for approximate size comparisons, negotiated capability flags, and Samba string wire helpers. The suite is registered by `raw.c` as the `qfsinfo` one-SMB test.

## Risks And Edge Cases
Some comparisons assume a mostly quiescent filesystem; concurrent allocation can affect available-space comparisons. The failure guard appears inverted: after counting failed levels it asserts `count > 13` with message "too many level failures", which is unusual and may be historical behavior worth reviewing before modifying. Optional or obsolete levels such as object-id information are guarded, and Unix info depends on negotiated capabilities.

## Test Signals
Success means all advertised query levels work and alias levels agree. Diagnostics identify failed levels, inconsistent disk sizes/free space, unexpected nonzero unknown fields, and string termination errors. The test also prints volume name, filesystem type, total disk, and free disk values as useful context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/qfsinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/raw.c -->
# sources/user-network-fs/samba/source4/torture/raw/raw.c

## Purpose
This file is the registration hub for the `raw` smbtorture suite. It does not implement protocol checks itself; instead, `torture_raw_init()` creates the suite, attaches all raw SMB subtests and nested suites, sets a description, and registers the suite with the torture framework.

## Important APIs, Types, And Functions
The only function is `torture_raw_init(TALLOC_CTX *ctx)`. It uses `torture_suite_create()`, `torture_suite_add_simple_test()`, `torture_suite_add_1smb_test()`, `torture_suite_add_2smb_test()` indirectly through nested suites, `torture_suite_add_suite()`, and `torture_register_suite()`. It references many externally implemented entry points from `torture/raw/proto.h`.

## Control Flow
Initialization creates a suite named `raw`, adds benchmarks, single-connection tests, grouped nested suites, Samba3 compatibility tests, and scan tests, then assigns `"Tests for the raw SMB interface"` as the description. It returns `NT_STATUS_OK` after successful registration. There is no conditional registration logic in this file.

## State And Persistence Behavior
The file only mutates in-memory torture registration state under the provided talloc context. It creates no SMB connections, files, or persistent artifacts directly. Runtime state and cleanup belong to the individual tests it registers.

## Dependencies And Integration Points
This file is the integration point that exposes raw SMB tests to smbtorture. It depends on `torture/smbtorture.h`, `torture/util.h`, `libcli/raw/libcliraw.h`, and generated raw torture prototypes. The order and names here define how users invoke tests such as `RAW-QFSINFO`, `RAW-READ`, `RAW-RENAME`, `RAW-SAMBA3HIDE`, and others through the test runner.

## Risks And Edge Cases
Because this is a registry, stale prototypes or renamed tests cause build failures or missing runtime coverage. Adding a test in its implementation file is not enough unless it is registered here or inside a nested suite already registered here. The explicit test names are user-facing and may be consumed by automation.

## Test Signals
There are no direct protocol assertions. The signal is structural: the raw suite appears in smbtorture with all expected children, and `torture_raw_init()` returns `NT_STATUS_OK`. Missing registrations show up as absent test names rather than failed SMB operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/read.c -->
# sources/user-network-fs/samba/source4/torture/raw/read.c

## Purpose
This file implements the raw SMB read test suite. It validates legacy `SMBread`, `SMBlockread`, `SMBreadX`, `SMBreadbraw`, and READX execute-permission behavior across empty files, EOF, invalid handles, large reads, locked ranges, large offsets, alignment, and access-mask combinations.

## Important APIs, Types, And Functions
The exported suite factory is `torture_raw_read()`, which registers `test_read`, `test_readx`, `test_lockread`, `test_readbraw`, and `test_read_for_execute`. Shared helpers `setup_buffer()` and `check_buffer()` create deterministic pseudo-random data based on a seed. The test code uses `union smb_read`, `union smb_open`, `union smb_write`, raw calls `smb_raw_read()`, `smb_raw_read_send()`, `smb_raw_open()`, `smb_raw_write()`, and classic helpers such as `smbcli_open`, `smbcli_write`, `smbcli_lock`, and `smbcli_lock64`.

## Control Flow
Each read variant creates `\testread\test.txt`, runs protocol-specific reads, validates status and byte counts, then tears down the directory. `test_read()` covers `RAW_READ_READ`, including empty/zero reads, invalid FID, short reads, maximum offsets, large count handling, and write-lock conflict. `test_lockread()` first checks negotiated `lockread_supported`, then validates the implicit locking behavior of LOCKREAD and expected `LOCK_NOT_GRANTED`/`FILE_LOCK_CONFLICT` outcomes.

`test_readx()` is the broadest path: it validates empty and zero reads, invalid handles, reserved response words, Unicode alignment via `CHECK_READX_ALIGN`, short reads, `mincnt`/`maxcnt` combinations, page-sized and 64 KiB reads, `CAP_LARGE_READX`, locked regions, and large-file offsets when `CAP_LARGE_FILES` is set. `test_readbraw()` checks raw-read behavior, including its unusual success-with-zero-data behavior for invalid handles and locked regions. `test_read_for_execute()` verifies `FLAGS2_READ_PERMIT_EXECUTE`: execute-only opens can read only when `read_for_execute` is true, while read-data opens work with or without the flag.

## State And Persistence Behavior
All tests use the transient `\testread` directory and remove it with `smbcli_deltree()`. They create and close SMB file handles, take byte-range locks, manipulate `cli->session->pid` to simulate a different locker, and in one path call `smb_raw_exit()` before cleanup. Data persistence is temporary but deliberately writes up to 90,000 bytes to exercise large transfer paths.

## Dependencies And Integration Points
The file depends on negotiated capability flags (`CAP_LARGE_FILES`, `CAP_LARGE_READX`), transport feature booleans (`lockread_supported`, `readbraw_supported`), raw SMB read/open/write APIs, torture settings such as `read_support`, and the shared raw torture registration in `raw.c`. It also depends on low-level SMB request access to inspect READX response words.

## Risks And Edge Cases
The deterministic buffer helper uses global `srandom()`/`random()`, so it is not thread-local. Large-read expectations intentionally allow Samba's large-read extension in some cases. Lock behavior is sensitive to server byte-range lock semantics and PID handling. READBRAW has legacy behavior where some errors are represented as OK with zero bytes, so refactoring must preserve protocol-specific expectations rather than normalizing all read paths.

## Test Signals
Pass signals include exact NTSTATUS values, exact read byte counts, byte-for-byte buffer validation, zeroed READX reserved fields, aligned READX data offsets when Unicode is negotiated, and correct access-denied behavior for execute-only reads without `read_for_execute`. Failures print assertion context, expected status/value, buffer offsets, or protocol-specific diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/rename.c -->
# sources/user-network-fs/samba/source4/torture/raw/rename.c

## Purpose
This file implements raw SMB rename and hardlink torture tests. It covers classic `SMBmv`, `SMBntrename`, hardlink creation, copy-style NT rename, case-only rename behavior, invalid flags, attribute filtering, and directory rename interactions with open children, open directory handles, long names, and directory streams.

## Important APIs, Types, And Functions
The suite factory `torture_raw_rename()` registers local tests `test_mv`, `test_ntrename`, `test_nthardlink`, `test_osxrename`, and `test_dir_rename`, plus externally implemented `test_trans2rename()` and `test_nttransrename()` from `oplock.c`. Core types are `union smb_rename`, `union smb_open`, and `union smb_fileinfo`. The tests use `smb_raw_rename()`, `smb_raw_open()`, `smb_raw_pathinfo()`, `smbcli_close()`, `smbcli_unlink()`, `smbcli_deltree()`, `create_complex_file()`, and `torture_set_file_attribute()`.

## Control Flow
`test_mv()` validates simple SMBmv behavior: rename fails while the source is open without delete sharing, succeeds with `SHARE_ACCESS_DELETE`, supports case-only renames, works after session exit, allows self-rename, and reports not-found for absent sources. `test_osxrename()` focuses on case-changing rename compatibility by probing/deleting an existing uppercase spelling before renaming.

`test_ntrename()` exercises `RAW_RENAME_NTRENAME`: sharing violation while open, wildcard syntax rejection, hidden-attribute filtering, copy flag behavior, attribute independence between source and copy, invalid flag handling with Win7-specific expectations, unknown cluster-size tolerance, move-cluster rejection, and a warning loop over many unsupported flags. `test_nthardlink()` creates a hardlink with `RENAME_FLAG_HARD_LINK` and verifies `nlink` and shared attributes. `test_dir_rename()` checks that a directory containing an open child file cannot be renamed, but a directory can be renamed while a separate directory handle or a stream on the directory is open in the tested access modes.

## State And Persistence Behavior
The suite uses `\testrename` and removes it after each test. It creates files, directories, hardlinks, copies, attributes, and streams, and often calls `smb_raw_exit()` before deleting the tree to flush session state. Some tests intentionally hold handles open across rename attempts to exercise share-mode and delete-sharing semantics.

## Dependencies And Integration Points
Dependencies include raw SMB rename/open/pathinfo APIs, torture helper functions, target detection through `TARGET_IS_WIN7()`, and nested tests implemented in the oplock module. The suite is registered by `raw.c` as the raw rename sub-suite.

## Risks And Edge Cases
Expected statuses differ between Windows versions for invalid NT rename flags. Case-only rename behavior depends on server case-preservation and case-sensitivity settings. Hardlink checks require filesystem support for links. Directory stream behavior and long-name open regressions are compatibility-sensitive. The invalid-flag loop logs warnings rather than failing most cases, so it is diagnostic coverage rather than strict exhaustive validation.

## Test Signals
The test asserts exact NTSTATUS outcomes for each operation and checks returned file metadata such as final filename, link count, and attributes. Cleanup failure can leave `\testrename` artifacts that influence later runs, so the repeated `torture_setup_dir()` and `smbcli_deltree()` calls are important signals for isolation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/samba3hide.c -->
# sources/user-network-fs/samba/source4/torture/raw/samba3hide.c

## Purpose
This file contains Samba3 compatibility tests for permission-based hiding and close-error propagation. `torture_samba3_hide()` verifies `hide unreadable` and `hide unwriteable` share behavior using Unix permissions. `torture_samba3_closeerr()` verifies that close returns an access error when delete-on-close cannot be completed because parent directory permissions were removed.

## Important APIs, Types, And Functions
`init_unixinfo_nochange()` prepares a `RAW_SFILEINFO_UNIX_BASIC` structure with all non-permission fields set to Samba Unix-extension "no change" sentinel values. `smbcli_setup_unix()` negotiates CIFS Unix extensions by querying `RAW_QFS_UNIX_INFO` and setting `RAW_SETFS_UNIX_INFO`. `smbcli_chmod()` applies Unix permissions with `smb_raw_setpathinfo()`.

Visibility and access helpers include `is_visible()` using `smbcli_list()`, `is_readable()`, `is_writeable()`, and `smbcli_file_exists()`. The tests also use `torture_second_tcon()` to connect to special shares named `hideunread` and `hideunwrite`.

## Control Flow
`torture_samba3_hide()` enables Unix extensions, opens secondary tree connections to the hide shares, creates `torture_samba3_hide.txt`, and verifies three permission states. With read/write user permissions, the file must be visible and accessible everywhere. With read-only permissions, it must remain visible on the normal and hide-unreadable shares but disappear from the hide-unwriteable share. With no permissions, it must remain visible only on the normal share and be hidden from both special shares. The test restores permissions and unlinks the file.

`torture_samba3_closeerr()` creates `closeerr.dir\closerr.txt`, opens it with delete sharing, sets delete-on-close, chmods the parent directory to `000`, and then closes the file. It restores directory permissions, deletes the tree, and asserts that close returned `NT_STATUS_ACCESS_DENIED`.

## State And Persistence Behavior
The hide test mutates Unix mode bits on a test file and uses multiple tree connections to shares that must be configured differently. The close-error test mutates parent directory permissions to force cleanup failure, then restores owner read/write/execute before deleting. If interrupted between chmod and restore, server-side permissions may need manual cleanup.

## Dependencies And Integration Points
These tests depend on Samba Unix extensions, POSIX permission semantics, configured shares named `hideunread` and `hideunwrite`, and raw setpathinfo/setfsinfo support. They are registered in `raw.c` as `samba3hide` and `samba3closeerr`.

## Risks And Edge Cases
The tests are environment-sensitive: missing Unix extensions, differently named shares, non-POSIX backing stores, or unexpected ACL overlays can produce failures unrelated to the raw SMB client code. `smbcli_file_exists()` treats any `getatr` failure as nonexistence, which is good enough for this purpose but not a general existence test. Close-error behavior depends on the server surfacing delete-on-close failures at close time.

## Test Signals
Success is a matrix of visibility/read/write outcomes for each permission state plus an exact `NT_STATUS_ACCESS_DENIED` on forced close failure. Failures name the specific visibility or access expectation that was violated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/samba3hide.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/samba3misc.c -->
# sources/user-network-fs/samba/source4/torture/raw/samba3misc.c

## Purpose
This file collects miscellaneous Samba3 regression and compatibility tests for raw SMB1 behavior. It covers FID/tree validation, NTSTATUS versus DOS error mappings, case-insensitive listing, interaction between local POSIX locks and SMB locks, root-directory FID opens, oplock/logoff behavior, and malformed OpenX name blobs.

## Important APIs, Types, And Functions
The first helper group builds OpenX requests from raw name blobs: `smb_raw_openX_name_blob_send()`, `smb_raw_openX_name_blob()`, and `raw_smbcli_openX_name_blob()`. Related wrappers `raw_smbcli_open()`, `raw_smbcli_t2open()`, and `raw_smbcli_ntcreate()` expose old open, trans2 open with EAs, and NTCreateX behavior for error-code tests.

Major exported tests are `torture_samba3_checkfsp`, `torture_samba3_badpath`, `torture_samba3_caseinsensitive`, `torture_samba3_posixtimedlock`, `torture_samba3_rootdirfid`, `torture_samba3_rootdirfid2`, `torture_samba3_oplock_logoff`, and `torture_samba3_check_openX_badname`. Async lock support uses `receive_lock_result()` and a `tevent` timer callback `close_locked_file()`.

## Control Flow
`torture_samba3_checkfsp()` creates a second tree connection and verifies invalid FID handling: a directory FID read on the owning tree returns `INVALID_DEVICE_REQUEST`, while using that FID on another tree returns `INVALID_HANDLE`; the same cross-tree invalid-handle check is applied to a normal file FID.

`torture_samba3_badpath()` opens one connection with NT status support and one with DOS error mapping, then compares `chkpath`, `getatr`, OpenX, T2Open, NTCreateX, SMBmv, and NT rename errors for malformed paths, files used as directories, exclusive-create collisions, and rename collisions. `torture_samba3_caseinsensitive()` confirms that listing `InSeNsItIvE\*` finds the expected entries created under `insensitive`.

`torture_samba3_posixtimedlock()` requires `torture:localdir`; it creates a file over SMB, opens the backing local path, places a POSIX write lock with `fcntl`, verifies an immediate SMB lock fails, then sends a timed SMB lock and closes the local fd via timer so the SMB lock can complete. The rootdir FID tests open files relative to an open root or directory FID. The oplock/logoff test queues a conflicting open, logs off the session, and verifies the transport remains usable via echo. The bad-name test sends a 65535-byte `0xcc` OpenX name blob and expects `OBJECT_NAME_INVALID`.

## State And Persistence Behavior
The tests create and delete small files/directories such as `testdir`, `insensitive`, `posixlock`, `dir1`, and `testfile`. `torture_samba3_badpath()` temporarily changes client configuration options (`nt status support`, `client ntlmv2 auth`) and restores them after opening the required connections. `torture_samba3_posixtimedlock()` touches both SMB server state and a local filesystem path to the same backing file.

## Dependencies And Integration Points
Dependencies include raw SMB open/rename/lock/echo/logoff APIs, `tevent`, local POSIX `open`, `fcntl`, and `close`, Samba loadparm mutation helpers, and configured test settings such as `share`, `samba3`, and `localdir`. The tests are individually registered by `raw.c` under `samba3checkfsp`, `samba3badpath`, `samba3caseinsensitive`, `samba3posixtimedlock`, `samba3rootdirfid`, `samba3rootdirfid2`, `samba3oplocklogoff`, and `samba3badnameblob`.

## Risks And Edge Cases
Several tests are highly environment-dependent. DOS versus NT error mapping requires the client options to take effect as intended. T2Open accepts Samba3-specific `EAS_NOT_SUPPORTED` behavior when configured. POSIX timed lock testing requires the local path to map to the same file the SMB server exports and requires `posix locking = yes`. `raw_smbcli_t2open()` and `raw_smbcli_ntcreate()` assign returned FIDs through the `openx` union member even for other open levels, which works only if the union layout matches expectations.

## Test Signals
Signals are mostly exact NTSTATUS or DOS-status comparisons. Additional signals include count of case-insensitive listing entries, async timed-lock completion with `NT_STATUS_OK`, successful relative opens through root directory FIDs, successful echo after ulogoff during an oplock break, and rejection of an oversized invalid OpenX name blob.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/samba3misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/search.c -->
# sources/user-network-fs/samba/source4/torture/raw/search.c

## Purpose
This file implements the raw SMB search torture suite. It validates old SMB search levels and TRANS2 find levels for single-file metadata consistency, multi-page enumeration continuation, directory modification during search, ordering behavior, concurrent old-style search handles, OS/2-style delete while enumerating, EA-list search semantics, and `max_count` behavior.

## Important APIs, Types, And Functions
The exported helper `torture_single_search()` performs one-entry searches across `RAW_SEARCH_SEARCH`, `RAW_SEARCH_FFIRST`, `RAW_SEARCH_FUNIQUE`, and `RAW_SEARCH_TRANS2`. The static `levels[]` table maps search level/data-level pairs to names, name offsets, resume-key offsets, capabilities, and stored results. `extract_name()` and `extract_resume_key()` use those offsets to interpret `union smb_search_data` generically.

`setup_smb1_posix()` negotiates SMB1 POSIX extensions for `RAW_SEARCH_DATA_UNIX_INFO`. `multiple_search()` performs find-first/find-next loops using continuation by flags, last name, or resume key. `multiple_search_callback()` accumulates results in `struct multiple_result`. Test entry points are registered by `torture_raw_search()`.

## Control Flow
`test_one_file()` creates `torture_search.txt`, queries every search level, checks the not-found status for a missing file, fetches file-info levels, and compares search metadata with pathinfo metadata: attributes, times, sizes, allocation, EA size, alternate names, long names, Unix names, and file IDs.

`test_many_files()` creates 700 files and enumerates them across many data levels and continuation modes, then sorts returned names and verifies the complete expected set. `test_modify_search()` starts an enumeration, mutates the directory by adding, deleting, hiding, system-marking, and delete-on-close-marking files, then checks which names should appear. `test_sorted()` observes whether the server naturally returns alphabetically sorted names but treats unsorted output as informational rather than a failure.

`test_many_dirs()` exercises old-style search IDs across 20 directories and checks search-next behavior including rewind support. `test_os2_delete()` enumerates with EA-size records and deletes files while continuing by resume key until all files are gone. `test_ea_list()` creates files with EAs, queries selected EA names through `RAW_SEARCH_DATA_EA_LIST`, continues the search, sorts results, and validates returned EA names and values. `test_max_count()` confirms that TRANS2 find-first with `max_count = 0` returns one entry and a following find-next with `max_count = 1` returns one more.

## State And Persistence Behavior
Most tests operate under `\testsearch` and remove it with `smbcli_deltree()`. They create hundreds of files/directories, set attributes, set EAs, mark delete-on-close, and hold server-side search handles until close-on-end flags or session exit. The module uses static `levels[]` result storage and a static `compare_data_level` for sorting callbacks.

## Dependencies And Integration Points
The file depends on raw search APIs (`smb_raw_search_first`, `smb_raw_search_next`, `smb_raw_search_close`), raw path/file info, raw setpathinfo, Unix extension negotiation through TRANS2, talloc, type-safe sorting, and torture settings including `resume_key_support`, `rewind_support`, `raw_search_search`, `search_ea_size`, `search_ea_support`, and `ea_support`. It is registered as the nested raw `search` suite.

## Risks And Edge Cases
Search semantics vary across servers, especially resume keys, ordering, old search rewind, POSIX/Unix info, and EA support. Some tests deliberately skip based on settings or warn on unsupported levels. Directory mutation during enumeration is inherently compatibility-sensitive. Generic offset extraction is compact but fragile if `union smb_search_data` layout changes without updating `levels[]`.

## Test Signals
Success signals include exact metadata parity with `ALL_INFO`, complete enumeration of 700 files under multiple continuation mechanisms, correct inclusion/exclusion after directory mutation, expected behavior for old-style search handles, full deletion count during OS/2-style delete, exact EA-list values, and correct `max_count` handling. Failures include level names, expected statuses, field-level mismatches, missing/extra names, and count discrepancies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/search.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/seek.c -->
# sources/user-network-fs/samba/source4/torture/raw/seek.c

## Purpose
This file implements `torture_raw_seek()`, a focused raw SMB seek test. It validates `smb_raw_seek()` behavior for invalid handles, absolute/current/end-relative seeks, 32-bit maximum offsets, overflow behavior, and the relationship between legacy seek offsets and `RAW_FILEINFO_POSITION_INFORMATION`.

## Important APIs, Types, And Functions
`test_seek()` performs all checks using `union smb_seek`, `union smb_fileinfo`, and `union smb_setfileinfo`. It calls `smb_raw_seek()`, `smb_raw_fileinfo()`, `smb_raw_setfileinfo()`, `smb_raw_setpathinfo()`, `smbcli_open()`, `smbcli_write()`, `smbcli_read()`, and cleanup helpers. The public `torture_raw_seek()` simply invokes `test_seek()`.

## Control Flow
The test creates `\testseek\test.txt`, verifies an invalid FID returns `INVALID_HANDLE`, seeks to offset 17 from start, then seeks back three bytes relative to current. It seeks from end and compares the returned offset to `ALL_INFO.size`, seeks to `-1` from start and expects `0xffffffff`, then checks that file-position information remains zero after pure seek calls.

After writing two bytes, it verifies current seek position and file-position information after read/write operations. It opens a second handle, sets `RAW_SFILEINFO_POSITION_INFORMATION` to 25 on that handle, and confirms the first handle remains at position 1. Finally, it attempts path-based position setting and verifies handle positions are unaffected and pathinfo position is zero.

## State And Persistence Behavior
The test creates a transient `\testseek` directory and deletes it at the end. It uses two handles to the same file to prove position state is per handle. It writes and reads small byte buffers and calls `smb_raw_exit()` before deleting the tree.

## Dependencies And Integration Points
Dependencies are the raw seek, fileinfo, and setfileinfo APIs plus standard smbcli open/read/write helpers. `raw.c` registers this as the `seek` one-SMB test.

## Risks And Edge Cases
The test targets legacy 32-bit seek behavior, so sign extension and overflow expectations are subtle. It assumes seek calls do not update `POSITION_INFORMATION`, while actual reads and explicit setfileinfo do. Path-based position information is expected to be a no-op-like query returning zero, which may surprise implementers trying to unify handle and path state.

## Test Signals
Success is a sequence of exact status and offset checks: invalid handle, offsets 17/14/end/0xffffffff/999, position values 0/1/25, and isolation between two handles. Failures print the source line, actual status/value, and expected value.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/seek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/session.c -->
# sources/user-network-fs/samba/source4/torture/raw/session.c

## Purpose
This file implements raw SMB session setup, reauthentication, and Kerberos session-expiry tests. It verifies that reauth can preserve the VUID and open handles, that changing credentials affects access checks on existing/opened objects, and that dynamic reauth handles expired Kerberos sessions as expected.

## Important APIs, Types, And Functions
The suite factory `torture_raw_session()` registers `test_session_reauth1`, `test_session_reauth2`, and `test_session_expire1`. The tests use `struct smb_composite_sesssetup`, `smb_composite_sesssetup()`, command-line credentials from `samba_cmdline_get_creds()`, anonymous credentials from `cli_credentials_init_anon()`, and raw file operations including `smb_raw_open`, `smb_raw_open_send/recv`, `smb_raw_fileinfo`, and `smbcli_nt_delete_on_close()`.

`test_session_reauth2_oplock_timeout()` is an oplock break handler that returns true, allowing the test to proceed through a conflicting open. `test_session_expire1()` additionally uses `smbcli_full_connection()`, loadparm session options, Kerberos credential state, ccache invalidation, and the `CAP_DYNAMIC_REAUTH` capability flag.

## Control Flow
`test_session_reauth1()` creates a random delete-on-close file, writes random data, performs a second session setup using the normal credentials, asserts that the returned VUID equals the original VUID, and reads the still-open file to prove handle continuity.

`test_session_reauth2()` opens a file with a batch oplock, queues a conflicting open, sets delete-on-close on the original handle, reauthenticates the same session as anonymous, closes the first handle, receives the queued open, writes data, and verifies querying the security descriptor owner fails with `ACCESS_DENIED`. It then reauthenticates back to the command-line credentials using the same VUID, repeats the security descriptor query successfully, marks delete-on-close, and closes.

`test_session_expire1()` requires `--use-kerberos=required`, sets a short requested GSSAPI lifetime, opens a new SMB connection, creates a delete-on-close file, and queries access information across sleeps. With `CAP_DYNAMIC_REAUTH`, it expects operations after expiry to return `NT_STATUS_NETWORK_SESSION_EXPIRED`, then reauthenticates and repeats. Without `CAP_DYNAMIC_REAUTH`, it expects reauth to keep subsequent operations OK through shorter sleeps. It restores the GSSAPI lifetime option on exit.

## State And Persistence Behavior
The tests create random-named delete-on-close files and rely on open handles for cleanup. They mutate the authenticated identity associated with an existing SMB session while preserving VUID, manipulate oplock/conflicting-open state, invalidate the Kerberos credential cache, and temporarily set `gensec_gssapi:requested_life_time`. `test_session_expire1()` owns a separate full SMB connection and frees it at cleanup.

## Dependencies And Integration Points
Dependencies include composite session setup, raw SMB file operations, oplock callbacks, command-line credential plumbing, Kerberos configuration, loadparm options, resolver and event contexts, and NT security descriptor query support. The suite integrates through `raw.c` as the nested `session` suite.

## Risks And Edge Cases
These tests are authentication-environment-sensitive. `expire1` is skipped unless Kerberos is required and includes real sleeps, making it slower and time-dependent. Reauth behavior is subtle because VUID preservation, credential replacement, open handles, oplock breaks, and delete-on-close interact. Anonymous access expectations can differ by server policy, but the test specifically requires security descriptor owner query denial after anonymous reauth.

## Test Signals
Success signals include unchanged VUIDs across reauth, readable data through an open handle after reauth, anonymous `ACCESS_DENIED` for owner security descriptor query, restored access after credential reauth, expected `NETWORK_SESSION_EXPIRED` with dynamic reauth, and continued OK operations without dynamic expiry signaling. Failures identify the session setup phase, file operation, VUID comparison, or expiry expectation that failed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/session.c -->
