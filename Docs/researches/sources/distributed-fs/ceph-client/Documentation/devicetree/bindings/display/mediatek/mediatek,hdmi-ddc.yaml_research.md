<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi-ddc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi-ddc.yaml

### Purpose
This schema defines the MediaTek HDMI DDC I2C controller used to access HDMI DDC pins for EDID and related display transactions.

### Important APIs, Types, And Functions
The node contract is small: `compatible` for supported SoCs, one `reg`, one interrupt, one clock, and `clock-names = "ddc-i2c"`. `additionalProperties: false` keeps the node limited to the DDC controller resources.

### Control Flow
There is no executable flow. The schema accepts only listed compatible values and requires the register, interrupt, and clock resources needed by the I2C/DDC driver.

### State, Persistence, And Dependencies
The persistent hardware description names the DDC controller and its clock. Dependencies include the peripheral clock provider, interrupt controller, and HDMI connector/encoder nodes that reference the DDC bus.

### Integration Points
The HDMI encoder or connector uses this I2C adapter for EDID reads. It is separate from the HDMI transmitter node so board descriptions can connect DDC cleanly through connector properties.

### Risks
The controller register region is small, so incorrect size or base addresses are easy to overlook. A wrong clock-name breaks driver lookup. HDMI may probe but lack EDID if this node or connector link is wrong.

### Test Signals
Run `dt_binding_check` for required fields. Runtime signals are DDC I2C adapter creation, successful EDID reads, hotplug display mode discovery, and no clock lookup errors during HDMI probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi-ddc.yaml -->
