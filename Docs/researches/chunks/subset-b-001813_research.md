# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 27505-30069

## Purpose

This chunk is generated AMD Display Core Next 3.1.2 register field metadata. It contains C preprocessor constants for memory-mapped display hardware register fields: `REGISTER__FIELD__SHIFT` gives the bit offset and `REGISTER__FIELD_MASK` gives the packed 32-bit mask. It has no executable C control flow, no structs, no functions, no storage, and no direct side effects.

The selected range starts at the tail of the `ABM2` adaptive-backlight block, covers a complete `ABM3` block, then spans OPP display-output blocks for instances 0 through 3, DSCRM forwarding controls, OPP top/perfmon fields, ODM input controls for instances 0 through 3, and the first large part of OTG0 timing-generator fields. It stops on the marker for `OTG0_OTG_TRIG_MANUAL_CONTROL`; that register's field definitions continue in the next chunk. Adjacent chunks are therefore required for the complete file-level report.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display-controller hardware metadata, not distributed-filesystem code.

## Important APIs, Types, And Macro Families

The public API is the generated macro namespace. Consumers normally do not hand-code every symbol; they use token-pasting helpers such as `SF`, `SRI`, `OPP_SF`, and `ABM_SF` inside register-list and mask-list macros. The matching `dcn_3_1_2_offset.h` supplies MMIO addresses, while this file supplies the field layouts used by `REG_SET`, `REG_UPDATE`, `REG_GET`, and raw register-read paths.

Major macro families in this chunk:

- `ABM2_*` tail: line 27505 finishes `ABM2_DC_ABM1_HG_SAMPLE_RATE`, then defines low-side sample-rate controls, histogram bin shift/index words, histogram result registers 1 through 24, and the ABM backlight master lock.
- `ABM3_*`: PWM ambient/user/target/current/final/minimum duty-cycle registers, ABM enable and auto-update controls, sample-rate controls, group update lock, ABM enable/bypass, IPCSC coefficient selection, ACE offset/slope/threshold fields, histogram/luma statistics, min/max pixel thresholds and counts, high-gain and low-side sample rates, histogram bin shift/index registers, histogram results, and master lock.
- `DPG0` through `DPG3`: display pattern-generator control, ramp control, dimensions, RGB/YCbCr colors, offset segment, and status fields for four OPP pipes.
- `FMT0` through `FMT3`: output formatter clamp component limits, dynamic expansion, pixel encoding/subsampling, dithering/truncation, random seeds, clamp control, side-by-side stereo control, 4:2:0 memory control, and 4:2:2 controls.
- `OPPBUF0` through `OPPBUF3` and `OPP_PIPE0` through `OPP_PIPE3`: OPP buffer active width, pixel repetition, segmentation, overlap/padded pixels, 3D dummy data/VACT-space parameters, memory power control, and OPP pipe clock control.
- `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: CRC enable/mode/source/window/mask fields and CRC result registers for each OPP pipe.
- `DSCRM0` through `DSCRM2`: DSC forward configuration fields that connect DSC forwarding through the OPP side.
- `OPP_TOP_*` and `OPP_ABM_CONTROL`: top-level OPP clock control and ABM mux/connection control.
- `DC_PERFMON16_*`: display perfmon counter controls, event selection, state, current-value threshold/interrupt handling, and low/high readback words associated with the OPP address block.
- `ODM0` through `ODM3`: OPTC input global control, data-source/segment selection, data format and DSC mode, bytes-per-pixel, width and segment width, input clock control, memory selection, and spare register fields.
- `OTG0_*`: horizontal/vertical timing totals, blanking and sync, variable-vtotal controls, trigger controls, flow/stereo/interlace controls, status counters, snapshot and interrupt controls, update locks, vertical interrupt positions, CRC controls/results/windows, static-screen detection, 3D structure, genlock/swaplock controls, clock/reset status, global sync events, master update lock, GSL windows, vupdate keepout, and global control fields.

## Control Flow And Data Flow

This header has no runtime control flow. Runtime behavior is created by AMD Display Core code that binds these constants into per-block register tables and later performs MMIO reads/writes:

1. The DCN 3.1/3.1.2 display stack includes the matching offset and shift/mask headers.
2. Resource code builds static register tables. For example, `dcn31_resource.c` creates ABM register arrays with `ABM_DCN302_REG_LIST(id)`, OPP register arrays with `OPP_REG_LIST_DCN30(id)`, and OPTC register arrays with `OPTC_COMMON_REG_LIST_DCN3_1(id)`.
3. Mask/shift tables are initialized from field-list macros such as `ABM_MASK_SH_LIST_DCN30`, `OPP_MASK_SH_LIST_DCN20`, and `OPTC_COMMON_MASK_SH_LIST_DCN3_1`, which paste field names into the generated symbols in this file.
4. Hardware block constructors receive the tables. Examples include `dmub_abm_create()` for ABM/backlight and OPTC/OPP constructors for timing-generator and output-pixel-processor state.
5. Modeset, color, backlight, CRC, timing, ODM combine/split, diagnostics, and interrupt paths call `REG_UPDATE`, `REG_SET`, `REG_GET`, or `REG_READ`. Those helpers use the shift/mask values to alter or decode individual fields while preserving unrelated bits.

The chunk itself does not encode ordering. Callers must still sequence writes around clocks, resets, vblank/vupdate windows, double-buffer pending bits, update locks, genlock/swaplock state, power gating, and hardware interrupt clear/ack behavior.

## State And Persistence Behavior

The macros do not hold software state or persist data on disk. They describe state inside GPU display hardware registers. Configuration fields generally remain until overwritten, reset, power-gated, or restored by suspend/resume and modeset paths; status fields may be read-only, sticky, self-clearing, write-one-to-clear, or latch-on-read depending on the hardware register.

Important hardware state represented here includes:

- Adaptive brightness and backlight state: ABM PWM levels, user/ambient/target/current values, auto-calculated duty cycle, ACE curve segments, histogram/luma statistics, sample-rate frame counters, register locks, and master locks.
- Output formatting state: per-pipe clamp limits, pixel encoding, dynamic expansion, bit-depth truncation, spatial/temporal dithering, random seeds, stereo packing, and 420/422 handling.
- OPP buffer and pipe state: active output width, segmentation/overlap, pixel repetition, 3D dummy data and spacing, memory power controls, OPP pipe clock enable, and CRC capture state.
- Pattern and diagnostic state: DPG ramp/color/dimension generators, OPP pipe CRC windows/results, OTG CRC windows/results, perfmon counter selects/states/thresholds/readbacks, and snapshot status.
- ODM/OPTC input state: segment source selection, number of input segments, DSC data format and bytes-per-pixel, segment/slice widths, input clock enables, memory selection, underflow status, and double-buffer pending state.
- OTG timing-generator state: programmed timing totals and syncs, variable-vtotal controls, trigger sources/windows, flow-control delay, stereo/interlace mode/status, vertical interrupts, static-screen detection, global sync events, update locks, genlock/swaplock controls, vupdate keepout, and master/global update controls.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.2 register database and must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`. A mask/shift symbol is meaningful only when paired with the corresponding register offset and base-index constants.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`, which directly includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h` so DMUB service register helpers can expand `FD_MASK` and `FD_SHIFT` values for DCN31-family hardware.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which builds ABM, OPP, and OPTC register/mask/shift tables used by DCN31 resources. The chunk supplies many of the field names used by those table macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.h` and the DMUB ABM paths, which map ABM fields such as sample-rate, current/target/user level, IPCSC selection, ACE, histogram progress, and PWM update control into backlight/adaptive-brightness operations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h`, `dcn20_opp.h`, and corresponding OPP implementations, which use FMT, OPPBUF, OPP pipe, and CRC fields when programming bit-depth reduction, clamping/pixel encoding, dithering, buffer segmentation, 3D parameters, memory power, and CRC readback.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.h` and `dcn31_optc.c`, which consume ODM and OTG fields for timing programming, ODM segment routing, DSC formatting at the timing generator input, CRC, vertical interrupts, update locks, genlock/swaplock, and state readback.
- User-facing and validation paths in DRM/AMDGPU that depend indirectly on these fields for modesets, panel brightness/ABM controls, CRC debugfs output, vblank/vertical interrupts, underflow handling, and display diagnostics.

## Risks And Edge Cases

- Numeric drift is the primary risk. A wrong mask or shift can compile successfully while programming the wrong hardware bits, corrupting visible color, timing, brightness, CRC diagnostics, or pipe routing.
- The range is artificially bounded. It starts mid-`ABM2` and ends immediately before the fields for `OTG0_OTG_TRIG_MANUAL_CONTROL`; adjacent chunks are required for complete ABM2 and OTG0 coverage.
- Repeated instance blocks are copy-sensitive. `DPG/FMT/OPPBUF/OPP_PIPE/OPP_PIPE_CRC` and `ODM` instances 0 through 3 share layouts but distinct prefixes; an instance-prefix error can silently bind one pipe's software table to another pipe's field names.
- ABM fields mix configuration, readback, locks, and hardware-collected histogram/luma data. Treating readback/status fields like ordinary writable configuration, or ignoring lock/update-pending fields, can produce stale brightness state or bad adaptive-brightness behavior.
- Formatter and OPP buffer fields are user-visible. Mistakes in clamp, encoding, truncation, dithering, 420/422, segmentation, overlap, or 3D fields can show up as color shifts, banding, stereo errors, corruption, or blank output rather than a clean kernel failure.
- ODM and OTG fields are timing-critical. Incorrect data-source selection, segment count, DSC bytes-per-pixel/slice width, vtotal limits, sync positions, update locks, GSL, vupdate keepout, or clock/reset bits can cause underflow, missed vblank/update events, broken multi-pipe combine, VRR issues, or display blanking.
- Status and interrupt fields have hardware-defined side effects that this generated file does not express. Consumers must know which bits are read-only, sticky, write-one-to-clear, self-clearing, double-buffered, or safe only during vblank/vupdate.

## Test Signals

Useful validation signals are mostly integration and hardware behavior rather than unit tests for this header alone:

- Kernel build coverage for DCN 3.1/3.1.2 paths, especially token-pasted field-list macros that fail compilation if a referenced generated symbol is missing or renamed.
- Modeset and hotplug smoke tests across all four timing/OPP instances, including ODM combine/split configurations where segment routing and DSC formatting fields are exercised.
- DRM CRC/debugfs tests that enable OPP and OTG CRC capture and confirm stable, expected readbacks from the result fields.
- Backlight and ABM tests on eDP panels, including user brightness changes, ABM level changes, ambient/user/current/target level programming, pause/save/restore, and histogram readback through DMUB ABM commands.
- VRR/vblank/vertical-interrupt tests that exercise OTG vtotal, vertical interrupt positions, global sync status, update locks, and vupdate keepout behavior.
- Display diagnostics/perfmon tests that configure `DC_PERFMON16` counters, observe threshold/interrupt status, and read low/high counter values without disturbing normal display output.
