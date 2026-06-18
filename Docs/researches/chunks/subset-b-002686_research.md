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
