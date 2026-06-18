# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan.h

## Purpose
Defines the driver-local VLAN value object used by VSI and VF VLAN code.

## Important APIs and Types
`struct ice_vlan` stores TPID, VID, and priority. `ICE_VLAN(tpid, vid, prio)` provides a compound-literal initializer for concise call-site construction.

## Control Flow and State
This header contains no control flow. The struct is passed to filter and VSI context programming functions; callers decide whether it represents a filter, port VLAN, or VLAN zero/untagged behavior.

## Dependencies and Integration Points
Includes Linux types and `ice_type.h`; consumed by `ice_vsi_vlan_lib.h`, VF state, VLAN filter code, and host VF configuration rebuild.

## Risks
No validation is embedded in the type. TPID, VID, and priority constraints are enforced by callers such as `validate_vlan()` and port VLAN setters.

## Test Signals
Validate all call paths reject invalid TPIDs or priorities and correctly handle VID 0 with priority, VLAN 0 filters, 802.1Q, 802.1ad, and QinQ TPIDs.
