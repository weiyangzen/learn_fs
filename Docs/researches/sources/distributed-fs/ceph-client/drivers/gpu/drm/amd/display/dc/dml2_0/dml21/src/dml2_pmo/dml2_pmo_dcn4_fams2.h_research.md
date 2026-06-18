## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn4_fams2.h

### Purpose
This header declares the DCN4 FAMS2 PMO interface implemented by `dml2_pmo_dcn4_fams2.c`.

### Important APIs, Types, And Functions
It forward-declares `struct display_configuation_with_meta` and exposes helper queries for vactive p-state margin and reserved vblank time. It declares initialization, DCC mcache optimization, vmin optimization, p-state optimization, stutter optimization, and base-strategy expansion functions using the `dml2_pmo_*_in_out` structs from `dml2_internal_shared_types.h`.

### Control Flow
The header itself has no runtime flow. Its declarations define the callable lifecycle used by the PMO factory and top-level optimization pipeline: create an instance, initialize it, then call `init`, `test`, and `optimize` functions for each optimization family.

### State, Persistence, And Dependencies
There is no local state. The file depends on `dml2_internal_shared_types.h` for PMO parameter structs and strategy types. All persistent optimizer data lives in `struct dml2_pmo_instance`.

### Integration Points
`dml2_pmo_factory.c` includes this header to assign function pointers. `dml2_top_soc15.c` reaches the functions indirectly through `struct dml2_pmo_instance`.

### Risks
The header exposes the misspelled type name `display_configuation_with_meta`, so downstream code is coupled to that spelling. Function declarations do not encode stream/plane count bounds, leaving those invariants to callers and implementation assertions.

### Test Signals
Build coverage should ensure the factory can include this header for all supported DCN4 project IDs and that every declared symbol is defined when the DCN4 FAMS2 object is linked.
