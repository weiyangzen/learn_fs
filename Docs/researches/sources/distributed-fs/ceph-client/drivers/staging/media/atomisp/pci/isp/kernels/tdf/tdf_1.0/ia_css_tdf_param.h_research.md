<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf_param.h` is a ISP parameter ABI header for the AtomISP transform-domain filtering block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 35-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `VMEM_ARRAY`; types: `struct ia_css_isp_tdf_vmem_params` (no parsed scalar fields); `struct ia_css_isp_tdf_dmem_params` (`Epsilon_0`, `Epsilon_1`, `EpsScaleText`, `EpsScaleEdge`, `Sepa_flat`, `Sepa_Edge`, `Blend_Flat`, `Blend_Text`, `Blend_Edge`, `Shading_Gain`, `Shading_baseGain`, `LocalY_Gain`, `LocalY_baseGain`); macros/guards: `__IA_CSS_TDF_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"vmem.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for transform-domain filtering: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf_param.h -->
