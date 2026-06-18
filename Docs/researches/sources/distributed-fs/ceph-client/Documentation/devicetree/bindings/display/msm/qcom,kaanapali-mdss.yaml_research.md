<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,kaanapali-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,kaanapali-mdss.yaml

### Purpose
This binding defines the Qualcomm Kaanapali MDSS parent. It contains DPU, DSI, and DSI PHY child blocks for that SoC family.

### Important APIs, Types, And Functions
The schema imports `mdss-common.yaml`, sets `compatible = "qcom,kaanapali-mdss"`, defines the platform clock set, and constrains child compatibles for Kaanapali DPU, DSI controller, and DSI PHY nodes.

### Control Flow
Validation applies common MDSS rules plus Kaanapali child compatible filters. The display data path is encoded by child graph endpoints rather than parent control flow.

### State, Persistence, And Dependencies
Persistent state includes parent MDSS resources and child bus topology. Dependencies include display clocks, PM domains, optional IOMMU/interconnects from the common schema, DPU/DSI/PHY child schemas, and graph bindings.

### Integration Points
The Kaanapali MDSS parent provides address space, interrupts, and power/clock context for its DPU and DSI children. The DSI child uses the newer high-clock-count branch in the DSI controller schema.

### Risks
Child compatibility filters do not replace child schema validation. Kaanapali DSI clock names are numerous, and a parent node can validate while a child still fails due to clock/resource mismatch.

### Test Signals
Binding checks should run on the complete MDSS example. Runtime signals are parent probe, DPU/DSI child population, DSI PHY attach, graph connectivity, and panel modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,kaanapali-mdss.yaml -->
