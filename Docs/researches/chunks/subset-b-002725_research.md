# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 19049-21368

## Scope And Purpose

This chunk is the final range of the generated AMD GFX 8.1 register-mask header. It contains C preprocessor constants for bit masks and shifts, not executable code. The covered register families are:

- `WD_DEBUG_REG7` through `WD_DEBUG_REG10`, exposing Work Distributor debug/status bits for shader-engine arbitration, thread-group traffic, TF/TC handshakes, patch/TF fetch state, and WD-to-TE output FIFOs.
- `IA_DEBUG_REG0` through `IA_DEBUG_REG9`, exposing Input Assembler busy flags, normal and high-priority DMA paths, DMA pipeline stages, pipe request arbitration, FIFO occupancy, current index/data state, EOP/null flags, and TC/MC return-path status.
- `VGT_DEBUG_REG0` through `VGT_DEBUG_REG36` except skipped/reserved numbers, exposing Vertex Grouper/Tessellator pipeline debug state, event/EOP markers, counters, shader-engine/pipe routing state, DMA/IA/WD handshakes, and several reserved/spare bitfields.
- `VGT_PERFCOUNTER*`, `IA_PERFCOUNTER*`, and `WD_PERFCOUNTER*` selector and data registers, defining event-selection, counter mode, perf mode, and 64-bit low/high counter halves for VGT, IA, and WD blocks.
- `DIDT_IND_INDEX` and `DIDT_IND_DATA`, the indirect access window for DIDT registers.
- `DIDT_{SQ,DB,TD,TCP,DBR}_CTRL*`, `*_CTRL_OCP`, and `*_WEIGHT*` registers, defining dynamic power/current control fields for Shader Queue, Depth Block, Tessellator, Texture Cache Pipe, and Depth Buffer/DBR domains.

The file closes the `GFX_8_1_SH_MASK_H` include guard at line 21368. The companion address header is `gfx_8_1_d.h`; this header supplies only the field layout for composing or decoding 32-bit register values.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The effective interface is the macro naming convention:

- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for a field.
- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for the same field.

Driver code typically uses these macros directly with bitwise operations or through AMD helper macros such as `REG_SET_FIELD`/`REG_GET_FIELD` when the register family is available to those helpers. The DIDT fields in this chunk are visibly consumed by power-management code. For example, `kv_dpm.c` reads and writes DIDT indirect registers with `RREG32_DIDT`/`WREG32_DIDT`, toggling fields such as `DIDT_SQ_CTRL0__DIDT_CTRL_EN_MASK`, `DIDT_DB_CTRL0__DIDT_CTRL_EN_MASK`, `DIDT_TD_CTRL0__DIDT_CTRL_EN_MASK`, and `DIDT_TCP_CTRL0__DIDT_CTRL_EN_MASK`. `smu7_powertune.c` uses the same mask/shift pairs in configuration tables for DIDT weights, min/max power limits, interval sizing, phase/clock controls, and enable bits.

The debug and perf-counter macros are lower-level register definitions. They are integration points for debugfs, perf-counter programming, bring-up diagnostics, GPU hang triage, and any ASIC-specific code that has selected the GFX 8.1 register layout. They do not perform reads or writes by themselves.

## Register Groups

### Work Distributor Debug Registers

`WD_DEBUG_REG7` continues WD debug coverage from earlier chunks. It exposes per-shader-engine arbitration and thread-group signals: SE0/SE1 input FIFO empty/full/read state, `SE1VGT_WD_thdgrp_send_in`, `se*_thdgrp_is_event`, `se*_thdgrp_eop`, `tfreq_arb_tgroup_rtr`, `arb_tfreq_tgroup_rts`, `arb_tfreq_tgroup_event`, and `te11_arb_busy`. These fields are useful when diagnosing whether thread groups are stuck before or after WD arbitration.

`WD_DEBUG_REG8` and `WD_DEBUG_REG9` describe TF/TC and TTP pipeline handshakes: `pipe*_dr`, `pipe*_rtr`, TF data/skid FIFO empty/full/busy/count state, TC read request/return valid/stall bits, first/last request markers, event/null flags, `ttp_patch_fifo_*`, `ttp_tf_fifo_empty`, `tf_fetch_state_q`, `tf_pointer_p0_q`, dynamic hull-shader state, and pipe4 traffic. Together they show whether WD is blocked by TF fetch, TC memory return, or patch FIFO state.

`WD_DEBUG_REG10` covers TTP-to-patch/PD state and WD output toward TE instances. It contains patch/event/EOP/EOPG flags, pipe handshakes, donut and patch shader-engine switching markers, `patch_accum_q`, and per-SE `wd_te11_out_se{0..3}_fifo_full/empty` flags. These fields are diagnostic state only, but stale or incorrect masks would make WD hang dumps misleading.

### Input Assembler Debug Registers

`IA_DEBUG_REG0` is a top-level IA activity summary. It includes extended and non-DMA busy state, DMA request/busy state, MC translator busy state, group busy/read/valid flags, clock-busy flags, and sclk validity flags.

`IA_DEBUG_REG1` and `IA_DEBUG_REG2` are parallel normal and high-priority DMA decode/status maps. Both expose input FIFO empty/full, start-new-packet markers, DMA request valid state, zero-index and buffer-type bits, request path, discard-first/second-chunk flags, TC return selection, last-read-request state, mask/data/request FIFO status, stage2-stage4 valid/ready handshakes, skid FIFO status, group DMA valid/read bits, current-data-valid, out-of-range detection, mask FIFO write enable, and return-data write enable. This symmetry is important: normal and high-priority DMA paths must be decoded with their own `hp_` masks rather than by reusing normal-path fields.

`IA_DEBUG_REG3` through `IA_DEBUG_REG9` cover per-pipe read-request validity/read/null/EOP/use-TC bits, MC/TC request ready/send state, pair/quad assembly state, current and previous index/data registers, EOP/null flags, DMA counter state, output FIFO state, and pipe selection arbitration. These fields bridge IA's front-end fetch/decode logic to VGT/WD and memory clients.

### VGT Debug Registers

`VGT_DEBUG_REG0` through `VGT_DEBUG_REG36` form the largest part of the debug range. The fields are mostly raw internal state from the VGT front end: busy/active signals, input and output FIFO status, per-pipe draw/request handshakes, primitive/thread-group/event/EOP flags, state-machine values, per-SE routing, counters, reserved `SPARE*` fields, and handshakes with IA, WD, and tessellation/geometry units.

Because these are generated hardware definitions, the field names are the authoritative semantic labels. Driver code should treat reserved/spare fields as read-only diagnostics unless the hardware programming guide explicitly assigns behavior. The dense use of `*_state_q`, `*_cnt_q`, `*_fifo_*`, `*_rtr`, and `*_dr` names indicates sampled pipeline state rather than persistent software state.

### Performance Counters

The VGT, IA, and WD perf-counter blocks use the same broad pattern:

- Select registers hold event selectors and modes. `VGT_PERFCOUNTER0_SELECT`/`1_SELECT` and `IA_PERFCOUNTER0_SELECT` can select two events (`PERF_SEL` and `PERF_SEL1`) plus `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`. VGT/IA select1 registers add `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`. Later counters expose narrower selectors with `PERF_SEL` and `PERF_MODE`.
- `WD_PERFCOUNTER0_SELECT` through `WD_PERFCOUNTER3_SELECT` each define an 8-bit `PERF_SEL` and upper-nibble `PERF_MODE`.
- Each counter has `*_LO__PERFCOUNTER_LO_MASK` and `*_HI__PERFCOUNTER_HI_MASK`, both full-width `0xffffffff`, so software must combine low and high halves carefully when reading a 64-bit count.
- `VGT_PERFCOUNTER_SEID__SEID_MASK` selects the shader-engine instance for VGT counter collection.

Programming these counters requires address definitions from the matching `gfx_8_1_d.h` file plus an ordering policy from the caller. This header only defines the field layout.

### DIDT Power Control Registers

`DIDT_IND_INDEX` and `DIDT_IND_DATA` are full-width 32-bit fields for selecting and accessing indirect DIDT registers. In the AMDGPU driver, indirect DIDT access is serialized by `adev->reg.didt.lock` in ASIC helpers such as `cik_didt_rreg`/`cik_didt_wreg` and `vi_didt_rreg`/`vi_didt_wreg`: the driver writes the index register, then reads or writes the data register.

The DIDT block definitions repeat the same register pattern across `SQ`, `DB`, `TD`, `TCP`, and `DBR`:

- `*_CTRL0` has enable, reference-clock, phase-offset, reset, clock-enable-override, and unused/reserved fields.
- `*_CTRL1` has `MIN_POWER` and `MAX_POWER` half-word fields.
- `*_CTRL2` has `MAX_POWER_DELTA`, `SHORT_TERM_INTERVAL_SIZE`, `LONG_TERM_INTERVAL_RATIO`, and reserved fields.
- `*_CTRL_OCP` provides an over-current protection maximum power field plus reserved bits.
- `*_WEIGHT0_3`, `*_WEIGHT4_7`, and `*_WEIGHT8_11` pack four 8-bit weight values per register.

PowerTune code uses these masks and shifts to build tables of per-domain DIDT parameters, then applies them through indirect DIDT register writes. The repeated layout across domains lowers software complexity but increases the risk of copy/paste mistakes when adding or adjusting a domain.

## Control Flow

This header contributes no control flow. Runtime flow is supplied by callers:

1. Include the ASIC address and mask headers matching the detected GPU generation.
2. Read a register or construct a new register value.
3. Clear a field with `value &= ~FIELD_MASK`.
4. Insert a field with `(field_value << FIELD_SHIFT) & FIELD_MASK`, or use a register-field helper.
5. Write the register through the correct MMIO or indirect register accessor.

DIDT indirect access has an extra two-step control flow: callers select the DIDT offset via `DIDT_IND_INDEX` and then transfer the value through `DIDT_IND_DATA`. Existing ASIC accessors lock around that index/data pair to avoid races between concurrent readers and writers.

## State And Persistence Behavior

The macros are compile-time constants and have no in-memory state. The state they describe lives in hardware registers:

- Debug registers are sampled hardware status. Reads reflect transient GPU pipeline state and are primarily useful during diagnostics, hang analysis, and hardware validation.
- Perf-counter select registers persist until reprogrammed or reset by the GPU/IP block. Counter low/high registers accumulate hardware events according to the selected event and mode.
- DIDT registers persist hardware power-control configuration until reset, suspend/resume reinitialization, ASIC reset, or another power-management path rewrites them.

Because DIDT and perf-counter fields affect live hardware behavior, caller-side read-modify-write sequencing matters. Reserved fields must be preserved unless the programming sequence intentionally initializes the entire register.

## Dependencies And Integration Points

This chunk depends on the matching GFX 8.1 register address header for `mm*` and `ix*` register offsets. It integrates with:

- AMDGPU register access helpers such as `RREG32`, `WREG32`, `RREG32_DIDT`, and `WREG32_DIDT`.
- ASIC-specific indirect DIDT accessors in `cik.c` and `vi.c`, which serialize `DIDT_IND_INDEX`/`DIDT_IND_DATA` access.
- Power-management code in `pm/legacy-dpm/kv_dpm.c` and `pm/powerplay/hwmgr/smu7_powertune.c`, which uses DIDT mask/shift pairs to enable blocks and program power-tuning tables.
- Debug and performance tooling paths that decode VGT/IA/WD debug registers or program/read their performance counters.
- Generated-register conventions shared with nearby headers such as `gfx_8_0_sh_mask.h`, later `gc_*_sh_mask.h` files, and helper macros that assume the `<REGISTER>__<FIELD>_{MASK,__SHIFT}` naming scheme.

## Risks And Edge Cases

- Mask/shift mismatches are high-impact despite the file being declarative: an incorrect mask can silently set reserved bits, fail to enable DIDT, select the wrong perf event, or misdecode a debug dump.
- The DIDT indirect window is race-prone if accessed without the existing lock. Interleaved index/data operations can read or write the wrong DIDT register.
- Full-width counter halves require careful 64-bit reads. If callers read high/low halves without considering rollover, sampled perf counts can be inconsistent.
- Debug fields are transient; tests or diagnostics that expect stable FIFO/handshake state must account for GPU activity and clock/power gating.
- Repeated DIDT layouts across `SQ`, `DB`, `TD`, `TCP`, and `DBR` invite wrong-domain macro use. A value intended for one domain may have the same bit layout but target a different hardware block.
- Reserved `SPARE*` and `UNUSED_*` fields should not be interpreted as stable software-visible ABI. They may differ across ASIC revisions even when nearby functional fields look similar.
- This is a generated hardware header. Manual edits can diverge from hardware source data and should be avoided unless they are part of a verified register-definition update.

## Test Signals

There are no direct unit tests for this header in the chunk. Useful validation signals are indirect:

- Successful compilation of AMDGPU code that includes GFX 8.1 register headers and references these masks.
- Power-management tests or hardware smoke tests that enable/disable DIDT on supported ASICs and verify stable clocks, power limits, and no GPU reset/hang.
- Register readback tests for DIDT programming: after table application, reading each DIDT register should show expected field values while preserving reserved bits.
- Perf-counter tests that program VGT/IA/WD selector fields, run known GPU workloads, and observe nonzero, monotonic, and domain-plausible low/high counter values.
- Debugfs or hang-dump validation that decodes VGT/IA/WD debug registers without field overlap, impossible bit positions, or all-zero/all-reserved interpretation.
- Static checks can verify that every field has exactly one mask and one shift, that masks do not overlap within a register except for documented full-register fields, and that `(mask >> shift)` has the intended field width.
