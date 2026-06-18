# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 92914-95292

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for the CR4 raw-lane digital register space. It contains only preprocessor constants: `__SHIFT` macros define field bit positions and `_MASK` macros define field masks for 16-bit-shaped DPCS control/status registers. In this line range there are 2,111 `#define` entries across 268 register-comment groups, with 1,058 shift constants and 1,053 mask constants.

The chunk starts in the middle of `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_TX_DCC_CONT_STATUS`, covers the tail of raw lane 0 TX/RX control and ATE PCS override fields, then covers a large raw lane 1 and raw lane 2 digital control surface. It ends inside `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN`. Although the path is under a `ceph-client` source mirror, this header is AMDGPU display PHY register metadata and has no Ceph filesystem behavior.

## Purpose

The purpose of this header slice is to provide AMDGPU display code with generated bitfield metadata for programming DPCS 4.2.2 CR4 raw-lane PCS, FSM, IRQ, PMA, TX-control, and RX-control registers. Consumers pair these macros with the matching `ixDPCSSYS_CR4_RAWLANE*...` address definitions from `dpcs_4_2_2_offset.h` and AMD display register helpers, allowing driver code to assemble read-modify-write values without open-coding bit numbers.

The covered fields describe:

- Raw lane 0 late TX/RX control and ATE-facing PCS override fields, including OCLA/debug enables, RX FSM and loss-of-signal masking, RX data-enable override timing, adaptation/off-channel continuous status, rate/width/P-state/low-power detect overrides, loopback bits, master MPLL loop controls, VCO/ref load overrides, RX valid override, and TX data/async override bits.
- Raw lane 1 PCS transmit and receive handshakes, override inputs/outputs, PCS inputs/outputs, RX adaptation status/FOM, directed TX pre/main/post controls, lane-number readback, ATE override controls, EQ/termination/phase calibration registers, FSM control/status/fast-calibration flags, IRQ status/clear/mask fields, PMA interface overrides, TX/RX control registers, and lane 1 ATE PCS overrides.
- Raw lane 2 mirrors of the lane 1 PCS/FSM/IRQ/PMA/TX/RX control surface, including the same request/ack, reset, P-state/rate/width, RX adaptation, EQ, termination, phase calibration, fast-calibration, IRQ, PMA handshake, MPHY, TX/RX control, and ATE override families.
- The beginning of raw lane 3 PCS TX override input fields for P-state, low-power detect, width, rate, MPLL selection/enables, master MPLL state overrides, and TX async enable overrides.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocations, or direct MMIO operations in this chunk. The exported interface is the generated macro namespace:

- `DPCSSYS_CR4_RAWLANE*_*__FIELD__SHIFT`: least-significant bit index for `FIELD`.
- `DPCSSYS_CR4_RAWLANE*_*__FIELD_MASK`: bit mask for the same field.
- Register delimiter comments such as `//DPCSSYS_CR4_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK`: field-group markers that correspond to address macros in the companion offset header.

Notable PCS transfer/interface groups include:

- `DIG_PCS_XF_TX_OVRD_IN`, `DIG_PCS_XF_TX_OVRD_IN_1`, and `DIG_PCS_XF_TX_OVRD_IN_2`: TX-side override values/enables for reset, request, P-state, low-power detect, width, rate, MPLL selection/enables, master MPLL state, detect-RX request, VBOOST, IBOOST level, beacon, loopback, TX data enable, async data, and async enable.
- `DIG_PCS_XF_TX_PCS_IN`, `DIG_PCS_XF_TX_OVRD_OUT`, and `DIG_PCS_XF_TX_PCS_OUT`: PCS TX request/reset inputs and acknowledgement/detect-result/status outputs.
- `DIG_PCS_XF_RX_OVRD_IN`, `DIG_PCS_XF_RX_OVRD_IN_1` through `_3`, and ATE variants: RX-side override fields for rate, width, P-state, low-power detect, adaptation enable/request/continuous modes, reset/request, RX loss-of-signal thresholds, VCO/ref load values, CDR VCO low-frequency indication, RX data enable, and loopback.
- `DIG_PCS_XF_RX_PCS_IN` through `_4`: PCS RX inputs for request, rate, width, P-state, low-power detect, CDR VCO low-frequency, adaptation AFE/DFE, adaptation/off-channel continuous modes, reset, ref/VCO load values, EQ attenuation/VGA/CTLE/DFE fields.
- `DIG_PCS_XF_RX_OVRD_OUT`, `DIG_PCS_XF_RX_PCS_OUT`, `DIG_PCS_XF_RX_OVRD_OUT_1`, and `DIG_PCS_XF_RX_OVRD_OUT_2`: RX acknowledgements, control-enable status, RX clock enable, and RX valid override/readback fields.
- `DIG_PCS_XF_RX_ADAPT_ACK`, `DIG_PCS_XF_RX_ADAPT_FOM`, `DIG_PCS_XF_RX_TXPRE_DIR`, `DIG_PCS_XF_RX_TXMAIN_DIR`, and `DIG_PCS_XF_RX_TXPOST_DIR`: adaptation completion/quality and directed transmit-cursor feedback.
- `DIG_PCS_XF_ATE_OVRD_IN`, `DIG_PCS_XF_RX_EQ_DELTA_IQ_OVRD_IN`, `DIG_PCS_XF_TXRX_TERM_CTRL_OVRD_IN`, `DIG_PCS_XF_TXRX_TERM_CTRL_IN`, `DIG_PCS_XF_RX_EQ_OVRD_IN_1`, `DIG_PCS_XF_RX_EQ_OVRD_IN_2`, and `DIG_PCS_XF_RX_PH2_CAL`: ATE/debug hooks for reset/request/data-enable overrides, RX EQ, termination, delta-IQ, and phase-2 calibration handshake.

Notable FSM groups include:

- `DIG_FSM_FSM_OVRD_CTL`, `DIG_FSM_MEM_ADDR_MON`, and `DIG_FSM_STATUS_MON`: FSM jump/command/break override control and status/readiness monitoring.
- `DIG_FSM_FAST_RX_*`, `DIG_FSM_FAST_TX_*`, and `DIG_FSM_FAST_SUP`: fast-path calibration/adaptation flags for RX startup, AFE/DFE, bypass, reference level, IQ, continuous calibration/adaptation/data/phase/AFE operations, TX common-mode, TX RX-detect, and supervisor behavior.
- `DIG_FSM_CMNCAL_MPLL_STATUS`, `DIG_FSM_CMNCAL_RCAL_STATUS`, `DIG_FSM_TX_DCC_FLAGS`, `DIG_FSM_TX_DCC_STATUS`, `DIG_FSM_TX_EQ_UPDATE_FLAG`, and `DIG_FSM_RX_IQ_PHASE_OFFSET`: calibration status and tuning observability fields.
- `DIG_FSM_FAST_FLAGS` and `DIG_FSM_CR_LOCK`: consolidated fast-calibration flags and CR register/memory lock bits.

Notable IRQ groups include:

- Status bits for RX reset, RX request, RX rate, RX P-state, RX adaptation request/disable, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX loopback enable, DCC on-demand, TX reset, and TX request.
- Matching `_CLR` groups for write-to-clear style acknowledgement of those events.
- `DIG_IRQ_CTL_IRQ_MASK` and `DIG_IRQ_CTL_IRQ_MASK_2` fields that mask RX-side, lane-mode, phase-calibration, loopback, DCC, TX reset, and TX request interrupts.

Notable PMA/TX/RX control groups include:

- `DIG_PMA_XF_LANE_OVRD_IN/OUT`, `DIG_PMA_XF_SUP_OVRD_IN`, and `DIG_PMA_XF_SUP_PMA_IN`: lane MPLL and supervisor state override/readback.
- `DIG_PMA_XF_TX_OVRD_OUT`, `DIG_PMA_XF_TX_PMA_IN`, `DIG_PMA_XF_RX_OVRD_OUT`, and `DIG_PMA_XF_RX_PMA_IN`: PMA-facing TX/RX request, reset, beacon, async, loopback, data-enable, and acknowledgement fields.
- `DIG_PMA_XF_LANE_RTUNE_CTL`, `DIG_PMA_XF_SUP_PMA_IN_1`, `DIG_PMA_XF_MPHY_OVRD_IN`, `DIG_PMA_XF_MPHY_OVRD_OUT`, and `DIG_PMA_XF_RX_ADAPT_OVRD_OUT`: lane retune, low-speed MPHY PWM/termination/async, and RX adaptation phase-adjust map fields.
- `DIG_TX_CTL_TX_FSM_CTL`, `DIG_TX_CTL_TX_CLK_CTL`, `DIG_TX_CTL_TX_DCC_CONT_STATUS`, `DIG_TX_CTL_OCLA`, and `DIG_TX_CTL_UPCS_OCLA`: TX FSM timing, RX-detect allowance per power state, TX clock selection/enables, async beacon timing, DCC continuous status, and OCLA capture controls.
- `DIG_RX_CTL_RX_FSM_CTL`, `DIG_RX_CTL_RX_LOS_MASK_CTL`, `DIG_RX_CTL_RX_DATA_EN_OVRD_CTL`, `DIG_RX_CTL_OFFCAN_CONT_STATUS`, `DIG_RX_CTL_ADAPT_CONT_STATUS`, and `DIG_RX_CTL_UPCS_OCLA`: RX FSM enable/rate-change behavior, loss-of-signal masking, RX data-enable timing, off-channel/adaptation continuous status, and OCLA capture controls.

## Control Flow

This header has no runtime control flow. It supplies compile-time constants only. Runtime sequencing lives in AMD display/DC code that includes this header, selects the appropriate DPCS register address, reads the current register value, preserves unrelated and reserved bits, applies masks/shifts, and writes the updated value back to indexed DPCS hardware.

The implied hardware control flows are sensitive PHY paths: PCS request/ack transitions, TX/RX reset sequencing, P-state/rate/width changes, MPLL selection and master-state overrides, RX adaptation, RX EQ and termination overrides, phase calibration, DCC and VCO/ref load handling, PMA request/ack handshakes, interrupt/status polling and clearing, OCLA debug capture, low-speed MPHY behavior, and TX/RX continuous calibration status handling. This chunk describes the bit layout for those flows but does not enforce ordering, timeouts, polling loops, access direction, or reset cleanup.

## State And Persistence Behavior

The macros are stateless compile-time constants. The mutable state they describe lives in volatile DPCS CR4 raw-lane hardware registers. Those registers may be changed by link training, modesets, hotplug handling, PHY retuning, suspend/resume, GPU reset recovery, power gating, firmware or hardware state machines, and diagnostic tooling.

Several field families are stateful in hardware:

- Request, acknowledge, reset, ready, valid, calibration-done, and interrupt bits represent transient handshakes or latched status.
- P-state, rate, width, MPLL, clock-enable, data-enable, loopback, low-power detect, termination, RX EQ, adaptation, and PMA override fields influence active PHY behavior until rewritten or reset.
- Value/enable override pairs are common. Setting an override value without its enable bit may have no effect; leaving an enable bit asserted can keep normal PCS/PMA/FSM control bypassed after a debug or ATE path finishes.
- Reserved masks are widespread and should be preserved during read-modify-write operations unless authoritative hardware documentation requires a defined write.

## Dependencies

This chunk depends on the AMD ASIC register-generation source remaining synchronized with DPCS 4.2.2 silicon documentation. The key paired file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which defines matching register addresses such as `ixDPCSSYS_CR4_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`, `ixDPCSSYS_CR4_RAWLANE1_DIG_FSM_STATUS_MON`, and `ixDPCSSYS_CR4_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK`.

The in-tree AMD display resource consumers include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which include `dpcs_4_2_2_sh_mask.h` and build DPCS register shift/mask tables through `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`. Related register-list definitions live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`.

## Integration Points

This chunk integrates with AMDGPU display PHY programming for DPCS 4.2.2 hardware, particularly DCN 3.1.x-style link encoder/resource setup. The macros are not useful alone; they must be paired with the corresponding CR4 raw-lane address macros and the display register helper layer that performs indexed register access.

Correct integration requires three alignments:

- ASIC-version alignment: use DPCS 4.2.2 offsets with DPCS 4.2.2 masks/shifts, not neighboring generated DPCS versions.
- Instance alignment: use `CR4` raw-lane masks only with `CR4` raw-lane register addresses.
- Lane alignment: use `RAWLANE0`, `RAWLANE1`, `RAWLANE2`, and `RAWLANE3` masks only with their matching lane addresses and physical-lane programming path.

This range is especially relevant to low-level PHY diagnostics and bring-up because it exposes ATE override, OCLA capture, fast-calibration, PMA handshake, IRQ mask/clear, and continuous calibration/adaptation control fields that sit below the higher-level display link policy code.

## Risks And Edge Cases

- Chunk boundaries are not semantic. The first line is the final mask for `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_TX_DCC_CONT_STATUS`, and the final lines stop before `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` is complete.
- These are untyped preprocessor constants. A wrong shift, mask, or lane prefix can compile successfully and only surface as hardware misprogramming.
- Generated header edits can diverge from AMD's register database, the companion offset header, firmware assumptions, and silicon documentation.
- Lane repetition is copy-sensitive. Raw lane 1 and raw lane 2 are largely mirrored, but using a lane 1 field with a lane 2 address, or applying a raw-lane mask to a non-raw-lane address, can program the wrong hardware.
- Override value/enable pairs are easy to misuse. Leaving override enables asserted after ATE/debug use can break later link training, power management, hotplug handling, or suspend/resume.
- PCS/PMA request-ack and IRQ clear/mask fields are sequencing-sensitive. Incorrect masks can cause false readiness, missed interrupts, uncleared latched status, stuck state-machine waits, or failure recovery loops.
- Analog-adjacent fields such as RX EQ, termination, VCO/ref load, MPLL state, DCC, and IQ phase can fail only under specific link rates, lane counts, cables, boards, sinks, temperature, or voltage corners.
- Reserved bits are common. Consumers should preserve reserved fields during read-modify-write operations and should not assume the whole 16-bit register may be freely rewritten.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`, especially DCN315/DCN316 resource table initialization and DCN31 link encoder register tables.
- Static generation checks that complete fields have matching `__SHIFT` and `_MASK` constants, masks align with their shifts and intended widths, and all masks remain within the expected DPCS CR register shape.
- Cross-checks against `dpcs_4_2_2_offset.h` to ensure each CR4 raw-lane register-comment group in this range has a corresponding `ixDPCSSYS_CR4_RAWLANE*...` address macro.
- Repetition checks between raw lane 1 and raw lane 2 where the hardware model expects identical layouts, while allowing chunk-boundary splits and intentional lane-specific differences.
- Display bring-up, hotplug, modeset, blank/unblank, suspend/resume, and GPU reset recovery on hardware using DPCS 4.2.2.
- Link-training stress across lane counts and link rates that exercises PCS/PMA request-ack flows, P-state/rate/width changes, RX adaptation, TX/RX data-enable overrides, MPLL selection, and low-power transitions.
- PHY diagnostic coverage for OCLA, ATE override paths, RX EQ and termination overrides, phase-2 calibration, fast-calibration flags, DCC on-demand IRQs, RX/TX reset/request IRQs, PMA retune, MPHY PWM/termination, and RX adaptation FOM/ack readback.
- Register dumps from failed link training decoded with these masks to confirm request/ack state, interrupt masks/clears, TX/RX control bits, PMA override state, calibration flags, and reserved-bit preservation.

## Cross-Chunk Notes

The previous chunk is required to reconstruct the complete `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_TX_DCC_CONT_STATUS` group and earlier raw lane 0 definitions. This chunk then completes late raw lane 0 control/ATE fields and covers most of raw lanes 1 and 2. The following chunk is required for the remainder of raw lane 3 and for any whole-register claims about `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN`.
