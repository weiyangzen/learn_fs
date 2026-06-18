# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn201/dcn201_hubbub.h

Purpose: Declares DCN2.01 hubbub register/mask lists and constructor.

Important APIs and types: `HUBBUB_REG_LIST_DCN201` includes common hubbub registers, VM watermark registers, and CRC control. `HUBBUB_MASK_SH_LIST_DCN201` includes common masks plus global timer refdiv. `hubbub201_construct` installs the generation-specific function table on a `dcn20_hubbub` object.

Control flow: resource code expands these macros for DCN201 static register metadata and calls the constructor during resource pool setup.

State and persistence: no unique state beyond the reused `dcn20_hubbub` object.

Dependencies and integration: includes `dcn20_hubbub.h`. Integrated by DCN201 resource creation.

Risks and test signals: reduced register coverage relative to DCN20 must match hardware. Build tests should ensure all fields used by `hubbub201_program_watermarks` exist in the generated tables.
