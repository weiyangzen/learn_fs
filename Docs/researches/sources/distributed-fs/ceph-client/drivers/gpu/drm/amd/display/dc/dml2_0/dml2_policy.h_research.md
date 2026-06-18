<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.h

Purpose: declares the DML2.0 policy construction interface and scratch/parameter structures for synthetic SoC-state generation.

Important APIs/types/functions: `struct dml2_policy_build_synthetic_soc_states_params` carries input bounding box, input states, output states, DCFCLK STA list, and STA count. `struct dml2_policy_build_synthetic_soc_states_scratch` stores one temporary `soc_state_bounding_box_st` entry. Public functions are `dml2_policy_build_synthetic_soc_states()` and `build_unoptimized_policy_settings()`.

Control flow: no runtime flow in the header. The API separates scratch from inputs so callers can keep large temporary state inside `dml2_context` rather than on the stack.

State and persistence behavior: no direct state. The declared builder mutates the supplied output state table and policy struct.

Dependencies and integration points: includes `display_mode_core_structs.h` and is used by translation and FPU wrapper code before DML mode support.

Risks and test signals: callers must provide valid arrays and at least one initialized input state. Build/test coverage should validate the header remains synchronized with scratch members stored in `dml2_internal_types.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.h -->
