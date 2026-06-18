# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 105624-108006

## Scope

This chunk is a generated AMDGPU DCN 4.1.0 shift/mask header slice. It contains preprocessor constants only: no C functions, structs, enums, global storage, locks, allocation paths, or executable logic. Its exported contract is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace used by register-helper code to pack and unpack bitfields.

The requested range covers DPCSSYS CR2 internal PHY/register metadata. It starts in the middle of `DPCSSYS_CR2_SUP_DIG_LVL_OVRD_IN` after the first field's shift, then covers most of the CR2 supervisor digital/analog PLL and tuning register set, all of the CR2 lane0 digital/analog TX/RX groups in this range, and the beginning of CR2 lane1 TX/RX override fields. It ends inside `DPCSSYS_CR2_LANE1_DIG_ASIC_RX_OVRD_IN_4`, before the final masks for that register and the following lane1 RX equalization/status/lane input definitions.

This is AMD display/link PHY metadata despite the repository path containing `ceph-client`. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this chunk is to describe bit layout for CR2 DisplayPort/HDMI PHY control registers in DCN 4.1.0. These definitions allow DCN/DPCS/link-encoder code or generated tooling to address individual fields without hard-coding bit positions.

The covered hardware areas are:

- CR2 supervisor digital input and override fields for link reference behavior, level selection, PLL selection, PLL enable/standby/calibration, fractional-N and spread-spectrum controls, divided/HDMI clocks, PHY reset, reference-clock enable, RTUNE handshake state, and test/powerdown bits.
- CR2 supervisor analog fields for prescaler, RTUNE, bandgap, pre-regulator, VREF generator, MPLL A/B common analog controls, charge pump settings, loop/filter/DAC controls, lock controls, PMIX controls, and analog test bus selections.
- CR2 digital MPLL power-control/status fields for both MPLLA and MPLLB, including override enables, powerdown/run enable, clock-ready state, lock state, timer programming, calibration request/status, DAC output state, and spread-spectrum generator type.
- CR2 clock/reset and RTUNE state fields for bandgap/reference-clock power-up timing, VPH under-drive behavior, RTUNE counters, configured set values, measured status values, and TX calibration codes.
- CR2 supervisor-to-analog override output fields for MPLLA/MPLLB, RTUNE, bandgap, and PMIX values flowing toward the analog PHY.
- CR2 lane0 digital ASIC override, ASIC input/output, TX power-control, DCC DAC, clock-align, LBERT, RX status, and analog TX override/status/control fields.
- CR2 lane1 digital ASIC lane override and TX/RX override fields through the middle of `LANE1_DIG_ASIC_RX_OVRD_IN_4`.

The range contains 2,188 `#define` entries across 195 register-comment blocks. A simple count over the requested lines finds 1,103 `__SHIFT` occurrences and 1,093 `_MASK` occurrences because the artificial chunk boundary begins and ends inside register definitions rather than on complete register blocks.

## Important APIs, Types, And Macros

There are no callable APIs or concrete C types in this chunk. The important interface is the generated macro convention:

- `DPCSSYS_CR2_<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field.
- `DPCSSYS_CR2_<REGISTER>__<FIELD>_MASK`: already-shifted mask for that field.

Major macro families in this slice are:

- `DPCSSYS_CR2_SUP_DIG_MPLLA_ASIC_IN_*` and `DPCSSYS_CR2_SUP_DIG_MPLLB_ASIC_IN_*`: digital inputs for two MPLLs, including enable, div5 clock enable, TX clock divider, V2I, standby, VCO frequency, calibration force, fractional-N enable, multiplier, SSC enable/up-spread, PMIX enable, word-div2, config-update, clock sync, SSC peak, and SSC step-size fields.
- `DPCSSYS_CR2_SUP_DIG_MPLLA_DIV_CLK_ASIC_IN`, `MPLLA_HDMI_CLK_ASIC_IN`, `MPLLB_DIV_CLK_ASIC_IN`, and `MPLLB_HDMI_CLK_ASIC_IN`: divided and HDMI pixel clock divisors for the two MPLLs.
- `DPCSSYS_CR2_SUP_DIG_ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, `MPLLA_CP_ASIC_IN`, `MPLLA_CP_GS_ASIC_IN`, `MPLLB_CP_ASIC_IN`, and `MPLLB_CP_GS_ASIC_IN`: supervisor input state for PHY reset/reference clock/test mode, RX VREF/TX swing levels, bandgap enable, and charge-pump current/prop/int gain settings.
- `DPCSSYS_CR2_SUP_ANA_*`: analog control/status field maps for prescaler DCO range/fine-tune, RTUNE timing and trim, bandgap current/RCAL/VREF/regulator controls, VREF force/probe, MPLLAB miscellaneous controls, MPLLAB overrides, analog test bus, VREG controls, outclk controls, lock controls, loop controls, charge pump, VCO, PMIX, and reserved/debug fields.
- `DPCSSYS_CR2_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR2_SUP_DIG_MPLLB_MPLL_PWR_CTL_*`: digital power/control/status registers for each MPLL, including enable/run override bits, state readback, DAC max range, lock/stable timers, calibration, DAC output, and SSC spread type.
- `DPCSSYS_CR2_SUP_DIG_CLK_RST_*` and `DPCSSYS_CR2_SUP_DIG_RTUNE_*`: clock/reset sequencing and resistor-tuning metadata, including power-up timers, RTUNE done/mode/count values, RX/TX set values and status values, config counters, and TX calibration code fields.
- `DPCSSYS_CR2_SUP_DIG_ANA_*_OVRD_OUT` and `DPCSSYS_CR2_SUP_DIG_ANA_STAT`: override output/readback fields for analog MPLL, RTUNE, bandgap, and PMIX paths.
- `DPCSSYS_CR2_LANE0_DIG_ASIC_*`: lane0 digital lane/TX/RX override and ASIC input/output fields. These include request/override enables, pstate, rate, width, MPLLB select, data enable, transmit cursor/pre/post cursor, async driver, HDMI mode, clock ready, detect-RX request/result, inversion, low-power detect, DC coupling, FIFO, MPHY mode, reset, boost controls, lane transceiver mode, DCC bypass, TX ack, RX ack/adaptation/async/squelch state, and loopback.
- `DPCSSYS_CR2_LANE0_DIG_TX_PWRCTL_*`: TX pstate P0/P0S/P1/P2 configuration, pre/main/post cursor settings, lane mode, pstate powerdown and ready acknowledgement behavior, TX power-up timers, and DCC DAC access/control/ack/address fields.
- `DPCSSYS_CR2_LANE0_DIG_RX_STAT_*`: RX status/load/match/stat-counter controls for observing and matching RX data patterns, sample count, status counters, calibration compare clock, and match controls.
- `DPCSSYS_CR2_LANE0_DIG_ANA_TX_*` and `DPCSSYS_CR2_LANE0_ANA_TX_*`: lane0 analog TX override/status/control fields for TX power, term codes, EQ coefficients, DCC DAC, PMOS/NMOS/boost/driver controls, measurements, alternate bus, ATB, DCC, clock override, misc controls, select mux, VREG, and reserved analog registers.
- `DPCSSYS_CR2_LANE1_DIG_ASIC_*`: lane1 starts in this chunk and repeats the lane digital override pattern through RX low-power/invert/adaptation/termination fields.

Most fields in this range are 16-bit CR-style masks (`0xFFFFL` or narrower 16-bit masks). Many registers include explicit reserved fields. Those reserved masks are still part of the generated ABI because they document occupied/unused bit ranges and help mechanical comparison against the hardware register database.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by code that includes DCN 4.1.0 generated headers, builds register/field tables, and then uses AMDGPU display register helpers.

Visible integration in this tree includes:

1. `display/dc/resource/dcn401/dcn401_resource.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, and `display/dmub/src/dmub_dcn401.c` include both `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. DCN401 code uses token-paste helpers such as `SR`, `SRI`, field-list macros, `FD_MASK(reg, field)`, and `FD_SHIFT(reg, field)` to turn generated names into offsets, masks, and shifts.
3. Generic display helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use those tables to perform MMIO reads and read-modify-writes.
4. For DPCS/PHY CR access specifically, `dcn_4_1_0_offset.h` exposes CR2 address/data doorbell-style registers such as `regDPCSSYS_CR2_DPCSSYS_CR_ADDR` and `regDPCSSYS_CR2_DPCSSYS_CR_DATA`, and also aliases the same aperture through `regRDPCSTX2_RDPCS_TX_CR_ADDR` and `regRDPCSTX2_RDPCS_TX_CR_DATA`. Earlier/later DPCS headers and link-encoder headers show the common pattern of using `RDPCS_TX_CR_ADDR`/`RDPCS_TX_CR_DATA` to access PHY CR spaces.

The shift/mask macros in this particular range do not themselves encode programming order. Callers or generated PHY programming sequences must still handle PLL bring-up, reset release, RTUNE request/ack, calibration, clock-stable polling, power-state transitions, DCC DAC access, and lane TX/RX override sequencing.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes hardware register fields whose state lives in the DCN/DPCS PHY and is controlled by link training, modeset, hotplug, display power management, suspend/resume, and ASIC reset paths.

State represented by this chunk includes:

- PLL state for MPLLA/MPLLB: enable/standby, VCO frequency, dividers, fractional-N, multiplier, SSC peak/step-size, PMIX, charge-pump/current/gain, calibration request/status, lock state, and clock-ready state.
- Reference and supervisor state: PHY reset, reference clock enable/source, test/burn-in/powerdown controls, RTUNE request/ack, MPLL state bits, bandgap enable/state, pre-regulator controls, VREF generator values, and power-up timers.
- Analog tuning state: prescaler DCO range/fine tuning, RTUNE timing/count/set/status values, TX calibration code, VREG levels, loop/filter/DAC values, lock controls, and analog test/probe selections.
- Lane0 TX/RX control state: request, pstate, rate, width, data enable, MPLL selection, TX cursor/pre/post values, TX/RX override enables, reset, inversion, low-power detect, DC coupling, FIFOs, transceiver mode, boost controls, loopback, DCC DAC address/data/control, and RX match/stat counters.
- Lane0 analog TX state: TX power override, term code override, EQ override outputs, DCC DAC override, PMOS/NMOS/boost/driver values, measurement controls, alternate-bus and ATB controls, VREG settings, and mux/reserved debug settings.
- Lane1 partial state: lane override, TX override, TX ack/detect-RX result, and RX override fields through low-power/invert/adaptation/termination controls.

Persistence is hardware-defined. Configuration fields generally remain until rewritten, the relevant PHY/lane is reset, link encoder state is rebuilt, a power-gating transition drops the domain, suspend/resume restores state, or the GPU/ASIC is reset. Status and handshake fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while clocks and power are present. This generated header does not encode those access semantics.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which provides the DCN 4.1.0 register offsets and base indices. For CR2 PHY access, that offset header exposes the address/data MMIO registers used to reach internal CR fields; this shift/mask chunk supplies the bit geometry for those internal fields.

Important integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`: includes this generated header and defines `SR`/`SRI`/`SRI_ARR` and base-index expansion patterns for DCN401 hardware object register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c`: includes the DCN 4.1.0 generated offset and shift/mask headers for IRQ-source register metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`: includes the same generated headers for DCN401 clock-manager register programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` and `dmub_dcn401.h`: use `FD_MASK` and `FD_SHIFT` to initialize DMUB-facing field tables from `dcn_4_1_0_sh_mask.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.h`, `dcn20_link_encoder.h`, and `dcn31_dio_link_encoder.h`: show the generic link-encoder table fields and `RDPCS_TX_CR_ADDR`/`RDPCS_TX_CR_DATA` access pattern used for DPCS PHY CR programming across generations.
- Nearby generated DPCS headers under `include/asic_reg/dpcs/`, which carry equivalent `DPCSSYS_CR*` and `RDPCSTX*` CR-address/data and field layouts for other DPCS versions. These are useful for cross-generation sanity checks but are not interchangeable with DCN 4.1.0.

Not every macro in this CR2 slice is visibly token-pasted by current C code in this tree. That is expected for generated hardware databases: some fields are consumed by firmware tables, debug tooling, board/ASIC-specific sequences, or future code paths, and some are retained for completeness against the silicon register specification.

## Risks And Edge Cases

- Shift/mask constants are untyped preprocessor values. A wrong value can compile cleanly while writing the wrong PHY bit, corrupting adjacent fields, or decoding status incorrectly.
- CR2 is an internal PHY CR space accessed through address/data apertures. Misprogramming can affect link PLLs, reference clocks, RTUNE, lane power, TX equalization, RX adaptation, and DCC calibration rather than a simple display-pipe software variable.
- The chunk starts inside `DPCSSYS_CR2_SUP_DIG_LVL_OVRD_IN`; `RX_VREF_CTRL__SHIFT` is in the previous chunk while the enable, TX swing, VCO VREF, and masks are here. Pairing checks must account for this boundary.
- The chunk ends inside `DPCSSYS_CR2_LANE1_DIG_ASIC_RX_OVRD_IN_4`; masks for `RX_DCC_BYP_AC_CAP`, `RX_DCC_BYP_AC_CAP_OVRD_EN`, and `RESERVED_15_12` continue in the next chunk.
- PLL and clock fields are sequencing-sensitive. Enabling MPLL, changing multipliers/dividers/SSC, forcing calibration, or altering lock/timer fields at the wrong time can cause link-training failure, unstable pixel clocks, intermittent blanking, or resume-only failures.
- RTUNE and calibration fields cross analog/digital boundaries. Confusing request/ack/status/set-value fields can leave termination or TX calibration stale while software believes tuning completed.
- Lane TX cursor/pre/post and boost fields affect signal integrity. Incorrect masks may only fail with certain link rates, cable lengths, sink devices, DisplayPort link training levels, HDMI modes, or high-bandwidth modes.
- RX adaptation, termination, VCO/ref load, CDR, align, invert, and low-power-detect fields can create failures that look like sink compatibility or hotplug problems.
- Reserved fields are present throughout the generated output. Callers must avoid treating reserved masks as safe write targets unless an authoritative PHY sequence explicitly requires them.
- Repeated MPLLA/MPLLB and lane0/lane1 naming is copy-error prone. A table or generated sequence that mixes A/B PLL fields or lane instance fields can work on one topology and fail on another.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Build AMDGPU display support with DCN401 enabled. Missing or renamed generated macros should fail in DCN401 resource, IRQ, clock-manager, DMUB, or link-encoder table construction when referenced.
- Run mechanical consistency checks over this range against AMD's authoritative DCN 4.1.0 register database: every complete field should have matching `__SHIFT` and `_MASK` definitions with expected widths, while allowing the known start/end boundary exceptions.
- Compare this CR2 range with nearby DPCS/DCN generated headers where CR2 PHY layouts are expected to be shared, while explicitly reviewing generation-specific changes.
- Exercise DisplayPort and HDMI link bring-up on DCN401 hardware at multiple link rates, lane counts, color depths, and pixel clocks; watch for link-training retries, blank display, unstable clock, or hotplug failures.
- Validate suspend/resume, runtime power management, and GPU reset paths with active external displays, because PLL, RTUNE, bandgap, lane reset, and calibration state must be restored or reinitialized correctly.
- Test DP link training levels and HDMI modes that stress TX swing/pre/post cursor, boost, MPLL selection, divided clock, and HDMI pixel-clock divisor fields.
- Exercise long-cable/marginal-sink scenarios and high-bandwidth modes to expose RX adaptation, CDR, termination, VREF, DCC, and signal-integrity errors.
- Use debugfs, register dumps, firmware traces, or vendor register-validation tooling where available to confirm that CR2 address/data accesses program the intended internal fields.
- Watch kernel logs and display diagnostics for link-training failures, HPD storms, clock-not-ready/lock timeouts, RTUNE/calibration timeout, PHY reset loops, underflow caused by unstable link clocks, and resume-only display loss.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR2_SUP_DIG_LVL_OVRD_IN`, including the missing `RX_VREF_CTRL__SHIFT` for the masks at the start of this range. This chunk then covers the bulk of CR2 supervisor, PLL, RTUNE, lane0, and lane1-start metadata. The next chunk continues `DPCSSYS_CR2_LANE1_DIG_ASIC_RX_OVRD_IN_4` and then owns the remaining lane1 RX equalization/output/lane ASIC fields and subsequent CR2 definitions. The final per-file research document should merge adjacent chunks before making whole-file claims about complete CR2 register coverage or global shift/mask pairing across `dcn_4_1_0_sh_mask.h`.
