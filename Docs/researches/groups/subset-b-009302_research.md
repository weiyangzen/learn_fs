# subset-b-009302 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock202.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock202.c

## Purpose
This file exercises mlock2(2) negative paths for invalid flags, RLIMIT_MEMLOCK exhaustion, zero memlock limits, and unmapped address ranges.
The source-level description states or implies: Copyright (c) 2018 FUJITSU LIMITED. All rights reserved. Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions
Key local functions: `verify_mlock2()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mlock2`.
LTP and helper APIs used include: `SAFE_GETPWNAM`, `SAFE_GETRLIMIT`, `SAFE_MMAP`, `SAFE_MUNLOCK`, `SAFE_MUNMAP`, `SAFE_SETEUID`, `SAFE_SETRLIMIT`, `TEST`, `mlock2`, `tst_res`, `tst_strerrno`, `tst_syscall`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_root`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 3 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; effective uid changes between root and nobody. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mlock2` syscall test directory. LTP new harness, lapi/syscalls, Linux mlock2 definitions, /proc/self/status VmLck, RLIMIT_MEMLOCK, root/nobody credential changes.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; temporarily changes resource limits or kernel control files and must restore them.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock203.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock203.c

## Purpose
This file regression-checks that relocking an MLOCK_ONFAULT range with normal mlock2 accounting does not double-count VmLck.
The source-level description states or implies: Copyright (c) 2018 FUJITSU LIMITED. All rights reserved. Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions
Key local functions: `verify_mlock2()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mlock2`.
LTP and helper APIs used include: `SAFE_FILE_LINES_SCANF`, `SAFE_MMAP`, `SAFE_MUNLOCK`, `SAFE_MUNMAP`, `TEST`, `mlock`, `mlock2`, `tst_res`, `tst_syscall`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_root`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mlock2` syscall test directory. LTP new harness, lapi/syscalls, Linux mlock2 definitions, /proc/self/status VmLck, RLIMIT_MEMLOCK, root/nobody credential changes.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/Makefile

## Purpose
This file builds the mlockall syscall leaf tests through the common LTP testcases and generic leaf make rules.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
There are no local compiler or linker overrides beyond the common LTP leaf rules.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes build variables only; no runtime persistence. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mlockall` syscall test directory. legacy LTP harness test.h, mlockall(2), RLIMIT_MEMLOCK, root/nobody credential transitions, and loop/pause options.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall01.c

## Purpose
This file legacy positive mlockall(2) smoke test for MCL_CURRENT, MCL_FUTURE, and their combination under root.
The source-level description states or implies: Copyright (c) Wipro Technologies Ltd, 2002. All Rights Reserved. This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PU

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mlockall`.
LTP and helper APIs used include: `TEST`, `mlockall`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mlockall` syscall test directory. legacy LTP harness test.h, mlockall(2), RLIMIT_MEMLOCK, root/nobody credential transitions, and loop/pause options.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall02.c

## Purpose
This file legacy mlockall(2) errno test for ENOMEM, EPERM, and EINVAL using RLIMIT_MEMLOCK and nobody credentials.
The source-level description states or implies: Copyright (c) Wipro Technologies Ltd, 2002. All Rights Reserved. This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PU

## Important APIs, Types, and Functions
Key local functions: `setup()`, `setup_test()`, `cleanup_test()`, `cleanup()`, `main()`, `setup()`, `setup_test()`, `cleanup_test()`, `cleanup()`.
Primary syscall/API surface: `mlockall`, `mount`.
LTP and helper APIs used include: `SAFE_SETEUID`, `TEST`, `mlock`, `mlockall`, `seteuid`, `setrlimit`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; mount namespace, mounted filesystems, and mount flags; effective uid changes between root and nobody; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mlockall` syscall test directory. legacy LTP harness test.h, mlockall(2), RLIMIT_MEMLOCK, root/nobody credential transitions, and loop/pause options.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering; signal or child-process expectations can be timing-sensitive; temporarily changes resource limits or kernel control files and must restore them.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall03.c

## Purpose
This file post-2.6.8 mlockall(2) errno regression test with explicit kernel-release gating and RLIMIT_MEMLOCK manipulation.
The source-level description states or implies: Copyright (C) Bull S.A. 2005. $ This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. You should have received a

## Important APIs, Types, and Functions
Key local functions: `setup()`, `setup_test()`, `compare()`, `cleanup_test()`, `cleanup()`, `main()`, `setup()`, `compare()`, `setup_test()`, `cleanup_test()`, `cleanup()`.
Primary syscall/API surface: `mlockall`.
LTP and helper APIs used include: `SAFE_SETEUID`, `TEST`, `mlockall`, `seteuid`, `setrlimit`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; effective uid changes between root and nobody; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mlockall` syscall test directory. legacy LTP harness test.h, mlockall(2), RLIMIT_MEMLOCK, root/nobody credential transitions, and loop/pause options.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive; temporarily changes resource limits or kernel control files and must restore them.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/Makefile

## Purpose
This file builds mmap syscall tests and adds pthread linkage for threaded mmap cases.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `LDLIBS 			+= -lpthread`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap01.c

## Purpose
This file verifies partial-page file mappings zero-fill bytes past EOF and do not write dirty beyond-EOF bytes back to the file.
The source-level description states or implies: Verify that mmap() succeeds when used to map a file where size of the file is not a multiple of the page size, the memory area beyond the end of the file to the end of the page is accessible. Also, verify that this area is all zeroed and the modifications done to this area are not written to the file. mmap() should succeed returning the address of the mapped region. The memory area beyond the end of file to the end o

## Important APIs, Types, and Functions
Key local functions: `check_file()`, `set_file()`, `run()`, `cleanup()`, `setup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CALLOC`, `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_MMAP`, `SAFE_MSYNC`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_STAT`, `SAFE_UNLINK`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `mmap`, `tst_brk`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap02.c

## Purpose
This file checks that a read-only file descriptor can be mapped PROT_READ and the mapped bytes match the file contents.
The source-level description states or implies: Verify that, mmap() call with PROT_READ and a file descriptor which is open for read only, succeeds to map a file creating mapped memory with read access.

## Important APIs, Types, and Functions
Key local functions: `setup()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FCHMOD`, `SAFE_MALLOC`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `mmap`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap03.c

## Purpose
This file checks PROT_EXEC file mappings from a readable executable file, including architecture behavior that may SIGSEGV on access.
The source-level description states or implies: Map a file with mmap() syscall, creating a mapped region with execute access under the following conditions: - file descriptor is open for read - minimum file permissions should be 0555 - file being mapped has PROT_EXEC execute permission bit set mmap() should succeed returning the address of the mapped region and the mapped region should contain the contents of the mapped file. On mips architecture, an attempt to ac

## Important APIs, Types, and Functions
Key local functions: `run_child()`, `run()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_LSEEK`, `SAFE_MALLOC`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_WAITPID`, `TST_EXP_EQ_LI`, `mmap`, `tst_fill_file`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap04.c

## Purpose
This file maps anonymous regions with many protection/share combinations and validates /proc/self/maps permission strings.
The source-level description states or implies: Verify that, after a successful mmap() call, permission bits of the new mapping in /proc/pid/maps file matches the prot and flags arguments in mmap() call.

## Important APIs, Types, and Functions
Key local functions: `run()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_FILE_LINES_SCANF`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_SYSCONF`, `mmap`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 15 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap05.c

## Purpose
This file verifies PROT_NONE mappings are created successfully and fault with SIGSEGV when dereferenced.
The source-level description states or implies: Verify that, mmap() call with 'PROT_NONE' and a file descriptor which is open for read and write, succeeds to map the file creating mapped memory, but any attempt to access the contents of the mapped region causes the SIGSEGV signal.

## Important APIs, Types, and Functions
Key local functions: `sig_handler()`, `setup()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MALLOC`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_SIGNAL`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `mmap`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap06.c

## Purpose
This file tests mmap(2) failure errnos for write-only file descriptors, zero length, and missing sharing mode flags.
The source-level description states or implies: Verify that, mmap() call fails with errno: - EACCES, when a file mapping is requested but the file descriptor is not open for reading. - EINVAL, when length argument is 0. - EINVAL, when flags contains none of MAP_PRIVATE, MAP_SHARED, or MAP_SHARED_VALIDATE.

## Important APIs, Types, and Functions
Key local functions: `setup()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MALLOC`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TST_EXP_FAIL_PTR_VOID`, `mmap`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 9 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap08.c

## Purpose
This file verifies mmap(2) returns EBADF for a closed invalid file descriptor.
The source-level description states or implies: Verify that, mmap() calls fails with errno EBADF when a file mapping is requested but the fd is not a valid file descriptor.

## Important APIs, Types, and Functions
Key local functions: `setup()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MUNMAP`, `SAFE_OPEN`, `TST_EXP_FAIL_PTR_VOID`, `mmap`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap09.c

## Purpose
This file keeps a file mapped while ftruncate shrinks, grows, and truncates it to zero to ensure the operations succeed.
The source-level description states or implies: Verify that truncating a mmaped file works correctly. Use ftruncate to: 1. shrink the file while it is mapped 2. grow the file while it is mapped 3. zero the size of the file while it is mapped

## Important APIs, Types, and Functions
Key local functions: `verify_mmap()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `ftruncate`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FTRUNCATE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `TST_EXP_PASS`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 4 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap10.c

## Purpose
This file stress-tests /dev/zero and anonymous mappings, optional KSM mergeability, fork, and partial munmap paths related to THP/rmap bugs.
The source-level description states or implies: This test examines the functionality of mapping and unmapping /dev/zero, which is a common method for allocating anonymous memory in Solaris. The primary objective is to determine whether it is possible to successfully map and unmap /dev/zero, as well as to read from and write to the mapped memory. The design of this test is inspired by two previous bugs, incorporating variations based on their reproducers. Additiona

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`.
Primary syscall/API surface: `mmap`, `munmap`, `madvise`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_SYSCONF`, `fork`, `madvise`, `mmap`, `munmap`, `tst_brk`, `tst_reap_children`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.forks_child`, `.needs_root`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 5 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap11.c

## Purpose
This file legacy threaded regression for munmap not checking sysctl_max_mapcount when detached pthread stacks are freed.
The source-level description states or implies: Copyright (C) 2010 Red Hat, Inc. This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Further, this software is

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `check()`, `main()`, `setup()`, `cleanup()`, `check()`.
Primary syscall/API surface: `munmap`.
LTP and helper APIs used include: `munmap`, `pthread_attr_init`, `pthread_attr_setdetachstate`, `pthread_attr_t`, `pthread_create`, `pthread_t`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap12.c

## Purpose
This file checks MAP_POPULATE file mappings by consulting pagemap for present pages and verifying zero-filled file contents.
The source-level description states or implies: Verify that mmap() with MAP_POPULATE succeed returning the address of the mapped region. The file should be read into RAM, and pages should be present.

## Important APIs, Types, and Functions
Key local functions: `page_check()`, `verify_mmap()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FTRUNCATE`, `SAFE_LSEEK`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_READ`, `mmap`, `tst_brk`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap13.c

## Purpose
This file verifies that touching a mapped page beyond file-backed storage raises SIGBUS.
The source-level description states or implies: Verify that, mmap() call succeeds to create a file mapping with length argument greater than the file size but any attempt to reference the memory region which does not correspond to the file causes SIGBUS signal.

## Important APIs, Types, and Functions
Key local functions: `sig_handler()`, `setup()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FTRUNCATE`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_SIGNAL`, `mmap`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap14.c

## Purpose
This file checks MAP_LOCKED accounting by comparing VmLck before and after a locked anonymous mapping.
The source-level description states or implies: Verify basic functionality of mmap(2) with MAP_LOCKED. mmap(2) should succeed returning the address of the mapped region, and this region should be locked into memory.

## Important APIs, Types, and Functions
Key local functions: `getvmlck()`, `run()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_FCLOSE`, `SAFE_FOPEN`, `SAFE_MUNMAP`, `SAFE_SSCANF`, `mmap`, `tst_res`, `tst_safe_stdio`, `tst_test`.
Harness fields present in `struct tst_test`: `.needs_root`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap15.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap15.c

## Purpose
This file ensures a fixed mapping into a high address fails with ENOMEM or EINVAL.
The source-level description states or implies: Verify that, a normal page cannot be mapped into a high memory region, and mmap() call fails with either ENOMEM or EINVAL errno.

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MUNMAP`, `SAFE_OPEN`, `TESTPTR`, `mmap`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap16.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap16.c

## Purpose
This file ext4 regression test for mmap data corruption when the filesystem runs out of blocks with block size below page size.
The source-level description states or implies: This is a regression test for a silent data corruption for a mmaped file when filesystem gets out of space. Fixed by commits: commit 0572639ff66dcffe62d37adfe4c4576f9fc398f4 Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> Date: Thu Feb 12 23:00:17 2015 -0500 ext4: fix mmap data corruption in nodelalloc mode when blocksize < pagesize commit d6320cbfc92910a3e5f10c42d98c231c98db4f60 Author: Jan Kara <jack@suse.cz> D

## Important APIs, Types, and Functions
Key local functions: `do_child()`, `run_single()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mmap`, `mremap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_FTRUNCATE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_UNLINK`, `SAFE_WAITPID`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `mmap`, `mremap`, `tst_brk`, `tst_fs`, `tst_res`, `tst_strstatus`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.mntpoint`, `.mount_device`, `.needs_checkpoints`, `.needs_root`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; mount namespace, mounted filesystems, and mount flags; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering; signal or child-process expectations can be timing-sensitive; It intentionally exhausts a small ext4 filesystem and relies on SIGBUS versus silent corruption behavior, so filesystem selection and cleanup are high risk..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap17.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap17.c

## Purpose
This file validates MAP_FIXED_NOREPLACE by attempting to map over an existing range and expecting EEXIST.
The source-level description states or implies: Verify MAP_FIXED_NOREPLACE flag for the mmap() syscall and check if an attempt to mmap at an exisiting mapping fails with EEXIST.

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `test_mmap()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `mmap`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.min_kver`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.
The test declares a minimum kernel version so unsupported kernels are filtered by the harness.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap18.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap18.c

## Purpose
This file tests MAP_GROWSDOWN stack growth with custom pthread stacks and expected SIGSEGV when growth is blocked.
The source-level description states or implies: Verify mmap() syscall using MAP_GROWSDOWN flag. [Algorithm] **Test 1** We assign the memory region partially allocated with MAP_GROWSDOWN flag to a thread as a stack and expect the mapping to grow when we touch the guard page by calling a recusive function in the thread that uses the growable mapping as a stack. The kernel only grows the memory region when the stack pointer is within guard page when the guard page is

## Important APIs, Types, and Functions
Key local functions: `__attribute__()`, `setup()`, `grow_stack()`, `grow_stack_success()`, `grow_stack_fail()`, `run_test()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_FORK`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_WAIT`, `mmap`, `pthread_attr_init`, `pthread_attr_setstack`, `pthread_attr_t`, `pthread_stack`, `pthread_t`, `tst_brk`, `tst_no_corefile`, `tst_res`, `tst_safe_pthread`, `tst_strsig`, `tst_strstatus`, `tst_test`.
Harness fields present in `struct tst_test`: `.forks_child`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap18.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap19.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap19.c

## Purpose
This file checks TLB flushing by remapping two file mappings at swapped virtual addresses and comparing contents.
The source-level description states or implies: If the kernel fails to correctly flush the TLB entry, the second mmap will not show the correct data. [Algorithm] - create two files, write known data to the files - mmap the files, verify data - unmap files - remmap files, swap virtual addresses - check wheather if the memory content is correct

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `mmap`, `tst_brk`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap19.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap20.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap20.c

## Purpose
This file checks MAP_SHARED_VALIDATE rejects an unknown flag with EOPNOTSUPP.
The source-level description states or implies: Test mmap(2) with MAP_SHARED_VALIDATE flag. Test expected EOPNOTSUPP errno when testing mmap(2) with MAP_SHARED_VALIDATE flag and invalid flag.

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `test_mmap()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MUNMAP`, `SAFE_OPEN`, `mmap`, `tst_brk`, `tst_fill_file`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.min_kver`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.
The test declares a minimum kernel version so unsupported kernels are filtered by the harness.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap21.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap21.c

## Purpose
This file maps a large file, writes deterministic bytes through the mapping in a child, msyncs, and verifies file contents.
The source-level description states or implies: Verify that we can use mmap() to map a large file, write to it via memory access, and read back the data from the file.

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_LSEEK`, `SAFE_MALLOC`, `SAFE_MMAP`, `SAFE_MSYNC`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_UNLINK`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `mmap`, `tst_brk`, `tst_option`, `tst_parse_filesize`, `tst_reap_children`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.needs_tmpdir`, `.options`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap22.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap22.c

## Purpose
This file tests MAP_DROPPABLE reclaim behavior under memory cgroup pressure using mincore.
The source-level description states or implies: Test :manpage:`mmap(2)` with MAP_DROPPABLE flag. Test based on :kselftest:`mm/droppable.c`. Ensure that memory allocated with MAP_DROPPABLE can be reclaimed under memory pressure within a cgroup.

## Important APIs, Types, and Functions
Key local functions: `stress_child()`, `test_mmap()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CG_PRINTF`, `SAFE_FORK`, `SAFE_KILL`, `SAFE_MALLOC`, `SAFE_MINCORE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_WAITPID`, `mmap`, `tst_brk`, `tst_cg`, `tst_cg_drain`, `tst_cg_group`, `tst_cg_group_mk`, `tst_cg_group_rm`, `tst_remaining_runtime`, `tst_res`, `tst_safe_macros`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.min_mem_avail`, `.needs_cgroup_ctrls`, `.needs_root`, `.needs_tmpdir`, `.runtime`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 3 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive; temporarily changes resource limits or kernel control files and must restore them; It moves the test into a memory cgroup and kills a pressure child; cgroup drain cleanup is essential..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap22.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/Makefile

## Purpose
This file builds the modify_ldt leaf tests through the common LTP make infrastructure.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
There are no local compiler or linker overrides beyond the common LTP leaf rules.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes build variables only; no runtime persistence. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `modify_ldt` syscall test directory. x86/i386 LDT ABI via lapi/ldt.h and SAFE_MODIFY_LDT; tests are architecture-gated.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/common.h

## Purpose
This file provides the modify_ldt helper that fills a user_desc entry and installs it with SAFE_MODIFY_LDT.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer Copyright (c) 2025 SUSE LLC Ricardo B. Marlière <rbm@suse.com>

## Important APIs, Types, and Functions
LTP and helper APIs used include: `SAFE_MODIFY_LDT`, `tst_test`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes . Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `modify_ldt` syscall test directory. x86/i386 LDT ABI via lapi/ldt.h and SAFE_MODIFY_LDT; tests are architecture-gated.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/modify_ldt01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/modify_ldt01.c

## Purpose
This file i386-only modify_ldt(2) validation of read/write success and EFAULT/EINVAL error cases.
The source-level description states or implies: Verify that modify_ldt() calls: - Fails with EFAULT, when reading (func=0) from an invalid pointer - Passes when reading (func=0) from a valid pointer - Fails with EINVAL, when writing (func=1) to an invalid pointer - Fails with EINVAL, when writing (func=1) with an invalid bytecount value - Fails with EINVAL, when writing (func=1) an entry with invalid values - Fails with EINVAL, when writing (func=0x11) an entry wi

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`.
Primary syscall/API surface: `modify_ldt`.
LTP and helper APIs used include: `TST_EXP_FAIL`, `TST_EXP_POSITIVE`, `modify_ldt`, `tst_buffers`, `tst_test`.
Harness fields present in `struct tst_test`: `.bufs`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 6 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `modify_ldt` syscall test directory. x86/i386 LDT ABI via lapi/ldt.h and SAFE_MODIFY_LDT; tests are architecture-gated.

## Risks
Risks: bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/modify_ldt01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/modify_ldt02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/modify_ldt02.c

## Purpose
This file i386-only segment access regression that expects SIGSEGV after replacing an LDT entry with an invalid base.
The source-level description states or implies: Verify that after writing an invalid base address into a segment entry, a subsequent segment entry read will raise SIGSEV.

## Important APIs, Types, and Functions
Key local functions: `read_segment()`, `run()`.
LTP and helper APIs used include: `SAFE_FORK`, `SAFE_WAITPID`, `TST_EXP_EQ_LI`, `tst_res`, `tst_strstatus`, `tst_test`.
Harness fields present in `struct tst_test`: `.forks_child`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `modify_ldt` syscall test directory. x86/i386 LDT ABI via lapi/ldt.h and SAFE_MODIFY_LDT; tests are architecture-gated.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/modify_ldt02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/Makefile

## Purpose
This file builds mount syscall tests with _GNU_SOURCE enabled for GNU mount-related interfaces.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `CFLAGS			+= -D_GNU_SOURCE`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes build variables only; no runtime persistence. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount01.c

## Purpose
This file basic mount(2) positive test across supported filesystems using an LTP-formatted block device.
The source-level description states or implies: Basic test that checks mount() syscall works on multiple filesystems.

## Important APIs, Types, and Functions
Key local functions: `cleanup()`, `run()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_UMOUNT`, `TST_EXP_PASS`, `tst_device`, `tst_is_mounted`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.cleanup`, `.format_device`, `.mntpoint`, `.needs_root`, `.skip_filesystems`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount02.c

## Purpose
This file mount(2) negative matrix covering bad filesystem types, devices, mountpoints, remount state, bad pointers, and path errors.
The source-level description states or implies: Check for basic errors returned by mount(2) system call. - ENODEV if filesystem type not configured - ENOTBLK if specialfile is not a block device - EBUSY if specialfile is already mounted or it cannot be remounted read-only, because it still holds files open for writing. - EINVAL if specialfile or device is invalid or a remount was attempted, while source was not already mounted on target. - EFAULT if special file o

## Important APIs, Types, and Functions
Key local functions: `pre_mount()`, `post_umount()`, `pre_create_file()`, `post_delete_file()`, `pre_mount()`, `post_umount()`, `pre_create_file()`, `post_delete_file()`, `setup()`, `cleanup()`, `run()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MKNOD`, `SAFE_MOUNT`, `SAFE_OPEN`, `SAFE_TOUCH`, `SAFE_UMOUNT`, `TST_EXP_FAIL`, `tst_device`, `tst_get_bad_addr`, `tst_is_mounted`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.format_device`, `.mntpoint`, `.needs_root`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 15 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount03.c

## Purpose
This file validates mount flags such as readonly, nodev, noexec, remount, nosuid, noatime, nodiratime, and strictatime.
The source-level description states or implies: Check mount(2) system call with various flags. Verify that mount(2) syscall passes for each flag setting and validate the flags: - MS_RDONLY - mount read-only - MS_NODEV - disallow access to device special files - MS_NOEXEC - disallow program execution - MS_REMOUNT - alter flags of a mounted FS - MS_NOSUID - ignore suid and sgid bits - MS_NOATIME - do not update access times - MS_NODIRATIME - only update access_time

## Important APIs, Types, and Functions
Key local functions: `test_rdonly()`, `test_nodev()`, `test_noexec()`, `test_remount()`, `test_nosuid()`, `test_file_dir_noatime()`, `test_noatime()`, `test_nodiratime()`, `test_strictatime()`, `setup()`, `cleanup()`, `run()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_CHMOD`, `SAFE_CLOSE`, `SAFE_CLOSEDIR`, `SAFE_CP`, `SAFE_EXECL`, `SAFE_FORK`, `SAFE_FSTAT`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_MKNOD`, `SAFE_MOUNT`, `SAFE_OPEN`, `SAFE_OPENDIR`, `SAFE_READ`, `SAFE_READDIR`, `SAFE_SETREUID`, `SAFE_STAT`, `SAFE_STATFS`, `SAFE_UMOUNT`, `SAFE_UNLINK`, `SAFE_WRITE`, `TST_EXP_EQ_LI`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.cleanup`, `.forks_child`, `.format_device`, `.mntpoint`, `.needs_root`, `.resource_files`, `.setup`, `.skip_filesystems`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 14 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; effective uid changes between root and nobody; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering; signal or child-process expectations can be timing-sensitive; The nosuid check depends on copying the helper binary and preserving setuid mode while executing as nobody..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount03_suid_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount03_suid_child.c

## Purpose
This file setuid helper used by mount03 to prove MS_NOSUID prevents privilege gain.
The source-level description states or implies: Copyright (c) Wipro Technologies Ltd, 2002. All Rights Reserved. Copyright (c) 2022 Petr Vorel <pvorel@suse.cz>

## Important APIs, Types, and Functions
Key local functions: `main()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `TST_EXP_FAIL`, `setreuid`, `tst_reinit`, `tst_test`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; effective uid changes between root and nobody. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount03_suid_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount04.c

## Purpose
This file verifies mount(2) fails with EPERM after dropping effective uid to nobody.
The source-level description states or implies: Verify that mount(2) returns -1 and sets errno to EPERM if the user is not root.

## Important APIs, Types, and Functions
Key local functions: `cleanup()`, `run()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SAFE_UMOUNT`, `TST_EXP_FAIL`, `tst_device`, `tst_is_mounted`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.format_device`, `.mntpoint`, `.needs_root`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; effective uid changes between root and nobody. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount05.c

## Purpose
This file tests MS_BIND by bind-mounting a populated tree and checking the file and directory are visible through the second mount.
The source-level description states or implies: Test for feature MS_BIND of mount, which performs a bind mount, making a file or a directory subtree visible at another point within a file system.

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `run()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_RMDIR`, `SAFE_UMOUNT`, `TEST`, `TST_EXP_PASS`, `tst_device`, `tst_is_mounted`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.cleanup`, `.format_device`, `.mntpoint`, `.needs_root`, `.setup`, `.skip_filesystems`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 3 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount06.c

## Purpose
This file tests MS_MOVE by moving a mounted filesystem from one mountpoint to another in a private mount parent.
The source-level description states or implies: Test for feature MS_MOVE of mount, which moves an existing mount point to a new location.

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `run()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_RMDIR`, `SAFE_UMOUNT`, `TEST`, `TST_EXP_FAIL`, `TST_EXP_PASS`, `tst_device`, `tst_is_mounted`, `tst_test`, `tst_tmpdir_genpath`, `tst_tmpdir_path`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.cleanup`, `.format_device`, `.mntpoint`, `.needs_root`, `.setup`, `.skip_filesystems`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount07.c

## Purpose
This file tests MS_NOSYMFOLLOW semantics, including link traversal failure, readlink/realpath behavior, and statfs flags.
The source-level description states or implies: It is a basic test for MS_NOSYMFOLLOW mount option and is copied from :kselftest:`mount/nosymfollow-test.c`. It tests to make sure that symlink traversal fails with ELOOP when 'nosymfollow' is set, but symbolic links can still be created, and :manpage:`readlink(2)` and :manpage:`realpath(3)` still work properly. It also verifies that :manpage:`statfs(2)` correctly returns ST_NOSYMFOLLOW.

## Important APIs, Types, and Functions
Key local functions: `setup_symlink()`, `test_link_traversal()`, `test_readlink()`, `test_realpath()`, `test_cycle_link()`, `test_statfs()`, `setup()`, `cleanup()`, `run_tests()`, `run()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_STATFS`, `SAFE_SYMLINK`, `SAFE_UMOUNT`, `TESTPTR`, `TST_EXP_FAIL2`, `TST_EXP_FD`, `TST_EXP_PASS`, `TST_EXP_PASS_SILENT`, `TST_EXP_POSITIVE`, `tst_device`, `tst_is_mounted`, `tst_res`, `tst_test`, `tst_tmpdir_genpath`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.cleanup`, `.forks_child`, `.format_device`, `.min_kver`, `.mntpoint`, `.needs_root`, `.setup`, `.skip_filesystems`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 5 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.
The test declares a minimum kernel version so unsupported kernels are filtered by the harness.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering; signal or child-process expectations can be timing-sensitive; Symlink behavior differs for tmpfs setup and for filesystems that do not support MS_NOSYMFOLLOW, hence the version and skip gates..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount08.c

## Purpose
This file regression test that bind mounting onto /proc/<pid>/fd magic links fails with ENOENT or SELinux EACCES.
The source-level description states or implies: Verify that mount will raise ENOENT if we try to mount on magic links under /proc/<pid>/fd/<nr>. If SELinux is enabled, the expected error also can be EACCES since SElinux plicy could be configured to block the operation.

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_OPENAT`, `SAFE_TOUCH`, `TST_EXP_FAIL_ARR`, `tst_safe_file_at`, `tst_selinux_enforcing`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.mntpoint`, `.needs_root`, `.setup`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/Makefile

## Purpose
This file builds mount_setattr tests through generic LTP syscall test rules.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
There are no local compiler or linker overrides beyond the common LTP leaf rules.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes build variables only; no runtime persistence. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount_setattr` syscall test directory. new mount API wrappers from lapi/fsmount.h, root privileges, mount namespaces, open_tree/move_mount, and statvfs or mountinfo inspection.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr01.c

## Purpose
This file checks mount_setattr and open_tree_attr variants by setting mount attributes and observing statvfs flags after move_mount.
The source-level description states or implies: Basic mount_setattr()/open_tree_attr() test. Test whether the basic mount attributes are set correctly. Verify some MOUNT_SETATTR(2) attributes: - MOUNT_ATTR_RDONLY - makes the mount read-only - MOUNT_ATTR_NOSUID - causes the mount not to honor the set-user-ID and set-group-ID mode bits and file capabilities when executing programs. - MOUNT_ATTR_NODEV - prevents access to devices on this mount - MOUNT_ATTR_NOEXEC - p

## Important APIs, Types, and Functions
Key local functions: `open_tree_variant1()`, `open_tree_variant2()`, `cleanup()`, `setup()`, `open_tree_variant1()`, `open_tree_variant2()`, `run()`.
Primary syscall/API surface: `mount`, `mount_setattr`, `move_mount`, `open_tree`, `open_tree_attr`, `fsmount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MKDIR`, `SAFE_UMOUNT`, `TST_EXP_FD`, `TST_EXP_FD_SILENT`, `TST_EXP_PASS`, `TST_EXP_PASS_SILENT`, `fsmount`, `mount_setattr`, `move_mount`, `open_tree`, `open_tree_attr`, `tst_buffers`, `tst_res`, `tst_test`, `tst_variant`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.bufs`, `.cleanup`, `.mntpoint`, `.mount_device`, `.needs_root`, `.setup`, `.skip_filesystems`, `.tcnt`, `.test`, `.test_variants`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 5 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount_setattr` syscall test directory. new mount API wrappers from lapi/fsmount.h, root privileges, mount namespaces, open_tree/move_mount, and statvfs or mountinfo inspection.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr02.c

## Purpose
This file checks mount_attr.propagation handling for invalid, unchanged, shared, slave, and private propagation values.
The source-level description states or implies: This test is checking if the propagation field of the mount_attr structure is handled properly. - EINVAL with propagation set to -1 - When propagation is set to 0 it's not changed - MS_SHARED turns propagation on - MS_SLAVE turns propagation off - MS_PRIVATE turns propagation off

## Important APIs, Types, and Functions
Key local functions: `check_mount_type()`, `cleanup()`, `setup()`, `run()`.
Primary syscall/API surface: `mount_setattr`, `fsmount`.
LTP and helper APIs used include: `SAFE_FOPEN`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_UMOUNT`, `SAFE_UNSHARE`, `TST_EXP_EQ_LI`, `TST_EXP_FAIL_SILENT`, `TST_EXP_PASS_SILENT`, `fsmount`, `mount_setattr`, `tst_res`, `tst_safe_stdio`, `tst_test`, `tst_tmpdir_path`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_root`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 4 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount_setattr` syscall test directory. new mount API wrappers from lapi/fsmount.h, root privileges, mount namespaces, open_tree/move_mount, and statvfs or mountinfo inspection.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering; It unshares the mount namespace and remounts / private; cleanup must not leak mounts in the namespace..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/Makefile

## Purpose
This file builds move_mount tests through generic LTP syscall test rules.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
There are no local compiler or linker overrides beyond the common LTP leaf rules.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes build variables only; no runtime persistence. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_mount` syscall test directory. new mount API wrappers fsopen/fsconfig/fsmount/open_tree/move_mount, root privileges, formatted devices, tmpfs, and kernel-version gates.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount01.c

## Purpose
This file positive move_mount(2) test that builds a detached fsopen/fsmount tree and moves it onto a mountpoint with flag variants.
The source-level description states or implies: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> Basic move_mount() test.

## Important APIs, Types, and Functions
Key local functions: `run()`.
Primary syscall/API surface: `move_mount`, `fsopen`, `fsconfig`, `fsmount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_UMOUNT`, `TEST`, `fsconfig`, `fsmount`, `fsopen`, `move_mount`, `tst_device`, `tst_is_mounted_at_tmpdir`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.format_device`, `.mntpoint`, `.needs_root`, `.setup`, `.skip_filesystems`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 6 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_mount` syscall test directory. new mount API wrappers fsopen/fsconfig/fsmount/open_tree/move_mount, root privileges, formatted devices, tmpfs, and kernel-version gates.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount02.c

## Purpose
This file negative move_mount(2) test for invalid fds, missing paths, and invalid flags.
The source-level description states or implies: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> Basic move_mount() failure tests.

## Important APIs, Types, and Functions
Key local functions: `run()`.
Primary syscall/API surface: `move_mount`, `fsopen`, `fsconfig`, `fsmount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_UMOUNT`, `TEST`, `fsconfig`, `fsmount`, `fsopen`, `move_mount`, `tst_device`, `tst_res`, `tst_strerrno`, `tst_test`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.format_device`, `.mntpoint`, `.needs_root`, `.setup`, `.skip_filesystems`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 4 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_mount` syscall test directory. new mount API wrappers fsopen/fsconfig/fsmount/open_tree/move_mount, root privileges, formatted devices, tmpfs, and kernel-version gates.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount03.c

## Purpose
This file kernel 6.5 MOVE_MOUNT_BENEATH regression test that stacks one tmpfs mount below another and checks visibility after unmount.
The source-level description states or implies: Test allow to mount beneath top mount feature added in kernel 6.5: 6ac392815628 ("fs: allow to mount beneath top mount") Test based on: https://github.com/brauner/move-mount-beneath See also: - https://lore.kernel.org/all/20230202-fs-move-mount-replace-v4-0-98f3d80d7eaa@kernel.org/ - https://lwn.net/Articles/930591/ - https://github.com/brauner/move-mount-beneath

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mount`, `move_mount`, `open_tree`, `fsmount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_OPEN`, `SAFE_TOUCH`, `SAFE_UMOUNT`, `TST_EXP_FAIL`, `TST_EXP_PASS`, `fsmount`, `move_mount`, `open_tree`, `tst_brk`, `tst_is_mounted_at_tmpdir`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.min_kver`, `.needs_root`, `.needs_tmpdir`, `.setup`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 3 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_mount` syscall test directory. new mount API wrappers fsopen/fsconfig/fsmount/open_tree/move_mount, root privileges, formatted devices, tmpfs, and kernel-version gates.
The test declares a minimum kernel version so unsupported kernels are filtered by the harness.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/Makefile

## Purpose
This file builds move_pages numbered tests, links each with move_pages_support.o, and adds pthread/rt plus NUMA utility include paths.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `CPPFLAGS		+= -I$(abs_srcdir)/../utils`; `MAKE_TARGETS		:= $(patsubst $(abs_srcdir)/%.c,%,$(sort $(wildcard $(abs_srcdir)/*[0-9].c)))`; `LDLIBS			+= -lpthread -lrt`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages01.c

## Purpose
This file retrieves NUMA node status for pages allocated across allowed nodes and verifies move_pages query results.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `fork`, `numa_move_pages`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages02.c

## Purpose
This file moves private pages from one NUMA node to another with MPOL_MF_MOVE and verifies the destination node.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `fork`, `numa_move_pages`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages03.c

## Purpose
This file moves shared pages with MPOL_MF_MOVE_ALL while a forked child also maps them, synchronizing with shared semaphores.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `child()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `fork`, `numa_move_pages`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages04.c

## Purpose
This file validates move_pages per-page status for untouched memory, shared zero page, and invalid address cases.
The source-level description states or implies: Verify that move_pages() properly reports failures when the memory area is not valid, no page is mapped yet or the shared zero page is mapped. [Algorithm] #. Pass the address of a valid memory area where no page is mapped yet (not read/written), the address of a valid memory area where the shared zero page is mapped (read, but not written to) and the address of an invalid memory area as page addresses to move_pages()

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `numa_alloc_onnode`, `numa_free`, `numa_move_pages`, `tst_brk`, `tst_res`, `tst_strerrno`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.setup`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages05.c

## Purpose
This file checks moving a shared page without MPOL_MF_MOVE_ALL reports -EACCES while using an unshared companion page.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `child()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `fork`, `numa_move_pages`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages06.c

## Purpose
This file passes a non-existent NUMA node to move_pages and expects ENODEV.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `fork`, `numa_max_node`, `numa_move_pages`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages07.c

## Purpose
This file passes an unused process id to move_pages and expects ESRCH.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `fork`, `numa_move_pages`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_get_unused_pid`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages09.c

## Purpose
This file requests pages to stay on their current NUMA node and expects move_pages to succeed.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `fork`, `numa_move_pages`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages10.c

## Purpose
This file passes invalid move_pages flags and expects EINVAL.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `fork`, `numa_move_pages`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages11.c

## Purpose
This file drops to nobody and verifies MPOL_MF_MOVE_ALL on shared pages fails with EPERM.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `child()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `SAFE_SETEUID`, `fork`, `numa_move_pages`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; effective uid changes between root and nobody; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages12.c

## Purpose
This file hugetlb race regression suite for move_pages versus hugepage free, soft offline, and migration/fault behavior.
The source-level description states or implies: *Test 1* This is a regression test for the race condition between move_pages() and freeing hugepages, where move_pages() calls follow_page(FOLL_GET) for hugepages internally and tries to get its refcount without preventing concurrent freeing. This test can crash the buggy kernel, and the bug was fixed in: commit e66f17ff71772b209eed39de35aaa99ba819c93d Author: Naoya Horiguchi <n-horiguchi@ah.jp.nec.com> Date: Wed Feb

## Important APIs, Types, and Functions
Key local functions: `do_soft_offline()`, `do_child()`, `do_test()`, `alloc_free_huge_on_node()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`, `move_pages`, `madvise`.
LTP and helper APIs used include: `SAFE_FILE_LINES_SCANF`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_FORK`, `SAFE_KILL`, `SAFE_MALLOC`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_WAITPID`, `TEST`, `madvise`, `mbind`, `mlock`, `mmap`, `numa_bitmask_alloc`, `numa_bitmask_free`, `numa_bitmask_setbit`, `numa_max_possible_node`, `numa_move_pages`, `tst_brk`, `tst_remaining_runtime`, `tst_res`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.needs_root`, `.runtime`, `.setup`, `.tags`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 10 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive; temporarily changes resource limits or kernel control files and must restore them; It mutates hugepage pool sysfs state and runs for up to 240 seconds, so cleanup restoration and sufficient free memory are critical..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.c

## Purpose
This file shared NUMA helper implementation for page allocation, NUMA status verification, shared page setup, semaphores, and config gating.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warra

## Important APIs, Types, and Functions
Key local functions: `get_page_size()`, `free_pages()`, `alloc_pages_on_nodes()`, `alloc_pages_linear()`, `alloc_pages_on_node()`, `verify_pages_on_nodes()`, `verify_pages_linear()`, `verify_pages_on_node()`, `alloc_shared_pages_on_node()`, `free_shared_pages()`, `free_sem()`, `check_config()`.
Primary syscall/API surface: `mmap`, `munmap`.
LTP and helper APIs used include: `get_mempolicy`, `mmap`, `munmap`, `numa_alloc_onnode`, `numa_available`, `numa_free`, `numa_tonode_memory`, `tst_brkm`, `tst_resm`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.h

## Purpose
This file declares the NUMA helper API used by the move_pages syscall tests.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warra

## Important APIs, Types, and Functions
Key local functions: `get_page_size()`, `free_pages()`, `alloc_pages_on_nodes()`, `alloc_pages_linear()`, `alloc_pages_on_node()`, `verify_pages_on_nodes()`, `verify_pages_linear()`, `verify_pages_on_node()`, `alloc_shared_pages_on_node()`, `free_shared_pages()`, `free_sem()`, `check_config()`.
LTP and helper APIs used include: `numa_helper`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/Makefile

## Purpose
This file builds mprotect tests and adds function alignment for mprotect04 executable-page copying.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
There are no local compiler or linker overrides beyond the common LTP leaf rules.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mprotect` syscall test directory. mmap/mprotect primitives, legacy LTP signal handling or new harness tags, child processes for SIGSEGV checks, and architecture/compiler cache support in executable tests.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect01.c

## Purpose
This file legacy mprotect(2) errno test for inaccessible address, unaligned address, and adding write access to read-only mapping.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant

## Important APIs, Types, and Functions
Key local functions: `cleanup()`, `setup()`, `setup1()`, `setup2()`, `setup3()`, `main()`, `setup1()`, `setup2()`, `setup3()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`, `mprotect`.
LTP and helper APIs used include: `SAFE_OPEN`, `TEST`, `mmap`, `mprotect`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`, `tst_syscall`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mprotect` syscall test directory. mmap/mprotect primitives, legacy LTP signal handling or new harness tags, child processes for SIGSEGV checks, and architecture/compiler cache support in executable tests.

## Risks
Risks: bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect02.c

## Purpose
This file checks mprotect can change a read-only file mapping to writable by observing SIGSEGV before and successful write after.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant

## Important APIs, Types, and Functions
Key local functions: `sighandler()`, `cleanup()`, `setup()`, `main()`, `sighandler()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`, `mprotect`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_UNLINK`, `SAFE_WAITPID`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `fork`, `mmap`, `mprotect`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_resm`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mprotect` syscall test directory. mmap/mprotect primitives, legacy LTP signal handling or new harness tags, child processes for SIGSEGV checks, and architecture/compiler cache support in executable tests.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect03.c

## Purpose
This file checks mprotect can remove write permission from a shared mapping and cause child writes to SIGSEGV.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant

## Important APIs, Types, and Functions
Key local functions: `cleanup()`, `setup()`, `main()`, `sighandler()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`, `mprotect`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MUNMAP`, `SAFE_UNLINK`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `fork`, `mmap`, `mprotect`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_resm`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mprotect` syscall test directory. mmap/mprotect primitives, legacy LTP signal handling or new harness tags, child processes for SIGSEGV checks, and architecture/compiler cache support in executable tests.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect04.c

## Purpose
This file tests PROT_NONE faulting and PROT_EXEC execution after copying a function to an anonymous page.
The source-level description states or implies: Copyright (c) 2014 Fujitsu Ltd. Author: Xing Gu <gux.fnst@cn.fujitsu.com> This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PART

## Important APIs, Types, and Functions
Key local functions: `sighandler()`, `setup()`, `cleanup()`, `testfunc_protnone()`, `testfunc_protexec()`, `main()`, `sighandler()`, `setup()`, `testfunc_protnone()`, `exec_func()`, `page_present()`, `clear_cache()`, `testfunc_protexec()`, `cleanup()`.
Primary syscall/API surface: `mprotect`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `TEST`, `mprotect`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mprotect` syscall test directory. mmap/mprotect primitives, legacy LTP signal handling or new harness tags, child processes for SIGSEGV checks, and architecture/compiler cache support in executable tests.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect05.c

## Purpose
This file regression test for mprotect VMA split and merge behavior over a five-page mapping.
The source-level description states or implies: Testcase to check the mprotect(2) system call split and merge. https://bugzilla.kernel.org/show_bug.cgi?id=217061

## Important APIs, Types, and Functions
Key local functions: `setup()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mprotect`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_UNLINK`, `mprotect`, `tst_res`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mprotect` syscall test directory. mmap/mprotect primitives, legacy LTP signal handling or new harness tags, child processes for SIGSEGV checks, and architecture/compiler cache support in executable tests.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/Makefile

## Purpose
This file builds mq_notify tests with POSIX IPC helper include path and pthread/rt libraries.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `CPPFLAGS		+= -I$(abs_srcdir)/../utils`; `LDLIBS			+= -lpthread -lrt`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_notify` syscall test directory. POSIX message queues, tst_safe_posix_ipc, common mq helpers, signal/thread notification, pthread and realtime linkage.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify01.c

## Purpose
This file validates mq_notify registration, signal/thread notification delivery, invalid descriptors, and EBUSY for duplicate registration.
The source-level description states or implies: Copyright (c) Crackerjack Project., 2007-2008, Hitachi, Ltd Copyright (c) 2017 Petr Vorel <pvorel@suse.cz> Authors: Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp>

## Important APIs, Types, and Functions
Key local functions: `sigfunc()`, `tfunc()`, `do_test()`.
Primary syscall/API surface: `mq_notify`, `mq_timedsend`.
LTP and helper APIs used include: `TEST`, `mq_notify`, `mq_timedsend`, `tst_option`, `tst_res`, `tst_safe_posix_ipc`, `tst_strerrno`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.options`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 9 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_notify` syscall test directory. POSIX message queues, tst_safe_posix_ipc, common mq helpers, signal/thread notification, pthread and realtime linkage.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify02.c

## Purpose
This file small mq_notify invalid sigevent argument test expecting EINVAL.
The source-level description states or implies: This test verifies that mq_notify() fails with EINVAL when invalid input arguments are given.

## Important APIs, Types, and Functions
Key local functions: `run()`.
Primary syscall/API surface: `mq_notify`.
LTP and helper APIs used include: `TST_EXP_FAIL`, `mq_notify`, `tst_test`.
Harness fields present in `struct tst_test`: `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 3 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_notify` syscall test directory. POSIX message queues, tst_safe_posix_ipc, common mq helpers, signal/thread notification, pthread and realtime linkage.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify03.c

## Purpose
This file glibc CVE-2021-38604 regression for SIGEV_THREAD notifier unregister/re-register NULL dereference behavior.
The source-level description states or implies: Test for NULL pointer dereference in mq_notify(CVE-2021-38604) References links: - https://sourceware.org/bugzilla/show_bug.cgi?id=28213

## Important APIs, Types, and Functions
Key local functions: `try_null_dereference_cb()`, `try_null_dereference()`, `do_test()`.
Primary syscall/API surface: `mq_notify`, `mq_unlink`.
LTP and helper APIs used include: `SAFE_MQ_OPEN`, `TST_EXP_PASS`, `TST_EXP_VAL`, `mq_attr`, `mq_maxmsg`, `mq_msgsize`, `mq_notify`, `mq_receive`, `mq_send`, `mq_unlink`, `tst_safe_posix_ipc`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.needs_root`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_notify` syscall test directory. POSIX message queues, tst_safe_posix_ipc, common mq helpers, signal/thread notification, pthread and realtime linkage.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_open/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_open/Makefile

## Purpose
This file builds mq_open tests with pthread and realtime library linkage.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `LDLIBS			+= -lpthread -lrt`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_open` syscall test directory. POSIX message queues, /proc/sys/fs/mqueue/queues_max, RLIMIT_NOFILE, root/nobody credentials, and mqueue cleanup.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_open/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_open/mq_open01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_open/mq_open01.c

## Purpose
This file mq_open matrix covering creation, attributes, long names, access, exclusivity, file descriptor limits, missing queues, and queues_max.
The source-level description states or implies: Copyright (c) Crackerjack Project., 2007-2008 ,Hitachi, Ltd Author(s): Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Copyright (c) 2016 Linux Test Project

## Important APIs, Types, and Functions
Key local functions: `create_queue()`, `unlink_queue()`, `set_rlimit()`, `restore_rlimit()`, `set_max_queues()`, `restore_max_queues()`, `create_queue()`, `unlink_queue()`, `set_max_queues()`, `restore_max_queues()`, `set_rlimit()`, `restore_rlimit()`, `setup()`, `cleanup()`, `do_test()`.
Primary syscall/API surface: `mq_open`, `mq_unlink`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_GETPWNAM`, `SAFE_GETRLIMIT`, `SAFE_MQ_OPEN`, `SAFE_SETEUID`, `SAFE_SETRLIMIT`, `TEST`, `mq_attr`, `mq_close`, `mq_getattr`, `mq_maxmsg`, `mq_msgsize`, `mq_open`, `mq_unlink`, `tst_brk`, `tst_res`, `tst_safe_file_ops`, `tst_safe_posix_ipc`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_root`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 16 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; effective uid changes between root and nobody; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_open` syscall test directory. POSIX message queues, /proc/sys/fs/mqueue/queues_max, RLIMIT_NOFILE, root/nobody credentials, and mqueue cleanup.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; temporarily changes resource limits or kernel control files and must restore them.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_open/mq_open01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedreceive/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedreceive/Makefile

## Purpose
This file builds mq_timedreceive tests with POSIX IPC helper include path and pthread/rt libraries.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `CPPFLAGS		+= -I$(abs_srcdir)/../utils`; `LDLIBS			+= -lpthread -lrt`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_timedreceive` syscall test directory. shared mq_timed helper variants for libc/time64 syscalls, POSIX queues, signals, timeouts, and child isolation for bad pointers.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedreceive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedreceive/mq_timedreceive01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedreceive/mq_timedreceive01.c

## Purpose
This file mq_timedreceive matrix covering valid receives, sizes, priorities, bad fds, nonblocking empty queues, invalid timeouts, timeout, signal interruption, and bad timespec addresses.
The source-level description states or implies: Copyright (c) Crackerjack Project., 2007-2008, Hitachi, Ltd Copyright (c) 2017 Petr Vorel <pvorel@suse.cz> Authors: Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp>

## Important APIs, Types, and Functions
Key local functions: `setup()`, `verify_mqt_receive()`, `test_bad_addr()`, `do_test()`.
Primary syscall/API surface: `mq_timedreceive`, `mq_timedsend`.
LTP and helper APIs used include: `SAFE_FORK`, `SAFE_WAITPID`, `TEST`, `mq_timed`, `mq_timedreceive`, `mq_timedsend`, `tst_get_bad_addr`, `tst_res`, `tst_strerrno`, `tst_strstatus`, `tst_test`, `tst_ts`, `tst_ts_get`, `tst_ts_set_nsec`, `tst_ts_set_sec`, `tst_variant`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.setup`, `.tcnt`, `.test`, `.test_variants`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 16 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_timedreceive` syscall test directory. shared mq_timed helper variants for libc/time64 syscalls, POSIX queues, signals, timeouts, and child isolation for bad pointers.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedreceive/mq_timedreceive01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedsend/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedsend/Makefile

## Purpose
This file builds mq_timedsend tests with POSIX IPC helper include path and pthread/rt libraries.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `CPPFLAGS		+= -I$(abs_srcdir)/../utils`; `LDLIBS			+= -lpthread -lrt`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_timedsend` syscall test directory. shared mq_timed helper variants for libc/time64 syscalls, POSIX queues, signals, timeouts, full queue setup, and child isolation for bad pointers.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedsend/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedsend/mq_timedsend01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedsend/mq_timedsend01.c

## Purpose
This file mq_timedsend matrix covering valid sends, message size, priority, descriptors, nonblocking full queues, timeout validation, timeout, interruption, and bad pointers.
The source-level description states or implies: Copyright (c) Crackerjack Project., 2007-2008, Hitachi, Ltd Copyright (c) 2017 Petr Vorel <pvorel@suse.cz> Authors: Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp>

## Important APIs, Types, and Functions
Key local functions: `setup()`, `verify_mqt_send_receive()`, `test_bad_addr()`, `do_test()`.
Primary syscall/API surface: `mq_timedreceive`, `mq_timedsend`.
LTP and helper APIs used include: `SAFE_FORK`, `SAFE_WAITPID`, `TEST`, `mq_timed`, `mq_timedreceive`, `mq_timedsend`, `tst_get_bad_addr`, `tst_res`, `tst_strerrno`, `tst_strstatus`, `tst_test`, `tst_ts`, `tst_ts_get`, `tst_ts_set_nsec`, `tst_ts_set_sec`, `tst_variant`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.setup`, `.tcnt`, `.test`, `.test_variants`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 18 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_timedsend` syscall test directory. shared mq_timed helper variants for libc/time64 syscalls, POSIX queues, signals, timeouts, full queue setup, and child isolation for bad pointers.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedsend/mq_timedsend01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/Makefile

## Purpose
This file builds mq_unlink tests with pthread and realtime library linkage.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `LDLIBS			+= -lpthread -lrt`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_unlink` syscall test directory. POSIX message queues, root/nobody credentials, long queue-name boundary cases, and mqueue cleanup.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/mq_unlink01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/mq_unlink01.c

## Purpose
This file mq_unlink matrix covering successful unlink, permission denial as nobody, missing long queue names, and ENAMETOOLONG.
The source-level description states or implies: Copyright (c) Crackerjack Project., 2007-2008 ,Hitachi, Ltd Author(s): Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Copyright (c) 2016 Linux Test Project

## Important APIs, Types, and Functions
Key local functions: `setup()`, `do_test()`.
Primary syscall/API surface: `mq_unlink`.
LTP and helper APIs used include: `SAFE_GETPWNAM`, `SAFE_MQ_OPEN`, `TEST`, `mq_unlink`, `seteuid`, `tst_res`, `tst_safe_posix_ipc`, `tst_strerrno`, `tst_test`.
Harness fields present in `struct tst_test`: `.needs_root`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 5 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; effective uid changes between root and nobody; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_unlink` syscall test directory. POSIX message queues, root/nobody credentials, long queue-name boundary cases, and mqueue cleanup.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/mq_unlink01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/Makefile

## Purpose
This file builds mremap tests, links mremap04 with the LTP IPC library, and links mremap07 with pthreads.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `LTPLIBS = ipc`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap01.c

## Purpose
This file legacy positive mremap expansion of a shared file mapping followed by writes and msync.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`, `munmap`, `msync`, `mremap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `mmap`, `mremap`, `msync`, `munmap`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap02.c

## Purpose
This file legacy negative mremap test for an unaligned old address expecting EINVAL.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `munmap`, `mremap`.
LTP and helper APIs used include: `mremap`, `munmap`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap03.c

## Purpose
This file legacy negative mremap test for an unmapped old region expecting EFAULT.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `munmap`, `mremap`.
LTP and helper APIs used include: `mremap`, `munmap`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_get_bad_addr`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap04.c

## Purpose
This file legacy negative mremap test for expansion without MREMAP_MAYMOVE when a SysV shared mapping cannot grow in place.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `munmap`, `mremap`.
LTP and helper APIs used include: `mremap`, `munmap`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap05.c

## Purpose
This file MREMAP_FIXED matrix for missing MAYMOVE, unaligned target, overlapping ranges, moving data, and replacing an existing target mapping.
The source-level description states or implies: Copyright (C) 2012 Linux Test Project, Inc. This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Further, this

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `setup0()`, `setup1()`, `setup2()`, `setup3()`, `setup4()`, `cleanup0()`, `cleanup1()`, `free_test_area()`, `test_mremap()`, `setup0()`, `setup1()`, `setup2()`, `setup3()`, `setup4()`, `cleanup0()`, `cleanup1()`.
Primary syscall/API surface: `mmap`, `mremap`.
LTP and helper APIs used include: `SAFE_MUNMAP`, `mmap`, `mremap`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`.
Harness fields present in `struct tst_test`: `.cleanup`, `.setup`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap06.c

## Purpose
This file regression test for vm_pgoff correctness when mremap fixed moves merge back into file-backed VMAs.
The source-level description states or implies: Bug reproducer for 7e7757876f25 ("mm/mremap: fix vm_pgoff in vma_merge() case 3")

## Important APIs, Types, and Functions
Key local functions: `check_pages()`, `do_test()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`, `mremap`, `mprotect`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `mmap`, `mprotect`, `mremap`, `tst_brk`, `tst_fs_type`, `tst_res`, `tst_safe_macros`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.tags`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 4 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap07.c

## Purpose
This file MREMAP_DONTUNMAP plus userfaultfd test proving old-address faults are handled by copying data from the new mapping.
The source-level description states or implies: LTP test case for mremap() with MREMAP_DONTUNMAP and userfaultfd. Test mremap() with MREMAP_DONTUNMAP and verify that accessing the old memory region triggers a page fault, which is then correctly handled by a userfaultfd handler.

## Important APIs, Types, and Functions
Key local functions: `check_mremap_dontunmap()`, `setup()`, `cleanup()`, `run()`.
Primary syscall/API surface: `mmap`, `mremap`, `userfaultfd`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_IOCTL`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_READ`, `SAFE_USERFAULTFD`, `TST_EXP_EQ_STR`, `mmap`, `mremap`, `pthread_t`, `tst_brk`, `tst_res`, `tst_safe_pthread`, `tst_test`, `userfaultfd`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_checkpoints`, `.needs_kconfigs`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls; It relies on CONFIG_USERFAULTFD, checkpoint ordering, and a nonblocking userfaultfd handler; races would produce hangs or false failures..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mseal/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mseal/Makefile

## Purpose
This file builds mseal tests through generic LTP syscall test rules; this work item only covers the build leaf, not the numbered mseal sources.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
There are no local compiler or linker overrides beyond the common LTP leaf rules.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes build variables only; no runtime persistence. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mseal` syscall test directory. LTP generic syscall build infrastructure for the mseal directory.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mseal/Makefile -->
