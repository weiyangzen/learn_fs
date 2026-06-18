# Group research: subset-b-009307

This grouped report covers 120 source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit02.c

## Purpose
Testcase to test the different errnos set by :manpage:`setrlimit(2)` system call.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setrlimit`; types `struct rlimit`, `struct
tcase`, `struct passwd`, `struct tst_test`; constants/macros `RLIMIT_NOFILE`; safe wrappers
`SAFE_GETPWNAM`, `SAFE_SETUID`, `SAFE_GETRLIMIT`; harness APIs `tst_test`, `TEST`, `tst_res`,
`tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`. Local functions include `verify_setrlimit`, `setup`.

## State and persistence behavior
The test changes process credentials for the running process or child; changes resource limits in
the current process or child process. State is scoped to the LTP process tree unless a privileged
syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EINVAL`,
`EPERM`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit03.c

## Purpose
Test :manpage:`setrlimit(2)` errnos: - EPERM when the super-user tries to increase RLIMIT_NOFILE
beyond the system limit. - EINVAL when rlim->rlim_cur is greater than rlim->rlim_max.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setrlimit`; types `struct rlimit`, `struct
tcase`, `struct tst_test`; constants/macros `RLIMIT_NOFILE`; safe wrappers `SAFE_FILE_SCANF`,
`SAFE_GETRLIMIT`; harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`. Local functions include `verify_setrlimit`, `setup`.

## State and persistence behavior
The test changes resource limits in the current process or child process. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, Linux UAPI headers. The file is
built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EPERM`,
`EINVAL`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit04.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit04.c

## Purpose
Attempt to run a trivial binary with stack < 1MB. Early patches for stack guard gap caused that gap
size was contributing to stack limit. This caused failures for new processes (E2BIG) when ulimit was
set to anything lower than size of gap. Kernel commit 1be7107fbe18 ("mm: largerstack guard gap,
between vmas") from v4.12 sets default gap size to 1M (for systems with 4k pages), so let's set
stack limit to 512kB and confirm we can still run some trivial binary. Referenced kernel commit ids
include `1be7107fbe18`.

## Important APIs, types, and functions
Important interfaces include types `struct rlimit`, `struct tst_test`; constants/macros
`RLIMIT_STACK`; safe wrappers `SAFE_SETRLIMIT`, `SAFE_FORK`, `SAFE_EXECLP`, `SAFE_WAITPID`; harness
APIs `tst_test`, `tst_res`, `tst_strstatus`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`,
`.forks_child`, `.needs_root`. Local functions include `test_setrlimit`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes resource limits in
the current process or child process. State is scoped to the LTP process tree unless a privileged
syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`; expected errno/status values `E2BIG`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit05.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit05.c

## Purpose
Test :manpage:`setrlimit(2)` for EFAULT when rlim points outside the accessible address space.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setrlimit`; types `struct rlimit`, `struct
tst_test`; constants/macros `RLIMIT_NOFILE`, `SIGSEGV`; safe wrappers `SAFE_FORK`, `SAFE_WAITPID`;
harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strstatus`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.forks_child`. Local functions include `verify_setrlimit`, `setup`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes resource limits in
the current process or child process. State is scoped to the LTP process tree unless a privileged
syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EFAULT`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit06.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit06.c

## Purpose
Set CPU time limit for a process and check its behavior after reaching CPU time limit - Process got
SIGXCPU after reaching soft limit of CPU time - Process got SIGKILL after reaching hard limit of CPU
time Test is also a regression test for kernel bug from v4.17: c3bca5d450b62 ("posix-cpu-timers:
Ensure set_process_cpu_timer is always evaluated"). Referenced kernel commit ids include
`c3bca5d450b62`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setrlimit`, `setrlimit_u64`, `alarm`; types
`struct rlimit`, `struct rlimit64`, `struct tst_test`, `struct tst_buffers`, `struct tst_tag`;
constants/macros `SIGXCPU`, `SIGKILL`, `RLIMIT_CPU`, `SIGALRM`; safe wrappers `SAFE_SIGNAL`,
`SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_FORK`, `SAFE_WAITPID`; harness APIs `tst_test`, `tst_variant`,
`TEST`, `tst_res`, `tst_strstatus`, `tst_buffers`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`, `.test_variants`, `.forks_child`. Local functions include `sighandler`,
`setup`, `cleanup`, `verify_setrlimit`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; maps or protects temporary
memory for buffers, alternate stacks, or coordination; changes resource limits in the current
process or child process. State is scoped to the LTP process tree unless a privileged syscall
changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, LTP syscall ABI variants. The file is built by
the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsid/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsid/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `setsid`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsid/setsid01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsid/setsid01.c

## Purpose
Test to check the error and trivial conditions in setsid system call USAGE setsid01 RESTRICTIONS
This test doesn't follow good LTP format - PLEASE FIX!

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsid`, `setpgid`, `wait`, `kill`;
constants/macros `SIGKILL`; harness APIs `tst_parse_opts`, `tst_count`, `tst_fork`, `tst_resm`,
`tst_exit`, `tst_brkm`, `tst_sig`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include
`do_child_1`, `do_child_2`, `setup`, `cleanup`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`; expected errno/status values `EPERM`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsid/setsid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `setsockopt`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `setsockopt06 setsockopt07:	CFLAGS += -pthread`; `setsockopt06 setsockopt07:	LDLIBS += -lrt`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt01.c

## Purpose
Verify that setsockopt() fails and set errno: - EBADF on invalid file descriptor - ENOTSOCK on non-
socket file descriptor - EFAULT on invalid option buffer - EINVAL on invalid optlen - ENOPROTOOPT on
invalid level - ENOPROTOOPT on invalid option name (UDP) - ENOPROTOOPT on invalid option name (IP) -
ENOPROTOOPT on invalid option name (TCP).

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct sockaddr_in`, `struct
test_case`, `struct sockaddr`, `struct tst_test`; constants/macros `SOL_SOCKET`, `SO_OOBINLINE`,
`AF_INET`; safe wrappers `SAFE_OPEN`, `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_CLOSE`; harness APIs
`tst_test`, `tst_res`, `TEST`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`.
Local functions include `setup`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TINFO`, `TTERRNO`, `TERRNO`; expected errno/status values
`EBADF`, `ENOTSOCK`, `EFAULT`, `EINVAL`, `ENOPROTOOPT`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt02.c

## Purpose
Test for CVE-2017-7308 on a raw socket's ring buffer Try to set tpacket_req3.tp_sizeof_priv to a
value with the high bit set. So that tp_block_size < tp_sizeof_priv. If the vulnerability is present
then this will cause an integer arithmetic overflow and the absurd tp_sizeof_priv value will be
allowed. If it has been fixed then setsockopt will fail with EINVAL. We also try a good
configuration to make sure it is not failing with EINVAL for some other reason. For a better and
more interesting discussion of this CVE see:
https://googleprojectzero.blogspot.com/2017/05/exploiting-linux-kernel-via-packet.html.
CVE/regression focus: CVE-2017-7308.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct tpacket_req3`,
`struct tst_test`, `struct tst_tag`; constants/macros `TPACKET_V3`, `AF_PACKET`, `SOL_PACKET`,
`PACKET_VERSION`, `PACKET_RX_RING`; safe wrappers `SAFE_SYSCONF`, `SAFE_CLOSE`, `SAFE_SOCKET`;
harness APIs `tst_test`, `tst_safe_net`, `TEST`, `tst_brk`, `tst_res`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_root`. Local functions include `setup`, `cleanup`, `create_skbuf`,
`good_size`, `bad_size`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; privilege assumptions can produce `TCONF`/`TBROK` instead of
meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status
values `EINVAL`; regression tags for CVE-2017-7308.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt03.c

## Purpose
Test for CVE-2016-4997 For a full explanation of how the vulnerability works see:
https://github.com/nccgroup/TriforceLinuxSyscallFuzzer/tree/master/crash_reports/report_compatIpt
The original vulnerability was present in the 32-bit compatibility system call, so the test should
be compiled with -m32 and run on a 64-bit kernel. For simplicities sake the test requests root
privileges instead of creating a user namespace. CVE/regression focus: CVE-2016-4997. Referenced
kernel commit ids include `ce683e5f9d04`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct ipt_entry`, `struct
xt_entry_match`, `struct xt_entry_target`, `struct payload`, `struct ipt_replace`, `struct
tst_test`, `struct tst_tag`; constants/macros `AF_INET`, `SOL_IP`; safe wrappers `SAFE_SOCKET`;
harness APIs `tst_test`, `tst_safe_net`, `tst_kernel`, `tst_is_compat_mode`, `tst_res`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_root`. Local functions include `setup`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; compatibility-mode behavior depends on architecture, compiler
flags, and kernel ABI support; privilege assumptions can produce `TCONF`/`TBROK` instead of
meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TINFO`, `TERRNO`; regression tags for CVE-2016-4997.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt04.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt04.c

## Purpose
CVE-2016-9793 With kernels between version 3.11 and 4.8 missing commit b98b0bc8 it is possible to
pass a very high unsigned integer as send buffer size to a socket which is then interpreted as a
negative value. This can be used to escalate privileges by every user that has the CAP_NET_ADMIN
capability. For additional information about this CVE see:
https://www.suse.com/security/cve/CVE-2016-9793/. CVE/regression focus: CVE-2016-9793. Referenced
kernel commit ids include `b98b0bc8c431`.

## Important APIs, types, and functions
Important interfaces include types `struct tst_test`, `struct tst_tag`; constants/macros
`SOL_SOCKET`, `SO_SNDBUFFORCE`, `SO_SNDBUF`, `AF_INET`; safe wrappers `SAFE_SETSOCKOPT`,
`SAFE_GETSOCKOPT`, `SAFE_SOCKET`, `SAFE_CLOSE`; harness APIs `tst_test`, `tst_safe_net`, `tst_res`,
`tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`, `.needs_root`. Local functions include `run`, `setup`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; privilege assumptions can produce `TCONF`/`TBROK` instead of
meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TINFO`; regression tags for CVE-2016-9793.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt05.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt05.c

## Purpose
CVE-2017-1000112 Check that UDP fragmentation offload doesn't cause memory corruption if the
userspace process turns off UFO in between two send() calls. Kernel crash fixed in 4.13 85f1bd9a7b5a
("udp: consistently apply ufo or fragmentation"). CVE/regression focus: CVE-2017-1000112. Referenced
kernel commit ids include `85f1bd9a7b5a`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `send`; types `struct sockaddr_in`, `struct
ifreq`, `struct sockaddr`, `struct tst_test`, `struct tst_path_val`, `struct tst_tag`;
constants/macros `AF_INET`, `SIOCSIFMTU`, `SIOCSIFFLAGS`, `SOL_SOCKET`, `SO_NO_CHECK`; safe wrappers
`SAFE_SOCKET`, `SAFE_IOCTL`, `SAFE_BIND`, `SAFE_GETSOCKNAME`, `SAFE_CLOSE`, `SAFE_CONNECT`,
`SAFE_SEND`, `SAFE_SETSOCKOPT_INT`; harness APIs `tst_test`, `tst_net`, `tst_setup_netns`,
`tst_init_sockaddr_inet_bin`, `tst_taint_check`, `tst_res`, `tst_path_val`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `cleanup`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, kernel config gates "CONFIG_USER_NS=y",
"CONFIG_NET_NS=y". The file is built by the syscall directory Makefile and executed as part of the
LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; missing kernel options cause configuration skips rather than
failures.

## Test signals
LTP result macros `TPASS`, `TFAIL`; regression tags for CVE-2017-1000112.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt06.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt06.c

## Purpose
CVE-2016-8655 Check for race condition between packet_set_ring() and tp_version. On some kernels,
this may lead to use-after-free. Kernel crash fixed in 4.9 84ac7260236a ("packet: fix race condition
in packet_set_ring"). CVE/regression focus: CVE-2016-8655. Referenced kernel commit ids include
`84ac7260236a`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct tst_fzsync_pair`,
`struct tpacket_req3`, `struct tst_test`, `struct tst_path_val`, `struct tst_tag`; constants/macros
`SOL_PACKET`, `PACKET_RX_RING`, `TPACKET_V1`, `TPACKET_V3`, `AF_PACKET`, `PACKET_VERSION`; safe
wrappers `SAFE_SYSCONF`, `SAFE_SOCKET`, `SAFE_CLOSE`; harness APIs `tst_test`, `tst_fuzzy_sync`,
`tst_fzsync_pair`, `tst_setup_netns`, `tst_fzsync_pair_init`, `tst_fzsync_run_b`,
`tst_fzsync_start_race_b`, `tst_fzsync_end_race_b`, `tst_fzsync_pair_add_bias`,
`tst_fzsync_pair_reset`, `tst_fzsync_run_a`, `TEST`, `tst_brk`, `tst_fzsync_start_race_a`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `run`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, kernel config gates "CONFIG_USER_NS=y",
"CONFIG_NET_NS=y". The file is built by the syscall directory Makefile and executed as part of the
LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; race reproduction is timing-sensitive and can be flaky on slow or
heavily loaded systems; missing kernel options cause configuration skips rather than failures;
signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status
values `EINVAL`; regression tags for CVE-2016-8655.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt07.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt07.c

## Purpose
CVE-2017-1000111 Check for race condition between packet_set_ring() and tp_reserve. The race allows
you to set tp_reserve bigger than ring buffer size. While this will cause truncation of all incoming
packets to 0 bytes, sanity checks in tpacket_rcv() prevent any exploitable buffer overflows. Race
fixed in v4.13 c27927e372f0 ("packet: fix tp_reserve race in packet_set_ring"). CVE/regression
focus: CVE-2017-1000111. Referenced kernel commit ids include `c27927e372f0`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct tst_fzsync_pair`,
`struct tpacket_req3`, `struct tst_test`, `struct tst_path_val`, `struct tst_tag`; constants/macros
`SOL_PACKET`, `PACKET_RESERVE`, `TPACKET_V3`, `AF_PACKET`, `PACKET_VERSION`, `PACKET_RX_RING`; safe
wrappers `SAFE_SYSCONF`, `SAFE_SOCKET`, `SAFE_GETSOCKOPT`, `SAFE_CLOSE`; harness APIs `tst_test`,
`tst_fuzzy_sync`, `tst_fzsync_pair`, `tst_setup_netns`, `tst_fzsync_pair_init`, `tst_fzsync_run_b`,
`tst_fzsync_start_race_b`, `tst_fzsync_end_race_b`, `tst_fzsync_pair_reset`, `tst_fzsync_run_a`,
`TEST`, `tst_brk`, `tst_fzsync_start_race_a`, `tst_fzsync_end_race_a`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `run`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, kernel config gates "CONFIG_USER_NS=y",
"CONFIG_NET_NS=y". The file is built by the syscall directory Makefile and executed as part of the
LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; race reproduction is timing-sensitive and can be flaky on slow or
heavily loaded systems; missing kernel options cause configuration skips rather than failures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status
values `EINVAL`; regression tags for CVE-2017-1000111.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt08.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt08.c

## Purpose
This will reproduce the bug on x86_64 in 32bit compatibility mode. It is most reliable with KASAN
enabled. Otherwise it relies on the out-of-bounds write corrupting something which leads to a crash.
It will run in other scenarious, but is not a test for the CVE. See
https://google.github.io/security-research/pocs/linux/cve-2021-22555/writeup.html Also below is
Nicolai's detailed description of the bug itself. The problem underlying CVE-2021-22555 fixed by
upstream commit b29c457a6511 ("netfilter: x_tables: fix compat match/target pad out-of-bound write")
is that the (now removed) padding zeroing code in xt_compat_target_from_user() had been based on the
premise that the user specified. CVE/regression focus: CVE-2021-22555. Referenced kernel commit ids
include `b29c457a6511`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct compat_ipt_replace`,
`struct xt_entry_target`, `struct ipt_replace`, `struct ipt_entry`, `struct xt_entry_match`, `struct
tst_test`, `struct tst_buffers`, `struct tst_path_val`, `struct tst_tag`; constants/macros
`AF_INET`; safe wrappers `SAFE_SOCKET`, `SAFE_CLOSE`; harness APIs `tst_test`, `tst_safe_net`,
`tst_is_compat_mode`, `tst_res`, `tst_setup_netns`, `TEST`, `tst_brk`, `tst_buffers`,
`tst_path_val`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.forks_child`. Local functions include `setup`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, kernel config gates
"CONFIG_NETFILTER_XT_MATCH_STATE", "CONFIG_IP_NF_TARGET_REJECT", "CONFIG_USER_NS=y",
"CONFIG_NET_NS=y". The file is built by the syscall directory Makefile and executed as part of the
LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; compatibility-mode behavior depends on architecture, compiler
flags, and kernel ABI support; missing kernel options cause configuration skips rather than
failures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`; expected errno/status
values `ENOPROTOOPT`, `EINVAL`; regression tags for CVE-2021-22555.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt09.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt09.c

## Purpose
Check for possible double free of rx_owner_map after switching packet interface versions aka
CVE-2021-22600. Kernel crash fixed in: commit ec6af094ea28f0f2dda1a6a33b14cd57e36a9755 Author:
Willem de Bruijn <willemb@google.com> Date: Wed Dec 15 09:39:37 2021 -0500 net/packet: rx_owner_map
depends on pg_vec commit c800aaf8d869f2b9b47b10c5c312fe19f0a94042 Author: WANG Cong
<xiyou.wangcong@gmail.com> Date: Mon Jul 24 10:07:32 2017 -0700 packet: fix use-after-free in
prb_retire_rx_blk_timer_expired(). CVE/regression focus: CVE-2021-22600. Referenced kernel commit
ids include `ec6af094ea28f0f2dda1a6a33b14cd57e36a9755`, `c800aaf8d869f2b9b47b10c5c312fe19f0a94042`,
`ec6af094ea28`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct tpacket_req3`,
`struct tst_test`, `struct tst_path_val`, `struct tst_tag`; constants/macros `TPACKET_V3`,
`TPACKET_ALIGNMENT`, `AF_PACKET`, `SOL_PACKET`, `PACKET_VERSION`, `PACKET_RX_RING`, `TPACKET_V2`;
safe wrappers `SAFE_SYSCONF`, `SAFE_SOCKET`, `SAFE_SETSOCKOPT`, `SAFE_SETSOCKOPT_INT`, `SAFE_CLOSE`;
harness APIs `tst_test`, `tst_setup_netns`, `TEST`, `tst_brk`, `tst_taint_check`, `tst_res`,
`tst_path_val`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `run`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, kernel config gates "CONFIG_USER_NS=y",
"CONFIG_NET_NS=y". The file is built by the syscall directory Makefile and executed as part of the
LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; missing kernel options cause configuration skips rather than
failures; signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status
values `EINVAL`; regression tags for CVE-2021-22600.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt10.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt10.c

## Purpose
Reproducer for CVE-2023-0461 which is an exploitable use-after-free in a TLS socket. In fact it is
exploitable in any User Level Protocol (ULP) which does not clone its context when accepting a
connection. Because it does not clone the context, the child socket which is created on accept has a
pointer to the listening socket's context. When the child is closed the parent's context is freed
while it still has a reference to it. TLS can only be added to a socket which is connected. Not
listening or disconnected, and a connected socket can not be set to listening. So we have to connect
the socket, add TLS, then disconnect, then set it to listening. To my knowledge, setting a socket
from open. CVE/regression focus: CVE-2023-0461. Referenced kernel commit ids include
`2c02d41d71f90a5168391b6a5f2954112ba2307c`, `2c02d41d71f90`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`, `connect`; types `struct
tls12_crypto_info_aes_gcm_128`, `struct sockaddr_in`, `struct sockaddr`, `struct tst_test`, `struct
tst_tag`; constants/macros `AF_UNSPEC`, `AF_INET`, `SOL_TCP`, `SOL_TLS`; safe wrappers `SAFE_CLOSE`,
`SAFE_SOCKET`, `SAFE_BIND`, `SAFE_LISTEN`, `SAFE_ACCEPT`, `SAFE_FORK`, `SAFE_CONNECT`,
`SAFE_SETSOCKOPT`; harness APIs `tst_test`, `tst_checkpoint`, `tst_net`, `tst_safe_net`,
`tst_taint`, `tst_init_sockaddr_inet`, `tst_res`, `TEST`, `tst_brk`, `tst_reap_children`,
`tst_flush`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`, `.forks_child`. Local functions include `setup`, `cleanup`, `child`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths; uses child
processes and wait/exit status as observable state. State is scoped to the LTP process tree unless a
privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, kernel config gates "CONFIG_TLS",
`lapi/socket.h` compatibility wrappers, Linux UAPI headers. The file is built by the syscall
directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; missing kernel options cause configuration skips rather than
failures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`; expected
errno/status values `EINVAL`, `ENOENT`, `EOPNOTSUPP`; regression tags for CVE-2023-0461.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `settimeofday`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/settimeofday01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/settimeofday01.c

## Purpose
This LTP test source exercises `settimeofday` syscall behavior in `settimeofday01.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `settimeofday`, `gettimeofday`; types `struct
timeval`, `struct tst_test`; harness APIs `tst_test`, `tst_brk`, `TEST`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`,
`.needs_root`. Local functions include `verify_settimeofday`.

## State and persistence behavior
The test may alter system clock state, so setup/cleanup must preserve host time expectations. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, `lapi/syscalls.h` compatibility
wrappers. The file is built by the syscall directory Makefile and executed as part of the LTP kernel
syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TTERRNO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/settimeofday01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/settimeofday02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/settimeofday02.c

## Purpose
This LTP test source exercises `settimeofday` syscall behavior in `settimeofday02.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `settimeofday`; types `struct tcase`, `struct
timeval`, `struct tst_test`, `struct tst_cap`; harness APIs `tst_capability`, `tst_test`, `tst_res`,
`TST_EXP_FAIL`, `tst_cap`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `verify_settimeofday`.

## State and persistence behavior
The test may alter system clock state, so setup/cleanup must preserve host time expectations. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/syscalls.h` compatibility wrappers. The
file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TINFO`; expected errno/status values `EINVAL`, `EPERM`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/settimeofday02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setuid/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setuid/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `setuid`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setuid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid01.c

## Purpose
Verify that setuid(2) returns 0 and effective uid has been set successfully as a normal or super
user.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setuid`; types `struct tst_test`; harness APIs
`tst_test`, `TST_EXP_PASS`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`. Local
functions include `verify_setuid`.

## State and persistence behavior
The test changes process credentials for the running process or child. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: compatibility-mode behavior depends on architecture, compiler flags, and kernel ABI
support.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid03.c

## Purpose
This test will switch to nobody user for correct error code collection. Verify setuid returns errno
EPERM when it switches to root_user.

## Important APIs, types, and functions
Important interfaces include types `struct passwd`, `struct tst_test`; safe wrappers
`SAFE_GETPWNAM`, `SAFE_SETUID`; harness APIs `tst_test`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_root`. Local functions include `verify_setuid`, `setup`.

## State and persistence behavior
The test changes process credentials for the running process or child. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: compatibility-mode behavior depends on architecture, compiler flags, and kernel ABI
support; privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
expected errno/status values `EPERM`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid04.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid04.c

## Purpose
Check if setuid behaves correctly with file permissions. The test creates a file as ROOT with
permissions 0644, does a setuid and then tries to open the file with RDWR permissions. The same test
is done in a fork to check if new UIDs are correctly passed to the son.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setuid`, `open`, `close`; types `struct passwd`,
`struct tst_test`; safe wrappers `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_TOUCH`; harness APIs
`tst_test`, `tst_fd`, `TEST`, `tst_res`, `tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.forks_child`, `.needs_root`, `.needs_tmpdir`. Local functions include `dosetuid`,
`verify_setuid`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount;
changes process credentials for the running process or child; uses child processes and wait/exit
status as observable state. State is scoped to the LTP process tree unless a privileged syscall
changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: compatibility-mode behavior depends on architecture, compiler flags, and kernel ABI
support; privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TTERRNO`, `TERRNO`; expected errno/status values
`EACCES`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `setxattr`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr01.c

## Purpose
Tests for setxattr(2) and make sure setxattr(2) handles error conditions correctly. - EINVAL - any
other flags being set except XATTR_CREATE and XATTR_REPLACE - ENODATA - with XATTR_REPLACE flag set
but the attribute does not exist - ERANGE - create new attr with name length greater than
XATTR_NAME_MAX(255) - E2BIG - create new attr whose value length is greater than
XATTR_SIZE_MAX(65536) - SUCCEED - create new attr whose value length is zero - EEXIST - replace the
attr value without XATTR_REPLACE flag being set - SUCCEED - replace attr value with XATTR_REPLACE
flag being set - ERANGE - create new attr whose key length is zero - EFAULT - create new attr whose
key is NULL.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setxattr`; types `struct test_case`, `struct
tst_test`; safe wrappers `SAFE_SETXATTR`, `SAFE_REMOVEXATTR`, `SAFE_MALLOC`, `SAFE_TOUCH`; harness
APIs `tst_test`, `TEST`, `tst_brk`, `tst_res`, `tst_strerrno`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`. Local functions include `verify_setxattr`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields; invalid-
address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status values
`EINVAL`, `ENODATA`, `ERANGE`, `E2BIG`, `EEXIST`, `EFAULT`, `EOPNOTSUPP`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr02.c

## Purpose
In the user.* namespace, only regular files and directories can have extended attributes. Otherwise
setxattr(2) will return -1 and set errno to EPERM. - SUCCEED - set attribute to a regular file -
SUCCEED - set attribute to a directory - EEXIST - set attribute to a symlink which points to the
regular file - EPERM - set attribute to a FIFO - EPERM - set attribute to a char special file -
EPERM - set attribute to a block special file - EPERM/SUCCEED - set attribute to a UNIX domain
socket (dc0876b9846d "xattr: support extended attributes on sockets"). Referenced kernel commit ids
include `dc0876b9846d`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socket`, `setxattr`; types `struct test_case`,
`struct tst_test`; constants/macros `S_IFIFO`, `S_IFCHR`, `S_IFBLK`, `S_IFSOCK`; safe wrappers
`SAFE_SETXATTR`, `SAFE_REMOVEXATTR`, `SAFE_TOUCH`, `SAFE_MKDIR`, `SAFE_SYMLINK`, `SAFE_MKNOD`;
harness APIs `tst_test`, `TEST`, `tst_brk`, `tst_res`, `tst_strerrno`, `tst_kvercmp`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`, `.needs_tmpdir`. Local functions include `verify_setxattr`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status values
`EPERM`, `EEXIST`, `EOPNOTSUPP`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr03.c

## Purpose
setxattr(2) to immutable and append-only files should get EPERM - Set attribute to a immutable file
- Set attribute to a append-only file.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `ioctl`, `setxattr`; types `struct test_case`,
`struct tst_test`; safe wrappers `SAFE_CREAT`, `SAFE_CLOSE`, `SAFE_UNLINK`; harness APIs `tst_test`,
`TEST`, `tst_res`, `tst_strerrno`, `tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_root`, `.needs_tmpdir`. Local functions include `verify_setxattr`,
`fsetflag`, `setup`, `cleanup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TWARN`, `TTERRNO`, `TERRNO`; expected
errno/status values `EPERM`, `ENOTSUP`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sgetmask/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sgetmask/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sgetmask`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sgetmask/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sgetmask/sgetmask01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sgetmask/sgetmask01.c

## Purpose
NOTE: This case test the behavior of sgetmask # Sometime the returned "Oops"in this case don't mean
anything for # correct or error, we check the result between different kernel and # try to find if
there exist different returned code in different kernel #.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sgetmask`, `ssetmask`; constants/macros
`SIGRTMAX`; harness APIs `tst_exit`, `tst_rmdir`, `tst_tmpdir`, `tst_parse_opts`, `tst_count`,
`TEST`, `tst_syscall`, `tst_resm`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `cleanup`,
`setup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, temporary directory support, `lapi/syscalls.h`
compatibility wrappers. The file is built by the syscall directory Makefile and executed as part of
the LTP kernel syscall suite.

## Risks and edge cases
Key risks: obsolete or direct syscall paths may be absent or emulated differently on newer
architectures.

## Test signals
LTP result macros `TPASS`, `TINFO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sgetmask/sgetmask01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `shutdown`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/shutdown01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/shutdown01.c

## Purpose
This test verifies the following shutdown() functionalities: - SHUT_RD should enable send() ops but
disable recv() ops - SHUT_WR should enable recv() ops but disable send() ops - SHUT_RDWR should
disable both recv() and send() ops.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `send`, `recv`, `shutdown`; types `struct tcase`,
`struct sockaddr_un`, `struct sockaddr`, `struct tst_test`, `struct tst_buffers`; constants/macros
`AF_UNIX`; safe wrappers `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_LISTEN`, `SAFE_CLOSE`, `SAFE_UNLINK`,
`SAFE_FORK`, `SAFE_CONNECT`, `SAFE_RECV`, `SAFE_SEND`; harness APIs `tst_test`, `tst_safe_net`,
`tst_res`, `TST_EXP_PASS`, `TST_EXP_FAIL`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.forks_child`. Local functions include `run_server`, `start_test`, `run`, `setup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths; uses child
processes and wait/exit status as observable state. State is scoped to the LTP process tree unless a
privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TINFO`; expected errno/status values `EWOULDBLOCK`, `EPIPE`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/shutdown01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/shutdown02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/shutdown02.c

## Purpose
This test verifies the following shutdown() errors: - EBADF sockfd is not a valid file descriptor -
EINVAL An invalid value was specified in how - ENOTCONN The specified socket is not connected -
ENOTSOCK The file descriptor sockfd does not refer to a socket.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `shutdown`; types `struct sockaddr_in`, `struct
tcase`, `struct sockaddr`, `struct tst_test`, `struct tst_buffers`; constants/macros `AF_INET`; safe
wrappers `SAFE_OPEN`, `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_CLOSE`; harness APIs `tst_test`,
`TST_EXP_FAIL`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `run`, `setup`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
expected errno/status values `EBADF`, `EINVAL`, `ENOTCONN`, `ENOTSOCK`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/shutdown02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigaction`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `CFLAGS			+= -DGLIBC_SIGACTION_BUG=1 -D_GNU_SOURCE`; `LDLIBS			+= -lpthread`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/sigaction01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/sigaction01.c

## Purpose
Test some features of sigaction (see below for more details) ALGORITHM Use sigaction(2) to set a
signal handler for SIGUSR1 with a certain set of flags, set a global variable indicating the test
case, and finally send the signal to ourselves, causing the signal handler to run. The signal
handler then checks the signal handler to run. The signal handler then checks certain conditions
based on the test case number. There are 4 test cases: 1) Set SA_RESETHAND and SA_SIGINFO. When the
handler runs, SA_SIGINFO should be set. 2) Set SA_RESETHAND. When the handler runs, SIGUSR1 should
be masked (SA_RESETHAND makes sigaction behave as if SA_NODEFER was not set). 3) Same as case #2,
but when the.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigemptyset`, `sigaddset`,
`sigprocmask`, `kill`; types `struct sigaction`; constants/macros `SIGUSR1`, `SIG_BLOCK`; harness
APIs `tst_resm`, `TEST`, `tst_parse_opts`, `tst_count`, `tst_brkm`, `tst_exit`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `handler`, `set_handler`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TWARN`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/sigaction01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/sigaction02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/sigaction02.c

## Purpose
Testcase to check the basic errnos set by the sigaction(2) syscall. ALGORITHM 1. Pass an invalid
signal as the "sig" parameter, and expect EINVAL. 2. Attempt to catch the SIGKILL, and expect
EINVAL. 3. Attempt to catch the SIGSTOP, and expect EINVAL. 4. Pass an invalid address as the "act"
parameter, expect an EFAULT. 5. Pass an invalid address as the "oact" parameter, and expect EFAULT.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigemptyset`, `sigaddset`; types
`struct sigaction`; constants/macros `SIGKILL`, `SIGSTOP`, `SIGBAD`, `SIGUSR1`; harness APIs
`tst_resm`, `tst_parse_opts`, `tst_exit`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `handler`, `set_handler`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing; invalid-address tests can
expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TINFO`; expected errno/status values `EINVAL`, `EFAULT`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/sigaction02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigaltstack`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/sigaltstack01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/sigaltstack01.c

## Purpose
Test Name: sigalstack01 Send a signal using the main stack. While executing the signal handler
compare a variable's address lying on the main stack with the stack boundaries returned by
sigaltstack(). Expected result: sigaltstack() should succeed to get/set signal alternate stack
context. Algorithm: Setup: Setup signal handling. Pause for SIGUSR1 if option specified. Test: Loop
if the proper options are given. Execute system call Check return code, if system call failed
(return=-1) Log the errno and Issue a FAIL message. Otherwise, Verify the Functionality of system
call if successful, Issue Functionality-Pass message. Otherwise, Issue Functionality-Fail message.
Cleanup: Print errno log.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigaltstack`, `kill`; types `struct
sigaction`; constants/macros `SIGUSR1`, `SIGSTKSZ`, `SIGUSER1`; harness APIs `tst_parse_opts`,
`tst_count`, `TEST`, `tst_resm`, `tst_brkm`, `tst_exit`, `tst_sig`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `sig_handler`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/sigaltstack01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/sigaltstack02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/sigaltstack02.c

## Purpose
Verify that sigaltstack() fails with return value -1 and set expected errno: - EINVAL on invalid
value. - ENOMEM on stack is < MINSIGSTKSZ.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaltstack`; types `struct test_case`, `struct
tst_test`; constants/macros `SIGSTKSZ`; safe wrappers `SAFE_MALLOC`; harness APIs `tst_test`,
`TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `check_sigaltstack`, `setup`, `cleanup`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
expected errno/status values `EINVAL`, `ENOMEM`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/sigaltstack02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sighold/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sighold/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sighold`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sighold/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sighold/sighold02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sighold/sighold02.c

## Purpose
This test checks following conditions: 1. sighold action to turn off the receipt of all signals was
done without error. 2. After signals were held, and sent, no signals were trapped.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sighold`; types `struct tst_test`;
constants/macros `SIGRTMIN`, `SIGCHLD`, `SIGKILL`, `SIGALRM`, `SIGSTOP`; safe wrappers
`SAFE_SIGNAL`, `SAFE_FORK`, `SAFE_KILL`; harness APIs `tst_test`, `tst_brk`, `tst_strsig`,
`tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`,
`.forks_child`. Local functions include `skip_sig`, `handle_sigs`, `do_child`, `run`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes per-process signal
dispositions, masks, pending queues, or alternate signal stack state. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TINFO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sighold/sighold02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signal/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `signal`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `signal06: CFLAGS+=-pthread`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal01.c

## Purpose
Test SIGKILL for these items: 1. SIGKILL can not be set to be ignored, errno:EINVAL (POSIX). 2.
SIGKILL can not be reset to default, errno:EINVAL (POSIX). 3. SIGKILL can not be set to be caught,
errno:EINVAL (POSIX). 4. SIGKILL can not be ignored. 5. SIGKILL is reset to default failed but
processed by default. 6. SIGKILL can not be caught.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `signal`; types `struct tcase`, `struct
tst_test`; constants/macros `SIGKILL`, `SIG_IGN`, `SIG_DFL`; safe wrappers `SAFE_FORK`,
`SAFE_WAITPID`, `SAFE_KILL`; harness APIs `tst_test`, `TST_EXP_FAIL2`, `TST_EXP_EQ_SSZ`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`,
`.forks_child`. Local functions include `catchsig`, `do_test`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes per-process signal
dispositions, masks, pending queues, or alternate signal stack state. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TFAIL`; expected errno/status values `EINVAL`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal02.c

## Purpose
This LTP test source exercises `signal` syscall behavior in `signal02.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `signal`; types `struct tst_test`;
constants/macros `SIGKILL`, `SIGSTOP`, `SIG_IGN`; harness APIs `tst_test`, `TST_EXP_FAIL2`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `do_test`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
expected errno/status values `EINVAL`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal03.c

## Purpose
This LTP test source exercises `signal` syscall behavior in `signal03.c`.

## Important APIs, types, and functions
Important interfaces include types `struct tst_test`; constants/macros `SIGHUP`, `SIGINT`,
`SIGQUIT`, `SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGIOT`, `SIGBUS`, `SIGFPE`, `SIGUSR1`, `SIGSEGV`,
`SIGUSR2`, `SIGPIPE`, `SIGALRM`, `SIGTERM`, `SIGSTKFLT`, `SIGCHLD`, `SIGCONT`; safe wrappers
`SAFE_SIGNAL`, `SAFE_KILL`; harness APIs `tst_test`, `TST_EXP_EQ_SSZ`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `sighandler`, `do_test`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal04.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal04.c

## Purpose
This LTP test source exercises `signal` syscall behavior in `signal04.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `signal`; types `struct tst_test`;
constants/macros `SIGHUP`, `SIGINT`, `SIGQUIT`, `SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGBUS`, `SIGFPE`,
`SIGUSR1`, `SIGSEGV`, `SIGUSR2`, `SIGPIPE`, `SIGALRM`, `SIGTERM`, `SIGCHLD`, `SIGCONT`, `SIGTSTP`,
`SIGTTIN`; safe wrappers `SAFE_SIGNAL`; harness APIs `tst_test`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `sighandler`, `do_test`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal05.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal05.c

## Purpose
This LTP test source exercises `signal` syscall behavior in `signal05.c`.

## Important APIs, types, and functions
Important interfaces include types `struct tst_test`; constants/macros `SIGHUP`, `SIGINT`,
`SIGQUIT`, `SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGIOT`, `SIGBUS`, `SIGFPE`, `SIGUSR1`, `SIGSEGV`,
`SIGUSR2`, `SIGPIPE`, `SIGALRM`, `SIGTERM`, `SIGSTKFLT`, `SIGCHLD`, `SIGCONT`; safe wrappers
`SAFE_SIGNAL`, `SAFE_KILL`; harness APIs `tst_test`, `TST_EXP_EQ_SSZ`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `sighandler`, `do_test`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal06.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal06.c

## Purpose
save_xstate_sig()->drop_init_fpu() doesn't look right. setup_rt_frame() can fail after that, in this
case the next setup_rt_frame() triggered by SIGSEGV won't save fpu simply because the old state was
lost. This obviously mean that fpu won't be restored after sys_rt_sigreturn() from SIGSEGV handler.
These commits fix the issue on v3.17-rc3-3 stable kernel: commit
df24fb859a4e200d9324e2974229fbb7adf00aef Author: Oleg Nesterov <oleg@redhat.com> Date: Tue Sep 2
19:57:17 2014 +0200 commit 66463db4fc5605d51c7bb81d009d5bf30a783a2c Author: Oleg Nesterov
<oleg@redhat.com> Date: Tue Sep 2 19:57:13 2014 +0200 Reproduce: Test-case (needs -O2). Referenced
kernel commit ids include `df24fb859a4e200d9324e2974229fbb7adf00aef`,
`66463db4fc5605d51c7bb81d009d5bf30a783a2c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigaltstack`, `mprotect`,
`pthread_create`, `pthread_join`; types `struct sigaction`; constants/macros `SIGSEGV`, `SIGHUP`;
harness APIs `tst_resm`, `tst_exit`, `TEST`, `tst_brkm`, `tst_parse_opts`, `tst_count`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `test`,
`sigh`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state; maps or protects temporary memory for buffers, alternate stacks, or coordination. State is
scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, `lapi/syscalls.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: obsolete or direct syscall paths may be absent or emulated differently on newer
architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `signalfd`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/signalfd01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/signalfd01.c

## Purpose
Verify that signalfd() works as expected. - signalfd() can create fd, and fd can receive signal. -
signalfd() can reassign fd, and fd can receive signal.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `signalfd`; types `struct signalfd_siginfo`,
`struct tst_test`; constants/macros `SIGUSR1`, `SIG_BLOCK`, `SIGUSR2`; safe wrappers `SAFE_KILL`,
`SAFE_READ`, `SAFE_SIGEMPTYSET`, `SAFE_SIGADDSET`, `SAFE_SIGPROCMASK`, `SAFE_CLOSE`; harness APIs
`tst_test`, `TST_EXP_EQ_LI`, `TST_EXP_FD`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `check_signal`, `setup`, `cleanup`, `verify_signalfd`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/signalfd01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/signalfd02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/signalfd02.c

## Purpose
Verify that signalfd(2) fails with: - EBADF when fd is invalid - EINVAL when fd is not a valid
signalfd file descriptor - EINVAL when flags are invalid.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `signalfd`; types `struct test_case_t`, `struct
tst_test`, `struct tst_buffers`; constants/macros `SIGNAL_FILE`, `SIGUSR1`, `SIG_BLOCK`; safe
wrappers `SAFE_SIGEMPTYSET`, `SAFE_SIGADDSET`, `SAFE_SIGPROCMASK`, `SAFE_OPEN`, `SAFE_CLOSE`;
harness APIs `tst_test`, `TST_EXP_FAIL2`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `setup`, `cleanup`, `verify_signalfd`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
expected errno/status values `EBADF`, `EINVAL`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/signalfd02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd4/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signalfd4/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `signalfd4`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd4/signalfd4_01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signalfd4/signalfd4_01.c

## Purpose
http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-
2.6.git;a=commit;h=9deb27baedb79759c3ab9435a7d8b841842d56e9. Referenced kernel commit ids include
`9deb27baedb79759c3ab9435a7d8b841842d56e9`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigemptyset`, `sigaddset`, `close`;
constants/macros `SIGUSR1`, `SIGSETSIZE`; harness APIs `tst_exit`, `tst_rmdir`, `tst_tmpdir`,
`tst_parse_opts`, `tst_count`, `tst_syscall`, `tst_brkm`, `tst_resm`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `cleanup`,
`setup`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, temporary directory support, `lapi/syscalls.h`
compatibility wrappers, `lapi/fcntl.h` compatibility wrappers. The file is built by the syscall
directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: obsolete or direct syscall paths may be absent or emulated differently on newer
architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd4/signalfd4_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd4/signalfd4_02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/signalfd4/signalfd4_02.c

## Purpose
http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-
2.6.git;a=commit;h=5fb5e04926a54bc1c22bba7ca166840f4476196f. Referenced kernel commit ids include
`5fb5e04926a54bc1c22bba7ca166840f4476196f`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigemptyset`, `sigaddset`, `close`;
constants/macros `SIGUSR1`, `SIGSETSIZE`; harness APIs `tst_exit`, `tst_rmdir`, `tst_tmpdir`,
`tst_parse_opts`, `tst_count`, `tst_syscall`, `tst_brkm`, `tst_resm`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `cleanup`,
`setup`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, temporary directory support, `lapi/syscalls.h`
compatibility wrappers. The file is built by the syscall directory Makefile and executed as part of
the LTP kernel syscall suite.

## Risks and edge cases
Key risks: obsolete or direct syscall paths may be absent or emulated differently on newer
architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/signalfd4/signalfd4_02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigpending/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigpending/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigpending`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `CPPFLAGS += -DTEST_SIGPENDING`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigpending/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigpending/sigpending02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigpending/sigpending02.c

## Purpose
AUTHORS Paul Larson Matthias Maennich Test 1: Suppress handling SIGUSR1 and SIGUSR1, raise them and
assert their signal pending. Test 2: Call sigpending(sigset_t*=-1), it should return -1 with errno
EFAULT.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigemptyset`, `sigaddset`, `signal`,
`sigpending`, `sigprocmask`; types `struct tst_test`; constants/macros `SIGUSR1`, `SIGSETSIZE`,
`SIGMAX`, `SIGUSR2`, `SIG_SETMASK`; safe wrappers `SAFE_SIGNAL`; harness APIs `tst_test`,
`tst_variant`, `tst_res`, `tst_brk`, `tst_syscall`, `TEST`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`,
`.test_variants`. Local functions include `sigpending_info`, `tested_sigpending`, `sighandler`,
`test_sigpending`, `test_efault_on_invalid_sigset`, `run`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/syscalls.h` compatibility wrappers. The
file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery; obsolete or direct
syscall paths may be absent or emulated differently on newer architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`; expected
errno/status values `EFAULT`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigpending/sigpending02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigprocmask/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigprocmask/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigprocmask`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigprocmask/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigprocmask/sigprocmask01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigprocmask/sigprocmask01.c

## Purpose
Test Name: sigprocmask01 Verify that sigprocmask() succeeds to examine and change the calling
process's signal mask. Also, verify that sigpending() succeeds to store signal mask that are blocked
from delivery and pending for the calling process. Expected result: - sigprocmask() should return
value 0 on successs and succeed to change calling process's set of blocked/unblocked signals. -
sigpending() should succeed to store the signal mask of pending signal. Algorithm: Setup: Setup
signal handling. Create temporary directory. Pause for SIGUSR1 if option specified. Test: Loop if
the proper options are given. Execute system call Check return code, if system call failed
(return=-1) Log the errno.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigemptyset`, `sigaddset`,
`signal`, `sigpending`, `sigprocmask`, `kill`; types `struct sigaction`, `struct to`;
constants/macros `SIGUSR1`, `SIGINT`, `SIG_BLOCK`, `SIG_UNBLOCK`; harness APIs `tst_parse_opts`,
`tst_count`, `TEST`, `tst_resm`, `tst_brkm`, `tst_exit`, `tst_sig`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `sig_handler`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigprocmask/sigprocmask01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigrelse/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigrelse/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigrelse`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigrelse/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigrelse/sigrelse01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigrelse/sigrelse01.c

## Purpose
OS Test - Silicon Graphics, Inc. Eagan, Minnesota TEST IDENTIFIER : sigrelse01 Releasing held
signals. PARENT DOCUMENT : sgrtds01 sigrelse system call AUTHOR : Bob Clark : Rewrote 12/92 by
Richard Logan CO-PILOT : Dave Baumgartner DATE STARTED : 10/08/86 TEST ITEMS 1. sigrelse turns on
the receipt of signals held by sighold. SPECIAL PROCEDURAL REQUIRMENTS None DETAILED set up pipe for
parent/child communications fork off a child process parent(): set up for unexpected signals wait
for child to send ready message over pipe send all catchable signals to child process send alarm
signal to speed up timeout wait for child to terminate and check exit value if exit value is EXIT_OK
get message.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sighold`, `sigrelse`, `signal`, `pipe`, `fork`,
`kill`, `alarm`, `write`, `read`; constants/macros `SIG_CAUGHT`, `SIGCANCEL`, `SIGTIMER`, `SIGTERM`,
`SIG_ERR`, `SIGALRM`, `SIGKILL`, `SIGSTOP`, `SIGTSTP`, `SIGCONT`, `SIGNOBDM`, `SIGTTIN`, `SIGTTOU`,
`SIGPTINTR`, `SIGSWAP`, `SIGRTMIN`, `SIGRTMAX`; safe wrappers `SAFE_WAIT`, `SAFE_PIPE`; harness APIs
`TEST`, `tst_res`, `tst_parse_opts`, `tst_count`, `tst_fork`, `tst_brkm`, `tst_exit`, `tst_resm`,
`tst_sig`, `tst_tmpdir`, `tst_rmdir`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `parent`, `child`, `timeout`, `setup_sigs`, `handler`, `wait_a_while`, `write_pipe`,
`set_timeout`, `clear_timeout`, `getout`, `choose_sig`, `sighold`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes per-process signal
dispositions, masks, pending queues, or alternate signal stack state. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, legacy safe macro helpers, temporary directory
support. The file is built by the syscall directory Makefile and executed as part of the LTP kernel
syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TWARN`, `TERRNO`; expected errno/status values
`ESRCH`, `EOF`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigrelse/sigrelse01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigsuspend`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/sigsuspend01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/sigsuspend01.c

## Purpose
Verify the basic sigsuspend(2) syscall functionality: - sigsuspend(2) can replace process's current
signal mask by the specified signal mask and suspend the process execution until the delivery of a
signal. - sigsuspend(2) should return after the execution of signal handler and restore the previous
signal mask.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigsuspend`, `alarm`; types `struct sigaction`,
`struct tst_test`; constants/macros `SIGALRM`, `SIG_SETMASK`; safe wrappers `SAFE_SIGFILLSET`,
`SAFE_SIGPROCMASK`, `SAFE_SIGEMPTYSET`, `SAFE_SIGADDSET`, `SAFE_SIGACTION`; harness APIs `tst_test`,
`TEST`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`. Local functions include `sig_handler`, `verify_sigsuspend`, `setup`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EINTR`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/sigsuspend01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/sigsuspend02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/sigsuspend02.c

## Purpose
Verify that sigsuspend(2) fails with - EFAULT mask points to memory which is not a valid part of the
process address space.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigsuspend`; types `struct tst_test`; harness
APIs `tst_test`, `tst_get_bad_addr`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`. Local functions include `setup`, `verify_sigsuspend`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
expected errno/status values `EFAULT`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/sigsuspend02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigtimedwait/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigtimedwait/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigtimedwait`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `LTPLDLIBS  = -lltpsigwait`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigtimedwait/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigtimedwait/sigtimedwait01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigtimedwait/sigtimedwait01.c

## Purpose
This LTP test source exercises `sigtimedwait` syscall behavior in `sigtimedwait01.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigtimedwait`; types `struct sigwait_test_desc`,
`struct tst_test`; constants/macros `SIGUSR1`; harness APIs `tst_test`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.forks_child`. Local functions include `my_sigtimedwait`, `run`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigtimedwait/sigtimedwait01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigwait/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigwait/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigwait`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `LTPLDLIBS  = -lltpsigwait`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigwait/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigwait/sigwait01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigwait/sigwait01.c

## Purpose
This LTP test source exercises `sigwait` syscall behavior in `sigwait01.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigwait`; types `struct sigwait_test_desc`,
`struct tst_test`; constants/macros `SIGUSR1`; harness APIs `tst_test`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.forks_child`. Local functions include `my_sigwait`, `run`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigwait/sigwait01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigwaitinfo/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigwaitinfo/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigwaitinfo`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `LTPLDLIBS  = -lltpsigwait`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigwaitinfo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigwaitinfo/sigwaitinfo01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sigwaitinfo/sigwaitinfo01.c

## Purpose
This LTP test source exercises `sigwaitinfo` syscall behavior in `sigwaitinfo01.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigwaitinfo`; types `struct sigwait_test_desc`,
`struct tst_test`; constants/macros `SIGUSR1`; harness APIs `tst_test`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.forks_child`. Local functions include `my_sigwaitinfo`, `run`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sigwaitinfo/sigwaitinfo01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socket/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socket/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `socket`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `LDLIBS			+= -lpthread`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socket/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socket/socket01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socket/socket01.c

## Purpose
Test creating TCP, UDP, and Unix doman dgram sockets with socket() syscall. Also verify that
socket() fails and set proper errno - EAFNOSUPPORT on invalid domain - EINVAL on invalid type -
EPROTONOSUPPORT on raw open as non-root - EPROTONOSUPPORT on UDP stream - EPROTONOSUPPORT on TCP
dgram - EPROTONOSUPPORT on ICMP stream.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socket`; types `struct test_case_t`, `struct
tst_test`; safe wrappers `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `verify_socket`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values
`EAFNOSUPPORT`, `EINVAL`, `EPROTONOSUPPORT`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socket/socket01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socket/socket02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socket/socket02.c

## Purpose
This LTP test source exercises `socket` syscall behavior in `socket02.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socket`; types `struct tcase`, `struct
tst_test`; safe wrappers `SAFE_FCNTL`, `SAFE_CLOSE`; harness APIs `tst_test`, `tst_brk`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.cleanup`, `.test`, `.tcnt`.
Local functions include `verify_socket`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/fcntl.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socket/socket02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `socketcall`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall01.c

## Purpose
Basic test for the socketcall(2) raw syscall. Test creating TCP, UDP, raw socket and unix domain
dgram.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socketcall`; types `struct test_case_t`, `struct
tst_test`; constants/macros `AF_INET`; safe wrappers `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`,
`tst_syscall`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`,
`.needs_root`. Local functions include `verify_socketcall`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, `lapi/syscalls.h` compatibility
wrappers, Linux UAPI headers. The file is built by the syscall directory Makefile and executed as
part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
obsolete or direct syscall paths may be absent or emulated differently on newer architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall02.c

## Purpose
Author: Sowmya Adiga <sowmya.adiga@wipro.com> This is a error test for the socketcall(2) system
call.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socketcall`; types `struct test_case_t`, `struct
tst_test`; harness APIs `tst_test`, `tst_res`, `TEST`, `tst_syscall`, `tst_strerrno`,
`tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`.
Local functions include `verify_socketcall`, `setup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/syscalls.h` compatibility wrappers, Linux
UAPI headers. The file is built by the syscall directory Makefile and executed as part of the LTP
kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery; obsolete or direct
syscall paths may be absent or emulated differently on newer architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TINFO`, `TTERRNO`, `TERRNO`; expected errno/status values
`EINVAL`, `EFAULT`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall03.c

## Purpose
Author: Sowmya Adiga <sowmya.adiga@wipro.com> This is a basic test for the socketcall(2) for bind(2)
and listen(2).

## Important APIs, types, and functions
Important interfaces include syscall/library calls `bind`, `socketcall`; types `struct sockaddr_in`,
`struct tst_test`; constants/macros `AF_INET`; safe wrappers `SAFE_SOCKET`, `SAFE_CLOSE`; harness
APIs `tst_test`, `TEST`, `tst_syscall`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`. Local functions include `verify_socketcall`, `setup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/syscalls.h` compatibility wrappers, Linux
UAPI headers. The file is built by the syscall directory Makefile and executed as part of the LTP
kernel syscall suite.

## Risks and edge cases
Key risks: obsolete or direct syscall paths may be absent or emulated differently on newer
architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `socketpair`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `LDLIBS 			+= -lpthread`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/socketpair01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/socketpair01.c

## Purpose
Verify that socketpair(2) fails and set proper errno - EAFNOSUPPORT on invalid domain - EINVAL on
invalid type - EPROTONOSUPPORT on raw open as non-root - EFAULT on bad aligned pointer - EFAULT on
bad unaligned pointer - EOPNOTSUPP on UDP socket - EPROTONOSUPPORT on TCP dgram - EOPNOTSUPP on TCP
socket - EPROTONOSUPPORT on ICMP stream Also test creating UNIX domain dgram.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socketpair`; types `struct test_case_t`, `struct
tst_test`; safe wrappers `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `verify_socketpair`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values
`EAFNOSUPPORT`, `EINVAL`, `EPROTONOSUPPORT`, `EFAULT`, `EOPNOTSUPP`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/socketpair01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/socketpair02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/socketpair02.c

## Purpose
This LTP test source exercises `socketpair` syscall behavior in `socketpair02.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socket`, `socketpair`; types `struct tcase`,
`struct tst_test`; safe wrappers `SAFE_FCNTL`, `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`,
`tst_brk`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.cleanup`, `.test`, `.tcnt`.
Local functions include `verify_socketpair`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/fcntl.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/socketpair02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sockioctl/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sockioctl/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sockioctl`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sockioctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sockioctl/sockioctl01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/sockioctl/sockioctl01.c

## Purpose
Test Name: sockioctl01 Verify that ioctl() on sockets returns the proper errno for various failure
cases. Referenced kernel commit ids include `46ce341b2f176c2611f12ac390adf862e932eb02`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `ioctl`, `open`, `close`, `mknod`; types `struct
sockaddr_in`, `struct ifconf`, `struct ifreq`, `struct test_case_t`, `struct sockaddr`;
constants/macros `SIOCATMARK`, `SIOCGIFCONF`, `SIOCGIFFLAGS`, `SIOCSIFFLAGS`, `AF_INET`, `S_IFIFO`;
safe wrappers `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_IOCTL`; harness APIs `tst_parse_opts`, `tst_count`,
`TEST`, `tst_resm`, `tst_exit`, `tst_tmpdir`, `tst_rmdir`, `tst_brkm`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`setup0`, `setup1`, `setup2`, `setup3`, `cleanup`, `cleanup0`, `cleanup1`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, legacy safe macro helpers, temporary directory
support. The file is built by the syscall directory Makefile and executed as part of the LTP kernel
syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`; expected errno/status values `EBADF`, `EINVAL`,
`EFAULT`, `ENOIOCTLCMD`, `ENOTTY`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sockioctl/sockioctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `splice`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice.h -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice.h

## Purpose
This header provides `get_max_limit()`, a shared helper for splice tests that caps default pipe test
sizes against `/proc/sys/fs/pipe-max-size` or `/proc/sys/fs/pipe-max-pages` when those kernel
tunables exist.

## Important APIs, types, and functions
Important interfaces include safe wrappers `SAFE_FILE_SCANF`; harness APIs `tst_safe_file_ops`,
`tst_minmax`.

## Control flow
This helper/header is consumed by neighboring tests at compile time; it provides compatibility
definitions and small wrappers rather than a standalone runtime entry point.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies are the C library, Linux syscall ABI, and the LTP build/runtime harness. The file is
built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice01.c

## Purpose
This test case will verify basic function of splice added by kernel 2.6.17 or up.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`; safe wrappers
`SAFE_OPEN`, `SAFE_READ`, `SAFE_CLOSE`, `SAFE_PIPE`, `SAFE_WRITE`, `SAFE_WRITE_ALL`; harness APIs
`tst_test`, `tst_res`, `tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`, `.needs_tmpdir`. Local functions include `check_file`, `splice_test`, `setup`,
`cleanup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice02.c

## Purpose
Original reproducer for kernel fix bf40d3435caf NFS: add support for splice writes from v2.6.31-rc1.
http://lkml.org/lkml/2009/4/2/55 [ALGORITHM] - create pipe - fork(), child replace stdin with pipe -
parent write to pipe - child slice from pipe - check resulted file size and content. Referenced
kernel commit ids include `bf40d3435caf`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`, `stat`, `fork`; types `struct stat`,
`struct tst_test`, `struct tst_option`; safe wrappers `SAFE_CLOSE`, `SAFE_DUP2`, `SAFE_OPEN`,
`SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_PIPE`, `SAFE_FCNTL`, `SAFE_FORK`, `SAFE_WRITE`, `SAFE_WRITE_ALL`;
harness APIs `tst_test`, `tst_parse_int`, `tst_brk`, `TEST`, `tst_res`, `tst_reap_children`,
`tst_option`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.forks_child`, `.needs_tmpdir`. Local functions include `setup`, `do_child`, `run`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; maps or protects temporary
memory for buffers, alternate stacks, or coordination. State is scoped to the LTP process tree
unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TINFO`, `TTERRNO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice03.c

## Purpose
Verify that, splice(2) returns -1 and sets errno to 1. EBADF if the file descriptor fd_in is not
valid 2. EBADF if the file descriptor fd_out is not valid 3. EBADF if the file descriptor fd_in does
not have proper read-write mode 4. EINVAL if target file is opened in append mode 5. EINVAL if
neither of the descriptors refer to a pipe 6. ESPIPE if off_in is not NULL when the file descriptor
fd_in refers to a pipe 7. ESPIPE if off_out is not NULL when the file descriptor fd_out refers to a
pipe.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tcase`, `struct
tst_test`; safe wrappers `SAFE_FILE_PRINTF`, `SAFE_OPEN`, `SAFE_PIPE`, `SAFE_WRITE`,
`SAFE_WRITE_ALL`, `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `setup`, `splice_verify`, `cleanup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EBADF`,
`EINVAL`, `ESPIPE`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice04.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice04.c

## Purpose
This LTP test source exercises `splice` syscall behavior in `splice04.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`, `struct
tst_option`; safe wrappers `SAFE_MALLOC`, `SAFE_PIPE`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `SAFE_READ`,
`SAFE_CLOSE`; harness APIs `tst_test`, `tst_parse_int`, `tst_brk`, `tst_res`, `tst_option`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `cleanup`, `pipe_pipe`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TINFO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice05.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice05.c

## Purpose
Functional test for splice(2): pipe <-> socket This test case tests splice(2) from a pipe to a
socket and vice versa.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`, `struct
tst_option`; constants/macros `AF_UNIX`; safe wrappers `SAFE_MALLOC`, `SAFE_PIPE`,
`SAFE_SOCKETPAIR`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `SAFE_READ`, `SAFE_CLOSE`; harness APIs
`tst_test`, `tst_parse_int`, `tst_brk`, `tst_res`, `tst_option`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `cleanup`, `pipe_socket`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TINFO`, `TERRNO`; expected errno/status
values `EINVAL`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice06.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice06.c

## Purpose
This LTP test source exercises `splice` syscall behavior in `splice06.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`, `struct
tst_path_val`; safe wrappers `SAFE_OPEN`, `SAFE_PIPE`, `SAFE_READ`, `SAFE_CLOSE`, `SAFE_WRITE`,
`SAFE_WRITE_ALL`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`; harness APIs `tst_test`, `tst_brk`,
`tst_parse_int`, `tst_res`, `tst_path_val`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_tmpdir`. Local functions include `format_str`, `splice_read_num`,
`splice_write_num`, `splice_write_str`, `file_write_num`, `file_write_str`, `file_read_num`,
`splice_test`, `setup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TBROK`, `TCONF`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice07.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice07.c

## Purpose
Iterate over all kinds of file descriptors and feed splice() with all possible combinations where at
least one file descriptor is invalid. We do expect the syscall to fail either with EINVAL or EBADF.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_fd`, `struct
tst_test`; harness APIs `tst_test`, `tst_fd`, `TST_EXP_FAIL2_ARR`, `tst_fd_desc`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`. Local
functions include `check_splice`, `verify_splice`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TINFO`; expected errno/status values `EINVAL`, `EBADF`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice08.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice08.c

## Purpose
Test for splicing from /dev/zero and /dev/full. The support for splicing from /dev/zero and
/dev/full was removed in: c6585011bc1d ("splice: Remove generic_file_splice_read()") And added back
in: 1b057bd800c3 ("drivers/char/mem: implement splice() for /dev/zero, /dev/full"). Referenced
kernel commit ids include `c6585011bc1d`, `1b057bd800c3`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`; safe wrappers
`SAFE_PIPE`, `SAFE_READ`, `SAFE_CLOSE`, `SAFE_OPEN`; harness APIs `tst_test`, `TST_EXP_POSITIVE`,
`tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`. Local functions include `test_splice`, `verify_splice`, `setup`, `cleanup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TINFO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice09.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice09.c

## Purpose
Test for splicing to /dev/zero and /dev/null these two devices discard all data written to them. The
support for splicing to /dev/zero was added in: 1b057bd800c3 ("drivers/char/mem: implement splice()
for /dev/zero, /dev/full"). Referenced kernel commit ids include `1b057bd800c3`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`; safe wrappers
`SAFE_OPEN`, `SAFE_PIPE`, `SAFE_WRITE`, `SAFE_CLOSE`; harness APIs `tst_test`, `tst_res`,
`TST_EXP_POSITIVE`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `verify_splice`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TFAIL`, `TINFO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ssetmask/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/ssetmask/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `ssetmask`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ssetmask/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ssetmask/ssetmask01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/ssetmask/ssetmask01.c

## Purpose
This LTP test source exercises `ssetmask` syscall behavior in `ssetmask01.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sgetmask`, `ssetmask`; constants/macros
`SIGALRM`, `SIGUSR1`; harness APIs `tst_exit`, `tst_rmdir`, `tst_tmpdir`, `tst_parse_opts`,
`tst_count`, `tst_syscall`, `TEST`, `tst_brkm`, `tst_resm`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `cleanup`,
`setup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, temporary directory support, `lapi/syscalls.h`
compatibility wrappers. The file is built by the syscall directory Makefile and executed as part of
the LTP kernel syscall suite.

## Risks and edge cases
Key risks: obsolete or direct syscall paths may be absent or emulated differently on newer
architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ssetmask/ssetmask01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/stat/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `stat`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `%_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat01.c

## Purpose
Verify that, stat(2) succeeds to get the status of a file and fills the stat structure elements
regardless of whether process has or doesn't have read access to the file.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `stat`; types `struct passwd`, `struct tcase`,
`struct stat`, `struct tst_test`; safe wrappers `SAFE_GETPWNAM`, `SAFE_SETUID`, `SAFE_CHMOD`;
harness APIs `tst_test`, `TST_EXP_PASS`, `TST_EXP_EQ_LU`, `TST_EXP_EQ_LI`, `tst_fill_file`,
`tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`, `.needs_tmpdir`. Local functions include `verify_stat`, `setup`.

## State and persistence behavior
The test changes process credentials for the running process or child. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TBROK`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat02.c

## Purpose
Now check to see if the number of bytes written was the same as the number of bytes in the file.

## Important APIs, types, and functions
Important interfaces include types `struct test_case`, `struct stat`, `struct tst_test`; safe
wrappers `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `SAFE_CLOSE`, `SAFE_STAT`, `SAFE_UNLINK`,
`SAFE_MALLOC`; harness APIs `tst_test`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `verify`, `verify_stat_size`, `setup`,
`cleanup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat03.c

## Purpose
check stat() with various error conditions that should produce EACCES, EFAULT, ENAMETOOLONG, ENOENT,
ENOTDIR, ELOOP.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `stat`; types `struct passwd`, `struct tcase`,
`struct stat`, `struct tst_test`; safe wrappers `SAFE_GETPWNAM`, `SAFE_SETUID`, `SAFE_MKDIR`,
`SAFE_TOUCH`, `SAFE_CHMOD`, `SAFE_SYMLINK`; harness APIs `tst_test`, `tst_eaccesdir`, `tst_enoent`,
`tst_enotdir`, `TST_EXP_FAIL`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`, `.needs_tmpdir`. Local functions include `verify_stat`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount;
changes process credentials for the running process or child. State is scoped to the LTP process
tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
invalid-address tests can expose architecture-specific fault delivery.

## Test signals
expected errno/status values `EACCES`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `ELOOP`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat04.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat04.c

## Purpose
This test checks that stat() executed on file provide the same information of symlink linking to it.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `stat`; types `struct stat`, `struct tst_test`,
`struct tst_buffers`; safe wrappers `SAFE_STAT`, `SAFE_MKFS`, `SAFE_MOUNT`, `SAFE_TOUCH`,
`SAFE_LINK`, `SAFE_CHOWN`, `SAFE_OPEN`, `SAFE_CLOSE`, `SAFE_SYMLINK`, `SAFE_UMOUNT`; harness APIs
`tst_test`, `tst_safe_stdio`, `TST_EXP_EQ_LI`, `tst_tmpdir_genpath`, `tst_device`, `tst_fill_fd`,
`tst_is_mounted`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`, `.needs_root`, `.needs_device`. Local functions include `run`, `setup`,
`cleanup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up; creates temporary
filesystem objects under the LTP temporary directory or test mount. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support,
scratch block device. The file is built by the syscall directory Makefile and executed as part of
the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
signal and timeout based assertions depend on scheduler timing; mount namespace, filesystem type,
and kernel version differences affect expected fields.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statfs/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statfs/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `statfs`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `%_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs01.c

## Purpose
This LTP test source exercises `statfs` syscall behavior in `statfs01.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statfs`; types `struct statfs`, `struct
tst_test`; safe wrappers `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `SAFE_CLOSE`; harness APIs
`tst_test`, `TST_EXP_PASS`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_root`. Local functions include `setup`, `run`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs02.c

## Purpose
Tests for failures: - ENOTDIR A component of the pathname, which is not a directory. - ENOENT A
filename which doesn't exist. - ENAMETOOLONG A pathname which is longer than MAXNAMLEN. - EFAULT A
pathname pointer outside the address space of the process. - EFAULT A buf pointer outside the
address space of the process. - ELOOP A filename which has too many symbolic links.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statfs`, `close`; types `struct statfs`, `struct
test_case_t`, `struct tst_test`; constants/macros `SIGSEGV`; safe wrappers `SAFE_FORK`,
`SAFE_WAITPID`, `SAFE_CREAT`, `SAFE_SYMLINK`; harness APIs `tst_test`, `tst_safe_macros`,
`TST_EXP_FAIL`, `tst_res`, `tst_strstatus`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.forks_child`, `.needs_tmpdir`. Local functions include `statfs_verify`, `setup`,
`cleanup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount; uses
child processes and wait/exit status as observable state. State is scoped to the LTP process tree
unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`; expected errno/status values `ENOTDIR`, `ENOENT`,
`ENAMETOOLONG`, `EFAULT`, `ELOOP`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs03.c

## Purpose
Verify that statfs(2) fails with errno EACCES when search permission is denied for a component of
the path prefix of path.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statfs`; types `struct passwd`, `struct statfs`,
`struct tst_test`; safe wrappers `SAFE_MKDIR`, `SAFE_GETPWNAM`, `SAFE_SETEUID`; harness APIs
`tst_test`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_root`, `.needs_tmpdir`. Local functions include `setup`, `run`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount;
changes process credentials for the running process or child. State is scoped to the LTP process
tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
expected errno/status values `EACCES`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `statmount`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount.h -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount.h

## Purpose
This header provides compatibility definitions and wrappers for the new `statmount()` syscall so the
adjacent tests can build across libc and kernel header versions.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`;
constants/macros `STATMOUNT_H`; safe wrappers `SAFE_FOPEN`; harness APIs `tst_test`,
`tst_safe_stdio`, `tst_syscall`, `tst_brk`.

## Control flow
This helper/header is consumed by neighboring tests at compile time; it provides compatibility
definitions and small wrappers rather than a standalone runtime entry point.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up. State is scoped to the
LTP process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/syscalls.h` compatibility wrappers. The
file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields;
obsolete or direct syscall paths may be absent or emulated differently on newer architectures.

## Test signals
LTP result macros `TBROK`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount01.c

## Purpose
This test verifies that statmount() is working with no mask flags. [Algorithm] - create a mount
point - run statmount() on the mount point without giving any mask - read results and check that
mask and size are correct.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tst_test`, `struct tst_buffers`; constants/macros `AT_FDCWD`,
`STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_STATX`; harness APIs `TST_EXP_PASS`, `TST_EXP_EQ_LI`,
`tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`. Local functions include `run`, `setup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up. State is scoped to the
LTP process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/stat.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount02.c

## Purpose
This test verifies that statmount() is correctly reading basic filesystem info using
STATMOUNT_SB_BASIC. The btrfs validation is currently skipped due to the lack of support for VFS.
[Algorithm] - create a mount point and read its mount info - run statmount() on the mount point
using STATMOUNT_SB_BASIC - read results and check if mount info are correct.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct statfs`, `struct tst_test`, `struct tst_buffers`; constants/macros
`STATMOUNT_SB_BASIC`, `MS_RDONLY`, `AT_FDCWD`, `STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_MOUNT`,
`SAFE_STATX`, `SAFE_STATFS`, `SAFE_UMOUNT`; harness APIs `TST_EXP_PASS`, `TST_EXP_EQ_LI`,
`tst_device`, `tst_is_mounted`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `run`, `setup`, `cleanup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up. State is scoped to the
LTP process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/stat.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount03.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount03.c

## Purpose
This test verifies that statmount() is correctly reading mount information (mount id, parent mount
id, mount attributes etc.) using STATMOUNT_MNT_BASIC. [Algorithm] - create a mount point - create a
new parent folder inside the mount point and obtain its mount info - create the new "/" mount folder
and obtain its mount info - run statmount() on the mount point using STATMOUNT_MNT_BASIC - read
results and check if mount info are correct.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tcase`, `struct tst_test`, `struct tst_buffers`; constants/macros
`STATMOUNT_MNT_BASIC`, `STATX_MNT_ID`, `AT_FDCWD`, `STATX_MNT_ID_UNIQUE`, `MS_PRIVATE`, `MS_SHARED`,
`MS_SLAVE`, `MS_UNBINDABLE`, `MS_BIND`, `MS_REC`; safe wrappers `SAFE_STATX`, `SAFE_MOUNT`,
`SAFE_UMOUNT`, `SAFE_MKDIR`, `SAFE_UNSHARE`; harness APIs `tst_res`, `TST_EXP_PASS`,
`TST_EXP_EQ_LI`, `TST_EXP_EQ_LU`, `tst_is_mounted`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `read_mnt_id`, `run`, `setup`, `cleanup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up; creates temporary
filesystem objects under the LTP temporary directory or test mount. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support, `lapi/stat.h`
compatibility wrappers. The file is built by the syscall directory Makefile and executed as part of
the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
LTP result macros `TINFO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount04.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount04.c

## Purpose
This test verifies that statmount() is correctly reading propagation from what mount in current
namespace using STATMOUNT_PROPAGATE_FROM. [Algorithm] - create a mount point - propagate a mounted
folder inside the mount point - run statmount() on the mount point using STATMOUNT_PROPAGATE_FROM -
read results and check propagated_from parameter contains the propagated folder ID.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tst_test`, `struct tst_buffers`; constants/macros `STATMOUNT_PROPAGATE_FROM`,
`MS_BIND`, `MS_SHARED`, `MS_SLAVE`, `AT_FDCWD`, `STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_MKDIR`,
`SAFE_MOUNT`, `SAFE_STATX`, `SAFE_UMOUNT`; harness APIs `TST_EXP_PASS`, `TST_EXP_EQ_LI`,
`tst_is_mounted`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `run`, `setup`, `cleanup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up; creates temporary
filesystem objects under the LTP temporary directory or test mount. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/stat.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount05.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount05.c

## Purpose
This test verifies STATMOUNT_MNT_ROOT and STATMOUNT_MNT_POINT functionalities of statmount(). In
particular, STATMOUNT_MNT_ROOT will give the mount root (i.e. mount --bind /mnt /bla -> /mnt) and
STATMOUNT_MNT_POINT will give the mount point (i.e. mount --bind /mnt /bla -> /bla). [Algorithm] -
create a mount point - mount a folder inside the mount point - run statmount() on the mounted folder
using STATMOUNT_MNT_ROOT - read results and check if contain the mount root path - run statmount()
on the mounted folder using STATMOUNT_MNT_POINT - read results and check if contain the mount point
path.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tst_test`, `struct tst_buffers`; constants/macros `STATMOUNT_MNT_ROOT`,
`STATMOUNT_MNT_POINT`, `MS_BIND`, `AT_FDCWD`, `STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_MKDIR`,
`SAFE_MOUNT`, `SAFE_STATX`, `SAFE_UMOUNT`; harness APIs `tst_tmpdir`, `tst_res`, `TST_EXP_PASS`,
`TST_EXP_EQ_LI`, `TST_EXP_EQ_STR`, `TST_EXP_POSITIVE`, `tst_tmpdir_genpath`, `tst_is_mounted`,
`tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `test_mount_root`, `test_mount_point`, `run`, `setup`,
`cleanup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up; creates temporary
filesystem objects under the LTP temporary directory or test mount. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support, `lapi/stat.h`
compatibility wrappers. The file is built by the syscall directory Makefile and executed as part of
the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
LTP result macros `TINFO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount06.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount06.c

## Purpose
This test verifies that statmount() is correctly reading name of the filesystem type using
STATMOUNT_FS_TYPE. [Algorithm] - create a mount point - run statmount() on the mount point using
STATMOUNT_FS_TYPE - read results and check if contain the name of the filesystem.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tst_test`, `struct tst_buffers`; constants/macros `STATMOUNT_FS_TYPE`,
`AT_FDCWD`, `STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_STATX`; harness APIs `TST_EXP_PASS`,
`tst_device`, `TST_EXP_EQ_LI`, `TST_EXP_EQ_STR`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`. Local functions include `run`, `setup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up. State is scoped to the
LTP process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/stat.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount07.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount07.c

## Purpose
This test verifies that statmount() is raising the correct errors according with invalid input
values.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
tcase`, `struct ltp_statx`, `struct tst_test`, `struct tst_buffers`; constants/macros
`STATMOUNT_FS_TYPE`, `STATMOUNT_MNT_ROOT`, `STATMOUNT_MNT_POINT`, `AT_FDCWD`, `STATX_MNT_ID_UNIQUE`;
safe wrappers `SAFE_STATX`; harness APIs `TST_EXP_FAIL`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`.
Local functions include `run`, `setup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up. State is scoped to the
LTP process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/stat.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields;
invalid-address tests can expose architecture-specific fault delivery.

## Test signals
expected errno/status values `ENOENT`, `EOVERFLOW`, `EINVAL`, `EFAULT`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount08.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount08.c

## Purpose
This LTP test source exercises `statmount` syscall behavior in `statmount08.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct passwd`, `struct tst_test`, `struct tst_buffers`; constants/macros
`STATMOUNT_SB_BASIC`, `AT_FDCWD`, `STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_FORK`, `SAFE_SETEGID`,
`SAFE_SETEUID`, `SAFE_GETPWNAM`, `SAFE_STATX`, `SAFE_CHROOT`; harness APIs `TST_EXP_FAIL`,
`tst_tmpdir_path`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.forks_child`, `.needs_root`, `.needs_tmpdir`. Local functions include `run`, `setup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up; changes process
credentials for the running process or child; uses child processes and wait/exit status as
observable state. State is scoped to the LTP process tree unless a privileged syscall changes host-
visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support,
`lapi/stat.h` compatibility wrappers. The file is built by the syscall directory Makefile and
executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
expected errno/status values `EPERM`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount09.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount09.c

## Purpose
This test verifies that statmount() is correctly reading the mount ID for the current namespace.
[Algorithm] - create a mount point - run statmount() on the mount point using STATMOUNT_MNT_NS_ID -
read results and check if contain the correct mount ID for the current namespace.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tst_test`, `struct tst_buffers`; constants/macros `STATMOUNT_MNT_NS_ID`,
`AT_FDCWD`, `STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_STATX`, `SAFE_OPEN`, `SAFE_IOCTL`,
`SAFE_CLOSE`; harness APIs `TST_EXP_PASS`, `TST_EXP_EQ_LI`, `tst_res`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`. Local functions include `run`, `setup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up. State is scoped to the
LTP process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/stat.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
LTP result macros `TCONF`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `statvfs`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/statvfs01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/statvfs01.c

## Purpose
Verify that statvfs() executes successfully for all available filesystems. Verify statvfs.f_namemax
field by trying to create files of valid and invalid length names.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statvfs`, `creat`; types `struct statvfs`,
`struct tst_test`; safe wrappers `SAFE_CLOSE`, `SAFE_TOUCH`; harness APIs `tst_test`, `tst_fs_type`,
`TST_EXP_PASS`, `TST_EXP_FD`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_root`. Local functions include `run`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
expected errno/status values `ENAMETOOLONG`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/statvfs01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/statvfs02.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/statvfs02.c

## Purpose
Verify that statvfs() fails with: - EFAULT when path points to an invalid address. - ELOOP when too
many symbolic links were encountered in translating path. - ENAMETOOLONG when path is too long. -
ENOENT when the file referred to by path does not exist. - ENOTDIR a component of the path prefix of
path is not a directory.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statvfs`; types `struct statvfs`, `struct
tcase`, `struct tst_test`; safe wrappers `SAFE_SYMLINK`, `SAFE_TOUCH`; harness APIs `tst_test`,
`tst_get_bad_addr`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_tmpdir`. Local functions include `setup`, `run`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
expected errno/status values `EFAULT`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/statvfs02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/Makefile -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statx/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `statx`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `%_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64`; `statx06: LDLIBS += -lrt`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx01.c -->

# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx01.c

## Purpose
This code tests the functionality of statx system call. The metadata for normal file are tested
against expected values: - gid - uid - mode - blocks - size - nlink - mnt_id The metadata for device
file are tested against expected values: - MAJOR number - MINOR number.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statx`; types `struct statx`, `struct tcase`,
`struct tst_test`; constants/macros `STATX_MNT_ID`, `AT_FDCWD`, `S_IFMT`, `S_IFBLK`; safe wrappers
`SAFE_FOPEN`, `SAFE_FCLOSE`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `SAFE_MKNOD`,
`SAFE_CLOSE`; harness APIs `tst_test`, `tst_safe_macros`, `tst_safe_stdio`, `tst_res`, `TEST`,
`tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_root`, `.needs_devfs`. Local functions include `test_mnt_id`,
`test_normal_file`, `test_device_file`, `run`, `setup`, `cleanup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, device filesystem support,
`lapi/stat.h` compatibility wrappers, `lapi/fcntl.h` compatibility wrappers. The file is built by
the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`.

<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx01.c -->
