<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi-ddc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi-ddc.yaml

### Purpose
This schema documents the MT8195-series HDMI DDC block. It models the DDC channel used by MT8195 HDMI transmitters for EDID and related I2C transactions.

### Important APIs, Types, And Functions
The binding requires `compatible`, one clock, and a power-domain reference. Unlike older HDMI DDC bindings, this MT8195 schema does not define separate `reg` or interrupt properties in the visible contract, matching the SoC integration style.

### Control Flow
Validation accepts the MT8195-series compatible and required power/clock resources. There is no runtime control flow in the schema.

### State, Persistence, And Dependencies
The persistent state is the DDC resource relationship in devicetree. Dependencies include the HDMI transmitter, display clock provider, PM domain provider, and connector/bridge nodes that need EDID access.

### Integration Points
This node is paired with the MT8195 HDMI TX binding. It supplies the DDC service path used during connector discovery and mode enumeration.

### Risks
Because the contract is sparse, board integration errors may surface only at runtime. Missing power-domain linkage can make DDC fail while the HDMI node itself appears valid. Confusing this binding with older `mediatek,hdmi-ddc.yaml` can add invalid properties.

### Test Signals
Use `dt_binding_check` for the MT8195 DDC node and runtime EDID reads through the HDMI connector. Probe logs should show clock and power-domain acquisition without legacy register/interrupt assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi-ddc.yaml -->
