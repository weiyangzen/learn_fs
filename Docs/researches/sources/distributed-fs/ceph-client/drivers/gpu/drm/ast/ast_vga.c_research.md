<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vga.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vga.c

## Purpose

`ast_vga.c` creates the DRM DAC encoder and VGA connector for AST devices. It provides BMC-friendly fallback modes when no physical monitor is detected while keeping physical DDC state for epoch changes.

## Important APIs, Types, And Functions

- `ast_vga_output_init(struct ast_device *ast)`: creates DDC, initializes a `DRM_MODE_ENCODER_DAC`, initializes the VGA connector with DDC, sets helper callbacks/polling flags, stores initial physical status, and attaches connector to encoder.
- `ast_vga_connector_helper_detect_ctx()`: reads DDC-based physical status, bumps `connector->epoch_counter` on changes, stores the physical status, and always reports logical connected.
- `ast_vga_connector_helper_get_modes()`: returns EDID modes when physically connected; otherwise clears EDID and adds fallback modes with 1024x768 preferred.
- Standard DRM atomic connector funcs and encoder cleanup.

## Control Flow

The init flow mirrors the SIL164 path: DDC, encoder, connector, helper setup, polling setup, status seed, attach. Detection separates physical status from logical availability. Mode enumeration chooses EDID or no-EDID fallback based on physical status.

## State And Persistence Behavior

`ast_connector->physical_status` and the DRM epoch counter track physical hotplug changes. The file does not directly persist hardware register state.

## Dependencies And Integration Points

It depends on `ast_ddc_create()`, AST output storage, and DRM connector/encoder helpers. It integrates with the AST CRTC through `possible_crtcs`.

## Risks And Edge Cases

Returning connected even when DDC reports disconnected is deliberate for BMC remote-console behavior but can produce modes without a monitor. Error paths return without local cleanup after partial initialization. Fallback maximum mode generation may advertise modes later rejected by hardware-specific mode validation.

## Test Signals

Validate VGA EDID and no-EDID paths, connector polling and epoch changes, fallback preferred mode, atomic modesets with connected and disconnected VGA, and cleanup during driver unload after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vga.c -->
