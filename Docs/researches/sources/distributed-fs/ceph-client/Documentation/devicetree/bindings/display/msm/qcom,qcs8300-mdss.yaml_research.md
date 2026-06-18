<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcs8300-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcs8300-mdss.yaml

### Purpose
This binding defines the QCS8300 MDSS parent, containing DPU, DP/eDP, DSI, and PHY children.

### Important APIs, Types, And Functions
It references `mdss-common.yaml`, fixes `compatible = "qcom,qcs8300-mdss"`, defines three display clocks, one IOMMU, up to three interconnects/names, and child filters for `qcom,qcs8300-dpu`, `qcom,qcs8300-dp`, `qcom,qcs8300-dsi-ctrl`, `qcom,qcs8300-dsi-phy-5nm`, and `qcom,qcs8300-edp-phy`.

### Control Flow
Validation composes common MDSS properties and QCS8300 child-compatible constraints. The example also uses fallback compatibles to SA8775P for DPU/DP/DSI/PHY child schemas.

### State, Persistence, And Dependencies
Persistent state includes MDSS resources, interrupt domain, clocks, reset, power, interconnects, SMMU, and child display nodes. Dependencies include QCS8300/SA8775P clock and power bindings, DPU/DP/DSI/PHY schemas, and graph endpoints.

### Integration Points
The parent hosts a DPU, DSI path, DSI PHY, eDP PHY, and DP controller. It connects DPU outputs to DSI and DP through child graph endpoints.

### Risks
Fallback to SA8775P-compatible child bindings means resource lists must follow the fallback schema exactly. Three interconnect paths add review risk, especially `mdp1-mem` on multi-interface routes.

### Test Signals
Run binding checks for the complete QCS8300 example. Runtime signals are parent probe, child instantiation, SMMU/interconnect setup, DSI panel output, DP/eDP PHY attach, and DP link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcs8300-mdss.yaml -->
