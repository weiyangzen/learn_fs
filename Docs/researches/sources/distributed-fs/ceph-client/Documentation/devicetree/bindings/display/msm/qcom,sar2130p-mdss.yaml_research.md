<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sar2130p-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sar2130p-mdss.yaml

### Purpose
This binding defines the SAR2130P MDSS parent for DPU, DP, DSI, and PHY children.

### Important APIs, Types, And Functions
The schema imports `mdss-common.yaml`, fixes `compatible = "qcom,sar2130p-mdss"`, defines display clocks, optional IOMMU and interconnects, and constrains child compatibles for SAR2130P DPU, DP, DSI controller, and PHY blocks.

### Control Flow
Validation composes the common MDSS parent contract with SAR2130P child-compatible filters. Child DPU and DP resources are checked by their referenced schemas, including SC7280-style DPU fallback and SM8350-style DP fallback where applicable.

### State, Persistence, And Dependencies
Persistent state includes parent MDSS resources, interrupt controller state, power/clock/reset, interconnects, SMMU, and child display topology. Dependencies include display clock providers, RPMh power domains, DPU/DP/DSI/PHY bindings, and graph schemas.

### Integration Points
The parent coordinates SAR2130P display children and routes DPU outputs to DSI/DP interfaces via graph endpoints.

### Risks
SAR2130P often reuses fallback compatibles from nearby Qualcomm families. Mismatched fallback ordering can bind to the wrong resource model even when the parent compatible is correct.

### Test Signals
Use binding checks against full SAR2130P examples. Runtime signals include MDSS and child probe, graph resolution, DSI panel modeset, DP link training, interconnect votes, and SMMU attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sar2130p-mdss.yaml -->
