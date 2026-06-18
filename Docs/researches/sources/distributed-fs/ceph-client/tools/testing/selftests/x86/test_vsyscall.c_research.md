<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_vsyscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_vsyscall.c

## Purpose

`test_vsyscall.c` validates legacy vsyscall and vDSO time-related ABI behavior. It compares `gettimeofday`, `time`, and `getcpu` results between syscalls, vDSO symbols, and fixed-address vsyscall functions, then checks vsyscall page permissions and emulation behavior on x86-64.

## Important APIs, Types, and Functions

`init_vdso()` opens `linux-vdso.so.1` or `linux-gate.so.1` and resolves `__vdso_gettimeofday`, `__vdso_clock_gettime`, `__vdso_time`, and `__vdso_getcpu`. `init_vsys()` parses `/proc/self/maps` for `[vsyscall]`. `test_gtod()`, `test_time()`, and `test_getcpu()` compare syscall, vDSO, and vsyscall results. x86-64-only tests include `test_vsys_r()`, `test_vsys_x()`, `test_process_vm_readv()`, and `test_emulation()`.

## Control Flow and State

`main()` declares a kselftest plan, initializes vDSO and vsyscall state, runs time/getcpu checks, then installs signal handlers for vsyscall read/execute probes and single-step emulation detection. Global booleans track read and execute permissions for the vsyscall page, and trap globals track fault class.

## Dependencies and Integration Points

The file depends on dlopen/dlsym, `/proc/self/maps`, `process_vm_readv`, CPU affinity, signal ucontext trap fields, kselftest helpers, and legacy fixed vsyscall addresses. It integrates with x86 vDSO/vsyscall compatibility policy.

## Risks and Test Signals

Risks include vDSO returning inconsistent time, vsyscall map permissions diverging from actual access, debugger read semantics regressing, and native rather than emulated vsyscalls. Passing output records correct timing windows, CPU/node matches, expected permission faults, and emulated vsyscall single-step behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_vsyscall.c -->
