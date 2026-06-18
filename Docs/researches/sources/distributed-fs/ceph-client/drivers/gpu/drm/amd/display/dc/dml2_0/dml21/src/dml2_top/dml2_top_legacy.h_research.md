## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_legacy.h

### Purpose
This header declares the legacy top initializer.

### Important APIs, Types, And Functions
It includes `dml2_internal_shared_types.h` and declares `bool dml2_top_legacy_initialize_instance(struct dml2_initialize_instance_in_out *in_out)`.

### Control Flow
There is no runtime flow in the header.

### State, Persistence, And Dependencies
There is no local state. Any implementation would populate `struct dml2_instance` through the shared initialization parameter.

### Integration Points
It is included by the legacy source stub. The current public top interface in this subset does not dispatch to this initializer.

### Risks
The declaration can become a dangling API if no object defines it. If reintroduced, it must match the SOC15 initializer contract for function-table population and component creation.

### Test Signals
Compile/link coverage should determine whether any configuration references the legacy initializer and should fail loudly if the declaration is used without an implementation.
