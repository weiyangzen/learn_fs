# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_move.S

## Purpose
Implements `fmove` from emulated FP registers to integer registers or memory in the m68k FPU emulator.

## APIs, Flow, And State
The global entry is `fp_fmove_fp2mem`. It clears current exception status, decodes destination format and effective address, fetches the source FP register into a temporary stack-backed copy, normalizes it, converts to byte/word/long/single/double/extended as requested, writes to data registers or user memory, and jumps to `fp_final`. Packed decimal output is explicitly unsupported and routes to `fp_ill`. Data-register writes preserve unaffected bytes/words by reading the existing register and replacing only the requested portion.

## Dependencies And Integration
Depends on `fp_decode.h`, `fp_emu.h`, register accessors from `fp_entry.S`, conversion/finalization routines in `fp_util.S`, and user access exception labels. Called from `fp_scan.S` when the decoded move type is register-to-effective-address.

## Risks And Test Signals
Stack use around 12-byte temporary operands must match cleanup paths, especially unsupported packed formats. Correctness depends on destination-size conversion and rounding status. Test signals are FMOVE from FP registers to all supported data sizes, register partial writes, postincrement/predecrement address updates, user-memory fault handling, and packed-format illegal-instruction behavior.
