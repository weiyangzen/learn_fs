# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 12378-14892

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used when AMDGPU display code reads or updates MMIO registers with helper macros such as `REG_UPDATE`, `REG_SET`, `REG_GET`, `HUBP_SF`, and `TF_SF`.

The requested range contains 2,115 `#define` lines covering 374 register names. It starts in the tail of the `HUBPREQ3` request block, then covers the full `HUBPRET3` return/control block, `CURSOR0_3` cursor and DMDATA registers, `DC_PERFMON9`, and the beginning of the DPP0 pipe: `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CM0`, and the first `DC_PERFMON10` control/state fields. The boundaries are artificial: the first visible macro is paired with a `HUBPREQ3_REF_FREQ_TO_PIX_FREQ` comment from the previous line context, and the final line stops inside `DC_PERFMON10_PERFCOUNTER_STATE`.

Although the path sits under a local `ceph-client` source mirror, this file is AMDGPU display-controller hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: field bitmask for a 32-bit MMIO register value.
- Block comments such as `// addressBlock: dce_dc_dpp0_dispdec_cm_dispdec`: generated register-database grouping hints.

Major macro families in this slice:

- `HUBPREQ3_*`: tail fields for HUBP request-side timing and memory power state, including `REF_FREQ_TO_PIX_FREQ`, DRQ limits, DPTE/MPTE/META/PDE memory power force/disable/status, and VM/PTE/meta chunk timing for vblank and flip paths.
- `HUBPRET3_*`: return-side DET buffer base and component crossbar control, DET/DMROB/PIXCDC memory power control/status, read-line interval/window/status registers, and vblank/read-line interrupt mask/type/clear/status fields.
- `CURSOR0_3_*`: cursor enable, magnification, mode, TMZ, pitch, size, position, hot spot, stereo control, destination offset, cursor memory power, surface address high/low pieces, and display metadata (`DMDATA`) address/control/QoS/status/software-data fields.
- `DC_PERFMON9_*`: HUBP-local performance counter control, counter state selection, global perfmon enable/reset/state, interrupt/mask/clear controls, manual trigger, overflow/counter status, and high/low counter value registers.
- `DPP_TOP0_*`: DPP top-level control, soft reset, CRC values/control, and host-read control.
- `CNVC_CFG0_*` and `CNVC_CUR0_*`: converter pixel format, format control, floating-point bias/scale, color keying, alpha LUT/pre-dealpha/pre-realpha, pre-CSC matrix and coefficient format, pre-degamma, and cursor color/scale-bias fields for DPP-side cursor handling.
- `DSCL0_*`: scaler coefficient RAM access, scaler mode/taps/2-tap controls, manual replicate, horizontal/vertical/chroma scale ratio and init fields, black color, update/autocal, overscan, OTG blanking windows, recout/MPC sizing, line-buffer format/memory/v-counter, DSCL memory power/status, and output-buffer control/memory power.
- `CM0_*`: color-management control, post-CSC and gamut-remap matrices, bias/HDR multiplier/dealpha/coefficient format, gamut-correction and blend-gamma LUT controls plus RAM A/B region tables, shaper LUT and RAM A/B region tables, color-management memory power/status, 3D LUT mode/index/data/read-write/output normalization/output offset-scale, and CM test-debug index/data fields.
- `DC_PERFMON10_*`: start of DPP-local performance counter control, counter control 2, and partial counter state field definitions.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the DCN driver:

1. DCN 3.0.1 resource or DMUB code includes `dcn_3_0_1_offset.h` and this matching `dcn_3_0_1_sh_mask.h`.
2. Resource construction macros paste instance IDs into register names and pair offsets with field masks. In `dcn301_resource.c`, `hubp_regs(0..3)` uses `HUBP_REG_LIST_DCN30(id)`, while `hubp_shift` and `hubp_mask` are initialized with `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)`.
3. The same file constructs DPP instances from `dpp_regs[inst]`, `tf_shift`, and `tf_mask`; DPP field lists in shared `dcn10`/`dcn20`/`dcn3` headers reference many `CNVC_CFG0`, `DSCL0`, and `CM0` masks from this chunk.
4. Runtime code then calls typed block methods such as HUBP cursor/DMDATA updates, DPP scaler programming, color-transform setup, LUT programming, CRC/perfmon reads, and power-management routines. Those methods use the generated shift/mask constants through register helpers.

The macros do not express ordering. Consumers must still sequence clock and power enablement, memory-power requests, cursor surface programming, DMDATA update toggles, scaler coefficient loads, double-buffered update points, color-LUT programming, interrupt clear/ack, and performance-counter start/stop behavior.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes bit layouts for MMIO-backed display hardware state:

- HUBP request/return state: memory power force/disable/status for request-side page-table/meta memories, DET/DMROB/PIXCDC power state, request timing for vblank/flip, read-line windows, vblank/read-line interrupt state, and DET/crossbar configuration.
- Cursor and DMDATA state: cursor enable/mode/size/position/address, cursor memory power, trusted-memory-zone bit, cursor stereo controls, metadata address/control/QoS/status, and software-fed metadata data.
- DPP conversion/scaling/color state: input pixel format, dealpha/realpha, color keying, pre/post CSC matrices, gamut remap, scaler taps/ratios/init phases, line-buffer and output-buffer memory power, gamma/blend-gamma/shaper LUT RAM programming, 3D LUT control/data/output scaling, and debug selectors.
- Perfmon state: selected events, counted value type, run/interrupt/overflow controls, manual trigger, active/started flags, and low/high counter values.

Persistence is hardware-defined. Configuration fields generally remain until modeset, fast update, power gating, suspend/resume, or ASIC reset. Status, interrupt, clear, debug, power-state, and counter fields can be read-only, sticky, self-clearing, write-one-to-clear, or dependent on block clocks. This header only exposes bit positions; the consuming block code is responsible for preserving unrelated bits and respecting side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.1 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which supplies the matching `mm...` register offsets and base-index constants.
- Shared DCN block headers that consume the generated symbols, including `dc/hubp/dcn30/dcn30_hubp.h`, `dc/hubp/dcn20/dcn20_hubp.h`, and `dc/dpp/dcn10/dcn10_dpp.h`.
- DCN301 resource construction in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which includes this header and builds `hubp_shift`, `hubp_mask`, `tf_shift`, and `tf_mask` tables.
- DCN301 DMUB support in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes the same offset/mask pair for firmware-facing register definitions.

The primary integration pattern is token-pasting. Shared block macros use instance-zero field names such as `CM0_CM_GAMUT_REMAP_CONTROL` or `DSCL0_SCL_MODE` for masks, while register lists use per-instance offsets such as `HUBPREQ3` or `CURSOR0_3` for concrete pipes. For DPP masks, instance-zero field layouts are shared across DPP instances; for HUBP instance 3, this chunk provides the concrete generated names that correspond to the fourth HUBP pipe's request, return, cursor, and perfmon registers.

## Risks And Edge Cases

- Mask/shift drift is the central risk. These constants are untyped preprocessor values, so a wrong shift or mask can compile and then silently modify the wrong bits in a hardware register.
- Generated instance naming is easy to misuse. `HUBPREQ3`, `HUBPRET3`, and `CURSOR0_3` are pipe-instance-specific names, while many DPP field lists intentionally use `CM0`, `DSCL0`, and `CNVC_CFG0` as canonical layouts. Treating those naming schemes as interchangeable can break only one pipe or only nonzero DPP instances.
- The chunk starts and ends mid-context. Adjacent chunks are required for complete `HUBPREQ3_REF_FREQ_TO_PIX_FREQ` context and for the remainder of `DC_PERFMON10_PERFCOUNTER_STATE` and later DPP perfmon fields.
- Power-control fields are sequencing-sensitive. Forcing or disabling DPTE/MPTE/META/PDE, DET, line-buffer, output-buffer, gamma, shaper, or 3D LUT memories at the wrong time can cause display corruption, underflow, stuck status bits, or ignored writes.
- Cursor and DMDATA paths have update semantics. Incorrect `DMDATA_UPDATED`, software update, repeat, size, address-high, QoS, or done-status fields can break HDR/static metadata updates, cursor-only updates, or low-latency metadata delivery.
- Scaler and color fields are visually high impact. Incorrect tap counts, init phases, ratios, CSC coefficients, gamma region offsets, shaper regions, or 3D LUT controls can produce blank output, bad colors, banding, clipping, scaling artifacts, CRC mismatches, or failures limited to specific formats.
- Perfmon and debug fields can perturb diagnostics. Bad event selection, counter control, interrupt clear, or debug write-enable masks can hide performance regressions or create interrupt/status noise.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN301 support enabled; missing or renamed macros should fail in `dcn301_resource.c`, DPP/HUBP register-table construction, and DMUB DCN301 register setup.
- Mechanically verify that every field in lines 12378-14892 has one `__SHIFT` and one `_MASK` macro where the generated schema expects a pair, and that masks align with the declared shifts without overlapping unrelated fields.
- Diff this chunk against AMD's authoritative DCN 3.0.1 register database and nearby generated headers such as `dcn_3_0_0_sh_mask.h` or later DCN 3.x headers where the hardware layout is expected to match.
- Exercise four-pipe configurations so HUBP instance 3 is active: multi-display modesets, cursor movement, cursor-only plane updates, DMDATA/HDR metadata updates, flip/vblank timing, read-line interrupts, and suspend/resume.
- Validate DPP0 image-processing behavior with format conversion, color keying, dealpha/realpha, pre/post CSC, gamut remap, degamma/gamma/blend-gamma, shaper, 3D LUT, scaling up/down, chroma scaling, overscan, and CRC capture.
- Stress power-management transitions: idle display, memory power gating/ungating, cursor updates during idle optimization, fast updates, full modesets, hotplug, and resume from low-power states.
- Use perfmon/debug paths to confirm counters start/stop, overflow/interrupt status behaves correctly, and selected events produce plausible values.
- Watch kernel logs and display diagnostics for underflow, VM/DMDATA faults, stuck interrupts, cursor corruption, metadata loss, color errors, scaler artifacts, CRC mismatch, and resume-only failures.

## Cross-Chunk Notes

Previous chunks own the earlier portions of `HUBPREQ3` and the rest of the generated DCN 3.0.1 mask namespace before line 12378. Later chunks continue `DC_PERFMON10_PERFCOUNTER_STATE` and the remaining DPP/perfmon field definitions. The final per-file research document should merge adjacent chunks before making complete claims about all HUBP3 request fields, all DPP0 color/scaler fields, or all DCN301 perfmon registers.
