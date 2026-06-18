# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth.h

## Purpose
`dpaa2-eth.h` is the shared contract for the DPAA2 Ethernet driver. It defines queue, buffer, annotation, timestamp, classifier, statistics, XDP, and private-driver data structures used by the core driver, ethtool support, MAC support, devlink support, XSK support, DCB support, and debugfs code.

## Important APIs, types, and constants
The header sets hardware sizing and policy constants such as `DPAA2_ETH_STORE_SIZE`, `DPAA2_ETH_MFL`, `DPAA2_ETH_MAX_MTU`, RX/TX hardware annotation sizes, buffer-pool quota/refill thresholds, taildrop/congestion thresholds, queue limits, DPCON limits, SGT cache size, and enqueue retry bounds. `struct dpaa2_eth_swa` is the critical software annotation area stored in TX buffers; its union records ownership for linear SKB, SG SKB, XDP frame, XSK buffer, or software TSO descriptor. `struct dpaa2_fas`, `struct dpaa2_fapr`, and `struct dpaa2_faead` model hardware annotation status, parse results, and egress action descriptors.

Core runtime objects are `struct dpaa2_eth_fq`, `struct dpaa2_eth_channel`, `struct dpaa2_eth_bp`, and `struct dpaa2_eth_priv`. `dpaa2_eth_priv` aggregates the netdev, queue arrays, enqueue callback, channels, DPNI attributes/version/token, MC IO portal, buffer pools, per-CPU statistics, link and classifier state, XDP program, MAC pointer, timestamping workqueue, devlink data, and per-CPU descriptor array. Inline helpers include annotation accessors `dpaa2_get_fas()`, `dpaa2_get_ts()`, `dpaa2_get_fapr()`, `dpaa2_get_faead()`, version comparator `dpaa2_eth_cmp_dpni_ver()`, queue/TC/FS capability macros, pause-state helpers, `dpaa2_eth_needed_headroom()`, and lock-asserting MAC helpers.

## Control flow and integration
This header is included by `dpaa2-eth.c`, `dpaa2-ethtool.c`, `dpaa2-mac.c`, and adjacent feature files. It declares externally used functions for hash/classifier setup, devlink, buffer-pool allocation, RX processing helpers, IOVA translation, buffer recycling, XDP enqueue, XSK setup/wakeup/TX, TX FD cleanup, and SGT cache handling. It also exposes `dpaa2_ethtool_ops`, optional `dpaa2_eth_dcbnl_ops`, and global PTP objects.

## State and persistence behavior
The structures here describe volatile kernel and hardware-programmed state, not durable state. Hardware annotation layout must remain compatible with the DPNI buffer layout programmed at probe time. `DPAA2_ETH_SWA_SIZE` is a fixed 64-byte contract with `struct dpaa2_eth_swa`; adding fields risks corrupting TX cleanup. Capability macros encode MC firmware version gates that persist only as runtime decisions.

## Dependencies
The header depends on Linux netdev, VLAN, timestamping, devlink, XDP, DPAA2 IO/FD, DPNI/DPNI command headers, trace/debugfs headers, and `dpaa2-mac.h`. It exposes DPAA2 concepts to multiple compilation units, so changes here have broad build and ABI-like implications inside the driver.

## Risks and edge cases
The largest risks are layout and arithmetic mistakes. `DPAA2_ETH_MAX_SG_ENTRIES` depends on RX buffer size; headroom calculations interact with XDP and PTP TX annotation; queue-count macros assume one RX and TX-conf queue per channel; `dpaa2_eth_is_type_phy()` and `dpaa2_eth_has_mac()` require `mac_lock` held. `DPAA2_FAPR_SIZE` uses `sizeof((struct dpaa2_fapr))`, which is unusual but accepted by the compiler; any cleanup should be careful. Duplicated prototypes for DPBP allocation/free appear in the file and could be simplified, but they are harmless.

## Test signals
Compile coverage is the first signal because this header fans out widely. Runtime signals include correct `netdev->needed_headroom`, successful TX timestamping for SKBs with annotation headroom, XDP attach/detach with correct RX headroom, ethtool stats alignment with `DPAA2_ETH_CH_STATS`, classifier field offsets matching hardware keys, and no `WARN_ONCE` from unsupported classification fields.
