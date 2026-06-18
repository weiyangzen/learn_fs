# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 17350-19866

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field shift/mask header. It contains no executable C logic; it publishes compile-time bit layout constants for DCN display pipeline registers. Each register field is represented as paired preprocessor macros: `REGISTER__FIELD__SHIFT` gives the field's low bit position, and `REGISTER__FIELD_MASK` gives the already-positioned bit mask used by AMD display register helpers.

The range covers the tail of DPP0 color-management fields, a DPP0 performance-monitor block, most of DPP1's DPP/CNVC/DSCL/CM field layout, and the beginning of DPP2 scaler fields:

- Tail of `CM0` shaper RAMB region programming, memory power controls/status, 3D LUT programming, output normalization/offset, and CM test-debug registers.
- `DC_PERFMON13` performance-counter and performance-monitor registers associated with the DPP0 display pipeline.
- `DPP_TOP1` top-level DPP1 control, soft reset, CRC value/control, and host-read controls.
- `CNVC_CFG1` and `CNVC_CUR1` input/cursor formatter fields for DPP1, including surface pixel format, format conversion, FP bias/scale, color keying, alpha LUT, and cursor color/control.
- `DSCL1` scaler fields for DPP1, including coefficient RAM programming, scaler mode, tap counts, ratios, initial phases, overscan/recout/MPC sizes, line-buffer controls, memory power controls/status, and output-buffer controls.
- `CM1` color-management fields for DPP1, including input CSC, gamut remap, bias, degamma, blend gamma, shaper LUT, HDR multiplier, memory power controls/status, de-alpha, coefficient format, 3D LUT, and test-debug registers.
- `DC_PERFMON14` performance-counter and performance-monitor registers associated with DPP1.
- Start of `DPP_TOP2`, `CNVC_CFG2`, `CNVC_CUR2`, and `DSCL2` fields for the DPP2 pipeline, ending at the first two shifts of `DSCL2_DSCL_MEM_PWR_CTRL`.

Although this repository path is nested under a `ceph-client` source tree, this chunk is AMD GPU display hardware metadata. It has no Ceph filesystem protocol behavior, no distributed filesystem state, and no storage persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or global objects in this chunk. The API surface is the generated macro namespace consumed by AMD display code.

Important macro families include:

- `CM0_CM_SHAPER_RAMB_REGION_*`, `CM0_CM_MEM_PWR_CTRL2`, `CM0_CM_MEM_PWR_STATUS2`, `CM0_CM_3DLUT_*`, and `CM0_CM_TEST_DEBUG_*`: finish DPP0 color-management shaper/3D-LUT/test-debug field metadata.
- `DC_PERFMON13_*` and `DC_PERFMON14_*`: performance counter control, counter state, monitor control, captured counter values, high/low readback, and interrupt/status/mask fields.
- `DPP_TOP1_*` and `DPP_TOP2_*`: DPP enable/control, soft reset, CRC value/control, and host-read control fields for pipeline instances 1 and 2.
- `CNVC_CFG1_*` and `CNVC_CFG2_*`: input formatter and converter fields, including `CNVC_SURFACE_PIXEL_FORMAT`, `CNVC_BYPASS`, alpha enable, expansion mode, floating-point conversion bias/scale, color key compare values, and alpha lookup table fields.
- `CNVC_CUR1_*` and `CNVC_CUR2_*`: cursor enable, expansion, pixel-invert, ROM enable, cursor mode, alpha modulation, update-pending, cursor color, and floating-point cursor scale/bias fields.
- `DSCL1_*` and `DSCL2_*`: scaler coefficient RAM select/data, scaler mode, tap control, 2-tap sharpness, manual replication, luma/chroma horizontal and vertical ratios, filter init values, black offset, update/autocal, overscan, output rectangle, MPC size, line-buffer data format/memory partitioning, vertical counters, and memory power controls.
- `CM1_*`: the largest section in the chunk. It describes DPP1 color-management programming for input CSC matrices, gamut remap matrices, bias registers, degamma LUT, blend-gamma LUT, shaper LUT, HDR multiplier coefficients, shared/shaper/3D-LUT memory power controls, coefficient format, de-alpha, and test-debug access.

The macro names are instance-specific (`CM1_`, `DSCL1_`, `CNVC_CFG1_`, etc.), but many runtime consumers store instance-neutral field names in register tables. For example, DPP setup code builds per-instance register addresses with `SRI(..., CM, id)` and uses field shifts/masks generated from instance 0 names through macros such as `TF_REG_LIST_SH_MASK_DCN20(__SHIFT)` and `TF_REG_LIST_SH_MASK_DCN20(_MASK)`. This works because the repeated DPP instances share the same bit layout even when their register addresses differ.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is introduced by consumers that combine these field constants with register addresses from `dcn_2_0_0_offset.h` and register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

A typical runtime path is:

1. DCN 2.0 resource setup creates per-pipeline register tables for DPP, IPP/CNVC, DSCL, and CM blocks.
2. The register table selects the correct instance address, such as `CM1_CM_3DLUT_MODE` or `DSCL1_SCL_MODE`, using generated offset macros.
3. Driver code uses an instance-neutral field name, such as `CM_3DLUT_MODE`, `SCL_H_SCALE_RATIO`, `CNVC_SURFACE_PIXEL_FORMAT`, or `LUT_MEM_PWR_FORCE`.
4. Register helper macros insert or extract the value using the generated `*_SHIFT` and `*_MASK` constants from this header.
5. Hardware applies the write according to the register's own timing, latch, self-clear, or power-gating semantics.

Control-sensitive operations represented by this chunk include scaler coefficient RAM updates, scaler mode transitions, line-buffer and output-buffer power control, DPP soft reset, CRC capture, host-read access, cursor format/color updates, CNVC bypass and pixel format changes, color-keying, gamma/shaper/3D-LUT programming, performance-counter start/stop/restart/interrupt handling, and color pipeline test-debug access. The macros do not enforce sequencing or valid ranges.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes bit positions for state held in display hardware registers.

The represented hardware state includes:

- Color-management programming: CSC and gamut-remap matrices, bias values, degamma/blend-gamma/shaper region descriptors, LUT indices/data/write masks, 3D-LUT mode/index/data/read-write control, 3D-LUT output normalization, and output scale/offset values.
- Pixel and cursor formatting: CNVC surface format, alpha handling, expansion/bypass, FP conversion scale/bias, color-key compare values, cursor enable/mode/color/scale/bias, and update-pending status.
- Scaler state: coefficient RAM address/data, tap counts, luma/chroma scale ratios and initial phases, 2-tap sharpness, manual replication, boundary/autocal mode, overscan, recout/MPC size, black offset, line-buffer format/partitioning, vertical counters, and update-pending status.
- Power and reset state: DPP soft reset bits, CM shared/shaper/3D-LUT memory power force/disable/status, DSCL LUT/line-buffer memory power force/disable/status, and output-buffer memory power controls.
- Diagnostics and telemetry: DPP CRC values/control, CM test-debug index/data, performance-counter event selection, active/run/interrupt bits, counter readbacks, and counter compare/status fields.

Persistence is hardware-defined. Some fields are latched programming values that survive until reprogrammed or reset, some are live status bits, some are sticky interrupt/status bits that require explicit acknowledgement or clearing, and some are self-clearing request/update bits. Values may be changed by modesets, plane updates, cursor updates, color-management updates, power management, hotplug recovery, suspend/resume, firmware/DMUB involvement, or ASIC reset. The generated header does not encode read-only, write-one-to-clear, self-clearing, or safe-update rules.

## Dependencies And Integration Points

The companion address definitions are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`; this chunk supplies field layout inside those addresses. Consumers include both headers together.

Direct include points for `dcn_2_0_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The most relevant integration point for this chunk is the DPP stack. `dcn20_resource.c` builds `tf_regs`, `tf_shift`, and `tf_mask` tables from `TF_REG_LIST_DCN20`, `TF_REG_LIST_SH_MASK_DCN20(__SHIFT)`, and `TF_REG_LIST_SH_MASK_DCN20(_MASK)`. Those tables are consumed by DPP code under `display/dc/dpp/dcn10` and `display/dc/dpp/dcn20` for color-management, CNVC, DSCL, memory-power, and scaler programming.

The IPP/CNVC integration uses register-list and field-list macros from `dcn10_ipp.h`, including `IPP_REG_LIST_DCN20` and `IPP_MASK_SH_LIST_DCN20`. DSCL fields are used by scaler code in `dcn10_dpp_dscl.c` for coefficient loading, scale ratio/init programming, tap setup, autocal, black offset, line-buffer handling, and memory-power waits. CM fields are used by `dcn10_dpp_cm.c`, `dcn10_dpp.c`, and `dcn20_dpp.c` for color matrices, gamma/shaper programming, 3D LUT status/configuration, and DPP power setup.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can compile cleanly while updating the wrong bits, failing to update the intended bits, or corrupting adjacent fields during read-modify-write operations.

High-risk fields in this chunk include:

- Scaler coefficient RAM select/data, tap counts, scale ratios, initial phases, and mode fields. Bad values can cause distorted scaling, chroma misalignment, underflow/overflow symptoms, or blank output.
- Memory power force/disable/status fields for CM, DSCL, line buffer, LUT, and output buffer memories. Incorrect constants can leave memories powered down while being accessed, prevent expected power savings, or break resume/modeset sequences that wait on status bits.
- CNVC pixel format, bypass, expansion, alpha, and FP scale/bias fields. Errors can produce wrong colors, alpha handling bugs, bad cursor format, or incorrect fixed/floating conversion.
- CM LUT, shaper, 3D-LUT, CSC, gamut-remap, bias, and coefficient-format fields. Errors can produce color regressions, bad HDR/SDR transforms, LUT upload failures, or incorrect readback/status.
- DPP soft reset, CRC, host-read, test-debug, and perfmon fields. Errors can break diagnostics, cause stuck reset states, corrupt debug access, or make performance counters report misleading data.

The generated instance pattern is another risk. DPP0, DPP1, and DPP2 register fields are largely repeated with different prefixes, while DPP runtime tables often use instance 0 field definitions as canonical masks/shifts for every instance. If a later instance ever diverged, that assumption would fail outside the C type system.

This chunk is also bounded in the middle of repeated generated blocks. It starts in the middle of `CM0_CM_SHAPER_RAMB_REGION_10_11` and ends after only the first two `DSCL2_DSCL_MEM_PWR_CTRL` shift definitions. Those are chunking artifacts for research generation, not evidence that the source register block is incomplete.

## Test Signals

Useful validation signals are mostly compile-time checks plus display hardware behavior:

- Kernel builds for DCN 2.0 display paths should compile all generated field names referenced by DPP, IPP, DSCL, CM, IRQ, GPIO, clock, DMUB, and GMC code.
- Generated-header validation should compare every `*_MASK` and `*__SHIFT` pair in this line range against AMD's register database and the matching offsets in `dcn_2_0_0_offset.h`.
- Modeset and plane-scaling tests should exercise DPP1 and DPP2 paths with no scaling, luma/chroma scaling, 4:4:4 and 4:2:0 formats, different tap counts, underscan/overscan, and cursor updates.
- Color-management tests should upload and switch degamma, blend-gamma, shaper, 3D-LUT, CSC, gamut-remap, HDR multiplier, and bias programming while checking expected CRCs or visual output.
- Power-management tests should cover blanking, idle, hotplug, suspend/resume, and repeated modesets while checking that CM/DSCL memory status fields reach expected states and do not time out.
- Perfmon and CRC/debug tests should verify that `DC_PERFMON13`, `DC_PERFMON14`, DPP CRC, and CM test-debug fields produce plausible counters/readbacks and do not target the wrong instance.
- Regression symptoms from bad constants include blank or flickering displays, wrong color conversion, cursor corruption, scaler artifacts, failed LUT programming, stuck power-gating waits, resume failures, bad CRCs, and misleading performance-counter values.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define the preceding DCN 2.0 display register field families and the start of the DPP0 color-management section. Later chunks complete `DSCL2_DSCL_MEM_PWR_CTRL`, continue through the rest of the DPP2 scaler/color-management blocks, and cover subsequent DCN 2.0 register families. The final per-file report should treat this source as one generated hardware register-layout contract rather than independent algorithmic code.
