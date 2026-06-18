# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_main.c

## Purpose
Primary PCI/netdev implementation for EG20T/OKI/LAPIS PCH Gigabit Ethernet. It owns PCI probe/remove, netdev operations, NAPI, IRQs, rings, MAC/PHY programming, watchdog link maintenance, WOL PM, PCI error recovery, multicast filtering, MTU/features, and PCH PTP timestamping.

## Important APIs, Types, And Functions
PCI/module: `pch_gbe_probe()`, `pch_gbe_remove()`, `pch_gbe_shutdown()`, PCI ID table, driver, and error handlers. Netdev ops use `pch_gbe_open()`, `pch_gbe_stop()`, `pch_gbe_xmit_frame()`, MAC/MTU/features/ioctl/timestamp callbacks. Core lifecycle: `pch_gbe_sw_init()`, `pch_gbe_reset()`, `pch_gbe_up()`, `pch_gbe_down()`. Data path: `pch_gbe_tx_queue()`, `pch_gbe_intr()`, `pch_gbe_napi_poll()`, `pch_gbe_clean_tx()`, `pch_gbe_clean_rx()`.

## Control Flow
Probe enables PCI, maps BAR1, allocates netdev, applies platform quirks, finds companion PTP function, installs ops/NAPI/ethtool, resets MAC, initializes software and PHY/MII state, reads MAC, validates module options, registers netdev, and disables carrier. Open allocates descriptor rings, powers PHY, configures TX/RX, requests IRQ, allocates RX pool, preallocates TX skbs, fills RX descriptors, enables DMA/MAC RX, starts watchdog/NAPI/IRQs/queue. IRQ masks RX/TX completions and schedules NAPI. NAPI cleans RX into GRO and TX completions, then re-enables IRQs.

## State And Persistence
Runtime state in `struct pch_gbe_adapter`, rings, coherent RX pool, preallocated TX skbs, hardware/PHY registers, timer, reset work, stats, WOL flags, and timestamp enables. No file persistence; suspend/shutdown may program WOL and PCI low power state.

## Dependencies And Integration Points
Depends on PCI, netdevice, NAPI, DMA, generic MII, PHY helper file, ethtool setup, `ptp_pch`, GPIO lookup quirks, PM, and PCI AER.

## Risks And Edge Cases
TX preallocates internal skbs and does not check allocation before `skb_reserve()`. RX combines per-packet skbs with a large coherent pool. `pch_gbe_request_irq()` does not free IRQ vectors on `request_irq()` failure. Timestamp code assumes companion PTP PCI function exists. Link uses timer polling. PM/error paths coordinate NAPI, IRQ, timer, PHY power, and WOL.

## Test Signals
Probe on supported IDs, MAC validation, open/stop without DMA leaks, traffic and checksum offload, TX queue stop/wake, RX FIFO recovery, jumbo MTU changes, multicast/promiscuous filtering, PTP timestamp ioctls, WOL suspend/resume, PCI recovery, MinnowBoard GPIO quirk, and unload after reset work cancellation.
