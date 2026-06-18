<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.c

Purpose: implements LSDMA 6.0 PIO helper functions for synchronous memory copy, constant fill, and memory power-gating updates. The exported function table lets common AMDGPU LSDMA code issue low-speed DMA PIO operations through IP-version-specific registers.

Important APIs and functions: `lsdma_v6_0_wait_pio_status()` polls `regLSDMA_PIO_STATUS` until both idle and FIFO-empty bits are set. `lsdma_v6_0_copy_mem()` writes source and destination addresses, clears PIO control, sets `BYTE_COUNT`, source/destination location, increment, overlap, and constant-fill fields, then waits for completion. `lsdma_v6_0_fill_mem()` programs fill data and destination address, sets `CONSTANT_FILL`, and waits. `lsdma_v6_0_update_memory_power_gating()` toggles `MEM_POWER_CTRL_EN`. `lsdma_v6_0_funcs` exports these callbacks.

Control flow: copy/fill operations are immediate and synchronous. They program registers directly, issue the command by writing `regLSDMA_PIO_COMMAND`, poll for completion through `amdgpu_lsdma_wait_for()`, and log an error on timeout/failure.

State and persistence behavior: no software state is retained in this file. Hardware state persists in PIO source/destination/data/control/command/status registers and in `regLSDMA_MEM_POWER_CTRL`. The power-gating helper explicitly clears then sets the enable field to force a transition.

Dependencies and integration points: depends on SOC15 LSDMA 6.0 generated offsets/masks, `amdgpu_lsdma_wait_for()`, AMDGPU MMIO helpers, and `struct amdgpu_lsdma_funcs`. Callers are expected to serialize operations if the PIO engine is shared.

Risks and edge cases: `size` is `uint64_t` but is assigned into the hardware `BYTE_COUNT` field, so oversized requests may truncate. The code assumes address increment fields of zero are the desired hardware encoding. There is no explicit pre-wait for idle before programming a new operation beyond the post-command wait. Memory power-gating updates are not protected by a local lock.

Test signals: issue small and maximum-sized copy/fill operations, verify destination contents, exercise timeout handling by forcing the status poll to fail, check register field encodings against LSDMA 6.0 docs, and validate memory power-gating toggles around suspend or low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.c -->
