# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0.h

Purpose: declares PSP v13 callback installation and the SPI ROM update timeout shared by the v13 implementation.

Important APIs/types/functions: defines `PSP_SPIROM_UPDATE_TIMEOUT` as 60000 ms and declares `void psp_v13_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no local flow. The timeout constant is consumed by SPI ROM update/dump command waits; the setter is called during PSP IP setup.

State and persistence behavior: no state. The implementation persists the callback table in `psp->funcs` and uses the timeout for hardware polling behavior.

Dependencies and integration points: includes `amdgpu_psp.h` and integrates with common PSP and VBIOS flashing code.

Risks and test signals: too-short or too-long SPI timeout values affect user-visible VBIOS flash operations. Test signals include compile coverage, callback selection, and SPI ROM update timing behavior.
