<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c

Purpose: implements LSDMA 7.1 PIO copy and constant-fill callbacks. Compared with v6.0/v7.0, the v7.1 command format uses `COUNT`, `RAW_WAIT`, and `CONSTANT_FILL` fields and does not expose a memory power-gating callback in its function table.

Important APIs and functions: `lsdma_v7_1_wait_pio_status()` polls idle and FIFO-empty status. `lsdma_v7_1_copy_mem()` programs source/destination addresses, clears PIO control, sets command `COUNT`, clears `RAW_WAIT`, clears `CONSTANT_FILL`, and waits. `lsdma_v7_1_fill_mem()` writes constant data, destination address, command `COUNT`, clears `RAW_WAIT`, sets `CONSTANT_FILL`, and waits. `lsdma_v7_1_funcs` exports copy and fill only.

Control flow: copy and fill are synchronous MMIO command sequences that complete only after `amdgpu_lsdma_wait_for()` observes idle and FIFO-empty status. Errors are reported with `dev_err()`.

State and persistence behavior: this file keeps no software state. The active request is represented by LSDMA PIO address, control, command, constant-fill, and status registers.

Dependencies and integration points: depends on generated LSDMA 7.1 offsets/masks, SOC15 register helpers, and common AMDGPU LSDMA polling/type definitions. The absence of `update_memory_power_gating` must be tolerated by common callers.

Risks and edge cases: size truncation into the hardware `COUNT` field, caller serialization requirements, no pre-command idle check, and behavior changes from v7.0 field names/semantics. Common code must not assume the memory power-gating callback exists.

Test signals: copy and fill data integrity, status polling on v7.1 hardware, timeout/error path coverage, and common LSDMA code safely handling a function table without memory power-gating support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c -->
