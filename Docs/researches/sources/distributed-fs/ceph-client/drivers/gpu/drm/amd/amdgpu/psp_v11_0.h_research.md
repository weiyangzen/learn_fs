# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0.h

Purpose: declares the PSP v11 callback installer.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v11_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no executable flow. The setter is invoked by AMDGPU IP discovery when a PSP v11 block is selected.

State and persistence behavior: no direct state. The setter stores the v11 `struct psp_funcs` pointer in `psp->funcs`.

Dependencies and integration points: built with the PSP v11 implementation and referenced from AMDGPU discovery and PSP setup paths.

Risks and test signals: declaration drift would break builds or wrong generation dispatch. Test signals are compile coverage and correct runtime function table selection for v11 ASICs.
