<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-mdss.yaml

### Purpose
This schema defines the SC7180 MDSS parent, hosting SC7180 DPU, DSI, DP, and DSI PHY children.

### Important APIs, Types, And Functions
It imports `mdss-common.yaml`, fixes `compatible = "qcom,sc7180-mdss"`, defines clocks named `iface`, `ahb`, and `core`, allows one IOMMU, defines two interconnects `mdp0-mem` and `cpu-cfg`, and filters child compatibles for SC7180 DPU, DP, DSI controller, and `qcom,dsi-phy-10nm`.

### Control Flow
Common MDSS validation is composed with SC7180 child filters. Child schemas validate detailed DPU, DSI, DP, and PHY resources.

### State, Persistence, And Dependencies
Persistent state includes MDSS bus resources, interrupts, clocks, power domain, interconnects, SMMU, and child topology. Dependencies include GCC/DISPCC, RPMh/RPMPD, SMMU, DPU/DSI/DP/PHY bindings, and graph schemas.

### Integration Points
SC7180 MDSS wires DPU outputs to one DSI controller and one DP controller in the example. It also provides the interrupt parent for those children.

### Risks
The clock-name set uses both GCC and DISPCC AHB clocks, so `iface` versus `ahb` naming must not be swapped. Child DP/eDP and DSI resources must be checked with their own schemas.

### Test Signals
Binding checks should run on the full SC7180 example. Runtime signals are parent probe, interconnect votes, SMMU attach, DPU-to-DSI/DP graph resolution, DSI panel output, and DP link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-mdss.yaml -->
