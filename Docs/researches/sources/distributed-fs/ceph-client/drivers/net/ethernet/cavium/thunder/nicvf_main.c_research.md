# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_main.c

## Purpose
`nicvf_main.c` is the PCI/netdev front end for the Cavium ThunderX NIC virtual-function driver. It binds supported Thunder NIC VF PCI IDs, negotiates VF identity and resources with the physical-function driver over a mailbox, registers the Linux `net_device`, owns open/stop/probe/remove lifecycle, and coordinates NAPI, MSI-X interrupts, RSS, XDP, timestamping, multicast receive mode, link state, and statistics.

## Important APIs, Types, and Functions
The file exports low-level register access helpers (`nicvf_reg_read`, `nicvf_reg_write`, `nicvf_queue_reg_read`, `nicvf_queue_reg_write`) and the PF mailbox API `nicvf_send_msg_to_pf`. `nicvf_open` and `nicvf_stop` are the core netdev lifecycle functions; `nicvf_xmit` is `ndo_start_xmit`; `nicvf_probe`, `nicvf_remove`, and `nicvf_shutdown` implement PCI lifecycle. NAPI and interrupt paths are centered on `nicvf_poll`, `nicvf_cq_intr_handler`, `nicvf_intr_handler`, `nicvf_misc_intr_handler`, `nicvf_rbdr_intr_handler`, and `nicvf_qs_err_intr_handler`. Feature-control entry points include `nicvf_change_mtu`, `nicvf_set_mac_address`, `nicvf_set_features`, `nicvf_xdp`, `nicvf_hwtstamp_get`, `nicvf_hwtstamp_set`, and `nicvf_set_rx_mode`.

## Control Flow and Integration
Probe enables PCI, requests regions, sets a 48-bit DMA mask, allocates a multi-queue netdev, maps VF CSRs, allocates per-CPU stats, initializes a queue set, registers the mailbox interrupt, sends the local `nicvf` pointer to PF, determines silicon capabilities, and registers the netdev unless this VF is a secondary queue-set-only VF. Opening the interface registers NAPI contexts, configures mailbox-mediated CPI/RSS/MTU/PTP state, requests secondary queue sets, registers data interrupts, initializes queues through `nicvf_config_data_transfer`, enables CQ/RBDR/QS interrupts, and sends `NIC_MBOX_MSG_CFG_DONE`.

RX/TX completions are consumed in `nicvf_cq_intr_handler`. RX CQEs are converted into SKBs or handled by XDP, then decorated with RX timestamp, RSS hash, queue id, checksum status, VLAN tag, and delivered through GRO or `netif_receive_skb`. TX CQEs free DMA mappings and SKBs, update BQL with `netdev_tx_completed_queue`, wake stopped TX queues, and handle PTP completion CQEs. The mailbox interrupt updates VF identity, link state, RSS size, BGX stats, PFC settings, and primary/secondary VF pointers.

## State and Persistence
Persistent runtime state is in `struct nicvf`: PF ack/nack flags, VF id, node, SQS topology, queue counts, link status, RSS table/key, PTP clock and outstanding timestamp skb, XDP program, per-CPU driver stats, hardware stats, workqueues, delayed link polling, and pointers to secondary/primary VFs. Hardware-visible state lives in VF CSRs and queue descriptors; the file itself does not persist state to disk.

## Dependencies and Risks
This file depends on `nic.h`, `nic_reg.h`, `nicvf_queues.h`, `q_struct.h`, BGX mailbox semantics, Cavium PTP support, PCI/MSI-X, NAPI, XDP, IOMMU translation, and the Linux netdev API. Risks include mailbox timeout or serialization bugs around `rx_mode_mtx`, mismatched queue accounting across primary and secondary VFs, XDP MTU/page-recycling corner cases, single-outstanding TX timestamp assumptions, recursive SQS open/stop ordering, and error paths where partial interrupt/NAPI setup must unwind cleanly.

## Test Signals
Strong signals are probe/open/stop/remove tests on PF-backed hardware or emulation, mailbox ACK/NACK/timeout coverage, multi-queue and SQS traffic, TX ring-full recovery, CQ/RBDR/QS error interrupt injection, XDP attach/detach and XDP_TX traffic, MTU rejection with XDP, hardware timestamp RX/TX validation, multicast/promiscuous mode changes, RSS indirection checks, and stats consistency against hardware counters.
