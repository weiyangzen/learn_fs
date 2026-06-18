<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dpu-common.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dpu-common.yaml

### Purpose
This common schema defines shared properties for Qualcomm DPU display-controller nodes. SoC-specific DPU bindings reference it to avoid duplicating interrupt, power, OPP, and port requirements.

### Important APIs, Types, And Functions
The common contract includes interrupt resources, one power domain, optional `operating-points-v2`/`opp-table`, and graph `ports`. It defines required baseline resources that SoC-specific bindings extend with compatible, register, clock, and clock-name details.

### Control Flow
The file is selected only by explicit `$ref`; it is not a standalone compatible match. Validation flow is composition: SoC-specific schemas import this common shape, then add stricter resource cardinality and `unevaluatedProperties: false`.

### State, Persistence, And Dependencies
State persists in the final composed devicetree node. Dependencies include graph bindings, OPP bindings, PM domains, interrupt parent configuration, and SoC-specific DPU schemas.

### Integration Points
Every referenced Qualcomm DPU binding relies on this file for shared DRM display-controller requirements. It standardizes the graph output ports used to connect DPU interfaces to DSI, DP, HDMI, or other encoders.

### Risks
Changes here have broad blast radius because many SoC DPU bindings inherit it. Too-loose common constraints can let bad DTS pass; too-strict constraints can break valid SoC-specific variants.

### Test Signals
Run binding checks for all SoC-specific DPU schemas that reference this file. Regression signals include unchanged validation for DPU interrupt, power-domain, OPP, and ports across MSM8998, QCM2290, SC7180, SC7280, and later families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dpu-common.yaml -->
