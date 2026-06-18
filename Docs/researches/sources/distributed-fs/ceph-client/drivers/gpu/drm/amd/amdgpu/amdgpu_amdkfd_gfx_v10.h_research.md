# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.h

Purpose: this header exposes GFX10 debug, address-watch, IQ wait, and limited HQD introspection helpers for reuse by GFX10.3 and other closely related implementations.

Important APIs: declarations cover debug trap enable/disable, trap override validation and programming, wave launch mode, TCP/SQ address watch setup and clear, IQ wait-time read and dequeue wait-count packet construction, and placeholder-style `hqd_get_pq_addr`, `hqd_reset`, and `hqd_sdma_get_doorbell` helpers. The signatures mirror `struct kfd2kgd_calls` callback slots.

Control flow and integration: `amdgpu_amdkfd_gfx_v10_3.c` includes this header and reuses the debug/address/IQ/HQD helper functions in its `gfx_v10_3_kfd2kgd` table while overriding queue load, PASID mapping, and SDMA register offsets. The base GFX10 file provides the definitions.

State and persistence: the header stores no state. Its declared functions manipulate SPI debug state, watchpoint registers, IQ wait registers, or report unsupported HQD values in the implementation.

Dependencies: consumers need AMDGPU core types, KFD preemption/debug UAPI types, and fixed-width integer types available before inclusion. This is a private driver header rather than UAPI.

Risks and test signals: since the header is a sharing boundary between base GFX10 and GFX10.3, changes can silently affect both tables. Compile coverage catches signature drift; runtime tests should include GFX10.3 debug trap and watchpoint flows to ensure shared helpers still match that hardware's register behavior.
