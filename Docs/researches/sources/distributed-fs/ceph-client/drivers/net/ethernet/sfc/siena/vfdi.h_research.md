<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/vfdi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/vfdi.h

## Purpose
Defines the Virtual Function Driver Interface ABI used for Siena PF/VF communication over user events and DMA request/status pages.

## Important APIs, Types, And Functions
- Event field layout constants: `VFDI_EV_SEQ`, `VFDI_EV_TYPE`, `VFDI_EV_DATA`, request word types, status, and reset event types.
- Endpoint and status structures: `struct vfdi_endpoint` and `struct vfdi_status`.
- Request ABI: `enum vfdi_op`, response codes, and `struct vfdi_req` with operation-specific flexible-array payloads.
- Queue/filter flags: RX scatter, TX checksum-disable flags, MAC filter RSS/scatter flags.

## Control Flow
The VF sends a page-aligned request address as four ordered user events. The PF DMAs `struct vfdi_req` from that address, executes the requested operation, writes `rc` and `VFDI_OP_RESPONSE` back, and can asynchronously DMA `struct vfdi_status` then send status or reset events to EVQ0.

## State And Persistence Behavior
The file defines guest-visible memory layouts, so fields are part of an ABI rather than private state. `vfdi_status` uses `generation_start` and `generation_end` to let the VF detect torn DMA updates. Version and length fields allow compatible extension.

## Dependencies And Integration Points
Consumed by `siena_sriov.c` PF logic and the corresponding VF driver. Depends on kernel Ethernet/VLAN types through included driver headers. The ABI maps directly onto Siena hardware user-event mailbox semantics.

## Risks And Test Signals
Structure layout changes can break guest drivers. Flexible arrays require page-size bounds validation in PF code. Test signals include VF queue initialization, filter insertion, status page updates with matching generation values, peer-list extension pages, and reset event reception after PF/VF reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/vfdi.h -->
