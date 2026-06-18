# sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/gettimeofday.h

## Purpose

`gettimeofday.h` implements MIPS VDSO time fallback syscalls and architecture counter readers for generic VDSO time code.

## Important APIs, Types, And Functions

Important APIs are `gettimeofday_fallback()`, `clock_gettime_fallback()`, `clock_getres_fallback()`, 32-bit time fallbacks, `read_r4k_count()`, `read_gic_count()`, `__arch_get_hw_counter()`, `mips_vdso_hres_capable()`, and `__arch_get_vdso_u_time_data()`. Includes: `asm/vdso/vdso.h`, `asm/clocksource.h`, `asm/unistd.h`, `asm/vdso.h`. Macros/constants: `__ASM_VDSO_GETTIMEOFDAY_H`, `VDSO_HAS_CLOCK_GETRES`, `VDSO_SYSCALL_CLOBBERS`, `__arch_vdso_hres_capable`, `__arch_get_vdso_u_time_data`. Types/enums/unions: `__kernel_old_timeval`, `timezone`, `__kernel_timespec`, `old_timespec32`, `vdso_time_data`. Functions/prototypes/helpers: `gettimeofday_fallback`, `clock_gettime_fallback`, `clock_getres_fallback`, `clock_gettime32_fallback`, `clock_getres32_fallback`, `mips_vdso_hres_capable`, `asm`, `get_gic`, `__raw_readl`, `read_r4k_count`, `read_gic_count`, `IS_ENABLED`, `get_vdso_time_data`.

## Control Flow

Fast paths read R4K `rdhwr` count or the GIC counter using stable hi/lo/hi reads. Unsupported or racing modes return 0 so generic VDSO code retries/falls back. Fallbacks invoke raw `syscall` with MIPS register conventions and translate the `a3` error flag.

## State And Persistence

State read includes VDSO data pages, optional mapped GIC counter page, hardware counters, and user output buffers.

## Dependencies And Integration Points

It integrates with generic `vdso/gettimeofday`, clocksource mode selection, syscall numbers, ABI64 versus time64 syscall selection, and MIPS clobber rules for HI/LO before ISA r6.

## Risks

Risks are wrong syscall number per ABI, missing clobbers, torn GIC counter reads, unsupported clock modes, and VDSO relocation/GOT use.

## Test Signals

Test signals are VDSO time selftests, 32-bit time64 tests, clocksource switching, strace fallback comparisons, and monotonicity checks.
Static review signal: this source currently has 221 lines and 5388 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
