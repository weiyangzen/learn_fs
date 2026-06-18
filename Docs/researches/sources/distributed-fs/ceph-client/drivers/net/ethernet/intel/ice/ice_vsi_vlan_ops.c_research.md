# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_ops.c

## Purpose
Initializes generic VSI VLAN operation tables and provides compatibility selection between inner and outer VLAN ops based on cached hardware VLAN mode.

## Important APIs and Functions
- `ice_vsi_init_vlan_ops()` initializes all ops to unsupported, then dispatches to PF, VF, or SF VSI-specific setup based on `vsi->type`.
- `ice_get_compat_vsi_vlan_ops()` returns outer ops in DVM and inner ops in SVM, preserving older code paths that do not explicitly distinguish inner versus outer VLANs.
- Local unsupported op implementations return `-EOPNOTSUPP` for each signature.

## Control Flow
Every VSI starts with safe unsupported callbacks to avoid NULL function pointer crashes. Type-specific setup overlays supported callbacks for PF/VF/SF. Unknown VSI types keep unsupported ops and log debug output.

## State and Persistence
Mutates `vsi->outer_vlan_ops` and `vsi->inner_vlan_ops` function-pointer tables. No hardware state is changed in this file directly.

## Dependencies and Integration Points
Depends on PF, VF, and SF VLAN op headers, generic library, `ice_lib.h`, and `ice.h`. Called during VSI creation/rebuild and used by callers that need mode-compatible VLAN behavior.

## Risks
- Adding a new op to `struct ice_vsi_vlan_ops` requires updating `ops_unsupported`; otherwise uninitialized pointers may appear.
- Compatibility selection hides inner/outer semantics; new code should prefer explicit ops when behavior differs.
- New VSI types need explicit handling or all VLAN operations will fail with `-EOPNOTSUPP`.

## Test Signals
Test PF, VF, SF, and unknown VSI types; SVM versus DVM compatibility selection; and all ops returning `-EOPNOTSUPP` before type-specific initialization.
