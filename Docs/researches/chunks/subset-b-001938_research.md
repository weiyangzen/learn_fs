# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 22681-25260

## Purpose

This chunk is generated AMD DCN 3.2.0 register field metadata. It contains no executable C logic; it exports preprocessor constants that describe MMIO bit positions (`__SHIFT`) and bit masks (`_MASK`) for display-controller registers. Consumers pair these masks with the matching offsets from `dcn_3_2_0_offset.h` and AMD display register helpers to build per-ASIC register tables.

The requested range starts in the tail of the ABM2 histogram/gain control block, covers the complete visible ABM3 block, OPP display pipe groups 0 through 3, OPP formatter/buffer/CRC/DSC-remap blocks, OPP top controls, ODM input blocks 0 through 3, and most of the OTG0 timing-generator block. It ends inside the beginning of OTG1 horizontal timing fields. In this slice there are 2,114 generated `#define` entries and 402 generated register/comment headings.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct register reads/writes in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.
- Address-block comments such as `// addressBlock: dcn_dc_opp_fmt0_dispdec` and `// addressBlock: dcn_dc_optc_otg0_dispdec`: generated grouping metadata for the owning display block.

Major register families in this range:

- ABM2/ABM3 adaptive backlight management fields: luminance statistics, min/max luma, pixel counts, histogram sample rates, histogram bin shift/index/result registers, backlight master locks, PWM ambient/user/target/current/final/minimum duty registers, ABM enable/update controls, ACE offset/slope/threshold controls, histogram/global-lock status, and read-progress/missed-frame flags.
- DPG0 through DPG3 display pattern generator fields: pattern control, ramp parameters, dimensions, RGB/YUV color components, offset segment, and DPG status.
- FMT0 through FMT3 formatter fields: RGB clamp components, dynamic expansion, formatter control, bit-depth and dithering controls, random dither seeds, clamp behavior, side-by-side stereo, 4:2:0 memory mapping, and 4:2:2 controls.
- OPPBUF0 through OPPBUF3 and OPP_PIPE0 through OPP_PIPE3 fields: OPP buffer control, 3D parameters, control1 flags, and OPP pipe control.
- OPP_PIPE_CRC0 through OPP_PIPE_CRC3 fields: CRC enable/control, mask, and result registers.
- DSCRM0 through DSCRM3 fields: DSC forward-remap routing controls.
- OPP top fields: clock control and ABM routing/control.
- ODM0 through ODM3 input fields: global input control, data source select, data format, bytes per pixel, width, input clock, memory config, and spare register fields.
- OTG0 timing-generator fields: horizontal/vertical totals, blanking, sync A, timing divider controls, VTotal min/max/mid and dynamic-refresh-rate controls, vstartup/vupdate/vready interrupts, trigger A/B controls, force-count/flow-control controls, stereo/interlace state, pixel readback, status counters, snapshot registers, interrupt controls, update locks, double-buffer control, master enable, vertical interrupt positions/controls, CRC windows/results/masks, static-screen controls, 3D structure, global sync lock, master update/global controls, manual triggers, DRR timing status/ranges, M_CONST DTO, request control, DSC start position, and pipe update status.
- Beginning of OTG1: `OTG1_OTG_H_TOTAL`, `OTG1_OTG_H_BLANK_START_END`, `OTG1_OTG_H_SYNC_A`, `OTG1_OTG_H_SYNC_A_CNTL`, and the shift/mask fields for `OTG1_OTG_H_TIMING_CNTL`.

Representative field groups include one-bit enables/status/clear flags, multi-bit selectors, 10- to 17-bit timing/duty/luma values, full 32-bit histogram/CRC/readback values, and paired low/high coordinate fields packed into one register.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.2 code includes `dcn_3_2_0_offset.h` and this `dcn_3_2_0_sh_mask.h` file.
2. Register-list macros paste symbolic register names into offset and field names. Offsets come from the offset header; field masks and shifts come from this header.
3. Helper macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `SR(...)`, `SR_ARR(...)`, `DMUB_SF(...)`, IRQ register-entry helpers, and DC block register-list builders materialize per-ASIC register, mask, and shift tables.
4. Driver code later uses those tables with register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and polling/wait helpers to program ABM/PWM behavior, pattern generation, output formatter state, OPP CRC, DSC remap, ODM routing, and OTG timing/interrupt/update-lock behavior.

The macros do not encode hardware ordering rules. Consumers must still sequence timing disable/enable, blanking, update locks, double-buffered updates, vertical interrupt clears, CRC enable/disable, ABM readback/update locking, and ODM/OPP routing changes around modeset and atomic commit boundaries.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed GPU display state. The represented hardware state includes:

- ABM/PWM state for ambient/user/target/current backlight levels, automatic update step size, sample-rate counters, histogram/luma statistics, ACE curve controls, and ABM lock/readback status.
- DPG state for internally generated test patterns and ramp/color settings.
- Formatter state for clamp ranges, bit depth, dithering mode, random dither seeds, dynamic expansion, stereo, and chroma packing/mapping.
- OPP buffer/pipe/CRC state for buffering, pipe enable/control, CRC windowing, CRC result values, and CRC masks.
- DSC remap and OPP top state for forwarding compressed-stream segments and top-level OPP clock/ABM selection.
- ODM state for input source, input formatting, width, memory, and clock controls used when combining or splitting display pipes.
- OTG state for active timing, blank/sync periods, dynamic refresh rate, trigger windows, counter reset/force behavior, stereo/interlace reporting, snapshots, vblank/vline/vupdate/vstartup/vready interrupts, CRC signatures, static-screen detection, global sync lock, master update lock, and pipe-update status.

Persistence is hardware-defined. Configuration fields generally retain values until a modeset, pipe disable, power gating, suspend/resume, or ASIC reset. Status, interrupt, event, clear, pending, read-progress, missed-frame, CRC-result, snapshot, and lock-status bits may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header only supplies bit locations; it does not express access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies the matching MMIO offsets.
- DCN base-address definitions and register-list macros in DCN 3.2 resource, IRQ, GPIO, clock-manager, DMUB, and GMC code.
- Common AMD display register helpers that derive masks and shifts from generated names.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`

Important consumer areas:

- DCN resource construction uses the generated fields to initialize OPP, formatter, ODM, timing-generator, ABM, and related display block objects.
- IRQ service code maps OTG vertical/vupdate/vline and HUBP flip interrupt sources; the OTG interrupt masks and clear/status fields in this chunk are part of that hardware contract.
- DMUB register initialization exports generated offsets/masks/shifts to firmware-facing register tables, so firmware-visible DCN 3.2 register access relies on these constants being exact.
- Clock-manager, GPIO, and GMC code include the same generated register database for chip-specific register access even when only a subset of fields is used directly.
- Display modeset and atomic commit code indirectly relies on these fields when programming timing, formatter, ODM, ABM/backlight, CRC, and update-lock behavior through shared DC block abstractions.

## Risks And Edge Cases

- Field drift is the central risk. These macros are untyped constants, so an incorrect shift or mask can compile cleanly while reading or writing the wrong MMIO bits.
- The chunk boundary is artificial. It starts inside `ABM2_DC_ABM1_HG_MISC_CTRL` and stops inside `OTG1_OTG_H_TIMING_CNTL`; adjacent chunks are required for complete ABM2 and OTG1 coverage.
- Repeated instance families are copy-sensitive. DPG/FMT/OPPBUF/OPP_PIPE/OPP_PIPE_CRC/DSCRM/ODM instances 0 through 3 and OTG instances 0 and 1 are structurally similar but instance prefixes are not interchangeable.
- ABM/PWM mistakes can cause visible backlight jumps, failed adaptive-brightness updates, stale histogram/luma reads, missed-frame flags that never clear, or writes blocked by master/reg locks.
- Formatter and dithering field mistakes can cause color clipping, wrong bit depth, banding, stereo/chroma-format corruption, or format-specific artifacts.
- OPP CRC fields are often used for validation and diagnostics. Bad masks can produce false CRC failures or hide real corruption.
- ODM and DSC-remap fields affect pipe combining/splitting and compressed stream routing. Wrong masks can break high-resolution modes, multi-pipe configurations, or DSC forwarding.
- OTG timing and interrupt fields are high impact. Incorrect totals, blank/sync windows, DRR controls, vertical interrupt positions, event clears, or update locks can cause blank displays, flicker, missed vblank/vline events, stuck interrupts, frame pacing problems, or atomic commit stalls.
- Status/clear fields may be write-one-to-clear or self-clearing. Treating masks as ordinary read/write fields in consumers can clear events accidentally or leave sticky status bits set.

## Test Signals

Useful validation combines generated-header consistency checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.2 support enabled. Missing or renamed masks/shifts should fail in `dcn32_resource.c`, `irq_service_dcn32.c`, `dmub_dcn32.c`, GPIO, clock-manager, GMC, and shared display block users.
- Mechanically verify that each visible `__SHIFT` macro in lines 22681-25260 has the expected companion `_MASK` macro for the same register field where the generated schema defines one.
- Diff this slice against AMD's authoritative DCN 3.2.0 register database and nearby generated headers such as DCN 3.2.1 or DCN 3.1.x where hardware compatibility is expected.
- Exercise ABM/backlight paths: ambient/user level changes, automatic ABM level updates, histogram/luma readback, lock/unlock behavior, and suspend/resume with panel brightness preserved.
- Run modes that use all covered OPP/FMT/ODM instances: multiple displays, overlays, pipe split/combine, DSC, high resolution, high refresh, SDR/HDR format changes, chroma formats, and dithering-sensitive gradients.
- Validate OTG behavior through DRM vblank/vline/page-flip tests, dynamic refresh-rate modes, interlace/stereo paths if supported, rapid modesets, and atomic commits while monitoring for missed vblank, stuck vupdate, or update-lock hangs.
- Enable display CRC capture and compare CRC stability across known test patterns, color formats, dither settings, and window positions.
- Watch kernel logs and display debug counters for underflow, timing validation failures, stuck interrupts, ABM read missed-frame flags, blank/flicker reports, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the start of the ABM2 block before `ABM2_DC_ABM1_HG_MISC_CTRL`. Later chunks continue OTG1 after `OTG1_OTG_H_TIMING_CNTL` and cover the rest of the generated DCN 3.2.0 shift/mask namespace. The final per-file report should merge adjacent chunk reports before making complete statements about all ABM instances, all OPP/ODM/OTG instances, or the full `dcn_3_2_0_sh_mask.h` hardware map.
