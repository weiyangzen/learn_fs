# sources/distributed-fs/ceph-client/drivers/net/usb/lan78xx.c

## Purpose
`lan78xx.c` is the full Linux USB network driver for Microchip LAN7800, LAN7850, LAN7801, and AT29M2-AF gigabit Ethernet devices. It owns netdev allocation, URB pools, NAPI, phylink/MDIO, interrupt-domain mapping, register access, EEPROM/OTP access, filtering, offloads, statistics, Wake-on-LAN, autosuspend, and reset/resume behavior.

## Important APIs, Types, And Functions
Core state is `struct lan78xx_net`; receive-filter and WoL state is `struct lan78xx_priv`; URB-backed SKBs use `struct skb_data` in `skb->cb`; hardware counters use `struct statstage`; PHY IRQ bridging uses `struct irq_domain_data`. USB control access is centralized in `lan78xx_read_reg()`, `lan78xx_write_reg()`, and `lan78xx_update_reg()`. EEPROM/OTP access is handled by `lan78xx_read_raw_eeprom()`, `lan78xx_write_raw_eeprom()`, `lan78xx_read_raw_otp()`, and `lan78xx_write_raw_otp()`. MAC address setup uses registers, Device Tree, EEPROM, OTP, or random fallback through `lan78xx_init_mac_address()`.

PHY and link management runs through `lan78xx_mdio_init()`, `lan78xx_setup_irq_domain()`, `lan78xx_get_phy()`, `lan78xx_phylink_setup()`, `lan78xx_mac_prepare_for_phy()`, `lan78xx_phy_init()`, and `lan78xx_phylink_mac_ops`. TX/RX data flow centers on `lan78xx_start_xmit()`, `lan78xx_tx_bh()`, `lan78xx_tx_buf_fill()`, `tx_complete()`, `rx_submit()`, `rx_complete()`, `lan78xx_bh()`, and `lan78xx_poll()`.

## Control Flow
`lan78xx_probe()` allocates the netdev, initializes queues, locks, NAPI, work, timer, endpoint pipes, speed-specific URB pools, then calls `lan78xx_bind()`. Binding allocates private state, initializes filters and offload features, creates the IRQ domain, performs `lan78xx_reset()`, and registers the MDIO bus. Probe then allocates the interrupt URB, enables remote wake, initializes PHY/phylink, registers the netdev, and configures autosuspend.

`lan78xx_open()` takes runtime PM, enables NAPI, marks `EVENT_DEV_OPEN`, submits the interrupt URB, and starts phylink. Phylink `mac_link_up()` configures speed, duplex, pause thresholds, USB U1/U2 settings, RX URBs, FIFO flushes, and MAC/FIFO TX/RX enable bits. `mac_link_down()` stops queues, disables TX/RX paths, and resets the MAC.

TX is staged through `txq_pend`; NAPI batches pending packets into preallocated TX URB buffers with LAN78xx command words for checksum, TSO, and VLAN insertion. RX completion moves URB buffers to `rxq_done`; NAPI parses one or more RX command blocks per URB, copies valid frames to fresh SKBs, applies checksum/VLAN offload metadata, and delivers through GRO. Overflow frames are queued when the NAPI budget is exhausted.

Deferred work clears halted pipes, acknowledges PHY interrupts, and updates stats with exponential timer backoff. Suspend stops/flushes hardware paths, drains URBs, arms autosuspend or WoL filters, and marks the device asleep; resume flushes TX, submits interrupt/deferred URBs, restarts TX, schedules NAPI, clears wake state, and reset-resume reinitializes hardware first.

## State And Persistence Behavior
Volatile state includes event bits, URB queues, NAPI, delayed work, timers, runtime PM references, and software rollover counters. Persistent or device-backed state includes EEPROM, OTP, MAC registers, MAF filters, VLAN/hash RAM, flow thresholds, USB LPM/LTM settings, PHY state, and wake filters. The driver maintains 64-bit software stats from narrower hardware counters.

## Dependencies And Integration Points
This file integrates USB core, netdev, NAPI/GRO, ethtool, phylink, phylib, MDIO/OF MDIO, irqdomain, runtime PM, VLAN/checksum/VXLAN feature helpers, and `lan78xx.h`. It exposes `lan78xx_netdev_ops`, `lan78xx_ethtool_ops`, `lan78xx_phylink_mac_ops`, and the `usb_driver` product table.

## Risks And Test Signals
Key risks are disconnect races, MDIO versus MAC reset lockups, EEPROM LED mux restoration, URB unlink/completion races, malformed RX command lengths, checksum trust with unstripped VLANs, suspend with pending TX, and LAN7801 fixed-link fallback masking board errors. Test signals include successful netdev registration, ethtool stats/register/EEPROM paths, phylink link transitions, RX/TX under load, VLAN and multicast filter changes, jumbo MTU edge rejection, TSO limit enforcement, EEE/pause behavior, WoL wake sources, autosuspend/resume, and reset-resume.
