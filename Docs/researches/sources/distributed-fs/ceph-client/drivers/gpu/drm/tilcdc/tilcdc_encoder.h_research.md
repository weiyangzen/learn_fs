# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_encoder.h

## Purpose

`tilcdc_encoder.h` declares the tilcdc encoder creation entry point for the platform probe path.

## Important APIs, Types, and Functions

- Declares `int tilcdc_encoder_create(struct drm_device *ddev);`.

## Control Flow

`tilcdc_drv.c` calls this function after CRTC/mode-limit setup and before vblank/IRQ registration.

## State and Persistence Behavior

The header has no state. The implementation populates `priv->encoder` and potentially `priv->connector`.

## Dependencies and Integration Points

It relies on `struct drm_device` being visible to the includer and connects the driver core to `tilcdc_encoder.c`.

## Risks and Edge Cases

- The include guard name still references `EXTERNAL` and the trailing comment references `SLAVE`, suggesting historical naming drift.
- No forward declaration of `struct drm_device` appears in this header; includers must include a DRM header or `tilcdc_drv.h` first.

## Test Signals

Build tests should include this header from current and potential new users to catch missing type declarations. Probe tests should validate the success/no-connector behavior.
