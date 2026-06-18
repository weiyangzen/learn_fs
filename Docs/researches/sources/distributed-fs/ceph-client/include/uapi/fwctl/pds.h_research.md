<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/pds.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/pds.h

## Purpose
Defines AMD/Pensando PDS-specific fwctl information and RPC envelope. It exposes capability bits for query/send support and a structured payload-pointer request/response format.

## Important APIs, Types, And Functions
`struct fwctl_info_pds` reports `uctx_caps`. `enum pds_fwctl_capabilities` defines query and send capability indexes. `struct fwctl_rpc_pds` has nested `in` and `out` structs with operation, endpoint, length, payload pointer, return value, and reserved fields.

## Control Flow
Userspace discovers `FWCTL_DEVICE_TYPE_PDS`, checks `uctx_caps`, fills `fwctl_rpc_pds.in` with operation, endpoint, and payload buffer, and passes the struct through generic `FWCTL_RPC`; the driver writes result metadata and output payload through `out`.

## State And Persistence
State is held in the fwctl fd and PDS firmware. RPC payloads may query or mutate firmware/device state depending on operation and capability.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and generic fwctl. Integrates with PDS firmware endpoints, capability-gated command dispatch, and vendor management tooling.

## Risks And Edge Cases
Reserved fields must remain zero. `len`/payload pointer mismatches, endpoint misuse, and conflating `out.retval` with ioctl errno are likely bugs. Capability bits are indexes, so tooling must treat them as bitmap positions.

## Test Signals
Test query/send capability reporting, rejected reserved fields, bad pointer/length handling, endpoint validation, and output `retval`/payload updates for successful firmware delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/pds.h -->
