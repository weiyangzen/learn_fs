<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mst.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mst.c

Purpose: implements bridge Multiple Spanning Tree (MST) support. It allows VLANs to be assigned to MST instances, stores per-port per-MSTI forwarding states through VLAN state, exposes MST state through rtnetlink and exported APIs, gates MST mode changes, and notifies switchdev hardware of MST enablement, VLAN-to-MSTI mappings, and per-port MST states.

Important APIs, types, and functions:

- Mode APIs: `br_mst_enabled()`, `br_mst_set_enabled()`, and `br_mst_uninit()`.
- Query APIs: `br_mst_get_info()` returns VLAN membership for an MSTI and `br_mst_get_state()` returns a port's state for an MSTI.
- State mutation: `br_mst_set_state()` applies an MSTI state to all VLANs on a port whose bridge VLAN maps to that MSTI.
- VLAN mapping: `br_mst_vlan_set_msti()` changes a bridge VLAN's MSTI and synchronizes port VLAN states.
- Initialization and netlink helpers: `br_mst_vlan_init_state()`, `br_mst_info_size()`, `br_mst_fill_info()`, and `br_mst_process()`.
- `DEFINE_STATIC_KEY_FALSE(br_mst_used)` provides a jump-label optimization for MST checks in hot paths.

Core control flow:

- `br_mst_set_enabled()` refuses to toggle MST while any port has VLANs configured, because existing VLAN state would need migration. It sends `SWITCHDEV_ATTR_ID_BRIDGE_MST`, updates the static key, and toggles `BROPT_MST_ENABLED`.
- `br_mst_uninit()` decrements the static key if a bridge is deleted while MST is enabled.
- `br_mst_vlan_init_state()` starts all VLANs in MSTI 0. Bridge VLANs are forwarding; port VLANs inherit the port's current STP state.
- `br_mst_vlan_set_msti()` sends `SWITCHDEV_ATTR_ID_VLAN_MSTI`, updates the bridge VLAN's `msti`, and for each port that has that VID, calls `br_mst_vlan_sync_state()`. Sync inherits an existing state for the same MSTI on that port, or disables the VLAN if this is the first VLAN in that MSTI.
- `br_mst_set_state()` optionally sends `SWITCHDEV_ATTR_ID_PORT_MST_STATE` for nonzero MSTIs, then walks the port VLAN list under RCU and updates each VLAN whose master bridge VLAN maps to the requested MSTI. `br_mst_vlan_set_state()` also updates PVID state when needed.
- `br_mst_process()` parses nested `IFLA_BRIDGE_MST_ENTRY` attributes, requires MST mode enabled, validates MSTI and state ranges, and applies each entry through `br_mst_set_state()`.
- `br_mst_fill_info()` emits one netlink entry per unique MSTI in a VLAN group, reporting MSTI and current state.

State and persistence behavior:

- MST mode is stored as a bridge option bit plus the global static key count. VLAN-to-MSTI mapping is stored in bridge VLAN objects. Per-port MST state is represented by each port VLAN's `state`.
- No separate MST database exists; MST state is derived from VLAN lists and bridge VLAN mappings.
- Switchdev hardware state is updated best-effort; `-EOPNOTSUPP` is accepted for software operation, while other errors abort changes.
- Administrative operations expect RTNL or RCU context as annotated by the functions.

Dependencies and integration points:

- `br_input.c` and `br_forward.c` use MST-aware checks so per-VLAN state can replace classic per-port STP state when MST is enabled.
- VLAN code owns VLAN objects, PVID state, and master/port VLAN relationships used here.
- Switchdev drivers can offload bridge MST enablement, VLAN MSTI mapping, and per-port MSTI state.
- Rtnetlink bridge attributes use `br_mst_process()`, `br_mst_info_size()`, and `br_mst_fill_info()` to configure and report MST.

Risks and edge cases:

- MST mode cannot be toggled with VLANs on ports. Tests must verify this guard because changing mode with live VLANs could leave inconsistent per-VLAN states.
- MSTI 0 is reserved for CST in netlink policy; per-MST switchdev state notifications are skipped for 0 and handled by normal STP state.
- State synchronization when moving a VLAN to a new MSTI intentionally disables it if no peer VLAN on that port has an established state. Misunderstanding this can look like a forwarding regression.
- The static key must be balanced across enable, disable, and bridge deletion. Unbalanced increments would keep MST hot-path code enabled globally.
- Netlink fill emits one entry per unique MSTI by bitmap. Large or sparse MSTI mappings should be checked against skb sizing.

Test signals:

- Enable/disable MST on bridges with and without configured port VLANs and verify extack/error behavior.
- Assign VLANs to MSTIs, query VLAN bitmaps with `br_mst_get_info()`, and verify per-port `br_mst_get_state()`.
- Set MST states through rtnetlink and confirm ingress/egress forwarding follows VLAN state rather than only port state.
- Validate switchdev notifications for bridge MST mode, VLAN MSTI mapping, and nonzero per-port MST state.
- Dump MST netlink info and ensure duplicate MSTIs are emitted once with the expected state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mst.c -->
