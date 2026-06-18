<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-dpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-dpu.yaml

### Purpose
This schema defines the QCM2290 DPU display controller.

### Important APIs, Types, And Functions
It references `dpu-common.yaml`, fixes `compatible = "qcom,qcm2290-dpu"`, requires two register regions named `mdp` and `vbif`, and five clocks named `bus`, `iface`, `core`, `lut`, and `vsync`.

### Control Flow
Validation composes common DPU requirements with the QCM2290 resource layout. Ports from the common schema represent DPU outputs, usually to a single DSI controller.

### State, Persistence, And Dependencies
Persistent state includes DPU MMIO, clocks, power/OPP, interrupt parent, and graph. Dependencies include QCM2290 MDSS parent, GCC/DISPCC clocks, RPM power domains, OPP tables, and DSI bindings.

### Integration Points
The DPU child appears under `qcom,qcm2290-mdss` and feeds QCM2290 DSI through a graph endpoint.

### Risks
Clock order differs from SC7180/SC7280 families. The platform has a simpler two-register DPU layout, so copying four-register MSM8998 snippets would be invalid.

### Test Signals
Binding checks should validate exact register and clock lists. Runtime signals include DPU probe, LUT/core/vsync clock enablement, OPP scaling, interrupt delivery, and DSI graph output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-dpu.yaml -->
