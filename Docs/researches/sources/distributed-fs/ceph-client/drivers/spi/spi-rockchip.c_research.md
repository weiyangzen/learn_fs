# sources/distributed-fs/ceph-client/drivers/spi/spi-rockchip.c

## Purpose

`spi-rockchip.c` is a generic Rockchip SPI controller driver supporting host and target modes, PIO and DMA transfer paths, native/GPIO chip selects, active-high support on newer IP, runtime PM, and common SPI modes. It targets the Rockchip DesignWare-like SPI register block used across many Rockchip SoCs.

## Important APIs, Types, and Functions

`struct rockchip_spi` stores clocks, MMIO registers, DMA port addresses, current TX/RX pointers and word counts, DMA state bits, FIFO depth, source frequency, bytes-per-word, RX sample delay, target-abort state, CS-inactive detection support, and the active transfer pointer. Core helpers are `spi_enable_chip()`, `wait_for_tx_idle()`, `get_fifo_len()`, `rockchip_spi_set_cs()`, `rockchip_spi_config()`, `rockchip_spi_prepare_irq()`, `rockchip_spi_prepare_dma()`, `rockchip_spi_isr()`, and DMA callbacks.

The controller hooks are `rockchip_spi_setup()`, `rockchip_spi_transfer_one()`, `rockchip_spi_can_dma()`, `rockchip_spi_target_abort()`, `rockchip_spi_handle_err()`, and `rockchip_spi_max_transfer_size()`. Probe/remove and power management are implemented by `rockchip_spi_probe()`, `rockchip_spi_remove()`, system suspend/resume, and runtime suspend/resume.

## Control Flow

Probe chooses `devm_spi_alloc_target()` when the DT node has `spi-slave`, otherwise `devm_spi_alloc_host()`. It maps registers, enables `apb_pclk` and `spiclk`, requests the IRQ, computes RX sample delay, detects FIFO depth from the version register, enables runtime PM, configures controller capabilities, optionally requests TX/RX DMA channels, derives DMA port addresses, detects newer active-high/CS-inactive behavior, and registers the controller.

Each transfer validates length and buffers, derives one or two bytes per word, decides DMA eligibility from FIFO depth, writes CTRLR0/CTRLR1/RX threshold/DMA thresholds/BAUDR, then starts either PIO IRQ or DMA. PIO preloads TX FIFO, enables RX-full and optional CS-inactive interrupts, and finalizes when RX words drain to zero. DMA starts RX before TX, sets state bits atomically, enables CS-inactive interrupt in target mode when supported, and finalizes from the last DMA callback. Target abort pauses/terminates DMA, drains RX FIFO, adjusts the transfer length to the actual received bytes, disables the chip, and finalizes.

## State and Persistence Behavior

Driver state is volatile: current transfer pointers, residual word counts, DMA state bits, FIFO length, cached clock rate, RX sample delay, and runtime-PM references held while native CS is asserted. There is no persistent storage. Hardware state is reprogrammed for each transfer, and clocks are gated by runtime PM when idle.

## Dependencies and Integration Points

The driver depends on platform/OF, clock, DMAengine, interrupt, scatterlist, pinctrl, PM runtime, and the SPI core. It integrates with GPIO descriptors for external CS lines, native chip-select registers for internal CS, SPI target abort handling, and optional DMA channels named `tx` and `rx`.

## Risks and Edge Cases

Native CS handling takes a runtime-PM reference on assertion and drops it on deassertion; any missed deassertion would keep clocks on. DMA callbacks use atomic state to wait for both directions, so callback ordering and abort races are important. Target abort depends on DMA residue being meaningful and on the active `rs->xfer` pointer remaining valid. Zero-length transfers are finalized manually because hardware will not interrupt. Transfer length is capped at `0xffff` because `0x10000` can hang the controller. Active-high native CS is rejected unless the IP version advertises support.

## Test Signals

Exercise PIO and DMA thresholds, 4/8/16-bit words, TX-only/RX-only/full-duplex transfers, target mode with CS-inactive abort, GPIO and native chip selects, active-high rejection/acceptance, RX sample delay DT settings, DMA callback order, `handle_err()` during active DMA, runtime suspend around CS assertion, and suspend/resume with queued transfers.
