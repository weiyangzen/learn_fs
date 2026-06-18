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
