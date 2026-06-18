# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-isp.c

## Purpose
`v4l2-isp.c` provides generic validation helpers for V4L2 ISP parameter buffers. It checks the videobuf2 payload size, the `v4l2_isp_params_buffer` header, format version, total data size, and the sequence of typed ISP parameter blocks supplied to drivers.

## Important APIs, Types, and Functions
The exported APIs are `v4l2_isp_params_validate_buffer_size` and `v4l2_isp_params_validate_buffer`. Important types are `struct vb2_buffer`, `struct v4l2_isp_params_buffer`, `struct v4l2_isp_params_block_header`, and `struct v4l2_isp_params_block_type_info`.

## Control Flow
`v4l2_isp_params_validate_buffer_size` obtains plane 0 payload size, rejects payloads larger than a driver-supplied maximum destination size, rejects payloads smaller than the ISP parameter buffer header, and otherwise succeeds.

`v4l2_isp_params_validate_buffer` accepts only format versions `V4L2_ISP_PARAMS_VERSION_V0` and `V4L2_ISP_PARAMS_VERSION_V1`, allowing existing drivers that used either zero or one as their first supported version. It checks that `header_size + buffer->data_size` equals the vb2 payload size. It then walks the variable-length block data while enough bytes remain for a block header. For each block it validates that the type index is in range, the block does not exceed remaining data, ENABLE and DISABLE flags are not both set, and the block size matches the driver-provided type info. A disabled block may contain only the header. Any trailing bytes that cannot form a block header cause failure.

## State and Persistence Behavior
The helpers do not mutate buffer contents or persistent state. They read vb2 payload size and caller-provided metadata, emit `dev_dbg` diagnostics, and return success or `-EINVAL`.

## Dependencies and Integration Points
The file depends on `media/v4l2-isp.h`, `videobuf2-core`, and device debug logging. ISP/statistics drivers can call these helpers before consuming userspace parameter buffers from metadata queues.

## Risks
The main risks are malformed user buffers: integer size mismatches, block sizes that skip over data, invalid type indexes, unsupported versions, contradictory flags, and partial trailing data. Callers must still ensure that the memory pointed to by `buffer` corresponds to the validated vb2 payload and remains accessible. Type-info tables must match driver ABI definitions.

## Test Signals
Test payload too large, payload smaller than header, unsupported version, header data size mismatch, valid empty data area, valid multiple blocks, invalid block type, block size beyond remaining data, enable+disable flags together, disabled header-only blocks, incorrect block sizes, and trailing bytes after the final block.
