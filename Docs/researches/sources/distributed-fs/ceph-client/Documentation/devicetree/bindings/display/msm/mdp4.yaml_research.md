<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdp4.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdp4.yaml

### Purpose
This schema documents Qualcomm MDP4 display controller nodes. MDP4 is an older display controller generation used before MDP5/DPU.

### Important APIs, Types, And Functions
The binding includes compatible values, MMIO `reg` and names, interrupts, clocks and names, optional power-domain/interconnect resources, IOMMU, and graph `ports` describing output interfaces.

### Control Flow
Validation is resource and graph based. There is no executable control flow; compatible selection maps the node to an older MDP4 driver path.

### State, Persistence, And Dependencies
Persistent DT state describes the controller register block, interrupt, clocks, memory translation, and output graph. Dependencies include MDSS or platform interrupt parents, clock providers, IOMMU, graph bindings, and downstream HDMI/DSI/LCDC-style outputs depending on the SoC.

### Integration Points
The msm DRM driver uses MDP4 as the display controller for older Qualcomm platforms. Its graph ports connect scanout to HDMI, DSI, or related encoders.

### Risks
Older bindings may coexist with legacy DTS assumptions, so strict validation can expose historical naming differences. Missing IOMMU or clock names can cause probe/runtime failures rather than schema-only failures.

### Test Signals
Run `dt_binding_check` for the MDP4 example and existing DTS files. Runtime signals are MDP4 probe, IRQ handling, scanout, output encoder attach, and suspend/resume clock sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdp4.yaml -->
