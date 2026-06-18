# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 4747-7277

## Scope

This chunk is a generated AMD DPCS 4.2.3 shift/mask header segment. It covers lines 4747-7277 of `dpcs_4_2_3_sh_mask.h` and defines C preprocessor constants for hardware register fields. The range contains 1,136 `__SHIFT` macros and 970 `_MASK` macros; the imbalance is expected because this line slice starts and ends inside larger generated register groups.

The content is declarative only. It has no functions, structs, enums, runtime variables, branches, loops, or local persistence. Its public surface is the macro namespace used by AMDGPU display code to select bit positions and masks when programming DPCS 4.2.3 registers.

## Purpose

The header gives DCN 3.1.6 display code symbolic access to DPCS 4.2.3 hardware bitfields. Consumer code pairs these field constants with register addresses from `dpcs_4_2_3_offset.h` and register helper macros for read-modify-write operations.

This chunk specifically covers:

- The tail of `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED8` through `RESERVED57`.
- Complete reserved macro-control field maps for `DCIO_UNIPHY2`, `DCIO_UNIPHY3`, and `DCIO_UNIPHY4`, each exposing `UNIPHY_MACRO_CNTL_RESERVED` as a full 32-bit field.
- The start of the `dpcssys_cr0_rdpcstxcrind` address block, including CR0 supervisor digital/analog fields, MPLLA/MPLLB override/status/calibration fields, RTUNE fields, common analog override outputs, and the beginning of lane 0 digital TX/RX control and statistics fields.
- The final register in this chunk is partial: `DPCSSYS_CR0_LANE0_DIG_ANA_TX_OVRD_OUT` continues with `TX_OVRD_EN_MASK` on the next line outside this range.

## Exported API Surface

There are no callable APIs or local types. The exported API is the generated macro naming contract:

- `REG__FIELD__SHIFT` gives the field's starting bit position.
- `REG__FIELD_MASK` gives the field's unshifted register mask.

Important macro families in this chunk:

- `DCIO_UNIPHY{1,2,3,4}_UNIPHY_MACRO_CNTL_RESERVED*`: reserved 32-bit macro-control fields for display PHY instances.
- `DPCSSYS_CR0_SUP_DIG_IDCODE_*`, `REFCLK_OVRD_IN`, `MPLLA_*_OVRD_IN`, and `MPLLB_*_OVRD_IN`: supervisor digital ID, reference-clock override, PLL clock override, PLL parameter override, and spread-spectrum programming fields.
- `DPCSSYS_CR0_SUP_DIG_*_ASIC_IN` and `*_OVRD_OUT`: ASIC-facing input/status and override-output fields for MPLLA, MPLLB, clocks, level control, bandgap, charge-pump, RTUNE, analog status, and PMIX paths.
- `DPCSSYS_CR0_SUP_ANA_*`: analog supervisor register fields for prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB miscellaneous, override, ATB, control, and reserved registers.
- `DPCSSYS_CR0_SUP_DIG_MPLL{A,B}_MPLL_PWR_CTL_*`: MPLL power-control override, status, DAC range, lock/stability timers, calibration, analog DAC output, and spread type fields.
- `DPCSSYS_CR0_SUP_DIG_CLK_RST_*`: bandgap and reference-clock power-up timing and reference VPHUD fields.
- `DPCSSYS_CR0_SUP_DIG_RTUNE_*`: RTUNE debug/config/status, set values, readback status, counters, and TX calibration code fields.
- `DPCSSYS_CR0_LANE0_DIG_ASIC_*`: lane 0 ASIC-facing lane/TX/RX override inputs and outputs.
- `DPCSSYS_CR0_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX pstate, power-up timers, DCC CR-bank access, DCC DAC control/range/select/ack/address, and TX clock alignment fields.
- `DPCSSYS_CR0_LANE0_DIG_RX_STAT_*`: lane 0 RX statistic load/start, data mask, match patterns, statistic controls, counters, calibration comparator clock, and statistic stop fields.
- `DPCSSYS_CR0_LANE0_DIG_ANA_TX_OVRD_OUT`: lane 0 analog TX override output bits for clock/data/refgen enable, VCM hold, MPLL clock enables, reset, serial enable, data rate, div4, RX detect, and override enable.

## Register Areas Covered

The UNIPHY portion is mostly structural padding from the generated register database. Each reserved register exposes a single `UNIPHY_MACRO_CNTL_RESERVED` field with shift `0x0` and mask `0xFFFFFFFFL`. These definitions preserve named access to reserved macro-control address slots for UNIPHY instances 1 through 4.

The CR0 supervisor digital section starts with low/high IDCODE words, then maps override inputs for reference clocks, MPLLA/MPLLB divided and HDMI clocks, PLL parameter fields, spread-spectrum peak and step-size values, charge-pump and gain settings, prescaler, supply/level controls, and debug visibility. The matching ASIC input groups expose hardware-provided status and clock/PLL configuration signals.

The CR0 supervisor analog section maps prescaler and RTUNE controls, bandgap fields, switch power measurement, PLL analog miscellaneous fields, override controls, ATB test-bus selections, PLL control registers, and generated reserved analog slots. These are low-level PHY analog controls rather than normal display policy code.

The MPLL power-control groups define override/status/calibration fields for both MPLLA and MPLLB. The fields include power-control override enables, status bits, maximum DAC range, lock and PCLK-stable timers, calibration controls, analog DAC output, and spread-spectrum generator spread type.

The RTUNE groups expose termination tuning state: debug controls, config/status registers, RX/TXDN/TXUP set values and status readbacks, configuration counters, and TX calibration code. These fields are part of PHY calibration and impedance/termination management.

The lane 0 section begins the per-lane CR0 field map. It covers ASIC lane/TX/RX overrides, TX pstate and power-up sequencing, DCC register/DAC control, clock alignment, LBERT TX pattern control, RX statistic pattern matching and counters, and the first analog TX override output register.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior is determined by driver code that expands these macros inside register helper calls and by hardware state machines in the DPCS/UNIPHY blocks.

The field names imply several hardware interaction patterns:

- Register helpers use `__SHIFT` and `_MASK` constants to pack or extract field values during read-modify-write operations.
- PLL bring-up and clock selection flows can use MPLLA/MPLLB override, ASIC input, spread-spectrum, power-control, timer, and calibration fields.
- Analog PHY bring-up and diagnostics can use bandgap, RTUNE, ATB, PLL control, PMIX, charge-pump, and analog status fields.
- Lane 0 TX power sequencing uses pstate, power-up timer, DCC DAC, DCC CR-bank, clock alignment, and TX analog override fields.
- Lane 0 RX diagnostics use the statistic load/start, match pattern, data mask, statistic control, sample/counter, comparator clock, and stop fields.

No software state is persisted here. Hardware register contents persist only according to ASIC reset, power-domain, and firmware/hardware sequencing rules. Reserved-field macros are part of the generated hardware contract and should not be interpreted as permission to write arbitrary values into reserved bits.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependencies are the DPCS 4.2.3 register database and the companion offset header, `dpcs_4_2_3_offset.h`, which supplies register addresses for these field definitions.

Within this source tree, `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`. That ties these macros to DCN 3.1.6 resource setup and the AMDGPU display hardware blocks that use DPCS 4.2.3.

Integration points visible from the names include DC link encoder/PHY setup, DisplayPort and HDMI PHY clocking, UNIPHY programming, PLL and spread-spectrum configuration, analog PHY calibration, RTUNE calibration, power-gating and reset flows, lane 0 TX power sequencing, DCC calibration, RX statistic/debug capture, manufacturing ATE/ATB access, and low-level debug paths.

## Risks

- Generated-header drift is the main risk. A wrong mask or shift can silently update the wrong hardware field while still compiling cleanly.
- This chunk begins inside the UNIPHY1 reserved bank and ends one line before the full `DPCSSYS_CR0_LANE0_DIG_ANA_TX_OVRD_OUT` field set is complete, so merge/reconciliation must treat boundary groups as partial.
- Reserved full-width UNIPHY fields and reserved bit masks in CR0 registers should be preserved during read-modify-write operations unless the hardware specification explicitly requires otherwise.
- Many fields combine override values with override enables. Leaving override enables asserted after diagnostics can bypass normal hardware or firmware state machines.
- MPLL, bandgap, RTUNE, DCC, and analog TX fields affect physical link stability. Incorrect programming can cause display link-training failures, intermittent hotplug/link loss, or power-management regressions.
- DCC CR-bank and DAC access fields include request/update/ack-style handshakes. Consumers need the hardware access rules; the mask header does not encode timing, polling, or write-one-to-clear semantics.
- The repeated MPLLA/MPLLB and UNIPHY2/3/4 families are copy-generated. Single-instance generation mistakes can create asymmetric behavior that appears only on specific PHY instances or connector routes.

## Test Signals

Useful validation is primarily build-time, generated-header, and hardware-integration oriented:

- Compile/preprocess AMDGPU display code that includes `dpcs_4_2_3_sh_mask.h` through `dcn316_resource.c`.
- Static checks that complete register groups have matching `__SHIFT` and `_MASK` definitions, while accepting known chunk-boundary partial groups in this range.
- Consistency checks against `dpcs_4_2_3_offset.h` so every complete `DCIO_UNIPHY*` and `DPCSSYS_CR0_*` register-field prefix has a corresponding offset macro.
- Generated-register comparisons against adjacent DPCS versions and adjacent chunks to catch accidental field-width, mask-format, or repeated-block drift.
- Runtime display tests on DCN 3.1.6 hardware: DP/HDMI link training, lane-rate and pstate changes, hotplug, suspend/resume, low-power transitions, PLL spread-spectrum configuration, RTUNE calibration, DCC calibration, and connector routing across UNIPHY instances.
- Register readback during bring-up should show expected transitions for MPLL power/status, lock timers, PCLK-stable timers, RTUNE status, DCC request/ack, TX pstate, clock alignment, analog TX override state, and RX statistic counter done bits.

## Chunk Notes For Merge

This document intentionally covers only lines 4747-7277 of `dpcs_4_2_3_sh_mask.h`. Earlier chunks should cover the beginning of the UNIPHY1 register bank, and later chunks should continue lane 0 analog TX override and subsequent CR0 lane/common register groups. The final merged per-file report should describe the whole file as a generated ASIC register bitfield map for DPCS 4.2.3, with `dcn316_resource.c` and `dpcs_4_2_3_offset.h` as primary in-tree integration anchors.
