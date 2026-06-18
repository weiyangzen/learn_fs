<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,eliza-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,eliza-mdss.yaml

### Purpose
This schema defines the Qualcomm Eliza SoC MDSS parent. It encapsulates DPU, DSI, DP, and DSI PHY child nodes for that platform.

### Important APIs, Types, And Functions
The binding references `mdss-common.yaml`, fixes `compatible = "qcom,eliza-mdss"`, defines three display clocks, optional IOMMU, two interconnects named `mdp0-mem` and `cpu-cfg`, and patternProperties for `qcom,eliza-dpu`, `qcom,eliza-dp`, `qcom,eliza-dsi-ctrl`, and `qcom,eliza-dsi-phy-4nm` children.

### Control Flow
Validation composes the common MDSS parent contract with Eliza-specific child compatibility checks. Child nodes remain fully validated by their own DPU/DP/DSI/PHY schemas.

### State, Persistence, And Dependencies
Persistent state is the Eliza display subsystem bus, interrupt controller, clocks, power domain, interconnects, SMMU, and children. Dependencies include RPMh power/interconnect providers, display clocks, DPU/DSI/DP/PHY bindings, and graph endpoints.

### Integration Points
The MDSS parent hosts child display controllers and routes their interrupts through the MDSS interrupt controller. Example topology shows DPU outputs to two DSI controllers and one DP controller.

### Risks
PatternProperties only constrain child compatibles; resource correctness remains delegated. Eliza-specific DSI uses the SM8750 DSI clock model, so child clock lists must match that branch.

### Test Signals
Run binding checks for the whole example. Runtime signals include MDSS parent probe, child population, interconnect votes, SMMU attachment, DPU-to-DSI/DP graph resolution, and interrupt routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,eliza-mdss.yaml -->
