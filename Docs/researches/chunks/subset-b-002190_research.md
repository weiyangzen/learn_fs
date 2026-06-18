# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 95899-98338

## Purpose

This chunk is generated AMD DCN 4.1.0 register-field metadata. It has no executable C logic; it publishes preprocessor constants that encode bit positions and bit masks for DPCSSYS CR1 raw lane and always-on raw lane registers. Consumers combine these constants with the matching DCN 4.1.0 offset metadata and AMDGPU display register helpers to update or read individual MMIO fields.

The requested range is a mid-file slice of `dcn_4_1_0_sh_mask.h`. It starts inside the `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_RESERVED_2` field pair and continues through lane-2 and lane-3 DisplayPort PHY/control-system register families before entering `DPCSSYS_CR1_RAWAONLANE0` analog/always-on lane metadata. It stops on the first shift macro for `DPCSSYS_CR1_RAWAONLANE0_DIG_TX_RX_DCC`, so the matching masks for that register are in the next chunk.

The range contains 2,131 `#define` lines: 1,066 `__SHIFT` macros and 1,065 `_MASK` macros in 309 register-comment groups. By register-comment prefix, the chunk covers 101 `DPCSSYS_CR1_RAWLANE2` groups, 125 `DPCSSYS_CR1_RAWLANE3` groups, and 83 `DPCSSYS_CR1_RAWAONLANE0` groups. Although the repository path is under a local `ceph-client` mirror, this header is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or persistence APIs in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or preserving a field during read-modify-write operations.

Major register families in this slice:

- `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_*`: lane-2 PCS transfer controls for ATE overrides, RX equalization override values, TX/RX termination control, RX clock enable, phase-2 calibration request/ack, PCS/PMA override handshakes, and test-oriented RX/TX override inputs.
- `DPCSSYS_CR1_RAWLANE2_DIG_FSM_*` and `DPCSSYS_CR1_RAWLANE3_DIG_FSM_*`: per-lane finite-state-machine override, memory-address/status monitor, fast calibration/adaptation flags, RX/TX DCC status, OCLA/debug enable, common calibration status, clock-recovery lock, TX equalization update flags, and IQ phase offset reporting.
- `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_*` and `DPCSSYS_CR1_RAWLANE3_DIG_IRQ_CTL_*`: per-lane IRQ flags, clear bits, and interrupt masks for RX/TX reset and request events, RX rate and P-state changes, adaptation requests/disable, lane transceiver mode changes, phase-2 calibration, RX-to-TX loopback, and DCC on-demand signaling.
- `DPCSSYS_CR1_RAWLANE2_DIG_PMA_XF_*` and `DPCSSYS_CR1_RAWLANE3_DIG_PMA_XF_*`: PCS/PMA boundary fields for lane and supervisor override inputs/outputs, MPLL state, TX/RX PMA request/reset/data-enable controls, loopback, RTUNE request/ack, MPHY/PWM controls, and RX adaptation override output.
- `DPCSSYS_CR1_RAWLANE2_DIG_TX_CTL_*`, `DPCSSYS_CR1_RAWLANE3_DIG_TX_CTL_*`, `DPCSSYS_CR1_RAWLANE2_DIG_RX_CTL_*`, and `DPCSSYS_CR1_RAWLANE3_DIG_RX_CTL_*`: TX/RX control FSM settings, TX clock selection, DCC continuous status, OCLA/UPCS debug enables, RX loss-of-signal mask counters, RX data-enable override counters, and adaptation/off-cancel continuous status.
- `DPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_*`: the same PCS transfer, RX/TX PCS input/output, equalization, lane-number, reserved, ATE, calibration, and termination fields as lane 2, repeated for raw lane 3.
- `DPCSSYS_CR1_RAWAONLANE0_DIG_*`: always-on lane-0 analog/adaptation data, including AFE/DFE IDAC and VDAC offsets, RX IQ/phase adjustment, DFE reference levels, PLL coarse tuning, initial power-up done, RX adaptation values for ATT/VGA/CTLE/DFE taps, adaptation done, fast calibration flags, common calibration status, TX/RX disable overrides, RX loss-of-signal and signal-detect filtering, signal-detect calibration/tune codes, VREF generator enable, calibration code storage, RX DCC calibration code banks, TX DCC bank address/data/control, MPLL background control, firmware configuration fields, lane transceiver mode, and RX signal-detect configuration.

Most fields are 16-bit register-field masks. Common naming patterns include `_OVRD_VAL` plus `_OVRD_EN` pairs for forced hardware values, `_IRQ` plus `_IRQ_CLR` pairs for status/acknowledgement, `_MSK` fields for interrupt masking, and `RESERVED_*` masks that protect unused or reserved bits.

## Control Flow

This header has no runtime control flow. The runtime path is supplied by AMDGPU display code:

1. DCN 4.1.0 display components include `dcn_4_1_0_offset.h` and this `dcn_4_1_0_sh_mask.h` header.
2. Register-list macros token-paste register and field identifiers into per-block offset, shift, and mask tables.
3. DCN 4.0.1/4.1-era resource, IRQ, GPIO, clock-manager, and DMUB code stores those tables in hardware abstraction objects.
4. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to program or inspect DPCSSYS lane fields.

The macros do not encode sequencing. Consumers must still order link bring-up, PHY power transitions, TX/RX request and reset handshakes, calibration, adaptation, interrupt clear/mask programming, loss-of-signal filtering, loopback/test enablement, and suspend/resume restore according to the hardware programming model.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state in DCN 4.1.0 display PHY/control-system registers:

- PCS/PMA handshake and override state for TX/RX request, reset, data enable, clock enable, termination, equalization, loopback, PWM/MPHY, and lane transceiver mode.
- Calibration and adaptation state for RX AFE, DFE, IQ, VREF, signal detect, phase adjustment, DCC, RTUNE, MPLL/common calibration, and fast/continuous calibration bypass flags.
- FSM/debug state for lane microsequencer override, command readiness, state monitors, OCLA/UPCS debug enables, memory-address monitor, ALU/wait-counter status, and lock/status indicators.
- Interrupt state for RX/TX reset/request, rate/P-state changes, adaptation events, phase-2 calibration, lane mode transitions, loopback events, DCC requests, clear bits, and mask fields.
- Always-on lane-0 analog state for calibration code registers, adaptation result registers, DFE reference/offset registers, PLL coarse tuning, signal-detect filters/tune codes, and firmware configuration fields.

Persistence is hardware-defined. Configuration and override fields generally remain until reprogrammed, link teardown, power gating, suspend/resume, driver reset, or ASIC reset. Status, IRQ, clear, calibration-done, acknowledgement, and debug fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant PHY clocks and power domains are active. This generated header does not identify those access semantics; consuming code and the hardware register specification must provide them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.1.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which provides matching MMIO offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c`, which includes both DCN 4.1.0 generated headers for DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c`, which consumes generated shift/mask data for DCN 4.0.1 IRQ programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, which includes the same headers for clock-manager register programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c` and `hw_factory_dcn401.c`, which use DCN 4.1.0 register metadata in GPIO/AUX/DDC translation and construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`, which builds the DCN 4.0.1 display resource pool and register tables.

The most direct behavioral integration from this exact chunk is DisplayPort/PHY lane management: link training support, lane power and reset transitions, RX/TX request handshakes, termination/equalization adaptation, calibration and DCC flows, signal detect/loss filtering, loopback/test modes, and lane-related interrupt handling.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bit, corrupting a neighboring field, breaking link training, disabling a lane, or causing stuck calibration.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the matching offset header, firmware assumptions, and silicon documentation.
- Lane 2 and lane 3 are highly repetitive. A generator or copy error can affect one lane instance while adjacent lanes appear healthy, making failures connector-, lane-count-, or link-rate-specific.
- Several names are mechanically irregular. For example, some mask macros in this area use shortened register tokens such as `IRQ_CTL_IRQ__..._MASK` for shifts under `IRQ_CTL_IRQ_MASK__...__SHIFT`, and `RX_LOS_CTL__..._MASK` for shifts under `RX_LOS_MASK_CTL__...__SHIFT`. Consumers must use the exact generated names rather than deriving mask names with simplistic string replacement.
- The chunk boundaries are artificial. The first two lines finish `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_RESERVED_2` from the previous register group context, and line 98,338 starts `DPCSSYS_CR1_RAWAONLANE0_DIG_TX_RX_DCC` without the remaining shift and mask macros.
- Override fields can force PHY behavior outside normal sequencer control. Incorrect `_OVRD_EN` or `_OVRD_VAL` programming can hold TX/RX in reset, disable data, force wrong termination/equalization, or leave test/loopback paths active.
- IRQ and clear fields are side-effect-sensitive. Confusing flag, mask, and clear bits can create missed lane events, interrupt storms, stale calibration requests, or failure to recover after hotplug/link retraining.
- Calibration and adaptation fields are timing- and power-sensitive. Writes or reads while PLL/PMA/PCS blocks are off, gated, or mid-transition may be ignored, stale, or harmful.
- Always-on lane analog fields expose low-level calibration codes and offsets. Bad values can degrade signal integrity only at certain cable lengths, data rates, lane mappings, or resume paths.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.1.0 hardware behavior:

- Build AMDGPU display support with DCN 4.0.1/4.1.0 code enabled; missing or renamed macros should fail in DMUB, IRQ, GPIO, clock-manager, resource, or register-table construction.
- Mechanically verify this range against AMD's authoritative DCN 4.1.0 register database and the matching `dcn_4_1_0_offset.h`; allow the known artificial end-boundary exception for `DPCSSYS_CR1_RAWAONLANE0_DIG_TX_RX_DCC`.
- Compare repeated lane-2 and lane-3 field layouts against adjacent raw-lane chunks and related generated DPCS headers where the hardware layout is expected to match.
- Exercise DisplayPort and USB-C/DP-alt-mode links across lane counts, link rates, training patterns, hotplug/unplug, MST, link retraining, low-power entry/exit, suspend/resume, and ASIC reset.
- Validate PHY calibration and adaptation paths by checking RX/TX request acknowledgements, RX adaptation done/status fields, common calibration done/status, DCC status, RTUNE request/ack, signal detect, and loss-of-signal filtering.
- Test IRQ behavior for RX/TX reset/request, RX rate/P-state, adaptation request/disable, phase-2 calibration, lane mode, loopback, and DCC events; verify masks and clears do not cause storms or missed events.
- Use display diagnostics for lane failure, link-training retries, HPD/link flaps, blank display after resume, high bit error rates, CRC failures, audio/video dropouts on high link rates, and failures limited to lanes 2 or 3.

## Cross-Chunk Notes

Previous chunks contain the beginning of the lane-2 PCS register family, including the register comment for `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_RESERVED_2`. Later chunks continue `DPCSSYS_CR1_RAWAONLANE0_DIG_TX_RX_DCC` and then the remaining DCN 4.1.0 shift/mask namespace. The final per-file research document should merge adjacent chunks before making whole-file claims about all DPCSSYS lanes, all always-on lanes, or complete DCN 4.1.0 display register coverage.
