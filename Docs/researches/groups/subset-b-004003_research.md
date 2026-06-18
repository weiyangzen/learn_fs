# subset-b-004003 research group

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-its.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-its.c

## Purpose

`irq-gic-v3-its.c` implements the ARM GICv3 Interrupt Translation Service driver. It discovers ITS blocks from device tree or ACPI, allocates ITS command queues and BASER tables, creates MSI parent domains for device LPIs, configures per-CPU redistributor LPI tables, and provides the GICv4/GICv4.1 virtual LPI and virtual PE support used by KVM. The file is the bridge between Linux MSI allocation, physical LPI routing, ITS command submission, redistributor LPI state, and virtualization-specific doorbell/VPE mechanisms.

## Important APIs, Types, And Functions

Key data types are `struct its_node`, `struct its_device`, `struct event_lpi_map`, `struct its_collection`, `struct its_baser`, `struct its_cmd_desc`, `struct its_cmd_block`, `struct lpi_range`, `struct cpu_lpi_count`, and the global `vpe_proxy` state. `struct its_node` owns one hardware ITS instance, its MMIO base, command queue, BASER backing tables, MSI domain data, collections, quirks, and device list. `struct its_device` owns one DevID's ITT and LPI/event maps. `event_lpi_map` tracks physical LPIs, collection mappings, VLPI mappings, and the owning VM when events are forwarded.

The low-level command path is built around encoder helpers such as `its_encode_cmd()`, `its_encode_devid()`, `its_encode_event_id()`, `its_encode_target()`, `its_encode_vpeid()`, and builder functions including `its_build_mapd_cmd()`, `its_build_mapti_cmd()`, `its_build_movi_cmd()`, `its_build_inv_cmd()`, `its_build_vmapp_cmd()`, `its_build_vmapti_cmd()`, `its_build_vmovp_cmd()`, `its_build_invdb_cmd()`, and `its_build_vsgi_cmd()`. `its_send_single_command()` and `its_send_single_vcommand()` allocate a queue entry, encode a command, optionally add `SYNC` or `VSYNC`, flush or order the command memory, write `GITS_CWRITER`, and wait for `GITS_CREADR` to advance.

LPI allocation is managed by `its_lpi_init()`, `alloc_lpi_range()`, `free_lpi_range()`, `its_lpi_alloc()`, and `its_lpi_free()`. Table allocation and programming is handled by `its_setup_lpi_prop_table()`, `allocate_lpi_tables()`, `its_cpu_init_lpis()`, `its_setup_baser()`, `its_parse_indirect_baser()`, `its_alloc_tables()`, `its_alloc_table_entry()`, `its_alloc_device_table()`, and `allocate_vpe_l1_table()`. MSI domain integration is centered on `its_init_domain()`, `its_msi_prepare()`, `its_msi_teardown()`, `its_irq_domain_alloc()`, `its_irq_domain_activate()`, `its_irq_domain_deactivate()`, and `its_irq_compose_msi_msg()`.

Virtualization APIs include `its_init_v4()`, `its_init_vpe_domain()`, `its_vpe_init()`, `its_vpe_teardown()`, `its_vlpi_map()`, `its_vlpi_unmap()`, `its_vlpi_prop_update()`, `its_vpe_set_affinity()`, `its_vpe_set_vcpu_affinity()`, `its_vpe_4_1_set_vcpu_affinity()`, SGI-domain helpers, and doorbell proxy helpers. Init and firmware entry points are `its_init()`, `its_cpu_init()`, `its_lpi_memreserve_init()`, `its_of_probe()`, `gic_acpi_parse_madt_its()`, and `its_acpi_probe()`.

## Control Flow

The top-level initialization path starts in `its_init()`, which creates the ITT genpool, records the GIC redistributor state and parent irq domain, probes ITS instances through OF or ACPI, allocates global LPI property and per-CPU pending tables, detects GICv4 capability, initializes VPE support when possible, and registers syscore suspend/resume callbacks. Each ITS is first reset/quiesced, then `its_node_init()` captures the hardware `GITS_TYPER`, default MSI base, fwnode, NUMA node, and domain flags. `its_probe_one()` applies quirks, computes ITS-list state for GICv4, maps GICv4.1 SGIR space, allocates the command queue, allocates BASER tables, creates collections, programs `GITS_CBASER`, enables the ITS, creates the MSI parent domain, and links the node into `its_nodes`.

CPU bring-up calls `its_cpu_init()`. If any ITS exists, it tries to disable unsafe pre-enabled LPIs, programs this CPU's redistributor LPI property and pending tables in `its_cpu_init_lpis()`, allocates or inherits GICv4.1 VPE tables, and maps one collection per ITS in `its_cpu_init_collections()`. MSI allocation first calls `its_msi_prepare()` to find or create an `its_device` for the supplied DevID, including an ITT and LPI range. `its_irq_domain_alloc()` allocates physical LPIs for the Linux IRQs, prepares IOMMU MSI translation, allocates the parent GIC LPI, and installs `its_irq_chip`. Activation selects a CPU, updates the event's collection map, and emits `MAPTI`.

Interrupt operations update LPI property bytes, route events, and submit ITS commands. Mask/unmask update the property table and invalidate by direct redistributor LPIR when available, by `INV` for physical LPIs, or by virtual invalidation for forwarded VLPIs. Affinity changes move physical LPIs with `MOVI`. Pending state injection uses `INT` and `CLEAR`. Compose-MSI writes the event ID as MSI data and uses either `GITS_TRANSLATER` or a quirked pre-ITS window as MSI target.

GICv4 transitions are layered on `irq_set_vcpu_affinity()`. Mapping a VLPI allocates per-event virtual maps, maps the VM's VPEs to the ITS if needed, flips the IRQ to forwarded state, writes the virtual property table, discards the physical mapping, and emits `VMAPTI`. Unmapping discards the virtual mapping, restores `MAPTI`, restores LPI config, and drops VM association when the last VLPI is gone. VPE IRQ allocation reserves doorbell LPIs and a virtual property table, allocates VPE IDs and VPTs, and maps VPEs eagerly or lazily depending on ITS-list and GICv4.1 capabilities. Scheduling/descheduling programs `GICR_VPROPBASER` and `GICR_VPENDBASER` or GICv4.1 VPEID fields, while VPE affinity emits serialized `VMOVP` commands and moves doorbells.

## State And Persistence Behavior

Persistent kernel state includes the global `its_nodes` list, global `its_lock`, `its_parent`, `gic_rdists`, `itt_pool`, `lpi_range_list`, `its_list_map`, `vmovp_seq_num`, per-CPU `local_4_1_its`, per-CPU LPI counts, and VPE ID allocator. Per-ITS state persists in `its_node` until boot teardown or probe failure and includes command queue memory, BASER tables, collections, quirk flags, saved control registers, and an ITS device list. Per-device state persists across MSI allocation while a DevID is active, and shared devices are intentionally retained across teardown.

The driver also persists hardware-visible memory: LPI property tables, pending tables, ITTs, BASER tables, VPE L1/L2 tables, virtual pending tables, and virtual property tables. These tables are explicitly cache-flushed or ordered with `dsb()` based on hardware shareability. EFI persistent memory reservations are used for LPI tables so a later kexec kernel can detect preprogrammed tables. Syscore suspend saves `GITS_CTLR` and `GITS_CBASER`, forces ITS quiescence, and resume restores CBASER, BASER registers, command writer state, CTLR, and local collections.

## Dependencies And Integration Points

The file depends on Linux irqdomain, MSI parent-domain helpers, IOMMU MSI preparation, OF and ACPI/IORT discovery, EFI memory reservation, memblock reserved ranges, CPU hotplug, syscore suspend/resume, GIC common helpers, redistributor state from `irq-gic-v3.c`, and public GICv4 types from `arm-gic-v4.h`. It is called by the GICv3 core through `its_init()`, `its_cpu_init()`, and `its_lpi_memreserve_init()`. It exports behavior to MSI users through created domains and to KVM through the GICv4 helper API implemented in `irq-gic-v4.c`.

The firmware integration paths are split between device tree `arm,gic-v3-its` children with `msi-controller` and ACPI MADT Generic Translator entries plus IORT domain-token registration. NUMA affinity is read from OF node NUMA IDs or ACPI SRAT GIC ITS affinity subtables. Hardware quirks alter table sizing, cacheability/shareability, pre-ITS MSI windows, VLPI redistributor offsets, DMA32 allocation constraints, and GICv4.1 invalidation behavior.

## Risks

The highest-risk areas are command queue synchronization, cacheability/shareability fallbacks, and GICv4 state transitions. A stuck ITS command queue or redistributor sync register can turn MSI delivery into timeouts. Incorrect BASER, CBASER, PROPBASER, PENDBASER, or VPROPBASER programming can corrupt memory or make LPIs disappear. Firmware that leaves LPIs enabled without reserved tables is explicitly tainted as unsafe. GICv4 lazy VM mapping, `VMOVP` serialization, vPE locking, and proxy-device doorbell mapping are concurrency-sensitive and can misroute guest interrupts if locks or reference counts drift. Shared DevIDs and proxy DevID collisions are guarded but remain integration hazards for unusual PCI aliasing or hardware layouts.

Other risks include large contiguous allocations for tables, limited VPEID space, hardware that does not preserve requested shareability, inconsistent GICv4/GICv4.1 capabilities across ITS and redistributors, ACPI systems without valid IORT/SRAT data, and error paths that intentionally leak decrypted pages if encryption state cannot be restored. The driver relies on many architecture-specific polling timeouts, so test coverage must include failure and slow-hardware paths.

## Test Signals

Useful runtime signals are boot logs reporting ITS discovery, BASER allocation, LPI property table address, pending table setup per CPU, GICv4/GICv4.1 feature enablement, DirectLPI mode, proxy device allocation, and quirk activation. Functional tests should allocate PCI MSI/MSI-X and platform MSI vectors, change affinity, mask/unmask, retrigger, hotplug CPUs, suspend/resume, and kexec across an LPI-enabled boot. Virtualization tests should map and unmap VLPIs, schedule and deschedule VPEs, move vCPUs across CPUs and redistributor affinity groups, update VLPI/VSGI properties, and verify doorbell behavior for blocking and running vCPUs. Negative tests should cover queue timeouts, invalid firmware ranges, DevID aliasing, missing ITS nodes, non-coherent devices, and systems with restricted or preallocated LPI tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-its.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-mbi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-mbi.c

## Purpose

`irq-gic-v3-mbi.c` implements GICv3 Message Based Interrupt support for systems that expose SPIs through GICD `SETSPI_NSR` and `CLRSPI_NSR` writes rather than a full ITS. It creates an MSI parent irq domain over the normal GIC domain, allocates SPIs from firmware-described MBI ranges, and composes MSI or MBI messages that devices can write to assert and, for level-capable platform MSI, clear an interrupt.

## Important APIs, Types, And Functions

The central type is `struct mbi_range`, which records an SPI base, SPI count, and allocation bitmap. Global state is `mbi_lock`, `mbi_phys_base`, `mbi_ranges`, and `mbi_range_nr`. `mbi_irq_chip` delegates mask, unmask, EOI, type, and affinity operations to the parent GIC IRQ.

`mbi_init()` is the firmware entry point called by the GICv3 core when `GICD_TYPER.MBIS` is present. It parses the OF `msi-controller`, `mbi-ranges`, and optional `mbi-alias` properties, allocates range bitmaps, records the frame physical base, and calls `mbi_allocate_domain()`. Domain operations are `mbi_irq_domain_alloc()`, `mbi_irq_domain_free()`, and the `msi_lib_irq_domain_select()` selector. `mbi_irq_gic_domain_alloc()` allocates the parent GIC SPI using an OF-style fwspec and forces edge-rising type. `mbi_compose_msi_msg()` creates a one-message set-SPI MSI, while `mbi_compose_mbi_msg()` creates set and clear messages for level-capable device MSI.

## Control Flow

Initialization is OF-only. If the GIC node lacks `msi-controller`, `mbi_init()` returns success without creating a domain. Otherwise, it validates the `mbi-ranges` property as pairs of `(spi_start, nr_spis)`, allocates a bitmap per range, determines the physical MBI frame from `mbi-alias` or the GIC resource base, and creates an MSI parent domain with `gic_v3_mbi_msi_parent_ops`.

During MSI allocation, `mbi_irq_domain_alloc()` searches all range bitmaps under `mbi_lock` for a power-of-two aligned region large enough for `nr_irqs`. It prepares the MSI through `iommu_dma_prepare_msi()` against `mbi_phys_base + GICD_SETSPI_NSR`, allocates each parent GIC SPI through `mbi_irq_gic_domain_alloc()`, and assigns `mbi_irq_chip` plus the selected range as chip data. Freeing releases the bitmap region and parent IRQs. Message composition writes the parent hwirq as MSI data and sets the target address to `SETSPI_NSR`; MBI level messages also include a `CLRSPI_NSR` clear message.

## State And Persistence Behavior

The MBI driver stores all configured ranges for the life of the kernel. Allocation state is the bitmap inside each `mbi_range`, protected by `mbi_lock`. Per-IRQ chip data points back to the owning `mbi_range` so frees can release the correct bitmap. There is no suspend/resume state in this file; persistence is primarily the static MMIO frame base and the allocated MSI parent domain.

## Dependencies And Integration Points

This driver depends on OF GIC node properties, the parent GICv3 irq domain, Linux MSI parent-domain helpers, the irq-msi-lib selector and MSI info initializer, IOMMU MSI preparation, and generic parent irq-chip delegation. It integrates into `irq-gic-v3.c` through `mbi_init(handle, gic_data.domain)` when the distributor reports MBIS. It supports PCI MSI/MSI-X and platform device MSI via `MATCH_PCI_MSI | MATCH_PLATFORM_MSI`, but explicitly rejects ACPI because the specification has no MBI description.

## Risks

Important risks are firmware description errors, bitmap sizing/alignment mismatches for multi-MSI allocations, and failing to release allocated bitmap regions if parent allocation or IOMMU preparation fails. The allocation path releases the region only after some failures, so allocation-order changes should be audited carefully. Since all parent IRQs are forced edge-rising by default, devices needing level semantics rely on the platform MSI path to mark level capability and compose clear messages. Incorrect `mbi-alias` translation would direct devices to the wrong set/clear SPI frame.

## Test Signals

Boot logs should show each MBI range and the selected MBI frame address. Tests should allocate PCI MSI, PCI MSI-X, and platform MSI vectors, verify the composed address/data pair targets `SETSPI_NSR`, verify level-capable platform MSI gets both set and clear messages, free and reallocate ranges, exercise multi-vector power-of-two allocation, and verify affinity/type operations delegate to the parent GIC domain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-mbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3.c

## Purpose

`irq-gic-v3.c` is the core ARM GICv3/GICv4 interrupt controller driver. It maps distributor and redistributor frames, configures SGIs, PPIs, SPIs, extended PPI/SPI ranges, interrupt priority and pseudo-NMI support, CPU interface system registers, irq domains, SMP IPIs, CPU hotplug, CPU power-management restore, KVM VGIC metadata, GIC errata, MBI, and ITS/LPI initialization.

## Important APIs, Types, And Functions

Core state is stored in `struct gic_chip_data gic_data`, which holds the fwnode, distributor base and physical address, redistributor regions, shared `struct rdists`, root irq domain, stride, flags, RSS support, PPI partition data, and counters. `struct redist_region` describes mapped redistributor MMIO regions. `struct partition_affinity` maps OF PPI partition fwnodes to CPU masks. Static keys control split EOI/deactivate support, pseudo-NMI support, and specific errata.

Key hardware helpers include `gic_dist_init()`, `gic_cpu_init()`, `gic_cpu_sys_reg_enable()`, `gic_cpu_sys_reg_init()`, `gic_enable_redist()`, `gic_populate_rdist()`, `gic_update_rdist_properties()`, and wait helpers for distributor/redistributor RWP. IRQ operations are provided by `gic_chip` and `gic_eoimode1_chip`, with handlers for mask/unmask, EOI, type, affinity, retrigger, irqchip state, vcpu affinity, and NMI setup/teardown. Domain operations are `gic_irq_domain_translate()`, `gic_irq_domain_alloc()`, `gic_irq_domain_free()`, `gic_irq_domain_select()`, and `gic_irq_get_fwspec_info()`.

Firmware entry points are `gic_of_init()` via `IRQCHIP_DECLARE("arm,gic-v3")` and `gic_acpi_init()` via ACPI declarations for GICv3, GICv4, and version-none distributors. Integration calls include `mbi_init()`, `its_init()`, `its_cpu_init()`, `its_lpi_memreserve_init()`, `gicv2m_init()`, `vgic_set_kvm_info()`, and `set_smp_ipi_range()`.

## Control Flow

OF initialization maps the distributor and all redistributor regions, validates the distributor version, reads redistributor stride/region count, applies OF quirks, then calls `gic_init_bases()`. ACPI initialization maps the distributor from MADT, counts and maps redistributors from GICR or GICC subtables, creates a GSI fwnode, and also calls `gic_init_bases()`. `gic_init_bases()` chooses split EOI/deactivate mode, records global state, reads `GICD_TYPER`, applies IIDR quirks, creates the root irq domain, allocates per-CPU redistributor data, handles MBI if supported, installs the top-level IRQ handler, discovers redistributor features, enables CPU system-register access, initializes priorities, distributor, boot CPU redistributor, pseudo-NMI support, SMP hooks, PM notifier, and finally ITS or GICv2m MSI support.

The interrupt handling path reads `ICC_IAR1_EL1`, detects pseudo-NMI priority when enabled, performs priority drop and instruction synchronization, dispatches to `generic_handle_domain_irq()` or `generic_handle_domain_nmi()`, and deactivates unexpected interrupts. In EOI mode 1, EOI and deactivate are split and forwarded interrupts are not deactivated by the host. Masking and state operations select redistributor or distributor registers based on INTID range, with special register offsets for EPPI/ESPI. Affinity changes mask enabled SPIs, write `IROUTER`, then restore enablement.

CPU bring-up enables SRE, locates the CPU's redistributor by MPIDR affinity, wakes it, configures SGIs/PPIs, initializes system registers, checks RSS ability for SGIs, and calls `its_cpu_init()` when LPIs are available. SMP IPI setup allocates 8 SGIs from the GIC domain and sends SGIs by grouping targets by MPIDR cluster. CPU PM exit re-enables redistributor and CPU interface state; CPU PM enter can disable group 1 and put the redistributor to sleep when distributor security is disabled.

## State And Persistence Behavior

`gic_data` is global and `__read_mostly`, with per-CPU redistributor state allocated at init. Hardware state programmed by this file persists in the distributor, redistributors, and CPU interface registers. Per-CPU `has_rss` records local SGI routing support. `dist_prio_irq`, `dist_prio_nmi`, `cpus_have_group0`, `cpus_have_security_disabled`, and pseudo-NMI static keys encode boot-time priority model decisions. PPI partitions persist as allocated masks and fwnode pointers. ACPI setup uses init-only `acpi_data` and a persistent GSI domain fwnode.

The driver does not save full distributor state in this file for system suspend. Instead, it relies on CPU PM callbacks for per-CPU redistributor and system-register restoration, while ITS-specific syscore callbacks handle ITS tables. Affinity, mask, active, and pending state live in hardware registers and Linux irqdesc/irqdomain metadata.

## Dependencies And Integration Points

The driver depends on ARM GIC architecture headers, irqdomain core, generic irq-chip handlers, OF and ACPI MADT parsing, CPU hotplug, CPU PM, SMP, ARM SMCCC for NVIDIA T241 detection, KVM VGIC info, and optional ITS, MBI, and GICv2m code. It is the parent domain for LPIs and MBI SPIs and provides redistributor feature data consumed by the ITS driver. Firmware bindings include OF `arm,gic-v3`, `#redistributor-regions`, `redistributor-stride`, `ppi-partitions`, and ACPI GIC distributor/GICC/GICR subtables.

## Risks

The sensitive areas are priority/security configuration for pseudo-NMIs, split EOI/deactivate semantics, redistributor discovery, affinity routing, extended SPI/PPI offset translation, and errata-specific aliases. Incorrect priority translation when security is enabled can break interrupt masking or NMI behavior. Redistributor mismatch prevents CPUs from coming online. EOI/deactivate bugs can leave forwarded or unhandled interrupts stuck active. ACPI disabled CPUs with inaccessible redistributors are marked in `broken_rdists`; future hotplug behavior depends on this being correct. Errata such as T241 aliasing and GIC-700 deactivation workaround change register access paths and need hardware-specific validation.

## Test Signals

Boot logs should report SPIs, ESPIs, GICD_CTLR.DS/SCR_EL3.FIQ, redistributor discovery per CPU, feature strings, pseudo-NMI enablement, MBI/ITS handoff, and quirk activation. Functional tests should cover wired IRQ allocation from OF and ACPI fwspecs, SGI/IPI delivery, SPI/ESPI type and affinity changes, PPI/EPPI per-CPU handling, CPU hotplug, CPU PM suspend/resume, pseudo-NMI setup and teardown, KVM maintenance IRQ metadata, and boot with `irqchip.gicv3_nolpi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v4.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v4.c

## Purpose

`irq-gic-v4.c` provides the public, hypervisor-facing GICv4/GICv4.1 helper layer. It hides the ITS-specific command details behind irqchip APIs and gives KVM-style users functions to allocate VPE doorbell IRQs, map and unmap guest VLPIs, schedule and deschedule VPEs, update VLPI or VSGI properties, and commit/invalidate VPE state.

## Important APIs, Types, And Functions

Static state consists of `gic_domain`, `vpe_domain_ops`, and `sgi_domain_ops`, installed by `its_init_v4()`. `gic_cpuif_has_vsgi()` checks ARM64 CPU feature registers for GICv4.1 virtual SGI support. `has_v4_1()` and `has_v4_1_sgi()` summarize initialized capabilities.

The main exported helpers are `its_alloc_vcpu_irqs()`, `its_free_vcpu_irqs()`, `its_make_vpe_non_resident()`, `its_make_vpe_resident()`, `its_commit_vpe()`, `its_invall_vpe()`, `its_map_vlpi()`, `its_get_vlpi()`, `its_unmap_vlpi()`, `its_prop_update_vlpi()`, `its_prop_update_vsgi()`, and `its_init_v4()`. `its_alloc_vcpu_sgis()` is the internal GICv4.1 virtual SGI-domain allocator.

## Control Flow

`its_init_v4()` is called by the ITS driver after it has created the VPE irq-domain operations. It records the root GIC domain and VPE/SGI domain ops and enables the public GICv4 path. A VM calls `its_alloc_vcpu_irqs()` with an `its_vm` containing VPE pointers. The helper creates a named fwnode, creates a hierarchical domain over the GIC domain using `vpe_domain_ops`, initializes each VPE's VM pointer and IDAI default, allocates one VPE doorbell IRQ per VPE, records the Linux IRQ numbers, and optionally creates a 16-entry virtual SGI domain per VPE when GICv4.1 vSGI is available.

Residency helpers build `struct its_cmd_info` values and pass them through `irq_set_vcpu_affinity(vpe->irq, info)`, relying on the ITS VPE irq_chip to interpret command types. Non-resident transitions either request GICv4.1 doorbell behavior or re-enable a masked doorbell IRQ for GICv4.0. Resident transitions disable the doorbell for GICv4.0 before guest entry, or pass group enable bits for GICv4.1. VLPI mapping, query, unmapping, pending-state, and property updates similarly use `irq_set_vcpu_affinity()` on the physical LPI IRQ, with command types such as `MAP_VLPI`, `GET_VLPI`, `PROP_UPDATE_VLPI`, and `PROP_UPDATE_AND_INV_VLPI`.

## State And Persistence Behavior

This file stores only the global domain operation pointers. VM and VPE state lives in caller-provided `struct its_vm` and `struct its_vpe` objects, plus the irq domains and fwnodes allocated here. Allocation persists until `its_free_vcpu_irqs()` frees SGI domains, frees VPE IRQs, removes the VM domain, and releases the fwnode. Runtime state transitions update VPE flags such as `resident` and `ready`, but hardware state is programmed by the ITS irq_chip implementation in `irq-gic-v3-its.c`.

## Dependencies And Integration Points

The file depends on `linux/irqchip/arm-gic-v4.h`, irqdomain APIs, generic IRQ APIs, PID naming for fwnodes, and ARM64 CPU feature access when built for ARM64. It is intentionally a thin layer over the irqchip callbacks implemented by the ITS driver. Its consumers are hypervisor code paths that know about `struct its_vm`, `struct its_vpe`, and `struct its_vlpi_map`.

## Risks

The main risk is that the API multiplexes many GICv4 operations through `irq_set_vcpu_affinity()`. Incorrect command types, null maps, or calls before `its_init_v4()` has installed domain ops result in failures that can be hard to distinguish from hardware errors. GICv4.0 doorbell masking uses nested enable/disable balancing, so residency ordering matters. Partial allocation failures must remove fwnodes and domains; SGI allocation failure after VPE IRQ allocation can leave cleanup paths sensitive to missing mappings.

## Test Signals

Tests should allocate and free VPE IRQs for VMs with multiple VPEs, verify domain and fwnode cleanup on injected failures, schedule/deschedule VPEs with and without doorbell requests, map/get/unmap VLPIs, update VLPI properties with and without invalidation, update VSGI priority/group on GICv4.1 systems, and confirm `resident` and `ready` fields track successful irqchip operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-irs.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-irs.c

## Purpose

`irq-gic-v5-irs.c` implements GICv5 Interrupt Routing Service discovery and initialization. IRS blocks route SPIs and LPIs, provide Interrupt State Tables, map CPUs to IAFFIDs, expose SPI configuration operations, synchronize IRS state, and hand off to GICv5 ITS probing. The file supports both OF and ACPI firmware descriptions and initializes global GICv5 LPI domain data from the first IRS.

## Important APIs, Types, And Functions

The main driver state is `struct gicv5_irs_chip_data`, allocated per IRS and linked on `irs_nodes`. Per-CPU mappings are stored in `per_cpu_irs_data` and `cpu_iaffid`. File-local wrappers `irs_readl_relaxed()`, `irs_writel_relaxed()`, `irs_readq_relaxed()`, and `irs_writeq_relaxed()` access IRS MMIO.

IST setup is handled by `gicv5_irs_init_ist_linear()`, `gicv5_irs_init_ist_two_level()`, `gicv5_irs_l2_sz()`, `gicv5_irs_init_ist()`, and `gicv5_irs_iste_alloc()`. Public helpers include `gicv5_irs_cpu_to_iaffid()`, `gicv5_irs_lookup_by_spi_id()`, `gicv5_spi_irq_set_type()`, `gicv5_irs_syncr()`, `gicv5_irs_register_cpu()`, `gicv5_irs_remove()`, `gicv5_irs_enable()`, `gicv5_irs_its_probe()`, `gicv5_irs_of_probe()`, and `gicv5_irs_acpi_probe()`.

## Control Flow

OF probing iterates child nodes under the parent and initializes those compatible with `arm,gic-v5-irs`. `gicv5_irs_of_init()` allocates chip data, maps the `ns-config` register range, initializes base registers and cacheability with `gicv5_irs_init_bases()`, reads IAFFID width, parses CPU and `arm,iaffids` arrays, and calls `gicv5_irs_init()`. ACPI probing parses MADT GICv5 IRS subtables, reserves/maps IRS config space, initializes bases, parses GICC entries matching the current IRS ID to populate IAFFID mappings, and also calls `gicv5_irs_init()`.

`gicv5_irs_init()` validates LPI support, records the IRS SPI range, and for the first IRS initializes global virtual capability, priority bits, global SPI count, and the GICv5 LPI domain. `gicv5_irs_enable()` later initializes the IST on the first IRS. IST initialization reads IDR2 capabilities, chooses linear or two-level tables, caps ID bits by CPUIF support, chooses IST entry size and L2 table size, writes `IRS_IST_CFGR` and `IRS_IST_BASER`, waits for idle, and calls `gicv5_init_lpis()`. With two-level ISTs, `gicv5_irs_iste_alloc()` lazily allocates L2 tables for an LPI and asks the IRS to map the L2 entry.

CPU registration uses the previously parsed IAFFID and per-CPU IRS pointer. `gicv5_irs_register_cpu()` writes `IRS_PE_SELR`, waits for a valid PE selection, writes `IRS_PE_CR0_DPS`, and waits for completion. SPI type changes lock `spi_config_lock`, select the SPI, validate selection, write level/edge mode, and wait for the operation. `gicv5_irs_syncr()` writes `IRS_SYNCR` and waits on sync status. After IRSes are available, `gicv5_irs_its_probe()` invokes OF or ACPI GICv5 ITS probing.

## State And Persistence Behavior

Persistent state includes the global `irs_nodes` list, per-CPU IRS pointers, per-CPU IAFFID validity, and global GICv5 data updated by the first IRS. Per-IRS state stores MMIO base, fwnode, SPI range, flags, and a raw spinlock for SPI config. IST memory is allocated and intentionally ignored by kmemleak after hardware ownership. Two-level IST global metadata stores the L1 table address, L2 size, and L2 index bits. `gicv5_irs_remove()` tears down LPI domains, deinitializes LPIs, unmaps IRS MMIO, removes list entries, and frees chip data.

## Dependencies And Integration Points

The driver depends on GICv5 architecture helpers and global data from `arm-gic-v5.h`, OF and ACPI MADT parsing, kmemleak, cache maintenance helpers for non-coherent IRS blocks, and GICv5 ITS/LPI domain helpers such as `gicv5_init_lpi_domain()`, `gicv5_free_lpi_domain()`, `gicv5_init_lpis()`, `gicv5_deinit_lpis()`, `gicv5_its_of_probe()`, and `gicv5_its_acpi_probe()`. Firmware integration uses OF `reg-names = "ns-config"`, `cpus`, `arm,iaffids`, optional `dma-noncoherent`, and ACPI IRS/GICC fields including IRS ID, IAFFID, and non-coherent flags.

## Risks

Risks include incorrect IAFFID-to-CPU mapping, invalid firmware counts between CPUs and IAFFIDs, non-coherent cache maintenance mistakes, IST sizing errors, and lazy L2 allocation races. The code relies on irqdomain serialization for `gicv5_irs_iste_alloc()` rather than an internal lock. Linear IST allocation can approach kmalloc limits and caps LPI ID bits if necessary. ACPI parsing uses transient globals for the current IRS while scanning GICC entries, so future parallelization would need serialization. SPI configuration depends on correct IRS lookup and operation-status validity bits.

## Test Signals

Boot logs should show IRS detection, SPI ranges, IAFFID parsing warnings, global SPI counts, IST initialization failures, and LPI support checks. Tests should cover OF and ACPI probing, non-coherent IRS cache paths, CPU registration for every possible CPU, SPI type changes for edge and level variants, SPI lookup by ID, global sync, one-level and two-level IST initialization, lazy L2 IST allocation, GICv5 ITS handoff, and cleanup through `gicv5_irs_remove()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-irs.c -->
