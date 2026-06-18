# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_emac.c

## Purpose
`davinci_emac.c` is the platform network driver for TI DaVinci EMAC hardware. It wires the EMAC register block, CPDMA channels, PHY/MDIO integration, NAPI polling, IRQ handling, multicast filtering, ethtool coalescing, netdev operations, runtime PM, and platform/OF probing into a Linux Ethernet device.

## Important APIs, Types, and Functions
The central state type is `struct emac_priv`, containing netdev/platform pointers, NAPI, mapped EMAC/control registers, CPDMA controller/channels, link state, speed/duplex, multicast hash state, coalescing interval, bus frequency, RMII/version flags, PHY references, lock, and optional platform interrupt callbacks. Netdev operations are implemented by `emac_dev_open()`, `emac_dev_stop()`, `emac_dev_xmit()`, `emac_dev_setmac_addr()`, `emac_dev_mcast_set()`, `emac_devioctl()`, `emac_dev_tx_timeout()`, and `emac_dev_getnetstats()`. Probe/remove and PM are handled by `davinci_emac_probe()`, `davinci_emac_remove()`, suspend/resume callbacks, and `late_initcall()`.

## Control Flow and State
Probe obtains the EMAC clock, allocates a netdev, parses platform/OF data, maps register resources, creates a CPDMA controller and one TX/RX channel, derives or randomizes the MAC address, adds NAPI, enables runtime PM, and registers the netdev. Open resumes the device, resets local MAC filter state, pre-fills RX descriptors through `cpdma_chan_idle_submit()`, requests all platform IRQs, soft-resets and configures EMAC hardware, enables NAPI/interrupts, starts CPDMA, connects a PHY by phandle or bus scan, or falls back to fixed 100/full operation. IRQ handling only disables interrupts and schedules NAPI. NAPI reads `MACINVECTOR`, processes bounded TX/RX CPDMA completions, handles fatal host errors, and reenables interrupts when budget is not exhausted. Stop disables queue/NAPI/interrupts, stops CPDMA, soft-resets EMAC, disconnects PHY, frees IRQs, and drops the runtime PM reference.

## Dependencies and Integration Points
The driver depends on `davinci_cpdma`, PHYLIB, OF MDIO/fixed-link helpers, TI control-module MAC ID helpers, platform resources, runtime PM, ethtool, and optional platform interrupt enable/disable hooks. It expects a separate MDIO provider (`ti,davinci_mdio`) unless a fixed link is used.

## Risks and Test Signals
Risk areas include open rollback after partial IRQ allocation, RX descriptor prefill failure, CPDMA stop while NAPI/IRQ state is changing, fatal host-error recovery that disables NAPI without full device reset, multicast hash collisions/counters, coalescing math across EMAC versions, and MAC address acquisition fallbacks. `davinci_emac_remove()` destroys CPDMA channels before `unregister_netdev()`, which is unusual if the interface can still be up; removal tests should exercise opened devices. Test signals include probe/remove under OF and platform data, link up/down and speed changes, TX timeout restart, RX refill after allocation failure, ethtool coalesce boundaries, multicast/promiscuous/allmulti transitions, runtime suspend/resume, and CPDMA stats under traffic.
