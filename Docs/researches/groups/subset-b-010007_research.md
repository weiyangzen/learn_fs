# subset-b-010007 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/streams.c -->
# sources/user-network-fs/samba/source4/torture/smb2/streams.c

## Purpose
`streams.c` implements the `smb2.streams` torture suite for SMB2 alternate data stream behavior. It is a protocol conformance and regression collection for named streams on files and directories, including stream creation, lookup, stream list enumeration, delete-on-close, share-mode interaction, stream name parsing, case-insensitive stream lookup, stream rename semantics, create disposition effects, metadata propagation between base file and streams, and a Samba inherit-permissions crash regression.

## Important APIs, Types, and Functions
The suite entry point is `torture_smb2_streams_init()`, which registers tests named `dir`, `io`, `sharemodes`, `names`, `names2`, `names3`, `rename`, `rename2`, `create-disposition`, `attributes1`, `attributes2`, `delete`, `zero-byte`, and `basefile-rename-with-open-stream`. Local helpers include `check_stream()`, which opens `<base>:<stream>` and optionally verifies stream data, `check_stream_list()`, which queries `RAW_FILEINFO_STREAM_INFORMATION` and compares sorted stream names, `create_file_with_stream()`, `open_stream()`, and `check_metadata()`.

The file uses `struct smb2_tree`, `struct smb2_handle`, `struct smb2_create`, `struct smb2_read`, `union smb_open`, `union smb_fileinfo`, and `union smb_setfileinfo`. Most assertions use local `CHECK_STATUS`, `CHECK_VALUE`, `CHECK_NTTIME`, `CHECK_STR`, and `CHECK_CALL_HANDLE` macros that fail through the torture context and jump to cleanup.

## Control Flow
Every test creates a clean `teststreams` directory with `torture_smb2_testdir()` after removing prior contents with `smb2_deltree()` or `smb2_util_unlink()`. The tests then build SMB2 create/open or setinfo requests against path forms such as `file:stream`, `file:stream:$DATA`, `file::$DATA`, and invalid variants.

`test_stream_dir()` verifies that directory stream opens fail with the expected not-a-directory or file-is-directory statuses. `test_stream_io()` creates streams on nonexistent and existing base files, writes and rewrites data, checks default and named stream list entries, and verifies deletion through unlink and delete-on-close. `test_zero_byte_stream()` asserts that a zero-length named stream is still returned in stream enumeration.

`test_stream_sharemodes()` and `test_stream_delete()` exercise stream-specific sharing and delete behavior: different streams can avoid share conflicts, the same stream conflicts, an open stream without `FILE_SHARE_DELETE` blocks deleting the base file, and delete-pending behavior blocks name-based access until open stream handles close. `test_stream_names()`, `test_stream_names2()`, and `test_stream_names3()` cover unusual characters, invalid stream type suffixes, wildcard-like stream names, stream metadata queries, stream rename collisions, control-character rejection, and case-insensitive stream access when the filesystem advertises case-sensitive search support. `test_stream_rename()` and `test_stream_rename2()` focus on SMB1-style and SMB2-style rename information buffers for stream-to-stream and stream-to-default-stream renames.

`test_stream_create_disposition()` verifies that base-file `OVERWRITE`, `OVERWRITE_IF`, and `SUPERSEDE` remove named streams while stream-level overwrite preserves the stream set. `test_stream_attributes1()` and `test_stream_attributes2()` check that stream timestamp and attribute updates are reflected on the base file where Windows-compatible semantics require it, and that creation time is not accidentally refreshed by writes. `test_basefile_rename_with_open_stream()` uses a second SMB2 connection and expects renaming the base file to fail while a stream is open. `test_stream_inherit_perms()` reads and extends a directory security descriptor, writes the DACL back, then creates a stream under the directory to trigger bug 15695 coverage.

## State and Persistence Behavior
The tests mutate a live SMB share under `teststreams` and a few temporary top-level names. Persistent state under test includes named streams, stream data, open-handle share tables, delete-pending state, file metadata, security descriptors, and directory entries. Local state is stack or talloc-scoped, with explicit handle cleanup in `done` blocks and tree cleanup at test end. Some tests skip or adjust behavior based on torture settings such as `samba3` and `samba4`.

## Dependencies and Integration Points
This file depends on Samba's SMB2 client calls (`smb2_create`, `smb2_read`, `smb2_getinfo_file`, `smb2_setinfo_file`), SMB2 torture helpers from `torture/smb2/proto.h`, talloc, stream sorting via `TYPESAFE_QSORT`, locale helpers for character tests, and security descriptor helpers. It integrates with the broader `TORTURE_SMB2` module through `torture_smb2_streams_init()`.

## Risks
The suite encodes exact Windows-compatible ADS behavior, so expected statuses can be brittle across Samba backends, non-NTFS-like filesystems, or target profiles. Timing and metadata propagation checks can be sensitive to filesystem timestamp granularity. The tests are destructive under their test directory and assume stream syntax and delete-pending semantics are implemented consistently by the server.

## Test Signals
Failures are reported as mismatched `NTSTATUS`, unexpected stream names or counts, bad stream data, incorrect metadata values, unexpected share-mode acceptance, missing delete-pending behavior, invalid rename outcomes, or security descriptor/permission inheritance regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/streams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/tcon.c -->
# sources/user-network-fs/samba/source4/torture/smb2/tcon.c

## Purpose
`tcon.c` implements a focused SMB2 tree-connect identity test. It verifies that file handles are scoped correctly to the tree ID and session ID that opened them, and that a server rejects writes performed through an unrelated tree connect, an invalid tree ID, or an invalid session ID.

## Important APIs, Types, and Functions
The central exported test function is `run_tcon_test(struct torture_context *tctx, struct smb2_tree *tree)`. The local helper `smb2cli_session_set_id()` wraps `smb2cli_session_set_id_and_flags()` so the test can temporarily alter only the session ID while preserving session flags. The test uses `smb2_create`, `smb2_util_write`, `smb2_util_close`, `smb2_util_unlink`, `torture_smb2_tree_connect`, `smb2cli_tcon_current_id`, `smb2cli_tcon_set_id`, and `smb2cli_session_current_id`.

## Control Flow
The test removes any stale `tcontest.tmp`, creates the file on the supplied tree with read/write access and broad share access, records the valid tree ID and session ID, and performs an initial write to prove the handle is usable. It then opens a second tree connect on the same session and derives an invalid tree ID and invalid session ID.

The negative checks deliberately mutate the second tree's IDs. First it uses the second tree's valid TID with the first tree's file handle and expects the write to fail. Next it sets an arbitrary invalid TID and again expects failure. Finally it changes the session ID to a different value while setting the TID back to the first tree ID and expects the server to reject the write. After the negative checks, the original session and tree IDs are restored, the handle is closed, and the file is removed.

## State and Persistence Behavior
The only durable server object is `tcontest.tmp`, which is created, written, closed, and unlinked. More important is transient connection state: the test mutates client-side tree and session IDs to send intentionally invalid SMB2 requests. That state is restored before the final close to avoid poisoning later tests on the same connection.

## Dependencies and Integration Points
This file depends on low-level SMB2 client ID accessors from `smbXcli_base`, SMB2 torture connection helpers, resolver/event/loadparm context includes, and the standard torture result path. The function is registered elsewhere in the SMB2 suite through generated prototypes from `torture/smb2/proto.h`.

## Risks
Because it changes in-memory IDs on a live client object, failed cleanup could leave the connection in an invalid state for subsequent tests. The expected failures are protocol-security critical: accepting any of these writes would indicate handle authorization is not bound to the correct tree/session identity.

## Test Signals
The primary signals are `NT_STATUS_OK` for initial create/write/close and non-OK statuses for writes through the wrong TID, invalid TID, and invalid VUID/session ID. Any successful negative write is a torture failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/tcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/timestamps.c -->
# sources/user-network-fs/samba/source4/torture/smb2/timestamps.c

## Purpose
`timestamps.c` implements SMB2 timestamp torture suites. It validates timestamp round-tripping across extreme `time_t` values, special `NTTIME_FREEZE` and `NTTIME_THAW` values, close response behavior, immediate write-time update rules, sticky write-time semantics across multiple handles, EOF/allocation-size metadata effects, and a Windows timestamp-resolution observation test.

## Important APIs, Types, and Functions
The main suite entry points are `torture_smb2_timestamps_init()` and `torture_smb2_timestamp_resolution_init()`. Registered tests include `test_close_not_attrib`, many `time_t_*` cases, `freeze-thaw`, delayed write-time tests, two multi-tree `modern_write_time_update` tests, and `resolution1`.

Key helpers are `test_time_t()`, which sets create/write times and verifies both handle getinfo and directory find results, `test_delayed_write_vs_setbasic_do()`, which reuses a caller-provided basic-info setinfo payload, and `getinfo_both()`, which compares handle-based and path-based write times. The code uses `struct smb2_create`, `struct smb2_close`, `struct smb2_find`, `struct smb2_flush`, `union smb_fileinfo`, `union smb_setfileinfo`, `NTTIME`, `unix_to_nt_time()`, and `full_timespec_to_nt_time()`.

## Control Flow
Each test cleans `smb2-timestamps`, creates a test directory, creates or opens `testfile.dat` or a generated filename, and performs SMB2 create, setinfo, getinfo, write, flush, close, and find requests. `test_close_no_attrib()` closes without full-information flags and asserts that close output attributes and times are omitted. `test_time_t()` covers future, epoch, negative, and pre-1970 values by setting basic information, verifying direct getinfo, verifying `SMB2_FIND_ID_BOTH_DIRECTORY_INFO`, reopening, and verifying again.

`test_freeze_thaw()` sets known timestamps, then submits `NTTIME_FREEZE` and `NTTIME_THAW` and verifies neither changes stored values. `test_delayed_write_vs_seteof()`, `test_delayed_write_vs_flush()`, `test_delayed_write_vs_setbasic()`, `test_delayed_1write()`, and `test_delayed_2write()` check modern immediate write-time behavior, including that flush and close do not apply extra pending write-time changes and that explicit write-time setinfo is respected.

`test_modern_write_time_update1()` opens the same file from two SMB2 trees and verifies that writes and sticky write-time settings are visible consistently through both handles and path opens. It confirms that after a handle sets a sticky future write time, writes from that same handle preserve it, while a write from the second handle unfreezes and advances it. `test_modern_write_time_update2()` applies the same multi-handle model to end-of-file and allocation-size updates, distinguishing mtime and ctime behavior. `test_timestamp_resolution1()` documents Windows 2019-style roughly 15 ms resolution: an immediate write may not change close write time, while a write after 20 ms should.

## State and Persistence Behavior
The tests create and remove the `smb2-timestamps` tree. Server state under test is file timestamps, close response fields, write-time sticky state, allocation size, EOF size, change time, open handles across two tree connections, and directory search metadata. Several tests intentionally sleep or wait milliseconds to avoid filesystem timestamp granularity.

## Dependencies and Integration Points
The file depends on SMB2 client calls, SMB2 torture helpers, general torture assertions, `torture/util.h`, time conversion utilities, and generated SMB2 suite prototypes. The two modern update tests are registered as `torture_suite_add_2smb2_test()` because they require two SMB2 tree connections.

## Risks
Timestamp tests are inherently sensitive to server clock behavior, filesystem resolution, network latency, and platform time range support. Extreme negative and far-future values may expose backend limitations. The resolution test is explicitly timing-dependent and documented as unsuitable for normal Samba CI.

## Test Signals
Signals include exact `NTTIME` equality or inequality checks, directory find metadata matching handle metadata, close output fields being omitted or preserved as expected, mtime/ctime changes after EOF and allocation operations, sticky write-time preservation, and consistent values observed through concurrent handles and path opens.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/timestamps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/util.c -->
# sources/user-network-fs/samba/source4/torture/smb2/util.c

## Purpose
`util.c` provides shared helper functions for Samba's SMB2 torture tests. It centralizes file and directory creation, SMB2 connection setup, tree/session setup, read/write utilities, metadata dump and verification helpers, lease/oplock/create request builders, and privilege checks so individual tests can focus on protocol behavior.

## Important APIs, Types, and Functions
Core file helpers include `smb2_util_write()`, `smb2_create_complex_file()`, `smb2_create_complex_dir()`, `smb2_create_simple_file()`, `torture_smb2_testfile_access()`, `torture_smb2_testfile()`, `torture_smb2_open()`, `torture_smb2_testdir_access()`, `torture_smb2_testdir()`, `torture_setup_simple_file()`, `torture_setup_complex_file()`, `torture_setup_complex_dir()`, `smb2_util_roothandle()`, and `smb2_util_setup_dir()`. Diagnostic and verification helpers include `torture_smb2_all_info()`, `torture_smb2_get_allinfo_access()`, `smb2_util_verify_sd()`, and `smb2_util_verify_attrib()`.

Connection helpers include `torture_smb2_tree_connect()`, `torture_smb2_session_setup()`, `torture_smb2_connection_ext()`, `torture_smb2_connection()`, `torture_smb2_con_share()`, and `torture_smb2_con_sopt()`. Lease/oplock helpers include `smb2_util_lease_state()`, `smb2_util_lease_state_string()`, `smb2_util_share_access()`, `smb2_util_oplock_level()`, `smb2_generic_create_share()`, `smb2_generic_create()`, `smb2_lease_create_share()`, `smb2_lease_create()`, `smb2_lease_v2_create_share()`, `smb2_lease_v2_create()`, `smb2_oplock_create_share()`, and `smb2_oplock_create()`.

## Control Flow
Simple helpers build a request struct, call the relevant SMB2 API, and return either an `NTSTATUS` or boolean. `smb2_create_complex()` is the most involved path: it removes a prior object, prepares a file or directory create request, optionally adds EAs, retries without EAs if unsupported, writes sample data for files, sets deliberately distinct timestamps, then queries all information to verify that the server stored the requested times.

Connection setup reads `host`, `share`, and optional `unclist` torture settings, pulls SMB client options and credentials from the command-line context, creates transports/sessions/trees, and reports failures through `torture_comment()`. Generic create builders populate `struct smb2_create` consistently for lease, oplock, directory, share-access, and disposition scenarios.

## State and Persistence Behavior
These helpers mutate remote SMB shares by creating, deleting, writing, and setting metadata on files and directories. They also allocate talloc contexts tied to trees or the torture context and return open SMB2 handles that callers must close. Connection helpers create client transport/session/tree state and may advance `tctx->conn_index` when `unclist` is used.

## Dependencies and Integration Points
The file sits at the center of SMB2 torture integration. It depends on SMB2 client calls, `smbXcli_base`, command-line credentials, loadparm, resolver and event contexts, security descriptor and NDR printing helpers, LSA privilege helpers, and `source4/torture/util.h`. Many SMB2 tests depend on these helpers through generated declarations in `torture/smb2/proto.h`.

## Risks
Because this file defines common request defaults, a change can alter many unrelated torture suites. The complex-file helper assumes timestamp setting support and reports errors if backends round or omit times. Attribute verification masks archive and non-indexed bits, which is intentional but can hide some server differences. Connection helpers depend on global command-line state and must be used with the correct talloc ownership.

## Test Signals
Signals produced by this file are usually helper-level `NTSTATUS` returns, torture comments, descriptor/attribute mismatch warnings, and failed assertions inside callers. For connection helpers, inability to connect or perform tree/session setup is an immediate test setup failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/wscript_build -->
# sources/user-network-fs/samba/source4/torture/smb2/wscript_build

## Purpose
`wscript_build` declares the Samba build target for the SMB2 torture module. It tells waf which SMB2 torture source files form the `TORTURE_SMB2` internal module and how that module integrates into the `smbtorture` subsystem.

## Important APIs, Types, and Functions
The file calls `bld.SAMBA_MODULE('TORTURE_SMB2', ...)`. Its source list includes all SMB2 torture implementations in this directory, including `streams.c`, `tcon.c`, `timestamps.c`, and `util.c`. Build metadata sets `subsystem='smbtorture'`, `deps='LIBCLI_SMB2 torture NDR_IOCTL CMDLINE_S4'`, `internal_module=True`, `autoproto='proto.h'`, and `init_function='torture_smb2_init'`.

## Control Flow
At configure/build time, waf evaluates this Python-style build script, collects the listed source files, generates `proto.h` declarations, and builds an internal module initialized through `torture_smb2_init`. Runtime test registration happens in the compiled C files, but this build file is what makes those registration functions available to smbtorture.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is build graph state: object compilation membership, generated prototype output, dependency linkage, and internal module metadata.

## Dependencies and Integration Points
It integrates SMB2 tests with Samba's waf build system and the broader smbtorture module loader. The explicit dependencies provide SMB2 client APIs, torture harness APIs, ioctl NDR definitions, and Samba command-line support.

## Risks
Removing a source file from this list silently drops tests from the SMB2 module. Adding a source without the right dependencies can cause compile or link failures. The `autoproto` setting means function signatures exported by source files affect generated headers consumed by sibling tests.

## Test Signals
Build success confirms the source list and dependencies are coherent. At runtime, `smbtorture --list-suites` or `--list` should expose SMB2 suites only if this module built and initialized correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smbtorture.c -->
# sources/user-network-fs/samba/source4/torture/smbtorture.c

## Purpose
`smbtorture.c` is the main executable entry point for Samba's smbtorture test runner. It parses command-line options, initializes Samba client configuration, loads torture modules, creates the torture context and output directory, resolves targets, lists or runs requested tests, and returns a process status based on torture results.

## Important APIs, Types, and Functions
Key helpers are `prefix_name()`, `print_test_list()`, `run_matching()`, `torture_run_named_tests()`, `torture_parse_target()`, `parse_dns()`, `print_structured_testsuite_list()`, `print_testsuite_list()`, `torture_print_testsuites()`, `usage()`, `max_runtime_handler()`, and `main()`. Global `use_fullname` controls subunit prefix behavior. The runner relies on `torture_root`, `torture_init()`, `torture_run_suite()`, `torture_run_tcase_restricted()`, and `torture_run_test_restricted()` from the torture framework.

## Control Flow
`main()` initializes talloc, Samba command-line parsing, popt options, loadparm, credentials, and optional restrictions from `--load-list`. It translates target profiles such as `samba3`, `samba4`, `win7`, `w2k16`, and `onefs` into `torture:*` loadparm settings that individual tests read. It sets an optional alarm for maximum runtime, loads an extra module if requested, otherwise calls `torture_init()` to initialize static and shared smbtorture modules.

Listing modes print suites or test names and exit. Normal execution seeds the PRNG, selects a UI backend (`simple` or `subunit`), creates a per-run output directory under `--basedir` or the current directory, initializes `struct torture_context`, calls `gensec_init()`, and either enters `torture_shell()` or parses the first positional argument as a binding/UNC target. It then runs each requested test expression through `torture_run_named_tests()`.

`torture_run_named_tests()` treats `ALL` specially and otherwise delegates to `run_matching()`. `run_matching()` recursively walks suite, testcase, and test nodes, matches names with `gen_fnmatch()`, reloads character conversion state before execution, optionally adjusts subunit prefixes, and runs only matching nodes. `torture_parse_target()` accepts UNC paths or DCERPC binding strings and stores host/share/binding settings for tests.

## State and Persistence Behavior
The runner stores process-wide settings in loadparm under the `torture` namespace and in global variables such as `torture_seed`, `torture_numops`, `torture_entries`, `torture_failures`, and `torture_numasync`. It creates a temporary per-run output directory and deletes it via `torture_deltree_outputdir()` before exit. It can also load extra dynamic modules and read restriction files.

## Dependencies and Integration Points
The file integrates popt, Samba command-line and credentials helpers, loadparm, event contexts, GENSEC, module loading, DCERPC binding parsing, readline shell support, and torture UI backends. It is the top-level consumer of `torture.c` registration and of all module init functions built into smbtorture.

## Risks
Target profile flags are compatibility policy: changing them can alter expected behavior across many tests. The final return code logic is subtle because a torture result return code can coexist with the local `correct` boolean. `parse_dns()` allocates strings with `strdup`/`strndup` and stores them as command-line settings without local frees, which is acceptable for process lifetime but not reusable library style.

## Test Signals
Signals include successful suite/test discovery, valid parsing of UNC or binding targets, subunit/simple result output, nonzero return on setup or test failure, unknown-test messages for unmatched expressions, and maximum-runtime termination through `SIGALRM`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smbtorture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smbtorture.h -->
# sources/user-network-fs/samba/source4/torture/smbtorture.h

## Purpose
`smbtorture.h` is the public header for the smbtorture runner and suite registration layer. It declares global torture runner settings, the root suite pointer, runner lifecycle functions, test dispatch/listing functions, target parsing, and documents target capability flags consumed by tests.

## Important APIs, Types, and Functions
The header declares `torture_root`, `torture_entries`, `torture_seed`, `torture_numops`, `torture_failures`, and `torture_numasync`. Public functions include `torture_init()`, `torture_register_suite()`, `torture_shell()`, `torture_print_testsuites()`, `torture_run_named_tests()`, and `torture_parse_target()`. It forward-declares `struct smbcli_state` and `struct torture_test` and includes the central `../lib/torture/torture.h` harness header.

## Control Flow
The header itself has no runtime control flow, but it defines the interface between module init functions and the smbtorture executable. Modules call `torture_register_suite()` to add suites under `torture_root`; `smbtorture.c` calls `torture_init()` and `torture_run_named_tests()`; tests read settings documented here to adapt expectations to server targets.

## State and Persistence Behavior
All declared globals are process-lifetime runner state. The long comment block describes `torture:*` loadparm settings such as `invalid_lock_range_support`, `sacl_support`, `resume_key_support`, `rewind_support`, `ea_support`, `search_ea_support`, and `hide_on_access_denied`; these settings persist in the loadparm context for the duration of a run.

## Dependencies and Integration Points
This header is included by runner code and suite registration files throughout `source4/torture`. It ties server capability policy to command-line target parsing and lets individual tests avoid hard-coded server names by reading feature flags.

## Risks
The documented feature flags are a compatibility contract. Misspelled or inconsistent setting names cause tests to default to full support and may produce false failures against older or partial servers. Global variables make runner behavior process-wide and unsuitable for independent concurrent runner contexts within one process.

## Test Signals
The header has no direct tests, but successful compilation of torture modules and correct target-specific skips or expected-status changes are indirect signals that this interface remains coherent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smbtorture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/tests/test_gentest.sh -->
# sources/user-network-fs/samba/source4/torture/tests/test_gentest.sh

## Purpose
`test_gentest.sh` is a blackbox wrapper for the `gentest` differential SMB operation generator. It runs `gentest` against two test shares on the same server using deterministic seeds and reports the outcome through Samba's subunit shell helpers.

## Important APIs, Types, and Functions
The script expects `SERVER USERNAME PASSWORD DOMAIN PREFIX` plus optional extra arguments. It uses environment variable `BINDIR` to locate `gentest`, optional `VALGRIND`, and sources `../../../testprogs/blackbox/subunit.sh` for `testit`. It creates `$PREFIX/gentest.ignore` containing fields to ignore: `all_info.out.fname` and `internal_information.out.file_id`.

## Control Flow
After validating the argument count, the script assigns positional arguments, shifts them away, initializes `failed=0`, writes the ignore file, and invokes `testit "gentest"` with `//$SERVER/test1` and `//$SERVER/test2`, `--seed=1`, `--seedsfile=$PREFIX/gentest_seeds.dat`, `--num-ops=100`, the ignore file, domain, and two identical user credentials. It increments `failed` if `testit` fails, removes the ignore file, and exits with the failure count.

## State and Persistence Behavior
The wrapper creates a temporary ignore file and a persistent seed file under `PREFIX`. The remote side is mutated by `gentest` under its own test paths on the `test1` and `test2` shares. The script removes only the ignore file.

## Dependencies and Integration Points
It integrates the standalone `gentest` executable into Samba's blackbox test harness and depends on configured shares `test1` and `test2`, credentials, `BINDIR`, and subunit shell reporting.

## Risks
The test is destructive to the remote test shares. The same username/password is used for both user roles, which is intentional for this wrapper but limits multi-user coverage. Missing `PREFIX`, missing `BINDIR`, or absent test shares result in setup failures.

## Test Signals
The subunit `testit` result is the primary signal. A zero exit means `gentest` completed 100 deterministic operations without unignored divergence; nonzero means the differential generator or setup failed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/tests/test_gentest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/tests/test_locktest.sh -->
# sources/user-network-fs/samba/source4/torture/tests/test_locktest.sh

## Purpose
`test_locktest.sh` is a blackbox wrapper for the `locktest` executable. It runs deterministic locking behavior tests against two server shares and reports success or failure through Samba's subunit shell harness.

## Important APIs, Types, and Functions
The script expects `SERVER USERNAME PASSWORD DOMAIN PREFIX` plus optional extra arguments. It locates `locktest` under `$BINDIR`, optionally prefixes the command with `$VALGRIND`, and uses `testit` from `../../../testprogs/blackbox/subunit.sh`.

## Control Flow
The script validates the argument count, assigns positional variables, shifts the first five arguments, initializes `failed=0`, and calls `testit "locktest"` with `//$SERVER/test1`, `//$SERVER/test2`, `--num-ops=100`, domain, and `--user1="$DOMAIN\\$USERNAME%$PASSWORD"`. Any additional arguments are appended. The script exits with the accumulated failure count.

## State and Persistence Behavior
The wrapper itself writes no files despite accepting `PREFIX`. Remote test state is created by `locktest` on the two test shares, including lock and file operation state that the executable is responsible for cleaning up.

## Dependencies and Integration Points
It depends on a built `locktest` binary, two configured test shares, valid domain credentials, optional Valgrind integration, and the blackbox subunit helper.

## Risks
The script assumes both test shares exist and are safe for destructive locking tests. Because it passes only `user1`, coverage is tied to the default behavior of `locktest` for the second side. Any quoting or domain-format mismatch can prevent authentication.

## Test Signals
A zero exit indicates the lock operation sequence completed as expected. Nonzero exit reports either command setup failure or locktest-detected locking divergence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/tests/test_locktest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/tests/test_masktest.sh -->
# sources/user-network-fs/samba/source4/torture/tests/test_masktest.sh

## Purpose
`test_masktest.sh` is a blackbox wrapper for Samba's `masktest` executable. It exercises wildcard and filename mask behavior against a temporary SMB share path and emits the result through subunit.

## Important APIs, Types, and Functions
The script expects `SERVER USERNAME PASSWORD DOMAIN PREFIX` plus optional extra arguments. It resolves `masktest` from `$BINDIR`, supports `$VALGRIND`, and sources the standard blackbox `subunit.sh` to use `testit`.

## Control Flow
After argument validation, the script initializes variables and calls `testit "masktest"` with `//$SERVER/tmp`, `--num-ops=200`, `--dieonerror`, domain, and `-U"$USERNAME%$PASSWORD"`, followed by any extra arguments. Failures increment `failed`; the script exits with that value.

## State and Persistence Behavior
The wrapper writes no local files and does not use `PREFIX`. The `masktest` binary mutates the remote `tmp` share while generating and checking mask operations and is responsible for cleanup.

## Dependencies and Integration Points
It integrates `masktest` into the Samba blackbox suite and requires a built binary, a writable `tmp` share, credentials, and the blackbox subunit helper.

## Risks
The remote `tmp` share must be disposable. `--dieonerror` makes the test stop on the first detected mismatch, which is useful for CI but may reduce evidence from later generated operations. Authentication format differs from `test_locktest.sh` because it omits the domain prefix in `-U`.

## Test Signals
A zero exit indicates 200 mask operations completed without mismatch. Nonzero exit indicates a wrapper setup problem or masktest-detected wildcard/mask behavior failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/tests/test_masktest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/torture.c -->
# sources/user-network-fs/samba/source4/torture/torture.c

## Purpose
`torture.c` provides the small core registration layer for smbtorture modules. It owns global default torture settings, the root suite pointer, suite registration, and module initialization for static and shared smbtorture modules.

## Important APIs, Types, and Functions
The file defines `_PUBLIC_` globals `torture_numops`, `torture_entries`, `torture_failures`, `torture_seed`, and `torture_numasync`, plus `struct torture_suite *torture_root`. Public functions are `torture_register_suite()` and `torture_init()`.

## Control Flow
`torture_register_suite()` treats a NULL suite as success, lazily allocates `torture_root` with `talloc_zero()`, and adds the provided suite under the root with `torture_suite_add_suite()`. `torture_init()` expands static module prototypes, builds a static init array from `STATIC_smbtorture_MODULES`, loads shared modules named `smbtorture`, runs both static and shared init functions, frees the shared init array, and returns success.

## State and Persistence Behavior
The file creates process-lifetime test registry state in `torture_root` and stores default numeric settings used by many tests. Module initialization mutates this registry by calling each module's init function.

## Dependencies and Integration Points
It depends on the generic torture harness, Samba module loading, talloc, and generated static module macros. `smbtorture.c` calls `torture_init()`, while each suite module calls `torture_register_suite()`.

## Risks
If `torture_root` allocation fails, `torture_suite_add_suite()` receives NULL root state. Module init failures are not surfaced in the return value because `run_init_functions()` results are not checked here. Global defaults are shared across all tests in a process.

## Test Signals
Indirect signals include visible suites after initialization, successful module loading, and `smbtorture --list-suites` showing registered modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/torture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/unix/unix.c -->
# sources/user-network-fs/samba/source4/torture/unix/unix.c

## Purpose
`unix.c` registers the CIFS UNIX extensions torture suite. It groups the UNIX extension tests under the top-level suite name `unix`.

## Important APIs, Types, and Functions
The only function is `torture_unix_init(TALLOC_CTX *ctx)`. It creates a `struct torture_suite`, sets a human-readable description, and registers simple tests `whoami` and `info2` pointing to `torture_unix_whoami` and `unix_torture_unix_info2`.

## Control Flow
At module initialization time, `torture_unix_init()` creates the suite, attaches two simple tests, and calls `torture_register_suite()`. It converts the boolean registration result into `NT_STATUS_OK` or `NT_STATUS_UNSUCCESSFUL`.

## State and Persistence Behavior
The file only mutates the in-process torture suite registry. It creates no remote SMB state itself; the registered tests perform their own connections and cleanup.

## Dependencies and Integration Points
It depends on `torture/smbtorture.h` for registration and `torture/unix/proto.h` for test prototypes. The suite becomes discoverable and runnable through smbtorture after module initialization.

## Risks
Registration failure prevents both UNIX extension tests from being visible. Because this file is only a registry shim, incorrect prototype generation or missing linked test functions will surface as build failures.

## Test Signals
The expected signal is that `smbtorture ... unix.whoami` and `smbtorture ... unix.info2` are listed and runnable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/unix/unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/unix/unix_info2.c -->
# sources/user-network-fs/samba/source4/torture/unix/unix_info2.c

## Purpose
`unix_info2.c` tests the CIFS UNIX extension `SMB_QUERY_FILE_UNIX_INFO2` and related set/find operations. It verifies that file-info, path-info, and directory-search variants return consistent UNIX metadata and that `SMB_SFILEINFO_UNIX_INFO2` accepts or rejects file flag updates according to the server-advertised mask.

## Important APIs, Types, and Functions
The local `struct unix_info2` mirrors the UNIX_INFO2 fields: EOF, bytes, times, uid/gid, file type, device numbers, unique id, permissions, link count, create time, file flags, and flags mask. Important helpers are `connect_to_server()`, `check_unix_info2()`, `set_path_info2()`, `query_file_path_info2()`, `query_file_info2()`, `query_path_info2()`, `search_callback()`, `find_single_info2()`, `set_no_metadata_change()`, `verify_setinfo_flags()`, `create_file()`, `match_info2()`, and the exported `unix_torture_unix_info2()`.

## Control Flow
`connect_to_server()` opens an SMB1 client connection and sends `SMB_SET_CIFS_UNIX_INFO` through `smb_raw_trans2()` to enable UNIX capabilities such as POSIX ACLs, POSIX pathnames, fcntl locks, extended attributes, and POSIX path operations. `unix_torture_unix_info2()` unlinks any prior test file, creates `\smb_unix_info2.txt`, queries UNIX_INFO2 by file handle, queries it by path, compares the two, queries it through a `SMB_FIND_UNIX_INFO2` find-first search, compares again, then verifies flag-setting behavior.

`verify_setinfo_flags()` first reads the server's flags mask. It then iterates all 32 possible flag bits, sets `file_flags` to exactly one bit and `flags_mask` to include that bit, fills all unrelated metadata fields with no-change sentinels, and calls `set_path_info2()`. Bits included in the server mask must succeed and be observable afterward; unsupported bits must return `NT_STATUS_INVALID_PARAMETER`. Finally it verifies that a zero mask with all flags set is accepted as a no-op.

## State and Persistence Behavior
The test creates and deletes one file on the target share. It changes UNIX extension negotiation state on the SMB connection and temporarily changes file flags through UNIX_INFO2 setpathinfo. Cleanup closes the file handle, unlinks the file, closes the SMB connection, and frees the talloc context.

## Dependencies and Integration Points
The file uses SMB1 raw client APIs, Trans2, UNIX extension constants, command-line credentials, loadparm options, resolver/event contexts, and the generic torture assertion framework. It is registered by `unix.c` as `unix.info2`.

## Risks
The test requires a server implementing CIFS UNIX extensions; non-support or partial support will fail during negotiation or info levels. File flag behavior depends on backend filesystem capabilities, and the exhaustive 32-bit flag loop assumes unsupported flags are rejected exactly with `NT_STATUS_INVALID_PARAMETER`.

## Test Signals
Signals include successful UNIX extension negotiation, matching file/path/find metadata, valid `file_flags` constrained by `flags_mask`, accepted supported flag updates, rejected unsupported flag updates, and accepted no-op zero-mask updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/unix/unix_info2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/unix/whoami.c -->
# sources/user-network-fs/samba/source4/torture/unix/whoami.c

## Purpose
`whoami.c` tests the CIFS UNIX extension `SMB_QFS_POSIX_WHOAMI`. It verifies that the server reports the authenticated user's POSIX UID/GID, supplementary groups, SID list, mapping flags, and buffer truncation behavior consistently, optionally cross-checking SIDs against LDAP tokenGroups.

## Important APIs, Types, and Functions
The local `struct smb_whoami` stores mapping flags and mask, server UID/GID, GID and SID counts, SID byte count, reserved field, GID list, and SID list. Core helpers are `connect_to_server()`, `whoami_sid_parse()`, `smb_raw_query_posix_whoami()`, `test_against_ldap()`, and the exported `torture_unix_whoami()`.

## Control Flow
`torture_unix_whoami()` connects to the SMB server with command-line credentials and calls `smb_raw_query_posix_whoami()` with a large buffer. The query helper sends a Trans2 `TRANSACT2_QFSINFO` request with info level `SMB_QFS_POSIX_WHOAMI`, validates the fixed 40-byte response header, parses optional 64-bit GIDs, parses SIDs with `whoami_sid_parse()`, and verifies that counts and byte lengths consume the response exactly.

The main test checks the guest mapping flag if the server advertises `SMB_WHOAMI_GUEST`. If a torture `addc` setting is present, it connects to LDAP and `test_against_ldap()` compares the returned CIFS SID list with `tokenGroups`. On a DC it expects exact ordered equality; on a member server it filters domain SIDs before comparing. The final query uses a small max-data value (`0x40`) and expects the server to omit GID and SID lists while returning valid fixed fields.

## State and Persistence Behavior
The test does not create files. It creates an authenticated SMB session, optionally an LDAP connection, allocates parsed SID/GID arrays under talloc contexts, and disconnects the tree with `smbcli_tdis()` on success or failure.

## Dependencies and Integration Points
It depends on SMB1 raw Trans2 APIs, credentials, loadparm, resolver/event context, dom SID parsing, LDB, Samba DSDB helpers, LDAP wrapping, and UNIX extension constants. It is registered by `unix.c` as `unix.whoami`.

## Risks
The optional LDAP comparison is environment-sensitive: member servers and DCs report different SID sets, ordering assumptions can be brittle, and missing `addc` skips that deeper validation. The SID parser enforces maximum sub-authority count and response length, so malformed server responses fail fast. Small-buffer behavior must match the server's truncation contract.

## Test Signals
Signals include a valid fixed whoami header, zero reserved field, coherent GID/SID counts and byte lengths, guest flag consistency with credentials, optional LDAP tokenGroups alignment, and empty GID/SID lists when queried with the small response buffer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/unix/whoami.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/util.h -->
# sources/user-network-fs/samba/source4/torture/util.h

## Purpose
`util.h` declares shared SMB1 and general torture utility APIs used across Samba's torture tests. It also defines target-detection macros that let tests adapt expected behavior to Windows, Samba, and other server profiles selected on the smbtorture command line.

## Important APIs, Types, and Functions
Target macros include `TARGET_IS_WINXP`, `TARGET_IS_W2K3`, `TARGET_IS_W2K8`, `TARGET_IS_W2K12`, `TARGET_IS_WIN7`, `TARGET_IS_SAMBA3`, `TARGET_IS_SAMBA4`, `TARGET_IS_W2K16`, and `TARGET_IS_WINDOWS`; they read boolean `torture` settings from the context. Declared helpers cover directory setup, complex file/dir creation, wire string validation, all-info dumping, file attribute and sparse setting, EA checks, opening and closing SMB1 connections, connection-index selection from UNC lists, error checking, multi-process torture execution, adding SMB-specific tests to suites, secondary tree connects, privilege checks, and second-user credential construction.

## Control Flow
The header has no executable flow, but it defines the call surface used by many test files. Suite builders call `torture_suite_add_smb_multi_test()`, `torture_suite_add_2smb_test()`, and `torture_suite_add_1smb_test()` to wrap SMB connection setup around test callbacks. Tests call setup and creation helpers before exercising protocol behavior and use target macros to branch around known server differences.

## State and Persistence Behavior
The declared functions operate on SMB connection state, remote files/directories, EAs, privileges, and credentials. The macros read process-run loadparm settings set by `smbtorture.c`. `torture_user2_credentials()` consumes `torture:user2*` options documented in the comment block.

## Dependencies and Integration Points
The header depends on the generic torture harness and forward declarations for SMB client state, tree state, transport, and credentials. It is the shared interface between raw/basic SMB tests, the runner's target profile settings, and utility implementations elsewhere in `source4/torture`.

## Risks
Because these declarations are broadly consumed, signature changes have large compile-time impact. Target macros only check settings, so misspelled settings or unsupported new targets silently fall back to default behavior. Helpers that mutate server files must be used with safe test shares.

## Test Signals
Indirect signals include successful compilation of all consumers, correct target-specific skips or expected-status branches, reliable SMB connection setup/teardown, and helper-produced failures for setup, EA, privilege, or attribute mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/util.h -->
