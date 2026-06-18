<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob_param.h` is a ISP parameter ABI header for the AtomISP optical black correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 39-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `VMEM_ARRAY`; types: `struct sh_css_isp_ob_stream_config` (`isp_pipe_version`, `raw_bit_depth`); `struct sh_css_isp_ob_params` (`blacklevel_gr`, `blacklevel_r`, `blacklevel_b`, `blacklevel_gb`, `area_start_bq`, `area_length_bq`, `area_length_bq_inverse`); `struct sh_css_isp_ob_vmem_params` (no parsed scalar fields); macros/guards: `__IA_CSS_OB_PARAM_H`, `OBAREA_MASK_SIZE`, `OBAREA_LENGTHBQ_INVERSE_SHIFT`, `AREA_LENGTH_UNIT`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"vmem.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for optical black correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob_param.h -->
