# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_l2.c

## Purpose

`qed_l2.c` implements the QED Ethernet/L2 slowpath operations. It allocates L2 queue bookkeeping, converts logical queue parameters into firmware CIDs and absolute resource IDs, starts/stops vports and RX/TX queues, updates RSS/TPA/filter modes, programs unicast/multicast/aRFS filters, reads and resets Ethernet statistics, configures tunnel ports, and publishes the `qed_eth_ops` table consumed by the upper Ethernet driver.

The file is the main bridge between the protocol-facing `linux/qed/qed_eth_if.h` operations and QED firmware ramrods. It handles both PF and VF flows, using direct SPQ ramrods for PFs and VF/PF mailbox helpers for VFs.

## Important APIs, types, and functions

- `struct qed_l2_info` holds the number of L2 queues and a per-queue-zone bitmap of queue usage indices protected by a mutex.
- `qed_l2_alloc()`, `qed_l2_setup()`, and `qed_l2_free()` allocate, initialize, and release L2 queue bookkeeping.
- `qed_eth_queue_to_cid()` and `_qed_eth_queue_to_cid()` allocate or derive firmware CIDs and fill `struct qed_queue_cid` with relative and absolute vport, queue, stats, status-block, VF, and queue-zone usage metadata.
- `qed_eth_queue_cid_release()` releases firmware CIDs for PF queues, clears queue-zone usage for self-owned queues, and frees the queue handle.
- `qed_sp_eth_vport_start()`, `qed_sp_vport_update()`, and `qed_sp_vport_stop()` build vport start/update/stop ramrods.
- `qed_eth_rxq_start_ramrod()`, `qed_eth_rx_queue_stop()`, `qed_eth_txq_start_ramrod()`, and `qed_eth_tx_queue_stop()` build queue start/stop ramrods and release queue handles on successful stop.
- `qed_sp_eth_filter_ucast()`, `qed_mcast_bin_from_mac()`, and the filter command helpers program unicast, multicast, VLAN, VNI, and accept-mode filtering.
- Statistics helpers read MSTORM, USTORM, TSTORM, PSTORM, and MCP port stats into `struct qed_eth_stats`; public functions are `qed_get_vport_stats()`, `qed_get_vport_stats_context()`, and `qed_reset_vport_stats()`.
- `qed_arfs_mode_configure()` and `qed_configure_rfs_ntuple_filter()` configure accelerated RFS search profiles and individual GFT ntuple filters.
- `qed_get_queue_coalesce()`, `qed_get_rxq_coalesce()`, and `qed_get_txq_coalesce()` read queue coalescing values from CAU and storm memories.
- `qed_get_eth_ops()` exports the `qed_eth_ops_pass` operation table.

## Control flow

L2 allocation begins with `qed_l2_alloc()`, which exits early for non-L2 personalities. PF queue count comes from `RESC_NUM(QED_L2_QUEUE)`, while VF queue count is the max of VF RX and TX queues reported by the PF. The function allocates one bitmap per queue zone, each sized for `MAX_QUEUES_PER_QZONE`. `qed_l2_setup()` initializes the mutex after allocation.

Queue start flows first allocate a queue CID. For PFs, `qed_eth_queue_to_cid()` acquires a protocol CID from context management unless the queue is a legacy VF CID. `_qed_eth_queue_to_cid()` translates relative vport and L2 queue IDs to firmware absolute IDs, handles VF-specific stats and queue metadata, and allocates a queue-zone usage index unless VF parameters already supply one. RX start initializes the PF producer GTT memory to zero before posting `ETH_RAMROD_RX_QUEUE_START`; VF RX start delegates to `qed_vf_pf_rxq_start()`. TX start posts `ETH_RAMROD_TX_QUEUE_START`, selects a PQ with `qed_get_cm_pq_idx_mcos()`, and returns a doorbell address for PF queues.

Queue stop flows post RX or TX stop ramrods for PFs or VF mailbox requests for VFs. RX stop chooses CQE and EQE completion flags based on whether the queue belongs to the PF itself, whether only EQ completion is requested, and whether CQE completion is forced. On successful stop, the queue CID is released, which also clears the queue-zone usage bit for self-owned queues.

Vport start is exposed externally by `qed_start_vport()`. It loops over hardware functions, fills `qed_sp_vport_start_params`, posts PF or VF vport start, starts fastpath hardware with `qed_hw_start_fastpath()`, and optionally resets stats. Vport update translates protocol-level flags to `qed_sp_vport_update_params`, optionally prepares per-hwfn RSS parameters, and posts one update per hwfn. In CMT mode, RSS indirection entries are split by queue owner; if an engine would use only one queue, RSS is disabled for that update.

Filtering has three main paths. Accept-mode changes build a vport update with RX/TX accept flags. Unicast filter commands translate high-level add/delete/replace to firmware filter actions, support MAC, VLAN, MAC/VLAN, inner MAC/VLAN, MAC/VNI, and VNI forms, and can emit two firmware commands for move or replace. Multicast programming hashes MACs into approximate multicast bins using CRC32C and posts a vport update; ADD is treated as setting the full bin vector while REMOVE clears it.

Statistics are gathered per hwfn. PFs acquire a PTT and read fixed storm memory offsets; VFs read addresses and lengths supplied by the PF in the acquire response. The leading PF also reads MCP public port statistics and link-change count. `qed_reset_vport_stats()` zeroes per-vport storm stats and stores a baseline snapshot for port stats that cannot necessarily be reset.

The exported operation table wires these internals into the public Ethernet interface: device info, vport start/stop/update, queue start/stop, filter configuration, fastpath stop, CQE completion, stats, tunnel configuration, ntuple/aRFS, coalescing, MAC validation, and VF bulletin MAC update.

## State and persistence behavior

State is volatile kernel and device state. `struct qed_l2_info` persists only for the lifetime of the hwfn L2 personality and tracks queue-zone usage. Each started queue returns a dynamically allocated `struct qed_queue_cid` handle that owns the firmware CID and queue-zone usage index until queue stop releases it.

Firmware/device state is mutated through SPQ ramrods and direct register or memory writes. Examples include vport active/accept/RSS/TPA/filter state, RX/TX queue state, producer initialization in MSTORM GTT memory, approximate multicast bins, GFT filter entries, tunnel port configuration, and storm statistics reset writes. No on-disk persistence exists.

The code handles multi-hwfn devices by iterating `for_each_hwfn()` and splitting queue IDs/RSS tables by `rss_num % cdev->num_hwfns`. VF state changes generally route through VF/PF helpers rather than direct firmware ramrods.

## Dependencies and integration points

This file depends on Linux DMA, CRC32C, bit operations, vmalloc, Ethernet helpers, and QED subsystems: context allocation (`qed_cxt`), slowpath queue (`qed_sp`), hardware/PTT/register access (`qed_hw`, `qed_dev_api`, `qed_reg_addr`), interrupts/status blocks (`qed_int`), MCP public data (`qed_mcp`), SR-IOV VF/PF mailbox (`qed_sriov`), DCB and PTP operation tables, tunnel configuration, and firmware HSI ramrod structures.

External integration is through `qed_get_eth_ops()` and `qed_put_eth_ops()` exports. The returned `qed_eth_ops` table is consumed by the Ethernet client driver and references shared common, IOV, DCB, and PTP operation tables when configured.

## Risks and edge cases

- `qed_l2_alloc()` can leak earlier allocations if a later queue bitmap allocation fails; cleanup is deferred to caller paths only if they call `qed_l2_free()`.
- Queue-zone usage is protected by a mutex, but invalid queue IDs or exhausted per-zone usage return failure and can prevent queue start.
- The queue start wrappers mutate `p_params->queue_id` by dividing it by `num_hwfns`; callers must not assume the original value remains intact after the call.
- RSS update silently disables RSS if the CMT split degenerates to one queue per engine, by clearing `params->update_rss_flg` after `qed_update_vport_rss()` returns an error.
- Multicast REMOVE clears the entire approximate multicast vector rather than selectively removing only supplied addresses.
- Many operations are per-hwfn loops with partial failure risk; if a later hwfn fails, earlier hwfns may already have been configured.
- VF paths rely on PF-provided resource counts, stats addresses, and mailbox helpers. Incorrect PF/VF capability negotiation can affect queue, stats, XDP, or filter behavior.
- Statistics reset stores a baseline for non-resettable port stats; consumers must understand that returned values are adjusted by `cdev->reset_stats`.
- aRFS VF filter configuration rewrites `vport_id` and `qid` when `b_is_vf` is set, so caller-provided queue targeting is intentionally ignored for VF filters.

## Test signals

Important coverage includes PF and VF L2 allocation/free, queue-zone bitmap exhaustion, RX/TX queue start and stop for PF, VF, and legacy VF modes, vport start/update/stop, GRO/TPA parameter programming, RSS table programming on single-hwfn and CMT devices, accept-mode transitions for normal/promisc/multicast-promisc, unicast add/delete/replace/move for MAC/VLAN/VNI forms, multicast bin hashing and full-vector updates, stats read/reset for PF and VF, tunnel port bulletin propagation to VFs, aRFS enable/disable and ntuple add/delete/drop, coalescing reads for RX/TX queues, and partial-failure handling across multi-hwfn loops.
