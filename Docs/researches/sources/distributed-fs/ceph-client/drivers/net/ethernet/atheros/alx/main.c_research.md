# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/main.c

## Purpose
Implements the ALX PCIe Ethernet netdev driver: PCI probe/remove, netdev lifecycle, descriptor ring allocation, RX/TX datapath, NAPI, MSI/MSI-X/legacy interrupts, link work, reset work, MDIO ioctl bridge, suspend/resume, PCI error recovery, and module registration.

## Important APIs, Types, and Functions
Probe/remove are `alx_probe()` and `alx_remove()`. Netdev ops include `alx_open()`, `alx_stop()`, `alx_start_xmit()`, `alx_change_mtu()`, `alx_ioctl()`, `alx_get_stats64()`, and `alx_tx_timeout()`. Lifecycle helpers are `__alx_open()`, `__alx_stop()`, `alx_halt()`, `alx_activate()`, and `alx_reinit()`. Ring/data path helpers include `alx_refill_rx_ring()`, `alx_clean_rx_irq()`, `alx_clean_tx_irq()`, `alx_map_tx_skb()`, `alx_tso()`, and `alx_tx_csum()`. Interrupt paths cover MSI-X misc/ring, MSI, and legacy. Power/error paths are `alx_suspend()`, `alx_resume()`, and PCI error handlers.

## Control Flow and State
PCI probe enables the device, sets DMA mask, requests BARs, maps registers, initializes locks/state, resets PCIe/PHY/MAC, configures link advertisement, obtains MAC/PHY identity, installs netdev/ethtool ops, and registers the netdev. Open chooses MSI-X if possible or falls back to MSI/INTx, allocates NAPI contexts and coherent descriptor memory, configures hardware, requests IRQs, initializes rings, starts queues, enables interrupts, and schedules link check. RX NAPI consumes updated RRDs, validates expected RFD index/count, unmaps DMA, handles error bits, sets checksum state, and passes packets to GRO. TX maps SKB head/frags into TPDs, handles TSO and checksum offload, advances producer index, and reclaims completions from hardware consumer index. Link work reads PHY state, starts/stops MAC and queues, and reinitializes hardware after link down.

## Dependencies and Integration Points
Depends on PCI core, DMA API, NAPI, netdev multiqueue, MSI/MSI-X, MDIO ioctl emulation, ethtool ops, CRC32 multicast hashing, and low-level `hw.c` helpers. Device ids include AR8161/AR8162/AR8171/AR8172 and Killer E2200/E2400/E2500 variants with an MSI INTx-disable quirk.

## Risks and Test Signals
Risk areas include descriptor memory needing one 4 GB address window, MSI-X fallback after partial resource allocation, RX DMA address workaround near page offset `0xfc0`, reset while NAPI/IRQs are active, and clear-on-read stats. `alx_request_msix()` initializes `free_vector` to zero and frees vectors based on it during partial failure; failure-path testing is important. Tests should cover traffic under MSI-X/MSI/legacy, multiqueue TX mapping, TSO/IPv6 TSO/checksum offload, MTU changes above TSO limit, suspend/resume, PCI AER recovery, link flap, and netpoll if enabled.
