<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,glymur-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,glymur-mdss.yaml

### Purpose
This schema defines the Qualcomm Glymur MDSS parent, a subsystem containing DPU and DP display blocks.

### Important APIs, Types, And Functions
It imports `mdss-common.yaml`, fixes `compatible = "qcom,glymur-mdss"`, defines display AHB, hf AXI, and core clocks, optional IOMMU and interconnects, and constrains child nodes with patternProperties for Glymur DPU, DP, and PHY-compatible blocks.

### Control Flow
Validation is composed: common MDSS properties are inherited and Glymur-specific child compatible filters are applied. Runtime display routing remains represented by child graph endpoints.

### State, Persistence, And Dependencies
Persistent state covers MDSS bus resources, interrupts, power, clocks, interconnects, IOMMU, and child display nodes. Dependencies include Qualcomm display clock controllers, RPMh power/interconnect providers, DP/DPU/PHY bindings, and graph schemas.

### Integration Points
The parent node hosts DPU and DP controllers and provides interrupt-controller behavior for children under the MDSS address space.

### Risks
Glymur DP controllers may have complex MST/SST resource requirements inherited from `dp-controller.yaml`. The parent schema does not fully validate child internals, so child schemas must be run together.

### Test Signals
Use `dt_binding_check` on Glymur MDSS examples and full DTS. Runtime signals are MDSS bus probe, DPU/DP child creation, interconnect voting, graph resolution, and DP link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,glymur-mdss.yaml -->
