# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h lines 19164-20836

## Scope And Purpose

This chunk is the final line range of the GFX 8.0 shader/register mask header. It contains preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>_MASK` and matching `<REGISTER>__<FIELD>__SHIFT` definition. There are no functions, structs, storage objects, or executable control-flow paths in this range.

The chunk covers three major hardware-contract areas:

- `VGT_DEBUG_REG1` tail plus `VGT_DEBUG_REG2` through `VGT_DEBUG_REG36`, describing bit layouts for Vertex Grouper/Tessellator debug snapshot registers.
- `VGT_PERFCOUNTER*`, `IA_PERFCOUNTER*`, and `WD_PERFCOUNTER*`, describing performance counter select, mode, low, and high counter fields for VGT, input assembler, and work distributor blocks.
- `DIDT_*`, describing dynamic independent digital temperature/power-throttling controls, thresholds, weights, over-current protection limits, tuning registers, and indirect register index/data fields for SQ, DB, TD, TCP, and DBR blocks.

The header itself is a generated-style ASIC register description file. Its purpose is to let driver code form and decode 32-bit MMIO/indirect register values without hard-coded literals at each call site.

## Important APIs, Types, And Constants

There are no C APIs or types exported here. The usable interface is the macro namespace:

- `VGT_DEBUG_REG*__*_{MASK,__SHIFT}`: bitfield definitions for VGT debug reads. The fields expose internal pipeline state such as busy flags, FIFO empty/full flags, ready-to-receive/ready-to-send handshakes, primitive/index validity, GS/ES/VS table states, tessellation ring state, patch/edge FIFO state, active shader masks, and available ring-buffer space.
- `VGT_PERFCOUNTER_SEID_MASK__PERF_SEID_IGNORE_MASK_*`: shader-engine filtering for VGT performance counter collection.
- `VGT_PERFCOUNTER[0-3]_SELECT*__*`: event selector and mode fields. Counters 0 and 1 have wider multi-selector forms (`PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, `PERF_MODE*`), while counters 2 and 3 expose simpler `PERF_SEL` and `PERF_MODE` fields in this ASIC definition.
- `VGT_PERFCOUNTER[0-3]_{LO,HI}__PERFCOUNTER_*`: full-width 32-bit low/high halves for counter reads.
- `IA_PERFCOUNTER*` and `WD_PERFCOUNTER*`: analogous input-assembler and work-distributor performance counter field definitions.
- `DIDT_IND_INDEX__DIDT_IND_INDEX_*` and `DIDT_IND_DATA__DIDT_IND_DATA_*`: full-width fields for the indirect DIDT address and data registers.
- `DIDT_{SQ,DB,TD,TCP,DBR}_CTRL0`: enable/reset/clock/reference/phase fields for DIDT blocks. For SQ, TD, and TCP, this chunk also defines `DIDT_MAX_STALLS_ALLOWED_{HI,LO}` overlays on the corresponding `CTRL0` register.
- `DIDT_{SQ,DB,TD,TCP,DBR}_CTRL1`, `CTRL2`, and `CTRL_OCP`: min/max power, max power delta, interval size, long-term ratio, and OCP max power field layouts.
- `DIDT_{SQ,DB,TD,TCP,DBR}_WEIGHT0_3`, `WEIGHT4_7`, and `WEIGHT8_11`: packed 8-bit activity weights.
- `DIDT_{SQ,TD,TCP}_STALL_CTRL` and `DIDT_{SQ,TD,TCP}_TUNING_CTRL`: additional stall enable, stall delay, high-power threshold, and split max-power-delta tuning fields.

## Control Flow And State Behavior

This chunk has no local control flow. At compile time, including C files receive symbolic constants. Runtime behavior appears only in consumers:

- DIDT indirect reads and writes in `amdgpu/vi.c` and `amdgpu/cik.c` lock `adev->reg.didt.lock`, write `mmDIDT_IND_INDEX`, then read or write `mmDIDT_IND_DATA`. The masks in this chunk are used after those register accesses to preserve unrelated bits or place field values correctly.
- Power management code such as `pm/powerplay/hwmgr/smu7_powertune.c` stores tables of `{register, mask, shift, value, register-space}` entries. Those tables use the DIDT field macros here to program Polaris/SMU7 power-tune defaults through the DIDT indirect register path.
- Legacy DPM code such as `pm/legacy-dpm/kv_dpm.c` reads `ixDIDT_*_CTRL0`, toggles `DIDT_*_CTRL0__DIDT_CTRL_EN_MASK`, and writes the result back to enable or disable ramping for SQ, DB, TD, and TCP blocks.

State is persisted in GPU hardware registers, not in this header. Debug/performance fields are observational state when read from hardware. DIDT fields are configuration state whose values survive only according to GPU reset/power-management behavior; the header does not manage lifetime, caching, locking, or restore sequencing.

## Dependencies And Integration Points

This file is included by GFX 8-era AMDGPU and AMDKFD code through `gca/gfx_8_0_sh_mask.h`. It is paired with address headers such as `gfx_8_0_d.h`, where `mm*` and `ix*` register offsets are defined. The mask header is not useful by itself: code needs a register address macro plus these mask/shift macros to generate an MMIO value.

Important integration points visible from repository cross-references:

- `drivers/gpu/drm/amd/amdgpu/vi.c` and `cik.c` provide DIDT indirect accessor functions around `mmDIDT_IND_INDEX` and `mmDIDT_IND_DATA`.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_powertune.c` consumes many `DIDT_*` macros in static power-tune configuration tables.
- `drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.c` consumes `DIDT_*_CTRL0__DIDT_CTRL_EN_MASK` macros for runtime enable/disable toggles.
- AMDKFD VI queue/MQD managers include this header as part of the shared GFX 8 register vocabulary, though this specific chunk is primarily debug/perf/power-management oriented.

## Risks And Edge Cases

- Hardware contract drift is the main risk. These constants must match the exact GFX 8.0 register specification. A wrong mask or shift can write reserved bits, leave a power-management field unchanged, select the wrong performance event, or misdecode debug state.
- Some registers have full-width fields (`0xffffffff`) and some masks use an `L` suffix. Consumers should keep values unsigned/32-bit to avoid sign-extension or host-width surprises in arithmetic and formatting.
- DIDT registers are accessed indirectly through an index/data pair. Any consumer must serialize access, as `vi.c` and `cik.c` do with `adev->reg.didt.lock`; otherwise interleaved index/data operations can read or write the wrong indirect register.
- Several DIDT control fields are duplicated or overlaid late in the file, such as additional `DIDT_MAX_STALLS_ALLOWED_*` fields on `DIDT_SQ_CTRL0`, `DIDT_TD_CTRL0`, and `DIDT_TCP_CTRL0`. Table-driven code must use the exact mask/shift pair for the intended ASIC generation rather than assuming similarly named fields across GFX versions share layout.
- Debug register fields expose internal pipeline names (`rtr`, `rts`, `dr`, FIFO flags, `_q` latched state) that are easy to misinterpret. They are best treated as hardware diagnostic signals unless documentation ties a field to a stable software-visible behavior.
- The chunk ends with the header guard close. Any generated merge or patch must preserve this `#endif`; losing it breaks all users of the header.

## Test And Validation Signals

There are no direct unit tests for this macro chunk. Useful validation signals are integration-level:

- Compile coverage of AMDGPU/AMDKFD users that include `gfx_8_0_sh_mask.h`, especially files that build SMU7 power-tune tables and legacy DPM DIDT toggles.
- Static checks that every edited or regenerated field preserves mask/shift consistency: single-bit masks shift to their bit index; contiguous multi-bit masks shift down to a dense field; full-width fields have shift zero.
- Runtime power-management smoke tests on GFX 8 hardware: DIDT enable/disable paths should preserve unrelated bits and not trigger hangs, throttling regressions, or invalid register access warnings.
- Perf-counter tests or manual debugfs/perf instrumentation on supported ASICs can confirm `VGT`, `IA`, and `WD` selector fields map to expected events and counter values.
- Register dumps before and after SMU7/legacy DPM initialization should show only intended DIDT fields changing when table-driven programming applies masks and shifts.

## Chunk Notes For Merge Lane

This is a partial chunk of a much larger generated register mask header. Whole-file research should avoid describing this chunk as standalone logic. It should be merged as the tail section that supplies VGT debug/performance-counter and DIDT bitfield definitions for GFX 8-era AMDGPU register programming.
