# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_pf_vsi_vlan_ops.h

## Purpose
`ice_pf_vsi_vlan_ops.h` declares the PF VSI VLAN operation initialization API and forward-declares `struct ice_vsi`.

## Important APIs, Types, and Functions
- Includes `ice_vsi_vlan_ops.h` so the operation-table type is available to callers.
- Forward declaration: `struct ice_vsi`.
- Public function: `ice_pf_vsi_init_vlan_ops(struct ice_vsi *vsi)`.

## Control Flow
The header provides the declaration used by VSI setup code to call the implementation in `ice_pf_vsi_vlan_ops.c`. There is no executable control flow in the header.

## State and Persistence
No state is declared here. The declared function mutates VSI operation pointers at runtime.

## Dependencies and Integration Points
The header is an integration point between PF VSI setup and the VLAN operation implementation. It relies on `ice_vsi_vlan_ops.h` and avoids requiring the full `struct ice_vsi` definition at declaration sites.

## Risks
The header is simple, but include-order issues can arise if callers need the full VSI definition and only include this file. The API name is PF-specific; using it for non-PF VSI types would require checking whether the selected operation table semantics still apply.

## Test Signals
Compile coverage for all callers is the primary signal. Runtime behavior is covered through tests of `ice_pf_vsi_init_vlan_ops()`.
