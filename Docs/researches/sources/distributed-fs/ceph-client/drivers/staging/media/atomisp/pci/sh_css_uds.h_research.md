# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_uds.h

## Purpose
Defines compact UDS and crop-position structures shared between pipeline descriptions and CSS internals.

## Important APIs, Types, and Functions
Defines bit-size constants `SIZE_OF_SH_CSS_UDS_INFO_IN_BITS` and `SIZE_OF_SH_CSS_CROP_POS_IN_BITS`, plus `struct sh_css_uds_info` (`curr_dx`, `curr_dy`, `xc`, `yc`) and `struct sh_css_crop_pos` (`x`, `y`).

## Control Flow
No execution; these structs are embedded in pipeline or firmware-facing data.

## State and Persistence Behavior
Values represent per-stage/per-frame scaling and crop positions. They are plain data and persist wherever their parent pipeline structures persist.

## Dependencies and Integration Points
Depends on `type_support.h` for fixed-width `u16`. Used by `pipeline_global.h`, `sh_css_internal.h`, and UDS/crop configuration paths.

## Risks
The bit-size constants imply firmware/layout coupling. Widening fields or changing order can break SP/ISP interpretation.

## Test Signals
Scaling/crop tests should verify expected UDS deltas and crop positions are serialized into SP/ISP structures.
