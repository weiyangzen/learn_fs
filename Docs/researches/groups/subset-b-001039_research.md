<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_hpt37x.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_hpt37x.c

## Purpose

`pata_hpt37x.c` is the libata PCI low-level driver for non-N-series HighPoint HPT37x/HPT30x PATA controllers, including HPT370, HPT370A, HPT371, HPT372, HPT372A, HPT302, and HPT374 variants. It translates PCI revision/device IDs into the right libata port operations, transfer masks, cable detection rules, timing tables, and clock policy. The core job is to make these older BMDMA PCI IDE controllers appear as normal libata hosts while preserving the many chip-specific timing, DPLL, reset, and DMA-engine workarounds inherited from the legacy IDE driver.

## Important APIs, Types, And Functions

The key private types are `struct hpt_clock`, which maps an `XFER_*` mode to a 32-bit controller timing word, and `struct hpt_chip`, which describes a chip name, base clock divisor, and timing tables for 33/40/50/66 MHz slots. `hpt37x_find_mode()` looks up the timing word from `ap->host->private_data`, which is seeded at probe time with the chosen timing table. `hpt37x_set_piomode()` and `hpt37x_set_dmamode()` both call `hpt37x_set_mode()`, which masks and rewrites the appropriate PCI timing register for the selected device.

Mode filtering is split by chip generation. `hpt370_filter()` blocks UDMA on known-problem Maxtor ATA33 drives and masks UDMA100 modes for listed IBM/WDC devices; `hpt370a_filter()` applies only the UDMA100 blacklist; `hpt372_filter()` strips UDMA1-3 and all MWDMA for SATA identify data, matching Marvell bridge limitations on some HighPoint SATA cards. Cable detection is handled by `hpt37x_cable_detect()` for normal functions and `hpt374_fn1_cable_detect()` for HPT374 function 1. Reset and DMA cleanup are customized through `hpt37x_pre_reset()`, `hpt370_bmdma_stop()`, and `hpt37x_bmdma_stop()`.

## Control Flow

Module registration is conventional PCI: `module_pci_driver(hpt37x_pci_driver)` binds IDs from the `hpt37x[]` table and enters `hpt37x_init_one()`. Probe first enables the PCI function, rejects revisions handled by other drivers, selects an `ata_port_info`, chooses a `hpt_chip` descriptor, and handles HPT371/HPT374 topology quirks. It then programs PCI latency/cache/min/max grant defaults, clears an interrupt mask bit, forces MA15/16 output, performs HPT372A I/O-space setup, detects the PCI bus clock via `hpt37x_pci_clock()`, and either uses a direct timing table or calibrates a DPLL with `hpt37x_calibrate_dpll()`. Finally it calls `ata_pci_bmdma_init_one()` with the selected port info and timing table as host private data.

At runtime libata calls the port operations. Reset first checks per-port enable bits and resets the channel state machine. Mode programming is per device and preserves unrelated timing fields via masks. BMDMA stop paths add controller-specific engine clearing before or after the generic `ata_bmdma_stop()`.

## State, Dependencies, And Integration Points

Persistent driver state is minimal and lives in PCI configuration space plus `host->private_data`. The chosen clock table is stored as host private data and read by every timing update. HPT371 channel absence and HPT374 function differences are persisted by PCI register writes. Dependencies are the PCI core, libata SFF/BMDMA helpers, `scsi_host_template` glue through `ATA_BMDMA_SHT()`, and low-level I/O helpers such as `inl()`, `outb()`, `pci_read_config_*()`, and `pci_write_config_*()`. The driver integrates with libata through `ata_port_operations` inheritance from `ata_bmdma_port_ops` and through normal PCI remove/suspend support delegated to libata helpers.

## Risks And Test Signals

The highest-risk areas are clock detection, DPLL stabilization, revision routing to the correct sibling driver, and timing masks in `hpt37x_set_mode()`. A wrong clock table can silently corrupt data at high DMA modes. The blacklists and SATA bridge filter are also behavioral compatibility risks because they intentionally reduce advertised capabilities. Useful tests include boot/probe on each supported revision, cable detection on both ports and HPT374 functions, fallback when BIOS clock data is absent, DPLL failure handling, mode negotiation with blacklisted devices, and DMA timeout/error injection to confirm the BMDMA stop workarounds clear active engines without hanging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_hpt37x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_hpt3x2n.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_hpt3x2n.c

## Purpose

`pata_hpt3x2n.c` supports the HighPoint HPT371N, HPT372N, and HPT302N generation, which is separated from `pata_hpt37x.c` because the N-series chips use a different DPLL/clock switching policy. It is still a libata PCI BMDMA driver, but it assumes a 66 MHz DPLL timing table and dynamically switches between the PCI clock and DPLL around command issue when necessary. This is required for writes, 66 MHz PCI, and some high-speed paths, while reads can sometimes use the PCI clock.

## Important APIs, Types, And Functions

The driver uses `struct hpt_clock` and a single `hpt3x2n_clocks[]` table mapping transfer modes through UDMA7 to timing words. `hpt3x2n_find_mode()` resolves transfer mode timing, and `hpt3x2n_set_mode()` writes masked PCI timing fields for PIO, MWDMA, and UDMA. `hpt372n_filter()` applies the same SATA bridge limitation as the HPT372 path, removing UDMA1-3 and MWDMA when identify data reports SATA.

The distinctive runtime hooks are `hpt3x2n_qc_defer()` and `hpt3x2n_qc_issue()`. They use `hpt3x2n_use_dpll()` to decide whether the upcoming command requires the DPLL, store current clock flags in `host->private_data`, and call `hpt3x2n_set_clock()` to tristate the bus, switch the clock source, reset internal state machines, and reconnect channels. `hpt3x2n_bmdma_stop()` mirrors the later HPT37x cleanup by checking BWSR/MSC state and forcing recovery bits before generic BMDMA stop.

## Control Flow

`hpt3x2n_init_one()` enables the PCI device, rejects revisions owned by the non-N driver, maps HPT366/HPT371/HPT372/HPT302/HPT372N IDs to either generic N-series or HPT372N port info, configures latency/cache PCI registers, clears the interrupt mask bit, disables the phantom HPT371 primary channel, computes the PCI clock, and programs/calibrates the 66 MHz DPLL. It initializes `hpriv` with `USE_DPLL`, adding `PCI66` when the bus is above 60 MHz, then calls `ata_pci_bmdma_init_one()`.

At command time, libata first asks `qc_defer()`. If a clock switch is needed while the paired port has active commands, the command is deferred with `ATA_DEFER_PORT`. `qc_issue()` performs the actual clock change only when the desired DPLL state differs from `host->private_data`, then delegates to `ata_bmdma_qc_issue()`.

## State, Dependencies, And Integration Points

State is encoded compactly in `host->private_data` as `PCI66` and `USE_DPLL` flags. Timing tables are global and fixed. The driver depends on PCI config/I/O space, libata BMDMA/SFF callbacks, and scsi host template glue. Its integration points are the PCI ID table, `ata_bmdma_port_ops` inheritance, custom command defer/issue hooks, and reset/cable/mode programming callbacks.

## Risks And Test Signals

The most important risk is concurrent two-port access during clock transitions; `qc_defer()` is the guard that prevents switching clocks under another active command. DPLL calibration has no frequency-jiggle fallback unlike the HPT37x driver, so marginal hardware may fail probe. Tests should cover paired-port read/write workloads that alternate DPLL requirements, HPT371N single-channel masking, SATA bridge mode filtering, DPLL failure, 66 MHz PCI detection, cable detection, suspend/resume via libata PCI helpers, and DMA stop recovery after controller-reported bus status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_hpt3x2n.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_hpt3x3.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_hpt3x3.c

## Purpose

`pata_hpt3x3.c` is the libata driver for HighPoint HPT343/HPT363 controllers. These chips are older and simpler than the HPT37x family but have nonstandard BAR4 taskfile layout and errata around DMA and freeze handling. The driver programs PIO timing unconditionally and conditionally enables DMA support under `CONFIG_PATA_HPT3X3_DMA`.

## Important APIs, Types, And Functions

`hpt3x3_set_piomode()` writes PCI config registers `0x44` and `0x48`, encoding a three-bit PIO timing value per device and clearing MWDMA/UDMA enable bits. When DMA support is compiled in, `hpt3x3_set_dmamode()` writes the same timing field with a DMA mode number and sets either the MWDMA or UDMA bit. `hpt3x3_freeze()` stops any pending DMA before calling `ata_sff_dma_pause()` and `ata_sff_freeze()` because writing the control register during active DMA can hang the chip. `hpt3x3_bmdma_setup()` clears interrupt/error/active bits before generic setup, and `hpt3x3_atapi_dma()` rejects ATAPI DMA.

The port operations inherit from `ata_bmdma_port_ops`, use `ata_cable_40wire`, and wire in PIO plus optional DMA callbacks. `hpt3x3_init_chipset()` initializes board register `0x80` and sets latency differently for HPT343 versus HPT363 based on `PCI_COMMAND_MEMORY`.

## Control Flow

`hpt3x3_init_one()` initializes chipset registers, allocates a two-port libata host, enables the PCI device, maps BAR4, sets a coherent DMA mask, and manually assigns each port's taskfile/control/BMDMA addresses relative to BAR4 offsets. It then sets the device bus master and activates the host with `ata_bmdma_interrupt()`. Resume calls `ata_pci_device_do_resume()`, reruns chipset initialization, and resumes the libata host.

Mode configuration is driven by libata after device discovery. PIO setup always leaves DMA disabled in config bits until a DMA mode is explicitly selected. The DMA freeze/setup hooks protect known hardware edge cases before using generic BMDMA mechanisms.

## State, Dependencies, And Integration Points

The driver keeps no heap private state. Persistent hardware state is in PCI config registers and BAR4 I/O registers. It depends on PCI managed resource mapping, DMA mask setup, libata BMDMA/SFF helpers, and optional power management. Integration is through a single PCI ID for `PCI_DEVICE_ID_TTI_HPT343`, a custom BAR4 address map, and `ata_host_activate()` rather than `ata_pci_bmdma_init_one()` because the normal PCI IDE BAR layout is not usable.

## Risks And Test Signals

Risks include incorrect BAR4 offsets, compile-time divergence with and without `CONFIG_PATA_HPT3X3_DMA`, and DMA hangs if freeze/setup ordering regresses. Test signals include probe on both 343-like and 363-like command-memory configurations, PIO mode transitions for master/slave on both ports, optional MWDMA/UDMA operation, ATAPI fallback to PIO, resume reinitialization, and forced error/freeze paths while DMA is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_hpt3x3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_icside.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_icside.c

## Purpose

`pata_icside.c` supports ICS IDE expansion cards on Acorn/RiscPC-style systems through the ARM expansion-card bus. It handles several card interface types, maps their unusual memory layouts into libata SFF ports, manages expansion-card IRQ enable/disable behavior, and optionally uses the platform IOMD DMA controller for MWDMA. The driver is board/platform-specific rather than PCI-based.

## Important APIs, Types, And Functions

`struct portinfo` describes taskfile data/control offsets and register spacing. `struct pata_icside_state` is host-private runtime state: IRQ base, IOC base, card type, DMA channel, per-port select values, disabled flags, and per-device DMA cycle timings. `struct pata_icside_info` is probe-time assembly state containing the expansion card, mapped bases, IRQ ops, resource addresses, supported DMA mask, and port descriptors.

Version-specific IRQ operations are implemented as `pata_icside_irqenable_arcin_v5()`, `pata_icside_irqdisable_arcin_v5()`, and the V6 equivalents with `pata_icside_irqpending_arcin_v6()`. DMA support is custom: `pata_icside_set_dmamode()` computes ATA timing, chooses an IOMD DMA cycle class, and records a cycle value; `pata_icside_bmdma_setup()`, `pata_icside_bmdma_start()`, `pata_icside_bmdma_stop()`, and `pata_icside_bmdma_status()` drive the shared IOMD DMA channel instead of a PCI BMDMA engine. `pata_icside_postreset()` disables empty V6 ports to avoid floating interrupt lines.

## Control Flow

`pata_icside_probe()` requests expansion-card resources, allocates state, reads card type bits from `ICS_IDENT_OFFSET`, and dispatches to V5 or V6 registration. V5 maps MEMC space, registers one port, and uses one IRQ status register. V6 maps IOCFAST and optionally EASI space, sets port selectors, registers two ports, and initializes DMA if an expansion-card DMA channel is available. `pata_icside_add_ports()` installs IRQ operations, disables interrupts for safety, allocates a libata host, marks it `ATA_HOST_SIMPLEX`, fills each port's SFF addresses, and activates with `ata_bmdma_interrupt()`.

Removal detaches the host, disables card interrupts, resets the IOC selector to make ROM readable after soft reboot, frees the DMA channel, and releases expansion-card resources.

## State, Dependencies, And Integration Points

State persists in `pata_icside_state`, expansion-card IRQ hooks, the shared DMA channel, and hardware selector registers. Dependencies include `asm/ecard.h`, `asm/dma.h`, libata SFF/BMDMA helpers, ARM IOMD DMA APIs, and expansion-card resource management. The libata integration is custom because the SFF register spacing and DMA engine are platform-specific; the driver also sets a custom SCSI host template with `SG_MAX_SEGMENTS` and `IOMD_DMA_BOUNDARY`.

## Risks And Test Signals

The largest risks are shared simplex DMA misuse, incorrect card-type detection, V6 floating interrupts from empty ports, and mismatched IOC/EASI selector programming. `BUG_ON(dma_channel_active())` makes concurrent DMA misuse fatal. Tests should cover V5 one-port and V6 two-port cards, unsupported A3IN/A3USER rejection, no-DMA fallback, DMA timing selection for MWDMA modes, port disable after empty reset, shutdown path resetting EASI access, and remove/unload with active expansion-card resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_icside.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_imx.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_imx.c

## Purpose

`pata_imx.c` is the platform driver for the Freescale i.MX PATA block, specifically matching `fsl,imx27-pata`. It provides PIO-only libata access with 32-bit data transfers, programs controller timing registers from the enabled peripheral clock, deasserts controller resets, enables ATA interrupts, and handles suspend/resume clock and register restoration.

## Important APIs, Types, And Functions

The driver state is `struct pata_imx_priv`, containing the enabled `clk`, mapped host timing/control registers, and a saved `ata_ctl` value for suspend. `pata_imx_set_timing()` computes timing values with `ata_timing_compute()` using the clock period and writes i.MX timing registers such as `PATA_IMX_ATA_TIME_1`, `PATA_IMX_ATA_TIME_2W`, `PATA_IMX_ATA_TIME_2R`, `PATA_IMX_ATA_TIME_4`, `PATA_IMX_ATA_TIME_9`, and `PATA_IMX_ATA_TIME_AX`. `pata_imx_set_piomode()` updates timings and toggles `PATA_IMX_ATA_CTRL_IORDY_EN` according to `ata_pio_need_iordy()`.

`pata_imx_setup_port()` maps libata SFF taskfile addresses into the controller's register spacing, shifting standard ATA register indices by two. The port operations inherit from `ata_sff_port_ops`, use `ata_sff_data_xfer32`, report unknown cable type, and provide only PIO timing setup.

## Control Flow

`pata_imx_probe()` obtains the platform IRQ, allocates state, enables the clock via `devm_clk_get_enabled()`, allocates a one-port host, maps resource 0, assigns command/control addresses at `PATA_IMX_DRIVE_DATA` and `PATA_IMX_DRIVE_CONTROL`, sets up SFF addresses, deasserts FIFO and ATA resets, enables `ATA_INTRQ2`, and activates the host with `ata_sff_interrupt()`. Remove detaches the host and disables controller interrupts.

Suspend asks libata to suspend, disables interrupts, saves the ATA control register, and disables the clock. Resume re-enables the clock, restores the saved control register, reenables interrupts, and resumes the libata host.

## State, Dependencies, And Integration Points

Persistent runtime state is limited to the mapped register base, clock handle, and saved control word. Hardware state lives in timing/control/interrupt registers. Dependencies include the platform bus, device tree matching, common clock framework, libata SFF helpers, and raw MMIO accessors. Integration is a standard `platform_driver` with `SIMPLE_DEV_PM_OPS`.

## Risks And Test Signals

Risks include division by zero or invalid timing when the clock rate is unavailable, incorrect shifted taskfile mapping, and lost interrupt/control state across suspend. There is no DMA support despite a TODO, so performance expectations should remain PIO-only. Tests should cover probe with valid/missing IRQ, clock enable failure, all PIO modes 0-4, IORDY toggling, interrupt delivery, remove interrupt disable, suspend/resume with an attached disk, and DT binding compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_isapnp.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_isapnp.c

## Purpose

`pata_isapnp.c` is a small ISA Plug-and-Play PATA controller driver. It binds generic PnP IDE controller ID `PNP0600`, maps the advertised command and optional control ports, and registers a single PIO0 libata SFF port. It exists for old ISA PnP IDE interfaces that are not PCI devices and may not provide an alternate-status/control port.

## Important APIs, Types, And Functions

The driver defines two port-operation sets. `isapnp_port_ops` inherits from `ata_sff_port_ops` and uses a 40-wire cable report. `isapnp_noalt_port_ops` is the same except `lost_interrupt = ATA_OP_NULL`, because libata's lost-interrupt polling relies on altstatus, which is absent when the PnP device exposes only the command block.

`isapnp_init_one()` is the central probe function. It validates PnP port 0, optionally extracts IRQ 0 and uses `ata_sff_interrupt`, allocates a one-port host, maps the 8-byte command region, selects no-alt ops by default, and switches to normal ops when PnP port 1 can be mapped as a one-byte control/altstatus port. It calls `ata_sff_std_ports()` to fill the taskfile addresses and activates the host.

## Control Flow

The module uses `module_pnp_driver()`. On a matching PnP device, probe maps resources directly from `pnp_port_start()` values. If an IRQ is absent, the host is activated with IRQ 0 and a `NULL` handler, leaving operation dependent on libata's non-IRQ behavior for this class. Removal fetches the host from device driver data and detaches it.

## State, Dependencies, And Integration Points

The driver keeps no explicit private state. Resource lifetime is managed through devm I/O port mapping and libata host ownership. Dependencies are the ISA PnP core, libata SFF/PIO helpers, and the SCSI host template from `ATA_PIO_SHT()`. It integrates with libata through a single SFF port, fixed `ATA_PIO0`, `ATA_FLAG_SLAVE_POSS`, and 40-wire cable assumption.

## Risks And Test Signals

The important behavioral risk is no-altstatus operation: using normal lost-interrupt polling without a control port would be unsafe, hence the separate ops. Other risks are absent IRQs, malformed PnP resources, and assumptions that all supported devices are only PIO0. Tests should cover devices with and without control port resources, with and without IRQ resources, resource map failures, module unload detach, and basic PIO identify/read paths on a `PNP0600` interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_isapnp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_it8213.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_it8213.c

## Purpose

`pata_it8213.c` supports the ITE IT8213 PATA controller. The chip is described as Intel ICH/PIIX-like for timing layout, but with different cable detection and a simpler single-port topology. The driver provides BMDMA libata integration, PIO/MWDMA/UDMA timing programming in PCI config space, and a reset-time enabled-port check.

## Important APIs, Types, And Functions

`it8213_pre_reset()` checks PCI config bit `0x41[7]` before normal SFF reset and returns `-ENOENT` for disabled ports. `it8213_cable_detect()` reads config byte `0x42` and returns 40-wire when bit 1 is set, noting that early documentation had the polarity wrong. `it8213_set_piomode()` implements ICH-style PIO timing programming: it derives PPE/IE/TIME control bits, uses static ISP/RTC timing tables, writes master timing in config word `0x40`, and writes slave timing in byte `0x44`.

`it8213_set_dmamode()` handles UDMA and MWDMA separately. For UDMA it sets per-device UDMA enable in byte `0x48`, writes UDMA cycle timing in word `0x4A`, and selects 33/66/100 MHz clock bits in word `0x54`. For MWDMA it derives compatible PIO timing, can force PIO cycles to PIO0 via DMA-only control, clears UDMA enable, and writes the shared PIO/DMA timing registers.

## Control Flow

PCI probe enters `it8213_init_one()`, prints the driver version, defines one real port and one dummy port, and delegates setup to `ata_pci_bmdma_init_one()`. Runtime control is then libata-driven: reset filters disabled hardware, cable detection constrains UDMA, and mode callbacks update PCI timing registers.

## State, Dependencies, And Integration Points

The driver stores no private heap state. Hardware state is entirely in PCI config timing/control registers. Dependencies include PCI config access, libata BMDMA operations, SFF reset, and standard suspend/resume through `ata_pci_device_suspend()` and `ata_pci_device_resume()`. Integration is conservative: one IT8213 PCI ID, `ATA_MWDMA12_ONLY`, `ATA_UDMA6`, and `ATA_FLAG_SLAVE_POSS`.

## Risks And Test Signals

Risks center on register compatibility with ICH assumptions, master/slave timing interactions, and correct clock selection for UDMA modes above 2 and 4. The MWDMA path's forced PIO0 behavior for insufficient PIO capability is subtle. Tests should cover disabled-port reset behavior, 40/80 cable detection polarity, PIO modes for master and slave, MWDMA0-2, UDMA0-6, ATAPI PPE behavior, resume retaining timing through libata restore, and one-real-port/one-dummy-port enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_it8213.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_it821x.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_it821x.c

## Purpose

`pata_it821x.c` supports ITE IT8211/IT8212 and RDC D1010 PATA/IDE RAID-style controllers. It must handle two very different modes: pass-through IDE mode, where Linux programs timings directly, and smart RAID firmware mode, where the controller exposes firmware-managed volumes and supports only a restricted command set. It also supports forcing IT8212 out of RAID mode via the `noraid` module parameter.

## Important APIs, Types, And Functions

`struct it821x_dev` is per-port state allocated in `it821x_port_start()`. It records smart mode, revision 0x10 errata, selected 50/66 MHz clock, per-device clock desires, cached PIO/MWDMA/UDMA timing words, and the last selected device. `it821x_program()` and `it821x_program_udma()` write timing bytes according to the current clock, with revision 0x10 forcing paired-device UDMA programming. `it821x_clock_strategy()` chooses the channel clock from per-device priorities and reprograms cached timings after a switch.

Pass-through callbacks include `it821x_passthru_set_piomode()`, `it821x_passthru_set_dmamode()`, `it821x_passthru_bmdma_start()`, `it821x_passthru_bmdma_stop()`, `it821x_passthru_dev_select()`, and `it821x_passthru_qc_issue()`. Smart-mode callbacks include `it821x_smart_qc_issue()`, which rejects unsupported ATA commands, `it821x_smart_set_mode()`, which trusts firmware-configured DMA/PIO state, `it821x_dev_config()`, which limits `max_sectors` to 255 and sets quirks, and `it821x_read_id()`, which rewrites identify data to mask unsupported features and stabilize RAID volume serial numbers. Firmware command helpers `it821x_firmware_command()`, `it821x_probe_firmware()`, and `it821x_display_disk()` query and print controller RAID state.

## Control Flow

`it821x_init_one()` enables PCI, chooses RDC-specific port ops or ITE smart/pass-through ops based on vendor/device and config byte `0x50`, optionally calls `it821x_disable_raid()`, and delegates to `ata_pci_bmdma_init_one()`. `port_start()` then allocates per-port state, detects smart mode from config bit 0, probes firmware once for port 0, derives the current clock from config `0x50`, initializes clock wants to `ATA_ANY`, and enables revision 0x10 workarounds.

Runtime behavior diverges by mode. Pass-through mode actively switches timings and clocks around device selection and DMA start/stop. Smart mode filters commands and massages identity/capabilities to prevent the OS from issuing unsupported operations or large LBA48 requests that can crash firmware.

## State, Dependencies, And Integration Points

State spans module parameter `it8212_noraid`, PCI config registers, per-port `it821x_dev`, and firmware-reported RAID metadata. Dependencies include PCI, libata BMDMA/SFF, string/identify helpers, and devm allocation. Integration points are three `ata_port_operations` sets: smart, pass-through, and RDC, plus PM resume that reapplies `noraid` bypass if requested.

## Risks And Test Signals

This driver has high behavioral risk because firmware mode intentionally lies about device capabilities and command support. Key risks include firmware hangs from >255-sector requests, incorrect identify rewriting, revision 0x10 paired timing errata, ATAPI DMA filtering, and clock-switch regressions affecting a paired master/slave channel. Tests should cover smart RAID volume identify, unsupported command rejection, max-sector limiting, pass-through mixed PIO/MWDMA/UDMA pairs, `noraid=1`, RDC D1010 and Vortex86SX no-UDMA mode, revision 0x10, firmware command timeout/rejection, and suspend/resume with forced bypass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_it821x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ixp4xx_cf.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_ixp4xx_cf.c

## Purpose

`pata_ixp4xx_cf.c` drives CompactFlash cards wired to the Intel IXP4xx expansion bus in TrueIDE mode. It is a PIO-only platform driver that configures expansion-bus chip-select timing via a parent syscon/regmap and performs a special data-transfer sequence that temporarily switches the bus between 8-bit command timing and 16-bit data timing.

## Important APIs, Types, And Functions

`struct ixp4xx_pata` stores the libata host, parent regmap, command chip-select timing register offset, and mapped command/control windows. `ixp4xx_set_8bit_timing()` and `ixp4xx_set_16bit_timing()` program PIO0-4 timing constants and bus-width bits in the expansion timing register. `ixp4xx_set_piomode()` logs the selected PIO mode and leaves the command chip select in 8-bit timing for normal taskfile access.

`ixp4xx_mmio_data_xfer()` is the core custom transfer path. Under the ATA port lock it switches to 16-bit timing, delays, transfers the data payload with `readw()`/`writew()`, handles a trailing odd byte via a temporary 16-bit buffer, restores 8-bit timing, delays again, and returns the transferred byte count. `ixp4xx_setup_port()` maps SFF addresses and applies little-endian address swizzling by XORing register addresses when the CPU is not big endian.

## Control Flow

`ixp4xx_pata_probe()` allocates state, obtains a syscon regmap from the parent OF node, reads the first `reg` cell to derive the command chip-select index, allocates a one-port host from `ixp4xx_port_info`, maps command and control resources, obtains and configures an edge-rising IRQ, sets up the libata port, prints the version, and activates with `ata_sff_interrupt()`. Removal is delegated to `ata_platform_remove_one()`.

## State, Dependencies, And Integration Points

Persistent state is the regmap/timing register offset and mapped windows. Hardware state is the expansion-bus timing and width bits. Dependencies include OF platform probing, MFD syscon/regmap, IRQ type configuration, MMIO, libata SFF PIO helpers, and endianness configuration. The port info sets `ATA_FLAG_NO_ATAPI`, `ATA_PIO4`, 40-wire cable detection, and custom `sff_data_xfer`.

## Risks And Test Signals

Risks include incorrect chip-select derivation from device tree, timing/width restoration failures after data transfer, address swizzling errors on little-endian systems, and interrupt polarity assumptions. The function logs "PIO%d 8bit" even though data transfers switch to 16-bit, which is intentional but can confuse diagnostics. Tests should cover big- and little-endian address maps, odd-byte transfers, PIO modes 0-4 timing writes, IRQ delivery, no-ATAPI filtering, syscon lookup failure, and command/data/control resource mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ixp4xx_cf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_jmicron.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_jmicron.c

## Purpose

`pata_jmicron.c` handles JMicron IDE-class controllers in non-AHCI mode, primarily to drive PATA ports while SATA ports are normally handled by AHCI. The controller can map physical PATA and SATA ports into logical IDE primary/secondary channels in several firmware-defined ways, so this driver mostly performs pre-reset port mapping and cable detection before delegating timing and BMDMA behavior to generic libata PCI IDE support.

## Important APIs, Types, And Functions

The `port_type` enum identifies `PORT_PATA0`, `PORT_PATA1`, and `PORT_SATA`. `jmicron_pre_reset()` is the only chip-specific callback. It reads PCI config dword `0x40` to check logical port enablement, determine whether the secondary channel maps to PATA0, and detect logical channel swap. It also reads config dword `0x80` for JMB365/JMB366 secondary PATA mapping. After resolving the physical port, it validates the relevant enable bit and sets `ap->cbl` to `ATA_CBL_PATA40`, `ATA_CBL_PATA80`, or `ATA_CBL_SATA`.

The port operations inherit from `ata_bmdma_port_ops` and override only `.reset.prereset`. The PCI ID table matches JMicron IDE-class storage functions broadly using `PCI_CLASS_STORAGE_IDE`.

## Control Flow

`jmicron_init_one()` defines one BMDMA-capable port-info record with PIO4, MWDMA2, UDMA5, slave possible, and `jmicron_ops`, then delegates to `ata_pci_bmdma_init_one()`. During libata reset/probe for each port, `jmicron_pre_reset()` rejects disabled logical or physical ports with `-ENOENT`; otherwise it sets cable state and calls `ata_sff_prereset()`.

## State, Dependencies, And Integration Points

The driver keeps no private state. All decisions are made from PCI config registers at reset time. Dependencies are PCI class matching, libata BMDMA/SFF helpers, and standard PCI PM helpers. It integrates with AHCI indirectly: this driver binds only IDE-class functions, while typical SATA AHCI functions are handled elsewhere.

## Risks And Test Signals

Risks are concentrated in bit interpretation for logical/physical port mapping. A wrong mapping can probe SATA as PATA, hide an enabled PATA port, or apply the wrong cable limit. Tests should cover JMB361/363 one-PATA-port layouts, JMB365/366 PATA1 mapping via config `0x80[24]`, logical channel swap via `0x40[22]`, disabled-port handling, SATA cable reporting, PCI class matching, and suspend/resume through generic libata PCI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_jmicron.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_legacy.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_legacy.c

## Purpose

`pata_legacy.c` probes and registers legacy ISA-side IDE ports on PC-class systems. It covers traditional primary/secondary addresses and optional tertiary ranges, while avoiding ports already claimed or implied by PCI devices. The driver is intentionally simple: BIOS-configured ports are treated as PIO-only, and optional "snooping" controllers can be exposed with normal libata PIO mode handling.

## Important APIs, Types, And Functions

Module parameters control scan scope and capabilities: `all`, `probe_all`, `probe_mask`, `autospeed`, `pio_mask`, and `iordy_mask`. `struct legacy_probe` records candidate port/IRQ/type/private data. `struct legacy_data` stores per-slot controller state and the platform device used to anchor resources. `struct legacy_controller` describes a controller family, port ops, PIO mask, ATA flags, pflags, and optional setup callback.

`legacy_probe_add()` builds an ordered probe list using stable legacy port slots. `legacy_set_mode()` forces discovered devices to PIO0 and marks them PIO, reflecting BIOS-owned timing. `legacy_init_one()` registers a platform device for a candidate, requests command/control I/O regions, maps them, allocates a libata host, fills SFF addresses, activates with `ata_sff_interrupt()`, synchronizes async probing, and drops the host if no device is present. `legacy_check_special_cases()` avoids probing legacy ranges owned by Cyrix and MPIIX bridge-style ATA implementations.

## Control Flow

At module init, `legacy_init()` scans all PCI devices for resources overlapping `0x1f0` or `0x170`, applies special-case checks, adds primary/secondary probes if unclaimed or `all=1`, optionally adds tertiary legacy addresses, resolves unknown probe types through `probe_chip_type()`, and attempts to initialize each candidate. If none succeed it returns `-ENODEV`. Module exit detaches any registered hosts and unregisters their platform devices.

## State, Dependencies, And Integration Points

State is global arrays: `probe_list`, `legacy_data`, and `legacy_host`, each sized by `NR_HOST`. The driver depends on PCI enumeration for avoidance, platform devices for resource ownership, devm I/O port mapping, libata SFF PIO helpers, and async probing synchronization. Integration with libata uses one SFF port per legacy address, 40-wire cable assumption, and `ATA_FLAG_SLAVE_POSS`; BIOS mode also sets `ATA_FLAG_NO_IORDY` unless overridden.

## Risks And Test Signals

Risks include probing ports that belong to another controller, missing real non-PCI ports when PCI is present, module parameter interactions, and global state cleanup. Tests should cover systems with PCI IDE native/legacy overlap, `all=1`, `probe_all=1`, each `probe_mask` bit, absent-device cleanup after activation, autospeed/snooping mode, IORDY mask behavior, special-case Cyrix/MPIIX exclusion, and unload after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_macio.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_macio.c

## Purpose

`pata_macio.c` is the libata driver for Apple PowerMac MacIO-family PATA controllers, including OHare, Heathrow/Paddington, KeyLargo ATA-3/ATA-4, UniNorth/Kauai ATA-6, K2, and Shasta. It supports both macio bus devices and related Apple PCI devices. The driver handles device-tree-based variant discovery, timing-table programming, DBDMA command construction, PowerMac feature-control reset/enable, media-bay hotplug, suspend/resume, cable detection, and controller-specific DMA alignment quirks.

## Important APIs, Types, And Functions

`struct pata_macio_priv` is the central private state: controller kind, Apple bus id, media-bay flag, OF node, macio/PCI device pointers, IRQ, cached timing registers for two devices, mapped taskfile/FCR registers, DBDMA command table, libata host, and selected timing table. `struct pata_macio_timing` maps transfer modes to one or two hardware timing-register values; multiple static tables cover the controller families.

Timing selection flows through `pata_macio_find_timing()`, `pata_macio_set_timings()`, `pata_macio_apply_timings()`, `pata_macio_dev_select()`, and `pata_macio_default_timings()`. Cable detection uses OF `cable-type`, model checks for PowerBook short 40-wire behavior, and K2/Shasta overrides. DBDMA support is implemented in `pata_macio_qc_prep()`, `pata_macio_bmdma_setup()`, `pata_macio_bmdma_start()`, `pata_macio_bmdma_stop()`, and `pata_macio_bmdma_status()`. `pata_macio_sdev_configure()` adjusts queue DMA alignment/padding for OHare and K2/Shasta ATAPI issues.

## Control Flow

Initialization is gated by `machine_is(powermac)`. The module registers a PCI driver first, then a macio driver. Both attach paths allocate `pata_macio_priv`, obtain OF nodes and resources, then call `pata_macio_common_init()`. Common init identifies invariants from OF compatibility, sets default timings, derives libata mode masks from the selected table, allocates a one-port host, maps taskfile/DMA/FCR resources, installs port private data, resets/enables hardware through `pata_macio_reset_hw()`, applies timings, sets PCI bus master if applicable, and activates with `ata_bmdma_interrupt()`.

Suspend calls libata suspend, restores default timings, disables IRQ, disables FCR or PCI DMA, and powers down the feature-controlled IDE cell. Resume resets/re-enables hardware, reapplies timings, reenables IRQ, and resumes libata. Media-bay events freeze or abort the port and mark devices detached.

## State, Dependencies, And Integration Points

State is substantial and persists across callbacks in `pata_macio_priv`, cached timing registers, DBDMA descriptors, OF node references, and platform feature-control hardware. Dependencies include macio, PCI, Open Firmware, PowerMac `ppc_md.feature_call()`, DBDMA, media bay, IRQ domains, libata BMDMA/SFF, and SCSI queue-limit configuration. Integration uses custom SCSI host template limits for DBDMA command count and segment size, custom PM paths, and two bus registration mechanisms.

## Risks And Test Signals

Risks are broad: incorrect timing tables, DBDMA segment splitting near 64K boundaries, DMA flush timeouts, device-tree cable misinformation, feature-control reset timing, media-bay races, and platform-specific ATAPI alignment. Tests should cover each controller kind, PIO/MWDMA/UDMA mode masks, master/slave timing switching, DBDMA boundary splitting, DMA error/flush paths, OHare and K2/Shasta queue limits, PowerBook short cable handling, K2/Shasta cable override, macio and PCI attach/detach, media-bay plug/unplug, and suspend/resume with PCI state restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_macio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_marvell.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_marvell.c

## Purpose

`pata_marvell.c` is a legacy-mode libata driver for Marvell ATA controllers with PATA functionality. It intentionally uses the simple PCI BMDMA path rather than exposing every device feature. For some devices, particularly 6145, it checks whether the PATA port is actually active and can defer to AHCI when the PATA function is disabled.

## Important APIs, Types, And Functions

`marvell_pata_active()` determines whether a PATA port may be active. For device `0x6145`, it maps BAR5, reads register `0x0c`, and checks bit `0x10`; for other devices it assumes active because no specific detection is known. `marvell_pre_reset()` uses this helper to return `-ENOENT` for inactive 6145 port 0 before normal SFF reset. `marvell_cable_detect()` reports PATA cable type for port 0 from BMDMA status byte bit 0, unknown if BMDMA registers are unavailable, and reports `ATA_CBL_SATA` for the legacy SATA port 1.

Port operations inherit from `ata_bmdma_port_ops` and override cable detection plus pre-reset only. `marvell_init_one()` selects two port-info entries: PATA UDMA5 and a "legacy SATA" UDMA6 entry, except device `0x6101` uses a dummy second port.

## Control Flow

PCI probe optionally defers to AHCI when `CONFIG_SATA_AHCI` is enabled and `marvell_pata_active()` returns false. Otherwise it calls `ata_pci_bmdma_init_one()`. At reset time inactive 6145 PATA ports are skipped, while active ports run generic SFF reset. Cable detection is queried by libata mode negotiation.

## State, Dependencies, And Integration Points

There is no private state. The driver depends on PCI BAR mapping, libata BMDMA helpers, and optional compile-time AHCI cooperation. It integrates with PCI IDs for `0x11AB:6101/6121/6123/6145` and `0x1B4B:91A0/91A4`, and with generic PCI PM helpers.

## Risks And Test Signals

Risks include assuming unknown devices have active PATA, BAR5 mapping failures returning negative values through a boolean-style helper, and BMDMA bit interpretation for cable detection. Tests should cover 6145 active/inactive BAR5 state, AHCI-enabled deferral, 6101 dummy second port, port 1 SATA reporting, missing BMDMA address fallback, suspend/resume, and normal UDMA mode negotiation on PATA40 versus PATA80 cables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_marvell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_mpc52xx.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_mpc52xx.c

## Purpose

`pata_mpc52xx.c` is the OF platform libata driver for the Freescale MPC52xx on-chip IDE/ATA controller. It supports PIO plus optional MWDMA/UDMA via BestComm DMA tasks, with transfer mode availability controlled by device-tree properties because board routing and MPC5200B silicon errata make DMA unsafe on some systems.

## Important APIs, Types, And Functions

`struct mpc52xx_ata` describes the memory-mapped controller register block, including timing registers, FIFO registers, taskfile registers, and DMA mode. `struct mpc52xx_ata_timings` caches computed timing register values per device. `struct mpc52xx_ata_priv` stores the IPB clock period, mapped register base and physical address, IRQ, per-device timings, selected device, BestComm task, timing spec tables, last DMA direction, and DMA status flags.

Timing is computed by `mpc52xx_ata_compute_pio_timings()`, `mpc52xx_ata_compute_mdma_timings()`, and `mpc52xx_ata_compute_udma_timings()`, then applied with `mpc52xx_ata_apply_timings()`. `mpc52xx_ata_hw_init()` resets the host/FIFO, enables interrupts/IORDY, programs share counter timing, and initializes PIO0. DMA flow is custom: `mpc52xx_ata_build_dmatable()` converts libata scatterlists into BestComm ATA buffer descriptors, `mpc52xx_bmdma_setup()` programs FIFO and DMA mode, `mpc52xx_bmdma_start()` enables the BestComm task, `mpc52xx_bmdma_stop()` disables/resets it, `mpc52xx_bmdma_status()` reports FIFO/DMA state, and `mpc52xx_ata_task_irq()` drains completed buffers and sets `ATA_DMA_INTR`.

## Control Flow

`mpc52xx_ata_probe()` reads the IPB bus frequency, maps the OF register resource, reads `mwdma-mode` and `udma-mode` properties to build masks, maps the ATA IRQ, allocates private state, selects 66 MHz or 132 MHz timing spec tables, allocates a BestComm ATA task, requests the task IRQ, initializes hardware, and registers the libata host through `mpc52xx_ata_init_one()`. Host initialization maps libata taskfile pointers directly into the controller struct and activates with `ata_bmdma_interrupt()`.

## State, Dependencies, And Integration Points

State persists in `mpc52xx_ata_priv`, BestComm descriptors/tasks, controller FIFO/DMA registers, and cached per-device timing values. Dependencies include OF address/IRQ helpers, MPC5xxx bus-frequency helpers, BestComm DMA APIs, big-endian MMIO accessors, libata BMDMA/SFF callbacks, and platform PM. Integration includes direct taskfile register mapping, custom DMA status semantics via `waiting_for_dma`, and DT compatibility strings `fsl,mpc5200-ata` and `mpc5200-ata`.

## Risks And Test Signals

Risks include DMA enabled on boards that cannot safely route signals, UDMA timing limited to modes 0-2 despite tables, FIFO error handling, BestComm descriptor overflow, and IPB clock miscalculation. Tests should cover DT with no DMA properties, MWDMA/UDMA masks from properties, BestComm init/IRQ failure unwind, large scatterlists over `MAX_DMA_BUFFERS`, FIFO error injection, read/write direction changes, device-select timing reapply, suspend/resume hardware reinitialization, and PIO fallback behavior when DMA table building fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_mpc52xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_mpiix.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_mpiix.c

## Purpose

`pata_mpiix.c` supports the Intel 82371MX MPIIX bridge-style IDE function. MPIIX is unusual because timing is configured through PCI config space, but the IDE command/control ports are ISA legacy addresses and the PCI device is not a normal IDE-class function. The driver keeps this special probing and non-disable behavior local rather than pushing quirks into generic libata.

## Important APIs, Types, And Functions

The `IDETIM` config register at `0x6c` supplies enable, primary/secondary selection, and timing bits. `mpiix_pre_reset()` checks `IDETIM` enable state via config byte `0x6d[7]` before generic reset. `mpiix_set_piomode()` computes PIO timing bits using static ISP/RTC values, sets PPE for ATA disks, IORDY when required, and FTIM for PIO modes above 1, then writes the shared `IDETIM` register. It stores the currently programmed `ata_device` in `ap->private_data`.

`mpiix_qc_issue()` reloads timings before command issue when the queued command targets a different device than the one currently programmed, then calls `ata_sff_qc_issue()`. This is necessary because the hardware can effectively time only one device correctly at a time.

## Control Flow

`mpiix_init_one()` allocates a one-port host without using normal PCI IDE BAR plumbing. It reads `IDETIM`, rejects disabled IDE, chooses primary `0x1f0/0x3f6/14` or secondary `0x170/0x376/15` based on the `SECONDARY` bit, maps those I/O ports, fills SFF addresses, and activates with a shared IRQ. The PCI driver still uses `ata_pci_remove_one()` and generic PM hooks, but probe intentionally avoids `pcim_enable_device()`/disable style assumptions that could disrupt the multifunction bridge.

## State, Dependencies, And Integration Points

Runtime state is only `ap->private_data` for the currently loaded timing and the `IDETIM` PCI config word. Dependencies include PCI config access, legacy I/O port mapping, libata SFF PIO helpers, and the Intel PCI ID. It integrates with libata as a one-port PIO-only SFF host using 32-bit data transfer and 40-wire cable reporting.

## Risks And Test Signals

Risks include shared timing switching between master and slave, incorrect primary/secondary legacy address selection, accidentally disabling or power-managing a multifunction bridge incorrectly, and ThinkPad/PCMCIA configurations where the secondary port is decoded elsewhere. Tests should cover enabled/disabled `IDETIM`, both primary and secondary mappings, master/slave PIO transitions, IORDY/PPE bits, command issue timing reloads, shared IRQ delivery, and suspend/resume on real MPIIX-era hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_mpiix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_netcell.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_netcell.c

## Purpose

`pata_netcell.c` is a compact libata BMDMA driver for Netcell Revolution PATA RAID controllers. The firmware handles most timing and RAID behavior, so the driver's main chip-specific task is to repair identify data that the firmware reports incompletely.

## Important APIs, Types, And Functions

`netcell_read_id()` wraps `ata_do_dev_read_id()`. On success, it sets bit `0x4000` in `id[ATA_ID_CSF_DEFAULT]` because the firmware forgets to mark command-set words 85-87 valid. This prevents upper layers and tools from seeing a malformed identify block. The port operations inherit from `ata_bmdma_port_ops`, force 80-wire cable reporting, and override `.read_id`.

`netcell_init_one()` enables the PCI device, clears simplex status with `ata_pci_bmdma_clear_simplex()`, and delegates to `ata_pci_bmdma_init_one()` with PIO4/MWDMA2/UDMA5 masks and `ATA_FLAG_SLAVE_POSS`.

## Control Flow

The PCI module binds `PCI_DEVICE_ID_REVOLUTION`. Probe prints version, enables PCI, performs the simplex clear, and registers a generic BMDMA libata host. During identify, libata invokes `netcell_read_id()` so the corrected validity bit is visible before device configuration continues. Remove and PM are generic libata PCI paths.

## State, Dependencies, And Integration Points

There is no private state. Persistent behavior is firmware-managed; the only driver-side mutation is the in-memory identify buffer correction. Dependencies are PCI, libata BMDMA helpers, ATA identify definitions, and generic PCI PM. Integration assumes the firmware owns real timing policy despite advertised masks.

## Risks And Test Signals

Risks are low but specific: identify-data repair must not mask real read errors, and forced 80-wire reporting assumes the RAID controller's firmware-facing link rather than physical cabling. Tests should cover successful and failed identify reads, validation that words 85-87 become usable, probe after simplex clearing, basic DMA I/O through firmware volumes, suspend/resume, and behavior with management tools reading identify data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_netcell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ninja32.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_ninja32.c

## Purpose

`pata_ninja32.c` supports Ninja32/CardBus-style PATA controllers with a nonstandard BAR0 register layout. The controller has shared timing registers for PIO and DMA and requires manual programming of chipset control bytes. The driver exposes it as a one-port BMDMA libata host with 32-bit PIO transfers and timing reprogramming on device selection.

## Important APIs, Types, And Functions

`ninja32_set_piomode()` writes one of five static timing bytes to BAR0 offset `0x1f` and stores the programmed `ata_device` in `ap->private_data`. `ninja32_dev_select()` compares the requested device with that cached pointer, resets timing to a safe PIO0-like value, performs standard device select, and reapplies the target device's PIO timing. `ninja32_program()` writes controller initialization constants to BAR0 offsets for IRQ enable, chipset control, wait bits, and bus-master control.

The port operations inherit from `ata_bmdma_port_ops`, override `sff_dev_select`, use 40-wire cable detection, provide PIO timing, and set `ata_sff_data_xfer32`. The driver sets `ATA_PFLAG_PIO32 | ATA_PFLAG_PIO32CHANGE` because data transfer width can require 32-bit PIO behavior changes.

## Control Flow

`ninja32_init_one()` allocates a one-port host, enables the PCI device, maps BAR0, sets the ATA DMA mask, enables PCI bus mastering, fills taskfile/control/BMDMA addresses at fixed BAR0 offsets, initializes the hardware with `ninja32_program()`, and activates with shared `ata_bmdma_interrupt()`. Resume re-enables the PCI device, reruns `ninja32_program()`, and resumes the host.

## State, Dependencies, And Integration Points

State is limited to the BAR0 register block and `ap->private_data` timing cache. Dependencies are PCI managed I/O mapping, DMA mask setup, libata BMDMA/SFF helpers, and a table of vendor/device IDs. Integration is custom because the controller is not a generic SFF BAR layout despite using BMDMA-like operations.

## Risks And Test Signals

Risks include undocumented magic initialization bytes, shared timing across devices, lack of explicit remove-time interrupt disable, and fixed 40-wire assumption. Tests should cover all listed CardBus IDs, BAR0 mapping failure, PIO mode changes for master/slave, device selection timing reload, 32-bit PIO data transfers, DMA interrupt behavior, suspend/resume reprogramming, and hot-unplug/remove with interrupts enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ninja32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ns87410.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_ns87410.c

## Purpose

`pata_ns87410.c` supports the National Semiconductor NS87410 PATA controller. It is a PIO-only PCI SFF driver with per-channel rather than per-device timing registers, so it reloads timings on command issue when switching between master and slave devices.

## Important APIs, Types, And Functions

`ns87410_pre_reset()` checks channel enable bits in PCI config bytes `0x43` and `0x47` before normal SFF reset. `ns87410_set_piomode()` computes ATA PIO timing with `ata_timing_compute()` using a 30.303 ns clock, clamps setup/active/recover values, maps active and recovery cycles through static encoding tables, writes the timing-control byte, and toggles IORDY enable in the feature register. It stores the currently programmed device in `ap->private_data`.

`ns87410_qc_issue()` reloads PIO timing if the queued command targets a different device than the cached one, then delegates to `ata_sff_qc_issue()`. Port ops inherit from `ata_sff_port_ops`, use 40-wire cable detection, implement PIO setup, and hook pre-reset.

## Control Flow

PCI probe defines PIO3-capable `ata_port_info` and calls `ata_pci_sff_init_one()`. Libata handles standard PCI SFF resource setup. During reset disabled ports are skipped. During mode negotiation and command issue, timing is computed and refreshed for the active device as needed.

## State, Dependencies, And Integration Points

State is small: PCI timing/config bytes and `ap->private_data` for current timing ownership. Dependencies include PCI config access, libata SFF PIO helpers, ATA timing computation, and generic PCI PM callbacks. Integration is normal PCI SFF rather than BMDMA.

## Risks And Test Signals

Risks include off-by-one timing encoding, shared timing between master/slave devices, and IORDY enable polarity. Because the advertised mask is only `ATA_PIO3`, tests should verify that PIO4 is not negotiated. Additional signals include disabled channel handling, timing reload on command issue, master/slave mixed PIO modes, suspend/resume through generic helpers, and error handling when `ata_timing_compute()` rejects a mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ns87410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ns87415.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_ns87415.c

## Purpose

`pata_ns87415.c` supports National Semiconductor NS87415 controllers and, when `CONFIG_SUPERIO` is enabled, the related PARISC SuperIO 87560 cell. It is a BMDMA-capable PATA driver with chip errata requiring timing reloads on PIO/DMA transitions, nonstandard DMA setup/status clearing, and optional PARISC read workarounds.

## Important APIs, Types, And Functions

`ns87415_set_mode()` computes PCI-clock-based PIO timing with `ata_timing_compute()`, writes read/write timing nibbles to per-device registers at `0x44 + 2 * unit`, and updates config byte `0x42` to select IORDY versus DMA behavior after waiting for write buffers in status byte `0x43` to drain. `ns87415_set_piomode()` applies PIO timing. `ns87415_bmdma_start()` switches to DMA timing before `ata_bmdma_start()`, and `ns87415_bmdma_stop()` switches back to PIO after generic stop.

`ns87415_bmdma_setup()` manually writes the PRD address and DMA command register because of an erratum that requires interrupt/error bits to be written to the command byte rather than the normal status location. `ns87415_irq_clear()` likewise clears interrupt/error through the command register. `ns87415_check_atapi_dma()` disables ATAPI DMA. `ns87415_fixup()` initializes 512-byte sector and PIO0 8-bit clocking registers.

With `CONFIG_SUPERIO`, `ns87560_read_buggy()` retries reads that return zero, and the SuperIO ops override status, taskfile read, and BMDMA status paths to use that workaround.

## Control Flow

`ns87415_init_one()` enables PCI, applies `ns87415_fixup()`, selects SuperIO-specific port ops when the PCI slot indicates 87560, and calls `ata_pci_bmdma_init_one()`. Runtime DMA setup/start/stop paths interleave timing switches with generic BMDMA flow. Resume re-enables the PCI device, reapplies fixups, and resumes the libata host.

## State, Dependencies, And Integration Points

The driver stores no explicit private data. State is in PCI config timing/control bytes and the BMDMA register block. Dependencies include PCI config and I/O access, libata BMDMA/SFF helpers, ATA timing computation, optional PARISC `superio.h`, and generic PCI PM. Integration is via one port-op set for NS87415 and a derived one for NS87560.

## Risks And Test Signals

Risks include DMA errata handling, timing flips around every DMA transfer, disabled ATAPI DMA reducing performance, and SuperIO read retries hiding real bus faults. Tests should cover PIO and MWDMA timing programming, DMA setup command/status bits, interrupt clear behavior, ATAPI DMA rejection, write-buffer wait loop, resume fixups, SuperIO status/taskfile reads under injected zero reads, and operation with both legacy IRQ and native shared INTA firmware setups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ns87415.c -->
