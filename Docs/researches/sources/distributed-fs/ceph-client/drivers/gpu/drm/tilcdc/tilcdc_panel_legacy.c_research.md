# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_panel_legacy.c

## Purpose

`tilcdc_panel_legacy.c` provides boot-time compatibility for deprecated `ti,tilcdc,panel` device-tree bindings. It applies an embedded overlay that creates a modern panel-dpi node, copies panel and timing properties from the legacy node, translates selected panel-info flags, and disables matching on the legacy node.

## Important APIs, Types, and Functions

- Embedded symbols `__dtbo_tilcdc_panel_legacy_begin/end` identify the built-in DT overlay blob.
- `tilcdc_panel_update_prop()` allocates and queues a property update in an OF changeset.
- `tilcdc_panel_copy_props()` selects native timing, copies panel properties except `compatible`, creates `panel-timing`, copies timing properties, translates `invert-pxl-clk` and `sync-edge` to `pixelclk-active` and `syncclk-active`, removes the old compatible property, and applies the changeset.
- `tilcdc_panel_legacy_init()` finds tilcdc and legacy panel nodes, applies the overlay, finds the new panel node, copies properties, and removes the overlay on failure.
- `subsys_initcall()` runs the conversion early in boot.

## Control Flow

If both tilcdc and legacy panel nodes exist and are available, the initcall applies the embedded overlay, locates `tilcdc-panel-dpi`, migrates properties, and leaves the live DT in a state consumable by standard `panel-dpi`/bridge code. If migration fails after overlay apply, the overlay is removed.

## State and Persistence Behavior

The live device tree is mutated for the remainder of boot. Allocated properties are owned by OF changeset/DT infrastructure after apply. The legacy node's `compatible` is removed to prevent old driver matching.

## Dependencies and Integration Points

The file depends on OF core, OF overlay, wrapped DTBO symbols from the Makefile, and simple-panel expectations for `panel-dpi`. It is enabled by `DRM_TILCDC_PANEL_LEGACY`.

## Risks and Edge Cases

- `of_changeset_apply()` return is ignored in `tilcdc_panel_copy_props()`.
- If `of_find_property(old_panel, "compatible", NULL)` returns NULL, removal behavior depends on OF changeset validation.
- Property copy is broad and may migrate legacy-only properties that modern panel-dpi ignores or misinterprets.
- The code assumes one matching LCDC and one matching legacy panel.
- Endianness conversion is handled for generated boolean-like timing values, but copied properties retain original representation.

## Test Signals

Boot tests should cover legacy DT with native-mode phandle, legacy DT without native-mode, missing `display-timings`, missing `panel-info`, unavailable LCDC/panel nodes, overlay apply failure, property-copy allocation failures, and successful creation of a usable panel-dpi bridge for tilcdc probe.
