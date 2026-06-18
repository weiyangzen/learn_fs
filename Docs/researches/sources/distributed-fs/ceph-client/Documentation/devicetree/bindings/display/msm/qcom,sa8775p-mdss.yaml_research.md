<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sa8775p-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sa8775p-mdss.yaml

### Purpose
This schema defines the SA8775P MDSS parent. It covers a display subsystem with DPU, DP/eDP, DSI, and PHY children.

### Important APIs, Types, And Functions
The binding imports `mdss-common.yaml`, fixes `compatible = "qcom,sa8775p-mdss"`, defines display AHB, hf AXI, and core clocks, optional IOMMU, up to three interconnect paths, and child compatible filters for SA8775P DPU, DP, DSI controller, DSI PHY, and eDP PHY.

### Control Flow
Validation is common MDSS plus SA8775P child constraints. DP child nodes must follow the DP controller schema, including SA8775P MST register and clock cardinalities.

### State, Persistence, And Dependencies
Persistent state includes the MDSS parent register block, interrupts, clocks, reset, power, interconnects, SMMU, and child bus. Dependencies include SA8775P display clocks, RPMh power/interconnects, DPU/DP/DSI/PHY bindings, and graph endpoints.

### Integration Points
SA8775P MDSS hosts high-capability display paths with multiple memory interconnects and DP stream support. It provides interrupt-controller behavior for child blocks.

### Risks
SA8775P DP supports four-stream MST on some controllers, so child resource counts are easy to under-describe. Multi-path interconnect names must match driver expectations.

### Test Signals
Binding checks should cover DPU, DSI, DP, and PHY children together. Runtime signals are MDSS probe, interconnect voting, DP MST/SST bring-up, DSI output, and interrupt routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sa8775p-mdss.yaml -->
