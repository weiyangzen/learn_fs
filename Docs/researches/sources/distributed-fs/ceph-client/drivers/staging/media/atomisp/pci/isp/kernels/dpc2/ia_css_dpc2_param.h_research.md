<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2_param.h` is a ISP parameter ABI header for the AtomISP second-generation defect-pixel correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_isp_dpc2_params` (`metric1`, `metric2`, `metric3`, `wb_gain_gr`, `wb_gain_r`, `wb_gain_b`, `wb_gain_gb`); macros/guards: `__IA_CSS_DPC2_PARAM_H`, `NUM_PLANES`, `MAX_FRAME_SIMDWIDTH`, `DPC2_STATE_INPUT_BUFFER_HEIGHT`, `DPC2_STATE_INPUT_BUFFER_WIDTH`, `DPC2_STATE_LOCAL_DEVIATION_BUFFER_HEIGHT`, `DPC2_STATE_LOCAL_DEVIATION_BUFFER_WIDTH`, `DPC2_STATE_SECOND_MINMAX_BUFFER_HEIGHT`, `DPC2_STATE_SECOND_MINMAX_BUFFER_WIDTH`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<linux/math.h>`, `"type_support.h"`, `"vmem.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for second-generation defect-pixel correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2_param.h -->
