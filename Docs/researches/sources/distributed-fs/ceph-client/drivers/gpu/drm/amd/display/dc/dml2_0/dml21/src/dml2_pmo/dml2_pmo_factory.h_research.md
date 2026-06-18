## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_factory.h

### Purpose
This header declares the PMO factory entry point.

### Important APIs, Types, And Functions
It includes shared PMO types and top project enums, then declares `bool dml2_pmo_create(enum dml2_project_id project_id, struct dml2_pmo_instance *out)`.

### Control Flow
There is no runtime flow in the header. It establishes the creation contract used by top-level DML2 initialization.

### State, Persistence, And Dependencies
There is no local state. The output instance supplied to `dml2_pmo_create()` receives function pointers and persistent PMO state storage.

### Integration Points
Included by PMO implementations and by the SOC15 top initializer. It is the narrow boundary between project selection and concrete optimizer implementations.

### Risks
Because the factory only returns a boolean, callers must inspect or trust callback population per project. The header does not document which callbacks are mandatory for each project.

### Test Signals
Compile and initialization tests should validate all supported project IDs and confirm the top initializer rejects projects for which the factory returns false.
