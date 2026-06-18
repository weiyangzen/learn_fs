<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/unwind_vdso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/unwind_vdso.c

## Purpose

`unwind_vdso.c` tests unwind metadata for the 32-bit vDSO `AT_SYSINFO` syscall entry. It verifies that single-stepping through the fast syscall path still permits correct stack unwinding and argument recovery.

## Important APIs, Types, and Functions

The test uses `getauxval(AT_SYSINFO)`, `dladdr()`, `_Unwind_Backtrace()`, `_Unwind_GetIP()`, `_Unwind_GetGR()`, and a `SIGTRAP` handler. `trace_fn()` walks frames until the expected return address and validates syscall number and argument registers. `sigtrap()` detects entry into AT_SYSINFO and disables TF at the return address.

## Control Flow and State

`main()` discovers AT_SYSINFO, installs SIGTRAP, forces lazy binding with one syscall, sets TF, and calls `syscall(SYS_getpid, 1, 2, 3, 4, 5, 6)`. The handler tracks whether it has reached the vDSO, records the return address from the stack, and runs unwinding on trap events. Globals store `sysinfo`, `return_address`, `got_sysinfo`, and error count.

## Dependencies and Integration Points

It depends on a libc new enough for `getauxval`, the 32-bit vDSO fast syscall path, libgcc unwind support, `helpers.h`, and correct vDSO unwind annotations. It integrates with compat ABI and debugger/unwinder expectations.

## Risks and Test Signals

Risks include missing or wrong unwind info, failed AT_SYSINFO discovery, trap flag not being cleared, and incorrect register recovery. Passing output maps AT_SYSINFO to the vDSO and reports recovered syscall number and arguments as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/unwind_vdso.c -->
