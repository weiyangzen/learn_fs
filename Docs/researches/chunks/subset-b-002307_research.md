# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 45338-47685

## Scope And Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for Display Core Next display PHY/DPCS hardware. It is declarative metadata only: it defines C preprocessor constants for bit positions and bit masks, and contains no executable functions, structs, enums, variables, allocations, locks, or direct MMIO accesses.

The requested range contains 2,145 complete `#define` entries: 1,072 `__SHIFT` constants and 1,073 `_MASK` constants. The one extra mask is a chunk-boundary artifact: line 45338 begins inside `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`, after `meas_iv_bias__SHIFT` was emitted just before the requested range. The chunk then covers 203 register groups: 54 supervisor/common CR2 groups, 85 lane 0 groups, and 64 lane 1 groups. It ends inside the lane 1 RX VCO calibration status area at `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_0`; `RX_VCO_STAT_1` starts after this chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The exported interface is the generated macro naming convention consumed by AMD display register helper tables:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to isolate or update the field.
- `RESERVED_*`, `RSVD_*`, and similarly named fields preserve undocumented or reserved bit ranges so generated layouts stay aligned with the hardware register database.

Major macro families in this chunk are:

- CR2 supervisor analog MPLLB controls: `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`, `CTR1-5`, and `RESERVED1-2` describe MPLLB analog measurement, charge pump, regulator, Vref, standby, spoof/calibration-lock, bypass, DLL, divider, and reserved low-byte fields.
- CR2 supervisor digital MPLL power and SSC controls: paired `DPCSSYS_CR2_SUP_DIG_MPLLA_*` and `MPLLB_*` groups define MPLL override enables, feedback/PCLK enables, fast power-up/lock controls, divider selection, state readback, DAC range/input/output, lock/stable/gearswitch/PCLK timers, calibration override, and spread-spectrum generator spread-type override.
- Clock/reset and resistor tuning support: `CLK_RST_BG_PWRUP_TIME_*`, `CLK_RST_REF_PWRUP_TIME_0`, `CLK_RST_REF_VPHUD`, and `RTUNE_*` groups expose bandgap/reference timing, VPH/U/D reference bits, RTUNE request/force/set/readback values, calibration counters, and TX calibration code.
- Supervisor digital-to-analog override/readback groups: `SUP_DIG_ANA_MPLLA_OVRD_OUT_*`, `MPLLB_OVRD_OUT_*`, `RTUNE_OVRD_OUT`, `ANA_STAT`, `ANA_BG_OVRD_OUT`, and `PMIX_OVRD_OUT` describe override values and enable bits driven toward analog MPLL, RTUNE, bandgap, and PMIX circuits.
- Lane 0 digital ASIC interface: `DPCSSYS_CR2_LANE0_DIG_ASIC_*` defines software override and normal ASIC-facing TX signals such as request, pstate, rate, width, MPLL select, data enable, detect-RX, inversion, reset, clock-ready, low-power detect, beacon, async drive/data, and cross-lane shift handshakes, plus TX/RX output ACK/status fields.
- Lane 0 TX power, DCC, clock-align, LBERT, and RX statistics: `LANE0_DIG_TX_PWRCTL_*` gives pstate recipes, power-up timing, DCC CR-bank/DAC controls, and DAC ACK/address fields. `TX_CLK_ALIGN`, `TX_LBERT`, and `RX_STAT_*` cover clock alignment, loopback BERT control, match/mask programming, sample counters, statistic counters, calibration comparison clocking, stop, and done/status bits.
- Lane 0 digital/analog TX controls: `LANE0_DIG_ANA_TX_*` and `LANE0_ANA_TX_*` expose digital override values for analog TX clock/data/reset/refgen/serial/MPLL enables, termination-code overrides, TX equalization override banks, DCC DAC overrides, RX detect/status readbacks, analog measurement, power override, alternate bus/JTAG/test bus fields, DCC DAC programming, termination-code update/reset strobes, clock override, and miscellaneous analog TX tuning.
- Lane 1 digital ASIC interface: `DPCSSYS_CR2_LANE1_DIG_ASIC_*` repeats the lane 0 TX-side pattern and adds a larger RX-side surface in this range: RX request/pstate/rate/width, reset, CDR/VCO load values, adaptation enable/continuous adaptation, termination, low-power detect, RX valid, EQ override inputs, RX CDR/VCO ASIC inputs, OCLA, RX output readback, and cross-lane shift handshake fields.
- Lane 1 TX/RX power and VCO calibration: `LANE1_DIG_TX_PWRCTL_*` mirrors lane 0 TX pstate, power-up, and DCC controls. `LANE1_DIG_RX_PWRCTL_*` defines RX pstate recipes and RX power-up timing. `LANE1_DIG_RX_VCOCAL_*` covers RX VCO calibration fixed count/gain/bounce controls, reset/continuous-calibration overrides, DPLL calibration update gain, frequency tune start/step/skip controls, startup/update/counter timing, and the first RX VCO analog status register.

Most masks in this range are 16-bit-style values carried in 32-bit C literals ending in `L`, matching the DPCS CR register payload style used by these generated headers.

## Control Flow

This header has no local runtime control flow. The effective control flow is created by AMDGPU display code that includes this header with its companion offset header and uses register helpers to pack or unpack fields.

A typical consumer path is:

1. DCN 3.1 resource code includes `dpcs/dpcs_4_2_0_offset.h` and this `dpcs/dpcs_4_2_0_sh_mask.h` header.
2. Register-list and shift/mask-list macros token-paste generated register and field names into ASIC-specific tables.
3. Link encoder, PHY, hardware sequencer, clock, AUX/link-training, panel, or debug code calls helper macros such as register read, write, get, set, or update operations through those tables.
4. Hardware state machines, not this header, perform MPLL power sequencing, RTUNE calibration, lane pstate transitions, DCC updates, RX VCO calibration, RX adaptation, statistic counting, and ACK/status latching.

The field names imply sequencing dependencies: override value fields generally need paired override-enable bits, pstate recipes are selected by higher-level lane state changes, timing fields are interpreted by hardware counters, ACK/status fields are polled by driver code, and clear/mask/status fields require hardware-specific access semantics outside this generated file.

## State And Persistence Behavior

The file stores no software state and persists nothing itself. It names hardware-visible state in DPCS CR2 supervisor, lane 0, and lane 1 registers:

- Common clock/PLL state: MPLLA/MPLLB power override, feedback/PCLK/output enables, lock state, calibration state, DAC range/output, lock and stable timers, gearswing/preset timers, PCLK enable/disable/powerdown timers, spread-spectrum type override, bandgap/reference power timing, and analog PLL control bits.
- Tuning/calibration state: RTUNE request/force/calibration counters, RX/TX up/down set and status values, TX calibration code, MPLL calibration override, VCO calibration fixed-count and frequency-tune parameters, VCO calibration timing, and analog VCO readback signals.
- Lane TX state: pstate recipes for P0/P0S/P1/P2, analog/digital enables, refgen and clock enables, reset and serial-enable controls, data-enable and receive-detect allowance, DCC compensation policy, DCC DAC request/update/bin-hot/ACK, clock alignment, LBERT control, TX termination, equalization, DCC DAC, and miscellaneous analog tuning.
- Lane RX state: lane 1 RX request, reset, pstate, rate, width, termination, CDR/VCO load values, adaptation enable/continuous adaptation controls, EQ override values, RX valid/readback status, RX pstate recipes, RX power-up timers, and VCO status fields.
- Diagnostic and test state: analog test bus and alternate bus fields, OCLA selectors, RX statistic match/mask/sample/counter controls, calibration comparison clocking, loopback BERT control, DCC DAC diagnostics, directed TX coefficient/status readbacks, and cross-lane shift synchronization signals.

Persistence is hardware-defined. Configuration fields can remain until a modeset, link retraining pass, PHY/lane reset, power-gate transition, suspend/resume reinitialization, firmware action, or GPU reset rewrites them. Status, ACK, calibration, statistic, and diagnostic fields may be latched, sampled, clear-on-write, self-clearing, or only valid while the relevant clock and power domains are active. This generated header does not encode those semantics.

## Dependencies And Integration Points

This chunk is tightly coupled to the rest of the DPCS 4.2.0 generated register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_CR2_*` register offsets, including the same MPLL power-control groups at offsets such as `0x0061` onward and lane 1 RX VCO calibration groups around `0x1148` onward.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both the DPCS 4.2.0 offset and shift/mask headers when building DCN 3.1 resource definitions.
- AMD display `reg_helper.h`-style access macros and generated register tables consume these names indirectly; most runtime code will not mention every raw field name directly.
- Link encoder, PHY, clock-source, hardware sequencing, link-training, suspend/resume, and diagnostic paths depend on these masks to program lane power, clocking, PLL selection, MPLL calibration, RTUNE, DCC, RX VCO calibration, RX adaptation, and low-level lane status.
- Firmware and hardware state machines share ownership of some surfaces, especially override, calibration, clock-ready, request/ACK, cross-lane shift, OCLA/debug, and status fields. The header only describes bit layout, not ownership policy.

The constants are ASIC-version-specific. Nearby DPCS generations may have similarly named fields, but mixing this `dpcs_4_2_0_sh_mask.h` slice with another generation's offset table or hardware database can compile while programming the wrong register layout.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift or mask compiles cleanly but can write the wrong DPCS bit, corrupt reserved fields, or decode status incorrectly.
- Chunk boundaries are artificial. This slice starts after one `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3` shift and ends before `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_1`; whole-file research must reconcile adjacent chunks before treating those groups as complete.
- Repeated MPLLA/MPLLB and lane 0/lane 1 layouts are copy-sensitive. A generator error can affect one PLL bank, one lane, or one status register while nearby repeated groups appear correct.
- Override and normal ASIC-input fields often coexist. Writing a value without the matching override-enable bit may be ignored; leaving override bits set after diagnostics can bypass normal hardware sequencing.
- Power, clock, PLL, DCC, RTUNE, and VCO fields are sequencing-sensitive. Bad masks can produce blank displays, unstable link clocks, stuck resets, failed link training, RX adaptation failures, suspend/resume-only regressions, or high error rates.
- Status, ACK, clear, and mask fields can have side effects or transient validity. Confusing request, ACK, status, clear, and mask bits can cause missed events, stuck waits, repeated interrupts, or misleading diagnostics.
- Reserved fields are emitted as masks. Driver code should preserve reserved bits during read-modify-write unless the hardware specification explicitly requires a value.
- Timing fields are narrow packed bitfields. Consumers must mask or validate values before shifting so out-of-range values do not spill into adjacent controls.
- Analog/test/debug fields are not harmless metadata: ATB, alt-bus, termination, equalization, DCC, Vref, PMIX, RTUNE, and PLL controls can alter PHY electrical behavior or obscure useful debug evidence.

## Test Signals

Useful validation is a mix of generated-header checks and hardware behavior:

- Build AMDGPU display support for the DCN generation that includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`; missing, duplicate, or renamed macros should fail table initialization or preprocessor expansion.
- Mechanically verify that complete fields in this range have matching `__SHIFT` and `_MASK` definitions, allowing the expected boundary exception for `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3__meas_iv_bias`.
- Cross-check every complete `DPCSSYS_CR2_*` register group in this chunk against `dpcs_4_2_0_offset.h` and AMD's authoritative DPCS 4.2.0 register database.
- Diff repeated lane 0/lane 1 and MPLLA/MPLLB groups where the hardware spec expects identical layouts, while preserving intentional RX-only differences in the lane 1 section.
- Exercise DisplayPort and HDMI link bring-up, retraining, hotplug, stream disable/enable, high-bandwidth modes, and suspend/resume on hardware using DPCS 4.2.0. Watch for blank screens, clock lock failures, lane ACK timeout, RX adaptation failure, retraining loops, or DCC/VCO calibration failures.
- Inspect register dumps or PHY traces around MPLL lock/state, PCLK/output enable, RTUNE status, TX/RX pstate, DCC DAC ACK, RX statistic counters, RX VCO calibration status, lane clock-ready/data-enable, detect-RX, and cross-lane shift handshakes.
- Run diagnostics that use OCLA, LBERT, RX statistic match/count controls, analog test bus/readback, DCC DAC override, termination/equalization override, and RX VCO calibration readback to confirm masks decode expected bits.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`, including the `meas_iv_bias__SHIFT` line just before this range. This chunk covers the remainder of CR2 supervisor MPLLB/common control, lane 0 digital/analog TX and RX statistic surfaces, and the start of lane 1 digital TX/RX power and VCO calibration surfaces. The next chunk should continue with `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_1` and later lane 1 RX calibration/status definitions. The final per-file merge should treat this as one generated ASIC register map, not handwritten driver logic.
