## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_lsdma.c

Purpose: provides common wrapper helpers for LSDMA register polling, memory copy, and memory fill operations while chunking large transfers into hardware-supported maximum sizes.

Important APIs/functions: `amdgpu_lsdma_wait_for()` polls an MMIO register until `(value & mask) == reg_val` or `adev->usec_timeout` expires. `amdgpu_lsdma_copy_mem()` splits a copy into chunks of at most `AMDGPU_LSDMA_MAX_SIZE` and delegates to `adev->lsdma.funcs->copy_mem()`. `amdgpu_lsdma_fill_mem()` similarly chunks fills and calls `fill_mem()`.

Control flow: copy/fill reject zero-length requests with `-EINVAL`, then loop while bytes remain, choose `min(mem_size, 0x2000000)`, call the ASIC-specific function, propagate any error immediately, and advance addresses/remaining size. The wait helper uses microsecond polling with `udelay(1)`.

State and persistence: no state is owned here. Functions operate on device registers and pass-through transfer parameters to version-specific callbacks.

Dependencies/integration: depends on `adev->lsdma.funcs`, MMIO `RREG32`, `adev->usec_timeout`, and hardware-specific LSDMA implementations that program transfer engines.

Risks: wrappers do not null-check `adev->lsdma.funcs` or callback pointers, so callers/ASIC init must ensure LSDMA support before calling. Polling is busy-waiting and can consume CPU for long timeouts. Chunking advances byte addresses, so callback semantics must use byte sizes/addresses consistently.

Test signals: large copy/fill tests crossing 32 MiB boundaries, zero-size negative tests, callback error propagation, register wait timeout tests, and memory compare verification after LSDMA transfers.
