# sources/distributed-fs/ceph-client/drivers/net/ethernet/jme.c

## Purpose
`jme.c` is the implementation of the JMicron JMC250/JMC260 PCIe Ethernet driver. It binds a PCI driver to JMicron PCI device IDs, registers a `net_device`, manages the device MMIO register block defined in `jme.h`, and implements RX/TX DMA rings, MDIO/MII access, link management, interrupt moderation, ethtool controls, EEPROM access, wake-on-LAN, and suspend/resume behavior.

## Important APIs, Types, And Functions
The public integration surface is `jme_driver`, `jme_netdev_ops`, and `jme_ethtool_ops`. `jme_init_one()` performs PCI enablement, DMA mask selection, BAR mapping, `alloc_etherdev()`, feature setup, NAPI registration, PHY discovery, EEPROM reload, MAC address loading, and `register_netdev()`. `jme_remove_one()`, `jme_shutdown()`, `jme_suspend()`, and `jme_resume()` provide lifecycle and power management.

The core datapath functions are `jme_open()`, `jme_close()`, `jme_start_xmit()`, `jme_tx_clean_tasklet()`, `jme_process_receive()`, `jme_alloc_and_feed_skb()`, and `jme_poll()`. Hardware access is wrapped by `jread32()`, `jwrite32()`, and `jwrite32f()` from `jme.h`. PHY control is handled through `jme_mdio_read()`, `jme_mdio_write()`, `jme_reset_phy_processor()`, `jme_check_link()`, `jme_restart_an()`, `jme_phy_on()`, `jme_phy_off()`, `jme_phy_calibration()`, and revision-specific `jme_phy_setEA()` logic.

## Control Flow
Probe disables PCIe low-power link states, enables the PCI function, chooses a 64/40/32-bit coherent DMA mask, maps BAR0, seeds cached register defaults, initializes spinlocks and atomic gates, installs NAPI, discovers PHY ID for FPGA variants, powers down the PHY, resets the MAC, reloads EEPROM, reads the MAC address, and registers the network device. Opening the netdev enables NAPI, initializes tasklets, requests MSI or shared INTx, enables interrupt sources and packet coalescing, powers and configures the PHY, calibrates revision-specific PHY state, and triggers link resolution through the timer/software interrupt path.

Link-change work is serialized by `link_changing`. It stops queues, disables PCC/timers/tasklets, tears down RX/TX engines and rings when needed, resets the MAC, rechecks link state, allocates fresh rings, enables engines, restarts queues, or starts pseudo hotplug shutdown timing when link is down. RX is driven either by tasklets or NAPI depending on `JME_FLAG_POLL`; interrupt mode schedules RX clean tasklets, while polling mode disables RX PCC and schedules NAPI. TX maps skb head and fragments into descriptor chains, kicks queue 0, and frees completed mappings from `jme_tx_clean_tasklet()`.

## State And Persistence
Persistent driver state lives in `struct jme_adapter`: cached register values (`reg_txcs`, `reg_rxcs`, `reg_rxmcs`, `reg_ghc`, `reg_pmcs`, `reg_gpreg1`), PHY/link settings, ring size/masks, `mii_if`, NAPI, tasklets, work item, dynamic PCC counters, and synchronization atomics. RX/TX rings persist while the interface is carrier-up/open; descriptors are coherent DMA allocations and `jme_buffer_info` tracks skb ownership and DMA mappings. User-configured link settings are cached in `old_cmd` under `JME_FLAG_SSET`; WoL selection persists in `reg_pmcs` for suspend/shutdown. Module parameters alter pseudo hotplug behavior at load time.

## Dependencies And Integration Points
This file depends on PCI, DMA mapping, `net_device`, NAPI, tasklet, workqueue, MII, ethtool, VLAN acceleration, checksum/GSO helpers, and Linux PM APIs. It integrates with the kernel through `pci_register_driver()`, `netdev_ops`, `ethtool_ops`, `mii_if_info`, module parameters, MSI/INTx IRQ handling, and optional netpoll.

## Risks
The driver has complex concurrency between IRQ, NAPI/tasklets, link-change work, close/suspend, and TX timeout. Several hardware waits are busy polling with fixed timeouts, so register semantics matter for hangs. DMA error unwind is delicate: if `jme_fill_tx_desc()` fails after `jme_alloc_txdesc()` has reserved descriptors, `jme_start_xmit()` returns `NETDEV_TX_OK` without an obvious skb free or `nr_free` rollback in that path. RX replacement allocates a new skb before handing the old one up; allocation failure drops but keeps the original mapping for reuse. Ettool EEPROM writes directly program SMB-backed EEPROM and need hardware validation. MTU over 1900 disables TSO/checksum features, so jumbo behavior needs regression coverage.

## Test Signals
Useful signals include PCI probe/remove with both JMC250 and JMC260 IDs, MSI fallback to INTx, open/close cycles, RX/TX under stress with SG/TSO/VLAN/checksum combinations, MTU changes around 1900 and max jumbo, ethtool coalesce/pause/WoL/EEPROM/register dumps, suspend/resume with WoL enabled and disabled, forced media and autonegotiation changes, netpoll if configured, and fault injection for DMA mapping, RX allocation, IRQ request, EEPROM reload, and PHY timeouts.
