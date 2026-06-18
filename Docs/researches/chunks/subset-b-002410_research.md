# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 58382-60803

## Scope

This chunk is a generated AMD DPCS 4.2.3 shift/mask header segment for the `DPCSSYS_CR2` register block. It covers 2,422 lines and 2,159 `#define` entries, with 263 register-group comments. The range starts inside `DPCSSYS_CR2_LANEX_DIG_ASIC_RX_OVRD_EQ_IN_0`: the first lines in this chunk are masks whose shifts appear immediately before line 58382. It ends inside the raw-lane IRQ clear group after `DPCSSYS_CR2_RAWLANEX_DIG_IRQ_CTL_RX_ADAPT_DIS_IRQ_CLR`; later IRQ mask and additional IRQ/status groups continue in the next chunk.

The content is declarative hardware metadata only. It has no functions, structs, enums, variables, includes, branches, loops, allocation, locking, or direct MMIO calls. Its exported interface is the macro namespace used by AMDGPU display code to compose and decode DPCS 4.2.3 indirect register fields.

## Purpose

The header gives the AMD display driver symbolic bitfield definitions for DPCS 4.2.3 PHY registers. Consumer code pairs these `__SHIFT` and `_MASK` constants with register addresses from `dpcs_4_2_3_offset.h` and with AMD display register helpers to perform read/modify/write, status decode, interrupt clear, and diagnostic operations without embedding raw bit numbers.

This chunk specifically covers a CR2 lane-X and raw-lane slice:

- ASIC lane interface overrides and ASIC input/output mirrors for RX equalization, TX/RX requests, reset, low-power detect, pstate, rate, width, MPLL selection, loopback, async data, and acknowledgements.
- Lane TX and RX power-control programming, including pstate registers, power-up timing, TX DCC DAC control, TX clock alignment, and LBERT controls.
- RX VCO calibration, RX alignment, RX LBERT, CDR, DPLL frequency/bounds, RX adaptation configuration, DFE tap/readback status, slicer and VDAC offsets, adaptation reset, and CR bank address/data access.
- RX statistic capture controls and counters.
- MPHY low-speed RX controls, digital analog TX/RX override outputs, raw analog TX/RX control/status/test-bus fields, and signal-detect or DCC DAC override outputs.
- Raw-lane PCS transfer fields, FSM monitor/fast-calibration fields, and the beginning of raw-lane IRQ status/clear definitions.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata and does not implement distributed filesystem or Ceph behavior.

## Important APIs, Types, And Macros

There are no callable APIs or local C types. The public surface follows the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` names the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK` names the mask used to isolate, compose, or update that field.

Important macro families in this range:

- `DPCSSYS_CR2_LANEX_DIG_ASIC_*`: lane-X digital ASIC-facing controls and status. These include RX/TX override input banks, ASIC input mirrors, ASIC output/ACK mirrors, lane loopback bits, TX main/pre/post cursor fields, RX EQ attenuation/VGA/CTLE/DFE fields, RX CDR VCO/ref load values, async data, detect-RX request/result, and override-enable bits.
- `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_*`: TX pstate configuration, pstate validity/standby/power-down fields, TX power-up timers, DCC CR-bank address/data, DCC DAC control/range/select/ACK/address, TX clock alignment, and TX LBERT enable/status fields.
- `DPCSSYS_CR2_LANEX_DIG_RX_PWRCTL_*`: RX pstate and power-up timing definitions.
- `DPCSSYS_CR2_LANEX_DIG_RX_VCOCAL_*`: RX VCO calibration control, period/wait/load-value programming, reference/VCO load values, and VCO status readback.
- `DPCSSYS_CR2_LANEX_DIG_RX_*`: RX alignment mask, LBERT control/error status, CDR controls/status, DPLL frequency and bounds, adaptation configuration, DFE tap status, VDAC offsets, slicer controls, adaptation reset, DAC select, and CR bank access.
- `DPCSSYS_CR2_LANEX_DIG_RX_STAT_*`: RX statistic/match engine fields, including sample load, data masks, match controls, statistic controls, sample/stat counters, calibration-comparison clock control, extended match controls, and stop control.
- `DPCSSYS_CR2_LANEX_DIG_MPHY_*`: MPHY low-speed RX PWM, termination, and analog PWM clock-stability fields.
- `DPCSSYS_CR2_LANEX_DIG_ANA_*`: digital views of analog TX/RX override outputs and status, covering TX enable/clock/reset/data, TX termination and EQ, RX CTLE/VCO/power/slicer/scope/DAC/calibration controls, IQ phase/sense/calibration toggles, PLL lock/readback status, term-code clocks, MPHY overrides, signal-detect overrides, and TX DCC DAC overrides.
- `DPCSSYS_CR2_LANEX_ANA_TX_*` and `DPCSSYS_CR2_LANEX_ANA_RX_*`: raw analog lane controls for TX power/measurement/test bus/DCC/termination/miscellaneous fields and RX clock/CDR/deserializer/slicer/power/squelch/calibration/ATB fields.
- `DPCSSYS_CR2_RAWLANEX_DIG_PCS_XF_*`: raw lane PCS transfer/override fields for TX/RX reset, request, pstate, rate, width, MPLL selection, loopback, data enable, adaptation, FOM, directed TX equalization feedback, lane number, ATE override, termination control, RX EQ override, and PH2 calibration.
- `DPCSSYS_CR2_RAWLANEX_DIG_FSM_*`: raw lane FSM override/status monitors and fast-flow bits for RX startup, adaptation, AFE/DFE/bypass/ref-level/IQ calibration, supervisor/TX common-mode/RX detect/RX power-up/VCO wait/VCO calibration states, common MPLL/RCAL status, continuous calibration/adaptation states, CR lock, TX DCC flags/status, OCLA, TX EQ update flag, and RX IQ phase offset.
- `DPCSSYS_CR2_RAWLANEX_DIG_IRQ_CTL_*`: the beginning of the raw-lane interrupt model, including reset-return request, RX reset/request/rate/pstate/adaptation status bits, and matching clear bits through RX adaptation-disable clear.

Most masks are 16-bit-style constants with an `L` suffix, consistent with the DPCS indirect register width used by these lane, raw-lane, and analog register blocks.

## Control Flow

This file has no runtime control flow. It participates in compile-time register metadata construction:

1. AMD display resource code for DCN 3.1.6 includes `dpcs_4_2_3_offset.h` and this shift/mask header.
2. Register tables, shift tables, and mask tables use these generated names to bind register offsets to field layouts.
3. Runtime code outside this header uses AMD register helpers to read, write, update, poll, or decode the DPCS fields.
4. Hardware and firmware state machines implement the real sequencing for lane power, TX/RX handshakes, link training, CDR/VCO calibration, RX adaptation, DCC, statistic capture, loopback, test-bus access, and interrupts.

The macros only describe bit layout. They do not encode reset values, access direction, write-one-to-clear behavior, self-clearing behavior, valid clock/power domains, polling timeouts, or required operation ordering.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. The named fields correspond to hardware-visible state in CR2 lane-X and raw-lane DPCS registers:

- TX/RX lane state: reset, request, ACK, data enable, low-power detect, pstate, rate, width, MPLL select, TX main/pre/post cursor settings, loopback, async data, detect-RX request/result, and TX/RX disable controls.
- Calibration/adaptation state: RX EQ attenuation/VGA/CTLE/DFE values, CDR/VCO/ref load values, VCO calibration settings/status, CDR and DPLL controls, DFE tap status, even/odd VDAC offsets, slicer controls, error levels, adaptation reset, and DAC selection.
- Power and timing state: TX/RX pstate entries, pstate standby/powerdown behavior, TX/RX power-up timers, MPHY PWM/termination controls, and analog clock-stability counters.
- Analog and diagnostic state: TX/RX analog override outputs, termination-code clocks, PLL lock/readback status, signal-detect override/status, raw analog TX/RX power, CDR, deserializer, slicer, squelch, calibration, ATB/test-bus, measurement, and miscellaneous controls.
- Raw PCS/FSM/IRQ state: raw lane PCS/PMA-facing transfer signals, RX adaptation ACK/FOM, directed TX EQ feedback, PH2 calibration, fast FSM state bits, continuous calibration/adaptation flags, CR lock, TX DCC status, OCLA capture selectors, TX EQ update flags, RX IQ phase offset, and early raw-lane IRQ status/clear bits.

Persistence is hardware-defined. Configuration fields remain until driver reprogramming, modeset/link retraining, low-power transitions, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware sequencing rewrites them. Status, ACK, statistics, interrupt, and calibration fields may be latched, sampled, volatile, clear-on-write, self-clearing, or only valid while relevant clocks and power domains are active. Reserved fields are explicitly represented and should be preserved by read/modify/write users.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is AMD's DPCS 4.2.3 register database and the companion address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies matching `ixDPCSSYS_*` register offsets. In that header, this chunk maps from `ixDPCSSYS_CR2_LANEX_DIG_ASIC_RX_OVRD_EQ_IN_0` at `0x900d` through lane-X power/RX/stat/analog blocks around `0x9010`-`0x90ff`, then into raw-lane PCS/FSM/IRQ blocks starting at `0xe000`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`, making DCN 3.1.6 resource setup the visible in-tree consumer.
- Higher-level AMDGPU display paths consume these constants indirectly through generated register, shift, and mask tables used by link encoder, PHY bring-up, clocking, DisplayPort/HDMI link training, diagnostics, hotplug, modeset, power management, and interrupt handling.

Integration is low-level and hardware-facing. The macros describe field layout for the DPCS lane/PHY control plane; they do not expose a stable driver API by themselves.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but can update the wrong hardware bit, corrupt a neighboring field, or decode status incorrectly.
- This chunk has artificial boundaries. It starts after the shift definitions for `DPCSSYS_CR2_LANEX_DIG_ASIC_RX_OVRD_EQ_IN_0` and ends before the rest of the raw-lane IRQ control block. Merge/reconciliation must avoid treating the boundary groups as complete here.
- Many registers pair override value fields with separate override-enable fields. Programming a value without its enable bit may do nothing; leaving an enable bit asserted after debug or test use can force the PHY away from normal hardware state-machine control.
- TX/RX pstate, rate, width, MPLL, CDR, DPLL, VCO, DCC, and adaptation fields are sequencing-sensitive. Bitfield mistakes can manifest as link-training failures, unstable clocks, blank displays, retraining loops, or rate-specific regressions.
- Analog and test-bus fields can affect electrical behavior. Incorrect termination, EQ, signal-detect, slicer, squelch, DCC, ATB, or calibration masks may produce compliance failures or misleading diagnostic readbacks.
- IRQ status and clear fields have repeated names with only suffix differences. Consumers must respect the hardware access semantics from the register spec; this header does not say whether a clear bit is write-one-to-clear, self-clearing, or level-sensitive.
- Reserved masks occupy many high-bit ranges. Driver code should preserve reserved fields and avoid using full-register writes unless the surrounding register programming sequence owns every bit.
- Raw-lane and lane-X register families are repeated across DPCS generations. Copy or generator errors can affect only one version or one lane class while nearby macros look plausible.

## Test Signals

Useful validation is mostly build-time, generated-header, and hardware-integration oriented:

- Build AMDGPU display support for DCN 3.1.6 so `dcn316_resource.c` includes this header and any missing or renamed field macro fails table initialization.
- Mechanically verify complete register groups in this line range have matching shift and mask definitions, allowing the known split at `DPCSSYS_CR2_LANEX_DIG_ASIC_RX_OVRD_EQ_IN_0` at the start and the raw-lane IRQ continuation after line 60803.
- Cross-check every complete register group in this chunk against `dpcs_4_2_3_offset.h`, especially the transition from lane-X offsets around `0x900d`-`0x90ff` into raw-lane PCS/FSM/IRQ offsets around `0xe000`-`0xe04c`.
- Compare against AMD's source register database and nearby generated variants such as DPCS 4.2.0 to catch unintended field-width, shift, or mask differences.
- Exercise DisplayPort/HDMI bring-up across supported lane counts, rates, widths, and power states. Expected signals include stable link training, correct TX/RX request/ACK transitions, correct MPLL selection, clean VCO/CDR lock behavior, and successful RX adaptation.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch stale override enables, lost pstate programming, bad power-up timers, or uninitialized analog/calibration fields.
- Use register dumps or PHY debug traces during failures to confirm that RX EQ/DFE tap status, CDR/DPLL/VCO state, DCC status, statistic counters, FSM fast flags, OCLA selections, and raw-lane IRQ status/clear bits decode correctly.
- Exercise diagnostic and manufacturing-style paths where available: LBERT, loopback, RX statistic match/count controls, OCLA, analog test-bus/readback, directed TX coefficient feedback, PH2 calibration, MPHY low-speed controls, and ATE/override banks.

## Chunk Notes For Merge

This document intentionally covers only lines 58382-60803 of `dpcs_4_2_3_sh_mask.h`. Earlier chunks own the start of the lane-X ASIC override region, including the missing shifts for the first boundary register in this chunk. Later chunks should finish the raw-lane IRQ control block and continue subsequent PMA/TX/RX/ATE or later address-block definitions. The final per-file research document should describe the whole file as a generated DPCS 4.2.3 ASIC register bitfield map with `dcn316_resource.c` and the matching offset header as the primary in-tree integration anchors.
