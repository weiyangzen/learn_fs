# Research Group subset-b-010002

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/lease_break_handler.c -->
# sources/user-network-fs/samba/source4/torture/smb2/lease_break_handler.c

## Purpose
`lease_break_handler.c` implements the shared SMB2 torture lease-break callback machinery used by lease and multichannel tests. It records the last lease break notification, optionally acknowledges it, optionally closes a handle when a handle-caching lease is revoked, counts callbacks and failures, and provides a bounded event-loop wait helper for tests that expect an asynchronous break.

## Important APIs, Types, and Functions
The file defines the global `struct lease_break_info lease_break_info`, declared in `lease_break_handler.h`. `torture_lease_handler()` is the transport-level lease break handler installed on `struct smb2_transport`. It consumes `struct smb2_lease_break` notifications, records the transport and break payload, increments `count`, closes `lease_break_info.lease_handle` with `smb2_close_send()` when a HANDLE lease is removed, and sends `smb2_lease_break_ack_send()` when `SMB2_NOTIFY_BREAK_LEASE_FLAG_ACK_REQUIRED` is set and `lease_skip_ack` is false. `torture_wait_for_lease_break()` spins the test event loop until a new break arrives or a one-second timer fires. The async receive callbacks update `lease_break_ack`, `close`, and `failures`.

## Control Flow
A server lease break enters through `torture_lease_handler()`. The handler converts the new lease state to a diagnostic string, stores the notification in global test state, and chooses one of three paths: close a stored handle for handle-lease revocation, deliberately skip acknowledgment for retry/timing tests, or asynchronously send a lease-break acknowledgment. `torture_wait_for_lease_break()` snapshots the old count, installs a `tevent` timer on `tctx->ev`, and loops with `tevent_loop_once()` until `count` advances or the timer sets `timesup`.

## State and Persistence Behavior
All state is process-local torture state in the global `lease_break_info`. There is no durable persistence; the state is reset by `torture_reset_lease_break_info()` from the header. Asynchronous acknowledgments and closes are stored into the global struct after their send requests complete, so tests must continue the event loop before inspecting ack output.

## Dependencies and Integration Points
The code depends on Samba SMB2 client calls, `tevent`, torture assertions/logging, `smbXcli_base`, and the lease helper declarations in `lease_break_handler.h`. `multichannel.c` installs this handler on each bound channel to verify which transport receives lease breaks and whether breaks can be acknowledged on another channel.

## Risks and Edge Cases
The global singleton means concurrent lease tests would interfere with each other. The close-on-handle-revocation path returns before sending an explicit lease ack, so correctness depends on the close being the intended response for that scenario. The wait helper treats timeout as diagnostic rather than fatal, leaving each caller to assert count/failure expectations. Async send failures are counted only after the callback runs.

## Test Signals
Consumers assert `lease_break_info.count`, `failures`, recorded transport, break state, epoch, and ack contents through macros in the header. Retry tests intentionally set `lease_skip_ack` or block transports to verify timeout/retry behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/lease_break_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/lease_break_handler.h -->
# sources/user-network-fs/samba/source4/torture/smb2/lease_break_handler.h

## Purpose
`lease_break_handler.h` defines the shared state, assertion macros, and reset/helper declarations for SMB2 lease-break torture tests. It is a test-support header, not production protocol logic.

## Important APIs, Types, and Functions
`struct lease_break_info` records the active torture context, last `smb2_lease_break`, receiving `smb2_transport`, ack-skip flag, last `smb2_lease_break_ack`, optional handle to close on break, close response, lease counters, and colocated oplock counters/levels used by combined tests. The external singleton `lease_break_info` is defined in the `.c` file. `torture_lease_handler()` and `torture_wait_for_lease_break()` are declared for test files to install and drive the handler. `torture_reset_lease_break_info()` zeroes the state and reinstalls the current `tctx`.

The macros are the main API surface: `CHECK_LEASE_BREAK`, `CHECK_LEASE_BREAK_ACK`, `CHECK_NO_BREAK`, `CHECK_OPLOCK_BREAK`, `CHECK_BREAK_INFO`, `CHECK_BREAK_INFO_V2`, and NOWAIT variants encode expected lease states, keys, ack behavior, transport routing, and epoch values.

## Control Flow
Tests reset the global state, perform SMB2 creates/writes/closes that may trigger a break, call a macro that invokes `torture_wait_for_lease_break()` when needed, then compare the recorded break and optional ack output. The V2 macros additionally check `new_epoch` and, except for Samba3 targets, the exact transport pointer.

## State and Persistence Behavior
The header models memory-only state owned by the current torture process. Macros mutate state indirectly by waiting for async callbacks and by updating `held_oplock_level` after oplock break checks.

## Dependencies and Integration Points
It depends on `torture/util.h` assertion macros and SMB2 lease/oplock types from including translation units. It is included by lease and multichannel tests, especially where lease break expectations must be written compactly.

## Risks and Edge Cases
The macros assume local variables such as `tctx` exist in scope for several checks. Key checks only validate the two 64-bit words filled by Samba test helpers (`key` and bitwise inverse). The global structure combines lease and oplock fields, so callers must reset it before each scenario to avoid stale counts.

## Test Signals
The header is itself test instrumentation. Its signal is compile-time integration plus repeated use by lease and multichannel suites to enforce state transitions, ack payloads, no-break windows, transport routing, and epoch increments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/lease_break_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/lock.c -->
# sources/user-network-fs/samba/source4/torture/smb2/lock.c

## Purpose
`lock.c` is the SMB2 byte-range locking torture suite. It validates protocol parameter checking, shared/exclusive lock interaction, pending asynchronous locks, cancellation semantics, zero-byte lock behavior, multi-element atomicity, replay detection, and historical deadlock regressions.

## Important APIs, Types, and Functions
The suite entry point is `torture_smb2_lock_init()`, which registers one- and two-tree tests. The file uses `struct smb2_lock`, `struct smb2_lock_element`, `struct smb2_request`, `struct smb2_create`, `struct smb2_read`, and `struct smb2_write`. Helper macros `CHECK_STATUS`, `CHECK_STATUS_CMT`, `CHECK_STATUS_CONT`, `CHECK_VALUE`, and `WAIT_FOR_ASYNC_RESPONSE` keep assertions concise and event-loop aware.

Key tests include `test_valid_request()` for malformed counts, flags, invalid handles, and range overflow; `test_lock_read_write()` plus `rw-none/shared/exclusive` wrappers for read/write access under locks; `test_lock()`, `test_stacking()`, `test_contend()`, `test_context()`, `test_range()`, and `test_overlap()` for range conflict semantics; `test_async()`, `test_cancel()`, `test_cancel_tdis()`, and `test_cancel_logoff()` for pending lock completion and teardown; `test_zerobytelength()` and `test_zerobyteread()` for zero-length edge cases; `test_unlock()` and `test_multiple_unlock()` for unlock validation and partial multi-lock behavior; `test_truncate()` for overwrite/supersede with held locks; replay tests for resilient/durable/multichannel lock sequence verification; and CTDB/open-vs-brlock deadlock regressions.

## Control Flow
Most tests create `testlock`, create one or more handles to a test file, write a small buffer, issue SMB2 LOCK operations with exact offsets/lengths/flags, and assert returned NTSTATUS values. Async tests issue `smb2_lock_send()`, drive `tevent` until the request is cancellable/pending, then cancel, close, disconnect, log off, or unlock the blocking range before receiving the pending response. Replay tests set specific lock sequence bucket/sequence values and verify whether repeated requests are ignored or treated as new requests according to dialect, resiliency, durable handle, and multichannel capabilities. Deadlock regressions run either a simple lock/unlock relock sequence on CTDB or two continuous async loops, one opening/closing a file and one locking/unlocking another file until a configured timer stops.

## State and Persistence Behavior
The file creates transient files and directories under `testlock` and removes them with `smb2_deltree()`. Lock state lives on the server under open handles and is intentionally exercised across multiple handles, sessions, trees, and teardown events. No local durable state is written, but replay tests intentionally depend on server-side per-open lock sequence buckets, resilient handle state via `FSCTL_LMR_REQ_RESILIENCY`, durable-open state, and multichannel capabilities.

## Dependencies and Integration Points
The suite depends on Samba SMB2 client calls, `smbXcli_conn_protocol()`/capability helpers, `tevent`, torture settings, cluster configuration via `lpcfg_clustering()`, and utility helpers such as `torture_smb2_testfile()`, `torture_smb2_testdir()`, `smb2_util_write()`, and `smb2_util_close()`. The two-tree `overlap` and `open-brlock-deadlock` cases integrate cross-session behavior into the same suite.

## Risks and Edge Cases
The suite encodes target-specific behavior for Windows Server 2008 quirks (`w2k8`) and optional invalid-range support, so configuration mismatches can turn expected failures into false alarms. Several tests intentionally tolerate alternate teardown statuses because servers close file, tree, and session state in different orders. Long-running range and deadlock tests depend on `torture_numops` or an opt-in timeout and can be expensive. The misspelled option `open_brlock_deadlock_timemout` is part of the tested interface in this file.

## Test Signals
The registered subtests provide detailed NTSTATUS signals for every major lock path: invalid parameters, lock conflict versus file lock conflict, cancellation, tree/session teardown, zero-byte locking, multi-lock atomicity, lock sequence replay, CTDB tombstone relock, and async open/byte-range lock progress under load.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/mangle.c -->
# sources/user-network-fs/samba/source4/torture/smb2/mangle.c

## Purpose
`mangle.c` tests SMB2 8.3 short-name/name-mangling behavior. It stress-generates long names, verifies that short aliases can open and delete the same file, tracks short-name collisions, and checks that SMB2 FIND can use a mangled search mask.

## Important APIs, Types, and Functions
`test_one()` creates a file, queries its alternate short name with `smb2_qpathinfo_alt_name()`, unlinks via the short name, recreates via the short name, unlinks via the long name, and stores short-name-to-long-name mappings in an internal TDB. `gen_name()` produces randomized names under `mangle_test\\` with biased prefixes/extensions to provoke mangling collisions. `torture_smb2_mangle()` drives `torture_numops` iterations and reports collision/failure counts. `test_mangled_mask()` creates `verylongfilename`, obtains its short name from `SMB2_FIND_BOTH_DIRECTORY_INFO`, then uses that short name as a single-entry find pattern. `torture_smb2_name_mangling_init()` registers `mangle` and `mangled-mask`.

## Control Flow
The stress test creates the test directory, repeatedly generates a candidate name, and runs the create/query-shortname/delete/recreate/delete cycle. The TDB is used only to notice whether two distinct long names mapped to the same short alias. The mask test refreshes a directory handle before enumerating so the new file is visible, skips dot entries, captures the returned short name, and performs a single-result find with that pattern.

## State and Persistence Behavior
Server-side test files are transient under `mangle_test`. Client-side collision tracking uses an in-memory `TDB_INTERNAL` database and static counters `total`, `collisions`, and `failures`. The file does not persist data beyond the test process.

## Dependencies and Integration Points
The test depends on SMB2 create/close/find/pathinfo/unlink helpers, TDB utility wrappers, random name generation from the C runtime, and torture settings such as `torture_numops` and `progress`.

## Risks and Edge Cases
The randomized stress path can be nondeterministic and may miss rare collision patterns in short runs. Static counters and TDB state are process-global. The test treats inability to unlink by long name after short-name recreation as a failure but continues to clean up via the short path. Short-name support can be disabled or filesystem-dependent, making this suite sensitive to server/share configuration.

## Test Signals
Useful signals are collision counts, failures unlinking recreated files, successful alternate-name querying, successful short-name create/unlink, and successful SMB2 FIND with `SMB2_CONTINUE_FLAG_SINGLE` and a mangled mask.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/mangle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/max_allowed.c -->
# sources/user-network-fs/samba/source4/torture/smb2/max_allowed.c

## Purpose
`max_allowed.c` tests SMB2 `SEC_FLAG_MAXIMUM_ALLOWED` behavior, privilege-sensitive access masks, and read-only file/directory access calculations.

## Important APIs, Types, and Functions
`torture_smb2_maximum_allowed()` creates a restrictive security descriptor granting authenticated users read rights, creates `torture_maximum_allowed`, discovers the owner SID, checks restore/backup/security privileges with `torture_smb2_check_privilege()`, then iterates every single access bit combined with `SEC_FLAG_MAXIMUM_ALLOWED`. It expects success only for the computed allowed mask or maximum-allowed alone, with `NT_STATUS_PRIVILEGE_NOT_HELD` for SACL requests without privilege and `NT_STATUS_ACCESS_DENIED` otherwise. It finally restores a DACL permitting delete.

`torture_smb2_read_only_file()` and `torture_smb2_read_only_dir()` create read-only objects, open with maximum allowed and maximal-access query context, verify returned maximal and actual access masks through `RAW_FILEINFO_ACCESS_INFORMATION`, and test write/create/delete behavior. `torture_smb2_max_allowed()` registers the three subtests.

## Control Flow
The maximum-allowed test builds a known ACL baseline, records privilege capabilities for the current user, closes the original handle, then repeatedly opens the same file with `SEC_FLAG_MAXIMUM_ALLOWED | (1u << i)`. Cleanup reopens with `WRITE_DAC`, sets a delete-capable DACL, closes handles, unlinks the file, and frees the context. The read-only tests create an object, reopen it with maximum allowed, inspect effective access, and then try operations that should be denied for files or allowed inside read-only directories.

## State and Persistence Behavior
The only persistent server state is the temporary file or directory and its security descriptor/attributes; cleanup removes it. The tests intentionally mutate DACLs to make cleanup possible after restrictive setup.

## Dependencies and Integration Points
The code uses Samba security descriptor construction, SID formatting, privilege lookup helpers, SMB2 create/getinfo/setinfo utilities, and the torture `sacl_support` setting to skip SACL-related expectations where configured.

## Risks and Edge Cases
Expected masks depend on the authenticated user's privileges and server SACL support. The read-only file expected access mask follows MS-FSA rules and explicitly removes write-data, append/add-subdir, and delete-child bits; server-specific attribute enforcement can surface here. Cleanup depends on successful DACL reset.

## Test Signals
Signals include per-bit open NTSTATUS, privilege-differentiated security failures, maximal access create context values, actual access infolevel masks, denied write to a read-only file, and successful child create/delete inside a read-only directory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/max_allowed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/maxfid.c -->
# sources/user-network-fs/samba/source4/torture/smb2/maxfid.c

## Purpose
`maxfid.c` stress-tests how many SMB2 file identifiers/open handles a server and client test environment can sustain on one tree connection.

## Important APIs, Types, and Functions
The sole exported test function is `torture_smb2_maxfid()`. It reads the `maxopenfiles` torture setting, defaults to `65520`, opens an SMB2 connection, allocates an array of `struct smb2_handle`, creates a directory fanout under `smb2_maxfid`, then opens files until the requested limit is reached or the server returns an error.

## Control Flow
After connecting and creating the base directory, the test creates one subdirectory per 1000 intended files to avoid a single huge directory. It then loops from zero to `max_handles - 1`, creates `smb2_maxfid\\<bucket>\\<i>`, stores each returned handle, and stops on first create failure. It reports whether the configured limit was reached, closes every successfully opened handle, and removes the tree.

## State and Persistence Behavior
The server accumulates many live file handles and created test files during the run. Local state is the handle array and the `maxfid` count. Cleanup closes only handles that were actually opened and then deletes the base directory tree.

## Dependencies and Integration Points
The file uses `torture_smb2_connection()`, SMB2 create/close helpers, `torture_smb2_testdir()`, `smb2_deltree()`, and the `maxopenfiles` setting. The source comment notes socket-wrapper limits and `SOCKET_WRAPPER_MAX_SOCKETS` for larger local test runs.

## Risks and Edge Cases
This is intentionally resource-heavy. Memory allocation, server open-file limits, client socket-wrapper limits, share quotas, and filesystem directory scaling can all terminate the loop before the configured maximum. On early failure, cleanup still depends on closing all stored handles and deleting a potentially large tree.

## Test Signals
Primary signals are the number of successful opens before failure, the exact create error at the limit, successful cleanup closes, and whether the configured `maxopenfiles` ceiling was reached.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/maxfid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/maxwrite.c -->
# sources/user-network-fs/samba/source4/torture/smb2/maxwrite.c

## Purpose
`maxwrite.c` probes the maximum SMB2 write size accepted by a server and verifies data integrity for successful large writes.

## Important APIs, Types, and Functions
`torture_smb2_maxwrite()` establishes an SMB2 connection, creates `testmaxwrite.dat`, and delegates to `torture_smb2_write()`. `torture_smb2_write()` performs a binary search between one byte and 80,000,000 bytes using `smb2_write()` and `smb2_read()` on a single handle. It fills each candidate buffer with a deterministic byte pattern and compares the read-back buffer after successful writes.

## Control Flow
For each midpoint size, the helper allocates a temporary data blob, writes from offset zero, and either lowers `max` on failure or raises `min` on success. On write failure it closes and recreates the file handle; if close fails because the server disconnected, it reconnects and recreates. After every successful write it reads the same length from offset zero and checks length/content. When the search converges it closes and unlinks the test file.

## State and Persistence Behavior
The test repeatedly overwrites a single temporary file and removes it at the end. Local state is the binary-search bounds and the generated buffer for the current attempt. A server disconnect can replace the tree connection inside the helper.

## Dependencies and Integration Points
The code uses SMB2 create/read/write/close/unlink helpers and torture connection creation. It is an older stress-style test that exercises server max write request handling rather than a negotiated-size helper.

## Risks and Edge Cases
The helper always returns `NT_STATUS_OK` after convergence even if read-back mismatches were only logged, so integrity failures may not fail the test unless a status check fails. The local `tree` pointer is passed by value to the helper; reconnecting inside the helper does not update the caller, though the helper finishes cleanup itself. Large allocations and very large writes can be expensive.

## Test Signals
Signals include logged candidate sizes, write failure boundaries, reconnect handling after disconnect, read status, read length/content comparison, and the converged maximum size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/maxwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/mkdir.c -->
# sources/user-network-fs/samba/source4/torture/smb2/mkdir.c

## Purpose
`mkdir.c` is a compact SMB2 directory create/remove behavior test. It checks normal mkdir/rmdir, collisions, file-versus-directory status codes, invalid path syntax, and missing parent path handling.

## Important APIs, Types, and Functions
The only test function is `torture_smb2_mkdir()`. It uses `smb2_util_setup_dir()`, `smb2_util_mkdir()`, `smb2_util_rmdir()`, `smb2_create_complex_file()`, `smb2_util_unlink()`, and `smb2_deltree()`. The base directory is `mkdirtest`, and the main target path is `mkdirtest\\mkdir.dir`.

## Control Flow
The test creates the base directory, creates `mkdir.dir`, verifies a second mkdir returns `NT_STATUS_OBJECT_NAME_COLLISION`, removes it, verifies a second rmdir returns `NT_STATUS_OBJECT_NAME_NOT_FOUND`, creates a file at the same path, verifies mkdir collides with the file, verifies rmdir of the file returns `NT_STATUS_NOT_A_DIRECTORY`, removes the file, then checks `..\\..\\..` and a missing nested parent path for syntax/path-not-found errors.

## State and Persistence Behavior
All server-side state is temporary under `mkdirtest`. Cleanup always calls `smb2_deltree()` on the base directory.

## Dependencies and Integration Points
This test depends on SMB2 utility wrappers from the torture suite and is likely registered by the broader SMB2 torture initialization code rather than defining a local suite.

## Risks and Edge Cases
Expected status codes are precise and may expose server differences in path normalization, dot-dot handling, or file/directory collision mapping. If base directory setup fails, later assertions do not run.

## Test Signals
The meaningful signals are exact NTSTATUS values for create collision, missing remove target, rmdir-on-file, bad path syntax, and missing parent directory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/multichannel.c -->
# sources/user-network-fs/samba/source4/torture/smb2/multichannel.c

## Purpose
`multichannel.c` tests SMB3 multichannel negotiation, channel binding, network-interface discovery, oplock/lease break routing across bound transports, channel retry behavior under blocked transports, maximum channel limits, and a channel-merging race regression.

## Important APIs, Types, and Functions
The suite entry point is `torture_smb2_multichannel_init()`, which creates `generic`, `oplocks`, `leases`, and `bugs` subsuites. `test_ioctl_network_interface_info()` sends `FSCTL_QUERY_NETWORK_INTERFACE_INFO` and decodes `fsctl_net_iface_info`. `test_multichannel_create_channel()` connects a transport and optionally binds it to a parent session using `smb2_session_channel()` and `smb2_session_setup_spnego()`, installs oplock and lease handlers, and sends keepalive so async break handling is active. `test_multichannel_create_channel_array()` and `test_multichannel_create_channels()` build channel sets sharing a client GUID.

Oplock tests cover basic break delivery, retry when the break channel is blocked, and two 32-channel models: observed Windows behavior where only the latest channel is used and specification behavior where breaks are attempted across channels. Lease tests mirror basic/retry/cross-channel-ack cases and a V2 epoch/order test over 32 blocked channels. `test_multichannel_num_channels()` checks the Windows-style 32-channel limit. `test_multichannel_bug_15346()` opens 31 raw SMB connections, negotiates them concurrently, verifies echo, then binds each as a session channel and runs a root getinfo.

## Control Flow
Each behavioral test first checks SMB3 dialect, `SMB2_CAP_MULTI_CHANNEL`, and interface info support. It then creates `multichanneltestdir`, opens files with leases or oplocks on secondary channels, opens conflicting handles from the primary session, and inspects which transport received a break. Blocking helpers from `block.h` simulate unresponsive channels so retry and timeout behavior can be observed. Break handler state is reset between phases to isolate counts. Cleanup restores the original primary session pointer, closes handles on the right tree, unlinks files, deletes the base directory, unblocks transports, and frees channel trees.

## State and Persistence Behavior
Persistent server state is limited to temporary files/directories and server-side open/lease/oplock/channel state. Client-side state includes arrays of `smb2_tree` pointers, per-channel timing structures, global `break_info` and `lease_break_info`, blocked transport state, and async `tevent_req` objects for the bug regression. Durable V2 create fields are initialized in helper routines but the tests assert Samba currently reports non-durable opens in these scenarios.

## Dependencies and Integration Points
The file integrates many Samba subsystems: SMB2 connect/session/channel APIs, ioctl/NDR decoding, credentials and loadparm configuration, resolver/socket helpers, `smbXcli` negotiation/echo, security definitions, oplock and lease break handlers, and transport-blocking test utilities. It relies on `oplock_break_handler.h` and `lease_break_handler.h` for shared callback state.

## Risks and Edge Cases
The tests intentionally distinguish Samba, Windows, and specification behavior, so some expectations are split into separate subtests. Timing-sensitive checks require break retries or opens to take more than 35 seconds when channels are blocked, which can make the suite slow and environment-sensitive. The same global break state is reused across many channels and must be reset carefully. Several cleanup blocks close handles through specific secondary trees; incorrect tree selection can mask routing bugs or cause noisy cleanup statuses. Channel count expectations assume a 32-channel server limit.

## Test Signals
Signals include SMB3/multichannel capability skips, decoded interface info, successful channel binding, local TCP port diagnostics, break counts and receiving transports, lease epoch increments, ordered per-channel break numbers, open durations under blocked transports, expected `NT_STATUS_INSUFFICIENT_RESOURCES` for channel 33, echo/getinfo success after concurrent negotiation, and absence of assertion flags in the bug 15346 async state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/multichannel.c -->
