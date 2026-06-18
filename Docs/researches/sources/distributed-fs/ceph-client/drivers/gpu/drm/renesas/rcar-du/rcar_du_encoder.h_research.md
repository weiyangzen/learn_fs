# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_encoder.h

## Purpose

`rcar_du_encoder.h` declares the R-Car DU encoder wrapper and initialization API used by KMS setup.

## Important APIs, Types, and Functions

- `struct rcar_du_encoder` embeds `struct drm_encoder` and stores the `enum rcar_du_output` route it represents.
- `to_rcar_encoder()` converts DRM encoders to the driver wrapper.
- `rcar_du_encoder_init()` initializes one encoder/bridge/connector chain.

## Control Flow

The header enables KMS code to initialize encoders per DT endpoint and later recover output route information from encoder masks during atomic CRTC checks.

## State and Persistence Behavior

Each encoder's persistent route identity is stored in `output` and consumed by CRTC output-routing state.

## Dependencies and Integration Points

- Includes DRM encoder definitions and depends on `enum rcar_du_output` from the driver header.
- Used by KMS and CRTC code.

## Risks and Edge Cases

- The container conversion assumes all relevant non-writeback encoders are allocated as `struct rcar_du_encoder`; CRTC code explicitly skips virtual writeback encoders.

## Test Signals

- Atomic routing tests should confirm encoder output IDs are reflected in `rcar_du_crtc_state::outputs`.
