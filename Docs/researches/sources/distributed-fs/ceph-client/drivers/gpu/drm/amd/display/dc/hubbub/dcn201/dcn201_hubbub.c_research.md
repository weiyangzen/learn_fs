# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn201/dcn201_hubbub.c

Purpose: Implements the DCN2.01 hubbub variant by reusing DCN2 DCHUB/DCC/readback helpers while installing a simplified watermark program path.

Important APIs and functions: `hubbub201_program_watermarks` programs urgent and pstate watermarks, SAT level, outstanding request threshold, and self-refresh control, but does not program stutter/SR watermark registers. `hubbub201_construct` binds the DCN201 function table and initializes common DCN20 fields.

Control flow: the DCN201 vtable uses `hubbub2_update_dchub`, DCC helpers, `hubbub2_wm_read_state`, `hubbub2_get_dchub_ref_freq`, and `hubbub2_read_state`, with VM context init callbacks set to NULL. Watermark programming follows the same safe-lowering behavior via DCN1 helper calls.

State and persistence: uses the `dcn20_hubbub` struct, cached watermarks, detile buffer size, and hardware arbiter registers. No VMID initialization state is managed through this vtable.

Dependencies and integration: depends on DCN20 hubbub helpers and register helpers. Integrated by DCN2.01 resource construction for generation-specific behavior.

Risks and test signals: NULL VM callbacks mean callers must branch by capability before invoking them. Tests should verify DCN201 resource code does not call missing VM init functions and that absence of stutter watermark programming matches hardware expectations.
