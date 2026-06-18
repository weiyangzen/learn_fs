# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bt3c_cs.c

## Purpose

`bt3c_cs.c` is the PCMCIA HCI driver for the 3Com Bluetooth PC Card. It claims PCMCIA I/O resources, loads `BT3CPCC.bin` firmware into the card using a Motorola S-record-like format, registers an `HCI_PCCARD` device, and handles interrupt-driven RX/TX through card registers.

## Important APIs, Types, And Functions

`struct bt3c_info` stores the PCMCIA device, HCI device, spinlock, TX queue/state, RX parser state/count/skb. Low-level I/O helpers `bt3c_address`, `bt3c_put`, `bt3c_io_write`, `bt3c_get`, and `bt3c_read` access card address/data/control registers. TX is handled by `bt3c_write`, `bt3c_write_wakeup`, and `bt3c_hci_send_frame`. RX and IRQ handling are in `bt3c_receive` and `bt3c_interrupt`. Firmware loading is in `bt3c_load_firmware`. PCMCIA configuration uses `bt3c_check_config`, `bt3c_check_config_notpicky`, and `bt3c_config`.

## Control Flow

Probe allocates state, enables IRQ and automatic PCMCIA VPP/IO configuration, and calls `bt3c_config`. Configuration first loops over normal config tuples, then falls back to less picky standard serial-port-like base addresses and finally any free port. It requests IRQ, enables the device, and calls `bt3c_open`. Open allocates an HCI device, installs callbacks, requests `BT3CPCC.bin`, loads firmware, waits one second, then registers HCI.

The firmware loader resets card registers, parses S-record lines, validates checksum, writes S3 records into card memory through address/data ports, boots the controller at address `0x3000`, and clears status/FIFO registers. Interrupts read a status register when the control interrupt bit is set, report antenna state changes, receive available bytes, and wake TX when transmit complete. RX parsing is a byte-oriented HCI packet state machine. TX prepends packet type, queues the skb, and under spinlock writes the frame to FIFO address `0x7080` and length register `0x7005`.

## State And Persistence

State is volatile. Firmware is loaded on open/probe and not preserved by the driver across removal. `tx_state` gates one active send at a time, and `rx_state`/`rx_count`/`rx_skb` preserve packet parser progress across interrupts. The HCI device exists until release/detach, where it is unregistered and freed.

## Dependencies And Integration Points

The driver depends on PCMCIA, I/O port access, firmware loader, spinlocks, skbuffs, and Bluetooth HCI core. It is built by `CONFIG_BT_HCIBT3C`, which selects `FW_LOADER` and requires `PCMCIA && HAS_IOPORT`. The module declares `BT3CPCC.bin`.

## Risks

Firmware parsing is sensitive to record format, sizes, and checksum math. Bad input can abort with `-EFAULT`, `-EINVAL`, or `-EILSEQ`; any parser rewrite should preserve bounds assumptions around `ptr` and `count`. Register addresses and delays are hardware-specific. Interrupt handling shares IRQ lines and must not claim unrelated interrupts. Cleanup must handle failed firmware load without leaving a registered HCI device or enabled PCMCIA function.

## Test Signals

Signals include successful port selection, IRQ request, firmware request and load, HCI registration, command/ACL/SCO transmit stats, RX frame delivery, antenna status logging, and clean detach. Negative tests should cover malformed firmware records, checksum failure, missing firmware, no usable port range, and card removal during interrupt activity.
