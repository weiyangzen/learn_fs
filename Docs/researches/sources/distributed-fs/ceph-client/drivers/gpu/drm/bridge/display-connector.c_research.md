# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/display-connector.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/display-connector.c

## Purpose

This platform driver models physical display connectors as terminal DRM bridges. It supplies connector type, HPD, DDC/EDID, optional connector power, and bus-format pass-through for simple DT-described connectors.

## Important APIs, Types, And Functions

`struct display_connector` stores bridge, HPD GPIO/IRQ, power regulator, and HDMI DDC-enable GPIO. Main functions are `display_connector_probe/remove()`, `display_connector_attach()`, `display_connector_detect()`, `display_connector_edid_read()`, HPD IRQ handler, and bus-format forwarding helpers.

## Control Flow

Probe derives connector type from compatible and properties, handles DVI analog/digital and HDMI type variants, enables interlace/Y420 allowances, gets optional HPD GPIO/IRQ, DDC I2C adapter, DP/HDMI power supplies, and DDC-enable GPIO, enables power, sets bridge ops according to available HPD/DDC, and adds the bridge. Attach only supports `DRM_BRIDGE_ATTACH_NO_CONNECTOR`. Detect prefers HPD GPIO, then DDC probe, then connector-type-specific unknown/disconnected fallback. Bus format helpers forward to the previous bridge if possible or return connector/fixed fallback formats.

## State And Persistence Behavior

State is static connector resources and enabled supply/DDC GPIO. There is no mode cache or persistent storage. Remove disables DDC/power, removes the bridge, and releases DDC adapter reference.

## Dependencies And Integration Points

It depends on platform OF match data, GPIO, IRQ, regulator, I2C adapter lookup, DRM bridge EDID/detect/HPD ops, and media bus formats. It supports composite, DVI, HDMI, S-Video, VGA, and DP compatibles.

## Risks And Test Signals

Risks include resource leaks if probe fails after enabling a regulator, DP detection requiring DPCD elsewhere, connector type property errors, and fallback bus formats that may hide negotiation bugs. Test signals are HPD IRQ notifications, EDID reads over DDC, correct detection semantics per connector type, and power rails toggling on remove.
