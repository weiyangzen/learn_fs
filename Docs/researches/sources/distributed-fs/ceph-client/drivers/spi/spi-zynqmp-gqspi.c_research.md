<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-zynqmp-gqspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-zynqmp-gqspi.c

## Purpose

`spi-zynqmp-gqspi.c` is the SPI memory controller driver for Xilinx Zynq UltraScale+ MPSoC and Versal GQSPI hardware. It drives generic FIFO command entries, supports single/dual/quad bus widths, up to two chip selects, per-operation frequency changes, RX DMA for aligned larger reads, runtime PM, and platform-specific tap-delay programming.

The driver is host-mode only and exposes the controller through `spi-mem` rather than generic SPI message transfers.

## Important APIs, Types, and Functions

`struct zynqmp_qspi` stores the SPI controller, MMIO base, clocks, IRQ, device, active TX/RX buffers and counters, selected GENFIFO CS/bus bits, RX DMA byte count and mapped address, current GENFIFO entry, IO-vs-DMA mode, completion, operation mutex, current speed, and tap-delay quirk flag. `struct qspi_platform_data` stores match quirks; Versal enables `QSPI_QUIRK_HAS_TAPDELAY`.

Register and mask definitions cover GQSPI config/status/interrupt/enable, TX/RX data, generic FIFO, FIFO control/thresholds, QSPI DMA destination registers, tap-delay registers, mode bits, chip-select/bus select bits, DMA alignment, speed thresholds, and PM timeout.

Core helpers include `zynqmp_gqspi_read()`, `zynqmp_gqspi_write()`, `zynqmp_gqspi_selecttarget()`, `zynqmp_qspi_set_tapdelay()`, `zynqmp_qspi_init_hw()`, `zynqmp_qspi_chipselect()`, `zynqmp_qspi_selectspimode()`, `zynqmp_qspi_config_op()`, `zynqmp_qspi_filltxfifo()`, `zynqmp_qspi_readrxfifo()`, `zynqmp_qspi_fillgenfifo()`, `zynqmp_qspi_setuprxdma()`, `zynqmp_qspi_write_op()`, `zynqmp_qspi_read_op()`, `zynqmp_qspi_irq()`, and `zynqmp_qspi_exec_op()`.

PM hooks are `zynqmp_qspi_suspend()`, `zynqmp_qspi_resume()`, `zynqmp_runtime_suspend()`, and `zynqmp_runtime_resume()`. Probe/remove manage clocks, runtime PM, IRQ, DMA mask, and SPI controller registration.

## Control Flow

Probe allocates a devm SPI host, stores private state as platform data, reads match quirks, maps registers, obtains clocks, enables clocks, initializes completion and operation mutex, enables runtime PM with autosuspend, initializes controller mode/speed, configures GQSPI hardware, requests IRQ, sets a 44-bit DMA mask, validates optional `num-cs`, fills SPI MEM callbacks/capabilities, registers the controller, and puts the device into autosuspend.

Hardware init selects GQSPI mode, clears/disable interrupts and DMA status, disables the controller, programs manual GENFIFO start, little-endian TX FIFO, clock phase/polarity defaults, baud divisor for current speed, tap delays through firmware or local registers, resets FIFOs, sets thresholds, selects lower CS/bus by default, initializes destination DMA control, and enables the controller.

`exec_op` serializes operations with `op_lock`, updates speed/tap delay if needed, asserts chip select through GENFIFO CS setup, builds a base GENFIFO entry from current CS/bus, and executes command, address, dummy, and data phases. Write-like phases fill GENFIFO length entries, preload TX FIFO, start GENFIFO, enable TX/GENFIFO interrupts, and wait for completion using a size-derived timeout. Read data phases choose DMA when the RX buffer is 4-byte aligned and at least eight bytes; otherwise they use IO-mode RX interrupts. DMA completion unmaps the buffer, accounts bytes, disables DMA interrupt, and switches to IO for trailing unaligned bytes.

The IRQ handler clears GQSPI status, reads DMA status in DMA mode, services TX-not-full by filling TX FIFO, handles DMA done through `zynqmp_process_dma_irq()`, drains RX FIFO for IO reads when GENFIFO is empty enough, and completes the phase when TX/RX counters reach zero and the expected interrupt mask is present.

System suspend suspends the SPI controller and disables GQSPI; resume re-enables and resumes. Runtime suspend disables clocks; runtime resume enables clocks.

## State and Persistence Behavior

No file-backed state is used. Persistent hardware state includes current speed divisor, tap-delay configuration, selected CS/bus bits, FIFO thresholds, DMA control, and enable state. Runtime PM can disable clocks between operations; operation state is re-established through setup/init paths.

Per-operation state is kept in buffer pointers, byte counters, GENFIFO entry, DMA address, DMA byte count, and mode. External SPI flash contents may be persistently changed by program/erase operations sent through `spi-mem`.

## Dependencies and Integration Points

The driver depends on platform/OF matching (`"xlnx,zynqmp-qspi-1.0"` and `"xlnx,versal-qspi-1.0"`), clocks, MMIO, IRQs, DMA mapping, firmware API `zynqmp_pm_set_tapdelay_bypass()`, runtime PM, completions, mutexes, and SPI MEM.

SPI integration uses `mem_ops.exec_op`, `mem_caps.per_op_freq`, `setup`, automatic runtime PM, mode bits for CPOL/CPHA and dual/quad TX/RX, and 8-bit words. DMA integration is register-level destination DMA rather than DMAengine.

## Risks and Edge Cases

`zynqmp_qspi_filltxfifo()` appears to update `count` after setting `bytes_to_transfer = 0` in the short trailing-byte branch, so `count += xqspi->bytes_to_transfer` adds zero. The loop still exits because bytes become zero, but accounting is confusing and should be reviewed.

The command phase stores a 16-bit `opcode` and transmits `op->cmd.nbytes`; most SPI MEM commands are one byte, but multi-byte command assumptions should be tested for byte order. Address bytes are staged in a local `u64 opaddr`, which avoids the Zynq driver's scratch-buffer problem.

Completion requires both byte counters to reach zero and a specific interrupt-mask pattern. Unexpected hardware status ordering can cause timeouts even after data movement. RX DMA is used only for aligned reads and leaves remainder bytes for IO mode; transition correctness is important.

Tap-delay programming differs between ZynqMP firmware calls and Versal local registers. Errors from firmware tap-delay calls are ignored, so bad firmware responses may silently degrade high-speed timing.

Runtime PM error paths are complex: probe calls `pm_runtime_get_sync()` and multiple error labels disable PM/clocks. Remove calls `pm_runtime_get_sync()` without checking its return. These paths need fault-injection coverage.

## Test Signals

Tests should cover ZynqMP and Versal compatibles, tap-delay branches at 37.5/40/100/150 MHz thresholds, one and two chip selects, lower/upper bus selection, command/address/dummy/data phase combinations, single/dual/quad bus widths, per-operation speed changes, TX writes, RX IO reads, aligned RX DMA reads, unaligned and short RX reads, DMA remainder transition, timeouts, runtime autosuspend/resume, system suspend/resume, invalid `num-cs`, DMA mask failure, and IRQ ordering.

Static analysis should inspect TX FIFO trailing-byte accounting, ignored tap-delay firmware return values, runtime PM unwind paths, and completion conditions in the IRQ handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-zynqmp-gqspi.c -->
