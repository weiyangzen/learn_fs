# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_idc_int.h

## Purpose
Defines the internal event-forwarding interface from `ice` to the RDMA auxiliary driver.

## Important APIs, types, and functions
- Includes `linux/net/intel/iidc_rdma.h` and `iidc_rdma_ice.h` for event and device types.
- Forward declares `struct ice_pf`.
- Declares `ice_send_event_to_aux(struct ice_pf *pf, struct iidc_rdma_event *event)`.

## Control flow
No executable flow. It exposes one internal call used by other `ice` modules when they need to notify the RDMA auxiliary driver.

## State and persistence behavior
No state is stored here. State is handled by `pf->cdev_info` and auxiliary-device lifecycle code in `ice_idc.c`.

## Dependencies and integration points
Ties the LAN driver to the Intel IIDC RDMA interface without exposing the full implementation. This keeps event senders independent of auxiliary bus details.

## Risks
Any event ABI changes in IIDC headers can affect all senders. Callers must respect the implementation requirement that events be sent from task context.

## Test signals
Build coverage for IIDC header compatibility and runtime RDMA event delivery during link/reset/VSI state changes.
