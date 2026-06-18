# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/test_util.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/test_util.h

Purpose: generic KVM selftest utility header. It provides logging, skip/assertion macros, robust I/O helpers, SIGBUS expectation support, time math, guest random generation, memory backing-source metadata, alignment helpers, paranoid numeric parsing, guest snprintf, and clocksource lookup.

Important APIs/types/functions: `pr_debug`, `pr_info`, `print_skip`, `TEST_REQUIRE`, `TEST_ASSERT`, `TEST_ASSERT_EQ`, `TEST_ASSERT_KVM_EXIT_REASON`, `TEST_FAIL`, `TEST_EXPECT_SIGBUS`, `parse_size`, timespec helpers, `struct guest_random_state`, guest RNG helpers, `enum vm_mem_backing_src_type`, `struct vm_mem_backing_src_alias`, backing-source helpers, `align_up`, `align_down`, `align_ptr_up`, `atoi_paranoid`, `atoi_positive`, `atoi_non_negative`, `guest_vsnprintf`, `guest_snprintf`, `strdup_printf`, and `sys_get_cur_clocksource`.

Control flow and state: assertion macros terminate failing tests through kselftest mechanisms; `TEST_REQUIRE` skips. SIGBUS expectation temporarily installs a signal handler and uses `sigjmp_buf`. Memory backing helpers map CLI strings to mmap flags/page sizes. Guest RNG maintains deterministic seed/state for repeatable guest workloads.

Dependencies and integration: depends on `kselftest.h`, POSIX headers, Linux types, and is included by most KVM selftest headers. It is the base for `kvm_util.h` error handling and memory-source parsing.

Risks: assertion macros evaluate arguments with local temporaries but still terminate the process, so negative-path tests need non-asserting helpers. Host sysfs/proc feature probes can be environment-dependent. SIGBUS handler use must restore old handlers to avoid affecting later checks.

Test signals: every selftest using assertions, memory backing CLI, time helpers, or guest RNG validates this header. Failures are usually clear because macros include expression, file, line, and formatted diagnostics.
