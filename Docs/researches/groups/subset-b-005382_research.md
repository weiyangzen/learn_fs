# subset-b-005382 SPI Driver Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw-dma.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-dw-dma.c

## Purpose
Implements the DMA backend for the Synopsys DesignWare SPI core. It plugs into `struct dw_spi_dma_ops` so the shared DW SPI core can initialize DMA channels, decide whether a transfer is DMA-capable, set up controller DMA registers, execute transfers, and stop or release DMA resources. It has two channel-acquisition paths: Intel Medfield-specific PCI DMA discovery and generic named `rx`/`tx` DMA channels.

## Important APIs, Types, And Functions
Key entry points are `dw_spi_dma_setup_mfld()` and `dw_spi_dma_setup_generic()`, both exported in namespace `SPI_DW_CORE`. They install either `dw_spi_dma_mfld_ops` or `dw_spi_dma_generic_ops` into `dws->dma_ops`. Initialization flows through `dw_spi_dma_init_mfld()` or `dw_spi_dma_init_generic()`, then `dw_spi_dma_caps_init()` and `dw_spi_dma_maxburst_init()`. Transfer work is split across `dw_spi_dma_setup()`, `dw_spi_dma_transfer()`, `dw_spi_dma_transfer_all()`, and `dw_spi_dma_transfer_one()`. Completion is driven by DMA callbacks `dw_spi_dma_tx_done()` and `dw_spi_dma_rx_done()` plus the DW interrupt handler callback `dw_spi_dma_transfer_handler()`.

## Control Flow
After channel allocation, the driver records channels in both `struct dw_spi` and the SPI controller. A transfer is eligible only when its length exceeds FIFO depth and the current word width is supported by DMA address-width capabilities. Setup configures slave directions, bus widths, DMA thresholds, `DW_SPI_DMACR`, interrupt masks, and the DW core transfer handler. Normal transfers submit TX and optional RX scatterlists once, starting RX before TX. If the DMA engine cannot safely traverse large SG lists in hardware, `dw_spi_dma_transfer_one()` virtually splits TX/RX SGs into matched one-entry chunks to avoid RX FIFO overflow.

## State And Persistence
State is runtime-only in `struct dw_spi`: channel pointers, burst levels, SG burst limit, supported address widths, `dma_chan_busy` bits, DMA completion, and the data-register DMA address. No persistent storage is used. Cleanup terminates live channels and releases them; `dw_spi_dma_stop()` terminates only channels whose busy bits remain set.

## Dependencies And Integration Points
Depends on Linux DMAengine, DMA mapping/scatterlist infrastructure, PCI lookup for Medfield, and the DW SPI register helpers from `spi-dw.h`. It integrates with the shared DW core via `dws->dma_ops`, `dws->transfer_handler`, and SPI controller `can_dma`, `dma_rx`, and `dma_tx` fields.

## Risks
The main risk is synchronization between TX and RX DMA. The code explicitly starts RX first, limits TX bursts, waits for residual FIFO drain, and chunks SG lists when SG hardware traversal may race. Timeout estimates depend on effective bus speed, so wrong speed metadata can cause false timeouts or long waits. TX-only DMA requires a TX buffer; `dw_spi_dma_setup()` rejects missing `tx_buf`.

## Test Signals
Useful tests include long full-duplex SG transfers with mismatched SG boundaries, TX-only transfers, FIFO-sized transfers that must stay PIO, DMA timeout injection, unsupported word-width fallback, suspend/remove during DMA, and Medfield/generic channel allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw-mmio.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-dw-mmio.c

## Purpose
Provides the platform/MMIO bus glue for the DesignWare SPI core. It maps registers, obtains clocks/resets/IRQ, applies SoC-specific quirks, optionally wires DMA setup, registers the shared DW SPI controller, and handles suspend/resume/remove.

## Important APIs, Types, And Functions
`struct dw_spi_mmio` wraps `struct dw_spi` with core clock, optional APB clock, reset, and private quirk state. SoC initialization hooks include `dw_spi_mscc_ocelot_init()`, `dw_spi_mscc_jaguar2_init()`, `dw_spi_mscc_sparx5_init()`, `dw_spi_alpine_init()`, `dw_spi_pssi_init()`, `dw_spi_hssi_init()`, `dw_spi_intel_init()`, `dw_spi_mountevans_imc_init()`, `dw_spi_canaan_k210_init()`, and `dw_spi_elba_init()`. Chip-select overrides include MSCC, Sparx5, and Elba implementations. Core lifecycle functions are `dw_spi_mmio_probe()`, `dw_spi_mmio_remove()`, `dw_spi_mmio_suspend()`, and `dw_spi_mmio_resume()`.

## Control Flow
Probe allocates wrapper state, maps resource 0, records physical base, fetches IRQ, enables clocks, deasserts reset, reads `reg-io-width` and `num-cs`, runs match-data initialization, enables runtime PM, and calls `dw_spi_add_controller()`. Suspend asks the shared core to suspend, asserts reset, and disables clocks. Resume enables clocks, deasserts reset, and calls the shared resume path. Remove unregisters the shared controller, disables runtime PM, and asserts reset.

## State And Persistence
State is held in devm-managed wrapper memory and hardware registers. Quirk private data can be a syscon regmap or MSCC structure. No persistent storage exists. Hardware state such as CS override ownership, FIFO length overrides, IP variant ID, and reset/clock state is re-established at probe or resume.

## Dependencies And Integration Points
Depends on platform resources, `clk`, optional `pclk`, reset controls, ACPI/OF matching, syscon/regmap, and the DW core exported APIs. Compatible strings select quirks for Synopsys PSSI/HSSI, MSCC/Microchip, Amazon Alpine, Renesas RZN1, Intel Keem Bay/Mount Evans, Canaan K210, and AMD Pensando Elba.

## Risks
Chip-select override logic is hardware-specific and can break devices if syscon ownership or active-low semantics are wrong. Mount Evans and K210 override FIFO depth to avoid known corruption/overrun errata. Resume ignores errors from `clk_prepare_enable()` and reset deassert in this source, which is a possible robustness gap.

## Test Signals
Probe/remove on each compatible, clock/reset failure injection, CS polarity/override checks with GPIO and native CS, DMA availability for PSSI/HSSI, suspend/resume register access, and FIFO-depth errata regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw-mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw-pci.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-dw-pci.c

## Purpose
Provides PCI glue for the DesignWare SPI core on Intel MID and Elkhart Lake PSE controllers. It maps PCI BAR resources, allocates IRQ vectors, applies device-specific descriptors, enables DMA setup, registers the shared DW SPI controller, and wires PM callbacks.

## Important APIs, Types, And Functions
`struct dw_spi_pci_desc` supplies setup callback, chip-select count, bus number, and maximum frequency. `dw_spi_pci_mid_init()` reads the Intel MID clock-control register and installs Medfield DMA ops. `dw_spi_pci_generic_init()` installs generic DMA ops. Probe/remove are `dw_spi_pci_probe()` and `dw_spi_pci_remove()`, with sleep PM handled by `dw_spi_pci_suspend()` and `dw_spi_pci_resume()`.

## Control Flow
Probe enables the PCI device with managed PCI helpers, allocates `struct dw_spi`, stores BAR physical address, enables bus mastering, allocates one IRQ vector, maps BAR0, sets IRQ, applies descriptor fields, calls the descriptor setup hook, registers the DW controller, records drvdata, and enables runtime autosuspend. Remove forbids runtime PM, resumes the device without changing state, unregisters the DW controller, and frees IRQ vectors. Sleep PM delegates entirely to the shared DW core.

## State And Persistence
Runtime state is held in `struct dw_spi` and PCI core structures. Intel MID clock-derived `max_freq`, descriptor bus number, chip-select count, mapped BAR, and DMA ops are established at probe. No persistent state is written.

## Dependencies And Integration Points
Depends on the PCI subsystem, runtime PM, PCI IRQ vector allocation, and `spi-dw.h` shared core APIs. Device IDs cover Intel MID controller IDs and Elkhart Lake PSE SPI PCI IDs. The module imports namespace `SPI_DW_CORE`.

## Risks
MID clock discovery uses a fixed physical control register mapping; incorrect assumptions here affect clock calculations. Probe error handling frees IRQ vectors but relies on managed mapping/allocation for other resources. Descriptor absence is fatal. Runtime PM autosuspend behavior depends on the shared core being prepared for idle transitions.

## Test Signals
PCI probe/remove for all IDs, IRQ allocation failures, BAR mapping failures, MID clock-divisor validation, DMA channel discovery, runtime autosuspend, and suspend/resume transfer continuity are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-dw.h

## Purpose
Defines the shared private interface for the DesignWare SPI driver family. It centralizes register offsets, bitfields, capability flags, transfer/DMA state structures, register access helpers, chip reset/shutdown helpers, and core function declarations consumed by MMIO, PCI, DMA, and the DW core implementation.

## Important APIs, Types, And Functions
Important types are `struct dw_spi_cfg`, `struct dw_spi_dma_ops`, and `struct dw_spi`. The header defines virtual IP IDs for PSSI/HSSI, version comparison macros, capability flags `DW_SPI_CAP_CS_OVERRIDE` and `DW_SPI_CAP_DFS32`, register offsets from `DW_SPI_CTRLR0` through `DW_SPI_CS_OVERRIDE`, CTRLR0/TMOD/SR/interrupt/DMACR bitfields, and mem-op buffer sizing helpers. Inline APIs include `dw_readl()`, `dw_writel()`, `dw_read_io_reg()`, `dw_write_io_reg()`, `dw_spi_enable_chip()`, `dw_spi_set_clk()`, `dw_spi_mask_intr()`, `dw_spi_umask_intr()`, `dw_spi_reset_chip()`, and `dw_spi_shutdown_chip()`.

## Control Flow
The header itself has no runtime control flow, but its helpers define common sequences: mask/unmask interrupt bits by read-modify-write of `IMR`, reset by disabling the engine, masking interrupts, clearing interrupt status, deselecting CS, and re-enabling, and shutdown by disabling the engine and baud clock. DMA setup declarations become no-ops when `CONFIG_SPI_DW_DMA` is disabled.

## State And Persistence
`struct dw_spi` is the central runtime state: controller pointer, IP/version/capabilities, register base and physical address, IRQ, FIFO/depth/frequency metadata, chip-select callback, current transfer pointers and lengths, memory-op buffer, word width, handler pointer, sample delay state, mem ops, DMA channels and completion, and optional debugfs data. All state is volatile kernel driver state.

## Dependencies And Integration Points
Depends on kernel bitfield/io/scatterlist/debugfs/SPI MEM headers. It is included by DesignWare platform, PCI, DMA, and core files. Exported declarations are implemented by the shared core and used by bus glue modules under namespace `SPI_DW_CORE`.

## Risks
The header is a cross-module ABI inside the driver family. Register offset or bitfield mistakes affect every DW backend. `__raw_readl()`/`__raw_writel()` helpers assume the DW register endianness/ordering expected by the supported platforms, while data-register access can vary by `reg_io_width`.

## Test Signals
Compile coverage with and without `CONFIG_SPI_DW_DMA`, PSSI/HSSI variant detection, register-width access tests, reset/shutdown behavior, interrupt masking, DMA ops linkage, and SPI MEM buffer boundary tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ep93xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-ep93xx.c

## Purpose
Implements a SPI controller driver for Cirrus Logic EP93xx SSP hardware. It supports GPIO-described chip selects, 4- to 16-bit words, interrupt-driven PIO, optional DMA for larger transfers, and controller clock prepare/unprepare hooks.

## Important APIs, Types, And Functions
`struct ep93xx_spi` stores clock, MMIO base, SSPDR physical address, byte counters, FIFO occupancy, DMA channels, scatter tables, and a zero page for dummy TX/RX. Setup and data functions include `ep93xx_spi_calc_divisors()`, `ep93xx_spi_chip_setup()`, `ep93xx_do_write()`, `ep93xx_do_read()`, and `ep93xx_spi_read_write()`. DMA is handled by `ep93xx_spi_dma_prepare()`, `ep93xx_spi_dma_finish()`, `ep93xx_spi_dma_callback()`, and `ep93xx_spi_dma_transfer()`. Lifecycle functions are `ep93xx_spi_probe()` and `ep93xx_spi_remove()`.

## Control Flow
Probe allocates a SPI host, configures callbacks and mode/word masks, gets the clock, maps registers, requests IRQ, attempts DMA setup, disables hardware, and registers the controller. Each transfer configures divisors/mode, resets counters, and selects DMA when RX DMA exists and length exceeds FIFO depth. PIO primes TX FIFO and enables RX/TX/overrun interrupts. The ISR handles overrun as `-EIO`, otherwise drains RX and fills TX until complete, then disables interrupts and finalizes the transfer. DMA maps page-sized scatter chunks for both directions, uses a zero page when one side has no buffer, starts RX and TX DMA, and finalizes when RX completes.

## State And Persistence
Transfer state lives in `host->cur_msg->state`, `tx`, `rx`, and `fifo_level`. DMA scatter tables are reused between transfers and freed on remove. Hardware is enabled only during prepared transfer hardware. No persistent storage is used.

## Dependencies And Integration Points
Depends on platform resources, clk, IRQ, DMAengine, scatterlists, SPI core, and OF compatible `cirrus,ep9301-spi`. It relies on SPI core transfer finalization and GPIO descriptor chip-select support.

## Risks
PIO FIFO accounting must remain exact to avoid RX overruns. DMA uses `virt_to_page()` over client buffers, so assumptions about buffer mapping are important. The DMA callback finalizes on RX completion and assumes TX completion has also become harmless. Timeout while flushing stale RX FIFO blocks message preparation.

## Test Signals
PIO transfers at 4/8/16 bits, DMA and PIO fallback, TX-only/RX-only dummy-buffer paths, RX overrun injection, divisor boundary rates, DMA probe defer, remove after DMA allocation, and FIFO flush timeout are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ep93xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-falcon.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-falcon.c

## Purpose
Implements the Lantiq Falcon serial flash controller as a half-duplex SPI controller. The hardware is serial-flash oriented, so the driver translates SPI messages into EBU serial flash command/address/dummy/data register operations and maintains chip select across multi-transfer flash sequences.

## Important APIs, Types, And Functions
`struct falcon_sflash` stores cached `sfcmd` state and the SPI host pointer. `falcon_sflash_xfer()` is the state machine for command preparation, write, read, CS disable, and end states. `falcon_sflash_setup()` programs EBU timing and serial-flash bus configuration. `falcon_sflash_xfer_one()` walks an entire SPI message, marks begin/end flags, serializes hardware access with `ebu_lock`, and finalizes the message. Probe registers a devm SPI controller with `SPI_CONTROLLER_HALF_DUPLEX`.

## Control Flow
Setup selects a 100 MHz or 50 MHz EBU clock and derives the serial clock period. Each message starts with `FALCON_SPI_XFER_BEGIN`; the first TX byte becomes the opcode and cached CS command. Up to three following bytes are treated as address, zero bytes as dummy cycles, and remaining TX data as write payload. Read and write data are chunked through 32-bit `SFDATA` accesses with command length fields. The last transfer gets `FALCON_SPI_XFER_END`, which clears keep-CS behavior either on the final data command or an explicit CS-disable command.

## State And Persistence
The only software state is cached `sfcmd` per message. Hardware state includes EBU clock/timing, serial-flash device-size setup, bus read/write configuration, command status, address, and data registers. No persistent storage is used.

## Dependencies And Integration Points
Depends on Lantiq SoC helpers (`ltq_ebu_*`, `ltq_sys1_*`) and the global `ebu_lock`. It integrates with SPI NOR/flash-style clients through standard SPI messages but supports only mode 3 and half-duplex behavior.

## Risks
The parser assumes flash-style message layout: opcode first, up to three address bytes, and zero-valued dummy bytes. Complex SPI devices or unusual flash commands may not map cleanly. Busy polling on `SFSTAT_CMD_PEND` lacks an explicit timeout. Warnings indicate unsupported per-transfer delay and `cs_change`.

## Test Signals
Read JEDEC ID, page program, erase/status commands, multi-byte reads with dummy cycles, 50/100 MHz setup, nonstandard command layouts, command-error handling, and concurrent EBU users are key test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-falcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsi.c

## Purpose
Exposes SPI controllers attached behind an IBM FSI2SPI bridge. The driver discovers child SPI controllers under an FSI engine, checks that the upstream FSI mux is configured for SPI, and implements half-duplex SPI message execution through 64-bit bridge register accesses and a hardware sequencer.

## Important APIs, Types, And Functions
`struct fsi2spi` stores the shared FSI engine and mutex. `struct fsi_spi` stores each SPI controller device, bridge pointer, and base offset. Register access flows through `fsi_spi_read_reg()` and `fsi_spi_write_reg()`, with `fsi_spi_check_status()` validating the FSI2SPI interface. SPI-side helpers include `fsi_spi_reset()`, `fsi_spi_status()`, sequence builders, `fsi_spi_transfer_init()`, `fsi_spi_transfer_data()`, and `fsi_spi_transfer_one_message()`. Probe is `fsi_spi_probe()`.

## Control Flow
Probe first validates the mux via `FSI_MBOX_ROOT_CTRL_8`, allocates one bridge state, then creates one SPI controller for each available child node with a `reg` base. Message execution validates the mux again, then for each transfer requires a TX phase first, builds a sequence selecting slave `cs + 1`, emits shift-out chunks of up to eight bytes, optionally folds the next RX or TX transfer into the same sequence, deselects the slave, writes the sequence register, and moves data through `DATA_TX` or `DATA_RX`. TX waits for TDR not full; RX waits for RDR full.

## State And Persistence
The bridge mutex serializes all register accesses across child controllers. Controller state is the per-child base plus runtime status/reset state in hardware. The driver clears errors by resetting clock/status registers. No persistent storage is used.

## Dependencies And Integration Points
Depends on the FSI subsystem, big-endian FSI register access, OF child nodes, and the SPI core. It registers as an FSI driver for engine ID `0x23` and creates standard SPI controllers with `SPI_CONTROLLER_HALF_DUPLEX`.

## Risks
Transfer shapes are tightly constrained: TX must precede RX, RX is at most 8 bytes, TX chunks are limited, and only simple adjacent transfer folding is supported. Poll loops use 1 second timeouts. Mux misconfiguration returns `-ENOLINK`/`-ENODEV`, and bridge errors trigger reset.

## Test Signals
Mux-disabled probe, multiple child controllers, TX-only commands, TX+RX command/read pairs, timeout paths, bridge status error reset, max transfer size enforcement, and concurrent controller access through the bridge mutex are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-cpm.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-cpm.c

## Purpose
Implements CPM/QE buffer-descriptor mode support for the classic Freescale MPC8xxx SPI driver. It allocates parameter RAM and buffer descriptors, maps dummy and real DMA buffers, starts CPM transfers, services CPM/QE completion interrupts, and releases CPM resources.

## Important APIs, Types, And Functions
Exports `fsl_spi_cpm_reinit_txrx()`, `fsl_spi_cpm_bufs()`, `fsl_spi_cpm_bufs_complete()`, `fsl_spi_cpm_irq()`, `fsl_spi_cpm_init()`, and `fsl_spi_cpm_free()`. Internal helpers include `fsl_spi_cpm_bufs_start()`, `fsl_spi_alloc_dummy_rx()`, `fsl_spi_free_dummy_rx()`, and `fsl_spi_cpm_get_pram()`. State is stored in shared `struct mpc8xxx_spi` from `spi-fsl-lib.h`.

## Control Flow
Initialization only runs when `SPI_CPM_MODE` is set. It allocates a shared dummy RX buffer, resolves QE/CPM subblock and parameter RAM, allocates TX/RX BDs in MURAM, maps zero-page dummy TX and dummy RX DMA buffers, initializes PRAM fields, and returns to the parent driver. For a transfer, `fsl_spi_cpm_bufs()` maps real buffers or selects dummy buffers, does 16-bit TX byte-order conversion when needed, enables RXB interrupt, records `xfer_in_progress`, and starts the first chunk. IRQ handling reads completed length from RX BD, clears events, subtracts from remaining count, restarts if bytes remain, or completes the parent transfer.

## State And Persistence
Runtime state includes PRAM pointer, BD pointers, DMA addresses, map flags, current transfer pointer, count, and globally refcounted dummy RX memory. Hardware state lives in CPM/QE parameter RAM and BDs. No persistent storage is used.

## Dependencies And Integration Points
Depends on CPM1/CPM2 or QE APIs, MURAM allocation, DMA mapping, OF properties, and the classic Freescale SPI register definition. It is called by `spi-fsl-spi.c` when platform data or OF mode selects CPM/QE.

## Risks
Resource unwinding is complex because PRAM, BDs, dummy buffers, and DMA mappings are allocated from different subsystems. Chunking is capped by `PAGE_SIZE`. 16-bit conversion allocates a temporary TX buffer but this source does not visibly free that converted buffer, making ownership worth auditing in context. Bad BD lengths trigger `WARN_ON`.

## Test Signals
CPM1, CPM2, QE fixed/dynamic PRAM, dummy TX/RX transfers, large transfers split over multiple BD starts, DMA map failures, 16-bit word transfers, IRQ completion, and cleanup/refcount behavior are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-cpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-cpm.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-cpm.h

## Purpose
Declares the CPM/QE helper interface used by the classic Freescale SPI driver. It provides real prototypes when Freescale SoC support is enabled and harmless inline stubs otherwise, allowing `spi-fsl-spi.c` to compile across configurations.

## Important APIs, Types, And Functions
The header exposes `fsl_spi_cpm_reinit_txrx()`, `fsl_spi_cpm_bufs()`, `fsl_spi_cpm_bufs_complete()`, `fsl_spi_cpm_irq()`, `fsl_spi_cpm_init()`, and `fsl_spi_cpm_free()`. All functions operate on `struct mpc8xxx_spi`, and transfer execution accepts `struct spi_transfer`.

## Control Flow
There is no runtime control flow in the header. With `CONFIG_FSL_SOC`, calls bind to exported functions from `spi-fsl-cpm.c`. Without it, reinit/complete/irq/free become no-ops, init returns success, and buffer submission returns success.

## State And Persistence
The header owns no state. It defines the compile-time availability of CPM behavior for the parent driver.

## Dependencies And Integration Points
Includes `spi-fsl-lib.h` for `struct mpc8xxx_spi`. It is included by `spi-fsl-spi.c` and `spi-fsl-cpm.c`, bridging generic Freescale SPI code to optional CPM/QE support.

## Risks
The non-FSL stubs return success for buffer submission/init, so callers must only route real CPM transfers here when CPM mode is valid for the build/platform. Mismatch between flags and configuration could otherwise hide missing hardware support until transfer behavior is wrong.

## Test Signals
Build coverage with `CONFIG_FSL_SOC` on and off, CPM mode probe paths, and ensuring CPU-mode transfers do not accidentally depend on CPM symbols are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-cpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-dspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-dspi.c

## Purpose
Implements the Freescale/NXP DSPI controller driver for multiple SoCs, supporting host and target mode, XSPI FIFO command mode, DMA mode, GPIO/native chip selects, per-device timing setup, optional polling, PM suspend/resume, and S32G-specific behavior.

## Important APIs, Types, And Functions
Core state is `struct fsl_dspi`; per-device timing is `struct chip_data`; DMA state is `struct fsl_dspi_dma`; hardware variants are described by `struct fsl_dspi_devtype_data`. Important functions include data conversion helpers, `dspi_setup_accel()`, `dspi_fifo_write()`, `dspi_rxtx()`, `dspi_interrupt()`, `dspi_dma_xfer()`, `dspi_request_dma()`, `dspi_transfer_one_message()`, `dspi_setup()`, `dspi_init()`, `dspi_target_abort()`, `dspi_probe()`, and `dspi_remove()`.

## Control Flow
Probe selects host or target allocation, reads platform data or OF match data, configures endian-specific PUSHR offsets, initializes regmaps, clocks, MCR/RSER state, IRQ or poll mode, optional DMA, speed limits, and registers the controller. Setup computes CTAR timing from clock rate, requested speed, CS setup/hold delays, mode bits, LSB-first, and optional S32G modified transfer format. Message transfer clears FIFOs/status, builds a PUSHR command including PCS/CONT semantics, then runs either DMA chunks or XSPI FIFO writes. IRQ or polling reads previous FIFO data, checks FIFO errors, writes more data, and completes when all words are transferred.

## State And Persistence
Runtime state includes current message/transfer/chip, TX/RX pointers, remaining length, progress, words in flight, command word, MTF flag, completion, DMA buffers, regmaps, and clock. Per-SPI-device `chip_data` caches CTAR value. Hardware is halted after messages unless `cs_change` keeps CS asserted. No persistent storage is used.

## Dependencies And Integration Points
Depends on platform/OF, regmap, DMAengine, clk, pinctrl PM, GPIO descriptors, SPI core, and `linux/spi/spi-fsl-dspi.h` platform data. Compatible data covers VF610, Layerscape families, LX2160A, ColdFire, and S32G.

## Risks
The driver has many variant paths: XSPI vs DMA, host vs target, IRQ vs polling, big vs little endian, and S32G MTF. FIFO error handling protects TX underflow/RX overflow, but command continuation and GPIO CS semantics are subtle. DMA timeouts and target abort must terminate both channels. Speed/timing calculations clamp through table searches and can silently pick maximum prescalers.

## Test Signals
Variant probe matrix, host/target transfers, DMA timeout/abort, XSPI 8-on-16/8-on-32/16-on-32 acceleration, GPIO and native CS with `cs_change`, polling mode, FIFO errors, suspend/resume reinitialization, and S32G >25 MHz MTF are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-dspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-espi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-espi.c

## Purpose
Implements the Freescale enhanced SPI controller driver. It aggregates each SPI message into one hardware transaction, drives TX/RX FIFOs with interrupts, supports dual-output reads through RXSKIP mode, manages per-CS mode registers, and uses runtime PM autosuspend.

## Important APIs, Types, And Functions
`struct fsl_espi` stores device/MMIO state, current message transfer list, TX/RX transfer pointers and positions, completion, swab mode, RXSKIP count, lock, and input clock. Per-device CS state is `struct fsl_espi_cs`. Important functions include `fsl_espi_check_message()`, `fsl_espi_check_rxskip_mode()`, FIFO fill/read helpers, `fsl_espi_setup_transfer()`, `fsl_espi_bufs()`, `fsl_espi_trans()`, `fsl_espi_do_one_msg()`, `fsl_espi_setup()`, `fsl_espi_irq()`, runtime PM callbacks, `fsl_espi_init_regs()`, and `fsl_espi_probe()`.

## Control Flow
Probe gets chip-select count from OF, maps registers, requests IRQ, initializes mode/CS registers from child node properties, enables runtime PM, and registers the controller. A message is validated for maximum length and uniform speed/word size. The driver builds a synthetic transfer with total frame length, maximum delay, and RX bus width, configures CS mode, writes `SPCOM` with chip select, transfer length, optional RXSKIP and dual-output bits, enables interrupts, fills TX FIFO under spinlock, and waits up to two seconds. The ISR reads events/mask, drains RX, refills TX, checks final DON and FIFO counts, clears events, and completes.

## State And Persistence
Per-message state is maintained in TX/RX positions and done flags. Per-device `fsl_espi_cs` caches mode register fields. Runtime PM disables/enables `SPMODE_ENABLE`. Hardware CS registers are reinitialized on resume. No persistent storage is used.

## Dependencies And Integration Points
Depends on Freescale system frequency (`fsl_get_sys_freq()`), OF address/IRQ parsing, runtime PM, SPI core, and compatible `fsl,mpc8536-espi`. It uses SPI core auto runtime PM and max-message-size callbacks.

## Risks
All transfers in a message must share bits-per-word and speed; unsupported mixed messages fail. RXSKIP dual-output mode only supports a write followed by a read and requires the command phase to fit the FIFO. Timeout is fixed at two seconds. FIFO final-state checks log errors but completion has already occurred.

## Test Signals
Uniform and mixed message validation, max transaction length, RXSKIP dual-output flash reads, LSB-first 16-bit byte swapping, runtime suspend/resume, per-CS DT timing fields, FIFO threshold IRQ behavior, and transfer timeout are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-espi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lib.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lib.c

## Purpose
Provides shared helper code for the classic Freescale SPI/eSPI family, especially buffer accessor functions, platform-data conversion, mode-name formatting, and common probe initialization for `struct mpc8xxx_spi`.

## Important APIs, Types, And Functions
Macro-generated exports implement `mpc8xxx_spi_rx_buf_u8/u16/u32()` and `mpc8xxx_spi_tx_buf_u8/u16/u32()`. Other exports are `to_of_pinfo()`, `mpc8xxx_spi_strmode()`, `mpc8xxx_spi_probe()`, and `of_mpc8xxx_spi_probe()`.

## Control Flow
The generated TX helpers read one typed value from the current TX pointer, shift it by `tx_shift`, advance the pointer, and return zero for dummy TX. RX helpers shift incoming register data by `rx_shift`, store one typed value, and advance RX. `mpc8xxx_spi_probe()` initializes controller mode bits, private buffer functions, flags, input clock, IRQ, shifts, bus number, chip-select count, and completion. `of_mpc8xxx_spi_probe()` allocates OF-backed platform data, determines bus number and clock, and sets mode flags from `mode` or compatible strings.

## State And Persistence
State lives in `struct mpc8xxx_spi` and platform data attached to the device. Buffer pointers are advanced during transfers; completion is initialized once. No persistent state is stored.

## Dependencies And Integration Points
Depends on SPI core, platform devices, OF, Freescale platform data, and optionally `get_brgfreq()`/`fsl_get_sys_freq()` under `CONFIG_FSL_SOC`. It is used by `spi-fsl-spi.c` and CPM helpers.

## Risks
The typed buffer helpers assume alignment and word-size choices made by the parent driver. OF mode parsing maps textual modes to flags and must stay synchronized with CPM/QE backend support. If clock discovery fails, probe returns `-ENODEV` or property errors.

## Test Signals
Accessor behavior for 8/16/32-bit buffers and shifts, dummy TX, OF mode parsing for CPU/QE/CPM, clock fallback paths, and initialization of controller limits are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lib.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lib.h

## Purpose
Defines the shared private structures and function prototypes for the classic Freescale SPI/eSPI drivers. It is the contract between common helper code, CPM support, and `spi-fsl-spi.c`.

## Important APIs, Types, And Functions
`struct mpc8xxx_spi` stores controller-private state including device, MMIO base, TX/RX pointers, CPM/QE PRAM and BDs, current transfer, DMA addresses and map flags, dummy DMA buffers, typed buffer callbacks, remaining count, IRQ, timing, input clock, shifts, mode flags, optional native chip-select metadata, and completion. `struct spi_mpc8xxx_cs` stores per-device buffer callbacks, shifts, and cached hardware mode. `struct mpc8xxx_spi_probe_info` wraps platform data and optional IMMR SPI CS mapping. It also defines big-endian register read/write helpers and prototypes for shared exports.

## Control Flow
The header has no independent runtime flow. Its inline `mpc8xxx_spi_write_reg()` and `mpc8xxx_spi_read_reg()` enforce big-endian MMIO access for classic Freescale registers.

## State And Persistence
It declares all runtime state used by the classic Freescale SPI path. The state is volatile and owned by the SPI controller/device lifecycle.

## Dependencies And Integration Points
Includes `asm/io.h` and uses `struct fsl_spi_platform_data` from Freescale platform headers through included compilation context. Included by `spi-fsl-lib.c`, `spi-fsl-cpm.c`, `spi-fsl-cpm.h`, and `spi-fsl-spi.c`.

## Risks
This header is a private ABI shared by several files. Structure-field changes can break CPM and CPU transfer paths. Conditional fields under `CONFIG_SPI_FSL_SPI` mean build coverage across configurations is important.

## Test Signals
Build tests for all relevant Kconfig combinations, big-endian register access, per-CS state allocation/cleanup, and CPU vs CPM transfer paths are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lpspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lpspi.c

## Purpose
Implements the Freescale/NXP LPSPI controller driver for i.MX7ULP, i.MX93, and S32G-like variants. It supports host and target mode, PIO and DMA transfers, runtime PM clock gating, optional hardware-derived chip-select count, and erratum-specific prescale limits.

## Important APIs, Types, And Functions
Variant data is `struct fsl_lpspi_devtype_data`; per-transfer configuration is `struct lpspi_config`; runtime state is `struct fsl_lpspi_data`. Important functions include typed TX/RX buffer helpers, `fsl_lpspi_can_dma()`, hardware prepare/unprepare PM hooks, FIFO read/write helpers, `fsl_lpspi_set_cmd()`, `fsl_lpspi_set_bitrate()`, `fsl_lpspi_config()`, `fsl_lpspi_prepare_message()`, `fsl_lpspi_transfer_one()`, DMA helpers, ISR `fsl_lpspi_isr()`, PM callbacks, probe, and remove.

## Control Flow
Probe allocates host or target controller, maps MMIO, requests IRQ with `IRQF_NO_AUTOEN`, obtains `per` and `ipg` clocks, enables runtime PM, reads FIFO sizes and chip-select count, registers callbacks, attempts DMA setup, enables IRQ for PIO fallback, and registers the controller. Message preparation configures the first transfer, chooses DMA eligibility, writes command/FIFO/status setup, and clears FIFOs. Each transfer recalculates config, writes TCR, and runs DMA or PIO. PIO fills TX FIFO, services interrupts until frame complete, then resets. DMA configures slave channels, submits RX then TX SG descriptors, waits for completions or target abort, and resets.

## State And Persistence
Runtime state includes clock handles, MMIO base/physical address, target flags, buffer pointers, typed accessors, remaining bytes, FIFO sizes/watermark, current config, completions, DMA usage and completions, and abort flag. No persistent storage is used.

## Dependencies And Integration Points
Depends on platform/OF, clk, DMAengine, runtime PM, pinctrl PM, IRQ, SPI core, and optional target-mode SPI core APIs. Compatible data covers `fsl,imx7ulp-spi`, `fsl,imx93-spi`, and `nxp,s32g2-lpspi`.

## Risks
`fsl_lpspi_set_bitrate()` computes `effective_speed_hz` with multiplication/division ordering that should be validated for intended units. DMA completion waits depend on calculated timeout and transfer speed. Target abort must wake both PIO and DMA waiters. IRQ is requested disabled and only explicitly enabled on DMA setup failure, so DMA-capable configurations rely on DMA rather than PIO IRQs.

## Test Signals
PIO fallback, DMA SG transfers for 1/2/4-byte words, host and target abort, runtime PM clock transitions, i.MX93 prescale limit, CS1-only selection, FIFO size discovery, timeout/reset behavior, and suspend/resume are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lpspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-qspi.c

## Purpose
Implements a Freescale/NXP QuadSPI controller using the SPI MEM API. It programs a single reusable LUT entry per operation, supports per-operation clock frequency, uses IP commands for small operations, uses AHB memory mapping for larger reads, and handles multiple SoC-specific quirks.

## Important APIs, Types, And Functions
`struct fsl_qspi_devtype_data` captures FIFO sizes, AHB buffer size, invalid master ID, address-window size, quirks, and register endianness. `struct fsl_qspi` stores MMIO/AHB mappings, clocks, reset, lock, completion, PM QoS request, selected CS, and memory-map base. SPI MEM callbacks are `fsl_qspi_adjust_op_size()`, `fsl_qspi_supports_op()`, `fsl_qspi_exec_op()`, and `fsl_qspi_get_name()`. Other key functions include `fsl_qspi_prepare_lut()`, `fsl_qspi_select_mem()`, `fsl_qspi_fill_txfifo()`, `fsl_qspi_read_rxfifo()`, `fsl_qspi_do_op()`, `fsl_qspi_default_setup()`, and probe/cleanup helpers.

## Control Flow
Probe allocates a SPI host, maps controller and AHB memory resources, obtains reset and clocks, enables clocks, deasserts reset, requests IRQ, sets four chip selects, installs SPI MEM ops/caps, performs default hardware setup, and registers the controller. `exec_op()` serializes with a mutex, waits for IP/AHB idle, selects chip and rate, programs SFAR, clears FIFOs/pointers, invalidates AHB buffer ownership, programs the LUT for command/address/dummy/data, then either copies large reads from AHB mapping or fills TX FIFO and launches an IP command. The IRQ completes transfer-finished events.

## State And Persistence
The selected chip index, LUT contents, clock rate, AHB buffer configuration, and reset state are runtime hardware/software state. The driver invalidates AHB buffers after operations to avoid stale reads. No persistent storage is used.

## Dependencies And Integration Points
Depends on SPI MEM, clk, reset, platform named resources `QuadSPI` and `QuadSPI-memory`, IRQ completion, mutex locking, PM QoS for wait-mode erratum, and OF compatible data for Vybrid, i.MX6/7, Layerscape, and Spacemit K1 variants.

## Risks
LUT construction is limited to operations fitting a single LUT entry and dummy cycles <=64. Read sizes have alignment constraints around RX FIFO vs AHB path. Quirk handling controls endian swapping, 4x clocks, minimum TX FIFO fill, AMBA base offsets, TDH clearing, and clock-disable behavior; wrong variant data can corrupt operations. `fsl_qspi_select_mem()` returns void, so clock-rate failures are not propagated to `exec_op()`.

## Test Signals
SPI NOR probe/read/write/erase across bus widths, large AHB reads, unaligned near-FIFO-size reads, TX FIFO fill erratum, endian variants, per-op frequency switching, suspend/resume default setup, timeout on missing IRQ, and multi-CS naming/selection should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-spi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-spi.c

## Purpose
Implements the classic Freescale MPC8xxx SPI controller driver with CPU, QE CPU, CPM/QE buffer-descriptor, GRLIB, OF, and optional legacy platform support. It configures per-device modes and clock divisors, transfers data synchronously through IRQ/completion, delegates CPM mode to `spi-fsl-cpm.c`, and manages native/GPIO chip selects.

## Important APIs, Types, And Functions
Important functions include `fsl_spi_change_mode()`, shift setup helpers, `mspi_apply_cpu_mode_quirks()`, `fsl_spi_setup_transfer()`, `fsl_spi_cpu_bufs()`, `fsl_spi_bufs()`, `fsl_spi_prepare_message()`, `fsl_spi_transfer_one()`, `fsl_spi_setup()`, `fsl_spi_irq()`, GRLIB CS/probe helpers, `fsl_spi_probe()`, `of_fsl_spi_probe()`, remove paths, and module init/exit.

## Control Flow
Probe obtains OF/platform data, maps chip-select boot override if requested, determines chip-select count, allocates a host, initializes shared `mpc8xxx_spi` state, sets callbacks, initializes CPM if needed, maps registers, configures GRLIB capabilities when applicable, requests IRQ, initializes mode/mask/command/event registers, enables the controller, and registers it. Message preparation enforces no speed changes inside a message, opportunistically widens CPU-mode byte transfers to 16/32 bits, and adjusts CPM word sizes/endian constraints. Each transfer sets mode/divisors, starts CPU or CPM transfer, waits on completion, disables interrupts, and completes.

## State And Persistence
Per-device `spi_mpc8xxx_cs` caches hardware mode, buffer callbacks, and shifts. Controller state includes current buffers, count, flags, completion, CPM resources, shifts, and native CS metadata. Hardware mode is temporarily disabled/re-enabled for mode changes. No persistent storage is used.

## Dependencies And Integration Points
Depends on `spi-fsl-lib`, optional `spi-fsl-cpm`, `spi-fsl-spi.h` registers, SPI bitbang-era platform data, OF/GPIO/IRQ/address helpers, Freescale SoC clock/IMMR helpers, and optional GRLIB compatible data.

## Risks
Mode changes can glitch SPI clock, so preparation rejects intra-message speed changes and changes mode before CS assertion. CPM endian limitations reject some LSB-first word sizes. CPU IRQ waits spin on not-full events. Legacy and OF paths share probe/remove but resource cleanup for boot CS mapping is only in some failure paths, worth auditing.

## Test Signals
CPU and CPM transfers, mode/clock divisor boundaries, large-transfer word widening, LSB-first rejection in CPM, GRLIB native CS, GPIO CS and `fsl,spisel_boot`, IRQ completion, legacy platform probe, and remove cleanup are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-spi.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-spi.h

## Purpose
Defines the classic Freescale SPI controller register layout and bitfields used by `spi-fsl-spi.c` and CPM helpers. It covers mode, event, mask, command, TX/RX data, and GRLIB-specific capability/native chip-select registers.

## Important APIs, Types, And Functions
`struct fsl_spi_reg` describes the register block: `cap`, `mode`, `event`, `mask`, `command`, `transmit`, `receive`, and `slvsel`. Bitfields include `SPMODE_*` for loop, clock polarity/phase, divider, bit order, master/enable, word length, prescaler, and QE CPU operation; `SPCAP_*` for GRLIB capabilities; default `SPMODE_INIT_VAL`; and event/mask bits `SPIE_NE/NF` and `SPIM_NE/NF`.

## Control Flow
The header has no runtime control flow. Its constants drive mode construction, interrupt masking, event handling, and GRLIB capability interpretation in the implementation.

## State And Persistence
No state is owned by the header. It defines the shape of MMIO state used by the controller hardware.

## Dependencies And Integration Points
Used by `spi-fsl-spi.c` for register access and by `spi-fsl-cpm.c` to start CPM transfers through the command register. It relies on big-endian register access wrappers from `spi-fsl-lib.h`.

## Risks
Incorrect bit definitions would directly corrupt controller mode, interrupt, or chip-select behavior. GRLIB fields share the same register block but are variant-specific, so code must only interpret them on matching hardware.

## Test Signals
Register layout compile coverage, mode bit programming for CPOL/CPHA/LSB/loop/word length, interrupt mask/event handling, and GRLIB capability/native CS parsing are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-spi.h -->
