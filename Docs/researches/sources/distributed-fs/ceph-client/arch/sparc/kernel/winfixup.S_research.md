<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/winfixup.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/winfixup.S

## Purpose
Handles SPARC64 register-window spill/fill fault fixups when user stack pointers are invalid or memory faults occur during low-level window operations.

## Important APIs, Types, And Functions
Important labels include `fill_fixup`, `spill_fixup`, `spill_fixup_mna`, `spill_fixup_dax`, `winfix_mna`, `fill_fixup_mna`, `winfix_dax`, and `fill_fixup_dax`. It calls `do_sparc64_fault`, `sun4v_do_mna`, `mem_address_unaligned`, `sun4v_data_access_exception`, and `spitfire_data_access_exception`.

## Control Flow
Fill fixups restore the faulting CWP, record fault code/address in thread info, build a normal trap frame via `etrap`, and call the page-fault handler. Spill fixups save the current window into the per-thread register-window buffer in 64-bit or 32-bit layout, increment `TI_WSAVED`, mark the window saved, and either retry privileged spills or enter the fault handler for user spills. MNA and DAX trampoline labels rewrite `%tnpc` so `done` lands at the correct fill fixup variant.

## State And Persistence
Mutates `thread_info` saved-window buffers, saved stack-pointer array, `TI_WSAVED`, `TI_FAULT_CODE`, and `TI_FAULT_ADDR`, plus privileged trap registers CWP/TNPC. Buffered windows persist until C code later syncs or clears them.

## Dependencies And Integration Points
Integrated with SPARC64 register-window spill/fill macros, `urtt_fill.S`, `traps_64.c`, page-fault handling, Sun4v platform detection, and thread-info offsets validated in `trap_init`.

## Risks And Edge Cases
The code cannot freely use trap globals because some contain fault metadata. Stack pointer low-bit and `_TIF_32BIT` checks choose 32-bit versus 64-bit save format. A wrong `saved`/`retry` decision can corrupt the window state or loop in trap context.

## Test Signals
Signals include faults while spilling/filling user windows, unaligned window stack pointers, Sun4v versus Spitfire MNA/DAX dispatch, 32-bit compat window saves, and later successful `synchronize_user_stack` of buffered windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/winfixup.S -->
