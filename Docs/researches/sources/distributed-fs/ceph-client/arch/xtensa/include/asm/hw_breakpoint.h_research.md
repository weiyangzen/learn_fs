<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/hw_breakpoint.h

## Purpose
Declares Xtensa hardware breakpoint/watchpoint support for perf and ptrace.

## Important APIs, Types, And Functions
Defines breakpoint types `XTENSA_BREAKPOINT_EXECUTE`, `XTENSA_BREAKPOINT_LOAD`, and `XTENSA_BREAKPOINT_STORE`; `struct arch_hw_breakpoint`; and functions including `hw_breakpoint_slots`, `arch_check_bp_in_kernelspace`, `hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `hw_breakpoint_pmu_read`, `check_hw_breakpoint`, `clear_ptrace_hw_breakpoint`, and `restore_dbreak`.

## Control Flow
When `CONFIG_HAVE_HW_BREAKPOINT` is enabled, perf/ptrace code uses these declarations to parse, install, handle, and remove debug registers. Otherwise `clear_ptrace_hw_breakpoint` is a no-op stub.

## State And Persistence
State is hardware debug register programming and per-task breakpoint metadata managed elsewhere.

## Dependencies And Integration Points
Depends on perf events, ptrace, notifier chains, and Xtensa debug/breakpoint exception handling.

## Risks And Edge Cases
Breakpoint length/type parsing must match hardware capabilities. Kernel-space checks protect against invalid user breakpoints. Restore paths must reprogram debug registers after context switches.

## Test Signals
Run perf breakpoint tests, ptrace hardware watchpoint tests, kernel/user address rejection tests, and context-switch restore tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/hw_breakpoint.h -->
