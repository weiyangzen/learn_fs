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
