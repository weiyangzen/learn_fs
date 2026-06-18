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
