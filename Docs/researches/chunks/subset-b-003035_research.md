# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 73848-76453

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 1,945 `#define` macros across 2,606 source lines. There are no C functions, structs, enums, global objects, locks, allocations, or executable statements in this range.

The range covers DWC E12MP PHY X4 North/South X4 instance 1 register-field layout macros. It starts inside the common digital memory table at `DWC_E12MP_PHY_X4_NS_X4_1_RAWCMN_DIG_MEM_CMN4_B6_R21`, continues through common memory rows for `CMN4`, `CMN5`, and most of `CMN6`, defines common digital control and MPLL override fields, then moves into lane 0 and lane 1 PHY control/status definitions. The boundary is artificial: the chunk begins after the comment for `RAWCMN_DIG_MEM_CMN4_B6_R21`, and ends after only the shift definitions for `RAWLANE1_DIG_PCS_XF_RX_PCS_IN_4`; the matching masks for that final register are in the following chunk.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of AMD's generated NBIO 6.1 hardware register interface. For each named register it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit index used to position a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update that field.

The companion NBIO 6.1 offset and default headers provide matching register addresses and reset/default values. Runtime AMDGPU code combines those addresses with these field constants through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, indexed-register accessors, and SOC/NBIO-specific read/write paths.

This chunk specifically describes low-level PHY programming for the DWC E12MP PCIe/display PHY exposed through NBIO. The represented state covers common PHY memory data words, common digital control, MPLLA/MPLLB bandwidth and spread-spectrum-clocking overrides, per-lane PCS transmit/receive handshake and override signals, lane FSM monitor and fast-calibration controls, always-on analog/adaptation calibration state, IRQ status/clear/mask fields, PMA cross-function handshake fields, and lane TX/RX control status.

## Important Macro Families

The `RAWCMN_DIG_MEM_*` block is a large memory-map style region:

- `RAWCMN_DIG_MEM_CMN4_B6_R21` through `CMN4_B7_R31` expose 16-bit `DATA` fields for the tail of common memory bank 4.
- `RAWCMN_DIG_MEM_CMN5_B0_R0` through `CMN5_B7_R31` expose the full common memory bank 5, again as 16-bit `DATA` fields.
- `RAWCMN_DIG_MEM_CMN6_B0_R0` through `CMN6_B6_R31` expose most of common memory bank 6.

The common digital control and PLL block follows:

- `RAWCMN_DIG_CMN_CTL` defines common reset and enable control bits, including `RESET`, `RX_EN`, and `TX_EN`.
- `RAWCMN_DIG_MPLLA_BW_OVRD_IN` and `RAWCMN_DIG_MPLLB_BW_OVRD_IN` define override value/enable fields for MPLL bandwidth selection.
- `RAWCMN_DIG_MPLLA_SSC_CTL_OVRD_IN`, `RAWCMN_DIG_MPLLB_SSC_CTL_OVRD_IN`, and related `SSC_EN_OVRD_IN` registers define spread-spectrum clocking step, direction, enable, and override-enable fields for both MPLL paths.

The `RAWLANE0_DIG_PCS_XF_*` block describes the PCS interface for lane 0:

- TX override/input registers cover power state, low-power detect, width, rate, MPLL selection/enables, master MPLL state, override enable, reset/request override controls, detector request override controls, voltage boost, and current boost level.
- TX output/status registers expose acknowledgment, detect-result, and enable-control bits.
- RX override/input registers cover rate, width, power state, low-power detect, adaptation enables, reset/request override controls, VCO load/low-frequency overrides, RX loss-of-signal threshold override, reference-load override, adaptation request, continuous adaptation, and offset-cancel continuation controls.
- RX PCS input registers carry the non-overridden request/rate/width/power/adaptation/reset signals plus reference-load, VCO-load, and equalization settings such as attenuation, VGA gains, CTLE boost/pole, and DFE tap 1.
- RX output/status and adaptation registers expose acknowledgment, enable control, adaptation acknowledgment, figure-of-merit, and directed TX pre/main/post cursor values.

The lane 0 FSM block describes firmware or hardware calibration sequencing:

- `RAWLANE0_DIG_FSM_FSM_OVRD_CTL` provides override enables for startup calibration, RX adaptation, AFE/DFE calibration, bypass calibration, reference-level calibration, IQ calibration, AFE/DFE adaptation, supervisory steps, TX common mode, TX RX detect, RX power-up, VCO wait, and VCO calibration.
- `RAWLANE0_DIG_FSM_MEM_ADDR_MON` and `RAWLANE0_DIG_FSM_STATUS_MON` expose monitor/status information.
- The `RAWLANE0_DIG_FSM_FAST_*` registers provide fast-path values or enablement for the same RX/TX calibration substeps.
- `RAWLANE0_DIG_FSM_CMNCAL_STATUS` exposes common calibration status, including done/fail style fields.

The lane 0 always-on and adaptation block describes calibrated analog state:

- `RAWLANE0_DIG_AON_AFE_*`, `DFE_*`, `RX_PHSADJ_*`, and related registers define offset or calibration values for attenuation, CTLE, VGA, DFE summer/phase/data/bypass/error paths, slicer controls, and RX phase adjustment.
- `RAWLANE0_DIG_AON_MPLLA_COARSE_TUNE`, `MPLLB_COARSE_TUNE`, `RTUNE_RX_VAL`, `RTUNE_TXDN_VAL`, and `RTUNE_TXUP_VAL` expose tuning values.
- `RAWLANE0_DIG_AON_INIT_PWRUP_DONE`, `RX_ADAPT_DONE`, `LANE_CMNCAL_STATUS`, and `FAST_FLAGS` expose lane initialization, adaptation, common calibration, and fast-calibration state.
- `RAWLANE0_DIG_AON_ADPT_CTL_0` through `ADPT_CTL_7` are 16-bit adaptation-control data words.

The lane 0 IRQ/PMA/TX/RX control block provides operational handshakes:

- `RAWLANE0_DIG_IRQ_CTL_*` defines reset-return request, RX reset/request/rate/pstate/adaptation IRQ status, matching clear registers, and an IRQ mask register.
- `RAWLANE0_DIG_PMA_XF_*` defines lane, supervisory, TX, and RX PMA interface override/input/output fields plus lane RTUNE control.
- `RAWLANE0_DIG_TX_CTL_*` and `RAWLANE0_DIG_RX_CTL_*` define TX/RX FSM clock/control, RX loss-of-signal masking, RX data-enable override, and status for offset-cancel and adaptation continuation.

The chunk then starts the same PCS interface pattern for lane 1:

- `RAWLANE1_DIG_PCS_XF_TX_*` and `RX_*` definitions mirror lane 0 for PCS TX/RX rate, width, power state, reset/request, override, detector, VCO, LOS threshold, reference-load, adaptation, and equalization fields.
- The line range ends at `RAWLANE1_DIG_PCS_XF_RX_PCS_IN_4` after `EQ_CTLE_POLE`, `EQ_DFE_TAP1`, and `RESERVED_15_11` shift definitions. The masks for those three fields are outside this chunk.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. Consumers depend on the exact register names, field names, shifts, and masks remaining synchronized with the NBIO 6.1 offset/default headers and with the underlying hardware register database.

The constants are untyped preprocessor integer literals, typically using an `L` suffix for masks. They encode only bit positions and bit masks. They do not encode access width, reset value, read/write permission, sticky status behavior, write-one-to-clear semantics, ordering requirements, clock-domain restrictions, or PHY side effects. Driver code must obtain those semantics from the hardware specification and from the surrounding NBIO/PHY access path.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU or power-management code selects an NBIO/DWC PHY register offset from the companion generated headers.
2. The code reads a hardware value, extracts fields with the `__SHIFT` and `_MASK` constants, or composes a new value through generated register helpers.
3. The decoded value informs link, PHY, calibration, interrupt, or diagnostics policy; writes update override, clear, mask, tuning, or control fields in hardware.

Likely flows using this chunk include PHY initialization, firmware-assisted PHY table programming, PCIe or display link bring-up, MPLL bandwidth/SSC configuration, lane reset/request handshakes, rate/width/power-state transitions, RX detector and low-power handling, RX adaptation and equalization, AFE/DFE calibration, PMA/PCS interface validation, interrupt masking/clearing, and low-level debug dumps of PHY state.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO 6.1 DWC E12MP common and lane registers. Persistence is controlled by the GPU/NBIO reset domain, PHY reset, lane reset, power-gating and clock-gating state, firmware initialization, suspend/resume save-restore, and explicit driver writes.

The common memory `DATA` registers model table-like 16-bit state. These values may represent firmware-provided or hardware-generated PHY configuration data, and they should be treated as tightly coupled to the generated offset/default headers rather than as ordinary software arrays.

Override registers have persistent hardware effect until reset or until software clears their enable fields. Examples include MPLLA/MPLLB bandwidth and SSC override enables, PCS TX/RX override enables, reset/request override controls, VCO/reference-load overrides, LOS threshold override, adaptation request override, and data-enable overrides. Incorrectly leaving override-enable bits asserted can force the PHY away from normal hardware or firmware control.

Status and monitor registers represent live PHY state rather than durable configuration. Examples include PCS ACK/result fields, FSM status, calibration done/fail information, adaptation figure-of-merit, fast flags, initialization power-up done, common calibration status, IRQ pending fields, PMA output handshakes, and continuous adaptation/off-cancel status. These values can change asynchronously with link state, clock state, lane training, or firmware activity.

Clear and mask registers have side-effect semantics. The `RAWLANE0_DIG_IRQ_CTL_*_CLR` registers are not normal storage fields; writes are expected to clear pending interrupt state. The IRQ mask register controls whether lane events propagate. The generated masks only identify the bits; call sites must preserve correct clear/write ordering and avoid losing diagnostic evidence.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 6.1 register database and must stay aligned with sibling generated headers:

- `nbio_6_1_offset.h` supplies matching offsets for the same `DWC_E12MP_PHY_X4_NS_X4_1_*` register names.
- `nbio_6_1_default.h` supplies matching default values for many of these registers.
- AMDGPU register helper macros consume these shift/mask constants for field extraction and update.

Direct include users in this tree include `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`, which include the NBIO 6.1 generated register headers as part of the Vega-era power-management hardware-manager register set. The broader integration surface is the AMDGPU NBIO, PCIe/link, display/PHY, and power-management code that programs or diagnoses PHY state.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem control flow.

## Risks And Edge Cases

- Generated mask or shift drift can compile cleanly while causing software to read, preserve, clear, or set the wrong hardware bit. In this chunk the highest-risk fields are override enables, reset/request controls, MPLL/SSC controls, IRQ clear/mask fields, PMA/PCS handshakes, and adaptation/calibration controls.
- The chunk boundaries are mid-register-family. The beginning omits the comment line for `RAWCMN_DIG_MEM_CMN4_B6_R21`, and the end omits the masks for `RAWLANE1_DIG_PCS_XF_RX_PCS_IN_4`. Merge/reconciliation must combine adjacent chunks before judging register completeness.
- The common memory table is intentionally repetitive. Mechanical `DATA` definitions should be checked for address/row continuity against offsets rather than manually interpreted as independent semantic registers.
- Per-lane definitions are intentionally mirrored. A lane 0/lane 1 mismatch can indicate real generated database drift, but the end-of-chunk truncation of lane 1 must not be misread as a hardware asymmetry.
- Override fields can wrest control from hardware or firmware sequencers. Wrong values can leave lanes in reset, force incorrect rate/width/power-state signals, disable normal adaptation, or select the wrong MPLL behavior.
- PLL bandwidth and spread-spectrum-clocking fields affect link clocking. Incorrect programming can cause unstable links, failed training, clock compliance issues, or hard-to-reproduce resume failures.
- RX adaptation, AFE/DFE, CTLE, VGA, slicer, phase, and VCO fields interact with analog calibration state. Incorrect masks can make debug output misleading or actively degrade signal integrity if written.
- IRQ clear and mask fields can lose event evidence or create repeated interrupts if treated as ordinary read/write storage.
- Status fields are live and may change while being sampled. Diagnostics should tolerate races with link retrain, power transitions, firmware calibration, and reset.

## Test Signals

- Build AMDGPU configurations that include NBIO 6.1/Vega register headers. Compile failures catch missing or renamed generated symbols, but not incorrect bit positions.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: offset-to-field pairing, shift/mask width checks, non-overlap checks, default-value compatibility, and continuity of `CMN4`/`CMN5`/`CMN6` memory rows.
- Compare lane 0 and lane 1 PCS field layouts for mirrored registers, accounting for this chunk's line-boundary truncation at `RAWLANE1_DIG_PCS_XF_RX_PCS_IN_4`.
- Exercise PHY/link bring-up on affected AMD GPUs and verify stable negotiated speed/width, successful reset/request handshakes, and expected MPLL/SSC behavior.
- Validate suspend/resume and GPU reset paths for restoration of PHY defaults, release of override-enable bits, and absence of stuck lane reset or request state.
- Use debug or register-dump tooling to verify PCS ACK/result, FSM status, calibration done/fail, adaptation figure-of-merit, PMA output, and fast-flag fields decode consistently with observed link behavior.
- Exercise lane IRQ paths where available: trigger RX reset/request/rate/pstate/adaptation events, confirm pending bits decode, clear bits clear only the intended events, and mask bits suppress delivery without corrupting status.
- For generated data review, diff this chunk against adjacent NBIO/DPCS PHY generations to spot accidental generator drift in repeated `DATA`, override, adaptation, IRQ, and PMA/PCS field patterns.
