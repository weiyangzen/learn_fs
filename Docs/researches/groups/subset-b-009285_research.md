<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-reg.c -->
## sources/test-tools/liburing/test/eventfd-reg.c

Purpose: verifies eventfd registration lifetime rules on a single io_uring instance.

Important APIs/types/functions: `io_uring_queue_init_params`, `eventfd`, `io_uring_register_eventfd`, `io_uring_unregister_eventfd`, and the `T_EXIT_*` test result constants.

Control flow: `main` creates one ring and two eventfds, registers the first eventfd, verifies that a second registration fails with `-EBUSY`, unregisters the first eventfd, then performs 100 register/unregister cycles to catch reference-counting and repeated-state bugs.

State and persistence behavior: the ring keeps at most one registered completion eventfd. The test creates kernel eventfd state and closes descriptors before exit, but it does not call `io_uring_queue_exit`.

Dependencies and integration points: depends on eventfd support, liburing registration helpers, and normal test skip behavior when invoked with extra arguments.

Risks: leaks are possible on early failure because cleanup is minimal. The important regression risk is accepting duplicate eventfd registrations or failing to fully clear ring eventfd state.

Test signals: pass means duplicate registration returns `-EBUSY` and repeated register/unregister remains stable.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-ring.c -->
## sources/test-tools/liburing/test/eventfd-ring.c

Purpose: checks that two rings can register different eventfds and poll each other's completion notifications without recursive or cross-ring confusion.

Important APIs/types/functions: `test(flags)`, `io_uring_queue_init_params`, `io_uring_queue_init`, `io_uring_register_eventfd`, `io_uring_prep_poll_add`, `io_uring_prep_nop`, and feature flag `IORING_FEAT_CUR_PERSONALITY`.

Control flow: `test` creates two rings, registers separate eventfds, queues a poll in each ring against the other ring's eventfd, submits both polls, then submits a NOP on the first ring to generate a completion signal. `main` runs the scenario once normally and once with `IORING_SETUP_DEFER_TASKRUN | IORING_SETUP_SINGLE_ISSUER`.

State and persistence behavior: each ring owns its own registered eventfd and pending poll SQE. The test intentionally does not reap CQEs or unregister eventfds, relying on process teardown.

Dependencies and integration points: exercises completion eventfd signaling, poll readiness, and defer-taskrun/single-issuer behavior.

Risks: because the test exits immediately after the triggering NOP submit, it mainly catches setup-time and obvious notification bugs, not detailed CQE ordering. Unsupported ring flags are treated as skip.

Test signals: pass indicates independent eventfd registration across rings and successful submissions in both normal and defer-taskrun modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd.c -->
## sources/test-tools/liburing/test/eventfd.c

Purpose: validates eventfd-triggered completions and linked poll/read behavior on a ring with a registered eventfd.

Important APIs/types/functions: `io_uring_register_eventfd`, `io_uring_prep_poll_add`, `io_uring_prep_readv`, `io_uring_prep_nop`, `IOSQE_IO_LINK`, `POLLIN`, and `IORING_FEAT_CUR_PERSONALITY`.

Control flow: the test creates a ring, registers an eventfd, links a poll on the eventfd to a read of the same eventfd, then submits a NOP to trigger eventfd notification. It waits for three completions and validates the poll result, the eventfd read size, and the NOP success.

State and persistence behavior: eventfd counter state is consumed by the linked read. CQEs are acknowledged as they arrive; descriptor cleanup is left mostly to process exit.

Dependencies and integration points: integrates eventfd notification with poll, readv, linked SQEs, and completion delivery.

Risks: ordering can vary, so validation is keyed by `user_data`. Kernels without current-personality feature support skip the test.

Test signals: pass means eventfd notification wakes poll, the linked read consumes exactly one eventfd value, and unrelated NOP completion still appears.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/evfd-short-read.c -->
## sources/test-tools/liburing/test/evfd-short-read.c

Purpose: regression test for eventfd short-read handling when a read buffer is larger than one eventfd counter value.

Important APIs/types/functions: `eventfd(EFD_NONBLOCK)`, `io_uring_prep_read`, `io_uring_wait_cqe`, `sigaction`, `alarm`, and the timeout handler `sig_alrm`.

Control flow: the test submits a read for two `uint64_t` eventfd values, waits briefly, writes one eventfd value, then waits for the CQE. A one-second alarm fails the test if the kernel incorrectly waits for the full larger buffer.

State and persistence behavior: eventfd state is a single counter increment. The ring has one pending read and the eventfd is closed after completion.

Dependencies and integration points: relies on anonymous-inode eventfd semantics and io_uring read retry/short-read logic.

Risks: the test does not inspect `cqe->res`, so its primary signal is absence of hang rather than exact returned byte count. Timing is guarded by `alarm`.

Test signals: pass indicates io_uring completes a partial eventfd read once one event is available instead of treating eventfd like a regular file requiring the full buffer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/evfd-short-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/evloop.c -->
## sources/test-tools/liburing/test/evloop.c

Purpose: guards against recursive completion generation when a ring polls its own registered completion eventfd with multishot poll.

Important APIs/types/functions: `io_uring_register_eventfd`, `io_uring_prep_poll_multishot`, `io_uring_prep_nop`, `io_uring_wait_cqe`, `io_uring_peek_cqe`, and `IORING_CQE_F_MORE`-style multishot behavior.

Control flow: `main` creates a ring and eventfd, registers the eventfd for completions, submits a multishot poll on that same eventfd, then submits a NOP. It consumes two CQEs and asserts no third CQE is immediately available.

State and persistence behavior: the ring's completion eventfd can trigger the ring's own poll request. The expected stable state is no runaway loop of additional completion notifications.

Dependencies and integration points: exercises eventfd notification, multishot polling, and CQ overflow avoidance.

Risks: older kernels may only stop recursion at overflow while newer kernels abort earlier. The test is sensitive to unexpected extra CQE production.

Test signals: pass means self-polling a registered eventfd does not recursively create unbounded completion events.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/evloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/exec-target.c -->
## sources/test-tools/liburing/test/exec-target.c

Purpose: minimal executable target used by other tests that need a known successful `exec` destination.

Important APIs/types/functions: only `main`.

Control flow: `main` returns zero unconditionally.

State and persistence behavior: no state is created, read, or persisted.

Dependencies and integration points: integrates with tests that fork/exec another binary and need a stable target whose success is independent of io_uring behavior.

Risks: this file provides no direct io_uring signal. Its usefulness depends on external tests invoking it correctly.

Test signals: process exit status zero indicates the exec target ran.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/exec-target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/exit-no-cleanup.c -->
## sources/test-tools/liburing/test/exit-no-cleanup.c

Purpose: stress test for process exit while many threads own rings with pending io-wq-backed reads and no explicit cleanup.

Important APIs/types/functions: `pthread_create`, `pthread_barrier_t`, `sem_t`, `pipe`, `io_uring_queue_init`, `io_uring_prep_read`, `io_uring_submit_and_wait`, and sanitizer guard `CONFIG_USE_SANITIZER`.

Control flow: when sanitizer builds are not enabled, `main` creates one thread per CPU, each thread creates a ring and loops reading from a shared pipe. The parent writes one notification per CPU, waits until each thread reports a completed read, then calls `exit` without joining threads or exiting rings.

State and persistence behavior: global thread array, barrier, semaphore, and pipe descriptors coordinate worker startup and completion. The deliberate persistence behavior is leaked live rings and threads at process exit.

Dependencies and integration points: targets io-wq cleanup, task exit, pthread interaction, and ASAN-unsafe timing.

Risks: highly timing and CPU-count dependent. It is skipped under sanitizer builds to avoid known unrelated cleanup crashes.

Test signals: pass is a clean process exit after leaving active rings uncleaned.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/exit-no-cleanup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fadvise.c -->
## sources/test-tools/liburing/test/fadvise.c

Purpose: basic `IORING_OP_FADVISE` coverage with cache-drop and prefetch advisory patterns.

Important APIs/types/functions: `do_fadvise`, `do_read`, `test_fadvise`, `io_uring_prep_fadvise`, `POSIX_FADV_DONTNEED`, `POSIX_FADV_WILLNEED`, `utime_since_now`, and `t_create_file`.

Control flow: the test opens a supplied or temporary file, measures an initial cached read, submits DONTNEED, reads again, submits DONTNEED then WILLNEED, and reads a third time. It repeats up to 100 loops but exits after at least ten good timing iterations with no bad samples.

State and persistence behavior: temporary `.fadvise.tmp` is created when no path is supplied and removed on exit. The ring has one fadvise SQE per advisory call.

Dependencies and integration points: depends on filesystem advisory behavior and liburing's fadvise prep wrapper.

Risks: timing comparisons are explicitly disabled as hard failure because cache behavior is noisy. Unsupported fadvise returns `-EINVAL` or `-EBADF` and skips.

Test signals: strong signal is successful fadvise CQEs; timing is informational only.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fadvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fallocate.c -->
## sources/test-tools/liburing/test/fallocate.c

Purpose: validates io_uring fallocate, linked fallocate+fsync, and file-size-limit error propagation.

Important APIs/types/functions: `test_fallocate`, `test_fallocate_fsync`, `test_fallocate_rlimit`, `io_uring_prep_fallocate`, `io_uring_prep_fsync`, `IOSQE_IO_LINK`, `RLIMIT_FSIZE`, and `SIGXFSZ`.

Control flow: `main` installs a `SIGXFSZ` handler, creates a ring, checks a 128 KiB fallocate updates file size, checks linked fallocate plus fsync both complete successfully, then lowers `RLIMIT_FSIZE` and expects a larger fallocate to fail with `-EFBIG`.

State and persistence behavior: each scenario uses an unlinked `mkstemp` file. `no_fallocate` suppresses dependent checks after unsupported fallocate detection.

Dependencies and integration points: exercises file allocation, linked SQE sequencing, fsync, signal/rlimit interaction, and CQE error mapping.

Risks: mutates process file-size rlimit without restoring it. Unsupported filesystems or kernels return skip via `-EINVAL` or `-EOPNOTSUPP`.

Test signals: pass means fallocate success updates `st_size`, linked fsync is ordered, and rlimit failure is surfaced as `-EFBIG`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fallocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fc2a85cb02ef.c -->
## sources/test-tools/liburing/test/fc2a85cb02ef.c

Purpose: syzkaller-derived fault-injection regression for io_uring registration under allocation/futex failure conditions.

Important APIs/types/functions: `write_file`, `setup_fault`, `inject_fault`, raw `__sys_io_uring_setup`, raw `__sys_io_uring_register`, `/proc/thread-self/fail-nth`, and debugfs fault knobs.

Control flow: the test maps a fixed userspace area, enables relevant fault injection controls, initializes a large `io_uring_params` blob in mapped memory, sets up a ring through the raw syscall, opens an unusual socket, injects the next failure point, and calls raw io_uring register opcode 2 with one fd.

State and persistence behavior: depends on kernel debugfs fault-injection state and writes to system fault-control files. It leaves most syscall results unchecked because the regression is crash/leak oriented.

Dependencies and integration points: requires fail-slab/fail-futex/fail-page-alloc support and permission to write debugfs/proc fault controls.

Risks: environment-specific and privileged; skipped when fault injection is unavailable. It intentionally uses fixed addresses and raw syscalls.

Test signals: pass means the crafted failing register path returns without crashing the process/kernel.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fc2a85cb02ef.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fd-install.c -->
## sources/test-tools/liburing/test/fd-install.c

Purpose: tests installing fixed/direct descriptors from a ring's fixed-file table into the regular process fd table.

Important APIs/types/functions: `test_flags`, `test_linked`, `test_not_fixed`, `test_creds`, `test_ring_exit`, `io_uring_prep_fixed_fd_install`, `io_uring_register_files`, `IORING_FIXED_FD_NO_CLOEXEC`, `IOSQE_FIXED_FILE`, `IOSQE_ASYNC`, and linked SQEs.

Control flow: scenarios register pipe fds as fixed files, verify invalid install flags return `-EINVAL`, verify accepted flags produce a real fd, check linked NOP+install completion, check install without fixed-file context, and run variants with async execution and ring teardown interactions.

State and persistence behavior: registered file tables hold references to pipe fds while install operations create ordinary process fds that must be closed separately. The global `no_fd_install` records unsupported kernel behavior.

Dependencies and integration points: integrates fixed-file registration with fd allocation, close-on-exec flag handling, linked SQEs, credentials, and ring lifetime.

Risks: fd leaks on early failure are the main local risk. Kernel support is feature-dependent and may skip on `-EINVAL`.

Test signals: pass means direct descriptors can be safely materialized as normal fds and invalid flag/fixedness combinations fail as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fd-install.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fd-pass.c -->
## sources/test-tools/liburing/test/fd-pass.c

Purpose: verifies `MSG_RING` fixed-file passing between io_uring instances.

Important APIs/types/functions: `verify_fixed_read`, `test`, `io_uring_prep_msg_ring_fd`, `io_uring_prep_openat_direct`, `io_uring_prep_read`, `io_uring_prep_close_direct`, `IORING_FILE_INDEX_ALLOC`, `IOSQE_FIXED_FILE`, and `IORING_SETUP_DEFER_TASKRUN | IORING_SETUP_SINGLE_ISSUER`.

Control flow: `main` creates a patterned file, then runs source/target fixed-slot combinations in normal and defer-taskrun rings. Each scenario opens the file into a direct slot in the source ring, sends it to the destination ring, verifies the destination can read the pattern, closes the source slot, verifies source access fails, and confirms destination access still works.

State and persistence behavior: two rings own independent fixed-file tables. Passing duplicates the underlying file reference into the destination table; source close must not invalidate destination state.

Dependencies and integration points: exercises ring-to-ring messaging, fixed-file allocation, direct close, and data verification.

Risks: unsupported `MSG_RING` fd passing sets `no_fd_pass` and skips. Correctness hinges on reference ownership and slot allocation.

Test signals: pass proves fixed-file transfer preserves file contents and lifetime across rings.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fd-pass.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fdinfo-sqpoll.c -->
## sources/test-tools/liburing/test/fdinfo-sqpoll.c

Purpose: races `/proc/self/fdinfo/<ring_fd>` reads against SQPOLL ring teardown and signal interruption.

Important APIs/types/functions: `struct data`, `fdinfo_read`, `__test`, `test`, `t_create_ring(... IORING_SETUP_SQPOLL)`, `pthread_barrier_t`, `fork`, `kill`, and `waitpid`.

Control flow: each iteration forks. The child creates an SQPOLL ring, starts a thread continuously reading ring fdinfo, waits a random short interval, signals the thread to stop, joins it, and exits. The parent may send SIGINT during the child's fdinfo activity, then waits. `main` repeats this 1000 times.

State and persistence behavior: shared `done` flag and barrier coordinate the fdinfo reader. Ring fdinfo is opened once and read repeatedly while the ring may be torn down.

Dependencies and integration points: depends on procfs fdinfo, SQPOLL permission, pthreads, and signal/process cleanup.

Risks: nondeterministic race coverage; it mainly catches kernel crashes, hangs, or fdinfo read errors.

Test signals: pass means repeated fdinfo reads are stable during SQPOLL exit races.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fdinfo-sqpoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fdinfo.c -->
## sources/test-tools/liburing/test/fdinfo.c

Purpose: broad regression test that performs io_uring read/write workloads while repeatedly reading `/proc/self/fdinfo` for the ring.

Important APIs/types/functions: `fdinfo_read`, `__test_io`, `test_io`, `has_nonvec_read`, `test_eventfd_read`, `io_uring_get_sqe128`, `io_uring_prep_nop128`, `t_register_buffers`, `io_uring_register_files`, `IORING_SETUP_SQPOLL`, and `IORING_SETUP_SQE_MIXED`.

Control flow: the main matrix creates a test file and buffers, probes non-vectored read support, then runs read/write combinations across buffered/direct IO, SQPOLL fixed files, registered buffers, mixed SQE sizes, and non-vectored operations. Each workload flushes SQ state, reads fdinfo before and during submission, and validates completions. It also tests eventfd reads under normal, defer-taskrun, and SQPOLL rings.

State and persistence behavior: global `vecs`, `no_read`, and `warned` track buffers and feature skips. Temporary files are unlinked after the matrix.

Dependencies and integration points: combines procfs fdinfo rendering with active ring state, fixed resources, buffer selection-like paths, and eventfd IO.

Risks: large feature matrix can skip selectively. fdinfo reads are diagnostic but must not perturb SQ/CQ state.

Test signals: pass means fdinfo inspection is safe while varied io_uring workloads are live.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fdinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fifo-futex-poll.c -->
## sources/test-tools/liburing/test/fifo-futex-poll.c

Purpose: ensures an inline-failing futex wait does not poison later fixed-file poll on a FIFO.

Important APIs/types/functions: `mkfifo`, `io_uring_prep_futex_wait`, `io_uring_register_files`, `io_uring_prep_poll_add`, `IOSQE_FIXED_FILE`, `FUTEX_BITSET_MATCH_ANY`, and `FUTEX2_SIZE_U32`.

Control flow: the test creates and opens a FIFO, initializes a ring, submits an invalid futex wait with a null address and expects `-EFAULT` or skips on `-EINVAL`. It then registers the FIFO fd, submits a fixed-file poll for `POLLIN`, writes to the FIFO, and waits for the poll completion.

State and persistence behavior: temporary `fifo` filesystem node and fifo fd are cleaned up; the ring holds one registered file during poll.

Dependencies and integration points: combines futex opcode validation with double-waitqueue FIFO poll and fixed-file registration.

Risks: stale local `fifo` path could interfere. Unsupported futex opcode maps to skip.

Test signals: pass means a failed futex SQE does not corrupt later poll request setup or completion.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fifo-futex-poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fifo-nonblock-read.c -->
## sources/test-tools/liburing/test/fifo-nonblock-read.c

Purpose: regression test for retrying io_uring reads on nonblocking pipe/FIFO-style fds instead of returning immediate `-EAGAIN`.

Important APIs/types/functions: `pipe`, `t_set_nonblock`, `io_uring_prep_read`, `io_uring_submit`, `io_uring_wait_cqe`.

Control flow: a ring and pipe are created, the read end is made nonblocking, and a read SQE is submitted before data exists. After a short sleep, the write end receives data, and the test waits for a CQE whose result must be nonnegative.

State and persistence behavior: the pipe's nonblocking flag and pending read request are the relevant state. The ring is exited at the end.

Dependencies and integration points: exercises io-wq retry logic for nonblocking read endpoints.

Risks: the test accepts any nonnegative result and does not verify exact byte count. It assumes the delayed write races with the pending read as intended.

Test signals: pass means the kernel retries the operation until data arrives rather than reporting `-EAGAIN` to userspace.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fifo-nonblock-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-alloc-range-hint.c -->
## sources/test-tools/liburing/test/file-alloc-range-hint.c

Purpose: verifies auto-allocated fixed-file slots honor a configured allocation range even after operations outside the range update allocation hints.

Important APIs/types/functions: `file_update_alloc`, `test_hint_below_range`, `test_hint_above_range`, `io_uring_register_files_sparse`, `io_uring_register_file_alloc_range`, `io_uring_register_files_update`, and `IORING_FILE_INDEX_ALLOC`.

Control flow: the below-range scenario creates a sparse 20-slot table, limits auto-allocation to `[10,20)`, installs/removes a file at slot 2, then auto-allocates another fd and checks the returned slot remains inside range. The above-range scenario configures `[0,10)`, installs at slot 15, and checks auto-allocation still stays inside `[0,10)`.

State and persistence behavior: sparse fixed-file tables and kernel allocation hints are the core state. Pipe fds are closed and rings exited per scenario.

Dependencies and integration points: targets fixed-file sparse tables, allocation ranges, and userspace writeback of allocated slot indexes.

Risks: unsupported sparse registration skips. Failure indicates allocation hint corruption can escape configured bounds.

Test signals: pass means both below-range and above-range hint perturbations still allocate within the configured range.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-alloc-range-hint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-exit-unreg.c -->
## sources/test-tools/liburing/test/file-exit-unreg.c

Purpose: checks that exiting a defer-taskrun ring with tagged registered files does not hit file unregistration/task-work locking bugs.

Important APIs/types/functions: `io_uring_queue_init` with `IORING_SETUP_SINGLE_ISSUER | IORING_SETUP_DEFER_TASKRUN`, `io_uring_register_files_tags`, `pipe`, and `io_uring_queue_exit`.

Control flow: the test creates a pipe, initializes a defer-taskrun single-issuer ring, registers both pipe fds with two tags, exits the ring, sleeps briefly, and returns success. Unsupported ring flags or tagged registration return skip.

State and persistence behavior: registered files carry tags, and unregistration occurs implicitly during `io_uring_queue_exit`.

Dependencies and integration points: integrates tagged fixed-file registration with deferred task-work cleanup.

Risks: no explicit CQE workload is submitted; this is a lockdep/lifetime sentinel rather than functional IO validation. Pipe fds are not explicitly closed.

Test signals: pass is no failure, hang, or lockdep-visible issue during ring exit after tagged file registration.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-exit-unreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-register.c -->
## sources/test-tools/liburing/test/file-register.c

Purpose: comprehensive fixed-file registration suite covering valid/invalid tables, updates, sparse sets, huge tables, allocation ranges, SCM-accounted fds, partial failure cleanup, and defer-taskrun interactions.

Important APIs/types/functions: `open_files`, `close_files`, `test_basic`, `test_sparse`, `test_additions`, `test_removals`, `test_grow`, `test_shrink`, `test_huge`, `test_skip`, `test_sparse_updates`, `test_fixed_removal_ordering`, `test_mixed_af_unix`, `test_partial_register_fail`, `test_file_alloc_ranges`, `io_uring_register_files`, `io_uring_register_files_update`, `io_uring_register_files_sparse`, `io_uring_register_file_alloc_range`, and `io_uring_prep_files_update`.

Control flow: `main` creates one base ring and runs ordered registration scenarios: normal registration, expected invalid fd failure, large table registration, sparse-table support probing, add/remove/replace/grow/shrink updates, zero-initialized sparse table fill, huge sparse table IO verification, skip marker behavior, full sparse update loops, fixed-file removal while linked IO is pending, mixed pipe/AF_UNIX registration, partial-register failure cleanup, allocation-range bounds, and optional defer-taskrun read/unregister behavior.

State and persistence behavior: many `.reg.*` and `.add.*` files are created and unlinked. Fixed-file tables hold references after original fds are closed. `no_update` gates update-dependent tests when sparse registration is unsupported.

Dependencies and integration points: central integration test for liburing fixed files, direct IO via fixed indexes, file allocator ranges, resource limits, sockets, pipes, and ring cleanup.

Risks: broad coverage means early failures can leave temporary files or descriptors. Some scenarios depend on `RLIMIT_NOFILE`, sparse-file-table kernel support, and SCM accounting behavior.

Test signals: pass is strong evidence that fixed-file table registration and update semantics are correct across normal and edge-case lifetimes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-register.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-update.c -->
## sources/test-tools/liburing/test/file-update.c

Purpose: validates fixed-file table updates across multiple rings and via `IORING_OP_FILES_UPDATE`.

Important APIs/types/functions: `test_update_multiring`, `test_sqe_update`, `test_update_no_table`, `io_uring_register_files`, `io_uring_register_files_update`, `io_uring_prep_files_update`, and `t_create_ring`.

Control flow: `main` creates three rings, registers the same initial fds into all three, updates all tables to new fds with and without explicit unregister, then submits a files-update SQE replacing ten entries with `-1`. It also tests a malformed update offset against a small table and accepts known error results.

State and persistence behavior: temporary `.reg.*` and `.add.*` files back the fd arrays and are cleaned after each scenario. Multi-ring fixed-file tables independently hold references to the same fd values.

Dependencies and integration points: exercises synchronous register update and asynchronous SQE-based files-update paths.

Risks: shared fd arrays across rings make ownership/refcount behavior important. Unsupported `IORING_OP_FILES_UPDATE` returns skip.

Test signals: pass means multi-ring updates, table removal, and invalid update offsets behave predictably.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-verify.c -->
## sources/test-tools/liburing/test/file-verify.c

Purpose: large data-integrity test for buffered and direct reads across vectored, fixed-buffer, provided-buffer, and truncation/short-read cases.

Important APIs/types/functions: `verify_buf`, `test_truncate`, `do_punch`, `provide_buffers`, `test`, `fill_pattern`, `io_uring_prep_read`, `io_uring_prep_readv`, `io_uring_prep_read_fixed`, `io_uring_prep_provide_buffers`, `IOSQE_BUFFER_SELECT`, and `t_register_buffers`.

Control flow: `main` creates or uses a 128 MiB file, fills it with offset-derived integer patterns, then runs buffered and O_DIRECT read passes with plain buffers, registered buffers, provided buffers, large/small iovec arrays, and truncation-like short reads near file end. Each read batch validates returned bytes against expected file offsets.

State and persistence behavior: the test file is filled with deterministic content. `posix_fadvise(... DONTNEED)` creates cache holes to force incremental buffered read paths. Registered buffers are unregistered after each pass.

Dependencies and integration points: touches page cache behavior, O_DIRECT alignment, provided buffers, registered buffers, block-device size queries, and architecture-specific hppa cache flush handling.

Risks: high IO volume and filesystem/direct-IO support requirements. The test skips unsupported direct IO and permission cases.

Test signals: pass is a strong end-to-end data integrity signal for read result length, buffer selection, and retry behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/files-exit-hang-poll.c -->
## sources/test-tools/liburing/test/files-exit-hang-poll.c

Purpose: regression test for process/ring exit hangs when a request pins the task file table and is linked to an unfinished poll.

Important APIs/types/functions: `add_poll`, `add_accept`, `setup_io_uring`, `t_bind_ephemeral_port`, `io_uring_prep_poll_add`, `io_uring_prep_accept`, `IOSQE_IO_LINK`, and `alarm`.

Control flow: the test creates a nonblocking TCP listener on an ephemeral port, initializes a ring, queues a linked poll on the listening socket followed by an accept, submits both, installs a one-second alarm that exits successfully, and waits for a CQE that should normally not arrive.

State and persistence behavior: global `ring` and listening socket remain live while the alarm triggers process exit. The intentional behavior is abrupt exit with pending linked requests.

Dependencies and integration points: integrates socket listen state, poll, accept, linked SQEs, and task file table cleanup.

Risks: the alarm-based success path means a hang is detected by external test timeout rather than explicit code. If a CQE arrives unexpectedly, the ring exits and returns pass.

Test signals: pass means the process exits rather than hanging with linked poll/accept file-table references.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/files-exit-hang-poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/files-exit-hang-timeout.c -->
## sources/test-tools/liburing/test/files-exit-hang-timeout.c

Purpose: companion exit-hang regression using a long linked timeout instead of poll before accept.

Important APIs/types/functions: `add_timeout`, `add_accept`, `setup_io_uring`, `io_uring_prep_timeout`, `io_uring_prep_accept`, `IOSQE_IO_LINK`, fixed port scan from `PORT`, and `alarm`.

Control flow: the test binds a nonblocking TCP listener to the first available port in a 100-port range, initializes a ring, links a 300-second timeout to an accept request, submits both, sets a one-second alarm that exits successfully, and waits for completion.

State and persistence behavior: the ring has a long pending linked timeout and an accept. The socket and ring are intentionally left pending until alarm-driven process exit or normal cleanup.

Dependencies and integration points: exercises timeout linked to socket accept and task file table cleanup on process exit.

Risks: hardcoded port range can be exhausted and cause skip. Like the poll variant, success is primarily absence of hang.

Test signals: pass means pending timeout/accept chains do not deadlock exit cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/files-exit-hang-timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-buf-iter.c -->
## sources/test-tools/liburing/test/fixed-buf-iter.c

Purpose: verifies fixed-buffer read/write with non-iterator file operations, based on a liburing issue regression.

Important APIs/types/functions: `test`, `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `io_uring_prep_write_fixed`, `/dev/urandom`, and `/dev/zero`.

Control flow: the test opens `/dev/urandom` and `/dev/zero`, allocates a 4096-byte buffer, registers it, reads random data into it via `read_fixed`, then writes it to `/dev/zero` via `write_fixed`, validating both CQEs are nonnegative.

State and persistence behavior: one fixed buffer remains registered during both IO operations. The file descriptors and buffer are local resources; the ring exits in `main`.

Dependencies and integration points: targets fixed-buffer support for character devices whose file operations do not use normal iterators.

Risks: cleanup is incomplete on some error paths. It validates success/nonnegative result rather than exact byte counts.

Test signals: pass means fixed-buffer IO can traverse non-iterator read/write implementations without kernel failure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-buf-iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-buf-merge.c -->
## sources/test-tools/liburing/test/fixed-buf-merge.c

Purpose: regression test for fixed-buffer range merging/skipping when multiple fixed reads target adjacent offsets inside one registered buffer.

Important APIs/types/functions: `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `io_uring_submit_and_wait`, `io_uring_for_each_cqe`, `io_uring_cq_advance`, and `t_aligned_alloc`.

Control flow: the test creates a temporary direct-IO file, allocates a large aligned buffer, registers it as one iovec, submits three fixed reads into consecutive 4096-byte slices starting at a 4096-byte offset inside the registered range, then checks all completions return 4096.

State and persistence behavior: one 128-page registered buffer backs several subrange fixed IOs. Temporary `.fixed-buf-*` file is unlinked on success and failure.

Dependencies and integration points: depends on O_DIRECT support and fixed-buffer registration over a larger range than each IO.

Risks: skips when O_DIRECT is unsupported. Failure indicates fixed-buffer accounting incorrectly merges or rejects subsegments.

Test signals: pass means fixed-buffer subrange lookup handles multiple adjacent requests inside one registered iovec.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-buf-merge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-hugepage.c -->
## sources/test-tools/liburing/test/fixed-hugepage.c

Purpose: tests registered fixed buffers backed by huge pages, multi-size THP-like allocations, unaligned hugepage offsets, and mixed huge/small page mappings.

Important APIs/types/functions: `mmap_hugebufs`, `mmap_mixture`, `get_mthp_bufs`, `register_submit`, `do_read`, `do_write`, `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `io_uring_prep_write_fixed`, `MAP_HUGETLB`, and `MTHP_16KB`.

Control flow: `main` opens an input file or `/dev/urandom` plus `/dev/zero`, creates a ring, then runs one-hugepage, multi-hugepage, unaligned hugepage, unaligned multi-size-page, and two mixed huge/small page scenarios. Each scenario registers buffers, performs fixed read and fixed write, unregisters, and unmaps/frees memory.

State and persistence behavior: each scenario maps or allocates memory and registers it as fixed buffers. Mappings are explicitly unmapped or freed after use.

Dependencies and integration points: depends on hugepage availability, THP/mTHP configuration, memlock limits, and fixed-buffer pinning.

Risks: many environments skip due to missing hugepages or `-ENOMEM`/`-EINVAL`. Mixed mappings target coalescing bugs.

Test signals: pass means fixed buffer registration and IO handle huge and mixed page-backed memory correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-hugepage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-link.c -->
## sources/test-tools/liburing/test/fixed-link.c

Purpose: checks linked fixed-buffer reads use the current iovec lengths and complete successfully.

Important APIs/types/functions: `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `io_uring_sqe_set_flags`, `IOSQE_IO_LINK`, and `/dev/zero`.

Control flow: the test opens `/dev/zero`, initializes a ring, allocates two 64-byte buffers, registers them, adjusts each iovec length to the length of a small string, queues two fixed reads linked together, submits and waits for both, and verifies each completion length matches the adjusted length.

State and persistence behavior: two registered buffers persist through the linked reads. Their `iov_len` fields are modified after registration in userspace, but the SQE read lengths are explicit.

Dependencies and integration points: exercises fixed buffer indexes, linked SQE submission, and completion validation.

Risks: no data comparison; it only checks result sizes. Cleanup is simple and early failures may leak allocations.

Test signals: pass indicates linked fixed reads complete with expected byte counts.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-reuse.c -->
## sources/test-tools/liburing/test/fixed-reuse.c

Purpose: verifies linked direct-open/read/close in a reused fixed-file slot sees the new file, not stale slot state.

Important APIs/types/functions: `io_uring_prep_openat_direct`, `io_uring_prep_read`, `io_uring_prep_close_direct`, `io_uring_register_files`, `IOSQE_FIXED_FILE`, `IOSQE_IO_LINK`, and feature `IORING_FEAT_CQE_SKIP`.

Control flow: the test creates two patterned files, registers an empty fixed-file table, opens the first file into slot 0, then submits a linked chain that opens the second file into slot 0, reads from fixed slot 0, and closes it. It validates completions and checks the buffer contains the second file's pattern.

State and persistence behavior: fixed slot 0 is deliberately reused. The core state is direct descriptor replacement across a linked operation chain.

Dependencies and integration points: integrates direct open/close, fixed-file reads, linked ordering, and fixed slot table setup.

Risks: skipped if `IORING_FEAT_CQE_SKIP` is absent. Pattern validation catches stale reference use.

Test signals: pass means fixed slot reuse is ordered correctly and reads observe the newly opened file.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-seg.c -->
## sources/test-tools/liburing/test/fixed-seg.c

Purpose: tests fixed-buffer segment validation for O_DIRECT reads, including offsets inside a registered buffer.

Important APIs/types/functions: `read_it`, `test`, `is_bdev`, `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `BLKGETSIZE64`, and aligned iovecs.

Control flow: the test opens a supplied file/block device or creates a temporary direct-IO file, registers read/write buffers, and issues fixed reads with varying lengths and offsets into the registered segment. It uses block-device detection to decide whether a supplied fd is acceptable.

State and persistence behavior: global `rvec` and `wvec` hold aligned registered buffers. Temporary files are unlinked when created by the test.

Dependencies and integration points: depends on O_DIRECT compatibility, block-device or regular-file sizing, and fixed buffer offset accounting.

Risks: direct IO support and alignment rules are environment-sensitive. Bad segment validation can surface as short reads or negative CQE results.

Test signals: pass means fixed-buffer segments and offsets are accepted only when valid and complete with expected lengths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-seg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fpos.c -->
## sources/test-tools/liburing/test/fpos.c

Purpose: verifies shared file-position (`f_pos`) handling for many linked reads and writes submitted with offset `-1`.

Important APIs/types/functions: `create_file`, `test_read`, `test_write`, `io_uring_prep_read`, `io_uring_prep_write`, `IOSQE_IO_LINK`, `IOSQE_ASYNC`, `io_uring_submit_and_wait`, and `lseek`.

Control flow: `main` runs eight combinations of read/write, async/non-async, and block size 1 or 7. Read tests submit 2048 linked reads at offset `-1`, reorder completions by `user_data`, validate alternating file data, and check `lseek` matches bytes read. Write tests submit 2048 linked one-byte writes at offset `-1`, verify file position equals queue size, then read back expected repeated data.

State and persistence behavior: temporary read/write files are unlinked after opening, so fd state persists without pathname. The file offset is shared mutable kernel state under heavy concurrent completions.

Dependencies and integration points: exercises implicit file-position updates, linked SQEs, async workers, and completion reordering.

Risks: assumes linked submission maintains enough ordering for `f_pos` semantics while completions may reorder. Failures show lost or duplicated offset advancement.

Test signals: pass means offset `-1` reads/writes advance `f_pos` coherently across large linked batches.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fpos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fsnotify.c -->
## sources/test-tools/liburing/test/fsnotify.c

Purpose: verifies io_uring O_DIRECT reads still generate fanotify access events with a meaningful task pid.

Important APIs/types/functions: conditional `CONFIG_HAVE_FANOTIFY`, `fanotify_init`, `fanotify_mark`, `io_uring_prep_read`, `fork`, `wait`, and `O_DIRECT`.

Control flow: when fanotify is available, the test creates or opens a regular file with O_DIRECT, marks it for `FAN_ACCESS | FAN_MODIFY`, forks, and the parent performs an io_uring read. The child reads one fanotify event and fails if the access mask is missing or the pid is zero.

State and persistence behavior: fanotify fd watches the target file while the read request completes. Temporary `.fsnotify.*` file is removed on exit.

Dependencies and integration points: requires fanotify permissions, regular files, O_DIRECT support, and io_uring read attribution to task context.

Risks: skipped without fanotify or privilege. Parent/child synchronization relies on fanotify blocking until the read event exists.

Test signals: pass means direct io_uring reads trigger fsnotify access events tied to a userspace task.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fsnotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fsync.c -->
## sources/test-tools/liburing/test/fsync.c

Purpose: validates io_uring fsync, drained fsync ordering, and sync-file-range support.

Important APIs/types/functions: `test_single_fsync`, `test_barrier_fsync`, `test_sync_file_range`, `io_uring_prep_fsync`, `io_uring_prep_writev`, `IOSQE_IO_DRAIN`, `IORING_FSYNC_DATASYNC`, and `io_uring_prep_sync_file_range`.

Control flow: `main` creates a ring, submits a single fsync on a temp file, then submits four writes plus a drained datasync fsync and verifies write CQEs precede fsync unless drain is unsupported. Finally it creates a small file and submits `sync_file_range`.

State and persistence behavior: temporary files are unlinked after opening or after creation. Iovec write buffers are allocated per barrier test and freed afterward.

Dependencies and integration points: exercises file writeback, drain ordering, fsync flags, and sync-file-range opcode.

Risks: older kernels may report `-EINVAL` for drain, which the barrier loop tolerates by breaking. Some error paths leak fd/buffers.

Test signals: pass means fsync operations complete and drained fsync is not observed before prior writes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/futex-kill.c -->
## sources/test-tools/liburing/test/futex-kill.c

Purpose: ensures killing a process with an active private futex wait through io_uring does not leave bad state or crash.

Important APIs/types/functions: `do_child`, `test`, `io_uring_prep_futex_wait`, `io_uring_prep_futex_waitv`, `FUTEX2_PRIVATE`, `FUTEX2_SIZE_U32`, `IORING_SETUP_SQPOLL`, and `IOSQE_ASYNC`.

Control flow: each scenario forks a child that creates a ring, allocates a futex word, submits either scalar or vectored private futex wait, optionally async and optionally SQPOLL, then exits success without waiting. The parent sleeps briefly, kills the child with SIGKILL, and waits.

State and persistence behavior: futex wait state is intentionally abandoned by a killed process. Rings and futex memory are not cleaned by the child.

Dependencies and integration points: targets futex cancellation/cleanup across process death, async workers, and SQPOLL.

Risks: signal timing is approximate. The test does not validate CQEs; it is a lifetime/crash regression.

Test signals: pass means all scalar/vectored async/SQPOLL combinations tolerate waiter death.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/futex-kill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/futex.c -->
## sources/test-tools/liburing/test/futex.c

Purpose: comprehensive futex wait, wake, waitv, cancellation, ordering, and invalid-flag coverage for io_uring futex opcodes.

Important APIs/types/functions: `fwake`, `__test`, `test`, `test_order`, `test_multi_wake`, `test_wake_zero`, `test_invalid`, `io_uring_prep_futex_wait`, `io_uring_prep_futex_waitv`, `io_uring_prep_futex_wake`, `io_uring_prep_cancel64`, and `io_uring_register_sync_cancel`.

Control flow: the main matrix loops 500 times through scalar and vectored futex waits, spawning wake threads and racing async/non-async cancel requests. It then checks wake-zero semantics, invalid flag errors, SQPOLL and cooperative taskrun modes, wake ordering with one remaining wait canceled synchronously, and multi-wake completion of two waits.

State and persistence behavior: dynamically allocated futex words and `futex_waitv` arrays represent wait state. Global `no_futex` records unsupported kernels.

Dependencies and integration points: integrates futex2 flags, pthread wake helpers, io_uring async cancel, SQPOLL, COOP_TASKRUN, and sync cancel registration.

Risks: race-heavy; expected completion order is constrained only in specific ordering tests. Unsupported futex opcodes return `-EINVAL` or `-EOPNOTSUPP` and skip.

Test signals: pass strongly indicates futex wait/wake/cancel semantics are correct across ring modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/hardlink.c -->
## sources/test-tools/liburing/test/hardlink.c

Purpose: tests `IORING_OP_LINKAT` hardlink creation, symlink-follow behavior, and expected linkat errors.

Important APIs/types/functions: `do_linkat`, `files_linked_ok`, `io_uring_prep_linkat`, `io_uring_wait_cqes`, `AT_EMPTY_PATH`, `AT_SYMLINK_FOLLOW`, `stat`, and `unlinkat`.

Control flow: the test creates a target file, optionally links it through `AT_EMPTY_PATH` when running as root, creates a symlink, links target to a new name, verifies inode/link counts, links through the symlink with follow flag, then verifies expected `-EEXIST` and `-ENOENT` error cases.

State and persistence behavior: several fixed test pathnames are created and always unlinked in the cleanup path. Hardlink state is validated by device, inode, and `st_nlink`.

Dependencies and integration points: exercises raw linkat semantics through io_uring and filesystem metadata.

Risks: root-only `AT_EMPTY_PATH` coverage is skipped for non-root. Existing files with the same names would interfere.

Test signals: pass means io_uring linkat mirrors syscall hardlink behavior for success and error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/hardlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/helpers.c -->
## sources/test-tools/liburing/test/helpers.c

Purpose: shared test utility implementation for allocation, file creation, ring setup, socket setup, timing, nonblocking toggles, submission helpers, and iovec comparison.

Important APIs/types/functions: `t_malloc`, `t_calloc`, `t_posix_memalign`, `t_aligned_alloc`, `t_create_file`, `t_create_file_pattern`, `t_create_buffers`, `t_create_ring_params`, `t_create_ring`, `t_register_buffers`, `t_create_socket_pair`, `t_create_socketpair_ip`, `t_probe_defer_taskrun`, `__io_uring_flush_sq`, `t_error`, timing helpers, `t_submit_and_wait_single`, `t_iovec_data_length`, and `t_compare_data_iovec`.

Control flow: functions are independent helpers. Most allocation helpers assert on failure; ring helpers normalize unsupported SQPOLL/invalid setup to `T_SETUP_SKIP`; socket helpers create connected IPv4/IPv6 TCP/UDP pairs; `__io_uring_flush_sq` publishes SQ tail with appropriate memory ordering.

State and persistence behavior: helpers create files, sockets, and rings on behalf of callers but generally transfer cleanup responsibility to tests. Timing helpers are pure calculations.

Dependencies and integration points: central dependency for almost all liburing tests, wrapping liburing APIs and Linux sockets/files.

Risks: assert-on-failure simplifies tests but aborts rather than returning recoverable errors. Incorrect `__io_uring_flush_sq` ordering would affect low-level SQPOLL/IOPOLL tests.

Test signals: this file is infrastructure; correctness is inferred by dependent tests using its helpers successfully.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/helpers.h -->
## sources/test-tools/liburing/test/helpers.h

Purpose: public helper declarations and shared test result/setup constants for the liburing test suite.

Important APIs/types/functions: enums `t_setup_ret` and `t_test_result`, declarations for allocation/file/socket/ring helpers, `t_probe_defer_taskrun`, nonblocking helpers, `__io_uring_flush_sq`, timing helpers, `t_submit_and_wait_single`, iovec utilities, and inline `t_io_uring_init_sqarray`.

Control flow: header-only logic is limited to `t_io_uring_init_sqarray`, which calls `__io_uring_queue_init_params` with no SQ array memory and converts nonnegative returns to zero.

State and persistence behavior: no persistent state. It defines shared return-code contracts: pass `0`, fail `1`, skip `77`, and setup skip vs OK.

Dependencies and integration points: includes `liburing.h`, internal `setup.h`, socket/time/system headers, and exposes helpers to C and C++ callers with `extern "C"`.

Risks: changes here affect nearly every test. The inline setup wrapper reaches into internal liburing setup APIs.

Test signals: successful compilation and broad dependent test execution validate the declarations and result constants.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ignore-single-mmap.c -->
## sources/test-tools/liburing/test/ignore-single-mmap.c

Purpose: regression test for applications that ignore `IORING_FEAT_SINGLE_MMAP` and still perform smaller legacy-style ring mmaps.

Important APIs/types/functions: raw `__sys_io_uring_setup`, raw `__sys_mmap`, `IORING_OFF_SQ_RING`, `IORING_FEAT_SINGLE_MMAP`, `IS_ERR`, and `PTR_ERR`.

Control flow: the test sets up a ring with 128 entries through the raw syscall, skips if setup fails or single-mmap feature is absent, then mmaps only the SQ ring-sized area at `IORING_OFF_SQ_RING`. Success passes; mmap error fails.

State and persistence behavior: one raw ring fd is created and closed only on the pass/skip paths before failure. The mapping is not explicitly unmapped.

Dependencies and integration points: targets kernel mmap ABI compatibility for io_uring ring layout.

Risks: low-level syscall use bypasses liburing cleanup. Failure catches kernels returning `-EFAULT` for valid smaller mappings.

Test signals: pass means single-mmap rings still tolerate legacy segmented mmap calls.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ignore-single-mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/init-mem.c -->
## sources/test-tools/liburing/test/init-mem.c

Purpose: verifies `io_uring_queue_init_mem` and `io_uring_memory_size_params` compute sufficient memory for many SQ/CQ sizes and SQE/CQE layout variants.

Important APIs/types/functions: `struct ctx`, `struct q_entries`, `setup_ctx`, `check_red`, `test`, `io_uring_memory_size_params`, `io_uring_queue_init_mem`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_NO_SQARRAY`, `IORING_SETUP_SQE128`, and `IORING_SETUP_CQE32`.

Control flow: for each entry configuration, the test allocates 2 MiB aligned memory, places redzones immediately before and after the ring memory region, initializes the ring in caller-provided memory, checks returned memory size matches the required size, then submits enough NOP batches to cycle through twice the CQ depth while repeatedly checking redzones and user_data ordering.

State and persistence behavior: ring memory is caller-owned and freed after `io_uring_queue_exit`. Redzone values detect overrun/underrun persistence.

Dependencies and integration points: covers custom ring memory initialization, no-SQ-array mode, CQ sizing, and 128-byte SQE/32-byte CQE modes.

Risks: unsupported parameters skip. A mismatch between size calculation and actual initialization is a serious memory corruption signal.

Test signals: pass means memory sizing is accurate and no ring operation writes outside the advertised buffer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/init-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io-cancel.c -->
## sources/test-tools/liburing/test/io-cancel.c

Purpose: broad cancellation suite for normal IO, partial cancels, cross-ring isolation, forked cancellation, inflight exit, and SQPOLL/io-wq cleanup.

Important APIs/types/functions: `start_io`, `wait_io`, `do_io`, `start_cancel`, `test_io_cancel`, `test_dont_cancel_another_ring`, `test_cancel_req_across_fork`, `test_cancel_inflight_exit`, `test_sqpoll_cancel_iowq_requests`, `io_uring_prep_cancel64`, `io_uring_prep_poll_add`, and `io_uring_prep_timeout`.

Control flow: `main` first runs targeted pipe/poll/fork/SQPOLL cleanup scenarios, then creates an O_DIRECT test file and buffers. It runs eight combinations of read/write, full/partial cancel, and async/non-async cancel. IO is timed to allow some requests to start before cancel SQEs are submitted; completions are validated based on whether partial cancellation should leave odd-numbered IO intact.

State and persistence behavior: global `vecs` backs the file IO matrix. Pipes, forked processes, and temporary `.io-cancel-test` file create transient state; the file is unlinked on exit.

Dependencies and integration points: integrates cancel-by-user_data, async cancel, direct IO, pipes, fork sharing, linked poll/timeout chains, SQPOLL, and io-wq references.

Risks: cancellation timing is inherently race-sensitive and accepts several legitimate results such as `-ECANCELED`, `-EINTR`, `-EALREADY`, or successful completion in targeted cases.

Test signals: pass means cancellation is scoped, does not cross rings accidentally, handles fork/exit, and leaves uncanceled IO valid.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io-cancel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io-wq-exit.c -->
## sources/test-tools/liburing/test/io-wq-exit.c

Purpose: verifies a thread that creates io-wq work can exit promptly without waiting for idle worker timeout.

Important APIs/types/functions: thread function `test`, `get_time_ns`, `pthread_create`, `pthread_join`, `io_uring_prep_splice`, `pipe`, and `io_uring_queue_exit`.

Control flow: the worker thread creates a ring, source/destination files, and a pipe, writes source data, queues two splice operations through the pipe, waits for both completions, cleans resources, and exits. `main` measures total thread lifetime and fails if it takes 500 ms or more.

State and persistence behavior: temporary `.splice.<pid>.src` and `.splice.<pid>.dst` files plus pipe descriptors are created inside the thread and unlinked in cleanup.

Dependencies and integration points: targets io-wq worker lifecycle for splice operations and thread teardown.

Risks: timing threshold may be noisy on overloaded systems. There is a minor cleanup typo checking `fd_src` before closing `fd_dst`.

Test signals: pass means io-wq workers do not force long idle timeout waits during thread/ring exit.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io-wq-exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io-wq-unused-exit.c -->
## sources/test-tools/liburing/test/io-wq-unused-exit.c

Purpose: ensures io-wq worker threads disappear after the last ring is closed, supporting checkpoint/restore style quiescence.

Important APIs/types/functions: `count_iowq_workers`, `wait_for_iowq_workers`, `/proc/self/task/*/comm`, `io_uring_prep_splice`, `io_uring_queue_exit`, and helper timing `mtime_since_now`.

Control flow: the test creates a ring, temporary source/destination files, a pipe, submits two splice operations, validates both completions, waits until at least one `iou-wrk-` thread is visible, exits the ring, then waits up to two seconds for all such worker threads to disappear.

State and persistence behavior: worker-thread presence is observed through procfs task comm names. Temporary files and pipe fds are cleaned on all exit paths.

Dependencies and integration points: integrates io-wq creation by splice with ring shutdown and procfs worker detection.

Risks: if workers are not observed quickly, the test converts that failure to skip because the environment may not have created io-wq workers. Name-prefix matching depends on kernel worker naming.

Test signals: pass means io-wq worker threads are not left lingering after ring closure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io-wq-unused-exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_enter.c -->
## sources/test-tools/liburing/test/io_uring_enter.c

Purpose: low-level unit tests for the `io_uring_enter` syscall ABI and SQ ring drop accounting.

Important APIs/types/functions: `expect_fail`, `try_io_uring_enter`, `setup_file`, `io_prep_read`, `reap_events`, `submit_io`, raw `io_uring_enter`, `t_io_uring_init_sqarray`, `io_uring_smp_store_release`, and SQ fields `ktail`, `khead`, `kdropped`.

Control flow: the test initializes a large SQ-array ring, verifies invalid flags/fds and valid no-op enter behavior, fills the SQ with readv requests, calls enter with `IORING_ENTER_GETEVENTS` and `min_complete` equal to SQ depth, verifies all completions are available, then manually writes an invalid SQ array index and checks the kernel increments the dropped counter.

State and persistence behavior: temporary `/tmp/io_uring_enter-test.XXXXXX` file backs the read requests and is unlinked after submission. SQ ring memory is directly modified for the invalid-index test.

Dependencies and integration points: bypasses high-level submit helpers for syscall ABI and ring memory ordering validation.

Risks: direct SQ manipulation is fragile but intentional. If large ring setup fails with `-ENOMEM`, it falls back to 128 entries.

Test signals: pass means syscall error handling, GETEVENTS waiting, completion accounting, and invalid SQE drop accounting work.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_enter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_passthrough.c -->
## sources/test-tools/liburing/test/io_uring_passthrough.c

Purpose: NVMe passthrough read/write test matrix for `IORING_OP_URING_CMD` with SQE128/CQE32 rings.

Important APIs/types/functions: `verify_buf`, `fill_pattern`, `__test_io`, `test_io`, `test_invalid_passthru_submit`, `test_io_uring_submit_enters`, `io_uring_prep_uring_cmd`, `NVME_URING_CMD_IO`, `NVME_URING_CMD_IO_VEC`, `IORING_URING_CMD_FIXED`, and NVMe fields from `nvme.h`.

Control flow: the test expects an NVMe block device path. It builds NVMe read/write commands over a 256 KiB buffer matrix, varying read/write, SQPOLL fixed files, registered buffers, vector vs non-vector command payloads, hybrid IOPOLL, async, and linked NOP chains. It verifies read data patterns, tests an invalid namespace submission failure, and checks submit behavior on IOPOLL passthrough rings.

State and persistence behavior: global data/meta buffers and NVMe namespace geometry drive command construction. `no_pt` and `vec_fixed_supported` gate unsupported passthrough variants.

Dependencies and integration points: requires NVMe uring command support, SQE128/CQE32, optional metadata handling, IOPOLL, fixed files, and registered buffers.

Risks: highly hardware-specific and commonly skipped without NVMe passthrough support. Incorrect LBA/metadata calculations can produce device errors.

Test signals: pass means passthrough commands operate correctly across command layouts and ring modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_passthrough.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_register.c -->
## sources/test-tools/liburing/test/io_uring_register.c

Purpose: low-level unit tests for the `io_uring_register` syscall ABI, buffer limits, file-table limits, and ring-fd registration restrictions.

Important APIs/types/functions: `expect_fail`, `new_io_uring`, `map_filebacked`, `test_max_fds`, `test_memlock_exceeded`, `test_iovec_nr`, `test_iovec_size`, `ioring_poll`, `test_poll_ringfd`, raw `io_uring_register`, `IORING_REGISTER_BUFFERS`, and `IORING_REGISTER_FILES`.

Control flow: `main` verifies invalid fd/opcode handling, then tests buffer registration error cases: null base, zero length, partially unmapped memory, huge pages, file-backed memory, memlock pressure, and excessive iovec count. It then attempts very large file registration using a huge mapped fd array, and finally verifies polling the ring fd works while registering the ring fd as a fixed file fails.

State and persistence behavior: tracks page size, memlock rlimit, and `/dev/null` fd globally. It maps large anonymous/file-backed regions and unmaps them after file-table tests.

Dependencies and integration points: covers syscall ABI, memory pinning, rlimits, filesystem mapping type detection, poll, SQPOLL, and fixed-file validation.

Risks: resource-heavy; many cases depend on memlock limits, hugepages, address-space availability, and root/non-root behavior.

Test signals: pass means registration rejects invalid inputs, accepts supported boundary cases, and protects against ring-fd fixed-file registration.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_register.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_setup.c -->
## sources/test-tools/liburing/test/io_uring_setup.c

Purpose: low-level unit tests for the `io_uring_setup` syscall ABI.

Important APIs/types/functions: `try_io_uring_setup`, raw `io_uring_setup`, `struct io_uring_params`, `IORING_SETUP_SQ_AFF`, `IORING_SETUP_SQPOLL`, `get_nprocs_conf`, and `read` on ring fd.

Control flow: the test checks expected setup failures for zero entries, null params, nonzero reserved fields, invalid flags, SQ_AFF without SQPOLL, and SQPOLL CPU affinity outside the configured CPU range. It then creates a valid ring fd and verifies normal `read` from that fd fails.

State and persistence behavior: only transient ring fds are created; valid fds are closed after unexpected success or left to process exit in the final check.

Dependencies and integration points: directly validates kernel setup argument checking and ring fd file operations.

Risks: `-EPERM` for privileged setup cases is tolerated for non-root. The helper compares raw negative syscall-style returns.

Test signals: pass means setup rejects malformed params and ring fds are not readable as normal files.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-leak.c -->
## sources/test-tools/liburing/test/iopoll-leak.c

Purpose: regression test for memory/resource leaks when an IOPOLL ring exits with submitted IO not explicitly completed.

Important APIs/types/functions: `do_iopoll`, `test`, `fork`, `wait`, `t_create_ring(... IORING_SETUP_IOPOLL)`, and `io_uring_prep_read`.

Control flow: `main` creates or uses a direct-IO file and runs 16 child processes. Each child opens the file with O_DIRECT, creates one aligned buffer, initializes an IOPOLL ring, submits a read, then closes the fd and frees the buffer without waiting for completion or exiting the ring explicitly.

State and persistence behavior: each child leaks/abandons an in-flight IOPOLL request by design; process exit performs final cleanup. The temporary file is removed by the parent.

Dependencies and integration points: depends on O_DIRECT and IOPOLL support.

Risks: does not verify CQEs; leak detection requires external sanitizers/kernel accounting. Unsupported direct IO skips.

Test signals: pass means repeated abandoned IOPOLL submissions do not cause visible process failure; deeper leak signal comes from surrounding test infrastructure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-leak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-overflow.c -->
## sources/test-tools/liburing/test/iopoll-overflow.c

Purpose: stresses IOPOLL completion queue overflow handling with many submitted direct reads and a small CQ size.

Important APIs/types/functions: `test`, `t_create_ring_params`, `IORING_SETUP_IOPOLL`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_SUBMIT_ALL`, raw `__sys_io_uring_enter`, `io_uring_prep_read`, and `io_uring_wait_cqe`.

Control flow: the ring is created with 64 SQ entries and 64 CQ entries, then eight batches of 32 reads are submitted without reaping completions. After a short sleep, the test enters the kernel requesting all 256 events and then waits/reaps each CQE.

State and persistence behavior: global `vecs` hold aligned buffers, and the CQ is intentionally overfilled relative to its configured size. Temporary file is removed when created by the test.

Dependencies and integration points: requires O_DIRECT and IOPOLL support.

Risks: unsupported filesystems skip. It does not validate each `cqe->res`, focusing on overflow/liveness.

Test signals: pass means IOPOLL CQ overflow can be drained without lost wakeups or hangs.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-overflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-sync.c -->
## sources/test-tools/liburing/test/iopoll-sync.c

Purpose: verifies uring socket command operations on an IOPOLL ring for files that do not support normal polled IO.

Important APIs/types/functions: `io_uring_prep_cmd_sock`, `SOCKET_URING_OP_GETSOCKOPT`, `SOCKET_URING_OP_SETSOCKOPT`, `IORING_SETUP_IOPOLL`, `IOSQE_IO_LINK`, and `io_uring_cqe_iter`.

Control flow: the test creates a TCP socket, initializes `SO_REUSEADDR` to zero, creates an IOPOLL ring, queues linked getsockopt, setsockopt, and getsockopt socket commands, submits all three, then iterates CQEs to verify the first read returns zero, the set succeeds, the second read returns one, and no extra CQEs exist. Unsupported command results skip.

State and persistence behavior: socket option state changes from 0 to 1. The ring CQ is traversed using the CQE iterator without explicit advance in this file.

Dependencies and integration points: integrates uring command socket operations with IOPOLL rings and linked CQE ordering.

Risks: command support is kernel-dependent. The test assumes CQEs appear in link order.

Test signals: pass means socket uring commands work and synchronize correctly on an IOPOLL ring.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll.c -->
## sources/test-tools/liburing/test/iopoll.c

Purpose: main polled-IO matrix for read/write, SQPOLL fixed files, registered buffers, provided buffers, hybrid polling, defer-taskrun, and CQE polling helpers.

Important APIs/types/functions: `provide_buffers`, `__test_io`, `test_io_uring_cqe_peek`, `test_io_uring_submit_enters`, `test_io`, `probe_buf_select`, `io_uring_prep_readv`, `io_uring_prep_writev`, `io_uring_prep_read_fixed`, `io_uring_prep_write_fixed`, `IORING_SETUP_IOPOLL`, `IORING_SETUP_HYBRID_IOPOLL`, `IOSQE_BUFFER_SELECT`, and `__io_uring_flush_sq`.

Control flow: `main` probes provided-buffer support, creates a test file and aligned buffers, and runs up to 64 combinations over write/read, SQPOLL, fixed buffers, hybrid IOPOLL, provided buffers, and defer-taskrun. It then verifies that `io_uring_submit` enters the kernel to reap IOPOLL completions and that `io_uring_peek_cqe` can drive IOPOLL completion retrieval.

State and persistence behavior: global flags `no_buf_select`, `no_iopoll`, and `no_hybrid` prune unsupported matrix branches. Temporary file and global buffers back all tests.

Dependencies and integration points: depends on O_DIRECT and device/filesystem IOPOLL support, plus buffer selection and defer-taskrun feature probing.

Risks: environment support varies widely. Some paths detect `-EOPNOTSUPP` after submission and disable further IOPOLL checks.

Test signals: pass means polled IO completes across supported buffer/file modes and liburing CQE peek/submit helpers properly enter the kernel.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iowait.c -->
## sources/test-tools/liburing/test/iowait.c

Purpose: tests `io_uring_set_iowait` toggling on kernels advertising `IORING_FEAT_NO_IOWAIT`.

Important APIs/types/functions: `get_iowait`, `test`, `io_uring_set_iowait`, `/proc/stat`, `sched_setaffinity`, `io_uring_wait_cqe_timeout`, and `IORING_FEAT_NO_IOWAIT`.

Control flow: `main` pins the process to CPU 0, creates a ring, and runs `test` first with iowait disabled then enabled. Each scenario submits a pipe read that will block, records CPU0 iowait from `/proc/stat`, waits one second with timeout, closes pipe fds to complete the read, reaps the CQE, and checks iowait delta is small when disabled and large when enabled.

State and persistence behavior: ring iowait mode is mutable per scenario. `/proc/stat` provides external CPU accounting state.

Dependencies and integration points: depends on scheduler affinity, procfs accounting, pipe blocking reads, and kernel iowait feature support.

Risks: CPU accounting thresholds can be noisy in virtualized or busy systems. Lack of affinity permission causes skip.

Test signals: pass means io_uring wait accounting can be toggled and affects CPU iowait reporting as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iowait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/kallsyms.c -->
## sources/test-tools/liburing/test/kallsyms.c

Purpose: exercises `/proc/kallsyms` read file operations through io_uring with vectored/non-vectored and registered/non-registered buffers.

Important APIs/types/functions: `__test_io`, `test_io`, `has_nonvec_read`, `io_uring_register_probe`, `io_uring_prep_read`, `io_uring_prep_readv`, `io_uring_prep_read_fixed`, and `t_register_buffers`.

Control flow: the test allocates one 8192-byte aligned buffer, probes non-vectored read opcode support, then reads `/proc/kallsyms` with readv and read paths, both with and without registered buffers as supported. It waits for each CQE and tolerates `-EINVAL` on unsupported non-vectored reads.

State and persistence behavior: global `vecs` hold buffers and `warned` suppresses repeated unsupported messages. `/proc/kallsyms` content is read-only kernel symbol state.

Dependencies and integration points: integrates procfs file operations, registered buffers, opcode probing, and standard ring setup.

Risks: `/proc/kallsyms` may be unavailable or permission-restricted; those cases are treated as nonfatal returns. The test does not validate data content.

Test signals: pass means procfs read handlers work through io_uring's read/readv/fixed-buffer paths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/kallsyms.c -->
