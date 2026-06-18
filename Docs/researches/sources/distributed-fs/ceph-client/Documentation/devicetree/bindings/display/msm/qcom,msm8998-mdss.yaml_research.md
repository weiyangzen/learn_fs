<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-mdss.yaml

### Purpose
This schema defines the MSM8998 MDSS parent, hosting MSM8998 DPU, DSI controllers, and DSI PHYs.

### Important APIs, Types, And Functions
It references `mdss-common.yaml`, fixes `compatible = "qcom,msm8998-mdss"`, defines clocks named `iface`, `bus`, and `core`, allows one IOMMU, and constrains children to `qcom,msm8998-dpu`, `qcom,msm8998-dsi-ctrl` plus `qcom,mdss-dsi-ctrl`, and `qcom,dsi-phy-10nm-8998`.

### Control Flow
Validation composes common MDSS rules with MSM8998 child-compatible filters. Child schemas validate DPU, DSI, and PHY internals.

### State, Persistence, And Dependencies
Persistent state is the MSM8998 MDSS bus, clocks, power, interrupt domain, IOMMU, and children. Dependencies include MMCC/RPM clocks, RPM power domains, SMMU, DPU/DSI/PHY bindings, and graph endpoints.

### Integration Points
This parent wires the MSM8998 DPU outputs to two DSI controllers and provides interrupt routing for the child display blocks.

### Risks
The binding title and child filters are MSM8998-specific; sharing with generic DPU/MDSS snippets can lose required MSM8998 clock and PHY naming. The parent can validate while child dual-DSI graph endpoints remain semantically incomplete.

### Test Signals
Run binding checks on full examples. Runtime signals are MDSS parent probe, IOMMU attachment, child creation, DPU-to-DSI graph resolution, and dual-panel/dual-DSI modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-mdss.yaml -->
