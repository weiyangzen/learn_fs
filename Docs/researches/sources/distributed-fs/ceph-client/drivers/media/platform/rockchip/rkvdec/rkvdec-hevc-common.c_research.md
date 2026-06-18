# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-hevc-common.c

## Purpose
This file provides shared HEVC helpers for Rockchip RKVDEC and VDPU HEVC backends. It computes tile dimensions, translates scaling matrices into hardware layout, derives SPS short/long-term reference-picture-set tables, resolves reference buffers, adjusts decoded formats, maps SPS image formats, and snapshots HEVC stateless controls.

## Important APIs, Types, And Functions
- `compute_tiles_uniform()` and `compute_tiles_non_uniform()` derive CTB tile column/row sizes from PPS parameters.
- `rkvdec_hevc_assemble_hw_scaling_list()` updates a hardware `struct scaling_factor` only when the V4L2 scaling matrix differs from the cache.
- `rkvdec_hevc_assemble_hw_rps()` assembles long-term and short-term SPS RPS data for backends that store hardware RPS tables.
- `get_ref_buf()` maps an HEVC DPB index to a capture buffer by timestamp, falling back to the destination buffer if unavailable.
- `rkvdec_hevc_adjust_fmt()`, `rkvdec_hevc_get_image_fmt()`, and `rkvdec_hevc_run_preamble()` provide common format and run setup behavior.

## Control Flow
Scaling-list assembly compares the current matrix to a caller cache, translates matrices through `variant->ops->flatten_matrices()`, writes DC coefficients, and refreshes the cache. RPS assembly optionally reads extended SPS ST/LT controls, derives predicted or explicit short-term sets, writes packed hardware fields, and fills long-term POC/used flags. The run preamble retrieves required HEVC controls plus optional extended RPS controls.

## State And Persistence
This file owns no persistent allocations except temporary ST-RPS calculation memory during RPS preparation. Caches are caller-owned. `get_ref_buf()` is per-run and returns the destination buffer as a safe fallback address.

## Dependencies And Integration Points
The helpers depend on V4L2 stateless HEVC controls, V4L2 mem2mem queues, videobuf2 timestamp lookup, `rkvdec_variant` matrix-flattening callbacks, and shared RKVDEC context state. RPS helpers are used by VDPU381/VDPU383 HEVC paths; the base backend builds per-slice software RPS packets instead.

## Risks
- Temporary ST-RPS allocation is not checked before use.
- ST-RPS cache comparison/copy covers one control element while the control can contain multiple sets, risking stale cached RPS for later elements.
- Scaling-list cache correctness depends on caller initialization and reuse.
- Fallback to the destination buffer can hide missing-reference bugs.
- Tile helpers trust PPS tile counts and arrays from validated controls.

## Test Signals
Use HEVC streams with uniform and non-uniform tiles, scaling-list changes, explicit and predicted short-term RPS, long-term RPS, missing reference timestamps, 8-bit and 10-bit formats, and optional extended SPS RPS controls on VDPU variants.
