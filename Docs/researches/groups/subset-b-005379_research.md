# Research group subset-b-005379

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-apple.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-apple.c

## Purpose
Apple SoC SPI host driver for Asahi-supported Apple controllers, exposing one chip select through the Linux SPI core. It programs Apple-specific MMIO registers for IRQ or short polling transfers, supports CPOL, CPHA, LSB-first, 1 to 32 bits per word, GPIO descriptors, and runtime PM.

## Important APIs, Types, and Functions
`struct apple_spi` holds MMIO base, enabled clock, and a completion for IRQ wakeups. Register helpers wrap relaxed MMIO access. `apple_spi_init()` resets FIFOs, selects IRQ mode, disables delay registers, and leaves CS inactive. `apple_spi_prepare_message()` programs mode bits. `apple_spi_set_cs()` drives the hardware CS bit. `apple_spi_transfer_one()` is the main SPI core callback and delegates setup, FIFO push, FIFO drain, and waits to `apple_spi_prep_transfer()`, `apple_spi_tx()`, `apple_spi_rx()`, and `apple_spi_wait()`.

## Control Flow
Probe allocates a managed SPI controller, maps registers, enables the bus clock, requests the IRQ, enables runtime PM, initializes hardware, and registers the controller. For each transfer, the driver computes a clock divider, sets bits per word in `SHIFTCFG`, resets FIFOs, clears interrupt flags, programs TX/RX word counts, primes TX FIFO, starts the controller, then loops until the requested TX and RX completion bits have been seen. Depending on expected wait time, completion is either polled or IRQ-driven through `apple_spi_irq()`.

## State and Persistence
State is volatile hardware state plus the per-transfer local cursor variables. The driver does not persist configuration outside registers. Runtime PM is automatic through the SPI core, with clock ownership handled by devm clock APIs.

## Dependencies and Integration Points
It integrates with platform devices matched by `apple,t8103-spi` or `apple,spi`, Linux `spi_controller`, clk, IRQ, MMIO, OF, and PM runtime. It relies on SPI core validation for most transfer shape constraints.

## Risks
Timeouts are bounded at 200 ms per wait, but a completed RX transfer can still require a retry loop to pull the final word. `WARN_ON()` catches unexpected FIFO overrun or underrun after completion. Lengths not aligned to the chosen bytes-per-word are converted by integer division, so SPI core validation is important. The clock divider is capped at `0x7ff`, which may silently produce a faster-than-requested low speed.

## Test Signals
Useful signals are probe success, IRQ delivery, no transfer timeout logs, expected `actual_length` from SPI core tests, loopback transfers at 8/16/32 bpw, LSB-first mode tests, and stress tests around RX-only, TX-only, full-duplex, and very slow transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-apple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ar934x.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-ar934x.c

## Purpose
SPI controller driver for Qualcomm Atheros AR934x and QCA95xx SoCs. It exposes a simple register-shift engine with three chip selects, fixed supported word sizes, and no DMA or interrupt handling.

## Important APIs, Types, and Functions
`struct ar934x_spi` stores controller, MMIO base, clock, and cached input clock rate. `ar934x_spi_clk_div()` computes the 6-bit divider for the hardware control register. `ar934x_spi_setup()` clamps max speed to the hardware range. `ar934x_spi_transfer_one_message()` implements all transfer handling and finalizes messages. Probe maps registers, enables the clock, initializes function-select and IOC defaults, fills `spi_controller` callbacks, and calls `spi_register_controller()`.

## Control Flow
At probe, flash mapping is disabled by writing `AR934X_SPI_ENABLE` to the function-select register, and IOC is restored to inactive CS and low DO/CLK. Transfer processing iterates each `spi_transfer`, selects bytes per word from bits-per-word, computes and writes the clock divider, then chunks the buffer into one hardware word at a time. For TX, bytes are packed MSB-first into `DATAOUT`. The driver writes `SHIFT_CTRL` with enable, CS, termination flag for the final word of the final transfer, and bit count. It polls for `SHIFT_EN` to clear with a 5 usec timeout, then unpacks `DATAIN` into RX buffers.

## State and Persistence
There is little software state beyond the cached clock rate. The hardware register state persists until remove or next transfer. Message accounting is maintained by `m->actual_length` and `m->status`.

## Dependencies and Integration Points
It depends on platform resources, clk, MMIO, OF match `qca,ar934x-spi`, and the SPI core `transfer_one_message` path. It supports `SPI_LSB_FIRST` as a mode bit but the transfer packing is otherwise explicit.

## Risks
The hardware poll timeout is very short, so slow or wedged hardware immediately fails the message. Only 8, 16, 24, and 32 bpw are advertised; other values fall into 32-bit packing if somehow passed. The `term` flag is not reset inside the outer loop once set, so correctness depends on it being set only at the last chunk. Divider failures are converted to `-EIO`, losing the more precise cause.

## Test Signals
Exercise all advertised word sizes, per-transfer speed changes, multi-transfer messages, RX-only and TX-only buffers, final chip-select termination behavior, and divider lower/upper limits. A logic analyzer should confirm CS and bit counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ar934x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-armada-3700.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-armada-3700.c

## Purpose
Marvell Armada 3700 SPI host driver for FIFO and full-duplex non-FIFO transfers. It supports multiple native chip selects from DT, mode 3, 8/32 bpw, and single, dual, or quad transfer lane flags.

## Important APIs, Types, and Functions
`struct a3700_spi` stores controller, MMIO base, clock, IRQ, buffer cursors, byte length, wait mask, and completion. Register helpers are `spireg_read()` and `spireg_write()`. Setup helpers program CS, pin mode, FIFO mode, CPOL/CPHA, clock prescaler, byte length, FIFO thresholds, and headers. Core callbacks are `a3700_spi_prepare_message()`, `a3700_spi_transfer_one()`, `a3700_spi_unprepare_message()`, and `a3700_spi_set_cs()`.

## Control Flow
Probe reads `num-cs`, maps resources, obtains a prepared clock, computes min/max speed, initializes hardware, requests IRQ, and registers the controller. Message preparation enables the clock, flushes FIFOs, and sets SPI mode. A transfer is initialized into `tx_buf`, `rx_buf`, and `buf_len`. Full-duplex uses non-FIFO mode and busy-waits on `XFER_DONE` for each 4-byte or final 1-byte chunk. Half-duplex FIFO mode configures lane width, thresholds, headers for unaligned leading TX bytes, starts read or write mode, then waits on `WFIFO_RDY`, `RFIFO_RDY`, `WFIFO_EMPTY`, and `XFER_RDY` through completion-backed IRQ handling.

## State and Persistence
State is primarily MMIO state plus current buffer cursors. `wait_mask` links the active waiter to the IRQ handler. The clock is enabled only during prepared messages. CS state is held in hardware enable bits and deactivated explicitly.

## Dependencies and Integration Points
It integrates with OF compatible `marvell,armada-3700-spi`, platform IRQ/MMIO, clk, completions, and SPI core transfer callbacks. Lane mode values come from SPI core transfer fields.

## Risks
The wait path clears `wait_mask` before its second status recheck, making that fallback ineffective as written and increasing timeout sensitivity for edge-triggered IRQ races. Full-duplex uses unbounded `cpu_relax()` polling on `XFER_DONE`. Several timeout constants are only 10 ms or 10 loop iterations, so slow hardware may fail. Header-mode unaligned TX handling mutates `buf_len` and `tx_buf`, which must remain tightly coupled to FIFO writes.

## Test Signals
Use IRQ-driven FIFO read/write tests, full-duplex loopback, unaligned transfer lengths, 8 and 32 bpw, dual and quad paths, clock gating through prepare/unprepare, timeout injection, and CS behavior across multi-transfer messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-armada-3700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-aspeed-smc.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-aspeed-smc.c

## Purpose
ASPEED FMC/SPI memory controller driver for SPI NOR style devices across AST2400, AST2500, AST2600, and AST2700 variants. It provides `spi-mem` exec and direct-map read support, user-mode SPI transfers, AHB window management, chip enable/type setup, and read timing calibration.

## Important APIs, Types, and Functions
`struct aspeed_spi_data` describes per-SoC capabilities, segment encoding, clock dividers, calibration, max CS, and window granularity. `struct aspeed_spi` is controller-wide state; `struct aspeed_spi_chip` stores per-CS control registers, AHB mapping, configured read controls, clock, and forced user-mode flag. Important paths include `aspeed_spi_exec_mem_op()`, `aspeed_spi_dirmap_create()`, `aspeed_spi_dirmap_read()`, `aspeed_spi_setup()`, `aspeed_spi_user_transfer()`, `aspeed_spi_set_window()`, adjustment helpers, and calibration helpers.

## Control Flow
Probe selects SoC data from OF, maps controller registers and the AHB memory resource, enables the clock, configures controller callbacks, computes default windows, and registers the controller. Setup initializes per-CS registers, optionally sets flash type, and enables the chip. `exec_op` programs opcode, address mode, dummy cycles, data width, and user-mode read/write helpers, then restores default read control state. Direct-map creation adjusts the AHB segment window to the requested flash range, programs command-mode read settings, sets 3-byte or 4-byte address mode, and calibrates read timing. Direct-map reads use `memcpy_fromio()` when the window covers the request, otherwise fall back to user-mode command reads.

## State and Persistence
Per-chip `ctl_val[]` caches base/read/write control values and calibrated dividers. Segment registers persist remapped AHB windows. `force_user_mode` persists when trimming makes command mode incomplete. `cs_change` tracks user transfer preparation/unpreparation.

## Dependencies and Integration Points
It integrates with SPI core and `spi_mem`, platform OF data, clk, MMIO, and memory resources. It matches ASPEED FMC/SPI compatibles and relies on child nodes to determine active chip selects.

## Risks
Window calculations are hardware-specific and can reduce command-mode coverage, affecting performance and debug behavior. Calibration requires non-uniform flash data; uniform regions force low speed. Some user-mode full-duplex support is AST2700-specific and rejects dual/quad full-duplex. No DMA path is implemented even though IRQ comments mention DMA. Address-mode changes are global CE control bits and must be restored correctly.

## Test Signals
Run SPI NOR read/write/erase via `spi-mem`, direct-map reads across window edges, 3-byte and 4-byte address modes, dual/quad read modes, multi-CS window layouts, calibration logs at different flash contents, fallback-to-user-mode reads, and remove-time chip disable checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-aspeed-smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-at91-usart.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-at91-usart.c

## Purpose
Microchip AT91 USART-as-SPI controller driver. It reuses a USART parent device register block as an 8-bit SPI host with mandatory TX and RX, GPIO chip selects, optional DMA, interrupt-driven PIO fallback, and system/runtime PM.

## Important APIs, Types, and Functions
`struct at91_usart_spi` stores parent platform device, current transfer, registers, clock, completion, spinlock, physical base, IRQ, remaining byte counters, cached status, and DMA flag. DMA functions configure, release, stop, and execute slave DMA. PIO helpers read status, write THR, read RHR, and handle overrun. SPI callbacks are `at91_usart_spi_setup()`, `at91_usart_spi_prepare_message()`, `at91_usart_spi_transfer_one()`, `at91_usart_spi_unprepare_message()`, and cleanup.

## Control Flow
Probe obtains the parent USART memory and IRQ, gets the USART clock, allocates a SPI controller, sets GPIO CS support, maps registers, requests IRQ, enables the clock, initializes USART SPI mode, tries to configure DMA, initializes lock/completion, and registers the controller. Setup stores a per-device mode register in `spi->controller_state`. Prepare enables RX/TX, enables overrun/RX-ready interrupts, and writes the saved mode. Transfer programs baud rate, initializes byte counters, and loops while TX or RX remains. For sufficiently large transfers and available DMA, it submits RX and TX SG descriptors and waits for RX DMA completion. Otherwise it polls TX-ready and writes one byte, while RX data is drained by IRQ. Unprepare resets/disables RX/TX and interrupts.

## State and Persistence
Per-device mode state is dynamically allocated and freed in cleanup. Transfer state lives in remaining-byte counters and `current_transfer`. DMA channel pointers are stored in the SPI controller. Runtime PM gates the USART clock and pinctrl state.

## Dependencies and Integration Points
It depends on a parent USART platform device, clk, GPIO descriptors, pinctrl, DMAengine, IRQ, PM runtime, and SPI core flags `SPI_CONTROLLER_MUST_RX` and `SPI_CONTROLLER_MUST_TX`.

## Risks
DMA setup failure currently exits the probe path after clock enable instead of treating DMA as optional, despite transfer code having PIO fallback. PIO has no explicit per-transfer timeout in the main loop, relying on hardware progress and overrun detection. Cleanup declares a different pointer type name than setup allocated, but only frees it. DMA callback re-enables RX-ready IRQ after DMA and sets RX remaining to zero.

## Test Signals
Validate probe with and without DMA channels, 8-bit loopback, short PIO transfers, large DMA transfers, TX-only/RX-only core-provided dummy buffers, overrun injection, suspend/resume reinitialization, GPIO CS polarity, and baud-rate limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-at91-usart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-atcspi200.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-atcspi200.c

## Purpose
Andes ATCSPI200 SPI controller driver focused on `spi-mem` operations for Qilai and AE350 compatibles. It supports command/address/data transactions, single to quad data widths, optional DMA for large aligned data phases, and suspend/resume.

## Important APIs, Types, and Functions
`struct atcspi_dev` stores controller, mutex, DMA completion, regmap, clock, data register DMA address, FIFO sizes, target clock, data-merge flag, and DMA availability. `atcspi_exec_mem_op()` is the central `spi_mem` path. Helpers program transfer format/control, poll FIFO readiness, transfer data in PIO, configure DMA, map `spi_mem` data buffers for DMA, and wait for controller idle. `atcspi_setup()` resets hardware, configures 8-bit data length, reads FIFO sizes, and programs SCLK divider.

## Control Flow
Probe allocates the controller, initializes mutex and regmap-backed MMIO, enables the clock, fills controller properties, resets/configures the hardware, registers the controller, then tries to acquire RX/TX DMA channels. Each memory op is serialized by `mutex_lock()`, programs format/control/address/opcode, chooses DMA when enabled and length is at least 256 bytes, otherwise uses FIFO polling. After data movement, it polls `ATCSPI_ACTIVE` clear before unlocking. `adjust_op_size` caps data to 512 bytes and aligns DMA-sized operations down to four bytes.

## State and Persistence
Controller state includes cached clock rate, selected SCLK rate, FIFO sizes, and transient `data_merge` mode. DMA channels live in `host->dma_rx` and `host->dma_tx`. Registers are not cached by regmap. Suspend disables the clock after SPI core suspend; resume re-enables the clock, reruns setup, then resumes the controller.

## Dependencies and Integration Points
It integrates with platform MMIO, regmap, clk, DMAengine, SPI core, and `spi_mem`. It uses `spi_controller_dma_map_mem_op_data()` and related unmap helpers for DMA-safe `spi_mem` buffers.

## Risks
The driver is `spi-mem` only and does not implement generic `transfer_one`. `atcspi_init_controller()` sets max speed to a fixed target rather than reading per-device speeds. DMA enable bits are set but not explicitly cleared after DMA transfers. Data merge assumes 4-byte aligned lengths and pointer access; `adjust_op_size` helps only for DMA-sized ops.

## Test Signals
Run SPI NOR read-id, read, page program, quad read, operation splitting at 512 bytes, DMA and PIO length thresholds, unaligned small transfers, suspend/resume, clock divider boundary tests, and forced DMA timeout/error tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-atcspi200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ath79.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-ath79.c

## Purpose
Bitbang SPI driver for Atheros AR71XX, AR724X, and AR913X SoCs. It toggles controller GPIO-style registers for SPI mode 0 transfers and provides a fast `spi-mem` read path for memory-mapped flash on hardware CS0.

## Important APIs, Types, and Functions
`struct ath79_spi` embeds `spi_bitbang`, caches IOC base and CTRL register state, stores MMIO base, clock, and register read/write delay. `ath79_spi_chipselect()` toggles CS bits. `ath79_spi_enable()` switches the controller to GPIO mode and saves original registers; `ath79_spi_disable()` restores them. `ath79_spi_txrx_mode0()` shifts one word by writing DO and CLK bits. `ath79_exec_mem_op()` temporarily disables GPIO mode to copy directly from mapped flash.

## Control Flow
Probe allocates a SPI host, configures GPIO descriptor use and `SPI_CONTROLLER_GPIO_SS`, installs bitbang callbacks, maps registers, enables the AHB clock, computes the register-read/write delay compensation, enables GPIO-mode SPI, and starts `spi_bitbang`. Normal transfers go through the bitbang framework into `ath79_spi_txrx_mode0()`, which shifts MSB-first data, delays around each register transition, and reads the shifted data register at the end. `spi-mem` fast read only supports opcode `0x0b`, 3-byte address, 1 dummy byte, data-in, no GPIO CS, and native CS0; it disables GPIO mode, copies from `base + addr`, then restores GPIO mode and IOC.

## State and Persistence
`ioc_base` carries the desired stable DO/CLK/CS state across bitbang operations. `reg_ctrl` stores the original controller register for remove. No persistent storage is used. Remove and shutdown stop bitbang and restore hardware state.

## Dependencies and Integration Points
It depends on `spi_bitbang`, `spi_mem`, clk, platform MMIO, OF compatible `qca,ar7100-spi`, and GPIO descriptors for chip-select handling.

## Risks
Only SPI mode 0 has a txrx callback. Timing is approximate and based on a delay factor derived from the AHB clock. Direct mapped `spi-mem` reads are intentionally narrow and can only target native CS0 without GPIO CS. The TODO in enable notes speed setup is fixed rather than per-device.

## Test Signals
Check bitbang transfers with a logic analyzer, CS polarity, multi-CS operation, fast-read fallback behavior for unsupported ops, mapped flash reads on CS0, remove/shutdown register restoration, and delay calibration across AHB clock rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ath79.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-atmel.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-atmel.c

## Purpose
Atmel AT32/AT91 SPI controller driver supporting older PDC engines, newer DMAengine transfers, FIFO and non-FIFO PIO, native and GPIO chip selects, runtime PM, and controller-version capability detection.

## Important APIs, Types, and Functions
`struct atmel_spi` holds locks, registers, clocks, current transfer, DMA bounce buffers, completion, capability flags, backend selection, FIFO size, and chip-select bookkeeping. `struct atmel_spi_device` stores per-device CSR. Major paths include `atmel_spi_setup()`, `atmel_spi_set_cs()`, `atmel_spi_one_transfer()`, DMA/PDC/PIO submission helpers, IRQ handlers `atmel_spi_pio_interrupt()` and `atmel_spi_pdc_interrupt()`, and PM/probe/remove routines.

## Control Flow
Probe selects pinctrl default state, gets IRQ and clocks, allocates the controller, maps registers, detects capabilities from `SPI_VERSION`, configures DMA or PDC, requests the appropriate IRQ handler, enables clocks, reads optional FIFO size, initializes hardware, enables runtime PM, and registers the controller. Per-device setup builds a CSR with bits-per-word, polarity, phase, chip-select-active-after-transfer, and word delay. Transfers reject bits-per-word changes not matching the saved CSR, set speed, initialize completion state, then loop until all bytes are moved. Backend selection is PDC if old hardware, DMA for large transfers when channels are available, or PIO. Completion is interrupt-driven, with timeout based on SPI core transfer timeout.

## State and Persistence
Per-device CSR persists in `spi->controller_state`. Runtime state includes `current_transfer`, remaining byte count, `done_status`, `keep_cs`, FIFO size, last polarity, and native CS allocation for GPIO CS. Hardware is reset on init, error cleanup, remove, and resume. Runtime PM gates both peripheral and optional generated clocks.

## Dependencies and Integration Points
It integrates with platform MMIO/IRQ, clk, optional `spi_gclk`, GPIO descriptors, pinctrl, DMAengine, PM runtime, SPI tracepoints, and OF compatible `atmel,at91rm9200-spi`.

## Risks
Chip-select behavior has many hardware erratum workarounds, including dummy transfers for polarity changes with GPIO CS. The native-CS-for-GPIO check appears inverted: it errors when `native_cs_free` is nonzero. PDC and DMA cleanup paths are complex and sensitive to overrun. Resume manually initializes hardware with clocks temporarily enabled before returning to runtime PM state. FIFO thresholds and byte counts must match bits-per-word exactly.

## Test Signals
Test PIO FIFO and non-FIFO, DMA, and PDC hardware where available; CS GPIO and native CS polarity; bits-per-word 8 to 16; word delays; transfer timeouts and overruns; suspend/resume/runtime autosuspend; vmalloc DMA bounce paths on SAM V4/V5; and multi-transfer messages with `cs_change`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-atmel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-au1550.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-au1550.c

## Purpose
Alchemy Au1550/Au1200/Au1300 PSC SPI host driver using the legacy `spi_bitbang` framework, platform data chip-select callbacks, IRQ-driven PIO, and optional Au1xxx DBDMA for 4 to 8 bit transfers.

## Important APIs, Types, and Functions
`struct au1550_spi` embeds `spi_bitbang`, stores PSC registers, IRQ, transfer cursors, word handlers, selected transfer backend, completion, DBDMA channel IDs, RX temporary DMA buffer, platform data, and MMIO resource. `au1550_spi_baudcfg()` computes hardware baud/divider fields. `au1550_spi_chipsel()` configures mode, word length, DMA disable, speed, and platform CS callbacks. `au1550_spi_dma_txrxb()` and `au1550_spi_pio_txrxb()` implement transfer backends. IRQ dispatch calls either DMA or PIO callback based on word size and DMA availability.

## Control Flow
Module init first validates the Alchemy CPU type and registers an 8-bit DBDMA memory device when DMA is enabled. Probe requires platform data, IRQ, DMA resources, and MMIO resource, manually reserves and maps registers, initializes bitbang callbacks, allocates DBDMA rings and RX temp buffer if available, configures word handlers, requests IRQ, computes host speed limits, initializes PSC SPI mode, and starts bitbang. During CS activation, the driver disables PSC device enable, writes CPOL/CPHA/LSB/word length/DMA/speed settings, waits for device ready, then calls platform CS activation. Transfers wait on `host_done`, completed by PSC events in IRQ context.

## State and Persistence
Word handler function pointers are updated by current bits-per-word. `usedma` is both module parameter and per-device flag. Temporary RX DMA buffer is persistent across transfers and resized as needed. Hardware state is manually restored only through PSC setup/remove paths and platform CS callbacks.

## Dependencies and Integration Points
It depends on MIPS Alchemy PSC and DBDMA headers/APIs, platform data `au1550_spi_info`, `spi_bitbang`, manual MMIO reservation, IRQs, and DMA mapping.

## Risks
The driver is legacy and non-devm; error unwinding is manual. DMA mapping errors are logged but do not always abort before DBDMA setup. DMA uses `virt_to_phys()` after `dma_map_single()`, which is suspicious on nontrivial DMA mappings. DMA only works for <=8 bpw; wider transfers use PIO. Completion waits have no timeout, so a lost IRQ can hang a transfer.

## Test Signals
Validate PIO and DMA transfers, all supported bpw ranges, missing RX buffer path using temp DMA buffer, DBDMA residue accounting after error, platform CS callbacks, module parameter `usedma=0`, probe unwind paths, and IRQ loss/error event behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-au1550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-axi-spi-engine.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-axi-spi-engine.c

## Purpose
Analog Devices AXI SPI Engine host driver. It compiles SPI messages into hardware instruction programs, streams command/TX/RX FIFOs under IRQ control, and optionally exposes SPI offload trigger support with static TX data or stream DMA channels.

## Important APIs, Types, and Functions
`struct spi_engine_program` is a flexible array of 16-bit instructions. `struct spi_engine_message_state` tracks pending command words and TX/RX transfer cursors. `struct spi_engine_offload` stores assigned/prepared state, offload number, optimized config, lane masks, and bits-per-word. `struct spi_engine` stores clocks, MMIO base, lock, completion, interrupt mask, CS inversion, offload memory sizes, caps, and sync behavior. Key functions are precompile/compile, FIFO read/write helpers, IRQ handler, optimize/unoptimize, transfer-one-message, offload prepare/trigger, setup, and probe.

## Control Flow
Probe allocates a controller, detects optional offload from `trigger-sources` and DMA names, enables AXI and SPI clocks, maps registers, validates ADI AXI version, reads data/offload widths, resets interrupt state, requests IRQ, sets controller capabilities by IP version, and registers. Message optimization validates lane modes and offload constraints, computes effective speeds, dry-runs then allocates an instruction program, appends a sync instruction for normal messages, and preloads offload memories when needed. Non-offload transfer initializes message state, writes as much command and TX FIFO as possible, enables FIFO and sync interrupts, waits up to 5 seconds for sync completion, and finalizes. IRQ drains pending bits, refills command/TX FIFOs, drains RX FIFO, and completes on matching sync ID.

## State and Persistence
Compiled programs live in `msg->opt_state` until unoptimized. Runtime FIFO cursors live in `msg_state`. `cs_inv` shadows chip-select inversion and is programmed through command FIFO during setup. Offload assignment/prepared flags prevent conflicting users. Hardware is reset and interrupts disabled by managed release action.

## Dependencies and Integration Points
It depends on ADI AXI common version helpers, clk, IRQ, MMIO, `spi_controller` optimize hooks, tracepoints, SPI offload provider APIs, DMAengine channel requests, OF compatible `adi,axi-spi-engine-1.00.a`, and SPI multi-lane metadata.

## Risks
Normal transfers depend on a final sync IRQ and have a hard 5 second timeout. Offload supports only one offload instance for now. Single-transfer offload through `transfer_one_message` is rejected. FIFO handlers assume SPI core has validated transfer lengths against bits-per-word. Version-gated features mean CS_HIGH, MOSI idle, and multi-data-lane behavior differ by hardware IP version.

## Test Signals
Use message optimization tests with varied speeds, bpw, delays, `cs_change`, `cs_off`, and lane modes; IRQ FIFO refill/drain stress; RX/TX-only and full-duplex transfers; timeout injection; CS_HIGH setup; offload assignment/preparation contention; trigger enable/disable; and DMA channel request naming for offload streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-axi-spi-engine.c -->
