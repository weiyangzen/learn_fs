# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib.h

## Purpose
Defines the public VF data model and SR-IOV helper API for the `ice` driver. It centralizes VF resource limits, capability/state bits, VF hash-table iteration contracts, `struct ice_vf`, `struct ice_vfs`, `struct ice_vf_ops`, and public helper prototypes or stubs depending on `CONFIG_PCI_IOV`.

## Important APIs and Types
- `ICE_MAX_SRIOV_VFS` caps supported VFs at 256; `ICE_MAX_RSS_QS_PER_VF` caps VF RSS queues at 16.
- `enum ice_virtchnl_cap` currently defines the trusted/privileged VF capability bit.
- `enum ice_vf_states` defines INIT, ACTIVE, QS_ENA, DIS, MC_PROMISC, and UC_PROMISC runtime bits.
- `struct ice_vf` stores identity, PF/VSI links, FDIR state, RSS/hash contexts, virtchnl version/caps, MACs, VLAN state, mailbox state, queue bitmaps, queue bandwidth config, devlink port, LLDP rule IDs, and callback tables.
- `struct ice_vf_ops` abstracts generation-specific reset, mailbox, IRQ-close, and post-rebuild behavior.
- `ice_for_each_vf()` and `ice_for_each_vf_rcu()` document locking expectations for sleeping versus short RCU iterations.
- Inline helpers expose port VLAN ID/priority/TPID, port VLAN enabled check, and LLDP enabled check.

## Control Flow and Conditional Compilation
When `CONFIG_PCI_IOV` is enabled the header exports real VF operations. When disabled, it provides inert stubs returning false, NULL, zero, or `-EOPNOTSUPP` as appropriate. This lets non-SR-IOV driver code compile while avoiding runtime SR-IOV operations.

## State and Persistence
The state layout in `struct ice_vf` defines which data survives reset and which is transient. Host-admin properties such as `trusted`, `spoofchk`, `port_vlan_info`, requested rates, and default MAC live beside transient negotiated properties such as `driver_caps`, allowlisted opcodes, active FDIR rules, and queue-enable bitmaps.

## Dependencies and Integration Points
Includes Linux hash table, bitmap, mutex, PCI, devlink, virtchnl, `ice_type.h`, `ice_flow.h`, `virt/fdir.h`, and `ice_vsi_vlan_ops.h`. This header is consumed broadly by SR-IOV, virtchnl, reset, devlink, VSI, and representor code.

## Risks
- The VF hash table is keyed by `vf_id`, but iteration bucket index is not the VF ID; callers must use `vf->vf_id`.
- `ice_vf_is_port_vlan_ena()` treats either VID or priority as enabling a port VLAN, which is important for priority-tagged port VLAN behavior.
- Stub behavior under `!CONFIG_PCI_IOV` must remain conservative so callers do not accidentally assume VF availability.

## Test Signals
Build with and without `CONFIG_PCI_IOV`; validate VF table lookup/refcount behavior, non-contiguous VF IDs, port VLAN helper semantics for VID 0/prio non-zero, and that all public users tolerate stubs in non-SR-IOV builds.
