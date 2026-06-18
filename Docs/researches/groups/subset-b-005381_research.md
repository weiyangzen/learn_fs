# subset-b-005381 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cadence-quadspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-cadence-quadspi.c

## Purpose

`spi-cadence-quadspi.c` is the Cadence QSPI/OSPI `spi-mem` controller driver used by several SoCs, including Cadence generic, TI K2G/AM654, Intel LGM/SoCFPGA, AMD Versal/Versal2/Pensando, StarFive JH7110, Mobileye EyeQ5, and Renesas RZ/N1 variants. It exposes NOR/NAND flash operations through `spi_controller_mem_ops` rather than ordinary message transfers. The driver supports short STIG register commands, indirect SRAM-backed reads and writes, direct AHB-window reads/writes, optional memcpy DMA for mapped reads, and Versal OSPI indirect DMA.

## Important APIs, Types, and Functions

The central state is `struct cqspi_st`, which stores platform resources, clocks, register windows, AHB window, FIFO geometry, IRQ completions, optional DMA channel, runtime PM state, quirk flags, refcounts, current chip-select/clock, and per-CS `struct cqspi_flash_pdata`. `struct cqspi_driver_platdata` binds SoC quirks, capabilities, and optional indirect DMA callbacks.

Key `spi-mem` entry points are `cqspi_exec_mem_op()`, `cqspi_supports_mem_op()`, and `cqspi_get_name()` in `cqspi_mem_ops`. `cqspi_mem_process()` chooses among `cqspi_command_read()`, `cqspi_command_write()`, `cqspi_read()`, and `cqspi_write()`. Read/write setup is handled by `cqspi_read_setup()`, `cqspi_write_setup()`, DTR helpers `cqspi_enable_dtr()` and `cqspi_setup_opcode_ext()`, and controller tuning helpers `cqspi_configure()`, `cqspi_chipselect()`, `cqspi_config_baudrate_div()`, `cqspi_delay()`, and `cqspi_readdata_capture()`.

I/O engines are `cqspi_indirect_read_execute()`, `cqspi_indirect_write_execute()`, `cqspi_direct_read_execute()`, and `cqspi_versal_indirect_read_dma()`. Lifecycle and PM are implemented by `cqspi_probe()`, `cqspi_remove()`, `cqspi_runtime_suspend()`, `cqspi_runtime_resume()`, `cqspi_suspend()`, and `cqspi_resume()`.

## Control Flow

Probe allocates a controller, parses global OF properties, parses each flash child into `f_pdata`, enables clocks, maps the controller and AHB windows, resets optional reset lines, applies matched quirk data, requests the IRQ, detects/configures FIFO depth, initializes the controller, optionally enables runtime PM, requests an optional DMA memcpy channel for direct reads, and registers the SPI controller.

Every memory operation first validates lifetime/refcount state, resumes runtime PM unless the SoC disables it, then calls `cqspi_mem_process()`. That function configures chip-select and clock, then routes small register-style operations through STIG command registers and address-bearing bulk operations through direct, indirect, or DMA paths. Indirect reads/writes program start address and byte count registers, enable interrupt masks, start the indirect engine, drain/fill the SRAM window, wait for completion bits, and cancel on timeout. Direct mode copies through the AHB memory window, with optional DMA memcpy for valid direct-read buffers.

## State and Persistence Behavior

The driver has no file-backed persistence. Persistent effects are flash-visible writes, erase/status commands, reset-pin toggles, and controller register programming. Runtime state persists for the probed controller: FIFO configuration, direct/indirect mode selection, current chip select, current SCLK, optional DMA channel, and refcounts used to block in-flight operations during removal.

Runtime PM disables the controller and clocks on suspend and fully reinitializes controller registers on resume. Remove clears the externally visible refcount, waits for in-flight operations where needed, releases DMA, disables the controller, and disables clocks.

## Dependencies and Integration Points

The file integrates with the Linux `spi-mem` core, platform/OF probing, runtime PM, reset controllers, clock bulk APIs, DMA engine memcpy, DMA mapping, completions, IRQ handling, ZynqMP firmware OSPI mux control for Versal DMA, and memory-mapped I/O accessors. Device-tree child nodes provide chip-select, timing, and maximum-frequency data. SoC compatibility strings select quirk bundles such as disabled DAC mode, slow SRAM, APB/AHB hazard workarounds, no IRQ reads, external DMA, write-protect control, and no indirect mode.

## Risks and Edge Cases

The read/write path has many mode interactions: DTR disables direct write in some cases, write-completion polling is disabled for devices that need status-address/dummy-address phases, and RZ/N1 forbids DTR and indirect mode. Refcount handling is nontrivial: `inflight_ops` starts at 1 and is conditionally decremented only when greater than 1, so lifetime changes need careful review. Indirect read timeouts may still succeed if FIFO bytes are available; the code distinguishes timeout-with-data from timeout-without-data. Direct DMA only works for valid kernel linear buffers; nonvalid buffers fall back to CPU copy. Versal DMA has several cleanup paths that must restore mux, DMA bits, and mappings.

## Test Signals

Build coverage should include multiple compatible strings and DTR support. Runtime validation should exercise STIG reads/writes up to 8 bytes, SDR and 8-8-8 DTR operations, direct AHB reads/writes, indirect read/write, slow-SRAM read, no-IRQ read, RZ/N1 no-indirect mode, Versal DMA with aligned and remainder bytes, timeout/cancel paths, runtime suspend/resume, remove during blocked operations, and flash child parsing errors. Fault injection should cover clock/reset/IRQ/DMA failures and invalid child `reg` or timing properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cadence-quadspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cadence-xspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-cadence-xspi.c

## Purpose

`spi-cadence-xspi.c` is the Cadence XSPI flash controller driver. It primarily implements `spi-mem` STIG command execution with SDMA data movement, plus Marvell CN10 hardware-overlay support for PHY setup, clock programming, 64-bit SDMA FIFO access, and a special generic `transfer_one_message` path.

## Important APIs, Types, and Functions

`struct cdns_xspi_dev` stores the platform device, SPI controller, IO/AUX/SDMA/XFER windows, IRQ, completions, current chip select, SDMA buffers, hardware bank count, Marvell-overlay state, and handler callbacks. `struct cdns_xspi_driver_data` supplies overlay selection and PHY register defaults.

Important functions include `cdns_xspi_controller_init()`, `cdns_xspi_send_stig_command()`, `cdns_xspi_mem_op_execute()`, `marvell_xspi_mem_op_execute()`, `cdns_xspi_supports_op()`, `cdns_xspi_adjust_mem_op_size()`, `cdns_xspi_irq_handler()`, `cdns_xspi_probe()`, and PM callbacks. Marvell-specific helpers include `cdns_mrvl_xspi_setup_clock()`, `cdns_xspi_configure_phy()`, `marvell_xspi_sdma_handle()`, `cdns_xspi_transfer_one_message_b0()`, and generic command packing/readback helpers.

## Control Flow

Probe allocates a host, selects driver data from OF match, assigns standard or Marvell mem ops and handler callbacks, validates child chip-select `reg` values, maps IO/SDMA/AUX and optional XFER resources, requests a shared IRQ, configures Marvell clock/PHY if needed, validates controller magic/features, sets `num_chipselect` from hardware bank count, and registers the controller.

For a `spi-mem` operation, the driver updates `cur_cs`, waits for the controller to become idle, switches to STIG mode, enables interrupts, emits a profile-1 instruction command, optionally emits a data sequence command, waits for SDMA trigger and STIG done completions, drains/fills SDMA through the selected handler, disables interrupts, and checks command status bits for DQS/CRC/bus/sequence errors. The Marvell mem path first reprograms the overlay clock based on the SPI device speed.

The Marvell B0 message path enables an XFER state machine, chunks transfers into up to 32 qwords, uses generic STIG commands for small transfers or a generic command plus SDMA data sequence for larger transfers, reads returned qwords through overlay registers with bit reversal, honors delays, and releases the state machine unless `cs_change` keeps CS active.

## State and Persistence Behavior

The driver maintains volatile controller state only: current CS, SDMA buffer pointers for the active command, completion state, SDMA error flag, Marvell PHY/clock state, and ongoing generic-transfer qword index. Persistent side effects are limited to SPI flash operations and controller/PHY register programming. Suspend stops the SPI controller through `spi_controller_suspend()`. Resume reconfigures Marvell clock/PHY, disables controller interrupts, and resumes the core.

## Dependencies and Integration Points

The file integrates with platform resources named `io`, `sdma`, `aux`, and optionally `xfer`, OF child nodes, Linux `spi-mem`, IRQ completions, MMIO accessors, bitfield helpers, PM sleep callbacks, and the SPI controller framework. Supported compatibles are `cdns,xspi-nor` and `marvell,cn10-xspi-nor`.

## Risks and Edge Cases

The completion objects are not reinitialized before each command, so stale completions would be a concern if a previous command completed before the next wait; IRQ ordering should be reviewed carefully. `cdns_xspi_supports_op()` mutates `spi->mode` while answering support queries under ACPI builds, which can make support probing stateful. `cdns_xspi_adjust_mem_op_size()` clamps all data directions to SDMA size, including no-data operations. The Marvell generic message path decrements `t->len` in-place, which is unusual for SPI transfer descriptors. Busy-wait timeouts are short and may be sensitive to slow firmware/hardware. PHY lock polling appears to read the interrupt status register for `CDNS_XSPI_DLL_LOCK`, so register selection should be checked against the hardware manual.

## Test Signals

Validation should cover standard and Marvell probe, bad magic number, child CS out of range, missing resource fallback by index, IRQ request failure, STIG no-data commands, read/write SDMA commands at SDMA-size boundary, injected SDMA errors, command status failure bits, Marvell clock divisor changes, suspend/resume reinitialization, and B0 generic-message transfers below 10 bytes, above 10 bytes, exact qword multiples, partial qwords, and `cs_change` sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cadence-xspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cadence.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-cadence.c

## Purpose

`spi-cadence.c` is the basic Cadence SPI controller driver for host and target mode controllers such as Xilinx Zynq and compatible `cdns,spi-r1p6` variants. It implements FIFO-driven SPI transfers with interrupt completion, manual chip-select handling in host mode, target abort support, FIFO depth detection, optional reset control, and runtime PM for host mode.

## Important APIs, Types, and Functions

`struct cdns_spi` stores MMIO registers, APB/reference clocks, cached clock rate, current speed, TX/RX buffer pointers and remaining word counts, bytes-per-word, decoded-CS state, detected FIFO depth, and reset control. Main functions are `cdns_spi_init_hw()`, `cdns_spi_chipselect()`, `cdns_spi_config_clock_mode()`, `cdns_spi_config_clock_freq()`, `cdns_spi_process_fifo()`, `cdns_spi_irq()`, `cdns_transfer_one()`, `cdns_prepare_transfer_hardware()`, `cdns_unprepare_transfer_hardware()`, `cdns_target_abort()`, `cdns_spi_probe()`, and PM callbacks.

## Control Flow

Probe chooses `spi_alloc_target()` when the `spi-slave` property is present, otherwise `spi_alloc_host()`. It maps registers, enables `pclk` and `ref_clk`, toggles optional reset, sets up runtime PM and chip-select properties for host mode, detects FIFO depth by writing the threshold register, initializes hardware, requests the IRQ, fills controller callbacks and mode bits, and registers the controller.

For each host transfer, `cdns_transfer_one()` configures clock frequency, sets current TX/RX buffers and counts, converts byte length to word count based on `bits_per_word`, preloads the FIFO, enables TX-overwater and mode-fault interrupts, and returns a positive length so the SPI core waits. The IRQ handler acknowledges status, handles mode fault by disabling interrupts and finalizing, or handles TX-overwater by draining received words, filling more TX words, lowering the threshold near the end, and finalizing after the final drain. Target mode uses the same FIFO helpers but skips clock and CS setup; `target_abort` disables relevant interrupts and finalizes.

## State and Persistence Behavior

State is volatile and per-controller. The cached `speed_hz`, `current` buffers, word counters, FIFO threshold, decoded-CS mode, and current enable state survive between transfers until reconfigured. Runtime PM disables/enables both clocks for host mode; system resume reinitializes controller registers. There is no persistent storage, but SPI transfers can change attached devices.

## Dependencies and Integration Points

The driver depends on platform/OF probing, clocks, reset controls, IRQs, runtime PM, GPIO-descriptor chip-select integration, and the SPI core. OF properties include `spi-slave`, `num-cs`, and `is-decoded-cs`. The `cix,sky1-spi-r1p6` compatible expands allowed `bits_per_word` to 16 and 32, while default compatibles are 8-bit only.

## Risks and Edge Cases

The reader/writer functions only log and return on unaligned buffers, but the transfer continues with unchanged counters already decremented by `cdns_spi_process_fifo()`, which can produce data loss rather than an error. The IRQ path uses a fixed 10 us delay to work around unreliable RX-not-empty status. Runtime PM is configured only for host mode, so target-mode clock lifetime relies on devm-enabled clocks. Clock divisor selection silently chooses the nearest lower speed. Transfer completion on mode fault depends on the SPI core noticing nonzero remaining bytes.

## Test Signals

Tests should cover probe in host and target mode, decoded and nondecoded CS, 8/16/32-bit modes for the CIX compatible, unaligned buffer fault behavior, FIFO depth detection, long transfers crossing FIFO thresholds, RX-only/TX-only transfers, mode-fault IRQ, target abort, runtime autosuspend/resume, system suspend/resume, and error paths for missing clocks, reset, IRQ, or MMIO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cadence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cavium-octeon.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-cavium-octeon.c

## Purpose

`spi-cavium-octeon.c` is the platform front-end for Cavium OCTEON MPI SPI controllers. It binds OF platform devices, maps OCTEON register space, supplies OCTEON-specific register offsets and clock rate, and delegates actual transfer execution to the shared Cavium core in `spi-cavium.c`.

## Important APIs, Types, and Functions

The driver uses shared `struct octeon_spi` from `spi-cavium.h`. `octeon_spi_probe()` allocates a SPI host, maps the first platform memory resource, sets `sys_freq` from `octeon_get_io_clock_rate()`, installs MPI register offsets, configures controller capabilities, and registers the host. `octeon_spi_remove()` unregisters the controller and writes zero to the configuration register to clear CS enable bits.

## Control Flow

On probe, the driver allocates host-private `struct octeon_spi`, stores the platform drvdata, maps MMIO, initializes offsets for config/status/tx/data, advertises four chip selects and mode support for CPHA, CPOL, CS-high, LSB-first, and 3-wire, sets 8-bit-only transfers and 16 MHz maximum speed, points `transfer_one_message` at `octeon_spi_transfer_one_message()`, and registers the controller. Remove unregisters, then leaves hardware in a disabled state.

## State and Persistence Behavior

The file owns no complex persistent state. It initializes `register_base`, `sys_freq`, and offset values that persist for the life of the host. Hardware configuration is reset to zero on remove. SPI device-visible state is created by the shared core during transfers.

## Dependencies and Integration Points

It depends on platform devices, OF matching, OCTEON architecture support for `octeon_get_io_clock_rate()`, MMIO accessors, and the shared `spi-cavium` core. The compatible string is `cavium,octeon-3010-spi`.

## Risks and Edge Cases

This front-end assumes the OCTEON architecture helper is available and that the register layout starts at offsets 0, 0x08, 0x10, and 0x80. It has no runtime PM, clock gating, or IRQ support. Registering fixed four chip selects may mismatch unusual hardware descriptions. Cleanup uses a controller reference get/put pattern around unregister, so lifetime expectations should remain aligned with SPI core behavior.

## Test Signals

Probe tests should validate MMIO mapping failure, host allocation failure, controller registration failure, OF matching, and the reported mode/bits/speed caps. Runtime tests should use the shared Cavium transfer tests for CS handling, chunking, and polling, then confirm remove writes zero to the config register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cavium-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cavium-thunderx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-cavium-thunderx.c

## Purpose

`spi-cavium-thunderx.c` is the PCI front-end for Cavium ThunderX SPI controllers. It adapts the shared OCTEON-style Cavium SPI transfer core to a PCI BAR register layout and clock source.

## Important APIs, Types, and Functions

`thunderx_spi_probe()` allocates a host, enables the PCI device with managed helpers, requests BAR regions, maps BAR 0, fills ThunderX register offsets, gets/enables an optional unnamed clock, computes `sys_freq` with fallback to 700 MHz, configures controller capabilities, and registers the controller. `thunderx_spi_remove()` unregisters and clears the hardware config register. The PCI ID table matches Cavium vendor ID device `0xa00b`.

## Control Flow

Probe initializes the shared `struct octeon_spi` but with offsets `0x1000`, `0x1008`, `0x1010`, and `0x1080`. It sets `SPI_CONTROLLER_HALF_DUPLEX`, four chip selects, CPHA/CPOL/CS-high/LSB-first/3-wire mode bits, 8-bit words, 16 MHz maximum speed, and `octeon_spi_transfer_one_message()` as the message engine. On any failure before registration it releases the host; managed PCI resources handle device cleanup.

## State and Persistence Behavior

Per-controller state consists of BAR mapping, clock pointer, system frequency, register offsets, and shared-core transfer cache such as `last_cfg` and `cs_enax`. Remove writes zero to the configuration register to leave hardware disabled. There is no file-backed persistence or runtime PM.

## Dependencies and Integration Points

The file integrates with Linux PCI, managed PCI resource APIs, clocks, the SPI controller core, and the shared `spi-cavium` transfer implementation. Hardware integration is through BAR 0 and the ThunderX register offset convention.

## Risks and Edge Cases

If the clock provider returns a zero rate, the driver silently falls back to 700 MHz; incorrect fallback frequency affects baud divisor calculation in the shared core. The controller is marked half-duplex, but the shared core can fill both TX and RX buffers in a transfer cycle, so integration expectations should be checked. Like the OCTEON front-end, there is no interrupt, runtime PM, or dynamic CS count discovery.

## Test Signals

Tests should cover PCI enable/request/map failures, missing or zero-rate clock, registration failure cleanup, supported mode advertisement, half-duplex behavior through SPI core validation, and remove-time hardware disable. Shared Cavium transfer tests should run against the ThunderX register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cavium-thunderx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cavium.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-cavium.c

## Purpose

`spi-cavium.c` is the shared transfer engine for Cavium OCTEON/ThunderX MPI SPI controllers. It implements polling, register programming, chip-select retention, byte chunking, and message finalization for the platform and PCI front-ends.

## Important APIs, Types, and Functions

`octeon_spi_transfer_one_message()` is the exported controller callback used by both front-ends. It iterates message transfers and calls `octeon_spi_do_transfer()`. `octeon_spi_do_transfer()` configures `cvmx_mpi_cfg`, writes up to nine bytes at a time to DAT registers, starts transfers through `cvmx_mpi_tx`, polls readiness via `octeon_spi_wait_ready()`, copies received bytes, and executes transfer delays. `octeon_spi_wait_ready()` loops on the MPI busy bit.

## Control Flow

For each `spi_transfer`, the core computes CPHA/CPOL-derived idle and late-CS settings, a clock divisor from `sys_freq` and requested speed, CS polarity, LSB-first, 3-wire mode, and per-CS enable bits. It writes the config register only when it changes. The data path splits transfers into `OCTEON_SPI_MAX_BYTES` chunks of nine bytes. Full chunks force `leavecs = 1`; the final chunk sets `leavecs` according to whether this is the last transfer and `cs_change`. RX data is read back after each hardware transaction. The message callback accumulates actual length, stops on errors, sets message status, and finalizes the message.

## State and Persistence Behavior

The shared state in `struct octeon_spi` caches `last_cfg` to avoid redundant config writes and `cs_enax` to keep CS enable bits accumulated for chip selects below four. Per-transfer pointers and lengths are local. No persistent host storage is written; hardware registers retain the latest config until overwritten or cleared by front-end remove.

## Dependencies and Integration Points

The file depends on the SPI core, delay helpers, 64-bit MMIO accessors, and `spi-cavium.h` register/bitfield definitions. It is not a module by itself; front-ends compile and call it.

## Risks and Edge Cases

`octeon_spi_wait_ready()` has no timeout, so broken hardware can spin indefinitely. The clock divisor calculation does not clamp or reject zero `speed_hz`, and `clkdiv` can become zero or out of hardware range depending on inputs. Transfers larger than nine bytes are handled, but all operations are CPU-polling and synchronous. RX-only transfers use `txnum = 0` but `totnum` nonzero; hardware behavior must match that assumption. The cached `cs_enax` only sets bits and never clears per-device CS enable bits until front-end remove.

## Test Signals

Functional tests should cover TX-only, RX-only, full-duplex, transfers crossing nine-byte boundaries, `cs_change` across multi-transfer messages, all advertised mode bits, LSB-first, 3-wire, chip selects 0-3, and transfer delays. Fault tests should include bad speed values and simulated stuck busy bit to motivate timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cavium.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cavium.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-cavium.h

## Purpose

`spi-cavium.h` is the shared private header for Cavium OCTEON and ThunderX SPI drivers. It defines common driver state, controller limits, register-offset access macros, the shared transfer callback prototype, and 64-bit MPI register bitfield layouts used by the shared core.

## Important APIs, Types, and Functions

`struct octeon_spi_regs` stores offsets for config, status, TX, and data registers. `struct octeon_spi` stores the mapped register base, cached configuration, accumulated CS enable bits, system frequency, offsets, and optional clock pointer. Macros `OCTEON_SPI_CFG()`, `OCTEON_SPI_STS()`, `OCTEON_SPI_TX()`, and `OCTEON_SPI_DAT0()` access those offsets. Constants include `OCTEON_SPI_MAX_BYTES` and `OCTEON_SPI_MAX_CLOCK_HZ`.

The header declares `octeon_spi_transfer_one_message()`. It also defines legacy OCTEON physical MPI register addresses and unions `cvmx_mpi_cfg`, `cvmx_mpi_datx`, `cvmx_mpi_sts`, and `cvmx_mpi_tx` with endian-specific bitfields and SoC-family variants.

## Control Flow

The header is not executable by itself. Front-ends fill `struct octeon_spi` with a register base, register offsets, and frequency, then install `octeon_spi_transfer_one_message()` as the controller callback. The shared core uses the bitfield unions to build hardware config and TX command words, poll status, and move byte data through DAT registers.

## State and Persistence Behavior

The state described here lives for the lifetime of a probed controller. `last_cfg` and `cs_enax` persist across transfers and influence whether the core rewrites config registers and which CS enable bits stay active. The union definitions model hardware register state but do not persist data outside the controller.

## Dependencies and Integration Points

The header depends on kernel clock types and SPI controller declarations from inclusion context. It integrates front-end drivers with the shared Cavium transfer core and exposes OCTEON MPI register fields for big-endian and little-endian bitfield layouts.

## Risks and Edge Cases

The union register layouts rely on compiler bitfield ordering and `__BIG_ENDIAN_BITFIELD`; mismatches would corrupt hardware programming. Several SoC-family variants are present but the shared core mostly uses the generic `.s` views, so variant-specific missing fields may matter on older OCTEON parts. The legacy `CVMX_ADD_IO_SEG` addresses assume OCTEON architecture definitions when used.

## Test Signals

Compile tests should include relevant endianness and architecture configurations. Layout-sensitive changes should be checked against hardware manuals or register-unit tests where possible. Runtime tests should validate that platform and PCI front-ends fill offsets correctly and that shared-core config bits map to expected CPOL/CPHA/CS/clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cavium.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ch341.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-ch341.c

## Purpose

`spi-ch341.c` is a USB-to-SPI controller driver for the QinHeng/WCH CH341A adapter. It registers a USB driver, exposes a SPI host backed by USB bulk transfers, configures CH341 stream/pin modes, and creates a default SPI device with modalias `spi-ch341a`.

## Important APIs, Types, and Functions

`struct ch341_spi_dev` stores the SPI controller, USB device, bulk pipe addresses, RX URB/buffer, TX buffer, and created child SPI device. `ch341_probe()` and `ch341_disconnect()` handle USB lifecycle. `ch341_transfer_one()` sends a `CH341A_CMD_SPI_STREAM` packet and reads the response through bulk endpoints. `ch341_set_cs()` drives CS through UIO stream commands. `ch341_config_stream()` and `ch341_enable_pins()` initialize the adapter.

## Control Flow

Probe finds bulk IN/OUT endpoints, allocates a devm SPI host, allocates buffers and a RX URB, submits the URB, configures controller callbacks and mode bits, stores USB interface data, sends stream configuration, enables pins, registers the controller, and creates a child SPI device. Each transfer builds a packet of at most 32 bytes including command byte, copies TX data after it, sends it on the bulk OUT pipe, then reads response bytes from the bulk IN pipe. Disconnect unregisters the child device and controller, disables pins, kills the URB, and frees it.

## State and Persistence Behavior

State is volatile USB/controller state. The TX buffer is reused for CS and transfer commands. The driver creates one child SPI device automatically after controller registration. Adapter pin state is enabled on probe and disabled on disconnect. There is no runtime PM or persistent storage.

## Dependencies and Integration Points

The file integrates with the USB core, SPI controller core, bulk endpoints, URBs, and a board-info-created child SPI device. It matches USB device ID `1a86:5512`.

## Risks and Edge Cases

`ch341_transfer_one()` caps the packet length at 32 bytes and silently truncates longer SPI transfers to 31 payload bytes while returning only the USB read status, not the number transferred. It unconditionally copies from `trans->tx_buf`, so RX-only transfers with NULL TX buffer can crash. It unconditionally reads into `trans->rx_buf`, so TX-only transfers with NULL RX buffer can also crash. The submitted RX URB appears unused for transfer data because transfers use synchronous `usb_bulk_msg()` reads. The driver advertises only `SPI_CPHA` and has fixed speed behavior.

## Test Signals

Tests should cover probe with missing endpoints, allocation failures, stream/pin command failures, transfer lengths 0, 1, 31, 32, and greater than 31 payload bytes, TX-only/RX-only validation, disconnect during pending operations, CS-high/low command bytes, and USB stall/disconnect errors from bulk messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ch341.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-clps711x.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-clps711x.c

## Purpose

`spi-clps711x.c` is a compact SPI bus driver for CLPS711X/EP7209 synchronous I/O hardware. It uses one MMIO syncio register, a syscon register bit for CPHA mode, a clock, and one IRQ to implement byte/frame transfers.

## Important APIs, Types, and Functions

`struct spi_clps711x_data` stores the syncio MMIO pointer, syscon regmap, SPI clock, current TX/RX buffers, bits-per-word, and remaining length. `spi_clps711x_prepare_message()` programs clock phase through `SYSCON3_ADCCKNSEN`. `spi_clps711x_transfer_one()` sets the clock rate, initializes current transfer state, writes the first frame, and returns asynchronous completion. `spi_clps711x_isr()` reads one received frame, writes the next, or finalizes the transfer. `spi_clps711x_probe()` wires platform resources into a SPI host.

## Control Flow

Probe gets the IRQ, allocates the host, sets controller capabilities, obtains the clock, resolves the `syscon` phandle, maps syncio, disables extended mode due hardware problems, clears a pending interrupt by reading syncio, requests the IRQ, and registers the controller. A transfer begins by setting clock rate, storing buffers and length, and writing the first data byte plus frame length and TX frame enable bits. Each interrupt consumes one byte from syncio and writes the next until length reaches zero.

## State and Persistence Behavior

The per-transfer state is stored in the host-private structure and is valid only while one transfer is active. Persistent controller configuration is minimal: syscon CPHA bit, disabled extended mode, and clock rate. There is no runtime PM or file-backed persistence.

## Dependencies and Integration Points

The driver depends on platform/OF, clocks, syscon/regmap, MMIO, IRQs, GPIO descriptor chip-select support, and the SPI core. It matches `cirrus,ep7209-spi`.

## Risks and Edge Cases

The driver treats `xfer->len` as a byte count even when `bits_per_word` may be 1-8; non-8-bit frame semantics should be verified. There is no timeout if interrupts stop. `clk_set_rate()` return value is ignored. Only CPHA and CS-high are advertised, not CPOL. The syscon update in prepare_message is shared system state and could affect non-SPI syncio users.

## Test Signals

Tests should cover probe failure for missing IRQ/clock/syscon/MMIO, CPHA toggling, clock-rate requests, transfers with and without TX/RX buffers, 1-bit through 8-bit frame sizes, interrupt completion, no-interrupt timeout behavior at the SPI core level, and GPIO CS integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-clps711x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-coldfire-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-coldfire-qspi.c

## Purpose

`spi-coldfire-qspi.c` is the Freescale/Motorola ColdFire queued SPI controller driver. It uses the QSPI command/data RAM, an interrupt-backed waitqueue, platform-supplied chip-select callbacks, and optional runtime/system PM clock gating to perform 8-bit and 16-bit transfers.

## Important APIs, Types, and Functions

`struct mcfqspi` stores MMIO base, IRQ, clock, platform CS callbacks, and waitqueue. Register helpers wrap QMR/QDLYR/QWR/QIR/QAR/QDR accesses. Transfer engines `mcfqspi_transfer_msg8()` and `mcfqspi_transfer_msg16()` fill command and TX buffers, run queued transfers in 16-entry then 8-entry ping-pong chunks, wait for SPE to clear, and drain RX. `mcfqspi_transfer_one()` programs mode/baud and dispatches the right engine. `mcfqspi_set_cs()`, `mcfqspi_setup()`, `mcfqspi_probe()`, `mcfqspi_remove()`, and PM callbacks provide SPI integration.

## Control Flow

Probe requires platform data and `cs_control`, allocates a host, maps registers, requests IRQ, enables `qspi_clk`, initializes chip-select callbacks, creates the waitqueue, sets mode and bits-per-word capabilities, enables runtime PM, and registers the controller. A transfer programs QMR for master, bits per word, CPOL/CPHA, and baud divisor. It enables SPIF interrupt, runs the 8- or 16-bit queued transfer routine, then disables interrupts. The IRQ clears SPIF and wakes the waitqueue used by the transfer routines.

## State and Persistence Behavior

Persistent state is limited to controller registers, the platform CS backend, and clock/runtime PM state. Per-transfer data remains on the stack inside transfer routines and blocks until completion. Remove unregisters, disables runtime PM, programs QMR to master with baud 0, and tears down chip-select callbacks.

## Dependencies and Integration Points

The driver depends on ColdFire architecture headers, platform data (`struct mcfqspi_platform_data` and CS control callbacks), MMIO, IRQs, clocks, runtime PM, and the SPI core. It does not use OF parsing in this file.

## Risks and Edge Cases

The waitqueue waits have no explicit timeout, so lost interrupts or stuck SPE can hang the transfer. In the no-TX-buffer path of `mcfqspi_transfer_msg8()`, the initial fill loop iterates over `count` instead of `n`, which may overrun the 16-entry RAM window for large RX-only transfers; the 16-bit path uses `n`. Baud calculation uses the `MCF_BUSCLK / 2` macro rather than the enabled clock rate. The driver assumes platform CS callbacks are valid and synchronous.

## Test Signals

Tests should cover missing platform data, missing CS callbacks, IRQ and clock failures, 8-bit and 16-bit TX/RX/RX-only transfers, lengths 1, 8, 16, 17, and large multi-chunk transfers, CS polarity callbacks, runtime/system suspend/resume, stuck SPE/interrupt loss, and the RX-only command RAM fill boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-coldfire-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cs42l43.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-cs42l43.c

## Purpose

`spi-cs42l43.c` is the SPI controller driver for the Cirrus Logic CS42L43 MFD. It exposes an internal register-controlled SPI master, supports half-duplex transfers through regmap FIFOs, and can create sidecar CS35L56 amplifier devices based on ACPI/firmware-node information.

## Important APIs, Types, and Functions

`struct cs42l43_spi` holds device, regmap, and SPI controller pointers. Data movement uses `cs42l43_spi_tx()` and `cs42l43_spi_rx()` to write/read 16-byte FIFO blocks through regmap and handshake status bits. `cs42l43_transfer_one()` sets clock divider, configures read/write length, starts transfer, and calls the relevant FIFO helper. `cs42l43_prepare_message()`, `cs42l43_set_cs()`, `cs42l43_prepare_transfer_hardware()`, and `cs42l43_unprepare_transfer_hardware()` configure mode, CS, and block enable. Probe handles controller allocation, PM, FIFO thresholds, firmware-node selection, sidecar GPIO/software-node setup, registration, and optional child amp creation.

## Control Flow

Probe obtains parent `struct cs42l43`, allocates driver state and a host, wires regmap and callbacks, sets half-duplex mode and 8/16/32-bit word caps, enables runtime PM, programs FIFO sizes and stall/watchdog settings, chooses an OF `spi` child node or ACPI function-expansion node, clears the controller fwnode, optionally creates a software node with CS GPIO references and speaker-id property, registers the controller, and, for sidecars, creates left/right `cs35l56` SPI devices.

A transfer chooses the first divider whose root/divided frequency is not above `tfr->speed_hz`, programs read or write mode and length-minus-one register, starts the transaction, then streams FIFO blocks. TX writes packed little-endian words and signals TX done per block. RX polls for RX request, reads words, unpacks bytes, then signals RX done.

## State and Persistence Behavior

The driver persists controller regmap settings, runtime PM enablement, firmware/software-node associations, and optional child SPI devices while probed. Transfer state is local. Persistent side effects are register changes in the parent MFD and creation of child devices; attached amplifier/device state changes happen through SPI clients.

## Dependencies and Integration Points

It integrates with the CS42L43 MFD/regmap, runtime PM, GPIO descriptors, GPIO software nodes, ACPI and OF firmware nodes, property APIs, and the SPI core. It imports the `GPIO_SWNODE` namespace. Sidecar support uses `cs35l56` board info and speaker-id properties from ACPI or GPIOs.

## Risks and Edge Cases

Probe allocates the host with `sizeof(*priv->ctlr)` rather than zero/private data size and then separately calls `spi_controller_set_devdata()`, which wastes memory and should be reviewed. `cs42l43_transfer_one()` returns `-EINVAL` for full-duplex transfers and for speeds below the slowest divider, but only implicitly through missing TX/RX handling or divider loop. Regmap write return values are often ignored in setup paths. Firmware-node lifetime and software-node references are subtle, especially when `nsidecars` is nonzero and the controller node is cleared.

## Test Signals

Tests should cover OF and ACPI probe paths, no-sidecar and sidecar configurations, speaker-id from ACPI and GPIOs, software-node creation failure, controller registration failure, 8/16/32-bit TX and RX, unsupported full-duplex transfer rejection, clock divider boundary speeds, FIFO block lengths including 16-byte multiples and remainders, runtime PM enable/idle, and child amplifier creation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-cs42l43.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-davinci.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-davinci.c

## Purpose

`spi-davinci.c` is the TI DaVinci/DA8xx/Keystone SPI master driver. It uses `spi_bitbang` orchestration with controller-specific register programming, GPIO or native chip select, polled/interrupt/DMA transfer modes, per-device timing configuration, and OF or legacy platform data.

## Important APIs, Types, and Functions

`struct davinci_spi` stores the bitbang controller, clock, MMIO base/physical base, IRQ, completion, TX/RX pointers, word counts, DMA channels, platform data, byte-access callbacks, per-CS bytes-per-word cache, and prescaler limit. Important functions include `davinci_spi_setup_transfer()`, `davinci_spi_setup()`, `davinci_spi_chipselect()`, `davinci_spi_bufs()`, `davinci_spi_process_events()`, `davinci_spi_irq()`, DMA callbacks, `davinci_spi_request_dma()`, `spi_davinci_get_pdata()`, `davinci_spi_probe()`, and `davinci_spi_remove()`.

## Control Flow

Probe gets platform data or OF match data, allocates per-CS byte-size cache, maps registers, requests a threaded IRQ with a dummy thread function, enables the clock, configures SPI controller and bitbang callbacks, optionally requests DMA channels, resets the SPI module, programs pins, interrupt level, default CS, master/clock/powerdown bits, and starts `spi_bitbang`.

Setup configures native CS pin function, READY and loopback bits, and per-device OF config such as `ti,spi-wdelay`; if both DMA channels exist the device config defaults to DMA. Transfer setup selects 8- or 16-bit buffer callbacks, computes prescaler, programs SPIFMT and SPIDELAY. `davinci_spi_bufs()` initializes counts, enables the module, uses DMA when allowed or starts PIO/IRQ/polling by writing the first word, waits for completion or polls events, disables interrupts and module, checks error flags, and returns transferred length.

## State and Persistence Behavior

Per-device `struct davinci_spi_config` may be allocated from OF and stored in `spi->controller_data` until cleanup. Controller state persists in hardware registers, DMA channel handles, per-CS bytes-per-word cache, and bitbang workqueue state. There is no file-backed persistence; SPI transfers affect attached devices.

## Dependencies and Integration Points

The driver depends on platform/OF data, `spi_bitbang`, clocks, GPIO descriptors, IRQs, DMA engine slave channels, EDMA platform types, MMIO accessors, completions, and the SPI core. Compatible data selects IP version and prescaler limits.

## Risks and Edge Cases

`davinci_spi_get_prescale()` rejects prescalers below `prescaler_limit`, which is version-specific and easy to misconfigure. DMA eligibility rejects vmalloc buffers but assumes prepared SPI SG lists are valid. RX-only DMA aliases TX SG to RX SG to keep reloads synchronized, which is clever but fragile. Timeout calculation derives from speed and length and may underflow to too-short waits for small/fast transfers. Error handling clears interrupts after wait but DMA descriptors may need explicit termination on timeout. The threaded IRQ dummy exists solely to satisfy the API.

## Test Signals

Tests should cover OF and platform-data probe, all compatible versions, prescaler boundaries, CPOL/CPHA/LSB/loopback/READY/CS_WORD modes, GPIO and native CS, 8- and 16-bit buffers, polling, IRQ, and DMA modes, RX-only DMA with many SG entries, timeout/error flag handling, DMA request defer/failure, setup/cleanup of OF controller_data, and remove cleanup of bitbang and DMA channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-davinci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dln2.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-dln2.c

## Purpose

`spi-dln2.c` is the SPI host driver for the Diolan DLN-2 USB/MFD adapter. It communicates with adapter firmware through `dln2_transfer()` commands, queries firmware capabilities, configures chip selects, speed, mode and frame size, splits transfers into firmware-sized chunks, and supports runtime/system PM by enabling or disabling the SPI module.

## Important APIs, Types, and Functions

`struct dln2_spi` stores the platform device, SPI host, DLN2 port, reusable command buffer, cached bits-per-word, speed, mode, and selected CS. Firmware command helpers include `dln2_spi_enable()`, `dln2_spi_cs_set()`, `dln2_spi_cs_enable_all()`, `dln2_spi_get_cs_num()`, `dln2_spi_get_speed_range()`, `dln2_spi_set_speed()`, `dln2_spi_set_mode()`, and `dln2_spi_set_bpw()`. Data helpers include endian conversion functions, `dln2_spi_write_one()`, `dln2_spi_read_one()`, `dln2_spi_read_write_one()`, and `dln2_spi_rdwr()`. SPI integration is through `dln2_spi_prepare_message()`, `dln2_spi_transfer_one()`, probe/remove, and PM callbacks.

## Control Flow

Probe allocates the host and a reusable buffer, reads platform port data, disables the firmware module, queries chip-select count, min/max speed, and supported frame sizes, enables all CS lines, sets controller callbacks, enables the module, enables runtime PM, and registers the controller.

Before a message, `prepare_message()` selects the target CS if it changed. Each transfer calls `dln2_spi_transfer_setup()`, which disables the module if bus parameters changed, applies speed/mode/bpw changes, updates caches, and re-enables the module. `dln2_spi_rdwr()` breaks transfer data into 256-byte operations, setting `LEAVE_SS_LOW` for intermediate chunks or continued SPI transfers, and dispatches write, read, or read-write firmware commands with little-endian word ordering.

## State and Persistence Behavior

The driver caches bus setup to avoid unnecessary firmware reconfiguration. Suspend resets cached CS/speed/bpw/mode because USB power may be cut and forces the next transfer to reconfigure the board. Runtime suspend disables the SPI module; runtime resume enables it. No file-backed persistence exists, but firmware module state and CS enables persist while the adapter is powered.

## Dependencies and Integration Points

The file depends on the DLN2 MFD command API, platform data, property headers, runtime PM, unaligned helpers, and the SPI core. It advertises CPOL/CPHA modes and firmware-reported bits-per-word and speed ranges.

## Risks and Edge Cases

`dln2_spi_transfer_setup()` returns immediately after a failed speed/mode/bpw set without re-enabling the module, leaving the adapter disabled until recovery. `dln2_spi_get_supported_frame_sizes()` requires a full fixed-size response rather than accepting `count` plus present entries, which may reject shorter firmware replies. The reusable buffer relies on SPI core serialization. Big-endian conversion paths must avoid unaligned 32-bit access, which is handled on RX but should be regression-tested. Runtime PM and transfer setup both enable/disable the module and can expose ordering bugs if a transfer races with suspend.

## Test Signals

Tests should cover firmware query protocol lengths, min/max speed reporting, frame-size masks, chip-select count and selection, parameter-change and no-change setup, failure during speed/mode/bpw update, transfers of 1, 256, 257, and multi-chunk lengths, TX-only/RX-only/read-write commands, big-endian word conversion, runtime suspend/resume, system suspend/resume cache reset, and remove disabling the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dln2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw-core.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-dw-core.c

## Purpose

`spi-dw-core.c` is the shared Synopsys DesignWare SPI controller core used by glue drivers. It provides controller registration/removal, FIFO-based PIO and IRQ transfers, optional DMA integration, target-mode abort, debugfs registers, native chip-select control, `spi-mem` execution for standard native-CS APB SSI controllers, and suspend/resume helpers.

## Important APIs, Types, and Functions

Externally visible APIs include `dw_spi_add_controller()`, `dw_spi_remove_controller()`, `dw_spi_suspend_controller()`, `dw_spi_resume_controller()`, `dw_spi_set_cs()`, `dw_spi_update_config()`, and `dw_spi_check_status()`. Runtime helpers include `dw_writer()`, `dw_reader()`, `dw_spi_transfer_handler()`, `dw_spi_irq()`, `dw_spi_prepare_cr0()`, `dw_spi_irq_setup()`, `dw_spi_poll_transfer()`, `dw_spi_transfer_one()`, `dw_spi_abort()`, and `dw_spi_hw_init()`.

The `spi-mem` path is implemented by `dw_spi_adjust_mem_op_size()`, `dw_spi_supports_mem_op()`, `dw_spi_init_mem_buf()`, `dw_spi_write_then_read()`, `dw_spi_wait_mem_op_done()`, `dw_spi_stop_mem_op()`, `dw_spi_exec_mem_op()`, and `dw_spi_init_mem_ops()`. Per-device state is `struct dw_spi_chip_data`, storing prepared CR0 and RX sample delay.

## Control Flow

Glue drivers fill `struct dw_spi` and call `dw_spi_add_controller()`. The core allocates host or target controller based on `spi-slave`, initializes hardware, requests IRQ unless disconnected, installs default mem ops when appropriate, configures controller capabilities, initializes DMA if supplied, registers the controller, and creates debugfs.

Normal transfers disable the chip, update CTRLR0/CTRLR1/clock/sample delay, detect DMA mapping, mask interrupts, set up DMA if needed, enable the chip, then execute via DMA, poll mode, or IRQ mode. IRQ mode uses TX/RX FIFO thresholds and finalizes when RX length reaches zero. Poll mode repeatedly writes as much as possible, delays for expected receive clocks, reads FIFO, and checks raw status. Error handling aborts DMA if active and resets the chip.

The default `spi-mem` implementation packs opcode/address/dummy/TX data into one buffer, programs transmit-only or EEPROM-read mode, enables the controller, disables local interrupts and preemption, manually keeps TX FIFO nonempty while native CS is active, drains RX fast enough to avoid overflow, waits for busy to clear, checks errors, deasserts CS, and frees temporary buffers.

## State and Persistence Behavior

The core maintains controller state in `struct dw_spi`: FIFO length, number of chip selects, version/capabilities, max/current frequency, DMA state, current transfer buffers and counts, debugfs, and per-controller memory buffer. Per-SPI-device `dw_spi_chip_data` persists from setup to cleanup. There is no file-backed persistence; hardware register state is reset during init, remove, suspend, and error abort.

## Dependencies and Integration Points

The core depends on glue-provided `struct dw_spi` fields from `spi-dw.h`, SPI controller APIs, optional DMA ops, interrupts, MMIO accessors, debugfs, firmware properties, `spi-mem`, preemption/IRQ control, and namespace exports `SPI_DW_CORE`. It supports PSSI and HSSI register-layout differences and optional capabilities such as `DW_SPI_CAP_DFS32` and `DW_SPI_CAP_CS_OVERRIDE`.

## Risks and Edge Cases

The `spi-mem` path intentionally disables local IRQs/preemption and can still fail on slow buses/CPUs if the FIFO drains or RX overflows; platform glue must cap `max_mem_freq` appropriately. `free_irq(dws->irq, ...)` is called even when `request_irq()` returned `-ENOTCONN`, so disconnected IRQ configurations should be checked. FIFO and CS autodetection write test values to hardware registers and assume reversible side effects. Per-device setup allocates state and must be paired with cleanup. DMA setup failures occur after chip configuration and before chip enable, so glue DMA ops must leave consistent state.

## Test Signals

Tests should cover glue-driver add/remove with connected and disconnected IRQs, host and target mode, FIFO/CS/DFS autodetection, PSSI and HSSI CR0 fields, 4- through 32-bit transfers, IRQ, poll, and DMA paths, RX/TX overflow/underflow handling, target abort, suspend/resume, debugfs register exposure, default `spi-mem` reads/writes with native CS, GPIO CS fallback, `rx-sample-delay-ns` properties, and low `max_mem_freq` mitigation of CS underrun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-dw-core.c -->
