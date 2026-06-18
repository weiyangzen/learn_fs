# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h lines 1-4698

## Purpose

This chunk is the opening slice of the generated AMD GFX 8.0 register shift/mask header. It defines preprocessor constants for hardware register fields in the GCA/GFX8 block: every field has a `*_MASK` literal and a matching `*__SHIFT` literal that callers use to construct, update, or decode 32-bit MMIO register values.

The chunk covers three major hardware areas:

- Color buffer (`CB`) render target state and diagnostics, including blend state, color target base/pitch/slice/view, color target format and compression metadata, CMASK/FMASK/DCC addresses, target/shader masks, CB performance counters, clock gating, and CB debug bus fields.
- Command processor (`CP`, `CPC`, `CPF`, `CPG`, `CP_HQD`, `CP_MQD`) queue, interrupt, microcode, coherency, DMA, scratch, ring/IB, performance, and compute queue state.
- Depth buffer (`DB`) state through the start of `DB_DEBUG3`, including depth/stencil surface layout, render control/override, shader depth/stencil export control, HTILE/preload/stencil-ref state, DB performance counters, and debug/optimization-disable fields.

The chunk is not a complete header by itself. It starts with the include guard and ends mid-file at `DB_DEBUG3__ALLOW_RF2P_RW_COLLISION__SHIFT`; later chunks continue the rest of `gfx_8_0_sh_mask.h`.

## Important APIs, Types, And Data

This file defines no functions, structs, enums, or storage. Its API surface is macro data consumed by AMDGPU register helpers and by code that fills GPU queue descriptors.

Important macro families in this chunk:

- `CB_BLEND*_CONTROL` and `CB_COLOR_CONTROL` define source/destination blend factors, blend combine functions, separate-alpha behavior, ROP3 control, degamma, and color-control mode bits.
- `CB_COLOR[0-7]_{BASE,PITCH,SLICE,VIEW,INFO,ATTRIB}` define render target addresses and layout: 256-byte base fields, tile maxima, slice start/max, format, endian, number type, component swap, fast clear/compression/DCC/CMASK fields, tile mode, sample and fragment count fields.
- `CB_COLOR[0-7]_{DCC_CONTROL,CMASK,CMASK_SLICE,FMASK,FMASK_SLICE,CLEAR_WORD0,CLEAR_WORD1,DCC_BASE}` define auxiliary color compression and fast-clear state.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_HW_CONTROL*`, `CB_DCC_CONFIG`, `CB_PERFCOUNTER*`, `CB_CGTT_SCLK_CTRL`, and `CB_DEBUG_BUS_17` through `CB_DEBUG_BUS_22` expose target write masks, CB cache/overwrite-combiner tuning, performance counter selection/data, clock gating delays/overrides, and debug-bus busy/credit signals.
- `CP_RB*`, `CP_IB*`, `CP_CE_IB*`, `CP_ST_*`, `CP_ROQ*`, `CP_STQ*`, `CP_MEQ*`, and `CP_CEQ*` define command ring, indirect buffer, state buffer, read-order queue, state queue, micro-engine queue, and constant-engine queue base, size, pointer, threshold, and status fields.
- `CP_INT_*`, `CPC_INT_*`, `CP_ME[12]_PIPE*_INT_*`, `CP_*_INT_STAT_DEBUG`, and `CP_*_F32_*` define interrupt enable, status, and debug fields for graphics and compute command processor paths. These include doorbell, ECC, timeout, busy/context, privileged access, opcode, timestamp, reserved-bit, dequeue, query-status, and generic interrupt bits.
- `CP_RB_DOORBELL_*`, `CP_MEC_DOORBELL_*`, `CP_HQD_PQ_DOORBELL_CONTROL`, and queue pointer poll registers define how host writes and doorbells wake hardware queues.
- `CP_PFP_UCODE_*`, `CP_CE_UCODE_*`, `CP_MEC_ME[12]_UCODE_*`, `CP_ME_RAM_*`, and program-counter/intr-routine start fields define microcode and instruction-memory access/control metadata.
- `CP_COHER_*` and `COHER_DEST_BASE*` define CP surface-sync/coherency actions for CB, DB, TC/TCL1, shader instruction/cache, destination-base ranges, and coherency status.
- `CP_DMA_{ME,PFP}_*`, atomic-preop, GDS atomic, append, semaphore, wait-reg-mem, EOP done, stream-out, pipe stats, and primitive/invocation count registers define packet-side memory operations and counters.
- `CP_HQD_*` and `CP_MQD_*` define compute queue descriptor state: queue active/VMID/persistence/quantum, PQ/IB/EOP bases and pointers, queue control, IQ timer/dequeue/offload/semaphore/message fields, context-save metadata, GDS resource state, and HQD error state.
- `DB_*` macros in this chunk define depth/stencil base addresses, surface tiling, Z/stencil formats, render control, Z/stencil count control, render overrides, EQAA, shader export/depth ordering, bounds/clear values, HTILE, preload, stencil ref/mask state, DB performance counters, and debug bits.

The paired GFX8 offset header supplies the register addresses for these field definitions; for example `gfx_8_0_d.h` defines `mmCB_COLOR0_INFO` at `0xa31c`, `mmCP_COHER_CNTL` at `0xc07c`, `mmCP_HQD_PQ_CONTROL` at `0x3256`, and `mmDB_DEPTH_CONTROL` at `0xa200`.

## Control Flow

There is no executable control flow in this chunk. The C preprocessor exposes field masks and shifts at compile time. Runtime behavior is supplied by callers that:

- build register values with left shifts and masks, or with AMDGPU helpers such as `REG_SET_FIELD`;
- write those values to GFX8 MMIO registers named by sibling `gfx_8_0_d.h` offsets;
- decode status, interrupt, busy, performance counter, queue pointer, or debug fields from MMIO reads.

The practical flow for a field is usually: read or initialize a 32-bit value, clear the field mask, insert `value << FIELD__SHIFT`, and write the register. Queue-descriptor paths often assemble fields directly into an MQD memory image instead of immediately writing MMIO.

## State And Persistence Behavior

The macros are stateless compile-time constants. The state they describe lives in GPU registers, queue descriptors, or memory-mapped ring/queue metadata.

- CB and DB render state persists in GPU context/register state until overwritten, context-switched, reset, or invalidated by a command stream. Compression-related fields such as DCC, CMASK, FMASK, HTILE, fast clear, and render override bits affect how color/depth surfaces are interpreted and synchronized.
- CP ring and queue fields describe persistent runtime scheduling state: ring bases, read/write pointers, doorbell offsets/ranges, VMIDs, priority counts, queue sizes, IB bases/sizes, EOP rings, context-save areas, and MQD/HQD fields. KFD queue creation code writes many of these into MQD structures, so incorrect field definitions can persist for the lifetime of a compute queue.
- Interrupt enable/status fields configure and observe GPU interrupt state. Status and debug fields may be sticky or hardware-latched depending on the register contract, while enable fields persist until the driver reprograms them or hardware resets.
- Performance counter and debug fields are volatile hardware telemetry. Counter low/high pairs represent sampled hardware counts and can wrap; debug bus and busy/stalled fields reflect instantaneous or latched internal pipeline state.
- Coherency fields describe cache flush/invalidate/surface-sync operations and the address ranges those operations target. These are central to making CB/DB/TC/shader cache effects visible in the right order.

No filesystem persistence is implemented here. Durable policy comes from the driver, firmware, user queue setup, or command streams that use these constants.

## Dependencies

Direct dependencies are generated-register metadata and AMDGPU helper conventions:

- `gfx_8_0_d.h` provides the matching GFX8 register offsets for the field names in this chunk.
- `gfx_8_0_enum.h` and related ASIC headers provide symbolic field values where code does not use raw literals.
- Register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` rely on the exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` naming convention.
- KFD MQD and queue management code depends on CP/HQD/MQD field definitions matching the MQD layout for GFX8.
- Power-management and SMU support code includes this GFX8 mask header for register-level control of older Sea Islands/Volcanic Islands-era hardware paths.

The constants are ASIC-generation-specific. Similar names exist in GFX7, GFX8.1, GC9, and later GC headers, but masks and shifts can differ. Code must include the matching header for the target ASIC.

## Integration Points

Concrete consumers in this tree include:

- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c`, which includes `gca/gfx_8_0_sh_mask.h` and uses fields such as `CP_HQD_PQ_CONTROL__RPTR_BLOCK_SIZE__SHIFT`, `CP_HQD_PQ_CONTROL__PQ_ATC__SHIFT`, `CP_HQD_PQ_CONTROL__MTYPE__SHIFT`, `CP_HQD_PQ_CONTROL__NO_UPDATE_RPTR_MASK`, `CP_HQD_PQ_CONTROL__SLOT_BASED_WPTR__SHIFT`, `CP_HQD_PQ_CONTROL__PRIV_STATE__SHIFT`, and `CP_HQD_PQ_CONTROL__KMD_QUEUE__SHIFT` while constructing VI MQDs.
- `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_vi.c`, which includes this header for GFX8 queue management paths.
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/smu8_smumgr.c` and `drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h`, which include this header for SMU/PowerPlay register access on the relevant generation.
- Generic AMDGPU register programming patterns in GFX code that combine offset headers, `*_sh_mask.h` fields, and `REG_SET_FIELD`/masked writes for CP interrupts, ring control, doorbells, cache coherency, ME/MEC control, and render/depth state.
- Command stream and queue-descriptor ABI surfaces. The `CP_HQD_*`, `CP_MQD_*`, and `CP_RB*` fields are part of the software/hardware contract for compute queue setup and dispatch.

## Risks

- Mask/shift drift is high impact. A one-bit error can program the wrong render target format, compression mode, queue control bit, doorbell offset, interrupt enable, or coherency action.
- Cross-generation reuse is unsafe. Nearby GFX7/GFX8.1/GC9 headers contain similarly named fields with different masks, missing fields, or extra fields.
- Partial masked writes can preserve stale bits if callers do not clear the full mask before setting a field. This is especially risky for CB/DB compression flags, CP coherency actions, queue privilege/KMD bits, and interrupt enable/status registers.
- Address fields use implicit alignment units such as 256-byte bases or low-address masks starting at bit 2, 3, 5, or 12. Passing byte addresses without required shifting/alignment can point hardware at the wrong memory.
- Queue state fields influence scheduling, preemption, VMID ownership, doorbell behavior, and context save/restore. Incorrect `CP_HQD_*` or `CP_MQD_*` fields can hang queues, corrupt context state, or make user queues run with unintended privilege/cache policy.
- CB/DB compression and fast-clear fields must align with metadata allocations and cache/coherency programming. Mismatches can produce rendering corruption that only appears under MSAA, DCC/HTILE, fast clear, or resolve paths.
- Debug and performance counter fields are often hardware-diagnostic and may have side effects or generation-specific interpretation. Treating them as stable ABI without hardware documentation can mislead diagnostics.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for GFX8 AMDGPU/KFD/SMU paths that include `gca/gfx_8_0_sh_mask.h`.
- Static checks that each line-1-4698 register field has both a `*_MASK` and matching `*__SHIFT`, and that the paired register exists in `gfx_8_0_d.h` when it represents an MMIO register rather than an MQD memory field.
- KFD VI queue smoke tests that create, run, suspend, and destroy compute queues, then verify MQD fields such as `cp_hqd_pq_control`, doorbell offsets, VMID, PQ/IB/EOP bases, and read/write pointer reporting behave correctly.
- Graphics render tests covering color target formats, blend modes, MRT masks, MSAA/FMAsk/CMASK, DCC/fast clear, depth/stencil formats, HTILE, depth bounds, alpha-to-mask/EQAA, and DB render overrides.
- Interrupt tests that enable/disable CP and CPC/ME pipe interrupt bits and verify expected interrupt status/debug bits without spurious privileged-register, opcode, reserved-bit, or timeout interrupts.
- Coherency and synchronization tests that exercise CB/DB/TC/shader-cache invalidation and writeback paths after render, compute, DMA, stream-out, and EOP events.
- Performance/debug validation on real GFX8 hardware: counters should increment under targeted workloads, busy/stalled fields should correlate with induced stalls, and 64-bit low/high counter reads should handle wraparound.
