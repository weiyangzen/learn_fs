# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001508`: lines 1-3028, `Docs/researches/chunks/subset-b-001508_research.md`
- `subset-b-001509`: lines 3029-6043, `Docs/researches/chunks/subset-b-001509_research.md`
- `subset-b-001510`: lines 6044-7658, `Docs/researches/chunks/subset-b-001510_research.md`

## Chunk Research

### subset-b-001508: lines 1-3028

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h lines 1-3028

## Scope And Purpose

This chunk is the first part of the generated-style AMD DCE 11.0 register address header. It contains license text, the `DCE_11_0_D_H` include guard, and 2,969 preprocessor constants mapping symbolic `mm...` and a few `ix...` register names to numeric DCE 11.0 MMIO or indexed-register offsets. There are no functions, structs, enums, inline helpers, or executable branches in this range.

The purpose is to give AMDGPU and DC display code stable symbolic names for DCE 11.0 hardware blocks: display power gating, ambient backlight management, CRTC timing and status registers, DAC/performance counters, DCCG display-clock generation, PLL/CPLL reserved control spaces, DMIF/DCI/MCIF memory-interface registers, DCIO/UNIPHY link and pad registers, DCRX/DPHY PHY reserved ranges, DCP graphics-plane programming, color-space conversion, cursor state, gamma/LUT programming, CRC controls, and the opening DVMM PTE register.

The range starts at file line 1 and stops at line 3028 with `mmDCP0_DVMM_PTE_CONTROL`; the DVMM family continues in the next chunk, so conclusions about DVMM coverage require adjacent chunk research.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace itself. Consumers include this file together with `dce_11_0_sh_mask.h`, then pass address macros to register access helpers such as `dm_read_reg()`, `dm_write_reg()`, `RREG32()`, `WREG32()`, offset wrappers such as `CRTC_REG(reg)` and `DCP_REG(reg)`, or generated register tables.

Important macro families in this chunk include:

- Power gating and low-level display control: `mmPIPE0_PG_CONFIG` through `mmPIPE2_PG_STATUS`, `mmDCFEV0_PG_*`, `mmDCPG_INTERRUPT_*`, `mmDC_IP_REQUEST_CNTL`, `mmDC_PGFSM_*`, `mmDC_PGCNTL_STATUS_REG`, and DCPG debug-index/data registers.
- Backlight and ABM: `mmBL1_PWM_*`, `mmDC_ABM1_*`, histogram/gain/luma-summary registers, `mmDC_ABM1_BL_MASTER_LOCK`, and `mmABM_TEST_DEBUG_*` provide display backlight, ambient-light, adaptive backlight, histogram, and debug register addresses.
- CRTC timing generators: the large `mmCRTC_*` family plus `mmCRTC0_...` through `mmCRTC5_...` aliases define horizontal/vertical totals, blanking, sync, triggers, counters, status, stereo, snapshots, update locks, test patterns, vertical interrupts, CRC windows/data, GSL, and master/update controls for six display pipes.
- DAC and display performance monitors: `mmDAC_*` covers legacy analog-output, CRC, autodetect, power, comparator, FIFO, and debug registers; `mmPERFCOUNTER_*`, `mmPERFMON_*`, and `mmDC_PERFMON0...11_*` define replicated performance-monitor control, state, counter, select, and interrupt registers.
- DCCG and clock generation: `mmDCCG_*`, `mmDP_DTO*`, `mmCRTC*_PIXEL_RATE_CNTL`, `mmDCCG_AUDIO_DTO*`, `mmSYMCLK*`, `mmDISPCLK_*`, `mmDCCG_GATE_DISABLE_*`, and `mmMICROSECOND_TIME_BASE_DIV` define display clock, pixel-rate DTO, audio DTO, gate, reset, timing-base, and debug registers.
- PLL and CPLL reserved macro spaces: `mmCPLL_MACRO_CNTL_RESERVED*`, `mmDCCG_CPLL0...3_*`, `mmPLL_MACRO_CNTL_RESERVED*`, and `mmDCCG_PLL0...2_*` describe contiguous PLL/CPLL control windows, including the highest address in this chunk, `mmDCCG_CPLL3_CPLL_MACRO_CNTL_RESERVED11` at `0x5fff`.
- DMIF, DCI, MCIF, and DVMM memory-interface controls: `mmDMIF_*`, `mmPIPE0...7_*`, `mmMCIF_*`, `mmRBBMIF_*`, `mmDCI_*`, and the first `mmDVMM_*` names cover display memory request arbitration, VMID, fault/status, memory power, reset/debug, and PTE programming entry points.
- DCIO, link, and panel registers: `mmDC_GENERICA/B`, pad/ref-clock/GPIO/debug registers, `mmUNIPHY[A-G]*`, `mmUNIPHYLPA/B*`, impedance calibration, AUX impedance, `mmLVTMA_PWRSEQ_*`, `mmBL_PWM_*`, GSL/swaplock pads, GPU timer, DCIO clock/reset/debug, and indexed `ixDCIO_DEBUG*` constants.
- PHY macro windows: `mmDCIO_UNIPHY0...8_UNIPHY_MACRO_CNTL_RESERVED*`, `mmDCRX_PHY_MACRO_CNTL_RESERVED*`, and `mmDPHY_MACRO_CNTL_RESERVED*` expose contiguous reserved/control spaces for link PHY bring-up, tuning, or diagnostics.
- DCP graphics, color, cursor, and LUT registers: `mmGRPH_*`, `mmDCP0...5_GRPH_*`, prescale, input/output CSC, common matrix, gamut remap, spatial dither, cursor surface/address/position/color/update, `mmDC_LUT_*`, DCP CRC, and the initial DVMM PTE address are replicated for six DCP instances.

## Control Flow And Data Flow

There is no runtime control flow in this header. Data flow is compile-time substitution: C code names a register, the preprocessor replaces it with an offset, and a register access helper combines it with any per-block offset before issuing MMIO or indexed-register accesses.

The implied hardware data flows are:

- CRTC programming code writes timing totals, sync windows, blanking, update locks, test patterns, CRC controls, and interrupt positions/status through the `mmCRTC*` addresses.
- DCP and graphics-plane code writes surface addresses, pitch, viewport bounds, CSC coefficients, prescale values, gamut matrices, cursor memory and position, LUT indices/data, and CRC controls through base names plus DCP instance offsets or explicit `mmDCP0...5_*` aliases.
- Clock and audio code programs DCCG DTO phase/modulo/source registers, pixel-rate controls, symbol clocks, and clock gating/reset registers.
- Memory-interface and power paths program DMIF/MCIF/DCI arbitration, request limits, VMID, low-power tiling, power status/control, and soft-reset/debug registers.
- Link/panel bring-up code may use DCIO, UNIPHY, LVTMA, backlight PWM, impedance calibration, GSL, and debug-index/data registers for output routing, panel sequencing, clocking, and diagnostics.

## State And Persistence Behavior

This header stores no runtime state. The state represented by the constants lives in DCE 11.0 hardware registers and persists according to the underlying block's reset, power-gating, suspend/resume, and mode-set behavior.

State classes represented in this chunk include:

- Mutable display configuration: CRTC timing, blanking, sync, interlace/stereo, update-lock, DCP graphics format, surface addresses, pitch, cursor configuration, CSC/prescale/gamut/LUT state, DCCG clocks, and DCIO output routing.
- Latched or sticky status: power-gating status, CRTC vertical/update/CRC/status counters, DAC autodetect/comparator/FIFO state, performance monitor counters and interrupts, DMIF/DVMM/DCI/RBBMIF status/faults, DCIO debug state, and DCP CRC current values.
- Hardware shadow/update behavior: CRTC and DCP update locks, master update mode, graphics address in-use registers, LUT write/index registers, and CRC windows are intended to coordinate active scanout changes.
- Diagnostic/indexed state: DCPG, ABM, CRTC, DAC, DCCG, DMIF, MCIF, DCI, DCIO, and PHY debug-index/data windows expose hardware-internal read/write views rather than normal driver-owned software storage.

Incorrect constants can survive until the affected block is reprogrammed or reset. A bad address for timing, clock, surface, LUT, CSC, or memory arbitration can immediately affect active scanout; a bad status or interrupt address can hide faults or create false diagnostics.

## Dependencies And Integration Points

This header is paired with `dce_11_0_sh_mask.h` for bitfield masks and shifts. DC DCE110 code includes it in timing generator, compressor, transform, memory-input, OPP, audio, link encoder, clock manager, IRQ, GPIO, resource, and HW sequence modules. The older AMDGPU DCE paths use the same register-address style directly through `RREG32()` and `WREG32()`.

Concrete integration examples in the repository include:

- `display/dc/dce110/dce110_timing_generator.c` includes this file and defines `CRTC_REG(reg) (reg + tg110->offsets.crtc)` and `DCP_REG(reg) (reg + tg110->offsets.dcp)`. It programs `mmCRTC_H_TOTAL`, `mmCRTC_V_TOTAL`, and `mmCRTC_STATUS` via `dm_read_reg()` / `dm_write_reg()`.
- DCE audio programming in older AMDGPU display code writes `mmDCCG_AUDIO_DTO0_PHASE`.
- LUT setup code writes `mmDC_LUT_RW_INDEX + amdgpu_crtc->crtc_offset`, relying on the base DCP address pattern represented in this chunk.
- `pm/powerplay/hwmgr/polaris_baco.c` includes the same DCE 11.0 address header, so display register constants also intersect with power-management and BACO sequencing.

The repeated alias pattern is central to integration. For example, the generic `mmCRTC_H_TOTAL` and `mmCRTC0_CRTC_H_TOTAL` both map to pipe 0, while pipe 1-5 aliases step through separate address ranges. DCP aliases follow the same model: generic `mmGRPH_ENABLE` and `mmDCP0_GRPH_ENABLE` map to DCP0, with DCP1-5 at later offsets.

## Risks And Edge Cases

The main risk is mismatch between these generated constants and the actual DCE 11.0 hardware register database. The compiler can catch a missing macro name, but it cannot catch a wrong numeric address.

Specific risks in this chunk:

- Repeated per-instance aliases are easy to drift. CRTC0-5, DCP0-5, PERFMON0-11, PIPE0-7, UNIPHY0-8, PLL0-2, and CPLL0-3 names differ only by instance number while mapping into different address windows.
- Generic names usually alias instance 0. Code that adds an instance offset must use the right base macro; code that uses explicit instance macros must avoid adding another offset.
- Debug-index/data and reserved PHY/PLL macro windows are low-level and may have undocumented side effects. Accidental writes can affect link clocks, PHY tuning, or diagnostic state.
- Address families are not strictly sorted by address. For example DCCG low-address registers, high-address PLL/CPLL windows, and later mid-address DCP registers are interleaved by functional grouping, so range assumptions based on source order are unsafe.
- CRTC and DCP update-lock, in-use, CRC, and status registers have timing-sensitive hardware semantics. Wrong offsets can cause tearing, stale scanout, failed CRC validation, or writes landing in a neighboring pipe.
- The chunk boundary is mid-register-family at `mmDCP0_DVMM_PTE_CONTROL`; any DVMM analysis must merge with the following chunk before making final per-file claims.

## Test Signals

There are no unit tests for this header alone. Useful validation signals are build coverage, generated-header comparison, and hardware or register-readback tests:

- Build AMDGPU/DC configurations that include DCE110 display code and Polaris power-management code; this catches missing or renamed macros.
- Compare lines 1-3028 against the authoritative AMD DCE 11.0 register database or an upstream generated copy, especially repeated instance offsets and the PHY/PLL reserved windows.
- Exercise DCE 11.0 mode setting across multiple CRTCs and planes; verify timing, update-lock, surface-address, cursor, CSC, LUT, CRC, and vblank/status readbacks.
- Validate audio DTO and pixel-clock programming through display bring-up, audio-over-display output, and clock readback.
- Test suspend/resume and BACO or power-gating paths for DCPG, DCCG, DCIO, DMIF/DCI, and register restoration behavior.
- Run DisplayPort/eDP panel and link tests that touch UNIPHY, DCIO, LVTMA power sequencing, backlight PWM/ABM, and PHY debug paths.
- Use register dump comparison after known-good modesets to confirm generic-plus-offset access and explicit per-instance macros resolve to the intended hardware blocks.

### subset-b-001509: lines 3029-6043

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h

Chunk: `subset-b-001509`
Covered source range: lines 3029-6043 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h`

## Purpose

This chunk is a generated AMD DCE 11.0 register-address header segment. It contains no executable C code; it publishes preprocessor constants that map display-engine register names to ASIC-specific MMIO offsets or indexed-register indices.

The range covers 3,015 `#define` entries. Most are `mm*` MMIO register address constants, with 46 `ix*` indexed VGA/debug register constants near the end. The chunk begins in the middle of the DCP register-address block at `mmDCP1_DVMM_PTE_CONTROL` and ends in legacy VGA CRTC indexed-register definitions through `ixCRT0D`. The merge lane must combine this with neighboring chunks for a full-file view because both the opening DCP families and the later VGA indexed families continue outside this range.

The covered register families describe the display pipeline for DCE 11.0 hardware: DCP/graphics plane state, regamma, digital encoder and DisplayPort/HDMI audio/video packet registers, AUX channels, DVO, frame-buffer compression, formatter, line buffer, video line-buffer/scaler/color-management blocks, underlay plane registers, MVP, scalar, and legacy VGA sequencer/CRTC access points.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface is a flat set of integer macros:

- `mmDCP*_*`: DCP and graphics-plane register offsets for DVMM/PTE controls, CRC, GSL, debug/status, flip-rate/stereo flip, hardware rotation, XDMA underflow/recovery, alpha, surface counters, and the `REGAMMA_*` lookup-table and piecewise-linear region controls.
- `mmDIG*_*`, `mmHDMI_*`, and `mmAFMT_*`: digital front-end/back-end, HDMI, TMDS, audio formatter, CRC, infoframe, ACR, generic packet, audio source, and debug registers. The block exposes replicated DIG instances 0-8 with address bases such as `0x4a00`, `0x4b00`, `0x4c00`, `0x4d00`, `0x4e00`, `0x4f00`, `0x5400`, `0x5600`, and `0x5700`.
- `mmDP*_*`: DisplayPort link, pixel format, MSA, video timing, DPHY training, scrambling, CRC, fast training, secondary-data, audio M/N, MST/MSE, and DP test/debug registers. These are replicated for DP instances 0-8.
- `mmAUX_*` and `mmDP_AUX*_*`: DisplayPort AUX channel control, arbitration, interrupt, software/native data, DPHY TX/RX, GTC sync, and test/debug registers. The six AUX channels are spaced by `0x1c`.
- `ixDP_AUX_DEBUG_*`: indexed debug selector values for AUX debug registers.
- `mmDVO_*`: DVO enable/source/output/control, CRC, FIFO error, and debug registers.
- `mmFBC_*`: frame-buffer compression control, idle masks, delays, compression mode, indirect LUT entries, CSM region offsets, client masks, debug CSR data, status, and debug registers.
- `mmFMT*_*`: formatter clamp, dynamic expansion, bit-depth/dither, CRC, debug, and test/debug register offsets for FMT instances 0-5.
- `mmLB*_*` and `mmLBV_*`: line-buffer data format, memory, vline/vblank status, interrupts, keyer colors, urgency/status, MVP flip integration, and debug/test registers for standard pipe LBs and the video line-buffer path.
- `mmMVP_*` and `ixMVP_DEBUG_*`: multi-view/plane control, FIFO, slave status, in-band capability, black keyer, CRC, receive counters, and debug selectors.
- `mmSCL*_*` and `mmSCLV_*`: scalar coefficient RAM, mode/taps, bypass/replicate/automatic mode, horizontal/vertical scale ratios and filter init values, viewport/overscan, mode-change detection, ALU/debug, and test/debug registers for pipe scalers and video scaler.
- `mmCOL_MAN_*`, `mmINPUT_CSC_*`, `mmOUTPUT_CSC_*`, `mmPRESCALE_*`, `mmDENORM_*`, `mmGAMMA_CORR_*`, and `mmINPUT_GAMMA_*`: video color-management, CSC matrix, prescale, denormal clamp, gamma-correction LUT/regions, FIFO error, input gamma LUT, and debug registers.
- `mmUNP_*`: underlay graphics enable/control, luma/chroma surface addresses, pitch, offsets, dimensions, update/in-use addresses, DVMM controls, interrupts, flip, CRC, rotation, outstanding request limit, and debug registers.
- `mmGEN*`, `mmVGA*`, `mmDAC*`, `mmSEQ8_*`, `ixSEQ*`, `mmCRTC8_*`, and `ixCRT*`: legacy VGA, DAC, sequencer, and CRTC access/index definitions.

The `mm` constants are intended to be used with AMDGPU/DC register access helpers such as `dm_read_reg`, `dm_write_reg`, `RREG32`, `WREG32`, generated `REG_FIELD` tables, and offset arithmetic for replicated pipes. Field masks and shifts for these addresses live in the matching DCE 11.0 `*_sh_mask.h` headers.

## Control Flow

This chunk has no runtime control flow. Its operational flow is compile-time substitution:

1. A DCE 11.0 display source file includes `dce/dce_11_0_d.h`.
2. The source picks an address macro, often through a generated register table or by adding a pipe offset such as a CRTC/pipe instance offset.
3. The driver reads, writes, or read-modify-writes the hardware register through the AMDGPU or DC register accessor layer.
4. Companion mask/shift constants decode or compose individual fields when the register is not written as a whole value.

The hardware operations driven by consumers are state-machine heavy even though this header is declarative. DP link training uses the `DP_*` DPHY/training/status registers; HDMI/AFMT setup uses packet/audio/infoframe registers; FBC setup programs compression and status registers; underlay/video paths program `UNP`, `LBV`, `SCLV`, and color-management addresses; and pipe programming coordinates DCP, LB, SCL, FMT, and DIG blocks.

## State And Persistence Behavior

The header owns no software state and persists nothing. The constants become immediate values in compiled code.

The addressed hardware state is persistent at the register level. Writes to the DCE blocks can remain effective until changed by the driver, firmware, a modeset, display hotplug flow, suspend/resume, BACO/power transition, engine reset, or full GPU reset. Important persistent hardware state includes:

- plane surface addresses, pitch, offsets, viewport size, scaler ratios, and underlay luma/chroma addresses;
- regamma/gamma LUT indices/data and piecewise-linear region control;
- DP link configuration, training pattern, scrambling, M/N, secondary packet, MST/MSE, and AUX channel state;
- HDMI/AFMT infoframe/audio packet contents and ACR timing state;
- FBC compression mode, idle behavior, indirect LUT entries, and status/control bits;
- interrupt mask/status registers for line-buffer and underlay paths;
- legacy VGA indexed register selectors used by compatibility paths.

Some registers are read-only status, sticky status, clear-on-write, indexed debug, or hardware-owned. This address header does not encode access semantics, so callers must rely on the generated mask headers, block-specific code, and hardware documentation before doing generic updates.

## Dependencies

The direct dependency is only the C preprocessor, but practical use depends on the surrounding AMDGPU display register ecosystem:

- Companion DCE 11.0 shift/mask headers that define fields for the addresses declared here.
- DC/AMDGPU register access wrappers such as `dm_read_reg`, `dm_write_reg`, `RREG32`, `WREG32`, `REG_SET`, `REG_UPDATE`, and generated register-table macros.
- DCE 11.0 display component code. Tree references include IRQ service, GPIO hardware translation/factory, audio, link encoder, hardware sequencing, resource construction, clock manager, timing generator, compressor/FBC, video transform/memory input, OPP/regamma, and OPP CSC code under `drivers/gpu/drm/amd/display/dc`.
- Power-management integration, including the `polaris_baco.c` path that includes this DCE 11.0 address header.
- Hardware/firmware knowledge for DCE 11.0 register replication, pipe offsets, DIG/DP/AUX instance routing, and legacy VGA indexed access.

The constants are ASIC-generation specific. Neighboring generation headers (`dce_10_0_d.h`, `dce_11_2_d.h`, `dce_12_0_offset.h`, and older DCE headers) contain similar names with different offsets for some blocks, so consumers must not mix address headers from different hardware generations.

## Integration Points

This chunk is central to DCE 11.0 display programming. It supplies the address side of the register contract for:

- Pipe programming across DCP, LB, SCL, FMT, and DIG instances. Many replicated pipe blocks use a consistent offset pattern: DCP/LB/SCL/FMT instances 0-2 are based near `0x1a00`, `0x1c00`, and `0x1e00`; instances 3-5 are based near `0x4000`, `0x4200`, and `0x4400`.
- Link programming for HDMI, TMDS, AFMT, and DisplayPort. DIG/DP instances expose repeated per-link registers for video timing, training, scrambling, CRC, infoframes, audio, and debug paths.
- AUX and hotplug-adjacent DisplayPort transactions. The six `DP_AUX*` blocks provide register targets for AUX software/native operations and GTC synchronization state.
- FBC/compressor paths. `dce110_compressor.c` and `dce112_compressor.c` use `mmFBC_CNTL` and related FBC registers to set up frame-buffer compression behavior.
- Video underlay paths. `dce110_mem_input_v.c` reads and updates `mmUNP_GRPH_ENABLE`; related `UNP_*`, `LBV_*`, `SCLV_*`, and color-management registers define the underlay pipeline.
- Legacy VGA compatibility paths, where `mmGEN*`, `mmDAC*`, `mmSEQ8_*`, `mmCRTC8_*`, and `ixSEQ*`/`ixCRT*` constants identify indexed VGA register access points.

Consumers often do not reference every macro name directly. The header is commonly included by generated register lists and block-specific register tables that map abstract DC structures to these concrete offsets.

## Risks And Edge Cases

- These are untyped integer macros. The compiler cannot detect using a DCE 11.0 address with a different generation's field mask, using a per-link register on the wrong instance, or writing a status/debug register as if it were a normal control register.
- The chunk starts mid-family at `mmDCP1_DVMM_PTE_CONTROL`, so DCP0 and the earlier surface/GRPH definitions are outside this range. The final file-level report should merge neighboring chunks before claiming complete DCP coverage.
- Replicated register blocks are repetitive and easy to misread. DIG/DP instances do not use one simple contiguous base stride for every instance: after DIG5/DP5 at `0x4fxx`, later instances move to `0x54xx`, `0x56xx`, and `0x57xx`.
- There is a suspicious generated alias at line 4555: `mmDP8_DP_DPHY_SCRAM_CNTL` is assigned `0x56b6`, while the surrounding pattern has DP6 at `0x54b6` and then no `mmDP7_DP_DPHY_SCRAM_CNTL` before DP8. The same pattern appears in the related DCE 11.2 header, so it may reflect generator input rather than a local typo, but any code that expects a DP7/DP8 sequence should verify it against hardware documentation.
- Address-only macros do not document access rules. Some covered registers are read-only status, sticky/clear-on-write interrupt or error status, indexed debug selectors, LUT data ports, or hardware-sequenced training registers.
- LUT/index/data pairs such as regamma, gamma-correction, input-gamma, FBC indirect LUT, and debug-index/data registers require ordered accesses. Reordering, concurrent access, or generic register dumps that write index registers can disturb the hardware-visible selector state.
- Surface-address registers span low/high and luma/chroma pairs in the underlay block. Partial updates or wrong ordering can produce invalid scanout addresses.
- DP/HDMI audio and packet registers affect link-visible data sent to monitors. Incorrect writes may not fail compilation but can cause silent audio, bad infoframes, link-training failures, or display blanking.
- Legacy VGA aliases reuse low offsets such as `0xf0`, `0xf1`, and `0xf2`; those names should only be used through the intended VGA access path.

## Test Signals

Useful validation signals are build-time, static-generation, and hardware integration checks:

- Build AMDGPU/DC targets that include `dce/dce_11_0_d.h`, especially DCE 11.0 IRQ, GPIO, audio, link encoder, resource, clock, timing generator, compressor, underlay, OPP/regamma, OPP CSC, and BACO paths.
- Static validation should compare this address header with the matching DCE 11.0 shift/mask header and generated register tables so every used register has the expected address and field definitions.
- Generator checks should verify replicated DCP/LB/SCL/FMT/DIG/DP/AUX instance address patterns, including intentional gaps and nonuniform instance bases.
- Modeset tests should exercise multiple pipes, scaler ratios, regamma/gamma programming, viewport/overscan changes, FMT bit-depth/dither settings, and CRC/debug readbacks where supported.
- DisplayPort tests should cover AUX transactions, link training, fast training, HBR2 pattern control, scrambling, CRC, MST/MSE secondary-data behavior, and DP audio M/N readback.
- HDMI tests should validate infoframes, ACR packet programming, AFMT audio packet state, TMDS control, and generic packet registers.
- FBC tests should enable/disable compression, read `FBC_STATUS`, verify idle/start-stop behavior, and check suspend/resume or BACO transitions.
- Underlay/video tests should verify `UNP_*`, `LBV_*`, `SCLV_*`, and color-management programming for luma/chroma surfaces, scaling, CSC, gamma, FIFO error, and interrupt/status behavior.
- Register-dump or debug tooling should read representative status/debug registers without disturbing index/data pairs, and should flag missing or unexpected aliases such as the `DP_DPHY_SCRAM_CNTL` DP7/DP8 sequence for manual review.

### subset-b-001510: lines 6044-7658

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h lines 6044-7658

## Scope And Purpose

This chunk is the final part of AMDGPU's generated DCE 11.0 register-address header. It contains no executable C logic; it is a compile-time map from symbolic register names to numeric MMIO or indirect register indices for the Display Controller Engine used by VI/Polaris-era AMD GPUs.

The range starts in legacy VGA indirect register indices and VGA MMIO controls, then covers display PHY PLL and UNIPHY addresses, display memory interface arbitration/watermark controls, HDMI/DP audio codec registers, blender and writeback/converter registers, display front-end clock/power controls, hot-plug-detect and I2C/DDC registers, virtual CRTC/blender/timing-generator registers, and XDMA master/slave register windows. It also closes the header with `#endif /* DCE_11_0_D_H */`.

The source path is under a Ceph client source mirror, but this file is Linux AMDGPU display hardware metadata. There is no Ceph filesystem behavior in this chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or persistent software objects in this line range. The API surface is entirely preprocessor constants:

- `mm*` names are register addresses for direct MMIO-style AMDGPU register accesses, or for indexed register address/data windows.
- `ix*` names are indirect register indices used through a paired index/data register or through a block-specific indirect access path.
- Many blocks define both a generic register name and instance-specific aliases, for example `mmDPG_PIPE_URGENCY_CONTROL` plus `mmDMIF_PG0_DPG_PIPE_URGENCY_CONTROL` through `mmDMIF_PG5_DPG_PIPE_URGENCY_CONTROL`.
- Repeated per-instance aliases encode DCE 11.0's display pipe layout: six main display pipes commonly step by `0x200` across `0x1bxx`, `0x1dxx`, `0x1fxx`, `0x41xx`, `0x43xx`, and `0x45xx`, while virtual-display blocks use the `0x47xx` range.

Major register families in this chunk include:

- Legacy VGA: `ixCRT*`, `ixGRA*`, `ixATTR*`, `mmVGA_RENDER_CONTROL`, `mmVGA_SOURCE_SELECT`, `mmVGA_MODE_CONTROL`, `mmVGA_MEMORY_BASE_ADDRESS`, per-display `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`, VGA status/interrupt/debug registers, and VGA page-address registers.
- PHY and link clocks: `mmBPHYC_DAC_*`, `mmPLL_*`, `mmBPHYC_PLL0_*` through `mmBPHYC_PLL2_*`, VGA pixel PLL variants such as `mmVGA25_PPLL_*`, and `mmPPLL_*` debug/spare registers.
- UNIPHY lanes/links: `mmUNIPHY_TX_CONTROL1` through `CONTROL4`, power, PLL feedback/control/spread-spectrum, synchronization, test/BIST, TMDS/DisplayPort tuning registers `mmUNIPHY_TMDP_REG0` through `REG6`, test-pattern, and debug registers, with instance aliases `mmBPHYC_UNIPHY0_*` through `mmBPHYC_UNIPHY8_*`.
- DMIF/DPG: pipe arbitration, watermark mask, urgency, DPM, stutter, NB pstate change, repeater, pre-check, debug, and test-debug registers for `DMIF_PG0` through `DMIF_PG5`, plus virtual DPG registers `mmDPGV0_*` and `mmDPGV1_*`.
- Azalia/HD audio: root/function/converter/pin codec parameters, immediate-command index/data registers, stream descriptor index/data registers, endpoint index/data windows, input endpoints, CRC controls, DTO/SCLK/DMA/CORB/RIRB controls, cyclic buffer synchronization, payload capabilities, and memory power control/status.
- Blender/writeback/converter: per-pipe `mmBLND*` control/update/underflow/update-lock/debug/test registers, virtual `mmBLNDV_*`, writeback enable/config, converter mode/window/source/CSC coefficients/round/clamp/test CRC, and converter debug registers.
- DCFE/DCO/HPD/I2C: display front-end clock/reset/debug/memory-power registers, virtual front-end registers, HPD interrupt/control/filter/fast-train registers for six connectors, DCO scratch/interrupt/clock/power/reset/debug registers, and DC/generic I2C/DDC transaction/speed/status/data registers.
- Virtual timing generator: `mmCRTCV_*` timing, sync, blanking, status, trigger, stereo, snapshot, update-lock, master update, interrupt, color, CRC, GSL, 3D structure, and test-debug registers.
- XDMA: top-level XDMA interface/config/interrupt/clock/memory-power/status/debug/power-gating registers, master global registers, six master pipe register groups, slave global registers, and six slave channel register groups.

Consumers pair this address header with `dce_11_0_sh_mask.h`, which supplies bit masks and shifts for the fields inside these addresses. Register access usually flows through AMDGPU helpers such as `RREG32()`, `WREG32()`, `dm_read_reg()`, `dm_write_reg()`, indexed Azalia helpers, or display-core register tables.

## Control Flow

This chunk has no local control flow. Its runtime effect is indirect: it determines which hardware register a distant driver read or write touches.

A typical control sequence using these constants is:

1. Select an address macro from this file, often with a pipe-specific offset or an instance-specific alias.
2. Read the register through `RREG32()`, `dm_read_reg()`, an Azalia endpoint helper, or a display-core register abstraction.
3. Decode or modify fields with masks from the matching `dce_11_0_sh_mask.h`.
4. Write the value back with `WREG32()` or `dm_write_reg()`, often inside display-mode programming, audio setup, power-gating, hotplug, I2C/DDC, or reset sequencing.

Visible integration examples in this repository include:

- `amdgpu/vi.c`, `amdgpu/cik.c`, `amdgpu/si.c`, `gmc_v*_0.c`, and `dce_v*_0.c` reading and writing `mmVGA_RENDER_CONTROL` to disable or restore VGA legacy rendering behavior during memory/display setup.
- `amdgpu/dce_v10_0.c`, `dce_v8_0.c`, and `dce_v6_0.c` using Azalia endpoint index/data registers to program audio codec endpoint state.
- DCE display core files under `display/dc/dce110/` including this header for timing generator, compressor, transform, OPP, clock, GPIO, link encoder, audio, and IRQ support.
- `display/dc/dce110/dce110_timing_generator_v.c` directly using `mmCRTCV_*` addresses for virtual timing-generator operations such as enable, blank control, status reads, timing programming, interlace setup, color programming, and frame-count reads.
- `display/dc/hwss/dce/dce_hwseq.h` and `dce110_hwseq.c` using virtual CRTC/blender offsets for hardware sequencer register table setup.
- SI/VI/MxGPU golden register arrays referencing `mmXDMA_CLOCK_GATING_CNTL` and `mmXDMA_MEM_POWER_CNTL` for XDMA clock and memory power programming.

Because the file is generated constants, bad behavior does not manifest near this file. A wrong address silently redirects a hardware access in display initialization, mode set, link/audio programming, hotplug handling, I2C/DDC transactions, virtual display timing, or XDMA setup.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It names hardware-backed state held by the DCE, PHY, audio, VGA, virtual display, and XDMA blocks. That state persists according to hardware rules until changed by the driver, firmware, display microcode, hotplug events, audio codec commands, suspend/resume, power-gating, BACO-like low-power transitions, function reset, or full ASIC reset.

The state represented by these addresses spans several categories:

- Legacy compatibility state: VGA sequencer/CRT/graphics/attribute indices, VGA render routing, memory base addresses, VGA page addresses, and per-display VGA controls.
- Clock and link state: PLL dividers, spread-spectrum controls, update locks, analog controls, UNIPHY power and PLL controls, data synchronization, transmitter test registers, and PHY debug/BIST state.
- Display pipe state: DMIF arbitration, watermark, urgency, DPM, stutter, NB pstate, repeater, and debug state for the six main pipes and virtual pipes.
- Audio state: Azalia controller clocking, DMA, CORB/RIRB, stream descriptors, endpoint codec parameters, pin/converter controls, sink information, multichannel enables, LPIB snapshots, CRC windows/results, and input endpoint controls.
- Composition and writeback state: blender controls, update locks, underflow interrupt state, writeback enable/config, converter window/source/CSC coefficients, clamps, and test CRC state.
- Front-end and connector state: DCFE clock/reset/memory-power state, DCO scratch and interrupt status, HPD interrupt/control/filtering state, and DDC/I2C transaction state.
- Timing state: virtual CRTC totals, blanks, syncs, triggers, counters, frame/vblank status, stereo/snapshot/update-lock/master-update state, color registers, vertical interrupts, CRC windows/data, and GSL controls.
- XDMA state: interface status, interrupt status, power-gating status, master pipe transfer descriptors, remote/local GPU addresses, cache base addresses, channel starts, performance counters, and slave channel addressing/status.

The macros do not encode access semantics. A register may be read-only, write-only, write-one-to-clear, self-clearing, double-buffered, locked behind an update-lock register, valid only during blanking, valid only after a clock is enabled, or protected by an indirect index/data protocol. Consumers must follow the block-specific sequencing in the display and AMDGPU code.

## Dependencies And Integration Points

This chunk depends on the generated AMDGPU DCE register ecosystem:

- `dce_11_0_sh_mask.h` supplies the field masks and shifts for many addresses defined here.
- Other DCE generation headers for `dce_6_0`, `dce_8_0`, `dce_10_0`, and `dce_11_2` provide parallel ASIC-generation layouts used by sibling driver files.
- AMDGPU register helpers (`RREG32`, `WREG32`, display-core `dm_read_reg`/`dm_write_reg`, and register-table macros) consume these addresses.
- The DRM display stack, AMD display core, audio support, hotplug/HPD handling, I2C/DDC EDID reads, power management, and virtualization/XDMA setup all depend on these constants mapping to the correct hardware addresses.

Important integration surfaces are:

- DCE 11.0 display core initialization and mode-setting: timing generator, memory input/compressor, transform, output pixel processor, regamma/CSC, link encoder, and hardware sequencer code include this header.
- Audio-over-HDMI/DP support: Azalia stream/endpoint/pin/converter registers are the address side of audio codec programming and status polling.
- Connector discovery and link management: HPD and I2C/DDC registers connect this file to monitor hotplug, EDID fetches, and DisplayPort/HDMI setup.
- Power and reset flows: DCFE, DCO, XDMA, Azalia memory power, VGA render, UNIPHY power, PLL update, and DMIF stutter/DPM registers participate in suspend/resume, clock gating, memory power gating, and ASIC golden-register programming.
- Virtual display paths: `mmCRTCV_*`, `mmBLNDV_*`, `mmDPGV*`, and `mmDCFEV_*` are consumed by virtual timing/blending and hardware-sequencer tables.
- Multi-instance display pipes: generic names plus per-pipe aliases let shared display code use offsets while ASIC-specific tables can name exact pipe instances.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. The compiler will happily accept an incorrect `#define`; the resulting failure appears only when a particular display, audio, HPD, I2C, virtual CRTC, PHY, or XDMA path uses that address.

High-risk address families include:

- `mmVGA_RENDER_CONTROL` and related VGA routing registers, because mistakes can leave legacy VGA decode enabled, route display status incorrectly, or interfere with memory-controller setup.
- PLL and UNIPHY registers, because wrong addresses can break link clocks, spread-spectrum programming, PHY power sequencing, or transmitter training.
- DMIF/DPG arbitration, watermark, urgency, stutter, and pstate registers, because display underflow, flicker, hangs, or power regressions may result from programming the wrong pipe or wrong control register.
- Azalia index/data, stream, endpoint, codec, DMA, and CRC registers, because audio failures can present as missing HDMI/DP audio, wrong sink info, format-change handling bugs, DMA underruns, or broken LPIB snapshots.
- HPD and I2C/DDC registers, because wrong constants can cause missed hotplug events, interrupt storms, EDID read failures, or incorrect connector detection.
- `mmCRTCV_*` virtual timing-generator registers, because virtual display mode programming relies on exact timing, blanking, status, update-lock, and color register addresses.
- XDMA master/slave pipe and channel registers, because bad addresses can corrupt remote/local surface addressing, channel starts, performance status, or memory/PCIe client configuration.

Repeated instance aliases are vulnerable to generated-copy mistakes. For example, most six-pipe DCE aliases are separated by fixed address strides, but virtual blocks and some debug/test registers do not always follow the same pattern. A single alias with the wrong instance address can work on one CRTC and fail only on another.

Index/data pairs need special care. Several names intentionally share the same numeric address, such as Azalia immediate-command index/data or VGA attribute/index/data aliases. The value alone is not enough to infer whether a caller is accessing an index, data, read, or write path; the surrounding protocol determines the meaning.

The chunk boundary is also relevant. Earlier chunks define the beginning and middle of `dce_11_0_d.h`, while this chunk only contains the tail. The final per-file merge should present this header as one generated DCE 11.0 address map, not as independent APIs split by these artificial line ranges.

## Test Signals

Validation is mostly build-time plus hardware/display behavior:

- AMDGPU and display-core builds should compile with DCE 11.0 register names used by `display/dc/dce110/*`, `display/dc/hwss/*`, `display/dc/irq/*`, `amdgpu/vi.c`, `pm/powerplay/hwmgr/polaris_baco.c`, and related code.
- Boot and mode-set testing on DCE 11.0 hardware should show stable display bring-up, correct CRTC timing, no unexpected underflow interrupts, no blanking/update-lock stalls, and correct frame/vblank counters.
- Multi-display tests should exercise all six pipe instance ranges so alias/stride errors are caught outside pipe 0.
- Virtual display paths should exercise `mmCRTCV_*`, `mmBLNDV_*`, `mmDPGV*`, and `mmDCFEV_*` through virtual timing-generator and hardware-sequencer flows.
- HDMI/DP audio tests should verify Azalia endpoint programming, codec sink info, stream format changes, multichannel/HBR paths, LPIB snapshots, and audio CRC/debug paths where available.
- Hotplug and EDID tests should verify HPD interrupt status/control/filtering and DC/generic I2C/DDC transactions across every connector.
- Suspend/resume, runtime power, and BACO-like transitions should verify DCFE/DCO/UNIPHY/Azalia/XDMA memory-power and clock-gating registers return to valid state.
- XDMA/MxGPU tests should verify clock gating, memory power, master/slave channel setup, remote address programming, and interrupt/status reporting.

Regression symptoms from bad constants include display underflows, black screens, modeset timeouts, incorrect virtual CRTC timing, broken HDMI/DP audio, missing or noisy HPD, EDID failures, link-clock or PHY training failures, resume-only display loss, VGA decode conflicts, XDMA transfer/channel failures, or failures limited to a specific display pipe instance.

## Cross-Chunk Notes

This is chunk 3 of 3 for `dce_11_0_d.h` in the current manifest. It begins at line 6044 with the tail of legacy VGA indirect constants and ends at line 7658 with the header guard close. Earlier chunks contain the first DCE 11.0 address families for the same generated namespace. The merge lane should combine all chunks into a single source-tree-aligned report for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h`.
