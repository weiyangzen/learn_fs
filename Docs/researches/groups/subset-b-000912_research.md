# Research: subset-b-000912

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/fixup.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/fixup.c

## Purpose
`fixup.c` is the x86 PCI quirk table for hardware and firmware defects that must be corrected during PCI enumeration, enable, suspend, resume, or final setup. It does not provide a single driver; it registers many `DECLARE_PCI_FIXUP_*` callbacks that alter device resources, config registers, power-management capabilities, bus operations, host-bridge windows, and platform-specific reserved regions.

## Important APIs, types, and functions
Important callbacks include `pci_fixup_i450nx()`, `pci_fixup_i450gx()`, `pci_fixup_umc_ide()`, `pci_fixup_via_northbridge_bug()`, `pcie_rootport_aspm_quirk()`, `pci_xeon_x2_bifurc_quirk()`, `pci_fixup_video()`, Toshiba OHCI1394 pre/post fixups, `sb600_disable_hpet_bar()`, `pci_amd_enable_64bit_bar()`, `rs690_fix_64bit_dma()`, ChromeOS L1SS save/restore helpers, `asus_disable_nvme_d3cold()`, and AMD root-port PME suspend/resume quirks. The file uses PCI core fixup registration macros, DMI matching tables, resource APIs, raw I/O ports, HPET state, VGA arbitration, AMD SMN access, and suspend helpers.

## Control flow
The PCI core invokes callbacks at declared phases. Early/header fixups correct discovery inputs such as bogus BARs, secondary buses, ROM shadows, HPET BARs, transparent bridges, or non-compliant BAR sizing. Final fixups mutate post-enumeration policy such as PME support, D3cold permissions, root-window resources, MRRS limits, and bus operation wrappers. Suspend/resume fixups restore firmware-clobbered registers or temporarily mask broken PME states before system sleep.

## State and persistence behavior
Most changes persist in `struct pci_dev` fields or device config space. File-local state includes ASPM offsets per root port, saved Toshiba cache-line size, AMD 64-bit root-window `struct resource`, saved ChromeOS L1SS capability headers, and cached PME support restored from config space. Some changes reserve global address ranges through `request_mem_region()` or add resources to root buses. Quirks are deliberately idempotent where they run at resume.

## Dependencies and integration points
This file sits between PCI core enumeration, architecture PCI helpers, DMI, VGA arbitration, HPET, suspend, AMD node/SMN support, resource management, and platform firmware behavior. It affects downstream drivers by changing BAR ownership, link power management, PME capabilities, IRQ-visible resources, and hotplug child-bus config writes.

## Risks and edge cases
Quirk match scope is the main risk: a too-broad vendor/device match can damage unrelated hardware, while too-narrow DMI matching leaves machines broken. Config-space writes can race with firmware expectations across suspend/resume. The ASPM bus-op replacement assumes bounded root-port/device indexing. The AMD root-window workaround taints the kernel and must avoid multisocket systems. PME masking changes wake behavior and must distinguish runtime suspend from system suspend.

## Test signals
Useful signals are PCI enumeration logs, resource tree diffs, suspend/resume on affected DMI systems, ASPM write filtering tests, BAR sizing on listed Intel/AMD chipsets, USB wake validation on AMD SoCs, MacBook/Twinhead reserved-region checks, and no regressions in generic PCI resource assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/fixup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/i386.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/i386.c

## Purpose
`i386.c` implements 32-bit x86 PCI resource survey and assignment policy. It preserves usable firmware BAR assignments when possible, releases or invalidates bad assignments, aligns ISA-sensitive I/O windows, disables enabled ROM decoders during claiming, and records original firmware addresses for later retrieval by the PCI core.

## Important APIs, types, and functions
`struct pcibios_fwaddrmap` stores per-device firmware BAR starts. `pcibios_save_fw_addr()`, `pcibios_retrieve_fw_addr()`, and `pcibios_fw_addr_list_del()` manage that temporary map. `pcibios_align_resource()` is exported as the architecture resource alignment hook. Resource walking is split across `pcibios_allocate_bridge_resources()`, `pcibios_allocate_bus_resources()`, `pcibios_allocate_dev_resources()`, `pcibios_allocate_resources()`, ROM helpers, `pcibios_resource_survey_bus()`, `pcibios_resource_survey()`, and the `fs_initcall` `pcibios_assign_resources()`.

## Control flow
During survey, bridge windows are claimed first in depth-first order, then enabled device BARs are claimed, then disabled device BARs are attempted. Failed non-fixed claims are converted to unassigned size-only resources after saving firmware start addresses. ROM resources are disabled unless the user requested assignment, then later claimed or assigned. Late survey reserves E820 and IO-APIC resources before unassigned PCI resources are allocated.

## State and persistence behavior
The temporary firmware-address list holds device references until `pcibios_assign_resources()` runs. `pcibios_fw_addr_done` prevents late access after cleanup. Resource state persists in `struct resource` parents, starts, ends, flags, and ROM enable bits. The code may mutate device config space to disable ROM decoding.

## Dependencies and integration points
It integrates with PCI core resource claiming/assignment, memblock/E820 reservation, PAT/memtype logic through included architecture headers, IO-APIC resource insertion, and `pci_probe` boot flags such as `PCI_ASSIGN_ROMS` and `PCI_CAN_SKIP_ISA_ALIGN`. `pcibios_align_resource()` is called by generic PCI allocation.

## Risks and edge cases
The firmware-address list is protected by a spinlock, but the allocation path briefly drops the lock and can race to add duplicate maps in unusual concurrent probe paths. ISA I/O alignment is conservative unless a bridge is known not to forward ISA cycles. Incorrectly preserving an overlapping firmware BAR can block valid allocation; incorrectly clearing a fixed BAR would break immovable platform resources.

## Test signals
Boot logs with `pci=assign-busses`, ROM assignment modes, 32-bit systems with ISA bridges, overlapping firmware BARs, IO-APIC-in-PCI-space systems, and PCI hotplug resource-survey calls are useful. Inspect `/proc/iomem`, `/proc/ioports`, and PCI BAR assignments before and after `pci_assign_unassigned_resources()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/i386.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/init.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/init.c

## Purpose
`init.c` is the ordered x86 PCI architecture initialization entry point. It sequences direct config-space probing, early ECAM discovery, platform-specific PCI initialization, MSI-domain creation, PCI BIOS fallback, direct-access installation, and DMI PCI-probe quirks.

## Important APIs, types, and functions
The central function is `pci_arch_init()`, registered with `arch_initcall()`. It calls `pci_direct_probe()`, `pci_mmcfg_early_init()`, optional `x86_init.pci.arch_init()`, `x86_create_pci_msi_domain()`, `pci_pcbios_init()`, `pci_direct_init()`, `dmi_check_pciprobe()`, and `dmi_check_skip_isa_align()`. It uses `pci_probe`, `raw_pci_ops`, and `raw_pci_ext_ops`.

## Control flow
Initialization first discovers the direct mechanism type. Unless `PCI_PROBE_NOEARLY` is set, early MCFG/ECAM setup runs before platform overrides. Xen or other platform hooks can then override PCI or MSI behavior through `x86_init.pci.arch_init()`. MSI domains are created after that hook so Xen can replace the creation callback. If platform init allows PCI BIOS probing, BIOS32 probing runs before direct init so legacy probing can still obtain `pcibios_last_bus`.

## State and persistence behavior
The file itself stores no long-lived state, but it establishes global config-access pointers and boot-probe flags. Its ordering determines whether raw config operations, extended config operations, and MSI domains are available to all later PCI scans.

## Dependencies and integration points
It is tightly coupled to `pci/direct.c`, `mmconfig-shared.c`, `pcbios.c`, `x86_init`, IRQ-domain setup, and DMI quirk code. Hypervisors and platform code rely on the `x86_init.pci.arch_init()` insertion point.

## Risks and edge cases
Ordering regressions are high impact: MSI domain creation before Xen setup would allocate the wrong domain, and direct probing before PCI BIOS could lose legacy last-bus information. If no raw or extended config access path is installed, the system logs a fatal PCI access error but boot may continue with no PCI.

## Test signals
Boot with native PCI, Xen PV/HVM, `pci=nobios`, `pci=nommconf`, `pci=noearly`, and old BIOS-only machines. Confirm logs show the intended config-space mechanism and that MSI domains and DMI quirks are initialized in the expected order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/intel_mid.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/intel_mid.c

## Purpose
`intel_mid.c` supplies PCI access, IRQ, power, and fixed-BAR behavior for Intel MID/Moorestown-style SoCs where many devices use MMCONFIG, selected Lincroft devices also require type-1 writes, and some non-existent type-1 config accesses can hang hardware.

## Important APIs, types, and functions
Core helpers include `fixed_bar_cap()`, `pci_device_update_fixed()`, `type1_access_ok()`, custom `pci_read()`/`pci_write()`, `intel_mid_pci_irq_enable()`, `intel_mid_pci_irq_disable()`, `intel_mid_pci_init()`, `pci_d3delay_fixup()`, `mid_power_off_devices()`, and `pci_fixed_bar_fixup()`. The file defines MID PCI ops and CPU/device IDs for Silvermont MID plus Merrifield MMC/HSU quirks.

## Control flow
`intel_mid_pci_init()` installs custom root PCI ops, initializes late ECAM, replaces IRQ enable/disable hooks, marks SoC mode, and disables ACPI IRQ routing. Reads use type-1 only for known safe bus-0 devices/registers; other accesses go through `raw_pci_ext_ops`. Writes ignore ROM BARs, synthesize fixed-BAR sizing writes when a vendor extended capability advertises fixed sizes, and otherwise choose safe type-1 or MMCONFIG. IRQ enable maps PCI interrupt-line GSIs directly to IO-APIC IRQs with model-specific polarity and IRQ0 exceptions.

## State and persistence behavior
`pci_soc_mode` gates final/header fixups in kernels that also run on non-SoC systems. Fixed-BAR fixups rewrite resource ends and mark BARs `IORESOURCE_PCI_FIXED`. MID power-off fixups push known LSS devices into D3hot by updating PMCSR; actual power removal happens elsewhere.

## Dependencies and integration points
It depends on ECAM setup, direct config ops, IO-APIC GSI mapping, ACPI no-IRQ mode, Intel MID power island IDs, IOSF-era device topology, PCI extended capabilities, and generic PCI fixup stages.

## Risks and edge cases
Access filtering must never type-1 probe absent Lincroft devices. Fixed-BAR size synthesis assumes power-of-two size descriptors and a read immediately after a `~0` sizing write. IRQ0 handling is device-specific and can silently leave bogus devices without an interrupt. `pci_soc_mode` must be correct before fixups run.

## Test signals
Boot on Moorestown/Merrifield/Tangier hardware, BAR sizing on fixed-BAR devices, IRQ allocation for MMC and HSU devices, suspend/power-island behavior, and absence of hangs when scanning non-existent functions are primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/intel_mid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/irq.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/irq.c

## Purpose
`irq.c` implements legacy x86 PCI INTx routing using BIOS `$PIR` tables, AMI `$IRT` conversion, PCI BIOS fallback, chipset-specific PIRQ routers, ELCR programming, DMI workarounds, and IO-APIC fallback for devices not handled by ACPI/MSI.

## Important APIs, types, and functions
Key data structures are `struct irq_router`, `struct irq_router_handler`, global `pirq_table`, `pirq_router`, `pirq_router_dev`, `pcibios_irq_mask`, and `pirq_penalty[16]`. Public hooks are `pcibios_enable_irq`, `pcibios_disable_irq`, `pcibios_irq_init()`, `pcibios_fixup_irqs()`, `pcibios_penalize_isa_irq()`, `elcr_set_level_irq()`, and `mp_should_keep_irq()`. Router handlers cover Intel PIIX/ICH/PCEB/IB, VIA, ALI/FinALi, SiS, VLSI, ServerWorks, AMD756, OPTi, ITE, Cyrix, PicoPower, and optional PCI BIOS routing.

## Control flow
Boot scans BIOS memory for `$PIR`, then byte scans for `$IRT` and converts it if needed. If a table exists, peer buses are scanned, a router device is found by table vendor/device or fallback device matching, and exclusive IRQs penalize unavailable lines. IRQ lookup resolves a device pin, swizzles through bridges if needed, applies DMI quirks, chooses an existing or lowest-penalty IRQ, programs router links and ELCR level mode, then propagates the chosen IRQ to devices sharing the same PIRQ link. IO-APIC mode bypasses the PIRQ table and maps bus/slot/pin vectors instead.

## State and persistence behavior
State persists in global routing-table pointers, router function tables, DMI flags for broken HP/Acer systems, ELCR programmed mask, IRQ penalties, `dev->irq`, and `dev->irq_managed`. BIOS-converted routing tables are allocated dynamically and freed when IO-APIC routing makes them unnecessary.

## Dependencies and integration points
The file integrates with raw PCI config access, PCI BIOS services, DMI, ACPI IRQ penalty routing, IO-APIC MP-table vector lookup, ISA ELCR ports, chipset config-space or port-I/O registers, `x86_init.pci.fixup_irqs()`, and the PCI core enable/disable IRQ hooks.

## Risks and edge cases
Legacy routing relies on firmware tables that may contain wrong links, masks, router IDs, or bus numbers. Router register programming is chipset-specific and often undocumented. Penalty choices affect shared ISA/PCI IRQ stability. Bridge swizzling and shared-PIRQ propagation can misroute multifunction or bridge-hidden devices. Disable must preserve IRQs during system suspend and runtime suspend preparation.

## Test signals
Use old BIOS-only systems, `pci=biosirq`, `pci=routeirq`, `pci=usepirqmask`, IO-APIC disabled/enabled boots, DMI-quirked laptops, and drivers using legacy INTx. Logs showing PIRQ table discovery, router selection, ELCR changes, and INTx-to-IRQ mappings are key evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/legacy.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/legacy.c

## Purpose
`legacy.c` handles traditional PCI bus probing for x86 systems that do not use ACPI root scanning or another platform-specific method. It scans bus 0, discovers peer root buses from `pcibios_last_bus`, initializes IRQ routing, and calls the generic pcibios init path.

## Important APIs, types, and functions
`pci_legacy_init()` probes primary PCI hardware. `pcibios_scan_specific_bus()` tests a bus for any valid vendor ID and scans it as a root bus. `pcibios_fixup_peer_bridges()` iterates up to `pcibios_last_bus`. `pci_subsys_init()` is the `subsys_initcall()` that invokes `x86_init.pci.init()`, legacy fallback, peer scanning, `x86_init.pci.init_irq()`, and `pcibios_init()`.

## Control flow
At subsystem init, platform PCI init is tried first. A nonzero return requests legacy probing. Legacy probing scans root bus 0 using `pcibios_scan_root()`. If BIOS last-bus data indicates possible peer bridges, each bus is probed by reading vendor ID at device/function strides; Jailhouse paravirtual systems scan every function instead of every slot. IRQ initialization and final PCI BIOS setup run after bus discovery.

## State and persistence behavior
The file holds no private persistent state. It consumes `pcibios_last_bus` and mutates global PCI bus lists through root-bus scans. `raw_pci_ops` availability gates whether any probing can happen.

## Dependencies and integration points
It integrates with `x86_init.pci`, Jailhouse paravirtual detection, raw PCI config access, `pcibios_scan_root()`, IRQ initialization, and generic PCI subsystem startup.

## Risks and edge cases
Peer-bus discovery is heuristic and depends on reliable `pcibios_last_bus`. Reading config space on absent devices must be safe for the installed access mechanism. Jailhouse changes scan stride because virtual PCI topologies may expose functions in ways normal slot-based scanning would miss.

## Test signals
Validate with legacy BIOS systems, Jailhouse guests, systems with peer host bridges, and no-PCI systems. Logs should show primary probing, discovered peer buses, or a clear "does not support PCI" message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig-shared.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig-shared.c

## Purpose
`mmconfig-shared.c` is the common x86 ECAM/MMCONFIG discovery, validation, resource, and hotplug-management layer. It builds the global list of PCI ECAM regions from known hostbridge probes, ACPI MCFG, and hotplug `_CBA` inputs, validates reservation ownership, and invokes architecture-specific map/unmap backends.

## Important APIs, types, and functions
Primary APIs are `pci_mmconfig_add()`, `pci_mmconfig_lookup()`, `pci_mmcfg_early_init()`, `pci_mmcfg_late_init()`, `pci_mmconfig_insert()`, and `pci_mmconfig_delete()`. Internal helpers allocate sorted `struct pci_mmcfg_region` entries, probe Intel E7520/945, AMD Fam10h, NVIDIA MCP55, parse ACPI MCFG, validate E820/ACPI/EFI reservations, reject broken ECAM regions, insert resources at late init, and optionally provide an APEI address filter.

## Control flow
Early init runs if `PCI_PROBE_MMCONF` is enabled. It prefers known hostbridge probes, otherwise parses ACPI MCFG, rejects unreserved/broken regions, sets `pcibios_last_bus` if needed, and calls `pci_mmcfg_arch_init()`. Late init retries ACPI parsing after more infrastructure is available when early config access did not fully select ECAM. `late_initcall()` inserts ECAM resources into `iomem_resource`. Hostbridge hotplug calls `pci_mmconfig_insert()` to validate, map, insert, and publish new regions under lock; deletion removes them with RCU synchronization.

## State and persistence behavior
Global state includes `pci_mmcfg_list`, `pci_mmcfg_lock`, `pci_mmcfg_running_state`, `pci_mmcfg_arch_init_failed`, and `known_bridge`. Region entries persist resource names, physical ranges, segment/bus ranges, and architecture-private mappings. Lookup uses RCU-compatible list traversal.

## Dependencies and integration points
It depends on ACPI table/resource parsing, EFI memory descriptors, E820 reservation checks, raw PCI config access for hostbridge probes, resource insertion, APEI filtering, and arch-specific files `mmconfig_32.c`/`mmconfig_64.c`/platform overrides.

## Risks and edge cases
Firmware MCFG ranges are often malformed, overlapping, too large, above 4GB on old systems, or not reserved in ACPI resources. Early validation cannot use the ACPI interpreter, so it relies on DMI age and E820 only for older systems. Hotplug insertion must avoid duplicates, invalid bus ranges, conflicting resources, failed mappings, and concurrent readers.

## Test signals
Boot with `pci=nommconf`, ACPI MCFG-only systems, known Intel/AMD/NVIDIA hostbridges, EFI MMIO-backed ECAM, hot-added host bridges, APEI error injection, and resource conflict scenarios. Logs should show ECAM ranges, reservation source, size reductions, and map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig-shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_32.c

## Purpose
`mmconfig_32.c` implements the 32-bit x86 ECAM config-space accessor. Because 32-bit kernels cannot cheaply keep all ECAM space permanently mapped, it maps one device's 4KB extended config page at a fixed virtual address on demand.

## Important APIs, types, and functions
The file defines `pci_mmcfg_read()`, `pci_mmcfg_write()`, `pci_exp_set_dev_base()`, `get_base_addr()`, `pci_mmcfg` raw-ops table, `pci_mmcfg_arch_init()`, `pci_mmcfg_arch_free()`, `pci_mmcfg_arch_map()`, and `pci_mmcfg_arch_unmap()`. State is `mmcfg_last_accessed_device` and `mmcfg_last_accessed_cpu`.

## Control flow
Each read/write validates bus, devfn, and register bounds, looks up the region under RCU, locks `pci_config_lock`, maps the target device page into `FIX_PCIE_MCFG` if the cached device/cpu differs, performs byte/word/dword MMIO access, then unlocks and drops RCU. Architecture init installs `raw_pci_ext_ops = &pci_mmcfg`.

## State and persistence behavior
The fixmap mapping is cached per last device and CPU to avoid repeated `set_fixmap_nocache()` calls. Unmap invalidates that cache when a region is deleted. No per-region virtual mapping is stored on 32-bit.

## Dependencies and integration points
It depends on `pci_mmcfg_list` lookup from the shared file, fixmap slot `FIX_PCIE_MCFG`, `pci_config_lock`, RCU, and generic raw PCI extended ops. It coexists with type-1 access for conventional config space.

## Risks and edge cases
All accesses serialize on `pci_config_lock`, and the cached fixmap is CPU-sensitive. Invalid region lookup returns `-EINVAL` and all-ones reads. The physical base is stored as `u32`, so 32-bit ECAM above 4GB is intentionally unsupported by earlier validation.

## Test signals
32-bit boots with ECAM-enabled hardware, extended PCI capability reads, concurrent config access stress, ECAM hot-delete invalidation, and `pci=nommconf` fallback checks are appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_64.c

## Purpose
`mmconfig_64.c` implements the x86_64 ECAM accessor. Unlike 32-bit, it maps each ECAM window persistently and allows lockless MMIO config-space access protected by RCU lookup and shared-region lifetime rules.

## Important APIs, types, and functions
Important functions are `pci_dev_base()`, `pci_mmcfg_read()`, `pci_mmcfg_write()`, `mcfg_ioremap()`, `pci_mmcfg_arch_map()`, `pci_mmcfg_arch_unmap()`, `pci_mmcfg_arch_init()`, and `pci_mmcfg_arch_free()`. The exported raw ops table is `pci_mmcfg`.

## Control flow
Architecture init maps every region in `pci_mmcfg_list`; any mapping failure frees all previously mapped regions and reports failure. Reads/writes validate bounds, find a mapped base with RCU, compute `virt + bus offset + devfn offset + reg`, and perform byte/word/dword MMIO access. Hotplug insert/delete uses the same map/unmap helpers.

## State and persistence behavior
Each `struct pci_mmcfg_region` stores `virt`, a virtual base biased so bus offsets can be applied uniformly. Unmap calls `iounmap()` on the real mapped start and clears `virt`. Raw extended ops persist globally after successful arch init.

## Dependencies and integration points
It depends on the shared ECAM region list, `ioremap()`, RCU, x86 MMIO config accessors, and generic PCI raw extended config operations. Hotplug region insertion from ACPI root handling also uses these map routines.

## Risks and edge cases
Persistent mappings consume virtual address space proportional to bus coverage. RCU readers require deletion to synchronize before freeing. Incorrect bus-range biasing would produce wrong config addresses. Reads from absent mappings return all ones and `-EINVAL`, matching PCI config failure semantics.

## Test signals
Validate extended capability access on multiple segments, ECAM windows starting at nonzero bus numbers, hotplug insertion/deletion, mapping failure paths, and concurrent config-space readers during hostbridge removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/numachip.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/numachip.c

## Purpose
`numachip.c` provides Numascale NumaConnect-specific PCI config accessors derived from x86_64 ECAM, with an extra guard that prevents AMD Northbridges from decoding bus-0 accesses to non-existent devices in remote I/O configurations.

## Important APIs, types, and functions
The central functions are `pci_mmcfg_read_numachip()`, `pci_mmcfg_write_numachip()`, `pci_dev_base()`, and `pci_numachip_init()`. The raw ops table `pci_mmcfg_numachip` is installed for both normal and extended config access. File-local `limit` records the highest bus-0 devfn allowed.

## Control flow
Initialization reads AMD Northbridge register `0x60` at bus 0 device 0x18 function 0. Bits 6:4 describe fabric size; the resulting number of northbridges determines the first disallowed devfn. Reads and writes reject bus 0 accesses at or beyond `limit`, returning all ones for reads and dropping writes, otherwise using normal ECAM lookup and MMIO access.

## State and persistence behavior
`limit` is read-mostly and persists after init. Global `raw_pci_ops` and `raw_pci_ext_ops` are replaced with Numachip ops. Per-region mapping state remains owned by the shared MMCONFIG layer.

## Dependencies and integration points
It depends on preexisting ECAM region mappings, raw config read during init, AMD northbridge layout, and Numachip platform detection code that calls `pci_numachip_init()`.

## Risks and edge cases
If fabric-size decoding is wrong, valid devices can disappear or unsafe accesses can still reach absent northbridges. The special guard only applies to bus 0; other buses use ordinary ECAM behavior. Initialization must run after raw PCI reads are possible.

## Test signals
Boot on Numascale hardware, scan bus 0 around the northbridge limit, verify no machine checks or remote decode issues, and confirm normal ECAM access continues for valid devices and nonzero buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/numachip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/olpc.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/olpc.c

## Purpose
`olpc.c` implements PCI config-space simulation for OLPC XO-1 systems using AMD Geode GX/LX plus CS5536 devices when VSA firmware emulation is not used. It replaces SMM-based PCI virtualization with kernel-side table-backed config headers for integrated devices.

## Important APIs, types, and functions
Static header tables describe simulated northbridge, framebuffer, AES, ISA, AC97, OHCI, and EHCI config spaces for GX/LX variants. `is_simulated()` selects bus-0 Geode slots, `hdr_addr()` handles normal reads versus BAR-size probing, `pci_olpc_read()` and `pci_olpc_write()` implement raw config ops, and `pci_olpc_init()` installs `raw_pci_ops`.

## Control flow
Non-simulated devices fall back to `pci_direct_conf1`. Simulated reads choose a table by devfn, return zero beyond stored config range, or all ones for absent devices. BAR writes of `~0` set `bar_probing`, causing the next read to return the corresponding size mask instead of normal header data. Other writes are ignored except for warnings on unexpected registers.

## State and persistence behavior
File-local state includes `ff_loc`, `zero_loc`, `bar_probing`, and `is_lx`. The simulation is mostly read-only; it does not persist writes into the tables. `bar_probing` is a single global one-shot flag and assumes PCI core sizing reads immediately follow writes.

## Dependencies and integration points
It depends on Geode/OLPC platform detection, type-1 direct PCI access for external devices, and the PCI core's standard BAR sizing sequence. It avoids the external VSA SMM path for suspend/resume speed and maintainability.

## Risks and edge cases
The global BAR-probing flag is not device-specific, so unexpected concurrent config accesses could read a size mask for the wrong simulated device. Ignoring config writes is acceptable only because these integrated devices expose mostly fixed resources. Header tables must accurately match LX versus GX hardware.

## Test signals
Boot XO-1 with VSA disabled, enumerate simulated Geode devices, verify BAR sizes/resources, USB/audio/framebuffer availability, suspend/resume speed, and absence of unexpected config-write warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/olpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/pcbios.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/pcbios.c

## Purpose
`pcbios.c` implements BIOS32 and PCI BIOS support for legacy x86 PCI config access and IRQ routing. It scans low BIOS memory for the BIOS32 service directory, invokes real firmware entry points through far calls, optionally installs PCI BIOS raw config ops, and exposes BIOS IRQ routing APIs.

## Important APIs, types, and functions
Important functions include `set_bios_x()`, `bios32_service()`, `check_pcibios()`, `pci_bios_read()`, `pci_bios_write()`, `pci_find_bios()`, `pcibios_get_irq_routing_table()`, `pcibios_set_irq_routing()`, and `pci_pcbios_init()`. Data includes `bios32_indirect`, `pci_indirect`, `pcibios_enabled`, `pci_bios_present`, and the BIOS raw ops table.

## Control flow
`pci_pcbios_init()` runs when `PCI_PROBE_BIOS` is enabled. It scans `0xe0000-0xfffff` for a valid `_32_` structure, marks BIOS memory executable, locates the `$PCI` service, calls the BIOS present function, validates the PCI signature and version, updates direct-probe masks for supported hardware mechanisms, and installs BIOS config access. IRQ helpers later call BIOS functions to fetch routing options or set a hardware interrupt line.

## State and persistence behavior
BIOS entry pointers are stored in kernel virtual form with kernel code/data segments. Enabling PCI BIOS marks the low BIOS area RWX and sets `pcibios_enabled`. `pci_bios_present` gates routing calls. `pcibios_last_bus` may be populated from BIOS present output.

## Dependencies and integration points
It integrates with low-memory mappings, x86 segment descriptors, `pci_config_lock`, PCI BIOS function numbers, PCI IRQ routing in `irq.c`, direct-probe fallback selection, and boot option `pci=nobios`.

## Risks and edge cases
Running BIOS code after kernel boot is inherently risky and leaves a RWX BIOS hole unless disabled. Firmware may return bogus signatures, nonzero carry status, unmasked read data, high-memory BIOS32 entries, or routing tables larger than a page. The implementation warns that modern systems should prefer MMCONFIG/direct access.

## Test signals
Legacy BIOS machines, `pci=biosirq`, `pci=nobios`, systems lacking direct mechanism support, IRQ routing table fetches, and NX/RWX log messages are relevant. Confirm config reads/writes serialize under `pci_config_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/pcbios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/xen.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/xen.c

## Purpose
`xen.c` replaces native x86 PCI INTx, ACPI GSI, and MSI/MSI-X setup with Xen PIRQ/event-channel based handling for PV guests, HVM guests needing PIRQs, and Xen initial domains. It bridges PCI core IRQ allocation to Xen hypercalls and frontend/backend operations.

## Important APIs, types, and functions
Key paths are `xen_pcifront_enable_irq()`, `xen_register_pirq()`, `acpi_register_gsi_xen_hvm()`, PV Dom0 `xen_register_gsi()`, MSI setup variants `xen_setup_msi_irqs()`, `xen_hvm_setup_msi_irqs()`, `xen_initdom_setup_msi_irqs()`, `xen_initdom_restore_msi()`, teardown helpers, the synthetic MSI irq-domain callbacks, `pci_xen_init()`, `pci_xen_hvm_init()`, and `pci_xen_initial_domain()`.

## Control flow
PV DomU installs pcifront INTx hooks and keeps ACPI out of IRQ routing. HVM installs ACPI GSI registration and defers MSI-domain replacement until APIC mode is known; if APIC virtualization is available, native MSI is retained. Initial domain installs MSI hypercall setup, ACPI GSI registration, and preallocates legacy IRQ overrides. MSI setup maps PCI devices or MSI-X table entries to Xen PIRQs, binds them to Linux IRQs, and populates MSI sysfs.

## State and persistence behavior
Global state includes exported `xen_pci_frontend`, `xen_msi_ops`, and `pci_seg_supported`. PCI device state is updated through `dev->irq`, MSI descriptors, and Xen IRQ bindings. Initial domain restore may switch permanently from segment-aware hypercalls to legacy calls if unsupported.

## Dependencies and integration points
It depends on Xen hypervisor feature flags, physdev operations, event-channel binding, pcifront MSI helpers, ACPI registration hooks, x86 APIC state, the MSI irq-domain framework, and generic PCI enable/disable flows.

## Risks and edge cases
Domain type determines which hooks are legal; using PV frontend ops in Dom0 or HVM paths would misroute interrupts. Multi-MSI support may return positive retry signals. MSI-X setup depends on a valid table BAR. Segment-aware hypercalls are probed and may degrade to legacy domain-0-only bus encoding. The synthetic irq domain is intentionally a compatibility wrapper.

## Test signals
Test PV DomU passthrough, HVM with and without APIC virtualization, PV Dom0, MSI and MSI-X devices, multi-MSI fallback, ACPI GSI overrides, suspend/resume MSI restore, and pcifront backend absence/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/xen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/Makefile

## Purpose
This Makefile aggregates x86 platform-specific subdirectories into the architecture build. It is the top-level build hook for platform families such as Atom, CE4100, EFI, Geode, Intel MID/Quark, OLPC, UV, and other legacy x86 platforms.

## Important APIs, types, and functions
The file is declarative Kbuild content. It uses unconditional `obj-y +=` entries for platform subdirectories: `atom/`, `ce4100/`, `efi/`, `geode/`, `iris/`, `intel/`, `intel-mid/`, `intel-quark/`, `olpc/`, `scx200/`, `ts5500/`, and `uv/`.

## Control flow
There is no runtime control flow. During kernel build, Kbuild descends into each listed directory; per-directory Makefiles then decide which objects are selected by configuration symbols.

## State and persistence behavior
No runtime state. Build-time state is the set of platform directories included in `arch/x86/platform`.

## Dependencies and integration points
This file integrates the architecture Makefile with platform-specific Kbuild fragments. It intentionally leaves feature gating to child Makefiles so common platform directories can exist across configurations.

## Risks and edge cases
Removing a directory here silently omits all objects beneath it even if their config symbols are enabled. Adding directories unconditionally is fine only if the child Makefile is safe for all configs.

## Test signals
Build matrix coverage across x86 platform configs, especially EFI, Intel MID, OLPC, UV, and CE4100, verifies this aggregation remains correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/atom/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/atom/Makefile

## Purpose
This Makefile selects the Intel Atom Punit debug driver when configured.

## Important APIs, types, and functions
It contains a single Kbuild rule: `obj-$(CONFIG_PUNIT_ATOM_DEBUG) += punit_atom_debug.o`.

## Control flow
There is no runtime control flow. At build time, the object is compiled into the kernel or module set only when `CONFIG_PUNIT_ATOM_DEBUG` is enabled.

## State and persistence behavior
No runtime state. The only persistent effect is build inclusion of `punit_atom_debug.c`.

## Dependencies and integration points
It is reached from `arch/x86/platform/Makefile` and depends on Kconfig selecting `CONFIG_PUNIT_ATOM_DEBUG`.

## Risks and edge cases
If the config symbol is renamed or the object name changes, the debugfs/s2idle Atom diagnostics disappear from builds.

## Test signals
Enable and disable `CONFIG_PUNIT_ATOM_DEBUG` and confirm `punit_atom_debug.o` appears only in the enabled build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/atom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/atom/punit_atom_debug.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/atom/punit_atom_debug.c

## Purpose
`punit_atom_debug.c` is a debug driver for Intel Atom SoC Punit power-state visibility. It exposes North Complex device D-state information through debugfs and, when ACPI suspend support is present, checks selected devices before s2idle.

## Important APIs, types, and functions
`struct punit_device` maps device names to IOSF PMC register/bit positions. Tables cover Bay Trail, Tangier/Merrifield, and Cherry Trail. `punit_dev_state_show()` reads IOSF MBI registers and prints D0/D0i1/D0i2/D0i3. `punit_dbgfs_register()` creates `debugfs/punit_atom/dev_power_state`. `punit_s2idle_check()` reports devices still in D0 before low-power idle. `punit_atom_debug_init()` matches CPUs with `x86_match_cpu()`.

## Control flow
Module init matches an Atom CPU with MWAIT support, selects the right Punit table, registers debugfs, and registers ACPI LPS0 check ops if enabled. Debugfs reads iterate the table and issue `iosf_mbi_read()` calls. Exit unregisters LPS0 ops and removes debugfs recursively.

## State and persistence behavior
Persistent state is minimal: `punit_dbg_file` for debugfs removal and `punit_dev` for s2idle checks. Hardware state is read-only; the driver does not alter Punit registers.

## Dependencies and integration points
It depends on CPU model matching, IOSF MBI PMC access, debugfs, seq_file, ACPI LPS0 hooks, suspend support, and Intel family IDs.

## Risks and edge cases
IOSF reads can fail and are reported per device. The s2idle check skips MIO because it remains on until late suspend. CPU matching must select correct register layouts or D-state names will be misleading.

## Test signals
On supported Atom platforms, read `debugfs/punit_atom/dev_power_state`, trigger s2idle and inspect pre-suspend logs, verify unsupported CPUs return `-ENODEV`, and confirm module removal cleans debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/atom/punit_atom_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ce4100/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/ce4100/Makefile

## Purpose
This Makefile includes CE4100 platform setup code when the Intel CE platform is configured.

## Important APIs, types, and functions
It contains `obj-$(CONFIG_X86_INTEL_CE) += ce4100.o`.

## Control flow
No runtime control flow. Kbuild includes `ce4100.o` only for `CONFIG_X86_INTEL_CE`.

## State and persistence behavior
No runtime state. The build output determines whether CE4100 early setup hooks are available.

## Dependencies and integration points
It is included by the parent x86 platform Makefile and depends on the x86 Intel CE Kconfig symbol.

## Risks and edge cases
Wrong gating would either omit CE4100 platform boot support or compile CE4100-only hooks into unrelated builds.

## Test signals
Build with `CONFIG_X86_INTEL_CE=y` and confirm `ce4100.o` is linked; build without it and confirm omission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ce4100/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ce4100/ce4100.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/ce4100/ce4100.c

## Purpose
`ce4100.c` installs early x86 platform overrides for Intel CE4100 systems. It disables PC-style firmware discovery that CE4100 does not use, routes PCI/IRQ setup through CE4100/Open Firmware paths, fixes serial setup, and supplies correct reboot/poweroff behavior.

## Important APIs, types, and functions
`ce4100_power_off()` writes command `0x4` to I/O port `0xcf9` for the platform 8051/PMU path. `sdv_arch_setup()` calls `sdv_serial_fixup()`. `sdv_pci_init()` calls `x86_of_pci_init()`. `x86_ce4100_early_setup()` rewires `x86_init` hooks, sets `reboot_type = BOOT_KBD`, and assigns `pm_power_off`.

## Control flow
Early platform detection calls `x86_ce4100_early_setup()` before generic x86 initialization consumes `x86_init`. Later architecture setup uses the substituted hooks: no ROM probing, no MP table parsing, CE4100 PCI config init, and OF PCI IRQ initialization.

## State and persistence behavior
Persistent global mutations are `x86_init` function pointer overrides, `reboot_type`, and `pm_power_off`. No file-local state is retained.

## Dependencies and integration points
It depends on CE4100 PCI support, Open Firmware PCI init, serial fixup, x86 setup/reboot infrastructure, and platform power-management wiring through I/O port `0xcf9`.

## Risks and edge cases
These overrides must run only on CE4100. Applying them elsewhere would disable ROM/MP parsing and break PCI/IRQ discovery. The reboot workaround chooses keyboard-controller reset because the bootloader's ACPI reset path powers off instead of rebooting.

## Test signals
Boot CE4100 hardware or emulator, verify PCI devices and IRQs appear through OF paths, serial console works, reboot resets rather than powers off, and poweroff writes the expected PMU command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ce4100/ce4100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/Makefile

## Purpose
This Makefile selects x86 EFI support objects and disables sanitizing/profiling options that are unsafe or undesirable for early/runtime firmware call paths.

## Important APIs, types, and functions
It sets `KASAN_SANITIZE := n` and `GCOV_PROFILE := n`. `CONFIG_EFI` builds `memmap.o`, `quirks.o`, `efi.o`, architecture-width `efi_$(BITS).o`, and `efi_stub_$(BITS).o`. `CONFIG_EFI_MIXED` adds `efi_thunk_$(BITS).o`; `CONFIG_EFI_RUNTIME_MAP` adds `runtime-map.o`.

## Control flow
No runtime control flow. Kbuild compiles width-specific C and assembly support according to kernel bitness and EFI feature config.

## State and persistence behavior
No runtime state. Build output controls availability of EFI memory map handling, runtime services, mixed-mode thunks, and runtime map exposure.

## Dependencies and integration points
It integrates with x86 platform Kbuild, EFI Kconfig, bitness-specific object naming, KASAN, and GCOV. The sanitizer/profiling disables matter for firmware ABI stubs and early boot mappings.

## Risks and edge cases
Sanitizer instrumentation in EFI runtime call paths could break firmware ABI assumptions or early address-space transitions. Missing mixed-mode thunk objects would break 64-bit kernels booted via 32-bit EFI.

## Test signals
Build 32-bit EFI, 64-bit EFI, mixed-mode EFI, and EFI runtime-map configs. Confirm expected object files are linked and no KASAN/GCOV instrumentation is applied in this directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi.c

## Purpose
`efi.c` is the common x86 EFI bring-up and runtime virtual-mode coordinator. It imports firmware tables, initializes and sanitizes the EFI memory map, optionally folds EFI memory into E820, removes problematic MMIO reservations, maps runtime regions, calls `SetVirtualAddressMap()`, installs native or mixed runtime services, and exposes EFI table addresses through sysfs attributes.

## Important APIs, types, and functions
Key functions are `efi_memblock_x86_reserve_range()`, `efi_init()`, `efi_clean_memmap()`, `efi_remove_e820_mmio()`, `efi_print_memmap()`, `efi_systab_init()`, `efi_config_init()`, `efi_merge_regions()`, `efi_map_regions()`, `kexec_enter_virtual_mode()`, `__efi_enter_virtual_mode()`, `efi_enter_virtual_mode()`, `efi_is_table_address()`, `efi_attr_is_visible()`, and `__x86_efi_boot_mode()`. State includes `efi_systab_phys`, `efi_runtime`, `efi_nr_tables`, `efi_fw_vendor`, `efi_config_table`, and `efi_setup`.

## Control flow
Early memory reservation maps the bootloader-provided EFI memory map, optionally imports it into E820, reserves the map storage, and marks boot-services preservation. `efi_init()` maps and validates the system table, parses config tables, checks runtime support/disable options, sanitizes bad descriptors, removes large EFI MMIO ranges from E820, and marks runtime services available. `efi_enter_virtual_mode()` later either reuses kexec mappings or builds new EFI page tables, maps required regions, installs a late memory map, calls `efi_set_virtual_address_map()`, checks embedded firmware, unmaps boot services, installs runtime call handlers, updates permissions, and deletes the dummy variable used by quirks.

## State and persistence behavior
EFI table physical addresses are retained for sysfs and table-address checks. The EFI memory map transitions from early mapping to late mapping. Runtime service availability is represented by bits in `efi.flags`. New runtime memory maps contain only mapped descriptors with assigned virtual addresses.

## Dependencies and integration points
It depends on boot parameters, EFI generic table parsing, memblock, E820, early memremap, kexec setup_data, architecture-specific mapping functions in `efi_32.c`/`efi_64.c`, EFI quirks, BGRT/ESRT/TPM/RNG/MOK/CoCo tables, sysfs EFI attributes, and runtime service setup.

## Risks and edge cases
32-bit kernels cannot handle EFI tables or maps above 4GB. Invalid descriptor overflow must be removed before use. Firmware may require boot-services mappings even after ExitBootServices. Mixed-mode and kexec paths have different mapping constraints. Removing large EFI MMIO from E820 helps PCI hotplug but must preserve small non-window MMIO.

## Test signals
EFI boots across 32/64-bit, mixed mode, kexec, `add_efi_memmap`, `efi=noruntime`, `efi=debug`, soft-reserve memory, large MMIO host windows, and malformed memory maps. Validate runtime variables, sysfs table attributes, E820 output, and `SetVirtualAddressMap()` status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_32.c

## Purpose
`efi_32.c` provides 32-bit x86 EFI runtime mapping and calling support. It maps EFI runtime descriptors into the kernel's existing address space or cached I/O mappings, performs the physical-mode `SetVirtualAddressMap()` call through an assembly stub, and marks runtime code executable when NX is supported.

## Important APIs, types, and functions
Important functions are `efi_map_region()`, `efi_alloc_page_tables()`, `efi_sync_low_kernel_mappings()`, `efi_dump_pagetable()`, `efi_setup_page_tables()`, `efi_map_region_fixed()`, `parse_efi_setup()`, `efi_set_virtual_address_map()`, `efi_runtime_update_mappings()`, `arch_efi_call_virt_setup()`, and `arch_efi_call_virt_teardown()`. The assembly entry `efi_call_svam()` is declared here.

## Control flow
For each runtime descriptor, `efi_map_region()` uses the direct kernel mapping if the PFN range is already mapped, setting UC attributes for non-WB memory, or `ioremap_cache()` otherwise. `efi_set_virtual_address_map()` switches CR3 to `initial_page_table`, loads a physical GDT, disables interrupts, calls the physical-mode stub, then restores the fixmap GDT, original page tables, and TLB state. Runtime call setup only brackets FPU and firmware branch-speculation restrictions.

## State and persistence behavior
The file stores no private persistent state. It writes `md->virt_addr` in EFI descriptors and may alter page attributes for runtime regions. Several functions are no-ops because 32-bit does not use a separate `efi_mm`.

## Dependencies and integration points
It depends on x86 GDT/CR3/TLB manipulation, `efi_stub_32.S`, memory attribute APIs, EFI generic virtual-mode orchestration in `efi.c`, and FPU/speculation firmware wrappers.

## Risks and edge cases
The `SetVirtualAddressMap()` path temporarily disables paging in the stub and relies on low physical mappings and a valid GDT. Non-WB mappings must be made uncached. Null ioremap results are logged but still leave runtime services vulnerable unless higher-level code disables them.

## Test signals
32-bit EFI boot with runtime variables, non-WB runtime descriptors, NX-enabled kernels, EFI page-table dumps, and `SetVirtualAddressMap()` failures are important validation cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_64.c

## Purpose
`efi_64.c` implements 64-bit x86 EFI page-table management, runtime virtual mappings, permission updates, native runtime-call context switching, and mixed-mode thunk wrappers for calling 32-bit firmware from a 64-bit kernel.

## Important APIs, types, and functions
Core mapping APIs are `efi_alloc_page_tables()`, `efi_sync_low_kernel_mappings()`, `efi_setup_page_tables()`, `efi_map_region()`, `efi_map_region_fixed()`, `parse_efi_setup()`, `efi_runtime_update_mappings()`, `efi_set_virtual_address_map()`, and `efi_dump_pagetable()`. Runtime-call setup uses `arch_efi_call_virt_setup()`, `arch_efi_call_virt_teardown()`, `efi_enter_mm()`, LASS toggles, and `efi_runtime_lock`. Mixed-mode services include `efi_thunk_*` variable/reset/query wrappers and `efi_thunk_runtime_setup()`.

## Control flow
EFI setup allocates a private `efi_mm` page-table root and shares only non-EFI parts of the kernel address space. Runtime descriptors are first 1:1 mapped, then assigned top-down virtual addresses below `EFI_VA_START` unless mixed mode forces physical virtual addresses. `efi_setup_page_tables()` identity maps the new memory map, page zero, SEV-ES GHCBs, and, for mixed mode, low 32-bit stack/text/rodata/trampoline pages. Runtime calls synchronize low mappings, save FPU state, apply speculation restrictions, borrow `efi_mm`, disable LASS if needed, call firmware, and restore state. Mixed-mode wrappers convert kernel virtual pointers to 32-bit physical addresses before `efi64_thunk()`.

## State and persistence behavior
State includes top-down `efi_va`, previous borrowed mm pointer, saved CR4.LASS bit, `efi_runtime_lock`, `efi_disable_ibt_for_runtime`, and `efi_mixed_mode_stack_pa` from assembly. EFI descriptors persist 1:1 and virtual mappings. Runtime permission updates honor EFI memory attributes for RO/NX and encrypted memory.

## Dependencies and integration points
It integrates with x86 page-table allocation, temporary-mm switching, SEV-ES, confidential-computing encryption bits, LASS, IBT policy, EFI memory attributes table, mixed-mode assembly thunks, FPU/speculation wrappers, UCS-2 variable names, and generic EFI runtime dispatch.

## Risks and edge cases
Firmware may still use stale physical pointers, requiring 1:1 mappings. Mixed mode requires all callable code/data/stack addresses to fit in 32-bit physical space. Pointer conversion rejects buffers crossing page boundaries. Runtime calls are serialized for mixed-mode variable/reset paths. Permission tightening must wait until after `SetVirtualAddressMap()`.

## Test signals
Native 64-bit EFI runtime variables, mixed 32-bit firmware boots, kexec, SEV-ES guests, LASS-capable CPUs, EFI memory attribute tables, IBT-enabled kernels, capsule/query-variable behavior, and page-table dump inspection are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_32.S

## Purpose
`efi_stub_32.S` provides the 32-bit assembly stub used to call EFI `SetVirtualAddressMap()` in physical addressing mode with interrupts disabled.

## Important APIs, types, and functions
The sole symbol is `efi_call_svam`. It receives the runtime-services-table pointer and arguments from the C wrapper in `efi_32.c`, switches to a flat physical alias of itself, disables paging, calls `EFI_svam`, captures the remapped runtime-services pointer, re-enables paging, and returns.

## Control flow
The stub saves frame state and `%ebx`, pushes the call arguments, jumps to the physical alias of label `1`, clears CR0.PG, converts `%esp` from kernel virtual to physical by subtracting `__PAGE_OFFSET`, calls firmware, stores the new `efi.runtime` pointer through the supplied physical output argument, sets CR0.PG again, restores stack/frame state, and returns.

## State and persistence behavior
It directly mutates CR0 paging state for the duration of the call and writes the C-visible runtime-services pointer. It does not allocate memory or retain local state.

## Dependencies and integration points
It depends on the IA32 calling convention, `EFI_svam` offset from asm offsets, `__PAGE_OFFSET`, the C wrapper having installed suitable CR3/GDT state, and firmware accepting physical-mode execution.

## Risks and edge cases
Any missing identity/flat mapping, wrong stack conversion, or invalid GDT/segment state can crash during early boot. Interrupts must remain disabled because handlers are not valid while paging and address interpretation are changed.

## Test signals
32-bit EFI boot reaching successful `SetVirtualAddressMap()`, runtime variable access after virtual-mode entry, and fault-free transition with EFI debug page-table dumps provide validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_64.S

## Purpose
`efi_stub_64.S` adapts Linux x86_64 function calling to the EFI x86_64 ABI for native firmware runtime calls.

## Important APIs, types, and functions
The sole symbol is `__efi_call`. It is an assembly ABI shim used by the `arch_efi_call_virt()` machinery.

## Control flow
The stub saves `%rbp`, aligns the stack to 16 bytes, reserves EFI shadow/home space, moves Linux register arguments into EFI-required registers, stores stack arguments, and performs an indirect no-speculation call through the function pointer in `%rdi`. It then restores the frame and returns.

## State and persistence behavior
No persistent state is kept. The only mutations are transient stack/register ABI conversions during the firmware call.

## Dependencies and integration points
It depends on x86_64 Linux and Microsoft/EFI ABI differences, `CALL_NOSPEC`, no-CFI annotation for firmware code, and C wrappers that already switched into `efi_mm` and prepared FPU/speculation state.

## Risks and edge cases
Stack alignment and home-space layout must exactly match EFI firmware expectations. Indirect calls into firmware lack kernel CFI metadata, hence explicit annotations are needed to avoid objtool/CFI issues.

## Test signals
Native 64-bit EFI runtime service calls such as GetVariable/SetVariable/ResetSystem under CFI, retpoline/no-spec, and page-table switching configurations validate this shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_thunk_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_thunk_64.S

## Purpose
`efi_thunk_64.S` implements the long-mode-to-compatibility-mode thunk used by 64-bit kernels to call 32-bit EFI runtime services after ExitBootServices in mixed-mode EFI.

## Important APIs, types, and functions
The main symbol is `__efi64_thunk`; return support is in read-only data symbol `__efi64_thunk_ret_tramp`; `efi_mixed_mode_stack_pa` is a BSS variable holding the physical low-memory stack top allocated by `efi_setup_page_tables()`.

## Control flow
The thunk saves `%rbp/%rbx`, switches to the 1:1 mapped 32-bit stack, copies stack-passed arguments into 32-bit layout, computes physical addresses for return labels by subtracting the kernel physical mapping delta, builds a 32-bit return frame and argument area, then uses `lretq` to enter `__KERNEL32_CS` at the EFI runtime service address. The 32-bit trampoline returns through a far return to 64-bit code, restores the original stack and saved registers, and returns to C.

## State and persistence behavior
Persistent state is only `efi_mixed_mode_stack_pa`, set by C code. Runtime mutations are limited to stack switching and far control transfers.

## Dependencies and integration points
It depends on mixed-mode C wrappers in `efi_64.c`, identity mappings for kernel text/rodata/trampoline and low stack, `phys_base`, segment descriptors `__KERNEL32_CS`/`__KERNEL_CS`, and objtool annotations for nonstandard stack frames.

## Risks and edge cases
All firmware-call targets, arguments, stack, and trampoline addresses must be representable to 32-bit firmware. Incorrect identity mappings or segment descriptors would fault in compatibility mode. The dummy return instruction exists for objtool, not runtime behavior.

## Test signals
64-bit kernel booted via 32-bit EFI, variable service calls, ResetSystem, query-variable-info, and mixed-mode runtime calls under interrupt-capable paths are the key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_thunk_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/memmap.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/memmap.c

## Purpose
`memmap.c` contains common EFI memory-map allocation, replacement, splitting, and insertion helpers used by x86 EFI setup and later memory-map modifications. It abstracts early memblock allocation versus late page allocation and updates EFI descriptors around inserted attribute ranges.

## Important APIs, types, and functions
Important functions are `efi_memmap_alloc()`, `efi_memmap_install()`, `efi_memmap_split_count()`, and `efi_memmap_insert()`. Internal helpers allocate via `memblock_phys_alloc()` or `alloc_pages()` and free through memblock or page allocator based on map flags.

## Control flow
`efi_memmap_alloc()` computes size from entry count and current descriptor size/version, selects slab/page allocation when available or memblock early allocation otherwise, records allocation flags, and returns a physical map address. `efi_memmap_install()` unmaps the current map, initializes the new map using existing mapping mode, and frees the old storage unless EFI paravirtual mode bypasses replacement. Split/count and insert helpers determine how many descriptors are needed when a target range bisects existing descriptors, then copy and split descriptors while OR-ing requested attributes into covered portions.

## State and persistence behavior
The helpers update `struct efi_memory_map_data` and, through `efi_memmap_install()`, replace global `efi.memmap`. Allocation flags encode whether old storage is freed through memblock or normal pages. Inserted maps preserve descriptor size/version and only alter descriptor ranges/attributes.

## Dependencies and integration points
It depends on generic EFI memmap internals, memblock, page allocator, early/late mapping functions, EFI page alignment, and callers such as EFI quirks, runtime virtual-mode setup, and memory reservation code.

## Risks and edge cases
Inserted ranges must be EFI-page aligned; otherwise the function warns and returns. Buffer sizing must include all possible split descriptors, normally computed by `efi_memmap_split_count()`. `efi_memmap_install()` intentionally does not switch early/late mapping modes, so callers must pass compatible data.

## Test signals
EFI memmap replacement during boot, adding attributes that split descriptors into two or three pieces, late allocation after slab availability, paravirtual EFI bypass, and leak/failure checks on allocation or install errors are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/memmap.c -->
