<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.h

## Purpose

`enic_pp.h` declares ENIC port-profile helpers and defines the macro that selects the self or VF port-profile entry after validation.

## Important APIs, Types, and Definitions

`ENIC_PP_BY_INDEX(enic, vf, pp, err)` calls `enic_is_valid_pp_vf`; on success it returns `enic->pp` for `PORT_SELF_VF` or `enic->pp + vf` for an SR-IOV VF. The header declares set/get request processing and VF validation functions.

## Control Flow

The macro provides inline selection flow for callers in `enic_main.c` and `enic_pp.c`. Actual provisioning state-machine flow is implemented in `enic_pp.c`.

## State and Persistence Behavior

No state is stored in the header. The macro returns pointers into `enic->pp`, whose contents persist for the device lifetime or until overwritten/cleared by port-profile operations.

## Dependencies and Integration Points

The header depends on `PORT_SELF_VF` and port-profile constants from included ENIC/vNIC headers through users. It integrates netdev VF operations with ENIC provisioning functions.

## Risks and Edge Cases

Because the macro sets `pp = NULL` on validation failure, callers must check `err` before dereferencing. Pointer arithmetic assumes `enic->pp` was allocated with enough entries for enabled VFs.

## Test Signals

Compile all macro users, test self and VF selection, invalid VF indexes, SR-IOV-disabled behavior, and dynamic-vNIC validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.h -->
