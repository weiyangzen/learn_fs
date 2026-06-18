# subset-b-005390 Research Group

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sun6i.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sun6i.c

## Purpose
Allwinner sun6i/sun8i/sun50i SPI host controller driver. It registers a `spi_controller`, configures native/GPIO chip select, SPI mode, clock dividers or sample modes, FIFO thresholds, burst counters, and optional dual/quad transfers.

## Important APIs, Types, And Functions
`struct sun6i_spi_cfg` provides FIFO depth, clock-control variant, and mode bits. `struct sun6i_spi` stores MMIO, clocks, reset, DMA addresses, completions, active buffers, remaining length, and config. Key functions are `sun6i_spi_probe()`, `sun6i_spi_remove()`, `sun6i_spi_transfer_one()`, `sun6i_spi_handler()`, `sun6i_spi_set_cs()`, `sun6i_spi_prepare_dma()`, `sun6i_spi_can_dma()`, runtime PM callbacks, and FIFO helpers.

## Control Flow
Probe maps registers, requests IRQ, gets clocks/reset, optionally obtains both DMA channels, resumes hardware, enables runtime PM autosuspend, and registers the SPI host. Each transfer clears interrupt state, resets FIFOs, selects PIO or DMA, programs mode/CS/clock/counters/bus width, primes FIFO or submits DMA descriptors, starts exchange, waits for controller completion, then drains FIFO or waits for RX DMA. The IRQ completes transfers, drains RX on RX-ready, and refills TX on TX-empty.

## State And Persistence
Active transfer state is transient in `tx_buf`, `rx_buf`, and `len`; completions synchronize IRQ/DMA completion. Runtime PM gates AHB/module clocks and asserts/deasserts reset. No durable state exists.

## Dependencies And Integration Points
Linux SPI core, platform/OF matching, clk/reset, DMAengine, runtime PM, IRQs, MMIO, and GPIO descriptors. Compatible strings include Allwinner A31, H3, R329, and A523 variants.

## Risks
DMA requires both channels and uses scatter-gather descriptors; timeout cleanup terminates DMA but relies on later setup for full recovery. Clock behavior differs by match data, and dual/quad support is SoC-config dependent. FIFO counter assumptions are called out for A523-compatible hardware.

## Test Signals
Small PIO transfers, FIFO-boundary transfers, large DMA transfers, RX-only/TX-only/full-duplex, CS polarity, GPIO CS, dual/quad modes, runtime PM, and timeout/DMA failure logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sun6i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sunplus-sp7021.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sunplus-sp7021.c

## Purpose
Sunplus SP7021 SPI controller driver supporting either host mode or target mode based on the `spi-slave` property. Host mode uses FIFO/register transfers split into 255-byte chunks; target mode uses slave DMA registers and manually mapped buffers.

## Important APIs, Types, And Functions
`struct sp7021_spi_ctlr` stores master/slave MMIO bases, IRQs, clock/reset, mode, completions, mutex, current buffers, and counters. Main functions are `sp7021_spi_controller_probe()`, host/target transfer callbacks, `sp7021_spi_controller_prepare_message()`, `sp7021_spi_host_irq()`, `sp7021_spi_target_irq()`, target abort, and PM callbacks.

## Control Flow
Probe selects `devm_spi_alloc_host()` or `devm_spi_alloc_target()`, maps named resources, requests master/slave IRQs, enables clock/reset, and registers the controller. Host transfers are chunked, locked with `buf_lock`, clocked, FIFO-primed, started, and completed by the host IRQ. Target TX/RX maps one DMA buffer, programs slave DMA control/length/address, waits for completion, and unmaps.

## State And Persistence
Per-transfer counters and buffers track host FIFO progress; target state is synchronized with completions. Suspend/runtime suspend asserts reset; resume deasserts reset and prepares the clock. No persistent storage.

## Dependencies And Integration Points
SPI core host/target APIs, OF, platform named resources, IRQs, clk/reset, runtime PM, DMA mapping, and GPIO descriptors in host mode.

## Risks
Host mode assumes MUST_RX/MUST_TX dummy buffers are supplied by the SPI core. The host IRQ may spin while waiting for expected RX count. Target mode accepts only TX-only or RX-only transfers. Resume/reset sequencing should be hardware-tested.

## Test Signals
Host and target DT modes, 16-byte FIFO unit behavior, 255-byte chunk boundaries, CPOL/CPHA/CS_HIGH/LSB modes, DMA target completion, abort, reset and PM transitions, and timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sunplus-sp7021.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-synquacer.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-synquacer.c

## Purpose
Socionext Synquacer HSSPI controller driver for OF and ACPI systems. It supports four chip selects, 8/16/24/32-bit words, single/dual/quad transfers, configurable clock source, and interrupt-driven FIFO transfers.

## Important APIs, Types, And Functions
`struct synquacer_spi` caches device, completion, mode, speed, chip select, bpw, ACES/RTM flags, clock, MMIO, active buffers, FIFO word counts, bus width, transfer mode, and IRQ names. Main functions are `synquacer_spi_probe()`, `synquacer_spi_enable()`, `synquacer_spi_config()`, `synquacer_spi_transfer_one()`, `synquacer_spi_set_cs()`, RX/TX IRQ handlers, and FIFO read/write helpers.

## Control Flow
Probe maps registers, resolves iHCLK/iPCLK or ACPI clock rate, requests RX and TX IRQs, reads ACES/RTM properties, enables the module, enables runtime PM, and registers the host. Transfers flush FIFOs, optionally optimize aligned 8-bit transfers as 32-bit FIFO words, configure PCC/FIFO/DMSTART registers, seed TX FIFO, program RX threshold, start the transfer, enable TX or RX interrupts, and wait for completion.

## State And Persistence
Configuration is cached and skipped if unchanged. Resume invalidates cached speed, re-enables clock and hardware, and resumes the controller. No durable state.

## Dependencies And Integration Points
SPI core, platform bus, OF/ACPI, clk, runtime PM, IRQs, MMIO, and device properties. Compatible is `socionext,synquacer-spi`; ACPI ID is `SCX0004`.

## Risks
Full-duplex dual/quad transfers are rejected. Divider bounds reject too-low speeds. Temporary mutation of `xfer->bits_per_word` requires careful restore. RX cleanup drains residual FIFO data into a scratch buffer.

## Test Signals
Word-size coverage, 8-bit aligned optimization, TX-only/RX-only, unsupported full-duplex dual/quad rejection, low-speed divider errors, ACES/RTM flags, OF/ACPI probe, IRQ timeout, suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-synquacer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tegra114.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-tegra114.c

## Purpose
NVIDIA Tegra114/Tegra124/Tegra210 SPI controller driver. It supports native/GPIO chip select, 4-32 bits per word, LSB-first, 3-wire, dual TX/RX, hardware CS timing, tap delays, PIO chunks, and DMA transfers via coherent bounce buffers.

## Important APIs, Types, And Functions
`struct tegra_spi_data` contains controller state, lock, clock/reset/MMIO/IRQ, transfer progress, DMA resources, completions, status fields, register shadows, CS timing, and SoC data. `struct tegra_spi_soc_data` controls interrupt-mask behavior; `struct tegra_spi_client_data` stores tap delays. Main functions include probe/remove, setup/cleanup, `tegra_spi_set_hw_cs_timing()`, `tegra_spi_transfer_one_message()`, transfer setup/start helpers, DMA helpers, FIFO helpers, and threaded IRQ handlers.

## Control Flow
Probe allocates the host, maps registers, gets IRQ/clock/reset, allocates DMA channels and buffers, enables runtime PM, resets hardware, initializes register shadows, requests a threaded IRQ, and registers. Message transfer configures first-transfer mode/CS/tap delays, computes packed/unpacked chunks, flushes FIFOs, starts DMA for chunks larger than the 64-word FIFO or PIO otherwise, waits for completion, and handles `cs_change` and delays.

## State And Persistence
Register shadows and current transfer counters persist across callbacks; per-device tap delay data is allocated at setup. Runtime PM gates the clock; system resume restores command registers and invalidates last-CS cache. No durable storage.

## Dependencies And Integration Points
SPI core, OF matching, clk/reset, runtime PM, GPIO descriptors, DMAengine, threaded IRQs, and child-node tap-delay properties. Compatible strings cover Tegra114/124/210 SPI.

## Risks
Packed/unpacked byte accounting, DMA length rounding, CS mode interactions, timeout reset recovery, and SoC-specific interrupt masks are the primary risk areas. Hardware CS timing only accepts SCK units and clamps values.

## Test Signals
Word-size range, packed/unpacked lengths, FIFO/DMA thresholds, dual and 3-wire modes, GPIO versus native CS, CS timing and `cs_change`, tap delays, runtime PM, suspend/resume, timeout and FIFO error dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tegra114.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tegra20-sflash.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-tegra20-sflash.c

## Purpose
Legacy NVIDIA Tegra20 serial flash controller driver. It is a four-word FIFO SPI host using interrupt-driven CPU transfers and no DMA.

## Important APIs, Types, And Functions
`struct tegra_sflash_data` stores controller handles, lock, clock/reset/MMIO/IRQ, active device/transfer, progress counters, direction, status shadows, command/DMA-control shadows, and completion. Key functions are probe/remove, `tegra_sflash_transfer_one_message()`, transfer setup/start helpers, FIFO fill/drain helpers, ISR, and runtime/system PM callbacks.

## Control Flow
Probe maps resources, requests IRQ, gets clock/reset, enables runtime PM, resets hardware, writes a default master/software-CS command, and registers the controller. Each message transfer programs speed, mode, CS, bit length, TX/RX direction, starts a CPU transfer, waits for completion, checks error flags, updates actual length, and restores default command state. ISR records FIFO errors, clears status, and advances or completes the FIFO chunk.

## State And Persistence
Command and DMA-control shadows persist in memory; transfer progress is reset per transfer. Runtime PM gates the clock after readback. Resume writes saved command state. No durable storage.

## Dependencies And Integration Points
SPI core, OF compatible `nvidia,tegra20-sflash`, platform resources, clk/reset, runtime PM, IRQs, and MMIO.

## Risks
Small FIFO limits throughput and raises interrupt sensitivity. Error recovery resets hardware in IRQ context. A macro references `SPI_TX_EMPTY`/`SPI_RX_EMPTY` names not defined in this file snapshot, which should be checked at build time.

## Test Signals
Serial-flash style 8-bit transfers, lengths beyond four words, RX/TX paths, CPOL/CPHA, timeouts, FIFO errors, reset recovery, runtime/system PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tegra20-sflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tegra20-slink.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-tegra20-slink.c

## Purpose
NVIDIA Tegra20/Tegra30 SLINK SPI controller driver with CPOL/CPHA/CS_HIGH, packed 8/16-bit mode, CPU FIFO transfers, DMA through coherent bounce buffers, and Tegra30 CS hold capability.

## Important APIs, Types, And Functions
`struct tegra_slink_data` holds controller, SoC chip data, clock/reset/MMIO/IRQ, DMA channels/buffers, completions, packed state, current transfer progress, status fields, and register shadows. Main functions are probe/remove, setup, prepare/unprepare message, transfer callback, FIFO helpers, DMA helpers, and hard/threaded IRQ handlers.

## Control Flow
Probe initializes OPP/clock/reset/MMIO, allocates DMA resources, enables runtime PM, resets hardware, requests a threaded IRQ, writes default registers, and registers the host. Setup updates CS polarity. Prepare-message programs software CS and mode. Each transfer computes packing, writes command2 before command to avoid CS spikes, chooses DMA for more than 32 FIFO words, and lets the threaded IRQ continue chunks until completion.

## State And Persistence
Register shadows are maintained for command and DMA state. Runtime PM gates clock after readback; system resume restores command registers. DMA buffers live for the device lifetime.

## Dependencies And Integration Points
SPI core, OF compatibles `nvidia,tegra20-slink` and `nvidia,tegra30-slink`, Tegra OPP helper, clk/reset, DMAengine, runtime PM, IRQ threading, and MMIO.

## Risks
Packed/unpacked accounting and DMA length rounding are sensitive. Probe fails if DMA resources are unavailable. One DMA error branch appears to assert reset twice without deasserting, requiring validation. Command ordering is important for chip-select stability.

## Test Signals
Tegra20/Tegra30 match data, packed 8/16-bit transfers, unpacked word sizes, FIFO/DMA boundaries, CS_HIGH and `cs_change`, OPP clock changes, DMA errors/timeouts, suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tegra20-slink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tegra210-quad.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-tegra210-quad.c

## Purpose
NVIDIA Tegra QSPI host driver for Tegra210/186/194/234/241. It supports half-duplex single/dual/quad transfers, PIO and DMA, external or internal DMA modes, combined command/address/dummy/data sequences, optional TPM flow support, OF/ACPI matching, and runtime PM.

## Important APIs, Types, And Functions
`struct tegra_qspi` stores controller, lock, clock/MMIO/IRQ, DMA channels/buffers, transfer progress, packed state, register shadows, completions, dummy cycles, and SoC data. `struct tegra_qspi_soc_data` records combined-sequence, TPM, DMA, and CS-count capabilities. Main functions include probe/remove/setup, `tegra_qspi_transfer_one_message()`, combined/non-combined transfer paths, validation, transfer setup/start, FIFO/DMA helpers, timeout handling, and IRQ thread.

## Control Flow
Probe applies OF/ACPI match data, maps registers, gets IRQ/clock, initializes DMA or PIO fallback, enables runtime PM autosuspend, resets hardware, requests a threaded IRQ, and registers. Message handling chooses combined sequence for supported command/address/dummy/data layouts or non-combined mode otherwise. Transfers program mode, CS, tap delays, bus width, dummy cycles, flush FIFOs, then use DMA for large chunks when available or PIO for smaller chunks. The IRQ thread handles real and delayed completions, error bits, chunk continuation, and DMA completion waiting.

## State And Persistence
Register shadows, dummy cycles, active transfer pointers, and DMA buffers are runtime-only. Runtime PM gates the QSPI clock except on ACPI systems. Resume restores command registers. No durable storage.

## Dependencies And Integration Points
SPI core, OF/ACPI platform matching, clk, generic `device_reset()`, runtime PM, DMAengine, DMA mapping, MMIO polling, threaded IRQs, and device properties. Supports several Tegra QSPI compatibles and ACPI IDs.

## Risks
Combined-sequence validation must match actual SPI memory/TPM command shapes. External DMA and internal DMA address paths differ by SoC. Packed DMA maps client buffers directly; unpacked mode uses bounce buffers. Timeout recovery can complete a transfer when hardware is ready but IRQ was delayed, which needs race testing. Some macros expand lowercase names despite uppercase formal parameters and should be checked by build coverage.

## Test Signals
Combined and non-combined SPI memory sequences, TPM flow, single/dual/quad widths, packed word sizes, FIFO/DMA thresholds, external/internal DMA SoCs, IOMMU-disabled fallback, OF/ACPI probe, delayed IRQ timeout recovery, real timeout cleanup, suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tegra210-quad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-test.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-test.h

## Purpose
Shared SPI test definitions header. It describes test cases, buffer sentinels, fill modes, iteration lengths, and runner prototypes for SPI controller/device test code.

## Important APIs, Types, And Functions
`struct spi_test` contains a description, template `spi_message`, up to four transfers, optional run/execute callbacks, expected return, length/alignment iteration controls, fill option/pattern, and elapsed time. Prototypes are `spi_test_run_test()`, `spi_test_execute_msg()`, and `spi_test_run_tests()`.

## Control Flow
The header has no executable flow. Consumers instantiate `struct spi_test` arrays, translate `RX()`/`TX()` sentinel pointers, fill buffers, iterate lengths/alignments, execute messages, and compare outcomes.

## State And Persistence
State is per test object; no global mutable state or persistent storage.

## Dependencies And Integration Points
Depends on `linux/spi/spi.h` and integrates SPI self-test definitions with SPI devices/controllers.

## Risks
High-bit pointer sentinels must never be dereferenced before translation. Iteration arrays rely on `-1` sentinels. Fill modes are numeric macros. Maximum test size is large enough to stress DMA and memory.

## Test Signals
Expected returns, guard-pattern integrity, filled RX regions, elapsed-time measurements, and boundary lengths around FIFO/DMA/page/alignment behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ti-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-ti-qspi.c

## Purpose
TI DRA7xx/AM4372 QSPI controller driver. It supports ordinary half-duplex SPI transfers, dual/quad reads, runtime PM clock restore, `spi-mem` memory-mapped reads, and optional DMA memcpy from the mmap window.

## Important APIs, Types, And Functions
`struct ti_qspi` stores completion, transfer mutex, host, MMIO/mmap windows, syscon CS regmap, clock, saved clock context, DMA channel/bounce buffer, command/control shadows, and mmap state. Main functions are probe/remove/setup, `ti_qspi_start_transfer_one()`, `ti_qspi_exec_mem_op()`, `ti_qspi_adjust_op_size()`, read/write message helpers, mmap enable/disable/setup, and DMA copy helpers.

## Control Flow
Probe maps controller and optional mmap resources, resolves syscon chip-selects, enables runtime PM, optionally allocates DMA_MEMCPY and bounce buffer, maps mmap window for PIO fallback, and registers. Ordinary messages set polarity/phase and frame length, disable mmap if active, process writes/reads with polling, invalidate command state, and finalize. `spi-mem` reads inside the mmap window enable memory-map mode, program opcode/address/dummy/bus width, then DMA-copy or `memcpy_fromio()` data.

## State And Persistence
Clock-control context is cached and restored on runtime resume. `mmap_enabled` and `current_cs` track shared memory-map state. No durable state.

## Dependencies And Integration Points
SPI core, `spi-mem`, OF, clk, runtime PM, regmap/syscon, DMAengine, scatterlist/DMA mapping, MMIO. Compatibles are `ti,dra7xxx-qspi` and `ti,am4372-qspi`.

## Risks
Only read operations use `spi-mem` optimization. Polling status bits can timeout. DMA timeout scales with transfer length. Mmap state must be disabled before ordinary transfers. The IRQ resource is requested but not used for completion in this code.

## Test Signals
8/16/32-bit transfers, 16-byte optimized reads/writes, dual/quad reads, frame cap, mmap in/out-of-window behavior, DMA SG and bounce paths, PIO fallback, syscon CS switching, runtime resume, busy/write/read timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ti-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tle62x0.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-tle62x0.c

## Purpose
SPI client driver for Infineon TLE62x0 output driver chips. It exposes output bits and diagnostics through sysfs attributes using platform data for output count and initial state.

## Important APIs, Types, And Functions
`struct tle62x0_state` stores the SPI device, mutex, output count, cached output state, and TX/RX buffers. Main functions are `tle62x0_write()`, `tle62x0_read()`, `decode_fault()`, sysfs show/store handlers, `to_gpio_num()`, probe, and remove.

## Control Flow
Probe requires platform data, allocates state, creates status and per-output sysfs files, and stores driver data. Status read performs a SPI diagnostic read and decodes two-bit fault codes. GPIO read returns cached state. GPIO write parses input, updates the cached bit, sends `CMD_SET`, and returns input length.

## State And Persistence
`gpio_state` is cached in memory and not written at probe because the initial write is commented out. Diagnostics are read live. Sysfs files are dynamic and removed on unload. No persistent storage.

## Dependencies And Integration Points
SPI client core, sysfs device attributes, platform data from `linux/spi/tle62x0.h`, mutexes, and `module_spi_driver()`.

## Risks
Legacy platform data and permissions are used. `gpio_count` is not validated against 16 attributes. `to_gpio_num()` can return `-1`. GPIO writes ignore SPI write errors. Initial state may not reach hardware.

## Test Signals
8/16-output platform data, sysfs lifecycle, bit writes and reads, SPI frame length/order, diagnostic decoding, invalid input, SPI read error propagation, partial creation cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-tle62x0.c -->
