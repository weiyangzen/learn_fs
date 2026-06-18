# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 15471-17691

## Purpose

This chunk is generated AMD DCN 3.5.0 register field metadata. It contains C preprocessor constants only: no executable functions, structs, enums, variables, locks, allocation, or persistence code. The exported contract is a large set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros used by AMDGPU display code to pack, update, read, and decode fields in DCN 3.5 MMIO registers.

The assigned range starts at `CURSOR0_3_DMDATA_ADDRESS_LOW` for cursor metadata instance 3, covers DC performance monitor instance 9, the DPP/CNVC/DSCL/CM register-field layouts for display pipe 0 and pipe 1, and ends inside the shift definitions for `DC_PERFMON11_PERFMON_CNTL`. It is a middle chunk of `dcn_3_5_0_sh_mask.h`; adjacent chunks own the preceding `CURSOR0_3_DMDATA_ADDRESS_HIGH` field and the remainder of `DC_PERFMON11`.

Although this source tree is rooted under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph, filesystem, distributed-storage, or network behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The important interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned bit mask for the field.
- Repeated instance prefixes such as `DPP_TOP0_`/`DPP_TOP1_`, `DSCL0_`/`DSCL1_`, `CNVC_CFG0_`/`CNVC_CFG1_`, `CNVC_CUR0_`/`CNVC_CUR1_`, `CM0_`/`CM1_`, and `DC_PERFMON9/10/11_` expose per-pipe or per-block copies of similar hardware layouts.

Major macro families in this slice:

- `CURSOR0_3_DMDATA_*`: display metadata registers for cursor/hubp instance 3. The chunk includes low address, hardware-mode control, QoS control, completion/underflow status and clear, software-mode control, and 32-bit software data fields.
- `DC_PERFMON9_*`, `DC_PERFMON10_*`, and the beginning of `DC_PERFMON11_*`: performance monitor counter selection, counted-value type, counter state, run/stop control, clock enable, interrupt status/acknowledge, current value, high/low readback, and report-count fields. The `DC_PERFMON11` group is incomplete in this chunk.
- `DPP_TOP0_*` and `DPP_TOP1_*`: DPP clock gating/enable, soft reset for CNVC/DSCL/CM/OBUF subblocks, DPP CRC readback/control, and host-read rate control.
- `DSCL0_*` and `DSCL1_*`: display scaler coefficient RAM selection/data, scaler mode and tap counts, 2-tap/sharpen controls, manual replication, horizontal/vertical scale ratios and initial phases for luma/chroma/bottom fields, black color, update-pending, autocal, overscan, timing blank windows, recout/MPC size, line-buffer data/memory controls, line-buffer counters, DSCL/LB memory power state, and output-buffer controls.
- `CNVC_CFG0_*` and `CNVC_CFG1_*`: converter surface pixel format, format expansion/conversion, alpha-plane enable, bypass/alignment/clamping, channel crossbar, floating-point conversion bias/scale, color keyer ranges, 2-bit alpha LUT, pre-dealpha, pre-CSC matrices and double-buffered B matrices, coefficient format, pre-degamma, and pre-realpha fields.
- `CNVC_CUR0_*` and `CNVC_CUR1_*`: cursor color-converter controls for cursor enable, mode, expansion, pixel inversion, ROM enable, alpha modulation, update-pending, 24-bit palette colors, and FP scale/bias.
- `CM0_*` and `CM1_*`: color-management bypass/update-pending, post-CSC matrices and B matrices, gamut-remap matrices and B matrices, bias, gamma-correction control, gamma LUT index/data/control, gamma RAM A/B start/end/slope/base/offset definitions, 34-region LUT segmentation pairs, HDR multiplier coefficient, gamma memory power control/status, dealpha, and coefficient-format fields.

The chunk also includes a `CM0_CM_TEST_DEBUG_INDEX` field pair, which is an indexed debug selector/write-enable style interface for the CM block.

## Control Flow

This header has no local runtime control flow. Runtime behavior is supplied by AMD display code that includes this generated mask header together with the matching offset header:

1. DCN 3.5 resource, IRQ, and DMUB files include `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-list macros in files such as `dcn35_resource.c`, `dcn35_dpp.h`, and common DPP/HUBP headers paste generated register and field tokens into shift and mask identifiers.
3. Resource construction stores these generated constants in per-block register, shift, and mask tables, for example DPP pipe tables created through `DPP_REG_LIST_DCN35_RI(id)` and `DPP_REG_LIST_SH_MASK_DCN35(__SHIFT/_MASK)`.
4. Operational code later uses helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and block-specific wrappers. Those helpers combine register offsets from `dcn_3_5_0_offset.h` with shift/mask constants from this file.

The macros themselves do not encode programming order. Cursor metadata code must still order DMDATA address, size, mode, updated/repeat bits, QoS, and status clear operations correctly. DPP code must still coordinate scaler programming, coefficient RAM updates, CNVC format setup, color-management LUT/matrix programming, double-buffer updates, memory power transitions, CRC control, and soft resets around mode-set and plane-update sequencing.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO-backed GPU state whose lifetime is controlled by display hardware, power management, reset, suspend/resume, and modeset reprogramming.

Represented hardware state includes:

- Cursor display metadata state for pipe/cursor instance 3: DMDATA low address, hardware/software mode, packet size, repeat/update latches, QoS mode/level/deadline delta, done status, underflow status, and underflow clear.
- Perfmon state for instances 9 and 10, plus the start of instance 11: event selector, counted-value type, run-enable and stop/start selection, counter active state, interrupt enable/status/acknowledge, high/low/current values, and report count.
- DPP top-level state: DPP clock enable/gating overrides, subblock soft-reset bits, CRC enable/one-shot/continuous/source/pixel-format/stereo/interlace/cursor-format masks, CRC results, and host-read throttling.
- DSCL state: scale ratios and phase accumulators, luma/chroma tap counts, coefficient RAM contents and bank selection, scaler mode, overscan/timing/recout geometry, line-buffer layout and partitioning, output-buffer bypass/hold behavior, and DSCL/LB/OBUF memory power force/disable/status bits.
- CNVC state: surface pixel format, alpha-plane handling, format expansion/conversion, component crossbar, positive clamp, color-key thresholds, pre-CSC matrix selection/current state, pre-degamma and pre-alpha behavior, FP conversion bias/scale, and cursor color conversion.
- CM state: post-CSC and gamut-remap matrices, bias, gamma LUT host/index/data selection, gamma RAM A/B PWL region definitions, HDR multiplier, dealpha behavior, coefficient formats, and gamma memory power state.

Some fields are configuration latches; others are live status, update-pending readback, interrupt/status acknowledge, clear bits, or counters. This generated header does not identify access type, self-clearing behavior, write-one-to-clear semantics, read-only fields, or required delays. Consumers must rely on block-level driver code and the ASIC programming guide for those semantics.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which defines matching `reg...` offsets and base-index constants. For this chunk, notable companion offsets include `regCURSOR0_3_DMDATA_*`, `regDC_PERFMON9_*`, `regDC_PERFMON10_*`, `regDC_PERFMON11_*`, `regDPP_TOP0_*`, and `regDPP_TOP1_*`.

Visible DCN 3.5 include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`, which includes the offset and mask headers and constructs DCN 3.5 block register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, which includes the same generated headers for DCN 3.5 interrupt table support.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which includes the generated DCN 3.5 register metadata for DMUB-side display-microcontroller access.

The DPP integration path is token-paste based. `dcn35_resource.c` initializes per-pipe DPP tables through `DPP_REG_LIST_DCN35_RI(id)` and initializes `struct dcn35_dpp_shift`/`struct dcn35_dpp_mask` through `DPP_REG_LIST_SH_MASK_DCN35`. That field list extends common DPP/DCN3 lists, which consume many macros in this chunk: `DPP_TOP0_DPP_CONTROL`, `DSCL0_*`, `CNVC_CFG0_*`, `CNVC_CUR0_*`, and `CM0_*`. Instance-specific register-list macros map the `0` field names across physical DPP instances.

The cursor DMDATA macros integrate with HUBP code families. Common HUBP field lists in nearby generations consume names such as `CURSOR0_0_DMDATA_CNTL`, `DMDATA_UPDATED`, `DMDATA_SIZE`, `DMDATA_QOS_LEVEL`, and `DMDATA_DONE`; the DCN 3.5 generated instance-3 names in this chunk are the same hardware contract for the fourth pipe/cursor instance.

Because the integration uses preprocessor token pasting, macro spelling is part of the compile-time ABI between generated register headers and AMD display code. A missing, renamed, or stale shift/mask macro can either break compilation or compile while sending `REG_UPDATE` to the wrong bitfield.

## Risks And Edge Cases

- Generated masks are untyped numeric constants. A wrong shift or mask can pass compilation and only appear as hardware-specific display corruption, missing cursor metadata, broken scaling, bad color, or invalid diagnostics.
- The chunk begins after `CURSOR0_3_DMDATA_ADDRESS_HIGH`. Whole DMDATA programming requires both high and low address fields; reviewing this chunk alone cannot validate the full address path.
- DMDATA update/status fields are stateful and timing-sensitive. Bad masks for `DMDATA_UPDATED`, `DMDATA_SIZE`, `DMDATA_QOS_LEVEL`, `DMDATA_DONE`, or `DMDATA_UNDERFLOW_CLEAR` can cause stale metadata, underflows, hidden faults, or repeated metadata transmission.
- Perfmon fields are diagnostic but still side-effect sensitive. Bad counter event, run-enable, interrupt, clear/ack, or read-select masks can corrupt performance data, hide counter overflows, or create spurious interrupts.
- DPP clock gating and soft reset bits can affect active display pipes. Incorrect `DPP_CLOCK_ENABLE`, clock-gate disable, or subblock reset masks may cause intermittent blanking, hangs, or resume-only failures.
- DSCL fields are dense fixed-point geometry and filter controls. Off-by-one shifts in ratio/init/tap/coef fields can produce scaling artifacts, chroma misalignment, overscan errors, line-buffer underflow, or corruption only for specific source/destination sizes.
- CNVC and CM fields directly affect pixel interpretation and color output. Bad format, alpha, color-key, CSC, gamut-remap, gamma, bias, or HDR multiplier masks can create subtle color regressions, wrong alpha blending, cursor color issues, or failures in HDR/wide-gamut modes.
- Gamma RAM A/B and LUT region registers are large repeated tables. Region pair masks must remain consistent across indices 0-33; a single wrong field can damage only part of a PWL transfer function, making failures hard to isolate visually.
- Memory power force/disable/status bits for DSCL, OBUF, and CM are power-state sensitive. Incorrect masks can leave memories powered off while in use or prevent intended low-power transitions.
- `DC_PERFMON11` is split by the chunk boundary. This document covers only its `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, and the first `PERFMON_CNTL` shift definitions; masks and remaining registers are in the next chunk.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU/DC with DCN 3.5 enabled. Token-paste consumers in `dcn35_resource.c`, `irq_service_dcn35.c`, `dmub_dcn35.c`, common DPP code, and HUBP paths should catch missing or renamed macros.
- Mechanically verify every `__SHIFT` macro in this line range has a matching `_MASK` macro where the chunk contains the complete field pair, and that each mask width aligns with the shift and intended field width.
- Cross-check each register in this range against `dcn_3_5_0_offset.h` to ensure the field macros have matching offsets and base indices.
- Diff this chunk against AMD's authoritative DCN 3.5 register database and nearby generated headers such as `dcn_3_2_0_sh_mask.h`, `dcn_3_5_1_sh_mask.h`, or later DCN headers where block layouts are expected to remain compatible.
- Exercise DMDATA paths using hardware and software metadata modes, including repeated metadata, large metadata sizes near the 12-bit size limit, QoS mode changes, underflow injection or stress, and pipe 3 usage.
- Exercise DPP/DSCL paths with scaling up/down, non-integer ratios, chroma subsampling, interlaced/bottom-field cases, overscan, line-buffer pressure, coefficient RAM updates, and repeated modesets.
- Exercise CNVC and CM paths with varied pixel formats, alpha plane enablement, color keying, cursor color modes, pre-CSC/post-CSC, gamut remap, gamma LUT updates, HDR multiplier, and suspend/resume.
- Use CRC/perfmon/debugfs or internal diagnostics where available to verify DPP CRC enable/one-shot/readback behavior and perfmon counter selection/readback for instances 9-11.
- Watch for symptoms such as blanking during modeset, scaler artifacts, color shifts, broken HDR/gamma, wrong cursor colors, metadata underflow logs, invalid perf counters, interrupt storms, or resume-only display failures.

## Cross-Chunk Notes

This is chunk 8 of 25 for `dcn_3_5_0_sh_mask.h`. The previous chunk contains earlier HUBP/cursor metadata fields including `CURSOR0_3_DMDATA_ADDRESS_HIGH`. The next chunk completes `DC_PERFMON11_PERFMON_CNTL` and continues later DCN 3.5 register-field families. The final per-file report should merge this chunk with adjacent chunks before drawing conclusions about complete DPP, DMDATA, or perfmon coverage.
