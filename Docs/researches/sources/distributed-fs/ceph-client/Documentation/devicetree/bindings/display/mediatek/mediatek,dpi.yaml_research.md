<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dpi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dpi.yaml

### Purpose
This binding documents the MediaTek DPI parallel/RGB display output controller. DPI converts the internal display pipeline into a parallel display interface, often feeding HDMI, LVDS, or external bridge hardware.

### Important APIs, Types, And Functions
The schema exposes SoC-specific `compatible` strings, MMIO `reg`, interrupts, clocks and `clock-names`, power domains, optional pinctrl, and graph `ports`. It also integrates common display timing and graph contracts through endpoint connectivity.

### Control Flow
The binding is declarative. Compatible entries select the hardware generation, while the required property set ensures the driver has register, clock, interrupt, and power resources before probing. Endpoint traversal controls data-flow topology from an upstream display block to the downstream bridge or connector.

### State, Persistence, And Dependencies
State persists as devicetree hardware description. Dependencies include clock and power-domain providers, interrupt controllers, pinctrl if board routing needs it, graph bindings, and downstream bridge or connector bindings.

### Integration Points
The MediaTek DRM component framework uses the node to bind the DPI encoder and connect it to adjacent display blocks. Downstream bridge/connector nodes use `remote-endpoint` links to form a complete DRM display path.

### Risks
Clock-name ordering is a common failure mode because schemas validate names but driver code depends on exact resources. Incorrect graph endpoints can make the controller probe but produce no active connector. Board-specific pinctrl omissions can look like display timing failures.

### Test Signals
`dt_binding_check` should validate compatible/resource cardinality and graph syntax. Runtime tests are DPI probe, clock enable sequencing, bridge attachment, mode-set success, and pixel output on representative boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dpi.yaml -->
