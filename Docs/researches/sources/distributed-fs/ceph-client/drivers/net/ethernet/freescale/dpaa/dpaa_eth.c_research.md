# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth.c

## Purpose
This is the main Freescale DPAA1 Ethernet driver. It wires netdev operations to FMan MAC/ports, QMan frame queues and congestion groups, BMan buffer pools, phylink, ethtool/sysfs sidecars, hardware timestamping, checksum offload, traffic classes, NAPI-over-QMan portals, and XDP.

## Important APIs, Types, and Functions
Important private constructs include `struct fm_port_fqs`, global `dpaa_bp_array`, `DPAA_BP_RAW_SIZE`, RX/TX headroom calculations, queue type constants, and module parameters `debug` and `tx_timeout`. Probe/remove are `dpaa_eth_probe()` and `dpaa_remove()`. Netdev ops are `dpaa_open()`, `dpaa_eth_stop()`, `dpaa_start_xmit()`, `dpaa_get_stats64()`, `dpaa_set_mac_address()`, `dpaa_set_rx_mode()`, `dpaa_setup_tc()`, `dpaa_change_mtu()`, `dpaa_xdp()`, `dpaa_xdp_xmit()`, and hardware timestamp get/set. Queue and pool management uses `dpaa_bp_alloc_pool()`, `dpaa_bp_seed()`, `dpaa_eth_refill_bpools()`, `dpaa_alloc_all_fqs()`, `dpaa_fq_setup()`, `dpaa_fq_init()`, `dpaa_fq_free()`, and congestion helpers `dpaa_eth_cgr_init()` and `dpaa_ingress_cgr_init()`.

## Control Flow
Module load reads FMan maximum frame/headroom values and registers a platform driver. Probe waits for BMan/QMan/portal readiness, allocates a multiqueue netdev, obtains the platform MAC device, configures DMA masks on FMan RX/TX port devices, creates a BMan pool and QMan FQs, allocates a QMan pool channel, configures egress and ingress congestion groups, initializes FQs and FMan ports, allocates per-CPU private data, adds NAPI objects, registers the netdev, and creates sysfs files. Open enables per-CPU NAPI, connects phylink, enables FMan ports and MAC, starts phylink, and starts all queues. Stop reverses the live datapath by stopping queues, stopping phylink, disabling MAC/ports, disconnecting PHY, and disabling NAPI.

## Packet Flow
TX pads short packets, ensures writable headroom, optionally linearizes unsupported SG depth, applies erratum A050385 alignment workarounds, builds either a contiguous or SG QMan frame descriptor, optionally requests hardware timestamping, and enqueues to a per-queue egress FQ with a confirmation FQ id in `fd.cmd`. TX confirmations and error queues call `dpaa_cleanup_tx_fd()` to unmap DMA, return XDP frames or consume/free skbs, and record timestamp data. RX callbacks refill buffer pools, reject error FDs, unmap incoming buffers, optionally run XDP for contiguous frames, build skbs from contiguous or SG FDs, attach checksum/hash/timestamp metadata, and inject into the stack with `netif_receive_skb()`.

## State and Persistence
Runtime state spans BMan pools, per-CPU buffer counts, QMan FQs, congestion groups, per-CPU stats, NAPI portal state, phylink state, MAC flags, XDP program pointer, timestamp flags, and FMan buffer-layout headroom. No persistent storage is used. The global `dpaa_bp_array` maps BPIDs to pool objects with refcounts so pools can be reused and drained safely.

## Dependencies and Integration Points
The driver depends on `soc/fsl/qman.h`, `soc/fsl/bman.h`, FMan port/MAC APIs, phylink, BPF/XDP, DMA mapping, PTP timestamping via FMan port headroom, kernel tracepoints, and the sidecar files `dpaa_ethtool.c`, `dpaa_eth_sysfs.c`, and `dpaa_eth_trace.h`.

## Risks
The driver is sensitive to DMA ownership and buffer accounting: missed decrements or failed remaps can leak pages or starve BMan pools. `dpaa_cleanup_tx_fd()` and SG conversion paths must match every mapping exactly. XDP supports only contiguous RX frames and rejects SG under XDP. Erratum A050385 rewrites or copies buffers and can affect metadata/headroom semantics. Congestion-group thresholds are speed dependent and must be updated on link changes. Probe failure unwinding crosses many subsystems and is a high-risk path. `dpaa_start_xmit()` reports `NETDEV_TX_OK` after freeing dropped skbs, so drop visibility depends on stats.

## Test Signals
Strong signals include module load/unload, probe deferral when QMan/BMan portals are missing, ifup/ifdown loops, phylink link changes, MTU and XDP MTU validation, single and multiqueue TX, SG and non-SG TX/RX, TX timestamping, RX timestamp/hash/checksum offload, XDP PASS/DROP/TX/REDIRECT, QMan congestion transitions, BMan pool low-memory refill behavior, PCD RX queue distribution, TC mqprio setup, and error FD/ERN handling.
