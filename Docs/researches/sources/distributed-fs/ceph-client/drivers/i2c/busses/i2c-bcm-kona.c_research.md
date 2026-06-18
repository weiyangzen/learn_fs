# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm-kona.c

## Purpose
Broadcom Kona BSC I2C master driver. It supports standard, fast, fast-mode-plus, and high-speed timing presets, FIFO-based reads/writes, 10-bit addressing, and `I2C_M_NOSTART`.

## APIs, Control Flow, and State
`struct bcm_kona_i2c_dev` holds MMIO, IRQ, external clock, adapter, completion, and selected timing tables. Command helpers issue START/RESTART/STOP/NOACTION and wait on the shared ISR completion. Reads are chunked through the 64-byte RX FIFO with last-byte NAK control; writes fill the 64-byte TX FIFO and temporarily disable the IRQ while loading a FIFO batch. `bcm_kona_i2c_xfer()` enables the external and internal clocks, enables pad output, sends START, optionally performs the high-speed controller-code handshake, loops messages with restarts and address phases, transfers data, sends STOP, restores standard timing, disables pad output, and drops clocks. Probe selects timing from `clock-frequency`, configures autosense, FIFOs, IRQ, and registers the adapter.

## Dependencies and Integration
Depends on clk rate changes between 13 MHz and 104 MHz, platform IRQ/MMIO, OF compatible `brcm,kona-i2c`, and the I2C core functionality/quirk surface.

## Risks and Test Signals
Risks are high-speed handshake failure, IRQ disable while filling FIFO, NAK interpretation, pad/clock cleanup on error paths, and strict accepted bus frequencies. Test 100 kHz/400 kHz/1 MHz/3.4 MHz modes, 10-bit reads, multi-message restarts and `NOSTART`, long FIFO-chunked reads/writes, NAK on address/data, timeout paths, and repeated probe/remove with shared IRQs.
