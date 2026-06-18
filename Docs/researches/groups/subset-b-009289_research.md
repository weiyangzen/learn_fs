# subset-b-009289 research

Grouped research report for liburing tests and LTP filesystem helpers. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/thread-exit.c -->
# sources/test-tools/liburing/test/thread-exit.c

Purpose: regression test that io_uring work submitted by short-lived pthreads is not canceled merely because the submitting thread exits, while still relying on process/ring teardown to cancel long-lived work. It submits writes that should complete and poll requests that remain pending.

Important APIs/types/functions: `struct d`, global `g_buf`, `free_g_buf`, `do_io`, `pthread_create`, `pthread_join`, `pipe`, `t_create_file`, `io_uring_queue_init`, `io_uring_prep_write`, `io_uring_prep_poll_add`, `io_uring_submit`, and `io_uring_wait_cqe`.

Control flow: main creates a pipe and ring, opens either a user-provided file or `.thread.exit`, then starts and joins eight threads. Each thread allocates a write buffer, queues one write and one poll, submits both SQEs, and exits. Main then reaps exactly eight write CQEs and requires each result to equal `WSIZE`; it does not reap the sticky poll requests before process exit.

State/persistence behavior: writes 512-byte chunks at monotonically increasing offsets. Buffers are kept in `g_buf` until completions arrive so submitted write memory remains valid after thread exit. Temporary file cleanup is by unlink-after-open.

Dependencies/integration: depends on pthreads, pipes, regular-file writes, poll wait queues, liburing helpers, and kernel io-wq lifetime semantics.

Risks/test signals: skips on inaccessible target file. Failures show as missing CQEs, short write results, bad submit counts, or worker-side `d.err` increments. The shared `struct d` is safe only because each thread is joined before the next mutation.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/thread-exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/timens-abs-timer.c -->
# sources/test-tools/liburing/test/timens-abs-timer.c

Purpose: regression test that absolute io_uring timers honor the caller's time namespace. It targets `IORING_TIMEOUT_ABS` and `IORING_ENTER_ABS_TIMER`, both of which must convert namespace-visible absolute monotonic deadlines to host time instead of firing immediately under a shifted time namespace.

Important APIs/types/functions: `write_one`, `enter_unpriv_userns_timens`, `ts_to_ns`, `elapsed_ns`, `test_op_timeout_abs`, `test_enter_abs_timer`, `run_tests_in_timens_grandchild`, `run_in_timens`, `unshare(CLONE_NEWUSER | CLONE_NEWTIME)`, `/proc/self/{setgroups,uid_map,gid_map,timens_offsets}`, `io_uring_prep_timeout`, and `io_uring_enter2`.

Control flow: main forks so namespace setup cannot contaminate the parent. The child creates a user and time namespace, maps uid/gid 0, applies a `monotonic -10 0` offset, then forks a grandchild because time namespaces apply to future children. The grandchild runs both timer paths with an absolute deadline of current monotonic time plus one second and validates observed elapsed time.

State/persistence behavior: no filesystem state beyond procfs namespace control writes. The durable state under test is kernel timer conversion state associated with the task namespace and io_uring wait/timeout paths.

Dependencies/integration: requires kernel time namespace support, permission to create unprivileged user namespaces, `IORING_FEAT` support sufficient for the tested operations, and direct syscall wrappers from `../src/syscall.h`.

Risks/test signals: skips for unsupported or prohibited namespaces. A failure is an elapsed time under 100 ms, strongly indicating missing `timens_ktime_to_host()` conversion; under 900 ms is also treated as early firing.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/timens-abs-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/timeout-new.c -->
# sources/test-tools/liburing/test/timeout-new.c

Purpose: focused tests for `io_uring_wait_cqe_timeout()` and multi-threaded getevents timeout behavior. It verifies returns both before and after timeout and checks that multiple waiters on the same ring handle wakeups without invalid errors.

Important APIs/types/functions: `msec_to_ts`, `test_return_before_timeout`, `test_return_after_timeout`, `__reap_thread_fn`, `reap_thread_fn0`, `reap_thread_fn1`, `test_multi_threads_timeout`, `io_uring_wait_cqe_timeout`, `io_uring_queue_init`, `io_uring_prep_nop`, and `IORING_SETUP_SQPOLL`.

Control flow: main initializes a normal ring, requires `IORING_FEAT_EXT_ARG`, and runs a NOP that should complete before a 200 ms timeout, then an empty wait that should return `-ETIME` near 200 ms. It repeats the same checks on an SQPOLL ring, with a one-shot retry for possible SQPOLL wakeup timing. Finally it starts two waiter threads, waits until both entered `io_uring_wait_cqe_timeout()`, submits one NOP, and accepts either one waiter consuming it or timeout on the other.

State/persistence behavior: only in-memory counters and thread return globals persist during the test. No files are created.

Dependencies/integration: exercises liburing's extended wait API, kernel `GETEVENTS` timeout support, SQPOLL submission, pthread synchronization, and helper timing `mtime_since_now`.

Risks/test signals: timing-sensitive around SQPOLL startup and thread scheduling. Failures are wrong timeout error, elapsed time outside 100-300 ms, bad NOP completion, or waiter return values other than success/`-ETIME`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/timeout-new.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/timeout.c -->
# sources/test-tools/liburing/test/timeout.c

Purpose: broad regression suite for io_uring timeout operations. It covers relative, absolute, immediate-argument, counted, linked, drained, removable, updatable, multishot, CQ overflow, SQPOLL, eventfd, and process-exec cancellation behavior.

Important APIs/types/functions: `msec_to_ts`, `t_prep_timeout`, `test_single_timeout*`, `test_multi_timeout*`, `test_timeout_flags*`, `test_update_timeout`, `test_update_multishot_timeouts`, `test_timeout_link_cancel`, `test_not_failing_links`, `test_timeout_multishot*`, `test_eventfd`, `io_uring_prep_timeout`, `io_uring_prep_timeout_remove`, `io_uring_prep_timeout_update`, `IORING_TIMEOUT_IMMEDIATE_ARG`, `IORING_TIMEOUT_ABS`, `IORING_TIMEOUT_MULTISHOT`, `IORING_TIMEOUT_ETIME_SUCCESS`, `IOSQE_IO_LINK`, and `IOSQE_IO_DRAIN`.

Control flow: main creates a normal ring and optionally an SQPOLL ring. It first establishes basic timeout support, then runs single relative and immediate timeouts, two-timeout ordering, absolute timeouts, timeout removal and not-found removal, `io_uring_enter` wait-for-many behavior, counted timeout completion, link/drain flag combinations, multishot behavior, and wait helper behavior. The ring is reinitialized after tests that may leave helper timeouts behind. If timeout update is supported, it checks nonexistent updates, invalid flags, immediate/1 ms/1 s updates, absolute and async updates, linked updates, multishot updates, and SQPOLL update. It ends with eventfd teardown, queue-exit cancellation, exec-triggered cancellation, and `ETIME_SUCCESS` linked behavior.

State/persistence behavior: state is mostly ring-local timeout requests and CQ/SQ flags. `test_timeout_link_cancel` forks a child that submits linked timeout/NOP then `exec`s `exec-target.t`, forcing full cancellation visible to the parent ring. `test_eventfd` registers an eventfd then exits a ring with an async timeout to catch teardown bugs.

Dependencies/integration: uses raw `io_uring_enter`, eventfd, fork/exec/wait, SQPOLL, helper executable discovery, and timing windows measured by `gettimeofday`. It integrates with multiple kernel feature levels by setting `not_supported`, `no_modify`, `no_multishot`, and `no_immediate`.

Risks/test signals: timing bounds are intentionally loose but still flaky under extreme load. Several subtests skip implicitly when operations return `-EINVAL`. Failures include wrong CQE order, wrong result codes (`-ETIME`, `-ECANCELED`, `-ENOENT`, `-EINVAL`), missing `IORING_CQE_F_MORE`, no CQ overflow after multishot saturation, update not shortening timeout, or linked operations being canceled incorrectly.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/timerfd-short-read.c -->
# sources/test-tools/liburing/test/timerfd-short-read.c

Purpose: regression test that io_uring read handling on anonymous-inode descriptors such as timerfd supports short reads correctly. It guards against kernel behavior that treated anonymous inodes like regular files and broke short read/write handling.

Important APIs/types/functions: `sig_alrm`, `timerfd_create`, `timerfd_settime`, `io_uring_queue_init_params`, `io_uring_prep_read`, `io_uring_submit`, `io_uring_wait_cqe`, `alarm`, and `SIGALRM`.

Control flow: main creates an io_uring and a monotonic timerfd. It submits a read for two `unsigned long` values, arms the timer to expire after 10 ms, installs a one-second alarm fail-safe, then waits for a CQE. The test succeeds if the wait returns instead of hanging; it does not require a specific byte count.

State/persistence behavior: no persistent state. The timerfd counter state is consumed by the pending read and closed afterward.

Dependencies/integration: depends on Linux timerfd, signal handling, io_uring read operations, and anonymous-inode file operations.

Risks/test signals: primary signal is non-hang. A hang triggers `sig_alrm` and `T_EXIT_FAIL`; setup failures or wait errors also fail.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/timerfd-short-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/timestamp-bug.c -->
# sources/test-tools/liburing/test/timestamp-bug.c

Purpose: regression test for socket transmit timestamp retrieval when the socket error queue contains both timestamp messages and real errors. It ensures `SOCKET_URING_OP_TX_TIMESTAMP` can retry/scan the current skb list rather than being confused by mixed error-queue contents.

Important APIs/types/functions: `create_sock_with_timestamps_and_errors`, `socket(AF_INET, SOCK_DGRAM)`, `setsockopt(SO_TIMESTAMPING)`, `setsockopt(IP_RECVERR)`, `sendto`, `recvmsg(MSG_ERRQUEUE)`, `IORING_SETUP_CQE32`, `IORING_OP_URING_CMD`, and `SOCKET_URING_OP_TX_TIMESTAMP`.

Control flow: helper creates a UDP socket with software TX timestamps and IP error queue reporting enabled, creates a receiving UDP socket on loopback, sends two packets to generate TX timestamps, then sends to closed port 9 to generate an error. Main creates a CQE32 ring, submits one socket uring command for TX timestamp retrieval, and treats `-EOPNOTSUPP` as skip. It then drains one error-queue message with `recvmsg`.

State/persistence behavior: no durable state. Runtime state is kernel socket error queue contents and CQE32 timestamp payload handling.

Dependencies/integration: uses IPv4 loopback UDP, Linux timestamping options, error queue support, socket uring commands, and CQE32 layout.

Risks/test signals: assumes localhost networking and port 9 closed enough to generate an error. Failures show as unsupported ring setup, wait errors, or timestamp command errors other than `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/timestamp-bug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/timestamp.c -->
# sources/test-tools/liburing/test/timestamp.c

Purpose: socket TX timestamp coverage for io_uring socket commands. It verifies timestamp CQEs for IPv6 TCP send paths, including SCHED, software send, ACK timestamp types, option-id progression, and both CQE32 and mixed-CQE modes.

Important APIs/types/functions: `struct ctx`, `struct send_req`, `validate_key`, `test_prep_sock`, `queue_ts_cmd`, `queue_send`, `get_tstype_name`, `do_test`, `resolve_hostname`, `do_listen`, `do_main`, `io_uring_prep_sendmsg`, `IORING_OP_URING_CMD`, `SOCKET_URING_OP_TX_TIMESTAMP`, `IORING_SETUP_CQE32`, `IORING_SETUP_CQE_MIXED`, `IORING_CQE_F_MORE`, `IORING_CQE_F_32`, and `struct io_timespec`.

Control flow: main binds a loopback IPv6 listener and runs TCP timestamp scenarios first with CQE32 and then mixed CQEs. Each `do_test` creates a timestamp-enabled socket, sends one payload with `sendmsg`, waits for the send CQE, sleeps briefly for timestamp availability, submits the TX timestamp uring command, and iterates all returned CQEs. It counts expected timestamp types from `SOF_TIMESTAMPING_TX_*` flags and validates timestamp keys advance by payload length for streams unless explicit cmsg option IDs are used.

State/persistence behavior: state is socket timestamp option configuration, saved timestamp key/type globals, and listener file descriptor lifetime. No filesystem state.

Dependencies/integration: requires IPv6 loopback, TCP_NODELAY, Linux timestamping ancillary data definitions, CQE32 or mixed CQE support, and liburing helper `t_create_ring`.

Risks/test signals: skips if timestamp command is unsupported. Failures include missing/extra timestamp CQEs, wrong key progression, missing CQE32 flag in mixed mode, error CQE results, or inability to bind/connect loopback.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/truncate.c -->
# sources/test-tools/liburing/test/truncate.c

Purpose: validates io_uring file truncation operations, especially large file sizes and invalid opcode usage. It exercises `IORING_OP_FTRUNCATE` through the liburing prep helper and ensures malformed truncate usage fails with `-EINVAL`.

Important APIs/types/functions: `test_truncate`, `test_ftruncate`, `get_file_size`, `io_uring_prep_ftruncate`, raw `io_uring_prep_rw(IORING_OP_FTRUNCATE, ...)`, `mkostemp`, `fstat`, `ioctl(BLKGETSIZE64)`, and size constants for 2 GiB, 1 GiB, and 512 MiB.

Control flow: main creates a one-entry ring and a temporary file, then ftruncates it through io_uring to 2 GiB, 1 GiB, and 512 MiB. After each completion it reads back the size via `fstat` or block-device ioctl semantics and checks equality. It then queues a deliberately invalid raw truncate form with a bogus pointer argument and expects `-EINVAL`.

State/persistence behavior: modifies a temporary file size and unlinks it before exit. Large sparse sizes are used, so disk data allocation should be minimal.

Dependencies/integration: depends on large-file support, filesystem truncate behavior, liburing ftruncate prep, and stat/ioctl size queries.

Risks/test signals: skips when ftruncate returns unsupported errors on the first size. Failures include unexpected CQE results, wrong file size, submit/wait errors, or invalid raw truncate not returning `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/tty-write-dpoll.c -->
# sources/test-tools/liburing/test/tty-write-dpoll.c

Purpose: regression test for double-poll TTY write behavior, targeting a kernel bug where io_uring assumed the triggered poll waitqueue was the only poll.

Important APIs/types/functions: `open("/dev/ttyS0", O_RDWR | O_NONBLOCK)`, `t_create_ring`, `io_uring_get_sqe`, `io_uring_prep_writev`, `io_uring_submit`, `struct iovec`, `SQES`, and `BUFSIZE`.

Control flow: main skips when invoked with arguments or when `/dev/ttyS0` is absent. It creates a 128-entry ring, queues 128 nonblocking `writev` operations to the TTY using identical static buffer storage, and submits them all. It only verifies the submit count.

State/persistence behavior: no durable state. It writes to a serial TTY if present, so runtime device output is possible.

Dependencies/integration: depends on a real `/dev/ttyS0`, nonblocking TTY driver write/poll behavior, and liburing test helpers.

Risks/test signals: intentionally opportunistic and returns success when no TTY exists. Failure is a ring setup error or submission count mismatch; completions are not reaped, so this is mainly a regression trigger for kernel-side poll handling.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/tty-write-dpoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/unlink.c -->
# sources/test-tools/liburing/test/unlink.c

Purpose: tests io_uring unlink and rmdir behavior, including successful file unlink, invalid path handling, bad user pointer handling, and directory removal through `AT_REMOVEDIR`.

Important APIs/types/functions: `test_rmdir`, `test_unlink_badaddr`, `test_unlink`, `stat_file`, `io_uring_prep_unlink`, `mkstemp`, `mkdir`, `stat`, `io_uring_queue_init`, `io_uring_submit`, and `io_uring_wait_cqe`.

Control flow: main creates a ring and temporary file, verifies it exists, unlinks it through io_uring, and requires later `stat` to return `ENOENT`. It then queues unlink for a guaranteed missing path and expects `-ENOENT`, queues unlink with address `0x1234` and expects `-EFAULT`, and finally creates/removes a temporary directory with `AT_REMOVEDIR`, verifying it is gone.

State/persistence behavior: creates and removes one temporary file and one temporary directory named with the process id. Error paths attempt cleanup with `unlink`.

Dependencies/integration: exercises VFS unlink/rmdir paths through io_uring and user pointer validation.

Risks/test signals: skips only by returning success when unlink opcode is unsupported (`-EBADF` or `-EINVAL` on the first real unlink). Failures are wrong CQE result codes or filesystem objects remaining after reported success.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/uring_cmd_ublk.c -->
# sources/test-tools/liburing/test/uring_cmd_ublk.c

Purpose: end-to-end test of cancellable `IORING_OP_URING_CMD` through the Linux ublk userspace block driver. It creates a null ublk device, runs direct fixed-buffer I/O against it, kills the userspace daemon mid-I/O, and checks that uring command cancellation and device teardown complete.

Important APIs/types/functions: when `CONFIG_HAVE_UBLK_HEADER` is present, key types include `struct ublk_dev`, `struct ublk_queue`, `struct ublk_io`, `struct ublk_tgt_ops`, and `struct io_ctx`. Control functions include `ublk_ctrl_init_cmd`, `__ublk_ctrl_cmd`, `ublk_ctrl_{add,del,get_info,set_params,get_features,start_dev}`, `ublk_queue_init`, `ublk_queue_io_cmd`, `ublk_handle_cqe`, `ublk_process_io`, `ublk_io_handler_fn`, `cmd_dev_add`, `cmd_dev_del_by_kill`, `ublk_null_tgt_init`, `ublk_null_queue_io`, `__test_io`, `test_io_worker`, and `test_del_ublk_with_io`.

Control flow: main skips without ublk headers/device/features, then loops four times. Each loop adds a `null` ublk target with two queues and 128-depth queues. A forked daemon maps ublk command buffers, registers the char device fd as fixed file, submits fetch/commit uring commands for all tags, and completes null target I/O immediately by reporting byte counts. Parent waits for `/dev/ublkbN`, forks I/O workers doing fixed-buffer direct reads and writes over the block device, sleeps briefly, kills the daemon with SIGKILL, waits for `/dev/ublkcN` close notification, deletes the device, and verifies `GET_DEV_INFO` no longer succeeds.

State/persistence behavior: creates transient `/dev/ublkcN` and `/dev/ublkbN` kernel devices, daemon process state, per-queue mmaped command buffers, registered files, and aligned per-I/O buffers. The null target declares a 250 GiB device but does not persist backing data.

Dependencies/integration: requires kernel ublk support, `/dev/ublk-control`, ublk headers, `UBLK_F_CMD_IOCTL_ENCODE`, direct I/O, inotify on `/dev`, block device ioctls, pthreads, fork/daemon behavior, and io_uring SQE128 uring commands.

Risks/test signals: high privilege and kernel-feature sensitivity. It is skipped when ublk is unavailable. Failures include inability to add/start/delete devices, queue mmap/register failures, fixed I/O CQE length mismatch, daemon not closing, or device info still present after deletion. The target lookup loop is intended to scan `tgt_ops_list`, so any future list changes should review loop bounds carefully.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/uring_cmd_ublk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/vec-regbuf.c -->
# sources/test-tools/liburing/test/vec-regbuf.c

Purpose: validates fixed registered-buffer vector operations for writev/sendmsg zero-copy and readv. It stresses registered vector boundaries, segment resizing, aligned/unaligned spans, invalid iovecs, and readback correctness.

Important APIs/types/functions: `struct buf_desc`, `struct work`, `probe_support`, `bind_ring`, `reinit_ring`, `init_buffers`, `verify_data`, `test_rw`, `test_sendzc`, `test_vec`, `test_sequence`, `test_basic`, `test_readv_fixed`, `test_readv`, `test_fail`, `io_uring_register_buffers_sparse`, `io_uring_register_buffers_update_tag`, `io_uring_prep_writev_fixed`, `io_uring_prep_sendmsg_zc_fixed`, and `io_uring_prep_readv_fixed`.

Control flow: main probes for `IORING_OP_READV_FIXED` support, allocates a guarded memory area with inaccessible guard pages, registers one buffer slot, and runs two passes: send zero-copy fixed and writev fixed. `test_basic` runs many valid iovec sequences over an IPv6 socket pair while a verifier thread reads the other side and compares bytes. `test_fail` submits zero-length and invalid/out-of-bounds iovecs and requires non-positive/error CQEs. `test_readv` creates a temp file with known data and reads it back through fixed readv for single, multi-segment, and unaligned vectors.

State/persistence behavior: uses mmaped anonymous memory for registered buffers, socket pairs for transfer, and an unlinked temporary file for readv verification. The ring is reinitialized frequently to exercise registration table update paths.

Dependencies/integration: depends on registered sparse buffer support, fixed vector op support, IPv6 socket-pair helpers, zero-copy sendmsg support, mmap guard behavior, and root or sufficient permissions for buffer registration if required.

Risks/test signals: skips if the probe lacks registered vector ops or if root-only registration blocks unprivileged runs. Failures are data mismatches, CQE byte counts not matching aggregate iovec length, invalid vectors succeeding, or registration/update errors.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/vec-regbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/version.c -->
# sources/test-tools/liburing/test/version.c

Purpose: sanity test for liburing compile-time and runtime version APIs/macros.

Important APIs/types/functions: `io_uring_major_version`, `io_uring_minor_version`, `IO_URING_VERSION_MAJOR`, `IO_URING_VERSION_MINOR`, `IO_URING_CHECK_VERSION`, and `T_EXIT_PASS`/`T_EXIT_FAIL`.

Control flow: main first verifies that checking the runtime major/minor pair does not report a newer required version. It then requires runtime major and minor values to equal the compile-time version macros. Finally, it uses a preprocessor-time `IO_URING_CHECK_VERSION(IO_URING_VERSION_MAJOR, IO_URING_VERSION_MINOR)` guard and fails if the macro considers the current version insufficient.

State/persistence behavior: no runtime state beyond version values; no filesystem effects.

Dependencies/integration: depends only on liburing headers/library exposing consistent version information and helper exit constants.

Risks/test signals: failures indicate an inconsistency between compiled headers and linked library version reporting or a broken version comparison macro.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/wait-timeout.c -->
# sources/test-tools/liburing/test/wait-timeout.c

Purpose: tests `io_uring_enter` getevents timeout behavior, absolute getevents timers, and registered wait clock support.

Important APIs/types/functions: `timespec_to_ns`, `ns_to_timespec`, `ns_since`, `t_io_uring_wait`, `probe_timers`, `test_timeout`, `test_clock_setup`, `io_uring_enter2`, `io_uring_getevents_arg`, `IORING_ENTER_ABS_TIMER`, `IORING_ENTER_EXT_ARG`, `io_uring_register_clock`, and `IORING_REGISTER_CLOCK`.

Control flow: main probes whether absolute enter timers and registered clocks are supported. If neither exists it skips. Clock setup tests invalid null registration, invalid clock id, valid monotonic and boottime registration, and repeated monotonic registration. It then runs combinations of relative/absolute wait and default/registered clock support. Each `test_timeout` checks current/zero timeout returns promptly with `-ETIME`, expired absolute timeouts return promptly, and a future timeout sleeps roughly one to three seconds.

State/persistence behavior: only ring configuration changes persist during each subtest, especially registered clock id. No external files are created.

Dependencies/integration: uses raw io_uring register/enter syscalls, kernel support for absolute wait timers and `IORING_REGISTER_CLOCK`, monotonic/boottime clocks, and signal mask sizing via `_NSIG`.

Risks/test signals: support is feature-probed by `-EINVAL`. Failures are wrong return code, invalid clock registration accepted, valid clock rejected, or waits firing too early/late.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/wait-timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/waitid.c -->
# sources/test-tools/liburing/test/waitid.c

Purpose: validates io_uring `waitid` support across successful child reaping, linked timeout cancellation, pid filtering, ready children, explicit cancellation, invalid `siginfo_t` pointers, and cancellation races.

Important APIs/types/functions: `child`, `test_invalid_infop`, `test_noexit`, `test_double`, `test_ready`, `test_cancel`, `test_cancel_race`, `test`, `io_uring_prep_waitid`, `io_uring_prep_link_timeout`, `io_uring_prep_cancel64`, `P_PID`, `P_ALL`, `WEXITED`, `IOSQE_IO_LINK`, and `IOSQE_ASYNC`.

Control flow: main initializes one ring and first runs a basic waitid test; `-EINVAL` marks unsupported and skips the rest. It then checks a wait linked to a 100 ms timeout against a child that exits after 200 ms, expecting waitid `-ECANCELED` and timeout result `1`. It verifies a wait for the second of two children ignores the first child, reaps an already-exited child, cancels a pending wait by user data, verifies invalid user `siginfo_t` returns `-EFAULT`, and runs 1000 cancellation races alternating async/non-async waitid.

State/persistence behavior: creates many child processes and reaps them with either io_uring waitid or fallback `wait`. No files are used.

Dependencies/integration: depends on process creation, wait queues, signal/child exit semantics, io_uring cancellation, link timeout support, and race tolerance around cancellation.

Risks/test signals: highly race-oriented. Expected race outcomes include wait completion or cancellation, and cancel CQEs may return `1`, `0`, `-ENOENT`, or `-EALREADY`. Other result codes, wrong `si_pid`, or unreaped children indicate failures.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/waitid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/wakeup-hang.c -->
# sources/test-tools/liburing/test/wakeup-hang.c

Purpose: regression test that poll requests sleeping in io_uring wake correctly when signaled by pipe and eventfd writes, avoiding hangs in wakeup paths.

Important APIs/types/functions: `struct thread_data`, `listener_thread`, `wakeup_io_uring`, `test_pipes`, `test_eventfd`, `io_uring_prep_poll_add`, `io_uring_wait_cqe`, `eventfd`, `eventfd_write`, `pipe`, pthreads, and `POLLIN`.

Control flow: `test_pipes` creates a pipe, queues a poll-add on the read end, starts a listener thread blocked in `io_uring_wait_cqe`, sleeps one second, and starts a writer thread that writes to the pipe write end using `eventfd_write`-style helper data. `test_eventfd` repeats the pattern with an actual eventfd. Main requires both listener joins to report success.

State/persistence behavior: only file descriptor readiness state and ring CQ state exist. Descriptors are closed by process teardown; rings are explicitly exited.

Dependencies/integration: exercises io_uring poll wait queues, eventfd/pipe readiness, pthread scheduling, and CQ wakeups.

Risks/test signals: can hang if wakeup is broken because no timeout guard is installed. Failures include wait errors, negative CQE results, failed submit, or listener thread returning an error pointer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/wakeup-hang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/wq-aff.c -->
# sources/test-tools/liburing/test/wq-aff.c

Purpose: checks io-wq worker CPU affinity for SQPOLL rings. It verifies the SQPOLL thread and io-wq worker are pinned to expected CPUs when affinity is registered.

Important APIs/types/functions: `verify_comm`, `verify_affinity`, `test`, `test_invalid_cpu`, `io_uring_register_iowq_aff`, `io_uring_queue_init_params`, `IORING_SETUP_SQPOLL`, `IORING_SETUP_SQ_AFF`, `IOSQE_ASYNC`, `/proc/<pid>/comm`, `sched_getaffinity`, `CPU_SET`, and `CPU_COUNT`.

Control flow: main requires at least two CPUs. It first creates an SQPOLL ring with an invalid CPU id and expects `-EINVAL`, unless `-EPERM` requires skip. Then `test(1)` creates an SQPOLL ring pinned to CPU 1, registers io-wq affinity to CPU 0, submits an async pipe read to force an io-wq worker, sleeps briefly, and verifies expected kernel thread comm names and affinity masks based on current pid offsets.

State/persistence behavior: ring thread affinity and io-wq worker affinity are kernel thread state. No persistent files; `/proc` is read for verification.

Dependencies/integration: depends on predictable thread naming/pid adjacency (`iou-sqp-<pid>` and `iou-wrk-<pid>`), CPU affinity APIs, SQPOLL permissions, and at least two online CPUs.

Risks/test signals: fragile if kernel thread creation order changes. It skips when `/proc` names or permissions do not match. Failures include wrong affinity mask width, wrong CPU, invalid CPU accepted, or registration errors.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/wq-aff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/xattr.c -->
# sources/test-tools/liburing/test/xattr.c

Purpose: verifies io_uring extended attribute operations for both fd-based and path-based APIs, including success paths and invalid argument behavior.

Important APIs/types/functions: wrappers `io_uring_fsetxattr`, `io_uring_fgetxattr`, `io_uring_setxattr`, `io_uring_getxattr`; tests `test_fxattr`, `test_xattr`, `test_failure_fxattr`, `test_failure_xattr`, `test_invalid_sqe`; liburing prep helpers `io_uring_prep_fsetxattr`, `io_uring_prep_fgetxattr`, `io_uring_prep_setxattr`, and `io_uring_prep_getxattr`.

Control flow: main runs fd-based set/get first. `test_fxattr` creates `xattr.test`, writes two `user.*` attributes, and reads them back by fd. If the first set reports `-EINVAL` or `-EOPNOTSUPP`, `no_xattr` is set and the rest of the test exits successfully. Otherwise path-based set/get does the same using a filename. Failure tests then submit bad fd/path/name/value/size combinations and require failures or zero-length success where appropriate. A destructive invalid-SQE case is compiled only under `DESTRUCTIVE_TEST`.

State/persistence behavior: creates and unlinks `xattr.test` in multiple tests. Attribute state is written to the file and checked before cleanup.

Dependencies/integration: requires filesystem support for `user.*` xattrs, kernel io_uring xattr op support, and normal VFS xattr permission behavior.

Risks/test signals: skips xattr-op unsupported kernels by exiting success after fd test. Some invalid cases rely on kernel validation order and on zero-size xattr semantics. Failures are wrong CQE status, wrong returned value length, or mismatched value bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/xfail_prep_link_timeout_out_of_scope.c -->
# sources/test-tools/liburing/test/xfail_prep_link_timeout_out_of_scope.c

Purpose: negative ASan-oriented test for stack lifetime misuse with timeout preparation. It intentionally passes a stack `__kernel_timespec` to a timeout SQE and lets the variable go out of scope before submit.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_get_sqe`, `io_uring_prep_timeout`, `io_uring_sqe_set_data`, and `io_uring_submit_and_wait`.

Control flow: main skips when invoked with arguments. It initializes a ring; if queue init fails it returns pass because this xfail expects inverted handling. Inside a nested scope it initializes `timespec`, prepares a timeout SQE using its address, sets user data, leaves scope, then submits and waits. It always returns `T_EXIT_PASS`.

State/persistence behavior: no persistent state. The test intentionally creates invalid pointer lifetime state in user memory.

Dependencies/integration: designed for sanitizer runs, particularly AddressSanitizer, to catch stack-use-after-scope in liburing prep/submit paths.

Risks/test signals: by normal exit code this file is not a conventional correctness test; the expected interesting signal is an ASan report. Without sanitizer it may appear to pass despite the misuse.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/xfail_prep_link_timeout_out_of_scope.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/xfail_register_buffers_out_of_scope.c -->
# sources/test-tools/liburing/test/xfail_register_buffers_out_of_scope.c

Purpose: negative ASan-oriented test for registering buffers after freeing one iovec base. It is intended to expose use-after-free detection in buffer registration paths.

Important APIs/types/functions: `calloc`, `malloc`, `free`, `io_uring_queue_init`, `io_uring_register_buffers`, `io_uring_submit_and_wait`, `struct iovec`, `BUFFERS`, and `BUFFER_SIZE`.

Control flow: main initializes a ring, allocates an array of eight iovecs and backing buffers, frees `iovs[4].iov_base`, calls `io_uring_register_buffers` with the stale pointer still present, then submits/waits and returns `T_EXIT_PASS`. Queue init failure is also treated as pass because the xfail uses inverted exit-code expectations.

State/persistence behavior: heap allocation state is intentionally corrupted by freeing one registered buffer candidate. No files or durable state.

Dependencies/integration: intended for sanitizer-instrumented liburing/kernel-test harnesses. It uses normal buffer registration but expects external tooling to flag invalid memory use.

Risks/test signals: exit status alone does not indicate the bug; without ASan or equivalent it may pass. Memory allocated for other buffers is not freed because process exit is the cleanup boundary.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/xfail_register_buffers_out_of_scope.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/zcrx.c -->
# sources/test-tools/liburing/test/zcrx.c

Purpose: comprehensive zero-copy receive test suite for io_uring ZCRX registration, refill queues, nodev receive, import/export clone, invalid parameter handling, buffer return/flush, and abnormal teardown paths.

Important APIs/types/functions: `struct zcrx_reg`, `struct t_executor`, `write_ro_params`, `submit_and_wait_one`, `test_io_uring_prep_zcrx`, `query_zcrx`, `default_reg`, `try_register_zcrx`, `clone_zcrx`, `test_register_basic`, `test_rq`, `test_area`, `test_ro_params`, `test_invalid_rx_page`, `prep_server`, `return_buffer`, `transfer_bytes`, `test_invalid_recv`, `test_exit_with_inflight`, `test_zcrx_invalid_clone`, `test_zcrx_clone`, `test_rq_flush`, `test_recv`, `test_abnormal_exit`, `test_invalid_rq_pointers`, `test_invalid_rqes`, `test_area_ro`, `run_tests`, `io_uring_register_ifq`, `IORING_OP_RECV_ZC`, and `IORING_REGISTER_ZCRX_CTRL`.

Control flow: main queries ZCRX support and nodev registration flags, allocates default RQ/area/read-only parameter memory, then runs a sequence of registration and I/O tests. Early tests validate basic registration, invalid refill queue descriptors, invalid area descriptors, read-only parameter memory, read-only area memory, and invalid receive page lengths. Runtime tests register a nodev IFQ over a socket pair, test invalid receive fds/zcrx ids, exit with inflight receive, optionally export/import ZCRX state, flush refill queues, inject invalid refill queue pointers/RQEs, transfer patterned bytes with and without returning buffers, and exit abnormally across direct/io-wq and pinned/unpinned ZCRX cases.

State/persistence behavior: state is ring registration state, user-provided refill queue memory, registered receive area tokens, socket-pair data flow, exported ZCRX file descriptors, and memory protection for negative tests. No persistent filesystem artifacts.

Dependencies/integration: requires kernel ZCRX query/register support, `ZCRX_REG_NODEV`, CQE32/defer-taskrun/single-issuer/submits-all ring flags, socket pairs, mmap/mprotect/madvise, optional huge pages, and potentially `NET_ADMIN` capability.

Risks/test signals: skips when ZCRX or nodev mode is unsupported, or when registration returns `-EPERM`. Failures include invalid registration accepted, expected import/export errors missing, pattern mismatch in zero-copy payload, missing final non-more CQE, inability to return/flush buffers, or crashes during abnormal teardown. The setup maps `def_area_mem` twice, so memory accounting should be reviewed if extending this test.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/zcrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/Makefile

Purpose: top-level LTP kernel filesystem test Makefile for this subtree. It delegates build/install behavior to the generic trunk target infrastructure.

Important APIs/types/functions: GNU make variables `top_srcdir`, includes `$(top_srcdir)/include/mk/env_pre.mk` and `$(top_srcdir)/include/mk/generic_trunk_target.mk`.

Control flow: the file sets a default `top_srcdir` of `../../..`, imports the LTP environment prelude, then imports the generic trunk target rules. It defines no local targets or source lists.

State/persistence behavior: no runtime state. Build state is produced by the included LTP make fragments.

Dependencies/integration: integrates this directory into the LTP recursive build and install tree. It depends entirely on parent make infrastructure for target discovery.

Risks/test signals: risk is limited to path correctness. If `top_srcdir` is wrong or included make fragments change expectations, filesystem subdirectory recursion may fail.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/acl/tacl_xattr.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/acl/tacl_xattr.sh

Purpose: legacy root-only shell test for POSIX ACL and extended attribute behavior on a loopback ext2/ext3 filesystem mounted with `acl,user_xattr`.

Important APIs/types/functions: shell commands `dd`, `losetup`, `mkfs`, `mount`, `useradd`, `userdel`, `su`, `setfacl`, `getfacl`, `chmod`, `chown`, `attr`, `getfattr`, `setfattr`, `diff`, `umount`, and filesystem paths under `tacl/`.

Control flow: the script requires UID 0, creates `tacl/blkext2`, attaches `/dev/loop0`, formats ext2 or ext3 depending on existing mount output, mounts it, creates four local users, and builds directories/files/symlinks owned by test users. ACL tests then manipulate owner, named user, group, mask, other, default ACL, chmod/chown, and backup/restore semantics, checking success by file creation, `ls -l`, `getfacl`, and `diff`. Xattr tests attach attributes to directories/files/symlinks, dump logical/physical traversals, get/remove attributes, backup/restore with hex encoding, then delete users, unmount, and remove `tacl`.

State/persistence behavior: destructive and persistent until cleanup. It creates system users, modifies a fixed `/dev/loop0`, formats a loopback block file, mounts a filesystem, writes ACL/xattr data, and removes everything at the end.

Dependencies/integration: depends on root, loop device support, mkfs/mount ACL/xattr support, `acl` and `attr` userland tools, local user management, and a test environment where `/dev/loop0` is safe.

Risks/test signals: high operational risk because fixed user names and `/dev/loop0` can collide with host state, and many checks print `FAILED` without exiting nonzero immediately. Some filename typos (`newfil` vs `newfile`) weaken assertions. Test signal is textual success/failure plus final cleanup completing.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/acl/tacl_xattr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/Makefile

Purpose: LTP Makefile for installing binfmt_misc shell tests and their shared library.

Important APIs/types/functions: `top_srcdir`, `env_pre.mk`, `generic_trunk_target.mk`, and `INSTALL_TARGETS`.

Control flow: sets default `top_srcdir` to `../../../..`, imports the LTP environment prelude, declares `binfmt_misc01.sh`, `binfmt_misc02.sh`, and `binfmt_misc_lib.sh` as install targets, then imports generic trunk target rules.

State/persistence behavior: no runtime state. Build/install state is controlled by LTP make includes.

Dependencies/integration: ties the binfmt_misc tests into LTP installation so scripts are available to the test harness.

Risks/test signals: path and install-list errors would prevent tests from being deployed. The Makefile itself has no executable test signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc01.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc01.sh

Purpose: LTP regression test that invalid binfmt_misc registration strings fail and do not create usable binary type entries. It includes offset-overflow coverage for a historical kernel bug.

Important APIs/types/functions: `TST_CNT=9`, `TST_TESTFUNC=do_test`, `verify_binfmt_misc`, `get_binfmt_misc_mntpoint`, `remove_binary_type`, `tst_res`, `tst_run`, shell `echo` to `$mntpoint/register`, `cat`, `awk`, and `which cat`.

Control flow: each test case builds one invalid registration string: bad delimiter/format, invalid type, slash in name, slash in magic/extension, invalid negative or huge offset, and invalid flags. `verify_binfmt_misc` writes the string to the register file and passes only if registration fails and no entry file exists. If an entry is created, it reads it with `cat` to trigger potential kernel issues, reports failure, and removes the entry.

State/persistence behavior: may transiently create binfmt_misc entries under the mounted binfmt_misc filesystem, then removes them.

Dependencies/integration: sources `binfmt_misc_lib.sh`, requiring root, mounted or loadable binfmt_misc, LTP shell harness, and `cat`.

Risks/test signals: failure messages indicate invalid input was accepted. Registration-name extraction with colon delimiters depends on string shape, so adding new malformed cases should preserve cleanup ability.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc02.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc02.sh

Purpose: LTP test that valid binfmt_misc registrations recognize matching files, do not recognize mismatches, and stop recognizing after disabling the entry.

Important APIs/types/functions: `TST_CNT=6`, `recognised_unrecognised`, `unrecognised`, `verify_binfmt_misc`, `do_test`, `get_binfmt_misc_mntpoint`, `remove_binary_type`, `tst_res`, data files under `$TST_DATAROOT`, shell `eval`, `grep`, `head`, and `cat`.

Control flow: `do_test` registers extension and magic rules with several delimiters. Valid cases run the target data file and require output to contain either extension or magic test text, then write `0` to the binfmt entry and require the same execution to fail or omit that text. Invalid-match cases register rules that should not match the data file and require nonrecognition. Each case removes the binfmt entry after checking.

State/persistence behavior: transiently creates and disables binfmt_misc entries. It writes a `temp` output file in the LTP temporary directory.

Dependencies/integration: sources `binfmt_misc_lib.sh`, needs root, mounted binfmt_misc, installed data files, `cat`, `head`, and LTP harness variables.

Risks/test signals: uses `eval` on file paths, so inputs must remain controlled. Failure signals are explicit TFAIL results for registration, recognition, disable, or mismatch behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc_lib.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc_lib.sh

Purpose: shared LTP shell library for binfmt_misc tests. It handles setup, cleanup, mount discovery, module loading, and binary type removal.

Important APIs/types/functions: `TST_SETUP`, `TST_CLEANUP`, `TST_NEEDS_DRIVERS`, `TST_NEEDS_TMPDIR`, `TST_NEEDS_ROOT`, `TST_NEEDS_CMDS`, globals `rmod_binfmt_misc`, `umount_binfmt_misc`, `binfmt_misc_mntpoint`, functions `remove_binary_type`, `get_binfmt_misc_mntpoint`, `binfmt_misc_setup`, and `binfmt_misc_cleanup`.

Control flow: setup checks `/proc/filesystems` and loads `binfmt_misc` with `modprobe` if needed. It then checks `/proc/mounts` for an actual `binfmt_misc` mount and, if absent, creates and mounts `ltp_binfmt_misc`. Cleanup unmounts only if this library mounted it, removes the mount directory, and unloads the module only if setup loaded it.

State/persistence behavior: may load/unload the kernel module, mount/unmount a binfmt_misc filesystem, create/remove a temporary mount directory, and remove binfmt entries by writing `-1` to their control files.

Dependencies/integration: depends on LTP `tst_test.sh`, root privileges, `modprobe`, `mount`, `umount`, `mkdir`, and `rm`.

Risks/test signals: cleanup tracks ownership through flags to avoid disturbing preexisting mounts/modules. Incorrect mount detection could leave a mount behind or affect a system binfmt_misc instance.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/datafiles/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/datafiles/Makefile

Purpose: installs data fixtures used by `binfmt_misc02.sh`.

Important APIs/types/functions: `top_srcdir`, `env_pre.mk`, `generic_leaf_target.mk`, `INSTALL_DIR`, and `INSTALL_TARGETS`.

Control flow: sets default `top_srcdir`, includes the LTP environment prelude, declares install directory `testcases/data/binfmt_misc02`, lists `file.extension` and `file.magic` as install targets, then includes generic leaf target rules.

State/persistence behavior: only build/install artifacts under the LTP install tree.

Dependencies/integration: connects magic/extension fixture files to the LTP data root consumed through `$TST_DATAROOT`.

Risks/test signals: if install paths drift, `binfmt_misc02.sh` cannot find fixtures and will fail recognition tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/datafiles/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/Makefile

Purpose: builds and installs the LTP `doio` filesystem stress tools and shared helper objects.

Important APIs/types/functions: `top_srcdir`, `testcases.mk`, `CFLAGS`, `LDLIBS`, `MAKE_TARGETS`, `INSTALL_TARGETS`, pattern rule `%.o`, and `generic_leaf_target.mk`.

Control flow: imports LTP testcase build rules, adds large-file support and include path for `doio/include`, links with realtime and pthread libraries, declares executables `growfiles`, `doio`, and `iogen`, installs `rwtest`, and makes each executable depend on shared helper objects such as `dataascii.o`, `databin.o`, `datapid.o`, `bytes_by_prefix.o`, and others.

State/persistence behavior: build outputs are object files and binaries; runtime state belongs to the built tools, not this Makefile.

Dependencies/integration: integrates older SGI-style filesystem stress utilities into LTP. Depends on helper sources and headers under the same doio tree and the LTP generic leaf build system.

Risks/test signals: missing helper objects or include paths break all three tools. Link dependencies on `-lrt -lpthread` are required by async/threaded helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/bytes_by_prefix.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/bytes_by_prefix.c

Purpose: parses human-readable byte strings with optional suffix multipliers into `int`, `long`, or `long long` byte counts for doio tools.

Important APIs/types/functions: `bytes_by_prefix`, `lbytes_by_prefix`, `llbytes_by_prefix`, constants `B_MULT`, `K_MULT`, `M_MULT`, `G_MULT`, `T_MULT`, `DEV_BSIZE`, and `sscanf`.

Control flow: each function scans a numeric prefix and optional single-character multiplier. A plain number is returned directly if nonnegative. Supported suffixes are `b`, `k`, `K`, `m`, `M`, `g`, and `G`, where uppercase variants multiply by the target word-size type. Invalid scan shape, unknown suffix, or negative converted result returns `-1`.

State/persistence behavior: stateless conversion helpers with no external effects.

Dependencies/integration: included by doio/growfiles/iogen style tools through `bytes_by_prefix.h`. Uses `DEV_BSIZE` when available, otherwise falls back to 512.

Risks/test signals: integer versions can overflow silently into negative and then return `-1`; positive wraparound may not be detected. `T_MULT` is defined but unused. Float/double conversion can lose precision for large values.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/bytes_by_prefix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/dataascii.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/dataascii.c

Purpose: generates and verifies repeating ASCII data patterns for doio read/write validation.

Important APIs/types/functions: `dataasciigen`, `dataasciichk`, default `CHARS`, `Errmsg`, optional `UNIT_TEST` main, `strlen`, and `sprintf`.

Control flow: generation selects either caller-provided character list or default alphabet/newline pattern, then fills `buffer` from `offset` through `offset + bsize` by indexing `cnt % chars_size`. Checking mirrors the same sequence and returns the file offset of the first mismatch, setting `*errmsg` to static `Errmsg`; on success it returns `-1` and reports all bytes matched.

State/persistence behavior: writes caller-provided memory only and uses one static error buffer, making it non-reentrant/thread-unsafe for concurrent checks.

Dependencies/integration: used by doio data fill/check plumbing via `dataascii.h`. Optional unit test allocates memory and exercises aligned/shifted/mismatch cases.

Risks/test signals: empty custom `listofchars` would cause modulo by zero. Static error storage can be overwritten by subsequent calls. Success signal is return `-1`; nonnegative return is the failing absolute offset.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/dataascii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/databin.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/databin.c

Purpose: generates and checks binary test patterns for doio filesystem stress operations.

Important APIs/types/functions: `databingen`, `databinchk`, static `Errmsg`, modes `a`, `c`, `C`, `o`, `z`, and `r`, plus optional `UNIT_TEST` main.

Control flow: generation fills buffers by mode: alternating `0x55`, checkerboard `0xf0`, counting pattern `(offset + ind) % 8`, all ones `0xff`, zeros, or random high-bit-ish bytes. Checking returns `-1` for success, the absolute failing offset for deterministic patterns, or immediately `-1` for random mode because it cannot be verified. Counting mode validates each byte against its offset-derived value; fixed modes compare every byte against one expected byte value.

State/persistence behavior: writes caller buffers and uses a static error message buffer. Random mode uses process-global `rand()` state.

Dependencies/integration: built into doio tools through `databin.h` and shared object dependencies in the Makefile.

Risks/test signals: random mode provides no integrity signal. Static `Errmsg` is not thread-safe. Signed `char` comparisons in counting mode can be platform-sensitive, though expected values are small.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/databin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/datapid.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/datapid.c

Purpose: Cray-specific data pattern generator/checker that embeds pid and file offset into machine words for doio validation.

Important APIs/types/functions: `datapidgen`, `datapidchk`, macros `LOWER16BITS`, `LOWER32BITS`, `NBPBYTE`, conditional `CRAY`, static `Errmsg`, and optional K&R-style `UNIT_TEST` main.

Control flow: under `CRAY`, generation handles partial leading word, full words, and partial trailing word. Each word encodes lower 16 bits of pid, lower 32 bits of the word's file offset, and lower 16 bits of pid. Checking reconstructs the same expected words and returns the absolute offset of the first mismatching byte, or `-1` on success. On non-CRAY builds, generation returns `-1`; checking sets the error message to "Not supported on this OS." and returns `0`.

State/persistence behavior: writes caller buffers and uses static error text. It has no external state.

Dependencies/integration: retained for legacy doio portability; behavior is meaningful only when compiled with CRAY word-size assumptions and `NBPW` available.

Risks/test signals: on normal Linux builds `datapidchk` returns `0`, which conventionally means mismatch at offset zero rather than unsupported success, so callers must understand this mode. The code uses assignment in conditionals intentionally but can trip modern warnings.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/datapid.c -->
