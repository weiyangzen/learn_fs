# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 4821-7169

## Purpose

This chunk is a generated AMD GC 9.2.1 register bitfield header. It does not implement executable logic; it defines the `_SHIFT` and `_MASK` constants that the AMDGPU driver uses with `REG_SET_FIELD()` and `REG_GET_FIELD()` to compose or decode 32-bit hardware register values. The covered range starts in the middle of the graphics backend tiling table definitions and ends partway through `VM_CONTEXT13_CNTL`.

The chunk covers these register groups:

- `GB_TILE_MODE11` through `GB_TILE_MODE31` and `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15`, which describe graphics backend tile and macrotile layout fields.
- Color buffer controls such as `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, and `CB_DCC_CONFIG`.
- Render backend fuse/harvest controls through `GC_USER_RB_REDUNDANCY` and `GC_USER_RB_BACKEND_DISABLE`.
- `gc_ea_gceadec2` fields for GCEA performance counters, diagnostic/static memory controls, TCC crossbar credits, probe mapping, error status, DRAM arbitration, and SDP credit/backdoor enable controls.
- `gc_rmi_rmidec` fields for RMI request path control, status, UTCL1 interaction, xbar/demux arbitration, scoreboard/invalidation state, clock control, and spare registers.
- `gc_utcl2_atcl2dec` and `gc_utcl2_vml2pfdec` fields for ATC L2, VM L2 cache control, page fault/default page handling, identity aperture mapping, parity controls, and clock gating.
- `gc_utcl2_vml2vcdec` fields for `VM_CONTEXT0_CNTL` through the first part of `VM_CONTEXT13_CNTL`, defining per-VMID page table depth/block size and fault interrupt/default behavior.

## Important APIs, Types, And Macros

There are no functions or C types in this range. The public surface is a set of preprocessor constants named as:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The constants are consumed by the common AMDGPU bitfield helpers in `drivers/gpu/drm/amd/amdgpu/amdgpu.h`:

- `REG_SET_FIELD(orig_val, reg, field, field_val)` clears `reg__field_MASK` in `orig_val` and inserts `field_val << reg__field__SHIFT`.
- `REG_GET_FIELD(value, reg, field)` masks `value` with `reg__field_MASK` and shifts it down by `reg__field__SHIFT`.

The companion address definitions are in `gc_9_2_1_offset.h`. This mask header is included directly by `amdgpu/gfxhub_v1_1.c` and by `pm/powerplay/hwmgr/vega12_inc.h`; `gfxhub_v1_1.c` is the concrete GC 9.2.1 consumer in this tree.

## Register Areas In This Chunk

`GB_TILE_MODE11` through `GB_TILE_MODE31` repeat the same five fields: `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, `MICRO_TILE_MODE_NEW`, and `SAMPLE_SPLIT`. These are hardware layout encodings used by the graphics backend for tiled surfaces. The range starts with the final two masks for `GB_TILE_MODE10`, so chunk reconciliation needs to account for the split from the previous chunk.

`GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15` define `BANK_WIDTH`, `BANK_HEIGHT`, `MACRO_TILE_ASPECT`, and `NUM_BANKS`. These constants describe the macrotiling memory-bank layout and must remain consistent with the tile mode register offsets and any users that decode tiling metadata.

The `CB_*` section defines color buffer cache, blend, fast-clear, DCC, and memory arbiter controls. Notable fields include cache eviction/tag counts, FIFO depths, several disable/workaround bits, read/write arbiter weights, and DCC overwrite-combiner behavior. These bits affect render target cache behavior and color/depth compression paths.

`GC_USER_RB_REDUNDANCY` and `GC_USER_RB_BACKEND_DISABLE` expose render backend redundancy/disable masks. Other generations read these fields to account for harvested or disabled render backends when deriving active RB topology; the same naming convention enables generation-specific code to use common field helpers.

The `GCEA_*` section covers graphics client/event/address path controls: diagnostic memory single-write/error injection fields, TCC crossbar credit and max-burst fields, probe routing maps, error status bits, DRAM-bank arbitration, and SDP backdoor credit accounting. These are low-level performance, diagnostics, and fabric-credit knobs rather than ordinary runtime state.

The `RMI_*` section describes the request memory interface between graphics clients, render backends, UTCL1/UTCL2, and memory. It includes xbar muxing and arbitration, harvest bits for RB paths, skid FIFO errors, UTCL1 invalidation control, TCIW formatter behavior, scoreboard flush/invalidation status, and clock/spare controls. The scoreboard fields are particularly relevant to VMID invalidation progress and flush completion signals.

The `ATC_L2_*` section defines address translation cache L2 controls and status fields. These cover translation request limits, bank selection, cache update modes, cache data inspection, parity status, memory light sleep, and clock-gating timer/override fields.

The `VM_L2_*` section defines the graphics VM L2 behavior: cache enablement, fragment processing, endian-swap modes, queue sizing, page fault classification, dummy/default page addresses, fault status/address capture, identity aperture low/high bounds, physical offset, MM group request classes, reserved client ID bank selection, parity control, and VM L2 clock gating.

`VM_CONTEXT0_CNTL` through `VM_CONTEXT13_CNTL` are per-context VM controls. Each full context block defines `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry controls, and interrupt/default-enable bits for range, dummy-page, PDE0, valid, read, write, and execute protection faults. The chunk ends inside `VM_CONTEXT13_CNTL`; later lines continue that register and subsequent contexts.

## Control Flow

This header has no runtime control flow. The effective control flow appears in users that include this file:

1. Driver code reads or constructs a 32-bit register value.
2. `REG_SET_FIELD()` uses the `_MASK` and `_SHIFT` macros to update a specific field.
3. The driver writes the value with SOC15 register accessors such as `WREG32_SOC15*()`, or decodes a read value with `REG_GET_FIELD()`.

For GC 9.2.1, `gfxhub_v1_1.c` includes this header and the matching offset header. That source uses the same register metadata style for XGMI and graphics hub setup. The VM L2 and context fields in this chunk align with the common gfxhub initialization pattern used across neighboring `gfxhub_v1_2.c` and `mmhub_v1_*` implementations: configure `VM_L2_CNTL*`, initialize `VM_CONTEXT0_CNTL`, program `VM_CONTEXT1_CNTL + i * ctx_distance`, and set `ctx_distance` from adjacent context register offsets.

## State And Persistence Behavior

The file itself has no mutable state. The macros describe persistent hardware register state:

- Tile/macrotile and color buffer fields influence GPU memory layout, render target cache policy, DCC behavior, and render backend availability.
- GCEA/RMI/ATC/VM fields affect request routing, credit accounting, diagnostic injection, cache/parity status, VM invalidation, and fault response.
- `VM_L2_PROTECTION_FAULT_STATUS` and fault address registers describe latched fault state. Fields such as `CLEAR_PROTECTION_FAULT_STATUS_ADDR` and `ALLOW_SUBSEQUENT_PROTECTION_FAULT_STATUS_ADDR_UPDATES` control whether captured fault addresses are cleared or overwritten.
- `VM_CONTEXT*_CNTL` fields persist per VM context until reprogrammed during GPU initialization, reset, suspend/resume, or VM hub reconfiguration.

Because these constants encode a hardware ABI, persistence is in the GPU registers, not in this header. Incorrect masks or shifts can silently write the wrong bit and persist until the next register programming sequence or reset.

## Dependencies And Integration Points

This chunk depends on the AMD GC 9.2.1 hardware register specification and must match `gc_9_2_1_offset.h` register addresses. It also depends on the `REG_SET_FIELD()`/`REG_GET_FIELD()` macro contract, which assumes exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names.

Primary integration points:

- `amdgpu/gfxhub_v1_1.c` includes `gc/gc_9_2_1_offset.h` and `gc/gc_9_2_1_sh_mask.h`, tying these bit definitions to graphics hub register programming.
- `pm/powerplay/hwmgr/vega12_inc.h` includes this file for Vega12 power management paths that need GC register field names.
- SOC15 register access macros (`RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and offset variants) combine with this header and the offset header to address and manipulate actual MMIO registers.
- VM fault interrupt handling elsewhere in AMDGPU/AMDKFD depends on correctly programmed VM context and VM L2 fault bits, even when the direct handling code uses generation-specific aliases.

## Risks

The main risk is bitfield drift from the hardware specification. A wrong shift or mask can corrupt neighboring fields, for example enabling the wrong VM fault response, misprogramming page table depth/block size, breaking tile layout interpretation, or disabling a color buffer optimization unexpectedly.

This range includes many repeated register families. Copy/paste or generator errors are easy to miss, especially in `GB_TILE_MODE*`, `GB_MACROTILE_MODE*`, and `VM_CONTEXT*_CNTL`, where most blocks are intentionally identical except the register prefix. The range boundary is also split: it starts with two `GB_TILE_MODE10` masks and ends inside `VM_CONTEXT13_CNTL`, so merge tooling must preserve continuity with adjacent chunks.

Several fields are diagnostic or fault-injection controls (`GCEA_DSM_CNTL*`, `GCEA_DSM_CNTL2*`, parity/fault controls). Accidental writes in production paths could create artificial memory/fabric errors or alter fault recovery behavior.

VM fields are high risk because they affect GPU virtual memory isolation and page fault handling. Misprogramming retry/default bits can convert recoverable faults into fatal behavior, suppress interrupts, or route invalid accesses to dummy/default pages.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Kernel build coverage for configurations that compile `gfxhub_v1_1.c` and Vega12 powerplay includes catches missing or renamed macros.
- Boot/probe on GC 9.2.1 ASICs should complete graphics hub setup without register programming failures.
- GPUVM tests should exercise VM context setup, page table depth/block size, VMID invalidation, and fault handling paths.
- Fault injection or negative VM tests should produce expected `VM_L2_PROTECTION_FAULT_STATUS`, fault address, VMID, client ID, read/write/execute, and retry/no-retry behavior.
- Render and display workloads using tiled render targets should validate that tile/macrotile and CB/DCC fields remain compatible with surface layout and compression expectations.
- RAS/parity diagnostics should validate ATC/VM L2 parity status and clear paths where hardware support is available.
