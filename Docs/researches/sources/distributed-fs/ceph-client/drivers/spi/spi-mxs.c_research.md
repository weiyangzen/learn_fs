<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mxs.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mxs.c

## Purpose

`spi-mxs.c` is the Freescale/NXP MXS SSP-based SPI host driver for i.MX23 and i.MX28. It exposes a half-duplex SPI controller backed by the shared MXS SSP block, using PIO for small transfers and DMAengine with MXS-specific PIO descriptors for larger transfers.

## Important APIs, Types, and Functions

`struct mxs_spi` embeds `struct mxs_ssp`, a completion, and the last requested SCK rate. `mxs_spi_setup_transfer()` programs clock, SSP SPI mode, word length, CPOL/CPHA, and command registers. `mxs_spi_cs_to_reg()` maps chip-select index to SSP control bits. `mxs_ssp_wait()` polls register bits with a 10-second timeout.

Data paths are `mxs_spi_txrx_pio()` and `mxs_spi_txrx_dma()`. DMA completion is signaled by `mxs_ssp_dma_irq_callback()`, while `mxs_ssp_irq_handler()` logs unexpected SSP IRQ state. `mxs_spi_transfer_one()` implements the message loop. Probe allocates the controller, maps MMIO, obtains clock and DMA channel, enables runtime PM, resets the SSP block, and registers the controller. Remove unregisters, disables PM, releases DMA, and drops the controller reference.

## Control Flow

For each message, the driver programs chip-select bits into `HW_SSP_CTRL0` and iterates transfers. Each transfer sets up clock and mode, records effective speed, computes whether CS should deassert at the end using last-transfer and `cs_change` state, then chooses PIO for transfers under 32 bytes and DMA otherwise.

PIO sends or receives one byte at a time by programming transfer count, READ direction, RUN, DATA_XFER, and optionally IGNORE_CRC as a CS-deassert signal. DMA allocates an array of per-segment PIO/scatterlist descriptors, splits vmalloc buffers by page or linear buffers by 0xff00 bytes, maps each segment, queues SSP PIO register writes and data moves to the MXS DMA channel, adds a callback to the last descriptor, starts DMA, waits for completion, and unmaps all mapped segments.

On transfer failure, the SSP block is reset and the message ends with error status. On success, `actual_length` is incremented and the message is finalized.

## State and Persistence Behavior

`spi->sck` caches the requested speed to reduce redundant clock programming. The embedded SSP state holds device, clock, base, DMA channel, and SoC id. Transfer descriptors and mappings are temporary. There is no host persistence; external SPI devices may be modified by writes.

Runtime PM and system sleep move pinctrl states and clock state. The SSP hardware is reset during probe and after failed messages.

## Dependencies and Integration Points

The driver integrates with the SPI core, device tree compatibles `fsl,imx23-spi` and `fsl,imx28-spi`, MXS SSP register definitions, STMP reset helpers, DMAengine, MXS DMA flags, clock framework, pinctrl PM, runtime/system PM, tracepoints, and optional regulator headers inherited from platform context.

## Risks and Edge Cases

The controller is half-duplex; if both TX and RX buffers are present, the code may run TX then RX sequentially for the same transfer rather than true simultaneous exchange. DMA error cleanup uses labels inside an unwind loop and must preserve correct `sg_count` semantics for all partial-queue failures. Vmalloc handling maps one page per segment and depends on `offset_in_page()` plus `PAGE_SIZE` segmentation. Very long fixed 10-second timeouts hide hangs but slow failure recovery.

CS handling uses SSP WAIT_FOR_CMD/WAIT_FOR_IRQ bits in SPI mode, which is hardware-specific and easy to regress when changing control-word setup.

## Test Signals

Tests should cover i.MX23 and i.MX28, all three chip selects, mode 0-3, sub-32-byte PIO TX/RX, DMA TX/RX for linear and vmalloc buffers, segment boundaries at page and 0xff00 sizes, `cs_change` on multi-transfer messages, DMA timeout and descriptor-prep failures, runtime/system suspend-resume, and block reset after failed transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mxs.c -->
