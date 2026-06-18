
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/ether1.c

## Purpose
`ether1.c` is the Acorn Ether1 expansion-card Ethernet driver built around an Intel 82586. It manages the card’s banked onboard RAM, initializes 82586 command/receive structures, handles transmit/receive interrupts, and registers an `ecard_driver`.

## Important APIs, Types, And Functions
- `ether1_inw_p()`, `ether1_outw_p()`, `ether1_writebuffer()`, and `ether1_readbuffer()` access banked card RAM through the page register and optimized ARM copy loops.
- `ether1_ramtest()`, `ether1_reset()`, `ether1_init_2()`, and `ether1_init_for_open()` validate card memory and initialize 82586 SCP/ISCP/SCB/config/address/multicast/TDR/NOP/RFD/RBD structures.
- `ether1_txalloc()` allocates space from the card RAM TX circular area.
- `ether1_sendpacket()` builds TX/TBD/data/NOP blocks in card RAM and links the previous NOP to the new TX command.
- `ether1_xmit_done()` and `ether1_recv_done()` process completed TX/RX descriptors.
- `ether1_interrupt()` acknowledges SCB events and dispatches TX/RX/RU/CU handling.
- `ether1_probe()` maps the expansion card, reads IDPROM MAC address, tests RAM, registers netdev, and stores driver data.

## Control Flow
Probe requests ecard resources, maps the IOCFAST region, resets/tests card RAM, reads MAC, installs netdev ops, and registers. Open requests IRQ, initializes the 82586 command chain and receive ring in onboard RAM, then starts the netdev queue. TX pads short packets, reserves card-RAM regions for TX command/TBD/data/NOP, writes them, patches the prior NOP link under IRQ exclusion, and stops the queue if a future full-size frame would not fit. Interrupts acknowledge SCB bits, process command completions, restart CU/RU when needed, and recycle RX descriptors by moving the suspend marker.

## State And Persistence Behavior
`struct ether1_priv` stores MMIO base, TX linked-list pointers, RX head/tail, bus type, and reset/restart flags. The 82586 state itself lives in the card’s 64 KiB RAM as descriptor rings and command blocks. No persistent state survives device removal.

## Dependencies And Integration Points
It depends on Acorn expansion-card APIs (`ecard_*`), ARM I/O/DMA headers, netdevice APIs, and `ether1.h` descriptor definitions. It integrates with the kernel netdev model through `ether1_netdev_ops`.

## Risks And Edge Cases
- Banked RAM access disables local IRQs selectively; concurrent descriptor updates must preserve page-register correctness.
- `ether1_txalloc()` uses software head/tail pointers over card RAM and must handle wraparound without colliding with pending TX blocks.
- Multicast filter function is empty, so multicast/promiscuous behavior is limited despite netdev callback presence.
- Reset during TX interrupt is tracked by flags but remains a fragile legacy path.
- The optimized ARM assembly copy routines are architecture-specific and sensitive to odd lengths.

## Test Signals
Probe/RAM-test logs, TX/RX traffic, TX ring wraparound, watchdog reset recovery, RU suspended recovery, odd-length packet copy correctness, and ecard remove/open/close cycles are key signals.
