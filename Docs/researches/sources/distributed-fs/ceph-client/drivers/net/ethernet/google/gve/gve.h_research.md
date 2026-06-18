# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve.h

## Purpose
Central shared header for the Google gVNIC driver. It defines constants, queue formats, Tx/Rx ring state for GQI and DQO, QPL/page/buffer abstractions, notify blocks, RSS and flow-rule caches, PTP/timestamp state, service/reset flags, helper accessors, and cross-file prototypes.

## Important APIs and Types
Key types include `gve_priv`, `gve_tx_ring`, `gve_rx_ring`, `gve_notify_block`, `gve_queue_page_list`, queue config structs, QPL config, DQO pending packet/buffer states, RSS config, flow rule/cache structs, and `gve_ptp`. Inline helpers expose reset/admin/resource/NAPI state flags, queue format checks (`gve_is_gqi()`, `gve_is_dqo()`, `gve_is_qpl()`), queue/QPL id mapping, notify block mapping, XDP queue ids, and PTP availability. Prototypes cover admin queue users, Tx/Rx allocation and polling, XDP, reset/config adjustment, flow rules, RSS, PTP, and stats reporting.

## Control Flow and Integration
This header is the contract tying together `gve_main`, `gve_adminq`, Tx/Rx implementations, ethtool, flow steering, buffer management, and PTP. Queue format determines which union members in ring structs are active: GQI uses descriptor/data rings and QPL/raw addressing, while DQO uses completion/buffer queues, pending packet lists, page pools, header buffers, and miss/reinjection completion tracking.

## State and Persistence
`gve_priv` is the persistent per-device state. It stores PCI BAR mappings, MSI-X vectors, admin queue ring and counters, event counters, queue arrays/configs, QPL accounting, feature limits, stats report DMA, workqueue/timers/service flags, link speed, flow rules, RSS cache, NIC timestamp DMA, and PTP clock handles. Queue structs maintain free-running counters and synchronized stats for 32-bit architectures.

## Dependencies and Integration Points
Depends on Linux DMA, PCI, netdevice, ethtool netlink, PTP, page pool, XDP, and descriptor headers `gve_desc.h`/`gve_desc_dqo.h`. `gve_adminq.c` populates much of this state from device descriptors and options.

## Risks and Test Signals
Risks include using the wrong union member for a queue format, stale state flags after reset, QPL id collisions, mismatch between adminq feature negotiation and ring allocation, PTP stubs with optional builds, and stats races. Test with all queue formats supported by the device, XDP/XSK paths, reset during traffic, flow rule and RSS ethtool operations, PTP-enabled and disabled builds, and 32-bit stat-read validation.
