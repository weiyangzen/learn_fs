# sources/distributed-fs/ceph-client/arch/sparc/kernel/fpu_traps.S

## Purpose
`fpu_traps.S` handles sparc64 FPU disabled and FPU exception traps. It lazily restores/saves floating-point state, handles unfinished `fitos` cases, and enters C trap handlers when emulation or exception processing is needed.

## Important APIs, Types, and Functions
Global labels are `do_fpdis`, `do_fpother_check_fitos`, and `do_fptrap`; internal label `fp_other_bounce` calls `do_fpother()`. It uses `TI_FPSAVED`, `TI_FPREGS`, `TI_XFSR`, `TI_GSR`, `FPRS_*`, `TSTATE_PEF`, secondary context registers, block ASIs, and sun4v patch sections.

## Control Flow and State
`do_fpdis()` enables FPRS, restores saved lower/upper FP register halves from thread storage when present, zeroes unsaved halves, restores GSR/FSR, sets `TSTATE_PEF`, clears dirty FPRS bits, and retries. If FPU state is already enabled in a special Cheetah state it traps through `etrap`. `do_fpother_check_fitos()` detects a specific unfinished integer-to-single conversion without inexact, decodes source/destination registers via jump tables, emulates with `fitod` then `fdtos`, restores `%f62`, and `done`s. Other cases enter `do_fptrap_after_fsr`, save dirty FP banks and GSR/FSR to thread_info, clear FPRS, and branch to `etrap`.

## Persistence and Dependencies
Persistent state is per-thread FP register storage, FSR, GSR, and FPRS dirty/saved flags. Dependencies include V9 FP register layout, DMMU/MMU context ASIs, thread_info offsets, and C handlers declared in `entry.h`.

## Integration Points, Risks, and Test Signals
Integration is with lazy FPU context switching, signal/ptrace FP state, and trap return. Risks include stale secondary context restoration, partial FP bank saves, incorrect `fitos` instruction decoding, and trap recursion while accessing thread FP storage. Test signals include FP-heavy context switching, ptrace/signal FP register validation, unfinished FP exception tests, and sun4v versus sun4u ASI patch coverage.
