# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth.h

## Purpose
This private header defines DPAA1 Ethernet driver state shared by the main, ethtool, sysfs, and trace files.

## Important APIs, Types, and Functions
The header defines `DPAA_TC_NUM`, `enum dpaa_fq_type`, `struct dpaa_fq`, `struct dpaa_fq_cbs`, `struct dpaa_bp`, `struct dpaa_rx_errors`, `struct dpaa_ern_cnt`, `struct dpaa_napi_portal`, `struct dpaa_percpu_priv`, `struct dpaa_buffer_layout`, `struct dpaa_eth_swbp`, and `struct dpaa_priv`. It declares `dpaa_ethtool_ops`, `dpaa_eth_sysfs_init()`, and `dpaa_eth_sysfs_remove()`. Helpers `dpaa_num_txqs_per_tc()` and `dpaa_max_num_txqs()` bind TX queue scaling to `num_possible_cpus()` and four traffic classes.

## Control Flow
The header has no executable control flow, but it defines the layout used throughout the driver. FQ entries wrap QMan FQs and optional XDP RX queue metadata. Buffer pools track per-CPU counts, raw/usable size, BPID, BMan pool, seed/free callbacks, and refcounting. `dpaa_priv` is the root object behind `netdev_priv()` and connects the netdev to MAC, DMA devices, FQ arrays, congestion groups, buffer layouts, timestamp flags, and XDP program.

## State and Persistence
All represented state is runtime-only. Per-CPU stats and buffer counts are volatile. `xdp_prog` is a live BPF program pointer managed by the main driver. No file or firmware persistence is represented.

## Dependencies and Integration Points
It depends on netdev, refcount, XDP, QMan, BMan, FMan, MAC definitions, and local trace declarations. It is the key integration contract for `dpaa_eth.c`, `dpaa_ethtool.c`, `dpaa_eth_sysfs.c`, and tracing.

## Risks
Because many files share this structure layout, changes can have broad ABI-like impact inside the module. Queue-count helpers based on possible CPUs can allocate more queues than online CPUs and must stay aligned with netdev queue setup. `dpaa_eth_swbp` size must remain within `DPAA_TX_PRIV_DATA_SIZE`.

## Test Signals
Compile all DPAA objects after any structure change, then validate per-CPU stats, sysfs FQ/BPID reporting, ethtool stats, XDP RX queue registration, and traffic class queue counts on systems with different CPU online/possible masks.
