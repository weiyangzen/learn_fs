# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_encoder.c

## Purpose

`tidss_encoder.c` creates the DRM encoder and bridge-connector chain for each TIDSS video port. It provides a small internal bridge that extracts display bus format/flags during atomic checks and forwards attach operations to the next bridge or panel bridge.

## Important APIs, Types, and Functions

- `struct tidss_encoder` embeds a DRM bridge, DRM encoder, connector pointer, next bridge pointer, and parent `struct tidss_device`.
- `tidss_bridge_attach()` attaches the next bridge after the TIDSS bridge.
- `tidss_bridge_atomic_check()` determines the input bus format and bus flags from the next bridge state or connector display info and stores them in `struct tidss_crtc_state`.
- `tidss_encoder_create()` allocates the bridge wrapper, initializes a simple encoder, attaches the bridge without creating a connector, creates a `drm_bridge_connector`, and attaches that connector to the encoder.

## Control Flow

`tidss_kms.c` discovers panel/bridge endpoints per VP, then calls `tidss_encoder_create()` after creating the corresponding CRTC. During atomic check, bridge state propagation runs before CRTC programming; this file writes `bus_format` and `bus_flags` into the TIDSS CRTC state so `dispc_vp_bus_check()` and `dispc_vp_prepare()` can program data width and polarities.

## State and Persistence Behavior

The encoder/bridge wrapper is devm/drmm managed and persists for the DRM device lifetime. The connector pointer is stored for ownership/reference only after `drm_bridge_connector_init()`. The bus format is not persistent in the encoder; it is copied into each atomic CRTC state.

## Dependencies and Integration Points

The file depends on DRM bridge, bridge connector, atomic helper bridge state, simple encoder helpers, connector display info, and `tidss_crtc_state`. It integrates with `tidss_kms.c` for creation and `tidss_dispc.c` for later VP bus programming.

## Risks and Edge Cases

- If neither the next bridge state nor connector display info provides bus formats, atomic check fails.
- Only the first connector bus format is used when there is no next bridge state.
- Bridge attach requires the caller to pass `DRM_BRIDGE_ATTACH_NO_CONNECTOR` semantics through the chain.
- Encoder type is supplied by KMS setup and must match bus type/panel connector type.

## Test Signals

Tests should cover panel bridge and external bridge chains, atomic bus-format negotiation, missing bus-format errors, connector attach failures, LVDS/DPI encoder type selection from KMS setup, and mode commits where bus flags affect VP polarity.
