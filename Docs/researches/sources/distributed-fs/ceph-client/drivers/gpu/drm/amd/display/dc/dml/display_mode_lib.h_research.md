# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_lib.h

## Purpose
This header defines the main DML instance object, project enum, callback table, and public utility functions for initialization and logging. It is the core interface between resource/FPU code and the generated DML implementations.

## Important APIs, Types, And Functions
`enum dml_project` identifies supported DML generations up to `DML_PROJECT_DCN32`. `struct dml_funcs` contains callbacks for validation, recalculation, legacy RQ/DLG register calculation, and DCN32 v2 RQ/DLG register calculation. `struct display_mode_lib` stores IP params, SoC bounding box, selected project, `vba_vars_st`, logger pointer, callback table, a six-pipe DML pipe state array, and `validate_max_state`. Public functions are `dml_init_instance()`, `dml_get_status_message()`, `dml_log_pipe_params()`, and `dml_log_mode_support_params()`.

## Control Flow And State
The header has no implementation behavior, but it defines the state shape that all DML calculations mutate. Callers initialize the struct with a project-specific bounding box, call `validate`/`recalculate`, and then call the appropriate RQ/DLG callback family for hardware register derivation.

## Dependencies And Integration Points
Includes `dm_services.h`, `dc_features.h`, `display_mode_structs.h`, `display_mode_enums.h`, and `display_mode_vba.h`. It is consumed by `display_mode_lib.c`, generation-specific DML code, and ASIC FPU/resource code. The six-element `dml_pipe_state` reflects a fixed display pipe capacity assumption in this tree.

## Risks
The callback table contains both legacy and v2 RQ/DLG signatures; calling the wrong family for a project would corrupt arguments. The project enum currently ends at DCN32, so newer DCN35/DCN351 code initializing as DCN31 is a compatibility choice rather than a first-class project entry. Struct size and embedded generated VBA state make copying and initialization order important.

## Test Signals
Compile-time tests should catch callback signature mismatches. Runtime validation should ensure initialized `funcs` pointers are non-null for every active project and that DCN32 uses v2 callbacks. New DML projects should add enum values, dispatch table entries, and initialization tests together.
