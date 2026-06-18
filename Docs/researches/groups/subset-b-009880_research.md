# subset-b-009880 Research

Grouped research for the listed Samba torture sources. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_readdir_timestamp.c -->
# sources/user-network-fs/samba/source3/torture/test_readdir_timestamp.c

## Purpose
This file implements the `run_readdir_timestamp` smbtorture test. It stress-tests directory enumeration timestamp fidelity by creating many files through multiple SMB client connections, encoding each file's logical index into the low 16 bits of its last-write timestamp, and then verifying that `cli_list()` returns `file_info.mtime_ts` values matching the encoded filename index. The test is aimed at readdir/listing paths where timestamp metadata can be cached, rounded, reordered, or returned from a different metadata source than direct file operations.

## Important APIs, Types, And Functions
Key state types are `create_ts_state`, `create_ts_files_state`, `create_files_state`, and `list_cb_state`. The first three are tevent request state containers used to compose asynchronous file creation across one file, one client, and all clients respectively. `list_cb_state` accumulates the number of listed files and a boolean timestamp validation result.

The main async chain starts in `create_ts_send()`: it calls `cli_ntcreate_send()`, receives the handle in `create_ts_opened()`, adjusts the last-write time with `cli_setfileinfo_ext_send()`, waits 100 ms with `tevent_wakeup_send()`, writes a small payload with `cli_write_send()`, and marks the handle delete-on-close with `cli_nt_delete_on_close_send()`. `create_ts_recv()` returns the open file number so the test can keep handles alive until enumeration has completed.

`create_ts_files_send()` launches `num_files` `create_ts_send()` requests for one client. `create_files_send()` launches one `create_ts_files_send()` per SMB client. `list_cb()` parses the numeric suffix after the underscore in listed names with `smb_strtoull()` and compares it with the low 16 bits of `f->mtime_ts.tv_sec`.

## Control Flow
`run_readdir_timestamp()` opens `torture_nprocs` connections, creates or reuses the `readdir_ts` directory, initializes a tevent context, and dispatches `create_files_send()` for `torture_nprocs * torture_numops` files. The asynchronous fan-out means many creates and metadata updates are in flight concurrently. After `tevent_req_poll_ntstatus()` completes and `create_files_recv()` returns the handle arrays, the test enumerates `readdir_ts\*` through `cli_list()`. It then checks both the count and the timestamp match flag before freeing the client array, which also releases the open handles and triggers delete-on-close cleanup.

## State And Persistence Behavior
The test creates transient files named `readdir_ts/<client_index>_<file_index>`. It intentionally leaves file handles open during the listing phase and sets delete-on-close rather than deleting immediately. Persistent state is limited to the test directory and any files left behind if the process aborts before handle cleanup. Timestamp state is deliberately mutated: the test preserves most of the server-returned last-write time but overwrites the low 16 bits of `tv_sec` with the expected index.

## Dependencies And Integration Points
The file depends on Samba client and event infrastructure: `cli_ntcreate_send/recv`, `cli_setfileinfo_ext_send/recv`, `cli_write_send/recv`, `cli_nt_delete_on_close_send/recv`, `cli_list`, `samba_tevent_context_init`, `tevent_req_*`, and the global torture knobs `torture_nprocs` and `torture_numops`. It integrates with smbtorture through the exported `run_readdir_timestamp()` entry point and with the SMB server under test through normal SMB create, setinfo, write, delete-on-close, mkdir, and directory listing operations.

## Risks And Edge Cases
The test is timing-sensitive because it waits 100 ms between setting the timestamp and writing file data. That wait is meant to avoid accidental timestamp equality or server timestamp coalescing, but slow or coarse timestamp backends can still affect results. `create_ts_written()` calls `tevent_req_nterror(subreq, status)` instead of reporting on the parent `req`, which looks suspicious because failures could be recorded on the just-freed subrequest path rather than the outer request. The filename parser ignores entries without an underscore or numeric suffix, so unexpected files in `readdir_ts` can affect the found count only when they look like test files. Runs against shares with preexisting matching files or failed prior cleanup may produce count mismatches.

## Test Signals
Success requires all async create/setinfo/write/delete-on-close operations to complete, `cli_list()` to return OK, `state.found` to equal `torture_nprocs * torture_numops`, and every listed test file to have low timestamp bits matching its filename suffix. Diagnostic output names failed SMB operations, expected and actual counts, and timestamp mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_readdir_timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_rpc_samr.c -->
# sources/user-network-fs/samba/source3/torture/test_rpc_samr.c

## Purpose
This is a focused cmocka regression test for SAMR password-complexity command expansion, specifically `check_password_complexity_internal()`. It validates how a configured command string containing `%u` is expanded for a candidate username, including shell quoting, dangerous characters, option-looking names, Unicode input, fallback substitution, and invalid principal-name rejection. Many cases are explicitly tied to hardening around command injection, including the fallback marker `__CVE-2026-4408_FallbackUsername__`.

## Important APIs, Types, And Functions
`struct cmd_expansion` defines each test vector: `lp_cmd`, `username`, expected `result_cmd`, and expected `NTSTATUS`. The `expansions[]` table is the main test specification. `setup_talloc_context()` and `teardown_talloc_context()` provide a per-suite talloc root through cmocka state. `test_expansions()` iterates the vector table and calls `check_password_complexity_internal(mem_ctx, t.lp_cmd, t.username, &result_cmd)`.

The code uses `NT_STATUS_IS_OK()`, `NT_STATUS_EQUAL()`, and `nt_errstr()` for status handling, `assert_int_equal()` for cmocka assertions, and conditional `debug_message()` output. `main()` registers the single unit test and switches to Subunit output when stdout is not a terminal.

## Control Flow
The cmocka runner creates a talloc context, runs `test_expansions()`, and frees the context. For each table row, the test invokes the SAMR utility under test. If both expected and actual statuses are success, the generated command must exactly match `result_cmd`. If the actual status equals the expected failure status, the case passes without comparing command output. Any status mismatch or command mismatch fails the test immediately through cmocka assertions.

## State And Persistence Behavior
The test has no persistent runtime state. All allocations are under the cmocka-provided talloc context and are freed by `teardown_talloc_context()`. The only external state is stdout/stderr-style test reporting. The command strings are not executed; the test validates expansion output only.

## Dependencies And Integration Points
The file includes generated SAMR NDR headers and `rpc_server/samr/srv_samr_util.h`, which exposes the internal password-complexity helper. It depends on cmocka, talloc, and Samba NTSTATUS utilities. It integrates as a standalone unit-test executable with its own `main()`, unlike many smbtorture tests that export `run_*` entry points.

## Risks And Edge Cases
The table is security-sensitive because it encodes expected sanitization behavior for metacharacters such as quotes, backslashes, redirection, command substitution, wildcard characters, leading dashes, spaces, percent expansion, and non-ASCII usernames. A legitimate change in quoting policy must update many exact expected strings. `SAMR_DEBUG_VERBOSE` is set to true, so verbose messages are enabled by default; non-tty output is mitigated by Subunit mode but local terminal output can be noisy. The test validates command construction, not shell execution behavior, so shell-specific semantics remain outside its coverage.

## Test Signals
Passing means every command expansion either matches the exact expected command string or returns the exact expected NTSTATUS. Failures print the vector index, input command, username, actual status, expected status, and mismatched command strings, which gives direct repair signals for the sanitization logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_rpc_samr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_rpc_scale.c -->
# sources/user-network-fs/samba/source3/torture/test_rpc_scale.c

## Purpose
This file implements `run_rpc_scale`, an smbtorture load test for repeated asynchronous DCE/RPC pipe setup and basic spoolss RPC calls across multiple SMB connections. It repeatedly opens the `spoolss` named pipe, binds anonymously, calls `EnumPrinters`, closes the RPC client, and loops for `torture_numops` iterations per connection. The intent is to exercise connection scaling, named-pipe open/bind teardown behavior, RPC client lifetime management, and server stability under repeated RPC setup.

## Important APIs, Types, And Functions
`struct rpc_scale_one_state` holds one client's event context, `cli_state`, iteration count, active `rpc_pipe_client`, spoolss response buffer, and `EnumPrinters` result fields. `rpc_scale_one_send()` starts one per-client loop. Its callbacks are `rpc_scale_one_opened()`, `rpc_scale_one_bound()`, and `rpc_scale_one_listed()`. `rpc_scale_one_recv()` returns the final NTSTATUS.

`struct rpc_scale_state` aggregates all per-client requests. `rpc_scale_send()` starts one `rpc_scale_one_send()` per element in the talloc-sized `clis` array, and `rpc_scale_done()` completes once all have succeeded. `run_rpc_scale()` is the exported smbtorture entry point.

Important external APIs include `rpc_pipe_open_np_send/recv`, `rpccli_anon_bind_data()`, `rpc_pipe_bind_send/recv`, `dcerpc_spoolss_EnumPrinters_send/recv`, `smbXcli_conn_remote_name()`, `data_blob_talloc()`, and tevent request helpers.

## Control Flow
`run_rpc_scale()` allocates `torture_nprocs` client slots, opens each SMB connection, initializes a tevent context, and dispatches `rpc_scale_send()`. Each per-client request opens the spoolss named pipe, creates anonymous bind auth data, binds, builds a server string from the remote SMB name, allocates a 4096-byte response buffer, and calls `EnumPrinters` at level 1 with `PRINTER_ENUM_LOCAL`. On a successful WERROR result, it frees `state->rpccli`, decrements `num_iterations`, and either completes or starts another open/bind/list cycle. The aggregate request completes only when all clients finish their loops.

## State And Persistence Behavior
The test does not create durable server-side data. Its state is connection-oriented: SMB connections, RPC pipe handles, bind state, allocated response buffers, and returned printer metadata. Each iteration explicitly frees the RPC client, which triggers a synchronous close noted by the in-code comment. All local allocations are tied to the talloc stack frame or request states and are freed at function exit.

## Dependencies And Integration Points
This source depends on Samba RPC client infrastructure, generated spoolss client stubs, SMB named-pipe transport, tevent, and global torture parameters. It integrates with any server exposing the spoolss pipe over SMB named pipes. The test assumes anonymous binding to spoolss and a successful `EnumPrinters` call are acceptable in the target test environment.

## Risks And Edge Cases
The test is intentionally heavy: total pipe open/bind/list cycles are `torture_nprocs * torture_numops`. The synchronous close during `TALLOC_FREE(state->rpccli)` can serialize or block progress despite the async outer structure. `rpc_scale_one_bound()` constructs the server name with a trailing newline (`"\\%s\n"`), which is unusual and may be either intentional compatibility behavior or a typo-like quirk worth preserving until understood. A too-small 4096-byte buffer may cause non-OK spoolss WERRORs on servers with many printers if the call does not transparently handle `needed` sizing.

## Test Signals
Success requires every SMB connection to open, every named-pipe open and bind to succeed, every `EnumPrinters` RPC transport status to be OK, and every spoolss WERROR result to be OK. Failures are reported as NTSTATUS strings from `rpc_scale_send` or `rpc_scale_recv`, making this primarily a stability/load signal rather than a detailed functional printer enumeration test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_rpc_scale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_smb1_dfs.c -->
# sources/user-network-fs/samba/source3/torture/test_smb1_dfs.c

## Purpose
This large smbtorture source is a raw SMB1 DFS behavior suite. It verifies how an SMB1 DFS share parses pathnames and search patterns, and how classic SMB1 commands behave when the apparent path includes DFS server/share components. The tests intentionally use low-level SMB1 request builders rather than the higher-level `cli_*` pathname wrappers because the target is server-side DFS path parsing and protocol compatibility, especially behavior observed against Windows.

The exported entry points are `run_smb1_dfs_paths`, `run_smb1_dfs_search_paths`, `run_smb1_dfs_operations`, and `run_smb1_dfs_check_badpath`.

## Important APIs, Types, And Functions
The shared helpers are `get_smb1_crtime()`, `smb1_crtime_matches()`, and `smb1_dfs_delete()`. They use `smb1cli_ntcreatex()`, `cli_qfileinfo_basic()`, `cli_nt_delete_on_close()`, and `smb1cli_close()` to identify objects by create time and clean up test artifacts through file handles.

Rename and hardlink coverage is split by protocol mechanism:
- `smb1_mv_send()/smb1_mv()` builds an `SMBmv` request.
- `smb1_setpathinfo_send()/smb1_setpathinfo()` sends `SMBtrans2` `TRANSACT2_SETPATHINFO` with `SMB_FILE_RENAME_INFORMATION` or `SMB_FILE_LINK_INFORMATION`.
- `smb1_ntrename_send()/smb1_ntrename()` builds `SMBntrename` with `RENAME_FLAG_RENAME` or `RENAME_FLAG_HARD_LINK`.
- `smb1_setfileinfo_send()/smb1_setfileinfo()` sends handle-based set-info data for rename/link levels.

Search coverage uses `smb1_findfirst()`, `calc_next_entry_offset()`, `get_filename()`, and `test_smb1_findfirst_path()` to issue a one-shot `TRANSACT2_FINDFIRST` and parse `SMB_FIND_FILE_BOTH_DIRECTORY_INFO` records.

Operation coverage includes raw wrappers and tests for `SMBunlink`, `SMBmkdir`, `SMBrmdir`, `NT_CREATE_ANDX`, `NT_TRANSACT_CREATE`, `SMBopenX`, `SMBopen`, `SMBcreate`, `SMBmknew`, `SMBgetatr`, `SMBsetatr`, `SMBcheckpath`, `SMBctemp`, and `TRANSACT2_QPATHINFO`.

## Control Flow
Every exported `run_*` function opens a torture connection, verifies both connection-level DFS support with `smbXcli_conn_dfs_supported()` and tree-connect DFS-share status with `smbXcli_tcon_is_dfs_share()`, then runs a set of low-level checks. If DFS support is absent, the test reports the server/share limitation and returns false rather than trying non-DFS behavior.

`run_smb1_dfs_paths()` starts with cleanup, constructs the official DFS root path as `\\<remote_name>\\<share>`, records its create time, and checks that many abbreviated or malformed server/share prefixes resolve to the share root. It verifies expected failures for deeper nonexistent paths, invalid share-name colon handling, and then creates `BAD\BAD\file` to test rename and hardlink behavior through `SMBmv`, setpathinfo, setfileinfo, and ntrename variants. Create-time comparisons prove whether operations addressed the intended object or just the share root.

`run_smb1_dfs_search_paths()` creates a file, captures a baseline directory listing for `SERVER\SHARE\*`, and verifies that equivalent DFS search patterns such as `\SERVER\SHARE\*`, `*`, `\*`, and `\SERVER\*` return the same names in the same order.

`run_smb1_dfs_operations()` executes a broad command matrix. For many SMB1 commands, short paths like `file` or `\BAD\file` are expected to resolve to the DFS root and therefore fail as directory operations or report root directory attributes, while full DFS-style paths like `\BAD\BAD\file` are expected to operate on the test file. It also captures known Windows-compatible oddities, such as `SMBctemp` returning `NT_STATUS_FILE_IS_A_DIRECTORY` for all tested DFS-share variants.

`run_smb1_dfs_check_badpath()` isolates the Bug 15419 regression by checking that `SMBcheckpath` on `\x//\/` succeeds.

## State And Persistence Behavior
The suite mutates the connected DFS share by creating and deleting temporary files, directories, renamed files, and hardlinks under paths such as `\BAD\BAD\file`, `\BAD\BAD\dir`, and command-specific names. Cleanup is best-effort and appears at the beginning and end of most tests. Many cleanup calls use delete-on-close through `smb1_dfs_delete()`, so leaked handles or early process termination can leave artifacts behind. No local persistent state is written, but the remote share contents and metadata are used as the test oracle.

## Dependencies And Integration Points
The file depends on Samba's SMB1 client internals (`smb1cli_ntcreatex`, `smb1cli_close`, raw `cli_smb`, `cli_smb_send`, `cli_trans`, `cli_trans_send`, request chaining, and byte-string marshalling helpers), talloc, tevent, NTSTATUS/WERROR utilities, time helpers, and generated protocol constants. It integrates with smbtorture via exported `run_*` functions and with the global torture connection settings (`host`, `share`, credentials, and related globals). It also uses Windows protocol behavior comments as compatibility expectations for Samba server behavior.

## Risks And Edge Cases
This test suite is sensitive to the exact server behavior of SMB1 DFS path normalization. Several expected statuses are intentionally surprising: short paths can map to the share root, invalid server-name characters can be ignored, only `:` is treated as invalid in a DFS share name, setpathinfo rename/link with separators returns `NT_STATUS_NOT_SUPPORTED`, handle-based setfileinfo rename/link returns `NT_STATUS_UNSUCCESSFUL`, and ctemp returns directory errors. These are compatibility constraints and are easy to break with cleanup refactors in path parsing.

The file contains hand-built SMB parameter/data blocks, UCS-2 conversion, manual info-level layouts, and manual directory-entry parsing. Risks include off-by-one string lengths, Unicode/null-termination differences, incorrect returned-handle extraction, and response parser assumptions. One suspicious detail is `smb1_nttrans_create()` reading the returned fnum from `param` rather than `rparam`; if intentional, it deserves a comment, and if not, it may reduce cleanup reliability. Tests also assume a writable, empty-enough DFS share and SMB1 availability, which many modern environments disable.

## Test Signals
The strongest signal is exact NTSTATUS compatibility for each raw SMB1 operation and exact object identity validation through create-time comparisons. Search tests add listing equivalence and parser validation for `SMB_FIND_FILE_BOTH_DIRECTORY_INFO`. Diagnostic output includes source line, operation, path, expected status, and actual status. Passing the suite indicates Samba's SMB1 DFS server path handling is aligned with the captured Windows-compatible behavior across open/create/delete/rename/link/search/attribute/checkpath/query operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_smb1_dfs.c -->
