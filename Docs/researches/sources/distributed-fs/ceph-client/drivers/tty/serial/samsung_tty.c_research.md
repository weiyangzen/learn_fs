# sources/distributed-fs/ceph-client/drivers/tty/serial/samsung_tty.c

## Purpose

`samsung_tty.c` is the serial-core driver for Samsung S3C/S5P/Exynos-family UARTs plus Apple S5L-compatible UARTs and related derivatives such as ARTPEC and Google GS101. It exposes `ttySAC` ports, supports normal console and early console paths, PIO and optional DMA transfer modes, multiple FIFO geometries, clock-source selection, system suspend/resume, and both platform-ID and OF matching.

## Important APIs, Types, and Functions

`struct s3c24xx_uart_info` describes a hardware family: port type, FIFO masks/shifts/full bits, clock-selection fields, default clock selection, number of baud clocks, register IO width, and fractional divisor support. `struct s3c24xx_serial_drv_data` pairs that info with default platform config and optional per-port FIFO sizes. `struct s3c24xx_uart_dma` stores DMA channels, configs, mappings, descriptors, cookies, buffers, and byte counts. `struct s3c24xx_uart_port` is the per-port serial state: enable flags, PM level, clocks, IRQs, transfer modes, info/config pointers, `uart_port`, and optional DMA state.

Core routines include register helpers `rd_reg*()`/`wr_reg*()`, `s3c24xx_serial_init_port()` for resource/clock/MMIO/IRQ setup, `s3c24xx_serial_set_termios()` for clock/divisor/line-control programming, `s3c24xx_serial_start_tx()` and `s3c24xx_serial_start_next_tx()` for PIO/DMA TX selection, `s3c24xx_serial_rx_irq()` for PIO/DMA RX dispatch, `s3c64xx_serial_handle_irq()` and `apple_serial_handle_irq()` for variant-specific interrupt acknowledgement, and console/earlycon helpers for boot output.

## Control Flow

Probe chooses a port index from OF alias or a static probe counter, resets the static port object, obtains match data, selects S3C64xx-style or Apple ops, applies DT FIFO and IO-width properties, computes `min_dma_size`, maps MMIO, obtains the IRQ, optionally allocates DMA metadata when `dmas` is present, enables controller and baud clocks, masks/clears variant interrupts, resets FIFOs, registers the UART driver on first probe, adds the port, stores drvdata, and disables clocks until serial-core PM enables them.

Startup masks interrupts, requests DMA channels if configured, requests the variant IRQ, resets RX/TX FIFO state, enables PIO RX, and unmasks RX interrupts. TX starts by marking TX enabled, optionally disabling RX for console-flow ports, and either enabling PIO TX IRQs or launching a DMA transfer from an aligned linear xmit FIFO region when size and alignment meet `min_dma_size`. DMA completion advances the xmit FIFO by residue-derived count and starts the next TX batch. RX DMA continuously submits a page-sized buffer; timeout IRQs pause/terminate DMA, copy received bytes to tty, switch to PIO, drain the FIFO, push tty data, clear timeout, and later restart DMA.

Termios programming forces local mode, rejects HUPCL/CMSPAR, chooses the closest allowed baud clock by trying `clk_uart_baudN` sources, switches and enables the best clock, calculates fractional divisor or slot value, writes ULCON/UBRDIV/UDIVSLOT, configures AFC for CRTSCTS, updates timeout and read/ignore masks, and supports custom divisors for `UPF_SPD_CUST`. Suspend uses serial core; resume temporarily enables clocks, resets the port, disables clocks, resumes the UART, and a noirq resume hook restores interrupt masks for wake/console-sensitive variants.

## State and Persistence Behavior

There is no filesystem persistence. Persistent in-kernel state is the static `s3c24xx_serial_ports[]` array, match/config data, clocks, DMA mappings, selected baud clock, transfer modes, IRQ numbers, and serial-core state. Hardware state includes FIFO contents, UCON/ULCON/UMCON/UBRDIV/UDIVSLOT values, interrupt masks, timeout bits, and FIFO trigger/reset configuration. Clocks are intentionally enabled during probe and then disabled so serial-core PM owns active runtime state.

## Dependencies and Integration Points

The driver depends on platform and OF device matching, Samsung serial register definitions, clocks, DMAengine, DMA mapping, serial core, tty flip buffers, console/earlycon, sysrq, ARM fixmap handling for Apple earlycon on ARM64, and system PM. It integrates with many compatibles including Samsung S3C6400/S5PV210/Exynos variants, Apple S5L, Axis ARTPEC-8, Google GS101, and Samsung Exynos8895, and with module init by registering the console before the platform driver.

## Risks and Edge Cases

The DMA paths rely on residue granularity and cache-line alignment; misaligned TX tails intentionally fall back or split to PIO, but errors in residue reporting can over/under-advance xmit data. In `s3c24xx_serial_stop_rx()`, the code pauses `dma->tx_chan` while stopping RX, which looks suspicious and should be verified against the intended `rx_chan`. `s3c24xx_serial_remove()` unregisters the shared UART driver on each remove, which is risky if multiple ports are still present. Console code uses a single global `cons_uart`, so console setup order matters. Clock selection opens and releases candidate clocks on every termios change; failure to find a valid clock silently leaves termios unchanged. Apple and S3C64xx interrupt mask semantics differ, making variant-specific regressions likely when changing common paths.

## Test Signals

Test OF and platform-ID probe for each driver data variant, `reg-io-width` 1/4 and invalid values, DT FIFO override, missing clocks, baud clock selection and fractional divisors, PIO TX/RX, DMA TX/RX thresholds and alignment fallbacks, DMA capability failure, RX timeout handoff from DMA to PIO, parity/frame/overrun/break flags, CRTSCTS/AFC, console and earlycon output/read, Apple MMIO32 earlycon fixmap behavior, suspend/resume/noirq IRQ mask restore, multi-port remove ordering, and custom divisor handling.
