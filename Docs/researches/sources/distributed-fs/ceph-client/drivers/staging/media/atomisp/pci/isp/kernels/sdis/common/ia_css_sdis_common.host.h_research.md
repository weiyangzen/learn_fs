<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/common/ia_css_sdis_common.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/common/ia_css_sdis_common.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/common/ia_css_sdis_common.host.h` is a host API header for the AtomISP statistics-based digital image stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 93-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `VMEM_ARRAY`; types: `struct sh_css_isp_sdis_hori_proj_tbl` (`margin`); `struct sh_css_isp_sdis_vert_proj_tbl` (`margin`); `struct sh_css_isp_sdis_hori_coef_tbl` (no parsed scalar fields); `struct sh_css_isp_sdis_vert_coef_tbl` (no parsed scalar fields); 1 additional structs; macros/guards: `_IA_CSS_SDIS_COMMON_HOST_H`, `ISP_MAX_SDIS_HOR_PROJ_NUM_ISP`, `ISP_MAX_SDIS_VER_PROJ_NUM_ISP`, `_ISP_SDIS_HOR_COEF_NUM_VECS`, `ISP_MAX_SDIS_HOR_COEF_NUM_VECS`, `ISP_MAX_SDIS_VER_COEF_NUM_VECS`, `__ISP_SDIS_HOR_COEF_NUM_VECS`, `__ISP_SDIS_VER_COEF_NUM_VECS`, `__ISP_SDIS_HOR_PROJ_NUM_ISP`, `__ISP_SDIS_VER_PROJ_NUM_ISP`, `SH_CSS_DIS_VER_NUM_COEF_TYPES`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the statistics-based digital image stabilization kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for statistics-based digital image stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/common/ia_css_sdis_common.host.h -->
