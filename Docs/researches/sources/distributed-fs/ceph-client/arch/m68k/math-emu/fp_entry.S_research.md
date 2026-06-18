# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_entry.S

## Purpose
Provides the trap entry point for FPU emulation and helper routines for accessing saved integer/address registers during instruction decoding.

## APIs, Flow, And State
The global entry `fpu_emu` saves interrupt context, gets `current`, adjusts 040/060 PC state when needed, calls `fp_scan`, handles 68060 trace delivery, and returns via `ret_from_exception`. User-access fixup labels `fp_err_ua1` and `fp_err_ua2` repair the stack and call `fpemu_signal(SIGSEGV, SEGV_MAPERR, a0)`. The file also exports `fp_get_data_reg`, `fp_put_data_reg`, `fp_get_addr_reg`, and `fp_put_addr_reg`, using jump tables to read/write saved registers in the trap frame, live callee-saved registers, or USP for A7. `fp_debugprint` stores debug masks.

## Dependencies And Integration
Depends on `SAVE_ALL_INT`, `GET_CURRENT`, m68k pt_regs offsets, `fp_scan`, `fpemu_signal`, `ret_from_exception`, CPU feature symbols, and `fp_emu.h`. Decode and move files call the register helper labels.

## Risks And Test Signals
Register accessor offsets assume the exact saved exception stack layout. User-access fixup stack adjustment must match call depth. Test signals are trapped FPU instructions using every data/address register, user-memory fault tests, 040/060 PC handling, and ptrace/trace behavior on 68060.
