# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_wb.h

## Purpose
Declares the writeback hardware wrapper, configuration object, and operation table used by DPU writeback support.

## Important APIs, types, and functions
- `struct dpu_hw_wb_cfg` carries destination layout, interface mode, ROI, and crop rectangles.
- `struct dpu_hw_wb_ops` exposes output address/format, ROI, QoS, CDP, clock force, and pingpong binding callbacks.
- `struct dpu_hw_wb` stores register map, index, catalog caps, and ops.
- `dpu_hw_wb_init()` constructs the wrapper.

## Control flow
The header is declarative. Ops are feature/version gated by the implementation, so callers must check optional callbacks.

## State and persistence
Config data is transient per writeback job. Persistent state is in WB registers after ops run.

## Dependencies and integration points
Includes catalog, MDSS, TOP, utility, and pingpong headers. It connects KMS writeback initialization, encoder/writeback code, and hardware programming.

## Risks
The writeback path combines output memory layout, muxing, QoS, and format packing; mismatched config can corrupt captured buffers. Optional ops require defensive callers across hardware generations.

## Test signals
Build coverage catches signature drift. Runtime signals are successful DRM writeback connector jobs across formats, ROI sizes, and CWB/pingpong routes.
