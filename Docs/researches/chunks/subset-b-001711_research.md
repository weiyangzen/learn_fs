# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 59134-61618

## Scope

This chunk is a late slice of AMD's generated DCN 3.0.0 register shift/mask header. It contains 2,123 `#define` entries and 348 register/address-block comments, but no C functions, structs, enums, global variables, includes, allocation paths, or executable control flow. The exported interface is the generated `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` namespace consumed by register helper macros.

The range begins in the middle of `MPC_RMU0_SHAPER_RAMB_END_CNTL_B`, covers the rest of the `MPC_RMU0` shaper/3DLUT fields, complete analogous `MPC_RMU1` and `MPC_RMU2` shaper/3DLUT field groups, DC perfmon blocks 28 and 29, stream packet/audio fields for instance 6 (`AFMT6`, `VPG6`, `DME6`), `HPO_TOP_CLOCK_CONTROL`, complete ABM field groups for `ABM0` and `ABM1`, and the first part of `ABM2` through `ABM2_DC_ABM1_ACE_THRES_12`.

Although this source tree is under a local `ceph-client` mirror, the file is AMDGPU display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this chunk is to describe bit layouts for DCN 3.0 display hardware registers so runtime driver code can read, compose, and update MMIO fields without hard-coding shifts and masks at each call site. It pairs with `dcn_3_0_0_offset.h`, which supplies register addresses. Consumers typically include both files and feed these constants into macros such as `SF`, `FD_SHIFT`, `FD_MASK`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and `REG_WRITE`.

The covered hardware areas are:

- MPC RMU shaper and 3D LUT color-management fields for RMU instances 0, 1, and 2.
- DC performance monitor field layouts for counters 28 and 29.
- `AFMT6`, `VPG6`, and `DME6` stream-output support fields for audio, infoframes, generic packets, ISRC/MPEG metadata, CRC/status, memory power, and DME control.
- HPO top-level clock-gating control.
- ABM/backlight fields for ambient light input, user/target/current levels, final/minimum duty cycle, ABM enablement, frame-rate update control, grouped register locking, ACE curve programming, histogram/luma statistics, sample-rate control, histogram result readback, and master lock.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. Its only API surface is generated preprocessor constants:

- `REGISTER__FIELD__SHIFT`: bit position for a field.
- `REGISTER__FIELD_MASK`: bit mask for the same field.
- Register comments such as `//MPC_RMU1_3DLUT_MODE` and address-block comments such as `// addressBlock: dce_dc_opp_abm0_dispdec` group the constants by hardware block.

Important field groups:

- `MPC_RMU[0-2]_SHAPER_*`: shaper enable/mode, per-channel offsets and scales, LUT index/data, write-enable mask, RAM A/B start/end controls, and 34 exponential-region descriptors per RAM bank. Region pairs use LUT-offset fields and segment-count fields; start/end controls split per-channel end/base values.
- `MPC_RMU[0-2]_3DLUT_*`: 3D LUT mode, size, current mode readback, index, packed data writes, 30-bit data path, read/write control fields such as write-enable mask, RAM select, 30-bit enable, config status, and read select, plus output normalization and RGB offsets.
- `DC_PERFMON28_*` and `DC_PERFMON29_*`: event-selection, counter-control, counter-state, perfmon-run control, interrupt status/ack, low/high counter readback, and current-value misc fields.
- `AFMT6_*`: VBI/audio packet control, audio layout override, audio info fields, IEC 60958 channel-status fields, CRC control/result/status, ramp controls, packet enables, infoframe control, audio source selection, and memory power.
- `VPG6_*`: generic packet access/data, generic-stream-packet frame and immediate update controls, update locks and pending flags, generic status, memory power, ISRC access/data, and MPEG info fields.
- `DME6_*`: DME enable/reset, ready/status, clock gating, memory low-power, and shut-down control fields.
- `HPO_TOP_CLOCK_CONTROL`: HPO top clock-gating disable field.
- `ABM[0-2]_*`: PWM level fields, ABM enable and auto-update controls, grouped register lock/update behavior, ABM processing enable/bypass, IPCSC coefficient selection, ACE slopes/offsets/thresholds, histogram/luma-sensor read-progress flags, histogram bin controls, luma sums/min/max/counts, sample-rate frame counters, histogram result registers, and backlight master lock.

## Control Flow

This header has no runtime control flow. Its effect is compile-time symbol resolution:

1. DCN 3.0 display code includes `dcn_3_0_0_sh_mask.h` with the matching offset header.
2. Register-list macros paste register and field names into `SF(...)`/`FD_*` macro invocations.
3. The resulting shift/mask tables are stored in per-block structures such as ABM, VPG, AFMT, stream encoder, DMUB, IRQ, GPIO, and clock-manager register metadata.
4. Runtime code uses those tables through MMIO helpers to program color LUTs, packet generators, audio formatting, performance counters, HPO clock state, ABM backlight processing, and histogram/luma measurement.

Runtime ordering is external to this header. Consumers must still sequence power/clock enablement, LUT RAM selection, shaper/3DLUT programming, frame-synchronized packet updates, ABM grouped-register locking, histogram sampling, perfmon run/ack handling, and suspend/resume restoration.

## State And Persistence Behavior

The chunk stores no software state and writes no persistent files. It describes MMIO-backed hardware state:

- MPC RMU state includes shaper/3DLUT mode, active RAM bank selection, LUT payload, region layout, output normalization, and offset/scale state. These values affect color processing until reprogrammed, disabled, power-gated, or reset.
- VPG/AFMT/DME state controls secondary-data packets, audio payload metadata, CRC/status reporting, memory power, and DME block readiness for stream instance 6.
- Perfmon state includes selected events, counter enable/run state, sampled counter values, and sticky interrupt/ack state.
- ABM state includes backlight PWM levels, ambient/user/target/current/final values, auto-update configuration, ACE curve coefficients, histogram/luma sample results, read-progress flags, register lock state, and master lock state.

The macros do not encode access permissions or side effects. Some represented fields are ordinary read/write controls, some are read-only status/counter fields, and some are sticky clear/ack or lock fields. Callers must use the register programming model, not just the macro name, to decide whether read-modify-write is safe.

## Dependencies And Integration Points

This chunk depends on generated consistency with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h` for register addresses and base-index selection.
- SOC/DCN base-address headers such as `sienna_cichlid_ip_offset.h`.
- AMD display helper macros in `dm_services.h`, `dmub_reg.h`, and DC block headers that build field metadata from `SF`, `FD_MASK`, and `FD_SHIFT`.

Observed direct include sites for the DCN 3.0 mask/offset pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Specific integration patterns visible in nearby code:

- `dcn30_resource.c` instantiates `abm_regs`, `abm_shift`, and `abm_mask` with `ABM_DCN30_REG_LIST` and `ABM_MASK_SH_LIST_DCN30`, then creates per-pipe DMUB ABM objects. It also instantiates `vpg_regs`/`vpg_shift`/`vpg_mask` and `afmt_regs`/`afmt_shift`/`afmt_mask` for stream encoders.
- `dce/dmub_abm_lcd.c` programs fields from this ABM namespace through calls such as `REG_WRITE(DC_ABM1_HG_SAMPLE_RATE, ...)`, `REG_SET_3(DC_ABM1_HG_MISC_CTRL, ...)`, `REG_UPDATE(BL1_PWM_CURRENT_ABM_LEVEL, ...)`, and `REG_SET_3(DC_ABM1_HGLS_REG_READ_PROGRESS, ...)`.
- `dc/dpp/dcn10/dcn10_dpp.h` shows the broader color-management table shape for shaper and 3DLUT fields, including RAM A/B region descriptors, 3DLUT mode/index/data/read-write controls, and shaper LUT data/index registers. The RMU names in this chunk are the DCN 3.x MPC/RMU-side equivalents of that style of field metadata.

## Risks And Edge Cases

- A wrong shift or mask compiles cleanly but can corrupt hardware programming. This is especially risky for full-width masks, lock bits, clear/ack bits, and packed fields with adjacent channel data.
- The chunk starts and ends inside logical register groups. `MPC_RMU0_SHAPER_RAMB_END_CNTL_B` begins before this range, and `ABM2_DC_ABM1_ACE_THRES_12` continues after it. Whole-file analysis must merge adjacent chunks before claiming complete RMU0 or ABM2 coverage.
- Repeated instance families are copy-sensitive. `MPC_RMU0`, `MPC_RMU1`, `MPC_RMU2`, `ABM0`, `ABM1`, and `ABM2` use nearly identical field layouts; an instance-specific typo may only break one plane, pipe, panel, or multi-display configuration.
- LUT and shaper programming is stateful. Incorrect RAM selection, index increments, write-enable masks, 30-bit mode, or region descriptors can produce color corruption that may only appear with plane 3D LUT, HDR/color-management, or specific LUT dimensions.
- ABM fields combine backlight controls, histogram/luma measurement, grouped register locks, and DMUB-managed firmware behavior. Bad masks can cause incorrect brightness, flicker, missed frame updates, stuck locks, histogram readback failures, or ABM state divergence after suspend/resume.
- VPG/AFMT instance 6 may be exercised only on systems or configurations with enough stream encoders. Errors in these fields can escape single-display testing and appear as audio loss, bad infoframes, bad generic packets, ISRC/MPEG metadata failures, or CRC/status anomalies.
- Perfmon fields can have sticky or write-one-to-clear behavior. Using an interrupt-ack mask in a generic update path can drop evidence or leave counters in a stuck state.
- Clock/power fields such as HPO clock gating and DME/VPG/AFMT memory power must be programmed only when their blocks are in a valid clock/reset state; this header cannot enforce that sequencing.

## Test Signals

Useful validation signals are mostly compile-time consistency plus hardware exercise:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.0.2 enabled. Missing or renamed fields should fail at macro expansion in resource, DMUB, IRQ, GPIO, clock, ABM, VPG, AFMT, and stream-encoder code.
- Mechanically verify that every `__SHIFT` macro in lines 59134-61618 has a matching `_MASK` macro with the same `REGISTER__FIELD` prefix, accounting for the artificial range boundaries at the first and last registers.
- Compare this chunk against AMD's generated register database and nearby DCN versions where field layouts are expected to remain compatible.
- Exercise color-management paths that use shaper LUTs and 3DLUTs: plane color properties, 17-cube and 9-cube LUT modes, host/DMA LUT loading where applicable, HDR/degamma/gamma transitions, modesets, and suspend/resume.
- Exercise stream encoder instance 6 where hardware supports it: DP/HDMI modesets, generic packets, audio playback, audio channel-status fields, infoframes, MPEG/ISRC metadata, CRC capture, and memory-power transitions.
- Run ABM/backlight tests on eDP panels: initial backlight programming, ABM level changes, ambient-level updates, PWM fraction changes, pause/save/restore, panel mask selection, histogram/ACE readback, and suspend/resume.
- Configure DC perfmon counters 28 and 29, validate event selection, low/high readback, run/stop state, interrupt status, and interrupt acknowledge behavior.
- Watch kernel logs and display diagnostics for blank displays, color corruption, audio dropouts, bad infoframes, stuck ABM updates, flicker, unexpected brightness changes, perfmon interrupt storms, and resume regressions.

## Cross-Chunk Notes

Adjacent chunks are required for complete file-level conclusions. The previous chunk owns the start of the `MPC_RMU0_SHAPER_RAMB_END_CNTL_B` register fields, and the next chunk continues `ABM2` ACE threshold fields and the remaining generated mask namespace. The merge lane should reconcile this report with neighboring chunks before making final claims about full `MPC_RMU0` or `ABM2` coverage.
