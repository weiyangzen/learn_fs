# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_vsi_vlan_ops.c

## Purpose

`ice_sf_vsi_vlan_ops.c` initializes VLAN operation callbacks for subfunction VSIs. It selects the outer VLAN operation table in double VLAN mode and the inner VLAN operation table in single VLAN mode, then installs common add/delete VLAN helpers.

## Important APIs, Types, And Functions

- `ice_sf_vsi_init_vlan_ops()` is the only function. It selects `vsi->outer_vlan_ops` when `ice_is_dvm_ena(&vsi->back->hw)` is true, otherwise `vsi->inner_vlan_ops`.
- The installed callbacks are `ice_vsi_add_vlan` and `ice_vsi_del_vlan`.

## Control Flow

The function is a small initialization branch. Callers pass an SF VSI after its PF/backpointer is available. The function checks VLAN mode through the hardware object and writes the add/delete function pointers into the selected operation table.

## State And Persistence

State is limited to function pointers in `struct ice_vsi_vlan_ops` embedded in the VSI. There is no hardware programming and no persistence beyond the VSI lifetime; later VLAN add/delete requests use the installed callbacks.

## Dependencies And Integration Points

The file depends on `ice_vsi_vlan_ops.h`, `ice_vsi_vlan_lib.h`, `ice_vlan_mode.h`, `ice.h`, and its own header. It integrates with subfunction VSI initialization and common ice VLAN add/delete logic.

## Risks

- Only add/delete callbacks are installed here. If the broader VLAN ops table expects other callbacks for SF VSIs, they must be initialized elsewhere or guarded by callers.
- Correct inner-vs-outer selection depends entirely on `ice_is_dvm_ena()` matching the current hardware VLAN mode before VLAN operations are used.

## Test Signals

Tests should instantiate SF VSI-like objects in DVM and SVM modes and verify the selected operation table and function pointers. Integration tests should add and delete VLANs on an SF netdev in both VLAN modes.
