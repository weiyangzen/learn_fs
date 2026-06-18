<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.h

## Purpose

`dc_spl.h` is the public SSPL interface header for scaler parameter calculation.

## Important APIs, Types, And Functions

- Defines scaler black offsets: `BLACK_OFFSET_RGB_Y` and `BLACK_OFFSET_CBCR`.
- Declares `SPL_NAMESPACE(spl_calculate_scaler_params(struct spl_in *spl_in, struct spl_out *spl_out))`.
- Declares `SPL_NAMESPACE(spl_get_number_of_taps(struct spl_in *spl_in, struct spl_out *spl_out))`.
- Includes `dc_spl_types.h`.

## Control Flow

The header has no executable flow. It exposes the two core entry points implemented in `dc_spl.c`.

## State And Persistence Behavior

No state is stored here. The declared functions write caller-owned output structures and may update fields inside `spl_in`.

## Dependencies And Integration Points

Consumers include this header to call SPL from Display Core scaling/resource programming. The `SPL_NAMESPACE` macro allows namespacing across build environments.

## Risks And Edge Cases

The API relies on large structured inputs from `dc_spl_types.h`; callers must initialize all geometry, format, quality, callback, and output pointers before calling. The black-offset constants must remain consistent with DSCL programming expectations for RGB and YCbCr.

## Test Signals

Build coverage confirms public symbols. Runtime scaler tests should call both public APIs with valid `spl_in`/`spl_out` structures and verify programmed recout, viewport, taps, ratios, and filter pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.h -->
