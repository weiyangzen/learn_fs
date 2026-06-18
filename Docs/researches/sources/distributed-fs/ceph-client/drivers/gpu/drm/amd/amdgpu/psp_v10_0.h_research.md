# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.h

Purpose: declares the PSP v10 callback installer for Raven-family PSP support.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v10_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no direct control flow. Device discovery or ASIC setup calls the setter so the common PSP layer dispatches through v10-specific callbacks.

State and persistence behavior: no state is defined here. The setter persists a pointer to the file-local `psp_v10_0_funcs` table in `psp->funcs`.

Dependencies and integration points: integrated by AMDGPU PSP discovery and built via the AMDGPU Makefile with other PSP generation objects.

Risks and test signals: risks are declaration/definition drift and missing inclusion where v10 PSP blocks are selected. Test signals are successful builds and runtime selection of PSP v10 devices.
