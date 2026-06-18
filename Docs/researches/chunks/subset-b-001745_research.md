# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 2678-5218

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register-offset header segment. It contains preprocessor constants only: each hardware register has one `mm...` macro for the MMIO register offset and one matching `mm..._BASE_IDX` macro that selects the register base index used by AMDGPU register helpers. The chunk spans 2,541 source lines and contains 1,207 register-offset macros plus 1,207 `_BASE_IDX` macros.

The slice begins in the tail of the `HUBP2` block at `mmHUBP2_DCHUBP_REQ_SIZE_CONFIG_C` and ends in the early `CNVC_CFG2` block at `mmCNVC_CFG2_FCNV_FP_SCALE_R`, so both chunk boundaries are partial hardware blocks. Complete file-level analysis must reconcile this chunk with adjacent chunks for the omitted opening `HUBP2` registers and the remaining `DPP2` converter/scaler/color-management registers.

## Purpose

The purpose of this header segment is to provide symbolic register addresses for the DCN 3.0.2 display pipeline. Driver code includes this file so it can populate per-instance register tables for HUBP, HUBPREQ, HUBPRET, cursor, DPP, CNVC, DSCL, CM, and DC perfmon blocks without hard-coding numeric offsets. The companion `dcn_3_0_2_sh_mask.h` header supplies the bit shifts and masks used with these addresses.

This is data-like source rather than executable logic. Its correctness depends on exact correspondence with the DCN 3.0.2 hardware register map and with the generated register-list macros consumed by the DC resource code.

## Address Blocks And Register Surface

Visible HUBP-side blocks:

- Tail of `HUBP2`: request-size config, HUBP control, clock control, virtual memory page config, HUBPREQ debug/debug double-buffer, and measurement window controls.
- `dce_dc_dcbubp2_dispdec_hubpreq_dispdec` at base `0x6e0`: `HUBPREQ2` surface pitch/address/meta-address, flip control, in-use/earliest-in-use readbacks, TTU/QoS, VM aperture/TLB, destination geometry, prefetch, vblank/flip/nominal delivery parameters, cursor settings, and memory power registers.
- `dce_dc_dcbubp2_dispdec_hubpret_dispdec`, `cursor0`, and `hubp_dcperfmon` blocks: `HUBPRET2`, `CURSOR0_2`, and `DC_PERFMON8`.
- Parallel full instance sets for `HUBP3`, `HUBP4`, and `HUBP5`, including `HUBPREQ3` through `HUBPREQ5`, `HUBPRET3` through `HUBPRET5`, `CURSOR0_3` through `CURSOR0_5`, and perfmon blocks `DC_PERFMON9` through `DC_PERFMON11`.

Visible DPP-side blocks:

- `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CM0`, and `DC_PERFMON6`, rooted at DPP0 base `0x0` plus perfmon base `0x3890`.
- `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, `CM1`, and `DC_PERFMON12`, rooted at DPP1 base `0x5ac` plus perfmon base `0x3e3c`.
- Start of `DPP_TOP2` and `CNVC_CFG2`, rooted at DPP2 base `0xb58`.

The macro-family count in this slice is dominated by two complete color-management blocks (`CM0`, `CM1`, 500 definitions each including offsets and base indices), four HUBPREQ families (`HUBPREQ2`-`HUBPREQ5`, 162 definitions each), DPP converter/scaler families, cursor blocks, perfmon blocks, and repeated HUBP/HUBPRET controls.

## Important Macros And Register Families

`HUBP*_` macros define hub pipe control and data-fetch registers. They cover surface address configuration, viewport and request-size controls, HUBP clock/control registers, VM page configuration, and debug/measurement registers.

`HUBPREQ*_` macros define the request/pre-request side of plane fetch. Important groups include `DCSURF_*` pitch, primary/secondary surface addresses, metadata addresses, surface control, flip control, flip interrupt, in-use/earliest-in-use registers, TTU QoS and cursor TTU controls, VM system aperture and L1 TLB control, destination dimensions and scaler output geometry, prefetch timing, vblank/flip/nominal delivery parameters, per-line delivery, cursor settings, reference-clock to pixel-clock ratio, DRQ limit, and HUBPREQ memory power control/status.

`HUBPRET*_` macros define return/read-line behavior for hub pipe fetch. The visible register set is compact: control, memory power control/status, and read-line control registers.

`CURSOR0_*` macros define per-HUBP cursor surface controls: cursor control, surface address high/low, size, position, hot spot, destination offset, color slots, settings, and memory power control/status.

`DC_PERFMON*` macros define display performance monitor registers for HUBP and DPP instances. Each perfmon block exposes counter control, counter state, perfmon control, current value, and high/low counter registers. In this chunk the HUBP perfmon instances are `DC_PERFMON8`-`DC_PERFMON11`, while DPP perfmon instances include `DC_PERFMON6` and `DC_PERFMON12`.

`DPP_TOP*` macros define top-level DPP controls: DPP control, soft reset, CRC result registers, CRC control, and host read control. These are used for DPP bring-up, reset, diagnostics, and CRC validation.

`CNVC_CFG*` and `CNVC_CUR*` macros define converter configuration and cursor conversion controls. The configuration blocks include surface pixel format, format control, floating-point bias and scale, color keyer alpha/R/G/B, alpha LUT and pre-dealpha, output channel expansion, and memory power control/status. The cursor converter blocks include cursor control and cursor color registers.

`DSCL*` macros define display scaler setup: scaler tap/filter control, viewport start/size, reciprocal and initial-phase values, ratio registers, overscan values, round offset, clamp settings, coefficient RAM tap data/address/control, manual replicate controls, DOUT remap, debug registers, and memory power control/status.

`CM0` and `CM1` macros define DPP color-management registers. They cover gamut remap matrices, color correction, alpha/dealpha, coefficient format, HDR multiplier, de-gamma and regamma LUT control/data/region tables, output CSC matrices, shaper LUT configuration, shaper RAM A/B regions, 3D LUT mode/index/data/read-write controls, output normalization/offset, memory power controls, and debug index/data.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime behavior is indirect: `dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` and `dcn/dcn_3_0_2_sh_mask.h`, then uses macros such as `HUBP_REG_LIST_DCN30(id)` and `DPP_REG_LIST_DCN30(id)` to initialize static register tables for each hardware instance. Constructors such as `dcn302_hubp_create()` and `dcn302_dpp_create()` pass those tables to HUBP and DPP object constructors, after which the DCN driver accesses the registers through shared `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and related helpers.

The hardware flows represented by these offsets include:

- Plane fetch programming: HUBP/HUBPREQ offsets let the driver program framebuffer and metadata base addresses, surface pitch, VMID/aperture/TLB behavior, surface control, and request sizing.
- Page flip and timing: flip-control, flip-parameter, vblank-parameter, nominal-delivery, prefetch, and in-use registers participate in flip scheduling, address latching, and watermarked memory request timing.
- Cursor composition: cursor address, position, hot spot, color, size, and cursor settings registers define hardware cursor fetch and placement for each pipe.
- Scaling and format conversion: CNVC and DSCL offsets support pixel format conversion, floating-point bias/scale, color-keying, scaler ratios, viewport geometry, filter taps, and output remapping.
- Color pipeline programming: CM offsets support de-gamma, regamma, gamut remap, output CSC, shaper LUTs, and 3D LUT programming for DPP0 and DPP1.
- Diagnostics and validation: DPP CRC registers and perfmon blocks expose counter and CRC signals used by debug, validation, and performance-monitoring paths.
- Memory power management: HUBPREQ, HUBPRET, cursor, CNVC, DSCL, and CM memory power control/status offsets let the driver gate internal memories and observe power state.

## State And Persistence

The macros themselves hold no mutable state and allocate no storage. They describe persistent memory-mapped hardware registers. Writes through these offsets mutate GPU display state until changed again, reset, power-gated, or reinitialized during modeset, suspend/resume, or GPU reset handling.

Several register groups represent stateful hardware handshakes:

- Surface address and flip registers are double-buffered or latched by display timing. Incorrect sequencing can leave stale addresses active or cause visible corruption at vblank boundaries.
- `DCSURF_SURFACE_INUSE*` and `DCSURF_SURFACE_EARLIEST_INUSE*` are readback/status style registers that expose address residency and hardware-use windows rather than ordinary driver-owned state.
- TTU, prefetch, vblank, nominal, and per-line delivery registers encode bandwidth/timing model outputs. They must stay consistent with DML calculations, watermark programming, clock selection, and plane geometry.
- LUT programming registers (`CM*_DEGAM_*`, `CM*_REGAMMA_*`, `CM*_SHAPER_*`, `CM*_3DLUT_*`) are persistent color state. Index/data style programming must preserve ordering, RAM selection, write-enable masks, and mode bits.
- Memory power control/status registers expose power-gating requests and acknowledgement. The offset header does not encode safe polling, delay, or write-one-to-clear semantics; consumers must rely on block-specific code and bitfield masks.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.2 shift/mask header for field-level operations. It also depends on AMDGPU display register-list macros that combine symbolic block names with instance IDs, for example `SRI_ARR(..., HUBPREQ, id)` and DPP/HUBP list macros, to resolve `mmHUBPREQ3_*`, `mmDPP_TOP1_*`, `mmCM0_*`, and similar names.

Confirmed integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`, which includes this header and initializes DCN 3.0.2 resource register tables.
- `dcn302_hubp_create()`, which uses `HUBP_REG_LIST_DCN30(id)` to construct HUBP instances backed by `HUBP*`, `HUBPREQ*`, `HUBPRET*`, and cursor/perfmon offsets from this slice.
- `dcn302_dpp_create()`, which uses `DPP_REG_LIST_DCN30(id)` to construct DPP instances backed by `DPP_TOP*`, `CNVC_*`, `DSCL*`, and `CM*` offsets from this slice.
- DCN register helper infrastructure (`reg_helper.h` and block-specific constructors), which treats these numeric macros as MMIO offsets and pairs them with field masks/shifts for read-modify-write operations.
- Display bring-up, mode programming, plane update, cursor update, color management, CRC, perfmon, and power-management paths that operate on the generated register tables rather than directly including this header at every call site.

Because these macros are compile-time API surface, a missing or renamed macro breaks resource table compilation. A wrong numeric value is more dangerous: it can compile cleanly while redirecting reads or writes to the wrong hardware register.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Any offset mismatch against the DCN 3.0.2 register specification can corrupt unrelated display state, causing plane fetch faults, blank displays, bad flips, color corruption, cursor artifacts, or power-management regressions.
- The chunk contains repeated hardware instances that are intentionally parallel but not independently validated by C type checking. Copy or generation errors between `HUBPREQ2`-`HUBPREQ5`, `CM0`/`CM1`, or `DPP_TOP0`/`DPP_TOP1` can be hard to detect unless instance parity checks exist.
- The first and last blocks are partial. `HUBP2` starts before line 2678, and `CNVC_CFG2` continues after line 5218. Merge-lane research must not treat this slice as complete coverage for those two blocks.
- `_BASE_IDX` values are part of the address resolution contract. Most definitions here use base index `2`, but earlier file sections include other base indices; tooling that assumes all DCN offsets share one base can read or write the wrong MMIO aperture.
- CM LUT and 3D LUT registers use index/data programming patterns. Correct offsets are necessary but not sufficient; write ordering, selected RAM bank, write-enable mask, and 30-bit data mode must also be correct in consuming code.
- Perfmon and CRC registers often have control/status coupling. A stale offset in a diagnostic path may not affect ordinary display output but can invalidate test results or hide hardware failures.
- Power-control and power-status registers are safety-sensitive. Incorrect offsets or instance selection can leave memories powered down while a pipe is active, or prevent low-power entry.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generated-header, and hardware display tests:

- Compile DCN 3.0.2 resource code to catch missing macro names used by `HUBP_REG_LIST_DCN30(id)`, `DPP_REG_LIST_DCN30(id)`, and related register lists.
- Generated-header consistency checks should verify every `mm...` offset in this chunk has a matching `mm..._BASE_IDX`, and that expected repeated instances have equivalent register-name sets where the hardware specification requires parity.
- Compare this offset header with `dcn_3_0_2_sh_mask.h` and any register-list definitions to ensure every table entry has both an address and usable field masks/shifts.
- Display mode-set and page-flip testing should exercise multi-plane fetch, framebuffer address changes, metadata address changes, vblank timing, prefetch/TTU programming, and DML-derived delivery parameters on HUBP2-HUBP5.
- Cursor tests should cover movement, hot spot changes, color cursor formats, memory power transitions, and cursor updates across all visible cursor instances.
- Scaling and color tests should cover CNVC format conversion, DSCL viewport/ratio/filter programming, degamma/regamma/shaper/3D LUT programming, gamut remap, output CSC, HDR multiplier, and alpha/dealpha behavior on DPP0 and DPP1.
- Diagnostics should validate DPP CRC reads, perfmon counter programming, and host-read control on affected DPP and HUBP instances.
- Suspend/resume, GPU reset, and display power-gating tests should confirm HUBPREQ/HUBPRET/cursor/CNVC/DSCL/CM memory power state is restored or reprogrammed correctly.

## Open Questions For Merge Lane

- Confirm the preceding chunk documents the full start of `HUBP2`, including surface address config and viewport registers before `DCHUBP_REQ_SIZE_CONFIG_C`.
- Confirm the following chunk documents the remainder of `CNVC_CFG2` and subsequent DPP2 blocks, so DPP2 is not underrepresented in the final per-file report.
- Check whether any DCN 3.0.2-specific differences from DCN 3.0.1 or DCN 2.1.0 in these offsets are intentional hardware changes; the repeated names are similar across ASIC revisions, but offset shifts exist in earlier headers.
