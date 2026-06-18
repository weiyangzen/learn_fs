# Research Report: subset-b-009287

This grouped report covers the 32 liburing test sources assigned to `subset-b-009287`. Each section is source-tree aligned and wrapped for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-update-trigger.c -->
# sources/test-tools/liburing/test/poll-update-trigger.c

Purpose: verifies that an existing `POLL_ADD` request can be updated to a newly-triggering event mask and that both the update SQE and the original poll SQE complete with the expected results. The specific regression target is a poll initially armed on the pipe write end for `POLLIN`, which should not fire, then changed with `io_uring_prep_poll_update()` to `POLLOUT`, which should fire immediately.

Important APIs and types: `io_uring_queue_init`, `io_uring_get_sqe`, `io_uring_prep_poll_add`, `io_uring_prep_poll_update`, `io_uring_submit`, `io_uring_wait_cqe`, `io_uring_cqe_seen`, `struct io_uring`, `struct io_uring_sqe`, `struct io_uring_cqe`, `pipe`, and poll masks from `<poll.h>`. `IORING_POLL_UPDATE_EVENTS` is the key update mode.

Control flow: initialize a four-entry ring, create a pipe, submit the non-triggering `POLL_ADD` with `user_data = 1`, submit the poll update with `user_data = 2`, then wait for two CQEs in any order. The original request must return `POLLOUT`; the update request must return `0`.

State and persistence: only kernel poll state associated with the pending SQE persists between submissions. The test uses `user_data` as the only durable correlation state and does not clean up the ring or pipe explicitly before process exit.

Dependencies and integration: depends on liburing poll update support and pipe write readiness semantics. It integrates with the liburing test harness via `helpers.h` exit codes and skips when extra command-line arguments are supplied.

Risks and test signals: failures indicate poll-update event masks are not applied, completion ordering assumptions are wrong, or the original poll does not complete after the update. A passing run produces two CQEs with `res` values `POLLOUT` and `0`; queue setup or pipe failures are hard failures.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-update-trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll-v-poll.c -->
# sources/test-tools/liburing/test/poll-v-poll.c

Purpose: compares io_uring poll behavior against traditional `poll(2)` and `epoll_wait(2)` for pipes, regular files, and epoll file descriptors. It ensures io_uring reports readiness masks compatible with conventional readiness APIs and that `IORING_OP_EPOLL_CTL` can add an fd before polling the epoll instance.

Important APIs and types: `pthread_create`, `poll`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `io_uring_prep_poll_add`, `io_uring_prep_epoll_ctl`, `io_uring_submit`, and CQE wait/seen helpers. `struct thread_data` shares a ring, fd, event mask, and two output slots between worker threads.

Control flow: `iou_poll()` arms an io_uring poll and records `cqe->res & 0x3f`; `poll_pipe()` records `pfd.revents`; `epoll_wait_fn()` blocks on `epoll_wait`. Pipe `POLLIN` and `POLLOUT` tests start both io_uring and POSIX poll waiters, trigger readiness with a write, then compare masks. `do_test_epoll()` adds a pipe read end to an epoll fd either through `epoll_ctl` or through `io_uring_prep_epoll_ctl`, then verifies both io_uring poll and epoll waiter wake after data arrives. `do_fd_test()` compares readiness on a file opened from argv or the test binary.

State and persistence: readiness observations are transient and stored in `td.out`. The single-entry ring is shared by threads, so the test assumes serialized SQE use from its specific timing.

Dependencies and integration: requires pthreads, pipes, epoll, and liburing epoll-control support. If the io_uring epoll-control operation returns `-EINVAL`, that subcase is treated as unsupported and skipped internally.

Risks and test signals: mismatched masks between io_uring and POSIX readiness paths fail the test. Important coverage includes poll-on-epoll, both direct and io_uring-created epoll interest, and readiness of ordinary fds for `POLLIN`, `POLLOUT`, and both combined.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll-v-poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/poll.c -->
# sources/test-tools/liburing/test/poll.c

Purpose: exercises several poll corner cases: basic child-process pipe polling, multishot poll event aggregation under deferred task-run rings, polling an io_uring ring fd from another ring, and lazy poll activation for rings created disabled. It targets regressions where poll events are lost or poll wakeups get stuck.

Important APIs and types: `io_uring_prep_poll_add`, `io_uring_prep_poll_multishot`, `io_uring_enable_rings`, `io_uring_for_each_cqe`, `io_uring_peek_cqe`, `socketpair`, `setsockopt`, `fork`, and `pipe`. The setup flags `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, and `IORING_SETUP_R_DISABLED` are central.

Control flow: `test_basic()` forks; the child polls the pipe read end and validates a `POLLIN` completion after the parent writes. `test_missing_events()` uses a socketpair with constrained send buffer, submits a multishot `POLLIN|POLLOUT`, triggers both directions, drains all CQEs, and verifies the aggregate mask contains both bits. `test_self_poll()` submits many polls against `ring.ring_fd`, then posts a NOP to ensure the self-polling path makes progress. `test_disabled_ring_lazy_polling()` checks both early and late polling of a disabled defer-taskrun ring: another ring polls its `ring_fd`, the target ring is enabled, a NOP is submitted, and exactly one CQE should appear.

State and persistence: per-test rings and sockets are independent. `res_mask` accumulates multishot results. Disabled ring state persists until `io_uring_enable_rings()` and is the behavior under test.

Dependencies and integration: feature-gated by `t_probe_defer_taskrun()` for deferred task-run cases. Uses helpers for exit codes and error handling.

Risks and test signals: failures expose lost poll events, missing `POLLOUT`, stuck poll wait queues, or incorrect ring-fd readiness. Passing signals include `POLLIN` from basic pipe, both `POLLIN|POLLOUT` observed in multishot, self-poll progress after NOP, and one CQE from the lazy polling scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/pollfree.c -->
# sources/test-tools/liburing/test/pollfree.c

Purpose: stress-tests pollfree wakeups when tasks exit with outstanding signalfd reads submitted through io_uring. It repeatedly forks children that create a ring, arm multiple reads on a nonblocking `signalfd`, then exit without explicitly waiting for completions, provoking cleanup paths for poll waiters.

Important APIs and types: `signalfd`, `sigemptyset`, `sigaddset`, `io_uring_prep_read`, `IOSQE_ASYNC`, `fork`, `waitpid`, `gettimeofday`, and `mtime_since_now`. Ring setup flags tested are plain, `IORING_SETUP_SQPOLL`, `IORING_SETUP_COOP_TASKRUN`, and `IORING_SETUP_DEFER_TASKRUN|IORING_SETUP_SINGLE_ISSUER`.

Control flow: `child()` initializes a ring, creates a nonblocking signalfd for `SIGINT`, submits three reads with different `user_data`, marks the middle read `IOSQE_ASYNC`, and exits. `run_test()` forks and waits. `test()` loops for roughly 2.5 seconds per flag set, stopping early if signalfd is unavailable. `main()` runs plain mode first, then SQPOLL, cooperative task-run, and deferred task-run variants.

State and persistence: `no_signalfd` is a process-global feature flag. A static `index` in the child throttles every eighth iteration with a short sleep, increasing scheduling variety. Outstanding requests persist only until child process teardown, which is the cleanup path being exercised.

Dependencies and integration: requires Linux signalfd and io_uring support for the selected setup flags. `-EINVAL` ring setup for a mode is treated as unsupported by returning success from the child.

Risks and test signals: kernel bugs may show up as child failures, hangs, or missed cleanup wakeups. The test does not inspect CQEs; its signal is absence of failures across repeated process-exit cleanup under all supported modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/pollfree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/probe.c -->
# sources/test-tools/liburing/test/probe.c

Purpose: validates `IORING_REGISTER_PROBE` and the liburing convenience probe helper. It checks that a partial probe reports metadata without operation entries and that a full probe marks core operations as supported.

Important APIs and types: `struct io_uring_probe`, `struct io_uring_probe_op`, `io_uring_register_probe`, `io_uring_get_probe_ring`, `io_uring_free_probe`, and opcode support flags such as `IO_URING_OP_SUPPORTED`. The expected operations include `IORING_OP_NOP`, `IORING_OP_READV`, and `IORING_OP_WRITE`.

Control flow: `test_probe()` allocates enough memory for 256 probe entries, first registers with count `0`, verifies `ops_len == 0` and nonzero `last_op`, then clears the buffer and registers for 256 entries, verifying the full table. `-EINVAL` from the first registration marks probe unsupported and sets `no_probe`. `test_probe_helper()` uses `io_uring_get_probe_ring()` and runs the same full verification. `main()` initializes a ring, runs direct probe, and only runs the helper if probing is supported.

State and persistence: `no_probe` records unsupported kernel behavior. Probe buffers are heap-allocated and freed after each path. No ring state is mutated besides registration queries.

Dependencies and integration: uses liburing's probe API and helpers for allocation and exit behavior. Extra argv skips the test for harness compatibility.

Risks and test signals: failures indicate malformed probe metadata, missing support bits for fundamental operations, or helper allocation/registration breakage. Unsupported kernels skip cleanly via `-EINVAL`; supported kernels must pass both direct and helper paths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/read-before-exit.c -->
# sources/test-tools/liburing/test/read-before-exit.c

Purpose: reproduces a thread-exit race where I/O is submitted from a pthread that immediately returns. It verifies queued reads survive the submitting thread's sudden exit and that ring teardown does not trip over pending timerfd reads. The test references liburing issue 582.

Important APIs and types: `pthread_create`, `pthread_join`, `timerfd_create`, `io_uring_prep_read`, `io_uring_submit`, `io_uring_peek_cqe`, `t_create_ring_params`, and setup flags `IORING_SETUP_IOPOLL` and `IORING_SETUP_SQPOLL`. `struct data` carries the ring, two timerfds, and two read buffers into the submit thread.

Control flow: `submit()` queues two timerfd reads and expects `io_uring_submit()` to submit both. If submit does not return 2, it peeks for an `-EOPNOTSUPP` CQE and records `no_iopoll` rather than failing on kernels without submit-all-on-error behavior. `test()` creates the ring with requested flags, creates two timerfds, starts and joins the submitter, then exits the queue and closes fds. `main()` runs 1000 plain iterations, up to 1000 IOPOLL iterations unless unsupported, and 100 SQPOLL iterations.

State and persistence: thread-local submission is intentionally short lived. The ring and timerfds persist in the parent thread across submitter exit. `no_iopoll` stops repeated unsupported IOPOLL loops.

Dependencies and integration: requires pthreads and timerfd. It uses helper ring setup so unsupported setup flags can skip individual loops without failing the full test.

Risks and test signals: failures include submit counts other than expected, unsupported behavior not represented as `-EOPNOTSUPP`, or crashes during queue exit. Passing is mostly stability oriented: submitted work remains owned by the ring, not by the exiting submit thread.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/read-before-exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/read-inc-buf-more.c -->
# sources/test-tools/liburing/test/read-inc-buf-more.c

Purpose: verifies `IORING_CQE_F_BUF_MORE` is correctly set for incremental provided buffer rings (`IOU_PBUF_RING_INC`) on both pollable pipes and regular files, including EOF. It targets bugs where early buffer commit paths or zero-length EOF reads dropped the `BUF_MORE` signal even though the buffer still had remaining space.

Important APIs and types: `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `io_uring_free_buf_ring`, `io_uring_prep_read`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, `IORING_CQE_F_BUF_MORE`, and `IOU_PBUF_RING_INC`. Constants define one 256-byte buffer and 32-byte read requests.

Control flow: `do_read()` submits a selected-buffer read, waits for one CQE, rejects negative results, requires `IORING_CQE_F_BUFFER`, and requires `IORING_CQE_F_BUF_MORE`. `test_pipe()` installs one incremental buffer, writes 12 bytes to a pipe, verifies a 12-byte read with `BUF_MORE`, closes the write end, and verifies EOF with `BUF_MORE`. `test_file()` creates a temporary file with four 32-byte chunks, reads four fixed-size chunks through the same single incremental buffer, and requires `BUF_MORE` each time.

State and persistence: `no_buf_ring_inc` records unsupported incremental buffer rings. The single buffer persists and is incrementally consumed across reads, which is the state under test. Temporary files are unlinked on normal and most error paths.

Dependencies and integration: depends on buffer ring registration and selected-buffer reads. `-EINVAL` from buffer ring setup is a skip signal.

Risks and test signals: missing `BUF_MORE`, missing buffer flag, wrong read lengths, or read errors fail. Passing demonstrates both locked and early commit paths preserve incremental buffer remaining-state metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/read-inc-buf-more.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/read-inc-file.c -->
# sources/test-tools/liburing/test/read-inc-file.c

Purpose: tests regular-file reads with incremental provided buffer consumption. It specifically guards against a bug where the beginning of the incremental buffer was skipped when reading a normal file.

Important APIs and types: `io_uring_queue_init_params`, `io_uring_setup_buf_ring` with `IOU_PBUF_RING_INC`, `io_uring_buf_ring_add`, `io_uring_prep_read`, `IOSQE_BUFFER_SELECT`, and `IORING_CQE_BUFFER_SHIFT`. `BUF_BGID` and `BUF_BID` identify the single large provided buffer.

Control flow: `create_test_file()` writes eight 80-byte blocks containing repeated letters `a` through `h`. `arm_read()` submits an 80-byte selected-buffer read at a requested file offset. `main()` creates and opens the temporary file, sets up a 32-entry incremental buffer ring but publishes one 64 KiB buffer with bid 8, then issues four reads at offsets 0, 80, 160, and 240. Each completion must have a buffer flag, bid 8, result length 80, and the expected repeated character at the current buffer pointer; the local pointer then advances by `cqe->res`.

State and persistence: the kernel's incremental cursor into the single 64 KiB buffer persists across read operations. The test's `ptr` mirrors the expected cursor and checks that data is laid out sequentially from the start.

Dependencies and integration: requires incremental buffer ring support; `-EINVAL` from setup is treated as skip. Uses a temporary file named by pid and helper exit codes.

Risks and test signals: wrong bid, missing buffer flag, short read, or failure to find the expected character at the current cursor fails. Passing indicates regular-file reads consume incremental buffers from the correct initial offset.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/read-inc-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/read-mshot-empty.c -->
# sources/test-tools/liburing/test/read-mshot-empty.c

Purpose: verifies multishot reads continue draining available data even when a pipe has more bytes than one provided buffer can hold. It targets an implementation bug where multishot read stopped too early if available data exceeded buffer size.

Important APIs and types: `io_uring_setup_buf_ring`, `io_uring_prep_read_multishot`, `IORING_CQE_F_BUFFER`, `IORING_CQE_F_MORE`, buffer IDs encoded in `cqe->flags`, `pthread_create`, and pipe read/write APIs. Four 32-byte buffers are registered in a buffer ring.

Control flow: a writer thread writes two 32-byte blocks, sleeps briefly, then writes two more. The main thread creates a pipe and ring, registers four buffers, submits one `io_uring_prep_read_multishot()` on the pipe read end, checks for immediate `-EINVAL` or `-EBADF` unsupported CQE, starts the writer, and waits for four CQEs. Each CQE must be 32 bytes, have a selected buffer, and carry `IORING_CQE_F_MORE`.

State and persistence: the multishot read request persists across multiple pipe writes and multiple buffer selections. Buffer ring entries are consumed by the kernel; the test does not recycle them because exactly four buffers match the four expected completions.

Dependencies and integration: requires multishot read and buffer ring support. Unsupported operation is detected by peeking after submission and returning skip.

Risks and test signals: failures indicate early termination, missing `MORE`, missing selected buffer flag, or incorrect lengths. Passing shows one multishot read can span multiple readiness episodes and drain all four buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/read-mshot-empty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/read-mshot-stdin.c -->
# sources/test-tools/liburing/test/read-mshot-stdin.c

Purpose: provides an interactive multishot read test for stdin. It is intentionally skipped by the normal harness unless invoked with the single argument `stdin`, because it requires human or piped input and prints CQE details.

Important APIs and types: `io_uring_queue_init_params` with `IORING_SETUP_CQSIZE`, `io_uring_setup_buf_ring`, `io_uring_prep_read_multishot`, selected-buffer flags, `IORING_CQE_F_MORE`, and buffer IDs encoded in CQE flags. The ring uses one SQE and a CQ sized to 64 buffers.

Control flow: `test_stdin()` registers 64 32-byte buffers with bids 1 through 64, submits a multishot read on `STDIN_FILENO`, then loops waiting for completions. Nonzero completions must have a buffer flag. It prints result, bid, and flags, verifies positive completions use consecutive bids, and stops when `IORING_CQE_F_MORE` is absent.

State and persistence: `last_bid` tracks expected bid sequencing across completions. Buffer ring entries are consumed by stdin reads. No data content validation is attempted because input is external.

Dependencies and integration: requires buffer ring and multishot read support. Queue or buffer-ring `-EINVAL` is treated as skip. `main()` skips unless argv is exactly `stdin`.

Risks and test signals: missing buffer flags for data, non-consecutive bids, submission failures, or wait failures are test failures. Passing is an interactive signal that stdin multishot reads return buffered CQEs in expected bid order and terminate cleanly.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/read-mshot-stdin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/read-mshot.c -->
# sources/test-tools/liburing/test/read-mshot.c

Purpose: comprehensive regression coverage for `IORING_OP_READ_MULTISHOT` on pipes with provided buffers. It covers normal and async submission, first-read-ready and not-ready cases, CQ overflow, invalid fd behavior, buffer length clamping, and incremental buffer consumption across several ring setup modes.

Important APIs and types: `io_uring_prep_read_multishot`, fallback single `io_uring_prep_read`, `io_uring_setup_buf_ring`, `IOU_PBUF_RING_INC`, `IOSQE_BUFFER_SELECT`, `IOSQE_ASYNC`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_SQPOLL`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, and CQE flags `IORING_CQE_F_BUFFER` and `IORING_CQE_F_MORE`.

Control flow: `test()` configures a pipe, ring, and buffer ring, optionally writes one message before arming, then submits a multishot read and writes enough messages to consume all buffers plus one. It verifies selected buffers, message size, optional incremental content, expected `-ENOBUFS`, and expected CQ overflow termination. `test_invalid()` submits multishot read on a temporary regular file and expects a final `-EBADFD` without `MORE`. `test_clamp()` registers buffers of 16 and 32 bytes, writes alternating sizes, and expects CQE lengths to match buffer capacity. `test_inc()` uses one large incremental buffer split into 2048-byte logical consumption, repeatedly writes 31-byte chunks, rearms when needed, and verifies each bid accumulates exactly 2048 bytes across normal, SQPOLL, and defer-taskrun modes.

State and persistence: global flags remember unsupported buffer rings, multishot read, and incremental rings. Incremental tests track current bid and bytes consumed per bid. The multishot request state persists until buffer exhaustion, overflow, invalid target, or lack of `MORE`.

Dependencies and integration: depends on pipes, temporary files, liburing buffer rings, and kernel support for multishot read. Unsupported features skip subsequent dependent cases rather than failing.

Risks and test signals: failures include missing `MORE`, missing buffer flag, wrong bid, truncated messages, unexpected overflow behavior, invalid-fd result other than `-EBADFD`, or incorrect clamping. Passing gives broad evidence that read multishot and provided buffer state machines behave across synchronous, async, overflow, and incremental paths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/read-mshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/read-write.c -->
# sources/test-tools/liburing/test/read-write.c

Purpose: broad basic I/O regression test for io_uring reads and writes. It covers buffered and `O_DIRECT` file I/O, SQPOLL with registered files, fixed and cloned buffers, vectored and non-vectored operations, selected buffers, async worker offload, linked I/O, eventfd reads, resource-limit `-EFBIG`, and buffer removal.

Important APIs and types: `io_uring_prep_read`, `readv`, `read_fixed`, `write`, `writev`, `write_fixed`, `io_uring_register_files`, `t_register_buffers`, `io_uring_clone_buffers`, `io_uring_prep_provide_buffers`, `io_uring_prep_remove_buffers`, `io_uring_prep_poll_add`, `io_uring_prep_link_timeout`, `IOSQE_FIXED_FILE`, `IOSQE_ASYNC`, `IOSQE_IO_LINK`, `IOSQE_BUFFER_SELECT`, `eventfd`, `setrlimit`, and probe APIs for non-vectored read support.

Control flow: `_test_io()` opens the file in read or write mode, optionally registers buffers and files, submits `BUFFERS` I/O SQEs with sequential or random offsets, then verifies each completion length and optionally buffer-selected data contents. `__test_io()` repeats fixed-buffer cases using `io_uring_clone_buffers()` into a second ring. `main()` creates a temporary 256 KiB file, runs a matrix over write/read, buffered/direct, SQPOLL, fixed buffers, async offload, and non-vectored operations, then runs buffer-selection, pipe selected-buffer, eventfd, linked write-poll-timeout, large linked async write chains, `RLIMIT_FSIZE` `-EFBIG`, buffer removal batch/single, and nonaligned fixed-buffer cases.

State and persistence: global `vecs` hold test buffers; global flags suppress unsupported nonvec, buffer-select, or buffer-clone paths after detection. Registered files and buffers persist per ring until explicitly unregistered. Temporary test file persists across the matrix and is unlinked at the end when internally created.

Dependencies and integration: uses helper buffer/file creation and liburing probe helpers. Some subcases skip on permissions, unsupported operations, missing huge functionality, or non-root for the `EFBIG` test.

Risks and test signals: this file has high blast radius. Failures point to core read/write completion sizing, fixed-file indexing, fixed-buffer registration/clone, selected-buffer data placement, linked operation progress, resource-limit propagation, or buffer removal semantics. Passing means a large cross-product of basic I/O modes agrees with expected lengths and data.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/read-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recv-bundle-buf-len.c -->
# sources/test-tools/liburing/test/recv-bundle-buf-len.c

Purpose: validates that non-incremental provided buffer descriptors are not persistently corrupted by receive bundle operations that trim the head buffer or fail before consuming data. It targets regressions where a bundle recv shrank `buf->len` and poisoned later operations.

Important APIs and types: `io_uring_prep_recv`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_mask`, `IORING_FEAT_RECVSEND_BUNDLE`, socketpair, pipe, and CQE buffer-id extraction.

Control flow: `setup()` initializes a ring, verifies bundle feature support, allocates two 4096-byte buffers, registers a non-incremental buffer ring, and publishes both entries. `test_eagain_no_corrupt()` submits a bundle recv with `MSG_DONTWAIT` and `len=1` on an empty datagram socket, expects `-EAGAIN`, verifies `t.br->bufs[0].len` is still 4096, then performs a selected-buffer pipe read that must consume all 4096 bytes using bid 0. `test_success_trim()` writes 64 bytes to a stream socket, submits a bundle recv with `SHORT_LEN` 32, expects `res == 32`, bid 0, and matching payload.

State and persistence: the raw buffer ring descriptor length is explicitly inspected after a failed recv. Buffer group state is reused by a later unrelated read in the first case to prove user-visible behavior is intact.

Dependencies and integration: requires kernel receive/send bundle feature and buffer rings; unsupported paths set `no_bundle` or `no_buf_ring` and skip. Uses helper exit codes.

Risks and test signals: corrupted descriptor length, wrong completion result, missing buffer flag, wrong bid, or data mismatch fail. Passing shows failed and successful bundle trims do not damage buffer-ring descriptor state beyond intended consumption.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recv-bundle-buf-len.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recv-bundle-short-ooo.c -->
# sources/test-tools/liburing/test/recv-bundle-short-ooo.c

Purpose: tests multishot receive with bundle support and a small non-incremental buffer ring, verifying that data from a large TCP stream is received in byte order even when completions can cover multiple bundled buffers. It is based on a regression around receive bundle ordering.

Important APIs and types: `io_uring_register_buf_ring`, manually mapped `struct io_uring_buf_ring`, `io_uring_prep_recv_multishot`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_MORE`, socket-pair helper, and CQE buffer ID extraction. `struct buf_ring_data` tracks mapped ring memory and backing buffer memory.

Control flow: `setup_buf_ring()` mmap-allocates four 1024-byte buffers and a separate ring, registers bgid 0, fills the ring, and advances it. The test creates a connected stream socket pair, fills a 1 MiB pattern buffer, writes all bytes to the sender, closes sender, then submits four multishot receive SQEs with bundle and buffer selection. The completion loop processes CQEs until 1 MiB has been received or a poll-count cap is hit. `process_completion()` may split one CQE across several 1024-byte logical buffers, verifies each segment against the expected pointer, recycles buffers, and advances the expected cursor.

State and persistence: global `data_received` accumulates received bytes across completions. Buffer IDs and ring entries are recycled manually after each bundled segment. The expected-data pointer persists through the receive loop.

Dependencies and integration: runs under normal, defer-taskrun, SQPOLL, and cooperative task-run modes. Unsupported buffer ring or recv multishot support sets skip flags.

Risks and test signals: ordering mismatches, unexpected negative CQEs, incomplete 1 MiB transfer, or missing support handling fail. Passing demonstrates receive bundles preserve stream ordering while recycling a small buffer ring.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recv-bundle-short-ooo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recv-inc-ooo.c -->
# sources/test-tools/liburing/test/recv-inc-ooo.c

Purpose: verifies ordering for multishot receive with receive bundles and incrementally consumed provided buffers. It targets a reported issue where incremental buffer consumption could place received data out of order.

Important APIs and types: `io_uring_register_buf_ring` with `IOU_PBUF_RING_INC`, `io_uring_prep_recv_multishot`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, mmap-backed buffer memory, socket-pair helper, and ring setup flags for defer-taskrun, SQPOLL, and cooperative task-run.

Control flow: `setup_buf_ring()` maps a four-entry 1024-byte buffer area, registers it as an incremental buffer ring, and publishes all entries. `test_recv_incr()` creates a stream socket pair, submits one bundled multishot recv, then writes 2 KiB of patterned data in deliberately uneven chunks: 512, 333, 777, and 426 bytes. For each chunk, it waits until the whole chunk has been received. `process_completion()` checks each CQE result, validates the bytes at the current incremental cursor, and advances `rb.cursor` by `cqe->res`.

State and persistence: `struct read_buf` tracks the user-space view of the incremental consumption cursor. `data_received` is local to the test. The kernel's incremental buffer tail persists across all completions and is checked by reading from `buffer_memory + cursor`.

Dependencies and integration: requires buffer-ring incremental support and recv multishot. Unsupported `-EINVAL` marks skip. The same scenario is run under several ring setup modes after the baseline succeeds.

Risks and test signals: failures indicate data ordering corruption, incorrect incremental cursor advancement, unsupported feature handling regressions, or incomplete receive. Passing shows uneven stream chunks are laid out sequentially in the incremental buffer across bundled multishot completions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recv-inc-ooo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recv-msgall-stream.c -->
# sources/test-tools/liburing/test/recv-msgall-stream.c

Purpose: verifies `MSG_WAITALL` behavior for stream sockets for both `recv` and `recvmsg`, comparing io_uring operations with synchronous system calls. The sender splits one logical message into two sends; the receiver must still obtain the full requested length.

Important APIs and types: `io_uring_prep_recv`, `io_uring_prep_recvmsg`, `io_uring_prep_send`, `MSG_WAITALL`, `pthread_mutex_t`, TCP socket/listen/accept/connect, `t_bind_ephemeral_port`, and `struct msghdr`/`struct iovec`.

Control flow: receiver setup binds an ephemeral localhost TCP port and unlocks a mutex to let the sender connect. `recv_prep()` accepts a connection, submits either `recv` or `recvmsg` with `MSG_WAITALL`, and returns the accepted fd. `do_send()` connects and sends the integer buffer as two half-size io_uring sends separated by a short sleep. `do_recv()` waits for the single receive CQE and requires the full `MAX_MSG * sizeof(int)` result. `recv_sync()` performs the same wait-all receive using synchronous `recv` or `recvmsg`. `test()` runs four combinations: io_uring recv, io_uring recvmsg, sync recv, and sync recvmsg.

State and persistence: `struct recv_data` carries synchronization state, selected receive API, and port. The receive buffer is stack-local and validated after completion for the 0..127 integer pattern.

Dependencies and integration: uses TCP loopback, pthreads, and liburing send/recv support. `-EINVAL` for io_uring receive or send is treated as unsupported skip within that path.

Risks and test signals: partial reads, content mismatch, socket synchronization bugs, or unsupported operations not handled as skips fail. Passing confirms io_uring stream `MSG_WAITALL` waits across multiple sends like synchronous APIs.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recv-msgall-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recv-msgall.c -->
# sources/test-tools/liburing/test/recv-msgall.c

Purpose: checks `MSG_WAITALL` on datagram sockets for `recv` and `recvmsg`. It documents and enforces datagram semantics: even with `MSG_WAITALL` and two sends, one receive should complete with one datagram, here half of the full integer buffer.

Important APIs and types: UDP socket bind/connect, `io_uring_prep_recv`, `io_uring_prep_recvmsg`, `io_uring_prep_send`, `MSG_WAITALL`, `pthread_barrier_t`, `t_bind_ephemeral_port`, and `struct msghdr`.

Control flow: `recv_fn()` creates a ring and UDP socket, binds an ephemeral port, submits one wait-all receive or recvmsg, then releases the sender through a barrier. `do_send()` connects a UDP socket to that port and submits two io_uring sends, each for half the buffer, with a sleep between submissions. `do_recv()` waits for the receive CQE and requires `MAX_MSG * sizeof(int) / 2`, because one datagram is delivered per receive. `test()` runs recv and recvmsg variants.

State and persistence: global `bind_port` communicates the receiver's ephemeral port to the sender after the barrier. `struct recv_data` stores the barrier, `use_recvmsg`, and persistent `msghdr` for recvmsg validation lifetime.

Dependencies and integration: uses UDP loopback and pthread barriers. `-EINVAL` for recv or send is treated as unsupported.

Risks and test signals: receiving the full two-send size would violate the expected datagram behavior for this test, while shorter or negative results indicate recv bugs. Passing shows io_uring preserves datagram message boundaries with `MSG_WAITALL`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recv-msgall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recv-mshot-drain.c -->
# sources/test-tools/liburing/test/recv-mshot-drain.c

Purpose: stress-tests multishot recv when the provided buffer ring is intentionally exhausted and refilled while data is actively arriving. It verifies that `-ENOBUFS` and missing `IORING_CQE_F_MORE` can be handled by refilling and rearming without data loss.

Important APIs and types: `io_uring_setup_buf_ring`, `io_uring_prep_recv_multishot`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, `IORING_CQE_F_MORE`, `io_uring_wait_cqe_timeout`, TCP loopback sockets, and pthread barriers.

Control flow: the receiver creates a four-entry 128-byte buffer ring, starts a sender thread, accepts a TCP connection, submits one multishot recv, and loops on CQEs with a two-second timeout. The sender transmits 4096 chunks of 64 bytes, with brief pacing. On `-ENOBUFS`, the receiver refills all four buffers and rearms. On normal data, it counts bytes, returns the selected buffer to the ring, and if `MORE` is absent while bytes remain, rearms the multishot request. EOF or timeout ends the loop. Final `total_recv` must equal `NR_SENDS * SEND_SIZE`.

State and persistence: `total_recv` accumulates bytes across multiple multishot lifetimes. The same buffer backing memory is recycled after each CQE. `thread_data` carries listener port synchronization to the sender.

Dependencies and integration: requires buffer rings and multishot recv; `-EINVAL` or `-ENOENT` during buffer ring setup skips. Uses TCP loopback and pthreads.

Risks and test signals: data loss, failure to rearm after exhaustion, mishandled `-ENOBUFS`, or byte-count mismatch fail. Passing shows buffer starvation is recoverable and multishot recv can be drained/refilled under sustained traffic.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recv-mshot-drain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recv-mshot-fair.c -->
# sources/test-tools/liburing/test/recv-mshot-fair.c

Purpose: tests fairness across multiple simultaneous multishot receive streams and validates the `optlen` byte limit for terminating a multishot request. It covers receive bundles and non-bundled multishot receive under defer-taskrun and cooperative task-run modes.

Important APIs and types: `io_uring_prep_recv_multishot`, SQE `optlen`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, `io_uring_setup_buf_ring`, pthread barriers, TCP loopback sockets, and CQE user data pointing to `struct recv_data`.

Control flow: `test()` prepares four receiver contexts on adjacent ports, starts one receiver thread that creates a CQ-sized ring and a 2048-entry buffer ring, and then runs four senders sequentially. `recv_prep()` binds/listens/accepts each connection, synchronizes with its sender, and arms a multishot receive. `do_recv()` waits for CQEs, attributes them to stream contexts via `io_uring_cqe_get_data()`, decrements remaining bytes, rearms when `MORE` is absent, and records unfairness if too many bytes arrive from one stream before switching. When `mshot_limit` is enabled, bytes since arm must not exceed `PER_MSHOT_LIMIT`. `run_tests()` executes bundled and non-bundled cases with and without the limit under defer and coop modes.

State and persistence: each `recv_data` records bytes remaining, bytes since arm, total bytes, unfair counters, and limit overshoot counters. Static `last_rd` and `bytes_since_last` track cross-stream scheduling fairness across CQEs.

Dependencies and integration: requires multishot iteration support, buffer rings, TCP loopback, and optionally `optlen` limit support. Unsupported iteration or limit support returns skip or pass depending on which feature is missing.

Risks and test signals: unfair scheduling, byte-limit overshoot, negative CQEs, missing buffer flags, or rearm failures fail. Passing indicates multishot receive does not monopolize one stream and honors per-request byte caps where supported.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recv-mshot-fair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recv-multishot.c -->
# sources/test-tools/liburing/test/recv-multishot.c

Purpose: comprehensive multishot recv and recvmsg validation across stream/datagram sockets, wait-each versus batched waits, deferred task-run, and early-error scenarios. It also validates liburing recvmsg output parsing helpers and explicit `-ENOBUFS` behavior.

Important APIs and types: `io_uring_prep_recv_multishot`, `io_uring_prep_recvmsg_multishot`, `io_uring_prep_provide_buffers`, `io_uring_prep_cancel64`, `io_uring_recvmsg_validate`, `io_uring_recvmsg_payload`, `io_uring_recvmsg_payload_length`, `io_uring_recvmsg_name`, `io_uring_recvmsg_cmsg_firsthdr`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_MORE`, `IORING_CQE_F_BUFFER`, and socket helpers.

Control flow: `test_recvmsg_validate()` first checks helper bounds handling. The main nested loop runs 16 combinations of stream/datagram, wait strategy, recv versus recvmsg, and defer mode, and for each combination runs early-error modes: none, not enough buffers, early sender close, early receiver cancel, and CQ overflow. `test()` provides buffers of alternating sizes, submits one multishot receive, sends progressively larger integer payloads, optionally triggers an early condition, collects CQEs, and validates final/non-final flags, selected buffer presence, payload order, recvmsg name/control metadata for datagrams, truncation accounting, and expected errors. `test_enobuf()` separately proves that two buffers followed by three datagrams produce two data CQEs and a final `-ENOBUFS` CQE without buffer or more flags.

State and persistence: arrays keep sent buffer pointers, allocated receive buffers, and copied CQEs for later validation. Totals track sent, received, and truncated bytes. `user_data` distinguishes provide-buffer, receive, and cancel operations.

Dependencies and integration: requires multishot receive support; initial unsupported behavior returns `T_EXIT_SKIP`. Defer mode is gated by `t_probe_defer_taskrun()`.

Risks and test signals: this is a high-value protocol-state test. Failures catch wrong final `MORE`, missing buffer flags, invalid recvmsg layout, address/control corruption, dropped bytes without truncation accounting, incorrect early errors, or malformed `-ENOBUFS`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recv-multishot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recvmsg-inc-tail.c -->
# sources/test-tools/liburing/test/recvmsg-inc-tail.c

Purpose: verifies `recvmsg` multishot with incremental provided buffers retires a too-small buffer tail instead of returning spurious `-EFAULT`. It targets the case where the remaining tail is smaller than the header area needed for `struct io_uring_recvmsg_out` plus address/control metadata.

Important APIs and types: `io_uring_register_buf_ring` with `IOU_PBUF_RING_INC`, `io_uring_buf_reg.min_left`, `io_uring_prep_recvmsg_multishot`, `io_uring_recvmsg_validate`, `io_uring_recvmsg_payload`, `io_uring_recvmsg_payload_length`, `IOSQE_BUFFER_SELECT`, and stream socket pairs.

Control flow: `setup_buf_ring()` maps four 1024-byte buffers and a buffer ring, sets `min_left = 32`, registers bgid 1 as incremental, and publishes four entries. `test()` submits one recvmsg multishot on a stream socket, then writes two 480-byte payloads and seven 305-byte payloads. The payload sizes are chosen so bid 0 is consumed exactly by two large CQEs, while three small CQEs leave a 13-byte tail in bids 1 and 2, forcing retire-to-next-buffer behavior. Each CQE must succeed, include a buffer id matching the expected bid sequence `{0,0,1,1,1,2,2,2,3}`, validate as recvmsg output, have zero controllen, and match the stream payload at the expected cursor.

State and persistence: `bid_offset[]` tracks consumed bytes within each incremental buffer for validating in-buffer layout. `stream_cursor` and `sent_offset` track expected payload ordering.

Dependencies and integration: requires incremental buffer rings and recvmsg multishot; `-EINVAL` or `-ENOTSUP` skips. Uses mmap-backed buffers and helper-created stream socket pairs.

Risks and test signals: a negative CQE, wrong bid transition, invalid recvmsg layout, payload mismatch, or too few distinct bids fails. Passing proves tail retirement avoids bad-address failures and preserves payload placement.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recvmsg-inc-tail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recvsend_bundle-inc.c -->
# sources/test-tools/liburing/test/recvsend_bundle-inc.c

Purpose: tests send and receive bundle behavior with incremental receive buffer rings over TCP. It verifies sequence ordering while using a single large incremental receive buffer and optionally send bundles, receive bundles, or both.

Important APIs and types: `io_uring_prep_send_bundle`, `io_uring_prep_send`, `io_uring_prep_recv_multishot`, `IORING_RECVSEND_BUNDLE`, `IOU_PBUF_RING_INC`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUF_MORE`, `IORING_CQE_F_MORE`, pthread barriers, and TCP loopback sockets. This file includes `<liburing.h>` directly and defines local `T_EXIT_*` values.

Control flow: the receiver thread creates a CQ-sized ring, registers one huge incremental buffer covering `RECV_BIDS * MSG_SIZE`, accepts a TCP connection, arms multishot recv, and validates received sequence numbers. The sender creates a send buffer ring with `nr_msgs` 128-byte messages containing monotonic `unsigned long` sequences, optionally fills the socket toward `EAGAIN`, then sends either with `io_uring_prep_send_bundle()` or individual selected-buffer sends. `run_tests()` starts with four messages and covers no bundle, recv bundle, both bundles, full socket, almost full socket, and send-only bundle. It then repeats selected almost-full cases with 32 messages.

State and persistence: `recv_data.seq` is the expected sequence counter. `recv_bytes` is increased by backlog sends and bundle sends. `verify_sz` accumulates partial pieces until it has whole 128-byte messages to validate. The incremental receive ring must keep returning bid 0 with `IORING_CQE_F_BUF_MORE`.

Dependencies and integration: requires `IORING_FEAT_RECVSEND_BUNDLE` and incremental buffer ring support, checked through setup and `has_pbuf_ring_inc()`. Unsupported send bundle sets `no_send_mshot` and skips.

Risks and test signals: missing `BUF_MORE`, bid other than 0, sequence mismatch, bad send CQEs, or incomplete byte accounting fail. Passing demonstrates bundle sends and bundled multishot receives interoperate with incremental buffers under socket pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recvsend_bundle-inc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/recvsend_bundle.c -->
# sources/test-tools/liburing/test/recvsend_bundle.c

Purpose: tests send and receive bundles with normal provided buffer rings and classic provided buffers over both TCP and UDP. It validates buffer-id ordering, sequence integrity, bundle re-submission, and behavior when the socket send queue is full or almost full.

Important APIs and types: `io_uring_prep_send_bundle`, `io_uring_prep_send`, `io_uring_prep_recv_multishot`, `io_uring_setup_buf_ring`, `io_uring_prep_provide_buffers`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, `IORING_FEAT_RECVSEND_BUNDLE`, TCP/UDP sockets, and pthread barriers.

Control flow: `recv_fn()` creates the receive ring, registers either a buffer ring with `RECV_BIDS` 128-byte entries or classic buffers, binds/listens or binds UDP, accepts/uses the socket, arms multishot recv, and validates completions. `do_recv()` checks selected bid equals the next expected bid, validates sequence data in message-sized chunks, advances expected bid based on bytes received, and rearms recv when `MORE` is absent before all expected bytes arrive. `do_send()` registers send buffers, optionally fills the socket send queue with nonblocking sends, populates bundle payloads with sequence numbers, then uses bundled or individual selected-buffer sends. `run_tests()` covers baseline, recv bundle, both bundles, full socket, almost-full socket, and larger-than-fast-iov segment counts. `main()` runs TCP and UDP with buffer rings, then TCP and UDP with classic provided buffers.

State and persistence: global `use_tcp`, `classic_buffers`, `nr_msgs`, and `use_port` select matrix state. `recv_data` carries synchronization, expected sequence, remaining bytes, and flags for send/recv bundle. Buffer IDs persist as ordering evidence.

Dependencies and integration: requires receive/send bundle feature for bundle cases. UDP skips backlog pressure cases because they are not reliable. Unsupported bundle marks `no_send_mshot` and produces a skip after joining the receiver.

Risks and test signals: wrong bid sequencing, oversized non-bundled receive, sequence mismatch, bad send results, or deadlock across barriers fail. Passing gives cross-protocol evidence that bundled send/recv works with both buffer ring styles and handles socket pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/recvsend_bundle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/reg-fd-only.c -->
# sources/test-tools/liburing/test/reg-fd-only.c

Purpose: tests rings created with `IORING_SETUP_REGISTERED_FD_ONLY | IORING_SETUP_NO_MMAP`. It verifies that already-registered ring fds behave correctly, that closing the ring fd still permits register operations through the registered-ring path, and that the ring remains usable for NOP submissions.

Important APIs and types: `io_uring_queue_init`, `io_uring_register_ring_fd`, `io_uring_close_ring_fd`, `io_uring_register_iowq_max_workers`, `io_uring_prep_nop`, `io_uring_submit`, and `io_uring_wait_cqe`. It tests normal-page and huge-page-sized entry counts plus SQPOLL.

Control flow: `test()` creates a registered-fd-only/no-mmap ring with optional SQPOLL, expects `io_uring_register_ring_fd()` to fail with `-EEXIST`, expects `io_uring_close_ring_fd()` to fail with `-EBADF` because the fd is already closed, then calls `io_uring_register_iowq_max_workers()` and requires nonzero returned worker limits. `test_nops()` submits and drains four ring-depths worth of NOPs in batches no larger than the SQ size. `main()` runs 8-entry normal, 8-entry SQPOLL, and 512-entry huge-page cases, skipping on unsupported no-mmap/registered-fd-only or huge page memory limits.

State and persistence: ring fd registration state is the primary persistent state. The test intentionally uses a ring whose normal fd is closed by setup semantics, then relies on the registered fd for further operations.

Dependencies and integration: requires registered-fd-only and no-mmap support; `-EINVAL` or `-ENOENT` marks unsupported. Huge-page-sized rings may skip with `-ENOMEM`.

Risks and test signals: incorrect `-EEXIST`/`-EBADF`, failed register after close, or inability to submit NOPs indicates registered-ring lifecycle regressions. Passing proves registered-fd-only rings remain operational without a regular ring fd.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/reg-fd-only.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/reg-hint.c -->
# sources/test-tools/liburing/test/reg-hint.c

Purpose: verifies direct descriptor allocation fails safely after unregistering the sparse file table. It targets stale allocation-hint state after `io_uring_unregister_files()`.

Important APIs and types: `io_uring_register_files_sparse`, `io_uring_unregister_files`, `io_uring_prep_socket_direct_alloc`, `io_uring_submit`, `io_uring_wait_cqe`, and socket constants `AF_UNIX`/`SOCK_DGRAM`.

Control flow: `main()` initializes a one-entry ring, registers a sparse file table with 16 slots, unregisters it, then submits `io_uring_prep_socket_direct_alloc()` to allocate an `AF_UNIX` datagram socket into a direct descriptor slot. Since no file table is registered anymore, the CQE must complete with `-ENFILE`.

State and persistence: the sparse file table registration is intentionally removed before the socket-direct allocation. The test checks that no stale table or hint persists in a way that allows allocation or crashes.

Dependencies and integration: requires sparse file table registration and socket-direct allocation. `-EINVAL` from sparse file registration is treated as feature unsupported and skipped.

Risks and test signals: any CQE result other than `-ENFILE` is a failure. Passing demonstrates direct allocation correctly sees the absence of a registered file table after unregister.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/reg-hint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/reg-reg-ring.c -->
# sources/test-tools/liburing/test/reg-reg-ring.c

Purpose: tests `IORING_REGISTER_USE_REGISTERED_RING` behavior for a ring fd explicitly registered with the kernel. It verifies registration, duplicate registration, close semantics, and continued register operations after closing the normal ring fd.

Important APIs and types: `io_uring_queue_init`, ring feature bit `IORING_FEAT_REG_REG_RING`, `io_uring_register_ring_fd`, `io_uring_unregister_ring_fd`, `io_uring_close_ring_fd`, and `io_uring_register_iowq_max_workers`.

Control flow: `main()` initializes a ring and skips if `IORING_FEAT_REG_REG_RING` is absent. Before registration, `io_uring_close_ring_fd()` and `io_uring_unregister_ring_fd()` must return `-EINVAL`. Registering must return `1`; duplicate registering must return `-EEXIST`. A normal register operation (`io_uring_register_iowq_max_workers`) must work before closing the ring fd. Closing must return `1`; the same register operation must still work after close through the registered-ring path. A second close must return `-EBADF`.

State and persistence: ring fd registration status transitions from unregistered to registered to closed-normal-fd while retaining registered-ring usability. Worker limit values are used as proof of register-call execution.

Dependencies and integration: feature-gated by `IORING_FEAT_REG_REG_RING`. Uses helpers for standard exit codes.

Risks and test signals: wrong lifecycle return codes or inability to register after close indicate registered-ring fd regressions. Passing confirms liburing can operate register opcodes on registered rings after closing the original fd.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/reg-reg-ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/reg-wait.c -->
# sources/test-tools/liburing/test/reg-wait.c

Purpose: validates registered wait argument memory regions for `io_uring_submit_and_wait_reg()` and direct `io_uring_enter2` registered wait offsets. It exercises user-provided regions, kernel-allocated regions, disabled-ring requirements, signal mask validation, bounds checks, huge page cases, and mapping types.

Important APIs and types: `struct io_uring_reg_wait`, `struct io_uring_region_desc`, `struct io_uring_mem_region_reg`, `IORING_MEM_REGION_REG_WAIT_ARG`, `IORING_MEM_REGION_TYPE_USER`, `IORING_REG_WAIT_TS`, `IORING_ENTER_EXT_ARG_REG`, `io_uring_register_region`, `io_uring_submit_and_wait_reg`, `io_uring_enable_rings`, `__sys_io_uring_enter2`, and mmap flags including huge pages.

Control flow: `test_regions()` verifies registration only succeeds on disabled rings, rejects null, zero-size, misaligned, bogus, read-only, and invalid kernel/user combinations, and records whether kernel-allocated regions are supported. `test_wait_arg()` registers one page of user memory as wait args, enables the ring, then runs `test_basic()` for timeout duration, `test_invalid_sig()` for bad sigmask size/address, and `test_offsets()` for first, last, one-past-end, overflow, and unaligned offsets. `test_region_buffer_types()` repeats offset checks over user memory, huge pages where available, and kernel-created regions of several sizes.

State and persistence: global `page_size` and `reg` define the active wait-argument memory. Registered memory persists across waits until ring exit. `struct t_region` tracks whether memory is user or kernel mapped and its size.

Dependencies and integration: requires registered memory-region support; unsupported region registration skips. Huge-page cases tolerate `-ENOMEM` and `-EINVAL`. Direct syscall wrapper is used for offset tests not exposed by the high-level helper.

Risks and test signals: wrong timeout duration, invalid signal handling, accepting out-of-bounds offsets, or registration accepting invalid memory all fail. Passing proves registered wait arguments are safely bounded and work across memory backends.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/reg-wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/regbuf-clone.c -->
# sources/test-tools/liburing/test/regbuf-clone.c

Purpose: tests fixed-buffer cloning between rings, including registered-ring variants, unregister behavior, dummy buffers, huge-page merge behavior, offset cloning, sparse destination tables, replacement semantics, and cloning within the same ring.

Important APIs and types: `io_uring_register_buffers`, `io_uring_register_buffers_sparse`, `io_uring_clone_buffers`, `io_uring_clone_buffers_offset`, `io_uring_unregister_buffers`, `io_uring_register_buffers_update_tag`, `IORING_REGISTER_DST_REPLACE`, `io_uring_register_ring_fd`, fixed reads via `io_uring_prep_read_fixed`, and huge-page mmap flags.

Control flow: `use_buf()` performs a fixed read from a pipe into a registered buffer index and returns the CQE result, serving as a behavioral probe for whether a buffer table entry is usable. `test()` runs source/destination rings with optional registered ring fds, verifies cloning from an empty source returns `-ENXIO`, registers 64 buffers in the source, verifies destination has no buffers, clones all buffers, checks `-EBUSY` on duplicate clone, unregisters and verifies `-EFAULT`, clones in reverse, and checks double-unregister errors. `test_offsets()` checks offset overflow, too many buffers, partial clone, replacement, sparse table replacement/expansion, and usability at expected indices. `test_dummy()` clones a zero-length dummy buffer. `test_merge()` tries updating sparse entries with adjacent huge-page slices. `test_same()` clones/replaces buffers within the same ring.

State and persistence: registered buffer tables persist in each ring and are repeatedly cloned, replaced, expanded, and unregistered. Global flags record unsupported clone and offset-clone support.

Dependencies and integration: requires fixed buffers, clone APIs, and optionally huge pages. `-EINVAL` and `-ENOMEM` are feature/resource skip paths in selected cases.

Risks and test signals: incorrect error codes (`-ENXIO`, `-EBUSY`, `-EOVERFLOW`, `-EFAULT`), unusable cloned buffers, stale buffers after unregister, or wrong replacement behavior fail. Passing provides strong coverage of buffer table ownership and clone lifecycle rules.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/regbuf-clone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/regbuf-merge.c -->
# sources/test-tools/liburing/test/regbuf-merge.c

Purpose: syzkaller-derived regression reproducer for buffer registration/merge behavior through raw syscalls and fixed mappings. It is disabled under sanitizer builds because it relies on fixed virtual addresses and low-level memory manipulation.

Important APIs and types: raw `io_uring_setup` and `io_uring_register` syscalls, manual `mmap` of SQ/CQ rings and SQEs, `struct io_uring_params`, `IORING_OFF_SQ_RING`, `IORING_OFF_SQES`, and hard-coded ring offset constants. `syz_io_uring_setup()` wraps setup and maps rings at supplied addresses.

Control flow: when sanitizers are not enabled, `main()` maps guard and data regions at syzkaller-style fixed addresses, writes a crafted `io_uring_params` structure, calls `syz_io_uring_setup()` with 0x2fd6 entries and fixed mapping addresses, stores the returned fd if setup succeeded, writes a small registration descriptor at another fixed address, and invokes `io_uring_register` opcode 0 with two entries. The program returns pass as long as it does not crash.

State and persistence: global `r[0]` stores the ring fd or all-ones fallback. All interesting state is laid out in fixed virtual memory, mirroring a minimized fuzz reproducer rather than normal liburing abstractions.

Dependencies and integration: depends on architecture/syscall numbers and Linux io_uring mmap ABI. Under `CONFIG_USE_SANITIZER`, `main()` skips to avoid sanitizer conflicts with fixed mappings.

Risks and test signals: this is a crash regression test, not a semantic assertion test. Passing means the kernel tolerates the crafted setup/register sequence without process-visible failure; crashes or fatal signals indicate memory-management regressions in buffer registration paths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/regbuf-merge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/register-restrictions.c -->
# sources/test-tools/liburing/test/register-restrictions.c

Purpose: validates io_uring restriction registration on disabled rings. It tests allowed SQE opcodes, allowed register opcodes, required fixed-file flags, allowed/required SQE flags, empty restriction sets, and rejection of restriction registration or submission in invalid ring states.

Important APIs and types: `struct io_uring_restriction`, restriction opcodes `IORING_RESTRICTION_SQE_OP`, `IORING_RESTRICTION_REGISTER_OP`, `IORING_RESTRICTION_SQE_FLAGS_ALLOWED`, `IORING_RESTRICTION_SQE_FLAGS_REQUIRED`, `io_uring_register_restrictions`, `io_uring_enable_rings`, `IORING_SETUP_R_DISABLED`, `IOSQE_FIXED_FILE`, `IOSQE_ASYNC`, `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, file registration, and read/writev SQEs.

Control flow: `test_restrictions_sqe_op()` allows `WRITEV` and `WRITE`, then verifies `WRITEV` succeeds and `READV` gets `-EACCES`. `test_restrictions_register_op()` allows only buffer registration and requires file registration to fail. `test_restrictions_fixed_file()` allows read/writev plus file registration and requires `IOSQE_FIXED_FILE`; fixed-file read/write succeed while non-fixed write fails. `test_restrictions_flags()` permits only fixed-file SQEs with optional ASYNC or IO_LINK; IO_DRAIN, ASYNC without fixed file, and no flags fail. `test_restrictions_empty()` registers zero restrictions, causing all tested register and SQE operations to be denied. `test_restrictions_rings_not_disabled()` requires restriction registration on an enabled ring to return `-EBADFD`; `test_restrictions_rings_disabled()` requires submission before enabling to return `-EBADFD`.

State and persistence: each test owns a fresh ring and pipe. Restrictions persist after registration and before/after enabling, defining the authorization policy for later operations.

Dependencies and integration: restriction support may be absent and is skipped on `-EINVAL`. Tests depend on disabled-ring setup and pipe I/O.

Risks and test signals: wrong `-EACCES` or `-EBADFD` behavior, allowed disallowed operations, denied allowed operations, or enable failures indicate security-policy regressions. Passing confirms restrictions are enforced consistently for SQEs, flags, and register operations.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/register-restrictions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/rename.c -->
# sources/test-tools/liburing/test/rename.c

Purpose: tests the io_uring rename operation for successful path replacement and error propagation for nonexistent paths and bad user pointers.

Important APIs and types: `io_uring_prep_rename`, `io_uring_submit`, `io_uring_wait_cqe`, `mkstemp`, `stat`, `unlink`, and standard errno results `ENOENT` and `EFAULT`. The file manually clears SQEs with `memset()` before preparation.

Control flow: `main()` creates two temporary files in the current directory and verifies both exist. `test_rename()` submits a rename from source to destination and returns the CQE result. If the first rename returns `-EBADF` or `-EINVAL`, rename support is treated as unavailable and the test skips the rest. Otherwise, the source must disappear and destination must exist. It then submits a rename for two invalid absolute paths and requires `-ENOENT`. Finally, `test_rename_badaddr()` submits one case with an invalid new path pointer and one with an invalid old path pointer, both expected to return `-EFAULT`.

State and persistence: filesystem state is persistent across calls: the first successful rename removes `src` and replaces `dst`. Cleanup unlinks `dst` on success/skip and both names on error.

Dependencies and integration: requires kernel support for `IORING_OP_RENAME` and a writable current directory. Extra argv exits success for harness behavior.

Risks and test signals: failures indicate rename support returns wrong errors, bad pointers are not rejected safely, or filesystem state after rename is wrong. Passing confirms successful operation and key error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/resize-mmap-fail.c -->
# sources/test-tools/liburing/test/resize-mmap-fail.c

Purpose: verifies ring resize failure handling when the new mmap cannot be created. The expected behavior is that `io_uring_resize_rings()` fails and the original ring remains valid and usable.

Important APIs and types: `io_uring_queue_init`, `io_uring_resize_rings`, `io_uring_prep_nop`, `io_uring_submit_and_wait`, `io_uring_peek_cqe`, `getrlimit`, `setrlimit`, `RLIMIT_AS`, `/proc/self/statm`, and `sysconf(_SC_PAGESIZE)`.

Control flow: `main()` initializes a small eight-entry ring and proves it works by submitting and completing a NOP. It reads current virtual memory size in pages, saves `RLIMIT_AS`, then sets a tight address-space limit to current usage plus two pages. It requests a resize to 64 SQ entries and 128 CQ entries, expecting failure due to mmap memory pressure. It restores the old limit immediately, requires a negative resize result, then submits and completes another NOP on the original ring.

State and persistence: the old ring mapping and ring bookkeeping must persist unchanged after failed resize. The process address-space limit is temporarily mutated and then restored before further checks.

Dependencies and integration: depends on `/proc/self/statm`, resource limits, and ring resize support. Inability to inspect VM size or page size skips; setup and resource-limit failures fail.

Risks and test signals: resize unexpectedly succeeding under the forced limit, inability to get an SQE after failure, submit failure, or missing completion after failure all indicate rollback bugs. Passing proves failed resize does not leave the ring broken.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/resize-mmap-fail.c -->
