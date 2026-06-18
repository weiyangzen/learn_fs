# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h lines 2516-4988

## Purpose

This chunk is the middle register-offset span of the generated GC 9.2.1 ASIC header used by AMDGPU for Vega12-class GC hardware. It contains compile-time `#define` constants that bind symbolic `mm*` register names to SOC15 graphics-core offsets, plus paired `*_BASE_IDX` selectors used by the SOC15 access macros to choose the correct per-IP base address from `adev->reg_offset`.

The line range starts in the middle of the command processor block: line 2516 is the `mmCP_DFY_STAT_BASE_IDX` partner for the previous chunk's `mmCP_DFY_STAT`, then this chunk continues through command processor, SPI, HQD, DIDT, GCCAC, TCP, GDS, RAS, graphics context registers, and the first part of the user-config CP register block. The chunk ends at `mmCP_CE_IB1_OFFSET` and its base-index macro, just before the continuation of the `gc_gfxudec` CP command-buffer and EOP registers in the next chunk.

This is not executable code. Its purpose is to provide the hardware register address vocabulary that higher-level AMDGPU code uses for ring setup, compute queue programming, scratch-register tests, depth/color backend configuration, graphics pipeline state, GDS context state, RAS signatures, and CP packet/user-config interactions.

## Important APIs, Types, And Data

The chunk contains preprocessor constants only. There are no functions, structs, enums, or local storage objects. The important API surface is the macro contract:

- Each register offset macro has an `mm` prefix, for example `mmCP_RB0_BASE`, `mmCP_HQD_PQ_CONTROL`, `mmDB_RENDER_CONTROL`, `mmCB_COLOR0_BASE`, `mmPA_SC_SCREEN_SCISSOR_TL`, `mmGDS_VMID0_BASE`, and `mmSCRATCH_REG0`.
- Nearly every register has a paired `*_BASE_IDX` macro. In this chunk most early CP registers use base index `0`, while the large `gc_gfxdec0` and `gc_gfxudec` register ranges use base index `1`.
- AMDGPU SOC15 helpers combine both halves with `adev->reg_offset[ip##_HWIP][inst][reg##_BASE_IDX] + reg`, as defined by `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15` in `amdgpu/soc15_common.h`.
- Field names, masks, shifts, and reset defaults are not defined here; consumers pair this header with `gc_9_2_1_sh_mask.h` and related default headers.

The chunk has about 1,216 register offset macros and 1,217 base-index macros. The extra base-index macro is the leading `mmCP_DFY_STAT_BASE_IDX`, whose register offset macro sits immediately before this chunk boundary.

Major register families covered include:

- CP/CPF/CPC/CPG command processor registers for DFY debug access, ring buffers, write/read pointers, interrupts, VMID assignment, doorbell ranges, queue status, trap/status registers, firmware program counter starts, and CP statistics.
- SPI shader processor input and arbiter registers, including arbitration, debug, wave-control, interpolation, resource limits, LDS and shader format controls.
- CP HQD registers for compute hardware queue descriptors, including PQ/RB bases, doorbell control, dequeue/status fields, EOP/state save/restore addresses, IB controls, and queue activity state.
- DIDT/GCCAC/TCP registers for droop/throttling indexed access, clock/activity controls, TCP watchpoints, UTCL1 translation behavior, and TCP performance counter selection/filtering.
- GDS registers for per-VMID base/size mappings, ordered append/consume state, GWS/OA allocations, context-save/restore, counter state, and debug/status controls.
- RAS signature registers for error/signature capture across SX, DB, PA, TA, SPI, and other GC sub-blocks.
- `gc_gfxdec0` graphics pipeline state registers for DB, PA, VGT, CB, SPI, and SX render/dispatch state.
- `gc_gfxudec` user-config registers for CP EOP events, append/atomic pre-op state, scratch registers, coherent-memory operations, CP DMA, IB offsets, and initial CP/CE offsets.

Explicit address blocks in this chunk are:

- `gc_cppdec2` at base address `0xc600`, containing additional CP doorbell, RB, interrupt, and CPC debug/control offsets.
- `gc_spipdec` at `0xc700`, containing SPI arbitration/debug/resource controls.
- `gc_cpphqddec` at `0xc800`, containing CP HQD queue-descriptor offsets.
- `gc_didtdec` at `0xca00`, containing DIDT indirect index/data controls.
- `gc_gccacdec` at `0xca10`, containing GC/SE CAC controls and indexed access registers.
- `gc_tcpdec` at `0xca80`, containing TCP watchpoint, UTCL1, and perf counter registers.
- `gc_gdspdec` at `0xcc00`, containing GDS/GWS/OA state and context registers.
- `gc_rasdec` at `0xce00`, containing RAS signature control and signature data offsets.
- `gc_gfxdec0` at `0x28000`, containing graphics context state for DB/PA/VGT/SPI/CB/SX.
- `gc_gfxudec` at `0x30000`, containing user-config CP and scratch/coherency registers.

## Control Flow

There is no runtime control flow inside the header. All behavior is introduced by code that includes it and passes the macros into register accessors, packet builders, golden-register tables, or debug register lists.

The common runtime pattern is:

1. The driver includes the GC 9.2.1 offset header through an ASIC-specific include path. `pm/powerplay/hwmgr/vega12_inc.h` includes both `gc_9_2_1_offset.h` and `gc_9_2_1_sh_mask.h`.
2. Runtime code selects GC instance `0` and a base index through the macro pair. For example, `SOC15_REG_OFFSET(GC, 0, mmSCRATCH_REG0)` expands into a register address using `mmSCRATCH_REG0_BASE_IDX`.
3. The driver reads or writes the computed MMIO address through `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, or lower-level `RREG32`/`WREG32`.
4. In ring or IB paths, some of these offsets are embedded into PM4 packets after subtracting packet-space starts such as `PACKET3_SET_UCONFIG_REG_START`.

Representative call paths from nearby driver code show how the macros are used:

- `gfx_v9_0_ring_test_ring()` resolves `mmSCRATCH_REG0` and emits a `PACKET3_SET_UCONFIG_REG` write to prove the graphics ring can update a scratch register.
- `gfx_v9_0_setup_rb()` programs `mmCP_RB0_CNTL`, `mmCP_RB0_WPTR`, `mmCP_RB0_RPTR_ADDR`, `mmCP_RB0_BASE`, `mmCP_RB_DOORBELL_CONTROL`, and doorbell range registers to initialize the graphics ring buffer.
- Compute queue setup writes HQD registers such as `mmCP_HQD_PQ_BASE`, `mmCP_HQD_PQ_CONTROL`, `mmCP_HQD_PQ_RPTR_REPORT_ADDR`, `mmCP_HQD_PQ_WPTR_POLL_ADDR`, and `mmCP_HQD_PQ_DOORBELL_CONTROL`.
- `gfx_v9_0_constants_init()` reads `mmDB_DEBUG2` into `adev->gfx.config.db_debug2`; `soc15_get_register_value()` later returns this cached value for debug register reads.
- Golden settings and workarounds in `gfx_v9_0.c` use related DB/RMI macros through `SOC15_REG_GOLDEN_VALUE` tables to program known-good hardware defaults.

## State And Persistence Behavior

The macros themselves are stateless compile-time metadata. They do not allocate memory, cache values, persist state, or perform I/O.

The hardware registers named here are stateful and volatile. Important state domains represented by this chunk include:

- CP ring state: ring buffer base addresses, buffer sizes, write/read pointers, VMID, active flags, interrupt status, doorbell enablement, and polling addresses.
- Compute queue state: HQD base pointers, queue size/control, dequeue requests, EOP/state-save/restore addresses, IB base/control, doorbell controls, and queue status.
- Pipeline context state: depth buffer, color buffer, viewport/scissor, primitive assembly, tessellation, streamout, shader input, interpolation, and blend/export settings.
- Scratch state: `mmSCRATCH_REG0` through `mmSCRATCH_REG7`, scratch mask/address/data registers, and related CP packet offsets used for ring and IB self-tests.
- Coherency/DMA state: `mmCP_COHER_*`, `mmCP_DMA_*`, wait-semaphore, atomic pre-op, and append/fence registers used by CP packet execution.
- GDS state: per-VMID allocation windows, GWS/OA mappings, ordered append/consume counters, context save/restore controls, and GDS debug/status registers.
- RAS/signature state: signature control/mask registers and block-specific signature registers used to capture error or diagnostic signatures.

Most hardware state in these registers is reset by GPU reset, IP block reset, or power-management transitions. Some fields are reprogrammed on every device initialization or ring resume. Runtime consumers must treat register contents as device-owned volatile state; values are not durable across resets and may be affected by firmware, the RLC, CP microcode, SR-IOV virtualization, or power-gating transitions.

One visible software persistence point is `adev->gfx.config.db_debug2`: `gfx_v9_0_constants_init()` reads `mmDB_DEBUG2` and keeps a cached copy for later debug register reporting in `soc15_get_register_value()`. That cache relies on this offset resolving to the correct hardware register.

## Dependencies

This chunk depends on the generated register map for GC 9.2.1 matching the silicon and the rest of the generated header set. Its direct consumers depend on:

- `gc_9_2_1_offset.h` for register offsets and base-index constants.
- `gc_9_2_1_sh_mask.h` for field masks and shifts used with `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15_RLC`, and golden-register tables.
- AMDGPU SOC15 register helpers in `amdgpu/soc15_common.h`, especially `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and RLC/no-KIQ variants.
- Device-specific `adev->reg_offset` initialization for GC hardware instances and base indices.
- CP/RLC firmware behavior for registers that are shadowed, protected, or accessed through RLC paths.
- PM4 packet definitions for command stream writes that target UCONFIG or CONFIG register spaces.

The chunk is also tied to ASIC selection. `vega12_inc.h` includes this header for Vega12 power-management code, while generic GFX9 code includes compatible GC 9.x generated headers and uses the same symbolic names. Cross-generation substitution is unsafe because many symbolic names repeat across GC 9.0, 9.2.1, 9.4.x, and GC 10.x headers but may have different offsets, base indices, availability, or valid programming sequences.

## Integration Points

The main integration point is the AMDGPU generated ASIC register include tree:

- `drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h` provides the symbolic offsets.
- `drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h` provides matching field encodings.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h` collects GC, THM, MP, and NBIO generated headers for Vega12 PowerPlay code.

Runtime driver integration points include:

- Graphics ring setup and tests in `amdgpu/gfx_v9_0.c`, especially scratch register tests and `mmCP_RB*` ring-buffer programming.
- Compute queue and KIQ/HQD setup paths in `amdgpu/gfx_v9_0.c`, where CP HQD, MEC doorbell range, EOP, and PQ registers are written.
- Golden setting programming in GFX9 initialization, where DB/SPI/RMI/CP register offsets are placed in tables and written during device bring-up.
- SOC15 debug register reporting in `amdgpu/soc15.c`, where selected GC registers are read directly or via indexed SE/SH access.
- Power-management code that includes the Vega12 register set and may use GC offset/mask pairs for throttling, clock, and workload-control programming.
- PM4 packet emission paths that target `mmSCRATCH_REG*`, CP coherency, CP DMA, WAIT_REG_MEM, atomic, and append/fence registers through command streams.

## Risks

- Register-offset drift is high-impact. A wrong offset or base index can silently program a different hardware register, leading to hangs, lost interrupts, invalid doorbell ranges, memory corruption, or misleading diagnostics.
- The chunk boundary itself is not semantically aligned at the start: `mmCP_DFY_STAT_BASE_IDX` belongs to a register macro in the prior chunk. Merge/reconciliation must preserve continuity across chunk reports.
- Base-index misuse is a common failure mode. The SOC15 helpers add `adev->reg_offset[...][reg##_BASE_IDX]`; using a macro with the wrong generated base index or a stale `adev->reg_offset` table redirects all accesses in that block.
- CP/HQD/RB register writes are sequencing-sensitive. Programming ring base, size, read/write pointers, VMID, and doorbells out of order can break graphics or compute queue execution.
- Doorbell range registers are security- and virtualization-sensitive. Incorrect `mmCP_RB_DOORBELL_RANGE_*` or `mmCP_MEC_DOORBELL_RANGE_*` values can expose the wrong doorbells or fail to wake GC after power-gating.
- Many registers are not safe for arbitrary writes. DB/CB/PA/VGT/SPI context registers are normally programmed by command streams; direct MMIO writes can race with CP/RLC-managed state.
- RAS, GDS, and performance-counter registers may be per-context, per-VMID, or destructive-on-read/write depending on fields described in the mask header. Diagnostic code must avoid changing workload-visible state.
- Cross-generation macro reuse is risky because names are intentionally stable while offsets and supported fields can change between GC versions.

## Test Signals

Useful validation signals are mostly build-time and hardware/runtime oriented:

- Build coverage for Vega12/GC 9.2.1 include paths that compile `vega12_inc.h`, `gc_9_2_1_offset.h`, and `gc_9_2_1_sh_mask.h` together.
- Static consistency checks that every `mm*` register macro in this chunk has the expected `*_BASE_IDX` partner, with the known exception that this chunk begins with a base-index partner for a previous-line register.
- Static checks that register names used by `gfx_v9_0.c`, `soc15.c`, and PowerPlay code exist in both the offset header and the mask header when field manipulation is used.
- Ring self-test success on GC 9.2.1 hardware: `gfx_v9_0_ring_test_ring()` should be able to write `0xDEADBEEF` to `mmSCRATCH_REG0` through a PM4 packet and observe it through MMIO.
- Graphics ring initialization should complete without timeout or GPU fault after programming `mmCP_RB0_*`, write/read pointers, and doorbell controls.
- Compute/KIQ queue bring-up should succeed after HQD and MEC doorbell range programming, with no invalid-register or queue-dequeue failures.
- Golden register programming should not report bad register accesses and should preserve expected cached values such as `adev->gfx.config.db_debug2`.
- Runtime debug register reads through SOC15 debug paths should return plausible values for CP/DB/GDS/RAS registers and should not require SE/SH selection for unindexed global registers.
- GPU reset, suspend/resume, and SR-IOV VF scenarios should reprogram volatile CP/HQD/RB/GDS state cleanly, because this header provides the addresses used by those restoration paths.
