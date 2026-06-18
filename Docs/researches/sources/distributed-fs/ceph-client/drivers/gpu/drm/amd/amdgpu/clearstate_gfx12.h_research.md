# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx12.h

## Purpose
`clearstate_gfx12.h` is the compact GFX12 clear-state table used by GFX12 AMDGPU graphics code. It defines the context-register clusters that are written into the newer RLC clear-state buffer format for GFX12 and GFX12.1 consumers.

## Important APIs, Types, and Data
The file defines six `static const unsigned int gfx12_SECT_CONTEXT_def_*[]` arrays, `gfx12_SECT_CONTEXT_defs[]`, and `gfx12_cs_data[]`. It uses `struct cs_extent_def` and `struct cs_section_def`, and is protected by `__CLEARSTATE_GFX12_H_`.

Unlike older clearstate headers, the table is much smaller. Extents are `0x0000a03e` for 34 registers, `0x0000a0cc` for 2, `0x0000a0d8` for 1, `0x0000a0db` for 6, `0x0000a2e5` for 11, and `0x0000a3c0` for 8. Comments identify the covered registers as memory temporal/speculative-read controls, 16 viewport TL/BR pairs, programmable near clip/rate control, perfmon context control, cliprect extension registers, HIZ/HIS metadata registers, binner controls, and `CB_MEM0_INFO` through `CB_MEM7_INFO`. All listed payload values are zero.

## Control Flow and Integration
There is no local execution path. `gfx_v12_0.c` and `gfx_v12_1.c` include this file and assign `adev->gfx.rlc.cs_data = gfx12_cs_data`. The GFX12 clear-state buffer builder differs from prior generations: `gfx_v12_0_get_csb_size()` starts with one dword for a cluster count and then adds `2 + reg_count` per extent, while `gfx_v12_0_get_csb_buffer()` writes `{reg_count, reg_index, payload...}` clusters and stores the final cluster count in `buffer[0]`. It does not build the older packet preamble format in this path.

## State and Persistence Behavior
The table is immutable rodata and has no runtime state. Its values are copied to the allocated RLC clear-state object during graphics initialization and reused across normal driver lifecycle events. Because every payload value is zero, the table primarily acts as a whitelist of GFX12 context registers that must be reset by clear-state, rather than carrying many generation-tuned nonzero defaults.

## Dependencies
Dependencies are the GFX12 register address map, `clearstate_defs.h`, and the GFX12/GFX12.1 clear-state buffer builders. The table assumes the consumer interprets `reg_index` as the hardware context-register index expected by the GFX12 RLC firmware format, not as an offset adjusted by `PACKET3_SET_CONTEXT_REG_START`.

## Risks
The small table makes missing coverage the key risk. If a register that should be reset is absent, stale context state may leak across queues or submissions. If the cluster count or extent lengths become inconsistent with the arrays, RLC firmware may parse the buffer incorrectly. Because all payloads are zero, accidental zeroing of a register that requires a nonzero architectural default is also a generation-porting risk.

## Test Signals
Signals include successful initialization in `gfx_v12_0_rlc_init()`/`gfx_v12_1` paths, valid clear-state buffer size/count, no RLC firmware errors, clean suspend/resume, and rendering tests that exercise viewport setup, clip rectangles, HIZ/HIS, binner behavior, and color-buffer memory info. Static validation should compare the six declared counts to the actual arrays and confirm the cluster count written by the consumer is six.
