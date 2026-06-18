# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_encoder.c

## Purpose

`tilcdc_encoder.c` creates the tilcdc encoder and attaches the downstream DT bridge/panel chain through a DRM bridge connector.

## Important APIs, Types, and Functions

- `tilcdc_attach_bridge()` sets the encoder CRTC mask, attaches the downstream bridge with `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, creates a bridge connector, attaches it to the encoder, and stores `priv->connector`.
- `tilcdc_encoder_create()` retrieves the downstream bridge from OF graph port 0, allocates a simple encoder, stores it in private state, and attaches the bridge.

## Control Flow

Probe calls `tilcdc_encoder_create()` after CRTC creation. If no bridge exists (`-ENODEV`), the function returns success without setting `priv->connector`; probe later treats this as no output and defers. Successful creation completes the single display pipeline.

## State and Persistence Behavior

The encoder is DRM-managed. `priv->encoder` and `priv->connector` persist until device removal. The downstream bridge chain owns mode discovery and bus properties.

## Dependencies and Integration Points

The file depends on DRM bridge, bridge connector, OF bridge lookup, simple encoder allocation, and the tilcdc private struct. It integrates with DT graph endpoints and the CRTC created in `tilcdc_crtc.c`.

## Risks and Edge Cases

- Returning success on no bridge shifts the actual error decision to probe; future callers must know to check `priv->connector`.
- The possible CRTC mask is hardcoded to `BIT(0)`, matching the single-CRTC design.
- Encoder type is `DRM_MODE_ENCODER_NONE`; downstream bridge/panel must provide meaningful connector behavior.

## Test Signals

Tests should cover absent bridge, deferred bridge, successful bridge connector creation, connector attach failure, and mode probing through panel/bridge chains.
