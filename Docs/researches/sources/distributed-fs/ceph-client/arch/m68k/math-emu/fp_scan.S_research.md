# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_scan.S

## Purpose
Decodes trapped FPU instructions and dispatches them to move, conditional, arithmetic, log, trig, and finalization routines.

## APIs, Flow, And State
The global entry is `fp_scan`, with `fp_datasize` exported as an operand-format size table. `fp_scan` fetches the current user PC, verifies the coprocessor opcode byte, reads the first two instruction words, advances PC, and dispatches by condition/move instruction type. For source-effective-address operations it decodes operand format, converts source data into `FPD_TEMPFP1`, resolves the destination FP register, pushes source/dest pointers and a finalization return, and jumps through a 128-entry operation table. It also handles FPU ROM constants (`fmovecr`) via a constant table and rewrites dispatch for single/double precision variants.

## Dependencies And Integration
Depends on PC get/put and user access macros, `fp_decode.h`, conversion routines from `fp_util.S`, C arithmetic/log/trig symbols, move/movem/condition entries, and `fp_finalrounding`.

## Risks And Test Signals
The opcode dispatch table is the emulator’s central routing point; wrong indices silently bind opcodes to the wrong implementation. Packed BCD and nonstandard opcodes are unsupported. Test signals are instruction decode coverage for every supported operation, operand format conversions, immediate operands, fmovecr constants, single/double precision opcode variants, and illegal-instruction paths.
