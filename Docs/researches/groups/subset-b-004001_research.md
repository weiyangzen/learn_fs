# subset-b-004001 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/tegra-smmu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/tegra-smmu.c

Purpose: Implements the NVIDIA Tegra memory-controller SMMU as a Linux IOMMU provider. It owns ASID allocation, page-directory/page-table programming, SWGROUP/client enable bits, device-tree fwspec parsing, IOMMU group creation, debugfs visibility, and registration of `tegra_smmu_ops`.

Important APIs/types/functions: `struct tegra_smmu`, `struct tegra_smmu_as`, `struct tegra_smmu_group`, `tegra_smmu_probe()`, `tegra_smmu_remove()`, `tegra_smmu_attach_dev()`, `tegra_smmu_identity_attach()`, `tegra_smmu_map()`, `tegra_smmu_unmap()`, `tegra_smmu_iova_to_phys()`, `tegra_smmu_probe_device()`, `tegra_smmu_of_xlate()`, and debugfs show handlers. Register helpers wrap `readl`/`writel`; page table helpers allocate second-level tables and flush PTC/TLB state.

Control flow: Probe initializes masks from SoC capabilities, enables PTC/TLB/SMMU hardware, enables the Tegra AHB SMMU path, and registers an `iommu_device`. Device probe walks `iommus` phandles, stores the SMMU in `dev_iommu_priv`, and adds SWGROUP IDs. Attaching a translated domain prepares the address space once, maps the page directory for DMA, allocates an ASID, loads PTB registers, then enables each SWGROUP/client. Identity attach disables old SWGROUPs and decrements the AS use count.

State and persistence: Runtime state is in hardware registers, an ASID bitmap, group list, and per-domain page directory/table arrays. Page-table lifetime is reference-counted per PDE on unmap, but `tegra_smmu_domain_free()` still has a TODO for freeing page directory and page tables, making domain teardown a risk area.

Dependencies/integration: Integrates with `linux/iommu`, `soc/tegra/mc`, `soc/tegra/ahb`, OF, PCI grouping, DMA mapping, `iommu-pages`, sysfs, and optional debugfs. It assumes Tegra MC SoC tables provide SWGROUP/client register metadata.

Risks and test signals: Test attach/detach across multiple SWGROUP IDs, ASID exhaustion, 64-bit DMA address rejection, concurrent map allocation under the spinlock, identity default-domain behavior, debugfs output, and repeated domain allocate/free cycles to expose the unfinished cleanup path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/tegra-smmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/virtio-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/virtio-iommu.c

Purpose: Provides the paravirtualized virtio IOMMU driver. It translates Linux IOMMU domain operations into virtqueue requests, keeps a software shadow of mappings, probes endpoint reserved regions, supports identity/bypass domains, and handles virtio fault events.

Important APIs/types/functions: `struct viommu_dev`, `struct viommu_domain`, `struct viommu_endpoint`, `struct viommu_mapping`, `viommu_send_req_sync()`, `viommu_add_req()`, `viommu_replay_mappings()`, `viommu_probe_endpoint()`, `viommu_attach_dev()`, `viommu_map_pages()`, `viommu_unmap_pages()`, `viommu_get_resv_regions()`, `viommu_probe()`, and `viommu_remove()`.

Control flow: Probe verifies required virtio features, initializes request/event virtqueues, reads config ranges and page masks, reserves a bypass-domain ID when supported, fills event buffers, and registers the IOMMU device against the parent bus. Device probe resolves the virtio IOMMU by fwnode, allocates endpoint state, and optionally sends a PROBE request to populate reserved memory. Domain allocation gets an ID from `ida`, records geometry/map flags, and initializes an interval tree.

State and persistence: Mapping state persists in `vdomain->mappings`, an interval tree protected by `mappings_lock`. MAP/UNMAP requests are queued and synchronized by `iotlb_sync*`, while attach/probe/detach are synchronous. Domains with zero endpoints retain their shadow mappings so `viommu_replay_mappings()` can recreate device state on reattach.

Dependencies/integration: Integrates with virtio config/queues, Linux IOMMU core, OF fwspec IDs, PCI/generic IOMMU grouping, `dma-iommu` reserved regions, MSI reservation helpers, interval trees, and module virtio-driver registration.

Risks and test signals: Exercise queue-full retry, zero-length virtqueue completions, map flag validation, unmap attempts that split an existing MAP range, attach failure with `nr_endpoints` accounting, endpoint PROBE overflow checks, bypass identity behavior, event queue refilling, and removal while requests/events are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/virtio-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ipack/Kconfig

Purpose: Defines the top-level `IPACK_BUS` menu option and includes carrier/device submenus when the IndustryPack framework is enabled.

Important APIs/types/functions: `menuconfig IPACK_BUS`, dependency `HAS_IOMEM`, and `source` statements for `drivers/ipack/carriers/Kconfig` and `drivers/ipack/devices/Kconfig`.

Control flow: Kconfig exposes a tristate bus framework. If selected, the nested carrier and device driver options become visible. If disabled, neither TPCI200 carrier nor IP-OCTAL device config entries are reachable through this subtree.

State and persistence: No runtime state. Build configuration persists through `.config`, influencing whether `ipack.o` and child directories are compiled.

Dependencies/integration: It is the configuration gate for the IPACK bus core and any module drivers consuming `<linux/ipack.h>`.

Risks and test signals: Confirm `HAS_IOMEM=n` hides the option; `IPACK_BUS=m` permits modular carrier/device builds; and disabling `IPACK_BUS` removes child driver symbols from configuration resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ipack/Makefile

Purpose: Builds the IPACK bus core and descends into IPACK device and carrier subdirectories.

Important APIs/types/functions: `obj-$(CONFIG_IPACK_BUS) += ipack.o`, `obj-y += devices/`, and `obj-y += carriers/`.

Control flow: The core object is conditional on `CONFIG_IPACK_BUS`. The subdirectories are always visited, but their own Makefiles gate actual objects by config symbols.

State and persistence: No runtime state. The file participates only in Kbuild object selection and module composition.

Dependencies/integration: Connects top-level driver build traversal to the IPACK core, TPCI200 carrier, and IP-OCTAL device modules.

Risks and test signals: Build with `IPACK_BUS=n/m/y`, `BOARD_TPCI200=m`, and `SERIAL_IPOCTAL=m` to ensure subdirectory traversal and object selection remain consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/carriers/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ipack/carriers/Kconfig

Purpose: Adds the TEWS TPCI-200 IndustryPack PCI carrier board configuration option.

Important APIs/types/functions: `config BOARD_TPCI200`, `tristate`, dependencies `IPACK_BUS` and `PCI`, and default `n`.

Control flow: The option is visible only when the IPACK bus and PCI support are available. Selecting it compiles the TPCI200 carrier driver through the carrier Makefile.

State and persistence: No runtime state. The selected symbol controls whether `tpci200.o` is built.

Dependencies/integration: Bridges PCI carrier support to the IPACK bus core and the child device enumeration path used by IPACK modules.

Risks and test signals: Validate menu visibility with `PCI=n`, modular builds with `IPACK_BUS=m`, and dependency closure so `tpci200.o` cannot build without bus core APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/carriers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/carriers/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ipack/carriers/Makefile

Purpose: Selects the TPCI200 carrier object for the IPACK carrier directory.

Important APIs/types/functions: `obj-$(CONFIG_BOARD_TPCI200) += tpci200.o`.

Control flow: Kbuild emits `tpci200.o` only when the carrier config symbol is enabled as built-in or module.

State and persistence: No runtime state; build artifact selection only.

Dependencies/integration: Hooks `drivers/ipack/carriers/tpci200.c` into the kernel/module build controlled by `BOARD_TPCI200`.

Risks and test signals: Verify `BOARD_TPCI200=m` produces a loadable `tpci200` module and `BOARD_TPCI200=y` links it into the kernel image without missing IPACK/PCI symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/carriers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/carriers/tpci200.c -->
# sources/distributed-fs/ceph-client/drivers/ipack/carriers/tpci200.c

Purpose: Implements the TEWS TPCI-200 PCI carrier. It maps PCI BAR windows into IPACK slot regions, registers an IPACK bus with four slots, creates child `ipack_device`s, and dispatches carrier interrupts to per-slot handlers.

Important APIs/types/functions: `tpci200_pci_probe()`, `tpci200_register()`, `tpci200_install()`, `tpci200_create_device()`, `tpci200_request_irq()`, `tpci200_free_irq()`, `tpci200_interrupt()`, `tpci200_bus_ops`, and the PCI driver/id table.

Control flow: PCI probe allocates board/info state, maps configuration memory, sets PLX descriptors to preserve big-endian IP module access, requests/maps interface and slot BARs, registers the shared PCI IRQ, registers an IPACK bus, and creates four child devices. Child creation fills each IPACK region from carrier base plus slot interval, then calls `ipack_device_init()` and `ipack_device_add()`. Interrupt handling reads the carrier status register, checks slot bits, and invokes each registered slot handler through an RCU-protected pointer.

State and persistence: Board state includes PCI resources, mapped control registers, slot array, a mutex, a register spinlock, and per-space physical bases. Slot IRQ handlers are installed under the mutex and published with RCU; removal unregisters the IPACK bus, frees the PCI IRQ, unmaps BARs, releases regions, and drops the PCI ref.

Dependencies/integration: Uses PCI, IPACK bus APIs, MMIO accessors, shared IRQ handling, RCU, mutex/spinlock protection, and constants from `tpci200.h`.

Risks and test signals: Test probe unwind at each PCI resource step, concurrent interrupt/free_irq behavior, absent slot handler disabling, clock-rate toggles, timeout/error status helpers, four-slot child enumeration, hot-unplug, and whether failures from individual `tpci200_create_device()` calls should be surfaced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/carriers/tpci200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/carriers/tpci200.h -->
# sources/distributed-fs/ceph-client/drivers/ipack/carriers/tpci200.h

Purpose: Defines TPCI200 hardware constants, BAR layout, register structures, interrupt/status bits, and private carrier data structures used by `tpci200.c`.

Important APIs/types/functions: `struct tpci200_regs`, `struct slot_irq`, `struct tpci200_slot`, `struct tpci200_infos`, `struct tpci200_board`, BAR constants, slot region offsets/sizes, control bits, status bits, PCI IDs, and PLX descriptor offsets.

Control flow: This header does not execute logic, but its layout drives all MMIO operations in the carrier. `tpci200_regs` maps revision/control/reset/status registers; slot space constants determine the child `ipack_device` memory windows.

State and persistence: Persistent runtime state is represented in `tpci200_board`: board number, mutex, register spinlock, slot array, info block, and physical bases for IPACK spaces. `slot_irq` stores a holder device and callback used by interrupt dispatch.

Dependencies/integration: Includes PCI, spinlock, IO, limits, byte-swap, and IPACK definitions. Must match TPCI200/PLX hardware register layout exactly.

Risks and test signals: Validate struct packing and endian-safe MMIO access on supported architectures, BAR indexes against hardware docs, status/control bit definitions, slot interval math, and that comments about mutex protection match the actual `regs_lock` usage in the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/carriers/tpci200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ipack/devices/Kconfig

Purpose: Defines the IP-OCTAL serial device driver option for IndustryPack buses.

Important APIs/types/functions: `config SERIAL_IPOCTAL`, `tristate`, dependencies `IPACK_BUS && TTY`, and default `n`.

Control flow: The option is available only when the IPACK bus core and TTY subsystem are enabled. Selecting it causes the device Makefile to compile `ipoctal.o`.

State and persistence: No runtime state. The selected symbol controls module/built-in availability of the IP-OCTAL TTY driver.

Dependencies/integration: Connects IPACK device enumeration to the Linux TTY serial stack.

Risks and test signals: Test configuration combinations for `IPACK_BUS=m`, `TTY=n`, and module builds to ensure no unresolved TTY or IPACK symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ipack/devices/Makefile

Purpose: Selects the IP-OCTAL object in the IPACK devices directory.

Important APIs/types/functions: `obj-$(CONFIG_SERIAL_IPOCTAL) += ipoctal.o`.

Control flow: Kbuild emits the IP-OCTAL driver only when `SERIAL_IPOCTAL` is enabled.

State and persistence: No runtime state; build selection only.

Dependencies/integration: Hooks `ipoctal.c` into the kernel/module build under the TTY/IPACK config gate.

Risks and test signals: Verify modular and built-in builds, especially with carrier drivers modular, so the IPACK driver registration symbols are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/ipoctal.c -->
# sources/distributed-fs/ceph-client/drivers/ipack/devices/ipoctal.c

Purpose: Implements the GE/SBS IP-OCTAL 232/422/485 IndustryPack serial board as eight dynamic raw TTY ports backed by SCC2698 DUART registers.

Important APIs/types/functions: `struct ipoctal`, `struct ipoctal_channel`, `ipoctal_probe()`, `ipoctal_inst_slot()`, `ipoctal_irq_handler()`, `ipoctal_irq_rx()`, `ipoctal_irq_tx()`, `ipoctal_write_tty()`, `ipoctal_set_termios()`, `ipoctal_hangup()`, `ipoctal_remove()`, `tty_operations ipoctal_fops`, and the IPACK device ID table.

Control flow: IPACK probe allocates board state, maps IO/INT/MEM8 spaces, resets each channel, programs default 9600 8N1 settings and block interrupt masks, allocates/registers a TTY driver, registers each channel device, and requests the carrier slot IRQ. The IRQ handler acknowledges the IPACK interrupt, scans all eight channels, drains RX FIFO into tty flip buffers with error flags, and pushes one TX byte per interrupt from the xmit buffer.

State and persistence: Per-channel state tracks stats, TX ring counters, tty port, register pointers, board ID, interrupt masks, and RX enable state. Carrier lifetime is pinned during tty install/cleanup through `ipack_get_carrier()` and `ipack_put_carrier()`. Removal frees the slot IRQ, unregisters TTY devices/driver, frees xmit buffers, and releases state.

Dependencies/integration: Depends on IPACK bus operations, TTY core, serial termios, `scc2698.h`, MMIO mapping, interrupt callbacks, and board IDs from IPACK headers.

Risks and test signals: Test all three board variants, half-duplex RS-485 RTS/RX transitions, termios changes while open, TX ring wrap/full behavior, RX error statistics, partial TTY registration failure cleanup, carrier removal with open ports, and the `i <= PAGE_SIZE - nb_bytes` copy condition near buffer-full boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/ipoctal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/ipoctal.h -->
# sources/distributed-fs/ceph-client/drivers/ipack/devices/ipoctal.h

Purpose: Provides shared IP-OCTAL constants and statistics structure for the serial driver.

Important APIs/types/functions: `NR_CHANNELS`, `IPOCTAL_MAX_BOARDS`, `MAX_DEVICES`, and `struct ipoctal_stats` with TX/RX/error counters.

Control flow: No executable flow. `ipoctal.c` uses the constants for TTY allocation and array sizing and uses `ipoctal_stats` for `TIOCGICOUNT` reporting.

State and persistence: `struct ipoctal_stats` is per-channel runtime state reset on close/free and incremented from IRQ paths.

Dependencies/integration: Header is local to the IP-OCTAL driver and complements SCC2698 register definitions.

Risks and test signals: Confirm the eight-channel constant matches board hardware, `MAX_DEVICES` aligns with tty minor allocation assumptions, and stats increments are safe under interrupt/TTY access patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/ipoctal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/scc2698.h -->
# sources/distributed-fs/ceph-client/drivers/ipack/devices/scc2698.h

Purpose: Describes SCC2698 DUART channel/block register layouts and bit definitions used by the IP-OCTAL driver.

Important APIs/types/functions: `union scc2698_channel`, `union scc2698_block`, MR1/MR2/CR/SR/ACR/CSR/OPCR/IMR/ISR bit macros, baud-rate selector macros, and interrupt acknowledge offsets `ACK_INT_REQ0/1`.

Control flow: No executable logic. The unions overlay read/write interpretations of the same byte-spaced MMIO registers; `ipoctal.c` writes MR/CSR/CR/IMR/OPCR and reads SR/RHR/ISR through these definitions.

State and persistence: Hardware state controlled via these bits includes RX/TX enable, mode-register pointer reset, parity/character/stop-bit settings, FIFO status, error flags, block interrupt masks, baud-rate generator selection, and RTS output modes.

Dependencies/integration: Local hardware contract for SCC2698 on IP-OCTAL boards. Correct `__packed` layout and offset padding are required for MMIO correctness.

Risks and test signals: Validate all register offsets against the SCC2698/IP-OCTAL documentation, supported baud encoding, error-bit interpretation, block/channel pointer arithmetic, and the reset sequence using `CR_CMD_RESET_MR` before mode-register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/devices/scc2698.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/ipack.c -->
# sources/distributed-fs/ceph-client/drivers/ipack/ipack.c

Purpose: Implements the Linux IndustryPack bus core. It registers the `ipack` bus type, matches devices by ID ROM metadata, exposes sysfs/modalias data, registers carrier buses and IPACK drivers, initializes devices, and parses ID PROM formats.

Important APIs/types/functions: `ipack_bus_register()`, `ipack_bus_unregister()`, `ipack_driver_register()`, `ipack_device_init()`, `ipack_device_add()`, `ipack_device_del()`, `ipack_device_read_id()`, `ipack_parse_id1()`, `ipack_parse_id2()`, `ipack_match_id()`, `ipack_bus_type`, and exported get/put helpers.

Control flow: Bus init registers `ipack_bus_type`. Carriers allocate a bus number, create `ipack_device`s, and call `ipack_device_init()`. Device init names the device, initializes it, forces 8 MHz for ID reads, resets timeouts, maps ID space, detects format 1 or VITA 4 format 2 PROMs, copies the ID bytes, validates CRC, and optionally switches to 32 MHz. Driver match compares format/vendor/device against the driver's ID table.

State and persistence: Global bus numbers are allocated through `ida`. Device state persists in embedded `struct device`, copied ID buffer, parsed ID fields, speed flags, CRC status, regions, and carrier bus pointer. Device release frees the copied ID then calls the carrier-provided release callback.

Dependencies/integration: Depends on Linux driver core, IDA, MMIO `ioremap`/`ioread`, IPACK public structs/macros, module aliases, and carrier-provided bus operations.

Risks and test signals: Test malformed/short ID PROMs, CRC mismatch warnings, format 1/2 modaliases, release callback correctness, bus unregister while children exist, clock-rate failures during init, and the `modalias_show()` string spelling versus uevent modalias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ipack/ipack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/irqchip/Kconfig

Purpose: Provides the central IRQ chip configuration menu for many architecture and SoC interrupt controllers.

Important APIs/types/functions: `config IRQCHIP`, GIC/ITS/MSI options, Armada/Alpine/AL FIC/Aspeed/ACLINT/Apple/Exynos symbols, dependency and `select` relationships for `IRQ_DOMAIN`, `IRQ_DOMAIN_HIERARCHY`, `GENERIC_MSI_IRQ`, `IRQ_MSI_LIB`, `GENERIC_IRQ_CHIP`, and architecture gates.

Control flow: Kconfig symbol selection determines which irqchip drivers are built and which generic IRQ/MSI capabilities are enabled. Several options are hidden bools selected by architecture code; others are user-visible for compile-test or module-capable drivers.

State and persistence: No runtime state. The file persists build-time capability decisions in `.config`, which directly affect early boot interrupt-controller availability.

Dependencies/integration: Integrates irqchip drivers with architecture support, OF/ACPI interrupt discovery, PCI MSI, SMP IPI, mailbox/MFD/regmap helpers, and virtualization-related GIC features.

Risks and test signals: Run Kconfig dependency checks for cross-architecture compile tests, ensure selected drivers pull required generic IRQ/MSI libraries, and verify user-visible tristate entries do not select unavailable architecture-only APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/irqchip/Makefile

Purpose: Maps IRQ chip Kconfig symbols to build objects.

Important APIs/types/functions: Object entries for core `irqchip.o`, AL FIC, Alpine MSI, ATH79, Exynos combiner, Armada MPIC, Aspeed controllers, RISC-V ACLINT, Apple AIC, GIC variants, Loongson, Qualcomm, STM32, TI, and many other controllers.

Control flow: Kbuild includes each object according to its `CONFIG_*` symbol. Some symbols build multiple objects, such as ARM GIC common/variant files and ARM GIC v5 components.

State and persistence: No runtime state; it controls build artifact inclusion and module linkage.

Dependencies/integration: Couples the Kconfig menu to implementation files and architecture-specific early init registration via `IRQCHIP_DECLARE`.

Risks and test signals: Build-test important symbol combinations, especially entries with line continuations and MSI library dependencies; ensure object names match source files and removed/renamed drivers are not left referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/alphascale_asm9260-icoll.h -->
# sources/distributed-fs/ceph-client/drivers/irqchip/alphascale_asm9260-icoll.h

Purpose: Defines register offsets and bitfields for the AlphaScale ASM9260 interrupt collector.

Important APIs/types/functions: `ASM9260_NUM_IRQS`, vector/level-ack/control/status/raw/interrupt/clear/undef-vector offsets, enable/priority/software interrupt bits, per-interrupt shift helpers, and set/clear/toggle register-layout notes.

Control flow: No code executes here. The definitions are consumed by the ASM9260 ICOLL driver to program enable bits, priorities, raw diagnostics, vector base, and interrupt completion.

State and persistence: Hardware state represented includes interrupt enable, priority, softirq generation, IRQ nesting/read-side-effect mode, current vector, raw interrupt lines, clear bits, and level acknowledge state.

Dependencies/integration: Assumes Linux `BIT()` macro availability from including code. It documents special register alias offsets and ICOLL semantics for ARM exception vector handling.

Risks and test signals: Validate `ASM9260_HW_ICOLL_CLEARn()` uses the expected set-register offset from including context, confirm priority changes are not applied while enabled, and test vector/level ack sequencing to avoid races when nested interrupts are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/alphascale_asm9260-icoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/exynos-combiner.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/exynos-combiner.c

Purpose: Implements the Samsung Exynos IRQ combiner, a cascaded controller that groups eight interrupt sources per combiner input and forwards them to parent IRQs.

Important APIs/types/functions: `struct combiner_chip_data`, `combiner_mask_irq()`, `combiner_unmask_irq()`, `combiner_handle_cascade_irq()`, `combiner_irq_domain_xlate()`, `combiner_irq_domain_map()`, `combiner_init_one()`, `combiner_of_init()`, and PM syscore suspend/resume hooks.

Control flow: OF init maps registers, reads optional `samsung,combiner-nr`, allocates per-combiner state, creates a linear IRQ domain, parses each parent IRQ, disables all group bits, and installs a chained handler. The chained handler reads status, masks to the current 8-source group, handles the first pending hwirq via the domain, and exits the parent chain.

State and persistence: Global state includes `combiner_data`, `combiner_irq_domain`, `max_nr`, and per-combiner base/mask/parent fields. Under `CONFIG_PM`, enabled bits are saved before suspend and restored after clearing all group bits on resume.

Dependencies/integration: Uses OF address/IRQ parsing, irqdomain, chained IRQ helpers, syscore PM, and generic level handlers.

Risks and test signals: Test multiple pending bits in one cascade, missing parent IRQ mappings, `combiner-nr` sizing, suspend/resume restore, affinity delegation to parent irqchip, and whether only servicing `__ffs(status)` per parent interrupt is sufficient on all hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/exynos-combiner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aclint-sswi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aclint-sswi.c

Purpose: Implements RISC-V ACLINT S-mode software interrupt support as an IPI provider for compatible MIPS P8700, Nuclei UX900, and T-HEAD C900 variants.

Important APIs/types/functions: `sswi_ipi_virq`, per-CPU `sswi_cpu_regs`, `aclint_sswi_ipi_send()`, `aclint_sswi_ipi_handle()`, `aclint_sswi_parse_irq()`, `aclint_sswi_probe()`, CPU hotplug callbacks, generic/T-HEAD probe wrappers, and `IRQCHIP_DECLARE` entries.

Control flow: Probe maps the SSWI MMIO region, parses each interrupt context to associate parent hart IDs and hart indexes with per-CPU set/clear registers, creates a mapping for `RV_IRQ_SOFT` in the RISC-V INTC domain, creates muxed IPIs, chains the soft IRQ handler, installs CPU hotplug callbacks, and publishes the virtual IPI range.

State and persistence: Persistent state is the global SSWI virq and per-CPU MMIO register pointers. CPU online/offline paths enable or disable the percpu IRQ and clear pending software interrupts.

Dependencies/integration: Uses OF IRQ parsing, RISC-V hart ID/index helpers, SBI/vendor IDs, CSR operations, `ipi_mux`, percpu IRQs, CPU hotplug, and `riscv_ipi_set_virq_range()`.

Risks and test signals: Test multiple SSWI nodes, malformed context lists, non-soft parent IRQs, missing hart indexes, offline/online clear behavior, T-HEAD CLINTEE gating, and IPI delivery under SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aclint-sswi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-al-fic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-al-fic.c

Purpose: Implements Amazon/Annapurna Labs Fabric Interrupt Controller wire-mode support as a 32-source cascaded irqchip.

Important APIs/types/functions: `struct al_fic`, `enum al_fic_state`, `al_fic_irq_set_type()`, `al_fic_irq_handler()`, `al_fic_irq_retrigger()`, `al_fic_register()`, `al_fic_wire_init()`, and `al_fic_init_dt()`.

Control flow: DT init maps MMIO, maps the parent IRQ, initializes hardware with all sources masked and cause cleared, creates a linear domain with generic chips, configures mask/ack registers and callbacks, and installs a chained parent handler. The first child interrupt type selection configures the whole FIC as level-high or rising-edge; later attempts to use a different mode are rejected.

State and persistence: `struct al_fic` stores base, domain, name, parent IRQ, and trigger state. Generic chip mask cache tracks masked sources. Hardware state includes cause, mask, control trigger mode, and MSI-X masking.

Dependencies/integration: Uses OF mapping, irqdomain generic chips, chained IRQ helpers, bitfield helpers, and generic mask/ack operations.

Risks and test signals: Test mixed trigger requests, retrigger via set-cause register, mask-cache correctness, parent IRQ disposal on init failure, and level/edge handler switching after the first configured source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-al-fic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-alpine-msi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-alpine-msi.c

Purpose: Provides Annapurna Labs Alpine MSI-X support by allocating GIC SPIs and composing MSI messages targeting a local GIC interrupt doorbell address.

Important APIs/types/functions: `struct alpine_msix_data`, `alpine_msix_allocate_sgi()`, `alpine_msix_free_sgi()`, `alpine_msix_compose_msi_msg()`, `alpine_msix_middle_domain_alloc()`, `alpine_msix_init_domains()`, `alpine_msix_init()`, `middle_irq_chip`, and `alpine_msi_parent_ops`.

Control flow: Init reads the MSI doorbell resource and DT properties `al,msi-base-spi`/`al,msi-num-spis`, creates a bitmap of available SPIs, finds the parent GIC domain, and creates an MSI parent domain. Allocation reserves a contiguous bitmap range, allocates matching parent GIC IRQs with edge-rising fwspecs, and associates the middle irqchip for MSI message composition.

State and persistence: Driver state holds a spinlock, doorbell address, SPI base/count, and allocation bitmap retained after successful init. Each allocated IRQ stores the SPI hwirq and chip data.

Dependencies/integration: Uses OF address/IRQ helpers, GIC IRQ domains, PCI MSI generic library, MSI parent domains, and bitmap allocation.

Risks and test signals: Test multi-vector MSI allocation/free, ENOSPC handling, parent allocation rollback, MSI message address/data encoding, property validation, and affinity propagation through the parent irqchip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-alpine-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-apple-aic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-apple-aic.c

Purpose: Implements Apple Silicon AIC/AIC2/AIC3 interrupt controllers, including hardware IRQs, FIQ sources, virtualized IPIs through `ipi_mux`, timer/PMU FIQ handling, affinity hints, and KVM VGIC maintenance integration.

Important APIs/types/functions: `struct aic_irq_chip`, `struct aic_info`, `aic_handle_irq()`, `aic_handle_fiq()`, `aic_irq_mask()/unmask()/eoi()`, FIQ mask/unmask/eoi helpers, `aic_irq_domain_translate()`, `aic_irq_domain_alloc()`, `aic_ipi_send_fast()`, `aic_handle_ipi()`, `aic_init_cpu()`, `build_fiq_affinity()`, and `aic_of_ic_init()`.

Control flow: OF init maps controller registers, selects version capabilities from compatible data, derives register layout/die stride, creates a tree IRQ domain, initializes `ipi_mux`, parses optional FIQ affinity children, installs IRQ and FIQ exception handlers, masks/clears all IRQs across dies, sets default targets for AICv1, enables AIC2/3 config, registers CPU hotplug initialization, optionally maps the VGIC maintenance FIQ, and publishes VGIC info. IRQ handling reads event registers until empty, dispatching IRQ events or IPI events; FIQ handling probes fast IPI, timer, PMU, and uncore PMU sources directly from sysregs.

State and persistence: Global `aic_irqc`, per-CPU FIQ unmasked bits, static keys for fast/local IPIs, per-FIQ affinity masks, register offsets, die/IRQ counts, and hardware mask/software-trigger state persist for the boot lifetime.

Dependencies/integration: Uses ARM64 sysregs, Apple PMU definitions, irqdomain hierarchy, `ipi_mux`, CPU hotplug, OF bindings, KVM VGIC info, static branches, and ARM exception hooks.

Risks and test signals: Test AICv1/v2/v3 register layouts, EL1 versus EL2 timer remapping, fast/local IPI selection, FIQ storms from unsupported PMU/uncore sources, multi-die IRQ encoding, affinity parsing, VGIC maintenance disable path, and CPU hotplug reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-apple-aic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-armada-370-xp.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-armada-370-xp.c

Purpose: Implements the Marvell Armada 370/XP MPIC, including wired IRQs, per-CPU interrupts, optional IPI doorbells, PCI MSI domains, CPU hotplug reinitialization, cascaded mode, and syscore suspend/resume.

Important APIs/types/functions: `struct mpic`, `mpic_irq_mask()/unmask()`, `mpic_irq_map()`, `mpic_handle_irq()`, `mpic_handle_cascade_irq()`, MSI helpers (`mpic_msi_alloc()`, `mpic_compose_msi_msg()`, `mpic_msi_init()`), IPI helpers (`mpic_ipi_send_mask()`, `mpic_ipi_init()`), CPU hotplug callbacks, `mpic_suspend()/resume()`, and `mpic_of_init()`.

Control flow: Init maps global and per-CPU regions, disables all interrupts, detects parent IRQ presence to choose top-level or cascaded mode, creates a wired IRQ domain, initializes boot CPU masks/perf IRQs, creates an MSI domain when PCI MSI is enabled, and either installs `set_handle_irq()` plus IPI domain or chains to a parent IRQ. Runtime top-level handling reads CPU INTACK repeatedly and dispatches normal, MSI, or IPI sources; cascaded mode scans per-CPU cause bits and source CPU masks.

State and persistence: `mpic_data` stores mapped bases, parent IRQ, wired/IPI/MSI domains, MSI bitmap and doorbell metadata, and saved doorbell mask. Per-CPU mask registers must be restored on CPU hotplug and resume.

Dependencies/integration: Uses OF, ARM exception hooks, irqdomain, MSI library, PCI MSI, SMP IPI APIs, CPU hotplug, syscore PM, and architecture CPU logical maps.

Risks and test signals: Test top-level versus cascaded platforms, per-CPU/global mask split, MSI allocation/free and message CPU encoding, IPI ordering barriers, suspend/resume doorbell restore, CPU hotplug, and IRQs 0/1 special handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-armada-370-xp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-i2c-ic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-i2c-ic.c

Purpose: Implements the Aspeed AST2400/AST2500 I2C interrupt fan-out controller, converting one parent interrupt into per-bus child interrupts.

Important APIs/types/functions: `struct aspeed_i2c_ic`, `aspeed_i2c_ic_irq_handler()`, `aspeed_i2c_ic_map_irq_domain()`, `aspeed_i2c_ic_of_init()`, and two `IRQCHIP_DECLARE` compatibles.

Control flow: Init allocates state, maps one MMIO register, maps the parent IRQ, creates a 14-entry linear domain, names it, and installs a chained parent handler. The handler reads the status word and dispatches every set bit to the child domain with a dummy irqchip/simple handler.

State and persistence: State is only base address, parent IRQ, and IRQ domain. The hardware status register is read but not explicitly acknowledged here, implying child I2C controllers likely clear their own conditions.

Dependencies/integration: Uses OF address/IRQ parsing, chained IRQ helpers, irqdomain, `dummy_irq_chip`, and generic child IRQ handling.

Risks and test signals: Test status bits for all 14 buses, parent interrupt clearing semantics, missing parent IRQ cleanup, domain host data being NULL despite `irq_set_chip_data()`, and interrupt storms if child handlers do not clear source status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-i2c-ic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-intc.c

Purpose: Implements the Aspeed AST2700 interrupt controller as a 32-source chained irqchip with enable/status registers.

Important APIs/types/functions: `struct aspeed_intc_ic`, `aspeed_intc_ic_irq_handler()`, `aspeed_intc_irq_mask()`, `aspeed_intc_irq_unmask()`, `aspeed_intc_ic_map_irq_domain()`, and `aspeed_intc_ic_of_init()`.

Control flow: Init maps registers, clears all pending status bits, disables all enables, creates a 32-entry domain, initializes raw spinlocks, validates every parent IRQ in the DT node, then chains the same handler to each parent. The handler reads status under `gic_lock`, dispatches each set child bit, and writes the bit back to clear status.

State and persistence: Persistent state includes base, two raw spinlocks, and the IRQ domain. Hardware state consists of enable bits and write-one-to-clear status bits.

Dependencies/integration: Uses OF IRQ parsing, chained IRQ handling, raw spinlocks, irqdomain, MMIO, and level child handlers.

Risks and test signals: Mask/unmask reads occur before taking `intc_lock`, so concurrent RMW races should be reviewed. Test multiple parent IRQs, all 32 child bits, status clearing after child handling, init failure cleanup after mapped parent IRQs, and lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-scu-ic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-scu-ic.c

Purpose: Implements Aspeed SCU interrupt controllers across AST24xx/25xx/26xx/27xx variants, handling combined enable/status registers and split IER/ISR layouts.

Important APIs/types/functions: `struct aspeed_scu_ic_variant`, `struct aspeed_scu_ic`, combined/split IRQ handlers, combined/split mask/unmask callbacks, `aspeed_scu_ic_map()`, `aspeed_scu_ic_find_variant()`, and `aspeed_scu_ic_of_init()`.

Control flow: Init finds variant metadata from the compatible string, maps registers, clears pending status and disables enable bits according to combined or split layout, maps the parent IRQ, creates a linear child domain sized by variant `num_irqs`, and chains the correct handler. Handlers compute enabled pending bits with variant shift/mask and dispatch child hwirqs, then clear the hardware status bit.

State and persistence: Runtime state stores enable mask, shift, number of IRQs, base, domain, and IER/ISR offsets. Hardware state persists in SCU enable/status registers and is variant-dependent.

Dependencies/integration: Uses OF, chained IRQs, irqdomain, bit helpers, and MMIO. It returns `-EINVAL` for affinity changes because the SCU fan-out has no CPU targeting.

Risks and test signals: Test all variant compatibles, especially AST2700 split register offsets; verify write-one-to-clear operations do not accidentally clear unrelated combined status bits; test shifted IRQ ranges, parent storms, and error cleanup after mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-scu-ic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-vic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-vic.c

Purpose: Implements the root Aspeed VIC for AST2400/AST2500 systems as a 64-source interrupt controller with top-level ARM IRQ handling.

Important APIs/types/functions: `struct aspeed_vic`, `vic_init_hw()`, `avic_handle_irq()`, `avic_ack_irq()`, `avic_mask_irq()`, `avic_unmask_irq()`, `avic_mask_ack_irq()`, `avic_map()`, and `avic_of_init()`.

Control flow: OF init rejects non-root/duplicate controllers, maps registers, allocates state, masks all sources, clears software triggers, selects IRQ mode, records which sources are edge-triggered from sense registers, clears edge latches, installs `set_handle_irq()`, and creates a simple IRQ domain. Runtime handling loops over low then high status registers, dispatching the first set pending bit until none remain.

State and persistence: Global `system_avic` points to the single controller. Per-controller state stores base, edge source masks for low/high banks, and the domain. Hardware enable, trigger, sense, and edge-latch state persists until explicitly changed.

Dependencies/integration: Uses OF, ARM exception IRQ hook, irqdomain, syscore-related includes, and generic edge/level handlers.

Risks and test signals: Test both 32-bit banks, firmware-provided sense configuration, edge latch clearing, duplicate-root rejection, and mixed edge/level source handling under interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-vic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ath79-cpu.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ath79-cpu.c

Purpose: Provides Atheros/QCA AR71xx/AR724x/AR913x CPU interrupt dispatch with optional DDR write-buffer flush mapping before invoking MIPS CPU IRQ handlers.

Important APIs/types/functions: `irq_wb_chan[]`, `plat_irq_dispatch()`, `ar79_cpu_intc_of_init()`, and `IRQCHIP_DECLARE(ar79_cpu_intc, "qca,ar7100-cpu-intc", ...)`.

Control flow: Platform dispatch reads MIPS status/cause pending bits, reports spurious interrupts if none are pending, then handles pending IP lines from highest to lowest. For mapped lines, it flushes the configured DDR write-buffer channel before calling `do_IRQ()`. OF init fills the IRQ-to-write-buffer-channel table from `qca,ddr-wb-channels` and optional `qca,ddr-wb-channel-interrupts`, then delegates to `mips_cpu_irq_of_init()`.

State and persistence: Global `irq_wb_chan` records optional write-buffer channel IDs per CPU interrupt line for the boot lifetime.

Dependencies/integration: Uses MIPS CP0 status/cause registers, ATH79 DDR write-buffer flush API, OF phandle parsing, and generic MIPS CPU IRQ domain initialization.

Risks and test signals: Test missing/default DDR write-buffer mappings, invalid IRQ indexes, phandle parse failures, ordering of write-buffer flush before device driver handling, spurious interrupt accounting, and multi-pending dispatch order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ath79-cpu.c -->
