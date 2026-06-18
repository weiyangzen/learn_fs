# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.h

Purpose: public Southern Islands common header shared by SI-era amdgpu blocks.

Important APIs, types, and functions: declares `SI_FLUSH_GPU_TLB_NUM_WREG`, `si_srbm_select()`, and `si_set_ip_blocks()`. The TLB flush constant is consumed by SDMA ring sizing; the function declarations connect common SI selection and device IP registration to other IP files.

Control flow: this header has no runtime flow. It enables compile-time linkage so GFX/GMC/SDMA/common code can call SRBM selection and top-level IP block registration.

State and persistence: no state is stored here; the declared functions mutate `amdgpu_device` hardware and software state in their implementations.

Dependencies and integration points: depends on `struct amdgpu_device` and basic fixed-width types being visible through including translation units. It is included by SI common and SDMA code.

Risks and test signals: risks are limited to ABI drift between declarations and definitions. Build coverage catches signature mismatches; runtime test signals come from successful SI IP block registration and VM flush ring sizing.
