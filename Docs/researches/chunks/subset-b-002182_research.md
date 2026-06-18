# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 76588-79052

## Purpose

This chunk is a generated AMD DCN 4.1.0 register field shift/mask slice for DisplayPort/PHY DPCS lane control registers. It contains no executable C code, functions, structs, or enums. Its exported interface is preprocessor metadata named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; driver register helpers use those constants to extract or update individual fields inside memory-mapped hardware registers.

The requested range contains 2,115 `#define` entries: 1,053 shift definitions and 1,062 mask definitions, plus 350 register-name comments. It starts at the tail of `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1`, covers the rest of RAWLANE3 digital PCS/FSM/IRQ/PMA/TX/RX control fields, covers full RAWAONLANE0 and RAWAONLANE1 analog/digital lane calibration and status field families, and ends at the first field of `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0`. The line boundaries are artificial: the first register group begins before the chunk and the final register group continues after it.

Although this file lives under a `ceph-client` source mirror, this range is AMDGPU Display Core hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important public surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: mask for preserving, testing, or writing that field.

The main register families in this range are:

- `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_*`: lane 3 PCS transmit/receive interface fields. The chunk includes RX override inputs, RX PCS inputs, ACK/readback outputs, adaptation FOM/ACK, TX pre/main/post cursor direction readbacks, lane number, ATE override controls, RX equalization override fields, TX/RX termination controls, RX phase calibration, and late TX override fields.
- `DPCSSYS_CR0_RAWLANE3_DIG_FSM_*`: lane 3 finite-state-machine controls and observability. These include FSM override controls, memory/status monitors, fast startup/adaptation/calibration enables, common calibration MPLL status, continuous calibration/adaptation flags, TX DCC flags/status, OCLA debug selector fields, TX EQ update flags, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR0_RAWLANE3_DIG_IRQ_CTL_*`: lane 3 interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation transitions, lane transceiver mode, phase-2 calibration request/disable, lane RX-to-TX serialized loopback, DCC on-demand, and TX reset/request.
- `DPCSSYS_CR0_RAWLANE3_DIG_PMA_XF_*`: lane 3 PCS-to-PMA bridge controls for lane, SUP, TX, RX, MPHY, and RX adaptation override paths. These fields describe reset/request/data-enable overrides, rate/width/pstate, impedance tuning, TX driver settings, RX EQ/adaptation outputs, MPLL loop selection, serial/parallel loopback, clock-ready/status, and related control/status signals.
- `DPCSSYS_CR0_RAWLANE3_DIG_TX_CTL_*` and `DPCSSYS_CR0_RAWLANE3_DIG_RX_CTL_*`: lane-local TX/RX control fields for TX FSM, TX clock, continuous TX DCC status, RX FSM, RX LOS masking, RX data-enable override, off-cancel/continuous-adaptation status, and OCLA debug views.
- `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_ATE_*`: ATE-oriented RX/TX override fields, master MPLL loop controls, extra RX/TX override groups, and test-mode paths used by factory, validation, or low-level diagnostics rather than normal display policy.
- `DPCSSYS_CR0_RAWAONLANE0_DIG_*`, `DPCSSYS_CR0_RAWAONLANE1_DIG_*`, and the beginning of `DPCSSYS_CR0_RAWAONLANE2_DIG_*`: always-on lane calibration/status fields. These repeated per-lane groups include AFE/CTLE/DFE IDAC/VDAC offsets, RX adaptation measurements and completion flags, phase-adjust and slicer controls, MPLL coarse tune and disable bits, initialization power-up status, fast flags, common calibration status, TX/RX disable overrides, LOS/signal-detect filtering, PMA signal-detect overrides, signal-detect calibration codes, VREF generator controls, calibration code storage, DCC calibration code banks, TX DCC bank/data/continuous controls, MPLL bandgap controls, firmware calibration/adaptation/MM config bits, lane transceiver mode override/input fields, RX signal-detect config, TX DCC config, TX/RX DCC and bypass AC capacitor controls.

## Control Flow

This header chunk has no local control flow. It participates in runtime control flow through AMDGPU Display Core register-access code:

1. DCN401/DCN 4.1 display components include `dcn_4_1_0_sh_mask.h` along with generated offset headers.
2. Register-list macros and helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and related generated-table initializers token-paste register and field names into mask/shift lookups.
3. Display bring-up, link training, PHY configuration, DMUB servicing, IRQ setup, GPIO translation, resource construction, and clock/power code use those tables to program or inspect hardware registers.
4. For the DPCS families in this chunk, the actual sequencing is owned by link/PHY firmware or display driver hardware-sequencer code: reset/release, request/ack handshakes, rate/width/pstate transitions, adaptation/calibration requests, interrupt clear/mask handling, and PMA/PCS override programming.

The macros themselves do not encode ordering, access type, locking, or side effects. A consumer must know whether a field is a control, status bit, sticky interrupt, write-one-to-clear bit, read-only calibration result, or debug selector before using the mask.

## State And Persistence Behavior

This chunk stores no software state. It describes hardware state in DCN 4.1.0 DPCS/PHY registers:

- PCS RX/TX state: reset/request/data-enable controls, rate, width, pstate, low-power detect, VCO/ref load values, RX loss-of-signal thresholds, adaptation controls, EQ settings, TX pre/main/post cursor direction, termination controls, lane numbering, and ACK/status readbacks.
- Lane FSM state: fast startup/adaptation/calibration bypass or acceleration bits, continuous calibration/adaptation flags, common calibration/MPLL/RCAL status, TX DCC state, OCLA debug selection, and TX EQ update indicators.
- Interrupt state: per-lane IRQ status, clear, and mask fields for RX/TX handshake changes, adaptation changes, transceiver mode changes, calibration requests, loopback events, and DCC on-demand events.
- PMA bridge state: override enables/values for TX/RX resets, requests, power state, data enable, rate/width, impedance, MPHY loopback/mode, RX/TX PMA status, and RX adaptation feedback.
- Always-on analog lane state: AFE/CTLE/DFE calibration offsets, RX adaptation figures of merit and done bits, phase/slicer settings, MPLL coarse tuning and disable controls, signal-detect filtering/calibration, VREF generator and code values, DCC calibration code banks, firmware-owned calibration configuration, and TX/RX DCC controls.

Persistence is hardware-defined. Control fields generally persist until rewritten by link training, modeset, HPD handling, suspend/resume, runtime power transitions, GPU reset, or ASIC reset. Status, ACK, interrupt, calibration-done, calibration-code, and debug fields may be read-only, sticky, self-clearing, power-domain-dependent, or only valid while the related lane/PHY block is clocked and powered. This header does not mark those semantics.

## Dependencies And Integration Points

- These masks/shifts must match generated register offsets. The sampled DPCS names in this chunk map to `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` rather than only to `dcn_4_1_0_offset.h`; for example `ixDPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1`, `ixDPCSSYS_CR0_RAWAONLANE0_DIG_AFE_ATT_IDAC_OFST`, and `ixDPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0` are defined there. A whole-file merge should reconcile how DCN and DPCS generated headers are included together for this ASIC.
- `dcn_4_1_0_sh_mask.h` is included by DCN401 display code under `drivers/gpu/drm/amd/display/`, including DMUB support, IRQ service, clock manager, GPIO factory/translation, and resource construction.
- The field names integrate with the AMD Display Core register helper layer through generated structures of masks and shifts. The helper layer is responsible for read-modify-write behavior and field packing.
- Link training and PHY bring-up code depend on these fields indirectly for per-lane reset/request handshakes, rate/width programming, power-state changes, RX adaptation, signal detect, DCC, VREF, MPLL, and termination/equalization control.
- IRQ service and diagnostics depend on the lane IRQ status/clear/mask groups, OCLA fields, FSM status monitor fields, TX DCC status, RX adaptation FOM, signal-detect status, and calibration done/code fields.
- Firmware and hardware ownership boundaries matter. Several field families are explicitly ATE, firmware calibration/adaptation, or always-on lane controls; normal OS driver code may only observe them or program them through tightly constrained PHY sequences.

## Risks And Edge Cases

- The constants are untyped preprocessor macros. A wrong shift or mask can compile cleanly while writing the wrong hardware bit, corrupting neighboring fields, or reading meaningless status.
- Offset/header drift is the biggest integrity risk. DPCS names in this DCN mask header must be paired with the correct DPCS offsets; mixing generations or offset families can silently target unrelated MMIO addresses.
- Chunk boundaries are not semantic. `RX_OVRD_IN_1` begins before line 76588, and `RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0` continues after line 79052. Cross-chunk validation is needed before claiming full register-group coverage.
- Full-register writes are hazardous. Many registers mix override values with override enables, status bits with clear bits, or reserved bits with controls. Most consumers should use read-modify-write helpers and avoid writing reserved masks.
- PCS/PMA handshake fields are timing-sensitive. Misprogrammed reset/request/ack/rate/width/pstate bits can produce link-training hangs, blank displays, stuck lanes, or failures that only appear at specific link rates.
- RX adaptation and EQ fields are signal-integrity-sensitive. Incorrect masks for CTLE, VGA, DFE, phase adjustment, VREF, termination, or signal-detect calibration can cause intermittent link errors rather than immediate failures.
- Interrupt clear and mask fields have side effects. Treating clear fields like ordinary status, or writing the wrong lane's clear bit, can lose HPD/link-training diagnostics or create interrupt storms.
- Repeated RAWAONLANE0/1/2 layouts make copy-generation drift easy to miss. A field width error in one lane instance may pass tests that only exercise a different physical lane.
- Debug, ATE, firmware, and override fields can fight firmware-owned PHY flows. Leaving override enables set after diagnostics may break later link retraining, resume, or hotplug behavior.

## Test Signals

Useful validation combines generated-header consistency checks with hardware-oriented DCN 4.1/DPCS behavior:

- Build AMDGPU display/DCN401 code that includes `dcn_4_1_0_sh_mask.h`. Missing or malformed macros should fail in generated register tables or DCN401 DMUB, IRQ, clock, GPIO, and resource code.
- Mechanically compare this range against the authoritative DCN 4.1.0/DPCS register database and the matching DPCS offset header. Verify every complete register group has matching offset, shift, and mask names.
- Run static checks that complete fields have valid `(mask >> shift)` widths, do not overlap within a register unless intentionally aliased, and keep reserved fields out of normal programming tables.
- Exercise link training across all physical lanes represented by RAWLANE3 and RAWAONLANE0/1/2 coverage: low/high link rates, lane-count changes, retraining, HPD unplug/replug, and fallback from failed training.
- Validate RX adaptation and calibration paths using signal-quality counters or link error monitoring: EQ adaptation, CTLE/VGA/DFE controls, phase adjustment, signal-detect calibration, VREF, DCC, MPLL, and termination changes.
- Test interrupt handling around lane reset/request/rate/pstate/adaptation, phase-2 calibration, loopback, TX reset/request, and DCC on-demand events. Confirm status, mask, and clear semantics do not lose or repeat events.
- Run suspend/resume, runtime power management, and GPU reset tests while checking that always-on lane calibration state is either preserved as expected or reinitialized by the driver/firmware.
- Use debug/OCLA/status readback paths to confirm FSM state, TX DCC status, RX adaptation FOM/done bits, signal-detect outputs, and calibration codes are coherent after link bring-up and after forced retraining.
- Include multi-display and lane remapping cases so tests cover repeated lane instances rather than only a single happy-path lane.

## Cross-Chunk Notes

The previous chunk contains the beginning of `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1` and earlier RAWLANE3 PCS fields. The next chunk continues `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0` and the rest of RAWAONLANE2/possibly later lane calibration definitions. The final per-file research document should reconcile the DCN mask header with the DPCS offset headers before making whole-file claims about DPCS register coverage.
