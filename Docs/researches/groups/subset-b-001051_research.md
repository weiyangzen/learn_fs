# subset-b-001051 research

Grouped research for the listed BCMA and block/AoE source files. Each section is bounded by the exact source-path markers required for reconciliation and is suitable for direct splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_pci.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_pci.c

Purpose: implements BCMA PCI/PCIe core client-side setup and runtime power hooks. It provides indirect PCIe register access, MDIO/SERDES access, early SPROM-related fixups, client-mode PCIe workarounds, and exported PCIe power-save behavior for BCMA devices hosted over PCI.

Important APIs and functions: `bcma_pcie_read()` is exported within the BCMA subsystem for indirect PCIe register reads through `BCMA_CORE_PCI_PCIEIND_ADDR/DATA`. `bcma_pcie_write()` mirrors it for local writes. The MDIO helpers `bcma_pcie_mdio_set_phy()`, `bcma_pcie_mdio_read()`, `bcma_pcie_mdio_write()`, and `bcma_pcie_mdio_writeread()` program SERDES/PLL registers, with revision-specific address formats and polling on `BCMA_CORE_PCI_MDIOCTL_ACCESS_DONE`. `bcma_core_pci_early_init()` detects host mode and fixes SPROM core index mapping. `bcma_core_pci_init()` dispatches to host-mode initialization or client-mode workarounds. `bcma_core_pci_power_save()` is exported and adjusts MDIO management registers on core revisions 15-22. `bcma_core_pci_up()` and `bcma_core_pci_down()` toggle the L1 timer extension.

Control flow: initialization is deliberately two-stage. Early init records `pc->hostmode` and, for client mode, calls `bcma_core_pci_fixcfg()` before SPROM reads. Full init then either calls `bcma_core_pci_hostmode_init()` from `driver_pci_host.c` or applies SERDES polarity/frequency-detect and L2/L3 exit fixups. Runtime up/down only changes the ASPM timer extension.

State and persistence: state is held in `struct bcma_drv_pci` flags `early_setup_done`, `setup_done`, `hostmode`, and the associated core revision. Register changes persist in hardware until reset or later power-state changes. The file does not allocate memory or maintain Linux-visible persistent objects.

Dependencies and integration points: depends on `bcma_private.h`, `linux/bcma/bcma.h`, PCI core register macros, `pcicore_read/write*`, sleep/delay primitives, and host-mode detection from `driver_pci_host.c`. It integrates with `main.c` through `bcma_core_pci_early_init()` and `bcma_core_pci_init()`, and with PCI-host runtime helpers through `bcma_host_pci_up/down()`.

Risks: MDIO polling silently returns zero or continues after timeout, so hardware failures can look like valid register values. Revision-specific magic values make regressions likely when adding chips. The `setup_done` guard is checked but not set in this file, so correctness depends on surrounding subsystem behavior. Test signals include successful BCMA PCI enumeration, SPROM reads after early fixcfg, no link instability after SERDES workarounds, and suspend/resume or power-save tests across core revisions 15-22.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_pci_host.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_pci_host.c

Purpose: implements BCMA PCIe core root-complex host mode for MIPS Broadcom SoCs. It exposes PCI configuration-space accessors, initializes host bridge windows and resources, enables CRS visibility, registers a platform PCI controller, and provides PCI fixups and IRQ mapping for devices behind the BCMA PCI core.

Important APIs and functions: `bcma_core_pci_is_in_hostmode()` probes eligible 0x4700/0x5300 chip families using `get_dbe()`-based `mips_busprobe32()`. `bcma_extpci_read_config()` and `bcma_extpci_write_config()` implement config access for internal device 0 and external devices through mapped config windows. `bcma_core_pci_hostmode_read_config()` and `_write_config()` are the `pci_ops` callbacks protected by `cfgspace_lock`. `bcma_find_pci_capability()` walks type-0 config capabilities. `bcma_core_pci_enable_crs()` enables PCIe Request Retry Status visibility and polls devices after reset. `bcma_core_pci_hostmode_init()` allocates `struct bcma_drv_pci_host`, programs SBTOPCI windows, configures chip-specific memory and I/O resources, enables interrupts, and calls `register_pci_controller()`. Exported integration helpers are `bcma_core_pci_plat_dev_init()` and `bcma_core_pci_pcibios_map_irq()`.

Control flow: host-mode init begins only if board flags do not disable PCI. It allocates the host controller, sets resources and pci_ops, resets the root complex, programs address windows depending on BCM4716/4748/4706 and core unit, waits the PCIe reset-required 100 ms, enables CRS, adjusts payload/read-request size for selected chips, enables master and memory access, maps I/O base, then registers with the MIPS PCI layer. Later PCI core fixups detect this bridge by comparing `dev->bus->ops->read` against the BCMA host read callback.

State and persistence: persistent state lives in `pc->host_controller`, `pc_host->pci_controller`, resource descriptors, `host_cfg_addr`, and the spinlock. Hardware state includes SBTOPCI window registers, bridge command bits, interrupt mask, BAR behavior, and max payload/read-request sizes.

Dependencies and integration points: MIPS-specific exception probing and `register_pci_controller()` are hard dependencies. It uses Linux PCI config constants, resource management, `ioremap/iounmap`, BCMA chip IDs, SPROM board flags, and interrupt mapping from `bcma_core_irq()`. `driver_pci.c` calls this file for host-mode initialization.

Risks: the implementation is explicitly MIPS-specific and assumes one-hot slot wiring and a small slot range. Config access uses temporary `ioremap()` per external access and bus exception probing; broken devices can still create latency. Resource-window programming is chip-specific and easy to regress. Test signals include boot on BCM4706/4716/4748 host-mode systems, PCI device enumeration, capability walking, CRS retry behavior, interrupt delivery, and early/header fixup logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_pci_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_pcie2.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/driver_pcie2.c

Purpose: initializes and services the BCMA PCIe Gen2 core. It applies chip/revision-specific workarounds, sets latency tolerance reporting values, configures power-management timing, records the preferred PCIe read request size, and applies that size when the PCI host is brought up.

Important APIs and functions: `bcma_core_pcie2_cfg_write()` writes indirect PCIe Gen2 config registers. `bcma_core_pcie2_war_delay_perst_enab()` toggles delayed PERST and SPROM-load clock-control bits for BCM4360 revisions. `bcma_core_pcie2_set_ltr_vals()` writes hard-coded LTR0-LTR2 values. `bcma_core_pcie2_hw_ltr_war()` applies the LTR workaround for core revisions 2-9 and 11-13, excluding 10. `pciedev_reg_pm_clk_period()` derives PM clock period from the chipcommon ALP clock. `bcma_core_pcie2_init()` is the main init entry; `bcma_core_pcie2_up()` calls `pcie_set_readrq()` on the host PCI device.

Control flow: init first checks a SPROM field and may write config offset `0x4e0`. It chooses `pcie2->reqsize` as 1024 for BCM4360/4352 and 128 otherwise. For BCM4360 rev > 3 it enables the delayed-PERST workaround, then runs LTR, low-power clock-generation placeholders, PM clock period, and mailbox/reference update workarounds in sequence.

State and persistence: software state is mainly `pcie2->reqsize` and `pcie2->core`. Hardware-visible state is stored in PCIe Gen2 config-indirect registers, clock control, LTR state, PM clock period, and mailbox registers. No memory ownership is created.

Dependencies and integration points: depends on BCMA core accessors `pcie2_read32/write32/set32`, chip IDs, chipcommon PMU clock calculation, and the Linux PCI `pcie_set_readrq()` helper. `main.c` initializes this core when `BCMA_CORE_PCIE2` unit 0 exists, and `host_pci.c` invokes runtime `up()` for PCI-host devices that scanned a PCIe2 core.

Risks: many values are magic hardware constants with partial TODO blocks, so behavior is fragile across new revisions. `pcie_set_readrq()` errors are logged but not recovered. Tests should cover BCM4360/4352 and default chips, read request size after probe/resume, LTR-enabled cores, and regression logs around PM clock period calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/driver_pcie2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/host_pci.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/host_pci.c

Purpose: implements the BCMA host adapter for Broadcom PCIe cards. It registers a PCI driver for supported Broadcom IDs, maps BAR0, provides BCMA core read/write operations over PCI BAR windows, scans/registers the BCMA bus, and exposes runtime PCI up/down and interrupt-routing controls to BCMA client drivers.

Important APIs and functions: `bcma_host_pci_switch_core()` programs `BCMA_PCI_BAR0_WIN` and a wrapper window, recording `bus->mapped_core`. `bcma_host_pci_provide_access_to_core()` uses fixed windows for chipcommon and PCIe cores and dynamic switching for others. The `bcma_host_pci_read/write{8,16,32}` and optional block I/O functions implement `struct bcma_host_ops`. `bcma_host_pci_probe()` owns PCI enablement, region request, BAR mapping, bus initialization, scan, and register. `bcma_host_pci_remove()` unwinds it. `bcma_host_pci_up()`, `bcma_host_pci_down()`, and exported `bcma_host_pci_irq_ctl()` are runtime integration hooks.

Control flow: PCI probe allocates a `bcma_bus`, enables and requests the PCI device, disables retry timeout, rejects non-PCIe cards, maps BAR0, initializes bus host fields and board info, scans cores, marks PCIe2 presence, registers BCMA devices, and stores bus drvdata. Remove unregisters BCMA devices before unmapping and disabling PCI resources. Suspend clears the mapped-core cache and delegates to `bcma_bus_suspend()`, while resume delegates to `bcma_bus_resume()`.

State and persistence: important state includes `bus->host_pci`, `bus->mmio`, `bus->host_is_pcie2`, `bus->mapped_core`, board vendor/type, and PCI drvdata. The interrupt mask in PCI config space is modified by `bcma_host_pci_irq_ctl()`.

Dependencies and integration points: Linux PCI driver core, module IDs, BAR ioread/iowrite APIs, optional `CONFIG_BCMA_BLOCKIO`, BCMA bus scan/register APIs from `main.c` and `scan.c`, and PCI/PCIe core runtime APIs from `driver_pci.c`/`driver_pcie2.c`.

Risks: window switching is global to the bus and protected only by expected upper-layer serialization; concurrent core accesses would be risky if host ops users do not serialize. Supported device IDs are static. Non-PCIe BCMA cards are rejected. Test signals include PCI probe/remove, suspend/resume, correct fixed/dynamic window access, IRQ mask toggling, and module alias matching for supported Broadcom IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/host_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/host_soc.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/host_soc.c

Purpose: provides BCMA host operations for memory-mapped Broadcom SoC buses. It supports early built-in SoC registration and Open Firmware platform-driver registration, mapping core and wrapper MMIO directly rather than using PCI windows.

Important APIs and functions: `bcma_host_soc_read/write{8,16,32}` directly access `core->io_addr`. Optional block I/O helpers perform raw repeated reads/writes for configured widths. `bcma_host_soc_aread32()` and `_awrite32()` access wrapper/agent registers through `core->io_wrap` and warn if absent. `bcma_host_soc_register()` maps the first core at `BCMA_ADDR_BASE` for early scan setup. `bcma_host_soc_init()` runs `bcma_bus_early_register()`. OF-enabled `bcma_host_soc_probe()` maps the platform resource, initializes the bus, and calls `bcma_bus_register()`.

Control flow: legacy early SoC registration first maps only one core because scanning discovers the rest. Later early init scans and initializes core infrastructure. The OF path allocates a bus with devm memory, maps the first resource from the device tree, initializes and registers the full bus, then stores platform drvdata. Remove unregisters the bus and unmaps MMIO.

State and persistence: `bus->mmio`, `bus->hosttype = BCMA_HOSTTYPE_SOC`, `bus->ops`, `bus->dev`, and per-core `io_addr/io_wrap` mappings are the primary state. Hardware register writes are direct SoC MMIO effects; no separate persistent storage is maintained.

Dependencies and integration points: depends on `scan.h` for base addresses, Linux OF address APIs, platform driver registration, BCMA bus scan/register from `main.c`, and per-core ioremap setup in `scan.c`. It supplies the `bcma_host_ops` used by all core drivers on SoC-hosted BCMA.

Risks: early registration maps a fixed physical base and only the first core, so platform assumptions are strict. Raw block I/O bypasses endian conversion beyond explicit little-endian pointer types. Wrapper accesses can return all ones when no wrapper exists. Test signals include OF compatible `brcm,bus-axi` probe, early SoC boot path, core wrapper access warnings, and correct IRQ/DMA configuration from device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/host_soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/main.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/main.c

Purpose: defines the BCMA Linux bus type and core lifecycle. It registers `struct bcma_device` objects discovered by the scanner, handles matching/probe/remove/uevent for BCMA drivers, initializes built-in cores in dependency order, exposes driver registration APIs, and wires module initialization for SoC and PCI hosts.

Important APIs and functions: `bcma_find_core_unit()` searches discovered cores by ID and unit. `bcma_wait_value()` polls core registers with timeout. `bcma_core_irq()` resolves IRQs for PCI, SoC MIPS, or OF-backed cores. `bcma_prepare_core()` initializes the embedded Linux device and DMA/IRQ fields. `bcma_init_bus()` assigns bus numbers and detects chip ID. `bcma_bus_register()` performs full scan, early chipcommon/PCI init, SPROM retrieval, core-specific initialization, and device registration. `bcma_bus_early_register()` is a non-sleeping early SoC variant. `__bcma_driver_register()` and `bcma_driver_unregister()` are exported for BCMA client drivers.

Control flow: full registration scans cores, initializes chipcommon early, initializes PCIe early for SPROM needs, populates OF children, registers NAND/QSPI early cores, retrieves SPROM, initializes chipcommon/chipcommon-B/MIPS/PCIe/PCIe2/GBIT common cores, then registers remaining externally driven cores. Unregister reverses GPIO, chipcommon-B, registered device, watchdog, and internal core state. Bus matching compares manufacturer, id, rev, and class against driver id tables with wildcard support.

State and persistence: global `bcma_bus_next_num` is protected by `bcma_buses_mutex`. Each bus owns a `cores` list, chipinfo, host fields, driver substructures, and Linux device registration flags. Per-core device lifetime is managed by `bcma_release_core_dev()`; mapped MMIO is unmapped there.

Dependencies and integration points: integrates with `scan.c`, `sprom.c`, chipcommon, MIPS, PCI/PCIe core drivers, GPIO/watchdog/flash platform devices, OF population, Linux driver core, and module init/exit. Host init functions are called for SoC always and PCI under `CONFIG_BCMA_HOST_PCI`.

Risks: registration ordering is critical because SPROM depends on early chipcommon/PCI and flash cores. Error handling logs many failures but may continue, e.g. missing SPROM. Device lifetime mixes registered and internally handled cores, making teardown sensitive. Test signals include module init, BCMA modalias generation, driver bind/unbind, suspend/resume callbacks, SPROM availability, and device-tree child matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/scan.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/scan.c

Purpose: discovers BCMA cores by parsing the hardware enumeration ROM. It detects chip identity, walks EROM component entries, filters bridges/non-core components, records core addresses and wrapper addresses, maps SoC cores, assigns core indexes and unit numbers, and prepares Linux devices for later registration.

Important APIs and functions: `bcma_detect_chip()` switches to the chipcommon base and reads `BCMA_CC_ID`. `bcma_bus_scan()` is the top-level scanner. EROM helpers include `bcma_erom_get_ent()`, `bcma_erom_get_ci()`, `bcma_erom_get_mst_port()`, `bcma_erom_get_addr_desc()`, and `bcma_erom_skip_component()`. `bcma_get_next_core()` parses component info words, port/wrapper counts, slave address descriptors, master/slave wrapper descriptors, applies match filtering, and maps SoC `io_addr`/`io_wrap`.

Control flow: scanning skips if `bus->nr_cores` is already nonzero. It obtains the EROM base from chipcommon; SoC hosts ioremap the EROM while PCI hosts use the mapped BAR window and switch BAR0 to the EROM base. It loops until the EROM end marker, allocating a `bcma_device` per candidate. Return codes from `bcma_get_next_core()` distinguish duplicate index, non-core/bridge, EROM end, invalid sequence, and allocation failure.

State and persistence: the scanner populates `bus->chipinfo`, `bus->nr_cores`, the `bus->cores` list, and each `bcma_device`'s ID, core index, unit, slave addresses, primary address, wrapper address, and SoC MMIO mappings. These objects persist until `bcma_unregister_cores()`.

Dependencies and integration points: depends on scan bit definitions from `scan.h`, BCMA register definitions, Linux MMIO APIs, PCI BAR window switching for PCI-hosted devices, and `bcma_prepare_core()` from `main.c`. Core names are local lookup tables for logging only.

Risks: EROM parsing is strict and returns `-EILSEQ` on unexpected descriptors, which can abort bus registration. The code ignores or skips bridges and ARM dummy components. SoC mapping failures can leak partial assumptions if wrapper mapping fails after core mapping. There is a likely cleanup concern: the final `iounmap(eromptr)` uses the advanced pointer rather than the original mapping. Test signals include scan logs for all expected cores, duplicate-index behavior, bridge skip logs, SoC ioremap/unmap checks, and successful rescans being no-ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/scan.h -->
# sources/distributed-fs/ceph-client/drivers/bcma/scan.h

Purpose: defines the BCMA scanner's physical base addresses and enumeration ROM bitfields. It is a private header consumed by `scan.c` and SoC host registration code.

Important definitions: `BCMA_ADDR_BASE` and `BCMA_WRAP_BASE` identify the standard SoC core and wrapper address ranges. `SCAN_ER_VALID`, `SCAN_ER_TAG`, `SCAN_ER_TAGX`, and tag constants classify EROM entries as component info, master port, address descriptor, or end. `SCAN_CIA_*` and `SCAN_CIB_*` masks decode core class, ID, manufacturer, master/slave ports, master/slave wrappers, and revision. `SCAN_ADDR_*` masks decode address descriptor size, type, port, 32-bit extension, and base address. `SCAN_SIZE_*` masks support explicitly sized descriptors.

Control flow role: this header has no executable flow, but its constants directly drive `bcma_erom_get_ci()`, `bcma_erom_get_addr_desc()`, and `bcma_get_next_core()`. A wrong mask changes how the scanner advances the EROM pointer and can turn valid cores into skipped components or invalid sequences.

State and persistence: no runtime state is defined. The values describe persistent hardware ROM formats and fixed SoC physical address conventions.

Dependencies and integration points: included by `scan.c` and `host_soc.c`; indirectly affects all BCMA bus registration because scanner output feeds `main.c`, PCI/SoC host ops, SPROM, and core driver initialization.

Risks: the comment on `SCAN_ER_TAGX` notes that bit 0x8 must be ignored for address tags; changing this would break address parsing. Constants assume 4 KiB alignment and 32-bit address descriptor layout. Test signals are indirect: chip scan should enumerate expected core IDs, revisions, wrappers, and addresses on known hardware, and malformed EROM should fail predictably rather than overrun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/sprom.c -->
# sources/distributed-fs/ceph-client/drivers/bcma/sprom.c

Purpose: locates, validates, and extracts BCMA SPROM data into `bus->sprom`. It supports external SPROM, on-chip OTP-backed SPROM, and architecture-provided fallback SPROM, then decodes revision 8-11 Broadcom calibration, board, GPIO, antenna, and power fields.

Important APIs and functions: `bcma_arch_register_fallback_sprom()` registers a platform callback. `bcma_sprom_get()` is the top-level retrieval API used by bus registration. `bcma_sprom_read()` reads 16-bit words from chipcommon SPROM space. `bcma_sprom_crc()`, `bcma_sprom_check_crc()`, and `bcma_sprom_valid()` validate CRC and supported revisions. `bcma_sprom_extract_r8()` performs the large field extraction using `SPEX`, `SPEX32`, and `SPEX_ARRAY8` macros. Availability helpers check external SPROM presence, on-chip OTP presence, and OTP offset.

Control flow: `bcma_sprom_get()` first requires a chipcommon core. It prefers external SPROM; when absent, it checks on-chip OTP and computes an offset; if neither is usable it calls the fallback callback. It temporarily disables external PA lines on BCM4331/43431, tries several SPROM word sizes, validates CRC/revision, restores PA lines, then either extracts fields or falls back after invalid reads.

State and persistence: decoded values persist in `bus->sprom`, including revision, board flags, MAC address, country code, per-core power info, FEM, antenna gain, PA curves, MCS/OFDM power offsets, temperature calibration, GPIOs, chains, and board metadata. `get_fallback_sprom` is a single global callback pointer.

Dependencies and integration points: depends on chipcommon registers/capabilities, SSB SPROM layout constants, BCMA chip IDs, PCI/SoC bus registration, and platform architecture callbacks. `main.c` calls this after early core setup and early flash-capable core registration.

Risks: only revisions 8-11 are accepted, so older/newer SPROM layouts require code changes. Fallback callback is global and only one can be registered. CRC or offset failures can silently move to fallback, masking bad hardware reads. Extraction is macro-heavy and easy to mis-map. Test signals include valid CRC on known SPROM dumps, fallback path for SPROM-less SoCs, OTP offset handling, BCM4331 PA-line toggling, and decoded regulatory/power fields matching hardware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bcma/sprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/block/Kconfig

Purpose: defines the Linux kernel configuration menu for block device drivers under `drivers/block`. It gates the entire block driver submenu behind `BLK_DEV`, sources subordinate Kconfig files, and declares selectable drivers such as floppy, loop, NBD, RAM disk, AoE, Xen, virtio, RBD, ublk, and zoned loop.

Important symbols: `menuconfig BLK_DEV` depends on `BLOCK` and defaults to enabled. Architecture-gated legacy drivers include `BLK_DEV_FD`, `AMIGA_FLOPPY`, `ATARI_FLOPPY`, `MAC_FLOPPY`, `BLK_DEV_SWIM`, `AMIGA_Z2RAM`, `N64CART`, and `GDROM`. Network/storage options include `BLK_DEV_NBD`, `ATA_OVER_ETH`, `BLK_DEV_RBD` with `select CEPH_LIB`, and `BLK_DEV_RNBD` through a sourced file. Virtualization options include UML UBD, Xen front/back, and `VIRTIO_BLK` selecting `SG_POOL`. Modern test/experimental options include `BLK_DEV_UBLK`, `BLKDEV_UBLK_LEGACY_OPCODES`, and `BLK_DEV_ZONED_LOOP`.

Control flow: Kconfig has declarative dependency flow. If `BLK_DEV=n`, all enclosed options are skipped. Sourced Kconfigs are included in menu order. Driver choices then control object inclusion in `drivers/block/Makefile` and subdirectory Makefiles.

State and persistence: configuration state persists in the kernel `.config` and controls compile-time object selection, module availability, selected dependencies, and help text exposed to configurators.

Dependencies and integration points: feeds the block driver Makefile, architecture symbols, networking, Xen, virtio, Ceph, io_uring, and sourced submenus. The `ATA_OVER_ETH` symbol is consumed by `drivers/block/aoe/Makefile`.

Risks: dependency mistakes can expose drivers on unsupported platforms or hide valid combinations. Help text may become stale relative to documentation. Test signals are Kconfig parsing (`make oldconfig`/`allyesconfig`/arch configs), expected object inclusion for selected symbols, and dependency propagation such as `BLK_DEV_RBD` selecting Ceph support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/Makefile -->
# sources/distributed-fs/ceph-client/drivers/block/Makefile

Purpose: maps block driver Kconfig symbols to built-in or modular objects for the kernel build. It is the primary build manifest for `drivers/block`.

Important entries: `ccflags-y += -I$(src)` makes local headers available for trace events. Object mappings include floppy variants (`floppy.o`, `amiflop.o`, `ataflop.o`, `swim3.o`, `swim_mod.o`), memory/virtual drivers (`z2ram.o`, `brd.o`, `loop.o`, `zloop.o`), network/storage drivers (`nbd.o`, `rbd.o`, `drbd/`, `rnbd/`), virtualization drivers (`virtio_blk.o`, Xen front/back), PS3 drivers, null block, Rust null block, ublk, and mtip32xx. `swim_mod-y` combines `swim.o` and `swim_asm.o`.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` assignment according to the final kernel configuration. `y` entries link built-in objects; `m` entries produce modules where supported; directory entries recurse into subdirectories.

State and persistence: no runtime state. Build state is produced in object/module artifacts based on `.config`.

Dependencies and integration points: tightly coupled to `drivers/block/Kconfig`; every referenced `CONFIG_*` should be defined there or in a sourced Kconfig. `CONFIG_ATA_OVER_ETH` is intentionally handled by `drivers/block/aoe/Makefile`, so this file does not list AoE directly in the viewed excerpt.

Risks: stale mappings cause selected drivers not to build or unselected code to build. Missing composite object lists break module links. Test signals include `make drivers/block/`, randconfig build coverage, and confirming `CONFIG_AMIGA_FLOPPY=m/y` produces `amiflop.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/amiflop.c -->
# sources/distributed-fs/ceph-client/drivers/block/amiflop.c

Purpose: implements the Amiga floppy block driver. It supports up to four drives, Amiga and MS-DOS sector layouts, raw MFM track encoding/decoding, formatting ioctls, media change detection, blk-mq request handling, and direct Amiga custom-chip/CIAA hardware control.

Important APIs and types: `struct fd_drive_type` describes physical drive timing/capacity, `struct fd_data_type` selects Amiga or MS-DOS codec functions, and `struct amiga_floppy_struct` holds per-drive state including type, layout, track buffer, dirty flag, gendisks, and tag set. Hardware helpers include `ms_delay()`, `get_fdc()/rel_fdc()`, `fd_select()/fd_deselect()`, `fd_motor_on/off()`, `fd_calibrate()`, `fd_seek()`, `raw_read()`, and `raw_write()`. Format codecs are `amiga_read/write()` and `dos_read/write()` plus checksum/CRC/MFM helpers. Block entry points are `amiflop_queue_rq()`, `floppy_open()`, `floppy_release()`, `fd_ioctl()`, and `amiga_check_events()`.

Control flow: platform probe registers the floppy major, allocates chip RAM `raw_buf`, requests disk DMA and CIA timer IRQs, probes drive IDs, allocates per-drive blk-mq disks for native and MS-DOS layouts, initializes timers and decode tables, and enables disk DMA. A request enters `amiflop_queue_rq()`, grabs a global spinlock, starts the request, then processes current sectors. `get_track()` ensures the motor is on, flushes dirty track buffers, seeks and reads a raw track, and decodes it. Reads copy from the track buffer; writes update the track buffer, mark it dirty, and schedule a near-term flush timer. Formatting ioctls fill a track and flush it.

State and persistence: per-drive state includes current track, motor state, selected disk layout, dirty track buffer, disk capacity, open alias tracking (`fd_ref`, `fd_device`), and timers for motor off, write flush, post-write delay, and motor spin-up completion. Disk data persists only after raw track write completion; dirty buffers are volatile until flushed.

Dependencies and integration points: depends on Amiga-specific CIA/custom registers, IRQs `IRQ_AMIGA_DSKBLK` and `IRQ_AMIGA_CIAA_TB`, chip memory allocation, Linux block major `FLOPPY_MAJOR`, blk-mq, legacy floppy ioctls, and platform driver alias `amiga-floppy`.

Risks: extensive global state and interrupt/timer interactions create race risk. Some waits and write completion paths depend on hardware timing and comments note assumptions about motor spin. `IOCTL_RAW_TRACK` copies raw data without richer validation. Error recovery retries with recalibration but may lose pending writes on media change. Test signals include boot probe on Amiga hardware, native and MS-DOS read/write/format, write-protect behavior, media-change events, delayed flush completion, and blk-mq stress with multiple aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/amiflop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/block/aoe/Makefile

Purpose: builds the ATA over Ethernet driver as a composite Kbuild object when `CONFIG_ATA_OVER_ETH` is enabled.

Important entries: `obj-$(CONFIG_ATA_OVER_ETH) += aoe.o` selects the composite object as built-in or module. `aoe-y := aoeblk.o aoechr.o aoecmd.o aoedev.o aoemain.o aoenet.o` defines the compilation units linked into that object.

Control flow: Kbuild links the listed objects in the composite `aoe.o`. Runtime module entry and exit come from `aoemain.o`; the rest provide block, character, command, device, and network subsystems.

State and persistence: no runtime state. Build outputs depend on `.config` and Kbuild's built-in/module selection.

Dependencies and integration points: consumes `CONFIG_ATA_OVER_ETH` from `drivers/block/Kconfig`, and all objects share declarations in `aoe.h`. Any new AoE source file must be added here to link into the module.

Risks: object omission causes unresolved symbols or missing functionality at runtime. Test signals are `CONFIG_ATA_OVER_ETH=y/m` builds and module symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoe.h -->
# sources/distributed-fs/ceph-client/drivers/block/aoe/aoe.h

Purpose: central private header for the AoE driver. It defines protocol wire headers, driver constants, device/target/frame/request state structures, flags, and cross-file function prototypes.

Important APIs and types: protocol structs `aoe_hdr`, `aoe_atahdr`, and `aoe_cfghdr` model Ethernet AoE, ATA command, and config payloads. `struct aoedev` is the main device object, holding AoE address, flags, disk/queue/tag set, geometry, request list, timers, skb pool, target array, active-frame hash, retransmit queue, and in-progress request pointers. `struct aoetgt` tracks one remote MAC target, congestion window state, free frames, interfaces, taint, and packet counts. `struct frame` tracks one outstanding AoE command, skb, tag, sent time, target, bio iterator, and response skb. `struct buf` bridges blk-mq requests/bios to frames. `struct ktstate` abstracts driver kthreads.

Control flow role: no executable code, but it defines the contracts between `aoeblk.c` queueing, `aoecmd.c` frame construction/completion, `aoedev.c` lifecycle, `aoechr.c` control devices, `aoenet.c` packet I/O, and `aoemain.c` module init.

State and persistence: enumerated `DEVFL_*` flags encode device lifecycle, including up, timer kill, LBA48, gendisk allocation, size updates, freeing/freed, and dead timeout. AoE storage identity persists in `aoedev.ident`, geometry, size, target list, and firmware version until flush or module unload.

Dependencies and integration points: includes blk-mq and references Linux block, networking, mempool, timers, sk_buffs, workqueues, and debugfs through the implementation files. Public constants include `AOE_MAJOR`, `DEVICE_NAME`, `AOE_PARTITIONS`, and `VERSION`.

Risks: shared mutable structures are accessed under several locks and kthreads; flag semantics must remain consistent across files. Changing struct layout or flag meaning has driver-wide effects. Test signals include compile coverage for all AoE objects, lockdep/runtime tests for target/device transitions, and protocol interop with AoE shelves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoeblk.c -->
# sources/distributed-fs/ceph-client/drivers/block/aoe/aoeblk.c

Purpose: provides the Linux block-device front end for AoE devices. It creates gendisks and blk-mq queues, exposes sysfs/debugfs state, queues requests into the AoE command engine, handles open/release/ioctl/getgeo, and owns the per-device `struct buf` slab cache.

Important APIs and functions: sysfs show functions expose state, MAC, network interfaces, firmware version, and payload size. `aoe_debugfs_show()` reports RTT, skb pool, target frame state, congestion, taint, and interface names. `aoeblk_open()` validates device state and increments `nopen`. `aoeblk_release()` decrements and triggers config rediscovery on last close. `aoeblk_queue_rq()` starts by checking `DEVFL_UP`, appends requests to `d->rq_list`, and calls `aoecmd_work()`. `aoeblk_gdalloc()` performs sleeping disk allocation from workqueue context. `aoeblk_init/exit()` create and destroy the buffer cache and debugfs root.

Control flow: `aoecmd` identifies a remote device and sets `DEVFL_GDALLOC`; deferred work calls `aoeblk_gdalloc()`. Disk allocation creates a mempool for `struct buf`, initializes a blk-mq tag set, allocates a disk with queue limits, fills major/minor/name/private data, sets `DEVFL_UP`, calls `device_add_disk()` with AoE attributes, and registers debugfs. Queue requests remain under `d->lock` and are transformed asynchronously by `aoecmd.c`.

State and persistence: per-device block state includes `gd`, `blkq`, `tag_set`, `bufpool`, `nopen`, `ssize`, and sysfs/debugfs visibility. The module parameter `aoe_maxsectors` controls maximum request sectors.

Dependencies and integration points: depends on `aoe.h`, Linux blk-mq, gendisk, sysfs attribute groups, debugfs, mempools, and command/device code. It calls `aoecmd_cfg()` on release and `aoecmd_work()` on queueing.

Risks: allocation failure requeues work and can loop if memory pressure persists. `aoeblk_queue_rq()` returns I/O error for down devices after starting the request but does not complete it in the same branch, which is a behavior worth verifying against blk-mq expectations. Test signals include disk creation after AoE discovery, sysfs/debugfs contents, open/close rediscovery, request completion under load, and teardown while requests are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoeblk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoechr.c -->
# sources/distributed-fs/ceph-client/drivers/block/aoe/aoechr.c

Purpose: implements AoE control and error character devices under `/dev/etherd/`. It supports discovery, interface filtering, device revalidation, flushing, and a blocking error-message stream.

Important APIs and functions: `aoe_devnode()` places devices under `etherd/`. `discover()` broadcasts AoE config requests. `interfaces()` updates the network interface allowlist through `set_aoe_iflist()`. `revalidate()` parses an `eX.Y` device string, clears command state, sends config, obtains an ATA identify skb, and transmits it. `aoechr_error()` appends messages to a fixed ring buffer. `aoechr_write()` dispatches control writes by minor. `aoechr_read()` blocks on `/dev/etherd/err` until an error message is available. `aoechr_init/exit()` register major 152 char devices and class entries.

Control flow: users open one of the known minors (`err`, `discover`, `interfaces`, `revalidate`, `flush`). Writes to control devices synchronously call the subsystem function and return the byte count on success. Error producers call `aoechr_error()` from other AoE files; readers either receive the next queued message, get `-EAGAIN` for nonblocking/no-space cases, or sleep on a completion until a message arrives.

State and persistence: state includes a 100-entry ring of `ErrMsg` objects, per-message allocated strings, head/tail indexes, reader wait completion, `nblocked_emsgs_readers`, and the registered device class. Messages persist only until consumed or overwritten refusal when the tail slot is still valid.

Dependencies and integration points: interacts with `aoecmd_cfg()`, `aoecmd_cleanslate()`, `aoecmd_ata_id()`, `aoenet_xmit()`, `aoedev_by_aoeaddr()`, `aoedev_flush()`, and `set_aoe_iflist()`. It uses the shared AoE major, Linux char device registration, class device creation, completions, spinlocks, and user-copy APIs.

Risks: if the error ring fills, new messages are silently dropped. `revalidate()` loops with sleeps until an identify skb can be allocated/transmitted, so user writes can block. Input parsing uses a small fixed buffer and requires `e%d.%d`. Test signals include `/dev/etherd/discover` triggering config packets, `interfaces` allowlist changes, `err` blocking/nonblocking reads, flush/revalidate commands, and cleanup of device nodes on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoechr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoecmd.c -->
# sources/distributed-fs/ceph-client/drivers/block/aoe/aoecmd.c

Purpose: core AoE command engine. It converts block requests into AoE ATA Ethernet frames, handles config and ATA responses, manages targets/interfaces/congestion windows, retransmits timed-out frames, completes bios in kthreads, and identifies devices to create or resize disks.

Important APIs and functions: `aoecmd_work()` drains retransmits and emits new ATA read/write frames. `aoecmd_cfg()` broadcasts config requests; `aoecmd_cfg_rsp()` handles config responses and target/interface setup. `aoecmd_ata_id()` builds ATA identify commands. `aoecmd_ata_rsp()` matches responses by tag, updates RTT, and queues completion work. `ktiocomplete()` validates ATA status, copies read data into bios, updates identify data through `ataid_complete()`, frees frames, and completes buffers. `rexmit_timer()` detects timeouts, taints targets, retransmits or fails devices after `aoe_deadsecs`. Kthread helpers `aoe_ktstart/stop()`, `ktio()`, and `ktcomplete()` process completions off receive context.

Control flow: blk-mq requests queued by `aoeblk.c` are converted by `nextbuf()` into `struct buf`, split into frame-sized chunks, assigned to a target by `newframe()`, tagged by `newtag()`, placed in the active hash, cloned, and sent through `aoenet_xmit()`. Responses enter from `aoenet.c`, remove frames from active/deferred queues, schedule more work, and hand completion to per-CPU-ish ktio queues. Config responses allocate/find `aoedev`, add/update `aoetgt`, compute payload size from MTU and shelf sector count, and issue identify if not open.

State and persistence: state includes global module parameters `aoe_deadsecs` and `aoe_maxout`, CPU-count-based ktio arrays, `empty_page` for probes, active frame hashes, retransmit queues, target congestion (`maxout`, `ssthresh`, `next_cwnd`), RTT estimates, target taint, skb pools, and per-request bio counters. Identified capacity/geometry and identity strings persist in `aoedev`.

Dependencies and integration points: depends on Linux ATA constants, blk-mq request APIs, sk_buff fragment APIs, net namespace iteration, workqueues, kthreads, unaligned access helpers, and other AoE modules for device lookup, block disk allocation, char error logging, and network transmit.

Risks: concurrency is complex: frames move among active hashes, deferred retransmit queues, ktio queues, and free lists under different locks. Tag space embeds jiffies and can wrap. Timeout/taint logic can down devices during transient network stalls. Data copying assumes response sizes match command sectors. Test signals include AoE read/write correctness, retransmit under packet loss, multipath target taint/recovery, identify/resize behavior, ktio scaling, module unload with pending completions, and lockdep under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoecmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoedev.c -->
# sources/distributed-fs/ceph-client/drivers/block/aoe/aoedev.c

Purpose: manages the global AoE device list, minor allocation, device lookup/allocation, downing and flushing devices, target/frame cleanup, skb-pool cleanup, and module-exit teardown.

Important APIs and functions: `aoedev_by_aoeaddr()` finds or allocates an `aoedev` for an AoE major/minor address and increments its reference. `aoedev_put()` releases lookup references. `aoedev_downdev()` marks a device down, fails active/retransmit/in-progress/queued I/O, resets target windows, freezes/quiesces blk-mq queues, and zeroes disk capacity. `aoedev_flush()` parses user flush requests and delegates to `flush()`. `freedev()` deletes timers, gendisks, tag sets, mempools, targets, skb pools, and minor allocation. `minor_get_dyn/static()` and `minor_free()` manage block minors. `freetgt()` releases netdev refs and frames.

Control flow: discovery/config code calls `aoedev_by_aoeaddr(..., do_alloc=1)` to create devices with target array, work item, lock, request list, skb pool, dummy timer, active frame buckets, minor, RTT defaults, and list insertion. Flush/exit is multi-pass: first mark eligible devices `DEVFL_TKILL` after downing them, second call sleeping `freedev()`, third unlink and free devices whose resources are gone. Eligibility differs for exit, explicit specific/all flush, open devices, refs, and pending allocation/resize flags.

State and persistence: global `devlist` is protected by `devlist_lock`. Minor usage persists in `used_minors`. Per-device lifecycle flags include up/dead/tkill/freeing/freed and allocation/resize state. Device refs protect ktio-held frames. Timer state persists until device free.

Dependencies and integration points: called by `aoecmd.c`, `aoechr.c`, and `aoemain.c`; depends on blk-mq queue freeze/quiesce, gendisk teardown, mempool destroy, sk_buff lifetime checks, netdev references, and AoE shared structures.

Risks: manual reference counting is narrow and comments acknowledge limited confidence under async flushes. `skbfree()` can leak after waiting 30 seconds if another holder keeps a reference. Flush eligibility can leave devices alive when open or referenced. Test signals include dynamic/static minor collision tests, `echo all > /dev/etherd/flush`, explicit device flush, module unload with active I/O, down-device fast-fail behavior, and no leaked netdev/skb/disk resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoedev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoemain.c -->
# sources/distributed-fs/ceph-client/drivers/block/aoe/aoemain.c

Purpose: module initialization and teardown coordinator for the AoE driver. It creates the shared workqueue, initializes AoE subsystems in dependency order, registers the block major, and runs a periodic discovery timer.

Important APIs and functions: `aoe_init()` is the module entry point. `aoe_exit()` is the module exit point. `discover_timer()` reschedules itself every 60 seconds and sends a broadcast config query through `aoecmd_cfg(0xffff, 0xff)`. `aoe_wq` is the global workqueue used for sleeping device/disk work.

Control flow: init allocates `aoe_wq`, then initializes device, character, block, network, and command subsystems. Only after these are ready does it register block major 152 and start discovery. Error labels unwind previously initialized subsystems in reverse partial order. Exit deletes the timer, shuts down networking, unregisters the block major, stops command kthreads, removes char devices, flushes/frees devices, frees block caches, and destroys the workqueue.

State and persistence: module state includes `aoe_wq` and the discovery `timer_list`. Module metadata declares GPL license, author, description, and `VERSION`. Runtime device state is delegated to other files.

Dependencies and integration points: depends on all AoE subsystem init/exit functions and on shared constants from `aoe.h`. The order matters: block cache must outlive device buffer deallocation, and command/network subsystems must be available for discovery.

Risks: if init ordering changes, discovery or cleanup can run without required subsystems. The periodic discovery timer emits network traffic every minute while loaded. Test signals include successful module load/unload, init failure injection at each stage, discovery packet emission, no timer after unload, and correct cleanup ordering with discovered devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoemain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoenet.c -->
# sources/distributed-fs/ceph-client/drivers/block/aoe/aoenet.c

Purpose: network transport layer for AoE. It filters allowed interfaces, queues transmit skbs to a dedicated kthread, registers an Ethernet packet handler for `ETH_P_AOE`, validates incoming AoE responses, dispatches ATA/config responses, and exposes the `aoe_iflist` module/boot parameter.

Important APIs and functions: `is_aoe_netif()` checks whether a net_device is allowed by the whitespace/comma-separated `aoe_iflist`. `set_aoe_iflist()` updates that list from userspace. `aoenet_xmit()` moves skbs from caller queues to the global transmit queue and wakes the tx kthread. `tx()` drains `skbtxq` and calls `dev_queue_xmit()`, dropping netdev refs after send. `aoenet_rcv()` is the packet_type receive callback; it ensures init_net, allowed interface, sufficient header linearization, response bit, non-user tag, no AoE error, and dispatches by command. `aoenet_init/exit()` set up the tx queue/kthread and packet handler.

Control flow: transmit callers prepare skbs with `skb->dev` held, call `aoenet_xmit()`, and return; the tx kthread serially sends packets. Receive path gets all AoE Ethernet packets from `dev_add_pack()`, shares/checks skb, pushes Ethernet header back into length accounting, handles protocol errors, then calls `aoecmd_ata_rsp()` or `aoecmd_cfg_rsp()`. ATA response handling may consume the skb asynchronously; config handling is synchronous.

State and persistence: global state includes `aoe_iflist`, tx waitqueue, `ktstate`, `txlock`, and `skbtxq`. Interface filtering persists until module parameter/user write changes it.

Dependencies and integration points: depends on Linux netdevice packet handlers, init network namespace, sk_buffs, `dev_queue_xmit()`, netdev refs, AoE protocol structures, char control path for interface list updates, and command response handlers.

Risks: only `init_net` is supported. Misconfigured `aoe_iflist` can hide devices or transmit on unintended interfaces when empty means all interfaces. Receive path drops vendor commands silently and logs protocol errors rate-limited. Test signals include interface allowlist parsing, packet receive on allowed/disallowed netdevs, tx queue drain under drops, AoE error packet logging, ATA/config dispatch, and cleanup after packet handler removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/aoe/aoenet.c -->
