# subset-b-005405 Research

Grouped source research for AtomISP ISP kernel host adapters, public CSS type contracts, ISP parameter ABI structures, state headers, and binary configuration hooks. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.h` is a host API header for the AtomISP Bayer noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_bnr2_2_encode`, `ia_css_bnr2_2_debug_dtrace`; macros/guards: `__IA_CSS_BNR2_2_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the Bayer noise reduction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_bnr2_2_types.h"`, `"ia_css_bnr2_2_param.h"`. The integration point is the AtomISP CSS parameter pipeline for Bayer noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2_types.h` is a CSS public type header for the AtomISP Bayer noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 63-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_bnr2_2_config` (`d_var_gain_r`, `d_var_gain_g`, `d_var_gain_b`, `d_var_gain_slope_r`, `d_var_gain_slope_g`, `d_var_gain_slope_b`, `n_var_gain_r`, `n_var_gain_g`, `n_var_gain_b`, `n_var_gain_slope_r`, `n_var_gain_slope_g`, `n_var_gain_slope_b`, `dir_thres`, `dir_thres_w`, `var_offset_coef`, `dir_gain`, `detail_gain`, `detail_gain_divisor`, and 5 more); macros/guards: `__IA_CSS_BNR2_2_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for Bayer noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr.host.c` is a host implementation for the AtomISP Bayer noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 57-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_bnr_encode`, `ia_css_bnr_dump`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the Bayer noise reduction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"sh_css_frac.h"`, `"ia_css_bnr.host.h"`. Important integration signals: debug tracing, fixed-point fitting helpers. The integration point is the AtomISP CSS parameter pipeline for Bayer noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; fixed-point fitting and bit-depth shifts must match firmware expectations or image quality changes silently.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr.host.h` is a host API header for the AtomISP Bayer noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_bnr_encode`, `ia_css_bnr_dump`; macros/guards: `__IA_CSS_BNR_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the Bayer noise reduction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"sh_css_params.h"`, `"ynr/ynr_1.0/ia_css_ynr_types.h"`, `"ia_css_bnr_param.h"`. The integration point is the AtomISP CSS parameter pipeline for Bayer noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr_param.h` is a ISP parameter ABI header for the AtomISP Bayer noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_bnr_params` (`gain_all`, `gain_dir`, `threshold_low`, `threshold_width_log2`, `threshold_width`, `clip`); macros/guards: `__IA_CSS_BNR_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr_1.0/ia_css_bnr_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr.host.c` is a host implementation for the AtomISP chroma noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 20-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_init_cnr_state`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. state initialization helpers zero or seed ISP state buffers before firmware execution. The path is specific to the chroma noise reduction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. state buffers are caller-owned and persist only for the lifetime of the ISP binary/frame context. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"ia_css_cnr.host.h"`. Important integration signals: debug tracing, vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for chroma noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr.host.h` is a host API header for the AtomISP chroma noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 17-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_init_cnr_state`; macros/guards: `__IA_CSS_CNR_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the chroma noise reduction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_cnr_param.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for chroma noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr_param.h` is a ISP parameter ABI header for the AtomISP chroma noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 16-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_CNR_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"../../ynr/ynr_1.0/ia_css_ynr_param.h"`. The integration point is the AtomISP CSS parameter pipeline for chroma noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_1.0/ia_css_cnr_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2.host.c` is a host implementation for the AtomISP chroma noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 65-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_cnr_encode`, `ia_css_cnr_debug_dtrace`, `ia_css_init_cnr2_state`; default/static data: `default_cnr_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures state initialization helpers zero or seed ISP state buffers before firmware execution debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the chroma noise reduction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data; state buffers are caller-owned and persist only for the lifetime of the ISP binary/frame context. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"ia_css_cnr2.host.h"`. Important integration signals: debug tracing, vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for chroma noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2.host.h` is a host API header for the AtomISP chroma noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 35-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_cnr_encode`, `ia_css_cnr_dump`, `ia_css_cnr_debug_dtrace`, `ia_css_init_cnr2_state`; macros/guards: `__IA_CSS_CNR2_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the chroma noise reduction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_cnr2_types.h"`, `"ia_css_cnr2_param.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for chroma noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2_param.h` is a ISP parameter ABI header for the AtomISP chroma noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 24-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_cnr_params` (`coring_u`, `coring_v`, `sense_gain_vy`, `sense_gain_vu`, `sense_gain_vv`, `sense_gain_hy`, `sense_gain_hu`, `sense_gain_hv`); macros/guards: `__IA_CSS_CNR2_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for chroma noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2_types.h` is a CSS public type header for the AtomISP chroma noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 46-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_cnr_config` (`coring_u`, `coring_v`, `sense_gain_vy`, `sense_gain_vu`, `sense_gain_vv`, `sense_gain_hy`, `sense_gain_hu`, `sense_gain_hv`); macros/guards: `__IA_CSS_CNR2_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for chroma noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/cnr/cnr_2/ia_css_cnr2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion.host.c` is a host implementation for the AtomISP Bayer quad conversion/deinterleave block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_conversion_encode`; default/static data: `default_conversion_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures. The path is specific to the Bayer quad conversion/deinterleave kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"ia_css_conversion.host.h"`. The integration point is the AtomISP CSS parameter pipeline for Bayer quad conversion/deinterleave: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion.host.h` is a host API header for the AtomISP Bayer quad conversion/deinterleave block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 21-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_conversion_encode`; macros/guards: `__IA_CSS_CONVERSION_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the Bayer quad conversion/deinterleave kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_conversion_types.h"`, `"ia_css_conversion_param.h"`. The integration point is the AtomISP CSS parameter pipeline for Bayer quad conversion/deinterleave: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion_param.h` is a ISP parameter ABI header for the AtomISP Bayer quad conversion/deinterleave block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 20-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_conversion_params` (`en`, `dummy0`, `dummy1`, `dummy2`); macros/guards: `__IA_CSS_CONVERSION_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for Bayer quad conversion/deinterleave: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion_types.h` is a CSS public type header for the AtomISP Bayer quad conversion/deinterleave block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 24-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_conversion_config` (`en`, `dummy0`, `dummy1`, `dummy2`); macros/guards: `__IA_CSS_CONVERSION_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for Bayer quad conversion/deinterleave: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/conversion/conversion_1.0/ia_css_conversion_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output.host.c` is a host implementation for the AtomISP copy-output routing block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_copy_output_config`, `ia_css_copy_output_configure`; default/static data: `default_config`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary. The path is specific to the copy-output routing kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_copy_output.host.h"`, `"ia_css_binary.h"`, `"type_support.h"`, `"ia_css_isp_configs.h"`, `"isp.h"`. Important integration signals: binary-specific configuration dispatch, generated per-kernel configuration hooks. The integration point is the AtomISP CSS parameter pipeline for copy-output routing: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output.host.h` is a host API header for the AtomISP copy-output routing block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 24-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_copy_output_config`, `ia_css_copy_output_configure`; macros/guards: `__IA_CSS_COPY_OUTPUT_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the copy-output routing kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"ia_css_binary.h"`, `"ia_css_copy_output_param.h"`. Important integration signals: binary-specific configuration dispatch. The integration point is the AtomISP CSS parameter pipeline for copy-output routing: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output_param.h` is a ISP parameter ABI header for the AtomISP copy-output routing block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_copy_output_configuration` (`enable`); `struct sh_css_isp_copy_output_isp_config` (`enable`); macros/guards: `__IA_CSS_COPY_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for copy-output routing: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/copy_output/copy_output_1.0/ia_css_copy_output_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop.host.c` is a host implementation for the AtomISP image crop and DMA port sizing block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 58-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_crop_encode`, `ia_css_crop_config`, `ia_css_crop_configure`; default/static data: `default_config`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary. The path is specific to the image crop and DMA port sizing kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<assert_support.h>`, `<ia_css_frame_public.h>`, `<ia_css_frame.h>`, `<ia_css_binary.h>`, `"ia_css_isp_configs.h"`, `"isp.h"`, `"ia_css_crop.host.h"`. Important integration signals: binary-specific configuration dispatch, generated per-kernel configuration hooks, frame geometry and DMA addressing, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for image crop and DMA port sizing: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; DMA port configuration assumes vector-width divisibility and returns `-EINVAL` otherwise.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop.host.h` is a host API header for the AtomISP image crop and DMA port sizing block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_crop_encode`, `ia_css_crop_config`, `ia_css_crop_configure`; macros/guards: `__IA_CSS_CROP_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the image crop and DMA port sizing kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<ia_css_frame_public.h>`, `<ia_css_binary.h>`, `"ia_css_crop_types.h"`, `"ia_css_crop_param.h"`. Important integration signals: binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for image crop and DMA port sizing: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop_param.h` is a ISP parameter ABI header for the AtomISP image crop and DMA port sizing block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 24-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_crop_isp_config` (`width_a_over_b`, `port_b`); `struct sh_css_isp_crop_isp_params` (`crop_pos`); macros/guards: `__IA_CSS_CROP_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<type_support.h>`, `"dma.h"`, `"sh_css_internal.h"`. The integration point is the AtomISP CSS parameter pipeline for image crop and DMA port sizing: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop_types.h` is a CSS public type header for the AtomISP image crop and DMA port sizing block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_crop_config` (`crop_pos`); `struct ia_css_crop_configuration` (`info`); macros/guards: `__IA_CSS_CROP_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<ia_css_frame_public.h>`, `"sh_css_uds.h"`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for image crop and DMA port sizing: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/crop/crop_1.0/ia_css_crop_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc.host.c` is a host implementation for the AtomISP color-space conversion block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 119-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_encode_cc`, `ia_css_csc_encode`, `ia_css_cc_dump`, `ia_css_csc_dump`, `ia_css_cc_config_debug_dtrace`; default/static data: `default_cc_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the color-space conversion kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"ia_css_csc.host.h"`. Important integration signals: debug tracing. The integration point is the AtomISP CSS parameter pipeline for color-space conversion: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc.host.h` is a host API header for the AtomISP color-space conversion block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 46-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_encode_cc`, `ia_css_csc_encode`, `ia_css_cc_dump`, `ia_css_csc_dump`, `ia_css_cc_config_debug_dtrace`; macros/guards: `__IA_CSS_CSC_HOST_H`, `ia_css_csc_debug_dtrace`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the color-space conversion kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_csc_types.h"`, `"ia_css_csc_param.h"`. The integration point is the AtomISP CSS parameter pipeline for color-space conversion: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc_param.h` is a ISP parameter ABI header for the AtomISP color-space conversion block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_csc_params` (`m_shift`, `m00`, `m01`, `m02`, `m10`, `m11`, `m12`, `m20`, `m21`, `m22`); macros/guards: `__IA_CSS_CSC_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for color-space conversion: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc_types.h` is a CSS public type header for the AtomISP color-space conversion block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 70-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_cc_config` (`fraction_bits`); macros/guards: `__IA_CSS_CSC_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for color-space conversion: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/csc/csc_1.0/ia_css_csc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5.host.c` is a host implementation for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 113-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ctc_gradient`, `ia_css_ctc_encode`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures. The path is specific to the chroma tone/control correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"assert_support.h"`, `"ctc/ctc_1.0/ia_css_ctc.host.h"`, `"ia_css_ctc1_5.host.h"`. Important integration signals: debug tracing, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5.host.h` is a host API header for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ctc_encode`, `ia_css_ctc_dump`; macros/guards: `__IA_CSS_CTC1_5_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the chroma tone/control correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"sh_css_params.h"`, `"ia_css_ctc1_5_param.h"`. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5_param.h` is a ISP parameter ABI header for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 38-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_ctc_params` (`y0`, `y1`, `y2`, `y3`, `y4`, `y5`, `ce_gain_exp`, `x1`, `x2`, `x3`, `x4`, `dydx0`, `dydx0_shift`, `dydx1`, `dydx1_shift`, `dydx2`, `dydx2_shift`, `dydx3`, and 3 more); macros/guards: `__IA_CSS_CTC1_5_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"ctc/ctc_1.0/ia_css_ctc_param.h"`. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc1_5/ia_css_ctc1_5_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2.host.c` is a host implementation for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 149-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ctc2_slope`, `ia_css_ctc2_vmem_encode`, `ia_css_ctc2_encode`; default/static data: `default_ctc2_config`; macros/guards: `INEFFECTIVE_VAL`, `BASIC_VAL`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures. The path is specific to the chroma tone/control correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"assert_support.h"`, `"ia_css_ctc2.host.h"`. Important integration signals: vector-memory array layout, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2.host.h` is a host API header for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ctc2_vmem_encode`, `ia_css_ctc2_encode`; macros/guards: `__IA_CSS_CTC2_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the chroma tone/control correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_ctc2_param.h"`, `"ia_css_ctc2_types.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2_param.h` is a ISP parameter ABI header for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 40-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `VMEM_ARRAY`; types: `struct ia_css_isp_ctc2_vmem_params` (no parsed scalar fields); `struct ia_css_isp_ctc2_dmem_params` (`uv_y0`, `uv_y1`, `uv_x0`, `uv_x1`, `uv_dydx`); macros/guards: `__IA_CSS_CTC2_PARAM_H`, `IA_CSS_CTC_COEF_SHIFT`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"vmem.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2_types.h` is a CSS public type header for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 46-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_ctc2_config` (`y_y0`, `y_y1`, `y_y2`, `y_y3`, `y_y4`, `y_y5`, `y_x1`, `y_x2`, `y_x3`, `y_x4`, `uv_y0`, `uv_y1`, `uv_x0`, `uv_x1`); macros/guards: `__IA_CSS_CTC2_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc2/ia_css_ctc2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc.host.c` is a host implementation for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ctc_vamem_encode`, `ia_css_ctc_debug_dtrace`; default/static data: `default_ctc_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace` copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the chroma tone/control correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"assert_support.h"`, `"ia_css_ctc.host.h"`. Important integration signals: debug tracing, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; buffer copies depend on grid dimensions and caller-allocated array sizes.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc.host.h` is a host API header for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ctc_vamem_encode`, `ia_css_ctc_debug_dtrace`; macros/guards: `__IA_CSS_CTC_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the chroma tone/control correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"sh_css_params.h"`, `"ia_css_ctc_param.h"`, `"ia_css_ctc_table.host.h"`. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_param.h` is a ISP parameter ABI header for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_ctc_vamem_params` (`ctc`); macros/guards: `__IA_CSS_CTC_PARAM_H`, `SH_CSS_ISP_CTC_TABLE_SIZE_LOG2`, `SH_CSS_ISP_CTC_TABLE_SIZE`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `<system_global.h>`, `"ia_css_ctc_types.h"`. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_table.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_table.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_table.host.c` is a host implementation for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 62-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_config_ctc_table`; default/static data: `default_ctc_table_data`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the chroma tone/control correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<linux/string.h>`, `<type_support.h>`, `"system_global.h"`, `"vamem.h"`, `"ia_css_types.h"`, `"ia_css_ctc_table.host.h"`. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

buffer copies depend on grid dimensions and caller-allocated array sizes.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_table.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_table.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_table.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_table.host.h` is a host API header for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 16-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_config_ctc_table`; macros/guards: `__IA_CSS_CTC_TABLE_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the chroma tone/control correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_ctc_types.h"`. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_table.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_types.h` is a CSS public type header for the AtomISP chroma tone/control correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 102-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_ctc_config` (`y0`, `y1`, `y2`, `y3`, `y4`, `y5`, `ce_gain_exp`, `x1`, `x2`, `x3`, `x4`); `struct ia_css_ctc_table` (`vamem_type`, `data`); macros/guards: `__IA_CSS_CTC_TYPES_H`, `IA_CSS_CTC_COEF_SHIFT`, `IA_CSS_VAMEM_1_CTC_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_1_CTC_TABLE_SIZE`, `IA_CSS_VAMEM_2_CTC_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_2_CTC_TABLE_SIZE`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<linux/bitops.h>`. The integration point is the AtomISP CSS parameter pipeline for chroma tone/control correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ctc/ctc_1.0/ia_css_ctc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de.host.c` is a host implementation for the AtomISP defect/dependent edge enhancement block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 71-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_de_encode`, `ia_css_de_dump`, `ia_css_de_debug_dtrace`, `ia_css_init_de_state`; default/static data: `default_de_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures state initialization helpers zero or seed ISP state buffers before firmware execution debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the defect/dependent edge enhancement kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data; state buffers are caller-owned and persist only for the lifetime of the ISP binary/frame context. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"sh_css_frac.h"`, `"ia_css_de.host.h"`. Important integration signals: debug tracing, fixed-point fitting helpers, vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for defect/dependent edge enhancement: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; fixed-point fitting and bit-depth shifts must match firmware expectations or image quality changes silently.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de.host.h` is a host API header for the AtomISP defect/dependent edge enhancement block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_de_encode`, `ia_css_de_dump`, `ia_css_de_debug_dtrace`, `ia_css_init_de_state`; macros/guards: `__IA_CSS_DE_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the defect/dependent edge enhancement kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_de_types.h"`, `"ia_css_de_param.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for defect/dependent edge enhancement: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de_param.h` is a ISP parameter ABI header for the AtomISP defect/dependent edge enhancement block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 19-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_de_params` (`pixelnoise`, `c1_coring_threshold`, `c2_coring_threshold`); macros/guards: `__IA_CSS_DE_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for defect/dependent edge enhancement: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de_types.h` is a CSS public type header for the AtomISP defect/dependent edge enhancement block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 34-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_de_config` (`pixelnoise`, `c1_coring_threshold`, `c2_coring_threshold`); macros/guards: `__IA_CSS_DE_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for defect/dependent edge enhancement: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_1.0/ia_css_de_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2.host.c` is a host implementation for the AtomISP defect/dependent edge enhancement block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ecd_encode`, `ia_css_ecd_debug_dtrace`; default/static data: `default_ecd_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the defect/dependent edge enhancement kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"ia_css_de2.host.h"`. Important integration signals: debug tracing. The integration point is the AtomISP CSS parameter pipeline for defect/dependent edge enhancement: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2.host.h` is a host API header for the AtomISP defect/dependent edge enhancement block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ecd_encode`, `ia_css_ecd_dump`, `ia_css_ecd_debug_dtrace`; macros/guards: `__IA_CSS_DE2_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the defect/dependent edge enhancement kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_de2_types.h"`, `"ia_css_de2_param.h"`. The integration point is the AtomISP CSS parameter pipeline for defect/dependent edge enhancement: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2_param.h` is a ISP parameter ABI header for the AtomISP defect/dependent edge enhancement block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_ecd_params` (`zip_strength`, `fc_strength`, `fc_debias`); macros/guards: `__IA_CSS_DE2_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"../de_1.0/ia_css_de_param.h"`. The integration point is the AtomISP CSS parameter pipeline for defect/dependent edge enhancement: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2_types.h` is a CSS public type header for the AtomISP defect/dependent edge enhancement block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 33-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_ecd_config` (`zip_strength`, `fc_strength`, `fc_debias`); macros/guards: `__IA_CSS_DE2_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for defect/dependent edge enhancement: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/de/de_2/ia_css_de2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp.host.c` is a host implementation for the AtomISP defect pixel correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 123-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_dp_encode`, `ia_css_dp_dump`, `ia_css_dp_debug_dtrace`, `ia_css_init_dp_state`; default/static data: `default_dp_10bpp_config`, `default_dp_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures state initialization helpers zero or seed ISP state buffers before firmware execution debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the defect pixel correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data; state buffers are caller-owned and persist only for the lifetime of the ISP binary/frame context. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"sh_css_frac.h"`, `"ia_css_dp.host.h"`. Important integration signals: debug tracing, fixed-point fitting helpers, vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for defect pixel correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; fixed-point fitting and bit-depth shifts must match firmware expectations or image quality changes silently.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp.host.h` is a host API header for the AtomISP defect pixel correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 39-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_dp_encode`, `ia_css_dp_dump`, `ia_css_dp_debug_dtrace`, `ia_css_init_dp_state`; macros/guards: `__IA_CSS_DP_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the defect pixel correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_dp_types.h"`, `"ia_css_dp_param.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for defect pixel correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp.host.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp_types.h` is a CSS public type header for the AtomISP defect pixel correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 40-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_dp_config` (`threshold`, `gain`, `gr`, `r`, `b`, `gb`); macros/guards: `__IA_CSS_DP_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for defect pixel correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dp/dp_1.0/ia_css_dp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2.host.c` is a host implementation for the AtomISP second-generation defect-pixel correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 57-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_dpc2_encode`, `ia_css_init_dpc2_state`, `ia_css_dpc2_debug_dtrace`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures state initialization helpers zero or seed ISP state buffers before firmware execution debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the second-generation defect-pixel correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. state buffers are caller-owned and persist only for the lifetime of the ISP binary/frame context. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_dpc2.host.h"`, `"assert_support.h"`. Important integration signals: kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for second-generation defect-pixel correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2.host.h` is a host API header for the AtomISP second-generation defect-pixel correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 31-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_dpc2_encode`, `ia_css_init_dpc2_state`, `ia_css_dpc2_debug_dtrace`; macros/guards: `__IA_CSS_DPC2_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the second-generation defect-pixel correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_dpc2_types.h"`, `"ia_css_dpc2_param.h"`. The integration point is the AtomISP CSS parameter pipeline for second-generation defect-pixel correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2.host.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2_types.h` is a CSS public type header for the AtomISP second-generation defect-pixel correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 51-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_dpc2_config` (`metric1`, `metric2`, `metric3`, `wb_gain_gr`, `wb_gain_r`, `wb_gain_b`, `wb_gain_gb`); macros/guards: `__IA_CSS_DPC2_TYPES_H`, `METRIC1_ONE_FP`, `METRIC2_ONE_FP`, `METRIC3_ONE_FP`, `WBGAIN_ONE_FP`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for second-generation defect-pixel correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dpc2/ia_css_dpc2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs.host.c` is a host implementation for the AtomISP digital video stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 289-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_dvs_config`, `ia_css_dvs_configure`, `convert_coords_to_ispparams`, `convert_allocate_dvs_6axis_config`, `store_dvs_6axis_config`; default/static data: `default_config`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary. The path is specific to the digital video stabilization kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"hmm.h"`, `"ia_css_frame_public.h"`, `"ia_css_isp_configs.h"`, `"ia_css_types.h"`, `"ia_css_host_data.h"`, `"sh_css_param_dvs.h"`, `"sh_css_params.h"`, `"ia_css_binary.h"`, `"ia_css_debug.h"`, `"assert_support.h"`, `"ia_css_dvs.host.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, generated per-kernel configuration hooks, frame geometry and DMA addressing, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for digital video stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs.host.h` is a host API header for the AtomISP digital video stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_dvs_config`, `ia_css_dvs_configure`, `convert_dvs_6axis_config`, `convert_allocate_dvs_6axis_config`, `store_dvs_6axis_config`; macros/guards: `__IA_CSS_DVS_HOST_H`, `DVS_GDC_BLI_INTERP_ENVELOPE`, `DVS_GDC_BCI_INTERP_ENVELOPE`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the digital video stabilization kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_frame_public.h"`, `"ia_css_binary.h"`, `"sh_css_params.h"`, `"ia_css_types.h"`, `"ia_css_dvs_types.h"`, `"ia_css_dvs_param.h"`. Important integration signals: binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for digital video stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs_param.h` is a ISP parameter ABI header for the AtomISP digital video stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 24-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_dvs_isp_config` (`num_horizontal_blocks`, `num_vertical_blocks`); macros/guards: `__IA_CSS_DVS_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<type_support.h>`, `"dma.h"`, `"uds/uds_1.0/ia_css_uds_param.h"`. The integration point is the AtomISP CSS parameter pipeline for digital video stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs_types.h` is a CSS public type header for the AtomISP digital video stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 21-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_dvs_configuration` (`info`); macros/guards: `__IA_CSS_DVS_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"ia_css_frame_public.h"`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for digital video stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/dvs/dvs_1.0/ia_css_dvs_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8.host.c` is a host implementation for the AtomISP edge enhancement and denoise block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 326-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_eed1_8_vmem_encode`, `ia_css_eed1_8_encode`, `ia_css_init_eed1_8_state`, `ia_css_eed1_8_debug_dtrace`; default/static data: `chgrinv_x`, `chgrinv_a`, `chgrinv_b`, `chgrinv_c`, `tcinv_x`, `tcinv_a`, `tcinv_b`, `tcinv_c`, `fcinv_x`, `fcinv_a`, `fcinv_b`, `fcinv_c`; macros/guards: `NUMBER_OF_CHGRINV_POINTS`, `NUMBER_OF_TCINV_POINTS`, `NUMBER_OF_FCINV_POINTS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures state initialization helpers zero or seed ISP state buffers before firmware execution debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the edge enhancement and denoise kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. state buffers are caller-owned and persist only for the lifetime of the ISP binary/frame context. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_debug.h"`, `"type_support.h"`, `"assert_support.h"`, `"math_support.h"`, `"ia_css_eed1_8.host.h"`. Important integration signals: debug tracing, vector-memory array layout, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for edge enhancement and denoise: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8.host.h` is a host API header for the AtomISP edge enhancement and denoise block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 37-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_eed1_8_vmem_encode`, `ia_css_eed1_8_encode`, `ia_css_init_eed1_8_state`, `ia_css_eed1_8_debug_dtrace`; macros/guards: `__IA_CSS_EED1_8_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the edge enhancement and denoise kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_eed1_8_types.h"`, `"ia_css_eed1_8_param.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for edge enhancement and denoise: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8.host.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8_types.h` is a CSS public type header for the AtomISP edge enhancement and denoise block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 79-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_eed1_8_config` (`rbzp_strength`, `fcstrength`, `fcthres_0`, `fcthres_1`, `fc_sat_coef`, `fc_coring_prm`, `aerel_thres0`, `aerel_gain0`, `aerel_thres1`, `aerel_gain1`, `derel_thres0`, `derel_gain0`, `derel_thres1`, `derel_gain1`, `coring_pos0`, `coring_pos1`, `coring_neg0`, `coring_neg1`, and 12 more); macros/guards: `__IA_CSS_EED1_8_TYPES_H`, `IA_CSS_NUMBER_OF_DEW_ENHANCE_SEGMENTS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for edge enhancement and denoise: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/eed1_8/ia_css_eed1_8_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats.host.c` is a host implementation for the AtomISP format conversion block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 56-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_formats_encode`, `ia_css_formats_dump`, `ia_css_formats_debug_dtrace`; default/static data: `default_formats_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the format conversion kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_formats.host.h"`, `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`. Important integration signals: debug tracing, fixed-point fitting helpers. The integration point is the AtomISP CSS parameter pipeline for format conversion: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats.host.h` is a host API header for the AtomISP format conversion block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_formats_encode`, `ia_css_formats_dump`, `ia_css_formats_debug_dtrace`; macros/guards: `__IA_CSS_FORMATS_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the format conversion kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_formats_types.h"`, `"ia_css_formats_param.h"`. The integration point is the AtomISP CSS parameter pipeline for format conversion: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats_param.h` is a ISP parameter ABI header for the AtomISP format conversion block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 17-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_formats_params` (`video_full_range_flag`); macros/guards: `__IA_CSS_FORMATS_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for format conversion: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats_types.h` is a CSS public type header for the AtomISP format conversion block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_formats_config` (`video_full_range_flag`); macros/guards: `__IA_CSS_FORMATS_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for format conversion: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fc/fc_1.0/ia_css_formats_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fixedbds/fixedbds_1.0/ia_css_fixedbds_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fixedbds/fixedbds_1.0/ia_css_fixedbds_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fixedbds/fixedbds_1.0/ia_css_fixedbds_param.h` is a ISP parameter ABI header for the AtomISP fixed Bayer downscaling block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 24-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_bds_params` (`baf_strength`); macros/guards: `__IA_CSS_FIXEDBDS_PARAM_H`, `BDS_UNIT`, `FRAC_LOG`, `FRAC_ACC`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for fixed Bayer downscaling: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fixedbds/fixedbds_1.0/ia_css_fixedbds_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fixedbds/fixedbds_1.0/ia_css_fixedbds_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fixedbds/fixedbds_1.0/ia_css_fixedbds_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fixedbds/fixedbds_1.0/ia_css_fixedbds_types.h` is a CSS public type header for the AtomISP fixed Bayer downscaling block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 16-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_bds_factor` (`numerator`, `denominator`, `bds_factor`); macros/guards: `__IA_CSS_FIXEDBDS_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for fixed Bayer downscaling: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fixedbds/fixedbds_1.0/ia_css_fixedbds_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn.host.c` is a host implementation for the AtomISP fixed pattern noise correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 85-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_fpn_encode`, `ia_css_fpn_dump`, `ia_css_fpn_config`, `ia_css_fpn_configure`; default/static data: `config`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the fixed pattern noise correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<linux/math.h>`, `<assert_support.h>`, `<ia_css_frame_public.h>`, `<ia_css_frame.h>`, `<ia_css_binary.h>`, `<ia_css_types.h>`, `<sh_css_defs.h>`, `<ia_css_debug.h>`, `"ia_css_isp_configs.h"`, `"isp.h"`, `"ia_css_fpn.host.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, generated per-kernel configuration hooks, frame geometry and DMA addressing, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for fixed pattern noise correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; DMA port configuration assumes vector-width divisibility and returns `-EINVAL` otherwise.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn.host.h` is a host API header for the AtomISP fixed pattern noise correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_fpn_encode`, `ia_css_fpn_dump`, `ia_css_fpn_config`, `ia_css_fpn_configure`; macros/guards: `__IA_CSS_FPN_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the fixed pattern noise correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_binary.h"`, `"ia_css_fpn_types.h"`, `"ia_css_fpn_param.h"`. Important integration signals: binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for fixed pattern noise correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn_param.h` is a ISP parameter ABI header for the AtomISP fixed pattern noise correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_fpn_params` (`shift`, `enabled`); `struct sh_css_isp_fpn_isp_config` (`width_a_over_b`, `port_b`); macros/guards: `__IA_CSS_FPN_PARAM_H`, `FPN_BITS_PER_PIXEL`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"dma.h"`. The integration point is the AtomISP CSS parameter pipeline for fixed pattern noise correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn_types.h` is a CSS public type header for the AtomISP fixed pattern noise correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 44-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_fpn_table` (`data`, `width`, `height`, `shift`, `enabled`); `struct ia_css_fpn_configuration` (`info`); macros/guards: `__IA_CSS_FPN_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for fixed pattern noise correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/fpn/fpn_1.0/ia_css_fpn_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc.host.c` is a host implementation for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 109-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_gc_encode`, `ia_css_ce_encode`, `ia_css_gc_vamem_encode`, `ia_css_gc_dump`, `ia_css_ce_dump`, `ia_css_gc_debug_dtrace`, `ia_css_ce_debug_dtrace`; default/static data: `default_gc_config`, `default_ce_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace` copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the gamma correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"sh_css_frac.h"`, `"vamem.h"`, `"ia_css_gc.host.h"`. Important integration signals: debug tracing, fixed-point fitting helpers. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; fixed-point fitting and bit-depth shifts must match firmware expectations or image quality changes silently; buffer copies depend on grid dimensions and caller-allocated array sizes.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc.host.h` is a host API header for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 57-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_gc_encode`, `ia_css_gc_vamem_encode`, `ia_css_ce_encode`, `ia_css_gc_dump`, `ia_css_ce_dump`, `ia_css_gc_debug_dtrace`, `ia_css_ce_debug_dtrace`; macros/guards: `__IA_CSS_GC_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the gamma correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_gc_param.h"`, `"ia_css_gc_table.host.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_param.h` is a ISP parameter ABI header for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 53-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_gc_params` (`gain_k1`, `gain_k2`); `struct sh_css_isp_ce_params` (`uv_level_min`, `uv_level_max`); `struct sh_css_isp_gc_vamem_params` (`gc`); macros/guards: `__IA_CSS_GC_PARAM_H`, `__INLINE_VAMEM__`, `SH_CSS_ISP_GAMMA_TABLE_SIZE_LOG2`, `SH_CSS_ISP_GC_TABLE_SIZE`, `GAMMA_OUTPUT_BITS`, `GAMMA_OUTPUT_MAX_VAL`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"vamem.h"`, `"ia_css_gc_types.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_table.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_table.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_table.host.c` is a host implementation for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 62-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_config_gamma_table`; default/static data: `default_gamma_table_data`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the gamma correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<linux/string.h>`, `<type_support.h>`, `"system_global.h"`, `"vamem.h"`, `"ia_css_types.h"`, `"ia_css_gc_table.host.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

buffer copies depend on grid dimensions and caller-allocated array sizes.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_table.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_table.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_table.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_table.host.h` is a host API header for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 16-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_config_gamma_table`; macros/guards: `__IA_CSS_GC_TABLE_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the gamma correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_gc_types.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_table.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_types.h` is a CSS public type header for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 89-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_gamma_table` (`vamem_type`, `data`); `struct ia_css_gc_config` (`gain_k1`, `gain_k2`); `struct ia_css_ce_config` (`uv_level_min`, `uv_level_max`); `struct ia_css_macc_config` (`exp`); macros/guards: `__IA_CSS_GC_TYPES_H`, `IA_CSS_GAMMA_GAIN_K_SHIFT`, `IA_CSS_VAMEM_1_GAMMA_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_1_GAMMA_TABLE_SIZE`, `IA_CSS_VAMEM_2_GAMMA_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_2_GAMMA_TABLE_SIZE`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"isp/kernels/ctc/ctc_1.0/ia_css_ctc_types.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_1.0/ia_css_gc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2.host.c` is a host implementation for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 101-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_yuv2rgb_encode`, `ia_css_rgb2yuv_encode`, `ia_css_r_gamma_vamem_encode`, `ia_css_g_gamma_vamem_encode`, `ia_css_b_gamma_vamem_encode`, `ia_css_yuv2rgb_dump`, `ia_css_rgb2yuv_dump`, `ia_css_rgb_gamma_table_debug_dtrace`; default/static data: `default_yuv2rgb_cc_config`, `default_rgb2yuv_cc_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace` copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the gamma correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"csc/csc_1.0/ia_css_csc.host.h"`, `"vamem.h"`, `"ia_css_gc2.host.h"`. Important integration signals: debug tracing. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; buffer copies depend on grid dimensions and caller-allocated array sizes.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2.host.h` is a host API header for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 71-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_yuv2rgb_encode`, `ia_css_rgb2yuv_encode`, `ia_css_r_gamma_vamem_encode`, `ia_css_g_gamma_vamem_encode`, `ia_css_b_gamma_vamem_encode`, `ia_css_yuv2rgb_dump`, `ia_css_rgb2yuv_dump`, `ia_css_rgb_gamma_table_debug_dtrace`; macros/guards: `__IA_CSS_GC2_HOST_H`, `ia_css_yuv2rgb_debug_dtrace`, `ia_css_rgb2yuv_debug_dtrace`, `ia_css_r_gamma_debug_dtrace`, `ia_css_g_gamma_debug_dtrace`, `ia_css_b_gamma_debug_dtrace`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the gamma correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_gc2_types.h"`, `"ia_css_gc2_param.h"`, `"ia_css_gc2_table.host.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_param.h` is a ISP parameter ABI header for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 35-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_rgb_gamma_vamem_params` (`gc`); macros/guards: `__IA_CSS_GC2_PARAM_H`, `SH_CSS_ISP_RGB_GAMMA_TABLE_SIZE`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"ia_css_gc2_types.h"`, `"gc/gc_1.0/ia_css_gc_param.h"`, `"csc/csc_1.0/ia_css_csc_param.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_table.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_table.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_table.host.c` is a host implementation for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 71-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_config_rgb_gamma_tables`; default/static data: `default_gamma_table_data`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the gamma correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<linux/string.h>`, `<type_support.h>`, `"system_global.h"`, `"vamem.h"`, `"ia_css_types.h"`, `"ia_css_gc2_table.host.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

buffer copies depend on grid dimensions and caller-allocated array sizes.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_table.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_table.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_table.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_table.host.h` is a host API header for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_config_rgb_gamma_tables`; macros/guards: `__IA_CSS_GC2_TABLE_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the gamma correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_gc2_types.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_table.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_types.h` is a CSS public type header for the AtomISP gamma correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 46-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_rgb_gamma_table` (`vamem_type`, `data`); macros/guards: `__IA_CSS_GC2_TYPES_H`, `IA_CSS_VAMEM_1_RGB_GAMMA_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_1_RGB_GAMMA_TABLE_SIZE`, `IA_CSS_VAMEM_2_RGB_GAMMA_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_2_RGB_GAMMA_TABLE_SIZE`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"isp/kernels/ctc/ctc_1.0/ia_css_ctc_types.h"`. The integration point is the AtomISP CSS parameter pipeline for gamma correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/gc/gc_2/ia_css_gc2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr.host.c` is a host implementation for the AtomISP high dynamic range tone mapping block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_hdr_init_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary state initialization helpers zero or seed ISP state buffers before firmware execution. The path is specific to the high dynamic range tone mapping kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_hdr.host.h"`. The integration point is the AtomISP CSS parameter pipeline for high dynamic range tone mapping: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr.host.h` is a host API header for the AtomISP high dynamic range tone mapping block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_hdr_init_config`; macros/guards: `__IA_CSS_HDR_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the high dynamic range tone mapping kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_hdr_param.h"`, `"ia_css_hdr_types.h"`. The integration point is the AtomISP CSS parameter pipeline for high dynamic range tone mapping: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr_param.h` is a ISP parameter ABI header for the AtomISP high dynamic range tone mapping block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_hdr_irradiance_params` (`test_irr`, `weight_bpp`); `struct sh_css_hdr_deghost_params` (`test_deg`); `struct sh_css_hdr_exclusion_params` (`test_excl`); `struct sh_css_isp_hdr_params` (`irradiance`, `deghost`, `exclusion`); macros/guards: `__IA_CSS_HDR_PARAMS_H`, `HDR_NUM_INPUT_FRAMES`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for high dynamic range tone mapping: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr_types.h` is a CSS public type header for the AtomISP high dynamic range tone mapping block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 61-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_hdr_irradiance_params` (`test_irr`, `weight_bpp`); `struct ia_css_hdr_deghost_params` (`test_deg`); `struct ia_css_hdr_exclusion_params` (`test_excl`); `struct ia_css_hdr_config` (`irradiance`, `deghost`, `exclusion`); macros/guards: `__IA_CSS_HDR_TYPES_H`, `IA_CSS_HDR_MAX_NUM_INPUT_FRAMES`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for high dynamic range tone mapping: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/hdr/ia_css_hdr_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io.host.c` is a host implementation for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 88-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_bayer_io_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary. The path is specific to the IPU2 input/output line-store formatting kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<linux/bitops.h>`, `<linux/math.h>`, `"ia_css_bayer_io.host.h"`, `"dma.h"`, `"ia_css_debug.h"`, `"ia_css_isp_params.h"`, `"ia_css_frame.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io.host.h` is a host API header for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_bayer_io_config`; macros/guards: `__BAYER_IO_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the IPU2 input/output line-store formatting kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_bayer_io_param.h"`, `"ia_css_bayer_io_types.h"`, `"ia_css_binary.h"`, `"sh_css_internal.h"`. Important integration signals: binary-specific configuration dispatch. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io_param.h` is a ISP parameter ABI header for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 12-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_BAYER_IO_PARAM`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"../common/ia_css_common_io_param.h"`. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io_types.h` is a CSS public type header for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 12-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_BAYER_IO_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"../common/ia_css_common_io_types.h"`. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/bayer_io_ls/ia_css_bayer_io_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/common/ia_css_common_io_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/common/ia_css_common_io_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/common/ia_css_common_io_param.h` is a ISP parameter ABI header for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 13-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_COMMON_IO_PARAM`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"../common/ia_css_common_io_types.h"`. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/common/ia_css_common_io_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/common/ia_css_common_io_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/common/ia_css_common_io_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/common/ia_css_common_io_types.h` is a CSS public type header for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_common_io_config` (`base_address`, `width`, `height`, `stride`, `ddr_elems_per_word`, `dma_channel`); macros/guards: `__IA_CSS_COMMON_IO_TYPES`, `MAX_IO_DMA_CHANNELS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/common/ia_css_common_io_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io.host.c` is a host implementation for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 91-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_yuv444_io_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary. The path is specific to the IPU2 input/output line-store formatting kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<linux/bitops.h>`, `<linux/math.h>`, `"ia_css_yuv444_io.host.h"`, `"dma.h"`, `"ia_css_debug.h"`, `"ia_css_isp_params.h"`, `"ia_css_frame.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io.host.h` is a host API header for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 19-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_yuv444_io_config`; macros/guards: `__YUV444_IO_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the IPU2 input/output line-store formatting kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_yuv444_io_param.h"`, `"ia_css_yuv444_io_types.h"`, `"ia_css_binary.h"`, `"sh_css_internal.h"`. Important integration signals: binary-specific configuration dispatch. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io_param.h` is a ISP parameter ABI header for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 13-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_YUV444_IO_PARAM`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"../common/ia_css_common_io_param.h"`. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io_types.h` is a CSS public type header for the AtomISP IPU2 input/output line-store formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 13-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_YUV444_IO_TYPES`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"../common/ia_css_common_io_types.h"`. The integration point is the AtomISP CSS parameter pipeline for IPU2 input/output line-store formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ipu2_io_ls/yuv444_io_ls/ia_css_yuv444_io_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator.host.c` is a host implementation for the AtomISP ISP iterator/grid traversal block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_iterator_config`, `ia_css_iterator_configure`; default/static data: `default_config`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary. The path is specific to the ISP iterator/grid traversal kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_iterator.host.h"`, `"ia_css_frame_public.h"`, `"ia_css_binary.h"`, `"ia_css_err.h"`, `"ia_css_isp_configs.h"`. Important integration signals: binary-specific configuration dispatch, generated per-kernel configuration hooks, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for ISP iterator/grid traversal: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator.host.h` is a host API header for the AtomISP ISP iterator/grid traversal block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_iterator_config`, `ia_css_iterator_configure`; macros/guards: `__IA_CSS_ITERATOR_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the ISP iterator/grid traversal kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_frame_public.h"`, `"ia_css_binary.h"`, `"ia_css_err.h"`, `"ia_css_iterator_param.h"`. Important integration signals: binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for ISP iterator/grid traversal: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator_param.h` is a ISP parameter ABI header for the AtomISP ISP iterator/grid traversal block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_iterator_configuration` (`input_info`, `internal_info`, `output_info`, `vf_info`, `dvs_envelope`); `struct sh_css_isp_iterator_isp_config` (`input_info`, `internal_info`, `output_info`, `vf_info`, `dvs_envelope`); macros/guards: `__IA_CSS_ITERATOR_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"ia_css_frame_public.h"`, `"ia_css_frame_comm.h"`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for ISP iterator/grid traversal: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/iterator/iterator_1.0/ia_css_iterator_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5.host.c` is a host implementation for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 66-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_macc1_5_encode`, `ia_css_macc1_5_vmem_encode`, `ia_css_macc1_5_debug_dtrace`; default/static data: `default_macc1_5_config`, `idx_map`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the matrix acceleration color correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"ia_css_macc1_5.host.h"`. Important integration signals: debug tracing, vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5.host.h` is a host API header for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 33-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_macc1_5_encode`, `ia_css_macc1_5_vmem_encode`, `ia_css_macc1_5_debug_dtrace`; macros/guards: `__IA_CSS_MACC1_5_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the matrix acceleration color correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_macc1_5_param.h"`, `"ia_css_macc1_5_table.host.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_param.h` is a ISP parameter ABI header for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 23-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `VMEM_ARRAY`; types: `struct sh_css_isp_macc1_5_params` (`exp`); `struct sh_css_isp_macc1_5_vmem_params` (no parsed scalar fields); macros/guards: `__IA_CSS_MACC1_5_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"vmem.h"`, `"ia_css_macc1_5_types.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_table.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_table.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_table.host.c` is a host implementation for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

default/static data: `default_macc1_5_table`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. the file performs direct field translation for the kernel host adapter. The path is specific to the matrix acceleration color correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"system_global.h"`, `"ia_css_types.h"`, `"ia_css_macc1_5_table.host.h"`. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_table.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_table.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_table.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_table.host.h` is a host API header for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 14-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_MACC1_5_TABLE_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the matrix acceleration color correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"macc/macc1_5/ia_css_macc1_5_types.h"`. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_table.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_types.h` is a CSS public type header for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 65-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_macc1_5_table` (no parsed scalar fields); `struct ia_css_macc1_5_config` (`exp`); macros/guards: `__IA_CSS_MACC1_5_TYPES_H`, `IA_CSS_MACC_NUM_AXES`, `IA_CSS_MACC_NUM_COEFS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc1_5/ia_css_macc1_5_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc.host.c` is a host implementation for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 41-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_macc_encode`, `ia_css_macc_debug_dtrace`; default/static data: `default_macc_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the matrix acceleration color correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"sh_css_frac.h"`, `"ia_css_macc.host.h"`. Important integration signals: debug tracing, fixed-point fitting helpers. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc.host.h` is a host API header for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 33-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_macc_encode`, `ia_css_macc_dump`, `ia_css_macc_debug_dtrace`; macros/guards: `__IA_CSS_MACC_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the matrix acceleration color correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"sh_css_params.h"`, `"ia_css_macc_param.h"`, `"ia_css_macc_table.host.h"`. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_param.h` is a ISP parameter ABI header for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 17-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_macc_params` (`exp`); macros/guards: `__IA_CSS_MACC_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_table.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_table.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_table.host.c` is a host implementation for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 43-line file for this report.

## Important APIs, Types, and Functions

default/static data: `default_macc_table`, `default_macc2_table`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. the file performs direct field translation for the kernel host adapter. The path is specific to the matrix acceleration color correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"system_global.h"`, `"ia_css_types.h"`, `"ia_css_macc_table.host.h"`. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_table.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_table.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_table.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_table.host.h` is a host API header for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 15-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_MACC_TABLE_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the matrix acceleration color correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_macc_types.h"`. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_table.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_types.h` is a CSS public type header for the AtomISP matrix acceleration color correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_macc_table` (no parsed scalar fields); macros/guards: `__IA_CSS_MACC_TYPES_H`, `IA_CSS_MACC_NUM_AXES`, `IA_CSS_MACC_NUM_COEFS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for matrix acceleration color correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/macc/macc_1.0/ia_css_macc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm.host.c` is a host implementation for the AtomISP normalization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 7-line file for this report.

## Important APIs, Types, and Functions

no callable API; the file contributes declarations or includes. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. the file performs direct field translation for the kernel host adapter. The path is specific to the normalization kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_norm.host.h"`. The integration point is the AtomISP CSS parameter pipeline for normalization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm.host.h` is a host API header for the AtomISP normalization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 12-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_NORM_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the normalization kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_norm_param.h"`. The integration point is the AtomISP CSS parameter pipeline for normalization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm_param.h` is a ISP parameter ABI header for the AtomISP normalization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 10-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_NORM_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for normalization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/norm/norm_1.0/ia_css_norm_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2.host.c` is a host implementation for the AtomISP optical black correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ob2_encode`, `ia_css_ob2_dump`, `ia_css_ob2_debug_dtrace`; default/static data: `default_ob2_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the optical black correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"sh_css_frac.h"`, `"ia_css_debug.h"`, `"isp.h"`, `"ia_css_ob2.host.h"`. Important integration signals: debug tracing, fixed-point fitting helpers. The integration point is the AtomISP CSS parameter pipeline for optical black correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; fixed-point fitting and bit-depth shifts must match firmware expectations or image quality changes silently.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2.host.h` is a host API header for the AtomISP optical black correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ob2_encode`, `ia_css_ob2_dump`, `ia_css_ob2_debug_dtrace`; macros/guards: `__IA_CSS_OB2_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the optical black correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_ob2_types.h"`, `"ia_css_ob2_param.h"`. The integration point is the AtomISP CSS parameter pipeline for optical black correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2_param.h` is a ISP parameter ABI header for the AtomISP optical black correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 20-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_ob2_params` (`blacklevel_gr`, `blacklevel_r`, `blacklevel_b`, `blacklevel_gb`); macros/guards: `__IA_CSS_OB2_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for optical black correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2_types.h` is a CSS public type header for the AtomISP optical black correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_ob2_config` (`level_gr`, `level_r`, `level_b`, `level_gb`); macros/guards: `__IA_CSS_OB2_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"ia_css_frac.h"`. The integration point is the AtomISP CSS parameter pipeline for optical black correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob2/ia_css_ob2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob.host.c` is a host implementation for the AtomISP optical black correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 146-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ob_configure`, `ia_css_ob_encode`, `ia_css_ob_vmem_encode`, `ia_css_ob_dump`, `ia_css_ob_debug_dtrace`; default/static data: `default_ob_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the optical black correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"isp.h"`, `"ia_css_ob.host.h"`. Important integration signals: debug tracing, vector-memory array layout, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for optical black correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob.host.h` is a host API header for the AtomISP optical black correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ob_configure`, `ia_css_ob_encode`, `ia_css_ob_vmem_encode`, `ia_css_ob_dump`, `ia_css_ob_debug_dtrace`; macros/guards: `__IA_CSS_OB_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the optical black correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_ob_types.h"`, `"ia_css_ob_param.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for optical black correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob.host.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob_types.h` is a CSS public type header for the AtomISP optical black correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 60-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_ob_config` (`mode`, `level_gr`, `level_r`, `level_b`, `level_gb`, `start_position`, `end_position`); macros/guards: `__IA_CSS_OB_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"ia_css_frac.h"`. The integration point is the AtomISP CSS parameter pipeline for optical black correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ob/ob_1.0/ia_css_ob_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output.host.c` is a host implementation for the AtomISP output formatter block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 150-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_output_encode`, `ia_css_output_config`, `ia_css_output0_config`, `ia_css_output1_config`, `ia_css_output_configure`, `ia_css_output0_configure`, `ia_css_output1_configure`, `ia_css_output_dump`, `ia_css_output_debug_dtrace`; default/static data: `default_output_config`, `default_output_configuration`, `default_output0_configuration`, `default_output1_configuration`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the output formatter kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_frame.h"`, `"ia_css_debug.h"`, `"ia_css_isp_configs.h"`, `"ia_css_output.host.h"`, `"isp.h"`, `"assert_support.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, generated per-kernel configuration hooks, frame geometry and DMA addressing, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for output formatter: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; DMA port configuration assumes vector-width divisibility and returns `-EINVAL` otherwise.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output.host.h` is a host API header for the AtomISP output formatter block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_output_encode`, `ia_css_output_config`, `ia_css_output0_config`, `ia_css_output1_config`, `ia_css_output_configure`, `ia_css_output0_configure`, `ia_css_output1_configure`, `ia_css_output_dump`, `ia_css_output_debug_dtrace`; macros/guards: `__IA_CSS_OUTPUT_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the output formatter kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_frame_public.h"`, `"ia_css_binary.h"`, `"ia_css_output_types.h"`, `"ia_css_output_param.h"`. Important integration signals: binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for output formatter: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output_param.h` is a ISP parameter ABI header for the AtomISP output formatter block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_output_isp_config` (`width_a_over_b`, `height`, `enable`, `info`, `port_b`); `struct sh_css_isp_output_params` (`enable_hflip`, `enable_vflip`); macros/guards: `__IA_CSS_OUTPUT_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<type_support.h>`, `"dma.h"`, `"ia_css_frame_comm.h"`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for output formatter: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output_types.h` is a CSS public type header for the AtomISP output formatter block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 39-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_output_configuration` (`info`); `struct ia_css_output0_configuration` (`info`); `struct ia_css_output1_configuration` (`info`); `struct ia_css_output_config` (`enable_hflip`, `enable_vflip`); macros/guards: `__IA_CSS_OUTPUT_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for output formatter: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/output/output_1.0/ia_css_output_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane.host.c` is a host implementation for the AtomISP quadrature-plane formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_qplane_config`, `ia_css_qplane_configure`; default/static data: `default_config`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary. The path is specific to the quadrature-plane formatting kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_frame.h"`, `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"assert_support.h"`, `"ia_css_isp_configs.h"`, `"isp.h"`, `"ia_css_qplane.host.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, generated per-kernel configuration hooks, frame geometry and DMA addressing, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for quadrature-plane formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

DMA port configuration assumes vector-width divisibility and returns `-EINVAL` otherwise.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane.host.h` is a host API header for the AtomISP quadrature-plane formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 31-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_qplane_config`, `ia_css_qplane_configure`; macros/guards: `__IA_CSS_QPLANE_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the quadrature-plane formatting kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<ia_css_frame_public.h>`, `<ia_css_binary.h>`, `"sh_css_internal.h"`, `"ia_css_qplane_types.h"`, `"ia_css_qplane_param.h"`. Important integration signals: binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for quadrature-plane formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane_param.h` is a ISP parameter ABI header for the AtomISP quadrature-plane formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_qplane_isp_config` (`width_a_over_b`, `port_b`, `inout_port_config`, `input_needs_raw_binning`, `format`); macros/guards: `__IA_CSS_QPLANE_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<type_support.h>`, `"dma.h"`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for quadrature-plane formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane_types.h` is a CSS public type header for the AtomISP quadrature-plane formatting block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 23-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_qplane_configuration` (`pipe`, `info`); macros/guards: `__IA_CSS_QPLANE_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<ia_css_frame_public.h>`, `"sh_css_internal.h"`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for quadrature-plane formatting: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/qplane/qplane_2/ia_css_qplane_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw.host.c` is a host implementation for the AtomISP raw frame pass-through block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 114-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `css2isp_stream_format`, `ia_css_raw_config`, `ia_css_raw_configure`; default/static data: `default_config`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary. The path is specific to the raw frame pass-through kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_frame.h"`, `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"assert_support.h"`, `"ia_css_isp_configs.h"`, `"isp.h"`, `"isp/modes/interface/isp_types.h"`, `"ia_css_raw.host.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, generated per-kernel configuration hooks, frame geometry and DMA addressing, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for raw frame pass-through: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

several paths rely on assertions for null/shape checks rather than recoverable validation; DMA port configuration assumes vector-width divisibility and returns `-EINVAL` otherwise.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw.host.h` is a host API header for the AtomISP raw frame pass-through block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_raw_config`, `ia_css_raw_configure`; macros/guards: `__IA_CSS_RAW_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the raw frame pass-through kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_binary.h"`, `"ia_css_raw_types.h"`, `"ia_css_raw_param.h"`. Important integration signals: binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for raw frame pass-through: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw_param.h` is a ISP parameter ABI header for the AtomISP raw frame pass-through block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_raw_isp_config` (`width_a_over_b`, `port_b`, `inout_port_config`, `input_needs_raw_binning`, `format`, `required_bds_factor`, `two_ppc`, `stream_format`, `deinterleaved`, `start_column`, `start_line`, `enable_left_padding`); macros/guards: `__IA_CSS_RAW_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`, `"dma.h"`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for raw frame pass-through: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw_types.h` is a CSS public type header for the AtomISP raw frame pass-through block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_raw_configuration` (`pipe`, `in_info`, `internal_info`, `two_ppc`, `stream_format`, `deinterleaved`, `enable_left_padding`); macros/guards: `__IA_CSS_RAW_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<ia_css_frame_public.h>`, `"sh_css_internal.h"`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for raw frame pass-through: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw/raw_1.0/ia_css_raw_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw_aa_binning/raw_aa_binning_1.0/ia_css_raa.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw_aa_binning/raw_aa_binning_1.0/ia_css_raa.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw_aa_binning/raw_aa_binning_1.0/ia_css_raa.host.c` is a host implementation for the AtomISP raw anti-alias binning block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 24-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_raa_encode`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures. The path is specific to the raw anti-alias binning kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_internal.h"`, `"sh_css_frac.h"`, `"ia_css_raa.host.h"`. Important integration signals: fixed-point fitting helpers. The integration point is the AtomISP CSS parameter pipeline for raw anti-alias binning: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw_aa_binning/raw_aa_binning_1.0/ia_css_raa.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw_aa_binning/raw_aa_binning_1.0/ia_css_raa.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw_aa_binning/raw_aa_binning_1.0/ia_css_raa.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw_aa_binning/raw_aa_binning_1.0/ia_css_raa.host.h` is a host API header for the AtomISP raw anti-alias binning block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 19-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_raa_encode`; macros/guards: `__IA_CSS_RAA_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the raw anti-alias binning kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"aa/aa_2/ia_css_aa2_types.h"`, `"aa/aa_2/ia_css_aa2_param.h"`. The integration point is the AtomISP CSS parameter pipeline for raw anti-alias binning: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/raw_aa_binning/raw_aa_binning_1.0/ia_css_raa.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref.host.c` is a host implementation for the AtomISP reference-frame transfer block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ref_config`, `ia_css_ref_configure`, `ia_css_init_ref_state`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary state initialization helpers zero or seed ISP state buffers before firmware execution. The path is specific to the reference-frame transfer kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. state buffers are caller-owned and persist only for the lifetime of the ISP binary/frame context. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<assert_support.h>`, `<ia_css_frame_public.h>`, `<ia_css_frame.h>`, `<ia_css_binary.h>`, `"ia_css_isp_configs.h"`, `"isp.h"`, `"ia_css_ref.host.h"`. Important integration signals: binary-specific configuration dispatch, generated per-kernel configuration hooks, frame geometry and DMA addressing, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for reference-frame transfer: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; several paths rely on assertions for null/shape checks rather than recoverable validation; DMA port configuration assumes vector-width divisibility and returns `-EINVAL` otherwise.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref.host.h` is a host API header for the AtomISP reference-frame transfer block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_ref_config`, `ia_css_ref_configure`, `ia_css_init_ref_state`; macros/guards: `__IA_CSS_REF_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the reference-frame transfer kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<ia_css_frame_public.h>`, `<ia_css_binary.h>`, `"ia_css_ref_types.h"`, `"ia_css_ref_param.h"`, `"ia_css_ref_state.h"`. Important integration signals: binary-specific configuration dispatch, frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for reference-frame transfer: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_param.h` is a ISP parameter ABI header for the AtomISP reference-frame transfer block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_ref_configuration` (`ref_frames`, `dvs_frame_delay`); `struct sh_css_isp_ref_isp_config` (`width_a_over_b`, `port_b`, `ref_frame_addr_y`, `ref_frame_addr_c`, `dvs_frame_delay`); macros/guards: `__IA_CSS_REF_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `<type_support.h>`, `"sh_css_defs.h"`, `"dma.h"`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for reference-frame transfer: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_state.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_state.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_state.h` is a ISP state header for the AtomISP reference-frame transfer block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_ref_dmem_state` (`ref_in_buf_idx`, `ref_out_buf_idx`); macros/guards: `__IA_CSS_REF_STATE_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for reference-frame transfer: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_types.h` is a CSS public type header for the AtomISP reference-frame transfer block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 17-line file for this report.

## Important APIs, Types, and Functions

macros/guards: `__IA_CSS_REF_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `<ia_css_frame_public.h>`. Important integration signals: frame geometry and DMA addressing. The integration point is the AtomISP CSS parameter pipeline for reference-frame transfer: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ref/ref_1.0/ia_css_ref_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a.host.c` is a host implementation for the AtomISP 3A statistics collection block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 373-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_s3a_configure`, `ia_css_ae_encode`, `ia_css_awb_encode`, `ia_css_af_encode`, `ia_css_s3a_encode`, `ia_css_process_s3a`, `ia_css_ae_dump`, `ia_css_awb_dump`, `ia_css_af_dump`, `ia_css_s3a_dump`, `ia_css_s3a_debug_dtrace`, `ia_css_s3a_hmem_decode`, `ia_css_s3a_dmem_decode`, `merge_hi_lo_14`, `ia_css_s3a_vmem_decode`; default/static data: `default_3a_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace` copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the 3A statistics collection kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"sh_css_frac.h"`, `"assert_support.h"`, `"bh/bh_2/ia_css_bh.host.h"`, `"ia_css_s3a.host.h"`. Important integration signals: debug tracing, fixed-point fitting helpers, vector-memory array layout, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for 3A statistics collection: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; fixed-point fitting and bit-depth shifts must match firmware expectations or image quality changes silently; buffer copies depend on grid dimensions and caller-allocated array sizes; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a.host.h` is a host API header for the AtomISP 3A statistics collection block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 69-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_s3a_configure`, `ia_css_s3a_encode`, `ia_css_ae_dump`, `ia_css_awb_dump`, `ia_css_af_dump`, `ia_css_s3a_dump`, `ia_css_s3a_debug_dtrace`, `ia_css_s3a_hmem_decode`, `ia_css_s3a_dmem_decode`, `ia_css_s3a_vmem_decode`; macros/guards: `__IA_CSS_S3A_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the 3A statistics collection kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_s3a_types.h"`, `"ia_css_s3a_param.h"`, `"bh/bh_2/ia_css_bh.host.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for 3A statistics collection: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a_param.h` is a ISP parameter ABI header for the AtomISP 3A statistics collection block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_ae_params` (`y_coef_r`, `y_coef_g`, `y_coef_b`); `struct sh_css_isp_awb_params` (`lg_high_raw`, `lg_low`, `lg_high`); `struct sh_css_isp_af_params` (`fir1`, `fir2`); `struct sh_css_isp_s3a_params` (`ae`, `awb`, `af`); macros/guards: `__IA_CSS_S3A_PARAM_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for 3A statistics collection: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/s3a/s3a_1.0/ia_css_s3a_param.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc.host.c` is a host implementation for the AtomISP shading correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 82-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_sc_encode`, `ia_css_sc_dump`, `sh_css_get_shading_settings`, `sh_css_set_shading_settings`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the shading correction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"assert_support.h"`, `"ia_css_isp_configs.h"`, `"ia_css_sc.host.h"`. Important integration signals: debug tracing, generated per-kernel configuration hooks, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for shading correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc.host.h` is a host API header for the AtomISP shading correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_sc_encode`, `ia_css_sc_dump`, `sh_css_get_shading_settings`, `sh_css_set_shading_settings`; macros/guards: `__IA_CSS_SC_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the shading correction kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"sh_css_params.h"`, `"ia_css_sc_types.h"`, `"ia_css_sc_param.h"`. The integration point is the AtomISP CSS parameter pipeline for shading correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc_param.h` is a ISP parameter ABI header for the AtomISP shading correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 34-line file for this report.

## Important APIs, Types, and Functions

types: `struct sh_css_isp_sc_params` (`gain_shift`); `struct sh_css_isp_sc_isp_config` (`interped_gain_hor_slice_bqs`, `internal_frame_origin_y_bqs_on_sctbl`); macros/guards: `__IA_CSS_SC_PARAM_H`, `SH_CSS_SC_INTERPED_GAIN_HOR_SLICE_TIMES`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow here. The declared structures are populated by host encode/configure helpers, copied into ISP DMEM/VMEM/state memory, and consumed by the firmware kernel during frame processing.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for shading correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc_types.h` is a CSS public type header for the AtomISP shading correction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 112-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_shading_table` (`enable`, `sensor_width`, `sensor_height`, `width`, `height`, `fraction_bits`, `data`); `struct ia_css_shading_settings` (`enable_shading_table_conversion`); macros/guards: `__IA_CSS_SC_TYPES_H`, `IA_CSS_SC_NUM_COLORS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for shading correction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sc/sc_1.0/ia_css_sc_types.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis.host.c` is a host implementation for the AtomISP statistics-based digital image stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 428-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `fill_row`, `ia_css_sdis_horicoef_vmem_encode`, `ia_css_sdis_vertcoef_vmem_encode`, `ia_css_sdis_horiproj_encode`, `ia_css_sdis_vertproj_encode`, `ia_css_get_isp_dis_coefficients`, `ia_css_sdis_hor_coef_tbl_bytes`, `ia_css_sdis_ver_coef_tbl_bytes`, `ia_css_sdis_init_info`, `ia_css_sdis_clear_coefficients`, `ia_css_get_dvs_statistics`, `ia_css_translate_dvs_statistics`, `ia_css_isp_dvs_statistics_allocate`, `ia_css_isp_dvs_statistics_map_allocate`, `ia_css_isp_dvs_statistics_map_free`, `ia_css_isp_dvs_statistics_free`, and 4 more; default/static data: `default_sdis_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures state initialization helpers zero or seed ISP state buffers before firmware execution debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace` copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the statistics-based digital image stabilization kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data; statistics or coefficient payloads live in HMM/ISP memory until explicitly copied or freed. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"hmm.h"`, `"assert_support.h"`, `"ia_css_debug.h"`, `"ia_css_sdis_types.h"`, `"sdis/common/ia_css_sdis_common.host.h"`, `"ia_css_sdis.host.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, vector-memory array layout, host/ISP memory transfer, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for statistics-based digital image stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; buffer copies depend on grid dimensions and caller-allocated array sizes; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis.host.h` is a host API header for the AtomISP statistics-based digital image stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 93-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_sdis_horicoef_vmem_encode`, `ia_css_sdis_vertcoef_vmem_encode`, `ia_css_sdis_horiproj_encode`, `ia_css_sdis_vertproj_encode`, `ia_css_get_isp_dis_coefficients`, `ia_css_get_dvs_statistics`, `ia_css_translate_dvs_statistics`, `ia_css_isp_dvs_statistics_allocate`, `ia_css_isp_dvs_statistics_free`, `ia_css_sdis_hor_coef_tbl_bytes`, `ia_css_sdis_ver_coef_tbl_bytes`, `ia_css_sdis_init_info`, `ia_css_sdis_clear_coefficients`, `ia_css_sdis_horicoef_debug_dtrace`, `ia_css_sdis_vertcoef_debug_dtrace`, `ia_css_sdis_horiproj_debug_dtrace`, and 1 more; macros/guards: `__IA_CSS_SDIS_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the statistics-based digital image stabilization kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_sdis_types.h"`, `"ia_css_binary.h"`, `"ia_css_stream.h"`, `"sh_css_params.h"`. Important integration signals: binary-specific configuration dispatch, vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for statistics-based digital image stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis_types.h` is a CSS public type header for the AtomISP statistics-based digital image stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 47-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_dvs_coefficients` (`grid`, `hor_coefs`, `ver_coefs`); `struct ia_css_dvs_statistics` (`grid`, `hor_proj`, `ver_proj`); macros/guards: `__IA_CSS_SDIS_TYPES_H`, `IA_CSS_DVS_NUM_COEF_TYPES`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"isp/kernels/sdis/common/ia_css_sdis_common_types.h"`. The integration point is the AtomISP CSS parameter pipeline for statistics-based digital image stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_1.0/ia_css_sdis_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.c` is a host implementation for the AtomISP statistics-based digital image stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 340-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `fill_row`, `ia_css_sdis2_horicoef_vmem_encode`, `ia_css_sdis2_vertcoef_vmem_encode`, `ia_css_sdis2_horiproj_encode`, `ia_css_sdis2_vertproj_encode`, `ia_css_get_isp_dvs2_coefficients`, `ia_css_sdis2_clear_coefficients`, `ia_css_get_dvs2_statistics`, `ia_css_translate_dvs2_statistics`, `ia_css_isp_dvs2_statistics_allocate`, `ia_css_isp_dvs2_statistics_free`, `ia_css_sdis2_horicoef_debug_dtrace`, `ia_css_sdis2_vertcoef_debug_dtrace`, `ia_css_sdis2_horiproj_debug_dtrace`, `ia_css_sdis2_vertproj_debug_dtrace`; default/static data: `default_sdis2_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace` copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the statistics-based digital image stabilization kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data; statistics or coefficient payloads live in HMM/ISP memory until explicitly copied or freed. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"hmm.h"`, `<assert_support.h>`, `"ia_css_debug.h"`, `"ia_css_sdis2.host.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, vector-memory array layout, host/ISP memory transfer, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for statistics-based digital image stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; buffer copies depend on grid dimensions and caller-allocated array sizes; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.h` is a host API header for the AtomISP statistics-based digital image stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 87-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_sdis2_horicoef_vmem_encode`, `ia_css_sdis2_vertcoef_vmem_encode`, `ia_css_sdis2_horiproj_encode`, `ia_css_sdis2_vertproj_encode`, `ia_css_get_isp_dvs2_coefficients`, `ia_css_sdis2_clear_coefficients`, `ia_css_get_dvs2_statistics`, `ia_css_translate_dvs2_statistics`, `ia_css_isp_dvs2_statistics_allocate`, `ia_css_isp_dvs2_statistics_free`, `ia_css_sdis2_horicoef_debug_dtrace`, `ia_css_sdis2_vertcoef_debug_dtrace`, `ia_css_sdis2_horiproj_debug_dtrace`, `ia_css_sdis2_vertproj_debug_dtrace`; macros/guards: `__IA_CSS_SDIS2_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the statistics-based digital image stabilization kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_sdis2_types.h"`, `"ia_css_binary.h"`, `"ia_css_stream.h"`, `"sh_css_params.h"`. Important integration signals: binary-specific configuration dispatch, vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for statistics-based digital image stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2_types.h` is a CSS public type header for the AtomISP statistics-based digital image stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_dvs2_coef_types` (`odd_real`, `odd_imag`, `even_real`, `even_imag`); `struct ia_css_dvs2_coefficients` (`grid`, `hor_coefs`, `ver_coefs`); `struct ia_css_dvs2_stat_types` (`odd_real`, `odd_imag`, `even_real`, `even_imag`); `struct ia_css_dvs2_statistics` (`grid`, `hor_prod`, `ver_prod`); macros/guards: `__IA_CSS_SDIS2_TYPES_H`, `IA_CSS_DVS2_NUM_COEF_TYPES`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"isp/kernels/sdis/common/ia_css_sdis_common_types.h"`. The integration point is the AtomISP CSS parameter pipeline for statistics-based digital image stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf.host.c` is a host implementation for the AtomISP transform-domain filtering block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 66-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_tdf_vmem_encode`, `ia_css_tdf_encode`, `ia_css_tdf_debug_dtrace`; default/static data: `g_pyramid`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the transform-domain filtering kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. all state is supplied by the caller through configuration and output parameter pointers. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_debug.h"`, `"ia_css_tdf.host.h"`. Important integration signals: debug tracing, vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for transform-domain filtering: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf.host.h` is a host API header for the AtomISP transform-domain filtering block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_tdf_vmem_encode`, `ia_css_tdf_encode`, `ia_css_tdf_debug_dtrace`; macros/guards: `__IA_CSS_TDF_HOST_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

There is no executable control flow in this header. It declares the host entry points that pipeline setup, parameter encoding tables, and debug code call for the transform-domain filtering kernel; the paired `.host.c` or generated configuration layer supplies the actual flow.

## State and Persistence Behavior

No storage is owned by this file; it only participates in compile-time declarations for the AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_tdf_types.h"`, `"ia_css_tdf_param.h"`. Important integration signals: vector-memory array layout. The integration point is the AtomISP CSS parameter pipeline for transform-domain filtering: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

the main risk is configuration drift between the public CSS type, host encoder, and firmware parameter layout.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf.host.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf_types.h` is a CSS public type header for the AtomISP transform-domain filtering block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 44-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_tdf_config` (`thres_flat_table`, `thres_detail_table`, `epsilon_0`, `epsilon_1`, `eps_scale_text`, `eps_scale_edge`, `sepa_flat`, `sepa_edge`, `blend_flat`, `blend_text`, `blend_edge`, `shading_gain`, `shading_base_gain`, `local_y_gain`, `local_y_base_gain`, `rad_x_origin`, `rad_y_origin`); macros/guards: `__IA_CSS_TDF_TYPES_H`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are `"type_support.h"`. The integration point is the AtomISP CSS parameter pipeline for transform-domain filtering: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tdf/tdf_1.0/ia_css_tdf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr3/ia_css_tnr3_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr3/ia_css_tnr3_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr3/ia_css_tnr3_types.h` is a CSS public type header for the AtomISP temporal noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 56-line file for this report.

## Important APIs, Types, and Functions

types: `struct ia_css_tnr3_kernel_config` (`maxfb_y`, `maxfb_u`, `maxfb_v`, `round_adj_y`, `round_adj_u`, `round_adj_v`, `ref_buf_select`); macros/guards: `_IA_CSS_TNR3_TYPES_H`, `TNR3_NUM_SEGMENTS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

This header has no runtime flow. User-facing CSS configuration is stored in the public structures, then a host encoder translates those fields into lower-level ISP parameter structures before a binary is started.

## State and Persistence Behavior

The file defines layout state rather than owning storage. Instances are embedded in CSS API objects, ISP parameter buffers, or per-binary state blocks, and their values persist only while the corresponding stream, frame, or binary configuration remains active.

## Dependencies and Integration Points

Direct includes are none. The integration point is the AtomISP CSS parameter pipeline for temporal noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

struct layout is an ABI with ISP firmware and generated parameter tables, so field order/type changes are high risk.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; layout checks for expected struct sizes and field offsets when firmware ABI changes are suspected; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr3/ia_css_tnr3_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.c` is a host implementation for the AtomISP temporal noise reduction block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 113-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `ia_css_tnr_encode`, `ia_css_tnr_dump`, `ia_css_tnr_debug_dtrace`, `ia_css_tnr_config`, `ia_css_tnr_configure`, `ia_css_init_tnr_state`; default/static data: `default_tnr_config`; macros/guards: `IA_CSS_INCLUDE_CONFIGURATIONS`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures configuration helpers build a small local configuration object and call the generated `ia_css_configure_*` hook for the selected binary state initialization helpers zero or seed ISP state buffers before firmware execution debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace`. The path is specific to the temporal noise reduction kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data; state buffers are caller-owned and persist only for the lifetime of the ISP binary/frame context. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"ia_css_types.h"`, `"ia_css_frame.h"`, `"sh_css_defs.h"`, `"ia_css_debug.h"`, `"sh_css_frac.h"`, `"assert_support.h"`, `"ia_css_isp_configs.h"`, `"isp.h"`, `"ia_css_tnr.host.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, generated per-kernel configuration hooks, frame geometry and DMA addressing, fixed-point fitting helpers, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for temporal noise reduction: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; fixed-point fitting and bit-depth shifts must match firmware expectations or image quality changes silently; several paths rely on assertions for null/shape checks rather than recoverable validation; DMA port configuration assumes vector-width divisibility and returns `-EINVAL` otherwise.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; binary configuration tests that exercise success and `-EINVAL`/allocation failure paths; debug trace smoke tests with null and populated inputs where supported; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.c -->
