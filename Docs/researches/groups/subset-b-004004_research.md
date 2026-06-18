# subset-b-004004 Research

Grouped research for Linux irqchip source files in subset B work item `subset-b-004004`. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-its.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-its.c

## Purpose
Implements the GICv5 Interrupt Translation Service used for MSI translation into LPIs. It owns ITS device table setup, per-device interrupt translation tables, MSI parent domain creation, EventID allocation, and OF/ACPI discovery of ITS and translate frames.

## Important APIs, Types, And Functions
`struct gicv5_its_chip_data` stores the ITS MMIO base, fwnode, xarray of registered devices, device-table configuration, MSI domain flags, and non-coherency flag. `struct gicv5_its_dev` represents one MSI requester with DeviceID, ITT configuration, EventID bitmap, event count, and translation-frame physical address. Important helpers include `gicv5_its_init_bases()`, `gicv5_its_init_devtab()`, `gicv5_its_device_register()`, `gicv5_its_alloc_device()`, `gicv5_its_msi_prepare()`, `gicv5_its_irq_domain_alloc()`, `gicv5_its_irq_domain_activate()`, and `gicv5_its_compose_msi_msg()`.

## Control Flow
Probe maps the ITS configuration frame, disables firmware-enabled ITS instances if needed, programs CR1 memory attributes, builds a linear or two-level device table from IDR capabilities, enables ITS CR0, and creates an MSI parent irqdomain above the GICv5 LPI domain. MSI preparation receives DeviceID and translation address through MSI allocation scratchpad, registers a device table entry, allocates an ITT, and stores the device in an xarray. Domain allocation reserves EventIDs, prepares IOMMU MSI translation, allocates parent LPIs, and encodes DeviceID/EventID into the irq hwirq. Activation maps EventID to the parent LPI in the ITT; deactivation clears that ITT entry.

## State And Persistence
State is in kernel memory plus hardware-visible tables. Device table and ITT entries are regular allocated memory exposed to hardware through physical addresses, with explicit cache maintenance for non-coherent ITS instances. `event_map` persists allocated EventID ranges until MSI teardown. Hardware caches are invalidated with ITS INV/SYNC registers, and interrupt translation persists in device/ITT entries until deactivate/free or device unregister.

## Dependencies And Integration Points
The driver depends on GICv5 core LPI domains, `gicv5_wait_for_op*()`, IRS synchronization, MSI library helpers, IOMMU MSI preparation, OF address parsing, ACPI MADT GICv5 ITS/translate records, and IORT domain tokens. It integrates with PCI/platform MSI users through the MSI parent irqdomain and with the GICv5 core through parent LPI allocation and `gicv5_irs_syncr()`.

## Risks
The table layout code is sensitive to DeviceID/EventID bit counts, L2 table sizes, `KMALLOC_MAX_SIZE` capping, and physical address mask fields. A bad cache-maintenance decision can make non-coherent systems lose translations. Fixed-message-data allocations rely on single-IRQ EventIDs. Error paths must unwind xarray entries, bitmaps, ITTs, and device-table validity in the right order.

## Test Signals
Build with GICv5, MSI, OF, ACPI, and IOMMU MSI support. Runtime signals are ITS enable messages, successful MSI allocation for PCI or platform devices, correct `/proc/interrupts` LPI delivery, no `EventID outside of ITT range` or cache-sync timeout logs, working MSI teardown/reallocation, and suspend/resume or driver reprobe without stale device-table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-its.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-iwb.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-iwb.c

## Purpose
Implements the GICv5 Interrupt Wire Bridge, which exposes wired interrupt inputs as an MSI-style device domain so wired sources can be delivered through the GICv5 LPI/MSI hierarchy.

## Important APIs, Types, And Functions
`struct gicv5_iwb_chip_data` stores the IWB MMIO base and number of 32-bit wire-enable registers. `iwb_msi_template` defines the wired-to-MSI domain, chip callbacks, fixed message-data allocation, and OF/ACPI translation. Core functions are `gicv5_iwb_init_bases()`, `gicv5_iwb_create_device_domain()`, `gicv5_iwb_irq_domain_translate()`, `gicv5_iwb_set_type()`, `gicv5_iwb_irq_enable()`, and `gicv5_iwb_irq_disable()`.

## Control Flow
Platform probe maps the single IWB resource, reads IDR0 to derive the wire count, verifies firmware has already enabled IWB CR0, clears all WENABLER registers, waits for the enable operation to become idle, and creates a per-device MSI domain sized to the number of wires. IRQ enable first enables the physical wire and then the parent IRQ; disable reverses this by disabling the wire and then the parent. Type setting modifies WTMR bits to distinguish level and edge inputs.

## State And Persistence
The driver persists only the MMIO base, register count, and MSI device domain in memory. Hardware state is the WENABLER and WTMR bitmaps. It intentionally leaves CR0 enable ownership to firmware and does not provide a remove path or runtime power state handling.

## Dependencies And Integration Points
It depends on GICv5 shared register definitions, `gicv5_wait_for_op_atomic()`, Linux MSI domain templates, OF platform probing, ACPI device ID `ARMH0003`, and the parent MSI domain attached to the platform device. ACPI GSI translation extracts the IWB wire from encoded GICv5 GSI fields.

## Risks
The code assumes firmware enabled the IWB; systems that expect Linux to enable it will fail probe. Wire register bounds must match IDR0, or enable/type operations reject interrupts. Since the MSI write callback is intentionally empty, correctness depends on fixed message data and parent MSI plumbing rather than a normal generated MSI message.

## Test Signals
Test OF and ACPI enumeration, creation of a `DOMAIN_BUS_WIRED_TO_MSI` device domain, wired interrupt delivery for low/high and rising/falling sources, disable/enable cycles clearing WENABLER bits, and failure behavior when CR0 is disabled or wire numbers exceed IDR0 capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-iwb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5.c

## Purpose
Provides the core ARM GICv5 irqchip. It creates separate irqdomains for PPIs, SPIs, LPIs, and IPIs, implements system-instruction based mask/unmask/EOI/state operations, initializes CPU interfaces, registers CPUs with IRS, and supports OF/ACPI initialization.

## Important APIs, Types, And Functions
Global state lives in `struct gicv5_chip_data gicv5_global_data`, plus `lpi_ida`, `num_lpis`, `pri_bits`, and `base_ipi_virq`. Important irq chips are `gicv5_ppi_irq_chip`, `gicv5_spi_irq_chip`, `gicv5_lpi_irq_chip`, and `gicv5_ipi_irq_chip`. Key functions are `gicv5_init_common()`, `gicv5_init_domains()`, `gicv5_handle_irq()`, `handle_irq_per_domain()`, `gicv5_starting_cpu()`, `gicv5_hwirq_init()`, PPI sysreg state helpers, SPI/LPI affinity callbacks, and LPI allocation/free domain operations.

## Control Flow
OF or ACPI first probes the IRS layer, initializes the LPI domain, then `gicv5_init_common()` creates PPI/SPI/IPI domains, reads CPU interface priority and ID bit capacities, initializes the boot CPU interface, installs `gicv5_handle_irq`, enables IRS, registers CPU hotplug state, allocates per-CPU IPIs from the IPI hierarchy, and probes ITS nodes. Interrupt handling issues `CDIA`, validates the returned interrupt, applies GSB/ISB ordering, extracts type and ID, and dispatches into the matching irqdomain.

## State And Persistence
Static global data holds irqdomain pointers, CPU interface capabilities, SPI counts, IRS capability state, and fwnode. LPI IDs are allocated from an IDA and released on domain free. CPU-local PPI enable, priority, PCR, and CR0 registers are programmed on each CPU start. Hardware affinity, priority, pending, and active state are stored in GICv5 system-instruction-visible state rather than memory-mapped distributor registers.

## Dependencies And Integration Points
The core depends on ARM64 FEAT_GCIE CPU capability checks, GICv5 IRS helpers, ITS probing, KVM VGIC info, cpuhotplug, hierarchical irqdomains, SMP IPI setup, OF `arm,gic-v5`, ACPI MADT GICv5 IRS records, and IORT IWB token lookup for GSI routing. The LPI domain is the parent for ITS and IWB interrupt delivery.

## Risks
Ordering is critical around system instructions: masking uses GSB/ISB to satisfy lazy-disable and acknowledge rules. Domain `select()` paths assume firmware fwspec formats are consistent. LPI allocation must free IRS ISTE state and IDA IDs on partial failures. CPU interface capability mismatches produce hard boot failures on affected CPUs.

## Test Signals
Boot on GICv5 hardware or emulation with FEAT_GCIE, validate PPI/SPI/LPI/IPI delivery, CPU hotplug registration, SMP IPIs, MSI via ITS/IWB, KVM maintenance IRQ setup when virtualization is available, irqchip pending/active state operations, affinity changes, and ACPI GSI routing for regular GSI and IWB encoded GSI values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic.c

## Purpose
Implements the classic ARM GICv1/GICv2 interrupt controller, including distributor and CPU interface setup, irqdomain mapping for SGI/PPI/SPI interrupts, SMP IPI delivery, CPU PM save/restore, KVM VGIC information, cascaded secondary GICs, OF probing, and ACPI MADT probing.

## Important APIs, Types, And Functions
`struct gic_chip_data` stores distributor/CPU base addresses, raw mappings, non-banked per-CPU aliases, saved PM state, irqdomain, and interrupt count. Important chip callbacks include `gic_mask_irq()`, `gic_unmask_irq()`, `gic_eoi_irq()`, `gic_eoimode1_*()`, `gic_set_type()`, `gic_set_affinity()`, `gic_ipi_send_mask()`, and irqchip state get/set. Initialization is centered on `gic_of_init()`, `gic_v2_acpi_init()`, `gic_of_setup()`, `gic_init_bases()`, `__gic_init_bases()`, `gic_dist_init()`, and `gic_cpu_init()`.

## Control Flow
Probe maps distributor and CPU interface registers, handles quirks, decides whether split EOI/deactivate can be used, creates a linear irqdomain, initializes distributor targets/configuration, initializes the boot CPU interface, installs `gic_handle_irq`, sets up SMP IPIs, and optionally initializes GICv2m MSI frames. Runtime interrupt handling reads `GIC_CPU_INTACK`, filters spurious IDs, performs EOI early in split mode, stores SGI source encodings, and dispatches through the domain. Cascaded GICs use a chained handler that reads their CPU interface and dispatches to a secondary domain.

## State And Persistence
The driver keeps static `gic_data[]`, per-CPU SGI source state, CPU target maps, and static keys for deactivate and read-modify-write access. PM support saves SPI enable/active/config/target and per-CPU PPI enable/active/config registers, then restores them before re-enabling the distributor and CPU interface. No on-disk state exists; persistence is MMIO register programming across boot, suspend, and CPU hotplug.

## Dependencies And Integration Points
It depends on `irq-gic-common`, ARM/ARM64 exception hooks, cpuhotplug, CPU PM notifiers, OF and ACPI IRQ initialization, KVM VGIC info, GICv2m MSI support, and optional non-banked GIC handling. It integrates with device tree compatibles such as `arm,gic-400`, `arm,cortex-a9-gic`, and `qcom,msm-qgic2`, and with ACPI `GENERIC_DISTRIBUTOR`/`GENERIC_INTERRUPT` records.

## Risks
Register ordering and EOI/deactivate mode are high risk, especially for forwarded interrupts. Broken firmware ranges may hide GICv2 deactivate registers unless `irqchip.gicv2_force_probe` is used. CPU target mapping must match hardware CPU interface IDs. PM save/restore can lose edge interrupts while powered down, as noted by the source comments. Non-banked and byte-access quirks are platform specific.

## Test Signals
Build on ARM and ARM64 with OF and ACPI variants. Runtime coverage should include boot IRQ delivery, SGI/IPI operation, CPU hotplug, suspend/resume, cascaded child GICs, GICv2m MSI users, KVM VGIC initialization, `irqchip.gicv2_force_probe` behavior on broken ranges, and spurious IRQ handling under interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-goldfish-pic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-goldfish-pic.c

## Purpose
Implements the 32-source Goldfish virtual platform PIC for MIPS/Goldfish systems as a cascaded interrupt controller behind one parent IRQ.

## Important APIs, Types, And Functions
`struct goldfish_pic_data` stores the MMIO base and legacy irqdomain. `goldfish_pic_of_init()` maps resources, allocates a generic chip named `GFPIC`, configures enable/disable registers, creates the legacy domain, and installs `goldfish_pic_cascade()`. The cascade handler reads `GFPIC_REG_IRQ_PENDING`, handles each set bit, and dispatches through `generic_handle_domain_irq()`.

## Control Flow
OF init maps the parent IRQ and register block, disables all PIC interrupts, sets generic chip callbacks to `irq_gc_unmask_enable_reg` and `irq_gc_mask_disable_reg`, creates a 32-entry legacy domain rooted at hardware base 8, and chains the parent IRQ. Runtime cascade drains all pending bits from high to low using `__fls()`.

## State And Persistence
State is limited to the allocated private struct, generic chip mask cache, irqdomain, and MMIO enable/disable state. There is no suspend/resume handler or dynamic allocation after initialization.

## Dependencies And Integration Points
It depends on OF IRQ/address parsing, generic irqchip helpers, chained IRQ support, and the `google,goldfish-pic` compatible. It integrates with the parent interrupt controller through a single parent IRQ and exposes child IRQs via a one-cell legacy domain.

## Risks
The fixed `GFPIC_IRQ_BASE` can conflict if platform IRQ numbering assumptions change. The cascade handler does not mask while dispatching each source, so level sources depend on child handlers and hardware state behaving normally. Error unwinding must dispose the parent mapping and destroy the generic chip.

## Test Signals
Boot a Goldfish DT platform, confirm parent cascade registration, map all 32 child interrupts, trigger multiple pending bits simultaneously, verify mask/unmask MMIO effects, and test init failure paths with missing parent IRQ or MMIO resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-goldfish-pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-hip04.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-hip04.c

## Purpose
Implements the HiSilicon HiP04 interrupt controller, a GIC-like controller with different target-register layout and up to 510 interrupts.

## Important APIs, Types, And Functions
`struct hip04_irq_data` stores distributor and CPU interface bases, irqdomain, and IRQ count. Core callbacks are `hip04_mask_irq()`, `hip04_unmask_irq()`, `hip04_eoi_irq()`, `hip04_irq_set_type()`, `hip04_irq_set_affinity()`, and `hip04_ipi_send_mask()`. Initialization uses `hip04_of_init()`, `hip04_irq_dist_init()`, `hip04_irq_cpu_init()`, and `hip04_irq_domain_map()`.

## Control Flow
OF init maps the distributor and CPU interface, initializes CPU maps to all bits, reads the controller interrupt count and caps it at 510, allocates legacy IRQ descriptors and a legacy domain, sets the global IRQ handler, configures the distributor, and registers a CPU hotplug startup callback for CPU interfaces. Runtime handling reads INTACK in a loop and dispatches valid IDs through the legacy domain.

## State And Persistence
Global `hip04_data` and `hip04_cpu_map[]` persist for the boot lifetime. Hardware state consists of distributor target/config/enable registers and CPU interface priority/control registers. There is no PM save/restore path in this file.

## Dependencies And Integration Points
It depends on ARM exception and SMP APIs, `irq-gic-common` helpers, OF mapping, legacy irqdomains, and the `hisilicon,hip04-intc` compatible. SMP integration uses `set_smp_ipi_range()` and CPU hotplug state.

## Risks
The target register format differs from standard GIC; affinity writes use 16-bit fields for pairs of interrupts. Locking protects mask/type/affinity operations, so missing lock coverage can race MMIO updates. Legacy descriptor allocation can fail or collide with platform assumptions.

## Test Signals
Run boot, timer, peripheral IRQ, SMP IPI, affinity migration, CPU hotplug, and PPI/SPI trigger-type tests on HiP04 hardware. Check that interrupt count is capped correctly and that invalid DT mappings fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-hip04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-i8259.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-i8259.c

## Purpose
Implements the legacy dual 8259A/XT-PIC interrupt controller, including ISA IRQ mask state, initialization command words, spurious IRQ handling, syscore resume/shutdown, polling, and optional OF cascaded setup.

## Important APIs, Types, And Functions
Global state includes `i8259A_auto_eoi`, `i8259A_lock`, `cached_irq_mask`, and `i8259_poll`. `i8259A_chip` provides mask, unmask, disable, and mask-ack callbacks. Important functions are `init_8259A()`, `disable_8259A_irq()`, `enable_8259A_irq()`, `mask_and_ack_8259A()`, `i8259A_irq_real()`, `__init_i8259_irqs()`, `make_8259A_irq()`, and `i8259_irq_dispatch()`.

## Control Flow
Initialization reserves PIC I/O port resources, sends ICW commands to master and slave PICs, restores cached masks, creates a legacy 16-entry IRQ domain at `I8259A_IRQ_BASE`, requests the cascade IRQ, and registers syscore ops. Runtime mask/ack first updates cached masks, writes IMR, then sends specific EOI to slave and master in the required order. OF init additionally maps a parent IRQ and installs a chained dispatcher that polls for the active hwirq.

## State And Persistence
The cached mask is the authoritative software copy of the two PIC IMR registers. `i8259A_auto_eoi` records initialization mode and controls resume/shutdown behavior. Syscore resume reinitializes the PIC; shutdown masks both controllers. No dynamically allocated per-interrupt state is used beyond the irqdomain.

## Dependencies And Integration Points
It depends on arch I/O port accessors, `asm/i8259.h`, irqdomain legacy mapping, syscore ops, and optional OF compatible `intel,i8259`. It integrates with ISA-style users expecting IRQ 0-15 numbering and can use a platform-provided poll function through `i8259_set_poll()`.

## Risks
8259A ordering is fragile; the source explicitly requires masking before EOI and slave EOI before master cascade EOI. Spurious IRQ7/IRQ15 handling must avoid slow ISR reads except on suspicious masked IRQs. Auto-EOI mode changes chip behavior by replacing mask-ack with simple disable.

## Test Signals
Validate boot on legacy PIC systems, ISA IRQ enable/disable, spurious IRQ accounting, cascade IRQ request, syscore resume after suspend, shutdown quiescence, OF parent dispatch, and custom polling through `i8259_set_poll()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-i8259.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-idt3243x.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-idt3243x.c

## Purpose
Implements the IDT/Renesas 79RC3243x 32-source interrupt controller as a cascaded generic irqchip.

## Important APIs, Types, And Functions
`struct idt_pic_data` holds the MMIO base, irqdomain, and generic chip pointer. `idt_pic_init()` maps the parent and MMIO resources, creates a linear domain, allocates domain generic chips, sets mask/unmask callbacks, masks all sources, and installs `idt_irq_dispatch()`.

## Control Flow
Runtime dispatch enters from the parent chained IRQ, reads pending bits, masks out sources that are disabled in `gc->mask_cache`, and forwards each set bit to the domain. Child interrupts use `handle_level_irq`, `irq_gc_mask_set_bit`, and `irq_gc_mask_clr_bit` against the PIC mask register.

## State And Persistence
State is the private struct, domain, generic chip `mask_cache`, and the hardware mask register. There are no power-management callbacks or late dynamic state beyond IRQ mappings.

## Dependencies And Integration Points
It depends on OF IRQ/address helpers, chained IRQ support, generic irqchip, and compatible `idt,32434-pic`. It exposes a 32-entry linear domain under one parent interrupt line.

## Risks
The dispatcher relies on `mask_cache` matching the hardware mask register; out-of-band writes would cause stale filtering. All IRQs are level handled, so edge-like sources need hardware latching. Init error paths must clean parent mapping and MMIO.

## Test Signals
Test parent cascade registration, pending-bit fan-out, mask cache filtering, all 32 child mappings, and probe failures with missing parent IRQ, MMIO base, or domain allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-idt3243x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imgpdc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imgpdc.c

## Purpose
Implements the Imagination PowerDown Controller interrupt controller, exposing peripheral wake interrupts and syswake pins with wake routing, trigger programming, and chained parent IRQ handlers.

## Important APIs, Types, And Functions
`struct pdc_intc_priv` stores counts, peripheral IRQ array, shared syswake IRQ, irqdomain, MMIO base, cached `PDC_IRQ_ROUTE`, and a raw spinlock. Important functions are `pdc_intc_probe()`, `pdc_intc_setup()`, `perip_irq_mask()`, `perip_irq_unmask()`, `syswake_irq_set_type()`, `pdc_irq_set_wake()`, `pdc_intc_perip_isr()`, and `pdc_intc_syswake_isr()`.

## Control Flow
Probe reads `num-perips` and `num-syswakes`, maps peripheral parent IRQs plus one syswake parent IRQ, creates a 16-entry linear domain, allocates two generic chips with edge and level chip types for syswake sources, initializes routing with syswakes disabled, then chains all parent lines. Peripheral parent IRQs map one-to-one to hwirqs 0-7; the shared syswake parent reads status and enable registers and dispatches hwirqs 8-15.

## State And Persistence
The cached `irq_route` is persistent software state because the route register contains both mask and wake bits. Syswake trigger mode is programmed in per-pin registers and handler type is updated with `irq_setup_alt_chip()`. Wake enable state is propagated to destination parent IRQs using `irq_set_irq_wake()`.

## Dependencies And Integration Points
It depends on platform devices, OF properties, generic irqchip, chained IRQs, raw spinlocks, and compatible `img,pdc-intc`. It integrates with system suspend through IRQ wake flags and with peripheral/syswake consumers through the PDC irqdomain.

## Risks
Route register sharing makes generic cached mask callbacks unsafe for peripheral masks, hence custom locked route updates. `num-perips` and `num-syswakes` are capped at 8; bad DT counts fail probe. Wake routing must stay synchronized with destination parent wake state to preserve standby wake behavior.

## Test Signals
Validate DT count parsing, surplus peripheral IRQ rejection, edge and level syswake modes, wake enable/disable propagation, chained peripheral fan-out, shared syswake status masking, suspend wake from each source, and removal/domain cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imgpdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-gpcv2.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-gpcv2.c

## Purpose
Implements the NXP i.MX GPCv2 interrupt mask/wakeup controller as a hierarchical irqchip above a parent GIC domain, mainly to control wake sources and per-core interrupt mask registers.

## Important APIs, Types, And Functions
`struct gpcv2_irqchip_data` stores the raw spinlock, MMIO base, wakeup source masks, saved IRQ masks, and selected wakeup CPU register offset. Important functions are `imx_gpcv2_irqchip_init()`, `imx_gpcv2_domain_alloc()`, `imx_gpcv2_irq_mask()`, `imx_gpcv2_irq_unmask()`, `imx_gpcv2_irq_set_wake()`, `gpcv2_wakeup_source_save()`, and `gpcv2_wakeup_source_restore()`.

## Control Flow
OF init requires a parent domain, matches the compatible to a 2-core or 4-core layout, maps registers, creates a 128-entry hierarchical domain, masks all per-core interrupts, selects CORE0 as default wake CPU, applies the GPR interrupt workaround, registers syscore suspend/resume, and clears OF populated state so the GPC power-domain driver can bind later. Child allocations copy the fwspec to the parent after installing the GPCv2 chip data.

## State And Persistence
Wakeup source masks are kept in `wakeup_sources[]`, where clearing a bit enables wake. Suspend saves current IMR registers and replaces them with wake masks; resume restores saved run-time masks. Normal mask/unmask updates the GPC IMR and then delegates to the parent IRQ chip.

## Dependencies And Integration Points
It depends on OF irq init, parent irqdomains, syscore ops, GIC parent callbacks, and compatibles `fsl,imx7d-gpc` and `fsl,imx8mq-gpc`. It integrates with the i.MX power-domain driver by clearing `OF_POPULATED` and resetting fwnode initialized state.

## Risks
Wake mask polarity is inverted and easy to regress. The hard-coded GPR interrupt workaround keeps IRQ 32 unmasked in run mode. The single global `imx_gpcv2_instance` means only one instance is supported by syscore save/restore. Parent translation rejects PPIs.

## Test Signals
Test boot with i.MX7D/i.MX8MQ DTs, hierarchy allocation under GIC, normal mask/unmask, wake-source programming across suspend/resume, GPR interrupt behavior, power-domain driver later binding, and invalid SPI numbers beyond 128.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-gpcv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-intmux.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-intmux.c

## Purpose
Implements the NXP i.MX INTMUX interrupt multiplexer, where each channel accepts 32 sources and emits one parent interrupt.

## Important APIs, Types, And Functions
`struct intmux_data` stores the MMIO base, IPG clock, channel count, lock, and per-channel `struct intmux_irqchip_data`. Per-channel data stores saved enable register, channel index, parent IRQ, and irqdomain. Important functions are `imx_intmux_probe()`, `imx_intmux_irq_handler()`, `imx_intmux_irq_map()`, `imx_intmux_irq_select()`, `imx_intmux_irq_mask()`, `imx_intmux_irq_unmask()`, runtime suspend, and runtime resume.

## Control Flow
Probe counts platform IRQs to determine channels, maps registers, enables the IPG clock, creates one 32-entry linear domain per channel using the same fwnode but a `select()` callback that chooses by channel index, disables all sources, chains each channel parent IRQ, then enables runtime PM. The chained handler reads `CHANIPR(channel)` and dispatches all pending source bits into that channel's domain.

## State And Persistence
Each channel enable register `CHANIER` is the main hardware state. Runtime suspend saves `CHANIER` for every channel and disables the IPG clock; resume re-enables the clock and restores saved enables. No pending state is persisted.

## Dependencies And Integration Points
It depends on platform IRQ resources, OF IRQ parsing, clocks, runtime PM, chained IRQs, and `fsl,imx-intmux`. The irqdomain `select()` logic integrates with `interrupts-extended` style lookups where the second cell is the channel index.

## Risks
Channel count comes from platform IRQ count and is limited to 8. The code creates multiple domains with the same fwnode, so selection by `param[1]` is essential. Error unwinding does not remove already-created domains in all partial failure paths, so probe failures after some channels are initialized deserve testing.

## Test Signals
Test all channel parent IRQs, source masking/unmasking, fwspec selection by channel, runtime PM suspend/resume restoring `CHANIER`, clock failure paths, and DTs with 1 to 8 channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-intmux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-irqsteer.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-irqsteer.c

## Purpose
Implements the i.MX IRQSTEER block, which steers many input interrupts through a smaller set of output interrupts, with optional channel-control support and runtime PM.

## Important APIs, Types, And Functions
`struct irqsteer_data` stores registers, IPG clock, output IRQs, register count, selected channel, domain, saved masks, and device-type quirks. Important functions are `imx_irqsteer_probe()`, `imx_irqsteer_irq_handler()`, `imx_irqsteer_irq_mask()`, `imx_irqsteer_irq_unmask()`, `imx_irqsteer_get_hwirq_base()`, `imx_irqsteer_save_regs()`, and `imx_irqsteer_restore_regs()`.

## Control Flow
Probe reads `fsl,num-irqs` and `fsl,channel`, maps registers, enables the clock, optionally writes `CHANCTRL`, creates a linear domain covering all sources, and chains one output IRQ per 64 input interrupts. Runtime dispatch determines which output fired, reads two 32-bit `CHANSTATUS` registers for that output range, and dispatches each pending source.

## State And Persistence
Mask state is held in the hardware `CHANMASK` register set and mirrored into `saved_reg[]` during PM. Suspend saves all mask registers and disables the IPG clock; resume re-enables the clock, rewrites `CHANCTRL` when supported, and restores masks. Bus lock/unlock uses runtime PM around IRQ chip register access.

## Dependencies And Integration Points
It depends on platform devices, OF properties, clocks, runtime PM, generic irqdomains, chained IRQs, and compatibles `fsl,imx-irqsteer` and `nxp,s32n79-irqsteer`. GPIO or peripheral child controllers can sit below this domain.

## Risks
The reverse register-index calculation is easy to break because hwirqs are mapped from the high register down. Output IRQ count is `DIV_ROUND_UP(num_irqs, 64)` and must not exceed 15. Some SoCs lack `CHANCTRL`, controlled by a quirk. Runtime PM must keep the clock enabled across mask/unmask access.

## Test Signals
Test source delivery across 32-bit register boundaries and 64-source output boundaries, channel-control and no-channel-control SoCs, runtime PM register access, suspend/resume state restoration, child GPIO irqchips, and invalid `fsl,num-irqs` or missing output IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-irqsteer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-mu-msi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-mu-msi.c

## Purpose
Uses the Freescale/NXP Messaging Unit as a small MSI parent controller, exposing four receive channels as MSI vectors for platform devices.

## Important APIs, Types, And Functions
`struct imx_mu_dcfg` describes MU register offsets and version-specific bit layouts. `struct imx_mu_msi` stores the register base, MSI write address, used-channel bitmap, lock, clock, and configuration. Important functions include `imx_mu_probe()`, `imx_mu_msi_domains_init()`, `imx_mu_msi_domain_irq_alloc()`, `imx_mu_msi_parent_compose_msg()`, `imx_mu_msi_irq_handler()`, `imx_mu_msi_parent_mask_irq()`, and runtime PM callbacks.

## Control Flow
IRQCHIP platform-driver matching selects one of the i.MX6SX, i.MX7ULP, or i.MX8ULP register layouts. Probe maps processor A registers, computes the processor B transmit register MSI address, attaches two power domains, creates a parent MSI irqdomain, enables runtime PM, and chains the MU receive IRQ. MSI allocation reserves one of four channels, installs the parent chip, and compose-message points writes at `processor-b-side + xTR + 4 * channel`. The handler reads receive status and dispatches each full receive register.

## State And Persistence
`used` tracks allocated channels in memory. Hardware state is receive interrupt enable bits in the MU receive control register and receive data registers consumed for ACK. Runtime suspend disables the clock; runtime resume re-enables it. Power-domain links keep both MU sides active while needed.

## Dependencies And Integration Points
It depends on IRQCHIP platform-driver macros, MSI parent ops, `irq-msi-lib`, clocks, runtime PM, named memory resources `processor-a-side` and `processor-b-side`, and named power domains. Compatibles are `fsl,imx7ulp-mu-msi`, `fsl,imx6sx-mu-msi`, and `fsl,imx8ulp-mu-msi`.

## Risks
Only four MSI vectors exist, so allocation pressure returns `-ENOSPC`. Register bit definitions differ between v1 and v2 MU blocks. The error path around power-domain links returns `-EINVAL` rather than original errors and must not leak attached domains. Affinity is unsupported.

## Test Signals
Test allocation/free of all four vectors, MSI message address/data contents, interrupt delivery and ACK by receive register read, runtime PM clock behavior, power-domain attach failures, all three compatible register layouts, and over-allocation returning `-ENOSPC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-mu-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic-tcu.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic-tcu.c

## Purpose
Implements the Ingenic JZ47xx/X1000 Timer Counter Unit interrupt controller, exposing timer channel interrupts through a regmap-backed generic irqchip and one or more parent IRQs.

## Important APIs, Types, And Functions
`struct ingenic_tcu` stores the regmap, domain, and up to three parent IRQs. `ingenic_tcu_irq_init()` creates the domain and generic chip. `ingenic_tcu_intc_cascade()` reads flag and mask registers and dispatches unmasked timer bits. Custom generic-chip callbacks handle TCU write-one-to-clear, mask, unmask, and mask-ack register semantics.

## Control Flow
OF init obtains the syscon regmap from the node, counts parent interrupts, creates a 32-entry domain, allocates one generic chip, programs disable/enable/ack registers, masks all channels by default, then registers the same cascade handler on every parent IRQ because different SoCs route subsets of timers differently.

## State And Persistence
The regmap and generic chip hold mask cache and hardware register access. All TCU IRQs are masked at init. No PM callbacks are present; wake handling is skipped with `IRQCHIP_SKIP_SET_WAKE` while `IRQCHIP_MASK_ON_SUSPEND` masks the lines on suspend.

## Dependencies And Integration Points
It depends on MFD/syscon regmap lookup, Ingenic TCU register definitions, OF IRQ parsing, generic irqchip, and compatibles `ingenic,jz4740-tcu`, `jz4725b-tcu`, `jz4760-tcu`, `jz4770-tcu`, and `x1000-tcu`.

## Risks
Multiple parent IRQs share one domain and handler; an incorrect DT parent list can drop channels. The custom callbacks update `mask_cache` with unusual polarity because TCU mask clear enables interrupts. Missing regmap access errors are not checked in the fast path.

## Test Signals
Test each compatible's parent IRQ topology, timer channel interrupt delivery, mask/unmask/ack behavior, all-IRQ masking at init, and invalid `interrupts` property counts greater than three.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic-tcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic.c

## Purpose
Implements the main Ingenic XBurst SoC interrupt controller for one-chip and two-chip variants, using generic irqchips and a shared cascade interrupt.

## Important APIs, Types, And Functions
`struct ingenic_intc_data` stores MMIO base, irqdomain, and chip count. `ingenic_intc_of_init()` maps the parent IRQ and register block, creates the domain, allocates generic chips, configures mask/unmask/wake callbacks, masks all IRQs, and requests the parent cascade IRQ. `intc_cascade()` reads each chip's pending register and dispatches set bits.

## Control Flow
The one-chip wrappers register 32 hwirqs for JZ4740/JZ4725B; two-chip wrappers register 64 hwirqs for JZ4760/JZ4770/JZ4775/JZ4780. Runtime handling iterates chips, reads `JZ_REG_INTC_PENDING`, and forwards each pending bit to the domain.

## State And Persistence
State is the private struct, domain, generic chip mask cache, and hardware mask registers. Wake-enabled masks are set for all 32 bits per chip, and `irq_gc_set_wake()` manages wake state. There is no explicit suspend/resume state beyond generic irqchip suspend behavior.

## Dependencies And Integration Points
It depends on OF mapping, generic irqchip, parent IRQ request, and Ingenic compatibles for one-chip and two-chip SoCs. It integrates with the arch interrupt path through a shared parent IRQ rather than `set_handle_irq()`.

## Risks
`request_irq()` passes NULL dev_id while handler data is set on the IRQ descriptor, so cleanup would be awkward if later added. All interrupts are configured as level handled; source-specific edge semantics must be handled elsewhere. Two-chip offset math must remain aligned to `CHIP_SIZE`.

## Test Signals
Test one-chip and two-chip DTs, pending dispatch from both chips, mask/unmask and wake callbacks, parent IRQ request failure logging, and hwirq-to-domain mapping around bit 31/32.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ixp4xx.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ixp4xx.c

## Purpose
Implements the Intel IXP4xx interrupt controller for 32-source and 64-source SoC variants, including the primary exception IRQ handler and a hierarchical irqdomain suitable for child GPIO irqchips.

## Important APIs, Types, And Functions
`struct ixp4xx_irq` stores MMIO base, variant flag, irqchip, and domain. Important functions are `ixp4xx_of_init_irq()`, `ixp4xx_irq_setup()`, `ixp4xx_handle_irq()`, `ixp4xx_irq_mask()`, `ixp4xx_irq_unmask()`, `ixp4xx_set_irq_type()`, and hierarchical domain translate/alloc callbacks.

## Control Flow
OF init maps the controller, detects whether the compatible has the upper 32 IRQ registers, routes sources to IRQ rather than FIQ, disables all inputs, creates a linear domain of 32 or 64 hwirqs, and installs `ixp4xx_handle_irq()`. Runtime handling reads `ICIP`, dispatches all low pending bits, then reads `ICIP2` and dispatches high bits on 64-source variants.

## State And Persistence
A single static `ixirq` represents the controller. Hardware mask state lives in ICMR/ICMR2; FIQ routing is disabled by writing ICLR/ICLR2. No PM callbacks or saved masks are present.

## Dependencies And Integration Points
It depends on ARM exception handling, OF mapping, hierarchical irqdomains, and compatibles `intel,ixp42x-interrupt`, `ixp43x`, `ixp45x`, and `ixp46x`. GPIO IRQ users can allocate below this domain.

## Risks
Only level-high interrupts are accepted. The controller is represented by one global instance. High-register handling must be correct for IXP43x/45x/46x, while 42x only has 32 sources. The TODO notes that some legacy consumers may not call set_type.

## Test Signals
Test 32-source and 64-source hardware, low/high register pending dispatch, mask/unmask for hwirqs below and above 32, level-high type enforcement, GPIO child irqchip integration, and boot-time primary handler installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ixp4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-jcore-aic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-jcore-aic.c

## Purpose
Implements the J-Core SoC AIC1/AIC2 local interrupt controller using a legacy irqdomain and a minimal irqchip.

## Important APIs, Types, And Functions
The file uses a single static `struct irq_chip jcore_aic`. `aic_irq_of_init()` allocates descriptors and creates a legacy domain. `jcore_aic_irqdomain_map()` installs `handle_jcore_irq()`, which chooses `handle_percpu_devid_irq()` for per-CPU requested IRQs and `handle_simple_irq()` otherwise. `noop()` satisfies mask/unmask requirements.

## Control Flow
OF init chooses a minimum hwirq range based on AIC1 or AIC2. AIC1 additionally maps per-CPU register resources and writes all priorities enabled to `JCORE_AIC1_INTPRI_REG`. It then allocates descriptors and creates a legacy domain covering the valid hwirq range.

## State And Persistence
There is no private state object. Hardware state is limited to AIC1 priority initialization. The irqchip has no real mask/unmask because masking is CPU-global rather than per-source.

## Dependencies And Integration Points
It depends on OF mapping, CPU iteration, legacy irqdomains, and compatibles `jcore,aic1` and `jcore,aic2`. It integrates with request-time IRQF_PERCPU state rather than knowing per-CPU sources at mapping time.

## Risks
No per-source masking means Linux cannot disable individual AIC sources through this chip. AIC1 mapping assumes one MMIO resource per present CPU. Legacy descriptor allocation must not collide with platform IRQ numbering.

## Test Signals
Test AIC1 priority programming for all present CPUs, AIC2 descriptor/domain creation, per-CPU and non-per-CPU request handling, descriptor range boundaries at 16/64/127, and missing per-CPU MMIO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-jcore-aic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-keystone.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-keystone.c

## Purpose
Implements the TI Keystone IRQ controller, which reads and clears source bits from a syscon register and exposes 28 child IRQs.

## Important APIs, Types, And Functions
`struct keystone_irq_device` stores device pointer, irqchip, software mask, parent IRQ, child domain, syscon regmap, offset, and workaround lock. Key functions are `keystone_irq_probe()`, `keystone_irq_handler()`, `keystone_irq_map()`, `keystone_irq_setmask()`, `keystone_irq_unmask()`, and `keystone_irq_remove()`.

## Control Flow
Probe resolves `ti,syscon-dev` with one argument for the register offset, gets the parent IRQ, initializes all child sources masked, creates a 28-entry linear domain, requests the parent IRQ, and clears all source bits. Runtime handler reads pending bits, writes the same value back to clear them, shifts off reserved low bits, applies the software mask, and dispatches each active source under `wa_lock`.

## State And Persistence
The software `mask` is the primary mask state; hardware pending state is cleared by writing the syscon register. There is no PM state. Removal frees the parent IRQ, disposes child mappings, and removes the domain.

## Dependencies And Integration Points
It depends on platform probing, OF, syscon/regmap, linear irqdomains, and compatible `ti,keystone-irq`. It integrates with device-control registers rather than a dedicated MMIO mapping.

## Risks
Mask/unmask only update software, so pending bits are still read and cleared for masked sources. The source ID bits start at bit 4; off-by-one shifts would deliver wrong hwirqs. Dispatch under `wa_lock` suggests a hardware or ordering workaround; removing it may reintroduce races.

## Test Signals
Test all 28 hwirqs, masked pending bits not dispatched, pending clear writeback, syscon lookup failure, parent IRQ request failure, remove cleanup, and interrupt storms with multiple simultaneous sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-keystone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-lan966x-oic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-lan966x-oic.c

## Purpose
Implements the Microchip LAN966x outbound interrupt controller, mapping up to 86 source interrupts to one destination interrupt and exposing them through domain generic chips.

## Important APIs, Types, And Functions
`struct lan966x_oic_data` stores MMIO base and parent IRQ. `struct lan966x_oic_chip_regs` describes each 32-source register bank. Important functions include `lan966x_oic_probe()`, `lan966x_oic_chip_init()`, `lan966x_oic_irq_startup()`, `lan966x_oic_irq_shutdown()`, `lan966x_oic_irq_handler()`, and `lan966x_oic_irq_handler_domain()`.

## Control Flow
Probe maps registers, gets the parent IRQ, instantiates an irqdomain with destroyable generic chips, and its domain init chains the parent IRQ. Each generic-chip bank sets enable, disable, ack, map, and ident register offsets. Startup maps the source to destination 0, acknowledges sticky state, and unmasks. Shutdown masks and unmaps. The chained handler checks ident registers for banks 0, 32, and 64 and dispatches set bits.

## State And Persistence
Per-source mapping state lives in the destination map registers and is changed at IRQ startup/shutdown. Enable state is in atomic set/clear registers; sticky status is acknowledged through sticky registers. No explicit PM save/restore exists.

## Dependencies And Integration Points
It depends on platform devices, OF compatible `microchip,lan966x-oic`, `devm_irq_domain_instantiate()`, domain generic-chip init/exit callbacks, and chained IRQ support. Child consumers use the irqdomain as a normal interrupt controller.

## Risks
Only level-high flow type is supported. The third bank has only 22 valid IRQs although the generic chip handles 32-bit registers, so domain size and hwirq max must stay at 86. Startup/shutdown map updates must be serialized under the generic-chip lock.

## Test Signals
Test hwirqs across all three banks including 85, startup mapping, shutdown unmapping, sticky ACK, level-high type enforcement, parent chained dispatch with multiple banks pending, and devm domain teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-lan966x-oic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-avec.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-avec.c

## Purpose
Implements the LoongArch Advanced Vector Interrupt Controller, an MSI-capable vector allocator and dispatcher layered below PCH MSI initialization.

## Important APIs, Types, And Functions
`struct avecintc_chip` stores the lock, fwnode, domain, vector matrix, and MSI base address. `struct avecintc_data` tracks each IRQ's current and previous CPU/vector plus migration state. Important functions are `avecintc_init()`, `avecintc_domain_alloc()`, `avecintc_alloc_vector()`, `avecintc_set_affinity()`, `complete_irq_moving()`, `avecintc_irq_dispatch()`, `avecintc_compose_msi_msg()`, and `avecintc_acpi_init()`.

## Control Flow
ACPI initialization creates a named fwnode and tree domain, maps the AVEC CPU interrupt from the parent CPUINTC, initializes an IRQ matrix with legacy vectors reserved, chains the AVEC dispatcher, registers CPU hotplug callbacks, enables AVEC in IOCSR, then parses the MSI PIC MADT entry to set the MSI base and initialize PCH MSI over the AVEC domain. Allocation reserves a vector on an online CPU, stores the descriptor in per-CPU `irq_map`, and installs an edge IRQ. Dispatch repeatedly reads CSR IRR until invalid and handles the descriptor mapped to each vector.

## State And Persistence
Per-IRQ allocation state persists in `avecintc_data`; per-CPU vector-to-desc state persists in `irq_map`. SMP migration keeps old vector state in per-CPU pending lists until `complete_irq_moving()` observes that the old ISR bit has cleared, then frees the old vector in the matrix.

## Dependencies And Integration Points
It depends on LoongArch CSRs/IOCSR, IRQ matrix allocation, cpuhotplug, SMP IPI callbacks for `ACTION_CLEAR_VECTOR`, MSI library domain selection, ACPI MADT MSI PIC parsing, and `pch_msi_acpi_init_avec()`. It is invoked from the LoongArch CPU interrupt controller when `cpu_has_avecint` is true.

## Risks
Vector migration is subtle: freeing the old vector before hardware clears it can misdeliver interrupts. The global `intersect_mask` is protected by the AVEC lock and must not be used locklessly. MSI message composition packs CPU and vector into an address, so bit masks and `AVEC_MSG_OFFSET` must match hardware.

## Test Signals
Test MSI allocation/free, vector exhaustion, interrupt delivery on all online CPUs, affinity changes during load, CPU hotplug online/offline, `complete_irq_moving()` IPI flow, PCH MSI initialization through ACPI, and unexpected-vector warning paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-avec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-cpu.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-cpu.c

## Purpose
Implements the root LoongArch CPU interrupt controller and ACPI/OF cascade discovery for LIOINTC, EIOINTC, AVECINTC, LPC, PCH PIC, and PCH MSI domains.

## Important APIs, Types, And Functions
Global `irq_domain` is the CPUINTC domain and `cpuintc_handle` is its fwnode. `cpu_irq_controller` masks and unmasks CPU interrupt bits in CSR ECFG. Important functions are `handle_cpu_irq()`, `loongarch_cpu_intc_map()`, `cpuintc_of_init()`, `cpuintc_acpi_init()`, `lpic_get_gsi_domain_id()`, `lpic_gsi_to_irq()`, and `acpi_cascade_irqdomain_init()`.

## Control Flow
OF init creates a linear domain over `EXCCODE_INT_NUM`, installs `handle_cpu_irq`, and returns. ACPI init masks CPU interrupt bits, creates a named fwnode domain, installs the handler, configures ACPI LPIC GSI domain routing and fallback translation, then parses MADT LIO PIC and EIO PIC entries and optionally initializes AVEC. Runtime CPU dispatch reads CSR ESTAT interrupt pending bits and forwards each set bit to the CPU domain.

## State And Persistence
State is minimal: root domain and fwnode handle plus CSR enable bits controlled by mask/unmask callbacks. ACPI GSI routing relies on global handles maintained by downstream Loongson irqchip drivers. No PM callbacks are present here.

## Dependencies And Integration Points
It depends on LoongArch CSR helpers, setup globals, ACPI MADT parsing, OF compatible `loongson,cpu-interrupt-controller`, and downstream functions from `irq-loongson.h`. It is the parent domain for platform interrupt controllers and optional AVEC MSI routing.

## Risks
The GSI domain selection logic depends on global handles being initialized by other drivers. CPU interrupt hwirq masking directly updates CSR ECFG, so wrong hwirq values can mask CPU exception inputs. ACPI init is idempotent only through the `irq_domain` guard.

## Test Signals
Test OF and ACPI boot, CPU timer/IPI interrupt delivery, ECFG mask/unmask, MADT LIO/EIO parsing, ACPI GSI translation to LPC/PCH/PIC domains, AVEC initialization when supported, and fallback GSI registration for PCH IRQ ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-eiointc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-eiointc.c

## Purpose
Implements the Loongson Extended I/O Interrupt Controller, a 128/256-vector interrupt controller with CPU/node routing, virtualization support, ACPI/OF initialization, and cascaded PCH PIC/MSI setup.

## Important APIs, Types, And Functions
`struct eiointc_priv` stores node identity, vector count, node and CPU span masks, fwnode/domain, flags, parent hwirq, and per-route dispatch metadata. Key functions are `eiointc_init()`, `eiointc_router_init()`, `eiointc_irq_dispatch()`, `eiointc_domain_alloc()`, `eiointc_set_irq_affinity()`, `eiointc_acpi_init()`, `eiointc_of_init()`, and ACPI cascade parsers for PCH PIC/MSI.

## Control Flow
Initialization builds node and CPU span masks from MADT node maps or all possible CPUs, creates a linear domain for the vector count, detects KVM virtual EXTIOI CPU-encode support, stores the instance globally, optionally enables multi-IP routing, chains the parent CPU interrupt(s), programs routing and enable registers through `eiointc_router_init(0)`, and registers syscore/cpuhotplug callbacks on the first PIC. Dispatch reads ISR register ranges assigned to the parent IP, clears pending bits, and forwards vectors through the domain.

## State And Persistence
Global `eiointc_priv[]` and `nr_pics` persist all instances. Hardware state includes nodemap, IP map, route, enable, and bounce registers. Syscore resume re-runs router initialization. SMP affinity updates mask a vector, rewrite CPU/node route, then unmask it; virtual CPU-encode mode uses a different route register format.

## Dependencies And Integration Points
It depends on LoongArch IOCSR/CSR helpers, KVM paravirtual feature detection, CPU topology constants, cpuhotplug, syscore ops, ACPI MADT EIO/BIO/MSI records, OF compatibles `loongson,ls2k0500-eiointc` and `loongson,ls2k2000-eiointc`, and downstream PCH PIC/MSI initialization from `irq-loongson.h`.

## Risks
Routing is complex across physical nodes, virtual EXTIOI, CPU encode, and multi-IP hypervisor mode. Incorrect node maps can make `eiointc_index()` fail on CPU hotplug. The code assumes vector counts divisible by register sizes and route groups. Affinity updates must preserve masking around route changes to avoid delivery to stale CPUs.

## Test Signals
Test OF LS2K0500 with 128 vectors and LS2K2000 with 256 vectors, ACPI multi-node EIO PICs, CPU hotplug router reinit, interrupt affinity changes, virtual EXTIOI CPU-encode guests, multi-IP hypervisor routing, PCH PIC/MSI cascade initialization, syscore resume, and spurious dispatch when ISR ranges are empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-eiointc.c -->
