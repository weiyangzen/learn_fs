# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 2418-4814

## Purpose

This chunk is generated AMD GC 9.0 graphics-core register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants for fields in 32-bit hardware registers. AMDGPU, AMDKFD, power-management, debug, and profiling code pair these macros with register offsets from `gc_9_0_offset.h` and register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

The selected range starts in the tail of SQC data-share-memory single-write controls, then covers SQC error injection and EDC counters, SQ command/indexed debug and instruction/resource encodings, SQ load-balance and EDC state, SQ thread-trace token word layouts, SQC instruction/data UTCL1 control/status registers, the `gc_shsdec` block for SX and SPI debug/wave-lifetime state, the `gc_tpdec` TD/TA texture control/status block, and the beginning of `gc_gdsdec` GDS configuration/status/fault/EDC registers. Despite the repository path being under `ceph-client`, this file is AMD GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, locks, allocations, or direct MMIO operations in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Consumers compose or decode register values with the matching `mm*`/`reg*` offsets from `gc_9_0_offset.h`.

Major register groups in this range:

- SQC DSM and EDC controls: `SQC_DSM_CNTLB`, `SQC_DSM_CNTL2`, `SQC_DSM_CNTL2A`, `SQC_DSM_CNTL2B`, `SQC_EDC_FUE_CNTL`, `SQC_EDC_CNT2`, `SQC_EDC_CNT3`, and `SQC_EDC_CNT` describe single-write irritator data, error-injection enables/delays, fatal uncorrectable error interrupt flags, and SEC/DED/SED counters for instruction and data tag RAMs, bank RAMs, UTCL1 FIFOs, miss FIFOs, dirty-bit RAMs, and per-CU data paths.
- SQ debug and command registers: `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_CMD`, `SQ_TIME_HI`, and `SQ_TIME_LO` define timestamp windows, indexed wave/thread reads, force-read/read-timeout controls, command mode/data fields, VMID checking, wave/SIMD/queue targeting, and 64-bit time readback split into high/low registers.
- Shader instruction encoding views: `SQ_DS_*`, `SQ_EXP_*`, `SQ_FLAT_*`, `SQ_GLBL_*`, `SQ_INST`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SCRATCH_*`, `SQ_SMEM_*`, `SQ_SOP*`, `SQ_VINTRP`, `SQ_VOP*`, `SQ_VOP_DPP`, `SQ_VOP_SDWA`, and `SQ_VOP_SDWA_SDST_ENC` expose bitfield layouts for GC 9 shader instruction words. These include operand registers, offsets, opcodes, encodings, cache-policy bits such as `GLC`/`SLC`, data/number formats, swizzle fields, modifiers, clamp/neg/abs controls, and DPP/SDWA lane-selection fields.
- SQ load-balance, EDC, and trace-word decode: `SQ_LB_CTR_CTRL`, `SQ_LB_DATA[0-3]`, `SQ_LB_CTR_SEL`, `SQ_LB_CTR[0-3]_CU`, `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, `SQ_EDC_INFO`, `SQ_EDC_CNT`, `SQ_EDC_FUE_CNTL`, and `SQ_THREAD_TRACE_WORD_*` define load-balance counter controls/data/CU masks, LDS/SGPR/VGPR EDC counters and fault source metadata, fatal error flags, and packed thread-trace token formats for events, instructions, issue groups, register writes, wave state, wave starts, user data, PC halves, perf data, and timestamps.
- Shader resource descriptors and samplers: `SQ_BUF_RSRC_WORD[0-3]`, `SQ_IMG_RSRC_WORD[0-7]`, `SQ_IMG_SAMP_WORD[0-3]`, `SQ_FLAT_SCRATCH_WORD[0-1]`, and `SQ_M0_GPR_IDX_WORD` describe buffer base/stride/format/swap/index bounds, image base/metadata/width/height/depth/pitch/mip/array/swizzle/compression fields, sampler clamp/filter/aniso/LOD/border-color fields, scratch size/offset, and M0 relative-index controls.
- SQC UTCL1 controls and status: `SQC_ICACHE_UTCL1_CNTL1/2`, `SQC_DCACHE_UTCL1_CNTL1/2`, `SQC_ICACHE_UTCL1_STATUS`, and `SQC_DCACHE_UTCL1_STATUS` cover instruction/data cache translation behavior, GPUVM default page size and permission modes, response/fault modes, client ID, LFIFO controls, VMID invalidation fields, force-miss/in-order knobs, reduced FIFO/cache sizing, EDC disable, snoop/ack behavior, perf-event filters, and fault/retry/PRT detection bits.
- `addressBlock: gc_shsdec`: `SX_DEBUG_BUSY` through `SX_DEBUG_BUSY_5` expose shader export/color path busy and valid bits across position banks, write controls, DBIF interfaces, color blend queues, and scoreboard/fifo paths. `SX_DEBUG_1` exposes SX-to-DB credit and debug/optimization disable controls. The SPI portion includes `SPI_PS_MAX_WAVE_ID`, `SPI_START_PHASE`, `SPI_GFX_CNTL`, `SPI_DEBUG_READ`, `SPI_DSM_CNTL`, `SPI_DSM_CNTL2`, `SPI_EDC_CNT`, `SPI_DEBUG_BUSY`, `SPI_CONFIG_PS_CU_EN`, wavefront lifetime limit/status/debug registers, SPI load-balance counters, static CU masks, GDS credits, SX export/scoreboard buffer sizes, CSQ active wave status/counts, per-CU wave data readback, SPIS/BCI debug reads, and trap-screen base/mask/GPR-min registers for P0 and P1.
- `addressBlock: gc_tpdec`: `TD_CNTL`, `TD_STATUS`, `TD_DSM_CNTL`, `TD_DSM_CNTL2`, `TD_SCRATCH`, `TA_CNTL`, `TA_CNTL_AUX`, `TA_STATUS`, and `TA_SCRATCH` define texture data/address controls, busy/empty indicators, DSM injection, scratch windows, non-determinism/perf/texture behavior toggles, anisotropy and LOD controls, gather/border/swizzle controls, deterministic-disable bits, FIFO status, and aggregate TA busy state.
- `addressBlock: gc_gdsdec`: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE2`, `GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`, `GDS_EDC_CNT`, and the start of `GDS_EDC_GRBM_CNT` describe GDS shader-array phase selection, GDS/GRBM/ordered-append/GWS/DS busy and conflict status, protection-fault attribution fields, VM fault attribution including VMID/TMZ/GWS/OA, and GDS EDC counters.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the driver and hardware:

1. GC 9 code includes `gc_9_0_sh_mask.h` with the companion GC 9 offset header.
2. The caller selects a register offset and uses the field macros here to build or decode a 32-bit register value.
3. AMDGPU/AMDKFD helpers perform direct or indirect register reads/writes.
4. Higher-level GFX, KFD, reset, debug, profiling, and power-management code owns ordering, locking, safe-mode entry, polling, and timeout handling.

The `SQ_CMD` fields are a concrete example of this flow. GC 9 soft-recovery code in `gfx_v9_0.c` builds a command by setting `CMD`, `MODE`, `CHECK_VMID`, and `VM_ID`, enters RLC safe mode, writes `mmSQ_CMD`, and exits safe mode. KFD debug wave-reset code has a matching `union SQ_CMD_BITS` layout and writes equivalent command fields when killing wavefronts for a process VMID. The header only defines the field layout; it does not decide when wave termination is safe.

SQC and GDS status/fault fields participate in diagnostic flows. GC 9 debug register lists include `mmGDS_PROTECTION_FAULT`, `mmGDS_VM_PROTECTION_FAULT`, `mmSQC_DCACHE_UTCL1_STATUS`, and `mmSQC_ICACHE_UTCL1_STATUS`, allowing hang/fault reporting code to sample whether translation faults, retries, PRT events, or GDS protection faults were observed.

The instruction and resource descriptor macros describe packed data formats rather than driver procedures. They may be used by debug decoders, firmware-facing tooling, trace parsing, or hardware validation to interpret instruction words, buffer/image descriptors, sampler descriptors, thread-trace packets, and load-balance counters.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes hardware state in GC 9 registers and packed shader-facing words.

The represented hardware state includes EDC injection configuration, SEC/DED/SED counters, fatal error flags, SQ command targeting, indirect wave/thread debug indices and data, timestamp/time values, instruction encodings, resource descriptors, sampler descriptors, scratch configuration, SQ load-balance counters, EDC fault source metadata, thread-trace token payloads, SQC UTCL1 invalidation and fault state, SX/SPI busy/debug/status state, SPI wave lifetime thresholds and interrupt-sent status, per-CU/static-CU masks, trap-screen base/mask windows, TD/TA texture controls and busy flags, GDS phase controls, GDS busy/conflict/clamp state, GDS protection-fault attribution, and GDS EDC counters.

Persistence is hardware-defined. Configuration fields generally remain until reset, GPU reset, suspend/resume reinitialization, power transition, or explicit reprogramming. Status, busy, counter, and fault fields can change asynchronously while queues, shaders, texture blocks, caches, and GDS pipelines are active. Some fields are action-like or side-effectful, such as error injection enables, counter load/clear/start bits, SQ commands, SQC invalidation toggles, SPI reset-count controls, and interrupt/fault clear paths in surrounding code.

The macros do not encode access permissions, reset values, read-only/write-only behavior, write-one-to-clear behavior, sticky semantics, self-clearing semantics, reserved-bit policy, alignment units, or privileged access rules. Consumers must preserve unrelated bits in mixed registers and follow the ASIC programming guide and local driver sequencing.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`, which supplies matching register offsets and base-index symbols. This mask header is unsafe to pair with another GC generation's offsets even when register names overlap.

Observed and likely integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c`, which includes `gc_9_0_offset.h` and `gc_9_0_sh_mask.h`, lists SQC/GDS/UTCL1 fault registers for diagnostics, applies golden settings for `TA_CNTL_AUX`, and uses `SQ_CMD` fields for ring soft recovery.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager.c`, which interact with `SQ_CMD` semantics for process wavefront reset and KFD queue/debug control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v9.c`, `amdgpu_amdkfd_arcturus.c`, `soc15.c`, `mxgpu_ai.c`, `gfxhub_v1_0.c`, PSP v3/v11/v12 paths, and Vega10 powerplay includes, which include the GC 9 generated headers for ASIC-specific register programming.
- GFX 9 golden-register and workaround paths. `TA_CNTL_AUX` and `TD_CNTL` fields in this chunk correspond to texture-address/data knobs that are programmed through SOC15 golden settings for Vega and later GC 9 variants.
- Debugfs, GPU hang analysis, RAS/EDC diagnostics, and crash-dump paths, because SQC/SQ/GDS EDC counters, UTCL1 status, SX/SPI busy bits, and GDS protection-fault fields expose low-level fault or activity state.
- Profiling and trace tooling, because `SQ_THREAD_TRACE_WORD_*`, SPI wave lifetime/status, SQ/SPI load-balance counters, and full-width debug readback registers are decode surfaces for shader trace and performance analysis.
- VM and memory-management integration, because SQC instruction/data UTCL1 controls/status and GDS VM protection-fault fields include VMID, fault/retry/PRT, TMZ, and address fragments.
- Graphics and compute pipeline setup, because shader instruction encodings, buffer/image/sampler descriptors, scratch descriptors, SPI CU masks, GDS credits, and TD/TA controls are on the boundary between command submission, shader execution, and hardware validation.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. These constants are untyped integer macros and can compile while targeting the wrong register block or ASIC revision.
- The chunk starts mid-register in the tail of `SQC_DSM_CNTLB` and ends mid-register at the start of `GDS_EDC_GRBM_CNT`; adjacent chunks are required for a complete per-file view.
- Whole-register writes are dangerous for mixed control/status registers. SQC UTCL1, TD/TA, SPI, and GDS registers contain reserved, unused, status, and control fields in the same word.
- `SQ_CMD` is sequencing-sensitive. Issuing wave kill/debug commands without correct VMID selection, safe-mode handling, queue quiescence, or RLC coordination can kill the wrong waves or destabilize recovery.
- Error-injection fields in SQC/SPI/TD are high impact. Accidentally enabling DSM irritator data or delayed error injection can create artificial SEC/DED/FUE conditions and misleading RAS results.
- EDC counters are small packed fields in several registers. Readers must know saturation, clear, and rollover behavior outside this header before treating values as precise event counts.
- Low/high time or counter windows can race with live hardware updates. `SQ_TIME_HI/LO` and full-width counter/debug data registers may require latching, retry reads, or stop/sample sequencing.
- Instruction/resource descriptor masks are not validation logic. A bit pattern that fits a mask may still be illegal for a shader stage, resource type, format, swizzle mode, alignment, or GPUVM configuration.
- SQC UTCL1 invalidation fields include VMID-specific and all-VMID invalidation toggles. Wrong use can leave stale translations, force excessive misses, or affect other VMIDs.
- Fault/status bits such as `FAULT_DETECTED`, `RETRY_DETECTED`, `PRT_DETECTED`, GDS fault fields, and busy flags are volatile. Diagnostic code must tolerate transitions and clear/observe semantics rather than assuming stable snapshots.
- `TA_CNTL_AUX` contains deterministic-disable and texture behavior fields that are touched by golden settings. Wrong values can affect texture determinism, anisotropy, gather behavior, border color handling, and workload-specific rendering correctness.
- SPI wave lifetime limit/status registers are replicated and threshold-like. Misprogrammed limits or sample periods can create unexpected warning interrupts or hide long-lived wavefronts.
- GDS protection-fault address fields are partial and unit-specific. Decoding must combine fault type, VMID or shader attribution, and address fragments according to the hardware spec.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware smoke/debug coverage:

- Build GC 9 AMDGPU, AMDKFD, PSP, GFXHUB, Vega10 powerplay, and SOC15 paths that include `gc_9_0_sh_mask.h`.
- Generated-header checks that every field has coherent `__SHIFT` and `_MASK` definitions, masks align with shifts, fields within a register do not overlap except documented aliases/reserved regions, and registers in this range have matching entries in `gc_9_0_offset.h`.
- Static checks that GC 9 code does not mix `gc_9_0_sh_mask.h` fields with GC 8, GC 10, GC 11, or GC 12 offset headers.
- Soft-recovery and KFD debug tests that issue `SQ_CMD` wave reset/kill commands for selected VMIDs and verify only intended queues/waves are affected.
- GPU hang and fault-dump tests that sample SQC UTCL1 status, GDS protection-fault registers, SX/SPI busy registers, and SQ EDC info after induced or simulated faults.
- RAS/EDC validation that toggles supported injection paths, observes SQC/SPI/GDS counters and FUE flags, then verifies recovery and interrupt behavior.
- VM/cache tests that exercise SQC instruction/data UTCL1 invalidation, fault/retry/PRT reporting, VMID-specific behavior, and suspend/resume or reset reinitialization.
- Shader trace/profiling tests that decode representative `SQ_THREAD_TRACE_WORD_*` packets, SQ/SPI load-balance counter data, wave lifetime status, and full-width debug readback windows.
- Graphics correctness tests around texture sampling and descriptors, especially workloads sensitive to `TA_CNTL_AUX`, image/sampler descriptor encodings, anisotropy, border color, deterministic behavior, and compressed/metadata image fields.
- GDS tests that allocate/use GDS, GWS, and ordered-append resources, stress conflict/clamp paths, trigger or simulate protection faults, and verify busy/status/EDC fields decode plausibly.
