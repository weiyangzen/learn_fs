# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.h

Purpose: declares the DCN315 private resource-pool wrapper and factory used by the Display Core resource selection layer.

Important APIs/types/functions: defines `TO_DCN315_RES_POOL(pool)` for converting a base `struct resource_pool *` to `struct dcn315_resource_pool *`, declares external DML/IP parameter block `dcn3_15_ip`, defines `struct dcn315_resource_pool { struct resource_pool base; }`, and declares `dcn315_create_resource_pool(const struct dc_init_data *init_data, struct dc *dc)`.

Control flow: no runtime control flow in the header. Inclusion enables chip-family selection code to call `dcn315_create_resource_pool()` and lets the implementation recover the enclosing allocation during destruction.

State and persistence behavior: the only state shape introduced is a thin wrapper around the generic `resource_pool`; all persistent runtime state is owned by the constructed base pool in the `.c` file.

Dependencies and integration points: includes `core_types.h` for `struct resource_pool`, `struct dc_init_data`, and `struct dc`. The external `dcn3_15_ip` symbol connects this resource file to DCN315 DML/IP bounding-box data used when publishing `dc->dcn_ip->max_num_dpp`.

Risks and test signals: because the wrapper contains only `base`, lifetime and layout correctness depend on using the matching `TO_DCN315_RES_POOL` macro in the DCN315 destroy path. Build coverage should catch missing `dcn3_15_ip` or factory symbols; runtime probe should verify DCN315 selects this factory rather than a neighboring DCN31 variant.
