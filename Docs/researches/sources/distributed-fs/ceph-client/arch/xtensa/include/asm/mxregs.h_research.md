<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mxregs.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mxregs.h

## Purpose
Defines external register offsets for the Xtensa MX interrupt distributor and multicore control block.

## Important APIs, Types, And Functions
Macros include `MIROUT`, `MIPICAUSE`, `MIPISET`, `MIENG`, `MIENGSET`, `MIASG`, `MIASGSET`, `MIPIPART`, `SYSCFGID`, `MPSCORE`, and `CCON`.

## Control Flow
No code flow; SMP and interrupt-controller code uses these offsets with external-register read/write instructions.

## State And Persistence
State resides in MX hardware registers controlling IRQ routing, IPI causes, enables, run-stall, and coherency.

## Dependencies And Integration Points
Depends on Xtensa MX hardware and code selected by `XTENSA_MX`/SMP platform support.

## Risks And Edge Cases
Wrong offsets can misroute interrupts or stall cores. IPI partition and coherency registers are hardware-version sensitive.

## Test Signals
Boot SMP MX systems, send IPIs, route external IRQs, offline/online CPUs, and verify cache coherency enable state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mxregs.h -->
