# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/parallel-display.c

## Purpose
Implements the i.MX IPUv3 parallel DPI display component. It bridges the IPU display interface to a downstream panel/bridge, negotiates bus formats and flags, supports legacy `interface-pix-fmt` device-tree overrides, and creates a bridge connector.

## Important APIs, types, and functions
- `struct imx_parallel_display` stores the selected bus format, next bridge, local bridge, and device pointer.
- Bridge callbacks include `imx_pd_bridge_attach()`, `imx_pd_bridge_atomic_check()`, `imx_pd_bridge_atomic_get_input_bus_fmts()`, and `imx_pd_bridge_atomic_get_output_bus_fmts()`.
- `imx_pd_bind()` creates the DRM encoder and bridge connector.
- `imx_pd_probe()` resolves the downstream bridge or legacy bridge, parses `interface-pix-fmt`, registers the local bridge, and adds the component.

## Control flow
Probe allocates a DRM bridge, looks for the output bridge at port 1, falls back to an i.MX legacy DPI bridge when no graph bridge exists, maps legacy string formats such as `rgb24`, `rgb565`, `bgr666`, and `lvds666` to media bus formats, registers the local bridge, and joins the component framework. Bind allocates a simple encoder, parses possible CRTCs, attaches the local bridge without a connector, creates a bridge connector, and attaches it.

During bus negotiation, output formats come from the legacy override, downstream display info, or the local supported list. Input formats validate the requested output and prefer the legacy DT format when it differs from the downstream output, preserving old board descriptions with physical swizzling. Atomic check copies downstream bus flags into both bridge bus configs and into `imx_crtc_state`, along with the selected input bus format and DI pins 2/3.

## State and persistence
The only persistent runtime setting is `imxpd->bus_format`, parsed from device tree or zero when negotiated from the panel. Per-commit bus format/flags persist in bridge state and `imx_crtc_state`.

## Dependencies and integration points
Depends on DRM bridge connector helpers, OF graph bridge lookup, i.MX legacy bridge support, and `imx_drm_encoder_parse_of()`. It integrates with the IPUv3 CRTC by supplying bus format, flags, and DI pins through atomic check.

## Risks
Legacy `interface-pix-fmt` can intentionally override the panel format, so changing precedence can break old DTs. Unsupported bus formats return no input formats or fail atomic check. `drm_bridge_attach()` in bind is not checked for failure in the current code path, so downstream attach issues could surface later.

## Test signals
Test cases should include graph bridges, legacy bridge fallback, each legacy pixel-format string, panel-provided bus formats, unsupported format rejection, bus flag propagation, probe deferral, and connector creation for DPI panels.
