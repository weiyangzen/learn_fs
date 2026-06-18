## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_interfaces.c

### Purpose
`dml2_top_interfaces.c` is the public top-level dispatch layer for DML2. It exposes instance sizing, initialization, mode support, mode programming, and mcache programming entry points.

### Important APIs, Types, And Functions
The file defines `dml2_get_instance_size_bytes()`, `dml2_initialize_instance()`, `dml2_check_mode_supported()`, `dml2_build_mode_programming()`, and `dml2_build_mcache_programming()`.

### Control Flow
Initialization switches on `options.project_id` and routes supported DCN4/DCN40/DCN42 projects to `dml2_top_soc15_initialize_instance()`. The other top-level APIs validate that the corresponding function pointer is installed in `in_out->dml2_instance->funcs` and then dispatch to the SOC15 implementation.

### State, Persistence, And Dependencies
This file holds no state. State belongs to the caller-provided `struct dml2_instance`, whose size is returned by `dml2_get_instance_size_bytes()` and whose `funcs` table is filled by the initializer. Dependencies are `dml_top.h`, `dml2_internal_shared_types.h`, and the SOC15 top header.

### Integration Points
This is the ABI-style entry used by wrappers and callers that do not know the project-specific implementation. It bridges external top interfaces to `dml2_top_soc15.c`.

### Risks
The dispatch functions assume non-null `in_out` and `in_out->dml2_instance`; only missing function pointers are guarded. Unsupported project IDs return false at initialization, so callers must check initialization before using the instance.

### Test Signals
Tests should validate instance-size allocation, initialization for each supported project ID, invalid project rejection, and null callback rejection for manually corrupted instances.
