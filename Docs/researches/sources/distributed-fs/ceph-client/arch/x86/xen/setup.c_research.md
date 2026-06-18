<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/setup.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/setup.c

## Purpose
Provides Xen PV x86 machine setup: memory map ingestion, E820 conflict handling, p2m/m2p remapping, initial extra-memory accounting, Xen callback registration, PV MMU setup, syscall callback setup, command-line import, idle policy, and ACPI/NUMA restrictions for PV guests.

## Important APIs, Types, And Functions
Major entry points are `xen_memory_setup`, `xen_remap_memory`, `xen_inv_extra_mem`, `xen_chk_extra_mem`, `xen_chk_is_e820_usable`, `xen_find_free_area`, `xen_enable_syscall`, and `xen_arch_setup`. Important internal helpers include `xen_set_identity_and_remap_chunk`, `xen_do_set_identity_and_remap_chunk`, `xen_update_mem_tables`, `xen_e820_resolve_conflicts`, `xen_e820_swap_entry_with_ram`, `xen_reserve_xen_mfnlist`, and `register_callback`.

## Control Flow
Boot parses the optional `xen_512gb_limit` command-line flag, derives the initial page count, asks Xen for the machine or guest memory map, normalizes it, checks kernel/start_info/page-table/initrd conflicts, computes extra pages needed for remapping, builds the kernel E820 table, identity maps non-RAM regions, reserves or relocates the Xen MFN list and initrd, then records remap work in a linked list stored inside pages being remapped. Later `xen_remap_memory` walks that list, updates p2m/m2p/VA mappings, releases consumed extra memory, and applies non-RAM remaps.

## State And Persistence
Boot-only state includes `xen_e820_table`, `ini_nr_pages`, `xen_remap_buf`, `xen_remap_mfn`, and `xen_512gb_limit`. Persistent runtime effects include modified p2m/m2p mappings, E820 entries, memblock reservations, `xen_extra_mem`, `xen_pv_pci_possible`, callback registration with Xen, disabled cpuidle/cpufreq, and copied boot command line.

## Dependencies And Integration Points
Depends on Xen memory, callback, physdev, feature, and console interfaces; x86 E820, memblock, boot params, fixmaps, NUMA, ACPI, and paravirt idle hooks; p2m code declared in `xen-ops.h`; and syscall entry assembly in `xen-asm.S`.

## Risks And Edge Cases
The most delicate logic is moving non-RAM E820 entries while preserving MFNs, remapping identity-mapped holes without allocating early memory, zapping stale VA mappings, and relocating initrd/p2m data when Xen placed them in E820-reserved ranges. Several failure paths call `BUG()`, making bad hypervisor maps fatal. The 512 GiB domU limit, extra-memory ratio, and hotplug `max_mem_size` interactions can restrict visible memory.

## Test Signals
Test with PV domU and dom0 boots across memory maps containing RAM, reserved, NVS, unusable, initrd conflicts, and high memory; verify E820 logs, p2m consistency, PCI passthrough identity mappings, syscall callback registration, and suspend/resume or balloon activity after remap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/setup.c -->
