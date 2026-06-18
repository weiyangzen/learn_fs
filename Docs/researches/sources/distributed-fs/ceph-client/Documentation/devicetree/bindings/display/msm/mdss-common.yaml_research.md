<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdss-common.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdss-common.yaml

### Purpose
This common schema defines shared Qualcomm MDSS display-subsystem properties for modern SoC-specific MDSS bindings. It is explicitly not auto-selected for legacy `qcom,mdss` nodes.

### Important APIs, Types, And Functions
The common MDSS contract includes node-name pattern, one `reg` named `mdss`, one power domain, clocks, interrupts, interrupt-controller properties, address/size cells, `ranges`, optional resets, optional IOMMU, and interconnects. SoC-specific schemas add exact compatible, clock names, and child pattern constraints.

### Control Flow
The file uses `select: false` and is consumed through `$ref`. Validation composition lets each SoC binding inherit the MDSS bus/interrupt/power shape while defining allowed children.

### State, Persistence, And Dependencies
Persistent state is the MDSS bus container and interrupt controller description. Dependencies include clock/power/reset providers, interconnect providers, SMMU, child DPU/DSI/DP/PHY schemas, and the graph topology below child nodes.

### Integration Points
Modern Qualcomm MDSS bindings import this schema for the parent display subsystem that hosts DPU, DSI, DP, and PHY children.

### Risks
Because many SoC-specific bindings depend on it, common-property changes can have wide validation impact. The schema validates structure but child compatibility semantics remain in each SoC wrapper.

### Test Signals
Run binding checks for all SoC-specific MDSS schemas that reference it. Regression signals are stable validation of interrupt-controller, `ranges`, reg-names, power, clocks, and child bus address layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdss-common.yaml -->
