# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wqe.h

## Purpose
Defines hardware WQE, CQE, command-queue, SQ, and RQ wire formats for the original HiNIC driver. It is an ABI header shared by queue allocation, Tx/Rx datapaths, and firmware command submission.

## Important APIs, Types, And Constants
The file provides bitfield setters/getters for command queue control/header words, SQ control and task offload words, RQ CQE status/length/offload fields, RSS type bits, VLAN extraction, and packet/LRO decoding. Key sizes are `HINIC_SQ_WQE_MAX_SIZE`, `HINIC_RQ_WQE_SIZE`, `HINIC_MAX_SQ_BUFDESCS`, and `HINIC_SQ_WQE_SIZE(nr_sges)`. Important structs include `hinic_cmdq_wqe_scmd`, `hinic_cmdq_wqe_lcmd`, `hinic_sq_wqe`, `hinic_rq_cqe`, `hinic_rq_wqe`, and the top-level `union` in `struct hinic_hw_wqe`.

## Control Flow And State
There is no executable flow; state is encoded in WQE/CQE fields consumed by hardware and the datapath. Tx fills SQ control/task/buffer descriptors for checksum, TSO, tunnel, VLAN, and scatter-gather DMA. Rx reads RQ CQE status bits for RXDONE, checksum errors, LRO packet count, VLAN tag, packet type, and SGE length. Command-queue code uses the command WQE structs for short and long commands and either direct or SGE completion response.

## Dependencies And Integration Points
The header depends on `hinic_common.h` for SGE layout and endian helpers. It is directly used by `hinic_tx.c`, `hinic_rx.c`, `hinic_hw_wq.c`, `hinic_hw_cmdq.c`, and queue-pair helpers. Its definitions must match firmware and hardware documentation exactly.

## Risks And Test Signals
Risk concentrates in bitfield definitions, endian conversions, and size/alignment of hardware structs. Incorrect masks can manifest as broken offloads, corrupt DMA descriptors, false checksum errors, missing completions, or command timeouts. Test signals include checksum/TSO/tunnel/VLAN/LRO traffic, RSS configuration, command-queue direct and SGE responses, and hardware counter or dmesg errors under mixed offload workloads.
