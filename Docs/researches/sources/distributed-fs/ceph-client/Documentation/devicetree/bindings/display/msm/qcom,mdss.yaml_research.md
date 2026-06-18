<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdss.yaml

### Purpose
This binding describes legacy Qualcomm Mobile Display Subsystem parent nodes using `compatible = "qcom,mdss"`. It encapsulates MDP5, DSI, HDMI, eDP, PHY, and related children.

### Important APIs, Types, And Functions
The parent API includes node-name pattern, `compatible`, two or three register regions named `mdss_phys`, `vbif_phys`, and optional `vbif_nrt_phys`, one interrupt, interrupt-controller cells, one power domain, clock sets, address/size cells, `ranges`, optional reset, and interconnects. PatternProperties allow MDP5, DSI, PHY, and HDMI child nodes.

### Control Flow
The schema validates the MDSS bus container and permits known child node patterns with compatible filters. It does not deeply validate child nodes inline; those are handled by child schemas.

### State, Persistence, And Dependencies
Persistent state is the display-subsystem bus, VBIF register map, interrupt controller, clocks, power domain, and child address space. Dependencies include GCC/MMCC clocks, power domains, interrupt controller, interconnects, and child display bindings.

### Integration Points
Legacy msm DRM platforms use this parent to route child interrupts and instantiate MDP5/DSI/HDMI/PHY nodes below the MDSS address space.

### Risks
This legacy binding overlaps conceptually with `mdss-common.yaml` but has different register names and child constraints. Mixing modern and legacy parent contracts can produce invalid DTS.

### Test Signals
Run binding checks on legacy MDSS examples and DTS files. Runtime signals are MDSS parent probe, interrupt-domain registration, child population, clock/power enablement, and MDP5-to-output graph resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdss.yaml -->
