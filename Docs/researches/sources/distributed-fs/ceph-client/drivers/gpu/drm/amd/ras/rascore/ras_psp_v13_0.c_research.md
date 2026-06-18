# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp_v13_0.c

Purpose: this file provides PSP v13 ring write-pointer accessors for the generic PSP command transport.

Important functions: `ras_psp_v13_0_ring_wptr_get()` reads SOC15 MP0 register `regMP0_SMN_C2PMSG_67`. `ras_psp_v13_0_ring_wptr_set()` writes the same register with the new DWORD write pointer. `ras_psp_v13_0` exports these operations in a `struct ras_psp_ip_func`.

Control flow and state: the file is stateless; state lives in the PSP hardware register and the shared ring memory managed by `ras_psp.c`. There is no persistence.

Dependencies and integration: generic PSP init selects this table for PSP IP versions 13.0.6, 13.0.14, and 13.0.12. Command submission uses these callbacks to locate and advance the ring frame slot. Risks include incorrect register selection for future PSP v13 variants, no readback/validation in the setter, and reliance on caller conversion between byte and DWORD pointers. Test signals should mock register reads/writes, ring wrap handling in `ras_psp.c`, and supported IP version selection.
