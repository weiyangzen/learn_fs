# sources/distributed-fs/ceph-client/drivers/net/wan/pci200syn.c

## Purpose
`pci200syn.c` is the Goramo PCI200SYN synchronous serial card driver. It exposes two V.35 generic HDLC ports over a PLX PCI bridge and HD64572 SCA-II controller, using shared `hd64572.c` logic for rings, interrupts, attach, and xmit.

## Important APIs, Types, And Functions
`plx9052` models the bridge registers. `port_t` stores netdev, card pointer, spinlock, sync settings, SCA channel/ring state, encoding, parity, and NAPI. `card_t` stores mapped RAM/SCA/PLX bases, ring sizing, IRQ, and two ports. Local functions include `new_memcpy_toio()` for chunked writes with posted-write flushing, `pci200_set_iface()`, `pci200_open()`, `pci200_close()`, `pci200_ioctl()`, `pci200_pci_init_one()`, and `pci200_pci_remove_one()`.

## Control Flow
Module init validates `pci_clock_freq` and registers the PCI driver. Probe enables PCI, requests regions, allocates card and two HDLC netdevices, validates BAR sizes, maps PLX/SCA/RAM, resets the PLX bridge, detects RAM, sizes TX/RX rings for two ports, enables bridge interrupts, requests shared IRQ, initializes SCA, initializes each port, and registers HDLC devices. Open/close wrap `hdlc_open()`/`hdlc_close()` with SCA start/stop and bridge flushing. Ioctl exposes V.35 sync serial settings and delegates other WAN commands to `hdlc_ioctl()`.

## State And Persistence
All state is runtime memory and hardware registers. The only module-level setting is `pci_clock_freq`, used as `CLOCK_BASE`. Cleanup releases IRQ, unmaps resources, releases PCI regions, disables the device, frees netdevices, and frees `card_t`.

## Dependencies And Integration Points
The file integrates with PCI matching on PLX subsystem IDs, generic HDLC, shared `hd64572.c`, SCA interrupt handling, PLX register access, DMA-capable memory-mapped RAM, and sync-serial ioctls.

## Risks
The driver assumes exactly two ports and V.35 semantics. `new_memcpy_toio()` overrides `memcpy_toio` for included SCA code and relies on readback from `dest` after advancing, which is a subtle hardware flush pattern. PCI error unwind must cope with both netdevices allocated before BAR validation. As with similar SCA drivers, changing shared `hd64572.c` contracts can affect this driver indirectly.

## Test Signals
Test PCI matching, invalid clock parameter rejection, invalid BAR sizes, RAM/ring sizing, IRQ request failure, open/close flush behavior, V.35 ioctl validation, protocol attach via generic HDLC, and SIOCDEVPRIVATE ring dumps when debug is enabled.
