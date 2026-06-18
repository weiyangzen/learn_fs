# sources/distributed-fs/ceph-client/drivers/net/wan/pc300too.c

## Purpose
`pc300too.c` is a PCI driver for Cyclades PC300 synchronous serial cards using HD64572 SCA-II. It registers one or two generic HDLC ports, configures PLX PCI9050 bridge registers, maps SCA and buffer RAM, supports X.21/V.35/V.24 interface selection depending on card type, and delegates packet movement to shared `hd64572.c`.

## Important APIs, Types, And Functions
`plx9050` models bridge registers. `port_t` stores NAPI, netdev, SCA ring indices, sync settings, interface type, and channel number. `card_t` stores mapped RAM/SCA/PLX bases, saved init control, ring sizing, card type, port count, and IRQ. Core functions include `pc300_set_iface()`, `pc300_open()`, `pc300_close()`, `pc300_ioctl()`, `pc300_pci_init_one()`, and `pc300_pci_remove_one()`.

## Control Flow
Probe enables the PCI device, requests regions, allocates card state, validates BAR sizes, maps PLX/SCA/RAM regions, works around a PLX read bug by temporarily switching BAR0, derives card type and port count, allocates HDLC netdevices, resets/reloads the bridge, detects RAM, chooses clock source, sizes rings, enables bridge interrupts, requests IRQ, initializes SCA and ports, and registers HDLC devices. Open calls `hdlc_open()`, starts SCA, and applies interface settings. Ioctl exposes `IF_GET_IFACE` and accepts only interface modes compatible with the detected card type before delegating other requests to generic HDLC.

## State And Persistence
State is volatile in `card_t` and `port_t`. Module parameters `pci_clock_freq` and `use_crystal_clock` influence `CLOCK_BASE` at module init. Cleanup unregisters HDLC devices, frees IRQ, unmaps BARs, releases PCI regions, disables the device, frees netdevices, and frees card memory.

## Dependencies And Integration Points
The driver depends on PCI IDs for Cyclades PC300 variants, PLX bridge register behavior, `hd64572.c` SCA helpers, generic HDLC, NAPI fields shared with SCA code, sync-serial ioctls, and module parameters.

## Risks
PC300 TE cards are detected but noted as not fully supported; users may see registered behavior for hardware with incomplete semantics. The PLX BAR workaround is hardware-specific and sensitive to ordering. `CLOCK_BASE` is global, so multiple cards with different clock expectations are not represented. Error unwind must handle partially allocated netdevices and mapped resources.

## Test Signals
Test PCI probe on 1-port and 2-port IDs, invalid BAR-size rejection, RAM-detection failure, IRQ request failure unwind, card type to allowed interface mapping, `use_crystal_clock` behavior, open/close SCA start/stop, and generic protocol attach through `hdlc_ioctl()`.
