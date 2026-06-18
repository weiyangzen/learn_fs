# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpsr.h

## Purpose
Defines the FPA11 floating-point status register and control register bit layout used by NWFPE.

## Important APIs, Types, And Functions
Defines `FPSR`, `FPCR`, system ID bits, trap-enable bits `BIT_IXE` through `BIT_IOE`, system-control bits including `BIT_AC`, exception flags `BIT_IXC` through `BIT_IOC`, FPCR bits, operation/precision/source/destination masks, and write/read masks `MASK_WFC` and `MASK_RFC`.

## Control Flow
No runtime flow. Constants drive `fpa11.inl`, `fpmodule.c`, CPDO rounding, and CPRT FPSR/FPCR behavior.

## State, Dependencies, And Integration
No state itself, but it defines the bit contract for `FPA11.fpsr` and `FPA11.fpcr`. Integrated with user-visible FP state, SoftFloat exception mapping, and comparison condition behavior.

## Risks And Test Signals
Risks are ABI-visible bit mistakes, incorrect trap-enable mapping to cumulative flags, and read/write mask regressions. Test signals are FPSR/FPCR read/write instructions, exception flag tests, SIGFPE trap-enable tests, and user ABI inspection.
