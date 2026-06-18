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
