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
