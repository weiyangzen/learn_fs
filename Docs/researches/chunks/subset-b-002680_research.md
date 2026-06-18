# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 31947-33003

## Scope

This chunk is the final section of the generated AMD GC 9.4.2 shift/mask header. It starts in the tail of the `GC_CAC_ACC_PA0` field definitions, continues through the late `gccacind` clock/activity counter metadata, covers power and throttle pattern masks, then defines the `secacind` and `sqind` shader-engine/shader-queue debug layouts through the SQ interrupt word formats. The range ends at the file's closing `#endif`.

The file contains preprocessor constants only. There are no C functions, structs, enums, variables, allocations, locks, callbacks, or executable branches in this range.

## Purpose

The purpose of this section is to expose the bit-level contract between AMDGPU/KFD code and GC 9.4.2 hardware registers. Each register field is represented by generated macro pairs:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field in a 32-bit value.

The matching register offsets and indirect indices are supplied by the companion GC 9.4.2 offset header. This mask header is consumed by AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`, by MMIO accessors such as `RREG32_SOC15`/`WREG32_SOC15`, and by indirect register access paths for `gccacind`, `secacind`, and `sqind`.

## Important APIs, Types, And Macro Families

The API surface is the generated macro namespace. Important families in this chunk are:

- `GC_CAC_ACC_*` accumulator fields for graphics clock/activity counter blocks. These include PA, PC, SC, SPI0..5, EA0..5, RMI0, UTCL2/ATCL20..24, SQ lower/upper accumulator pairs, SX/SXRB, TA, TCC0..4, TCP0..4, TD0..5, VGT0..2, WD0, CU0..13, BCI1, UTCL2 router0..9, UTCL2 VML20..24, and UTCL2 walker0..4. Most are full 32-bit `ACCUMULATOR_31_0` fields; SQ accumulators split into lower 32 bits and upper 8 bits for a 40-bit accumulator view.
- `GC_CAC_WEIGHT_*` fields for packed 16-bit signal weights. The range covers EA, RMI, UTCL2/ATCL2, UTCL2 router, UTCL2 VML2, and UTCL2 walker weights, usually two signal weights per register with low and high halfword masks.
- `GC_CAC_OVRD_*` fields for block-specific override select/value bitmaps. The override width varies by block: single-bit domains such as IA/PC/SC/CU/SX/SXRB/TA/WD, wider block groups such as SPI/TD/EA, the 9-bit SQ override pair, and 10-bit UTCL2 router select/value fields.
- `EDC_STALL_PATTERN_*`, `PCC_STALL_PATTERN_*`, `PCC_THROT_REINCR_FIRST_PATN_*`, `PCC_THROT_DECR_FIRST_PATN_*`, `PWRBRK_STALL_PATTERN_CTRL`, `PWRBRK_STALL_PATTERN_*`, `PCC_PWRBRK_HYSTERESIS_CTRL`, and `FIXED_PATTERN_PERF_COUNTER_*`. These describe encoded stall/throttle lookup patterns, power-break hysteresis, and fixed-pattern performance counter fields.
- `SE_CAC_CNTL`, `SE_CAC_OVR_SEL`, and `SE_CAC_OVR_VAL` in the `secacind` block. These provide shader-engine CAC force-disable, threshold, block ID, signal ID, and full-width override selection/value fields.
- `SQ_DEBUG_STS_LOCAL`, `SQ_DEBUG_CTRL_LOCAL`, `SQ_WAVE_VALID_AND_IDLE`, `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_STS`, `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_INST_DW0/DW1`, `SQ_WAVE_IB_DBG0/DBG1`, `SQ_WAVE_FLUSH_IB`, `SQ_WAVE_TTMP0..15` except `TTMP2` in this visible range, `SQ_WAVE_M0`, and `SQ_WAVE_EXEC_LO/HI`. These define the SQ indirect wave debug/register-save view.
- `SQ_INTERRUPT_WORD_AUTO_CTXID`, `SQ_INTERRUPT_WORD_AUTO_HI/LO`, `SQ_INTERRUPT_WORD_CMN_CTXID`, `SQ_INTERRUPT_WORD_CMN_HI`, and `SQ_INTERRUPT_WORD_WAVE_CTXID/HI/LO`. These define packed SQ interrupt payload fields for thread-trace/timestamp/overflow events, common SE/encoding metadata, and wave-specific data such as shader array, privilege, wave ID, SIMD ID, CU ID, VM ID, and data payload bits.

There are no local type definitions. The effective "types" are 32-bit hardware register values interpreted through these shift/mask constants.

## Control Flow

This header has no runtime control flow. The runtime model is:

1. GC 9.4.2-specific code includes the generated offset and mask headers.
2. A caller selects a direct or indirect register offset, such as an `ixGC_CAC_*`, `ixSE_CAC_*`, or `ixSQ_WAVE_*` index from the matching offset header.
3. The caller composes or decodes a register value using the `__SHIFT` and `_MASK` macros in this file.
4. AMDGPU/KFD access helpers perform the actual MMIO or indirect read/write, and the hardware interprets the resulting packed value.

For CAC and throttle/power-pattern fields, sequencing is supplied by power-management, SMU, or initialization code that owns the relevant programming table. For SQ wave fields, debug and hang-analysis paths select a wave through SQ indirect access, then read these indexes to snapshot wave state. For SQ interrupt words, interrupt handlers decode payload words produced by hardware.

## State And Persistence Behavior

The macros are compile-time constants and persist no software state. The hardware fields they describe are stateful:

- CAC control, weight, and override fields persist in GPU registers until reset, power transition, reinitialization, or explicit reprogramming. Accumulator fields are hardware-updated counters whose reset/clear behavior is controlled by CAC hardware and surrounding driver sequences.
- SQ accumulator lower/upper pairs represent wider hardware counters. Consumers must treat the lower and upper reads as a coherent snapshot problem if hardware can update them between reads.
- PCC, EDC, and PWRBRK pattern/hysteresis/counter fields affect throttle behavior and expose performance or stall accounting. Some fields are durable configuration, while fixed-pattern counters and status-like fields are hardware-updated telemetry.
- `SE_CAC_CNTL` and override registers are shader-engine CAC configuration. These settings are hardware-owned and tied to the current ASIC power/performance configuration.
- SQ wave registers expose live execution state for a selected wave: mode bits, status/trap bits, hardware placement, GPR/LDS allocation, wait counters, PC, instruction dwords, instruction-buffer state, TTMP registers, M0, and EXEC. Values can change as waves execute, halt, trap, drain, or are context-saved.
- SQ interrupt word fields describe payloads delivered by interrupt/context-ID hardware. They are not persistent driver storage; they are decoded at interrupt handling time.

The header does not encode access permissions or side effects. A full-width mask may describe readback state, command data, or a scratch/debug value; it does not mean arbitrary writes are safe.

## Dependencies

This chunk depends on the generated GC 9.4.2 register database staying synchronized across:

- `gc_9_4_2_sh_mask.h`, which supplies the field masks and shifts researched here.
- The companion `gc_9_4_2_offset.h`, which supplies the matching `ix*`, `mm*`, or `reg*` register identifiers.
- AMDGPU field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`, which derive field names from the generated macro convention.
- SOC15 direct register addressing for ordinary GC registers and indexed/indirect access mechanisms for `gccacind`, `secacind`, and `sqind`.
- Power-management/SMU/CAC programming code that selects CAC blocks/signals, weights, overrides, and throttle patterns.
- GFX debug and reset-diagnostics code that reads SQ wave state through SQ indirect registers.
- KFD interrupt handling and trap/context-save code that relies on generation-specific SQ wave status, trap, allocation, and interrupt payload bit positions.

Although this source tree is under `sources/distributed-fs/ceph-client`, this file is AMD GPU hardware metadata and has no Ceph filesystem behavior.

## Integration Points

The primary integration point is the generated AMD GPU register include tree under `drivers/gpu/drm/amd/include/asic_reg/gc/`. Higher-level integration points include:

- GFX/SMU initialization and power-tuning paths that program CAC counters, weights, overrides, throttle patterns, power-break controls, and fixed-pattern performance counters.
- Driver code that reads CAC accumulators for activity, power, or diagnostics, including multi-register SQ accumulator reads.
- Shader-engine CAC configuration through `SE_CAC_CNTL`, `SE_CAC_OVR_SEL`, and `SE_CAC_OVR_VAL`.
- Debugfs, GPU reset, and hang-dump paths that select SQ waves and read `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, allocation registers, PC/instruction words, IB status/debug, TTMP, M0, and EXEC.
- KFD interrupt processing for SQ interrupt payloads. The same `SQ_INTERRUPT_WORD_*` layout pattern appears in GFX9 KFD code, where interrupt context IDs are decoded into thread-trace, overflow, wave ID, SIMD, CU, SE, privilege, and encoding information.
- KFD CWSR/trap handler assembly, which carries parallel constants for SQ wave status/trap/allocation behavior because save/restore code manipulates hardware wave state directly.

## Risks And Edge Cases

- The range starts mid-register at `GC_CAC_ACC_PA0`; the preceding line(s) from the prior chunk are needed to reconstruct the full `PA0` shift/mask pair in the merged per-file report.
- Header/offset mismatch is the main correctness risk. Pairing GC 9.4.2 masks with another GC generation's offset header can compile while programming the wrong fields.
- CAC override widths vary by block. Reusing an override mask from a similar block can overwrite adjacent fields or leave part of an override value unprogrammed.
- SQ accumulator lower/upper fields form a wider counter. Non-atomic reads can produce torn values if hardware updates the accumulator between lower and upper reads.
- Power/throttle pattern programming is performance- and stability-sensitive. Incorrect EDC/PCC/PWRBRK patterns, hysteresis, or first-pattern fields can cause unwanted throttling, power excursions, misleading counters, or hangs.
- SQ wave state is volatile and indirect. Callers must select the intended wave and tolerate races with wave execution, halt, trap, replay, context save/restore, or invalid wave slots.
- SQ interrupt word layouts are generation-sensitive. Similar names across GC generations do not guarantee identical payload packing, especially for context-ID versus high/low split formats.
- Reserved or unnamed bits are not documented by these macros. Read-modify-write sequences should preserve unrelated bits unless the ASIC programming sequence explicitly requires full-register writes.
- Full-width masks such as `0xFFFFFFFFL` occur for accumulators, override values, PC/instruction words, TTMP/M0/EXEC, and wave-slot bitmaps. Full-width masks are not proof that software owns every bit for writes.

## Test And Validation Signals

Useful validation is mostly build, static, and hardware coverage:

- Build coverage for AMDGPU and KFD paths that include the GC 9.4.2 offset/mask headers and use `REG_SET_FIELD`/`REG_GET_FIELD` with these names.
- Generated-header consistency checks that every field has a matching shift/mask pair, masks align with shifts, and register names match the companion GC 9.4.2 offset header.
- Static checks for non-overlapping fields inside each register, with expected exceptions for full-width data/counter registers and documented aliases.
- Power-management smoke tests on GC 9.4.2 hardware that initialize CAC, throttle, and power-break registers, then survive idle/load transitions, suspend/resume, and GPU reset.
- Activity-counter tests that verify CAC accumulators and fixed-pattern counters change plausibly under idle, graphics, and compute workloads, and that SQ upper/lower accumulator reads are handled coherently.
- SQ wave debug tests that capture wave dumps and decode mode, status, trap status, hardware ID, allocation, wait counters, PC, instruction dwords, TTMP/M0, and EXEC fields without malformed output.
- KFD interrupt tests that trigger thread-trace, timestamp, overflow, and wave-related interrupts and validate `SQ_INTERRUPT_WORD_*` decoding against known payloads.
- CWSR/trap save/restore tests for workloads that exercise trap, halt, replay, ECC/error, allocation, TTMP, and EXEC state bits.
