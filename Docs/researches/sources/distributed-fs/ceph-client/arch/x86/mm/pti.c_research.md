# sources/distributed-fs/ceph-client/arch/x86/mm/pti.c

## Purpose
`pti.c` implements x86 Kernel/User Page Table Isolation setup. It decides whether PTI is enabled, builds the user-visible shadow copy of required kernel mappings, clones entry/CPU shared mappings needed for safe transitions, and finalizes permissions after init memory and kernel text protections settle.

## Important APIs, Types, and Functions
Externally relevant functions are `pti_check_boottime_disable()`, `__pti_set_user_pgtbl()`, `pti_init()`, and `pti_finalize()`. Important helpers include PTI command-line parsers, `pti_user_pagetable_walk_p4d/pmd/pte()`, `pti_clone_pgtable()`, `pti_clone_p4d()`, `pti_clone_user_shared()`, `pti_setup_vsyscall()`, `pti_setup_espfix64()`, `pti_clone_entry_text()`, `pti_set_kernel_image_nonglobal()`, and `pti_clone_kernel_text()`.

## Control Flow and State
Boot policy starts in auto mode, disables PTI for Xen PV or mitigated CPUs unless forced, and enables `X86_FEATURE_PTI` for Meltdown-vulnerable or forced-on systems while disabling incompatible `INVLPGB` and `FRED`. `__pti_set_user_pgtbl()` mirrors user PGD entries into the user table and marks kernel copies NX for user pages where possible. `pti_init()` clones CPU entry area/shared TSS scratch space, clears global bits from the kernel image, clones early entry text, ESPFIX, and vsyscall mappings. `pti_finalize()` reclones entry text after permissions have changed, optionally clones safe kernel text/rodata as global for non-PCID auto mode, and runs user page-table W+X checks.

## State and Persistence
Persistent state includes `pti_mode`, CPU feature bits, allocated user shadow page-table pages, global-bit changes in kernel mappings, cloned entry/vsyscall/CPU-entry mappings, and per-mm user PGD synchronization rules. Pages allocated for shadow tables persist for the kernel lifetime.

## Dependencies and Integration Points
The file depends on x86 CPU bug and mitigation detection, hypervisor detection, page-table walkers, `set_memory_global/nonglobal()`, CPU entry area and TSS layout, vsyscall emulation, ESPFIX64, PTI CR3/PCID conventions in TLB code, and boot command-line handling.

## Risks and Test Signals
Risks include exposing too much kernel mapping in user page tables, missing transition-critical mappings, stale shadow tables after late kernel mapping changes, incorrect global-bit policy weakening KASLR, and allocation failures during early boot. Test signals are PTI boot logs, `pti=on/off/auto` behavior, Meltdown mitigation status, syscall/interrupt/NMI transitions, 32-bit PTI warnings on PCID-capable CPUs, vsyscall behavior, ESPFIX64 tests, and `debug_checkwx_user()` output.
