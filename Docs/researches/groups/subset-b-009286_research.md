# subset-b-009286 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/large-resize.c -->
# sources/test-tools/liburing/test/large-resize.c

Purpose: exercises `io_uring_resize_rings()` while large CQE/SQE layouts are active, including fixed 32-byte CQEs, mixed CQE/SQE modes, pending SQEs, and wrapped CQ state.

Important APIs/types/functions: `io_uring_queue_init_params`, `io_uring_resize_rings`, `io_uring_prep_nop`, `io_uring_submit`, `io_uring_wait_cqe`, `io_uring_peek_cqe`, `__io_uring_flush_sq`, `IORING_SETUP_CQE32`, `IORING_SETUP_CQE_MIXED`, `IORING_SETUP_SQE128`, `IORING_SETUP_SQE_MIXED`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_DEFER_TASKRUN`, and `IORING_SETUP_SINGLE_ISSUER`.

Control flow: `main()` runs five subtests. CQE32 and mixed-CQE tests submit NOPs, resize the CQ from 8 to 16 entries, then validate `user_data`. The wrapping test uses a four-entry ring, consumes early CQEs to force head/tail wrap, resizes, and verifies only the last two completions remain. SQE128 and SQE-mixed tests queue NOPs with extended command bytes, flush SQ state before submit, resize, then submit and reap.

State and persistence behavior: all state is transient ring memory, especially SQ/CQ mapping size, CQ head/tail wrapping, pending SQEs, and 32-byte CQE payload preservation. No filesystem persistence is used.

Dependencies and integration points: depends on newer kernel/liburing resize and large-entry support. `-EINVAL` at setup or resize is treated as skip in feature-probe paths. It integrates with `helpers.h` for `T_EXIT_*` status constants.

Risks and test signals: catches data corruption during remap/copy of large CQEs or SQEs, bad CQ ordering across resize, and lost completions after wrap. Success is exact `user_data` preservation and expected completion counts; failures print corruption markers.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/large-resize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/lfs-openat-write.c -->
# sources/test-tools/liburing/test/lfs-openat-write.c

Purpose: verifies that an `IORING_OP_OPENAT` result can be used for a large-file write beyond 4 GiB when `O_LARGEFILE` is used.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_prep_openat`, `io_uring_prep_write`, `io_uring_submit`, `io_uring_wait_cqe`, `open`, `unlink`, `O_LARGEFILE`, and `T_EXIT_SKIP`.

Control flow: `main()` opens `/tmp` as a directory, initializes a small ring, and calls `test_open_write()`. That submits openat for `io_uring_openat_write_test1`, extracts the returned fd from the CQE, and calls `do_write()` at offset `1ULL << 32`.

State and persistence behavior: creates and removes one temporary file under `/tmp`. Persistent test signal is whether the filesystem accepts sparse large-file writes; the code does not inspect file contents afterward.

Dependencies and integration points: depends on large-file-capable filesystem semantics, liburing open/write preparation helpers, and `helpers.h` exit constants. An extra CLI argument skips execution.

Risks and test signals: failure indicates openat completion errors, write submission/CQE errors, or inability to write at a large offset. The opened fd is not explicitly closed in `test_open_write()`, so process exit performs cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/lfs-openat-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/lfs-openat.c -->
# sources/test-tools/liburing/test/lfs-openat.c

Purpose: tests `openat` through io_uring with `O_LARGEFILE`, including linked and drained interactions with blocked pipe reads during ring flush/exit.

Important APIs/types/functions: `open_io_uring`, `prepare_file`, `test_linked_files`, `test_drained_files`, `io_uring_prep_openat`, `io_uring_prep_readv`, `io_uring_prep_nop`, `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, `IOSQE_ASYNC`, `dup(ring.ring_fd)`, and `io_uring_queue_exit`.

Control flow: `main()` prepares a sparse `/tmp/io_uring_openat_test`, verifies a direct io_uring open, then submits linked read/open combinations and drained NOP/open combinations. The pipe read intentionally blocks, then a duped ring fd is closed to trigger kernel flush behavior before ring exit.

State and persistence behavior: creates a temporary sparse file with data past 4 GiB and removes it at exit. The tested state is in-flight request dependency state during file table and ring cleanup.

Dependencies and integration points: depends on pipe blocking semantics, `O_PATH` directory fd for `/tmp`, and kernel handling of linked/drained requests on ring teardown.

Risks and test signals: main risk is hangs during close/flush when blocked reads coexist with linked or drained openat requests. Any submit/open error, failed dup, or hang is a failure signal.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/lfs-openat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/link-timeout.c -->
# sources/test-tools/liburing/test/link-timeout.c

Purpose: comprehensive linked-timeout regression suite covering timeout cancellation, invalid linked timeout placement, update operations, poll/read chains, and kernel-version-dependent return codes.

Important APIs/types/functions: `io_uring_prep_link_timeout`, `io_uring_prep_timeout`, `io_uring_prep_timeout_update`, `io_uring_prep_readv`, `io_uring_prep_writev`, `io_uring_prep_poll_add`, `io_uring_prep_nop`, `IOSQE_IO_LINK`, `IOSQE_ASYNC`, `IORING_LINK_TIMEOUT_UPDATE`, `__kernel_timespec`, and `mtime_since_now`.

Control flow: `main()` runs many focused subtests. It checks standalone linked timeouts reject with `-EINVAL`, timeout-to-timeout chains, NOP/read/poll heads with link timeouts, chains where timeouts cancel later links, and `timeout_update` for valid and missing target IDs. Pipe reads and polls provide operations that either block until timeout or complete after a paired write.

State and persistence behavior: no persistent storage. State is per-ring linked request lists, timeout target identity via `user_data`, cancellation propagation, pipe readiness, and wall-clock duration of timeout update.

Dependencies and integration points: depends on liburing helpers, pipe and poll semantics, and kernel behavior that may return acceptable alternatives such as `-EALREADY`, `-ETIME`, `-EINTR`, `-ECANCELED`, or `-EINVAL` on different paths.

Risks and test signals: failures identify broken timeout arming, cancellation propagation, invalid SQE validation, timeout update lookup, or link-chain termination. The update test also asserts elapsed time is roughly 10-200 ms after shortening a five-second timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/link-timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/link.c -->
# sources/test-tools/liburing/test/link.c

Purpose: validates basic linked SQE semantics, hard links, cancellation after a failing head, independent chains, and `submit_and_wait` behavior after early failure.

Important APIs/types/functions: `test_single_link`, `test_double_link`, `test_double_chain`, `test_single_link_fail`, `test_single_hardlink`, `test_double_hardlink`, `test_early_fail_and_wait`, `io_uring_prep_nop`, `io_uring_prep_timeout`, `io_uring_prep_remove_buffers`, `io_uring_prep_readv`, `IOSQE_IO_LINK`, and `IOSQE_IO_HARDLINK`.

Control flow: a normal ring and an IOPOLL ring are initialized. The suite submits NOP chains, a bad remove-buffer linked to a NOP, timeout hardlink chains, and an invalid readv chain with `io_uring_submit_and_wait`.

State and persistence behavior: ring-only state. `no_hardlink` records whether the kernel returns `-EINVAL` for hard links and skips later hardlink checks.

Dependencies and integration points: uses normal and `IORING_SETUP_IOPOLL` rings plus liburing/test helpers. It relies on exact CQE sequencing and link cancellation semantics.

Risks and test signals: expected results include successful NOP dependents, `-ENOENT` for invalid buffer removal, `-ECANCELED` for canceled dependents, `-ETIME` for hardlink timeouts, and no hang after early submit failure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/link_drain.c -->
# sources/test-tools/liburing/test/link_drain.c

Purpose: stress-tests ordering when `IOSQE_IO_LINK` and `IOSQE_IO_DRAIN` are combined with normal writes and NOPs.

Important APIs/types/functions: `test_link_drain_one`, `test_link_drain_multi`, `test_drain`, `io_uring_prep_writev`, `io_uring_prep_nop`, `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, `t_malloc`, and `t_probe_defer_taskrun`.

Control flow: the one-chain test submits write, linked NOP, linked drained NOP, NOP, and normal NOP, then expects CQEs in `user_data` order 0..4. The multi-chain test submits two linked/drained sequences and expects order 0..8. Each is repeated 1000 times for normal rings and, when supported, deferred taskrun rings.

State and persistence behavior: creates transient `testfile` files and unlinks/closes them. Tested state is scheduler ordering across link/drain dependencies.

Dependencies and integration points: integrates with filesystem writes, liburing helper allocation, and optional `IORING_SETUP_SINGLE_ISSUER | IORING_SETUP_DEFER_TASKRUN`.

Risks and test signals: any out-of-order completion, short submit, failed wait, or failure under deferred taskrun indicates broken drain/link sequencing.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/link_drain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/linked-defer-close.c -->
# sources/test-tools/liburing/test/linked-defer-close.c

Purpose: reproduces a deferred-taskrun close bug where a linked send chain with skipped CQEs must still close the accepted socket and wake a peer.

Important APIs/types/functions: `io_uring_prep_multishot_accept`, `io_uring_prep_send`, `io_uring_prep_close`, `IOSQE_CQE_SKIP_SUCCESS`, `IOSQE_IO_LINK`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, sockets, `pthread_create`, `SIGUSR1`, and `alarm`.

Control flow: main listens on port 9999, arms multishot accept, starts a client thread, then on accept submits three linked sends followed by a close, all success-CQEs skipped except the accept. The client reads until EOF and signals the parent with `SIGUSR1`; an alarm fails the test if EOF never arrives.

State and persistence behavior: no files. State is TCP socket lifetime, skipped CQE handling, and deferred taskrun completion while the submitter is in `cqring_wait`.

Dependencies and integration points: depends on loopback networking, multishot accept support, signal handling, and deferred taskrun support. `-EINVAL` setup or multishot accept returns skip.

Risks and test signals: failure is seeing unexpected skipped send/close CQEs, never receiving SIGUSR1, bind/listen/connect errors, or timeout after five seconds.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/linked-defer-close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/madvise.c -->
# sources/test-tools/liburing/test/madvise.c

Purpose: basic `IORING_OP_MADVISE` test that uses mmap copy timings as a soft signal for `MADV_DONTNEED` and `MADV_WILLNEED`.

Important APIs/types/functions: `do_madvise`, `test_madvise`, `io_uring_prep_madvise`, `io_uring_submit_and_wait`, `mmap`, `msync`, `MADV_DONTNEED`, `MADV_WILLNEED`, `t_create_file`, and `utime_since_now`.

Control flow: creates or uses a file, mmaps 128 KiB, copies it twice for cached timing, submits DONTNEED, copies again, submits DONTNEED then WILLNEED, syncs, and copies again. `main()` repeats up to 100 loops but exits early after at least ten good runs without bad timing.

State and persistence behavior: may create `.madvise.tmp` and unlinks it unless an input filename was supplied. Kernel page cache state is the behavior under test.

Dependencies and integration points: depends on mmap, filesystem page cache, io_uring madvise support, and helpers for temporary file creation.

Risks and test signals: `-EINVAL`/`-EBADF` skips unsupported kernels. Timing is intentionally treated as unreliable; hard failures are setup, CQE, mmap, or unexpected madvise errors.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/min-timeout-wait.c -->
# sources/test-tools/liburing/test/min-timeout-wait.c

Purpose: validates `io_uring_wait_cqes_min_timeout()` behavior for minimum wait windows with already-ready CQEs, delayed pipe writes, no CQEs, and different ring modes.

Important APIs/types/functions: `io_uring_wait_cqes_min_timeout`, `io_uring_prep_read`, `io_uring_prep_nop`, `io_uring_cq_advance`, `IORING_FEAT_MIN_TIMEOUT`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_SETUP_SQPOLL`, `pthread_barrier_t`, and `mtime_since_now`.

Control flow: helper threads write to pipes after configured delays. The tests cover full availability, partial availability within min timeout, late first event, no events, and min-wait values larger or equal to the total wait. `main()` runs the matrix on normal, deferred-taskrun, and SQPOLL rings when available.

State and persistence behavior: transient pipes, ring CQ state, and elapsed time checks. No persistent files.

Dependencies and integration points: uses `t_create_ring_params` to probe setup, feature flag `IORING_FEAT_MIN_TIMEOUT`, pthreads, and helper timing functions.

Risks and test signals: failures are wrong timeout duration, unexpected `-ETIME` or success return, not enough CQEs advanced, or inconsistent behavior across supported ring modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/min-timeout-wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/min-timeout.c -->
# sources/test-tools/liburing/test/min-timeout.c

Purpose: tests `io_uring_submit_and_wait_min_timeout()` with pipe reads, staged writers, context switch expectations, and normal/deferred/SQPOLL rings.

Important APIs/types/functions: `io_uring_submit_and_wait_min_timeout`, `io_uring_prep_read`, `IORING_FEAT_MIN_TIMEOUT`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_SETUP_SQPOLL`, `getrusage(RUSAGE_THREAD)`, `mtime_since_now`, and `pthread_create`.

Control flow: `test()` initializes a ring, arms eight pipe reads, starts a writer that writes six buffers with a configured delay, waits with a total timeout and optional minimum wait, then counts CQEs and elapsed milliseconds. `main()` runs cases with no min timeout, 50 ms, 500 ms, and delayed-first-event variants across setup flags.

State and persistence behavior: no files. State includes pipe readiness, CQE accumulation, min timeout duration, and voluntary context-switch count.

Dependencies and integration points: depends on kernel min-timeout feature detection, pthread timing, and pipe read/write behavior.

Risks and test signals: failures include wrong CQE count, wait duration outside 25 percent tolerance, feature absence skip, or submit returning fewer requests than expected.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/min-timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/mkdir.c -->
# sources/test-tools/liburing/test/mkdir.c

Purpose: validates `IORING_OP_MKDIRAT` success and common error paths.

Important APIs/types/functions: `io_uring_prep_mkdirat`, `io_uring_wait_cqes`, `stat`, `unlinkat`, `AT_FDCWD`, `AT_REMOVEDIR`, and `strerror`.

Control flow: submits mkdirat for `io_uring-mkdirat-test`, checks it exists via `stat`, submits again expecting `-EEXIST`, submits a missing-parent path expecting `-ENOENT`, and submits a bogus pointer expecting `-EFAULT`.

State and persistence behavior: creates one temporary directory and removes it with `unlinkat(..., AT_REMOVEDIR)`.

Dependencies and integration points: depends on current working directory permissions, mkdirat opcode support, and liburing completion helpers.

Risks and test signals: `-EBADF` or `-EINVAL` skips unsupported kernels; any unexpected errno or missing directory is a failure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/mock_file.c -->
# sources/test-tools/liburing/test/mock_file.c

Purpose: integration tests for the `/dev/io_uring_mock` driver, covering mock-file creation, `uring_cmd` probing, registered-buffer copy commands, and mock read paths.

Important APIs/types/functions: `setup_mgr`, `create_mock_file`, `t_copy_regvec`, `t_copy_verify_regvec`, `test_regvec_cmd`, `test_rw`, `io_uring_prep_uring_cmd`, `IORING_URING_CMD_FIXED`, `io_uring_register_buffers`, and structs from `mock_file.h`.

Control flow: opens the mock manager device, probes feature bits, creates mock files, optionally runs registered-buffer copy commands in both directions over complex iovec layouts, and runs read tests over feature combinations of NOWAIT, async delay, and pollable mock files.

State and persistence behavior: uses global manager ring/fd and mock feature bitmap. Mock files are kernel/device objects returned as fds and closed after each test; no ordinary files are persisted.

Dependencies and integration points: requires `/dev/io_uring_mock`, sufficient permissions, liburing test helpers from `test.h`/`helpers.h`, and feature constants from `mock_file.h`.

Risks and test signals: skips when the mock device or feature is missing. Failures are probe/create command errors, copy length/data mismatches, unexpected read CQE sizes, or unsupported feature flags being mishandled.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/mock_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/mock_file.h -->
# sources/test-tools/liburing/test/mock_file.h

Purpose: local ABI header for the io_uring mock-file manager and mock-file commands used by `mock_file.c`.

Important APIs/types/functions: feature enum values `IORING_MOCK_FEAT_*`, `struct io_uring_mock_probe`, `struct io_uring_mock_create`, manager command enums `IORING_MOCK_MGR_CMD_PROBE` and `IORING_MOCK_MGR_CMD_CREATE`, `IORING_MOCK_CMD_COPY_REGBUF`, and `IORING_MOCK_COPY_FROM`.

Control flow: header only; it defines constants and packed-like request structs consumed by `uring_cmd` SQEs.

State and persistence behavior: describes manager-visible fields such as feature bitmap, output fd, flags, mock file size, and artificial read/write delay. It has no executable state.

Dependencies and integration points: includes `<linux/types.h>` and is coupled to the kernel mock driver ABI and the liburing test program.

Risks and test signals: ABI drift between this header and the driver would surface as failed probe/create/copy commands in `mock_file.c`. Reserved fields preserve forward-compatible layout.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/mock_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/msg-ring-fd.c -->
# sources/test-tools/liburing/test/msg-ring-fd.c

Purpose: tests `IORING_OP_MSG_RING` fd passing between rings, both in-process and to a ring owned by another thread.

Important APIs/types/functions: `io_uring_prep_msg_ring_fd`, `io_uring_register_files`, `io_uring_unregister_files`, `io_uring_prep_read`, `io_uring_prep_write`, `IOSQE_FIXED_FILE`, pthread barriers, and `IORING_SETUP_SINGLE_ISSUER | IORING_SETUP_DEFER_TASKRUN`.

Control flow: local mode registers fixed-file tables in source and destination rings, writes random bytes to a pipe, passes the read end into the destination fixed table, then reads via `IOSQE_FIXED_FILE` and compares buffers. Remote mode starts a thread with its own ring and performs the same fd handoff/read flow.

State and persistence behavior: transient pipes, registered fixed-file tables, and thread-shared buffer state. No filesystem persistence.

Dependencies and integration points: depends on sparse/fixed file support, msg-ring fd passing support, pthread synchronization, and normal/deferred ring modes.

Risks and test signals: `-EINVAL` can mark fd passing unsupported and skip. Failures include bad registration, message CQE errors, short reads/writes, or buffer mismatch after transfer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/msg-ring-fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/msg-ring-flags.c -->
# sources/test-tools/liburing/test/msg-ring-flags.c

Purpose: validates msg-ring CQE injection with custom CQE flags through `io_uring_prep_msg_ring_cqe_flags()`.

Important APIs/types/functions: `send_msg`, `recv_msg`, `io_uring_prep_msg_ring_cqe_flags`, `CUSTOM_FLAG`, `USER_DATA`, `LEN`, pthread barrier, and deferred-taskrun ring setup.

Control flow: sends one message to a second local ring, verifies `user_data`, `res`, and `flags`, repeats eight sends/receives, then starts a destination ring in another thread and sends to it.

State and persistence behavior: only in-memory CQE delivery state across rings. No persistent resources beyond ring fds and a joined thread.

Dependencies and integration points: depends on msg-ring cqe-flags opcode support and ring flags 0 plus `SINGLE_ISSUER|DEFER_TASKRUN`.

Risks and test signals: unsupported kernels return skip on `-EINVAL`. Failures are missing custom flags, wrong CQE length/user data, bad sender completion, or remote thread failure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/msg-ring-flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/msg-ring-overflow.c -->
# sources/test-tools/liburing/test/msg-ring-overflow.c

Purpose: tests msg-ring delivery when the destination CQ is undersized and overflows.

Important APIs/types/functions: `io_uring_prep_msg_ring`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_IOPOLL`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_SETUP_SINGLE_ISSUER`, and `io_uring_wait_cqe`.

Control flow: creates a destination ring with four CQ entries, submits eight msg-ring SQEs from a source ring, then drains eight sender completions and eight destination CQEs. The matrix includes normal, IOPOLL, deferred, and deferred+IOPOLL destination flags.

State and persistence behavior: transient CQ overflow/overflow flushing state. No files.

Dependencies and integration points: depends on msg-ring support, CQ size override support, and destination ring modes.

Risks and test signals: detects lost messages, bad len/user_data in overflowed destination CQEs, sender completion errors, and old kernels where only one SQE submits or returns unsupported status.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/msg-ring-overflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/msg-ring.c -->
# sources/test-tools/liburing/test/msg-ring.c

Purpose: broad msg-ring command suite covering self-messages, synchronous registered messages, remote-thread delivery, invalid fds, IOPOLL rings, deferred taskrun, remote submitter threads, and disabled destination rings.

Important APIs/types/functions: `io_uring_prep_msg_ring`, `io_uring_register_sync_msg`, `test_own`, `test_remote`, `test_remote_submit`, `test_invalid`, `test_disabled_ring`, `IORING_SETUP_IOPOLL`, `IORING_SETUP_R_DISABLED`, `IOSQE_FIXED_FILE`, and pthread barriers.

Control flow: `test()` creates normal and IOPOLL rings, sends async and sync messages to self, verifies invalid regular and fixed target fds return `-EBADFD`, sends to a thread-owned ring, and under deferred-taskrun also checks remote submit and disabled-ring behavior. `main()` runs normal flags and deferred flags.

State and persistence behavior: all state is ring-to-ring CQE injection and ring fd lifetime. Fixed-file registration is temporary in invalid-fd tests.

Dependencies and integration points: depends on msg-ring opcode support, sync-msg registration support where available, IOPOLL compatibility, disabled-ring semantics, and pthread synchronization.

Risks and test signals: unsupported msg-ring or sync-msg paths are skipped. Failures include missing remote CQEs, wrong `res`/`user_data`, invalid fd not reporting `-EBADFD`, or disabled ring completion returning an unexpected code.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/msg-ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/mshot-shutdown-race.c -->
# sources/test-tools/liburing/test/mshot-shutdown-race.c

Purpose: stress reproducer for multishot recv racing with a send immediately followed by socket shutdown, ensuring neither data nor EOF events are lost.

Important APIs/types/functions: `io_uring_prep_recv_multishot`, `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_MORE`, `IORING_CQE_F_BUFFER`, `socketpair`, optional loopback TCP via `TEST_USE_INET`, and pthread barriers.

Control flow: a client thread waits on a barrier, sends one or two fixed-size messages, then `shutdown(SHUT_WR)`. For 10,000 iterations, main creates sockets, arms one multishot recv with provided buffers, releases the client, drains CQEs until EOF, replenishes buffers, verifies flags, and checks total bytes.

State and persistence behavior: no files. State is provided-buffer ownership, multishot continuation flags, socket shutdown state, and a watchdog alarm that detects stalls.

Dependencies and integration points: depends on AF_UNIX socketpair by default or AF_INET loopback when `TEST_USE_INET` is set, buf-ring support, and multishot receive semantics.

Risks and test signals: failures include missing `MORE` on data CQEs, buffer flag missing, EOF still marked `MORE`, wrong byte count, unexpected negative recv, or watchdog timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/mshot-shutdown-race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/multicqes_drain.c -->
# sources/test-tools/liburing/test/multicqes_drain.c

Purpose: randomized and simple tests for drain ordering when multishot poll can produce multiple CQEs before cancellation.

Important APIs/types/functions: `io_uring_prep_poll_add`, `io_uring_prep_poll_multishot`, `io_uring_prep_poll_remove`, `io_uring_prep_nop`, `io_uring_get_events`, `io_uring_submit_and_get_events`, `IOSQE_IO_DRAIN`, `IOSQE_IO_LINK`, and `IORING_POLL_ADD_MULTI`.

Control flow: the simple test arms multishot and single poll, triggers events, then removes the multishot and submits a drained NOP, expecting the drained NOP last. The generic test randomly generates up to 50 operations across multishot poll, single poll, NOP, and cancel while avoiding illegal link/drain combinations, then verifies drained CQEs appear only after all prior non-multishot or canceled multishot work is complete.

State and persistence behavior: transient pipes and arrays tracking generated SQE metadata, active multishot requests, and completion bitmaps. No persistent files.

Dependencies and integration points: uses time-based randomness, pipes, optional deferred-taskrun mode, and liburing CQ event pumping helpers.

Risks and test signals: catches drain completion before earlier work, improper multishot cancellation accounting, lost events under deferred taskrun, or illegal ordering after randomized chains.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/multicqes_drain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/napi-test.c -->
# sources/test-tools/liburing/test/napi-test.c

Purpose: NAPI busy-poll receive test run either directly through `napi-test.sh` or as sender/receiver roles inside network namespaces.

Important APIs/types/functions: `io_uring_register_napi`, `struct io_uring_napi`, `io_uring_prep_recv`, TCP sockets, `setsockopt`, `inet_pton`, `accept`, `connect`, `geteuid`, and role arguments `receive`/`send`.

Control flow: with no args, it locates and runs the shell script. Receiver mode creates a ring with supplied queue flags, registers NAPI preferences, listens on port 9999, accepts a connection, receives 4 KiB buffers through io_uring, and validates byte sequence. Sender mode probes ring creation with the same flags, connects to `10.10.10.20`, and writes 8 MiB of patterned data.

State and persistence behavior: no files. State is TCP stream order, NAPI registration settings, and a shared `current_byte` sequence per process.

Dependencies and integration points: requires root, the companion shell script, network namespaces/veth setup, and NAPI-capable kernel support. It is intended to be invoked as `napi-test.t receive|send <flags>`.

Risks and test signals: skips when not root or ring flags unsupported. Failures include bind/connect errors, receive CQE errors, short/failed writes, or data pattern mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/napi-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/napi-test.sh -->
# sources/test-tools/liburing/test/napi-test.sh

Purpose: creates an isolated two-namespace veth topology and runs `napi-test.t` sender/receiver pairs for multiple queue flag configurations.

Important APIs/types/functions: `ip netns`, `ip link add ... type veth`, `ethtool -K`, shell `trap`, `QUEUE_FLAGS="0x0 0x3000 0x2"`, and executable discovery for `napi-test.t`.

Control flow: verifies `ip` and `ethtool` exist, installs an EXIT cleanup trap, creates client/server namespaces and veth peers, assigns `10.10.10.10/24` and `10.10.10.20/24`, adjusts offloads, brings links up, then for each flag starts receiver in server namespace, runs sender in client namespace, and waits.

State and persistence behavior: creates temporary network namespaces and veth devices, deleted by `clean_namespaces` on exit. No repository files are modified.

Dependencies and integration points: requires root or namespace privileges, iproute2, ethtool, and the compiled test binary in current or `test/` path.

Risks and test signals: missing tools exit 77, missing binary exits 77, and networking/setup failures propagate as nonzero shell exits. Cleanup assumes namespace names are not used by other processes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/napi-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/no-mmap-inval.c -->
# sources/test-tools/liburing/test/no-mmap-inval.c

Purpose: verifies `IORING_SETUP_NO_MMAP` rejects an invalid user-provided SQ/CQ mapping layout.

Important APIs/types/functions: `io_uring_queue_init_params`, `IORING_SETUP_NO_MMAP`, `io_uring_params.cq_off.user_addr`, `t_posix_memalign`, `sysconf(_SC_PAGESIZE)`, `-EFAULT`, and `-ENOMEM`.

Control flow: allocates one page-aligned 8 KiB area, sets only the CQ user address in params, and tries to initialize a no-mmap ring. Unsupported kernels returning `-EINVAL` or `-ENOENT` skip; expected invalid mapping returns `-EFAULT` or sometimes `-ENOMEM`.

State and persistence behavior: one allocated userspace buffer is freed. No ring should be successfully persisted.

Dependencies and integration points: depends on no-mmap setup support and helper allocation. It directly probes kernel validation of user ring addresses.

Risks and test signals: any return other than unsupported skip, expected fault, or memory failure is a test failure, as it suggests bad validation or changed error semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/no-mmap-inval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/nolibc.c -->
# sources/test-tools/liburing/test/nolibc.c

Purpose: validates liburing's nolibc helper `get_page_size()` against libc `sysconf(_SC_PAGESIZE)` on supported architectures.

Important APIs/types/functions: architecture preprocessor guards, `CONFIG_NOLIBC`, `../src/lib.h`, `get_page_size`, `sysconf`, and `T_EXIT_SKIP`.

Control flow: unsupported architectures compile a main that skips. Supported architectures define `CONFIG_NOLIBC`, include liburing internals, compare page-size values, and pass or fail.

State and persistence behavior: no mutable external state or persistence.

Dependencies and integration points: coupled to liburing internal `src/lib.h` and architecture support for nolibc implementations on x86, x86-64, aarch64, and riscv64.

Risks and test signals: failure means nolibc page-size detection differs from libc, which can break mmap/ring sizing paths in nolibc builds.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/nolibc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/nop-all-sizes.c -->
# sources/test-tools/liburing/test/nop-all-sizes.c

Purpose: exercises NOP submission and completion across ring depths from 1 up to 32768.

Important APIs/types/functions: `fill_nops`, `test_nops`, `io_uring_get_sqe`, `io_uring_prep_nop`, `io_uring_submit`, `io_uring_wait_cqe`, and `io_uring_queue_init`.

Control flow: for each power-of-two depth, creates a ring, fills and submits all available SQEs twice, then waits for the total number of completions before doubling depth. `-ENOMEM` stops the size sweep gracefully.

State and persistence behavior: ring allocation and CQ/SQ occupancy only. No filesystem state.

Dependencies and integration points: depends on memory limits and maximum allowed ring size. No helper status constants are used in the normal path.

Risks and test signals: catches off-by-one SQ fill behavior, submission count mismatch, CQ drain failures, and large-ring allocation or completion issues.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/nop-all-sizes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/nop-flags.c -->
# sources/test-tools/liburing/test/nop-flags.c

Purpose: tests extended NOP flags that force file lookup, fixed-file lookup, registered-buffer lookup, task-work completion, injected results, and 32-byte CQE payloads.

Important APIs/types/functions: `IORING_NOP_INJECT_RESULT`, `IORING_NOP_FILE`, `IORING_NOP_FIXED_FILE`, `IORING_NOP_FIXED_BUFFER`, `IORING_NOP_TW`, `IORING_NOP_CQE32`, `IORING_SETUP_SUBMIT_ALL`, `IORING_SETUP_CQE32`, `io_uring_register_files`, `io_uring_register_buffers`, and `cqe->big_cqe`.

Control flow: first detects support by injecting result 42. It then probes bad fd behavior, validates normal and fixed file lookup, validates registered buffer lookup and bad buffer error, submits task-work NOPs, tests task-work plus injected result, checks CQE32 extra fields on a CQE32 ring, checks CQE32 rejection on a normal ring, and finally combines file/fixed-buffer/task-work flags.

State and persistence behavior: opens `/dev/null`, registers temporary file and buffer tables, and tears them down. No persistent files.

Dependencies and integration points: depends on newer kernel NOP flag support but defines missing constants locally for build compatibility. Integrates with helpers for exit statuses.

Risks and test signals: skips unsupported subfeatures. Failures include ignored lookup errors, wrong injected result, missing `big_cqe` payload, CQE32 accepted on unsupported rings, or combined flags not resolving registered resources.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/nop-flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/nop.c -->
# sources/test-tools/liburing/test/nop.c

Purpose: baseline NOP stress test across all configured ring test modes, including async requests, drain barriers, injected results, and optional CQE32 verification.

Important APIs/types/functions: `FOR_ALL_TEST_CONFIGS`, `IORING_GET_TEST_CONFIG_FLAGS`, `io_uring_prep_nop`, `IOSQE_ASYNC`, `IOSQE_IO_DRAIN`, `IORING_NOP_INJECT_RESULT`, `IORING_SETUP_CQE32`, and `cqe->big_cqe`.

Control flow: for each test configuration, `test_ring()` loops 1000 times, alternating async flag use. Each iteration submits one NOP, an eight-NOP batch with the fifth marked drain, and an injected-result NOP expecting either `-EFAULT` or `-EINVAL`.

State and persistence behavior: `seq` provides increasing `user_data`; otherwise only ring CQ/SQ state is used. No persistent state.

Dependencies and integration points: depends on `test.h` configuration macros and liburing support for each selected setup flag.

Risks and test signals: failures are missing `user_data`, nonzero CQE32 extras for ordinary NOPs, bad drain batch submission, or injected-result handling outside allowed error codes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/nop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/nop32-overflow.c -->
# sources/test-tools/liburing/test/nop32-overflow.c

Purpose: validates mixed 16-byte/32-byte CQE handling when a small CQ overflows.

Important APIs/types/functions: `IORING_SETUP_CQE_MIXED`, `IORING_SETUP_CQSIZE`, `IORING_NOP_CQE32`, `IORING_CQE_F_32`, `IORING_CQE_F_SKIP`, `io_uring_for_each_cqe`, `io_uring_cqe_nr`, and `io_uring_cq_advance`.

Control flow: creates an eight-entry SQ with a CQ size of eight but mixed CQE sizing. Submits eight NOPs where the first is normal and the rest request CQE32. It inspects visible CQEs for one normal, three 32-byte, and a skip CQE, advances by the correct CQE slot count, then waits for four overflowed 32-byte CQEs.

State and persistence behavior: transient CQ overflow state and sequence counter only.

Dependencies and integration points: depends on mixed CQE support and liburing helpers for iterating variable-sized CQEs.

Risks and test signals: detects incorrect CQE slot accounting, missing 32-bit flags, absent skip CQE, bad overflow flushing, or wrong user_data order after overflow.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/nop32-overflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/nop32.c -->
# sources/test-tools/liburing/test/nop32.c

Purpose: verifies `IORING_NOP_CQE32` produces 32-byte CQEs with expected extra fields on a mixed-CQE ring.

Important APIs/types/functions: `IORING_SETUP_CQE_MIXED`, `IORING_NOP_CQE32`, `IORING_CQE_F_32`, `sqe->off`, `sqe->addr`, and `cqe->big_cqe`.

Control flow: initializes a mixed-CQE ring, submits one ordinary NOP, then submits 16 CQE32 NOPs with increasing `off` and `addr` values and validates `big_cqe[0]` and `[1]` against expected counters.

State and persistence behavior: in-memory sequence and expected extra counters only.

Dependencies and integration points: depends on mixed CQE and NOP CQE32 support; `-EINVAL` setup skips.

Risks and test signals: catches missing `IORING_CQE_F_32`, corrupted extra fields, or broken ordinary NOP behavior on a mixed ring.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/nop32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/nvme.h -->
# sources/test-tools/liburing/test/nvme.h

Purpose: helper header for tests that issue NVMe io_uring passthrough commands and need namespace geometry.

Important APIs/types/functions: fallback `struct nvme_uring_cmd`, `NVME_URING_CMD_IO`, `NVME_URING_CMD_IO_VEC`, `struct nvme_id_ns`, `struct nvme_lbaf`, `nvme_get_info`, `NVME_IOCTL_ID`, `NVME_IOCTL_ADMIN_CMD`, `nvme_admin_identify`, `nvme_cmd_read`, `nvme_cmd_write`, `ilog2`, and globals `nsid`, `lba_shift`, `meta_size`.

Control flow: `nvme_get_info()` opens an NVMe device, obtains the namespace id via ioctl, sends an identify admin command, derives LBA size/shift and metadata size from the active LBA format, then closes the fd.

State and persistence behavior: stores namespace id, LBA shift, and metadata size in static globals for later test code. It does not write to the device.

Dependencies and integration points: depends on `<linux/nvme_ioctl.h>` and supplies local uring command definitions when system headers lack them. Intended for inclusion by NVMe passthrough tests.

Risks and test signals: ioctl failures return negative errno or raw admin error, causing callers to skip/fail device tests. Header ABI compatibility is critical for older distro headers.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/nvme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ooo-file-unreg.c -->
# sources/test-tools/liburing/test/ooo-file-unreg.c

Purpose: checks that out-of-order sparse fixed-file unregistration with an in-flight poll request does not corrupt or hang ring cleanup.

Important APIs/types/functions: `io_uring_register_files_sparse`, `io_uring_register_files_update`, `io_uring_prep_poll_add`, `IOSQE_FIXED_FILE`, UDP sockets, and `sleep`.

Control flow: registers two sparse fixed-file slots, installs two UDP sockets, submits a poll on fixed slot 0, closes the original sockets, unregisters slot 1 first and slot 0 second by updating them to `-1`, sleeps briefly, then exits the ring.

State and persistence behavior: fixed-file table state and an in-flight poll request are the tested state. No files are persisted.

Dependencies and integration points: depends on sparse fixed-file tables and socket poll behavior. `-EINVAL` for sparse registration skips.

Risks and test signals: failures are bad registration/update counts or ring exit problems after unregistering slots while fixed-file poll is pending.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ooo-file-unreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/open-close.c -->
# sources/test-tools/liburing/test/open-close.c

Purpose: tests io_uring open and close operations, including relative/absolute openat, closing normal and ring fds, fixed-file close, close flush, and direct-open `O_CLOEXEC` rejection.

Important APIs/types/functions: `io_uring_prep_openat`, `io_uring_prep_close`, `__io_uring_set_target_fixed_file`, `io_uring_register_files`, `test_close_fixed`, `test_close_flush`, `test_open_direct_cloexec`, `t_create_file`, `O_CLOEXEC`, and `IOSQE_FIXED_FILE`.

Control flow: creates `/tmp/.open.close` and optionally a relative file, opens both via io_uring, closes the returned fd, attempts to close the ring fd expecting wait failure/`-EBADF`, exercises fixed-file close error and success cases, optionally closes tracing `trace_pipe_raw`, and ensures direct open with `O_CLOEXEC` fails with `-EINVAL`.

State and persistence behavior: creates temporary files and unlinks them. Fixed-file table slots are mutated and verified by a subsequent fixed-file read returning `-EBADF`.

Dependencies and integration points: depends on file permissions, optional debugfs tracing file, fixed-file close support, and helpers for creating files.

Risks and test signals: skip on unsupported open or access-restricted files. Failures include wrong close error codes, fixed table not invalidated, or direct open accepting incompatible flags.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/open-close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/open-direct-link.c -->
# sources/test-tools/liburing/test/open-direct-link.c

Purpose: validates linked or drained direct open/read/close through fixed-file slot 0, including skipped success CQEs and async submission.

Important APIs/types/functions: `io_uring_prep_openat_direct`, `io_uring_prep_read`, `io_uring_prep_close_direct`, `io_uring_register_files`, `IOSQE_FIXED_FILE`, `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, `IOSQE_CQE_SKIP_SUCCESS`, and `IOSQE_ASYNC`.

Control flow: registers eight fixed-file slots initialized to `-1`, creates `.link.direct`, then runs six combinations: link, drain, async link, async drain, skip-success link, and async skip-success link. Each sequence opens into slot 0, reads 4096 bytes via fixed file, and closes slot 0.

State and persistence behavior: creates `.link.direct` and unlinks it. Fixed-file slot 0 is repeatedly installed and closed.

Dependencies and integration points: requires fixed-file registration and `IORING_FEAT_CQE_SKIP`; skips if extra argument is provided or feature absent.

Risks and test signals: failures include bad open/read/close CQE results, unexpected CQE when success CQEs are skipped, or illegal drain/skip-success combination.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/open-direct-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/open-direct-pick.c -->
# sources/test-tools/liburing/test/open-direct-pick.c

Purpose: tests auto-allocation of direct fixed-file slots via `file_index = UINT_MAX` and exhaustion behavior.

Important APIs/types/functions: `io_uring_register_files_sparse`, `io_uring_prep_openat_direct`, `io_uring_prep_close_direct`, `UINT_MAX`, `FDS=800`, and `t_create_file`.

Control flow: registers an 800-slot sparse table, opens the same file 800 times into auto-picked slots, randomly closes 100 occupied slots, opens 100 more successfully, then attempts one extra open expecting `-ENFILE`.

State and persistence behavior: creates `/tmp/.open.direct.pick` and unlinks it. Fixed-file table occupancy is the tested state.

Dependencies and integration points: depends on sparse file registration and direct slot picking support. `-EINVAL` on first auto-pick marks feature unsupported and exits successfully.

Risks and test signals: failures are bad auto-pick error handling, inability to reuse closed slots, wrong full-table error, or random close loop not finding occupied slots.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/open-direct-pick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/openat2.c -->
# sources/test-tools/liburing/test/openat2.c

Purpose: tests `IORING_OP_OPENAT2` normal opens, direct fixed-file opens, invalid fixed slots, reinstalling over an existing fixed slot, and bad pointer errors.

Important APIs/types/functions: `struct open_how`, `io_uring_prep_openat2`, `io_uring_prep_openat2_direct`, `io_uring_register_files`, `io_uring_prep_write`, `io_uring_prep_read`, `IOSQE_FIXED_FILE`, `IOSQE_IO_LINK`, `pipe2(O_NONBLOCK)`, and `t_create_file`.

Control flow: opens absolute and relative paths with openat2, opens into fixed slot 0 and verifies write/read through that slot, checks direct open without a table returns `-ENXIO`, out-of-bounds and u16-overflow indexes return `-EINVAL`, reinstalls a file over pipe slot 1 and verifies pipe is not written, then tests bad path and bad `open_how` pointers expecting `-EFAULT`.

State and persistence behavior: creates `/tmp/.open.at2` and optionally `.open.at2`, then unlinks them. Fixed-file tables and a pipe table entry are mutated transiently.

Dependencies and integration points: depends on openat2 kernel support, fixed-file direct-open support, and filesystem permissions.

Risks and test signals: unsupported openat2 or fixed-open paths skip. Failures indicate wrong direct-slot validation, stale fixed-file slot content after reinstall, or missing bad-address checking.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/openat2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/personality.c -->
# sources/test-tools/liburing/test/personality.c

Purpose: verifies io_uring personality registration executes operations under saved credentials, including linked operations, and rejects invalid personality ids.

Important APIs/types/functions: `io_uring_register_personality`, `io_uring_unregister_personality`, `sqe->personality`, `seteuid`, `geteuid`, `io_uring_prep_openat`, `IOSQE_IO_LINK`, `FNAME=/tmp/.tmp.access`, and `USE_UID=1000`.

Control flow: root-only main registers current credentials, creates a 0600 file, verifies current root can open it, switches effective uid to 1000, verifies normal open fails with `-EACCES`, verifies open with registered personality succeeds both standalone and after a linked NOP, restores euid 0, unregisters, then checks invalid personality use and unregister return `-EINVAL`.

State and persistence behavior: creates `/tmp/.tmp.access` and removes it. Stores one registered credential id in the ring until unregistered.

Dependencies and integration points: requires root and a usable UID 1000. `-EINVAL` personality registration skips unsupported kernels.

Risks and test signals: failures are credential leakage, inability to use registered credentials in linked chains, invalid ids accepted, or failure to restore/unregister credentials.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/pipe-bug.c -->
# sources/test-tools/liburing/test/pipe-bug.c

Purpose: regression test for task_work execution after pipe write/close/read sequencing, linked to a bug where task_work was gated incorrectly.

Important APIs/types/functions: `io_uring_prep_write`, `io_uring_prep_close`, `io_uring_prep_read`, `io_uring_wait_cqe_timeout`, pipe fds, `__kernel_timespec`, and `CHECK` macro.

Control flow: `pipe_bug()` creates a ring and pipe, writes "foobar" through io_uring, closes the write end through io_uring, reads available data, then reads EOF, each with a one-second timeout for close/read paths. `main()` repeats this 10,000 times.

State and persistence behavior: transient pipe and ring state only. `-ENOMEM` during ring creation is tolerated with a short sleep.

Dependencies and integration points: depends on pipe semantics and task_work completion paths in the kernel.

Risks and test signals: timeouts or failed CHECKs indicate close/read completions stuck behind task_work notification bugs. Repetition aims to expose intermittent failures.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/pipe-bug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/pipe-direct-fixed.c -->
# sources/test-tools/liburing/test/pipe-direct-fixed.c

Purpose: validates `io_uring_prep_pipe_direct()` when creating pipes in explicit fixed-file slots, including the historic bug where non-auto slot installs reported or cleaned up slot 0.

Important APIs/types/functions: `io_uring_register_files_sparse`, `io_uring_register_files_update`, `io_uring_prep_pipe_direct`, `io_uring_prep_read`, `io_uring_prep_write`, `IOSQE_FIXED_FILE`, and fixed slot indexes.

Control flow: `test_specific_slots()` creates a fixed pipe at requested slot and slot+1, verifies returned indexes, then writes/reads through fixed slots. It runs for slot 5 and slot 0. `test_no_clobber_slot0()` installs a sentinel pipe read-end at slot 0, creates another fixed pipe at slots 5/6, and verifies slot 0 still reads sentinel data.

State and persistence behavior: fixed-file table entries and pipe fds are transient. No files.

Dependencies and integration points: requires sparse fixed-file support and pipe-direct opcode support; `-EINVAL` marks no-pipe skip.

Risks and test signals: failures are wrong returned slot indexes, broken fixed pipe communication, or clobbering slot 0 during nonzero slot installation/cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/pipe-direct-fixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/pipe-eof.c -->
# sources/test-tools/liburing/test/pipe-eof.c

Purpose: verifies that reads from a pipe whose writer has closed complete with EOF (`res == 0`) instead of waiting indefinitely.

Important APIs/types/functions: `pthread_create`, `io_uring_prep_read`, `io_uring_submit`, `io_uring_wait_cqe`, pipe fds, and `BUFSIZE`.

Control flow: a thread writes a test string to the pipe and closes the write end. Main repeatedly submits pipe reads via io_uring until a CQE returns zero, treating negative results as errors.

State and persistence behavior: transient pipe, thread, and static buffer only.

Dependencies and integration points: depends on standard pipe EOF semantics and io_uring read completion.

Risks and test signals: failure is any read error, submit/wait failure, or hang before EOF. `-ENOMEM` ring setup skips.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/pipe-eof.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/pipe-reuse.c -->
# sources/test-tools/liburing/test/pipe-reuse.c

Purpose: checks that split pipe `readv` uses stable submitted iovecs even if userspace mutates them after submission.

Important APIs/types/functions: `io_uring_prep_readv`, `IORING_FEAT_SUBMIT_STABLE`, `struct iovec`, pipe writes, and `memcmp`.

Control flow: fills a 16-entry iovec over a 16 KiB buffer, writes half the data, submits readv, overwrites all iovec bases/lengths with invalid values, writes the second half, then waits and compares the received buffer to the original pattern.

State and persistence behavior: transient pipe and stack buffers only.

Dependencies and integration points: depends on `IORING_FEAT_SUBMIT_STABLE`; skips if absent. Uses pipe buffering to force split completion after userspace iovec mutation.

Risks and test signals: data mismatch or read error means the kernel reused mutated userspace iovec data rather than the stable submission copy. Short reads are ignored rather than fatal.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/pipe-reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/pipe.c -->
# sources/test-tools/liburing/test/pipe.c

Purpose: tests pipe creation through io_uring, both normal fd output and fixed-file direct output, with async requests, multiple ring modes, and too-small fixed tables.

Important APIs/types/functions: `io_uring_prep_pipe`, `io_uring_prep_pipe_direct`, `IORING_FILE_INDEX_ALLOC`, `io_uring_register_files_sparse`, `io_uring_prep_read`, `io_uring_prep_write`, `IOSQE_ASYNC`, `IOSQE_FIXED_FILE`, `IORING_SETUP_SQPOLL`, and `IORING_SETUP_DEFER_TASKRUN`.

Control flow: for normal, SQPOLL, and deferred rings, it runs eight parameter combinations of fixed/nonfixed, async/sync, and too-small table. Successful pipe creation is followed by a 32-byte write/read communication test. A fixed too-small table expects `-ENFILE`.

State and persistence behavior: transient pipe fds and fixed-file table slots. Normal fds are closed explicitly; ring exit releases fixed ones.

Dependencies and integration points: depends on pipe opcode and fixed pipe support. `-EINVAL` marks feature unsupported and skips.

Risks and test signals: failures include wrong pipe creation result, fixed table exhaustion not detected, bad communication through created fds, or mode-specific regressions under SQPOLL/deferred taskrun.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-cancel-all.c -->
# sources/test-tools/liburing/test/poll-cancel-all.c

Purpose: validates async cancel flags for cancel-all-by-fd, fixed fd cancellation, cancel-any across mixed poll/read operations, and selective cancellation among multiple fds.

Important APIs/types/functions: `io_uring_prep_poll_add`, `io_uring_prep_cancel`, `io_uring_prep_read`, `IORING_ASYNC_CANCEL_ALL`, `IORING_ASYNC_CANCEL_FD`, `IORING_ASYNC_CANCEL_FD_FIXED`, `IORING_ASYNC_CANCEL_ANY`, `IOSQE_FIXED_FILE`, and `IOSQE_ASYNC`.

Control flow: `test1()` arms eight polls on one pipe and cancels all by fd, including fixed-file mode. `test2()` arms polls on two pipes and cancels one fd at a time, checking no extra CQEs leak. `test3()` cancels mixed async polls with CANCEL_ANY. `test4()` cancels eight async pipe reads. Main runs these on one ring after creating a pipe.

State and persistence behavior: transient pipes, optional fixed-file registrations, and in-flight poll/read requests.

Dependencies and integration points: depends on cancel flag support; `-EINVAL` on cancel completion sets `no_cancel_flags` and skips later flag-specific tests.

Risks and test signals: expected cancel CQE counts are exact: 8, 4, 8, or 8 depending on test. Poll/read CQEs must report `-ECANCELED`; extra or missing completions are failures.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-cancel-all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-cancel-ton.c -->
# sources/test-tools/liburing/test/poll-cancel-ton.c

Purpose: stress test for adding and removing very large numbers of poll requests by user-data identity.

Important APIs/types/functions: `POLL_COUNT=30000`, `sqe_index`, `io_uring_prep_poll_add`, `io_uring_prep_poll_remove`, `IORING_SETUP_CQSIZE`, `io_uring_peek_cqe`, and `io_uring_wait_cqe`.

Control flow: initializes a ring with large CQ when supported, batches 30,000 poll adds in chunks of 1024, storing SQE pointers as user data, then submits random poll remove batches and reaps up to twice each batch count.

State and persistence behavior: one pipe and the ring's large pending poll set are transient. `sqe_index` tracks cancellation keys.

Dependencies and integration points: depends on memory, CQ sizing support, and poll remove semantics. Falls back to normal ring if CQSIZE unsupported.

Risks and test signals: catches scalability issues, missed cancel completions, bad submit counts, and failure to handle large randomized cancel workloads.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-cancel-ton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-cancel.c -->
# sources/test-tools/liburing/test/poll-cancel.c

Purpose: tests basic poll remove completion ordering and a child-exit cleanup path involving timeouts linked to ring-fd polling.

Important APIs/types/functions: `io_uring_prep_poll_add`, `io_uring_prep_poll_remove`, `io_uring_sqe_set_data`, `io_uring_cqe_get_data`, `io_uring_prep_timeout`, `io_uring_prep_link_timeout`, `fork`, `waitpid`, and `alarm`.

Control flow: the first test arms a poll on a pipe, submits a poll remove keyed by the poll's user data pointer, and waits for both cancel and poll CQEs, accepting either order with exact results. The second forks a child that submits a timeout, a linked poll on another ring fd, and a link timeout, then exits without cleanup so process exit cancels everything.

State and persistence behavior: transient pipes, rings, and child process state only.

Dependencies and integration points: depends on poll cancel semantics and kernel cleanup of ring resources on process exit.

Risks and test signals: failures are cancel CQE nonzero, poll CQE not `-ECANCELED`, alarm timeout, or child cleanup causing nonzero exit.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-cancel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-link.c -->
# sources/test-tools/liburing/test/poll-link.c

Purpose: validates linked poll plus link-timeout behavior for both timeout and ready-connection cases.

Important APIs/types/functions: pthread condition/barrier helpers, TCP loopback sockets, `t_bind_ephemeral_port`, `io_uring_prep_poll_add`, `io_uring_prep_link_timeout`, `IOSQE_IO_LINK`, `POLLIN`, `POLLHUP`, and `POLLERR`.

Control flow: a receiver thread listens on an ephemeral port, submits linked poll and timeout, and checks two CQEs against expected values. For no-connect, poll should be `-ECANCELED` and timeout `-ETIME`. For connect, poll should include `POLLIN` and timeout should be `-ECANCELED`. A sender thread connects only in the ready case.

State and persistence behavior: transient sockets and synchronization flags. No files.

Dependencies and integration points: depends on loopback TCP, helper ephemeral binding, and exact linked timeout cancellation semantics.

Risks and test signals: detects poll not canceled on timeout, timeout not canceled when poll completes, or mask mismatches when accepting a connection.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-many.c -->
# sources/test-tools/liburing/test/poll-many.c

Purpose: scales poll add/rearm over thousands of pipe fds to stress poll readiness and CQ handling.

Important APIs/types/functions: `NFILES=5000`, `BATCH=500`, `NLOOPS=1000`, `io_uring_prep_poll_add`, `IORING_SETUP_CQSIZE`, `RLIMIT_NOFILE`, `t_probe_defer_taskrun`, and pipe read/write.

Control flow: raises file descriptor limit when possible, creates many pipes, arms a poll on each, then for 1000 loops randomly triggers 500 untriggered pipes, reaps 500 CQEs, reads one byte, rearms each poll, and submits the rearm batch. It repeats under deferred-taskrun when supported.

State and persistence behavior: thousands of transient pipe fds and per-pipe `triggered` flags. No persistent files.

Dependencies and integration points: depends on high fd limits and optionally CQSIZE. Skips when not enough files can be opened and privileges cannot raise limits.

Risks and test signals: failures indicate lost poll readiness, rearm submit mismatch, bad CQ size behavior, or deferred-taskrun poll regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-many.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-mshot-overflow.c -->
# sources/test-tools/liburing/test/poll-mshot-overflow.c

Purpose: validates multishot poll behavior when CQ overflow occurs, including downgrade/no-more signaling and remove behavior.

Important APIs/types/functions: `io_uring_prep_poll_multishot`, `io_uring_prep_poll_remove`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_CQE_F_MORE`, `io_uring_get_events`, and `io_uring_cq_ready`.

Control flow: `test_downgrade()` uses a two-entry CQ and repeatedly triggers a multishot poll to inspect whether overflow causes a final CQE without `MORE`. `test()` fills a tiny CQ with NOPs, triggers multishot poll overflow, drains NOPs, forces event processing, removes the poll, and validates final CQEs.

State and persistence behavior: transient pipe and CQ overflow state. No files.

Dependencies and integration points: uses `SINGLE_ISSUER` as a proxy for newer behavior and optionally deferred taskrun support.

Risks and test signals: failures are no downgrade on kernels expected to downgrade, `MORE` flag after terminal CQE, missing poll CQE, or unexpected user data while flushing overflow/removal.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-mshot-overflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-mshot-update.c -->
# sources/test-tools/liburing/test/poll-mshot-update.c

Purpose: stress-tests multishot poll update requests while many pipe polls are concurrently triggered.

Important APIs/types/functions: `io_uring_prep_poll_multishot`, `io_uring_prep_poll_update`, `IORING_POLL_UPDATE_EVENTS`, `IORING_TIMEOUT_UPDATE`, `IORING_CQE_F_MORE`, `RLIMIT_NOFILE`, pthread trigger thread, and `O_NONBLOCK`.

Control flow: first probes poll-update support by expecting `-ENOENT` for an update to a missing request. It then creates up to 5000 nonblocking pipes, arms multishot polls, and for each loop starts a thread that writes to 500 pipes while the main thread submits 500 update SQEs and drains both update and poll CQEs. It runs with CQ sizes 1024 and 8192.

State and persistence behavior: transient pipe arrays, trigger flags, multishot poll state, and update completions. No persistent files.

Dependencies and integration points: requires poll update support, high fd limits, pthreads, and CQSIZE support or fallback.

Risks and test signals: failures include lost update completions, stale non-MORE poll needing failed rearm, read errors other than EAGAIN, and concurrency races between updates and readiness.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-mshot-update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-mshot-wake.c -->
# sources/test-tools/liburing/test/poll-mshot-wake.c

Purpose: verifies multishot poll remains functional when polling the same eventfd used for io_uring CQ notifications.

Important APIs/types/functions: `eventfd`, `io_uring_register_eventfd`, `io_uring_prep_poll_multishot`, `io_uring_wait_cqe_timeout`, `IORING_CQE_F_MORE`, and `NR_LOOPS=2`.

Control flow: registers a nonblocking eventfd as the ring notification fd, arms multishot poll on that eventfd, then twice writes and drains the eventfd and waits for a poll CQE. The first CQE should have `MORE`; the second is expected to terminate without `MORE`.

State and persistence behavior: transient eventfd, ring eventfd registration, and multishot poll state.

Dependencies and integration points: depends on eventfd notification integration and poll wake path handling `EPOLL_URING_WAKE`.

Risks and test signals: failure indicates a stuck multishot poll, missing CQE within one second, wrong user_data/res, or incorrect `MORE` flag transition.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-mshot-wake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-race-mshot.c -->
# sources/test-tools/liburing/test/poll-race-mshot.c

Purpose: checks that racing socket wakeups do not reissue poll/multishot receive in ways that leak provided buffers or produce duplicate completions.

Important APIs/types/functions: `io_uring_setup_buf_ring`, `io_uring_prep_recv`, `io_uring_prep_recv_multishot`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, `IORING_CQE_F_MORE`, socketpair, pthread barrier, and `io_uring_free_buf_ring`.

Control flow: for 1000 loops, the regular test posts 64 receives using a provided buffer ring while another thread writes 64 buffers; every CQE must include a valid buffer id. Then for another 1000 loops, the multishot test arms one multishot receive with the same buffer ring and expects 64 data events plus terminal behavior or an explicit quieting path on kernels with `msg_inq` support.

State and persistence behavior: transient socketpairs, provided buffer rings, allocated receive buffers, and thread synchronization.

Dependencies and integration points: depends on buf-ring support, socket wakeups, and multishot recv behavior. `-EINVAL` buf-ring setup skips the whole test.

Risks and test signals: detects missing buffer ids, invalid buffer ids, too many CQEs, bad receive sizes, or multishot termination races that would leak buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-race-mshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-race.c -->
# sources/test-tools/liburing/test/poll-race.c

Purpose: stress test for multiple concurrent receives on the same socket when readiness wakeups race.

Important APIs/types/functions: `socketpair`, `io_uring_prep_recv`, `io_uring_submit`, `io_uring_wait_cqe`, pthread barrier, and `NREQS=64`.

Control flow: initializes one ring, then 1000 times creates a socketpair, starts a writer thread, queues 64 recv SQEs on one socket, releases the writer, submits all requests, and waits for 64 completions.

State and persistence behavior: transient socketpairs and a shared barrier. No files.

Dependencies and integration points: depends on PF_LOCAL stream socket readiness and io_uring receive poll-wakeup internals.

Risks and test signals: failure means a receive stalled or submit count was short under racing wakeups; CQE result contents are not deeply validated here.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-ring.c -->
# sources/test-tools/liburing/test/poll-ring.c

Purpose: minimal regression test for polling an io_uring ring fd from the same ring, which can create circular references during process exit.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_prep_poll_add`, `io_uring_sqe_set_data`, `ring.ring_fd`, and `POLLIN`.

Control flow: creates a one-entry ring, queues a poll add on `ring.ring_fd`, submits it, and exits without explicitly draining or tearing the ring down.

State and persistence behavior: intentionally leaves an in-flight poll on the ring fd so process cleanup exercises reference release. No files.

Dependencies and integration points: depends on kernel ring-fd poll support and process-exit cleanup paths.

Risks and test signals: direct process return is success; external harnesses detect buggy kernels by stuck worker references or hung exit after the circular poll.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-ring.c -->
