# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 76007-78466

## Scope

This chunk covers lines 76007-78466 of the generated AMD DCN 3.2.0 shift/mask header. It is preprocessor register metadata only: 2,098 `#define` entries across 2,460 source lines, with 1,044 `__SHIFT` constants, 1,054 `_MASK` constants, and 363 logical register groups. There are no C functions, structs, enums, variables, includes, allocations, locks, branches, or executable statements in this range.

The range starts inside `C20_PHY_CR0_RAWLANE3_DIG_TX_PCS_XF_OVRD_IN_1`, with only its trailing mask definitions visible. It then covers most of the C20 PHY CR0 raw lane 3 digital TX/RX PCS, FW, IRQ, PMA, control, and finite-state-machine register fields, followed by the always-on lane 0 TX/RX firmware, calibration, DCC, IDAC/VDAC, and IQ calibration fields. It ends inside `C20_PHY_CR0_RAWLANEAON0_DIG_RX_IQ_CAL_BANK_3`, with only the two shift constants visible for that final register; the corresponding masks continue in the next chunk.

## Purpose

The purpose of this header slice is to publish exact bit positions and masks for DCN 3.2.0 PHY control registers. AMDGPU display, DMUB, GPIO, IRQ, resource, and low-level GPU memory-controller code include `dcn_3_2_0_sh_mask.h` with the matching offset headers so register helper macros can pack MMIO writes and decode MMIO reads without hand-coding field positions.

This chunk is a generated hardware contract. Runtime behavior lives in the code that consumes these constants. The constants here describe field layout for raw PHY lane control, firmware handshakes, interrupt controls, calibration control/status, margining, loopback, deskew, power-up, and analog trim/calibration registers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- `//<REGISTER>` comments group related field definitions under one hardware register.

Important register families in this chunk include:

- `C20_PHY_CR0_RAWLANE3_DIG_TX_PCS_XF_*`: TX PCS cross-fabric override, input, output, and context configuration fields for reset/request handshakes, power state, low-power detect, data enable, inversion, clock ready, beacon enable, MPLL selection/state, receiver detect, deskew, recalibration, context select, rate, width, DCC range, termination, boost, KR drive, and unique ID.
- `C20_PHY_CR0_RAWLANE3_DIG_TX_FW_XF_*`: TX firmware cross-fabric override, input, output, and lane-number fields for reset/request, power state, low-power detect, rate, MPLL selection, MPLL enable, master MPLL state, acknowledgement, and DETRX result.
- `C20_PHY_CR0_RAWLANE3_DIG_TX_IRQ_CTL_*`: TX interrupt mask, enable, status, and clear fields for TX rate/reset/request, RX-to-TX parallel loopback enable/disable, RTUNE, TX termination control, and lane transceiver mode.
- `C20_PHY_CR0_RAWLANE3_DIG_TX_CTL_*`: TX controller fields for FSM override/initial state/disable flags, clock gate controls, off-cancel continuous status, rate IRQ acknowledgement, termination code, firmware power-up done, and MPLLA/MPLLB restart calibration controls.
- `C20_PHY_CR0_RAWLANE3_DIG_TX_PMA_XF_*`: TX PMA cross-fabric lane/supervisor override and input/output fields for loopback, link number, ACK/REQ, RTUNE acknowledgement, TX disable, and PMA lane RTUNE control.
- `C20_PHY_CR0_RAWLANE3_DIG_RX_PCS_XF_*`: RX PCS cross-fabric override, input, output, and context configuration fields for reset/request, PSTATE, rate, width, invert, elastic-buffer mode, PLL selection, foreground calibration, adaptation request, PLL ready/detect enable, CDR control, terminal control, offset control, eye shaping, lossy detection, and data bus inversion.
- `C20_PHY_CR0_RAWLANE3_DIG_RX_FW_XF_*`: RX firmware override/input/output fields for reset/request, PSTATE, rate, CDR enable/done, foreground calibration, adaptation enable/request, acknowledgement, adaptation FOM, TX pre/main/post direction hints, clock control, and margining-related output.
- `C20_PHY_CR0_RAWLANE3_DIG_RX_IRQ_CTL_*`: RX interrupt mask, enable, status, and clear fields for reset, request, rate, PSTATE, adaptation request/disable, termination control, margin IQ/VDAC start, margin error clear, margin init/finish, and global margin interrupts.
- `C20_PHY_CR0_RAWLANE3_DIG_RX_CTL_*`: RX controller status/control fields for termination code, off-cancel/adaptation status, adaptation mode/select, PPM drift, CDR detect, PMA misc control, adaptation-mode override/enable, FOM values, reference errors, IQ/phase adjustment, margin status/error, FSM control, rate IRQ acknowledgement, and IQ linear/step read/write codes.
- `C20_PHY_CR0_RAWLANE3_DIG_FSM_*`: lane firmware/FSM controls for override and jump-bank selection, breakpoint and monitor registers, firmware configuration stage, scratch registers, CR lock, fast-path controls, startup/continuous calibration skip controls, and RX calibration status.
- `C20_PHY_CR0_RAWLANEAON0_DIG_TX_*`: always-on TX firmware state, SRAM recording controls, CCA timing, startup/continuous algorithm controls, fast flags, high-power protection override/input, lane transceiver mode override/input, init power-up done, override inputs, MPLLA/MPLLB DCC calibration banks, calibration-done flags, DCC code readouts, calibration bank selection, and TX inputs.
- `C20_PHY_CR0_RAWLANEAON0_DIG_RX_*`: always-on RX startup calibration/adaptation algorithm controls, continuous adaptation controls, fast flags, VGEN/signal-detect/AFE/reference/DFE/IDAC/VDAC offsets, IQ calibration bounds/reset/adjustment, and DCC/full/half data, bypass, phase, IQ, and calibration-done banks.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. DCN 3.2.0 consumers include `dcn/dcn_3_2_0_offset.h` and `dcn/dcn_3_2_0_sh_mask.h`.
2. Register tables and helper macros concatenate register and field names with `__SHIFT` or `_MASK`.
3. Runtime code uses the resolved constants in MMIO helper operations such as register set/update/get paths, IRQ status decoding, DMUB register access, GPIO translation, and generation-specific resource setup.
4. Hardware performs the actual state transitions: firmware handshakes, PHY lane state machines, interrupts, calibration sequencing, margining, PLL/deskew/recalibration behavior, and analog trim read/write behavior.

The declaration order follows hardware register layout, not software execution order. Repeated fields are expanded as independent macros for lane 3 raw-lane registers and for always-on lane 0 calibration/status banks.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes bit locations for state held in DCN 3.2.0 display PHY hardware registers.

Writable fields in this range can request or override PHY lane resets, power state, rates, widths, PLL selection/enables, deskew, receiver detect, recalibration, loopback, termination, RTUNE, PMA enable/disable, calibration skip/fast-path behavior, algorithm controls, SRAM recording, high-power protection, transceiver mode, DCC values, IDAC/VDAC offsets, and IQ calibration parameters.

Hardware-updated fields expose acknowledgements, firmware power-up completion, DETRX result, IRQ status, IRQ clear side effects, off-cancel/adaptation status, CDR detect, FOM values, margining status/error, FSM monitors, scratch registers, calibration-done bits, DCC code readouts, IQ calibration banks, and RX calibration status. This generated file does not encode access type, reset values, write-one-to-clear semantics, polling requirements, timing delays, or required programming sequences.

Programmed values persist according to the PHY, lane, firmware, and always-on power/reset domains. They may survive ordinary register reads, but can be rewritten by firmware, lost on PHY/display power gating, reset by lane/FSM resets, restored during modeset/link training flows, or invalidated by suspend/resume and GPU reset paths.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.2.0 offset/header database. The shift/mask header provides bit positions only; it must be paired with matching offset macros for actual MMIO addresses and instances.

Primary includes of `dcn_3_2_0_sh_mask.h` in this tree include:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`, which uses DCN32 register definitions for DMUB-controlled display hardware access.
- `drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`, which uses generated masks/shifts to decode and manage DCN32 IRQ sources.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c` and `hw_factory_dcn32.c`, which integrate DCN32 register definitions with GPIO/DDC/AUX hardware translation.
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`, which wires DCN32 resource tables and hardware block constructors to generated register metadata.
- `drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`, which includes DCN32 masks for generation-specific GPU memory-controller/display-adjacent register work.

The specific fields in this chunk are more PHY/firmware/lane-control oriented than DPP color/scaler oriented. They integrate with link bring-up, link training, PHY power sequencing, interrupt handling, DMUB firmware coordination, debug/margining paths, and low-level diagnostics rather than with high-level plane composition.

## Risks And Edge Cases

- The chunk starts mid-register. Only trailing masks for `C20_PHY_CR0_RAWLANE3_DIG_TX_PCS_XF_OVRD_IN_1` are present; its shifts and early masks are in the previous chunk.
- The chunk ends mid-register. `C20_PHY_CR0_RAWLANEAON0_DIG_RX_IQ_CAL_BANK_3` includes `HALF_RATE_VAL__SHIFT` and `FULL_RATE_VAL__SHIFT`, but its masks continue in the next chunk.
- Many TX/RX override registers pair a value bit with an `*_OVRD_EN` bit. Using a value mask without enabling the override, or enabling an override with stale data, can silently force wrong PHY behavior.
- IRQ registers use separate mask, enable, status, and clear fields with visually similar names. Confusing status and clear masks can drop interrupts or leave IRQs stuck.
- Firmware cross-fabric handshakes depend on ACK/REQ/reset sequencing. These constants do not protect callers from polling the wrong acknowledgement bit or racing firmware ownership.
- Calibration and DCC fields are banked and repeated for MPLLA/MPLLB, full/half rate, data/bypass/phase, and banks 0-3. Copy/paste or generator drift can compile but apply calibration to the wrong bank or PLL.
- Analog trim and VDAC/IDAC fields are display-link sensitive. Wrong masks can appear as link training failures, intermittent hotplug/link instability, poor signal margin, or marginal high-rate behavior rather than obvious software faults.
- FSM fast/skip controls can bypass calibration or adaptation. Incorrect use can shorten bring-up in a lab setting while destabilizing real hardware, so consumers must treat these as hardware-specific controls rather than generic optimization toggles.
- Several masks use packed 16-bit fields with high-byte/low-byte layout and constants ending in `L`. Nonstandard helper code should preserve unsigned-width behavior when shifting or inverting masks.

## Test Signals

Useful validation is mostly build-time consistency plus hardware/link integration:

- Build AMDGPU with DCN32 enabled to catch missing or renamed macros in `dmub_dcn32.c`, `irq_service_dcn32.c`, GPIO DCN32 code, `dcn32_resource.c`, and `gmc_v11_0.c`.
- Mechanically verify that each complete register group in this chunk has paired `__SHIFT` and `_MASK` definitions for every field, allowing for the intentionally partial first and last register groups.
- Compare this slice against the authoritative DCN 3.2.0 register database and matching offset header to ensure each raw-lane and always-on register maps to the intended hardware address and field layout.
- Exercise DCN32 link bring-up and retraining across common DisplayPort/HDMI rates so TX/RX PCS/FW handshakes, MPLL selection, CDR enable/done, rate changes, deskew, and recalibration paths use real values.
- Exercise hotplug, suspend/resume, GPU reset, and display power-gating paths to verify PHY lane and always-on calibration state is restored or reinitialized correctly.
- Exercise IRQ paths for TX/RX rate, reset, request, adaptation, margining, RTUNE, termination, and lane-mode events. Expected signals are correct status decode, clear behavior, and no stuck or missing IRQs.
- Exercise diagnostic/margining paths where available: read FOM values, margin status/error, IQ/phase adjustment fields, CDR detect status, FSM status monitors, scratch registers, and calibration-done flags.
- Exercise PHY debug or lab flows that use fast/skip calibration controls only on supported hardware, verifying link quality and error counters before and after bypassing calibration steps.

## Open Cross-Chunk Notes

The merge lane should combine this chunk with the previous chunk to describe `C20_PHY_CR0_RAWLANE3_DIG_TX_PCS_XF_OVRD_IN_1` completely. It should combine this chunk with the next chunk to complete `C20_PHY_CR0_RAWLANEAON0_DIG_RX_IQ_CAL_BANK_3` and continue the always-on RX register sequence. Whole-file analysis should reconcile this PHY-heavy slice with neighboring DCN 3.2.0 chunks before making final claims about the complete C20 PHY raw-lane and always-on register coverage.
