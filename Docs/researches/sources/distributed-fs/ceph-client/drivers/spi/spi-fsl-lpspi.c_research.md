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
