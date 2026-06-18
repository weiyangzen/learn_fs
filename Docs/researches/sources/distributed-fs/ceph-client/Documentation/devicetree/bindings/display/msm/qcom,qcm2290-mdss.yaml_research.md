<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-mdss.yaml

### Purpose
This schema defines the QCM2290 MDSS parent for DPU and DSI display blocks.

### Important APIs, Types, And Functions
The binding imports `mdss-common.yaml`, fixes `compatible = "qcom,qcm2290-mdss"`, defines clocks named `iface`, `bus`, and `core`, allows one IOMMU, defines interconnects named `mdp0-mem` and `cpu-cfg`, and constrains DPU, DSI, and DSI PHY child compatibles.

### Control Flow
Common MDSS validation is composed with QCM2290-specific child filters. The schema validates the parent bus and delegates child internals.

### State, Persistence, And Dependencies
Persistent state includes the MDSS register block, clocks, power, interrupts, interconnect paths, IOMMU, and child bus. Dependencies include QCM2290 GCC/DISPCC, RPM power/interconnect providers, SMMU, DPU/DSI/PHY bindings, and graph endpoints.

### Integration Points
The MDSS parent hosts the QCM2290 DPU and DSI controller and provides the interrupt-controller context used by child nodes.

### Risks
The title says `QCM220`, likely a typo for QCM2290. Interconnect naming must match the common and driver expectations. Child compatible filters do not enforce complete child resource correctness.

### Test Signals
Use `dt_binding_check` on the example and full DTS. Runtime signals include MDSS probe, interconnect votes, IOMMU attach, child creation, DPU-to-DSI graph resolution, and panel modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-mdss.yaml -->
