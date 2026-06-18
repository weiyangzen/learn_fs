# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_util.h

## Purpose
Declares common DPU register-map structures, scaler/detail-enhancer configuration, DRM-facing scaler structures, QoS config, CSC constants, and shared hardware utility APIs.

## Important APIs, types, and functions
- Macros include `REG_MASK`, MISR control bits, `TO_S15D16`, and `CALCULATE_WD_LOAD_VALUE`.
- `struct dpu_hw_blk_reg_map` carries block MMIO base and log mask.
- `struct dpu_hw_scaler3_de_cfg`, `dpu_hw_scaler3_cfg`, `dpu_drm_pix_ext_v1`, `dpu_drm_de_v1`, and `dpu_drm_scaler_v2` describe scaler inputs.
- `struct dpu_hw_qos_cfg` carries danger/safe/CREQ LUTs and danger/safe enable.
- Declares register I/O macros, scaler, CSC, CDP, QoS, MISR, and clock-force helpers.

## Control flow
The header is mostly declarative. `DPU_REG_WRITE` and `DPU_REG_READ` macros feed register names and offsets into implementation wrappers.

## State and persistence
It defines the register-map handle embedded in hardware wrappers and config structures passed by value or pointer during atomic programming. Persistent hardware effects occur in implementation functions.

## Dependencies and integration points
Includes Linux MMIO/slab headers, MDSS common definitions, and DPU catalog. It is one of the central include files for all DPU hardware block wrappers.

## Risks
The utility structs encode hardware register field assumptions such as max planes, LUT sizes, and watchdog clock math. Mismatched scaler or QoS config can corrupt register programming across multiple blocks.

## Test signals
Build coverage across all DPU blocks is the main static signal. Runtime coverage comes from scaling, CSC, QoS, MISR, CDP, and debug logging features that depend on these declarations.
