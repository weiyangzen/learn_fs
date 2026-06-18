# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_cond.S

## Purpose
Implements floating-point conditional instructions for the emulator: FDBcc, FScc, FBcc word/long, and condition-code computation.

## APIs, Flow, And State
Global entry points are `fp_fscc`, `fp_fbccw`, and `fp_fbccl`; `fp_fdbcc` is reached through the FScc decode table. Branch handlers compute target PCs from extension displacements and update emulated PC when `fp_compute_cond()` returns true. `fp_fscc` decodes destination effective addresses, writes `0xff` or `0x00` to data register or user memory, and handles data-register byte replacement. `fp_fdbcc` decrements a data register low word when the condition is false and branches if it has not underflowed. `fp_compute_cond()` reads `FPD_FPSR`, optionally raises NaN-related exception bits, and evaluates the 16 Motorola ordered/unordered condition predicates from NAN/Z/N bits.

## Dependencies And Integration
Depends on `fp_decode.h` addressing macros, `fp_emu.h` FPSR offsets, register accessor helpers from `fp_entry.S`, user access fixups, and `fp_end`.

## Risks And Test Signals
Condition behavior is tightly coupled to FPSR bit layout and unordered NaN semantics. Effective-address macros intentionally do not reject every invalid mode. Test signals are FScc/FDBcc/FBcc instruction suites covering all condition codes, NaN comparisons, data-register and memory destinations, PC-relative displacements, and user-access faults.
