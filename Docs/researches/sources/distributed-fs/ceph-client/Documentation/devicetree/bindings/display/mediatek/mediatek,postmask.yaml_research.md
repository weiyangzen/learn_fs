<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,postmask.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,postmask.yaml

### Purpose
This schema describes MediaTek POSTMASK display blocks, which apply post-processing masks in the display pipeline before later color or output stages.

### Important APIs, Types, And Functions
The binding exposes SoC/fallback `compatible` values, one `reg`, one interrupt, power-domain and clock resources, optional `mediatek,gce-client-reg`, and graph `ports`. Ports describe input from upstream display processing and output to blocks such as DITHER.

### Control Flow
The schema validates compatible fallback order, required resources, and optional graph topology. There is no imperative control flow.

### State, Persistence, And Dependencies
The DT node persists MMIO, interrupt, power, clock, GCE, and graph data. Dependencies include MMSYS/VDOSYS, GCE definitions, graph schemas, and the display component driver.

### Integration Points
POSTMASK is inserted into MediaTek DRM routes as a display component and can be programmed through normal atomic update paths, including GCE where present.

### Risks
Since POSTMASK often sits between other color-processing blocks, wrong endpoint ordering can alter visual output while still producing a picture. GCE offsets and compatible fallback must match the SoC register map.

### Test Signals
Use `dt_binding_check` and DTS graph validation. Runtime signals include component bind, route construction with POSTMASK between expected neighbors, mask programming, and successful suspend/resume of power and clock resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,postmask.yaml -->
