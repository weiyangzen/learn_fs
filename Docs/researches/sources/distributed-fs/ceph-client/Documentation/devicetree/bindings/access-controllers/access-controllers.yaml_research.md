<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/access-controllers/access-controllers.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/access-controllers/access-controllers.yaml

### Purpose
Defines the common device-tree binding schema for generic domain access controller providers and consumers.

### Important APIs, Types, And Functions
Properties include #access-controller-cells, access-controller-names string-array, and access-controllers phandle-array. select: true makes the schema always participate, with additionalProperties allowed.

### Control Flow
The schema documents how consumer nodes reference one or more access controllers by phandle and optional arguments defined by provider-specific bindings.

### State, Persistence, And Dependencies
No runtime state; it validates DTS source and provides generated documentation. Depends on devicetree core meta-schema and /schemas/types.yaml definitions.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include broad select:true and additionalProperties:true making validation permissive; provider-specific cell semantics must be enforced elsewhere.

### Test Signals
Test signals include dt_binding_check and examples with multiple controllers and matching names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/access-controllers/access-controllers.yaml -->
