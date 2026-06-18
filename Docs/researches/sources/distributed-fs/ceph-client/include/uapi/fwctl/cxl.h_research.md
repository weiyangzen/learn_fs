<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/cxl.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/cxl.h

## Purpose
Defines CXL-specific fwctl RPC payloads for mailbox feature commands. It maps generic `FWCTL_RPC` buffers to CXL mailbox opcode, flags, input payload, and output return-value formats.

## Important APIs, Types, And Functions
`struct fwctl_rpc_cxl` contains a grouped header with `opcode`, `flags`, `op_size`, and reserved zero field, followed by a union of CXL mailbox feature input structs. `struct fwctl_rpc_cxl_out` reports output `size`, device `retval`, and either structured supported-feature data or a flexible byte payload.

## Control Flow
Userspace discovers `FWCTL_DEVICE_TYPE_CXL`, builds a `fwctl_rpc_cxl` request with a supported mailbox opcode, passes it as the `in` buffer to `FWCTL_RPC`, and receives `fwctl_rpc_cxl_out` in the `out` buffer. Kernel delivery errors are represented by ioctl errno; CXL mailbox completion status is carried in `retval`.

## State And Persistence
No state is stored in the header. Persistent effects depend on mailbox opcode, especially Set Feature commands that can modify device feature configuration.

## Dependencies And Integration Points
Depends on `<linux/types.h>`, `<linux/stddef.h>`, and `<cxl/features.h>`. It integrates with the CXL mailbox subsystem, CXL feature descriptors, fwctl scope validation, and CXL management utilities.

## Risks And Edge Cases
Reserved fields must be zero. `op_size` and output `size` must match payload expectations. Feature payload versions, flexible array sizing, and distinguishing ioctl failure from device `retval` are key ABI risks.

## Test Signals
Test with Get Supported Features, Get Feature, and Set Feature payloads; invalid opcode/size rejection; reserved-field validation; short output-buffer handling; and correct propagation of mailbox return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/cxl.h -->
