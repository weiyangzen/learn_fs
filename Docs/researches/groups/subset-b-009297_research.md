<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl21.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl21.c

Purpose: Legacy record-lock stress test that forks a child and parent to exercise POSIX byte-range locking, `F_SETLK`, `F_SETLKW`, and `F_GETLK` over a temporary file containing known alphabet data. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA NAME fcntl21.c DESCRIPTION Check locking of regions of a file ALGORITHM Test changing lock sections around a read lock USAGE fcntl21 HISTORY 07/2001 Ported by Wayne Boyer... The file was read in full for this report (849 lines, 18439 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), wait(), close(), pipe(), read(), write(), sigaction(); types/structs: struct flock, struct sigaction; functions: setup, cleanup, do_child, do_lock, do_test, compare_lock, unlock_file, parent_put, parent_get, child_put, child_get, stop_child, catch_child, main; local macros/constants: STRINGSIZE, STRING, STOP.

Control flow: setup path: setup; exercise path: do_child, do_lock, do_test, parent_put, parent_get, child_put, child_get, stop_child, catch_child, main; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `fcntl.h`, `errno.h`, `signal.h`, `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `inttypes.h`, `test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit failure reporting; key constants: PATH_MAX, SIGCHLD, F_GETLK, F_SETLK, F_UNLCK, F_WRLCK, F_RDLCK.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl22.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl22.c

Purpose: Checks `F_SETLK` contention: a parent holds a write lock, the child attempts a conflicting nonblocking lock, and the expected result is `EAGAIN`. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA Test Name: fcntl22 Test Description: Verify that, fcntl() fails with -1 and sets errno to EAGAIN when Operation is prohibited by locks held by other processes. Expected Re... The file was read in full for this report (127 lines, 2772 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), close(); types/structs: struct flock; functions: main, setup, cleanup.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `fcntl.h`, `errno.h`, `signal.h`, `stdlib.h`, `sys/types.h`, `sys/wait.h`, `test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EAGAIN; key constants: F_SETLK, F_WRLCK.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl22.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl23.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl23.c

Purpose: Exercises `F_SETLEASE` with `F_RDLCK`, confirms `F_GETLEASE` reports the read lease, then releases it with `F_UNLCK`. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA ******************************************************** TEST IDENTIFIER : fcntl23 EXECUTED BY : anyone TEST TITLE : Basic test for fcntl(2) using F_SETLEASE & F_RDLCK arg... The file was read in full for this report (212 lines, 5475 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), open(), close(); functions: main, setup, cleanup.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `errno.h`, `string.h`, `signal.h`, `test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: filesystem-specific semantics can change expected results.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXECUTED, ENVIRONMENTAL; key constants: F_SETLEASE, F_RDLCK, SIGNALS, SIGUSR1, F_GETLEASE, F_UNLCK, O_RDONLY, O_CREAT.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl24.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl24.c

Purpose: Exercises `F_SETLEASE` with `F_WRLCK`, confirms `F_GETLEASE` reports the write lease, and handles overlayfs lease limitations as expected configuration behavior. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA ******************************************************** TEST IDENTIFIER : fcntl24 EXECUTED BY : anyone TEST TITLE : Basic test for fcntl(2) using F_SETLEASE & F_WRLCK arg... The file was read in full for this report (216 lines, 5620 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), open(), close(); functions: main, setup, cleanup.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `errno.h`, `string.h`, `signal.h`, `test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: filesystem-specific semantics can change expected results.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXECUTED, ENVIRONMENTAL, EAGAIN; key constants: F_SETLEASE, F_WRLCK, SIGNALS, SIGUSR1, F_GETLEASE, F_UNLCK, O_RDWR, O_CREAT.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl25.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl25.c

Purpose: Legacy write-lease test variant focused on `F_SETLEASE/F_WRLCK` success, `F_GETLEASE`, and explicit unlock cleanup. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA ******************************************************** TEST IDENTIFIER : fcntl25 EXECUTED BY : anyone TEST TITLE : Basic test for fcntl(2) using F_SETLEASE & F_WRLCK arg... The file was read in full for this report (217 lines, 5723 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), open(), close(); functions: main, setup, cleanup.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `errno.h`, `string.h`, `signal.h`, `test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: filesystem-specific semantics can change expected results.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXECUTED, ENVIRONMENTAL, EAGAIN; key constants: F_SETLEASE, F_WRLCK, SIGNALS, SIGUSR1, F_GETLEASE, F_UNLCK, O_RDONLY, O_CREAT.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl26.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl26.c

Purpose: Legacy write-lease test variant with the same lease acquisition/get/unlock sequence used to catch filesystem-specific lease regressions. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA ******************************************************** TEST IDENTIFIER : fcntl26 EXECUTED BY : anyone TEST TITLE : Basic test for fcntl(2) using F_SETLEASE & F_WRLCK arg... The file was read in full for this report (217 lines, 5721 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), open(), close(); functions: main, setup, cleanup.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `errno.h`, `string.h`, `signal.h`, `test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: filesystem-specific semantics can change expected results.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXECUTED, ENVIRONMENTAL, EAGAIN; key constants: F_SETLEASE, F_WRLCK, SIGNALS, SIGUSR1, F_GETLEASE, F_UNLCK, O_WRONLY, O_CREAT.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl26.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl27.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl27.c

Purpose: Modern negative lease test proving `F_SETLEASE/F_RDLCK` fails with `EAGAIN` for selected open-mode combinations. Source notes: Author: Jacky Malcles \ Basic test for fcntl(2) using F_SETLEASE and F_RDLCK argument, testing O_RDWR and O_WRONLY. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (45 lines, 990 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_OPEN, TST_EXP_FAIL, SAFE_CLOSE; types/structs: struct test_case, struct tst_test; functions: verify_fcntl; local macros/constants: TC.

Control flow: exercise path: verify_fcntl; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `lapi/fcntl.h`, `tst_test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit failure reporting; errno checks: EAGAIN; key constants: F_SETLEASE, F_RDLCK, O_RDWR, O_WRONLY, O_CREAT; harness metadata: .test, .tcnt, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl27.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl29.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl29.c

Purpose: Verifies `F_DUPFD_CLOEXEC` duplicates a descriptor and sets `FD_CLOEXEC` on the new descriptor. Source notes: Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> \ Basic test for fcntl(2) using F_DUPFD_CLOEXEC and getting FD_CLOEXEC. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (47 lines, 905 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_CREAT, SAFE_CLOSE, TST_EXP_FD, TST_EXP_POSITIVE; types/structs: struct tst_test; functions: setup, cleanup, run.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `lapi/fcntl.h`, `tst_test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: F_DUPFD_CLOEXEC, F_GETFD; harness metadata: .test_all, .setup, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl29.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl30.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl30.c

Purpose: Validates `F_GETPIPE_SZ` and `F_SETPIPE_SZ` on a pipe using `/proc/sys/fs/pipe-max-size` as the unprivileged maximum. Source notes: Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> \ Verify that, fetching and changing the capacity of a pipe works as expected with fcntl(2) syscall using F_GETPIPE_SZ, F_SETPIPE_SZ arguments. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (52 lines, 1127 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_PIPE, TST_EXP_POSITIVE, TST_EXP_EXPR, SAFE_CLOSE, SAFE_FILE_SCANF; types/structs: struct tst_test; functions: run, setup, cleanup.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: key constants: F_GETPIPE_SZ, F_SETPIPE_SZ, PATH_FS_PIPE_MAX_SIZE; harness metadata: .test_all, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl31.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl31.c

Purpose: Comprehensive asynchronous I/O owner/signal test for `F_SETOWN`, `F_GETOWN`, `F_SETOWN_EX`, `F_GETOWN_EX`, `F_SETSIG`, and `F_GETSIG`. Source notes: Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. You should have received a copy of the GNU General Public License along with this program; if not, write the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA. Description: Verify that: Basic test for fcntl(2) using F_GETOWN, F_SETOWN, F_GETOWN_EX, F_SETOWN_EX, F_GETSIG, F_SETSIG argument. we have these tests on pipe Changing process group ID is forbidden when PID == SID i.e. we are sessio... The file was read in full for this report (361 lines, 8287 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), wait(), close(), write(), SAFE_PIPE, SAFE_READ; types/structs: struct f_owner_ex, struct timespec; functions: main, setup, setown_pid_test, setown_pgrp_test, setownex_cleanup, setownex_tid_test, setownex_pid_test, setownex_pgrp_test, test_set_and_get_sig, signal_parent, check_io_signal, cleanup.

Control flow: setup path: setup; exercise path: main, setown_pid_test, setown_pgrp_test, setownex_tid_test, setownex_pid_test, setownex_pgrp_test, test_set_and_get_sig, signal_parent; cleanup path: setownex_cleanup, cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `errno.h`, `unistd.h`, `string.h`, `signal.h`, `sys/types.h`, `sys/wait.h`, `pwd.h`, `sched.h`, `test.h`, `config.h`, `lapi/syscalls.h`, `tso_safe_macros.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: F_GETOWN, F_SETOWN, F_GETOWN_EX, F_SETOWN_EX, F_GETSIG, F_SETSIG, F_SETFL, O_ASYNC, SIGUSR1, SIGIO, F_OWNER_TID, __NR_gettid.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl32.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl32.c

Purpose: Checks write leases against duplicate opens and verifies expected lease break behavior for read/write access combinations. Source notes: Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. You should have received a copy of the GNU General Public License alone with this program. DESCRIPTION Basic test for fcntl(2) using F_SETLEASE & F_WRLCK argument. "A write lease may be placed on a file only if there are no other open file descriptors for the file." The file was read in full for this report (137 lines, 2939 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), close(), SAFE_TOUCH, SAFE_OPEN, SAFE_CLOSE; types/structs: struct test_case_t; functions: main, setup, verify_fcntl, cleanup; local macros/constants: FILE_MODE.

Control flow: setup path: setup; exercise path: main, verify_fcntl; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `test.h`, `tso_safe_macros.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: filesystem-specific semantics can change expected results.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBUSY, EAGAIN; key constants: F_SETLEASE, F_WRLCK, O_RDONLY, O_WRONLY, O_RDWR.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl33.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl33.c

Purpose: Fork/checkpoint lease-breaking test covering write/read leases against conflicting open/truncate operations and `/proc/sys/fs/lease-break-time` restoration. Source notes: Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> DESCRIPTION Test for feature F_SETLEASE of fcntl(2). "F_SETLEASE is used to establish a lease which provides a mechanism: When a process (the lease breaker) performs an open(2) or truncate(2) that conflicts with the lease, the system call will be blocked by kernel, meanwhile the kernel notifies the lease holder by sending it a signal (SIGIO by default), after the lease holder successes to downgrade or remove the lease, the kernel permits the system call of the lease breaker to proceed." MIN_TIME_LIMIT is defined to 5 senconds as a minimal acceptable amount of time for the lease breaker waiting for unblock via lease holder voluntarily downgrade or remove the lease, if the lease breaker is unblocked within MIN_TIME_LIMIT we may consider that the feature of the lease mechanism works well.... The file was read in full for this report (229 lines, 5579 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), open(), truncate(), SAFE_FILE_SCANF, SAFE_FILE_PRINTF, SAFE_TOUCH, SAFE_FORK, SAFE_OPEN, TST_CHECKPOINT_WAKE, SAFE_CLOSE, TST_CHECKPOINT_WAIT, SAFE_TRUNCATE; types/structs: struct timespec, struct test_case_t, struct tst_test; functions: setup, do_test, do_child, cleanup; local macros/constants: MIN_TIME_LIMIT, OP_OPEN_RDONLY, OP_OPEN_WRONLY, OP_OPEN_RDWR, OP_TRUNCATE, FILE_MODE, PATH_LS_BRK_T.

Control flow: setup path: setup; exercise path: do_test, do_child; cleanup path: cleanup; notable execution mechanics: iterates a case table, forks child processes for concurrency or privilege separation, uses LTP checkpoints to order parent/child actions.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, kernel tunables that setup/cleanup must restore, UID/capability-sensitive kernel state, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `tst_test.h`, `tst_timer.h`, `tst_safe_macros.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; filesystem-specific semantics can change expected results; must restore proc/sys tunables after failures; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EAGAIN; key constants: F_SETLEASE, SIGIO, PATH_LS_BRK_T, F_WRLCK, O_RDONLY, O_WRONLY, O_RDWR, F_RDLCK, CLOCK_MONOTONIC, F_UNLCK; harness metadata: .forks_child, .needs_root, .needs_checkpoints, .tcnt, .setup, .test, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl33.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl34.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl34.c

Purpose: Open-file-description lock write test that uses multiple pthreads to append patterned data safely under OFD locks. Source notes: Author: Alexey Kodanev <alexey.kodanev@oracle.com> SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (131 lines, 2642 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_PTHREAD_CREATE, SAFE_PTHREAD_JOIN, SAFE_OPEN, SAFE_LSEEK, SAFE_WRITE, SAFE_CLOSE, SAFE_READ; types/structs: struct flock, struct tst_test; functions: setup, spawn_threads, wait_threads, thread_fn_01, test01.

Control flow: setup path: setup; exercise path: thread_fn_01, test01; notable execution mechanics: uses pthread workers for concurrent access.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, threads and shared in-process synchronization, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `unistd.h`, `pthread.h`, `sched.h`, `fcntl_common.h`, `tst_safe_pthread.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, F_WRLCK, F_OFD_SETLKW, F_UNLCK, O_CREAT, O_TRUNC; harness metadata: .needs_tmpdir, .test_all, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl34.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl35.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl35.c

Purpose: Pipe capacity privilege regression test proving unprivileged users cannot exceed `/proc/sys/fs/pipe-max-size` while privileged paths can use larger pipe sizes. Source notes: Author: Xiao Yang <yangx.jy@cn.fujitsu.com> Description: fcntl(2) manpage states that an unprivileged user could not set the pipe capacity above the limit in /proc/sys/fs/pipe-max-size. However, an unprivileged user could create a pipe whose initial capacity exceeds the limit. We add a regression test to check that pipe-max-size caps the initial allocation for a new pipe for unprivileged users, but not for privileged users. This kernel bug has been fixed by: commit 086e774a57fba4695f14383c0818994c0b31da7c Author: Michael Kerrisk (man-pages) <mtk.manpages@gmail.com> Date: Tue Oct 11 13:53:43 2016 -0700 pipe: cap initial pipe capacity according to pipe-max-size limit SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (124 lines, 2783 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_FILE_SCANF, SAFE_FILE_PRINTF, SAFE_GETPWNAM, SAFE_PIPE, SAFE_CLOSE, SAFE_FORK, SAFE_SETUID; types/structs: struct passwd, struct tcase, struct tst_test, struct tst_tag; functions: setup, cleanup, verify_pipe_size, do_test.

Control flow: setup path: setup; exercise path: verify_pipe_size, do_test; cleanup path: cleanup; notable execution mechanics: iterates a case table, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, kernel tunables that setup/cleanup must restore, UID/capability-sensitive kernel state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/types.h`, `pwd.h`, `unistd.h`, `stdlib.h`, `lapi/fcntl.h`, `tst_test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; must restore proc/sys tunables after failures; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: PATH_FS_PIPE_MAX_SIZE, F_OK, F_GETPIPE_SZ; harness metadata: .needs_root, .forks_child, .tcnt, .setup, .cleanup, .test, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl36.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl36.c

Purpose: OFD lock concurrency stress test comparing OFD and POSIX locking behavior across threaded readers/writers and validating final file contents. Source notes: Author: Xiong Zhou <xzhou@redhat.com> This is testing OFD locks racing with POSIX locks: OFD read lock vs OFD write lock OFD read lock vs POSIX write lock OFD write lock vs POSIX write lock OFD write lock vs POSIX read lock OFD write lock vs OFD write lock OFD r/w locks vs POSIX write locks OFD r/w locks vs POSIX read locks For example: Init an file with preset values. Threads acquire OFD READ locks to read a 4k section start from 0; checking data read back, there should not be any surprise values and data should be consistent in a 1k block. Threads acquire OFD WRITE locks to write a 4k section start from 1k, writing different values in different threads. Check file data after racing, there should not be any surprise values and data should be consistent in a 1k block. OFD write lock writing data POSIX write lock writing data SPDX-Licen... The file was read in full for this report (395 lines, 8364 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_OPEN, SAFE_LSEEK, SAFE_WRITE, SAFE_CLOSE, SAFE_FCNTL, SAFE_READ, SAFE_PTHREAD_CREATE, SAFE_PTHREAD_JOIN; types/structs: struct param, struct flock, struct tcase, struct tst_test; functions: setup, fn_ofd_w, fn_posix_w, fn_ofd_r, fn_posix_r, fn_dummy, test_fn, tests.

Control flow: setup path: setup; exercise path: fn_ofd_w, fn_posix_w, fn_ofd_r, fn_posix_r, fn_dummy, test_fn, tests; notable execution mechanics: iterates a case table, uses pthread workers for concurrent access.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, threads and shared in-process synchronization, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `unistd.h`, `stdio.h`, `stdlib.h`, `pthread.h`, `sched.h`, `errno.h`, `lapi/fcntl.h`, `tst_safe_pthread.h`, `tst_test.h`, `fcntl_common.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, F_WRLCK, F_OFD_SETLKW, F_UNLCK, F_SETLKW, F_RDLCK, F_OFD_SETLK, F_SETLK, O_RDONLY; harness metadata: .timeout, .needs_tmpdir, .test, .tcnt, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl36.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl37.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl37.c

Purpose: Negative pipe-size test for `F_SETPIPE_SZ`, including too-small, too-large, and over-capacity values. Source notes: Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com> Test basic error handling for fcntl(2) using F_SETPIPE_SZ, F_GETPIPE_SZ argument. 1)fcntl fails with EINVAL when cmd is F_SETPIPE_SZ and the arg is beyond 1<<31. 2)fcntl fails with EBUSY when cmd is F_SETPIPE_SZ and the arg is smaller than the amount of the current used buffer space. 3)fcntl fails with EPERM when cmd is F_SETPIPE_SZ and the arg is over /proc/sys/fs/pipe-max-size limit under unprivileged users. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (97 lines, 2451 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_PIPE, SAFE_MALLOC, SAFE_WRITE, SAFE_FILE_SCANF, SAFE_CLOSE, TST_CAP; types/structs: struct tcase, struct tst_test, struct tst_cap; functions: verify_fcntl, setup, cleanup.

Control flow: setup path: setup; exercise path: verify_fcntl; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, kernel tunables that setup/cleanup must restore, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `unistd.h`, `sys/types.h`, `limits.h`, `stdlib.h`, `tst_test.h`, `lapi/fcntl.h`, `lapi/capability.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: must restore proc/sys tunables after failures.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, EBUSY, EPERM; key constants: F_SETPIPE_SZ, F_GETPIPE_SZ, F_GET, PATH_FS_PIPE_MAX_SIZE; harness metadata: .setup, .cleanup, .tcnt, .test.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl37.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl38.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl38.c

Purpose: Dnotify regression test for `fcntl(F_NOTIFY)` and `fcntl(F_SETSIG)`, proving a `DN_ATTRIB` change on a watched subdirectory is reported both to the parent directory watch and the subdirectory watch. Source notes: Started by Amir Goldstein <amir73il@gmail.com> DESCRIPTION Check that dnotify event is reported to both parent and subdir Watch "." and its children for changes Also watch subdir itself for changes Generate DN_ATTRIB event on subdir that should send a signal on both fds SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (96 lines, 2325 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), sigaction(), SAFE_OPEN, SAFE_CHMOD, SAFE_CLOSE, SAFE_MKDIR; types/structs: struct sigaction, struct tst_test; functions: dnotify_handler, setup_dnotify, verify_dnotify, setup, cleanup; local macros/constants: TEST_DIR, TEST_SIG.

Control flow: setup path: setup_dnotify, setup; exercise path: verify_dnotify; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `signal.h`, `stdio.h`, `unistd.h`, `tst_test.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers; declares kernel configuration requirements.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: SIGRTMIN, F_SETSIG, F_NOTIFY, O_RDONLY; harness metadata: .needs_tmpdir, .setup, .cleanup, .test_all, .needs_kconfigs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl38.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl39.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl39.c

Purpose: Dnotify rename regression test for `fcntl(F_NOTIFY)` with `DN_RENAME`, proving rename notifications are delivered only for renames inside the watched parent and not for moves into or out of the watched directory. Source notes: Started by Amir Goldstein <amir73il@gmail.com> \ Check that dnotify DN_RENAME event is reported only on rename inside same parent. Watch renames inside ".", but not in and out of "." Also watch for renames inside subdir, but not in and out of subdir Rename file from "." to subdir should not generate DN_RENAME on either Rename subdir itself should generate DN_RENAME on ".", but not on itself Cleanup before rerun SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (130 lines, 3202 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), sigaction(), SAFE_OPEN, SAFE_RENAME, SAFE_CLOSE, SAFE_MKDIR, SAFE_TOUCH; types/structs: struct sigaction, struct tst_test; functions: dnotify_handler, setup_dnotify, verify_dnotify, setup, cleanup; local macros/constants: TEST_DIR, TEST_DIR2, TEST_FILE, TEST_SIG.

Control flow: setup path: setup_dnotify, setup; exercise path: verify_dnotify; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `fcntl.h`, `signal.h`, `stdio.h`, `unistd.h`, `tst_test.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers; declares kernel configuration requirements.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: SIGRTMIN, F_SETSIG, F_NOTIFY, O_RDONLY; harness metadata: .needs_tmpdir, .setup, .cleanup, .test_all, .needs_kconfigs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl39.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl40.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl40.c

Purpose: Basic `fcntl(F_CREATED_QUERY)` test that distinguishes descriptors opened on an existing file from a descriptor that actually created a file with `O_CREAT | O_CLOEXEC`. Source notes: \ Basic test for fcntl using F_CREATED_QUERY. Verify if the fcntl() syscall is recognizing whether a file has been created or not via O_CREAT when O_CLOEXEC is also used. Test is based on a kernel selftests commit d0fe8920cbe4. We didn't create "/dev/null". We're opening it again, so no positive creation check. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (46 lines, 1099 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_OPEN, TST_EXP_EQ_LI, SAFE_CLOSE, SAFE_UNLINK; types/structs: struct tst_test; functions: verify_fcntl; local macros/constants: TEST_NAME.

Control flow: exercise path: verify_fcntl.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `lapi/fcntl.h`, `tst_test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: key constants: F_CREATED_QUERY, O_CREAT, O_CLOEXEC, O_RDONLY; harness metadata: .test_all, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl_common.h

Purpose: Shared helpers and constants for fcntl OFD-lock concurrency tests, including file names, buffer sizes, and common record geometry. Source notes: F_OFD_* commands always require flock64 struct. Older GLibc (pre 2.29) would pass the flock sturct directly to the kernel even if it had 32-bit offsets. If we are on 32-bit abi we need to use the fcntl64 compat syscall. See: glibc: 06ab719d30 Fix Linux fcntl OFD locks for non-LFS architectures (BZ#20251) kernel: fs/fcntl.c FCNTL_COMMON_H__ The file was read in full for this report (75 lines, 1661 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_FCNTL; types/structs: struct my_flock64, struct flock; functions: fcntl_compat; local macros/constants: FCNTL_COMMON_H__, FCNTL_COMPAT.

Control flow: the file provides declarations/helpers consumed by sibling tests.

State and persistence behavior: The test manipulates advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `inttypes.h`, `tst_test.h`, `tst_kernel.h`, `lapi/syscalls.h`, `lapi/abisize.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: key constants: F_OFD_, __NR_fcntl64.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/Makefile

Purpose: Build integration for the LTP `fdatasync` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 237 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync01.c

Purpose: Validates successful `fdatasync()` on a writable temporary file and loops through cases under the LTP harness. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. You should have received a copy of the GNU General Public License along with this program; if not, write the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA. ******************************************************** TEST IDENTIFIER : fdatasync01 EXECUTED BY : Any user TEST TITLE : Basic test for fdatasync(2) TEST CASE TOTAL : 1 AUTHOR : Madhu T L <madhu.tarikere@wipro.com> SIGNALS Uses SIGUSR1 to pause before test if option set. (See the p... The file was read in full for this report (155 lines, 4115 bytes).

Important APIs/types/functions: calls/wrappers: fdatasync(), open(), close(), write(); functions: main, setup, cleanup.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `test.h`; integrates with the LTP fdatasync syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXECUTED; key constants: SIGNALS, SIGUSR1, O_CREAT, O_WRONLY, O_CREATE.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync02.c

Purpose: Validates `fdatasync()` errno handling for invalid descriptors, read-only descriptors, pipes, and special descriptor states. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. You should have received a copy of the GNU General Public License along with this program; if not, write the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA. ******************************************************** TEST IDENTIFIER : fdatasync02 EXECUTED BY : Any user TEST TITLE : Checking error conditions for fdatasync(2) TEST CASE TOTAL : 2 AUTHOR : Madhu T L <madhu.tarikere@wipro.com> SIGNALS Uses SIGUSR1 to pause before test if option... The file was read in full for this report (197 lines, 4908 bytes).

Important APIs/types/functions: calls/wrappers: fdatasync(), open(), SAFE_CLOSE; types/structs: struct test_case_t; functions: main, setup1, setup2, cleanup2, setup, cleanup; local macros/constants: EXP_RET_VAL, SPL_FILE.

Control flow: setup path: setup1, setup2, setup; exercise path: main; cleanup path: cleanup2, cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `pwd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `test.h`, `tso_safe_macros.h`; integrates with the LTP fdatasync syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXECUTED, EBADF, EINVAL, EXP_RET_VAL; key constants: SIGNALS, SIGUSR1, O_RDONLY; harness metadata: .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync03.c

Purpose: Checks `fdatasync()` on a write-only file descriptor and reports success or expected kernel/libc failure details. Source notes: Author: Sumit Garg <sumit.garg@linaro.org> fdatasync03 It basically tests fdatasync() to sync test file data having large dirty file pages to block device. Also, it tests all supported filesystems on a test block device. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (66 lines, 1393 bytes).

Important APIs/types/functions: calls/wrappers: fdatasync(), SAFE_OPEN, SAFE_CLOSE; types/structs: struct tst_test; functions: verify_fdatasync; local macros/constants: MNTPOINT, FNAME, FILE_SIZE_MB, FILE_SIZE, MODE.

Control flow: exercise path: verify_fdatasync.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`; integrates with the LTP fdatasync syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .needs_root, .test_all.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/Makefile

Purpose: Build integration for the LTP `fgetxattr` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 236 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr01.c

Purpose: Sets an extended attribute and verifies `fgetxattr()` returns the expected value through an open descriptor. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Basic tests for fgetxattr(2) and make sure fgetxattr(2) handles error conditions correctly. There are 3 test cases: 1. Get an non-existing attribute: - fgetxattr(2) should return -1 and set errno to ENODATA 2. Buffer size is smaller than attribute value size: - fgetxattr(2) should return -1 and set errno to ERANGE 3. Get attribute, fgetxattr(2) should succeed: - verify the attribute got by fgetxattr(2) is same as the value we set case 00, get non-existing attribute case 01, small value buffer case 02, get existing attribute SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (150 lines, 3380 bytes).

Important APIs/types/functions: calls/wrappers: fgetxattr(), SAFE_TOUCH, SAFE_OPEN, SAFE_MALLOC, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct test_case, struct tst_test; functions: verify_fgetxattr, setup, cleanup; local macros/constants: XATTR_SIZE_MAX, XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, XATTR_TEST_INVALID_KEY, MNTPOINT, FNAME.

Control flow: setup path: setup; exercise path: verify_fgetxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fgetxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENODATA, ERANGE, EOPNOTSUPP; key constants: O_RDONLY; harness metadata: .timeout, .setup, .test, .cleanup, .tcnt, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr02.c

Purpose: Table-driven negative `fgetxattr()` coverage for invalid descriptors, missing attributes, undersized buffers, and bad addresses. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> In the user.* namespace, only regular files and directories can have extended attributes. Otherwise fgetxattr(2) will return -1 and set proper errno. There are 7 test cases: 1. Get attribute from a regular file: - fgetxattr(2) should succeed - checks returned value to be the same as we set 2. Get attribute from a directory: - fgetxattr(2) should succeed - checks returned value to be the same as we set 3. Get attribute from a symlink which points to the regular file: - fgetxattr(2) should succeed - checks returned value to be the same as we set 4. Get attribute from a FIFO: - fgetxattr(2) should return -1 and set errno to ENODATA 5. Get attribute from a char special file: - fgetxattr(2) should return -1 and set errno to ENODATA 6. Get attribute from a block special file: - fgetxattr... The file was read in full for this report (273 lines, 6855 bytes).

Important APIs/types/functions: calls/wrappers: fgetxattr(), open(), getxattr(), SAFE_TOUCH, SAFE_MKDIR, SAFE_SYMLINK, SAFE_MKNOD, SAFE_MALLOC, SAFE_SOCKET, SAFE_BIND, SAFE_OPEN, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct test_case, struct sockaddr_un, struct sockaddr, struct tst_test; functions: verify_fgetxattr, setup, cleanup; local macros/constants: XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, MNTPOINT, OFFSET, FILENAME, DIRNAME, SYMLINK, SYMLINKF, FIFO, CHR, BLK.

Control flow: setup path: setup; exercise path: verify_fgetxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/sysmacros.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/socket.h`, `sys/un.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fgetxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENODATA, EOPNOTSUPP; key constants: O_RDONLY, O_NONBLOCK; harness metadata: .setup, .test, .cleanup, .tcnt, .needs_devfs, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr03.c

Purpose: Regression coverage for `fgetxattr()` buffer-size probing and correct returned value length. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> An empty buffer of size zero can be passed into fgetxattr(2) to return the current size of the named extended attribute. HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (73 lines, 1548 bytes).

Important APIs/types/functions: calls/wrappers: fgetxattr(), SAFE_TOUCH, SAFE_OPEN, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct tst_test; functions: verify_fgetxattr, setup, cleanup; local macros/constants: XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, FILENAME.

Control flow: setup path: setup; exercise path: verify_fgetxattr; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fgetxattr syscall suite; uses the LTP C harness and result macros.

Risks: xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDONLY; harness metadata: .setup, .test_all, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/Makefile

Purpose: Build integration for the LTP `file_attr` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 236 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr01.c

Purpose: Validates getting and setting Linux file attribute flags on a regular file. Source notes: \ Verify that `file_getattr` and `file_setattr` syscalls are raising the correct errors according to the invalid input arguments. In particular: - EBADFD: Invalid file descriptor. - ENOENT: File doesn't exist - EFAULT: File name is NULL - EFAULT: File attributes is NULL - EINVAL: File attributes size is zero - E2BIG: File attributes size is too big - EINVAL: Invalid AT flags SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (189 lines, 4167 bytes).

Important APIs/types/functions: calls/wrappers: TST_EXP_FAIL, SAFE_OPEN, SAFE_CHDIR, SAFE_TOUCH, SAFE_SYSCONF, SAFE_CLOSE; types/structs: struct file_attr, struct tcase, struct tst_test, struct tst_buffers; functions: run, setup, cleanup; local macros/constants: MNTPOINT, FILENAME, NO_FILENAME.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: runs across syscall ABI variants, iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `string.h`, `tst_test.h`, `tst_kconfig.h`, `lapi/fs.h`, `lapi/fcntl.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options; bad-address tests are ABI-sensitive.

Test signals: explicit failure reporting; errno checks: EBADFD, ENOENT, EFAULT, EINVAL, E2BIG, EBADF, EOPNOTSUPP; key constants: O_RDONLY; harness metadata: .test, .setup, .cleanup, .tcnt, .needs_root, .test_variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr02.c

Purpose: Checks file attribute ioctl error handling for invalid descriptors and unsuitable file types. Source notes: \ Verify that `file_getattr` is correctly reading filesystems additional attributes. We are running test on XFS only, since it's the only filesystem currently implementing the features we need. this will force at least one extent to be allocated SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (109 lines, 2478 bytes).

Important APIs/types/functions: calls/wrappers: mount(), TST_EXP_PASS, TST_EXP_EQ_LI, SAFE_MKDIR, SAFE_STAT, SAFE_OPEN, SAFE_CREAT, SAFE_IOCTL, SAFE_WRITE, SAFE_CLOSE, SAFE_UMOUNT; types/structs: struct fsxattr, struct file_attr, struct stat, struct tst_test, struct tst_fs, struct tst_buffers; functions: run, setup, cleanup; local macros/constants: MNTPOINT, FILENAME, BLOCKS, PROJID.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/mount.h`, `tst_test.h`, `lapi/fs.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; errno checks: EOPNOTSUPP; key constants: O_RDONLY, FS_IOC_FSGETXATTR, FS_XFLAG_EXTSIZE, FS_XFLAG_COWEXTSIZE, FS_IOC_FSSETXATTR; harness metadata: .test_all, .setup, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr03.c

Purpose: Tests immutable/append-only style file flags and their effects on write/unlink/truncate behavior. Source notes: \ Verify that `file_setattr` is correctly setting filesystems additional attributes. We are running test on XFS only, since it's the only filesystem currently implementing the features we need. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (76 lines, 1770 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_CREAT, TST_EXP_PASS, SAFE_IOCTL, SAFE_CLOSE, TST_EXP_EQ_LI, SAFE_UNLINK; types/structs: struct fsxattr, struct file_attr, struct tst_test, struct tst_fs, struct tst_buffers; functions: run, setup, cleanup; local macros/constants: MNTPOINT, FILEPATH, BLOCKS, PROJID.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fs.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; key constants: AT_FDCWD, FS_IOC_FSGETXATTR, FS_XFLAG_EXTSIZE, FS_XFLAG_COWEXTSIZE; harness metadata: .test_all, .setup, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr04.c

Purpose: Directory-focused file attribute coverage, including flags that affect directory mutation semantics. Source notes: \ Verify that `file_getattr` and `file_setattr` are correctly raising an error when the wrong file descriptors types are passed to them. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (62 lines, 1203 bytes).

Important APIs/types/functions: calls/wrappers: TST_EXP_FAIL, TST_FD_FOREACH, SAFE_TOUCH; types/structs: struct file_attr, struct tst_fd, struct tst_test, struct tst_buffers; functions: test_invalid_fd, run, setup; local macros/constants: FILENAME.

Control flow: setup path: setup; exercise path: test_invalid_fd, run; notable execution mechanics: runs across syscall ABI variants.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fs.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit failure reporting; errno checks: ENOTDIR; harness metadata: .test_all, .setup, .test_variants, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr05.c

Purpose: Privilege and capability-sensitive file attribute test for flags that require elevated rights or filesystem support. Source notes: \ Verify that `file_setattr` is correctly raising EOPNOTSUPP when filesystem doesn't support FSX operations. EINVAL is raised before EOPNOTSUPP vfat is not implementing file_[set|get]attr SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (63 lines, 1419 bytes).

Important APIs/types/functions: calls/wrappers: TST_EXP_FAIL, SAFE_TOUCH, SAFE_STAT; types/structs: struct file_attr, struct stat, struct tst_test, struct tst_buffers, struct tst_tag; functions: run, setup; local macros/constants: MNTPOINT, FILEPATH, BLOCKS, PROJID.

Control flow: setup path: setup; exercise path: run.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fs.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior.

Test signals: explicit failure reporting; errno checks: EOPNOTSUPP, EINVAL; key constants: AT_FDCWD, FS_XFLAG_EXTSIZE, FS_XFLAG_COWEXTSIZE; harness metadata: .test_all, .setup, .needs_root, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/Makefile

Purpose: Build integration for the LTP `finit_module` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `obj-m := finit_module.o; include $(top_srcdir)/include/mk/testcases.mk; REQ_VERSION_MAJOR	:= 3; REQ_VERSION_PATCH	:= 8; MAKE_TARGETS		:= finit_module01 finit_module02 finit_module.ko; include $(top_srcdir)/include/mk/module.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (21 lines, 395 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module.c

Purpose: Tiny kernel module fixture whose init/exit paths allow `finit_module` syscall tests to load a known module object. Source notes: Dummy test module. The module accepts a single argument named "status" and it fails initialization if the status is set to "invalid". SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (39 lines, 780 bytes).

Important APIs/types/functions: types/structs: struct proc_dir_entry; functions: dummy_init, dummy_exit; local macros/constants: DIRNAME.

Control flow: setup path: dummy_init; cleanup path: dummy_exit.

State and persistence behavior: The test manipulates kernel module load/unload state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `linux/module.h`, `linux/init.h`, `linux/proc_fs.h`, `linux/kernel.h`; integrates with the LTP finit_module syscall suite.

Risks: kernel config, module signing, and privilege policy affect results.

Test signals: errno checks: EINVAL.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module01.c

Purpose: Positive `finit_module()` path: opens the fixture `.ko`, loads it, and verifies module insertion/removal integration. Source notes: \ Basic finit_module() tests. [Algorithm] Inserts a simple module after opening and mmaping the module file. lockdown and SecureBoot requires signed modules SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (62 lines, 1117 bytes).

Important APIs/types/functions: calls/wrappers: finit_module(), SAFE_OPEN, TST_EXP_FAIL, TST_EXP_PASS, SAFE_CLOSE; types/structs: struct tst_test; functions: setup, run, cleanup; local macros/constants: MODULE_NAME.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, shared or anonymous memory mappings, UID/capability-sensitive kernel state, kernel module load/unload state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `errno.h`, `lapi/init_module.h`, `tst_module.h`; integrates with the LTP finit_module syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; kernel config, module signing, and privilege policy affect results.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EKEYREJECTED; key constants: O_RDONLY, O_CLOEXEC; harness metadata: .test_all, .setup, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module02.c

Purpose: Negative `finit_module()` path checking invalid fd, invalid params, malformed module contents, and permission-related errors. Source notes: \ Basic finit_module() failure tests. [Algorithm] Tests various failure scenarios for finit_module(). Insert module twice SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (155 lines, 3813 bytes).

Important APIs/types/functions: calls/wrappers: finit_module(), TST_CAP, SAFE_MKDIR, SAFE_OPEN, SAFE_CLOSE, TST_EXP_FAIL; types/structs: struct tst_cap, struct tcase, struct tst_test, struct tst_tag; functions: bad_fd_setup, dir_setup, setup, cleanup, run; local macros/constants: MODULE_NAME, TEST_DIR.

Control flow: setup path: bad_fd_setup, dir_setup, setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, kernel module load/unload state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `linux/capability.h`, `stdlib.h`, `errno.h`, `lapi/init_module.h`, `tst_module.h`, `tst_capability.h`; integrates with the LTP finit_module syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; kernel config, module signing, and privilege policy affect results; bad-address tests are ABI-sensitive.

Test signals: explicit failure reporting; errno checks: ENOEXEC, EBADF, EISDIR, EINVAL, EFAULT, EPERM, EEXIST, EKEYREJECTED, ETXTBSY; key constants: O_RDONLY, O_CLOEXEC, O_WRONLY, O_RDWR, O_DIRECTORY; harness metadata: .tags, .test, .tcnt, .setup, .cleanup, .needs_tmpdir, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/Makefile

Purpose: Build integration for the LTP `flistxattr` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (9 lines, 296 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr01.c

Purpose: Sets xattrs and verifies `flistxattr()` returns the expected attribute name list through a descriptor. Source notes: Author: Dejan Jovicevic <dejan.jovicevic@rt-rk.com> Test Name: verify_flistxattr01 Description: The testcase checks the basic functionality of the flistxattr(2). flistxattr(2) retrieves the list of extended attribute names associated with the file itself in the filesystem. HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (90 lines, 1768 bytes).

Important APIs/types/functions: calls/wrappers: flistxattr(), SAFE_OPEN, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct tst_test; functions: has_attribute, verify_flistxattr, setup, cleanup; local macros/constants: SECURITY_KEY1, VALUE, VALUE_SIZE, KEY_SIZE.

Control flow: setup path: setup; exercise path: verify_flistxattr; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `errno.h`, `sys/types.h`, `string.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP flistxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT; harness metadata: .needs_tmpdir, .needs_root, .test_all, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr02.c

Purpose: Negative `flistxattr()` coverage for invalid descriptors and bad/undersized buffers. Source notes: Author: Dejan Jovicevic <dejan.jovicevic@rt-rk.com> Test Name: flistxattr02 Description: 1) flistxattr(2) fails if the size of the list buffer is too small to hold the result. 2) flistxattr(2) fails if fd is an invalid file descriptor. Expected Result: 1) flistxattr(2) should return -1 and set errno to ERANGE. 2) flistxattr(2) should return -1 and set errno to EBADF. HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (95 lines, 1899 bytes).

Important APIs/types/functions: calls/wrappers: flistxattr(), SAFE_OPEN, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct test_case, struct tst_test; functions: verify_flistxattr, setup, cleanup; local macros/constants: SECURITY_KEY, VALUE, VALUE_SIZE.

Control flow: setup path: setup; exercise path: verify_flistxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `errno.h`, `sys/types.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP flistxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ERANGE, EBADF; key constants: O_RDWR, O_CREAT; harness metadata: .needs_tmpdir, .needs_root, .test, .tcnt, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr03.c

Purpose: Validates `flistxattr()` size-query behavior and output length consistency. Source notes: Author: Dejan Jovicevic <dejan.jovicevic@rt-rk.com> Test Name: flistxattr03 Description: flistxattr is identical to listxattr. an empty buffer of size zero can return the current size of the list of extended attribute names, which can be used to estimate a suitable buffer. HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (84 lines, 1735 bytes).

Important APIs/types/functions: calls/wrappers: flistxattr(), SAFE_OPEN, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct tst_test; functions: check_suitable_buf, verify_flistxattr, setup, cleanup; local macros/constants: SECURITY_KEY, VALUE, VALUE_SIZE.

Control flow: setup path: setup; exercise path: verify_flistxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `errno.h`, `sys/types.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP flistxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT; harness metadata: .needs_tmpdir, .needs_root, .test, .tcnt, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/Makefile

Purpose: Build integration for the LTP `flock` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 237 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock01.c

Purpose: Basic `flock()` success test for exclusive and shared advisory locks on a temporary file. Source notes: Author: Vatsal Avasthi \ Basic test for flock(2), uses LOCK_SH, LOCK_UN, LOCK_EX locks. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (58 lines, 1072 bytes).

Important APIs/types/functions: calls/wrappers: flock(), SAFE_OPEN, SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: verify_flock, setup, cleanup.

Control flow: setup path: setup; exercise path: verify_flock; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/file.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: LOCK_SH, LOCK_UN, LOCK_EX, O_CREAT, O_TRUNC, O_RDWR; harness metadata: .tcnt, .test, .needs_tmpdir, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock02.c

Purpose: Checks nonblocking `flock()` conflict behavior and expected `EWOULDBLOCK`/`EAGAIN` style failures. Source notes: Author: Vatsal Avasthi \ Verify flock(2) returns -1 and set proper errno: - EBADF if the file descriptor is invalid - EINVAL if the argument operation does not include LOCK_SH,LOCK_EX,LOCK_UN - EINVAL if an invalid combination of locking modes is used i.e LOCK_SH with LOCK_EX - EWOULDBLOCK if the file is locked and the LOCK_NB flag was selected SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (80 lines, 1746 bytes).

Important APIs/types/functions: calls/wrappers: flock(), SAFE_OPEN, SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: verify_flock, setup.

Control flow: setup path: setup; exercise path: verify_flock; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/file.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, EINVAL, EWOULDBLOCK; key constants: LOCK_SH, LOCK_EX, LOCK_UN, LOCK_NB, O_RDWR, O_CREAT, O_TRUNC; harness metadata: .tcnt, .test, .needs_tmpdir, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock03.c

Purpose: Fork-based `flock()` inheritance and mutual exclusion coverage between parent and child descriptors. Source notes: \ Verify that flock(2) cannot unlock a file locked by another task. Fork a child processes. The parent flocks a file with LOCK_EX. Child waits for that to happen, then checks to make sure it is locked. Child then tries to unlock the file. If the unlock succeeds, the child attempts to lock the file with LOCK_EX. The test passes if the child is able to lock the file. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (97 lines, 2102 bytes).

Important APIs/types/functions: calls/wrappers: flock(), TST_CHECKPOINT_WAIT, SAFE_OPEN, SAFE_CLOSE, SAFE_FORK, TST_CHECKPOINT_WAKE; types/structs: struct tst_test; functions: childfunc, verify_flock, setup.

Control flow: setup path: setup; exercise path: childfunc, verify_flock; notable execution mechanics: forks child processes for concurrency or privilege separation, uses LTP checkpoints to order parent/child actions.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `stdlib.h`, `sys/file.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: LOCK_EX, O_RDWR, LOCK_NB, LOCK_UN, O_CREAT, O_TRUNC; harness metadata: .test_all, .needs_checkpoints, .forks_child, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock04.c

Purpose: Validates `flock()` unlock and descriptor-close behavior across repeated lock transitions. Source notes: Author: Vatsal Avasthi \ Test verifies that flock() behavior with different locking combinations along with LOCK_SH and LOCK_EX: - flock() succeeded in acquiring shared lock on shared lock file. - flock() failed to acquire exclusive lock on shared lock file. - flock() failed to acquire shared lock on exclusive lock file. - flock() failed to acquire exclusive lock on exclusive lock file. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (95 lines, 2056 bytes).

Important APIs/types/functions: calls/wrappers: flock(), SAFE_OPEN, SAFE_CLOSE, SAFE_FORK; types/structs: struct tcase, struct tst_test; functions: child, verify_flock, setup.

Control flow: setup path: setup; exercise path: child, verify_flock; notable execution mechanics: iterates a case table, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/file.h`, `stdlib.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: LOCK_SH, LOCK_EX, O_RDWR, LOCK_NB, O_CREAT, O_TRUNC; harness metadata: .tcnt, .test, .needs_tmpdir, .setup, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock06.c

Purpose: Regression test for flock behavior across fork/exec or duplicated descriptor style scenarios. Source notes: Author: Matthew Wilcox \ Test verifies that flock locks held on one file descriptor conflict with flock locks held on a different file descriptor. The process opens two file descriptors on the same file. It acquires an exclusive flock on the first descriptor, checks that attempting to acquire an flock on the second descriptor fails. Then it removes the first descriptor's lock and attempts to acquire an exclusive lock on the second descriptor. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (69 lines, 1775 bytes).

Important APIs/types/functions: calls/wrappers: flock(), SAFE_OPEN, SAFE_CLOSE; types/structs: struct tst_test; functions: verify_flock, setup.

Control flow: setup path: setup; exercise path: verify_flock.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/file.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, LOCK_EX, LOCK_NB, LOCK_UN, O_CREAT, O_TRUNC; harness metadata: .test_all, .needs_tmpdir, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock07.c

Purpose: Checks `flock()` interactions with open modes and descriptor lifecycle edge cases. Source notes: Author: Yang Xu <xuyang2018.jy@fujitsu.com> \ Verify that flock(2) fails with errno EINTR when waiting to acquire a lock, and the call is interrupted by a signal. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (77 lines, 1428 bytes).

Important APIs/types/functions: calls/wrappers: flock(), SAFE_TOUCH, SAFE_OPEN, SAFE_CLOSE, SAFE_SIGEMPTYSET, SAFE_SIGACTION, TST_EXP_FAIL, TST_EXP_PASS, SAFE_FORK, SAFE_KILL, SAFE_WAITPID; types/structs: struct sigaction, struct tst_test; functions: handler, setup, cleanup, child_do, verify_flock; local macros/constants: TEMPFILE.

Control flow: setup path: setup; exercise path: child_do, verify_flock; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, UID/capability-sensitive kernel state, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/file.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINTR; key constants: O_RDWR, SIGUSR1, LOCK_EX; harness metadata: .setup, .cleanup, .test_all, .needs_tmpdir, .needs_root, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fmtmsg/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fmtmsg/Makefile

Purpose: Build integration for the LTP `fmtmsg` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 237 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fmtmsg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fmtmsg/fmtmsg01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fmtmsg/fmtmsg01.c

Purpose: Table-driven libc `fmtmsg()` validation over classification, severity, label/action/tag, environment variables, and return code combinations. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA 01/02/2003 Port to LTP avenkat@us.ibm.com 06/30/2001 Port to Linux nsharoff@us.ibm.com fmtmsg(3C) and addseverity(3C) ALGORITHM Check basic functionality using various mes... The file was read in full for this report (252 lines, 6086 bytes).

Important APIs/types/functions: calls/wrappers: fmtmsg(), close(); functions: clearbuf, main, anyfail, setup, blenter, blexit; local macros/constants: FAILED, PASSED.

Control flow: setup path: setup; exercise path: main; cleanup path: blexit.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `ctype.h`, `stdio.h`, `fmtmsg.h`, `string.h`, `stdlib.h`, `unistd.h`, `errno.h`, `test.h`; integrates with the LTP fmtmsg syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: MM_PRINT, MM_SOFT, MM_INFO, MM_NOTOK, MM_OK, MM_HARD, MM_OPSYS, MM_CONSOLE.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fmtmsg/fmtmsg01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/Makefile

Purpose: Build integration for the LTP `fork` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 237 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork01.c

Purpose: Basic fork test confirming parent receives child pid, child exits through the expected path, and wait observes the child. Source notes: Author: Kathy Olmsted Co-Pilot: Steve Shaw \ This test verifies that fork returns without error and that it returns the pid of the child. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (75 lines, 1491 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_FORK, SAFE_FILE_PRINTF, SAFE_WAITPID, SAFE_FILE_SCANF, TST_EXP_EQ_LI, SAFE_CREAT, SAFE_CLOSE; types/structs: struct tst_test; functions: verify_fork, setup, cleanup; local macros/constants: KIDEXIT, FILENAME.

Control flow: setup path: setup; exercise path: verify_fork; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, kernel tunables that setup/cleanup must restore, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `string.h`, `stdlib.h`, `sys/types.h`, `sys/wait.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; harness metadata: .setup, .cleanup, .needs_tmpdir, .forks_child, .test_all.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork03.c

Purpose: Fork error or accounting coverage focused on repeated process creation under LTP controls. Source notes: Author: 2001 Ported by Wayne Boyer \ Check that child process can use a large text space and do a large number of operations. In this situation, check for pid == 0 in child and check for pid > 0 in parent after wait. child uses some cpu time slices SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (57 lines, 1212 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_FORK, SAFE_WAIT; types/structs: struct tst_test; functions: verify_fork.

Control flow: exercise path: verify_fork; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `unistd.h`, `sys/wait.h`, `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; harness metadata: .test_all, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork04.c

Purpose: Verifies parent/child memory or variable state separation after fork. Source notes: \ This test verifies that parent process shares environ variables with the child and that child doesn't change parent's environ variables. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (94 lines, 2015 bytes).

Important APIs/types/functions: calls/wrappers: TST_EXP_EXPR, TST_CHECKPOINT_WAKE_AND_WAIT, SAFE_SETENV, TST_CHECKPOINT_WAKE, SAFE_FORK, TST_CHECKPOINT_WAIT; types/structs: struct tst_test; functions: run_child, run; local macros/constants: ENV_KEY, ENV_VAL0, ENV_VAL1.

Control flow: exercise path: run_child, run; notable execution mechanics: forks child processes for concurrency or privilege separation, uses LTP checkpoints to order parent/child actions.

State and persistence behavior: The test manipulates child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit failure reporting; errno checks: ENV_KEY, ENV_VAL0, ENV_VAL1; harness metadata: .test_all, .forks_child, .needs_checkpoints.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork05.c

Purpose: Checks fork behavior with signal handling or child exit status propagation. Source notes: Author: Ulrich Drepper / Nate Straz , Red Hat \ This test verifies that LDT is propagated correctly from parent process to the child process. On Friday, May 2, 2003 at 09:47:00AM MST, Ulrich Drepper wrote: Robert Williamson wrote: I'm getting a SIGSEGV with one of our tests, fork05.c, that apparently you wrote (attached below). The test passes on my 2.5.68 machine running SuSE 8.0 (glibc 2.2.5 and Linuxthreads), however it segmentation faults on RedHat 9 running 2.5.68. The test seems to "break" when it attempts to run the assembly code....could you take a look at it? There is no need to look at it, I know it cannot work anymore on recent systems. Either change all uses of %gs to %fs or skip the entire patch if %gs has a nonzero value. On Sat, Aug 12, 2000 at 12:47:31PM -0700, Ulrich Drepper wrote: Ever since the %gs handling was fixed... The file was read in full for this report (117 lines, 3205 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_MODIFY_LDT, SAFE_FORK, TST_EXP_EQ_LI, SAFE_WAITPID, TST_TEST_TCONF; types/structs: struct user_desc, struct tst_test; functions: run.

Control flow: exercise path: run; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/ldt.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: SIGSEGV; harness metadata: .test_all, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork07.c

Purpose: Regression coverage for fork limits or repeated fork/wait loops. Source notes: 07/2001 Ported by Wayne Boyer 07/2002 Limited forking and split "infinite forks" testcase to fork12.c by Nate Straz \ Check that all children inherit parent's file descriptor. Parent opens a file and forks children. Each child reads a byte and checks that the value is correct. Parent checks that correct number of bytes was consumed from the file. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (70 lines, 1413 bytes).

Important APIs/types/functions: calls/wrappers: read(), SAFE_OPEN, SAFE_FORK, SAFE_READ, SAFE_CLOSE; types/structs: struct tst_test; functions: run, setup, cleanup; local macros/constants: NFORKS, TESTFILE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDONLY; harness metadata: .forks_child, .needs_tmpdir, .cleanup, .setup, .test_all.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork08.c

Purpose: Validates descriptor or file-offset inheritance semantics after fork. Source notes: 07/2001 Ported by Wayne Boyer \ Check that the parent's file descriptors will not be affected by being closed in the child. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (68 lines, 1185 bytes).

Important APIs/types/functions: calls/wrappers: read(), SAFE_OPEN, SAFE_FORK, SAFE_CLOSE, SAFE_READ; types/structs: struct tst_test; functions: run, setup, cleanup; local macros/constants: TESTFILE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDONLY; harness metadata: .forks_child, .needs_tmpdir, .cleanup, .setup, .test_all.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork09.c

Purpose: Checks fork behavior around signals, scheduling, or process-group interactions. Source notes: 07/2001 Ported by Wayne Boyer 10/2008 Suzuki K P <suzuki@in.ibm.com> \ Verify that a forked child can close all the files which have been open by the parent process, after closing and re-opening. raised if we reached OPEN_MAX SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (99 lines, 2017 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_FORK, SAFE_FCLOSE, SAFE_FOPEN, SAFE_UNLINK, SAFE_MALLOC; types/structs: struct tst_test; functions: run, setup, cleanup; local macros/constants: FILE_PREFIX.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `tst_safe_stdio.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; errno checks: EMFILE; key constants: PATH_MAX; harness metadata: .test_all, .setup, .cleanup, .forks_child, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork10.c

Purpose: Stresses repeated fork/wait cycles and validates no unexpected child failures. Source notes: 07/2001 Ported by Wayne Boyer \ This test verifies inheritance of file descriptors from parent to child process. We open a file from parent, then we check if file offset changes accordingly with file descriptor usage. [Algorithm] Test steps are the following: - create a file made in three parts -> | aa..a | bb..b | cc..c | - from parent, open the file - from child, move file offset after the first part - from parent, read second part and check if it's | bb..b | - from child, read third part and check if it's | cc..c | Test passes if we were able to read the correct file parts from parent and child. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (99 lines, 2113 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_OPEN, SAFE_FORK, SAFE_LSEEK, SAFE_WAIT, SAFE_READ, TST_EXP_EXPR, SAFE_CLOSE, SAFE_CREAT, SAFE_WRITE; types/structs: struct tst_test; functions: run, setup, cleanup; local macros/constants: FILENAME, DATASIZE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: harness metadata: .forks_child, .needs_tmpdir, .test_all, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork13.c

Purpose: Validates fork under resource limit or memory pressure setup and expected failure/success reporting. Source notes: \ A race in pid generation that causes pids to be reused immediately From the mainline commit 5fdee8c4a5e1 ("pids: fix a race in pid generation that causes pids to be reused immediately") A program that repeatedly forks and waits is susceptible to having the same pid repeated, especially when it competes with another instance of the same program. This is really bad for bash implementation. Furthermore, many shell scripts assume that pid numbers will not be used for some length of time. [Race Description] :: A B // pid == offset == n // pid == offset == n + 1 test_and_set_bit(offset, map->page) test_and_set_bit(offset, map->page); pid_ns->last_pid = pid; pid_ns->last_pid = pid; // pid == n + 1 is freed (wait()) // Next fork()... last = pid_ns->last_pid; // == n pid = last + 1; The distance mod PIDMAX between two pids, where the first pi... The file was read in full for this report (121 lines, 3044 bytes).

Important APIs/types/functions: calls/wrappers: fork(), wait(), SAFE_FORK, SAFE_WAITPID; types/structs: struct tst_test, struct tst_path_val, struct tst_tag; functions: pid_distance, check; local macros/constants: PID_MAX, PID_MAX_STR, RETURN, MAX_ITERATIONS.

Control flow: the file provides declarations/helpers consumed by sibling tests; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, UID/capability-sensitive kernel state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `fcntl.h`, `errno.h`, `unistd.h`, `stdio.h`, `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: PATH_KERN_PID_MAX; harness metadata: .needs_root, .forks_child, .test_all, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork14.c

Purpose: Additional fork regression coverage for high process counts or VM/resource inheritance. Source notes: \ This test is a reproducer for kernel 3.5: 7edc8b0ac16c ("mm/fork: fix overflow in vma length when copying mmap on clone") Since VMA length in dup_mmap() is calculated and stored in a unsigned int, it will overflow when length of mmaped memory > 16 TB. When overflow occurs, fork will incorrectly succeed. The patch above fixed it. keep track of the failed fork() and verify that next one is failing as well. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (122 lines, 2343 bytes).

Important APIs/types/functions: calls/wrappers: fork(), mmap(), SAFE_MUNMAP, SAFE_MALLOC; types/structs: struct tst_test, struct tst_tag; functions: run, setup, cleanup; local macros/constants: LARGE, EXTENT.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates child processes and wait status, shared or anonymous memory mappings. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `stdlib.h`, `sys/wait.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXTENT, ECHILD; harness metadata: .test_all, .setup, .cleanup, .forks_child, .needs_abi_bits, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork_procs.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork_procs.c

Purpose: Standalone helper used by fork tests to spawn a requested number of child processes and hold/release them predictably. Source notes: \ This test spawns multiple processes using fork() and it checks if wait() returns the right PID once they end up. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (53 lines, 1040 bytes).

Important APIs/types/functions: calls/wrappers: fork(), wait(), SAFE_FORK, SAFE_WAIT, TST_EXP_EXPR; types/structs: struct tst_test, struct tst_option; functions: run, setup.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: harness metadata: .test_all, .setup, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork_procs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fpathconf/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fpathconf/Makefile

Purpose: Build integration for the LTP `fpathconf` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 237 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fpathconf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fpathconf/fpathconf01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fpathconf/fpathconf01.c

Purpose: Calls `fpathconf()` for supported `_PC_*` names on an open descriptor and checks returned values/errors. Source notes: \ Check the basic functionality of the fpathconf(2) system call. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (54 lines, 1095 bytes).

Important APIs/types/functions: calls/wrappers: fpathconf(), TST_EXP_POSITIVE, SAFE_OPEN, SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: verify_fpathconf, setup, cleanup.

Control flow: setup path: setup; exercise path: verify_fpathconf; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`; integrates with the LTP fpathconf syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: key constants: O_RDWR, O_CREAT; harness metadata: .needs_tmpdir, .test, .tcnt, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fpathconf/fpathconf01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/Makefile

Purpose: Build integration for the LTP `fremovexattr` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 236 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr01.c

Purpose: Sets and removes an xattr through `fremovexattr()`, then verifies it is gone. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Test Name: fremovexattr01 Description: Like removexattr(2), fremovexattr(2) also removes an extended attribute, identified by a name, from a file but, instead of using a filename path, it uses a descriptor. This test verifies that a simple call to fremovexattr(2) removes, indeed, a previously set attribute key/value from a file. HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (98 lines, 2186 bytes).

Important APIs/types/functions: calls/wrappers: fgetxattr(), fremovexattr(), removexattr(), SAFE_FSETXATTR, SAFE_CLOSE, SAFE_OPEN, TST_TEST_TCONF; types/structs: struct tst_test; functions: verify_fremovexattr, cleanup, setup; local macros/constants: ENOATTR, XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, MNTPOINT, FNAME.

Control flow: setup path: setup; exercise path: verify_fremovexattr; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `errno.h`, `stdlib.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fremovexattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENOATTR, ENODATA, EOPNOTSUPP; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .setup, .test_all, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr02.c

Purpose: Negative `fremovexattr()` coverage for invalid descriptors, missing xattrs, and bad names. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Test Name: fremovexattr02 Test cases:: 1) fremovexattr(2) fails if the named attribute does not exist. 2) fremovexattr(2) fails if file descriptor is not valid. 3) fremovexattr(2) fails if named attribute has an invalid address. Expected Results: fremovexattr(2) should return -1 and set errno to ENODATA. fremovexattr(2) should return -1 and set errno to EBADF. fremovexattr(2) should return -1 and set errno to EFAULT. case 1: attribute does not exist case 2: file descriptor is invalid case 3: bad name attribute HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (121 lines, 2487 bytes).

Important APIs/types/functions: calls/wrappers: fremovexattr(), SAFE_CLOSE, SAFE_OPEN, TST_TEST_TCONF; types/structs: struct test_case, struct tst_test; functions: verify_fremovexattr, cleanup, setup; local macros/constants: XATTR_TEST_KEY, MNTPOINT, FNAME.

Control flow: setup path: setup; exercise path: verify_fremovexattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `errno.h`, `fcntl.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fremovexattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options; bad-address tests are ABI-sensitive.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENODATA, EBADF, EFAULT, EOPNOTSUPP; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .setup, .test, .cleanup, .tcnt, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/Makefile

Purpose: Build integration for the LTP `fsconfig` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (6 lines, 175 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig01.c

Purpose: Positive/feature `fsconfig()` coverage using `fsopen()` contexts and parameter commands from the new mount API. Source notes: Basic fsconfig() test which tries to configure and mount the filesystem as well. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (94 lines, 2413 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fsmount(), fsopen(), SAFE_CLOSE, SAFE_UMOUNT; types/structs: struct tst_test; functions: cleanup, run; local macros/constants: MNTPOINT.

Control flow: exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fsconfig syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EOPNOTSUPP; key constants: AT_FDCWD; harness metadata: .timeout, .test_all, .setup, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig02.c

Purpose: Negative `fsconfig()` coverage for invalid command, bad fd, bad key/value, and kernel errno behavior. Source notes: Basic fsconfig() failure tests. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (97 lines, 3560 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fsopen(), SAFE_OPEN, SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: setup, cleanup, run.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fsconfig syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, EOPNOTSUPP; key constants: AT_FDCWD, O_RDWR, O_CREAT; harness metadata: .tcnt, .test, .setup, .cleanup, .needs_root, .needs_device.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig03.c

Purpose: Additional `fsconfig()` regression coverage for binary parameters, final creation/reconfiguration, or unsupported combinations. Source notes: \ Test for CVE-2022-0185. References links: - https://www.openwall.com/lists/oss-security/2022/01/25/14 - https://github.com/Crusaders-of-Rust/CVE-2022-0185 use same logic in kernel legacy_parse_param function Legacy fsconfig() just copies arguments to buffer SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (98 lines, 2144 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fsopen(), SAFE_CLOSE; types/structs: struct tst_test, struct tst_tag; functions: setup, run, cleanup; local macros/constants: MNTPOINT.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fsconfig syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL; harness metadata: .timeout, .test_all, .setup, .cleanup, .needs_root, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/Makefile

Purpose: Build integration for the LTP `fsetxattr` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 236 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr01.c

Purpose: Sets extended attributes through file descriptors and verifies create/replace semantics and stored values. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Basic tests for fsetxattr(2) and make sure fsetxattr(2) handles error conditions correctly. There are 9 test cases: 1. Any other flags being set except XATTR_CREATE and XATTR_REPLACE, fsetxattr(2) should return -1 and set errno to EINVAL 2. With XATTR_REPLACE flag set but the attribute does not exist, fsetxattr(2) should return -1 and set errno to ENODATA 3. Create new attr with name length greater than XATTR_NAME_MAX(255) fsetxattr(2) should return -1 and set errno to ERANGE 4. Create new attr whose value length is greater than XATTR_SIZE_MAX(65536) fsetxattr(2) should return -1 and set errno to E2BIG 5. Create new attr whose value length is zero, fsetxattr(2) should succeed 6. Replace the attr value without XATTR_REPLACE flag being set, fsetxattr(2) should return -1 and set errno... The file was read in full for this report (230 lines, 5682 bytes).

Important APIs/types/functions: calls/wrappers: fsetxattr(), SAFE_FSETXATTR, SAFE_FREMOVEXATTR, SAFE_CLOSE, SAFE_MALLOC, SAFE_TOUCH, SAFE_OPEN, TST_TEST_TCONF; types/structs: struct test_case, struct tst_test; functions: verify_fsetxattr, cleanup, setup; local macros/constants: XATTR_NAME_MAX, XATTR_NAME_LEN, XATTR_SIZE_MAX, XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, MNTPOINT, FNAME.

Control flow: setup path: setup; exercise path: verify_fsetxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fsetxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options; bad-address tests are ABI-sensitive.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, ENODATA, ERANGE, E2BIG, EEXIST, EFAULT, EOPNOTSUPP; key constants: O_RDONLY; harness metadata: .timeout, .setup, .test, .cleanup, .tcnt, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr02.c

Purpose: Negative `fsetxattr()` coverage for invalid descriptors, flags, namespace/name errors, bad address, and size constraints. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> \ Verify basic fsetxattr(2) syscall functionality: - Set attribute to a regular file, fsetxattr(2) should succeed. - Set attribute to a directory, fsetxattr(2) should succeed. - Set attribute to a symlink which points to the regular file, fsetxattr(2) should return -1 and set errno to EEXIST. - Set attribute to a FIFO, fsetxattr(2) should return -1 and set errno to EPERM. - Set attribute to a char special file, fsetxattr(2) should return -1 and set errno to EPERM. - Set attribute to a block special file, fsetxattr(2) should return -1 and set errno to EPERM. - Set attribute to a UNIX domain socket, fsetxattr(2) should return -1 and set errno to EPERM on kernels < 7.1.0. On kernel 7.1.0+ (dc0876b9846d "xattr: support extended attributes on sockets"), returns 0 (success) as sockets no... The file was read in full for this report (276 lines, 6827 bytes).

Important APIs/types/functions: calls/wrappers: fsetxattr(), open(), SAFE_FSETXATTR, SAFE_FREMOVEXATTR, SAFE_TOUCH, SAFE_MKDIR, SAFE_SYMLINK, SAFE_MKNOD, SAFE_OPEN, SAFE_SOCKET, SAFE_BIND, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct test_case, struct sockaddr_un, struct sockaddr, struct tst_test; functions: verify_fsetxattr, setup, cleanup; local macros/constants: XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, MNTPOINT, OFFSET, FILENAME, DIRNAME, SYMLINK, FIFO, CHR, BLK, SOCK.

Control flow: setup path: setup; exercise path: verify_fsetxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/sysmacros.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/socket.h`, `sys/un.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fsetxattr syscall suite; uses the LTP C harness and result macros; declares kernel configuration requirements.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EEXIST, EPERM, EOPNOTSUPP; key constants: O_RDONLY, O_NONBLOCK; harness metadata: .setup, .test, .cleanup, .tcnt, .needs_devfs, .needs_root, .needs_kconfigs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/Makefile

Purpose: Build integration for the LTP `fsmount` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 233 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount01.c

Purpose: Uses `fsopen`, `fsconfig`, and `fsmount` to build a detached mount and validate successful new mount API behavior. Source notes: Author: Zorro Lang <zlang@redhat.com> Basic fsmount() test. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (127 lines, 3346 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fsmount(), fsopen(), SAFE_CLOSE, TST_EXP_VAL, SAFE_UMOUNT; types/structs: struct tcase, struct tst_test; functions: run; local macros/constants: MNTPOINT, TCASE_ENTRY.

Control flow: exercise path: run; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`, `tst_safe_stdio.h`; integrates with the LTP fsmount syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; key constants: AT_FDCWD; harness metadata: .timeout, .tcnt, .test, .setup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount02.c

Purpose: Negative `fsmount()` coverage for bad descriptors, bad flags, invalid mount attributes, and errno contracts. Source notes: Basic fsmount() failure tests. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (81 lines, 1857 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fsmount(), fsopen(), SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: cleanup, setup, run; local macros/constants: MNTPOINT.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fsmount syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, EINVAL; harness metadata: .timeout, .tcnt, .test, .setup, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/Makefile

Purpose: Build integration for the LTP `fsopen` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (6 lines, 175 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/fsopen01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/fsopen01.c

Purpose: Checks successful `fsopen()` creation of filesystem configuration descriptors for supported filesystems. Source notes: Basic fsopen() test which tries to configure and mount the filesystem as well. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (81 lines, 1757 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fsmount(), fsopen(), SAFE_CLOSE, SAFE_UMOUNT; types/structs: struct tcase, struct tst_test; functions: run; local macros/constants: MNTPOINT, TCASE_ENTRY.

Control flow: exercise path: run; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fsopen syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; key constants: AT_FDCWD; harness metadata: .timeout, .tcnt, .test, .setup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/fsopen01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/fsopen02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/fsopen02.c

Purpose: Negative `fsopen()` coverage for invalid filesystem names, bad flags, and unsupported kernel behavior. Source notes: Basic fsopen() failure tests. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (58 lines, 1154 bytes).

Important APIs/types/functions: calls/wrappers: fsopen(), SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: setup, run.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fsopen syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENODEV, EINVAL; harness metadata: .tcnt, .test, .setup, .needs_root, .needs_device.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/fsopen02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fspick/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fspick/Makefile

Purpose: Build integration for the LTP `fspick` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (6 lines, 175 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fspick/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fspick/fspick01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fspick/fspick01.c

Purpose: Checks successful `fspick()` on existing paths/mount points and integrates with the new mount API descriptor flow. Source notes: Basic fspick() test. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (85 lines, 2119 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fspick(), TST_EXP_VAL, SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: run; local macros/constants: MNTPOINT, TCASE_ENTRY.

Control flow: exercise path: run; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`, `tst_safe_stdio.h`; integrates with the LTP fspick syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; key constants: AT_FDCWD; harness metadata: .timeout, .tcnt, .test, .setup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fspick/fspick01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fspick/fspick02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fspick/fspick02.c

Purpose: Negative `fspick()` coverage for invalid dirfd/path/flags and inaccessible mount targets. Source notes: Basic fspick() failure tests. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (55 lines, 1334 bytes).

Important APIs/types/functions: calls/wrappers: fspick(), SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: run; local macros/constants: MNTPOINT.

Control flow: exercise path: run; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fspick syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, ENOENT, EINVAL; key constants: AT_FDCWD; harness metadata: .timeout, .tcnt, .test, .setup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fspick/fspick02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstat/Makefile

Purpose: Build integration for the LTP `fstat` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (11 lines, 322 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat02.c

Purpose: Validates `fstat()` metadata fields for an open temporary file. Source notes: 07/2001 Ported by Wayne Boyer 05/2019 Ported to new library: Christian Amann <camann@suse.com> \ Tests if fstat() returns correctly and reports correct file information using the stat structure. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (62 lines, 1357 bytes).

Important APIs/types/functions: calls/wrappers: fstat(), TST_EXP_PASS, TST_EXP_EQ_LU, TST_EXP_EQ_LI, SAFE_OPEN, SAFE_LINK, SAFE_CLOSE; types/structs: struct stat, struct tst_test; functions: run, setup, cleanup; local macros/constants: TESTFILE, LINK_TESTFILE, FILE_SIZE, FILE_MODE, NLINK.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`; integrates with the LTP fstat syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; key constants: O_WRONLY, O_CREAT; harness metadata: .test_all, .setup, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat03.c

Purpose: Checks `fstat()` error handling for invalid descriptors and descriptor types. Source notes: 07/2001 Ported by Wayne Boyer 05/2019 Ported to new library: Christian Amann <camann@suse.com> Tests different error scenarios: 1) Calls fstat() with closed file descriptor -> EBADF 2) Calls fstat() with an invalid address for stat structure -> EFAULT (or receive signal SIGSEGV) SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (102 lines, 2079 bytes).

Important APIs/types/functions: calls/wrappers: fstat(), SAFE_FORK, SAFE_WAITPID, SAFE_OPEN, SAFE_CLOSE; types/structs: struct stat, struct tcase, struct tst_test; functions: check_fstat, run, setup, cleanup; local macros/constants: TESTFILE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: iterates a case table, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `stdlib.h`, `unistd.h`, `wait.h`, `sys/types.h`, `sys/stat.h`, `tst_test.h`, `tst_safe_macros.h`; integrates with the LTP fstat syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose; bad-address tests are ABI-sensitive.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, EFAULT; key constants: SIGSEGV, O_RDWR, O_CREAT; harness metadata: .test, .tcnt, .setup, .cleanup, .needs_tmpdir, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstatat/Makefile

Purpose: Build integration for the LTP `fstatat` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (7 lines, 236 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatat/fstatat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstatat/fstatat01.c

Purpose: Table-driven `fstatat()` coverage for dirfd-relative paths, symlinks, empty path, and expected errno cases. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>. DESCRIPTION This test case will verify basic function of fstatat64/newfstatat added by kernel 2.6.16 or up. Author Yi Yang <yyangcdl@cn.ibm.com> The file was read in full for this report (152 lines, 3678 bytes).

Important APIs/types/functions: calls/wrappers: fstatat(), close(), SAFE_ASPRINTF, SAFE_MKDIR, SAFE_OPEN, SAFE_FILE_PRINTF; types/structs: struct stat64, struct stat; functions: fstatat, main, setup, cleanup; local macros/constants: TEST_CASES, AT_FDCWD.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, kernel tunables that setup/cleanup must restore. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`, `string.h`, `signal.h`, `config.h`, `test.h`, `tso_safe_macros.h`, `lapi/syscalls.h`; integrates with the LTP fstatat syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENOTDIR, EBADF, EINVAL; key constants: AT_FDCWD, __NR_fstatat64, __NR_newfstatat, __NR_fstatat, O_DIRECTORY, O_CREAT, O_RDWR.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatat/fstatat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/Makefile

Purpose: Build integration for the LTP `fstatfs` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (11 lines, 322 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs01.c

Purpose: Validates successful `fstatfs()` on descriptors and checks returned filesystem statistics are sensible. Source notes: \ Verify that fstatfs() syscall executes successfully for all available filesystems. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (66 lines, 1212 bytes).

Important APIs/types/functions: calls/wrappers: fstatfs(), TST_EXP_PASS, SAFE_OPEN, SAFE_PIPE, SAFE_CLOSE; types/structs: struct tcase, struct statfs, struct tst_test; functions: run, setup, cleanup; local macros/constants: MNT_POINT, TEMP_FILE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `tst_test.h`; integrates with the LTP fstatfs syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior.

Test signals: explicit pass reporting; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .setup, .cleanup, .tcnt, .test, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs02.c

Purpose: Checks `fstatfs()` error behavior for invalid descriptors. Source notes: \ Testcase to check if fstatfs() sets errno correctly. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (74 lines, 1362 bytes).

Important APIs/types/functions: calls/wrappers: fstatfs(), SAFE_FORK, TST_EXP_FAIL, SAFE_WAITPID, SAFE_OPEN, SAFE_CLOSE; types/structs: struct statfs, struct test_case_t, struct tst_test; functions: fstatfs_verify, setup, cleanup.

Control flow: setup path: setup; exercise path: fstatfs_verify; cleanup path: cleanup; notable execution mechanics: iterates a case table, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `stdlib.h`, `sys/types.h`, `sys/statfs.h`, `sys/wait.h`, `tst_test.h`, `tst_safe_macros.h`; integrates with the LTP fstatfs syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose; bad-address tests are ABI-sensitive.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, EFAULT; key constants: SIGSEGV, O_RDWR, O_CREAT; harness metadata: .test, .tcnt, .setup, .cleanup, .needs_tmpdir, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsync/Makefile

Purpose: Build integration for the LTP `fsync` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: low behavioral risk; failures usually show up as missing test binaries or helper scripts at build/install time.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (8 lines, 237 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync01.c

Purpose: Basic `fsync()` success test on a writable temporary file. Source notes: AUTHOR : William Roske CO-PILOT : Dave Fenner SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (55 lines, 994 bytes).

Important APIs/types/functions: calls/wrappers: fsync(), SAFE_WRITE, SAFE_OPEN, SAFE_CLOSE; types/structs: struct tst_test; functions: verify_fsync, setup, cleanup; local macros/constants: BUF.

Control flow: setup path: setup; exercise path: verify_fsync; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `unistd.h`, `errno.h`, `stdio.h`, `tst_test.h`; integrates with the LTP fsync syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .cleanup, .setup, .test_all, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync02.c

Purpose: Checks `fsync()` error behavior for invalid descriptors and descriptor states. Source notes: Test Description: Test fsync() return value on test file fsync() has to finish within TIME_LIMIT. free blocks avail to non-superuser SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (119 lines, 2692 bytes).

Important APIs/types/functions: calls/wrappers: fsync(), SAFE_OPEN, SAFE_FCNTL, SAFE_WRITE, SAFE_LSEEK, SAFE_FTRUNCATE, SAFE_CLOSE; types/structs: struct statvfs, struct tst_test; functions: setup, run, cleanup; local macros/constants: BLOCKSIZE, MAXBLKS, BUF_SIZE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `stdlib.h`, `sys/types.h`, `sys/statvfs.h`, `fcntl.h`, `sys/resource.h`, `time.h`, `tst_test.h`; integrates with the LTP fsync syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT, O_TRUNC, F_SETFL, O_LARGEFILE; harness metadata: .test_all, .setup, .cleanup, .needs_tmpdir, .timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync03.c

Purpose: Validates data persistence/metadata behavior after writing a temporary file and calling `fsync()`. Source notes: \ Verify that, fsync(2) returns -1 and sets errno to - EINVAL if calling fsync() on a pipe(fd). - EINVAL if calling fsync() on a socket(fd). - EBADF if calling fsync() on a closed fd. - EBADF if calling fsync() on an invalid fd. - EINVAL if calling fsync() on a fifo(fd). EINVAL - fsync() on pipe should not succeed. EINVAL - fsync() on socket should not succeed. EBADF - fd is closed EBADF - fd is invalid (-1) EINVAL - fsync() on fifo should not succeed. SPDX-License-Identifier: GPL-2.0-or-later // FIFO must be opened for reading first, otherwise // open(fifo, O_WRONLY) will block. // Do not open any file descriptors after this line unless you close // them before the next test run. The file was read in full for this report (89 lines, 2167 bytes).

Important APIs/types/functions: calls/wrappers: fsync(), open(), pipe(), socket(), SAFE_MKFIFO, SAFE_PIPE, SAFE_OPEN, SAFE_SOCKET, SAFE_CLOSE; types/structs: struct test_case, struct tst_test; functions: setup, test_fsync, cleanup; local macros/constants: FIFO_PATH.

Control flow: setup path: setup; exercise path: test_fsync; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `unistd.h`, `errno.h`, `tst_test.h`; integrates with the LTP fsync syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, EBADF; key constants: O_WRONLY, O_RDONLY, O_NONBLOCK; harness metadata: .test, .tcnt, .needs_tmpdir, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync04.c

Purpose: Additional `fsync()` regression coverage for special filesystems, directories, or sync error handling. Source notes: Author: Sumit Garg <sumit.garg@linaro.org> fsync04 It basically tests fsync() to sync test file having large dirty file pages to block device. Also, it tests all supported filesystems on a test block device. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (66 lines, 1359 bytes).

Important APIs/types/functions: calls/wrappers: fsync(), SAFE_OPEN, SAFE_CLOSE; types/structs: struct tst_test; functions: verify_fsync; local macros/constants: MNTPOINT, FNAME, FILE_SIZE_MB, FILE_SIZE, MODE.

Control flow: exercise path: verify_fsync.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`; integrates with the LTP fsync syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .needs_root, .test_all.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/Makefile

Purpose: Build integration for the LTP `ftruncate` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; INSTALL_TARGETS		:= ftruncate04.sh; include $(top_srcdir)/include/mk/generic_leaf_target.mk`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: script/helper install targets must stay in sync with C tests.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (13 lines, 358 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate01.c

Purpose: Verifies `ftruncate()` shrinks/extends a file, preserves earlier data, zero-fills extension ranges, and updates file size. Source notes: Author: Wayne Boyer \ Verify that, ftruncate() succeeds to truncate a file to a certain length, if the file previously is smaller than the truncated size, ftruncate() shall increase the size of the file. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (103 lines, 2133 bytes).

Important APIs/types/functions: calls/wrappers: ftruncate(), SAFE_FSTAT, SAFE_LSEEK, SAFE_READ, SAFE_OPEN, SAFE_CLOSE; types/structs: struct stat, struct tst_test; functions: check_and_report, verify_ftruncate, setup, cleanup; local macros/constants: TESTFILE, TRUNC_LEN1, TRUNC_LEN2, FILE_SIZE.

Control flow: setup path: setup; exercise path: verify_ftruncate; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `unistd.h`, `fcntl.h`, `errno.h`, `string.h`, `tst_test.h`; integrates with the LTP ftruncate syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR; harness metadata: .test_all, .setup, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate03.c

Purpose: Negative `ftruncate()` coverage for socket descriptors, read-only descriptors, bad descriptors, and invalid lengths. Source notes: Author: Jay Huie, Robbie Williamson \ Verify that ftruncate(2) system call returns appropriate error number: 1. EINVAL -- the file is a socket 2. EINVAL -- the file descriptor was opened with O_RDONLY 3. EINVAL -- the length is negative 4. EBADF -- the file descriptor is invalid SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (91 lines, 1892 bytes).

Important APIs/types/functions: calls/wrappers: ftruncate(), SAFE_SOCKET, SAFE_OPEN, SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: verify_ftruncate, setup, cleanup; local macros/constants: TESTFILE1, TESTFILE2.

Control flow: setup path: setup; exercise path: verify_ftruncate; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `errno.h`, `string.h`, `sys/socket.h`, `tst_test.h`; integrates with the LTP ftruncate syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, EBADF; key constants: O_RDONLY, O_CREAT, O_RDWR; harness metadata: .tcnt, .test, .setup, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate04.c

Purpose: Mandatory locking regression test: parent `ftruncate()` calls fail inside/before a child-held lock and succeed after the child releases it. Source notes: Robbie Williamson <robbiew@us.ibm.com> Roy Lee <roylee@andestech.com> Test Description: Tests truncate and mandatory record locking. Parent creates a file, child locks a region and sleeps. Parent checks that ftruncate before the locked region and inside the region fails while ftruncate after the region succeds. Parent wakes up child, child exits, lock is unlocked. Parent checks that ftruncate now works in all cases. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (182 lines, 3920 bytes).

Important APIs/types/functions: calls/wrappers: fstat(), ftruncate(), mount(), SAFE_FSTAT, TST_CHECKPOINT_WAIT, SAFE_OPEN, TST_CHECKPOINT_WAKE, SAFE_WAIT, SAFE_CLOSE, SAFE_FCNTL, TST_CHECKPOINT_WAKE_AND_WAIT, SAFE_CHMOD, SAFE_FORK; types/structs: struct stat, struct flock, struct tst_test; functions: ftruncate_expect_fail, ftruncate_expect_success, doparent, dochild, verify_ftruncate, setup; local macros/constants: RECLEN, MNTPOINT, TESTFILE.

Control flow: setup path: setup; exercise path: ftruncate_expect_fail, ftruncate_expect_success, doparent, dochild, verify_ftruncate; notable execution mechanics: forks child processes for concurrency or privilege separation, uses LTP checkpoints to order parent/child actions.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, UID/capability-sensitive kernel state, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `errno.h`, `sys/types.h`, `sys/stat.h`, `sys/mount.h`, `unistd.h`, `stdlib.h`, `sys/statvfs.h`, `tst_test.h`; integrates with the LTP ftruncate syscall suite; uses the LTP C harness and result macros; declares kernel configuration requirements.

Risks: requires root/capability-sensitive behavior; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EAGAIN, EPERM; key constants: O_RDWR, O_NONBLOCK, F_WRLCK, F_SETLKW; harness metadata: .needs_kconfigs, .test_all, .setup, .needs_checkpoints, .forks_child, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/Makefile

Purpose: Build integration for the LTP `futex` syscall-test directory. It includes the common LTP syscall make rules and adds any directory-local compiler, linker, or install-target settings.

Important APIs/types/functions: Make variables and include flow are the important interface. Directory rules include `futex_cmp_requeue01: LDLIBS+=-lrt; futex_cmp_requeue02: LDLIBS+=-lrt; futex_wait02: LDLIBS+=-lrt; futex_wake03: LDLIBS+=-lrt; futex_wait05: LDLIBS+=-lrt; futex_wait_bitset01: LDLIBS+=-lrt; futex_waitv01: LDLIBS+=-lrt; futex_waitv02: LDLIBS+=-lrt; futex_waitv03: LDLIBS+=-lrt; futex_wait03: CFLAGS+=-pthread`

Control flow: The makefile is declarative: it sets local variables before including the shared LTP syscall makefile, so build-system evaluation applies these flags to only this syscall directory's targets.

State and persistence behavior: No runtime state is modified by this file. Its persistent effect is build metadata: generated binaries, linked libraries, and any installed helper scripts come from the surrounding LTP build.

Dependencies and integration points: Integrates with `../utils/newer_iptables`-style common LTP make infrastructure through `$(top_srcdir)/include/mk/testcases.mk` and `$(top_srcdir)/include/mk/generic_leaf_target.mk` when present in the file. It is consumed by the parent LTP test build, not by the test harness at runtime.

Risks: linker flags must match tests that use realtime, pthread, or helper libraries; compile flags are test-specific and affect threading or feature exposure.

Test signals: Successful compilation/install of this directory's tests is the primary signal; runtime assertions live in the sibling C files. The file was read in full for this report (23 lines, 654 bytes).
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex2test.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex2test.h

Purpose: Header helper for futex2/futex_waitv tests, wrapping `__NR_futex_waitv` and time64 ABI differences. Source notes: Futex2 library addons for futex tests futex_waitv - Wait at multiple futexes, wake on any @waiters: Array of waiters @nr_waiters: Length of waiters array @flags: Operation flags @timo: Optional timeout for operation _FUTEX2TEST_H The file was read in full for this report (47 lines, 1140 bytes).

Important APIs/types/functions: types/structs: struct timespec64, struct futex_waitv, struct timespec; functions: futex_waitv; local macros/constants: FUTEX2TEST_H.

Control flow: the file provides declarations/helpers consumed by sibling tests.

State and persistence behavior: The test manipulates futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdint.h`, `lapi/syscalls.h`, `futextest.h`, `lapi/abisize.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: key constants: __NR_futex_waitv.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex2test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue01.c

Purpose: Functional `FUTEX_CMP_REQUEUE` test that forks waiters, wakes some, requeues others, and verifies final wake counts. Source notes: \ Verify the basic functionality of futex(FUTEX_CMP_REQUEUE). futex(FUTEX_CMP_REQUEUE) can wake up the number of waiters specified by val argument and then requeue the number of waiters limited by val2 argument (i.e. move some remaining waiters from uaddr to uaddr2 address). spurious wakeup or signal make sure TST_PROCESS_STATE_WAIT() can always succeed change futex value, so any spurious wakeups or signals after this point get bounced back to userspace. Wakes up a maximum of tc->set_wakes waiters. tc->set_requeues specifies an upper limit on the number of waiters that are requeued. Returns the total number of waiters that were woken up or requeued. Fail if more than requested wakes + requeues were returned SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (221 lines, 5965 bytes).

Important APIs/types/functions: calls/wrappers: futex(), TST_PROCESS_STATE_WAIT, SAFE_FORK, SAFE_WAITPID, SAFE_MMAP, SAFE_MUNMAP; types/structs: struct shared_data, struct tcase, struct futex_test_variants, struct tst_ts, struct tst_test; functions: do_child, verify_futex_cmp_requeue, setup, cleanup.

Control flow: setup path: setup; exercise path: do_child, verify_futex_cmp_requeue; cleanup path: cleanup; notable execution mechanics: runs across syscall ABI variants, iterates a case table, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/wait.h`, `stdlib.h`, `sys/time.h`, `tst_test.h`, `futextest.h`, `lapi/futex.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EAGAIN; key constants: FUTEX_CMP_REQUEUE, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64, FUTEX_INITIALIZER; harness metadata: .setup, .cleanup, .tcnt, .test, .test_variants, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue02.c

Purpose: Negative `FUTEX_CMP_REQUEUE` and CVE-2018-6927 regression test for invalid wake/requeue counts and compare mismatches. Source notes: Description: Check various errnos for futex(FUTEX_CMP_REQUEUE). 1) futex(FUTEX_CMP_REQUEUE) with invalid val returns EINVAL. 2) futex(FUTEX_CMP_REQUEUE) with invalid val2 returns EINVAL. 3) futex(FUTEX_CMP_REQUEUE) with mismatched val3 returns EAGAIN. It's also a regression test for CVE-2018-6927: fbe0e839d1e2 ("futex: Prevent overflow by strengthen input validation") SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (98 lines, 2517 bytes).

Important APIs/types/functions: calls/wrappers: futex(), SAFE_MMAP, SAFE_MUNMAP; types/structs: struct tcase, struct futex_test_variants, struct tst_test, struct tst_tag; functions: verify_futex_cmp_requeue, setup, cleanup.

Control flow: setup path: setup; exercise path: verify_futex_cmp_requeue; cleanup path: cleanup; notable execution mechanics: runs across syscall ABI variants, iterates a case table.

State and persistence behavior: The test manipulates shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/time.h`, `tst_test.h`, `futextest.h`, `lapi/futex.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, EAGAIN; key constants: FUTEX_CMP_REQUEUE, FUTEX_INITIALIZER, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64; harness metadata: .setup, .cleanup, .test, .tcnt, .test_variants, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_utils.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_utils.h

Purpose: Shared futex syscall-variant and process/thread state helpers for futex tests. Source notes: Wait for nr_threads to be sleeping skip ".", ".." and the main thread FUTEX_UTILS_H__ SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (76 lines, 1742 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_OPENDIR, SAFE_READDIR, SAFE_FILE_SCANF, SAFE_CLOSEDIR; types/structs: struct futex_test_variants, struct dirent; functions: futex_variant, wait_for_threads; local macros/constants: FUTEX_UTILS_H__, FUTEX_VARIANTS.

Control flow: the file provides declarations/helpers consumed by sibling tests; notable execution mechanics: runs across syscall ABI variants.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `stdlib.h`; integrates with the LTP futex syscall suite.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: key constants: FUTEX_UTILS_H__, __NR_futex, __NR_futex_time64, FUTEX_VARIANTS, FUTEX_FN_FUTEX, FUTEX_FN_FUTEX64.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait01.c

Purpose: Checks `FUTEX_WAIT` timeout and would-block behavior for shared and private operations. Source notes: Based on futextest (futext_wait_timeout.c and futex_wait_ewouldblock.c) written by Darren Hart <dvhltc@us.ibm.com> Gowrishankar <gowrishankar.m@in.ibm.com> 1. Block on a futex and wait for timeout. 2. Test if FUTEX_WAIT op returns -EWOULDBLOCK if the futex value differs from the expected one. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (78 lines, 2127 bytes).

Important APIs/types/functions: types/structs: struct testcase, struct futex_test_variants, struct tst_ts, struct tst_test; functions: run, setup.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: runs across syscall ABI variants, iterates a case table.

State and persistence behavior: The test manipulates futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `futextest.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EWOULDBLOCK, ETIMEDOUT; key constants: FUTEX_WAIT, FUTEX_INITIALIZER, FUTEX_PRIVATE_FLAG, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64; harness metadata: .setup, .test, .tcnt, .test_variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait02.c

Purpose: Fork-based `FUTEX_WAIT` wakeup test using a shared mmap futex and child `futex_wake()`. Source notes: Block on a futex and wait for wakeup. This tests uses shared memory page to store the mutex variable. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (80 lines, 1702 bytes).

Important APIs/types/functions: calls/wrappers: TST_PROCESS_STATE_WAIT, SAFE_FORK, SAFE_WAIT, SAFE_MMAP; types/structs: struct futex_test_variants, struct tst_test; functions: do_child, run, setup.

Control flow: setup path: setup; exercise path: do_child, run; notable execution mechanics: runs across syscall ABI variants, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/mman.h`, `sys/wait.h`, `futextest.h`, `futex_utils.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64, FUTEX_INITIALIZER; harness metadata: .setup, .test_all, .test_variants, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait03.c

Purpose: Threaded private `FUTEX_WAIT` wakeup test using pthread synchronization and `FUTEX_PRIVATE_FLAG`. Source notes: Block on a futex and wait for wakeup. This tests uses private mutexes with threads. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (71 lines, 1669 bytes).

Important APIs/types/functions: calls/wrappers: TST_PROCESS_STATE_WAIT, SAFE_PTHREAD_CREATE, SAFE_PTHREAD_JOIN; types/structs: struct futex_test_variants, struct tst_test; functions: threaded, run, setup.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: runs across syscall ABI variants, uses pthread workers for concurrent access.

State and persistence behavior: The test manipulates threads and shared in-process synchronization, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `futextest.h`, `futex_utils.h`, `tst_safe_pthread.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: FUTEX_INITIALIZER, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64, FUTEX_PRIVATE_FLAG; harness metadata: .setup, .test_all, .test_variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait04.c

Purpose: Zero-page/uninitialized mapping regression test expecting `FUTEX_WAIT` on a mismatched value to return immediately. Source notes: Based on futextest (futext_wait_uninitialized_heap.c) written by KOSAKI Motohiro <kosaki.motohiro@jp.fujitsu.com> Wait on uninitialized heap. It shold be zero and FUTEX_WAIT should return immediately. This test tests zero page handling in futex code. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (58 lines, 1614 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_MMAP, SAFE_MUNMAP; types/structs: struct futex_test_variants, struct tst_ts, struct tst_test; functions: run, setup.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: runs across syscall ABI variants.

State and persistence behavior: The test manipulates shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `futextest.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EWOULDBLOCK; key constants: FUTEX_WAIT, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64; harness metadata: .setup, .test_all, .test_variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait05.c

Purpose: Timer harness test verifying `FUTEX_WAIT` timeout duration is approximately correct. Source notes: 1. Block on a futex and wait for timeout. 2. Check that the futex waited for expected time. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (44 lines, 891 bytes).

Important APIs/types/functions: types/structs: struct timespec, struct tst_test; functions: sample_fn.

Control flow: the file provides declarations/helpers consumed by sibling tests.

State and persistence behavior: The test manipulates futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `tst_timer_test.h`, `futextest.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit failure reporting; errno checks: ETIMEDOUT; key constants: FUTEX_INITIALIZER, FUTEX_WAIT; harness metadata: .scall, .sample.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait06.c

Purpose: Negative `FUTEX_WAIT` coverage for bad futex address and bad timeout pointer returning `EFAULT`. Source notes: \ Check that futex(FUTEX_WAIT) returns EFAULT when: 1) uaddr points to unmapped memory 2) timeout points to unmapped memory SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (73 lines, 1801 bytes).

Important APIs/types/functions: calls/wrappers: futex(), TST_EXP_FAIL; types/structs: struct futex_test_variants, struct testcase, struct tst_ts, struct tst_test; functions: run, setup.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: runs across syscall ABI variants, iterates a case table.

State and persistence behavior: The test manipulates futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/mman.h`, `futextest.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose; bad-address tests are ABI-sensitive.

Test signals: explicit failure reporting; errno checks: EFAULT; key constants: FUTEX_WAIT, FUTEX_INITIALIZER, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64; harness metadata: .setup, .test, .tcnt, .test_variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait07.c

Purpose: Signal interruption test proving a blocked `FUTEX_WAIT` returns `EINTR` after parent sends `SIGUSR1`. Source notes: \ Check that futex(FUTEX_WAIT) returns EINTR when interrupted by a signal. A child process blocks on futex_wait() with a long timeout. The parent waits for the child to enter sleep state, then sends SIGUSR1 to it. The child verifies it received EINTR and exits accordingly. Empty handler: receiving the signal is sufficient to interrupt futex_wait(). SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (89 lines, 2185 bytes).

Important APIs/types/functions: calls/wrappers: futex(), SAFE_SIGEMPTYSET, SAFE_SIGACTION, TST_EXP_FAIL, SAFE_FORK, TST_PROCESS_STATE_WAIT, SAFE_KILL, SAFE_WAITPID, SAFE_MMAP, SAFE_MUNMAP; types/structs: struct futex_test_variants, struct sigaction, struct tst_ts, struct tst_test; functions: sigusr1_handler, run, setup, cleanup.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: runs across syscall ABI variants, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `signal.h`, `futextest.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit failure reporting; errno checks: EINTR; key constants: FUTEX_WAIT, SIGUSR1, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64, FUTEX_INITIALIZER; harness metadata: .setup, .cleanup, .test_all, .test_variants, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait07.c -->
