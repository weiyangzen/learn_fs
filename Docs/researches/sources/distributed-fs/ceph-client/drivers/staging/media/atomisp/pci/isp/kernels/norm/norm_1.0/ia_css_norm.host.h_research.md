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
