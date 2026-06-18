# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-empty-vm.c

Purpose: x86-only procfs VM accounting regression test for a ptrace-stopped process whose userspace mappings have been unmapped. It validates that `/proc/$pid/maps`, `numa_maps`, `smaps`, `smaps_rollup`, and `statm` handle an effectively empty mm without corrupt output or crashes.

Important APIs and functions: `protection_key_support()` probes `pkey_alloc/free`; `vsyscall()` classifies the unavoidable amd64 vsyscall VMA; `test_proc_pid_*()` readers assert exact or empty proc output; `parse_u64()` validates `statm` fields. It uses `fork`, `ptrace(PTRACE_TRACEME)`, `munmap`, `sigaction`, `waitpid`, `open/read`, and raw pkey syscalls.

Control flow: the parent probes vsyscall and pkeys, forks a child, and waits briefly while the child marks itself traceable and unmaps almost the entire userspace address range. The parent then reads each proc VM file and finally waits for the child's SIGSEGV stop.

State and persistence: no persistent state beyond transient child process state and procfs observations. Global variables cache detected vsyscall and pkey capabilities to select expected strings.

Dependencies and integration: depends on x86 address-space assumptions, procfs, ptrace availability, optional `CONFIG_NUMA`, optional `CONFIG_PROC_PAGE_MONITOR`, and optional pkeys. Non-x86 builds return kselftest skip code 4.

Risks and test signals: the deliberate `sleep(1)` is a timing compromise because the child cannot reliably signal after unmapping itself. Exact smaps strings are kernel-output-sensitive. Failures signal proc VM walkers mishandling empty mm state, vsyscall handling drift, or `statm` accounting regressions.
