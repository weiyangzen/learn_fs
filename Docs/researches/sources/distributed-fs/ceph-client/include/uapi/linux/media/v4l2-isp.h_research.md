# sources/distributed-fs/ceph-client/include/uapi/linux/media/v4l2-isp.h

## Purpose
Defines a generic V4L2 ISP extensible parameters buffer ABI: versioned top-level parameter buffers containing a packed sequence of driver-specific parameter blocks with a common header.

## Important APIs, Types, And Functions
Exports `v4l2_isp_params_version`, block flags `V4L2_ISP_PARAMS_FL_BLOCK_DISABLE` and `V4L2_ISP_PARAMS_FL_BLOCK_ENABLE`, macro `V4L2_ISP_PARAMS_FL_DRIVER_FLAGS(n)`, `v4l2_isp_params_block_header`, and `v4l2_isp_params_buffer`.

## Control Flow
Userspace sets the buffer version, appends block-specific records back-to-back in `data[]`, and sets `data_size`. Drivers walk the byte stream by reading each aligned block header, validating `size`, checking enable/disable flags, and dispatching by driver-specific `type`.

## State, Persistence, And Dependencies
No persistent state is owned by the header. It defines a userspace-to-driver serialization format. Dependencies are `linux/stddef.h` and `linux/types.h`.

## Integration Points
Shared by ISP drivers that support V4L2 controls or buffers carrying algorithm parameters. Driver-specific headers define block type IDs and payload structs that embed `v4l2_isp_params_block_header` first.

## Risks
Malformed `data_size` or block `size` can desynchronize parsing. Version V0 and V1 are intentionally identical, which must be preserved for compatibility. Alignment and flexible array handling are ABI-sensitive.

## Test Signals
Exercise zero-block buffers, unknown versions, short block headers, oversized and undersized block `size`, enable/disable flag combinations, driver flag bit positions, and exact 8-byte header alignment.
