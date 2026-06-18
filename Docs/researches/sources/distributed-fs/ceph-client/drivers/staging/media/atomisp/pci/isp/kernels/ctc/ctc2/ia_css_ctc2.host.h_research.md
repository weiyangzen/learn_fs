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
