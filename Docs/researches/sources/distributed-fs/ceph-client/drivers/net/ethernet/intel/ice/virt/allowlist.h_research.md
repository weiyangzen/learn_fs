# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/allowlist.h

## Purpose
Declares the VF virtchnl opcode allowlist API.

## Important APIs
Exports `ice_vc_is_opcode_allowed()`, `ice_vc_set_default_allowlist()`, `ice_vc_set_working_allowlist()`, and `ice_vc_set_caps_allowlist()`.

## Control Flow and State
The header has no control flow; functions operate on `struct ice_vf` and its `opcodes_allowlist` bitmap.

## Dependencies and Integration Points
Includes `ice.h` to expose `struct ice_vf`; used by VF lifecycle/reset and virtchnl dispatch code.

## Risks
Including `ice.h` from this small header increases dependency breadth, but keeps callers simple. API users must call the setters in the correct negotiation/reset order.

## Test Signals
Compile all virtchnl users and verify dispatch calls `ice_vc_is_opcode_allowed()` before handling capability-scoped operations.
