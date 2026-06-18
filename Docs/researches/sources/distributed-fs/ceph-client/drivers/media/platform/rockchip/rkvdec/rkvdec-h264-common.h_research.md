# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264-common.h

## Purpose
This header defines the shared H.264 hardware-facing data structures and helper prototypes for Rockchip RKVDEC H.264 backends.

## Important APIs, Types, And Data
- `struct rkvdec_h264_scaling_list` mirrors the hardware 4x4/8x8 scaling-list blob.
- `struct rkvdec_h264_reflists` stores V4L2 P, B0, and B1 reference lists.
- `struct rkvdec_h264_run` extends `struct rkvdec_run` with current H.264 decode controls and resolved DPB buffers.
- `struct rkvdec_rps_entry` and `struct rkvdec_rps` define packed hardware RPS memory.
- Prototypes export reference lookup, RPS assembly, scaling-list assembly, format adjustment, image-format detection, SPS validation, and run preamble.

## Control Flow
Backends allocate a private table containing these structures, call the helpers during each `run()`, then program register addresses pointing to the filled table.

## State And Persistence
`rkvdec_h264_run` is per decode invocation. `rkvdec_rps` and `rkvdec_h264_scaling_list` usually live inside a coherent per-context private table until stop.

## Dependencies And Integration Points
The header includes V4L2 H.264 and mem2mem headers plus `rkvdec.h`. It is part of the ABI between common H.264 logic and hardware-specific RKVDEC/VDPU backends.

## Risks
- Packed bitfield layout is compiler- and ABI-sensitive within the kernel build environment.
- Changing padding or field widths changes hardware memory layout.
- `struct rkvdec_h264_run` carries raw V4L2 control pointers; users must populate it with `rkvdec_h264_run_preamble()` before helper use.

## Test Signals
Compile-time users catch prototype drift. Runtime signals include correct RPS behavior for P/B slices, field pictures, and long-term references across all H.264 backend variants.
