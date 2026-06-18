# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_movem.S

## Purpose
Implements FPU multiple-register moves for data FP registers and FP control registers.

## APIs, Flow, And State
Global entries are `fp_fmovem_fp` and `fp_fmovem_cr`. `fp_fmovem_fp` decodes static or dynamic FP register masks, counts selected registers for addressing updates, decodes memory effective address, and moves 12-byte extended register images between user memory and `FPD_FPREG`, supporting incremental and decremental order. `fp_fmovem_cr` moves FPCR/FPSR/FPIAR between data/address registers, immediate/memory operands, and `FPDATA`; after writes it masks reserved bits and derives cached `FPD_RND` and `FPD_PREC` fields from FPCR.

## Dependencies And Integration
Depends on decode macros configured with `do_fmovem` and `do_fmovem_cr`, user access helpers, `FPDATA` offsets, and register helpers. It is selected by `fp_scan.S` move-type dispatch for `fmovem` encodings.

## Risks And Test Signals
Register masks, predecrement order, and 12-byte extended layout are easy to regress. Control-register reserved-bit masking affects later rounding and precision globally for the task’s emulated FPU state. Test signals are FMOVEM static/dynamic masks, predecrement/postincrement modes, FPCR rounding/precision effects, FPSR/FPIAR transfer tests, and user fault recovery.
