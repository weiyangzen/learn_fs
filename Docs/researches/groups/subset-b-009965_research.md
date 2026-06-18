# subset-b-009965 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/denytest.c -->
# sources/user-network-fs/samba/source4/torture/basic/denytest.c

## Purpose
This file implements Samba torture coverage for classic SMB deny modes, NT CreateX share/access behavior, and security-descriptor-driven maximum allowed access. It is a behavioral oracle for compatibility-sensitive file-open semantics, including DOS deny modes, NT share modes, file versus directory opens, delete/share-delete rules, SACL-sensitive access bits, and privilege-dependent `SEC_FLAG_MAXIMUM_ALLOWED` outcomes.

## Important APIs, types, and functions
Key local helpers include `denystr()`, `openstr()`, `resultstr()`, `progress_bar()`, `map_bits()`, `bit_string()`, and `predict_share_conflict()`. The main exported torture entry points are `torture_denytest1()`, `torture_denytest2()`, `torture_denytest3()`, `torture_ntdenytest1()`, `torture_ntdenytest2()`, `torture_denydos_sharing()`, `torture_createx_sharemodes_file()`, `torture_createx_sharemodes_dir()`, `torture_createx_access()`, `torture_createx_access_exhaustive()`, and `torture_maximum_allowed()`. The file relies on `union smb_open`, `union smb_read`, `union smb_write`, `union smb_fileinfo`, `union smb_setfileinfo`, `struct createx_data`, and `struct security_descriptor`.

## Control flow
The first half is table-driven. `denytable1` and `denytable2` encode expected read/write results for combinations of `O_RDONLY`, `O_WRONLY`, `O_RDWR` with `DENY_DOS`, `DENY_ALL`, `DENY_WRITE`, `DENY_READ`, `DENY_NONE`, and `DENY_FCB`, split between single-connection and two-connection behavior and `.dat` versus `.exe` names. The deny tests create seed files, iterate the tables, open one or two handles, probe read/write success on the second handle, compare to the table, and clean up.

The NT deny path randomly generates share/access masks, opens via `RAW_OPEN_NTCREATEX`, probes read/write behavior, and compares the server result with `predict_share_conflict()`. CreateX coverage uses `createx_fill_file()` and `createx_fill_dir()` to parameterize opens, then calls `createx_test_file()` or `createx_test_dir()` to exercise read/write/execute or enumerate/create-child/traverse operations. Results are checked against `cxd_known` unless exhaustive output mode is enabled through `CREATEX_DATA`.

## State and persistence
The tests create and remove files such as `\denytest*.dat`, `\denytest*.exe`, `\ntdeny_*.dll`, `\torture_denydos.txt`, `\createx_dir`, and `torture_maximum_allowed`. `data_file_fd` is a process-global descriptor used only by exhaustive CreateX data capture. `torture_numops`, `torture_seed`, `torture_failures`, and settings such as `deny_fcb_support`, `deny_dos_support`, `sacl_support`, `showall`, and `progress` shape execution. Cleanup is mostly explicit through `smbcli_close()`, `smbcli_unlink()`, `smbcli_rmdir()`, and `smbcli_deltree()`.

## Dependencies and integration points
The file integrates with Samba's `libcli` raw SMB layer, security descriptor helpers, torture assertions/results, and the generated `cxd_known.h` baseline. It assumes a connected `smbcli_state` or pair of connections supplied by the torture harness. `torture_check_privilege()` and `sec_privilege_name()` make `torture_maximum_allowed()` dependent on server-side privilege configuration.

## Risks
The dense static deny tables and `cxd_known` baselines are brittle by design: a server compatibility change may require updating expected data rather than code. Exhaustive CreateX access can be very expensive, especially when `CREATEX_DATA` is set. Some tests skip SACL paths based on settings, so coverage can silently narrow. Several cleanup paths continue after failed opens and may attempt closes on invalid fnums, which is normal for this torture style but can obscure the first failure.

## Test signals
Strong signals are mismatches between observed `A_0`, `A_R`, `A_W`, `A_RW`, `A_X` and expected table or predicted share-conflict results, unexpected `NT_STATUS_SHARING_VIOLATION`, `NT_STATUS_ACCESS_DENIED`, `NT_STATUS_PRIVILEGE_NOT_HELD`, or failure to preserve DENY_DOS shared-handle file-position semantics. For CreateX, unknown result tuples printed in initializer syntax indicate new or divergent server behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/denytest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/dir.c -->
# sources/user-network-fs/samba/source4/torture/basic/dir.c

## Purpose
This file provides basic directory listing torture tests. It measures listing behavior over many randomly named files and verifies old SMB list filtering semantics for file and directory attributes.

## Important APIs, types, and functions
The only callback is `list_fn()`, a no-op `smbcli_list*` visitor. Exported tests are `torture_dirtest1()` and `torture_dirtest2()`. They use `smbcli_open()`, `smbcli_close()`, `smbcli_unlink()`, `smbcli_list()`, `smbcli_list_old()`, `smbcli_nt_create_full()`, `smbcli_mkdir()`, `smbcli_deltree()`, `torture_setup_dir()`, and `timeval_current()/timeval_elapsed()`.

## Control flow
`torture_dirtest1()` seeds libc random with zero, creates `torture_numops` files named from hex random values in the share root, runs three wildcard/non-wildcard `smbcli_list()` calls, reports elapsed time, reseeds random, and deletes the same generated names. `torture_dirtest2()` creates `\LISTDIR`, adds `torture_entries` regular files and `torture_entries` directories, then verifies `smbcli_list_old()` counts for all entries, directory-only must-have bits, and archive-file selection.

## State and persistence
The file mutates the test share root and `\LISTDIR`. It depends on deterministic random seeding for cleanup in `dirtest1`. It stores no durable local state.

## Dependencies and integration points
The tests are intended for the basic SMB torture suite and require a connected `smbcli_state`. They depend on Samba's legacy listing API and DOS attribute constants, especially `FILE_ATTRIBUTE_DIRECTORY` and `FILE_ATTRIBUTE_ARCHIVE`.

## Risks
`dirtest1()` creates files in the share root, so cleanup failure leaves scattered hex-named files. `dirtest2()` assumes `.` and `..` are returned by old listing, making it sensitive to server dialect or compatibility behavior. The no-op callback means content correctness is inferred only from counts.

## Test signals
Useful signals are entry-count mismatches, open/mkdir/list failures, incorrect handling of "must have" attribute high bits, and anomalous elapsed-time output under large `torture_numops`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/disconnect.c -->
# sources/user-network-fs/samba/source4/torture/basic/disconnect.c

## Purpose
This file verifies that the server handles abrupt client disconnects while asynchronous requests are outstanding. It targets cleanup paths for pending opens and timed locks.

## Important APIs, types, and functions
Local helpers are `test_disconnect_open()` and `test_disconnect_lock()`, with exported `torture_disconnect()`. Important APIs are `smb_raw_open()`, `smb_raw_open_send()`, `smb_raw_lock()`, `smb_raw_lock_send()`, `smbcli_chkpath()`, `torture_open_connection()`, `talloc_free(cli)`, and `smb_raw_exit()`. It uses `union smb_open`, `union smb_lock`, and `struct smb_lock_entry`.

## Control flow
The harness creates `\test_disconnect`, then for each `torture_numops` iteration sends a blocking/timed lock request behind an existing lock and frees the client before completion. It reconnects, then opens a file, queues two conflicting async opens, validates the connection is still alive with `chkpath`, and frees that client too. Samba3 mode adds a small sleep to reduce process scheduling races.

## State and persistence
The server-side state under test is pending request state, byte-range lock state, and file handle cleanup after transport teardown. Test files are under `\test_disconnect` and are removed by `smbcli_deltree()` at the end.

## Dependencies and integration points
This is a basic torture test using raw SMB open/lock async calls. It relies on talloc ownership: freeing `cli` is the simulated disconnect. The server must tolerate abandoned SMB requests without leaking locks, fnums, or process state.

## Risks
The test intentionally drops connections with live requests, so failures can look like transport instability. Timing is non-deterministic around lock timeouts and Samba3 scheduling. If cleanup does not run after an early return, `\test_disconnect` may remain.

## Test signals
Expected signals are successful `chkpath` before disconnect, no unexpected status from initial open/lock setup, successful reconnection after each forced disconnect, and absence of hangs or later sharing violations caused by leaked locks or opens.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/disconnect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/locking.c -->
# sources/user-network-fs/samba/source4/torture/basic/locking.c

## Purpose
This file builds the `lock` torture suite for SMB byte-range locking semantics. It checks close behavior, lock timeouts, PID-scoped contexts, 32-bit offsets, overlapping read/write locks, recursive lock stacks, unusual LockingX bits, strict locking enforcement, and truncation while locked.

## Important APIs, types, and functions
The suite is created by `torture_base_locktest()`, registering `LOCK1` through `LOCK7`. Local tests are `torture_locktest1()` through `torture_locktest7()`. They use `smbcli_open()`, `smbcli_close()`, `smbcli_lock()`, `smbcli_unlock()`, `smbcli_locktype()`, `smbcli_read()`, `smbcli_write()`, `smbcli_getatr()`, `smbcli_unlink()`, and `check_error()`. `cli->session->pid` is deliberately mutated to simulate multiple SMB process IDs over one connection.

## Control flow
`LOCK1` verifies locks persist until the locking handle closes and that timed lock requests actually wait. `LOCK2` checks same-connection PID isolation and failed unlocks from the wrong PID. `LOCK3` walks offsets across the 32-bit range and verifies non-overlap and conflict behavior. `LOCK4` probes overlapping read/write combinations across same process, different connection, and different PID, including strict read/write blocking and a known NT byte-range bug. `LOCK5` focuses on lock upgrade/downgrade and stack unlock order. `LOCK6` sends `LOCKING_ANDX_CHANGE_LOCKTYPE` and `LOCKING_ANDX_CANCEL_LOCK`. `LOCK7` validates read-lock versus write-lock access restrictions and confirms truncation through a separate open.

## State and persistence
All test files live under `\locktest` except `LOCK6`'s `\lock6.txt`. The persistent server state under test is lock ownership by connection, PID, fnum, range, and lock type. There is no local durable state.

## Dependencies and integration points
The suite depends on the basic torture framework and connected one- or two-SMB test wrappers. It validates Samba behavior against Windows/SMB semantics rather than POSIX byte-range lock semantics, especially same-PID overlap rules.

## Risks
Timing-sensitive checks can fail on very slow or overloaded servers. Tests mutate `cli->session->pid` and must leave it sane for later operations. Some cases intentionally call unlocks after failed locks to probe behavior, so error handling must be read in context.

## Test signals
Important signals are expected `ERRlock`, `ERRnotlocked`, `NT_STATUS_LOCK_NOT_GRANTED`, `NT_STATUS_FILE_LOCK_CONFLICT`, and `NT_STATUS_RANGE_NOT_LOCKED`; timed locks sleeping long enough; read/write failures on locked ranges; and the final suite registration exposing all seven cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/locking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/mangle_test.c -->
# sources/user-network-fs/samba/source4/torture/basic/mangle_test.c

## Purpose
This file stress-tests 8.3 short-name mangling. It creates randomized long names, queries their alternate names, verifies open/unlink interoperability through long and short names, and tracks short-name collisions.

## Important APIs, types, and functions
Key functions are `test_one()`, `gen_name()`, and exported `torture_mangle()`. It uses an internal TDB (`tdb_open(NULL, ..., TDB_INTERNAL, ...)`) with `tdb_fetch_bystring()` and `tdb_store_bystring()` to remember short-name mappings. SMB APIs include `smbcli_open()`, `smbcli_close()`, `smbcli_qpathinfo_alt_name()`, `smbcli_unlink()`, `smbcli_unlink_wcard()`, and `smbcli_rmdir()`.

## Control flow
`torture_mangle()` opens the in-memory TDB, creates `\mangle_test`, then runs `torture_numops` generated filenames. For each name, `test_one()` creates the long name, queries the server alternate name, deletes via the short name, recreates via short name, deletes via long name, and records or reports alternate-name collisions. Periodic progress prints collision and failure ratios.

## State and persistence
Server state is confined to `\mangle_test`, which is wildcard-unlinked and removed. Process-global counters `total`, `collisions`, and `failures`, plus global `tdb`, persist across the test invocation. The TDB is in-memory only.

## Dependencies and integration points
The test depends on `system/dir.h`, TDB utility helpers, Samba pathinfo alternate-name support, and torture settings. It is part of the basic SMB torture tests and assumes the target filesystem exposes short names.

## Risks
Short-name behavior is configuration- and filesystem-dependent; valid failures may indicate disabled mangling rather than a generic SMB bug. The random generator intentionally biases toward collision-prone names, which can be expensive for large `torture_numops`. Global counters are not reset inside `torture_mangle()`, so repeated in-process calls may accumulate totals.

## Test signals
Failures are inability to query alternate names, inability to unlink/recreate across long/short names, or a nonzero `failures` counter. Collisions are reported but not necessarily fatal unless they lead to operation failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/mangle_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/misc.c -->
# sources/user-network-fs/samba/source4/torture/basic/misc.c

## Purpose
This file contains miscellaneous SMB torture and benchmark utilities: randomized read/write stress, pipe count probing, idle connection/file-handle hold tests, maximum fnum discovery, IOCTL scanning, and an asynchronous multi-connection read/write benchmark.

## Important APIs, types, and functions
Exported entry points include `run_torture()`, `run_pipe_number()`, `torture_holdcon()`, `torture_holdopen()`, `torture_maxfid_test()`, `torture_ioctl_test()`, and `run_benchrw()`. The benchmark uses `enum benchrw_stage`, `struct bench_params`, `struct benchrw_state`, `init_benchrw_params()`, `benchrw_callback()`, `benchrw_rw_callback()`, `benchrw_open()`, `benchrw_mkdir()`, `benchrw_close()`, `async_open_callback()`, and `torture_connect_async()`.

## Control flow
`rw_torture()` coordinates random file writers through a lock file and verifies PID data after repeated writes. `run_pipe_number()` opens `\WKSSVC` until failure. `torture_holdcon()` opens many connections and pings until all die; `torture_holdopen()` opens one file many times then pings forever. `torture_maxfid_test()` creates a directory fanout and opens up to `0x11000` files, then closes and unlinks them. `torture_ioctl_test()` scans device/function values and prints successful IOCTLs.

The `run_benchrw()` path is an event-driven state machine. It initializes UNC targets from settings or an `unclist`, starts async composite connects, cleans/creates per-worker directories, opens files, writes initial blocks, keeps a configured number of parallel read/write requests in flight, closes, deletes test dirs, and disconnects trees.

## State and persistence
The tests create `\torture.lck`, `\torture.N`, `\holdopen.dat`, `\maxfid`, `\ioctl.dat`, and benchmark directories such as `benchrw0`. Several tests are deliberately long-lived or infinite until the server drops connections. Local state is stored in talloc-owned benchmark structs and callbacks.

## Dependencies and integration points
This file touches raw SMB, composite connect APIs, tevent, resolver configuration, command-line credentials, local file loading for `unclist`, and torture runtime settings such as `nprocs`, `retry`, `blocksize`, `writeblocks`, `writeratio`, `parallel_requests`, `host`, and `share`.

## Risks
Some functions are destructive stress tools rather than normal pass/fail unit tests. `torture_holdcon()` and `torture_holdopen()` intentionally loop indefinitely. `torture_maxfid_test()` can create many files and consume server resources. `run_benchrw()` mixes async callbacks with synchronous cleanup and is sensitive to callback state transitions, memory ownership, and event-loop progress.

## Test signals
Signals include data corruption in `rw_torture()`, maximum open pipe/file counts, successful IOCTL discovery lines, benchmark `ERROR` states, tree disconnect failures, and whether all async workers reach `FINISHED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/properties.c -->
# sources/user-network-fs/samba/source4/torture/basic/properties.c

## Purpose
This file prints negotiated server capabilities and filesystem attributes. It is an inspection test rather than a deep mutating torture scenario.

## Important APIs, types, and functions
The core helpers are `struct bitmapping`, `BIT_NAME`, `show_bits()`, and exported `torture_test_properties()`. It uses `cli->transport->negotiate.capabilities` and `smb_raw_fsinfo()` with `RAW_QFS_ATTRIBUTE_INFO`.

## Control flow
`torture_test_properties()` prints the capability mask, decodes known capability bits, queries filesystem attribute information, decodes known filesystem flags, and prints max component length and filesystem type. Failure to query fsinfo sets `correct=false`.

## State and persistence
The test is read-only from the server perspective and has no local persistent state.

## Dependencies and integration points
It depends on negotiated SMB capability constants and filesystem attribute constants, plus the raw fsinfo API. It is useful as context for interpreting other torture failures because it reveals DFS, NT SMB, Unicode, large file, ACL, sparse file, named stream, and similar capability claims.

## Risks
Unknown bits are only printed, not failed. Some attributes are server-advertised capabilities, not proof that all related behavior is correct.

## Test signals
Primary signals are a failed `RAW_QFS_ATTRIBUTE_INFO` request, missing expected capability/attribute bits for a test environment, or unexpected unknown bit masks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/properties.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/rename.c -->
# sources/user-network-fs/samba/source4/torture/basic/rename.c

## Purpose
This file tests rename behavior for open files under different share-delete and access-mask combinations.

## Important APIs, types, and functions
The exported function is `torture_test_rename()`. It uses `smbcli_nt_create_full()`, `smbcli_rename()`, `smbcli_close()`, `smbcli_unlink()`, `torture_assert()`, and `torture_assert_ntstatus_ok()`.

## Control flow
The test clears `\test.txt` and `\test1.txt`, opens `\test.txt` with read access and read share only, and asserts rename fails. It repeats with `NTCREATEX_SHARE_ACCESS_DELETE | NTCREATEX_SHARE_ACCESS_READ` and asserts rename succeeds. Finally it opens with only `SEC_STD_READ_CONTROL` and no sharing and asserts rename succeeds, reflecting semantics where no delete/read/write data access is held.

## State and persistence
Only `\test.txt` and `\test1.txt` are created, renamed, closed, and unlinked. There is no local durable state.

## Dependencies and integration points
The test is a basic torture test relying on NT CreateX share-mode semantics and the higher-level `smbcli_rename()` wrapper. It complements deny/share tests in `denytest.c`.

## Risks
Server behavior around metadata-only opens can be subtle; the third case expects rename success even with share access none because the handle does not request conflicting data/delete access. Cleanup runs after each case but early assertion failure can leave a test file.

## Test signals
The critical signals are first rename failing, second rename succeeding with share-delete, and third rename succeeding with `SEC_STD_READ_CONTROL`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/scanner.c -->
# sources/user-network-fs/samba/source4/torture/basic/scanner.c

## Purpose
This file implements exploratory scanners for TRANS2, NTTRANS, and base SMB opcodes. It discovers which opcodes and information levels elicit meaningful responses from a server.

## Important APIs, types, and functions
TRANS2 helpers are `trans2_check_hit()`, `try_trans2()`, `try_trans2_len()`, `trans2_op_exists()`, `scan_trans2()`, and exported `torture_trans2_scan()`. NTTRANS helpers are `nttrans_check_hit()`, `try_nttrans()`, `try_nttrans_len()`, `scan_nttrans()`, and exported `torture_nttrans_scan()`. Base opcode scanning is in `torture_smb_scan()`. It uses `struct smb_trans2`, `struct smb_nttrans`, `DATA_BLOB`, `SSVAL`, `push_string()`, and raw SMB request setup/send/process APIs.

## Control flow
TRANS2 scanning first creates/open handles for a test file, root directory, and quota stream. It checks whether each op differs from a known invalid op, then probes levels `0..50`, `0x100..0x130`, and `1000..1049` using multiple parameter shapes: info-level-only, file descriptor, quota descriptor, notify-style descriptor, existing filename, new filename, and DFS-style directory name. NTTRANS follows the same level ranges without the quota case. Base SMB scanning opens a fresh connection for each opcode except `SMBreadbraw`, sends a minimal request, waits briefly, prints status or no-reply, and avoids closing a connection that did not reply.

## State and persistence
The scanners create `\scanner.dat`, `\newfile.dat`, and `\testdir` transiently, but cleanup is incomplete for `\scanner.dat` and open handles. Most state is temporary talloc memory and raw request buffers.

## Dependencies and integration points
This is a low-level compatibility discovery tool over Samba's raw SMB APIs. It depends on dialect behavior, server validation paths, and configured access to quota/DFS-like paths. Output is printed rather than asserted.

## Risks
The scanners send intentionally malformed or broad requests and can trigger server log noise, slow paths, or disconnects. The base SMB scanner may leave a connection open on no-reply paths by design. Results are discovery data, not deterministic pass/fail guarantees.

## Test signals
Signals are printed `Found op`, `found <format> level=...`, base opcode status lines, no-reply cases, and unexpected non-generic statuses that survive the ignore filters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/scanner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/secleak.c -->
# sources/user-network-fs/samba/source4/torture/basic/secleak.c

## Purpose
This file repeatedly attempts failed SMB session setup with invalid credentials to expose security/authentication memory leaks.

## Important APIs, types, and functions
Local `try_failed_login()` creates a new `smbcli_session`, builds `struct smb_composite_sesssetup`, initializes credentials, sets an invalid domain/user/password, calls `smb_composite_sesssetup()`, and frees the session. Exported `torture_sec_leak()` loops this helper until a configured time limit expires and calls `talloc_report()`.

## Control flow
For each iteration, the test obtains SMB session options from `lp_ctx`, attaches to the existing transport, configures credentials with invalid values, performs composite session setup, and expects failure. A successful invalid login is a hard failure. The outer loop runs until `time_mono()` exceeds `timelimit` (default 20 seconds).

## State and persistence
The test creates no files. State under test is client/server authentication allocation behavior and cleanup after failed session setup. It prints talloc reports to stdout to show memory growth.

## Dependencies and integration points
It depends on `auth/credentials`, gensec settings, composite SMB session setup, and the existing negotiated transport. It is a runtime diagnostic rather than a file operation test.

## Risks
The test can generate many authentication failures and logs. It does not automatically quantify memory growth; humans or log tooling must interpret `talloc_report()` output. The invalid credential path must remain invalid in the environment.

## Test signals
Signals are any accepted invalid session setup, increasing talloc allocation reports across iterations, or unexpected transport/session failures unrelated to authentication rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/secleak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/unlink.c -->
# sources/user-network-fs/samba/source4/torture/basic/unlink.c

## Purpose
This file validates that unlinking an open file is denied even when the file was opened with delete-related access/share settings.

## Important APIs, types, and functions
The exported function is `torture_unlinktest()`. It uses `torture_setup_dir()`, `smbcli_open()`, `smbcli_unlink()`, `smbcli_close()`, `smb_raw_open()` with `RAW_OPEN_NTCREATEX`, `check_error()`, and `union smb_open`.

## Control flow
The test creates `\unlinktest\unlink.tst`, opens it with classic `smbcli_open()`, asserts unlink fails with sharing violation, closes and removes it, then recreates it using NT CreateX with full file rights and `NTCREATEX_SHARE_ACCESS_DELETE`. It again asserts unlink while open fails and verifies the error mapping.

## State and persistence
State is confined to `\unlinktest` and the single test file. The final NT CreateX handle is not explicitly closed before return, relying on harness/session cleanup; this is acceptable for the test intent but notable.

## Dependencies and integration points
The file complements rename/share-delete tests and uses both high-level and raw open paths. It depends on DOS/NT error mapping through `check_error()`.

## Risks
Servers that implement POSIX delete-on-open semantics differently may fail this compatibility expectation. The missing explicit close after the second open can leave transient state until connection cleanup.

## Test signals
Both unlink attempts must fail and report `ERRDOS/ERRbadshare` with `NT_STATUS_SHARING_VIOLATION`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/utable.c -->
# sources/user-network-fs/samba/source4/torture/basic/utable.c

## Purpose
This file probes Unicode filename acceptance and case-equivalence behavior. It can generate a `valid.dat` table of accepted Unicode codepoints and exercise server case folding through file aliases.

## Important APIs, types, and functions
Exported functions are `torture_utable()` and `torture_casetable()`. Helper `form_name()` converts a codepoint to a `\utable\...` filename. It uses `convert_string(CH_UTF16, CH_UNIX, ...)`, `SSVAL`, `smbcli_open()`, `smbcli_nt_create_full()`, `smbcli_qpathinfo_alt_name()`, `smbcli_qfileinfo()`, `smbcli_read()`, `smbcli_write()`, wildcard unlink/rmdir, and `sys_write_v()`.

## Control flow
`torture_utable()` loops over codepoints `1..0xffff`, converts each to a filename with a long extension, tries to create it, asks for the alternate name, and records codepoints whose alternate name is not the generic `X_A_L...` pattern. It writes the 65536-byte validity bitmap to local `valid.dat`. `torture_casetable()` loops codepoints, creates/opens corresponding filenames, reads existing equivalence data if another codepoint maps to the same name, writes the current codepoint, and reports equivalence sets.

## State and persistence
Server state is under `\utable` and is cleaned by unlink/rmdir. Local durable output is `valid.dat` in the current working directory. Large in-memory arrays include `valid[0x10000]` and `equiv[0x10000][8]`.

## Dependencies and integration points
The test depends on Samba charset conversion, server Unicode filename handling, short-name generation, and case-insensitive filesystem behavior. It is sensitive to locale/charset configuration.

## Risks
The full Unicode loop is expensive and may produce many server operations. `valid.dat` is written outside the research tree/test share and can surprise callers. Case table probing can be noisy and depends heavily on filesystem normalization semantics.

## Test signals
Signals are counts of allowed characters and alternate-name-allowed characters, printed equivalence groups, conversion failures, failed creates for specific codepoints, and successful creation of `valid.dat`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/utable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dfs/common.c -->
# sources/user-network-fs/samba/source4/torture/dfs/common.c

## Purpose
This file provides the shared DFS referral transaction helper used by the DFS torture tests.

## Important APIs, types, and functions
The only exported function is `dfs_cli_do_call(struct smbcli_tree *tree, struct dfs_GetDFSReferral *ref)`. It uses `struct smb_trans2`, setup code `TRANSACT2_GET_DFS_REFERRAL`, `ndr_push_struct_blob()`, `ndr_pull_struct_blob()`, generated NDR routines `ndr_push_dfs_GetDFSReferral_in` and `ndr_pull_dfs_referral_resp`, and `smb_raw_trans2()`.

## Control flow
The function initializes a TRANS2 request with one setup word, marshals `ref->in.req` into the parameter blob, sends the request, and unmarshals `trans.out.data` into `ref->out.resp`. Push failures return `NT_STATUS_INTERNAL_ERROR`, transport/server failures are returned directly, and pull failures return `NT_STATUS_INVALID_NETWORK_RESPONSE`.

## State and persistence
The helper is stateless aside from talloc allocations under `tree` for blobs. It does not create files or mutate share contents.

## Dependencies and integration points
It is the integration point between Samba's raw TRANS2 client and generated DFS referral NDR structures. Callers must initialize `ref->in.req.max_referral_level`, `ref->in.req.servername`, and `ref->out.resp`.

## Risks
The response buffer limit is fixed at 4096 bytes; unusually large referral responses may truncate or fail. The helper assumes response data, not params, contains the referral response. Memory is tied to `tree`, which is fine for test lifetime but can accumulate in long loops.

## Test signals
Signals are the exact NTSTATUS returned by `dfs_cli_do_call()` and whether response unmarshalling succeeds. `NT_STATUS_INVALID_NETWORK_RESPONSE` indicates malformed or incompatible DFS referral encoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dfs/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dfs/domaindfs.c -->
# sources/user-network-fs/samba/source4/torture/dfs/domaindfs.c

## Purpose
This file defines the domain DFS torture suite. It validates domain referrals, DC referrals for FQDN and NetBIOS names, SYSVOL referrals, unknown-domain errors, subtree referral errors, low referral level errors, and suite registration.

## Important APIs, types, and functions
Local tests are `test_getdomainreferral()`, `test_getdcreferral()`, `test_getdcreferral_netbios()`, `test_getsysvolreferral()`, `test_unknowndomain()`, `test_getsysvolplusreferral()`, and `test_low_referral_level()`. `torture_dfs_init()` creates and registers the `dfs/domain` suite. The file uses `struct dfs_GetDFSReferral`, `struct dfs_referral_resp`, `dfs_cli_do_call()`, referral constants such as `DFS_SERVER_NON_ROOT`, `DFS_FLAG_REFERRAL_DOMAIN_RESP`, `DFS_HEADER_FLAG_STORAGE_SVR`, and torture assertion helpers.

## Control flow
Most tests start by requesting a level-3 domain referral with an empty server name, then use returned `special_name` values to request DC or SYSVOL referrals. FQDN logic chooses a referral containing a dot; NetBIOS logic chooses one without a dot. SYSVOL tests build `<domain>\sysvol`, validate `path_consumed`, storage-server header flags, referral version/type/flags, and expected substrings in `DFS_path` and `netw_address`. The level-4 SYSVOL check expects version 4 and an all-zero service-site GUID. Negative tests expect `NT_STATUS_INVALID_PARAMETER`, `NT_STATUS_NOT_FOUND`, or `NT_STATUS_UNSUCCESSFUL`.

## State and persistence
The tests are read-only protocol calls and do not create files. State comes from live domain DFS configuration returned by the server.

## Dependencies and integration points
The suite depends on `dfs_cli_do_call()` from `common.c`, generated DFS referral NDR structures, and a server configured as or connected to a domain DFS referral provider. It registers under the torture subsystem with one-SMB test cases.

## Risks
The tests assume at least two referral entries in some paths and make selection decisions by looking for dots in returned names. Environments with unusual domain naming, single referral entries, disabled SYSVOL, or different referral-level support may fail for configuration reasons. String assertions are strict and may need updates if referral formatting changes.

## Test signals
Strong signals are nonzero domain referrals, correct path consumption, expected header flags, version 3/4 referral entries, valid special names and expanded names, FQDN/NetBIOS formatting, all-zero service-site GUID for level 4 SYSVOL, and the expected negative NTSTATUS values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dfs/domaindfs.c -->
