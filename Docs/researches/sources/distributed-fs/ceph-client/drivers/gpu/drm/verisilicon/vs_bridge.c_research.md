<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.c

## Purpose
`vs_bridge.c` implements the VeriSilicon output bridge layer between a DC CRTC and a downstream DRM bridge. It detects DPI versus DP graph endpoints, exposes bus-format negotiation, programs panel/DP/DPI output registers, creates an encoder and bridge connector, and wires the output into atomic KMS.

## Important APIs, Types, and Functions
Key entry point: `vs_bridge_init(struct drm_device *drm_dev, struct vs_crtc *crtc)`. Important helpers include `vs_bridge_attach()`, DPI/DP bus-format callbacks, `vs_bridge_atomic_check_dp()`, `vs_bridge_enable_common()`, `vs_bridge_atomic_enable_dpi()`, `vs_bridge_atomic_enable_dp()`, `vs_bridge_atomic_disable()`, and `vs_bridge_detect_output_interface()`. `struct vsdc_dp_format` maps Linux media-bus formats to VSDC DP register fields and YUV state.

## Control Flow
Initialization probes the device-tree graph for a remote endpoint on the CRTC output's DPI port and then DP port. It obtains the downstream bridge, allocates a `struct vs_bridge`, chooses DPI or DP bridge funcs, allocates a plain encoder, assigns the possible CRTC mask, registers and attaches the local bridge without creating a connector, then creates a bridge connector and attaches it to the encoder. Atomic enable programs either DPI RGB888 or DP format/YUV bits, applies bus polarity flags, enables DE/data/clock output, starts the panel, and commits panel config. Disable clears running bits and commits.

## State and Persistence Behavior
Persistent state is `struct vs_bridge`: the DRM bridge base, encoder, connector, CRTC pointer, downstream bridge pointer, and output interface type. Hardware state persists in display panel, DPI, and DP config registers until disabled or reprogrammed. There is no separate cache of bus format beyond DRM bridge state.

## Dependencies and Integration Points
The file depends on OF graph helpers, DRM bridge/encoder/connector helpers, `drm_bridge_connector`, media-bus format constants, regmap access to DC registers, `vs_crtc` output IDs, and register definitions in `vs_bridge_regs.h`. It is invoked by `vs_drm_initialize()` after each CRTC is created.

## Risks
Only DPI RGB888 is advertised for DPI. DP bus format support must remain synchronized between the format table, input/output callbacks, atomic check, and register programming. Device-tree port numbering is part of the ABI. `drm_bridge_attach()` and connector creation failures abort the whole DRM initialization. Common enable uses bus flag polarity interpretation that should be verified against downstream bridge expectations.

## Test Signals
Tests should cover DT graphs with DPI, DP, missing endpoints, and `-EPROBE_DEFER`; DP RGB/YUV media-bus format negotiation; atomic enable register programming; disable sequencing; connector creation; and modeset operation with bridge chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.c -->
