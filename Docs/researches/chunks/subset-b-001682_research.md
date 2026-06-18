# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 5204-7718

## Purpose

This chunk is generated AMDGPU DCN 3.0 register-offset metadata. It has no executable C logic; its API is a preprocessor namespace of MMIO register address offsets and per-register `*_BASE_IDX` constants for display pipe processor (DPP) blocks. The path sits under a local `ceph-client` source mirror, but the content is AMD display-driver hardware metadata rather than distributed filesystem code.

The range starts in the tail of the DPP1 color-management (`CM1`) block, at `CM_3DLUT` output and debug offsets. It then covers DPP2, DPP3, and DPP4 top/control, converter/cursor (`CNVC`), scaler (`DSCL`), color-management (`CM`), and DPP-local performance monitor blocks. The final section begins DPP5 and reaches into `CM5_CM_BLNDGAM_RAMA_*`; the remaining DPP5 blend-gamma offsets continue after this chunk.

All visible register offsets in this slice use `BASE_IDX` value `2`. The address-block comments identify instance base addresses for DPP2 at `0xb58`, DPP3 at `0x1104`, DPP4 at `0x16b0`, and DPP5 at `0x1c5c`; the associated DPP-local perfmon blocks use separate bases such as `0x3e3c`, `0x43e8`, `0x4994`, and `0x4f40`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this range. The important surface is the macro contract consumed by AMD display register-list code:

- `mmDPP_TOP{2,3,4,5}_*`: DPP clock/control, soft reset, CRC value/control, and host-read control registers.
- `mmCNVC_CFG{2,3,4,5}_*`: converter and formatter offsets for surface pixel format, format control, floating-point scale/bias, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha.
- `mmCNVC_CUR{2,3,4,5}_*`: cursor control and cursor color/scale-bias offsets for cursor 0 within each DPP instance.
- `mmDSCL{2,3,4,5}_*`: scaler coefficient RAM, scaler mode/tap control, DSCL control/autocal/update, overscan, OTG blanking, recout/MPC size, line-buffer format and memory control/status, DSCL memory power, output-buffer control, and OBUF memory power offsets.
- `mmCM{2,3,4}_*`: complete color-management register groups for DPP instances 2 through 4, including CM control, de-alpha, post-CSC, gamut remap, bias, gamma correction (`GAMCOR`), blend gamma (`BLNDGAM`), shaper LUT, CM memory power/status, 3D LUT, and debug-index/data offsets.
- `mmCM5_*`: the beginning of the DPP5 color-management group, from `CM5_CM_CONTROL` through partial `CM5_CM_BLNDGAM_RAMA_*` coverage.
- `mmCM1_*`: only the tail of the DPP1 CM block in this chunk, covering `CM_3DLUT_OUT_NORM_FACTOR`, output offsets, and CM test debug index/data.
- `mmDC_PERFMON13_*` through `mmDC_PERFMON16_*`: DPP-local display performance monitor offsets for counter control, counter state, perfmon control, counted-value interrupt/misc, and low/high counter value registers.

These offsets are paired with the matching generated field header `dcn_3_0_0_sh_mask.h`. Resource code expands them through macros such as `SRI(...)` and DPP register-list definitions, while runtime DPP code uses generic `REG(...)`, `REG_READ`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` helpers against instance-specific register tables.

## Control Flow

This header chunk is declarative data and contains no branches, loops, calls, callbacks, or allocation paths. Runtime control flow is created by the AMD display driver around these constants:

1. DCN 3.0 resource setup includes `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`, then builds per-instance DPP register tables with generated names such as `CNVC_CFG2_*`, `DSCL2_*`, and `CM2_*`.
2. Plane and pipe programming paths select a DPP instance and use the table to program pixel format, alpha behavior, pre-CSC, scaler parameters, recout size, line-buffer state, color transforms, gamma/3D LUTs, and cursor formatting.
3. Color-management paths in the DCN 3.0 DPP implementation read current LUT modes, choose RAM A or RAM B, write LUT index/data registers, update control registers, and manage CM memory power before and after programming.
4. Scaling paths program DSCL mode, taps, filter coefficients, scale ratios, initial phases, overscan, blanking, and memory power/status through the DSCL offsets.
5. Diagnostics and validation paths can read DPP CRC registers, host-read controls, perfmon counters, and CM debug index/data registers.

The offsets do not encode sequencing. Consumers must know when the DPP clock is enabled, when soft reset is allowed, when memory power has reached the expected state, and when double-buffered color or scaler changes latch.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It names MMIO-backed display hardware state.

The represented hardware state includes:

- DPP control state: clock enable/gating controls, block soft reset bits, CRC controls and CRC result registers, and host-read throttling.
- Converter and cursor state: surface pixel format, alpha-plane enablement, pre-dealpha/re-alpha, floating-point conversion scale/bias, color keying values, pre-CSC matrix registers, cursor mode/colors, and cursor scale/bias.
- Scaler state: coefficient RAM tap selection/data, horizontal and vertical scale ratios, initial phases, chroma/luma filter setup, manual replication, black color, overscan, recout and MPC dimensions, line-buffer format, line-buffer memory power/status, DSCL LUT memory power/status, and output-buffer behavior.
- Color pipeline state: CM bypass/control, dealpha and bias controls, post-CSC matrices, gamut remap matrices, `GAMCOR`, `BLNDGAM`, shaper, and 3D LUT index/data/control registers, LUT RAM A/B region descriptors, offsets, slopes, base values, and memory power/status registers.
- Performance and debug state: per-DPP perf counter control/state/value registers and CM debug index/data windows.

Persistence is hardware-defined. Configuration registers generally remain until a modeset, plane update, power-gating transition, suspend/resume, soft reset, or ASIC reset changes them. Registers named `*_STATUS`, `*_CURRENT`, `*_UPDATE_PENDING`, `*_CRC_VAL_*`, `*_PERFMON_*`, `*_TEST_DEBUG_*`, and memory-power fields may be read-only, sticky, snapshot, self-clearing, or side-effect-sensitive depending on the matching field definitions and hardware specification.

## Dependencies And Integration Points

The direct companion for this offset chunk is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h`

Observed include and consumer points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which includes the DCN 3.0 offset/mask headers and defines `SRI(reg_name, block, id)` for instance-specific register table construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c`, which programs and reads CM, CNVC, and DSCL registers through generic DPP register tables. This includes gamma, blend gamma, shaper, 3D LUT, memory power, pixel format, and scaler behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, which defines the DPP register and field table shapes that bind generated offset macros with generated shift/mask macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`, which include the same generated DCN 3.0 register contract for IRQ and DMUB-facing display hardware access.

Higher-level integration is through DC plane, color, cursor, scaling, and mode-setting code. DML bandwidth calculations model DPP/CNVC/DSCL timing, while DPP runtime code turns selected plane state into MMIO writes using these generated offsets.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong offset or wrong instance suffix can compile cleanly while programming the wrong DPP, causing blank planes, incorrect colors, bad scaling, cursor artifacts, missed CRC/perfmon reads, or hangs during power transitions.
- The repeated DPP2, DPP3, DPP4, and DPP5 blocks are copy-patterned. Instance drift is a major risk: one bad `CM3` or `DSCL4` offset may only appear with enough active displays or planes to use that instance.
- This chunk has artificial boundaries. It starts after most DPP1 CM offsets and ends before the complete DPP5 CM blend-gamma block, so whole-file analysis must merge adjacent chunks before claiming full instance coverage.
- LUT programming is stateful. `*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, RAM A/B selection, region descriptors, and current-mode bits require careful sequencing; racing updates or selecting the active RAM can show visible color corruption.
- Power and reset offsets are side-effect-sensitive. `DPP_SOFT_RESET`, `DPP_CONTROL`, `CM_MEM_PWR_CTRL*`, `DSCL_MEM_PWR_CTRL`, and `OBUF_MEM_PWR_CTRL` interact with clock gating and memory power states; writes while a block is disabled may be dropped or stall.
- DSCL programming is timing-sensitive. Incorrect scaler ratio, filter-init, recout, blanking, or line-buffer offsets can fail only for scaled, 4:2:0, high refresh, rotated, or multi-plane modes.
- Color pipeline registers are packed by function but not by safety. Mixing post-CSC, gamut remap, gamma correction, blend gamma, shaper, and 3D LUT offsets across instances can produce subtle color-management failures that are hard to distinguish from userspace color bugs.
- Debug, CRC, and perfmon registers may have read side effects or latch requirements. Generic polling or full-register writes to diagnostic registers should be checked against the field header and hardware programming guide.

## Test Signals

Useful validation is compile-time plus DCN 3.0 display behavior:

- Build AMDGPU/DC with DCN 3.0 enabled; missing or renamed macros should fail in `dcn30_resource.c`, `dcn30_dpp.*`, IRQ service code, or DMUB DCN 3.0 code.
- Diff the generated offsets against AMD's DCN 3.0 register database and adjacent DCN family headers to catch per-instance drift across `DPP_TOP`, `CNVC_CFG`, `CNVC_CUR`, `DSCL`, `CM`, and `DC_PERFMON` groups.
- Exercise multi-pipe hardware with enough active planes/displays to use DPP2, DPP3, DPP4, and DPP5. Validate modesets, hotplug, DPMS, suspend/resume, plane enable/disable, page flips, cursor movement, and cursor format changes.
- Test scaler-heavy modes: up/down scaling, 4:2:0 content, chroma scaling, overscan, recout sizing, line-buffer pressure, high refresh, and multiple active planes. Watch for underflow, flicker, cropping, or corruption.
- Test color-management paths: post-CSC, gamut remap, degamma/gamma, blend gamma, shaper LUT, 3D LUT, RAM A/B switching, bypass modes, and memory power transitions.
- Use CRC and perfmon/debug paths where available to confirm `DPP_TOP*_DPP_CRC_*`, `CM*_CM_TEST_DEBUG_*`, and `DC_PERFMON13` through `DC_PERFMON16` offsets map to the expected DPP instances.
- Monitor kernel logs for DC underflow, timeout, page fault, IRQ storm, power-gating, or pipe-specific errors that appear only on higher-numbered DPP instances.

## Cross-Chunk Notes

Previous chunks define the earlier DPP1 and likely DPP0/DPP1 top, CNVC, DSCL, and CM offsets. Later chunks continue the DPP5 color-management block after `CM5_CM_BLNDGAM_RAMA_END_CNTL2_B`. The merge lane should combine adjacent chunks before making complete claims about all DCN 3.0 DPP instances or the full DPP5 CM register set.
