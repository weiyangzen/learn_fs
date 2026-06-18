<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2_param.h` is a ISP parameter ABI header for the AtomISP Bayer noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 39-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_bnr2_2_params` (`d_var_gain_r`, `d_var_gain_g`, `d_var_gain_b`, `d_var_gain_slope_r`, `d_var_gain_slope_g`, `d_var_gain_slope_b`, `n_var_gain_r`, `n_var_gain_g`, `n_var_gain_b`, `n_var_gain_slope_r`, `n_var_gain_slope_g`, `n_var_gain_slope_b`, `dir_thres`, `dir_thres_w`, `var_offset_coef`, `dir_gain`, `detail_gain`, `detail_gain_divisor`, and 5 more); macros/guards: `__IA_CSS_BNR2_2_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for Bayer noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2_param.h -->
