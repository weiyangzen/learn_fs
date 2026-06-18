<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-mdss.yaml

### Purpose
This schema defines the SC7280 MDSS parent, hosting SC7280 DPU, DSI, DP/eDP, and PHY children.

### Important APIs, Types, And Functions
It references `mdss-common.yaml`, fixes `compatible = "qcom,sc7280-mdss"`, defines display clocks, optional IOMMU, interconnects, and patternProperties for `qcom,sc7280-dpu`, `qcom,sc7280-dp`, `qcom,sc7280-edp`, `qcom,sc7280-dsi-ctrl`, and matching DSI/eDP PHY nodes.

### Control Flow
Validation composes common MDSS constraints with SC7280 child-compatible filters. Child DP validation distinguishes DP from eDP behavior, including sound/AUX rules in `dp-controller.yaml`.

### State, Persistence, And Dependencies
Persistent state includes MDSS register block, interrupt-controller behavior, clocks, power, interconnects, optional SMMU, and child address space. Dependencies include SC7280 display/GCC clocks, power domains, DPU/DSI/DP/PHY schemas, graph bindings, and OPP/interconnect providers.

### Integration Points
The parent hosts DPU outputs to DSI and DP/eDP controllers. It is the container through which msm DRM discovers and binds the SC7280 display subsystem.

### Risks
SC7280 supports both DP and eDP child paths; applying DP audio/AUX assumptions to eDP nodes is invalid. Child pattern filters must remain aligned with DSI/DP/PHY schema compatible lists.

### Test Signals
Binding checks should cover full SC7280 examples with DSI, DP, and eDP children. Runtime signals include MDSS probe, DPU/DSI/DP child binding, eDP versus DP behavior, graph resolution, and link/panel bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-mdss.yaml -->
