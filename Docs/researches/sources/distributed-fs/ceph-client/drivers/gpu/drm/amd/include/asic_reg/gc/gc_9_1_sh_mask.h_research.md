# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002632`: lines 1-2407, `Docs/researches/chunks/subset-b-002632_research.md`
- `subset-b-002633`: lines 2408-4822, `Docs/researches/chunks/subset-b-002633_research.md`
- `subset-b-002634`: lines 4823-7193, `Docs/researches/chunks/subset-b-002634_research.md`
- `subset-b-002635`: lines 7194-9653, `Docs/researches/chunks/subset-b-002635_research.md`
- `subset-b-002636`: lines 9654-12153, `Docs/researches/chunks/subset-b-002636_research.md`
- `subset-b-002637`: lines 12154-14604, `Docs/researches/chunks/subset-b-002637_research.md`
- `subset-b-002638`: lines 14605-17204, `Docs/researches/chunks/subset-b-002638_research.md`
- `subset-b-002639`: lines 17205-19598, `Docs/researches/chunks/subset-b-002639_research.md`
- `subset-b-002640`: lines 19599-22320, `Docs/researches/chunks/subset-b-002640_research.md`
- `subset-b-002641`: lines 22321-24774, `Docs/researches/chunks/subset-b-002641_research.md`
- `subset-b-002642`: lines 24775-27132, `Docs/researches/chunks/subset-b-002642_research.md`
- `subset-b-002643`: lines 27133-29689, `Docs/researches/chunks/subset-b-002643_research.md`
- `subset-b-002644`: lines 29690-31176, `Docs/researches/chunks/subset-b-002644_research.md`

## Chunk Research

### subset-b-002632: lines 1-2407

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 1-2407

## Scope

This chunk covers the opening 2,407 lines of the generated AMD GC 9.1 shader/register mask header. It includes the license guard and the beginning of the GC 9.1 register-field catalog: `gc_grbmdec`, `gc_cpdec`, `gc_padec`, and the first part of `gc_sqdec`. The range contains 2,173 `#define` macros for 203 register names, almost entirely paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

The chunk starts at the beginning of the file and ends in the middle of `SQC_EDC_CNT2`, so merge-time reconciliation should combine it with later chunks for the complete GC 9.1 header view.

## Purpose

`gc_9_1_sh_mask.h` provides compile-time bitfield metadata for programming Graphics Core 9.1 registers in the AMDGPU driver. It does not define register addresses; instead it complements generated offset headers such as `gc_9_1_offset.h` by naming each field's shift and mask. Driver code can then use raw C bit operations or helper macros such as `REG_SET_FIELD()` and `REG_GET_FIELD()` to construct, update, and decode 32-bit MMIO register values without embedding magic bit positions.

The covered range focuses on front-end graphics control and diagnostics:

- `gc_grbmdec` describes GRBM global graphics register bus management fields: global/SE busy status, read/write/IOV errors, soft reset bits, trap registers, scratch registers, power request controls, and UTCL2 invalidation ranges.
- `gc_cpdec` describes command processor status and control: CPC/CPF busy and stall signals, MEC/ME reset/halt/step controls, command/ring/queue FIFO thresholds and pointer status, PRT LOD statistics controls, and command-index/data access.
- `gc_padec` describes primitive assembly, vertex generation, input assembler, work distributor, primitive/rasterizer binner, PA/SC enhancement, UTCL1 control/status, and shader-array or primitive-configuration masks.
- `gc_sqdec` begins shader core metadata: SQ/SQC configuration, LDS behavior, wave priority, register credits, FIFO sizes, DSM/error-injection controls, shader memory base/config registers, SQ UTCL1 controls, shader TBA/TMA address fields, and SQC EDC/FUE counters.

## Important API Surface

The public surface is the macro namespace, not C functions or structs. The naming contract is `REGISTER__FIELD__SHIFT` for the bit position and `REGISTER__FIELD_MASK` for the already-shifted mask. Consumers must pair these names with matching `mmREGISTER` offsets from the same ASIC generation.

- GRBM status and reset macros include `GRBM_STATUS`, `GRBM_STATUS2`, `GRBM_STATUS_SE0` through `GRBM_STATUS_SE3`, and `GRBM_SOFT_RESET`. These are used to determine which graphics blocks are busy and which blocks need reset, including CP, RLC, GFX, CPF, CPC, CPG, CAC, CPAXI, and EA.
- GRBM error, trap, and virtualization macros include `GRBM_READ_ERROR`, `GRBM_READ_ERROR2`, `GRBM_WRITE_ERROR`, `GRBM_IOV_ERROR`, `GRBM_INT_CNTL`, `GRBM_TRAP_*`, `GRBM_RSMU_READ_ERROR`, and `GRBM_RSMU_CFG`. These decode faulty read/write requesters, ME/pipe/VM/VF identity, interrupt enables, and debug trap data.
- GRBM targeting and scratch macros include `GRBM_GFX_CNTL`, `GRBM_IH_CREDIT`, `GRBM_UTCL2_INVAL_RANGE_START/END`, `GRBM_NOWHERE`, and `GRBM_SCRATCH_REG0` through `GRBM_SCRATCH_REG7`. These support queue targeting, interrupt-handler credit programming, invalidation range selection, and scratch-based register-access tests.
- CP status and diagnostic macros include `CP_CPC_STATUS`, `CP_CPC_BUSY_STAT`, `CP_CPC_STALLED_STAT1`, `CP_CPF_STATUS`, `CP_CPF_BUSY_STAT`, `CP_CPF_STALLED_STAT1`, `CP_STALLED_STAT1/2/3`, `CP_BUSY_STAT`, and `CP_STAT`. They expose fine-grained command processor stalls across MEC, CPF, CPC, PFP, ME, CE, queues, semaphores, TC/UTCL, stream-out, append, and surface-sync paths.
- CP control and queue macros include `CP_MEC_CNTL`, `CP_ME_CNTL`, `CP_*_HEADER_DUMP`, `CP_*_INSTR_PNTR`, `CP_GRBM_FREE_COUNT`, `CP_CPC_GRBM_FREE_COUNT`, `CP_CPF_GRBM_FREE_COUNT`, `CP_CNTX_STAT`, `CP_ME_PREEMPTION`, `CP_ROQ_*`, `CP_STQ_*`, `CP_MEQ_*`, `CP_CEQ*`, `CP_RB*_RPTR`, `CP_RB_WPTR_*`, `CP_CMD_INDEX`, and `CP_CMD_DATA`. These define micro-engine reset/halt/step bits, instruction/header dump fields, ring/queue thresholds, read/write pointers, and indirect command-register access.
- PA/VGT/IA/WD macros include `VGT_*`, `IA_CNTL_STATUS`, `WD_CNTL_STATUS`, `WD_QOS`, `WD_UTCL1_*`, `IA_UTCL1_*`, `GFX_PIPE_CONTROL`, `VGT_DMA_*`, `WD_BUF_RESOURCE_*`, and shader-array/primitive configuration registers. These describe primitive grouping, DMA FIFO sizing, cache invalidation, wave IDs, inactive CUs, UTCL1 fault/retry/PRT state, and draw/input-assembler work distribution.
- PA/SC binner and raster controls include `PA_CL_*`, `PA_SU_CNTL_STATUS`, `PA_SC_FIFO_*`, `PA_SC_FORCE_EOV_MAX_CNTS`, `PA_SC_BINNER_EVENT_CNTL_0` through `_3`, `PA_SC_BINNER_TIMEOUT_COUNTER`, `PA_SC_BINNER_PERF_CNTL_*`, `PA_SC_PKR_WAVE_TABLE_CNTL`, `PA_UTCL1_CNTL1/2`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_DSM_CNTL`, and `PA_SC_TILE_STEERING_CREST_OVERRIDE`.
- SQ/SQC macros include `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQ_REG_CREDITS`, `SQ_FIFO_SIZES`, `SQ_DSM_CNTL`, `SQ_DSM_CNTL2`, `SQ_RUNTIME_CONFIG`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `CC_GC_SHADER_RATE_CONFIG`, `GC_USER_SHADER_RATE_CONFIG`, `SQ_INTERRUPT_*`, `SQ_UTCL1_CNTL1/2`, `SQ_UTCL1_STATUS`, `SQ_SHADER_TBA/TMA_LO/HI`, `SQC_DSM_CNTL*`, `SQC_EDC_FUE_CNTL`, and the start of `SQC_EDC_CNT2`.

## Control Flow

There is no executable control flow in this header. Runtime behavior appears when AMDGPU code reads or writes a matching register and applies these constants. A typical pattern is:

1. Read a register with an MMIO helper such as `RREG32_SOC15(GC, instance, mmREGISTER)`, or start from zero when constructing a value.
2. Extract a field with `REG_GET_FIELD(value, REGISTER, FIELD)`, or test a condition with `value & REGISTER__FIELD_MASK`.
3. Insert a field with `REG_SET_FIELD(value, REGISTER, FIELD, new_value)`, which relies on the matching `__SHIFT` and `_MASK` constants.
4. Write the result to the matching `mmREGISTER` offset with a SOC15/MMIO write helper.

The GFX 9 driver follows this pattern around GRBM soft reset: `gfx_v9_0_soft_reset()` reads `mmGRBM_STATUS` and `mmGRBM_STATUS2`, tests fields such as `GRBM_STATUS__PA_BUSY_MASK`, `GRBM_STATUS__CP_BUSY_MASK`, and `GRBM_STATUS2.RLC_BUSY`, then sets `GRBM_SOFT_RESET` fields before issuing reset sequencing. Although this particular source file includes the GC 9.0 mask header, it demonstrates the integration contract shared by the GC 9.x generated mask families. GC 9.1-specific consumers must use the GC 9.1 offset/mask pair.

## State and Persistence

The macros are stateless preprocessor constants. The state they describe lives in GPU hardware registers and can persist until changed by driver initialization, ring setup, command submission, context switch restore, power/reset handling, or full device reset.

- GRBM status and error registers are mostly read/diagnostic state. Their fields reveal live block activity, request queues, read/write faults, requester identity, VF/VM attribution, and interrupt causes.
- GRBM reset, clock, power, trap, UTCL2, and scratch registers are mutable control state. Wrong writes can halt traffic, invalidate the wrong address range, hide errors, or disrupt debug/trap behavior.
- CP queue/ring threshold, pointer, halt, step, reset, and preemption registers control command processor progress and diagnostics. They are tightly coupled to graphics and compute ring setup.
- PA/VGT/IA/WD and PA/SC registers represent persistent graphics-pipeline configuration: primitive assembly, DMA/invalidation behavior, inactive hardware masks, rasterizer/binning behavior, UTCL1 translation controls, and fault status.
- SQ/SQC registers represent shader-core configuration and diagnostics: cache sizing/behavior, LDS reporting, wave priority, register-credit state, shader memory aperture layout, trap handler address fields, UTCL1 invalidation/status, error injection, and EDC/FUE counters.

Because these constants define the bit layout, persistence risk comes from consumers using the wrong mask generation for the running ASIC, mixing `gc_9_1_*` offsets with another generation's masks, or treating reserved/workaround fields as stable public configuration knobs.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.1 register specification. The shift/mask pairs must stay synchronized with `gc_9_1_offset.h` and any GC 9.1 default/value headers used by initialization and golden-register paths.
- Integrates with AMDGPU SOC15 register access helpers in `drivers/gpu/drm/amd/amdgpu`, especially code that uses `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, indirect SQ register helpers, ring initialization, reset handling, and debug/register-dump paths.
- Integrates with PSP and ASIC-specific initialization code when GC 9.1 offsets are included for firmware or security processor register programming.
- Provides a decode contract for debugging tools and logs: raw register dumps can be mapped back to busy, stall, fault, queue, and control fields using these masks.
- Shares macro names with neighboring GC 9.x headers. That consistency helps common driver code but also makes include-order and ASIC-selection correctness important.

## Risks

- Bitfield drift is the main correctness risk. A wrong shift or mask can silently program an unrelated field, especially in reset, halt, trap, virtualization, UTCL invalidation, or shader memory configuration registers.
- The file is generated-style and untyped. C compilation catches missing macro names but cannot catch using `REGISTER_A__FIELD_MASK` with `REGISTER_B`, or pairing a GC 9.1 field layout with a GC 9.0/9.2/9.4 register address.
- Busy/reset fields have high blast radius. Misinterpreting `GRBM_STATUS*` can cause unnecessary resets or missed resets; misprogramming `GRBM_SOFT_RESET`, `CP_ME_CNTL`, or `CP_MEC_CNTL` can leave engines halted, stepped, or reset.
- Queue/ring pointer and threshold fields are sensitive to off-by-one and width mistakes. Incorrect `CP_ROQ_*`, `CP_STQ_*`, `CP_MEQ_*`, `CP_RB*`, or `CP_CEQ*` usage can wedge command submission.
- Fault and virtualization fields must be decoded accurately. `GRBM_IOV_ERROR`, `GRBM_WRITE_ERROR`, `GRBM_RSMU_READ_ERROR`, and UTCL1 status fields carry VF/VM/requester information used for diagnosis and isolation.
- Enhancement, DSM, and error-injection fields are hardware-specific. Accidentally enabling `*_DSM_*`, `*_ENABLE_ERROR_INJECT`, or reserved PA/SC/SQ controls outside intended test paths can create hangs or hard-to-reproduce corruption.
- This chunk ends mid-register at `SQC_EDC_CNT2`; downstream documentation must not treat the partial tail as the complete SQC EDC counter surface.

## Test Signals

- Build signal: compile the AMDGPU driver with the generated GC 9.1 headers; missing/duplicate definitions or syntax drift will fail immediately.
- Generation consistency: compare this header against the authoritative GC 9.1 register source and `gc_9_1_offset.h` to verify every field mask matches its documented bit range and every field belongs to the expected register.
- Reset/idle smoke tests: boot a GC 9.1 ASIC or emulator, exercise graphics and compute rings, and confirm GRBM/CP idle polling, soft reset, and RLC stop/start paths do not time out.
- Register decode validation: capture `GRBM_STATUS`, `GRBM_STATUS2`, CP busy/stall registers, PA/VGT/IA/WD status, and SQ/SQC status under known workloads; verify decoded fields match expected active blocks.
- Graphics conformance: Vulkan/OpenGL CTS and stress workloads covering draw dispatch, primitive assembly, streamout, binning, cache invalidation, preemption, shader scratch/trap setup, and VM fault handling exercise many of these fields indirectly.
- Fault-path tests: controlled VM faults, VF/VM isolation tests, and RAS/EDC diagnostics should produce decodable `GRBM_*ERROR`, UTCL1 status, SQC EDC/FUE, and CP stall information without misattribution.

### subset-b-002633: lines 2408-4822

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 2408-4822

## Purpose

This chunk is generated AMD GC 9.1 register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, display, power-management, debug, RAS, and profiling paths to compose or decode MMIO register values for a GFX9/GC 9.1-class graphics block. The matching register addresses live in the companion GC 9.1 offset namespace, and many consumers in this tree also use the same field names through the broader GFX9 register include set.

The selected range covers the tail of SQC EDC counter definitions, a large SQ instruction and resource-descriptor encoding block, SQ indirect access and command fields, SQ lightweight/performance counters, SQ EDC and thread-trace token layouts, SQC instruction/data UTCL1 controls and status bits, then address blocks for `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and the start of `gc_rbdec`. Concretely, the block spans shader/SQ instruction formats, buffer/image/sampler resource descriptors, scratch and wave execution state, SPI wavefront lifetime/debug/trap controls, texture data/address unit controls, GDS status/protection/EDC controls, depth-buffer/debug/cache/DFSM controls, color/render-backend redundancy, and graphics backend address configuration.

Although this repository subtree is under `ceph-client`, this file is AMD GPU driver hardware metadata, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, memory allocations, or direct I/O operations in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Consumers normally combine these with `mm*` or `reg*` register offsets and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Major register groups in this chunk:

- `SQC_EDC_CNT2` tail and `SQC_EDC_CNT3`: instruction/data SQC bank A/B ECC/EDC counters for tag RAMs, bank RAMs, UTCL1 miss FIFOs, hit/miss FIFOs, dirty-bit RAM, and UTCL1 LFIFO SEC/DED counters. The chunk starts after the first `SQC_EDC_CNT2` shift fields, so the full register definition depends on the preceding chunk.
- `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, `SQ_TIME_HI`, and `SQ_TIME_LO`: timestamp/time fields used by SQ debug, command, and tracing flows.
- `SQ_IND_INDEX` and `SQ_IND_DATA`: indirect SQ register access selection and payload fields, including wave, SIMD, thread, auto-increment, forced read, timeout, unindexed mode, and index fields.
- `SQ_CMD`: shader-queue command fields including command, mode, VMID check, data, wave ID, SIMD ID, queue ID, and VM ID. Comparable GFX paths use this to issue soft recovery commands targeting a VMID.
- `SQ_DS_*`, `SQ_EXP_*`, `SQ_FLAT_*`, `SQ_GLBL_*`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SCRATCH_*`, `SQ_SMEM_*`, `SQ_SOP*`, `SQ_VINTRP`, `SQ_VOP*`, `SQ_VOP_DPP`, and `SQ_VOP_SDWA*`: generated field layouts for instruction encodings. These describe operand registers, offsets, opcodes, cache control flags, segment selectors, data formats, destination selectors, modifiers, encodings, and SDWA/DPP-specific controls.
- `SQ_LB_CTR_*` and `SQ_LB_DATA*`: SQ lightweight counter control, event selection, per-CU masks, and counter data readback fields.
- `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, `SQ_EDC_INFO`, `SQ_EDC_CNT`, and `SQ_EDC_FUE_CNTL`: SQ EDC status/counter fields for LDS, SGPR, VGPR, source/VMID/wave metadata, and fatal uncorrectable error interrupt/block controls.
- `SQ_THREAD_TRACE_WORD_*`: hardware thread-trace token layouts for common/event/instruction/PC/userdata/issue/misc/perf/register/timestamp/wave/wave-start records. These fields decode token type, time deltas, shader/CU/SIMD/wave identity, register access metadata, instruction issue slots, counters, PCs, userdata, and threadgroup IDs.
- `SQ_WREXEC_EXEC_*`, `SQ_BUF_RSRC_WORD*`, `SQ_IMG_RSRC_WORD*`, `SQ_IMG_SAMP_WORD*`, `SQ_FLAT_SCRATCH_WORD*`, and `SQ_M0_GPR_IDX_WORD`: buffer, image, sampler, scratch, WREXEC, and relative-index descriptor fields. These encode GPU virtual addresses, record counts, strides, data/number formats, swizzle and cache properties, metadata addresses, compression, sampler clamp/filter/LOD behavior, border color, and relative operand controls.
- `SQC_ICACHE_UTCL1_CNTL*`, `SQC_DCACHE_UTCL1_CNTL*`, `SQC_ICACHE_UTCL1_STATUS`, and `SQC_DCACHE_UTCL1_STATUS`: SQC instruction/data cache UTCL1 controls for GPUVM response behavior, permission/fault modes, client IDs, LFIFO behavior, VMID invalidation, force-miss/in-order modes, EDC disable, GPUVM invalidation mode, snooping, performance-event filtering, fragment forcing, and fault/retry/PRT status.
- `SX_DEBUG_1`: SX-to-DB credit and blend/pixel optimization debug controls.
- `SPI_*`: shader processor interpolation/control registers covering PS max wave IDs, start phases, graphics reset counts, DSM and EDC controls, pixel-shader CU enable masks, wavefront lifetime sampling/limits/status for slots 0-20, SPI lightweight counters and per-CU wave data, static CU masks, GDS credits, SX export/scoreboard buffer sizes, CSQ active wavefront counts, and per-process trap-screen memory base/mask/GPR minima.
- `TD_*` and `TA_*`: texture data/address block controls and status. These include texture data precision/rounding/power/stall compatibility controls, TD DSM/error-injection/scratch/status fields, TA credits, auxiliary determinism and sampler behavior controls, busy status bits, and scratch fields.
- `GDS_*`: global data share configuration, busy/status fields, enhanced mode bits, protection fault and VM protection fault metadata, EDC counters for GDS memory/input queues/GRBM/onion-access paths, DSM/error-injection controls, watchdog counter, and physical/pipe EDC counters.
- `DB_*`: depth buffer debug and resource-control fields. These cover depth/stencil compression/debug reads, HiZ/HiS behavior, fast Z/stencil and culling disables, cache-force/miss/stall options, viewport and resummarization controls, over-rasterization/context-suspend fixes, credit limits, watermarks, subtile MSAA layout fields, free cacheline depths, FIFO depths, exception panic-disable controls, ring-counter controls, RMI cache policies, DFSM configuration/watermarks/in-flight limits/watchdog/flush events.
- `CC_RB_REDUNDANCY` and `CC_RB_BACKEND_DISABLE`: render-backend failure/redundancy enable and backend disable masks.
- `GB_ADDR_CONFIG` and `GB_BACKEND_MAP`: graphics backend/tile addressing configuration and backend mapping fields. `GB_ADDR_CONFIG` exposes pipe count, pipe interleave, compressed fragments, bank interleave/count, shader-engine tile size, shader-engine count, GPU count, multi-GPU tile size, RBs per shader engine, row size, lower-pipe count, and shader-engine enable. The chunk ends with only the `GB_GPU_ID` section comment; the `GB_GPU_ID` fields are in the next chunk.

Fields named `RESERVED`, `UNUSED`, `Unused`, or full-width `DATA` are still part of the generated hardware contract. They should not be interpreted as permission for arbitrary whole-register writes; consumers need the programming guide, reset values, and existing read-modify-write patterns.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from driver code that includes the generated GC/GFX register headers:

1. A consumer selects a GFX/GC register address from an offset header or an `mm*`/`reg*` macro.
2. It composes a register value with `REG_SET_FIELD`, decodes a register value with `REG_GET_FIELD`, or supplies a mask/value pair to golden-register programming.
3. AMDGPU register helpers perform MMIO reads/writes or ring-packet emission while the owning initialization, reset, queue, VM, profiling, display, RAS, or interrupt path handles ordering.

Observed integration examples in this tree include `gfx_v9_0.c` golden-register tables for GC 9.1 programming `DB_DEBUG2`, `GB_GPU_ID`, `TA_CNTL_AUX`, `TD_CNTL`, `GB_ADDR_CONFIG`, and `GB_ADDR_CONFIG_READ`; `gfx_v9_0_gpu_early_init()` decoding `GB_ADDR_CONFIG` fields into `adev->gfx.config.gb_addr_config_fields`; older and newer GFX soft-recovery paths composing `SQ_CMD` with `CMD`, `MODE`, `CHECK_VMID`, and `VM_ID`; and display code reading `GB_ADDR_CONFIG` to derive tiling/modifier pipe properties. RAS-related GFX9 code also defines sub-block coverage for SQ/SQC/TD/GDS-like EDC domains represented by this macro family.

The chunk describes field positions only. It does not encode legal access order, read/write permissions, self-clearing behavior, golden-setting values, firmware ownership, GRBM broadcast/indexing requirements, power-gating constraints, or whether a status/counter bit is sticky, clear-on-read, clear-on-write, or live.

## State And Persistence Behavior

The file stores no software state and persists nothing. It defines names for hardware state inside a GC 9.1 graphics block.

The represented hardware state includes:

- Shader instruction and descriptor ABI state: instruction encodings, scalar/vector operands, memory op flags, image/buffer/sampler resource descriptors, scratch descriptors, and relative indexing state.
- SQ debug/recovery state: SQ indirect register access, targeted SQ commands by wave/SIMD/queue/VMID, timestamps, WREXEC execution address fields, and soft-recovery command inputs.
- Profiling and trace state: SQ/SPI lightweight counters, per-CU masks, counter data registers, thread-trace token payloads, timestamp words, issue-token fields, performance counter token fields, register-access trace fields, and wave-start metadata.
- Error-detection state: SQC/SQ/SPI/GDS EDC counters, SEC/DED summaries, fatal uncorrectable error controls, EDC source metadata, TD/GDS/SPI DSM and error-injection controls, and instruction/data UTCL1 fault/retry/PRT status.
- Translation/cache state: SQC I-cache/D-cache UTCL1 behavior for response/fault modes, VMID invalidation, snooping, force-miss, cache-size/FIFO reductions, GPUVM invalidation acknowledgement, and performance-event VMID/read-write filters.
- Shader processor state: SPI CU masks, PS wave limits, start phases, trap-screen base/mask ranges, GDS credits, export/scoreboard buffer sizing, CSQ activity counters, and lifetime warning/status slots.
- Texture state: TD/TA credit, determinism, filtering, rounding, stall, scratch, DSM, and busy-status controls.
- GDS state: configuration, busy/status bits, GDS/GWS/OA/VM protection fault metadata, EDC counters, DSM/error-injection knobs, and watchdog state.
- Depth/render backend state: DB debug knobs, cache and FIFO depths, watermarks, subtile layout for MSAA modes, DFSM controls, panic-disable bits, RMI cache policy for depth/stencil/HTILE and color metadata traffic, render-backend disable/redundancy, backend mapping, and backend address configuration.

Persistence is hardware-defined. Some fields are configuration programmed during ASIC init, golden-register setup, queue setup, profiling setup, or debug enablement and persist until reset, suspend/resume, power-gating, or reinitialization. Others are live counters, status bits, error latches, trace-token decoders, interrupt/debug readbacks, or write-trigger controls. The macros alone do not identify volatility or side effects, so driver code must preserve unrelated bits and follow ASIC-specific sequencing.

## Dependencies And Integration Points

The closest companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`, which provides register offsets for this ASIC family. In the current tree, `psp_v10_0.c` directly includes `gc/gc_9_1_offset.h`, while the main GFX9 driver code in `gfx_v9_0.c` uses GFX9 `mm*` names and common SOC15 helpers to program GC 9.1 hardware variants.

Important integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c`: GC 9.1 golden-register tables, GFX early init, `GB_ADDR_CONFIG` decoding, DB/TA/TD programming, and RAS registration/query/reset/error-injection plumbing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`: related-generation examples of `SQ_CMD` composition for ring soft recovery, showing how the SQ command bitfield convention is consumed.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c`: display modifier code reads `GB_ADDR_CONFIG` fields in newer GFX paths to derive tiling pipe/picker properties; GC 9.1 uses related `GB_ADDR_CONFIG` semantics for GFX9 tiling calculations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/*`: KFD interrupt and trap-handler code consumes SQ interrupt/resource descriptor conventions adjacent to these SQ/SPI definitions, especially for wave identity, trap/debug, and buffer resource metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c`: power-management paths manipulate GFX EDC/GRBM-indexed blocks, which makes SQC/SQ/SPI/TD/DB EDC and debug field correctness relevant to power and error handling.

The generated masks integrate with AMDGPU register-access abstraction, GRBM broadcast/indexing, golden settings, firmware/RLC-owned initialization, PM4/ring emission, KFD queue/trap handling, GPU reset/recovery, display tiling metadata, RAS counters, and profiling/thread-trace tooling. Address-block comments in this chunk identify the hardware decoder regions: pre-existing SQ/SQC blocks, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and `gc_rbdec`.

## Risks And Edge Cases

- Header/offset mismatches are the primary correctness risk. `gc_9_1_sh_mask.h` field layouts must be paired with the matching GC 9.1 offsets or compatible GFX9 register names; using another GC generation can compile while programming the wrong bits.
- The chunk boundary is artificial. It starts in the middle of `SQC_EDC_CNT2` and ends at the `GB_GPU_ID` section comment without the field definitions. Adjacent chunks are required for complete per-register coverage.
- These macros are untyped constants. A wrong register/field pairing can silently corrupt shader descriptors, SQ commands, SQC cache controls, trace decoding, GDS protection status, DB cache policy, or backend tiling configuration.
- SQ instruction and descriptor fields are compiler/ABI sensitive. Incorrect resource-word packing, image/sampler metadata, scratch size/offset, or memory-op flags can cause invalid shader execution, memory faults, data corruption, or hangs.
- `SQ_CMD` fields are recovery/debug sensitive. Targeting the wrong VMID, SIMD, queue, or wave can fail to recover the intended ring or disturb unrelated work.
- Thread-trace token layouts are decode-only metadata in many consumers. If masks drift, trace tools may produce plausible but wrong wave, PC, counter, or register-access data.
- SQC UTCL1 controls include invalidation, fault-response, snoop, VMID, and force-miss behavior. Bad values can create stale translations, excessive misses, missed fault reporting, or workloads that hang under GPUVM pressure.
- EDC, DSM, and error-injection fields must be treated carefully. Enabling injection, disabling EDC, clearing counters, or interpreting SEC/DED summaries without block-specific sequencing can hide real RAS events or create artificial faults.
- SPI wavefront lifetime, trap-screen, CU-mask, and CSQ active-count registers affect scheduling/debug visibility. Wrong masks can lose traps, misattribute wavefronts, or disable intended CUs.
- TA/TD determinism, filtering, rounding, and stall controls can change texture sampling behavior or performance. Carrying assumptions from adjacent GFX generations is risky because subtle field differences are common in generated ASIC headers.
- GDS protection fault fields carry security- and isolation-relevant metadata such as VMID, TMZ, OA/GWS, write/read direction, and address fragments. Incorrect decoding can misdiagnose process isolation failures.
- DB debug and DFSM controls are performance and correctness sensitive. Disabling fast Z/stencil paths, resummarization, coherency stalls, or cache policies can produce rendering artifacts or severe performance regressions.
- `GB_ADDR_CONFIG` drives tiling and memory-layout interpretation. Incorrect pipe/bank/RB/SE/row-size decoding can break display modifiers, DCC, render backend mapping, scanout compatibility, or memory swizzle calculations.
- Reserved and unused fields should be preserved unless a hardware programming sequence explicitly supplies reset/golden values.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware smoke/stress coverage:

- Build AMDGPU/KFD/display paths that use GFX9/GC 9.1 register headers, especially `gfx_v9_0.c`, PSP GC 9.1 offset users, KFD interrupt/trap code, and display tiling/modifier paths.
- Generated-header consistency checks that every field in this line range has the expected shift/mask pair, repeated lifetime-status and counter layouts are regular, and the fields have matching register offsets in the relevant GC/GFX9 offset headers.
- Golden-register programming tests on GC 9.1/Raven-class hardware confirming `DB_DEBUG2`, `GB_GPU_ID`, `TA_CNTL_AUX`, `TD_CNTL`, `GB_ADDR_CONFIG`, and `GB_ADDR_CONFIG_READ` are programmed with expected mask/value pairs and survive resume/reset as intended.
- GFX early-init tests that decode `GB_ADDR_CONFIG` into pipe, bank, compressed-fragment, RB-per-SE, shader-engine, and pipe-interleave fields and compare against known ASIC/VBIOS topology.
- Ring recovery tests that trigger soft recovery and confirm `SQ_CMD` VMID-targeted commands do not disturb unrelated queues.
- Shader and compute smoke tests exercising buffer/image/sampler descriptors, scratch access, flat/global/scratch memory instructions, scalar/vector instruction encodings, wave32/64 behavior where applicable, and trap/debug modes.
- Thread-trace/profiling tests that enable SQ/SPI lightweight counters and thread trace, run known workloads, and verify token decode fields, timestamps, wave IDs, CU/SIMD IDs, PCs, register events, and counter payloads are plausible.
- SQC cache/VM tests that issue VMID invalidations, force fault/retry/PRT scenarios, and verify instruction/data UTCL1 status and invalidation behavior under GPUVM stress.
- RAS tests for SQ/SQC/SPI/TD/GDS/DB-related EDC counters, including SEC/DED count changes, source metadata, query/reset paths, and error-injection guardrails where supported.
- Texture and sampler conformance tests for TA/TD controls, especially filtering, LOD, anisotropy, determinism, rounding, and busy/stall behavior.
- GDS protection tests that exercise GDS/GWS/OA accesses under multiple VMIDs, validate protection fault metadata, and confirm TMZ/VM isolation behavior.
- Depth/render tests covering fast Z/stencil, HTILE, DCC/metadata traffic, MSAA subtile layouts, DB cache policies, DFSM flushing, and backend disable/redundancy handling.
- Regression indicators include valid workloads producing SQ/SQC/UTCL1 faults, missing expected GPUVM faults, corrupted trace decode, stuck counters, incorrect display modifiers or tiling, rendering artifacts in depth/stencil workloads, GDS protection faults with wrong VMID/address data, RAS counter drift, and ring timeouts during recovery.

### subset-b-002634: lines 4823-7193

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 4823-7193

## Scope

This chunk covers a generated AMD GC 9.1 shader/register mask header range. It starts at the `GB_GPU_ID` field macros without the preceding register comment and ends in the middle of `VM_CONTEXT9_CNTL`, so merge-time reconciliation should join it with adjacent chunks for the complete file-level view. The range contains 2,186 `#define` macros, almost entirely paired `...__SHIFT` and `..._MASK` constants for 32-bit hardware register bitfields.

## Purpose

The header provides compile-time bitfield metadata for programming GC 9.1 registers in the AMDGPU driver. Consumers use these macros with the companion address/default headers to construct, decode, compare, or patch hardware register values without hard-coding bit positions. The covered registers describe graphics backend topology, tiling modes, color-buffer hardware controls, EA/RMI data path behavior, debug register ports, ATC L2 translation cache controls, VM L2 page table/fault state, and VM context controls.

This chunk does not implement executable logic or define C types. Its behavioral importance comes from being included by AMDGPU generation-specific code and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD`, where the mask and shift names become the ABI between driver source and GC 9.1 hardware register layout.

## Important API Surface

- `GB_GPU_ID`, `CC_RB_DAISY_CHAIN`, and `GB_ADDR_CONFIG_READ` expose GPU/backend identity and address configuration fields: pipe count, pipe interleave, compressed fragment count, bank interleave/count, shader engine count, multi-GPU tile size, render backends per shader engine, row size, lower-pipe count, and SE enable.
- `GB_TILE_MODE0` through `GB_TILE_MODE31` define repeated tiling descriptors with `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, `MICRO_TILE_MODE_NEW`, and `SAMPLE_SPLIT`. `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15` define macro tile bank width, bank height, aspect, and bank count.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, and `CB_DCC_CONFIG` cover color-buffer cache eviction, cache/tag sizing, FIFO depths, blend and fast-clear workaround bits, memory arbitration weights, and DCC overwrite-combiner behavior.
- `GC_USER_RB_REDUNDANCY` and `GC_USER_RB_BACKEND_DISABLE` expose user-visible render-backend redundancy and disable masks.
- The `gc_ea_gceadec2` block defines `GCEA_EDC_CNT`, `GCEA_EDC_CNT2`, DSM controls, TCC/XBR credit and burst controls, probe controls, error status, misc, SDP backdoor command/data/misc credits, and `GCEA_SDP_ENABLE`. These fields support error counting, data path arbitration/credit tuning, diagnostics, and service/data path enablement.
- The `gc_rmi_rmidec` block defines RMI control/status fields: general RMI mode and arbitration controls, subblock status registers, xbar configuration, UTC/XNACK and UTCL1 controls, TCIW formatter controls, scoreboard controls/status, xbar arbiter weights, clock control, UTCL1 fault/retry/PRT status, and spare control words.
- The `gc_dbgu_gfx_dbgudec` block defines debug port A/B/C/D address selectors and low/high data registers, allowing register-level debug access through port address/data pairs.
- The `gc_utcl2_atcl2dec` block defines ATC L2 translation cache controls, cache-data readout fields, busy/parity status, clock-gating, memory light-sleep, and CGTT clock control.
- The `gc_utcl2_vml2pfdec` block defines VM L2 controls, cache invalidation fields, cache sizing/update modes, busy/parity status, dummy-page fault address/control registers, protection fault control/status/address/default-address registers, context1 identity aperture registers, physical offset registers, group/real-time class fields, reserved CID bank selection, cache parity controls, and clock control.
- The `gc_utcl2_vml2vcdec` block defines `VM_CONTEXT0_CNTL` through the first half of `VM_CONTEXT9_CNTL`, with repeated fields for enabling a VM context, page table depth and block size, retry policy, and per-fault-class interrupt/default behavior.

## Control Flow

There is no direct control flow in this range. Runtime behavior is indirect:

1. AMDGPU code reads or initializes a 32-bit register value using SOC15/MMIO helpers or command-stream state setup.
2. It clears and inserts fields using generated names, usually through macros that combine `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
3. It writes the resulting value to the matching register offset from `gc_9_1_d.h` or a closely related generated address header.
4. Hardware consumes the programmed fields as persistent graphics, memory, translation, or fault-handling state until later state emission, reset, or context restore changes them.

Indexed register groups introduce implicit control flow in consumers. Tiling mode setup can iterate over `GB_TILE_MODE0..31` and `GB_MACROTILE_MODE0..15`; VM setup computes context register offsets from `VM_CONTEXT0_CNTL` to later contexts; RMI scoreboard and status fields are used by fault/invalidation paths that poll or inspect progress bits.

## State and Persistence

The macros are stateless build-time constants, but the registers they describe hold durable GPU state:

- `GB_ADDR_CONFIG_READ`, tile modes, and macrotile modes encode memory layout and backend topology used by surface addressing, render target setup, and compatibility decisions. Incorrect field extraction can produce wrong tiling, wrong pipe/bank interpretation, or surface corruption.
- `CB_HW_*` and `CB_DCC_CONFIG` tune color-buffer caches, DCC behavior, blend/resolve optimizations, fast-clear behavior, and memory arbitration. These values persist as graphics backend state and often appear in golden-register programming.
- `GCEA_*`, `RMI_*`, and `ATC_L2_*` state affects fabric credits, crossbar arbitration, request formatting, cache behavior, clock gating, parity reporting, and debug visibility. Misprogramming can manifest as hangs, bandwidth loss, dropped status, or noisy/hidden fault signals.
- `VM_L2_*` and `VM_CONTEXTn_CNTL` state controls GPU virtual-memory translation, TLB/cache invalidation, dummy-page handling, protection fault classification, interrupt/default responses, and per-context enablement. These registers persist across workloads until VM hub setup, context management, or reset changes them.
- Protection fault address/status registers are diagnostic state. Clear/update fields such as `CLEAR_PROTECTION_FAULT_STATUS_ADDR` and `ALLOW_SUBSEQUENT_PROTECTION_FAULT_STATUS_ADDR_UPDATES` affect whether later faults overwrite captured fault information.

## Dependencies and Integration Points

- Depends on AMD-generated GC 9.1 register specifications. The names and bit positions must stay synchronized with companion generated headers such as `gc_9_1_d.h`, default-value headers, and any ASIC-specific aliases used by SOC15 register helpers.
- Integrated through AMDGPU register programming under `drivers/gpu/drm/amd/amdgpu`. Repository usage shows GC 9.x paths reading/programming `GB_ADDR_CONFIG_READ`, using `GB_TILE_MODE0__*` field shifts in tiling helpers, setting `VM_CONTEXT0_CNTL` fields in gfxhub/mmhub setup, and decoding `GCEA_EDC_CNT`/`GCEA_EDC_CNT2` error counters via `SOC15_REG_FIELD`.
- Golden-register and IMU/RLC initialization tables use these register names and masks to enforce ASIC-specific defaults for backend, RMI, and VM behavior.
- Debug and telemetry paths use status and counter masks for EDC accounting, VM fault capture, UTCL1 fault/retry/PRT detection, parity status, and register dumps.
- User-visible graphics and compute APIs reach these fields indirectly through memory allocation layout, render-target/DCC setup, GPUVM/KFD VMID setup, page fault handling, reset recovery, and performance/power controls.

## Risks

- Bitfield drift is the main risk. If this generated header does not match the hardware spec or the companion address header, `REG_SET_FIELD`/`REG_GET_FIELD` will silently target the wrong bits.
- This chunk is not self-contained: it begins after the `GB_GPU_ID` register comment and ends before the final `VM_CONTEXT9_CNTL` masks. Automated documentation or validation should merge with adjacent chunks before making file-level claims.
- Repeated register families create copy/paste and index hazards. Using `GB_TILE_MODEn` or `GB_MACROTILE_MODEn` fields with the wrong slot can corrupt surface layout; using the wrong `VM_CONTEXTn_CNTL` slot can enable or alter the wrong VMID/context.
- Fault-control fields are high impact. Defaults for range, PDE0, dummy-page, valid, read, write, and execute faults decide whether faults interrupt, retry, use default handling, or continue; wrong settings can hide memory bugs or cause excessive GPU faults.
- Cache, arbitration, and credit fields in `CB_HW_*`, `GCEA_*`, `RMI_*`, `ATC_L2_*`, and `VM_L2_*` are performance- and hang-sensitive. Many are hardware tuning or workaround bits, so changing masks without matching firmware/hardware guidance can cause subtle regressions.
- Address split fields for dummy pages, protection fault addresses, default fault addresses, identity apertures, and physical offsets require correct low/high composition and alignment. Mask mistakes can redirect fault handling or identity mappings.

## Test Signals

- Build coverage: compile AMDGPU with this header included; duplicate macros, syntax mistakes, or missing field names fail quickly.
- Generation consistency: compare this range against the GC 9.1 register source used to generate `gc_9_1_sh_mask.h`, and verify one-to-one pairing with matching offsets in `gc_9_1_d.h`.
- Register programming smoke tests: boot a GC 9.1 ASIC, load AMDGPU, initialize gfxhub/mmhub/graphics, and watch for VM setup errors, golden-register warnings, GPU hangs, or reset loops.
- GPUVM and fault tests: exercise userptr/BO mapping, VM context enablement, invalid mappings, read/write/execute protection faults, dummy-page behavior, retry paths, and fault address capture.
- Graphics layout tests: run rendering workloads that cover tiled surfaces, DCC, fast clears, resolves, MRT/blend paths, and display/3D transitions; corruption often indicates wrong `GB_*` or `CB_*` field use.
- Diagnostics validation: compare register dumps and EDC/VM fault counters decoded with these masks against expected hardware state, especially `GCEA_EDC_CNT*`, `RMI_*STATUS*`, `ATC_L2_STATUS*`, `VM_L2_STATUS`, `VM_L2_PROTECTION_FAULT_STATUS`, and `VM_CONTEXTn_CNTL`.

### subset-b-002635: lines 7194-9653

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 7194-9653

## Scope

This chunk is a generated AMD GC 9.1 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, variables, allocations, locks, callbacks, includes, or executable branches in this range.

The selected lines begin in the tail of the `VM_CONTEXT9_CNTL` mask list, then cover VM context control for contexts 10-15, global VM-context disable bits, VM invalidation engines 0-17, per-context page table base/start/end addresses for contexts 0-15, VM shared memory-controller aperture/TLB controls, and a large `gc_ea_gceadec` block for GCEA DRAM and IO request grouping, priority, address normalization, and address decode. Although this path sits under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_9_1_sh_mask.h` supplies bit layouts for the GC 9.1 graphics IP. Driver code pairs these masks with register addresses from the matching `gc_9_1_offset.h` header and uses AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to pack fields for MMIO writes, command-stream setup, firmware initialization, or diagnostic reads.

This chunk describes three main hardware surfaces:

- GPU virtual memory context programming: context enable, page-table depth/block size, retry behavior, fault interrupt/default controls, global context disable bits, invalidation engine request/ack/semaphore fields, invalidation address ranges, and per-context page table base/start/end logical page numbers.
- VM shared memory-controller policy: NB MMIO and PCI aperture controls, top-of-DRAM and framebuffer/system/AGP aperture ranges, default physical aperture address, direct-system/cacheable/local-HBM aperture configuration, reset request bits for PF/VF virtualization, memory light-sleep timing, and L1 TLB/ATC controls.
- GCEA/effective-address memory scheduling and decode: DRAM and IO client-to-group maps, group-to-virtual-channel maps, lazy delays, CAM depth/reorder limits, page burst limits, priority aging/queue/fixed/urgency/quantum thresholds, address normalization, DRAM/GMI bank/channel/chip-select/rank-mask selection, hashing, harvesting, and duplicated address decoder 0/1 mappings for primary and secondary chip selects.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register-address symbols are supplied by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`.
- AMDGPU consumers typically combine these definitions with `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, and ASIC-specific initialization or golden-register tables.

Notable macro families in this slice are:

- `VM_CONTEXT10_CNTL` through `VM_CONTEXT15_CNTL`: per-VMID context enable, page table depth, page table block size, retry-on-fault controls, and individual fault interrupt/default behavior for range, dummy-page, PDE0, valid, read, write, and execute protection faults. The chunk also includes the last eight mask macros for `VM_CONTEXT9_CNTL`.
- `VM_CONTEXTS_DISABLE`: one disable bit for each VM context 0-15.
- `VM_INVALIDATE_ENG*_SEM`, `VM_INVALIDATE_ENG*_REQ`, `VM_INVALIDATE_ENG*_ACK`, and `VM_INVALIDATE_ENG*_ADDR_RANGE_{LO32,HI32}`: semaphore, request, acknowledgement, and optional logical-page-number range fields for invalidation engines 0-17. Request fields include invalidate-start, invalidate-end, PASID, flush type, and invalidation type.
- `VM_CONTEXT*_PAGE_TABLE_BASE_ADDR_{LO32,HI32}`, `VM_CONTEXT*_PAGE_TABLE_START_ADDR_{LO32,HI32}`, and `VM_CONTEXT*_PAGE_TABLE_END_ADDR_{LO32,HI32}`: split low/high logical page number fields for contexts 0-15.
- `MC_VM_NB_*`, `MC_VM_FB_OFFSET`, `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_*`, `MC_VM_STEERING`, `MC_SHARED_VIRT_RESET_REQ`, `MC_MEM_POWER_LS`, `MC_VM_CACHEABLE_DRAM_ADDRESS_*`, `MC_VM_APT_CNTL`, and `MC_VM_LOCAL_HBM_ADDRESS_*`: memory-controller aperture, PCI/MMIO, virtualization reset, cacheability, local memory, and power timing fields.
- `MC_VM_FB_LOCATION_*`, `MC_VM_AGP_*`, `MC_VM_SYSTEM_APERTURE_*`, and `MC_VM_MX_L1_TLB_CNTL`: framebuffer/AGP/system aperture limits and L1 TLB/system-access/advanced-driver-model/memory-type/ATC controls.
- `GCEA_DRAM_{RD,WR}_CLI2GRP_MAP{0,1}` and `GCEA_IO_{RD,WR}_CLI2GRP_MAP{0,1}`: 2-bit group assignment fields for client IDs 0-31, separately for DRAM read/write and IO read/write traffic.
- `GCEA_DRAM_{RD,WR}_GRP2VC_MAP`, `GCEA_DRAM_{RD,WR}_LAZY`, `GCEA_DRAM_{RD,WR}_CAM_CNTL`, and `GCEA_DRAM_PAGE_BURST`: GCEA DRAM group-to-VC mapping, delay, CAM sizing/reorder, and read/write burst limit fields.
- `GCEA_DRAM_{RD,WR}_PRI_AGE`, `GCEA_DRAM_{RD,WR}_PRI_QUEUING`, `GCEA_DRAM_{RD,WR}_PRI_FIXED`, `GCEA_DRAM_{RD,WR}_PRI_URGENCY`, and `GCEA_DRAM_{RD,WR}_PRI_QUANT_PRI{1,2,3}`: per-group priority aging, queuing, fixed priority, urgency, and threshold controls.
- `GCEA_ADDRNORM_*`, `GCEA_ADDRDEC_BANK_CFG`, `GCEA_ADDRDEC_MISC_CFG`, `GCEA_ADDRDECDRAM_ADDR_HASH_*`, and `GCEA_ADDRDECDRAM_HARVEST_ENABLE`: address range validity, interleave selection, socket/die/fabric target, high-address offset, DRAM hole, bank/GMI selection, VCM/channel/chip-select/rank-mask masks, address hashing, and harvest forcing.
- `GCEA_ADDRDEC{0,1}_*`: two parallel decoder instances with chip-select enable/base, address masks, address geometry, bank/row/column selectors, rank-mask selectors, channel-bit choice, and row-MSB inversion for CS01, CS23, SECCS01, and SECCS23.
- `GCEA_IO_RD_COMBINE_FLUSH`, `GCEA_IO_WR_COMBINE_FLUSH`, `GCEA_IO_GROUP_BURST`, `GCEA_IO_{RD,WR}_PRI_AGE`, and `GCEA_IO_{RD,WR}_PRI_QUEUING`: IO traffic flush timers, read/write burst limits, and per-group priority controls. The chunk ends at the first two shift macros of `GCEA_IO_RD_PRI_FIXED`, so the rest of that register is outside this work item.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 9.1 register definitions for the detected ASIC.
2. Choose a register address from `gc_9_1_offset.h`.
3. Read a current register value or construct a new register payload.
4. Use the `__SHIFT` and `__MASK` constants, usually through common field helpers, to extract or insert field values.
5. Write the value through MMIO, include it in a command stream where supported, or decode it for debugging, reset, fault handling, or telemetry.

For VM context programming, initialization code sets page table depth/block size and enables contexts, then programs page table base/start/end addresses. Fault policy fields decide whether protection faults interrupt, use a default behavior, or retry for specific classes. `VM_CONTEXTS_DISABLE` can globally prevent selected contexts from being used, so it must be coordinated with VMID allocation, queue setup, and reset flows.

For invalidation, software or firmware sequences an invalidation engine by coordinating its semaphore, address range, request, and acknowledgement fields. The `REQ` fields encode the start/end trigger, PASID, flush type, and invalidate type; the `ACK` fields report completion for the engine. The header does not encode ordering rules, poll timeouts, fences, or cache/TLB dependencies around those writes.

For MC and GCEA programming, boot, resume, reset, virtualization, and golden-register paths establish aperture limits, TLB behavior, cacheable/local-memory windows, client grouping, virtual-channel routing, DRAM address mapping, priority controls, and IO throttling. Diagnostic paths may also read these registers to explain memory routing, aperture, or translation behavior.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, the kernel driver, and command submission.

VM context control and page-table address registers are persistent VMID state. They define whether a context is enabled, how page tables are walked, which virtual range is valid, where page tables start, and how faults are surfaced. Incorrect field packing can disable a context, point a VMID at the wrong page table, select the wrong page-table depth, hide important faults, or generate interrupt storms.

Invalidation engine registers are stateful synchronization interfaces. Request bits can trigger TLB/cache invalidation work, acknowledgement bits can be polled or latched, and range registers scope the invalidation. Races or stale fields can produce missed translations, overbroad flushes, hangs while waiting for ACK, or incorrectly attributed PASID invalidations.

MC aperture and TLB registers persist platform memory policy. Framebuffer, AGP, system aperture, local HBM, TOM, MMIO, default physical page, steering, direct-system, memory type, ATC, and L1 TLB fields must match firmware discovery and platform topology. Wrong values can route accesses outside intended memory, produce GPU page faults, break PCI/MMIO visibility, or corrupt coherency.

GCEA registers persist low-level memory scheduling and address decode policy. Client grouping, VC mapping, priority coefficients, burst limits, address normalization, hashing, bank/channel/chip-select selection, and harvesting settings can affect correctness and performance. A decode mismatch against real DRAM/GMI topology can create silent data corruption or hard hangs; priority and CAM mistakes can also show up as starvation or severe bandwidth loss rather than immediate failures.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.1 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h` provides the matching register addresses.
- Common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, and golden-register programming helpers consume these shift and mask definitions.
- GC/GMC/GFXHUB/MMHUB code is the likely consumer of the VM context, invalidation, aperture, and TLB fields.
- Reset, suspend/resume, SR-IOV, KFD queue management, PASID handling, VM fault handling, and GPU hang recovery paths depend on these registers being programmed and decoded consistently.
- Platform discovery and firmware tables provide the topology values that must be packed into framebuffer/system/AGP/local-memory ranges and GCEA address decode fields.

Integration points include VMID setup, page table base programming, per-process PASID invalidation, GPUVM fault handling, global VM context masking during reset or virtualization, memory aperture setup, local HBM/cacheable DRAM region programming, ATC/system-access policy, memory-power light sleep timing, DRAM/IO QoS tuning, and board/ASIC-specific address decode and harvest configuration.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong mask or shift compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- The chunk starts and ends mid-family. It begins with the tail of `VM_CONTEXT9_CNTL` and ends after only `GCEA_IO_RD_PRI_FIXED__GROUP0_FIXED_COEFFICIENT__SHIFT` and `GROUP1_FIXED_COEFFICIENT__SHIFT`; adjacent chunks are required for complete context 9 and IO fixed-priority coverage.
- VM context controls are repetitive but not harmless. Copy/paste mistakes across contexts 10-15 can make one VMID use another context's policy or leave a context unexpectedly disabled.
- Split address registers require correct low/high composition and address-unit interpretation. The masks expose logical or physical page number bits, not necessarily byte addresses.
- Invalidation engines 0-17 are structurally similar. Software must target the correct engine, preserve unrelated fields, and pair request/ack/semaphore handling with the hardware-required ordering outside this header.
- PASID, invalidate type, and flush type fields are side-effectful. Incorrect values can flush the wrong address space, miss stale translations, or stall command processing.
- Fault interrupt/default fields can change reliability symptoms. Masking fault interrupts or selecting default handling may turn a visible protection fault into data corruption, retry loops, or delayed recovery.
- MC aperture and TLB settings are platform-sensitive. System aperture, framebuffer location, AGP windows, TOM, local HBM ranges, ATC, and memory type fields must agree with firmware, IOMMU, SR-IOV, and memory topology.
- GCEA address decode and hashing fields are correctness-critical. Bad base/mask/selector/hash/harvest values can alias chip-selects, select the wrong bank/channel/rank mapping, or access harvested resources.
- Priority, lazy, CAM, VC, and burst controls affect fairness and latency. Incorrect values may only appear as workload-specific bandwidth collapse, queue starvation, or intermittent timeouts.
- Full-width masks such as `0xFFFFFFFFL` do not imply arbitrary legal values; alignment, reserved encodings, topology constraints, and hardware sequencing are documented outside this generated header.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_9_1_sh_mask.h`, especially GC/GMC/GFXHUB/MMHUB, VM fault, reset, SR-IOV, KFD, and suspend/resume paths.
- Mechanical comparison against AMD's authoritative GC 9.1 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that registers in this chunk have matching address macros in `gc_9_1_offset.h`.
- Static mask/shift sanity checks: masks align with shifts, repeated VM context and invalidation-engine families remain consistent, 2-bit CID group fields tile 32-bit registers without overlap, and full-width/address fields use the expected masks.
- GPUVM tests that create multiple VMIDs, program page tables, exercise read/write/execute permissions, trigger valid/range/dummy/PDE0 faults, and verify interrupt/default/retry behavior.
- TLB invalidation tests that issue PASID and range invalidations through multiple engines, poll acknowledgements, and verify stale translations are removed without hangs.
- SR-IOV or virtualization tests that exercise `MC_SHARED_VIRT_RESET_REQ`, PF/VF reset paths, and VM context disable behavior.
- Aperture tests covering framebuffer, AGP, system aperture, cacheable DRAM, local HBM, default system aperture address, ATC, and L1 TLB configuration across boot, suspend/resume, and GPU reset.
- Memory stress tests checking DRAM/IO routing, GCEA client grouping, VC mapping, burst limits, priority aging/urgency/quantum settings, CAM reorder behavior, and starvation under mixed graphics/compute/DMA workloads.
- Platform/topology validation that verifies GCEA address normalization, bank/channel/chip-select/rank-mask selection, hashing, harvesting, and DRAM hole programming against discovered memory geometry.
- Runtime warning signals include VM fault storms, missed fault interrupts, invalidate ACK timeouts, stale GPU translations, incorrect PASID attribution, aperture out-of-range faults, unexplained memory corruption, DRAM bandwidth collapse, queue starvation, or repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002635`. It covers lines 7194-9653 of `gc_9_1_sh_mask.h`. The final per-file research should merge this with adjacent chunks to restore the beginning of `VM_CONTEXT9_CNTL` before line 7194 and the remainder of `GCEA_IO_RD_PRI_FIXED` plus later GC 9.1 register families after line 9653.

### subset-b-002636: lines 9654-12153

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 9654-12153

## Scope

This chunk covers a generated AMD GC 9.1 shader/register mask header range. It starts in the middle of the `GCEA_IO_RD_PRI_FIXED` definition and ends in the middle of `CPF_UTCL1_CNTL`, so the file-level report should reconcile this chunk with adjacent chunks before treating those boundary registers as complete. The range contains 2,143 `#define` macros that provide bit shifts and masks for GC 9.1 register fields.

The covered region spans the tail of the GCEA block, the `gc_tcdec` texture/cache block, the `gc_shdec` shader/compute register block, and the beginning of the `gc_cppdec` command-processor block. It is data-only C preprocessor surface: no functions, structs, or executable statements are defined here.

## Purpose

`gc_9_1_sh_mask.h` supplies compile-time bitfield metadata for AMDGPU code that programs GC 9.1 registers. The macros follow the generated naming pattern `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, allowing driver code to build register values through helpers such as `REG_SET_FIELD()` and to decode register dumps without hard-coded bit positions.

In this chunk, the register fields describe:

- GCEA request arbitration, priority, urgency, credit/reserve, miscellaneous, latency-sampling, and performance-counter controls.
- TCP/TCI/TCC/TCA cache and texture-channel controls, including invalidate/status bits, cache policy masks, EDC counters, redundancy, DSM controls, writeback/invalidate, and soft reset.
- Graphics shader stage programming registers for PS, VS, ES, GS, LS, and HS, including program base addresses, resource descriptors, late allocation, user-data SGPR payload registers, and pointer-to-user-data address registers.
- Compute dispatch state, including grid dimensions, starts/restarts, thread counts, shader program addresses, scratch bases, resource descriptors, VMID/resource limits, thread management, dispatch identifiers, wave restore addresses, relaunch controls, and compute user data.
- CP/CPC/CPF command-processor debug/fault/UTCL1 controls, including CP DFY address/data/cmd registers, EOP queue wait timing, CPC interrupt metadata, `CP_GFX_ERROR`, and UTCL1 invalidate/drop/bypass/snoop controls.

## Important API Surface

- `GCEA_IO_*` and `GCEA_SDP_*` macros define arbitration coefficients, urgency modes and masks, quantum priorities, SDP DRAM/final priority behavior, credits, tag/VCC/VCD reserves, request controls, latency sampling, and performance counters. These fields affect how GC clients arbitrate traffic and how performance tooling can sample that behavior.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CHAN_STEER_LO/HI`, `TCP_ADDR_CONFIG`, `TCP_CREDIT`, and `TCP_BUFFER_ADDR_HASH_CNTL` describe texture cache invalidation, busy/status reporting, control bits, channel steering, address hashing, and credit behavior. GC 9.1 golden settings in `amdgpu/gfx_v9_0.c` program `mmTCP_CHAN_STEER_LO` and `mmTCP_CHAN_STEER_HI`.
- `TC_CFG_L1_*`, `TC_CFG_L2_*`, `TCI_*`, `TCC_*`, and `TCA_*` define cache-policy and cache-controller fields for load/store/atomic behavior, volatile modes, L2/TCC controls, EDC counters, redundancy, DSM configuration, execution-disable, writeback/invalidate, and reset. These are low-level memory-hierarchy controls rather than user-facing APIs.
- `SPI_SHADER_PGM_RSRC*_{PS,VS,GS,HS}`, `SPI_SHADER_PGM_LO/HI_*`, `SPI_SHADER_LATE_ALLOC_VS`, and `SPI_SHADER_PGM_RSRC2_GS_VS` expose shader-stage program address and resource fields. Important fields include VGPR/SGPR counts, priority, float mode, privilege/debug/IEEE modes, scratch enable, LDS size, trap/debug wavefront behavior, EXCP_EN, user SGPR count, shared VGPR count, CU enable/disable controls, and wave limits.
- `SPI_SHADER_USER_DATA_{PS,VS,ES,LS,COMMON}_0` through `_31` and `SPI_SHADER_USER_DATA_ADDR_{LO,HI}_{GS,HS}` are the ABI-facing registers used to pass shader user data and indirect user-data addresses into graphics pipeline stages.
- `COMPUTE_DISPATCH_INITIATOR`, `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_NUM_THREAD_*`, `COMPUTE_PGM_LO/HI`, `COMPUTE_DISPATCH_PKT_ADDR_*`, `COMPUTE_DISPATCH_SCRATCH_BASE_*`, `COMPUTE_PGM_RSRC1/2`, `COMPUTE_VMID`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE*`, `COMPUTE_TMPRING_SIZE`, `COMPUTE_RESTART_*`, `COMPUTE_THREAD_TRACE_ENABLE`, `COMPUTE_DISPATCH_ID`, `COMPUTE_THREADGROUP_ID`, `COMPUTE_RELAUNCH`, `COMPUTE_WAVE_RESTORE_ADDR_*`, and `COMPUTE_USER_DATA_0` through `_15` form the compute-dispatch register ABI. `COMPUTE_DISPATCH_INITIATOR` includes fields such as `COMPUTE_SHADER_EN`, partial-threadgroup/ordering controls, scalar/vector L1 invalidate controls, reserved/DATA_ATC-position behavior, and restore.
- `CP_DFY_*` registers expose command-processor debug/fabric-yield style address, data, command, status, and control fields. `CP_DFY_DATA_0` through `_15` are full-width payload registers, while `CP_DFY_CMD` carries offset and size fields.
- `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, and `CP_VIRT_STATUS` describe CP/CPC wait timing, clock-gating sync periods, interrupt address/type/VMID/queue metadata, PASID, and virtualization status.
- `CP_GFX_ERROR` defines a dense fault bitmap for command-processor and graphics-path UTCL1 errors, including SUA, SEM, queue stream/EOP/pipe/read, sync memory read/write, shadow, append, CE DMA/init, PFP/VGT DMA, DMA source/destination, PFP/ME/CE TC, PRT LOD, read-pointer report, RB and instruction/constant/stream fetcher errors.
- `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, and the visible start of `CPF_UTCL1_CNTL` define UTCL1 XNACK retry timer, VMID reset, drop, bypass, invalidate, fragment-limit, force-snoop, force-dirty, no-PTE memory type, and CPF force-no-execute fields.

## Control Flow

There is no direct control flow in this header slice. Runtime behavior is indirect and comes from C code that includes this generated header, selects the matching `mmREGISTER` offset from the GC 9.1 address header, and writes values through MMIO, ring packets, golden-register initialization, or debug-register paths.

A typical consumer flow is:

1. Pick a register offset, usually from `gc_9_1_d.h` or SOC15 register macros.
2. Construct or patch a 32-bit value using `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, commonly through `REG_SET_FIELD()`.
3. Write the result through an AMDGPU register helper, a `PACKET3_SET_SH_REG` packet, or a golden-register table entry.
4. Hardware latches that value into graphics, compute, cache, or CP state until a later context restore, command stream, reset, or golden-setting pass changes it.

The chunk has concrete consumers in the surrounding AMDGPU tree. `gfx_v9_0.c` uses `REG_SET_FIELD(0, COMPUTE_DISPATCH_INITIATOR, COMPUTE_SHADER_EN, 1)` while building internal compute dispatch packets, and its GC 9.1 golden-setting tables program `mmCPC_UTCL1_CNTL`, `mmCPF_UTCL1_CNTL`, `mmCPG_UTCL1_CNTL`, `mmTCP_CHAN_STEER_LO`, and `mmTCP_CHAN_STEER_HI`. Register-dump tables include `CP_GFX_ERROR` for GFX generations, making these masks relevant to diagnostic decoding as well.

## State and Persistence

The macros themselves are stateless build artifacts, but they describe persistent hardware state:

- GCEA priority, urgency, reserve, and credit fields persist as arbitration policy for GC traffic until reprogrammed or reset.
- TCP/TCC/TCA/TCI controls persist as cache and memory-path policy; invalidate bits and writeback/invalidate controls can trigger transient hardware actions, but control fields such as channel steering, cache policy, redundancy, DSM, and EDC behavior remain configured state.
- Shader program address/resource and user-data registers persist as context state used by graphics draws. Incorrect user-data or resource fields can survive across draws until overwritten by later state emission.
- Compute dispatch registers persist as compute context state. Dispatch initiation and DATA_ATC/PTR32-related address-mode behavior integrate with KFD/HSA aperture interpretation; `kfd_flat_memory.c` documents that compute SUA mode is decoded from `COMPUTE_DISPATCH_INITIATOR:DATA_ATC` together with `SH_MEM_CONFIG:PTR32`.
- CP/CPC/CPF debug, interrupt, error, and UTCL1 fields persist as command-processor state. Error registers may be read for diagnostics; UTCL1 invalidate/drop/bypass/snoop settings affect address translation and memory consistency behavior for CP front-end paths.

Because this is generated hardware metadata, persistence risk is mostly in consumers using constants from the wrong ASIC generation or pairing a GC 9.1 mask with a non-GC-9.1 register offset.

## Dependencies and Integration Points

- The header depends on AMD's generated GC 9.1 register specification. It must stay synchronized with companion address headers such as `gc_9_1_d.h`; masks alone are not useful without matching register offsets.
- AMDGPU SOC15 helpers, register golden tables, ring packet emission, and debug/register-dump code are the main kernel integration points. The macros are consumed via preprocessor expansion rather than through typed C APIs.
- The compute fields connect to internal AMDGPU GPU tests and KFD/HSA dispatch semantics. `COMPUTE_DISPATCH_INITIATOR` is especially important because command packets, memory aperture mode, restore behavior, and cache invalidation semantics meet there.
- Shader user-data and program-resource fields are the ABI boundary between userspace driver state emission and the kernel/hardware register model. Userspace-generated command streams ultimately program these registers through the GPU command processor.
- Cache, TC/TCP/TCC/TCA, and UTCL1 fields integrate with VM, memory fault handling, cache flush/invalidate sequencing, golden-register initialization, and performance/debug tooling.

## Risks

- Boundary incompleteness: this chunk omits the start of `GCEA_IO_RD_PRI_FIXED` and the end of `CPF_UTCL1_CNTL`. Merge-time documentation must use neighboring chunks for complete field lists.
- Bitfield drift: if the generated shift/mask values diverge from the GC 9.1 hardware spec or the companion address header, register writes can silently program wrong bits.
- Untyped macro misuse: the compiler cannot prevent mixing `*_SHIFT` and `*_MASK` from different registers, different shader stages, or different GC generations.
- Repeated indexed registers create copy/paste hazards. `SPI_SHADER_USER_DATA_*_0..31`, `COMPUTE_USER_DATA_0..15`, `CP_DFY_DATA_0..15`, and stage-specific `SPI_SHADER_PGM_*` fields are parallel but not interchangeable.
- Address split fields are sensitive. `SPI_SHADER_PGM_LO/HI_*`, `COMPUTE_PGM_LO/HI`, dispatch packet address, scratch base, and wave-restore address fields must respect hardware alignment and high/low split rules.
- Cache and translation-control fields can cause severe failures. Incorrect invalidate, bypass, force-snoop, no-PTE memory type, XNACK retry, or VMID reset settings may surface as hangs, stale memory, VM faults, or data corruption.
- Debug/error masks are diagnostic-critical. Misdecoding `CP_GFX_ERROR`, `CPC_INT_INFO`, or `CPC_INT_PASID` can send triage toward the wrong queue, VMID, PASID, or faulting CP sub-block.

## Test Signals

- Build coverage: compiling AMDGPU with GC 9.1 support catches syntax errors, duplicate definitions, and missing macro names used by `REG_SET_FIELD()` or golden-setting tables.
- Generation consistency: compare the macros in this slice against AMD's GC 9.1 register source and verify one-to-one pairing with `gc_9_1_d.h` offsets for the same register names.
- Golden-register validation: boot GC 9.1 hardware or emulation and verify golden settings that program `mmCPC_UTCL1_CNTL`, `mmCPF_UTCL1_CNTL`, `mmCPG_UTCL1_CNTL`, `mmTCP_CHAN_STEER_LO`, and `mmTCP_CHAN_STEER_HI` apply without warnings or unexpected readback differences.
- Compute dispatch smoke tests: AMDGPU internal compute dispatch paths that write `COMPUTE_PGM_LO/HI` and `COMPUTE_DISPATCH_INITIATOR` should complete without fence timeouts, VM faults, or shader launch failures.
- KFD/HSA memory-mode tests: dispatches exercising HSA64/HSA32/GPUVM64 aperture behavior provide coverage for `COMPUTE_DISPATCH_INITIATOR` address-mode interactions.
- Graphics pipeline tests: draw workloads covering PS/VS/GS/HS/LS shader programming and user-data delivery validate the `SPI_SHADER_PGM_*` and `SPI_SHADER_USER_DATA_*` masks indirectly.
- Cache/VM stress: memory-coherency, cache-invalidate, XNACK, VM fault, and GPU reset tests are the strongest signals for the TC/TCP/TCC/TCA and CP/CPC/CPF UTCL1 fields.
- Debug validation: register dumps after injected or observed faults should decode `CP_GFX_ERROR`, `CPC_INT_INFO`, `CPC_INT_ADDR`, and `CPC_INT_PASID` consistently with the failing queue, VMID, PASID, and fault address.

### subset-b-002637: lines 12154-14604

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 12154-14604

## Scope

This chunk is a generated AMD GC 9.1 shift/mask register-header segment. It contains preprocessor constants only: every hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, global variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the mask tail for `CPF_UTCL1_CNTL`, then cover a large command-processor block, the `gc_cppdec2` scheduler/doorbell/status block, the `gc_spipdec` SPI scheduling/resource-reservation block, the `gc_cpphqddec` hardware queue descriptor block, and the beginning of DIDT/CAC/EDC power-management controls. Although the path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_9_1_sh_mask.h` supplies bit layouts for the GC 9.1 graphics IP. Driver code pairs these masks with register addresses from `gc_9_1_offset.h` and uses AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and SOC15 register-offset helpers to pack fields for MMIO writes, command-processor setup, KFD/MQD queue setup, interrupt programming, debug collection, and status decoding.

This chunk describes these hardware areas:

- CPF/CP UTCL1 fields for cache/TLB-related command-processor behavior, including bypass, invalidate, snoop, VMID dirty, no-PTE mode, and no-execute policy.
- Graphics command-processor ring-buffer state: base addresses, control words, read/write pointers, read-pointer report addresses, write-pointer polling addresses, buffer-size masks, VMID selection, active bits, doorbell control/ranges, ring priorities, and fatal/interrupt state.
- Per-ring and per-ME/MEC interrupt enable/status registers for VM doorbell writes, ECC, general protection faults, busy/empty/idle state, privileged instruction/register faults, opcode errors, timestamps, reserved-bit errors, and generic interrupts.
- CP power, memory-sleep, ECC first-occurrence, VMID reset/preempt/status, program-counter start, interrupt-routine start, context-control, context-count, instruction-queue wait-time, CPC instruction-cache, CPC op-control, and MEC F32 interrupt-disabling fields.
- `gc_cppdec2` scheduler doorbell controls for scheduler slots 0-7, doorbell clear/range fields, GFX MQD base/control, CP ring status, CPG/CPC/CPF UTCL1 status, SD control, soft reset controls, and CPC graphics control.
- `gc_spipdec` SPI arbitration, pipe cycle/percentage controls, compute-queue reset, per-CU resource-reservation masks, per-CU reservation enable masks, compute wavefront context-save control, and arbitration control.
- `gc_cpphqddec` HQD/MQD queue registers: GFX queue state, HPD status/UTCL1 error reporting, MQD base, HQD active/VMID/persistent state, queue priorities/quantum, packet-queue and indirect-buffer base/pointer/control, doorbell controls, dequeue requests, DMA/offload/semaphore/message fields, HQ scheduler/status/control, EOP ring, context-save buffers, GDS resource state, HQD error bits, AQL control, and packet-queue write-pointer memory fields.
- DIDT/CAC/EDC controls for dynamic inductive droop throttling, compute activity counters, clock-gating override, aggregation counters, power bounds, weighting by block, and the first EDC control bits.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Address symbols live in the matching GC 9.1 offset header; this file only describes field positions.

Notable macro families in this slice are:

- `CP_RB0_*`, `CP_RB1_*`, `CP_RB2_*`, and generic `CP_RB_*`: ring-buffer base/control, read/write pointer, read-pointer report address, write-pointer polling, buffer-size mask, VMID, and active-state fields.
- `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, and `CP_RB_DOORBELL_CONTROL_SCH_[0-7]`: doorbell routing, offset, enable, hit-clear, range, and scheduler-slot doorbell controls.
- `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING[0-2]`, `CP_INT_STATUS_RING[0-2]`, `CP_ME[1-2]_PIPE[0-3]_INT_CNTL`, `CP_ME[1-2]_PIPE[0-3]_INT_STATUS`, `CPC_INT_CNTL`, and `CPC_INT_STATUS`: interrupt enables and status bits for CP/CPC/MEC rings and pipes.
- `CP_ME*_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME*_PIPE*_PRIORITY`, and `CP_RING*_PRIORITY`: priority count and priority-selection fields for graphics and compute rings.
- `CP_FATAL_ERROR`, `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_ECC_FIRSTOCCURRENCE*`, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CP_PQ_STATUS`, `CP_CONTEXT_CNTL`, and `CP_MAX_CONTEXT`: fault, power, ECC, VMID, queue, and context-control/status fields.
- `CP_CE/PFP/ME/MEC*_PRGRM_CNTR_START` and `CP_CE/PFP/ME/MEC*_INTR_ROUTINE_START`: micro-engine program counter and interrupt-routine start addresses.
- `CP_CPC_IC_*`, `CP_CPC_IC_OP_CNTL`, `CP_CPC_GFX_CNTL`, `CPG_UTCL1_*`, `CPC_UTCL1_*`, and `CPF_UTCL1_*`: CPC instruction cache, CPC graphics control, and command-processor UTCL1 error/status/control fields.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_*`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_RESOURCE_RESERVE_CU_*`, `SPI_RESOURCE_RESERVE_EN_CU_*`, `SPI_COMPUTE_WF_CTX_SAVE`, and `SPI_ARB_CNTL_0`: SPI queue arbitration, pipe-share, queue reset, CU reservation, and context-save controls.
- `CP_HQD_*`, `CP_HPD_*`, `CP_MQD_*`, and `CP_GFX_MQD_*`: HQD/MQD queue state, persistent state, PQ/IB/EOP rings, doorbells, dequeue/offload/semaphore/message operations, AQL control, GDS resources, context-save locations, and error reporting.
- `DIDT_IND_*`, `GC_CAC_*`, `GC_DIDT_*`, and `GC_EDC_CTRL`: indirect DIDT access, activity counter windows/aggregation, soft snapshot, droop-throttle power limits/weights, and EDC enable/reset/clock/stall control bits.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Detect a GC 9.1 ASIC and include/select the matching generated register headers.
2. Choose a register address from `gc_9_1_offset.h` or a SOC15 register-offset table.
3. Read an existing register value, construct a new register value, or decode a status/debug value.
4. Use these `__SHIFT` and `__MASK` constants directly or through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`.
5. Apply the value during ring initialization, MQD/HQD programming, doorbell setup, interrupt enablement, queue scheduling, power-management setup, reset/recovery, debugfs collection, hang analysis, or KFD queue management.

For graphics rings, callers typically program ring base addresses, read-pointer report addresses, write-pointer poll addresses, ring size/block size, VMID, and doorbell ranges before enabling the ring active bit. Write/read pointers and active/status fields then become live state used by scheduling and hang recovery.

For compute queues, KFD and MES/MQD paths populate HQD/MQD fields for packet-queue base, queue size, read/write pointer behavior, doorbells, privilege/KMD/TMZ state, priorities, EOP ring storage, indirect buffers, context-save buffers, and AQL behavior. Dequeue, offload, DMA, semaphore, message, and scheduler-control fields are command-state knobs rather than autonomous code in this header.

For interrupts, driver code writes enable fields in CP/CPC/ring/pipe interrupt-control registers and later decodes matching status registers. The names in this chunk show the intended one-to-one relationship between enable and status bits, but clear/ack behavior and ordering are governed by hardware and higher-level interrupt code.

For SPI and power-management fields, initialization/golden-setting paths can program persistent arbitration percentages, CU reservation masks, compute queue resets, context-save policy, CAC/DIDT windows, power bounds, weights, clock-gating overrides, and EDC enable/reset/stall controls. Status fields are read by diagnostics and recovery paths.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, command submission, AMDGPU initialization, KFD queue management, and reset/recovery code.

Ring-buffer and HQD/MQD fields are persistent execution state until rewritten, queue-dequeued, or reset. Base addresses, pointer-report addresses, doorbell offsets, VMIDs, queue sizes, priority/quantum fields, context-save addresses, and EOP/PQ/IB controls must match allocated GPU memory, VM mappings, and scheduler state. Pointer and status fields can change while the GPU is executing and should be treated as volatile.

Interrupt enable fields persist until disabled or reset. Interrupt status fields may be live, sticky, clear-on-read, or write-one-to-clear depending on the register behavior outside this header. Incorrectly mixing enable and status masks can either hide faults or create interrupt storms.

SPI CU reservation, arbitration, queue-reset, and context-save fields affect scheduling and occupancy. A bad mask or stale value can disable compute units, reserve the wrong CU ranges, reset the wrong compute queue, or break CWSR/context-save behavior.

UTCL1, CPC instruction-cache, power, CAC, DIDT, and EDC fields represent hardware policy and counters. Some are persistent controls, some are snapshots or aggregates, and some are live status. Full-register writes are risky because generated headers include reserved/unused masks but do not encode which reserved bits must be preserved.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.1 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h` provides matching register addresses.
- Common AMDGPU field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and `SOC15_REG_OFFSET` consume these macros.
- AMDGPU GFX ring setup, CP interrupt handling, reset/recovery, debug and register-dump paths use the CP ring, interrupt, status, and doorbell definitions.
- AMDKFD/MQD/MES-style queue setup uses the `CP_HQD_*`, `CP_MQD_*`, and queue-control bit definitions to create and update compute queue descriptors.
- Power and reliability paths consume `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `GC_CAC_*`, `GC_DIDT_*`, and `GC_EDC_CTRL` fields for clock/power/error behavior.

Integration points include graphics ring bring-up, compute queue creation and teardown, MQD save/restore, VMID assignment and preemption, doorbell aperture programming, KFD user-queue scheduling, interrupt enable/disable and ISR decode, GPU reset/hang diagnostics, golden-register programming, power gating/clock gating, ECC/EDC reporting, UTCL1 fault diagnosis, and shader/SPI resource scheduling.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading status.
- The range starts and ends mid-register family. It begins with only the tail masks for `CPF_UTCL1_CNTL` and ends before the remaining `GC_EDC_CTRL` masks plus later EDC status/threshold registers.
- Similar ring and queue families are not interchangeable. `CP_RB0_*`, generic `CP_RB_*`, `CP_RB1_*`, `CP_RB2_*`, scheduler doorbells, and HQD PQ/EOP/IB fields have similar names but different scopes and side effects.
- Address fields are often split into low/high registers or aligned fields. Full-width masks such as `0xFFFFFFFFL` do not remove alignment, VM, aperture, or high/low ordering constraints.
- Doorbell offset and range mistakes can route writes to the wrong ring, allow unintended user access, or leave a queue unable to receive work.
- Pointer-control fields such as no-update, polling, read-pointer reports, write-pointer high/low fields, and queue-full behavior can cause silent queue stalls if packed incorrectly.
- Interrupt fields can be volatile or sticky. Enabling the wrong bits can produce interrupt storms, while failing to preserve unrelated bits can hide GPU faults.
- `CP_VMID_RESET`, `CP_VMID_PREEMPT`, and HQD dequeue/offload controls can affect running queues; writes require hardware-specific sequencing outside this header.
- SPI CU reservation and arbitration fields can produce workload-dependent failures: disabled CUs, unfair scheduling, bad occupancy, or broken context-save behavior may only appear under compute pressure.
- CAC/DIDT/EDC controls affect throttling and power reliability. Incorrect windows, weights, bounds, or reset/clock override bits can cause performance collapse, unexpected throttling, or missed droop/error reporting.
- Reserved and unused masks are present. Callers should preserve reserved bits unless an ASIC programming guide or golden-register table explicitly specifies the value.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU and AMDKFD code that includes GC 9.1 generated register headers.
- Mechanical comparison against AMD's authoritative GC 9.1 register database to confirm every `__SHIFT` and `__MASK` value in this line range.
- Cross-checks that every register family in this chunk has matching address symbols in `gc_9_1_offset.h`.
- Static mask/shift sanity checks: masks align with shifts, fields do not overlap unexpectedly, full-width data fields use full-width masks, and repeated ring/pipe/HQD families remain structurally consistent where hardware expects them to.
- GFX ring bring-up tests that validate `CP_RB0_*`, doorbell range/control, read-pointer reporting, write-pointer polling, VMID, and active-state programming.
- KFD compute queue tests that create, run, preempt, dequeue, destroy, and restore queues while exercising HQD PQ/IB/EOP/context-save/AQL fields.
- Interrupt tests that enable CP/CPC/ring/pipe interrupt bits, trigger known events where possible, and verify status decode, ack/clear behavior, and absence of interrupt storms.
- GPU reset and hang-recovery tests that read CP ring status, HQD state, UTCL1 status/error fields, VMID status, and ECC/EDC first-occurrence fields after induced faults.
- SPI scheduling tests that exercise CU reservation masks, compute queue reset, arbitration percentages, and wavefront context save under graphics and compute workloads.
- Power/reliability tests that validate CAC aggregation, DIDT throttling controls, EDC control/reset/stall behavior, memory sleep, and clock-gating override settings across suspend/resume and runtime power transitions.
- Runtime warning signals include stuck CP/HQD pointers, inactive rings after doorbell writes, VMID reset/preempt hangs, bad queue priority/fairness, missing or excessive interrupts, UTCL1 error bits, ECC/EDC first-occurrence reports, unexpected throttling, and repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002637`. It covers lines 12154-14604 of `gc_9_1_sh_mask.h`. The final per-file research should merge this with adjacent chunks to recover the full `CPF_UTCL1_CNTL` context before line 12154 and the remainder of `GC_EDC_CTRL` plus later EDC fields after line 14604.

### subset-b-002638: lines 14605-17204

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 14605-17204

## Purpose

This chunk is generated AMD GC 9.1 register field metadata. It contains no executable driver logic; it publishes C preprocessor constants for hardware register bit positions and masks used by AMDGPU code when constructing, updating, or decoding Graphics Core MMIO register values.

The requested line range spans several GC hardware decode areas:

- The tail of GC-level EDC/DIDT and CAC metadata, beginning mid-`GC_EDC_CTRL` and then covering EDC thresholds/status/overflow, DIDT and EDC droop controls, GC/SE CAC indirect index/data registers, and SE CAC clock-gating timing.
- `addressBlock: gc_tcpdec`, covering TCP watchpoint address/control registers, GATCL1/UTCL1 controls and status, and TCP perf-counter filter fields.
- `addressBlock: gc_gdspdec`, covering GDS per-VMID base/size windows, GWS/OA per-VMID ownership, GWS/OA reset controls, compute max wave ID, GDS enhance/restore bits, and compute/graphics context-switch status/counters.
- `addressBlock: gc_rasdec`, covering RAS signature controls and signature readback registers for SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI blocks.
- The beginning of `addressBlock: gc_gfxdec0`, covering DB depth/stencil/render state, PA scissor/clip/window/viewport state, CB target/shader masks and blend constants, CP context identifiers, VGT reset index, DCC/stencil state, viewport transforms, user clip planes, and `SPI_PS_INPUT_CNTL_0` through the first fields of `SPI_PS_INPUT_CNTL_14`.

The chunk has more than 2,100 `#define` lines. The line boundaries are artificial: line 14605 starts after the `GC_EDC_CTRL` shift and low mask fields, and line 17204 stops before the remaining `SPI_PS_INPUT_CNTL_14` masks. Adjacent chunks are required for complete per-register coverage at both edges.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU kernel-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field within a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: mask used to extract, clear, or set that field.

These constants are intended to be paired with the matching address macros in `gc_9_1_offset.h`, then consumed through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `REG_GET_FIELD`, `REG_SET_FIELD`, and lower-level CGS accessors.

Representative register groups in this chunk:

- `GC_EDC_*`, `GC_DIDT_DROOP_CTRL`, `GC_EDC_DROOP_CTRL`, `GC_CAC_IND_*`, and `SE_CAC_*`: power droop, electrical-design-current throttling/status, CAC indirect access, and SE CAC clock-gating fields.
- `TCP_WATCH{0..3}_ADDR_{H,L}` and `TCP_WATCH{0..3}_CNTL`: TCP address watchpoint comparators with address, mask, VMID, ATC, mode, and valid fields.
- `TCP_GATCL1_CNTL`, `TCP_UTCL1_CNTL1`, `TCP_UTCL1_CNTL2`, and `TCP_UTCL1_STATUS`: texture cache and L1 translation/cache behavior, invalidation, fault response, snooping, force-miss, FIFO/cache-depth reduction, and status fields.
- `TCP_PERFCOUNTER_FILTER` and `_EN`: per-event perf-counter selection and enable fields for texture-cache-related counters.
- `GDS_VMID{0..15}_BASE` and `GDS_VMID{0..15}_SIZE`: per-VMID GDS address-window base and size fields.
- `GDS_GWS_VMID{0..15}` and `GDS_OA_VMID{0..15}`: per-VMID ownership/resource fields for global wave sync and ordered append.
- `GDS_GWS_RESET*`, `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, and `GDS_OA_RESET`: reset masks and reset triggers for GDS-managed resources.
- `GDS_*_CTXSW_*`: context-switch status and counters for compute shader, graphics shader, VS, PS0-PS7, and GS activity.
- `RAS_*_SIGNATURE*`: signature-control and per-block signature readback fields used for RAS/diagnostic comparison.
- `DB_*`: depth/stencil render control, depth view, render override, htile base, depth/stencil clear values, Z/stencil info and base addresses, and DFSM controls.
- `PA_SC_*`, `PA_SU_*`, and `PA_CL_*`: screen/window/generic/viewport scissors, clip-rect rules, edge rules, hardware screen offset, raster config, tile steering, viewport transforms, and user clip planes.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_BLEND_*`, and `CB_DCC_CONTROL`: color-buffer write masks, shader export masks, blend constants, and DCC behavior.
- `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID`: command processor context identification and perfmon context fields.
- `VGT_MULTI_PRIM_IB_RESET_INDX`: primitive restart index for indexed draws.
- `SPI_PS_INPUT_CNTL_{0..14}`: pixel-shader interpolator input metadata fields such as attribute offset, default values, flat shade, cylindrical wrap, point-sprite texture selection, duplication, FP16 interpolation mode, and attribute-valid bits.

## Control Flow

This header has no local control flow. It participates in runtime behavior only through macro expansion in code that reads, modifies, and writes registers.

Common usage follows a read-modify-write pattern:

1. Runtime code reads a register value from the GC address space or an indirect index/data pair.
2. It clears a field with `~<REGISTER>__<FIELD>_MASK`.
3. It shifts a desired value by `<REGISTER>__<FIELD>__SHIFT` and masks it back into place.
4. It writes the resulting register value, or extracts a field with the same mask/shift pair for status decisions.

For the GC EDC/DIDT fields, power-management code uses table-driven configuration entries containing an offset, mask, shift, and value. The local Vega10 PowerTune implementation demonstrates the pattern for same-named GC EDC fields: `vega10_program_gc_didt_config_registers()` reads a register, clears the configured mask, ORs `(value << shift) & mask`, and writes the value back; `vega10_enable_psm_gc_edc_config()` wraps related programming with RLC safe-mode entry/exit and shader-engine selection.

For DB/PA/CB/VGT/SPI state, the control flow is normally driven by command submission and graphics pipeline setup rather than ordinary CPU-side loops in this header. User-mode or kernel command builders emit register writes for draw state; hardware then consumes these fields during depth/stencil testing, rasterization, clipping, viewport transform, color export, interpolation, and primitive restart handling.

GDS and TCP fields sit on compute and memory/cache control paths. GDS base/size/ownership/reset fields are relevant to queue setup, context switching, and resource isolation by VMID. TCP watchpoints, UTCL1 invalidation, and perf-counter filters are diagnostic, cache-control, or performance-measurement surfaces; correct sequencing is imposed by the relevant cache, VM, or profiling code rather than by this generated file.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state.

EDC/DIDT/CAC registers hold power-management configuration and status. Control fields can enable throttling, reset logic, select droop levels, configure thresholds, or select indirect CAC addresses; status fields expose throttle levels, rolling droop/power deltas, overflow conditions, and similar hardware-maintained values.

TCP registers hold watchpoint, translation/cache, invalidation, and perf-counter state. Watchpoint `VALID`, `VMID`, `ATC`, `MODE`, address, and mask fields persist in hardware until overwritten or reset. UTCL1 invalidation and force-miss/force-snoop controls may be transient or side-effect-sensitive depending on the hardware programming sequence.

GDS registers hold VMID-scoped resource allocation and context-switch accounting state. Base/size and GWS/OA ownership fields define resource partitioning. Reset fields can clear resources, while context-switch counters/status reflect hardware-maintained activity and may be sticky until reset or overwritten by hardware.

RAS signature registers are diagnostic state. Signature control/mask fields configure collection or comparison, and signature registers expose block-specific values that are meaningful only under the selected RAS/test mode.

DB/PA/CB/VGT/SPI registers are graphics pipeline state. They persist in the GPU context until command streams, context switches, suspend/resume, reset, or driver reinitialization replace them. Many of these fields are part of user-visible rendering correctness: scissor bounds, viewport transforms, depth/stencil base addresses, target masks, shader export masks, and pixel-shader input controls directly affect draws.

The header does not encode read-only, write-one-to-clear, self-clearing, sticky, privilege, or reserved-bit semantics. Those properties are hardware-defined and must be respected by the code that uses the masks.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`, which supplies matching register offsets and base-index symbols. This shift/mask header must remain synchronized with that offset header and AMD's GC 9.1 register database.

Other nearby integration surfaces include:

- AMDGPU SOC15 access helpers and field helpers used to read/write GC registers.
- PowerPlay/PowerTune DIDT and EDC code paths that use offset/mask/shift/value tables to program GC power-management registers.
- GFX/RLC safe-mode and GRBM index selection when programming per-SE or per-instance graphics state.
- KFD and graphics queue setup paths that depend on GDS partitioning, VMID resource ownership, and context-switch state.
- Command submission and graphics pipeline state programming paths that consume DB, PA, CB, VGT, and SPI field layouts.
- RAS and diagnostics paths that read signature registers or set signature controls.
- Perf/debug paths that configure TCP perf filters, watchpoints, or register dumps.

In this tree, direct textual inclusion of `gc_9_1_sh_mask.h` was not observed in the C files searched; `gc_9_1_offset.h` is included by `psp_v10_0.c`, and same-named GC EDC/DIDT field macros are used by `pm/powerplay/hwmgr/vega10_powertune.c` through that platform's include stack. The exact generated generation selected at compile time is ASIC-specific, so users must pair GC 9.1 offsets and masks rather than mixing them with GC 9.0, GC 10, or later headers that may share names but differ in bit layout.

## Risks And Edge Cases

- These macros are untyped numeric constants. A wrong mask or shift compiles cleanly but can program the wrong hardware bits.
- The chunk contains many repeated per-VMID, per-viewport, per-pixel-shader-input, and per-pipeline-stage register families. A generation or copy error can affect only one VMID, viewport, PS input slot, or shader stage, making failures sparse and workload-specific.
- The range starts and ends mid-register. Research consumers must merge adjacent chunks before making complete claims about `GC_EDC_CTRL` or `SPI_PS_INPUT_CNTL_14`.
- Reserved and `UNUSED` masks are present. Blindly writing full register values can corrupt reserved fields unless hardware documentation explicitly requires it.
- EDC/DIDT fields affect throttling, droop handling, clock override, and force-stall behavior. Bad programming can create power, stability, or performance failures that only appear under load, thermal pressure, or power-management transitions.
- TCP watchpoint and UTCL1 invalidation fields are VMID- and address-sensitive. Incorrect `VMID`, `ATC`, address, mask, or invalidation fields can miss debug events, disrupt translation behavior, or create cache-coherency symptoms.
- GDS VMID base/size and GWS/OA ownership fields are isolation-sensitive. Wrong masks can overlap VMID resources or reset the wrong GDS allocation.
- DB depth/stencil and base-address fields are memory-safety-sensitive. Bad masks can point hardware at the wrong depth, stencil, or htile memory or misconfigure compressed/decompressed layout fields.
- PA scissor, clip, viewport, and user clip-plane fields are rendering-correctness-sensitive. Off-by-one or sign/width mistakes usually show up as clipped, missing, or overdrawn pixels rather than immediate driver errors.
- `SPI_PS_INPUT_CNTL_*` fields define interpolation and attribute validity. A wrong attribute offset, default, point-sprite, FP16 interpolation, or valid bit can produce shader input corruption that varies by pipeline state.

## Test Signals

Useful validation is mostly integration and hardware oriented:

- Kernel build coverage with AMDGPU, PowerPlay, GFX, KFD, RAS, and debug/perf code enabled catches missing or renamed macros.
- Static checks should verify that GC 9.1 offset and shift/mask headers are regenerated together and that same-named fields are not accidentally mixed across GC generations.
- Power-management validation should exercise DIDT/EDC enable, disable, reset, forced-stall, load, idle, suspend/resume, and thermal/power-limit transitions while monitoring for ring timeouts, throttling anomalies, and unstable clocks.
- TCP and UTCL1 validation should cover VMID-specific watchpoints, address masks, invalidation paths, perf-counter filters, and fault-response modes.
- GDS validation should run compute workloads using multiple queues/VMIDs and verify that GDS, GWS, and OA resources remain isolated across context switches and resets.
- RAS/debug validation should confirm that signature controls and signature readbacks change predictably under the selected diagnostic mode and do not report stale values after reset.
- Graphics validation should include depth/stencil, DCC, scissor/clip/window, viewport arrays, primitive restart, blend constants, target/shader masks, and pixel-shader interpolation tests.
- Register tracing around read-modify-write sequences should confirm that only intended field masks change and reserved bits are preserved.

### subset-b-002639: lines 17205-19598

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 17205-19598

## Scope

This chunk covers a generated AMD GC 9.1 shader/register mask header range. It starts inside the mask half of `SPI_PS_INPUT_CNTL_14` and ends inside the shift half of `CB_COLOR1_INFO`, so adjacent chunks are needed for the complete file-level view. The range contains 2,174 `#define` macros and 220 register comment anchors. The macros are almost entirely paired bitfield constants named `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.

## Purpose

`gc_9_1_sh_mask.h` provides compile-time bit positions and masks for GC 9.1 graphics registers used by the AMDGPU driver. This slice describes late graphics-pipeline state: pixel shader input routing, interpolation controls, shader export formats, blend optimization, render target blend controls, primitive assembly, tessellation and geometry-stage routing, depth/stencil controls, rasterization, MSAA sample locations and masks, streamout, and the beginning of color buffer render-target state.

The file does not implement executable behavior. Its value is as a hardware contract: C code can compose register values without hard-coding bit positions, while companion address headers provide the matching `mm...` register offsets. The constants in this chunk are consumed indirectly by register initialization, command emission, clear-state tables, golden-register programming, and debugging/decode code for GC 9.1 ASICs.

## Important API Surface

- `SPI_PS_INPUT_CNTL_14` through `SPI_PS_INPUT_CNTL_31` describe pixel shader input attribute routing. The chunk begins with remaining `SPI_PS_INPUT_CNTL_14` masks, then complete entries for 15-31. Common fields include `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `CYL_WRAP`, `PT_SPRITE_TEX`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, and attribute-valid bits.
- `SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL` define shader interface state: VS export count, PS input enable/address masks, interpolation mode, barycentric behavior, point/linear center selections, position sample selection, and related PS-side routing.
- `SPI_TMPRING_SIZE`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` cover shader temporary-ring sizing and shader export formats for position, depth/stencil/sample-mask, and color MRT outputs.
- `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, and `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` define shader export/color downconversion and blend optimization controls for multiple render targets.
- `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL`, `CB_MRT0_EPITCH` through `CB_MRT7_EPITCH`, `CB_COLOR_CONTROL`, and the first `CB_COLOR0_*`/`CB_COLOR1_*` groups define color-blend equations, MRT pitch, color-operation mode, render-target base addresses, views, formats, DCC/CMASK/FMASK metadata bases, and clear words.
- `DB_DEPTH_CONTROL`, `DB_EQAA`, `DB_SHADER_CONTROL`, `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK` define depth/stencil, EQAA, shader depth export, HTILE metadata, sample-result compare, preload, and alpha-to-coverage state.
- `PA_CL_*`, `PA_SU_*`, and `PA_SC_*` groups describe clipping, viewport transform, NaN/Inf handling, point/line setup, primitive filtering, over/conservative rasterization, centroid priority, AA sample locations, AA masks, binner controls, shader control, and scanner/rasterizer modes.
- `VGT_*`, `IA_ENHANCE`, and `WD_ENHANCE` groups cover draw initiation, DMA/index buffers, event initiation, primitive ID handling, tessellation distribution, shader-stage enables, LS/HS/GS/VS routing, streamout, instance stepping, and vertex reuse/deallocation controls.
- `CS_COPY_STATE` and `GFX_COPY_STATE` expose a single copy-state field each for compute/graphics copy-state handling.

There are no C types, structs, or functions in this slice. The public surface is the preprocessor namespace itself, and correctness depends on pairing each `__SHIFT` constant with its corresponding `_MASK` and register address.

## Control Flow

There is no direct control flow. Runtime flow happens in consumers:

1. Select the register offset from the matching GC 9.1 address header.
2. Build a 32-bit register value by shifting field values with `REGISTER__FIELD__SHIFT`.
3. Mask fields with `REGISTER__FIELD_MASK`.
4. Emit the value through MMIO writes, PM4 packets, clear-state restore, or golden-register setup.

The repeated register families in this chunk imply looped or table-driven consumers. MRT state commonly iterates over indices 0-7 for `SX_MRTn_BLEND_OPT`, `CB_BLENDn_CONTROL`, and `CB_MRTn_EPITCH`; streamout iterates over buffer slots 0-3; MSAA sample-location programming expands across pixel quadrants and sample pairs.

## State and Persistence

The macros are stateless build artifacts, but they describe persistent GPU context state. Once programmed, the underlying registers remain active until another command stream, context restore, clear-state packet, mode set, or GPU reset changes them.

Important persistent domains include:

- Pixel shader ABI state in `SPI_PS_INPUT_CNTL_*`, `SPI_PS_INPUT_ENA`, and `SPI_PS_INPUT_ADDR`; wrong offsets or validity bits can misroute interpolants or force default values into shaders.
- Render-target and blend state in `SX_*`, `CB_BLEND*`, `CB_COLOR_CONTROL`, and `CB_COLOR0_*`; incorrect format, blend, compression, base-address, or view fields can produce visible corruption or writes to the wrong surface.
- Primitive/tessellation/geometry routing in `VGT_*`; incorrect ring item sizes, output primitive types, subgroup sizes, or shader-stage enables can break draws or hang the graphics pipe.
- Depth/rasterization state in `DB_*`, `PA_CL_*`, `PA_SU_*`, and `PA_SC_*`; mismatches affect depth/stencil tests, conservative rasterization, AA coverage, point/line rendering, clipping, and binning behavior.
- Streamout state in `VGT_STRMOUT_*`; size, stride, offset, and buffer-filled-size fields persist across draw sequences and must match buffer allocations.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.1 register specification. This header must stay synchronized with companion GC 9.1 address-definition headers such as `gc_9_1_d.h` and other generated include files in `drivers/gpu/drm/amd/include/asic_reg/gc/`.
- Integrated into AMDGPU graphics code through SOC15 register access helpers, command submission paths, golden-register tables, clear-state data, and debug register dumps.
- Maps higher-level graphics API state from Mesa/Vulkan/OpenGL into hardware fields: shader input interpolation, MRT formats and blend modes, depth/stencil state, MSAA sample positions, streamout, primitive assembly, tessellation, and rasterization all eventually rely on these masks.
- Interacts with memory management through GPU address fields such as `VGT_DMA_BASE`, `VGT_EVENT_ADDRESS_REG`, `CB_COLOR0_BASE`, `CB_COLOR0_BASE_EXT`, `CB_COLOR0_CMASK`, `CB_COLOR0_FMASK`, and `CB_COLOR0_DCC_BASE`; callers must apply hardware alignment and address-splitting rules outside this header.
- Uses plain C preprocessor constants only. There is no type checking, range checking, or validation that a field value fits its mask.

## Risks

- Bitfield drift is the central risk. If these generated masks differ from the GC 9.1 hardware spec or the matching address header, register writes silently target the wrong bits.
- This chunk is boundary-partial: `SPI_PS_INPUT_CNTL_14` lacks the field shifts and early masks in this slice, while `CB_COLOR1_INFO` lacks most masks and later shifts here. Merge tooling must not treat either as fully documented by this chunk alone.
- Indexed render-target and blend families create copy/paste hazards. A wrong `CB_BLENDn_CONTROL`, `SX_MRTn_BLEND_OPT`, `CB_MRTn_EPITCH`, or `CB_COLORn_*` index can alter a different MRT than intended.
- Address and metadata fields have high blast radius. Incorrect `CB_COLOR0_*` base/extension, CMASK/FMASK/DCC base, DCC control, or `DB_HTILE_SURFACE` fields can corrupt render-target/depth metadata or trigger GPU VM faults.
- Shader-stage routing fields in `VGT_SHADER_STAGES_EN`, `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, and ring item-size registers must match compiled shader ABI assumptions. Mismatches can cause bad geometry output, missing primitives, or hangs.
- Rasterization controls such as `PA_SC_AA_SAMPLE_LOCS_*`, `PA_SC_AA_MASK_*`, `PA_SU_OVER_RASTERIZATION_CNTL`, and `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL` are visually sensitive and can cause subtle conformance failures without obvious kernel errors.

## Test Signals

- Build coverage: compiling AMDGPU with this header catches syntax errors, duplicate macros, and missing include dependencies.
- Generation consistency: compare this range against the GC 9.1 register source/spec and companion address header to verify each register has the expected field widths, masks, and shifts.
- Graphics conformance: Vulkan/OpenGL CTS cases for shader interpolation, point sprites, flat shading, MRT blending, color write masks, depth/stencil, tessellation, geometry shaders, streamout, MSAA sample locations, alpha-to-coverage, conservative rasterization, and primitive clipping exercise this register surface.
- Runtime smoke tests: boot a GC 9.1 device, run display plus 3D workloads, and monitor for GPU hangs, VM faults, bad render output, or golden-register warnings.
- Register-dump validation: decode known-good state emission using these masks, especially `SPI_PS_INPUT_CNTL_*`, `CB_BLEND*`, `DB_DEPTH_CONTROL`, `DB_SHADER_CONTROL`, `VGT_SHADER_STAGES_EN`, `PA_SC_AA_*`, `PA_SC_BINNER_*`, and `CB_COLOR0_*`.

### subset-b-002640: lines 19599-22320

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 19599-22320

## Scope

This chunk is a generated AMD GC 9.1 register bitfield header segment. It contains C preprocessor `#define` constants for register field shifts and masks, not executable driver logic. The visible range starts in the middle of `CB_COLOR1_INFO`, continues through color buffer targets 1-7, covers a large `gc_gfxudec` graphics/command-processor register block, covers `gc_perfddec` performance counter data registers, and ends at the beginning of `gc_perfsdec` with `CPG_PERFCOUNTER1_SELECT`.

The chunk exports 2,103 macro definitions across 605 register names. Each field generally appears as:

- `REGISTER__FIELD__SHIFT`, the low bit position for the field.
- `REGISTER__FIELD_MASK`, the full 32-bit mask for the field.

These macros are paired with the matching GC 9.1 offset header, primarily `gc_9_1_offset.h`, and with common AMDGPU helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.

## Purpose

The purpose of this chunk is to let GC 9.1 software program and decode hardware registers using symbolic field names instead of raw bit positions. The register families in this range support:

- Color-buffer render-target setup, including base addresses, views, formats, sample counts, swizzle modes, DCC/CMASK/FMASK metadata, fast-clear words, and compression controls for CB color targets 1-7.
- Command processor event, streamout, primitive/statistics, scratch, append/fence, atomic pre-operation, semaphore, CP DMA, coherency, indirect-buffer, command-buffer, metadata, draw/dispatch, index, and GDS backup registers.
- VGT/IA/WD/PA registers for primitive/index state, transform feedback, vertex/index buffers, multi-VGT parameters, screen extents, line stipple, and trap-screen controls.
- Shader and cache diagnostics, especially SQ thread trace setup/status, SQC cache invalidate/writeback controls, and SPI configuration.
- Depth/occlusion counters and GDS/GWS/OA/atomic registers for global data store access, synchronization resources, ordered append state, and GDS atomic operations.
- Performance counter readback registers for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, RMI, ATC L2, and MC VM L2 blocks.

The file is hardware metadata. It declares no functions, structs, variables, locks, or software-owned storage.

## Important Macro Groups

Color-buffer groups include `CB_COLOR1_*` through `CB_COLOR7_*`. For targets 2-7, this chunk includes complete visible groups for `BASE`, `BASE_EXT`, `ATTRIB2`, `VIEW`, `INFO`, `ATTRIB`, `DCC_CONTROL`, `CMASK`, `CMASK_BASE_EXT`, `FMASK`, `FMASK_BASE_EXT`, `CLEAR_WORD0`, `CLEAR_WORD1`, `DCC_BASE`, and `DCC_BASE_EXT`. Target 1 starts mid-register with late `CB_COLOR1_INFO` fields, then continues with `ATTRIB`, `DCC_CONTROL`, metadata base, clear-word, and DCC base fields. Important fields encode render target format/number type/component swap, fast clear, compression, blend optimization, DCC enablement, CMASK address type, resource type, color and FMASK swizzle modes, sample/fragment counts, RB/pipe alignment, MIP dimensions, slice ranges, and 256-byte-aligned base-address pieces.

Command processor event and query groups include `CP_EOP_DONE_ADDR_*`, `CP_EOP_DONE_DATA_*`, `CP_EOP_LAST_FENCE_*`, streamout addresses, primitive written/needed counters 0-3, `CP_PIPE_STATS_ADDR_*`, `CP_VGT_*INVOC*` and `CP_PA_*COUNT*` statistics, `CP_SC_PSINVOC_COUNT*`, `CP_PIPE_STATS_CONTROL`, `CP_STREAM_OUT_CONTROL`, and `CP_STRMOUT_CNTL`. These fields describe where the CP writes event/fence/query data and how streamout or pipeline statistics are controlled.

CP scratch, append, atomic, semaphore, and wait groups include `SCRATCH_REG0..7`, `SCRATCH_UMSK`, `SCRATCH_ADDR`, `CP_APPEND_*`, `CP_ATOMIC_PREOP_*`, `CP_ME_ATOMIC_PREOP_*`, `CP_PFP_ATOMIC_PREOP_*`, `CP_GDS_ATOMIC*_PREOP_*`, `CP_ME_GDS_ATOMIC*_PREOP_*`, `CP_PFP_GDS_ATOMIC*_PREOP_*`, `CP_ME_MC_*ADDR*`, `CP_ME_MC_WDATA_*`, `CP_SEM_WAIT_TIMER`, `CP_SIG_SEM_ADDR_*`, `CP_WAIT_SEM_ADDR_*`, and `CP_WAIT_REG_MEM_TIMEOUT`. Several high-address registers carry address bits plus `SEL`/`SWAP` fields, so consumers must preserve both addressing and access-mode bits.

CP DMA and coherency groups include `CP_DMA_PFP_CONTROL`, `CP_DMA_ME_CONTROL`, `CP_DMA_ME_COMMAND`, `CP_DMA_PFP_COMMAND`, source/destination address pairs, `CP_DMA_CNTL`, `CP_DMA_READ_TAGS`, `CP_COHER_BASE*`, `CP_COHER_SIZE*`, `CP_COHER_START_DELAY`, `CP_COHER_CNTL`, `CP_COHER_STATUS`, and the equivalent `CP_ME_COHER_*` controls. Coherency fields enable actions for TC noncoherent/write-combine/writeback, metadata invalidation, TCL1, CB, DB, shader K-cache, shader volatile K-cache, shader I-cache, and K-cache writeback. DMA command fields encode byte count and source/destination address-space/cache/increment behavior.

Indirect-buffer and command-buffer groups include `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, `CP_*_OFFSET`, `CP_IB*_PREAMBLE_*`, `CP_CE_*`, `CP_IB*_BASE_*`, `CP_IB*_BUFSZ`, `CP_ST_*`, and command buffer size registers. These fields define IB base/size/offset state, preamble ranges, CE command buffers, and state-shadow buffer addresses.

Draw, dispatch, index, and metadata groups include `CP_PFP_METADATA_BASE_ADDR*`, `CP_CE_METADATA_BASE_ADDR*`, `CP_DRAW_INDX_INDR_ADDR*`, `CP_DISPATCH_INDR_ADDR*`, `CP_INDEX_BASE_ADDR*`, `CP_INDEX_TYPE`, `CP_GDS_BKUP_ADDR*`, `CP_SAMPLE_STATUS`, `CP_PFP_COMPLETION_STATUS`, `CP_CE_COMPLETION_STATUS`, and `CP_PRED_NOT_VISIBLE`. `CP_SAMPLE_STATUS` is relatively dense, exposing request/enabled/done bits for counters, pixels, vertices, primitives, and GDS.

VGT/IA/WD/PA groups include `VGT_GSVS_RING_SIZE`, `VGT_PRIMITIVE_TYPE`, `VGT_INDEX_TYPE`, streamout filled sizes, max/min vertex index, index offset, multi-primitive reset enable, index and instance counts, transform feedback ring/base registers, HS off-chip parameters, WD position/control/index buffer bases, `IA_MULTI_VGT_PARAM`, `VGT_INSTANCE_BASE_ID`, line stipple, screen extent min/max pairs, and P3D/HP3D/general trap-screen controls. `GRBM_GFX_INDEX` selects shader engine, shader array, and instance broadcast behavior for instance-scoped GC accesses.

SQ/SQC/SPI groups include `SQ_THREAD_TRACE_BASE`, `SIZE`, `MASK`, `TOKEN_MASK`, `PERF_MASK`, `CTRL`, `MODE`, `BASE2`, `TOKEN_MASK2`, `WPTR`, `STATUS`, `HIWATER`, `CNTR`, and `USERDATA_0..3`, plus `SQC_CACHES`, `SQC_WRITEBACK`, `TA_CS_BC_BASE_ADDR*`, and `SPI_CONFIG_CNTL*`. Thread trace fields control CU/SH/SIMD/VMID selection, token filtering, shader-stage masking, capture mode, autoflush, performance capture, issue/test/interrupt/wrap behavior, write pointer status, buffer reset, and full/busy/error indications.

DB and GDS groups include occlusion counters 0-3, zpass count, direct GDS read/write/burst registers, `GDS_ATOM_*`, `GDS_GWS_RESOURCE*`, `GDS_OA_*`, and `GDS_WRITE_COMPLETE`. These fields expose low-level global data store access, GDS atomic operand/result registers, global wave sync resource ownership/head-queue state, and ordered-append allocation counters/addresses.

Performance counter data groups include `*_PERFCOUNTER{0..15}_{LO,HI}` style registers for many GC blocks. Most low/high halves are simple full-width `PERFCOUNTER_LO` or `PERFCOUNTER_HI` fields. ATC L2 and MC VM L2 high halves split `COUNTER_HI` from `COMPARE_VALUE`. The final visible selector group, `CPG_PERFCOUNTER1_SELECT`, starts the performance-select block and exposes `CNTR_SEL0`, `CNTR_SEL1`, `SPM_MODE`, and `CNTR_MODE1`; the rest of that select register is outside this chunk.

## Control Flow

There is no control flow in this header. Runtime control flow is created by consumers that combine these masks with GC register offsets and MMIO access helpers:

1. Choose the ASIC-specific offset macro for a GC 9.1 register from the matching offset header.
2. Build a 32-bit value with `REG_SET_FIELD()` or direct `FIELD << REGISTER__FIELD__SHIFT` operations, masked by `REGISTER__FIELD_MASK`.
3. Write the value through AMDGPU accessors such as `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, packet emission paths, or firmware-mediated register paths.
4. Read status or counter registers with `RREG32_SOC15()` or command/query readback and decode fields with `_MASK` tests or `REG_GET_FIELD()`.
5. Branch in driver code based on decoded completion, busy, counter, semaphore, cache, trace, or query status.

Typical driver flows affected by this macro surface include render-target setup, clear-state programming, end-of-pipe events, streamout/statistics queries, CP DMA copies, cache flush/invalidate sequences, indirect-buffer setup, shader thread tracing, GDS/GWS synchronization, and performance monitoring.

## State And Persistence Behavior

This chunk defines bit layouts for hardware state, not software state. The represented state falls into several categories:

- Persistent configuration until rewritten or reset: CB target format/base/metadata layout, DCC behavior, CP coherency action masks, CP DMA control, IB/command-buffer bases and sizes, VGT/IA/WD setup, SQ thread trace mode/masks, SQC cache command bits, SPI configuration, GDS atomic/resource/OA setup, and performance counter selectors.
- Command-like or doorbell-style state: CP DMA commands, coherency requests, semaphore addresses, wait/reg-mem timeouts, thread trace buffer reset, SQC invalidate/writeback requests, and GDS atomic/ordered-append operations.
- Status or readback state: CP completion/fence/query data, primitive/statistics counters, CP coherency status, DMA tags and FIFO state, PFP/CE completion status, SQ thread trace status/write pointer/counter/high-water, SQC completion/dirty state, DB occlusion/zpass counters, GDS write/atomic completion, GWS head/resource state, and perf counter low/high halves.
- Address state: many registers encode GPU addresses split into low/high pieces and often in 256-byte units. Consumers must pair low/high/base-ext registers correctly and must respect address alignment implied by field names such as `BASE_256B`.

Hardware persistence is register-defined. Configuration fields usually survive until reset, suspend/resume reinitialization, ring/queue setup, or a later programming sequence. Status fields are volatile and may change while engines are active. Some status bits are sticky or completion-style and require the corresponding hardware clear or reset sequence rather than ordinary software memory semantics.

## Dependencies And Integration Points

The generated naming convention is the primary API contract. AMDGPU macros concatenate register and field tokens, so a spelling or layout change in this header can break `REG_SET_FIELD(value, REGISTER, FIELD, x)` / `REG_GET_FIELD(value, REGISTER, FIELD)` users even when no C symbol is directly referenced.

Important dependencies and integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`, which provides register addresses for the field layouts in this file. In this tree, `amdgpu/psp_v10_0.c` directly includes the GC 9.1 offset header for PSP register interactions; other generated GC 9.x paths use the same offset-plus-mask pattern.
- SOC15 and AMDGPU register helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, `WREG32()`, `REG_SET_FIELD()`, and `REG_GET_FIELD()`.
- Clear-state and graphics setup tables for GFX generations. This tree has GC color-target clear-state tables in files such as `amdgpu/clearstate_gfx9.h`, where `CB_COLOR1_INFO` through `CB_COLOR7_INFO` and related CB registers are part of the saved/programmed hardware context.
- Command processor packet paths that emit event, DMA, cache, semaphore, query, streamout, draw, dispatch, and IB setup state. Some CP fields may be programmed indirectly by packet commands rather than by CPU MMIO writes.
- Profiling and debug paths that consume SQ thread trace and performance counter registers. The accompanying enum headers, such as `vega10_enum.h`, provide event/token selector values that are written into selector fields defined in generated mask headers.
- Per-instance register selection through `GRBM_GFX_INDEX`. Any code that writes instance-scoped VGT/PA/SQ/SPI/GDS/perf state must select or broadcast the intended shader engine, shader array, and instance before using these bitfields.

The source path is under a `ceph-client` mirror, but the content is AMD GPU driver register metadata. There is no Ceph filesystem logic in this chunk.

## Risks And Edge Cases

- Bitfield mistakes are high impact and low visibility. A wrong shift or mask compiles cleanly but can program the wrong hardware bit, corrupt render-target state, break cache flushes, stall CP DMA, misreport counters, or wedge debug/profiling flows.
- This range starts and ends mid-family. It begins partway through `CB_COLOR1_INFO`, so the complete target-1 color-buffer layout must be reconciled with the previous chunk. It ends after the first fields of `CPG_PERFCOUNTER1_SELECT`, so performance selector coverage is incomplete until later chunks are merged.
- Repeated CB target definitions invite generator or copy/paste drift. `CB_COLOR2_*` through `CB_COLOR7_*` should remain layout-identical where the hardware register families are replicated; a single mismatched mask can affect only one render target and be hard to diagnose.
- Address fields are alignment-sensitive. Many bases are in 256-byte units or have separate extension registers; using byte addresses directly or omitting high/ext pieces can redirect CB metadata, CP event writes, DMA transfers, IBs, or trace buffers.
- Cache and coherency fields are ordering-sensitive. Incorrect `CP_COHER_CNTL` or `CP_ME_COHER_CNTL` action masks can leave CB/DB/TC/SQ caches stale or force unnecessary flushes that hurt performance.
- Status registers are volatile. Polling `CP_COHER_STATUS`, DMA tags/FIFO bits, SQ thread trace status, SQC completion, GDS completion, or perf counters can race with active hardware and needs existing driver synchronization.
- Thread trace and perf counter controls can perturb workloads. Trace stall, interrupt, wrap, autoflush, and performance event masks affect shader execution and profiling data; invalid combinations can produce empty traces, full buffers, or unexpected stalls.
- GDS/GWS/OA and atomic registers are synchronization-sensitive. Misprogrammed resource/head/counter fields can affect queue synchronization, ordered append allocation, or global data store atomics.
- Generation-specific names are not interchangeable. GC 9.0, GC 9.1, GC 9.4.x, GC 10+, and GC 11+ headers have many matching register names but can differ in field availability or bit positions.

## Test And Validation Signals

Useful validation signals for this chunk are:

- Build AMDGPU with GC 9.1/Vega-era support enabled so generated macro names resolve wherever this ASIC's offset and mask headers are consumed.
- Run graphics workloads that bind multiple color targets, use DCC/CMASK/FMASK, fast clears, MSAA, and varied render-target formats. Problems in `CB_COLOR*_INFO`, `ATTRIB`, metadata-base, or clear-word fields tend to show as rendering corruption, bad clears, compression faults, or GPU hangs.
- Exercise CP event/query paths: fences, EOP writes, streamout, primitive statistics, occlusion/zpass queries, and pipeline statistics should complete and return plausible low/high counter values.
- Exercise CP DMA and coherency paths with buffer copies, cache flush/invalidate waits, and VM-visible data synchronization. Failures can appear as stale data, coherency wait timeouts, DMA tag stalls, or ring timeouts.
- Validate indirect-buffer and command-buffer execution under normal graphics and compute submissions. Incorrect IB base/size/offset or preamble fields can show as command processor hangs or malformed packet execution.
- Run shader thread trace/profiling flows and confirm trace buffers fill, wrap/interrupt/full/busy/status bits behave coherently, and token filters produce expected data.
- Run GDS/GWS/OA and atomic-sensitive compute workloads where available, especially queue synchronization and ordered append behavior.
- Compare generated masks mechanically against AMD's authoritative GC 9.1 register database and against neighboring GC 9.x headers, allowing only documented ASIC-version differences.

## Cross-Chunk Notes

This chunk should be merged with adjacent chunks before producing the final per-file research document. The previous chunk is needed for the beginning of `CB_COLOR1_INFO` and likely earlier `CB_COLOR1_*` state. Later chunks are needed for the rest of `gc_perfsdec` performance selector registers and any remaining GC 9.1 register-mask families.

### subset-b-002641: lines 22321-24774

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 22321-24774

## Scope

This chunk is a generated AMD GC 9.1 shift/mask header slice. It contains 2,154 `#define` constants grouped by register-name comments. The range starts inside the `CPG_PERFCOUNTER1_SELECT` field list and ends at `RLC_SRM_INDEX_CNTL_ADDR_0`, so both ends require adjacent chunks for complete register-family coverage. There are no functions, structs, enums, variables, allocation paths, locks, or executable statements here.

The covered register groups are:

- Command-processor performance counter selectors and controls for CPG, CPC, CPF, TC counter windows, latency stats, draw-object tracking, and draw-window masks.
- GRBM global and per-shader-engine busy performance counter selectors.
- Graphics pipeline performance counter selectors for WD, IA, VGT, PA/SU, PA/SC, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, RMI, ATC L2, and MC VM L2.
- RLC streaming performance monitor ring, mux selection, segment sizing, sample-delay, clock-control, and interrupt/memory-control fields.
- RLC core, safe-mode, SMU/RLCV command, timer, load-balancing, clock-gating, power-gating, CU power status, SERDES master mask/busy, GPM scratch/general, interrupt, and save/restore memory command fields.

## Purpose

The purpose of this header segment is to expose the bit layout of GC 9.1 hardware registers to AMDGPU driver code. The paired offset header supplies register addresses; this file supplies the field encodings used to compose or decode 32-bit MMIO register values.

The generated API pattern is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for that field.

Most consumers use these constants through register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, SOC15 MMIO accessors, or local read-modify-write helpers. This chunk is therefore compile-time hardware metadata rather than runtime logic.

## Important Macro Families

### CP, GRBM, And Pipeline Perf Counters

The first half of the chunk is dominated by performance counter selection registers. CP blocks use `CPG_*`, `CPC_*`, and `CPF_*` selector fields such as `CNTR_SEL0..3`, `SPM_MODE`, and `CNTR_MODE0..3`, plus global `CP_PERFMON_CNTL` state and sample-enable bits. `CPF_TC_PERF_COUNTER_WINDOW_SELECT` and `CPG_TC_PERF_COUNTER_WINDOW_SELECT` define index, always, and enable fields for TC performance windows. `CPF_LATENCY_STATS_SELECT`, `CPG_LATENCY_STATS_SELECT`, and `CPC_LATENCY_STATS_SELECT` expose index, clear, and enable controls for latency statistics.

`GRBM_PERFCOUNTER0_SELECT`, `GRBM_PERFCOUNTER1_SELECT`, and `GRBM_SE0_PERFCOUNTER_SELECT` through `GRBM_SE3_PERFCOUNTER_SELECT` select GRBM-level events and user-defined busy/clean masks for blocks such as DB, CB, VGT, TA, SX, SPI, SC, PA, CP, IA, GDS, BCI, RLC, TC, WD, UTCL2, EA, and RMI.

The graphics pipeline selectors include `WD`, `IA`, `VGT`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, `SX`, `GDS`, `TA`, `TD`, `TCP`, `TCC`, `TCA`, `CB`, `DB`, `RLC`, and `RMI` families. Common fields are `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, `SPM_MODE`, `PERF_MODE`, and companion `*_SELECT1` registers. Field widths vary: many blocks use 10-bit selectors, `SQ` uses 9-bit selectors plus `SQC_BANK_MASK`, `SQC_CLIENT_MASK`, and `SIMD_MASK`, while CB and RMI selectors use narrower 9-bit event masks.

Specialized controls include:

- `SPI_PERFCOUNTER_BINS`, which packs four min/max bin ranges.
- `SQ_PERFCOUNTER_CTRL`, with shader-stage enables, per-ME/pipe disable bits, poll-before-read, and shader-engine masking.
- `SQ_PERFCOUNTER_MASK` and `SQ_PERFCOUNTER_CTRL2`, with counter masking and force/VMID filtering.
- `VGT_PERFCOUNTER_SEID_MASK`, which controls shader-engine ID ignore masking.
- `CB_PERFCOUNTER_FILTER`, with operation, format, clear, MRT, sample-count, and fragment-count filters.
- `RMI_PERF_COUNTER_CNTL`, with transaction/event/TC enables, event windows, CID/VMID filters, burst-length threshold, soft reset, and SPM selection.

### UTCL2 And VM L2 Perf Counters

The `gc_utcl2_atcl2pfcntldec` address block defines `ATC_L2_PERFCOUNTER0_CFG`, `ATC_L2_PERFCOUNTER1_CFG`, and `ATC_L2_PERFCOUNTER_RSLT_CNTL`. Each counter config has event start/end selection, mode, enable, and clear fields. The result-control register chooses a counter, defines start/stop triggers, enables any counter, clears all, and can stop all counters on saturation.

The `gc_utcl2_vml2pldec` address block mirrors that shape for `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG` and `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`. These fields support memory-management/L2 performance observation rather than graphics-pipe event selection.

### RLC SPM And Perfmon

The RLC streaming performance monitor section includes:

- `RLC_SPM_PERFMON_CNTL`, with ring mode and sample interval.
- `RLC_SPM_PERFMON_RING_BASE_LO`, `RLC_SPM_PERFMON_RING_BASE_HI`, and `RLC_SPM_PERFMON_RING_SIZE`, which describe the memory ring used for streamed samples.
- `RLC_SPM_PERFMON_SEGMENT_SIZE`, with global and SE line counts.
- `RLC_SPM_SE_MUXSEL_ADDR/DATA` and `RLC_SPM_GLOBAL_MUXSEL_ADDR/DATA`, which expose mux selection RAM windows.
- Per-block `RLC_SPM_*_PERFMON_SAMPLE_DELAY` registers for CPG, CPC, CPF, CB, DB, PA, GDS, IA, SC, TCC, TCA, TCP, TA, TD, VGT, SPI, SQG, SX, and RMI.
- `RLC_SPM_RING_RDPTR`, `RLC_SPM_SEGMENT_THRESHOLD`, `RLC_PERFMON_CLK_CNTL`, `RLC_PERFMON_CNTL`, and `RLC_PERFCOUNTER0/1_SELECT`.
- `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, and `RLC_SPM_INT_STATUS`, which describe SPM memory-client attributes and interrupt state.

The chunk also includes `RLC_GPU_IOV_PERF_CNT_*` fields for virtualization-visible performance counter control, write/read address windows keyed by VFID and counter ID, and 4-bit data values.

### RLC Core, Power, And Save/Restore

The `gc_rlcpdec` block defines RLC control and status fields:

- `RLC_CNTL` enables/steps the F32 RLC core, controls retry, and can disable the read cache.
- `RLC_STAT` exposes RLC, GPM, SPM, SRM, MC, and thread busy bits.
- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `SMU_RLC_RESPONSE`, `RLC_RLCV_COMMAND`, and `RLC_SMU_MESSAGE` define command, message, and response mailboxes among RLC, RLCV, and SMU paths.
- `RLC_REFCLOCK_TIMESTAMP_*`, `RLC_GPU_CLOCK_COUNT_*`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32` describe timestamp and clock-count readback.
- `RLC_GPM_TIMER_INT_0..3`, `RLC_GPM_TIMER_CTRL`, and `RLC_GPM_TIMER_STAT` define RLC GPM timer intervals, enable bits, and status bits.
- `RLC_INT_STAT`, `RLC_FIREWALL_VIOLATION`, `RLC_GPM_STAT`, and `RLC_CU_STATUS` expose interrupt, fault-address, power-management, and work-pending status.
- `RLC_LB_CNTL`, `RLC_LB_CNTR_MAX`, `RLC_LB_CNTR_INIT`, `RLC_LOAD_BALANCE_CNTR`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, `RLC_LB_PARAMS`, and `RLC_THREAD1_DELAY` configure CU load balancing and power-gating heuristics.
- `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_PG_CNTL`, `RLC_PG_DELAY`, `RLC_PG_DELAY_2`, `RLC_PG_DELAY_3`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_PG_ALWAYS_ON_CU_MASK`, `RLC_MAX_PG_CU`, `RLC_AUTO_PG_CTRL`, and `RLC_SMU_GRBM_REG_SAVE_CTRL` cover clock gating, light/deep sleep, power gating, per-CU power status/request masks, and SMU handshakes.

The SERDES and save/restore area includes `RLC_SERDES_RD_MASTER_INDEX`, read data ports, CU/non-CU master write masks, `RLC_SERDES_WR_CTRL`, `RLC_SERDES_WR_DATA`, CU/non-CU busy status, `RLC_GPM_GENERAL_0..7`, `RLC_GPM_SCRATCH_ADDR/DATA`, GPM log and interrupt disable/force registers, and `RLC_SRM_*` ARAM/DRAM/GPM/RLCV command fields. The chunk ends after `RLC_SRM_INDEX_CNTL_ADDR_0`, so the following index-control registers and any remaining SRM fields belong to the next chunk.

## Control Flow

There is no direct control flow in this header. Runtime behavior is supplied by AMDGPU code that includes the generated header and performs MMIO access. Typical flows are:

1. Driver code selects a GC 9.1 register address from the paired offset header.
2. It composes a value by shifting field values by `__SHIFT` and constraining them with `_MASK`, usually through helper macros.
3. It writes the register, or reads a register and decodes fields through the matching mask/shift pair.
4. For status or command-like fields, surrounding driver code handles ordering, polling, timeouts, and reset/suspend sequencing.

Performance-counter flows program selector and mode fields, optionally set filters, VMID/CID masks, bins, sample delays, or SPM muxes, run a workload, then read counters or streamed samples. RLC flows are more stateful: safe-mode entry/exit, SPM ring setup, timer configuration, clock/power-gating control, SERDES commands, SRM transfers, and SMU/RLCV mailboxes require hardware-specific sequencing outside this header.

## State And Persistence Behavior

The macros hold no software state. They describe hardware state that persists in GC registers until reset, power loss, firmware reinitialization, or explicit driver writes.

Performance counter selectors, filters, windows, and SPM modes persist as programmed hardware configuration and directly affect collected profiling data. Counter result-control bits such as clear, enable, start/stop trigger, and saturation behavior are command/configuration fields whose effects depend on hardware state.

RLC SPM state includes memory ring base/size, read pointer, mux selection RAM contents, segment size/threshold, sample delays, memory-client attributes, interrupts, and global/per-block perfmon state. Misprogrammed base addresses or sizes affect DMA-like writes to the SPM ring.

RLC core and power-management fields represent durable control state and live status. Clock-gating, CGCG/CGLS, load-balancing, power-gating, per-CU request/status masks, and SMU handshakes can remain active across workloads. Status registers such as `RLC_STAT`, `RLC_GPM_STAT`, SERDES busy registers, timer status, and SPM interrupt status are live observations that may change asynchronously with firmware and hardware activity.

SRM, SERDES, scratch, and mailbox fields are indirect access windows or command/status registers. Their data registers do not represent ordinary persistent kernel memory; they represent hardware/firmware-visible storage or command FIFOs whose interpretation depends on current RLC/SRM state.

## Dependencies And Integration Points

This chunk depends on the generated AMD register database for GC 9.1 and must stay synchronized with:

- `gc_9_1_offset.h`, which provides register addresses and address-block mappings for the names defined here.
- Adjacent generated headers such as default-value files and other GC 9.1 register namespaces.
- AMDGPU SOC15 register access helpers and bitfield helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.
- GC 9.1 graphics, compute, KFD, profiling, virtualization, clock/power-management, reset, and firmware-control paths that program CP, GRBM, SQ, memory L2, RLC, SPM, and SRM registers.

The path is under a `ceph-client` source mirror, but this file is AMD GPU driver hardware metadata. It has no Ceph protocol behavior, distributed filesystem data path, network persistence, or storage consistency logic.

## Risks And Edge Cases

- These are untyped preprocessor constants. Incorrect masks or shifts can compile cleanly and produce wrong MMIO writes.
- The chunk starts inside `CPG_PERFCOUNTER1_SELECT` and ends inside the RLC SRM index-control area. Whole-file analysis must merge adjacent chunks before making complete claims about those families.
- Repeated performance-counter families look similar but have different selector widths and upper-bit meanings. For example, SQ selectors include SQC/SIMD masks, CB/RMI selectors use narrower event fields, and some pipeline counters only expose a single `PERF_SEL`.
- Selector/mode field swaps can produce plausible but wrong profiling results, which are hard to catch with normal build tests.
- Clear, enable, force, reset, safe-mode command, capture, and interrupt-force bits are not all ordinary persistent settings. Treating command-like bits as passive configuration can cause lost samples, stuck status bits, or firmware sequencing failures.
- RLC SPM ring base/size and mux fields influence hardware writes into memory. Bad values can corrupt profiling buffers or make samples unreadable.
- RLC power and clock fields can affect liveness, power draw, and suspend/resume behavior. Leaving overrides asserted or programming delay/hysteresis fields incorrectly can hide idle state, prevent gating, or destabilize wakeup paths.
- SERDES and SRM windows require busy/FIFO sequencing. Writing command fields without respecting `FIFO_FULL`, `FIFO_EMPTY`, or master busy status can race the firmware/hardware access path.
- Virtualization performance counter fields use VFID and counter IDs. Incorrect programming can attribute data to the wrong virtual function or break PF/VF isolation assumptions.

## Test Signals

Useful validation signals include:

- Build AMDGPU and AMDKFD code paths that include GC 9.1 headers; missing or renamed macros should surface at compile time.
- Compare this generated header against the authoritative GC 9.1 register database and the paired `gc_9_1_offset.h` to catch drift in field masks or register names.
- Exercise performance counter programming on GC 9.1 hardware across CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC/TCA, CB, DB, RLC, RMI, ATC L2, and MC VM L2 blocks. Look for zero, saturated, or misattributed counters.
- Validate SQ counter filtering with SQC bank/client masks, SIMD masks, shader-stage enables, pipe disables, force enable, and VMID filtering.
- Run SPM collection with ring base/size, segment sizing, global/SE mux selection, sample delays, memory-client attributes, interrupts, and ring read-pointer handling.
- Test RLC bring-up, safe mode, SMU/RLCV mailbox responses, timers, clock counters, GPM thread reset, CP DMA completion flags, and interrupt status under normal boot, suspend/resume, reset, and GPU fault recovery.
- Exercise clock-gating and power-gating paths that touch RLC MGCG, CGCG/CGLS, PG control, per-CU dynamic/static masks, SMU handshakes, and load-balance controls while checking for hangs and power telemetry regressions.
- Validate SERDES and SRM command flows with busy/FIFO polling, read/write data ports, scratch access, and ARAM/DRAM command status.

## Cross-Chunk Notes

The previous chunk is required for the full beginning of the CP performance-counter selector area, including the missing start of `CPG_PERFCOUNTER1_SELECT`. The next chunk is required for the remainder of the `RLC_SRM_INDEX_CNTL_*` family and any later GC 9.1 RLC/SRM definitions. The final per-file research document should merge this chunk with `subset-b-002632` through `subset-b-002644` before summarizing the complete `gc_9_1_sh_mask.h` file.

### subset-b-002642: lines 24775-27132

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 24775-27132

## Purpose

This chunk is generated register-field metadata for AMD GC 9.1 graphics-core registers. It contains only preprocessor `#define` constants for bit shifts and masks; it does not define executable code. The slice begins in the `gc_grbmdec` address block, covering RunList Controller (RLC) save/restore, UTCL1, load-balancer, interrupt, and DSM/R2I fields, then crosses into the `gc_pwrdec` address block for shader/compute-unit clock-gating and clock-test controls.

The major purpose is to let AMDGPU code name hardware register fields symbolically when using the driver register helpers. For example, callers can set `RLC_CP_SCHEDULERS.scheduler1` via `REG_SET_FIELD()` instead of hard-coding an 8-bit field at shift 8, and can preserve reserved bits by masking only named fields.

The assigned range contains 175 register comment blocks and 2181 `#define` lines. It starts at `RLC_SRM_INDEX_CNTL_ADDR_1`; the matching `_ADDR_0` block is immediately before this chunk, so merge/reconciliation should treat the `_ADDR_0..7` family as split across chunk boundaries.

## Important APIs, Types, And Data

There are no C functions, structs, classes, or enums. The API surface is the macro naming contract used by the AMD register access layer:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift amount for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for that field.
- Register comments such as `//RLC_SRM_STAT` or `//CGTS_CU4_SP0_CTRL_REG` delimit generated groups.

Important register families in this chunk:

- `RLC_SRM_INDEX_CNTL_ADDR_1..7` and `RLC_SRM_INDEX_CNTL_DATA_0..7`: save/restore-memory indexed address and data windows. Address fields are 16-bit plus reserved upper bits; data windows expose full 32-bit payload fields.
- `RLC_SRM_STAT`, `RLC_SRM_GPM_ABORT`, `RLC_SRM_*_COMMAND_STATUS`: busy, delay, abort, FIFO-empty, and FIFO-full fields used around RLC save/restore commands.
- `RLC_CSIB_ADDR_LO`, `RLC_CSIB_ADDR_HI`, `RLC_CSIB_LENGTH`: command-stream indirect-buffer address/length fields, with the high address field limited to 16 bits.
- `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_1`, `RLC_SMU_ARGUMENT_2`: full-width command and argument fields for RLC-to-SMU command exchange.
- `RLC_CP_SCHEDULERS`: four 8-bit scheduler fields named `scheduler0` through `scheduler3`.
- `RLC_GPM_GENERAL_8..12`: full-width general-purpose RLC GPM data registers.
- `RLC_GPM_UTCL1_CNTL_0..2`, `RLC_SPM_UTCL1_CNTL`, `RLC_PREWALKER_UTCL1_CNTL`: UTCL1 control fields for XNACK redo timer count, drop mode, bypass, invalidate, fragment-limit mode, force-snoop, and VMID-dirty behavior.
- `RLC_UTCL1_STATUS` and `RLC_UTCL1_STATUS_2`: busy and stall-on-transaction status bits for GPM threads, SPM, and prewalker UTCL1 paths.
- `RLC_*_UTCL1_*_ERROR_*`: UTCL1 fault fields, including client ID, faulting VMID, permissions, queue ID, CID, and GCRD client ID.
- `RLC_LB_THR_CONFIG_1..4`, `RLC_R2I_CNTL_0..3`, `RLC_DS_CNTL`, `RLC_DSM_TRIG`, `RLC_LBPW_CU_STAT`: RLC load balancing, response-to-interrupt, depth/stencil, DSM trigger, and load-balance prewalker/CU status fields.
- `RLC_CGCG_CGLS_CTRL_3D` and `RLC_CGCG_RAMP_CTRL_3D`: coarse-grain clock-gating and light-sleep controls for the 3D block, including enable, delay, divider, ramp, wakeup, and override-style fields.
- `RLC_SEMAPHORE_0`, `RLC_SEMAPHORE_1`, `RLC_CP_EOF_INT`, `RLC_CP_EOF_INT_CNT`, `RLC_SPARE_INT`, `RLC_RLCV_SPARE_INT`: synchronization and interrupt flags/counters.
- `CGTS_SM_CTRL_REG`, `CGTS_RD_CTRL_REG`, `CGTS_RD_REG`, `CGTS_TCC_DISABLE`, `CGTS_USER_TCC_DISABLE`: global clock-test/control and TCC-disable fields in the `gc_pwrdec` block.
- `CGTS_CU0..15_*_CTRL_REG`: six repeated compute-unit control register types per CU: `SP0`, `LDS_SQ`, `TA_SQC`, `SP1`, `TD_TCP`, and `TCPI`. These expose 7-bit clock-test values plus override, busy-override, light-sleep-override, and SIMD-busy-override fields for shader processor, LDS, SQ, texture address, SQC, texture data, TCP/TCPF, and TCPI subblocks.
- `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, `CGTT_BCI_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`: clock-gating turn-on delay, turn-off hysteresis, performance-enable, soft-stall override, core override, and register override fields for SPI, primitive/culling, BCI, and VGT blocks.

The CU clock-test pattern is highly regular: every CU index from 0 through 15 appears with the same six register types. Dual-subblock registers generally place the first subblock at bits 0-11 and the second at bits 16-27, leaving upper or intermediate reserved bits outside the named masks.

## Control Flow

The header chunk has no runtime control flow. Its practical control flow is compile-time expansion through AMDGPU macros:

1. A GC-generation-specific implementation includes the appropriate generated offset/mask headers.
2. Runtime code reads a 32-bit hardware register with `RREG32*()` or derives an address through `SOC15_REG_OFFSET()`.
3. Code updates fields with `REG_SET_FIELD()`, `WREG32_FIELD15*()`, or explicit mask operations using the macros in this file.
4. Code writes the result back with `WREG32*()`.

Examples elsewhere in the tree show the same fields being used in that pattern. `gfx_v9_0.c` reads `mmRLC_SRM_CNTL`, sets `RLC_SRM_CNTL__AUTO_INCR_ADDR_MASK`, and later uses `WREG32_FIELD15(..., RLC_SRM_CNTL, SRM_ENABLE, 1)` during RLC setup. MES and KFD code read `regRLC_CP_SCHEDULERS`, update scheduler fields, and write the value back. GC 10 code programs `mmCGTT_VGT_CLK_CTRL` in golden-register tables and direct writes, illustrating how CGTT masks map to clock-gating programming even when a newer generation owns the active implementation.

## State And Persistence Behavior

The macros are stateless compile-time constants. The state they describe is GPU hardware register state:

- RLC save/restore registers hold volatile command, address, data, FIFO, abort, busy, and status state. That state is meaningful during firmware-driven graphics setup, suspend/resume, reset, and power-management transitions.
- RLC UTCL1 status/error fields report live memory-translation/fault status. They should be treated as volatile hardware state, not cached software state.
- RLC interrupt and semaphore fields describe transient signaling between command processor, RLC firmware, and driver paths.
- CGTS/CGTT fields program persistent-until-reset clock-test and clock-gating behavior. They are not persisted by this header; persistence comes from driver init/golden-setting code reprogramming registers after GPU reset or power transitions.

Reserved masks are part of the persistence story: callers must preserve reserved bits on read-modify-write paths because these registers can carry hardware-owned state outside the named fields.

## Dependencies

This chunk depends on the generated GC 9.1 register database remaining synchronized with the hardware specification. It is coupled to:

- `gc_9_1_offset.h`, which provides the register offsets corresponding to these field masks.
- AMDGPU register helpers such as `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `WREG32_FIELD15`.
- ASIC-specific GFX, MES, KFD, PM, and reset code that manipulates RLC, CP scheduler, CGTS, and CGTT registers.
- RLC firmware/SMU protocols for save/restore memory, scheduler setup, and power-gating state.

The only GC 9.1-specific generated files in this directory are `gc_9_1_offset.h` and `gc_9_1_sh_mask.h`; unlike some generations, there is no separate `gc_9_1_d.h` in this tree. The mask names therefore need to line up with offset naming and with the include path selected by the target ASIC code.

## Integration Points

Primary integration points are low-level AMDGPU hardware bring-up and power-management paths:

- RLC initialization and firmware setup use `RLC_SRM_*`, `RLC_SMU_*`, and `RLC_CP_SCHEDULERS` fields to prepare save/restore memory, communicate with the SMU, and assign scheduler positions.
- MES/KFD queue-management code uses `RLC_CP_SCHEDULERS__scheduler*` fields to place or clear scheduler ownership for compute and kernel queues.
- GPU reset, suspend/resume, and power-gating paths depend on the RLC status, UTCL1 status/error, interrupt, and semaphore fields to sequence hardware state safely.
- Golden-register and clock-gating programming use the `CGTS_*` and `CGTT_*` fields to override clocks, force clocks on for diagnostics or safe programming, and tune on/off delays and hysteresis.
- Diagnostics and debug tooling can decode register dumps using these masks to show named field values instead of raw 32-bit words.

Because the chunk crosses from `gc_grbmdec` into `gc_pwrdec`, it sits at an integration boundary between RLC control/status and power/clock-control metadata.

## Risks

- Incorrect mask or shift values can silently program the wrong hardware bit, causing hangs, missed interrupts, bad queue scheduling, broken RLC save/restore, or unstable clock-gating behavior.
- The range starts mid-family at `RLC_SRM_INDEX_CNTL_ADDR_1`; generated-file consumers are fine, but research merging must avoid assuming `_ADDR_1` is the first address register.
- Many CGTS CU blocks are repetitive. Copy/paste or generation errors can be hard to spot because all 16 CUs should have consistent field layouts.
- Clock-gating override fields can affect power, performance, and hardware liveness. Writing broad constants to `CGTT_*` or `CGTS_*` registers without preserving reserved bits is risky.
- UTCL1 control fields such as bypass, invalidate, force snoop, and VMID dirty behavior can affect GPU virtual memory correctness and fault recovery.
- Full-width data/command fields such as `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_*`, and `RLC_GPM_GENERAL_*` provide no field-level guardrails; correctness depends on the higher-level firmware protocol.
- Cross-generation reuse is unsafe. Nearby GC versions often share names but can differ in offsets, extra fields, or reserved-bit layout.

## Test Signals

Useful validation signals for this chunk are mostly build-time, static, and hardware-runtime oriented:

- Build AMDGPU configurations that include GC 9.x generated register masks and exercise `REG_SET_FIELD()`/`WREG32_FIELD15*()` call sites for `RLC_SRM_CNTL` and `RLC_CP_SCHEDULERS`.
- Static comparison against `gc_9_1_offset.h` should confirm every register family in this chunk has a corresponding offset definition and that split families are reconciled with neighboring chunks.
- Static lint can verify that each field mask matches its shift and width, that masks within a register do not overlap unexpectedly, and that reserved masks cover the unnamed bits.
- Hardware smoke tests on GC 9.1 ASICs should cover RLC firmware load, RLC save/restore memory enable, CP scheduler programming, queue creation/destruction, suspend/resume, GPU reset, and memory-fault handling.
- Power-management tests should check that CGCG/CGLS and CGTT/CGTS programming does not regress idle power, wake latency, clock-gating counters, or GPU hang rates.
- Register-dump decoders should decode representative `RLC_UTCL1_STATUS*`, `RLC_*_ERROR_*`, `CGTS_CU*_CTRL_REG`, and `CGTT_*_CLK_CTRL` values consistently with these masks.

### subset-b-002643: lines 27133-29689

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 27133-29689

## Purpose

This chunk is generated AMD GPU register metadata for GC 9.1. It defines bit shifts and masks for several late sections of the graphics-core register map: clock-gating controls, external-access and VM/SR-IOV controls, RLC hypervisor and GPU-IOV registers, clock/activity counter (CAC) programming and accumulators, and shader-queue indirect wave/debug status registers.

The file contains no executable logic. Its purpose is to provide the symbolic field names consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indirect `ix*` register access, and generated golden-register programming tables. The matching offset names live in the adjacent GC 9.1 offset header; this chunk supplies the field layout for those offsets.

The chunk starts in the tail of `CGTT_VGT_CLK_CTRL`, then covers these main groups:

- `CGTT_*_CLK_CTRL`, `*_CGTT_*CLK_CTRL`, `SQ_*_CLK_CTRL`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CB_CGTT_SCLK_CTRL`, `DB_CGTT_CLK_CTRL_0`, `TCC_CGTT_SCLK_CTRL`, `TCA_CGTT_SCLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, and `GCEA_CGTT_CLK_CTRL` clock-gating fields.
- `gc_utcl2_vmsharedhvdec` fields for per-VF framebuffer size/offset, MARC regions, IOMMU enable/performance, PCIe ATS, and UTCL2 clock gating.
- `gc_hypdec` fields for CP/RLC microcode windows, GRBM shadow/cam access, RLC GPU-IOV scheduling/config/status, virtual reset, interrupts, doorbell status, scratch, and SDMA save/restore status.
- `gccacind` and `secacind` CAC selection, override, weighting, and accumulator fields for many graphics sub-blocks.
- `sqind` shader-queue debug and wave-state fields, including `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, and the beginning of `SQ_WAVE_HW_ID`.

## Important APIs, Types, And Data

The API surface is entirely preprocessor constants with the generated naming form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no C functions, structs, or enums in this chunk.

Important field families:

- Clock gating registers use a repeated layout: `ON_DELAY` at low bits, `OFF_HYSTERESIS` in bits 4-11, stall override fields around bits 16-23, and soft/core/register override fields in the high byte. These appear across IA, WD, PA, SC, SQ, SQG, SX, TD, TA, TCPI, TCI, GDS, DB, CB, TCC, TCA, CP/CPF/CPC, RLC, RMI, TCPF, EA, and UTCL2 domains. Variants add domain-specific override names such as `PRIMGEN_OVERRIDE`, `TESS_OVERRIDE`, `GS_OVERRIDE`, `PBB_*`, `PFF_ZFF_MEM_CLK_*`, `TCI_TCC*_CLK_OVERRIDE`, `RBIU_INPUT_OVERRIDE`, `MGLS_OVERRIDE`, or `SPARE`.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` expose small single-purpose disable fields; `SQ_POWER_THROTTLE` and `SQ_POWER_THROTTLE2` expose `MIN_POWER`, `DRAWER`, `FORCE_POWER`, `POWER_GOOD`, `HIGHER`, and `LOWER`.
- VM virtualization fields define `MC_VM_FB_SIZE_OFFSET_VF0` through `VF15` as paired 16-bit `VF_FB_SIZE` and `VF_FB_OFFSET` values, MARC base/relocation/length registers split into low and high halves, `VM_IOMMU_CONTROL_REGISTER__IOMMUEN`, `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER__PERFOPTEN`, and ATS fields `STU` plus `ATC_ENABLE`.
- RLC GPU-IOV fields define command execution and status (`RLC_GPU_IOV_CFG_REG1/2`), active function selection, scheduler block metadata, microcode/scratch address/data windows, timer control/status, virtual function masks, virtual reset requests, interrupt force/disable registers, SDMA preempt/save/restore status bits, and full-width busy/response/status fields.
- CAC fields define selection/control registers (`GC_CAC_CNTL`, `SE_CAC_CNTL`, `*_OVR_SEL`, `*_OVR_VAL`), two-16-bit weight slots per register for block signal weights, 32-bit accumulator fields, and override select/value bit ranges. The block coverage includes BCI, CB, CP, DB, GDS, IA, LDS, PA, PC, SC, SPI, SQ, SX, SXRB, TA, TCC, TCP, TD, VGT, WD, CU, PG, EA, RMI, UTCL2/ATCL2, router, VML2, and walker.
- SQ indirect debug fields describe queue occupancy and wave state. `SQ_DEBUG_STS_GLOBAL*` exposes busy and FIFO/wave levels; `SQ_DEBUG_STS_LOCAL` exposes local busy and wave level; `SQ_WAVE_MODE` covers FP rounding/denorm behavior, DX10 clamp, IEEE mode, exception enables, FP16 overflow, perf disable, GPR indexing, VSKIP, and CSP; `SQ_WAVE_STATUS` covers condition/status bits such as `SCC`, priorities, `PRIV`, trap/thread-trace enable, export readiness, `EXECZ`, `VCCZ`, barrier/halt/trap/valid/ECC/perf/replay/fatal-halt/export flags; `SQ_WAVE_TRAPSTS` covers exception, save-context, illegal instruction, XNACK, DP rate, and exception-cycle fields.

Representative consumers elsewhere in the tree show the intended macro contract. `gfx_v9_0_read_wave_data()` reads `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_HW_ID`, `ixSQ_WAVE_TRAPSTS`, and `ixSQ_WAVE_MODE` through SQ indirect access. PowerPlay tables in `smu7_powertune.c` program `ixGC_CAC_CNTL` entries through `GPU_CONFIGREG_GC_CAC_IND`; the masks in this chunk define how those packed values break down into enable, threshold, block, and signal fields.

## Control Flow

There is no runtime control flow inside this header. The control-flow model is:

1. GC 9.1-specific code includes generated offset and mask headers.
2. Callers read or write a register through SOC15, indexed, or indirect accessors.
3. `REG_SET_FIELD` and `REG_GET_FIELD` use the `__SHIFT` and `_MASK` constants to pack or unpack field values.
4. The hardware block interprets the final 32-bit register value.

For clock-gating fields, runtime code typically writes golden settings during ASIC initialization or power-management transitions. For CAC fields, PowerPlay/DPM tables select hardware signals, enable/disable counters, and program weights/overrides. For SQ wave fields, debug and hang-analysis paths use SQ indirect access to snapshot wave state into driver-visible buffers. For RLC GPU-IOV fields, hypervisor/SR-IOV control paths use command, scheduler, reset, doorbell, interrupt, and status fields as a hardware handshake surface.

## State And Persistence Behavior

The macros are compile-time-only and have no persistence. The hardware registers they describe are stateful and side-effect-bearing:

- Clock-gating controls persist in GPU registers until reset, power-gating, suspend/resume reinitialization, or explicit reprogramming. Incorrect override bits can force clocks on or stall gating.
- VM/IOMMU/ATS/MARC and per-VF framebuffer fields define hardware translation and virtualization state. These settings persist for the active device lifetime and must match the current PF/VF and memory-management configuration.
- RLC GPU-IOV registers carry scheduler state, active function IDs, virtual reset requests, doorbell status, interrupts, microcode/scratch windows, and save/restore status. Some registers are command or set/clear style and should be treated as transactional rather than passive storage.
- CAC accumulators are hardware counters. Weight and override registers affect how activity is counted or modeled; accumulator registers expose volatile telemetry that may reset on hardware reset or explicit CAC control actions.
- SQ debug and wave registers expose volatile execution state for currently selected shader waves. Reads reflect a point-in-time hardware snapshot and can change immediately as waves execute, halt, trap, or drain.

## Dependencies

This chunk depends on the generated GC 9.1 register database remaining synchronized across:

- `gc_9_1_sh_mask.h` for field masks and shifts.
- The matching `gc_9_1_offset.h` names for `mm*`, `reg*`, and `ix*` offsets.
- AMDGPU register helper macros that expand field names into masks/shifts.
- SOC15 block addressing for memory-mapped GC registers.
- Indirect register paths for `gccacind`, `secacind`, `sqind`, and hypervisor/indexed register spaces.
- PowerPlay/DPM tables that program CAC and power-related registers.
- GFX debug and hang-dump code that reads SQ wave registers.
- SR-IOV/hypervisor paths that manage RLC GPU-IOV, VF framebuffer windows, ATS, MARC, and virtual reset state.

The same field names also appear in sibling generated headers for other IP blocks or GC generations, but the exact offsets, field widths, and reserved bits can differ. Consumers must include the GC/IP-version-specific header selected for the ASIC.

## Integration Points

The primary integration point is AMDGPU's generated ASIC register include tree under `drivers/gpu/drm/amd/include/asic_reg/gc/`. Higher-level integration points include:

- GFX initialization and golden-setting tables for clock-gating register programming.
- Runtime power-management code that enables clock gating, CAC activity accounting, and power-throttle behavior.
- PowerPlay/SMU code that writes `GC_CAC_CNTL`, CAC weights, overrides, and accumulators through GC CAC indirect access.
- GPU virtualization/SR-IOV code using RLC GPU-IOV command/status, per-VF masks, active function IDs, doorbell status, virtual reset requests, ATS, IOMMU, and framebuffer partition fields.
- Microcode loading or inspection paths that use CP/RLC microcode address/data windows.
- Debugfs, hang detection, and GPU reset diagnostics that capture SQ wave mode/status/trap/hardware identity through `SQ_IND_INDEX` and `SQ_IND_DATA`.

## Risks

- A wrong shift or mask can silently corrupt unrelated bits in a hardware register; this is especially dangerous for high-bit override fields and reserved-bit regions.
- Cross-generation reuse is risky. GC 9.1 mask definitions should not be assumed valid for other GC versions, even when names look similar.
- Clock-gating override mistakes can cause hangs, excess power draw, broken performance counter behavior, or failure to enter low-power states.
- CAC weight/control mistakes can produce misleading power/activity telemetry or destabilize power tuning if thresholds, block IDs, signal IDs, or override values are packed incorrectly.
- SR-IOV and hypervisor fields are privilege-sensitive. Incorrect VF masks, active function IDs, reset requests, ATS enables, or framebuffer partition fields can affect isolation, device assignment, or recovery paths.
- Set/clear style status registers such as VF doorbell status set/clear and reset/interrupt force controls should not be handled like ordinary read/write fields.
- SQ wave-state reads are debug snapshots, not stable persistent state. Consumers must tolerate races with running waves and avoid interpreting stale or partially drained wave data as a deterministic program state.
- Reserved fields are explicitly named in several registers; writes should preserve documented reserved bits unless the programming sequence is known to require a full-register value.

## Test Signals

Useful validation is mostly compile-time, static, and hardware smoke coverage:

- Build coverage for GC 9.1 AMDGPU code that includes `gc_9_1_sh_mask.h` and uses `REG_SET_FIELD`/`REG_GET_FIELD` with these field names.
- Static consistency checks that each register in this chunk has matching offset definitions in the GC 9.1 offset header and, where applicable, matching default definitions in generated default headers.
- Golden-register table validation that clock-gating masks preserve reserved bits and only set documented override/delay/hysteresis fields.
- Runtime smoke tests on GC 9.1 hardware showing clock-gating initialization, suspend/resume, and GPU reset complete without register-access faults or hangs.
- Power-management tests that enable CAC programming and verify activity counters/weights behave plausibly under idle and graphics/compute load.
- SR-IOV validation that per-VF framebuffer, ATS, RLC GPU-IOV scheduler, doorbell, reset, interrupt, and SDMA save/restore status paths behave correctly for PF and VF contexts.
- GPU hang/debug tests that capture SQ wave dumps and decode `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_MODE`, and `SQ_WAVE_HW_ID` fields without malformed output.

### subset-b-002644: lines 29690-31176

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 29690-31176

## Scope

This chunk is the final portion of the generated AMD GC 9.1 shift/mask header. It starts in the middle of the `SQ_WAVE_HW_ID` bitfield definitions, continues through shader-queue wave debug and interrupt word layouts, then covers the complete `addressBlock: didtind` register-mask area for DIDT/EDC control across several graphics blocks. The chunk ends at the file's closing `#endif`.

The file contains preprocessor constants only. There are no C functions, structs, enums, variables, allocations, locks, callbacks, or executable branches in this range.

## Purpose

The purpose of this header section is to publish the bit-level ABI between AMDGPU/KFD code and GC 9.1 hardware registers. Each field is represented by the generated macro pair:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position for the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field inside a register value.

The corresponding register addresses are supplied by `gc_9_1_offset.h`; this file supplies the field positions for those addresses. Consumers normally combine these macros with AMDGPU helper patterns such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indirect register accessors, and DIDT-specific read/write helpers.

## Important APIs, Types, And Macro Families

The exposed API is the generated macro namespace. Major groups in this chunk are:

- `SQ_WAVE_HW_ID`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_STS`, `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_INST_DW0/DW1`, `SQ_WAVE_IB_DBG0/DBG1`, `SQ_WAVE_FLUSH_IB`, `SQ_WAVE_TTMP0..15`, `SQ_WAVE_M0`, and `SQ_WAVE_EXEC_LO/HI`. These describe the wavefront debug/register-save view: wave/SIMD/pipe/CU/SE identity, VGPR/SGPR/LDS allocation, outstanding instruction-buffer counters, program counter, current instruction dwords, instruction-buffer debug state, temporary trap registers, M0, and EXEC mask halves.
- `SQ_INTERRUPT_WORD_AUTO_CTXID`, `SQ_INTERRUPT_WORD_AUTO_HI/LO`, `SQ_INTERRUPT_WORD_CMN_CTXID`, `SQ_INTERRUPT_WORD_CMN_HI`, `SQ_INTERRUPT_WORD_WAVE_CTXID`, and `SQ_INTERRUPT_WORD_WAVE_HI/LO`. These define how SQ interrupt payloads encode automatic thread-trace/timestamp/overflow events, common SE/encoding fields, and wave-specific data such as shader array, privilege, wave ID, SIMD ID, CU ID, VM ID, SE ID, and interrupt encoding.
- `DIDT_SQ_*`, `DIDT_DB_*`, `DIDT_TD_*`, `DIDT_TCP_*`, and `DIDT_DBR_*`. These repeated families describe dynamic inductive droop throttling controls for the shader queue, depth block, texture data, texture cache pipe, and depth buffer/raster block. Each block exposes a similar set of control, threshold, stall, pattern, weight, EDC, status, overflow, rolling power delta, and event-counter masks.

The DIDT register families are highly regular:

- `*_CTRL0` fields enable/reset DIDT logic, override clocks, enable stall/tuning/auto-release controls, set high-power thresholds, enable automatic MPD, enable stall events, and clear stall event counters.
- `*_CTRL1` and `*_CTRL2` carry min/max power, max power delta, short-term interval size, and long-term interval ratio fields.
- `*_STALL_CTRL`, `*_TUNING_CTRL`, and `*_STALL_AUTO_RELEASE_CTRL` define stall delay, maximum stalls allowed, max-power-delta tuning, and auto-release timing.
- `*_CTRL3` fields enable GC/SE-level DIDT behavior, choose throttle policy, select trigger/power-level low bits, configure stall pattern width, qualify or force stalls, choose stall source, and enable stall delay.
- `*_STALL_PATTERN_1_2` through `*_STALL_PATTERN_7` pack seven 15-bit stall patterns with reserved/unused bits.
- `*_WEIGHT0_3`, `*_WEIGHT4_7`, and `*_WEIGHT8_11` pack 8-bit weights used by the hardware power/throttle estimator.
- `*_EDC_CTRL`, `*_EDC_THRESHOLD`, `*_EDC_STALL_PATTERN_*`, `*_EDC_STATUS`, `*_EDC_STALL_DELAY_*`, `*_EDC_OVERFLOW`, and `*_EDC_ROLLING_POWER_DELTA` define the EDC-side enable/reset/clock/stall policy, thresholds, stall patterns, status, overflow counters, and rolling power delta state.
- `DIDT_*_STALL_EVENT_COUNTER` registers expose full 32-bit stall event counters for SQ, DB, TD, TCP, and DBR.

There are small per-block differences in the repeated DIDT layout. For example, SQ and TD expose three EDC stall-delay registers covering lanes `0..10`, TCP exposes three stall-delay registers covering `0..10`, DB exposes only one EDC stall-delay register, and DBR exposes a single-bit `EDC_STALL_DELAY_DBR0`. These differences matter because the names are similar enough that mechanical cross-block substitution can silently use the wrong mask.

## Control Flow

This chunk has no runtime control flow. Runtime behavior is supplied by the driver or firmware paths that include the matching GC 9.1 register headers:

1. Code selects a register address from `gc_9_1_offset.h` or an indirect register index such as an `ixSQ_WAVE_*` or `ixDIDT_*` register.
2. Code composes or decodes a 32-bit register value with the `__SHIFT` and `_MASK` macros from this header.
3. The actual MMIO or indirect access is performed through AMDGPU/KFD helpers.
4. Hardware, firmware, interrupt handling, or debug code supplies sequencing, polling, reset, and timeout policy.

The macros do not encode access type. A field may be read-only status, write-only command, sticky status, self-clearing command, write-one-to-clear, reserved, or durable configuration depending on the register definition.

## State And Persistence Behavior

This header stores no software state and persists nothing on its own. It describes hardware state in GC 9.1 registers.

The SQ wave fields represent live or captured wavefront state: execution mask, PC, current instruction, GPR/LDS allocation, instruction-buffer counters, replay state, temporary trap registers, and hardware placement. These values are hardware-owned and can change as waves execute, halt, trap, or are sampled through indirect debug paths.

The SQ interrupt word fields describe payload state delivered through interrupt/context ID data. KFD's GFX9 interrupt processing carries matching definitions for `SQ_INTERRUPT_WORD_AUTO_CTXID` and `SQ_INTERRUPT_WORD_WAVE_CTXID` and decodes thread-trace, timestamp, overflow, SE, encoding, wave ID, SIMD ID, CU ID, privilege, and data fields from interrupt payloads.

The DIDT/EDC fields describe hardware throttle and power-estimation state. Control and threshold fields can persist until reset or reprogramming; event counters, overflow counters, EDC status, and rolling power delta are hardware-updated status. Clear/reset bits such as `DIDT_CTRL_RST`, `DIDT_STALL_EVENT_COUNTER_CLEAR`, and `EDC_SW_RST` are command-like and must be sequenced by the owning power-management or hardware initialization code.

Persistence is hardware-defined. GPU reset, suspend/resume, power gating, clock gating, firmware reload, or ASIC-specific initialization may clear or reinitialize these registers. The header itself does not say which fields must be restored after a power transition.

## Dependencies And Integration Points

The direct generated-header dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`, which provides the corresponding register offsets and indirect register indices. Related generated headers such as GC 9.1 defaults/enums, where present, provide reset values or symbolic field values.

Observed and implied integration points in this source tree include:

- `amdgpu/gfx_v9_0.c`, whose wave debug dump path reads registers such as `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, `ixSQ_WAVE_HW_ID`, `ixSQ_WAVE_INST_DW0`, `ixSQ_WAVE_INST_DW1`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_DBG0`, and `ixSQ_WAVE_M0`.
- `amdkfd/kfd_int_process_v9.c`, which carries equivalent SQ interrupt word definitions and uses `REG_GET_FIELD` to decode GFX9 SQ interrupt messages for auto, instruction, and error encodings.
- KFD CWSR/trap-handler assembly for GFX9, which relies on SQ wave allocation/status/trap/IB-status bit positions when saving and restoring wave state.
- Power-management and ASIC bring-up paths that program DIDT/EDC controls through `ixDIDT_*` registers and DIDT-specific accessors. Similar DIDT masks are used by older legacy/powerplay code, and GC 9.1 has ASIC-specific layouts that must be paired with the matching offset/mask header.
- Debug/profiling paths that expose wave state, SQ interrupt payloads, DIDT event counters, and EDC status for diagnostics.

Although this repository subtree is under `sources/distributed-fs/ceph-client`, this file is AMD GPU driver hardware metadata and has no relationship to Ceph filesystem logic.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. Pairing `gc_9_1_sh_mask.h` with another GC generation's offset header can compile while reading or writing the wrong hardware fields.
- The chunk starts mid-register at `SQ_WAVE_HW_ID`; adjacent chunk context is needed for the first few `SQ_WAVE_HW_ID` shift definitions. The merged per-file report should join this with the previous chunk.
- SQ wave state is live and indirect. Reading wave registers while a wave is running, halted, trapped, or being context-saved can produce inconsistent snapshots unless the caller follows the GFX debug sequencing rules.
- Interrupt word layouts are generation-sensitive. GFX9, GFX10, GFX11, and GFX12 use similar names but not identical payload packing. Reusing the wrong `SQ_INTERRUPT_WORD_*` layout can misclassify thread-trace, timestamp, overflow, wave, SIMD, CU, VMID, or encoding fields.
- DIDT/EDC programming affects power, throttling, and stall behavior. Wrong thresholds, stall patterns, weights, throttle policy, or force-stall bits can cause performance cliffs, thermal/power instability, hangs, or misleading event counters.
- Repeated DIDT families invite copy/paste errors. SQ, DB, TD, TCP, and DBR mostly share field names, but delay-register count and field widths differ in places.
- Reserved and `UNUSED_*` fields are explicitly present. Read-modify-write users must preserve bits unless ASIC documentation says otherwise.
- Full-width masks such as `0xFFFFFFFFL` appear for data, counters, PC/instruction words, and rolling power delta. Full-width does not imply safe arbitrary writes; some are readback/status or hardware-owned data windows.
- EDC status/overflow fields can be sticky or live hardware state. Tests that only check register writes may miss failures where counters never advance, overflow unexpectedly, or throttle state never clears.

## Test And Validation Signals

Useful validation is mostly build, static, and hardware coverage:

- Build coverage for AMDGPU, KFD, PSP, and power-management paths that include the GC 9.1 offset/mask headers.
- Generated-header consistency checks that each field has a matching shift/mask pair, masks align to shifts, and register names match `gc_9_1_offset.h`.
- Static checks for non-overlapping fields inside each register, except full-width data registers and documented aliases.
- GFX9 wave debug tests that halt or sample waves and verify PC, EXEC, HW_ID, instruction dwords, GPR/LDS allocation, IB status, IB debug, and M0 fields decode plausibly.
- KFD SQ interrupt tests that trigger thread trace, timestamp, overflow, instruction, and wave/error interrupts and verify `SQ_INTERRUPT_WORD_*` decoding against known context ID payloads.
- CWSR/trap save/restore tests on GFX9 workloads, especially around SGPR/VGPR/LDS allocation and replay/status fields that depend on SQ wave bit positions.
- Power-management validation that enables/disables DIDT and EDC, applies known thresholds/patterns/weights, clears stall counters, and confirms throttle/status/event-counter behavior under controlled graphics and compute loads.
- Reset, suspend/resume, runtime power-management, and GPU recovery tests while DIDT/EDC or wave debugging is active, because these registers are hardware-owned and may need reinitialization after power transitions.
