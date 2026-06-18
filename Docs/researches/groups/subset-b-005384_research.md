# Research: subset-b-005384

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-lantiq-ssc.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-lantiq-ssc.c

## Purpose

`spi-lantiq-ssc.c` is the SPI host-controller driver for Lantiq SSC and Intel LGM SSC hardware. It registers a platform SPI controller, maps SSC registers, configures clocks/FIFOs/interrupts/chip-selects, and moves SPI transfers through the hardware TX/RX FIFOs.

## Important APIs, Types, And Functions

The key state is `struct lantiq_ssc_spi`, which stores the SPI controller, MMIO base, gate/FPI clocks, hardware-variant config, FIFO sizes, current buffers, byte counters, speed, bits-per-word, and an ordered workqueue. `struct lantiq_ssc_hwcfg` abstracts SoC differences in interrupt wiring, IRQ status/ack registers, FIFO masks, and RX/TX interrupt bits.

Core helpers are register accessors, FIFO level/free/reset/flush helpers, `hw_setup_speed_hz()`, `hw_setup_bits_per_word()`, `hw_setup_clock_mode()`, `lantiq_ssc_hw_init()`, and `hw_setup_transfer()`. SPI framework hooks are `lantiq_ssc_setup()`, `lantiq_ssc_set_cs()`, `lantiq_ssc_prepare_message()`, `lantiq_ssc_unprepare_message()`, `lantiq_ssc_transfer_one()`, and `lantiq_ssc_handle_err()`. Interrupt paths are `lantiq_ssc_xmit_interrupt()`, `lantiq_ssc_err_interrupt()`, and `intel_lgm_ssc_isr()`.

## Control Flow, State, And Persistence

Probe selects hardware data from OF, allocates a controller, maps MMIO, requests variant-specific IRQs, enables clocks, reads FIFO sizes from the ID register, initializes FIFOs and controller state, then registers the SPI host. Each message enters config mode to update CPOL/CPHA/LSB/loopback and returns to active mode. Each transfer reprograms speed/word size only when cached values differ, then enables TX and/or RX.

Transfers are interrupt-driven. TX buffers initially fill the TX FIFO; RX-only transfers write `RXREQ` chunks sized to avoid FIFO overflow. Full-duplex reads wait for the expected RX fill corresponding to the last TX fill, while half-duplex RX handles the controller's 32-bit receive behavior and final partial bytes through `STAT.RXBV`. Completion is deferred to `lantiq_ssc_bussy_work()`, which waits for the hardware busy flag to clear before calling `spi_finalize_current_transfer()`.

Persistent runtime state is hardware register state plus cached transfer settings and in-flight pointers/counters protected by a spinlock. There is no disk persistence.

## Dependencies And Integration Points

The file depends on Linux platform/OF, clock, interrupt, workqueue, PM runtime headers, and SPI core. It supports compatibles `lantiq,ase-spi`, `lantiq,falcon-spi`, `lantiq,xrx100-spi`, and `intel,lgm-spi`; legacy Lantiq builds can use `clk_get_fpi()`. Internal chip-selects use SSC GPO registers, while GPIO chip-selects are delegated through SPI core descriptors.

## Risks And Test Signals

Risks include busy-waiting in the full-duplex RX path, subtle RX-only partial-byte handling, FIFO overflow at high clocks if `RXREQ` sizing is wrong, and timeout sensitivity in the final busy-bit work item. The Intel LGM IRQ-ack path differs from older Lantiq variants and needs separate coverage. Test signals include SPI loopback, TX-only/RX-only/full-duplex transfers at 8/16/32 bpw, GPIO and internal CS polarity tests, high-clock FIFO stress, injected error IRQs, and remove/probe clock and workqueue cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-lantiq-ssc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ljca.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-ljca.c

## Purpose

`spi-ljca.c` exposes the Intel La Jolla Cove Adapter USB-SPI function as a Linux SPI controller on the auxiliary bus. It translates SPI transfers into LJCA USB protocol commands.

## Important APIs, Types, And Functions

`struct ljca_spi_dev` holds the LJCA client, SPI controller, LJCA SPI descriptor, cached speed/mode, and fixed 60-byte input/output protocol buffers. Protocol structures are `ljca_spi_init_packet` and `ljca_spi_xfer_packet`; commands include init, read, write, write-read, and deinit.

Important functions are `ljca_spi_read_write()`, `ljca_spi_init()`, `ljca_spi_deinit()`, `ljca_spi_transfer()`, `ljca_spi_transfer_one()`, `ljca_spi_probe()`, remove, and system suspend/resume wrappers.

## Control Flow, State, And Persistence

Probe allocates an SPI host, stores LJCA platform data, sets mode support to CPOL/CPHA, chooses a 48 MHz max clock, and registers the controller. For each transfer, the driver computes a LJCA divider from requested speed, initializes the bridge if speed or mode changed, then splits the transfer into chunks no larger than `LJCA_SPI_MAX_XFER_SIZE`. Each chunk carries an indicator containing sequence id, completion flag, and adapter SPI index.

State is limited to cached mode/speed and the stack of chunked transfers through fixed buffers. There is no persistent storage; remove unregisters the controller and sends LJCA deinit.

## Dependencies And Integration Points

The driver depends on `linux/auxiliary_bus.h`, SPI core, and `linux/usb/ljca.h`. It imports the `LJCA` namespace and binds to `usb_ljca.ljca-spi`. Runtime PM is not used for transfers; system sleep calls suspend/resume the SPI controller.

## Risks And Test Signals

Risks include protocol-size limits, unvalidated returned packet lengths beyond the minimum packet header, mode/speed caching errors across devices, and divider clamping to the bridge's minimum speed enum. Test with long transfers crossing the 60-byte packet boundary, read-only/write-only/full-duplex transfers, all four SPI modes, suspend/resume, and disconnect during transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ljca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-lm70llp.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-lm70llp.c

## Purpose

`spi-lm70llp.c` is a parport-backed SPI bitbang host for the National Semiconductor/TI LM70EVAL-LLP temperature-sensor evaluation board. It creates an SPI controller and instantiates an `lm70` SPI device for the hwmon LM70 protocol driver.

## Important APIs, Types, And Functions

`struct spi_lm70llp` wraps `struct spi_bitbang`, the parallel port/device, the created LM70 SPI device, and board info. Low-level board helpers manipulate parport data/status bits: `assertCS()`, `deassertCS()`, `clkHigh()`, `clkLow()`, `setsck()`, `setmosi()`, and `getmiso()`. SPI bitbang integration is through `lm70_chipselect()` and `lm70_txrx()`. Parport lifecycle is `spi_lm70llp_attach()` and `spi_lm70llp_detach()`.

## Control Flow, State, And Persistence

The parport driver claims one exclusive global instance. Attach allocates an SPI host, configures `spi_bitbang` for SPI mode 0 and 3-wire operation, registers and claims the parport device, starts bitbang, powers the board through data pins, and creates the child `lm70` device. Detach stops bitbang, powers down the board, releases/unregisters parport resources, and releases the host.

Runtime state is primarily physical parport output levels and the global `lm70llp` pointer enforcing exclusivity. No persistent storage is used.

## Dependencies And Integration Points

The file depends on Linux parport, SPI core, and `spi_bitbang`; it includes `spi-bitbang-txrx.h` for the CPHA0 big-endian bitbang routine. It integrates with the hwmon `lm70` SPI protocol driver through `spi_new_device()` and matching modalias.

## Risks And Test Signals

Risks include the intentionally incomplete `setmosi()` path, board-specific inverted MISO wiring, global singleton behavior, lack of actual LM70 detection, and parport timing delays. Test signals are successful parport exclusive claim, child `lm70` bind, plausible temperature reads, detach/reload cleanup, and logic-analyzer confirmation of CS/SCLK/SIO behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-lm70llp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-core.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-core.c

## Purpose

`spi-loongson-core.c` implements the shared Loongson SPI controller logic used by both PCI and platform frontends. It registers the SPI controller, performs byte-at-a-time FIFO transfers, manages chip-selects, mode, clock dividers, and suspend/resume state.

## Important APIs, Types, And Functions

The shared state is `struct loongson_spi` from `spi-loongson.h`. Core helpers are `loongson_spi_write_reg()`, `loongson_spi_read_reg()`, `loongson_spi_set_cs()`, `loongson_spi_set_clk()`, `loongson_spi_set_mode()`, `loongson_spi_update_state()`, `loongson_spi_write_read_8bit()`, `loongson_spi_write_read()`, and `loongson_spi_reginit()`. Exported entry points are `loongson_spi_init_controller()` and `loongson_spi_dev_pm_ops`.

## Control Flow, State, And Persistence

Frontends pass a mapped register base to `loongson_spi_init_controller()`. The core allocates a devm SPI host, sets mode/setup/prepare/transfer/unprepare/set_cs hooks, reads an optional clock, initializes the hardware, and registers the controller. Message preparation saves and clears `PARA.MEM_EN`; unprepare restores it, keeping SPI transfers from colliding with memory-style controller mode. Transfers update speed/mode if cached values differ, then loop one byte at a time by writing FIFO, polling `SPSR.RFEMPTY` with a 1 ms timeout, and reading FIFO.

Suspend stores SPCR/SPER/SPSR/PARA/SFCS/TIMI and resumes by restoring them before resuming the controller. This is volatile hardware state only.

## Dependencies And Integration Points

The core depends on SPI core, clocks, MMIO byte access, and polling helpers. It exports symbols in namespace `SPI_LOONGSON_CORE` for `spi-loongson-pci.c` and `spi-loongson-plat.c`.

## Risks And Test Signals

Risks include byte-at-a-time polling latency, `mode` cache accumulation via OR instead of exact assignment, divider table assumptions, and timeout behavior when RFEMPTY never clears. Test with all SPI modes, CS polarity, multiple chipselects, suspend/resume register restoration, and transfer timeout injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-pci.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-pci.c

## Purpose

`spi-loongson-pci.c` is the PCI glue for Loongson SPI controllers. It enables the PCI device, maps BAR0, and delegates controller registration to the shared Loongson core.

## Important APIs, Types, And Functions

The only substantive function is `loongson_spi_pci_register()`. The driver table matches Loongson PCI IDs `0x7a0b` and `0x7a1b`; the `pci_driver` uses Loongson core PM ops.

## Control Flow, State, And Persistence

Probe uses `pcim_enable_device()`, `pcim_iomap_region()` for BAR0, and `loongson_spi_init_controller()`. Devm/pcim resource management owns cleanup. The file maintains no private runtime state beyond PCI driver binding.

## Dependencies And Integration Points

It depends on PCI core and `spi-loongson.h`, and imports namespace `SPI_LOONGSON_CORE`. Its behavior is entirely coupled to the shared core implementation.

## Risks And Test Signals

Risks are mostly resource binding errors: wrong BAR, missing PCI clock assumptions in core, or ID table gaps. Test by probing both supported PCI IDs, unbind/rebind, suspend/resume through the inherited PM ops, and basic SPI transfer after PCI resource mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-plat.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-plat.c

## Purpose

`spi-loongson-plat.c` is the OF/platform glue for Loongson SPI controllers. It maps the MMIO resource from a platform device and delegates the implementation to the shared Loongson core.

## Important APIs, Types, And Functions

The central function is `loongson_spi_platform_probe()`. The OF match table contains `loongson,ls2k1000-spi`; the platform driver uses `loongson_spi_dev_pm_ops`.

## Control Flow, State, And Persistence

Probe maps resource 0 using `devm_platform_ioremap_resource()` and calls `loongson_spi_init_controller()`. Cleanup is devm-managed. There is no private persistent state.

## Dependencies And Integration Points

This file depends on platform device and OF matching infrastructure plus `spi-loongson.h`. It imports namespace `SPI_LOONGSON_CORE` and should be considered a frontend, not an independent controller implementation.

## Risks And Test Signals

Risks include device-tree compatible/resource mistakes and dependency on the shared core's optional clock handling. Test with DT probe, unbind/rebind, runtime transfers, and system suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loongson.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-loongson.h

## Purpose

`spi-loongson.h` defines the private contract between the Loongson SPI core and its PCI/platform frontends. It names controller registers, bit definitions, shared runtime state, and exported core entry points.

## Important APIs, Types, And Functions

Register offsets include SPCR, SPSR, FIFO, SPER, PARA, SFCS, and TIMI. Important bits include `LOONGSON_SPI_PARA_MEM_EN`, CPHA/CPOL/SPE in SPCR, and RFEMPTY/WCOL/SPIF in SPSR. `struct loongson_spi` stores the SPI controller, MMIO base, cached speed/mode/register values, and clock rate. Public declarations are `loongson_spi_init_controller()` and `loongson_spi_dev_pm_ops`.

## Control Flow, State, And Persistence

The header has no runtime flow. Its structure fields define the volatile state saved across suspend/resume and the cached mode/speed data used by the core transfer path.

## Dependencies And Integration Points

It includes Linux bits, PM, and type headers, and forward-declares `struct device` and `struct spi_controller`. Both Loongson frontend drivers include it and rely on the exported namespace from the core.

## Risks And Test Signals

Risks are ABI drift within the Loongson mini-driver set: register offsets or cached fields must remain consistent with core suspend/resume and transfer code. Compile all three Loongson files together and test probe through both PCI and platform frontends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loongson.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loopback-test.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-loopback-test.c

## Purpose

`spi-loopback-test.c` is a SPI protocol test driver and reusable test helper implementation. It runs a table of synthetic SPI messages against a target device, optionally requiring physical/controller loopback, to validate controller behavior around transfer lengths, alignment, CS handling, delays, DMA-like boundaries, and RX/TX buffer integrity.

## Important APIs, Types, And Functions

The module parameters control simulation, message dumps, loopback checking, requested `SPI_LOOP`, `SPI_NO_CS`, test/length filtering, vmalloc buffers, range checking, and inter-test delay. The static `spi_tests[]` table defines one-, two-, and three-transfer cases with TX-only, RX-only, full-duplex, page-boundary, overlapping-cacheline, alignment, and delay scenarios.

The driver probe is `spi_loopback_test_probe()`. Exported helpers are `spi_test_execute_msg()`, `spi_test_run_test()`, and `spi_test_run_tests()`. Internal helpers translate symbolic TX/RX offsets into allocated buffers, fill data patterns, dump messages, check modified RX ranges, verify loopback data, and enforce elapsed-time lower bounds.

## Control Flow, State, And Persistence

Probe optionally changes the SPI device mode, then calls `spi_test_run_tests()`. That allocates large TX/RX buffers with `kzalloc()` or `vmalloc()`, iterates the test array, clones each template, expands length/alignment combinations, translates pseudo-pointers, fills TX/RX patterns, executes via `spi_sync()` unless simulating, and validates results. A timed-out message is retried after scheduling.

State is per-run test data and module parameters. The file has no persistent storage, but it exports helpers for other in-kernel SPI tests.

## Dependencies And Integration Points

It depends on SPI core and local `spi-test.h`. It binds by OF compatible `linux,spi-loopback-test`, with a module parameter allowing compatible override. It is a consumer/test driver, not a controller.

## Risks And Test Signals

Risks include destructive runtime cost on real devices, false failures without actual loopback, pointer-template mutation if a copied test is not used correctly, and very verbose logs on dump/error paths. Useful signals are successful completion across controllers, failures pinpointing actual length mismatches, RX writes outside expected ranges, loopback byte mismatches, and elapsed time shorter than physical transfer minimums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-loopback-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-lp8841-rtc.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-lp8841-rtc.c

## Purpose

`spi-lp8841-rtc.c` is a minimal platform SPI host for the ICP DAS LP-8841 RTC wiring. It bitbangs a DS1302-like 3-wire, LSB-first, active-high chip-select bus through an MMIO byte register.

## Important APIs, Types, And Functions

`struct spi_lp8841_rtc` stores the mapped I/O byte and current output state. Helpers `setsck()`, `setmosi()`, and `getmiso()` manipulate CLK/MOSI/MISO bits. `bitbang_txrx_be_cpha0_lsb()` clocks one LSB-first word. SPI hooks are `spi_lp8841_rtc_setup()`, `spi_lp8841_rtc_set_cs()`, and `spi_lp8841_rtc_transfer_one()`.

## Control Flow, State, And Persistence

Probe allocates a host, sets half-duplex flags, supports only `SPI_CS_HIGH | SPI_3WIRE | SPI_LSB_FIRST`, maps MMIO, and registers the controller. Setup rejects unsupported active-low, MSB-first, or non-3-wire clients. Transfers are either TX-only or RX-only; TX clears nWE and clocks bytes out, RX sets nWE and clocks bytes in. Each transfer finalizes synchronously.

Runtime state is just the output bit shadow and MMIO register. No persistent storage is used.

## Dependencies And Integration Points

The driver depends on platform/OF, MMIO, delay helpers, and SPI core. It matches `icpdas,lp8841-spi-rtc` and is intended to host an RTC protocol device above it.

## Risks And Test Signals

Risks include strict mode limitations, busy sleep timing, synchronous finalize semantics, and no support for simultaneous TX/RX buffers. Test with the RTC client using read/write register operations, mode rejection tests, CS timing on a scope, and unbind/rebind resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-lp8841-rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mem.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mem.c

## Purpose

`spi-mem.c` implements the SPI memory framework used by NOR/NAND/EEPROM-style devices. It validates memory operations, chooses controller-optimized `mem_ops` when available, provides SPI-message fallback execution, direct-map helpers, status polling, operation sizing/frequency helpers, DMA-map helpers, statistics, tracing, and SPI-memory driver registration wrappers.

## Important APIs, Types, And Functions

Exported APIs include `spi_controller_dma_map_mem_op_data()`, `spi_controller_dma_unmap_mem_op_data()`, `spi_mem_default_supports_op()`, `spi_mem_supports_op()`, `spi_mem_exec_op()`, `spi_mem_adjust_op_size()`, `spi_mem_adjust_op_freq()`, `spi_mem_calc_op_duration()`, direct-map create/destroy/read/write devm and non-devm variants, `spi_mem_poll_status()`, and SPI-mem driver register/unregister functions.

Internal validation covers command/address/dummy/data bus widths, DTR constraints, ECC and swap16 capabilities, per-operation frequency support, and stack-buffer rejection for DMA-able data buffers.

## Control Flow, State, And Persistence

`spi_mem_exec_op()` adjusts frequency, validates the op, checks support, and first attempts controller `mem_ops->exec_op()` under queue flush, runtime PM, bus lock, and IO mutex when no GPIO CS blocks optimized access. If unsupported, it allocates a DMA-able command/address/dummy buffer, builds up to four `spi_transfer` entries, runs `spi_sync()`, and verifies actual length.

Direct maps store a `spi_mem_dirmap_desc`; if controller dirmap creation fails but the template op is supported, the descriptor falls back to repeated `spi_mem_exec_op()`. Status polling uses controller `poll_status()` when available, otherwise read-polls an input op. State is allocated descriptor/driver data and per-CPU SPI statistics; no disk persistence exists.

## Dependencies And Integration Points

The file integrates SPI core internals, runtime PM, DMA mapping, tracepoints, `spi_controller_mem_ops`, `spi_mem_driver`, and upper-layer memory drivers. It is central framework code, so many controller drivers in this subset, especially Microchip CoreQSPI, plug into it through `mem_ops`.

## Risks And Test Signals

Risks include accepting unsupported bus-width/DTR combinations, using non-DMA-safe buffers, lock ordering around direct optimized ops, GPIO-CS incompatibility with controller-native mem ops, and fallback message length mistakes. Test with spi-nor/spi-nand operations across single/dual/quad/octal and DTR variants, stack-buffer warnings, direct-map fallback, per-op frequency limits, status polling timeouts, and statistics/tracepoint validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-meson-spicc.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-meson-spicc.c

## Purpose

`spi-meson-spicc.c` is the Amlogic Meson SPICC SPI host driver. It supports GX/AXG/G12A controller variants, interrupt-driven PIO transfers, a special 64-bit-word DMA path, clock-divider registration, pinctrl idle handling, loopback, and GPIO chip-select descriptors.

## Important APIs, Types, And Functions

`struct meson_spicc_data` describes variant limits and features; `struct meson_spicc_device` stores host, MMIO, clocks, completion, current message/transfer, buffer pointers, counters, pinctrl states, DMA addresses, and DMA mode flag. Transfer functions include `meson_spicc_setup_xfer()`, `meson_spicc_setup_burst()`, `meson_spicc_tx()`, `meson_spicc_rx()`, `meson_spicc_irq()`, `meson_spicc_transfer_one()`, and DMA helpers `meson_spicc_dma_map()`, `meson_spicc_calc_dma_len()`, `meson_spicc_setup_dma()`, and `meson_spicc_dma_irq()`.

## Control Flow, State, And Persistence

Probe maps MMIO, requests IRQ, enables clocks, gets pinctrl, resets hardware, configures SPI host hooks, registers derived clock dividers, and registers the controller. Message preparation programs master/mode/CS/ready/loopback fields and idle pinctrl. Each transfer sets word width and clock, resets FIFOs, initializes completion, computes timeout, then either starts PIO bursts or the 64-bit DMA path. IRQs drain RX, start the next burst, or complete. Unprepare disables IRQs, resets hardware, and restores pinctrl.

State is volatile hardware register configuration, derived clock providers tied to controller state, and in-flight counters. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on platform/OF, clocks/clk-provider, reset, pinctrl, DMA mapping, IRQs, and SPI core. OF data selects `amlogic,meson-gx-spicc`, `amlogic,meson-axg-spicc`, or `amlogic,meson-g12a-spicc`.

## Risks And Test Signals

Risks include DMA-map error cleanup after partial mapping, timeout estimation, FIFO reset/clock-output interactions, 64-bit DMA alignment/length constraints, and clock providers refusing operations when no message is active. Test PIO at 8/16/24/32 bpw, DMA at 64 bpw and split bursts, loopback, CPOL idle pinctrl states, all variants, timeout/error paths, and remove disabling SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-meson-spicc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-meson-spifc.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-meson-spifc.c

## Purpose

`spi-meson-spifc.c` is the Amlogic Meson SPI flash controller driver. It exposes a single-chipselect, 8-bit SPI host that transfers data through the controller's 64-byte internal command/data buffer and manages its clock with runtime PM.

## Important APIs, Types, And Functions

`struct meson_spifc` stores the SPI host, regmap, input clock, and device. Key functions are `meson_spifc_wait_ready()`, `meson_spifc_drain_buffer()`, `meson_spifc_fill_buffer()`, `meson_spifc_setup_speed()`, `meson_spifc_txrx()`, `meson_spifc_transfer_one()`, `meson_spifc_hw_init()`, probe/remove, and system/runtime PM hooks.

## Control Flow, State, And Persistence

Probe allocates a host, initializes an MMIO regmap, enables the clock, sets 8-bit-only transfer support and min/max speeds from the clock, resets the hardware, enables runtime PM, and registers the controller. A transfer programs the divider, disables AHB mode, splits the transfer into up to 64-byte chunks, fills the buffer for TX, configures DOUT and DIN stages, handles CS continuation according to transfer/message boundaries, starts the user command, waits up to 5 ms for `SLAVE_TRST_DONE`, drains RX if needed, and finally re-enables AHB mode.

State is volatile controller registers and runtime PM clock state. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on platform/OF, regmap MMIO, clocks, runtime PM, and SPI core. It matches `amlogic,meson6-spifc` and `amlogic,meson-gxbb-spifc`.

## Risks And Test Signals

Risks include unaligned `u32 *` buffer accesses, chunked CS-change semantics, fixed 5 ms ready timeout, and clock disable/enable ordering across system and runtime PM. Test flash reads/writes spanning 64-byte chunks, TX/RX/full-duplex transfers, CS-change cases, runtime suspend/resume, and ready-timeout injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-meson-spifc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-microchip-core-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-microchip-core-qspi.c

## Purpose

`spi-microchip-core-qspi.c` drives the Microchip coreQSPI controller. It supports regular SPI transfers plus optimized `spi-mem` operations for SPI flash, including single/dual/quad modes, software chip-select control, command/data frame programming, and interrupt completion.

## Important APIs, Types, And Functions

`struct mchp_coreqspi` stores MMIO, clock, completion, operation mutex, current TX/RX buffers and lengths, and IRQ. Important helpers are `mchp_coreqspi_set_mode()`, `mchp_coreqspi_set_cs()`, `mchp_coreqspi_setup_clock()`, `mchp_coreqspi_config_op()`, FIFO routines for read/write/write-read, `mchp_coreqspi_isr()`, and `mchp_coreqspi_wait_for_ready()`. `spi-mem` integration is `mchp_coreqspi_exec_op()`, `mchp_coreqspi_supports_op()`, and `mchp_coreqspi_adjust_op_size()`.

## Control Flow, State, And Persistence

Probe maps registers, enables the clock, initializes completion/mutex, requests a shared IRQ, configures chip-select count, advertises SPI memory caps, enables master/controller mode, puts CS into software direct mode, and registers the controller. Memory ops lock the device, wait ready, configure per-op clock and line mode, program frame counts and dummy cycles, assert CS, push opcode/address/data or prepare RX, enable interrupts, wait for completion, then deassert CS and disable interrupts. Regular SPI messages use prepare/unprepare to lock, configure frames over all transfers, apply dual/quad mode, and add a required 750 us unprepare delay.

State is volatile register configuration plus serialized in-flight buffer pointers. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on platform/OF, clocks, interrupts, MMIO polling, SPI core, and `spi-mem`. It matches `microchip,coreqspi-rtl-v2` and advertises per-operation frequency support.

## Risks And Test Signals

Risks include busy-wait FIFO loops, unaligned word accesses, complex frame accounting, unsupported quad-write extended-read-only cases, and mutex/IRQ completion paths that can leave CS asserted on error. Test with spi-nor command negotiation, dual/quad reads, rejected quad program ops, regular `spi_sync()` transfers, transfers above 256 bytes through adjusted op size, timeout/IRQ loss, and CS polarity/GPIO CS combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-microchip-core-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-microchip-core-spi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-microchip-core-spi.c

## Purpose

`spi-microchip-core-spi.c` is the Microchip CoreSPI controller driver for the RTL v5 IP. It implements Motorola-mode SPI transfers through a small byte FIFO, with polling for normal data movement and interrupts for overflow/underflow error reporting.

## Important APIs, Types, And Functions

`struct mchp_corespi` stores MMIO, clock, current TX/RX buffers and lengths, divider, IRQ, and FIFO depth. Main functions are `mchp_corespi_init()`, `mchp_corespi_set_clk_div()`, `mchp_corespi_write_fifo()`, `mchp_corespi_read_fifo()`, `mchp_corespi_transfer_one()`, `mchp_corespi_setup()`, `mchp_corespi_set_cs()`, and `mchp_corespi_interrupt()`.

## Control Flow, State, And Persistence

Probe validates device-tree configuration: only Motorola protocol is supported, mode is fixed by hardware configuration, frame size must be 8, and `microchip,ssel-active` must be enabled to keep CS asserted through a transfer. It maps registers, requests IRQ, enables clock, initializes master mode and interrupts, and registers the host. Each transfer sets the divider, assigns buffers, writes up to FIFO depth bytes, reads the same count back, and loops until all bytes have been clocked. It finalizes synchronously and returns `1` to indicate completion was already handled.

State is volatile hardware configuration and current buffer pointers. No persistent storage exists.

## Dependencies And Integration Points

The file depends on platform/OF properties, clocks, IRQs, MMIO byte access, and SPI core. It matches `microchip,corespi-rtl-v5` and uses GPIO descriptors when chip-selects are GPIO-backed.

## Risks And Test Signals

Risks include reliance on polling loops without data timeout, mismatch between fixed hardware Motorola mode and device mode, active-high CS rejection for native CS, and only 8-bit actual data handling despite a broader bits-per-word mask. Test DT validation failures, mode mismatch rejection, TX/RX/full-duplex transfers, FIFO-depth variations, overflow/underflow IRQ injection, and unbind disabling controller/interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-microchip-core-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mpc512x-psc.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mpc512x-psc.c

## Purpose

`spi-mpc512x-psc.c` drives Freescale MPC5121/MPC5125 PSC blocks configured in SPI mode. It adapts two PSC register layouts, controls PSC FIFO slices, and implements message-level transfers with GPIO chip-select support.

## Important APIs, Types, And Functions

`struct mpc512x_psc_spi` stores the PSC type, PSC/FIFO MMIO bases, IRQ, current bits-per-word, master clock rate, and a TX-empty completion. `struct mpc512x_psc_spi_cs` caches per-device bits-per-word and speed. Key functions are `mpc512x_psc_spi_transfer_setup()`, `mpc512x_psc_spi_activate_cs()`, `mpc512x_psc_spi_transfer_rxtx()`, `mpc512x_psc_spi_msg_xfer()`, hardware prep/unprep hooks, `mpc512x_psc_spi_port_config()`, and `mpc512x_psc_spi_isr()`.

## Control Flow, State, And Persistence

Probe selects MPC5121 or MPC5125 layout from OF data, maps PSC/FIFO registers, requests IRQ, enables `mclk` and `ipg`, configures PSC SPI master mode and FIFO slices, and registers the controller. Message transfer iterates transfers, updates speed/word size, asserts CS when needed, sends chunks limited by TX and RX FIFO space, waits for TX FIFO empty interrupt, drains RX with bounded retries, updates actual length, handles delays and CS changes, then finalizes the message.

State consists of PSC/FIFO registers, per-device controller state allocated in setup, and completion-based wait state. No persistent storage exists.

## Dependencies And Integration Points

The file depends on PowerPC MPC52xx PSC definitions, platform/OF, clocks, GPIO descriptors through SPI core, completions, and SPI core. It matches `fsl,mpc5121-psc-spi` and `fsl,mpc5125-psc-spi`.

## Risks And Test Signals

Risks include PSC layout macro mistakes, FIFO size/rxcnt arithmetic, indefinite wait for TX-empty completion, arbitrary RX retry timeout, and EOF/CS-change handling. Test on both PSC variants, low-speed RX completion, TX-only/RX-only/full-duplex, GPIO CS with `cs_change`, clock divider limits, and IRQ loss/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mpc512x-psc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mpc52xx-psc.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mpc52xx-psc.c

## Purpose

`spi-mpc52xx-psc.c` drives the MPC52xx PSC peripheral when configured as SPI. It is distinct from the dedicated MPC52xx SPI controller driver and uses PSC FIFO alarms plus completions to move bytes.

## Important APIs, Types, And Functions

`struct mpc52xx_psc_spi` stores PSC/FIFO MMIO, IRQ, current bits-per-word, and RX completion. `struct mpc52xx_psc_spi_cs` caches speed and word size. Main functions are `mpc52xx_psc_spi_transfer_setup()`, `mpc52xx_psc_spi_activate_cs()`, `mpc52xx_psc_spi_transfer_rxtx()`, `mpc52xx_psc_spi_transfer_one_message()`, `mpc52xx_psc_spi_setup()`, `mpc52xx_psc_spi_port_config()`, and `mpc52xx_psc_spi_isr()`.

## Control Flow, State, And Persistence

Probe reads `cell-index`, maps PSC registers, derives FIFO register address, requests IRQ, configures PSC clocking/SPI mode/FIFO behavior, initializes completion, and registers the controller. Message transfer walks each transfer, updates setup when needed, activates CS on the first or changed transfer, writes a block to the PSC buffer, configures RX alarm/RXRDY interrupt, waits for completion, drains available RX bytes, updates actual length, applies transfer delay, and finalizes the message.

State is volatile PSC register configuration, per-device controller state, and the completion used by the ISR. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on PowerPC MPC52xx PSC helpers, platform/OF properties, MMIO, completions, and SPI core. It matches `fsl,mpc5200-psc-spi` and legacy `mpc5200-psc-spi`.

## Risks And Test Signals

Risks include fixed 20 MHz MCLK assumptions, one-byte RX interrupt special cases, completion with no timeout, limited CS handling compared with newer SPI APIs, and FIFO alarm tuning. Test with varying transfer sizes, exactly one byte, larger-than-FIFO transfers, CPOL/CPHA/LSB modes, interrupt loss, and PSC clock divider validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mpc52xx-psc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mpc52xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mpc52xx.c

## Purpose

`spi-mpc52xx.c` drives the dedicated MPC5200 SPI controller, not PSC-SPI mode. It implements a queued message engine around a small byte-oriented controller and a finite-state machine that runs from IRQs or a polling workqueue.

## Important APIs, Types, And Functions

`struct mpc52xx_spi` stores the SPI host, MMIO registers, two IRQs, bus frequency, debug counters, pending message queue, lock/work item, current message/transfer, FSM callback, buffers, CS state, and optional GPIO CS array. FSM handlers are `mpc52xx_spi_fsmstate_idle()`, `mpc52xx_spi_fsmstate_transfer()`, and `mpc52xx_spi_fsmstate_wait()`, driven by `mpc52xx_spi_fsm_process()`, `mpc52xx_spi_irq()`, and `mpc52xx_spi_wq()`.

## Control Flow, State, And Persistence

Probe maps registers, initializes controller pins/registers, checks for mode fault, allocates the host, gets optional GPIO chip-selects, initializes the queue/work/lock, requests MODF and SPIF IRQs when available, otherwise uses polling, and registers the controller. `transfer` queues messages under lock and schedules work. The idle state dequeues a message, programs mode and baud rate, asserts CS, and starts the first byte. Transfer state handles WCOL retry, MODF failure, RX byte storage, next-byte TX, and transition to wait. Wait state honors transfer delay, advances to the next transfer, or completes the message.

State is in-memory queued messages, FSM state, GPIO CS values, and volatile controller registers. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on OF address/IRQ helpers, PowerPC timebase/bus-frequency helpers, GPIO descriptors, workqueues, spinlocks, and SPI core. It matches `fsl,mpc5200-spi`.

## Risks And Test Signals

Risks include legacy `host->transfer` queueing, no timeout for queued work, WCOL retry behavior at slow speeds, MODF when pins are misconfigured, and mixed IRQ/poll operation. Test interrupt and polled modes, slow-speed WCOL scenarios, mode-fault detection, GPIO and native CS, transfer delays, multi-transfer messages, and remove while queue/work are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mpc52xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mpfs.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mpfs.c

## Purpose

`spi-mpfs.c` drives the Microchip PolarFire SoC SPI controller. It performs polling-based FIFO transfers, supports 1- to 32-bit words, direct chip-select control, per-transfer clock generation, and interrupt-based overflow/underflow error handling.

## Important APIs, Types, And Functions

`struct mpfs_spi` stores MMIO, clock, current buffers and lengths, divider mode/value, pending slave-select register value, IRQ, and bytes per frame. Important functions are `mpfs_spi_init()`, `mpfs_spi_set_clk_gen()`, `mpfs_spi_calculate_clkgen()`, `mpfs_spi_set_mode()`, `mpfs_spi_set_framesize()`, `mpfs_spi_set_xfer_size()`, FIFO helpers, `mpfs_spi_transfer_one()`, `mpfs_spi_prepare_message()`, `mpfs_spi_set_cs()`, and `mpfs_spi_interrupt()`.

## Control Flow, State, And Persistence

Probe allocates a host, reads `num-cs`, maps registers, requests a shared IRQ, enables the clock, initializes master Motorola mode, BIGFIFO, direct CS mode, interrupts, frame size, and controller enable, then registers the host. Prepare programs CPOL/CPHA with a temporary controller disable. `set_cs()` defers CS assertion in `pending_slave_select` to avoid target-visible glitches while registers requiring disable are changed. Transfer calculates the best clock divider mode, sets frame size, resets FIFOs, writes pending CS, then loops writing and reading FIFO chunks until all frames are complete before finalizing synchronously.

State is volatile register configuration plus cached pending CS and divider values. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on platform/OF, clocks, MMIO, interrupts, and SPI core. It matches `microchip,mpfs-spi`, supports GPIO descriptors, and currently defines no PM ops.

## Risks And Test Signals

Risks include polling loops without timeout, frame-count quirks between CONTROL and FRAMESUP, CS deferral correctness, divider-mode edge cases, alignment/casting for 16/32-bit buffers, and finalization from both error IRQ and transfer path. Test all word sizes, active-high/active-low CS, low/high clock requests, long transfers above 16-bit frame count, overflow/underflow injection, and repeated probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mpfs.c -->
