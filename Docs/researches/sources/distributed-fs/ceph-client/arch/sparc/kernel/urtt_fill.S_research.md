<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/urtt_fill.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/urtt_fill.S

## Purpose
Provides a SPARC64 return-from-trap fill fixup path for user register-window fill faults, restoring enough kernel context to call C fault, unaligned, or data-access handlers safely.

## Important APIs, Types, And Functions
Exports `user_rtt_fill_fixup_common`. It calls `do_sparc64_fault`, `sun4v_do_mna`, `mem_address_unaligned`, `sun4v_data_access_exception`, and `spitfire_data_access_exception` depending on saved fault classification and platform.

## Control Flow
The routine adjusts CWP and WSTATE, restores kernel primary context, saves fault code/address from `%g4/%g5`, drops trap level, restores global level and PSTATE, reloads current/per-CPU state, and then dispatches. A zero saved subtype calls the normal page fault handler; subtype `2` is memory-not-aligned; other values are data-access exceptions. All paths return through `rtrap`.

## State And Persistence
It mutates privileged registers `%cwp`, `%wstate`, `%tl`, `%pstate`, MMU primary context, and per-thread fault fields `TI_FAULT_CODE` and `TI_FAULT_ADDR`. No independent persistent storage exists.

## Dependencies And Integration Points
Integrated with register-window return paths, Sun4v patch sections, ADI/MCD PSTATE handling, `trap_block`, thread-info offsets, and C handlers in `traps_64.c`.

## Risks And Edge Cases
The code runs while unwinding a failed trap return, so register conventions and PSTATE restoration are critical. Sun4v and M7 patches alter MMU/PSTATE behavior. Misclassifying `%l3` would call the wrong C handler for MNA versus DAX.

## Test Signals
Signals include user register-window fill faults during trap return, user stack page faults, unaligned user stack windows, Sun4v versus Spitfire data faults, and ADI-enabled M7 return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/urtt_fill.S -->
