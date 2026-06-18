<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dp-controller.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dp-controller.yaml

### Purpose
This schema defines Qualcomm MSM DisplayPort host controllers compatible with VESA DisplayPort. It covers DP, eDP, SST, and MST-capable variants across many SoCs.

### Important APIs, Types, And Functions
The node API includes layered `compatible` choices, `reg` blocks for AHB/AUX/link/stream/MST register windows, interrupts, `clocks` and `clock-names`, one DP PHY, power-domain, optional OPP table, optional `aux-bus`, optional audio `#sound-dai-cells`, deprecated top-level `data-lanes`, and graph `ports`. Output endpoint properties include `data-lanes` and `link-frequencies`.

### Control Flow
The `allOf` chain is the core logic. eDP variants disallow sound DAI cells. Some DP variants require either `aux-bus` or audio cells, while older variants disallow `aux-bus` and require audio cells. Additional conditionals set register and clock counts for SST-only, two-stream MST, four-stream MST, and Glymur variants.

### State, Persistence, And Dependencies
Persistent state is the DT description of controller register windows, PHY link, clocks, power, OPP, and graph. Dependencies include DP AUX bus, sound DAI schema, video-interface endpoints, PHY providers, display clock controllers, PM domains, and MDSS interrupt parents.

### Integration Points
The msm DP driver consumes this node under MDSS, connects to DPU output through `port@0`, and exposes a connector, Type-C mux, bridge, or PHY-linked output through `port@1`.

### Risks
The schema uses `clocks-names` in conditionals while the property is `clock-names`; this typo weakens conditional validation for clock-name counts. Deprecated compatible fallbacks and top-level lane properties can preserve old DTS but should not be copied. MST register/clock cardinality must match the specific controller instance.

### Test Signals
Run `dt_binding_check` with examples for SST, eDP, MST, and AUX/audio variants. Runtime signals include DP probe, PHY attach, AUX transactions, link training at declared frequencies, audio registration for DP-only variants, and MST stream bring-up where declared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dp-controller.yaml -->
