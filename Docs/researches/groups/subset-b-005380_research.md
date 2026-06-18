# subset-b-005380 Research

Grouped research for SPI controller and bitbang support files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-axiado.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-axiado.c

## Purpose
Implements the Axiado AX3000 SPI host controller driver, including standard SPI transfers and a `spi-mem` fast path for serial memory reads/writes. It is a platform driver for `axiado,ax3000-spi` that maps the controller registers, enables the APB/reference clocks, registers an SPI controller, and manages suspend/runtime PM.

## Important APIs, Types, And Functions
The driver-private state is `struct ax_spi` from `spi-axiado.h`. Local register helpers `ax_spi_read()`, `ax_spi_write()`, and `ax_spi_write_b()` hide relaxed MMIO access. Hardware configuration is centered on `ax_spi_init_hw()`, `ax_spi_detect_fifo_depth()`, `ax_prepare_message()`, `ax_prepare_transfer_hardware()`, and `ax_unprepare_transfer_hardware()`. SPI-core integration uses `ax_transfer_one()` plus the IRQ handler `ax_spi_irq()`. SPI memory integration is exposed through `ax_spi_mem_ops`, with `ax_spi_mem_exec_op()` executing operations and `ax_spi_mem_adjust_op_size()` limiting payload size by FIFO overhead and `SZ_64K`.

## Control Flow
Probe allocates a host with `devm_spi_alloc_host()`, maps registers, enables `pclk` and `ref` clocks, enables runtime PM autosuspend, reads `num-cs`, detects the FIFO depth, initializes the hardware, requests the IRQ, fills SPI controller callbacks, and registers the controller. A normal SPI transfer clears stale RX FIFO data and interrupt flags, stores TX/RX pointers and remaining byte counters, configures clock defaults, fills the TX FIFO, sets host transmit enable, then enables message-complete and RX-threshold interrupts. The IRQ path handles transfer-complete first, then RX FIFO threshold events; received bytes are unpacked from 32-bit FIFO words into byte streams until copied or discarded bytes reach zero, then interrupts are disabled and `spi_finalize_current_transfer()` is called. The `spi-mem` path bypasses the async IRQ flow: it initializes hardware, asserts chip select, writes opcode/address/dummy/data into TX FIFO, starts transmission, polls FIFO status, unpacks RX data when needed, and deasserts chip select.

## State And Persistence
Transfer state is held in `xspi->tx_buf`, `rx_buf`, `tx_bytes`, `rx_bytes`, `rx_discard`, and `rx_copy_remaining`. Because the RX FIFO is 32-bit while SPI buffers are byte-addressed, the driver keeps separate buffered-word state for IRQ transfers and `spi-mem` operations: `current_rx_fifo_word`, `bytes_left_in_current_rx_word`, `current_rx_fifo_word_for_irq`, and `bytes_left_in_current_rx_word_for_irq`. Persistent device state includes clock handles, MMIO base, detected FIFO depth, cached `clk_rate`, and current `speed_hz`. Runtime PM autosuspend disables and reenables clocks through runtime suspend/resume. System resume reinitializes controller registers.

## Dependencies And Integration Points
The file depends on the Linux SPI core, `spi-mem`, platform-device resources, device tree, interrupts, clocks, and runtime PM. It uses constants and the private data definition from `spi-axiado.h`. The controller advertises `SPI_CPOL`, `SPI_CPHA`, `SPI_CS_HIGH`, 8-bit words, GPIO descriptors, and `mem_ops`. Device-tree integration is through `axiado,ax3000-spi`, named clocks `pclk` and `ref`, an IRQ, an MMIO resource, and optional `num-cs`.

## Risks And Edge Cases
Clock-frequency handling is currently effectively fixed: `ax_spi_config_clock_freq()` writes the default divider rather than deriving a divider from `transfer->speed_hz`, so reported max speed may not match actual transfer speed. `ax_spi_config_clock_mode()` computes CPOL/CPHA bits but then writes `0x03` unconditionally, which can override the requested mode and deserves hardware validation. `ax_spi_chipselect()` ignores its `is_high` argument and only programs the target-select bits, so GPIO/core chip-select behavior needs careful testing. The `spi-mem` path writes the entire command/data sequence into FIFO and relies on `adjust_op_size()` to prevent overflow; mistakes in FIFO depth or overhead accounting can truncate memory operations. RX FIFO drains are bounded, which avoids infinite loops but can leave stale data if the controller reports a stuck count.

## Test Signals
Useful tests are loopback or analyzer-backed SPI mode tests for CPOL/CPHA, TX-only/RX-only/full-duplex transfers that cross FIFO thresholds, long transfers that require repeated IRQ refill, and `spi-mem` reads with opcode/address/dummy combinations near FIFO capacity. Runtime PM tests should exercise autosuspend, system suspend/resume, and remove paths while checking clocks and register reinitialization. Error signals include `RX FIFO drain timeout before transfer`, `-ETIMEDOUT` from `spi-mem`, missing transfer finalization, and data shifted by stale buffered RX words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-axiado.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-axiado.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-axiado.h

## Purpose
Defines the Axiado SPI host controller register map, bit fields, fixed limits, default values, and private driver state consumed by `spi-axiado.c`. It is not a public subsystem API; it is the hardware contract for the Axiado SPI driver.

## Important APIs, Types, And Functions
The central type is `struct ax_spi`, containing MMIO base, clock handles, cached speeds, transfer buffer pointers, byte counters, FIFO depth, RX word-unpacking state, and RX copy/discard counters. Register offsets cover control registers `AX_SPI_CR1` through `AX_SPI_CR3`, FIFO count registers, clock divider register `AX_SPI_SCDR`, interrupt mask/status/vector registers, and TX/RX FIFO addresses. Bit definitions include controller enable/reset, CPHA/CPOL, read/write enable, read-ignore, host transmit enable, interrupt bits, FIFO threshold values, target-select values, and limits such as `AX_SPI_COMMAND_BUFFER_SIZE`, `AX_SPI_RX_FIFO_DRAIN_LIMIT`, and `AX_SPI_TRX_FIFO_TIMEOUT`.

## Control Flow
This header has no executable control flow, but it shapes driver flow by naming which register bits are written during initialization, transfer setup, interrupt handling, FIFO draining, and `spi-mem` operation sizing. The interrupt constants map directly to the ISR/IMR/IVR logic in `spi-axiado.c`; FIFO and timeout constants bound polling and drain loops.

## State And Persistence
`struct ax_spi` is allocated as SPI controller private data and persists for the lifetime of the platform device. The header distinguishes persistent hardware resources (`regs`, `ref_clk`, `pclk`, `clk_rate`, `tx_fifo_depth`) from per-transfer mutable state (`tx_buf`, `rx_buf`, byte counters, RX staging words). Separate RX staging fields exist for interrupt-driven and polled `spi-mem` contexts.

## Dependencies And Integration Points
The header assumes Linux kernel integer types, `__iomem`, and `struct clk` declarations included by the C file. Its values integrate tightly with Axiado Digital Blocks SPI IP, the Linux SPI controller callbacks, and SPI memory operations.

## Risks And Edge Cases
Several constants are fixed policy rather than discovered hardware state: `FIFO_DEPTH` is hard-coded to 256, threshold values are fixed, and divider min/default/max naming is potentially confusing. If silicon revisions differ, these definitions can silently misconfigure transfers. The target-select values and mask only cover four chip selects. The drain limit of 24 32-bit FIFO reads may be insufficient if stale FIFO state exceeds that amount.

## Test Signals
Header-level validation is indirect: successful driver probe, correct FIFO thresholds, correct interrupt bit clearing, and expected transfer behavior across all supported chip selects indicate that the register definitions match hardware. Static review should verify each field in `struct ax_spi` remains synchronized with the C driver’s documented usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-axiado.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm-qspi.c

## Purpose
Implements the common Broadcom QSPI controller core for BRCMSTB, NSP, NS2, Cygnus, and related SoCs. It supports MSPI register-driven transfers for generic SPI messages and optional BSPI/RAF accelerated read mode for aligned SPI NOR memory reads. SoC wrapper drivers call the exported `bcm_qspi_probe()` and `bcm_qspi_remove()` functions, optionally passing a SoC-specific interrupt controller adapter.

## Important APIs, Types, And Functions
Key state lives in `struct bcm_qspi`, which tracks platform resources, MMIO bases for MSPI/BSPI/chip-select blocks, clocking, interrupt wiring, transfer position, current chip select, BSPI read state, transfer-mode cache, completions, revision data, and endian mode. `struct bcm_qspi_soc_intc` is defined in `spi-bcm-qspi.h` and lets wrappers acknowledge, mask, and read muxed interrupt status. MSPI transfer helpers include `bcm_qspi_hw_set_parms()`, `write_to_hw()`, `read_from_hw()`, `bcm_qspi_transfer_one()`, and slot readers/writers for 8/16/32/64-bit words. BSPI helpers include `bcm_qspi_bspi_set_mode()`, `bcm_qspi_bspi_exec_mem_op()`, `bcm_qspi_bspi_lr_data_read()`, and enable/disable/flush helpers. SPI memory support is exposed via `bcm_qspi_mem_ops` and `bcm_qspi_exec_mem_op()`.

## Control Flow
Probe validates device tree compatibility, allocates the SPI controller, maps MSPI and optional BSPI/chip-select resources, configures optional clocks, identifies controller revisions, disables stale hardware state, requests either named L2 IRQs or a muxed L1 IRQ, initializes MSPI/BSPI, and registers the SPI host. Generic SPI transfers run through `bcm_qspi_transfer_one()`: the driver selects chip select when GPIO CS is absent, tracks current byte offset, writes up to `MSPI_NUM_CDRAM` slots to TXRAM/CDRAM, starts MSPI, waits for `mspi_done`, then reads RXRAM back and repeats until the transfer length is consumed. SPI memory reads are accepted only for address-bearing data-in operations; unsupported, unaligned, short, SFDP, or BSPI-v3 4 MB boundary-crossing reads fall back to MSPI. Otherwise the driver configures BSPI flex/override mode, starts RAF chunks of up to 256 bytes, harvests data in the BSPI IRQ path, and waits for `bspi_done`.

## State And Persistence
Persistent state includes mapped bases, optional clock, `base_clk`, cached `max_speed_hz`, endian selection, revision flags, interrupt descriptors, completions, and BSPI/MSPI availability. Per-device setup allocates `struct bcm_qspi_parms` via `spi_set_ctldata()` and caches mode/speed/bits per word. Per-transfer state is held in `qspi->trans_pos`. BSPI read state is held in `bspi_rf_op`, index, length, and status while a RAF session is active. Suspend stores BSPI strap override state for newer BSPI revisions, suspends the SPI controller, disables the clock, and uninitializes hardware; resume reinitializes hardware, restores chip select, re-enables SoC interrupts, reenables the clock, and resumes the SPI controller.

## Dependencies And Integration Points
The driver depends on Linux SPI, `spi-mem`, SPI NOR opcode definitions, platform resources named `hif_mspi` or `mspi`, optional `bspi` and `cs_reg`, optional clock, device-tree compatible data, IRQs, completions, and common helpers from `spi-bcm-qspi.h`. It exports probe/remove/PM symbols for wrapper drivers such as `spi-brcmstb-qspi.c`. It supports big-endian MMIO through the header accessors and integrates with optional SoC interrupt controllers for muxed interrupt status.

## Risks And Edge Cases
The driver has two very different execution engines sharing chip-select and clock state; switching between BSPI and MSPI requires correct write-locking and prefetch flushing. BSPI v3 address remapping and the 4 MB boundary fallback are easy to regress. The BSPI data path assumes 32-bit alignment for the fast path but handles tails bytewise; incorrect `bspi_rf_op_idx` use could corrupt unaligned buffers. MSPI slot code must preserve `cs_change`, delay, 3-wire, and 8/16/32/64-bit packing semantics. Timeout paths return `-ETIMEDOUT`, but hardware state must still be left usable for later transfers. `bcm_qspi_probe()` allocates `dev_ids` with `kzalloc_objs()` and frees it in remove/error paths, so leak detection around probe failures matters.

## Test Signals
Important tests include generic SPI transfers for 8/16/32/64-bit words, 3-wire mode, GPIO and native chip selects, delays and `cs_change`, BSPI-aligned NOR reads, unaligned/short/SFDP fallback to MSPI, BSPI v3 boundary-crossing reads, big-endian register access, muxed and separate interrupt configurations, suspend/resume, and clock-rate changes. Useful log signals include timeouts waiting for MSPI or BSPI, invalid BSPI mode warnings, and missing IRQ registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm-qspi.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm-qspi.h

## Purpose
Declares the shared interface and interrupt definitions used by the Broadcom QSPI common driver and its SoC-specific wrappers. It provides interrupt mask constants, the SoC interrupt-controller callback structure, endian-aware MMIO helpers, and exported common probe/remove/PM declarations.

## Important APIs, Types, And Functions
`struct bcm_qspi_soc_intc` is the wrapper-facing adapter for SoC interrupt integration, with callbacks to acknowledge interrupt groups, enable/disable groups, and read muxed status. Interrupt group constants identify `MSPI_DONE`, `BSPI_DONE`, `BSPI_ERR`, and combined `MSPI_BSPI_DONE`. `get_qspi_mask()` maps those logical groups to hardware interrupt masks. `bcm_qspi_readl()` and `bcm_qspi_writel()` choose big-endian or relaxed little-endian access. The file declares `bcm_qspi_probe()`, `bcm_qspi_remove()`, and `bcm_qspi_pm_ops`.

## Control Flow
The header has no independent runtime flow. It supports flow in `spi-bcm-qspi.c` by letting wrapper drivers pass a `bcm_qspi_soc_intc`, allowing the common L1 ISR to read SoC status, dispatch to MSPI/BSPI handlers, acknowledge events, and mask/unmask BSPI completion/error sources.

## State And Persistence
The header defines no storage except callback contracts. Persistent state is supplied by wrapper-specific implementations of `struct bcm_qspi_soc_intc` and by the common driver’s `struct bcm_qspi`, which stores the pointer passed to `bcm_qspi_probe()`.

## Dependencies And Integration Points
It depends on Linux `types.h` and `io.h`, plus forward declarations for `platform_device` and `dev_pm_ops`. It is included by the common QSPI core and wrappers such as `spi-brcmstb-qspi.c`. The endian helpers integrate with device-tree `big-endian` selection in the common driver.

## Risks And Edge Cases
Incorrect interrupt mask mapping can cause lost completions or unhandled BSPI errors. Wrappers passing a partially implemented `bcm_qspi_soc_intc` can make muxed IRQ handling fail at runtime. Endian access helpers centralize byte order, so any future register that requires different access width or ordering should not blindly use these helpers.

## Test Signals
Validation comes from wrapper probe success, correct interrupt dispatch in both muxed and non-muxed IRQ modes, BSPI error handling, and big-endian platform smoke tests. Static checks should confirm every logical interrupt group used by wrappers is represented in `get_qspi_mask()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm-qspi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm2835.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm2835.c

## Purpose
Implements the primary Broadcom BCM2835 SPI controller driver used on Raspberry Pi-class SoCs. It supports polling, interrupt, and DMA transfer modes, software/GPIO chip select handling, debugfs counters, runtime setup per SPI device, and platform registration for `brcm,bcm2835-spi`.

## Important APIs, Types, And Functions
`struct bcm2835_spi` holds controller resources, transfer pointers/counters, DMA prologue bookkeeping, debugfs counters, current target state, DMA activity flags, and reusable DMA descriptors. `struct bcm2835_spidev` holds per-device precomputed CS register values plus a reusable RX-DMA descriptor used to clear RX FIFO during TX-only DMA transfers. Transfer helpers include FIFO byte and 32-bit count routines, `bcm2835_spi_reset_hw()`, IRQ handler `bcm2835_spi_interrupt()`, polling/IRQ/DMA transfer functions, DMA callbacks, DMA setup/release, `bcm2835_spi_setup()`, and `bcm2835_spi_prepare_message()`.

## Control Flow
Probe allocates a host, configures SPI core callbacks and limits, maps registers, enables the core clock, initializes optional DMA, clears FIFOs, requests a shared IRQ, registers the controller, and creates debugfs counters. For each device, setup allocates per-target state, prepares reusable DMA descriptors when DMA is available, precomputes CS register values, and handles native-CS-to-GPIO fallback for legacy device-tree users. During a transfer, the driver computes the clock divider, sets 3-wire receive mode if needed, stores TX/RX pointers and lengths, then chooses polling for short transfers, DMA for large DMA-capable transfers, or IRQ otherwise. Polling loops fill/read FIFOs until complete or falls back to IRQ after a module-parameter-controlled time limit. IRQ mode fills TX FIFO, enables interrupts, drains RX FIFO on RX threshold/full events, refills TX on DONE, and finalizes when all RX bytes arrive. DMA mode may transmit a CPU prologue to align sglist entries, starts TX DMA early, starts RX DMA late, and finalizes in RX or TX callbacks depending on transfer direction.

## State And Persistence
Persistent state includes MMIO base, clock handle/rate, IRQ, debugfs counters, DMA channels/descriptors, and per-device CS/DMA state. Mutable transfer state includes `tx_buf`, `rx_buf`, `tx_len`, `rx_len`, active `tfr`, prologue byte counts, spillover flag, current target pointer, and DMA active flags. The driver mutates mapped scatterlist DMA addresses/lengths during the DMA prologue and restores them with `bcm2835_spi_undo_prologue()` before completion/error handling. Debugfs counters persist until driver removal and provide runtime mode-use observability.

## Dependencies And Integration Points
The driver depends on Linux SPI, DMAengine, DMA mapping, OF address lookup, GPIO descriptors and lookup tables, debugfs, interrupts, clocks, and platform resources. It advertises `SPI_CPOL`, `SPI_CPHA`, `SPI_CS_HIGH`, `SPI_NO_CS`, and `SPI_3WIRE`, and only supports 8-bit words. Device-tree matching is `brcm,bcm2835-spi`.

## Risks And Edge Cases
DMA handling is the highest-risk area: FIFO access width changes with DMA enable, sglist prologue mutation must be reversed exactly, and TX-only/RX-only transfers use cyclic descriptors with race handling between TX and RX callbacks. Hardware quirks require writing the DONE bit and clearing FIFOs; missing reset paths can leave the controller wedged. Native chip-select support is intentionally redirected to GPIO for documented lines and has legacy lookup-table complexity. Polling timeout heuristics depend on estimated byte time and can affect latency. The maximum DMA transfer size is capped at 65532 bytes because of the 16-bit DLEN register.

## Test Signals
Test short transfers that stay in polling mode, longer IRQ transfers, DMA transfers above 96 bytes, TX-only/RX-only/full-duplex DMA, vmalloc-backed buffers with non-4-byte first sg entries, 3-wire reads, CS GPIO fallback, mode changes before chip-select assertion, error cancellation, and remove/shutdown reset. Debugfs counters should reflect transfer lane selection. DMA mapping or prologue bugs usually show as shifted data, corrupted first bytes, DMA residue warnings, or stuck transfer finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm2835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm2835aux.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm2835aux.c

## Purpose
Implements the Broadcom BCM2835 auxiliary SPI controller driver. It is a simpler polling/IRQ driver for the auxiliary SPI block and intentionally relies on GPIO chip-selects for correct operation, preserving limited native-CS behavior only for legacy device trees.

## Important APIs, Types, And Functions
`struct bcm2835aux_spi` stores MMIO base, clock, IRQ, precomputed CNTL0/CNTL1 register values, transfer buffers and counters, pending byte count, debugfs counters, and debugfs directory. FIFO helpers `bcm2835aux_rd_fifo()` and `bcm2835aux_wr_fifo()` move up to 3 bytes per hardware word using variable-width mode. Transfer logic is split between `bcm2835aux_spi_transfer_helper()`, polling, IRQ, and common transfer entry functions. SPI core hooks include setup, prepare/unprepare message, transfer_one, and error handling.

## Control Flow
Probe allocates the host, sets mode bits and callbacks, maps registers, enables the clock, validates clock rate, resets the block, requests a shared IRQ, registers the controller, and creates debugfs counters. `prepare_message()` computes CNTL0/CNTL1 according to CPOL and writes initial mode registers. `transfer_one()` computes the speed field, stores TX/RX pointers and lengths, clears pending count, estimates whether the transfer should complete within the polling limit, then chooses polling or IRQ. The common helper drains RX words while RX level is nonzero and writes TX words while pending bytes are below the 12-byte FIFO limit. IRQ mode enables TX-empty and idle interrupts, disables TX-empty once TX is exhausted, and finalizes when RX length reaches zero. Unprepare and error handling reset the hardware.

## State And Persistence
Persistent state is mostly controller resources, precomputed register images, and debugfs counters. Transfer state is `tx_buf`, `rx_buf`, `tx_len`, `rx_len`, and `pending`, where `pending` tracks transmitted bytes not yet received back. CNTL register images are recomputed per message and speed bits are updated per transfer. There is no DMA state and no persistent child-device state.

## Dependencies And Integration Points
The driver depends on Linux SPI, platform resources, OF matching, clocks, shared IRQs, debugfs, and MMIO. It matches `brcm,bcm2835-aux-spi`, advertises `SPI_CPOL`, `SPI_CS_HIGH`, and `SPI_NO_CS`, supports 8-bit words, and uses GPIO descriptors. Native chip select is warned against and only CS0 is tolerated for old DT compatibility.

## Risks And Edge Cases
The auxiliary hardware writes up to 3 bytes per FIFO word in variable-width mode; off-by-one errors in `pending` or RX length can misalign data. Native chip-select behavior is explicitly broken for multiple CS, CS high, `cs_change`, and delays, so board descriptions should use `cs-gpio`. Polling fallback to IRQ depends on the `polling_limit_us` module parameter. The driver does not support SPI_CPHA, so clients requiring other modes must not bind here.

## Test Signals
Test GPIO chip-select transfers, short polling transfers, longer IRQ transfers, TX-only/RX-only/full-duplex buffers whose lengths are not multiples of 3, CPOL mode behavior, polling disabled by setting `polling_limit_us=0`, native-CS warning paths, and error reset. Debugfs counters should show polling, IRQ, and polling-to-IRQ fallback counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm2835aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm63xx-hsspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm63xx-hsspi.c

## Purpose
Implements the Broadcom BCM63xx High Speed SPI controller driver for older broadband SoCs and compatible `bcmbca-hsspi-v1.0` hardware. It supports a 512-byte FIFO, dual-bit transfers, polling or interrupt completion modes, a prepend optimization for multi-transfer messages, and a dummy-chip-select workaround for hardware that cannot keep CS asserted through idle gaps.

## Important APIs, Types, And Functions
`struct bcm63xx_hsspi` stores completion, bus/message mutexes, platform/clock resources, MMIO base and FIFO pointer, base speed, chip-select polarity cache, sysfs-controlled wait/transfer modes, prepend metadata, and the prepend buffer. Sysfs attributes `wait_mode` and `xfer_mode` expose runtime policy. Core helpers include `bcm63xx_prepare_prepend_transfer()`, `bcm63xx_hsspi_do_prepend_txrx()`, `bcm63xx_hsspi_do_dummy_cs_txrx()`, `bcm63xx_hsspi_do_txrx()`, `bcm63xx_hsspi_set_clk()`, `bcm63xx_hsspi_set_cs()`, and `bcm63xx_hsspi_transfer_one()`.

## Control Flow
Probe obtains IRQ, registers, clocks, optional reset, allocates the host, initializes mutexes/completion, sets SPI controller capabilities, clears interrupts, caches default CS polarity, enables clock gating behavior, requests IRQ, enables runtime PM, creates sysfs attributes, and registers the controller. For each SPI message, the driver locks `msg_mutex`, tries prepend mode unless forced to dummy-CS mode, and either executes a merged/prepended transfer or falls back to dummy-CS transfer. Prepend mode combines leading half-duplex writes into controller prepend bytes and sends one final transfer. Dummy-CS mode asserts the real target manually, selects an inactive dummy CS in hardware, runs each transfer in FIFO-sized chunks, handles delay and cs_change semantics, then restores CS. Completion can be interrupt-driven via `done` or polling by watching ping-pong busy status.

## State And Persistence
`wait_mode` and `xfer_mode` persist as mutable sysfs-controlled driver state until changed or driver removal. `cs_polarity` caches per-CS polarity and is updated in setup. `prepend_cnt`, `md_start`, and `prepend_buf` are per-message scratch protected by `msg_mutex`. `bus_mutex` protects global control register changes for CS and clock polarity. System suspend disables clocks after suspending the SPI controller; resume reenables clocks and resumes the controller.

## Dependencies And Integration Points
The driver depends on Linux SPI, `spi-mem` support probing, platform resources, clocks `hsspi` and optional `pll`, optional reset control, IRQs, sysfs, mutexes, completions, runtime PM, and OF matching. It advertises CPOL/CPHA/CS_HIGH plus RX/TX dual mode and 8-bit words. Compatible strings are `brcm,bcm6328-hsspi` and `brcm,bcmbca-hsspi-v1.0`.

## Risks And Edge Cases
The prepend eligibility rules are strict: delays, `cs_change`, unsupported transfer ordering, prepend length over 15, total FIFO overrun, or single-bit after multi-bit transitions can force dummy-CS fallback or fail when prepend mode is forced. Dummy-CS mode is a hardware workaround and caps speed to 25 MHz in auto mode for safety. The transfer code mutates `t->speed_hz` when falling back, which may surprise callers if they inspect transfer state later. Sysfs mode changes race are mitigated by `msg_mutex`, but operational policy can change at runtime. Interrupt mode must clear stale status before enabling to avoid spurious completions.

## Test Signals
Test prependable flash-style messages, non-prependable messages requiring dummy CS, forced prepend failure, forced dummy-CS mode, dual RX/TX operations, FIFO boundary lengths, sysfs wait-mode switching, timeout behavior in polling and IRQ modes, CS polarity setup, suspend/resume, and `spi-mem` default support negotiation. Warnings about forced dummy-CS speed reduction and errors about non-prependable forced prepend mode are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm63xx-hsspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm63xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm63xx.c

## Purpose
Implements the legacy Broadcom BCM63xx SPI controller driver for BCM6338/6348 and BCM3368/6358/6262/6368-style register layouts. It handles one FIFO-sized message batch at a time, supports only basic CPOL/CPHA and 8-bit words, and works around the controller’s inability to keep chip select active by merging transfers when possible.

## Important APIs, Types, And Functions
`struct bcm63xx_spi` stores completion, MMIO base, IRQ, layout-specific register offsets, FIFO size, message-control metadata, TX/RX IO pointers, clock, and platform device. Register-layout tables `bcm6348_spi_reg_offsets` and `bcm6358_spi_reg_offsets` adapt the same logic to two hardware families. Important functions include `bcm63xx_spi_setup_transfer()`, `bcm63xx_txrx_bufs()`, `bcm63xx_spi_transfer_one()`, `bcm63xx_spi_interrupt()`, `bcm63xx_spi_max_length()`, probe/remove, and suspend/resume.

## Control Flow
Probe chooses the register layout from OF match or platform ID, gets IRQ/clock/reset, allocates the host, maps registers, requests IRQ, sets SPI core callbacks and limits, initializes clock/reset/interrupt state, enables runtime PM, and registers the controller. Message execution walks transfers, grouping them until `cs_change` or end-of-message, while rejecting total lengths beyond FIFO size, speed changes between grouped transfers, or delays that would require CS to remain asserted. `bcm63xx_txrx_bufs()` copies TX data into the hardware message FIFO, writes dummy bytes for read-only transfers to satisfy a hidden FIFO-length accumulator, programs message control and command registers, enables command-done interrupt, waits for completion, and copies RX data back.

## State And Persistence
Persistent state is register layout, FIFO size, clock, IO pointers, and completion. Per-message state is local to transfer grouping and `bcm63xx_txrx_bufs()`. The driver does not keep per-device controller state beyond SPI core fields. Suspend suspends the controller and disables the clock; resume reenables the clock and resumes the controller.

## Dependencies And Integration Points
The driver depends on Linux SPI, platform/OF matching, clocks, reset controls, interrupts, completions, runtime PM, and MMIO. It supports platform IDs `bcm6348-spi` and `bcm6358-spi` plus OF compatibles `brcm,bcm6348-spi` and `brcm,bcm6358-spi`. It exposes `transfer_one_message` rather than `transfer_one` because it must merge transfers to approximate CS behavior.

## Risks And Edge Cases
The controller can only transfer FIFO-sized batches, and delays or speed changes inside grouped messages are rejected. Prepend support is limited to one small leading TX transfer before RX and only up to seven bytes. Read-only transfers require dummy TX writes due to hidden hardware accounting. Interrupt handling always returns handled after clearing status, so shared IRQ behavior depends on interrupt routing. Big-endian builds use `iowrite16be()` for 16-bit writes, while byte accesses remain byte-order independent.

## Test Signals
Test both register layouts, full-duplex and half-duplex transfer groups, small TX prepend followed by RX, read-only dummy-fill behavior, FIFO-limit rejection, delay and speed-change rejection, command-done timeout, suspend/resume, and legacy platform-data instantiation. Good signals are correct `actual_length`, absence of shifted RX data after prepend, and clean interrupt completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcm63xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcmbca-hsspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-bcmbca-hsspi.c

## Purpose
Implements the Broadcom BCMBCA High Speed SPI controller driver for `brcm,bcmbca-hsspi-v1.1`. It is a newer HSSPI variant with a separate `spim-ctrl` chip-select override register, polling/interrupt completion modes, dual-bit support, and explicit SPI message-level chip-select handling.

## Important APIs, Types, And Functions
`struct bcmbca_hsspi` stores completion, bus/message mutexes, platform/clock resources, HSSPI and SPIM control MMIO bases, FIFO pointer, base speed, chip-select polarity cache, and wait mode. Sysfs exposes only `wait_mode`. Main helpers are `bcmbca_hsspi_set_cs()`, `bcmbca_hsspi_set_clk()`, `bcmbca_hsspi_wait_cmd()`, `bcmbca_hsspi_do_txrx()`, `bcmbca_hsspi_setup()`, `bcmbca_hsspi_transfer_one()`, and the IRQ handler.

## Control Flow
Probe maps named `hsspi` and `spim-ctrl` resources, enables `hsspi` or fallback `pll` clock, allocates the host, initializes locks/completion, configures SPI core callbacks, clears interrupts, caches default CS polarity, requests IRQ, enables runtime PM, creates the sysfs group, and registers the controller. Setup programs latch/launch edge behavior, CS polarity in the HSSPI global register, and override output polarity in `spim_ctrl`. Message transfer locks `msg_mutex`, runs each transfer through FIFO chunks, asserts CS as close as possible to command start, handles delays and `cs_change` between transfers, updates actual length, and deasserts CS unless the final transfer requests it remain active.

## State And Persistence
Persistent state includes MMIO bases, clocks, FIFO pointer, base speed, cached CS polarity, and sysfs-controlled `wait_mode`. Per-transfer state is local in `bcmbca_hsspi_do_txrx()`. `bus_mutex` protects shared global and SPIM control register changes; `msg_mutex` serializes transfer policy and wait-mode changes. Suspend disables clocks after SPI controller suspend; resume restores clocks and resumes the controller.

## Dependencies And Integration Points
The driver depends on Linux SPI, platform named resources, clocks, IRQs, sysfs, mutexes, completions, runtime PM, and OF. It advertises CPOL/CPHA/CS_HIGH plus RX/TX dual and 8-bit words. Unlike the older BCM63xx HSSPI driver, it does not expose xfer-mode sysfs or prepend logic; chip select is controlled through the external SPIM control override register.

## Risks And Edge Cases
CS 7 is special-cased to skip override, which is board-specific and can hide failures on other designs. `bcmbca_hsspi_do_txrx()` accepts a `msg` parameter but does not use it, so future changes should avoid assuming message context is active there. Interrupt-mode completion requires stale interrupt status to be cleared when switching modes. FIFO chunking must respect opcode space for TX/write operations. As with other HSSPI drivers, global clock polarity and CS polarity are shared hardware state protected by locks.

## Test Signals
Test polling and interrupt wait modes, all usable chip selects including CS7 behavior, CPOL/CPHA setup, CS_HIGH polarity, dual TX/RX transfers, FIFO boundary chunking, `cs_change` and `cs_off` sequencing, suspend/resume, and probe failure cleanup after sysfs registration. Timeout logs and missing deassertions on logic analyzer traces are key failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bcmbca-hsspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bitbang-txrx.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-bitbang-txrx.h

## Purpose
Provides inline SPI bitbang transmit/receive loops for controllers that implement `setsck()`, `setmosi()`, `getmiso()`, and `spidelay()` before including the header. It covers big-endian/MSB-first and little-endian/LSB-first bit ordering for CPHA 0 and CPHA 1 modes.

## Important APIs, Types, And Functions
The exported inline helpers are `bitbang_txrx_be_cpha0()`, `bitbang_txrx_be_cpha1()`, `bitbang_txrx_le_cpha0()`, and `bitbang_txrx_le_cpha1()`. Each takes `struct spi_device *`, half-period delay in nanoseconds, CPOL, SPI controller no-TX/no-RX flags, a word value, and bit count, then returns the received word shifted into the same scalar.

## Control Flow
Each helper loops once per bit. CPHA0 variants set MOSI on the trailing edge, delay, toggle SCK to the active edge, delay/sample MISO, then return SCK to inactive polarity. CPHA1 variants toggle SCK first, set MOSI on the leading edge, delay, toggle back, delay/sample MISO on the trailing edge. Big-endian helpers shift toward bit 31 and sample into the low bit after left shifts; little-endian helpers shift right and sample into the current high receive bit.

## State And Persistence
The header keeps no persistent state. It does cache `oldbit` locally to avoid repeated MOSI writes when the outgoing bit does not change. All external line state is maintained by the including driver’s `setsck()` and `setmosi()` implementations.

## Dependencies And Integration Points
Including code must define the four low-level line functions/macros and include SPI core definitions for mode flags. The helpers are used by bitbang-style drivers such as `spi-butterfly.c` and can be wired into the `spi_bitbang` framework in `spi-bitbang.c`.

## Risks And Edge Cases
Because this is a header-only template, incorrect or non-inline line functions can make timing unpredictable. `getmiso()` must return only 0 or 1; larger values corrupt received words. The caller must pass valid bit counts and correct CPOL/CPHA pairing. These loops are CPU-bound and can violate device timing on preempted systems or very fast requested clocks.

## Test Signals
Test with logic analyzer traces for SPI modes 0 through 3, MSB/LSB ordering, no-RX and no-TX flags, MOSI idle behavior in the caller, and devices with strict setup/hold timing. Loopback tests can validate returned word shifting for each helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bitbang-txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bitbang.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-bitbang.c

## Purpose
Provides reusable SPI controller utilities for simple polling and bitbanging host drivers. It adapts per-word bitbang callbacks or transfer-at-a-time callbacks into Linux SPI controller setup, transfer, chip-select, registration, and teardown behavior.

## Important APIs, Types, And Functions
Internal `struct spi_bitbang_cs` stores per-device half-period delay, selected `txrx_word` callback, and selected buffer-transfer routine. Exported functions are `spi_bitbang_setup_transfer()`, `spi_bitbang_setup()`, `spi_bitbang_cleanup()`, `spi_bitbang_init()`, `spi_bitbang_start()`, and `spi_bitbang_stop()`. Buffer helpers handle 8-, 16-, and 32-bit words. Controller callbacks installed by `spi_bitbang_init()` include prepare/unprepare hardware, transfer_one, and optional set_cs.

## Control Flow
Setup allocates `spi->controller_state` if needed, selects a mode-specific word transfer callback from `bitbang->txrx_word[]`, configures bits-per-word and delay, and optionally sets MOSI idle. During a transfer, `spi_bitbang_transfer_one()` calls any setup-transfer hook, runs `bitbang->txrx_bufs()`, translates partial positive byte counts to `-EREMOTEIO`, finalizes the current transfer, and returns status. The default `spi_bitbang_bufs()` handles 3-wire direction changes and no-RX/no-TX flags before dispatching to the selected per-width loop. `spi_bitbang_start()` initializes callbacks and registers the SPI controller with an extra reference; `spi_bitbang_stop()` unregisters it.

## State And Persistence
Per-controller state is stored in the caller-provided `struct spi_bitbang`, including lock, busy flag, callbacks, flags, and controller pointer. Per-device state is dynamically allocated as `struct spi_bitbang_cs` and freed in cleanup. The `busy` flag is set during prepare hardware and cleared during unprepare hardware under `bitbang->lock`.

## Dependencies And Integration Points
The file depends on Linux SPI core, `linux/spi/spi_bitbang.h`, workqueue/interrupt headers for framework compatibility, delay/time constants, and module exports. Glue drivers provide `chipselect`, mode-specific `txrx_word` callbacks, optional `txrx_bufs`, optional line-direction and MOSI-idle callbacks, and a preallocated SPI controller.

## Risks And Edge Cases
Controller initialization rejects drivers that already set `transfer` or `transfer_one_message`, because this utility owns `transfer_one`. If GPIO descriptors are used without `SPI_CONTROLLER_GPIO_SS`, a custom chipselect callback is not installed, which can surprise older glue drivers. Bits-per-word above 32 are rejected. Delay calculation can fail for extremely low speeds that exceed `MAX_UDELAY_MS`. The transfer function finalizes even when returning an error, so glue callbacks must not also finalize.

## Test Signals
Test glue drivers using custom chipselects and GPIO descriptors, 8/16/32-bit transfers, 3-wire TX and RX phases, MOSI idle setting, partial-transfer error conversion, setup failure cleanup, registration/unregistration reference behavior, and low-speed delay rejection. Logic analyzer traces should show CS delay and expected clock polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-bitbang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-brcmstb-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-brcmstb-qspi.c

## Purpose
Provides the BRCMSTB-specific platform wrapper for the common Broadcom QSPI driver. It binds set-top SoC compatibles and delegates all substantive controller behavior to `spi-bcm-qspi.c`.

## Important APIs, Types, And Functions
The file defines an OF match table for `brcm,spi-brcmstb-qspi` and `brcm,spi-brcmstb-mspi`, a probe function that calls `bcm_qspi_probe(pdev, NULL)`, a remove function that calls `bcm_qspi_remove()`, and a `platform_driver` using the common `bcm_qspi_pm_ops`.

## Control Flow
When a matching platform device probes, the wrapper invokes the common QSPI probe with no SoC-specific interrupt controller, causing the common driver to use its direct/named IRQ handling paths. Remove and PM operations are similarly delegated to common code.

## State And Persistence
This wrapper maintains no private runtime state. Platform driver binding state is held by the driver core, and all controller state is allocated and stored by the common Broadcom QSPI driver.

## Dependencies And Integration Points
It depends on platform driver infrastructure, OF matching, module support, and `spi-bcm-qspi.h`. It integrates BRCMSTB device-tree compatibles with the common QSPI implementation.

## Risks And Edge Cases
Because it passes `NULL` for `soc_intc`, BRCMSTB devices that route interrupts through a SoC-specific mux would need a different wrapper or new integration. Any common-driver probe requirement for named resources, IRQs, or clocks applies here even though this file does not mention those resources.

## Test Signals
Probe a BRCMSTB QSPI/MSPI node and verify the common driver registers the SPI controller, resources map correctly, IRQs are requested, and suspend/resume uses `bcm_qspi_pm_ops`. Wrapper-specific testing is mostly compatible-string coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-brcmstb-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-butterfly.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-butterfly.c

## Purpose
Implements a parport-to-SPI adapter driver for the AVR Butterfly board and its DataFlash device. It demonstrates a concrete SPI bitbang controller built on the `spi_bitbang` framework and parallel-port pin manipulation.

## Important APIs, Types, And Functions
`struct butterfly` embeds `struct spi_bitbang`, stores the parport and pardevice, tracks the last data byte driven to the port, records created SPI devices, and holds two `spi_board_info` entries. Low-level bitbang hooks are `setsck()`, `setmosi()`, `getmiso()`, and `butterfly_chipselect()`. `butterfly_txrx_word_mode0()` wires `bitbang_txrx_be_cpha0()` from `spi-bitbang-txrx.h` into SPI mode 0. Parport lifecycle is handled by `butterfly_attach()` and `butterfly_detach()`.

## Control Flow
When a parport matches, `butterfly_attach()` refuses additional instances because of a single global pointer, allocates an SPI host, configures bus number 42 and two chip selects, wires bitbang callbacks, registers and claims a parport device, powers and resets the Butterfly through data/control pins, starts the SPI bitbang controller, and creates an `mtd_dataflash` SPI child on chip select 1 with partition data. Detach stops the bitbang controller, powers off VCC, releases/unregisters the parport device, and drops the SPI controller reference.

## State And Persistence
The global `butterfly` pointer enforces a single active adapter and persists until detach. `lastbyte` mirrors the parallel port data register state for SCK/MOSI/VCC/reset updates. Child SPI devices and MTD partitions exist while the bitbang controller is registered. Partition definitions and flash platform data are static module data.

## Dependencies And Integration Points
The driver depends on Linux parport, SPI core, `spi_bitbang`, `spi-bitbang-txrx.h`, SPI flash platform data, and MTD partitions. It registers as a `parport_driver` named `spi_butterfly`, creates an SPI controller, and instantiates an `mtd_dataflash` child device. Documentation is referenced in `Documentation/spi/butterfly.rst`.

## Risks And Edge Cases
There is no hardware discovery; attach assumes the custom cable and Butterfly are present. The single global prevents more than one adapter. Timing uses no delay by default, so it relies on parport operations being slow enough. Power/reset sequencing is board-specific. The code uses old-style board-info instantiation and static partitioning; modern systems may prefer device tree or software nodes. Failure cleanup must unwind parport claim, power, and SPI host references in the right order.

## Test Signals
Test attach/detach with the actual parallel-port cable, logic analyzer mode-0 waveforms, DataFlash device creation, MTD partition registration, power/reset pin behavior, and failure paths when parport claim or `spi_bitbang_start()` fails. Functional signal is successful reads from the DataFlash child at the configured speed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-butterfly.c -->
