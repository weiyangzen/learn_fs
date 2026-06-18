# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 47693-50047

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for the CR2 register instance. It contains only C preprocessor constants: `__SHIFT` macros define field bit positions and `_MASK` macros define the corresponding field masks. The range starts in the middle of `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`, covers the remainder of CR2 lane 1 RX power, VCO calibration, CDR/DPLL, RX adaptation, RX statistics, MPHY, digital analog override/status, and raw analog TX/RX controls, then enters CR2 lane 2 and covers its ASIC override/status interface, TX power control, TX clock/LBERT fields, RX power control, and the first RX VCO calibration/status registers. It ends in the middle of `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_RX_VCO_STAT_1`.

## Purpose

The header provides compile-time bitfield metadata used by AMDGPU display/PHY code when programming DPCS 4.2.2 hardware. Consumers pair these masks and shifts with matching address macros from the companion DPCS offset header and with AMD display register-access helpers to assemble read-modify-write values without open-coding numeric bit positions.

In this range, the fields describe:

- CR2 lane 1 RX power-state programming for P0S, P1, and P2, including analog AFE/clock/deserializer/CDR enables, VCO reset/calibration/continuous-calibration controls, digital clock enables, and RX power-up timing.
- CR2 lane 1 RX VCO calibration controls, calibration timing, and status, including frequency-tune start values, calibration step controls, skip bits, startup/update/counter timing, VCO FSM state, calibration-done status, and DPLL reset status.
- CR2 lane 1 RX alignment, LBERT, CDR, DPLL, adaptation, statistics, MPHY, digital analog override, and raw analog TX/RX bit layouts.
- CR2 lane 2 ASIC-facing override and status registers for lane, TX, RX, RX equalization, RX CDR/VCO, cross-lane clock/shift handshake, and OCLA debug enablement.
- CR2 lane 2 TX power-state and power-up timing fields, DCC CR-bank/DAC controls, TX clock alignment, TX LBERT, RX power-state controls, RX power-up timing, and the start of RX VCO calibration status.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or callable APIs in this chunk. The public interface is the generated macro naming contract:

- `DPCSSYS_CR2_LANE*_...__FIELD__SHIFT`: bit offset for `FIELD`.
- `DPCSSYS_CR2_LANE*_...__FIELD_MASK`: bit mask for the same field.
- Register delimiter comments such as `//DPCSSYS_CR2_LANE1_DIG_RX_ADPTCTL_ADPT_CFG_0` mark groups that correspond to address macros in `dpcs_4_2_2_offset.h`.

Notable CR2 lane 1 groups include:

- `DIG_RX_PWRCTL_*`: RX P-state enable fields and timing controls for AFE, clock regulator, analog clock, deserializer, CDR, VCO reset/calibration, continuous calibration, fast-start timing, rate timing, CDR-enable timing, deserializer enable/disable timing, and reserved-bit preservation.
- `DIG_RX_VCOCAL_*`: VCO calibration control, timing, and status registers, including `INT_GAIN_CAL_*`, `RX_VCO_OVRD_SEL`, `RX_VCO_FREQ_RST`, `RX_VCO_CAL_RST`, `RX_VCO_CONTCAL_EN`, `DPLL_CAL_UG`, `DTB_SEL`, frequency tune values, calibration skip bits, startup/update/counter timing, VCO FSM state, calibration done, and DPLL frequency reset status.
- `DIG_RX_CDR_*` and `DIG_RX_DPLL_*`: CDR enable/status, bias, phase, calibration, and DPLL frequency/bound fields that support receiver clock recovery.
- `DIG_RX_ADPTCTL_*`: adaptation configuration, training-pattern generator fields, enable masks for CTLE/VGA/ATT/DFE/eye/TGG logic, threshold and adaptation step controls, reset controls, ATT/VGA/CTLE/DFE status codes, slicer/DAC offsets, error slicer levels, DAC control selections, and adaptation CR-bank address/data fields.
- `DIG_RX_STAT_*`: statistic load values, data masks, CR1A/CR1B pattern/mask controls, statistic/correlation source selectors, sample/count enable bits, seven statistic counters, comparator clock controls, extended pattern controls, valid-loss clearing, stop control, and sample-done bits.
- `DIG_MPHY_*`: low-speed MPHY RX PWM, termination, and analog PWM clock stability fields.
- `DIG_ANA_*` and raw `ANA_*`: digital outputs toward analog TX/RX blocks, analog status readback, RX termination/signal-detect/DAC/slicer/IQ/phase controls, TX DCC DAC/equalization/fast-start/loopback controls, analog TX power/ATB/termination/misc fields, and analog RX clock/CDR/slicer/power/squelch/calibration/ATB/reserved registers.

Notable CR2 lane 2 groups include:

- `DIG_ASIC_*_OVRD_IN`, `DIG_ASIC_*_OVRD_OUT`, and `DIG_ASIC_*_ASIC_IN/OUT`: ASIC-side override enables and values for TX/RX requests, resets, data enables, P-state/rate/width, lane inversion/disable, RX CDR tracking and SSC, RX alignment, low-power detect, term controls, EQ fields, CDR/VCO load values, TX cursors, TX/RX acknowledgements, adaptation status, valid/data readback, cross-lane repeater/digital-clock/shift handshakes, and OCLA clock/data enablement.
- `DIG_TX_PWRCTL_*`: TX P0/P0S/P1/P2 enables for refgen, VCM hold, analog/digital clocks, reset, serial/data, RX-detect, VBOOST allowance, and DCC calibration; power-up timing; DCC CR-bank address/data; DCC DAC control/range/selection/ack/address; TX clock alignment; and TX LBERT control.
- `DIG_RX_PWRCTL_*` and `DIG_RX_VCOCAL_*`: lane 2 mirrors of the RX power-state, power-up timing, VCO calibration control/time/status fields seen for lane 1 earlier in this chunk.

## Control Flow

This header contributes no runtime control flow. Runtime sequencing lives in AMDGPU display and PHY code that uses these constants to read, mask, shift, and write indexed DPCS CR registers.

The implied hardware sequences in this chunk are sensitive PHY bring-up and diagnostic paths: RX P-state changes, CDR/VCO/DPLL setup, RX adaptation, statistic sampling, MPHY low-speed handling, analog override programming, lane 2 ASIC handshakes, TX power-state entry/exit, TX DCC programming, TX clock alignment, LBERT test enablement, and RX VCO calibration/status polling.

## State And Persistence

The macros are stateless compile-time constants. The mutable state they describe lives in volatile DPCS hardware registers. That state can be changed by display link training, modesets, hotplug handling, PHY reinitialization, suspend/resume, GPU reset recovery, power gating, and debug or validation tools. The many reserved masks are part of the hardware contract: callers should preserve reserved bits during read-modify-write operations unless a hardware sequence explicitly documents otherwise.

Some fields represent latched or sampled hardware status, such as TX/RX acknowledge bits, detect-RX results, valid bits, adaptation status, statistic/sample done bits, calibration done, VCO FSM state, analog status, and DCC acknowledgements. Other fields are override values or override enables; leaving override enables asserted after diagnostics can persistently redirect normal PHY control until the register is restored or reset.

## Dependencies

This chunk depends on the AMD ASIC register-generation pipeline remaining synchronized with the DPCS 4.2.2 hardware specification. It is normally consumed together with:

- `dpcs_4_2_2_offset.h`, which supplies the `ixDPCSSYS_CR2_LANE1_*` and `ixDPCSSYS_CR2_LANE2_*` register addresses for the field groups described here.
- AMDGPU display/DC register access helpers that combine address, mask, and shift constants for indexed DPCS CR MMIO operations.
- Display link training, PHY power management, receiver adaptation, CDR/VCO/DPLL calibration, diagnostic, and hardware bring-up code in the AMD GPU driver.

The file is part of an imported Linux GPU driver tree under this repository and has no direct dependency on Ceph filesystem logic.

## Integration Points

The definitions integrate with AMD display PHY initialization and runtime link management for the CR2 instance. Lane 1 content in this slice is mostly receiver-side control and analog PHY detail, including power sequencing, calibration, adaptation, statistics, MPHY, and raw analog control. Lane 2 content begins with the ASIC-facing digital interface and then covers TX/RX power and early RX VCO calibration.

Correct integration requires pairing lane-specific masks with the matching lane-specific register addresses. A `DPCSSYS_CR2_LANE2_*` field must not be applied to a lane 1 or different CR instance address, even when field names and masks look identical. ASIC-version specificity also matters: these layouts are for `dpcs_4_2_2` and should not be mixed with neighboring DPCS versions without explicit hardware gating.

## Risks

- The range starts in the middle of `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`; the preceding chunk is required for that register's full field list.
- The range ends in the middle of `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_RX_VCO_STAT_1`; the following chunk is required for the rest of that status register.
- Generated mask/shift mistakes would compile cleanly but can silently program the wrong PHY bit.
- Many fields are sequencing-sensitive. Incorrect RX P-state, VCO/CDR/DPLL, adaptation, TX power, DCC, clock-alignment, or analog override writes can cause link-training failures, display blanking, intermittent high-rate instability, or misleading diagnostic readings.
- Reserved fields must be preserved. Accidentally writing reserved bits in 16-bit DPCS CR registers can change undocumented hardware behavior.
- Override fields usually have separate value and enable bits. Setting values without enables may do nothing; leaving enables asserted after a debug path can block normal ASIC control.
- Repetitive lane 1/lane 2 naming makes copy-paste errors likely in consumers, especially where lane 2 mirrors lane 1 field layouts but uses different address groups.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`.
- Static checks that each field has a matching `__SHIFT` and `_MASK`, masks match their shifts and widths, and DPCS CR fields stay within the expected 16-bit register shape unless hardware documentation says otherwise.
- Display bring-up on hardware using DPCS 4.2.2, including boot display, hotplug, modesets, suspend/resume, GPU reset recovery, and multi-monitor operation.
- Link-training stress across lane counts and link rates, with attention to CR2 lane 1 RX adaptation/statistic paths and CR2 lane 2 TX/RX power and calibration paths.
- PHY diagnostics that exercise TX/RX LBERT, DCC DAC programming and acknowledgement, RX VCO/CDR/DPLL status polling, adaptation status readback, statistic counters, MPHY low-speed controls, analog override/status readback, and cross-lane clock/shift handshakes.
