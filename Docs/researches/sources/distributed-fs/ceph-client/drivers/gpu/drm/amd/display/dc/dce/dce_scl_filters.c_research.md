# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_scl_filters.c

## Purpose
This file provides static scaler filter coefficient tables for the DCE transform/scaler path. It contains Modified Lanczos coefficient sets for 2-8 tap filters, 16-phase and 64-phase variants, and multiple input/output scale-ratio bands.

## Important APIs and Data
The core data is a collection of `static const uint16_t` arrays such as `filter_2tap_16p`, `filter_3tap_16p_upscale`, `filter_4tap_64p_149`, through `filter_8tap_64p_183`. Exported selectors are `get_filter_3tap_16p()`, `get_filter_3tap_64p()`, `get_filter_4tap_16p()`, `get_filter_4tap_64p()`, `get_filter_5tap_64p()`, `get_filter_6tap_64p()`, `get_filter_7tap_64p()`, `get_filter_8tap_64p()`, `get_filter_2tap_16p()`, and `get_filter_2tap_64p()`.

## Control Flow
There is no dynamic computation of coefficients. For 3-8 tap selectors, the caller passes a `fixed31_32` ratio. The selector chooses the upscale table for ratios below 1.0, the 1.166 band for ratios below 4/3, the 1.499 band for ratios below 5/3, and the 1.833 band otherwise. Two-tap selectors return fixed tables without ratio branching.

## State and Persistence
All state is read-only static data in the kernel image. The returned pointers are borrowed pointers to constant tables; callers must know the required coefficient count from tap and phase configuration.

## Dependencies and Integration Points
The file includes `transform.h` for `fixed31_32`, `dc_fixpt_one`, and `dc_fixpt_from_fraction()`. It integrates with DCE scaler coefficient programming in the transform block, where selected coefficient arrays are written into scaler filter RAM/registers.

## Risks and Test Signals
The primary risk is table-size or selector mismatch: callers must pair the returned table with the exact tap/phase count. Boundary behavior at ratios exactly 1.0, 4/3, and 5/3 follows the next downscale band because comparisons use `<`. Coefficients are opaque generated constants, so accidental edits are hard to review visually. Test signals include scaler visual tests for upscaling and downscaling across threshold ratios, CRC or image-quality comparison, array length assertions in callers, and build warnings for missing prototypes.
