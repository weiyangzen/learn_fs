# subset-b-005389 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sifive.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sifive.c

## Purpose

`spi-sifive.c` is the Linux SPI host controller driver for the SiFive SPI IP block in host mode. It exposes the memory-mapped controller through the SPI core, supports up to 32 chip selects, 8-bit words, CPOL/CPHA, active-high chip select, LSB-first ordering, and dual/quad transfer width flags, but it explicitly does not implement sub-8-bit word handling or DMA.

## Important APIs, Types, and Functions

`struct sifive_spi` stores MMIO registers, the bus clock, discovered FIFO depth, inactive CS polarity bitmap, and a completion used by interrupt-driven waits. Register helpers `sifive_spi_read()` and `sifive_spi_write()` wrap `ioread32()`/`iowrite32()`. `sifive_spi_init()` disables watermark interrupts, configures TX/RX watermarks and default delays, and exits flash-specialized mode.

SPI core hooks are `sifive_spi_prepare_message()`, `sifive_spi_set_cs()`, and `sifive_spi_transfer_one()`. `sifive_spi_prep_transfer()` calculates `SCKDIV`, programs frame format/protocol/endianness/direction, and chooses polling versus interrupt wait. `sifive_spi_irq()` handles TX/RX watermark interrupts, disables further interrupts, and completes the waiter. Probe allocates a host, maps registers, enables the clock, reads optional `sifive,fifo-depth` and `sifive,max-bits-per-word`, probes CS lines through `CSDEF`, requests the IRQ, and registers the controller.

## Control Flow

For each message, `prepare_message` updates CS polarity/defaults, selected chip select, and SCK mode. `set_cs` switches hardware CS mode between automatic and hold, with active-high correction. `transfer_one` sets transfer format, then sends data in FIFO-sized chunks. It always requires TX data because the controller is registered with `SPI_CONTROLLER_MUST_TX`; dummy data is supplied by the SPI core when callers provide receive-only transfers. For each chunk it fills TX FIFO, waits for RX watermark when receiving or TX watermark when transmitting only, then drains RX FIFO if applicable.

Probe performs one-time hardware setup and register discovery. Remove unregisters the controller and disables interrupts. System suspend suspends the SPI controller, disables interrupts, and gates the clock; resume re-enables the clock and resumes the SPI controller.

## State and Persistence Behavior

There is no file-backed persistence. Long-lived state is limited to one controller's MMIO base, clock handle, FIFO depth, CS inactive bitmap, and completion. Hardware state persists while powered: programmed delay registers, watermarks, chip select defaults, SCK mode, SCK divisor, and frame format. Suspend disables the clock without fully reinitializing all format registers on resume, relying on future message/transfer setup to rewrite active transfer settings.

## Dependencies and Integration Points

The driver depends on platform devices, device tree matching (`sifive,spi0`), clocks, MMIO accessors, IRQs, completions, and the Linux SPI controller API. It integrates with GPIO chip selects through `SPI_CONTROLLER_GPIO_SS` and disables device DMA by clearing `pdev->dev.dma_mask`.

## Risks and Edge Cases

`sifive_spi_transfer_one()` increments `tx_ptr` unconditionally. Correct operation depends on `SPI_CONTROLLER_MUST_TX` ensuring a valid TX buffer for RX-only transfers. The wait path has no timeout, so lost interrupts or a stuck watermark can hang a transfer. Polling loops are also unbounded. The divisor calculation masks to 12 bits; an unsupported low speed can silently wrap to an unintended faster speed. The dual/quad mode selection uses the max of TX/RX nbits, so mixed-width phases inside a single transfer are not represented.

## Test Signals

Useful tests include probe with explicit and missing FIFO-depth properties, CS line auto-probe, all CPOL/CPHA modes, active-high and GPIO CS, LSB-first transfers, RX-only dummy TX, TX-only, dual/quad advertised transfers, long transfers spanning multiple FIFO chunks, suspend/resume around active devices, and fault injection for missing IRQ, zero clock, and stuck TX/RX watermark conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sifive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-slave-mt27xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-slave-mt27xx.c

## Purpose

`spi-slave-mt27xx.c` implements a MediaTek SPI target controller for MT2712 and MT8195-class hardware. It registers a target-mode SPI controller, supports FIFO and DMA transfers, configures CPOL/CPHA and bit order, and exposes `target_abort` for upper-layer target handlers that need to cancel a pending transaction.

## Important APIs, Types, and Functions

`struct mtk_spi_slave` stores the device, MMIO base, SPI clock, completion, current transfer pointer, abort flag, and compatible-specific limits. `struct mtk_spi_compatible` describes FIFO size and whether RX is mandatory; MT2712 has a 512-byte FIFO and MT8195 has a 128-byte FIFO with `SPI_CONTROLLER_MUST_RX`.

Core hooks are `mtk_spi_slave_prepare_message()`, `mtk_spi_slave_transfer_one()`, `mtk_spi_slave_setup()`, and `mtk_target_abort()`. FIFO and DMA paths are split into `mtk_spi_slave_fifo_transfer()` and `mtk_spi_slave_dma_transfer()`. `mtk_spi_slave_interrupt()` acknowledges hardware status, copies FIFO RX data, unmaps DMA buffers on DMA completion, disables transfer/DMA state, and completes the waiter. Probe allocates a target controller with `spi_alloc_target()`, maps resources, requests IRQ, enables the clock for registration, sets runtime PM, and registers the controller.

## Control Flow

Message preparation writes polarity, phase, MSB/LSB order, and endian bits into `SPIS_CFG_REG`. A transfer reinitializes completion, clears abort state, records the current transfer, and chooses DMA when length exceeds the compatible FIFO size. FIFO mode resets hardware, enables TX/RX according to buffers, preloads TX FIFO in 32-bit words plus remainder, then waits for an IRQ. DMA mode maps TX and/or RX buffers, writes DMA addresses, enables DMA-address mode, enables TX/RX, writes transfer length, starts DMA, then waits for completion. The interrupt path distinguishes DMA and FIFO completion based on `DMA_DONE_ST` plus `DATA_DONE_ST`/`RSTA_DONE_ST`.

## State and Persistence Behavior

Persistent kernel state is per-controller only: current transfer pointer, clock state, compatible data, and completion/abort flags. No filesystem persistence exists. Hardware register state is reset at the start and end of transfers. Runtime/system PM gates the SPI clock while the controller is idle or suspended.

## Dependencies and Integration Points

The driver depends on platform resources, OF compatible data, MMIO, IRQs, completions, DMA mapping, clocks, runtime PM, and the SPI target controller API. Target handlers such as `spi-slave-time` and `spi-slave-system-control` can run on top of this controller.

## Risks and Edge Cases

The DMA path writes `xfer->tx_dma` and `xfer->rx_dma` registers even when the corresponding buffer is absent; those fields must be harmless or preinitialized by SPI core. Successful DMA completion relies on the IRQ handler to unmap buffers and disable DMA, while error paths clean up locally. `mtk_spi_slave_wait_for_completion()` has no timeout, so a missing host transaction or lost interrupt can block indefinitely unless `target_abort` is invoked. `CMD_INVALID_ST` returns `IRQ_NONE` after warning, which may confuse shared IRQ diagnostics while a transfer is still completed afterward only if the code reaches the final completion path; here it returns before clearing `cur_transfer`.

## Test Signals

Exercise FIFO and DMA thresholds for both compatibles, TX-only, RX-only, full duplex, non-4-byte remainders, MT8195 mandatory RX behavior, target abort while waiting, command-invalid interrupts, reset-done interrupts, runtime suspend/resume, system suspend/resume, and DMA mapping failures for each direction. IRQ-driven cleanup should be checked for double-unmap and missing-unmap cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-slave-mt27xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-slave-system-control.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-slave-system-control.c

## Purpose

`spi-slave-system-control.c` is a SPI target protocol handler that lets a remote SPI host request system reboot, poweroff, halt, or suspend by sending one of four two-byte big-endian command values. It is intentionally small and policy-heavy: received SPI data directly triggers kernel system-control APIs.

## Important APIs, Types, and Functions

`struct spi_slave_system_control_priv` stores the bound `spi_device`, a `finished` completion, one reusable `spi_transfer`, one `spi_message`, and a big-endian 16-bit command buffer. `spi_slave_system_control_submit()` initializes the reusable one-transfer message, installs the completion callback, and queues it with `spi_async()`. `spi_slave_system_control_complete()` decodes the command and calls `kernel_restart()`, `kernel_power_off()`, `kernel_halt()`, or `pm_suspend(PM_SUSPEND_MEM)`. Probe allocates state, sets the RX buffer, submits the first asynchronous receive, and stores drvdata. Remove calls `spi_target_abort()` and waits for the callback to complete.

## Control Flow

The handler keeps exactly one asynchronous RX message outstanding. When a two-byte message completes successfully, the callback converts `priv->cmd` with `be16_to_cpu()`, executes the matching system action, and then resubmits another receive. Any SPI message error or resubmit failure terminates the loop by completing `finished`. Removal aborts the target-side controller transaction and waits until the callback observes termination.

## State and Persistence Behavior

There is no persistent storage. State is limited to the reusable SPI message/transfer and the last received command. The side effects are system-wide and potentially persistent outside the driver: reboot modes, power state changes, and suspend state are controlled by kernel system-control paths.

## Dependencies and Integration Points

The file depends on the SPI target-device API, completions, reboot/poweroff/halt APIs, and system suspend support. It must run on a SPI controller that supports target mode and `spi_target_abort()`.

## Risks and Edge Cases

Any entity able to send the magic two-byte values on the SPI link can reboot, power off, halt, or suspend the machine. There is no authentication, framing beyond two bytes, rate limit, or confirmation. Calling reboot or suspend APIs from an SPI completion callback may run in a context where sleeping behavior depends on SPI core completion threading. Unknown commands only warn and resubmit. Remove can wait indefinitely if the controller's `target_abort` fails to complete the outstanding message.

## Test Signals

Tests should cover all four command values in big-endian order, unknown commands, repeated commands, SPI completion error, resubmit failure, driver removal while an RX is pending, and target controller abort behavior. Security review should treat this as a privileged hardware management interface, not a general-purpose remote-control protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-slave-system-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-slave-time.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-slave-time.c

## Purpose

`spi-slave-time.c` is a SPI target protocol handler that continuously returns the local uptime captured at the time the previous SPI message was submitted. The payload is two big-endian 32-bit integers: seconds since boot and microseconds within the current second.

## Important APIs, Types, and Functions

`struct spi_slave_time_priv` stores the `spi_device`, a termination completion, one reusable transfer/message pair, and a two-word transmit buffer. `spi_slave_time_submit()` samples `local_clock()`, converts nanoseconds into seconds and microseconds with `do_div()`, stores values in network byte order, initializes a one-transfer message, and queues it with `spi_async()`. The completion callback checks `msg.status` and resubmits on success. Probe allocates state, sets the TX buffer and length, submits the first message, and stores drvdata. Remove aborts the target transaction and waits for termination.

## Control Flow

The driver maintains one outstanding asynchronous TX message. The buffer is refreshed immediately before submission, so the SPI host receives the timestamp of the last submission, effectively the previous request boundary. On successful completion, the callback immediately submits the next message. Any error or resubmit failure stops the loop and completes `finished`.

## State and Persistence Behavior

The only durable in-kernel state is the reusable message/transfer and the current two-word timestamp buffer. There is no filesystem or firmware persistence. The time source is `local_clock()`, so semantics are uptime-like and local CPU clock dependent rather than wall-clock time.

## Dependencies and Integration Points

The file depends on the SPI target-device API, `local_clock()` from scheduler clock support, big-endian conversion helpers, and completions. It requires a target-capable SPI controller with working abort semantics.

## Risks and Edge Cases

The 32-bit seconds field wraps after roughly 136 years of uptime; the microseconds field is derived from nanosecond remainder and is safe within one second. `local_clock()` may have CPU-local behavior on some platforms, so cross-CPU callback migration could expose tiny discontinuities depending on architecture. Remove can block if `spi_target_abort()` does not terminate the queued async message. There is no timeout or flow control beyond SPI core completion.

## Test Signals

Validate big-endian encoding, monotonic progression across repeated host reads, behavior under fast polling, remove while a message is pending, SPI error completion, and target abort. Tests should also compare returned seconds/microseconds against kernel uptime within reasonable scheduling tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-slave-time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sn-f-ospi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sn-f-ospi.c

## Purpose

`spi-sn-f-ospi.c` is a SPI memory controller driver for Socionext F_OSPI flash hardware. It implements `spi_mem` indirect operations for single, dual, quad, and octal bus widths, with per-operation frequency support, but it does not implement interrupt-driven or DMA data movement.

## Important APIs, Types, and Functions

`struct f_ospi` holds MMIO base, device, clock, and a mutex protecting configuration and transfers. Configuration helpers include `f_ospi_prepare_config()`, `f_ospi_unprepare_config()`, `f_ospi_config_clk()`, `f_ospi_get_mode()`, and `f_ospi_config_indir_protocol()`. Transfer helpers are `f_ospi_indir_read()`, `f_ospi_indir_write()`, `f_ospi_indir_start_xfer()`, `f_ospi_indir_stop_xfer()`, and `f_ospi_indir_wait_xfer_complete()`.

The `spi_controller_mem_ops` table provides `adjust_op_size`, `supports_op`, and `exec_op`. Probe uses `devm_spi_alloc_host()`, maps registers, enables the clock, initializes hardware via `f_ospi_init()`, and registers the controller.

## Control Flow

Each indirect operation locks the controller, stops the internal clock and waits until AXI is idle/SPI clock stopped, programs the requested clock divisor, chip select, command/address/data bus widths, bit order, sample edge, data unit size, direction, address size, dummy cycles, address, opcode, and relevant IRQ status bits, then restarts the internal clock. Read starts the transfer and polls `READ_BUF_READY` for each byte, reading from `OSPI_DAT`; write polls `WRITE_BUF_READY` and writes one byte at a time. No-data writes start and then wait for transaction completion. Completion is detected by polling `CS_TRANS_COMP`, then the status bit is cleared.

## State and Persistence Behavior

There is no persistent storage. Controller state is hardware register configuration protected by `mlock`. Probe disables boot signal mode and all IRQ status/output bits; transfers program protocol state per operation. The device clock is acquired enabled and is not runtime-managed.

## Dependencies and Integration Points

The driver depends on platform device resources, device tree compatible `socionext,f-ospi`, clocks, MMIO polling, mutexes, and `spi_mem`. It advertises up to four chip selects and per-operation frequency capability.

## Risks and Edge Cases

The timeout constants are named in milliseconds but passed as the timeout argument to `readl_poll_timeout()`, whose timeout is in microseconds; this makes several waits much shorter than the names imply. Data movement is byte-at-a-time despite data-unit programming, which may be correct for the FIFO contract but limits throughput. `FIELD_PREP()` is used with single-bit data-rate masks and zero values, which is harmless but easy to misread. Unsupported directions only warn in lower helpers; `exec_op` returns `-EOPNOTSUPP` for unknown directions. Address sizes over four bytes and dummy cycles over 255 are rejected.

## Test Signals

Validate `spi_mem` opcode/address/dummy/data combinations for 1-1-1, dual, quad, and octal widths; all chip selects; per-operation clock rates; no-data commands; reads/writes at `OSPI_DAT_SIZE_MAX`; address nbytes rejection; dummy-cycle rejection; and poll timeout behavior with hardware stalled in AXI-active, clock-stopped, buffer-ready, and transaction-complete states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sn-f-ospi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sprd-adi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sprd-adi.c

## Purpose

`spi-sprd-adi.c` implements the Spreadtrum ADI controller as a specialized SPI host used to access PMIC-style analog/digital interface slave registers. It also provides platform restart support by programming PMIC watchdog registers through the ADI bus.

## Important APIs, Types, and Functions

`struct sprd_adi` stores the SPI controller, device, MMIO base, optional hardware spinlock, virtual/physical slave register windows, and SoC data. `struct sprd_adi_data` defines slave address offset/size, readback validation, restart callback, and watchdog reset-mode callback. Read/write primitives are `sprd_adi_read()` and `sprd_adi_write()`, protected by the optional hardware spinlock and bounded by `sprd_adi_check_addr()`. `sprd_adi_transfer_one()` maps SPI transfers into either a register read or write using 32-bit buffer conventions.

Restart helpers `sprd_adi_restart()` and `sprd_adi_restart_sc9860()` record reboot mode in PMIC reset-status registers and trigger the PMIC watchdog. `sprd_adi_hw_init()` programs channel priority, clock-gating mode, and optional `sprd,hw-channels` device-tree channel configuration.

## Control Flow

Probe obtains SoC match data, maps the ADI register block, calculates slave register virtual and physical windows, requests an optional hardware spinlock, initializes hardware channel settings, optionally tags watchdog reset mode, registers a half-duplex SPI controller, and registers a restart handler for SoCs that provide one. Transfers are nonstandard: for read, the RX buffer initially contains the register offset and is overwritten with the read value; for write, the TX buffer contains register offset followed by value.

Reads write `REG_ADI_RD_CMD`, poll `REG_ADI_RD_DATA` until busy clears, optionally verify returned address bits, and return the 16-bit value. Writes drain the FIFO, wait for not-full, then write the value through the slave virtual register window.

## State and Persistence Behavior

Kernel state is per-controller and non-persistent. Hardware channel configuration and PMIC register writes can have lasting effects in PMIC state. Restart writes reboot reason/status and watchdog configuration that affect the next boot. No local filesystem persistence exists.

## Dependencies and Integration Points

The file depends on platform resources, OF match data, optional hardware spinlocks for multi-master ADI arbitration, reboot/sys-off infrastructure, MMIO polling, and the SPI controller API. Child device count determines chip select count, but the transfer protocol is register-oriented rather than byte-stream SPI.

## Risks and Edge Cases

The transfer ABI assumes buffers are at least 32 bits for reads and 64 bits for writes, with no explicit length validation. `sprd_adi_write()` writes only a 16-bit value conceptually but accepts a 32-bit `val`; upper bits may be ignored by hardware or cause surprises. Hardware spinlock timeouts are long and occur in transfer path. Restart ignores read/write failures, so watchdog reset programming may partially fail before the one-second delay. Device-tree channel list parsing assumes pairs of big-endian cells and silently ignores channels 0 and 1.

## Test Signals

Test read/write bounds for each address-mode compatible, readback validation for r2/r3 formats, absent and present hardware spinlock paths, FIFO full/drain timeout, child count to chip-select mapping, PMIC watchdog restart commands for each reboot mode string, optional `sprd,hw-channels` programming, and malformed SPI transfer lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sprd-adi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sprd.c

## Purpose

`spi-sprd.c` is the Spreadtrum SPI host controller driver for `sprd,sc9860-spi`. It supports PIO and DMA transfers, CPOL/CPHA, 3-wire mode, dual TX line mode, runtime PM, and FIFO-length chunking.

## Important APIs, Types, and Functions

`struct sprd_spi` stores MMIO/physical base, clock, IRQ, source/hardware speed, transfer mode, word delay, current buffers, DMA state, and completion. `struct sprd_spi_dma` tracks RX/TX DMA channels, bus width, fragment length, and RX length. Setup and transfer are split across `sprd_spi_setup_transfer()`, `sprd_spi_init_hw()`, `sprd_spi_txrx_bufs()` for PIO, and `sprd_spi_dma_txrx_bufs()` for DMA. Buffer accessors handle 8-, 16-, and 32-bit words. IRQ handling completes DMA transfers and reads any RX tail not covered by DMA.

## Control Flow

Probe allocates a SPI host, maps registers, initializes clocks, IRQ, and optional DMA, enables runtime PM, resumes the controller, and registers it. `transfer_one` records buffers, configures hardware mode, speed, bits per word, transfer length, RX/TX mode, word delay, FIFO reset, and then chooses DMA when available and transfer length exceeds the 32-byte FIFO. PIO transfers loop in FIFO-sized chunks, set TX or RX length registers, write TX data or trigger receive-only mode, poll TX/RX completion, read RX FIFO, and enter idle. DMA transfers enable interrupts, configure TX and/or RX DMA descriptors, program length registers, enable DMA, wait for completion, then disable DMA/IRQs and enter idle.

## State and Persistence Behavior

State is volatile per-controller runtime state plus hardware registers. Runtime suspend releases DMA channels and disables the enable clock; runtime resume re-enables the clock and reacquires DMA channels when DMA was enabled. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on platform resources, OF aliasing, clocks named `spi`, `source`, and `enable`, DMAengine with Spreadtrum DMA flags, IRQs, completions, runtime PM, and the SPI core. It registers `set_cs`, `transfer_one`, and `can_dma`.

## Risks and Edge Cases

`sctlr->max_speed_hz` is set before `sprd_spi_clk_init()` initializes `ss->src_clk`, so the advertised max speed can be based on zero. `sprd_spi_clk_init()` calls `clk_set_parent(clk_spi, clk_parent)` even if optional clock lookups failed and set those pointers to NULL; that relies on clock API tolerance. DMA wait has no timeout. Runtime suspend releases DMA channels while `ss->dma.enable` remains true, then resume reacquires them; error handling for later transfers after failed reacquire depends on runtime PM returning failure. Transfer length conversions for 16/32-bit frames use right shifts, so invalid odd byte lengths are not explicitly rejected.

## Test Signals

Exercise PIO and DMA transfers above/below FIFO size, RX-only, TX-only, full duplex, 3-wire TX/RX, dual TX line mode, 8/16/32-bit frames including unaligned lengths, word-delay units and clamp bounds, DMA tail RX handling, runtime suspend/resume with DMA channel loss, missing optional clocks, and IRQ timeout/hang scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-st-ssc4.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-st-ssc4.c

## Purpose

`spi-st-ssc4.c` is a host-mode SPI driver for the STMicroelectronics SSC4 serial controller. It uses FIFO/interrupt-driven PIO, GPIO chip selects, runtime PM, and supports 8- and 16-bit transfers with CPOL/CPHA, LSB-first, loopback, and CS-high modes.

## Important APIs, Types, and Functions

`struct spi_st` stores MMIO base, SSC clock, device, current TX/RX pointers, bytes per word, remaining word count, current baud rate, and completion. `spi_st_setup()` configures baud rate, mode bits, data width, loopback, FIFO enable, and controller enable. `spi_st_transfer_one()` sets per-transfer pointers, chooses 8- or 16-bit packing, preloads TX FIFO, enables TX-empty interrupt, waits for completion, restores control register if it temporarily packed even 8-bit transfers as 16-bit, finalizes the transfer, and returns the byte count. `spi_st_irq()` drains RX FIFO, refills TX FIFO, and completes when words are exhausted.

## Control Flow

Probe allocates a host, gets and enables the SSC clock, maps registers, disables I2C mode, resets SSC, temporarily sets target mode before pin reconfiguration, maps the IRQ, enables runtime PM, and registers the controller. Setup requires `max_speed_hz` and a valid CS GPIO, computes `SSC_BRG`, writes mode/data-width bits into `SSC_CTL`, enables TX/RX FIFOs and the controller, and clears stale status by reading `SSC_RBUF`. Transfers proceed FIFO-batch by FIFO-batch under IRQ control.

## State and Persistence Behavior

No persistent storage exists. Per-device setup writes global controller registers, so configuration is changed for each SPI device setup. Runtime suspend disables interrupts, selects sleep pinctrl state, and disables the clock; runtime resume re-enables the clock and default pinctrl state.

## Dependencies and Integration Points

The driver depends on platform/OF resources, `irq_of_parse_and_map()`, clocks, pinctrl PM states, GPIO descriptors for chip select, completions, and the SPI controller API. It sets `auto_runtime_pm` and `use_gpio_descriptors`.

## Risks and Edge Cases

`spi_st_transfer_one()` waits without timeout, so missing TX-empty interrupts can hang. It returns `t->len` after calling `spi_finalize_current_transfer()`, whereas modern `transfer_one` implementations typically return 0 when complete; this pattern may rely on SPI core compatibility. Even-length 8-bit transfers are packed as 16-bit words, which changes byte ordering through `ssc_write_tx_fifo()`/`ssc_read_rx_fifo()` and needs device-level validation. Setup rejects devices without GPIO CS, so native-CS designs are unsupported.

## Test Signals

Test 8-bit odd/even lengths, 16-bit transfers, TX-only, RX-only, full duplex, CPOL/CPHA combinations, LSB-first, loopback, CS-high via GPIO descriptors, baud-rate min/max rejection, runtime suspend/resume, missing IRQ, and interrupt loss while a transfer is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-st-ssc4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-stm32-ospi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-stm32-ospi.c

## Purpose

`spi-stm32-ospi.c` is the STM32MP25 OCTO SPI memory controller driver. It targets SPI NOR/NAND flash subnodes, supports `spi_mem` exec, status polling, direct-map reads, single/dual/quad/octal widths, DMA fallback to polling, GPIO chip-select message emulation, runtime PM, reset control, and optional reserved-memory mapping for memory-mapped reads.

## Important APIs, Types, and Functions

`struct stm32_ospi` stores controller/device handles, clock/reset, IRQ, MMIO and memory-map regions, DMA channels and completions, per-CS prescalers, cached CR/DCR state, current functional mode, status timeout, and a mutex. Key helpers include `stm32_ospi_abort()`, `stm32_ospi_poll()`, `stm32_ospi_wait_cmd()`, `stm32_ospi_tx_dma()`, `stm32_ospi_xfer()`, `stm32_ospi_wait_poll_status()`, and `stm32_ospi_send()`. `stm32_ospi_mem_ops` provides `exec_op`, `dirmap_create`, `dirmap_read`, and `poll_status`.

## Control Flow

Probe first validates that one or two flash children are present, allocates a host, gathers MMIO/clock/IRQ/reset/DMA/reserved-memory resources, configures DMA, initializes the mutex and SPI controller fields, enables runtime PM, acquires/deasserts reset, and registers the controller. Setup records per-CS prescaler and writes base CR/DCR1. `exec_op` chooses indirect read or write mode, locks, and calls `stm32_ospi_send()`. `poll_status` programs match/mask registers and automatic-poll mode. Direct-map reads choose memory-mapped mode when the requested range fits the mapped window, otherwise indirect read.

`stm32_ospi_send()` selects CS and functional mode, programs data length, prescaler, command/address/dummy/data bus widths, instruction register, address register, optional auto-poll wait, and data transfer. Data transfer uses memory copy, DMA, or FIFO polling. On errors or memory-mapped reads it aborts and clears flags.

## State and Persistence Behavior

State is volatile. The driver caches CR and DCR1 for resume, stores per-CS prescalers, and keeps DMA channels until remove. Runtime suspend only gates the clock. System suspend releases reset and force-suspends runtime PM; resume reacquires reset and restores cached CR/DCR1.

## Dependencies and Integration Points

The file depends on `spi_mem`, DMAengine, reserved-memory mapping, GPIO descriptors, reset controls, clocks, IRQ completions, mutexes, pinctrl PM, and runtime PM. It integrates with flash drivers through `spi_mem` and can emulate simple SPI messages by converting transfers into `spi_mem_op` structures.

## Risks and Edge Cases

In `stm32_ospi_resume()`, if `reset_control_acquire()` fails after `pm_runtime_resume_and_get()`, the function returns without dropping the runtime PM reference. `stm32_ospi_send()` updates `OSPI_DCR2` with `|=` for the prescaler without clearing `DCR2_PRESC_MASK`, so changing to a lower prescaler after a higher one can leave stale bits. Direct-map address bound uses `addr + nbytes + 1`, which is conservative but can overflow a 32-bit `addr_max`. DMA has a timeout; FIFO polling also has bounded timeouts.

## Test Signals

Validate one and two flash child nodes, invalid flash-node counts, all supported bus widths, per-CS prescaler changes, indirect read/write, status polling completion and false-timeout handling, direct-map read bounds, GPIO-CS message emulation with dummy transfers, DMA success/fallback/timeout, suspend/resume error branches, and reset acquire/release sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-stm32-ospi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-stm32-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-stm32-qspi.c

## Purpose

`spi-stm32-qspi.c` is the STM32 QuadSPI memory controller driver for `st,stm32f469-qspi`. It implements `spi_mem` operations, status polling, direct-map reads through the memory-mapped aperture, DMA/polling data movement, GPIO-CS message emulation, runtime PM, and reset handling for up to two NOR flash chip selects.

## Important APIs, Types, and Functions

`struct stm32_qspi` tracks the SPI controller, MMIO and memory-map bases, clock/rate, per-flash CS and prescaler, completions, functional mode, DMA channels, cached CR/DCR state, status timeout, and a mutex. Data paths are `stm32_qspi_tx_poll()`, `stm32_qspi_tx_dma()`, and `stm32_qspi_tx_mm()`. Command sequencing is centralized in `stm32_qspi_send()`, with helpers for busy waits, command completion, automatic-poll match completion, and abort. `stm32_qspi_mem_ops` supplies `exec_op`, `dirmap_create`, `dirmap_read`, and `poll_status`.

## Control Flow

Probe maps the register and memory-map resources, requests IRQ, enables the clock, optionally resets the controller, sets up DMA channels, configures controller hooks, enables runtime PM, and registers the SPI controller. Setup validates speed and dual-flash GPIO requirements, computes a per-chip prescaler, writes base CR and max DCR FSIZE. `exec_op` resumes runtime PM, locks, sets indirect read/write mode, sends the operation, unlocks, and autosuspends. `poll_status` programs PSMKR/PSMAR, sets automatic-poll mode, and sends. Direct-map read builds a local op with requested offset/length and selects memory-mapped mode when it fits in `mm_size`.

## State and Persistence Behavior

There is no persistent storage. Runtime state consists of per-CS prescalers, cached CR/DCR for resume, functional mode, DMA channel availability, and in-flight completions. Runtime suspend gates the clock; system resume restores cached CR/DCR after force-resuming PM.

## Dependencies and Integration Points

The driver depends on `spi_mem`, DMAengine, GPIO descriptors, reset controls, named memory resources `qspi` and `qspi_mm`, IRQ completions, mutexes, pinctrl PM, and runtime PM. It integrates with flash drivers through `spi_mem` and with the generic SPI message path by translating dummy/data transfers to memory operations.

## Risks and Edge Cases

`stm32_qspi_send()` returns only `err` after abort; if `err_poll_status` or abort timeout occurs while `err` is zero, the error can be logged but reported as success. The direct-map bound check uses `addr + nbytes + 1` in a 32-bit variable, which can overflow and is stricter than a typical inclusive end check. DMA setup returns immediately on `dma_get_slave_caps()` errors without releasing already acquired channels in those branches. Polling/status IRQ handling always returns `IRQ_HANDLED`, even for interrupts without `SR_SMF`.

## Test Signals

Test exec reads/writes, no-data commands, automatic status polling success/timeout/error propagation, direct-map reads at aperture boundaries, dual-flash mode requiring CS GPIOs, DMA RX/TX success and fallback to polling, DMA timeout, suspend/resume CR/DCR restore, reset failure, and message emulation with dummy bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-stm32-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-stm32.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-stm32.c

## Purpose

`spi-stm32.c` is the main STM32 SPI controller driver covering STM32F4, STM32F7, STM32H7, and STM32MP25 variants. It supports host mode and, for H7/MP25-style compatibles, target mode; PIO, interrupt, polling, DMA, and optional RX DMA/MDMA chaining through SRAM; runtime PM; GPIO chip selects; and variant-specific register layouts.

## Important APIs, Types, and Functions

`struct stm32_spi_regspec` describes variant register offsets and bit masks. `struct stm32_spi_cfg` binds variant operations for FIFO sizing, BPW masks, disable/config, BPW/mode/data-idleness/TSIZE setup, FIFO access, DMA start/callbacks, IRQ handlers, divisors, feature flags, and DMA-burst policy. `struct stm32_spi` holds controller state, MMIO/clock/IRQ, FIFO size, feature set, current transfer parameters, DMA channels, optional SRAM pool and MDMA channel.

Core SPI hooks are `stm32_spi_prepare_msg()`, `stm32_spi_transfer_one()`, `stm32_spi_unprepare_msg()`, and `stm32_spi_optimize_message()`. Variant data paths include F4/F7 data-register access, H7 FIFO access, FX and H7 IRQ handlers, H7 polling, and DMA setup/start/callback helpers. Probe selects config from OF match data, allocates host or target controller, maps resources, requests threaded IRQ, enables clock/reset, detects FIFO and feature set, configures the controller, requests DMA channels, optional SRAM/MDMA resources, enables runtime PM, and registers.

## Control Flow

Preparation programs CPOL/CPHA/LSB-first/CS-high/RDY bits and optional inter-data idleness. Each transfer records TX/RX buffers, determines DMA eligibility, sets BPW, baud divisor, communication type, mode registers, optional data idleness, and H7/MP25 TSIZE. Transfer then chooses DMA, short-transfer polling, or IRQ. DMA prepares RX before TX, optionally chains RX DMA into SRAM with MDMA to final memory, enables DMA request bits, starts channels, enables SPI, and completes through DMA callbacks or SPI EOT IRQ depending on mode. IRQ paths service TX/RX FIFO/data-register events, handle overrun/mode fault/suspend, disable hardware, and finalize transfers.

## State and Persistence Behavior

All state is volatile. The driver maintains current transfer state under a spinlock and caches variant/feature information. Runtime suspend disables the clock and selects sleep pinctrl; resume restores default pinctrl and clock. Remove unregisters, disables hardware, disables PM, releases DMA/MDMA channels, frees SRAM buffer, and selects sleep pins.

## Dependencies and Integration Points

The driver integrates deeply with the Linux SPI core, DMAengine, genalloc SRAM pools, pinctrl, reset controls, runtime PM, threaded IRQs, and device tree properties including `spi-slave`, `st,spi-midi-ns`, and `sram`. It exposes standard SPI devices in host mode and target-mode handlers in device mode.

## Risks and Edge Cases

Several callbacks finalize transfers from IRQ, DMA callback, or polling paths, so double-finalization and disable ordering are key risks. DMA fallback from descriptor preparation clears RX DMA request but may leave TX request state dependent on which failure label is taken. `stm32_spi_prepare_rx_dma_mdma_chaining()` uses `GFP_ATOMIC` and temporary SG tables while under spinlock, increasing allocation-failure sensitivity. In probe error cleanup, `gen_pool_free()` is called when `spi->sram_pool` exists, even if allocation failed and `sram_rx_buf` is NULL. The MP25 config omits `.write_tx` and `.read_rx`, yet inherits H7 IRQ/poll transfer functions that call those hooks when PIO is used, which is a strong null-callback risk unless MP25 always uses DMA or the missing assignments are intentional elsewhere.

## Test Signals

Build and boot-test all compatibles. Exercise host and target mode, 4- through 32-bit BPW where supported, CPOL/CPHA/LSB/CS-high/RDY, 3-wire TX/RX, simplex/full-duplex, short polling, IRQ PIO, DMA TX/RX/full-duplex, DMA fallback, MDMA chaining with SRAM, transfer splitting at TSIZE limits, overrun/mode-fault/suspend IRQs, runtime/system PM, probe deferral and partial resource cleanup, and MP25 limited/full feature detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-stm32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sun4i.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sun4i.c

## Purpose

`spi-sun4i.c` is the Allwinner A10/A20 SPI host controller driver. It implements interrupt-driven PIO transfers for 8-bit words with manual chip select, CPOL/CPHA, CS-high, LSB-first, runtime PM clock gating, and a 64-byte FIFO.

## Important APIs, Types, and Functions

`struct sun4i_spi` stores the SPI controller, MMIO base, AHB/module clocks, completion, and current TX/RX buffer state. Register helpers wrap `readl()`/`writel()`. FIFO helpers `sun4i_spi_fill_fifo()` and `sun4i_spi_drain_fifo()` move bytes to/from hardware. SPI hooks are `sun4i_spi_set_cs()`, `sun4i_spi_transfer_one()`, and `sun4i_spi_max_transfer_size()`. `sun4i_spi_handler()` handles transfer complete, RX FIFO 3/4 full, and TX FIFO 3/4 empty interrupts. Probe maps resources, requests IRQ, gets clocks, initializes runtime PM, and registers the host.

## Control Flow

Runtime resume enables AHB and module clocks and sets master/TX-pause defaults. `set_cs` selects the chip, enables manual CS, sets the requested level, and updates inactive polarity. A transfer rejects lengths beyond the 24-bit hardware counter, clears interrupts, resets FIFOs, programs mode bits, enables/disables discard-hash-burst for TX-only, enables the controller, adjusts the module clock if necessary, chooses CDR2 or CDR1 divider, programs burst/transmit counts, preloads up to FIFO depth minus one, enables TC and RX FIFO interrupts plus TX FIFO interrupt when needed, starts exchange, and waits with a computed timeout. The IRQ drains/fills FIFO and completes on TC.

## State and Persistence Behavior

State is volatile and per-controller. Runtime PM gates clocks while idle. Transfer-specific buffer pointers and remaining length live in `struct sun4i_spi`. Hardware registers are reprogrammed on each transfer and clocks are disabled during runtime suspend.

## Dependencies and Integration Points

The driver depends on platform/OF matching (`allwinner,sun4i-a10-spi`), clocks named `ahb` and `mod`, MMIO, IRQs, completions, runtime PM, GPIO descriptors, and the SPI core. It advertises four chip selects and max transfer size one less than the 24-bit counter maximum.

## Risks and Edge Cases

The timeout calculation divides by `tfr->speed_hz / 1000`; speeds below 1000 Hz would divide by zero, though the controller advertises a 3 kHz minimum. `platform_get_irq()` errors are collapsed to `-ENXIO`, losing deferral details. `clk_set_rate()` return value is ignored when trying to raise module clock. On timeout, interrupts are disabled but the exchange bit or FIFO state is not explicitly reset until a later transfer. RX-only transfers use zero-filled TX bytes from `sun4i_spi_fill_fifo()`, which is expected for SPI but should be tested.

## Test Signals

Test all mode bits, manual CS levels and inactive polarity, RX-only/TX-only/full-duplex transfers, lengths around FIFO depth and maximum counter, low/high speed divisor selection, module clock rate adjustment failure, timeout handling, runtime suspend/resume, missing clocks/IRQ, and interrupt sequencing where RX FIFO and TC arrive close together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sun4i.c -->
