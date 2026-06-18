<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-dpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-dpu.yaml

### Purpose
This schema defines the MSM8998 DPU display-controller node.

### Important APIs, Types, And Functions
The binding references `dpu-common.yaml`, fixes `compatible = "qcom,msm8998-dpu"`, requires four register regions named `mdp`, `regdma`, `vbif`, and `vbif_nrt`, and five clocks named `iface`, `bus`, `mnoc`, `core`, and `vsync`.

### Control Flow
Validation composes common DPU requirements with MSM8998-specific register and clock layouts. Graph ports from the common schema connect DPU outputs to DSI controllers.

### State, Persistence, And Dependencies
Persistent state includes DPU register windows, clocks, interrupt parent, OPP/power data, and graph ports. Dependencies include the MSM8998 MDSS parent, MMCC clocks, RPM power domains, OPP tables, and DSI child nodes.

### Integration Points
The msm DPU driver uses this node under `qcom,msm8998-mdss`; the example exposes two DPU output ports feeding two DSI controllers.

### Risks
MSM8998 uses a distinct `regdma` region and non-realtime VBIF. Omitting or reordering these register names can break driver access. Clock naming differs from newer DPU variants.

### Test Signals
Binding checks should validate exact register and clock names. Runtime signals include DPU probe, RegDMA access, VBIF setup, OPP scaling, and dual-DSI graph resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-dpu.yaml -->
