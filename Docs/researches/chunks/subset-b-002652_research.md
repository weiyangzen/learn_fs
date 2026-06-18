# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 7170-9632

## Scope

This chunk is a generated AMD GC 9.2.1 register shift/mask header slice. It contains C preprocessor `#define` constants only: each register field is represented as a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or runtime branches in this range.

The selected lines contain 2,127 `#define` statements covering 328 register macro groups. The chunk starts in the middle of `VM_CONTEXT13_CNTL`, then covers complete VM context controls for contexts 14 and 15, VM invalidation semaphore/request/ack/range registers, VM context page-table base/start/end address fields, GC shared VM aperture controls, and a large GCEA address/priority/decode register block. It ends inside `GCEA_IO_WR_PRI_URGENCY_MASK`, so that register's remaining CID shift/mask definitions continue in the next chunk.

Although this repository path is under `sources/distributed-fs/ceph-client`, this header is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem client behavior.

## Purpose

`gc_9_2_1_sh_mask.h` supplies the field-level bit positions and masks for GC 9.2.1 registers. Driver code includes it with the companion `gc_9_2_1_offset.h` so AMDGPU paths can build, update, and decode MMIO register values with symbolic field names rather than hard-coded bit constants.

This chunk focuses on graphics VM and GCEA memory-fabric surfaces:

- VM context enable/fault-policy fields for contexts 13 through 15.
- Context-wide disable bits for VM contexts 0 through 15.
- VM invalidation engines 0 through 17, including semaphore ownership, per-VMID request bits, flush type, L2/L1 PTE/PDE invalidation selectors, protection-fault-status clearing, acknowledgment bits, and optional address-range bounds.
- VM context page-table base, start, and end address fields for contexts 0 through 15.
- Shared VM/MC aperture, framebuffer, AGP, top-of-DRAM, HBM, XGMI local-framebuffer, PCI, steering, cacheable-address, and L1 TLB controls.
- GCEA DRAM and IO client-to-group maps, group-to-VC maps, lazy/CAM/page-burst controls, priority age/queue/fixed/urgency/quantum controls, urgency masks, address normalization, DRAM hole/trichannel settings, bank/misc address decode configuration, address hashing, harvest controls, and two address-decoder instances for chip-select, row, column, bank, and rank-module selection.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field's bit mask in the 32-bit register value.
- `// addressBlock:` comments identify generated hardware address blocks. This chunk transitions through `gc_utcl2_vmsharedpfdec`, `gc_utcl2_vmsharedvcdec`, and `gc_ea_gceadec`; it begins in a previous VM block whose address-block marker is outside the selected lines.

There are no callable APIs or C types here. Consumers normally use these definitions through AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`. Register offsets live in `gc_9_2_1_offset.h`; this file only describes field layout inside the register value.

Important register families in this chunk include:

- `VM_CONTEXT14_CNTL` and `VM_CONTEXT15_CNTL`, plus the tail of `VM_CONTEXT13_CNTL`: `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry policy, and fault interrupt/default policy bits for range, dummy-page, PDE0, valid, read, write, and execute faults.
- `VM_CONTEXTS_DISABLE`: one disable bit per context 0 through 15.
- `VM_INVALIDATE_ENG0..17_SEM`, `_REQ`, `_ACK`, `_ADDR_RANGE_LO32`, and `_ADDR_RANGE_HI32`: the field contract for TLB/page-table invalidation engines.
- `VM_CONTEXT0..15_PAGE_TABLE_BASE_ADDR_LO32/HI32`, `START_ADDR_LO32/HI32`, and `END_ADDR_LO32/HI32`: page-directory-entry and logical-page-number fields split into low 32-bit and small high-bit portions.
- `MC_VM_NB_*`, `MC_VM_FB_OFFSET`, `MC_VM_SYSTEM_APERTURE_*`, `MC_VM_STEERING`, `MC_SHARED_VIRT_RESET_REQ`, `MC_MEM_POWER_LS`, `MC_VM_APT_CNTL`, `MC_VM_LOCAL_HBM_*`, and `MC_VM_XGMI_LFB_*`: shared VM aperture and memory-location fields.
- `MC_VM_FB_LOCATION_BASE/TOP`, `MC_VM_AGP_TOP/BOT/BASE`, `MC_VM_SYSTEM_APERTURE_LOW/HIGH_ADDR`, and `MC_VM_MX_L1_TLB_CNTL`: visible VM aperture and TLB configuration fields.
- `GCEA_DRAM_*` and `GCEA_IO_*`: read/write client group maps, virtual-channel maps, lazy/CAM controls, burst controls, priority coefficients, urgency modes, quantum values, combine-flush policy, and per-CID urgency masks.
- `GCEA_ADDRNORM*`, `GCEA_ADDRDEC*`, and `GCEA_ADDRDECDRAM*`: address normalization, DRAM hole, bank/channel/chip-select/rank-module decode, XOR hash, harvest, chip-select base/mask/config, column selection, row/bank selection, and secondary chip-select selection fields.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution of symbolic shift and mask constants into register composition or decode expressions.

The implied runtime flow is:

1. A GC 9.2.1 path selects an `mm...` register offset from `gc_9_2_1_offset.h`.
2. The same path uses this header's `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to construct or inspect a 32-bit register value.
3. AMDGPU reads or writes the register through SOC15 MMIO helpers, or stores the field definition in a golden-register, debug, RAS, or initialization table.
4. The hardware VM, GCEA, memory-controller, invalidation-engine, address-decoder, or prioritization logic applies the resulting state.

The VM invalidation fields imply higher-level sequencing, but the sequence is not encoded here. Typical code composes a request with a per-VMID invalidate bit, selected flush type, L1/L2 invalidate selectors, and optional address-range registers; writes the request engine; then polls or waits for the matching ACK/semaphore state. This chunk only defines the bit positions needed by that flow.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists only in the GPU registers whose fields are described here.

Hardware state represented by this chunk includes VM context enablement, page-table depth/block sizing, fault interrupt/default policies, VMID/context disable state, invalidation-engine request and acknowledgment bits, page-table base/start/end address bounds, framebuffer and AGP aperture locations, default system aperture address, L1 TLB behavior, cacheability and HBM/XGMI placement, GCEA client grouping, traffic arbitration coefficients, urgency masks, address normalization windows, DRAM address hashing, harvest overrides, and address-decoder chip-select geometry.

Many programmed values persist until driver reinitialization, VM hub setup, GPU reset, suspend/resume restore, power-gating loss, firmware initialization, or explicit register reprogramming. Invalidation request and acknowledgment fields are transient hardware synchronization state. Fault-policy bits affect later VM fault behavior until changed. Address decode, aperture, and TLB settings are global enough that stale or mismatched state can affect all command queues that issue memory transactions through the corresponding hub.

This generated header does not distinguish read-only, write-only, sticky, clear-on-write, self-clearing, security-sensitive, or reset-default behavior. Consumers must rely on the hardware programming sequence and the companion offset/default headers.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.2.1 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h` supplies matching `mm...` register offsets and base indices for the field names in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h` includes `gc_9_2_1_offset.h` and `gc_9_2_1_sh_mask.h` for Vega12 power-management code.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c` includes this GC 9.2.1 shift/mask header and uses the VM invalidation, aperture, framebuffer, and TLB field macros for the GFX hub.
- Shared AMDGPU VM hub code patterns use these fields with `REG_SET_FIELD` and `REG_GET_FIELD` around `MC_VM_MX_L1_TLB_CNTL`, `VM_INVALIDATE_ENG0_REQ`, `VM_INVALIDATE_ENG0_ACK`, `VM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32`, `MC_VM_FB_LOCATION_BASE/TOP`, `MC_VM_AGP_*`, and `MC_VM_SYSTEM_APERTURE_*`.
- GFX9 family initialization and golden-setting paths program GCEA, GCMC, and VM registers during ASIC bring-up, reset, power-management, and hub setup.
- Display and memory-management code may read or depend on framebuffer/aperture registers such as `MC_VM_FB_LOCATION_BASE/TOP`, `MC_VM_FB_OFFSET`, and `MC_VM_SYSTEM_APERTURE_*` to derive visible VRAM and aperture layout.

Runtime integration points include VM hub setup, GPUVM page-table configuration, VMID invalidation and TLB flush, fault interrupt policy, KFD/compute and graphics queue memory access, framebuffer/AGP/system-aperture programming, XGMI/HBM local-memory placement, golden-register initialization, power-management restore, debug register dumps, and low-level GCEA traffic/address-decode tuning.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits, silently corrupting VM, aperture, invalidation, or address-decode state.
- The chunk starts mid-register at `VM_CONTEXT13_CNTL`; the earlier `SHIFT` definitions and address-block context for that register are in the previous chunk.
- The chunk ends mid-register at `GCEA_IO_WR_PRI_URGENCY_MASK`; CID14 through CID31 and the corresponding masks continue in the next chunk.
- Repeated families are easy to mis-index. `VM_INVALIDATE_ENG0..17`, `VM_CONTEXT0..15`, `GCEA_ADDRDEC0/1`, `CS01/CS23`, secondary chip-select fields, and `CID0..31` masks depend on consistent generated naming and bit spacing.
- VM invalidation programming is synchronization-sensitive. Wrong `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, L1/L2 invalidate selector, ACK, or semaphore masks can produce stale translations, memory corruption, GPU page faults, or hung queues.
- Page-table address fields are split across low and high registers. Incorrect masks for high-bit fields can truncate or overrun GPU virtual-address bounds.
- Fault-policy fields control interrupt/default behavior for range, dummy-page, PDE0, valid, read, write, and execute faults. Bad values can hide VM faults, flood interrupts, or allow an unsafe default response.
- Aperture and framebuffer fields affect visible VRAM, AGP, system aperture, cacheable memory ranges, HBM, and XGMI layout. Incorrect masks can misplace memory windows or break display, DMA, or page-table access.
- GCEA address-decode and hash fields are topology-sensitive. Incorrect bank, channel, chip-select, row, column, rank-module, harvest, or XOR hash programming can cause hard-to-debug memory faults or severe performance issues.
- Priority and urgency controls influence traffic fairness and latency. Bad coefficients or per-CID masks can create starvation, performance cliffs, or intermittent hangs under mixed graphics/compute/IO traffic.
- The same field names appear across multiple AMD GPU generations with similar but not guaranteed-identical layouts. Cross-ASIC copy/paste must stay tied to the GC 9.2.1 offset and mask pair.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include Vega12/GC 9.2.1 support. Missing, malformed, or renamed macros should surface in `gfxhub_v1_1.c`, Vega12 powerplay files that include `vega12_inc.h`, and shared GFX9 paths.
- Mechanically compare every `__SHIFT` and `_MASK` in this chunk against AMD's authoritative GC 9.2.1 register database.
- Cross-check each register family in this chunk against `gc_9_2_1_offset.h` so every field group has a matching `mm...` register offset.
- Verify repeated counts and spacing: VM contexts 0-15, invalidation engines 0-17, page-table base/start/end low/high pairs, GCEA DRAM/IO CID maps 0-31, address-decoder instances 0/1, and chip-select groups `CS01`, `CS23`, `SECCS01`, and `SECCS23`.
- Exercise GPUVM workloads that create, update, invalidate, and destroy page tables while checking for missing ACKs, stuck invalidation semaphores, page faults, stale translations, and queue hangs.
- Run graphics and compute workloads across reset and suspend/resume paths to confirm VM context, TLB, aperture, and GCEA state is restored correctly.
- Validate display and memory-aperture reporting on Vega12 hardware, especially framebuffer base/top, AGP, system aperture, and default aperture address handling.
- Use register dumps to decode known-good hardware state with these masks and compare decoded fields against reference tools.
- Stress mixed traffic and memory-topology cases if GCEA priority/address-decode programming is changed: graphics, compute, DMA, display scanout, XGMI/HBM, and page-fault injection are useful signals.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002652`. The final per-file research should merge this with neighboring chunks for full `gc_9_2_1_sh_mask.h` coverage. The previous chunk owns the beginning of `VM_CONTEXT13_CNTL`; the next chunk owns the remainder of `GCEA_IO_WR_PRI_URGENCY_MASK` and subsequent GC 9.2.1 field definitions.
