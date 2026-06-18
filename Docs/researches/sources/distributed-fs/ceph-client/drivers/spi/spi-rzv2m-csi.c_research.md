# sources/distributed-fs/ceph-client/drivers/spi/spi-rzv2m-csi.c

## Purpose

`spi-rzv2m-csi.c` is a Renesas RZ/V2M Clocked Serial Interface driver exposing CSI as a SPI controller. It supports host and target modes, 8- and 16-bit words, interrupt-driven PIO transfers, optional SS pin handling in target mode, software reset, and CSI clock divisor programming.

## Important APIs, Types, and Functions

`struct rzv2m_csi_priv` holds MMIO base, CSI and peripheral clocks, device/controller pointers, active TX/RX buffers, transfer counters, bytes-per-word, waitqueue, error/status bits, target-abort flag, and SS-pin policy. Register helpers include `rzv2m_csi_reg_write_bit()`, `rzv2m_csi_sw_reset()`, and `rzv2m_csi_start_stop_operation()`.

Transfer functions include FIFO fill/read/empty helpers, current chunk calculation, RX trigger setup, IRQ enable/disable/clear helpers, wait helpers, `rzv2m_csi_irq_handler()`, clock and operating-mode setup, device `setup()`, `rzv2m_csi_pio_transfer()`, `rzv2m_csi_transfer_one()`, and `rzv2m_csi_target_abort()`.

## Control Flow

Probe chooses host or target allocation based on `spi-slave`, decides whether to use the SS pin for target mode from `renesas,csi-no-ss`, maps registers, gets IRQ, clocks, and shared reset, initializes the waitqueue, assigns SPI hooks, requests IRQ, deasserts reset without asserting it for shared-reset safety, puts the IP into software reset, enables `csiclk`, and registers the controller.

Device setup deasserts reset, writes base mode, programs CPOL/CPHA, bit order, host/target role, SS polarity/enable, performs a software reset pulse, then briefly enables/disables communication so the clock line settles. Each transfer records buffers/length, programs transmit-receive or receive-only mode and word length, sets host clock divisor, then runs chunked PIO. The PIO loop clears FIFOs/status, enables RX triggers and error IRQs, computes a power-of-two chunk no larger than FIFO capacity, fills TX FIFO or dummy clocks, starts operation, waits for RX trigger or target abort, stops in host mode, drains/copies RX FIFO, and repeats until done.

## State and Persistence Behavior

All state is runtime-only: buffer pointers, bytes sent/received, current chunk sizing, error bits, IRQ status, target abort flag, and clock divisor. The driver has no persistence. Because reset is shared with hardware outside Linux control, probe only deasserts it and later uses CSI software reset for local cleanup.

## Dependencies and Integration Points

The driver uses platform/OF, clocks, reset controls, waitqueues, interrupts, polling helpers, and SPI core host/target APIs. It uses GPIO descriptors through the SPI core and exposes active-high CS support. It does not use DMA.

## Risks and Edge Cases

`rzv2m_csi_calc_current_transfer()` rounds chunk size down to a power of two; zero-length or badly aligned lengths would be problematic, though normal SPI transfers have positive lengths and supported 8/16-bit words. Target-mode waits are interruptible and return `-EINTR` on abort. FIFO level checks are strict; unexpected hardware levels produce `-EIO`. `rzv2m_csi_setup_clock()` may change `csiclk` up or down to satisfy the PCLK/2 restriction, so shared clock consumers need consideration. Only `csiclk` is explicitly enabled, while `pclk` is used for rate decisions after acquisition.

## Test Signals

Test host and target modes, with and without SS pin, 8- and 16-bit transfers, RX-only and TX/RX transfers, non-FIFO-multiple lengths, overflow/underrun IRQ injection, target abort during wait, clock requests above 8 MHz and near divisor limits, setup polarity/phase combinations, shared-reset behavior, and remove after active/failed transfer.
