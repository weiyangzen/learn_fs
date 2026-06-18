# sources/distributed-fs/ceph-client/arch/arm/lib/backtrace.S

Purpose: implements `c_backtrace` for GCC-style ARM frame-pointer builds. It decodes the classic APCS frame layout containing saved PC, LR, SP, FP, and optional saved registers/arguments.

Control flow validates frame pointers, corrects saved PC for prefetch offset, detects prologue store patterns, calls `dump_backtrace_entry` and `dump_backtrace_stm`, then advances to the previous frame until zero or invalid. Exception-table fixups report aborted backtraces rather than faulting. State is transient. Dependencies include CONFIG_FRAME_POINTER, CONFIG_PRINTK, frame layout emitted by GCC, IRQ stack configuration, and trap dump helpers. Risks are compiler layout drift, corrupted frame chains, 26-bit mode masks, and incomplete traces through nonstandard assembly. Test signals are readable oops/dump_stack traces and bad-frame abort messages rather than secondary faults.
