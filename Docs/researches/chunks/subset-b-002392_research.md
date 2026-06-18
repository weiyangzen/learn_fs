# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 14530-16954

## Purpose

This chunk is generated AMD DPCS 4.2.3 register field metadata. It contains no executable C logic; it publishes `__SHIFT` and `_MASK` preprocessor constants for bitfields in the display PHY/control-space register set used by DCN 3.1.6-era AMDGPU display code.

The requested range covers 2,425 lines of masks and shifts for `DPCSSYS_CR0_RAWLANE1`, `DPCSSYS_CR0_RAWLANE2`, and `DPCSSYS_CR0_RAWLANE3` indirect raw-lane registers. It begins at the tail of raw lane 1's RX IQ phase offset field, covers lane 1 interrupt/PMA/TX/RX/PCS tail fields, then covers most of the same PCS/FSM/IRQ/PMA/TX/RX field families for lanes 2 and 3. Although the repository path is under a `ceph-client` source mirror, this file is AMD GPU display-driver hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The exported interface is the generated macro namespace:

- `DPCSSYS_CR0_RAWLANE<n>_<register>__<field>__SHIFT`: the bit offset for a field.
- `DPCSSYS_CR0_RAWLANE<n>_<register>__<field>_MASK`: the already-shifted field mask.
- `RESERVED_*` field macros: generated masks for reserved hardware bits. They are useful for register database completeness but should generally not be intentionally written by driver code.

Major register/field families in this slice:

- `DIG_IRQ_CTL_*` for lanes 1, 2, and 3: per-lane RX/TX reset, request, rate, P-state, adaptation request/disable, phase-2 calibration, lane transceiver mode, lane loopback, DCC-on-demand interrupt status, clear, and mask fields.
- `DIG_PMA_XF_*`: PMA interface override and status fields for MPLL A/B state, lane override input/output, supervisor state, TX/RX request/reset, beacon/async/data enable, serial/parallel loopback, PMA data enable, RTUNE, MPHY data, RX adaptation, ACK, and receiver detect/status handshakes.
- `DIG_TX_CTL_*` and `DIG_RX_CTL_*`: TX/RX finite-state-machine controls, clock selects, DCC continuous status, OCLA selection/data, RX loss-of-signal mask, RX data-enable override, off-candidate/continuous adaptation status, and UPCS observation controls.
- `DIG_PCS_XF_*`: PCS-level TX/RX override/status fields including PLL-ready, TX rate/P-state/swing/equalization, RX request/rate/P-state/adaptation, electrical idle, data enable, termination, lane number, ATE overrides, equalization delta/IQ, phase-2 calibration, RX adaptation feedback, figure-of-merit, TX pre/main/post cursor direction, and loopback/data-valid controls.
- `DIG_FSM_*` for lanes 2 and 3, with lane 1 represented only by the preceding chunk tail: FSM override, memory/status monitors, fast RX startup/adaptation/calibration flags, TX common-mode/RX detect, VCO wait/calibration, common calibration status, continuous calibration/adaptation status, fast flags, CR lock, TX DCC flags/status, OCLA, TX EQ update, RCAL status, and RX IQ phase offset.

These masks are consumed by AMD's register helper conventions. `dm_services.h` defines `FD(reg_field)` as `reg_field__SHIFT, reg_field_MASK`, and `reg_helper.h` builds `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers through `FN(reg_name, field)`. The mask header therefore supplies the field ABI for helper calls that paste register and field tokens together.

## Control Flow

This header has no runtime control flow. Runtime sequencing lives in AMD display code:

1. `dcn316_resource.c` includes `dpcs/dpcs_4_2_3_offset.h` and this matching `dpcs/dpcs_4_2_3_sh_mask.h`.
2. The offset header supplies indirect `ixDPCSSYS_CR0_RAWLANE*` register addresses for the same raw-lane register names, while this chunk supplies the field masks and shifts.
3. Driver register helpers expand `FD(DPCSSYS_CR0_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK__RX_REQ_IRQ_MSK)` or token-pasted equivalents into a shift/mask pair.
4. Low-level register read/write/update helpers combine those constants with a register address to encode a field value, preserve unrelated bits when appropriate, or decode status.

The macros do not encode ordering. Correct code still needs to sequence PHY power, PLL/MPLL state, lane reset/request handshakes, TX/RX data enable, link training, calibration, interrupt clearing, and power-gating boundaries according to hardware requirements.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes MMIO/indirect-register state inside the display physical coding/control system.

The represented hardware state is per lane:

- Sticky or edge-driven interrupt state and write/clear controls for RX/TX reset/request, link-rate changes, P-state transitions, adaptation, phase-2 calibration, transceiver mode changes, loopback, and DCC-on-demand events.
- PMA/PCS override state that can force or bypass normal hardware control of requests, resets, PLL state, TX/RX enables, beacon/async/data paths, termination, loopback, receiver detection, and adaptation.
- FSM monitor/status state for lane calibration, RX startup, RX/TX transitions, VCO/calibration progress, CR lock, DCC, EQ update, and IQ phase offset.
- Observation/debug controls such as OCLA selectors and monitor registers.

Persistence is hardware-defined. Many configuration and override registers may retain values until modeset, link disable, power gating, suspend/resume, or ASIC reset. Status, interrupt, monitor, ACK, clear, calibration, and debug fields may be read-only, sticky, self-clearing, write-one-to-clear, timing-sensitive, or invalid when the PHY lane is powered down. This header does not mark those semantics; consumers must know them from the hardware programming model and surrounding display code.

## Dependencies And Integration Points

This chunk depends on the generated DPCS 4.2.3 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which provides the corresponding `ixDPCSSYS_CR0_RAWLANE*` indirect register addresses and DPCS base-index constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, the direct include site for both DPCS 4.2.3 generated headers in this tree.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dm_services.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/reg_helper.h`, whose `FD`, `FN`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and wait/update helpers depend on the `__SHIFT`/`_MASK` naming contract.

The lane naming is also an integration boundary. The chunk repeats similar field layouts for raw lanes 1, 2, and 3, but these names are instance-specific; a lane-2 field constant cannot be substituted for a lane-3 register unless the consuming access path intentionally targets that hardware lane.

## Risks And Edge Cases

- Mask/shift drift is the main risk. These are untyped preprocessor constants, so an incorrect bit position can compile cleanly while writing the wrong control bit or misreading hardware status.
- Reserved-bit masks are visible. Generic code must avoid using reserved masks as writable fields unless a specific hardware sequence requires it.
- Interrupt fields are side-effect-sensitive. Confusing status, mask, and clear registers can leave lane IRQs stuck, drop events, or clear a condition before software observes it.
- Override fields can defeat normal PHY control. Incorrect PMA/PCS/FSM overrides may hold a lane in reset, force an invalid PLL state, disable TX/RX data, break receiver detection, or leave loopback/test paths active.
- Lane copy/paste errors are easy. The macro families are highly repetitive across raw lanes 1-3, but each maps to a distinct hardware lane.
- The chunk boundary is artificial. It starts after the beginning of lane 1 FSM fields and stops inside lane 3 PMA RX override definitions, so adjacent chunks are required for complete per-file coverage.
- Status fields may be invalid when clocks, lane power, or PHY blocks are gated. Register polling code must account for display power state and reset sequencing outside this header.

## Test Signals

Useful validation signals are mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU display support for DCN 3.1.6; missing or renamed macros should fail in `dcn316_resource.c` or downstream register-table/helper expansion.
- Mechanically verify that every field in lines 14530-16954 has both `__SHIFT` and `_MASK` definitions where expected, and that field masks match the width implied by adjacent generated fields.
- Cross-check the raw-lane field layout against the companion `dpcs_4_2_3_offset.h` indirect address block and against neighboring DPCS generated versions such as `dpcs_4_2_2_sh_mask.h` or later DCN-integrated headers where compatibility is expected.
- Exercise displays that use multiple PHY lanes: link training at different lane counts/rates, hotplug, modeset, MST where applicable, suspend/resume, and display power-gating transitions.
- Validate interrupt paths by watching for stuck or missing RX/TX reset/request/rate/P-state/adaptation/phase-calibration events in kernel logs and display diagnostics.
- Validate PHY health through link-training stability, absence of blank screens, no repeated training retries, no AUX/link timeout cascades caused by lane failure, no unexpected loopback/test mode behavior, and clean resume after low-power states.

## Cross-Chunk Notes

Earlier chunks own the beginning of the raw-lane 1 PCS/FSM definitions that precede line 14530. Later chunks continue after line 16954 with the rest of raw-lane 3 PMA/RX/TX/PCS/FSM/IRQ fields and subsequent DPCS 4.2.3 register metadata. The final per-file report should merge those adjacent chunks before making complete claims about all raw lanes or the full `dpcs_4_2_3_sh_mask.h` field namespace.
