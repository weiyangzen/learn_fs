# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/allowlist.c

## Purpose
Maintains per-VF virtchnl opcode allowlists. It starts VFs with only minimal default opcodes, enables working opcodes after resources are allocated, and enables feature-specific opcodes based on negotiated VF driver capabilities.

## Important APIs and Functions
- `ice_vc_is_opcode_allowed()` checks an opcode bit in `vf->opcodes_allowlist`.
- `ice_vc_set_default_allowlist()` clears all bits and allows GET_VF_RESOURCES, VERSION, and RESET_VF.
- `ice_vc_set_working_allowlist()` adds operational queue/stats/event opcodes.
- `ice_vc_set_caps_allowlist()` iterates negotiated capability bits and adds corresponding opcode groups.
- Static opcode arrays map L2, requested queues, legacy VLAN, VLAN v2, RSS, flex descriptors, advanced RSS, FDIR, PTP, and QoS capabilities to virtchnl opcodes.

## Control Flow
Capability-to-opcode mapping uses `BIT_INDEX(caps) (HWEIGHT((caps) - 1))`, relying on capability constants being single-bit masks. Setting caps allowlist walks set bits in `vf->driver_caps` up to the mapping table size and applies each opcode list.

## State and Persistence
The mutable state is `vf->opcodes_allowlist`, a bitmap of `VIRTCHNL_OP_MAX` bits. It is reset to default on VF initialization and reset; working and caps allowlists are added during virtchnl negotiation.

## Dependencies and Integration Points
Depends on `allowlist.h`, `ice.h`, virtchnl constants, and VF `driver_caps`. Used by virtchnl message dispatch to reject opcodes outside the VF's current state/capability set.

## Risks
- The `BIT_INDEX` mapping assumes capability values are powers of two; non-bitmask capability definitions would index incorrectly.
- New virtchnl capabilities or opcodes require updating these arrays or VFs may be denied valid messages.
- Default and reset behavior must clear old negotiated opcodes to prevent privilege carryover after reset.

## Test Signals
Test opcode rejection before resource negotiation, working opcode enable after GET_VF_RESOURCES, feature-specific enable for every listed capability, reset returning to default-only, invalid opcode >= `VIRTCHNL_OP_MAX`, and additions for new virtchnl capabilities.
