<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-dpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-dpu.yaml

### Purpose
This schema defines SC7180-family DPU display controllers, also covering SM6125, SM6350, and SM6375 variants.

### Important APIs, Types, And Functions
It references `dpu-common.yaml`, accepts four compatible values, requires two register regions named `mdp` and `vbif`, and defines six or seven clocks named `bus`, `iface`, `rot`, `lut`, `core`, `vsync`, and optionally `throttle`.

### Control Flow
The `allOf` branch requires at least seven clocks and names for SM6375 and SM6125. Other variants use the six-clock minimum. Common DPU ports connect outputs to DSI and DP.

### State, Persistence, And Dependencies
Persistent state includes DPU MMIO, clocks, interrupt, power/OPP, and graph outputs. Dependencies include SC7180-family MDSS parents, GCC/DISPCC clocks, RPMh/RPMPD power domains, OPP tables, and DSI/DP child nodes.

### Integration Points
The DPU child under SC7180-style MDSS feeds DSI and DP endpoints. The rotator and LUT clocks reflect hardware blocks in this DPU generation.

### Risks
SM6125/SM6375 need the throttle clock; copying the SC7180 six-clock example can under-specify those variants. Output port numbering should match DPU interface indices.

### Test Signals
Binding checks should cover all compatible variants. Runtime signals include DPU probe, optional throttle clock acquisition where required, DSI/DP graph resolution, OPP scaling, and scanout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-dpu.yaml -->
