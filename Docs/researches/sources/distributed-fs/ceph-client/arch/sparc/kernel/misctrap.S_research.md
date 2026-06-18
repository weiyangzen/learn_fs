# sources/distributed-fs/ceph-client/arch/sparc/kernel/misctrap.S

Purpose: Provides miscellaneous SPARC64 trap entry stubs for KGDB breakpoints, privileged action traps, memory-not-aligned traps, floating load/store alignment emulation, and breakpoints.

Important APIs/types/functions: Under `CONFIG_KGDB`, `arch_kgdb_breakpoint` emits `ta 0x72` and returns. `__do_privact` clears the DMMU fault-valid bit and calls `do_privact()`. `do_mna` captures DMMU fault address/status, clears fault-valid, handles higher trap levels through `winfix_mna`, or calls `mem_address_unaligned()`. `do_lddfmna` and `do_stdfmna` call `handle_lddfmna()` and `handle_stdfmna()`. `breakpoint_trap` calls `sparc_breakpoint()`.

Control flow: Each trap stub prepares `%g7` for `etrap`, branches into the common trap entry path, passes `pt_regs` at `%sp + PTREGS_OFF` plus saved fault information to C handlers, and returns through `rtrap`. The unaligned access path has an early high-trap-level branch to window-fixup handling.

State and persistence: The stubs mutate MMU fault status registers by clearing `TLB_SFSR`, use DMMU SFAR/SFSR values as arguments, and rely on trap-frame state built by `etrap`. No persistent memory is allocated.

Dependencies and integration points: It depends on SPARC64 trap entry/return assembly (`etrap`, `rtrap`, `winfix_mna`), MMU ASIs, KGDB, and C handlers for privileged action, alignment, floating memory alignment, and breakpoints.

Risks and test signals: Incorrect register handoff to C handlers misreports fault address/status. Failure to clear fault-valid can retrigger traps. Tests include KGDB breakpoint entry, unaligned user/kernel memory access, lddf/stdf alignment emulation, privileged action traps, high trap-level MNA handling, and breakpoint trap dispatch.
