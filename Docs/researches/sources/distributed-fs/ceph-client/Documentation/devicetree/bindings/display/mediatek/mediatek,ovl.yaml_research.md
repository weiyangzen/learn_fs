<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl.yaml

### Purpose
This binding describes MediaTek full overlay blocks. OVL reads memory-backed layers and alpha-blends them into the display pipeline.

### Important APIs, Types, And Functions
The schema includes many SoC/fallback compatible combinations, one `reg`, one interrupt, power-domain, one OVL clock, required `iommus`, optional GCE register metadata, and optional graph `ports`. `port@0` is input from MMSYS or VDOSYS routing; `port@1` outputs to COLOR, RDMA, or WDMA.

### Control Flow
Compatible `oneOf` entries encode hardware-generation fallback rules, including display and MDP3 OVL variants. Required IOMMU and clock/power resources ensure the driver has memory and display access. Graph ports encode pipeline flow.

### State, Persistence, And Dependencies
Persistent state is the DT description of blending hardware and its memory-master identity. Dependencies include MediaTek IOMMU, display clock and PM domains, interrupts, GCE, graph schemas, and MMSYS placement.

### Integration Points
OVL is a primary DRM plane-composition block in MediaTek display pipelines. It can feed display output or WDMA capture paths.

### Risks
Confusing display OVL and MDP3 OVL compatibles may select wrong driver capabilities. IOMMU master IDs are SoC-specific and critical. Pipeline routes with OVL-to-WDMA versus OVL-to-display need explicit graph review.

### Test Signals
Binding checks should catch required IOMMU and resources. Runtime tests include multi-plane blending, alpha formats, DMA/IOMMU fault absence, GCE-assisted atomic commits, and routes to both display and WDMA where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl.yaml -->
