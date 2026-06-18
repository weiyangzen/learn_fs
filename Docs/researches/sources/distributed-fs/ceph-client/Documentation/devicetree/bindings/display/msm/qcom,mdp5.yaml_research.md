<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdp5.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdp5.yaml

### Purpose
This schema describes Qualcomm MDP5 display controllers. MDP5 is the display engine generation used on several pre-DPU Snapdragon platforms.

### Important APIs, Types, And Functions
The binding includes SoC-specific compatible strings with `qcom,mdp5` fallback, register resources, one interrupt, clocks and names, power-domain, optional IOMMU, and graph `ports`. The ports represent outputs to DSI, DP, HDMI, or other display interfaces.

### Control Flow
Validation constrains compatible pairs and required controller resources. The schema relies on graph endpoints to express which display interface each MDP5 output drives.

### State, Persistence, And Dependencies
Persistent state is the MDP5 hardware description: register window, clocks, interrupt, power domain, memory translation, and output graph. Dependencies include MDSS parent interrupt-controller behavior, clock/PM/IOMMU providers, graph bindings, and downstream interface schemas.

### Integration Points
The msm DRM driver uses MDP5 as the central display controller under legacy `qcom,mdss` parents. It drives child outputs through the graph.

### Risks
MDP5 platforms vary in clock availability and output count. A graph may validate with missing outputs but not match board hardware. IOMMU omission can cause scanout memory faults.

### Test Signals
Use binding checks plus existing DTS validation. Runtime signals include MDP5 probe, IRQ delivery, plane scanout, graph-resolved encoder attachment, IOMMU fault absence, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdp5.yaml -->
