# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002685`: lines 1-2410, `Docs/researches/chunks/subset-b-002685_research.md`
- `subset-b-002686`: lines 2411-4805, `Docs/researches/chunks/subset-b-002686_research.md`
- `subset-b-002687`: lines 4806-7180, `Docs/researches/chunks/subset-b-002687_research.md`
- `subset-b-002688`: lines 7181-9540, `Docs/researches/chunks/subset-b-002688_research.md`
- `subset-b-002689`: lines 9541-11973, `Docs/researches/chunks/subset-b-002689_research.md`
- `subset-b-002690`: lines 11974-14503, `Docs/researches/chunks/subset-b-002690_research.md`
- `subset-b-002691`: lines 14504-16929, `Docs/researches/chunks/subset-b-002691_research.md`
- `subset-b-002692`: lines 16930-19506, `Docs/researches/chunks/subset-b-002692_research.md`
- `subset-b-002693`: lines 19507-21915, `Docs/researches/chunks/subset-b-002693_research.md`
- `subset-b-002694`: lines 21916-24636, `Docs/researches/chunks/subset-b-002694_research.md`
- `subset-b-002695`: lines 24637-27087, `Docs/researches/chunks/subset-b-002695_research.md`
- `subset-b-002696`: lines 27088-29458, `Docs/researches/chunks/subset-b-002696_research.md`
- `subset-b-002697`: lines 29459-31649, `Docs/researches/chunks/subset-b-002697_research.md`

## Chunk Research

### subset-b-002685: lines 1-2410

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 1-2410

## Purpose

This chunk is the opening generated register field mask/shift header for AMD GC 9.4.3 graphics-core registers. It starts the include guard for `gc_9_4_3_sh_mask.h` and defines 2,172 preprocessor constants for 204 register blocks through line 2410.

The chunk covers these address blocks:

- `xcd0_gc_grbmdec`: graphics register bus manager status, error reporting, soft reset, trap, scratch, RSMU, IOV, fence, UTCL2 invalidation, and power-control field definitions.
- `xcd0_gc_cpdec`: command processor, CPF, CPC, MEC, queue, ring-buffer, read/write pointer, stalled/busy status, interrupt-debug, debug-bus, and privilege-violation field definitions.
- `xcd0_gc_padec`: primitive assembler, VGT, IA, WD, PA/SC/CL/SU, binning/event, UTCL1, shader-array, primitive config, and front-end pipeline tuning fields.
- The beginning of `xcd0_gc_sqdec`: SQ, SQC, LDS, SH memory, shader-rate, debug, interrupt, UTCL1, cache, clock-gating, timeout, and MFMA configuration fields.

The final line of the chunk is intentionally mid-register: line 2410 ends at `SQ_UTCL1_CNTL2__SHOOTDOWN_OPT_MASK`; the remaining `SQ_UTCL1_CNTL2` masks and later SQ fields are outside this work item.

## Important APIs, Types, And Data

This header defines no functions, structs, enums, global variables, or storage. Its public API is a generated preprocessor namespace with two constants per hardware field:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift amount for extracting or inserting the field.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.

Important groups in this chunk include:

- GRBM status and control macros such as `GRBM_STATUS__GUI_ACTIVE_MASK`, `GRBM_STATUS2__CPAXI_BUSY_MASK`, `GRBM_SOFT_RESET__SOFT_RESET_*_MASK`, `GRBM_READ_ERROR*`, `GRBM_WRITE_ERROR`, `GRBM_IOV_ERROR`, `GRBM_RSMU_READ_ERROR`, and `GRBM_GFX_CNTL` queue-selection fields.
- CP/CPC/CPF/MEC macros for scheduler and queue observability: `CP_CPC_STATUS`, `CP_CPC_BUSY_STAT`, `CP_CPC_STALLED_STAT1`, `CP_CPF_STATUS`, `CP_CPF_BUSY_STAT`, `CP_STALLED_STAT1/2/3`, `CP_BUSY_STAT`, `CP_STAT`, `CP_GRBM_FREE_COUNT`, ring/queue availability and pointer fields, command-index/data fields, interrupt debug bits, and ME/MEC halt, step, reset, and icache invalidation bits.
- PA/VGT/WD/IA front-end macros for primitive flow and raster/binning behavior: `VGT_CACHE_INVALIDATION`, `VGT_DMA_CONTROL`, `VGT_CNTL_STATUS`, `IA_CNTL_STATUS`, `WD_CNTL_STATUS`, `PA_CL_ENHANCE`, `PA_SC_BINNER_EVENT_CNTL_0` through `_3`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_ENHANCE_2`, FIFO sizing, and UTCL1 invalidation/control fields.
- SQ/SQC/LDS/SH macros for shader core behavior: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_DSM_CNTL*`, `SQ_DEBUG_STS_GLOBAL*`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SH_CAC_CONFIG`, `SQ_TIMEOUT_CONFIG/STATUS`, shader-rate configuration, interrupt controls, and `SQ_UTCL1_CNTL1` plus the first part of `SQ_UTCL1_CNTL2`.

These constants are normally used with AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, masked register writes, and debug register dumps. The companion `gc_9_4_3_offset.h` supplies register addresses; this file supplies field placement inside each 32-bit register.

## Control Flow

There is no executable control flow. Compile-time inclusion makes symbolic field layouts available to C code that reads or writes GC 9.4.3 registers.

Runtime flow is created by consumers. Typical patterns are:

- Read a register via MMIO or indexed register access, then extract a field with the matching mask and shift.
- Build a new register value by clearing a mask and inserting a shifted field value.
- Poll busy/status bits from `GRBM_STATUS*`, `CP_*_STATUS`, `IA_CNTL_STATUS`, `VGT_CNTL_STATUS`, `WD_CNTL_STATUS`, or `SQ_DEBUG_STS_GLOBAL*` before reset, suspend, mode changes, or fault handling.
- Write reset, halt, invalidate, queue-threshold, timeout, binning, or UTCL1 control bits during initialization, bring-up, debug, or recovery paths.

Since this is register metadata, branch behavior and sequencing requirements live in callers and hardware documentation, not in the header itself.

## State And Persistence Behavior

The macros are stateless compile-time constants. They describe volatile GPU hardware state:

- Status and busy fields reflect live hardware state and can change between reads.
- Reset, halt, invalidate, bypass, force-miss, clock-gating, timeout, and debug fields are control state held in hardware registers until overwritten, reset, or lost through power/reset transitions.
- Error registers such as GRBM read/write/IOV/RSMU error fields and UTCL1 fault/retry/PRT status fields expose latched or sampled hardware fault state depending on the register semantics enforced by the hardware block.
- Scratch and dump fields (`GRBM_SCRATCH_REG*`, `CP_*_HEADER_DUMP`, command data, and related debug fields) are register-backed diagnostic state, not file-system or software persistence.
- Queue, ROQ, STQ, MEQ, CEQ, ring pointer, FIFO, and credit fields expose transient command processor occupancy and flow-control state.

No persistent on-disk state, firmware blob management, or software cache is implemented here.

## Dependencies

The chunk depends on generated AMD ASIC register metadata being synchronized with GC 9.4.3 hardware:

- `gc_9_4_3_offset.h` provides the register offsets for these field definitions.
- AMDGPU's register manipulation helpers consume the `*_SHIFT` and `*_MASK` naming convention.
- Driver code under `drivers/gpu/drm/amd/` must include the GC 9.4.3 headers only for compatible ASICs; similar register names in other GC generations can have different field layouts.
- Hardware/firmware initialization code, reset paths, power-management code, queue scheduling, GPUVM invalidation, and diagnostics rely on these masks matching the silicon.

The header has no direct include dependencies in this chunk beyond its own include guard, but incorrect generation or stale synchronization with the offset/default headers would break consumers at compile time or, worse, misprogram hardware at runtime.

## Integration Points

Primary integration points are AMDGPU's GC 9.4.3 support paths:

- GPU reset and idle-detection paths using GRBM busy, clean, active, read/write-error, and soft-reset masks.
- Command processor bring-up, halt/step/debug, queue setup, and recovery code using CP, CPF, CPC, MEC, ring-buffer, ROQ/STQ/MEQ/CEQ, stalled-stat, and interrupt-debug masks.
- Graphics front-end initialization and diagnostics using VGT, IA, WD, PA/CL/SC/SU, primitive config, shader-array config, binning-event, FIFO, and UTCL1 masks.
- Shader-core initialization, debug, ECC/error-injection, timeout, cache, memory-base/config, interrupt, performance-trap, and UTCL1 invalidation paths using SQ/SQC/LDS/SH masks.
- Debugfs, register dump, fault decoding, and bring-up scripts that decode raw register values into named fields.

The source path places this file in the distributed Ceph client's vendored Linux AMDGPU tree. It is not Ceph filesystem logic itself; it is low-level GPU driver register metadata carried by that source tree.

## Risks

- A wrong mask or shift can silently corrupt unrelated bits in a hardware register, which is especially dangerous for reset, halt, invalidate, clock-gating, memory-translation, and privilege/error registers.
- Cross-generation reuse is unsafe. GC 9.4.3 names overlap with other `gc_*_sh_mask.h` files, but field widths and positions may differ.
- The chunk boundary splits `SQ_UTCL1_CNTL2`; analysis or generated consumers must not assume line 2410 contains the complete register definition.
- Many status bits are transient. Poll loops that read GRBM, CP, PA/VGT, or SQ status must handle races, timeouts, and hardware blocks entering or leaving busy state between reads.
- Debug, DSM, error-injection, force-miss, force-snoop, bypass, and clock-gating fields can significantly alter execution behavior or performance if written outside controlled bring-up/debug flows.
- Reserved and spare fields appear in several registers. Callers should preserve unknown bits unless hardware documentation explicitly requires a value.
- Error and fault fields include VF/VMID/VFID/TMZ/privilege information; incorrect decoding can misattribute virtualization or memory-protection failures.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage of AMDGPU GC 9.4.3 code that includes `gc_9_4_3_sh_mask.h` alongside `gc_9_4_3_offset.h`.
- Static checks that every field in lines 1-2410 has a paired `SHIFT` and `MASK`, except where the chunk boundary intentionally cuts off the rest of `SQ_UTCL1_CNTL2`.
- Cross-header consistency checks against generated offset/default headers and neighboring GC 9.4.x headers for expected register families.
- Runtime smoke tests on matching GC 9.4.3 hardware that exercise GPU reset, command submission, queue setup, suspend/resume, GPUVM invalidation, and fault reporting without invalid-register or timeout errors.
- Register dump or debugfs checks that decode GRBM/CP/PA/SQ busy and fault bits into plausible names under idle and load.
- Fault-injection or recovery tests that verify GRBM read/write errors, CP privilege violations, UTCL1 fault/retry/PRT status, timeout status, and CP interrupt-debug bits decode correctly.

### subset-b-002686: lines 2411-4805

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 2411-4805

## Scope

This chunk covers a generated AMD GC 9.4.3 shader/register mask header range. It contains 2,180 `#define` macros under 213 register comment anchors. The slice starts in the mask half of `SQ_UTCL1_CNTL2`, continues through SQ, SQC, LDS, SP0/SP1, and SPI shader-pipeline definitions, enters the `xcd0_gc_shsdec` address block at `SX_DEBUG_BUSY`, and ends one line before the final `SPI_CSQ_WF_ACTIVE_COUNT_5__EVENTS_MASK` macro.

The file is not executable code. Its public surface is a collection of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` preprocessor constants used with matching register-offset definitions and SOC15/MMIO access helpers elsewhere in AMDGPU and KFD code.

## Purpose

`gc_9_4_3_sh_mask.h` supplies compile-time bit positions and masks for AMD GC 9.4.3 graphics-core registers. This range focuses on shader front-end, shader core, shader cache, trace, ECC/EDC, and shader processor interpolator state:

- SQ UTCL1 status/control, FED interrupt status, clock-gating/test configuration, trap base/mask addresses, debug/timestamp/host-trap state, indirect register windows, and shader commands.
- SQ instruction-format decode words for DS, EXP, FLAT, GLBL, MIMG, MTBUF, MUBUF, scratch, SMEM, SOP, VINTRP, VOP, DPP, SDWA, and MFMA encodings.
- SQ resource descriptor words for buffers, images, samplers, flat scratch, and M0/GPR-index metadata.
- SQC DSM/error-injection controls, SQC EDC counters, SQC instruction/data UTCL1 controls and status, and SQC UE/CE error report words.
- SQ/LDS/SP0/SP1 UE and CE error status words, including address validity, memory IDs, ECC/parity/other flags, counters, poison flags, and reserved high bits.
- Thread trace token layouts for event, instruction, issue, misc, performance, register, timestamp, wave, and wave-start records.
- SPI/SX shader-pipeline controls for debug busy state, DSM/error injection, EDC, per-stage UE/CE status, PS CU enablement, wavefront lifetime warning/status, load-balancer counters, GDS credits, SX export/scoreboard sizing, and initial CSQ active-count fields.

The constants let driver, debug, firmware-support, and diagnostic code compose and decode 32-bit hardware register values without embedding raw bit numbers.

## Important API Surface

- `SQ_UTCL1_CNTL2` starts this chunk with only the tail masks for `FORCE_SNOOP`, `FORCE_GPUVM_INV_ACK`, `RETRY_TIMER`, `FORCE_FRAG_2M_TO_64K`, and `PREFETCH_PAGE`; the matching shifts and earlier fields are in the previous chunk.
- `SQ_UTCL1_STATUS` exposes `FAULT_DETECTED`, `RETRY_DETECTED`, and `PRT_DETECTED` bits plus reserved/unused masks. `gfx_v9_4_3.c` includes this header and lists `regSQ_UTCL1_STATUS` among GC fault/status registers.
- `SQ_FED_INTERRUPT_STATUS` describes front-end dispatch interrupt attribution by SIMD, wave, CU, and VM ID, with disable bits for RSMU, IH, and FED halt routing.
- `SQ_SHADER_TBA_{LO,HI}` and `SQ_SHADER_TMA_{LO,HI}` split shader trap base and trap memory addresses across low 32-bit and high 8-bit fields.
- `SQC_DSM_CNTL`, `SQC_DSM_CNTLA/B`, `SQC_DSM_CNTL2`, `SQC_DSM_CNTL2A/B/E`, and `SPI_DSM_CNTL/2` describe design-for-test/error-injection selectors for instruction/data tag RAMs, miss FIFOs, bank RAMs, dirty bits, UTCL1 LFIFOs, SPI PC RAM, and parameter/position/color caches.
- `SQ_DEBUG`, `SQ_DEBUG_FOR_INTERNAL_CTRL`, `SQ_PERF_SNAPSHOT_CTRL`, `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, `SQ_HOSTTRAP_STATUS`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_CMD`, `SQ_TIME_HI`, and `SQ_TIME_LO` are control/status access surfaces for shader debug, snapshots, timestamps, traps, indirect indexing, and wave commands.
- `SQ_CONFIG1` is a dense shader-core behavior and clock-gating override register. Its fields disable or override MGCG/FGCG behavior across IBUF, PERF, EXP, scalar/vector paths, SP cores, MACC blocks, VALU co-execution, VGPR collapse/read skipping, barrier memory-violation handling, and XNACK retry checks.
- The `SQ_DS_*`, `SQ_EXP_*`, `SQ_FLAT_*`, `SQ_GLBL_*`, `SQ_INST`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SCRATCH_*`, `SQ_SMEM_*`, `SQ_SOP*`, `SQ_VINTRP`, `SQ_VOP*`, `SQ_VOP_DPP`, and `SQ_VOP_SDWA*` groups are bitfield layouts for shader instruction words. They expose operand register fields, opcodes, modifiers, clamp/negation/absolute flags, cache controls, address/data operands, and encoding bits.
- `SQ_THREAD_TRACE_WORD_*` groups define trace-record token parsing: token type, time deltas, shader/CU/SIMD/wave attribution, event types, instruction issue slots, register operations, timestamps, program counters, user data, wave-state bits, and performance counters.
- `SQ_BUF_RSRC_WORD*`, `SQ_IMG_RSRC_WORD*`, and `SQ_IMG_SAMP_WORD*` expose resource descriptor layouts such as base address, stride, swizzle, numeric/data formats, destination selection, compression/write-combine/coherency flags, texture dimensions, mip/filter settings, anisotropy, border-color metadata, and PRT-related sampler behavior.
- `SQC_ICACHE_UTCL1_CNTL{1,2}`, `SQC_DCACHE_UTCL1_CNTL{1,2}`, `SQC_ICACHE_UTCL1_STATUS`, and `SQC_DCACHE_UTCL1_STATUS` describe instruction/data cache UTCL1 VM behavior: L2 response size, GPUVM 64K defaults, permission/response/fault modes, client IDs, invalidation VMID and toggle fields, force-miss/in-order controls, FIFO/cache reductions, snoop/invalidation acknowledgement, perf-event selection, and fault/retry/PRT status.
- `SQC_UE_EDC_*`, `SQC_CE_EDC_*`, `SQ_*_ERR_STATUS_*`, `LDS_*_ERR_STATUS_*`, `SP0_*_ERR_STATUS_*`, `SP1_*_ERR_STATUS_*`, and `SPI_*_ERR_STATUS_*` define common low/high error-report layouts for uncorrectable and correctable errors.
- `SPI_WF_LIFETIME_CNTL`, `SPI_WF_LIFETIME_LIMIT_0` through `_9`, `SPI_WF_LIFETIME_STATUS_0` through `_20`, and `SPI_WF_LIFETIME_DEBUG` define wavefront lifetime monitoring, warning enablement, count limits, interrupt-sent status, and debug start-value override.
- `SPI_LB_CTR_CTRL`, `SPI_LB_CU_MASK`, `SPI_LB_DATA_REG`, `SPI_PG_ENABLE_STATIC_CU_MASK`, `SPI_GDS_CREDITS`, `SPI_SX_EXPORT_BUFFER_SIZES`, `SPI_SX_SCOREBOARD_BUFFER_SIZES`, `SPI_CSQ_WF_ACTIVE_STATUS`, and partial `SPI_CSQ_WF_ACTIVE_COUNT_0` through `_5` define shader-pipeline load-balancer, CU mask, GDS credit, export/scoreboard, and command-sequencer wavefront activity fields.

There are no structs, enums, functions, or inline helpers in this chunk. The API is entirely macro names and numeric shift/mask values.

## Control Flow

There is no direct C control flow in the header. Runtime flow happens in consumers:

1. Select a GC 9.4.3 register offset from `gc_9_4_3_offset.h` or related generated address headers.
2. Compose a 32-bit value by shifting a field value with `REGISTER__FIELD__SHIFT`.
3. Clear, preserve, or extract fields with `REGISTER__FIELD_MASK`.
4. Read or write the register through AMDGPU SOC15 register accessors, KFD queue-management paths, golden-register setup, debug dumps, interrupt/fault handlers, or firmware-support code.

The repeated families imply table-driven or indexed handling. Instruction and resource descriptor words are parsed as fixed layouts; EDC/error status registers are decoded as low/high pairs across SQC, SQ, LDS, SP0, SP1, and SPI; wavefront lifetime status registers are naturally iterated by status index; CSQ active-count registers are iterated by counter number, with this chunk ending in the middle of counter 5.

## State and Persistence

The macros are stateless build artifacts, but the hardware registers they describe are persistent GPU state until changed by driver programming, firmware, context setup, debug tooling, power-management transitions, reset, suspend/resume, or hardware event updates.

UTCL1 controls affect VM translation and cache invalidation behavior for SQ and SQC instruction/data cache clients. Fields such as response/fault mode, client ID, invalidation VMID/toggle, forced snooping, force-miss, FIFO/cache-depth reductions, and 2M-to-64K fragmentation can persist and change fault visibility, cache behavior, or retry timing.

Debug, trap, timestamp, indirect-index, command, and thread-trace fields are synchronization or diagnostic state. Incorrect values can misdirect trap handlers, target the wrong wave/SIMD/CU/VMID, decode trace streams incorrectly, or leave indirect access windows pointing at unintended registers.

Instruction-format and resource descriptor masks describe state stored in shader binaries, debug/trace packets, descriptors, or captured dumps rather than ordinary MMIO configuration alone. Bad bit definitions can cause disassemblers, diagnostics, or queue/debug tooling to interpret operands, opcodes, descriptors, or sampler state incorrectly.

DSM and error-injection controls persist as test and fault-injection state for internal memories and FIFOs. EDC counters and UE/CE status words persist as hardware-updated diagnostic state until cleared by the relevant hardware sequence. Wavefront lifetime and load-balancer counters likewise represent live hardware counters/status and can be affected by clear-on-read, reset, or load control fields.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.4.3 register database. These masks must match companion offset/default headers such as `drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h`.
- Included by GC 9.4.3 AMDGPU and KFD code, including `amdgpu/gfx_v9_4_3.c`, `amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, `amdkfd/kfd_device_queue_manager_v9.c`, and `amdgpu/gfxhub_v1_2.c`.
- Integrated with SOC15/MMIO register access, GPU fault/status register lists, KFD queue and VM setup, shader debug/trap handling, register dumps, and firmware or golden-register programming paths.
- Ties into GPUVM fault diagnostics through `SQ_UTCL1_STATUS`, `SQC_{I,D}CACHE_UTCL1_STATUS`, SQC UTCL1 control fields, and the SQC/SQ/LDS/SP/SPI error status families.
- Ties into shader ISA tooling and debug/trace paths through the many `SQ_*` instruction-word, resource-word, sampler-word, and `SQ_THREAD_TRACE_WORD_*` layouts.
- Ties into reliability and test flows through SQC/SPI DSM controls, EDC counters, UE/CE status registers, FUE controls, lifetime monitors, and load-balancer counters.
- Uses plain C preprocessor constants only. Consumers are responsible for range validation, reserved-bit preservation, register-address selection, sequencing, locking, and hardware generation checks.

## Risks

- Generated bitfield drift is the central risk. If a mask or shift diverges from the GC 9.4.3 hardware specification or companion offset/default headers, callers silently program or decode the wrong bits.
- The chunk starts and ends on partial registers. `SQ_UTCL1_CNTL2` is missing its shift definitions and earlier masks from the previous chunk, and `SPI_CSQ_WF_ACTIVE_COUNT_5` is missing `EVENTS_MASK` from the next line. Merge tooling must not treat either boundary as a complete register-family view.
- Reserved and unused masks are present but not enforced. Read/modify/write code must preserve reserved bits unless hardware documentation says otherwise.
- SQ/SQC UTCL1 fields are sensitive. Bad invalidation VMID/toggle, client ID, force-miss, response/fault mode, snoop, retry, or fragmentation settings can hide VM faults, create false fault attribution, or destabilize shader cache traffic.
- Shader command/debug fields can target specific waves, SIMDs, queues, and VMIDs. Incorrect `SQ_CMD`, trap address, host-trap, indirect-index, or timestamp handling can affect the wrong executing wave or corrupt debug state.
- Instruction and descriptor layouts are copy/paste prone because many encodings share names like `OP`, `ENCODING`, `ADDR`, `DATA`, `VDST`, `SRSRC`, and cache-control fields with different bit widths. A decoder using the wrong family can produce plausible but incorrect output.
- DSM/error-injection and EDC fields can intentionally perturb internal RAMs/FIFOs or report persistent fault state. Accidentally enabling injection or failing to clear/interpret counters can create misleading reliability signals.
- Repeated UE/CE low/high status layouts across SQC, SQ, LDS, SP0, SP1, and SPI have small naming differences such as `MEM_ID` versus `MEMORY_ID`, `STATUS_VALID_FLAG` versus `ERR_STATUS_VALID_FLAG`, and `POSION` versus `POISON`; consumers should avoid string-based assumptions.
- Wavefront lifetime and load-balancer counter controls include warning, interrupt-sent, reset, clear-on-read, and load fields. Incorrect sequencing can lose diagnostic counts or produce spurious warning interrupts.

## Test Signals

- Build coverage: compiling AMDGPU/KFD with this generated header catches syntax errors, duplicate definitions, and missing include dependencies.
- Generation validation: compare lines 2411-4805 against the GC 9.4.3 register source/spec and companion `gc_9_4_3_offset.h` to verify each `__SHIFT` has the expected `_MASK`, width, and register association, while accounting for the two partial boundary registers.
- Fault/status decode validation: exercise GPUVM fault, retry/XNACK, PRT, and cache-invalidation paths and decode `SQ_UTCL1_STATUS`, `SQC_ICACHE_UTCL1_STATUS`, `SQC_DCACHE_UTCL1_STATUS`, and related UTCL1 controls with these masks.
- Reliability diagnostics: inject or simulate SQC/SPI/SQ/LDS/SP UE/CE conditions where supported and confirm low/high status fields, counters, address validity, memory IDs, poison flags, ECC/parity flags, and FUE interrupt enables decode as expected.
- Shader debug and trace validation: capture known-good SQ thread-trace streams, timestamps, traps, and command/debug register dumps and verify token, wave, CU, SIMD, PC, user-data, register-operation, and performance-counter fields.
- ISA/descriptor decode validation: use known GC 9.4.3 shader instruction words and resource descriptors to verify the `SQ_*` instruction, buffer/image resource, sampler, flat scratch, and M0/GPR index masks.
- Power/performance smoke tests: run workloads that exercise shader clock-gating overrides, wavefront lifetime warnings, SPI load-balancer counters, GDS credits, and SX export/scoreboard sizing while checking for hangs, unexpected interrupts, lost counters, or performance regressions.
- Register-dump validation: decode representative dumps for `SQ_CONFIG1`, `SQ_CMD`, `SQC_DSM_*`, `SQC_*_UTCL1_*`, `SQ_THREAD_TRACE_WORD_*`, `SQ_*_ERR_STATUS_*`, `SPI_WF_LIFETIME_*`, `SPI_LB_*`, and `SPI_CSQ_WF_ACTIVE_*` to catch field-width or mask drift.

### subset-b-002687: lines 4806-7180

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 4806-7180

## Purpose

This chunk is a generated AMD GC 9.4.3 shader/register field mask header segment. It exports C preprocessor constants for bit positions and 32-bit masks used by AMDGPU code when composing, updating, and decoding graphics-core registers. The declarations are hardware contract data rather than executable code: each register field is represented with `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros.

The covered range starts in the tail of the SPI block, then defines field masks for `xcd0_gc_tpdec`, `xcd0_gc_gdsdec`, `xcd0_gc_rbdec`, and the beginning of `xcd0_gc_ea_gceadec`. These blocks cover shader processor interface counters/trap-screen bases, texture data/address controls, global data share configuration and error reporting, depth/color render-backend controls and tiling configuration, and graphics cache/external-arbitration read/write priority mapping.

## Major Register Areas Covered

The opening SPI tail completes live wave/counter and trap-screen metadata. `SPI_CSQ_WF_ACTIVE_COUNT_6` and `_7` expose `COUNT` and `EVENTS` fields for command-stream queue wavefront activity counters. `SPI_LB_DATA_WAVES` and the `SPI_LB_DATA_PERCU_WAVE_*` registers expose packed per-stage live wave counts for HSGS, VSPS, and CS. `SPIS_DEBUG_READ` and `BCI_DEBUG_READ` are full-width or low-width debug data reads. The `SPI_P0_*` and `SPI_P1_*` trap-screen registers define low/high memory base fields for PSBA/PSMA and minimum VGPR/SGPR fields, giving debug or trap handling code generation-specific masks for program trap-screen memory and register thresholds.

The `xcd0_gc_tpdec` section defines TD and TA controls. `TD_CNTL`, `TD_STATUS`, and `TD_POWER_CNTL` include synchronization phase, CAC/chicken bits, LDS stall tuning, power throttle disable, round-to-zero, signed-format disable, SRAM/clock-gating related fields, busy status, and medium-grain clock-gating controls. TD and TA both define correctable and uncorrectable EDC status registers with common low/high layouts: status/address valid flags, error address, memory id, ECC/parity or other error type, detailed error info, event counters, FED counters, and poison bits for correctable paths. `TD_DSM_CNTL`, `TD_DSM_CNTL2`, `TA_DSM_CNTL`, and `TA_DSM_CNTL2` expose data-pattern, single-write, error-injection, delay-selection, and injection-delay masks for FIFO/RAM diagnostic self-test paths.

The TA half of `xcd0_gc_tpdec` covers texture address block behavior. `TA_POWER_CNTL` controls clock enable modes for input, LOD, and WDP logic. `TA_CNTL` exports credit fields for FX/SQ XNACK, TC data, aligner, and TD FIFO paths. `TA_CNTL_AUX` includes swizzle, texture fault override, gather4 behavior, and determinism-disable bits for specific opcode/sample/writeop/format cases. `TA_FEATURE_CNTL` exposes atomic coalescing and several FIFO/chicken fields. `TA_STATUS` reports PFIFO empty state and block busy state for input, FG, TA, FA, AL, and aggregate busy.

The `xcd0_gc_gdsdec` section defines global data share controls, status, fault registers, EDC counters, and diagnostic injection masks. `GDS_CONFIG` includes write-disable and per-shader-array GPR phase selection. `GDS_CNTL_STATUS` reports GDS, GRBM buffer, DS, GWS, order FIFO, conflict/clamp, and eight credit-busy bits. `GDS_PROTECTION_FAULT` and `GDS_VM_PROTECTION_FAULT` encode fault detection, write-disable, GRBM/GWS/OA/TMZ indicators, shader/CU/SIMD/wave or VMID information, and fault address fields. EDC-related registers include total GDS memory SEC/DED counts, GRBM SEC/DED counts, OA DED status by ME/pipe, OA physical and pipe SEC/DED counters, and low/high UE/CE error status records. `GDS_DSM_CNTL`, `GDS_DSM_CNTL2`, and `GDS_WD_GDS_CSB` support diagnostic irritator data selection, single-write enable, error injection, delay selection, and watchdog/counter fields across GDS memory, input queue, physical command/data RAM, and pipe memory.

The `xcd0_gc_rbdec` section is the largest part of the chunk. `DB_DEBUG` through `DB_DEBUG4` expose many depth-buffer debug, performance, workaround, coherency, cache, compression, fast-Z/stencil, pre-Z/post-Z, viewport, synchronization, and clock/power-related switches. `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_SUBTILE_CONTROL`, cacheline/FIFO depth registers, exception/ring controls, RMI cache policy, DFSM configuration/watermarks/watchdog/flush controls, and DFSM counters describe backend pipeline capacity and scheduling behavior. Many of these fields are "debug" or "chicken" bits that may be programmed only for bring-up, workarounds, or hardware tuning.

The same `xcd0_gc_rbdec` block also defines render-backend and graphics-buffer topology data. `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GC_USER_RB_REDUNDANCY`, and `GC_USER_RB_BACKEND_DISABLE` encode failed/disabled backend masks and redundancy enable fields. `GB_ADDR_CONFIG` and `GB_ADDR_CONFIG_READ` expose tile/split/pipe/bank/rb/hash/interleave/PRT/screen-index layout fields. `GB_BACKEND_MAP`, `GB_GPU_ID`, and `CC_RB_DAISY_CHAIN` describe backend mapping, GPU id, and per-backend daisy-chain state. `GB_TILE_MODE0` through `GB_TILE_MODE31` repeat a compact tiling layout definition with fields such as micro tile mode, array mode, pipe config, tile split, sample split, bank dimensions/height, and macro tile aspect. `GB_MACROTILE_MODE0` through `_15` provide bank width/height, macro tile aspect, and number-of-banks fields. These masks are central to surface layout interpretation and must match the paired offset/register-definition headers.

The color buffer controls appear near the end of the render-backend section. `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, and `CB_HW_CONTROL_3` expose blend/resolve/write-mask optimizations, CM/FC/CC/DC cache and FIFO sizing, read latency FIFO depths, arbitration assumptions, overwrite-combiner behavior, shader blend optimizations, nack/early-write-ack controls, blender clock gating, target-mask validation, and color cache prefetch count. `CB_HW_MEM_ARBITER_RD` and `_WR` define read/write arbiter modes, urgency age handling, group-age breaks, per-client weights, decay behavior, age/weight scaling, and "send lasts" handling. `CB_DCC_CONFIG` defines DCC overwrite-combiner depth/disable fields, constant encode disable, keyid/read-return FIFO depths, DCC cache eviction point, and DCC cache tag count.

The `xcd0_gc_ea_gceadec` section begins external arbitration/cache routing for DRAM and IO clients. `GCEA_DRAM_RD_CLI2GRP_MAP0/1` and `GCEA_DRAM_WR_CLI2GRP_MAP0/1` map client IDs 0-31 into four priority/groups using two-bit fields. `GCEA_DRAM_RD_GRP2VC_MAP` and `_WR_GRP2VC_MAP` map each group to a virtual channel. `GCEA_DRAM_RD_LAZY` and `_WR_LAZY` tune group delays, request accumulation thresholds, timeouts, and idle maxima. `GCEA_DRAM_RD_CAM_CNTL` and `_WR_CAM_CNTL` define CAM entry limits, GMI thresholds, hold-off timers, and same-group all-timer fields. Burst, priority aging, queuing, fixed priority, urgency, and priority quantum registers then define how DRAM requests are ordered. The chunk continues into IO arbitration with `GCEA_IO_RD/WR_CLI2GRP_MAP*`, combine/flush timers, group burst limits, and the beginning of IO read/write priority aging. The last register in this chunk, `GCEA_IO_WR_PRI_AGE`, is incomplete here; its masks continue in the next file chunk.

## Important APIs, Types, and Functions

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface is the macro namespace itself:

- `*_SHIFT` constants define the least-significant bit offset for a hardware register field.
- `*_MASK` constants define the field's occupied bits in a 32-bit register value.
- Register comments such as `//TD_CNTL` and address block comments such as `// addressBlock: xcd0_gc_gdsdec` provide generated grouping metadata for readers and tooling.

AMDGPU code normally consumes these macros through register helper macros such as field set/get helpers and read/modify/write paths, paired with neighboring headers that define register offsets and possibly defaults. The macro names are therefore an internal hardware ABI for GC 9.4.3 driver code: renaming or changing a constant affects any token-pasting helper or direct bitwise expression that references it.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time inclusion:

1. A GC 9.4.3-specific AMDGPU source file includes generated register offset and mask headers.
2. Driver code selects the correct `REGISTER__FIELD__SHIFT` or `REGISTER__FIELD_MASK` constant for a register field.
3. The compiler folds the constants into MMIO, indirect-register, diagnostic decode, or register value construction code.
4. Hardware behavior changes only when the including driver code performs the actual register read or write.

The register groups imply external driver flows. Trap/debug paths can read SPI live-wave counters and program trap-screen bases. GPU initialization or workaround code can program TD/TA controls, clocks, credits, determinism, and chicken bits. Error-handling code can decode TD/TA/GDS EDC status and fault registers. Render-backend initialization programs topology, backend disables, tiling modes, DCC, cache/FIFO sizing, and arbitration. Performance or QoS tuning code can program GCEA client-to-group, group-to-VC, priority, urgency, lazy accumulation, and quantum fields.

## State and Persistence Behavior

The file itself stores no state and has no persistence behavior. All state described by these masks lives in GPU hardware registers.

The represented hardware state includes live SPI wave counters, trap-screen base addresses, TD/TA busy and power/clock controls, XNACK and FIFO credits, deterministic texture-addressing switches, EDC status/counters, diagnostic injection selectors, GDS protection fault records, DB/CB/GB backend configuration, tiling and macrotile modes, color/depth cache and FIFO sizing, render-backend disable/redundancy masks, and GCEA arbitration policy.

Persistence depends on hardware reset and driver lifecycle rather than this header. Values written using these masks may persist until GPU reset, driver reinitialization, suspend/resume restore, power-gating reset, or later register programming. Status and error fields may be latched, clear-on-read, write-one-to-clear, or otherwise side-effectful depending on the register; this generated mask header does not encode access type, reset value, locking, ordering, or side-effect semantics.

## Dependencies and Integration Points

This header depends only on the C preprocessor and the file-level include guard from the complete header. In practice it must be synchronized with AMD's generated register database and adjacent GC 9.4.3 headers that provide register offsets/base indices. Numeric masks in this file are meaningful only when paired with the correct generation, register address, and access path.

Primary integration points include:

- AMDGPU GC 9.4.3 initialization and workaround code for TD/TA, DB, CB, GB, GDS, and GCEA registers.
- Debug and hang-diagnosis paths that read SPI live wave counters, TD/TA/GDS/DB busy bits, and protection-fault or EDC status.
- RAS/error-handling paths that decode correctable/uncorrectable ECC, parity, poison, memory id, error address, and FED/counter fields.
- Render-backend topology and harvest handling that uses backend disable, redundancy, daisy-chain, GPU id, tile mode, macrotile mode, and address configuration fields.
- Surface layout and memory-management code that depends on `GB_ADDR_CONFIG*`, `GB_TILE_MODE*`, and `GB_MACROTILE_MODE*` values matching the actual ASIC.
- Performance, QoS, and memory-traffic tuning paths that program CB memory arbiters and GCEA DRAM/IO grouping, priority, urgency, quantum, lazy accumulation, and combine/flush behavior.

## Risks and Edge Cases

The main risk is definition drift from the GC 9.4.3 hardware specification. A wrong shift or mask can silently program the wrong bit, decode the wrong error field, misconfigure tiling, or corrupt arbitration policy without producing a compiler error.

Specific risks in this chunk include:

- The section starts and ends at chunk boundaries inside larger register families. The first SPI context was defined before line 4806, and `GCEA_IO_WR_PRI_AGE` is incomplete at line 7180, so consumers of this research should reconcile adjacent chunks before treating those families as complete.
- Repeated families such as `GB_TILE_MODE0-31`, `GB_MACROTILE_MODE0-15`, `GCEA_*_CLI2GRP_MAP0/1`, and read/write priority register pairs are vulnerable to generator or copy-pattern errors that are hard to review manually.
- Several fields are named `RESERVED`, `UNUSED`, `CHICKEN`, or `DEBUG`; callers must not assume these are safe for normal runtime programming just because masks exist.
- Status/error/fault registers and diagnostic injection controls may have side effects or privileged access constraints not represented here.
- Backend disable, redundancy, tile mode, macrotile mode, and address config masks are high blast-radius constants: incorrect values can break surface layout, memory addressing, harvest handling, or render backend routing.
- Arbitration and priority fields in CB/GCEA can affect fairness, latency, and deadlock-avoidance behavior. A wrong two-bit group mapping or priority quantum can cause workload-specific performance regressions rather than immediate failures.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0x80000000L` require callers to use unsigned/fixed-width register values and avoid sign-extension surprises in helper code.

## Test Signals

Useful validation signals are mostly compile-time, generated-data, and hardware-behavior checks:

- GC 9.4.3 AMDGPU builds should compile without missing or duplicate macro definitions after including this header with the matching offset headers.
- Static/generated validation should compare every `*_SHIFT` and `*_MASK` pair in this chunk against AMD's authoritative register database for GC 9.4.3.
- Field helper tests or compile-time assertions can verify representative set/get round trips for packed fields such as GCEA client groups, GDS fault VMID/address, TD/TA EDC counters, GB tile mode fields, and CB arbiter weights.
- Hardware bring-up on GC 9.4.3 devices should confirm TD/TA/GDS EDC injection and status decode paths report the expected memory id, address, ECC/parity, CE/UE, FED, and poison fields.
- Render-backend tests should cover backend harvesting/redundancy, tile/macrotile programming, DCC behavior, depth/stencil compression, fast clear, and surface layout correctness across color/depth formats.
- Hang and fault diagnostics should verify that SPI live-wave counters, TA/TD/GDS/DB busy bits, and GDS protection faults decode consistently with firmware traces or known fault-injection scenarios.
- Performance and QoS testing should watch for regressions after any GCEA or CB arbitration changes, especially read/write fairness, DRAM/IO virtual-channel mapping, urgency handling, lazy request accumulation, and priority quantum behavior.

### subset-b-002688: lines 7181-9540

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 7181-9540

## Scope

This chunk covers generated shift and mask definitions from the GC 9.4.3 AMD GPU register mask header. It starts inside the `GCEA_IO_WR_PRI_AGE` family, continues through GCEA arbitration, SDP, MAM, DSM, probe, performance counter, and error-status fields, then covers RMI control/status fields, ATC L2 fields, VM L2 fault/cache fields, and ends in the UTCL2/VML2 correctable-error status families at `UTCL2_CE_ERR_STATUS_HI`.

The chunk contains preprocessor constants only. In this range there are 2,182 `#define` entries across 164 register groups: 1,090 `__SHIFT` constants and 1,092 `_MASK` constants. It does not define C functions, structs, variables, storage, or executable control flow.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU driver code and GC 9.4.3 hardware registers. Each field is represented by the generated convention:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask that isolates the field in a register value.

Driver code combines these constants with register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and `SOC15_REG_OFFSET`. The sibling `gc_9_4_3_offset.h` header supplies the register addresses; this file supplies the field layout for those addresses.

## Important Macro Families

### GCEA priority, arbitration, SDP, and performance fields

The first part of the chunk is dominated by Graphics Core EA (`GCEA_*`) fields:

- IO read/write priority aging, queuing, fixed-priority, urgency, urgency masking, and quantized-priority threshold fields. These encode group coefficients, group thresholds, and per-client-ID masks for up to 32 CIDs.
- `GCEA_SDP_ARB_DRAM`, `GCEA_SDP_ARB_FINAL`, `GCEA_SDP_DRAM_PRIORITY`, `GCEA_SDP_IO_PRIORITY`, `GCEA_SDP_CREDITS`, tag reserve, VCC reserve, VCD reserve, request-control, enable, and backdoor credit fields. These describe arbitration and credit allocation between DRAM, GMI, IO, return, command, and data paths.
- `GCEA_MISC` and `GCEA_MISC2`, with debug, arbitration, clock, interrupt, switch, bypass, and error-reporting knobs.
- `GCEA_LATENCY_SAMPLING`, `GCEA_PERFCOUNTER_LO/HI`, `GCEA_PERFCOUNTER0_CFG`, `GCEA_PERFCOUNTER1_CFG`, and `GCEA_PERFCOUNTER_RSLT_CNTL`, which expose local sampling and performance-counter selection, mode, enable, clear, trigger, and result-control fields.
- `GCEA_MAM_CTRL` and `GCEA_MAM_CTRL2`, covering ADRAM/ARAM modes, flush controls, ALOG activity/filtering, SDP priority, client ID, address high bits, and MAM disable behavior.

These fields are used to tune or observe GPU memory fabric behavior. Many are low-level hardware scheduler controls rather than normal user-facing policy.

### GCEA DSM and ECC/error-status support

The DSM families `GCEA_DSM_CNTL`, `GCEA_DSM_CNTLA`, `GCEA_DSM_CNTLB`, `GCEA_DSM_CNTL2`, `GCEA_DSM_CNTL2A`, and `GCEA_DSM_CNTL2B` define diagnostic single-write, irritator-data, error-injection, inject-delay, and inject-delay-select fields for DRAM, GMI, IO, return-tag, page memory, and MAM data/address memories.

The GCEA error-status groups include:

- `GCEA_UE_ERR_STATUS_LO/HI`, with valid flags, address, memory ID, ECC/parity indicators, error info, uncorrectable error count, FED count, and reserved bits.
- `GCEA_CE_ERR_STATUS_LO/HI`, with similar low/high address, memory ID, ECC/other indicators, correctable error count, poison, and reserved bits.
- `GCEA_ERR_STATUS`, `GCEA_PROBE_CNTL`, and `GCEA_PROBE_MAP`, which expose additional probe and error-status surfaces.

These macros are integration points for RAS, diagnostics, and validation code. Writes to DSM control fields can deliberately inject or alter error behavior and therefore must be guarded by the owning debug/RAS path.

### RMI control, status, xbar, TCIW, and scoreboard fields

The chunk next covers the RMI address block. Important groups include:

- `RMI_GENERAL_CNTL`, `RMI_GENERAL_CNTL1`, and `RMI_GENERAL_STATUS`, describing global control and status for RMI busy/error conditions, skid FIFO over/underflow, xbar, UTCL1, scoreboard, TCIW formatter, write/read request FIFO, UTC probe, XNACK, and FIFO occupancy flags.
- `RMI_SUBBLOCK_STATUS0..3`, exposing probe FIFO, TCIW inflight, skid FIFO free-space, PRT FIFO occupancy, and aggregate free-space fields.
- `RMI_XBAR_CONFIG`, `RMI_XBAR_ARBITER_CONFIG`, and `RMI_XBAR_ARBITER_CONFIG_1`, which configure crossbar muxing, xbar input enables, arbiter mode, stalls, break-on-idle/weighted-round-robin behavior, stall timer start values, and round-robin weights for RB0/RB1 read/write traffic.
- `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, and `RMI_DEMUX_CNTL`, covering probe FIFO depth, XNACK timers, UTCL1 permission mode, CP VMID reset disable, demux arbitration, and demux stall timers.
- `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, `RMI_UTC_UNIT_CONFIG`, `RMI_UTCL1_STATUS`, and `RMI_XNACK_DEBUG`, describing UTCL1 response modes, GPUVM defaults, invalidation toggles, forced miss/order/snoop/ack behavior, EDC disable, shootdown options, perf-event filters, TMZ request enablement, status, and XNACK debug fields.
- `RMI_TCIW_FORMATTER0_CNTL` and `RMI_TCIW_FORMATTER1_CNTL`, with write-combine disable/timeout, max inflight request, skid FIFO delta update, safe mode, reorder disable, last-of-burst behavior, and all-fault return-data controls.
- `RMI_SCOREBOARD_CNTL` and `RMI_SCOREBOARD_STATUS0..2`, which expose completion flush controls, VMID invalidation override/force behavior, session IDs, invalidation progress/done state, running/snapshot counters, underflow/overflow indicators, and timestamp/completion flush state.
- `RMI_CLOCK_CNTRL` and `RMI_SPARE*`, which provide dynamic clock busy/wakeup masks and spare override/debug fields.

These fields sit near memory translation, request routing, and VMID invalidation handling. Misprogramming them can affect ordering, invalidation completion, fault return behavior, and fabric-level deadlock risk.

### ATC L2 cache, DSM, power, clock, and error fields

The `ATC_L2_*` register families define address-translation cache L2 behavior:

- `ATC_L2_CNTL`, `ATC_L2_CNTL2`, `ATC_L2_CNTL3`, and `ATC_L2_CNTL4`, covering cache enable/fragment-processing style controls, status, invalidation, update behavior, request shaping, associativity/effective size, force-miss bits, and additional control fields.
- `ATC_L2_CACHE_DATA0..3`, `ATC_L2_CACHE_4K_DSM_INDEX`, `ATC_L2_CACHE_32K_DSM_INDEX`, `ATC_L2_CACHE_2M_DSM_INDEX`, and matching `*_DSM_CNTL` registers, which define diagnostic scan/access fields for cache data and DSM controls.
- `ATC_L2_STATUS` and `ATC_L2_STATUS2`, for busy and status reporting.
- `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL`, which expose clock-gating and memory power/light-sleep controls.
- `ATC_L2_MM_GROUP_RT_CLASSES`, which maps memory-management groups to real-time classes.
- `ATC_L2_UE_ERR_STATUS_LO/HI` and `ATC_L2_CE_ERR_STATUS_LO/HI`, which mirror the UE/CE error-reporting layout used by other memory blocks: valid/address flags, address, memory ID, ECC/parity/other indicators, error info, counters, poison, FED, and reserved fields.

### VM L2 cache, protection fault, identity aperture, and bank-selection fields

The `VM_L2_*` portion is one of the key driver-facing parts of this chunk:

- `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_CNTL4`, and `VM_L2_CNTL5` define VM L2 cache enablement, fragment processing, endian swap modes, LRU update behavior, default-page behavior, split modes, queue sizes, PDE fault classification, context-1 identity access mode, identity fragment size, PTE address mode, L1/L2 invalidation controls, cache update mode, bank selection, effective sizes, force-miss bits, MM IFIFO limits, BPM/clock-gating overrides, and walker fetch MTYPE/noalloc enablement.
- `VM_L2_STATUS` exposes L2 busy state, per-context-domain busy bits, and PTE/PDE parity-error indicators.
- `VM_DUMMY_PAGE_FAULT_CNTL` and `VM_DUMMY_PAGE_FAULT_ADDR_LO32/HI32` define dummy page fault enablement and comparison address fields.
- `VM_L2_PROTECTION_FAULT_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL2`, `VM_L2_PROTECTION_FAULT_MM_CNTL3`, and `VM_L2_PROTECTION_FAULT_MM_CNTL4` configure which fault classes produce status updates or interrupts, including range, PDE0/1/2, translate-further, NACK, dummy-page, valid, read, write, execute, no-retry client ID, retry fault, active page migration PTE, and VML1 read/write client masks.
- `VM_L2_PROTECTION_FAULT_STATUS` decodes fault state: more faults, walker error, permission fault class, mapping error, client ID, read/write, atomic, VMID, VF, VFID, UCE, and FED.
- `VM_L2_PROTECTION_FAULT_ADDR_*` and `VM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` expose faulting logical page address and default physical page address halves.
- `VM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*` define the identity aperture and physical offset used for context-1 identity mappings.
- `VM_L2_MM_GROUP_RT_CLASSES`, `VM_L2_BANK_SELECT_RESERVED_CID`, and `VM_L2_BANK_SELECT_RESERVED_CID2` provide group real-time class bits and reserved read/write client-ID bank-selection controls.
- `VM_L2_CACHE_PARITY_CNTL`, `VM_L2_CGTT_CLK_CTRL`, and `VM_L2_CGTT_BUSY_CTRL` define parity handling and clock-gating busy/wakeup behavior.

This family is central to page-table cache behavior, TLB/cache invalidation, VM fault reporting, and SR-IOV-aware fault attribution.

### VML2, VML2 walker, and UTCL2 ECC/EDC fields

The tail of the chunk defines ECC and EDC control/status for VM L2, the VM L2 walker, and UTCL2:

- `VML2_MEM_ECC_INDEX`, `VML2_WALKER_MEM_ECC_INDEX`, and `UTCL2_MEM_ECC_INDEX` select the memory instance or index for ECC controls.
- `VML2_MEM_ECC_CNTL`, `VML2_WALKER_MEM_ECC_CNTL`, and `UTCL2_MEM_ECC_CNTL` define inject delay, DSM irritator data, single-write enable, error-injection enable, delay selection, SEC/DED counters, write-counters strobe, and test-FUE flags.
- `VML2_MEM_ECC_STATUS`, `VML2_WALKER_MEM_ECC_STATUS`, and `UTCL2_MEM_ECC_STATUS` expose UCE and FED status bits.
- `UTCL2_EDC_MODE` and `UTCL2_EDC_CONFIG` define force-SEC-on-DED, FED counting, FUE gating, DED mode, FED propagation, bypass, write disable, and EDC disable behavior.
- `VML2_UE_ERR_STATUS_*`, `VML2_WALKER_UE_ERR_STATUS_*`, `UTCL2_UE_ERR_STATUS_*`, `VML2_CE_ERR_STATUS_*`, `VML2_WALKER_CE_ERR_STATUS_*`, and `UTCL2_CE_ERR_STATUS_*` expose uncorrectable and correctable error detail fields. The low registers carry valid/address flags, address, and memory ID. The high registers carry ECC/parity/other indicators, valid error-info, error-info payload, UE/CE count, FED count or poison, and reserved bits.

These fields are RAS-oriented and are tightly coupled to the hardware error collection and injection flows.

## Control Flow and State Behavior

This header has no executable control flow. Its influence is compile-time: C code includes the header and uses the constants to compose, read, and decode 32-bit MMIO register values.

The state represented by this chunk is hardware state, not software persistence inside the header. Important state surfaces include priority/arbitration policy, SDP credits, performance counter configuration/results, MAM/ALOG configuration, DSM error-injection controls, GCEA/ATC/VML2/UTCL2 error status, RMI FIFOs and xbar/scoreboard status, UTCL1 invalidation and XNACK controls, ATC L2 cache and DSM state, VM L2 cache/invalidation/fault status, identity aperture registers, and ECC/EDC control/status.

Some fields are durable configuration bits, some are latched or sticky status bits, and some are command/strobe-like fields. Examples include cache invalidation bits in `VM_L2_CNTL2`, protection-fault clear/update controls in `VM_L2_PROTECTION_FAULT_CNTL`, DSM error-injection enable and write-counter bits, RMI invalidation toggles, scoreboard flush controls, and clock-gating/busy mask fields. Correct use depends on the owning driver sequence and hardware spec; the generated macros do not encode polling, ordering, locking, or timeout policy.

## Dependencies and Integration Points

This chunk depends on the AMD generated register-header convention:

- `gc_9_4_3_offset.h` provides register address names for the field names defined here.
- Other generated GC 9.4.3 headers, especially defaults and registers under `include/asic_reg/gc/`, provide reset values and related register metadata.
- AMDGPU register helpers consume the `__SHIFT` and `_MASK` definitions through `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask/shift expressions, and SOC15 read/write helpers.

Concrete include points in this tree include `amdgpu/gfxhub_v1_2.c`, `amdgpu/gfx_v9_4_3.c`, `amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, and `amdkfd/kfd_device_queue_manager_v9.c`, all of which include GC 9.4.3 offset/mask headers for this ASIC generation.

Observed cross-file integration for the VM fault fields includes `amdgpu/gmc_v9_0.c`, which decodes `VM_L2_PROTECTION_FAULT_STATUS` with `REG_GET_FIELD` for fields such as `CID`, `RW`, `FED`, `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, and `MAPPING_ERROR`. GC 9.4.3-specific gfxhub and KFD paths use the same field/header pattern when configuring VM, queue, and fault behavior for this generation.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated hardware fields, causing bad VM fault attribution, cache invalidation failures, hangs, incorrect RAS reporting, or silent performance/debug misconfiguration.
- The file is generated and repetitive. Similar-looking priority, DSM, ECC, and status families have small layout differences, so hand edits or mechanical regeneration mistakes are hard to review by eye.
- GCEA and SDP arbitration/credit fields affect memory fabric scheduling. Incorrect values can starve traffic classes or distort performance measurements.
- DSM and ECC injection controls can intentionally create hardware error conditions. They must stay confined to RAS/debug validation flows.
- RMI and UTCL1 controls are close to VM invalidation, XNACK, request routing, and scoreboard completion. Incorrect sequencing can produce stale translations, false completion, FIFO pressure, or deadlock-prone routing behavior.
- VM L2 fault control and status fields are driver-visible diagnostics. If these masks are wrong, logs may report the wrong client, VMID, VF/VFID, access type, or fault class, making recovery and isolation unreliable.
- Cache, parity, clock-gating, and power fields must match hardware topology and firmware policy. Treating debug or clock-gating masks as ordinary runtime knobs can destabilize bring-up, suspend/resume, reset, or SR-IOV operation.
- The chunk starts after the first `GCEA_IO_RD_PRI_AGE` definitions and continues from the preceding chunk's register family. A merged per-file report should connect this document with neighboring chunks for the complete GCEA priority family.

## Test and Validation Signals

Useful validation is mostly integration-oriented:

- Build AMDGPU and KFD code paths that include `gc/gc_9_4_3_sh_mask.h`; this catches missing, renamed, or syntactically malformed macros.
- Exercise GC 9.4.3 VM fault handling and confirm `VM_L2_PROTECTION_FAULT_STATUS` logs decode CID, RW, VMID, VF/VFID, FED/UCE, permission, mapping, walker, and more-fault fields correctly.
- Run GPU reset, suspend/resume, and VM cache invalidation tests to cover `VM_L2_CNTL*`, `VM_L2_STATUS`, RMI scoreboard, and UTCL1 invalidation-related fields.
- Run KFD queue and GPUVM workloads on GC 9.4.3 hardware to stress RMI request routing, VMID invalidation, XNACK, and protection-fault paths.
- Run RAS validation for GCEA, ATC L2, VML2, VML2 walker, and UTCL2 UE/CE/ECC/EDC fields, including controlled error injection where supported.
- Run performance/debug tests that configure GCEA performance counters and latency sampling, verifying counter selection, enable/clear, result-control, and trigger fields.
- For SR-IOV or partitioned deployments, validate that VM fault attribution and RMI/VM L2 behavior remain correct for VF/VFID and reserved-client-ID bank-selection fields.

### subset-b-002689: lines 9541-11973

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 9541-11973

## Scope

This chunk covers the GC 9.4.3 shift/mask definitions from the tail of `UTCL2_CE_ERR_STATUS_HI` through the beginning of `TCC_CTRL2`. It is generated hardware-description data, not executable C logic. The definitions describe bit positions and bit masks for several GC address blocks:

- `xcd0_gc_utcl2_vml2vcdec`: VM context control registers, VMID context-disable bits, VM invalidation engines, invalidation ACKs, invalidation address ranges, and per-context page-table base/start/end addresses.
- `xcd0_gc_utcl2_vmsharedpfdec`: VM shared memory-controller aperture, PCI, power, HBM, XGMI local-frame-buffer, steering, and clock-gating controls.
- `xcd0_gc_utcl2_vmsharedvcdec`: framebuffer, AGP, system aperture, and L1 TLB controls.
- `xcd0_gc_utcl2_l2tlbdec`: L2 TLB status and GPUVA/VMID translation-assist request/response fields.
- `xcd0_gc_tcdec`: texture/cache pipeline controls including TCP invalidate/status/control, channel steering, cache policy registers, EDC/RAS reporting, TCI controls, and the start of TCC controls.

The line range begins inside a register definition: only the remaining masks for `UTCL2_CE_ERR_STATUS_HI` are present here, while its shifts and earlier masks are in the preceding chunk. The range also ends inside `TCC_CTRL2`: the first three masks are in this chunk and the remaining `TCC_CTRL2` masks continue in the next chunk. Merge/reconciliation should account for those boundary splits.

## Purpose

`gc_9_4_3_sh_mask.h` supplies symbolic bitfield metadata for the AMDGPU GC 9.4.3 IP block. These macros let driver code build and decode MMIO register values without hard-coding numeric bit offsets at each call site. For example, AMDGPU code can use `REG_SET_FIELD(tmp, VM_CONTEXT0_CNTL, ENABLE_CONTEXT, 1)` and rely on this header to provide `VM_CONTEXT0_CNTL__ENABLE_CONTEXT__SHIFT` and `VM_CONTEXT0_CNTL__ENABLE_CONTEXT_MASK`.

For this chunk, the main purpose is to expose the programmable surface for graphics-hub virtual memory and cache-control hardware:

- VM context setup for VMIDs 0 through 15, including context enablement, page-table depth, page-table block size, retry policy for invalid-page/protection faults, and interrupt/default handling for range, dummy-page, PDE, valid, read, write, execute, and secure protection faults.
- VM invalidation machinery for engines 0 through 17. The macros define semaphore bits, request payloads, acknowledge fields, and optional address range registers used to flush page-table and translation caches after GPU page-table changes.
- VM aperture and memory-controller controls for AGP, framebuffer, system aperture, default page addresses, HBM-local ranges, XGMI local frame buffer regions, cacheable DRAM ranges, host mapping, low-power state, and local/shared virtual reset.
- TLB and translation-assist fields for checking L2 TLB busy/parity state and for representing address, VMID, VFID, permissions, memory type, NACK/ACK, and related metadata in GPUVA translation-assist request/response registers.
- TCP/TCI/TCC cache controls and status fields, including L1/L2 load/store/atomic policy encodings, channel steering, buffer address hashing, volatile policy, cache invalidation, busy status, clock-gating bits, error injection, and EDC error-reporting fields.

These constants are infrastructure for device initialization, VM updates, fault handling, cache-policy setup, suspend/resume restore, debugfs/register dumps, and RAS error collection on GC 9.4.3 devices.

## Important APIs, Types, And Data

There are no functions, structs, enums, or exported variables in this chunk. The API surface is a set of preprocessor macros following the AMD ASIC register convention:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: the pre-shifted bit mask for the field.

Important register families in the chunk include:

- `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL`: each context has the same 21 fields and 21 masks. Key fields are `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry controls, and fault interrupt/default controls for range, dummy page, PDE0, valid, read, write, execute, and secure faults.
- `VM_CONTEXTS_DISABLE`: one disable bit per context 0 through 15. This gives software a compact way to disable selected VM contexts.
- `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`: single `SEMAPHORE` bit per invalidation engine.
- `VM_INVALIDATE_ENG0_REQ` through `VM_INVALIDATE_ENG17_REQ`: per-engine request fields. Each request has a 16-bit `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, flags for invalidating L2 PTEs, PDE0, PDE1, PDE2, and L1 PTEs, plus `CLEAR_PROTECTION_FAULT_STATUS_ADDR` and `LOG_REQUEST`.
- `VM_INVALIDATE_ENG0_ACK` through `VM_INVALIDATE_ENG17_ACK`: per-engine `PER_VMID_INVALIDATE_ACK` status bits.
- `VM_INVALIDATE_ENG<n>_ADDR_RANGE_LO32` and `_HI32`: optional invalidation range bounds. Low registers include `ADDR` and `SYSTEM_ACCESS_MODE`; high registers expose the upper `ADDR`.
- `VM_CONTEXT<n>_PAGE_TABLE_BASE_ADDR_LO32/HI32`, `START_ADDR_LO32/HI32`, and `END_ADDR_LO32/HI32`: 32-bit halves for page-table base and valid virtual-address range programming.
- `MC_VM_*` registers: aperture and mapping fields including `MC_VM_NB_MMIOBASE`, `MC_VM_NB_MMIOLIMIT`, PCI control/arbitration, DRAM top registers, `MC_VM_FB_OFFSET`, system aperture default addresses, steering, shared reset, memory power, cacheable DRAM ranges, `MC_VM_APT_CNTL`, local HBM ranges and locks, XGMI LFB controls, cacheable DRAM control, host mapping, framebuffer and AGP locations, system aperture low/high, and `MC_VM_MX_L1_TLB_CNTL`.
- `UTCL2_CGTT_CLK_CTRL`: UTCL2 clock-gating and frequency-gating delay/override fields such as `SOFT_OVERRIDE`, `DS_OVERRIDE`, `REG_OVERRIDE`, `TCP_OVERRIDE`, `FGCG_DLY`, and `FGCG_DIS`.
- `L2TLB_TLB0_STATUS`: `BUSY` and `FOUND_PARITY_ERRORS`.
- `UTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*` and `RESPONSE_*`: address, VMID, VFID, VF/GPA mode, permissions, client ID, request, fragment size, snoop, SPA/IO/TMZ, no-PTE, memory type, memlog, LLC no-alloc, NACK, and ACK fields.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CHAN_STEER_0/1`, `TCP_ADDR_CONFIG`, `TCP_CREDIT`, and `TCP_BUFFER_ADDR_HASH_CNTL`: texture-cache pipeline invalidation, busy/status, cache sizing/force-hit/miss, channel steering, address geometry, credits, and hashing.
- `TC_CFG_L1_LOAD_POLICY0/1`, `TC_CFG_L1_STORE_POLICY`, `TC_CFG_L2_LOAD_POLICY0/1`, `TC_CFG_L2_STORE_POLICY0/1`, and `TC_CFG_L2_ATOMIC_POLICY`: four 2-bit policy fields per 32-bit register for L1/L2 load, store, and atomic cache policies.
- `TC_CFG_L1_VOLATILE` and `TC_CFG_L2_VOLATILE`: volatile policy nibbles.
- `TCP_*_EDC_*` and `TCI_*_EDC_*`: corrected and uncorrected EDC reporting fields. High registers indicate ECC/parity class, error-info validity, error information, UE/CE counters, fatal-event-detected or poison bits, and reserved bits. Low registers indicate status/address validity, error address, and memory ID.
- `TCI_MISC`, `TCI_CNTL_1/2/3`, `TCI_DSM_CNTL`, `TCI_DSM_CNTL2`, and `TCI_STATUS`: TCI clock gating, bandwidth/combining behavior, debug/error-injection controls, busy status, FIFO/RAM depths, L1 invalidation-on-WBINVL2, and TCA credit fields.
- `TCC_CTRL` and partial `TCC_CTRL2`: TCC cache sizing, rate, FIFO size, set hashing, multiple clock-mode fields, shared 128-byte-read disable, probe FIFO size, NaN/Inf clamp, probe-filter control, wait-stable count, and several fine-grained clock-gating disable fields. `TCC_CTRL2` continues after the chunk boundary.

The consumer-side helper APIs are defined elsewhere in AMDGPU, but this chunk is designed for them. The most relevant patterns are `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and `WREG32_SOC15_OFFSET`, with register addresses coming from the paired `gc_9_4_3_offset.h`.

## Control Flow

This header chunk has no runtime control flow. Its control-flow role is indirect: it parameterizes register programming sequences in AMDGPU and KFD code.

Typical VM initialization flow using these fields is visible in `amdgpu/gfxhub_v1_2.c`:

1. The driver includes `gc/gc_9_4_3_offset.h` for register addresses and this file for field metadata.
2. VMID page-table base registers are written through `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` plus a context address stride. The corresponding `_ADDR` masks in this chunk document that the full 32-bit low/high words carry address bits.
3. VMID0 aperture start/end registers are programmed with `VM_CONTEXT0_PAGE_TABLE_START_ADDR_*` and `END_ADDR_*` fields.
4. System aperture registers such as `MC_VM_AGP_BASE`, `MC_VM_AGP_BOT`, `MC_VM_AGP_TOP`, `MC_VM_SYSTEM_APERTURE_LOW_ADDR`, `MC_VM_SYSTEM_APERTURE_HIGH_ADDR`, and default-address registers are set from `adev->gmc` ranges and scratch/dummy pages.
5. `MC_VM_MX_L1_TLB_CNTL` is read, modified with `REG_SET_FIELD`, and written back to enable the L1 TLB, select system access behavior, enable the advanced driver model, set unmapped access behavior, select `MTYPE`, and enable ATC.
6. `VM_CONTEXT0_CNTL` and `VM_CONTEXT1_CNTL` are read/modified/written to enable contexts and choose page-table depth, block size, retry handling, and protection-fault response behavior.
7. Invalidation engine addresses and distances are recorded from `regVM_INVALIDATE_ENG0_*`, `regVM_INVALIDATE_ENG1_*`, and context register spacing so common VM hub code can invalidate VMIDs without hard-coding per-engine register numbers.

VM invalidation itself is a hardware handshake represented by the `VM_INVALIDATE_ENG<n>` register families:

1. Software claims or observes the engine semaphore.
2. Software writes an invalidation address range when range invalidation is used.
3. Software writes a request word selecting VMIDs and PTE/PDE/L1/L2 flush behavior.
4. Hardware reports completion in the ACK register.
5. Higher-level VM code can poll or wait until the ACK bits match the requested VMID mask.

The translation-assist request/response registers define another hardware protocol. Request fields encode a GPU virtual address, VMID/VFID context, access permissions, GPA/VF attributes, client ID, and a request bit. Response fields encode translated address bits, permissions, fragment size, cache/memory attributes, NACK/ACK state, and no-PTE or TMZ information. The header does not implement the protocol; it makes the request/response words decodable and constructible.

For cache and RAS controls, driver flow is similarly external. `gfx_v9_4_3.c` includes this header and registers TCP/TCI/TCC memory blocks in RAS tables using paired low/high EDC registers. EDC collection logic can read the registers and use these masks to decode status validity, address validity, memory ID, error information, and corrected/uncorrected counters. Cache-policy and invalidate code can use `TCP_INVALIDATE`, `TCP_STATUS`, `TC_CFG_*`, and TCI/TCC fields to configure or observe cache behavior.

## State And Persistence Behavior

The macros themselves are compile-time constants and carry no state. The state represented by this chunk lives in GPU MMIO registers and is persistent at hardware scope until reset, power-gating loss, suspend/resume reinitialization, driver reprogramming, or firmware/hardware side effects.

Important state categories are:

- Per-VMID state: `VM_CONTEXT<n>_CNTL`, page-table base, start, and end registers define which address spaces are active and which GPU virtual ranges are legal for each VMID.
- Fault behavior state: context control bits decide whether range, dummy-page, PDE0, valid, read, write, execute, and secure faults interrupt, use defaults, or retry. Incorrect persistence across reset/resume can change user-visible GPU fault behavior.
- Invalidation state: invalidation semaphores, request words, ACK words, and address ranges are transient hardware synchronization state. They should not be treated as durable configuration; stale request/ACK interpretation can cause missed TLB flushes or hangs.
- Aperture state: MC VM registers define framebuffer, AGP, HBM, system aperture, cacheable DRAM, host mapping, XGMI LFB, and default fault addresses. These are core memory-routing state and must match `adev->gmc` topology, virtualization mode, XGMI setup, and VRAM/GART placement.
- TLB/cache state: `MC_VM_MX_L1_TLB_CNTL`, L2 TLB status, TCP/TCI/TCC controls, policy registers, and invalidation controls shape caching, translation, and busy status. Some values are configuration, while status bits such as `BUSY`, `TCP_BUSY`, and `TCI_BUSY` are live hardware observations.
- RAS/EDC state: EDC low/high registers expose latched error status, address information, memory ID, error info, counters, and poison/fatal flags. Reads may be part of a wider RAS flow that logs, clears, or escalates errors.
- Debug/error-injection state: `TCI_DSM_CNTL` and `TCI_DSM_CNTL2` expose write-RAM irritator and error-injection controls. These should remain tightly controlled because they intentionally perturb hardware behavior.

Because this is a kernel driver header, no file-system persistence is involved. Persistence concerns are register programming order, reset-domain behavior, XCC instance replication, and whether suspend/resume or GPU reset paths restore the same values consistently across all active GC instances.

## Dependencies And Integration Points

This file depends conceptually on AMD's generated register database for GC 9.4.3. It must stay consistent with:

- `gc_9_4_3_offset.h`, which provides the `reg...` address symbols for the fields described here.
- SOC15 access helpers and field macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and `WREG32_SOC15_OFFSET`.
- AMDGPU VM hub structures such as `struct amdgpu_vmhub`, which store context and invalidation-engine base addresses and distances derived from GC register offsets.
- `adev->gmc` memory topology state, including framebuffer, GART, AGP, VRAM, HBM, XGMI, dummy page, scratch page, and page-directory base values.
- KFD VM and queue management policy, especially retry/XNACK behavior and per-process memory policy.
- RAS infrastructure, which maps GC memory blocks to low/high EDC status register pairs.

Known direct includes of this header in the GC 9.4.3 path are:

- `amdgpu/gfxhub_v1_2.c`: programs VM context registers, page-table bases/ranges, system aperture registers, L1 TLB control, invalidation-engine addresses, and XGMI LFB discovery. This is the strongest direct consumer for the VM and MC fields in this chunk.
- `amdgpu/gfx_v9_4_3.c`: uses GC register metadata for graphics setup, TCP/TCI/TCC block naming, RAS register registration, and related GC debug/error-handling paths.
- `amdgpu/amdgpu_amdkfd_gc_9_4_3.c`: KFD/AMDGPU bridge for GC 9.4.3; it uses the same generated register namespace for queue, watchpoint, and compute-facing configuration.
- `amdkfd/kfd_device_queue_manager_v9.c`: includes this header for GFX9-era KFD queue/process memory configuration fields, though many of the fields it uses are outside this exact line range.

The chunk is also integrated indirectly by common VM hub code. `gfxhub_v1_2.c` records addresses for `regVM_INVALIDATE_ENG0_SEM`, `REQ`, `ACK`, `regVM_CONTEXT0_CNTL`, context distance, invalidation request distance, and invalidation address-range distance. Common code can then operate over multiple VM hubs and XCC instances using those offsets while relying on these masks to preserve field layout.

## Risks And Edge Cases

The highest risk is a silent bitfield mismatch. These macros are trusted by register field helpers; if a mask or shift is wrong, the driver can write a valid-looking 32-bit value that programs the wrong hardware bit. For VM context control this can disable address spaces, select the wrong page-table depth, break invalid-page retry/XNACK behavior, or convert recoverable GPU page faults into hangs or unexpected interrupts.

The repeated register families create copy/paste and generation risks. `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` are expected to have identical field layouts. The same is true for invalidation engines 0 through 17 and for repeated page-table base/start/end register pairs. A single divergent mask in one instance could affect only one VMID or one invalidation engine, making the bug highly workload-specific.

Invalidation request and ACK fields are correctness-critical. Missing `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE*`, or `INVALIDATE_L1_PTES` bits can leave stale translations resident after page-table updates. Wrong `PER_VMID_INVALIDATE_REQ` or ACK decoding can make software believe a VMID flush completed when it did not, or spin forever waiting for the wrong bit.

Address field units differ by register family and call site. Some driver writes shift addresses by 12, 18, 24, or 44 before programming low/high registers. The masks in this chunk usually describe the register payload width, not the semantic address granularity. Reviewers must check the programming code and hardware spec rather than assuming all `_ADDR` fields use byte units.

Virtualization and partitioning add integration risk. GC 9.4.3 systems can have multiple XCC instances, SR-IOV VF mode, XGMI-connected memory, and GART-for-framebuffer translation. `gfxhub_v1_2.c` loops over instance masks and sometimes disables conventional FB/AGP aperture windows. A field mismatch may only appear on multi-XCC, XGMI, VF, or partitioned configurations.

RAS fields have diagnostic and availability impact. EDC high/low masks decide how software interprets corrected/uncorrected counts, poison/fatal flags, memory IDs, and error addresses. Incorrect decoding can under-report real hardware faults, over-report reserved bits as errors, or attribute an error to the wrong GC memory block.

The chunk boundaries are partial. `UTCL2_CE_ERR_STATUS_HI` is already in progress at line 9541 and `TCC_CTRL2` continues after line 11973. Chunk-local tooling should not assume each commented register block is complete. The merge lane should reconstruct this file with adjacent chunks before doing whole-register completeness checks.

Manual edits are fragile because this header is generated. Any change should be checked against the corresponding AMD register specification or regeneration source. Local fixes to only the mask header can be overwritten and can also desynchronize offset, enum, and mask headers for the same IP.

## Test Signals

Useful verification signals for this chunk include:

- Compile the AMDGPU driver with GC 9.4.3 enabled and warnings treated seriously. This catches missing macro names, duplicate definitions, and obvious field-helper integration breakage.
- Boot or initialize a GC 9.4.3 device and confirm `gfxhub_v1_2.c` VM setup succeeds across all active XCC instances. Relevant signals are successful GART setup, VMID0 context enablement, page-table base/range programming, and no early VM faults.
- Exercise GPU VM updates that require invalidation. Page-table updates followed by command submission should complete without stale mappings, VM fault storms, or invalidation timeout messages.
- Test KFD/HSA workloads with XNACK/retry enabled and disabled. The `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` and related context-fault fields should produce expected recoverable fault or no-retry behavior.
- Run suspend/resume and GPU reset paths. After resume or reset recovery, aperture, context, TLB, and invalidation-engine programming should be restored and command submission should resume without VM faults.
- Validate multi-XCC and XGMI configurations. The same VM and aperture programming should be applied to each intended `GET_INST(GC, i)` instance, and XGMI LFB size/region fields should decode to plausible ranges.
- Exercise SR-IOV VF and bare-metal paths if hardware is available. Aperture programming differs by virtualization mode, and `VF`, `VFID`, and translation-assist fields are particularly relevant to virtualized deployments.
- Check RAS paths by reading/injecting supported corrected and uncorrected errors for TCP and TCI blocks. Expected signals are correct low/high EDC status decoding, memory block attribution, CE/UE counter handling, and no reserved-bit false positives.
- Use register dumps or debugfs comparisons against known-good hardware traces. The decoded `MC_VM_MX_L1_TLB_CNTL`, `VM_CONTEXT<n>_CNTL`, `VM_INVALIDATE_ENG<n>_*`, TCP/TCI/TCC control, and EDC fields should match expected boot-time and workload-time values.
- For merge validation, verify that adjacent chunk documents cover the missing start of `UTCL2_CE_ERR_STATUS_HI` and the remainder of `TCC_CTRL2`, then run a whole-file scan for every `__SHIFT` having a matching `_MASK` where the register database expects both.

### subset-b-002690: lines 11974-14503

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 11974-14503

## Purpose

This chunk is a generated register-field mask slice for AMD GC 9.4.3. It exports C preprocessor constants for bit shifts and masks used to compose and decode 32-bit graphics-core register values. The range starts in the tail of `TCC_CTRL2`, covers TCC/TCA/TCX cache fabric diagnostic, soft-reset, writeback-invalidate, and ECC/error-status fields, then enters `addressBlock: xcd0_gc_shdec` for shader and compute state registers, and ends in `addressBlock: xcd0_gc_cppdec` with command processor ring, doorbell, interrupt, ECC, power, and debug masks through `CP_ME1_PIPE0_INT_CNTL`.

The file is declarative. It contains no executable code, but its macro names and numeric values are part of the AMDGPU hardware binding for GC 9.4.3. Including code combines these masks with companion register-offset headers and register helper macros to program shader stages, compute dispatches, command processor rings, KIQ/HQD queues, interrupts, and error reporting.

## Major Register Areas Covered

The initial TCC/TCA/TCX section describes lower-level cache and transaction fabric fields. `TCC_DSM_CNTL`, `TCC_DSM_CNTLA`, `TCC_DSM_CNTL2`, `TCC_DSM_CNTL2A`, `TCC_DSM_CNTL2B`, and `TCC_DSM_CNTL3` expose DSM irritator and error-injection fields for cache data banks, dirty banks, tag arrays, source/atomic/write-return FIFOs, latency FIFOs, return paths, output FIFOs, and write-early-return behavior. `TCC_WBINVL2` exposes a `DONE` status bit, while `TCC_SOFT_RESET` exposes `HALT_FOR_RESET`. `TCA_CTRL`, `TCA_BURST_MASK`, `TCA_BURST_CTRL`, `TCA_DSM_CNTL`, `TCA_DSM_CNTL2`, `TCX_CTRL`, `TCX_DSM_CNTL`, and `TCX_DSM_CNTL2` cover fabric arbitration, fine-grained clock-gating disables, burst controls, and SED/error-injection controls. `TCA_*_ERR_STATUS_*`, `TCX_*_ERR_STATUS_*`, and `TCC_*_ERR_STATUS_*` provide corrected and uncorrected error status fields, including validity bits, address, memory ID, ECC/parity indicators, error info, CE/UE counters, FED counters, and poison status.

The `xcd0_gc_shdec` section defines shader-program state for graphics stages. It covers PS, VS, GS, ES, HS, and LS program base registers, resource registers, late allocation, user data, and cross-stage details such as `SPI_SHADER_PGM_RSRC*_PS`, `SPI_SHADER_PGM_RSRC*_VS`, `SPI_SHADER_PGM_RSRC*_GS`, `SPI_SHADER_PGM_RSRC*_HS`, `SPI_SHADER_PGM_RSRC2_GS_VS`, `SPI_SHADER_PGM_RSRC4_GS`, and the `SPI_SHADER_USER_DATA_*` families. Important fields include shader program base low/high words, VGPR/SGPR counts, priority, float mode, private/debug/IEEE flags, scratch enable, user SGPR count and MSB, exception enables, trap-present flags, LDS sizing, stream-out enables, CU masks, wave limits, SIMD disable masks, and 32 full-width user-data registers per stage or common bank.

The compute portion of `xcd0_gc_shdec` defines dispatch packet and resource fields. `COMPUTE_DISPATCH_INITIATOR` controls shader enable, partial threadgroups, ordered append, thread-dimension mode, cache invalidation hints, and restore behavior. Dimension, start, restart, and thread-count registers define grid geometry and full/partial thread counts. `COMPUTE_PGM_LO/HI`, `COMPUTE_DISPATCH_PKT_ADDR_*`, `COMPUTE_DISPATCH_SCRATCH_BASE_*`, `COMPUTE_PGM_RSRC1`, `COMPUTE_PGM_RSRC2`, `COMPUTE_PGM_RSRC3`, `COMPUTE_RESOURCE_LIMITS`, static thread management by SE, temporary ring size, VMID, relaunch, wave restore address, thread trace, dispatch ID, threadgroup ID, checksum, and `COMPUTE_USER_DATA_0..15` describe the hardware state needed to launch and resume compute workloads.

The `xcd0_gc_cppdec` section starts command processor control and diagnostics. It includes defer/write data command registers (`CP_DFY_*`), EOP wait time, CPC MGCG sync, interrupt info/address/PASID, virtualization status, `CP_GFX_ERROR`, UTCL1 control/error fields for CPG/CPC/CPF, AQL SMM status, graphics ring-buffer base/control/read-pointer/write-pointer fields, write-pointer polling address fields, privilege mode, global and per-ring CP interrupt enable/status registers, CP device/priority/fatal-error/VMID registers, doorbell control/range registers, active bits, ME/PFP/CE/MEC F32 interrupt summaries, CP power and memory-sleep controls, ECC first-occurrence registers, `GB_EDC_MODE`, CP/CPF/CPC debug controls, CP priority-queue write-pointer polling controls, and `CP_ME1_PIPE0_INT_CNTL`.

## Important APIs, Types, and Functions

There are no functions, types, structs, or enums in this chunk. The exported interface is the macro namespace:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field's 32-bit mask.
- Register comments and `addressBlock` comments preserve generated grouping metadata for readers and downstream tooling.

The main consumers are AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, `RREG32_XCC`, `WREG32_XCC`, and `WREG32_FIELD15_PREREG`. For GC 9.4.3 specifically, representative integration appears in `amdgpu/gfx_v9_4_3.c`: `CP_INT_CNTL_RING0` fields are set when enabling GUI idle interrupts, `CP_PQ_WPTR_POLL_CNTL.EN` is disabled during KIQ/HQD setup, and `CP_ME1_PIPE0_INT_CNTL.TIME_STAMP_INT_ENABLE` is toggled in MEC interrupt setup. `amdgpu/amdgpu_amdkfd_gc_9_4_3.c` writes `CP_PQ_WPTR_POLL_CNTL1` with a queue mask when restoring KFD queue write-pointer polling.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time constant expansion:

1. A GC 9.4.3 AMDGPU source file includes generated register offset and mask headers.
2. The code selects a register and field by ASIC generation, XCC instance, shader stage, ring, pipe, or queue.
3. Helper macros combine the `SHIFT` and `MASK` definitions with a field value.
4. The resulting 32-bit value is written to MMIO or read back and decoded by the including driver code.

The hardware flows implied by the masks are substantial. Shader/compute setup programs resource registers, user data, program base addresses, VMIDs, thread geometry, scratch bases, and dispatch initiators before a graphics draw or compute dispatch can execute. Command processor setup writes ring-buffer bases, ring sizes, read-pointer report addresses, write-pointer registers, doorbell offsets and ranges, queue masks, and interrupt enables. Error-handling flows read status and first-occurrence fields to decode ECC, UTCL1, fatal, privilege, opcode, timestamp, and reserved-bit events.

## State and Persistence Behavior

The header stores no state. The state described by the macros lives in GPU registers and persists according to hardware power/reset behavior and driver sequencing:

- TCC/TCA/TCX fields can affect cache/fabric diagnostics, error injection, clock-gating overrides, writeback invalidation, soft reset, ECC/SED status, and corrected/uncorrected error counters.
- Shader and compute fields hold per-dispatch or per-pipeline executable state such as program addresses, resource usage, wave/CU limits, user SGPR payloads, scratch pointers, LDS allocation, exception/trap bits, thread geometry, VMID, and relaunch/restore metadata.
- CP fields hold ring and queue control state, read/write pointers, doorbell ranges, VMID assignment, interrupt enables/status, error-first-occurrence data, debug overrides, power/memory-sleep gating controls, and write-pointer polling configuration.

The chunk does not encode access type, reset values, read-clear behavior, write-one-to-clear behavior, locking, sequencing requirements, or XCC broadcast rules. Those are enforced by the caller, firmware, hardware documentation, and the AMDGPU/KFD lifecycle around GPU reset, suspend/resume, queue eviction/restore, and per-XCC initialization.

## Dependencies and Integration Points

This generated header depends only on the C preprocessor. In practice it must stay synchronized with adjacent generated GC 9.4.3 headers that define register offsets and base indices, especially `gc_9_4_3_offset.h`-style files and SOC15 register-base metadata.

Important integration points include:

- `amdgpu/gfx_v9_4_3.c` graphics IP initialization and ring/KIQ setup, which use CP ring, polling, interrupt, and per-XCC register access helpers.
- `amdgpu/amdgpu_amdkfd_gc_9_4_3.c` KFD queue restore paths, which write `CP_PQ_WPTR_POLL_CNTL1` and related HQD registers for user-mode compute queues.
- Shader and command processor packet setup paths that program `SPI_SHADER_*` and `COMPUTE_*` registers through PM4 or direct register programming.
- Interrupt handling and enable paths for global CP interrupts, per-ring interrupts, ME/PFP/CE/MEC F32 summaries, timestamp interrupts, ECC errors, GPF/SUA violations, opcode errors, and reserved-bit errors.
- RAS and diagnostics paths that decode TCC/TCA/TCX CE/UE status, CP ECC first occurrence, UTCL1 errors, `CP_GFX_ERROR`, `CP_FATAL_ERROR`, and CP debug state.
- Multi-XCC GC 9.4.3 paths that select `GET_INST(GC, xcc_id)` and must pair these masks with the correct instance-specific register offset.

## Risks and Edge Cases

The primary risk is silent hardware misprogramming if a mask or shift drifts from the GC 9.4.3 register database. A wrong bit in this chunk can corrupt shader resource programming, compute dispatch geometry, CP ring pointer handling, doorbell routing, interrupt enables, or ECC/error decoding without producing a compile failure.

Repeated register families are a notable review hazard. The chunk contains many near-identical PS/VS/GS/HS/LS user-data registers, per-SE static thread-management registers, per-ring CP interrupt registers, and TCC/TCA/TCX error-status layouts. Copy-generation mistakes can be hard to spot because the structure looks intentionally repetitive.

Several masks expose full 32-bit data fields such as shader user data, program base low words, dispatch IDs, restart coordinates, ring write pointers, and obsolete ECC first-occurrence ring registers. Callers must use the correct fixed-width types and avoid assuming signed semantics from the `L` suffix on constants like `0xFFFFFFFFL`.

Some fields are control bits with side effects, while others are sticky status, counters, address captures, first-occurrence records, or debug-only overrides. The header does not distinguish safe read/write behavior. In particular, error-injection controls, soft reset, writeback invalidation, doorbell enable/hit, fatal-error, debug, and interrupt status fields require external sequencing and hardware-specific clearing rules.

The chunk starts mid-register at the mask tail of `TCC_CTRL2` and ends after `CP_ME1_PIPE0_INT_CNTL`; surrounding chunks are needed for the complete generated header context. A per-file report should avoid treating this range as a complete register map for GC 9.4.3.

## Test Signals

Useful validation signals are mostly build-time, static, and hardware-integration oriented:

- Kernel builds that include GC 9.4.3 AMDGPU and KFD paths should compile without missing or renamed macro errors.
- Static comparison against AMD's authoritative generated register database should verify every `SHIFT`/`MASK` pair, repeated family, and address-block boundary.
- Register helper tests or build-time assertions can check representative field round trips for `SPI_SHADER_PGM_RSRC*`, `COMPUTE_PGM_RSRC*`, `CP_INT_CNTL_RING0`, `CP_ME1_PIPE0_INT_CNTL`, `CP_PQ_WPTR_POLL_CNTL`, and TCC/TCA/TCX error status masks.
- GC 9.4.3 hardware testing should exercise graphics shader launch, compute dispatch, KIQ/HQD queue setup, queue eviction/restore, write-pointer polling, doorbell delivery, and per-XCC ring initialization.
- Interrupt tests should confirm CP busy/empty/idle, timestamp, ECC, GPF, SUA, opcode, privilege, and reserved-bit interrupt enables and statuses map to the expected handler paths.
- RAS and fault-injection testing should validate TCC/TCA/TCX CE/UE decode, CP ECC first-occurrence decode, UTCL1 error handling, fatal-error paths, and debug/status reporting under controlled errors.

### subset-b-002691: lines 14504-16929

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 14504-16929

## Purpose

This chunk is a generated AMD GC 9.4.3 register field mask header range. It provides C preprocessor constants for command processor, shader processor interface, HQD/MQD queue, and texture cache/TCP register fields. Each field is represented by a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro, letting AMDGPU code compose and decode 32-bit hardware register values without embedding raw bit positions.

The range starts at `CP_ME1_PIPE1_INT_CNTL`, after the adjacent `CP_ME1_PIPE0_INT_CNTL` family has already begun in the previous chunk, and ends inside `TCP_UTCL1_CNTL2`, before `TCP_UTCL1_STATUS` appears in the next lines. The content is declarative hardware metadata rather than executable code. Its correctness matters because consumers normally combine these masks with companion GC 9.4.3 register offset headers and AMD register helpers such as field set/get macros around MMIO or indirect register reads and writes.

## Major Register Areas Covered

The opening section covers command processor MEC/ME interrupt enable and status fields for `CP_ME1_PIPE1_INT_CNTL` through `CP_ME2_PIPE3_INT_CNTL`, followed by matching `CP_ME1_PIPE0_INT_STATUS` through `CP_ME2_PIPE3_INT_STATUS` groups and aggregate debug status registers `CP_ME1_INT_STAT_DEBUG` and `CP_ME2_INT_STAT_DEBUG`. These families expose queue and pipe events such as compare-query status, dequeue requests, CP ECC errors, SUA violations, graphics page faults, WRM poll timeouts, privileged register faults, opcode errors, timestamps, reserved-bit errors, and generic interrupt lanes.

The next command processor block defines priority, program-counter start, interrupt routine start, context, VMID, CPC interrupt, indirect-cache, preemption, queue status, and ECC/error reporting fields. Important register groups include `CP_ME*_PIPE_PRIORITY_CNTS`, per-pipe priorities, `CP_*_PRGRM_CNTR_START`, `CP_*_INTR_ROUTINE_START`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME*`, `CP_VMID_RESET`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CP_VMID_PREEMPT`, `CP_PQ_STATUS`, `CP_CPC_IC_*`, `CP_MEC*_F32_INT_DIS`, `CP_VMID_STATUS`, and CPC/CPF/CPG correctable and uncorrectable error status low/high registers.

The `xcd0_gc_cppdec2` address block adds scheduler ring doorbell controls and command processor diagnostic/error injection controls. It includes `CP_RB_DOORBELL_CONTROL_SCH_0` through `_SCH_7`, `CP_RB_DOORBELL_CLEAR`, CPF/CPG/CPC DSM control families, `CP_EDC_FUE_CNTL`, graphics MQD base/control fields, ring buffer status, CPG/CPC/CPF UTCL1 fault-status fields, shader dispatch control, soft reset control, and CPC graphics control.

The `xcd0_gc_spipdec` address block describes SPI arbitration, wave/debug, scratch, queue reset, and compute-unit resource reservation fields. It includes `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_*`, `SPI_CDBG_SYS_*`, workload pipe percentages for graphics, HP3D, and compute queues, graphics debug wave/trap/per-VMID controls, scratch address check/status, reset/debug controls, compute queue reset, `SPI_RESOURCE_RESERVE_CU_0` through `_CU_15`, matching enable registers, compute wavefront context save controls, and `SPI_ARB_CNTL_0`.

The `xcd0_gc_cpphqddec` address block is the largest part of the chunk. It defines HQD/HPD/MQD queue-management fields for graphics and compute queues: HQD graphics control/status, persistent state, pipe and queue priority, scheduling quantum, packet queue base/read/write pointers, doorbell control, packet queue control, indirect buffer base/control, IQ timer/read pointer, dequeue/offload controls, semaphore and message type, atomic pre-operation registers, HQ scheduler/status/control pairs, EOP base/control/read/write/event fields, context-save addresses and sizes, GDS resource state, HQD error bits, EOP write-pointer memory, AQL control/dispatch IDs, and MQD base/control fields.

The final `xcd0_gc_tcpdec` block covers TCP watchpoints, GATCL1 controls, DSM controls, clock controls, and UTCL1 control fields. It defines four TCP watch address/control groups with address, VMID, ATC, mode, valid, and mask fields; cache/TLB invalidation and force-miss fields in `TCP_GATCL1_CNTL`; ATC EDC count fields; TCP DSM irritator selection/single-write controls; TCP clock-gating disable fields in `TCP_CNTL2`; UTCL1 GPUVM response, invalidation, force miss, cache-size, and FIFO-depth controls in `TCP_UTCL1_CNTL1`; and the beginning of `TCP_UTCL1_CNTL2` fields for spare bits, MTYPE override, line-valid state, GPUVM invalidation mode, force snoop, forced invalidate ack, 2M-to-64K fragmentation, and thrashing controls.

## Important APIs, Types, and Functions

There are no functions, structs, enums, or inline helpers in this chunk. The API surface is the macro namespace:

- `*_SHIFT` constants give the bit offset for a register field.
- `*_MASK` constants give the 32-bit field mask.
- Register comments such as `//CP_HQD_PQ_CONTROL` and address block comments such as `// addressBlock: xcd0_gc_cpphqddec` preserve generated grouping information.

Consumers are expected to include this file with the matching GC 9.4.3 offset definitions and then use the macros through AMDGPU register helpers or direct bit operations. The names are part of the source-level hardware binding for this ASIC generation; renaming or changing a value breaks callers even though the header itself has no linker-visible symbols.

## Control Flow

This header has no runtime control flow. The effective flow is compile-time and caller-driven:

1. AMDGPU source includes the GC 9.4.3 offset and mask headers.
2. The caller chooses a register and field macro for a specific graphics, command processor, SPI, HQD, or TCP programming path.
3. Register helper macros shift, mask, insert, or extract field values.
4. The caller performs MMIO, indexed, or other hardware register access using the companion register offset.

The repeated interrupt, doorbell, HQD, and resource-reservation families imply external loops or table-driven setup code, but this file does not encode those loops. It also does not encode access type, reset value, write-one-to-clear behavior, ordering requirements, or locking.

## State and Persistence Behavior

The macros are stateless compile-time constants. The state they describe lives in GC 9.4.3 hardware registers and persists according to hardware and driver lifecycle rules.

Command processor interrupt and status bits represent live events, enables, queue faults, ECC/error states, VMID state, preemption state, and diagnostics. Doorbell and ring/MQD/HQD fields describe persistent queue configuration such as base addresses, sizes, read/write pointers, doorbell routing, active state, priorities, scheduling quantum, context-save addresses, EOP buffers, and AQL dispatch tracking. SPI fields describe arbitration/debug state and reserved compute-unit masks. TCP fields describe watchpoint state, cache/TLB invalidation behavior, UTCL1 response and fault behavior, and clock/power gating controls.

Programmed values can survive until a later driver write, queue teardown, context restore, power transition, suspend/resume reinitialization, GPU reset, or firmware-driven sequence changes them. This header does not enforce validation or sequencing; callers must avoid writing reserved bits and must respect side effects documented by the hardware specification.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it must stay synchronized with AMD's generated GC 9.4.3 register database and the matching offset/header files under the same `asic_reg/gc` tree. Integration points include:

- AMDGPU command processor initialization, interrupt setup, and interrupt-status decoding for ME/MEC pipes, CPC, CPF, and CPG.
- Ring, doorbell, VMID, MQD, HQD, AQL, EOP, packet queue, indirect buffer, and context-save setup paths for graphics and compute queues.
- GPU fault and hang diagnostics that decode ECC, UTCL1, GPF, privilege, opcode, reserved-bit, and HQD error status fields.
- SPI debug, wave trap, compute queue reset, arbitration, and CU resource reservation programming.
- TCP watchpoint programming, UTCL1 invalidation/fault controls, cache/TLB behavior, DSM/error-injection support, and clock-gating controls.

Because many macros are consumed via token-pasting field helpers, the exact `REGISTER__FIELD` spelling is an API contract for source consumers. Numeric correctness also depends on using a GC 9.4.3 offset definition with the GC 9.4.3 mask definition; mixing ASIC generations can silently target wrong fields.

## Risks and Edge Cases

The primary risk is bitfield drift between this generated header and the hardware specification. A wrong shift or mask can enable the wrong interrupt, miss a fatal error, misprogram a doorbell, corrupt a queue pointer field, reserve the wrong compute units, or change TCP/UTCL1 cache behavior. These failures often appear as hangs, missed interrupts, VM faults, bad preemption, or misleading diagnostics rather than clean compile errors.

Repeated register families create review risk. ME1/ME2 pipe interrupt groups, doorbell scheduler controls, SPI CU reservation registers, and HQD queue fields differ mostly by register number, so generator or copy errors can be hard to spot manually. Several fields are full-width address, pointer, dispatch ID, or reserved masks (`0xFFFFFFFFL`), so callers must use appropriate 32-bit register access types and pair high/low address halves correctly.

The chunk boundaries are partial. `CP_ME1_PIPE0_INT_CNTL` belongs to the preceding chunk, while `TCP_UTCL1_CNTL2` continues immediately before later TCP status and DSM2 definitions. Merge tooling should preserve this exact range and not treat either adjacent family as completely covered by this document alone.

The header does not distinguish control, status, sticky status, clear-on-write, read-only, write-only, or debug/test-only fields. That is especially important for interrupt status, ECC status, soft reset, DSM/FUE/error injection, dequeue/offload, watchpoint, and UTCL1 invalidation fields, where incorrect read-modify-write behavior can lose events or cause hardware side effects.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Build AMDGPU with GC 9.4.3 support enabled to catch syntax errors, duplicate definitions, and consumers expecting different macro names.
- Compare this range against the authoritative GC 9.4.3 register database and matching offset header to verify every field name, shift, mask, width, and register grouping.
- Exercise command submission on GC 9.4.3 hardware, including graphics and compute queues, doorbells, VMID assignment, MQD/HQD setup, AQL queues, EOP handling, indirect buffers, preemption, and queue teardown.
- Validate interrupt enable/status handling with normal workloads and fault-injection paths for CP ECC, GPF, privileged register, opcode, reserved-bit, timestamp, dequeue, and generic interrupts.
- Run suspend/resume, GPU reset, and hang-recovery scenarios to catch stale queue, context-save, EOP, soft-reset, and UTCL1 state.
- Use debug or bring-up tests for SPI wave/trap state, compute queue reset, CU resource reservation masks, TCP watchpoints, UTCL1 invalidation/fault controls, and DSM/FUE error-injection fields where hardware access is available.

### subset-b-002692: lines 16930-19506

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 16930-19506

## Scope

This chunk is a generated AMD GC 9.4.3 shader/register mask header slice. It starts at the tail of `TCP_UTCL1_CNTL2` mask definitions, contains complete TCP status/perf/error-injection groups, the `xcd0_gc_gdspdec` GDS register block, the `xcd0_gc_rasdec` RAS signature block, and the beginning of the `xcd0_gc_gfxdec0` graphics pipeline state block. It ends inside `SPI_PS_INPUT_CNTL_19`, after its `CYL_WRAP_MASK`; the remaining masks for that register are in the next chunk.

The range contains 2,140 `#define` entries. They follow the generated convention `REGISTER__FIELD__SHIFT` for bit positions and `REGISTER__FIELD_MASK` for the corresponding 32-bit field masks. The file is declarative only: it exports constants used by AMDGPU and KFD code that writes or decodes GC 9.4.3 hardware registers.

## Purpose

`gc_9_4_3_sh_mask.h` provides the bitfield half of the GC 9.4.3 register ABI. This slice covers fields for texture cache/L1 VM status, GDS allocation and reset, graphics RAS signatures, depth/stencil and raster state, render target masks, viewport and clip state, and pixel shader input interpolation controls.

The constants are meant to be paired with `gc_9_4_3_offset.h`, which supplies the matching `reg...` offsets and base indices. Runtime driver code combines these masks and shifts with SOC15 helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, and packet-emission helpers. This avoids open-coded bit numbers in ASIC-specific paths.

## Important API Surface

- `TCP_UTCL1_CNTL2` tail masks describe L1 VM/cache control bits including memory-type override disable, any-line-valid, GPUVM invalidation mode, forced snoop, forced GPUVM invalidation acknowledgement, 2M-to-64K fragmentation, and thrashing protection/enablement. The matching shifts start before this chunk.
- `TCP_UTCL1_STATUS` exposes fault, retry, PRT, and timeout detection bits for TCP UTCL1 diagnostics.
- `TCP_DSM_CNTL2` provides error-injection enable/select fields for TCP cache RAM, LFIFO RAM, command FIFO, VM FIFO, DB RAM, UTCL1 LFIFO0/LFIFO1, and a global TCP inject delay field.
- `TCP_PERFCOUNTER_FILTER` and `TCP_PERFCOUNTER_FILTER_EN` define filter values and enables for TCP performance counter collection, including buffer/flat/dimension mode, data and numeric formats, software mode, sample count, opcode type, GLC/SLC, compression, and address mode.
- `GDS_VMID0_BASE/SIZE` through `GDS_VMID15_BASE/SIZE` define per-VMID GDS address windows. `GDS_GWS_VMID0` through `GDS_GWS_VMID15` define per-VMID GWS base/size fields. `GDS_OA_VMID0` through `GDS_OA_VMID15` define per-VMID ordered-append allocation masks.
- `GDS_GWS_RESET0`, `GDS_GWS_RESET1`, `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, and `GDS_OA_RESET` expose reset controls for global wave sync and ordered-append resources. `GDS_ENHANCE`, `GDS_OA_CGPG_RESTORE`, and GDS context-switch status/counter registers describe GDS behavior across compute, graphics, VS, PS0-PS7, and GS contexts.
- `RAS_SIGNATURE_CONTROL`, `RAS_SIGNATURE_MASK`, and `RAS_*_SIGNATURE*` define signature collection or comparison fields for SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI blocks.
- `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_Z_INFO`, `DB_STENCIL_INFO`, `DB_DFSM_CONTROL`, depth/stencil base/clear/bounds registers, and HTILE fields define depth-buffer state, compression/decompression behavior, Z/stencil formats, tile/compression layout, clear/copy operations, and override modes.
- `PA_SC_*` and `PA_CL_*` families define screen/window/generic/viewport scissors, clip rectangles, edge rules, hardware offsets, raster configuration, tile steering, viewport scale/offset, viewport Z min/max, user clip planes, and near-clip Z programming.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_BLEND_*`, `CB_DCC_CONTROL`, `COHER_DEST_BASE*`, and CP context identifiers define color output masks, blend constants, DCC control, coherency destination bases, and current CP performance/context identity fields.
- `SPI_PS_INPUT_CNTL_0` through the partial `SPI_PS_INPUT_CNTL_19` define pixel shader input mapping and interpolation controls: attribute offsets, default values, flat shading, cylindrical wrap, point-sprite texture selection, duplicate controls, FP16 interpolation mode, secondary attribute defaults, and attribute-valid bits.

There are no C functions, structs, enums, inline helpers, or runtime APIs in this chunk. The macro namespace itself is the exported interface.

## Control Flow

The header has no executable control flow. Its effective flow is compile-time inclusion followed by runtime register access in consumer code:

1. A GC 9.4.3 driver path includes this header and the offset header.
2. The code selects a register offset such as `regGDS_VMID0_BASE`, `regGDS_GWS_VMID0`, `regTCP_UTCL1_STATUS`, or a DB/PA/SPI graphics state register.
3. It composes, modifies, or decodes a 32-bit value by applying the relevant `__SHIFT` and `_MASK` constants, often through register-field helper macros.
4. It writes the value through MMIO, RLC-safe register paths, or command stream packet emission, or it reads status bits for diagnostics.

The GDS families imply indexed control flows. In `gfx_v9_4_3.c`, initialization loops write `regGDS_VMID0_BASE`, `regGDS_VMID0_SIZE`, `regGDS_GWS_VMID0`, and `regGDS_OA_VMID0` with offsets derived from the VMID to remove GDS/GWS/OA access for compute and user graphics VMIDs. Ring emission later programs the same resource windows for a target VMID, using `GDS_GWS_VMID0__SIZE__SHIFT` to pack GWS size with GWS base.

The DB/PA/CB/SPI families are graphics pipeline state definitions. They are normally consumed by command streams, clear-state tables, state setup code, or debugging paths rather than by local loops in the header. The RAS and TCP status/error-injection fields are diagnostic or service flows: code reads status/signature registers, checks the field masks, and may configure injection or performance-counter filters during validation and RAS handling.

## State and Persistence Behavior

The macros are stateless compile-time constants. The state they describe lives in GC 9.4.3 hardware registers and persists according to hardware reset, power-gating, context-switch, firmware, and driver programming rules.

GDS VMID base/size, GWS, and OA registers control per-VMID access to shared on-chip resources. Incorrect values can persist until rewritten by firmware, a ring packet, driver initialization, suspend/resume restore, or GPU reset. VMID0 is treated specially by the GC 9.4.3 graphics code so HWS firmware can preserve save/restore entries while other VMIDs are cleared during initialization.

DB, PA, CB, and SPI fields represent graphics context state. Their values are usually part of command-submission or context state and can survive within a context until another packet, clear-state load, context switch, or reset changes them. Depth/stencil compression controls, DCC state, scissor/viewport ranges, clip planes, raster configuration, and pixel shader input routing directly affect rendered output and memory accesses.

TCP, RAS, and GDS status/counter fields describe live hardware conditions such as VM faults, retries, PRT events, timeouts, RAS signatures, context-switch counts, and reset/resource status. This header does not encode access semantics such as read-clear, write-one-to-clear, privilege level, required ordering, or reserved-bit policy; those constraints belong to the hardware spec and the consuming driver code.

## Dependencies and Integration Points

- Depends only on the C preprocessor and its include guard, but semantically depends on AMD's generated GC 9.4.3 register database.
- Must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h`, which supplies offsets such as `regGDS_VMID0_BASE`, `regGDS_VMID0_SIZE`, `regGDS_GWS_VMID0`, `regGDS_OA_VMID0`, and `regTCP_UTCL1_STATUS`.
- Included by GC 9.4.3 consumers including `amdgpu/gfxhub_v1_2.c`, `amdgpu/gfx_v9_4_3.c`, `amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, and `amdkfd/kfd_device_queue_manager_v9.c`.
- Integrates with SOC15 register helpers, GRBM/SRBM selection, RLC-safe writes, and command stream packet emission. The GDS macros are directly used by `gfx_v9_4_3.c` when clearing per-VMID GDS/GWS/OA access and when emitting GDS resource switches.
- Integrates with KFD because compute VMIDs, shared memory settings, traps, and queue management rely on the same GC 9.4.3 register model.
- Integrates with RAS and debug paths through TCP UTCL1 status, TCP error-injection controls, performance-counter filters, and per-block RAS signature fields.

## Risks and Edge Cases

- Bitfield drift is the main risk. A wrong shift or mask can silently write a valid but incorrect hardware bit, causing VMID isolation failures, resource leakage, wrong depth/stencil behavior, rendering corruption, missed fault detection, or bad diagnostics.
- This chunk is boundary-partial. It begins after the `TCP_UTCL1_CNTL2__SPARE_MASK` line, so the corresponding shifts and first mask for that register are outside the range. It ends before the rest of `SPI_PS_INPUT_CNTL_19` and before `SPI_PS_INPUT_CNTL_20`, so merge tooling must not treat those register groups as complete here.
- Repeated VMID and viewport families are easy to mis-generate. Off-by-one indexing in `GDS_VMIDn`, `GDS_GWS_VMIDn`, `GDS_OA_VMIDn`, `PA_SC_VPORT_*`, `PA_CL_VPORT_*`, or `SPI_PS_INPUT_CNTL_n` definitions would compile cleanly but affect the wrong VMID, viewport, or shader input.
- GDS/GWS/OA fields affect isolation and scheduling. Programming an incorrect base, size, or reset mask can grant a VMID unintended access to shared resources or break HWS/KFD context save/restore assumptions.
- DB/CB/PA/SPI fields are high visual-correctness risk. Errors in depth/stencil formats, compression metadata, scissor bounds, viewport transform, raster configuration, color masks, DCC control, or interpolation control can produce subtle rendering defects rather than immediate failures.
- Status, signature, and injection fields mix observation and control. This header does not distinguish passive status bits from destructive reset or injection controls, so caller-side discipline and hardware documentation are required.

## Test Signals

- Build AMDGPU/KFD with GC 9.4.3 enabled to catch missing, renamed, or duplicate macro definitions and mismatches with token-pasting register helpers.
- Generated-header validation should compare this chunk against the authoritative GC 9.4.3 register database and verify every `__SHIFT`/`_MASK` pair, repeated VMID family, viewport family, and `SPI_PS_INPUT_CNTL_n` family.
- Runtime GC 9.4.3 smoke should boot, submit graphics and compute queues, exercise VMID allocation, KFD queue creation, suspend/resume, and GPU reset while checking for VM faults, hangs, and RAS warnings.
- GDS-specific tests should verify initialization clears non-VMID0 GDS/GWS/OA access, firmware can enable target compute VMIDs, and ring-emitted GDS switches program expected base/size values.
- Graphics validation should include depth/stencil clears, decompression, stencil masks, DCC behavior, scissor and viewport clipping, clip planes, blend constants, color target masks, and pixel shader input interpolation.
- RAS/debug validation should inspect `TCP_UTCL1_STATUS`, TCP performance counter filters, error-injection paths, and `RAS_*_SIGNATURE*` decoding against known-good hardware traces or injected faults.

### subset-b-002693: lines 19507-21915

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 19507-21915

## Scope

This chunk covers a generated shift/mask section of the GC 9.4.3 AMD GPU register bitfield header. It starts in the middle of the `SPI_PS_INPUT_CNTL_19` definition, covers full definitions for `SPI_PS_INPUT_CNTL_20` through `SPI_PS_INPUT_CNTL_31`, then spans shader interpolation/output controls, color blend state, VGT draw and geometry/tessellation state, depth/stencil and rasterizer state, streamout state, multisample sample-location state, primitive binning/conservative rasterization state, and the beginning of the per-render-target color-buffer descriptor families through `CB_COLOR3_DCC_CONTROL`.

The file is generated hardware ABI data. This chunk contains only C preprocessor constants in the standard AMDGPU form:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

There are no functions, structs, variables, dynamic allocations, or executable control flow in this chunk.

## Purpose

The purpose of this chunk is to describe how GC 9.4.3 graphics pipeline state is packed into 32-bit hardware registers. AMDGPU and KFD code include the matching `gc_9_4_3_offset.h` and `gc_9_4_3_sh_mask.h` pair so register helper macros can address a register and compose or decode its fields without hard-coded bit positions.

The fields here are largely context/draw state: pixel shader input interpolation, render-target blend and color-buffer layout, draw initiator and index-buffer parameters, primitive assembly, clipping, rasterization, depth/stencil, MSAA/EQAA sample layout, streamout, tessellation, geometry shader ring sizing, NGG-related controls, and CB metadata/compression addresses for MRTs 0 through the start of MRT 3.

## Important Macro Families

### Pixel Shader Input and SPI State

`SPI_PS_INPUT_CNTL_20` through `SPI_PS_INPUT_CNTL_31` continue the per-attribute pixel shader input map. Each register defines fields such as `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, and validity bits for attribute lanes. These fields control how interpolated vertex outputs are routed into pixel shader inputs and how missing/default attributes are supplied.

`SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, and `SPI_PS_INPUT_ADDR` describe shader output/input export masks. `SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR` each expose 32 single-bit fields, one for every pixel shader input slot, and are paired with the `SPI_PS_INPUT_CNTL_*` attribute descriptors.

`SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL` define interpolation/barycentric behavior, pixel parameter generation, front-face and ancillary slot locations, position/parameter offset controls, and perspective/linear centroid or sample barycentric enables. `SPI_TMPRING_SIZE`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` describe scratch/temp ring sizing and shader export format selection for position, depth, stencil/sample mask, and color targets.

### Color Blend and Render Target State

`CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` define independent MRT blend state. Each target has source/destination blend factors and combine functions for color and alpha, plus `SEPARATE_ALPHA_BLEND`, `ENABLE`, and `DISABLE_ROP3` bits.

`CB_COLOR_CONTROL` defines global color-buffer mode controls including dual-quad disable, degamma enable, color mode, and ROP3 operation. `CB_MRT0_EPITCH` through `CB_MRT7_EPITCH` define extended pitch for each MRT.

The end of the chunk begins full per-MRT color descriptors:

- `CB_COLOR0_BASE/BASE_EXT`, `CB_COLOR1_*`, `CB_COLOR2_*`, and the start of `CB_COLOR3_*` carry 256-byte aligned base addresses.
- `CB_COLORn_ATTRIB2` carries mip0 height, mip0 width, and max mip.
- `CB_COLORn_VIEW` carries slice start/max and mip level.
- `CB_COLORn_INFO` carries endian, format, number type, component swap, fast clear, compression, blend behavior, DCC enable, FMASK controls, and CMASK address type.
- `CB_COLORn_ATTRIB` carries mip0 depth, metadata linearity, sample/fragment counts, swizzle modes, resource type, and RB/pipe alignment.
- `CB_COLORn_DCC_CONTROL` carries DCC overwrite/key-clear/block-size/color-transform/independent-block/lossy precision/constant-encode controls.
- `CB_COLORn_CMASK`, `FMASK`, clear words, and DCC base/base-ext registers carry color metadata, FMASK, clear color, and DCC metadata addresses.

This chunk ends partway through `CB_COLOR3_DCC_CONTROL`; the remaining masks for that register and later MRTs belong to the next chunk.

### Draw, VGT, Tessellation, Geometry, and Streamout State

`VGT_DMA_BASE`, `VGT_DMA_BASE_HI`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, and `VGT_DMA_NUM_INSTANCES` encode index-buffer addressing, index count, index type/swap mode, request policy, primitive generator enablement, and instancing count.

`VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_EVENT_INITIATOR`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_DISPATCH_DRAW_INDEX`, and `VGT_DMA_EVENT_INITIATOR` describe draw/event packet payload fields: draw source and major mode, not-EOP behavior, register render-target index, immediate data, event type/address, object/primitive ID payload enables, and dispatch draw index.

The geometry/tessellation block includes `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, tessellation min/max levels and distribution, `VGT_GROUP_*` primitive/vector controls, `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, GS/ES/VS ring item sizes and offsets, `VGT_GS_OUT_PRIM_TYPE`, `VGT_GS_MAX_PRIMS_PER_SUBGROUP`, `VGT_GS_MAX_VERT_OUT`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TF_PARAM`, `VGT_GS_INSTANCE_CNT`, and `VGT_PRIMITIVEID_*`. These fields configure which hardware shader stages are active, how many vertices/primitives are grouped, how GS/ES/LS/HS rings are sized, what primitive topology is emitted, and how primitive IDs reset or propagate.

`VGT_STRMOUT_*` registers define streamout buffer size, vertex stride, buffer offset for four streamout buffers, opaque draw offset/filled size/stride, streamout rasterization disable, primitive-needed/count-needed enables, and per-buffer streamout enable state.

### Depth, Stencil, HTILE, and Shader Depth Interaction

`DB_DEPTH_CONTROL` controls stencil enable, Z enable, Z writes, depth bounds, depth compare function, backface stencil, and color-write behavior on depth pass/fail. `DB_SHADER_CONTROL` controls shader depth/stencil/mask exports, Z ordering, kill/coverage-to-mask behavior, execution on hierarchical depth outcomes, depth-before-shader, conservative Z export, POPS, and overlap execution.

`DB_EQAA`, `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK` define EQAA sample counts, HTILE preload/cache/alignment behavior, shader-result compare tests, preload windows, and alpha-to-mask behavior. These fields are central to depth/stencil correctness and multisample coverage semantics.

### PA/SC Rasterization, Clipping, Viewport, and Multisample State

The PA/SC blocks describe front-end rasterization state:

- `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, and guard-band adjustment registers control clipping, viewport transform enables, VS export interpretation, NaN/Inf handling, cull/clip distances, and guard-band clip/discard extents.
- `PA_SU_SC_MODE_CNTL`, point/line/polygon offset controls, `PA_SU_LINE_STIPPLE_*`, `PA_SU_PRIM_FILTER_CNTL`, `PA_SU_SMALL_PRIM_FILTER_CNTL`, `PA_SU_POINT_*`, `PA_SU_LINE_CNTL`, and `PA_SU_VTX_CNTL` define culling, polygon mode, polygon offset, point/line sizes, stipple, primitive filtering, provoking vertex, and pixel-center/rounding behavior.
- `PA_SC_MODE_CNTL_0`, `PA_SC_MODE_CNTL_1`, `PA_SC_LINE_STIPPLE`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL` define scan converter MSAA, tile walk/binning, line stipple, sample count, sample mask, shader collision instrumentation, primitive binning, conservative rasterization, and NGG mode behavior.
- `PA_SC_AA_SAMPLE_LOCS_PIXEL_*` registers encode 16 sample X/Y positions for each 2x2 pixel quadrant, and `PA_SC_AA_MASK_*` encodes per-quadrant AA masks.

These masks are consumed by command submission and clear-state paths to establish the exact fixed-function rasterization contract expected by user-mode graphics drivers.

## Control Flow and State Behavior

This header has no control flow. Its effect is compile-time substitution into code that reads and writes GPU MMIO or packetized context registers. Runtime sequencing is owned by the AMDGPU/KFD callers and firmware-visible command streams.

The state described here is persistent GPU context state until overwritten by another context/state packet, reset by clear-state programming, or changed by firmware/driver initialization. Important persistent state includes shader input interpolation mappings, shader export formats, blend factors and color control, draw/index-buffer descriptors, depth/stencil compare/write policy, rasterizer culling and clipping policy, tessellation/geometry shader ring sizing, streamout buffer setup, multisample sample locations and masks, primitive binning/conservative rasterization settings, and color target/metadata base addresses.

Some fields are command-like or event payload fields rather than long-lived configuration, such as `VGT_DRAW_INITIATOR`, `VGT_EVENT_INITIATOR`, `VGT_DMA_EVENT_INITIATOR`, and `CS_COPY_STATE`/`GFX_COPY_STATE` source-state IDs. Others describe memory-backed render state and must remain synchronized with buffer object addresses, tiling/swizzle metadata, DCC/CMASK/FMASK allocation, and pipe/RB alignment assumptions.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention. The sibling `gc_9_4_3_offset.h` provides register addresses such as the `reg*` names, and this file provides field positions/masks for those addresses. AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and packet/context-state emission code consume these masks.

Direct source-tree inclusion points for this GC 9.4.3 mask header include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c`
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c`
- `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c`

The same register names also appear in clear-state tables for nearby generations, which shows how these fields map to context-state programming for graphics pipeline reset/default state. For GC 9.4.3 specifically, the masks are part of the graphics IP support layer and are coupled to KFD queue management, GFX initialization, GPUVM/GFXHUB setup, and user-mode driver command streams that emit the corresponding context registers.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can silently program unrelated graphics state, causing rendering corruption, GPU hangs, incorrect depth/stencil behavior, or invalid memory addresses for color metadata.
- The many repeated families are easy to corrupt mechanically. `SPI_PS_INPUT_CNTL_n`, `CB_BLENDn_CONTROL`, `PA_SC_AA_SAMPLE_LOCS_*`, streamout buffer triplets, and `CB_COLORn_*` families are regular but not interchangeable across all fields.
- Color-buffer address and metadata fields are memory-safety sensitive. Bad `BASE`, `BASE_EXT`, `CMASK`, `FMASK`, or `DCC_BASE` masks can direct hardware to the wrong memory or misinterpret compression metadata.
- DCC/CMASK/FMASK and alignment bits must match surface creation metadata. Mismatched swizzle, sample count, fragment count, resource type, RB alignment, or pipe alignment can produce corruption that is workload-dependent.
- Rasterization and depth/stencil fields interact with API-visible semantics. Errors in clip control, viewport transform, conservative rasterization, sample locations, alpha-to-mask, depth-before-shader, or stencil/Z functions can pass simple smoke tests while failing conformance.
- Draw/VGT fields control packet interpretation and geometry-stage sizing. Invalid index type, draw source, shader-stage enablement, GS/ES ring item size, tessellation factor mode, or streamout stride/offset can break command streams or hang geometry processing.
- The chunk starts and ends mid-family: it starts after most of `SPI_PS_INPUT_CNTL_19` and ends inside `CB_COLOR3_DCC_CONTROL`. The merge lane must reconcile adjacent chunks for complete per-register coverage.

## Test and Validation Signals

Useful validation is mostly build, conformance, and hardware execution coverage:

- Build AMDGPU and KFD paths that include `gc/gc_9_4_3_sh_mask.h`; this catches missing or renamed macro definitions.
- Run graphics clear-state and context-switch tests that exercise default programming for SPI, CB, DB, PA/SC, and VGT context registers.
- Run draw tests covering indexed/non-indexed draws, instancing, primitive restart/primitive ID, tessellation, geometry shader output, NGG mode, streamout, and event packets.
- Run render-target tests across multiple MRTs, blend modes, ROP3, formats, component swaps, DCC enabled/disabled, CMASK/FMASK, fast clear, MSAA/EQAA sample counts, and mipped/sliced render targets.
- Run depth/stencil tests covering depth bounds, front/back stencil, shader depth exports, early/late Z, alpha-to-mask, HTILE preload, and shader-result compare state.
- Run rasterization conformance for clipping, culling, guard bands, viewport transform, line/point/polygon offset, small primitive filtering, conservative rasterization, binning, sample locations, and sample masks.
- For GC 9.4.3 multi-die/accelerator configurations, include KFD queue and compute coexistence workloads to ensure graphics context-state definitions remain compatible with queue management and reset paths.

### subset-b-002694: lines 21916-24636

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 21916-24636

## Scope

This chunk is part of the generated AMD GC 9.4.3 shift/mask register header. It contains preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit MMIO register values.

The range starts in the middle of the `CB_COLOR3_DCC_CONTROL` family, covers most of the color-buffer target slots 4 through 7, then spans these generated address blocks:

- `xcd0_gc_gfxudec`: command processor, graphics pipeline, shader trace/cache, depth/color query, GDS, and SPI control fields.
- `xcd0_gc_gccanedec`: GC CANE correctable/uncorrectable error status fields.
- `xcd0_gc_perfddec`: performance counter data registers for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, and RMI.
- `xcd0_gc_utcl2_atcl2pfcntrdec`, `xcd0_gc_utcl2_vml2prdec`, and `xcd0_gc_utcl2_l2tlbprdec`: UTCL2/VM L2/L2TLB performance counter data fields.
- `xcd0_gc_perfsdec`: the beginning of performance counter selector/control fields for CPG, CPC, CPF, CP perfmon, CP draw-window filtering, and the first portion of `GRBM_PERFCOUNTER0_SELECT`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_9_4_3_sh_mask.h` is the bit-level ABI between GC 9.4.3 driver code and AMD graphics hardware registers. The sibling `gc_9_4_3_offset.h` header supplies register offsets such as `regCB_COLOR4_INFO`, `regCP_COHER_CNTL`, `regSQ_THREAD_TRACE_CTRL`, `regGDS_ATOM_CNTL`, `regCP_PERFMON_CNTL`, and `regGRBM_PERFCOUNTER0_SELECT`; this header supplies the field positions and masks used with those offsets.

Driver code consumes these definitions through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `SOC15_REG_OFFSET`, command-stream packets, and register dump/debug tooling. The macros also allow common code to share field names across ASIC-specific generated headers while still using the correct GC 9.4.3 layout.

## Important Macro Families

### Color Buffer Targets

The opening section completes the tail of `CB_COLOR3_DCC_CONTROL` and the remaining `CB_COLOR3_*` metadata registers, then defines `CB_COLOR4_*` through `CB_COLOR7_*`. These families describe render-target state:

- `*_BASE` and `*_BASE_EXT` carry the low and high portions of 256-byte-aligned color surface base addresses.
- `*_ATTRIB2`, `*_VIEW`, `*_INFO`, and `*_ATTRIB` encode mip dimensions, slice ranges, mip level, format, numeric type, component swap, fast clear, compression, DCC enable, CMASK address type, sample/fragment count, color/FMASK swizzle mode, resource type, and RB/pipe alignment.
- `*_DCC_CONTROL` contains DCC policy fields such as overwrite combiner disable, key-clear enable, compressed and uncompressed block sizes, color transform, independent 64-byte blocks, lossy precision, and constant encode controls.
- `*_CMASK`, `*_FMASK`, `*_CLEAR_WORD*`, and `*_DCC_BASE` provide metadata-surface base addresses and clear words.

These definitions are context/render-target state, not general software data structures. Incorrect masks can make render-target programming write the wrong surface address, format, compression mode, or metadata layout.

### Command Processor And Coherency Windows

The `xcd0_gc_gfxudec` block starts with CP end-of-pipe, stream-out, primitive counter, pipe-stat, scratch, append/fence, semaphore, atomic pre-operation, memory read/write, and DMA fields. Most low/high address or counter registers are full-width `0xFFFFFFFFL` fields, while control registers expose narrower command bits.

Important CP control families include:

- `CP_PIPE_STATS_CONTROL`, `CP_STREAM_OUT_CONTROL`, and `CP_STRMOUT_CNTL`, which gate pipeline statistics and stream-out accounting.
- `SCRATCH_REG0..7`, `SCRATCH_UMSK`, and `SCRATCH_ADDR`, which define CP scratch data, user mask, and scratch address selection.
- `CP_SIG_SEM_ADDR_*`, `CP_WAIT_SEM_ADDR_*`, `CP_SEM_WAIT_TIMER`, and `CP_WAIT_REG_MEM_TIMEOUT`, which support semaphore and wait-reg-mem sequencing.
- `CP_DMA_ME_*`, `CP_DMA_PFP_*`, and `CP_DMA_CNTL`, which describe CP DMA source/destination addresses, commands, byte counts, SA/DA increment behavior, raw-wait, disable-write-confirm, and read-tag state.
- `CP_COHER_*` and `CP_ME_COHER_*`, which define coherency operation base, size, control, status, engine/VMID bits, cache action bits, GL2 probe behavior, and destination base state.
- `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, command-buffer offsets/sizes, CE/IB base registers, EOP done event/data controls, metadata base registers, indirect draw/dispatch addresses, index base/type, GDS backup base, and sample status fields.

The command processor fields connect directly to ring execution, indirect buffer setup, event/fence completion, cache flush/invalidate sequencing, and low-level synchronization. The header has no sequencing logic; the owning CP/GFX code must still order writes, waits, and polling correctly.

### Graphics Pipeline, Shader Trace, SQC, DB, And GDS

The same block includes front-end and shader/debug controls:

- `RLC_GPM_PERF_COUNT_0/1` expose GPM performance counter and read-valid/counter-valid status fields.
- `GRBM_GFX_INDEX` selects SE/SA/instance targeting and broadcast modes for indexed graphics register access.
- `VGT_*`, `IA_MULTI_VGT_PARAM`, and `WD_*` fields cover primitive type, index type, stream-out buffer filled sizes, vertex-index bounds, primitive reset enable, draw instance/index counts, tessellation ring and offchip parameters, and work distributor buffer bases.
- `PA_SC_*`, `PA_SU_LINE_STIPPLE_VALUE`, and stereo/trap screen fields describe line stipple, screen extents, and raster/trap-screen debug counters.
- `SQ_THREAD_TRACE_*` fields define shader thread-trace base/size, token and performance masks, control/status, mode, write pointer, hi-water mark, counter, and userdata registers.
- `SQC_CACHES` and `SQC_WRITEBACK` expose shader instruction/cache invalidation, volatile behavior, client selection, force bits, writeback, and completion status.
- `DB_OCCLUSION_COUNT*` and `DB_ZPASS_COUNT*` provide query counter low/high fields.
- `GDS_RD_*`, `GDS_WR_*`, `GDS_WRITE_COMPLETE`, `GDS_ATOM_*`, and `GDS_GWS_*` fields describe GDS direct read/write, burst access, atomic operation setup/completion/readback, global-wave-sync resource selection, ownership/mask/counter state, and ordered-append ring control/address/incdec/ring size.
- `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, and `SPI_WAVE_LIMIT_CNTL` define shader processor interface policy such as GPR write priority, export priority order, SQG event enables, resource-management reset, thread-trace stall, allocation/export arbitration, pixel shader packer priority, PC-limit behavior, CRC/LBPW checks, CSG/CSC power-save disables, context-save wait overheads, and wave-slot limits.

These fields are a mix of persistent configuration, hardware-updated status, and command-like bits. Trace, cache, GDS atomic, and ordered-append registers are especially side-effect-prone because they represent active hardware engines rather than passive metadata.

### GC CANE Error Status

The `xcd0_gc_gccanedec` block defines `GC_CANE_ERR_STATUS`, `GC_CANE_UE_ERR_STATUS_LO/HI`, and `GC_CANE_CE_ERR_STATUS_LO/HI`. These fields expose GC CANE correctable and uncorrectable error bits across shader and graphics blocks, including CPF/CPC/CPG, TCP, SQ, SPI, TA, TD, WD, IA, VGT, PA_SC, PA_SU, DB, CB, SX, and GDS-style sources.

These masks are diagnostic and RAS-facing integration points. They can be used to decode hardware error status words, but this header does not define clear semantics, interrupt routing, recovery policy, or whether individual bits are sticky.

### Performance Counter Data

The `xcd0_gc_perfddec` and UTCL2-related blocks are dominated by low/high performance counter data registers. Families include:

- CP front-end counters: `CPG`, `CPC`, `CPF`, plus latency-stat data.
- Global and per-SE GRBM counters.
- Pipeline counters for `WD`, `IA`, `VGT`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, `SX`, `GDS`, `TA`, `TD`, `TCP`, `TCC`, `TCA`, `CB`, `DB`, `RLC`, and `RMI`.
- UTCL2, VM L2, and L2 TLB counters: `ATC_L2_PERFCOUNTER_*`, `MC_VM_L2_PERFCOUNTER_*`, and `L2TLB_PERFCOUNTER_*`.

Most low registers expose a full-width `PERFCOUNTER` or `COUNTER_LO` field. High registers often split the low 16 bits of counter high data from a high-half `COMPARE_VALUE` field. Consumers need a coherent read strategy outside this header when sampling split 64-bit counters that may update while being read.

### Performance Counter Selection And Draw Filtering

The `xcd0_gc_perfsdec` portion begins performance-counter selector state:

- `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, and `CPF_PERFCOUNTER*` selector registers pack `CNTR_SEL*`, `SPM_MODE`, and `CNTR_MODE*` fields.
- `CP_PERFMON_CNTL` controls CP perfmon state, SPM perfmon state, enable mode, and sample-enable behavior.
- `CPF_TC_PERF_COUNTER_WINDOW_SELECT` and `CPG_TC_PERF_COUNTER_WINDOW_SELECT` choose TC performance counter windows with `INDEX`, `ALWAYS`, and `ENABLE` bits.
- `CPF_LATENCY_STATS_SELECT`, `CPG_LATENCY_STATS_SELECT`, and `CPC_LATENCY_STATS_SELECT` choose latency-stat slots and expose `CLEAR` and `ENABLE` bits.
- `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` provide draw-object and draw-window filtering controls for performance/debug measurement.
- The chunk ends in the first half of `GRBM_PERFCOUNTER0_SELECT`, after the busy-mask shift fields through `EA_BUSY_USER_DEFINED_MASK__SHIFT`; the corresponding `RMI` shift and all masks are in the following lines/chunk.

These selector fields configure what the data counters in the preceding block measure. They are persistent profiling/debug configuration until reset or reprogrammed.

## Control Flow

There is no runtime control flow in this chunk. It contains no C functions, structs, variables, allocations, locks, callbacks, loops, or branches. Its behavior is compile-time macro substitution.

The implied runtime flow is:

1. GC 9.4.3 driver code includes `gc_9_4_3_offset.h` and `gc_9_4_3_sh_mask.h`.
2. A call site chooses the relevant `reg*` offset for the active register.
3. The call site uses these `__SHIFT` and `_MASK` macros through helper macros or manual bit operations to compose, update, or decode a 32-bit register value.
4. The value is read or written through SOC15 MMIO helpers, RLC-safe accessors, packetized command streams, debug/register-dump code, KFD queue-management code, or profiling tooling.

Any real ordering, polling, W1C/W1S behavior, latching, privilege checks, XCC instance selection, or timeout policy lives in the surrounding AMDGPU/KFD code and hardware specification, not in this generated header.

## State And Persistence Behavior

The macros themselves hold no software state and persist nothing. They describe hardware-visible state:

- Color-buffer base, view, format, compression, DCC, CMASK, FMASK, and clear-word registers persist as render-target context state until changed by command streams, context restore, reset, or clear-state setup.
- CP scratch, append/fence, semaphore, atomic, DMA, IB, coherency, metadata, indirect draw/dispatch, index, GDS backup, and EOP registers represent command processor execution and synchronization state. Some are software-programmed, some are hardware-updated completion/status words.
- Shader trace, SQC cache, SPI control, GDS atomic/GWS/OA, DB query counters, and PA/SC trap-screen fields are active debug, cache, synchronization, and query surfaces with side effects.
- CANE error registers represent hardware error status and may contain sticky or latched bits depending on the underlying register semantics.
- Performance counter selector and control registers persist as measurement configuration. Counter data registers are hardware-updated while active, and low/high halves can race unless sampled using the correct hardware sequence.

Reserved fields and non-covered bits should be preserved in read-modify-write sequences unless the driver is deliberately writing a known full-register value from an authoritative table.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h`, which supplies the matching register offsets and base indices. `gc_9_4_3_default.h` and generation-adjacent enum headers provide reset/default values or selector enumerations where available.

Observed integration points in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`, which includes this header with `gc_9_4_3_offset.h` for GC 9.4.3 initialization, register lists, queue setup, RLC/GFX handling, XCC-aware access, and diagnostics.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c`, which includes `gc/gc_9_4_3_sh_mask.h` for GCVM/gfxhub register field programming and decoding on this ASIC family.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c`, which include the same generated header for KFD/compute queue and GC 9.4.3 integration.
- Common AMDGPU helpers and command definitions in SOC15-era code, including register read/write helpers and packet definitions for copying perf counters or GDS atomic return data.
- Clear-state and context-state paths for render targets, which rely on matching CB register offsets/masks when restoring graphics context state.
- Profiling, debugfs, register-dump, RAS, GPU reset, suspend/resume, and bring-up code paths that read or program CP, SQ trace, SQC cache, SPI, GDS, CANE, and performance-monitoring registers.

Cross-generation similarity is high but not exact. Nearby GC 9.0, GC 10.x, GC 11.x, and GC 12.x headers expose many similarly named fields, but masks, offsets, address-block names, and complete register coverage can differ. Consumers must include the GC 9.4.3 header set that matches the active ASIC.

## Risks And Edge Cases

- Generated bitfield drift is the central risk. A wrong mask or shift compiles cleanly but can program unrelated hardware bits, leading to rendering corruption, hangs, bad synchronization, invalid profiling data, or broken recovery paths.
- This chunk starts mid-register at `CB_COLOR3_DCC_CONTROL` and ends mid-register at `GRBM_PERFCOUNTER0_SELECT`. The final merged report must join adjacent chunks before describing those two register families as complete.
- Color-buffer target slots 4 through 7 are highly repetitive. Mechanical generation or copy errors can affect only one MRT slot and show up as format, DCC, CMASK/FMASK, clear, or base-address bugs under multi-render-target workloads.
- Address high/low registers commonly encode aligned addresses rather than byte addresses. Callers must respect hardware granularity such as 256-byte base fields and not treat every field as a raw byte pointer.
- CP coherency, DMA, semaphore, wait, EOP, and indirect-buffer registers have strict sequencing requirements. The masks do not encode cache flush ordering, wait conditions, timeout handling, or engine ownership.
- GDS atomic, ordered append, GWS resource, and write-complete fields can be active command surfaces. Treating command/status bits as inert configuration can corrupt synchronization or return data.
- SQ thread trace and SQC cache control fields are debug/cache-management surfaces. Bad masks can stall shader execution, miss trace data, or leave stale instruction/data cache state.
- CANE error-status fields are RAS-sensitive. Mis-decoding correctable versus uncorrectable error status can hide real hardware faults or trigger unnecessary recovery.
- Performance counter data and select fields are dense and repeated. Wrong selector, mode, SPM, window, latency-stat, or draw-window masks can silently collect plausible but incorrect measurements.
- Low/high counter pairs can race with hardware updates. This header provides bit positions only, not a latching or retry algorithm.
- `GRBM_GFX_INDEX` and per-SE/SA targeting fields affect which graphics instance is addressed. Incorrect broadcast or instance selection can write only part of a multi-XCC/multi-SE device or unintentionally broadcast to all instances.

## Test And Validation Signals

Useful validation is a mix of generated-data checks, build coverage, and hardware-oriented runtime behavior:

- Build AMDGPU and KFD code paths that include `gc/gc_9_4_3_sh_mask.h`, including `gfx_v9_4_3.c`, `gfxhub_v1_2.c`, `amdgpu_amdkfd_gc_9_4_3.c`, and `kfd_device_queue_manager_v9.c`. Missing or renamed macros should fail at compile time.
- Mechanically compare this chunk against AMD's authoritative GC 9.4.3 register database. Each complete register in the range should have paired `__SHIFT` and `_MASK` entries, aligned masks, and matching offsets in `gc_9_4_3_offset.h`.
- Run static sanity checks for repeated CB slots 4-7, CP counter pairs, GDS fields, and performance counter families to catch one-slot or one-counter layout drift.
- Exercise graphics render-target workloads with multiple color attachments, DCC/FMASK/CMASK paths, fast clears, MSAA, mip/slice views, and context save/restore. Expected signals are correct rendering and no metadata corruption.
- Exercise CP DMA, wait-reg-mem, semaphore, fence/EOP, coherency, indirect draw/dispatch, stream-out, and query paths. Watch for hangs, timeouts, stale cache contents, missing fences, or wrong primitive/query counts.
- Exercise SQ thread trace and SQC cache invalidation/writeback flows where supported. Expected signals are valid trace buffers, correct write pointers/status, and no shader execution stalls outside intended trace control.
- Exercise GDS atomic/GWS/ordered-append behavior through compute and graphics workloads that use append/consume, atomics, and GDS backup/restore. Expected signals are correct synchronization and returned atomic data.
- Run RAS/error-injection or register-decode tests for GC CANE correctable and uncorrectable status where hardware or simulation support exists.
- Run profiling validation that programs CPG/CPC/CPF selectors, CP perfmon state, latency stats, draw-window filters, and the covered data counters. Counter movement should match controlled graphics, compute, memory, and shader workloads.
- On multi-XCC or partitioned GC 9.4.3 systems, validate instance-targeted register access through `GRBM_GFX_INDEX` and XCC-aware AMDGPU helpers so that reads/writes reach the intended hardware instance.

## Cross-Chunk Notes

The previous chunk owns the beginning of `CB_COLOR3_DCC_CONTROL`; this range begins with its later shift/mask fields and then continues into `CB_COLOR3_CMASK`. The next chunk owns the remainder of `GRBM_PERFCOUNTER0_SELECT`, starting after `EA_BUSY_USER_DEFINED_MASK__SHIFT`, including the `RMI` shift and all masks. The merge/reconciliation lane should stitch these artificial boundaries before producing the final per-file research document.

### subset-b-002695: lines 24637-27087

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 24637-27087

## Scope

This chunk covers generated shift and mask macros for GC 9.4.3 graphics-core registers. It begins in the tail of `GRBM_PERFCOUNTER0_SELECT`, continues through broad performance counter selector coverage, and ends inside the `RLC_SRM_RLCV_COMMAND` field list. The covered range includes:

- Global and per-shader-engine GRBM performance counter selector fields.
- WD, IA, VGT, PA_SU, PA_SC, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, RMI, ATC_L2, MC_VM_L2, and L2TLB performance counter configuration fields.
- RLC streaming performance monitor ring, segment, mux select, sample delay, and memory-client/interrupt controls.
- RLC GPU IOV performance counter access windows.
- GDFLL EDC hysteresis control and status fields.
- RLC core control, status, safe-mode, SMU/RLCV command, timers, interrupts, load balancing, clock-gating, power-gating, clock counter, GPM thread, serdes, scratch, log, interrupt force/disable, and save/restore memory fields.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only. It contains no C functions, structs, variables, executable branches, or software storage.

## Purpose

The purpose of this header section is to provide the bit-level ABI between GC 9.4.3 hardware registers and AMDGPU/KFD driver code. Each field is represented by the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for extracting or composing that field.

Driver code pairs these macros with register address definitions from `gc_9_4_3_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`. The constants are therefore not business logic by themselves; they are the authoritative encoding used when software programs MMIO state for profiling, power management, virtualization, firmware coordination, and low-level graphics-core control.

## Important Macro Families

### Performance Counter Selection

The first major section is dominated by performance counter selector macros. These registers choose which hardware event each block-local counter observes and how the counter is filtered or counted.

Common selector patterns appear across many blocks:

- `*_PERFCOUNTER0_SELECT` often exposes `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`, supporting packed selection of multiple event lanes plus counter modes.
- Matching `*_PERFCOUNTER0_SELECT1` registers often expose `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`.
- Later counters in the same block may be simpler, with only `PERF_SEL` and `PERF_MODE`.
- Some blocks use narrower event selectors. For example, GRBM uses a 6-bit `PERF_SEL`; SQ uses a 9-bit `PERF_SEL` plus SQC bank/client masks, SPM mode, SIMD mask, and performance mode; CB and RMI selectors use 9-bit event masks.

Covered graphics and shader blocks include GRBM, WD, IA, VGT, PA_SU, PA_SC, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, and RMI. This makes the chunk a central source for profiling and debug paths that program GC 9.4.3 counters.

Specialized control registers in this group include:

- `GRBM_PERFCOUNTER*_SELECT` and `GRBM_SE*_PERFCOUNTER_SELECT`, which combine event selection with user-defined busy/clean masks for major graphics blocks such as DB, CB, VGT, TA, SX, SPI, SC, PA, CP, IA, GDS, RLC, TC, WD, UTCL2, EA, and RMI.
- `VGT_PERFCOUNTER_SEID_MASK`, which filters VGT counting by shader-engine ID.
- `SPI_PERFCOUNTER_BINS`, which defines four min/max bin ranges for SPI counter bucketing.
- `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, and `SQ_PERFCOUNTER_CTRL2`, which gate SQ counting by shader stage, counter rate, flush behavior, VMID mask, shader mask, and forced enable.
- `CB_PERFCOUNTER_FILTER`, which enables and selects operation, format, clear, MRT, sample-count, and fragment-count filters before CB counter samples are accepted.
- `RMI_PERF_COUNTER_CNTL`, which selects transaction/event/TC enables, event windows, CID/VMID filters, burst-length threshold, soft reset, and SPM selection.

### RLC Streaming Performance Monitor

The `RLC_SPM_*` section defines the streaming performance monitor path owned by RLC:

- `RLC_SPM_PERFMON_CNTL` selects ring mode and sample interval.
- `RLC_SPM_PERFMON_RING_BASE_LO`, `_HI`, and `_RING_SIZE` define the capture buffer address and size.
- `RLC_SPM_PERFMON_SEGMENT_SIZE` and `RLC_SPM_SEGMENT_THRESHOLD` describe global and per-SE sample segmentation.
- `RLC_SPM_SE_MUXSEL_ADDR/DATA` and `RLC_SPM_GLOBAL_MUXSEL_ADDR/DATA` provide indirect RAM-style programming windows for sample source mux selections.
- `RLC_SPM_RING_RDPTR` exposes the software-visible read pointer.
- Per-block `RLC_SPM_*_PERFMON_SAMPLE_DELAY` registers tune sample timing for CPG, CPC, CPF, CB, DB, PA, GDS, IA, SC, TCC, TCA, TCP, TA, TD, VGT, SPI, SQG, SX, and RMI.
- `RLC_SPM_PERFMON_SAMPLE_DELAY_MAX` caps the maximum sample delay.
- `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, and `RLC_SPM_INT_STATUS` configure the memory-client attributes and interrupt control/status for SPM output.

These fields are stateful hardware controls: software programs a ring, muxes, segment sizes, and delays, then relies on RLC and hardware blocks to stream samples into memory.

### RLC and IOV Performance Counter Windows

`RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER0_SELECT`, and `RLC_PERFCOUNTER1_SELECT` define RLC-local performance counter state. `RLC_PERFMON_CNTL` exposes a small `PERFMON_STATE` field and a sample-enable bit.

The `RLC_GPU_IOV_PERF_CNT_*` registers expose a virtualization-aware counter access path:

- `RLC_GPU_IOV_PERF_CNT_CNTL` enables, selects mode, and resets the IOV performance counter mechanism.
- `RLC_GPU_IOV_PERF_CNT_WR_ADDR` and `_RD_ADDR` select a VF ID and counter ID.
- `RLC_GPU_IOV_PERF_CNT_WR_DATA` and `_RD_DATA` carry the small per-counter data payload.

These fields are tied to SR-IOV or partitioned-GPU operation and should be treated as privileged RLC/virtualization control, not generic user-facing performance counter state.

### UTCL2, VM L2, and L2TLB Counters

The address-block sections for `xcd0_gc_utcl2_atcl2pfcntldec`, `xcd0_gc_utcl2_vml2pldec`, and `xcd0_gc_utcl2_l2tlbpldec` cover translation and VM-cache performance counters:

- `ATC_L2_PERFCOUNTER0_CFG` and `ATC_L2_PERFCOUNTER1_CFG` select ATC L2 event ranges, modes, enable bits, and clear bits.
- `ATC_L2_PERFCOUNTER_RSLT_CNTL` selects a counter result and defines start/stop triggers, enable-any, clear-all, and stop-on-saturate behavior.
- `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG` provide the same style of selection, mode, enable, and clear fields for VM L2 performance counters.
- `MC_VM_L2_PERFCOUNTER_RSLT_CNTL` controls result selection and aggregate start/stop/clear behavior for the VM L2 group.
- `L2TLB_PERFCOUNTER0_CFG` through `L2TLB_PERFCOUNTER3_CFG` and `L2TLB_PERFCOUNTER_RSLT_CNTL` do the same for L2 TLB events.

These registers connect graphics-core profiling to address translation and VM behavior. They are useful for memory-management performance analysis but can be confused with similarly named GMC/MMHUB counter blocks in other generated headers.

### GDFLL EDC Hysteresis

`GDFLL_EDC_HYSTERESIS_CNTL` and `GDFLL_EDC_HYSTERESIS_STAT` provide graphics dynamic frequency loop fields related to EDC hysteresis:

- `max_hysteresis` configures a hysteresis limit.
- `edc_frequency_status` and `hysteresis_count` report observed status.

These fields are power/frequency-management state and should remain coordinated with the SMU and platform power policy.

### RLC Core, Safe Mode, Timers, and Interrupts

The `xcd0_gc_rlcpdec` portion starts a broad RLC control block:

- `RLC_CNTL` exposes RLC enablement, central queue, RLCM, SRM, clock counter, sleep, save/restore, safe mode, request-table invalidation, register-write gating, and queue-selection fields.
- `RLC_CGCG_CGLS_CTRL_2`, `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL` describe clock-gating, light-sleep, ramp, and override controls.
- `RLC_STAT` and `RLC_GPM_STAT` expose RLC sleep, wait-for-idle, 3D-full, GPM idle, power/clock status, context processing, register save/restore, CU power transitions, clock-gating override status, ROM execution, and power-gating error state.
- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `SMU_RLC_RESPONSE`, `RLC_RLCV_COMMAND`, and `RLC_SMU_MESSAGE` form command/response channels between software, RLC, RLCV, and SMU-controlled safe-mode or command flows.
- `RLC_REFCLOCK_TIMESTAMP_LSB/MSB`, `RLC_GPU_CLOCK_COUNT_LSB/MSB`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_CLK_COUNT_GFXCLK_*`, `RLC_CLK_COUNT_REFCLK_*`, `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32` define timestamp, clock-count capture, run/reset/sample controls, and valid/resync status.
- `RLC_GPM_TIMER_INT_0..3`, `RLC_GPM_TIMER_CTRL`, and `RLC_GPM_TIMER_STAT` define timer intervals, enables, status bits, and enable synchronization.
- `RLC_INT_STAT`, `RLC_GPM_INT_DISABLE_TH0`, `RLC_GPM_INT_FORCE_TH0`, and `RLC_GPM_INT_FORCE_TH1` expose interrupt status and thread-specific interrupt disable/force masks.

Several fields in this group are command-like or latch-like rather than durable configuration. Examples include safe-mode command bits, GPU clock capture, timer status/enable synchronization, interrupt force fields, and clock-count sample/reset bits.

### RLC Power Gating and Load Balancing

The chunk includes many per-CU and graphics power-gating fields:

- `RLC_PG_CNTL` controls graphics power gating, dynamic/static per-CU power gating, graphics pipeline PG, overrides, CP PG disable, CHUB/SMU handshake behavior, clock slowdown on power-up/down, ultra-low-voltage enable, and SMU handshake disable.
- `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_CU_STATUS`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, and `RLC_PG_ALWAYS_ON_CU_MASK` expose or request CU-level power state and masks.
- `RLC_PG_DELAY`, `RLC_PG_DELAY_2`, and `RLC_PG_DELAY_3` tune power-up/down, command propagation, memory sleep, serdes timeout, per-CU timeout, and CGCG-before-CGPG delays.
- `RLC_LB_CNTL`, `RLC_LB_CNTR_MAX`, `RLC_LB_CNTR_INIT`, `RLC_LOAD_BALANCE_CNTR`, `RLC_LB_PARAMS`, `RLC_THREAD1_DELAY`, `RLC_MAX_PG_CU`, and `RLC_AUTO_PG_CTRL` control load-balancing counters and automatic power-gating thresholds.
- `RLC_SMU_GRBM_REG_SAVE_CTRL` starts GRBM register save behavior under SMU/RLC coordination.

These fields describe persistent hardware policy and observed state. Incorrect programming can change power sequencing, CU availability, or clock-gating behavior.

### RLC GPM, Serdes, Scratch, and SRM Access

The tail of the chunk covers RLC internal machinery:

- `RLC_GPM_THREAD_RESET`, `RLC_GPM_THREAD_PRIORITY`, and `RLC_GPM_THREAD_ENABLE` control/reset and prioritize four GPM threads.
- `RLC_GPM_CP_DMA_COMPLETE_T0/T1`, `RLC_UCODE_CNTL`, `RLC_FIREWALL_VIOLATION`, `RLC_GPM_GENERAL_0..7`, `RLC_GPM_SCRATCH_ADDR/DATA`, `RLC_GPM_LOG_SIZE`, `RLC_GPM_LOG_CONT`, `RLC_GPR_REG1`, and `RLC_GPR_REG2` provide firmware-visible completion, control, scratch, log, and general-purpose state.
- `RLC_SERDES_RD_PENDING`, `RLC_SERDES_RD_MASTER_INDEX`, `RLC_SERDES_RD_DATA_0..2`, `RLC_SERDES_WR_CU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK_1`, `RLC_SERDES_WR_CTRL`, `RLC_SERDES_WR_DATA`, `RLC_SERDES_CU_MASTER_BUSY`, `RLC_SERDES_NONCU_MASTER_BUSY`, and `RLC_SERDES_NONCU_MASTER_BUSY_1` define read/write selection, power up/down command bits, command/data payloads, master masks, and busy state for CU and non-CU serdes operations.
- `RLC_MEM_SLP_CNTL` controls memory light-sleep delays and disable controls for IRAM, DRAM, ARAM, and GPR storage.
- `RLC_SRM_CNTL`, `RLC_SRM_ARAM_ADDR/DATA`, `RLC_SRM_DRAM_ADDR/DATA`, `RLC_SRM_GPM_COMMAND`, `RLC_SRM_GPM_COMMAND_STATUS`, and the beginning of `RLC_SRM_RLCV_COMMAND` define save/restore memory enable, auto-increment, indirect ARAM/DRAM address/data access, command queue fields, and FIFO empty/full status.

The chunk ends before the complete `RLC_SRM_RLCV_COMMAND` field set is visible, so any merged file-level report should stitch this section to the next chunk.

## Control Flow and State Behavior

There is no software control flow in this chunk. Its impact is compile-time: C code expands these macros to compose and decode 32-bit MMIO register values.

The state described here lives in hardware. Important state includes performance event selection, counter enable/clear/result selection, RLC SPM ring base/size/read pointer and mux programming, per-block SPM sample timing, RLC/IOV counter windows, translation/cache counter controls, GDFLL EDC hysteresis, RLC enable/safe-mode/SMU command state, RLC timer and interrupt state, clock-count capture state, power-gating and load-balancing policy, GPM thread controls, serdes command/busy state, scratch/log storage, and SRM command FIFO state.

Some fields are persistent configuration until rewritten. Others are status bits, command strobes, reset bits, clear bits, or indirect address/data windows. Consumers must follow the sequencing rules in the owning AMDGPU/KFD code and the hardware specification, especially for safe-mode handshakes, SMU messages, SPM ring setup, result-control clear/enable bits, RLC timer status, serdes read/write busy polling, and SRM FIFO command submission.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `gc_9_4_3_offset.h` supplies the register addresses and base indices for the names whose fields are defined here.
- `gc_9_4_3_default.h` supplies reset/default values where generated for this ASIC.
- AMDGPU helper macros consume the `__SHIFT` and `_MASK` definitions to avoid open-coded bit positions.

Direct includes in this tree show GC 9.4.3 integration through:

- `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`, which includes `gc_9_4_3_offset.h` and `gc_9_4_3_sh_mask.h` for graphics-core initialization and control.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c`, which includes the same GC 9.4.3 headers for GFXHUB-related register programming.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, which bridges AMDGPU and KFD behavior on this generation.
- `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c`, which includes `gc_9_4_3_sh_mask.h` for queue-management register field encodings.

Implied consumers include performance/debug paths that program GC counters and RLC SPM, power-management paths that coordinate RLC/SMU clock and power-gating state, virtualization paths that access RLC GPU IOV counters, and firmware/RLC bring-up paths that enable RLC, check status, manage safe mode, and inspect timer/interrupt/serdes/SRM state.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can program adjacent hardware fields, causing hangs, incorrect counters, bad power sequencing, lost interrupts, broken virtualization accounting, or firmware/RLC failures.
- Repeated performance-counter families are mechanically similar but not identical. Selector width and presence of `PERF_SEL1`, `SELECT1`, `CNTR_MODE`, filters, and SPM mode fields vary by block.
- The chunk starts and ends mid-family. It begins after `GRBM_PERFCOUNTER0_SELECT` has already started and ends inside `RLC_SRM_RLCV_COMMAND`, so consumers of generated documentation must reconcile adjacent chunks before treating either family as complete.
- RLC SPM setup combines address/data windows, ring memory, mux RAM, segment sizing, sample delays, and interrupt controls. Missing ordering or pointer handling can produce corrupt samples or stalled collection.
- Counter result-control registers contain enable, clear, start/stop trigger, and stop-on-saturate fields. Treating clear or enable bits as ordinary passive state can disrupt profiling.
- RLC safe-mode, SMU message, RLCV command, and SRM/serdes fields are handshake-oriented. They require polling and timeout policy outside this header.
- Power-gating and clock-gating fields are platform-sensitive. Incorrect `RLC_PG_CNTL`, delay, CU mask, load-balancing, or clock-count control programming can affect power transitions, CU availability, or suspend/resume stability.
- Virtualization-related IOV performance counter fields are privilege-sensitive and should remain isolated to PF/hypervisor-aware paths.

## Test and Validation Signals

Useful validation is mostly integration-oriented:

- Build coverage for AMDGPU and KFD code that includes `gc_9_4_3_sh_mask.h`; this catches missing or renamed macros and incompatible generated headers.
- GC 9.4.3 bring-up, reset, suspend/resume, and RLC firmware tests should exercise `RLC_CNTL`, `RLC_STAT`, safe-mode registers, SMU/RLCV command paths, timers, interrupts, and GPM status.
- Performance counter tests should program representative counters across GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA/TD/TCP/TCC/TCA, CB/DB, RLC, RMI, ATC_L2, MC_VM_L2, and L2TLB, then verify expected event increments and result-control clear/enable behavior.
- RLC SPM validation should check ring base/size setup, mux select programming, segment sizing, read-pointer movement, per-block sample delays, interrupt status, and memory-client attributes.
- Power-management tests should cover RLC clock-gating, graphics power-gating, per-CU power-gating masks, auto-PG thresholds, clock-count capture, and SMU handshake behavior.
- SR-IOV or partitioning tests should verify the RLC GPU IOV performance counter address/data windows use the correct VF ID and counter ID fields.
- Low-level RLC diagnostic tests should exercise serdes busy polling, read/write data selection, GPM scratch/log access, SRM ARAM/DRAM indirect windows, and SRM command FIFO empty/full status.

## Unresolved Cross-Chunk References

The first visible line is the final shift definition for `GRBM_PERFCOUNTER0_SELECT`; the earlier fields in that register are in the previous chunk. The last visible lines are the beginning of `RLC_SRM_RLCV_COMMAND` and stop after `RLC_SRM_RLCV_COMMAND__RESERVED_16_MASK`; the remaining fields and masks for that command register are in the next chunk. The merge/reconciliation lane should combine adjacent chunk reports before producing a final file-level document.

### subset-b-002696: lines 27088-29458

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 27088-29458

## Scope

This chunk is a generated AMD GC 9.4.3 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are exposed as `__SHIFT` and `__MASK` macros for composing or decoding 32-bit register values. There are no functions, structs, enums, includes, branches, allocations, locks, callbacks, or file/network persistence behavior in this range.

The selected lines start in the middle of `RLC_SRM_RLCV_COMMAND`, carrying only the final `START_OFFSET`, reserved, and `DEST_MEMORY` masks from that register. The chunk then covers a broad RLC block for SRM command/status, indexed SRM control windows, SMU command arguments, GPM/SPM UTCL1 controls and error capture, semaphores, interrupts, prewalker controls, UTCL2/R2I/LB/DS controls, GPU clock counters, RLC CPG invalidation, UE/CE error status, DSM irritator and error-injection controls, and the RLC SMU clock request bit. It then crosses the `addressBlock: xcd0_gc_pwrdec` marker into CGTS power/clock-gating controls, including global CGTS state-machine/readback/TCC-disable registers, per-CU subblock controls for CUs 0-15, and the beginning of the per-CU TCPI control sequence through the first three fields of `CGTS_CU9_TCPI_CTRL_REG`.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 9.4.3 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_9_4_3_sh_mask.h` supplies bit layouts for GC 9.4.3 registers. Driver code pairs these field definitions with register addresses from the matching offset header and, where generated, reset/default values from the matching default header. Consumers typically use AMDGPU helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, or equivalent generated-register helpers, to pack field values before MMIO, indexed register, or command-stream access.

This slice focuses on two related but distinct hardware surfaces:

- RLC service, microcontroller, memory-management, interrupt, error-reporting, and diagnostic controls. The RLC block defines command/status fields for SRM/RLCV operations, indexed address/data windows, busy and abort status, command/argument mailboxes to SMU, scheduler byte fields, UTCL1 translation retry/drop/invalidate/snoop controls, translated request error VMID/address capture, semaphore client IDs, EOF/spare interrupt bits and counters, prewalker trigger/address/size fields, UTCL2 cache and invalidation controls, LB threshold data registers, clock counters, CPG status invalidation, CE/UE error status, DSM memory irritator controls, and RLC-SMU clock request validity.
- CGTS power-decode and clock-gating state. The `xcd0_gc_pwrdec` block defines global CGTS state-machine delays, MGCG enable/mode/override bits, readback mux selection, TCC disable masks, per-compute-unit SP/LDS/SQ/TA/SQC/TD/TCPF controls, and TCPI controls. The repeated per-CU fields provide local clock/power gating thresholds and override paths for shader and texture/cache-related subblocks.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register address macros are expected in the companion GC 9.4.3 offset header.
- Callers use these constants with AMDGPU register packing/extraction helpers, direct MMIO helpers, indexed register helpers, firmware mailbox setup, diagnostics, or power-management programming sequences.

Important register families in this slice include:

- `RLC_SRM_*`: RLC service/resource-management command status, indexed control address/data windows 0-7, busy status, and GPM abort.
- `RLC_CSIB_*`, `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_*`, `RLC_SMU_CLK_REQ`, and `RLC_CP_SCHEDULERS`: RLC-to-firmware/control-plane data paths, scheduler bytes, SMU command arguments, clock request validity, and command buffer or instruction-buffer address/length style fields.
- `RLC_GPM_GENERAL_*`, `RLC_GPM_UTCL1_CNTL_*`, `RLC_SPM_UTCL1_CNTL`, `RLC_PREWALKER_UTCL1_*`, `RLC_UTCL1_STATUS*`, and `RLC_UTCL2_CNTL`: scratch/general registers and memory-translation/cache-control fields for GPM, SPM, and prewalker traffic.
- `RLC_*_UTCL1_*ERROR_*`, `RLC_UE_ERR_STATUS_*`, and `RLC_CE_ERR_STATUS_*`: error-capture fields for translated request failures and corrected/uncorrected RLC memory errors, including valid flags, address fragments, VMID, memory ID, error info, counters, parity/ECC/poison indicators, and reserved bits.
- `RLC_SEMAPHORE_*`, `RLC_CP_EOF_INT*`, `RLC_SPARE_INT*`, and `RLC_RLCV_SPARE_INT*`: small client-ID, interrupt, and interrupt-count fields used by RLC/CP/RLCV synchronization and notification paths.
- `RLC_DSM_TRIG`, `RLC_DSM_CNTL*`, and `RLC_DSM_CNTL2*`: diagnostic stress/error-injection controls for RLCG/RLCV instruction RAM, scratch RAM, TCTAG RAM, SPM scratch RAM, SRM data/address RAM, and per-SE SPM scratch RAM.
- `CGTS_SM_CTRL_REG`, `CGTS_RD_CTRL_REG`, `CGTS_RD_REG`, `CGTS_TCC_DISABLE`, and `CGTS_USER_TCC_DISABLE`: global CGTS state-machine, readback, and TCC-disable controls.
- `CGTS_CU<n>_SP0_CTRL_REG`, `CGTS_CU<n>_LDS_SQ_CTRL_REG`, `CGTS_CU<n>_TA_SQC_CTRL_REG`, `CGTS_CU<n>_SP1_CTRL_REG`, and `CGTS_CU<n>_TD_TCP_CTRL_REG` for CUs 0-15: repeated subblock control fields with base 7-bit values plus override, busy override, light-sleep override, and SIMD-busy override bits.
- `CGTS_CU<n>_TCPI_CTRL_REG`: per-CU TCPI controls begin at the end of the chunk, complete for CUs 0-8 and partial for CU9.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 9.4.3 register metadata for the active ASIC.
2. Choose an address macro from the matching offset header.
3. Build a register value from firmware state, power-management policy, error handling, debugfs/diagnostic input, or a read-modify-write of current hardware state.
4. Pack or extract fields using the `__SHIFT`/`__MASK` pairs, usually through common AMDGPU register helpers.
5. Issue MMIO/indexed writes or reads, send RLC/SMU mailbox commands, poll status bits, service interrupts/errors, or program CGTS clock-gating state.

The RLC-side runtime sequences are generally command/status or diagnostic flows: write command/argument registers, poll FIFO/busy/ready/status fields, capture errors, trigger prewalker or DSM behavior, and update interrupt or semaphore state. The CGTS-side runtime sequences are power-management flows: configure global CGTS behavior, select readback muxes, disable or mask TCCs, and apply per-CU subblock override or gating policy. This header does not define required waits, side effects, reset ordering, privilege rules, pulse-versus-level semantics, or whether a field is read-only/write-only; those constraints must come from the hardware spec and the AMDGPU code that uses the macros.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware fields whose values live in GPU registers, firmware-visible mailboxes, diagnostic latches, or command/state storage until overwritten, reset, restored after GPU reset, or reinitialized during suspend/resume and power transitions.

Several fields in this chunk represent persistent control state:

- RLC UTCL1/UTCL2 controls can change retry timing, drop behavior, invalidation, fragment limit mode, and snooping behavior for RLC-originated translation traffic. Stale or incorrectly restored values can affect later RLC memory operations beyond the code path that programmed them.
- `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_*`, and `RLC_SMU_CLK_REQ` are mailbox-style fields. Their correctness depends on firmware protocol ordering and ownership, not just field packing.
- Semaphores, interrupts, and EOF counters are synchronization-visible state. Misinterpreting level, pulse, clear-on-read, or write-one-to-clear semantics can lose events or leave stale notifications.
- Error-status registers capture hardware fault state. Valid flags, address-valid flags, counters, VMID, memory ID, and high/low address fragments must be read consistently before software clears or overwrites the source state.
- DSM controls are diagnostic and error-injection state. Leaving irritator or injection bits enabled outside controlled test paths can intentionally corrupt internal RLC memories or produce artificial error reports.
- CGTS state-machine and per-CU control registers persist as power/clock-gating policy. Override and busy-override fields can hold hardware units on, force light-sleep behavior, or defeat normal automatic gating until explicitly changed.

The header does not encode reset defaults, reserved-bit preservation requirements, access width, or safe read-modify-write rules. Callers should preserve reserved bits unless writing a documented full-register value and should use unsigned 32-bit arithmetic because many masks occupy high bits or full 32-bit data fields.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.4.3 register set staying internally consistent:

- The companion `gc_9_4_3_offset.h` provides the register addresses corresponding to these field masks.
- A matching `gc_9_4_3_default.h`, where present for the same families, provides reset/default values.
- AMDGPU register helpers provide field packing/extraction plus MMIO, indexed-register, mailbox, and power-management access paths.
- Firmware protocols with RLC and SMU determine legal command/argument values, readiness polling, and clock-request semantics.
- GPU memory-management, VM fault handling, interrupt handling, reset/recovery, suspend/resume, RAS, diagnostics, debugfs, and power-gating code rely on these bit layouts matching the hardware database.

Integration points include RLC SRM/RLCV command submission, indexed SRM register access, RLC-to-SMU communication, UTCL1/UTCL2 translation tuning, prewalker memory priming, RLC error capture and reporting, CP EOF and spare interrupt handling, RLC semaphores, GPU clock counter reads, CPG invalidation, RLC diagnostic stress/error injection, TCC disable policy, CGTS readback/debug selection, and per-CU clock-gating override programming for SP, LDS, SQ, TA, SQC, TD, TCPF, and TCPI blocks.

The `addressBlock: xcd0_gc_pwrdec` marker is a meaningful boundary: macros after it describe CGTS power-decode registers rather than the preceding RLC service/control register block. The final per-file merge should preserve that boundary.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Wrong shifts or masks compile cleanly but can program unrelated hardware bits, causing RLC hangs, lost firmware commands, false or missed errors, broken interrupt signaling, bad power behavior, or device reset failures.
- The chunk starts mid-register: only the last three masks of `RLC_SRM_RLCV_COMMAND` are present here. The preceding chunk is required to understand the full command layout.
- The chunk ends mid-register: `CGTS_CU9_TCPI_CTRL_REG` includes only `TCPI`, `TCPI_OVERRIDE`, and `TCPI_BUSY_OVERRIDE` shifts here. The following chunk is required for its remaining shifts and masks plus later TCPI instances.
- Repeated CGTS per-CU layouts invite generator or copy/paste errors. A mismatch on one CU or one subblock may present as a topology-specific performance or power regression rather than a broad failure.
- RLC mailbox, semaphore, interrupt, and status registers may have side-effect semantics not visible in the mask header. Treating them as ordinary read/write state can lose events, clear latches unexpectedly, or race firmware.
- Address fields in prewalker and CSIB registers are split into low/high fragments and may use hardware-specific alignment units. Raw byte-address assumptions can produce plausible but wrong register values.
- UTCL1/UTCL2 retry, drop, invalidation, force-snoop, and cache-control fields affect memory-translation behavior. Incorrect values can cause timeouts, translation faults, stale translations, or poor performance under VM pressure.
- Error-status low/high pairs must be correlated carefully. Reading only one half, ignoring valid flags, or clearing in the wrong order can produce misleading RAS reports.
- DSM irritator and error-injection controls are intentionally hazardous diagnostic knobs. They should be isolated to test/debug paths with explicit cleanup.
- CGTS override and TCC-disable fields can silently alter power, clock, cache, and compute-unit behavior. Full-register writes that do not preserve reserved or ASIC-specific bits can cause subtle instability or power regressions.

## Test Signals

Useful validation is mostly build coverage, generated-data consistency checks, and hardware/runtime coverage:

- Kernel build coverage for AMDGPU files including `gc_9_4_3_sh_mask.h`, especially RLC, GC power management, RAS, reset/recovery, suspend/resume, diagnostics, and debugfs paths.
- Mechanical comparison against AMD's authoritative GC 9.4.3 register database for every `__SHIFT`/`__MASK` pair in this line range.
- Cross-checks that every complete register family in this chunk has matching address macros in `gc_9_4_3_offset.h` and expected defaults in generated default headers where those defaults exist.
- Static sanity checks that masks align with shifts, full-width data registers use `0xFFFFFFFFL`, high-bit masks are handled as unsigned values, split low/high address fields are complete across chunks, and repeated per-CU CGTS patterns remain consistent.
- Runtime RLC tests that exercise SRM/RLCV command/status paths, SMU command/argument handshakes, scheduler fields, semaphore/interrupt handling, EOF counters, GPU clock counter capture, CPG invalidation, and reset/recovery reinitialization.
- VM and fault-path tests that cover UTCL1/UTCL2 controls, prewalker trigger/address/size programming, translated request error capture, CE/UE error reporting, poison/ECC/parity indicators, and RAS logging.
- Diagnostic tests that enable and disable DSM irritator/error-injection fields in a controlled environment and verify cleanup restores normal behavior.
- Power-management tests that cover CGTS global mode programming, readback muxes, TCC disable masks, per-CU SP/LDS/SQ/TA/SQC/TD/TCPF/TCPI overrides, compute workloads across all CUs, idle transitions, clock gating, suspend/resume, and GPU reset.
- Runtime warning signals include RLC busy or FIFO status stuck, SMU command timeouts, missing or repeated EOF/spare interrupts, malformed RAS addresses or counters, VM faults after prewalker/UTCL changes, artificial errors outside diagnostic mode, unexpected TCC disablement, per-CU performance asymmetry, higher idle power, failed clock-gating transitions, and regressions isolated to one CU index.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002696`. It covers lines 27088-29458 of `gc_9_4_3_sh_mask.h`. The final per-file document should merge it with the preceding chunk for the complete `RLC_SRM_RLCV_COMMAND` field list and with the following chunk for the rest of `CGTS_CU9_TCPI_CTRL_REG` and subsequent CGTS TCPI controls.

### subset-b-002697: lines 29459-31649

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 29459-31649

## Scope

This chunk is the final slice of the generated AMD GC 9.4.3 shader-mask header. It starts in the tail of `CGTS_CU9_TCPI_CTRL_REG`, completes the CU10-CU15 TCPI control masks, covers a large set of clock-gating and power/throttle register fields, then moves through GC hypervisor/IOV, VM shared hypervisor, PSP/security, GRBM, and SQ indirect debug register layouts. The range ends at the file's closing `#endif`.

The file is declarative hardware metadata. It contains preprocessor constants only: no C functions, structs, enums, runtime variables, loops, branches, allocations, locks, or callbacks.

## Purpose

`gc_9_4_3_sh_mask.h` defines bit positions and masks for GC 9.4.3 registers. Driver code combines these macros with the companion `gc_9_4_3_offset.h` register IDs and AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and indirect register accessors. The effective API pattern is:

- `<REGISTER>__<FIELD>__SHIFT` for the field's least-significant bit.
- `<REGISTER>__<FIELD>_MASK` for the raw 32-bit register mask.

This specific chunk provides field contracts for clock gating, RLC/CP microcode and virtualization control, VM/IOMMU/ATS virtualization, PSP/GRBM security and error reporting, SQ wave snapshot/debug state, and SQ interrupt payload decoding. Although the repository path is under a Ceph source mirror, this file is AMD GPU driver hardware metadata and has no distributed-filesystem behavior.

## Important Register Families

The first section finishes TCPI and clock-gating controls. `CGTS_CU10_TCPI_CTRL_REG` through `CGTS_CU15_TCPI_CTRL_REG` repeat the per-CU `TCPI`, `TCPI_OVERRIDE`, `TCPI_BUSY_OVERRIDE`, `TCPI_LS_OVERRIDE`, and `TCPI_SIMDBUSY_OVERRIDE` layout. `CGTT_*_CLK_CTRL` families then describe clock-gating delay, hysteresis, soft-stall, soft-override, group-override, and register-override fields for SPI, SPIS, PC, BCI, VGT, IA, WD, PA, SC, SQ, SQG, TCPI, DB, CB, TCC, TCA, CP, CPC, RLC, RMI, TCPF, and related blocks. `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` provide per-shader-array `FORCE_CU_ON` masks, while `SQ_POWER_THROTTLE` and `SQ_POWER_THROTTLE2` expose min/max power, phase offset, delta, interval, ratio, and reference-clock controls.

The `xcd0_gc_hypdec` section defines command-processor and RLC hypervisor-facing fields. It includes CP PFP/ME/CE/MEC microcode address/data/checksum registers, hypervisor variants of those programming surfaces, `CP_HYP_XCP_CTL` for physical XCC and die IDs, RLC GPM microcode access, GRBM indexed shadow-register select/data fields, RLC GPU IOV enable/config/status/doorbell/mask registers, RLC hypervisor semaphores, RLC clock controls, scheduler block metadata, active function IDs, interrupt status/disable/force fields, IOV microcode and scratch access, F32 enable/reset, SMU/RLC response registers, VF/PF virtual reset requests, and SDMA0-SDMA7 preempt/save/restore and busy-status fields.

The `xcd0_gc_utcl2_vmsharedhvdec` section is VM and virtualization metadata. It defines per-VF framebuffer size/offset registers for VF0-VF15, IOMMU enable and performance-optimization bits, MARC base/relocation/length low/high registers for four MARC regions, PCIe ATS control including shared STU/ATC enable and per-VF ATC enable, active shared function ID fields, and XGMI GPU IOV enable bits for VF0-VF15 plus PF.

The `xcd0_gc_pspdec` section covers PSP/security and GRBM debug/error surfaces. `CPG_PSP_DEBUG` and `CPC_PSP_DEBUG` describe privilege and VMID violation controls, with CPC-specific UTCL2 override and disable bits. `GRBM_SEC_CNTL` has a debug enable bit. `GRBM_IOV_ERROR_FIFO_DATA` packs IOV error address, VF ID, source ID, operation, VF/PF flag, overflow, and read-valid status. `GRBM_CAM_INDEX`, `GRBM_HYP_CAM_INDEX`, `GRBM_CAM_DATA`, and `GRBM_HYP_CAM_DATA` define CAM remap selectors/data. `RLC_FWL_FIRST_VIOL_ADDR` reports the first firewall violation status, operation, address, and aperture ID.

The `sqind` section is the SQ indirect wave/debug view. It defines `SQ_DEBUG_STS_LOCAL`, `SQ_DEBUG_CTRL_LOCAL`, `SQ_WAVE_VALID_AND_IDLE`, performance snapshot placeholders, `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, GPR/LDS allocation, instruction-buffer status/debug registers, PC and instruction dwords, `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`, `SQ_WAVE_M0`, and `SQ_WAVE_EXEC_LO/HI`. The final `SQ_INTERRUPT_WORD_*` families describe packed interrupt payloads for automatic events, common metadata, and wave-specific events in context-ID and high/low split forms.

## Control Flow

There is no control flow in the header itself. Runtime control flow is supplied by consumers:

1. GC 9.4.3-specific code includes `gc_9_4_3_offset.h` and this mask header.
2. The caller selects a direct register or an indirect/indexed register such as an SQ wave register.
3. Code composes or decodes a 32-bit value with the generated shift/mask macros, usually through `REG_SET_FIELD` or `REG_GET_FIELD`.
4. AMDGPU or KFD access helpers perform MMIO, SOC15, or indirect reads/writes.

In-tree GC 9.4.3 code includes this header from `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`; that file reads SQ wave state through `wave_read_ind()` using registers such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_HW_ID`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_DBG0`, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_MODE`. KFD queue-manager code for v9 also includes this mask header.

## State And Persistence Behavior

The macros persist no software state; they are compile-time constants. The hardware fields they describe are stateful and have different lifetimes:

- Clock-gating and power-throttle fields are configuration state. They persist in GC registers until ASIC reset, suspend/resume reprogramming, power-gating transitions, firmware sequences, or explicit driver writes.
- CP and RLC microcode address/data/checksum fields are programming windows for firmware-visible state. Their sequencing and side effects are controlled by microcode load and RLC/CP initialization paths, not by this header.
- RLC GPU IOV fields track virtualization scheduler commands, active functions, doorbells, VM busy state, SDMA save/restore state, interrupt state, and reset requests. Some fields are command/configuration knobs; others are status, sticky status, or response readbacks.
- VM shared hypervisor fields encode VF framebuffer windows, MARC relocation ranges, IOMMU/ATS enablement, active function identity, and XGMI GPU IOV enablement. These are isolation-sensitive device registers, not kernel data structures.
- GRBM/PSP/RLC firewall fields expose security/debug state such as violation controls and first-violation capture. Status fields may be latched, FIFO-backed, or clear-on-read/write according to hardware rules outside this header.
- SQ wave fields are a live per-wave snapshot. Values can change while waves execute, halt, trap, replay, drain, or context-save. TTMP, M0, EXEC, PC, status, trap status, and allocation fields describe the selected wave at the time of indirect access.
- SQ interrupt word fields describe payloads delivered through interrupt/context-ID paths; they are decoded at interrupt time and are not persistent driver storage.

Full-width masks such as `0xFFFFFFFFL` appear for data, scratch, microcode, status bitmap, and register-save fields. A full-width mask does not imply that arbitrary writes are safe.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.4.3 register database remaining synchronized across:

- `gc_9_4_3_sh_mask.h`, which supplies the field layouts researched here.
- `gc_9_4_3_offset.h`, which supplies matching register offsets and indirect indices.
- AMDGPU helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, which rely on exact generated macro spelling.
- SOC15 MMIO helpers and XCC-aware register-address normalization in `gfx_v9_4_3.c`.
- Indirect SQ access helpers used for wave dumps, hang diagnostics, and reset/debug paths.
- RLC and CP firmware loading, scheduler, and virtualization code that programs hypervisor, IOV, scratch, semaphore, and microcode windows.
- VM/MMU/IOMMU/ATS and SR-IOV paths that configure VF address windows, active function IDs, XGMI GPU IOV, and PCIe ATS.
- KFD queue, trap, and interrupt paths that use generation-specific SQ wave and interrupt payload layouts.

The macros are generation-specific. Similar field names in GC 9.1, GC 9.4.2, GC 10, GC 11, or GC 12 headers may have different widths, split formats, or register ownership.

## Risks And Edge Cases

- The chunk starts mid-register in `CGTS_CU9_TCPI_CTRL_REG`; the merged per-file report must reconcile the preceding `CU9` field definitions from chunk 12.
- Header/offset mismatch is the highest general risk. Pairing GC 9.4.3 masks with another generation's offset header can compile while programming incorrect bits.
- Clock-gating families are repetitive but not identical. Copying masks across blocks can set reserved bits, leave override bits unset, or force clocks on/off unexpectedly.
- RLC GPU IOV and VM shared hypervisor fields are isolation-sensitive. Incorrect VF enable, framebuffer offset/size, MARC relocation, ATS, active-function, or reset-request programming can break PF/VF isolation, scheduling, or recovery.
- Microcode address/data windows require strict sequencing. Misusing address masks, checksum fields, or hypervisor versus non-hypervisor aliases can corrupt firmware loading or diagnostics.
- SQ wave state is volatile and indirect. Callers must select the intended XCC/SE/SH/SIMD/wave context and tolerate races with wave execution and context save/restore.
- SQ interrupt payload layouts are generation-sensitive. The chunk provides both context-ID and high/low split forms; mixing the wrong form can misdecode wave ID, SIMD ID, CU ID, SE ID, privilege, or event bits.
- Reserved masks are present throughout the chunk. Read-modify-write consumers should preserve unknown bits unless the hardware programming sequence explicitly requires a full-register write.
- The final `#endif` means this is the end of the generated header; downstream merge should not expect later chunks for this source file.

## Test And Validation Signals

Useful validation is primarily build, static, and hardware based:

- Build AMDGPU and KFD code that includes `gc_9_4_3_offset.h` and `gc_9_4_3_sh_mask.h`, especially `gfx_v9_4_3.c` and `kfd_device_queue_manager_v9.c`.
- Preprocess or compile call sites using `REG_SET_FIELD`/`REG_GET_FIELD`; spelling drift in generated field names should fail at compile time when directly referenced.
- Static generated-header checks should verify that complete register groups have matching `__SHIFT` and `_MASK` pairs, masks align with shifts, and fields do not overlap except for documented full-width data/status registers.
- Cross-check register names in this chunk against the companion offset header for `CGTT_*`, `RLC_GPU_IOV_*`, `MC_VM_*`, `VM_PCIE_ATS_CNTL*`, `GRBM_*`, `SQ_WAVE_*`, and `SQ_INTERRUPT_WORD_*`.
- Runtime GC 9.4.3 bring-up should validate stable clock-gating initialization, CP/RLC firmware loading, RLC scheduler setup, IOV doorbell/status handling, VM/IOMMU/ATS configuration, suspend/resume, and GPU reset.
- SR-IOV or multi-function testing should exercise VF framebuffer windows, active function IDs, XGMI GPU IOV enables, virtual reset requests, SDMA save/restore status, and IOV error FIFO reporting.
- Debug and hang-dump tests should read SQ wave data through `gfx_v9_4_3_read_wave_data()` and verify plausible mode, status, trap, PC, instruction, allocation, IB, M0, and EXEC fields.
- KFD interrupt and trap tests should trigger thread-trace, timestamp, overflow, wave, trap, and context-save related paths and validate decoded `SQ_INTERRUPT_WORD_*` payloads against known hardware events.
