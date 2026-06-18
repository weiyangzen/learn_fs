# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.c

## Purpose
`abm/main.c` registers and coordinates the NFP Advanced Buffer Management NIC app. It owns app-level initialization/cleanup, devlink eswitch mode transitions, representor creation/removal, per-vNIC ABM link allocation, persistent MAC assignment, queue-manager reset, ABM stats exposure, TC setup dispatch, and the `app_abm` type definition.

## Important APIs, types, and functions
`nfp_abm_portid()` encodes representor type and id into an ABM port id. `nfp_abm_setup_tc()` dispatches TC root/qdisc/block setup to ABM qdisc and classifier helpers. `nfp_abm_repr_get()`, `nfp_abm_spawn_repr()`, and `nfp_abm_kill_repr()` manage representor lookup and lifetime. Eswitch functions are `nfp_abm_eswitch_mode_get()`, `nfp_abm_eswitch_set_legacy()`, `nfp_abm_eswitch_set_switchdev()`, and `nfp_abm_eswitch_mode_set()`. Per-vNIC lifecycle is handled by `nfp_abm_vnic_alloc()`, `nfp_abm_vnic_free()`, and `nfp_abm_vnic_init()`. App lifecycle is `nfp_abm_init()` and `nfp_abm_clean()`.

## Control flow
App init validates ETH table and MAC stats availability, allocates `struct nfp_abm`, discovers firmware control addresses, allocates threshold/action state, resets firmware queue levels/actions, disables QM, and allocates representor tables for physical and PF representors. Each vNIC allocation creates an `nfp_abm_link`, reads firmware parameters, allocates a priority map, configures the physical MAC as up, keeps dst cache entries, assigns a persistent MAC from NSP hwinfo or random fallback, and initializes qdisc tracking. Switchdev mode enables QM and spawns physical plus PF representors for each vNIC; legacy mode kills all representors and disables QM. Cleanup forces legacy mode, frees representor tables and app state.

## State and persistence
`struct nfp_abm` persists for the app lifetime and stores firmware capabilities, threshold/action arrays, representor mode, and symbol pointers. Each `struct nfp_abm_link` is attached to `nn->app_priv` and stores vNIC id, queue base, total queues, priority map, DSCP mappings, default band, qdisc tree, and stats timing. Persistent MAC lookup uses NSP hardware info keys like `eth%u.mac.pf%u`; if unavailable, runtime random MAC addresses are assigned.

## Dependencies and integration points
The file integrates with the NFP app framework, PF/vNIC lists, NSP/hwinfo, NFP port and representor infrastructure, RCU-protected representor arrays, rtnl locking, devlink eswitch mode APIs, TC qdisc/classifier setup, ABM control helpers, and ethtool stats hooks.

## Risks and edge cases
Switchdev transition has multi-step failure cleanup: if any representor spawn fails, all spawned representors are killed and QM is disabled. RCU and RTNL ordering around representor arrays must remain correct. `nfp_abm_vnic_set_mac()` checks `if (id > pf->eth_tbl->count)`, which permits `id == count` even though array indexing uses `ports[id]`; this boundary deserves scrutiny. Init assumes `max_data_vnics` equals ETH table count. Firmware RED support gates switchdev mode. Qdisc radix tree must be empty on vNIC free.

## Test signals
Useful tests include app init with missing ETH table, mismatched vNIC/ETH counts, missing MAC stats, firmware discovery failure, legacy-to-switchdev and switchdev-to-legacy devlink transitions, representor spawn failure unwinds, vNIC alloc/free/init, NSP MAC lookup success/failure/parse failure, ABM port stats string/count/value exposure, TC setup dispatch for root/MQ/RED/GRED/block, and cleanup with active qdisc/classifier state.
