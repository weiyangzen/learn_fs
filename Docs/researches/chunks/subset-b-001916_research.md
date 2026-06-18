# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 46939-49518

## Purpose

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and masks used to pack, update, and read display-controller MMIO register fields. Consumers include it with `dcn_3_1_6_offset.h` so register-table macros can pair a physical register offset with field-level layout.

The assigned range starts at the tail of `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED37`, covers the remaining UNIPHY macro-reserved register masks for UNIPHY1 and complete reserved maps for UNIPHY2 through UNIPHY6, covers panel power/backlight sequencing fields for `PWRSEQ0` and `PWRSEQ1`, covers DSC compressor instance 0 and 1 fields including DSCC, DSCCIF, DSC_TOP, and local perfmon blocks, and ends inside `DSCC2_DSCC_PPS_CONFIG18`.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, includes, variables, allocation sites, or locks in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field within a 32-bit register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Repeated instance prefixes such as `PWRSEQ0_`, `PWRSEQ1_`, `DSCC0_`, `DSCC1_`, and `DSCC2_` expose per-instance copies of the same hardware layouts.

Major macro families in this slice:

- `DCIO_UNIPHY*_UNIPHY_MACRO_CNTL_RESERVED*`: full-width `UNIPHY_MACRO_CNTL_RESERVED` fields with shift `0` and mask `0xFFFFFFFFL` for UNIPHY lanes/blocks 1 through 6. These are opaque/reserved register fields rather than semantically named driver controls.
- `PWRSEQ0_*` and `PWRSEQ1_*`: GPIO power-sequence enable/control/mask/readback, panel power sequencing controls and state, programmable delays, reference dividers, backlight PWM duty/period controls, group-lock/update-pending fields, and spare bits.
- `DSCC0_*` and `DSCC1_*`: complete Display Stream Compression compressor-client layouts for config, status, interrupt/status, PPS configuration registers 0 through 22, memory power, squared/max error counters, rate-buffer fullness counters, rate-control-buffer fullness counters, and debug-bus rotation.
- `DSCCIF0_*` and `DSCCIF1_*`: DSC client interface fields for input underflow recovery/status/interrupts, input pixel format, bits per component, double-buffer update status, acknowledge fields, picture width, and picture height.
- `DSC_TOP0_*` and `DSC_TOP1_*`: top-level DSC clock gating/enables and debug controls.
- `DC_PERFMON19_*` and `DC_PERFMON20_*`: DSC-local performance monitor counter select, enable/clear, mode, state, current value, threshold, and overflow fields.
- `DSCC2_*`: beginning of DSC compressor instance 2, from config/status/interrupt fields through PPS fields for picture geometry, slice geometry, rate-control model parameters, RC thresholds, and range entries through QP range 6.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by AMD display code:

1. DCN316 resource and DMUB files include `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`.
2. Register-list macros such as `SR`, `SRI`, `SRIR`, and field-list macros such as `DSC_SF` paste register and field tokens into names from this file.
3. Resource constructors populate register-offset tables and field shift/mask tables for blocks such as panel control and DSC.
4. Operational code later calls helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and wait/poll wrappers. Those helpers use the shifts and masks in this chunk to preserve unrelated fields while programming panel power, backlight PWM, DSC PPS data, DSC status/interrupt handling, and perfmon counters.

The macros do not encode sequencing requirements. Panel control still has to order power rails, DIGON/BLON, delays, PWM updates, and register locks. DSC code still has to program PPS registers, interface format, memory power, clocks, and double-buffer updates in the order required by the hardware.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- UNIPHY reserved registers are opaque 32-bit hardware state. Because the fields are named reserved, driver code should avoid relying on undocumented bit meanings unless directed by hardware programming tables.
- `PWRSEQ*` registers represent panel power/backlight state: GPIO output enables, mask/data values, target and readback states, delay counters, PWM duty/period/ref-divider values, group lock state, and update-pending state.
- `DSCC*` registers represent DSC compressor state: slice layout, ICH behavior, rate-control buffer model size, sticky overflow/underflow status, interrupt enables, PPS payload fields, memory low-power/force/disable/state fields, debug selectors, and error/fullness counters.
- `DSCCIF*` registers represent DSC input-interface state and double-buffer update handshake state.
- `DSC_TOP*` registers represent DSC clock/debug gating.
- `DC_PERFMON19/20` registers represent programmable performance counter state and threshold/overflow state for the DSC-related perfmon blocks.

Persistence is hardware-defined. Configuration fields normally retain values until modeset reprogramming, power gating, suspend/resume, or ASIC reset. Status, interrupt, update-pending, acknowledgement, clear, and counter fields may be sticky, self-clearing, write-one-to-clear, read-only, or timing-sensitive. This generated mask file does not identify access type; consuming code and hardware documentation must supply those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.6 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which gives the companion `reg...` offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes this header and builds DCN316 register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which includes the same generated DCN316 headers for DMUB-side register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` and `dcn20_dsc.c`, whose `DSC_REG_LIST_DCN20` and `DSC_REG_LIST_SH_MASK_DCN20` macros consume `DSCC0_*`, `DSCCIF0_*`, and `DSC_TOP0_*` field names and apply them to DSC instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.h` and `dcn301_panel_cntl.c`, which consume panel/backlight masks for `PANEL_PWRSEQ*`, `BL_PWM*`, and register lock/update-pending fields.

The primary integration pattern is token-pasting, so macro spelling is part of the ABI between generated headers and driver tables. A renamed field, missing mask, or changed shift can break compilation or, worse, compile while corrupting hardware programming if a stale value still matches a token expected by shared helper code.

## Risks And Edge Cases

- Generated masks are untyped constants. A wrong shift or mask can compile cleanly and cause only runtime display failures on specific hardware paths.
- The UNIPHY reserved blocks are especially risky for manual edits because every register is exposed as a full-width opaque field. Accidental writes through these masks could alter undocumented PHY behavior.
- `PWRSEQ0` and `PWRSEQ1` are stateful and timing-sensitive. Bad masks can break embedded panel power-up/down, backlight PWM duty or period, GPIO output selection, register locking, or idle/suspend resume.
- DSC PPS fields must match the DSC encoder model and the DRM DSC configuration. Incorrect masks for bit depth, bits-per-pixel, slice size, RC thresholds, range QP/BPG offsets, or native 4:2:0/4:2:2 flags can produce link bandwidth failures or visible corruption while modesets otherwise appear successful.
- Interrupt/status masks for DSCC buffer overflow/underflow and rate-control-model overflow are sticky/error-path fields; bad clear or enable masks can hide DSC faults or create interrupt storms.
- Perfmon fields are diagnostic but still side-effect-sensitive. Wrong clear, enable, counter-selection, or threshold masks can invalidate performance/debug data.
- Chunk boundaries are artificial. The range begins after part of `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED37` and ends before the rest of `DSCC2`, so final file-level conclusions require adjacent chunks.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN316 support enabled; token-pasting consumers in `dcn316_resource.c`, DMUB DCN316 code, panel control, and DSC code should catch missing or renamed macros.
- Mechanically compare every `__SHIFT` macro in this line range with its matching `_MASK` macro and verify masks align with their shifts and expected field widths.
- Diff this chunk against AMD's authoritative DCN 3.1.6 register database and nearby generated headers such as `dcn_3_1_4_sh_mask.h`, `dcn_3_2_0_sh_mask.h`, or `dcn_3_5_0_sh_mask.h` where hardware compatibility is expected.
- Exercise embedded-panel power paths: boot display bring-up, backlight enable/disable, brightness changes, PWM fractional mode, panel off/on cycles, suspend/resume, and idle optimizations that depend on `PWRSEQ0`.
- Exercise DSC-capable modes on pipes using DSC instances 0, 1, and 2: high-bandwidth modes, slice-count changes, bits-per-component changes, native 4:2:0/4:2:2 cases, MST or high-rate DP where DSC is required, and repeated modesets.
- Monitor kernel logs and display diagnostics for backlight failures, panel stuck-off/stuck-on behavior, DSC underflow/overflow interrupts, rate-buffer fullness anomalies, visual corruption, link-training fallback, and resume regressions.

## Cross-Chunk Notes

Adjacent chunks are required for a complete file report. Earlier chunks contain the beginning of the UNIPHY1 reserved field block and other preceding DCN316 mask families. Later chunks continue `DSCC2_DSCC_PPS_CONFIG18` and the remaining DSC/perfmon/register-mask namespace. The merge lane should preserve that this chunk is only a middle slice of `dcn_3_1_6_sh_mask.h`.
