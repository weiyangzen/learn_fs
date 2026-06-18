# Research: subset-b-000728

Grouped research for MIPS machine headers under the ceph-client source tree, covering ATH79, Alchemy Au1x00, BCM47xx, and BCM63xx platform contracts. Each section preserves the source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ar71xx_regs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ar71xx_regs.h

**Purpose:** This is the central ATH79 register map header for Atheros/QCA AR71xx, AR724x, AR913x, AR933x, AR934x, QCA953x, QCA955x, QCA956x, and related SoCs. It gives board code and platform drivers stable symbolic names for physical MMIO bases, block sizes, register offsets, bit fields, reset lines, bootstrap pins, interrupt status masks, revision IDs, GPIO mux selectors, SPI signals, MII/GMAC mode fields, PCI/PCIe windows, USB, DDR flush registers, PLL controls, and hidden QCA956x MAC/DAM configuration registers.

**Important APIs/types/functions:** The public surface is almost entirely `#define` constants. Major groups include `AR71XX_APB_BASE`, per-block base/size pairs, PCI window offsets, DDR flush offsets, PLL register fields, reset-module bits, bootstrap bits, `REV_ID_*` masks, SPI register bits, GPIO register and mux values, MII control fields, and GMAC/SGMII configuration masks. It includes `<linux/types.h>`, `<linux/io.h>`, and `<linux/bitops.h>` for typed MMIO consumers and `BIT()` masks, but declares no functions.

**Control flow:** The header has no runtime flow by itself. Its constants drive control flow in platform init, clock, reset, PCI, GPIO, Ethernet, SPI, USB, and interrupt code that selects SoC-specific offsets after CPU revision detection, reads/writes MMIO registers, and composes bit masks for hardware sequencing. Macros such as `AR934X_PCIE_WMAC_INT_*_ALL` and `QCA955X_EXT_INT_*_ALL` encode grouped interrupt handling policy.

**State and persistence behavior:** It owns no C storage. Consumers mutate persistent hardware state by writing reset, PLL, GPIO mux, PCI window, SPI, DDR flush, and GMAC registers named here. Many values are boot-time strap or revision IDs and must be treated as hardware ABI, not ordinary configurable state.

**Dependencies and integration points:** Integrated by ATH79 arch setup, clock/reset code, PCI/PCIe host setup, GPIO/pinctrl users, Ethernet MAC/SGMII setup, SPI flash access, USB platform devices, and interrupt controllers. It depends on `BIT()` and raw MMIO helpers in consumers.

**Risks:** The file is dense and SoC variants reuse similar register names with different offsets or bit meanings. A wrong base, size, reset bit, or mux value can hang boot, break flash access, disable Ethernet/USB/PCIe, or corrupt DDR/flush handling. Unsupported hardware placeholders are not explicit, so incorrect variant selection is a key risk. Some hidden QCA956x addresses are outside the normal APB base and need extra care.

**Test signals:** Build ATH79 defconfigs with PCI, Ethernet, SPI, GPIO, and USB enabled. Boot-test each supported SoC family, checking revision detection, DDR write-buffer flushes, reset sequencing, GPIO muxing, SPI flash probe, PCIe enumeration, Ethernet link modes, USB enumeration, and interrupt delivery. Static review should compare every offset and bit with datasheets and downstream BSP users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ar71xx_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ar933x_uart.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ar933x_uart.h

**Purpose:** Defines the AR933x-specific UART register layout and bit fields. It supports the compact 20-byte UART block used by AR933x platform serial code rather than the more common 8250-compatible layout.

**Important APIs/types/functions:** Exports register offsets `AR933X_UART_DATA_REG`, `CS_REG`, `CLOCK_REG`, `INT_REG`, and `INT_EN_REG`; FIFO/register sizes; data CSR bits; control/status fields for parity, DTE/DCE interface mode, DMA, ready override, break, host interrupt, TX/RX busy; clock step/scale masks; and interrupt bits for RX valid, TX ready, framing/overflow/parity/break, RX full, and TX empty. It relies on `BIT()` being visible through including code and declares no functions.

**Control flow:** Serial drivers use the offsets to poll RX/TX readiness, program parity/interface/flow-control mode, compute fractional clock divisor values, acknowledge interrupt sources, and enable selected interrupts. The header itself is declarative.

**State and persistence behavior:** No software state is stored. Consumers mutate UART FIFO, control, clock, interrupt-status, and interrupt-enable registers. UART configuration persists until reset or reprogramming by serial/console paths.

**Dependencies and integration points:** Integrated by AR933x console/serial code and platform device setup, using the base address from `ar71xx_regs.h`. It sits on the low-level printk/early-console path where missing includes or wrong bit values are visible very early in boot.

**Risks:** `AR933X_UART_CLOCK_STEP_M` is defined twice with the same value; this is harmless to the preprocessor but is a maintenance smell. Missing an include for `BIT()` in a direct consumer would break builds. Wrong clock scale/step programming can produce unusable baud rates, and wrong interrupt masks can lose console input or flood interrupts.

**Test signals:** Compile serial console users with warnings enabled, boot with early console and normal console, verify baud rate accuracy, RX/TX interrupt handling, break/framing/overflow reporting, FIFO limits, and suspend/resume or reset reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ar933x_uart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ath79.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ath79.h

**Purpose:** Provides common ATH79 SoC identity, revision, and reset/PLL access helpers for board and platform code.

**Important APIs/types/functions:** Defines `enum ath79_soc_type`, extern globals `ath79_soc` and `ath79_soc_rev`, SoC predicate helpers such as `soc_is_ar71xx()`, `soc_is_ar724x()`, `soc_is_ar933x()`, `soc_is_ar934x()`, `soc_is_qca955x()`, and `soc_is_qca956x()`, declarations for `ath79_ddr_wb_flush()`, `ath79_ddr_set_pci_windows()`, `ath79_device_reset_set()`, and `ath79_device_reset_clear()`, and extern MMIO bases `ath79_pll_base`/`ath79_reset_base`. Inline helpers `ath79_pll_wr/rr()` and `ath79_reset_wr/rr()` perform raw MMIO access.

**Control flow:** Boot CPU detection initializes the global SoC type and revision; all later SoC-specific paths branch through the inline predicates. Reset and PLL helpers are used during device bring-up and clock programming. DDR flush helpers are called around DMA or device write-buffer synchronization.

**State and persistence behavior:** Holds global software identity state through `ath79_soc` and `ath79_soc_rev`, and uses global mapped MMIO base pointers. Inline writes mutate PLL and reset registers, which can change clocks or hold/release device blocks.

**Dependencies and integration points:** Depends on `<linux/types.h>`, `<linux/io.h>`, CPU detection code, MMIO mapping setup, `ar71xx_regs.h` register definitions, clock/reset users, PCI setup, and board files.

**Risks:** Incorrect SoC identity causes broad misconfiguration because many drivers branch through these predicates. The QCA9561/QCA9563 helpers currently both map to the single `ATH79_SOC_QCA956X` value, so code cannot distinguish those packages unless additional revision/strap logic is used. Raw writes have no locking in the inline layer.

**Test signals:** Validate CPU ID/revision logs across every SoC, unit-review predicate coverage for new enum entries, boot-test reset/PLL users, and run Ethernet/PCI/USB/SPI smoke tests that exercise DDR flush and reset helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ath79.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/cpu-feature-overrides.h

**Purpose:** Supplies compile-time CPU feature constants for ATH79 MIPS32 systems so generic MIPS code can optimize away unsupported paths.

**Important APIs/types/functions:** Defines `cpu_has_*` and cache-line macros: TLB, 4K exception/cache, counter, watch, divec, prefetch, EJTAG, LL/SC, MIPS16, MIPS32r1/r2, 32-bit-only GP registers, no FPU/32FPR/64-bit/MIPS MT/userlocal, 32-byte I/D cache lines, D-cache aliases present, and physically indexed D-cache absent. There are no functions or storage declarations.

**Control flow:** The generic MIPS feature machinery includes this header and compiles conditional code based on constant expressions. Runtime flow is affected indirectly because FPU emulation, cache maintenance, exception-vector setup, and LL/SC behavior are selected from these constants.

**State and persistence behavior:** No mutable state. It constrains kernel feature state at compile time and must match real CPU capabilities for every configured ATH79 target.

**Dependencies and integration points:** Integrated by MIPS CPU feature detection and low-level arch code. It must stay consistent with ATH79 CPU revisions and any Kconfig combinations for this machine.

**Risks:** A wrong feature bit can produce invalid instructions, broken cache flushing, missing exception support, or unnecessary slow paths. The file assumes a uniform feature set across ATH79; adding a variant with different MIPS revision/cache/FPU behavior requires revisiting these constants.

**Test signals:** Build ATH79 kernels with CPU feature debug enabled, boot across SoC variants, run cache aliasing stress, LL/SC atomic tests, exception/watchpoint smoke tests, and verify no FPU or 64-bit paths are emitted unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/irq.h

**Purpose:** Defines the ATH79 Linux IRQ number layout layered on top of MIPS CPU IRQs.

**Important APIs/types/functions:** Exports `MIPS_CPU_IRQ_BASE`, `NR_IRQS`, and mapping macros `ATH79_CPU_IRQ(x)`, `ATH79_MISC_IRQ(x)`, `ATH79_PCI_IRQ(x)`, `ATH79_IP2_IRQ(x)`, and `ATH79_IP3_IRQ(x)`. It reserves 32 misc IRQs after CPU IRQs, 6 PCI IRQs, 2 IP2 IRQs, and 3 IP3 IRQs, then includes `<asm/mach-generic/irq.h>`.

**Control flow:** Interrupt controller setup and drivers use these macros to allocate fixed Linux IRQ numbers. Runtime interrupt flow is in controller code; this header fixes the numbering boundaries that demultiplexers and platform devices rely on.

**State and persistence behavior:** No software state. It creates a compile-time ABI between board files, irqchip code, and drivers through numeric IRQ assignments.

**Dependencies and integration points:** Depends on the generic MIPS IRQ header and is consumed by ATH79 interrupt, PCI, GPIO, timer, and device registration code.

**Risks:** `NR_IRQS` must cover all ranges. Changing a base or count breaks platform-device resources and interrupt demux assumptions. Fixed numbering can conflict with newer dynamic irqdomain patterns if mixed carelessly.

**Test signals:** Build with all ATH79 interrupt users, boot with PCI/WMAC/GPIO/misc interrupts active, inspect `/proc/interrupts`, trigger each interrupt source class, and check for out-of-range IRQ warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/kernel-entry-init.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/kernel-entry-init.h

**Purpose:** Provides ATH79 assembly macros used at kernel entry before normal C initialization.

**Important APIs/types/functions:** Defines `kernel_entry_setup` and an empty `smp_slave_setup` assembly macro. `kernel_entry_setup` reads CP0 Config, clears `CONF_CM_CMASK`, and sets `CONF_CM_CACHABLE_NONCOHERENT` to force KSEG0 from bootloader-selected write-through/no-write-allocate mode to write-back/write-allocate cacheability.

**Control flow:** This runs at the earliest MIPS kernel entry path. It executes before platform devices or normal memory management, ensuring subsequent KSEG0 accesses use the desired cache algorithm. `smp_slave_setup` is intentionally empty for this platform.

**State and persistence behavior:** It mutates CP0 Config cacheability bits on the boot CPU. That CPU state persists until changed and affects performance and memory behavior for cached kernel segments.

**Dependencies and integration points:** Depends on MIPS assembly symbols `CP0_CONFIG`, `CONF_CM_CMASK`, and `CONF_CM_CACHABLE_NONCOHERENT` from low-level headers. Integrated by MIPS entry assembly for the ATH79 machine.

**Risks:** Incorrect CP0 manipulation can break caching or early boot. The macro assumes the selected cacheability is valid for all ATH79 CPUs and that changing it at this point is safe. Any SMP enablement would need real slave setup.

**Test signals:** Boot with multiple bootloaders, verify no early cache exceptions, compare memory bandwidth/performance before and after entry setup, and run cache coherency and DMA tests after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/kernel-entry-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1000.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1000.h

**Purpose:** This is the central Alchemy Au1x00 platform header. It defines interrupt numbering, common clock names, physical address maps, register offsets, CPU-type detection, early MMIO helpers, UART helpers, sleep/USB declarations, PCI platform hooks, IrDA platform data, Au1300 pin/power controls, and SoC-specific IRQ enums for Au1000/Au1100/Au1500/Au1550/Au1200/Au1300.

**Important APIs/types/functions:** Key exports include `AU1000_INTC*`, `ALCHEMY_GPIC_*`, `ALCHEMY_*_CLK`, many `*_PHYS_ADDR` constants, GPIC register/config macros, SDRAM/static-memory/PCI/SYS register fields, `alchemy_rdsys/wrsys()`, `alchemy_rdsmem/wrsmem()`, `au1xxx_cpu_has_pll_wo()`, `au1xxx_cpu_needs_config_od()`, `alchemy_get_cputype()`, `alchemy_get_uarts()`, `alchemy_uart_enable/disable/putchar()`, `alchemy_get_macs()`, sleep functions, `alchemy_usb_control()`, `struct alchemy_pci_platdata`, `struct au1k_irda_platform_data`, `enum au1300_multifunc_pins`, Au1300 pinfunc/priority/DBDMA/VSS declarations, and per-SoC interrupt enums.

**Control flow:** Early boot uses PRID-based helpers to select chip type and errata behavior, board setup uses the address map and interrupt enums to register platform devices, UART helpers directly reset/clock/poll TX for early output, and power/USB/PCI/pinmux helpers are called from common Alchemy code and board files.

**State and persistence behavior:** Inline helpers write SYS, static-memory, UART, GPIC, and PCI-related hardware registers through KSEG1 raw MMIO and issue write barriers. They do not hold private locks. External declarations mutate sleep, USB, pinmux, and VSS state in their implementations.

**Dependencies and integration points:** Depends on MIPS CP0 PRID values, KSEG1 addressing, Linux IO/IRQ/delay APIs, board files, PCI core, USB host/device code, serial console, GPIC/gpioint code, and platform-device registration.

**Risks:** The header centralizes many SoC generations with overlapping physical addresses. Wrong CPU-type detection or address choice can access the wrong device. Early raw MMIO bypasses ioremap and locking, so ordering and CPU/SoC guards matter. Errata helpers must remain aligned with real silicon revisions.

**Test signals:** Boot all enabled Alchemy CPU families, validate clock names, early UART output, PCI windows, USB control, sleep/resume, GPIO/GPIC interrupts, MAC counts, and board IRQ assignments. Compare PRID switch cases with supported CPU table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1000_dma.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1000_dma.h

**Purpose:** Defines the legacy Au1000-style eight-channel, double-buffer DMA controller interface used by early Alchemy peripheral drivers.

**Important APIs/types/functions:** Exports DMA register offsets and mode bits, device ID enums for primary and AU1100 secondary banks, `struct dma_chan`, extern `au1000_dma_table[]`, `request_au1000_dma()`, `free_au1000_dma()`, proc read hook, and `au1000_dma_spin_lock`. Inline API includes `get_dma_chan()`, `claim_dma_lock()/release_dma_lock()`, buffer enable helpers, `start_dma()`, `halt_dma()`, `disable_dma()`, `dma_halted()`, `init_dma()`, mode/fifo/address/count setters, done-bit clear/query helpers, `get_dma_done_irq()`, and `get_dma_residue()`.

**Control flow:** Drivers request a channel, set permitted mode bits, initialize FIFO/device ID, program buffer addresses/counts, enable buffers, start DMA, handle done interrupts, clear done bits, and halt/disable on teardown. `halt_dma()` polls the hardware halt bit and logs if it expires.

**State and persistence behavior:** Software state lives in the global channel table and spinlock; hardware state lives in channel MMIO registers. The inline layer silently returns on invalid/unallocated channels, which avoids crashes but can hide misuse.

**Dependencies and integration points:** Depends on Linux raw IO, spinlocks, delays, IRQ handler types, `CPHYSADDR()`, and DMA controller implementation in Alchemy common code. Used by UART, AC97, USB device, I2S, SD, and general-purpose DMA users.

**Risks:** Double-buffer ownership and count masks are easy to misuse. `disable_dma()` writes `~DMA_GO` to the clear register, relying on write-one-to-clear semantics. Residue conversion depends on DMA width bits. Missing locks around register programming by callers can race interrupts.

**Test signals:** Exercise each device ID, allocate/free channels under contention, run RX/TX double-buffer transfers, verify interrupt clearing, halt timeout behavior, residue accounting for 8/16/32-bit widths, and invalid-channel handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1000_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1100_mmc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1100_mmc.h

**Purpose:** Provides register offsets, bit definitions, and board platform data for the Au1100/Au1x MMC/SD controller driver.

**Important APIs/types/functions:** Defines `struct au1xmmc_platform_data` with card-detect setup/status, read-only, power control, LED, and host-capability mask hooks. Exports `SD0_BASE`, `SD1_BASE`, register offsets such as `SD_TXPORT`, `SD_RXPORT`, `SD_CONFIG`, `SD_ENABLE`, `SD_BLKSIZE`, `SD_STATUS`, `SD_CMD`, response and timeout registers, plus masks for config/status FIFO, command, response, block size/count, and enable bits.

**Control flow:** Board code supplies callbacks, the MMC driver programs clock/divider and enable bits, issues commands through `SD_CMDARG`/`SD_CMD`, transfers data through TX/RX ports or DMA, watches status bits, and calls board hooks for power/card state.

**State and persistence behavior:** The header owns no state. Runtime state is in controller registers and board callback side effects such as card power, LED state, and host capabilities.

**Dependencies and integration points:** Depends on `<linux/leds.h>` and the MMC core driver. Integrates with Alchemy address definitions, GPIO/card-detect hardware, and board-specific power control.

**Risks:** Register masks include reserved/placeholder fields and direct physical base constants, so mismatched controller revisions can fail silently. Board callbacks receive opaque `mmc_host` pointers, making type misuse possible. Wrong block count/size or status handling can corrupt transfers.

**Test signals:** Probe both slots where present, test card insertion/removal, read-only detection, power cycling, LED behavior, PIO/DMA transfers, timeout/error reporting, and broad MMC/SD card compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1100_mmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1200fb.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1200fb.h

**Purpose:** Defines platform data for the Au1200 framebuffer/LCD driver.

**Important APIs/types/functions:** Exports `struct au1200fb_platdata` with board callbacks `panel_index()`, `panel_init()`, and `panel_shutdown()`. It declares no register constants or inline helpers.

**Control flow:** The framebuffer driver calls into these board hooks to choose a panel profile and sequence board-specific panel power/init/shutdown around LCD controller operation.

**State and persistence behavior:** No local state. State is external: panel power rails, reset lines, backlight, and selected panel index as implemented by board callbacks.

**Dependencies and integration points:** Integrated by Au1200 board files and the `au1200fb` platform driver. It depends on board code matching callback semantics expected by the driver.

**Risks:** Null or incorrect callbacks can leave panels uninitialized, powered incorrectly, or selected with the wrong mode. The header does not encode error handling beyond callback return values.

**Test signals:** Build the framebuffer driver and board files, boot with each supported panel, test mode selection, blank/unblank, shutdown/reboot paths, and suspend/resume power sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1200fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1550_spi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1550_spi.h

**Purpose:** Defines board/platform data for the Au1550 PSC SPI controller driver.

**Important APIs/types/functions:** Exports `struct au1550_spi_info` with `mainclk_hz`, `num_chipselect`, and board-provided `activate_cs()`/`deactivate_cs()` callbacks that receive the SPI info object, chip-select index, and polarity.

**Control flow:** SPI controller setup reads the input clock and number of chipselects, then invokes activate/deactivate callbacks around transfers to drive board-specific CS GPIOs or glue logic while PSC SPI registers are managed elsewhere.

**State and persistence behavior:** No local storage. Board callbacks mutate chip-select hardware state. `mainclk_hz` is persistent configuration supplied during platform registration.

**Dependencies and integration points:** Integrated by Au1550 PSC SPI driver, board files, and `au1xxx_psc.h` register definitions. Uses Linux fixed-width integer types through normal include context.

**Risks:** Bad clock values break SPI timing; wrong CS polarity or callback sequencing can corrupt flash/peripheral transactions. The header does not bound `num_chipselect` or validate callback presence.

**Test signals:** Probe SPI devices, test each CS line and polarity, verify transfer speed calculations against scope/logic analyzer, and test concurrent SPI messages if the driver serializes correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1550_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1550nd.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1550nd.h

**Purpose:** Provides platform data for the Au1550 NAND driver.

**Important APIs/types/functions:** Exports `struct au1550nd_platdata` containing an MTD partition table pointer, partition count, and `devwidth` flag where 0 means 8-bit NAND and 1 means 16-bit NAND. It includes `<linux/mtd/partitions.h>`.

**Control flow:** Board registration passes this data to the NAND driver; the driver configures bus width and registers MTD partitions accordingly.

**State and persistence behavior:** No local state. The partition table describes persistent flash layout; wrong values affect MTD device creation and on-flash data interpretation.

**Dependencies and integration points:** Integrated by Au1550 board files, static memory controller setup, NAND/MTD core, and partition parsers.

**Risks:** Incorrect `devwidth` corrupts NAND reads/writes. Stale or wrong partition tables can overwrite bootloader, configuration, or rootfs areas. The structure has no explicit ownership/lifetime annotations for `parts`.

**Test signals:** Probe NAND, validate ID and bus width, compare partition layout with board flash map, run read/write/erase tests on non-critical partitions, and test bad-block handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1550nd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_dbdma.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_dbdma.h

**Purpose:** Defines the descriptor-based DMA controller used by later Alchemy SoCs, including hardware descriptor layouts, device ID assignments, channel state structures, and the exported DBDMA driver API.

**Important APIs/types/functions:** Exports `dbdma_global_t`, `au1x_dma_chan_t`, `au1x_ddma_desc_t`, `dbdev_tab_t`, `chan_tab_t`, descriptor command/status masks, device IDs for Au1550/Au1200/Au1300, custom ID helpers, descriptor width/type/status macros, `NUM_DBDMA_CHANS`, device/channel flags, and APIs such as `au1xxx_dbdma_chan_alloc()`, `au1xxx_dbdma_ring_alloc()`, `au1xxx_dbdma_put_source()`, `au1xxx_dbdma_put_dest()`, `au1xxx_dbdma_get_dest()`, `au1xxx_dbdma_start/stop/reset()`, `au1xxx_get_dma_residue()`, channel free/dump, descriptor put, device add/delete, and next-pointer translation.

**Control flow:** Drivers allocate a source/destination channel, allocate descriptor rings, enqueue source/destination buffers, start the channel, receive completion callbacks, drain descriptors, and stop/reset/free during teardown. Doorbell and descriptor-valid bits drive hardware execution.

**State and persistence behavior:** Software state is in channel tables, descriptor rings, spinlocks, callbacks, and device table entries maintained by the implementation. Hardware state lives in DBDMA global/channel registers and descriptor memory visible to DMA.

**Dependencies and integration points:** Depends on Linux DMA address types and spinlocks in consumers. Integrated by PSC, NAND, MAC, LCD, SD, AES, UART, USB, and memory-to-memory users on Au1550/Au1200/Au1300.

**Risks:** Descriptors must be 32-byte aligned and cache-coherent handling must match `SN/DN/DFN` bits. Wrong device IDs or widths can DMA to the wrong FIFO. Ring ownership, callbacks, and custom device IDs are easy to race or leak. The header contains a FIXME noting API placement concerns.

**Test signals:** Stress descriptor ring allocation/free, memory-to-memory transfers, each peripheral source/destination pair, callback ordering, residue reporting, descriptor alignment, non-coherent buffer handling, and error recovery after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_dbdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_eth.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_eth.h

**Purpose:** Defines platform-specific Ethernet configuration for Au1x00 MAC drivers.

**Important APIs/types/functions:** Exports `struct au1000_eth_platform_data` with PHY static/search flags, PHY address, bus ID, PHY IRQ, and 6-byte MAC address. Declares `au1xxx_override_eth_cfg(unsigned port, struct au1000_eth_platform_data *eth_data)`.

**Control flow:** Board code can override per-port Ethernet configuration before MAC driver registration. The driver then uses PHY search/static settings, interrupt routing, and MAC address data to attach PHYs and configure networking.

**State and persistence behavior:** No local state in the header. The override function implementation mutates platform Ethernet configuration; MAC addresses and PHY config persist as device registration data.

**Dependencies and integration points:** Integrated by Alchemy board setup, Ethernet MAC driver, MII/PHY layer, and NVRAM/bootloader MAC address sources.

**Risks:** Wrong PHY address/search policy can bind the wrong PHY or fail link. Invalid MAC addresses create duplicate network identities. Board overrides need to occur before device registration.

**Test signals:** Boot each board, verify MAC addresses, PHY attachment, link negotiation, PHY IRQ delivery, dual-MAC configurations, and fallback behavior when PHY search flags differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_psc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_psc.h

**Purpose:** Defines register layout and bit fields for Au1xxx Programmable Serial Controllers in AC97, I2S, SPI, and SMBus modes.

**Important APIs/types/functions:** Exports common select/control offsets and mode values, AC97 offsets and config/mask/status/event/CODEC/reset/GPIO bits, `psc_i2s_t` and I2S config/status/event masks, `psc_spi_t` and SPI config/mask/status/event/txrx bits, and SMBus config/mask/protocol/status/event/timer bits. Macros encode FIFO thresholds, DMA enable/disable, protocol start/stop, word lengths, clock divisors, baud fields, slot enables, and interrupt masks.

**Control flow:** PSC drivers select protocol mode, configure clock source/dividers/FIFO thresholds/word sizes, enable DMA or interrupt events, drive protocol control bits, and read status/event registers to service transfers. The header itself is declarative.

**State and persistence behavior:** No C storage. Consumers mutate PSC select/control and protocol registers; state persists until reset or mode switch. Reusing the same PSC across protocols makes mode state mutually exclusive.

**Dependencies and integration points:** Integrated by Alchemy SPI, SMBus/I2C, AC97, I2S/audio, and DBDMA drivers. Works with platform clock, pinmux, and DMA channel setup from other Au1x00 headers.

**Risks:** Many fields overlap by protocol and some macros perform arithmetic on caller-provided lengths/dividers without validation. Incorrect mode selection can make a shared PSC unavailable to another driver. Event/mask naming is similar but not identical between protocols.

**Test signals:** For each protocol, validate PSC select/control sequencing, transfer sizes and clock rates, FIFO thresholds, DMA and interrupt paths, underrun/overrun handling, and mode handoff/reset between users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_psc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/cpu-feature-overrides.h

**Purpose:** Provides compile-time MIPS CPU feature constants for Alchemy Au1x00 platforms.

**Important APIs/types/functions:** Defines many `cpu_has_*` values: TLB and 4K exception/cache present, no FPU, no MIPS16/microMIPS/MIPS64/DSP/MT/virtualization features, counter/watch/divec/prefetch/mcheck/EJTAG/LLSC present, no D-cache aliases, I-cache fills from D-cache, MIPS32r1 yes and r2/r6 no, and no secondary cache line size. It has no functions or storage.

**Control flow:** Generic MIPS code compiles feature-dependent paths based on these constants, affecting cache ops, exception handling, atomics, watchpoints, and instruction selection.

**State and persistence behavior:** No mutable state. It is a compile-time hardware contract for all Au1x00 variants selected by this machine.

**Dependencies and integration points:** Integrated by generic MIPS CPU feature logic and must agree with CP0 PRID handling in `au1000.h` and Kconfig support.

**Risks:** Any incorrect feature bit can emit unsupported instructions or skip required cache handling. The uniform values must remain true for every Au1x00 variant, including Au1300.

**Test signals:** Build all Alchemy defconfigs, boot on representative SoCs, run atomics/LLSC tests, cache coherency tests, watchpoint smoke tests, and verify no FPU/DSP/MIPS32r2-only code is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/gpio-au1000.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/gpio-au1000.h

**Purpose:** Provides legacy Au1000/Au1100/Au1500/Au1550/Au1200 GPIO helpers and GPIO-to-IRQ mappings for GPIO1 and GPIO2 blocks.

**Important APIs/types/functions:** Defines GPIO number spaces `ALCHEMY_GPIO1_BASE` and `ALCHEMY_GPIO2_BASE`, register offsets for SYS GPIO1 and GPIO2 block, per-SoC `gpio*_to_irq()` and `irq_to_gpio()` helpers, GPIO value/direction/validity helpers, `alchemy_gpio1_input_enable()`, GPIO2 interrupt enable/disable helpers, GPIO2 block enable/disable, and wrapper APIs `alchemy_gpio_direction_input/output()`, `alchemy_gpio_get/set_value()`, `alchemy_gpio_is_valid()`, `alchemy_gpio_to_irq()`, and `alchemy_irq_to_gpio()`.

**Control flow:** Callers select GPIO1 or GPIO2 based on GPIO number, then helpers branch on `alchemy_get_cputype()` to apply SoC-specific IRQ routing. Direction/value helpers write raw SYS or GPIO2 registers, and shared-interrupt helpers gate per-pin contribution for grouped GPIO2 IRQs.

**State and persistence behavior:** No private state. The helpers mutate GPIO output, direction, input-enable, interrupt-enable, and block-enable hardware registers. They use local IRQ save/restore around GPIO2 direction and interrupt-enable register read-modify-write sequences.

**Dependencies and integration points:** Depends on `au1000.h`, KSEG1 raw MMIO, local IRQ control, and Linux error code `-ENXIO` through include context. Integrated by early board code and gpiolib registration paths.

**Risks:** GPIO/IRQ mappings differ sharply by SoC, and some GPIO2 interrupt lines are shared. Wrapper helpers do not validate every range before MMIO. GPIO1 input enable has different semantics across chip generations. Read-modify-write protection is local CPU only.

**Test signals:** Test direction/value operations before and after gpiolib registration, per-SoC GPIO-to-IRQ and IRQ-to-GPIO mapping, shared GPIO2 interrupt enable bits, GPIO2 block power enable/disable, and input behavior after `alchemy_gpio1_input_enable()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/gpio-au1000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/gpio-au1300.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/gpio-au1300.h

**Purpose:** Defines inline GPIO helpers for the Au1300 GPIC-backed GPIO controller.

**Important APIs/types/functions:** Exports `AU1300_GPIO_BASE`, `AU1300_GPIO_NUM`, `AU1300_GPIO_MAX`, `AU1300_GPIC_ADDR`, and inline helpers `au1300_gpio_get_value()`, `au1300_gpio_direction_input()`, `au1300_gpio_set_value()`, `au1300_gpio_direction_output()`, `au1300_gpio_to_irq()`, `au1300_irq_to_gpio()`, `au1300_gpio_is_valid()`, and `au1300_gpio_getinitlvl()`.

**Control flow:** Helpers compute the GPIC bank offset and bit mask from a GPIO number, then read or write GPIC pin-value, pin-clear, device-clear, and reset-value registers. IRQ mapping is direct from GPIO number to `AU1300_FIRST_INT`.

**State and persistence behavior:** No software state. Hardware state includes GPIC pin levels, device/GPIO ownership, and reset-captured initial levels for GPIO 0-63.

**Dependencies and integration points:** Depends on `au1000.h`, `addrspace.h`, `io.h`, GPIC macros, and `alchemy_get_cputype()`. Integrated with Au1300 gpiolib, interrupt controller, pinmux, and board setup.

**Risks:** `au1300_gpio_is_valid()` only accepts Au1300 CPU type; using helpers on older Alchemy chips is invalid. Range checking is minimal in value/direction helpers. GPIOs above 63 have no reset-level support. Hardware automatically switches output state on value writes.

**Test signals:** Boot Au1300, test all exposed GPIOs 0-74, verify GPIO-to-IRQ direct mapping, initial level readback for 0-63, device-to-GPIO ownership transition, and gpiolib integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/gpio-au1300.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/prom.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/prom.h

**Purpose:** Declares Alchemy PROM/bootloader argument and environment access helpers.

**Important APIs/types/functions:** Exports `prom_argc`, `prom_argv`, `prom_envp`, `prom_init_cmdline()`, `prom_getenv(char *envname)`, and `prom_get_ethernet_addr(char *ethernet_addr)`.

**Control flow:** Early boot initializes command line state from PROM arguments, queries environment variables, and extracts Ethernet addresses before platform devices are registered.

**State and persistence behavior:** The extern globals hold bootloader-provided argument/environment pointers. Helper implementations may copy boot data into kernel command line and network configuration. No state is defined in the header.

**Dependencies and integration points:** Integrated by Alchemy prom init, board setup, Ethernet platform data, and early kernel command-line construction.

**Risks:** PROM pointers are early-boot data with architecture-specific lifetime/format assumptions. MAC address parsing must handle missing or malformed environment values. Command-line initialization errors can affect rootfs and console selection.

**Test signals:** Boot with multiple bootloaders, verify kernel command line, environment lookup, MAC address extraction, missing variable behavior, and no invalid early pointer dereferences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/prom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/bcm47xx.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/bcm47xx.h

**Purpose:** Defines the BCM47xx common bus abstraction for systems using either SSB or BCMA internal buses.

**Important APIs/types/functions:** Exports `enum bcm47xx_bus_type`, `union bcm47xx_bus` containing `struct ssb_bus` and/or `struct bcma_soc` depending on Kconfig, extern `bcm47xx_bus`, extern `bcm47xx_bus_type`, and `bcm47xx_set_system_type(u16 chip_id)`. Includes SSB, BCMA, NVRAM, and SPROM headers.

**Control flow:** Platform probe selects the active internal bus, populates the union, sets the bus type, and records a system type based on chip ID. Later code branches on `bcm47xx_bus_type` to access SSB or BCMA-specific resources.

**State and persistence behavior:** Global bus union and bus type persist for the running kernel and represent discovered SoC fabric state. The header declares, but does not define, that state.

**Dependencies and integration points:** Integrated by BCM47xx early platform setup, SSB/BCMA bus cores, NVRAM/SPROM handling, wireless/Ethernet/flash drivers, and system type reporting.

**Risks:** The union is Kconfig-shaped; code must not access unavailable members. Incorrect bus type or chip ID breaks all downstream device discovery. Including both bus backends requires careful runtime checks.

**Test signals:** Build SSB-only, BCMA-only, and combined configurations where supported; boot hardware from both families, verify bus detection, SPROM/NVRAM access, device enumeration, and system type strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/bcm47xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/bcm47xx_board.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/bcm47xx_board.h

**Purpose:** Enumerates known BCM47xx router/board models and declares board detection accessors.

**Important APIs/types/functions:** Defines `enum bcm47xx_board` with many ASUS, Belkin, Buffalo, Cisco/Linksys, Dell, D-Link, Huawei, Luxul, Microsoft, Motorola, Netgear, Phicomm, Siemens, SimpleTech, ZTE, plus `UNKNOWN` and `NO`. Exports `BCM47XX_BOARD_MAX_NAME`, `bcm47xx_board_detect()`, `bcm47xx_board_get()`, and `bcm47xx_board_get_name()`.

**Control flow:** Early board detection matches NVRAM/SPROM/model data to an enum, stores the result in implementation state, and later board-specific quirks or LEDs/buttons/devices branch on `bcm47xx_board_get()`.

**State and persistence behavior:** The header has no storage, but the implementation maintains detected board identity for the boot lifetime. Board identity effectively becomes platform configuration state.

**Dependencies and integration points:** Integrated with BCM47xx NVRAM parsing, board setup, LEDs/buttons, Ethernet, wireless calibration, flash layout, and user-visible machine name reporting.

**Risks:** Adding/removing/reordering enum values can break code that stores or compares numeric IDs internally. Board-name length limits can truncate model strings. Misdetecting a board can apply wrong GPIO, switch, LED, or flash quirks.

**Test signals:** Boot boards across vendor families, verify detected enum/name, compare against NVRAM model fields, test board-specific buttons/LEDs/network ports, and build-check every enum user after adding IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/bcm47xx_board.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/cpu-feature-overrides.h

**Purpose:** Provides BCM47xx compile-time CPU feature constants, with different assumptions for BCMA-only versus SSB-only builds.

**Important APIs/types/functions:** Defines MIPS feature macros for TLB, 4K cache/exception, no FPU/32FPR, counter, divec, prefetch, mcheck, EJTAG, LL/SC, no 64-bit, no MT/VZ, and cache-line sizes. Conditional blocks set `cpu_has_watch`, `cpu_has_mips32r2`, `cpu_has_dsp`, `cpu_has_dsp2`, `cpu_has_vint`, line sizes, and perf counter interrupt bit differently for BCMA-only and SSB-only builds. Some features such as `cpu_has_mips16` and `cpu_has_dc_aliases` are intentionally left to generic detection/comments.

**Control flow:** Generic MIPS code compiles feature-dependent paths based on these constants. Kconfig selection of SSB or BCMA materially changes emitted code and runtime expectations.

**State and persistence behavior:** No mutable state. The file is a compile-time CPU capability contract.

**Dependencies and integration points:** Integrated by BCM47xx Kconfig, generic MIPS CPU feature handling, exception/cache/perf/watchpoint code, and SSB/BCMA platform selection.

**Risks:** Combined SSB+BCMA builds leave some conditional features undefined here and must rely on generic fallback. Wrong line size or MIPS32r2/DSP/watch assumptions can produce invalid instructions or broken cache maintenance on older cores.

**Test signals:** Build SSB-only, BCMA-only, and combined configs; boot representative cores; run cache tests, perf counter/watchpoint tests, and scan generated config for expected feature macro values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_board.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_board.h

**Purpose:** Declares BCM63xx board-level initialization entry points.

**Important APIs/types/functions:** Exports `board_get_name()`, `board_prom_init()`, `board_setup()`, and `board_register_devices()`.

**Control flow:** Boot code calls PROM init, board setup, and device registration to convert NVRAM/board data into platform devices and machine state. `board_get_name()` exposes the selected board identity.

**State and persistence behavior:** No state in the header. Implementations initialize persistent boot-time board configuration, platform resources, and device registration state.

**Dependencies and integration points:** Integrated by BCM63xx arch init, NVRAM, flash, GPIO, Ethernet, PCI, UART, SPI, and USB registration paths.

**Risks:** Ordering is critical: devices registered before board/NVRAM setup can receive incomplete resources. Board name mismatches can select wrong quirks.

**Test signals:** Boot boards with known NVRAM, verify board name, platform-device list, resource ranges, and failure behavior when device registration returns errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_board.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_cpu.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_cpu.h

**Purpose:** Central BCM63xx CPU identity, register-set address, IRQ mapping, and machine-control contract.

**Important APIs/types/functions:** Defines CPU IDs for BCM3368/6328/6338/6345/6348/6358/6362/6368, `bcm63xx_cpu_init()`, `bcm63xx_get_cpu_rev()`, `bcm63xx_get_cpu_freq()`, global `bcm63xx_cpu_id`, `bcm63xx_get_cpu_id()`, `BCMCPU_IS_*()` predicates, `enum bcm63xx_regs_set`, register-set size macros, per-CPU base address constants, `bcm63xx_regs_base`, `__GEN_CPU_REGS_TABLE()`, `bcm63xx_regset_address()`, `enum bcm63xx_irq`, per-CPU IRQ constants including high IRQ banks, `bcm63xx_irqs`, `__GEN_CPU_IRQ_TABLE()`, `bcm63xx_get_irq_number()`, `bcm63xx_get_memory_size()`, `bcm63xx_machine_halt()`, and `bcm63xx_machine_reboot()`.

**Control flow:** CPU init identifies silicon and selects the active register-base and IRQ tables. Device registration and IO helpers query `bcm63xx_regset_address()` and `bcm63xx_get_irq_number()` so drivers can remain SoC-neutral. CPU predicates gate feature-specific paths. Halt/reboot functions are used by machine operations.

**State and persistence behavior:** Global CPU ID, register-base table pointer, and IRQ table pointer persist after early init. The header maps absent blocks to `0xdeadbeef` or zero IRQs, so callers must gate unsupported resources.

**Dependencies and integration points:** Depends on Linux types/init, Kconfig CPU options, `IRQ_INTERNAL_BASE` from `bcm63xx_irq.h` include ordering, and all BCM63xx platform device headers. It is consumed by IO, GPIO, flash, SPI, Ethernet, PCI, USB, timer, watchdog, and memory code.

**Risks:** Table entries are long and repetitive; a single wrong base/IRQ can break a device only on one SoC. Unsupported placeholders can become real bad MMIO accesses if callers skip feature checks. `unreachable()` in unsupported CPU ID paths assumes Kconfig and runtime ID cannot disagree.

**Test signals:** Build every CPU Kconfig combination, boot all supported SoCs, verify `/proc/cpuinfo`, memory size, register resources, IRQ tables, timer/watchdog/UART, PCI/USB/Ethernet/SPI, and assert no driver maps `0xdeadbeef` resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_cs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_cs.h

**Purpose:** Declares chip-select configuration helpers for BCM63xx external memory/peripheral interfaces.

**Important APIs/types/functions:** Exports `bcm63xx_set_cs_base(cs, base, size)`, `bcm63xx_set_cs_timing(cs, wait, setup, hold)`, `bcm63xx_set_cs_param(cs, flags)`, and `bcm63xx_set_cs_status(cs, enable)`.

**Control flow:** Board or flash/PCMCIA setup code programs the chip-select base window, timing, bus parameters, then enables/disables the CS line.

**State and persistence behavior:** No local state. Implementations mutate external bus controller registers that persist until reset or reconfiguration.

**Dependencies and integration points:** Integrated by flash, PCMCIA, board setup, and memory controller code. Uses `u32` through include context, so callers generally include CPU/IO types first.

**Risks:** Wrong base/size/timing can make flash or PCMCIA unreadable or corrupt accesses. No constraints are visible in the prototype for valid chip-select numbers or timing ranges.

**Test signals:** Probe flash/PCMCIA devices, verify CS windows with resource maps, stress reads/writes at configured timings, and test disable/enable transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_cs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_enet.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_enet.h

**Purpose:** Defines BCM63xx Ethernet MAC and Ethernet switch platform data plus ENET DMA channel register indexing.

**Important APIs/types/functions:** Exports `struct bcm63xx_enet_platform_data` with MAC, PHY presence/internal/external info, PHY IRQ, pause/forced link settings, optional MII config callback, DMA masks, SRAM flag, channel width/descriptor shift, and RX/TX channels. Defines switch constants `ENETSW_MAX_PORT`, `ENETSW_PORTS_6328`, `ENETSW_PORTS_6368`, `ENETSW_RGMII_PORT0`, `struct bcm63xx_enetsw_port`, `struct bcm63xx_enetsw_platform_data`, registration functions `bcm63xx_enet_register()` and `bcm63xx_enetsw_register()`, `enum bcm63xx_regs_enetdmac`, and inline `bcm63xx_enetdmacreg()`.

**Control flow:** Board setup fills MAC/PHY/switch/DMA data, registers either legacy MAC units or integrated switch devices, and the network driver configures PHY or forced link state, DMA channels, and MII callbacks from that data.

**State and persistence behavior:** Platform data persists as device registration configuration. DMA register offset table is extern state selected by CPU code. Network runtime state is held by drivers, not this header.

**Dependencies and integration points:** Depends on Ethernet address types, `bcm63xx_regs.h`, net_device callback signatures, BCM63xx CPU/resource tables, PHY/MII core, and IUDMA descriptors.

**Risks:** Misconfigured PHY and DMA masks can prevent link or DMA traffic. Callback prototypes couple board code to driver MII semantics. Switch port arrays must match real port count and RGMII wiring.

**Test signals:** Boot MAC and switch variants, verify MAC address, PHY attach/interrupt, pause and forced-link modes, RX/TX DMA interrupts, integrated SRAM behavior, all switch ports, and register offset selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_enet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_flash.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_flash.h

**Purpose:** Declares BCM63xx flash type identifiers and flash device registration.

**Important APIs/types/functions:** Defines flash types `BCM63XX_FLASH_TYPE_PARALLEL`, `BCM63XX_FLASH_TYPE_SERIAL`, and `BCM63XX_FLASH_TYPE_NAND`, plus `bcm63xx_flash_register()`.

**Control flow:** Board setup detects or selects flash type, then calls registration to create the appropriate MTD/SPI/NAND/parallel flash platform device.

**State and persistence behavior:** No state in the header. Registered flash devices expose persistent storage; wrong type selection affects boot-critical partitions.

**Dependencies and integration points:** Integrated with NVRAM, MTD, SPI/NAND/parallel flash drivers, chip-select setup, and board registration.

**Risks:** Incorrect type causes probe failure or destructive writes through the wrong bus protocol. Flash registration must coordinate with NVRAM and partition parsing.

**Test signals:** Boot each flash type, verify MTD layout, read JEDEC/NAND IDs, mount/read rootfs, and run safe read-only checks on bootloader/NVRAM partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_flash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_hsspi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_hsspi.h

**Purpose:** Declares registration for the BCM63xx high-speed SPI controller.

**Important APIs/types/functions:** Exports `bcm63xx_hsspi_register()` and includes `<linux/types.h>`.

**Control flow:** Board/device setup calls the registration helper when the active SoC has an HSSPI register set and IRQ.

**State and persistence behavior:** No local state. The implementation registers platform-device resources for HSSPI hardware.

**Dependencies and integration points:** Depends on CPU register-set/IRQ tables, SPI core, flash/device board data, and HSSPI-capable SoCs such as BCM6328/6362.

**Risks:** Calling registration on a SoC with `0xdeadbeef` HSSPI base or zero IRQ would create invalid resources. HSSPI and legacy SPI support must be selected correctly.

**Test signals:** Boot HSSPI-capable boards, verify SPI controller probe, flash/peripheral enumeration, transfer speed, IRQ handling, and absence on unsupported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_hsspi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_pci.h

**Purpose:** Publishes BCM63xx PCI enable state.

**Important APIs/types/functions:** Exports `extern int bcm63xx_pci_enabled`.

**Control flow:** Board and PCI setup code read or set this flag to decide whether to initialize PCI resources and register PCI devices.

**State and persistence behavior:** The extern integer is global boot-time state owned by implementation code. It persists after detection/setup and gates PCI availability.

**Dependencies and integration points:** Integrated by BCM63xx PCI host code, board setup, and possibly bootloader/NVRAM configuration.

**Risks:** A stale or incorrect enabled flag can skip real PCI hardware or probe absent/disabled hardware. The header exposes mutable global state without accessor validation.

**Test signals:** Boot PCI-capable and non-PCI boards, verify flag value, PCI host registration, resource windows, enumeration, and disabled-board behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_pcmcia.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_pcmcia.h

**Purpose:** Defines platform data and registration for BCM63xx PCMCIA.

**Important APIs/types/functions:** Exports `struct bcm63xx_pcmcia_platform_data` with `ready_gpio`, and `bcm63xx_pcmcia_register()`.

**Control flow:** Board setup supplies the ready GPIO and calls registration, after which the PCMCIA driver uses fixed IO/memory windows and GPIO readiness to manage cards.

**State and persistence behavior:** No local state. Platform data persists in the registered device and references GPIO hardware state.

**Dependencies and integration points:** Integrates with BCM63xx IO window constants, chip-select setup, GPIO, IRQ tables, and PCMCIA core.

**Risks:** Wrong ready GPIO or unsupported SoC resources can make card detection unreliable. PCMCIA shares external bus windows with timing/chip-select setup.

**Test signals:** Probe PCMCIA on supported boards, validate ready GPIO polarity/state, card insertion/removal, IO/memory access windows, and unsupported-board absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_pcmcia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_spi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_spi.h

**Purpose:** Declares registration for the legacy BCM63xx SPI controller.

**Important APIs/types/functions:** Includes Linux types, `bcm63xx_io.h`, and `bcm63xx_regs.h`, and exports `bcm63xx_spi_register()`.

**Control flow:** Board setup calls the registration helper for SoCs using the legacy SPI block. The implementation obtains resources through CPU register-set helpers and registers the SPI controller.

**State and persistence behavior:** No local state. Registration creates platform device state and exposes SPI flash/peripherals.

**Dependencies and integration points:** Integrated with CPU register maps, raw IO helpers, SPI core, flash registration, and board-selected chip-selects.

**Risks:** Confusing legacy SPI with HSSPI can map the wrong controller. Including IO/register headers from this small declaration header increases coupling and can hide missing includes in users.

**Test signals:** Boot legacy-SPI boards, verify controller probe, SPI flash reads, chip-select operation, IRQ/polling path, and no registration on HSSPI-only SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_uart.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_uart.h

**Purpose:** Declares BCM63xx UART platform registration.

**Important APIs/types/functions:** Exports `bcm63xx_uart_register(unsigned int id)`.

**Control flow:** Board setup registers UART instances by ID, and the implementation maps ID to the correct register set/IRQ from CPU tables.

**State and persistence behavior:** No header state. Registration creates serial platform device state and console resources.

**Dependencies and integration points:** Integrated by BCM63xx board setup, serial driver, console/early console path, CPU register and IRQ tables.

**Risks:** Registering an ID absent on a SoC can point at `UART1` placeholder resources. Console availability is sensitive to registration order and clock/frequency setup.

**Test signals:** Boot with console on UART0 and UART1 where present, verify baud rate, interrupts, early/late console handoff, and invalid-ID handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_uart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_usb_usbd.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_usb_usbd.h

**Purpose:** Defines platform data and registration for the BCM63xx USB device controller.

**Important APIs/types/functions:** Exports `struct bcm63xx_usbd_platform_data` with `use_fullspeed` and `port_no`, and `bcm63xx_usbd_register(const struct bcm63xx_usbd_platform_data *pd)`.

**Control flow:** Board setup passes speed limitation and PHY port selection to the USB device registration helper; the USB gadget driver then uses those resources.

**State and persistence behavior:** No local state. Platform data persists with the registered USB device and controls hardware mode/port selection.

**Dependencies and integration points:** Depends on CPU register/IRQ tables for USBD and DMA resources, USB gadget core, PHY/port wiring, and board hardware limits.

**Risks:** Wrong `port_no` can enable the wrong PHY. Ignoring `use_fullspeed` may advertise unsupported high-speed mode. USBD resources are absent on many SoCs and must be guarded.

**Test signals:** Probe gadget mode on supported boards, test full-speed-only boards, enumerate on host, transfer data over RX/TX DMA endpoints, and verify absence on host-only SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_usb_usbd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_gpio.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_gpio.h

**Purpose:** Declares BCM63xx GPIO initialization and per-CPU GPIO line counts.

**Important APIs/types/functions:** Exports `bcm63xx_gpio_init()`, inline `bcm63xx_gpio_count()`, and direction constants `BCM63XX_GPIO_DIR_OUT`/`BCM63XX_GPIO_DIR_IN`. GPIO count returns 32 for BCM6328, 40 for BCM3368, 8 for BCM6338, 16 for BCM6345, 38 for BCM6358/6368, 48 for BCM6362, and 37 for BCM6348/default.

**Control flow:** GPIO init registers the controller, and consumers use the count helper to size chips or validate GPIO numbers based on current CPU ID.

**State and persistence behavior:** No local state. Runtime state is in GPIO controller registers and gpiolib objects created by the implementation.

**Dependencies and integration points:** Depends on `bcm63xx_cpu.h` CPU detection. Integrated by board LEDs/buttons, PCI/PCMCIA ready lines, USB, Ethernet PHY reset, and gpiolib.

**Risks:** GPIO count defaults to 37 for unknown/default path, so CPU detection errors can expose invalid lines. Direction constants are hardware convention-specific and may be confused with gpiolib logical direction values.

**Test signals:** Boot every SoC family, verify registered GPIO count, exercise boundary GPIOs, direction/value operations, interrupt-capable lines, and board LEDs/buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_io.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_io.h

**Purpose:** Defines BCM63xx physical IO windows and raw register access macros for current-CPU register sets.

**Important APIs/types/functions:** Exports PCMCIA common/attribute/IO, PCI memory/IO, CardBus, and PCIe memory physical windows; `BCM_REGS_VA(x)`; raw volatile `bcm_readb/w/l/q()` and `bcm_writeb/w/l/q()` macros; generic `bcm_rset_read*()`/`bcm_rset_write*()` helpers; and convenience helpers for performance, timer, watchdog, GPIO, UART0, MPI, PCMCIA, PCIe, SDRAM, MEMC, DDR, and MISC register sets.

**Control flow:** Drivers ask `bcm63xx_regset_address()` for the active SoC base and then perform volatile MMIO through these helpers. Board/PCI/PCMCIA setup uses the physical window constants for resource creation.

**State and persistence behavior:** No software state. All writes mutate hardware registers directly through uncached/architecture-mapped addresses. The helpers impose no barriers beyond volatile access semantics.

**Dependencies and integration points:** Depends on `bcm63xx_cpu.h`. Integrated by most BCM63xx platform code, including timer, watchdog, GPIO, UART, PCI/PCMCIA, memory controller, and reset/performance blocks.

**Risks:** Direct pointer dereference macros bypass `readl()/writel()` ordering and sparse checks. Passing an unsupported register set can access `0xdeadbeef`. Physical window sizes must remain power-of-two where noted.

**Test signals:** Boot each SoC, verify no invalid MMIO faults, test timer/watchdog/GPIO/UART/PCIe helpers, inspect resource windows, and run sparse/build warnings around `__iomem` usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_irq.h

**Purpose:** Defines BCM63xx base Linux IRQ numbers for internal and external interrupts.

**Important APIs/types/functions:** Exports `IRQ_INTERNAL_BASE` as 8, `IRQ_EXTERNAL_BASE` as 100, and external IRQ aliases `IRQ_EXT_0` through `IRQ_EXT_3`. It includes `bcm63xx_cpu.h`.

**Control flow:** `bcm63xx_cpu.h` per-CPU IRQ tables offset internal device IRQs from `IRQ_INTERNAL_BASE`, while board/interrupt code uses `IRQ_EXT_*` for external lines.

**State and persistence behavior:** No state. Numeric values form a compile-time IRQ numbering contract.

**Dependencies and integration points:** Integrated by CPU IRQ tables, interrupt controller setup, GPIO/external IRQ handling, and platform-device resources.

**Risks:** Header include ordering is delicate because `bcm63xx_cpu.h` also uses `IRQ_INTERNAL_BASE` in per-CPU constants. Changing bases breaks all fixed IRQ resource mappings.

**Test signals:** Build BCM63xx IRQ users, boot and inspect `/proc/interrupts`, trigger internal devices and external IRQ lines, and verify no overlap between internal/high/external ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_iudma.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_iudma.h

**Purpose:** Defines the BCM63xx internal DMA descriptor format and status/control masks used by Ethernet and USB DMA paths.

**Important APIs/types/functions:** Exports `struct bcm_enet_desc` with `len_stat` and `address`; control masks for length, owner, EOP, SOP, ESOP, wrap, USB zero/no-zero; status masks for underrun, append CRC, oversize, RX error, CRC, overflow; and combined `DMADESC_ERR_MASK`.

**Control flow:** Network/USB drivers fill descriptors with address, length, SOP/EOP/WRAP/OWNER bits, hand ownership to hardware, then read status/error bits on completion.

**State and persistence behavior:** Descriptor rings in DMA-coherent memory are shared mutable state between CPU and hardware. The header defines layout only.

**Dependencies and integration points:** Depends on Linux fixed-width types. Integrated by BCM63xx Ethernet MAC/switch and USB device DMA engines, plus cache/DMA mapping code.

**Risks:** Bit ownership and length masks must match hardware exactly. Wrong cache coherency, wrap, or owner handling can corrupt packets or hang DMA. Error mask excludes `DMADESC_APPEND_CRC`, which is status not necessarily error.

**Test signals:** Run RX/TX network traffic, USB DMA transfers, ring wrap stress, error injection for CRC/overflow/underrun, and verify descriptor ownership transitions with DMA debug enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_iudma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_nvram.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_nvram.h

**Purpose:** Declares BCM63xx NVRAM initialization and accessors for board identity, MAC addresses, and PSI size.

**Important APIs/types/functions:** Exports `bcm63xx_nvram_init(void *nvram)`, `bcm63xx_nvram_get_name()`, `bcm63xx_nvram_get_mac_address(u8 *mac)`, and `bcm63xx_nvram_get_psi_size()`. Comments document checksum validation, a 16-byte board-name field that may not be null-terminated, and monotonic allocation of MAC addresses from NVRAM.

**Control flow:** Early boot copies and validates NVRAM from the provided address, board code reads the board name, device registration requests MAC addresses, and storage/flash code reads PSI size.

**State and persistence behavior:** Implementation keeps a local NVRAM copy and tracks allocated MAC addresses. NVRAM represents persistent board configuration stored in flash.

**Dependencies and integration points:** Depends on Linux types. Integrated by board detection, Ethernet registration, flash/partition layout, and bootloader-provided NVRAM location.

**Risks:** Board name may lack a terminator, so string users must bound copies. Bad checksum or malformed MAC pool can break board detection/network identity. Repeated MAC allocation changes results by call order.

**Test signals:** Boot with valid and invalid NVRAM, verify checksum handling, bounded board-name use, deterministic MAC allocation across devices, PSI size parsing, and fallback behavior for missing fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_nvram.h -->
