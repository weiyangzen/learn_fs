<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp_param.h` is a ISP parameter ABI header for the AtomISP defect pixel correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_dp_params` (`threshold_single`, `threshold_2adjacent`, `gain`, `coef_rr_gr`, `coef_rr_gb`, `coef_bb_gb`, `coef_bb_gr`, `coef_gr_rr`, `coef_gr_bb`, `coef_gb_bb`, `coef_gb_rr`); macros/guards: `__IA_CSS_DP_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"bnr/bnr_1.0/ia_css_bnr_param.h"`. The integration point is the AtomISP CSS parameter pipeline for defect pixel correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp_param.h -->
