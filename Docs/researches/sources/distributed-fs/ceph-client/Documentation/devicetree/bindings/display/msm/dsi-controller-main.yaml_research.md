<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dsi-controller-main.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dsi-controller-main.yaml

### Purpose
This schema defines Qualcomm MDSS DSI controller nodes across many Snapdragon and related SoCs. It models both the host controller and graph connections to DPU and panels/bridges.

### Important APIs, Types, And Functions
The node contract includes SoC-specific compatible plus `qcom,mdss-dsi-ctrl` fallback, one `reg` named `dsi_ctrl`, one interrupt, clocks and names, one DSI PHY, optional syscon for DSIv2, dual-DSI booleans, assigned clocks/parents, power-domain/OPP, regulator supplies, and graph `ports`. Endpoint properties include `data-lanes` and `qcom,te-source`.

### Control Flow
The schema imports the generic DSI controller binding, then uses many `if` branches keyed by compatible to enforce platform-specific clock counts and exact `clock-names`. Older platforms require `assigned-clocks` and `assigned-clock-parents`; newer SM8750/Kaanapali variants use twelve clocks including PLL, esync, osc, and source clocks.

### State, Persistence, And Dependencies
Persistent state is the controller hardware description, PHY relationship, clocks, power, OPP, regulators, and graph. Dependencies include DSI PHY nodes, clock controllers, MDSS interrupt parents, power domains, graph/video-interface schemas, and generic DSI schema.

### Integration Points
The msm DSI driver binds under MDSS, receives pixels from DPU through `port@0`, and drives a panel/bridge through `port@1`. Dual-DSI properties coordinate master/sync behavior between two controller nodes.

### Risks
Clock-name ordering is the highest-risk contract because each compatible branch lists exact names. Deprecated `phy-names` remains allowed but should not guide new DTS. Dual-DSI booleans are only structurally validated, so board-level pairing still needs review.

### Test Signals
Binding checks should cover each compatible family. Runtime signals include DSI host registration, PHY clock-parent setup, panel attach, TE source operation, dual-DSI synchronization, and OPP/power-domain transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dsi-controller-main.yaml -->
