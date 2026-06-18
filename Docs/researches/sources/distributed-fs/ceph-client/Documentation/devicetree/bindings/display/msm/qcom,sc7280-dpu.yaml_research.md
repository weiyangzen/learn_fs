<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-dpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-dpu.yaml

### Purpose
This schema defines SC7280-style DPU display controllers and related compatibles including SAR2130P, SC8280XP, SM8350, SM8450, and SM8550.

### Important APIs, Types, And Functions
The binding references `dpu-common.yaml`, accepts several compatible values, requires two register regions named `mdp` and `vbif`, and six clocks named `bus`, `nrt_bus`, `iface`, `lut`, `core`, and `vsync`.

### Control Flow
Validation is mostly fixed for this family: common DPU resources plus exact two-register and six-clock layout. Graph ports from the common schema express DPU interface outputs.

### State, Persistence, And Dependencies
Persistent state includes DPU registers, realtime/non-realtime bus clocks, AHB/core/LUT/vsync clocks, power/OPP, interrupt, and graph endpoints. Dependencies include SoC-specific MDSS parent, display/GCC clocks, RPMh power domains, OPP tables, and DSI/DP children.

### Integration Points
SC7280-family DPU nodes feed DSI and DP/eDP interfaces through MDSS graph ports. The `nrt_bus` clock differentiates this family from simpler QCM2290 layouts.

### Risks
This schema covers multiple SoCs; DTS authors must still use the correct SoC-specific MDSS parent and child outputs. Copying SC7180 clock names would omit `nrt_bus` and include invalid `rot`.

### Test Signals
Run binding checks for each compatible family represented in DTS. Runtime signals are DPU probe, bus and non-realtime bus clock control, graph output resolution, OPP scaling, and display scanout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-dpu.yaml -->
