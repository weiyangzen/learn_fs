# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/action.c

## Purpose
This file compiles Linux TC flower action lists into the NFP Flower firmware action bytecode stored in `nfp_fl_payload->action_data`. It supports output/mirror/redirect, VLAN/MPLS push/pop/mangle, tunnel encap/decap, packet edits, checksum validation, LAG pre-actions, pre-tunnel actions, ptype handling, and QoS meter actions.

## Important APIs, types, and functions
- `nfp_flower_compile_action()` is the exported compiler entry point. It validates delayed hardware stats, iterates TC actions, accumulates NFP actions, and records final action length/shortcut.
- Action encoders include `nfp_fl_push_mpls()`, `nfp_fl_pop_mpls()`, `nfp_fl_set_mpls()`, `nfp_fl_push_vlan()`, `nfp_fl_pop_vlan()`, `nfp_fl_output()`, `nfp_fl_set_tun()`, and `nfp_fl_meter()`.
- Pedit support is split across `nfp_fl_set_eth()`, `nfp_fl_set_ip4()`, `nfp_fl_set_ip6()`, `nfp_fl_set_tport()`, accumulated in `struct nfp_flower_pedit_acts`, and emitted by `nfp_fl_commit_mangle()`.
- `nfp_flower_loop_action()` is the per-action dispatcher and enforces feature/size/order constraints.
- `nfp_fl_push_geneve_options()` emits Geneve options in reverse order for hardware.

## Control flow
The compiler zeros the action buffer, initializes tunnel/output/checksum state, and walks actions. Consecutive mangle actions are accumulated so multiple pedit operations on the same hardware action can be merged before emission. Output actions validate the egress netdev, representor parent, tunnel type, LAG support, internal-port/pre-tunnel constraints, and last/mirror flags. Tunnel encap inserts a pre-tunnel action at the beginning of the list, optional Geneve option pushes, then a set-tunnel action. Checksum actions are accepted only if prior mangle actions caused hardware-supported checksum updates and consume the pending checksum flags.

## State and persistence
State is per compilation: `action_data`, `meta.shortcut`, `meta.act_len`, tunnel type, output counts, pedit accumulator, checksum flags, and ptype-host marker. It persists only as part of an offloaded flow payload in memory and firmware after the caller transmits the flow.

## Dependencies and integration points
This compiler uses TC action APIs, flow dissector data, NFP Flower firmware ABI structs from `cmsg.h`, LAG helpers from `lag_conf.c`, internal-port helpers from `main.c`, tunnel feature flags from `main.h`, and meter lookup helpers. The resulting action buffer is sent by flow offload paths outside this file.

## Risks
Most risks are ABI and validation risks. `NFP_FL_MAX_A_SIZ` must be enforced for every inserted action, especially pre-actions that memmove existing data. Pedit endian/mask handling must match TC semantics and firmware. Tunnel flag constants deliberately guard against kernel ABI drift with `BUILD_BUG_ON`. The helper `nfp_fl_check_mangle_end()` compares `current_act_idx == num_entries`, which looks suspicious because the last valid index is `num_entries - 1`; tests should confirm final mangle groups are committed.

## Test signals
Exercise each action type, maximum action length failures, multiple output/tunnel rejection, LAG as last action, pre-tunnel internal-port ptype requirements, Geneve option limits, IPv4/IPv6/tport/eth pedit plus csum ordering, unsupported stats mode, and mixed action lists where shortcut must fall back to null.
