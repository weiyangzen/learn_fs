<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi.yaml

### Purpose
This schema defines the MT8195-series HDMI-TX encoder. It is the newer HDMI transmitter binding for MT8195 display pipelines.

### Important APIs, Types, And Functions
The API includes `compatible`, `reg`, interrupts, clocks and names, power domains, graph `ports`, and an `allOf` reference to `sound/dai-common.yaml`. The input port is fed by a display pipeline component, and the output port connects to a connector or bridge.

### Control Flow
The schema is declarative. Required resources must be present before the transmitter can bind. The `allOf` sound reference validates HDMI audio DAI properties when present.

### State, Persistence, And Dependencies
Persistent state is the hardware description for MMIO, interrupts, clocks, PM domains, graph links, and optional audio DAI metadata. Dependencies include display clock/power providers, graph schemas, connector/bridge nodes, the MT8195 HDMI DDC binding, and sound DAI common rules.

### Integration Points
The MT8195 HDMI driver participates in DRM as an encoder/bridge and can expose audio through the sound DAI path. It consumes display input and publishes an output edge to board-level HDMI connectivity.

### Risks
The MT8195 binding differs from older MediaTek HDMI, so copying legacy PHY/syscon/DDC assumptions can create invalid or nonfunctional nodes. Audio properties must remain aligned with the DAI schema.

### Test Signals
Validate with `dt_binding_check`. Runtime checks include HDMI TX probe, DDC/EDID operation through its paired DDC node, connector modeset, power-domain transitions, and optional DAI registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi.yaml -->
