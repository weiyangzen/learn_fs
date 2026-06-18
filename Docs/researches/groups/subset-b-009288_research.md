# subset-b-009288 research

Grouped research report for liburing tests in `sources/test-tools/liburing/test`. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/resize-rings.c -->
# sources/test-tools/liburing/test/resize-rings.c

Purpose: stress-tests `io_uring_resize_rings()` across normal, async, SQPOLL, and `SINGLE_ISSUER|DEFER_TASKRUN` rings while requests and CQEs are in flight. It targets SQ/CQ remapping correctness, CQE preservation, overflow rejection, and mmap races.

Important APIs/types/functions: `io_uring_resize_rings`, `io_uring_queue_init_params`, `io_uring_queue_mmap`, `io_uring_unmap_rings`, `io_uring_for_each_cqe`, `io_uring_cq_advance`, `io_uring_prep_read`, `io_uring_prep_nop`, `IOSQE_ASYNC`, `IORING_SETUP_SQPOLL`, `IORING_SETUP_SINGLE_ISSUER`, and `IORING_SETUP_DEFER_TASKRUN`.

Control flow: `main()` optionally opens `/dev/nvme0n1` for direct read coverage, then runs `test()` over several ring modes and async settings. `test_basic()` verifies a NOP before and after resize, `test_reads()` and `test_pipes()` resize while blocking reads complete, `test_all_copy()` verifies CQE order after growing, `test_overflow()` expects `-EOVERFLOW` when shrinking below pending CQEs, `test_same_resize()` checks same-size resize, and `test_mmap_race()` forks children that mmap/unmap the ring while the parent resizes.

State/persistence behavior: no durable state except optional device/file reads; most state is ring mapping metadata, pending SQEs/CQEs, pipe bytes, per-request `user_data`, and child mmap views. The pipe writer thread creates live completions while the ring shape changes.

Dependencies/integration: uses liburing helpers, pthreads, fork/wait, pipes, optional block device direct I/O, and kernel support for resize and deferred taskrun. Unsupported setup or resize support is surfaced as `T_EXIT_SKIP`.

Risks/test signals: failures include lost/misordered CQEs, bad `user_data`, negative read CQEs, unexpected resize errors, overflow not rejected, or crash/race symptoms. The mmap race is timing-sensitive and intentionally stress-oriented.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/resize-rings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ring-leak.c -->
# sources/test-tools/liburing/test/ring-leak.c

Purpose: regression coverage for io_uring lifetime leaks caused by SCM_RIGHTS transfer, registered-file cycles, and io-wq cancellation during ring teardown.

Important APIs/types/functions: raw `__sys_io_uring_setup`, `__sys_io_uring_register`, `IORING_REGISTER_FILES`, `io_uring_register_files`, `io_uring_register_files_update`, `io_uring_queue_exit`, UNIX datagram `socketpair`, `SCM_RIGHTS`, and pipe reads as a quiescence signal.

Control flow: `test_iowq_request_cancel()` registers pipe fds, queues fixed-file reads including an async one, exits the ring, then verifies the registered write end eventually closes. `test_scm_cycles()` sends the ring fd over a UNIX socket, registers or updates a set containing pipes and socket endpoints, closes external references, exits the ring, triggers UNIX GC, and waits for EOF. `main()` also runs the original raw-ring SCM_RIGHTS cycle scenario around a fork.

State/persistence behavior: state is kernel-owned ring/file reference graphs rather than filesystem state. The tests deliberately create cycles among ring fds, registered file tables, UNIX sockets, pipes, and io-wq work.

Dependencies/integration: depends on UNIX ancillary fd passing, io_uring file registration, kernel garbage collection for UNIX sockets, and async ring teardown. `sendmsg` returning `EINVAL` is treated as an unsupported/skip path.

Risks/test signals: a bad kernel may hang, leak the ring, or keep pipe write ends alive. The test mostly signals by successful process exit and pipe EOF rather than by explicit memory accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ring-leak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ring-leak2.c -->
# sources/test-tools/liburing/test/ring-leak2.c

Purpose: reproduces a two-ring deadlock/leak pattern where server and client rings hold pending poll/eventfd operations and a circular reference can prevent full exit.

Important APIs/types/functions: `io_uring_queue_init_params`, raw `__sys_io_uring_enter`, `io_uring_prep_poll_add`, `io_uring_prep_read`, `IOSQE_ASYNC`, `eventfd`, pthreads, nonblocking TCP listener sockets, and packed `conn_info` stored in `sqe->user_data`.

Control flow: a server thread creates a nonblocking TCP listener and eventfd, queues eventfd read and listener poll, and on completions may submit the client ring under a mutex. A client thread creates its own ring, queues an async eventfd read, enters the ring manually with `IORING_ENTER_GETEVENTS`, and requeues eventfd reads. `main()` starts both threads and exits via a one-second `SIGALRM`.

State/persistence behavior: all state is process-local sockets, eventfds, ring CQ/SQ state, and cross-thread pointer state (`client_ring`, `client_eventfd`). No filesystem persistence is used.

Dependencies/integration: exercises io_uring poll/read on eventfds and sockets, raw enter behavior, pthread synchronization, and teardown of rings with pending operations. The alarm bounds the regression.

Risks/test signals: the intended failure is a hang or unkillable pending io-wq/ring reference cycle. Because success is time-bounded exit, this is a liveness regression test with limited semantic assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ring-leak2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ring-query.c -->
# sources/test-tools/liburing/test/ring-query.c

Purpose: validates the `IORING_REGISTER_QUERY` ABI for opcode/capability discovery, including invalid inputs, linked query headers, loop rejection, and forward/backward compatible result sizes.

Important APIs/types/functions: `io_uring_register`, `IORING_REGISTER_QUERY`, `IO_URING_QUERY_OPCODES`, `struct io_uring_query_hdr`, `struct io_uring_query_opcode`, short/large local ABI shape variants, and `uring_ptr_to_u64`.

Control flow: `test_basic_query()` probes support and stores the system opcode counts/flags. `test_invalid()` checks unsupported query ops and bad pointers. `test_chain()` links three valid query headers and verifies identical outputs. `test_chain_loop()` ensures cyclic query lists fail. Compatibility tests pass shorter and larger output buffers and compare common fields with `sys_ops`.

State/persistence behavior: no persistent state; `sys_ops` is process-global cached query output used to validate subsequent tests.

Dependencies/integration: includes `test.h` and liburing helpers, but uses the register ABI directly. It deliberately supports a null ring pointer by registering against fd `-1` for global query behavior.

Risks/test signals: exact negative errno behavior matters (`-EOPNOTSUPP`, `-EFAULT`, nonzero loop failure). A kernel that changes query sizing or result fields could fail compatibility checks.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ring-query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ringbuf-loop.c -->
# sources/test-tools/liburing/test/ringbuf-loop.c

Purpose: regression test for incremental provided buffer rings where the receive buffer address is the buffer ring itself, ensuring buffer completion accounting survives the command overwriting ring entries.

Important APIs/types/functions: `io_uring_queue_init` with `IORING_SETUP_NO_SQARRAY`, `io_uring_setup_buf_ring`, `IOU_PBUF_RING_INC`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `io_uring_prep_recv`, `IOSQE_BUFFER_SELECT`, and `io_uring_free_buf_ring`.

Control flow: the program creates a tiny provided buffer ring, adds the ring memory as a provided buffer, sends zero bytes over a UNIX datagram socketpair, and queues a receive selecting that buffer group. It waits for one completion, then frees the buffer ring and exits.

State/persistence behavior: ring memory is intentionally used as mutable data payload. The key state is the kernel-selected buffer metadata that must be committed even after the recv overwrites address/length fields in userspace memory.

Dependencies/integration: depends on provided buffer ring support, incremental buffer ring registration, UNIX datagram sockets, and `IORING_SETUP_NO_SQARRAY`. `-EINVAL` paths are treated as skips.

Risks/test signals: most regressions appear as kernel memory misuse, failed setup, failed completion, or teardown trouble rather than explicit payload checks.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ringbuf-loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ringbuf-read.c -->
# sources/test-tools/liburing/test/ringbuf-read.c

Purpose: tests mapped provided buffer rings with file reads, covering direct I/O, buffered I/O, and optional async submission.

Important APIs/types/functions: `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `io_uring_prep_read`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, `IORING_CQE_BUFFER_SHIFT`, `O_DIRECT`, `posix_memalign`, and `posix_fadvise`.

Control flow: `main()` creates or uses a test file whose 128 blocks contain distinct byte patterns. `test()` sets up 128 provided buffers, queues reads for half the file with buffer selection, waits for completions, extracts selected buffer IDs, and verifies the chosen buffer contains the expected pattern for the request `user_data`. The matrix covers direct/buffered and sync/async unless buffer rings are unsupported.

State/persistence behavior: temporary file contents are deterministic block patterns; provided ring state tracks available buffers and selected IDs. The temporary file is unlinked unless provided by argv.

Dependencies/integration: uses liburing buffer-ring APIs, filesystem reads, alignment requirements for direct I/O, and helper `t_create_file`.

Risks/test signals: detects wrong buffer IDs, missing `IORING_CQE_F_BUFFER`, short reads, unsupported direct I/O, and stale/misrouted payload data. Resource cleanup is partial on some early failures, but test process exit bounds it.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ringbuf-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ringbuf-status.c -->
# sources/test-tools/liburing/test/ringbuf-status.c

Purpose: validates userspace-visible provided buffer ring status helpers, especially group head lookup and available count before and after consumption.

Important APIs/types/functions: `io_uring_buf_ring_head`, `io_uring_buf_ring_available`, `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, and group id `BGID`.

Control flow: `test(0)` initializes an 8-buffer ring, verifies head zero and all buffers available, queues a pipe read with buffer selection, confirms head unchanged before data arrives, writes data, waits for completion, and verifies head advanced and availability dropped. `test(1)` checks invalid group-id lookup. `test_max()` registers 32,768 buffers and verifies availability at half and full states.

State/persistence behavior: all state is buffer-ring metadata, pipe data, and in-memory buffers. No files are persisted.

Dependencies/integration: requires kernel support for buffer rings and ring status queries; `-EINVAL` sets skip flags for missing support. It uses pipes to create a controlled buffer consumption event.

Risks/test signals: catches incorrect head reporting, bad invalid-group behavior, wrong availability counts, and missing buffer-selection completions. The high-buffer-count case also exercises sizing/overflow boundaries.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ringbuf-status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/rsrc_tags.c -->
# sources/test-tools/liburing/test/rsrc_tags.c

Purpose: tests resource tags for registered files and buffers, including tag CQE emission on update/removal, no-CQE behavior for zero tags, empty buffer semantics, and partial registration failure cleanup.

Important APIs/types/functions: raw `__sys_io_uring_register`, `IORING_REGISTER_FILES2`, `IORING_REGISTER_BUFFERS2`, `IORING_REGISTER_FILES_UPDATE2`, `IORING_REGISTER_BUFFERS_UPDATE`, `io_uring_rsrc_register`, `io_uring_rsrc_update2`, `IORING_FEAT_RSRC_TAGS`, `io_uring_register_files_update`, fixed-buffer reads, and `io_uring_register_*_tags`.

Control flow: `has_rsrc_update()` gates feature support. `test_tags_generic()` registers resources with tags, updates tags, and verifies emitted CQEs carry old tags only when appropriate. `test_files()` covers file removal and disallowed nonzero tag on removal. `test_buffers_update()` ensures updating an in-use buffer delays tag CQE until the read finishes. `test_buffers_empty_buffers()` covers empty-to-full, full-to-empty, invalid empty length, and failed fixed reads on empty slots. `test_tagged_register_partial_fail()` ensures failed tagged registration does not emit stray CQEs.

State/persistence behavior: state lives in registered resource tables, tags, pipe fds, and CQEs. No durable files are created.

Dependencies/integration: uses raw registration ABI intentionally instead of wrappers for ABI coverage. Runs under default, IOPOLL, SQPOLL, and defer-taskrun modes where supported.

Risks/test signals: failures include missing or extra tag CQEs, wrong `user_data` tag values, premature update notification while buffers are still in use, or acceptance of invalid empty-buffer/tag combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/rsrc_tags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/runtests-loop.sh -->
# sources/test-tools/liburing/test/runtests-loop.sh

Purpose: simple stress harness that repeatedly invokes `./runtests.sh` with the user-supplied test list until a run fails.

Important APIs/types/functions: Bash arrays, infinite `while true` loop, command status `$?`, integer iteration counter, and pass-through arguments.

Control flow: captures `"$@"` into `TESTS`, runs `./runtests.sh "${TESTS[@]}"`, breaks and reports the loop index on nonzero exit, otherwise prints completion and increments `ITER`.

State/persistence behavior: no private persistent state beyond stdout and whatever `runtests.sh` writes, such as output timings or failure artifacts. The loop counter is process-local.

Dependencies/integration: assumes current working directory contains executable `runtests.sh` and built test binaries. It is a wrapper around the main liburing test harness.

Risks/test signals: failures are surfaced only when `runtests.sh` returns nonzero. The loop is intentionally unbounded and needs external termination for long soak runs.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/runtests-loop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/runtests-quiet.sh -->
# sources/test-tools/liburing/test/runtests-quiet.sh

Purpose: quiet wrapper around `runtests.sh` that suppresses output for passing runs and prints captured output only when the test run fails.

Important APIs/types/functions: `mktemp`, Bash arrays, stdout/stderr redirection, exit status propagation, `cat`, and `rm`.

Control flow: stores arguments in `TESTS`, creates a temporary result file, runs `./runtests.sh` with all output redirected there, captures `RET`, prints the file only for nonzero return, removes it, and exits with `RET`.

State/persistence behavior: creates one temporary file and deletes it before exit. It otherwise relies on `runtests.sh` for output directory and artifact management.

Dependencies/integration: assumes `runtests.sh` is executable in the current directory and `mktemp` is available. It preserves the main harness return semantics.

Risks/test signals: if interrupted before `rm`, the temp file may remain. Successful runs are silent, so timing/skip summaries from the underlying harness are hidden unless failure occurs.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/runtests-quiet.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/runtests.sh -->
# sources/test-tools/liburing/test/runtests.sh

Purpose: main shell harness for running selected liburing test binaries with timeout, optional device arguments, dmesg scanning, skip/fail/timeout aggregation, and timing history.

Important APIs/types/functions: Bash arrays and associative arrays, `TIMEOUT`, `TEST_FILES`, `TEST_MAP`, optional `config.local`, `_check_dmesg()`, `run_test()`, `timeout -s INT -k`, `/dev/kmsg`, `dmesg`, status code `77` for skip, `TEST_EXCLUDE`, and `TEST_GNU_EXITCODE`.

Control flow: sources `config.local` if present and validates mapped devices. For each requested test, it optionally runs once without a device, against each `TEST_FILES` device, or against a specific `TEST_MAP` entry. `run_test()` prints status, skips excluded tests, runs the binary under timeout, preserves core files, checks exit/skips/xfails, scans dmesg after a marker, and records elapsed seconds under `output/`.

State/persistence behavior: writes timing files in `output/`, may move `core` to `core-$test_name`, may create `.dmesg` files for kernel warnings, and reads local config. No checklist state is modified.

Dependencies/integration: integrates compiled test binaries, kernel log access when root, system `timeout`, optional block devices, and liburing convention that `77` means skipped.

Risks/test signals: dmesg pattern matching can produce root-only signals and may be noisy if markers are unavailable. Timeout status is reported but not treated as failure unless downstream policy interprets output.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/runtests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/rw_merge_test.c -->
# sources/test-tools/liburing/test/rw_merge_test.c

Purpose: regression for incorrect async-list `io_should_merge()` behavior where a later file read could be merged with a blocked pipe read and hang.

Important APIs/types/functions: `io_uring_prep_readv`, `io_uring_wait_cqe_timeout`, `struct __kernel_timespec`, pipes, temporary file creation/truncation, and `t_create_ring`.

Control flow: queues a blocking pipe `readv` and a file `readv` past EOF, expects the file read CQE with result zero, then queues another file read adjacent to the previous file range. A three-second timeout detects whether the third read incorrectly merged with the pipe request and got stuck.

State/persistence behavior: creates and unlinks `testfile` while holding an fd, creates one pipe, and uses one shared buffer. The key state is kernel async request merge bookkeeping.

Dependencies/integration: relies on a kernel path that can punt reads to async context and on timeout waiting support. It skips only when ring creation is unavailable.

Risks/test signals: failure is a timeout or wrong CQE result/user data. The test uses assertions heavily, so abnormal behavior aborts rather than graceful diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/rw_merge_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/self.c -->
# sources/test-tools/liburing/test/self.c

Purpose: verifies async pathname resolution for `/proc/self` uses the original submitting task rather than an io-wq worker.

Important APIs/types/functions: `io_uring_prep_openat2`, `struct open_how`, `O_RDONLY`, `io_uring_submit`, `io_uring_wait_cqe`, `/proc/self/comm`, and normal `read`.

Control flow: `io_openat2()` submits one openat2 request and returns the CQE result fd or errno. `main()` opens `/proc/self/comm` through io_uring, reads it, and expects the command name to start with `self`.

State/persistence behavior: no durable state; it reads procfs task metadata. The tested state is the task context used by async path resolution.

Dependencies/integration: depends on kernel `openat2` support, procfs, and liburing openat2 prep helper. `-EINVAL` or `-EOPNOTSUPP` are treated as skip/success paths for older kernels.

Risks/test signals: a regression returns the worker comm rather than the test program name, or fails open/read. The assertion is narrow to process naming and may be affected by unusual invocation names.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/self.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/send-zerocopy.c -->
# sources/test-tools/liburing/test/send-zerocopy.c

Purpose: comprehensive coverage of zero-copy send operations, including `SEND_ZC`, `SENDMSG_ZC`, fixed buffers, IPv4/IPv6, TCP/UDP, cork/link sequences, async mode, address passing, large/unaligned/hugetlb buffers, notification CQEs, and invalid cases.

Important APIs/types/functions: `io_uring_prep_send_zc`, `io_uring_prep_sendmsg_zc`, `io_uring_prep_send_set_addr`, `IORING_CQE_F_MORE`, `IORING_CQE_F_NOTIF`, `IORING_RECVSEND_FIXED_BUF`, `IORING_RECVSEND_POLL_FIRST`, `IORING_SEND_ZC_REPORT_USAGE`, `io_uring_register_probe`, `t_register_buffers`, and helper `t_create_socketpair_ip`.

Control flow: `probe_zc_support()` gates opcode availability. `run_basic_tests()` covers simple sends, vector sends, bad buffers/addresses/flags, async address lifetime, report-usage notification, and malformed `SENDMSG_ZC`. The main matrix then registers buffers and `test_inet_send()` iterates many combinations of socket family, connection mode, TCP/UDP, `SO_ZEROCOPY`, send/sendmsg, fixed or mixed registered buffers, corked linked requests, async, poll-first, normal/large/unaligned/huge buffers, and iovec shape.

State/persistence behavior: state is socket buffers, registered memory, CQ notification chains, and global feature flags (`has_sendzc`, `has_sendmsg`, `has_regvec`, `hit_enomem`, `no_send_vec`). No files persist.

Dependencies/integration: uses loopback sockets, memory mapping/hugetlb where available, registered buffers, and kernel zero-copy notification semantics. Some paths skip on unsupported opcodes, `-EINVAL`, unavailable memory, or memlock limits.

Risks/test signals: detects wrong send lengths, missing or extra notification CQEs, bad `F_MORE`/`F_NOTIF` sequencing, payload mismatch, stale address use, incorrect fixed-buffer handling, and kernel `-ENOMEM` resource pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/send-zerocopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/send_recv.c -->
# sources/test-tools/liburing/test/send_recv.c

Purpose: exercises io_uring UDP send/recv paths with normal buffers, buffer selection, registered receive fds, SQPOLL, async submission, and vector send variants.

Important APIs/types/functions: `io_uring_prep_recv`, `io_uring_prep_send`, `IOSQE_FIXED_FILE`, `IOSQE_ASYNC`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_SOCK_NONEMPTY`, `IORING_SETUP_SQPOLL`, `IORING_FEAT_SQPOLL_NONFIXED`, and `IORING_SETUP_SUBMIT_ALL` invalid sendmsg/recvmsg checks.

Control flow: a receiver thread sets up a UDP socket bound to localhost, optionally registers it, queues a recv, unlocks the sender, and verifies completion length/data. The sender creates a connected UDP socket and submits send, two-iovec, or 32-iovec send. `main()` initializes a patterned 4 KiB payload, checks invalid NULL msg cases return `-EFAULT`, then runs a matrix across SQPOLL, registration, async, provided buffers, and vector send.

State/persistence behavior: no persistent state; process-global payload `str` is used as the expected data and `no_send_vec` records kernels without vector send support.

Dependencies/integration: depends on pthread synchronization, localhost UDP port 10202, liburing helpers, optional SQPOLL nonfixed support, and buffer selection behavior.

Risks/test signals: failures include wrong lengths, data mismatch, ENOBUFS flag mistakes, unsupported vector sends, bad invalid-pointer errno, and races around fixed port reuse.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/send_recv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/send_recvmsg.c -->
# sources/test-tools/liburing/test/send_recvmsg.c

Purpose: tests UDP `sendmsg`/`recvmsg` through io_uring with single and multi-iovec receive buffers, legacy provided buffers, provided buffer rings, missing-buffer errors, and async mode.

Important APIs/types/functions: `io_uring_prep_recvmsg`, `io_uring_prep_sendmsg`, `io_uring_prep_provide_buffers`, `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, buffer group `BUF_BGID`, and buffer id `BUF_BID`.

Control flow: `recv_fn()` creates a receive ring, optionally registers a buffer ring or provided buffer, queues `recvmsg`, then waits and validates the string payload or expected ENOBUFS. `do_sendmsg()` sends the fixed string to localhost UDP port 10203. `test()` synchronizes receiver and sender threads. `main()` runs sync and async cases across plain, multi-iov, buffer select, missing buffer, and buffer ring combinations.

State/persistence behavior: state is socket data, stack iovecs, optional provided-buffer registration, and global `ud` user data counter plus `no_pbuf_ring` feature cache.

Dependencies/integration: depends on pthreads, UDP localhost, provided buffer APIs, and kernel recvmsg support. Unsupported provide-buffers or buffer-ring paths are skipped by returning success from that scenario.

Risks/test signals: catches wrong payload length, string mismatch, wrong selected buffer id, missing ENOBUFS on no-buffer cases, and provided-buffer-ring support regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/send_recvmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sendmsg_iov_clean.c -->
# sources/test-tools/liburing/test/sendmsg_iov_clean.c

Purpose: regression for non-immediate `sendmsg` completion when the submitted `msghdr`/iovec memory is stack-backed and could be reused after submission.

Important APIs/types/functions: `io_uring_prep_multishot_accept`, `io_uring_prep_sendmsg`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, pthread barrier synchronization, TCP sockets, `SO_SNDBUF`, and `SIGUSR1` notification.

Control flow: `main()` starts a TCP listener on port 9999 and queues multishot accept. A client thread connects, waits on a barrier, and drains incoming data. On accept CQE, `queue_sends()` shrinks the send buffer, fills it until `EAGAIN`, then queues 256 `sendmsg` SQEs using an iovec array in the caller-owned `msghdr`. The loop exits successfully after all send completions are observed.

State/persistence behavior: all state is sockets, in-flight sendmsg requests, stack iovecs, and the receiver thread. It intentionally pressures non-immediate completion paths by filling the socket send buffer.

Dependencies/integration: requires multishot accept and `SINGLE_ISSUER|DEFER_TASKRUN`; `-EINVAL` setup or accept support leads to skip. Uses a fixed localhost port, so parallel runs can conflict.

Risks/test signals: failure means lost send completions, use-after-return of iovec data, setup unsupported, or unexpected CQE user data. The test exits directly on success after seeing all sends.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sendmsg_iov_clean.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sendzc-bug.c -->
# sources/test-tools/liburing/test/sendzc-bug.c

Purpose: regression for zero-copy sendmsg fixed-buffer lifetime where imported buffer nodes must remain tied to notification lifetime, not just the main request.

Important APIs/types/functions: `io_uring_prep_sendmsg_zc`, `IORING_RECVSEND_FIXED_BUF`, `io_uring_register_buffers`, `io_uring_unregister_buffers`, `SO_ZEROCOPY`, `mmap`, `munmap`, and a local TCP socketpair helper.

Control flow: creates a connected TCP pair, enables `SO_ZEROCOPY`, registers a 1 MiB mapped buffer, submits fixed-buffer `sendmsg_zc`, waits for the main CQE, unregisters and unmaps the buffer immediately, then reads the data from the peer socket.

State/persistence behavior: memory lifetime is the core state: the userspace buffer is unmapped after the send completion but before notification lifetime may end. Socket data is read into a static buffer.

Dependencies/integration: depends on TCP loopback, zero-copy sendmsg support, fixed buffer registration, and kernel notification ownership semantics. `-EINVAL` from the CQE is treated as skip.

Risks/test signals: a buggy kernel can access freed/unmapped memory, crash, or corrupt send data. The test mainly checks survival and successful peer read.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sendzc-bug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/shared-wq.c -->
# sources/test-tools/liburing/test/shared-wq.c

Purpose: tests workqueue sharing setup through `IORING_SETUP_ATTACH_WQ`, including rejection of non-ring descriptors and successful attachment to a real ring.

Important APIs/types/functions: `io_uring_queue_init_params`, `IORING_SETUP_ATTACH_WQ`, `io_uring_params.wq_fd`, and `io_uring_queue_exit`.

Control flow: `main()` creates a base ring, calls `test_attach_invalid(2)` expecting `-EINVAL` when attaching to stdout, then calls `test_attach()` with the base ring fd and accepts `-EINVAL` as unsupported sharing or zero as success.

State/persistence behavior: only kernel ring/workqueue state is involved. No files or sockets persist.

Dependencies/integration: exercises ring setup parameter validation and shared worker-pool attachment. It does not queue I/O.

Risks/test signals: detects acceptance of invalid `wq_fd`, unexpected setup errno, or inability to attach where supported. It treats missing feature support as a passing skip-style path.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/shared-wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/short-read.c -->
# sources/test-tools/liburing/test/short-read.c

Purpose: verifies a readv larger than the file returns a short successful completion rather than an error or hang.

Important APIs/types/functions: `t_create_file`, `io_uring_prep_readv`, `io_uring_wait_cqes`, `struct iovec`, `BUF_SIZE`, and `FILE_SIZE`.

Control flow: creates a 1024-byte temporary file, unlinks it after open, allocates a 4096-byte buffer, queues one `readv`, waits for one CQE, and expects `cqe->res == FILE_SIZE`.

State/persistence behavior: creates `.short-read` transiently and removes it immediately after open. Read state is a single fd and heap buffer.

Dependencies/integration: uses normal filesystem reads and liburing queue setup. No feature probing is needed beyond ring init.

Risks/test signals: failure indicates incorrect short-read result, wait failure, SQE acquisition failure, or submit count mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/short-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/shutdown.c -->
# sources/test-tools/liburing/test/shutdown.c

Purpose: checks `IORING_OP_SHUTDOWN` and subsequent socket write behavior: after shutting down write side, `writev` should fail with `-EPIPE`.

Important APIs/types/functions: `io_uring_prep_shutdown`, `io_uring_prep_writev`, TCP loopback sockets, `shutdown(SHUT_WR)`, `TCP_NODELAY`, `SIGPIPE` handler, and helper nonblocking connect utilities.

Control flow: sets up a loopback TCP connection, waits for connect completion via `SO_ERROR`, initializes a ring, submits shutdown on the client fd, accepts `-EINVAL` as unsupported, then submits `writev` and requires `-EPIPE`.

State/persistence behavior: only socket state is mutated; no files are written. `SIGPIPE` is ignored through a no-op handler so the process observes the CQE error.

Dependencies/integration: depends on TCP loopback, io_uring shutdown support, and correct socket error propagation through io_uring writev.

Risks/test signals: failures include shutdown unsupported, shutdown returning another error, write succeeding, or write returning an errno other than `-EPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/shutdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sigfd-deadlock.c -->
# sources/test-tools/liburing/test/sigfd-deadlock.c

Purpose: regression for signalfd polling deadlock involving recursive `sighand->siglock` acquisition.

Important APIs/types/functions: `sigprocmask`, `signalfd`, `io_uring_prep_poll_add`, `POLLIN`, `kill(getpid(), SIGINT)`, and `IORING_OP_POLL_ADD` completion masks.

Control flow: blocks SIGINT and creates a nonblocking signalfd, queues an io_uring poll for `POLLIN`, sends SIGINT to itself, waits for the poll CQE, and treats `-EOPNOTSUPP` as skip or `POLLIN` as pass.

State/persistence behavior: signal mask and signalfd readiness are process-local. No persistent data is touched.

Dependencies/integration: uses Linux signalfd and io_uring poll integration. It includes helper return codes for skip/pass/fail.

Risks/test signals: bad kernels can deadlock in poll wakeup or return wrong readiness/error. The test detects wrong masks and negative CQE results.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sigfd-deadlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/single-issuer.c -->
# sources/test-tools/liburing/test/single-issuer.c

Purpose: verifies ownership semantics for `IORING_SETUP_SINGLE_ISSUER` across creator, first enabler, forked children, disabled rings, SQPOLL rings, and registered-ring enter paths.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_enable_rings`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_R_DISABLED`, `IORING_SETUP_SQPOLL`, `io_uring_prep_nop`, `io_uring_submit`, fork/wait helpers, and expected `-EEXIST`.

Control flow: `try_submit()` submits and reaps a NOP. `main()` first confirms the creator can submit and a child cannot. It then tests disabled rings where a child enables first and becomes issuer, disabled rings enabled by parent rejecting child submits, SQPOLL allowing creator and child submits, and a final child rejection case after normal setup.

State/persistence behavior: state is per-ring issuer ownership and process identity across forks. No filesystem state is used.

Dependencies/integration: requires `SINGLE_ISSUER` support; `-EINVAL` skips. Uses process forking to validate cross-task behavior.

Risks/test signals: failures include allowing non-owner submit, rejecting rightful first issuer, broken SQPOLL exception behavior, or bad CQE content for allowed submits.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/single-issuer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/skip-cqe.c -->
# sources/test-tools/liburing/test/skip-cqe.c

Purpose: validates `IOSQE_CQE_SKIP_SUCCESS` behavior for successful linked chains, failed linked chains, link timeouts, timeout cancellation, and hardlink chains.

Important APIs/types/functions: `IOSQE_CQE_SKIP_SUCCESS`, `IOSQE_IO_LINK`, `IOSQE_IO_HARDLINK`, `IOSQE_ASYNC`, `io_uring_prep_link_timeout`, `io_uring_prep_nop`, `io_uring_prep_read`, `IORING_FEAT_CQE_SKIP`, and pipe-backed failure request prep.

Control flow: after feature gating, `main()` runs success chains with and without the last CQE skipped, failure chains where a NULL write fails, link-timeout cancellation cases across timeout positions and async mode, timeout-fire cases with skip flags on main/timeout SQEs, and hardlink matrices across fail/skip positions and last-link marking. Each helper verifies exactly the expected CQEs remain.

State/persistence behavior: only pipe fds, ring CQ state, and request flags are used. The pipe read in timeout tests provides a cancellable pending operation.

Dependencies/integration: depends on CQE skip feature support and precise link/hardlink cancellation semantics.

Risks/test signals: extra CQEs, missing failure CQEs, wrong `user_data`, wrong cancellation errno, or success CQEs that should have been skipped all fail the test.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/skip-cqe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/socket-getsetsock-cmd.c -->
# sources/test-tools/liburing/test/socket-getsetsock-cmd.c

Purpose: compares socket getsockopt/setsockopt operations issued through io_uring socket commands with equivalent synchronous system calls.

Important APIs/types/functions: `io_uring_prep_cmd_sock`, `SOCKET_URING_OP_GETSOCKOPT`, `SOCKET_URING_OP_SETSOCKOPT`, `SO_RCVBUF`, `SO_PEERNAME`, `SO_REUSEPORT`, `TCP_USER_TIMEOUT`, `IOSQE_ASYNC`, and helper `t_create_socket_pair`.

Control flow: creates a connected socket pair, writes data, and runs getsockopt tests for peer name and receive buffer in sync/async modes. It then sets `SO_REUSEPORT` values and `TCP_USER_TIMEOUT` values via io_uring commands in sync/async modes and verifies regular `getsockopt` observes the same state.

State/persistence behavior: state is socket options and queued data inside the socket pair. Global `no_sock_opt` records unsupported command behavior.

Dependencies/integration: requires kernel socket command support and TCP socket option behavior. `-EOPNOTSUPP`/`-EINVAL` can skip unsupported paths.

Risks/test signals: detects wrong result lengths, mismatched option values, unsupported command errno, or async command behavior diverging from sync behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/socket-getsetsock-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/socket-io-cmd.c -->
# sources/test-tools/liburing/test/socket-io-cmd.c

Purpose: validates io_uring socket ioctl command operations (`SIOCINQ`, `SIOCOUTQ`) against normal ioctl behavior and internal socket buffer accounting.

Important APIs/types/functions: `io_uring_prep_cmd_sock`, `SOCKET_URING_OP_SIOCINQ`, `SOCKET_URING_OP_SIOCOUTQ`, `ioctl(SIOCINQ/SIOCOUTQ)`, stream/datagram socket pairs, raw sockets, and `t_create_ring`.

Control flow: `run_test()` creates a stream or datagram socket pair, writes a known message, queries receive and send queue sizes through io_uring commands, and verifies their sum equals written bytes. `run_test_raw()` opens a raw TCP socket when permitted and compares io_uring command results directly with ioctl values, retrying once for racing queue changes.

State/persistence behavior: state is socket queue occupancy. `no_io_cmd` records lack of socket io command support.

Dependencies/integration: needs socket command support, helper socket pairs, and root/capabilities for raw socket coverage. Unsupported raw socket creation is skipped.

Risks/test signals: detects incorrect queue counts, unsupported command handling, raw socket mismatch, or CQE user data/result corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/socket-io-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/socket-nb.c -->
# sources/test-tools/liburing/test/socket-nb.c

Purpose: verifies empty-socket recv returns immediate `-EAGAIN` only when `MSG_DONTWAIT` is set, independent of the socket fd `O_NONBLOCK` flag.

Important APIs/types/functions: TCP loopback setup, `t_set_nonblock`, `t_clear_nonblock`, `io_uring_prep_recv`, `MSG_DONTWAIT`, `io_uring_peek_cqe`, and `SO_ERROR` connect polling.

Control flow: `test()` builds a connected TCP pair, optionally marks the receiving fd nonblocking, queues one recv with or without `MSG_DONTWAIT`, and peeks for completion. `main()` runs all four combinations of fd nonblocking and message flag.

State/persistence behavior: only socket readiness and ring state are used. No data is sent, so the recv should be pending unless `MSG_DONTWAIT` forces immediate completion.

Dependencies/integration: uses TCP loopback and liburing recv. The test expects peek to return `-EAGAIN` for pending CQE, not necessarily socket `-EAGAIN`.

Risks/test signals: catches incorrect treatment of `O_NONBLOCK` as enough for immediate CQE, failure to honor `MSG_DONTWAIT`, or unexpected completions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/socket-nb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/socket-rw-eagain.c -->
# sources/test-tools/liburing/test/socket-rw-eagain.c

Purpose: checks that a nonblocking socket `readv` queued before a `writev` returns `-EAGAIN` instead of waiting for later data on kernels without fast poll.

Important APIs/types/functions: TCP loopback sockets, `t_set_nonblock`, `io_uring_queue_init_params`, `IORING_FEAT_FAST_POLL`, `io_uring_prep_readv`, `io_uring_prep_writev`, and CQ iteration.

Control flow: creates a TCP connection, sets the receive side nonblocking, initializes a ring, skips if fast poll is present, queues readv on empty socket then writev on the peer, submits both, and expects CQEs for write length 128 and read `-EAGAIN`.

State/persistence behavior: state is socket readiness and CQ ordering. No files persist.

Dependencies/integration: specifically targets non-fast-poll behavior; fast-poll kernels skip because the semantics differ.

Risks/test signals: failure indicates blocking/merge behavior where the read consumes later data, wrong write length, or missing CQEs.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/socket-rw-eagain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/socket-rw-offset.c -->
# sources/test-tools/liburing/test/socket-rw-offset.c

Purpose: verifies socket `readv` with offset `-1` queued before a `writev` does not hang and completes correctly on kernels advertising current-position read/write support.

Important APIs/types/functions: TCP loopback setup, `IORING_FEAT_RW_CUR_POS`, `io_uring_prep_readv` with offset `-1`, `io_uring_prep_writev`, `io_uring_submit_and_wait`, and CQ iteration.

Control flow: creates a connected TCP pair, initializes a ring, skips if `IORING_FEAT_RW_CUR_POS` is absent, queues readv on one socket with offset `-1` and writev on the other, then waits until both CQEs report 128 bytes.

State/persistence behavior: socket data is transient; no filesystem persistence is involved.

Dependencies/integration: depends on feature bit semantics for offset `-1` on non-file fds and TCP loopback behavior.

Risks/test signals: detects hangs, wrong completion lengths, or improper offset handling for sockets.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/socket-rw-offset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/socket-rw.c -->
# sources/test-tools/liburing/test/socket-rw.c

Purpose: baseline regression that a socket `readv` queued before a peer `writev` does not hang and both complete with the expected byte count.

Important APIs/types/functions: TCP loopback sockets, `io_uring_prep_readv`, `io_uring_prep_writev`, `io_uring_submit_and_wait`, `io_uring_for_each_cqe`, and helper nonblocking connect functions.

Control flow: creates a loopback TCP connection, queues a readv for 128 bytes on the accepted socket and a writev for 128 bytes on the connecting socket, submits both, and advances CQEs after both report exactly 128 bytes.

State/persistence behavior: no durable state; only socket queues and ring completions.

Dependencies/integration: exercises basic socket read/write via io_uring without feature gating.

Risks/test signals: failure is generally a hang, wrong CQE result, or incomplete CQE count.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/socket-rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/socket.c -->
# sources/test-tools/liburing/test/socket.c

Purpose: tests `IORING_OP_SOCKET` socket creation followed by connect/send, including direct descriptor allocation and SQPOLL receive combinations.

Important APIs/types/functions: `io_uring_prep_socket`, `io_uring_prep_socket_direct`, `io_uring_prep_connect`, `io_uring_prep_send`, `io_uring_prep_recv`, `IOSQE_FIXED_FILE`, `IORING_FILE_INDEX_ALLOC`, `IORING_SETUP_SQPOLL`, `IORING_FEAT_SQPOLL_NONFIXED`, and `io_uring_register_files`.

Control flow: a receiver thread binds an ephemeral UDP port, optionally registers the receive fd, queues recv, and verifies the received string. The sender either uses `IORING_OP_SOCKET`/direct socket to create a UDP socket or falls back to normal socket+send if unsupported, connects to the receiver, and sends the string. `main()` runs normal, SQPOLL registered/nonregistered, direct fixed index, direct allocated index, and bad socket-family validation.

State/persistence behavior: state is UDP socket endpoints, global port `g_port`, and optional fixed-file slot. No persistent files.

Dependencies/integration: depends on socket opcode support for full coverage, but falls back when unavailable. It uses pthread synchronization and helper socket binding.

Risks/test signals: detects unsupported opcode handling, direct descriptor misuse, bad fixed-file flags, invalid family errno (`-EAFNOSUPPORT`), and payload/length mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/splice.c -->
# sources/test-tools/liburing/test/splice.c

Purpose: validates io_uring splice and tee operations across file-to-pipe, pipe-to-file, pipe-to-pipe, zero-length operations, invalid offsets, non-pipe tee failures, and registered fixed-file mode.

Important APIs/types/functions: `io_uring_prep_splice`, `IORING_OP_SPLICE`, `IORING_OP_TEE`, `SPLICE_F_FD_IN_FIXED`, `IOSQE_FIXED_FILE`, `io_uring_register_files`, `IORING_FEAT_FAST_POLL`, pipes, temporary files, and random data verification.

Control flow: initializes input/output files, two pipes, and random buffers. It probes splice and tee support by expecting `-EBADF` for invalid fds, runs all positive and negative checks with real fds, registers six fds, remaps context fds to fixed indexes, sets fixed-file flags, and repeats the same splice/tee suite.

State/persistence behavior: temporary files are created then unlinked while open; buffers contain random expected content. Pipe/file offsets and registered file indexes are the main mutable state.

Dependencies/integration: requires fast-poll feature for splice support in this test, filesystem temp files, `/dev/urandom`, pipes, and fixed-file registration.

Risks/test signals: detects data corruption, wrong offset handling, missing invalid-operation errno (`-ESPIPE`/`-EINVAL`), fixed-file splice regressions, and incomplete splice loops.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/splice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sq-full-cpp.cc -->
# sources/test-tools/liburing/test/sq-full-cpp.cc

Purpose: C++ compilation variant of the SQ-full test, confirming liburing headers and `io_uring_get_sqe()` behavior work under C++.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_get_sqe`, `io_uring_queue_exit`, and queue depth 8.

Control flow: initializes an 8-entry ring, repeatedly calls `io_uring_get_sqe()` until it returns NULL, and expects exactly 8 SQEs.

State/persistence behavior: only ring SQ state is used. No external state or persistence.

Dependencies/integration: exercises the C++ build/link path for liburing test code and the same runtime helper behavior as the C version.

Risks/test signals: catches header incompatibility in C++ builds or incorrect SQE accounting when the submission queue fills.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sq-full-cpp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sq-full.c -->
# sources/test-tools/liburing/test/sq-full.c

Purpose: verifies `io_uring_get_sqe()` returns exactly the queue depth worth of SQEs and then reports full.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_get_sqe`, and `io_uring_queue_exit`.

Control flow: creates an 8-entry ring, loops until `io_uring_get_sqe()` returns NULL, counts acquired SQEs, and fails unless the count is 8.

State/persistence behavior: no persistent state; it only consumes local SQ slots without submitting them.

Dependencies/integration: baseline liburing queue accounting test.

Risks/test signals: detects off-by-one SQ capacity bugs or get-SQE behavior that allows overfill/underfill.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sq-full.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sq-poll-dup.c -->
# sources/test-tools/liburing/test/sq-poll-dup.c

Purpose: tests SQPOLL rings sharing a workqueue while duplicating and optionally closing the original ring fd, ensuring enter/submission still works through the duplicate.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `IORING_SETUP_ATTACH_WQ`, `IORING_FEAT_SQPOLL_NONFIXED`, `dup`, `close`, direct `O_DIRECT` reads, `io_uring_prep_read`, and multi-ring arrays.

Control flow: creates four SQPOLL rings, rings 1-3 attached to ring 0's workqueue, performs direct reads across all rings, duplicates ring 0 fd and optionally closes the original, then reads through attached rings and the duplicated original ring before/after idle sleep. `main()` runs three combinations of dup/close behavior.

State/persistence behavior: reads from a 128 MiB temporary or supplied file using aligned buffers. Ring fd ownership and shared SQ thread state are the main kernel state.

Dependencies/integration: requires SQPOLL, nonfixed SQPOLL feature, O_DIRECT-capable file/device, and sufficient permissions. Direct I/O unsupported or inaccessible paths skip.

Risks/test signals: failures include read CQE sizes not equal to 4096, broken ring fd replacement, SQPOLL idle wake issues, or shared workqueue teardown problems.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sq-poll-dup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sq-poll-kthread.c -->
# sources/test-tools/liburing/test/sq-poll-kthread.c

Purpose: verifies SQPOLL kernel threads stop after a userspace process exits, both when the process explicitly closes the ring and when it does not.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `sq_thread_idle`, fixed-file registration, `io_uring_prep_writev`, fork/wait, `system("ps --ppid 2 | grep io_uring-sq")`, and pipe I/O.

Control flow: child process creates an SQPOLL ring, registers pipe write end, submits a fixed-file writev, waits for successful CQE, and optionally calls `io_uring_queue_exit`. Parent waits for child, sleeps briefly, and scans kernel threads for lingering `io_uring-sq`. `main()` runs both explicit-exit and no-exit variants.

State/persistence behavior: state is SQPOLL kthread lifetime, pipe fds, and child process exit. No files persist.

Dependencies/integration: depends on process/kthread visibility through `ps`, SQPOLL permissions, and fixed-file write support.

Risks/test signals: lingering SQPOLL thread after child exit is failure. The `ps|grep` heuristic can be environment-sensitive if unrelated io_uring SQ threads exist.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sq-poll-kthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sq-poll-share.c -->
# sources/test-tools/liburing/test/sq-poll-share.c

Purpose: tests SQPOLL workqueue sharing across multiple rings under sustained direct read load.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `IORING_SETUP_ATTACH_WQ`, `IORING_FEAT_SQPOLL_NONFIXED`, `io_uring_prep_read`, `O_DIRECT`, aligned buffers, and four-ring fanout.

Control flow: creates or uses a 128 MiB file, opens it with direct I/O, initializes four SQPOLL rings with rings 1-3 attached to ring 0, then loops through file-sized work queuing 64 reads per ring and waiting for each completion to return 4096 bytes.

State/persistence behavior: temporary read file is unlinked after open when created internally. Ring workqueue sharing and in-flight read state are the focus.

Dependencies/integration: requires SQPOLL, nonfixed SQPOLL feature, O_DIRECT support, and access to the test file/device.

Risks/test signals: detects sharing setup failures, read completion errors, wrong byte counts, and SQPOLL wake/completion issues under multi-ring load.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sq-poll-share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sq-space_left.c -->
# sources/test-tools/liburing/test/sq-space_left.c

Purpose: tests liburing SQ space accounting before fill, after each `get_sqe`, and after partial submission failure caused by an invalid opcode.

Important APIs/types/functions: `io_uring_sq_space_left`, `io_uring_sq_ready`, `io_uring_get_sqe`, `io_uring_prep_nop`, `io_uring_submit`, and invalid opcode `0xfe`.

Control flow: `test_left()` fills an 8-entry ring one SQE at a time and checks remaining space after every acquisition. `test_sync()` queues 8 NOPs, one invalid opcode, then 8 more NOPs; submit should process 8 successes plus the bad request, leave the trailing 8 ready, then a second submit should clear them.

State/persistence behavior: only local SQ state is used; no requests need CQE validation.

Dependencies/integration: covers liburing userspace SQ accounting and kernel submission-stop behavior on invalid opcodes.

Risks/test signals: catches stale SQ-ready counts, space-left miscounting, or failure to preserve trailing SQEs after a synchronous submission error.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sq-space_left.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sqe-mixed-bad-wrap.c -->
# sources/test-tools/liburing/test/sqe-mixed-bad-wrap.c

Purpose: verifies `IORING_SETUP_SQE_MIXED` rejects a 128-byte SQE placed at the final 64-byte slot before ring wrap and remains usable afterward.

Important APIs/types/functions: `IORING_SETUP_SQE_MIXED`, `io_uring_prep_nop`, `io_uring_prep_nop128`, `io_uring_get_sqe`, CQE result validation, and sequence `user_data`.

Control flow: initializes an 8-entry mixed-SQE ring, submits seven normal NOPs to position the SQ tail at the last slot, submits a NOP128 that should fail, then submits a normal NOP that should still succeed.

State/persistence behavior: state is SQ tail position and mixed SQE slot accounting. No external state.

Dependencies/integration: requires mixed SQE setup support; unsupported kernels skip.

Risks/test signals: catches acceptance of an out-of-bound 128-byte SQE at wrap, broken recovery after the rejected SQE, or CQE result/user data corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sqe-mixed-bad-wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sqe-mixed-boundary.c -->
# sources/test-tools/liburing/test/sqe-mixed-boundary.c

Purpose: tests physical SQE boundary validation for mixed SQEs when the `sq_array` remaps a logical NOP128 to the last physical SQE slot.

Important APIs/types/functions: `IORING_SETUP_SQE_MIXED`, `t_io_uring_init_sqarray`, `io_uring_get_sqe128`, `io_uring_prep_nop128`, direct `ring.sq.array` manipulation, and expected `-EINVAL`.

Control flow: `test_valid_position()` confirms a normal NOP plus valid NOP128 succeeds. `test_oob_boundary()` advances tail state, overrides `sq_array[1]` to the last physical slot, writes a NOP128 there, submits, and requires the NOP128 CQE to fail with `-EINVAL` rather than reading past the SQE array.

State/persistence behavior: mutates userspace SQ array mapping directly to force the boundary condition. No external state.

Dependencies/integration: depends on helper support for initializing a ring with exposed sq_array and on mixed SQE kernel validation.

Risks/test signals: detects the historical 64-byte out-of-bounds read risk, missing CQE for the rejected SQE, or failure of a valid NOP128 placement.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sqe-mixed-boundary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sqe-mixed-nop.c -->
# sources/test-tools/liburing/test/sqe-mixed-nop.c

Purpose: validates mixed 64-byte and 128-byte NOP SQEs, including SQ readiness/space accounting across wrap and `IORING_SETUP_SQ_REWIND`.

Important APIs/types/functions: `IORING_SETUP_SQE_MIXED`, `IORING_SETUP_SQ_REWIND`, `io_uring_get_sqe`, `io_uring_get_sqe128`, `io_uring_prep_nop128`, `io_uring_sq_ready`, `io_uring_sq_space_left`, and CQE user data sequencing.

Control flow: `test_flags()` alternates normal and 128-byte NOPs for 32 iterations, then `test_sq_space()` builds specific SQ occupancy sequences, checking that NOP128 consumes two or three slots depending on wrap behavior and rewind mode. It runs once without rewind and once with rewind.

State/persistence behavior: all state is mixed SQ tail/head accounting and CQ completions. No external resources.

Dependencies/integration: requires mixed SQE support and optionally SQ rewind support; unsupported setup skips.

Risks/test signals: catches wrong slot consumption, wrong ready/space counts, wrap handling bugs, CQE errors, and user_data sequencing errors.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sqe-mixed-nop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sqe-mixed-uring_cmd.c -->
# sources/test-tools/liburing/test/sqe-mixed-uring_cmd.c

Purpose: combines normal NOP SQEs with 128-byte NVMe passthrough `uring_cmd` SQEs under mixed SQE/CQE setup.

Important APIs/types/functions: `IORING_SETUP_CQE_MIXED`, `IORING_SETUP_SQE_MIXED`, `io_uring_prep_uring_cmd128`, `NVME_URING_CMD_IO`, `struct nvme_uring_cmd`, `nvme_get_info`, `nvme_cmd_read`, `lba_shift`, and `nsid`.

Control flow: requires a device path argument, verifies it is an NVMe character device with `nvme_get_info`, initializes a mixed SQE/CQE ring, then loops 32 times alternating normal NOP submissions and NVMe read passthrough commands into a static 4 KiB buffer.

State/persistence behavior: reads from an NVMe namespace but does not write. Global NVMe metadata from `nvme.h` shapes the command.

Dependencies/integration: depends on NVMe passthrough support, device permissions, character-device path, and mixed SQE/CQE kernel support. Missing prerequisites skip.

Risks/test signals: detects mixed SQE corruption, passthrough command failure, wrong CQE result, wrong user data, or incompatible device metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sqe-mixed-uring_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sqpoll-disable-exit.c -->
# sources/test-tools/liburing/test/sqpoll-disable-exit.c

Purpose: syzkaller-derived regression for SQPOLL/ring setup teardown involving disabled/large ring parameters and process exit under repeated forks.

Important APIs/types/functions: raw `__sys_io_uring_setup`, manual `mmap` of SQ/CQ rings and SQEs, fixed virtual addresses, process groups, `PR_SET_PDEATHSIG`, `oom_score_adj`, fork/kill/wait loops, and sanitizer skip guard.

Control flow: outside sanitizer builds, `main()` maps syzkaller-style memory regions and runs 100 iterations. Each child sets death-signal/process-group state and calls `execute_one()`, which writes crafted `io_uring_params` fields in mapped memory and invokes setup for a large entry count. Parent kills children that exceed five seconds and includes fuse abort cleanup logic.

State/persistence behavior: no durable files; it writes `/proc/self/oom_score_adj` and manipulates process/killing state. The core state is kernel ring setup/exit behavior under abnormal child teardown.

Dependencies/integration: includes raw syscall wrapper and syzkaller reproduction code; sanitizer builds return skip to avoid incompatible instrumentation.

Risks/test signals: designed to expose hangs, teardown leaks, or crashes. It has little semantic assertion beyond bounded child exit.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sqpoll-disable-exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sqpoll-exec.c -->
# sources/test-tools/liburing/test/sqpoll-exec.c

Purpose: regression for SQPOLL close task_work ordering where a file closed via io_uring must be immediately closed by the time its close CQE is received, allowing subsequent exec.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `io_uring_prep_openat`, `io_uring_prep_close`, `execve`, fork/wait, `stat`, and helper `t_create_ring_params`.

Control flow: finds `exec-target.t` in current or `test/`, opens it through an SQPOLL ring, closes the returned fd through io_uring, waits for the close CQE, forks, and the child execs the target. `main()` repeats this sequence 20 times.

State/persistence behavior: uses the executable file as a target and mutates only fd lifetime. No file contents are changed.

Dependencies/integration: depends on SQPOLL support and presence of `exec-target.t`. Missing target or SQPOLL support skips.

Risks/test signals: if close task_work is delayed, `execve` can fail because the executable is still open for write. Failures are child nonzero exit, open/close CQE errors, or target lookup failure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sqpoll-exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sqpoll-exit-hang.c -->
# sources/test-tools/liburing/test/sqpoll-exit-hang.c

Purpose: tests that process exit with SQPOLL and a request polling the ring fd itself does not hang due to circular references.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `IORING_FEAT_SQPOLL_NONFIXED`, `io_uring_prep_poll_add`, ring fd polling, and `mtime_since_now`.

Control flow: creates an SQPOLL ring with short idle timeout, skips if setup unsupported or lacks nonfixed SQPOLL, queues a poll on `ring.ring_fd`, submits it, sleeps for about one second, and returns without explicit ring teardown.

State/persistence behavior: kernel ring fd and pending poll request form the reference cycle under test. No filesystem state.

Dependencies/integration: may require root for SQPOLL on older kernels. Feature absence leads to skip-style success.

Risks/test signals: a bad kernel may hang on process exit or ring teardown. The program has minimal runtime assertions because liveness at exit is the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sqpoll-exit-hang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sqpoll-sleep.c -->
# sources/test-tools/liburing/test/sqpoll-sleep.c

Purpose: verifies an SQPOLL thread goes idle around the configured timeout and sets `IORING_SQ_NEED_WAKEUP`.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `sq_thread_idle`, `IORING_SQ_NEED_WAKEUP`, `IO_URING_READ_ONCE`, `io_uring_prep_nop`, and `mtime_since_now`.

Control flow: creates an SQPOLL ring with idle 100 ms, submits and reaps a NOP, then polls `*ring.sq.kflags` until `IORING_SQ_NEED_WAKEUP` appears or one second elapses. It requires wakeup timing between roughly 90 and 110 ms.

State/persistence behavior: state is SQPOLL kthread idle/wakeup flag. No external state.

Dependencies/integration: SQPOLL setup may require privileges; unsupported setup skips. Timing depends on scheduler behavior.

Risks/test signals: catches missing wakeup flag or significantly wrong idle timing, but may be sensitive to overloaded systems.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sqpoll-sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sqwait.c -->
# sources/test-tools/liburing/test/sqwait.c

Purpose: verifies `io_uring_sqring_wait()` lets applications obtain a new SQE after an SQPOLL ring becomes full under sustained I/O.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `io_uring_sqring_wait`, `io_uring_get_sqe`, `io_uring_prep_read`, direct `O_DIRECT` reads, aligned iovecs, and bounded completion reaping.

Control flow: creates or uses a 256 MiB file, allocates 256 aligned buffers, initializes an 8-entry SQPOLL ring, opens the file with direct I/O, and loops 10,000 read submissions. When `get_sqe` returns NULL, it calls `io_uring_sqring_wait()` and immediately requires a new SQE to be available, while `reap()` keeps in-flight operations below half the buffer pool.

State/persistence behavior: temporary file is created/unlinked when no argv file is supplied. The primary state is SQ occupancy under SQPOLL and in-flight read count.

Dependencies/integration: needs SQPOLL, direct I/O support, and sufficient file size/access. `-EINVAL` from sqring wait or setup skips.

Risks/test signals: detects sqring wait not freeing SQEs, read CQE errors, direct I/O setup failures, and leaks/cleanup issues around many in-flight reads.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sqwait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/statx.c -->
# sources/test-tools/liburing/test/statx.c

Purpose: validates io_uring `statx` against the raw `statx` syscall and checks invalid path/buffer error handling.

Important APIs/types/functions: `io_uring_prep_statx`, `struct statx`, raw `syscall(__NR_statx)`, `AT_EMPTY_PATH`, `STATX_ALL`, invalid pointer tests, and helper `t_create_file`.

Control flow: creates or uses a file, submits io_uring statx by path and compares the resulting `struct statx` with a synchronous syscall. It then checks invalid path pointer and invalid output buffer both return `-EFAULT`, and checks fd-based `AT_EMPTY_PATH` statx matches the syscall.

State/persistence behavior: creates `/tmp/.statx` when no path is supplied and unlinks it at the end. Otherwise only metadata is read.

Dependencies/integration: depends on kernel statx syscall and io_uring statx opcode. `-EINVAL` or ENOSYS-compatible paths are treated as unsupported skips.

Risks/test signals: detects metadata mismatch, wrong invalid-pointer errno, unsupported opcode behavior, and cleanup issues for the temporary file.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/statx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/stdout.c -->
# sources/test-tools/liburing/test/stdout.c

Purpose: checks writes to stdout and fixed-buffer writes to stdout/pipe through io_uring complete with correct byte counts and data.

Important APIs/types/functions: `io_uring_prep_writev`, `io_uring_prep_write_fixed`, `io_uring_prep_readv`, `io_uring_register_buffers`, `io_uring_unregister_buffers`, `STDOUT_FILENO`, pipes, and aligned buffers.

Control flow: `test_stdout_io()` submits a normal writev to stdout. `test_stdout_io_fixed()` registers one aligned buffer and writes it fixed to stdout. `test_pipe_io_fixed()` registers a fixed buffer, writes it to a pipe, concurrently reads from the pipe, and verifies both completions and read payload.

State/persistence behavior: stdout receives test text. Pipe data and registered buffer state are transient.

Dependencies/integration: depends on stdout being writable and fixed-buffer registration support.

Risks/test signals: detects stdout/pipe write errors, wrong byte counts, fixed-buffer registration failures, and pipe read payload mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/stdout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/submit-and-wait.c -->
# sources/test-tools/liburing/test/submit-and-wait.c

Purpose: verifies `io_uring_submit_and_wait_timeout()` returns promptly after timeout and does not wait twice when requested CQE count exceeds submitted work.

Important APIs/types/functions: `io_uring_submit_and_wait_timeout`, `io_uring_prep_nop`, `struct __kernel_timespec`, `mtime_since_now`, and `io_uring_queue_init_params`.

Control flow: queues one NOP, calls submit-and-wait-timeout asking for two CQEs with a one-second timeout, and verifies the call does not exceed roughly 1.2 seconds.

State/persistence behavior: only ring SQ/CQ state and a wall-clock measurement are used.

Dependencies/integration: tests liburing/kernel enter timeout semantics for partial completion.

Risks/test signals: catches double-wait behavior or unexpected negative return. It is timing-sensitive on very slow systems.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/submit-and-wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/submit-link-fail.c -->
# sources/test-tools/liburing/test/submit-link-fail.c

Purpose: tests linked requests that fail during submission/preparation and verifies later linked requests are canceled or preserved according to link/drain/hardlink rules.

Important APIs/types/functions: `IOSQE_IO_LINK`, `IOSQE_IO_HARDLINK`, `IOSQE_IO_DRAIN`, invalid fd reads with bad `ioprio`, pipe-backed drain blocker, `io_uring_submit`, and CQE result checks.

Control flow: `test_underprep_fail()` creates a fresh ring, optionally queues a draining pipe read, queues a link chain where one request is deliberately invalid, submits, tolerates old early-under-submit behavior, otherwise unblocks drain and verifies the drain CQE, failing request CQE, and canceled linked requests. `main()` runs small link sizes/failure indexes across hardlink, drain, and link-last combinations.

State/persistence behavior: only ring state and pipe fds are used. Each scenario uses a new ring because failures can leave dirty queue state.

Dependencies/integration: covers kernel linked-submit error handling and CQE cancellation semantics.

Risks/test signals: catches wrong submit counts, invalid failed-request result, missing cancellations, drain misuse, or kernel fault conditions from partially prepared linked SQEs.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/submit-link-fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/submit-reuse.c -->
# sources/test-tools/liburing/test/submit-reuse.c

Purpose: regression for submit-stable behavior where the kernel must not reuse caller iovec storage after submission, even when reads are punted to blocking context.

Important APIs/types/functions: `IORING_FEAT_SUBMIT_STABLE`, `io_uring_prep_readv`, `IOSQE_ASYNC`, `posix_fadvise(POSIX_FADV_DONTNEED)`, stack iovec arrays, background flusher thread, and `mtime_since_now`.

Control flow: `test_reuse()` initializes a ring and checks `SUBMIT_STABLE`, creates two files, starts a flusher thread that repeatedly evicts file pages, then for up to 1000 iterations or five seconds queues reads from both files. `prep()` constructs either one iovec or 16 split iovecs on the stack, submits, and immediately overwrites `iov_base` with NULL. `wait_nr()` requires nonnegative completions.

State/persistence behavior: creates temporary files `.reuse.1` and `.reuse.2` unless a path is supplied. The key state is the lifetime of submitted iovec memory versus kernel-side copied state.

Dependencies/integration: needs `IORING_FEAT_SUBMIT_STABLE` for meaningful coverage; otherwise it skips after first scenario. Uses filesystem cache eviction and pthreads to increase async/blocking likelihood.

Risks/test signals: a bad kernel may return `-EFAULT` or other negative CQEs after the iovecs are nulled. Timing and cache behavior affect how much async pressure is achieved.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/submit-reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/symlink.c -->
# sources/test-tools/liburing/test/symlink.c

Purpose: validates io_uring `symlinkat` operation success and common error cases.

Important APIs/types/functions: `io_uring_prep_symlinkat`, `io_uring_wait_cqes`, `readlink`, `unlinkat`, `AT_FDCWD`, and invalid user pointers.

Control flow: creates a symlink from a fixed target string to a fixed link name through io_uring, verifies link contents with `readlink`, then checks duplicate link returns `-EEXIST`, missing parent path returns `-ENOENT`, bad newname pointer returns `-EFAULT`, and bad oldname pointer returns `-EFAULT`.

State/persistence behavior: creates one symlink in the current directory and removes it on exit/error. No target file is required because symlink contents are textual.

Dependencies/integration: depends on symlinkat opcode support and filesystem symlink support. `-EBADF` or `-EINVAL` on initial operation is treated as unsupported.

Risks/test signals: detects wrong errno mapping, bad symlink contents, missing cleanup, or unsupported opcode behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/sync-cancel.c -->
# sources/test-tools/liburing/test/sync-cancel.c

Purpose: tests `io_uring_register_sync_cancel()` for user-data cancellation, fd cancellation, cancel-all, async/sync reads, per-op cancellation, and timeout behavior.

Important APIs/types/functions: `io_uring_sync_cancel_reg`, `io_uring_register_sync_cancel`, `IORING_ASYNC_CANCEL_ALL`, `IORING_ASYNC_CANCEL_FD`, `IORING_ASYNC_CANCEL_OP`, `IORING_OP_READ`, pipe reads, and `IOSQE_ASYNC`.

Control flow: `test_sync_cancel()` queues one or four blocking pipe reads, configures cancel by user_data or fd and optional all flag, calls sync cancel, then waits for all CQEs to have negative results. `test_sync_cancel_timeout()` queues a read and calls per-op cancel with a tiny timeout, accepting async races where cancel succeeds or times out. `main()` runs a matrix across sync/async, all/single, address/fd, and per-op timeout cases.

State/persistence behavior: pipe fds and pending read requests are the mutable state. Feature flags `no_sync_cancel` and `no_sync_cancel_op` record unsupported kernels.

Dependencies/integration: requires sync-cancel registration support; older kernels skip on `-EINVAL`.

Risks/test signals: catches uncanceled reads, nonnegative CQEs, wrong timeout/cancel errno, missing per-op support handling, and races around async cancellation posting completions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/sync-cancel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/task-restrict.c -->
# sources/test-tools/liburing/test/task-restrict.c

Purpose: tests per-task io_uring restrictions registered with fd `-1`, including SQE opcode restrictions, fork inheritance, double-registration rejection, and register-op restrictions.

Important APIs/types/functions: raw `__sys_io_uring_register(-1, IORING_REGISTER_RESTRICTIONS, ...)`, `struct io_uring_restriction`, `IORING_RESTRICTION_SQE_OP`, `IORING_RESTRICTION_REGISTER_OP`, `PR_SET_NO_NEW_PRIVS`, fork/wait, and expected `-EACCES`/`-EPERM`.

Control flow: each test runs in a child because restrictions cannot be removed. `test_task_restrict_sqe_op()` allows only NOP and verifies READ is denied. `test_task_restrict_fork_inherit()` registers NOP/WRITE allowance, forks a grandchild, and verifies READ denial there. `test_task_restrict_double_register()` expects a second registration to fail with `-EPERM`. `test_task_restrict_register_op()` allows file registration and verifies buffer registration is denied.

State/persistence behavior: restrictions are per-task kernel state inherited through fork. No persistent files are created.

Dependencies/integration: requires per-task restriction support and `no_new_privs`, similar to seccomp-style constraints. Unsupported `-EINVAL`/`-EBADF` skips.

Risks/test signals: catches missing inheritance, over-permissive SQE/register operations, incorrect double-registration errno, or failure to apply restrictions to newly created rings.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/task-restrict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/teardowns.c -->
# sources/test-tools/liburing/test/teardowns.c

Purpose: stress test concurrent ring setup teardown under memory pressure or allocation failure paths.

Important APIs/types/functions: `io_uring_queue_init`, fork/wait, `close`, expected `-ENOMEM`, and child exit status aggregation.

Control flow: `main()` forks 12 children. Each child runs `loop()`, attempting 100 ring initializations with depth `0xa4`; successful returns are closed immediately, and negative results other than `-ENOMEM` increment an error count. Parent waits for all children and returns the number of children reporting unexpected errors.

State/persistence behavior: state is transient kernel ring allocation/teardown state across concurrent processes. No external files or fds persist beyond each child.

Dependencies/integration: tests setup error handling and cleanup under parallelism.

Risks/test signals: detects unexpected setup errors, teardown leaks, or crashes during concurrent failed/successful ring creation. It intentionally tolerates `-ENOMEM`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/teardowns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/test.h -->
# sources/test-tools/liburing/test/test.h

Purpose: shared test configuration header defining common io_uring setup flag combinations for tests that iterate over ring modes.

Important APIs/types/functions: `io_uring_test_config`, `io_uring_test_configs`, `FOR_ALL_TEST_CONFIGS`, `IORING_GET_TEST_CONFIG_FLAGS()`, `IORING_GET_TEST_CONFIG_DESCRIPTION()`, and setup flags `IORING_SETUP_SQE128`, `IORING_SETUP_CQE32`, and `IORING_SETUP_SQ_REWIND`.

Control flow: no runtime control flow beyond macro expansion. Consumers use `FOR_ALL_TEST_CONFIGS` to iterate the static array and retrieve flags/descriptions by loop index `i`.

State/persistence behavior: contains a static header-local array marked unused to avoid compiler warnings. No mutable persistent state.

Dependencies/integration: depends on liburing setup flag definitions being visible before inclusion. The `extern "C"` guard supports C++ tests.

Risks/test signals: macro design assumes the caller's loop variable is named `i`; misuse outside the provided loop macro can break compilation or read the wrong entry.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/test.h -->
