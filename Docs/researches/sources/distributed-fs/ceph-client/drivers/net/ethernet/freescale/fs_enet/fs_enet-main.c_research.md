# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fs_enet-main.c

## Purpose
Implements the common net_device driver for legacy Freescale CPM/FEC Ethernet controllers. It abstracts controller-specific hardware through `struct fs_ops`, while handling probe, phylink, NAPI, DMA descriptor rings, SKB TX/RX, interrupts, ethtool, and timeout recovery.

## Important APIs, Types, and Functions
Important paths include `fs_enet_probe`, `fs_enet_remove`, `fs_enet_open`, `fs_enet_close`, `fs_enet_start_xmit`, `fs_enet_napi`, `fs_enet_interrupt`, `fs_init_bds`, `fs_cleanup_bds`, `fs_timeout_work`, phylink callbacks `fs_mac_link_up` and `fs_mac_link_down`, and ethtool helpers. The OF match table selects `fs_scc_ops`, `fs_fcc_ops`, or `fs_fec_ops` depending on enabled backends and compatible strings.

## Control Flow and State
Probe allocates platform info, selects backend ops, reads CPM command for non-FEC controllers, determines PHY mode, enables optional clock, allocates netdev/private ring arrays, creates phylink, calls backend `setup_data` and `allocate_bd`, initializes locks/NAPI/ethtool/netdev ops, sets SG support, and registers the netdev. Open initializes BDs, enables NAPI, requests IRQ, connects PHY, starts phylink, and starts TX queue. Interrupt handling clears non-NAPI events, reports backend errors, disables NAPI events, and schedules poll. NAPI reclaims TX descriptors, handles TX errors/restarts, processes RX descriptors with copybreak or buffer replacement, updates stats, returns descriptors to hardware, and reenables events when complete. Close stops queue/NAPI/phylink, calls backend stop, disconnects PHY, and frees IRQ.

## Dependencies and Integration Points
Depends on Linux netdev, DMA mapping, NAPI, phylink, ethtool, OF/platform, and controller-specific `fs_ops` backends. Buffer descriptor access macros and private state come from `fs_enet.h`. MDIO connectivity is external through DT and phylink.

## Risks and Test Signals
Risks include DMA map/unmap imbalance, descriptor wrap errors, TX queue wake thresholds tied to `MAX_SKB_FRAGS`, RX copybreak/cache sync mistakes, timeout recovery racing close, backend event-mask mismatches, and partial probe cleanup leaks. Test signals include sustained RX/TX with fragmented SKBs, NAPI budget exhaustion, TX timeout recovery, phylink reconnect/link mode changes, ethtool register dumps/tunables, netpoll builds, and probe/remove error injection.
