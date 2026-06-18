# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 7214-9828

## Scope

This chunk is a generated AMD DCN 3.1.6 register shift/mask header segment. It contains preprocessor constants only: each hardware field is represented by a `...__SHIFT` macro and a matching `..._MASK` macro. The range covers 2,615 source lines and starts in the middle of the DWB output-gamma RAMA field family, then continues through DWB OGAM RAMB, DC perfmon blocks, VGA/MMHUBBUB writeback, Azalia HDA audio, DCHUBBUB arbitration/clock/debug/timeout controls, SDPIF configuration, and the beginning of DCN VM physical-window fields.

Although this tree is under `ceph-client`, this source is AMDGPU display hardware metadata. It does not implement Ceph filesystem behavior.

## Purpose

The purpose of this chunk is to publish bit positions and masks for DCN 3.1.6 display MMIO registers. Driver code includes this file with `dcn_3_1_6_offset.h`, builds per-ASIC register tables from the generated names, and later uses AMD display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and `REG_WRITE` to pack and unpack fields without embedding literal bit layouts.

The constants are data-like, but correctness is high impact. A wrong shift or mask can still compile and then program an incorrect hardware field for writeback color, capture buffers, memory arbitration, VM apertures, audio control, or debug/status handling.

## Important APIs, Types, And Macros

There are no callable functions, structs, enums, variables, includes, locks, or allocation paths in this source range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating the field.
- `// addressBlock: ...` comments: generated grouping metadata for the owning hardware block.

Major register families in this chunk:

- `DWB_OGAM_RAMA_*` and `DWB_OGAM_RAMB_*`: output-gamma RAM bank A/B fields for writeback. The chunk starts with the final RAMA end-control mask from the previous logical block, then includes RAMA channel offsets, RAMA region pairs 0-33, all RAMB start/base/slope/end/offset fields for B/G/R channels, and RAMB region pairs 0-33. Region-pair registers encode LUT offsets and segment counts for piecewise-linear output-gamma curves.
- `DC_PERFMON3_*`, `DC_PERFMON4_*`, and `DC_PERFMON5_*`: display performance monitor counter control, secondary control, state, perfmon control, current-value interrupt/misc selection, and low/high counter readback fields around writeback, MMHUBBUB, and HDA blocks.
- VGA and VGAIF blocks: `VGA_RENDER_CONTROL`, sequencer reset, mode control, surface pitch/base addresses, HDP/cache controls, per-pipe `D1VGA_CONTROL` through `D6VGA_CONTROL`, security, status, interrupt, source select, and MCIF phase outstanding counters.
- `MCIF_WB_*`: memory client interface writeback fields for buffer-manager software control/status, luma/chroma pitch and addresses, buffer status and resolution for four buffers, arbitration, SCLK/NB pstate watermarks, clock gating, self refresh, VMID, minimum time-to-urgent, and luma/chroma buffer sizes.
- `MMHUBBUB_*` and `WBIF0_*`: writeback memory-hub warmup controls, warmup address/region, minimum time-to-urgent, global MMHUBBUB control, SMU watermark control, miscellaneous WBIF control, outstanding counters, source split, memory power status/control, clock gating, soft reset, DMU interface error status, client unit ID, and warmup VMID.
- `AZALIA_*`, `AZALIA_F0_*`, `AZF0STREAM*`, `AZF0ENDPOINT*`, and `AZF0INPUTENDPOINT*`: HDA/HDMI/DP audio controller fields, codec root parameters and controls, CRC control/readback, memory power state, stream index/data windows for 16 streams, and codec endpoint index/data windows for output and input endpoints.
- `DCHUBBUB_ARB_*`: hubbub arbitration and watermark fields for outstanding DF requests, saturation/QoS forcing, DRAM state control, watermarks A-D for urgency, memory trip latency, self-refresh enter/exit including Z8 variants, DRAM clock-change permission, fractional urgent bandwidth for nominal and flip traffic, host-VM controls, watermark-change control, and timeout enable.
- DCHUBBUB system fields: global timer, surface check addresses, `VTG0_CONTROL` through `VTG3_CONTROL`, soft reset, clock control, `DCFCLK_CNTL`, latency/performance measurement controls, vline snapshot, overflow/status clearing, timeout detection and interrupt status, `FMON_CTRL`, and test debug index/data.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, `DCHUBBUB_FORCE_IO_STATUS_*`, and `DCN_VM_*`: SDPIF port/credit/status/error/force-snoop fields, physical PDE/PTE request controls, force-IO status address/pipe/type capture fields, and the start of framebuffer/AGP aperture fields through `DCN_VM_AGP_BASE`.

## Control Flow And Runtime Behavior

The header has no runtime control flow. Runtime behavior is supplied by generated-table consumers:

1. DCN 3.1.6 resource and DMUB code includes `dcn_3_1_6_offset.h` and this header.
2. Register-list macros paste symbolic register and field names into table initializers. Offsets come from the offset header; shifts and masks come from this file.
3. DCN resource construction stores those constants in typed register/mask/shift tables such as hubbub, hubp, timing generator, clock, and writeback-related tables.
4. Runtime code uses those tables to perform read-modify-write programming and status reads against MMIO registers.

Concrete integration in this tree includes `display/dc/resource/dcn316/dcn316_resource.c`, which includes this generated header and builds `hubbub_reg`, `hubbub_shift`, and `hubbub_mask` using `HUBBUB_REG_LIST_DCN31(0)` and `HUBBUB_MASK_SH_LIST_DCN31(__SHIFT/_MASK)`. Those lists consume fields from this chunk such as `DCHUBBUB_ARB_FRAC_URG_BW_*`, `DCHUBBUB_ARB_REFCYC_PER_TRIP_TO_MEMORY_*`, Z8 self-refresh watermarks, `DCHUBBUB_CLOCK_CNTL`, `DCHUBBUB_SDPIF_CFG0`, and the `DCN_VM_FB_LOCATION_*` / `DCN_VM_AGP_*` aperture fields.

DMUB integration is direct as well. `display/dmub/src/dmub_dcn316.c` includes `dcn_3_1_6_offset.h` and this header, then initializes `dmub_srv_dcn316_regs` with `DMUB_DCN31_REGS()` and `DMUB_DCN31_FIELDS()`. The DMUB DCN31 field list consumes `DCN_VM_FB_LOCATION_BASE__FB_BASE` and `DCN_VM_FB_OFFSET__FB_OFFSET` from this chunk so firmware-facing code can read framebuffer placement with the correct DCN316 bit layout.

Writeback and memory-client behavior is shared with older DCN helpers. The `MCIF_WB_*` fields match the table style in `display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h` and are programmed by `dcn20_mmhubbub.c` for writeback buffer addresses, high address halves, pitch, size, arbitration, watermarks, pstate behavior, and buffer-manager interrupts. DWB color-management code uses the DWB OGAM RAMA/RAMB fields to program output-gamma LUT curves and bank selection around writeback capture.

DCHUBBUB arbitration fields are consumed by hubbub code such as the DCN30/DCN31/DCN32 families. Watermark programming writes the urgency, self-refresh, DRAM clock-change, and fractional bandwidth registers. SDPIF control code updates `DCHUBBUB_SDPIF_CFG0.SDPIF_PORT_CONTROL` to hand SDPIF port control between DC and another agent as required by the platform path.

The Azalia, VGA, perfmon, timeout, force-IO, and debug blocks are mostly accessed by generic display/audio/debug paths rather than by functions in this header. This file only describes the bit packing; it does not define when to clear status, arm interrupts, select debug indices, or read counters.

## State And Persistence Behavior

The macros hold no software state and persist nothing. They describe stateful hardware registers whose values remain in the display engine until later register writes, mode-set reprogramming, suspend/resume restore, power gating, soft reset, or ASIC reset changes them.

State represented by this chunk includes:

- DWB output-gamma RAM bank configuration, including B/G/R channel start/end/base/slope/offset values and per-region LUT segment layout for RAMA/RAMB.
- Perfmon counter source selection, enable/freeze/clear controls, current counter values, interrupt selection, overflow/status fields, and high/low readback.
- VGA mode, source selection, render/security/cache/HDP behavior, per-pipe enablement, and VGA interrupt/status state.
- MCIF writeback buffer-manager state: active addresses, buffer pitches, luma/chroma sizes, buffer status, buffer resolution, VMID, fences/locks, interrupt enables/acks, and watermark/pstate controls.
- MMHUBBUB and WBIF state for warmup, memory power, clock gating, soft reset, source split, SMU watermarks, outstanding counters, and DMU interface error status.
- HDA/Azalia controller and codec state, including audio DTO programming, DMA control, payload capabilities, CRC counters/results, power state, stream index/data windows, and endpoint index/data windows.
- DCHUBBUB arbitration and memory-service state for watermarks A-D, Z8 self-refresh watermarks, DRAM clock-change permissions, fractional urgent bandwidth, host-VM behavior, global timing, VTG links, latency measurement, ROB overflow, timeout detection, force-monitor controls, and SDPIF port/credit/error status.
- DCN VM aperture state for framebuffer base/top/offset and AGP bottom/top/base fields visible at the end of the chunk.

Some fields are not plain configuration bits. Status and clear fields such as MCIF buffer status, VGA interrupt/status, MMHUBBUB memory power status, Azalia CRC/power status, DCHUBBUB overflow/timeout/SDPIF error state, and force-IO sticky status may be read-only, latched, self-clearing, write-one-to-clear, or sequencing-sensitive. The generated header does not encode access type.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies the matching register offsets.
- `display/dc/resource/dcn316/dcn316_resource.c`, which includes this header and builds DCN316 resource tables from generated register and field macros.
- `display/dmub/src/dmub_dcn316.c` and `display/dmub/src/dmub_dcn31.h`, which expose selected DCN316 register offsets, masks, and shifts to DMUB service code.
- `display/dc/hubbub/dcn31/dcn31_hubbub.h`, `dcn30_hubbub.h`, and related hubbub implementation files, which consume DCHUBBUB watermark, SDPIF, VM aperture, clock, and fault-related field names through `HUBBUB_SF(...)` lists.
- `display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h` and `dcn20_mmhubbub.c`, whose writeback memory-interface register tables and runtime programming paths use the `MCIF_WB_*` field layout represented in this chunk.
- DWB writeback and color-management helpers, which rely on the DWB OGAM field names for output-gamma LUT/RAM programming.
- Audio/HDA code paths and diagnostics that use the Azalia register fields through the generated AMD register-access namespace.

The macro names themselves are the compile-time API. Missing or renamed macros are usually caught by table initializers. Wrong numeric constants are harder: they can preserve a clean build while producing display corruption, failed writeback, bad audio behavior, missed interrupts, or unstable power-state transitions.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts with the tail of a RAMA end-control field whose register began in the previous chunk, and it stops after `DCN_VM_AGP_BASE__AGP_BASE__SHIFT`; the matching mask and later VM fields continue in the next chunk.
- Generated-header drift is the main risk. A single incorrect mask width or shift can misprogram DWB gamma regions, MCIF writeback addresses, watermarks, VM apertures, audio DMA controls, or status clear bits.
- DWB OGAM programming is banked and channel-specific. RAMA/RAMB and B/G/R fields are structurally similar; swapped masks or region-pair errors can create color errors that only appear on writeback/capture paths using that LUT bank.
- MCIF writeback buffer address fields are high impact. Bad low/high address or pitch masks can direct writeback to the wrong memory, corrupt captured frames, trip VM faults, or break chroma/luma layout.
- Watermark and arbitration fields are timing-sensitive. Incorrect `DCHUBBUB_ARB_*` masks can cause underflow, stutter-entry failures, bad DRAM clock-change decisions, or bandwidth issues only under high-resolution, multi-display, low-clock, or page-flip stress.
- Status/clear/interrupt fields need correct access ordering. VGA, MCIF_WB, Azalia, perfmon, DCHUBBUB timeout, SDPIF, force-IO, and overflow bits may require read-before-clear or write-one-to-clear behavior that this header does not document.
- SDPIF credit and port-control fields affect request routing between display and system fabric. Wrong masks can leave requests blocked, credit errors uncleared, or snooping/host-VM attributes misapplied.
- Memory-power and clock-gating fields interact with sequencing. Forcing resets or gating clocks around active writeback, audio, or hubbub traffic can create transient failures even when masks are correct.
- The Azalia stream and endpoint index/data windows are repeated 16 and 8 times respectively. Instance-specific generation mistakes can affect only one audio stream or connector path and can be missed by basic display-only testing.

## Test Signals

Useful validation combines generated-header consistency checks, build coverage, and hardware behavior:

- Build AMDGPU/DC with DCN316 enabled. Missing or renamed symbols should fail in `dcn316_resource.c`, `dmub_dcn316.c`, hubbub table construction, DMUB table construction, writeback/MMHUBBUB users, or audio/debug users.
- Mechanically verify that every `__SHIFT` field visible in lines 7214-9828 has the expected companion `_MASK` field when the generated schema defines one, and that masks align with their shifts.
- Diff this DCN 3.1.6 slice against adjacent generated headers for compatible ASICs such as DCN 3.1.5, DCN 3.1.4, or DCN 3.2 where layout parity is expected.
- Exercise display writeback with multiple output formats, luma/chroma planes, four-buffer cycling, high address bits, VMID selection, buffer fences/locks, overflow interrupts, and suspend/resume.
- Validate DWB color-management writeback with OGAM bypass, RAMA/RAMB bank selection, B/G/R channel LUT writes, and region-pair programming across all 0-33 regions.
- Run bandwidth-stress display modes that exercise hubbub watermarks: high refresh, multiple displays, DCC, flips, memory-clock changes, self-refresh/Z8 transitions, and low-power entry/exit.
- Check DMUB boot and framebuffer-window setup on DCN316, especially reads of `DCN_VM_FB_LOCATION_BASE` and `DCN_VM_FB_OFFSET`.
- Exercise SDPIF control and monitor `SDPIF_REQ_CREDIT_ERROR`, response status, force-snoop behavior, and force-IO sticky status where diagnostics expose them.
- Validate HDA/DP/HDMI audio playback across multiple streams/connectors, including power transitions and CRC/debug paths if available.
- Read perfmon3/4/5 counters with known event selections and verify counter enable, clear, freeze, low/high readback, overflow, and interrupt status behavior.
- Monitor kernel logs and hardware status for MCIF writeback overrun, DCHUBBUB ROB overflow, timeout interrupts, VM faults, audio underflow, display underflow, or resume-only regressions.

## Cross-Chunk Notes

The previous chunk owns the earlier DWB top/color-management fields and the beginning of `DWB_OGAM_RAMA_END_CNTL2_R`. This chunk completes most of the RAMA/RAMB output-gamma region layout but begins from a partial logical register. The next chunk must be consulted for the `DCN_VM_AGP_BASE__AGP_BASE_MASK` companion field and subsequent DCN VM/security/fault blocks. The final per-file report should merge adjacent chunks before making complete claims about DWB OGAM, DCN VM, or the full DCN316 shift/mask namespace.
