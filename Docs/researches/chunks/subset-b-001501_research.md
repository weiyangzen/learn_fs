# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_d.h lines 6047-7358

## Scope

This chunk is the final section of the DCE 10.0 register-address header. It contains no executable code, functions, structs, or enums; its exported surface is a dense set of preprocessor constants mapping DCE 10.0 display, audio, PHY, I2C, and XDMA register names to MMIO or indexed-register offsets. It closes the file's include guard at line 7358.

## Purpose

The constants in this chunk are the address layer used by AMDGPU DCE 10 display code and related VI/SMU/powerplay paths. The companion `dce_10_0_sh_mask.h` supplies field masks and shifts; this file supplies register selectors such as `mmAZALIA_F0_CODEC_ENDPOINT_INDEX`, `mmDC_I2C_CONTROL`, `mmBLND_CONTROL`, and repeated per-instance aliases. Call sites include `amdgpu/dce_v10_0.c`, `amdgpu/vi.c`, `amdgpu/gmc_v8_0.c`, `amdgpu/gfx_v8_0.c`, `pm/powerplay/*`, and DC resource/hwseq code under `display/dc/.../dce100`.

## Important Macro Families

- BPHYC PLL and VGA PPLL registers at lines 6049-6184 define generic names plus `BPHYC_PLL0/1/2_*` aliases. The pattern maps PLL instance 0 at `0x1700..0x1723`, PLL1 offset by `0x2a`, and PLL2 offset by `0x54`. Covered controls include ref/fb/post dividers, spread-spectrum amount/control, deep-sleep/id clock control, analog/vreg/unlock/debug/update registers, VGA25/VGA28/VGA41 PPLL dividers, and spare/debug/status registers.
- UNIPHY PHY registers at lines 6185-6376 define `mmUNIPHY_*` generic names and `BPHYC_UNIPHY0..6_*` instance aliases. Instances are spaced by `0x20` from `0x48c0` through `0x4980`. Covered controls include transmitter control, power, PLL feedback/control/spread-spectrum, data synchronization, BIST/test outputs, TMDP registers, TPG seed/control, and debug.
- DMIF display pipe gateway registers at lines 6377-6488 define `DPG_*` control, watermark, urgency, DPM, stutter, NB p-state, repeater, hardware debug, and indexed debug registers. Per-pipe aliases cover `DMIF_PG0..6` with bases `0x1b30`, `0x1d30`, `0x1f30`, `0x4130`, `0x4330`, `0x4530`, and `0x4730`.
- Azalia/HDA audio definitions span lines 6489-6950. They include root/function codec parameter verbs (`ixAZALIA_F2_*`), DCE-side Azalia controller MMIO registers (`mmAZALIA_*`), HDA global/CORB/RIRB/stream descriptor offsets, endpoint index/data windows, output and input converter/pin controls, audio descriptors, sink info, CRC controls, stream and endpoint indirect register windows, and per-channel CRC selectors.
- Blender registers at lines 6951-7030 define `BLND_CONTROL`, secondary controls, update, underflow interrupt, vertical update lock, update status, debug, and indexed debug registers for `BLND0..6`, following the same pipe base pattern as DMIF/CRTC-style display instances.
- Writeback/converter registers at lines 7031-7061 define `WB_*` and `CNV_*` controls for writeback enable/config, converter mode/window/source size/update, color-space conversion matrix, rounding/clamp, CRC test results, debug, input selection, soft reset, and indexed converter test debug. These are single-address definitions in the `0x5e18..0x5e36` range in this chunk.
- DCFE and DCFEV registers at lines 7062-7088 define front-end clock control, soft reset, and debug config for `DCFE0..5`, plus virtual front-end `DCFEV_*` clock/reset/DMIFV memory power controls.
- HPD, DCO, interrupt, and I2C registers at lines 7089-7196 define hot-plug-detect status/control/fast-train/filter registers for `HPD0..5`, display-controller scratch registers, display interrupt status continuations, DCO memory power/clock/reset/debug registers, DCE I2C/DDC transaction/data/status/speed/setup registers, VGA DDC, EDID detect, generic I2C controls, and pin debug/selection.
- XDMA registers at lines 7197-7356 define global XDMA control/status/power/debug registers, master controls and per-master-pipe aliases for pipes 0-5 spaced by `0x10`, and slave controls plus slave channel aliases for channels 0-5 spaced by `0x8`. They cover local and remote surface base addresses, high address halves, remote GPU address fields, cache base/cache controls, channel start/dim/height, perf counters, urgent controls, NACK status, and slave latency/flip/channel state.

## APIs, Types, and Integration Points

The API surface is entirely macro-based. Users pass `mm*` constants to register access helpers such as `RREG32`, `WREG32`, indirect indexed audio helpers, register-sequence programming tables, and DC `reg_helper` macros. For example, `amdgpu/dce_v10_0.c` uses `mmAZALIA_F0_CODEC_ENDPOINT_INDEX + block_offset` and `mmAZALIA_F0_CODEC_ENDPOINT_DATA + block_offset` under `adev->reg.audio_endpt.lock` to access endpoint indirect registers.

The `ix*` constants are not direct MMIO registers in the same style as `mm*`; they are indexed-selector values or HDA verb/register indices used through an index/data window or codec command path. The repeated generic-plus-instance aliases let call sites either compute an instance offset (`base + block_offset`) or use a fully expanded instance macro when tables need literal addresses.

## Control Flow

This chunk has no runtime control flow. Its effective control flow appears in consumers:

- direct MMIO access through `RREG32/WREG32` using an `mm*` address;
- indirect access sequences that write an index register, then read or write the corresponding data register;
- per-instance dispatch using arrays or offsets added to generic base registers;
- register initialization tables that pair these address constants with masks and values from the companion mask header.

## State and Persistence Behavior

The header itself stores no state. The named registers represent hardware state that persists in the GPU display/audio/XDMA blocks until overwritten, reset, power-gated, or lost across device reset/suspend. Several macro groups point at stateful hardware domains:

- PLL/UNIPHY settings affect link clocks, transmitter power, spread spectrum, and PHY debug/test modes.
- DMIF and BLND registers affect per-pipe memory fetch arbitration, stutter/urgency, blending updates, and underflow reporting.
- Azalia registers control HDA command rings, stream descriptors, endpoint/pin/converter state, CRC/debug, sink information, and audio hotplug/status behavior.
- I2C/DDC registers drive EDID and AUX-adjacent display-detection workflows.
- XDMA master/slave registers configure cross-device display memory movement, addresses, caches, and perf/latency counters.

## Dependencies

The correctness of this chunk depends on the DCE 10.0 ASIC register map. It is normally paired with:

- `dce_10_0_sh_mask.h` for bit fields;
- AMDGPU register helpers and locking discipline around indexed register windows;
- display instance offset tables for CRTC/DMIF/BLND/DCFE/HPD-like blocks;
- HDA/Azalia codec logic that understands the distinction between MMIO window addresses and `ix*` indexed codec selectors;
- power-management and reset code that preserves or reprograms volatile display/audio state across BACO, suspend/resume, and GPU reset.

## Risks and Edge Cases

- Address aliasing is intentional but risky: many generic names equal instance 0, and several HDA offsets share the same low offset for different subfields, such as CORB/RIRB control/status/size and immediate-command index/data aliases. Consumers must use the correct access width, field mask, and indexed path.
- Instance spacing is not uniform across all groups. UNIPHY uses `0x20`, HPD uses `0x8`, XDMA master pipes use `0x10`, XDMA slave channels use `0x8`, and display pipe families jump from low pipe bases to `0x41xx+` for later pipes. Hard-coded arithmetic outside existing offset tables can easily select the wrong block.
- `mm*` and `ix*` constants are semantically different even when values overlap. Treating an `ixAZALIA_*` selector as a direct MMIO address, or vice versa, would corrupt unrelated registers.
- Several register groups control clocks, resets, power, I2C transactions, DMA addresses, and hotplug/audio status. Incorrect values can cause display blanking, missed hotplug interrupts, bad EDID reads, audio stream failure, underflows, or DMA to the wrong address.
- This file is generated-style hardware data with no compile-time type safety. Duplicate numeric values, stale ASIC documentation, or copy/paste drift across DCE versions will compile cleanly but fail only on affected hardware paths.

## Test Signals

Useful validation is mostly integration and hardware-facing:

- Build coverage for all DCE 10 include users, especially `amdgpu/dce_v10_0.c`, DC DCE100 resource/hwseq code, VI init, and SMU/powerplay paths.
- Display bring-up on DCE 10 ASICs with multiple connected outputs, validating HPD interrupts, EDID reads over every DDC/I2C path, mode set, vblank/page flip, and suspend/resume.
- Audio-over-HDMI/DP tests that exercise Azalia endpoint index/data windows, stream descriptors, converter/pin controls, hotplug, channel allocation, HBR/lipsync, and CRC/debug paths.
- Multi-pipe stress tests for underflow, watermark, stutter, DPM, and blend update behavior across all pipe instances.
- PHY/link tests across UNIPHY/PLL instances and VGA PPLL compatibility paths, including link training, spread-spectrum programming, power-gating, and reset recovery.
- XDMA master/slave validation on configurations that use XDMA display paths, checking remote address programming, perf/latency counters, NACK reporting, and channel start/flip behavior.

## Chunk Boundary Notes

This report covers only lines 6047-7358. Earlier chunks define the rest of the DCE 10.0 register map and may include the companion families needed to understand CRTC, GRPH, SCL, DIG, DP, AUX, and other display blocks. The final per-file report should merge this chunk with earlier chunk reports and preserve that this tail section closes `DCE_10_0_D_H`.
