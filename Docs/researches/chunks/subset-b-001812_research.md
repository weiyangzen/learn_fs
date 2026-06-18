# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 24979-27504

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and masks used to pack and unpack fields inside DCN display-controller MMIO registers.

The range covers the tail of the `MPCC_OGAM3` output-gamma/gamut-remap field map, the `MPC_OUT*` output color-space-conversion and denorm fields, the `MPC_RMU*` shaper and 3D LUT field map, full ABM0 and ABM1 backlight/ambient-backlight-management field maps, and the beginning of ABM2. The requested slice contains 2,106 `#define` lines. A prefix count over the first token shows 310 `MPCC*` definitions, 1,116 `MPC*` definitions, 252 `ABM0*` definitions, 252 `ABM1*` definitions, and 176 `ABM2*` definitions.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU display driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation sites, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the field bitmask in the raw 32-bit MMIO register value.

Major field groups visible in this slice:

- `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_16_17` through `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_32_33`: output-gamma RAM A region descriptors. Each pair of regions has `LUT_OFFSET` and `NUM_SEGMENTS` fields packed at shifts `0x0`, `0xc`, `0x10`, and `0x1c`, with `0x000001FF`, `0x00007000`, `0x01FF0000`, and `0x70000000` masks.
- `MPCC_OGAM3_MPCC_OGAM_RAMB_*`: output-gamma RAM B start, start-slope, start-base, end, offset, and region descriptors for B/G/R channels. Start and base values are 18-bit style fields, offsets use 19-bit masks, and region pairs follow the same two-regions-per-register packing as RAM A.
- `MPCC_OGAM3_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM3_MPC_GAMUT_REMAP_*`: gamut-remap format, mode/current-mode, and 3x4 coefficient fields for coefficient banks A and B.
- `MPC_OUT0_MUX` through `MPC_OUT3_MUX`: output mux flow/rate-control fields for four MPC outputs, including current mux status.
- `MPC_OUT0_DENORM_*` through `MPC_OUT3_DENORM_*`: output denormalization mode and clamp min/max fields for R/Cr, G/Y, and B/Cb channels.
- `MPC_OUT_CSC_COEF_FORMAT` plus `MPC_OUT0_CSC_*` through `MPC_OUT3_CSC_*`: output color-space-conversion mode/current-mode and 3x4 matrix coefficient fields for four output pipes and two coefficient banks.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`: RMU mux selection/current status plus memory power force/disable/low-power/state fields for RMU0 and RMU1 shaper and 3D LUT memories.
- `MPC_RMU0_SHAPER_*` and `MPC_RMU1_SHAPER_*`: shaper LUT mode/current mode, offsets, scales, LUT index/data/write mask/config status, and RAM A/RAM B piecewise-region metadata.
- `MPC_RMU0_3DLUT_*` and `MPC_RMU1_3DLUT_*`: 3D LUT mode/size/current mode, LUT index/data, 30-bit data path, read/write control, RAM select, config status, output normalization factor, and output offsets.
- `ABM0_*` and `ABM1_*`: backlight PWM levels, minimum/final duty cycle, ABM control, sample-rate and grouped-update lock fields, ABM enable/bypass, input CSC coefficient selection, ACE slope/offset/threshold fields, missed-frame and clear bits, high-gain/luma-stat read progress, histogram control, luma statistics, sample rates, histogram shift flags/indexes, histogram result registers, and master lock.
- `ABM2_*`: the same ABM field family starts for ABM instance 2, from PWM level/control fields through `ABM2_DC_ABM1_HG_SAMPLE_RATE` shifts. The chunk ends before that register's mask definitions.

## Control Flow

This header chunk has no runtime control flow. It is compile-time metadata that gets folded into driver register tables and helper calls:

1. DCN 3.1 resource, IRQ, and DMUB code include `dcn_3_1_2_sh_mask.h` with the matching `dcn_3_1_2_offset.h`.
2. Register-list macros in display blocks use token-pasting helpers such as `SF(reg, field, mask_sh)` or `FN(reg, field)` to reference names like `MPC_OUT0_CSC_MODE__MPC_OCSC_MODE__SHIFT` and `MPC_OUT0_CSC_MODE__MPC_OCSC_MODE_MASK`.
3. Initialization code stores these constants in generated `shift` and `mask` tables, usually as `uint8_t` shifts and `uint32_t` masks.
4. Runtime code uses register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and DMUB equivalents to manipulate the hardware fields.

The macros do not encode sequencing. The actual ordering is in the consumers: modeset, pipe construction, color management, output CSC/denorm programming, RMU shaper and 3D LUT programming, ABM/backlight programming, double-buffer updates, lock/unlock sequences, and power-gating transitions.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes MMIO-backed hardware state:

- MPCC output gamma and gamut remap state: piecewise-linear LUT region starts, slopes, bases, offsets, segment counts, coefficient format, mode/current-mode, and remap matrix coefficients.
- MPC output state: mux routing, flow/rate control, denormalization clamp mode and limits, output CSC mode/current-mode, and output CSC coefficient banks.
- RMU color state: shaper LUTs, shaper region tables, 3D LUT index/data/control, output normalization/offsets, mux routing, and memory power state.
- ABM state: PWM duty and level registers, ambient/user/current/target levels, automatic update controls, frame-sampled update rates, grouped register locks, ACE thresholds/slopes/offsets, read-progress/missed-frame status, luma statistics, histogram configuration/results, and master locks.

Persistence is hardware-defined. Configuration fields usually remain until rewritten, pipe-disabled, power-gated, suspended, or reset. Current-mode/status, update-pending, missed-frame, read-progress, histogram result, luma statistic, and clear fields may be read-only, sticky, double-buffered, self-clearing, write-one-to-clear, or frame-latched depending on the block. This generated mask header does not distinguish those behaviors; the consuming driver code and hardware programming guide provide the operational semantics.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.2 generated register offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`

Direct include sites for `dcn_3_1_2_sh_mask.h` in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

Important local integration patterns:

- `dcn31_resource.c` includes `yellow_carp_offset.h`, `dcn_3_1_2_offset.h`, and `dcn_3_1_2_sh_mask.h`, then uses macros such as `SR`, `SRI`, and field-list expansions to build DCN 3.1 hardware register tables.
- `dmub_dcn31.c` includes the same DCN 3.1.2 offset and mask headers and builds `dmub_srv_dcn31_regs` by expanding `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
- `dmub_reg.h` defines `FN(reg_name, field)` as a lookup of `(REGS)->shift.reg_name__field` and `(REGS)->mask.reg_name__field`, then passes those pairs to `dmub_reg_set`, `dmub_reg_update`, and `dmub_reg_get`.
- MPC field-list macros in `display/dc/mpc/dcn30/dcn30_mpc.h` reference many fields in this chunk, including `MPC_OUT0_CSC_MODE`, `MPC_RMU0_3DLUT_*`, `MPC_RMU0_SHAPER_*`, `MPC_RMU_MEM_PWR_CTRL`, and `MPCC_OGAM0_*` equivalents. The `MPCC_OGAM3` instance fields in this chunk are part of the same generated per-instance namespace used when register tables are expanded across MPCC instances.
- OPP/ABM code paths use ABM-style field definitions through OPP and panel/backlight control support, especially for PWM duty-cycle programming, ABM enable/bypass, luma/histogram status, and double-buffered lock/update behavior.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These constants are untyped preprocessor values, so a wrong mask or shift can compile cleanly while corrupting a different field in the same MMIO register.
- Copy-pattern errors are plausible. This chunk contains repeated instance families (`MPC_OUT0` to `MPC_OUT3`, `MPC_RMU0` and `MPC_RMU1`, `ABM0` to `ABM2`) and repeated region pairs (`0_1` through `32_33`). A one-instance typo may only affect a specific pipe, output, color block, or panel backlight path.
- The requested bounds are artificial. The first line starts inside `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_16_17`; earlier lines in the prior chunk define the comment marker and the RAMA regions before 16. The last line stops after `ABM2_DC_ABM1_HG_SAMPLE_RATE` shift definitions and before the corresponding masks.
- Some fields are double-buffered or frame-latched. Lock, update-pending, update-at-frame-start, readback DB, current-mode, missed-frame, and clear fields can cause subtle frame timing bugs if field metadata is correct but consumer sequencing is wrong.
- Color-management registers can fail visually rather than loudly. Incorrect OGAM/RMU/CSC/denorm fields can produce wrong color, clipped highlights, bad HDR/SDR transforms, or pipe-specific artifacts without obvious build-time failures.
- 3D LUT and shaper fields interact with RMU memory power state. Programming LUT data while memory is gated, in the wrong RAM selection, or with the wrong 30-bit/control bits can silently drop updates or produce stale color output.
- ABM/backlight fields are user-visible and panel-sensitive. Wrong duty-cycle, minimum-duty, auto-update, sample-rate, master-lock, or luma-stat fields can cause brightness jumps, flicker, stuck backlight levels, or failed ambient-backlight management.
- Status and clear bits can be side-effect sensitive. Misusing `*_MISSED_FRAME_CLEAR`, read-progress, update-pending, or lock bits can mask a real missed update or create polling loops that never complete.

## Test Signals

Useful validation signals combine generated-header consistency with hardware behavior:

- Build AMDGPU/DC with DCN 3.1 support enabled. Missing or renamed macros should fail in DCN31 resource, IRQ, DMUB, MPC, OPP, and ABM register-table construction.
- Mechanically verify that each complete register field in this chunk has both `__SHIFT` and `_MASK` definitions, while explicitly allowing the chunk-boundary exceptions at the first and last register groups.
- Compare this generated range against AMD's authoritative DCN 3.1.2 register database and adjacent DCN 3.x generated headers where compatible fields are expected to align.
- Exercise color-management paths: output CSC enable/bypass, matrix programming for outputs 0 through 3, denorm clamp modes, gamut remap coefficient programming, OGAM LUT updates, RMU shaper LUT programming, RMU 3D LUT programming, and memory power transitions.
- Test multiple-pipe and multi-monitor scenarios so `MPC_OUT*`, `MPCC_OGAM3`, and RMU instance fields are not only validated through output 0.
- Validate ABM and backlight behavior on supported panels: user brightness, ambient-light driven changes, minimum/final duty cycle, automatic ABM updates, sample-rate counters, frame-start update locking, suspend/resume, and rapid brightness changes.
- Poll and inspect luma/histogram status paths: read-progress bits, missed-frame flags and clears, luma min/max/filter stats, pixel counts, histogram bin results, and sample-rate reset behavior.
- Watch kernel logs and display diagnostics for register wait timeouts, update-pending bits that do not clear, color corruption, unexpected brightness changes, flicker, panel blanking, suspend/resume regressions, and DMUB register-access failures.

## Cross-Chunk Notes

Previous chunks are needed for the start of the `MPCC_OGAM3` OGAM block, including earlier RAM A regions and the beginning of `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_16_17`. Later chunks are needed for the rest of `ABM2_DC_ABM1_HG_SAMPLE_RATE` and the remaining ABM2 field map. The final per-file research document should merge this chunk with adjacent chunks before making complete claims about all DCN 3.1.2 field definitions, all MPCC OGAM instances, or the full ABM2 register namespace.
