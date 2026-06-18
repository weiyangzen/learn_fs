# subset-b-004997 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_pc.c -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_pc.c

Purpose: low-level PC-compatible parallel-port driver for ISA, PnP, PCI, platform-created legacy ports, Super-I/O chipsets, and selected PCI parallel cards. It maps classic SPP data/status/control I/O ports plus optional EPP and ECP/ECR windows into `struct parport_operations`.

Important APIs/types/functions: exports `parport_pc_probe_port()` and `parport_pc_unregister_port()`. The internal `__parport_pc_probe_port()` allocates `parport_operations` and `parport_pc_private`, calls `parport_register_port()`, reserves I/O regions, detects SPP/EPP/PS2/ECP/FIFO/DMA/IRQ capabilities, requests IRQ/DMA, and calls `parport_announce_port()`. EPP helpers override IEEE1284 defaults when hardware EPP is detected; FIFO/DMA helpers accelerate compat/ECP writes. PCI/PnP paths include `parport_pc_pci_probe()`, `parport_pc_pnp_probe()`, VIA/ITE Super-I/O probes, and static card tables.

Control flow/state: module init parses `io`, `io_hi`, `irq`, `dma`, and `init_mode`, registers the platform driver, probes user-specified ports or discovers Super-I/O, PnP, ISA, and PCI ports. Runtime state lives in private CTR/ECR snapshots, FIFO thresholds, DMA buffer/handle, `ports_list`, and parport core ownership state. Removal unregisters PCI/PnP/platform drivers and walks `ports_list` to release IRQ, DMA, I/O regions, coherent buffers, ops, private data, and optional synthetic platform devices.

Dependencies/integration: depends on parport core, IEEE1284 helpers, I/O port APIs, PCI, PNP, platform devices, ISA DMA APIs, and architecture `asm/parport.h`. Risks are hardware probing side effects, old chipset quirks, ECR writable masks, 32-bit legacy assumptions, DMA residue handling, and mode transitions around FIFO drains. Test signals include boot/module probe logs, mode list accuracy, interrupt/DMA fallback messages, parport device attachment, EPP timeout recovery, and clean unload without leaked regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_pc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_serial.c -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_serial.c

Purpose: supports PCI multi-I/O cards that expose serial and parallel functions through one PCI function/BAR layout. It coordinates parallel-port registration through `parport_pc_probe_port()` and serial-port registration through the 8250 PCI helper layer.

Important APIs/types/functions: `struct parport_pc_pci` describes per-card parallel BAR geometry and optional hooks; `pci_parport_serial_boards[]` describes serial geometry for `pciserial_init_ports()`. `netmos_parallel_init()` derives NetMos parallel-port count from subsystem IDs. `parport_serial_private` stores the serial handle, copied parallel card descriptor, and registered parport pointers. `parport_serial_pci_probe()` enables the PCI device, calls `parport_register()`, then `serial_register()`.

Control flow/state: probe allocates managed private storage, installs drvdata, enables the device with `pcim_enable_device()`, probes all declared parallel BARs using shared IRQs, and then initializes serial ports. If serial registration fails, all successfully registered parallel ports are immediately unregistered. Remove tears down serial ports first and then parports. Suspend/resume delegates only to serial helpers and explicitly leaves parport handling as a FIXME.

Dependencies/integration: relies on PCI ID matching, 8250 PCI board data, parport_pc low-level probing, and shared IRQ support. Risks include large static card tables, BAR interpretation quirks where `hi > 6` means offset, mismatch between parallel and serial geometry, returning an IRQ-vector error mid-loop after earlier parports were created, and missing parport power-management restore. Test signals are probe/remove on representative cards, NetMos subsystem variations, serial-failure unwind, and suspend/resume checks for serial plus parport usability after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_sunbpp.c -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_sunbpp.c

Purpose: SBUS/OpenFirmware platform driver for Sun bidirectional parallel-port hardware (`SUNW,bpp`). It adapts Sun BPP register semantics to the generic parport operations interface.

Important APIs/types/functions: `parport_sunbpp_ops` supplies data, control, status, IRQ, direction, and state callbacks. `status_sunbpp_to_pc()` and `control_sunbpp_to_pc()` translate Sun register polarity into PC parport bit definitions. `bpp_probe()` maps OF resources, duplicates ops, registers a parport, requests a shared IRQ with `parport_irq_handler`, enables device interrupts, initializes forward direction, stores drvdata, and announces the port. `bpp_remove()` performs the reverse.

Control flow/state: state is almost entirely hardware register state in `struct bpp_regs`; save/restore persists the parport control bits in `parport_state.u.pc.ctr`. Probe stores the mapped base address in `p->base`, size in `p->size`, and parent device in `p->dev`. Remove disables IRQs before freeing the IRQ, unmaps the OF resource, drops the port reference, and frees duplicated ops.

Dependencies/integration: integrates platform OF matching, SBUS I/O accessors, SPARC OpenPROM/DMA headers, and parport IEEE1284 generic helpers. Risks include register polarity mistakes, assuming `op->archdata.irqs[0]` exists, using `parport_put_port()` rather than `parport_del_port()` after `parport_remove_port()`, and limited non-SPARC coverage. Test signals include OF match/probe on Sun BPP hardware, status/control bit readback, shared IRQ activity, clean unbind, and IEEE1284 fallback transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_sunbpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/probe.c -->
# sources/distributed-fs/ceph-client/drivers/parport/probe.c

Purpose: obtains and parses IEEE 1284 Device ID strings for devices attached to parport ports, filling `port->probe_info[]` and logging human-readable class/manufacturer/model information.

Important APIs/types/functions: `parport_device_id()` is the exported entry point. It opens a daisy device, claims the port, negotiates compatibility then nibble Device ID mode, calls `parport_read_device_id()`, restores compatibility mode, parses returned fields with `parse_data()`, and closes the pardevice. `classes[]` maps IEEE class tokens to parport class IDs and descriptions.

Control flow/state: `parport_read_device_id()` reads the two-byte length header, handles big-endian/little-endian and off-by-two broken devices by trying sorted candidate lengths, drains excess data when the caller buffer is too small, terminates the caller buffer, and reports short/malformed IDs. `parse_data()` tokenizes semicolon-separated key/value pairs, normalizes keys, stores dynamically allocated strings in `parport_device_info`, guesses printers from PJL/PCL command sets, and invokes `pretty_print()`.

Dependencies/integration: depends on parport open/claim/negotiate/read/release/close APIs, daisy-chain naming, kernel string helpers, and allocation APIs. Risks include malformed device IDs, memory churn when replacing probe strings, blocking while claiming the port, and reliance on device behavior during repeated reads. Test signals include successful `/proc/sys/dev/parport/.../autoprobe*` content, logs for class/model, malformed length handling, small-buffer behavior, and no leaks after repeated probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/procfs.c -->
# sources/distributed-fs/ceph-client/drivers/parport/procfs.c

Purpose: provides sysctl/proc integration for parport defaults, per-port attributes, active device reporting, per-device timeslice tuning, and IEEE1284 autoprobe data.

Important APIs/types/functions: `parport_proc_register()` and `parport_proc_unregister()` manage `dev/parport/<port>` and `dev/parport/<port>/devices`; `parport_device_proc_register()` and unregister create per-pardevice `timeslice`; default registration is done by `subsys_initcall(parport_default_proc_register)`. Read handlers include `do_active_device()`, hardware base/irq/dma/modes handlers, and `do_autoprobe()` under `CONFIG_PARPORT_1284`.

Control flow/state: templates are duplicated per port/device, populated with port pointers, `spintime`, `timeslice`, and `probe_info` references, then registered with dynamically built sysctl paths. Defaults are backed by global `parport_default_timeslice` and `parport_default_spintime`, bounded by min/max constants. If sysctl or procfs is disabled, stubs return success and only initialize/exit the parport bus.

Dependencies/integration: depends on `CONFIG_SYSCTL`, `CONFIG_PROC_FS`, parport bus init/exit, sysctl registration, and parport core fields. Risks include registration unwind ordering, dynamic path allocation failure, proc handler buffer truncation, and stale pointers if unregister does not clear tables before freeing. Test signals include sysctl tree presence, writable bounded defaults, readable base/irq/dma/modes/autoprobe, and clean unregister on port/device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/share.c -->
# sources/distributed-fs/ceph-client/drivers/parport/share.c

Purpose: core parallel-port resource manager. It owns parport bus registration, port lifetime, driver notifications, pardevice registration, exclusive/shared access arbitration, wait queues, and IRQ dispatch.

Important APIs/types/functions: exports `__parport_register_driver()`, `parport_unregister_driver()`, `parport_register_port()`, `parport_announce_port()`, `parport_remove_port()`, `parport_register_dev_model()`, `parport_unregister_device()`, find/get/put helpers, `parport_claim()`, `parport_claim_or_block()`, `parport_release()`, and `parport_irq_handler()`. `dead_ops` replaces low-level callbacks after port removal.

Control flow/state: `all_ports` assigns stable parport numbers; `portlist` holds announced live ports; `registration_lock` serializes driver attach/detach. Port registration initializes device-model state, IEEE1284 state, locks, lists, default timing, and class defaults. Announcement registers proc entries, attaches daisy slaves, and notifies drivers. Device registration handles exclusive/lurking policy, module references, pardevice lists, state initialization, and per-device proc entry. Claiming preempts the current owner when callbacks permit, saves/restores hardware state, and manages wait lists.

Dependencies/integration: integrates Linux driver core bus APIs, kmod low-level autoloading, parport procfs, IEEE1284 daisy helpers, module reference counting, and low-level driver ops. Risks are documented wait-list locking gaps in release, preemption callbacks from interrupt context, stale ops after removal, exclusive-device races, and reference-counting complexity across device model failures. Test signals include concurrent claim/release stress, driver register/unregister attach/detach ordering, exclusive registration denial, low-level driver autoload, device removal while clients wait, and IRQ forwarding to `parport_generic_irq()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/Kconfig

Purpose: top-level PCI subsystem configuration. It defines the main `PCI` menu and options controlling core PCI, PCIe, MSI, quirks, IOV, ATS/PRI/PASID, DOE, TSM, P2PDMA, Hyper-V, dynamic OF nodes, hierarchy tuning, VGA arbitration, and subordinate PCI menus.

Important symbols: `HAVE_PCI` gates visibility, `FORCE_PCI` selects PCI unconditionally, `PCI` depends on `HAVE_PCI` and `MMU`, `PCI_MSI` selects generic MSI IRQ support, `PCI_IOV` selects `PCI_ATS`, `PCI_PRI` and `PCI_PASID` also select `PCI_ATS`, and `PCI_TSM` selects `PCI_IDE`, `PCI_DOE`, and `TSM`. It sources `pcie`, hotplug, controller, endpoint, switch, and pwrctrl Kconfigs.

Control flow/state: Kconfig state controls which objects the PCI Makefile builds and which code paths are compiled in core files such as `ats.c`, `access.c`, and controller drivers. The MPS/MRRS choice defaults to `PCIE_BUS_DEFAULT` and can be overridden at boot.

Dependencies/integration: integrates arch-provided PCI support with subsystem features and platform controller menus. Risks include hidden selects enabling security-sensitive capability code, compile-test dependency drift, and feature combinations requiring IOMMU/MSI/ACPI/OF support. Test signals include Kconfig dependency resolution, allmodconfig/allyesconfig builds, boot parameter overrides, and feature-specific object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/Makefile

Purpose: object list for the PCI core, feature modules, and subdirectories. It wires Kconfig symbols into compilation units and ensures endpoint/controller/switch directories are traversed.

Important build rules: `obj-$(CONFIG_PCI)` builds core files including `access.o`, `bus.o`, `probe.o`, `pci.o`, resource setup, IRQ, VPD, driver, and mmap/devres support. Conditional additions cover procfs, sysfs, ACPI, iomap, OF, quirks, ATS, IOV, ECAM, P2PDMA, Xen, VGA arbiter, DOE, IDE, TSM, NPEM, TPH, and CardBus setup. `obj-y` always enters `controller/` and `switch/`, while endpoint is ordered before users.

Control flow/state: no runtime state, but build order matters for endpoint initialization and subdirectory inclusion. `subdir-ccflags-$(CONFIG_PCI_DEBUG)` adds `-DDEBUG`; `trace.o` gets an include path and is built with tracing.

Dependencies/integration: consumes symbols from the top PCI Kconfig and exposes subdirectory builds to controller Kconfigs. Risks include missing objects for selected symbols, ordering regressions, and always-descending directories relying on internal Kconfig guards. Test signals are `make drivers/pci/`, allyesconfig/allmodconfig object coverage, and absence of missing-symbol link errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/access.c -->
# sources/distributed-fs/ceph-client/drivers/pci/access.c

Purpose: central PCI configuration-space access layer. It validates alignment, serializes config ops when configured, delegates to bus-specific `pci_ops`, exposes generic ECAM/MMIO accessors, implements user-access blocking around unsafe device states, and provides PCIe capability helpers.

Important APIs/types/functions: exports `pci_bus_read/write_config_{byte,word,dword}`, `pci_generic_config_read/write`, `pci_generic_config_read32/write32`, `pci_bus_set_ops()`, `pci_user_read/write_config_*`, `pci_cfg_access_lock/trylock/unlock()`, PCIe capability read/write/clear-set helpers, and device-level `pci_read/write_config_*`. `pci_lock` is the global raw spinlock unless `CONFIG_PCI_LOCKLESS_CONFIG` disables it.

Control flow/state: bus-level macros check offset alignment, lock, call `bus->ops`, and set error responses on failure. User accesses wait on `pci_cfg_wait` while `dev->block_cfg_access` is set. PCIe capability helpers synthesize zero or presence-detect defaults for unimplemented registers and protect selected read-modify-write paths with `dev->pcie_cap_lock`. 32-bit-only config write helpers warn once about adjacent RW1C corruption risk.

Dependencies/integration: depends on `struct pci_bus`, `struct pci_dev`, arch/controller `pci_ops`, wait queues, MMIO read/write primitives, and PCIe capability metadata. Risks include lock ordering, sleeping while dropping/reacquiring `pci_lock`, unsafe partial writes on 32-bit-only hardware, and callers ignoring PCIBIOS errors. Test signals include misaligned access rejection, disconnected-device error responses, config blocking during D-state/BIST transitions, PCIe register default behavior, and lockless-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/ats.c -->
# sources/distributed-fs/ceph-client/drivers/pci/ats.c

Purpose: implements PCIe ATS plus optional PRI and PASID capability management for IOMMU-facing devices and SR-IOV relationships.

Important APIs/types/functions: `pci_ats_init()`, `pci_ats_supported()`, `pci_prepare_ats()`, `pci_enable_ats()`, `pci_disable_ats()`, `pci_restore_ats_state()`, queue-depth and page-aligned queries; under `CONFIG_PCI_PRI`, PRI init/enable/disable/restore/reset and support/status helpers; under `CONFIG_PCI_PASID`, PASID init/enable/disable/restore/features/max/status helpers.

Control flow/state: init locates extended capability offsets and stores them in `pci_dev`. ATS enable validates support, untrusted status, page shift, PF/VF STU consistency, writes the control register, and sets `ats_enabled`/`ats_stu`; restore replays that state after reset/resume. PRI tracks `pri_enabled`, allocated request count, and PASID-required status, while VFs share PF PRI. PASID requires PF support, EETLP or no-TLP-prefix capability, ACS path isolation, supported feature bits, then writes enable/features into control state.

Dependencies/integration: depends on PCI config access, PCI extended capability definitions, SR-IOV PF/VF helpers, ACS path checks, and IOMMU drivers calling prepare/enable at the right lifecycle point. Risks include enabling translation features on untrusted or non-isolated paths, PF/VF state mismatches, restore after reset missing capability state, and WARN_ON misuse indicating lifecycle bugs. Test signals include IOMMU-driven ATS/PRI/PASID enablement, VF behavior, reset/resume restore, unsupported-feature rejection, and ACS isolation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/ats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/bus.c -->
# sources/distributed-fs/ceph-client/drivers/pci/bus.c

Purpose: PCI bus resource and device-addition helpers. It manages host bridge window lists, allocates device resources from bus windows, clips bridge resources, starts devices, walks bus hierarchies, and reference-counts PCI buses.

Important APIs/types/functions: exports resource list helpers `pci_add_resource_offset()`, `pci_add_resource()`, `pci_free_resource_list()`, `pci_bus_resource_n()`, `devm_request_pci_bus_resources()`, allocation helpers `pci_bus_alloc_resource()`, `pci_bus_clip_resource()`, device start helpers `pci_bus_add_device()` and `pci_bus_add_devices()`, hierarchy walkers `pci_walk_bus()` and `pci_walk_bus_reverse()`, and `pci_bus_get/put()`.

Control flow/state: extra bus resources are stored as `struct pci_bus_resource` list entries beyond fixed bridge-window slots. Allocation converts CPU resources to bus regions, clips to 32-bit/64-bit/high address windows, filters type/prefetch flags, applies min/max/alignment, and calls `allocate_resource()`. Adding a device runs arch hooks, final fixups, dynamic OF node creation for bridges, sysfs/proc attachment, D3/runtime PM setup, optional binding permission, initial probe, and added-state marking. Walkers hold `pci_bus_sem`.

Dependencies/integration: uses generic resource lists, resource trees, OF/proc/sysfs/PM hooks, PCI fixups, architecture `pcibios_*` hooks, and downstream driver binding. Risks include allocation window translation bugs, prefetch/type mismatches, partial device-add side effects, dynamic OF node availability rules, and recursive walk locking assumptions. Test signals include host bridge resource request failures, BAR allocation across 32/64-bit windows, bridge window clipping logs, device sysfs/proc presence, recursive probe ordering, and lockdep for walk APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/Kconfig

Purpose: PCI host/controller driver menu. It collects platform-specific root complex, endpoint, MSI, ECAM, bridge-emulation, and error-handling configuration for many SoC and firmware environments.

Important symbols: common support includes `PCI_HOST_COMMON` selecting `PCI_ECAM`; individual controllers include Aardvark, Altera, Apple, Aspeed, Broadcom STB/iProc, Cavium Thunder, Faraday, generic host, HiSilicon error, IXP4xx, VMD, Loongson, Marvell EBU, MediaTek, Hyper-V interface, Tegra, Renesas R-Car/RZ, Rockchip host/EP, V3, X-Gene, Xilinx variants, and sourced Cadence/DWC/Mobiveil/PLDA menus.

Control flow/state: Kconfig selections determine which controller objects are compiled by `controller/Makefile` and which shared infrastructure is enabled, especially MSI libraries, bridge emulation, ECAM, MFD syscon, endpoint support, and platform/OF dependencies.

Dependencies/integration: links architecture symbols, OF/ACPI availability, PCI core features, MSI infrastructure, endpoint framework, and compile-test coverage. Risks are dependency cycles, accidental hidden selects, allmodconfig build failures on compile-test paths, and controller options missing required shared infrastructure. Test signals include Kconfig warning-free resolution, cross-architecture compile tests, OF/ACPI combinations, and controller-specific boot probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/Makefile

Purpose: maps PCI controller Kconfig symbols to controller object files and subdirectories.

Important build rules: conditionally enters `cadence/` for `CONFIG_PCIE_CADENCE`, builds individual controller objects for Aardvark, Hyper-V, MVEBU, Tegra, Renesas, generic host, Thunder, Xilinx, X-Gene, Versatile, iProc, Altera, Rockchip, MediaTek, VMD, Loongson, HiSilicon error, Apple, MT7621, and Aspeed. It always descends into `dwc/`, `mobiveil/`, and `plda/`, whose own Makefiles/Kconfigs gate contents. ACPI+quirk ARM64 blocks force-build Thunder/X-Gene quirk providers for generic ACPI roots without explicit controller options.

Control flow/state: no runtime state; build state controls which controller drivers and shared object modules are linked. Multi-object host/EP combinations such as R-Car are assembled by listing common plus mode-specific objects.

Dependencies/integration: consumes symbols from `controller/Kconfig`, Cadence/DWC/Mobiveil/PLDA submenus, ACPI, PCI quirks, and ARM64. Risks include object duplication when both normal and ACPI quirk paths select a file, missing shared object members for composite drivers, and always-descended subdirectories relying on internal guards. Test signals are per-controller build targets, allmodconfig link checks, and ACPI quirk coverage on ARM64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/Kconfig

Purpose: Cadence PCIe controller configuration menu for shared core infrastructure, host mode, endpoint mode, generic platform wrappers, and vendor-specific Cadence-based controllers.

Important symbols: `PCIE_CADENCE` is shared infrastructure; `PCIE_CADENCE_HOST` depends on OF, selects IRQ domains and shared core; `PCIE_CADENCE_EP` depends on OF and PCI endpoint; `PCIE_CADENCE_PLAT_HOST` and `_EP` select platform and relevant host/EP support. Vendor options include `PCI_SKY1_HOST` selecting HPA/Cadence host plus ECAM, `PCIE_SG2042_HOST`, and TI `PCI_J721E` with separate host and endpoint options selecting Cadence host/EP as needed.

Control flow/state: selected symbols drive `cadence/Makefile` multi-object modules for common core, host common/host/HPA, endpoint, platform wrapper, J721E, SG2042, and SKY1. Host and endpoint modes can be built independently when dependencies permit.

Dependencies/integration: integrates OF probing, PCI endpoint framework, IRQ domain support, Cadence common code, and architecture/vendor compile-test gates. Risks include host/endpoint symbol interactions, missing endpoint dependency in vendor EP choices, and subtle sharing between first/second generation Cadence HPA code. Test signals include host and EP build matrices, DT binding probe tests, endpoint framework registration, and vendor SoC boot enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/Makefile

Purpose: builds Cadence PCIe shared, host, endpoint, platform, and vendor-specific controller objects.

Important build rules: `pcie-cadence-mod-y` combines HPA and common Cadence core objects; `pcie-cadence-host-mod-y` combines host common, host, and host-HPA objects; `pcie-cadence-ep-mod-y` builds endpoint support. `obj-$(CONFIG_PCIE_CADENCE)` links the shared module, host/EP symbols add their modules, platform support adds `pcie-cadence-plat.o`, and vendor symbols add `pci-j721e.o`, `pcie-sg2042.o`, and `pci-sky1.o`.

Control flow/state: no runtime behavior, but module composition controls symbol availability for wrapper drivers. Core, host, and endpoint are separated so vendor/platform drivers can select only the required mode.

Dependencies/integration: consumes Cadence Kconfig symbols and ties shared infrastructure to concrete SoC wrappers. Risks include missing objects from composite modules, assignment versus append semantics for `obj-$(CONFIG_PCIE_CADENCE) =`, and host/EP wrappers selecting an incomplete common set. Test signals are incremental builds for each symbol, module link checks, and boot/probe tests for platform, J721E, SG2042, and SKY1 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/Makefile -->
