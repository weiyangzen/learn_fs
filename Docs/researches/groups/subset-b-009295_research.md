# subset-b-009295 research

Grouped research report for LTP syscall tests covering eventfd, exec, exit, access, fadvise, fallocate, and fanotify sources. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd02.c

Purpose: Checks core `eventfd()` write semantics and error handling on a nonblocking descriptor.

Important APIs/types/functions: `eventfd(0, EFD_NONBLOCK)`, `SAFE_WRITE`, `SAFE_READ`, raw `write()`, `TST_EXP_FD`, `TST_EXP_FAIL`, `TST_EXP_EQ_LI`, and the `CONFIG_EVENTFD` kconfig requirement.

Control flow: The test creates an eventfd, writes value 12, reads it back, fills the counter to `UINT64_MAX - 1`, verifies a further write returns `EAGAIN`, verifies short writes return `EINVAL`, then verifies writing `UINT64_MAX` is rejected.

State and persistence behavior: The only kernel state is the in-kernel eventfd counter and descriptor flags. The counter is explicitly drained once and then saturated to exercise boundary behavior.

Dependencies and integration points: Runs through the LTP `struct tst_test` `.test_all` path and requires `CONFIG_EVENTFD`; no tmpdir or fork support is needed.

Risks and test signals: Boundary arithmetic is the risk: if counter saturation or buffer-size validation regresses, the fail/pass macros expose wrong errno or value. The source comment mentions zero/nonblocking behavior, but this implementation primarily validates write saturation and invalid write formats.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd03.c

Purpose: Verifies `select()` read readiness for an eventfd follows the counter being nonzero versus zero.

Important APIs/types/functions: `eventfd`, `fd_set`, `FD_ZERO`, `FD_SET`, `FD_ISSET`, `select()`, zero-timeout `timeval`, `SAFE_WRITE`, and `SAFE_READ`.

Control flow: After creating a nonblocking eventfd, the test writes 10, calls `select()` with the descriptor in the read set and expects readiness, drains the counter, calls `select()` again, and expects the descriptor not to be set.

State and persistence behavior: State is the eventfd counter. A write makes it readable; a full 8-byte read resets the counter to zero and removes read readiness.

Dependencies and integration points: Integrated with LTP result macros and `CONFIG_EVENTFD`; it relies on normal `select()` fdset mutation semantics.

Risks and test signals: The same `fd_set` is reused after `select()`, so the test depends on the previous ready bit still being present until the second call clears it. Failures show as wrong readiness or `select()` errors.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd04.c

Purpose: Verifies `select()` write readiness for eventfd descriptors below and at the maximum counter value.

Important APIs/types/functions: `eventfd`, `select()`, write fd sets, `SAFE_WRITE`, `SAFE_READ`, and the `UINT64_MAX - 1` eventfd saturation boundary.

Control flow: The test writes a small value and expects write readiness, drains that value, writes `UINT64_MAX - 1`, calls `select()` again with the descriptor in the write set, and expects it not to be writable.

State and persistence behavior: The eventfd counter is the relevant state: writable while another write can be accepted, not writable once the counter is saturated.

Dependencies and integration points: Runs as a single LTP test requiring `CONFIG_EVENTFD`; no persistent filesystem state is involved.

Risks and test signals: This is sensitive to exact eventfd readiness semantics and fdset mutation. A kernel that allows overflow-prone writes or misreports `POLLOUT` readiness would fail.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd05.c

Purpose: Checks that eventfd descriptors shared across `fork()` expose child counter updates to the parent.

Important APIs/types/functions: `eventfd`, `SAFE_FORK`, `SAFE_WRITE`, `tst_reap_children`, `SAFE_READ`, and `.forks_child = 1`.

Control flow: The parent creates a nonblocking eventfd, the child writes `0xdeadbeef` and exits, the parent reaps the child, reads the counter, and compares the returned value.

State and persistence behavior: The kernel eventfd object persists across fork through the inherited open file description; no durable storage is used.

Dependencies and integration points: Uses LTP fork management and `CONFIG_EVENTFD`; the expected behavior comes from file descriptor inheritance.

Risks and test signals: Failures indicate broken fork inheritance, eventfd counter sharing, or child write/read ordering. Reaping before the read removes scheduling races.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd06.c

Purpose: Exercises eventfd overflow notification through Linux AIO, where kernel-space completion increments can overflow a saturated eventfd counter.

Important APIs/types/functions: `libaio` APIs `io_setup`, `io_prep_pwrite`, `io_set_eventfd`, `io_submit`, `io_getevents`, `poll()`, `select()`, `eventfd`, `SAFE_OPEN`, and feature guards `HAVE_LIBAIO`/`HAVE_IO_SET_EVENTFD`.

Control flow: `setup()` initializes an AIO context, opens a temp file, and creates a nonblocking eventfd. Each subtest clears any pending counter, writes `UINT64_MAX - 1`, submits one async pwrite tied to the eventfd, then checks overflow state through `select()` or `poll()` and finally reads `UINT64_MAX`.

State and persistence behavior: Persistent state is limited to a temporary file used for AIO writes. Kernel state includes the AIO context, eventfd counter, and readiness/error flags produced by overflow.

Dependencies and integration points: Requires libaio, AIO eventfd support, a tmpdir, and `CONFIG_EVENTFD`. Unsupported kernels or build configurations return `TCONF` rather than false failures.

Risks and test signals: Overflow can only be reached by kernel-side increments, so the AIO path is essential. The select subtest currently uses the regular file descriptor in the fdset while reading `evfd` for the counter; that makes this source worth reviewing if the intended readiness check is specifically the eventfd descriptor. Poll explicitly checks `POLLERR` on `evfd`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. No local compiler overrides are needed for the eventfd2 syscall wrapper tests.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2.h

Purpose: Provides a small LTP-local wrapper for invoking the raw `eventfd2` syscall by number.

Important APIs/types/functions: `tst_syscall(__NR_eventfd2, count, flags)`, `lapi/syscalls.h`, `tst_brk(TBROK | TERRNO)`, and an inline `eventfd2()` helper.

Control flow: The helper calls the syscall and aborts the test on `-1`; otherwise it returns the new file descriptor to callers.

State and persistence behavior: No persistent state is stored in the header. It centralizes syscall invocation and error policy for all eventfd2 tests.

Dependencies and integration points: Used by `eventfd2_01.c`, `_02.c`, and `_03.c` to avoid depending on libc exporting `eventfd2()` directly.

Risks and test signals: Because the wrapper breaks on any syscall failure, tests that need to assert negative `eventfd2` behavior would require a different helper. Current users only test successful creation and flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_01.c

Purpose: Verifies that `eventfd2()` honors `EFD_CLOEXEC` by setting `FD_CLOEXEC` on the returned descriptor.

Important APIs/types/functions: `eventfd2()` from the local header, `SAFE_FCNTL(fd, F_GETFD)`, `FD_CLOEXEC`, `TST_EXP_EXPR`, and `SAFE_CLOSE`.

Control flow: The test creates one descriptor without flags and expects no close-on-exec bit, closes it, then creates another descriptor with `EFD_CLOEXEC` and expects the bit to be present.

State and persistence behavior: State is descriptor metadata in the per-process file descriptor table; no filesystem or counter persistence matters.

Dependencies and integration points: Integrates the raw syscall wrapper with POSIX `fcntl` flag inspection.

Risks and test signals: A regression in flag propagation or wrapper argument order is detected as a mismatched `FD_CLOEXEC` bit.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_02.c

Purpose: Verifies that `eventfd2()` honors `EFD_NONBLOCK` by setting `O_NONBLOCK` on the open file description.

Important APIs/types/functions: `eventfd2()`, `SAFE_FCNTL(fd, F_GETFL)`, `O_NONBLOCK`, `TST_EXP_EXPR`, and `SAFE_CLOSE`.

Control flow: It creates a descriptor without flags and asserts blocking mode, then creates one with `EFD_NONBLOCK` and asserts nonblocking mode.

State and persistence behavior: Only descriptor status flags are stateful; no counter operations are performed.

Dependencies and integration points: Uses the same local wrapper as other eventfd2 tests and LTP assertion macros.

Risks and test signals: The signal is direct flag inspection, so failures point to eventfd2 flag handling rather than read/write behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_03.c

Purpose: Validates eventfd semaphore mode by coordinating two forked processes through two `EFD_SEMAPHORE` descriptors.

Important APIs/types/functions: `eventfd2(0, EFD_SEMAPHORE)`, `SAFE_READ`, `SAFE_WRITE`, `SAFE_FORK`, `exit()`, and helper functions `xsem_wait`, `xsem_post`, and `sem_player`.

Control flow: The parent creates two semaphore eventfds and forks two children. Each child posts once to the other side, waits once, posts five units, then performs five waits on the opposite descriptor and reports success.

State and persistence behavior: The eventfd counters act as semaphores: each read consumes one unit instead of draining the full counter. Descriptors are inherited across fork.

Dependencies and integration points: Depends on eventfd2 syscall support and LTP child reaping through `.forks_child = 1`; no explicit parent assertions are needed beyond child results.

Risks and test signals: Deadlock would expose broken semaphore decrement semantics or lost fork inheritance. The test relies on the harness to reap both children after `.test_all` returns.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execl/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It builds the `execl01` parent and `execl01_child` helper together.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execl/execl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execl/execl01.c

Purpose: Tests successful `execl()` replacement of a forked child with a helper binary and varargs argument passing.

Important APIs/types/functions: `tst_get_path()`, `SAFE_FORK`, `execl(path, "execl01_child", "canary", NULL)`, `TEST()`, and LTP fork reinitialization settings.

Control flow: The parent locates `execl01_child`, forks, and the child calls `execl`. If `execl` returns, the child reports `TFAIL`; otherwise the helper validates the canary.

State and persistence behavior: Process image replacement and argv contents are the only state under test. The test sets unlimited stack via `.ulimit` to avoid environment-specific exec argument stack issues.

Dependencies and integration points: Integrated with `execl01_child.c` and `$PATH` resource discovery.

Risks and test signals: Failure can be an inability to locate the helper, failed exec, or child-side argument mismatch. Successful exec is signaled by the helper's `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execl/execl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execl/execl01_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execl/execl01_child.c

Purpose: Helper executable for the `execl` wrapper test. It is intentionally tiny so success means the parent really replaced the child image with this program.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `strcmp()`, `tst_brk()`, and `tst_res()` from the LTP harness.

Control flow: `main()` reinitializes LTP state after exec, validates `argc == 2` and `argv[1] == "canary"`, emits `TPASS`, and returns 0.

State and persistence behavior: No durable state is created; the process image and inherited environment/arguments are the state under test.

Dependencies and integration points: Consumed by the neighboring parent test through `$PATH` lookup or an absolute path discovered with `tst_get_path()`.

Risks and test signals: The helper is a sentinel: any argument/environment mismatch, missing harness reinit, or unexpected execution path produces `TFAIL`; parent-side exec failure is reported before this helper runs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execl/execl01_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execle/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execle/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It builds the `execle01` parent and environment-checking child helper.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execle/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execle/execle01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execle/execle01.c

Purpose: Tests `execle()` argument passing and explicit environment replacement.

Important APIs/types/functions: `execle()`, `tst_get_path`, `SAFE_FORK`, `IPC_ENV_VAR`, and an `envp` containing `LTP_TEST_ENV_VAR=test` plus the LTP IPC variable.

Control flow: The parent builds a minimal environment, locates the helper, forks, and the child invokes `execle`. Returning from exec is reported as a failure.

State and persistence behavior: The environment vector is the important transient state; it deliberately omits `PATH` while preserving the LTP IPC variable needed by `tst_reinit()`.

Dependencies and integration points: Works with `execle01_child.c`, which checks argv and environment content.

Risks and test signals: Risk is omitting harness-required IPC state or accidentally inheriting environment variables. The child catches missing custom env and unexpected `PATH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execle/execle01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execle/execle01_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execle/execle01_child.c

Purpose: Helper executable for the `execle` wrapper test. It is intentionally tiny so success means the parent really replaced the child image with this program.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `strcmp()`, `tst_brk()`, and `tst_res()` from the LTP harness.

Control flow: `main()` reinitializes LTP state after exec, validates `argc == 2`, `argv[1] == "canary"`, `LTP_TEST_ENV_VAR=test`, and that `PATH` is absent from the replacement environment, emits `TPASS`, and returns 0.

State and persistence behavior: No durable state is created; the process image and inherited environment/arguments are the state under test.

Dependencies and integration points: Consumed by the neighboring parent test through `$PATH` lookup or an absolute path discovered with `tst_get_path()`.

Risks and test signals: The helper is a sentinel: any argument/environment mismatch, missing harness reinit, or unexpected execution path produces `TFAIL`; parent-side exec failure is reported before this helper runs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execle/execle01_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execlp/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execlp/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It builds the PATH-searching `execlp01` parent and helper.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execlp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execlp/execlp01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execlp/execlp01.c

Purpose: Tests successful `execlp()` PATH search and varargs argument passing.

Important APIs/types/functions: `SAFE_FORK`, `execlp("execlp01_child", ...)`, `TEST()`, `tst_brk()`, and `.child_needs_reinit = 1`.

Control flow: The parent forks; the child calls `execlp` by basename, relying on the test environment PATH. Returning from exec is a failure.

State and persistence behavior: No durable state is used. The process search path and argv are the relevant runtime state.

Dependencies and integration points: Integrated with `execlp01_child.c` and LTP's resource installation/path setup.

Risks and test signals: Failures point to PATH lookup, exec failure, or child-side canary mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execlp/execlp01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execlp/execlp01_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execlp/execlp01_child.c

Purpose: Helper executable for the `execlp` wrapper test. It is intentionally tiny so success means the parent really replaced the child image with this program.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `strcmp()`, `tst_brk()`, and `tst_res()` from the LTP harness.

Control flow: `main()` reinitializes LTP state after exec, validates `argc == 2` and `argv[1] == "canary"`, emits `TPASS`, and returns 0.

State and persistence behavior: No durable state is created; the process image and inherited environment/arguments are the state under test.

Dependencies and integration points: Consumed by the neighboring parent test through `$PATH` lookup or an absolute path discovered with `tst_get_path()`.

Risks and test signals: The helper is a sentinel: any argument/environment mismatch, missing harness reinit, or unexpected execution path produces `TFAIL`; parent-side exec failure is reported before this helper runs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execlp/execlp01_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execv/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execv/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It builds the vector-argument `execv01` parent and helper.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execv/execv01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execv/execv01.c

Purpose: Tests successful `execv()` replacement using an explicit argv vector and resolved helper path.

Important APIs/types/functions: `tst_get_path`, `SAFE_FORK`, `execv(path, args)`, `TEST()`, and LTP child reinitialization.

Control flow: The parent resolves `execv01_child`, forks, and the child calls `execv` with `argv[0]` and a `canary` argument.

State and persistence behavior: The argv vector is transient state; no files are modified by the test itself.

Dependencies and integration points: Integrated with the sibling child helper and LTP resource path lookup.

Risks and test signals: The only success path is the helper running and reporting `TPASS`; any returned exec call is a parent-test failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execv/execv01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execv/execv01_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execv/execv01_child.c

Purpose: Helper executable for the `execv` wrapper test. It is intentionally tiny so success means the parent really replaced the child image with this program.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `strcmp()`, `tst_brk()`, and `tst_res()` from the LTP harness.

Control flow: `main()` reinitializes LTP state after exec, validates `argc == 2` and `argv[1] == "canary"`, emits `TPASS`, and returns 0.

State and persistence behavior: No durable state is created; the process image and inherited environment/arguments are the state under test.

Dependencies and integration points: Consumed by the neighboring parent test through `$PATH` lookup or an absolute path discovered with `tst_get_path()`.

Risks and test signals: The helper is a sentinel: any argument/environment mismatch, missing harness reinit, or unexpected execution path produces `TFAIL`; parent-side exec failure is reported before this helper runs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execv/execv01_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It adds `CPPFLAGS += -I$(abs_srcdir)/../lib` so execve tests can include shared syscall-test helper headers.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve01.c

Purpose: Tests that `execve()` passes argv and an explicit environment to the executed binary.

Important APIs/types/functions: `execve(path, args, envp)`, `tst_get_path`, `SAFE_FORK`, `IPC_ENV_VAR`, and LTP error reporting.

Control flow: The parent builds `args = {"execve01_child", "canary", NULL}` and an env containing `LTP_TEST_ENV_VAR=test` plus LTP IPC state, forks, and the child invokes `execve`.

State and persistence behavior: The replacement environment is intentionally minimal; absence of `PATH` is part of the child-side validation.

Dependencies and integration points: Integrated with `execve01_child.c`, which validates argument and environment contracts.

Risks and test signals: Failures expose execve replacement failure, missing helper discovery, or environment leakage/omission.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve01_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve01_child.c

Purpose: Helper executable for the `execve` wrapper test. It is intentionally tiny so success means the parent really replaced the child image with this program.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `strcmp()`, `tst_brk()`, and `tst_res()` from the LTP harness.

Control flow: `main()` reinitializes LTP state after exec, validates the canary argument, `LTP_TEST_ENV_VAR=test`, and that `PATH` is not inherited, emits `TPASS`, and returns 0.

State and persistence behavior: No durable state is created; the process image and inherited environment/arguments are the state under test.

Dependencies and integration points: Consumed by the neighboring parent test through `$PATH` lookup or an absolute path discovered with `tst_get_path()`.

Risks and test signals: The helper is a sentinel: any argument/environment mismatch, missing harness reinit, or unexpected execution path produces `TFAIL`; parent-side exec failure is reported before this helper runs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve01_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve02.c

Purpose: Verifies `execve()` returns `EACCES` when an unprivileged effective user attempts to execute a root-owned helper lacking execute permission for others.

Important APIs/types/functions: `SAFE_CHMOD`, `SAFE_GETPWNAM("nobody")`, `SAFE_SETEUID`, `execve(TEST_APP, argv, environ)`, and `.needs_root`/`.resource_files`.

Control flow: `setup()` chmods `execve_child` to 0700 and records nobody's uid. The forked child switches euid to nobody, calls `execve`, expects failure, and checks `TST_ERR == EACCES`.

State and persistence behavior: State includes helper file mode bits and the child's effective uid. The parent environment is inherited so the helper could reinitialize if accidentally executed.

Dependencies and integration points: Uses a staged resource helper and root privileges to change credentials safely.

Risks and test signals: If permission checks regress, exec may succeed and the helper reports that it should not have run. Wrong errno also fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve03.c

Purpose: Covers multiple `execve()` errno cases: `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `EFAULT`, `EACCES`, and `ENOEXEC`.

Important APIs/types/functions: `execve`, `SAFE_GETPWNAM`, `SAFE_SETGID`, `SAFE_GETCWD`, `SAFE_CREAT`, `tst_get_bad_addr`, and a table-driven `struct tcase`.

Control flow: `setup()` creates paths and files for each error condition, including a non-executable file and a zero-length executable file. Each testcase calls `execve(tc->tname, argv, NULL)` and compares `TST_ERR` to the expected errno.

State and persistence behavior: Temporary filesystem entries and a bad userspace pointer define the test state. No successful exec should occur.

Dependencies and integration points: Requires root and a tmpdir because it changes gid and creates controlled permission/path states.

Risks and test signals: Path construction and permission setup must match kernel checks; ordering matters because `ENOTDIR` is produced by appending a component beneath a regular file.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve04.c

Purpose: Checks historical `ETXTBSY` behavior when trying to execute a file that another process has open for writing.

Important APIs/types/functions: `SAFE_FORK`, LTP checkpoints, `SAFE_OPEN(TEST_APP, O_WRONLY)`, `execve`, `tst_kvercmp`, and `.resource_files`.

Control flow: The child opens the helper for write and waits at a checkpoint. The parent waits until the writer is active, calls `execve`, expects `ETXTBSY`, and then wakes the child.

State and persistence behavior: The helper's open write reference is the key transient state. No durable mutation is intended.

Dependencies and integration points: Uses LTP checkpoint synchronization and skips on kernels 6.11-rc1 and newer where the kernel deliberately changed `i_writecount` behavior.

Risks and test signals: This is version-sensitive by design. On older kernels, wrong success or wrong errno fails; on newer kernels it reports `TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve05.c

Purpose: Stress-tests concurrent successful `execve()` by spawning several children that all execute the same helper simultaneously.

Important APIs/types/functions: `SAFE_FORK`, `TST_CHECKPOINT_WAIT/WAKE2`, `execve(TEST_APP, argv, environ)`, `SAFE_STRTOL` option parsing, and `.resource_files`.

Control flow: The parent forks `nchild` children. Each child waits at a checkpoint, then all are released to call `execve` with a canary argument. Returning from exec is failure.

State and persistence behavior: The only shared state is checkpoint synchronization and the staged helper binary. The `-n` option controls child count.

Dependencies and integration points: Integrated with `execve_child.c`, which reports pass when invoked with the canary.

Risks and test signals: Risks are scheduler/concurrency sensitivity and timeout pressure; `.timeout = 3` bounds hangs. Failures show as exec returns, child errors, or harness timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve06.c

Purpose: Regression test for empty-argv `execve()` handling related to CVE-2021-4034: the kernel should synthesize a non-null `argv[0]`.

Important APIs/types/functions: `execve(path, argv, envp)` with `argv[] = {NULL}`, `tst_get_path`, `SAFE_FORK`, `IPC_ENV_VAR`, and LTP tags for the fixing kernel commit/CVE.

Control flow: The child process calls `execve` on `execve06_child` with an empty argument list and a minimal environment. If exec succeeds, the helper validates argc/argv.

State and persistence behavior: Process argument vector normalization is the state under test; there is no filesystem mutation beyond locating the helper.

Dependencies and integration points: Integrated with `execve06_child.c` and LTP metadata tags `linux-git dcd46d897adb` and `CVE 2021-4034`.

Risks and test signals: A vulnerable or regressed kernel may present `argc == 0` or `argv[0] == NULL`, which the child reports as failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve06_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve06_child.c

Purpose: Helper for `execve06.c` that validates kernel-synthesized argv state after an empty argument-list exec.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `argc`, `argv[0]`, `tst_res()`, and `TPASS`/`TFAIL`.

Control flow: `main()` expects `argc == 1` and a non-null `argv[0]`, reports failure for either violation, and otherwise reports that the kernel filled argv[0].

State and persistence behavior: No persistent state. The inherited process argument block is the only subject.

Dependencies and integration points: Runs only through `execve06.c`; it depends on the parent preserving LTP IPC environment for `tst_reinit()`.

Risks and test signals: The helper is intentionally not strict about argv[0] contents, only non-null presence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve06_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve_child.c

Purpose: Shared helper for `execve02`, `execve04`, and `execve05`, distinguishing expected successful and forbidden exec paths.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `strcmp()`, `tst_res()`, and return code 0.

Control flow: If invoked with `argv[1] == "canary"`, it reports pass for the concurrent execve05 case. Otherwise it reports failure because execve02/04 are expected not to execute it.

State and persistence behavior: No durable state; its behavior is entirely driven by argv.

Dependencies and integration points: Used as a resource file by multiple execve tests, so it encodes both positive and negative sentinel roles.

Risks and test signals: Misusing this helper in a new test without the canary would report failure by design. It is a guard against forbidden exec success.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It builds execveat parent tests plus the success and errno sentinel helpers.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat.h

Purpose: Provides a feature probe for `execveat()` support.

Important APIs/types/functions: `execveat(-1, "", NULL, NULL, AT_EMPTY_PATH)`, `errno`, and `tst_brk(TCONF)`.

Control flow: `check_execveat()` calls an intentionally invalid execveat form and treats `EINVAL` as meaning the syscall is not supported by the current environment.

State and persistence behavior: No persistent state; it is a runtime capability gate shared by execveat tests.

Dependencies and integration points: Included by all execveat parent test sources before they set up filesystem scenarios.

Risks and test signals: The probe distinguishes unsupported syscall behavior from later testcase errors. If errno conventions change, capability detection could misclassify support.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat01.c

Purpose: Checks basic `execveat()` path resolution modes: relative to dirfd, relative to `AT_FDCWD`, absolute path, and `AT_EMPTY_PATH` via an `O_PATH` fd.

Important APIs/types/functions: `execveat`, `SAFE_MKDIR`, `SAFE_CP`, `SAFE_GETCWD`, `SAFE_OPEN(... O_DIRECTORY/O_PATH)`, `AT_FDCWD`, and `AT_EMPTY_PATH`.

Control flow: `setup()` copies the helper into `testdir`, computes an absolute path, and opens directory/file descriptors. Each testcase forks and the child calls `execveat` with one addressing mode.

State and persistence behavior: State consists of the copied helper, directory fd, `O_PATH` fd, and cwd. Successful exec replaces the child image with `execveat_child`.

Dependencies and integration points: Uses `check_execveat()` and a resource helper staged by LTP.

Risks and test signals: Failures isolate dirfd/pathname semantics. Returning from `execveat` is failure because the helper should run.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat02.c

Purpose: Checks `execveat()` error handling for bad fd, invalid flags, symlink nofollow, and relative pathname under a non-directory fd.

Important APIs/types/functions: `execveat`, `SAFE_SYMLINK`, `SAFE_OPEN(... O_PATH)`, `AT_EMPTY_PATH`, `AT_SYMLINK_NOFOLLOW`, `TST_ERR`, and a table of expected errnos.

Control flow: `setup()` creates a directory, copies the errno helper, builds absolute/symlink paths, and opens the target file with `O_PATH`. Each forked child calls `execveat` and compares errno.

State and persistence behavior: Filesystem state includes a copied executable and symlink. Descriptor state includes a deliberate bad fd and an `O_PATH` fd to a regular file.

Dependencies and integration points: Integrated with `execveat_errno.c`, which should not run in any testcase.

Risks and test signals: If a case unexpectedly executes, the helper reports failure. SELinux or filesystem behavior could alter some errno paths, but the cases target kernel API validation.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat03.c

Purpose: Regression test that an unlinked executable opened with `O_PATH` can still be executed by `execveat(..., AT_EMPTY_PATH)` on overlayfs.

Important APIs/types/functions: `SAFE_CP`, `SAFE_OPEN(... O_PATH)`, `SAFE_UNLINK`, `execveat`, `AT_EMPTY_PATH`, overlayfs mount support, and root-required LTP mount fields.

Control flow: The child copies the helper onto the overlay mount, opens it with `O_PATH`, unlinks it, and calls `execveat` by fd. A returned syscall is failure.

State and persistence behavior: The open file reference persists after unlink; overlay dentry/file capability lookup state is the regression target.

Dependencies and integration points: Requires root, a mounted overlayfs test device, `check_execveat()`, and the `execveat_child` helper.

Risks and test signals: Tagged for commits introducing and fixing the regression. Unsupported overlayfs or syscall support yields configuration skip rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat_child.c

Purpose: Success sentinel for `execveat01.c` and `execveat03.c`.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, and `tst_res(TPASS)`.

Control flow: `main()` reinitializes the LTP harness, emits a pass message, and exits 0.

State and persistence behavior: No state is modified; its execution is the observable success of the parent execveat call.

Dependencies and integration points: Used as a resource file copied into test directories and overlay mounts.

Risks and test signals: If a parent expected failure uses this helper accidentally, it would report pass, so negative tests use `execveat_errno.c` instead.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat_errno.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat_errno.c

Purpose: Failure sentinel for `execveat02.c` negative errno cases.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, and `tst_res(TFAIL)`.

Control flow: `main()` reports that `execveat()` passed unexpectedly and returns 0.

State and persistence behavior: No persistent state; it only proves an expected-failure execveat case reached a new image.

Dependencies and integration points: Used by `execveat02.c` as a resource helper that should never successfully execute.

Risks and test signals: Any run of this helper means the parent accepted an invalid execveat combination.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat_errno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execvp/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execvp/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It builds the PATH-searching vector `execvp01` parent and helper.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execvp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execvp/execvp01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execvp/execvp01.c

Purpose: Tests successful `execvp()` PATH search with vector-style argv.

Important APIs/types/functions: `SAFE_FORK`, `execvp("execvp01_child", args)`, `tst_brk()`, and `.child_needs_reinit = 1`.

Control flow: The child calls `execvp` by basename with a canary argument. If the call returns, it reports failure.

State and persistence behavior: Runtime state is the PATH lookup environment and argv vector; no persistent files are changed.

Dependencies and integration points: Integrated with `execvp01_child.c` and the LTP test binary staging path.

Risks and test signals: Failure indicates PATH search or exec replacement regressions; the helper detects bad argv.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execvp/execvp01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execvp/execvp01_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/execvp/execvp01_child.c

Purpose: Helper executable for the `execvp` wrapper test. It is intentionally tiny so success means the parent really replaced the child image with this program.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `strcmp()`, `tst_brk()`, and `tst_res()` from the LTP harness.

Control flow: `main()` reinitializes LTP state after exec, validates `argc == 2` and `argv[1] == "canary"`, emits `TPASS`, and returns 0.

State and persistence behavior: No durable state is created; the process image and inherited environment/arguments are the state under test.

Dependencies and integration points: Consumed by the neighboring parent test through `$PATH` lookup or an absolute path discovered with `tst_get_path()`.

Risks and test signals: The helper is a sentinel: any argument/environment mismatch, missing harness reinit, or unexpected execution path produces `TFAIL`; parent-side exec failure is reported before this helper runs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/execvp/execvp01_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/exit/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It covers one legacy `test.h` exit-status test and one newer `tst_test` file-flush test.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit/exit01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/exit/exit01.c

Purpose: Legacy LTP test verifying that `exit()` status is reported correctly to a waiting parent.

Important APIs/types/functions: `test.h` harness globals `TCID`/`TST_TOTAL`, `tst_parse_opts`, `tst_fork`, `wait`, `tst_resm`, `TEST_LOOPING`, and `tst_exit`.

Control flow: Each loop forks one child that calls `exit(1)`. The parent waits, checks the returned pid, strips a core-dump bit from the low status byte, expects signal 0, and expects exit status 1.

State and persistence behavior: State is the child process exit status captured by `wait()`. No files or shared memory are used.

Dependencies and integration points: Uses old LTP signal/pause setup with `tst_sig(FORK, DEF_HANDLER, cleanup)`.

Risks and test signals: The test manually decodes wait status instead of `WIFEXITED`/`WEXITSTATUS`, so portability depends on historical status layout. Failures identify wrong pid, signal, or exit code.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit/exit01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit/exit02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/exit/exit02.c

Purpose: Checks that exiting without an explicit `close()` still makes written file data readable by the parent.

Important APIs/types/functions: `SAFE_CREAT`, `SAFE_WRITE(SAFE_WRITE_ALL)`, `exit(0)`, `SAFE_FORK`, `tst_reap_children`, `SAFE_OPEN`, `SAFE_READ`, `memcmp`, and `.needs_tmpdir`.

Control flow: The child creates `test_file`, writes the filename string, and exits without closing. The parent reaps the child, reads the file, checks length and bytes, then unlinks it.

State and persistence behavior: Persistent tmpdir file content is the test state. It validates kernel close-on-exit/writeback behavior for an open fd.

Dependencies and integration points: Uses the modern LTP harness and isolated tmpdir.

Risks and test signals: The length failure message compares against the read buffer size in text, but the actual condition uses `sizeof(FNAME)`. Any missing implicit close/flush shows as short or wrong data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit/exit02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit_group/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/exit_group/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It adds `exit_group01: CFLAGS+=-pthread` because the test creates pthread workers before invoking the raw syscall.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs. The important test signal is both successful linking with pthreads and runtime termination of all threads.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit_group/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit_group/exit_group01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/exit_group/exit_group01.c

Purpose: Checks that raw `exit_group()` terminates a child process and all its running threads with the requested status.

Important APIs/types/functions: `pthread_create` through `SAFE_PTHREAD_CREATE`, `tst_syscall(__NR_exit_group, 4)`, shared anonymous `mmap`, `tst_atomic_t`, `tst_gettid`, `sched_yield`, and `SAFE_WAITPID`.

Control flow: `setup()` allocates shared `worker_data` for at least two CPUs. The child starts one busy worker per CPU and calls `exit_group(4)`. The parent waits for exit status 4 and then snapshots counters to verify they no longer change.

State and persistence behavior: Shared mmap state records worker tids and counters across fork. After `exit_group`, counters should remain stable because all child threads are gone.

Dependencies and integration points: Requires pthread linking, fork support, and anonymous shared mapping; `.needs_checkpoints` is declared although no explicit checkpoint macro is used.

Risks and test signals: If any worker survives the group exit, counters continue changing and the test fails. A failed syscall or wrong wait status also fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/exit_group/exit_group01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. No local overrides are needed for the faccessat positive/negative cases.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/faccessat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/faccessat01.c

Purpose: Positive coverage for `faccessat()` path resolution with directory fd, absolute path, and `AT_FDCWD`.

Important APIs/types/functions: `faccessat`, `TST_EXP_PASS`, `tst_tmpdir_genpath`, `SAFE_MKDIR`, `SAFE_OPEN(... O_DIRECTORY)`, `AT_FDCWD`, and LTP managed string buffers.

Control flow: `setup()` creates `faccessatdir/faccessatfile`, opens the directory and file, and prepares absolute/relative path strings. Three table cases call `faccessat(..., R_OK, 0)` expecting success.

State and persistence behavior: State is a tmpdir directory, a readable file, and open fds. Access checks do not modify persistent data.

Dependencies and integration points: Uses modern table-driven LTP tests with automatic buffers and tmpdir isolation.

Risks and test signals: Failures identify regressions in dirfd-relative, absolute, or cwd-relative access checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/faccessat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/faccessat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/faccessat02.c

Purpose: Negative coverage for `faccessat()` with a non-directory dirfd and an invalid fd.

Important APIs/types/functions: `faccessat`, `TST_EXP_FAIL`, `ENOTDIR`, `EBADF`, `SAFE_MKDIR`, `SAFE_OPEN`, and a two-row testcase table.

Control flow: `setup()` creates the same directory/file layout as the positive test. One case passes the file fd with a relative name expecting `ENOTDIR`; the other passes `-1` expecting `EBADF`.

State and persistence behavior: The tmpdir file and fds are the only state. No access check should succeed.

Dependencies and integration points: Complements `faccessat01.c` and uses the same LTP tmpdir/fd cleanup pattern.

Risks and test signals: Kernel changes in dirfd validation would surface as wrong errno. The cases intentionally avoid absolute paths so dirfd validation is exercised.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/faccessat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. No local overrides are needed; syscall availability is handled by the LTP `lapi/faccessat.h` wrapper.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/faccessat201.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/faccessat201.c

Purpose: Positive coverage for the `faccessat2()` syscall, including `AT_EACCESS` and `AT_SYMLINK_NOFOLLOW`.

Important APIs/types/functions: `faccessat2` from `lapi/faccessat.h`, `SAFE_TOUCH`, `SAFE_SYMLINK`, `SAFE_OPEN(... O_DIRECTORY)`, `AT_FDCWD`, `AT_EACCESS`, `AT_SYMLINK_NOFOLLOW`, and `TST_EXP_PASS`.

Control flow: `setup()` creates a readable file and symlink. Seven table cases exercise dirfd-relative, absolute with bad fd, cwd-relative, effective-id mode, and symlink-no-follow access checks.

State and persistence behavior: Filesystem state is a tmpdir file with mode 0444 and a symlink. The syscall only observes permissions.

Dependencies and integration points: Depends on Linux 5.8+ syscall availability via the LTP lapi wrapper; unsupported syscall handling is centralized there.

Risks and test signals: Failures indicate wrong flag/path handling in `faccessat2`. Symlink behavior is a distinct signal from regular path resolution.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/faccessat201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/faccessat202.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/faccessat202.c

Purpose: Negative/error coverage for `faccessat2()` including bad address, invalid flags/mode, invalid fd, non-directory fd, and effective-id permission denial.

Important APIs/types/functions: `faccessat2`, `tst_get_bad_addr`, `SAFE_SETEUID`, `SAFE_GETPWNAM("nobody")`, `TST_EXP_FAIL`, `AT_EACCESS`, and root-required setup.

Control flow: `setup()` creates a 0444 file under a directory, opens the file, records a bad pointer and nobody user. Each row calls `faccessat2` with expected errno; the `EACCES` case temporarily switches euid to nobody and restores root.

State and persistence behavior: State includes tmpdir permissions, a regular-file dirfd, a bad userspace pointer, and effective uid transitions.

Dependencies and integration points: Requires root to change euid and create controlled permission scenarios.

Risks and test signals: Wrong errno or failure to restore euid would compromise later cases. The `AT_EACCESS` case specifically checks effective credential handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/faccessat202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It includes `../utils/newer_64.mk` and defines `%_64` CPPFLAGS so the fadvise suite can build large-file ABI variants.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs. Risk is ABI coverage: incorrect `_FILE_OFFSET_BITS=64` wiring would hide 64-bit offset regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise01.c

Purpose: Verifies `posix_fadvise()` returns 0 for every defined advice value.

Important APIs/types/functions: `posix_fadvise(fd, 0, 0, advice)`, advice constants `NORMAL`, `SEQUENTIAL`, `RANDOM`, `NOREUSE`, `WILLNEED`, `DONTNEED`, `SAFE_OPEN`, and `tst_strerrno`.

Control flow: `setup()` opens `/bin/cat` read-only. Each testcase calls `posix_fadvise` with one valid advice and expects return value 0 rather than `errno`.

State and persistence behavior: The open file descriptor is the only state; fadvise may update kernel caching hints but the test does not depend on persistent changes.

Dependencies and integration points: Uses LTP's syscall compatibility includes and table count over advice values.

Risks and test signals: Failures show invalid rejection of a permitted advice. The test assumes `/bin/cat` exists and is readable.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise02.c

Purpose: Verifies `posix_fadvise()` returns `EBADF` for a deliberately invalid file descriptor across all defined advice values.

Important APIs/types/functions: `WRONG_FD` constant 42, `close()` retry handling, `posix_fadvise`, `EBADF`, and `tst_strerrno`.

Control flow: `setup()` closes fd 42 if open, tolerating `EBADF` and retrying on `EINTR`. Each testcase calls `posix_fadvise(42, ...)` and expects returned error number `EBADF`.

State and persistence behavior: State is the absence of a valid fd 42 in the process fd table.

Dependencies and integration points: Complements the valid-fd fadvise tests and uses the modern LTP test table.

Risks and test signals: If some previous harness setup reopens fd 42 after setup, the signal could be corrupted, but the test closes it immediately before the cases.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise03.c

Purpose: Checks `posix_fadvise()` returns `EINVAL` for advice values outside the architecture-defined set.

Important APIs/types/functions: `ADVISE_LIMIT`, `is_defined_advise()`, `posix_fadvise`, `lapi/abisize.h`, and special 31-bit s390 handling for `DONTNEED`/`NOREUSE` values.

Control flow: `setup()` opens `/bin/cat`; test indexes from 0 to 31 skip values recognized as defined and call `posix_fadvise` on the rest, expecting `EINVAL`.

State and persistence behavior: Only the open fd is persistent test state. Architecture-specific defined values are encoded in the `defined_advise` array.

Dependencies and integration points: The file integrates syscall API behavior with ABI-specific constants.

Risks and test signals: Risk is architecture drift: if new advice values are added under 32, this test needs updating to avoid false failures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise04.c

Purpose: Verifies `posix_fadvise()` returns `ESPIPE` when used on a pipe descriptor.

Important APIs/types/functions: `SAFE_PIPE`, `SAFE_CLOSE`, `posix_fadvise(pipedes[0], ...)`, defined advice constants, and `ESPIPE`.

Control flow: `setup()` creates a pipe and closes the write end. Each testcase calls `posix_fadvise` on the read end with one advice and expects `ESPIPE`.

State and persistence behavior: The pipe read fd is the runtime state. No filesystem data is used.

Dependencies and integration points: Complements file and invalid-fd fadvise coverage by exercising non-seekable descriptors.

Risks and test signals: Failure means the syscall accepted or misreported advice on a pipe. Cleanup must not double-close invalid descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. No local overrides are needed; individual C tests choose legacy or modern LTP harness styles.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate01.c

Purpose: Legacy LTP basic `fallocate()` functionality test for default mode and `FALLOC_FL_KEEP_SIZE`.

Important APIs/types/functions: `fallocate`, `fstat`, `lseek`, `write`, legacy `test.h`/`tso_safe_macros`, `FALLOC_FL_KEEP_SIZE`, and `lapi/fallocate.h`.

Control flow: `setup()` creates two files, records block size, and writes 12 blocks. Each loop fallocates one block at EOF in default mode expecting file size growth, then with keep-size expecting original size, seeks within the allocated range, and writes one byte.

State and persistence behavior: State is file size, allocated blocks, current file offset, and file contents in a tmpdir.

Dependencies and integration points: Uses old LTP harness and filesystem support detection via `EOPNOTSUPP`/`ENOSYS`.

Risks and test signals: The random write offset is bounded by the allocated length. Failures can indicate unsupported fallocate, incorrect size semantics, broken seek positioning, or unwritable allocated space.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate02.c

Purpose: Legacy negative `fallocate()` test for `EBADF`, `EINVAL`, and large-offset `EFBIG` cases.

Important APIs/types/functions: `fallocate`, read-only and writable fds, `DEFAULT_TEST_MODE`, `TST_ABI64`/`_FILE_OFFSET_BITS`, `LLONG_MAX`, and old LTP result macros.

Control flow: `setup()` creates a read-only and read-write file and writes 12 blocks to the writable one. The table tries read-only fd, negative offset/len, zero length, too-negative offset, and optional huge offset/len cases, checking errno.

State and persistence behavior: Persistent state is the prepared tmpdir files and fd permissions. No successful allocation is expected.

Dependencies and integration points: Build-time ABI macros determine whether huge-file cases are included.

Risks and test signals: The test compares `TEST_ERRNO` directly, so a syscall returning success with stale errno would be suspicious. Unsupported filesystems become `TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate03.c

Purpose: Tests successful `fallocate()` on a sparse file at several offsets, both default and keep-size.

Important APIs/types/functions: `SAFE_OPEN`, `SAFE_FSTAT`, `SAFE_WRITE`, `SAFE_LSEEK`, `fallocate`, `FALLOC_FL_KEEP_SIZE`, and table-driven offsets in filesystem block units.

Control flow: `setup()` writes 12 blocks, seeks across a 12-block hole, writes 12 more blocks, and rewinds. Each row fallocates one block at an offset inside data, hole, or beyond-hole regions.

State and persistence behavior: State is a sparse temp file with data-hole-data layout. The test validates allocation succeeds in each region.

Dependencies and integration points: Runs in a tmpdir with modern LTP macros.

Risks and test signals: It does not verify resulting extents or contents, only syscall success. Unsupported sparse/allocation semantics would surface as failed `fallocate`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate04.c

Purpose: Filesystem-wide test of advanced `fallocate()` modes: punch hole, zero range, collapse range, and insert range.

Important APIs/types/functions: `fallocate`, `FALLOC_FL_PUNCH_HOLE`, `FALLOC_FL_ZERO_RANGE`, `FALLOC_FL_COLLAPSE_RANGE`, `FALLOC_FL_INSERT_RANGE`, `lseek(SEEK_HOLE)`, `fstat`, `fsync`, and buffer comparisons.

Control flow: The test allocates and writes a 3-block file, then sequential subtests punch the middle block, zero a range, collapse a block, and insert a block, checking allocated size and file data after each operation.

State and persistence behavior: State is mounted test filesystem data, allocated block count, file contents, and file size. Subtests are intentionally ordered because each mutates the same file.

Dependencies and integration points: Requires root, a mounted test device, all-filesystems coverage, and optional verbose hex dumps.

Risks and test signals: Mode support varies by filesystem and returns `TCONF` for `EOPNOTSUPP`. Because subtests mutate shared state, an early failure can affect later cases.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate05.c

Purpose: Tests that writes to preallocated space continue to work after the filesystem is filled, then verifies hole punching frees space.

Important APIs/types/functions: `fallocate`, `write`, `tst_fill_fs`, `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`, `lseek(SEEK_HOLE/SEEK_DATA)`, and filesystem-type checks for btrfs/bcachefs.

Control flow: The test preallocates 256 blocks, fills the filesystem, writes into preallocated space, keeps allocating one block at a time until `ENOSPC`, writes into any extra allocated space, punches a hole, writes again, and checks hole/data offsets.

State and persistence behavior: State is a deliberately full mounted filesystem and a large preallocated test file. Hole size expectations vary for extent-oriented filesystems.

Dependencies and integration points: Requires root, mounted device, all-filesystems mode, and a generous timeout.

Risks and test signals: Disk-full tests are inherently filesystem-sensitive. Expected signals are successful writes to reserved blocks, `ENOSPC` for new allocation, and correct hole reporting.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate06.c

Purpose: Regression test for misaligned allocation and hole punching, with copy-on-write and full-filesystem variants.

Important APIs/types/functions: `fallocate`, `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`, `ioctl(FS_IOC_GETFLAGS/SETFLAGS)`, `FS_NOCOW_FL`, `tst_fill_fs`, `write`, `read`, and buffer validation.

Control flow: `setup()` detects CoW flag support and fills known buffers. Four cases toggle no-CoW and filesystem filling, write initial data, perform misaligned allocation, write into it, punch a misaligned range, and verify only that range was zeroed.

State and persistence behavior: State includes mounted filesystem fullness, inode CoW flag, file block size, written data, and deallocated byte ranges.

Dependencies and integration points: Requires root, a mounted device, minimum device size, all-filesystems coverage, and tags for XFS/Btrfs regressions.

Risks and test signals: Expected `ENOSPC` is tolerated only for the full-FS CoW path. Other errors or incorrect zeroing indicate allocation or deallocation bugs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It adds `fanotify11: CFLAGS+=-pthread` for the FAN_REPORT_TID thread test.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs. The directory depends heavily on configured fanotify headers and root-capable filesystem mounts.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify.h

Purpose: Shared fanotify test helper header wrapping initialization, mark operations, feature probing, file-handle capture, and event-info parsing.

Important APIs/types/functions: `SAFE_FANOTIFY_INIT`, `SAFE_FANOTIFY_MARK`, `fanotify_get_fid`, `fanotify_save_fid`, `fanotify_flags_supported_on_fs`, `fanotify_get_supported_init_flags`, `get_event_info_*`, and many `REQUIRE_*` macros.

Control flow: Wrappers convert `ENOSYS`/unsupported flag combinations into `TCONF` and unexpected syscall errors into `TBROK`. FID helpers collect `statfs` fsid plus `name_to_handle_at` handles. Support probes open temporary fanotify groups and optionally try marks on a path.

State and persistence behavior: No global state is stored, but helper calls inspect kernel/filesystem support and may create short-lived fanotify fds and marks.

Dependencies and integration points: Included by all fanotify tests when `HAVE_SYS_FANOTIFY_H` is available; it integrates LTP safe macros with Linux fanotify and file-handle APIs.

Risks and test signals: Because the header centralizes support detection, incorrect errno classification can skip or break many tests. The known-flags mask must be updated when new fanotify init flags are added.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify01.c

Purpose: Checks basic fanotify file events for inode, mount, and filesystem marks, with and without `FAN_REPORT_FID`.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `FAN_ACCESS`, `FAN_MODIFY`, `FAN_CLOSE`, `FAN_OPEN`, ignored-mask flags, `FAN_REPORT_FID`, event metadata parsing, and fd/fid result validation.

Control flow: Each case marks a file, generates open/read/close/write sequences, reads events in batches to prevent unwanted merging, tests ignored masks and `FAN_MARK_IGNORED_SURV_MODIFY`, then verifies event order, masks, pid, and returned fd or `FAN_NOFD` for fid mode.

State and persistence behavior: State includes fanotify groups/marks, ignored masks, a mounted test file, and generated event queues.

Dependencies and integration points: Requires root, a mounted test filesystem, all-filesystems coverage, and runtime support checks for fid, mount, and filesystem marks.

Risks and test signals: Risks are event merging, filesystem support differences, and fid/multi-fs limitations. Failures report missing, unexpected, or malformed events.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify02.c

Purpose: Checks fanotify events on children of a watched directory and behavior after removing `FAN_EVENT_ON_CHILD`.

Important APIs/types/functions: `FAN_EVENT_ON_CHILD`, `FAN_ONDIR`, `FAN_ACCESS`, `FAN_MODIFY`, `FAN_CLOSE`, `FAN_OPEN`, `SAFE_FANOTIFY_INIT`, `SAFE_FANOTIFY_MARK`, and event queue parsing.

Control flow: The test marks the current tmpdir for child events, creates/writes/closes a file, opens/reads/closes it, then removes `FAN_EVENT_ON_CHILD` and verifies a file child no longer generates events while opening the directory itself still does.

State and persistence behavior: State consists of one fanotify group, a tmpdir file, and mark mask changes during the run.

Dependencies and integration points: Requires root and tmpdir isolation, but no mounted external filesystem.

Risks and test signals: The signal is exact event count/order. Event coalescing is controlled by reading the queue between phases.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify03.c

Purpose: Validates fanotify permission events and userspace allow/deny responses for inode, mount, filesystem, and parent-child marks.

Important APIs/types/functions: `FAN_OPEN_PERM`, `FAN_ACCESS_PERM`, `FAN_OPEN_EXEC_PERM`, `FAN_ALLOW`, `FAN_DENY`, `struct fanotify_response`, child process generation, and `FAN_CLASS_CONTENT`.

Control flow: Each testcase sets a content-class permission mark, forks a child to open/read/execute targets, reads permission events, verifies masks and pid, writes the configured allow/deny responses, and checks child termination behavior.

State and persistence behavior: State includes a fanotify permission group, response queue, watched file/helper executable, and child process blocked on permission decisions.

Dependencies and integration points: Requires root, mounted test filesystem, resource helper `fanotify_child`, and support checks for permission and exec events.

Risks and test signals: Deadlocks or missed responses are the main risk. The test also gates unsupported filesystem mark and `FAN_OPEN_EXEC_PERM` combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify04.c

Purpose: Checks special fanotify mark flags such as `FAN_MARK_ONLYDIR`, `FAN_MARK_DONT_FOLLOW`, and `FAN_MARK_FLUSH`.

Important APIs/types/functions: `fanotify_mark`, `FAN_MARK_ONLYDIR`, `FAN_MARK_DONT_FOLLOW`, `FAN_MARK_FLUSH`, `FAN_OPEN`, `FAN_NONBLOCK`, symlinks, directories, and nonblocking event reads.

Control flow: The test tries valid and invalid `ONLYDIR` marks, verifies no symlink-follow behavior with `DONT_FOLLOW`, adds multiple inode marks, flushes them, and confirms subsequent opens produce no events.

State and persistence behavior: State is a fanotify group, one regular file, one symlink, one directory, and marks that are added/removed/flushed.

Dependencies and integration points: Requires root and a tmpdir; it compiles only when fanotify headers are present.

Risks and test signals: Expected-failure mark calls are as important as event checks. Nonblocking reads distinguish no-event from blocking behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify05.c

Purpose: Checks that queue overflow produces `FAN_Q_OVERFLOW` for limited queues and not for unlimited queues.

Important APIs/types/functions: `FAN_UNLIMITED_QUEUE`, `FAN_REPORT_FD_ERROR`, `FAN_Q_OVERFLOW`, `/proc/sys/fs/fanotify/max_queued_events`, `SAFE_OPEN`, and nonblocking fanotify reads.

Control flow: The test determines the queue limit, marks a mount for `FAN_OPEN`, generates more open events than the queue can hold without reading, then drains events and counts regular open versus overflow records.

State and persistence behavior: State is a fanotify event queue under pressure plus many generated files on a mounted test filesystem.

Dependencies and integration points: Requires root, mounted filesystem, and support checks for `FAN_REPORT_FD_ERROR`.

Risks and test signals: Overflow tests are sensitive to kernel queue sizing and event generation count. The expected fd for overflow differs when `FAN_REPORT_FD_ERROR` is enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify06.c

Purpose: Regression test for merging ignore masks between inode and mount marks across fanotify priority classes, including overlayfs behavior.

Important APIs/types/functions: `FAN_CLASS_PRE_CONTENT`, `FAN_CLASS_CONTENT`, `FAN_CLASS_NOTIF`, `FAN_MARK_MOUNT`, `FAN_MARK_IGNORED_MASK`, `FAN_MARK_IGNORED_SURV_MODIFY`, `FAN_MODIFY`, and overlay mount helpers.

Control flow: For each scenario, it creates groups across priorities, marks a mount for modify events, adds ignored inode masks to selected groups, generates file modifications, reads event queues, and verifies which groups receive events.

State and persistence behavior: State includes multiple fanotify groups, priority ordering, ignored masks, mounted base/overlay files, and event queues.

Dependencies and integration points: Requires root, mount device support, optional overlayfs, and tags for fanotify/overlay regressions.

Risks and test signals: The risk is subtle event merging or duplicate overlay events. The test closes event fds after verification to avoid descriptor leaks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify07.c

Purpose: Checks permission-event cleanup when a fanotify instance is destroyed while children are waiting for responses.

Important APIs/types/functions: `FAN_ACCESS_PERM`, `FAN_CLASS_CONTENT`, `SAFE_FORK`, `SAFE_KILL`, `struct fanotify_response`, `SAFE_CLOSE(fd_notify)`, and raw child management.

Control flow: The test starts children that repeatedly access a watched file, responds to only some permission events, opens a new fanotify instance, closes the original instance with unanswered events, and then stops/reaps children.

State and persistence behavior: State is a permission-event wait queue with some unresolved events plus blocked child processes.

Dependencies and integration points: Requires root and tmpdir; tagged comments reference kernel crash/hang fixes.

Risks and test signals: The signal is survival without list corruption or hang. The test intentionally leaks responses for several events before instance destruction.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify08.c

Purpose: Sanity-checks that `FAN_CLOEXEC` maps to `FD_CLOEXEC` on a fanotify descriptor.

Important APIs/types/functions: `fanotify_init`, `FAN_CLOEXEC`, `SAFE_FCNTL(F_GETFD)`, `FD_CLOEXEC`, and two test rows.

Control flow: One row creates a group without `FAN_CLOEXEC` and expects the bit clear; the other creates one with `FAN_CLOEXEC` and expects the bit set.

State and persistence behavior: State is file descriptor close-on-exec metadata only.

Dependencies and integration points: Requires root and fanotify header support; no filesystem marks are created.

Risks and test signals: Failures are direct descriptor flag mismatches, pointing to init flag handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify09.c

Purpose: Regression matrix for events on children when parent, subdirectory, mountpoint, ignored-mask, and reported-name marks interact.

Important APIs/types/functions: `FAN_EVENT_ON_CHILD`, `FAN_ONDIR`, `FAN_CLOSE_NOWRITE`, `FAN_MODIFY`, `FAN_REPORT_DFID_NAME`, `FAN_MARK_IGNORE_SURV`, legacy ignored masks, and multiple fanotify groups.

Control flow: Each testcase creates several groups with first/non-first mark differences, generates close/modify events on files or subdirs, optionally uses reported names, and verifies masks, pids, names, and ignore mask behavior.

State and persistence behavior: State includes several fanotify groups, parent/subdir/mount marks, ignored masks, a mounted filesystem, and event buffers.

Dependencies and integration points: Requires root, a mount device, runtime support for reported-name and ignore-mark features, and regression tags for several kernel commits.

Risks and test signals: The key risk is event merging/masking logic. The test skips unsupported combinations to avoid false failures on older kernels.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify10.c

Purpose: Large regression matrix for ignore mask logic across inode, parent, mount, filesystem, evictable marks, exec events, bind mounts, priority classes, and legacy versus `FAN_MARK_IGNORE` variants.

Important APIs/types/functions: `FAN_MARK_IGNORED_SURV`, `FAN_MARK_IGNORE_SURV`, `FAN_MARK_EVICTABLE`, `FAN_OPEN`, `FAN_OPEN_EXEC`, `FAN_EVENT_ON_CHILD`, `FAN_ONDIR`, `/proc/*/fdinfo`, cache dropping, bind mounts, and child exec/open generation.

Control flow: Setup creates a directory tree, many optional files/dirs, helper executables, and a bind mount. Each case creates fanotify groups across classes/priorities, applies normal and ignore marks, generates an open or exec event in a child, verifies event counts/masks per group, then cycles mounts.

State and persistence behavior: State is extensive: mounted filesystem, bind mount, ignore marks that may be evicted, per-class event queues, cache pressure sysctl, and child pid identity.

Dependencies and integration points: Requires root, mounted filesystem, forked child helpers, save/restore of `vfs_cache_pressure`, and runtime feature gates for filesystem, evictable, ignore, reported-name, and exec events.

Risks and test signals: This is the highest-flake-risk fanotify file because it depends on cache eviction and many feature combinations. It deliberately skips undefined pre-5.9 ignored-child semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify11.c

Purpose: Verifies `FAN_REPORT_TID` reports the triggering thread id instead of the thread-group id.

Important APIs/types/functions: `pthread_create`, `gettid()` via `syscall(SYS_gettid)`, `FAN_REPORT_TID`, `FAN_ALL_EVENTS | FAN_EVENT_ON_CHILD`, `SAFE_FILE_PRINTF`, and `SAFE_PTHREAD_JOIN`.

Control flow: The test runs one case without and one with `FAN_REPORT_TID`, marks the tmpdir, spawns a thread that creates a file named with its tid, reads one event, and compares `event.pid` to either tgid or tid.

State and persistence behavior: State is a fanotify group and the thread-created file event. Global `tid` records the worker thread id for comparison.

Dependencies and integration points: Requires pthread build flags from the Makefile, root, tmpdir, and runtime support check for `FAN_REPORT_TID`.

Risks and test signals: The initial info log prints `event.pid` before the event is read, but pass/fail checks occur after reading. Failures indicate pid/tid reporting mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify12.c

Purpose: Validates `FAN_OPEN_EXEC` event masks and interactions with ignored masks.

Important APIs/types/functions: `FAN_OPEN`, `FAN_OPEN_EXEC`, `FAN_MARK_IGNORED_MASK`, child `SAFE_OPEN`, child `SAFE_EXECL`, event queue parsing, and resource helper `fanotify_child`.

Control flow: For each case, marks both a regular file and executable helper with the requested mask and optional ignored mask, forks a child that opens the file then execs the helper, reads events, and compares masks/pids to expected sequence.

State and persistence behavior: State is the fanotify group marks, ignored masks, regular file, executable helper, child pid, and event buffer.

Dependencies and integration points: Requires root, fork support, the helper resource file, and runtime support for `FAN_OPEN_EXEC`.

Risks and test signals: The expected combined mask for an exec open is subtle when both `FAN_OPEN` and `FAN_OPEN_EXEC` are requested. Unsupported exec events are skipped.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify13.c

Purpose: Verifies `FAN_REPORT_FID` events report correct file handles and fsids for open/close/delete-self events across base and overlay variants.

Important APIs/types/functions: `FAN_REPORT_FID`, `FAN_NONBLOCK`, `FAN_OPEN`, `FAN_CLOSE_NOWRITE`, `FAN_DELETE_SELF`, `FAN_ONDIR`, `name_to_handle_at`, overlay helpers, bind mounts, and fid comparison.

Control flow: Setup creates file/directory objects, optional overlay mounts, an extra non-fid mark, and records each object's fid. Each variant/case marks objects, generates opens/closes or deletes, reads events, and compares mask, `FAN_NOFD`, handle bytes/type/content, and fsid.

State and persistence behavior: State includes base or overlay mount topology, object identities, saved fids, and fanotify event queues. Delete-self cases recreate objects afterward.

Dependencies and integration points: Requires root, mounted filesystems, `name_to_handle_at`, support for `AT_HANDLE_FID` on overlay variants, and feature gating for filesystem marks.

Risks and test signals: Overlay combinations are version-sensitive and tagged for kernel fixes. Wrong fid/fsid or unexpected fd in fid mode fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify14.c

Purpose: Negative validation matrix for invalid `fanotify_init()`/`fanotify_mark()` flag and mask combinations, especially with `FAN_REPORT_FID`.

Important APIs/types/functions: `FAN_REPORT_FID`, `FAN_REPORT_NAME`, `FAN_REPORT_TARGET_FID`, dirent event masks, `FAN_MARK_ONLYDIR`, `FAN_MARK_IGNORE`, anonymous pipes, permission/pre-content event masks, SELinux enforcing detection, and `TST_EXP_FAIL_ARR`.

Control flow: Setup requires fid support, discovers supported init flags, creates a test file and pipes. Each table row either expects `fanotify_init` failure or creates a group and expects `fanotify_mark` to fail with the configured errno; `ENOTDIR` cases also verify the same masks are valid on a directory or filesystem mark.

State and persistence behavior: State is mostly validation inputs: mountpoint/file paths, anonymous pipe fds, SELinux mode, and temporary fanotify groups.

Dependencies and integration points: Requires root, mounted all-filesystems coverage, and fanotify support. Regression tags cover ENOTDIR validation and pipe mark rejection.

Risks and test signals: SELinux may produce `EACCES`, so expected errno arrays include it when enforcing. The large table must track evolving fanotify API rules.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify15.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify15.c

Purpose: Verifies `FAN_REPORT_FID` dirent events with create/delete/move/modify/delete-self merging for filesystem and parent-directory marks.

Important APIs/types/functions: `FAN_REPORT_FID`, `FAN_CREATE`, `FAN_DELETE`, `FAN_MOVE`, `FAN_MODIFY`, `FAN_DELETE_SELF`, `FAN_ONDIR`, `FAN_EVENT_ON_CHILD`, `fanotify_save_fid`, and event fid comparison.

Control flow: Each case marks `TEST_DIR`, saves fids for the root/file/subdir, creates/modifies/renames/unlinks a file, reads file events, then creates/renames/removes a directory and reads directory events. It verifies merged masks and fid/fsid/handle identity.

State and persistence behavior: State is the mounted test directory tree, file and directory fids, fanotify mark, and event buffer. Events are expected to merge by object.

Dependencies and integration points: Requires root, mounted all-filesystems coverage, `name_to_handle_at`, and fid support; filesystem marks are feature-gated.

Risks and test signals: The test is sensitive to event merge order and handle stability. It is tagged for the duplicate parent/child merge regression.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify15.c -->
