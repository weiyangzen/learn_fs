<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_sil164.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_sil164.c

## Purpose

`ast_sil164.c` creates the DRM encoder and connector for AST boards with a Silicon Image SIL164 TMDS/DVI transmitter. It mirrors the AST VGA connector behavior while using a DVI-I connector type and a TMDS encoder.

## Important APIs, Types, And Functions

- `ast_sil164_output_init(struct ast_device *ast)`: creates an AST DDC adapter, initializes `ast->output.sil164.encoder`, initializes the DVI-I connector with DDC, adds helper callbacks, sets polling flags, and attaches the connector to the encoder.
- `ast_sil164_connector_helper_detect_ctx()`: probes physical DDC status, updates `ast_connector->physical_status`, bumps `connector->epoch_counter` on physical changes, but always returns logical `connector_status_connected`.
- `ast_sil164_connector_helper_get_modes()`: uses EDID modes when the physical connector is connected; otherwise clears EDID and installs no-EDID fallback modes up to 4096x4096 with 1024x768 preferred.
- Static encoder/connector funcs use DRM atomic state helpers and standard cleanup.

## Control Flow

Initialization is DDC creation, encoder creation, connector creation, helper addition, property setup, physical-status initialization, and encoder attachment. Detection intentionally separates physical DDC state from logical connector state so BMC display paths remain available without a monitor. Mode enumeration follows that physical status to decide between EDID and fallback modes.

## State And Persistence Behavior

The file stores connector state in `ast_connector->physical_status` and increments the DRM connector epoch counter when physical DDC status changes. DRM core owns connector/encoder lifetime after initialization. No hardware registers are directly programmed here.

## Dependencies And Integration Points

It depends on AST DDC creation, `struct ast_device` output storage, and DRM connector/encoder helper APIs. It integrates with the AST single CRTC through `possible_crtcs = drm_crtc_mask(crtc)`.

## Risks And Edge Cases

Always reporting connected is intentional for server/BMC usability but can surprise generic hotplug assumptions. If `drm_encoder_init()` succeeds and connector init later fails, cleanup relies on higher-level resource management; this local function simply returns the error. Fallback mode generation must remain compatible with AST hardware limits enforced elsewhere.

## Test Signals

Test with SIL164 hardware connected and disconnected, verify EDID modes when DDC succeeds, verify 1024x768 preferred fallback without EDID, monitor connector epoch changes across plug/unplug, and run DRM atomic modeset and hotplug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_sil164.c -->
