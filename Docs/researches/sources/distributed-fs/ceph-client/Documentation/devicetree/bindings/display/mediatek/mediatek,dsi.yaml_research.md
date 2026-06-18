<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsi.yaml

### Purpose
This binding describes MediaTek MIPI DSI host controllers. The controller receives pixels from the display pipeline and drives a DSI panel or bridge.

### Important APIs, Types, And Functions
The schema defines the `compatible` set, `reg`, interrupts, clocks and `clock-names`, PHY and power resources, optional resets, and graph `ports`. It also participates in the common DSI controller and video-interface contracts through endpoints and child panel/bridge topology.

### Control Flow
Validation is declarative. Compatible strings select the supported host variant. Required resources make the host probeable, while graph ports determine pipeline input and downstream DSI device connectivity.

### State, Persistence, And Dependencies
Persistent state is the boot-time hardware description: register range, clocks, PHY relation, power domain, and endpoint graph. Dependencies include DSI PHY nodes, clock/reset/power providers, interrupt controllers, graph bindings, and any downstream panel or bridge schema.

### Integration Points
The MediaTek DRM DSI driver binds as both an encoder/bridge participant and a MIPI DSI host. Endpoint links connect it to upstream display components and panel/bridge consumers.

### Risks
DSI failures often stem from resource ordering or missing PHY/clock relationships. A graph that validates but points to the wrong upstream interface can leave the host active with no pixels. Dual-DSI or split pipelines need careful endpoint pairing.

### Test Signals
`dt_binding_check` should cover required resources and graph syntax. Runtime tests include host registration, panel attachment, mode set, lane/PLL setup, command transfer, and suspend/resume power sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsi.yaml -->
