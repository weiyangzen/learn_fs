<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/wuf.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/wuf.S

## Purpose
Implements the SPARC32 register window underflow trap handler, filling invalid windows from kernel or user stack and handling invalid user stacks by entering C fault recovery.

## Important APIs, Types, And Functions
Exports `fill_window_entry`, patch labels `fnwin_patch1`, `fnwin_patch2`, 7-window patch templates, and `srmmu_fwin_stackchk`. It uses `LOAD_WINDOW`, `STORE_PT_GLOBALS`, `STORE_PT_YREG`, `STORE_PT_INS`, `STORE_PT_PRIV`, `LOAD_CURRENT`, and SRMMU/LEON no-fault macros.

## Control Flow
The handler computes the next WIM, restores from trap window to the target invalid window, and branches by user/kernel origin. Kernel underflow simply loads from `%sp` and rotates back. User underflow validates stack alignment and address, temporarily enables MMU no-fault mode, attempts to load the window, checks fault status, and either finishes or constructs a `pt_regs` frame and calls `window_underflow_fault`.

## State And Persistence
Mutates `%wim`, register-window contents, `TI_UWINMASK`, `TI_W_SAVED`, and the trap frame built on the kernel stack for fault recovery. Patch labels persist for CPU window-count adaptation.

## Dependencies And Integration Points
Used by the SPARC32 trap table `WINDOW_FILL`, paired with `wof.S`, `windows.c`, SRMMU/LEON MMU accessors, and the C recovery path `window_underflow_fault`.

## Risks And Edge Cases
The invalid window has unusual register ownership; comments explicitly restrict which registers may be used before the load completes. User stack probing must restore MMU no-fault state and recover the expected window position on failure. Kernel over-restore is trusted, so kernel misuse can be fatal.

## Test Signals
Signals include deep returns causing underflow, user stack read faults, unaligned stack pointers, 7-window patch behavior, LEON/Sun MMU variants, and successful C recovery from `window_underflow_fault`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/wuf.S -->
