# sources/distributed-fs/ceph-client/drivers/net/ethernet/nxp/lpc_eth.c

## Purpose
Platform netdev driver for the NXP LPC32xx Ethernet MAC. It binds `nxp,lpc-eth`, configures RMII/MII, allocates a fixed coherent DMA area for descriptors/status/buffers, registers MDIO/phylib, and exposes one Ethernet queue with NAPI, multicast filtering, ethtool link settings, PM, and MAC address handling.

## Important APIs, Types, And Functions
`struct netdata_local` stores platform/netdev handles, MMIO base, clock, MDIO bus, optional PHY node, DMA base, descriptor/status pointers, TX counters, link state, spinlock, and NAPI. Lifecycle: `lpc_eth_drv_probe()`, `lpc_eth_drv_remove()`, `lpc_eth_open()`, `lpc_eth_close()`, suspend/resume. Data path: `lpc_eth_hard_start_xmit()`, `__lpc_handle_xmit()`, `__lpc_handle_recv()`, `lpc_eth_poll()`, `__lpc_eth_interrupt()`. PHY/MDIO: `lpc_mii_init()`, `lpc_mii_probe()`, `lpc_mdio_read()`, `lpc_mdio_write()`, `lpc_handle_link_change()`.

## Control Flow
Probe selects interface mode from DT, maps registers, requests IRQ, allocates DMA memory from optional LPC32xx IRAM or coherent SDRAM, derives the MAC address, shuts the MAC down for idle power, resets MII management, registers NAPI/netdev, then registers/probes MDIO. Open enables clock, resumes PHY, resets and initializes MAC/rings, starts phylib, queue, and NAPI. IRQ clears/masks status and schedules NAPI. NAPI handles TX completions and RX packets, then re-enables interrupts when under budget.

## State And Persistence
Runtime-only state in `netdata_local`, MAC/PHY registers, descriptor/status rings, and DMA buffers. No disk or NVM persistence. Link speed/duplex is cached and reprogrammed after phylib changes.

## Dependencies And Integration Points
Depends on platform/OF, LPC32xx misc helpers, clocks, phylib, MDIO, NAPI, coherent DMA, netdevice ops, and phylib ethtool helpers. DT properties include `phy-mode`, `use-iram`, `phy-handle`, and optional `mdio`.

## Risks And Edge Cases
TX/RX copy through fixed 1536-byte buffers, so jumbo frames are unsupported. `__lpc_eth_init()` has a precedence-sensitive command-mask expression. IRQ is requested before final netdev name registration. MDIO busy-waits up to 100 ms. PM paths reset hardware around clock state and need careful phylib ordering.

## Test Signals
Probe/IRQ/clock/MDIO success, PHY attach, MAC fallback, link changes, TX/RX traffic, queue wakeups, multicast/promiscuous filtering, suspend/resume, and unload without IRQ/DMA/MDIO lifetime warnings.
