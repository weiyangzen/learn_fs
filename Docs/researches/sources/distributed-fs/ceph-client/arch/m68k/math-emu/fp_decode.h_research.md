# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_decode.h

## Purpose
Defines assembler macros for decoding m68k FPU instruction classes, operand formats, addressing modes, extension words, and effective addresses.

## APIs, Flow, And State
The file is macro-only. It documents register conventions: `d2` holds instruction words, `d1` often holds size/count, `a0/a1` hold effective/source addresses, and `a2` points at task/FP state. Macros dispatch through PC-relative jump tables for instruction type and addressing mode, extract bitfields, fetch extension words, compute base/index/outer displacements, handle PC-relative modes unless disabled, and update address registers for postincrement/predecrement. Build-time variables such as `do_fmovem`, `do_fmovem_cr`, `do_no_pc_mode`, and `do_fscc` alter macro behavior.

## Dependencies And Integration
Included by `fp_scan.S`, `fp_move.S`, `fp_movem.S`, and `fp_cond.S`. Depends on user access macros, register accessor routines, debug-print macros, and labels such as `fp_ill` and `fp_err_ua1`.

## Risks And Test Signals
This is a high-risk shared decode layer: a macro bug can affect many instructions. The file explicitly allows some disallowed addressing modes if they do not crash emulation. Test signals are broad effective-address coverage, stack-pointer byte-move adjustment tests, PC-relative addressing, full extension word indexing, and user fault recovery.
