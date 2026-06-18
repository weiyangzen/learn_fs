# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc.h

## Purpose
Private header for the E5010 JPEG encoder driver. It defines JPEG/header constants, format limits, queue/device/context/buffer structures, chroma order and subsampling enums, and the format descriptor type.

## Important APIs, Types, and Functions
Constants include `MAX_PLANES`, `HEADER_SIZE`, min/max/default dimensions, module name, JPEG markers, Huffman/quantization marker lengths, component/sampling constants, and QP table sizing. Important structures are `struct e5010_q_data`, `struct e5010_dev`, `struct e5010_context`, `struct e5010_buffer`, and `struct e5010_fmt`. Inline `to_e5010_context()` converts a file handle to per-context state.

## Control Flow
No runtime flow beyond the inline container conversion. The constants guide JPEG header writing, QP generation, format negotiation, queue sizing, and hardware programming in the C file.

## State and Persistence
Defines in-memory state. `e5010_q_data` persists queue format, dimensions, sizeimage, bytesperline, sequence, crop, and crop flag. `e5010_context` persists quality and QP tables per open file. `e5010_dev` persists platform-device lifetime hardware and V4L2 state.

## Dependencies and Integration Points
Includes V4L2 controls/device/file-handle headers and is included by both the main driver and hardware-facing code indirectly through shared types.

## Risks
`HEADER_SIZE` must cover the generated marker/header bytes exactly enough for all supported formats. Fixed `MAX_PLANES` of 2 matches semiplanar formats but would need changes for planar formats. The unused `struct e5010_ctrl` appears legacy and may invite drift.

## Test Signals
Compile coverage, format negotiation for all listed formats, JPEG header size validation, QP table generation at quality 1/75/100, and crop/sequence state tests per context.
