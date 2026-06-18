# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 12327-14847

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register bitfield header segment. It contains preprocessor constants only: for each hardware register field, a `__SHIFT` macro gives the bit offset and a `_MASK` macro gives the bit mask. The chunk spans 2,521 source lines and contains 2,112 `#define` entries, including 1,054 shift definitions and 1,072 mask definitions. It starts in the tail of the `HUBPRET3` block and ends at the start of `CM0_CM_BLNDGAM_RAMA_REGION_6_7`, so both the opening and closing register families require adjacent chunks for full register coverage.

The covered surface is DCN display-pipe local MMIO state for HUBP/HUBPREQ/HUBPRET/cursor/perfmon instances 3 and 4, plus the beginning of DPP0 conversion, scaler, and color-management masks. There are no C functions, structs, or executable branches in this header chunk; its effective API is the generated macro namespace consumed by AMDGPU display resource construction and register helper tables.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN 3.0.2 display pipeline programming. Driver code includes this file with `dcn_3_0_2_offset.h` and uses the macros through register helper table builders such as `HUBP_MASK_SH_LIST_DCN30(__SHIFT)`, `HUBP_MASK_SH_LIST_DCN30(_MASK)`, `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)`, and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`. Those tables let runtime code perform field-safe `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and direct read/write operations without embedding literal bit positions.

For this chunk, the main hardware purposes are:

- tracking HUBP read-line interrupts and memory power for pipe 3;
- programming cursor and display metadata fetches for pipe 3 and pipe 4;
- programming HUBP4 surface layout, tiling, viewport, surface address, flip, DCC/TMZ, VMID, request-size, timing, QoS, prefetch, TTU, VM, and low-power controls;
- exposing DC performance counter controls for the HUBP side of pipe 3 and pipe 4;
- programming the first DPP instance's top control, pixel-format conversion, cursor conversion overlay, scaler, line buffer, post/pre color-space conversion, gamut remap, gamma correction LUTs, and the beginning of blend-gamma LUTs.

## Address Blocks And Register Surface

The chunk begins inside the `dce_dc_dcbubp3_dispdec_hubpret_dispdec` block, continuing `HUBPRET3` definitions for memory power, read-line windows, read-line interrupt mask/type/clear/status fields, current read-line value, snapshot, and read-line status.

Visible address blocks then include:

- `dce_dc_dcbubp3_dispdec_cursor0_dispdec`: `CURSOR0_3_*` cursor surface, size, position, hotspot, stereo, memory power, and `DMDATA` metadata registers.
- `dce_dc_dcbubp3_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON9_*` counter control, state, control/status, and counter-value masks.
- `dce_dc_dcbubp4_dispdec_hubp_dispdec`: `HUBP4_*` surface config, tiling, viewports, request-size, enable/blank/underflow control, clock, VM page config, and measurement windows.
- `dce_dc_dcbubp4_dispdec_hubpreq_dispdec`: `HUBPREQ4_*` surface pitch, VMID, primary/secondary and chroma surface/meta addresses, flip control, flip interrupt, current and earliest in-use addresses, expansion, QoS/TTU, VM controls, timing model parameters, prefetch, cursor timing, and memory power.
- `dce_dc_dcbubp4_dispdec_hubpret_dispdec`: `HUBPRET4_*` crossbar/packing/det-buffer control, memory power, read-line windows, interrupt/status, and read-line value.
- `dce_dc_dcbubp4_dispdec_cursor0_dispdec`: `CURSOR0_4_*` cursor and `DMDATA` metadata registers mirroring the pipe-3 cursor block.
- `dce_dc_dcbubp4_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON10_*` counter register masks.
- `dce_dc_dpp0_dispdec_dpp_top_dispdec`: `DPP_TOP0_*` DPP clock/control, soft reset, CRC values, CRC control, and host read control.
- `dce_dc_dpp0_dispdec_cnvc_cfg_dispdec`: `CNVC_CFG0_*` pixel format, format control, FP bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha.
- `dce_dc_dpp0_dispdec_cnvc_cur_dispdec`: `CNVC_CUR0_*` DPP-side cursor control, colors, and FP scale/bias.
- `dce_dc_dpp0_dispdec_dscl_dispdec`: `DSCL0_*` scaler coefficient RAM, mode, taps, control, two-tap control, manual replicate, ratios, init values, black color, update, autocal, overscan, OTG blanking, recout, MPC size, line-buffer, memory power, output buffer, and line-buffer counters.
- `dce_dc_dpp0_dispdec_cm_dispdec`: `CM0_*` color-management control, post-CSC, gamut remap, bias, gamma-correction LUT, gamma RAM A/B region programming, and the beginning of blend-gamma RAM A programming.

## Important Macro Families

`HUBPRET3_*` and `HUBPRET4_*` describe the post-request HUBP return path. The important fields are memory power force/disable/low-power-state controls for DET, DMROB, and PIXCDC memory; read-line programming for two line windows; interrupt mask/type/clear/status bits for vblank/read-line events; read-line current/snapshot values; and crossbar/pack controls in `HUBPRET4_HUBPRET_CONTROL`.

`CURSOR0_3_*` and `CURSOR0_4_*` expose cursor fetch and placement state. They include enable, 2x magnify, mode, TMZ, snoop/system, pitch, rotation/mirror bypass, lines per chunk, perfmon latency controls, 48-bit surface address fields, width/height, x/y position, hotspot, stereo offsets, destination x offset, cursor memory power, and DMDATA address/control/QoS/status/software-data fields.

`HUBP4_*` defines front-end HUBP surface interpretation for pipe 4: pixel format, rotation, horizontal mirror, alpha plane enable, address config (`NUM_PIPES`, `PIPE_INTERLEAVE`, compressed fragments, packers), tiling (`SW_MODE`, `META_LINEAR`, `PIPE_ALIGNED`), primary/secondary and chroma viewports, request-size grouping, blank/underflow/disable/VTG selection, clock enable/force-on, VM page config, and DCFCLK/DPPCLK measurement windows.

`HUBPREQ4_*` defines the request-generation and flip side of pipe 4. It covers pitch/meta pitch, VMID, primary/secondary surface and meta-surface base addresses for luma and chroma, TMZ/DCC surface-control bits, flip type/mode/pending/lock/triple-buffer/GSL controls, flip interrupt status/clear/mask, in-use and earliest-in-use address snapshots, request expansion modes, TTU QoS watermarks, per-surface and cursor delivery timing, metadata VM control/status/clear bits, system aperture and L1 TLB controls, blank offsets, destination timing, prefetch ratios, vblank/flip/nominal timing parameters, per-line delivery, cursor timing, and HUBPREQ memory power.

`DC_PERFMON9_*` and `DC_PERFMON10_*` expose the local display performance counters attached to HUBP instances. They include per-counter enable, clear, mode, state, counter selection, enable window, counter-off trigger, stopped/started flags, count-enable/status, high/low value, overflow, and event generation controls.

`DPP_TOP0_*`, `CNVC_CFG0_*`, and `CNVC_CUR0_*` are DPP instance 0 front-end controls. They cover DPP clock enable and disable gating, soft reset, CRC readback, host-read path, surface pixel format, conversion bypass/expansion/output FP and alpha enable, floating-point conversion bias/scale, color keying, alpha LUT, pre-dealpha/realpha, pre-CSC matrices for normal and B components, pre-degamma mode/select, and DPP-side cursor color/format.

`DSCL0_*` defines the scaler and line buffer. Important fields include coefficient RAM pair/phase/filter type and even/odd coefficient writes, scaler mode/current mode, chroma coefficient mode, taps, boundary mode, two-tap hardcode/sharpen controls, manual replicate controls, fixed-point horizontal/vertical luma/chroma ratios and initial phases, black color, update/autocal controls, overscan, OTG blank windows, recout and MPC dimensions, line-buffer format/memory configuration, LUT and OBUF memory power, and line-buffer v-counter readback.

`CM0_*` in this chunk covers DPP0 color management. It exposes CM enable and post-CSC enable/mode/current fields, post-CSC and gamut-remap matrices, per-component bias, gamma correction control and LUT index/data/control fields, gamma RAM A/B start/end/base/slope/offset/region definitions, and blend-gamma control plus the beginning of blend-gamma RAM A definitions.

## Control Flow And Runtime Behavior

There is no direct control flow in this file segment. Runtime behavior is indirect through AMDGPU display code that maps these constants into typed register tables.

The relevant integration path for this ASIC is `display/dc/resource/dcn302/dcn302_resource.c`, which includes `dcn/dcn_3_0_2_offset.h` and `dcn/dcn_3_0_2_sh_mask.h`. In `dcn302_hubp_create()`, the resource code builds `hubp_regs[]`, `hubp_shift`, and `hubp_mask`, then calls `hubp3_construct()`. In `dcn302_dpp_create()`, it builds `dpp_regs[]`, `tf_shift`, and `tf_mask`, then calls `dpp3_construct()`. The current chunk supplies the instance-4 register field values for the HUBP tables and the instance-0 DPP field values for the DPP tables.

Hardware flows represented by the bitfields include:

- Surface programming: HUBP/HUBPREQ macros define surface format, tiling, pitch, viewport, surface addresses, meta addresses, DCC enablement, TMZ bits, VMID, and aperture/TLB state before a plane can fetch pixels.
- Flip sequencing: `HUBPREQ4_DCSURF_FLIP_CONTROL*`, surface in-use snapshots, flip interrupt fields, and flip/vblank timing parameters support immediate, vblank, stereosync, triple-buffer, and GSL-related flip behavior.
- Cursor and metadata fetch: `CURSOR0_3_*`, `CURSOR0_4_*`, `HUBPREQ4_CURSOR_SETTINGS`, and `DMDATA` fields define cursor memory fetches, cursor placement, display metadata address/control, DMDATA repeat/update/mode, QoS, VM timing, and status/underflow signals.
- Bandwidth and timing model programming: `HUBPREQ4_DCN_*`, `VBLANK_PARAMETERS_*`, `FLIP_PARAMETERS_*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, `PREFETCH_SETTINGS*`, and TTU controls carry the computed display-mode timing values from the display mode library and watermarks into hardware.
- Scaler programming: DPP scaler code chooses a DSCL mode, programs line-buffer format and partitioning, writes coefficient RAM through `SCL_COEF_RAM_TAP_SELECT`/`SCL_COEF_RAM_TAP_DATA`, swaps coefficient RAM using `SCL_COEF_RAM_SELECT`, sets ratios/init phases, and programs taps/two-tap sharpening through `DSCL0_*` fields.
- Color pipeline programming: DPP code reads and writes `DPP_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `FORMAT_CONTROL`, pre/post CSC, gamut-remap, pre-degamma, gamma-correction RAM, and blend-gamma registers while applying per-plane color transforms and gamma LUTs.
- Power and low-power control: HUBPREQ/HUBPRET/CURSOR/DSCL memory power fields, clock control fields, and DPP clock/reset fields participate in display pipe power gating, memory low-power entry, and resume/reprogram paths.

## State And Persistence

The macros do not store mutable software state. They describe persistent hardware state in memory-mapped registers. Values written through fields in this chunk persist until rewritten, reset by the display block, or reinitialized during suspend/resume, modeset, power-gating, or GPU reset.

Several field classes represent latched or handshake state:

- Flip and address state: `SURFACE_FLIP_PENDING`, `SURFACE_FLIP_IN_STEREOSYNC`, in-use address readbacks, earliest-in-use address readbacks, and `HUBPREQ_MASTER_UPDATE_LOCK_STATUS` expose asynchronous surface update state.
- Interrupt and clear state: `PIPE_VBLANK_INT_*`, `PIPE_READ_LINE*_INT_*`, `SURFACE_FLIP_INT_*`, and DMDATA underflow clear fields require hardware-specific acknowledgement semantics. The mask constants alone do not encode whether a field is write-one-to-clear, level, edge, or read-only.
- VM and DMDATA status: `DMDATA_VM_FAULT_STATUS`, `DMDATA_VM_UNDERFLOW_STATUS`, `DMDATA_VM_LATE_STATUS`, status-clear fields, `DMDATA_VM_DONE`, `DMDATA_DONE`, and `DMDATA_UNDERFLOW` reflect metadata fetch status and error state.
- Memory power state: `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, `*_MEM_PWR_LS_MODE`, and `*_MEM_PWR_STATE` fields expose low-power controls/status for HUBPREQ, HUBPRET, cursor, DSCL LUT/line buffer/output-buffer, and color-management RAMs.
- Double-buffered LUT state: gamma and blend-gamma control fields include active/current selector fields and LUT index/data/control state; software typically alternates RAMs or updates host-selected LUTs before selecting the active bank.
- Performance counter state: `DC_PERFMON*_PERFCOUNTER_STATE`, `PERFMON_*_STARTED`, `STOPPED`, `OVERFLOW`, and high/low counter registers are readback state controlled by counter enable/clear fields.

## Dependencies And Integration Points

This header depends on the matching generated DCN 3.0.2 offset header for register addresses and on display-core register helper macros that combine register addresses, masks, and shifts. The same generated naming convention is used across `dcn302_resource.c`, HUBP headers, DPP headers, IRQ sources, and lower-level `reg_helper.h` accessors.

Concrete integration points visible in the source tree:

- `display/dc/resource/dcn302/dcn302_resource.c` includes this file and constructs DCN 3.0.2 resource objects for HUBP and DPP instances. Its `hubp_shift`/`hubp_mask` and `tf_shift`/`tf_mask` structures are populated from the macros in this header.
- `display/dc/hubp/dcn30/dcn30_hubp.h` defines `HUBP_MASK_SH_LIST_DCN30`, which references many fields present here, including `HUBPREQ0_*`, `HUBP0_*`, `HUBPRET0_*`, and `CURSOR0_0_*`. The generated per-instance names (`HUBPREQ4_*`, `HUBP4_*`, `HUBPRET4_*`, `CURSOR0_4_*`) are selected through the corresponding register-list address table.
- `display/dc/hubp/dcn10/dcn10_hubp.c` contains runtime behavior for HUBP request/read-line and debug DB handling, using the same field names abstracted by the table.
- `display/dc/dpp/dcn30/dcn30_dpp.h` defines DPP register and shift/mask lists for DCN 3.0. The DPP0 macros in this chunk satisfy the fields used by DCN 3.0.2 `dpp3_construct()`.
- `display/dc/dpp/dcn10/dcn10_dpp.c` consumes conversion and color-management fields such as `DPP_CONTROL`, `CM_GAMUT_REMAP_CONTROL`, `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `CURSOR_CONTROL`, and `CURSOR0_CONTROL`.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c` consumes scaler fields such as `DSCL_MEM_PWR_CTRL`, `DSCL_MEM_PWR_STATUS`, `LB_DATA_FORMAT`, `LB_MEMORY_CTRL`, `SCL_COEF_RAM_TAP_SELECT`, `SCL_COEF_RAM_TAP_DATA`, `DSCL_2TAP_CONTROL`, `SCL_MODE`, `SCL_TAP_CONTROL`, ratios, init values, recout, and MPC size.
- `display/dc/irq/dcn302/irq_service_dcn302.c` uses HUBPREQ interrupt register mappings for flip interrupt sources. This chunk's `HUBPREQ4_DCSURF_SURFACE_FLIP_INTERRUPT` masks provide the pipe-4 field definitions for that interrupt class.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong mask or shift can silently alter unrelated bits in a 32-bit MMIO register, causing incorrect surface fetches, cursor corruption, color errors, scaler artifacts, VM faults, hangs, or display underflow.
- The chunk starts in the middle of `HUBPRET3` and ends immediately after the `CM0_CM_BLNDGAM_RAMA_REGION_6_7` comment. Merge/reconciliation must combine adjacent chunks before making whole-block completeness claims.
- Instance families are highly repetitive. `HUBP4`, `HUBPREQ4`, `HUBPRET4`, and `CURSOR0_4` should parallel lower instances, but assuming exact parity can hide valid per-ASIC or per-instance differences. Consistency checks should compare against the generated offset header and hardware spec, not only against nearby instances.
- Field names that themselves end in `MASK`, `STATUS`, or `CLEAR` can produce ambiguous macro names such as interrupt mask masks or status-clear masks. Tooling that naively splits on `_MASK` or assumes `CLEAR` fields are always write-one-to-clear can misparse semantics.
- Several fields expose security and memory-routing controls (`TMZ`, `SNOOP`, `SYSTEM`, surface metadata TMZ, VMID, aperture, TLB, DMDATA VM status). Incorrect values can route fetches through the wrong memory path or break protected-content behavior.
- Gamma and scaler LUT programming depends on correct bank/index/data sequencing. A correct bit mask does not ensure safe ordering; runtime code must respect current-bank selectors, host selection, and update timing to avoid visible artifacts.
- Power-state controls are easy to misuse. Forcing memories off, selecting low-power states, or disabling clocking while a pipe is active can manifest as intermittent blanking, underflow, or stale status reads rather than immediate compile failures.
- DC performance counter controls are diagnostic but still stateful; incorrect clear/enable/mode masks can corrupt performance telemetry and make display underflow or bandwidth regressions harder to diagnose.

## Test Signals

Useful validation for this chunk is a mix of generated-header checks, compile coverage, and hardware/display regression signals:

- Build AMDGPU display with DCN 3.0.2 enabled so `dcn302_resource.c`, HUBP, DPP, IRQ, and register-helper consumers compile against these macro names.
- Run generated consistency checks that each visible `__SHIFT` field has a matching mask where expected, masks fit within 32 bits, and repeated instance blocks preserve intended parity with `HUBP0`-`HUBP4`, `HUBPREQ0`-`HUBPREQ4`, `HUBPRET0`-`HUBPRET4`, and `CURSOR0_0`-`CURSOR0_4`.
- Exercise modesets on DCN 3.0.2 hardware with plane enable/disable, format changes, tiling/DCC, rotation/mirror, alpha planes, protected surfaces, immediate and vblank flips, triple buffering, cursor movement, cursor format changes, and DMDATA/HDR metadata updates.
- Stress bandwidth-sensitive scenarios that validate TTU/QoS/prefetch/vblank/flip/nominal timing fields: high-resolution scanout, multi-plane overlays, chroma planes, scaling, fast page flips, and memory clock transitions.
- Validate scaler output for bypass, 444 RGB/YCbCr scaling, 420 luma/chroma modes, two-tap sharpening, coefficient RAM updates, line-buffer partition choices, and DSCL low-power entry/exit.
- Validate color behavior through pre-CSC, post-CSC, gamut remap, pre-degamma, gamma correction RAM A/B selection, blend-gamma RAM programming, cursor color, color keying, and FP16/fixed format conversion.
- Monitor runtime error/status signals: HUBP underflow, flip pending not clearing, surface flip interrupt delivery, DMDATA done/underflow/VM fault/late status, read-line/vblank interrupt status, line-buffer state, DSCL/CM memory power state, and DC_PERFMON overflow/counter state.
- Include suspend/resume, display hotplug, runtime power management, and pipe power-gating tests to ensure persistent register state is reprogrammed or safely reset.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the start of `HUBPRET3_HUBPRET_MEM_PWR_CTRL`; this chunk begins at `DMROB_MEM_PWR_DIS__SHIFT`, not at the register comment.
- Confirm the next chunk completes `CM0_CM_BLNDGAM_RAMA_REGION_6_7` and the rest of blend-gamma RAM A/B fields before the final file report summarizes the full DPP0 color-management surface.
- Compare DCN 3.0.2 masks against `dcn_3_0_2_offset.h` and equivalent DCN 3.0/3.0.1/3.0.3 generated headers to identify intentional ASIC differences versus generation drift.
