# sources/distributed-fs/ceph-client/net/bridge/br_switchdev.c

## Purpose
`br_switchdev.c` integrates the bridge with switchdev hardware offload. It tracks hardware domains, marks frames to avoid duplicate software forwarding, offloads bridge port flags, notifies/replays FDB/VLAN/MDB objects to drivers, and manages offload/unoffload lifecycle for bridge ports.

## Important APIs, types, and functions
- TX forwarding offload helpers: `br_switchdev_frame_uses_tx_fwd_offload()`, `br_switchdev_frame_set_offload_fwd_mark()`, `nbp_switchdev_frame_mark_tx_fwd_offload()`, `nbp_switchdev_frame_mark_tx_fwd_to_hwdom()`, `nbp_switchdev_frame_mark()`, and `nbp_switchdev_allowed_egress()`.
- `br_switchdev_set_port_flag()` pre-validates and applies hardware-offloadable bridge port flags.
- FDB APIs: `br_switchdev_fdb_notify()` and replay helpers populate `switchdev_notifier_fdb_info`.
- VLAN APIs: `br_switchdev_port_vlan_add()`, `br_switchdev_port_vlan_no_foreign_add()`, `br_switchdev_port_vlan_del()`, and replay helpers.
- MDB APIs under multicast snooping: `br_switchdev_mdb_notify()` and replay helpers for host and port MDB objects with completion callbacks.
- Lifecycle APIs: `br_switchdev_port_offload()`, `br_switchdev_port_unoffload()`, and `br_switchdev_port_replay()`.

## Control flow
When a driver offloads a bridge port, `br_switchdev_port_offload()` obtains the physical parent ID, assigns or reuses a hardware domain, optionally enables TX forwarding offload static key, then replays VLAN, MDB, and FDB objects. Failure unwinds the offload accounting. Unoffload replays deletions, processes deferred switchdev work, then decrements offload counters and releases hardware-domain/static-key state.

Data-plane marking records the source hardware domain from ingress ports and tracks destination domains already handled by hardware. Egress is suppressed if the skb was already forwarded to that hardware domain or if an offload forward mark indicates hardware already replicated within the source domain.

FDB notifications skip locked entries and user-added dynamic non-static entries that drivers cannot interpret. VLAN replay walks bridge and port VLAN groups, skips context-only VLANs, and replays MSTI attributes after VLAN adds. MDB replay snapshots objects while holding `multicast_lock`, then calls notifiers outside the lock.

## State and persistence
Switchdev state is per-port `hwdom`, `offload_count`, `ppid`, flags, bridge `busy_hwdoms`, and a static key for TX forwarding offload. Hardware state is external and synchronized by switchdev notifications; software stores only volatile accounting.

## Dependencies and integration points
The file depends on switchdev notifier/object APIs, netdevice parent IDs, bridge FDB/VLAN/MDB/multicast structures, skb bridge control block fields, and rtnetlink locking for replay. It is called by bridge FDB/VLAN/MDB code, bridge port flag setters, and driver offload callbacks.

## Risks and edge cases
Hardware-domain exhaustion returns `-EBUSY`. A single bridge port cannot be offloaded by different physical switch IDs, but repeated offload calls from the same switch are reference-counted. Deferred MDB events can duplicate replay unless `switchdev_port_obj_act_is_deferred()` is checked. Locked FDB entries and unsupported dynamic user entries are intentionally not offloaded. Offload/unoffload ordering must keep hardware and software synchronized.

## Test signals
Test offload/unoffload of simple ports and bond/team ports, mismatched parent IDs, hardware-domain reuse/exhaustion, TX forwarding offload duplicate suppression, port flag rejection, FDB/VLAN/MDB replay on late driver join, multicast offload completion success/failure, and unoffload deletion ordering.
