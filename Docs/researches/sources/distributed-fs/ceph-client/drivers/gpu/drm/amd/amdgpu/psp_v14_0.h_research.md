# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v14_0.h

Purpose: declares PSP v14 callback installation and the SPI ROM update timeout.

Important APIs/types/functions: defines `PSP_SPIROM_UPDATE_TIMEOUT` as 60000 ms and declares `void psp_v14_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no local executable flow. The timeout is used by SPI update polling; the setter is used by PSP discovery.

State and persistence behavior: no state. Runtime state is assigned by `psp_v14_0_set_psp_funcs()` in the implementation.

Dependencies and integration points: includes `amdgpu_psp.h` and integrates with MPASP PSP support and VBIOS flash callbacks.

Risks and test signals: risk is timeout mismatch with actual PSP flash latency or missing callback selection. Test signals are compile coverage, function table installation, and SPI update timing behavior.
