# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_encoder.h

## Purpose

`tidss_encoder.h` exposes the TIDSS encoder creation API to KMS setup code. It is intentionally small: callers provide the parent device, downstream bridge, encoder type, and possible CRTC mask.

## Important APIs, Types, and Functions

- Includes DRM encoder definitions for encoder type and CRTC mask context.
- Forward declares `struct tidss_device`.
- Declares `tidss_encoder_create(struct tidss_device *tidss, struct drm_bridge *next_bridge, u32 encoder_type, u32 possible_crtcs)`.

## Control Flow

`tidss_kms.c` calls this function once for each discovered output pipe after creating the CRTC. The implementation allocates encoder/bridge/connector objects and hooks the output path into DRM bridge atomic checks.

## State and Persistence Behavior

The header holds no state. The created objects persist under DRM/devm management after a successful call.

## Dependencies and Integration Points

It links KMS pipe discovery with `tidss_encoder.c` and the DRM bridge ecosystem. The downstream bridge can represent a panel bridge, OLDI bridge, or other bridge obtained from DT graph discovery.

## Risks and Edge Cases

- The prototype uses raw `u32` for encoder type and mask, so invalid values are caught only by runtime paths.
- The header does not document whether `next_bridge` may be NULL; the implementation assumes a valid bridge for attach.

## Test Signals

Build coverage should catch signature changes. Runtime coverage should include successful encoder creation for DPI and LVDS paths and expected failures when the downstream bridge is absent or rejects attach.
