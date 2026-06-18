# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-h264-common.c

## Purpose
This file contains H.264 helpers shared by the base RKVDEC backend and VDPU-specific H.264 backends. It translates V4L2 stateless H.264 controls into hardware reference-picture-set data, scaling-list data, decoded format metadata, SPS validation, and per-run control pointers.

## Important APIs, Types, And Functions
- `lookup_ref_buf_idx()` resolves active DPB `reference_ts` values to capture-queue `vb2_buffer` objects and stores them in `run->ref_buf[]`.
- `assemble_hw_rps()` builds the packed H.264 RPS structure consumed by hardware from V4L2 reference lists and resolved DPB buffers.
- `assemble_hw_scaling_list()` copies V4L2 4x4 and 8x8 scaling matrices into the hardware private table when present.
- `rkvdec_h264_adjust_fmt()`, `rkvdec_h264_get_image_fmt()`, `rkvdec_h264_validate_sps()`, and `rkvdec_h264_run_preamble()` provide format, validation, and per-run setup.

## Control Flow
The normal per-frame H.264 path snapshots controls, builds V4L2 P/B reference lists, copies scaling data, resolves DPB buffers, and packs RPS entries. `set_dpb_info()` places one reference-list entry into the correct packed slot for three reference lists.

## State And Persistence
The helpers fill caller-owned per-run or per-context structures. `run->ref_buf[]` is rebuilt every decode from current DPB timestamps. Scaling-list and RPS outputs persist only in the backend's coherent private table until overwritten or freed during codec stop.

## Dependencies And Integration Points
The file depends on V4L2 stateless H.264 controls, `v4l2_h264_reflist_builder`, V4L2 mem2mem queues, videobuf2 buffer lookup, and `rkvdec.h`. It is used by `rkvdec-h264.c`, `rkvdec-vdpu381-h264.c`, and `rkvdec-vdpu383-h264.c`.

## Risks
- Missing reference buffers are tolerated and encoded as invalid DPB entries, but bad timestamps can still cause prediction corruption.
- `assemble_hw_scaling_list()` leaves previous scaling data untouched when the PPS scaling flag is absent; hardware should ignore it.
- RPS packing relies on V4L2 reference indices staying within DPB bounds; `WARN_ON()` catches out-of-range references but continues.
- SPS validation allows H.264 4:2:2, so downstream backends must agree on support.

## Test Signals
Exercise H.264 I/P/B decode, field references, inactive DPB slots, long-term references, scaling matrices, 8-bit and 10-bit streams, 4:2:0 and 4:2:2 streams, and coded-size rejection.
