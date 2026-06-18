# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0.h

Purpose: declares the PSP 15.0.0 callback installer.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v15_0_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no direct control flow. Device setup invokes the setter for PSP 15.0.0 hardware.

State and persistence behavior: no state. The setter stores a `struct psp_funcs` table in `psp->funcs`.

Dependencies and integration points: integrated with AMDGPU PSP discovery and `psp_v15_0.c`.

Risks and test signals: header guard naming and callback name drift are the main risks. Test signals are successful builds and correct PSP 15.0.0 dispatch.
