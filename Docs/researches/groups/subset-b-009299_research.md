# subset-b-009299 research

Grouped research report for LTP syscall files in the `io*`, `ioctl`, `ioperm`, `iopl`, `ioprio`, and SysV IPC message/semaphore areas. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/io_getevents02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/io_getevents02.c

Purpose: negative libaio coverage for an invalid zeroed AIO context; expected result is `-EINVAL`, not success or another negative libaio errno. Source comment intent: Test io_getevents invoked via libaio with invalid ctx and expects it to return -EINVAL..

Important APIs/types/functions: core calls `io_getevents`; local functions `run`; local structs `tst_test`; headers `config.h`, `tst_test.h`, `libaio.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with the AIO completion wait path and libaio return-value conventions. Harness metadata `needs_kconfigs, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/io_getevents02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/Makefile

Purpose: adds AIO libraries where required and includes LTP leaf build rules.

Important APIs/types/functions: make variables and includes are the important interface here: `LDLIBS			+= $(AIO_LIBS)`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with the AIO completion path, optional signal-mask replacement, and 32-bit/time64 timeout ABI variants; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/io_pgetevents01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/io_pgetevents01.c

Purpose: successful `io_pgetevents` completion of a single pwrite request across old-timespec and time64 syscall variants. Source comment intent: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> Description: Basic io_pgetevents() test to receive 1 event successfully..

Important APIs/types/functions: core calls `io_pgetevents`, `io_setup`, `io_submit`, `io_destroy`, `SAFE_OPEN`; local functions `setup`, `run`; local structs `time64_variants`, `time64_variants`, `io_event`, `iocb`, `tst_ts`, `tst_test`; headers `time64_variants.h`, `tst_test.h`, `tst_timer.h`, `lapi/io_pgetevents.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with the AIO completion path, optional signal-mask replacement, and 32-bit/time64 timeout ABI variants. Harness metadata `min_kver, needs_tmpdir, setup, test_all, test_variants` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Variant coverage depends on syscall availability and kernel time ABI support.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/io_pgetevents01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/io_pgetevents02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/io_pgetevents02.c

Purpose: failure matrix for invalid context, negative min/max counts, bad events, timeout, and signal-mask pointers. Source comment intent: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> Description: Basic io_pgetevents() test to check various failures..

Important APIs/types/functions: core calls `io_pgetevents`, `io_setup`, `io_submit`, `io_destroy`, `SAFE_OPEN`; local functions `setup`, `cleanup`, `run`; local structs `io_event`, `tst_ts`, `tcase`, `io_event`, `tst_ts`, `time64_variants`, `time64_variants`, `iocb`; headers `time64_variants.h`, `tst_test.h`, `tst_timer.h`, `lapi/io_pgetevents.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with the AIO completion path, optional signal-mask replacement, and 32-bit/time64 timeout ABI variants. Harness metadata `cleanup, min_kver, needs_tmpdir, setup, tcnt, test, test_variants` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Variant coverage depends on syscall availability and kernel time ABI support.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/io_pgetevents02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/Makefile

Purpose: adds AIO libraries where required and includes LTP leaf build rules.

Important APIs/types/functions: make variables and includes are the important interface here: `LDLIBS			+= $(AIO_LIBS)`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with context allocation limits, invalid context pointers, and `/proc/sys/fs/aio-max-nr`; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/io_setup01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/io_setup01.c

Purpose: libaio `io_setup` success and failures for nonzero context, invalid event count, NULL context pointer, and aio-max-nr exhaustion. Source comment intent: Test io_setup invoked via libaio: - io_setup succeeds if both nr_events and ctxp are valid. - io_setup fails and returns -EINVAL if ctxp is not initialized to 0. - io_setup fails and returns -EINVAL if nr_events is invalid. - io_setup fails and returns -EFAULT if ctxp is NULL. - io_setup fails and returns -EAGAIN if nr_events exceeds the limit 1of available events..

Important APIs/types/functions: core calls `io_setup`, `io_destroy`; local functions `verify_failure`, `verify_success`, `verify_io_setup`; local structs `tst_test`; headers `errno.h`, `string.h`, `unistd.h`, `config.h`, `tst_test.h`, `libaio.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with context allocation limits, invalid context pointers, and `/proc/sys/fs/aio-max-nr`. Harness metadata `test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/io_setup01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/io_setup02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/io_setup02.c

Purpose: raw `__NR_io_setup` coverage for EFAULT, EINVAL, EAGAIN, success, and matching `io_destroy` cleanup. Source comment intent: Test io_setup invoked via syscall(2): - io_setup fails and returns EFAULT if ctxp is NULL. - io_setup fails and returns EINVAL if ctxp is not initialized to 0. - io_setup fails and returns EINVAL if nr_events is -1. - io_setup fails and returns EAGAIN if nr_events exceeds the limit of available events. - io_setup succeeds if both nr_events and ctxp are valid..

Important APIs/types/functions: core calls `io_setup`; local functions `run`; local structs `tst_test`; headers `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with context allocation limits, invalid context pointers, and `/proc/sys/fs/aio-max-nr`. Harness metadata `needs_kconfigs, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/io_setup02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/Makefile

Purpose: adds AIO libraries where required and includes LTP leaf build rules.

Important APIs/types/functions: make variables and includes are the important interface here: `io_submit01:	LDLIBS	+= $(AIO_LIBS)`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with submission of raw or libaio `iocb` requests and completion harvesting; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit01.c

Purpose: libaio `io_submit` validation for bad context/count/pointers/fds, zero-byte requests, and zero-count no-op submissions. Source comment intent: Test io_submit() invoked via libaio: - io_submit fails and returns -EINVAL if ctx is invalid. - io_submit fails and returns -EINVAL if nr is invalid. - io_submit fails and returns -EFAULT if iocbpp pointer is invalid. - io_submit fails and returns -EBADF if fd is invalid. - io_submit succeeds and returns the number of iocbs submitted. - io_submit succeeds and returns 0 if nr is zero..

Important APIs/types/functions: core calls `io_getevents`, `io_setup`, `io_submit`, `SAFE_OPEN`; local functions `setup`, `cleanup`, `verify_io_submit`; local structs `iocb`, `iocb`, `iocb`, `iocb`, `iocb`, `iocb`, `iocb`, `iocb`; headers `errno.h`, `string.h`, `fcntl.h`, `config.h`, `tst_test.h`, `libaio.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with submission of raw or libaio `iocb` requests and completion harvesting. Harness metadata `cleanup, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit02.c

Purpose: raw syscall success cases where `io_submit` returns the submitted count or zero for `nr == 0`. Source comment intent: Test io_submit invoked via syscall(2): 1. io_submit() returns the number of iocbs submitted. 2. io_submit() returns 0 if nr is zero..

Important APIs/types/functions: core calls `io_submit`, `io_destroy`, `SAFE_OPEN`; local functions `io_prep_option`, `setup`, `cleanup`, `run`; key constants/macros `TEST_FILE`, `MODE`; local structs `iocb`, `iocb`, `tcase`, `iocb`, `io_event`, `timespec`, `tst_test`; headers `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with submission of raw or libaio `iocb` requests and completion harvesting. Harness metadata `cleanup, needs_kconfigs, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit03.c

Purpose: raw syscall negative cases for invalid context/count/iocb pointers and descriptor access mode mismatches. Source comment intent: Test io_submit invoked via syscall(2): 1. io_submit fails and returns EINVAL if ctx is invalid. 2. io_submit fails and returns EINVAL if nr is invalid. 3. io_submit fails and returns EFAULT if iocbpp pointer is invalid. 4. io_submit fails and returns EBADF if fd is invalid..

Important APIs/types/functions: core calls `io_submit`, `io_destroy`, `SAFE_OPEN`; local functions `io_prep_option`, `setup`, `cleanup`, `run`; key constants/macros `RDONLY_FILE`, `WRONLY_FILE`, `MODE`; local structs `iocb`, `iocb`, `iocb`, `iocb`, `iocb`, `iocb`, `iocb`, `iocb`; headers `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with submission of raw or libaio `iocb` requests and completion harvesting. Harness metadata `cleanup, needs_kconfigs, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit04.c

Purpose: `RWF_NOWAIT` read from an empty pipe through AIO, expecting a completion result of `-EAGAIN`. Source comment intent: Test RWF_NOWAIT support in io_submit(), verifying that an asynchronous read operation on a blocking resource (empty pipe) will cause -EAGAIN. This is done by checking that io_getevents() :manpage:`io_getevents(2)` syscall returns immediately and io_event.res is equal to -EAGAIN..

Important APIs/types/functions: core calls `io_getevents`, `io_submit`, `io_destroy`; local functions `setup`, `cleanup`, `run`; key constants/macros `BUF_SIZE`; local structs `io_event`, `timespec`, `tst_test`; headers `config.h`, `tst_test.h`, `lapi/syscalls.h`, `lapi/aio_abi.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with submission of raw or libaio `iocb` requests and completion harvesting. Harness metadata `bufs, cleanup, needs_kconfigs, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/Makefile

Purpose: adds AIO libraries where required and includes LTP leaf build rules.

Important APIs/types/functions: make variables and includes are the important interface here: `top_srcdir, testcases.mk, generic_leaf_target.mk`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring01.c

Purpose: raw fixed-buffer read using `IORING_REGISTER_BUFFERS`, an SQE, `io_uring_enter`, and CQE data validation. Source comment intent: Copyright (C) 2020 ARM Ltd. All rights reserved. Author: Vikas Kumar <vikas.kumar2@arm.com> Copyright (C) 2020 Cyril Hrubis <chrubis@suse.cz> Tests for asynchronous I/O raw API i.e io_uring_setup(), io_uring_register() and io_uring_enter(). This tests validate basic API operation by creating a submission queue and a completion queue using io_uring_setup(). User buffer registered in the kernel for long term operation using io_uring_register(). This tests initiates I/O operations with the help of io_uring_enter()..

Important APIs/types/functions: core calls `io_uring_setup`, `io_uring_register`, `io_uring_enter`, `SAFE_OPEN`; local functions `setup_io_uring_test`, `check_buffer`, `drain_uring_cq`, `submit_to_uring_sq`, `cleanup_io_uring_test`, `run`, `setup`; key constants/macros `TEST_FILE`, `QUEUE_DEPTH`, `BLOCK_SZ`; local structs `tcase`, `io_uring_submit`, `iovec`, `io_cq_ring`, `io_uring_cqe`, `iovec`, `tcase`, `tst_test`; headers `io_uring_common.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `bufs, needs_tmpdir, save_restore, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring02.c

Purpose: CVE-2020-29373 regression that async `SENDMSG` must not bypass a process chroot. Source comment intent: Copyright (C) 2021 SUSE LLC Author: Nicolai Stange <nstange@suse.de> LTP port: Martin Doucha <mdoucha@suse.cz> CVE-2020-29373 Check that io_uring does not bypass chroot. Fixed in: commit 9392a27d88b9707145d713654eb26f0c29789e50 Author: Jens Axboe <axboe@kernel.dk> Date: Thu Feb 6 21:42:51 2020 -0700 io-wq: add support for inheriting ->fs commit ff002b30181d30cdfbca316dadd099c3ca0d739c Author: Jens Axboe <axboe@kernel.dk> Date: Fri Feb 7 16:05:21 2020 -0700 io_uring: grab ->fs as part of async preparation stable 5.4 specific backport: commit c4a23c852e80a3921f56c6fbc851a21c84a6d06b Author: Nicolai Stange <nstange@suse.de> Date: Wed Jan 27 14:34:43 2021 +0100.

Important APIs/types/functions: local functions `setup`, `drain_fallback`, `check_result`, `run`, `cleanup`; key constants/macros `CHROOT_DIR`, `SOCK_NAME`, `SPAM_MARK`, `BEEF_MARK`; local structs `sockaddr_un`, `io_uring_params`, `tst_io_uring`, `iovec`, `msghdr`, `msghdr`, `io_uring_sqe`, `io_uring_sqe`; headers `stdio.h`, `sys/socket.h`, `sys/un.h`, `tst_test.h`, `tst_safe_io_uring.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `caps, cleanup, needs_tmpdir, save_restore, setup, tags, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring03.c

Purpose: basic `IORING_OP_WRITE` and `IORING_OP_READ` data-integrity tests including split writes. Source comment intent: Test IORING_OP_READ and IORING_OP_WRITE operations. This test validates basic read and write operations using io_uring. It tests: 1. IORING_OP_WRITE - Writing data to a file 2. IORING_OP_READ - Reading data from a file 3. Data integrity verification.

Important APIs/types/functions: core calls `SAFE_OPEN`; local functions `init_buffer`, `verify_data_integrity`, `test_write_read`, `test_partial_io`, `run`, `setup`, `cleanup`; key constants/macros `TEST_FILE`, `QUEUE_DEPTH`, `BLOCK_SZ`; local structs `io_uring_submit`, `tst_test`; headers `io_uring_common.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `bufs, cleanup, needs_tmpdir, save_restore, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring04.c

Purpose: CVE-2026-43494 PinTheft/RDS zerocopy page-pin accounting regression using fixed and cloned io_uring buffers. Source comment intent: CVE-2026-43494 Test for PinTheft, fixed by: e17492979319 ("net/rds: reset op_nents when zerocopy page pin fails"). The bug is in the RDS zerocopy send error path. When RDS pins user pages for zerocopy send and a later page faults, the error cleanup can drop references for pages that are later released again during RDS message cleanup. This corrupts page reference accounting. The public exploit combines this RDS reference-counting bug with io_uring fixed buffers and cloned buffer registrations to turn stale page references into a page-cache overwrite and local privilege escalation. This test does not attempt privilege escalation. It triggers the underlying RDS zerocopy failure path by sending.

Important APIs/types/functions: core calls `io_uring_setup`, `io_uring_register`; local functions `clone_buffers`, `setup`, `trigger`, `poke_rss_accounting`, `run`, `cleanup`; key constants/macros `CLEANUP_WAIT_SECS`, `RSS_CHECK_CHILDREN`, `RSS_CHECK_SIZE`, `GUP_PIN_COUNTING_BIAS`; local structs `io_uring_clone_buffers`, `io_uring_params`, `iovec`, `sockaddr_in`, `sockaddr_in`, `cmsghdr`, `iovec`, `msghdr`; headers `stdint.h`, `tst_test.h`, `lapi/io_uring.h`, `lapi/rds.h`, `lapi/socket.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `cleanup, forks_child, needs_kconfigs, save_restore, setup, tags, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: This is stress/security-sensitive coverage and can expose kernel taint, crashes, or long runtimes on vulnerable or underprovisioned systems.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring_common.h

Purpose: shared raw-ring helper layer for mapping SQ/CQ rings, submitting read/write SQEs, and validating CQEs. Source comment intent: Copyright (C) 2026 IBM Author: Sachin Sant <sachinp@linux.ibm.com> Common definitions and helper functions for io_uring tests.

Important APIs/types/functions: core calls `io_uring_setup`, `io_uring_enter`; local functions `io_uring_setup_queue`, `io_uring_cleanup_queue`, `io_uring_submit_sqe_internal`, `io_uring_submit_sqe`, `io_uring_submit_sqe_vec`, `io_uring_wait_cqe`, `io_uring_init_buffer_pattern`, `io_uring_do_io_op`, `io_uring_do_vec_io_op`; key constants/macros `IO_URING_COMMON_H`; local structs `io_sq_ring`, `io_cq_ring`, `io_uring_cqe`, `io_uring_submit`, `io_sq_ring`, `io_uring_sqe`, `io_cq_ring`, `io_sq_ring`; headers `stdlib.h`, `string.h`, `fcntl.h`, `config.h`, `tst_test.h`, `lapi/io_uring.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `none explicit` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/Makefile

Purpose: targeted syscall behavior in the LTP kernel/syscalls suite.

Important APIs/types/functions: make variables and includes are the important interface here: `INSTALL_TARGETS		+= test_ioctl; ioctl01: LDLIBS+=-lutil; FILTER_OUT_MAKE_TARGETS	+= ioctl02`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl01.c

Purpose: generic ioctl errno coverage for invalid fds, bad termio/termios pointers, invalid commands, regular files, and NULL args. Source comment intent: Copyright (c) International Business Machines Corp., 2001 Copyright (c) 2020 Petr Vorel <petr.vorel@gmail.com> Copyright (c) Linux Test Project, 2002-2024 07/2001 Ported by Wayne Boyer 04/2002 Fixes by wjhuie.

Important APIs/types/functions: core calls `ioctl`, `openpty`, `SAFE_OPEN`; local functions `verify_ioctl`, `test_bad_addr`, `do_test`, `setup`, `cleanup`; key constants/macros `INVAL_IOCTL`; local structs `termio`, `termios`, `tcase`, `tcase`, `tst_test`; headers `errno.h`, `fcntl.h`, `stdio.h`, `termios.h`, `pty.h`, `tst_test.h`, `lapi/ioctl.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, forks_child, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl02.c

Purpose: TTY `TCGETA`/`TCGETS` and `TCSETA`/`TCSETS` round-trip checks using a parent/child tty device workflow. Source comment intent: Test TCGETA/TCGETS and TCSETA/TCSETS ioctl implementations for tty driver. In this test, the parent and child open the parentty and the childtty respectively. After opening the childtty the child flushes the stream and wakes the parent (thereby asking it to continue its testing). The parent, then starts the testing. It issues a TCGETA/TCGETS ioctl to get all the tty parameters. It then changes them to known values by issuing a TCSETA/TCSETS ioctl. Then the parent issues a TCSETA/TCGETS ioctl again and compares the received values with what it had set earlier. The test fails if TCGETA/TCGETS or TCSETA/TCSETS fails, or if the received values don't match those that were set. The parent does all.

Important APIs/types/functions: core calls `SAFE_OPEN`, `SAFE_IOCTL`; local functions `do_child`, `prepare_termio`, `run_ptest`, `chk_tty_parms_termio`, `chk_tty_parms_termios`, `setup`, `cleanup`, `verify_ioctl`, `prepare_termio`, `run_ptest`, `cmp_attr`, `cmp_c_cc`, `chk_tty_parms_termio`, `chk_tty_parms_termios`, `do_child`, `setup`, `cleanup`; key constants/macros `CMP_ATTR`, `CMP_C_CC`; local structs `termio`, `termios`, `variant`, `variant`, `tst_test`; headers `stdio.h`, `stdlib.h`, `asm/termbits.h`, `lapi/ioctl.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, forks_child, needs_checkpoints, needs_root, options, setup, test_all, test_variants, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Variant coverage depends on syscall availability and kernel time ABI support.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl03.c

Purpose: `TUNGETFEATURES` feature-bit enumeration for `/dev/net/tun` or Android `/dev/tun`. Source comment intent: Copyright (c) International Business Machines Corp., 2008 Copyright (c) Linux Test Project, 2017-2019 Author: Rusty Russell <rusty@rustcorp.com.au> Ported to LTP: subrata <subrata@linux.vnet.ibm.com> Test ioriginally written for kernel 2.6.27..

Important APIs/types/functions: core calls `SAFE_IOCTL`; local functions `verify_features`; key constants/macros `TUNGETFEATURES`, `IFF_VNET_HDR`, `IFF_MULTI_QUEUE`, `IFF_NAPI`, `IFF_NAPI_FRAGS`, `IFF_NO_CARRIER`; local structs `tst_test`; headers `sys/types.h`, `sys/ioctl.h`, `sys/stat.h`, `fcntl.h`, `errno.h`, `linux/if_tun.h`, `tst_test.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `needs_root, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl04.c

Purpose: block read-only state via `BLKROGET`/`BLKROSET`, verified by read-write and read-only mount attempts. Source comment intent: Basic test for :manpage:`ioctl(2)` with BLKROSET and BLKROGET . - Set the device read only, read the value back. - Try to mount the device read write, expect failure. - Try to mount the device read only, expect success..

Important APIs/types/functions: core calls `ioctl`, `mount`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl`, `setup`, `cleanup`; local structs `tst_test`; headers `errno.h`, `sys/mount.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, format_device, needs_root, setup, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl05.c

Purpose: block-device size consistency between `BLKGETSIZE` and `BLKGETSIZE64`, plus EOF behavior at device end. Source comment intent: Basic test for :manpage:`ioctl(2)` with BLKGETSIZE and BLKGETSIZE64. - BLKGETSIZE returns size in 512 byte blocks BLKGETSIZE64 in bytes compare that they return the same value. - lseek to the end of the device, this should work - try to read from the device, read should return 0.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl`, `cleanup`; local structs `tst_test`; headers `stdint.h`, `errno.h`, `sys/mount.h`, `tst_test.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, needs_device, needs_root, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl06.c

Purpose: block read-ahead round trips with `BLKRASET`/`BLKRAGET` and restoration of the original setting. Source comment intent: Basic test for :manpage:`ioctl(2)` with BLKRASET and BLKRAGET. Sets device read-ahead, reads it back and compares the values. The read-ahead value was choosen to be multiple of 512, since it's rounded based on page size on BLKRASET and 512 should be safe enough for everyone..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl`, `setup`, `cleanup`; local structs `tst_test`; headers `errno.h`, `sys/mount.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, needs_device, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl07.c

Purpose: random entropy count comparison between `RNDGETENTCNT` and `/proc/sys/kernel/random/entropy_avail`. Source comment intent: Very basic test for the RND* :manpage:`ioctl(2)`. Reads the entropy available from both /proc and the ioctl and compares they are similar enough (within a configured fuzz factor)..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl`, `setup`, `cleanup`; local structs `tst_test`; headers `asm/types.h`, `linux/random.h`, `stdlib.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, options, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl08.c

Purpose: btrfs `FIDEDUPERANGE` same/different/invalid-length cases and per-destination status validation. Source comment intent: Tests :manpage:`ioctl(2)` functionality to deduplicate fileranges using btrfs filesystem. 1. Sets the same contents for two files and deduplicates it. Deduplicates 3 bytes and set the status to FILE_DEDUPE_RANGE_SAME. 2. Sets different content for two files and tries to deduplicate it. 0 bytes get deduplicated and status is set to FILE_DEDUPE_RANGE_DIFFERS. 3. Sets same content for two files but sets the length to deduplicate to -1. ioctl(FIDEDUPERANGE) fails with EINVAL..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `verify_ioctl`, `cleanup`, `setup`; key constants/macros `SUCCESS`, `MNTPOINT`, `FILE_SRC_PATH`, `FILE_DEST_PATH`; local structs `file_dedupe_range`, `tcase`, `tcase`, `tst_test`; headers `config.h`, `stdlib.h`, `sys/ioctl.h`, `errno.h`, `tst_test.h`, `linux/fs.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, filesystems, min_kver, mount_device, needs_root, setup, tcnt, test, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl09.c

Purpose: `BLKRRPART` partition reread on a loop device after `parted` modifies the partition table. Source comment intent: Basic test for :manpage:`ioctl(2)` with BLKRRPART, it is the same as blockdev --rereadpt command..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `check_partition`, `verify_ioctl`, `setup`, `cleanup`; key constants/macros `RETVAL_CHECK`; local structs `loop_info`, `tst_test`; headers `stdio.h`, `unistd.h`, `string.h`, `sys/mount.h`, `stdbool.h`, `lapi/loop.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, needs_cmds, needs_kconfigs, needs_root, needs_tmpdir, setup, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl10.c

Purpose: `PROCMAP_QUERY` ioctl coverage for exact VMA lookup, no-match ENOENT, next-VMA lookup, writable filtering, and VMA name export. Source comment intent: Test PROCMAP_QUERY :manpage:`ioctl(2)` for /proc/$PID/maps. Test based on :kselftest:`proc/proc-pid-vm.c`. - ioctl with exact match query_addr - ioctl without match query_addr - check COVERING_OR_NEXT_VMA query_flags - check PROCMAP_QUERY_VMA_WRITABLE query_flags - check vma_name_addr content.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `parse_vm_flags`, `parse_maps_file`, `verify_ioctl`, `setup`, `cleanup`; key constants/macros `PROC_MAP_PATH`; local structs `map_entry`, `procmap_query`, `map_entry`, `procmap_query`, `tst_test`; headers `config.h`, `stdlib.h`, `sys/ioctl.h`, `errno.h`, `fnmatch.h`, `tst_test.h`, `tst_safe_stdio.h`, `sys/sysmacros.h`, `linux/fs.h`, `lapi/ioctl.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `bufs, cleanup, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone01.c

Purpose: whole-file reflink clone, inode/size/content checks, and copy-on-write isolation after destination modification. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONE feature clones file content from one file to an another. [Algorithm] - populate source file - clone source content inside destination file - verify that source content has been cloned inside destination file - write a single byte inside destination file - verify that source content didn't change while destination did.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `run`, `cleanup`; key constants/macros `MNTPOINT`, `SRCPATH`, `DSTPATH`, `FILEDATA`, `FILESIZE`; local structs `stat`, `stat`, `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `cleanup, filesystems, min_kver, mount_device, needs_root, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone02.c

Purpose: `FICLONERANGE` whole-file clone with `file_clone_range` on mounted reflink filesystems. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONE/FICLONERANGE feature correctly raises EOPNOTSUPP when an unsupported filesystem is used. In particular, filesystems which don't support copy-on-write..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `run`, `setup`; key constants/macros `MNTPOINT`, `SRCPATH`, `DSTPATH`; local structs `file_clone_range`, `stat`, `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `bufs, min_kver, mount_device, needs_root, setup, skip_filesystems, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone03.c

Purpose: negative `FICLONERANGE` cases covering invalid, read-only/write-only, directory, immutable, and mount file descriptors. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONE/FICLONERANGE feature correctly raises exceptions when it's supposed to..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `run`, `setup`, `cleanup`; key constants/macros `MNTPOINT`; local structs `file_clone_range`, `tcase`, `tcase`, `stat`, `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `bufs, cleanup, filesystems, min_kver, mount_device, needs_root, setup, tcnt, test, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone04.c

Purpose: generic bad-fd matrix for `FICLONE` using LTP `tst_fd` descriptors. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONE/FICLONERANGE feature raises the right error according with bad file descriptors..

Important APIs/types/functions: core calls `ioctl`; local functions `test_bad_fd`, `run`; local structs `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `min_kver, needs_root, needs_tmpdir, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlonerange01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlonerange01.c

Purpose: partial-range reflink clone with offset/length checks and copy-on-write source preservation. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONERANGE feature clones file content from one file to an another. [Algorithm] - populate source file - clone a portion of source content inside destination file - verify that source content portion has been cloned inside destination file - write a single byte inside destination file - verify that source content didn't change while destination did.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `run`, `setup`, `cleanup`; key constants/macros `MNTPOINT`, `SRCPATH`, `DSTPATH`, `CHUNKS`; local structs `file_clone_range`, `stat`, `stat`, `stat`, `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `bufs, cleanup, filesystems, min_kver, mount_device, needs_root, setup, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlonerange01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlonerange02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlonerange02.c

Purpose: reflink clone alignment/size validation using filesystem block-size-derived ranges. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONERANGE feature correctly raises EINVAL when: - filesystem does not support overlapping reflink ranges in the same file - filesystem does not support reflinking on bad blocks alignment.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `run`, `setup`, `cleanup`; key constants/macros `MNTPOINT`, `SRCPATH`, `DSTPATH`, `CHUNKS`; local structs `file_clone_range`, `stat`, `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `bufs, cleanup, filesystems, min_kver, mount_device, needs_root, setup, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlonerange02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_fiemap01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_fiemap01.c

Purpose: `FS_IOC_FIEMAP` extent reporting for sparse file layout and expected extent flags. Source comment intent: Verify basic fiemap ioctl functionality, including: - The ioctl returns EBADR if it receives invalid fm_flags. - 0 extents are reported for an empty file. - The ioctl correctly retrieves single and multiple extent mappings after writing to the file..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `print_extens`, `check_extent_count`, `check_extent`, `verify_ioctl`, `setup`; key constants/macros `MNTPOINT`, `TESTFILE`, `NUM_EXTENT`; local structs `fiemap_extent`, `fiemap`, `statvfs`, `tst_test`; headers `linux/fs.h`, `linux/fiemap.h`, `stdlib.h`, `sys/statvfs.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `mount_device, needs_root, setup, skip_filesystems, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_fiemap01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_getlbmd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_getlbmd01.c

Purpose: `BLKGETLBMDCAPS` logical block metadata capability probing on block and regular-file fds. Source comment intent: Verify :manpage:`ioctl(2)` with FS_IOC_GETLBMD_CAP on block devices. - fill struct logical_block_metadata_cap with non-zero pattern, call FS_IOC_GETLBMD_CAP on a block device without integrity support and verify the kernel zeroed out all fields - call FS_IOC_GETLBMD_CAP on a regular file and verify it fails with ENOTTY.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `run`, `setup`, `cleanup`; local structs `logical_block_metadata_cap`, `tst_test`; headers `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `bufs, cleanup, min_kver, needs_device, needs_kconfigs, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_getlbmd01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop01.c

Purpose: loop status flag coverage for AUTOCLEAR, PARTSCAN, READ_ONLY, and DIRECT_IO with sysfs state checks. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Copyright (c) Linux Test Project, 2020-2022 Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `check_loop_value`, `verify_ioctl_loop`, `setup`, `cleanup`; key constants/macros `SET_FLAGS`, `GET_FLAGS`; local structs `loop_info`, `tst_test`; headers `stdio.h`, `unistd.h`, `string.h`, `lapi/loop.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates temporary backing files and loop-device attachments, then checks sysfs and ioctl-visible loop state before detaching.

Dependencies and integration points: integrates with loop-control ioctls, backing files, sysfs state, and root-only block-device behavior. Harness metadata `cleanup, needs_cmds, needs_kconfigs, needs_root, needs_tmpdir, setup, tags, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop02.c

Purpose: `LOOP_CHANGE_FD` and `LOOP_CONFIGURE` behavior for changing read-only loop backing files. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Copyright (c) Linux Test Project, 2022 Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl_loop`, `setup`, `cleanup`; local structs `loop_config`, `tcase`, `tcase`, `loop_info`, `tst_test`; headers `stdio.h`, `unistd.h`, `string.h`, `stdlib.h`, `lapi/loop.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates temporary backing files and loop-device attachments, then checks sysfs and ioctl-visible loop state before detaching.

Dependencies and integration points: integrates with loop-control ioctls, backing files, sysfs state, and root-only block-device behavior. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop03.c

Purpose: `LOOP_CHANGE_FD` must fail with EINVAL when the loop device is not read-only. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Copyright (c) Linux Test Project, 2022 Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl_loop`, `setup`, `cleanup`; local structs `loop_info`, `tst_test`; headers `stdio.h`, `unistd.h`, `string.h`, `lapi/loop.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates temporary backing files and loop-device attachments, then checks sysfs and ioctl-visible loop state before detaching.

Dependencies and integration points: integrates with loop-control ioctls, backing files, sysfs state, and root-only block-device behavior. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop04.c

Purpose: `LOOP_SET_CAPACITY` after shrinking a backing file and matching loop sysfs size. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Copyright (c) Linux Test Project, 2022 Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl_loop`, `setup`, `cleanup`; key constants/macros `OLD_SIZE`, `NEW_SIZE`; local structs `loop_info`, `tst_test`; headers `stdio.h`, `unistd.h`, `string.h`, `stdlib.h`, `lapi/loop.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates temporary backing files and loop-device attachments, then checks sysfs and ioctl-visible loop state before detaching.

Dependencies and integration points: integrates with loop-control ioctls, backing files, sysfs state, and root-only block-device behavior. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop05.c

Purpose: `LOOP_SET_DIRECT_IO` mode toggles and alignment-sensitive offset behavior. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Copyright (c) Linux Test Project, 2020-2022 Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `check_dio_value`, `verify_ioctl_loop`, `setup`, `cleanup`; key constants/macros `DIO_MESSAGE`, `NON_DIO_MESSAGE`; local structs `loop_info`, `loop_info`, `tst_test`; headers `stdio.h`, `unistd.h`, `string.h`, `stdlib.h`, `sys/mount.h`, `lapi/loop.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates temporary backing files and loop-device attachments, then checks sysfs and ioctl-visible loop state before detaching.

Dependencies and integration points: integrates with loop-control ioctls, backing files, sysfs state, and root-only block-device behavior. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, skip_filesystems, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop06.c

Purpose: invalid loop block-size rejection through `LOOP_SET_BLOCK_SIZE` and `LOOP_CONFIGURE`. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Copyright (c) Linux Test Project, 2022 Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `verify_ioctl_loop`, `run`, `setup`, `cleanup`; local structs `loop_config`, `tcase`, `tcase`, `tst_test`; headers `stdio.h`, `unistd.h`, `sys/types.h`, `stdlib.h`, `lapi/blkdev.h`, `lapi/loop.h`, `tst_fs.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates temporary backing files and loop-device attachments, then checks sysfs and ioctl-visible loop state before detaching.

Dependencies and integration points: integrates with loop-control ioctls, backing files, sysfs state, and root-only block-device behavior. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop07.c

Purpose: `lo_sizelimit` effects through `LOOP_SET_STATUS64`, `LOOP_GET_STATUS64`, and `LOOP_CONFIGURE`. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Copyright (c) Linux Test Project, 2022 Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl_loop`, `run`, `setup`, `cleanup`; local structs `loop_config`, `tcase`, `tcase`, `loop_info64`, `tcase`, `tst_test`; headers `stdio.h`, `unistd.h`, `sys/types.h`, `stdlib.h`, `lapi/loop.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates temporary backing files and loop-device attachments, then checks sysfs and ioctl-visible loop state before detaching.

Dependencies and integration points: integrates with loop-control ioctls, backing files, sysfs state, and root-only block-device behavior. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, tags, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns01.c

Purpose: `NS_GET_PARENT` EPERM behavior for the initial PID namespace and a new child PID namespace. Source comment intent: Copyright (c) 2019 Federico Bonfiglio <fedebonfi95@gmail.com> Copyright (c) Linux Test Project, 2019-2022.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `setup`, `cleanup`, `test_ns_get_parent`, `child`, `run`; key constants/macros `_GNU_SOURCE`, `STACK_SIZE`; local structs `tst_test`; headers `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/ioctl_ns.h`, `lapi/sched.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with namespace file-descriptor ioctls under `/proc/*/ns`. Harness metadata `cleanup, forks_child, min_kver, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns02.c

Purpose: `NS_GET_PARENT` on nonhierarchical UTS namespace returning EINVAL. Source comment intent: Copyright (c) 2019 Federico Bonfiglio <fedebonfi95@gmail.com> Copyright (c) Linux Test Project, 2019-2022.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `setup`, `run`; key constants/macros `_GNU_SOURCE`; local structs `tst_test`; headers `errno.h`, `tst_test.h`, `lapi/ioctl_ns.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with namespace file-descriptor ioctls under `/proc/*/ns`. Harness metadata `min_kver, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns03.c

Purpose: `NS_GET_OWNER_UID` on non-user UTS namespace returning EINVAL. Source comment intent: Copyright (c) 2019 Federico Bonfiglio <fedebonfi95@gmail.com> Copyright (c) Linux Test Project, 2019-2022.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `setup`, `run`; key constants/macros `_GNU_SOURCE`; local structs `tst_test`; headers `errno.h`, `tst_test.h`, `lapi/ioctl_ns.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with namespace file-descriptor ioctls under `/proc/*/ns`. Harness metadata `min_kver, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns04.c

Purpose: `NS_GET_USERNS` on out-of-scope owning user namespace returning EPERM. Source comment intent: Copyright (c) 2019 Federico Bonfiglio <fedebonfi95@gmail.com> Copyright (c) Linux Test Project, 2019-2022.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `setup`, `run`; key constants/macros `_GNU_SOURCE`; local structs `tst_test`; headers `errno.h`, `tst_test.h`, `lapi/ioctl_ns.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with namespace file-descriptor ioctls under `/proc/*/ns`. Harness metadata `min_kver, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns05.c

Purpose: `NS_GET_PARENT` returns a parent PID namespace fd that matches the caller's namespace and differs from the child. Source comment intent: Copyright (c) 2019 Federico Bonfiglio <fedebonfi95@gmail.com> Copyright (c) Linux Test Project, 2019-2022.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `setup`, `cleanup`, `child`, `run`; key constants/macros `_GNU_SOURCE`, `STACK_SIZE`; local structs `stat`, `tst_test`; headers `errno.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/ioctl_ns.h`, `lapi/sched.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with namespace file-descriptor ioctls under `/proc/*/ns`. Harness metadata `cleanup, forks_child, min_kver, needs_checkpoints, needs_kconfigs, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns06.c

Purpose: `NS_GET_USERNS` returns the owning user namespace of a CLONE_NEWUSER child. Source comment intent: Copyright (c) 2019 Federico Bonfiglio <fedebonfi95@gmail.com> Copyright (c) Linux Test Project, 2019-2022.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `setup`, `cleanup`, `child`, `run`; key constants/macros `_GNU_SOURCE`, `STACK_SIZE`; local structs `stat`, `tst_test`; headers `errno.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/ioctl_ns.h`, `lapi/sched.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with namespace file-descriptor ioctls under `/proc/*/ns`. Harness metadata `cleanup, forks_child, min_kver, needs_checkpoints, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns07.c

Purpose: namespace ioctl requests against non-namespace file descriptors returning ENOTTY. Source comment intent: Copyright (c) 2019 Federico Bonfiglio <fedebonfi95@gmail.com> Copyright (c) Linux Test Project, 2022.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `test_request`; key constants/macros `_GNU_SOURCE`; local structs `tst_test`; headers `errno.h`, `tst_test.h`, `lapi/ioctl_ns.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with namespace file-descriptor ioctls under `/proc/*/ns`. Harness metadata `min_kver, needs_tmpdir, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd.h

Purpose: targeted syscall behavior in the LTP kernel/syscalls suite. Source comment intent: SPDX-License-Identifier: GPL-2.0-or-later.

Important APIs/types/functions: core calls `ioctl`; local functions `ioctl_pidfd_get_info_supported`, `ioctl_pidfd_info_exit_supported`; key constants/macros `IOCTL_PIDFD_H`; local structs `pidfd_info`, `pidfd_info`; headers `tst_test.h`, `lapi/pidfd.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `none explicit` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd01.c

Purpose: bad file descriptors for `PIDFD_GET_INFO` fail with allowed descriptor-specific errno values. Source comment intent: Verify that :manpage:`ioctl(2)` raises the right errors when an application provides wrong file descriptor..

Important APIs/types/functions: core calls `ioctl`; local functions `test_bad_pidfd`, `run`, `setup`; local structs `pidfd_info`, `tst_test`; headers `ioctl_pidfd.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `bufs, forks_child, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd02.c

Purpose: child exit-code retrieval via `PIDFD_INFO_EXIT` before and after reaping, with isolated and non-isolated children. Source comment intent: Copyright (c) 2025 Andrea Cervesato <andrea.cervesato@suse.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_IOCTL`; local functions `run`, `setup`; local structs `tst_clone_args`, `pidfd_info`, `tst_test`; headers `ioctl_pidfd.h`, `lapi/sched.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `bufs, forks_child, needs_checkpoints, needs_kconfigs, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd03.c

Purpose: isolated child `PIDFD_GET_INFO` without `PIDFD_INFO_EXIT` mask eventually returns ESRCH after reap. Source comment intent: Verify that :manpage:`ioctl(2)` returns ESRCH when a process attempts to access the exit status of an isolated child using PIDFD_GET_INFO and PIDFD_INFO_EXIT is not defined in struct pidfd_info..

Important APIs/types/functions: core calls `ioctl`, `SAFE_IOCTL`; local functions `run`, `setup`; local structs `tst_clone_args`, `pidfd_info`, `tst_test`; headers `ioctl_pidfd.h`, `lapi/sched.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `bufs, forks_child, needs_kconfigs, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd04.c

Purpose: signaled isolated child exit status is exported through `PIDFD_INFO_EXIT` and matches wait status. Source comment intent: Verify that :manpage:`ioctl(2)` permits to obtain the exit code of an isolated signaled child via PIDFD_INFO_EXIT from within a process..

Important APIs/types/functions: core calls `ioctl`, `SAFE_IOCTL`; local functions `run`, `setup`; local structs `tst_clone_args`, `pidfd_info`, `tst_test`; headers `ioctl_pidfd.h`, `lapi/sched.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `bufs, forks_child, needs_checkpoints, needs_kconfigs, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd05.c

Purpose: NULL and short extensible `PIDFD_GET_INFO` arguments fail with EINVAL or ENOTTY depending on kernel validation. Source comment intent: Verify that :manpage:`ioctl(2)` raises an EINVAL or ENOTTY (since v6.18-rc1) error when PIDFD_GET_INFO is used. This happens when: - info parameter is NULL - info parameter is providing the wrong size.

Important APIs/types/functions: core calls `ioctl`; local functions `run`, `setup`; key constants/macros `PIDFD_GET_INFO_SHORT`; local structs `pidfd_info_invalid`, `tst_clone_args`, `pidfd_info_invalid`, `tst_test`; headers `tst_test.h`, `lapi/pidfd.h`, `lapi/sched.h`, `errno.h`, `ioctl_pidfd.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `bufs, forks_child, needs_kconfigs, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd06.c

Purpose: another isolated process cannot retrieve a reaped isolated process exit status; expected ESRCH or newer EREMOTE. Source comment intent: Verify that :manpage:`ioctl(2)` doesn't allow to obtain the exit status of an isolated process via PIDFD_INFO_EXIT in within an another isolated process, which doesn't have any parent connection..

Important APIs/types/functions: core calls `ioctl`; local functions `run`, `setup`; local structs `tst_clone_args`, `pidfd_info`, `tst_test`; headers `ioctl_pidfd.h`, `lapi/sched.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `bufs, forks_child, needs_kconfigs, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_sg01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_sg01.c

Purpose: CVE-2018-1000204 `SG_IO` leak regression using a readable generic SCSI device and zeroed output buffer checks. Source comment intent: CVE-2018-1000204 Test ioctl(SG_IO) and check that kernel doesn't leak data. Requires a read-accessible generic SCSI device (e.g. a DVD drive). Leak fixed in: commit a45b599ad808c3c982fdcdc12b0b8611c2f92824 Author: Alexander Potapenko <glider@google.com> Date: Fri May 18 16:23:18 2018 +0200 scsi: sg: allocate with __GFP_ZERO in sg_build_indirect() commit 41e99fe2005182139b1058db71f0d241f8f0078c Author: Desnes Nunes <desnesn@redhat.com> Date: Fri Oct 31 01:34:36 2025 -0300 usb: storage: Fix memory leak in USB bulk transport.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `dump_hex`, `setup`, `cleanup`, `run`; key constants/macros `SYSDIR`, `BLOCKDIR`, `BUF_SIZE`, `CMD_SIZE`; local structs `sg_io_hdr`, `dirent`, `tst_test`; headers `sys/types.h`, `dirent.h`, `fcntl.h`, `unistd.h`, `ctype.h`, `scsi/sg.h`, `sys/ioctl.h`, `stdio.h`, `tst_test.h`, `tst_memutils.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, setup, tags, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: This is stress/security-sensitive coverage and can expose kernel taint, crashes, or long runtimes on vulnerable or underprovisioned systems.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_sg01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/test_ioctl -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/test_ioctl

Purpose: legacy shell harness for running `ioctl02` against usable tty devices discovered under `/dev/tty*`.

Important APIs/types/functions: shell functions `has_tty`, `stty -F`, `tst_resm`, `ioctl02 -d`, and `tst_exit`.

Control flow: exports LTP legacy counters, iterates numeric tty device names, skips unusable ttys, runs `ioctl02` with the device path, and reports TPASS/TFAIL from the child program exit status.

State and persistence behavior: no durable state beyond invoking `ioctl02`; it probes terminal devices and relies on the child test to restore tty attributes.

Dependencies and integration points: installed by the ioctl Makefile as `test_ioctl`; depends on the legacy LTP shell API and on `ioctl02` being built and reachable in PATH.

Risks: device enumeration is host-dependent, and the `has_tty` helper treats `stty` failures as skip candidates, so coverage varies by console configuration.

Test signals: emits TPASS/TFAIL per tty based on `ioctl02`'s exit code and exits through the LTP shell harness.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/test_ioctl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/Makefile

Purpose: targeted syscall behavior in the LTP kernel/syscalls suite.

Important APIs/types/functions: make variables and includes are the important interface here: `top_srcdir, testcases.mk, generic_leaf_target.mk`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with x86 I/O-port permission bitmap changes and privilege checks; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/ioperm01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/ioperm01.c

Purpose: successful x86 `ioperm` enablement for a small port range near the I/O bitmap limit. Source comment intent: Copyright (c) Linux Test Project, 2020 Copyright (c) Wipro Technologies Ltd, 2002.

Important APIs/types/functions: core calls `ioperm`; local functions `verify_ioperm`, `setup`, `cleanup`; key constants/macros `NUM_BYTES`, `IO_BITMAP_BITS`; local structs `tst_test`; headers `errno.h`, `unistd.h`, `tst_test.h`, `sys/io.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: changes per-process I/O privilege state and restores it in cleanup where applicable.

Dependencies and integration points: integrates with x86 I/O-port permission bitmap changes and privilege checks. Harness metadata `cleanup, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/ioperm01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/ioperm02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/ioperm02.c

Purpose: negative x86 `ioperm` cases for invalid high port ranges and unprivileged EPERM. Source comment intent: Copyright (c) Linux Test Project, 2020 Copyright (c) Wipro Technologies Ltd, 2002.

Important APIs/types/functions: core calls `ioperm`; local functions `setup`, `cleanup`, `verify_ioperm`; key constants/macros `NUM_BYTES`, `IO_BITMAP_BITS`, `IO_BITMAP_BITS_16`; local structs `tcase_t`, `passwd`, `tst_test`; headers `stdlib.h`, `errno.h`, `unistd.h`, `pwd.h`, `tst_test.h`, `tst_safe_macros.h`, `sys/io.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: changes per-process I/O privilege state and restores it in cleanup where applicable.

Dependencies and integration points: integrates with x86 I/O-port permission bitmap changes and privilege checks. Harness metadata `cleanup, needs_root, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/ioperm02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/iopl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/iopl/Makefile

Purpose: targeted syscall behavior in the LTP kernel/syscalls suite.

Important APIs/types/functions: make variables and includes are the important interface here: `top_srcdir, testcases.mk, generic_leaf_target.mk`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with x86 I/O privilege level changes and error handling; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/iopl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/iopl/iopl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/iopl/iopl01.c

Purpose: successful x86 `iopl` transitions through privilege levels 0..3 and cleanup back to 0. Source comment intent: Copyright (c) Linux Test Project, 2003-2024 Copyright (c) Wipro Technologies Ltd, 2002 Author: Subhab Biswas <subhabrata.biswas@wipro.com>.

Important APIs/types/functions: core calls `iopl`; local functions `verify_iopl`, `cleanup`; local structs `tst_test`; headers `errno.h`, `unistd.h`, `tst_test.h`, `sys/io.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: changes per-process I/O privilege state and restores it in cleanup where applicable.

Dependencies and integration points: integrates with x86 I/O privilege level changes and error handling. Harness metadata `cleanup, needs_root, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/iopl/iopl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/iopl/iopl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/iopl/iopl02.c

Purpose: negative x86 `iopl` cases for level 4 EINVAL and unprivileged EPERM. Source comment intent: Copyright (c) Linux Test Project, 2020 Copyright (c) Wipro Technologies Ltd, 2002 Author: Subhab Biswas <subhabrata.biswas@wipro.com>.

Important APIs/types/functions: core calls `iopl`; local functions `verify_iopl`, `setup`, `cleanup`; local structs `tcase`, `passwd`, `tst_test`; headers `errno.h`, `unistd.h`, `pwd.h`, `tst_test.h`, `tst_safe_macros.h`, `sys/io.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: changes per-process I/O privilege state and restores it in cleanup where applicable.

Dependencies and integration points: integrates with x86 I/O privilege level changes and error handling. Harness metadata `cleanup, needs_root, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/iopl/iopl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/Makefile

Purpose: targeted syscall behavior in the LTP kernel/syscalls suite.

Important APIs/types/functions: make variables and includes are the important interface here: `top_srcdir, testcases.mk, generic_leaf_target.mk`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with I/O priority syscall wrappers, class/priority encoding, and readback validation; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio.h

Purpose: shared wrappers and validation helpers around raw `ioprio_get`/`ioprio_set` syscalls. Source comment intent: Copyright (c) 2019 Linus Walleij <linus.walleij@linaro.org> Copyright (c) 2023 Linux Test Project.

Important APIs/types/functions: local functions `sys_ioprio_get`, `sys_ioprio_set`, `prio_in_range`, `class_in_range`, `ioprio_check_setting`; key constants/macros `LTP_IOPRIO_H`; headers `lapi/ioprio.h`, `lapi/syscalls.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: updates current-process I/O priority and validates the kernel-reported encoded class/priority value.

Dependencies and integration points: integrates with I/O priority syscall wrappers, class/priority encoding, and readback validation. Harness metadata `none explicit` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_get01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_get01.c

Purpose: current-process I/O priority readback with class and priority range validation. Source comment intent: Copyright (c) 2019 Linus Walleij <linus.walleij@linaro.org> Copyright (c) 2023 Linux Test Project.

Important APIs/types/functions: core calls `ioprio_get`; local functions `run`; local structs `tst_test`; headers `tst_test.h`, `ioprio.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with I/O priority syscall wrappers, class/priority encoding, and readback validation. Harness metadata `test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_get01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set01.c

Purpose: best-effort priority adjustment up and down from the current value with readback verification. Source comment intent: Copyright (c) 2019 Linus Walleij <linus.walleij@linaro.org> Copyright (c) 2019-2023 Linux Test Project.

Important APIs/types/functions: core calls `ioprio_set`; local functions `run`, `setup`; local structs `tst_test`; headers `tst_test.h`, `ioprio.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with I/O priority syscall wrappers, class/priority encoding, and readback validation. Harness metadata `setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set02.c

Purpose: setting every best-effort and idle priority level plus class NONE. Source comment intent: Copyright (c) 2019 Linus Walleij <linus.walleij@linaro.org> Copyright (c) 2023 Linux Test Project.

Important APIs/types/functions: core calls `ioprio_set`; local functions `run`; local structs `tst_test`; headers `tst_test.h`, `ioprio.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with I/O priority syscall wrappers, class/priority encoding, and readback validation. Harness metadata `test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set03.c

Purpose: invalid priority values must fail without changing the prior effective priority. Source comment intent: Copyright (c) 2019 Linus Walleij <linus.walleij@linaro.org> Copyright (c) 2023 Linux Test Project.

Important APIs/types/functions: core calls `ioprio_set`; local functions `run`; local structs `tst_test`; headers `tst_test.h`, `ioprio.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with I/O priority syscall wrappers, class/priority encoding, and readback validation. Harness metadata `test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/Makefile

Purpose: IPC trunk makefile delegates to child syscall subdirectories through LTP generic trunk rules.

Important APIs/types/functions: make variables and includes are the important interface here: `top_srcdir, testcases.mk, generic_leaf_target.mk`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with the local LTP make include stack and test binary linkage; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/Makefile

Purpose: links SysV message queue tests with `-lltpnewipc` helper library.

Important APIs/types/functions: make variables and includes are the important interface here: `LTPLIBS = newipc; LTPLDLIBS  = -lltpnewipc`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl01.c

Purpose: `IPC_STAT` metadata on a new message queue: times, queue counts, permissions, key, uid/gid, and byte limits. Source comment intent: Test that IPC_STAT command succeeds and the buffer is filled with correct data..

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgctl`, `setup`, `cleanup`; local structs `msqid_ds`, `tst_test`; headers `errno.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `cleanup, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl02.c

Purpose: `IPC_SET` lowers `msg_qbytes` and restores original queue metadata. Source comment intent: Copyright (c) International Business Machines Corp., 2001 03/2001 - Written by Wayne Boyer Copyright (c) 2018 Cyril Hrubis <chrubis@suse.cz>.

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgctl`, `setup`, `cleanup`; local structs `msqid_ds`, `msqid_ds`, `tst_test`; headers `errno.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `cleanup, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl03.c

Purpose: `IPC_RMID` removes a queue and subsequent `IPC_STAT` reports EINVAL. Source comment intent: DESCRIPTION msgctl13 - test for IPC_RMID.

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`; local functions `verify_msgctl`; local structs `msqid_ds`, `tst_test`; headers `errno.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `needs_tmpdir, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl04.c

Purpose: message-control EACCES/EFAULT/EINVAL/EPERM matrix across libc and raw syscall variants. Source comment intent: Test for EACCES, EFAULT and EINVAL errors using a variety of incorrect calls..

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `libc_msgctl`, `sys_msgctl`, `verify_msgctl`, `setup`, `cleanup`; local structs `msqid_ds`, `tcase`, `msqid_ds`, `test_variants`, `test_variants`, `test_variants`, `passwd`, `tst_test`; headers `errno.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`, `lapi/syscalls.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `cleanup, needs_root, needs_tmpdir, setup, tcnt, test, test_variants` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter. Variant coverage depends on syscall availability and kernel time ABI support.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl05.c

Purpose: kernel clearing of msqid64 high time fields during `IPC_STAT`. Source comment intent: Cross verify the _high fields being set to 0 by the kernel..

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `run`; local structs `msqid64_ds`, `tst_test`; headers `sys/msg.h`, `lapi/msgbuf.h`, `tse_newipc.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `needs_tmpdir, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl06.c

Purpose: `MSG_INFO`/`MSG_STAT_ANY` indexes and counts are cross-checked against `/proc/sysvipc/msg` as root and nobody. Source comment intent: Call msgctl() with MSG_INFO flag and check that: * The returned index points to a valid MSG by calling MSG_STAT_ANY * Also count that valid indexes < returned max index sums up to used_ids * And the data are consistent with /proc/sysvipc/msg There is a possible race between the call to the msgctl() and read from the proc file so this test cannot be run in parallel with any IPC testcases that adds or removes MSG queues. Note what we create a MSG segment in the test setup and send msg to make sure that there is at least one during the testrun. Also note that for MSG_INFO the members of the msginfo structure have completely different meaning than their names seems to suggest..

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `parse_proc_sysvipc`, `verify_msgctl`, `setup`, `cleanup`; local structs `passwd`, `tcases`, `tcases`, `msqid_ds`, `msginfo`, `msqid_ds`, `buf`, `tst_test`; headers `stdio.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`, `lapi/msg.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `cleanup, needs_root, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl12.c

Purpose: positive `IPC_INFO`, `MSG_INFO`, and `MSG_STAT` message-control commands. Source comment intent: msgctl12 - test for IPC_INFO MSG_INFO and MSG_STAT..

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgctl`, `setup`, `cleanup`; key constants/macros `_GNU_SOURCE`; local structs `msginfo`, `msqid_ds`, `tcase`, `tst_test`; headers `errno.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `cleanup, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/Makefile

Purpose: links SysV message queue tests with `-lltpnewipc` helper library.

Important APIs/types/functions: make variables and includes are the important interface here: `LTPLIBS = newipc; LTPLDLIBS  = -lltpnewipc`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget01.c

Purpose: queue creation followed by send/receive round trip for a generated IPC key. Source comment intent: Copyright (c) International Business Machines Corp., 2001.

Important APIs/types/functions: core calls `msgget`, `SAFE_MSGCTL`, `SAFE_MSGSND`, `SAFE_MSGRCV`; local functions `verify_msgget`, `setup`, `cleanup`; local structs `buf`, `tst_test`; headers `errno.h`, `string.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls. Harness metadata `cleanup, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget02.c

Purpose: `msgget` EEXIST, ENOENT, and EACCES cases with root and nobody execution paths. Source comment intent: Test for EEXIST, ENOENT, EACCES errors. - msgget(2) fails if a message queue exists for key and msgflg specified both IPC_CREAT and IPC_EXCL. - msgget(2) fails if no message queue exists for key and msgflg did not specify IPC_CREAT. - msgget(2) fails if a message queue exists for key, but the calling process does not have permission to access the queue, and does not have the CAP_IPC_OWNER capability..

Important APIs/types/functions: core calls `msgget`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgget`, `do_test`, `setup`, `cleanup`; local structs `passwd`, `tcase`, `tcase`, `tst_test`; headers `errno.h`, `stdlib.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls. Harness metadata `cleanup, forks_child, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget03.c

Purpose: controlled `MSGMNI` exhaustion to force `msgget` ENOSPC, with sysctl save/restore. Source comment intent: Test for ENOSPC error. ENOSPC - All possible message queues have been taken (MSGMNI).

Important APIs/types/functions: core calls `msgget`, `SAFE_MSGCTL`; local functions `verify_msgget`, `setup`, `cleanup`; local structs `tst_test`; headers `errno.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `stdlib.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls. Harness metadata `cleanup, needs_tmpdir, save_restore, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget04.c

Purpose: `msg_next_id` desired identifier allocation and reset to -1 after successful queue creation. Source comment intent: It is a basic test for msg_next_id. msg_next_id specifies desired id for next allocated IPC message. By default it's equal to -1, which means generic allocation logic. Possible values to set are in range {0..INT_MAX}. The value will be set back to -1 by kernel after successful IPC object allocation..

Important APIs/types/functions: core calls `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgget`, `setup`, `cleanup`; key constants/macros `NEXT_ID_PATH`; local structs `tst_test`; headers `errno.h`, `string.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls. Harness metadata `cleanup, needs_kconfigs, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget05.c

Purpose: `msg_next_id` collision behavior when the desired message queue id is already in use. Source comment intent: It is a basic test for msg_next_id. When the message queue identifier that msg_next_id stored is already in use, call msgget with different key just use another unused value in range [0,INT_MAX]. Kernel doesn't guarantee the desired id..

Important APIs/types/functions: core calls `msgget`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgget`, `setup`, `cleanup`; key constants/macros `NEXT_ID_PATH`; local structs `tst_test`; headers `errno.h`, `string.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls. Harness metadata `cleanup, needs_kconfigs, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/Makefile

Purpose: links SysV message queue tests with `-lltpnewipc` helper library.

Important APIs/types/functions: make variables and includes are the important interface here: `LTPLIBS = newipc; LTPLDLIBS  = -lltpnewipc`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv01.c

Purpose: successful receive, payload match, queue counters, last-receiver pid, and receive timestamp update. Source comment intent: Copyright (c) International Business Machines Corp., 2001 msgrcv01 - test that msgrcv() receives the expected message.

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `verify_msgrcv`, `setup`, `cleanup`; local structs `buf`, `msqid_ds`, `tst_test`; headers `string.h`, `sys/wait.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tst_clocks.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv02.c

Purpose: receive error matrix for E2BIG, EACCES, EFAULT, EINVAL, and ENOMSG. Source comment intent: Copyright (c) International Business Machines Corp., 2001 Basic error test for msgrcv(2). 1)msgrcv(2) fails and sets errno to E2BIG if the message text length is greater than msgsz and MSG_NOERROR isn't specified in msgflg. 2)The calling process does not have read permission on the message queue, so msgrcv(2) fails and sets errno to EACCES. 3)msgrcv(2) fails and sets errno to EFAULT if the message buffer address isn't accessible. 4)msgrcv(2) fails and sets errno to EINVAL if msqid was invalid(<0). 5)msgrcv(2) fails and sets errno to EINVAL if msgsize is less than 0. 6)msgrcv(2) fails and sets errno to ENOMSG if IPC_NOWAIT was specified in msgflg and no message of the requested type existed o.

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `verify_msgrcv`, `do_test`, `setup`, `cleanup`; key constants/macros `_GNU_SOURCE`; local structs `passwd`, `buf`, `tcase`, `buf`, `tcase`, `tst_test`; headers `string.h`, `sys/wait.h`, `sys/msg.h`, `stdlib.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, forks_child, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv03.c

Purpose: invalid `MSG_COPY` flag combinations and out-of-range copy index behavior. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com> This is a basic test about MSG_COPY flag. This flag was added in 3.8 for the implementation of the kernel checkpoint restore facility and is available only if the kernel was built with the CONFIG_CHECKPOINT_RESTORE option. On old kernel without this support, it only ignores this flag and doesn't report ENOSYS/EINVAL error. The CONFIG_CHECKPOINT_RESTORE has existed before kernel 3.8. So for using this flag, kernel should greater than 3.8 and enable CONFIG_CHECKPOINT_RESTORE together. 1)msgrcv(2) fails and sets errno to EINVAL if IPC_NOWAIT was not specified in msgflag. 2)msgrcv(2) fails and.

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `verify_msgrcv`, `setup`, `cleanup`; key constants/macros `_GNU_SOURCE`; local structs `buf`, `tcase`, `tcase`, `tst_test`; headers `string.h`, `sys/wait.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`, `lapi/msg.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv05.c

Purpose: blocking `msgrcv` interrupted by SIGHUP returns EINTR. Source comment intent: Copyright (c) International Business Machines Corp., 2001 msgrcv error test for EINTR..

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `sighandler`, `verify_msgrcv`, `do_test`, `setup`, `cleanup`; local structs `buf`, `tst_test`; headers `sys/types.h`, `sys/wait.h`, `signal.h`, `stdlib.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, forks_child, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv06.c

Purpose: blocking `msgrcv` returns EIDRM when the queue is removed while the child sleeps. Source comment intent: Copyright (c) International Business Machines Corp., 2001 msgrcv error test for EIDRM..

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgrcv`, `do_test`, `setup`, `cleanup`; local structs `buf`, `tst_test`; headers `errno.h`, `unistd.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `stdlib.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, forks_child, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv07.c

Purpose: `MSG_EXCEPT`, `MSG_NOERROR`, `MSG_COPY`, and positive/zero/negative message type selection semantics. Source comment intent: Copyright (c) 2014-2020 Fujitsu Ltd. Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> Author: Yang Xu <xuyang2018.jy@cn.fujitsu.com> Basic test for msgrcv(2) using MSG_EXCEPT, MSG_NOERROR, MSG_COPY and different msg_typ(zero,positive,negative). * With MSG_EXCEPT flag any message type but the one passed to the function is received. * With MSG_NOERROR and buffer size less than message size only part of the buffer is received. * With MSG_COPY and IPC_NOWAIT flag read the msg but don't destroy it in msg queue. * With msgtyp is 0, then the first message in the queue is read. * With msgtyp is greater than 0, then the first message in the queue of type msgtyp is read. * With msgtyp is less than .

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `prepare_queue`, `test_msg_except`, `test_msg_noerror`, `test_msg_copy`, `test_zero_msgtyp`, `test_positive_msgtyp`, `test_negative_msgtyp`, `cleanup`, `setup`, `verify_msgcrv`; key constants/macros `_GNU_SOURCE`, `MSGTYPE1`, `MSGTYPE2`, `MSG1`, `MSG2`; local structs `buf`, `msqid_ds`, `tst_test`; headers `sys/wait.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`, `lapi/msg.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv08.c

Purpose: compat regression for negative `msgtyp` receive selecting the expected positive message type. Source comment intent: Copyright (c) 2015 Author: Gabriellla Schmidt <gsc@bruker.de> Modify: Li Wang <liwang@redhat.com> A regression test for: commit e7ca2552369c1dfe0216c626baf82c3d83ec36bb Author: Mateusz Guzik <mguzik@redhat.com> Date: Mon Jan 27 17:07:11 2014 -0800 ipc: fix compat msgrcv with negative msgtyp Reproduce: 32-bit application using the msgrcv() system call gives the error message: msgrcv: No message of desired type If this progarm is compiled as 64-bit application it works..

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `verify_msgrcv`, `setup`, `cleanup`; local structs `mbuf`, `tst_test`; headers `stdio.h`, `string.h`, `unistd.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, needs_tmpdir, setup, tags, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/Makefile

Purpose: links SysV message queue tests with `-lltpnewipc` helper library.

Important APIs/types/functions: make variables and includes are the important interface here: `LTPLIBS = newipc; LTPLDLIBS  += -lltpnewipc`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with enqueue behavior, full-queue blocking, permissions, and metadata updates; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd01.c

Purpose: successful send updates queue byte/count metadata, last-sender pid, and send timestamp. Source comment intent: Copyright (c) International Business Machines Corp., 2001 Copyright (c) Linux Test Project, 2002-2024.

Important APIs/types/functions: core calls `msgsnd`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGRCV`; local functions `verify_msgsnd`, `setup`, `cleanup`; local structs `buf`, `msqid_ds`, `tst_test`; headers `errno.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tst_clocks.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with enqueue behavior, full-queue blocking, permissions, and metadata updates. Harness metadata `cleanup, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd02.c

Purpose: send error matrix for EACCES, EFAULT, EINVAL queue id, non-positive types, and negative size. Source comment intent: DESCRIPTION 1) The calling process does not have write permission on the message queue, so msgsnd(2) fails and sets errno to EACCES. 2) msgsnd(2) fails and sets errno to EFAULT if the message buffer address is invalid. 3) msgsnd(2) fails and sets errno to EINVAL if the queue ID is invalid. 4) msgsnd(2) fails and sets errno to EINVAL if the message type is not positive (0). 5) msgsnd(2) fails and sets errno to EINVAL if the message type is not positive (>0). 6) msgsnd(2) fails and sets errno to EINVAL if the message size is less than zero..

Important APIs/types/functions: core calls `msgsnd`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgsnd`, `do_test`, `setup`, `cleanup`; local structs `passwd`, `buf`, `tcase`, `buf`, `tcase`, `tst_test`; headers `errno.h`, `string.h`, `stdlib.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with enqueue behavior, full-queue blocking, permissions, and metadata updates. Harness metadata `cleanup, forks_child, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd05.c

Purpose: full-queue `msgsnd` EAGAIN with IPC_NOWAIT and EINTR for a blocking sender interrupted by SIGHUP. Source comment intent: Copyright (c) International Business Machines Corp., 2001 Copyright (c) Linux Test Project, 2002-2024.

Important APIs/types/functions: core calls `msgsnd`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgsnd`, `sighandler`, `do_test`, `setup`, `cleanup`; local structs `buf`, `tcase`, `tcase`, `tst_test`; headers `errno.h`, `unistd.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with enqueue behavior, full-queue blocking, permissions, and metadata updates. Harness metadata `cleanup, forks_child, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd06.c

Purpose: blocking full-queue sender returns EIDRM when the queue is removed. Source comment intent: DESCRIPTION Tests if EIDRM is returned when message queue was removed while msgsnd() was trying to send a message..

Important APIs/types/functions: core calls `msgsnd`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgsnd`, `do_test`, `setup`, `cleanup`; local structs `buf`, `tst_test`; headers `errno.h`, `unistd.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with enqueue behavior, full-queue blocking, permissions, and metadata updates. Harness metadata `cleanup, forks_child, needs_root, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgstress/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgstress/Makefile

Purpose: targeted syscall behavior in the LTP kernel/syscalls suite.

Important APIs/types/functions: make variables and includes are the important interface here: `top_srcdir, testcases.mk, generic_leaf_target.mk`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with concurrent sender/receiver integrity under queue and process pressure; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgstress/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgstress/msgstress01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgstress/msgstress01.c

Purpose: multi-process SysV message stress with paired writer/reader children and shared-memory result flags. Source comment intent: Stress test for SysV IPC. We send multiple messages at the same time, checking that we are not loosing any byte once we receive the messages from multiple children. The number of messages to send is determined by the free slots available in SysV IPC and the available number of children which can be spawned by the process. Each sender will spawn multiple messages at the same time and each receiver will read them one by one..

Important APIs/types/functions: core calls `msgrcv`, `msgsnd`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `get_used_sysvipc`, `reset_messages`, `create_message`, `writer`, `reader`, `remove_queues`, `run`, `setup`, `cleanup`; key constants/macros `SYSVIPC_TOTAL`, `SYSVIPC_USED`, `MSGTYPE`, `MAXNREPS`; local structs `sysv_msg`, `sysv_data`, `sysv_msg`, `sysv_data`, `sysv_data`, `sysv_data`, `sysv_msg`, `sysv_data`; headers `stdlib.h`, `tst_safe_sysv_ipc.h`, `tst_safe_stdio.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with concurrent sender/receiver integrity under queue and process pressure. Harness metadata `cleanup, forks_child, options, runtime, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: This is stress/security-sensitive coverage and can expose kernel taint, crashes, or long runtimes on vulnerable or underprovisioned systems. SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgstress/msgstress01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/Makefile

Purpose: links semaphore tests against `ltpipc` or `ltpnewipc` depending on legacy/new LTP harness usage.

Important APIs/types/functions: make variables and includes are the important interface here: `LTPLIBS = ipc newipc; semctl06: LTPLDLIBS = -lltpipc; semctl02 semctl03 semctl04 semctl05 semctl07 semctl08 semctl09: LTPLDLIBS = -lltpnewipc`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl01.c

Purpose: broad `semctl` command sweep: IPC_STAT/SET/RMID, GET/SETALL, GET/SETVAL, counters, PID, and IPC/SEM info. Source comment intent: Test the 13 possible semctl() commands.

Important APIs/types/functions: core calls `semctl`, `semop`, `SAFE_SEMGET`, `SAFE_SEMCTL`, `SAFE_SEMOP`; local functions `kill_all_children`, `func_stat`, `set_setup`, `func_set`, `func_gall`, `child_cnt`, `cnt_setup`, `func_cnt`, `child_pid`, `pid_setup`, `func_pid`, `func_gval`, `sall_setup`, `func_sall`, `func_sval`, `func_rmid`, `func_iinfo`, `func_sinfo`; key constants/macros `_GNU_SOURCE`, `INCVAL`, `NEWMODE`, `NCHILD`, `SEMUN_CAST`; local structs `semid_ds`, `seminfo`, `sembuf`, `tcases`, `tcases`, `tst_test`; headers `stdlib.h`, `tst_safe_sysv_ipc.h`, `tst_test.h`, `lapi/sem.h`, `tse_newipc.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability. Harness metadata `cleanup, forks_child, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl02.c

Purpose: `semctl(IPC_STAT)` EACCES as nobody on a semaphore without read permissions. Source comment intent: Test for semctl() EACCES error..

Important APIs/types/functions: core calls `semctl`, `SAFE_SEMGET`, `SAFE_SEMCTL`; local functions `verify_semctl`, `setup`, `cleanup`; local structs `semid_ds`, `passwd`, `tst_test`; headers `pwd.h`, `tst_safe_sysv_ipc.h`, `tst_test.h`, `lapi/sem.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability. Harness metadata `cleanup, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl03.c

Purpose: `semctl` EINVAL and EFAULT cases across libc and raw syscall variants. Source comment intent: Test for semctl() EINVAL and EFAULT errors.

Important APIs/types/functions: core calls `semctl`, `SAFE_SEMGET`, `SAFE_SEMCTL`; local functions `libc_semctl`, `sys_semctl`, `verify_semctl`, `setup`, `cleanup`; local structs `semid_ds`, `tcases`, `test_variants`, `tcases`, `test_variants`, `test_variants`, `tst_test`; headers `tst_safe_sysv_ipc.h`, `tst_test.h`, `lapi/sem.h`, `tse_newipc.h`, `lapi/syscalls.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability. Harness metadata `cleanup, setup, tcnt, test, test_variants` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter. Variant coverage depends on syscall availability and kernel time ABI support.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl04.c

Purpose: unprivileged child EPERM for `IPC_SET` and `IPC_RMID` on a root-created semaphore set. Source comment intent: Test for semctl() EPERM error Runs IPC_SET and IPC_RMID from unprivileged child process..

Important APIs/types/functions: core calls `semctl`, `SAFE_SEMGET`, `SAFE_SEMCTL`; local functions `do_child`, `verify_semctl`, `setup`, `cleanup`; local structs `semid_ds`, `passwd`, `tst_test`; headers `pwd.h`, `sys/wait.h`, `tst_safe_sysv_ipc.h`, `tst_test.h`, `lapi/sem.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability. Harness metadata `cleanup, forks_child, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl05.c

Purpose: `semctl` ERANGE for negative or too-large SETVAL/SETALL values. Source comment intent: Test for semctl() ERANGE error.

Important APIs/types/functions: core calls `semctl`, `SAFE_SEMGET`, `SAFE_SEMCTL`; local functions `verify_semctl`, `setup`, `cleanup`; key constants/macros `BIGV`; local structs `tcases`, `tcases`, `tst_test`; headers `tst_safe_sysv_ipc.h`, `tst_test.h`, `lapi/sem.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability. Harness metadata `cleanup, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl06.c

Purpose: legacy concurrent semaphore stress preserving random semaphore maxima across many `SEM_UNDO` operations. Source comment intent: NAME semctl06 CALLS semctl(2) semget(2) semop(2) ALGORITHM Get and manipulate a set of semaphores. RESTRICTIONS WARNING If this test fail, it may be necessary to use the ipcs and ipcrm commands to remove any semaphores left in the system due to a premature exit of this test. HISTORY 06/30/2001 Port to Linux nsharoff@us.ibm.com 10/30/2002 Port to LTP dbarrera@us.ibm.com 12/03/2008 Matthieu Fertré (Matthieu.Fertre@irisa.fr) - Fix concurrency issue. The IPC keys used for this test could conflict with keys from another task..

Important APIs/types/functions: core calls `semctl`, `semget`, `semop`; local functions `setup`, `cleanup`, `term`, `dosemas`, `dotest`, `main`, `dotest`, `dosemas`, `term`, `setup`, `cleanup`; key constants/macros `DEBUG`, `NREPS`, `NPROCS`, `NKIDS`, `NSEMS`, `HVAL`, `LVAL`, `FAILED`; local structs `sembuf`; headers `sys/types.h`, `sys/ipc.h`, `sys/sem.h`, `unistd.h`, `errno.h`, `stdlib.h`, `signal.h`, `test.h`, `sys/wait.h`, `tse_ipcsem.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability. Harness metadata `none explicit` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: This is stress/security-sensitive coverage and can expose kernel taint, crashes, or long runtimes on vulnerable or underprovisioned systems. SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl07.c

Purpose: basic `semctl` metadata, SETVAL/GETVAL, GETPID, GETNCNT, and GETZCNT checks. Source comment intent: Copyright (c) International Business Machines Corp., 2002 HISTORY 06/30/2001 Port to Linux nsharoff@us.ibm.com 10/30/2002 Port to LTP dbarrera@us.ibm.com 10/03/2008 Renaud Lottiaux (Renaud.Lottiaux@kerlabs.com) - Fix concurrency issue. A statically defined key was used. Leading to conflict with other instances of the same test..

Important APIs/types/functions: core calls `semctl`, `SAFE_SEMGET`, `SAFE_SEMCTL`; local functions `verify_semctl`, `setup`, `cleanup`; local structs `semid_ds`, `tst_test`; headers `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`, `lapi/sem.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability. Harness metadata `cleanup, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl08.c

Purpose: verification that kernel clears semid64 high time fields during IPC_STAT. Source comment intent: Cross verify the _high fields being set to 0 by the kernel..

Important APIs/types/functions: core calls `semctl`, `semget`; local functions `run`; local structs `semid64_ds`, `tst_test`; headers `lapi/sembuf.h`, `lapi/sem.h`, `tst_test.h`, `tse_newipc.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability. Harness metadata `needs_tmpdir, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl08.c -->
