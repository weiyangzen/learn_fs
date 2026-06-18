# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.h

Purpose: this header defines the DCE/DCN ABM register metadata contract and the concrete `struct dce_abm` type used by `dce_abm.c`. It provides register lists and mask/shift lists for multiple generations, including DCE110, DCN1.0, DCN2.0, DCN3.0/3.01/3.02, DCN3.2, DCN3.5, DCN4.0.1, and DCN4.2 ABM layouts.

Important APIs and types: register-list macros include `ABM_COMMON_REG_LIST_DCE_BASE()`, `ABM_DCE110_COMMON_REG_LIST()`, `ABM_DCN10_REG_LIST(id)`, `ABM_DCN20_REG_LIST()`, `ABM_DCN301_REG_LIST(id)`, `ABM_DCN302_REG_LIST(id)`, and `ABM_DCN30_REG_LIST(id)`. Mask/shift macros include `ABM_COMMON_MASK_SH_LIST_DCE_COMMON_BASE`, `ABM_MASK_SH_LIST_DCE110`, `ABM_MASK_SH_LIST_DCN10`, `ABM_MASK_SH_LIST_DCN20`, `ABM_MASK_SH_LIST_DCN30`, `ABM_MASK_SH_LIST_DCN35`, `ABM_MASK_SH_LIST_DCN32`, `ABM_MASK_SH_LIST_DCN401`, and `ABM_MASK_SH_LIST_DCN42`. `ABM_REG_FIELD_LIST(type)` defines fields shared by `struct dce_abm_shift` and `struct dce_abm_mask`. `struct dce_abm_registers` stores ABM and DMCU register offsets. `struct dce_abm` embeds `struct abm` plus register metadata pointers. Public functions are `dce_abm_create()` and `dce_abm_destroy()`.

Control flow: resource files expand the generation-specific register and mask macros to create metadata tables. `dce_abm.c` uses those tables through `REG_*`/`FN` macros when it initializes ABM and sends DMCU commands.

State and persistence: the header has no runtime state. The structs it defines hold per-object pointers to immutable register metadata and the inherited mutable `struct abm` runtime state.

Dependencies and integration: it includes `abm.h` for the base object and callback interface. NBIO scratch register macros appear in DCN register lists where BIOS scratch access is routed through NBIO. The newer DCN401/DCN42 mask lists include ACE piecewise-linear and histogram readback fields used by newer ABM/DMUB paths even though `dce_abm.c` itself programs only the older subset.

Risks: the header supports many hardware generations with macro concatenation, so generated register-name drift can break only one ASIC path. Some newer mask lists include fields not present in older register lists, requiring resource definitions to pair the right macro set. `ABM_MASK_SH_LIST_DCN35` maps only the DCN10 common fields, omitting master communication fields, which is only safe if that generation's ABM path does not use the DCE DMCU command helpers. Macro growth increases the chance of fields being present in masks but absent from `struct dce_abm_registers` or vice versa.

Test signals: compile resource tables for each ABM generation macro, verify `struct dce_abm_shift` and `struct dce_abm_mask` cover every field used by `dce_abm.c`, boot-test DCE/DCN ABM initialization and DMCU command paths, and validate newer DCN401/DCN42 ACE/histogram field mappings with their consumers.
