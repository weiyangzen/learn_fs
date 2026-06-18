# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 117471-119860

## Scope

This chunk is a generated register-field slice from the AMD DCN 3.2.0 shift/mask header. It contains C preprocessor constants only: `__SHIFT` macros for bit positions, `_MASK` macros for in-register bit masks, and `//<REGISTER>` comments that group fields by register. There are no functions, structs, enums, branches, loops, allocations, locks, or direct MMIO accesses in this range.

The requested range starts in the middle of `C20_PHY_CR1_LANEX_DIG_ANA_XF_TX_ANA_CREG03`, after that register's first shift definitions, and ends in the middle of `C20_PHY_CR1_RAWLANEX_DIG_TX_IRQ_CTL_TX_REQ_IRQ`, before its masks. Within the requested lines, the slice defines 2,169 macros across 221 register comments: 1,082 `__SHIFT` definitions and 1,087 `_MASK` definitions. The source path is under a local `ceph-client` mirror, but this file is AMDGPU display hardware metadata, not Ceph or filesystem logic.

## Purpose

The purpose of this header slice is to describe bit layouts for DCN 3.2 C20 PHY CR1 lane-X receiver/transmitter registers. The `LANEX` and `RAWLANEX` names are generated generic lane templates; the matching offset header also contains concrete `LANE0` through `LANE3` offsets and `LANEX` template offsets. Driver code combines offsets from `dcn_3_2_0_offset.h` with these field masks and shifts so register helper code can pack values for writes and decode readbacks from PHY MMIO registers.

This chunk covers four broad hardware areas:

- TX analog control tail: `C20_PHY_CR1_LANEX_DIG_ANA_XF_TX_ANA_CREG03..05` plus `CREG0_OVRD` and `CREG1_OVRD`, covering TX termination, pull-up/down, VPTX/VREG/boost/ring controls, PLL clock selects, bias/current modes, and analog-test-bus selections.
- RX ASIC and analog control: `C20_PHY_CR1_LANEX_DIG_ASIC_RX_*`, RX power-state/power-up/status, VCO calibration, LBERT, CDR/DPLL, receiver adaptation, statistic counters, IQ calibration, analog front-end overrides, signal-detect calibration, RX DAC/DCC/slicer/loopback controls, RX termination codes, and RX analog `CREG00..11` plus override registers.
- TX PCS and firmware cross-fabric controls: `C20_PHY_CR1_RAWLANEX_DIG_TX_PCS_XF_*` and `C20_PHY_CR1_RAWLANEX_DIG_TX_FW_XF_*`, covering lane reset/request/ack handshakes, P-state, low-power detect, rate/width, MPLL selection/enables, TX clock and deskew controls, loopback/detect-result signals, context configuration, unique lane ID, and firmware-visible lane number.
- TX IRQ control beginning: `C20_PHY_CR1_RAWLANEX_DIG_TX_IRQ_CTL_*` through the first two shift definitions for `TX_REQ_IRQ`, covering IRQ reset-return request, IRQ masks/enables, TX rate/reset/request status and clear registers.

## Important APIs, Types, And Macros

There are no callable APIs or software types in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: raw bit mask for isolating or updating the field.
- `//<REGISTER>` comments: generated grouping markers for the register whose fields follow.

Important field families include:

- Override pairs: many RX/TX interface registers expose a value bit or bitfield plus an `*_OVRD_EN` field, such as `RESET`/`RESET_OVRD_EN`, `RATE`/`RATE_OVRD_EN`, `WIDTH`/`WIDTH_OVRD_EN`, `PSTATE`/`PSTATE_OVRD_EN`, `MPLLB_SEL`/`MPLLB_SEL_OVRD_EN`, signal-detect threshold override fields, VCO load override fields, EQ adaptation override fields, and ACK/detect-result override fields.
- RX power-state fields: `RX_PSTATE_P0`, `P0S`, `P1`, and `P2` encode per-state analog and digital enables for bleeder, AFE, clock VREG, DIV16P5, analog clock, clock DCC, deserializer, CDR, VCO frequency/calibration reset, continuous calibration, digital clock, DFE, and bypass slicer controls.
- RX calibration and link-training fields: VCO calibration control/time/status fields, CDR controls, DPLL frequency bounds, LBERT control/error fields, adaptation config/status fields for ATT, VGA, CTLE, DFE taps, slicer levels, DCC phase/data/bypass offsets, and fast flags.
- RX analog-front-end fields: signal-detect high/low-frequency calibration, VCO override outputs, RX calibration registers, VDAC range, DAC/DCC controls, AFE override inputs, scope, slicer, IQ/IQC bypass and data adjustment clocks, loopback, AFE update, sample selection, termination-code outputs, analog status input/output, and analog `CREG` fields.
- RX statistic fields: data mask, match controls, statistic controls, sample counters, statistic counters, calibration-comparison clock control, stop control, shadowed count, and extended load values.
- TX PCS/FW fields: lane reset/request/ack, rate/width, align-wide-transfer, MPLLB selection, VREG TX bypass, VBOOST enable, IBOOST level, KR driver enable, offcan continuation, DCC range/bypass, term control, lane unique ID, P-state, low-power-detect, MPLL state and enable, TX clock enable, lane-to-lane and clock deskew.
- TX IRQ fields: IRQ mask bits for TX rate, TX request, TX reset, RX-to-TX parallel loopback enable/disable, RTUNE, TX termination control, and lane transceiver mode; enable flags for related interrupts; status/clear fields for TX rate and TX reset, with the requested range ending at `TX_REQ_IRQ` shifts.

Representative registers near the boundaries are partial: the first lines include only the tail of `C20_PHY_CR1_LANEX_DIG_ANA_XF_TX_ANA_CREG03`, and the last lines include only `C20_PHY_CR1_RAWLANEX_DIG_TX_IRQ_CTL_TX_REQ_IRQ__TX_REQ_IRQ__SHIFT` and `__RESERVED_15_1__SHIFT`.

## Control Flow

This header has no runtime control flow. Runtime behavior is table-driven and supplied by AMD display code:

1. DCN 3.2 code includes both `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register-list macros bind a register offset, such as an `ixC20_PHY_CR1_*` offset, to the matching generated field masks and shifts.
3. Hardware block code or firmware-facing tables use helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, and related display register helpers.
4. The actual sequence for reset, rate changes, link training, calibration, adaptation, IRQ handling, and power transitions is controlled by DCN link/PHY/hardware-sequencing code and firmware, not by this generated header.

The macros do not encode write ordering, read side effects, access type, reset defaults, polling requirements, or which fields are firmware-owned versus driver-owned.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed GPU PHY state. The represented state includes:

- TX analog state for termination, biasing, pull-up/down, VPTX/VREG boost, PLL clock enable selection, ring-control override, IBOOST, VREG charge-pump mode, and analog-test-bus observability.
- RX ASIC-interface state for reset, inversion, data enable, request, P-state, low-power-detect, rate, width, CDR, spread-spectrum clocking, disable, VREG clock bypass, flyover, loopback, DCC range/update/bypass, signal-detect thresholds, VCO load, and equalizer/adaptation override values.
- RX active configuration and telemetry for power states, power-up timing, status, VCO calibration, LBERT, CDR/DPLL, adaptation configuration, adaptation status, DFE/slicer/DCC offsets, statistic counters, and IQ calibration.
- RX analog front-end state for signal detect, VCO, DAC, DCC, AFE overrides, scope/slicer/IQ/IQC, loopback, update enable, sample selection, termination-code outputs, and analog control/status registers.
- TX PCS/FW handshake and context state for lane reset/request/ack, rate/width, P-state, low-power-detect, MPLL selection/enables/state, clock enable, deskew, loopback, TX context, unique ID, and lane number.
- TX IRQ mask/enable/status/clear state for rate, request, reset, parallel-loopback, RTUNE, termination-control, and lane-transceiver-mode events.

Persistence is hardware-defined. Configuration registers generally retain values until reset, power-gating, firmware reprogramming, modeset/link retraining, suspend/resume, or ASIC reset. Status, calibration, counter, IRQ, clear, ACK, and override output fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This header does not distinguish those behaviors.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which provides the matching register offsets. For example, the offset header exposes concrete and template C20 PHY CR1 offsets such as `ixC20_PHY_CR1_LANE0_DIG_RX_ADPTCTL_VGA_STATUS`, `ixC20_PHY_CR1_LANE1_DIG_RX_ADPTCTL_VGA_STATUS`, `ixC20_PHY_CR1_LANE2_DIG_RX_ADPTCTL_VGA_STATUS`, `ixC20_PHY_CR1_LANE3_DIG_RX_ADPTCTL_VGA_STATUS`, `ixC20_PHY_CR1_LANEX_DIG_RX_ADPTCTL_VGA_STATUS`, and `ixC20_PHY_CR1_RAWLANEX_DIG_TX_IRQ_CTL_IRQ_MASK`. The shift/mask names in this chunk supply the field layout for those generated register names.

Direct include sites for the DCN 3.2 offset/mask pair in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`

Functional integration points include:

- DMUB register initialization, where `dmub_srv_dcn32_regs_init()` populates firmware-visible mask and shift tables with `FD_MASK` and `FD_SHIFT`.
- DCN 3.2 resource construction, which includes the generated register namespace while creating display hardware blocks, stream/link encoders, AUX/I2C, audio, DCCG, HUBP/HUBBUB, and related resources.
- IRQ service setup, which uses the same generated register namespace for DCN 3.2 interrupt tables and interrupt-source mapping. This chunk's TX IRQ fields are PHY-specific and may be used by lower-level PHY or firmware diagnostics even when high-level DC IRQ code does not name each field directly.
- GPIO/AUX/hotplug translation and factory code, where generated DCN 3.2 offsets/masks provide the hardware register ABI for connector-facing blocks.
- Clock-manager and link/PHY sequencing paths that need stable definitions for rate changes, MPLL selection, deskew, VCO/CDR calibration, and power-state transitions.

## Risks And Edge Cases

- Generated-header drift is the main risk. These macros are untyped constants, so a wrong bit position or mask can compile cleanly while programming the wrong PHY field.
- The chunk boundaries are partial. The first register is already in progress, and the last register is incomplete. Adjacent chunks are required before making complete statements about `TX_ANA_CREG03` or `TX_REQ_IRQ`.
- Lane-template naming is easy to misuse. `LANEX` and `RAWLANEX` fields describe generic lane layouts, while the offset header also has concrete `LANE0..LANE3` offsets. Pairing a template mask with the wrong lane offset can produce valid-looking MMIO accesses against the wrong lane.
- Override-enable fields are dangerous when confused with value fields. Setting `*_OVRD_EN` without the intended value, or changing a value field without enabling/disabling override at the right time, can leave firmware or hardware state machines fighting driver state.
- RX power-state bits control analog and digital enables. Incorrect masks can leave CDR, DFE, deserializer, clocks, VCO calibration, or AFE blocks disabled or active in the wrong power state, causing link failures or excess power draw.
- CDR, DPLL, VCO, signal-detect, DCC, slicer, and adaptation fields are calibration-sensitive. Small mask/shift errors may appear only as marginal link training, high bit-error rate, unstable hotplug, resume-only failure, or failures at specific rates.
- Statistic and LBERT registers can be misread if full-width counters, shadowed counters, masks, stop controls, or load values are decoded with stale or mismatched field definitions.
- TX PCS/FW handshake fields are sequencing-sensitive. Incorrect reset/request/ack, rate/width, MPLL, deskew, or lane-number handling can stall firmware handshakes or misconfigure a lane during link bring-up.
- IRQ status and clear fields may be sticky or write-one-to-clear. Using an incorrect clear mask can drop real PHY events, leave IRQs stuck, or acknowledge the wrong event.
- Reserved fields are explicitly present in many masks. Consumers should avoid treating reserved masks as writable feature fields unless hardware documentation says otherwise.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN 3.2 enabled. Missing or renamed macros should fail at compile time in direct include users such as `dmub_dcn32.c`, `irq_service_dcn32.c`, `hw_translate_dcn32.c`, `hw_factory_dcn32.c`, `dcn32_clk_mgr.c`, and `dcn32_resource.c`.
- Regenerate or diff `dcn_3_2_0_sh_mask.h` against AMD's authoritative DCN 3.2 register database, especially for C20 PHY CR1 `LANEX`/`RAWLANEX` fields.
- Mechanically verify that each complete field in this slice has consistent `__SHIFT` and `_MASK` companions, while accounting for the intentionally partial first and last registers.
- Cross-check the corresponding `dcn_3_2_0_offset.h` lane offsets so `LANEX` and `RAWLANEX` field layouts align with concrete `LANE0..LANE3` address instances.
- Exercise DP/PHY link bring-up on DCN 3.2 hardware across rates and lane counts: hotplug, link training, retraining, suspend/resume, display mode changes, MST where supported, and low-power transitions.
- Monitor link-training logs and hardware readbacks for CDR lock, VCO calibration completion, DPLL frequency bounds, signal-detect behavior, adaptation status, DFE/slicer/DCC convergence, and LBERT/statistic counter sanity.
- Stress TX-side transitions by changing link rate/width, enabling/disabling lanes, entering/exiting low-power states, and checking firmware request/ack progress, MPLL selection, deskew behavior, and lane-number programming.
- Validate PHY IRQ behavior by checking TX rate/reset/request and loopback/RTUNE/termination-control event status and clear paths; expected signals are no stuck interrupts, no missed clears, and correct event attribution.

## Cross-Chunk Notes

The previous chunk owns the start of `C20_PHY_CR1_LANEX_DIG_ANA_XF_TX_ANA_CREG03`. The following chunk owns the masks for `C20_PHY_CR1_RAWLANEX_DIG_TX_IRQ_CTL_TX_REQ_IRQ` and the remaining TX IRQ control registers. The final per-file report should merge adjacent chunks before drawing complete conclusions about the full C20 PHY CR1 TX analog, RX lane, TX PCS/FW, or TX IRQ register map.
