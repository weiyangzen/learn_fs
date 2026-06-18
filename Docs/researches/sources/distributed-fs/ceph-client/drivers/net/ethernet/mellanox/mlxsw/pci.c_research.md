# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci.c

## Purpose
`pci.c` implements the high-performance mlxsw PCI bus backend. It owns PCI probe/remove/reset handling, command-register execution, firmware area mapping, async send/receive/completion/event queues, DMA mapping, NAPI processing, packet transmit/receive handoff, profile configuration, resource discovery, clock reads, and integration with the mlxsw core bus.

## Important APIs, Types, and Functions
- `struct mlxsw_pci` stores PCI device state, BAR mapping, queue groups, FW area pages, command mailboxes, bus info, capabilities, profile-selected modes, CQE version, SDQ/CQ counts, reset behavior, and dummy NAPI netdevs.
- Queue structures are `struct mlxsw_pci_queue`, `struct mlxsw_pci_queue_elem_info`, `struct mlxsw_pci_queue_type_group`, and queue ops tables for SDQ, RDQ, CQ, and EQ.
- Initialization paths include `mlxsw_pci_probe()`, `mlxsw_pci_cmd_init()`, bus callback `mlxsw_pci_init()`, `mlxsw_pci_reset()`, `mlxsw_pci_fw_area_init()`, `mlxsw_pci_config_profile()`, `mlxsw_pci_aqs_init()`, and per-queue init functions.
- Data paths include `mlxsw_pci_skb_transmit()`, `mlxsw_pci_cqe_sdq_handle()`, `mlxsw_pci_cqe_rdq_handle()`, `mlxsw_pci_napi_poll_cq_tx()`, `mlxsw_pci_napi_poll_cq_rx()`, and `mlxsw_pci_eq_tasklet()`.
- Command execution is `mlxsw_pci_cmd_exec()`, which serializes command registers, maps in/out mailboxes, polls GO bit, and copies direct or mailbox output.

## Control Flow
PCI probe allocates private state, enables the function, requests regions, sets DMA mask, maps BAR0, initializes command mailboxes, fills bus info, and registers the mlxsw bus. The bus init waits for system readiness, resets hardware unless recovery already did, allocates MSI-X, queries firmware, validates command interface/BAR expectations, maps firmware area pages, reads board info, queries resources, chooses CQE version, configures profile and modes, re-queries resources, initializes NAPI dummy devices, allocates EQ/CQ/SDQ/RDQ queue groups, and requests the EQ IRQ. EQ interrupts schedule a tasklet, the tasklet records active CQs and schedules their NAPI instances, NAPI drains CQEs, and CQ handlers process transmit completions or received packets.

## State and Persistence
Persistent runtime state includes DMA coherent queue memory, page-pool pages for receive WQEs, command mailboxes, firmware-area pages mapped to hardware, producer/consumer counters, owner-bit parity, skb pointers stored in SDQ element info, selected LAG/flood modes, clock offsets, and bus capabilities. Hardware state includes reset mode, config profile, queue ownership, doorbells, firmware area mappings, and command-register state.

## Dependencies and Integration Points
The file depends on Linux PCI/MSI-X/IRQ/tasklet/NAPI/page_pool/DMA APIs, mlxsw command mailbox helpers, `pci_hw.h` descriptor accessors, core bus registration, core packet receive/transmit callbacks, PTP timestamp handling, resource queries, tx header helpers, and port constants. It exports `mlxsw_pci_driver_register()` and `mlxsw_pci_driver_unregister()` so chip-specific PCI drivers can reuse this backend.

## Risks
Queue ownership and producer/consumer counters are subtle; incorrect owner-bit parity, missing barriers, or wrong doorbell order can cause lost completions or DMA races. Receive page replacement happens before skb construction, so allocation failure must recycle old pages correctly. `mlxsw_pci_skb_transmit()` must unmap all mapped fragments on partial failure and avoid leaking the skb pointer on failed first-fragment mapping. Reset and PCI error recovery paths must avoid double reset by using `skip_reset`. CQE version negotiation affects descriptor sizes and accessors; unsupported resource combinations abort init.

## Test Signals
Test PCI probe/remove, reset and PCI error recovery, command timeout/status errors, resource combinations for CQE v0/v1/v2, profile LAG/flood mode choices, TX queue full/EAGAIN behavior, TX completion DMA unmap and timestamp delivery, RX multi-fragment packets, mirror/sample metadata extraction, page-pool recycling under allocation failure, MSI-X EQ scheduling, NAPI budget behavior, and teardown with active queues.
