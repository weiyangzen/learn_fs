<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/gettimeofday.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/gettimeofday.h

Purpose: PowerPC vDSO time entry support, wiring generic vDSO gettimeofday/clock_gettime code to the PowerPC timebase and to architecture-specific syscall fallbacks.

Important APIs/types/functions: `VDSO_HAS_CLOCK_GETRES`, `VDSO_HAS_TIME`, `VDSO_DELTA_NOMASK`, `do_syscall_2()`, `gettimeofday_fallback()`, clock gettime/getres fallback variants, `__arch_get_hw_counter()`, `vdso_clocksource_ok()`, 32-bit `vdso_shift_ns()`, and exported C vDSO entry prototypes such as `__c_kernel_clock_gettime` and `__c_kernel_gettimeofday`.

Control flow: Fast paths read the timebase through `get_tb()` and let generic vDSO code compute times; fallback paths load PowerPC syscall arguments into r0/r3/r4, execute `sc`, normalize negative error returns, and select time64 syscalls for 32-bit vDSO clock_gettime/getres.

State and persistence: No persistent software state is owned here. The header consumes read-only vDSO data and the CPU timebase; it assumes PowerPC vDSO clocksources use a full 64-bit mask.

Dependencies and integration points: Depends on `asm/vdso/timebase.h`, syscall numbers, barrier semantics, UAPI time types, and generic vDSO data structures. Integrated by PowerPC vDSO builds and libc callers mapped to the vDSO page.

Risks: Inline assembly register constraints and clobbers are ABI-sensitive. Wrong syscall number selection breaks 32-bit time64 behavior. The `VDSO_DELTA_NOMASK` assumption must remain aligned with available PowerPC clocksources.

Test signals: Build 32-bit and 64-bit vDSO, run `clock_gettime`, `clock_getres`, `gettimeofday`, and `time` tests with forced fallback paths, and compare monotonic/realtime behavior against syscalls.

Source read size: 149 lines, 4132 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/gettimeofday.h -->
