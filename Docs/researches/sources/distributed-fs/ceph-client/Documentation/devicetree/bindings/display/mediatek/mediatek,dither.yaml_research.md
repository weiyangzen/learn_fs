<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dither.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dither.yaml

### Purpose
This YAML schema describes MediaTek display DITHER blocks, which reduce visible color-depth loss by approximating unavailable colors. The node is part of the MediaTek display pipeline and is expected to sit beside the central MMSYS configuration node.

### Important APIs, Types, And Functions
The binding API is the node contract: SoC-specific `compatible` strings, one MMIO `reg`, one interrupt, a power domain, one DITHER clock, optional `mediatek,gce-client-reg`, and optional graph `ports`. The graph exposes `port@0` as input, usually from POSTMASK or GAMMA, and `port@1` as output toward DSC, DP_INTF, DSI, LVDS, or another pipeline block.

### Control Flow
There is no executable control flow. Validation branches through `compatible.oneOf`: `mt8183` can stand alone, while several later SoCs must list their SoC string followed by the `mediatek,mt8183-disp-dither` fallback. Graph validation requires both input and output ports when `ports` is present.

### State, Persistence, And Dependencies
The persistent state is the devicetree description consumed at boot. Dependencies are MMSYS placement, power-domain providers, clock providers, interrupt controllers, graph endpoints, and optionally GCE command-engine metadata.

### Integration Points
The DRM/MediaTek display driver uses this node to discover the dither hardware and connect it into the component graph. GCE registration lets command queues program the block without synchronous CPU register writes.

### Risks
Incorrect fallback compatibles can bind the wrong register layout. Missing graph endpoints can leave a valid MMIO node disconnected from the display route. GCE tuple mistakes are hard to catch by schema because the referenced subsys IDs are chip-specific.

### Test Signals
Run `dt_binding_check` and SoC DTS checks for required `reg`, interrupt, power, and clock cells. Runtime signals are successful DRM component bind, valid graph endpoint resolution, and working low-bpp output without color-band artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dither.yaml -->
