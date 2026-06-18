# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.c

## Purpose
`smc91x.c` is the platform driver for SMSC/SMC 91C9x and 91C1xxx single-chip Ethernet controllers, including LAN91C94 and LAN91C111. Unlike PCI ring-DMA NICs, these chips expose bank-switched registers and internal packet memory managed by an MMU. The driver handles platform/DT/ACPI discovery, optional GPIO reset/power control, bus-width configuration, packet-memory TX/RX, PHY configuration, interrupts, ethtool, EEPROM access, suspend/resume, and architecture-specific hooks.

## Important APIs, Types, and Functions
- `struct smc_local` is defined in `smc91x.h` and stores MMIO base, optional data chip-select mapping, platform config, locks, tasklet, work item, MII state, current TCR/RCR/RPC modes, PHY type, pending TX SKB, DMA channel on PXA, and message level.
- Platform entry points are `smc_drv_probe()`, `smc_drv_remove()`, `smc_drv_suspend()`, and `smc_drv_resume()` in `smc_driver`.
- Core device control functions are `smc_reset()`, `smc_enable()`, `smc_shutdown()`, `smc_open()`, `smc_close()`, and `smc_timeout()`.
- Data path functions include `smc_hard_start_xmit()`, `smc_hardware_send_pkt()`, `smc_tx()`, `smc_rcv()`, and `smc_interrupt()`.
- PHY functions include serial MII bit-banging (`smc_mii_out()`, `smc_mii_in()`, `smc_phy_read()`, `smc_phy_write()`), detection, reset, fixed/autoneg configuration, powerdown, media checks, and PHY interrupt handling.
- Ettool supports driver info, message level, link settings, nway reset, link state, and EEPROM get/set.

## Control Flow
Platform probe allocates a netdev, merges platform data, OF properties, or defaults into bus-width/config flags, handles optional DT power/reset GPIOs, requests the register memory resource, obtains IRQ flags, requests optional attribute memory, enables the device through attribute-space ECOR/ECSR when present, maps the main register window, and calls `smc_probe()`. `smc_probe()` validates the bank-select signature, checks base-address consistency, identifies the chip revision, reads the MAC, resets the chip, autodetects IRQ if needed, initializes netdev/ethtool/tasklet/work/MII state, detects PHYs on 91C100-class devices, powers down, requests IRQ, optionally requests a PXA DMA channel, and registers the netdev.

Open sets default TCR/RCR/RPC modes, resets and enables the device, configures the PHY synchronously or checks 10baseT carrier, and starts the queue. TX first asks the chip MMU to allocate packet memory; if allocation is immediate it calls the TX tasklet function directly, otherwise it stores `pending_tx_skb`, stops the queue, and enables allocation interrupts. `smc_hardware_send_pkt()` writes packet headers/data/control word into chip memory, enqueues the packet, updates stats, enables TX interrupts, and frees the SKB. RX interrupt handling reads packet number/status/length from the RX FIFO, validates errors and VLAN-length exceptions, copies packet data out of chip memory into a new SKB, releases the MMU packet, and calls `netif_rx()`.

The interrupt handler masks interrupts, loops up to `MAX_IRQ_LOOPS`, and dispatches TX completion/error, RX, allocation, TX-empty statistics, RX overrun, EPH, PHY, and unsupported early-RX events while preserving the packet pointer register. Close stops queue/carrier, shuts the chip down, kills the tasklet, and powers down the PHY. Suspend detaches and shuts down; resume re-enables the platform device, resets/enables, reconfigures PHY if running, and reattaches.

## State and Persistence
State lives in `smc_local`, banked hardware registers, MMU packet memory, PHY registers, pending TX SKB, tasklet/work scheduling, interrupt mask, and EEPROM words. The driver can write EEPROM through ethtool, making that a true persistent hardware mutation. Platform data and DT properties determine persistent board-specific assumptions such as bus width, register shift, LED modes, and GPIO wiring.

## Dependencies and Integration Points
The driver depends on `smc91x.h` for hardware abstraction macros, platform bus, OF/ACPI matching, GPIO consumer APIs, IRQ APIs, workqueues/tasklets, MII helpers, ethtool, CRC32, optional PXA DMA and Assabet/Neponset hooks, and Linux netdev. Integration points include platform resources named `smc91x-regs`, `smc91x-attrib`, and `smc91x-data32`, compatible strings `smsc,lan91c94` and `smsc,lan91c111`, ACPI ID `LNRO0003`, module parameters `nowait` and `watchdog`, and generic netdev operations.

## Risks and Edge Cases
- Bank switching is shared device state; comments explicitly warn that bank 2 must be preserved while interrupts/tasklets can race.
- TX uses one `pending_tx_skb`; the code asserts no second pending packet and relies on queue stop/wake discipline.
- EEPROM set support can permanently change device contents and lacks a magic guard in this file.
- IRQ autodetection is legacy and may fail, requiring a provided IRQ.
- Platform config must expose at least one supported bus width; wrong `reg-io-width`, `reg-shift`, or NOWAIT settings can make the device inaccessible.
- PHY reset sleeps while temporarily dropping the spinlock, so callers must tolerate state changes around reset.

## Test Signals
Test platform, OF, and ACPI probe paths; optional GPIO reset/power timing; 8/16/32-bit access configurations; IRQ trigger selection; open/close; RX/TX with MMU allocation immediate and deferred; TX timeout reset; RX overrun and EPH interrupts; PHY present and absent paths; ethtool link settings and EEPROM read/write; suspend/resume while running and stopped; module parameters `nowait` and `watchdog`; netpoll builds; and PXA/Neponset conditional builds where relevant.
