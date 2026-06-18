# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_vga.c

## Purpose
Initializes a standard VGA connector and DAC encoder for non-BMC mgag200 outputs.

## Important APIs, types, and functions
- Encoder funcs use `drm_encoder_cleanup`.
- Connector helper funcs use generic DDC mode probing and DDC-based detect.
- Connector funcs use atomic reset/duplicate/destroy and standard fill modes.
- `mgag200_vga_output_init()` creates encoder, DDC adapter, connector, polling, and encoder attachment.

## Control flow
Output init creates a DAC encoder, restricts it to the single CRTC, creates the DDC bit-bang adapter, initializes a VGA connector with DDC, adds helper funcs, enables connect/disconnect polling, and attaches connector to encoder.

## State and persistence
The encoder and connector are embedded in `mdev->output.vga` and persist for the DRM device lifetime. The DDC adapter is DRM-managed.

## Dependencies and integration points
Used by original G200 PCI/AGP pipeline initialization. Depends on DRM connector/encoder helpers and `mgag200_ddc_create()`.

## Risks
Unlike the BMC-aware path, no fallback connected status or no-EDID modes are added. Systems without EDID may appear disconnected.

## Test signals
EDID detection, hotplug polling, connector mode listing, and successful encoder attachment on original G200 hardware are primary signals.
