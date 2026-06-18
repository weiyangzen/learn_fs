# subset-b-009972 Research

Grouped research for Samba source4 torture files. Each section preserves the source path and is bounded for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/man/smbtorture.1.xml -->
# sources/user-network-fs/samba/source4/torture/man/smbtorture.1.xml

## Purpose
This DocBook XML file is the `smbtorture(1)` manual page for Samba 4.0. It documents the command used to run SMB, RPC, NBT, benchmark, and other torture tests against SMB servers. The page is not executable code, but it is an integration contract for users and automated documentation generation: it defines the expected command synopsis, accepted binding/UNC formats, common command-line options, and the operational warning around dangerous tests.

## Important APIs, Types, And Functions
The artifact uses the DocBook `refentry` schema rather than C APIs. Important elements are `refmeta`, `refnamediv`, `refsynopsisdiv`, `cmdsynopsis`, `arg`, `refsect1`, `refsect2`, `variablelist`, and `varlistentry`. The page exposes CLI options such as `-d`, `-U`, `-k`, `-W`, `-n`, `-O`, `-m`, `-s`, `-L`, `-X`, `-t`, `-p`, `-c`, `-A`, `-C`, `-N`, `-e`, and `-f`. It also documents positional arguments for a UNC/binding string and one or more test names.

## Control Flow
The document is organized in the standard manpage flow: metadata, name/purpose, synopsis, description, binding string format, UNC format, option list, version, related material, and authorship. The binding-string section describes how transports such as `ncacn_np`, `ncacn_ip_tcp`, and `ncalrpc` select SMB named pipes, RPC/TCP endpoints, or local RPC, with flags controlling signing, sealing, validation, packet printing, endian behavior, and pad checking.

## State And Persistence
This file persists no runtime state. It does, however, persist user-visible assumptions about `smbtorture`: default NBENCH time limit, option names, dangerous-test behavior, and the version target. Documentation drift here can create user-facing misconfiguration even when the binary works correctly.

## Dependencies
The file depends on the DocBook XML 4.2 DTD and Samba's manpage build pipeline. Semantically it depends on the `smbtorture` command-line parser and test registration surface matching the described options.

## Integration Points
The generated manual integrates with packaging, installed manpages, online docs, and operator workflows. The binding examples are especially tied to Samba's DCE/RPC binding parser and named-pipe routing. The NBENCH options connect to the nbench sources in this same subset.

## Risks
The synopsis appears to combine older `//server/share` usage with newer `BINDING-STRING|UNC TEST...` usage, so readers may need implementation help to know which options apply to each test class. The page names Samba 4.0 and can become stale as protocols, options, or supported dialects evolve. The `-X` option explicitly enables tests that may crash target servers, so this manual page has operational safety significance.

## Test Signals
Useful signals are documentation build success, DocBook validation, generated `smbtorture.1` readability, and spot-checks that documented options are still accepted by `smbtorture --help`. Test coverage should also compare described benchmark options such as `-t`, `-c`, and `-N` with the nbench implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/man/smbtorture.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/masktest.c -->
# sources/user-network-fs/samba/source4/torture/masktest.c

## Purpose
`masktest.c` is a standalone SMB wildcard matching torture program. It creates test files on a target share, lists them through the server using SMB directory search calls, computes Samba's local `ms_fnmatch_protocol()` expectation for the same mask/file pair, and reports mismatches. It is aimed at detecting protocol-dialect differences and server behavior drift around DOS/SMB wildcard semantics, including long/short name interactions and special dot entries.

## Important APIs, Types, And Functions
Key globals configure fuzzing and reporting: `showall`, `old_list`, `maskchars`, `filechars`, `die_on_error`, `NumLoops`, and `max_length`. `struct masktest_state` carries a `TALLOC_CTX` into list callbacks. `reg_match_one()` wraps `ms_fnmatch_protocol()` and adds SMB-specific special cases for `*.*`, `.`, and `..`. `reg_test()` computes the three-character expected result for dot, dotdot, and the test file. `connect_one()` parses a UNC share and calls `smbcli_full_connection()`. `listfn()` is the `smbcli_list_new()` callback that records which class of entry the server returned and saves long/short names. `get_real_name()` obtains the server-side long and 8.3 short names by listing the `\\masktest` directory. `testpair()` creates one file, lists by mask, compares server and local results, prints mismatches, and unlinks the file. `test_mask()` either consumes explicit mask/file argument pairs or generates random masks and filenames indefinitely or until `NumLoops`.

## Control Flow
`main()` initializes talloc, Samba command-line handling, popt options, loadparm, logging, events, GENSEC, SMB client options, and the server connection. It normalizes the UNC path from `/` to `\\`, connects as workstation `masktest`, seeds the random generator after connection setup, and invokes `test_mask()`. `test_mask()` creates `\\masktest`, clears old entries, then either runs supplied pairs or a random fuzz loop. Each `testpair()` creates the file, queries the real server names, performs a masked listing, computes the local expectation, prints when results differ or `--showall` is set, and cleans up the file. The directory is removed at the end.

## State And Persistence
Runtime state is mostly global and process-local. `resultp` points at the current three-character result buffer used by `listfn()`, and `last_hit`/`f_info_hit` retain the most recent directory-listing match. Persistent remote state is limited to a temporary `\\masktest` directory and files under it; cleanup attempts are explicit but may leave artifacts if the process exits during a failure or `--dieonerror`. The random seed is printed so fuzz failures can be reproduced.

## Dependencies
The file depends on Samba client libraries (`libcli/libcli.h`), command-line and credentials helpers, talloc, tevent, loadparm, resolver, GENSEC, file/dir system wrappers, and protocol-aware name matching via `ms_fnmatch_protocol()`. It depends on SMB server support for open, close, list, unlink, wildcard unlink, mkdir, and rmdir operations.

## Integration Points
This program is an external torture utility rather than a registered `smbtorture` suite in this file. It integrates with Samba credentials and connection options through `POPT_COMMON_*` tables and `samba_cmdline_get_creds()`. Results validate both server behavior and Samba's internal wildcard matching rules for the negotiated protocol dialect.

## Risks
The code uses several globals, so concurrent use within one process would be unsafe. `get_real_name()` assumes `short_name` is initialized and dereferenceable after listing; severe list failure could leave `long_name` unset. Random generation avoids dot-only filenames and dotdot masks, but it can still generate large search spaces or server-expensive masks. Cleanup is best-effort and remote artifacts can remain after aborts. The `old_list` compatibility special case changes expected `*.*` semantics and must be used deliberately.

## Test Signals
Strong signals are reproducible mismatch lines showing `server_result expected_result count mask file real_names`, absence of mismatches across many seeded loops, successful cleanup of `\\masktest`, and coverage across protocol dialects. Useful focused tests include explicit pairs around `.`, `..`, `*`, `?`, `*.*`, short-name aliases, and protocol versions at or below `LANMAN1`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/masktest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbench/nbench.c -->
# sources/user-network-fs/samba/source4/torture/nbench/nbench.c

## Purpose
`nbench.c` registers and drives the `bench.nbench` smbtorture test. It replays a NetBench-style client load file against an SMB server, optionally with multiple client processes, timing control, target throughput throttling, read-only suppression of mutating operations, and reconnect retries. It delegates individual SMB operations and throughput accounting to `nbio.c`.

## Important APIs, Types, And Functions
Important globals are `nbench_line_count`, `timelimit`, `warmup`, `loadfile`, `read_only`, and `nb_max_retries`. The `NB_RETRY(op)` macro retries an operation through `do_reconnect()` while the operation returns false. `do_reconnect()` calls `nb_reconnect()` until retries are exhausted, then exits via `nb_exit()`. `run_netbench()` is the per-client worker used by `torture_create_procs()`. It parses load-file lines into shell-style tokens, handles optional leading timestamps, maps textual or numeric NT status values, dispatches operation names to `nb_*` wrappers, and loops the load file until `nb_tick()` indicates completion. `torture_nbench()` reads torture settings, creates shared nbench state, establishes common setup directories, installs signal handlers, forks workers, and prints final throughput. `torture_nbench_init()` creates the `bench` suite and registers the `nbench` test.

## Control Flow
`torture_nbench()` reads settings such as `nprocs`, `readonly`, `nretries`, `timelimit`, and `loadfile`, computes warmup as five percent of runtime, initializes `nbio_shmem()`, resets `SIGCHLD`, arms `SIGALRM` for periodic statistics, and runs `run_netbench()` in multiple torture processes. Each worker calls `nb_setup()`, prepares a per-client name like `client1`, opens the load file, then repeatedly parses and executes operations. Recognized operations include create, close, rename, unlink, deltree, directory operations, path/file/fs queries, setfileinfo, find-first, reads, writes, locks, unlocks, flushes, and sleep. Once the timer marks workers done, the worker closes the file, removes shared `\\clients` state when appropriate, closes its SMB connection, and returns correctness status.

## State And Persistence
`nbench_line_count` is global progress state used in diagnostics and by `nbio.c`. Runtime settings are file-static and process-local. Persistent remote state includes the `\\clients` directory and all files/directories created by the replayed workload; cleanup is performed by `torture_setup_dir()` before execution and `smbcli_deltree()` after execution when not read-only. Load-file progress is not persisted; the file is rewound repeatedly until the time limit expires.

## Dependencies
This file depends on Samba torture infrastructure, `smbcli_state`, `torture_create_procs()`, settings accessors, the nbench `proto.h` API implemented by `nbio.c`, NTSTATUS parsing, string-list helpers, locale character checks, and SMB/raw operation wrappers. It also depends on a valid NetBench-format load file, defaulting to `client.txt`.

## Integration Points
The suite is registered under `bench.nbench`, and documented options in `smbtorture.1.xml` map to settings consumed here. `run_netbench()` integrates tightly with `nbio.c`: every operation wrapper updates shared counters, checks statuses, and manages handle mappings. `torture_create_procs()` provides concurrency; `SIGALRM` drives reporting through `nb_alarm()`.

## Risks
The parser assumes enough parameters for each recognized operation and can read beyond token bounds if the load file is malformed despite the minimal `i < 2` check. `asprintf()` allocation for `cname` is not freed. The retry macro mutates local `n`, so maintenance changes around the macro must preserve that variable. Read-only mode silently skips mutating operations, which changes workload semantics. Signal handling is process-wide and can interact with surrounding test harness code if expectations change. A failed worker can leave remote test data.

## Test Signals
Useful signals include correct parsing of textual and hex NTSTATUS values, failure on dbench v1 load files, reconnect retry logs, periodic throughput/latency output from `nb_alarm()`, final `Throughput` output, and remote cleanup of `\\clients`. Regression tests should use a small synthetic load file covering each dispatch branch, malformed status fields, read-only mode, and forced reconnects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbench/nbench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbench/nbio.c -->
# sources/user-network-fs/samba/source4/torture/nbench/nbio.c

## Purpose
`nbio.c` implements the SMB operation layer, handle/lock tracking, shared benchmark accounting, reconnect restoration, and timer-driven statistics for the nbench torture test. It translates replayed NetBench operations into Samba raw SMB calls and validates each response against the expected NTSTATUS from the load file.

## Important APIs, Types, And Functions
Persistent in-process structures are `struct lock_info`, `struct createx_params`, and `struct ftable`. `ftable` maps load-file handles to server FIDs and records create parameters plus active byte-range locks so reconnect can reopen and relock files. The shared-memory `children` array tracks each process's bytes, warmup bytes, current line, done flag, connected flag, max latency, and start time. Setup/accounting APIs include `nbio_shmem()`, `nb_setup()`, `nbio_time_reset()`, `nbio_time_delay()`, `nbio_target_rate()`, `nbio_result()`, `nbio_latency()`, `nb_tick()`, `nb_alarm()`, and `nb_exit()`. Recovery APIs include `nb_reconnect()`, `nb_reopen_all_files()`, and `nb_reestablish_locks()`. Operation APIs include `nb_createx()`, `nb_close()`, `nb_unlink()`, `nb_rename()`, `nb_deltree()`, `nb_rmdir()`, `nb_mkdir()`, `nb_qpathinfo()`, `nb_qfileinfo()`, `nb_qfsinfo()`, `nb_sfileinfo()`, `nb_findfirst()`, `nb_writex()`, `nb_write()`, `nb_readx()`, `nb_lockx()`, `nb_unlockx()`, `nb_flush()`, and `nb_sleep()`.

## Control Flow
`nbio_shmem()` allocates anonymous shared memory for child statistics and initializes the benchmark timer. `nb_setup()` sets the process's `nbio_id`, stores the current `smbcli_state` in the static `c`, installs an oplock break handler, and marks the child connected. Operation wrappers look up file handles with `find_handle()`, build the corresponding `union smb_*` raw request, call a `smb_raw_*` function, and pass results to `check_status()`. Successful creates add or update `ftable`; closes remove entries; locks add `lock_info`; unlocks remove matching lock state. If a reconnect occurs, `nb_reconnect()` frees the old client, opens a new connection, calls `nb_setup()`, then replays create and lock state from `ftable`.

## State And Persistence
Most state is runtime memory, split between per-process globals and anonymous shared memory visible to all nbench children. Remote persistent state consists of files, directories, locks, and open handles on the SMB server. `nb_deltree()` sends an SMB exit, clears local handle state, recursively deletes a server tree, and removes the directory. Timers separate warmup bytes from measured bytes and mark all children done after the configured execution window.

## Dependencies
The file depends on Samba raw SMB client APIs, torture connection helpers, talloc, anonymous shared memory, timeval helpers, signal/alarm behavior, linked-list macros from `dlinklist.h`, and `nbench_line_count` from `nbench.c`. It also relies on the server honoring SMB open, read, write, lock, search, metadata, flush, tree cleanup, and oplock acknowledgement semantics.

## Integration Points
`nbench.c` dispatches all replayed operations into these APIs. `nb_alarm()` is installed as a `SIGALRM` handler by `torture_nbench()` and periodically prints connection count, lines per process, throughput, phase, and latency. The oplock handler integrates with the SMB transport to acknowledge break-to-none requests. Reconnect behavior integrates with the `NB_RETRY` macro in `nbench.c`.

## Risks
Several wrappers allocate buffers with `malloc(size)` and immediately `memset()` without checking allocation failure. `check_status()` treats some transport-like errors specially by returning false for retry; other expected/unexpected mismatches can exit the process. The static `c`, `nbio_id`, and `ftable` mean the code is not reentrant. `nb_mkdir()` intentionally ignores errors, which is useful for base fileset creation but hides failures. Shared state updates are not protected by locks; the design assumes mostly per-child writes with aggregate reads by the parent signal handler. The file table is talloc-allocated under `NULL` or file entries, so leaks are acceptable for benchmark lifespan but matter during repeated embedded use.

## Test Signals
Signals include exact status validation, fatal handle lookup failures, reconnect logs followed by reopened files and reestablished locks, correct byte accounting for reads/writes, `nb_alarm()` phase transitions from warmup to execute to cleanup, and final throughput calculation excluding warmup bytes. Focused tests should force reconnects with open locked files, exercise create disposition retry rules, validate lock tracking removal, and cover error/status mismatch branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbench/nbio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/dgram.c -->
# sources/user-network-fs/samba/source4/torture/nbt/dgram.c

## Purpose
`dgram.c` defines NetBIOS datagram torture tests for UDP/138 mailslot-based NETLOGON and NTLOGON behavior. It sends primary-domain-controller and SAM logon discovery requests to a resolved domain/workgroup name, waits for datagram replies, parses them as netlogon responses, and checks response type, command, version flags, user echoing, PDC name format, and account-control behavior.

## Important APIs, Types, And Functions
`netlogon_handler()` is a `dgram_mailslot_handler` callback that allocates `struct nbt_netlogon_response` storage and parses incoming datagrams via `dgram_mailslot_netlogon_parse_response()`. `nbt_test_netlogon()` sends a `LOGON_PRIMARY_QUERY` to `NBT_MAILSLOT_NETLOGON` and expects `NETLOGON_GET_PDC`. `nbt_test_netlogon2()` sends multiple `LOGON_SAM_LOGON_REQUEST` variants, joins a temporary machine account with `torture_join_domain()`, and verifies responses for unknown and trusted workstation cases. `nbt_test_ntlogon()` performs similar checks using `NBT_MAILSLOT_NTLOGON`. `torture_nbt_dgram()` registers the `dgram` suite with `netlogon`, `netlogon2`, and `ntlogon` tests.

## Control Flow
Each test creates an NBT datagram socket, resolves the configured workgroup/domain logon name with `resolve_name_ex()`, chooses a local interface IP via `iface_list_best_ip()`, then tries to bind the datagram socket to the configured datagram port. If binding the low port fails, it falls back to an ephemeral port, with comments noting this may prevent replies from some Windows versions. Tests create temporary mailslot listeners, build `struct nbt_netlogon_packet` requests, send with `dgram_mailslot_netlogon_send()`, and run the tevent loop until a reply arrives or five seconds elapse. More advanced paths join and leave a temporary domain machine account and repeat requests with SID and account-control fields.

## State And Persistence
Socket, mailslot, and response state are talloc-owned and per-test. `dgmslot->private_data` is used as both callback output and loop condition. Persistent external state occurs when `nbt_test_netlogon2()` and `nbt_test_ntlogon()` create a temporary workstation trust account named `TORTURE_TEST`; cleanup is done with `torture_leave_domain()`. The tests also rely on transient UDP network state and local port binding permissions.

## Dependencies
Dependencies include `libdgram`, socket abstractions, tevent, name resolution, network interface discovery, loadparm ports/workgroup, torture RPC join helpers, generated NBT/netlogon structures, and NBT mailslot constants. The target environment must have a reachable domain controller or Samba server responding to NBT logon datagrams.

## Integration Points
The suite is added by `torture_nbt_init()` in `nbt.c`. It validates Samba's datagram server behavior and compatibility with Windows netlogon conventions. Temporary domain joins integrate with Samba's RPC/LDAP account-management test helpers, while name resolution integrates with configured resolver policy.

## Risks
The low-port fallback changes test observability: inability to bind UDP/138 can make some valid servers appear silent. The timeout loops reuse a `struct timeval tv` initialized near the start of the test; in multi-step tests this can shorten later waits if not reset around each send. Temporary domain joins can leave accounts behind if a fatal assertion exits before cleanup. The callback replaces `private_data` with newly allocated response storage and returns silently on allocation failure, which appears as a timeout. Tests are environment-sensitive and may fail under firewalls, wrong interface selection, or missing NBT service.

## Test Signals
Positive signals are received datagram replies, parsed `NETLOGON_GET_PDC` or `NETLOGON_SAMLOGON` response types, correct command constants, expected NT version flag combinations, correct user-name echoing, and expected UNC/non-UNC PDC name formatting. Negative signals include assertion failures on send, parse, timeout, account join, or response field mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/dgram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/nbt.c -->
# sources/user-network-fs/samba/source4/torture/nbt/nbt.c

## Purpose
`nbt.c` is the registration and shared-helper entry point for Samba's NetBIOS over TCP/IP and WINS torture tests. It exposes common NBT socket/name-resolution helpers and registers all NBT-related suites under the top-level `nbt` smbtorture suite.

## Important APIs, Types, And Functions
`torture_init_nbt_socket()` creates an `nbt_name_socket` bound to the torture context's event loop. `torture_nbt_get_name()` constructs a server NBT name from the `host` torture setting, uppercases it, resolves it with `resolve_name_ex()`, and returns the chosen address. `torture_nbt_init()` creates the `nbt` suite, adds register, WINS, datagram, WINS replication, NBT benchmark, and WINS benchmark child suites, sets a description, and calls `torture_register_suite()`.

## Control Flow
NBT tests call the helper functions to obtain sockets and resolved target names. During module initialization, `torture_nbt_init()` builds the suite tree in a fixed order: registration tests, WINS tests, datagram tests, WINS replication tests, NBT query benchmark, and WINS benchmark. The function then publishes the suite to the smbtorture registry.

## State And Persistence
This file stores no persistent state. It allocates sockets and suite objects under caller-provided talloc contexts. The target name/address returned by `torture_nbt_get_name()` is derived from runtime settings and resolver state, not stored globally.

## Dependencies
Dependencies include the NBT client library, torture framework, smbtorture registration API, resolver context, talloc, loadparm, and prototypes for the child NBT suites. A valid `host` setting is required for name resolution.

## Integration Points
This file is the hub that connects `register.c`, `wins.c`, `dgram.c`, `query.c`, `winsbench.c`, and WINS replication tests into the smbtorture suite hierarchy. Its helper functions standardize target resolution for the other files in this subset.

## Risks
If the `host` setting is absent or not resolvable, all dependent NBT tests fail early. Uppercasing the host before resolution is consistent with NetBIOS naming but may hide case-sensitive edge cases unless individual tests override names. Suite registration depends on all referenced child-suite factories being linked.

## Test Signals
Signals are successful suite registration under `nbt`, correct child suite visibility in `smbtorture` listings, and successful name resolution through `torture_nbt_get_name()`. Failures usually appear as assertion messages reporting inability to resolve the configured host.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/nbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/query.c -->
# sources/user-network-fs/samba/source4/torture/nbt/query.c

## Purpose
`query.c` implements the `nbt.bench.namequery` benchmark. It measures how many asynchronous NetBIOS name queries a server can answer within a configured time limit while keeping a bounded number of outstanding requests.

## Important APIs, Types, And Functions
`struct result_struct` tracks `num_pass` and `num_fail`. `increment_handler()` is the asynchronous completion callback for `struct nbt_name_request`; it increments pass/fail depending on `req->state` and frees the request. `bench_namequery()` sets up the query template, sends asynchronous `nbt_name_query_send()` requests, runs the event loop, drains outstanding requests, and reports queries per second. `torture_bench_nbt()` registers the `bench` suite with the `namequery` simple test.

## Control Flow
`bench_namequery()` obtains an NBT socket with `torture_init_nbt_socket()`, resolves the target through `torture_nbt_get_name()`, initializes a `struct nbt_name_query` with retries disabled, one-second timeout, direct unicast destination, and non-WINS lookup mode. For the configured `timelimit` it maintains fewer than ten outstanding requests, attaches `increment_handler()` to each request, and advances tevent once per outer loop. After time expires it continues processing events until every sent request has either passed or failed, then reports throughput.

## State And Persistence
All benchmark state is in memory under the torture context. There is no remote persistent state because the test only queries names. The only long-lived observable state is benchmark output showing pass rate and failures.

## Dependencies
The file depends on NBT socket/query APIs, tevent, resolver/loadparm helpers from `nbt.c`, torture settings, timeval helpers, and the target server's NetBIOS name service. It uses `lpcfg_nbt_port()` for the destination port.

## Integration Points
The suite is registered by `torture_nbt_init()` through `torture_bench_nbt()`. It shares target resolution and socket creation with the rest of the NBT torture area. The `progress` torture setting controls periodic output.

## Risks
The benchmark divides by elapsed time and pass count, so very short time limits or no replies can produce unhelpful throughput output. The completion callback treats any non-`NBT_REQUEST_DONE` state as failure without distinguishing timeout, network error, or protocol error. With retries set to zero and only ten in-flight requests, results are intentionally latency-sensitive and may underrepresent high-throughput servers on lossy networks.

## Test Signals
Signals are the final queries-per-second line, failure count, periodic progress every thousand sends, and successful draining of all outstanding requests. Useful regression signals include stable pass/fail accounting and absence of request leaks under timeout-heavy conditions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/register.c -->
# sources/user-network-fs/samba/source4/torture/nbt/register.c

## Purpose
`register.c` defines NBT name registration and refresh tests that verify a server defends its own NetBIOS name. It attempts to register and refresh the target server's name from the local client and expects the server to answer with an active-name conflict response.

## Important APIs, Types, And Functions
Macros `CHECK_VALUE` and `CHECK_STRING` wrap torture assertions for integer and case-insensitive string comparisons. `nbt_register_own()` builds a `struct nbt_name_register` request for the resolved server name, binds a local NBT socket, sends normal registration and register-demand variants, and checks `NBT_RCODE_ACT`. `nbt_refresh_own()` sends `struct nbt_name_refresh` for the server's name and also expects `NBT_RCODE_ACT`. `torture_nbt_register()` creates the `register` suite and adds `register_own` and `refresh_own`.

## Control Flow
Both tests resolve the target name/address with `torture_nbt_get_name()`, choose the best local interface address for reaching the target, bind a socket on an ephemeral local port, populate request fields with target name, target NBT port, local address, B-node active flags, TTL, timeout, and retry count, then call the synchronous NBT client API. Assertions validate that the response name/type matches the target and that the response code indicates active conflict.

## State And Persistence
The tests do not intend to create persistent server state; they attempt operations that should be rejected/defended by the target owner. Local socket state is transient. If a server incorrectly accepts the registration, it may mutate name-service state, which is exactly the failure this test is meant to catch.

## Dependencies
Dependencies include NBT socket APIs, Samba socket abstraction, resolver helpers, interface selection, loadparm NBT port, and torture assertion macros. The environment must support local UDP sockets and a target server reachable by NetBIOS name service.

## Integration Points
The suite is registered from `nbt.c`. It shares helper functions with the WINS and benchmark tests and validates the same target resolved from the `host` setting. These tests are low-level signals for name ownership behavior that WINS and datagram tests depend on indirectly.

## Risks
The tests assume the best local interface IP chosen for the target is acceptable to the server. Firewalls, disabled NetBIOS service, or NAT can produce failures unrelated to server name defense. The refresh test comment contains a typo in an assertion message, but behavior is unaffected. Because retries are zero and timeout is three seconds, transient packet loss can fail the test.

## Test Signals
Positive signals are NTSTATUS success from `nbt_name_register()`/`nbt_name_refresh()`, echoed name/type values, and `NBT_RCODE_ACT`. Any `NBT_RCODE_OK` for the server's own name is a serious behavioral failure. Socket bind or resolution failures identify environment problems before protocol assertions run.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/register.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/wins.c -->
# sources/user-network-fs/samba/source4/torture/nbt/wins.c

## Purpose
`wins.c` implements functional WINS server torture tests. It registers, queries, refreshes, releases, and re-queries many NetBIOS name variants to validate WINS semantics, conflict behavior, group-name behavior, case sensitivity, scope handling, long-scope limits, and security around names passed to the WINS hook.

## Important APIs, Types, And Functions
Macros `CHECK_VALUE`, `CHECK_STRING`, and `CHECK_NAME` provide assertion helpers. `nbt_test_wins_name()` is the main scenario runner for one name/type/flag combination. It uses `nbt_name_release()`, `nbt_name_register_wins()`, asynchronous `nbt_name_register_send()`/`recv()`, `nbt_name_query()`, `nbt_name_refresh_wins()`, and `nbt_name_release()` to exercise a full lifecycle. `test_nbt_wins_scope_string()` creates long dotted scope strings for boundary tests. `nbt_test_wins()` generates a random base name and runs lifecycle tests across client, master, server, logon, browser, PDC, unusual type bytes, scoped names, empty/dot names, binary-ish names, and long scopes. `nbt_test_wins_bad_names()` verifies names with shell-sensitive characters do not trigger the WINS hook while normal safe names do. `torture_nbt_wins()` registers `wins` and `wins_bad_names`.

## Control Flow
`nbt_test_wins_name()` chooses a local interface IP, tries to bind the client socket to the low NBT port so the server sees the expected source, and falls back to an ephemeral port if needed. It first releases the name, optionally tests wrong-address registration and WACK/resend handling, registers the correct address through WINS, validates the returned WINS server and rcode, then queries the name. For successful names it checks returned addresses, case-sensitive lookup behavior, refreshes TTL, releases the name twice, and verifies final absence except for group-name semantics. `nbt_test_wins()` repeatedly mutates `struct nbt_name` fields and accumulates boolean success. `nbt_test_wins_bad_names()` removes a known hook-output file, runs a WINS lifecycle with each test name, polls for hook output, and asserts hook execution only for allowed names.

## State And Persistence
The test intentionally mutates WINS database state by registering and releasing names. It uses random name suffixes to reduce collisions and explicit release operations to clean up. Wrong-address registration and refresh paths temporarily place alternate records in the WINS database. `wins_bad_names` uses a persistent test file under `SELFTEST_TMPDIR` to observe hook execution and removes it before and after cases.

## Dependencies
Dependencies include NBT name registration/query/refresh/release APIs, async request queues, DLIST queue manipulation, tevent, socket binding, local interface selection, generated NBT constants, `SELFTEST_TMPDIR`, and server-side WINS hook configuration for the hook-specific test. It relies on `torture_nbt_get_name()` to resolve the WINS server address.

## Integration Points
The suite is added by `torture_nbt_init()`. It exercises Samba's WINS server and database behavior from the client side and overlaps with WINS hook shell-safety validation. The asynchronous resend path directly manipulates an NBT request back into the socket send queue after a WACK, so it integrates deeply with the NBT client state machine.

## Risks
This is highly environment-sensitive: inability to bind the low port skips wrong-address conflict checks, missing `SELFTEST_TMPDIR` can break hook observation, and packet loss can cause timeouts. The lifecycle intentionally changes WINS state and may leave records if assertions abort before release. The bad-name test treats some failures as expected DN syntax failures, so diagnosis requires reading comments and output. Long scope and unusual byte-name tests may expose encoding or database-layer assumptions.

## Test Signals
Signals include expected rcodes (`NBT_RCODE_OK`, `NBT_RCODE_ACT`, `NBT_RCODE_SVR`), correct returned WINS server, query address matching either the client IP or broadcast for some group names, object-not-found after release, failure for case-changed name/scope lookups, WACK/resend tolerance, and hook output only for safe names. Failures often point directly to WINS database semantics, source-address handling, or hook sanitization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/wins.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/winsbench.c -->
# sources/user-network-fs/samba/source4/torture/nbt/winsbench.c

## Purpose
`winsbench.c` implements the `nbt.bench-wins.wins` benchmark. It measures WINS server throughput under a random mixture of name registrations, releases, and queries across a configurable pool of generated names.

## Important APIs, Types, And Functions
`struct wins_state` stores benchmark configuration and counters: number of names, per-name registered flags, pass/fail counts, server/port, local IP, and TTL. `struct idx_state` associates an async request with a name index. `generate_name()` creates deterministic names like `WINSBench%6u` with type `0x4`. `register_handler()`, `release_handler()`, and `query_handler()` receive async completions, update pass/fail counts, and maintain `registered[idx]`. `generate_register()`, `generate_release()`, and `generate_query()` construct and send one async NBT request. `generate_request()` chooses a register roughly one-fifth of the time, release roughly one-twentieth of the remaining calls, otherwise query. `bench_wins()` runs the timed benchmark and reports throughput. `torture_bench_wins()` registers the `bench-wins` suite.

## Control Flow
`bench_wins()` resolves the WINS target with `torture_nbt_get_name()`, allocates `wins_state`, sizes the name pool from global `torture_entries`, selects a local interface IP, binds the NBT socket, and runs until `timelimit` seconds elapse. The loop maintains fewer than ten outstanding requests, sends a generated request for `num_sent % num_names`, periodically reports progress, and advances the tevent loop. After time expires it drains outstanding requests, prints final operations per second and failures, frees the socket, and returns.

## State And Persistence
In-memory state tracks whether each generated name is believed registered. Remote WINS state is intentionally mutated: registrations add names and releases remove them. TTL is set to the benchmark time limit, limiting but not eliminating residue if the benchmark exits early or releases fail. Registered state is probabilistic from the client's viewpoint because query failures against names believed registered are counted as failures, but successful queries for unregistered names are not treated as failure.

## Dependencies
The benchmark depends on NBT asynchronous request APIs, tevent, socket binding, interface discovery, loadparm NBT port, the global `torture_entries`, and the target WINS server. It also depends on talloc lifetime rules: request private data is allocated under the socket and freed by handlers.

## Integration Points
`torture_bench_wins()` is registered under the NBT suite by `nbt.c`. The benchmark complements functional WINS tests in `wins.c` by applying concurrent-style pressure through up to ten outstanding async operations. It uses the same target resolution helper and progress setting convention as `query.c`.

## Risks
`generate_register()`, `generate_release()`, and `generate_query()` assume `nbt_name_*_send()` returns a non-NULL request before assigning callbacks; allocation or send setup failure could dereference NULL. If `torture_entries` is zero, modulo by zero will occur. Because releases are random and TTL is only bounded by the run time, failed/early runs can leave WINS records behind until expiry. The benchmark does not validate returned query addresses, only status relative to local registered state.

## Test Signals
Signals are final operations-per-second output, failure count, progress every fifty sends when enabled, and complete draining of outstanding async requests. Important edge tests include `torture_entries=1`, larger pools, timeout-heavy servers, request allocation failure handling, and post-run WINS cleanup checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/winsbench.c -->
