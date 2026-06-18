# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h lines 5887-7275

## Scope

This chunk is the final segment of the generated AMD GC 10.3.0 default-register header. It contains only C preprocessor `#define` constants for register reset/default values; it declares no functions, structs, enums, storage objects, or executable initialization code.

The range starts in the `mmSDMA3_*` register-default area at `mmSDMA3_AQL_STATUS_DEFAULT`, covers SDMA3 queue defaults for the GFX, PAGE, and RLC0-RLC7 contexts, then transitions through generated indexed register address blocks:

- `gccacind`: global graphics CAC, PCC, power-brake, EDC, LUT, fixed-pattern counter, and hardware-LUT status defaults.
- `secacind`: per-shader-engine CAC selector/control defaults.
- `spmglbind`: global SPM sample-delay defaults.
- `spmind`: shader-engine and shader-array SPM sample-delay defaults.
- `grtavfsind`: RTAVFS register-table defaults.
- `spiind`: `ixSA_WGP_BLK_ID_DEFAULT`.
- `sqind`: SQ wave debug and interrupt-word defaults.
- `didtind`: DIDT/EDC throttle defaults for SQ, DB, TD, and TCP, ending with stall-event counters and the file `#endif`.

## Purpose

`gc_10_3_0_default.h` is generated hardware metadata for AMDGPU GC 10.3 ASICs. Its `_DEFAULT` macros give the reset value associated with register names from the matching GC register offset header. Driver code includes this header with `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h` so ASIC-specific code can use the correct register addresses, bit fields, and known reset values for this graphics generation.

This chunk documents late-file default surfaces rather than programming policy. The SDMA3 defaults describe the baseline state for the fourth SDMA engine's queue machinery: queue control, ring and indirect-buffer state, read/write pointers, doorbells, write-pointer polling, context status, preemption, AQL controls, mid-command scratch capture, and queue reset/status registers. The CAC/SPM/RTAVFS/DIDT indexed sections describe baseline power, droop, performance-monitoring, sampling, debug, and throttling registers used by graphics, shader-engine, shader-array, and texture/cache clients.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro convention:

- `mm<REGISTER>_DEFAULT` gives a default for a memory-mapped register named by the matching `mm<REGISTER>` offset macro.
- `ix<REGISTER>_DEFAULT` gives a default for an indexed register accessed through an indirect address block.
- The corresponding register addresses live in `gc_10_3_0_offset.h`.
- The field shifts and masks live in `gc_10_3_0_sh_mask.h`.
- Normal consumers combine these definitions with AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Notable macro groups in this chunk:

- `mmSDMA3_*`: starts with engine-level defaults such as `AQL_STATUS` = `0x00000003`, `TLBI_GCR_CNTL` = `0x40180454`, `STATUS4_REG` = `0x00000001`, and mostly-zero status, address, timestamp, scratch, interrupt, hole-address, and queue-reset defaults.
- `mmSDMA3_GFX_*` and `mmSDMA3_PAGE_*`: queue defaults for graphics and page queues. Their ring-buffer control defaults are `0x80840000`, write-pointer polling defaults are `0x00403000`, indirect-buffer control defaults are `0x00000100`, AQL control defaults are `0x00004000`, dummy-register defaults are `0x0000000f`, and the remaining pointer/base/status/doorbell/mid-command fields mostly reset to zero. `GFX_CONTEXT_STATUS_DEFAULT` is `0x00000005`; `PAGE_CONTEXT_STATUS_DEFAULT` is `0x00000004`.
- `mmSDMA3_RLC0_*` through `mmSDMA3_RLC7_*`: eight RLC queue contexts with repeated 44-register layouts. Each RLC queue uses `RB_CNTL_DEFAULT` = `0x80040000`, `RB_WPTR_POLL_CNTL_DEFAULT` = `0x00403000`, `IB_CNTL_DEFAULT` = `0x00000100`, `CONTEXT_STATUS_DEFAULT` = `0x00000004`, `DUMMY_REG_DEFAULT` = `0x0000000f`, `RB_AQL_CNTL_DEFAULT` = `0x00004000`, and zero defaults for base pointers, read/write pointers, doorbells, preemption, CSA, mid-command data, and status.
- `ixPCC_*`, `ixPWRBRK_*`, and `ixEDC_*`: power control and droop counter defaults. Stall-pattern controls default to nonzero values (`ixPCC_STALL_PATTERN_CTRL_DEFAULT` = `0x07fa0401`, `ixPWRBRK_STALL_PATTERN_CTRL_DEFAULT` = `0x00fa0401`), while the pattern payloads, hysteresis, and stretch/unstretch counters reset to zero.
- `ixGC_CAC_*`: global CAC metadata. `ixGC_CAC_CNTL_DEFAULT` is `0x000001fe`; selector/override fields reset to zero; CAC weights are generally `0x00010001` or `0x00000001`; the many `ixGC_CAC_ACC_*` activity accumulators and `ixGC_CAC_OVRD_*` override registers default to zero.
- `ixRELEASE_TO_STALL_*`, `ixSTALL_TO_RELEASE_*`, `ixSTALL_TO_PWRBRK_*`, and `ixPWRBRK_*_LUT_*`: LUT entries for stall/release and power-brake transitions, all zero defaults in this range.
- `ixFIXED_PATTERN_PERF_COUNTER_1_DEFAULT` through `_10_DEFAULT` and `ixHW_LUT_UPDATE_STATUS_DEFAULT`: fixed-pattern counters and update status, all zero defaults.
- `ixSE_CAC_*`: per-shader-engine CAC ID, control, override selector, and override value; `CNTL` mirrors the global `0x000001fe` default and the other values are zero.
- `ixGLB_*_SAMPLEDELAY_DEFAULT`: global SPM sample-delay registers for CPG/CPC/CPF, GDS/GCR/PH/GE/GUS, CHA/CHC, ATCL2/VML2, SDMA0-SDMA3, GL2A, GL2C0-15, EA0-15, and GE2SE links. All default to zero.
- `ixSE_*_SAMPLEDELAY_DEFAULT`: shader-engine SPM sample-delay registers for SPI, SQG, CBR, DBR, PA, SX, GL1, CB/DB, SC, RMI, and WGP-local TA/TD/TCP lanes for SA0 and SA1. All default to zero.
- `ixRTAVFS_REG0_DEFAULT` through `ixRTAVFS_REG165_DEFAULT`: RTAVFS table entries. Many entries are zero, but the table contains important nonzero reset words including repeated `0x01000000` values, `ixRTAVFS_REG134_DEFAULT` = `0x000211cd`, `REG135` = `0x000af12c`, `REG136` = `0x00000010`, `REG138` = `0x00000008`, `REG144` = `0x0015c040`, `REG146` = `0x83c00260`, `REG147` = `0x00000800`, `REG149`-`REG159` = `0x000000ff`, `REG161` = `0xcccdbcdd`, and `REG162` = `0x2587d190`.
- `ixSA_WGP_BLK_ID_DEFAULT`: SPI-indexed WGP block selector default, zero.
- `ixSQ_WAVE_*` and `ixSQ_INTERRUPT_WORD_*`: SQ wave debug state, trap temporary registers, program counter pieces, execution masks, shader-cycle counter, and interrupt payload words. Every SQ macro in this range defaults to zero.
- `ixDIDT_SQ_*`, `ixDIDT_DB_*`, `ixDIDT_TD_*`, and `ixDIDT_TCP_*`: dynamic droop/throttle defaults. The four clients share common defaults for `CTRL0` (`0x0000ff00`), `CTRL1` (`0x00ff00ff`), `CTRL2` (`0x18800004`), `STALL_CTRL` (`0x00fff000`), `TUNING_CTRL` (`0x00010004`), `STALL_AUTO_RELEASE_CTRL` (`0x00ffffff`), `CTRL3` (`0x00038000`), stall patterns (`0x01010001`, `0x11110421`, `0x25291249`, `0x00002aaa`), `EDC_CTRL` (`0x00001c00`), `EDC_TIMER_PERIOD` (`0x00003fff`), and mostly-zero thresholds, weights, statuses, overflow, rolling-power-delta, PCC counter, and throttle-control fields. `DIDT_TCP_CTRL_OCP_DEFAULT` is `0x0000ffff`; SQ/DB/TD OCP defaults are `0x000000ff`.

## Control Flow

This header has no runtime control flow. The only direct behavior is compile-time substitution of constants by the C preprocessor.

The implied consumer flow is:

1. Include the GC 10.3 offset, shift/mask, and default headers for a target ASIC block.
2. Select a register through an `mm...` or `ix...` macro.
3. Read, write, or read-modify-write that register through SOC15 and indirect-register helpers.
4. Use the `_DEFAULT` value as hardware reset documentation, a baseline for initialization tables, or a comparison/restoration value.

The SDMA3 RLC queue defaults integrate with runtime code that computes queue-register spacing from register symbols. For example, `amdgpu_amdkfd_gfx_v10_3.c` derives SDMA engine and RLC queue offsets using `mmSDMA3_RLC0_RB_CNTL` and adjacent RLC register spacing. This chunk does not execute that arithmetic, but the naming and generated layout must remain consistent with those consumers.

For DIDT/CAC/SPM/RTAVFS blocks, real sequencing occurs in power-management, performance-monitoring, debug, or hardware-init code outside this file: select an indirect address block, program thresholds, enable/disable counters or throttling, poll status, and clear counters. These defaults define the reset baseline before those sequences run.

## State And Persistence

The chunk stores no software state. All macros are compile-time constants and do not allocate memory or persist data.

The represented state is hardware state:

- SDMA3 queue state includes ring-buffer base addresses, read/write pointers, write-pointer polling addresses, doorbell state, context-save addresses, indirect-buffer state, preemption, AQL mode, and mid-command capture words.
- CAC and EDC state includes power/droop control words, stall patterns, activity weights, override registers, accumulators, counters, and transition LUT entries.
- SPM state includes sampling delay selectors for global, shader-engine, shader-array, and per-WGP units.
- RTAVFS state is a generated register table with several nonzero reset values that likely represent fused or specification-defined adaptive-voltage/frequency defaults.
- SQ state includes wave debug selection and readout registers that reset to idle/zero until a wave is selected and observed.
- DIDT state includes throttling thresholds, OCP limits, stall patterns, EDC timers, event counters, and rolling power metrics.

Hardware reset, GPU suspend/resume, ASIC initialization, runtime power management, and GPU reset paths are the events that make these defaults relevant. Any software that reinitializes these blocks must treat the defaults as ASIC-generation-specific, not as portable values.

## Dependencies And Integration Points

This generated header depends on the surrounding ASIC register description set:

- `gc_10_3_0_offset.h` supplies the register offsets and indirect register names that correspond to these `_DEFAULT` macros.
- `gc_10_3_0_sh_mask.h` supplies field shifts and masks for interpreting or modifying each value.
- SDMA-specific offset headers also contain SDMA3 register names used by consumers and by generated cross-block register layouts.
- AMDGPU SOC15 helpers provide address calculation and register I/O.
- KFD/AMDKFD queue code relies on the SDMA3 RLC register layout for MQD queue setup and per-engine/per-queue offset computation.
- `gfxhub_v2_1.c` includes this default header with the matching GC 10.3 offset and shift/mask headers for graphics hub programming.

The chunk is source-tree-aligned with `drivers/gpu/drm/amd/include/asic_reg/gc/`. It should be kept synchronized with any regenerated GC 10.3 register headers; manually changing a default without the corresponding offset and mask metadata risks creating inconsistent hardware descriptions.

## Risks And Edge Cases

- Generated-header drift is the main risk. If defaults, offsets, and masks are regenerated from different hardware databases or ASIC revisions, code can compile while silently using mismatched reset values.
- Queue layout symmetry is assumed by SDMA/KFD code. The repeated SDMA3 GFX/PAGE/RLC queue macro groups must stay ordered and named consistently because consumers derive offsets from adjacent register symbols rather than storing every queue's full address table.
- Nonzero SDMA queue-control defaults are meaningful. Values such as `0x80840000`, `0x80040000`, `0x00403000`, `0x00000100`, and `0x00004000` should not be normalized to zero during cleanup because they encode reset behavior for ring buffers, polling, IB handling, and AQL state.
- RTAVFS register names are opaque (`REG0`-`REG165`), making review harder. Nonzero words such as `0x83c00260`, `0xcccdbcdd`, and `0x2587d190` require validation against the generated source or hardware database rather than semantic code inspection.
- DIDT blocks are mostly symmetric but not perfectly identical: TCP has a wider OCP default (`0x0000ffff`) than SQ/DB/TD (`0x000000ff`), and DB lacks `EDC_STALL_DELAY_2`/`3` macros in this generated range while SQ, TD, and TCP include them. Treat these differences as hardware-description facts unless the upstream generator changes.
- The header itself cannot validate hardware behavior. A wrong default may only show up as power-management instability, counter mismatch, queue bring-up failure, suspend/resume regression, or ASIC-specific performance anomalies.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are integration and build oriented:

- Build coverage for AMDGPU and AMDKFD code that includes `gc_10_3_0_default.h`, especially `gfxhub_v2_1.c`, SDMA v4.x code, and `amdgpu_amdkfd_gfx_v10_3.c`.
- Compile-time detection of missing or renamed macros when generated offset/default/mask headers drift.
- Runtime dmesg traces from GPU initialization, SDMA/KFD queue setup, and GPU reset paths on GC 10.3 hardware.
- KFD queue tests that exercise SDMA RLC queue creation across multiple SDMA engines and RLC queue IDs.
- Suspend/resume and GPU reset testing, which can expose incorrect assumptions about reset/default queue, CAC, SPM, RTAVFS, or DIDT state.
- Power-management and throttling telemetry checks for CAC/DIDT/EDC counters, stall event counters, and power-brake behavior.
- SPM/performance-monitoring tests that confirm sample-delay and fixed-pattern counter registers can be programmed from their zero default baseline.
