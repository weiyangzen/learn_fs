# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sched.c

## Purpose

`ice_sched.c` implements the Intel ice transmit scheduler software database and the firmware AdminQ operations used to build, move, suspend, resume, rate-limit, and replay scheduler topology. It mirrors firmware scheduler elements into `struct ice_sched_node` trees under `struct ice_port_info`, manages VSI and queue-group placement for LAN/RDMA queues, provides aggregator nodes for VSI grouping, and maintains rate-limit profiles for CIR, EIR, and shared bandwidth.

## Important APIs, Types, And Functions

- Firmware command wrappers include `ice_aq_query_sched_elems()`, `ice_aq_add_sched_elems()`, `ice_aq_delete_sched_elems()`, `ice_aq_cfg_sched_elems()`, `ice_aq_move_sched_elems()`, suspend/resume helpers, scheduler resource query, and RL profile add/remove.
- Topology initialization and cleanup are handled by `ice_sched_query_res_alloc()`, `ice_sched_get_psm_clk_freq()`, `ice_sched_init_port()`, `ice_sched_clear_port()`, `ice_sched_cleanup_all()`, and `ice_free_sched_node()`.
- Tree lookup and mutation helpers include `ice_sched_find_node_by_teid()`, `ice_sched_add_node()`, `ice_sched_add_elems()`, `ice_sched_add_nodes_to_layer()`, `ice_sched_move_nodes()`, and `ice_sched_update_parent()`.
- Layer helpers `ice_sched_get_qgrp_layer()`, `ice_sched_get_vsi_layer()`, and `ice_sched_get_agg_layer()` adapt the logical tree to 5/7/9-layer firmware topologies.
- VSI scheduling APIs include `ice_sched_cfg_vsi()`, `ice_sched_get_free_qparent()`, `ice_rm_vsi_lan_cfg()`, and `ice_rm_vsi_rdma_cfg()`.
- Aggregator APIs include `ice_cfg_agg()`, `ice_move_vsi_to_agg()`, `ice_sched_get_agg_node()`, `ice_sched_clear_agg()`, `ice_sched_replay_agg_vsi_preinit()`, `ice_sched_replay_agg()`, and `ice_replay_vsi_agg()`.
- Bandwidth APIs include `ice_cfg_q_bw_lmt()`, `ice_cfg_q_bw_dflt_lmt()`, `ice_cfg_vsi_bw_lmt_per_tc()`, `ice_cfg_vsi_bw_dflt_lmt_per_tc()`, `ice_sched_set_node_bw_lmt()`, `ice_sched_set_node_priority()`, `ice_sched_set_node_weight()`, `ice_cfg_rl_burst_size()`, and `ice_sched_replay_q_bw()`.

## Control Flow

Scheduler setup first queries resource allocation to populate `hw->num_tx_sched_layers`, physical layer count, flattening bitmap, maximum children per layer, and layer capabilities. `ice_sched_init_port()` then fetches firmware default topology for the logical port, creates the root node, inserts every default branch element into the software tree, records the software entry point layer, removes default leaf/intermediate nodes that software should own, marks the port ready, initializes `sched_lock`, and initializes per-layer rate-limit profile lists.

When a VSI is configured, `ice_sched_cfg_vsi()` locates the TC branch and VSI context, optionally suspends an existing VSI node when the TC is disabled, or creates a new VSI path when enabled. It calculates required support nodes from the software entry point to the VSI layer and child nodes from the VSI layer to the queue-group layer, adds nodes through AdminQ, stores queue context arrays, and resumes a suspended node if needed. Queue-parent selection balances queues across queue-group siblings belonging to the same VSI subtree and owner.

Removal walks all traffic classes under `sched_lock`. `ice_sched_rm_vsi_subtree()` refuses to remove a VSI subtree if leaf queue nodes remain, deletes LAN or RDMA-owned child nodes, removes empty VSI nodes, and clears aggregator VSI metadata only after all VSI nodes are gone. The code intentionally does not shrink scheduler nodes when a VSI later requests fewer queues because existing nodes may own rate-limit or shared-rate-limit configuration.

Aggregator control creates an aggregator node at the topology-dependent aggregator layer, with intermediate nodes inserted as needed. Moving a VSI to an aggregator either finds a free parent under the aggregator subtree or creates intermediate nodes, then performs a firmware move and updates the software parent arrays. Removing an aggregator first moves attached VSIs back to the default aggregator and only frees the aggregator subtree when no VSI children remain.

Bandwidth control converts requested Kbps values into firmware RL profile parameters using the PSM clock, profile multipliers, wake-up calculation, and burst size. The code reuses matching profiles per layer/type/bandwidth, tracks profile reference counts, configures scheduler element sections, and removes stale profiles when no longer referenced. Shared bandwidth and EIR are mutually exclusive, so the code clears one path before enabling the other. Replay functions rebuild aggregator membership and restore saved queue/VSI bandwidth after reset.

## State And Persistence

Persistent runtime state is in memory and hardware/firmware, not on disk. `pi->root`, `pi->sib_head`, `pi->sched_node_ids`, and each node's parent/children/sibling fields mirror the scheduler tree. `ice_vsi_ctx->sched` stores per-TC VSI nodes, maximum LAN/RDMA queue counts, queue contexts, and replay bandwidth information. `pi->rl_prof_list[layer]` stores created RL profiles with reference counts. `hw->agg_list` stores aggregator IDs, type, TC bitmaps, replay TC bitmaps, and per-aggregator VSI membership. Firmware state is changed through AdminQ calls; after resets, replay code reconstructs selected software-saved configuration.

## Dependencies And Integration Points

The file depends on `ice_sched.h`, `ice_common.h` types, AdminQ descriptors, `ice_aq_send_cmd()`, register access via `rd32()`, firmware scheduler element formats, Linux list/xarray/mutex primitives, VSI context helpers, and shared driver constants for traffic classes, bandwidth types, queue handles, TEIDs, and scheduler defaults. It is used by VSI setup/teardown, queue configuration, devlink or tc bandwidth controls, reset replay, RDMA queue setup, and aggregator/VSI grouping paths.

## Risks

- Most topology mutations require `pi->sched_lock`; lookup helpers document this but cannot enforce it, so misuse can corrupt parent/child/sibling state.
- `ice_sched_add_elems()` returns immediately on `kzalloc()` failure for a node name after firmware nodes may already have been added, leaving partial topology that callers must unwind via broader cleanup.
- Firmware command success is often checked using both status and returned count; mismatched count paths become `-EIO`, but software state may already be partly updated in multi-node loops.
- Shared-rate-limit layer selection may choose a parent or child of the requested node. The validation requires single-child relationships, so later topology changes can make replay/configuration fail.
- Bandwidth profile reference counts are local bookkeeping. Any missed decrement can leak firmware profiles; any extra decrement could remove a profile still in use.
- Aggregator replay relies on saved bitmaps and enabled TC discovery after reset, so missing TC nodes are silently skipped and logged only at higher replay failures.

## Test Signals

Useful tests include AdminQ-mocked topology initialization for 5/7/9-layer layouts, node add/move/remove checks that validate parent arrays and sibling heads, VSI queue growth tests for LAN and RDMA owners, refusal tests when removing subtrees with leaf nodes, aggregator create/move/remove/replay tests, RL profile reuse/refcount/default-clearing tests, shared-vs-EIR exclusivity tests, burst-size boundary tests, and reset replay tests that verify queue/VSI bandwidth and aggregator membership are restored.
