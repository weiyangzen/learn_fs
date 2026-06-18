# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h lines 9629-11957

## Purpose

This chunk is a generated AMD DPCS 4.2.2 register-offset header slice for DCN 3.1.5 display PHY programming. It contains no executable C code. Its interface is a dense set of preprocessor constants that name hardware register indexes and MMIO register offsets used by AMDGPU display code.

The requested range contains 2,318 `#define` entries. It starts near the end of the CR3 indirect DPCS namespace with 162 `ixDPCSSYS_CR3_*` offsets, covers the complete `dpcssys_cr4_rdpcstxcrind` address block with 2,146 `ixDPCSSYS_CR4_*` offsets, then ends with ten `regRDPCSPIPE*_RDPCSPIPE_PHY_CNTL6` direct-register aliases plus their base-index constants. The final comment notes that the RDPCSPIPE aliases are a DCN315-specific hack because RDPCSPIPE has only two physical instances even though higher-level display code exposes more pipe/transmitter ids.

Although this file sits under a local `ceph-client` source mirror, this range is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, includes, or direct register accesses in this chunk. The exported API is the generated macro naming scheme:

- `ixDPCSSYS_CR3_*` and `ixDPCSSYS_CR4_*` name indirect DPCS control-register indexes inside the CR3/CR4 register spaces.
- `regRDPCSPIPE<n>_RDPCSPIPE_PHY_CNTL6` names direct MMIO offsets for the RDPCSPIPE `PHY_CNTL6` register instances.
- `*_BASE_IDX` gives the register base segment index used by AMD display register-table helpers.

The CR3 portion is the tail of the CR3 lane-X/register-X block. It covers analog TX/RX override readbacks and raw lane-X registers: PCS transfer overrides, RX adaptation feedback, lane number, ATE/test overrides, FSM fast-control/status registers, IRQ status/clear/mask registers, PMA transfer registers, TX/RX control registers, and additional PCS ATE overrides.

The CR4 block is the main body of this chunk and begins at `ixDPCSSYS_CR4_SUP_DIG_IDCODE_LO` offset `0x0000`. Major macro families include:

- `SUP_DIG_*`, `SUP_ANA_*`, `SUPX_DIG_*`, and `SUPX_ANA_*`: supervisor/common control, ID, refclk, MPLLA/MPLLB override and ASIC input registers, spread-spectrum clocking, PLL charge-pump and gain settings, bandgap/reference timing, RTUNE configuration/status, analog override outputs, and supervisor analog controls.
- `LANE0` through `LANE3` and `LANEX`: lane-level ASIC, TX power, RX power/VCO/CDR/adaptation, RX statistics, MPHY, digital analog override, analog TX, and analog RX offset namespaces. Lanes 1, 2, and `LANEX` include the larger RX-side set, while lanes 0 and 3 expose a narrower TX/stat-oriented subset in this generated map.
- `RAWCMN_DIG_*`: raw common DPCS controls for MPLLA/MPLLB override and bandwidth/SSC controls, lane FSM extension, common MPLL state, TX calibration, SRAM init, OCLA/debug, PCS/FW ID codes, always-on common RTUNE values, power-gate/supervisor/resource overrides, VREF stats, and reference range/misc configuration.
- `RAWLANE0` through `RAWLANE3` and `RAWLANEX`: repeated raw-lane PCS/FSM/IRQ/PMA/TX/RX/ATE register windows. Each lane has PCS transfer inputs/outputs, RX adaptation ACK/FOM, directed TX coefficient feedback, lane numbering, PH2 calibration, fast RX startup/adaptation/calibration controls, common calibration status, IRQ status/clear/mask registers, PMA lane/supervisor/TX/RX transfer registers, MPHY overrides, TX/RX control/status, and ATE/test override registers.
- `RAWAONLANE0` through `RAWAONLANE3` and `RAWAONLANEX`: always-on lane calibration/status registers. These name AFE/DFE offsets, RX phase and FOM values, MPLL coarse tune, initial power-up/adaptation status, fast flags, slicer and calibration controls, signal-detect and LOS filtering, firmware configuration, DCC calibration/bank access, lane transceiver-mode override/readback, and TX DCC configuration.
- `RAWMEM_DIG_ROM_CMN0_B0_R0` and `RAWMEM_DIG_RAM_CMN0_B0_R0`: raw memory windows in the CR4 indirect space.

The RDPCSPIPE tail maps `RDPCSPIPE0`, `RDPCSPIPE2`, and `RDPCSPIPE4` to offset `0x2d73`, while `RDPCSPIPE1` and `RDPCSPIPE3` map to offset `0x2e4b`; all use base index `2`. This deliberate aliasing is the mechanism described by the local TODO/comment.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of AMDGPU display register tables:

1. DCN 3.1.5 resource code includes `dpcs/dpcs_4_2_2_offset.h` together with `dpcs/dpcs_4_2_2_sh_mask.h`.
2. Register-list macros and helper macros such as `SR`, `SRI`, `SRI_IX`, `LE_SF`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use token-pasted register names to bind these offsets with matching shift/mask metadata.
3. Runtime display code performs actual sequencing for link encoder setup, DP/HDMI PHY programming, link training, USB-C DP alt-mode queries, lane power transitions, calibration, and debug reads.

The macros in this chunk only say where registers are addressed. They do not encode whether a register is read-only, write-only, clear-on-write, self-clearing, latched, power-domain dependent, or safe to access while firmware owns the PHY.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names hardware-visible state and control surfaces:

- Common/supervisor state for reference clocks, MPLLA/MPLLB programming, spread-spectrum settings, PLL power/calibration timers, bandgap/reference controls, RTUNE results, SRAM init, firmware IDs, and raw common power/resource overrides.
- Lane state for TX and RX request/reset/power-state behavior, data enable, lane width/rate/pstate handshakes, PLL selection, TX DCC, RX VCO/CDR, RX adaptation, DFE/CTLE/VGA/ATT values, signal-detect/LOS filtering, PH2 calibration, and MPHY PWM/termination controls.
- Interrupt and handshake state for RX/TX reset/request/rate/pstate/adaptation events, lane transceiver-mode changes, PH2 calibration request/disable, serial loopback, DCC on-demand events, PMA ACKs, and fast FSM status.
- Debug/test state for ATE overrides, OCLA/UPCS observation controls, LBERT controls and errors, directed TX coefficient feedback, analog test bus controls, and raw ROM/RAM windows.

Persistence is entirely hardware-defined. Configuration registers can survive until rewritten by link training, modeset, PHY reset, power gating, suspend/resume restoration, GPU reset, or ASIC reinitialization. Status, ACK, IRQ, calibration, and statistic registers may be transient, latched, clear-on-write, or valid only while the relevant DPCS common/lane power and clock domains are active.

## Dependencies And Integration Points

This generated offset header must stay synchronized with the matching DPCS 4.2.2 shift/mask header and AMD's authoritative register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h` supplies field shifts and masks for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes this header and defines the DCN315 DPCS base segments. In that file, DPCS segment bases include `DPCS_BASE__INST0_SEG0` through `DPCS_BASE__INST0_SEG5`, and the DPCS 4.2.2 headers are paired with `dcn_3_1_5` DCN register headers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` lists `RDPCSPIPE_PHY_CNTL6` in `DPCS_DCN31_REG_LIST(id)` and lists its `RDPCS_PHY_DPALT_*` fields in `DPCS_DCN31_MASK_SH_LIST`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c` reads `RDPCSPIPE_PHY_CNTL6` in legacy USB-C DP alt-mode paths on Yellow Carp B0-style hardware for transmitters that do not use `RDPCSTX_PHY_CNTL6`.
- Adjacent generated DPCS 4.2.0 and 4.2.3 offset headers expose very similar CR3/CR4 and RDPCSPIPE layouts, making them useful for generator-consistency checks but not substitutes for this ASIC-specific file.

Behaviorally, this chunk integrates with display link bring-up, PHY lane setup, RX adaptation and calibration, DP/HDMI rate and lane-count programming, USB-C DP alt-mode handling, hotplug/modeset flows, suspend/resume restore, firmware handoff, and low-level PHY diagnostics.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset can compile cleanly and only fail at runtime as a bad register read, corrupt write, stuck poll, or display link failure.
- The file is generated. Manual edits risk divergence from AMD's register database, the companion shift/mask header, firmware expectations, and silicon documentation.
- The chunk starts mid-CR3 namespace. Whole-file consumers must reconcile the preceding CR3 chunks before claiming complete CR3 coverage.
- CR4 contains repeated lane and raw-lane windows with similar register names and regular offset strides. A generator slip in only one lane can break one physical lane while leaving adjacent lanes functional.
- Lane-specific and `LANEX`/`RAWLANEX` macros are not automatically interchangeable. Code that combines a lane-X offset with a concrete-lane mask, or a CR3 offset with a CR4 offset, can silently target the wrong register.
- The RDPCSPIPE aliases intentionally map five logical instances onto two physical offsets. The local TODO says this should be verified for DCN315, so new ASIC support must not assume these aliases are generally correct.
- The RDPCSPIPE registers are used in a legacy DP-alt path that comments about avoiding hangs when querying through DMCUB is unavailable. Incorrect offsets or unsafe access ordering can affect USB-C link capability detection and lane-count limiting.
- Common PLL, spread-spectrum, bandgap, RTUNE, RX CDR/VCO, DCC, PH2 calibration, and DFE/CTLE/VGA/ATT registers are analog-sensitive. Mistakes may reproduce only at certain link rates, lane counts, boards, cables, sinks, voltage/temperature corners, or after suspend/resume.
- IRQ status, clear, and mask registers are side-effect-sensitive. Confusing status offsets with clear offsets can create repeated interrupts, missed events, or link-training timeout paths.
- Raw memory windows and ATE/OCLA/test overrides are high-risk diagnostic surfaces. Production code should access them only through documented sequences and preserve reserved or firmware-owned state.

## Test Signals

Useful validation combines generated-header consistency checks with real display behavior:

- Build AMDGPU display support for DCN315/DPCS 4.2.2. Missing or renamed symbols should surface in resource table, link encoder, and register helper initialization.
- Mechanically compare this offset range against the authoritative DPCS 4.2.2 register source and against `dpcs_4_2_2_sh_mask.h`, ensuring every expected register has matching field definitions where fields exist.
- Compare CR4 repeated `LANE*`, `RAWLANE*`, and `RAWAONLANE*` windows for expected offset stride and intentional asymmetries, especially the narrower lane 0/3 RX surface versus lane 1/2/`LANEX`.
- Cross-check DPCS 4.2.0 and 4.2.3 generated headers for expected CR3/CR4 and RDPCSPIPE alias stability while preserving ASIC-specific differences.
- Exercise DP and HDMI link bring-up across available PHYs, lanes, link rates, and power states. Watch for PLL lock failures, RX adaptation failures, false lane readiness, stuck request/ack bits, and DCC/calibration timeouts.
- Test USB-C DP alt-mode paths on hardware using the RDPCSPIPE aliases. Good signals are correct DP4-vs-two-lane detection, correct `DPALT_DISABLE` handling, and no hangs in the legacy fallback path.
- Run hotplug, modeset, blank/unblank, suspend/resume, runtime power management, and GPU reset tests to catch persistence and restoration issues around CR4 common/lane state.
- Use register dumps on failures to verify that decoded CR4 offsets align with expected supervisor, raw common, raw lane, always-on lane, IRQ, PMA, PCS, CDR/VCO, adaptation, and DCC register values.

## Cross-Chunk Notes

The previous chunk owns the earlier CR3 CR-indirect offset definitions. This chunk resumes at CR3 lane-X analog and raw-lane-X offsets, then contains the full CR4 `dpcssys_cr4_rdpcstxcrind` address block from `0x0000` through `0xe0c8`, followed by the RDPCSPIPE `PHY_CNTL6` direct-register aliases and the header guard close. The final per-file report should merge this with earlier chunks before making complete claims about CR0 through CR3 coverage or about the full DPCS 4.2.2 offset header.
