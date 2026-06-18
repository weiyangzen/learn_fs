# subset-b-005002 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-hyperv.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-hyperv.c

## Purpose
`pci-hyperv.c` is the Hyper-V virtual PCI front-end. It exposes PCI Express functions passed through from the Hyper-V parent partition as synthetic PCI root buses in the Linux guest. Each VMBus offer becomes a root PCI bus with its own PCI domain, synthetic config-space access, MSI/MSI-X interrupt remapping, device hot-add/eject handling, MMIO window allocation, and suspend/resume recovery. It does not expose conventional bridges or legacy line interrupts; the host protocol supplies child device descriptions and interrupt translations.

## Important APIs, types, and functions
The file defines the Hyper-V vPCI protocol message IDs, version constants, and packed message structures such as `pci_bus_relations`, `pci_bus_relations2`, `pci_resources_assigned*`, `pci_create_interrupt*`, `pci_read_block`, and `pci_write_block`. `hv_pcibus_device` is the main bus state object: it embeds arch-specific PCI sysdata, the `pci_host_bridge`, protocol version, VMBus device, MMIO config window resources, child-device lists, IRQ domain, ordered workqueue, and state machine. `hv_pci_dev` tracks each synthetic child function with the Hyper-V slot descriptor, refcount, optional `pci_slot`, BAR probes, and config-block invalidation callback.

Config-space access is implemented by `hv_pcifront_read_config()` and `hv_pcifront_write_config()` through `_hv_pcifront_read_config()` and `_hv_pcifront_write_config()`. These synthesize read-only identity fields from the host-provided description, force legacy interrupt fields and ROM BARs to zero, and route other config accesses through a two-page MMIO selector/data window. On x86, `hbus->use_calls` can use Hyper-V MMIO hypercalls via `hv_pci_read_mmio()` and `hv_pci_write_mmio()` instead of direct ioremap access.

Interrupt support is centered on `hv_pcie_init_irq_domain()`, `hv_compose_msi_msg()`, `hv_msi_free()`, `hv_irq_mask()`, and `hv_irq_unmask()`. The driver creates a PCI MSI parent IRQ domain over the platform root domain. On x86, retargeting uses `HVCALL_RETARGET_INTERRUPT` in `hv_irq_retarget_interrupt()` unless running as a root partition, where `hv_map_msi_interrupt()` is used. On arm64, the driver creates a Hyper-V vPCI SPI domain backed by the GIC parent domain and composes protocol v1.4 interrupt messages with larger vectors.

The config-block backchannel is exported through `hvpci_block_ops` using `hv_read_config_block()`, `hv_write_config_block()`, and `hv_register_block_invalidate()`. Device discovery and hotplug are handled by `hv_pci_devices_present()`, `hv_pci_devices_present2()`, `hv_pci_start_relations_work()`, `pci_devices_present_work()`, `hv_pci_eject_device()`, and `hv_eject_device_work()`. Probe, teardown, and PM flow through `hv_pci_probe()`, `hv_pci_remove()`, `hv_pci_suspend()`, and `hv_pci_resume()`.

## Control flow
Module initialization checks Hyper-V and VMBus availability, initializes the architecture IRQ support, installs the config-block operations, and registers a VMBus driver for `HV_PCIE_GUID`. Probe allocates a `pci_host_bridge` and `hv_pcibus_device`, chooses a nonzero PCI domain from the VMBus instance GUID, opens the VMBus channel with requestor callbacks, negotiates the highest mutually supported vPCI protocol version, allocates and maps the config MMIO window, creates a firmware node and MSI IRQ domain, and queries bus relations.

The host responds to relation queries asynchronously. `hv_pci_onchannelcallback()` receives VMBus packets, dispatches completion packets to pending stack-based `pci_packet` callbacks under the requestor lock, and turns inbound messages into workqueue tasks. Relation messages are copied into `hv_dr_state` and serialized through an ordered workqueue. `pci_devices_present_work()` drops stale relation snapshots, marks known children missing, creates new `hv_pci_dev` records by querying resource requirements, removes absent children, and either completes the initial resource survey or triggers a PCI rescan for installed buses.

After initial relations are surveyed, probe enters D0 through `PCI_BUS_D0ENTRY`, allocates bridge windows from VMBus MMIO ranges, sends `PCI_RESOURCES_ASSIGNED*` per child to advance the host state, prepopulates BARs using the probed BAR masks, and scans/adds a root PCI bus. Eject messages schedule `hv_eject_device_work()`, which removes the Linux PCI device if present, removes the internal child entry, destroys the sysfs slot, and sends `PCI_EJECTION_COMPLETE`.

MSI composition occurs under IRQ locks. `hv_compose_msi_msg()` selects a dummy CPU/vector where needed, sends the protocol-specific create-interrupt message to the VSP, polls completions while directly draining the channel callback, stores the returned translated interrupt descriptor in `irq_data->chip_data`, and returns the MSI address/data to the PCI/MSI core. Unmask later retargets the interrupt to the effective affinity on x86. Multi-MSI avoids duplicate host allocations by deriving later messages from the first vector.

## State and persistence behavior
The main persistent runtime state is in `hv_pcibus_device`: protocol version, bus state, child list, pending device-relations list, MMIO resources, config mapping, IRQ domain, ordered workqueue, and `wslot_res_allocated`. The state machine moves through `hv_pcibus_init`, `hv_pcibus_probed`, `hv_pcibus_installed`, and `hv_pcibus_removing`; it is protected by `state_lock` where host/device lifecycle crosses PCI core operations. Child lists are protected by `device_list_lock` and child lifetime is refcounted.

The driver persists no disk state. It programs host-side state through VMBus messages: D0 entry/exit, resources assigned/released, interrupt create/delete, config block read/write, and ejection completion. Suspend marks the bus removing, flushes work, releases host resources while keeping child structures, and closes the VMBus channel. Resume reopens the channel, renegotiates only the previous protocol version, queries relations, re-enters D0, re-sends resources, prepopulates BARs, and recreates host interrupt remapping entries by walking existing MSI/MSI-X descriptors.

## Dependencies and integration points
This driver integrates with VMBus, Hyper-V hypercalls, Linux PCI host bridge scanning, PCI MSI domains, ACPI/OF interrupt domains on arm64, x86 vector domains, VMBus MMIO allocation, NUMA node assignment, PCI slot sysfs entries, and `hvpci_block_ops` for VF/PF software backchannel users. It relies on Linux PCI core resource assignment but prepopulates BARs to avoid poor initial scan behavior with Hyper-V virtual BAR mappings.

## Risks and edge cases
Concurrency is the main risk. Completion packets point to stack-allocated request contexts, so the requestor lock and explicit request-ID cleanup paths are essential. `hv_compose_msi_msg()` runs with IRQ locks held and must poll VMBus completions without sleeping, which makes callback reentrancy and channel teardown races high-risk. The code contains specific mitigations for channel rescind, tasklet disable during remove/suspend, workqueue flushes after relation queries, and hibernation CPU-offline retarget failures.

Resource sizing and BAR prepopulation are also delicate. `survey_child_resources()` assumes memory BAR sizes can be summed by low/high type, and `prepopulate_bars()` depends on power-of-two packing and clearing `PCI_COMMAND_MEMORY` before BAR writes so Hyper-V honors updates. Protocol-version branches affect MSI message format, NUMA fields, resource-assignment message sizes, and >64 VP interrupt targeting. Hot add/remove can race with initial probing, ejection can arrive before the PCI bus exists, and kdump can require the D0 retry path that first releases resources believed held by the crashed kernel.

## Test signals
Useful validation includes booting a Hyper-V VM with pass-through PCI or SR-IOV devices, verifying unique nonzero PCI domains, config reads/writes, BAR sizing, MSI/MSI-X and multi-MSI operation, interrupt affinity changes, CPU hotplug/hibernate interrupt migration, config-block read/write/invalidate users, host-initiated hot add/eject, channel rescind during outstanding requests, D0 retry in kdump-like scenarios, and suspend/resume with MSI state restoration. Dynamic debug around VMBus protocol messages, PCI resource assignment logs, and interrupt composition failures gives strong coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-hyperv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-ixp4xx.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-ixp4xx.c

## Purpose
`pci-ixp4xx.c` is the PCI host controller driver for Intel IXP42x/IXP43x ARM SoCs. It turns the SoC PCI controller into a Linux `pci_host_bridge`, implements indirect PCI config cycles, configures AHB-to-PCI and PCI-to-AHB address windows, applies IXP42x config-read errata handling, and installs ARM abort handling for PCI master aborts. The source explicitly notes unverified I/O-space access and DMA support as TODO areas.

## Important APIs, types, and functions
`struct ixp4xx_pci` stores the device, MMIO base, `errata_hammer`, and host/option mode. `ixp4xx_readl()` and `ixp4xx_writel()` deliberately use `__raw_readl()`/`__raw_writel()` because the IXP4xx peripheral bus changes byte ordering based on CPU endian mode, while PCI device accesses remain little-endian.

Config access is split between non-posted indirect PCI cycles and CRP local controller config cycles. `ixp4xx_pci_read_indirect()` and `ixp4xx_pci_write_indirect()` program `NP_AD`, `NP_CBE`, and data registers, then call `ixp4xx_pci_check_master_abort()` to clear and report `IXP4XX_PCI_ISR_PFE`. `ixp4xx_config_addr()` builds Type 0 or Type 1 config addresses for the root bus and subordinate buses. `ixp4xx_pci_read_config()` and `ixp4xx_pci_write_config()` implement the `pci_ops` callbacks with byte-lane-enable calculation and value shifting. `ixp4xx_crp_write_config()` writes controller-local config fields such as BARs and command bits; `ixp4xx_crp_read_config()` is available under `CONFIG_ARM` for abort status handling.

Window setup lives in `ixp4xx_pci_parse_map_ranges()` and `ixp4xx_pci_parse_map_dma_ranges()`. Both consume `pci_host_bridge` windows populated from firmware and require 64 MiB ranges for memory and DMA windows. `ixp4xx_pci_addr_to_64mconf()` converts a base address into four 16 MiB byte fields for controller registers.

## Control flow
`ixp4xx_pci_probe()` allocates a host bridge with private state, selects the `ixp4xx_pci_ops`, detects the IXP42x errata quirk from the OF compatible string, maps the controller registers, reads the controller mode from `IXP4XX_PCI_CSR`, and, on ARM, installs an imprecise external abort handler with `hook_fault_code()`.

Probe then parses and programs memory, I/O, and DMA ranges. In host mode it writes local PCI BAR0-3 to consecutive 16 MiB windows starting at `__pa(PAGE_OFFSET)`, BAR4 to the following CSR/prefetch window, BAR5 to an I/O window at `0xfffffc00`, and the retry/transfer-ready timeout register. It clears PCI error interrupts, writes the CSR initialize-complete and byte-swapping bits, enables PCI memory/master in the local command register, and finally calls `pci_host_probe()`.

## State and persistence behavior
Runtime state is minimal and device-managed: private state, MMIO base, mode flags, and controller registers. The driver writes persistent hardware state for BARs, address windows, interrupt status, endian swap behavior, and PCI command bits, but it maintains no disk state and provides no remove path. The ARM abort handler uses the file-scope `ixp4xx_pci_abort_singleton`, which effectively assumes a single active controller instance.

## Dependencies and integration points
The driver depends on OF platform matching, generic PCI host bridge setup, firmware-provided PCI ranges/dma-ranges, ARM fault handling, IXP4xx controller register semantics, and Linux PCI config access conventions. It integrates with the PCI core only through `pci_host_probe()` and the custom `pci_ops`; there is no MSI, IRQ-domain, runtime PM, or reset-controller integration in this file.

## Risks and edge cases
The biggest hardware risks are endian handling, strict 64 MiB memory/DMA range requirements, and the IXP42x read errata path that repeatedly hammers the config register and assumes reads have no side effects. The abort handler singleton and builtin-only design make removal or multiple-controller scenarios unsafe. Missing `dma-ranges` only logs an error in the parser but still returns success, so firmware omissions may lead to partially configured hardware. The TODOs around I/O-space access and DMA support are explicit test gaps.

## Test signals
Validation should include OF probing for both `intel,ixp42x-pci` and `intel,ixp43x-pci`, config-space reads/writes on root and subordinate buses, master-abort behavior for absent devices, endian-mode tests on big-endian and little-endian ARM builds, 64 MiB range rejection, host-mode BAR programming, I/O-space exercises, DMA-capable endpoint traffic, and ARM imprecise abort recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-ixp4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-loongson.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-loongson.c

## Purpose
`pci-loongson.c` provides Loongson PCI host controller support for OF platforms and ACPI ECAM systems. It maps Loongson-specific CFG0/CFG1 config windows into generic PCI config operations and carries several PCI fixups for Loongson bridge/device quirks: bridge class correction, always-on/non-compliant system bus BARs, MRRS limits, interrupt pin correction, and an MSI enable quirk.

## Important APIs, types, and functions
`struct loongson_pci_data` describes controller capabilities with flags and `pci_ops`; `struct loongson_pci` stores CFG0/CFG1 bases and match data. `FLAG_CFG0`, `FLAG_CFG1`, `FLAG_DEV_FIX`, and `FLAG_DEV_HIDDEN` drive config window selection and device filtering. `cfg0_map()` and `cfg1_map()` build MMIO addresses for standard and extended config space; CFG1 supports extended config by folding high offset bits into the window address. `pci_loongson_map_bus()` enforces root/child visibility quirks and selects CFG0 for standard config or CFG1 for extended config.

The file registers many PCI fixups with `DECLARE_PCI_FIXUP_*`. `bridge_class_quirk()` changes Loongson PCIe ports to normal PCI bridge class. `system_bus_quirk()` marks selected internal devices with `mmio_always_on` and `non_compliant_bars`. `loongson_mrrs_quirk()` sets `pci_host_bridge.no_inc_mrrs`; on MIPS, `loongson_set_min_mrrs_quirk()` walks upstream bridges and clamps endpoint MRRS to 256 bytes under affected ports. `loongson_pci_pin_quirk()` derives interrupt pins from the function number, and `loongson_pci_msi_quirk()` explicitly enables MSI on a host bridge class device.

## Control flow
For OF builds, `loongson_pci_probe()` allocates a host bridge, loads match data, maps CFG0 and/or CFG1 resources according to flags, sets `bridge->sysdata`, installs the selected ops, sets `bridge->map_irq` to `loongson_map_irq()`, and calls `pci_host_probe()`. The OF match table supports `loongson,ls2k-pci`, `loongson,ls7a-pci`, and `loongson,rs780e-pci`; LS2K/LS7A use CFG1 and generic 8/16/32-bit config operations, while RS780E uses CFG0 and 32-bit-only config operations.

For ACPI builds, `loongson_pci_ecam_init()` allocates private data behind `struct pci_config_window`, marks CFG1 plus hidden-device filtering, and derives `cfg1_base` from the ECAM window and bus start. `loongson_pci_ecam_ops` then exposes `pci_loongson_map_bus()` through the standard ECAM interface.

## State and persistence behavior
The driver stores only mapped config-window bases and per-controller flags. PCI fixups mutate in-memory PCI core device state such as class, BAR compliance flags, MRRS policy, pin, and MSI capability flags. There is no disk persistence and no explicit remove path for the builtin platform driver.

## Dependencies and integration points
The file integrates with OF host bridge probing, ACPI ECAM, generic PCI config accessors, Loongson PCI IDs, IRQ mapping through `of_irq_parse_and_map_pci()`, legacy i8259 interrupt-line fallback, and the PCI fixup framework. It also depends on arch behavior: the MRRS clamp is compiled only for MIPS, while ACPI ECAM support is separately guarded.

## Risks and edge cases
Visibility filtering is important: `FLAG_DEV_FIX` suppresses extra devices behind non-root buses, and `FLAG_DEV_HIDDEN` avoids root functions that should not exist. A wrong flag set can make devices disappear or make invalid config cycles. CFG1 mapping is optional on OF probe; if absent, standard CFG0 may still be unavailable depending on the compatible data. `loongson_pci_msi_quirk()` assumes the target host bridge path has a valid MSI capability offset. MRRS behavior differs between firmware quality levels and architectures.

## Test signals
Test coverage should include OF boot on LS2K/LS7A/RS780E, ACPI ECAM boot, standard and extended config-space access, hidden-device filtering on root bus slots/functions, child-bus single-device filtering, bridge class fixups, internal system-bus BAR behavior, i8259 fallback IRQ mapping, MRRS clamp on MIPS, and MSI behavior on LS7A port 5.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-loongson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-mvebu.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-mvebu.c

## Purpose
`pci-mvebu.c` is the PCIe controller driver for Marvell Armada 370/XP, Dove, and Kirkwood style SoCs. It models multiple hardware PCIe ports as root-port devices on a virtual bus 0, emulates bridge config space for those root ports, routes child config cycles to the correct hardware port, programs MBus address windows for PCI memory and I/O forwarding, manages legacy INTx domains, and handles port power/reset/clock lifecycles.

## Important APIs, types, and functions
`struct mvebu_pcie` stores global controller state, resource apertures, and the array of ports. `struct mvebu_pcie_port` stores per-port MMIO base, port/lane identity, devfn, MBus target/attribute values, clock/reset GPIO, emulated bridge, DT node, current memory/I/O windows, saved status, slot power limit, INTx domain, lock, and IRQ.

Hardware setup functions include `mvebu_pcie_setup_hw()`, which enables root-complex mode, fixes link width, disables command bits, changes the class code to PCI bridge, sets DRAM decode windows, programs slot power limit messaging, and masks/clears interrupts. `mvebu_pcie_setup_wins()` and `mvebu_pcie_disable_wins()` manage BAR/window registers for DRAM and internal-register access. `mvebu_pcie_child_rd_conf()` and `mvebu_pcie_child_wr_conf()` issue hardware config cycles for downstream devices after finding the owning port and checking link state.

Bridge emulation is provided by `pci-bridge-emul`. `mvebu_pci_bridge_emul_*_read()` and `*_write()` expose command, bus number, bridge control, PCIe capability, slot control/status, root status, and AER registers while translating selected writes into hardware side effects. `mvebu_pcie_handle_iobase_change()` and `mvebu_pcie_handle_membase_change()` convert emulated bridge window registers into MBus windows through `mvebu_pcie_set_window()`.

IRQ support is implemented with `mvebu_pcie_init_irq_domain()`, `mvebu_pcie_irq_handler()`, `mvebu_pcie_intx_irq_mask()`, and `mvebu_pcie_intx_irq_unmask()`. Each port can expose a four-entry INTx domain under a child interrupt-controller node; old bindings without a named `intx` interrupt fall back to unmasking all INTx bits in hardware.

## Control flow
Probe allocates a host bridge, parses/request global PCI memory and I/O apertures from MBus helper APIs, counts available child DT nodes, parses each port child, then powers up and maps only successfully parsed ports. Per-port parsing requires `marvell,pcie-port`, a valid devfn with function zero, MEM target/attribute information from parent ranges, optional I/O target/attribute, optional named `intx`, optional reset GPIO and delay, slot power limit, and a clock.

For each active port, probe enables the clock/reset sequence, maps registers, initializes bridge emulation, creates the INTx domain and chained handler when available, programs hardware, and sets local device/bus numbers to support the driver's virtual bus-0 topology. Finally it installs root `pci_ops` for emulated root ports, child ops for downstream config cycles, resource alignment, IRQ mapping, and calls `pci_host_probe()`.

Remove stops and removes the root bus, disables command bits and interrupts, removes chained handlers and IRQ domains, cleans up bridge emulation, disables slot power limit messaging, clears hardware windows, deletes any dynamically created MBus windows, and powers down each port. Suspend saves `PCIE_STAT_OFF`; resume restores it and reruns hardware setup for each mapped port.

## State and persistence behavior
The driver maintains per-port current `memwin` and `iowin` state to avoid redundant MBus reprogramming and to delete old windows before installing new ones. Bridge config state lives in the emulation buffers and is partially synchronized to hardware. Hardware state includes root-complex mode, link capability width, BAR/window registers, interrupt masks, slot power limit, local bus/device numbers, and saved status across system sleep. There is no disk persistence.

## Dependencies and integration points
The driver depends on DT child-node topology, `of_pci_get_devfn()`, MBus aperture/window APIs, `pci-bridge-emul`, common PCI host bridge probing, GPIO descriptors for PERST, clocks, IRQ domains/chained IRQ handling, and generic PCI resource assignment. It exports no MSI domain; MSI support would be through platform facilities outside this file, while legacy INTx is handled here.

## Risks and edge cases
The topology is intentionally nonstandard: multiple independent host bridges are presented as bridges on one virtual bus 0 for compatibility with historical DT bindings. Routing errors in `mvebu_pcie_find_port()` or bus-number emulation can break config access. Window changes are not atomic; `mvebu_pcie_set_window()` deletes old windows before adding new ones. MBus windows require power-of-two splits and alignment, so resource alignment is critical. Old DTs without `intx` cannot mask individual INTx lines and may incur shared-interrupt overhead. Partial port failures are skipped, so systems can boot with fewer active ports than described.

## Test signals
Validation should cover Armada/Dove/Kirkwood DT variants, x1 and x4 links, absent/down links, root-port bridge config reads/writes, child config access, memory and I/O window assignment and teardown, non-power-of-two BAR sizes, INTx domain mapping and mask/unmask, old DT fallback interrupts, reset GPIO timing, slot power limit programming, suspend/resume link recovery, and hot remove/module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-mvebu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-rcar-gen2.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-rcar-gen2.c

## Purpose
`pci-rcar-gen2.c` supports the internal PCI bus on Renesas R-Car Gen2 and related RZ/N1 SoCs. The controller is used for built-in PCI USB host blocks rather than a general external PCIe hierarchy. It allocates a PCI host bridge, maps controller registers, configures AHB-to-PCI and PCI-to-AHB windows, enables PCI interrupts, optionally installs a debug error IRQ handler, and exposes limited config-space access for the host bridge and built-in devices.

## Important APIs, types, and functions
`struct rcar_pci` stores the device, register base, memory resource for the built-in device window, config resource, and IRQ. `rcar_pci_cfg_base()` implements config mapping for `pci_generic_config_read/write`: it rejects non-root buses, nonzero functions, slots above 2, and host-bridge config offsets at or above 0x40, then programs `RCAR_AHBPCI_WIN1_CTR_REG` for host or device config access and returns the appropriate MMIO offset.

`rcar_pci_setup()` performs the main hardware initialization. It selects a PCI-AHB window from `dma-ranges` or defaults to a 1 GiB window at `0x40000000`, enables runtime PM, reads the unit revision, asserts and deasserts USB/PLL reset bits, configures the window size, programs AHB master/slave mode, enables the PCI arbiter, sets PCI-AHB and AHB-PCI mappings, writes BAR0/BAR1 for the bridge communication area and PCI-AHB window, enables PCI command bits, and enables INT A/B/PME. With `CONFIG_PCI_DEBUG`, `rcar_pci_setup_errirq()` requests a shared error IRQ and unmasks controller error bits handled by `rcar_pci_err_irq()`.

## Control flow
`rcar_pci_probe()` allocates a host bridge and private state, maps the first MMIO resource as controller/config registers, obtains a second MMIO resource for the device memory area, validates that the second resource starts on a 64 KiB boundary, fetches the platform IRQ, installs `rcar_pci_ops`, sets `PCI_REASSIGN_ALL_BUS`, calls `rcar_pci_setup()`, and finally invokes `pci_host_probe()`. The builtin platform driver matches several Renesas compatible strings and suppresses bind attributes.

## State and persistence behavior
The driver stores only the mapped register base, resource copies, and IRQ in memory. Hardware state is programmed in controller registers for resets, bridge windows, arbiter, AHB bus mode, BARs, command bits, and interrupt enables. Runtime PM is enabled and acquired during setup, but there is no matching remove/suspend/resume logic in this file. No disk state is persisted.

## Dependencies and integration points
The driver depends on OF platform resources, generic PCI host bridge probing, runtime PM, generic PCI config accessors, resource lists for `dma_ranges`, and the Renesas AHB-PCI bridge register layout. It integrates with the PCI core through a simple `pci_ops` map function and `pci_host_probe()`, and with the IRQ subsystem only for optional debug error reporting.

## Risks and edge cases
The config mapper intentionally exposes only root bus slots 0-2 and function 0, so any unexpected topology is invisible. The host bridge only exposes config registers below 0x40. Unknown DMA window sizes silently default to 256 MiB after warning, which may mask firmware mistakes. `pm_runtime_get_sync()` is not checked for failure and has no visible balanced put in this driver. The second MMIO resource must be 64 KiB aligned; otherwise probe fails. Error IRQ coverage exists only with `CONFIG_PCI_DEBUG`.

## Test signals
Good tests include probing each compatible SoC, config-space reads for slots 0-2 and rejection of unsupported buses/functions/offsets, DMA window sizes of 256 MiB/512 MiB/1 GiB/2 GiB plus unknown-size fallback, reset sequencing, BAR/window programming, PCI reassignment behavior, built-in OHCI/EHCI enumeration, INT A/B/PME delivery, optional debug error IRQ handling, and runtime-PM behavior during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-rcar-gen2.c -->
