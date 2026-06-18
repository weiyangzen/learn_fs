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
