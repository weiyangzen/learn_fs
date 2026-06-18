<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,split.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,split.yaml

### Purpose
This schema defines MediaTek SPLIT blocks, which divide one display stream into multiple outputs for split-panel or multi-pipeline operation.

### Important APIs, Types, And Functions
The binding includes `compatible`, one `reg`, one interrupt, power-domain and clock resources, optional `mediatek,gce-client-reg`, and graph `ports`. The graph describes one input and multiple possible downstream outputs.

### Control Flow
Validation is compatible/resource based. Display data flow is declarative: incoming pixels are split through graph endpoints toward downstream pipeline halves.

### State, Persistence, And Dependencies
DT persists the split block resources and topology. Dependencies include MMSYS/VDOSYS routing, GCE, clock/power providers, interrupt controllers, graph bindings, and downstream paired display components.

### Integration Points
MediaTek DRM uses SPLIT in dual-pipeline modes where one logical display stream must be processed by parallel hardware paths before merge, DSC, DSI, or panel output.

### Risks
Split pipelines are highly order-sensitive. A missing endpoint may only affect high-resolution or dual-link modes. GCE metadata and compatible fallback must match the SoC to keep atomic commits synchronized.

### Test Signals
Use binding checks and graph validation. Runtime tests should cover split-panel modes, dual-output route construction, atomic commits across both halves, and fallback to non-split modes where the hardware supports it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,split.yaml -->
