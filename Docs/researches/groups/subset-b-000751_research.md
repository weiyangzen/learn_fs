# subset-b-000751 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm63xx.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm63xx.c

### Purpose
This file initializes Broadcom BCM63xx PCI or PCIe host support during early MIPS boot. It exposes the `bcm63xx_pci_enabled` runtime gate, builds `pci_controller` instances for conventional PCI, optional CardBus, and PCIe, programs host bridge address windows, resets PCIe SERDES/core blocks, and registers the selected controller with the MIPS PCI core.

### Important APIs, Types, And Functions
Key state includes `bcm63xx_controller`, optional `bcm63xx_cb_controller`, `bcm63xx_pcie_controller`, `pci_iospace_start`, and the private `pcie_clk`. `bcm63xx_int_cfg_readl()` and `bcm63xx_int_cfg_writel()` perform host bridge internal config cycles through MPI config registers. `bcm63xx_register_pci()` configures legacy PCI/CardBus windows and bus-mastering BARs. `bcm63xx_register_pcie()` enables the PCIe clock, resets the link, programs bridge options, and registers PCIe resources. `bcm63xx_pci_init()` dispatches by CPU ID.

### Control Flow
The `arch_initcall()` first checks `bcm63xx_pci_enabled`; disabled boards return `-ENODEV`. BCM6328/6362 use PCIe setup, while BCM3368/6348/6358/6368 use legacy PCI. Legacy PCI maps four bytes of I/O space for configuration cycles, sets local-to-PCI memory and I/O windows, configures CardBus IDSEL if enabled, programs PCI-to-local RAM remaps for DMA, clears host retry limits, enables memory/master bits, enables prefetching, and registers controllers. PCIe enables clocks, resets core and external reset lines with delays, configures bridge endian/BE handling, interrupt masks, class code, BAR0 remap, and registers the PCIe controller.

### State, Persistence, And Dependencies
All state is boot-time MMIO configuration plus static resources. Dependencies are BCM63xx CPU ID/revision helpers, MPI/MISC/PCMCIA/PCIe register accessors, reset control, clock framework, PCI controller registration, and constants from `pci-bcm63xx.h`. Persistent effects are hardware windows, reserved PCI I/O memory, and registered PCI buses.

### Integration Points
The file integrates BCM63xx board NVRAM policy through `bcm63xx_pci_enabled`, ops from `ops-bcm63xx.c`, optional CardBus support, and generic MIPS `register_pci_controller()`. Device enumeration, resource assignment, and IRQ mapping are handled by the common PCI layer and platform fixups after registration.

### Risks
The legacy path notes a real SMP hazard: config cycles temporarily remap the first four bytes of I/O space, so concurrent I/O can collide. Memory-size and old BCM6348 revision handling can restrict DMA. PCIe assumes clock and reset names are present. Wrong resource constants or CardBus IDSEL overlap can make devices invisible or corrupt config cycles.

### Test Signals
Useful signals are boot logs showing selected PCI/PCIe path, successful config-space reads, correct resource windows, working DMA from PCI devices, CardBus enumeration when configured, and absence of master/target aborts under concurrent I/O stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm63xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm63xx.h -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm63xx.h

### Purpose
This header provides BCM63xx PCI support declarations shared by the platform setup file and low-level PCI ops. It centralizes CardBus IDSEL policy, PCIe bus-number constants, external PCI ops declarations, and the shared I/O-space remap pointer.

### Important APIs, Types, And Functions
It defines `CARDBUS_PCI_IDSEL`, `PCIE_BUS_BRIDGE`, and `PCIE_BUS_DEVICE`. It declares `bcm63xx_pci_ops`, `bcm63xx_cb_ops`, `bcm63xx_pcie_ops`, and `pci_iospace_start`.

### Control Flow
There is no runtime control flow. The definitions influence how `pci-bcm63xx.c` registers controllers and how `ops-bcm63xx.c` forms config accesses.

### State, Persistence, And Dependencies
The header depends on BCM63xx CPU, I/O, register, and PCI device definitions. `pci_iospace_start` is initialized by the legacy PCI setup path and consumed by config ops.

### Integration Points
It is the contract between host-controller resource setup and config-space operations. CardBus support depends on reserving an otherwise normal PCI IDSEL value.

### Risks
Changing `CARDBUS_PCI_IDSEL` can conflict with real boards. Mismatched PCIe bus constants would break bridge/device config targeting.

### Test Signals
Build coverage with and without `CONFIG_CARDBUS`, plus PCIe config reads on BCM6328/6362 and legacy PCI config reads on older SoCs, validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm63xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-generic.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-generic.c

### Purpose
This file supplies generic MIPS PCI BIOS helpers for systems using the newer generic host-bridge path. It aligns resources, fixes up bridge bus resources, and optionally remaps I/O space.

### Important APIs, Types, And Functions
`pcibios_align_resource()` handles ISA-style I/O mirroring avoidance and delegates to a host bridge `align_resource` hook or generic `pci_align_resource()`. `pcibios_fixup_bus()` reads bridge bases. Under `pci_remap_iospace`, `pci_remap_iospace()` maps a physical I/O range and calls `set_io_port_base()`.

### Control Flow
Resource alignment first rounds I/O starts out of mirrored 0x100-0x3ff modulo ranges. It then finds the host bridge for the device and delegates when available. Memory resources use generic PCI alignment. I/O remapping accepts only a zero-based resource and installs the mapped virtual base globally.

### State, Persistence, And Dependencies
State effects are the global MIPS I/O port base and resource start choices made during PCI assignment. Dependencies are Linux PCI host-bridge helpers, `ioremap()`, and MIPS I/O-port base support.

### Integration Points
The file is used by generic PCI drivers such as `PCI_DRIVERS_GENERIC` systems. It complements platform files that register host bridges using standard Linux PCI APIs rather than legacy `pci_controller`.

### Risks
`pci_remap_iospace()` rejects nonzero I/O resource starts, so device-tree ranges must match this assumption. Resource alignment can surprise devices expecting dense I/O packing.

### Test Signals
Check assigned I/O BARs avoid mirrored ranges, host-specific alignment callbacks run when installed, and `pci_remap_iospace()` produces working inb/outb access for generic host bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ip27.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-ip27.c

### Purpose
This SGI IP27/IP29 support file provides NUMA node mapping for PCI buses and a final IOC3 fixup needed to enable an ethernet PHY on specific IP29 system boards.

### Important APIs, Types, And Functions
With `CONFIG_NUMA`, `pcibus_to_node()` returns the `bridge_controller` NASID and is exported. `ip29_fixup_phy()` reads the IOC3 subsystem ID and writes the remote hub LED register for matching IP29 system board devices. `DECLARE_PCI_FIXUP_FINAL()` binds the fixup to SGI IOC3 devices.

### Control Flow
During PCI final fixups, IOC3 devices call `ip29_fixup_phy()`. The function exits unless the bus is on NASID 1, then reads `PCI_SUBSYSTEM_VENDOR_ID` and enables the PHY only for `IOC3_SUBSYS_IP29_SYSBOARD`.

### State, Persistence, And Dependencies
The persistent effect is a remote hub register write through `REMOTE_HUB_S()`. Dependencies are SGI SN address, hub, IOC3, and bridge-controller definitions.

### Integration Points
The file works with `pci-xtalk-bridge.c`, which creates `bridge_controller` instances, and with Linux PCI fixup infrastructure.

### Risks
The fixup is board-specific and assumes NASID 1 is the second module requiring the PHY action. Incorrect subsystem-ID emulation in bridge code would suppress or misapply it.

### Test Signals
On IP29 hardware, check IOC3 ethernet link/PHY availability on the second module and confirm `pcibus_to_node()` reports expected NASIDs under NUMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ip27.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ip32.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-ip32.c

### Purpose
This file initializes the SGI O2/IP32 MACE PCI host bridge, installs an error interrupt handler, sets global I/O and memory resource bounds, and registers the MACE PCI controller.

### Important APIs, Types, And Functions
`macepci_error()` decodes MACE PCI error bits for master/target aborts, parity, retry, illegal command, SERR, overrun, and interrupt-test conditions, then clears handled bits. Static resources define 32-bit and 64-bit memory windows. `mace_pci_controller` binds external `mace_pci_ops` to resources. `mace_init()` performs boot setup.

### Control Flow
At `arch_initcall()`, `mace_init()` sets `PCIBIOS_MIN_IO`, clears error address/status, enables bridge error interrupts, logs revision, requests `MACE_PCI_BRIDGE_IRQ`, extends global resource limits, and calls `register_pci_controller()`. Later errors are reported by the IRQ handler.

### State, Persistence, And Dependencies
State lives in MACE MMIO registers and global PCI resources. Dependencies include IP32 MACE register definitions, interrupt constants, generic MIPS PCI controller registration, and `mace_pci_ops`.

### Integration Points
This file provides the host-controller registration; platform IRQ fixup and config operations are elsewhere. It integrates with the generic PCI scan after controller registration.

### Risks
`BUG_ON(request_irq())` panics if the bridge error IRQ cannot be installed. Error handling only logs and clears bits; some conditions may warrant stronger recovery. Resource ranges differ materially between 32-bit and 64-bit builds.

### Test Signals
Boot should print the MACE PCI revision, enumerate O2 PCI devices, and log bridge errors when forced by bad config/MMIO cycles without hanging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ip32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-lantiq.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-lantiq.c

### Purpose
This file implements the Lantiq XWAY PCI host controller platform driver. It maps PCI controller registers and config space, enables clocks, programs FCI/PCI address windows and arbitration, handles reset GPIO, loads device-tree ranges, and registers a legacy MIPS `pci_controller`.

### Important APIs, Types, And Functions
State includes `ltq_pci_mapped_cfg`, `ltq_pci_membase`, `reset_gpio`, `clk_pci`, `clk_external`, `pci_io_resource`, and `pci_mem_resource`. `ltq_calc_bar11mask()` computes the host BAR mask from system RAM size. `ltq_pci_startup()` performs hardware initialization. `ltq_pci_probe()` maps resources, starts hardware, loads OF ranges, and registers the controller. `pcibios_init()` registers the platform driver.

### Control Flow
Probe clears `PCI_PROBE_ONLY`, maps resource 1 as controller MMIO and resource 0 as config space, then calls startup. Startup obtains PCI and external clocks, optionally applies `lantiq,bus-clock`, enables or disables the external clock per DT, gets optional reset GPIO, enables PCI/EBU switching, enables bus-master/IO/memory bits in config space, programs request masks, address maps, BAR masks, endian swap, burst length, EBU IRQ routing, and toggles reset.

### State, Persistence, And Dependencies
Persistent state is in Lantiq PCI/CGU/EBU registers, clock state, reset line state, and registered PCI resources. Dependencies include Lantiq SoC MMIO helpers, Lantiq IRQ/EBU constants, OF PCI range parsing, GPIO descriptors, and config ops declared in `pci-lantiq.h`.

### Integration Points
The driver matches `"lantiq,pci-xway"` device-tree nodes and uses `pci_load_of_ranges()` from the legacy MIPS PCI code. Config access comes from Lantiq-specific ops in another source file.

### Risks
Startup errors after clock acquisition are not fully unwound. `ltq_pci_probe()` ignores the return value of `ltq_pci_startup()`, so failed GPIO or clock setup may still lead to registration. BAR mask calculation assumes a power-of-two memory envelope derived from `get_num_physpages()`.

### Test Signals
Device-tree boot should bind `pci-xway`, show correct ranges in `/proc/iomem`, enumerate PCI devices, observe reset GPIO toggling, and show working config reads through `ltq_pci_mapped_cfg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-lantiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-lantiq.h -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-lantiq.h

### Purpose
This header defines the shared contract between the Lantiq PCI platform driver and its config-space access implementation.

### Important APIs, Types, And Functions
It declares the global config mapping `ltq_pci_mapped_cfg` and the config access callbacks `ltq_pci_read_config_dword()` and `ltq_pci_write_config_dword()`.

### Control Flow
No control flow exists here. The declarations allow `pci-lantiq.c` to build a `struct pci_ops` before the functions are linked from the low-level operations file.

### State, Persistence, And Dependencies
`ltq_pci_mapped_cfg` must be initialized by `ltq_pci_probe()` before any config operations are used. The header depends on Linux PCI type declarations through including translation units.

### Integration Points
It connects Lantiq device-tree probing and generic PCI enumeration with config-space read/write routines.

### Risks
If config ops run before probe maps `ltq_pci_mapped_cfg`, config cycles will dereference an invalid mapping. The function names imply dword access even though PCI core may request byte and word sizes.

### Test Signals
A successful boot should show config reads after resource mapping, and build tests should catch missing ops definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-lantiq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-legacy.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-legacy.c

### Purpose
This is the core legacy MIPS PCI framework for platforms that register `struct pci_controller` objects. It queues controllers, requests their resources, scans buses, assigns or claims resources, handles OF ranges, and provides PCI BIOS hooks.

### Important APIs, Types, And Functions
Important state includes the private `controllers` list, `pci_initialized`, and `pci_scan_mutex`. Public functions include `pci_address_to_pio()`, `pcibios_align_resource()`, `pci_load_of_ranges()`, `pcibios_get_phb_of_node()`, `register_pci_controller()`, `pcibios_enable_device()`, `pcibios_fixup_bus()`, and `pcibios_setup()`. `pcibios_scanbus()` performs the actual root-bus allocation and enumeration.

### Control Flow
Platform code calls `register_pci_controller()`, which requests memory and I/O resources, appends the hose to the list, and immediately scans if the subsystem has already initialized. `subsys_initcall(pcibios_init)` scans all queued controllers. Scanning builds a `pci_host_bridge`, attaches resource windows with offsets, sets sysdata, bus number, ops, swizzle and IRQ callbacks, scans the root bus, assigns or claims resources depending on `PCI_PROBE_ONLY`, configures child PCIe settings, and adds devices.

### State, Persistence, And Dependencies
Persistent kernel state includes registered host bridges, resource-tree entries, bus numbers, and PCI devices. OF support stores the controller node and maps I/O ranges. Dependencies include Linux PCI host-bridge helpers, MIPS `struct pci_controller`, platform `pcibios_map_irq()` and `pcibios_plat_dev_init()`, and optional platform `pcibios_plat_setup`.

### Integration Points
Most legacy platform files in this subset call `register_pci_controller()` or `pci_load_of_ranges()`. It is the bridge from MIPS board-specific setup to generic Linux PCI enumeration.

### Risks
Resource conflicts silently skip bus scans after warnings. `need_domain_info` is global and becomes sticky after bus-number overflow or nonzero domain use. Late controller registration is serialized but still depends on platform resources being complete.

### Test Signals
Validate multiple controllers, `PCI_PROBE_ONLY` versus assignment modes, OF range loading, domain numbering after bus number wrap, and resource-conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-malta.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-malta.c

### Purpose
This file initializes PCI resources for MIPS Malta-family boards using GT-64120, Bonito64, or MSC/SoC-it controllers. It derives memory and I/O windows from controller registers, fixes controller quirks, and registers the selected `pci_controller`.

### Important APIs, Types, And Functions
Static resources/controllers exist for Bonito64, GT-64120, and MSC. External ops are `bonito64_pci_ops`, `gt64xxx_pci0_ops`, and `msc_pci_ops`. The single entry point `mips_pcibios_init()` selects the controller using `mips_revision_sconid`.

### Control Flow
For GT-64120, the function writes the controller BAR for internal registers, reads memory and I/O decode/remap registers, picks the widest memory window, validates remap masks, and computes offsets. Bonito combines adjacent PCIMAP windows. MSC reads system-controller memory and I/O windows, configures IOCU GCR regions when available, and trims overlapping memory/I/O ranges. All supported controllers set `PCIBIOS_MIN_IO`, adjust global resources, set `io_map_base`, and register the controller.

### State, Persistence, And Dependencies
State is controller hardware register programming, resource window fields, IOCU GCR configuration, and PCI controller registration. Dependencies include Malta board revision IDs, GT64120/Bonito/MSC register APIs, MIPS CPS IOCU support, and legacy PCI core.

### Integration Points
Board setup calls `mips_pcibios_init()` after determining the system controller. Config-space ops are provided by controller-specific files.

### Risks
The code panics with `BUG_ON()` for unsupported discontiguous remaps. It collapses multi-window hardware into one resource, potentially losing usable apertures. Incorrect controller ID detection means no PCI registration.

### Test Signals
Boot on each controller type, inspect computed resource ranges/offsets, enumerate behind bridges, and validate DMA coherency with IOCU-enabled systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-malta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-mt7620.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-mt7620.c

### Purpose
This file implements PCIe host support for Ralink/MediaTek MT7620A, MT7628AN, and MT7688 SoCs. It programs PCIe PHY sequences, resets and clocks the controller, checks link presence, implements config-space ops, maps interrupts, and registers the host controller.

### Important APIs, Types, And Functions
Global mappings include `bridge_base`, `pcie_base`, and reset control `rstpcie0`. Helpers `bridge_w32/r32/m32`, `pcie_w32/r32/m32`, `pcie_phyctrl_set()`, `wait_pciephy_busy()`, and `pcie_phy()` abstract register access. `pci_config_read()` and `pci_config_write()` implement `mt7620_pci_ops`. Hardware setup is split between `mt7620_pci_hw_init()` and `mt7628_pci_hw_init()`. `mt7620_pci_probe()`, `pcibios_map_irq()`, and `pcibios_plat_dev_init()` are the platform-facing hooks.

### Control Flow
Probe obtains reset control and maps bridge/PCIe resources, broadens global resource limits, resets the controller, enables clock, asserts PERST, selects a SoC-specific PHY init path, waits, deasserts PERST, and checks `PCIE_LINK_UP_ST`. If no card is present, it disables reset/clock/PHY. With a link, it programs MEM/IO bases, BAR0, class, interrupts, SDK-derived config tweaks, loads OF ranges, and registers the controller. IRQ mapping treats bus 1 slot 0 as the endpoint and bus 0 slot 0 as the root complex.

### State, Persistence, And Dependencies
State is SoC sysc clock/reset bits, PCIe PHY registers, root-complex config registers, global I/O mapping, and registered PCI controller resources. Dependencies include Ralink register helpers, reset framework, OF PCI ranges, delays, and `ralink_soc` identification.

### Integration Points
The driver matches `"mediatek,mt7620-pci"` DT nodes and relies on Ralink SoC initialization to set `ralink_soc`. It plugs into legacy MIPS PCI enumeration and common `pcibios_map_irq()`.

### Risks
Several failures return `-1` rather than standard errno. `pci_config_read/write()` do not reject invalid sizes explicitly. SDK "voodoo" PHY/config sequences are board-sensitive. No-card detection disables the controller, so marginal links can prevent enumeration.

### Test Signals
Boot with MT7620A and MT7628/MT7688 hardware, verify link-up and no-card paths, config access to bus 1 slot 0, assigned IRQ 4, OF resource ranges, and endpoint DMA/interrupt functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-mt7620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-octeon.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-octeon.c

### Purpose
This file initializes legacy PCI/PCI-X host mode on Cavium Octeon systems without PCIe. It configures Octeon NPI PCI controller registers, DMA BAR mappings, config-space access, board-specific interrupt routing, platform PCI device setup, EDAC device registration, and PCI DMA initialization.

### Important APIs, Types, And Functions
Global state includes `octeon_bar1_pci_phys`, `octeon_pcibios_map_irq`, and `octeon_dma_bar_type`. `union octeon_pci_address` encodes Octeon PCI config/I/O/MEM addresses. `pcibios_map_irq()` delegates to the selected Octeon mapper. `pcibios_plat_dev_init()` sets cache line, latency, parity/SERR, bridge controls, PCIe/AER reporting where present, and clears AER status. `octeon_get_pci_interrupts()` and `octeon_pci_pcibios_map_irq()` implement board IRQ mapping. `octeon_read_config()`/`octeon_write_config()` provide `pci_ops`. `octeon_pci_initialize()` and `octeon_pci_setup()` perform host bring-up.

### Control Flow
`octeon_pci_setup()` exits on PCIe-capable chips or endpoint mode, selects small or big DMA BAR mode, sets I/O port base, initializes the PCI controller, programs memory access endian/snoop attributes, remaps BAR2, configures BAR0/BAR1 differently for big versus small BAR modes, fills BAR1 index registers, sets device memory aperture, registers the controller, clears pending errors, registers `octeon_pci_edac`, and calls `octeon_pci_dma_init()`.

### State, Persistence, And Dependencies
Persistent state is extensive CSR/NPI hardware configuration, PCI resource windows, BAR mappings, global IRQ-mapping function pointer, and DMA translation mode. Dependencies include Octeon model/feature detection, CVMX NPI/PCI register unions, board type data, SWIOTLB for small BAR mode, platform device registration, and generic PCI/AER helpers.

### Integration Points
It shares `octeon_pcibios_map_irq` and `octeon_dma_bar_type` with `pcie-octeon.c`, while serving only non-PCIe chips. It integrates with EDAC through a simple platform device and with the common MIPS PCI core through `register_pci_controller()`.

### Risks
Hardware programming is highly model- and pass-specific. The AER section appears to test ECRC capability against the wrong local variable after reading `PCI_ERR_CAP`, so ECRC enablement deserves review. Big/small BAR setup must match DMA constraints or bus mastering can target unmapped memory.

### Test Signals
Validate host-mode detection, PCI/PCI-X status and clock logs, board-specific IRQ routing, config reads/writes, DMA under big and small BAR modes, EDAC device creation, and absence of pending NPI PCI errors after scan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-rc32434.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-rc32434.c

### Purpose
This file sets up the IDT RC32434 PCI host controller, including resource windows, byte/word/dword config-space access helpers, interrupt mapping, and platform device initialization.

### Important APIs, Types, And Functions
The file defines PCI access mode constants and macros for config address construction. `config_access()` is the core config-cycle routine. Typed helpers read and write byte, word, and dword values, and `pci_config_read()`/`pci_config_write()` expose them as `rc32434_pci_ops`. Static resources and the controller describe host memory/I/O windows. Platform hooks include `pcibios_map_irq()` and `pcibios_plat_dev_init()`.

### Control Flow
Config reads/writes form a bus/slot/function/register address, issue the controller access, and merge sub-dword writes into surrounding dwords. Controller initialization programs host windows and calls `register_pci_controller()` during boot. IRQ mapping derives platform interrupt lines for known device slots.

### State, Persistence, And Dependencies
State consists of RC32434 PCI controller registers, static resources, and the registered controller. Dependencies are RC32434 register definitions, PCI core types, and legacy MIPS controller infrastructure.

### Integration Points
This controller participates in the same legacy `register_pci_controller()` scan path as other non-OF MIPS PCI hosts.

### Risks
Sub-dword config writes depend on correct read-modify-write behavior and alignment checks. Unsupported slot/function probing should return master-abort-like results rather than corrupting controller state.

### Test Signals
Config read/write width tests, slot IRQ mapping, resource window visibility, and device enumeration on RC32434 boards are the most useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-rc32434.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-rt2880.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-rt2880.c

### Purpose
This file implements PCI host support for Ralink RT288x SoCs. It maps controller registers, implements config-space read/write, configures bridge windows and IDs, maps the single external PCI IRQ, and registers the controller from a platform driver.

### Important APIs, Types, And Functions
The file uses `rt2880_pci_base`, register access helpers, `rt2880_pci_get_cfgaddr()`, `rt2880_pci_config_read()`, `rt2880_pci_config_write()`, `rt2880_pci_read_u32()`, and `rt2880_pci_write_u32()`. `rt2880_pci_ops` and `rt2880_pci_controller` describe controller operations/resources. `rt288x_pci_probe()` performs setup. `pcibios_map_irq()` and `pcibios_plat_dev_init()` provide platform hooks.

### Control Flow
Probe maps controller and I/O space, installs the I/O port base, sets global I/O resource limits, initializes bridge config, arbitration, BAR0, memory and I/O bases, IDs/class/subsystem IDs, interrupt mask, root BAR0, records the OF node, and registers the controller. During device enable, `pcibios_plat_dev_init()` lazily initializes slot 0 BAR0 and command bits once because generic PCI does not do it for this platform.

### State, Persistence, And Dependencies
State is in MMIO registers, `rt2880_pci_controller.io_map_base`, global I/O port base, and a static `slot0_init` guard. Dependencies include Ralink RT288x register constants, OF platform matching, and legacy MIPS PCI.

### Integration Points
The driver matches `"ralink,rt288x-pci"`. It cooperates with Ralink SoC init and uses `RT288X_CPU_IRQ_PCI` for slot 0x11 devices.

### Risks
Unknown slots call `BUG()`, making unexpected hardware fatal. `ioremap()` failures are not checked. Slot 0 special initialization is deferred until another device is enabled, which is fragile if enumeration order changes.

### Test Signals
Boot with RT288x PCI endpoints, verify root BAR0 programming, IRQ assignment for slot 0x11, correct config access widths, and no crash when only expected slots exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-rt2880.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-rt3883.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-rt3883.c

### Purpose
This file implements the RT3662/RT3883 combined PCI/PCIe host controller. It detects desired PCI/PCIe mode from device-tree children, initializes clocks/resets, implements config access, creates a PCI interrupt domain, configures bridge BARs, and registers a legacy PCI controller.

### Important APIs, Types, And Functions
`struct rt3883_pci_controller` holds MMIO base, interrupt-controller node/domain, resources, embedded `pci_controller`, and `pcie_ready`. Helpers read/write controller registers and config space. IRQ support includes `rt3883_pci_irq_handler()`, mask/unmask methods, `rt3883_pci_irq_map()`, and `rt3883_pci_irq_init()`. Hardware setup is in `rt3883_pci_preinit()` and `rt3883_pci_probe()`.

### Control Flow
Probe allocates controller state, maps MMIO, locates interrupt-controller and PCI host child nodes, inspects child PCI devfn slots to decide PCI, PCIe, or both, runs preinit to reset/clock selected blocks and verify PCIe link, fills PCI ops/resources, loads OF ranges, programs MEM/IO bases and root-complex identity/class registers, creates an IRQ domain, enables command bits for PCIe and PCI root functions, adjusts BAR/P2P bridge registers depending on mode, and registers the controller.

### State, Persistence, And Dependencies
State persists in controller registers, sysc reset/clock registers, IRQ domain mappings, OF node references, `pcie_ready`, and PCI resources. Dependencies include RT3883 sysc register definitions, irqdomain APIs, OF PCI parsing, and legacy PCI core.

### Integration Points
The driver matches `"ralink,rt3883-pci"` and maps PCI IRQs with `of_irq_parse_and_map_pci()`. It can expose conventional PCI slots, PCIe slot, or both based on DT topology.

### Risks
OF child references must be released on error; the success path relies on device lifetime. Config access to bus 1 is blocked when PCIe link is absent. Mode detection depends on child slots matching expected devfn values. Interrupt handling processes all pending bits but spurious handling may hide masking bugs.

### Test Signals
Test PCI-only, PCIe-only, and combined modes; verify PCIe no-link disables access cleanly; confirm child interrupt domain mappings and OF IRQ parsing; enumerate devices behind the P2P bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-rt3883.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-sb1250.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-sb1250.c

### Purpose
This file provides Broadcom/Sibyte SB1250 PCI/LDT host glue. It maps configuration and I/O spaces, detects whether firmware enabled the PCI/LDT buses, implements config access with device-mode filtering, sets resource limits, registers the controller, and optionally takes over VGA console.

### Important APIs, Types, And Functions
Important state includes `cfg_space`, `sb1250_bus_status`, optional `ldt_eoi_space`, `sb1250_pci_ops`, and `sb1250_controller`. `sb1250_pci_can_access()` filters config cycles by bus status and device mode. `sb1250_pcibios_read()` and `sb1250_pcibios_write()` implement width-aware config operations. `sb1250_pcibios_init()` initializes the platform.

### Control Flow
The initcall sets `PCI_PROBE_ONLY`, minimum I/O/MEM limits, global resource ends, maps 16 MiB config space, checks firmware host/device mode and bridge command bits, maps I/O space with match-bytes policy, optionally maps LDT EOI space if the LDT bridge is enabled, registers the controller, and hands VGA console to `vga_con` when configured.

### State, Persistence, And Dependencies
Persistent effects are KSEG2/KSEG3 mappings, bus status flags, global resource limits, LDT EOI mapping, and registered PCI controller. Dependencies include Sibyte SCD/board register definitions, raw 64-bit reads, console infrastructure, and legacy MIPS PCI.

### Integration Points
Firmware/CFE assigns resources, so Linux claims them only. LDT support and VGA console integration are conditional.

### Risks
Large config/EOI mappings consume kernel virtual memory on 32-bit kernels. Device mode hides most bus-0 devices. If firmware leaves the PCI bridge master bit clear, scanning is skipped. Config write filtering must correctly simulate master aborts.

### Test Signals
Boot with firmware-initialized PCI, verify `PCI_PROBE_ONLY`, config-space all-ones on disallowed accesses, LDT interrupts with EOI mapping, and VGA console takeover when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-sb1250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-tx4927.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-tx4927.c

### Purpose
This file contains Toshiba TX4927 PCI clock reporting, optional 66 MHz setup, and PCI error IRQ registration helpers used by TXx9 board code.

### Important APIs, Types, And Functions
`tx4927_report_pciclk()` logs whether PCI66 is asserted and computes internal PCI clock from CPU clock and divider mode, or reports external clock. `tx4927_pciclk66_setup()` asserts M66EN and adjusts divider mode to double the clock when possible. `tx4927_setup_pcierr_irq()` registers `tx4927_pcierr_interrupt` for the TX4927 PCIERR IRQ.

### Control Flow
Board setup calls these helpers before or during PCI controller initialization. Clock setup reads `ccfg`/`pcfg`, selects a supported divider, writes changed config with `tx4927_ccfg_change()`, and returns the computed clock or `-1` for external clock.

### State, Persistence, And Dependencies
Persistent effects are TX4927 CCFG divider and PCI66 bits plus an installed PCI error interrupt handler. Dependencies include `tx4927_ccfgptr`, `txx9_cpu_clock`, TX4927 bit definitions, and the shared TX4927 PCI error handler.

### Integration Points
This is not a standalone controller driver; platform board files call it when wiring TX4927 PCI.

### Risks
Wrong divider selection can overclock PCI. Error IRQ registration failure is only a warning. External-clock mode leaves frequency unknown to callers except via `-1`.

### Test Signals
Check boot clock logs, measured PCI clock against divider settings, M66EN assertion, and PCIERR interrupt delivery on forced controller errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-tx4927.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-tx4938.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-tx4938.c

### Purpose
This file provides TX4938 PCI clock and error-IRQ helpers plus PCI1 Ethernet slot IRQ mapping. It is board-support glue consumed by TXx9 platform setup.

### Important APIs, Types, And Functions
`tx4938_report_pciclk()` reports PCIC clock from divider mode. `tx4938_report_pci1clk()` reports PCIC1 clock from GBUS clock and divider. `tx4938_pciclk66_setup()` asserts PCI66 and selects a faster supported divider. `tx4938_pcic1_map_irq()` maps PCIC1 slots 31/30 to ETH0/ETH1 IRQs when selected in `pcfg`. `tx4938_setup_pcierr_irq()` installs the shared PCI error handler.

### Control Flow
Board setup invokes reporting/setup helpers. The PCI1 IRQ mapper first checks that the device belongs to `tx4938_pcic1ptr`, then maps specific IDSEL-derived slots if Ethernet functions are selected, returns zero for unmapped PCIC1 slots, and `-1` for other controllers.

### State, Persistence, And Dependencies
State changes are CCFG divider/PCI66 bits and registered error IRQ. Dependencies include TX4938 CCFG/PCFG registers, TX4927 controller helpers, TXx9 clock globals, and interrupt constants.

### Integration Points
It layers TX4938-specific policy over generic TX4927 PCI controller code and board-level mapping.

### Risks
Clock setup may not reflect board signal integrity. Returning zero versus `-1` from `tx4938_pcic1_map_irq()` has distinct meanings and callers must preserve that distinction. PCI error IRQ failure is nonfatal.

### Test Signals
Validate clock logs, PCI66 divider writes, ETH0/ETH1 IRQ mapping for PCIC1 slots, and PCIERR interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-tx4938.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-xtalk-bridge.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci-xtalk-bridge.c

### Purpose
This file implements SGI Xtalk Bridge PCI host support. It provides DMA address translation, config-space access including IOC3 emulation, bridge interrupt domains, board-specific IOC3 subsystem/interrupt setup from NVMEM, host bridge probing/removal, and platform-driver registration.

### Important APIs, Types, And Functions
Exports include `phys_to_dma()` and `dma_to_phys()`. Config helpers are `ioc3_cfg_rd/wr()`, `pci_conf0/1_read_config()`, `pci_conf0/1_write_config()`, and `bridge_pci_ops`. IRQ support uses `bridge_irq_chip_data`, `bridge_irq_chip`, `bridge_domain_ops`, `bridge_map_irq()`, and affinity/activate/deactivate callbacks. Board setup helpers populate `ioc3_sid` and `int_mapping`. `bridge_get_partnum()` reads and CRC-validates NVMEM PROM contents. `bridge_probe()` and `bridge_remove()` manage the host bridge.

### Control Flow
Probe defers until bridge NVMEM is available, creates a child IRQ domain under the default domain, allocates a `pci_host_bridge` with private `bridge_controller`, adds memory/I/O/bus resources with offsets, requests resources, initializes bridge registers and interrupt routing defaults, disables or enables swapping/page-size bits, applies board setup based on part number, sets PCI ops/map_irq/swizzle, scans the root bus, claims firmware resources, and adds devices. Removal tears down IRQ domain and root bus under PCI rescan locks.

### State, Persistence, And Dependencies
State spans bridge MMIO registers, per-slot IOC3 subsystem IDs, cached PCI interrupt virqs, IRQ domain/fwnode, DMA base address, resource windows, and platform driver data. Dependencies include SGI Bridge register definitions, DBE-safe accessors, NVMEM, CRC16, irqdomain hierarchy, PCI host-bridge APIs, and Xtalk platform data.

### Integration Points
It drives `xtalk-bridge` platform devices and supports SGI IOC3 quirks used by IP27/IP29/IP30/IP34 systems. `pci-ip27.c` consumes the resulting bridge controller for NUMA node mapping and IOC3 fixups.

### Risks
IOC3 emulation is deliberately partial; unmodeled config registers return zero or ignore writes. `bridge_domain_free()` returns early when `nr_irqs` is nonzero, which is unusual and worth reviewing. Part-number matching depends on PROM CRC and NVMEM device naming. Type 1 access is acknowledged as poorly documented.

### Test Signals
Validate NVMEM deferral, PROM part matching, IOC3 subsystem IDs, PCI config reads behind root and subordinate buses, IRQ allocation/affinity on NUMA systems, DMA address round trips, and clean platform removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-xtalk-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pci.c

### Purpose
This small file provides common MIPS PCI globals and helpers shared by PCI implementations: default minimum I/O and memory values, cache-line-size initialization, and user-visible resource address fixup.

### Important APIs, Types, And Functions
`PCIBIOS_MIN_IO` and `PCIBIOS_MIN_MEM` are exported globals. `pcibios_set_cache_line_size()` computes the highest available data/secondary/tertiary cache line size and stores `pci_dfl_cache_line_size` in dwords. `pci_resource_to_user()` translates resource starts through `fixup_bigphys_addr()`.

### Control Flow
At `arch_initcall()`, cache line size is derived from CPU cache helpers and must be nonzero. Resource translation is called by PCI sysfs/proc paths when presenting BAR ranges to userspace.

### State, Persistence, And Dependencies
Persistent state is `pci_dfl_cache_line_size` and exported minimum-resource globals. Dependencies include MIPS CPU cache helpers and big physical address fixups.

### Integration Points
Platform files set `PCIBIOS_MIN_IO/MEM`; generic PCI device enable and user-resource reporting consume these values.

### Risks
`BUG_ON(!lsize)` makes broken CPU cache reporting fatal. `pci_resource_to_user()` sets `end` from the un-fixed resource start, which should be checked for consistency when big physical address fixups change `start`.

### Test Signals
Boot logs under PCI debug, `lspci -vv` cache line values, and sysfs resource files on high physical address systems validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pcie-octeon.c -->
## sources/distributed-fs/ceph-client/arch/mips/pci/pcie-octeon.c

### Purpose
This file initializes Octeon PCIe root complexes, provides low-level CVMX-style PCIe config/I/O/MEM address helpers, handles Gen1 and Gen2 link bring-up with errata workarounds, implements Linux `pci_ops` per port, creates dummy and real controllers, maps interrupts, and initializes PCIe DMA.

### Important APIs, Types, And Functions
Key state includes module parameter `pcie_disable`, `enable_pcie_14459_war`, `enable_pcie_bus_num_war[]`, and the shared `octeon_pcibios_map_irq`/`octeon_dma_bar_type`. `union cvmx_pcie_address` encodes config/I/O/MEM cycles. Helpers include `cvmx_pcie_get_*_base/size()`, `cvmx_pcie_cfgx_read/write()`, `__cvmx_pcie_build_config_addr()`, width-specific config accessors, `__cvmx_pcie_rc_initialize_config_space()`, Gen1/Gen2 link/root initialization functions, and `cvmx_pcie_rc_initialize()`. Linux-facing functions include `octeon_pcie_pcibios_map_irq()`, `octeon_pcie_read_config()`, `octeon_pcie_write_config()`, per-port wrappers, dummy ops, `device_needs_bus_num_war()`, and `octeon_pcie_setup()`.

### Control Flow
`octeon_pcie_setup()` exits if the chip lacks PCIe, is simulation, or `pcie_disable` is set. It installs the PCIe IRQ mapper, sets the aggregate I/O port base, registers a dummy controller to consume bus 0 for IDT bridge compatibility, determines host mode and DMA BAR type, initializes port 0 and port 1 when root-complex mode is available, fills each controller's mem/I/O windows and offsets, registers successful ports, records IDT bus-number workarounds, applies CN63XX SRIO/PCIe interrupt-map errata, then calls `octeon_pci_dma_init()`. Config reads update primary bus numbers, reject impossible root devices, apply non-existent-device errata workarounds, and optionally retry CRS config reads.

### State, Persistence, And Dependencies
Persistent state is vast: PCIe PEM/NPEI/SLI/DPI/CIU/MIO CSRs, BAR1 index tables, root-complex bus numbers, link state, resource windows, dummy controller bus consumption, workaround flags, and DMA mode. Dependencies include many Octeon CVMX register headers, model/feature/board detection, PCI core, module parameters, delay/cycle timers, and shared Octeon PCI DMA code.

### Integration Points
The file is mutually exclusive with legacy `pci-octeon.c` on PCIe-capable chips. It registers legacy MIPS `pci_controller` objects, but much of the hardware code comes from CVMX root-complex initialization. Interrupts map to `OCTEON_IRQ_PCI_INT0` plus swizzled pin offsets, with EBH5600 bridge correction.

### Risks
The file is highly errata-driven and model-specific; regressions can be board-pass specific. Dummy bus 0 is intentional but can confuse bus-number assumptions. Config-read workarounds for nonexistent devices and CN63XX CRS retry are subtle. Several branches return generic `-1`. Gen1/Gen2 link training, SRIO detection, and BAR overlap rules require hardware validation.

### Test Signals
Exercise PCIe disabled parameter, simulation skip, port0/port1 host and endpoint modes, empty slots, Gen2 fallback to Gen1, IDT bus-number workaround, CN56XX/CN63XX errata paths, config read/write widths, interrupt delivery, DMA through BAR1/BAR2, and multiport resource windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pcie-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/Kconfig

### Purpose
This Kconfig fragment defines PIC32 machine selection and built-in device-tree options for Microchip PIC32MZDA MIPS systems.

### Important APIs, Types, And Functions
`config PIC32MZDA` selects boot formats, R4K clocksource/event support, noncoherent DMA, MIPS32 R2 CPU support, early printk, 32-bit little-endian kernel support, GPIO, common clock, libfdt, OF, and pinctrl. `DTB_PIC32_NONE` and `DTB_PIC32_MZDA_SK` choose devicetree behavior.

### Control Flow
Kconfig selection determines which source files build, what boot formats are accepted, whether early console is available, and whether a built-in DTB is linked.

### State, Persistence, And Dependencies
There is no runtime state. Build-time dependencies select kernel subsystems needed by PIC32MZDA board code.

### Integration Points
The fragment is included under `MACH_PIC32` and gates `arch/mips/pic32` Makefile entries.

### Risks
The platform assumes little-endian 32-bit operation and noncoherent DMA. Selecting a built-in DTB without matching hardware can break memory and device discovery.

### Test Signals
Config builds for `PIC32MZDA`, `DTB_PIC32_NONE`, and `DTB_PIC32_MZDA_SK`, plus boot confirmation that selected subsystems and DTB match expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/Makefile

### Purpose
This Makefile selects PIC32 common and PIC32MZDA-specific object directories based on kernel configuration.

### Important APIs, Types, And Functions
It adds `common/` for `CONFIG_MACH_PIC32` and `pic32mzda/` for `CONFIG_PIC32MZDA`.

### Control Flow
Build inclusion is purely conditional. Common reset/IRQ support is built for all PIC32 machines, while PIC32MZDA code is included only for that machine type.

### State, Persistence, And Dependencies
No runtime state exists. Build state depends on Kconfig symbols from `pic32/Kconfig`.

### Integration Points
This is the build bridge from top-level MIPS platform selection to PIC32 subdirectories.

### Risks
Future PIC32 variants would need additional directory rules or they may accidentally reuse MZDA-only code.

### Test Signals
`make` should include only common objects for generic PIC32 and include `pic32mzda/` objects when `CONFIG_PIC32MZDA=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/common/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/common/Makefile

### Purpose
This Makefile builds the common PIC32 reset and IRQ initialization objects.

### Important APIs, Types, And Functions
It unconditionally builds `reset.o` and `irq.o` whenever the parent PIC32 common directory is selected.

### Control Flow
There is no runtime flow. The parent Makefile controls entry into this directory.

### State, Persistence, And Dependencies
No runtime state exists. The build assumes all PIC32 machine variants need these common hooks.

### Integration Points
The objects provide `arch_init_irq()` and reboot/poweroff hook setup for the PIC32 platform.

### Risks
If a future PIC32 variant uses a different IRQ or reset mechanism, unconditional inclusion may be too broad.

### Test Signals
Build logs should show `reset.o` and `irq.o` for `CONFIG_MACH_PIC32`; boot should reach IRQ initialization and reboot hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/common/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/common/irq.c

### Purpose
This file provides the PIC32 architecture IRQ initialization hook.

### Important APIs, Types, And Functions
`arch_init_irq()` calls `irqchip_init()`.

### Control Flow
During architecture interrupt initialization, control passes directly to generic irqchip OF probing. Device-tree interrupt-controller nodes determine the concrete IRQ chips.

### State, Persistence, And Dependencies
The function creates no local state. Persistent IRQ domains and chips are created by `irqchip_init()`. Dependencies are Linux irqchip infrastructure and MIPS `arch_init_irq()` expectations.

### Integration Points
PIC32MZDA device trees must describe interrupt controllers compatible with irqchip drivers.

### Risks
If the DT lacks a supported interrupt controller, the platform has no interrupt handling. There is no PIC32-specific fallback here.

### Test Signals
Boot should show irqchip initialization, timer interrupt mapping, and working device interrupts from DT-described controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/common/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/common/reset.c -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/common/reset.c

### Purpose
This file installs PIC32 restart, halt, and poweroff hooks. It implements software reset through the PIC32 reset register and a halt loop using the MIPS `wait` instruction.

### Important APIs, Types, And Functions
`pic32_halt()` disables forward progress with repeated `wait`. `pic32_machine_restart()` maps `PIC32_BASE_RESET + PIC32_RSWRST`, unlocks SYSKEY, writes and reads the reset bit, then halts. `pic32_machine_halt()` disables interrupts and halts. `mips_reboot_setup()` assigns `_machine_restart`, `_machine_halt`, and `pm_power_off`.

### Control Flow
At `arch_initcall()`, reboot hooks are registered. Restart later maps the reset register, performs the documented magic write/read after `pic32_syskey_unlock()`, and falls back to halt if reset does not complete.

### State, Persistence, And Dependencies
Persistent state is the global machine hook assignments and hardware reset request. Dependencies include PIC32 platform-data base addresses, `pic32_syskey_unlock()`, raw MMIO, and MIPS reboot hooks.

### Integration Points
Kernel restart, halt, and poweroff paths call these hooks. `pic32_syskey_unlock()` is implemented by the MZDA config code.

### Risks
The restart path maps the reset register on each call and never unmaps because reset or halt follows. If `pic32_syskey_unlock()` is unavailable or config MMIO is not initialized, restart may fail.

### Test Signals
Validate `reboot`, `halt`, and `poweroff` paths on hardware, and verify reset register write with a debugger or boot counter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/common/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/Makefile

### Purpose
This Makefile builds PIC32MZDA platform support objects and optional early printk support.

### Important APIs, Types, And Functions
Base objects are `config.o`, `early_clk.o`, `init.o`, and `time.o`. With `CONFIG_EARLY_PRINTK`, it also builds `early_console.o` and `early_pin.o`.

### Control Flow
Build rules follow Kconfig. Early console pin and UART setup are absent unless early printk is configured.

### State, Persistence, And Dependencies
No runtime state exists in the Makefile. Object selection depends on `CONFIG_PIC32MZDA` and `CONFIG_EARLY_PRINTK`.

### Integration Points
The built objects provide machine identity, DT population, clocks, reset-protected config registers, timer frequency, and early UART output.

### Risks
Disabling early printk removes early pin/UART setup, which can make bring-up failures harder to diagnose.

### Test Signals
Build with early printk enabled and disabled; verify symbol availability for `fw_init_early_console()` only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/config.c -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/config.c

### Purpose
This file manages PIC32MZDA configuration registers, including LCD enable/mode, SDHCI ADMA FIFO thresholds, SYSKEY unlock, reset-status capture, and device ID/version reporting.

### Important APIs, Types, And Functions
State includes `pic32_conf_base`, `config_lock`, and `pic32_reset_status`. Helpers `pic32_conf_get_reg_field()` and `pic32_conf_modify_atomic()` read and update register fields. Public APIs are `pic32_enable_lcd()`, `pic32_disable_lcd()`, `pic32_set_lcd_mode()`, `pic32_set_sdhci_adma_fifo_threshold()`, `pic32_syskey_unlock_debug()`, exported `pic32_get_boot_status()`, and `pic32_config_init()`.

### Control Flow
`pic32_config_init()` maps the config block, panics if mapping fails, reads and clears reset cause from `RCON`, and logs device ID/version. Runtime callers update `CFGCON2` under spinlock to avoid concurrent field clobbering. SYSKEY unlock writes the required three-key sequence.

### State, Persistence, And Dependencies
Persistent state is the config MMIO mapping, captured boot reset status, and modified config registers. Dependencies include PIC32 base-address macros, `PIC32_CLR/SET` helpers, spinlocks, and early platform init ordering.

### Integration Points
Reset code uses SYSKEY unlock. SDHCI platform data calls `pic32_set_sdhci_adma_fifo_threshold()`. LCD drivers can use LCD helpers. Boot-status users consume the exported symbol.

### Risks
`pic32_config_init()` maps only `0x110` bytes but reads `PIC32_RCON` at `0x1240`, which looks inconsistent and should be validated against PIC32 mapping semantics or fixed. Field setters do no range checking for threshold arguments.

### Test Signals
Boot log should show valid device ID/version, reset status should be captured and cleared, LCD/SDHCI register bits should change atomically, and reset SYSKEY unlock should permit software reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_clk.c -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_clk.c

### Purpose
This file computes early PIC32MZDA system and peripheral bus clocks directly from oscillator registers before the full common-clock framework is available.

### Important APIs, Types, And Functions
`pic32_get_sysclk()` reads `OSCCON` and `SPLLCON`, decodes oscillator source, PLL input divider, multiplier, output divider, and FRC divider, then returns the current system clock. `pic32_get_pbclk(int bus)` reads the PB divider for a bus and divides the system clock.

### Control Flow
Both functions temporarily `ioremap()` the oscillator block. System clock selection handles FRC, SPLL, POSC, and default unknown oscillator cases. PB clock computes `PB1DIV + ((bus - 1) * 0x10)` and divides by the encoded divider plus one.

### State, Persistence, And Dependencies
There is no persistent local state; mappings are released before return. Dependencies are PIC32 oscillator base address and register encodings.

### Integration Points
Early console uses PBCLK2 for UART baud setup. Timer init uses PBCLK7 to derive `mips_hpt_frequency`.

### Risks
Unknown oscillator sources return zero, which can propagate to baud or timer calculations. `pic32_get_pbclk()` does not validate bus range. Repeated `ioremap()` calls are acceptable early but inefficient.

### Test Signals
Compare boot-reported CPU clock, UART baud accuracy, and timer tick frequency against hardware oscillator/PLL settings for FRC, POSC, and SPLL modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_console.c -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_console.c

### Purpose
This file implements PIC32MZDA early UART setup and `prom_putchar()` support for early printk. It parses `earlyprintk=ttyS...` command-line parameters, configures PPS pins, programs UART baud/mode/status registers, and writes characters before normal serial drivers bind.

### Important APIs, Types, And Functions
State includes `uart_base` and `console_port`. `configure_uart_pins()` supports ports 1 and 5 with hard-coded PPS mappings. `configure_uart()` programs mode, baud generator, and TX/RX enable bits using PBCLK2. `pic32_getcmdline()`, `get_port_from_cmdline()`, and `get_baud_from_cmdline()` parse early command-line data. `fw_init_early_console()` maps UART space and initializes the selected/default console. `prom_putchar()` busy-waits for TX space and writes a byte.

### Control Flow
During `plat_mem_setup()` under `CONFIG_EARLY_PRINTK`, `fw_init_early_console()` maps UART registers, extracts port and baud or defaults to port 1 at 115200, configures PPS and UART. Later early printk calls `prom_putchar()`, which only emits when `console_port >= 0`.

### State, Persistence, And Dependencies
The UART mapping and console port persist through early boot. Dependencies include early clock helpers, PPS helpers from `early_pin.c`, firmware command-line helpers, and PIC32 UART base constants.

### Integration Points
This runs before full pinctrl and serial drivers. It uses built-in or firmware command lines depending on `CONFIG_CMDLINE_OVERRIDE`.

### Risks
Only ports 1 and 5 are supported. Command parsing is simple and assumes `ttyS<digit>,<baud>`. The UART mapping is intentionally not released. Bad PBCLK calculation causes baud mismatch.

### Test Signals
Boot with default earlyprintk, with `earlyprintk=ttyS5,57600`, and with unsupported ports; confirm early characters, pin muxing, and baud accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_pin.c -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_pin.c

### Purpose
This file provides minimal early Peripheral Pin Select configuration for PIC32MZDA before the full pinctrl driver is initialized. It maps abstract input functions and output pins to PPS register offsets and writes selected values.

### Important APIs, Types, And Functions
`input_pin_reg[]` maps `IN_FUNC_*` identifiers to input PPS registers. `output_pin_reg[]` maps `OUT_*` pin identifiers to output PPS registers. `pic32_pps_input()` maps the PPS block and writes a pin value to the matching function register. `pic32_pps_output()` maps the PPS block and writes a function value to the matching pin register.

### Control Flow
Each function linearly scans its table for the requested function or pin. On match it writes the requested value and returns. If no match is found, it unmaps before returning.

### State, Persistence, And Dependencies
Persistent effects are PPS hardware register assignments. Dependencies are the identifier definitions in `early_pin.h`, raw MMIO, and the fixed PPS base `0x1f800000`.

### Integration Points
`early_console.c` calls these helpers to route UART RX/TX pins for early printk. Later pinctrl may reconfigure pins for normal drivers.

### Risks
Successful paths return without `iounmap()`, leaving early mappings live. This may be intentional for early boot but should be documented or converted to static mapping. Linear tables lack validation for function/pin compatibility beyond caller convention.

### Test Signals
Confirm early UART pins route correctly for supported ports and verify later pinctrl can take over without conflicting PPS state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_pin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_pin.h -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_pin.h

### Purpose
This header defines the early PIC32MZDA PPS function and pin identifiers used by `early_pin.c` and early UART setup.

### Important APIs, Types, And Functions
It defines an enum of input functions, macros for input pin selector values, an enum of output pins, macros for output function selector values, and prototypes for `pic32_pps_input()` and `pic32_pps_output()`.

### Control Flow
There is no runtime control flow. The values are consumed by table lookups in `early_pin.c`.

### State, Persistence, And Dependencies
No state exists. The header encodes PIC32MZDA PPS selector values and depends on callers using function/pin combinations supported by the chip.

### Integration Points
Early console includes this header to configure UART2 or UART6 pin muxing before full pinctrl.

### Risks
Several output function macro names are repeated with different values because PPS output functions are bank-dependent. This is legal for the hardware encoding style but risky for generic callers. Values are not type-safe.

### Test Signals
Compile users with duplicate macro warnings disabled as expected, and verify each early UART mapping writes the documented register selector values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_pin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/init.c -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/init.c

### Purpose
This file contains PIC32MZDA machine initialization: system-type reporting, early device-tree setup, command-line construction, early console/config init, SDHCI auxdata, and OF platform population.

### Important APIs, Types, And Functions
`get_system_type()` returns `"PIC32MZDA"`. `plat_mem_setup()` obtains the FDT, calls `__dt_setup_arch()`, logs command lines, initializes early console and config registers. `pic32_init_cmdline()` builds `arcs_cmdline` from firmware arguments. `prom_init()` calls that parser. `pic32_auxdata_lookup[]` supplies SDHCI platform data with `pic32_set_sdhci_adma_fifo_threshold`. `pic32_of_prepare_platform_data()` fills auxdata names/addresses from DT. `plat_of_setup()` populates OF devices.

### Control Flow
Firmware args are captured in `prom_init()`. `plat_mem_setup()` runs early, loads DT memory/chosen data, copies command line when using an external DTB, initializes optional early console, and calls `pic32_config_init()`. At `arch_initcall()`, `plat_of_setup()` requires a populated DT, prepares auxdata, and calls `of_platform_default_populate()`.

### State, Persistence, And Dependencies
State includes boot command lines, OF device population, SDHCI platform data, and config initialization side effects. Dependencies include firmware FDT access, Linux OF APIs, PIC32 config/early-console helpers, and SDHCI PIC32 platform data.

### Integration Points
This is the central link between firmware, built-in/external DTB, early printk, platform devices, and PIC32-specific SDHCI DMA setup.

### Risks
No DTB only logs an error in `plat_mem_setup()`, but later `plat_of_setup()` panics if no populated DT exists. Command-line concatenation silently truncates. Auxdata lookup mutates names from DT and assumes first resource is the device base.

### Test Signals
Boot with built-in and external DTBs, confirm memory discovery, command-line logs, SDHCI auxdata setup, OF platform devices, and early console ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/pic32mzda.h -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/pic32mzda.h

### Purpose
This header declares PIC32MZDA platform helper APIs shared across early console, init, time, config, and common reset code.

### Important APIs, Types, And Functions
It declares early clock helpers `pic32_get_pbclk()` and `pic32_get_sysclk()`, config initialization and LCD/SDHCI helpers, `pic32_get_boot_status()`, and LCD enable/disable functions.

### Control Flow
There is no runtime flow. The declarations allow platform code to call across PIC32MZDA compilation units.

### State, Persistence, And Dependencies
No direct state exists. Functions declared here operate on oscillator and config MMIO state.

### Integration Points
Early console, timer setup, SDHCI auxdata, and reset paths depend on these declarations.

### Risks
The header exposes board-specific helpers globally within the directory without documenting valid argument ranges, especially for bus numbers, LCD mode, and SDHCI thresholds.

### Test Signals
Build coverage across early-printk and non-early-printk configurations should catch declaration/definition drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/pic32mzda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/time.c -->
## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/time.c

### Purpose
This file initializes PIC32MZDA timer support and maps the MIPS C0 compare interrupt through device tree infrastructure.

### Important APIs, Types, And Functions
`pic32_infra_match[]` identifies `"microchip,pic32mzda-infra"`. `pic32_xlate_core_timer_irq()` finds that node, maps its first IRQ, and falls back to mapping hardware interrupt 0. `get_c0_compare_int()` returns the translated IRQ. `plat_time_init()` initializes clocks, reports CPU clock, sets `mips_hpt_frequency`, and calls `timer_probe()`.

### Control Flow
Timer init reads PBCLK7 via early clock code, calls `of_clk_init(NULL)`, logs rate, sets high-precision timer frequency to half the rate, and probes timers. Compare IRQ lookup happens when generic MIPS timer code asks for it.

### State, Persistence, And Dependencies
Persistent state is `mips_hpt_frequency` and IRQ mappings created from DT. Dependencies include OF IRQ/clock APIs, PIC32 early clock helpers, and MIPS timer infrastructure.

### Integration Points
This connects PIC32 DT interrupt descriptions and common MIPS clockevent/clocksource setup.

### Risks
Fallback to `irq_create_mapping(NULL, 0)` may be invalid if no default domain exists. The logged "CPU Clock" uses PBCLK7, so naming may be misleading. Bad PB divider values affect scheduler timing.

### Test Signals
Check timer interrupt fires, `mips_hpt_frequency` matches hardware, DT infra IRQ is used, and fallback mapping behaves on minimal DTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/power/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/power/Makefile

### Purpose
This Makefile includes MIPS hibernation support objects when hibernation is enabled.

### Important APIs, Types, And Functions
For `CONFIG_HIBERNATION`, it builds `cpu.o`, `hibernate.o`, and `hibernate_asm.o`.

### Control Flow
Build inclusion is conditional on the hibernation Kconfig symbol.

### State, Persistence, And Dependencies
No runtime state exists. The object list provides architecture callbacks used by the generic suspend/hibernate core.

### Integration Points
The generated objects implement processor state save/restore, resume, and low-level image copy/return.

### Risks
Partial object selection is not supported; all three files are required for a functional hibernation path.

### Test Signals
Build with `CONFIG_HIBERNATION=y` and verify symbols `swsusp_arch_suspend`, `swsusp_arch_resume`, and processor state hooks are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/power/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/power/cpu.c -->
## sources/distributed-fs/ceph-client/arch/mips/power/cpu.c

### Purpose
This file saves and restores MIPS processor state across hibernation and marks the nosave memory range.

### Important APIs, Types, And Functions
State includes `saved_status` and global `saved_regs`, which assembly uses for callee-saved registers. `save_processor_state()` saves CP0 status, current FPU state if owned, and DSP state. `restore_processor_state()` restores CP0 status, FPU if owned, and DSP. `pfn_is_nosave()` checks PFNs against `__nosave_begin`/`__nosave_end`.

### Control Flow
Generic hibernation calls save before snapshot and restore after resume. Low-level assembly saves GPRs separately in `saved_regs`. PFN filtering excludes the nosave section from the image.

### State, Persistence, And Dependencies
Persistent hibernation state is saved CP0 status, saved registers, FPU/DSP state, and the nosave section boundaries. Dependencies include MIPS FPU/DSP helpers and linker section symbols.

### Integration Points
Works with `hibernate_asm.S` and generic swsusp memory image code.

### Risks
FPU restore is conditional on current ownership; ownership transitions during hibernation must be correct. Missing CPU extension state beyond FPU/DSP would not be preserved.

### Test Signals
Hibernate/resume with FPU and DSP workloads, verify CP0 status restoration, and confirm nosave pages are excluded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/power/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/power/hibernate.c -->
## sources/distributed-fs/ceph-client/arch/mips/power/hibernate.c

### Purpose
This file provides the MIPS architecture resume entry for software suspend.

### Important APIs, Types, And Functions
`swsusp_arch_resume()` flushes all local TLB entries and calls assembly `restore_image()`.

### Control Flow
During resume from hibernation, generic swsusp calls this function. It clears stale TLB translations before copying the saved image back to original pages and returning through saved registers.

### State, Persistence, And Dependencies
State effects are TLB invalidation and restored memory image through assembly. Dependencies include `local_flush_tlb_all()` and `restore_image()` from `hibernate_asm.S`.

### Integration Points
Pairs with `swsusp_arch_suspend()` and generic hibernation image restoration.

### Risks
The flush is local, so SMP resume ordering must ensure other CPUs are not using stale TLBs. Any failure in `restore_image()` directly affects resume integrity.

### Test Signals
Hibernate/resume on supported MIPS hardware, with memory pressure and TLB-sensitive workloads, validates this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/power/hibernate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/power/hibernate_asm.S -->
## sources/distributed-fs/ceph-client/arch/mips/power/hibernate_asm.S

### Purpose
This assembly file saves callee-critical registers before hibernation image creation and restores the memory image/registers during resume.

### Important APIs, Types, And Functions
`swsusp_arch_suspend` saves `ra`, `sp`, `fp`, `gp`, and `s0`-`s7` into `saved_regs`, then jumps to `swsusp_save`. `restore_image` walks `restore_pblist`, copies each saved page back to its original address, reloads saved registers, sets `v0` to zero, and returns to saved `ra`.

### Control Flow
Suspend enters assembly, snapshots registers, and transfers to generic swsusp save code. Resume iterates page backup entries: for each, it copies `_PAGE_SIZE` bytes in native register-sized chunks from backup to original, follows `PBE_NEXT`, then restores saved registers and returns as if suspend succeeded.

### State, Persistence, And Dependencies
State is `saved_regs`, `restore_pblist`, and page backup entries. Dependencies include generated asm offsets for `pt_regs` and `pbe`, MIPS register definitions, and page-size constants.

### Integration Points
Called by generic hibernation through architecture hooks and by `swsusp_arch_resume()` in `hibernate.c`.

### Risks
Copy loops assume valid restore lists and non-overlapping safe backup pages. Register save coverage must match ABI expectations. Cache/TLB coherency is handled outside this file and must be correct before returning.

### Test Signals
Resume should return zero from `swsusp_arch_suspend`, preserve stack/global/callee-saved registers, and restore page contents exactly across varied page sizes and endian modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/power/hibernate_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/Kconfig

### Purpose
This Kconfig fragment selects Ralink/MediaTek MIPS SoC variants, interrupt-controller options, debug illegal-access support, and built-in DTB choices.

### Important APIs, Types, And Functions
It defines `RALINK_ILL_ACC`, `IRQ_INTC`, SoC choices for RT288x, RT305x, RT3883, MT7620/8, and MT7621, and DTB choices for non-MT7621 systems. SoC selections enable PCI, GIC, SMP/CPS, highmem, pinctrl, SOC_BUS, and cache options as appropriate.

### Control Flow
Configuration controls which platform objects build and which architecture facilities are enabled. MT7621 selects generic PCI drivers and MIPS GIC rather than the legacy Ralink INTC path.

### State, Persistence, And Dependencies
No runtime state exists. Build-time dependencies determine IRQ model, PCI framework, SMP support, and DTB linkage.

### Integration Points
The Ralink Makefile consumes these symbols to include SoC, timer, IRQ, PCI, and debugfs components.

### Risks
Incorrect SoC choice can select incompatible IRQ and PCI paths. DTB choices are disabled for MT7621, requiring an external DT flow.

### Test Signals
Build each SoC choice, confirm expected object inclusion, and boot with matching DTB to verify selected IRQ and PCI model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/Makefile

### Purpose
This Makefile selects common Ralink platform code, timer/IRQ implementation, SoC-specific identification files, early printk, and optional debugfs bootrom exposure.

### Important APIs, Types, And Functions
Base objects are `prom.o`, `of.o`, and `reset.o`. Non-GIC builds add `clk.o` and `timer.o`; GIC builds add `irq-gic.o` and `timer-gic.o`. Other selections include `ill_acc.o`, `irq.o`, SoC files, `early_printk.o`, and `bootrom.o`.

### Control Flow
Build-time control follows Kconfig. MT7621/GIC uses a different timer/IRQ path from older Ralink SoCs.

### State, Persistence, And Dependencies
No runtime state exists. Object inclusion determines which `arch_init_irq()`, `plat_time_init()`, and `prom_soc_init()` implementations are linked.

### Integration Points
The Makefile is the build dispatcher for the Ralink architecture directory.

### Risks
Conflicting selections could link duplicate architecture hooks, so Kconfig dependencies must keep INTC and GIC paths exclusive.

### Test Signals
Inspect linked objects for each SoC config and confirm no duplicate symbol errors across IRQ/timer variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/bootrom.c -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/bootrom.c

### Purpose
This debugfs helper exposes the Ralink boot ROM contents through a read-only `bootrom` debugfs file.

### Important APIs, Types, And Functions
`membase` points at `KSEG1ADDR(BOOTROM_OFFSET)`. `bootrom_show()` writes `BOOTROM_SIZE` bytes to the seq file. `DEFINE_SHOW_ATTRIBUTE(bootrom)` generates file operations. `bootrom_setup()` creates the debugfs file at postcore init.

### Control Flow
When debugfs support includes this object, `postcore_initcall()` creates `/sys/kernel/debug/bootrom`. Reads stream the fixed boot ROM range.

### State, Persistence, And Dependencies
State is a fixed uncached KSEG1 pointer and the debugfs dentry. Dependencies include debugfs, seq_file, and Ralink physical memory map.

### Integration Points
Selected by `CONFIG_DEBUG_FS` in the Ralink Makefile, useful for platform bring-up and ROM inspection.

### Risks
The file exposes raw boot ROM contents to users with debugfs access. It assumes the boot ROM physical range is valid on all selected Ralink SoCs.

### Test Signals
With debugfs mounted, reading `bootrom` should return exactly 0x8000 bytes and not fault on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/bootrom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/clk.c -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/clk.c

### Purpose
This file initializes timer frequency for non-GIC Ralink SoCs by obtaining the CPU clock from the OF clock provider and setting `mips_hpt_frequency`.

### Important APIs, Types, And Functions
`clk_cpu()` maps the global `ralink_soc` enum to a sysc compatible string and clock index. `plat_time_init()` remaps Ralink OF registers, initializes clocks, fetches the CPU clock, logs the rate, sets `mips_hpt_frequency`, releases the clock, and calls `timer_probe()`.

### Control Flow
Timer init runs after SoC identification. It chooses a compatible/index pair, panics on unsupported SoC, initializes OF clocks, finds the provider node, gets the indexed clock, and derives the MIPS counter frequency as CPU clock divided by two.

### State, Persistence, And Dependencies
Persistent state is `mips_hpt_frequency`. Dependencies include `ralink_soc`, `ralink_of_remap()`, OF clock providers in sysc nodes, clock framework, and MIPS timer probing.

### Integration Points
This is used only when `CONFIG_MIPS_GIC` is not selected; MT7621 uses GIC timer code instead.

### Risks
Missing or mismatched clock providers panic early. The compatible/index table must stay aligned with DT bindings and SoC enum values.

### Test Signals
Boot each non-GIC SoC, verify CPU clock log, timer interrupt cadence, and correct sysc clock index selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/common.h -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/common.h

### Purpose
This header declares shared Ralink SoC information and early platform hooks.

### Important APIs, Types, And Functions
`RAMIPS_SYS_TYPE_LEN` bounds the system type string. `struct ralink_soc_info` records system type, compatible string, memory base/size/min/max, and optional memory-detect callback. It declares global `soc_info`, `ralink_of_remap()`, and SoC-specific `prom_soc_init()`.

### Control Flow
No runtime flow exists in the header. Platform init fills `soc_info` through the selected SoC implementation.

### State, Persistence, And Dependencies
State is external in `soc_info` and SoC files. The struct persists boot-time SoC and memory metadata.

### Integration Points
Common prom/OF code, clock code, and SoC-specific files share this contract.

### Risks
The `compatible` pointer is mutable `unsigned char *` even though callers assign string literals. Memory min/max and detect callback semantics must stay consistent across SoCs.

### Test Signals
Build all Ralink SoC variants and verify `soc_info.sys_type`, compatible string, and memory sizing are populated before OF/device setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/early_printk.c -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/early_printk.c

### Purpose
This file implements early `prom_putchar()` for Ralink/MediaTek SoCs using fixed KSEG1 UART addresses before normal serial drivers are available.

### Important APIs, Types, And Functions
Compile-time constants choose `EARLY_UART_BASE` and `CHIPID_BASE` for RT288x, MT7621, or other Ralink SoCs. `uart_membase`, `chipid_membase`, and `init_complete` hold early state. `soc_is_mt7628()` detects MT7628 by chip name. `find_uart_base()` scans possible MT7628 UART offsets. `prom_putchar()` writes one byte using SoC-specific TX/LSR register conventions.

### Control Flow
The first `prom_putchar()` call optionally discovers MT7628 UART base once. MT7621 and MT7628 write `UART_TX` then wait for THRE in `UART_REG_LSR`. Older SoCs wait on `UART_REG_LSR_RT2880`, write `UART_REG_TX`, then wait again.

### State, Persistence, And Dependencies
State is fixed uncached UART/chipid mappings and the one-time base discovery flag. Dependencies include serial register bit definitions, KSEG1 address mapping, and selected SoC Kconfig.

### Integration Points
Used by `CONFIG_EARLY_PRINTK` before full Ralink serial and pinctrl setup.

### Risks
MT7628 UART discovery assumes a nonzero LCR identifies the active UART. Fixed base addresses must match bootloader UART routing. Busy-waiting can hang if UART clocking is unavailable.

### Test Signals
Verify early output on RT288x, MT7621, MT7620, and MT7628/MT7688 boards, including correct UART selection and no hangs when TX FIFO is full.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/ill_acc.c -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/ill_acc.c

### Purpose
This file installs an illegal memory-access interrupt handler for RT305x-class Ralink memory controllers. It reports which bus master made an invalid read/write and clears the interrupt.

### Important APIs, Types, And Functions
`ill_acc_ids[]` names hardware requesters. `ill_acc_irq_handler()` reads illegal access address/type registers, decodes write/read, source ID, offset, and length, logs an error, and clears status. `ill_acc_of_setup()` locates the `"ralink,rt3050-memc"` node/platform device, maps IRQ, requests it, clears pending status, and logs registration.

### Control Flow
At `arch_initcall()`, setup skips RT5350, finds the memory-controller node, obtains the platform device and IRQ, installs the handler, and clears `ILL_INT_STATUS`. Interrupts later decode and clear each illegal access.

### State, Persistence, And Dependencies
Persistent state is the requested IRQ and enabled memory-controller interrupt status. Dependencies include Ralink memc register helpers, OF platform lookup, IRQ mapping, and RT305x compatibility.

### Integration Points
Selected by `RALINK_ILL_ACC` for SOC_RT305X and complements platform diagnostics.

### Risks
If `of_find_device_by_node()` succeeds and `request_irq()` succeeds, the device reference is intentionally retained; failure paths must release it. RT5350 is excluded because the driver breaks there. Logging in IRQ context can be noisy under repeated faults.

### Test Signals
Force illegal DMA/CPU accesses, confirm decoded source/address/length, and verify status clearing prevents interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/ill_acc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/irq-gic.c -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/irq-gic.c

### Purpose
This file provides IRQ initialization for Ralink platforms using the MIPS GIC, notably MT7621.

### Important APIs, Types, And Functions
`get_c0_perfcount_int()` returns `gic_get_c0_perfcount_int()` and is exported GPL. `arch_init_irq()` calls `irqchip_init()`.

### Control Flow
During architecture IRQ init, generic irqchip OF probing initializes CPU/GIC interrupt controllers. Performance-counter interrupt requests delegate to the GIC helper.

### State, Persistence, And Dependencies
No local state exists. Persistent IRQ domains are created by irqchip code. Dependencies include MIPS CPS/GIC support, OF irqchip data, and MIPS time/perf infrastructure.

### Integration Points
Selected under `CONFIG_MIPS_GIC` by the Ralink Makefile. It replaces the legacy Ralink INTC implementation.

### Risks
The platform depends entirely on DT-described irqchips. If GIC is not described or initialized, both device IRQs and performance counters fail.

### Test Signals
Boot MT7621 with GIC DT, validate timer/device interrupts, and confirm perf counter interrupt mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/irq-gic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/irq.c

### Purpose
This file implements the legacy Ralink interrupt controller path for non-GIC SoCs. It maps CPU interrupt lines, creates a 32-entry SoC interrupt domain, masks/unmasks INTC bits, dispatches cascaded interrupts, and exposes timer/perf IRQ mappings.

### Important APIs, Types, And Functions
State includes `rt_intc_regs[]`, `rt_intc_membase`, and `rt_perfcount_irq`. `ralink_intc_irq_unmask()`/`mask()` write enable/disable registers. `ralink_intc_irq_handler()` dispatches the first pending SoC IRQ from `STATUS0`. `plat_irq_dispatch()` handles MIPS IP7/IP5/IP6/IP4/IP2 priorities. `intc_map()` binds virqs to `ralink_intc_irq_chip`. `intc_of_init()` maps the controller, creates a legacy domain, enables global interrupts, and installs the chained handler. `arch_init_irq()` calls `of_irq_init()`.

### Control Flow
OF IRQ initialization first initializes the CPU interrupt controller, then the Ralink INTC node. The INTC setup optionally loads register offsets from DT, maps its parent IRQ, requests/remaps MMIO, disables all interrupts, routes all SoC interrupts to MIPS HW0, creates mappings, enables global INTC, chains the parent handler, and maps hwirq 9 for perf counters.

### State, Persistence, And Dependencies
Persistent state includes INTC MMIO mapping, IRQ domain, chip bindings, mask state, and performance IRQ. Dependencies include MIPS CPU IRQ code, OF address/IRQ parsing, irqdomain, and Ralink register layout.

### Integration Points
Device-tree interrupt specifiers use one-cell hwirq values under the Ralink INTC. MIPS timer code uses `get_c0_compare_int()` and perf uses `get_c0_perfcount_int()`.

### Risks
The chained handler dispatches only the least significant pending bit per parent interrupt; repeated entry must drain more. `request_mem_region()` failure logs but continues to ioremap. Priority in `plat_irq_dispatch()` is fixed and may starve lower-priority sources under storms.

### Test Signals
Validate each CPU interrupt line, multiple simultaneous INTC bits, mask/unmask behavior, DT custom register maps, perf counter IRQ, and spurious interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/mt7620.c -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/mt7620.c

### Purpose
This file identifies MT7620/MT7628/MT7688 SoCs, determines DRAM type and supported memory size range, reports PMU control mode, populates `soc_info`, and registers a `soc_device`.

### Important APIs, Types, And Functions
State includes `dram_type` and `soc_info_ptr`. DRAM helpers are `mt7620_dram_init()` and `mt7628_dram_init()`. ID helpers read chip name, revision, package, EFUSE, version, and ECO fields. `mt7620_get_soc_name()` sets `ralink_soc` and compatible string. `mt7620_get_soc_id_name()` formats sysfs ID. `mt7620_soc_dev_init()` registers SOC_BUS metadata. `prom_soc_init()` is the early SoC initializer.

### Control Flow
`prom_soc_init()` validates chip identity, formats `sys_type`, reads system config to derive DRAM type with MT76x8-specific encoding, fills memory base/min/max via the appropriate DRAM helper, logs analog/digital PMU mode, and stores `soc_info_ptr`. Later `device_initcall()` allocates and registers `soc_device_attribute`.

### State, Persistence, And Dependencies
Persistent state includes `ralink_soc`, `soc_info` fields, memory size bounds, and registered SoC device metadata. Dependencies include raw sysc register access, MT7620 register definitions, SOC_BUS, and global Ralink platform init.

### Integration Points
PCIe, early printk, clock, and board setup depend on the `ralink_soc` and compatible values set here.

### Risks
Unknown DRAM type triggers `BUG()`. MT7688 uses the MT7628 compatible string, which may be intentional for binding reuse but needs awareness. Memory size is bounded rather than directly detected here.

### Test Signals
Boot MT7620A, MT7620N, MT7628AN, and MT7688 boards; verify sysfs soc attributes, DRAM logs, PMU logs, compatible string, and downstream PCI/clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/mt7620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/mt7621.c -->
## sources/distributed-fs/ceph-client/arch/mips/ralink/mt7621.c

### Purpose
This file initializes MT7621 SoC identity, memory detection, CPS/IOCU setup, PCI coherence window preparation, SMP ops registration, and SOC_BUS metadata.

### Important APIs, Types, And Functions
State includes `detect_magic` and `soc_info_ptr`. `pcibios_root_bridge_prepare()` programs GCR region 1 for PCI memory coherence when IOCU exists. `mips_cpc_default_phys_base()` intentionally panics because CPC address cannot be auto-detected. `mt7621_addr_wraparound_test()` and `mt7621_memory_detect()` determine lowmem size and optional highmem. ID helpers read chip name/revision/version/ECO. `mt7621_soc_dev_init()` registers SoC attributes. `prom_soc_init()` performs early setup.

### Control Flow
Early SoC init probes CM/CPC, reprograms GCR region 0 for PALMBUS coherence if IOCU exists, validates chip ID, sets compatible and `ralink_soc`, formats system type, assigns the memory-detect callback, stores `soc_info_ptr`, and registers CPS or VSMP SMP ops. Memory detection writes patterns at uncached aliases to find wraparound size from 32 MiB to 256 MiB, then adds highmem if no wrap occurs.

### State, Persistence, And Dependencies
Persistent state includes CM/GCR register programming, memblock additions through the callback, SoC metadata, SMP ops, and PCI root bridge coherence settings. Dependencies include MIPS CPS/CPC/CM helpers, memblock, generic PCI host bridge resources, MT7621 sysc registers, and SOC_BUS.

### Integration Points
MT7621 uses generic PCI drivers; `pcibios_root_bridge_prepare()` is called from generic PCI host setup to configure coherent PCI access. GIC IRQ/timer paths are selected by Kconfig.

### Risks
`mips_cpc_default_phys_base()` panics if called, so CPC probing must discover the address otherwise. The GCR mask contiguity warning catches but does not prevent invalid regions. Memory wrap tests write near `detect_magic` aliases and assume safe uncached access.

### Test Signals
Validate memory size detection for 32/64/128/256 MiB and highmem boards, PCI DMA coherency, CPS SMP boot, soc_device revision (`E1`/`E2`), and PALMBUS access immediately after CM probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/mt7621.c -->
