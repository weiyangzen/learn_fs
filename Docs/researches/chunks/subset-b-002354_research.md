# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 40594-42955

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic; the exported surface is preprocessor constants that encode DPCS register bit positions (`__SHIFT`) and bit masks (`_MASK`).

The requested range contains 2,136 `#define` entries across 226 register-comment groups. It starts at `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL`, covers CR1 supervisor analog bandgap/RTUNE/MPLL definitions, CR1 supervisor digital MPLLA/MPLLB power-control and analog override outputs, and most of the CR1 lane-X digital ASIC, TX/RX power, CDR, adaptation, statistics, MPHY, and digital-to-analog override field definitions. It ends inside `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2`, before that register's final two masks and before `DPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL` in the next chunk.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field inside the associated DPCS register.
- `<REGISTER>__<FIELD>_MASK`: bit mask used by AMD display register helpers to isolate, compose, or update that field.

Most fields in this slice describe 16-bit DPCS register payloads stored in 32-bit constants. The exact requested range has 1,072 shift macros and 1,064 mask macros. The imbalance is caused by generated data and the artificial chunk boundary: `DPCSSYS_CR1_SUPX_DIG_RTUNE_DEBUG` provides shifts without matching masks in this range, and `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2` has two masks after line 42955.

Main register families in this chunk:

- `DPCSSYS_CR1_SUPX_ANA_*`: supervisor analog RTUNE, bandgap/reference selection, switch/power measurement, MPLLA/MPLLB miscellaneous, override, analog-test-bus, charge pump, PLL control, and reserved analog control fields.
- `DPCSSYS_CR1_SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR1_SUPX_DIG_MPLLB_MPLL_PWR_CTL_*`: digital MPLL override, status, DAC range, lock and power timing, calibration, analog DAC readback, and spread-spectrum type fields for both PLLs.
- `DPCSSYS_CR1_SUPX_DIG_CLK_RST_*`, `RTUNE_*`, and `ANA_*_OVRD_OUT`: supervisor digital bandgap/reference power-up timing, RTUNE configuration/status/setpoint/readback, MPLLA/MPLLB analog override outputs, RTUNE override output, analog status, bandgap override, and PMIX override fields.
- `DPCSSYS_CR1_LANEX_DIG_ASIC_*`: lane-X ASIC-facing override and normal input/output mirrors for TX, RX, EQ, CDR/VCO, lane loopback, AC JTAG, OCLA, ACK/status, lane-master, and cross-lane clock/shift handshakes.
- `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_*`: TX P-state programming, TX power-up timing, DCC CR-bank windows, DCC DAC control/range/selection/ACK/address, TX clock alignment, and TX LBERT controls.
- `DPCSSYS_CR1_LANEX_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, `RX_ADPTCTL_*`, and `RX_STAT_*`: RX power-state control, VCO calibration, CDR, DPLL frequency/bounds, adaptation configuration/status/reset, CR-bank windows, programmable RX statistic masks/matchers/counters, sample counts, and stop controls.
- `DPCSSYS_CR1_LANEX_DIG_MPHY_*` and `DIG_ANA_*`: MPHY RX PWM/termination controls and digital-to-analog TX/RX override outputs for TX control, term code, TX EQ, RX control/power, and RX VCO tuning.

## Control Flow

This header has no runtime control flow. It participates in AMDGPU display setup as compile-time register metadata:

1. `dcn315_resource.c` includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`.
2. DCN resource macros such as `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` expand register offsets, shifts, and masks into display resource tables.
3. Runtime display code uses common helpers such as register read/update macros against those tables.
4. Actual sequencing for PLL power, RTUNE, lane power states, CDR/VCO calibration, DCC, RX adaptation, statistics, and analog diagnostics lives outside this generated header.

The constants here define where bits live. They do not encode access direction, self-clearing behavior, timeout policy, clock-domain constraints, or reset ordering.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible CR1 supervisor and lane-X state:

- Supervisor analog state: bandgap/reference selection, RTUNE controls, ATB measurement selection, MPLLA/MPLLB enable/reset/calibration override values, charge-pump and PLL tuning, clock divider and regulator bypass bits, and PMIX control.
- Supervisor digital state: MPLLA/MPLLB power-control finite-state status, lock status, PLL lane ownership bits, clock enables, calibration controls, timing values, DAC limits/readback, spread-spectrum type override, RTUNE setpoints/status, and analog override outputs.
- Lane ASIC interface state: TX/RX request, P-state, rate, width, data enable, reset, disable, inversion, low-power detect, clock-ready, detect-RX, MPLLB select, HDMI/MPHY modes, loopback, async TX data/drive, ACK, valid, adaptation status, EQ values, VCO/ref load values, and lane-master/other-lane synchronization.
- TX state: per-P-state analog refgen, VCM hold, clock, reset, serial/data, powerdown, high-Z, DCC, output, RX-detect, and Vboost bits; TX power-up timing; DCC bank/DAC programming; TX clock alignment; LBERT control.
- RX state: per-P-state AFE, clock, CDR, deserializer, squelch, scope, adaptation, slicer, DFE, and fast-start controls; VCO calibration control/timing/status; CDR bypass/tracking/rate controls; DPLL frequency and bounds; adaptation algorithm settings and status readbacks.
- Diagnostic state: RX statistic masks/patterns/counters, OCLA enable/data controls, MPHY PWM and low-speed termination controls, term-code/TX EQ/RX VCO override outputs, analog status, and readback fields.

Persistence is hardware-defined. Control fields generally retain values until driver reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/hardware ownership changes. ACK, valid, lock, statistic, calibration, and status fields may be sampled, latched, self-clearing, or only valid while the relevant CR1 power and clock domains are active. This generated header does not describe those side effects.

## Dependencies And Integration Points

The direct syntactic dependency is only the C preprocessor, but the values must stay synchronized with the DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `regDPCSSYS_*` and `ixDPCSSYS_*` register addresses, including examples in this slice such as `ixDPCSSYS_CR1_SUPX_DIG_MPLLA_MPLL_PWR_CTL_MPLL_OVRD`, `ixDPCSSYS_CR1_LANEX_DIG_RX_STAT_MATCH_CTL0`, and `ixDPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes this header and the matching offset header for DCN 3.1.5 resource initialization.
- AMD display register helper tables consume the shift/mask names through DPCS register-list and mask-list macros.
- Behavioral consumers are link encoder, PHY, AUX/DPCS access, HPO/DP, HDMI, link-training, modeset, power-management, and diagnostic paths that program or inspect DPCS CR1 lanes and supervisor PLL/RTUNE blocks.

The chunk is source-tree-aligned with generated AMDGPU ASIC register headers, not with filesystem logic.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong bit position or mask compiles cleanly but can write an adjacent hardware field, preserve the wrong reserved bits, or decode a status field incorrectly.
- Manual edits to generated metadata risk divergence from AMD's authoritative register source, the matching `dpcs_4_2_2_offset.h`, firmware assumptions, and nearby DPCS generations.
- The chunk ends mid-register at `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2`; whole-register validation must reconcile its remaining masks from the next chunk.
- `DPCSSYS_CR1_SUPX_DIG_RTUNE_DEBUG` has shift-only field definitions in this range. Validators should distinguish generated shift-only groups from missing accidental masks.
- MPLLA/MPLLB and supervisor RTUNE/bandgap fields are shared resources for the CR1 PHY. Incorrect masks can affect more than one lane or connector path.
- Override-enable fields sit near override values. Accidentally setting an enable can take ownership away from normal hardware or firmware control; forgetting it can make a debug value write appear ineffective.
- TX/RX power, CDR, VCO, DPLL, DCC, adaptation, and termination fields are sequencing-sensitive. A mask error may show up as intermittent link training failure, blank display, CDR unlock, high bit error rate, or resume-only failure.
- Status/readback fields are intermixed with writable controls. Consumers cannot infer access direction, clear behavior, or side effects from `_MASK` presence alone.
- Repeated MPLLA/MPLLB and TX/RX lane-X structures are copy-sensitive. A generator issue can affect only one PLL, P-state, statistic counter, DFE tap, or calibration field while surrounding groups remain correct.
- Reserved and `NC` fields have explicit masks throughout the range. Driver writes should preserve them unless the hardware specification explicitly requires a value.

## Test Signals

Useful validation is mostly generated-data, build, and hardware-integration oriented:

- Build AMDGPU display code that includes `dcn315_resource.c`; missing or renamed DPCS 4.2.2 macros should fail during resource-table initialization.
- Mechanically verify that complete register groups in lines 40594-42955 have matching `__SHIFT` and `_MASK` entries, allowing the known `RTUNE_DEBUG` shift-only group and the `ANA_RX_VCO_OVRD_OUT_2` boundary.
- Cross-check the register names in this chunk against `dpcs_4_2_2_offset.h` for corresponding `ixDPCSSYS_*` offsets.
- Diff compatible fields against AMD's generated source and nearby DPCS variants such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` where the hardware register database expects stable layouts.
- Exercise DCN 3.1.5 display paths that depend on DPCS 4.2.2: DisplayPort and HDMI link bring-up, rate/width changes, hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset.
- Check register dumps or PHY debug traces for MPLLA/MPLLB lock and power states, RTUNE status/setpoints, TX/RX P-state transitions, CDR/VCO calibration status, DPLL bounds, DCC ACK, RX adaptation status, RX statistic counters, DETRX/TX ACK, and analog override/readback fields.
- Run controlled diagnostic paths for LBERT, OCLA, RX statistic match/counter logic, MPHY PWM/termination, TX term/EQ override, RX VCO override, RTUNE, and DCC DAC controls when hardware access is available.

## Cross-Chunk Notes

The previous chunk ends with `DPCSSYS_CR1_SUPX_ANA_PRESCALER_CTRL`; this chunk begins the next complete register group, `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL`. The next chunk should continue `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2` masks and then cover `DPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL` and later lane-X analog fields. The final per-file report should reconcile these artificial chunk boundaries before making whole-file claims about DPCS 4.2.2.
