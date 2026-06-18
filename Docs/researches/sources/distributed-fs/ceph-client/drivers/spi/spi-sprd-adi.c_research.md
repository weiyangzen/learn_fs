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
