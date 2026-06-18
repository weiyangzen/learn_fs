<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/hdmi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/hdmi.yaml

### Purpose
This binding describes Qualcomm MSM HDMI transmitter nodes used with MDSS/MDP display pipelines.

### Important APIs, Types, And Functions
The schema defines compatible values for HDMI TX variants, register ranges and names, interrupts, clock resources, power supplies/regulators, PHY linkage, DDC/I2C relationships, and graph ports connecting MDP input to connector or bridge output.

### Control Flow
The binding is declarative. Compatible and resource lists constrain the transmitter generation, while graph endpoints define the route from display controller to external HDMI sink.

### State, Persistence, And Dependencies
Persistent state is the DT hardware description for TX registers, clocks, regulators, PHY, DDC, and graph. Dependencies include MDSS interrupt hierarchy, HDMI PHY bindings, clock/regulator providers, DDC I2C adapter, graph schemas, and connector bindings.

### Integration Points
The msm HDMI driver binds as a display encoder/bridge. It consumes pixels from MDP/MDSS and exposes connector behavior including EDID and hotplug through associated DDC/PHY resources.

### Risks
HDMI nodes are sensitive to PHY and DDC topology. A display path may bind without EDID if DDC is wrong. Regulator omissions can appear as unstable hotplug or link failures.

### Test Signals
Run binding checks and board DTS validation. Runtime signals include HDMI TX probe, PHY attach, EDID reads, HPD interrupt delivery, modeset at common resolutions, and audio/clock behavior if supported by the variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/hdmi.yaml -->
