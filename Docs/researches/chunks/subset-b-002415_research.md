# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 70487-72909

## Scope

This chunk is a mid-file slice of the generated AMD DPCS 4.2.3 shift/mask header. It contains only C preprocessor constants for register field bit positions and field masks. There are no functions, structs, typedefs, enums, branches, allocations, locks, direct register accesses, or software-owned persistent objects in this range.

The requested range contains 2,142 `#define` entries: 1,071 `__SHIFT` constants and 1,071 `_MASK` constants. It also contains 281 register comment markers. The range starts in the middle of `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_LANE_XCVR_MODE_IRQ`: the comment and shift definitions for that first register are immediately before this chunk, while the first visible lines are its masks. The range ends at the complete `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_RX_FSM_CTL` field definitions; later RAWLANE3 RX-control registers continue after this chunk.

## Purpose

The purpose of this header chunk is to publish exact field encodings for CR3 raw-lane DPCS registers on AMD DPCS 4.2.3 hardware. Runtime display and PHY code uses these macros together with matching `ixDPCSSYS_*` register offsets to build masked reads, masked writes, status polls, and diagnostic register dumps without embedding raw bit positions in driver code.

The covered register-map area is the CR3 raw-lane digital interface for lanes 1, 2, and 3. It starts in the RAWLANE1 IRQ-control tail, covers RAWLANE1 PMA, TX/RX controller, and late PCS transfer fields, then covers a complete RAWLANE2 PCS/FSM/IRQ/PMA/TX/RX span, and then covers RAWLANE3 PCS/FSM/IRQ/PMA/TX-control plus the first RAWLANE3 RX-control register.

Although this repository path is under `sources/distributed-fs/ceph-client`, the source is AMD GPU display hardware metadata. It has no Ceph client or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs or C data types in this chunk. The public interface is the generated macro namespace:

- `DPCSSYS_CR3_RAWLANE<n>_<register>__<field>__SHIFT` gives the least-significant bit position for a field in a CR3 raw-lane DPCS register.
- `DPCSSYS_CR3_RAWLANE<n>_<register>__<field>_MASK` gives the bit mask for isolating or updating the same field.
- `RAWLANE1`, `RAWLANE2`, and `RAWLANE3` identify concrete raw lane windows. The field layouts repeat heavily across lanes but must still be consumed with the matching lane offset and hardware sequence.

Important field families in this chunk include:

- `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_*`: interrupt status and clear bits for lane transceiver mode, RX phase-2 calibration request/disable events, RX-to-TX serial loopback, DCC on-demand, TX reset, and TX request. The first visible register is split by the chunk boundary.
- `DPCSSYS_CR3_RAWLANE1_DIG_PMA_XF_*`: PMA transfer fields for MPLLA/MPLLB lane enable state, supervisor MPLL state, TX/RX request and reset overrides, TX async/beacon/data-enable controls, RX data-enable and loopback controls, PMA acknowledge bits, RTUNE request/acknowledge, MPHY PWM/termination controls, and RX adaptation phase-map override.
- `DPCSSYS_CR3_RAWLANE1_DIG_TX_CTL_*` and `DPCSSYS_CR3_RAWLANE1_DIG_RX_CTL_*`: lane TX/RX controller control/status fields, including TX MPLL-off wait time, RX-detect allowance in P states, TX clock enable/select, async beacon wait time, TX DCC continuous status, OCLA/UPCS observation enables, RX control FSM enable, RX rate-change allowance in P1, LOS mask count, RX data-enable override count, off-cancel/adaptation continuous status, and RX UPCS OCLA enables.
- `DPCSSYS_CR3_RAWLANE1_DIG_PCS_XF_*`: late RAWLANE1 PCS/ATE fields for RX/TX rate, width, P-state, LPD, adaptation enable/request/continuous modes, TX async/beacon/data enables, master MPLL loop selection, VCO/reference load-value overrides, RX LOS threshold, RX valid override, and TX/RX serial loopback controls.
- `DPCSSYS_CR3_RAWLANE2_DIG_PCS_XF_*`: a broad RAWLANE2 PCS transfer block covering TX/RX override inputs, PCS input/output mirrors, request/acknowledge bits, DETRX result, rate/width/P-state/LPD, MPLL selection/enables, adaptation controls, RX EQ readback, RX adaptation ACK/FOM, directed TX pre/main/post cursor controls, lane number, reserved test registers, ATE override, RX EQ delta-IQ override, termination override/input, RX clock enable, RX EQ override banks, and phase-2 RX calibration bits.
- `DPCSSYS_CR3_RAWLANE2_DIG_FSM_*` and `DPCSSYS_CR3_RAWLANE3_DIG_FSM_*`: raw lane FSM control and status fields, including override jump address/start/break bits, memory address monitor, state/CMD-ready/ALU/wait/mask status bits, fast RX startup/adaptation/calibration flags, fast TX DCC and continuous calibration flags, supervisor and common calibration status for MPLLA/MPLLB/RCAL, CR register/memory lock bits, TX DCC flags/status, OCLA controls, TX EQ update flag, and RX IQ phase offset.
- `DPCSSYS_CR3_RAWLANE2_DIG_IRQ_CTL_*` and `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_*`: IRQ status, clear, and mask fields for RX request, RX rate, RX P-state, RX adaptation request/disable, RX reset, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX serial loopback, DCC on-demand, TX reset, and TX request.
- `DPCSSYS_CR3_RAWLANE2_DIG_PMA_XF_*` and `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_*`: PMA handshake and override fields with the same general shape as RAWLANE1, including MPLL lane/supervisor state, TX/RX request and reset overrides, async/beacon/data controls, loopback controls, PMA acknowledgements, RTUNE, MPHY PWM/termination, and RX adaptation phase-map override.
- `DPCSSYS_CR3_RAWLANE3_DIG_TX_CTL_*` and the first `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_RX_FSM_CTL`: RAWLANE3 TX controller fields and the initial RX controller FSM enable/rate-change fields.

## Control Flow

This header has no runtime control flow. The runtime sequence is supplied by AMDGPU display and PHY code that includes this generated header:

1. Version-specific display resource code binds DPCS 4.2.3 offset macros and shift/mask macros into register tables or helper definitions.
2. Link encoder, PHY, or diagnostics code chooses the CR3 raw-lane window for the target lane.
3. The driver combines an `ixDPCSSYS_CR3_RAWLANE*_*` offset with these `__SHIFT` and `_MASK` constants.
4. AMD register-access helpers perform masked reads, masked writes, writes to clear IRQs, and polls of handshake/status bits.
5. Hardware and firmware implement the real sequencing for PCS/PMA request-acknowledge exchange, TX/RX reset and request handshakes, PLL and RTUNE state propagation, receiver adaptation, DCC and calibration events, IRQ generation, and debug/ATE override behavior.

The implicit hardware flow represented by this chunk is raw lane bring-up and observation: PCS requests and override values are mirrored into PMA/TX/RX control paths, firmware/FSM code runs calibration and adaptation, IRQ bits report state transitions, and status/acknowledge fields tell the display driver when a lane operation has completed or when diagnostics should clear an event.

## State And Persistence Behavior

The macros are stateless compile-time constants. The mutable state they describe lives in volatile DPCS hardware registers.

State represented by this slice includes:

- IRQ state: pending event bits, per-event clear bits, and mask bits for RX request/rate/P-state/adaptation/reset, lane transceiver mode, RX phase-2 calibration, RX-to-TX serial loopback, DCC on-demand, TX reset, and TX request.
- PCS/PMA handshake state: request, reset, acknowledge, DETRX result, lane enable, MPLLA/MPLLB state, RTUNE request/acknowledge, TX/RX data enable, async and beacon enable, and loopback controls.
- Lane configuration state: rate, width, P-state, LPD, MPLLB selection, MPLL enables, master MPLL override state, TX/RX termination controls, TX cursor direction controls, RX clock enable, and lane number.
- Receiver calibration/adaptation state: RX adaptation request and continuous/off-cancel modes, AFE/DFE enable, RX adaptation ACK/FOM, RX LOS threshold and LFPS enable, phase-2 calibration request/acknowledge, VCO and reference load values, RX EQ ATT/VGA/CTLE/DFE values, delta-IQ, and IQ phase offset.
- Raw FSM and debug state: FSM override command fields, FSM state monitor, memory address monitor, fast calibration/adaptation flags, common calibration status, CR register/memory locks, OCLA/UPCS observation gates, TX DCC status, TX EQ update flag, ATE override fields, and reserved diagnostic registers.

Persistence is controlled by hardware reset and power domains. Values may survive until a DPCS reset, lane reset, display engine reset, GPU reset, power-gating transition, suspend/resume, firmware reload, link retraining, hotplug-triggered modeset, or link-rate/lane-count change. The header does not encode reset values, access permissions, write-one-to-clear semantics, read-clear behavior, self-clearing bits, or firmware ownership rules.

## Dependencies

This chunk depends on AMD's generated DPCS 4.2.3 hardware database remaining synchronized with silicon and firmware behavior. The field macros are meaningful only when used with the matching offset file and register-access layer.

Key dependencies are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which supplies the matching `ixDPCSSYS_CR3_RAWLANE*_*` register offsets.
- AMDGPU display register helper infrastructure that applies field shifts and masks during indexed DPCS register reads, writes, and polls.
- DCN/DPCS version binding code, such as DCN 3.1.6 resource initialization, that includes the DPCS 4.2.3 offset and shift/mask headers together.
- Hardware and firmware state machines that own or react to raw FSM, PCS/PMA, IRQ, DCC, RTUNE, phase-2 calibration, RX adaptation, MPHY, OCLA, UPCS, and ATE fields.
- Correct lane and CR instance selection. This range is CR3-specific, and the repeated RAWLANE1/2/3 field names are not interchangeable with CR2 or alias-lane namespaces unless the hardware map explicitly routes them that way.

## Integration Points

The main integration surface is AMDGPU display PHY and link management code for hardware using DPCS 4.2.3 registers.

Important integration points include:

- Raw lane link bring-up through PCS/PMA request, reset, acknowledge, rate, width, P-state, LPD, MPLL selection, and lane enable fields.
- TX sequencing through TX reset/request, beacon/async/data-enable overrides, TX clock selection, DCC continuous status, TX EQ update status, DETRX request/result, and TX cursor direction controls.
- RX sequencing through RX request/reset/rate/P-state, RX control FSM, LOS mask timing, data-enable override count, adaptation request/continuous/off-cancel control, AFE/DFE enable, phase-2 calibration, and RX valid/clock enable fields.
- PLL and analog support handshakes through MPLLA/MPLLB state mirrors, master MPLL override/loop fields, RTUNE request/acknowledge, MPHY PWM and termination controls, VCO/reference load-value controls, and TX/RX termination override/input fields.
- IRQ handling through status, clear, and mask registers for lane bring-up and calibration events. Clear fields likely participate in write-to-clear flows, but this header does not define those semantics.
- Diagnostics and manufacturing/test flows through ATE override banks, reserved registers, OCLA/UPCS observation enables, raw FSM monitors, fast calibration flags, RX adaptation FOM, EQ readback/override values, and DCC/calibration status fields.

## Risks And Failure Modes

- A wrong shift or mask compiles cleanly but can update the wrong hardware bits, causing link-training failure, blank displays, failed hotplug, unstable high-rate links, calibration timeouts, or misleading diagnostics.
- Lane prefix mistakes are easy because RAWLANE1, RAWLANE2, and RAWLANE3 contain highly repetitive register names. Using RAWLANE2 field metadata with a RAWLANE3 offset, or vice versa, can corrupt the wrong lane's raw control path.
- Chunk boundaries hide context. The first register in this range is split from its comment and shift lines, and later RAWLANE3 RX-control fields continue in the next chunk. Whole-file analysis must reconcile adjacent chunks before asserting completeness.
- IRQ and clear fields may be side-effectful, including write-one-to-clear or self-clearing behavior. The shift/mask header does not identify side effects, so consumers must rely on hardware documentation and established driver sequences.
- Raw FSM, ATE, MPHY, RTUNE, phase-2 calibration, RX adaptation, and PCS/PMA override fields can bypass or interfere with firmware-owned state machines. Leaving override-enable bits set can hold a lane away from normal automatic control.
- Reserved masks are explicitly generated. Code that writes full words without preserving reserved fields risks programming undocumented bits.
- The field shapes are version-specific. DPCS 4.2.3 resembles neighboring generated headers, but silent substitutions with DPCS 4.2.0 or other versions can break hardware sequencing if any bit layout differs.
- Some fields expose status rather than writable controls. Without a typed access layer, macros alone do not prevent writes to read-only status bits or reads from clear-only registers.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code paths that include `dpcs_4_2_3_sh_mask.h` with the matching DPCS 4.2.3 offset header.
- Generated-header consistency checks that each register field has a matching shift/mask pair and that consumed `DPCSSYS_CR3_RAWLANE*_*` field names exist in both offset and mask metadata where applicable.
- Diff checks against AMD's authoritative DPCS 4.2.3 register database and nearby generated versions to detect generator drift, missing fields, or unintended bit movement.
- Lane-repetition checks across RAWLANE1/2/3 while allowing real chunk-boundary and lane-surface differences.
- Hardware display smoke tests on affected ASICs: boot display, hotplug, modeset, link retraining, lane-count changes, link-rate changes, suspend/resume, GPU reset, and display power-gating recovery.
- PHY traces or debug dumps showing expected PCS/PMA request-acknowledge transitions, TX/RX reset/request events, MPLL state propagation, RTUNE acknowledgement, DCC status, RX phase-2 calibration, RX adaptation acknowledgement/FOM, and IRQ clear/mask behavior.
- Diagnostic exercises for OCLA/UPCS gates, raw FSM status monitors, fast calibration flags, ATE override paths, RX EQ readback and override registers, TX cursor direction fields, and reserved-register preservation in masked writes.

## Chunk Notes

This is only the source-tree-aligned chunk report for `subset-b-002415`. It intentionally does not create a final per-file research document for `dpcs_4_2_3_sh_mask.h`; the merge/reconciliation lane should combine this with adjacent chunk reports before making complete-file statements.
