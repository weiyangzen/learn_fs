<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Kconfig

## Purpose

This Kconfig file defines build options for the Analog Devices ADV7511/ADV7513/ADV7533/ADV7535 HDMI bridge driver and optional audio/CEC support.

## Important APIs, Types, And Symbols

- `DRM_I2C_ADV7511`: tristate main encoder/bridge driver; depends on OF and selects KMS, regmap I2C, MIPI DSI, display helpers, bridge connector, and HDMI state helper support.
- `DRM_I2C_ADV7511_AUDIO`: optional bool for HDMI audio, depends on the main driver and `SND_SOC`, selects `SND_SOC_HDMI_CODEC`.
- `DRM_I2C_ADV7511_CEC`: optional bool for HDMI CEC, depends on the main driver, selects DRM HDMI CEC helper, and defaults to enabled.

## Control Flow

There is no runtime flow. These symbols control which objects from the local Makefile are linked and which optional hooks compile into `adv7511.h`.

## State And Persistence Behavior

The selected symbols persist in kernel configuration and determine module capabilities.

## Dependencies And Integration Points

The main driver integrates with DRM bridge/connector/HDMI helpers, I2C regmap, MIPI DSI for ADV7533/7535, ASoC HDMI codec for audio, and DRM HDMI CEC helper for CEC.

## Risks And Edge Cases

Audio and CEC are bool options tied to the main driver rather than separate modules. Enabling ADV7533 support selects MIPI DSI even when only ADV7511 parallel RGB hardware is used. CEC defaults on, so missing CEC clock/device-tree support must degrade gracefully.

## Test Signals

Build matrix for main only, main+audio, main+CEC, and all enabled; probe on ADV7511 and ADV7533/7535 device trees; HDMI audio and CEC adapter registration tests validate the options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Kconfig -->
