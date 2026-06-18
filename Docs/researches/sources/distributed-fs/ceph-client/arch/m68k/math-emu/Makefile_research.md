# sources/distributed-fs/ceph-client/arch/m68k/math-emu/Makefile

## Purpose
Builds the m68k floating-point emulator object set.

## APIs, Flow, And State
The Makefile adds `fp_entry.o`, `fp_scan.o`, `fp_util.o`, `fp_move.o`, `fp_movem.o`, `fp_cond.o`, `fp_arith.o`, `fp_log.o`, and `fp_trig.o` to `obj-y`. Optional debug flags for assembler and C are present but commented out.

## Dependencies And Integration
Consumed by Kbuild when the m68k FPU emulator is enabled. The listed objects form a pipeline: trap entry, instruction scan/decode, user-memory move/movem/condition handling, conversions/finalization, and C arithmetic/log/trig kernels.

## Risks And Test Signals
Object order matters mainly through symbol availability during linkage, not runtime sequencing. Enabling debug flags would change logging volume in trap context. Test signals are successful m68k FPU-emulator builds and execution of trapped FPU instructions on systems without hardware FPU or for unsupported instructions.
