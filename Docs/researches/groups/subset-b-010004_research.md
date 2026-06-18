# Research: subset-b-010004

Grouped research for Samba SMB2 torture tests around oplocks, oplock break handling, reads, read/write behavior, and rename semantics. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/oplock.c -->
# sources/user-network-fs/samba/source4/torture/smb2/oplock.c

## Purpose
This file implements Samba's SMB2 oplock torture coverage. It exercises exclusive, batch, level-II, stream, byte-range-lock, timeout, stat-open, stale-oplock, benchmark, manual hold, and kernel-oplock interactions against one or more SMB2 tree connections. The tests validate observable SMB2 server behavior: granted oplock levels, asynchronous oplock-break notifications, break acknowledgements, sharing violations, delete-pending responses, timeout handling, and race-prone deferred-open scenarios.

## Important APIs, Types, And Functions
The file is built around Samba torture APIs (`torture_suite_add_1smb2_test`, `torture_suite_add_2smb2_test`, `torture_assert_*`, `torture_comment`) and SMB2 client calls (`smb2_create`, `smb2_create_send/recv`, `smb2_break_send/recv`, `smb2_close_send`, `smb2_read`, `smb2_write`, `smb2_lock`, `smb2_getinfo_file`, `smb2_setinfo_file`, `smb2_composite_setpathinfo`, `smb2_util_*`). A file-local `break_info` struct records the most recent break handle, requested level, request body, count, failures, and failure status.

Break handler variants are central integration points: `torture_oplock_handler` acks to the server-requested level; `torture_oplock_handler_ack_to_none` always acks none; `torture_oplock_handler_level2_to_none` records level-II-to-none without sending the invalid SMB2 ack; `torture_oplock_handler_two_notifications` supports level-II then none sequences; `torture_oplock_handler_close` closes on break; and `torture_oplock_handler_timeout` deliberately leaves the break unanswered. `open_smb2_connection_no_level2_oplocks()` creates a connection with `options.use_level2_oplocks = false`.

Suite registration happens in `torture_smb2_oplocks_init()` for the standard oplock suite and `torture_smb2_kernel_oplocks_init()` for kernel-oplock coverage. Additional exported/manual helpers include `test_smb2_bench_oplock()` and `test_smb2_hold_oplock()`.

## Control Flow
Most test cases follow the same shape: create or clean `BASEDIR`, install a transport oplock handler, build a `union smb_open` or `struct smb2_create`, open a file with a requested oplock, perform a conflicting operation from another tree or the same tree, pump events with `torture_wait_for_oplock_break()`, then assert the status, granted oplock level, break count, break level, and ack failure state.

The exclusive tests cover conflicts from second opens, unlink, path-based EOF set, attributes-only opens, parent-directory delete access during rename, and create-disposition-specific break targets. The batch tests cover unlink, close-on-break, self reads/writes, shared-read downgrade to level II, attributes-only open behavior, overwrite/supersede dispositions, path EOF/allocation updates, qpathinfo, rename setinfo, delete-on-close, no-level-II clients, timeouts, streams, and stat-open access masks. BRL tests show when byte-range lock acquisition does or does not contend an existing oplock. `levelII500` verifies invalid protocol when a client acks a level-II-to-none break; `levelII501` schedules delayed break responses and multiple async opens with tevent timers; `levelII502` uses `smbXcli_conn_samba_suicide()` to test stale level-II cleanup.

The benchmark loops across multiple SMB2 connections, each requesting a batch oplock on the same non-shared file while close-on-break passes the oplock between connections. The hold helper opens a fixed set of files and waits indefinitely for manual break interaction. Kernel-oplock tests verify Samba behavior when server-side/kernel leases, alternate data streams, deferred opens, and a local child process holding a Linux lease are involved.

## State And Persistence
Persistent server state is limited to files and directories under `oplock_test` plus kernel test filenames such as `test_kernel_oplock*.dat`; tests try to clean with `smb2_util_unlink()` and `smb2_deltree()`. Client-side state is mostly per-test handles and the file-local `break_info`, which is frequently reset with `ZERO_STRUCT`. Transport handlers are mutable session state on `tree->session->transport->oplock` and must be set per connection. Async flows persist pending `smb2_request` and tevent timer state until callbacks complete. Kernel-oplock code may fork a child process, register signal handlers, and use a local path from the `localdir` torture setting.

## Dependencies And Integration Points
The file depends on Samba SMB2/libcli calls, SMB composite setpathinfo, cmdline credentials, resolve and loadparm configuration, tevent, torture helper headers, transport blocking helpers from `torture/smb2/block.h`, security access masks, and optional Linux kernel oplock support (`HAVE_KERNEL_OPLOCKS_LINUX`, `fcntl(F_SETLEASE)`, real-time signals). It integrates with the SMB2 torture runner through `torture_smb2_oplocks_init()` and `torture_smb2_kernel_oplocks_init()`, and with server-specific behavior through settings such as `oplocktimeout`, `nprocs`, `timelimit`, `progress`, `host`, `share`, and `localdir`.

## Risks
The tests are timing-sensitive: break waits are short, timeout tests depend on configured oplock timeout, and deferred-open/kernel-oplock cases intentionally exercise races. The file-local `break_info` and mutable transport handlers make tests non-reentrant and order-sensitive if run concurrently on shared connections. Some cleanup paths close handles on the originating tree even when a handle came from another tree, which is tolerated by the suite pattern but is a place to audit when changing tests. Kernel-oplock tests depend on Linux lease semantics, signals, local filesystem paths that match the SMB share, and child process cleanup.

## Test Signals
Important signals are exact NTSTATUS checks (`OK`, `SHARING_VIOLATION`, `DELETE_PENDING`, `INVALID_OPLOCK_PROTOCOL`), granted oplock levels (`BATCH`, `EXCLUSIVE`, `II`, `NONE`, `NO_OPLOCK_RETURN`), `break_info.count`, `break_info.level`, `break_info.failures`, elapsed timeout bounds, stream/base-file independence, BRL self-contention behavior, stat-open masks that avoid breaks, and successful suite registration under `smb2.oplock` and `smb2.kernel-oplocks`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/oplock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/oplock_break_handler.c -->
# sources/user-network-fs/samba/source4/torture/smb2/oplock_break_handler.c

## Purpose
This helper file provides shared oplock-break state and reusable handlers for SMB2 torture tests outside `oplock.c`. It centralizes break acknowledgement, optional ack suppression, and short event-loop polling for tests that expect asynchronous oplock breaks.

## Important APIs, Types, And Functions
It defines the global `struct break_info break_info` declared in the header. `torture_oplock_ack_handler()` records the incoming handle, break level, count, and received transport; validates that the callback arrived on the expected transport; optionally skips acknowledgement when `break_info.oplock_skip_ack` is set; otherwise sends `smb2_break_send()` and receives completion in `torture_oplock_ack_callback()`. `torture_oplock_ignore_handler()` deliberately ignores break requests while still returning true to the transport callback path. `torture_wait_for_oplock_break()` uses a one-second tevent timer and loops until either a new break arrives or the timeout fires.

## Control Flow
Consumers reset `break_info`, install one of these functions into `tree->session->transport->oplock.handler`, and then trigger a conflicting SMB2 operation. On break notification, the ack handler populates `break_info.br.in`, logs with `torture_comment()`, and asynchronously sends the SMB2 break response. The wait helper snapshots the old break count, installs a timer on `tctx->ev`, and calls `tevent_loop_once()` while waiting for `break_info.count` to advance.

## State And Persistence
State is process-global and mutable through `break_info`: test context, skip-ack flag, last handle, last level, `struct smb2_break`, count, failure count/status, and received transport pointer. No filesystem state is changed by this helper, but it drives network protocol acknowledgements that alter server-side oplock state.

## Dependencies And Integration Points
The file depends on Samba SMB2 client structures and calls, the torture framework, `smbXcli_base`, `oplock_break_handler.h`, and tevent timers. It is intended for SMB2 torture tests that need consistent break tracking; users must set `break_info.tctx` through `torture_reset_break_info()` or otherwise before relying on log messages.

## Risks
The global `break_info` is not safe for concurrent independent tests. The ack callback assumes the original `break_info.br` remains the right receive object for the outstanding request. `torture_wait_for_oplock_break()` waits only one second, so slow or blocked servers can produce false negatives. `torture_oplock_ignore_handler()` does not increment counters, so tests using it cannot infer whether a break arrived from `break_info`.

## Test Signals
Expected signals include `break_info.count` increments, `break_info.level` matching the server-requested downgrade, `break_info.failures == 0` after ack completion, `break_info.failure_status` on failed ack receive, and `break_info.received_transport` matching the tree transport.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/oplock_break_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/oplock_break_handler.h -->
# sources/user-network-fs/samba/source4/torture/smb2/oplock_break_handler.h

## Purpose
This header exposes the shared SMB2 oplock-break testing contract: a common break-tracking struct, handler prototypes, wait helper, and reset helper for torture tests.

## Important APIs, Types, And Functions
`struct break_info` carries the torture context, `oplock_skip_ack`, last SMB2 handle, last break level, SMB2 break request/response object, break count, failure count, failure NTSTATUS, and the transport that received the break. The header declares global `break_info`, `torture_oplock_ack_handler()`, `torture_oplock_ignore_handler()`, and `torture_wait_for_oplock_break()`. The inline `torture_reset_break_info()` zeroes a supplied `struct break_info` and restores its `tctx` pointer.

## Control Flow
Tests include the header, call `torture_reset_break_info(tctx, &break_info)`, install a handler on an SMB2 transport, perform an operation expected to break an oplock, and then call `torture_wait_for_oplock_break()` before checking the global fields.

## State And Persistence
The header itself has no runtime storage except the external declaration, but it defines the layout of the process-global state owned by `oplock_break_handler.c`. Resetting is destructive for all tracked break fields except the torture context pointer restored afterward.

## Dependencies And Integration Points
The declarations require Samba types such as `struct torture_context`, `struct smb2_handle`, `struct smb2_break`, `NTSTATUS`, and `struct smb2_transport` from the including translation unit's Samba headers. It integrates with the SMB2 transport callback signature and the torture framework.

## Risks
Because `break_info` is global, including tests must coordinate resets and cannot safely run independent break assertions on the same process state. The inline reset uses `ZERO_STRUCTP`, so any future fields needing nonzero defaults must be explicitly restored after the zero. Header consumers must include compatible Samba type declarations before or alongside this header.

## Test Signals
Compile-time signals are successful inclusion in SMB2 torture files and type compatibility with the transport oplock callback. Runtime signals are a reset `break_info.count == 0`, `tctx` preserved after reset, and expected handler-populated fields after a break.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/oplock_break_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/read.c -->
# sources/user-network-fs/samba/source4/torture/smb2/read.c

## Purpose
This file implements SMB2 read torture tests, including EOF/min-count semantics, read-position behavior, directory-handle read errors, access-mask requirements, a regression for read response body padding, and delayed AIO cancel behavior.

## Important APIs, Types, And Functions
The main suite is registered by `torture_smb2_read_init()` with tests `eof`, `position`, `dir`, `access`, and `bug14607`. A separate `torture_smb2_aio_delay_init()` suite registers `aio_cancel` for shares using the `delay_inject` VFS module. Tests use `struct smb2_read`, `struct smb2_handle`, `union smb_fileinfo`, `DATA_BLOB`, `smb2_read`, `smb2_read_send/recv`, `smb2_cancel`, `smb2_util_write`, `smb2_util_close`, `torture_smb2_testfile`, `torture_smb2_testdir`, `torture_smb2_testfile_access`, low-level `smb2cli_read`, and `smb2cli_ioctl`.

## Control Flow
`test_read_eof()` creates a file, verifies empty-file read returns EOF, writes 64 KiB, and then probes reads at start, exactly EOF, zero-length EOF, one byte before EOF, and inconsistent `min_count` combinations. `test_read_position()` checks whether a read advances current position, with a Windows-specific expected value difference. `test_read_dir()` opens a directory and verifies reads normally return `INVALID_DEVICE_REQUEST`, with Windows-specific zero-length exceptions. `test_read_access()` proves read succeeds with read-data or execute rights but fails with only read-attributes. `test_read_bug14607()` validates normal `smb2_read` and raw `smb2cli_read` before and after enabling the Samba torture FSCTL that pads read response bodies to an 8-byte boundary. `test_aio_cancel()` sends an async read, waits until the request can be cancelled, sends cancel, and still expects the read receive path to complete OK.

## State And Persistence
Tests create `smb2_readtest.dat` and `smb2_readtest.dir`, write temporary 64 KiB buffers, and clean handles and files on completion. Temporary allocations use talloc contexts scoped to the tree or test. The bug14607 test modifies server-side torture behavior through `FSCTL_SMBTORTURE_GLOBAL_READ_RESPONSE_BODY_PADDING8`, which may persist for the server process beyond the immediate request depending on the test FSCTL implementation.

## Dependencies And Integration Points
The file depends on Samba SMB2 calls, tevent for async/cancel, torture helpers, `smbXcli_base`, and generated ioctl definitions for the SMB torture FSCTL. It integrates with target-specific settings through `torture_setting_bool(torture, "windows", false)` and expects the delay AIO suite to run only where delayed async reads are configured.

## Risks
The tests encode Windows/Samba behavioral differences for current file position and directory zero-length reads, so changing expectations needs target awareness. `bug14607` depends on a Samba-specific FSCTL and skips when unsupported. `test_aio_cancel()` relies on `req->cancel.can_cancel` eventually becoming true; without a delay-inject share it may complete too quickly or not exercise the intended path.

## Test Signals
Key signals are exact NTSTATUS results (`OK`, `END_OF_FILE`, `INVALID_DEVICE_REQUEST`, `ACCESS_DENIED`), returned read lengths, byte-for-byte buffer equality for `smb2_read` and `smb2cli_read`, successful skip on unsupported FSCTL, and successful cancel/receive for delayed AIO reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/read_write.c -->
# sources/user-network-fs/samba/source4/torture/smb2/read_write.c

## Purpose
This file provides SMB2 read/write torture tests for data integrity, invalid offset boundaries, max-file-size edge behavior, delete-on-close read/write behavior, and append/write-data access semantics.

## Important APIs, Types, And Functions
`torture_smb2_readwrite_init()` registers `rw1`, `rw2`, `invalid`, and `append`. The implementation uses `struct smb2_create`, `struct smb2_read`, `struct smb2_write`, `union smb_setfileinfo`, `union smb_fileinfo`, `smb2_create`, `smb2_write`, `smb2_read`, `smb2_setinfo_file`, `smb2_getinfo_file`, `smb2_util_write`, `smb2_util_close`, `smb2_util_unlink`, `smb2_deltree`, and torture buffer helpers such as `generate_random_buffer()`.

## Control Flow
`run_smb2_readwritetest()` removes `torture2.lck`, opens it read/write on one tree and read-only on another tree, then runs `torture_numops` iterations. Each iteration chooses a random buffer length up to 128 KiB, writes it at offset 0 through the first handle, reads the same length through the second handle, and compares bytes exactly. `run_smb2_wrap_readwritetest()` reuses the same tree for both sides to cover same-session behavior.

`test_rw_invalid()` creates `smb2_writetest.dat`, marks it delete-on-close, writes 64 KiB, then probes read offsets around EOF, `INT64_MAX`, `INT64_MIN`, and negative values encoded as unsigned. It also checks write behavior for negative offsets, zero-length writes at high offsets, a Samba max-file-size boundary (`0xfffffff0000`), and target-specific disk-full versus Samba success at `MAXFILESIZE - 1`. `test_append()` verifies that `SEC_FILE_APPEND_DATA` alone does not force SMB2 writes to append when an explicit offset is supplied, then verifies a write-data handle can extend the file at offset 1000.

## State And Persistence
The tests create temporary files `torture2.lck` and `smb2_writetest.dat`, set delete-on-close in one invalid-path test, and remove files during cleanup. Random test buffers are stack allocated. Handles are zeroed after successful close so cleanup can avoid double-closing.

## Dependencies And Integration Points
The file depends on SMB2 client calls, torture framework globals such as `torture_numops`, target detection macros (`TARGET_IS_SAMBA3`, `TARGET_IS_SAMBA4`), and utility helpers from `torture/util.h` and `torture/smb2/proto.h`. It integrates with both two-connection and same-connection torture registration.

## Risks
The random integrity loop can be expensive or flaky if `torture_numops` is very high or the backing share has caching/consistency bugs. The invalid-offset expectations are sensitive to signed/unsigned offset handling and server maximum file size policy. The delete-on-close setup means cleanup and subsequent operations depend on handle lifetime. Append semantics are subtle because SMB2 explicit offsets differ from POSIX append intuition.

## Test Signals
Signals include exact read/write statuses, `w.out.nwritten`, returned read lengths, byte-for-byte buffer equality, file size checks after append/write-data scenarios, and target-specific handling of the max-file-size boundary.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/read_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/rename.c -->
# sources/user-network-fs/samba/source4/torture/smb2/rename.c

## Purpose
This file implements SMB2 rename torture coverage. It validates rename permission requirements, parent directory share/delete interactions, MS Word style save behavior, directory rename with open children, asynchronous directory rename stress, timestamp preservation, close full-information after rename, and renaming while another connection has the file open.

## Important APIs, Types, And Functions
`torture_smb2_rename_init()` registers the suite. Synchronous cases use `union smb_open`, `union smb_close`, `union smb_setfileinfo`, `union smb_fileinfo`, `struct smb2_create`, `struct smb2_close`, `smb2_create`, `smb2_setinfo_file`, `smb2_getinfo_file`, `smb2_close`, and `smb2_deltree`. The async benchmark uses custom tevent state machines: `rename_one_dir_cycle_send/recv()`, `rename_dir_bench_send/recv()`, and `rename_dirs_bench_send/recv()`, layered over `smb2_setinfo_file_send`, `smb2_create_send`, and `smb2_close_send`.

## Control Flow
The basic rename tests create `test_rename`, open files with different access/share masks, submit `RAW_SFILEINFO_RENAME_INFORMATION`, and assert either success or a precise failure. `simple` succeeds with delete access; `simple_nodelete` fails without delete access; `no_sharing` shows a non-shared handle can rename itself; parent-directory tests distinguish delete access and share-delete combinations that should block or allow child rename. `msword` replays observed Word 2010 access masks and create options. `rename_dir_openfile` verifies a directory cannot be renamed while it contains an open file.

The async benchmark opens or creates multiple directories in parallel, renames each directory through numbered names repeatedly, marks it delete-on-close, and closes it. `simple_modtime` creates two files separated by a five-second sleep, renames each, and confirms write timestamps are preserved. `close-full-information` creates two open handles on a source file, opens a delete-capable third handle, renames to `renamed.dat`, and verifies close responses with `SMB2_CLOSE_FLAGS_FULL_INFORMATION` still contain file attributes on both connections. `rename-open` proves a delete-capable handle can rename while a second connection has a read handle with delete sharing.

## State And Persistence
The suite creates and removes `test_rename` plus temporary files like `file.txt`, `newname.txt`, `file1.txt`, `file2.txt`, `tmp1.txt`, `request.dat`, and `renamed.dat`. Async benchmark state persists in tevent request structs until callbacks complete, and directory names mutate repeatedly. Some tests sleep for timestamp propagation or mtime differentiation.

## Dependencies And Integration Points
The file depends on SMB2 calls, tevent and `tevent_ntstatus`, torture utilities, generated security access masks, and standard sleep timing. It integrates into the SMB2 torture runner as `smb2.rename` with both one-tree and two-tree tests.

## Risks
Many access masks are raw constants or broad composed masks, so semantic changes should be checked carefully against Windows behavior. Rename behavior is sensitive to share modes, delete access, open child handles, and whether the new name already exists. The benchmark has asynchronous lifetime and cleanup risks if a callback errors before delete-on-close. Sleep-based timestamp/propagation checks can be slow or environment-sensitive.

## Test Signals
Signals include exact NTSTATUS values (`OK`, `ACCESS_DENIED`, `SHARING_VIOLATION`), successful `RAW_FILEINFO_SMB2_ALL_INFORMATION` after rename, preserved `write_time`, close full-information `file_attr == 0x20`, successful tevent polling and NTSTATUS from async benchmark, and final cleanup by `smb2_deltree()` or unlink.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/rename.c -->
