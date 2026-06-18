# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 51799-54370

## Purpose

This chunk is part of the generated AMD DCN 3.0.2 register shift/mask header. It contains C preprocessor constants only; there are no functions, structs, storage objects, branches, or executable algorithms in this source slice. Each exported constant maps a hardware register field to either a low bit position ending in `__SHIFT` or an already-positioned bit mask ending in `_MASK`.

The covered hardware area is the tail of MPC RMU color-management metadata, display performance-monitor instances, high-performance-output clock control, ambient/backlight-management instances, HD Audio/Azalia controller metadata, and legacy VGA indexed-register metadata:

- The chunk starts in the middle of the `MPC_RMU1` shaper RAM-B region table, then completes `MPC_RMU1` 3D LUT fields.
- It defines a full `MPC_RMU2` shaper and 3D LUT macro set, including shaper LUT control, per-channel offsets/scales, RAM-A and RAM-B region descriptors, 3D LUT mode/index/data/read-write controls, and output normalization/offset/scale fields.
- It defines `DC_PERFMON25` under the MPC performance-monitor block and `DC_PERFMON26` under the HPO performance-monitor block.
- It defines `HPO_TOP_CLOCK_CONTROL` for HDMI stream-clock gate disable.
- It defines repeated `ABM0`, `ABM1`, `ABM2`, `ABM3`, and `ABM4` backlight/ABM register fields for PWM levels, automatic backlight control, adaptive contrast enhancement, histogram/luma statistics, sample rates, update locks, and readback state.
- It defines HDA/Azalia controller command/response ring and immediate-command fields, plus endpoint immediate-command data/index fields.
- It ends in legacy VGA sequencer and CRT-controller indexed registers, through `CRT07` vertical high-bit fields.

The header is hardware ABI metadata for AMDGPU Display Core. Driver code combines these field constants with register-address macros from `dcn_3_0_2_offset.h`, stores them in generated register tables, and accesses hardware through helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and lower-level MMIO wrappers.

Although the path is under a `ceph-client` source mirror, this chunk is AMD GPU display/audio register metadata. It does not implement Ceph filesystem behavior, distributed storage logic, network protocol handling, or filesystem persistence.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: positioned bit mask for the same field.

Important macro families are:

- `MPC_RMU1_SHAPER_RAMB_REGION_28_29` through `MPC_RMU1_SHAPER_RAMB_REGION_32_33`: tail region descriptors for the second RAM bank of RMU instance 1 shaper LUTs. Each paired region register carries per-region LUT offsets and segment counts.
- `MPC_RMU1_3DLUT_*`: 3D LUT mode/current-mode, size, index, two-16-bit data writes, 30-bit data writes, RAM-bank selection, 30-bit enable, read selection, output normalization, and per-channel output offset/scale fields.
- `MPC_RMU2_SHAPER_*`: full shaper state for RMU instance 2. This includes shaper LUT mode/current mode, RGB offsets, RGB scale, LUT index/data/write-enable, RAM-A and RAM-B start/end controls, and paired exponent-region descriptors for regions 0 through 33.
- `MPC_RMU2_3DLUT_*`: 3D LUT control/data/normalization fields for RMU instance 2, matching the instance-1 shape.
- `DC_PERFMON25_*` and `DC_PERFMON26_*`: performance-counter control, secondary control, per-counter state, monitor state/repeat count, count-off interrupt control/status/ack, counter value interrupt status/ack, high/low current values, and selected high/low readback windows.
- `HPO_TOP_CLOCK_CONTROL__HPO_HDMISTREAMCLK_GATE_DIS`: HPO HDMI stream clock gating control bit.
- `ABM[0-4]_BL1_PWM_*`: backlight/PWM-facing fields for ambient light level, user-requested level, target/current ABM level, final/minimum duty cycle, ABM enable/use-ambient/auto-update controls, sample-rate counters, and group-2 double-buffer lock/update state.
- `ABM[0-4]_DC_ABM1_*`: ABM processing fields for enable/bypass, input color-space coefficient selection, ACE offset/slope and threshold parameters, missed-frame state, HGLS read progress, histogram controls, luma-statistic readbacks, histogram and luma sample rates, histogram bin shift flags/indexes, 24 histogram result registers, and the backlight master lock.
- `CORB_*`, `RIRB_*`, `IMMEDIATE_*`, `DMA_POSITION_*`, and `WALL_CLOCK_COUNTER_ALIAS`: HDA/Azalia controller fields for command output ring buffer pointers/control/status/size, response input ring buffer base addresses/pointers/control/status/size, immediate command/response paths, DMA position buffer base/enable, and wall-clock readback.
- `AZENDPOINT_*` and `AZENDPOINT_IMMEDIATE_COMMAND_INPUT_*`: endpoint immediate command data/index fields for output and input endpoints.
- `SEQ00` through `SEQ04`: legacy VGA sequencer reset, clocking, map mask, character-map select, and memory mode fields.
- `CRT00` through `CRT07`: legacy VGA CRT controller horizontal timing fields and vertical high-bit packing fields.

Several names contain repeated terms such as `MPC_RMU_3DLUT_WRITE_EN_MASK_MASK` or `PERFCOUNTER_OFF_MASK_MASK`. That is expected in generated register headers: the first `MASK` is part of the hardware field name and the final `_MASK` suffix denotes the generated mask constant.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is created by caller code that uses these constants to encode and decode MMIO register values.

A typical path is:

1. A DCN 3.0.2-specific resource or hardware block file includes `dcn_3_0_2_offset.h` and `dcn_3_0_2_sh_mask.h`.
2. Register-list and shift/mask table macros select register addresses from the offset header and field definitions from this shift/mask header.
3. Constructors for display objects, such as MPC, ABM, HPO/hwseq, or audio-adjacent blocks, bind those tables into per-IP-block structs.
4. Higher-level Display Core code computes color-management, backlight, link/audio, timing, or diagnostics state.
5. Hardware code writes or reads fields through `REG_*` helpers, which use the stored shift and mask values generated from this file.

Concrete integration patterns in the tree include:

- MPC color-management code and resource definitions use the same shaper RAM region and 3D LUT macro shape in newer DCN generations. The `MPC_RMU` and `MPCC_MCM` register lists are used to program shaper LUT region descriptors, select LUT banks, write 3D LUT entries, choose 30-bit mode, and read current LUT mode/status.
- `amdgpu_dm_color.c`, Display Core color state, and hardware sequencer code treat 3D LUTs as part of the color pipeline. This chunk supplies the bit-level register ABI used below those policy layers for the DCN 3.0.2 RMU instances.
- `dce_abm.c`, `dmub_abm_lcd.c`, `dce_abm.h`, and DCN resource headers use ABM register families such as `BL1_PWM_CURRENT_ABM_LEVEL`, `BL1_PWM_TARGET_ABM_LEVEL`, `BL1_PWM_USER_LEVEL`, and `DC_ABM1_HGLS_REG_READ_PROGRESS` to set backlight levels and clear missed-frame/readback status.
- Hardware-sequencer definitions reference `HPO_TOP_CLOCK_CONTROL` and its HPO HDMI stream clock-gate field to configure display output clock gating.
- The HDA/Azalia fields match standard GPU audio command paths: software programs CORB/RIRB ring buffers or immediate-command registers, then polls/handles busy, result-valid, response interrupt, overrun, and memory-error state.
- VGA `SEQ*` and `CRT*` fields exist for legacy VGA-compatible modes or low-level bring-up paths that still need indexed VGA register definitions, even though normal atomic KMS display programming mostly uses DCN-native blocks.

The hardware sequencing implied by these fields is important:

- Shaper and 3D LUT programming is generally banked or indexed. Callers must select the intended bank/read-write mode, write LUT data in the expected order, and switch the active LUT mode only after contents and normalization/scale fields are ready.
- ABM fields include update locks, pending bits, frame-start update controls, readback-in-progress bits, missed-frame flags, and clear bits. Callers need frame-boundary-aware sequencing to avoid stale or partially latched brightness/statistics state.
- Performance monitors require event selection, counter state programming, run/stop control, optional interrupt enable, and ordered status/ack handling before values are meaningful.
- HDA command rings require DMA base addresses, size programming, pointer resets, DMA enable, interrupt setup, and overrun/error clearing in the correct order.
- Legacy VGA CRT timing fields pack high bits across multiple registers, so callers must update related registers coherently if they are ever used for mode programming.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It defines compile-time constants.

The state represented by this chunk lives in GPU registers and in caller-maintained Display Core objects:

- RMU shaper LUT and 3D LUT RAM contents, current mode, active bank, output normalization, and output per-channel offset/scale are display hardware state. They affect color transformation until overwritten, reset, or power-gated.
- ABM/PWM registers hold current, target, user, ambient, final, and minimum backlight levels, plus automatic transition controls. Histogram, luma-statistic, ACE, and HGLS fields expose both programmed parameters and hardware-produced readbacks.
- Double-buffer lock and update-pending bits represent staged hardware state that may latch at frame start rather than immediately on CPU write.
- Performance-monitor counters and current values are volatile diagnostic state. Interrupt status and ack bits have write-sensitive side effects.
- HDA CORB/RIRB base addresses and DMA-position buffers point at system memory managed by the audio driver. Pointer reset, DMA enable, and status bits are device state, not persistent storage.
- VGA sequencer/CRT fields are legacy display register state.

None of this is filesystem-persistent. Across GPU reset, suspend/resume, display reinitialization, or power-gating transitions, caller code must reprogram the required registers from software state.

## Dependencies

This chunk depends conceptually on:

- `dcn_3_0_2_offset.h` for the matching register addresses and base-index values. The shift/mask constants are useful only when paired with the correct address definitions for the same ASIC generation.
- Display Core register-helper infrastructure that stores address, shift, and mask tables and implements field updates over MMIO.
- DCN resource definitions that know which physical instances exist and how instance-prefixed generated names map to abstract blocks such as MPC RMU, ABM, HPO, and audio controller paths.
- DRM/KMS color-management, backlight, audio, and mode-setting code that decides when these fields should be programmed.
- Hardware-generated enum headers for symbolic field values in some domains, for example 3D LUT size/depth/bank choices and HDA ring-size/status meanings.

The definitions are tightly coupled to DCN 3.0.2. Reusing them with a different offset header or another ASIC revision can silently program the wrong bits.

## Integration Points

The main integration points are:

- **MPC/RMU color pipeline:** shaper LUTs and 3D LUTs are used for post-blend or multi-plane color-management paths. DRM color state and DC color transforms eventually become RAM region descriptors, LUT entries, output normalization, offsets, scales, and active LUT-bank selections.
- **ABM/backlight:** Display Core and DMUB-assisted backlight paths program PWM levels, current/target/user brightness, sample rates, and HGLS/ACE/statistics controls. The repeated `ABM0` through `ABM4` blocks support multiple display/backlight instances.
- **Diagnostics/performance:** `DC_PERFMON25` and `DC_PERFMON26` expose counter selection, run control, current-value selection, interrupt, and readback fields for low-level display diagnostics or debug tooling.
- **HPO clocking:** `HPO_TOP_CLOCK_CONTROL` participates in high-performance-output clock gating, specifically the HDMI stream clock gate-disable bit in this generation slice.
- **Audio:** HDA/Azalia controller and endpoint fields integrate GPU display audio with command ring, response ring, immediate command, DMA position, and wall-clock mechanisms.
- **Legacy display compatibility:** VGA sequencer and CRT-controller fields provide low-level definitions for VGA-compatible indexed register access where needed.

## Risks And Edge Cases

- **Generated ABI drift:** The most important risk is mismatch between this shift/mask header and the corresponding offset header or hardware generation. Such mismatches compile cleanly but corrupt MMIO field programming.
- **Chunk boundary context:** The slice begins mid-register at `MPC_RMU1_SHAPER_RAMB_REGION_26_27` mask definitions and ends mid-VGA CRT block after `CRT07` partial fields. The final merged per-file research should combine adjacent chunks for complete block coverage.
- **Indexed RAM/LUT sequencing:** Shaper and 3D LUT writes rely on index, data, bank, and write-enable fields. Off-by-one indexes, wrong bank selection, or switching active mode before loading completes can produce visible color corruption.
- **Double-buffer and frame-boundary latching:** ABM and backlight fields include lock, pending, readback, and frame-start controls. Incorrect ordering can miss a frame, expose stale readbacks, or leave pending bits set.
- **Write-one/clear-style status:** Missed-frame clear, performance counter ack, HDA pointer reset, interrupt ack, and overrun/status fields are likely side-effect-sensitive. Read-modify-write helpers must preserve unrelated bits and use the hardware-required clear semantics.
- **Memory-address alignment:** HDA RIRB and DMA-position lower base registers mask low unimplemented bits. Callers must provide correctly aligned DMA memory and program upper/lower addresses consistently.
- **Clock gating:** Forcing or disabling HPO stream-clock gating at the wrong time can affect HDMI/HPO bring-up, power behavior, or link stability.
- **Legacy VGA packed bits:** `CRT07` carries high bits for multiple vertical timing fields. Any consumer must update it as a packed register, not as independent uncoordinated fields.

## Test Signals

Useful validation signals for changes touching consumers of these macros include:

- Successful AMDGPU/DC build coverage for DCN 3.0.2 paths, ensuring generated shift/mask names match resource table references.
- Display color-management tests that exercise shaper LUT and 3D LUT enable/disable, bank switching, LUT upload, 30-bit mode, and output normalization/scale programming.
- Visual or CRC-based display validation after programming LUTs, especially across atomic commits, modesets, suspend/resume, and power-gating transitions.
- Backlight tests that set user/current/target brightness, enable/disable ABM, verify smooth transitions, read HGLS status, and confirm missed-frame clear behavior.
- Hardware diagnostics or debugfs tests that program `DC_PERFMON25`/`DC_PERFMON26`, observe counters incrementing for selected events, and verify interrupt/status ack paths.
- HDMI/HPO bring-up and hotplug testing around `HPO_TOP_CLOCK_CONTROL`, watching for link training, audio, and clock-gating regressions.
- HDMI/DP audio playback and codec-command tests that exercise CORB/RIRB DMA, immediate command busy/result-valid polling, response interrupts, DMA position buffer updates, and overrun/error status.
- Legacy VGA or firmware-console handoff smoke tests if code paths still use the `SEQ*`/`CRT*` fields.

For this exact header chunk, the basic repository-level signal is that `Docs/researches/chunks/subset-b-001772_research.md` exists and is non-empty; no generated source or checklist state should be changed by this research item.
