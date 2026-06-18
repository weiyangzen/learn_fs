# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 61554-63931

## Purpose

This chunk is generated AMD DCN 3.2.0 register field metadata for C20 PHY lane control registers. It defines C preprocessor constants for field bit positions (`__SHIFT`) and bit masks (`_MASK`) under the `C20_PHY_CR0_*` namespace. There is no executable C logic here; the constants are consumed by AMDGPU/DC register helpers and firmware-facing register tables so software can compose or decode MMIO register values without hard-coding bit layouts.

The requested range contains 198 register groups and 2181 `#define` field macros. It begins inside the tail of `C20_PHY_CR0_LANE0_DIG_ANA_XF_RX_PWR_OVRD_OUT_1`, then covers the remaining lane0 RX analog cross-front-end masks, and then covers a large lane1 PHY slice: ASIC lane/TX controls, TX power and calibration/stat registers, lane1 TX analog front-end controls/status, lane1 RX ASIC override and status controls, RX power/VCO/CDR/adaptation controls, and the start of `RX_ADPTCTL_ADPT_CFG_9`. The final line stops after `ERR_SLO_ADPT_INIT__SHIFT`, so the corresponding masks for that register belong to the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata and has no Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

This chunk defines no functions, structs, enums, variables, locks, allocation paths, or includes. Its public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: least-significant bit position for a field.
- `REGISTER__FIELD_MASK`: register-positioned bit mask for isolating or updating the field.
- Comment lines such as `//C20_PHY_CR0_LANE1_DIG_RX_CDR_CDR_CTL_0`: generated register group markers.

Major macro families in this chunk:

- Lane0 RX analog masks: signal-detect calibration, high/low frequency signal-detect tuning, CDR/VCO enable/startup/frequency tuning overrides, RX calibration mux/DAC/VDAC controls, AFE trim, AFE attenuation/VGA/CTLE/bias/VCM overrides, scope/slicer/IQ controls, loopback, sampling selectors, termination-code overrides, status outputs, CREG analog test/override registers, and CREG override bits.
- Lane1 ASIC TX interface controls: lane loopback and transceiver-mode override, TX clock-ready/reset/invert/data-enable/request/low-power/P-state/rate/width/MPLL/flyover controls, TX equalization cursor fields, DCC/bypass/deskw/VREG controls, TX acknowledgements, RX-detect results, calibration status, and matching ASIC input/output readback fields.
- Lane1 TX power and timing controls: `TX_PSTATE_P0`, `P0S`, `P1`, and `P2` layouts for analog refgen, VCM hold, clock, reset, serializer, digital clock, data enable, RX detect, VBOOST, DCC, bleeder, and word-clock enable; power-up timing registers for refgen, clock, VCM hold, VBOOST disable, reset, RX detect, serial enable, and bleeder timing; `TX_CTL` and `TX_STATUS`.
- Lane1 TX calibration and diagnostics: TX DCC differential/common IDAC offset, DCC status, statistic load/control/sample/count/stop, calibration comparator clock control, clock-align controls/status, TX LBERT control and pattern registers, level-calculation status, FIFO control, analog DCC calibration control/data, TX status override/output groups, and TX analog CREG00-CREG05 plus CREG override registers.
- Lane1 ASIC RX interface controls: RX reset/invert/data-enable/request/low-power/P-state/DFE bypass, reference and VCO load values, div16p5 clock enable, CDR tracking/SSC, disable, VREG clock bypass, flyover, loopback, DCC controls, signal-detect LF/HF/filter overrides, CDR VCO config, equalizer ATT/VGA/CTLE/AFE/DFE tap overrides, RX acknowledgement/adaptation/status outputs, and matching ASIC input/readback fields.
- Lane1 RX power/VCO/CDR/adaptation controls: RX P-state definitions for AFE/VREG/DCC/clock/CDR/deserializer/bleeder/word-clock controls, RX power-up timing and control/status, VCO calibration controls/timers/status, RX LBERT control/error count, CDR phase detector/SSC/DPLL gain/frequency/bounds/status, and RX adaptation configuration registers 0-9.

Representative field names that consumers must treat as hardware contracts include `*_OVRD_VAL`, `*_OVRD_EN`, `PSTATE`, `RATE`, `WIDTH`, `TX_MAIN_CURSOR`, `TX_PRE_CURSOR`, `TX_POST_CURSOR`, `TX_DCC_CTRL_RANGE`, `RX_DCC_CTRL_RANGE`, `SIGDET_*`, `CDR_*`, `VCO_*`, `DFE_TAP*`, `CTLE_*`, `VGA_*`, `ATT_*`, `LBERT_*`, `DPLL_FREQ`, `FREQ_BOUND_*`, `N_TOP_ASM1`, `N_WAIT_ASM1`, `CTLE_EN`, `DFE_EN`, `EYEH*_EN`, and `ERR_SL*_ADPT_INIT`.

## Control Flow

The header has no runtime control flow. Runtime behavior appears when DCN 3.2 display, interrupt, firmware, and memory-management code includes `dcn_3_2_0_offset.h` with this `_sh_mask` header and expands register-field tables or `FD_MASK`/`FD_SHIFT` expressions. The relevant pattern is:

1. A DCN 3.2 source file includes the matching offset and shift/mask headers.
2. Register-list macros supply register addresses from `dcn_3_2_0_offset.h`.
3. Shift/mask-list macros or `FD_MASK`/`FD_SHIFT` build typed tables from this header's constants.
4. Runtime helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or DMUB register accessors write, read, or poll hardware fields.

The chunk's PHY fields represent sequencing-sensitive parts of link bring-up and diagnostics even though the sequencing is not encoded here. Typical hardware sequences include enabling lane power states, waiting power-up timers, asserting/deasserting reset, selecting lane rate/width/MPLL, programming TX EQ cursors, enabling DCC calibration, reading status/ack bits, programming RX CDR/VCO and signal-detect controls, running VCO calibration, measuring LBERT errors, and enabling RX adaptation loops for CTLE/VGA/ATT/DFE.

The DCN 3.2 resource code in this tree includes this header, but its DPCS/RDPCS link encoder register-list use is commented out around the DCN32 link encoder tables. That means many C20 PHY lane macros in this slice may be low-level generated coverage for firmware, bring-up, diagnostics, or future paths rather than heavily referenced by high-level display link-encoder code in this repository snapshot.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes MMIO-backed PHY state:

- Lane0 RX analog state: signal-detect calibration, CDR/VCO tuning, RX calibration DACs, AFE/equalizer analog overrides, scope/slicer/IQ controls, loopback, sampling selectors, termination code, status outputs, and analog CREG test/override state.
- Lane1 TX state: lane loopback/transceiver mode, TX control overrides, requested P-state/rate/width, TX main/pre/post cursor values, VBOOST/IBOOST/flyover/MPLL settings, DCC ranges/calibration data/status, power-state recipes, power-up timing, clock alignment, LBERT pattern generation, FIFO controls, and TX analog CREG state.
- Lane1 RX state: RX control overrides, reference/VCO load values, signal-detect thresholds, CDR tracking/SSC/VCO/DPLL configuration, EQ and DFE tap overrides, RX power-state recipes, VCO calibration state, LBERT error counters, DPLL frequency bounds/status, and adaptation-loop thresholds/mu settings.

Persistence is hardware-defined. Configuration fields generally remain in the PHY registers until the driver, firmware, reset, link reinitialization, suspend/resume, or power-gating transition changes them. Status, ack, counter, error, calibration, and sticky fields may be read-only, self-clearing, write-one-to-clear, or timing-sensitive depending on the underlying register; this generated header only describes the bit layout and not access policy.

## Dependencies And Integration Points

The file depends only on the C preprocessor and its include guard, but it must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies matching register offsets such as the C20 PHY lane/adaptation offset families. A shift/mask macro without the corresponding offset is not directly useful to register helpers, and an offset paired with the wrong mask silently targets the wrong bits.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`, which initializes DMUB-facing DCN32 register offsets, masks, and shifts via `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`, which builds DCN32 resource register, shift, and mask tables. Its DPCS/RDPCS link-encoder table blocks are commented out, but the header remains part of the DCN32 resource include set.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, and `display/dc/gpio/dcn32/hw_translate_dcn32.c`, which use the same generated DCN32 register metadata pattern for display, clock, GPIO, and interrupt integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`, which includes the DCN32 generated header set alongside memory-hub and VM fault code.

Functional integration points are link and PHY management: DisplayPort/HDMI PHY lane bring-up, link training, transmitter equalization, receiver adaptation, power management, VCO/CDR calibration, DCC calibration, diagnostic loopback, LBERT test patterns/error counts, and firmware-visible register programming.

## Risks And Edge Cases

- Field drift is the primary risk. These are untyped constants; a wrong shift or mask can compile cleanly while corrupting adjacent PHY fields during read-modify-write.
- The range is artificially bounded. It starts with only the final masks for `LANE0_DIG_ANA_XF_RX_PWR_OVRD_OUT_1`, omitting the matching shifts in the prior chunk, and it ends inside `LANE1_DIG_RX_ADPTCTL_ADPT_CFG_9`, before the masks for `ERR_SLE_ADPT_INIT` and `ERR_SLO_ADPT_INIT`.
- Reserved-bit masks are present throughout. Generic writes that fail to preserve reserved bits can change undocumented PHY behavior, particularly in analog CREG, calibration, and power-state registers.
- Override enable/value pairs must stay coordinated. Setting an override value without the matching `*_OVRD_EN`, or leaving an override enabled after diagnostics, can defeat firmware or hardware state machines.
- TX power-state recipes are repeated for P0/P0S/P1/P2 with similar layouts. Copying values between states without respecting intended low-power behavior can break fast training, RX detect, VBOOST, DCC, word-clock, or serializer sequencing.
- RX adaptation and CDR fields are link-quality-sensitive. Bad CTLE/VGA/ATT/DFE thresholds, mu values, signal-detect thresholds, DPLL frequency bounds, or VCO calibration masks may only fail on marginal cables, high link rates, spread-spectrum clocks, suspend/resume, or retimer paths.
- Status/counter fields such as LBERT errors, VCO status, DPLL status, adaptation status, and TX/RX ack/calibration fields may have read-only or sticky semantics not represented in this header.
- The DCN32 resource file comments out DPCS/RDPCS link encoder table construction in this snapshot. If future code enables those tables or firmware paths depend on these C20 PHY fields, stale generated metadata can become active without local source changes in this chunk.

## Test Signals

Useful validation for consumers of these macros includes:

- Build AMDGPU/DC with DCN32 support enabled. Missing or renamed macros should fail in DMUB DCN32, IRQ, GPIO, clock-manager, GMC, or resource code that expands generated field names.
- Mechanically compare lines 61554-63931 against AMD's authoritative DCN 3.2.0/C20 PHY register database and adjacent generated DPCS headers for compatible C20 PHY revisions.
- Verify each complete register group in the chunk has expected `__SHIFT`/`_MASK` pairs, while explicitly allowing the first and last partial groups to be completed by adjacent chunks.
- Exercise DP/HDMI link bring-up, link training, high bit-rate modes, hotplug, fast link retraining, suspend/resume, runtime power management, and ASIC reset on DCN 3.2 hardware.
- Check transmitter behavior across voltage swing/pre-emphasis changes, TX main/pre/post cursor programming, VBOOST/IBOOST settings, RX detect, DCC calibration, clock alignment, and PHY P-state transitions.
- Check receiver behavior across CDR lock, signal detect, VCO calibration, DPLL frequency bounds, CTLE/VGA/ATT/DFE adaptation, and error-rate stress cases.
- Run PHY diagnostics when available: loopback paths, LBERT pattern/error-count tests, calibration status polling, and register trace comparison against known-good firmware/driver logs.

## Cross-Chunk Notes

The preceding chunk owns the beginning of `C20_PHY_CR0_LANE0_DIG_ANA_XF_RX_PWR_OVRD_OUT_1` and earlier lane0 PHY fields. The following chunk owns the masks for `C20_PHY_CR0_LANE1_DIG_RX_ADPTCTL_ADPT_CFG_9` and continues the lane1 RX adaptation/reset/status register families. The final per-file report should merge adjacent chunks before making complete claims about all C20 PHY lanes, all RX adaptation registers, or the full DCN 3.2.0 generated register map.
