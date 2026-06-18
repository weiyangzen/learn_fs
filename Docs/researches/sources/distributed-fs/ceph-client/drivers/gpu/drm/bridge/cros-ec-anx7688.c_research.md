# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cros-ec-anx7688.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cros-ec-anx7688.c

## Purpose

This lightweight I2C DRM bridge represents a ChromeOS EC-managed ANX7688 HDMI-to-DisplayPort bridge. It validates device identity and, on newer firmware, filters modes by available DP bandwidth and lane count reported by EC registers.

## Important APIs, Types, And Functions

`struct cros_ec_anx7688` stores I2C client, regmap, bridge, and a `filter` flag. The key functions are `cros_ec_anx7688_bridge_probe/remove()` and `cros_ec_anx7688_bridge_mode_fixup()`.

## Control Flow

Probe allocates the bridge, initializes 8-bit regmap, bulk-reads vendor/device IDs, rejects unexpected IDs, reads firmware version, enables mode filtering for firmware 0.85 or newer, and adds the bridge. Mode fixup returns true unless filtering is enabled; then it reads bandwidth and lane count, validates maximum supported values, computes total 8b/10b DP bandwidth, computes required 8bpc RGB bandwidth from pixel clock, and rejects modes that exceed available bandwidth.

## State And Persistence Behavior

Runtime state is only the regmap and firmware-derived `filter` boolean. No hardware programming is performed by this driver.

## Dependencies And Integration Points

It integrates as a DRM bridge with legacy `.mode_fixup`, I2C regmap, and OF compatible `"google,cros-ec-anx7688"`. It assumes EC firmware owns actual ANX7688 configuration.

## Risks And Test Signals

Risks include accepting all modes on old firmware or zero bandwidth/lane reads, fixed 8bpc RGB bandwidth calculations, and no HPD/EDID handling in this file. Test signals are correct ID/version logs, rejection of oversized modes with new firmware, and compatibility with old firmware where filtering is intentionally disabled.
