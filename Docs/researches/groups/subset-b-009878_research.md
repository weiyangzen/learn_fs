# subset-b-009878 research

Grouped research for Samba `source3/torture` VFS, SMB torture, messaging, nbench, passdb, and local regression-test sources. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/cmd_vfs.c -->
# sources/user-network-fs/samba/source3/torture/cmd_vfs.c

## Purpose
`cmd_vfs.c` provides the command table for the `vfstest` interactive shell. It lets a developer load VFS modules and call Samba's VFS entry points directly against a test `connection_struct`, making it a manual probe for filesystem modules, ACL paths, named streams, xattrs, directory iteration, and create/open behavior.

## Important APIs, types, and functions
The file exports `vfs_commands[]`, a `struct cmd_set` table consumed by `vfstest.c`. Command handlers all take `struct vfs_state *vfs`, `TALLOC_CTX *mem_ctx`, `argc`, and `argv`, then return `NTSTATUS`. Important handlers include `cmd_load_module`, `cmd_connect`, `cmd_open`, `cmd_close`, `cmd_read`, `cmd_write`, `cmd_stat`/`cmd_fstat`/`cmd_lstat`, xattr handlers, NT ACL handlers, POSIX ACL handlers, `cmd_translate_name`, and `cmd_create_file`. It uses Samba abstractions such as `files_struct`, `smb_filename`, `vfs_open_how`, `synthetic_smb_fname*`, `synthetic_pathref`, `metadata_fsp`, and many `SMB_VFS_*` dispatch macros.

## Control flow
The shell dispatches a parsed command to the matching `cmd_*` function. Path-oriented commands synthesize `smb_filename` objects relative to `vfs->conn->cwd_fsp`, then call the matching VFS hook. Open creates a minimal `files_struct`, resolves stream base objects when needed, opens with `SMB_VFS_OPENAT`, stats the handle, initializes flags and identity fields, and stores the handle in `vfs->files[fd]`. ACL and xattr commands generally open a path reference first, then call fsp-based VFS methods. The shared buffer commands (`populate`, `read`, `write`, `showdata`) feed simple data through later file operations.

## State and persistence behavior
Runtime state lives in `vfs_state`: loaded module chain, open directory handle, `files[]` table, and the shared data buffer. Persistent effects are whatever the invoked VFS module does to the backing share: file creation, deletion, rename, xattr changes, ACL changes, timestamps, symlinks, hard links, and truncation. The code does not maintain durable metadata of its own.

## Dependencies and integration points
This file is built into the `vfstest` binary with `vfstest.c` and `vfstest_chain.c`. It integrates with smbd VFS internals, Samba filename conversion, ACL/security descriptor helpers, passdb machine SID lookup for SDDL encoding, and directory helpers from `source3/smbd/dir.h`.

## Risks and test signals
Many commands trust numeric argv indexes and only some validate `fd < 1024`; bad manual input can dereference missing `vfs->files[fd]`. The command intentionally bypasses full SMB request semantics, so it is best as a VFS hook signal, not as a complete client-behavior test. It is valuable for reproducing VFS module crashes, especially ACL, xattr, pathref, stream, translate-name, and `SMB_VFS_CREATE_FILE` edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/cmd_vfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/denytest.c -->
# sources/user-network-fs/samba/source3/torture/denytest.c

## Purpose
`denytest.c` validates classic SMB1 open deny-mode semantics. It runs large expected-result matrices for combinations of access mode, deny mode, executable/non-executable file name, and one-connection versus two-connection opens, then checks whether a second handle can be opened, read, and written.

## Important APIs, types, and functions
The central data type is `enum deny_result` (`A_X`, `A_0`, `A_R`, `A_W`, `A_RW`) describing first-open failure, second-open failure, or read/write capability. `denytable1[]` and `denytable2[]` encode expected results. `torture_denytest1()` tests two opens on one `cli_state`; `torture_denytest2()` tests two separate `cli_state` connections. Helper functions `denystr`, `openstr`, `resultstr`, and `progress_bar` make output readable.

## Control flow
Each test opens a torture connection, creates two files (`.dat` and `.exe`), and iterates the table. For each row it opens the first handle with `mode1/deny1`, opens the second handle with `mode2/deny2`, then if both succeed attempts a one-byte `cli_read` and `cli_writeall` through the second handle. The observed aggregate result is compared to the table, and mismatches are printed unless `torture_showall` requests all rows.

## State and persistence behavior
The test temporarily creates `\denytest1.dat`, `\denytest1.exe`, `\denytest2.dat`, and `\denytest2.exe`, writes their names into them, opens and closes many SMB handles, then unlinks the files. No durable state is intended after cleanup.

## Dependencies and integration points
The file is part of the `smbtorture3` binary and is declared in `torture/proto.h`. It depends on `torture_open_connection`, `torture_close_connection`, `cli_openx`, `cli_read`, `cli_writeall`, `cli_close`, and `cli_unlink`.

## Risks and test signals
Deny-mode behavior is legacy and protocol-sensitive; expected outcomes differ for same-session versus cross-session opens and for DOS executable handling. The table is the main oracle, so changes must be deliberate. Failures indicate regressions in share-mode conflict resolution, DOS deny-mode mapping, or read/write access enforcement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/denytest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/locktest2.c -->
# sources/user-network-fs/samba/source3/torture/locktest2.c

## Purpose
`locktest2.c` is a standalone byte-range lock comparator. It runs randomized lock, unlock, and reopen operations against two SMB shares and corresponding local/NFS paths, then verifies both servers produce identical success/failure behavior.

## Important APIs, types, and functions
`struct record` captures one randomized operation: lock type selector, action selector, connection, file index, filesystem type, range start/length, and whether the record is needed for minimized replay. Core helpers are `try_open`, `try_close`, `try_lock`, `try_unlock`, `connect_one`, `reconnect`, `open_files`, `close_files`, `test_one`, `retest`, and `test_locks`. `main()` parses `-U`, `-s`, `-o`, `-u`, `-a`, `-A`, and `-O`.

## Control flow
The program creates two SMB connections per server and opens two handles per connection for both SMB and NFS/local filesystem paths. It pre-generates `numops` random records, executes each operation against server 0 and server 1, and fails if the boolean result differs. If `-A` analysis mode is active, it repeatedly removes unneeded records to minimize a failing sequence, then replays with verbose lock-table printing through `brl_forall`.

## State and persistence behavior
State is in the `recorded` array, `cli` connection matrix, `fnum` handle matrix, global options, and Samba's readonly locking database access. It creates or reopens `\locktest.dat` on both shares and removes it during cleanup. NFS/local paths are converted from SMB-style backslashes before POSIX `open`/`fcntl`.

## Dependencies and integration points
The binary links against Samba client libraries, loadparm, credentials, `share_mode_lock`/BRL inspection, and POSIX file locking. It is listed separately in `wscript_build`, not just inside `smbtorture3`.

## Risks and test signals
Randomized tests depend on a seed; logs print the seed for reproduction. SMB and NFS lock semantics are not identical in all deployments, so mismatches can be environmental. The minimized replay path is a strong signal for subtle BRL bugs, lock-range overlap errors, reconnect cleanup problems, and oplock interaction when `-O` is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/locktest2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/mangle_test.c -->
# sources/user-network-fs/samba/source3/torture/mangle_test.c

## Purpose
`mangle_test.c` stress-tests Samba's 8.3 short-name mangling. It creates random long names, queries alternate short names, deletes by short name, recreates by short name, and deletes by long name, while tracking short-name collisions.

## Important APIs, types, and functions
`torture_mangle()` is the exported test. `gen_name()` builds biased random names under `\mangle_test` with common prefixes, extension lengths, and tricky characters. `test_one()` performs the create/query/delete/recreate/delete cycle. A process-local internal TDB maps generated short names to long names to detect collisions.

## Control flow
The test opens one SMB connection, creates a clean `\mangle_test` directory, opens a long-name file with `O_EXCL`, calls `cli_qpathinfo_alt_name`, unlinks via the returned short name, recreates the file via the short-name path, then unlinks via the original long-name path. Every 100 iterations it prints collision and failure statistics.

## State and persistence behavior
The only durable server state is the temporary directory tree and files, removed by `torture_deltree` before and after the run. Local transient state is the internal TDB plus `total`, `collisions`, and `failures` counters.

## Dependencies and integration points
The file uses Samba SMB1 client calls, `torture_open_connection`, `torture_deltree`, TDB utility helpers, and `torture_numops` from `torture.c`. It is registered as the `MANGLE` torture operation through `proto.h` and `torture.c`.

## Risks and test signals
The test intentionally amplifies collision-prone names, so collision reports are diagnostic rather than automatically fatal. Actual failures are inability to unlink/recreate through equivalent short/long names. It is a regression signal for mangling algorithms, case handling, alternate-name lookup, and directory cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/mangle_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/msg_sink.c -->
# sources/user-network-fs/samba/source3/torture/msg_sink.c

## Purpose
`msg_sink.c` is a standalone messaging throughput sink. It prints its `server_id`, continuously receives `MSG_SMB_NOTIFY` messages, and periodically prints the number received.

## Important APIs, types, and functions
The file uses tevent request patterns with `sink_send`/`sink_done`/`sink_recv`, `prcount_send`/`prcount_waited`/`prcount_recv`, and `msgcount_send`/`msgcount_sunk`/`msgcount_printed`/`msgcount_recv`. `struct sink_state`, `struct prcount_state`, and `struct msgcount_state` hold event loop, messaging context, interval, and count pointers.

## Control flow
`main()` loads global Samba configuration, initializes a tevent context and messaging context, prints the current `server_id`, starts `msgcount_send`, then polls forever. `msgcount_send` starts two independent child requests: one recurring `messaging_read_send` chain that increments the count per message, and one recurring timer that prints the count each second.

## State and persistence behavior
The only state is in memory: the messaging context registration/state, the count, and active tevent requests. It does not write durable files, but it participates in Samba's messaging transport and therefore depends on local messaging socket/TDB infrastructure.

## Dependencies and integration points
It includes `messages.h`, `server_id.h`, and `tevent_unix.h`, and is built as the `msg_sink` binary. It pairs naturally with `msg_source.c`, which accepts the printed destination id.

## Risks and test signals
The request loops are intentionally non-terminating unless an error occurs. A stalled count, `messaging_read_recv` error, or timer allocation failure points to messaging delivery, event-loop, or local messaging database problems. It is a throughput and liveness tool rather than a pass/fail unit test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/msg_sink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/msg_source.c -->
# sources/user-network-fs/samba/source3/torture/msg_source.c

## Purpose
`msg_source.c` is a standalone message generator for Samba's internal messaging system. It repeatedly sends fixed-size `MSG_SMB_NOTIFY` buffers to a destination `server_id` supplied on the command line.

## Important APIs, types, and functions
`struct source_state` stores the tevent context, messaging context, message type, interval, and destination id. `source_send()` starts a recurring wakeup request, `source_waited()` sends one message and arms the next timer, and `source_recv()` returns any stored Unix error. `main()` handles argument parsing, context setup, id parsing, and polling.

## Control flow
After loading config and initializing messaging, `main()` gets its own id to provide the correct virtual node number, parses the destination with `server_id_from_string`, starts a `source_send` loop with a 10 ms interval, and polls the request. Each timer callback sends a 200-byte zeroed buffer via `messaging_send_buf`.

## State and persistence behavior
The program has no durable state. In-memory state consists of the active tevent request and destination id. It emits traffic into Samba's local messaging subsystem.

## Dependencies and integration points
It is built as `msg_source` and is designed to target the id printed by `msg_sink`. It depends on `messages.h`, `server_id` helpers, `tevent_wakeup_send`, and Samba config loading.

## Risks and test signals
Invalid destination ids are rejected up front. The send return value is not checked in the callback, so the primary observable signal is whether the sink count increases. It is useful for load/liveness testing and less useful for precise delivery accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/msg_source.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/msgtest.c -->
# sources/user-network-fs/samba/source3/torture/msgtest.c

## Purpose
`msgtest.c` is an older standalone internal messaging test and speed probe. It sends `MSG_PING` messages to another process and to itself, counts `MSG_PONG` replies, and reports throughput.

## Important APIs, types, and functions
The important callback is `pong_message`, registered for `MSG_PONG`, which increments global `pong_count`. `main()` initializes locale, logging, loadparm, tevent, and messaging; parses `<pid> <count>`; registers the callback; sends messages via `messaging_send` and `messaging_send_buf`; and drives `tevent_loop_once`.

## Control flow
The first phase sends `n` pings to the given PID and loops until `pong_count` reaches the sent count. The second phase sends both empty and buffered pings to itself and loops until two replies per iteration arrive. The final speed phase sends paired buffered/unbuffered pings for `n` seconds while keeping outstanding pings bounded, then waits up to 30 seconds for replies.

## State and persistence behavior
State is limited to `pong_count`, local tevent/messaging contexts, and transient message queues. No durable data is written.

## Dependencies and integration points
It exercises Samba's process messaging APIs and expects a peer that replies to `MSG_PING` with `MSG_PONG`, normally an smbd/nmbd-style Samba process. It uses `pid_to_procid` and `messaging_server_id` for addressing.

## Risks and test signals
The test can hang or undercount if the peer is not running, not responding to ping, or the event loop stops. Failure messages distinguish local self-delivery count failures from remote ping loss. Throughput output is approximate and environment-dependent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/msgtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/nbench.c -->
# sources/user-network-fs/samba/source3/torture/nbench.c

## Purpose
`nbench.c` implements the newer asynchronous `NBENCH2` replay engine for `smbtorture3`. It reads `client.txt`, parses scripted SMB operations and expected statuses, issues asynchronous client calls, and fails on unexpected NTSTATUS results.

## Important APIs, types, and functions
`struct nbench_state` holds the event loop, `cli_state`, client-name substitution string, input file, open-file table, and optional bandwidth callback. `struct nbench_cmd_struct` stores parsed parameters, expected status, and `enum nbench_cmd`. `nbench_parse`, `nbench_cmd_send`, `nbench_cmd_done`, `status_wrong`, `nbench_send`, `nbench_done`, and `run_nbench2` are the key functions.

## Control flow
`run_nbench2()` opens `client.txt`, creates a tevent context, opens one SMB connection, and polls an `nbench_send` request. The replay loop reads one line, tokenizes it with shell-style splitting, converts the trailing status token, maps the command name, and currently implements async handlers for `NTCreateX`, `Close`, `Mkdir`, and `QUERY_PATH_INFORMATION`. Successful creates add an `ftable` entry; closes remove it. EOF completes the parent request.

## State and persistence behavior
Runtime state includes the open-file linked list and any files/directories created by replayed operations. Script path names replace `client1` with the configured client name. Persistent server-side state depends on the script and is not fully cleaned by this file.

## Dependencies and integration points
It uses Samba async client APIs (`cli_ntcreate_send`, `cli_close_send`, `cli_mkdir_send`, `cli_qpathinfo_send`) and tevent NTSTATUS helpers. It is registered as `NBENCH2` in the torture harness; the older `nbio.c` path supports classic generated replay functions.

## Risks and test signals
Only a subset of parsed commands is implemented; unsupported commands return `NT_STATUS_NOT_IMPLEMENTED`. The expected-status check intentionally converts unexpected success into `NT_STATUS_INVALID_NETWORK_RESPONSE`. Missing `client.txt` or unsupported trace content makes the test fail before exercising server behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/nbench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/nbio.c -->
# sources/user-network-fs/samba/source3/torture/nbio.c

## Purpose
`nbio.c` provides older synchronous SMB operation primitives used by generated nbench-style torture scripts. It manages a per-process SMB connection, a local handle table, shared-memory throughput counters, and recursive cleanup helpers.

## Important APIs, types, and functions
The exported API is declared in `proto.h`: `nbio_total`, `nb_alarm`, `nbio_shmem`, `nb_setup`, `nb_unlink`, `nb_createx`, `nb_writex`, `nb_readx`, `nb_close`, `nb_rmdir`, `nb_rename`, `nb_qpathinfo`, `nb_qfileinfo`, `nb_qfsinfo`, `nb_findfirst`, `nb_flush`, `nb_deltree`, and `nb_cleanup`. Local state includes `ftable[MAX_FILES]`, global `struct cli_state *c`, `children` shared counters, `buf`, and `nb_start`.

## Control flow
The harness allocates shared memory with `nbio_shmem`, forks clients, calls `nb_setup` per client, and generated script code invokes the operation wrappers. Each wrapper translates a logical handle to an SMB fnum, performs the corresponding `cli_*` call, updates byte counters for reads/writes, and exits on unexpected failures. `nb_alarm` periodically prints aggregate throughput from all children.

## State and persistence behavior
Persistent server-side state consists of files and directories created by the replay. `nb_deltree` recursively lists and removes tree contents, while `nb_cleanup` removes the `clients` directory and marks the child done. Local shared memory tracks bytes, line number, and completion status.

## Dependencies and integration points
The file depends on `torture.c` globals (`line_count`, `nbio_id`) and Samba SMB client APIs. It complements generated load files and the `run_nbench` multiprocess harness in `torture.c`.

## Risks and test signals
Most wrapper failures call `exit(1)`, so this code is intentionally harsh. Handle-table exhaustion, stale logical handles, mismatched read sizes, or cleanup failures are strong test signals. `nb_flush` appears to pass the table index rather than the stored fd, so flush coverage should be interpreted cautiously.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/nbio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/pdbtest.c -->
# sources/user-network-fs/samba/source3/torture/pdbtest.c

## Purpose
`pdbtest.c` is a standalone passdb backend validation utility. It creates a synthetic Samba account, verifies fields round-trip through a selected passdb backend, checks NTLM authentication/session-key behavior, and optionally tests trusted-domain persistence.

## Important APIs, types, and functions
`samu_correct()` compares many `struct samu` fields: usernames, account control, password hashes, password history, logon times, profile/home/script paths, logon hours, and SIDs. `test_auth()` builds NTLM challenge/response data and compares session keys from `check_sam_security_info3`, auth3, and winbind when available. `test_trusted_domains()` exercises `set_trusted_domain`, `get_trusted_domain`, and `del_trusted_domain`.

## Control flow
`main()` initializes Samba command-line/config handling, chooses `--backend` or `lp_passdb_backend()`, gets a Unix user (default `nobody`), builds a `samu`, fills account/profile/password/time fields, adds it through the backend, reads it back, validates it, authenticates it, deletes it, and then tests trusted domains if the backend advertises `PDB_CAP_TRUSTED_DOMAINS_EX`.

## State and persistence behavior
The utility writes a real passdb account and deletes it before exit. It may also write and delete a trusted-domain entry named `trustdom`. Random password/hash/history data is generated per run. Failures during add/read/delete can leave backend state behind.

## Dependencies and integration points
It integrates with passdb modules, Samba account-policy APIs, auth subsystem helpers, generated NDR DRS trust blobs, dom_sid utilities, tsocket, and wbclient. `wscript_build` builds it as the standalone `pdbtest` binary.

## Risks and test signals
Because it mutates the configured passdb backend, it must be run only against test backends. A pass indicates both persistence and authentication interoperability for common fields. It explicitly tolerates missing winbind (`WBC_ERR_WINBIND_NOT_AVAILABLE`) but treats other winbind/auth mismatches as failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/pdbtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/proto.h -->
# sources/user-network-fs/samba/source3/torture/proto.h

## Purpose
`proto.h` is the source3 SMB torture harness declaration header. It exposes test entry points and helper APIs across the many `source3/torture` compilation units.

## Important APIs, types, and functions
The header includes `source3/include/client.h` and `source3/libsmb/proto.h`, then declares denial tests, mangle test, `nbio` primitives, scanner entry points, connection helpers from `torture.c`, low-level SMB helper wrappers, Unicode/case table tests, POSIX tests, SMB2/DFS/notify/dbwrap/messaging/g_lock/idmap/cache tests, and local regression tests such as `run_local_conv_auth_info`.

## Control flow
There is no executable control flow in the header. Its declarations let `torture.c` build a registry of named test operations and let individual files call shared connection, cleanup, and raw-SMB helpers.

## State and persistence behavior
The header owns no state. It exposes functions that operate on `cli_state` connections and remote test shares, and it makes dependencies on globals in `torture.c` visible indirectly through implementation files.

## Dependencies and integration points
Every file in this work item except standalone binaries uses or is represented by this header. The declared functions are wired into the `smbtorture3` binary via `wscript_build` and the `torture_ops[]` registry in `torture.c`.

## Risks and test signals
Because this is a broad manual prototype header, stale declarations can cause build failures or hide ownership boundaries between torture modules. It is a useful integration map: functions declared here are expected to be callable by the harness and should remain source3-client compatible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/scanner.c -->
# sources/user-network-fs/samba/source3/torture/scanner.c

## Purpose
`scanner.c` probes SMB `TRANS2` and `NTTRANS` subcommands/info levels to discover accepted parameter formats, minimum data lengths, and non-obvious server responses.

## Important APIs, types, and functions
For `TRANS2`, key functions are `try_trans2`, `try_trans2_len`, `scan_trans2`, and `torture_trans2_scan`. For `NTTRANS`, analogous functions are `try_nttrans`, `try_nttrans_len`, `scan_nttrans`, and `torture_nttrans_scan`. `trans2_check_hit` and `nttrans_check_hit` filter common negative statuses.

## Control flow
Each exported test opens a connection, creates or opens `\scanner.dat` and a root directory handle, then loops operations `OP_MIN..OP_MAX` and level ranges `0..50`, `0x100..0x130`, and `1000..1049`. For each pair it tries several parameter shapes: info level alone, file handle, notify-style handles, existing filename, new filename, and DFS-style directory path. If a full-size request succeeds, it searches for the minimum data length that also succeeds and prints the hit.

## State and persistence behavior
The scanner creates temporary names such as `\scanner.dat`, `\newfile.dat`, and `\testdir`. It attempts cleanup after new-file and DFS probes, but the scanner is exploratory and may leave artifacts if interrupted.

## Dependencies and integration points
It uses low-level `cli_trans` over `SMBtrans2` and `SMBnttrans`, Unicode-aware `trans2_bytes_push_str`, and `torture_open_connection`. It is registered in the torture harness as trans2 and nttrans scan tests.

## Risks and test signals
This is a fuzz-like protocol scanner, not a strict conformance test. Positive prints indicate implemented or partially accepted levels; unusual statuses may suggest parser bugs. It can exercise server code paths with malformed parameter/data lengths, so it is useful for robustness testing but can be noisy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/scanner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_addrchange.c -->
# sources/user-network-fs/samba/source3/torture/test_addrchange.c

## Purpose
`test_addrchange.c` tests Samba's local address-change notification API. It waits for network address add/delete events and prints their type and address.

## Important APIs, types, and functions
The exported test is `run_addrchange`. It uses `addrchange_context_create`, `addrchange_send`, `addrchange_recv`, `tevent_req_poll_ntstatus`, `enum addrchange_type`, and `print_sockaddr`.

## Control flow
The test creates a tevent context and addrchange context, then loops `torture_numops` times. Each iteration starts an async addrchange request, polls it to completion, receives the event type and address, maps `ADDRCHANGE_ADD`/`ADDRCHANGE_DEL` to readable strings, and prints the result.

## State and persistence behavior
No durable state is written. The test holds local event and addrchange contexts and observes OS/network-interface state changes.

## Dependencies and integration points
It is part of `smbtorture3` through `proto.h` and uses Samba's `lib/addrchange.h` API plus tevent NTSTATUS polling helpers.

## Risks and test signals
The test blocks waiting for actual address-change events, so it depends on the runtime environment. Failure to create context or receive events signals platform integration issues in the addrchange backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_addrchange.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_async_echo.c -->
# sources/user-network-fs/samba/source3/torture/test_async_echo.c

## Purpose
`test_async_echo.c` stresses concurrent asynchronous SMB and DCERPC operations on one connection. It issues a long RPC echo sleep, SMB echo requests, and intentionally failing large writes, then verifies the event loop drains all callbacks.

## Important APIs, types, and functions
`run_async_echo()` is the exported test. Callback helpers `rpccli_sleep_done`, `cli_echo_done`, and `write_andx_done` receive request statuses and decrement a shared outstanding counter. The test uses `cli_rpc_pipe_open_noauth`, generated `dcerpc_echo_TestSleep_send/recv`, `cli_echo_send/recv`, and `cli_write_andx_send/recv`.

## Control flow
The test opens a torture SMB connection, opens the rpcecho pipe, starts a 15-second RPC sleep, starts one SMB echo, then loops ten times issuing a `cli_write_andx` to fnum `4711` and another echo. It runs `tevent_loop_once` until all callbacks have decremented `num_reqs` to zero.

## State and persistence behavior
State is transient: one event context, one SMB connection, one RPC pipe, outstanding request count, and a zeroed 64 KiB buffer. The invalid write handle should not persist data.

## Dependencies and integration points
It depends on the rpcecho RPC interface being available on the server and on Samba async client APIs. It is registered in the source3 torture harness.

## Risks and test signals
The test is mainly a concurrency and request-multiplexing signal. Deadlocks, missed callbacks, or event-loop failures indicate async client regressions. Some callback statuses may be expected failures for invalid writes, so the key signal is completion rather than every operation succeeding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_async_echo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_authinfo_structs.c -->
# sources/user-network-fs/samba/source3/torture/test_authinfo_structs.c

## Purpose
`test_authinfo_structs.c` validates conversion between LSA trust-domain auth-info structures and Samba trust auth blobs. It is a local, non-network serialization round-trip test.

## Important APIs, types, and functions
`run_local_conv_auth_info()` is the exported test. `cmp_TrustDomainInfoBuffer` and `cmp_auth_info` compare nested auth-info buffers. `covert_and_compare` calls `auth_info_2_auth_blob` and `auth_blob_2_auth_info` and compares the result.

## Control flow
The test builds several combinations of incoming/outgoing current and previous auth arrays, including clear-text password entries and `TRUST_AUTH_TYPE_VERSION` entries. After each setup, it converts to incoming/outgoing blobs, converts back to `lsa_TrustDomainInfoAuthInfo`, and requires exact structural equality.

## State and persistence behavior
All data is stack or temporary talloc memory. It writes no remote or local durable state.

## Dependencies and integration points
It depends on generated LSA NDR types and `libcli/lsarpc/util_lsarpc.h` conversion helpers. It is registered as a local torture test through `proto.h`.

## Risks and test signals
The comparisons check counts, timestamps, auth types, sizes, data bytes, and null-vs-non-null previous arrays. Failures indicate trust password blob serialization regressions that could break trusted-domain persistence or interop.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_authinfo_structs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_buffersize.c -->
# sources/user-network-fs/samba/source3/torture/test_buffersize.c

## Purpose
`test_buffersize.c` is a small regression/stress test for `cli_qpathinfo` response buffer sizing. It repeatedly queries root path information with receive buffer sizes from 0 to 499 bytes.

## Important APIs, types, and functions
The exported function is `run_qpathinfo_bufsize`. It opens a torture connection and calls `cli_qpathinfo` with `SMB_FILE_ALL_INFORMATION`, variable `max_data_bytes`, and output pointers for returned data length.

## Control flow
The test prints a start banner, opens one SMB connection, loops `i = 0..499`, and issues `cli_qpathinfo(cli, cli, "\\", SMB_FILE_ALL_INFORMATION, 0, i, &rdata, &num_rdata)`. It ignores individual statuses and returns success if setup and loop completion succeed.

## State and persistence behavior
No server state is intentionally changed. Returned buffers are allocated by the client stack under the passed talloc context and are transient.

## Dependencies and integration points
It depends on Samba client RAP/TRANS2 qpathinfo code and is registered in the torture harness through `proto.h`.

## Risks and test signals
The value is in memory-safety and truncation behavior rather than semantic pass/fail per request. Crashes, leaks, or invalid buffer handling in `cli_qpathinfo` are the expected regression signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_buffersize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_case_insensitive.c -->
# sources/user-network-fs/samba/source3/torture/test_case_insensitive.c

## Purpose
`test_case_insensitive.c` is a regression test for Samba bug 8042 involving file creation below a directory whose case differs from a prior path check on case-insensitive filesystems.

## Important APIs, types, and functions
The exported function is `run_case_insensitive_create`. It uses `cli_mkdir`, `cli_chkpath`, `cli_openx`, `cli_close`, `cli_unlink`, and `cli_rmdir`.

## Control flow
The test opens an SMB connection, creates directory `x`, verifies `X` exists with `cli_chkpath`, then creates `x\y`. If `cli_openx` returns `NT_STATUS_FILE_IS_A_DIRECTORY`, it prints a specific bug-reappeared message. Cleanup unlinks `x\y` and removes `x`.

## State and persistence behavior
The only persistent artifacts are temporary `x` and `x\y`, both removed on the normal cleanup path. Errors can leave them behind.

## Dependencies and integration points
It is part of the `smbtorture3` POSIX/local regression set via `proto.h`. It depends on server-side case-insensitive pathname handling and client open/checkpath helpers.

## Risks and test signals
The key signal is that `x\y` must be created as a file even after checking `X`. Failures indicate case-folding or name-cache confusion, especially on case-insensitive backing filesystems such as macOS.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/test_case_insensitive.c -->
