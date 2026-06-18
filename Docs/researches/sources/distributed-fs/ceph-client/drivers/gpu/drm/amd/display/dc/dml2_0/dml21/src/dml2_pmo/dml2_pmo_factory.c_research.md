## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_factory.c

### Purpose
`dml2_pmo_factory.c` constructs a `dml2_pmo_instance` by selecting PMO implementation callbacks for a DML2 project ID.

### Important APIs, Types, And Functions
The exported API is `dml2_pmo_create()`. It installs DCN3 callbacks, DCN4 FAMS2 callbacks, or dummy stutter callbacks depending on `enum dml2_project_id`. The dummy stutter functions are local placeholders used for DCN3-backed projects.

### Control Flow
The factory rejects a null output pointer, zeroes the instance, then switches on `project_id`. `dml2_project_dcn4x_stage1` gets DCN4 initialize and DCC mcache optimization only. `dml2_project_dcn40` and `dml2_project_dcn4x_stage2` get DCN3 PMO callbacks plus dummy stutter hooks. `dml2_project_dcn42` and `dml2_project_dcn4x_stage2_auto_drr_svp` get the full DCN4 FAMS2 callback set. Invalid or unknown projects return false.

### State, Persistence, And Dependencies
The only state change is the zeroed and populated `struct dml2_pmo_instance` provided by the caller. Dependencies include the DCN3 PMO implementation, DCN4 FAMS2 PMO implementation, `dml2_external_lib_deps.h` for memory helpers, and shared PMO types.

### Integration Points
`dml2_top_soc15_initialize_instance()` calls this after MCG, DPMM, and core creation. The top optimization phases later invoke callbacks through the populated `dml2_pmo_instance`.

### Risks
The stage1 DCN4 case leaves vmin, p-state, and stutter callbacks unset, so top code must only call features valid for that project or guard null pointers. Dummy stutter behavior returns `init=false`, `test=true`, and `optimize=false`, which makes stutter a no-op but can hide accidental use unless tests assert project-specific behavior.

### Test Signals
Tests should instantiate every project ID and verify the expected callback table, null-output rejection, invalid-project rejection, and that unsupported optimization phases are either not called or gracefully skipped by top-layer orchestration.
