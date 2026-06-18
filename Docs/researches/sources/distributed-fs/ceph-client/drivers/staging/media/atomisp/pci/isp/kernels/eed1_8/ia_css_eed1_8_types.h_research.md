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
