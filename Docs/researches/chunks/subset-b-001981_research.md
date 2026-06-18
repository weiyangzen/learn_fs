# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 127188-129581

## Purpose

This chunk is generated AMD DCN 3.2 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for C20 PHY CR2 register fields. Runtime AMDGPU display code combines these constants with companion register-offset definitions and register helper macros to read, write, update, and decode MMIO-backed display PHY state.

The requested range covers 2,166 `#define` lines: 1,082 `__SHIFT` constants and 1,084 `_MASK` constants across 229 register blocks. Most of the span is CR2 lane0 receive-side metadata, including RX power control, VCO calibration, CDR/DPLL, adaptive equalization, statistical counters, IQ correction, and RX analog crossbar/control fields. The chunk then transitions into CR2 lane1 transmit-side metadata, including ASIC override/input/output fields, TX power states and timing, DCC, TX statistics, clock alignment, LBERT, FIFO, TX analog overrides/status/equalization, and TX analog CREG fields. The final line stops inside `C20_PHY_CR2_LANE1_DIG_ANA_XF_TX_ANA_CREG03`, so the register block continues in the next chunk.

Although this file sits under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or persistence primitives in this range. The public interface is the generated macro namespace:

- `C20_PHY_CR2_LANE0_DIG_RX_...__<FIELD>__SHIFT`: low bit index for a receive-side C20 PHY CR2 lane0 register field.
- `C20_PHY_CR2_LANE0_DIG_RX_...__<FIELD>_MASK`: unshifted 16-bit mask for the same receive-side field.
- `C20_PHY_CR2_LANE0_DIG_ANA_XF_RX_...__<FIELD>__SHIFT` and `_MASK`: lane0 RX analog crossbar/control/status field metadata.
- `C20_PHY_CR2_LANE1_DIG_ASIC_...__<FIELD>__SHIFT` and `_MASK`: lane1 ASIC-facing TX/lane override, input, and output field metadata.
- `C20_PHY_CR2_LANE1_DIG_TX_...__<FIELD>__SHIFT` and `_MASK`: lane1 TX power, calibration, statistics, clock-alignment, LBERT, FIFO, and DCC metadata.
- `C20_PHY_CR2_LANE1_DIG_ANA_XF_TX_...__<FIELD>__SHIFT` and `_MASK`: lane1 TX analog override, status, equalization, DCC, termination, and CREG metadata.

The macros follow the AMD register helper convention used by DC and DMUB code. Helpers such as `FD_SHIFT(reg_name, field)`, `FD_MASK(reg_name, field)`, `FN(reg_name, field)`, `REG_SET`, `REG_UPDATE`, and `REG_GET` paste a register token and field token into `reg_name__field__SHIFT` and `reg_name__field_MASK`. The constants in this chunk are therefore compile-time data consumed indirectly through generated register tables and token-pasting helpers.

Major lane0 RX families in this chunk:

- `RX_PWRCTL`: receive power-control status and the tail of `RX_CTL`, including DCC DAC write enable, IQC skip, equalization force, and calibration override gate bits.
- `RX_VCOCAL`: VCO calibration control, timing, and status fields for frequency tuning, continuous calibration, reset, calibration done, VCO counter result, and up/correct flags.
- `RX_LBERT`, `RX_CDR`, and `RX_DPLL`: loopback BERT mode/error fields, CDR phase/frequency update gain controls, DPLL frequency and bounds, and CDR status.
- `RX_ADPTCTL`: adaptation configuration, resets, ATT/VGA/CTLE/DFE status, DFE tap codes, DAC offsets, slicer controls, DCC IDAC offsets, fast flags, and sample-search-manager configuration/final-code status.
- `RX_STAT`: pattern matching, sample-count load/control/status, statistical counters, counter freeze/stop controls, comparison-clock control, data masks, and extended load values.
- `RX_IQC_CTL`: IQ correction reset/adjust, configuration, and status.
- `ANA_XF_RX`: analog RX control and power override outputs, signal-detect and VCO overrides, calibration DAC controls, AFE overrides, scope/slicer controls, IQC overrides, loopback, term-code overrides, status in/out, and RX analog CREG fields.

Major lane1 TX families in this chunk:

- `ASIC_LANE` and `ASIC_TX`: lane loopback/transceiver mode, TX ASIC input/output handshake fields, TX override inputs and outputs, and miscellaneous override value/enable fields.
- `TX_PWRCTL`: P0/P0S/P1/P2 power-state bitfields, TX power-up timing registers, TX control bits, and TX power-state status.
- `TX_DCC_CTL`: TX DCC differential/common-mode IDAC offsets and DCC/DAC FSM status.
- `TX_STAT`: TX sample-count load, counter control, sample counter, stat counter, comparison-clock control, and stat stop.
- `TX_CLK_ALIGN`, `TX_LBERT`, `TX_LVL_CALC`, and `TX_FIFO`: clock-alignment startup/shift/status, TX LBERT control and pattern words, level-calculation status, and FIFO control.
- `ANA_XF_TX`: TX analog override output fields, termination override, DCC analog controls, equalization override/status, status in/out, and analog CREG fields through the start of `TX_ANA_CREG03`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code:

1. DCN 3.2 include sites bring in `dcn_3_2_0_sh_mask.h` together with matching offset/base headers.
2. Register-list setup code builds per-block tables of register offsets, shifts, and masks for the ASIC generation.
3. Runtime code calls helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET`.
4. Those helpers use token-pasted shift/mask constants to isolate or update fields in MMIO register values.
5. Hardware state changes happen through the GPU register fabric; this generated header only names the bit layout.

The macros do not encode ordering requirements. Consumers must still sequence PHY power transitions, TX/RX reset, VCO and DCC calibration, CDR/DPLL tuning, adaptation, clock alignment, loopback tests, statistical sampling, and analog override updates correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state in the C20 PHY CR2 block:

- Lane0 RX state includes power-management status, VCO calibration state, CDR/DPLL state, LBERT count/overflow, adaptive equalizer coefficients and completion flags, DFE tap/status values, IQC state, statistics/counters, analog power/control overrides, analog calibration values, loopback controls, scope/status signals, and RX analog CREG debug/test controls.
- Lane1 TX state includes lane/TX ASIC input and output handshake state, TX override values, power-state enable/reset/data controls, power-up timing, DCC offset/FSM state, TX statistics, clock-alignment FSM/shift state, LBERT mode/pattern state, FIFO controls, TX analog override/status/equalization values, termination/DCC controls, and TX analog debug/test CREG controls.

Persistence is hardware-defined. Configuration fields generally remain until reprogrammed, power-gated, reset, or lost across suspend/resume. Status, counter, done, IRQ, ack, start, stop, reset, update, and self-clear fields may be read-only, sticky, write-one-to-clear, write-triggered, or self-clearing depending on the underlying register. The generated mask header does not distinguish those semantics; the driver sequencing and hardware register specification must.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies the companion MMIO offsets and base-index macros.
- DC/DMUB register-helper headers that paste register and field names into `__SHIFT` and `_MASK` symbols.
- ASIC-specific register tables in DCN 3.2 display, GPIO, IRQ, clock, resource, DMUB, and amdgpu code.

Direct include sites for `dcn_3_2_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`

Direct `rg` checks did not find ordinary C references to representative CR2 PHY symbols from this span outside the generated header itself. That suggests these fields are either reserved for table-driven, firmware, diagnostic, or future/conditional flows in this source snapshot, or are used through macro expansion paths that do not spell the fully expanded symbol in source. They still form part of the generated header ABI: deleting or changing them can break builds or silently corrupt field extraction when a table or helper starts using the affected register name.

## Risks And Edge Cases

- The field constants are untyped numeric macros. A wrong shift or mask can compile cleanly and cause writes to the wrong hardware bit, missed status polling, or incorrect field decoding.
- Many masks cover adjacent power, reset, calibration, and override controls. A single off-by-one shift in `TX_PWRCTL`, `RX_PWRCTL`, VCO, DCC, or analog override fields can leave PHY lanes powered incorrectly, stuck in reset, or calibrated with invalid parameters.
- Lane and direction names are copy-sensitive. This chunk crosses from `LANE0` RX fields to `LANE1` TX fields; accidental lane or RX/TX substitution may only appear on specific physical lanes, link directions, or connector configurations.
- The first and last register blocks are partial because of the chunk boundary. The chunk starts at the tail of `C20_PHY_CR2_LANE0_DIG_RX_PWRCTL_RX_CTL` mask definitions and ends before the remaining fields of `C20_PHY_CR2_LANE1_DIG_ANA_XF_TX_ANA_CREG03`; adjacent chunks are required for full-file claims.
- Reserved fields are named and masked. Consumers should avoid programming reserved bits unless the authoritative hardware sequence requires it, since reserved-bit writes may be ignored on one stepping and harmful on another.
- Self-clear and trigger-like fields need careful sequencing. Names such as `*_ADJUST_CLK`, `*_CTRL_EN`, `*_UPDATE_EN`, `SC1_START`, `SC1_STOP`, `RESET_*`, `RETRIG_CLK_ALIGN`, and `START_SSM` imply write-trigger behavior that this header cannot enforce.
- Status and counter fields may be transient. Polling `*_DONE`, `*_FSM_STATE`, IRQ, overflow, calibration result, sample count, or LBERT error fields without the correct clock/power state can produce stale or meaningless values.
- Analog override and calibration fields are especially hardware-sensitive. Bad AFE/CTLE/VGA/DFE/DCC/VCO/termination/equalization values can produce link-training failures, signal integrity problems, display blanking, intermittent errors, or issues limited to high rates and certain boards.

## Test Signals

Useful validation is a mix of generated-header checks, compile coverage, and hardware behavior:

- Build AMDGPU/DC with DCN 3.2 support enabled. Missing or renamed shift/mask symbols should fail where register tables or helpers reference this header.
- Mechanically verify that each complete field in the span has matching `__SHIFT` and `_MASK` constants, allowing for the artificial first/last partial register-block boundaries.
- Diff this range against AMD's authoritative DCN 3.2 register database or neighboring generated headers for compatible ASICs to catch copy, lane, direction, or reserved-bit drift.
- Exercise DCN 3.2 display bring-up, modeset, link-rate changes, lane-count changes, hotplug, suspend/resume, and low-power transitions on hardware using the C20 PHY.
- Validate RX-sensitive flows where available: VCO calibration, CDR/DPLL lock, adaptation/DFE convergence, signal detect, loopback/BERT, IQC, statistical counters, and analog RX status.
- Validate TX-sensitive flows: TX power-state transitions, TX DCC calibration, clock alignment, FIFO behavior, TX LBERT/pattern generation, equalization levels, termination control, and analog TX status.
- Watch kernel logs, debugfs traces, display diagnostics, and hardware counters for link-training failures, AUX or HPD instability, stuck calibration FSMs, timeout polling, blank displays, CRC errors, underflow, intermittent high-rate errors, failed suspend/resume, and unexpected IRQ/status bits.

## Cross-Chunk Notes

Earlier chunks own the beginning of `C20_PHY_CR2_LANE0_DIG_RX_PWRCTL_RX_CTL` and prior DCN 3.2 mask definitions. Later chunks continue `C20_PHY_CR2_LANE1_DIG_ANA_XF_TX_ANA_CREG03` and the remaining `dcn_3_2_0_sh_mask.h` namespace. The final per-file research document should merge adjacent chunks before making complete claims about every C20 PHY lane, all CR2 TX/RX fields, or the full generated DCN 3.2 shift/mask contract.
