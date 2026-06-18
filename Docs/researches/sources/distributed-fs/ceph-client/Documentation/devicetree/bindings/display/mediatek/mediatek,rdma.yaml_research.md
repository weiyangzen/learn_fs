<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,rdma.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,rdma.yaml

### Purpose
This binding documents MediaTek display RDMA blocks. RDMA reads pixels from memory or pipeline sources and forwards them to display output processing.

### Important APIs, Types, And Functions
The schema defines compatible/fallback strings, one `reg`, one interrupt, power-domain and clock resources, optional `iommus`, optional `mediatek,gce-client-reg`, and graph `ports`. Ports connect RDMA input and output within the MediaTek display graph.

### Control Flow
Compatible `oneOf` entries encode SoC generations and fallback rules. Required register/interrupt/power/clock resources validate probeability, while IOMMU and graph properties encode optional memory and route integration.

### State, Persistence, And Dependencies
Persistent state includes the RDMA instance identity, command-queue window, memory-master relation, and route endpoints. Dependencies include clock/power domains, interrupt routing, optional IOMMU, GCE, graph bindings, and MMSYS configuration.

### Integration Points
RDMA is a central MediaTek DRM component for scanout paths. It can bridge memory-backed data and downstream encoders such as DPI/DSI/DP via the component graph.

### Risks
RDMA participates in both direct memory read and pipeline forwarding paths, so missing IOMMU or graph properties can fail differently by route. Compatible fallback mismatches can break register programming.

### Test Signals
Validation should include schema checks for required resources and DTS graph edges. Runtime tests are scanout from memory, route enablement to each output type, IOMMU fault absence, interrupt delivery, and GCE atomic updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,rdma.yaml -->
