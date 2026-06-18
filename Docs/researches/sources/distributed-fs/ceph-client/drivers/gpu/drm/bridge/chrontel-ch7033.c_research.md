# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chrontel-ch7033.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chrontel-ch7033.c

## Purpose

This I2C driver programs a Chrontel CH7033 video encoder as a DRM bridge, primarily forwarding to a downstream bridge while optionally creating a connector when the caller does not request connector-less attachment.

## Important APIs, Types, And Functions

`struct ch7033_priv` stores regmap, next bridge, bridge, and connector. Important paths are `ch7033_probe/remove()`, `ch7033_bridge_attach/detach()`, `ch7033_bridge_mode_valid()`, `ch7033_bridge_mode_set()`, `ch7033_bridge_enable/disable()`, connector detect/get-modes helpers, and `ch7033_hpd_event()`.

## Control Flow

Probe finds the downstream panel/bridge on port 1, initializes I2C regmap, validates chip/revision IDs across register pages, and adds the bridge. Attach first attaches the downstream bridge with `NO_CONNECTOR`; if a connector is requested, it initializes local connector helpers, configures polling/HPD based on downstream ops, and attaches the encoder. Mode set switches register pages and writes a long power/timing/PLL/bypass sequence derived from the mode. Enable/disable toggle reset bits on page 4.

## State And Persistence Behavior

State is volatile in regmap and connector/bridge objects. No cached mode is kept; programming happens in mode_set. Register page selection is a hardware side effect and must be correct before writes.

## Dependencies And Integration Points

The driver depends on I2C regmap, DRM bridge/connector helpers, downstream bridge EDID/detect/HPD/DDC support, and OF graph. It uses fallback no-EDID modes when downstream EDID read fails.

## Risks And Test Signals

Risks include dense undocumented register sequences, register page mistakes, ambiguous operator precedence in polarity bit expressions, connector cleanup only when a connector was initialized, and strict mode limits below 1920x1080/165 MHz. Test signals are ID/revision probe success, EDID pass-through, HPD notification from downstream bridge, accepted 1024x768 fallback, and stable HDMI/VGA-style output across modesets.
