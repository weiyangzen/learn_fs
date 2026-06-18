# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 4736-7219

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment. It covers lines 4736-7219 and defines 2,076 preprocessor constants: 1,043 `__SHIFT` constants and 1,033 `_MASK` constants. The unequal count is expected for this slice because it starts in the middle of the `DCIO_UNIPHY1` reserved-register run and ends after only the shift macro for `DPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0__PTTRN_MSK_CR1A_4_0`.

The file is declarative only. It contains no C functions, structs, enums, global variables, branches, loops, allocation, locking, I/O calls, or persistence code. Its exported surface is a set of generated symbolic bitfield definitions for display PHY and UNIPHY registers.

## Purpose

`dpcs_4_2_2_sh_mask.h` gives AMDGPU display code symbolic field positions and masks for DPCS 4.2.2 hardware registers. Consumer code pairs these macros with register addresses from `dpcs_4_2_2_offset.h` and the display core register-helper macros to compose read-modify-write operations without embedding raw bit numbers in driver logic.

This chunk specifically covers:

- The tail of the `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED*` field map and complete reserved macro-control maps for `DCIO_UNIPHY2`, `DCIO_UNIPHY3`, and `DCIO_UNIPHY4`.
- The start and most of the `DPCSSYS_CR0` indirect register-field namespace under address block `dpcssys_cr0_rdpcstxcrind`.
- Common/supervisor digital and analog control surfaces for reference clock overrides, MPLLA/MPLLB override/input/status fields, spread-spectrum fields, bandgap/prescaler/RTUNE fields, and MPLL power-control fields.
- Lane 0 ASIC-facing override/input/output fields and the beginning of lane 0 TX power-control, DCC DAC, clock-align, LBERT, and RX statistic match definitions.

## Exported API Surface

There are no callable APIs or local types. The public interface is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field.
- `REGISTER__FIELD_MASK` gives the bit mask for the same field.

Important macro families in this range:

- `DCIO_UNIPHY{1,2,3,4}_UNIPHY_MACRO_CNTL_RESERVED*`: full-width `UNIPHY_MACRO_CNTL_RESERVED` masks and shifts for reserved UNIPHY macro-control slots. These are 32-bit masks (`0xFFFFFFFFL`) and should not be treated as driver-owned scratch fields.
- `DPCSSYS_CR0_SUP_DIG_IDCODE_*`: low/high identification data fields for the CR0 DPCS block.
- `DPCSSYS_CR0_SUP_DIG_REFCLK_OVRD_IN`, `MPLLA_*_OVRD_IN`, `MPLLB_*_OVRD_IN`, `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, and `LVL_OVRD_IN`: digital override fields for reference clocks, PLL controls, divider/HDMI clocks, charge pump settings, power-good/state signals, and lane-level support signals.
- `DPCSSYS_CR0_SUP_DIG_*_ASIC_IN`, `BANDGAP_ASIC_IN`, `MPLLA_CP_ASIC_IN`, and `MPLLB_CP_ASIC_IN`: ASIC-sourced values that feed the same common support and PLL control paths when hardware rather than software override owns the signal.
- `DPCSSYS_CR0_SUP_ANA_*`: analog supervisor controls for prescaler, RTUNE, bandgap, MPLLA/MPLLB miscellaneous controls, override enables, analog test-bus selections, PLL control registers, and reserved analog fields.
- `DPCSSYS_CR0_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR0_SUP_DIG_MPLLB_MPLL_PWR_CTL_*`: MPLL power-control override, status, timer, calibration, DAC, and spread-spectrum selection fields for both PLLs.
- `DPCSSYS_CR0_SUP_DIG_CLK_RST_*` and `RTUNE_*`: common clock/reset bring-up timing and resistor-tuning configuration/status/set-value fields.
- `DPCSSYS_CR0_SUP_DIG_ANA_*_OVRD_OUT`, `ANA_STAT`, `ANA_BG_OVRD_OUT`, and `*_PMIX_OVRD_OUT`: digital-to-analog override output and status fields for PLL, RTUNE, bandgap, and PMIX paths.
- `DPCSSYS_CR0_LANE0_DIG_ASIC_*`: lane 0 loopback, TX/RX request, pstate, rate, width, MPLL select, reset, data enable, electrical cursor, beacon, async-data, VREG bypass, ACK, adaptation, and cross-lane clock/shift override surfaces.
- `DPCSSYS_CR0_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX power-state programming for P0/P0S/P1/P2, power-up timing, DCC bank/DAC controls, clock alignment, and TX LBERT controls.
- `DPCSSYS_CR0_LANE0_DIG_RX_STAT_*`: start of lane 0 RX statistic load/data/match-mask definitions.

## Register Areas Covered

The UNIPHY portion is a reserved macro-control map. It exposes a long sequence of full-width reserved fields for UNIPHY instances 1 through 4. The chunk starts at `UNIPHY1` reserved index 14, then includes all 58 reserved entries for `UNIPHY2`, `UNIPHY3`, and `UNIPHY4`. Because these are named reserved fields, consumers should preserve their values unless an AMD hardware sequence explicitly documents otherwise.

The `DPCSSYS_CR0_SUP_DIG_*` section is the common digital supervisor surface for the first DPCS CR instance. It includes ID fields, reference clock source/range/bandgap controls, MPLLA/MPLLB divided-clock and HDMI-clock overrides, PLL override-input bundles, spread-spectrum peak/step-size registers, support/status override paths, prescaler settings, debug, ASIC input mirrors, and level/bandgap/charge-pump inputs.

The `DPCSSYS_CR0_SUP_ANA_*` section maps common analog controls. It includes prescaler control, RTUNE control, bandgap trim/status fields, switch power measurement, MPLLA/MPLLB misc and override fields, analog test bus selectors, PLL control registers, and reserved analog slots. These fields affect PHY analog behavior and are tightly coupled to board, process, and ASIC stepping assumptions.

The MPLL power-control subsection appears twice, once for MPLLA and once for MPLLB. Each side defines override selection, clock enables, fast power-up/lock options, DTB/divider control, FSM state, lane ownership/status bits, lock/calibration/reset/status bits, DAC maximum range, lock and pclk-stable timers, calibration controls, analog DAC output, and SSC spread-type fields.

The clock/reset and RTUNE subsection defines bandgap/reference power-up timers, VPH underdrive timing, RTUNE debug/config/status fields, RX/TXDN/TXUP set values and readbacks, counter configuration, and TX calibration code fields. These are hardware calibration and sequencing registers rather than software-maintained state.

The digital-to-analog override-output subsection defines how digital logic can override or observe analog MPLLA/MPLLB, RTUNE, bandgap, and PMIX signals. Many fields are paired value and override-enable bits, so the field map is a contract for controlled bring-up, validation, or diagnostic code that needs to force a signal away from normal hardware ownership.

The lane 0 ASIC subsection maps the first lane's digital interface to the ASIC-side lane/TX/RX controls and status. It covers serial/parallel loopback, lane enable, ACJTAG enable, TX request/pstate/rate/width/MPLLB select/reset/data-enable/electrical cursor override fields, TX async and VREG bypass controls, TX/RX acknowledgement and status outputs, normal ASIC input mirrors, and cross-lane/master-lane clock synchronization override fields.

The lane 0 TX power-control subsection defines TX power states P0, P0S, P1, and P2. Common fields enable analog refgen, VCM hold, analog clock, word clock, analog reset, serial enable, digital clock, data, RX detect, and DCC compensation calibration. P2 additionally exposes `TX_P2_ALLOW_VBOOST`. The timing registers configure refgen/clock/VCM/VBOOST/RX-detect/reset/serial-enable waits and skip/fast-path controls. DCC fields expose CR bank address/data and DAC control/range/selection/request/ack/address. The end of this slice starts RX statistic matching after TX clock alignment and LBERT control.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior is created by driver code that selects these masks and shifts when programming hardware registers, and by the DPCS/UNIPHY hardware state machines that interpret those register values.

The field names imply several hardware sequences:

- Reference and PLL bring-up: reference clock overrides, bandgap enable/status, MPLLA/MPLLB override inputs, PLL power timers, lock timers, pclk-stable timers, calibration controls, and SSC fields participate in link clock setup and power transitions.
- Common analog calibration: RTUNE, bandgap, charge pump, prescaler, PMIX, analog override, and analog status fields expose low-level calibration and analog-control state.
- Lane 0 link state: TX request, reset, pstate, rate, width, data-enable, MPLLB select, electrical cursor, beacon, async data, and ACK/status fields describe the PHY-side part of DisplayPort/HDMI lane activation.
- Lane 0 power-state transitions: P0/P0S/P1/P2 and timing fields encode the sequencing of refgen, clocks, reset, serial enable, VCM hold, VBOOST, RX detect, and DCC compensation calibration.
- Diagnostics and validation: ACJTAG, analog test-bus, DTB selection, LBERT, DCC DAC, debug, and override-output fields support manufacturing, board validation, or deep hardware debug paths.

No software state is persisted in this file. Hardware register contents persist only according to the ASIC reset and power-domain behavior. Reserved fields and value/override-enable pairs must be handled by consumers with read-modify-write discipline and hardware-spec access semantics.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is AMD's generated DPCS 4.2.2 register database and the companion address header `dpcs_4_2_2_offset.h`.

In this source tree, `dpcs_4_2_2_sh_mask.h` is included by `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` together with `dpcs_4_2_2_offset.h`. That resource file also defines the DPCS base segments used for DCN 3.1.5 display hardware. The offset header maps the direct DPCS CR address/data windows, RDPCSTX register ranges, and repeated instance bases; this shift/mask header supplies the bitfield layer for those addresses.

Likely higher-level integration points include DCN 3.1.5 resource construction, link encoder and PHY setup, DisplayPort/HDMI link training, hotplug and link-rate/lane-width changes, power management, suspend/resume, PHY calibration, manufacturing test, and debug code that reads or writes DPCS indirect registers through the CR address/data windows.

## Risks

- Generated-header drift is the primary risk. A wrong shift or mask can silently program the wrong PHY bit and cause display link failures that look like training, clocking, or board issues.
- The slice contains many value and override-enable bit pairs. Setting a value without the matching enable bit may do nothing; leaving an enable bit asserted can force hardware away from normal state-machine control.
- Reserved UNIPHY and analog fields are numerous and sometimes full-width. Treating them as software-owned fields can corrupt undocumented hardware state.
- MPLLA and MPLLB fields are structurally similar. Copy/generation mistakes between the A and B PLL families can create asymmetric behavior depending on clock source selection.
- Lane 0 TX power-state and timing fields directly affect analog sequencing. Incorrect timings or skip/fast bits can break RX detect, VBOOST behavior, DCC compensation, or PLL/clock stability.
- The chunk ends mid-register at `DPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0`; merge/reconciliation must not assume the RX statistic match group is complete here.
- Mask constants do not encode access type. Status, clear, latch, and write-one-to-clear semantics must come from the hardware spec or surrounding driver accessors.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Preprocess or build AMDGPU DCN 3.1.5 code that includes `dcn315_resource.c`, `dpcs_4_2_2_offset.h`, and `dpcs_4_2_2_sh_mask.h`.
- Static checks that complete register groups have paired `__SHIFT` and `_MASK` definitions; for this exact sliced range expect 1,043 shifts and 1,033 masks because of boundary cuts.
- Compare generated field names against `dpcs_4_2_2_offset.h` and adjacent ASIC revisions to detect missing or renamed CR0 supervisor, analog, MPLL, RTUNE, lane 0, and UNIPHY register groups.
- Runtime display validation on DPCS 4.2.2/DCN 3.1.5 hardware: DP and HDMI link training, link-rate and lane-count changes, hotplug, suspend/resume, low-power entry/exit, and recovery from display blanking.
- Hardware readback should show expected transitions for reference clock enable, bandgap/RTUNE status, MPLL lock/calibration/FSM state, pclk stable, TX request/ACK, RX/adapter status, TX pstate sequencing, DCC DAC ACK, and LBERT/statistic paths when exercised.
- Debug/manufacturing validation should explicitly clear any override-enable bits it sets for analog, PLL, RTUNE, PMIX, lane, TX, RX, DCC, ACJTAG, and cross-lane synchronization tests.

## Chunk Notes For Merge

This document intentionally covers only lines 4736-7219 of `dpcs_4_2_2_sh_mask.h`. Earlier chunks should cover the beginning of the file and the start of `DCIO_UNIPHY1`; later chunks should continue lane 0 RX statistic/match fields and the remaining DPCS lane/register blocks. The final merged per-file report should describe the whole file as a generated ASIC register bitfield map for DPCS 4.2.2 rather than handwritten driver logic, with `dcn315_resource.c` and `dpcs_4_2_2_offset.h` as the primary in-tree anchors.
