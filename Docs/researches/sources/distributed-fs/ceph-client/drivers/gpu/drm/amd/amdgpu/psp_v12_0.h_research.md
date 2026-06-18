# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v12_0.h

Purpose: declares the PSP v12 callback installer.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v12_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no direct flow. AMDGPU device setup calls the setter for v12 PSP IP blocks.

State and persistence behavior: no state here; `psp->funcs` is assigned by the implementation.

Dependencies and integration points: tied to AMDGPU PSP discovery and the `psp_v12_0.c` implementation.

Risks and test signals: declaration mismatch and missing discovery wiring are the relevant risks. Test signals are build coverage and proper v12 dispatch.
