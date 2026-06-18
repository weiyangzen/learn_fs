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
