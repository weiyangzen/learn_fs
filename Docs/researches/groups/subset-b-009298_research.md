# subset-b-009298 research

Grouped research report for LTP syscall tests from futex through io_getevents. Each section preserves the exact source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait_bitset01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait_bitset01.c

Purpose: 1. Block on a bitset futex and wait for timeout, the difference between normal futex and bitset futex is that that the later have absolute timeout. 2. Check that the futex waited for expected time.

Important APIs/types/functions: includes `tst_test.h`, `tst_timer.h`, `futextest.h`; touches `futex`; defines `verify_futex_wait_bitset`, `run`, `setup`.

Control flow centers on `verify_futex_wait_bitset`, `run`, `setup`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt`, `.test_variants` into the LTP runner. Error-path assertions cover `ENOSYS`, `ETIMEDOUT`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `tst_test.h`, `tst_timer.h`, `futextest.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`. Expected errno values include `ENOSYS`, `ETIMEDOUT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait_bitset01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv01.c

Purpose: Negative and timeout coverage for futex_waitv: invalid flags, unaligned/null addresses, invalid waiter arrays, invalid clocks/counts, value mismatch, and ETIMEDOUT behavior.

Important APIs/types/functions: includes `time.h`, `stdlib.h`, `tst_test.h`, `lapi/futex.h`, `futex2test.h`, `tst_safe_clocks.h`; touches `futex`, `futex_waitv`; defines `setup`, `init_timeout`, `init_waitv`, `test_invalid_flags`, `test_unaligned_address`, `test_null_address`, `test_null_waiters`, `test_invalid_clockid`, `test_invalid_nr_futexes`, `test_mismatch_between_uaddr_and_val`, `test_timeout`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOCK_GETTIME`, `SAFE_MALLOC`.

Control flow centers on `setup`, `init_timeout`, `init_waitv`, `test_invalid_flags`, `test_unaligned_address`, `test_null_address`, `test_null_waiters`, `test_invalid_clockid`, `test_invalid_nr_futexes`, `test_mismatch_between_uaddr_and_val`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup` into the LTP runner. Error-path assertions cover `EAGAIN`, `EFAULT`, `EINVAL`, `ETIMEDOUT`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `time.h`, `stdlib.h`, `tst_test.h`, `lapi/futex.h`, `futex2test.h`, `tst_safe_clocks.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EAGAIN`, `EFAULT`, `EINVAL`, `ETIMEDOUT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv02.c

Purpose: Functional futex_waitv wake test for the maximum supported waiter array, verifying a wake on one futex releases a waitv caller.

Important APIs/types/functions: includes `unistd.h`, `time.h`, `tst_test.h`, `lapi/futex.h`, `lapi/syscalls.h`, `futex2test.h`, `futex_utils.h`, `tst_safe_pthread.h`; touches `futex`, `futex_waitv`; defines `setup`, `run`; uses LTP safe helpers such as `SAFE_CLOCK_GETTIME`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.test_variants` into the LTP runner.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `unistd.h`, `time.h`, `tst_test.h`, `lapi/futex.h`, `lapi/syscalls.h`, `futex2test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_RET`, `TST_RETRY_FUNC`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv03.c

Purpose: Shared-memory futex_waitv wake test, covering wait vectors whose futex words live in IPC shared memory rather than process-private storage.

Important APIs/types/functions: includes `unistd.h`, `time.h`, `sys/shm.h`, `tst_test.h`, `lapi/futex.h`, `lapi/syscalls.h`, `futex2test.h`, `futex_utils.h`; touches `futex`, `futex_waitv`; defines `setup`, `cleanup`, `run`; uses LTP safe helpers such as `SAFE_CLOCK_GETTIME`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_SHMAT`, `SAFE_SHMCTL`, `SAFE_SHMDT`, `SAFE_SHMGET`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.test_variants` into the LTP runner.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `unistd.h`, `time.h`, `sys/shm.h`, `tst_test.h`, `lapi/futex.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_RET`, `TST_RETRY_FUNC`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake01.c

Purpose: futex_wake() returns 0 (0 woken up processes) when no processes wait on the mutex. nr_wake = 0 is noop

Important APIs/types/functions: includes `limits.h`, `futextest.h`; touches `futex`; defines `run`, `setup`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt`, `.test_variants` into the LTP runner.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `limits.h`, `futextest.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake02.c

Purpose: Block several threads on a private mutex, then wake them up. We do the real test in a child because with the test -i parameter the loop that checks that all threads are sleeping may fail with ENOENT. That is because some of the threads from previous run may still be there. Which is because the userspace part of pthread_join() sleeps in a futex on a pthread tid which is woken up at the end of the exit_mm(tsk) which is before the process is removed from the parent thread_group list. So there is a small race window wh

Important APIs/types/functions: includes `sys/types.h`, `futextest.h`, `futex_utils.h`, `tst_safe_pthread.h`; touches `futex`, `pthread_join`; defines `threads_awake`, `clear_threads_awake`, `do_child`, `run`, `setup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`.

Control flow centers on `threads_awake`, `clear_threads_awake`, `do_child`, `run`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.test_variants`, `.forks_child` into the LTP runner. Error-path assertions cover `ENOENT`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `sys/types.h`, `futextest.h`, `futex_utils.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_RET`. Expected errno values include `ENOENT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake03.c

Purpose: Block several processes on a mutex, then wake them up.

Important APIs/types/functions: includes `sys/types.h`, `sys/wait.h`, `futextest.h`, `futex_utils.h`; touches `futex`; defines `do_child`, `do_wake`, `run`, `setup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_MMAP`.

Control flow centers on `do_child`, `do_wake`, `run`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.test_variants`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `sys/types.h`, `sys/wait.h`, `futextest.h`, `futex_utils.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_PROCESS_STATE_WAIT`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake04.c

Purpose: Regression coverage for unique futex keys on shared huge pages so unrelated futex words do not wake the wrong waiter.

Important APIs/types/functions: includes `stdio.h`, `fcntl.h`, `sys/time.h`, `string.h`, `futextest.h`, `futex_utils.h`, `lapi/mmap.h`, `tst_safe_stdio.h`; touches `futex`, `getpagesize`, `mmap`; defines `setup`, `wakeup_thread2`; uses LTP safe helpers such as `SAFE_MUNMAP`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`.

Control flow centers on `setup`, `wakeup_thread2`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.test_variants`, `.needs_root`, `.needs_tmpdir` into the LTP runner. Error-path assertions cover `ENOMEM`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `stdio.h`, `fcntl.h`, `sys/time.h`, `string.h`, `futextest.h`, `futex_utils.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`, `TFAIL`, `TPASS`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_NEEDS`. Expected errno values include `ENOMEM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futextest.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futextest.h

Purpose: Header-only futex test library that wraps raw futex syscalls and provides reusable wait, wake, bitset, PI, requeue, and kernel-support probes.

Important APIs/types/functions: includes `unistd.h`, `sys/syscall.h`, `sys/types.h`, `lapi/futex.h`, `tst_timer.h`; touches `futex`, `raw syscall path`; defines `futex_supported_by_kernel`, `futex_syscall`, `futex_wait`, `futex_wake`, `futex_wait_bitset`, `futex_wake_bitset`, `futex_lock_pi`, `futex_unlock_pi`, `futex_wake_op`, `futex_requeue`, `futex_cmp_requeue`, `futex_wait_requeue_pi`.

Control flow centers on `futex_supported_by_kernel`, `futex_syscall`, `futex_wait`, `futex_wake`, `futex_wait_bitset`, `futex_wake_bitset`, `futex_lock_pi`, `futex_unlock_pi`, `futex_wake_op`, `futex_requeue`. Error-path assertions cover `ECHCK`, `ENOSYS`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `unistd.h`, `sys/syscall.h`, `sys/types.h`, `lapi/futex.h`, `tst_timer.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`, `TST_ERR`, `TST_RET`, `TST_RETRY_FUNC`. Expected errno values include `ECHCK`, `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futextest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futimesat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futimesat/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `futimesat` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futimesat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futimesat/futimesat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futimesat/futimesat01.c

Purpose: published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program. If not, see <http://www.gnu.org/licenses/>. DESCRIPTION This test case will verify basic function of futimesat added by kernel 2.6.16 or up. Author Yi Yang <yyangcdl@cn.ibm.com>

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`, `string.h`, `signal.h`; touches `futimesat`, `gettimeofday`, `raw syscall path`; defines `setup`, `cleanup`, `myfutimesat`, `main`; uses LTP safe helpers such as `SAFE_ASPRINTF`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_OPEN`.

Control flow centers on `setup`, `cleanup`, `myfutimesat`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls. Error-path assertions cover `EBADF`, `ENOTDIR`.

State and persistence behavior: Runtime state is filesystem metadata: fixture files/directories, file descriptors, and atime/mtime values changed through futimesat.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TOTAL`. Expected errno values include `EBADF`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futimesat/futimesat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; LTPLIBS = numa; include $(top_srcdir)/include/mk/testcases.mk; LDLIBS  += $(NUMA_LIBS); LTPLDLIBS = -lltpnuma; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, plus directory-specific linker libraries. The generated binaries exercise the `get_mempolicy` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/get_mempolicy01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/get_mempolicy01.c

Purpose: Authors: Takahiro Yasui <takahiro.yasui.mp@hitachi.com> Yumiko Sugita <yumiko.sugita.yf@hitachi.com> Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Manas Kumar Nayak <maknayak@in.ibm.com> (original port to the legacy API) Verify that get_mempolicy() returns a proper return value and errno for various cases.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `numa.h`, `numaif.h`, `errno.h`, `tse_numa.h`; touches `get_mempolicy`, `mbind`, `set_mempolicy`, `getpagesize`; defines `test_set_mempolicy_default`, `test_set_mempolicy_none`, `test_mbind_none`, `test_mbind_default`, `test_mbind`, `setup`, `cleanup`, `do_test`; uses LTP safe helpers such as `SAFE_MMAP`, `SAFE_MUNMAP`.

Control flow centers on `test_set_mempolicy_default`, `test_set_mempolicy_none`, `test_mbind_none`, `test_mbind_default`, `test_mbind`, `setup`, `cleanup`, `do_test`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup` into the LTP runner.

State and persistence behavior: Runtime state is NUMA policy state attached to a process or mapping, plus an mmap area used for mbind/get_mempolicy checks.

Dependencies and integration points: Depends on libnuma/numaif headers, LTP NUMA capability checks, and helper wrappers for mmap/mbind/set_mempolicy. Direct include dependencies include `config.h`, `tst_test.h`, `numa.h`, `numaif.h`, `errno.h`, `tse_numa.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TFAIL`, `TST_EXP_PASS`, `TST_NUMA_MEM`, `TST_RET`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/get_mempolicy01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/get_mempolicy02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/get_mempolicy02.c

Purpose: Authors: Takahiro Yasui <takahiro.yasui.mp@hitachi.com> Yumiko Sugita <yumiko.sugita.yf@hitachi.com> Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Manas Kumar Nayak <maknayak@in.ibm.com> (original port to the legacy API) Verify that get_mempolicy() returns a proper return errno for failure cases.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `numa.h`, `numaif.h`, `errno.h`, `tse_numa.h`; touches `get_mempolicy`, `getpagesize`; defines `setup`, `cleanup`, `do_test`.

Control flow centers on `setup`, `cleanup`, `do_test`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is NUMA policy state attached to a process or mapping, plus an mmap area used for mbind/get_mempolicy checks.

Dependencies and integration points: Depends on libnuma/numaif headers, LTP NUMA capability checks, and helper wrappers for mmap/mbind/set_mempolicy. Direct include dependencies include `config.h`, `tst_test.h`, `numa.h`, `numaif.h`, `errno.h`, `tse_numa.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TST_EXP_FAIL`, `TST_NUMA_MEM`, `TST_TEST_TCONF`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/get_mempolicy02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_robust_list/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/get_robust_list/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `get_robust_list` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_robust_list/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_robust_list/get_robust_list01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/get_robust_list/get_robust_list01.c

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Name: get_robust_list01 Test Description: Verify that get_robust_list() returns the proper errno for various failure cases Usage: <for command-line> get_robust_list01 [-c n] [-e][-i n] [-I x] [-p x] [-t] where, -c n : Run n copies concurrently. -e : Turn on errno logging. -i n : Execute te

Important APIs/types/functions: includes `sys/types.h`, `sys/syscall.h`, `errno.h`, `stdint.h`, `stdio.h`, `stdlib.h`, `test.h`, `tso_safe_macros.h`; touches `get_robust_list`, `raw syscall path`; defines `setup`, `cleanup`, `main`; uses LTP safe helpers such as `SAFE_SETUID`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls. Error-path assertions cover `EFAULT`, `EPERM`, `ESRCH`.

State and persistence behavior: Runtime state is a task robust-futex-list pointer and length; permission and invalid-address paths are part of the kernel ABI surface.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/types.h`, `sys/syscall.h`, `errno.h`, `stdint.h`, `stdio.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TOTAL`. Expected errno values include `EFAULT`, `EPERM`, `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_robust_list/get_robust_list01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcontext/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcontext/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getcontext` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcontext/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcontext/getcontext01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcontext/getcontext01.c

Purpose:  Basic test for getcontext(). Calls a getcontext() then jumps back with a setcontext().

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `ucontext.h`; touches `getcontext`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the user-space ucontext_t snapshot returned by getcontext.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `config.h`, `tst_test.h`, `ucontext.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TST_EXP_PASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcontext/getcontext01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getcpu` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu01.c

Purpose:  The test process is affined to a CPU. It then calls getcpu and checks that the CPU and node (if supported) match the expected values.

Important APIs/types/functions: includes `dirent.h`, `errno.h`, `stdio.h`, `stdlib.h`, `sys/types.h`, `tst_test.h`, `lapi/cpuset.h`, `lapi/sched.h`; touches `getcpu`; defines `max_cpuid`, `set_cpu_affinity`, `get_nodeid`, `run`.

Control flow centers on `max_cpuid`, `set_cpu_affinity`, `get_nodeid`, `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `EINVAL`.

State and persistence behavior: Runtime state is the current CPU/node reported by the scheduler and optional userspace pointers that receive the values.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `dirent.h`, `errno.h`, `stdio.h`, `stdlib.h`, `sys/types.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`. Expected errno values include `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu02.c

Purpose:  Verify that getcpu(2) fails with EFAULT if cpu_id or node_id points outside the calling process address space.

Important APIs/types/functions: includes `tst_test.h`, `lapi/sched.h`; touches `getcpu`; defines `check_getcpu`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_WAITPID`.

Control flow centers on `check_getcpu`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.forks_child` into the LTP runner. Error-path assertions cover `EFAULT`.

State and persistence behavior: Runtime state is the current CPU/node reported by the scheduler and optional userspace pointers that receive the values.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/sched.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_EXP_FAIL`. Expected errno values include `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getcwd` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd01.c

Purpose: DESCRIPTION Testcase to test that getcwd(2) sets errno correctly. 1) getcwd(2) fails if buf points to a bad address. 2) getcwd(2) fails if the size is invalid. 3) getcwd(2) fails if the size is set to 0. 4) getcwd(2) fails if the size is set to 1. 5) getcwd(2) fails if buf points to NULL and the size is set to 1. Expected Result: 1) getcwd(2) should return NULL and set errno to EFAULT. 2) getcwd(2) should return NULL and set errno to EFAULT. 3) getcwd(2) should return NULL and set errno to ERANGE. 4) getcwd(2) shou

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `limits.h`, `tst_test.h`, `lapi/syscalls.h`; touches `getcwd`, `raw syscall path`; defines `verify_getcwd`.

Control flow centers on `verify_getcwd`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EFAULT`, `ERANGE`.

State and persistence behavior: Runtime state is the process current working directory and path dentries; several tests mutate directories, symlinks, or renamed paths while checking returned buffers and errors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `unistd.h`, `limits.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL2`. Expected errno values include `EFAULT`, `ERANGE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd02.c

Purpose:  Testcase to check the basic functionality of the getcwd(2) system call. 1. getcwd(2) works fine if buf and size are valid. 2. getcwd(2) works fine if buf points to NULL and size is set to 0. 3. getcwd(2) works fine if buf points to NULL and size is greater than strlen(path).

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/stat.h`, `tst_test.h`; touches `getcwd`; defines `dir_exists`, `verify_getcwd`, `setup`; uses LTP safe helpers such as `SAFE_CHDIR`.

Control flow centers on `dir_exists`, `verify_getcwd`, `setup`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test` into the LTP runner.

State and persistence behavior: Runtime state is the process current working directory and path dentries; several tests mutate directories, symlinks, or renamed paths while checking returned buffers and errors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `unistd.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/stat.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_ERR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd03.c

Purpose:  Testcase to check the basic functionality of the getcwd(2) system call on a symbolic link. [Algorithm] 1. create a directory, and create a symbolic link to it at the same directory level. 2. get the working directory of a directory, and its pathname. 3. get the working directory of a symbolic link, and its pathname, and its readlink info. 4. compare the working directories and link information.

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `string.h`, `stdlib.h`, `sys/stat.h`, `sys/types.h`, `stdlib.h`, `tst_test.h`; touches `getcwd`, `getpid`; defines `verify_getcwd`, `setup`; uses LTP safe helpers such as `SAFE_BASENAME`, `SAFE_CHDIR`, `SAFE_MKDIR`, `SAFE_READLINK`, `SAFE_SYMLINK`.

Control flow centers on `verify_getcwd`, `setup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process current working directory and path dentries; several tests mutate directories, symlinks, or renamed paths while checking returned buffers and errors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `stdio.h`, `string.h`, `stdlib.h`, `sys/stat.h`, `sys/types.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd04.c

Purpose: Note: this test has already been in xfstests generic/028 test case, I just port it to LTP. Kernel commit '232d2d60aa5469bb097f55728f65146bd49c1d25' introduced a race condition that causes getcwd(2) to return "/" instead of correct path. 232d2d6 dcache: Translating dentry into pathname without taking rename_lock And these two kernel commits fixed the bug: ede4cebce16f5643c61aedd6d88d9070a1d23a68 prepend_path() needs to reinitialize dentry/vfsmount/mnt on restarts f6500801522c61782d4990fa1ad96154cb397cd4 f650080 __de

Important APIs/types/functions: includes `stdio.h`, `errno.h`, `fcntl.h`, `sys/types.h`, `unistd.h`, `tst_test.h`; touches `getcwd`; defines `do_child`, `sigproc`, `verify_getcwd`, `setup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_GETCWD`, `SAFE_KILL`, `SAFE_RENAME`, `SAFE_SIGNAL`, `SAFE_TOUCH`, `SAFE_WAITPID`.

Control flow centers on `do_child`, `sigproc`, `verify_getcwd`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.needs_tmpdir`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is the process current working directory and path dentries; several tests mutate directories, symlinks, or renamed paths while checking returned buffers and errors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `errno.h`, `fcntl.h`, `sys/types.h`, `unistd.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getdents/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getdents` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents.h

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software See fs/compat.c struct compat_linux_dirent

Important APIs/types/functions: includes `stdint.h`, `config.h`, `lapi/syscalls.h`, `unistd.h`; touches `getdents`, `raw syscall path`; defines `linux_getdents`, `linux_getdents64`, `tst_getdents`, `getdents_info`.

Control flow centers on `linux_getdents`, `linux_getdents64`, `tst_getdents`, `getdents_info`.

State and persistence behavior: Runtime state is a directory file descriptor and the kernel getdents buffer containing linux_dirent records.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdint.h`, `config.h`, `lapi/syscalls.h`, `unistd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents01.c

Purpose: written by Wayne Boyer Basic getdents() test that checks if directory listing is correct and complete.

Important APIs/types/functions: includes `tst_test.h`, `getdents.h`, `stdlib.h`; touches `getdents`; defines `reset_flags`, `check_flags`, `set_flag`, `run`, `setup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_SYMLINK`.

Control flow centers on `reset_flags`, `check_flags`, `set_flag`, `run`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.test_variants`, `.needs_root`, `.mount_device` into the LTP runner. Error-path assertions cover `ENOSYS`.

State and persistence behavior: Runtime state is a directory file descriptor and the kernel getdents buffer containing linux_dirent records.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `getdents.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`. Expected errno values include `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents02.c

Purpose: written by Wayne Boyer Verify that: - getdents() fails with EBADF if file descriptor fd is invalid - getdents() fails with EINVAL if result buffer is too small - getdents() fails with ENOTDIR if file descriptor does not refer to a directory - getdents() fails with ENOENT if directory was unlinked() - getdents() fails with EFAULT if argument points outside the calling process's address space

Important APIs/types/functions: includes `errno.h`, `tst_test.h`, `getdents.h`; touches `getdents`; defines `setup`, `run`; uses LTP safe helpers such as `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_RMDIR`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.test`, `.setup`, `.tcnt`, `.test_variants`, `.needs_root`, `.mount_device` into the LTP runner. Error-path assertions cover `EBADF`, `EFAULT`, `EINVAL`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is a directory file descriptor and the kernel getdents buffer containing linux_dirent records.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `tst_test.h`, `getdents.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL2`. Expected errno values include `EBADF`, `EFAULT`, `EINVAL`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdomainname/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getdomainname/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getdomainname` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdomainname/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdomainname/getdomainname01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getdomainname/getdomainname01.c

Purpose: AUTHOR: Saji Kumar.V.R <saji.kumar@wipro.com> Basic test for getdomainname(2) This is a Phase I test for the getdomainname(2) system call. It is intended to provide a limited exposure of the system call.

Important APIs/types/functions: includes `linux/utsname.h`, `tst_test.h`; touches `getdomainname`; defines `verify_getdomainname`.

Control flow centers on `verify_getdomainname`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the kernel UTS domain name copied into a caller buffer.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `linux/utsname.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdomainname/getdomainname01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getegid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getegid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/compat_16.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getegid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getegid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getegid/getegid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getegid/getegid01.c

Purpose: William Roske, Dave Fenner This test checks if getegid() returns the effective group id.

Important APIs/types/functions: includes `tst_test.h`, `compat_tst_16.h`; touches `getegid`; defines `run`; uses LTP safe helpers such as `SAFE_FILE_LINES_SCANF`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process effective group ID as reported by the kernel and, in some tests, cross-checked through proc or passwd-derived credentials.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TPASS`, `TST_EXP_EQ_LI`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getegid/getegid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getegid/getegid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getegid/getegid02.c

Purpose: William Roske, Dave Fenner This test checks if getegid() returns the same effective group given by passwd entry via getpwuid().

Important APIs/types/functions: includes `pwd.h`, `tst_test.h`, `compat_tst_16.h`; touches `getegid`, `geteuid`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process effective group ID as reported by the kernel and, in some tests, cross-checked through proc or passwd-derived credentials.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `pwd.h`, `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TST_EXP_EQ_LI`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getegid/getegid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/geteuid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/geteuid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/compat_16.mk; CPPFLAGS		+= -I$(abs_srcdir)/../utils; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `geteuid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/geteuid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/geteuid/geteuid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/geteuid/geteuid01.c

Purpose: CO-PILOT: Dave Fenner Check the basic functionality of the geteuid() system call.

Important APIs/types/functions: includes `tst_test.h`, `compat_tst_16.h`; touches `geteuid`; defines `verify_geteuid`.

Control flow centers on `verify_geteuid`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process effective user ID as reported by the kernel and proc status.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_POSITIVE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/geteuid/geteuid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/geteuid/geteuid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/geteuid/geteuid02.c

Purpose: Ported by Wayne Boyer Check that geteuid() return value matches value from /proc/self/status.

Important APIs/types/functions: includes `tst_test.h`, `compat_tst_16.h`; touches `geteuid`; defines `verify_geteuid`; uses LTP safe helpers such as `SAFE_FILE_LINES_SCANF`.

Control flow centers on `verify_geteuid`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process effective user ID as reported by the kernel and proc status.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_EXPR`, `TST_EXP_POSITIVE`, `TST_PASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/geteuid/geteuid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getgid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/compat_16.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getgid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgid/getgid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getgid/getgid01.c

Purpose: AUTHOR : William Roske CO-PILOT : Dave Fenner Call getgid() and expects that the gid returned correctly.

Important APIs/types/functions: includes `pwd.h`, `tst_test.h`, `compat_tst_16.h`; touches `getgid`; defines `run`, `setup`; uses LTP safe helpers such as `SAFE_GETPWNAM`, `SAFE_SETGID`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.test_all`, `.setup` into the LTP runner.

State and persistence behavior: Runtime state is the process real group ID; setup may switch to a known test account/group before validation.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `pwd.h`, `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgid/getgid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgid/getgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getgid/getgid03.c

Purpose: Ported by Wayne Boyer Testcase to check the basic functionality of getgid(). [Algorithm] For functionality test the return value from getgid() is compared to passwd entry.

Important APIs/types/functions: includes `pwd.h`, `tst_test.h`, `compat_tst_16.h`; touches `getgid`, `getuid`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process real group ID; setup may switch to a known test account/group before validation.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `pwd.h`, `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgid/getgid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgroups/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getgroups/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; USE_LEGACY_COMPAT_16_H := 1; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/compat_16.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getgroups` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgroups/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgroups/getgroups01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getgroups/getgroups01.c

Purpose: published by the Free Software Foundation. WITHOUT ANY WARRANTY; without even the implied warranty of Further, this software is distributed without any warranty that it is free of the rightful claim of any third person regarding infringement or the like. Any license provided herein, whether implied or otherwise, applies only to this software file. Patent licenses, if any, provided herein do not apply to combinations of this program with other software, or any other product whatsoever. with this program; if not, wri

Important APIs/types/functions: includes `unistd.h`, `signal.h`, `string.h`, `errno.h`, `grp.h`, `sys/param.h`, `sys/types.h`, `test.h`; touches `getgid`, `getgroups`, `setgroups`; defines `setup`, `cleanup`, `main`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls. Error-path assertions cover `EINVAL`.

State and persistence behavior: Runtime state is the process supplementary group vector and its size/count ABI.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `unistd.h`, `signal.h`, `string.h`, `errno.h`, `grp.h`, `sys/param.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`, `TST_TOTAL`. Expected errno values include `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgroups/getgroups01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgroups/getgroups03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getgroups/getgroups03.c

Purpose: Ported by Wayne Boyer the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Description: Verify that, getgroups() system call gets the supplementary group IDs of the calling process. Expected Result: The call succeeds in getting all the supplementary group IDs of the calling process. The effective group ID may or may not be returned.

Important APIs/types/functions: includes `stdio.h`, `sys/types.h`, `unistd.h`, `errno.h`, `string.h`, `signal.h`, `grp.h`, `sys/stat.h`; touches `getegid`, `getgroups`, `setgroups`; defines `verify_groups`, `setup`, `cleanup`, `main`, `readgroups`.

Control flow centers on `verify_groups`, `setup`, `cleanup`, `main`, `readgroups`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is the process supplementary group vector and its size/count ABI.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `sys/types.h`, `unistd.h`, `errno.h`, `string.h`, `signal.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgroups/getgroups03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostbyname_r/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gethostbyname_r/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `gethostbyname_r` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostbyname_r/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostbyname_r/gethostbyname_r01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gethostbyname_r/gethostbyname_r01.c

Purpose:  Test for GHOST: glibc vulnerability (CVE-2015-0235). https://www.qualys.com/research/security-advisories/GHOST-CVE-2015-0235.txt

Important APIs/types/functions: includes `tst_test.h`; touches `gethostbyname_r`; defines `check_vulnerable`.

Control flow centers on `check_vulnerable`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `ERANGE`.

State and persistence behavior: Runtime state is libc resolver scratch buffers and result pointers; the test targets buffer sizing/error behavior rather than kernel state.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TST_EXP_EQ_LI`. Expected errno values include `ERANGE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostbyname_r/gethostbyname_r01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gethostid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `gethostid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostid/gethostid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gethostid/gethostid01.c

Purpose: AUTHOR: William Roske CO-PILOT: Dave Fenner 12/2002 Paul Larson: Add functional test to compare output from hostid command and gethostid(). 01/2003 Robbie Williamson: Add code to handle distros that add "0x" to beginning of `hostid` output. 01/2006 Marty Ridgeway: Correct 64 bit check so the second 64 bit check doesn't clobber the first 64 bit check. 07/2021 Xie Ziyao: Rewrite with newlib and use/test sethostid.

Important APIs/types/functions: includes `tst_test.h`, `config.h`; touches `gethostid`; defines `run`, `setup`, `cleanup`.

Control flow centers on `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.setup`, `.cleanup`, `.needs_root`, `.tcnt` into the LTP runner.

State and persistence behavior: Runtime state is the libc/kernel host identifier and the external hostid command result used as a comparison signal.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `config.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_EXP_PASS`, `TST_RET`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostid/gethostid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `gethostname` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/gethostname01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/gethostname01.c

Purpose:  Test is checking that gethostname() succeeds.

Important APIs/types/functions: includes `tst_test.h`, `stdlib.h`; touches `gethostname`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the kernel hostname copied into user buffers of different sizes.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/gethostname01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/gethostname02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/gethostname02.c

Purpose:  Verify that gethostname(2) fails with - ENAMETOOLONG when len is smaller than the actual size

Important APIs/types/functions: includes `tst_test.h`; touches `gethostname`; defines `verify_gethostname`; uses LTP safe helpers such as `SAFE_GETHOSTNAME`.

Control flow centers on `verify_gethostname`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `ENAMETOOLONG`.

State and persistence behavior: Runtime state is the kernel hostname copied into user buffers of different sizes.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `ENAMETOOLONG`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/gethostname02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getitimer` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/getitimer01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/getitimer01.c

Purpose: 03/2001 - Written by Wayne Boyer Check that a correct call to getitimer() succeeds.

Important APIs/types/functions: includes `tst_test.h`, `tst_safe_clocks.h`; touches `getitimer`, `gettimeofday`, `setitimer`; defines `set_setitimer_value`, `verify_getitimer`, `setup`; uses LTP safe helpers such as `SAFE_CLOCK_GETRES`.

Control flow centers on `set_setitimer_value`, `verify_getitimer`, `setup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.test` into the LTP runner.

State and persistence behavior: Runtime state is per-process interval timer configuration and the itimerval values returned by getitimer.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `tst_safe_clocks.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `TST_EXP_PASS_SILENT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/getitimer01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/getitimer02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/getitimer02.c

Purpose: 03/2001 - Written by Wayne Boyer Check that getitimer() call fails: 1. EFAULT with invalid itimerval pointer 2. EINVAL when called with an invalid first argument

Important APIs/types/functions: includes `stdlib.h`, `errno.h`, `sys/time.h`, `tst_test.h`, `lapi/syscalls.h`; touches `getitimer`, `raw syscall path`; defines `sys_getitimer`, `setup`, `verify_getitimer`, `cleanup`; uses LTP safe helpers such as `SAFE_MALLOC`.

Control flow centers on `sys_getitimer`, `setup`, `verify_getitimer`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is per-process interval timer configuration and the itimerval values returned by getitimer.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `errno.h`, `sys/time.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/getitimer02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpagesize/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpagesize/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getpagesize` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpagesize/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpagesize/getpagesize01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpagesize/getpagesize01.c

Purpose: Robbie Williamson <robbiew@us.ibm.com> Prashant P Yendigeri <prashant.yendigeri@wipro.com> Verify that getpagesize(2) returns the number of bytes in a memory page as expected.

Important APIs/types/functions: includes `tst_test.h`; touches `getpagesize`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the system page-size constant returned through libc/sysconf-compatible interfaces.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_VAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpagesize/getpagesize01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpeername/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpeername/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getpeername` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpeername/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpeername/getpeername01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpeername/getpeername01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that getpeername() returns the proper errno for various failure cases: - EBADF on invalid address. - ENOTSOCK on socket opened on /dev/null. - ENOTCONN on socket not connected. - EINVAL on negative addrlen. - EFAULT on invalid addr/addrlen pointers.

Important APIs/types/functions: includes `tst_test.h`; touches `getpeername`, `socket`; defines `setup_fd_file`, `setup_fd_stream`, `cleanup_fd`, `setup_pair`, `cleanup_pair`, `verify_getpeername`, `setup`; uses LTP safe helpers such as `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_SOCKET`, `SAFE_SOCKETPAIR`.

Control flow centers on `setup_fd_file`, `setup_fd_stream`, `cleanup_fd`, `setup_pair`, `cleanup_pair`, `verify_getpeername`, `setup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `EBADF`, `EFAULT`, `EINVAL`, `ENOTCONN`, `ENOTSOCK`.

State and persistence behavior: Runtime state is socket endpoint state, including unconnected sockets and invalid descriptors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EBADF`, `EFAULT`, `EINVAL`, `ENOTCONN`, `ENOTSOCK`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpeername/getpeername01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getpgid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/getpgid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/getpgid01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify the basic functionality of getpgid(2) syscall.

Important APIs/types/functions: includes `tst_test.h`; touches `getpgid`, `getpid`; defines `get_init_pgid`, `run`; uses LTP safe helpers such as `SAFE_FILE_SCANF`, `SAFE_FORK`.

Control flow centers on `get_init_pgid`, `run`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is process group membership for the current process, children, and invalid/unreferenced PIDs.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_EQ_LI`, `TST_EXP_PID`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/getpgid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/getpgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/getpgid02.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that getpgid(2) fails with errno ESRCH when pid does not match any process.

Important APIs/types/functions: includes `tst_test.h`; touches `getpgid`; defines `setup`, `run`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.setup`, `.test_all` into the LTP runner. Error-path assertions cover `ESRCH`.

State and persistence behavior: Runtime state is process group membership for the current process, children, and invalid/unreferenced PIDs.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL2`. Expected errno values include `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/getpgid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgrp/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpgrp/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getpgrp` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgrp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgrp/getpgrp01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpgrp/getpgrp01.c

Purpose: AUTHOR: William Roske, CO-PILOT: Dave Fenner Verify that getpgrp(2) syscall executes successfully.

Important APIs/types/functions: includes `tst_test.h`; touches `getpgrp`; defines `run`; uses LTP safe helpers such as `SAFE_GETPGID`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the caller's process group ID and its relationship to getpgid(0).

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_EQ_LI`, `TST_EXP_PID`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgrp/getpgrp01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getpid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid01.c

Purpose:  Verify that :manpage:`getpid(2)` system call returns process ID in range <2, PID_MAX>.

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`; touches `getpid`; defines `setup`, `verify_getpid`; uses LTP safe helpers such as `SAFE_FILE_SCANF`, `SAFE_FORK`, `SAFE_WAIT`.

Control flow centers on `setup`, `verify_getpid`. The `struct tst_test` registration wires `.setup`, `.forks_child`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is process identity across parent/child relationships and kernel PID range limits.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid02.c

Purpose:  Check that: - :manpage:`fork(2)` in parent returns the same pid as :manpage:`getpid(2)` in child - :manpage:`getppid(2)` in child returns the same pid as :manpage:`getpid(2)` in parent

Important APIs/types/functions: includes `tst_test.h`; touches `getpid`, `getppid`, `fork`; defines `verify_getpid`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_MMAP`, `SAFE_MUNMAP`.

Control flow centers on `verify_getpid`, `setup`, `cleanup`. The `struct tst_test` registration wires `.forks_child`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is process identity across parent/child relationships and kernel PID range limits.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getppid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getppid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getppid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getppid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getppid/getppid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getppid/getppid01.c

Purpose:  Test whether parent process id that getppid() returns is out of range.

Important APIs/types/functions: includes `errno.h`, `tst_test.h`; touches `getppid`; defines `setup`, `verify_getppid`; uses LTP safe helpers such as `SAFE_FILE_SCANF`.

Control flow centers on `setup`, `verify_getppid`. The `struct tst_test` registration wires `.setup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is parent/child process identity and the kernel PID range limits.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getppid/getppid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getppid/getppid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getppid/getppid02.c

Purpose:  Check that getppid() in child returns the same pid as getpid() in parent.

Important APIs/types/functions: includes `errno.h`, `tst_test.h`; touches `getpid`, `getppid`; defines `verify_getppid`; uses LTP safe helpers such as `SAFE_FORK`.

Control flow centers on `verify_getppid`. The `struct tst_test` registration wires `.forks_child`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is parent/child process identity and the kernel PID range limits.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getppid/getppid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getpriority` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/getpriority01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/getpriority01.c

Purpose: Ported to LTP: Wayne Boyer 11/2016 Modified by Guangwen Feng <fenggw-fnst@cn.fujitsu.com> Verify that getpriority(2) succeeds get the scheduling priority of the current process, process group or user, and the priority values are in the ranges of [0, 0], [0, 0] and [-20, 0] by default for the flags PRIO_PROCESS, PRIO_PGRP and PRIO_USER respectively.

Important APIs/types/functions: includes `errno.h`, `sys/resource.h`, `sys/time.h`, `tst_test.h`; touches `getpriority`; defines `verify_getpriority`.

Control flow centers on `verify_getpriority`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner.

State and persistence behavior: Runtime state is scheduler nice/priority lookup for process, group, and user selectors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `sys/resource.h`, `sys/time.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/getpriority01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/getpriority02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/getpriority02.c

Purpose: Ported to LTP: Wayne Boyer 11/2016 Modified by Guangwen Feng <fenggw-fnst@cn.fujitsu.com> Verify that, 1) getpriority(2) fails with -1 and sets errno to EINVAL if 'which' argument was not one of PRIO_PROCESS, PRIO_PGRP, or PRIO_USER. 2) getpriority(2) fails with -1 and sets errno to ESRCH if no process was located for 'which' and 'who' arguments.

Important APIs/types/functions: includes `errno.h`, `sys/resource.h`, `sys/time.h`, `tst_test.h`; touches `getpriority`; defines `verify_getpriority`.

Control flow centers on `verify_getpriority`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EINVAL`, `ESRCH`.

State and persistence behavior: Runtime state is scheduler nice/priority lookup for process, group, and user selectors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `sys/resource.h`, `sys/time.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`. Expected errno values include `EINVAL`, `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/getpriority02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getrandom` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom01.c

Purpose: Calls getrandom(2) with a NULL buffer and expects failure.

Important APIs/types/functions: includes `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`; touches `getrandom`, `raw syscall path`; defines `verify_getrandom`.

Control flow centers on `verify_getrandom`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom02.c

Purpose: Calls getrandom(2), checks that the buffer is filled with random bytes and expects success.

Important APIs/types/functions: includes `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`; touches `getrandom`, `raw syscall path`; defines `check_content`, `verify_getrandom`; uses LTP safe helpers such as `SAFE_FILE_SCANF`.

Control flow centers on `check_content`, `verify_getrandom`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EAGAIN`.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`. Expected errno values include `EAGAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom03.c

Purpose: Calls getrandom(2), check that the return value is equal to the number of bytes required and expects success.

Important APIs/types/functions: includes `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`; touches `getrandom`, `raw syscall path`; defines `verify_getrandom`.

Control flow centers on `verify_getrandom`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom04.c

Purpose: Calls getrandom(2) after having limited the number of available file descriptors to 3 and expects success.

Important APIs/types/functions: includes `sys/resource.h`, `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`; touches `getrandom`, `raw syscall path`; defines `verify_getrandom`; uses LTP safe helpers such as `SAFE_GETRLIMIT`, `SAFE_SETRLIMIT`.

Control flow centers on `verify_getrandom`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/resource.h`, `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom05.c

Purpose:  Verify that getrandom(2) fails with - EFAULT when buf address is outside the accessible address space - EINVAL when flag is invalid

Important APIs/types/functions: includes `tst_test.h`, `lapi/getrandom.h`, `getrandom_var.h`; touches `getrandom`; defines `setup`, `verify_getrandom`.

Control flow centers on `setup`, `verify_getrandom`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.test_variants`, `.setup` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/getrandom.h`, `getrandom_var.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TST_EXP_FAIL2`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom_var.h

Purpose: Variant helper for testing both the raw getrandom syscall and libc getrandom when available.

Important APIs/types/functions: includes `lapi/syscalls.h`; touches `getrandom`, `raw syscall path`; defines `do_getrandom`, `getrandom_info`.

Control flow centers on `do_getrandom`, `getrandom_info`.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals come from consumers of this helper and from compile-time availability checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom_var.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; USE_LEGACY_COMPAT_16_H := 1; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/compat_16.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getresgid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid01.c

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Name: getresgid01 Test Description: Verify that getresgid() will be successful to get the real, effective and saved user id of the calling process. Expected Result: getresgid() should return with 0 value and the real/effective/saved user ids should be equal to that of calling process. Algo

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`, `signal.h`, `test.h`; touches `getegid`, `getgid`, `getresgid`; defines `setup`, `cleanup`, `main`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is the real, effective, and saved set-group-ID tuple; legacy tests may temporarily change IDs as root.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid02.c

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Name: getresgid02 Test Description: Verify that getresgid() will be successful to get the real, effective and saved user ids after calling process invokes setregid() to change the effective/saved gids to that of specified user. Expected Result: getresgid() should return with 0 value and th

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`, `signal.h`, `pwd.h`; touches `getgid`, `getresgid`; defines `setup`, `cleanup`, `main`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is the real, effective, and saved set-group-ID tuple; legacy tests may temporarily change IDs as root.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid03.c

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Name: getresgid03 Test Description: Verify that getresgid() will be successful to get the real, effective and saved user ids after calling process invokes setresgid() to change the effective gid to that of specified user. Expected Result: getresgid() should return with 0 value and the effe

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`, `signal.h`, `pwd.h`; touches `getegid`, `getgid`, `getresgid`; defines `setup`, `cleanup`, `main`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is the real, effective, and saved set-group-ID tuple; legacy tests may temporarily change IDs as root.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; USE_LEGACY_COMPAT_16_H := 1; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/compat_16.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getresuid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/getresuid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/getresuid01.c

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Name: getresuid01 Test Description: Verify that getresuid() will be successful to get the real, effective and saved user id of the calling process. Expected Result: getresuid() should return with 0 value and the real/effective/saved user ids should be equal to that of calling process. Algo

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`, `signal.h`, `test.h`; touches `geteuid`, `getresuid`, `getuid`; defines `setup`, `cleanup`, `main`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is the real, effective, and saved set-user-ID tuple; legacy tests may temporarily change IDs as root.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/getresuid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/getresuid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/getresuid02.c

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Name: getresuid02 Test Description: Verify that getresuid() will be successful to get the real, effective and saved user ids after calling process invokes setreuid() to change the effective/saved uids to that of specified user. $ Expected Result: getresuid() should return with 0 value and

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`, `signal.h`, `pwd.h`; touches `getresuid`, `getuid`; defines `setup`, `cleanup`, `main`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is the real, effective, and saved set-user-ID tuple; legacy tests may temporarily change IDs as root.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/getresuid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/getresuid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/getresuid03.c

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Name: getresuid03 Test Description: Verify that getresuid() will be successful to get the real, effective and saved user ids after calling process invokes setresuid() to change the effective uid to that of specified user. $ Expected Result: getresuid() should return with 0 value and the ef

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`, `signal.h`, `pwd.h`; touches `geteuid`, `getresuid`, `getuid`; defines `setup`, `cleanup`, `main`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is the real, effective, and saved set-user-ID tuple; legacy tests may temporarily change IDs as root.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresuid/getresuid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; getrlimit03: CFLAGS += -D_LARGEFILE64_SOURCE; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, with local compiler flags. The generated binaries exercise the `getrlimit` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit01.c

Purpose:  Verify that getrlimit(2) call will be successful for all possible resource types.

Important APIs/types/functions: includes `sys/resource.h`, `tst_test.h`; touches `getrlimit`; defines `verify_getrlimit`.

Control flow centers on `verify_getrlimit`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner.

State and persistence behavior: Runtime state is per-process resource limit structures and architecture-specific syscall ABI representations.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/resource.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit02.c

Purpose: AUTHOR: Suresh Babu V. <suresh.babu@wipro.com> Verify that, getrlimit(2) returns -1 and sets errno to - EFAULT if an invalid address is given for address parameter. - EINVAL if an invalid resource type (RLIM_NLIMITS is a out of range resource type) is passed.

Important APIs/types/functions: includes `sys/resource.h`, `tst_test.h`; touches `getrlimit`; defines `verify_getrlimit`.

Control flow centers on `verify_getrlimit`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is per-process resource limit structures and architecture-specific syscall ABI representations.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/resource.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit03.c

Purpose: Architectures may provide up to three syscalls that have been used to implement getrlimit(2) in different libc implementations. These syscalls differ in the size and signedness of rlim_t: - __NR_getrlimit uses long or unsigned long, depending on the architecture - __NR_ugetrlimit uses unsigned long, and only exists on architectures where __NR_getrlimit is signed - __NR_prlimit64 uses uint64_t This test compares the results returned by all three syscalls, confirming that they either match or were appropriately cappe

Important APIs/types/functions: includes `inttypes.h`, `stdint.h`, `sys/time.h`, `sys/resource.h`, `tst_test.h`, `lapi/syscalls.h`, `lapi/abisize.h`; touches `getrlimit`, `raw syscall path`; defines `getrlimit_u64`, `getrlimit_ulong`, `getrlimit_long`, `compare_retval`, `compare_u64_ulong`, `compare_u64_long`, `run`.

Control flow centers on `getrlimit_u64`, `getrlimit_ulong`, `getrlimit_long`, `compare_retval`, `compare_u64_ulong`, `compare_u64_long`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EABI`, `ENOSYS`.

State and persistence behavior: Runtime state is per-process resource limit structures and architecture-specific syscall ABI representations.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `inttypes.h`, `stdint.h`, `sys/time.h`, `sys/resource.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`, `TST_ABI32`. Expected errno values include `EABI`, `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; LDLIBS += -lrt; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, plus directory-specific linker libraries. The generated binaries exercise the `getrusage` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage01.c

Purpose: AUTHOR: Saji Kumar.V.R <saji.kumar@wipro.com> Test that getrusage() with RUSAGE_SELF and RUSAGE_CHILDREN succeeds.

Important APIs/types/functions: includes `tst_test.h`; touches `getrusage`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage02.c

Purpose: AUTHOR : Saji Kumar.V.R <saji.kumar@wipro.com> Verify that getrusage() fails with: - EINVAL with invalid who - EFAULT with invalid usage pointer

Important APIs/types/functions: includes `errno.h`, `sched.h`, `sys/resource.h`, `tst_test.h`, `lapi/syscalls.h`; touches `getrusage`, `raw syscall path`; defines `libc_getrusage`, `sys_getrusage`, `verify_getrusage`, `setup`.

Control flow centers on `libc_getrusage`, `sys_getrusage`, `verify_getrusage`, `setup`. The `struct tst_test` registration wires `.test`, `.setup`, `.tcnt`, `.test_variants` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `errno.h`, `sched.h`, `sys/resource.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TCONF`, `TST_EXP_FAIL`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.c

Purpose:  Test ru_maxrss behaviors in struct rusage. This test program is backported from upstream commit: 1f10206cf8e9, which fills ru_maxrss value in struct rusage according to rss hiwater mark. To make sure this feature works correctly, a series of tests are executed in this program.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `tst_test.h`, `getrusage03.h`; defines `inherit_fork1`, `inherit_fork2`, `grandchild_maxrss`, `zombie`, `sig_ign`, `inherit_exec`, `run`; uses LTP safe helpers such as `SAFE_EXECLP`, `SAFE_FORK`, `SAFE_GETRUSAGE`, `SAFE_SIGNAL`, `SAFE_WAIT`.

Control flow centers on `inherit_fork1`, `inherit_fork2`, `grandchild_maxrss`, `zombie`, `sig_ign`, `inherit_exec`, `run`. The `struct tst_test` registration wires `.forks_child`, `.test`, `.tcnt`, `.caps` into the LTP runner.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `stdlib.h`, `stdio.h`, `tst_test.h`, `getrusage03.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_CAP`, `TST_CAP_REQ`, `TST_PROCESS_EXIT_WAIT`, `TST_PROCESS_STATE_WAIT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.h

Purpose: Shared helper header for getrusage03 that forces context switches, allocates/touches memory, reads swap accounting, and checks deltas.

Important APIs/types/functions: includes `sched.h`, `tst_test.h`; defines `force_context_switches`, `consume_mb`, `is_in_delta`; uses LTP safe helpers such as `SAFE_FILE_LINES_SCANF`, `SAFE_MALLOC`.

Control flow centers on `force_context_switches`, `consume_mb`, `is_in_delta`.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `sched.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03_child.c

Purpose: Companion executable for getrusage03 that consumes memory, forks grandchildren, and reports ru_maxrss behavior after exec/fork combinations.

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`, `getrusage03.h`; touches `fork`; defines `main`; uses LTP safe helpers such as `SAFE_GETRUSAGE`, `SAFE_STRTOL`.

Control flow centers on `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `stdlib.h`, `tst_test.h`, `getrusage03.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_NO_DEFAULT_MAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage04.c

Purpose: getrusage04 - accuracy of getrusage() with RUSAGE_THREAD This program is used for testing the following upstream commit: 761b1d26df542fd5eb348837351e4d2f3bc7bffe. getrusage() returns cpu resource usage with accuracy of 10ms when RUSAGE_THREAD is specified to the argument who. Meanwhile, accuracy is 1ms when RUSAGE_SELF is specified. This bad accuracy of getrusage() caused a big impact on some application which is critical to accuracy of cpu usage. The upstream fix removed casts to clock_t in task_u/stime(), to keep

Important APIs/types/functions: includes `sys/types.h`, `sys/resource.h`, `sys/time.h`, `errno.h`, `stdio.h`, `stdlib.h`, `time.h`, `test.h`; touches `getrusage`; defines `fusage`, `busyloop`, `setup`, `cleanup`, `main`; uses LTP safe helpers such as `SAFE_GETRUSAGE`, `SAFE_STRTOL`.

Control flow centers on `fusage`, `busyloop`, `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `sys/types.h`, `sys/resource.h`, `sys/time.h`, `errno.h`, `stdio.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getsid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsid/getsid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsid/getsid01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that session IDs returned by getsid() (with argument pid=0) are same in parent and child process.

Important APIs/types/functions: includes `tst_test.h`; touches `getsid`; defines `run`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_WAITPID`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is session membership for the current process, children, or nonexistent PIDs.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TST_EXP_EQ_LI`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsid/getsid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsid/getsid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsid/getsid02.c

Purpose:  Verify that getsid(2) fails with ESRCH errno when there is no process found with process ID pid.

Important APIs/types/functions: includes `tst_test.h`; touches `getsid`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `ESRCH`.

State and persistence behavior: Runtime state is session membership for the current process, children, or nonexistent PIDs.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsid/getsid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockname/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsockname/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getsockname` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockname/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockname/getsockname01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsockname/getsockname01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that getsockname() returns the proper errno for various failure cases: - EBADF on a not open file - ENOTSOCK on a file descriptor not linked to a socket - EFAULT on invalid socket buffer o invalid socklen - EINVALI on an invalid addrlen

Important APIs/types/functions: includes `tst_test.h`; touches `getsockname`, `socket`; defines `check_getsockname`, `setup`; uses LTP safe helpers such as `SAFE_BIND`, `SAFE_OPEN`, `SAFE_SOCKET`.

Control flow centers on `check_getsockname`, `setup`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `EBADF`, `EFAULT`, `EINVAL`, `EINVALI`, `ENOTSOCK`.

State and persistence behavior: Runtime state is local socket address binding and invalid descriptor/address-length combinations.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EBADF`, `EFAULT`, `EINVAL`, `EINVALI`, `ENOTSOCK`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockname/getsockname01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getsockopt` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that getsockopt() returns the proper errno for various failure cases: - EBADF on a not open file - ENOTSOCK on a file descriptor not linked to a socket - EFAULT on invalid address of value or length - EOPNOTSUPP on invalid option name or protocol - EINVAL on an invalid optlen

Important APIs/types/functions: includes `tst_test.h`; touches `getsockopt`, `socket`; defines `check_getsockopt`, `setup`; uses LTP safe helpers such as `SAFE_BIND`, `SAFE_OPEN`, `SAFE_SOCKET`.

Control flow centers on `check_getsockopt`, `setup`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `EBADF`, `EFAULT`, `EINVAL`, `ENOPROTOOPT`, `ENOTSOCK`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is socket option storage, peer credentials, and connected UNIX/TCP socket endpoints.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EBADF`, `EFAULT`, `EINVAL`, `ENOPROTOOPT`, `ENOTSOCK`, `EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt02.c

Purpose:  Test getsockopt(2) for retrieving peer credentials (SO_PEERCRED).

Important APIs/types/functions: includes `errno.h`, `stdlib.h`, `tst_test.h`; touches `getpid`, `getsockopt`, `socket`, `accept`; defines `setup`, `fork_func`, `test_function`, `cleanup`; uses LTP safe helpers such as `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_FORK`, `SAFE_LISTEN`, `SAFE_SOCKET`.

Control flow centers on `setup`, `fork_func`, `test_function`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is socket option storage, peer credentials, and connected UNIX/TCP socket endpoints.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gettid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; FILTER_OUT_MAKE_TARGETS	+= gettid01 gettid02; gettid02: LDLIBS += -lpthread; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, plus directory-specific linker libraries. The generated binaries exercise the `gettid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettid/gettid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gettid/gettid01.c

Purpose:  This test checks if parent pid is equal to tid in single-threaded application.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`; touches `raw syscall path`; defines `run`; uses LTP safe helpers such as `SAFE_FILE_LINES_SCANF`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is Linux task identity, contrasting process IDs with thread IDs in single- and multi-threaded cases.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TST_EXP_EQ_LI`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettid/gettid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettid/gettid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gettid/gettid02.c

Purpose:  This test spawns multiple threads, then check for each one of them if the parent ID is different AND if the thread ID is different from all the other spwaned threads.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`, `tst_safe_pthread.h`; touches `raw syscall path`; defines `run`; uses LTP safe helpers such as `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is Linux task identity, contrasting process IDs with thread IDs in single- and multi-threaded cases.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_EXP_EXPR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettid/gettid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `gettimeofday` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/gettimeofday01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/gettimeofday01.c

Purpose:  Test for gettimeofday error. - EFAULT: tv pointed outside the accessible address space - EFAULT: tz pointed outside the accessible address space - EFAULT: both tv and tz pointed outside the accessible address space

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`; touches `gettimeofday`, `raw syscall path`; defines `verify_gettimeofday`.

Control flow centers on `verify_gettimeofday`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EFAULT`.

State and persistence behavior: Runtime state is wall-clock time copied from the kernel/vDSO path into timeval buffers.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/gettimeofday01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/gettimeofday02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/gettimeofday02.c

Purpose:  Check if gettimeofday() is monotonous during 10s: - Call gettimeofday() to get a t1 (fist value) - Call it again to get t2, see if t2 < t1, set t2 = t1, repeat for 10 sec

Important APIs/types/functions: includes `stdint.h`, `sys/time.h`, `stdlib.h`, `unistd.h`, `time.h`, `errno.h`, `tst_test.h`, `tst_timer.h`; touches `gettimeofday`, `raw syscall path`; defines `breakout`, `verify_gettimeofday`, `setup`; uses LTP safe helpers such as `SAFE_SIGNAL`.

Control flow centers on `breakout`, `verify_gettimeofday`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is wall-clock time copied from the kernel/vDSO path into timeval buffers.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdint.h`, `sys/time.h`, `stdlib.h`, `unistd.h`, `time.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/gettimeofday02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getuid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getuid/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/compat_16.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `getuid` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getuid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getuid/getuid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getuid/getuid01.c

Purpose: AUTHOR : William Roske CO-PILOT : Dave Fenner Check the basic functionality of the getuid() system call.

Important APIs/types/functions: includes `tst_test.h`, `compat_tst_16.h`; touches `getuid`; defines `verify_getuid`.

Control flow centers on `verify_getuid`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process real UID and /proc/self/status cross-checks.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_POSITIVE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getuid/getuid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getuid/getuid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getuid/getuid03.c

Purpose: Ported by Wayne Boyer Check that getuid() return value matches value from /proc/self/status.

Important APIs/types/functions: includes `tst_test.h`, `compat_tst_16.h`; touches `getuid`; defines `verify_getuid`; uses LTP safe helpers such as `SAFE_FILE_LINES_SCANF`.

Control flow centers on `verify_getuid`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process real UID and /proc/self/status cross-checks.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_EXP_POSITIVE`, `TST_PASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getuid/getuid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; getxattr05: LDLIBS	+= $(ACL_LIBS); include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, plus directory-specific linker libraries. The generated binaries exercise the `getxattr` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr01.c

Purpose:  Basic tests for getxattr(2) and make sure getxattr(2) handles error conditions correctly. 1. Get an non-existing attribute, getxattr(2) should return -1 and set errno to ENODATA. 2. Buffer size is smaller than attribute value size, getxattr(2) should return -1 and set errno to ERANGE. 3. Get attribute, getxattr(2) should succeed, and the attribute got by getxattr(2) should be same as the value we set.

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`, `sys/xattr.h`; touches `getxattr`; defines `run`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_MALLOC`, `SAFE_SETXATTR`.

Control flow centers on `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.needs_root`, `.setup`, `.cleanup`, `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `ENODATA`, `ERANGE`.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `stdlib.h`, `tst_test.h`, `sys/xattr.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_EXP_FAIL`, `TST_EXP_VAL`. Expected errno values include `ENODATA`, `ERANGE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr02.c

Purpose:  In the user.* namespace, only regular files and directories can have extended attributes. Otherwise getxattr(2) will return -1 and set errno to ENODATA. There are 4 test cases: - Get attribute from a FIFO, setxattr(2) should return -1 and set errno to ENODATA - Get attribute from a char special file, setxattr(2) should return -1 and set errno to ENODATA - Get attribute from a block special file, setxattr(2) should return -1 and set errno to ENODATA - Get attribute from a UNIX domain socket, setxattr(2) should retu

Important APIs/types/functions: includes `sys/types.h`, `sys/sysmacros.h`, `sys/xattr.h`, `stdio.h`, `stdlib.h`, `tst_res_flags.h`, `tst_test.h`, `tst_test_macros.h`; touches `getxattr`, `socket`; defines `run`, `setup`; uses LTP safe helpers such as `SAFE_TOUCH`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.setup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `ENODATA`, `ENOTSUP`.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `sys/types.h`, `sys/sysmacros.h`, `sys/xattr.h`, `stdio.h`, `stdlib.h`, `tst_res_flags.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`. Expected errno values include `ENODATA`, `ENOTSUP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr03.c

Purpose:  An empty buffer of size zero can be passed into getxattr(2) to return the current size of the named extended attribute.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `sys/xattr.h`, `tst_safe_macros.h`; touches `getxattr`; defines `run`, `setup`; uses LTP safe helpers such as `SAFE_SETXATTR`, `SAFE_TOUCH`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.setup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `config.h`, `tst_test.h`, `sys/xattr.h`, `tst_safe_macros.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TST_EXP_VAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr04.c

Purpose:  This is a regression test for the race between getting an existing xattr and setting/removing a large xattr. This bug leads to that getxattr() fails to get an existing xattr and returns ENOATTR in xfs filesystem. This bug has been fixed in: 5a93790d4e2d ("xfs: remove racy hasattr check from attr ops")

Important APIs/types/functions: includes `config.h`, `errno.h`, `sys/types.h`, `string.h`, `stdlib.h`, `signal.h`, `tst_test.h`; touches `getxattr`; defines `sigproc`, `loop_getxattr`, `verify_getxattr`, `setup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_REMOVEXATTR`, `SAFE_SETXATTR`, `SAFE_SIGNAL`, `SAFE_TOUCH`.

Control flow centers on `sigproc`, `loop_getxattr`, `verify_getxattr`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.forks_child`, `.test_all`, `.setup` into the LTP runner. Error-path assertions cover `ENOATTR`, `ENODATA`.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `config.h`, `errno.h`, `sys/types.h`, `string.h`, `stdlib.h`, `signal.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`. Expected errno values include `ENOATTR`, `ENODATA`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr05.c

Purpose:  This test verifies that: - Without a user namespace, getxattr(2) should get same data when acquiring the value of system.posix_acl_access twice. - With/Without mapped root UID in a user namespaces, getxattr(2) should get same data when acquiring the value of system.posix_acl_access twice. This issue included by getxattr05 has been fixed in kernel: 82c9a927bc5d ("getxattr: use correct xattr length")

Important APIs/types/functions: includes `config.h`, `errno.h`, `unistd.h`, `sys/types.h`, `stdlib.h`, `tst_test.h`, `lapi/sched.h`; touches `getxattr`; defines `verify_getxattr`, `do_unshare`, `do_getxattr`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_ACCESS`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_FORK`, `SAFE_GETXATTR`, `SAFE_TOUCH`.

Control flow centers on `verify_getxattr`, `do_unshare`, `do_getxattr`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.needs_root`, `.forks_child`, `.setup`, `.cleanup`, `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EOPNOTSUPP`.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `config.h`, `errno.h`, `unistd.h`, `sys/types.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`, `TFAIL`, `TPASS`, `TST_TEST_TCONF`. Expected errno values include `EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/init_module/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `obj-m := init_module.o; top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; REQ_VERSION_MAJOR	:= 2; REQ_VERSION_PATCH	:= 6; MAKE_TARGETS		:= init_module01 init_module02 init_module.ko; include $(top_srcdir)/include/mk/module.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, and the kernel module build path. The generated binaries exercise the `init_module` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module.c

Purpose: Dummy kernel module used by init_module syscall tests; it accepts a status parameter and fails initialization when status is invalid.

Important APIs/types/functions: includes `linux/module.h`, `linux/init.h`, `linux/proc_fs.h`, `linux/kernel.h`; defines `dummy_init`, `dummy_exit`.

Control flow centers on `dummy_init`, `dummy_exit`. Error-path assertions cover `EINVAL`.

State and persistence behavior: Runtime state is kernel module loading, module signature enforcement, CAP_SYS_MODULE permission, and module reference cleanup.

Dependencies and integration points: Depends on building init_module.ko, CAP_SYS_MODULE, kernel module loading policy, signature enforcement settings, and tst_module helpers. Direct include dependencies include `linux/module.h`, `linux/init.h`, `linux/proc_fs.h`, `linux/kernel.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals come from consumers of this helper and from compile-time availability checks. Expected errno values include `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module01.c

Purpose:  Basic init_module() tests. [Algorithm] Inserts a simple module after opening and mmaping the module file.

Important APIs/types/functions: includes `stdlib.h`, `errno.h`, `lapi/init_module.h`, `tst_module.h`; touches `init_module`, `munmap`; defines `setup`, `run`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FSTAT`, `SAFE_MMAP`, `SAFE_OPEN`.

Control flow centers on `setup`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.needs_root` into the LTP runner. Error-path assertions cover `EKEYREJECTED`.

State and persistence behavior: Runtime state is kernel module loading, module signature enforcement, CAP_SYS_MODULE permission, and module reference cleanup.

Dependencies and integration points: Depends on building init_module.ko, CAP_SYS_MODULE, kernel module loading policy, signature enforcement settings, and tst_module helpers. Direct include dependencies include `stdlib.h`, `errno.h`, `lapi/init_module.h`, `tst_module.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`, `TST_EXP_PASS`, `TST_PASS`. Expected errno values include `EKEYREJECTED`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module02.c

Purpose:  Basic init_module() failure tests. [Algorithm] Tests various failure scenarios for init_module().

Important APIs/types/functions: includes `linux/capability.h`, `stdlib.h`, `errno.h`, `lapi/init_module.h`, `tst_module.h`, `tst_capability.h`; touches `init_module`, `munmap`; defines `setup`, `run`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FSTAT`, `SAFE_MMAP`, `SAFE_OPEN`.

Control flow centers on `setup`, `run`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_root` into the LTP runner. Error-path assertions cover `EEXIST`, `EFAULT`, `EINVAL`, `EKEYREJECTED`, `ENOEXEC`, `EPERM`.

State and persistence behavior: Runtime state is kernel module loading, module signature enforcement, CAP_SYS_MODULE permission, and module reference cleanup.

Dependencies and integration points: Depends on building init_module.ko, CAP_SYS_MODULE, kernel module loading policy, signature enforcement settings, and tst_module helpers. Direct include dependencies include `linux/capability.h`, `stdlib.h`, `errno.h`, `lapi/init_module.h`, `tst_module.h`, `tst_capability.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TST_CAP`, `TST_CAP_DROP`, `TST_CAP_REQ`, `TST_EXP_FAIL`, `TST_PASS`, `TST_RET`. Expected errno values include `EEXIST`, `EFAULT`, `EINVAL`, `EKEYREJECTED`, `ENOEXEC`, `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; inotify09: CFLAGS+=-pthread; inotify09: LDLIBS+=-lrt; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, plus directory-specific linker libraries, with local compiler flags. The generated binaries exercise the `inotify` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify.h

Purpose: Common inotify wrapper header that maps raw inotify syscalls and turns unsupported kernels or watch failures into LTP results.

Important APIs/types/functions: includes `lapi/syscalls.h`; touches `inotify_init`, `inotify_add_watch`, `raw syscall path`; defines `safe_myinotify_init`, `safe_myinotify_watch`; uses LTP safe helpers such as `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_MYINOTIFY_INIT1`.

Control flow centers on `safe_myinotify_init`, `safe_myinotify_watch`. Error-path assertions cover `ENOSYS`.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`. Expected errno values include `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify01.c

Purpose:  Basic test for inotify events on file.

Important APIs/types/functions: includes `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`, `string.h`, `sys/syscall.h`; touches `getpid`, `inotify_rm_watch`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CHMOD`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_WRITE`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify02.c

Purpose:  Basic test for inotify events on directory.

Important APIs/types/functions: includes `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`, `string.h`, `sys/syscall.h`; touches `inotify_rm_watch`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CHMOD`, `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_GETCWD`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_READ`, `SAFE_RENAME`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify03.c

Purpose:  Check that inotify get IN_UNMOUNT event and don't block the umount command.

Important APIs/types/functions: includes `config.h`, `stdio.h`, `sys/mount.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`, `string.h`; touches `getpid`, `inotify_rm_watch`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_WRITE`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.format_device`, `.setup`, `.cleanup`, `.test_all` into the LTP runner. Error-path assertions cover `EINVAL`.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `sys/mount.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TST_TEST_TCONF`. Expected errno values include `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify04.c

Purpose: Ngie Cooper, April 2012 Test for inotify IN_DELETE_SELF event. [Algorithm] This testcase creates a temporary directory, then add watches to a predefined file and subdirectory, and delete the file and directory to ensure that the IN_DELETE_SELF event is captured properly. Because of how the inotify(7) API is designed, we also need to catch the IN_ATTRIB and IN_IGNORED events.

Important APIs/types/functions: includes `config.h`, `errno.h`, `string.h`, `tst_test.h`, `inotify.h`; touches `inotify_rm_watch`; defines `cleanup`, `setup`, `verify_inotify`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_MKDIR`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_READ`, `SAFE_RMDIR`, `SAFE_UNLINK`.

Control flow centers on `cleanup`, `setup`, `verify_inotify`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `errno.h`, `string.h`, `tst_test.h`, `inotify.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify05.c

Purpose:  Check that inotify overflow event is properly generated.

Important APIs/types/functions: includes `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`, `string.h`, `sys/syscall.h`; touches `getpid`, `inotify_rm_watch`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_SCANF`, `SAFE_LSEEK`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT1`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_WRITE`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify06.c

Purpose:  Test for inotify mark destruction race. Kernels prior to 4.2 have a race when inode is being deleted while inotify group watching that inode is being torn down. When the race is hit, the kernel crashes or loops. The problem has been fixed by commit: 8f2f3eb59dff ("fsnotify: fix oops in fsnotify_clear_marks_by_group_flags()").

Important APIs/types/functions: includes `config.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `fcntl.h`, `time.h`, `signal.h`, `sys/time.h`; defines `setup`, `verify_inotify`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_FORK`, `SAFE_KILL`, `SAFE_MYINOTIFY_INIT1`, `SAFE_OPEN`, `SAFE_UNLINK`.

Control flow centers on `setup`, `verify_inotify`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.needs_tmpdir`, `.forks_child`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `fcntl.h`, `time.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify07.c

Purpose:  Check that inotify work for an overlayfs directory after copy up and drop caches. An inotify watch pins the directory inode in cache, but not the dentry. The watch will not report events on the directory if overlayfs does not obtain the pinned inode to the new allocated dentry after drop caches. The problem has been fixed by commit: 31747eda41ef ("ovl: hash directory inodes for fsnotify"). [Algorithm] Add watch on an overlayfs lower directory then chmod directory and drop dentry and inode caches. Execute operation

Important APIs/types/functions: includes `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`, `string.h`, `sys/syscall.h`; touches `inotify_rm_watch`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CHMOD`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_MOUNT_OVERLAY`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT1`, `SAFE_READ`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.needs_overlay`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify08.c

Purpose:  Check that inotify work for an overlayfs file after copy up and drop caches. An inotify watch pins the file inode in cache, but not the dentry. The watch will not report events on the file if overlayfs does not obtain the pinned inode to the new allocated dentry after drop caches. The problem has been fixed by commit: 764baba80168 ("ovl: hash non-dir by lower inode for fsnotify"). [Algorithm] Add watch on an overlayfs lower file then chmod file and drop dentry and inode caches. Execute operations on file and expec

Important APIs/types/functions: includes `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `sys/sysmacros.h`, `fcntl.h`, `errno.h`, `string.h`; touches `inotify_rm_watch`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CHMOD`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MOUNT_OVERLAY`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT1`, `SAFE_READ`, `SAFE_READ_ANY_EAGAIN`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.needs_overlay`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `sys/sysmacros.h`, `fcntl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify09.c

Purpose: Chnaged to use fzsync library by Cyril Hrubis <chrubis@suse.cz> Test for inotify mark connector destruction race. Kernels prior to 4.17 have a race when the last fsnotify mark on the inode is being deleted while another process reports event happening on that inode. When the race is hit, the kernel crashes or loops. The problem has been fixed by commit: d90a10e2444b ("fsnotify: Fix fsnotify_mark_connector race").

Important APIs/types/functions: includes `config.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `fcntl.h`, `time.h`, `signal.h`, `sys/time.h`; touches `inotify_rm_watch`; defines `setup`, `cleanup`, `verify_inotify`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_LSEEK`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT1`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ANY`.

Control flow centers on `setup`, `cleanup`, `verify_inotify`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `fcntl.h`, `time.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify10.c

Purpose: Started by Amir Goldstein <amir73il@gmail.com> Check that event is reported to watching parent and watching child based on their interest. Test case #3 is a regression test for commit fecc4559780d that fixes a bug introduced in kernel v5.9: fecc4559780d ("fsnotify: fix events reported to watching parent and child").

Important APIs/types/functions: includes `config.h`, `errno.h`, `string.h`, `tst_test.h`, `inotify.h`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CHMOD`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_READ`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test`, `.tcnt` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `errno.h`, `string.h`, `tst_test.h`, `inotify.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify11.c

Purpose: Started by Amir Goldstein <amir73il@gmail.com> based on reproducer from Ivan Delalande <colona@arista.com> Test opening files after receiving IN_DELETE. Kernel v5.13 has a regression allowing files to be open after IN_DELETE. The problem has been fixed by commit: a37d9a17f099 ("fsnotify: invalidate dcache before IN_DELETE event").

Important APIs/types/functions: includes `config.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `signal.h`, `sys/wait.h`, `tst_test.h`, `tst_safe_macros.h`; defines `churn`, `verify_inotify`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_FORK`, `SAFE_KILL`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_READ`, `SAFE_UNLINK`.

Control flow centers on `churn`, `verify_inotify`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.forks_child`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `signal.h`, `sys/wait.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify12.c

Purpose:  Test special inotify mask flags. Regression test for kernel commit: a32e697cda27 ("inotify: show inotify mask flags in proc fdinfo").

Important APIs/types/functions: includes `config.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `signal.h`, `sys/wait.h`, `tst_test.h`, `tst_safe_macros.h`; touches `getpid`; defines `verify_inotify`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT1`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_UNLINK`, `SAFE_WRITE`.

Control flow centers on `verify_inotify`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.cleanup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `EAGAIN`.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `signal.h`, `sys/wait.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`. Expected errno values include `EAGAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk. The generated binaries exercise the `inotify_init` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/inotify_init1_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/inotify_init1_01.c

Purpose: Ported to LTP - Jan 13 2009 - Subrata <subrata@linux.vnet.ibm.com> Verify that inotify_init1() returns a file descriptor and sets the close-on-exec (FD_CLOEXEC) flag on the new file descriptor only when called with IN_CLOEXEC.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`; touches `inotify_init1`, `raw syscall path`; defines `run`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FCNTL`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is a newly created inotify file descriptor and its close-on-exec/nonblocking flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_EQ_LI`, `TST_EXP_FD`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/inotify_init1_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/inotify_init1_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/inotify_init1_02.c

Purpose: Ported to LTP - Jan 13 2009 - Subrata <subrata@linux.vnet.ibm.com> Verify that inotify_init1() returns a file descriptor and sets the O_NONBLOCK file status flag on the open file description referred to by the new file descriptor only when called with IN_NONBLOCK.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`; touches `inotify_init1`, `raw syscall path`; defines `run`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FCNTL`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is a newly created inotify file descriptor and its close-on-exec/nonblocking flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_EQ_LI`, `TST_EXP_FD`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/inotify_init1_02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; LDLIBS			+= $(AIO_LIBS); include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, plus directory-specific linker libraries. The generated binaries exercise the `io_cancel` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/io_cancel01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/io_cancel01.c

Purpose: Ported from Crackerjack to LTP by Masatake YAMATO <yamato@redhat.com> Test io_cancel invoked via syscall(2) with one of pointers set to invalid address and expects it to return EFAULT.

Important APIs/types/functions: includes `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`; touches `io_cancel`, `raw syscall path`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `EFAULT`.

State and persistence behavior: Runtime state is Linux AIO context identifiers and request/event pointers passed through syscall or libaio wrappers.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/io_cancel01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/io_cancel02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/io_cancel02.c

Purpose: Ported from Crackerjack to LTP by Masatake YAMATO <yamato@redhat.com> Test io_cancel invoked via libaio with one of the data structures points to invalid data and expects it to return -EFAULT.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `libaio.h`; touches `io_cancel`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `EFAULT`.

State and persistence behavior: Runtime state is Linux AIO context identifiers and request/event pointers passed through syscall or libaio wrappers.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `config.h`, `tst_test.h`, `libaio.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_RET`, `TST_TEST_TCONF`. Expected errno values include `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/io_cancel02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_destroy/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_destroy/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; LDLIBS			+= $(AIO_LIBS); include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, plus directory-specific linker libraries. The generated binaries exercise the `io_destroy` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_destroy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_destroy/io_destroy01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_destroy/io_destroy01.c

Purpose: Ported from Crackerjack to LTP by Masatake YAMATO <yamato@redhat.com> Test io_destroy invoked via libaio with invalid ctx and expects it to return -EINVAL.

Important APIs/types/functions: includes `errno.h`, `string.h`, `config.h`, `tst_test.h`, `libaio.h`; touches `io_destroy`; defines `verify_io_destroy`.

Control flow centers on `verify_io_destroy`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `EINVAL`, `ENOSYS`.

State and persistence behavior: Runtime state is Linux AIO context identifiers and invalid context teardown behavior.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `string.h`, `config.h`, `tst_test.h`, `libaio.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`, `TST_RET`, `TST_TEST_TCONF`. Expected errno values include `EINVAL`, `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_destroy/io_destroy01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_destroy/io_destroy02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_destroy/io_destroy02.c

Purpose: Ported from Crackerjack to LTP by Masatake YAMATO <yamato@redhat.com> Test io_destroy invoked via syscall(2) with an invalid ctx and expects it to return EINVAL.

Important APIs/types/functions: includes `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`; touches `io_destroy`, `raw syscall path`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `EINVAL`.

State and persistence behavior: Runtime state is Linux AIO context identifiers and invalid context teardown behavior.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_destroy/io_destroy02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/Makefile

Purpose: build glue for the LTP syscall tests in this source directory. It does not implement runtime test logic; it declares how the local test binaries or helper artifacts are compiled.

Important APIs/types/functions: Make variables and includes used here are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; LDLIBS			+= $(AIO_LIBS); include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make includes the shared LTP testcase rules, then applies any local target filters, CFLAGS, LDLIBS, or module targets before the common build machinery expands test binaries.

State and persistence behavior: no runtime state is kept by this file. Its persistent effect is build metadata that determines which binaries, helper objects, or kernel modules are emitted.

Dependencies and integration points: integrates with LTP make fragments under include/mk/testcases.mk, plus directory-specific linker libraries. The generated binaries exercise the `io_getevents` syscall test directory.

Risks and test signals: a missing library, unsupported kernel-module build, or filtered target changes coverage before runtime. The signal is successful compilation and presence of the expected local test executable targets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/io_getevents01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/io_getevents01.c

Purpose: Ported from Crackerjack to LTP by Masatake YAMATO <yamato@redhat.com> Test io_getevents invoked via syscall(2) with invalid ctx and expects it to return EINVAL.

Important APIs/types/functions: includes `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`; touches `io_getevents`, `raw syscall path`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `EINVAL`.

State and persistence behavior: Runtime state is Linux AIO context identifiers plus event arrays/timeouts supplied to io_getevents.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL2`. Expected errno values include `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/io_getevents01.c -->
