# sources/distributed-fs/ceph-client/drivers/tty/serial/rp2.c

## Purpose

`rp2.c` drives Comtrol RocketPort EXPRESS and INFINITY PCI multiport serial cards. It registers `ttyRP` UARTs, discovers the port count from PCI IDs, initializes one or two ASICs, loads required firmware `rp2.fw` into each port's microcode window, and services all card ports through a shared PCI interrupt.

## Important APIs, Types, and Functions

`struct rp2_card` tracks the PCI device, BAR0/BAR1 mappings, per-card spinlock, number of ports, minor range, initialized count, and SMPTE capability flag. `struct rp2_uart_port` embeds `uart_port` and stores card linkage plus ASIC, port, and microcode MMIO bases. The driver-level `rp2_uart_driver` exposes `ttyRP` ports up to `CONFIG_SERIAL_RP2_NR_UARTS`.

Important helpers include `rp2_alloc_ports()` for monotonically assigning minor ranges, `rp2_rmw*()` register updates, `rp2_mask_ch_irq()` for shared channel IRQ masks, `rp2_init_card()` and `rp2_reset_asic()` for card/ASIC setup, `rp2_init_port()` for channel reset, firmware copy, default termios, modem control, FIFO enable, and TX/RX enable, and `rp2_load_firmware()` for per-port serial-core registration. Runtime UART callbacks implement modem control, termios, RX/TX, startup/shutdown, and verification.

## Control Flow

PCI probe allocates card state, enables the device with pcim helpers, requests BARs, maps BAR0/BAR1, decodes port count from the matched ID, reserves a global minor range, resets the card and ASICs, allocates the port array, requests `rp2.fw`, initializes and registers every port, releases firmware, and finally requests the shared IRQ. Each port's startup flushes FIFOs, enables RX IRQs and modem-status behavior, sets RX trigger level to 1 byte, clears channel status, and unmasks that channel. Shutdown clears break, masks the channel IRQ, and clears channel status.

On interrupt, `rp2_uart_interrupt()` checks ASIC 0 and ASIC 1 when present. `rp2_asic_interrupt()` reads pending channel bits after applying the inverse channel mask and calls `rp2_ch_interrupt()` for each bit. The channel handler clears status bits by writing them back, drains RX FIFO count bytes through `RP2_DATA_BYTE`, translates hardware exception bits into tty flags, handles sysrq, services TX-empty by filling the FIFO through `uart_port_tx_limited()`, and wakes modem-status waiters on DSR/CTS/DCD/RI deltas.

## State and Persistence Behavior

There is no local filesystem persistence apart from dependency on the external firmware file at load time. In-kernel state persists for the lifetime of the PCI device: minor allocation is monotonic and explicitly does not support reclaiming individual hot-unplugged card ranges, card/port structures, mapped BARs, microcode contents, per-port termios, and serial-core FIFOs. Hardware state includes ASIC resets, clock prescaler, channel IRQ masks, firmware bytes, FIFO enable state, baud divisors, flow-control microcode toggles, and modem outputs.

## Dependencies and Integration Points

The driver depends on PCI core, managed PCI resource mapping, Linux firmware loading, serial core, tty flip buffers, shared IRQs, sysrq support, and DMA-independent MMIO PIO. It integrates with many RocketPort PCI product IDs through the `rp2_pci_tbl`, with `MODULE_FIRMWARE("rp2.fw")`, and with serial userspace through `ttyRP` line numbers.

## Risks and Edge Cases

The global minor allocator never frees ranges, so repeated hotplug can exhaust `CONFIG_SERIAL_RP2_NR_UARTS` until module unload. Firmware load is mandatory and probe fails without `rp2.fw`. `rp2_asic_interrupt()` indexes `card->ports[ch]` for each ASIC-local channel; second-ASIC pending bits are read from the second ASIC base but still use the first 16 entries rather than offsetting by `PORTS_PER_ASIC`, which is a point to verify for 32-port cards. A macro typo defines `RP2_TXRX_CTL_TX_TRIG_m` using the RX shift, though this mask is not used. TX-empty status is based on FIFO count because the TXEMPTY bit is described as unreliable unless TX IRQ is enabled.

## Test Signals

Test probe for 2/4/8/16/32-port PCI IDs, insufficient configured UART minors, missing or short firmware, BAR mapping failures, shared IRQ behavior, second ASIC interrupts, RX exception bits, CREAD clearing via `RP2_DUMMY_READ`, XON/XOFF microcode toggles, hardware flow control, modem status changes, break control, startup/shutdown masking, and hot-unplug/remove after partial port registration failure.
