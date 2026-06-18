<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,seattle.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,seattle.yaml

### Purpose
Defines root-node compatible strings for AMD Seattle SoC platforms.

### Important APIs, Types, And Functions
Constrains $nodename to / and compatible to amd,seattle-overdrive followed by amd,seattle.

### Control Flow
The schema validates Seattle Overdrive root compatible ordering and allows additional root properties.

### State, Persistence, And Dependencies
No runtime state. Depends on devicetree core meta-schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks are minimal beyond stale platform coverage.

### Test Signals
Test signals include dt_binding_check for valid compatible pair and invalid order rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,seattle.yaml -->
