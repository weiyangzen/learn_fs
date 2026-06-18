<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsc.yaml

### Purpose
This schema defines MediaTek Display Stream Compression blocks. DSC compresses display stream slices before high-bandwidth output links such as DSI or DisplayPort.

### Important APIs, Types, And Functions
The node API includes supported `compatible` strings, one `reg`, one interrupt, power-domain and clock resources, optional `mediatek,gce-client-reg`, and graph `ports`. The ports describe input from an upstream block such as DITHER/MERGE and output to the next display interface.

### Control Flow
Schema control is compatible-driven and graph-driven. Validation accepts defined SoC/fallback compatible combinations, constrains resources to single MMIO/clock/interrupt entries, and requires the graph shape when `ports` is supplied.

### State, Persistence, And Dependencies
The devicetree node persists the hardware instance identity and command-queue register window. Dependencies include MMSYS topology, GCE command engine definitions, clock/power providers, interrupt controllers, and graph bindings.

### Integration Points
MediaTek DRM uses DSC components in multi-stage display pipelines, especially high-resolution DSI/DP modes where compression is needed. The block is coordinated with slice-producing upstream blocks and compressed-stream consumers.

### Risks
DSC blocks are sensitive to topology. A valid node with wrong endpoint routing can lead to bandwidth or mode failures. Fallback-compatible mistakes may hide register-layout differences. Missing GCE metadata can reduce command-queue support for atomic updates.

### Test Signals
Use binding checks for resource and graph validation. Runtime signals are component bind, command-queue programming where available, successful DSC-enabled modes, and correct behavior across compressed and uncompressed display routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsc.yaml -->
