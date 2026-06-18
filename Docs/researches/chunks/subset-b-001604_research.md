# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 2678-5241

## Scope And Purpose

This chunk is a generated AMD DCN 2.0 register-offset map. It contains only preprocessor constants mapping symbolic display-register names to MMIO offsets plus companion `_BASE_IDX` constants. It has no functions, structs, enums, executable control flow, or local storage.

The covered range starts in the tail of the `HUBPREQ1` block and then covers most of the replicated HUBP/HUBPREQ/HUBPRET/cursor/XFC register groups for display pipes 2 through 5. It then enters the DPP register space, covering DPP0 top, converter/cursor, scaler, and color-manager blocks, DPP0 perfmon, and the beginning of the same DPP1 blocks through `mmCM1_CM_SHAPER_LUT_DATA`. The file continues after this chunk, so DPP1 and later DPP instances are incomplete here and must be reconciled with later chunk reports.

The purpose of these macros is to give DCN 2.0 Display Core code stable register addresses for plane fetch, VM/page-table display reads, cursor fetch, metadata fetch, flip timing, prefetch/watermark programming, line/read diagnostics, DPP format conversion, scaling, color management, LUT programming, CRC, and performance monitoring. This source tree is a Ceph-client mirror that includes Linux AMDGPU display code; this header is hardware register metadata rather than Ceph filesystem logic.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types. The exported interface is the macro namespace. Each `mm...` macro is a register offset and each `mm..._BASE_IDX` macro selects the DCN base segment used by register helper macros such as `SR`, `SRI`, `SRII`, `REG_READ`, `REG_WRITE`, and `REG_UPDATE`.

The HUBP/HUBPREQ/HUBPRET section includes `HUBP2` through `HUBP5`, `HUBPREQ2` through `HUBPREQ5`, `HUBPRET1` through `HUBPRET5`, `CURSOR0_1` through `CURSOR0_5`, `HUBPXFC1` through `HUBPXFC5`, and display perfmons `DC_PERFMON8` through `DC_PERFMON13`. These define per-pipe scanout surface configuration, tiling/address config, luma/chroma primary and secondary viewport registers, request-size config, HUBP control/clock/VMPG/debug registers, DCFCLK/DPPCLK measure-window controls, surface pitches, VMID selection, primary/secondary surface and meta-surface low/high address pairs, flip controls, queue/frame pacing, surface-in-use and earliest-in-use readbacks, DCN TTU/QoS and prefetch parameters, VM aperture and page-table controls, protection-fault/default-address registers, TLB control, blank/destination/timing parameters, nominal delivery parameters, per-line delivery, cursor settings, memory power control/status, HUBPRET read-line controls/status/interrupts, cursor surface and DMDATA controls, and XFC buffer/delay/underflow/slave timing/scaler/MPC controls.

The DPP0 portion defines `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CM0`, and `DC_PERFMON13`. `DPP_TOP0` covers DPP enable/control, soft reset, CRC values/control, and host-read throttling. `CNVC_CFG0` covers surface pixel format, format/alpha expansion control, floating-point bias and scale, color keyer registers, and the 2-bit alpha LUT. `CNVC_CUR0` covers DPP-side cursor enable/mode/colors/FP scale-bias. `DSCL0` covers scaler coefficient RAM selection/data, scaling mode and taps, 2-tap/manual replicate controls, horizontal/vertical scale ratios and initial phases for luma/chroma, black offset, update/autocal, overscan, OTG blanking, RECOUT/MPC sizes, line-buffer format/control/counters, DSCL memory power, OBUF control, and OBUF memory power. `CM0` covers color-manager control, input CSC matrices, gamut remap matrices, bias, degamma LUT and piecewise region RAM A/B programming, alpha LUTs, 3D LUT mode/index/data/read-write controls, output CSC, output gamma, blend gamma, HDR multiplier, memory power, dealpha, coefficient format, shaper controls/LUTs, test/debug, and readback-current state.

The DPP1 portion begins the replicated instance-1 versions of the same families: `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, and the start of `CM1`. It is complete through DPP1 top/CNVC/cursor/DSCL and partial for `CM1`, ending at shaper LUT index/data rather than the whole color-manager block.

## Control Flow And Data Flow

This header has no runtime control flow. Data flow is compile-time macro substitution: DCN 2.0 resource code includes `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`, expands register-list macros, and stores concrete MMIO addresses and field masks in per-block register structures.

The main integration pattern is generated-instance expansion. `display/dc/resource/dcn20/dcn20_resource.c` defines `SR` and `SRI` so a list macro such as `HUBP_REG_LIST_DCN20(id)` or `TF_REG_LIST_DCN20(id)` becomes `.FIELD = BASE(mmBLOCKid_FIELD_BASE_IDX) + mmBLOCKid_FIELD`. The constants in this chunk therefore feed instance-specific HUBP and DPP objects without the driver computing raw offsets by hand.

At runtime, higher-level DC code programs these addresses through block abstractions. HUBP code writes surface pitches, addresses, VM controls, cursor addresses, DMDATA controls, flip controls, TTU/prefetch timing, and read-line controls. DPP code writes format-conversion, scaler, color-key, CSC, degamma/gamma/blend-gamma/shaper/3D-LUT, CRC, and power-control registers. The header does not enforce sequencing; synchronization is done by callers using vblank/update locks, flip status, readback registers, waits, and Display Core state machines.

## State And Persistence Behavior

The file itself stores no mutable state and performs no I/O. The state represented by these offsets is persistent hardware state in the DCN display engine until modeset, page flip, cursor update, color-management update, power-gating transition, suspend/resume restore, GPU reset, or another register write changes it.

Important state classes in this chunk include scanout base addresses and meta-addresses for luma/chroma surfaces, per-pipe VMID and VM aperture/page-table settings, DCC/meta fetch settings, flip and queue state, surface-in-use readbacks, frame pacing, prefetch and TTU watermarks, delivery timing, cursor image and DMDATA addresses, HUBP/HUBPREQ/HUBPRET/CURSOR/DSCL/CM memory power state, scaler coefficients and geometry, DPP input format/alpha/color-key state, cursor palette/control state in CNVC, color matrices, degamma/blend-gamma/shaper/3D LUT RAM contents, HDR multiplier/dealpha state, DPP CRC state, and perfmon counters.

Several represented registers are synchronization-sensitive. Surface address low/high pairs, meta-address pairs, cursor address pairs, DMDATA address pairs, flip controls, surface-in-use readbacks, `DSCL_UPDATE`, LUT index/data/write-enable triplets, RAM A/B piecewise gamma regions, memory power control/status pairs, and HUBPRET read-line status require caller-side ordering. The constants do not prevent partially updated address pairs, stale LUT banks, or writes while a block is powered down.

## Dependencies And Integration Points

This chunk depends on the rest of `dcn_2_0_0_offset.h` for a complete include-guarded DCN 2.0 register map and on `dcn_2_0_0_sh_mask.h` for bitfield shifts and masks. It is consumed by DCN 2.0 display resource construction, especially `display/dc/resource/dcn20/dcn20_resource.c`, and by register-list declarations in `display/dc/hubp/dcn20/dcn20_hubp.h` and `display/dc/dpp/dcn20/dcn20_dpp.h`.

Integration surfaces include DRM/KMS plane programming, GPU memory scanout through HUBP, VM/page-table display reads, cursor and DMDATA programming, page-flip timing and interrupt handling, Display Mode Library-derived prefetch/watermark/TTU programming, HUBP read-line diagnostics, XFC underflow/status handling, DPP scaler programming, format conversion, color keying, color-management pipelines, HDR and blend-gamma programming, CRC diagnostics, per-block memory power management, and display performance monitoring.

AMDGPU memory-controller code also reads related HUBP/HUBPREQ viewport and pitch registers when estimating active display memory use. That makes the offsets part of both display programming and memory-management diagnostics for DCN-era ASICs.

## Risks And Edge Cases

The main risk is silent hardware misprogramming if any generated offset or base index is wrong. These are integer constants; a wrong value can still compile while programming the wrong pipe, wrong color block, or unrelated register.

This range contains heavily replicated but instance-specific address families. HUBP instance offsets, cursor instance names such as `CURSOR0_5`, perfmon numbering, and DPP/CM register spacing must match the hardware database exactly. Generic code that assumes a single stride across HUBP, HUBPREQ, HUBPRET, cursor, XFC, perfmon, DSCL, and CM blocks can be fragile.

Address-pair and LUT-indexed registers are especially sensitive. Surface, metadata, cursor, DMDATA, and XFC buffer addresses have low/high or LSB/MSB halves. Degamma, blend-gamma, shaper, and 3D LUT paths use index/data/write-enable registers and RAM A/B banked region programming. Programming only part of a pair or switching banks/indexes at the wrong time can cause corrupted scanout, wrong colors, GPUVM faults, cursor corruption, or hangs in display fetch.

Power and timing registers are high-impact. Incorrect HUBP/HUBPREQ/HUBPRET/CURSOR/DSCL/CM memory power control, TTU/QoS/prefetch values, vblank/flip/nominal delivery parameters, or read-line programming can cause display underflow, missed flips, unstable vblank timing, blank screens, bad suspend/resume restore, or diagnostic counters that appear valid but reflect the wrong block.

The chunk starts after the beginning of `HUBPREQ1` and ends before the end of the DPP1 color-manager register map. The final merged report should treat those two edge blocks as partial in this chunk rather than complete descriptions of pipe 1 or DPP1.

## Test Signals

There are no unit tests for this header chunk alone. The first validation signal is build coverage for DCN 2.0 AMDGPU/DC configurations that include both `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`, especially `dcn20_resource.c`, `dcn20_hubp.h`, `dcn20_dpp.h`, and code using `HUBP_REG_LIST_DCN20` and `TF_REG_LIST_DCN20`.

Generated-header integrity should be checked against the authoritative DCN 2.0 register database or a known-good upstream header. Comparisons should focus on instance replication for HUBP2-HUBP5, HUBPREQ2-HUBPREQ5, cursor blocks, XFC blocks, DPP0/DPP1, CM LUT region sequences, `_BASE_IDX` values, and all low/high address-pair registers.

Runtime test signals include successful modesets using multiple pipes, correct page flips and flip-completion timing, stable cursor movement and DMDATA updates, no display underflows, no GPUVM/protection-fault reports from display fetch, correct surface pitch/address/readback behavior, correct scaler output with luma/chroma scaling, correct color conversion/gamut/degamma/blend-gamma/shaper/HDR behavior, stable suspend/resume, and correct memory power transitions.

Diagnostic validation should exercise DPP CRC readback, performance counter readback for the covered perfmon instances, HUBPRET read-line status, surface-in-use and earliest-in-use readbacks, XFC underflow status, LUT programming and bank switching, and stress tests that flip between compressed/uncompressed or luma/chroma surfaces. These signals catch offset and instance-selection mistakes that normal compilation cannot detect.
