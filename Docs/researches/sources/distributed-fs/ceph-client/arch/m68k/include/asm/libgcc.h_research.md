<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/libgcc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/libgcc.h

## Purpose
`libgcc.h` supplies an architecture-specific 32x32 to 64-bit multiply primitive for common libgcc-style helpers on m68k CPUs that support long multiply.

## Important APIs, Types, and Functions
Unless `CONFIG_CPU_HAS_NO_MULDIV64` is set, it defines `umul_ppmm(w1, w0, u, v)` using `mulu%.l %3,%1:%0` inline assembly to produce high and low product words.

## Control Flow, State, and Persistence
The macro has no persistent state. It emits one multiply sequence and assigns results to caller-provided lvalues.

## Dependencies and Integration Points
`lib/muldi3.c` and other arithmetic helpers can use `umul_ppmm()` for faster 64-bit multiplication. CPUs without the instruction fall back to C implementations.

## Risks
The macro depends on exact compiler constraints and CPU instruction availability. Enabling it on 68000 or ColdFire variants without long multiply would fail at build or runtime.

## Test Signals
Build with and without `CONFIG_CPU_HAS_NO_MULDIV64`, inspect generated assembly, and run 64-bit multiply/divide helper tests over edge values such as zero, max words, and carries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/libgcc.h -->
