# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 2614-5117

## Purpose

This chunk is a generated AMD DCN 4.1.0 register-offset slice. It contains no executable logic; it exports C preprocessor constants mapping display-controller register names to MMIO register offsets, plus matching `<register>_BASE_IDX` constants used by DCN register-helper macros to select the correct base segment. The companion `dcn_4_1_0_sh_mask.h` file supplies field shifts and masks; this chunk supplies the address side of those register accesses.

The requested range contains 2,395 `#define` entries: 1,197 register-offset definitions and 1,198 `_BASE_IDX` definitions, organized under 28 address-block comments. The slice starts in the middle of the `HUBPRET1` register group and ends in the early `CM3` color-management group, so both boundaries are chunking artifacts rather than complete hardware-block boundaries.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It is not Ceph or distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this range. The public interface is the generated macro namespace:

- `reg<REGISTER>` expands to the register's DCN 4.1.0 offset value.
- `reg<REGISTER>_BASE_IDX` expands to the base segment index, almost always `2` in this chunk.
- Address-block comments document the generated hardware block name and the block-local base address used by the generator.

Important register families in this chunk are:

- Tail of `HUBPRET1_*`: read-line registers for HUBP1/HUBPRET1, including read-line slots, interrupt, read-line value, and read-line status.
- `CURSOR0_1_*`: cursor and DMDATA registers for the cursor block attached to HUBP1, including cursor control, surface address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power control/status, dynamic metadata address/control/QoS/status/software registers, and HUBP 3D LUT address/control/DLG registers.
- `HUBP2_*` and `HUBP3_*`: display HUBP surface configuration, address/tiling configuration, primary/secondary viewport start and dimensions, request-size configuration, HUBP clock/control, VMPG, MALL, MCACHE ID, debug, measure-window, and MALL status registers for HUBP instances 2 and 3.
- `HUBPREQ2_*` and `HUBPREQ3_*`: surface pitch, VMID, primary/secondary surface address high/low for luma/chroma planes, surface/flip control, surface flip interrupt, in-use and earliest-in-use addresses, TTU/QoS controls, VM aperture and fault/default controls, cursor settings, display page table base, VM context, pstate force, and prefetch/deadline/per-channel delivery registers for HUBPREQ instances 2 and 3.
- `HUBPRET2_*` and `HUBPRET3_*`: HUBP vblank/read-line interrupt and status registers for instances 2 and 3.
- `CURSOR0_2_*` and `CURSOR0_3_*`: cursor/DMDATA/HUBP 3D LUT registers for HUBP instances 2 and 3, mirroring the `CURSOR0_1_*` shape.
- `CNVC_CFG0_*` through `CNVC_CFG3_*`: DPP converter configuration for DPP0-DPP3, covering surface pixel format, format control, floating-point format scale/bias, color keying, alpha LUT, pre-dealpha, pre-CSC matrix coefficients for main and B paths, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0_*` through `CNVC_CUR3_*`: converter cursor overlay registers for DPP0-DPP3, including cursor control, color registers, and cursor floating-point scale/bias.
- `DSCL0_*` through `DSCL3_*`: DPP scaler registers for DPP0-DPP3, including coefficient RAM, scaler mode, tap control, manual replication, horizontal/vertical ratios, chroma ratios, initial phases, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer format and memory controls, DSCL/OBUF memory power, EASF/scaler matrix controls, ring-estimation controls, BF/PWL segments, iSharp controls, and iSharp LUT memory power.
- `CM0_*`, `CM1_*`, `CM2_*`, and beginning of `CM3_*`: DPP color-management registers for post-CSC, post-CSC B path, bias, gamma-correction control, gamut remap coefficients, gamma LUT index/data/control, gamma RAM A/B start/end/slope/base/offset/region metadata, HDR multiplier, memory power, coefficient format, dealpha, debug index/data, and DPP CRC. The range ends after `regCM3_CM_GAMCOR_CONTROL`.
- `DPP_TOP0_*` through `DPP_TOP2_*`: DPP top-level control, clock control, debug, CRC control/value, output buffer memory control, DISPCLK current count, shared memory power, and DSC memory power controls for DPP0-DPP2. DPP3 top-level registers are outside this chunk.

The macro families are mechanically repeated by instance. For example, DPP0 at base address `0x0`, DPP1 at `0x5ac`, DPP2 at `0xb58`, and DPP3 at `0x1104` expose nearly the same CNVC, cursor, DSCL, and CM register names with different numeric suffixes.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated header:

1. DCN 4.1.0 consumers include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. Register-list macros token-paste names such as `regHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS` and `regHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS_BASE_IDX`.
3. Helper macros add the selected base segment to the generated offset, producing absolute MMIO addresses stored in per-block register tables.
4. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers combine this offset table with shift/mask definitions from the companion header.

The macros do not encode ordering. Consumers still need to program HUBP surfaces, cursor memory, DPP format conversion, scaler ratios/taps, color-management LUTs, CRC, interrupts, memory-power state, and flip/deadline state in the hardware-defined sequence and update window.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It names hardware-visible registers whose values live in DCN display hardware:

- HUBP surface and viewport state for scanout address, tiling, pitch, VMID, primary/secondary plane addresses, in-use and earliest-in-use latches, MCACHE/MALL/VMPG behavior, and request sizing.
- HUBPREQ state for surface flips, TTU/QoS, VM apertures, page-table base, VM context, pstate forcing, cursor request settings, and deadline/prefetch delivery parameters.
- HUBPRET state for vblank and read-line interrupt timing/status.
- Cursor state for enablement, mode, address, dimensions, position, hot spot, stereo, destination offset, DMDATA, memory-power state, and HUBP-attached 3D LUT access.
- DPP converter state for pixel format, alpha/dealpha/realpha, color keying, pre-CSC, pre-degamma, and cursor overlay color/scale/bias.
- DSCL state for filter coefficients, scaler mode, taps, phase/ratio programming, overscan, recout/MPC size, line-buffer behavior, DSCL/OBUF memory power, EASF, BF/PWL, and iSharp controls.
- CM state for post-CSC, gamut remap, gamma RAM A/B programming, LUT access, HDR multiplier, dealpha, coefficient format, debug, memory power, and DPP CRC.
- DPP top-level state for control, clock/debug, CRC capture, output buffer memory, shared memory power, and DSC memory power.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, plane update, pipe reset, power-gating transition, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, CRC, debug, in-use, earliest-in-use, memory-power-status, and counter-like fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the owning pipe and clocks are enabled. This offset header does not describe access semantics; those rules must come from silicon documentation and block-specific driver code.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DCN 4.1.0 register database and the companion shift/mask header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h` provides matching field masks and shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` includes both generated headers and builds DMUB register/field tables through `REG_OFFSET_EXP`, `FD_MASK`, and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c` includes both headers and uses token-pasted `SRI`/`SRI_DMUB` forms to construct IRQ source register addresses and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes both headers and defines `SR`, `SRI`, `SRI_ARR`, `SRII`, and related macros that expand these generated names into resource-pool register tables. The same file references `DPP_TOP0_DPP_CRC_*` registers from this chunk in the hardware-sequencer register list.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c`, `hw_factory_dcn401.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c` include the generated headers for DCN 4.1.0 GPIO and clock-manager register access.
- Shared AMD display block implementations for HUBP, DPP, DSCL, cursor, color management, IRQ, DMUB, hardware sequencing, and register helpers consume these constants through generated register-list macros rather than manually spelling most offsets at call sites.

The most direct behavioral integration from this slice is plane scanout and pixel processing for HUBP instances 1-3 and DPP instances 0-3: surface flips, cursor programming, scaling, color conversion, gamma/gamut programming, CRC/debug, MALL/MCACHE interaction, VM page-table programming, and power/memory state management.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset or base index can compile successfully while reading or writing the wrong MMIO register.
- The file is generated. Manual edits risk diverging from the authoritative register database, matching shift/mask definitions, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first complete offset in this range is `regHUBPRET1_HUBPRET_READ_LINE1`, but the preceding `HUBPRET1_HUBPRET_READ_LINE0` offset appears before line 2614 while its `_BASE_IDX` appears in this chunk. The range ends at `regCM3_CM_GAMCOR_CONTROL`, with most CM3 registers continuing in the next chunk.
- Repeated HUBP/HUBPREQ/HUBPRET/CURSOR/DPP instance layouts make generator drift hard to catch. DPP0 or HUBP2 working does not prove DPP1-DPP3 or HUBP3 offsets are correct.
- Base-index mistakes are especially high impact. Consumers add `ctx->dcn_reg_offsets[BASE_IDX]` or a compiled base segment to the offset; an incorrect `_BASE_IDX` can move otherwise correct register offsets into the wrong MMIO segment.
- Surface address, pitch, VM, page-table, aperture, and flip registers are scanout-critical. Bad offsets can lead to blank displays, page faults, stale flips, incorrect in-use latches, invalid memory fetches, or display underflow.
- Cursor address, size, position, hot-spot, stereo, and DMDATA offsets are user-visible and frequently updated. Errors can cause missing cursors, corruption, hot-spot mismatch, stereo placement bugs, or metadata delivery failures.
- DSCL ratio, tap, coefficient RAM, phase, line-buffer, EASF, BF/PWL, and iSharp offsets are precision-sensitive. A small mapping error can show up as blur, ringing, chroma displacement, crop mistakes, or scaler memory-power failures.
- CM, CSC, gamut, gamma RAM, HDR multiplier, and coefficient-format offsets affect color correctness. Regressions may be subtle and missed by simple modeset or boot tests.
- Interrupt/status/ack, CRC/debug, memory-power, and pstate-force registers can have side effects. Confusing a status, clear, enable, or power-control register can cause interrupt storms, missed vblank/read-line events, stuck power state, bad CRC reads, or resume-only failures.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.1.0 hardware behavior:

- Build AMDGPU display with DCN 4.1.0/DCN401 enabled. Missing or renamed constants should fail in DMUB, IRQ, GPIO, clock-manager, resource, hardware-sequencer, HUBP, DPP, or register-table construction.
- Mechanically compare this range against AMD's authoritative DCN 4.1.0 register source and the adjacent `dcn_4_1_0_sh_mask.h` names. Verify that each complete register group has both an offset and a `_BASE_IDX`, allowing for the artificial chunk boundaries.
- Check that repeated instance families preserve expected stride/base patterns: HUBP/HUBPREQ/HUBPRET/CURSOR instances around `0x370`, `0x6e0`, and `0xa50`, and DPP instances around `0x0`, `0x5ac`, `0xb58`, and `0x1104`.
- Exercise plane enable/disable, primary/secondary surface flips, viewport changes, tiling/pitch variants, VMID/page-table changes, MALL/MCACHE paths, pstate-force paths, suspend/resume, and rapid modesets.
- Exercise cursor enable/disable, movement, hotspot changes, size and pitch changes, stereo cursor modes, DMDATA programming, cursor memory power, and 3D LUT cursor-adjacent paths for pipes 1-3.
- Exercise scaler paths across identity scale, up/downscale, fractional scaling, chroma formats, overscan, recout changes, line-buffer pressure, coefficient RAM reload, EASF/BF/iSharp controls, and DSCL/OBUF memory-power transitions.
- Validate color paths with CRC or visual/color tests for pre-CSC, post-CSC, gamut remap, gamma correction RAM A/B, HDR multipliers, alpha/dealpha/realpha, color keying, and pixel-format conversion across DPP0-DPP3.
- Watch kernel logs and display diagnostics for page faults, underflows, stuck flips, missed vblank/read-line interrupts, cursor corruption, scaler artifacts, CRC mismatches, color regressions, memory-power transition failures, and resume-only display artifacts.

## Cross-Chunk Notes

The previous chunk contains the beginning of the `HUBPRET1` read-line group. The next chunk continues the `CM3` color-management register set after `CM3_CM_GAMCOR_CONTROL`. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 4.1.0 register offsets or all HUBP/DPP instances.
