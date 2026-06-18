# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output_7a1000.c

Purpose: implements LS7A1000 DVO/DPI output connectors and encoders.

Important APIs/types/functions: `ls7a1000_output_init`, DPI connector mode/detect helpers, best-encoder helper, and pipe encoder reset callbacks.

Control flow: connector mode probing reads EDID over DDC when available or adds fallback no-EDID modes with 1024x768 preferred. Detect probes DDC or reports unknown without it. Encoder reset programs DVO configuration registers needed for S3 recovery. Output init creates a TMDS encoder, DPI connector with DDC, helper callbacks, attaches connector to encoder, and enables connect/disconnect polling.

State and persistence: encoder/connector live in `lsdc_display_pipe.output`. DVO configuration register state persists across modes until reset or reprogram.

Dependencies and integration points: called by LS7A1000 descriptor; uses DRM EDID/probe helpers, DDC adapter from `lsdc_i2c.c`, and DVO register macros.

Risks and test signals: external encoders are assumed transparent, so non-transparent bridge chips are unsupported. Test EDID and fallback modes, S3 resume display restoration, hotplug polling, and both DVO pipes.
