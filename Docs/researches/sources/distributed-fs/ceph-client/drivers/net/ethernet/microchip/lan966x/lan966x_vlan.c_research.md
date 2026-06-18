# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vlan.c

## Purpose
This file owns LAN966x VLAN membership and per-port VLAN classification/rewriter programming. It keeps software masks for hardware VLAN table membership, tracks CPU VLAN intent, updates PVID/native VLAN state, applies ingress/egress tag behavior, and coordinates FDB/MDB entries when the CPU port joins or leaves VLANs.

## Important APIs, Types, And Functions
Public driver functions include `lan966x_vlan_init()`, `lan966x_vlan_port_add_vlan()`, `lan966x_vlan_port_del_vlan()`, `lan966x_vlan_cpu_add_vlan()`, `lan966x_vlan_cpu_del_vlan()`, `lan966x_vlan_port_apply()`, `lan966x_vlan_port_set_vid()`, `lan966x_vlan_port_set_vlan_aware()`, `lan966x_vlan_port_rew_host()`, and `lan966x_vlan_cpu_member_cpu_vlan_mask()`. Internal helpers manipulate `lan966x->vlan_mask[vid]`, `lan966x->cpu_vlan_mask`, and the `ANA_VLANACCESS` table command interface.

## Control Flow
`lan966x_vlan_init()` initializes the VLAN table, clears all normal VLANs, programs HOST and UNAWARE PVID membership for all physical ports plus CPU, configures the CPU port as VLAN-aware, and clears per-port REW VLAN settings. Adding a front-port VLAN may first add the CPU port and write FDB/MDB entries if bridge CPU intent already exists; then it updates PVID/native fields, hardware membership, and port registers. Deleting a VLAN removes port classification state and hardware membership, then removes CPU hardware membership and FDB/MDB entries when no front ports remain. CPU VLAN add/delete keeps an intent bitmap separate from active hardware membership.

## State And Persistence
All state is runtime memory plus hardware registers. `vlan_mask` is the source for VLAN table writes; `cpu_vlan_mask` records bridge CPU VLAN membership even when no front port currently uses that VID; each `lan966x_port` stores `pvid`, `vid`, and `vlan_aware`. Hardware state is in ANA VLAN table, ANA ingress VLAN/drop configuration, DEV MAC tag awareness, REW tag configuration, REW port VLAN defaults, and FDB/MDB tables updated by other files.

## Dependencies And Integration Points
The file is integrated with bridge VLAN callbacks, switchdev FDB/MDB helpers, LAN966x register accessors, and netdev port state. It depends on constants such as `HOST_PVID`, `UNAWARE_PVID`, `CPU_PORT`, `VLAN_N_VID`, and table polling timeouts from surrounding headers.

## Risks And Edge Cases
Only one untagged/native VLAN is allowed per port; attempts to add a second return `-EBUSY`. VLAN table update failures are logged but not propagated from `lan966x_vlan_set_mask()`, so callers may believe a software update succeeded when hardware rejected or timed out. CPU hardware membership is intentionally suppressed when no front ports are in the VLAN, which is important for broadcast storm avoidance but can surprise tests that inspect raw membership. `GENMASK(lan966x->num_phys_ports - 1, 0)` assumes at least one physical port.

## Test Signals
Test bridge VLAN add/delete, PVID transitions, untagged VLAN conflicts, host-mode tag insertion, VLAN-aware ports without PVID dropping untagged frames, CPU VLAN membership before and after first front-port join, FDB/MDB replay/erase, and table command timeout logging.
