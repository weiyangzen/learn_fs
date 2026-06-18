# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_rcb.h

## Purpose

`hns_dsaf_rcb.h` declares RCB topology constants, interrupt flags, ring/common control blocks, stats structures, and public RCB APIs used by the HNS DSAF and netdev layers. It is the shared contract between low-level RCB hardware programming and the Ethernet data path.

## Important APIs, Types, And Functions

Important constants describe IRQ layout, ring offset, service/debug engine count, descriptor limits, MTU limit, pending descriptor bounds, coalescing limits/defaults, buffer-size encodings, dump sizes, and TSO mode encodings. `enum rcb_int_flag` defines TX and RX interrupt flags. `struct hns_ring_hw_stats` stores RCB/PPE packet counters for a ring pair. `struct ring_pair_cb` binds one `hnae_queue` to common RCB state, device, global index, buffer size, TX/RX IRQs, port id, VF usage marker, and hardware stats. `struct rcb_common_cb` stores common MMIO/physical bases, DSAF device, VM/queue limits, common index, ring count, descriptor count, and the flexible ring-pair array.

The function declarations cover allocation/configuration, hardware init/commit, interrupt control, ring reset, descriptor drain waits, coalescing accessors, stats, register dumps, strings, and RX/TX buffer-size programming.

## Control Flow

No code executes in this header. Its layout drives RCB lifecycle: DSAF/PPE code allocates common blocks, netdev code consumes `hnae_queue` ring fields, ethtool queries use the stats/register functions, and reset paths call drain/reset helpers. The header also keeps v1/v2 differences visible through constants such as `HNS_RCB_RING_MAX_TXBD_PER_PKT` and `HNS_RCBV2_RING_MAX_TXBD_PER_PKT`.

## State And Persistence

The structures here hold in-memory topology and cumulative stats for a device instance. `io_base` and `phy_base` connect those objects to MMIO and DMA-visible addresses, while `desc_num`, `ring_num`, `max_vfn`, and `max_q_per_vf` persist the DSAF-mode-derived topology until device teardown.

## Dependencies And Integration Points

The header includes Linux netdevice/platform-device types plus `hnae.h` and `hns_dsaf_main.h`. It is included by PPE, RCB implementation, and netdev code. It is tightly coupled to `hnae_queue` and `hnae_ring` layout because `ring_pair_cb` embeds a queue.

## Risks And Test Signals

Risks include structure layout drift from `hnae`, incorrect dump/stat count constants, and callers passing unsupported buffer sizes to `hns_rcb_buf_size2type`. Test signals are clean builds across hardware-version configs, ethtool stat count consistency, queue count within `NIC_MAX_Q_PER_VF`, and no ring allocation or IRQ setup failures during probe.
