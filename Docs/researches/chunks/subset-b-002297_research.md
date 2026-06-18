# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 21540-23895

## Scope

This chunk documents lines 21540-23895 of the generated AMD DPCS 4.2.0 shift/mask header. The slice contains 2,140 `#define` entries: 1,073 `__SHIFT` macros and 1,078 `_MASK` macros. The uneven count is expected because the requested range starts in the middle of `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0`, after its shift definitions and first mask, and ends in the middle of `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT`, after its first shift definitions and before its masks.

The file content is declarative only. It defines preprocessor constants for bit positions and masks in memory-mapped display PHY/control registers; it has no C functions, structs, runtime storage, branching, or local algorithms.

## Purpose

The header gives AMDGPU display code symbolic access to DPCS 4.2.0 register fields. Consumer code can combine companion offset macros with these shift/mask macros to build read-modify-write operations without hardcoding raw bit values.

This chunk covers CR0 common and lane-level DPCS/PHY surfaces:

- SUPX analog override/status fields for MPLLB clock enables, analog control, RTUNE, bandgap, reference regulator, and PMIX selection.
- `LANEX_DIG_ASIC_*` bridge-facing override/input/output fields for lane, TX, RX, EQ, CDR/VCO, link rate, lane width, power state, loopback, inversion, DETRX, beacon, async drive, and acknowledge/status signaling.
- TX and RX power-control state tables and timing registers for P0, P0S, P1, P2, power-up delays, DCC DAC, and low-bit-error-rate test controls.
- RX VCO calibration, CDR, DPLL, adaptation, slicer, CTLE/VGA/DFE status, statistic/match counters, and calibration clock controls.
- Digital-to-analog TX/RX override registers for TX EQ, cursor/term codes, DCC DAC, MPHY, RX AFE, RX VCO, RX scope/slicer, signal-detect, analog status, and term-code clocks.
- Analog lane TX/RX registers for measurement, power override, alternate bus, ATB measurement/force points, DCC, term-code control, clocks, misc controls, RX CDR/deserializer, squelch, calibration, regulator/reference, and reserved fields.
- Raw memory and raw lane PCS windows for ROM/RAM data, TX PCS input/override input, and the beginning of TX override output.

## Exported API Surface

There are no callable APIs or local types. The exported surface is the macro namespace used by AMD display code after including `dpcs_4_2_0_sh_mask.h`.

Important macro families in this range:

- `DPCSSYS_CR0_SUPX_DIG_ANA_*`: common analog and PLL-related masks for MPLLB enables/resets/calibration, RTUNE comparison, bandgap/reference regulator control, and MPLLA/MPLLB PMIX selection.
- `DPCSSYS_CR0_LANEX_DIG_ASIC_*`: lane interface fields that expose override values and corresponding override-enable bits for TX/RX request, power state, rate, width, data enable, MPLLB select, async drive, VBOOST, DETRX, termination, inversion, loopback, RX EQ, and CDR/VCO settings, plus ASIC input and output mirrors.
- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_*` and `DPCSSYS_CR0_LANEX_DIG_RX_PWRCTL_*`: TX/RX power-state programming fields, delay/count fields, DCC CR-bank address/data, DAC selection/range/control/ack, and power-up timing.
- `DPCSSYS_CR0_LANEX_DIG_RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, and `RX_ADPTCTL_*`: receive-side calibration and adaptation fields, including VCO calibration windows, CDR PI/deserializer controls, DPLL frequency bounds, adaptation loop controls, gain/DFE/CTLE status, DAC control selection, and CR-bank access.
- `DPCSSYS_CR0_LANEX_DIG_RX_STAT_*`: programmable RX statistic matcher/counter fields, masks, sample counts, stop control, and comparator clock control.
- `DPCSSYS_CR0_LANEX_DIG_ANA_*` and `DPCSSYS_CR0_LANEX_ANA_*`: digital control of analog TX/RX circuitry, ATB measurement selectors, signal detect, term-code generation, DCC, VCO, power, squelch, calibration muxes, regulator references, and reserved raw analog windows.
- `DPCSSYS_CR0_RAWMEM_*` and `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_*`: raw 16-bit ROM/RAM data fields and raw PCS TX override/input/status handoff fields.

## Control Flow And State Behavior

The chunk has no software control flow. Runtime behavior comes from consumers using the macros with register access helpers.

The field names imply several hardware state machines and handshakes:

- Link/lane bring-up uses request/ack, reset, rate, width, power state, low-power detect, data-enable, clock-ready, MPLL select/enable, and DETRX fields across the ASIC and raw PCS views.
- Override programming is explicit. Most override fields have a paired `*_OVRD_EN`, `*_OVR_EN`, or `ovrd_*` bit, so software must set both the desired value and its enable bit before hardware should consume it.
- TX output behavior is shaped by main/pre/post cursor fields, EQ tables, term-code controls, VBOOST/IBOOST, beacon enable, async data/drive, inverter controls, DCC DAC, and per-state power-control values.
- RX acquisition and adaptation depend on CDR/VCO calibration, DPLL bounds, adaptation reset/config fields, VGA/CTLE/DFE status, slicer controls, squelch/signal detect, and statistic counters.
- Analog measurement and debug paths are exposed through ATB selectors, force fields, scope controls, raw memory data windows, CR-bank address/data registers, and reserved analog buses.

No software persistence is implemented here. Hardware register contents persist according to the ASIC reset and power domains. Several fields expose hardware latches, counters, readback/status, reserved storage, or raw data windows, but this header does not define ownership or lifetime rules for those values.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. The macros are intended to be paired with generated DPCS 4.2.0 offset headers and AMDGPU/DC register helper macros that know how to apply a field mask and shift to a memory-mapped register.

Visible integration points include:

- AMDGPU DRM display resource code for DCN 3.1 generation hardware, which includes `dpcs/dpcs_4_2_0_sh_mask.h`.
- Display Core link encoder, PHY, clock, DisplayPort/HDMI, and low-level diagnostics paths under `drivers/gpu/drm/amd/display`.
- Companion generated offset headers that define addresses such as the `DPCSSYS_CR0_LANEX_*`, `RAWLANEX_*`, and `RAWMEM_*` registers.
- Firmware/PHY coordination paths that require request/ack and override-enable semantics rather than blind writes.
- Hardware validation tooling that compares generated register headers against the ASIC register database.

## Risks

- Generated-header drift is the central risk. A wrong shift or mask can make a read-modify-write touch the wrong PHY bit and produce link training, power, or calibration failures that compile cleanly.
- This slice is densely populated with paired value/enable fields. Programming an override value without the matching enable bit, or leaving an enable bit asserted after diagnostics, can pin hardware away from normal firmware/PHY control.
- Status and control fields sit close together. Examples include request/ack, calibration request/status, statistic counters, DCC DAC ack, analog status, and raw PCS input/output. Consumers need the hardware access semantics from the register spec.
- Reserved and raw windows (`RESERVED_*`, `NC*`, `RAWMEM_*`, raw analog buses) must not be treated as stable general-purpose storage unless the ASIC documentation says so.
- TX/RX power-state tables and timing masks are small packed fields. Invalid values can affect suspend/resume, hotplug, low-power transitions, or signal integrity without being detected by unit tests.
- The requested chunk boundaries split register blocks, so automated reconciliation must merge adjacent chunks before judging field completeness for `MPLLB_OVRD_OUT_0` and `RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT`.

## Test Signals

Useful validation is mostly build-time, generated-header, and hardware-integration oriented:

- Compile or preprocess AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`, especially DCN 3.1 resource/link paths.
- Run generated-register consistency checks against the DPCS 4.2.0 register source database, including paired `__SHIFT`/`_MASK` coverage across chunk boundaries.
- Static grep checks for consumers of `DPCSSYS_CR0_LANEX_DIG_ASIC_*`, `RX_VCOCAL`, `RX_ADPTCTL`, `RX_STAT`, `DIG_ANA`, `LANEX_ANA`, and `RAWLANEX_DIG_PCS_XF_TX_*` fields.
- Runtime display tests on matching ASICs: DP and HDMI link training, hotplug, suspend/resume, lane power-state changes, DETRX handling, RX adaptation/calibration, and PHY diagnostics.
- Register readback during bring-up should show expected transitions for request/ack, reset release, clock/data enable, MPLL selection, VCO calibration status, DPLL bounds, RX adaptation status, DCC ack, analog status, statistic counters, and raw PCS output fields.

## Chunk Notes For Merge

This document intentionally covers only lines 21540-23895 of `dpcs_4_2_0_sh_mask.h`. Adjacent chunks should provide the missing beginning of `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0` and the continuation of `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT`. The final per-file report should treat this file as a generated ASIC bitfield map, not handwritten driver logic.
