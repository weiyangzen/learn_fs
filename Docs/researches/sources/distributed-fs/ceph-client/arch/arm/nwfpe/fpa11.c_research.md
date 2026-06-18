# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11.c

## Purpose
Owns FPA11 emulator initialization, rounding mode/precision decoding, and top-level opcode dispatch for NWFPE.

## Important APIs, Types, And Functions
Defines `nwfpe_init_fpa`, `SetRoundingMode`, `SetRoundingPrecision`, and `EmulateAll`. Internal `resetFPA11` initializes register type tags and FPSR system ID/AC bit.

## Control Flow
`nwfpe_init_fpa` clears the per-thread `FPA11` state, resets FPSR/type tags, and marks `initflag`. `EmulateAll` checks the coprocessor field for FPA11 CP1/CP2, then distinguishes CPDO/CPRT versus CPDT by opcode class and dispatches to `EmulateCPDO`, `EmulateCPRT`, or `EmulateCPDT`. Unknown opcodes return 0 for undefined-instruction handling.

## State, Dependencies, And Integration
State is `current_thread_info()->fpstate`, including register values, FPSR, FPCR, type tags, and init flag. Dependencies are `fpa11.h`, `fpopcode.h`, `fpmodule.inl`, and SoftFloat rounding constants. Integrated with `entry.S` and thread flush notifier initialization.

## Risks And Test Signals
Risks are opcode misclassification, incorrect initial FPSR compatibility, stale per-thread state, and rounding mode mismatch. Test signals are first-use FP traps, thread flush/exec state reset, CPDO/CPRT/CPDT dispatch tests, and invalid opcode fallback.
