<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a_types.h` is a CSS public type header for the AtomISP 3A statistics collection block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 213-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_3a_grid_info` (`ae_enable`, `ae_grd_info`, `awb_enable`, `awb_grd_info`, `af_enable`, `af_grd_info`, `awb_fr_enable`, `awb_fr_grd_info`, `elem_bit_depth`, `enable`, `use_dmem`, `has_histogram`, `width`, `height`, `aligned_width`, `aligned_height`, `bqs_per_grid_cell`, `deci_factor_log2`, and 1 more); `struct ia_css_3a_config` (`ae_y_coef_r`, `ae_y_coef_g`, `ae_y_coef_b`, `awb_lg_high_raw`, `awb_lg_low`, `awb_lg_high`, `af_fir1_coef`, `af_fir2_coef`); `struct ia_css_3a_output` (`ae_y`, `awb_cnt`, `awb_gr`, `awb_r`, `awb_b`, `awb_gb`, `af_hpf1`, `af_hpf2`); `struct ia_css_3a_statistics` (`grid`, `data`, `rgby_data`); 1 additional structs; macros/guards: `__IA_CSS_S3A_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<ia_css_frac.h>`, `"../../../../components/stats_3a/src/stats_3a_public.h"`. The integration point is the AtomISP CSS parameter pipeline for 3A statistics collection: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a_types.h -->
