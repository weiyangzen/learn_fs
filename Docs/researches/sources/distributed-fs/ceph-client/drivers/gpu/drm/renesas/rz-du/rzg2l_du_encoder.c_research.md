# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_encoder.c

## Purpose

`rzg2l_du_encoder.c` creates DRM encoders and bridge connectors for RZ/G2L DU outputs. It supports DPAD panel bridges and generic OF bridge chains, then attaches a bridge connector to the encoder.

## Important APIs, Types, and Functions

`rzg2l_du_encoder_count_ports()` detects simple panel-style DPAD nodes. `rzg2l_du_encoder_mode_valid()` caps DPAD0 mode clocks at 83.5 MHz. `rzg2l_du_encoder_init()` is the public constructor. The private `rzg2l_du_encoder` stores the output ID in addition to `drm_encoder`.

## Control Flow

KMS output enumeration passes an output enum and connected DT node. For DPAD with a single port, the code treats the node as a panel and creates a DPI panel bridge. Otherwise it looks up a DRM bridge and may defer probe. It allocates a managed DRM encoder, sets the output ID, attaches the bridge without creating a connector, creates a `drm_bridge_connector`, and attaches it to the encoder.

## State and Persistence Behavior

The encoder is managed by DRM and stores only the output enum. Downstream bridge/panel objects own their own state.

## Dependencies and Integration Points

It depends on OF graph helpers, DRM bridge/panel/connector helpers, and `rzg2l_du_output_name()`. It is called from `rzg2l_du_kms.c`.

## Risks and Edge Cases

- `rzg2l_du_encoder_count_ports()` treats a single-port DPAD node as a panel; unusual DT graph layouts can alter behavior.
- DPAD has an 83.5 MHz clock cap; other output-specific limits are delegated to downstream bridges.
- Bridge lookup returns `-EPROBE_DEFER` when missing, which bubbles to modeset init.

## Test Signals

DT tests for DPAD panel, DPAD external bridge, DSI bridge, disabled remote nodes, and DPAD clock validation around 83.5 MHz are useful.
