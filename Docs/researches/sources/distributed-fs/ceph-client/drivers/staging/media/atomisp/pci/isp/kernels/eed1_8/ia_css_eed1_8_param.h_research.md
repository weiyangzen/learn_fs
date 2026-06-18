<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8_param.h` is a ISP parameter ABI header for the AtomISP edge enhancement and denoise block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 147-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `VMEM_ARRAY`, `SVMEM_ARRAY`; types: `struct eed1_8_vmem_params` (no parsed scalar fields); `struct eed1_8_dmem_params` (`rbzp_strength`, `fcstrength`, `fcthres_0`, `fc_sat_coef`, `fc_coring_prm`, `fc_slope`, `aerel_thres0`, `aerel_gain0`, `aerel_thres_diff`, `aerel_gain_diff`, `derel_thres0`, `derel_gain0`, `derel_thres_diff`, `derel_gain_diff`, `coring_pos0`, `coring_pos_diff`, `coring_neg0`, `coring_neg_diff`, and 11 more); macros/guards: `__IA_CSS_EED1_8_PARAM_H`, `EED1_8_FC_ENABLE_MEDIAN`, `EED1_8_CORINGTHMIN`, `NUM_PLANES`, `EED1_8_STATE_INPUT_BUFFER_HEIGHT`, `EED1_8_STATE_INPUT_BUFFER_WIDTH`, `EED1_8_STATE_LD_H_HEIGHT`, `EED1_8_STATE_LD_H_WIDTH`, `EED1_8_STATE_LD_V_HEIGHT`, `EED1_8_STATE_LD_V_WIDTH`, `EED1_8_STATE_D_HR_HEIGHT`, `EED1_8_STATE_D_HR_WIDTH`, `EED1_8_STATE_D_HB_HEIGHT`, `EED1_8_STATE_D_HB_WIDTH`, `EED1_8_STATE_D_VR_HEIGHT`, `EED1_8_STATE_D_VR_WIDTH`, and 12 more. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<linux/math.h>`, `"type_support.h"`, `"vmem.h"`, `"ia_css_eed1_8_types.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for edge enhancement and denoise: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8_param.h -->
