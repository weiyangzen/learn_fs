# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_encoders.c

## Purpose

`radeon_encoders.c` provides common encoder and connector helper logic for Radeon display setup. It derives clone masks, maps firmware-supported device bits and DAC selections to Atom encoder object IDs, links encoders to connectors, initializes backlight support, resolves active connectors/external encoders, adjusts panel modes to native timing, determines dual-link requirements, and classifies digital encoders.

## Important APIs, Types, and Functions

- `radeon_setup_encoder_clones()` sets `possible_clones` for all encoders through `radeon_encoder_clones()`.
- `radeon_get_encoder_enum()` maps Atom device support masks and DAC numbers to encoder enum IDs, with family-specific exceptions.
- `radeon_link_encoder_connector()` attaches matching encoders to connectors and invokes backlight setup for LCD devices.
- `radeon_encoder_set_active_device()`, `radeon_get_connector_for_encoder()`, and `radeon_get_connector_for_encoder_init()` maintain or query the active device mask relationship.
- `radeon_get_external_encoder()` and `radeon_encoder_get_dp_bridge_encoder_id()` find external bridge encoders such as Travis/Nutmeg.
- `radeon_panel_mode_fixup()` replaces adjusted mode timing with native panel timing while preserving blank/sync relationships.
- `radeon_dig_monitor_is_duallink()` and `radeon_encoder_is_digital()` answer link capability/type questions used by mode validation and encoder programming.

## Control Flow

After BIOS connector/encoder objects are created, display setup calls clone configuration and later links encoders to connectors by intersecting Radeon device masks. When an LCD encoder is linked, `radeon_encoder_add_backlight()` applies module-parameter and quirk logic, initializes Atom or legacy native backlight if allowed, and falls back to ACPI video backlight registration if no native encoder is active. During modeset, active connector selection updates `active_device`, panel mode fixup copies native timing into the adjusted mode, and dual-link checks inspect connector type, HDMI status, DP sink type, ASIC generation, and pixel clock thresholds.

## State and Persistence Behavior

State is stored in DRM encoder/connector objects and Radeon extensions: `possible_clones`, `radeon_encoder->active_device`, `devices`, `native_mode`, backlight encoder state in `rdev->mode_info.bl_encoder`, and connector private DP sink data. The file also reads global `radeon_backlight`.

## Dependencies and Integration Points

The helpers depend on DRM mode objects, EDID display info, ACPI video backlight, Atom object IDs, legacy encoder code, family macros, and `radeon_display.c` connector setup. Atom/legacy mode-set files consume the helper answers when programming encoder hardware.

## Risks and Edge Cases

- Clone restrictions are conservative and family-specific; incorrect device masks from BIOS can attach wrong encoders.
- Backlight selection mixes module parameter, quirks, compile-time PPC behavior, native init success, and ACPI fallback.
- `radeon_dig_monitor_is_duallink()` assumes connector lookup succeeds; malformed topology could produce NULL dereference risk.
- HDMI 1.3 340 MHz threshold is only used for DCE6+ HDMI displays; other hardware uses 165 MHz.

## Test Signals

Test BIOS topologies with LVDS, DVI-I, HDMI, DP/eDP, TV/CV, external bridges, clone configurations on pre-R600, backlight module parameter modes, ACPI fallback, dual-link decisions around 165/340 MHz, and panel native-mode fixups.
