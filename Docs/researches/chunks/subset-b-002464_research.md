# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 37343-39656

## Scope

This chunk is a generated AMD GC 10.1.0 shift/mask header segment. It covers lines 37343 through 39656 and contains 2,192 `#define` entries: 1,093 `__SHIFT` macros and 1,101 `_MASK` macros. The count difference is expected for this sliced range because it starts with the tail masks of `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` and ends after only the first `GFX_PIPE_PRIORITY__HP_PIPE_SELECT__SHIFT` definition.

The content is declarative only. There are no C functions, structs, enums, variables, branches, loops, allocations, locks, or direct hardware accesses in this range. Its exported surface is a set of C preprocessor constants that describe bit positions and masks for Graphics Core hardware registers.

## Purpose

`gc_10_1_0_sh_mask.h` provides symbolic bitfield definitions for AMDGPU and AMDKFD code targeting the GC 10.1.0 register layout. Consumers pair these macros with register offsets from `gc_10_1_0_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to build or decode MMIO register values without embedding raw bit numbers.

This chunk covers three main areas:

- The end of the compute-unit clock/tree shader control register families for shader arrays `SA0` and `SA1`, WGP 12, CU 0/1, plus the tail of `SA1_WGP11_CU1_TCP_CTRL_REG`.
- A broad set of graphics clock-throttling and clock-control registers named `CGTT_*`, plus related block controls such as `SQ_ALU_CLK_CTRL`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `GL2*`, `GCEA`, `GRBM`, and `RLC_GFX_RM_CNTL`.
- The beginning of the `gc_hypdec` address block, including command processor microcode/RAM address/data fields, instruction-cache base/control/operation fields for PFP, ME, CE, CPC, and MES engines, MES data/local aperture fields, and memory instruction/data bounds.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro namespace emitted by the generated register database:

- `CGTS_SA{0,1}_WGP12_CU{0,1}_SIMD{0,1}_CTRL_REG`: per-SIMD control fields for `SIMD0` or `SIMD1`, associated scheduler/queue fields such as `SQ0` or `SQ1`, and local block fields such as `SQC` or `LDS`. Each field has value bits, an override enable bit, busy-override bits, light-sleep override bits, and SIMD-busy override bits.
- `CGTS_SA{0,1}_WGP12_CU{0,1}_TATD_CTRL_REG` and `CGTS_SA{0,1}_WGP12_CU{0,1}_TCP_CTRL_REG`: per-CU texture/address/data and texture-cache controls with the same value, override, busy, light-sleep, and SIMD-busy bitfield pattern.
- `CGTT_*_CLK_CTRL` and `*_CGTT_*_CTRL`: clock-control and clock-throttling fields for graphics front-end, shader, texture, cache, command processor, RLC, memory/cache, geometry, scan converter, DB/CB, GDS, PH, UTCL1, GRBM, and related GC blocks. Common fields include `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_OVERRIDE*`, `PERF_ENABLE`, `IDLE_THRESHOLD`, `IDLE_POLL_COUNT`, and block-specific power or clock-domain selectors.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL`: compact shader queue clock-control fields that expose `SOFT_OVERRIDE` and `CLK_READY` bits.
- `RLC_GFX_RM_CNTL`: a small RLC graphics resource-management control surface with `ATCL2_DISABLE`.
- `CP_*_UCODE_ADDR`, `CP_*_UCODE_DATA`, `CP_ME_RAM_*`, and `CP_MEC_ME{1,2}_UCODE_*`: command processor firmware and RAM address/data bit definitions.
- `CP_{PFP,ME,CE,CPC,MES}_IC_BASE_*` and `CP_{PFP,ME,CE,CPC,MES}_IC_OP_CNTL`: instruction-cache base address, VMID/cache policy/execute-disable controls, cache invalidation, cache priming, and completion/primed status fields.
- `CP_MES_*BASE*`, `CP_MES_LOCAL_*`, `CP_MES_*BOUND*`, and `CP_MES_LOCAL_APERTURE`: MES instruction/data base, local aperture, mask, and bounds fields for the micro-engine scheduler address windows.
- `GFX_PIPE_PRIORITY`: the chunk includes only `HP_PIPE_SELECT__SHIFT`; the rest of that register's masks and fields continue in the next chunk.

Most complete register groups follow the generated `<REGISTER>__<FIELD>__SHIFT` plus `<REGISTER>__<FIELD>_MASK` pattern. The only unmatched groups in this slice are the intentional boundaries: `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` has only tail masks here, and `GFX_PIPE_PRIORITY` has only its first shift.

## Register Areas Covered

The CGTS section is a per-compute-unit light-sleep and override map. It repeats a regular layout for shader arrays `SA0` and `SA1`, WGP 12, CU 0 and CU 1. The `SIMD0`/`SIMD1` register groups cover the SIMD lane itself plus related subblocks such as `SQ0`, `SQ1`, `SQC`, and `LDS`. The `TATD` and `TCP` groups cover texture address/data and texture cache interface blocks. The repeated `*_OVERRIDE`, `*_BUSY_OVERRIDE`, `*_LS_OVERRIDE`, and `*_SIMDBUSY_OVERRIDE` fields are used by GFX clock-gating/light-sleep control and diagnostics to force or inhibit hardware-controlled idle decisions.

The CGTT section maps clock-control registers for most major graphics blocks. `CGTT_SPI_PS_CLK_CTRL`, `CGTT_SPIS_CLK_CTRL`, `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, `CGTT_BCI_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, `CGTT_WD_CLK_CTRL`, `CGTT_GS_NGG_CLK_CTRL`, and the `CGTT_PA`/`SC`/`SQ`/`SX` groups cover front-end, rasterization, shader, and geometry domains. The `TD`, `TA`, `TCPI`, `TCI`, `TCPF`, `GDS`, `DB`, `CB`, `GL2C`, `GL2A`, `GL1C`, `GL1A`, `CHC`, `CHCG`, `CHA`, `GCR`, `UTCL1`, `GCEA`, `GRBM`, and `PH` groups extend the same pattern into texture, cache, command/data fabric, depth/color backend, address-translation, hub, graphics reset/broadcast, and physical clock domains.

The clock-control registers are mostly structured as delay and hysteresis controls plus soft overrides. Many have `PERF_ENABLE` or `CLOCK_DOMAIN_OVERRIDE` fields that interact with performance-controlled clock gating. Others expose extra idle-count, select, or busy/status bits. This makes the chunk relevant to golden-register programming, medium/fine/coarse-grain clock gating, light-sleep transitions, and GFX power-management debug.

The `gc_hypdec` section starts with command processor firmware access and instruction-cache setup. PFP, ME, CE, MEC ME1/ME2, CPC, and MES fields define microcode address/data windows, ME RAM read/write/data windows, instruction-cache base low/high address splits, base-control fields such as `VMID`, `ADDRESS_CLAMP`, `EXE_DISABLE`, and `CACHE_POLICY`, and operation controls for invalidating or priming instruction caches. The MES portion additionally defines data-code base registers, local base/mask pairs, local aperture selection, and instruction/data memory bounds.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior is introduced only when driver code includes the header and uses the macros in register read-modify-write sequences.

The field names imply several hardware state machines and state transitions:

- Compute-unit clock/light-sleep forcing: CGTS value and override fields can force subblocks such as SIMD, SQ, SQC, LDS, TA, TD, TCPF, and TCPI away from their normal hardware-derived idle or busy state.
- Graphics clock gating: CGTT delay, hysteresis, idle threshold, poll count, soft override, performance enable, and clock-domain override fields tune when clocks may be gated, held on, or overridden for specific graphics blocks.
- RLC and golden-register initialization: in-tree GC 10 code programs many CGTT registers through golden settings and toggles `RLC_CGTT_MGCG_OVERRIDE` around medium/fine-grain clock-gating enablement. These masks provide the field-level contract behind those raw register values and helpers.
- Command processor firmware bring-up: CP microcode, ME RAM, instruction-cache base, cache policy, execute-disable, invalidate, and prime fields participate in firmware loading and instruction-cache setup for PFP/ME/CE/CPC/MES engines.
- MES address-window setup: MES base, bound, aperture, and local mask fields describe how the micro-engine scheduler sees its instruction and data ranges.

No software persistence is implemented here. Hardware register contents persist according to ASIC reset and power domains. Fields named `*_COMPLETE`, `*_PRIMED`, `CLK_READY`, or similar are readback/status-oriented by name, while `*_OVERRIDE`, `*_ENABLE`, address, cache policy, timer, delay, and bounds fields are control-oriented by name. The header itself does not encode read-only, write-one-to-clear, reset-value, security, or sequencing rules.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is the GC 10.1.0 register database that generated this file and the companion `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` address map.

Direct in-tree include sites for this header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c`

Specific integration signals visible in this tree include `gfx_v10_0.c` golden-register arrays that program `CGTT_*` controls, GFX clock-gating enable/disable paths that manipulate `RLC_CGTT_MGCG_OVERRIDE`, CGTS light-sleep setup that iterates CU TCP control registers and uses `TCPI_LS_OVERRIDE`, and GFX firmware initialization code that programs `CP_PFP_IC_BASE_*`, `CP_ME_IC_BASE_*`, `CP_CE_IC_BASE_*`, and `CP_CPC_IC_BASE_*` registers. MES versions in later GFX blocks show the same `CP_MES_IC_BASE_*` and `CP_MES_MIBOUND_*` concepts, reinforcing this chunk's role in firmware scheduler memory setup even when exact generation-specific call sites differ.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently set an adjacent hardware bit during a read-modify-write update.
- The CGTS register families are highly repetitive across shader array, WGP, CU, and subblock coordinates. A generation or copy error for one coordinate can produce asymmetric CU behavior that appears only on certain harvested configurations, shader arrays, or workloads.
- Override fields are powerful and easy to misuse. Setting an override value without its corresponding override enable may have no effect, while leaving an override asserted can prevent normal clock-gating, light-sleep, or firmware-managed state transitions.
- CGTT fields affect power management, clock gating, and idle detection. Incorrect delay, hysteresis, idle threshold, or soft-override masks can cause hangs, performance loss, excess power draw, or unstable suspend/resume behavior.
- CP instruction-cache and microcode address fields participate in firmware bring-up. Incorrect base, VMID, cache policy, execute-disable, invalidate, or prime bits can prevent PFP/ME/CE/CPC/MES engines from fetching firmware correctly.
- Status and control fields are represented as identical macros. Consumer code must rely on the hardware spec and access helpers for read-only, write-one-to-clear, sticky status, polling, and reset semantics.
- Chunk boundaries split two logical registers. Merge-time validation should not treat the missing `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` shifts or missing `GFX_PIPE_PRIORITY` masks as defects in this chunk alone.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU and AMDKFD GC 10 paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
- Static generation checks that every complete register group in the full header has matching `__SHIFT` and `_MASK` definitions, with expected chunk-boundary exceptions for `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` and `GFX_PIPE_PRIORITY`.
- Cross-check this header against the matching `gc_10_1_0_offset.h` so every register-family prefix has the expected `mm...` or `reg...` address definition.
- Golden-register validation for GC 10 ASICs that touches `CGTT_CPF_CLK_CTRL`, `CGTT_SPI_CLK_CTRL`, `CGTT_SQ_CLK_CTRL`, `CGTT_SQG_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_WD_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, `GL2C_CGTT_SCLK_CTRL`, `UTCL1_CGTT_CLK_CTRL`, and related families visible in `gfx_v10_0.c`.
- Runtime GFX power-management tests: medium/fine/coarse-grain clock-gating enable/disable, CGTS light-sleep entry/exit, suspend/resume, reset recovery, workload idle transitions, and perf/power sanity checks.
- Runtime firmware tests: PFP, ME, CE, MEC/CPC, and MES firmware loading, instruction-cache invalidation/priming, queue submission, KFD compute queue bring-up, GPU reset recovery, and virtualization paths that depend on GC 10 command processor state.
- Register readback during bring-up should confirm expected CGTT golden values, override cleanup after power-management transitions, instruction-cache base/control programming, cache invalidate/prime completion bits, and MES memory aperture/bounds setup.

## Chunk Notes For Merge

This document intentionally covers only lines 37343-39656 of `gc_10_1_0_sh_mask.h`. Earlier chunks should cover the beginning of WGP 11 and the full start of the CGTS register families. Later chunks should continue `GFX_PIPE_PRIORITY` and the remaining `gc_hypdec`/GC register definitions. The final per-file report should describe the whole file as a generated ASIC register bitfield map for AMD GC 10.1.0, with this chunk contributing the compute-unit CGTS controls, graphics CGTT clock-control fields, and initial command-processor/MES instruction-cache and aperture definitions.
