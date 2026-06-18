# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002645`: lines 1-2515, `Docs/researches/chunks/subset-b-002645_research.md`
- `subset-b-002646`: lines 2516-4988, `Docs/researches/chunks/subset-b-002646_research.md`
- `subset-b-002647`: lines 4989-7470, `Docs/researches/chunks/subset-b-002647_research.md`
- `subset-b-002648`: lines 7471-7503, `Docs/researches/chunks/subset-b-002648_research.md`

## Chunk Research

### subset-b-002645: lines 1-2515

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h lines 1-2515

## Scope And Purpose

This chunk is the beginning of the AMDGPU GC 9.2.1 register offset header. It is a generated-style C preprocessor map from symbolic register names to register offsets for the graphics/compute IP block used by Vega12/GC 9.2.1-era devices. The assigned range covers the license and include guard, three early SQ debug status offsets, then register-offset groups from `gc_grbmdec` through most of `gc_shdec`, ending just after the first two `gc_cppdec` command-processor DFY offsets.

The header contains no executable code. Its purpose is to make SOC15 register access call sites readable and ASIC-specific: driver code can pass names such as `mmGRBM_CNTL`, `mmGB_TILE_MODE0`, `mmVM_INVALIDATE_ENG0_REQ`, `mmSPI_SHADER_PGM_LO_PS`, or `mmCOMPUTE_DISPATCH_INITIATOR` to register accessor macros instead of hard-coded numeric offsets. Each register offset is paired with a `<name>_BASE_IDX` macro, and every base index in this chunk is `0`.

Within the assigned lines there are 1,209 non-`_BASE_IDX` register offset macros and their matching base-index macros. The chunk is intentionally not the complete file: the file has 7,503 lines, and line 2,515 stops in the newly opened `gc_cppdec` address block at `mmCP_DFY_STAT`, with the rest of that block and later blocks outside this work item.

## Address Blocks Covered

The chunk is organized by hardware address-block comments. The comments give a block name and base address, while the macros give the offset values used by SOC15 access helpers.

- `gc_grbmdec`, base `0x8000`: GRBM control, status, reset, trap, scratch, power, fence, UTCL2 invalidation range, and error/status registers.
- `gc_cpdec`, base `0x8200`: command processor status, busy/stalled counters, MEC/ME/PFP/CE instruction pointers, ring/read pointers, ROQ/STQ/MEQ queue status, and related command/index/data registers.
- `gc_padec`, base `0x8800`: primitive assembly, vertex geometry/tessellation, wave limits, cache invalidation, PA/SC binning and FIFO controls, shader-array config, and UTCL1 PA controls.
- `gc_sqdec`, base `0x8c00`: shader queue/SQC/LDS configuration, shader trap base/mask addresses, SQ timestamps/commands/indirect access, instruction encoding aliases at `0x037f`, thread-trace word aliases, resource descriptor words, and SQ lightweight counters.
- `gc_shsdec`, base `0x9000`: SPI front-end and shader processor controls, debug/scan registers, interpolation and GDS credits, lifetime counters/status, CU masks, wave active counters, and trap-screen registers.
- `gc_tpdec`, base `0x9400`: texture data/texture address control, status, scratch, and DSM controls.
- `gc_gdsdec`, base `0x9700`: global data share config, status, protection fault reporting, DSM controls, and WD/GDS CSB.
- `gc_rbdec`, base `0x9800`: depth/color backend debug, watermarks, subtile/DFSM controls, render-backend redundancy/disable, GB address/tile/macro-tile configuration, CB memory arbiter/DCC controls, and user RB disable/redundancy registers.
- `gc_ea_gceadec2`, base `0x9c00`, and `gc_rmi_rmidec`, base `0x9e00`: GCEA/RMI data-fabric, credit, probe, error, formatter, scoreboard, arbiter, spare, and UTCL1 controls.
- `gc_utcl2_atcl2dec`, base `0xa000`: ATC L2 cache controls, status, memory power, and clock-gating controls.
- `gc_utcl2_vml2pfdec`, base `0xa100`: VM L2 controls, protection-fault controls/status/address/default-address registers, identity apertures, group classes, parity, and clock-gating.
- `gc_utcl2_vml2vcdec`, base `0xa200`: VM context controls for contexts 0-15, invalidation sem/request/ack registers for engines 0-17, invalidation address ranges, and per-context page-table base/start/end address registers.
- `gc_utcl2_vmsharedpfdec`, base `0xa590`, and `gc_utcl2_vmsharedvcdec`, base `0xa600`: memory-controller VM aperture, framebuffer, AGP, cacheable DRAM, HBM, XGMI LFB, reset, steering, and L1 TLB controls.
- `gc_ea_gceadec`, base `0xa800`: DRAM and IO client/group/VC maps, priority and burst controls, address normalization/decoding, hash/harvest controls, SDP reserves, latency sampling, and perf counter controls.
- `gc_tcdec`, base `0xac00`: TCP/TCC/TCA cache invalidation, status, cache policy, credit/channel steering, DSM, writeback/invalidate L2, soft reset, and burst controls.
- `gc_shdec`, base `0xb000`: graphics shader and compute dispatch register offsets, including PS/VS/GS/ES/HS/LS program addresses/resources, per-stage user data arrays, common user data, compute dimensions, thread counts, dispatch packet/scratch/program addresses, VMID, resource limits, static thread management, restart/relaunch, trace enable, checksum, dispatch ID, and compute user data.
- `gc_cppdec`, base `0xc080`: only the first two non-base offsets, `mmCP_DFY_CNTL` and `mmCP_DFY_STAT`, are inside this chunk; subsequent CP DFY data/address registers are outside the assigned lines.

## Important APIs, Types, And Macros

The "API" of this file is the macro namespace. A normal register macro has the form `#define mmREGISTER_NAME 0xNNNN`; its companion has the form `#define mmREGISTER_NAME_BASE_IDX 0`. These names are consumed by AMDGPU helper macros such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and golden-setting helpers which combine an IP block, instance, base index, and register offset into a final MMIO address.

The matching `gc_9_2_1_sh_mask.h` header supplies field shifts and masks for many of the same symbolic register names. This offset header gives the register location; the shift/mask header gives bitfield extraction and update metadata. Consumers usually include both when they need to read or write fields with helpers such as `REG_GET_FIELD()`.

Representative high-impact macro families in this chunk include:

- `mmGRBM_*`: global graphics register bus manager controls and status.
- `mmCP_*`: command processor status, queue, and control registers.
- `mmPA_*`, `mmVGT_*`, `mmWD_*`, `mmIA_*`: graphics front-end and primitive assembly controls.
- `mmSQ_*`, `mmSQC_*`, `mmSPI_*`: shader queue, shader cache, SPI, trap, wave, and debug controls.
- `mmDB_*`, `mmCB_*`, `mmGB_*`, `mmCC_RB_*`: depth/color backend and tiling/address configuration.
- `mmVM_*`, `mmMC_VM_*`, `mmATC_L2_*`: VM, address translation, aperture, invalidate, and page-table controls.
- `mmTCP_*`, `mmTCC_*`, `mmTCA_*`: texture/cache pipe controls.
- `mmCOMPUTE_*`: compute dispatch setup, resource, thread, VMID, scratch, restart, trace, and user-data registers.

There are no C types, functions, structs, global variables, or inline helpers in the assigned range.

## Control Flow

This chunk has no direct runtime control flow. It participates in driver control flow through inclusion and macro expansion. When GC 9.2.1-specific code reads, writes, or patches a register, these macros become compile-time constants used by the lower-level MMIO access path.

Typical indirect flows are:

1. ASIC-specific include wrappers, such as `pm/powerplay/hwmgr/vega12_inc.h`, include `gc_9_2_1_offset.h` together with `gc_9_2_1_sh_mask.h`.
2. GC hub and graphics code include this offset header directly for GC 9.2.1 paths; for example `amdgpu/gfxhub_v1_1.c` reads `mmMC_VM_XGMI_LFB_CNTL` and `mmMC_VM_XGMI_LFB_SIZE` through `RREG32_SOC15(GC, 0, ...)`.
3. Initialization tables in `amdgpu/gfx_v9_0.c`, including `golden_settings_gc_9_2_1` and `golden_settings_gc_9_2_1_vg12`, use these symbolic names with `SOC15_REG_GOLDEN_VALUE()` so the golden-register programming path writes the correct GC offsets.
4. Runtime code that computes register spacing uses adjacent offsets. For instance, VM invalidation code patterns derive engine distance from `mmVM_INVALIDATE_ENG1_REQ - mmVM_INVALIDATE_ENG0_REQ`, making the sequential layout in this header part of an implicit contract.

## State And Persistence Behavior

The header itself has no mutable state and persists nothing. Its values describe hardware state addresses. Any persistence or state transition happens in consumers that use the macros to read or write GPU registers.

The persistent consequences are therefore indirect and hardware-facing:

- Golden-setting tables can program registers during GPU initialization or resume.
- VM and ATC registers can affect address translation, page-table base/start/end ranges, invalidation requests, fault reporting, and aperture configuration.
- GRBM/CP/SPI/SQ/TC/RB registers can affect scheduling, command submission, shader execution, cache behavior, tiling, and debug/trap behavior.
- Compute and shader user-data registers describe per-dispatch or per-stage state that the command processor and shader front end consume.

Because these are compile-time constants, a wrong offset silently redirects MMIO access to the wrong hardware register unless caught by build-time comparisons, hardware validation, or runtime failures.

## Dependencies And Integration Points

The include guard `_gc_9_2_1_OFFSET_HEADER` prevents duplicate macro definitions within a translation unit. The license header is AMD MIT-style and matches the surrounding generated register headers.

Primary local integration points observed in the tree are:

- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`, which aggregates GC 9.2.1 offsets and masks with THM, MP, and NBIO headers for Vega12 power-management code.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c`, which includes this header and its shift/mask companion for GC hub VM/XGMI register reads.
- `drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c`, whose GC 9.2.1 golden-setting arrays use many symbols from this chunk, including DB, GB, PA, SH, SPI, SQC, TA, TCP, TD, and CP registers.
- The SOC15 access framework (`SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and golden-register table helpers), which interprets the offset/base-index pair in the context of an IP block and instance.
- Sibling GC headers such as `gc_9_2_1_sh_mask.h` and versioned offset headers (`gc_9_0_offset.h`, `gc_9_1_offset.h`, `gc_10_1_0_offset.h`, etc.), which provide ASIC-version-specific variants of many same-named macros.

The generated macro names are global preprocessor symbols. Translation units must include only the compatible ASIC offset header set for a given compile context, or identical names from different GC versions would collide.

## Risks And Edge Cases

- Offset correctness is safety-critical. A stale or transposed value can make otherwise valid driver code read or write an unrelated register, causing GPU hangs, broken VM invalidation, bad tiling, shader faults, or subtle performance regressions.
- Same-named macros exist in multiple ASIC-version headers with different numeric values. Accidental mixed inclusion of incompatible generated headers can produce redefinition conflicts or, worse, compile code against the wrong hardware map if include ordering hides the issue.
- The chunk boundary opens `gc_cppdec` but does not include the full block. Research or generated reports must not infer complete CP DFY coverage from this chunk alone.
- Several symbolic names intentionally alias the same offset. SQ instruction-class macros share `0x037f`, thread-trace word variants share `0x03b0` or `0x03b1`, and these aliases should be treated as hardware view names, not duplicate-generation mistakes.
- Sequential register families are implicit contracts. VM invalidation engine registers, shader user-data arrays, tile/macro-tile arrays, and compute user-data arrays are often used with arithmetic or indexed programming patterns; missing or misordered values can break those patterns even if individual names compile.
- All `_BASE_IDX` values in this chunk are `0`. If future hardware or generated headers introduce nonzero base indexes, consumers assuming base index zero outside the SOC15 helper layer would be fragile.
- This source copy is under a `ceph-client` distributed-fs tree but contains DRM AMDGPU code. Research and downstream reports should preserve the actual source path rather than moving the file into a graphics-only or slug-only bucket.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Build AMDGPU translation units that include `vega12_inc.h`, `gfxhub_v1_1.c`, and `gfx_v9_0.c` to catch missing macro names, duplicate definitions, or incompatible offset/mask header pairing.
- Run a preprocessor or static check ensuring each `mm*` macro in the chunk has a matching `mm*_BASE_IDX` macro, except at intentional chunk boundaries in partial research slices.
- Compare this header against the authoritative AMD register database or known-good upstream generated `gc_9_2_1_offset.h` for exact offset/base-index values.
- Add focused static checks for sequential families used arithmetically, such as `mmVM_INVALIDATE_ENG*_REQ`, `*_ACK`, address-range pairs, `mmGB_TILE_MODE*`, `mmGB_MACROTILE_MODE*`, `mmSPI_SHADER_USER_DATA_*`, and `mmCOMPUTE_USER_DATA_*`.
- On supported GC 9.2.1/Vega12 hardware, boot and resume with golden settings enabled and verify there are no register-programming warnings, GPU hangs, VM fault storms, or shader/compute dispatch failures.
- Exercise VM invalidation and page-table update paths that rely on `mmVM_INVALIDATE_ENG0_REQ` spacing, then check for correct invalidation acknowledgements and absence of stale mappings.
- Exercise XGMI info discovery through `gfxhub_v1_1_get_xgmi_info()` on supported devices, validating reads of `mmMC_VM_XGMI_LFB_CNTL` and `mmMC_VM_XGMI_LFB_SIZE` against expected node IDs and segment sizes.
- Run shader and compute workloads that cover PS/VS/GS/HS/LS and compute-dispatch programming, since this chunk defines the stage program/user-data and compute dispatch register offsets used by those paths.

### subset-b-002646: lines 2516-4988

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

### subset-b-002647: lines 4989-7470

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h lines 4989-7470

## Purpose

This chunk is the third generated register-offset segment for the AMDGPU GC 9.2.1 graphics-core register map, used by Vega12-class include paths. It contains only C preprocessor constants that bind symbolic register names to hardware offsets; there are no executable functions, structs, or enums in this range.

The chunk starts in the middle of the `gc_gfxudec` direct MMIO address block, whose block comment appears earlier in the file. The first registers in this chunk continue command-processor state around copy-engine indirect buffers, ring-buffer offsets, command-buffer base/size registers, end-of-pipe event completion controls, coherent memory ranges, and draw/dispatch/index indirect addresses. It then covers broad GC direct-register regions for geometry, scan/raster, shader, cache, GDS, RLC, virtualization, power, performance counters, and memory-hub integration.

After the direct `mm*` register offsets, this chunk switches into indexed register spaces:

- `gccacind`: graphics CAC/PCC weights, accumulators, overrides, and throttle pattern registers.
- `secacind`: shader-engine CAC control and override selector/value registers.
- `sqind`: shader-queue wave debug, trap/status, PC, instruction, temporary register, execution-mask, and interrupt-word indexed offsets.
- `didtind`: the beginning of Dynamic Inductive Droop Throttling offsets for SQ, DB, TD, and the start of TCP.

## Important APIs, Types, And Data

The API surface is the macro naming contract consumed by AMDGPU register helpers and generated mask headers:

- `mm*_BASE_IDX` companions specify the SOC15 base-index selector used with `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and related helpers.
- `mmCP*`, `mmCPF*`, `mmCPC*`, and `mmCPG*` offsets identify command-processor, prefetch parser, compute-pipe, compute-queue, microcode, DMA, indirect-buffer, and performance counter registers.
- `mmRLC*`, `mmRLCV*`, and `mmRLC_GPU_IOV*` offsets identify run-list controller, safe mode, firmware, scheduler, SR-IOV, and virtualization registers.
- `mmSQ*`, `mmSPI*`, `mmSX*`, `mmTA*`, `mmTCP*`, `mmTD*`, `mmTCC*`, `mmTCA*`, `mmCB*`, `mmDB*`, `mmPA*`, `mmVGT*`, `mmWD*`, `mmGDS*`, and `mmGRBM*` offsets expose graphics pipeline and shader/cache/GDS register addresses.
- `mmATC*`, `mmMC_VM*`, `mmVM_*`, `mmUTCL2*`, and `mmGCEA*` offsets cover GC-side address translation, VM L2, XGMI/ATS, and graphics cache clock/power integration.
- `ixGC_CAC*`, `ixSE_CAC*`, `ixSQ_*`, and `ixDIDT_*` are indirect offsets, not direct MMIO addresses. They are selected through indexed access paths such as CAC/DIDT/SQ index registers or driver helper macros.

The corresponding field-level data lives in `gc_9_2_1_sh_mask.h`, which is included beside this offset header by `pm/powerplay/hwmgr/vega12_inc.h` and `amdgpu/gfxhub_v1_1.c`. This offset header deliberately does not encode bit masks, reset values, or access semantics.

## Control Flow

There is no runtime control flow in this file segment. Compile-time inclusion replaces symbolic names with literal offsets, and runtime behavior is supplied by callers.

Representative downstream flows are visible elsewhere in the AMDGPU tree:

- `gfx_v9_0_read_wave_data()` writes `mmSQ_IND_INDEX` and reads `mmSQ_IND_DATA` through `wave_read_ind()` to sample `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_EXEC_LO`, and other `sqind` offsets from this family of headers.
- `gfx_v9_0_kiq_setting()` reads and writes `mmRLC_CP_SCHEDULERS` while configuring the KIQ queue, showing how `mmRLC*` offsets in this chunk become normal SOC15 MMIO accesses.
- Shader-command paths write `mmSQ_CMD` while entering and leaving RLC safe mode.
- PowerTune/DIDT code programs `ixDIDT_*` and `ixSE_CAC_*` tables while holding the GRBM index mutex, entering RLC safe mode, selecting shader engines through `mmGRBM_GFX_INDEX`, and then restoring broadcast writes.
- `gfxhub_v1_1_get_xgmi_info()` includes `gc_9_2_1_offset.h` and reads GC-side memory/XGMI registers such as `mmMC_VM_XGMI_LFB_CNTL` and `mmMC_VM_XGMI_LFB_SIZE`.

## State And Persistence Behavior

The macros are stateless compile-time metadata. The underlying hardware registers are volatile GPU state:

- CP, CE, IB, ring, and queue registers represent live command-submission state and firmware-visible buffers.
- RLC and RLCV registers include safe-mode controls, scheduler state, microcode address/data windows, scratch registers, and virtualization/interrupt state.
- Performance-counter blocks expose selectable counters and result registers; software must configure selectors, enable sampling, read low/high halves consistently, and handle rollover.
- CAC, PCC, and DIDT indirect registers tune power/current estimation and throttling. Writes can change live throttling behavior, and reads reflect hardware accumulators or debug state rather than persistent driver-owned state.
- SQ wave debug offsets expose per-wave execution state selected through index registers. The selected SIMD/wave/thread context is external to these macros and is controlled by the caller.

No disk persistence or software cache is implemented here. State persists only according to GPU reset, power-gating, firmware reload, and explicit register programming behavior.

## Dependencies

This chunk depends on the generated GC 9.2.1 register layout remaining synchronized with the ASIC specification. Important consumers and companion files include:

- `gc_9_2_1_sh_mask.h` for field shifts and masks matching the offsets in this file.
- `pm/powerplay/hwmgr/vega12_inc.h`, which includes this offset header for Vega12 PowerPlay register programming.
- `amdgpu/gfxhub_v1_1.c`, which directly includes this header for GC-side VM/XGMI registers.
- SOC15 register-access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and RLC-safe variants.
- Indexed register helpers and tables for SQ wave debug, CAC, SE CAC, and DIDT access.
- Firmware and hardware contracts for CP/RLC microcode windows, ring/IB layout, safe-mode sequencing, virtualization, and performance counter programming.

## Integration Points

The direct `mm*` constants integrate with AMDGPU initialization, queue management, KFD/compute queue handling, graphics reset/recovery, power management, performance monitoring, and virtualization paths. The `BASE_IDX` companions are part of the SOC15 addressing scheme; using the wrong base index can address the wrong register aperture even if the symbolic register name is correct.

The indirect `ix*` constants integrate with register windows rather than raw MMIO:

- `ixSQ_*` values are used after programming SQ index state to inspect or flush selected waves.
- `ixDIDT_*` and `ixSE_CAC_*` values are used by PowerTune tables that program per-block throttling and CAC behavior.
- `ixGC_CAC_*` and `ixPCC_*` values expose graphics CAC weight/accumulator/override and pattern controls for power/current estimation.

The chunk also bridges several address blocks: `gc_perfddec`, `gc_perfsdec`, UTCL2/VM L2 performance blocks, `gc_rlcpdec`, `gc_pwrdec`, `gc_hypdec`, and partial `didtind`. This means one generated file supports both ordinary driver MMIO and specialized telemetry/power/virtualization control planes.

## Risks

- A wrong literal offset can silently read or write an unrelated GPU register, which is especially dangerous for CP/RLC firmware windows, safe-mode registers, GRBM selection, and DIDT/CAC throttling controls.
- Direct `mm*` offsets and indirect `ix*` offsets are not interchangeable. Passing an indirect offset to a direct SOC15 accessor, or the reverse, can corrupt state or return meaningless data.
- `mmGRBM_GFX_INDEX` changes register targeting across shader engines, instances, and broadcast modes. Callers must restore broadcast/default targeting and serialize access, typically with the GRBM index mutex.
- Register pairs such as low/high performance counters, base address low/high registers, and microcode address/data windows require ordered accesses; this header only names addresses and cannot enforce ordering.
- Generated GC 9.2.1 values should not be casually reused for adjacent generations. Many symbols are shared across GC 9.x, but offsets and address blocks can diverge across ASICs.
- Partial chunking matters for reconciliation: the DIDT TCP block continues after line 7470, so this document should not be treated as covering the entire DIDT register space.

## Test Signals

Useful validation is mostly build-time, static, and hardware-oriented:

- Build AMDGPU configurations that include `vega12_inc.h`, `gfxhub_v1_1.c`, and GC 9.x graphics code with this header and `gc_9_2_1_sh_mask.h`.
- Static consistency checks that every non-`BASE_IDX` offset used by driver code has a matching mask entry where fields are accessed with `REG_GET_FIELD` or `REG_SET_FIELD`.
- Runtime smoke tests on GC 9.2.1/Vega12 hardware for queue bring-up, KIQ setup, IB submission, shader wave debug dumps, VM/XGMI discovery, RLC safe-mode entry/exit, and GPU reset recovery.
- Power-management tests that enable and disable DIDT/CAC programming while verifying no invalid register-access errors and no failure to restore `mmGRBM_GFX_INDEX`.
- Performance-counter tests that program selector registers, read low/high counter pairs, and confirm sane monotonic or reset behavior around counter control writes.
- Virtualization/SR-IOV test coverage for `mmRLC_GPU_IOV*`, `mmVM_*_VF*`, and related hypervisor-facing registers where supported.

### subset-b-002648: lines 7471-7503

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h lines 7471-7503

## Purpose

This chunk closes the generated GC 9.2.1 register-offset header with the tail of the DIDT TCP register block, the shared DIDT stall telemetry counters, late `CTRL1`/EDC threshold offsets, and the final include-guard `#endif`.

The constants are indirect-register offsets (`ixDIDT_*`) for Dynamic Inductive Droop Throttling logic in AMD's graphics core. The TCP entries cover stall-pattern programming, throttle timing, weights, EDC control, EDC stall patterns, and EDC stall delays:

- `ixDIDT_TCP_STALL_PATTERN_5_6` through `ixDIDT_TCP_STALL_PATTERN_7` at `0x006a`-`0x006b`.
- `ixDIDT_TCP_MPD_SCALE_FACTOR` and `ixDIDT_TCP_THROTTLE_CNTL0/1/STATUS` at `0x006c`-`0x006f`.
- `ixDIDT_TCP_WEIGHT0_3`, `ixDIDT_TCP_WEIGHT4_7`, and `ixDIDT_TCP_WEIGHT8_11` at `0x0070`-`0x0072`.
- `ixDIDT_TCP_EDC_CTRL`, `ixDIDT_TCP_THROTTLE_CTRL`, EDC stall-pattern registers, and EDC stall-delay registers at `0x0073`-`0x007b`.
- shared stall-event counters for SQ, DB, TD, TCP, and DBR at `0x00a0`-`0x00a4`.
- `CTRL1` and EDC threshold offsets for SQ, DB, TD, and TCP at `0x00b0`-`0x00b7`.

## Important APIs, Types, And Data

The chunk contains only preprocessor constants. It defines no functions, structs, enums, storage, or callable APIs. Its API surface is the symbolic offset namespace consumed by AMDGPU and PowerPlay register helpers:

- `ixDIDT_TCP_*` names select TCP-domain DIDT indirect registers.
- `ixDIDT_{SQ,DB,TD,TCP,DBR}_STALL_EVENT_COUNTER` names 32-bit hardware counters for stall-event telemetry.
- `ixDIDT_{SQ,DB,TD,TCP}_CTRL1` names min/max power limit registers.
- `ixDIDT_{SQ,DB,TD,TCP}_EDC_THRESHOLD` names full-width EDC threshold registers.

The sibling `gc_9_2_1_sh_mask.h` file supplies the field contracts for these offsets. Important fields include two 15-bit stall-pattern fields in `DIDT_TCP_STALL_PATTERN_5_6`, one 15-bit field in `DIDT_TCP_STALL_PATTERN_7`, 4-bit MPD scale fields in `DIDT_TCP_MPD_SCALE_FACTOR`, enable/release-delay fields in `DIDT_TCP_THROTTLE_CNTL0/1`, an FSM-state field in `DIDT_TCP_THROTTLE_CNTL_STATUS`, byte-wide DIDT weights in the three weight registers, EDC enable/reset/force-stall/policy bits in `DIDT_TCP_EDC_CTRL`, `PCC_STALL_EN` in `DIDT_TCP_THROTTLE_CTRL`, and full-width masks for the stall counters and EDC thresholds.

## Control Flow

There is no executable control flow in this header fragment. At compile time, the C preprocessor binds symbolic register names to literal indirect offsets. Runtime flow is supplied by callers that pass these macros to DIDT indexed-register accessors or table-driven configuration code.

The closest local integration pattern is `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c`. That file uses arrays of `struct vega10_didt_config_reg` entries to program DIDT registers by offset, mask, shift, and value. In that path:

- `SEDiDtCtrl1Config_Vega10` writes `ixDIDT_TCP_CTRL1` with `MIN_POWER` and `MAX_POWER` fields.
- `SEDiDtWeightConfig_Vega10` writes `ixDIDT_TCP_WEIGHT0_3`, `ixDIDT_TCP_WEIGHT4_7`, and `ixDIDT_TCP_WEIGHT8_11`.
- `SEDiDtStallPatternConfig_Vega10`, `SEEDCStallPatternConfig_Vega10`, `SEEDCStallDelayConfig_Vega10`, and `SEEDCThresholdConfig_Vega10` program the TCP stall pattern, EDC stall pattern, EDC stall delay, and threshold offsets from this chunk.
- EDC enable/disable code reads and writes `ixDIDT_TCP_EDC_CTRL` through `cgs_read_ind_register(..., CGS_IND_REG__DIDT, ...)` and `cgs_write_ind_register(..., CGS_IND_REG__DIDT, ...)`.

## State And Persistence Behavior

The macros themselves are stateless compile-time metadata. The state they address is volatile GPU hardware state:

- TCP DIDT weights, throttle controls, stall patterns, EDC controls, EDC stall delays, and threshold registers hold power-management configuration until reset, reprogramming, or relevant power-gating sequences.
- Stall-event counters are hardware counters. The matching mask definitions describe each counter as a full 32-bit `DIDT_STALL_EVENT_COUNTER` field, so sampling code must handle wraparound.
- EDC threshold registers are full-width threshold values. `vega10_powertune.c` programs TCP, TD, and DB thresholds to `0xffffffff` in one table, indicating these can be used as high/disabled-like thresholds depending on the platform policy.
- `CTRL1` min/max power fields are split into two 16-bit fields and are used by PowerTune to bound DIDT power calculations.

No file-system persistence, firmware blob persistence, or software cache is implemented here. Any durable policy is represented elsewhere in driver tables or firmware/platform data, then written into these hardware registers at runtime.

## Dependencies

This chunk depends on generated ASIC register metadata staying synchronized with the GC 9.2.1 hardware specification. Consumers generally need:

- `gc_9_2_1_offset.h` for the offsets in this chunk.
- `gc_9_2_1_sh_mask.h` for shifts and masks used with `REG_SET_FIELD` and table-based masked writes.
- AMDGPU/CGS indirect register accessors for the DIDT space, such as `CGS_IND_REG__DIDT`, `cgs_read_ind_register`, and `cgs_write_ind_register`.
- PowerPlay/SMU policy code that decides whether TCP ramping or EDC ramping is enabled before programming or toggling these registers.

The offsets are generation-specific. GC 9.4.2 keeps the same TCP tail and late threshold/counter offsets, while GC 10.x moves comparable DIDT offsets to different numeric ranges. Older GC 9.0/9.1 headers also differ in where some EDC threshold offsets appear. Cross-generation code must include the correct ASIC header rather than reusing these literals.

## Integration Points

This header fragment integrates with the generated AMDGPU register include tree under `drivers/gpu/drm/amd/include/asic_reg/gc/`. The effective consumers are power-management and diagnostics paths, especially:

- Vega10/GC 9.x PowerTune DIDT configuration tables that write TCP weights, thresholds, stall patterns, and EDC delays.
- EDC enable/disable logic that toggles `DIDT_TCP_EDC_CTRL` based on `PHM_PlatformCaps_TCPRamping`.
- Potential debug or telemetry code that reads the SQ/DB/TD/TCP/DBR stall-event counters.
- Mask/default validation between `*_offset.h`, `*_sh_mask.h`, and any default/reset-value headers generated for the same ASIC family.

## Risks

- A wrong offset can silently program the wrong indirect DIDT register, causing unstable throttling behavior, incorrect power tuning, or misleading telemetry.
- Cross-generation reuse is unsafe because DIDT layout changes across GC families; even similar macro names can have different numeric offsets.
- Stall-event counters are destructive to interpret if another path clears them or resets DIDT while a telemetry reader is sampling.
- 32-bit counters can wrap under heavy activity, so delta calculations must be wraparound-aware.
- EDC control fields include reset, force-stall, and policy bits; incorrect masked writes can disable EDC, force unwanted stalls, or alter throttle policy.
- Since this is generated-style register metadata, hand edits risk diverging from AMD's hardware register source and can be difficult to catch without hardware access.

## Test Signals

Useful validation signals include:

- Compile coverage for GC 9.2.1 AMDGPU code that includes `gc_9_2_1_offset.h` with `gc_9_2_1_sh_mask.h`.
- Static checks that each macro in lines 7471-7500 has a corresponding mask/shift block in `gc_9_2_1_sh_mask.h`.
- Table validation in `vega10_powertune.c` showing masked writes use the expected offsets for TCP weights, stall patterns, EDC delay/pattern, and thresholds.
- Runtime smoke tests on matching GC 9.2.1 hardware that enable TCP ramping, program the DIDT tables, and confirm indirect DIDT reads/writes do not report invalid-register access.
- Telemetry tests that read stall counters before and after load, then verify counter deltas and clear/reset behavior are plausible.
