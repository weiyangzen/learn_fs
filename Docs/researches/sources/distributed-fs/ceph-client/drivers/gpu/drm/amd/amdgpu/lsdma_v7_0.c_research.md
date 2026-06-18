<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.c

Purpose: implements LSDMA 7.0 PIO copy/fill and memory power-gating callbacks. The code mirrors v6.0 behavior against the 7.0 register namespace.

Important APIs and functions: `lsdma_v7_0_wait_pio_status()` polls idle and FIFO-empty status. `lsdma_v7_0_copy_mem()` writes source/destination address registers and command fields including `BYTE_COUNT`, location, increment, overlap, and `CONSTANT_FILL = 0`. `lsdma_v7_0_fill_mem()` writes constant-fill data and destination address with `CONSTANT_FILL = 1`. `lsdma_v7_0_update_memory_power_gating()` toggles `MEM_POWER_CTRL_EN`. `lsdma_v7_0_funcs` exports the callback table.

Control flow: operations are synchronous direct-MMIO sequences. Each request programs registers, writes `regLSDMA_PIO_COMMAND`, waits through the shared LSDMA poll helper, and logs a device error if the poll fails.

State and persistence behavior: no local software state. Operation parameters persist only in LSDMA PIO registers; memory power-gating state persists in `regLSDMA_MEM_POWER_CTRL`.

Dependencies and integration points: depends on `lsdma_7_0_0_offset.h`, `lsdma_7_0_0_sh_mask.h`, SOC15 register macros, and common `amdgpu_lsdma` interfaces. It is selected by hardware/IP version and called through `struct amdgpu_lsdma_funcs`.

Risks and edge cases: size truncation into `BYTE_COUNT`, no local serialization, no explicit idle wait before command programming, and reliance on v7.0 field encodings matching v6.0 semantics. Power-gating toggles may race with active PIO if callers do not order them.

Test signals: memory copy/fill correctness, poll timeout logging, successful use on v7.0 hardware, and low-power transitions that call `update_memory_power_gating()` without breaking later PIO operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.c -->
