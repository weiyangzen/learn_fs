# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 27329-29825

## Scope And Purpose

This chunk is a generated AMD DCE 12.0 register field mask/shift table for display instance 5. It contains no executable C logic. Its purpose is to publish compile-time bitfield metadata used by AMDGPU display code when composing or decoding MMIO register values for the sixth display pipe/controller path.

The source path is under a local `ceph-client` mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The chunk starts in the middle of `DCP5_GRPH_UPDATE`: lines 27329-27337 contain only the remaining `*_MASK` definitions for graphics surface/mode update state, update locks, and XDMA flip controls. The earlier `DCP5_GRPH_UPDATE` shifts and first masks are owned by the previous chunk. The chunk then covers full or near-full mask/shift families for:

- `DCP5_*`: display controller plane 5 graphics, color, cursor, LUT, CRC, XDMA, and surface-counter fields.
- `LB5_*`: line-buffer 5 data format, memory, vline/vblank interrupts, keyer, buffer-status, urgency, and MVP flip fields.
- `DCFE5_*`: display controller front-end 5 clock, reset, memory power, flush, and miscellaneous fields.
- `DC_PERFMON8_*`: performance counter/monitor 8 control, status, counted-value, high/low, and interrupt fields.
- `DMIF_PG5_*`: display memory interface page 5 pipe arbitration, watermark, urgency, stutter, low-power, and DVMM status fields.
- `SCL5_*`: scaler 5 coefficient RAM, mode/taps/filter ratios, viewport, update, sharpening, overscan, and mode-change detector fields.
- `BLND5_*`: blender 5 control, secondary-mode, update, underflow interrupt, v-update lock, and register-update status fields.
- `CRTC5_*`: timing-generator/CRTC 5 timing, sync, trigger, count, blanking, stereo, snapshot, interrupt, CRC, external timing sync, static-screen, 3D, GSL, range-timing, and DRR fields.
- `FMT5_*`: formatter 5 clamp, dynamic expansion, pixel encoding/subsampling, and the shift half of bit-depth/dither control.

The chunk ends inside `FMT5_FMT_BIT_DEPTH_CONTROL`: lines 29809-29825 define the shifts for truncation, spatial dither, randomization, temporal dither, temporal levels, reset, and FRC selectors, while the corresponding masks continue in the following chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register prefixes identify repeated display-pipe instance 5 blocks, while the companion address header provides `mm<REGISTER>` addresses and base-index macros.

The companion address file for this ASIC is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`. This mask header is included by DCE 12.0 display code such as `dce120_resource.c`, `dce120_timing_generator.c`, `irq_service_dce120.c`, `dce120_hwseq.c`, GPIO translation/factory code, and `amdgpu/gmc_v9_0.c`.

Important field groups in this chunk:

- `DCP5_GRPH_*` covers plane address-in-use fields, display flip queue control/status, page-flip interrupt status/control, compressed surface address and pitch, outstanding-request limits, prescale bias/scale fields, input/output CSC matrices, common transform matrices, denorm, output rounding/clamp, keying ranges, degamma/gamut/regamma controls, DCP spatial dither, cursor state, LUT programming, DCP CRC, DVMM PTE controls, GSL, stereo sync flip, rotation, XDMA underflow/flip timeout/delay/recovery, alpha control, and surface-counter output.
- `DCP5_CUR_*` exposes cursor enable/type/mode/2x-magnify/force-MC-on bits, cursor size/address/position/hot spot/color registers, cursor update pending/taken/lock/stereo fields, request filtering, and stereo-offset controls.
- `DCP5_DC_LUT_*` and `DCP5_REGAMMA_*` define color LUT and piecewise/regamma region metadata, including index, data, write-enable masks, autofill, control flags, black/white offsets, region counts, slopes, bases, and segment offsets.
- `LB5_*` defines line-buffer format and memory mode controls, vertical line interrupt windows/status, vblank status, sync reset selection, black/keyer colors, urgency controls/status, buffer status, no-outstanding-request status, and MVP AFR/in-band flip controls.
- `DCFE5_*` defines front-end clock enables/gates, soft reset and reset status bits, memory powerdown/shutdown/force controls and status for cursor/WDATA/REQ/pipe/channel/TLB memories, delayed memory powerdown delay, and flush trigger/status fields.
- `DC_PERFMON8_*` defines performance counter selection and enablement, counter clear/send/reset/start actions, counted-value type/unit/threshold, interrupt enable/status/clear/type, high/low counter data, and monitor state selectors.
- `DMIF_PG5_*` defines pipe arbitration slots, urgency latency/watermark controls, watermark-mask selection, urgent-level thresholds, stutter enable/deep-sleep/watermark fields, stutter-exit self-refresh settings, low-power/repeater controls, preprocessor check controls, and DVMM status flags.
- `SCL5_*` defines scaler coefficient RAM select and tap data, scaling mode, tap counts, bypass/manual-replicate/auto-mode controls, horizontal/vertical filter controls, scale ratios, phase inits, round offsets, update-mode/taken/pending bits, sharpening, ALU, coefficient RAM conflict status, viewport start/size, overscan, and mode-change detection/masking.
- `BLND5_*` defines blender enable/mode/alpha/select flags, stereo and feedthrough controls, source current, viewport enable, secondary-mode format/blanking/input alpha/lut/transfer fields, update and underflow interrupt bits, v-update lock timing, and update status flags.
- `CRTC5_*` is the largest group in this chunk. It includes horizontal/vertical totals, blank and sync ranges, V-total min/max/DRR controls, nominal and update interrupt status, trigger A/B source/polarity/frequency/delay fields, manual trigger bits, force-count-now and flow-control state, AV sync counters, CRTC enable/control/blank/interlace/field indication/status/count fields, stereo control/status, snapshot fields, start-line control, interrupt control, update locks, double buffering, VGA capture, test patterns, master update lock/mode, MVP in-band control, master enable, stop-off counters, overscan/blank/black colors, vertical interrupt windows/control, CRC windows/data, external timing sync/loss/signal interrupts, static-screen detection, 3D structure, GSL controls, range-timing interrupt status, and DRR/XDMA prefetch metadata.
- `FMT5_*` begins formatter 5 output-stage metadata: component clamps, dynamic expansion enable/mode, format control for stereo sync override, spatial dither frame counter, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, source select, 4:2:0 phase lock and clear, plus the shift definitions for bit-depth/truncation/dither/FRC control.

## Control Flow

This chunk has no runtime control flow. Every meaningful line is a preprocessor definition that the C compiler substitutes into register-helper expressions.

Runtime flow exists in consumers that pair these masks/shifts with addresses and base offsets. DCE 12.0 code includes this header alongside `dce_12_0_offset.h`, `soc15_hw_ip.h`, and `vega10_ip_offset.h`. Register helpers such as `generic_reg_update_soc15`, `generic_reg_set_soc15`, `dm_read_reg_soc15`, `get_reg_field_value`, and FD-style field descriptors build read-modify-write operations from this generated metadata.

A representative control path for CRTC fields is visible in `dce120_timing_generator.c`: the timing generator reads `mmCRTC0_CRTC_STATUS` with an instance offset and decodes `CRTC_V_BLANK`, updates `CRTC0_CRTC_MASTER_UPDATE_MODE`, updates `CRTC0_CRTC_MASTER_UPDATE_LOCK`, reads `CRTC0_CRTC_STATUS_FRAME_COUNT`, and uses field macros through helper wrappers. For controller 5, the same register layout is represented by the `CRTC5_*` macro family in this chunk and addressed through per-instance offsets built in resource code.

A representative interrupt integration path is visible in `irq_service_dce120.c`: IRQ table macros compose enable, ack, status registers, and field masks for HPD, page-flip, vupdate, and vblank sources. The `DCP5_GRPH_INTERRUPT_*`, `CRTC5_CRTC_INTERRUPT_CONTROL`, `CRTC5_CRTC_V_UPDATE_INT_STATUS`, and `CRTC5_CRTC_VERTICAL_INTERRUPT*_CONTROL` definitions in this chunk are the instance-5 bitfield vocabulary for those interrupt paths.

Because the header is declarative, it does not enforce sequencing. Consumers must order writes around update locks, double-buffered pending/taken bits, self-clearing clears, interrupt masks, power-gated blocks, PLL/timing enablement, and display blanking windows.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe state in hardware MMIO registers.

The hardware state represented here spans several display pipeline categories:

- Plane state: graphics surface in-use addresses, update pending/taken bits, flip queue state, compressed-surface metadata, cursor metadata, LUT/regamma state, CSC matrices, keying, dither, alpha, and XDMA recovery/underflow status.
- Memory/frontend state: line-buffer format/memory/urgency state, DCFE clock/reset/memory-power state, DMIF arbitration/watermark/stutter/DVMM state, and front-end flush state.
- Timing state: CRTC totals, blanks, syncs, counters, status positions, master/update locks, static-screen state, 3D/stereo state, range timing, GSL, external timing sync, vertical interrupts, vblank/vupdate status, CRC capture windows, and DRR state.
- Output formatting state: formatter clamp, dynamic expansion, pixel encoding/subsampling, source select, and dither/truncation mode fields.
- Diagnostic state: DCP/CRTC CRC data, DC performance counters, line-buffer and blender underflow/status bits, scaler coefficient conflict status, and XDMA/cache-underflow detection.

Persistence is register-specific and not encoded by this generated table. Some fields are durable control bits that remain programmed until another driver write, block reset, suspend/resume transition, power-gating transition, modeset, or GPU reset. Other fields are transient hardware status, sticky interrupt/status bits, write-one-to-clear bits, self-clearing update requests, or read-only counters. The naming hints at behavior (`*_CLEAR`, `*_STATUS`, `*_PENDING`, `*_TAKEN`, `*_UPDATE_LOCK`, `*_RESET`, `*_ACK`, `*_INT_STATUS`, `*_INT_ENABLE`, `*_INT_MSK`), but this header does not declare access type or side effects.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header convention and on DCE 12.0 hardware documentation. It is meaningful only when used with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h` for MMIO addresses and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_enum.h` for symbolic field values where applicable.
- SOC15 base-address metadata from `soc15_hw_ip.h` and `vega10_ip_offset.h`.
- AMD display register helpers such as `reg_helper.h`, `generic_reg_update_soc15`, `generic_reg_set_soc15`, `dm_read_reg_soc15`, `get_reg_field_value`, and generated FD macros.

The direct include surface found in this source tree includes:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`

The practical integration points are AMD display core resource construction, CRTC/timing generator programming, page flip and vblank/vupdate IRQ handling, graphics plane and cursor programming, scaler/line-buffer/blender programming, display-memory-front-end power and arbitration control, color pipeline programming, CRC/debug validation, and formatter output setup.

The instance-5 nature matters. DCE 12.0 resource code constructs offsets for six CRTC instances (`CRTC0` through `CRTC5`) and similar repeated display blocks. These macros must stay layout-compatible with the corresponding `DCP5`, `LB5`, `DCFE5`, `DMIF_PG5`, `SCL5`, `BLND5`, `CRTC5`, and `FMT5` address definitions in the offset header.

## Risks And Edge Cases

- Numeric masks and shifts are hardware ABI. A one-bit error can compile cleanly but cause incorrect MMIO updates, corrupt neighboring fields, leave interrupts uncleared, or program the wrong display behavior.
- The chunk is generated and highly repetitive. Human edits to a single `5` instance, line-buffer/scaler/blender prefix, or similarly named field are easy to miss in review. Prefer regenerating from the authoritative register database over hand-editing.
- The chunk boundaries split register families. Any per-file synthesis must merge this document with adjacent chunk research before treating `DCP5_GRPH_UPDATE` or `FMT5_FMT_BIT_DEPTH_CONTROL` as fully described.
- Update-lock and pending/taken fields are sequencing-sensitive. Misuse of `DCP5_GRPH_UPDATE`, `DCP5_CUR_UPDATE`, `SCL5_SCL_UPDATE`, `BLND5_BLND_UPDATE`, `CRTC5_CRTC_UPDATE_LOCK`, `CRTC5_CRTC_MASTER_UPDATE_LOCK`, or `CRTC5_CRTC_DOUBLE_BUFFER_CONTROL` can create torn updates, missed latches, or modeset races.
- Interrupt and status fields mix enable/mask/status/clear semantics. Page-flip, vblank, vupdate, vertical interrupt, CRTC static-screen, external timing sync, range timing, LB vline/vblank, and blender underflow fields must be used with the correct clear or mask polarity.
- Memory/power fields touch live display fetch paths. Incorrect DCFE memory power, DMIF arbitration/watermark/stutter, line-buffer memory, or DCP DFQ/XDMA settings can surface as underflow, black frames, page-flip stalls, display corruption, resume failures, or power-management regressions.
- Color pipeline fields are format-sensitive. CSC matrices, prescale, denorm, output rounding/clamp, key ranges, LUT/regamma, formatter pixel encoding/subsampling, and dither/truncation fields must match pixel format, color depth, gamut, and link encoding expectations.
- CRTC timing and DRR fields are mode-sensitive. Incorrect totals, min/max vertical totals, sync ranges, DRR control, external timing sync, GSL, stereo/3D, or master update mode can break vblank timing, variable refresh, genlock/swaplock, frame counting, or stereo output.
- Status fields are not self-describing. The macro table does not state whether a field is read-only, sticky, write-one-to-clear, write-zero-to-clear, reserved, or power-domain gated; callers need the hardware spec or existing driver sequence.

## Test Signals

Useful validation is mostly compile-time plus hardware/display behavior:

- Build AMDGPU/DC code for DCE 12.0 targets with warnings treated seriously; missing or renamed macros are caught at compile time by resource, timing-generator, IRQ, GPIO, and hwseq users.
- Compare generated masks/shifts against `dce_12_0_offset.h`, adjacent DCE 12.0 chunks, and older DCE/DCN generated headers for repeated register families to catch accidental instance or bit-position drift.
- Exercise modesets on all six display pipes, especially pipe/controller 5, and verify CRTC enable/disable, vblank counters, vupdate events, page flips, cursor movement, scaling, blending, color programming, and formatter output.
- Run vblank/page-flip interrupt tests and check that `DCP5_GRPH_INTERRUPT_*`, `CRTC5_CRTC_VERTICAL_INTERRUPT*`, and `CRTC5_CRTC_V_UPDATE_INT_STATUS` paths enable, fire, and clear without storms or lost events.
- Test high-risk modes: deep color, YCbCr/subsampled output, cursor and plane flips under load, scaling up/down, DRR/variable refresh, stereo/3D if supported, external timing sync/GSL paths, suspend/resume, display hotplug, and multi-display configurations using the last pipe.
- Use CRC/debug paths where available: DCP CRC, CRTC CRC windows, performance monitor counters, line-buffer/scaler/blender underflow or conflict status, XDMA/cache underflow status, and DMIF/DVMM status can provide direct evidence that the fields are mapped correctly.
- Watch for negative signals in kernel logs and display behavior: underflow reports, stuck vblank/page-flip waits, failed modeset commits, black screens, link retraining, cursor corruption, color shifts, flicker during flips, frame-counter anomalies, or power-management resume regressions.
