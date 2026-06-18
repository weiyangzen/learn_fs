<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/common/ia_css_sdis_common_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/common/ia_css_sdis_common_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/common/ia_css_sdis_common_types.h` is a CSS public type header for the AtomISP statistics-based digital image stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 211-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_dvs_grid_dim` (`width`, `height`); `struct ia_css_sdis_info` (`dim`, `pad`, `proj`, `deci_factor_log2`); `struct ia_css_dvs_grid_res` (`width`, `aligned_width`, `height`, `aligned_height`); `struct ia_css_dvs_grid_info` (`enable`, `width`, `aligned_width`, `height`, `aligned_height`, `bqs_per_grid_cell`, `num_hor_coefs`, `num_ver_coefs`); 7 additional structs; macros/guards: `__IA_CSS_SDIS_COMMON_TYPES_H`, `IA_CSS_DVS_STAT_NUM_OF_LEVELS`, `DEFAULT_DVS_GRID_INFO`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<type_support.h>`. The integration point is the AtomISP CSS parameter pipeline for statistics-based digital image stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/common/ia_css_sdis_common_types.h -->
