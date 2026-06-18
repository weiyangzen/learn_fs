# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_uv_x.c

## Purpose
This file implements the SGI/HPE UV x2APIC/APIC driver and UV platform bring-up path. It detects UV hubbed and hubless systems from ACPI MADT OEM IDs and UVsystab data, configures UV hub type and APIC behavior, maps UV MMR/GRU/MMIOH regions, builds socket/pnode/node translation tables, initializes per-CPU/per-hub UV state, and exposes legacy `/proc/sgi_uv` compatibility files.

## Important APIs, Types, and Functions
Core exported state includes `get_uv_system_type()`, `uv_get_hubless_system()`, `uv_get_archtype()`, `is_uv_system()`, `is_uv_hubbed()`, `__uv_hub_info_list`, per-CPU `__uv_cpu_info`, `uv_possible_blades`, and `sn_rtc_cycles_per_second`. Early detection is centered on `uv_acpi_madt_oem_check()`, `uv_set_system_type()`, `early_get_arch_type()`, `early_set_hub_type()`, `early_get_pnodeid()`, and `early_get_apic_socketid_shift()`. Runtime platform setup is split between `uv_system_init()`, `uv_system_init_hub()`, and `uv_system_init_hubless()`.

The APIC integration is the `apic_x2apic_uv_x` descriptor registered with `apic_driver()`. Its IPI methods route through UV global MMR writes in `uv_send_IPI_one()`, mask variants, and `uv_wakeup_secondary()`. Memory and address routing helpers include `decode_uv_systab()`, `decode_gam_params()`, `decode_gam_rng_tbl()`, `build_uv_gr_table()`, `build_socket_tables()`, `map_gru_high()`, `map_mmr_high()`, `map_mmioh_high()`, and `calc_mmioh_map()`.

## Control Flow
During APIC probing, the MADT OEM hook seeds CPU0 hub info and calls `uv_set_system_type()`. Hubbed systems require UV arch strings such as `SGI*`, NUMA enabled, valid hub revision/type, and UV MMR reads. Hubless systems use `NSGI*` arch strings and record hubless generation bits but do not select the UV APIC driver. Later, `uv_system_init()` dispatches to hubbed or hubless initialization. Hubbed initialization maps low MMRs, initializes UV BIOS, decodes UVsystab entries, builds conversion tables, maps high GRU/MMR/MMIOH windows, fills hub structures per blade and node, assigns CPU-to-hub pointers, installs UV NMI handling, registers VGA redirection, and adjusts reboot behavior. Hubless initialization is narrower: NMI, BIOS, UVsystab, block size, proc compatibility, and reboot fallback.

## State and Persistence
Most state is boot-time global or `__initdata` that is discarded after setup. Persistent runtime state includes `uv_system_type`, hubless/hubbed bitmasks, arch/OEM strings, per-node `__uv_hub_info_list`, per-CPU `__uv_cpu_info`, possible blade count, RTC frequency, and selected x86 platform hooks. The file also installs `x86_platform.is_untracked_pat_range` for ISA and GRU PAT exclusions, `x86_platform.nmi_init`, and optional PCI VGA state handling. UVsystab-derived tables and hub structures remain live because UV address translation helpers use them after boot.

## Dependencies and Integration Points
The code depends on ACPI, EFI, APIC/x2APIC, NUMA, memblock/memory hotplug block sizing, PCI, UV BIOS calls, UV MMR definitions, and x86 platform hooks. It integrates with TSC stability marking, PAT range policy, NMI setup, procfs, PCI VGA routing, reboot selection, and per-CPU topology data. It assumes UV firmware tables and MMR layouts match the detected hub generation.

## Risks and Test Signals
Primary risks are firmware table mismatches, incorrect pnode/socket/node translations, bad MMR base/shift values, and edge cases around deconfigured sockets. Incorrect APIC routing or memory mappings can break CPU bring-up, IPIs, MMIO access, or early boot. Test signals include boot logs for UV OEM IDs, hub type, TSC sync state, GAM table output, min/max pnodes, MMR/GRU/MMIOH mappings, `/proc/sgi_uv/*` values, successful secondary CPU startup, NMI delivery, VGA legacy routing, and absence of UVsystab mismatch warnings.
