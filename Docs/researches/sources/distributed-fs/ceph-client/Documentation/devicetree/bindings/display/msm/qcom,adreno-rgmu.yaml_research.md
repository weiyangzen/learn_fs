<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,adreno-rgmu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,adreno-rgmu.yaml

### Purpose
This binding describes RGMU blocks attached to certain Qualcomm Adreno GPUs. RGMU is a resource/power management unit for applicable GPU generations.

### Important APIs, Types, And Functions
The node contract includes `compatible`, register resources, clocks and names, power domains, interrupts, operating points, and GPU power-management integration properties. It is similar in role to GMU but targets the RGMU-supported hardware path.

### Control Flow
Validation is compatible and resource based. There is no executable flow; the schema ensures the GPU power-management driver receives the required register, clock, interrupt, and power resources.

### State, Persistence, And Dependencies
Persistent state describes RGMU register space and power/clock topology. Dependencies include GPU clock controllers, power-domain providers, interrupt controller, OPP table, and the corresponding GPU node.

### Integration Points
The Adreno driver uses RGMU data when bringing up GPUs that rely on this management unit for power/performance operations.

### Risks
RGMU and GMU nodes are not interchangeable; copying properties between bindings can describe the wrong hardware. Clock and power-domain naming must match the exact SoC.

### Test Signals
Use binding checks for the example DTS. Runtime signals include GPU probe with RGMU attachment, successful OPP transitions, interrupt handling, and suspend/resume without power-management errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,adreno-rgmu.yaml -->
