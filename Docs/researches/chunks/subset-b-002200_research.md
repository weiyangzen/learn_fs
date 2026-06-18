# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 120107-122526

## Purpose

This chunk is generated AMD DCN 4.1.0 register-field metadata for DPCSSYS CR2 PHY/DPCS registers. It contains no executable C logic; its exported contract is a set of C preprocessor constants that describe bit shifts and masks for 16-bit register fields. AMDGPU display/DPCS code consumes these constants with the matching register-offset headers to compose MMIO values, decode status, and build generated register tables.

The requested range contains 2,160 `#define` entries: 1,080 `__SHIFT` constants and 1,080 `_MASK` constants across 260 register names. The chunk starts at the field definitions for `DPCSSYS_CR2_RAWAONLANE3_DIG_CAL_IOFF_CODE`; that register's comment marker is on line 120106, just before the requested range. It then covers the tail of the raw always-on lane 3 block, a full generic `RAWAONLANEX` lane template block, most of the shared supervisor `SUPX` digital/analog/MPLL/RTUNE block, and the beginning of the generic `LANEX` ASIC lane override block. The final line is only the comment for `DPCSSYS_CR2_LANEX_DIG_ASIC_TX_ASIC_IN_0`, so that register's fields are outside this chunk.

Although the local tree is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph, filesystem, network, or storage behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocation paths, or direct I/O operations in this range. The public API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: mask for that field in the register value.

The main register families are:

- `DPCSSYS_CR2_RAWAONLANE3_DIG_*`: the tail of the lane-3 raw always-on PHY block. Fields cover calibration codes, RX DCC calibration ICM/IDF/QCM/QDF values for two banks, TX DCC bank address/data/control, MPLL bandgap delay control, signal-detect override/input, firmware configuration, lane transceiver mode override/input, RX signal-detect filtering, and TX/RX DCC bypass control.
- `DPCSSYS_CR2_RAWAONLANEX_DIG_*`: a generic lane-template version of the raw always-on lane controls. It includes analog front-end offset codes, RX adaptation values and FOM, DFE phase/data/bypass/error offsets, IQ phase adjust, MPLL coarse-tune, initial power-up done, adaptation status and controls, fast flags, CMNCAL MPLL/RCAL status, TX/RX override, loss-of-signal and signal-detect controls, RX override outputs, calibration codes, DCC banks, firmware configuration, lane mode, and DCC bypass state.
- `DPCSSYS_CR2_SUPX_DIG_*`: shared supervisor digital controls for ID code, reference clock overrides, MPLLA/MPLLB div and HDMI clock overrides, MPLLA/MPLLB override inputs, SSC peak and step-size fields, charge pump and gain-scale controls, supervisor and prescaler overrides, ASIC input mirrors, PMA version ID, MPLL power-control status/timers/calibration/DAC output, SSC spread type, clock/reset power-up timers, RTUNE configuration/status/set/stat registers, and analog override outputs/status.
- `DPCSSYS_CR2_SUPX_ANA_*`: analog supervisor controls for prescaler, RTUNE, bandgap, power measurement, pre-regulator references, vref generation force/probe, MPLLAB miscellaneous controls, override controls, ATB, central regulator, output clock, lock, CTR1-CTR7, and PMIX.
- `DPCSSYS_CR2_LANEX_DIG_ASIC_*`: the start of generic lane ASIC override and input fields. This chunk covers lane override input, TX override inputs 0-4, TX override output, RX override inputs 0-5, RX equalization override inputs 0-1, RX override output 0, and lane ASIC loopback input. The next `TX_ASIC_IN_0` register starts after the chunk.

Representative fields include calibration `DATA` values, `RX_DCC_CAL_*_CODE`, `TX_DCC_BYP_AC_CAP`, `RX_DCC_BYP_AC_CAP`, `RX_SIGDET_HF/LF`, `LANE_XCVR_MODE`, adaptation controls (`ADPT_EN`, `ADPT_CTL`, `ADAPT_DONE`, `FOM`, `DFE_TAP*`, `CTLE`, `VGA`, `ATT`), PLL controls (`MPLL*_FREQ`, `CLK_SEL`, `SSC_EN`, `PWR_CTL`, `LOCK`, timer and DAC fields), analog references and bandgap controls, RTUNE set/status values, TX/RX request/ack/data/rate/width/pstate controls, RX CDR/alignment/termination/inversion/low-power controls, EQ tap controls, and loopback enables.

Most masks in this chunk are 16-bit values with an `L` suffix, such as `0x0001L`, `0x00FFL`, `0x03FFL`, `0x1FFFL`, `0x8000L`, or `0xFFFFL`. Reserved fields are explicitly represented as masks and shifts, which helps generated table consumers preserve or decode full register layouts but also means callers must avoid treating reserved bits as programmable policy.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time token expansion:

1. AMDGPU display/DPCS code includes generated offset and shift/mask headers for the relevant ASIC generation.
2. Register helpers and generated register-table macros token-paste symbolic register and field names into field descriptors.
3. Runtime code reads or writes MMIO/register-indexed values using the paired register offsets and these field masks/shifts.
4. Hardware state machines implement the actual sequencing for PLL power-up, calibration, signal detection, RX adaptation, TX/RX override handshakes, and loopback. This header only exposes the bit positions needed by those code paths.

The prefix choice is part of the compile-time addressing model. `RAWAONLANE3` names lane 3 specifically, `RAWAONLANEX` and `LANEX` are generic lane templates, and `SUPX` is shared supervisor scope. Using the wrong prefix can still compile if a similarly named field exists, but it will target the wrong register instance or block.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It defines encodings for hardware-visible state in the DPCSSYS CR2 PHY:

- Calibration state: IOFF, ICONST, VREFGEN, RX DCC bank codes, TX DCC bank address/data/control, RTUNE calibration code, MPLL calibration enable/status, and analog DAC outputs.
- Link/PHY state: lane transceiver mode, signal-detect filter and override state, loss-of-signal masking, DCC bypass, TX/RX request/data/rate/width/pstate controls, reset/disable/low-power controls, termination and inversion controls, and loopback enables.
- Adaptation/equalization state: AFE and DFE adaptation enables/status, CTLE/VGA/ATT settings, DFE taps, slicer controls, phase adjust, FOM, fast flags, and EQ override tap fields.
- Shared clock and PLL state: reference clock selection, MPLLA/MPLLB frequency and clock output controls, SSC configuration, charge pump controls, lock/status/timer fields, DAC max range, power-up timers, and bandgap/reference/prescaler analog controls.
- Handshake and observation state: TX/RX ACK/result/status fields, ASIC input mirror fields, analog override output mirrors, CMNCAL status, RTUNE status, and PMA version/ID fields.

Persistence is hardware-defined. Configuration and override fields generally retain their values until driver reprogramming, power gating, suspend/resume, hotplug-driven retraining, GPU reset, or ASIC reset. Status, calibration, timer, lock, ACK, and mirror fields may be read-only, sticky, write-one-to-clear, self-clearing, valid only while the PHY block is powered, or valid only after a hardware calibration sequence. The generated mask header does not encode access direction, reset values, side effects, or required sequencing.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated ASIC register-header convention. For the DPCSSYS CR2 names visible in this chunk, the matching register offsets are visible in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`; for example `ixDPCSSYS_CR2_RAWAONLANE3_DIG_CAL_ICONST_CODE`, `ixDPCSSYS_CR2_SUPX_DIG_IDCODE_LO`, and `ixDPCSSYS_CR2_LANEX_DIG_ASIC_TX_ASIC_IN_0` are defined there. Consumers need those offsets plus this `dcn_4_1_0_sh_mask.h` field layout to address and manipulate the correct register bits.

Important integration points are AMDGPU display PHY/link bring-up and diagnostics:

- DisplayPort/HDMI PHY initialization and training code that configures PLLs, lane mode, TX/RX adaptation, equalization, and signal detection.
- Power-management and reset paths that sequence bandgap, reference clock, MPLL, prescaler, and PHY power-up timers.
- Calibration and tuning flows that read CMNCAL, RTUNE, RX DCC, TX DCC, VREFGEN, IOFF, and analog DAC/status values.
- Debug, manufacturing, bring-up, or firmware-assisted paths that force override inputs or inspect override outputs and ASIC mirror inputs.
- Generated register-list infrastructure that relies on exact field names and mask/shift pairs to keep DCN 4.1.0 source code synchronized with the hardware register database.

Because this is generated silicon ABI metadata, changes must stay synchronized with the authoritative AMD register source and any paired offset/base-index headers. Manual edits in this file can silently desynchronize the driver from hardware even when all C code still builds.

## Risks And Edge Cases

- The constants are untyped macros. A wrong shift or mask compiles cleanly but can corrupt neighboring hardware fields or decode misleading status.
- Many fields control analog/PHY behavior. Incorrect values can cause link-training failure, unstable clocking, no display, intermittent signal detect, degraded eye margins, or power-state hangs.
- Several registers expose override-enable plus override-value pairs. Setting a value without the corresponding enable bit, or leaving an override enabled after diagnostics, can make hardware ignore normal state-machine control.
- Status and handshake fields such as ACK, DETRX result, adaptation status, lock status, RTUNE status, and analog override outputs may have timing-sensitive validity windows. Blind polling or writes without the expected hardware sequence can produce stale or misleading observations.
- Reserved bit definitions are present. Generated consumers may need them for table completeness, but operational code should avoid programming reserved bits unless the hardware database explicitly requires a preserved value.
- Repeated `MPLLA`/`MPLLB`, `RAWAONLANE3`/`RAWAONLANEX`, and TX/RX override layouts are easy to confuse. A copy/paste prefix error may only fail for one PLL, one lane, or one link rate.
- The chunk boundaries are not semantic. `CAL_IOFF_CODE` starts just before the chunk comment-wise, and `LANEX_DIG_ASIC_TX_ASIC_IN_0` is only introduced at the last line. Adjacent chunks are required for whole-block conclusions.
- The mask width is mostly 16 bits while AMD display register helpers often operate on wider integer values. Callers must still preserve unrelated high bits and use the proper indexed-register access width for the DPCS block.

## Test Signals

Useful validation signals are mostly generated-header consistency checks plus hardware-oriented display PHY testing:

- Build AMDGPU display code that includes this header with the paired DPCS offset header. Missing, renamed, or mismatched field symbols should fail in generated register tables or register-helper uses.
- Mechanically compare this range against AMD's authoritative DCN 4.1.0/DPCS register database. Treat line 120107 and line 122526 as partial-boundary artifacts.
- Check that every `__SHIFT` macro has a matching `_MASK` macro with the same register and field name. This chunk has an even 1,080/1,080 split, which is a useful coarse signal.
- Validate repeated layouts: `MPLLA` vs `MPLLB` fields, raw lane 3 vs generic lane X DCC/signal-detect controls, and TX/RX override registers should have intentionally mirrored field sets where the hardware block is mirrored.
- Exercise display link bring-up across supported connectors and rates, including cold boot, hotplug, mode changes, suspend/resume, and GPU reset. Watch for link-training failures, display blanking, PLL lock timeouts, and unstable signal detect.
- Run PHY calibration and tuning diagnostics, if available, and verify plausible RTUNE, CMNCAL, DCC, VREFGEN, and MPLL status values.
- Test override/debug paths carefully: enable and clear TX/RX, lane mode, DCC bypass, signal-detect, loopback, EQ, PLL, and analog overrides; verify hardware returns to normal autonomous control afterward.
- Inspect kernel logs or display diagnostics for timeout/error counters around MPLL power control, adaptation completion, ACK handshakes, and RTUNE status after stress cycles.

## Cross-Chunk Notes

The previous chunk contains earlier `DPCSSYS_CR2_RAWAONLANE3` definitions, including the comment for the first register completed here. The next chunk continues `DPCSSYS_CR2_LANEX_DIG_ASIC_TX_ASIC_IN_0` and the rest of the generic lane ASIC input/status block. The final per-file research should reconcile adjacent DPCSSYS chunks before making whole-file claims about all DCN 4.1.0 shift/mask definitions.
