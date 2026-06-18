## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_soc15.h

### Purpose
This header declares the SOC15 top implementation and mcache helper APIs.

### Important APIs, Types, And Functions
It exposes `dml2_top_soc15_initialize_instance()`, mcache count/offset calculation, global mcache ID assignment, admissibility validation, and mcache programming construction.

### Control Flow
There is no runtime flow in the header. The declarations correspond to initialization, mode optimization support, and final hubp mcache programming stages.

### State, Persistence, And Dependencies
There is no local state. The functions operate on `struct dml2_instance` and parameter structs defined in `dml2_internal_shared_types.h`.

### Integration Points
Included by top interface dispatch and potentially by wrapper/resource code that needs direct mcache helper access.

### Risks
The API exposes low-level mcache helpers that mutate allocation arrays in place, so callers need clear ownership of the parameter storage. The misspelled `admissability` spelling is part of the symbol name.

### Test Signals
Build tests should verify all declarations are defined and callable in SOC15 builds; integration tests should exercise the direct mcache helper path used by mode support and programming.
