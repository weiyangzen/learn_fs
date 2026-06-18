<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arc/snps,archs-pct.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arc/snps,archs-pct.yaml

### Purpose
Defines the binding for ARC HS pipeline performance counters.

### Important APIs, Types, And Functions
Requires compatible const snps,archs-pct, one reg entry, and one clocks entry; additionalProperties is false.

### Control Flow
The schema validates a single performance counter hardware block capable of counting CPU/cache events and overflow interrupts as described.

### State, Persistence, And Dependencies
No runtime state; it constrains DTS nodes and generates docs. Depends on devicetree core schema and generic reg/clocks schemas.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include no interrupt property despite description mentioning overflow interrupts, which may be intentional or incomplete.

### Test Signals
Test signals include dt_binding_check with valid compatible/reg/clocks and rejection of extra properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arc/snps,archs-pct.yaml -->
