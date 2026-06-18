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
