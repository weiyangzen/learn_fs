# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 134520-136946

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask header slice for DPCSSYS CR3 raw-lane register fields. It contains no executable C code; its exported surface is preprocessor constants that describe bit positions and masks for fields in display PHY/PCS/PMA lane-control registers.

The requested range contains 2,138 `#define` entries and 289 register-comment groups. It starts in the tail of `DPCSSYS_CR3_RAWLANE0_DIG_FSM_CR_LOCK`, covers the remainder of RAWLANE0, covers a full RAWLANE1 raw-lane layout, and covers RAWLANE2 through the beginning of `DPCSSYS_CR3_RAWLANE2_DIG_PMA_XF_TX_OVRD_OUT`. Because the boundaries are artificial, the first visible entries are masks whose shifts are in the previous chunk, and the final RAWLANE2 PMA TX override shifts have their masks in the next chunk.

Although this file is under a local `ceph-client` source mirror, this range is AMDGPU display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the register.
- `<REGISTER>__<FIELD>_MASK`: the field's bit mask inside the register.

The main register-field families in this chunk are:

- RAWLANE0 tail: FSM DCC flags/status, on-chip logic analyzer controls, TX EQ update flag, common calibration status, RX IQ phase offset, lane interrupt status/clear/mask fields, PMA interface override fields, TX/RX control fields, and PCS/ATE lane override fields.
- RAWLANE1 complete layout: PCS TX/RX override and PCS input/output fields, RX adaptation acknowledgment and figure-of-merit readback, TX pre/main/post direction controls, lane-number and reserved registers, ATE overrides, RX EQ and termination overrides, RX phase-2 calibration fields, FSM control/status/fast-calibration fields, IRQ control, PMA interface overrides, TX/RX control status, and PCS ATE fields.
- RAWLANE2 beginning through PMA TX override: PCS TX/RX override and PCS input/output fields, RX adaptation and EQ readback/override fields, FSM control/status/fast-calibration fields, IRQ control, PMA lane/supervisor override fields, and the start of PMA TX override output fields.

Important field groups include:

- `DIG_FSM_*`: finite-state-machine control, debug/status, fast RX startup/adaptation/calibration shortcuts, continuous calibration/adaptation controls, common MPLL/RCAL status, CR register/memory lock status, DCC flags/status, and RX IQ phase offset.
- `DIG_IRQ_CTL_*`: per-lane RX/TX reset and request IRQs, RX rate and P-state IRQs, RX adaptation request/disable IRQs, phase-2 calibration IRQs, lane transceiver-mode and loopback IRQs, DCC-on-demand IRQ, write-to-clear style companion fields, and aggregate IRQ mask registers.
- `DIG_PMA_XF_*`: PCS-to-PMA and PMA-to-PCS override surfaces for MPLL A/B lane enables, supervisor MPLL states, TX/RX request/reset/data-enable/beacon/async/loopback overrides, PMA ACK readback, lane retune request/ack, MPHY PWM/term controls, and RX adaptation IQ phase map override.
- `DIG_TX_CTL_*` and `DIG_RX_CTL_*`: local TX/RX lane controller knobs for FSM enablement, wait timing, clock selection, RX loss-of-signal masking, RX data-enable override count, off-cancellation/adaptation continuous status, and UPCS/OCLA visibility.
- `DIG_PCS_XF_*`: PCS-facing TX/RX request/reset/rate/width/P-state/LPD/MPLL state fields, explicit override enables/values, ATE override variants, PCS ACK/result readbacks, RX adaptation status/FOM, equalization and termination controls, and RX phase-2 calibration request/ack values.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN401 code includes `dcn_4_1_0_offset.h` and this matching `dcn_4_1_0_sh_mask.h`.
2. AMD display register-list macros token-paste register and field names into offset, shift, and mask table initializers.
3. Runtime display objects receive those tables during resource, link, GPIO, IRQ, clock-manager, or DMUB setup.
4. Shared AMD display helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the tables to access the correct MMIO field.

The macros in this chunk do not define lane programming order. Link training, PHY bring-up, PMA/PCS override sequencing, IRQ acknowledgement, calibration polling, low-power transitions, and suspend/resume restore are controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It names hardware-visible lane state:

- PCS and PMA request/reset/ack handshakes for transmit and receive directions.
- Lane rate, width, P-state, low-power-detect, MPLL A/B selection, MPLL enable, and master MPLL state fields.
- Explicit override enable/value pairs for TX/RX request, reset, data enable, beacon, async drive, async enable, loopback, DETRX, VBOOST, IBOOST, RX loss thresholds, RX EQ, termination, VCO/reference load values, and phase-2 calibration.
- FSM status, command, memory address, fast-calibration, continuous-adaptation, DCC, RCAL, MPLL, and CR lock bits.
- Latched or status-like interrupt fields plus matching clear and mask fields for RX/TX events, adaptation, rate/P-state changes, phase-2 calibration, DCC on demand, transceiver mode changes, and lane loopback.
- TX/RX control status for clocking, finite-state machines, data-enable override counters, loss-of-signal masking, off-cancellation, and adaptation.

Persistence and side effects are hardware-defined. Configuration and override fields generally remain until the lane is reprogrammed, power-gated, reset, suspended/resumed, or the ASIC is reset. Status, IRQ, ACK, and clear fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while DPCSSYS/PHY clocks and power domains are active. This generated header only supplies field geometry; it does not encode those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.1.0 register database and companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` supplies the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes both generated DCN401 headers and constructs resource/register tables for DCN401 display blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` include the same generated header pair for DCN401 register access.
- Older link-encoder headers such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.h` show the established integration pattern for `RAWLANE*_DIG_PCS_XF_*` fields: link encoder register tables carry raw-lane PCS override registers and shift/mask fields for VCO/reference load overrides. DCN401 uses the same generated-header mechanism even when these exact CR3 fields are referenced indirectly.

Behaviorally, this chunk belongs to the physical display-link path below the stream encoder. It describes per-raw-lane controls used for PHY/PCS/PMA state transitions, link training support, test/ATE overrides, lane loopback, calibration, and lane-level interrupt reporting.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while touching the wrong MMIO bit at runtime.
- The file is generated. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. This range begins with only the mask half of `RAWLANE0_DIG_FSM_CR_LOCK` and ends after only the shift half of part of `RAWLANE2_DIG_PMA_XF_TX_OVRD_OUT`; adjacent chunks are required before making whole-register claims for those boundary registers.
- Repeated lane layouts are copy-sensitive. RAWLANE1 is complete in this chunk, while RAWLANE0 and RAWLANE2 are partial. A generator error can affect one lane only, producing connector, link-rate, lane-count, or board-routing-specific failures.
- Override-enable/value pairs are high risk. Setting an enable bit with an incorrect value can force reset/request/data-enable, rate/width/P-state, MPLL, EQ, termination, loopback, DETRX, or calibration state away from the normal PHY controller.
- IRQ status, clear, and mask fields are side-effect-sensitive. Bad masks can cause missed lane events, stuck interrupts, interrupt storms, or incorrect handling of RX adaptation, reset, rate change, P-state change, phase-2 calibration, or TX request/reset events.
- Calibration/status fields are sequencing-sensitive. Polling the wrong DCC, RCAL, MPLL, VCO, RX IQ phase, or CR lock bit can make link setup proceed before the lane is ready or wait forever on a bit that is not the intended status.
- PCS/PMA handshakes are direction-sensitive. Confusing TX and RX request/reset/ACK or loopback fields can break link bring-up, diagnostics, or recovery paths without producing obvious compile-time failures.
- Reserved masks appear throughout the generated layout. Driver code should not rely on reserved bits unless the hardware specification explicitly defines a safe use.

## Test Signals

Useful validation combines generated-header checks with hardware display-link behavior:

- Build AMDGPU display support with DCN401 enabled. Missing or renamed macros should fail in DCN401 resource, IRQ, GPIO, clock-manager, DMUB, or any link/register-table code that token-pastes these names.
- Mechanically verify that every complete field in this range has a matching `__SHIFT` and `_MASK` pair, while allowing the expected boundary exceptions at the start of `RAWLANE0_DIG_FSM_CR_LOCK` and the end of `RAWLANE2_DIG_PMA_XF_TX_OVRD_OUT`.
- Cross-check every DPCSSYS CR3 RAWLANE0-2 register field here against the matching `dcn_4_1_0_offset.h` entries and AMD's authoritative DCN 4.1.0 register-field database.
- Run repeated-instance consistency checks across RAWLANE0, RAWLANE1, RAWLANE2, and adjacent RAWLANE3 fields, allowing only intentional prefix and chunk-boundary differences.
- Exercise DP/USB-C/display PHY link bring-up across lane counts, link rates, hotplug, unplug, link retraining, MST if available, suspend/resume, and GPU reset. Watch for lane-specific link-training failures, stuck HPD/link states, AUX/link mismatch symptoms, or failures only on a subset of ports.
- Use register dumps or debug instrumentation during link training to confirm PCS/PMA request/reset/ACK, MPLL state, rate/width/P-state, and lane enable fields transition as expected.
- Exercise diagnostics and recovery paths that use loopback, ATE/test overrides, RX EQ override/readback, DCC/RCAL/MPLL calibration, RX phase-2 calibration, and RX adaptation. Expected signals are completed calibration handshakes, sane FOM/readback values, and no stuck FSM status.
- Stress interrupt handling around lane reset/request/rate/P-state/adaptation and TX request/reset events. Expected signals are correct status reporting, clear behavior, mask behavior, and no interrupt storms.

## Cross-Chunk Notes

The previous chunk owns the beginning of the DPCSSYS CR3 RAWLANE0 area, including the shift definitions for `RAWLANE0_DIG_FSM_CR_LOCK` whose masks open this chunk. The next chunk continues `RAWLANE2_DIG_PMA_XF_TX_OVRD_OUT` with the remaining shift fields and masks, then should cover the rest of RAWLANE2 and later raw-lane/register groups. The final per-file research document should reconcile these boundaries before making complete claims about all DPCSSYS CR3 raw lanes or all DCN 4.1.0 PHY/PCS/PMA lane fields.
