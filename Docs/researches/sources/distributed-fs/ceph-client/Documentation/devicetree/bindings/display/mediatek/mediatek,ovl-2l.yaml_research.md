<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl-2l.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl-2l.yaml

### Purpose
This schema documents MediaTek two-layer overlay blocks. OVL-2L composites a smaller number of memory-backed layers than the full OVL block.

### Important APIs, Types, And Functions
The binding defines compatible/fallback strings, `reg`, one interrupt, power-domain and clock resources, `iommus` for memory fetch, optional `mediatek,gce-client-reg`, and graph `ports`. The output port feeds the next display pipeline stage such as RDMA, COLOR, or WDMA.

### Control Flow
The schema validates SoC compatibility and mandatory memory/display resources. Data-flow is encoded by graph endpoints; memory access is encoded by the IOMMU phandle.

### State, Persistence, And Dependencies
State persists in devicetree as the OVL-2L instance identity, memory master, clock/power resources, and route connectivity. Dependencies include IOMMU bindings, MMSYS/VDOSYS, clocks, PM domains, interrupts, GCE, and graph bindings.

### Integration Points
The MediaTek DRM driver uses OVL-2L as an overlay plane source in display pipelines. IOMMU integration is required for framebuffer access.

### Risks
Missing or wrong `iommus` can cause DMA faults rather than schema-visible display failures. Fallback-compatible errors can select wrong layer capabilities. Incorrect graph routing can send output to unsupported downstream blocks.

### Test Signals
Use binding checks and DTS IOMMU validation. Runtime signals are plane enablement, framebuffer scanout through IOMMU, command-queue updates, and correct blend behavior with one or two active layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl-2l.yaml -->
