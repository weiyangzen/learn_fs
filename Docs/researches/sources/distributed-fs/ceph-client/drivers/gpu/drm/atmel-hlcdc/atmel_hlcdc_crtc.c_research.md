<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_crtc.c

## Purpose

`atmel_hlcdc_crtc.c` implements the DRM CRTC for Atmel/Microchip HLCDC and XLCDC display controllers. It validates modes, programs global timing/output registers, controls enable/disable sequencing, handles vblank/page-flip events, and creates the CRTC around the primary/cursor planes.

## Important APIs, Types, And Functions

- `struct atmel_hlcdc_crtc_state`: extends DRM CRTC state with selected output mode and XLCDC DPI flag.
- `struct atmel_hlcdc_crtc`: wraps `drm_crtc`, links the device controller, stores pending vblank event, and CRTC id.
- `atmel_hlcdc_crtc_mode_set_nofb()`: converts adjusted DRM timing into HLCDC CFG registers, selects pixel-clock divider/source, applies bus clock polarity, and writes output mode/sync polarity/DPI bits.
- `atmel_hlcdc_crtc_atomic_check()`: selects output bus format, prepares discard area, and balances AHB routing across planes.
- `atmel_hlcdc_crtc_atomic_enable()` and `_disable()`: sequence runtime PM, pinctrl, system clock, pixel clock, sync/display enables, and XLCDC CM/SD bits with status polling.
- `atmel_hlcdc_crtc_irq()`: handles SOF vblank and completes pending page-flip events.
- `atmel_hlcdc_crtc_create()`: picks base/cursor planes from layer descriptors, allocates the CRTC, assigns overlay `possible_crtcs`, and enables gamma/color-management support.

## Control Flow

Modeset programming starts by locating the active encoder/connector to read bus flags, then writes sync, porch, display size, clock divider, polarity, and output mode registers. Atomic check first intersects or unions connector-supported output formats according to SoC constraints, then delegates plane preparation. Enable and disable use ordered register writes plus `regmap_read_poll_timeout()` to wait for clock/sync/display status transitions; XLCDC adds CM/SD sequencing. Atomic flush transfers a pending event to private state under `event_lock`, and the IRQ path sends it after vblank.

## State And Persistence Behavior

Persistent software state includes extended CRTC state fields, pending page-flip event pointer, CRTC id, and `dc->crtc`. Hardware state persists in HLCDC CFG, EN/DIS/SR, interrupt, clock, sync, display, output-mode, and XLCDC-specific registers. Runtime PM forbids suspend while enabled and allows it again on disable.

## Dependencies And Integration Points

The file depends on Linux clocks, pinctrl, runtime PM, regmap, MFD HLCDC register definitions, videomode/DRM atomic helpers, and local plane/output helpers. It integrates with connector bus formats through `atmel_hlcdc_encoder_get_bus_fmt()` and with plane state through `atmel_hlcdc_plane_prepare_disc_area()` and `atmel_hlcdc_plane_prepare_ahb_routing()`.

## Risks And Edge Cases

Clock divider selection trades higher/lower error and may clamp when the divider field overflows. `connector` may be absent, so bus flags are optional. Output format selection can fail if connectors have no common format on SoCs with conflicting formats. Poll timeouts only warn, leaving the disable/enable path to continue. Page-flip event handling assumes vblank get succeeds; `WARN_ON` catches anomalies.

## Test Signals

Mode validation for porch/sync bounds, atomic commits across RGB bus widths and DSI encoders, suspend/resume while enabled, vblank/page-flip completion, clock divider accuracy, XLCDC and legacy HLCDC enable/disable tests, and multi-plane atomic checks are important validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_crtc.c -->
