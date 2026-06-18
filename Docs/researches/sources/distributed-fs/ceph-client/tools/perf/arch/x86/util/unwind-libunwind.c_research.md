# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/unwind-libunwind.c

Purpose: maps perf DWARF register numbers to libunwind register identifiers for x86 and x86_64.

Important APIs/types/functions: exports `LIBUNWIND__ARCH_REG_ID(int regnum)` with architecture-specific implementations. x86_64 maps DWARF registers 0-16 plus RIP to `UNW_X86_64_*`; i386 maps common general registers and EIP to `UNW_X86_*`.

Control flow: switch statements translate known register numbers and return `-EINVAL` for unsupported registers.

State and persistence: no state.

Dependencies and integration: depends on libunwind architecture constants and perf unwind glue macro naming. Used by perf callchain/unwind code when libunwind is enabled.

Risks: register maps must match the DWARF ABI and libunwind constants. Unsupported SIMD/FPU/system registers return errors; callers must tolerate missing registers.

Test signals: build with libunwind on 32-bit and 64-bit x86, unwind user stacks from samples, and validate instruction pointer/register recovery.
