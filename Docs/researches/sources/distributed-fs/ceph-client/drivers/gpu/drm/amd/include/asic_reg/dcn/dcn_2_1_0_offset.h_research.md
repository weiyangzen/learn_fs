# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001650`: lines 1-2687, `Docs/researches/chunks/subset-b-001650_research.md`
- `subset-b-001651`: lines 2688-5235, `Docs/researches/chunks/subset-b-001651_research.md`
- `subset-b-001652`: lines 5236-7883, `Docs/researches/chunks/subset-b-001652_research.md`
- `subset-b-001653`: lines 7884-10415, `Docs/researches/chunks/subset-b-001653_research.md`
- `subset-b-001654`: lines 10416-13053, `Docs/researches/chunks/subset-b-001654_research.md`
- `subset-b-001655`: lines 13054-13875, `Docs/researches/chunks/subset-b-001655_research.md`

## Chunk Research

### subset-b-001650: lines 1-2687

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 1-2687

## Scope And Purpose

This chunk is the first 2,687 lines of the generated DCN 2.1.0 register-offset header used by the AMDGPU display stack. It contains only preprocessor definitions: an include guard, AMD's permissive license block, address-block comments, `mm...` register-offset constants, and matching `mm..._BASE_IDX` segment selectors. The assigned range starts at legacy VGA/MMHUBBUB offsets and ends partway through the second HUBP cursor register block at `mmCURSOR0_1_DMDATA_STATUS_BASE_IDX`.

The header's purpose is to give DCN 2.1 display code stable symbolic register names. Consumer code combines each `mm` offset with a SoC base segment, typically through macros such as `SR()`, `SRI()`, `SRII()`, `DCCG_SRII()`, and `REG_OFFSET()`, to populate per-block register tables. Runtime display code then reads or writes the resulting absolute register addresses through AMDGPU register helpers. This file does not define behavior by itself; it is a hardware ABI map between DCN 2.1 register names and numeric offsets.

## Important Definitions

Every hardware register in this chunk is represented as a pair:

- `#define mmREGISTER_NAME 0xNNNN` gives the register offset within the block's selected MMIO aperture.
- `#define mmREGISTER_NAME_BASE_IDX N` selects the generated base segment, later expanded through `DMU_BASE__INST0_SEG<N>` in DCN resource code or equivalent DMUB helpers.

The main block families in this range are:

- VGA and VGA indexed register windows: `mmVGA_MEM_WRITE_PAGE_ADDR`, `mmVGA_MEM_READ_PAGE_ADDR`, indexed CRTC/SEQ/DAC/GRPH aliases, `mmVGA_RENDER_CONTROL`, `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`, `mmVGA_STATUS`, interrupt/status clear, cache/security, and source-select registers.
- DCCG display clock generation: PHY PLL pixel-clock resync controls, DP DTO phase/modulo, DPPCLK and DSCCLK DTO parameters, DISPCLK frequency change, time-base dividers, clock-gating control, audio DTOs, SYMCLK enables, VSYNC latch/counter controls, soft reset, and `mmDENTIST_DISPCLK_CNTL`.
- DC performance monitor blocks: `DC_PERFMON0` through `DC_PERFMON7` register groups appear across DCCG, DMU, writeback, MMHUBBUB, HDA, DCHUBBUB, and HUBP regions. Each group exposes counter control, state, current value, high, and low registers.
- DMU/DMCU/interrupt infrastructure: RBBMIF timeout/status registers, display power-gating domain config/status registers, DMU misc clock and memory power controls, DMCU firmware RAM/control/interrupt/mailbox registers, GPU timer registers, display interrupt status continuations, and interrupt-destination registers for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, HPD, AUX, AZ, and DSC.
- Writeback path: `WB_ENABLE`, CNV window/source/test/debug registers, writeback scaler coefficient/tap/filter/clamp/status registers, and MCIF writeback buffer manager, address, watermark, QoS, security, and self-refresh controls for `MCIF_WB0` and `MCIF_WB1`.
- Audio/HDA/Azalia: stream index/data registers for streams 0-15, endpoint index/data registers, input endpoint index/data registers, controller clock/DMA/RIRB/CORB/payload/CRC/memory power registers, and root codec parameter/control registers.
- DCHUBBUB and VM request path: SDPIF config, physical VM request and framebuffer/AGP/HBM location registers, ret-path DCC/CRC/memory power registers, arbitration watermarks A-D, DRAM clock/self-refresh controls, global timer, timeout/debug/status, host VM controls, VM context 0-15 page-table base/start/end registers, default address, fault control/status, and fault address registers.
- HUBP/HUBPREQ/HUBPRET/cursor for instances 0 and 1: surface configuration, tiling, viewports, request-size and control registers, surface pitch/address/meta-address pairs, flip and in-use registers, TTU/QoS/deadline/prefetch/vblank/nominal/flip parameter registers, VM aperture/L1 TLB controls, read-line controls, cursor position/size/hotspot/surface-address/DMDATA controls, and HUBP perfmon.

The chunk boundary matters: it includes complete HUBP0/HUBPREQ0/HUBPRET0/cursor0 instance definitions, most of HUBP1/HUBPREQ1/HUBPRET1, and only the beginning of `dce_dc_dcbubp1_dispdec_cursor0_dispdec`. Later HUBP1 DMDATA SW registers and subsequent DCN blocks are outside this work item.

## Consumers And Integration Points

Direct include sites for this DCN 2.1 offset header include:

- `display/dc/resource/dcn21/dcn21_resource.c`, which combines these offsets with `renoir_ip_offset.h` base segments and `dcn_2_1_0_sh_mask.h` field masks to build static register tables for DCCG, DMCU, ABM, audio, OPP, timing generators, MPC, HUBP, HUBBUB, DIO, VMID, DSC, DPP, AUX, and stream encoders.
- `display/dmub/src/dmub_dcn21.c`, which uses the same offsets through DMUB register macros to expose DMCUB common/internal registers to the display microcontroller service.
- `display/dc/irq/dcn21/irq_service_dcn21.c`, which needs DCN 2.1 offsets and masks to describe interrupt sources and acknowledge/enable them.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` and `display/dc/gpio/dcn21/hw_translate_dcn21.c`, which translate DCN 2.1 GPIO/AUX/DDC/HPD hardware identities into register-backed objects.

Important downstream register-list macros include `DCCG_COMMON_REG_LIST_DCN_BASE()`, `DCCG_MASK_SH_LIST_DCN2_1()`, `HUBP_REG_LIST_DCN21(id)`, `HUBP_MASK_SH_LIST_DCN21()`, `HUBBUB_REG_LIST_DCN21()`, `HUBBUB_MASK_SH_LIST_DCN21()`, `DMCU_DCN20_REG_LIST()`, `AUD_COMMON_REG_LIST(id)`, and `DCN20_VMID_REG_LIST(id)`. These macros depend on the naming convention in this header: for example `SRI(FLIP_PARAMETERS_3, HUBPREQ, 0)` expands to `mmHUBPREQ0_FLIP_PARAMETERS_3` and `mmHUBPREQ0_FLIP_PARAMETERS_3_BASE_IDX`.

## Control Flow

There is no function-level control flow in this header. The effective control flow is compile-time macro expansion followed by runtime register access:

1. A DCN 2.1 source file includes `renoir_ip_offset.h`, this offset header, and the matching `dcn_2_1_0_sh_mask.h`.
2. Resource macros such as `SR(reg)` or `SRI(reg, block, id)` concatenate tokens to find `mm...` and `mm..._BASE_IDX` definitions from this header.
3. The macro adds the selected MMIO base segment to the register offset and initializes a typed register table field.
4. Block constructors receive those register tables and matching shift/mask tables.
5. Runtime block methods use generic read/modify/write helpers against the precomputed register addresses to program clocks, display surfaces, VM, cursor state, watermarks, interrupts, audio, writeback, and power management.

The correctness contract is therefore mostly structural. Register names, instance suffixes, base indexes, and matching shift/mask names must line up exactly with the token-pasting macros used by the consumer block headers.

## State And Persistence

This file contains no mutable software state and persists nothing. It does, however, define addresses for registers that control persistent hardware-visible state while the GPU is powered:

- Surface state: HUBP/HUBPREQ registers hold framebuffer, chroma, metadata, pitch, viewport, tiling, flip, VMID, and cursor addresses.
- Clock and timing state: DCCG registers hold DPPCLK, DISPCLK, DP DTO, audio DTO, pixel-rate, time-base, and clock-gating configuration.
- Memory and VM state: DCHUBBUB/VMRQ registers describe framebuffer/AGP aperture ranges, VM contexts, page-table address ranges, fault status, and default fault handling.
- Power-management state: DMU, DMCU, DCHUBBUB, HUBP, HUBPREQ, HUBPRET, MMHUBBUB, MCIF_WB, Azalia, and cursor memory power registers coordinate gating, requests, status, and reset behavior.
- Diagnostics state: DC perfmon, CRC, debug index/data, timeout, interrupt-status, GPU timer, read-line, and fault-status registers expose transient hardware state for debugging and validation.

Because these are MMIO offsets, a wrong constant can cause writes to the wrong hardware register rather than a local software failure. The source tree's state is fixed at build time, while the actual hardware state changes only when consumer code uses these offsets.

## Dependencies

The header depends on C preprocessor token concatenation and on generated SoC base definitions from `renoir_ip_offset.h`. It is paired with `dcn_2_1_0_sh_mask.h`, which defines field shifts and masks for many of the same register names. Its constants are interpreted by AMD display core abstractions under `drivers/gpu/drm/amd/display/dc`, DMUB service code under `drivers/gpu/drm/amd/display/dmub`, and AMDGPU low-level register access helpers.

The `BASE_IDX` values seen in this chunk are significant:

- `0` is used for the small VGA memory page address aperture at base `0x48`.
- `1` is used for VGA legacy aliases and early DCCG/display clock registers.
- `2` is used for most DCN display engine blocks in this range, including perfmon, DMU, DMCU, writeback, MMHUBBUB, HDA/Azalia, DCHUBBUB, VMRQ, HUBP, HUBPREQ, HUBPRET, and cursor registers.

The header has no direct dependency on Ceph or distributed filesystem code despite living under this repository's mirrored `sources/distributed-fs/ceph-client` tree. Its functional owner is the vendored Linux AMDGPU display driver.

## Risks And Edge Cases

- Offset/header mismatches are high impact. A typo in either an `mm...` value or `_BASE_IDX` silently redirects runtime MMIO access and can manifest as display bring-up failures, corrupted scanout, bad cursor programming, broken audio, interrupt storms, VM faults, hangs, or power-management instability.
- The consumer macros rely on exact token naming. Renaming a register, changing an instance prefix such as `HUBPREQ0_` or `CURSOR0_1_`, or dropping a matching `_BASE_IDX` breaks compile-time expansion.
- This chunk includes duplicate numeric offsets for legacy indexed VGA aliases such as CRTC/SEQ/DAC/ATTR/GEN registers. That aliasing is intentional; treating duplicate offsets as a generation bug would be misleading.
- The assigned chunk cuts through a logical block. Research or automated validation for HUBP1 cursor support must include later lines of the file before concluding that all cursor/DMDATA registers are present.
- Register-list macros often cover only supported pipes or hardware instances. For DCN 2.1, `dcn21_resource.c` instantiates four HUBPs and four timing generators even though this chunk contains offsets for more global interrupt destinations and many shared blocks. Tests should validate the resource caps, not just the existence of offset constants.
- The DCCG macro set for DCN 2.1 programs OTG pixel-rate fields for instances 0-3, while older DCN2 lists include additional OTG instances. Mixing DCN 2.0 and DCN 2.1 offset/mask/list macros could compile but program unsupported or wrong registers.
- Several register families encode security, VM, and fault controls. Incorrect writes can disable fault reporting or set an invalid aperture, making subsequent GPU faults harder to diagnose.
- Generated headers are easy to review mechanically but hard to validate semantically. The best source of truth is a cross-check against the ASIC register database or known-good upstream Linux header for the same DCN version.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU display code with DCN 2.1 enabled and warnings treated as errors; token-pasting failures in `SR`, `SRI`, `SRII`, `DCCG_SRII`, `REG_OFFSET`, and field-mask macros should surface immediately.
- Compile `dcn21_resource.c`, `dmub_dcn21.c`, `irq_service_dcn21.c`, and the DCN21 GPIO translation/factory files together with this header and `dcn_2_1_0_sh_mask.h`.
- Compare generated register tables for DCCG, HUBBUB, HUBP0/HUBP1, VMID, DMCU, audio, writeback, and perfmon against a known-good DCN 2.1 table or upstream Linux AMDGPU source.
- On Renoir/DCN 2.1 hardware, smoke-test display modeset, page flip, cursor update, blank/unblank, hotplug interrupt, audio over DP/HDMI, suspend/resume, and basic writeback paths.
- Exercise VM/fault instrumentation by enabling display VM paths and checking DCHUBBUB fault-status/debug output after valid and invalid surface-address programming in a controlled test.
- Verify watermark and deadline programming through HUBBUB/HUBPREQ registers under memory clock changes, stutter/self-refresh entry and exit, and multi-plane scanout.
- Run perfmon/debug tests that read `DC_PERFMON*` and debug index/data registers to catch base-index mistakes that may not affect ordinary modesets.
- Run DMUB initialization and mailbox tests on DCN 2.1, because DMUB uses the same offset header for DMCUB common/internal register access.

### subset-b-001651: lines 2688-5235

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 2688-5235

## Scope And Purpose

This chunk is part of a generated AMD DCN 2.1 register offset header. It contains no executable C code, structs, enums, storage, or functions. Its interface is a set of `#define` constants that map symbolic display-engine register names to MMIO register offsets plus matching `_BASE_IDX` segment identifiers.

The path is under a local `ceph-client` source mirror, but this file belongs to the Linux AMDGPU display stack. In this range the content describes DCN display pipeline hardware blocks for HUBP/HUBPREQ/HUBPRET instances 2 and 3, cursor instances 1 through 3, DPP instances 0 through 3, color conversion, scaling, color management, and associated display performance monitors.

The chunk starts at the tail of cursor instance 1 DMDATA software-access registers and ends in the middle of DPP3 color-management degamma RAM A definitions. Adjacent chunks are required for the complete cursor1 and CM3 register sets.

## Important APIs, Types, And Macro Families

There are no callable APIs in this chunk. The public contract is the generated register-address macro naming scheme:

- `mm<REGISTER>` gives the register offset within the base segment selected by the companion `_BASE_IDX` macro.
- `mm<REGISTER>_BASE_IDX` gives the segment index used by DCN register-list macros to add the correct ASIC base address.
- Consumers combine this header with `dcn_2_1_0_sh_mask.h`, where matching field shift and mask macros live.
- Register-list helpers such as `SR`, `SRI`, `SRII`, `SRIR`, `DCCG_SRII`, and `DMUB_SR` concatenate names like `mmHUBP2_DCSURF_SURFACE_CONFIG` and `mmHUBP2_DCSURF_SURFACE_CONFIG_BASE_IDX` into per-block register tables.

The chunk contains 2,412 `#define` lines, representing 1,206 register offsets and 1,206 base-index constants. Every visible base index is `2`, which routes these offsets through the DCN/DMU register base segment used by the DCN21 display code.

Major macro families in this range:

- `HUBP2` and `HUBP3`: hub pipe front-end registers for surface configuration, tiling, primary/secondary viewport dimensions, request sizing, HUBP control, clock control, VM page settings, debug, and DCFCLK/DPPCLK measurement windows.
- `HUBPREQ2` and `HUBPREQ3`: hub request registers for surface pitches, VMID settings, primary/secondary luma/chroma surface and metadata addresses, flip control, in-use and earliest-in-use readbacks, TTU/QoS controls, VM aperture/TLB controls, prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor timing, reference-to-pixel frequency conversion, DRQ limits, and memory power state.
- `HUBPRET2` and `HUBPRET3`: hub return/read-line controls, memory power state, interrupt register, read-line value, and read-line status.
- `CURSOR0_1`, `CURSOR0_2`, and `CURSOR0_3`: cursor surface address, size, position, hot spot, stereo, destination offset, memory power, dynamic metadata address/control/QoS/status, and DMDATA software data registers. Instance 1 is only partially visible at the start of this chunk.
- `DC_PERFMON8` through `DC_PERFMON13`: performance counter control, state, perfmon control, current-value interrupt/misc, and high/low counter readback registers associated with HUBP/DPP perfmon address blocks.
- `DPP_TOP0` through `DPP_TOP3`: DPP control, soft reset, CRC value/control, and host-read control.
- `CNVC_CFG0` through `CNVC_CFG3`: color conversion surface format, format control, floating-point bias/scale by channel, color-keyer controls and values, and alpha 2-bit LUT registers.
- `CNVC_CUR0` through `CNVC_CUR3`: cursor color/conversion controls in the DPP color conversion path.
- `DSCL0` through `DSCL3`: scaler coefficient RAM access, scaler mode/tap/manual replicate controls, horizontal and vertical scale ratios and initial phases for luma/chroma, black offset, update/autocal, overscan, OTG blanking dimensions, recout/MPC size, line-buffer format/memory control, vertical counter, scaler memory power, and output-buffer controls.
- `CM0`, `CM1`, `CM2`, and partial `CM3`: color-management controls including input CSC matrices, gamut remap matrices, bias, degamma LUT programming, RAM A/B curve segment controls, blend gamma LUTs, HDR multiplier coefficient, CM memory power, dealpha, coefficient format, shaper LUTs, 3D LUT controls, output normalization/offset, and debug index/data. CM3 coverage ends before the full CM3 set is complete.

## Control Flow

This header has no runtime control flow. Runtime behavior is produced by AMD display code that includes the generated offset and shift/mask headers and uses register helper macros to build tables or perform MMIO accesses.

Typical flow for DCN21 register access:

1. A hardware object definition names a logical register, often through a macro list such as a HUBP, DPP, scaler, color-management, or perfmon register list.
2. `dcn21_resource.c` expands helper macros such as `SR`, `SRI`, and `SRII` against this header, computing `BASE(mm..._BASE_IDX) + mm...` for each register table entry.
3. Higher-level DC code stores those computed offsets in per-block register structs for HUBP, DPP, DSCL, color management, cursor, IRQ, and related hardware objects.
4. Runtime functions use those register structs with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and paired field masks from `dcn_2_1_0_sh_mask.h`.
5. The final effect is an MMIO read, write, or read-modify-write against DCN21 display hardware.

For HUBP/HUBPREQ, the flow is driven by plane programming and flips: the display core computes surface addresses, tiling, viewport, VMID, prefetch, QoS, and flip parameters, then writes the corresponding pipe instance registers. For DPP/DSCL/CM, the flow is driven by stream and plane color/scaler programming: the driver sets pixel format conversion, scaler ratios and taps, CSC/gamut matrices, gamma/shaper/3D LUTs, and memory power controls. Perfmon registers are used by diagnostic and performance paths to enable, select, and read display block counters.

## State And Persistence Behavior

The macros themselves are compile-time constants and store no state. The state they identify is hardware register state inside the DCN21 display engine.

The represented hardware state includes:

- Plane fetch state: surface addresses and metadata addresses, pitch, tiling, viewport, surface-in-use readbacks, flip controls, flip interrupt state, VMID and VM aperture controls.
- Timing and bandwidth state: TTU/QoS watermarks, prefetch parameters, vblank/flip/nominal timing registers, per-line delivery, destination dimensions, and reference-frequency conversion.
- Cursor state: cursor enable/configuration, memory addresses, position, hot spot, stereo control, memory power, dynamic metadata control/status, and software DMDATA access.
- DPP processing state: top-level enable/reset/CRC state, pixel format conversion, color keying, cursor color conversion, scaler taps/ratios/initial phases, line-buffer/output-buffer state, color-management matrices, LUT programming indices/data, 3D LUT controls, shaper/blend/degamma curve RAMs, and memory power/status.
- Readback and status state: HUBPRET read-line values/status, memory power status registers, scaler vertical counter, debug index/data ports, CRC values, and perfmon high/low counter values.

Some registers are durable configuration until the next modeset, plane update, power transition, or hardware reset. Others are latched status, debug selectors, counter readbacks, memory power state readbacks, interrupt/status registers, or index/data ports with side effects. This offset header does not encode write ordering, side effects, reset values, or read-modify-write rules; those semantics live in hardware documentation and in the consuming driver code.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- `dcn_2_1_0_offset.h` supplies the offsets covered here.
- `dcn_2_1_0_sh_mask.h` supplies matching field masks and shifts.
- `renoir_ip_offset.h` supplies the DCN/DMU base segment definitions used by `BASE(mm..._BASE_IDX)`.
- `reg_helper.h` and DMUB register helpers provide the token-concatenation and MMIO access macros that consume these names.

Direct local integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes this header and expands register-list macros into DCN21 hardware object register tables.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the same generated headers for DMUB common/internal register table construction, though this specific chunk is mostly display-pipe rather than DMUB register coverage.
- `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes the headers for interrupt-source register definitions and maps HUBP flip/vblank/vupdate/DMCUB sources into DAL IRQ sources.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `hw_translate_dcn21.c`, which share the same generated DCN21 register namespace for GPIO/DDC/HPD-related hardware tables.
- DCN20/DCN21 shared hardware modules such as HUBP, DPP, MPC, OPP, DSC, DCCG, VMID, DCE audio, DMCU, DMUB PSR/ABM, and hardware sequencing code that are instantiated from the DCN21 resource file.

## Risks And Maintenance Notes

- This is generated hardware ABI data. A wrong offset or base index can compile cleanly while directing a valid register helper to the wrong MMIO address.
- The repeated instance layout is easy to damage manually. `HUBP2` and `HUBP3`, `DPP_TOP0` through `DPP_TOP3`, `DSCL0` through `DSCL3`, and `CM0` through `CM3` have similar names but different offsets; instance drift can create failures that appear only when a specific pipe is used.
- The chunk boundary is not semantic. It starts after the beginning of cursor instance 1 and ends before the end of CM3, so a whole-file merge must combine adjacent chunk reports before claiming complete cursor1 or CM3 coverage.
- Surface address, metadata address, VMID, VM aperture, and TLB offsets are security- and stability-sensitive because they determine what memory the display engine fetches.
- Flip, in-use, earliest-in-use, and interrupt offsets must stay aligned with IRQ and page-flip code. Incorrect values can cause missed page-flip completion, stale buffers being scanned out, or interrupt storms.
- Scaler, CSC, gamut, gamma, shaper, blend, and 3D LUT registers are packed hardware programming surfaces. Bad offsets can cause visual corruption, wrong color output, HDR/SDR conversion regressions, or LUT writes landing in unrelated registers.
- Index/data style LUT and debug registers require correct sequencing in consumers. This header identifies the ports but does not prevent concurrent or out-of-order access.
- Memory power control/status offsets are power-management sensitive. Wrong register addresses can leave blocks powered down during use or prevent expected power savings.
- Perfmon offsets affect diagnostics and validation. Counter programming bugs may not affect scanout directly but can hide performance, bandwidth, or underflow issues during debugging.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU/DC with DCN21 support enabled; missing or renamed macros should fail in DCN21 resource, IRQ, GPIO, or DMUB compilation units.
- Compare regenerated `dcn_2_1_0_offset.h` output against the committed/generated source and adjacent ASIC families to catch accidental offset or instance drift.
- Exercise DCN21 hardware with at least four active display pipes where possible, so HUBP/DPP/DSCL/CM instances 0 through 3 are all used.
- Run modeset, hotplug, suspend/resume, page-flip, cursor movement, cursor format/size changes, and multi-plane overlay scenarios; watch for page-flip timeouts, stale frames, cursor corruption, or HUBP flip interrupt anomalies.
- Validate high-bandwidth and memory-pressure display modes that stress HUBPREQ prefetch, TTU/QoS, per-line delivery, and VM settings; watch for underflow, blanking artifacts, or bandwidth validation mismatches.
- Check color pipeline behavior with scaling, CSC/gamut remap, degamma/blend gamma, shaper LUT, 3D LUT, HDR, color keying, and alpha use cases; visual output should match expected color-management results.
- Confirm memory power transitions do not break active scanout or LUT/scaler programming and that related status registers report plausible state.
- Use display CRC and perfmon/debug readbacks where available to verify CRC counters and perfmon high/low values move as expected during active scanout.

### subset-b-001652: lines 5236-7883

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 5236-7883

## Scope And Purpose

This chunk is generated AMD DCN 2.1 register-offset metadata. It contains no executable C logic; its interface is a large set of preprocessor constants that map display hardware register names to numeric MMIO offsets and to a segment/base selector via the paired `_BASE_IDX` macros.

The path is under the local `ceph-client` source mirror, but this file belongs to the Linux AMDGPU display stack. In this line range it describes display engine blocks for Renoir/DCN 2.1: the tail of DPP color-management instance 3, the DPP perf monitor for instance 3, MPC/MPCC blending and output color blocks, OPP instances 0-5, DSC remap controls, OPP performance counters, and the beginning of OPTC/ODM input controls. It is not Ceph filesystem code.

The chunk boundaries are not semantic. It starts inside the `CM3` DPP color-management register sequence, at `mmCM3_CM_DGAM_RAMA_END_CNTL2_B`, and ends inside the `ODM3` block at `mmODM3_OPTC_WIDTH_CONTROL`; surrounding chunks are needed for the complete source-file register map.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or variables in this chunk. The public API is the generated macro naming contract:

- `mm<block/register>` gives the DCN 2.1 register offset.
- `mm<block/register>_BASE_IDX` gives the segment index used by register-table constructors to add the correct ASIC base address.
- Repeated instance prefixes such as `CM3`, `MPCC0` through `MPCC7`, `FMT0` through `FMT5`, `DPG0` through `DPG5`, `OPPBUF0` through `OPPBUF5`, `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`, `DSCRM0` through `DSCRM5`, and `ODM0` through `ODM3` distinguish hardware instances that share a common layout.

Important macro families in this range:

- `mmCM3_CM_*`: DPP instance 3 color-management and LUT programming offsets. The visible portion covers degamma RAM A/B tail registers, blend-gamma control/LUT/RAM A/B registers, HDR multiplier, memory power control/status, dealpha, coefficient format, shaper control/LUT/RAM A/B registers, 3D LUT mode/index/data/read-write controls, 3D LUT normalization and output offsets, and test/debug index/data.
- `mmDC_PERFMON15_*`: DPP3 display performance monitor offsets for perf counter control, state, control registers, current value, high/low counter words, and interrupt/misc value.
- `mmMPCC0_MPCC_*` through `mmMPCC7_MPCC_*`: multi-plane composition controller instance offsets for top/bottom source selection, OPP assignment, blend/control state, update-lock selection, top/bottom gains, background color, memory power control, stall status, and busy/idle status.
- `mmMPC_*`, `mmMPC_OUT*_*`, and `mmMPC_OCSC_*`: global MPC controls and output-side color processing. This includes soft reset, update-lock controls, pending/ack/status registers, stall controls, output muxes, denorm and clamp controls, output CSC coefficient sets for outputs 0-3, out CSC coefficient format, OC SC mode/coefficients for outputs 0-5, LUT/PWL RAM controls, and MPC perf monitor event selection.
- `mmMPCC_OGAM*_*`: output gamma programming for MPCC instances 0-7, including per-channel LUT index/data/write masks, RAM A/B start/slope/end/region programming, memory power state, and debug controls.
- `mmABM0_*` plus `mmBL1_PWM_*`: adaptive backlight management and PWM/backlight control offsets, including ABM control, hysteresis, luminance/current/target levels, pixel-count filters, test/debug controls, PWM period/current counter, backlight gain/level, and ramp/ramp-rate controls.
- `mmFMT0_FMT_*` through `mmFMT5_FMT_*`: output formatter offsets for component clamps, dynamic expansion, format control, bit-depth/dither seeds, clamp control, side-by-side stereo, 4:2:0 map memory control, and 4:2:2 control.
- `mmDPG0_DPG_*` through `mmDPG5_DPG_*`: display pattern generator offsets for pattern/ramp control, dimensions, RGB/YCbCr color values, offset segment, and status.
- `mmOPPBUF0_OPPBUF_*` through `mmOPPBUF5_OPPBUF_*`: output pixel processor buffer offsets for active width, pixel repetition, MSO/display segmentation, 3D parameters, and secondary control.
- `mmOPP_PIPE0_OPP_PIPE_CONTROL` through `mmOPP_PIPE5_OPP_PIPE_CONTROL`: OPP pipe controls.
- `mmOPP_PIPE_CRC0_*` through `mmOPP_PIPE_CRC5_*`: OPP pipe CRC control, mask, and result registers.
- `mmOPP_TOP_CLK_CONTROL`: shared OPP top-level clock control.
- `mmDSCRM0_DSCRM_DSC_FORWARD_CONFIG` through `mmDSCRM5_DSCRM_DSC_FORWARD_CONFIG`: DSC remapper/forwarding configuration for OPP/DSC routing.
- `mmDC_PERFMON16_*`: OPP-side display performance monitor offsets.
- `mmODM0_OPTC_*` through the visible start of `mmODM3_OPTC_*`: OPTC/ODM input controls for global control, data source selection, data format, bytes per pixel, segment width, input clock, memory configuration, and spare registers.

## Control Flow

This header has no runtime control flow. It is declarative hardware metadata. Runtime behavior appears when DCN 2.1 display code builds register tables from these macros and later uses those tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, and related helpers.

Representative integration flows in this tree:

- `display/dc/resource/dcn21/dcn21_resource.c` includes `dcn_2_1_0_offset.h`, defines `BASE(mm..._BASE_IDX) + mm...` expansion helpers such as `SR`, `SRI`, `SRII`, and `SRIR`, and instantiates arrays for DPP, OPP, MPC, OPTC, audio, hub, clock, and other DCN 2.1 blocks. This chunk feeds those table initializers for DPP color-management instance 3, OPP instances 0-5, MPCC/MPC, and ODM/OPTC offsets.
- `display/dmub/src/dmub_dcn21.c` includes this offset header for the DMUB service register table; the DMUB-facing file uses generated offset and mask headers to produce common register descriptors.
- `display/dc/dpp/dcn20/dcn20_dpp.h` defines `TF_REG_LIST_DCN20*` macros that reference `CM_BLNDGAM_*`, `CM_SHAPER_*`, and `CM_3DLUT_*` through `SRI(..., CM, id)`. For `id == 3`, the `CM3` macros in this chunk resolve those DPP color-management register addresses.
- `display/dc/mpc/dcn10/dcn10_mpc.h` and the DCN20 MPC implementation consume the `MPCC*` and `MPC*` register families through indexed register arrays. Runtime MPC code reads and writes `MPCC_TOP_SEL`, `MPCC_BOT_SEL`, `MPCC_OPP_ID`, status, and blend-related fields to build and tear down plane-composition trees.
- `display/dc/opp/dcn20/dcn20_opp.h` extends the DCN10 OPP register list with DPG registers. `dcn21_resource.c` instantiates `OPP_REG_LIST_DCN20(id)` for OPP instances 0-5, which maps to the `FMT`, `DPG`, `OPPBUF`, `OPP_PIPE`, and `OPP_PIPE_CRC` offsets in this chunk.
- OPTC headers such as `display/dc/optc/dcn10/dcn10_optc.h` use `SRI(OPTC_INPUT_GLOBAL_CONTROL, ODM, inst)` and related ODM macros. Runtime OPTC code reads underflow state, clears underflow, configures ODM data source selection, and manages segment/memory programming using these offsets.

Because the file only provides constants, sequencing rules are enforced by the consumers and by hardware. This header does not know when it is safe to program a LUT bank, change MPCC topology, clear underflow, read CRC results, or power-gate memories.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. The represented state is MMIO-backed DCN display hardware state. Values programmed through these offsets persist in the hardware block until a later register write, modeset/reprogramming sequence, power transition, reset, or firmware/hardware action changes them.

The state represented in this chunk includes:

- DPP/CM state for instance 3: degamma, blend-gamma, shaper, and 3D LUT selection/data/RAM segments; color coefficients; HDR multiplier; memory power controls; and debug/test selectors.
- MPC/MPCC state: composition topology, selected top/bottom inputs, OPP assignment, per-plane blending/gain/background colors, update-lock affiliation, stall/status bits, output muxes, output CSC/OCSC coefficients, PWL/OGAM LUT contents, and MPC memory/perf controls.
- ABM/backlight state: ABM algorithm thresholds and levels, PWM period and current count, backlight level/gain, ramping, and test/debug state.
- OPP/output state: formatter clamps, bit depth, dither seeds, 4:2:0/4:2:2 formatting, test pattern generator dimensions/colors/status, OPP buffer segmentation and 3D timing parameters, OPP pipe controls, pipe CRC configuration/results, DSC forwarding, and OPP perf counters.
- ODM/OPTC input state: source selection for output data, input data format, bytes per pixel, ODM segment width, input clock gating/control, memory selection/configuration, spare register contents, and underflow-related global-control fields defined by the paired shift/mask header.

Some registers are configuration state, some are data windows for LUT RAMs, and some are status or side-effect controls. Names such as `*_LUT_INDEX`, `*_LUT_DATA`, `*_READ_WRITE_CONTROL`, `*_MEM_PWR_CTRL`, `*_MEM_PWR_STATUS`, `*_STATUS`, `*_STALL_STATUS`, `*_CRC_RESULT*`, `*_PERFCOUNTER_STATE`, and `OPTC_INPUT_GLOBAL_CONTROL` signal different access semantics that must be respected by callers.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- The paired `dcn_2_1_0_sh_mask.h` header supplies field masks and shifts for these register offsets.
- `renoir_ip_offset.h` supplies the IP base/segment arrays used by `BASE(mm..._BASE_IDX)`.
- DC register helpers in `reg_helper.h` and `dm_services.h` consume the final addresses through `REG_*` macros and low-level MMIO accessors.
- Resource constructors in `display/dc/resource/dcn21/dcn21_resource.c` map the generated offsets into typed register structs for DPP, OPP, MPC, OPTC, ABM, audio, DCCG, and other hardware objects.
- Runtime block implementations in `display/dc/dpp`, `display/dc/mpc`, `display/dc/opp`, and `display/dc/optc` use those register structs to implement color programming, plane composition, output formatting, CRC capture, ODM combine/bypass, underflow handling, and debug/performance flows.
- DMUB service setup in `display/dmub/src/dmub_dcn21.c` also includes the offset/mask pair for DCN 2.1 register descriptors.

The numeric offsets are a hardware ABI for DCN 2.1. They must remain synchronized with AMD's generated register database, the matching shift/mask file, and the block register-list macros that assume specific register names exist.

## Risks And Edge Cases

- Incorrect offsets or `_BASE_IDX` values compile cleanly but can send MMIO reads/writes to the wrong register, wrong instance, or wrong segment. Failures can appear as color corruption, broken gamma/LUT programming, bad plane composition, missing output, CRC mismatch, underflow, hangs during modeset, or power-management regressions.
- The chunk starts and ends inside larger repeated blocks. A review of only this chunk cannot prove full `CM3` or `ODM3` coverage; adjacent chunk results must be reconciled before final per-file conclusions.
- Repeated instance families are vulnerable to copy/paste drift. `MPCC0` through `MPCC7`, `OGAM0` through `OGAM7`, and OPP instance 0-5 blocks should keep consistent per-instance spacing and naming; a single bad instance may only fail on high pipe counts, multi-plane compositions, or specific outputs.
- LUT and RAM window registers have ordering and bank-selection requirements outside this header. Programming `*_LUT_INDEX`, `*_LUT_DATA`, write-enable masks, RAM A/B regions, or 3D LUT controls in the wrong order can corrupt visible color state even if the offsets are correct.
- Status and side-effect registers require careful access. `*_STATUS`, `*_STALL_STATUS`, `*_CRC_RESULT*`, performance counter state/value registers, underflow clear/status bits, and memory power status/control registers may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive according to hardware semantics not encoded here.
- MPC/MPCC topology registers affect live plane blending. Changing `MPCC_TOP_SEL`, `MPCC_BOT_SEL`, `MPCC_OPP_ID`, update-lock selection, or output mux registers outside the intended hardware sequence can produce transient blanking, underflow, or composition glitches.
- ODM/OPTC controls are tied to stream splitting and high-bandwidth modes. Incorrect ODM data source, width, bytes-per-pixel, clock, or memory configuration may only surface on high-resolution, high-refresh, DSC, or ODM-combined modes.
- OPP formatter, OPPBUF, DPG, and pipe CRC registers have standards-visible output effects. Mistakes can affect bit depth, dithering, chroma format, stereo layout, MSO segmentation, blank/test patterns, and debug CRC validation.

## Test Signals

Useful validation combines build checks, generated-header consistency checks, and DCN 2.1 hardware behavior:

- Build AMDGPU with DC/DCN 2.1 support enabled. Missing or renamed macros should fail in `dcn21_resource.c`, DCN20 DPP/OPP/MPC/OPTC headers, DMUB DCN21 setup, or block implementation files.
- Diff this chunk against a regenerated DCN 2.1 offset header and against neighboring ASIC families to catch unintended offset/base-index drift, especially in repeated MPCC, OGAM, OPP, and ODM families.
- Boot and modeset on Renoir/DCN 2.1 hardware with one and multiple displays. Watch for blank screens, underflow logs, color corruption, failed hotplug, and suspend/resume regressions.
- Exercise DPP color paths: degamma, blend gamma, shaper LUT, 3D LUT, HDR multiplier, color transforms, and memory power transitions where supported by the driver and test stack.
- Exercise MPC/MPCC composition: single plane, multi-plane overlay, alpha blending, plane add/remove, pipe split, high pipe-count use, and transitions that rebuild MPCC trees.
- Exercise OPP/output paths: output bit-depth changes, dithering, RGB/YCbCr and 4:2:0/4:2:2 formats, test pattern generation, OPP pipe CRC capture, DSC forwarding, and MSO/segmentation where available.
- Exercise ODM/OPTC modes: high pixel-clock modes that require ODM combine/bypass transitions, DSC-enabled modes, and underflow clear/status handling.
- Check debugfs or driver diagnostics for pipe CRC stability, perf counter sanity, no unexpected underflow/stall status, correct LUT programming, and no MMIO access faults.

### subset-b-001653: lines 7884-10415

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 7884-10415

## Scope And Purpose

This chunk is generated AMD DCN 2.1 display register-offset metadata. It contains no executable C logic; its public surface is a sequence of `#define` constants that name MMIO registers and their corresponding base-index segments for the Renoir/DCN21 display engine.

The file lives under a `ceph-client` source mirror, but this range is entirely AMDGPU Display Core hardware metadata. The macros are consumed by DCN21 resource, GPIO, interrupt, link/stream encoder, AUX/DDC, and DMUB register-table code through generated register-list macros and register helper APIs.

The range starts at the tail of `dce_dc_optc_odm3_dispdec`, covers complete `ODM4` and `ODM5` input blocks, all six `OTG0` through `OTG5` timing-generator blocks, OPTC misc/performance-monitor blocks, DIO I2C/misc/HPD/AUX blocks, complete `DIG0`/`DP0` and `DIG1`/`DP1` blocks, and ends part-way through the `DIG2` block at `mmDIG2_AFMT_GENERIC_6`. The next chunk is needed for complete `DIG2` coverage.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or persistent software objects in this chunk. The interface is the generated AMD register-offset naming contract:

- `mm<register_name>` gives the register offset used by register-list initialization.
- `mm<register_name>_BASE_IDX` gives the segment selector used by `BASE(...)`, `REG_OFFSET(...)`, `SRI(...)`, `SRII(...)`, `REGI(...)`, and similar register-table macros.
- All visible `_BASE_IDX` values in this chunk are `2`, meaning these offsets resolve through the DCN/DC display base segment selected by the including code.

The chunk contains 1,210 register offset symbols and 1,210 matching `_BASE_IDX` symbols. Major macro families are:

- ODM/OPTC input macros: the tail of `mmODM3_OPTC_*`, complete `mmODM4_OPTC_*`, and complete `mmODM5_OPTC_*` input controls for data source selection, format, bytes-per-pixel, width, input clock, memory config, and spare registers.
- OTG macros: complete `mmOTG0_` through `mmOTG5_` timing generator register sets. Each instance has 105 registers covering horizontal/vertical totals, blanking, sync, trigger controls, status/readback, counters, stereo/interlace, snapshots, interrupts, update locks, blank/black colors, CRC windows/data, static-screen detection, 3D structure, global sync lock, vstartup/vupdate/vready, DRR, request control, DSC start position, pipe update status, and spare registers.
- OPTC misc macros: `mmDWB_SOURCE_SELECT`, `mmGSL_SOURCE_SELECT`, `mmOPTC_CLOCK_CONTROL`, `mmODM_MEM_PWR_CTRL*`, `mmODM_MEM_PWR_STATUS`, and `mmOPTC_MISC_SPARE_REGISTER`.
- Display performance monitor macros: `mmDC_PERFMON17_*` for OPTC and `mmDC_PERFMON18_*` for DIO, including counter control/state, perfmon control, interrupt/misc value, and high/low counter readback registers.
- DIO I2C/DDC macros: `mmDC_I2C_*` controls for arbitration, interrupts, software status, DDC1-DDC5 hardware status, per-DDC speed/setup, transaction slots, data, EDID-detect control, and read-request interrupt.
- DIO misc macros: `mmDIO_SCRATCH*`, `mmDCE_VCE_CONTROL`, DIO memory power status/control, DIO clock control, DIO power management, `mmDIG_SOFT_RESET`, HDMI RX status timer, PSP interrupt status/clear, and generic interrupt message/clear registers.
- HPD macros: `mmHPD0_` through `mmHPD4_` hotplug-detect status/control, interrupt control, fast-train control, and toggle-filter control.
- AUX macros: `mmDP_AUX0_` through `mmDP_AUX4_` AUX channel control, software control/status/data, arbitration, interrupt control, LS status/data, AUX DPHY TX/RX control/status, GTC sync control/status, error control, controller status, and PHY wake control.
- DIG stream-encoder macros: complete `mmDIG0_` and `mmDIG1_` register families, plus the first 43 `mmDIG2_` entries. These cover DIG front-end controls, output CRC, test/random patterns, FIFO status, HDMI metadata/generic packets, HDMI control/status, audio/ACR/VBI/infoframe packets, AFMT audio metadata and status, IEC 60958, audio CRC/ramp controls, DIG back-end controls, TMDS control/pattern registers, version/lane enable, AFMT control, and forced DIG disable. `DIG2` is incomplete in this chunk.
- DP link macros: complete `mmDP0_` and `mmDP1_` DisplayPort link families. They cover link control, pixel format, MSA colorimetry/timing parameters, video stream controls, link frame and secondary data control, DPHY control/status/test/training/scrambling/CRC, audio M/N and timestamp, Multi-Stream Transport MSE rate/SAT/link-timing/status controls, DSC control, metadata transmission, DSC bytes-per-pixel, and ALPM control.

Address-block inventory in this chunk:

- Partial previous block: tail of `dce_dc_optc_odm3_dispdec`, 3 visible registers.
- `dce_dc_optc_odm4_dispdec`, base `0x100`, 8 registers.
- `dce_dc_optc_odm5_dispdec`, base `0x140`, 8 registers.
- `dce_dc_optc_otg0_dispdec` through `dce_dc_optc_otg5_dispdec`, bases `0x0`, `0x200`, `0x400`, `0x600`, `0x800`, and `0xa00`, 105 registers each.
- `dce_dc_optc_optc_misc_dispdec`, base `0x0`, 8 registers.
- `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec`, base `0x79a8`, 9 registers.
- `dce_dc_dio_dout_i2c_dispdec`, base `0x0`, 26 registers.
- `dce_dc_dio_dio_misc_dispdec`, base `0x0`, 24 registers.
- `dce_dc_dio_hpd0_dispdec` through `dce_dc_dio_hpd4_dispdec`, bases `0x0`, `0x20`, `0x40`, `0x60`, and `0x80`, 5 registers each.
- `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec`, base `0x7d10`, 9 registers.
- `dce_dc_dio_dp_aux0_dispdec` through `dce_dc_dio_dp_aux4_dispdec`, bases `0x0`, `0x70`, `0xe0`, `0x150`, and `0x1c0`, 19 registers each.
- `dce_dc_dio_dig0_dispdec`, base `0x0`, 88 registers.
- `dce_dc_dio_dp0_dispdec`, base `0x0`, 73 registers.
- `dce_dc_dio_dig1_dispdec`, base `0x400`, 88 registers.
- `dce_dc_dio_dp1_dispdec`, base `0x400`, 73 registers.
- `dce_dc_dio_dig2_dispdec`, base `0x800`, 43 visible registers in this chunk, continuing later.

## Control Flow

This header has no runtime control flow. It is declarative hardware metadata. Control flow appears in consumers that include this offset header together with `dcn_2_1_0_sh_mask.h` and then build register tables or issue MMIO accesses.

Representative flow:

- DCN21 code includes `dcn/dcn_2_1_0_offset.h`, `dcn/dcn_2_1_0_sh_mask.h`, and `renoir_ip_offset.h`.
- Register-list macros such as `SR`, `SRI`, `SRII`, `REG`, and `REGI` concatenate block and register names into `mm...` and `mm..._BASE_IDX` symbols from this header.
- The `BASE(mm..._BASE_IDX) + mm...` expression produces the final register address stored in per-block register tables.
- Runtime display objects then use helper APIs such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, `REG_SET`, and field-specific variants with the generated address tables and masks.

Important control-flow users:

- `display/dc/resource/dcn21/dcn21_resource.c` uses this header to construct DCN21 resource register tables. The macros in this chunk feed timing-generator, OPTC, DIO, AUX/DDC, DIG, DP, and other display object register addresses used during resource creation and modeset programming.
- `display/dc/irq/dcn21/irq_service_dcn21.c` includes this header for DCN21 interrupt service setup. The OTG vertical interrupt and HPD-related register families in this chunk are part of the hardware surface used by vblank, vline, vupdate, page-flip, HPD, and HPDRX interrupt handling.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` includes this header and builds HPD and DDC GPIO register tables. The `mmHPD*_DC_HPD_*` and `mmDC_I2C_*` families are the relevant chunk content.
- `display/dc/gpio/dcn21/hw_translate_dcn21.c` uses the same generation-specific register definitions to map logical GPIO/DDC/HPD objects to hardware instances.
- `display/dmub/src/dmub_dcn21.c` includes this header for DMUB service register construction. Although this chunk is mostly display pipe/DIO metadata, it shares the same generated base-address contract used by DMUB register helpers.

The generated header does not encode sequencing rules. Consumers must still program hardware in the order required by Display Core: pipe setup, timing lock/update, link encoder setup, AUX/DDC transactions, HPD interrupt enablement, DP link training, HDMI/DP packet programming, audio infoframe programming, CRC/test setup, and power-management transitions.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. The macros point at hardware registers whose values live in the DCN21 display engine and may be reset, retained, latched, or self-cleared according to hardware semantics outside this file.

The represented state includes:

- ODM/OPTC input state: data source selection, pixel format, bytes per pixel, input width, clock control, and memory configuration for output data merger paths.
- OTG timing state: horizontal and vertical totals, blanking windows, sync positions, DRR total limits, vstartup/vupdate/vready timing, global sync lock state, master/update locks, and request/update state for each of six timing generators.
- OTG status and diagnostics: frame/HV/VF counters, snapshot position/frame, interlace/stereo status, CRC windows and readback data, range timing interrupt status, global sync status, pipe update status, and pixel readback.
- DIO physical/logical state: DIO scratch registers, clock and memory power control/status, soft reset, power management, PSP/generic interrupt state, and HDMI RX status timer configuration.
- Connector detection state: HPD interrupt status/control and toggle filtering for five HPD instances.
- AUX/DDC transaction state: DDC arbitration/status/speed/setup/transaction/data registers and AUX request/status/data/interrupt/DPHY/GTC/PHY-wake registers for five AUX channels.
- DIG/HDMI/AFMT state: stream source selection, HDMI packet controls, audio packet/ACR/infoframe metadata, generic packets, AFMT status, IEC 60958 channel status, audio CRC/ramp controls, TMDS controls, lane enablement, and forced-disable state.
- DP link state: link control, video stream control, MSA timing/colorimetry, DPHY training/test/scrambling/CRC/FEC-related state, secondary packet/audio timing, MST MSE rate and slot allocation state, DSC control, metadata transmission, and ALPM control.
- Performance monitoring state: DC perfmon counters and interrupt/misc value registers for OPTC and DIO performance counter blocks.

Register persistence must be interpreted by the owning hardware block. Configuration registers generally persist until modeset, stream disable, power-gate/reset, suspend/resume, or driver reprogramming. Status, interrupt, clear, force, snapshot, test, CRC, and counter registers can have side effects on read or write. Names such as `*_INT_STATUS`, `*_INTERRUPT_CONTROL`, `*_CLEAR`, `*_MANUAL_TRIG`, `*_COUNT_RESET`, `*_SNAPSHOT_CONTROL`, `*_CRC_*`, `*_TEST_PATTERN`, `*_FAST_TRAINING`, `*_PHY_WAKE_CNTL`, and `*_FORCE_DIG_DISABLE` are signals that consumer code must observe register-specific semantics from the hardware documentation and existing driver patterns.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header convention:

- `dcn_2_1_0_offset.h` supplies the offsets and base-index symbols documented here.
- `dcn_2_1_0_sh_mask.h` supplies the matching field shift/mask symbols for packed register fields.
- `renoir_ip_offset.h` supplies the generation-specific base segment macros used by `BASE(...)` in DCN21 consumers.
- `reg_helper.h` and DC register helper macros provide the compile-time concatenation and runtime MMIO helpers that consume these symbols.

Primary integration points in the local source tree:

- DCN21 resource construction in `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`.
- DCN21 interrupt mapping/service logic in `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`.
- DCN21 GPIO/HPD/DDC factories and translation in `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`.
- DMUB DCN21 register service setup in `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`.
- Shared display object implementations under `display/dc/dio`, `display/dc/dce`, `display/dc/optc`, `display/dc/gpio`, and `display/dc/resource` that consume generation-specific register tables initialized from these macros.
- Higher-level DRM/DC flows for modeset, vblank/vline/vupdate interrupts, page flips, hotplug, EDID/AUX transactions, DP link training, HDMI/DP infoframes, audio packet programming, MST slot allocation, DSC, ALPM, CRC capture, and suspend/resume.

The offset values in this chunk closely mirror other DCN generations for some blocks, but they are still generation-specific ABI. For example, `mmOTG0_OTG_H_TOTAL`, `mmDIG0_DIG_FE_CNTL`, and `mmDP0_DP_DPHY_CNTL` appear across several DCN/DCE headers with compatible names but not always identical offsets. DCN21 consumers should remain bounded to `dcn_2_1_0_*` headers unless intentionally porting or comparing ASIC generations.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong offset or base index can compile cleanly while directing register access to the wrong MMIO address, causing display modeset failures, blank screens, bad timings, broken hotplug, AUX/DDC failures, bad link training, HDMI/DP packet errors, lost audio, or hard-to-debug interrupt behavior.
- The chunk has non-semantic boundaries. It starts in the middle of `ODM3` and ends mid-`DIG2`; whole-file conclusions about those two blocks require adjacent chunk reconciliation.
- Repeated block instances are easy to drift manually. OTG0-5 each have the same 105-register shape with different offsets; HPD0-4, AUX0-4, DIG0-2, and DP0-1 follow similar repeated patterns. A one-instance typo can produce failures only on specific pipes or connectors.
- Base-index correctness matters as much as the numeric offset. The register-list macros add `BASE(mm..._BASE_IDX)` to `mm...`; an incorrect `_BASE_IDX` can target a wrong register segment even when the offset number looks plausible.
- Timing-generator registers are sensitive to programming order. Incorrect use of `OTG_UPDATE_LOCK`, `OTG_MASTER_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, vstartup/vupdate/vready registers, DRR limits, or global sync controls can cause tearing, hangs waiting for vblank/update, bad variable refresh behavior, or multi-display sync failures.
- Interrupt/status/clear registers may be sticky, write-one-to-clear, or latch-on-read depending on the register. HPD, OTG vertical/range timing, DIO PSP/generic, AUX, I2C, AFMT, and perfmon interrupt families need the surrounding driver helper behavior to avoid lost or storming interrupts.
- AUX and DDC offsets affect EDID, link training, DSC capability discovery, HDCP/DPCD transactions, and sink management. Subtle register drift can look like monitor-specific failures rather than a compile-time error.
- DIG and DP blocks mix HDMI, DP, audio, TMDS, MST, DSC, ALPM, CRC, and test controls. Misaddressed packet or link registers can regress only one transport mode, audio format, MST topology, DSC mode, or power-saving state.
- Power and reset registers in `DIO_*`, `ODM_MEM_PWR_*`, `DIG_SOFT_RESET`, and `FORCE_DIG_DISABLE` can disrupt active display paths if written at the wrong time or with the wrong instance.
- Performance counter registers are diagnostic but can still perturb measurement or interrupt behavior if counter control/state registers are misprogrammed.

## Test Signals

Useful validation is a mix of compile-time generation checks and hardware behavior:

- Build AMDGPU/DC with DCN21/Renoir support enabled. Missing or renamed macros should fail in DCN21 resource, GPIO, IRQ, DMUB, and shared display object register table initialization.
- Diff this generated chunk against the expected upstream/generated `dcn_2_1_0_offset.h` and against nearby DCN generation headers to catch unintended offset or `_BASE_IDX` drift, especially in repeated OTG, AUX, HPD, DIG, and DP instances.
- Exercise modesets on DCN21 hardware across all available pipes/connectors: single display, multi-display, clone/extend, rotation/scaling, interlace if supported, suspend/resume, runtime power transitions, and repeated enable/disable cycles.
- Validate vblank, vline, vupdate, page-flip, and range-timing interrupt behavior. Watch for missed interrupts, interrupt storms, stuck flips, delayed page flips, or timeouts waiting for vblank/update locks.
- Validate HPD and HPDRX behavior by hotplugging all physical connectors, including rapid plug/unplug and DP short/long pulse cases. Check that connector status changes, IRQ logs, and userspace DRM events remain correct.
- Validate DDC/AUX paths with EDID reads, DPCD reads/writes, DP link training at multiple link rates/lane counts, MST topology discovery, DSC capability discovery, and AUX wake behavior.
- Validate HDMI and DP stream-encoder behavior: link comes up, correct pixel format/colorimetry/timing, infoframes are correct, audio packets/ACR are stable, CRC capture works when enabled, and test-pattern paths do not affect normal mode.
- Validate MST, DSC, ALPM, FEC/training-related paths where supported by the ASIC and sink, because the `DP0`/`DP1` macro families include MSE, DSC, secondary-data, and ALPM offsets.
- Use debugfs or driver diagnostics to compare OTG counters, CRC readbacks, AUX transaction status, HPD status, and perfmon values with expected behavior during modeset, hotplug, and link-training scenarios.
- For the incomplete `DIG2` range, ensure merge-lane review includes the continuation chunk before judging full third-DIG support.

### subset-b-001654: lines 10416-13053

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 10416-13053

## Scope And Purpose

This chunk is a generated AMD DCN 2.1 register-offset header slice. It contains no executable C logic; its interface is a large set of preprocessor constants that map display, audio, compression, firmware, writeback, GPIO, legacy VGA, and Azalia/HDA register names to numeric offsets and base-index selectors.

The range contains 2,389 `#define` entries and 63 `addressBlock` comments. It starts in the middle of the `DIG2` display encoder block, then covers the full `DP2`, `DIG3`/`DP3`, and `DIG4`/`DP4` MMIO register families. The middle of the chunk defines DCIO shared registers, DCIO chip-level GPIO/DDC/HPD/AUX/power-sequencer registers, six DSC compressor instances, DMU/DMCUB firmware registers, MCIF writeback instance 2 registers, and DCHVM host-VM control registers. The tail defines indirect legacy VGA index spaces and Azalia audio codec, descriptor, sink-info, CRC, input-endpoint, root/function, and stream-latency offsets.

Although the repository path is under `ceph-client`, this file is AMDGPU display hardware metadata for the Linux kernel DRM driver. It has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, classes, or runtime variables in this chunk. The public API is the generated macro namespace:

- `mmDIG2_*`, `mmDIG3_*`, and `mmDIG4_*` name DIG display encoder registers. The visible `DIG2` lines are a continuation from the previous chunk and include AFMT generic/audio/CRC/ramp/status controls, HDMI ACR/status controls, backend enable controls, TMDS controls, version/lane-enable, and force-disable registers. `DIG3` and `DIG4` repeat the fuller encoder surface for HDMI packet generation, AFMT audio/infoframes, audio CRC/ramp/status, TMDS signaling, output CRC/test patterns, FIFO status, backend controls, lane enable, and force-disable.
- `mmDP2_*`, `mmDP3_*`, and `mmDP4_*` name DisplayPort link/stream registers. They cover link control, pixel format, MSA colorimetry/timing/VBID fields, stream control, DPHY training/8b10b/scrambling/CRC/fast-training/test patterns, secondary-data/audio M/N/timestamp/packet controls, MST/MSE rate and slot allocation tables, MSO, DSC transport controls, Display Stream Metadata, Dynamic Backlight (`DP_DB_CNTL`), and ALPM.
- `mmDC_*`, `mmUNIPHY*`, `mmLVTMA_*`, `mmBL_PWM_*`, `mmDCIO_*`, `mmPHY_AUX_CNTL`, `mmAUXI2C_*`, and `mmDC_GPIO_*` define shared DCIO and chip-level GPIO surfaces. These include reference clock control, PHY link and channel crossbar controls, write-command delay, pinstraps, panel power sequencing, backlight PWM, genlock/swaplock pads, soft reset, DDC GPIO groups, HPD, generic GPIO, power-sequencer GPIO, AUX pad controls, pullups, RX enable, and pad strength.
- `mmDSC_TOP<N>_*`, `mmDSCCIF<N>_*`, `mmDSCC<N>_*`, and `mmDSC<N>_DC_PERFMON_*` define six DSC instances. Each compressor instance has top/debug control, DSC CIF configuration, DSCC configuration/status/interrupt, PPS configuration words, picture/slice geometry, bits-per-pixel and rate-control parameters, chunk/slice byte counts, RC range parameters, debug/status, clock-gating, memory power, FEC-ready shadow, and a local perfmon block.
- `mmDMCUB_*` defines the DMU/DMCUB firmware interface: instruction/data/region/cache windows, inbox/outbox base/size/read/write pointers, timer triggers/current value, scratch registers, control/reset/enable, GPINT data in/out, interrupt enable/ack/status, memory power, processor ID, and undefined-address fault reporting.
- `mmMCIF_WB2_*` defines MCIF writeback instance 2 registers for buffer-manager control/status, pitch, four Y/C buffer address pairs with high/offset words, buffer sizes/resolutions, arbitration, SCLK and NB P-state watermarks, QoS, warm-up, self-refresh, clock gating, and debug index/data.
- `mmDCHVM_*` defines display host-VM and RIOMMU control/status registers. Unlike most MMIO entries in this range, these use base index `3`.
- `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` define legacy VGA sequencer, CRT controller, graphics controller, and attribute-controller indirect indexes.
- `ixAZALIA_*`, `ixAUDIO_DESCRIPTOR*`, `ixSINK_DESCRIPTION*`, and `ixAZF0STREAM*` define indirect HDA/Azalia audio register indexes for function group 2 endpoints, descriptor and sink-info tables, input/output CRC result channels, input endpoints, codec root/function controls, and stream FIFO/latency counters.

For `mm...` macros, each register has a companion `*_BASE_IDX` macro. Most display/DCIO/DMCUB/DSC/writeback entries in this chunk use base index `2`; the DCHVM block uses base index `3`. For `ix...` macros, the constants are indirect indexes and do not have `*_BASE_IDX` companions.

## Control Flow

This header has no local runtime control flow. Every line is declarative metadata consumed by AMDGPU display code through register-access macros and generated register tables.

The implied consumer flow for `mm...` entries is:

1. Select a DCN 2.1 register block or hardware instance, such as DIG3, DP4, DSC2, DMCUB, or MCIF_WB2.
2. Pass the symbolic register name to a helper such as `REG_OFFSET`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, or generated constructor macros.
3. Use the paired `*_BASE_IDX` to select the correct MMIO base segment.
4. Use the companion `dcn_2_1_0_sh_mask.h` definitions to encode or decode fields inside the register value.

The implied consumer flow for `ix...` entries is indirect: select the relevant VGA or Azalia index/data aperture, write or address the index value, then read or write the data register using the hardware-specific path. This chunk does not define the index/data mechanism or field semantics.

Programming order is external to this file. For example, DP link training, HDMI audio clock regeneration, DSC PPS setup, DMCUB boot/inbox setup, MCIF writeback buffer rotation, HPD/DDC GPIO handling, and Azalia stream routing all have sequencing rules enforced by higher-level driver code and hardware documentation, not by this offset header.

## State And Persistence Behavior

The macros themselves are immutable compile-time constants. They allocate no memory, hold no references, perform no locking, and persist no software state.

The hardware registers identified by these offsets are stateful and vary by block:

- DIG/DP registers hold encoder mode, packet/audio/metadata state, link-training state, MST allocation, DSC transport state, CRC/test state, and live status bits.
- DCIO and GPIO registers hold PHY routing, panel power sequencing, backlight PWM, HPD/DDC/AUX pad configuration, and soft-reset state.
- DSC registers hold compressor configuration and PPS/rate-control state, while perfmon registers expose counter/filter/snapshot behavior.
- DMCUB registers expose firmware boot windows, scratch mailboxes, GPINT signaling, inbox/outbox ring pointers, timers, interrupt state, fault state, and memory power controls.
- MCIF_WB2 registers hold writeback buffer addresses, sizes, pitch, arbitration, QoS/watermark, and buffer-manager state.
- DCHVM registers control and report display host-VM/RIOMMU state.
- VGA and Azalia `ix...` indexes address legacy display state, audio endpoint capabilities and controls, sink descriptors, CRC results, input status, power/reset controls, and stream FIFO/latency counters.

Volatility is register-specific and not encoded here. Some registers are read-only capabilities or status, some are sticky or write-one-to-clear interrupt/status bits, some are self-clearing controls, and some retain programmed values until modeset, hotplug, suspend/resume, GPU reset, or firmware reinitialization.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 2.1 ASIC register database. The numeric offsets must match the DCN 2.1 hardware map and the companion mask/shift header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h`.

In this tree, `dcn_2_1_0_offset.h` is included by DCN 2.1 display modules such as `dmub_dcn21.c`, `irq_service_dcn21.c`, `hw_factory_dcn21.c`, `hw_translate_dcn21.c`, and `dcn21_resource.c`. Those users integrate the constants with register helper macros, IRQ-source tables, GPIO construction/translation, resource initialization, and DMUB service register tables.

Major integration surfaces represented by this chunk include:

- DisplayPort and HDMI encoder bring-up for multiple link instances.
- DP MST, MSO, DSC-over-DP, secondary-data packets, audio transport, metadata, and ALPM.
- HDMI/TMDS packet and audio configuration.
- GPIO, HPD, DDC, AUX, panel power sequencing, and backlight control.
- DSC compressor programming for up to six instances and associated performance monitoring.
- DMCUB firmware boot, mailbox, GPINT, scratch, timer, and interrupt handling.
- Display writeback through MCIF writeback instance 2.
- Host-VM/IOMMU interaction for display memory access.
- Legacy VGA and HDA/Azalia audio endpoint compatibility paths.

## Risks And Edge Cases

The primary risk is silent hardware misaddressing. A wrong offset or base index compiles successfully but can read or write a different register, causing failures that look like link-training flakiness, absent display output, broken HDMI/DP audio, bad DSC compression, missed HPD/DDC events, invalid GPIO polarity, DMCUB boot or mailbox failures, writeback corruption, or VM/IOMMU faults.

The chunk is highly repetitive across instances. DIG3 and DIG4 are parallel layouts; DP2, DP3, and DP4 are parallel layouts; DSC0 through DSC5 are parallel compressor layouts with regular base-address spacing. Instance-local generator mistakes can affect only one connector, stream, compressor, or writeback path, so tests that exercise only the first instance may miss defects in higher-numbered blocks.

The range starts mid `DIG2` and ends mid `AZF0STREAM15`. Whole-file reconciliation should treat both ends as continuations owned jointly with neighboring chunks. In particular, this chunk should not be described as the complete DIG2 or Azalia stream namespace.

Names expose intent but not access semantics. Registers named `*_INTERRUPT_*`, `*_STATUS`, `*_ACK`, `*_RESET`, `*_SOFT_RESET`, `*_POWER_*`, `*_LPIB_SNAPSHOT_*`, and `*_FORMAT_CHANGED` still require companion field definitions and hardware documentation for polarity, clear behavior, ordering, and side effects.

The `mm...` and `ix...` namespaces must not be mixed. `mm...` values are MMIO offsets plus base indexes; `ix...` values are indirect indexes for VGA or Azalia mechanisms. Treating an `ix...` value as a flat MMIO address, or ignoring `*_BASE_IDX` on `mm...` values, would target the wrong hardware path.

DCHVM uses a different base index than the surrounding display blocks. Generic code that assumes base index `2` for every macro in this range would misaddress DCHVM control/status registers.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build DCN 2.1 AMDGPU display code and ensure `dmub_dcn21.c`, DCN 2.1 IRQ service, GPIO factory/translator, and resource code compile with this offset header and the matching mask/shift header.
- Compare all constants in this line range against AMD's source register database and against adjacent DCN/DCE generation headers where repeated block layouts should match.
- Exercise DP2, DP3, and DP4 links independently with link training, video modes, MST slot allocation, MSO where supported, DSC transport, secondary-data packets, audio, metadata, CRC, and hotplug.
- Exercise DIG3 and DIG4 HDMI/TMDS modes, including infoframes, generic packets, audio ACR, AFMT status/CRC, lane enable, backend enable, and force-disable paths.
- Validate DCIO GPIO behavior with HPD interrupts, DDC/AUX transactions, panel power sequencing, backlight PWM changes, genlock/swaplock pads, and suspend/resume.
- Program each DSC instance used by the platform and verify compressed display output, PPS/rate-control settings, interrupt/status handling, clock/memory power behavior, and perfmon counters.
- Boot and communicate with DMCUB on DCN 2.1 hardware, covering inbox/outbox ring pointers, GPINT interrupts, scratch/status registers, timer reads, reset transitions, and fault reporting.
- Run writeback tests that specifically use MCIF_WB2, checking buffer address high/low programming, Y/C offsets, pitch, resolution, watermarks, arbitration, buffer-manager status, and QoS behavior.
- Exercise Azalia audio enumeration and playback/capture-visible paths, including endpoint capabilities, sink descriptors, HBR/multichannel settings, stream latency counters, CRC channels, LPIB snapshots, codec reset/power state, and input endpoint infoframes.
- Include suspend/resume, GPU reset, repeated modesets, connector unplug/replug, audio format changes, and multi-connector scenarios to catch stale register state and instance-specific offset errors.

Regression symptoms from bad constants include black screens on specific connectors, DP link-training failures, MST bandwidth or slot allocation errors, DSC corruption, missing or unstable HDMI/DP audio, broken backlight or HPD/DDC/AUX behavior, DMCUB command timeouts, writeback frame corruption, impossible latency/CRC counters, and failures isolated to DIG3/DIG4, DP3/DP4, DSC instances above 0, or stream indexes above the first few.

## Cross-Chunk Notes

Neighboring chunks own the beginning of the `DIG2` block before line 10416 and the remainder of `AZF0STREAM15` and later offset definitions after line 13053. The final merge lane should describe this source file as generated DCN 2.1 register-offset metadata, with this chunk specifically covering the mid-file display-output, compression, firmware, writeback, host-VM, VGA, and Azalia indirect-register ranges.

### subset-b-001655: lines 13054-13875

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 13054-13875

## Scope

This chunk is the final DCN 2.1.0 register-offset segment for AMD display audio/Azalia blocks. It contains generated C preprocessor constants only: no structs, functions, executable control flow, or storage definitions are introduced here. The covered range starts with the last three `AZF0STREAM15` latency counter indices, then defines indirect endpoint register indices for eight output endpoints (`AZF0ENDPOINT0` through `AZF0ENDPOINT7`) and eight input endpoints (`AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`). The file closes with the header guard `#endif`.

The chunk contributes 755 `#define` entries. Every `addressBlock` in this range has `base address: 0x0`, because these values are not direct MMIO offsets by themselves; they are indices written through an Azalia endpoint index/data window.

## Purpose

`dcn_2_1_0_offset.h` is the DCN21 generated register address table used by the AMDGPU display driver for Renoir/DCN 2.1 hardware. Earlier parts of the file define direct MMIO offsets and base-index selectors for display, GPIO, interrupt, DMUB, DCCG, and audio wrapper registers. This tail chunk defines the indirect register numbers inside each Azalia function 0 endpoint.

The constants provide stable symbolic names for hardware-defined audio codec registers:

- `ixAZF0STREAM15_AZALIA_WORSTCASE_LATENCY_COUNT`, `ixAZF0STREAM15_AZALIA_CUMULATIVE_LATENCY_COUNT`, and `ixAZF0STREAM15_AZALIA_CUMULATIVE_REQUEST_COUNT` complete the stream-15 latency/counter group.
- `ixAZF0ENDPOINTn_*` defines output converter and output pin-control register indices for endpoint instances 0-7.
- `ixAZF0INPUTENDPOINTn_*` defines input converter and input pin-control register indices for input endpoint instances 0-7.

The values are small codec register indices such as `0x0001`, `0x0020`, `0x0054`, and `0x006e`, not full bus addresses. Runtime code selects an endpoint's index/data MMIO pair, writes one of these indices into the endpoint index register, and then reads or writes the endpoint data register.

## Important Definitions

### Output Endpoint Blocks

Each `azf0endpointN_endpointind` block, for N in 0-7, repeats the same 75-register output endpoint layout:

- Converter capability and programming:
  - `...CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` at `0x0001`
  - `...CONTROL_CONVERTER_FORMAT` at `0x0002`
  - `...CONTROL_CHANNEL_STREAM_ID` at `0x0003`
  - `...CONTROL_DIGITAL_CONVERTER` at `0x0004`
  - `...PARAMETER_STREAM_FORMATS` at `0x0005`
  - `...PARAMETER_SUPPORTED_SIZE_RATES` at `0x0006`
  - `...STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and GTC delta min/max registers at `0x0007`-`0x000e`.
- Pin capability and pin-control registers:
  - widget and pin capabilities at `0x0020` and `0x0021`
  - unsolicited response, pin sense, widget control, and channel/speaker allocation at `0x0022`-`0x0025`
  - `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` at `0x0028`-`0x0035`, used to expose sink audio format capabilities
  - multichannel, lipsync, HBR, and sink-info registers at `0x0036`-`0x0042`
  - hot-plug/audio enable and forced unsolicited response registers at `0x0054` and `0x0055`
  - configuration default, multichannel mode, codec channel-status overrides, association info, digital output status, LPIB snapshot/status, coding type, format-changed, wireless-display identification, remote-keepalive, and audio enable/interrupt status registers at `0x0056`-`0x006e`.

The output endpoint block is the part most directly tied to normal HDMI/DP audio output. `dce_audio.c` uses generic `ixAZALIA_F0_CODEC_*` names for the active endpoint, while DCN21 resource construction maps endpoint instances through `AZF0ENDPOINTn_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `...DATA` direct MMIO registers elsewhere in this same generated header.

### Input Endpoint Blocks

Each `azf0inputendpointN_inputendpointind` block, for N in 0-7, repeats a smaller 22-register input endpoint layout:

- Input converter capability and programming at indices `0x0001`-`0x0006`.
- Input pin capability and control at `0x0020`-`0x0024`.
- Multichannel enable, HBR, channel allocation, hot-plug/audio-enable, unsolicited response force, configuration default, LPIB snapshot/status, input status control, and input infoframe registers at `0x0036`-`0x0068`.

These names mirror output endpoint concepts but include `INPUT_` in the macro names and omit output-specific descriptors such as the `SINK_INFO0`-`SINK_INFO8`, codec channel-status override, digital output status, coding type, wireless display, and audio-format-change interrupt status registers.

## Runtime Integration

This header is included by DCN21 display code, notably:

- `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`

For this chunk, the meaningful consumer path is the DC audio resource setup:

- `dcn21_resource.c` includes this offset header and builds `audio_regs[]` with `AUD_COMMON_REG_LIST(id)`.
- `AUD_COMMON_REG_LIST(id)` in `display/dc/dce/dce_audio.h` expands to `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and `SRI(AZALIA_F0_CODEC_ENDPOINT_DATA, AZF0ENDPOINT, id)`, plus common audio function and DTO registers.
- `dcn21_create_audio()` passes `&audio_regs[inst]`, `audio_shift`, and `audio_mask` to `dce_audio_create()`.
- `dce_audio.c` implements `write_indirect_azalia_reg()` and `read_indirect_azalia_reg()`: these first program `AZALIA_F0_CODEC_ENDPOINT_INDEX.AZALIA_ENDPOINT_REG_INDEX`, then write/read `AZALIA_F0_CODEC_ENDPOINT_DATA.AZALIA_ENDPOINT_REG_DATA`.
- Higher-level audio setup uses `AZ_REG_READ()` and `AZ_REG_WRITE()` around indirect names such as `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR`, `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, `AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, `AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0 + format_index`, and `AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO0`-`SINK_INFO8`.

The line-range definitions therefore support the final indirect-index step for endpoint-local HDA codec programming. The companion `dcn_2_1_0_sh_mask.h` defines bit shifts and masks for these register payloads, while `soc21_enum.h` provides enum values for many decoded fields, including Azalia widget capabilities, HBR capability, multichannel mode, and input endpoint status concepts.

## Control Flow

There is no local control flow in this generated header chunk. The effective runtime flow is:

1. DCN21 resource initialization selects an audio endpoint instance and stores its direct index/data MMIO addresses in `struct dce_audio_registers`.
2. Audio configuration code computes HDMI/DP audio capabilities from CRTC timing, link information, and sink `audio_info`.
3. The driver writes an indirect endpoint register index, using the `ix...` numeric constants generated in this header family.
4. The driver writes or reads the endpoint data register using bitfield masks from `dcn_2_1_0_sh_mask.h`.
5. Hardware persists the resulting audio endpoint state until changed, reset, or power-managed by the display/audio block.

Typical output endpoint updates include enabling/disabling the audio pin, exposing HBR capability, programming lipsync delay, setting speaker/channel allocation, filling short-audio descriptors, and publishing sink information. The input endpoint definitions in this chunk are available for hardware support and mask/enum completeness, though the common DCN21 `dce_audio.c` path primarily programs output endpoint register names.

## State and Persistence

The header itself has no mutable state. It defines compile-time numeric constants.

The hardware registers named by these constants are stateful. Important endpoint state classes include:

- Capability/configuration state: converter format, stream ID, supported formats/rates, widget/pin capabilities, configuration default.
- Active audio-output state: hot-plug/audio-enable control, widget output enable, channel/speaker allocation, HBR enable/capability, lipsync, audio descriptors, sink info, and digital converter flags.
- Monitoring/counter state: LPIB snapshots, timer snapshots, latency counters, audio enable/disable/format-change interrupt status, input activity, and infoframe validity.
- Protocol-visible state: unsolicited response controls, pin sense, configuration default, and sink-info fields that can affect what the audio stack or connected sink observes.

Because the values are hardware indices, persistence is governed by the GPU display/audio block, suspend/resume paths, display hotplug, and driver reinitialization. Any incorrect constant can persist as an incorrect register write until the block is reset or the endpoint is reprogrammed.

## Dependencies

This chunk depends on the hardware register map generated for DCN 2.1.0. Its definitions are paired with:

- `dcn_2_1_0_sh_mask.h` for the bit-level layout of each endpoint register.
- `soc21_enum.h` for semantic enum values associated with Azalia fields.
- `renoir_ip_offset.h` and `DMU_BASE__INST0_SEG*` base macros for direct MMIO base calculation in DCN21 resource, IRQ, GPIO, and DMUB users.
- `display/dc/dce/dce_audio.h` for `AUD_COMMON_REG_LIST(id)` and the `struct dce_audio_registers` contract.
- `display/dc/dce/dce_audio.c` for indirect Azalia read/write helpers and HDMI/DP audio programming.
- AMD DC register helper macros such as `REG_SET`, `REG_READ`, `REG_SET_FIELD`, `SR`, `SRI`, and `SF`.

The generated naming convention is itself an integration dependency. Call sites synthesize names by token concatenation, so spelling, instance numbering, and suffix consistency are compile-time API surface.

## Risks

- **Wrong index values can program the wrong endpoint-local register.** Since these are indirect indices, a single bad value can redirect writes to unrelated codec state while still compiling cleanly.
- **Instance copy/paste or generator drift is high impact.** The output and input endpoint blocks are repeated for eight instances; mismatched values between instances would create endpoint-specific audio failures that are easy to miss in single-port testing.
- **Confusing direct offsets with indirect indices is a maintenance risk.** Most of `dcn_2_1_0_offset.h` contains `mm...` direct MMIO offsets plus `_BASE_IDX`; this chunk's `ix...` values are endpoint register numbers and must be used through the Azalia index/data window.
- **Field masks must match these offsets.** The companion mask header has instance-specific field names for `AZF0ENDPOINTn_*` and `AZF0INPUTENDPOINTn_*`; stale masks paired with changed indices would produce silent hardware misprogramming.
- **Audio behavior is sink- and timing-dependent.** Registers in this chunk expose EDID-derived audio descriptors, HBR support, channel allocation, lipsync, and sink info. Bad programming may present as missing audio, unsupported sample rates, wrong channel layout, HBR failures, or hotplug/audio enable races.
- **Input endpoint coverage may be lightly exercised.** The source tree's common DC audio path focuses on output endpoint programming. Input endpoint constants can remain compile-validated but receive less runtime coverage unless capture/input-audio paths are tested on supporting hardware.

## Test Signals

Useful signals for this chunk are mostly integration and hardware-behavior tests, not unit tests:

- Build coverage for DCN21/Renoir display code with `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h` included; token-concatenated register names should compile for audio, GPIO, IRQ, and DMUB users.
- HDMI and DisplayPort audio playback on each available endpoint instance, including endpoint instances beyond 0 when hardware exposes multiple display audio pins.
- Hotplug/replug tests that verify `HOT_PLUG_CONTROL`, unsolicited response, and audio enable/disable behavior do not leave stale audio state.
- EDID/audio-mode tests that exercise `AUDIO_DESCRIPTOR0`-`13`, channel/speaker allocation, sink info, and advertised sample-rate/channel capabilities.
- HBR audio tests, especially 192 kHz / 8-channel or compressed high-bitrate formats, to verify `RESPONSE_HBR` and descriptor programming.
- Suspend/resume and display modeset tests to ensure indirect endpoint state is restored after hardware reset or power transitions.
- Register trace/debugfs comparison against known-good DCN21 hardware tables: index writes should match expected values such as `0x0025` for channel/speaker, `0x0038` for HBR response, `0x0054` for hot-plug control, and `0x0064`-`0x0066` for LPIB snapshots.

## Summary

Lines 13054-13875 are a generated register-map chunk for DCN21 Azalia stream, output endpoint, and input endpoint indirect registers. The code does not implement algorithms, but it is part of the compile-time hardware ABI used by AMDGPU display audio setup. Its correctness is validated through successful DCN21 builds and hardware tests that cover HDMI/DP audio enablement, sink capability publication, HBR support, channel allocation, endpoint hotplug, and state restoration.
