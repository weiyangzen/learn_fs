<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/wof.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/wof.S

## Purpose
Implements the SPARC32 register window overflow trap handler, spilling windows to kernel or user stack and buffering user windows when the user stack is invalid.

## Important APIs, Types, And Functions
Exports `spill_window_entry`, patch labels `spnwin_patch1`, `spnwin_patch2`, `spnwin_patch3`, 7-window patch templates, and `spwin_srmmu_stackchk`. It uses macros such as `LOAD_CURRENT`, `STORE_WINDOW`, `STORE_PT_ALL`, `SAVE_BOLIXED_USER_STACK`, and SRMMU/LEON MMU access patch macros.

## Control Flow
The handler computes the new WIM, determines whether the trap came from user or kernel mode, spills kernel-only windows directly, and handles active user windows by updating `TI_UWINMASK`. For user stack spills, it validates stack alignment and user address range, uses SRMMU no-fault probing around the stores, and either finishes the trap return or buffers the window and calls `window_overflow_fault` through a constructed `pt_regs` frame.

## State And Persistence
Mutates `%wim`, `TI_UWINMASK`, `TI_W_SAVED`, saved register-window buffers, saved stack pointers, and user stack memory. Boot-time patch labels persist to adapt masks and shifts for 7-window versus 8-window CPUs.

## Dependencies And Integration Points
Used by SPARC32 trap table `WINDOW_SPILL`, paired with `wuf.S` and `windows.c`, and depends on SRMMU/LEON MMU no-fault controls, thread-info layout, and C fault routine `window_overflow_fault`.

## Risks And Edge Cases
Register-window handlers run with traps disabled and cannot provoke nested faults casually. User stack addresses in kernel space must be rejected because no-fault probing could otherwise succeed incorrectly. Boot patching for window count must update all mask operations consistently.

## Test Signals
Signals include deep call stacks causing overflow from user and kernel, bogus or unaligned user stack pointers, LEON/Sun SRMMU variants, 7-window CPU boot patching, and recovery via `window_overflow_fault`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/wof.S -->
