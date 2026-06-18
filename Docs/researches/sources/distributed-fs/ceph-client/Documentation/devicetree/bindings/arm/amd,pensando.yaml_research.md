<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,pensando.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,pensando.yaml

### Purpose
Defines root-node compatible strings for AMD Pensando Elba SoC platforms.

### Important APIs, Types, And Functions
Constrains $nodename to / and compatible to amd,pensando-elba-ortano followed by amd,pensando-elba.

### Control Flow
The schema validates root compatible ordering for Pensando Elba boards while allowing additional root properties.

### State, Persistence, And Dependencies
No runtime state. Depends on devicetree core meta-schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks are mainly board-list staleness and permissive additionalProperties true.

### Test Signals
Test signals include valid ortano compatible pair and rejection of missing SoC fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,pensando.yaml -->
