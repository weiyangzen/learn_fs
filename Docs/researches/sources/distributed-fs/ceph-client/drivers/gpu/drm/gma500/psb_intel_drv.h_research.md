# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_drv.h

## Purpose
This header defines the shared Intel-style display abstractions used by GMA500 output, CRTC, connector, and I2C code. It bridges DRM core objects to GMA500-specific encoder/connector/CRTC/private mode state.

## Important APIs, Types, and Functions
Important definitions include output type constants, clone bits, `INTELFB_CONN_LIMIT`, `struct psb_intel_mode_device`, `struct gma_i2c_chan`, `struct gma_encoder`, `struct gma_connector`, `struct psb_intel_crtc_state`, and `struct gma_crtc`. It provides container macros and declarations for I2C creation, DDC modes, CRTC init/readback, SDVO/LVDS/Oaktrail LVDS, best encoder, connector attachment, LVDS property/mode helpers, GMBUS helpers, and CDV DP/audio/color property helpers.

## Control Flow
There is no executable flow. Runtime display flow uses these structs to attach encoders to connectors, map outputs to CRTCs, preserve panel fixed modes, and dispatch helper callbacks.

## State and Persistence Behavior
The declared structs persist display state: panel fixed modes and backlight duty in `psb_intel_mode_device`, GPIO I2C bus data in `gma_i2c_chan`, output type/private pointers in `gma_encoder`, save/restore callbacks in `gma_connector`, and pipe/cursor/LUT/modes/page-flip state in `gma_crtc`.

## Dependencies and Integration Points
It depends on Linux I2C, DRM CRTC/encoder/probe/vblank headers, and `gma_display.h`. It is included by display, LVDS, SDVO, HDMI, I2C, and core driver code.

## Risks
The header exposes output internals broadly, so ownership of fields such as `connector->ddc`, `gma_encoder->dev_priv`, and `lvds_i2c_bus` must be consistent across output implementations. Some comments note legacy or FIXME areas, including shared SDVO/LVDS I2C ownership and display-private placement.

## Test Signals
Build coverage across all output implementations, correct connector-to-encoder attachment, valid container macro usage, mode device fixed-mode propagation, and successful GMBUS/I2C/LVDS/SDVO/HDMI integration.
