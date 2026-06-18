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
