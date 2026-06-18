<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/actions.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/actions.yaml

### Purpose
Defines root-node compatible strings for Actions Semi S500, S700, and S900 platforms.

### Important APIs, Types, And Functions
The schema constrains $nodename to / and compatible to oneOf board-specific item chains ending in SoC compatibles such as actions,s500, actions,s700, or actions,s900.

### Control Flow
It validates board DTS root compatible ordering and leaves additionalProperties true for normal root-node content.

### State, Persistence, And Dependencies
No runtime state; used by dt-schema and docs generation. Depends on core devicetree meta-schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include board list staleness and permissive additional properties.

### Test Signals
Test signals include valid board compatible arrays and rejection of wrong ordering or missing SoC fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/actions.yaml -->
