# Research: subset-b-000910

This grouped report covers x86 memory-management page attribute, page-table, PTI, TLB, NUMA SRAT, mmiotrace test, and architecture network build-selection files. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/set_memory.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pat/set_memory.c

## Purpose
`set_memory.c` implements x86 change-page-attribute (CPA) operations for kernel mappings. It changes cacheability, execute/write/present/global/encryption bits, keeps direct-map and high-kernel-map aliases coherent, splits and collapses large mappings when required, and provides the exported `set_memory_*()` and `set_pages_*()` APIs used by drivers, debug page allocation, memory failure recovery, confidential-computing guests, EFI mapping setup, and vmalloc/ioremap users.

## Important APIs, Types, and Functions
The central state object is `struct cpa_data`, which carries the target address or page array, optional alternate `pgd`, masks to set and clear, current PFN/page cursor, flags such as `CPA_ARRAY`, `CPA_PAGES_ARRAY`, `CPA_NO_CHECK_ALIAS`, and `CPA_COLLAPSE`, and split/flush controls. Public APIs include `lookup_address()`, `lookup_address_in_pgd()`, `lookup_pmd_address()`, `slow_virt_to_phys()`, `clflush_cache_range()`, `set_memory_uc/wc/wb/x/nx/ro/rox/rw/np/p/4k/nonglobal/global()`, `set_mce_nospec()`, `clear_mce_nospec()`, `set_memory_encrypted()`, `set_memory_decrypted()`, `set_pages_*()`, direct-map noflush helpers, `kernel_page_present()`, and boot-only `kernel_map_pages_in_pgd()`/`kernel_unmap_pages_in_pgd()`.

## Control Flow and State
Callers enter through `change_page_attr_set_clr()`, which canonicalizes unsupported protection bits, aligns inputs, flushes highmem/vmalloc aliases, fills `cpa_data`, and delegates to `__change_page_attr_set_clr()`. The inner loop resolves each current target with `_lookup_address_cpa()`, handles absent entries through `__cpa_process_fault()`, updates 4K PTEs directly, or calls `should_split_large_page()` to preserve, split, or rewrite large pages. Static protection enforcement prevents unsafe changes to executable kernel text, read-only rodata, and PCI BIOS ranges. Alias processing updates the direct map and, on x86-64, the high kernel text/data mapping for the same PFN. If any entry changed, `cpa_flush()` selects all-CPU TLB flushes, single-page flushes, cache writeback/invalidation, and optional large-page collapse.

## State and Persistence
Persistent kernel state includes direct-map page-size counters exposed in `/proc/meminfo`, optional CPA debugfs counters, memtype reservations for UC/WC/WB transitions, `mem_enc_lock` serialization for private/shared memory conversion, global PGD synchronization through `pgd_lock`/`pgd_list`, and page-table pages allocated or freed by split/collapse paths. Hardware-visible state is the page-table tree, TLB contents, CPU caches, and guest encryption attribute notifications.

## Dependencies and Integration Points
This file depends on PAT/memtype tracking, x86 page-table helpers, TLB flush primitives, highmem and vmalloc alias management, debugfs/procfs, memblock/E820, paravirt page-table hooks, confidential-computing platform callbacks, MCE poison-page recovery, debug page allocation, and KVM/EFI callers that need alternate PGDs or exact physical translation behavior.

## Risks and Test Signals
Risks are concentrated around stale large-page TLB entries during split/collapse, alias mismatches between direct map and high map, static-protection bypasses, incorrect cache-mode reservation rollback, non-canonical MCE decoy addresses, and conversion races between encrypted and decrypted memory. Test signals include CPA debugfs counter movement, direct-map size accounting, W^X warnings, successful module/vmalloc/ioremap cache-mode transitions, MCE poison isolation, debug-pagealloc present-bit toggling, EFI boot mappings before SMP, and confidential-guest shared/private conversion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/set_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pf_in.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pf_in.c

## Purpose
`pf_in.c` is the x86 instruction decoder used by mmiotrace page-fault interception. It classifies simple MMIO load/store instructions and extracts register, immediate, and memory access widths from the faulting instruction stream so mmiotrace can report what a trapped access attempted.

## Important APIs, Types, and Functions
The exported local interface from `pf_in.h` is implemented by `get_ins_type()`, `get_ins_mem_width()`, `get_ins_reg_val()`, and `get_ins_imm_val()`. Internal helpers include `skip_prefix()`, `get_opcode()`, `get_ins_reg_width()`, `get_reg_w8()`, and `get_reg_w32()`. Opcode tables classify register reads, register writes, immediate writes, and 8/16/32/64-bit memory widths, with separate i386 and amd64 prefix/opcode handling.

## Control Flow and State
Each decoder starts at `ins_addr`, strips recognized prefixes, including operand-size and REX prefixes on amd64, reads one- or two-byte opcodes, and searches static opcode arrays. Register-value extraction decodes the ModR/M register field, accounts for REX.R extension, treats `STOS` as fixed to AX, and returns a value from `struct pt_regs` using the inferred operand width. Immediate extraction skips ModR/M displacement forms before reading the immediate payload.

## State and Persistence
The file has no persistent mutable state beyond static opcode tables. It reads the faulting instruction bytes and saved register frame and emits diagnostic `printk()` errors for unsupported or malformed instructions.

## Dependencies and Integration Points
It depends on x86 instruction encoding, `struct pt_regs`, kernel `ARRAY_SIZE`, and the mmiotrace page-fault path that includes `pf_in.h`. It is intentionally narrow rather than a full instruction decoder.

## Risks and Test Signals
Risks include incomplete opcode coverage, unsafe instruction-byte reads if the faulting IP is unexpected, partial SIB/address-size handling in immediate decoding, and register-width mistakes around REX byte-register semantics. Test signals are mmiotrace logs showing correct read/write/immediate classification and widths for `ioread*()`, `iowrite*()`, and string-store patterns, plus error logs only for intentionally unsupported instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pf_in.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pf_in.h -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pf_in.h

## Purpose
`pf_in.h` defines the small mmiotrace fault-instruction decoding contract shared by the page-fault interception code and `pf_in.c`.

## Important APIs, Types, and Functions
`enum reason_type` describes how a faulting instruction relates to the traced MMIO region: `NOT_ME`, `NOTHING`, `REG_READ`, `REG_WRITE`, `IMM_WRITE`, and `OTHERS`. The declared functions are `get_ins_type()`, `get_ins_mem_width()`, `get_ins_reg_val()`, and `get_ins_imm_val()`.

## Control Flow and State
There is no runtime control flow or storage in the header. It fixes the classification vocabulary and decoder function signatures. `struct pt_regs` is used by declaration without being defined here, so includers must already have the appropriate architecture register context available.

## Dependencies and Integration Points
The header is local to x86 MM mmiotrace support and integrates with `pf_in.c` plus the mmiotrace fault handler that needs to decide whether a page fault represents an MMIO access to log or emulate.

## Risks and Test Signals
Risks are ABI drift between the enum meanings and mmiotrace callers, and missing includes if declarations are reused outside the existing path. Test signals are successful x86 builds with mmiotrace enabled and correct classification labels in mmiotrace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pf_in.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pgprot.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pgprot.c

## Purpose
`pgprot.c` maps Linux VMA permission flags to x86 page-protection encodings and applies memory-encryption and protection-key bits where needed.

## Important APIs, Types, and Functions
The file owns the `protection_map[16]` table, marked `__ro_after_init`, indexed by `VM_READ`, `VM_WRITE`, `VM_EXEC`, and `VM_SHARED`. Public functions are `add_encrypt_protection_map()` and exported `vm_get_page_prot()`.

## Control Flow and State
`add_encrypt_protection_map()` mutates every table entry with `pgprot_encrypted()` during encryption setup. `vm_get_page_prot()` selects the table entry for a VMA flag combination, folds in Intel memory-protection-key bits from `VM_PKEY_BIT0..3` when configured, applies `__sme_set()`, masks present entries with `__supported_pte_mask`, and returns the final `pgprot_t`.

## State and Persistence
The protection map persists after init and becomes read-only. Returned protections are not stored here; they are consumed by generic MM when creating PTEs for VMAs. Encryption setup permanently changes the baseline table for the running kernel.

## Dependencies and Integration Points
It depends on x86 page-protection constants, SME memory encryption helpers, optional Intel pkeys, and generic MM `vm_get_page_prot()` callers such as mmap, mprotect, and fault handling.

## Risks and Test Signals
Risks include unsupported bits escaping into present PTEs, wrong copy-vs-shared mappings for writeable private VMAs, and pkey bit mismatches between `vm_flags` and PTE encoding. Test signals are mmap/mprotect permission tests, pkey tests, SME encrypted memory boot/runtime tests, and W^X checks for executable mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pgprot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pgtable.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pgtable.c

## Purpose
`pgtable.c` provides x86 page-table allocation, freeing, PGD synchronization, access-bit operations, fixmap installation, huge-vmap helpers, and shadow-stack-aware write-protection helpers. It is the architecture layer between generic MM and x86 paging details.

## Important APIs, Types, and Functions
Key APIs include `pte_alloc_one()`, `___pte_free_tlb()`, `___pmd_free_tlb()`, `___pud_free_tlb()`, `___p4d_free_tlb()`, `pgd_alloc()`, `pgd_free()`, `ptep_set_access_flags()`, transparent-hugepage access helpers, `reserve_top_address()`, `native_set_fixmap()`, `pud_set_huge()`, `pmd_set_huge()`, huge-entry clear/free helpers, `pte_mkwrite()`, `pmd_mkwrite()`, and `arch_check_zapped_pte/pmd/pud()`. `physical_mask` is exported when dynamic physical masks are configured.

## Control Flow and State
PGD allocation creates the top-level table, preallocates PMDs where PAE and PTI require them, invokes paravirt allocation hooks, and adds the PGD to `pgd_list` under `pgd_lock` so kernel mapping changes can be synchronized. Freeing tears down preallocated PMDs, removes list membership, releases paravirt state, and frees the PGD. Access-flag helpers update PTE/PMD/PUD entries only when generic MM needs hardware-visible write/accessed changes. Fixmap setup resolves a fixed-address index to a virtual address and installs a sanitized PTE through `set_pte_vaddr()`. Huge-vmap helpers install or clear PMD/PUD huge mappings only when MTRR cache modes are uniform.

## State and Persistence
Persistent state includes each `mm_struct` PGD, preallocated kernel/user PMDs for PAE/PTI, the global `pgd_list`, per-table paravirt allocation state, `fixmaps_set`, `__FIXADDR_TOP`, and page-table page reference/accounting counters. Page aging state lives in hardware accessed bits that this file can test and clear.

## Dependencies and Integration Points
Dependencies include `asm/pgalloc.h`, paravirt hooks, `mmu_gather`, transparent hugepage support, fixmap code, MTRR type lookup, PTI helpers, shadow-stack PTE encodings, and generic mmap/fault/unmap paths.

## Risks and Test Signals
Risks include partial PGD prepopulation visible to `pgd_list` walkers, missing CR3 reloads in PAE, freeing page-table pages before TLB invalidation, huge mapping over non-uniform MTRR ranges, and mishandling shadow-stack dirty/write encodings. Test signals include fork/exec/exit page-table stress, PAE and PTI boot tests, vmalloc/ioremap huge-vmap behavior, THP access-bit tests, fixmap users, and CET shadow-stack selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pgtable_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pgtable_32.c

## Purpose
`pgtable_32.c` contains x86-32-specific page-table support for kernel virtual mappings, fixmap top placement, vmalloc sizing, and early reservation of top kernel address space.

## Important APIs, Types, and Functions
The important symbols are mutable `__VMALLOC_RESERVE`, `set_pte_vaddr()`, exported `__FIXADDR_TOP`, early-parameter handlers `parse_vmalloc()` and `parse_reservetop()`, and the `vmalloc=`/`reservetop=` command-line hooks.

## Control Flow and State
`set_pte_vaddr()` walks `swapper_pg_dir` down to the kernel PTE for a virtual address, installs or clears the PTE through `set_pte_at()`/`pte_clear()`, and flushes that single kernel TLB entry. `parse_vmalloc()` parses a requested vmalloc size and adds the guard-hole offset. `parse_reservetop()` reserves a top-of-address-space hole, relocates the fixmap via `reserve_top_address()`, and reinitializes early ioremap state.

## State and Persistence
The file persists boot-selected vmalloc reserve size and fixmap top address. It mutates kernel page tables and TLBs for fixed mappings, and the early parameters affect the whole 32-bit kernel virtual layout.

## Dependencies and Integration Points
It depends on x86-32 page-table layout, fixmap, early ioremap, E820/top reservation logic, vmalloc, and TLB flushing. `set_pte_vaddr()` is used by generic x86 fixmap code in `pgtable.c`.

## Risks and Test Signals
Risks include BUG-triggering missing upper-level entries, bad `vmalloc=` values crowding lowmem/fixmap areas, and reservetop relocation after fixmaps are already established. Test signals are 32-bit boot with `vmalloc=` and `reservetop=`, early ioremap users, fixmap setup, and single-entry TLB flush correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pgtable_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/physaddr.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/physaddr.c

## Purpose
`physaddr.c` validates and translates kernel virtual addresses to physical addresses on x86, with DEBUG_VIRTUAL checks that catch invalid direct-map, vmalloc, fixmap, and high-kernel-map use.

## Important APIs, Types, and Functions
On DEBUG_VIRTUAL builds it exports `__phys_addr()`. All builds export `__virt_addr_valid()`. x86-64 handles both `__START_KERNEL_map` image addresses and direct-map addresses using `phys_base`; x86-32 handles `PAGE_OFFSET` direct-map addresses and rejects vmalloc/fixmap ranges.

## Control Flow and State
x86-64 translation subtracts `__START_KERNEL_map` and uses carry-style comparisons to distinguish high kernel image aliases from direct-map addresses, then validates the resulting physical address and PFN. x86-32 DEBUG_VIRTUAL translation checks that the virtual address is above `PAGE_OFFSET`, not vmalloc once the vmalloc base is set, and within `max_low_pfn`, then cross-checks `slow_virt_to_phys()`.

## State and Persistence
No state is owned here. The functions read `phys_base`, `KERNEL_IMAGE_SIZE`, `max_low_pfn`, `__vmalloc_start_set`, and memmap PFN validity.

## Dependencies and Integration Points
It depends on `phys_addr_valid()` from `physaddr.h`, `pfn_valid()`, vmalloc address classification, and architecture virtual layout constants. It supports `virt_addr_valid()` users across MM, drivers, and debug code.

## Risks and Test Signals
Risks include accepting non-direct-map virtual addresses, rejecting valid highmap aliases under KASLR, and stale `max_low_pfn` assumptions very early in boot. Test signals are DEBUG_VIRTUAL warnings for bad `__pa()` users, boot on KASLR/non-KASLR kernels, vmalloc rejection tests, and highmem/direct-map validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/physaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/physaddr.h -->
# sources/distributed-fs/ceph-client/arch/x86/mm/physaddr.h

## Purpose
`physaddr.h` provides the local x86 physical-address validity predicate used by `physaddr.c`.

## Important APIs, Types, and Functions
The sole helper is `phys_addr_valid(resource_size_t addr)`. With `CONFIG_PHYS_ADDR_T_64BIT`, it checks that no address bits exist above `boot_cpu_data.x86_phys_bits`; otherwise it treats all resource-sized addresses as valid.

## Control Flow and State
The function is inline and stateless. Its only branch is configuration-dependent and, on 64-bit physical-address builds, compares the address width against CPU-reported physical address bits.

## Dependencies and Integration Points
It depends on `boot_cpu_data` from `<asm/processor.h>` and is included by `physaddr.c` to validate direct-map translations.

## Risks and Test Signals
Risks are limited but important: stale or wrong `x86_phys_bits` would make virtual-address validation too permissive or too strict. Test signals include DEBUG_VIRTUAL behavior on systems with different physical address widths and memory hotplug or high-address memory configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/physaddr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pkeys.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pkeys.c

## Purpose
`pkeys.c` manages x86 Intel Memory Protection Keys policy around execute-only mappings and initial PKRU defaults. It lets normal `mprotect(PROT_EXEC)` transparently use a pkey to deny data reads while allowing instruction fetches.

## Important APIs, Types, and Functions
Key functions are `__execute_only_pkey()`, `__arch_override_mprotect_pkey()`, debugfs handlers for `init_pkru`, and boot option parser `setup_init_pkru()`. Persistent `init_pkru_value` initializes pkey access-disallow bits for pkeys 1 through 15 while leaving pkey 0 usable.

## Control Flow and State
`__execute_only_pkey()` lazily allocates `mm->context.execute_only_pkey`, checks current PKRU to avoid redundant writes, then calls `arch_set_user_pkey_access()` with `PKEY_DISABLE_ACCESS`. If setup fails, it frees the key and disables execute-only pkey use for that attempt. `__arch_override_mprotect_pkey()` preserves explicit `mprotect_pkey()` values, assigns the execute-only pkey for plain `PROT_EXEC`, resets former execute-only VMAs to `ARCH_DEFAULT_PKEY` when protections broaden, or inherits the existing VMA pkey otherwise. Debugfs and `init_pkru=` allow controlled tuning of default PKRU.

## State and Persistence
State persists in each `mm_struct` execute-only pkey, per-thread PKRU hardware state, and global `init_pkru_value`. The debugfs write path rejects disabling access or writes on pkey 0 to avoid immediate system breakage.

## Dependencies and Integration Points
It depends on CPU `OSPKE`, Linux pkey allocation helpers, `vma_pkey()`, PKRU read/write helpers, debugfs, user-copy parsing, and generic mprotect paths.

## Risks and Test Signals
Risks include failing open to readable executable mappings if pkey allocation or PKRU writes fail, per-thread PKRU inheritance surprises, and unsafe `init_pkru=` values from boot or debugfs. Test signals are pkeys selftests, execute-only mmap/mprotect behavior, debugfs `init_pkru` read/write validation, and context-switch PKRU preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pkeys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pti.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/srat.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/srat.c

## Purpose
`srat.c` handles x86 ACPI SRAT CPU-affinity parsing for NUMA setup. It maps ACPI proximity domains to Linux NUMA nodes and associates LAPIC/x2APIC IDs with those nodes.

## Important APIs, Types, and Functions
The ACPI callbacks are `acpi_numa_x2apic_affinity_init()` and `acpi_numa_processor_affinity_init()`. `x86_acpi_numa_init()` calls generic `acpi_numa_init()` and returns failure if SRAT was disabled.

## Control Flow and State
Each affinity callback first exits if SRAT is disabled, validates record length, ignores disabled CPUs, extracts the proximity domain, maps it to a node through `acpi_map_pxm_to_node()`, validates APIC IDs, and records `set_apicid_to_node()`. The LAPIC path composes larger proximity domains for SRAT revision 2+ and handles UV x2APIC-style APIC IDs by combining APIC ID and SAPIC EID.

## State and Persistence
The file updates global APIC-ID-to-node mappings and marks `numa_nodes_parsed` and `numa_phys_nodes_parsed`. `bad_srat()` can disable or invalidate SRAT-derived NUMA setup.

## Dependencies and Integration Points
It depends on ACPI SRAT structures, generic ACPI NUMA parsing, x86 APIC ID validation, UV system-type detection, topology node masks, and early NUMA initialization.

## Risks and Test Signals
Risks include malformed SRAT lengths, proximity-domain overflow, too-large APIC IDs, UV APIC-ID interpretation mismatches, and assuming memory regions per proximity domain are contiguous enough for higher-level NUMA code. Test signals are boot logs mapping PXM to APIC/node, NUMA node CPU masks, SRAT disabled/fallback behavior, and validation on LAPIC, x2APIC, and UV systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/srat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/testmmiotrace.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/testmmiotrace.c

## Purpose
`testmmiotrace.c` is a deliberately dangerous test module for mmiotrace. Given a caller-supplied MMIO address, it maps the region, performs known 8/16/32-bit writes and reads, optionally performs a far read, and stress-tests repeated ioremap/iounmap reuse.

## Important APIs, Types, and Functions
Module parameters are `mmio_address` and `read_far`. Test helpers are `v16()`, `v32()`, `do_write_test()`, `do_read_test()`, `do_read_far_test()`, `do_test()`, and `do_test_bulk_ioremapping()`. Module lifecycle functions are `init()` and `cleanup()`.

## Control Flow and State
`init()` checks lockdown policy with `security_locked_down(LOCKDOWN_MMIOTRACE)`, requires `mmio_address`, warns loudly, chooses 16 KiB or 8 MiB mapping size, runs the read/write tests, performs repeated one-page mappings, forces RCU synchronization, and exits. `do_test()` wraps `ioremap()`, logs the returned virtual mapping through `mmiotrace_printk()`, performs writes, reads back expected values, optionally performs the far read, and unmaps.

## State and Persistence
Persistent module state is limited to parameters. External state is intentionally affected: the module writes test patterns to the supplied MMIO/PCI address space and emits mmiotrace records and kernel logs.

## Dependencies and Integration Points
It depends on mmiotrace, `ioremap()`/`iounmap()`, `ioread*()`/`iowrite*()`, RCU deferred freeing, kernel lockdown policy, and module parameter infrastructure.

## Risks and Test Signals
Risks are explicit: loading against a real device BAR can corrupt hardware state. Other risks include invalid addresses, read side effects, and test assumptions about writable/readable MMIO. Test signals are mmiotrace logs for each access width, read error counters, successful far-read logging, no crash during bulk ioremap reuse, and lockdown preventing use when policy forbids mmiotrace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/testmmiotrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/tlb.c

## Purpose
`tlb.c` implements x86 TLB context management, PCID/ASID allocation, local and remote shootdowns, lazy TLB handling, global-ASID broadcast invalidation, PTI user-PCID invalidation, temporary-mm switching, and debugfs tuning of single-page flush thresholds.

## Important APIs, Types, and Functions
Important entry points include `switch_mm()`, `switch_mm_irqs_off()`, `leave_mm()`, `initialize_tlbstate_and_flush()`, `flush_tlb_mm_range()`, `flush_tlb_all()`, `flush_tlb_kernel_range()`, `flush_tlb_one_kernel()`, `flush_tlb_one_user()`, `flush_tlb_local()`, `__flush_tlb_all()`, `arch_tlbbatch_flush()`, `use_temporary_mm()`, `unuse_temporary_mm()`, `nmi_uaccess_okay()`, and KVM-exported `__get_current_cr3_fast()`. Core state is per-CPU `cpu_tlbstate`/`cpu_tlbstate_shared`, `struct flush_tlb_info`, per-mm `context.tlb_gen`, dynamic ASID slots, and optional global ASIDs.

## Control Flow and State
Context switching chooses an ASID with `choose_new_asid()`, optionally assigns global ASIDs for processes active on many CPUs when `INVLPGB` is available, writes CR3 with or without `CR3_NOFLUSH`, updates per-ASID generation state, maintains `mm_cpumask()`, and applies IBPB/L1D/PCE/LDT mitigations. Flush requests increment the mm TLB generation, build per-CPU flush info, choose broadcast `INVLPGB`, remote IPI, or local direct flushing, and then update secondary MMU notifiers. Remote `flush_tlb_func()` compares local and target generations, skips lazy CPUs when safe, uses partial single-page invalidations only when generation ordering proves they are sufficient, otherwise performs full local flushes.

## State and Persistence
Persistent state includes per-CPU loaded mm/asid/LAM state, lazy flags, user-PCID flush masks, ASID generation slots, global ASID allocation bitmaps and rollover state, `last_user_mm_spec` mitigation tracking, `tlb_single_page_flush_ceiling`, and debugfs control for that ceiling. Temporary-mm use disables breakpoints while active and clears cpumasks on exit to avoid unnecessary shootdowns.

## Dependencies and Integration Points
This file depends on x86 CR3/PCID/INVPCID/INVLPGB/PTI/LAM semantics, scheduler context switching, mmu_gather and unmap batching, CPU hotplug, perf RDPMC policy, LDT switching, speculation mitigations, KVM CR3 restoration, MMU notifiers, paravirt TLB hooks, debugfs, and trace/vmstat TLB events.

## Risks and Test Signals
Risks include missed generation ordering causing stale translations, freeing page tables without flushing lazy CPUs, ASID reuse without adequate invalidation, global ASID transition races, PTI user-PCID flush mask mistakes, CR3 state mismatches during NMIs or temporary-mm use, and performance regressions from over-flushing. Test signals include context-switch stress, munmap/mprotect/mremap shootdown tests, THP flush ranges, CPU hotplug reinitialization, PTI+PCID boot, INVLPGB-capable broadcast paths, KVM CR3 checks, membarrier ordering tests, perf RDPMC availability changes, and debugfs threshold tuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/net/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/net/Makefile

## Purpose
`arch/x86/net/Makefile` selects the architecture-specific eBPF JIT objects built for x86 networking.

## Important APIs, Types, and Functions
There are no C APIs. The build variables add `bpf_jit_comp32.o` for `CONFIG_X86_32=y`, or `bpf_jit_comp.o` plus `bpf_timed_may_goto.o` for non-32-bit x86, all gated by `CONFIG_BPF_JIT`.

## Control Flow and State
Kbuild evaluates the `ifeq ($(CONFIG_X86_32),y)` branch at build time. Runtime behavior is entirely in the selected object files.

## State and Persistence
The file owns no runtime state. Its persistent effect is the object list recorded in the kernel build graph for the selected configuration.

## Dependencies and Integration Points
It integrates with Kbuild, x86 config symbols, and the BPF JIT implementation under `arch/x86/net`. The 64-bit path includes timed `may_goto` support in addition to the main JIT compiler.

## Risks and Test Signals
Risks include building the wrong JIT object for 32-bit versus 64-bit kernels or omitting auxiliary 64-bit BPF support. Test signals are `CONFIG_BPF_JIT` x86_32 and x86_64 builds, BPF selftests, and module/object presence in build logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/net/Makefile -->
