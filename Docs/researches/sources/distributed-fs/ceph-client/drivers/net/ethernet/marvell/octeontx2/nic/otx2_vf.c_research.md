# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_vf.c

## Purpose
`otx2_vf.c` is the PCI/netdev driver for OcteonTX2/CN10K RVU virtual functions, including regular VFs, LBK VFs, and SDP representor VFs. It owns VF probe/remove, mailbox setup with PF/AF, netdev operations, feature setup, queue/resource attachment, TC/QoS/devlink/XSK initialization, and reset/rx-mode work.

## Important APIs, Types, and Functions
The module registers `otx2vf_driver` for AFVF/VF/SDP IDs. Netdev ops include open/stop/xmit/select queue/rx mode/MAC/MTU/features/stats/timeout/TC/hwtstamp. Important helpers include `otx2vf_vfaf_mbox_init()`, `otx2vf_register_mbox_intr()`, mailbox work handlers, `otx2vf_probe()`, `otx2vf_remove()`, `otx2vf_xmit()`, `otx2vf_change_mtu()`, and `otx2vf_reset_task()`.

## Control Flow
Probe enables PCI, allocates netdev queues including QoS headroom, maps CSRs/mailbox, initializes hardware ops, verifies mailbox readiness, attaches NPA/NIX resources, reallocates MSI-X vectors, initializes LMT/PTP/MAC/features/IPsec, registers netdev, workqueues, MCAM/TC/devlink/XSK/DCB/QoS. Open delegates to common `otx2_open()` and forces carrier for LBK/SDP devices. TX validates length, calls `otx2_sq_append_skb()`, and stops/wakes queues based on SQB availability. Remove reverses pause/PFC, work, devlink, netdev, IPsec/PTP/MCAM/TC/QoS/resources/mailbox/IRQ/bitmap state.

## State and Persistence
Driver state lives in `struct otx2_nic` attached to the netdev: flags, mailbox, queue counts, LMT/IPsec/PTP/devlink resources, workqueues, TC and QoS state, XSK bitmap, and feature flags. Hardware mailbox state and attached LF resources persist until detach/remove.

## Dependencies and Integration Points
The file integrates with PCI, MSI-X, DMA/IOMMU, common RVU resource management, PF/AF mailbox protocol, CN10K ops, IPsec, PTP, ethtool, DCB, devlink, TC, QoS, and the TX/RX data path. It depends on `otx2_common.h`, `otx2_reg.h`, `otx2_ptp.h`, `cn10k.h`, and `cn10k_ipsec.h`.

## Risks and Edge Cases
Probe has many staged resources; unwind order must match allocation. VF mailbox mapping differs by OTX2/CN10K/CN20K platform. Queue count is based on online CPUs and QoS adds additional TX queues. MTU changes restart the device if up. Feature toggles must coordinate NTUPLE and TC offload. XSK bitmap allocation happens late and must be freed on all error/remove paths.

## Test Signals
Test VF bind/unbind on OTX2, CN10K, CN20K, LBK, and SDP IDs; mailbox deferral; netdev open/stop; TX queue busy recovery; MTU changes under traffic; rx mode changes; reset work; TC flower and HTB offloads; PTP/IPsec/DCB presence; XSK pool setup; and failure injection through probe unwind labels.
