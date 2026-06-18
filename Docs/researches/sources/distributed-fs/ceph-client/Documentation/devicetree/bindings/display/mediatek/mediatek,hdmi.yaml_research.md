<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi.yaml

### Purpose
This binding describes legacy MediaTek HDMI encoders capable of producing HDMI 1.4a or MHL 2.0 signals from a parallel input.

### Important APIs, Types, And Functions
The schema defines `compatible`, one `reg`, one interrupt, four clocks named `pixel`, `pll`, `bclk`, and `spdif`, one HDMI PHY named `hdmi`, `mediatek,syscon-hdmi`, and graph `ports`. `port@0` receives DPI output, while `port@1` connects to an HDMI connector or external bridge.

### Control Flow
Validation is fixed-resource and graph-oriented. The required set ensures the encoder has clocks, PHY, syscon, and two display endpoints. No conditional runtime logic is implemented in the YAML.

### State, Persistence, And Dependencies
Persistent state is the DT hardware contract. Dependencies include MMSYS syscon registers, HDMI PHY, clock providers, interrupt routing, graph bindings, connector/bridge nodes, and often the separate HDMI DDC node.

### Integration Points
The MediaTek HDMI driver binds this encoder into DRM through its DPI input and connector/bridge output. Audio-related clocks support S/PDIF and bit-clock paths.

### Risks
Clock order and names are critical. Missing `mediatek,syscon-hdmi` prevents register integration with system configuration. The output endpoint description allows connector or bridge targets, so board DTS must match the actual DDC and hotplug topology.

### Test Signals
Binding checks should validate required clocks, PHY, syscon, and ports. Runtime signals are PHY attach, EDID over DDC, hotplug detection, HDMI modeset, and audio clock availability where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi.yaml -->
