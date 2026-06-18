# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 22072-24583

## Purpose

This chunk is generated AMD DCN 3.1.4 display-controller register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used to pack and unpack fields inside MMIO registers. Runtime DCN314 code combines these definitions with the companion `dcn_3_1_4_offset.h` register offsets through `REG_SET`, `REG_UPDATE`, `REG_GET`, and related AMD display register helpers.

The range covers the tail of DPP0 color-management definitions and then moves into DPP1 display-pipe definitions. It contains 2,113 `#define` lines: 1,055 `__SHIFT` macros and 1,058 `_MASK` macros. The apparent three-macro difference is because the requested range starts after some fields in an already-open register family and ends inside the `CM1_CM_BLNDGAM_RAMB_*` family. Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver ASIC metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, local variables, dynamic allocations, locks, or includes in this slice. Its interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Major register families visible in this chunk:

- `CM0_CM_BLNDGAM_*`: DPP0 blend-gamma control, LUT index/data/control, RAM A/B piecewise-linear region starts, slopes, bases, offsets, and 34-region segment descriptors.
- `CM0_CM_HDR_MULT_COEF`, `CM0_CM_DEALPHA`, `CM0_CM_COEF_FORMAT`, `CM0_CM_MEM_PWR_*`, `CM0_CM_SHAPER_*`, and `CM0_CM_3DLUT_*`: DPP0 HDR multiplier, dealpha, coefficient format, gamma/shaper/3DLUT memory power state, shaper LUT programming, 3D LUT data/index/control, output normalization/offset/scale, and test debug fields.
- `DC_PERFMON10_*`: DPP0 display performance monitor fields for event selection, counter modes, hardware start/stop selection, counter state selection, report count, interrupts/status/ack, high/low counter values, and clock/run enable.
- `DPP_TOP1_*`: DPP1 top-level clock gating, soft reset, DPP CRC readback/control, and host-read rate control.
- `CNVC_CFG1_*` and `CNVC_CUR1_*`: DPP1 input converter fields for surface pixel format, format expansion/conversion/bypass, FP bias/scale, color-key ranges, alpha LUTs, pre-dealpha/pre-realpha, pre-CSC matrix banks, pre-degamma, and cursor control/colors/FP scale-bias.
- `DSCL1_*`: DPP1 scaler coefficient RAM selection/data, scaler modes, tap control, 2-tap controls, scale ratios, filter init values, overscan, output sizes, line-buffer format/partitioning/counters, scaler memory power/status, and output-buffer controls.
- `CM1_CM_*`: DPP1 color-management fields for post-CSC, gamut remap, bias, gamcor LUT/PWL RAM A/B regions, blend gamma LUT/PWL RAM A regions, and the beginning of blend-gamma RAM B start fields.

The repeated `*_RAMA_REGION_N_M` and `*_RAMB_REGION_N_M` macros encode two LUT region descriptors per register: region N fields occupy low bits with LUT offset at shift `0x0` and segment count at `0xc`; region M fields occupy high bits with LUT offset at `0x10` and segment count at `0x1c`. These are used by color pipeline code to program double-buffered PWL curve RAMs.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the display driver:

1. DCN314 resource, IRQ, and DMUB code include `dcn_3_1_4_offset.h` and this mask header.
2. Register-list construction in the DC resource layer token-pastes names such as `CM1_CM_GAMCOR_CONTROL`, `DSCL1_SCL_MODE`, or `DPP_TOP1_DPP_CRC_CTRL` into per-block register and shift/mask tables.
3. DPP, scaler, color, cursor, CRC, perfmon, IRQ, and DMUB paths use the tables with AMD register helpers to read, update, or poll specific fields.
4. Hardware latches or reports field changes according to each register's semantics; this generated file only defines field geometry and does not encode when values may be safely written.

Important ordering constraints therefore live outside this chunk: clocks and memory must be powered before programming LUTs or scaler buffers; mode changes must respect update-pending/current-status fields; LUT RAM selection must be coordinated with RAM A/B double buffering; CRC and perfmon interrupt/status bits require driver-managed clear/ack sequencing.

## State And Persistence Behavior

The chunk stores no software state and writes no persistent files. It describes MMIO-backed GPU state:

- Color-management state: post-CSC and gamut-remap matrices, coefficient formats, bias, gamma-correction and blend-gamma LUTs, shaper LUTs, HDR/3DLUT controls, and RAM A/B PWL region geometry.
- DPP1 conversion/cursor state: surface pixel format, alpha-plane enable, format expansion/conversion, color keying, pre-CSC/pre-degamma, dealpha/re-alpha, cursor enable/mode/color, and update-pending indicators.
- DPP1 scaler state: coefficient RAM contents, taps, scale ratios, initial phases, overscan, RECOUT/MPC dimensions, line-buffer memory partitioning, and OBUF/LB memory power state.
- Diagnostic and performance state: DPP CRC values/control, DPP0 perfmon counter configuration, interrupt status/ack fields, and test debug selectors/data.

Persistence is hardware-defined. Most configuration fields retain values only while the relevant display block remains powered and not reset; status/current/update-pending/perfmon/counter/interrupt fields can be read-only, sticky, self-clearing, or write-one-to-clear depending on the underlying register. This header does not distinguish those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.4 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`, which defines the companion `mm...` register addresses.
- AMD display register helper macros that consume register, shift, and mask tables.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

The main integration surface for the visible fields is the DCN314 DPP and color pipeline. Resource construction maps these generated macros into the DPP, DSCL, CNVC, CM, CRC, perfmon, IRQ, and DMUB abstractions; later higher-level display code programs them during modeset, plane updates, color-management updates, cursor updates, CRC capture, diagnostics, suspend/resume, and low-power transitions.

## Risks And Edge Cases

- Bitfield drift is the central risk. These are untyped integer constants, so a wrong shift or mask can compile cleanly while causing writes to the wrong hardware bits.
- The chunk is boundary-partial. It starts after the beginning of `CM0_CM_GAMCOR_RAMB_REGION_24_25` and stops inside `CM1_CM_BLNDGAM_RAMB_START_SLOPE_CNTL_B`; adjacent chunks are required for complete per-file claims.
- Repeated CM RAM region macros are copy-sensitive. Region numbers, RAM A/B selection, and RGB channel suffixes must match the hardware table; a one-register typo can corrupt only specific curve segments or only one color channel.
- Double-buffered LUT and mode-current fields are sequencing-sensitive. Programming the inactive RAM, toggling select bits, and waiting for `*_CURRENT` or `*_UPDATE_PENDING` state must be done by consumers in the right order.
- Memory-power fields for gamma, shaper, HDR3DLUT, scaler LUT/LB groups, and OBUF can make other writes ineffective or unsafe if a block is gated, forced off, or still transitioning.
- Perfmon and CRC fields include status and ack bits. Incorrect masks can leave interrupts stuck, miss counter events, or produce misleading diagnostic data.
- DPP1 CNVC/DSCL fields affect pixel interpretation and scaling. Incorrect masks can produce wrong color channel routing, alpha behavior, cursor format, scaling phase, line-buffer sizing, underflow, or visible corruption on only some formats or plane sizes.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU/DC with DCN314 enabled; missing or renamed macros should fail in `dcn314_resource.c`, `irq_service_dcn314.c`, or `dmub_dcn314.c` register-table construction.
- Mechanically verify that every field in lines 22072-24583 has coherent shift/mask geometry and that masks match their documented bit widths after applying the shift.
- Diff this chunk against AMD's authoritative DCN 3.1.4 register database and nearby generated DCN headers where register layouts are expected to match.
- Exercise color-management paths: post-CSC, gamut remap, bias, gamma correction, blend gamma, shaper LUT, 3D LUT, HDR multiplier, RAM A/B switching, and suspend/resume restoration.
- Exercise DPP1 plane paths with RGB/YUV, alpha, cursor, color keying, pre-CSC/pre-degamma, scaling up/down, chroma scaling, overscan, and line-buffer partition changes.
- Validate diagnostics: DPP CRC enable/one-shot/continuous modes, perfmon event selection/counting/interrupt ack, and debug index/data access.
- Watch kernel logs and visual output for update-pending timeouts, underflow, CRC mismatch, bad cursor colors, color banding, incorrect alpha, scaling artifacts, perfmon interrupt storms, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DPP0 color-management section, including earlier `CM0_CM_GAMCOR_RAMB_*` definitions. Later chunks continue the DPP1 `CM1_CM_BLNDGAM_RAMB_*` region definitions and the rest of the DCN 3.1.4 generated shift/mask namespace. The final per-file research document should merge adjacent chunk reports before making whole-file claims about all DCN314 DPP instances or the complete `dcn_3_1_4_sh_mask.h` register-field map.
