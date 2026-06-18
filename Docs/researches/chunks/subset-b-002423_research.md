# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 89939-92390

## Chunk Scope

This chunk is part of the generated AMD DPCS 4.2.3 shift/mask header. It contains C preprocessor constants only: register field `__SHIFT` macros and matching `_MASK` macros for 16-bit DPCS payload fields. There are no functions, structs, enums, executable statements, or kernel-owned storage declarations.

The range starts inside `DPCSSYS_CR4_RAWLANE2_DIG_FSM_FAST_RX_REFLVL_CAL`: the two shift macros for that register are immediately before the chunk, while this chunk contains its masks. It then covers the remainder of RAWLANE2 CR4 digital FSM/IRQ/PMA/TX/RX/PCS helper blocks, the corresponding RAWLANE3 CR4 digital lane blocks, and the beginning of the RAWAON always-on lane calibration/readback area for RAWAONLANE0 and RAWAONLANE1. The final line is only the `DPCSSYS_CR4_RAWAONLANE1_DIG_ADPT_CTL_0__VAL__SHIFT` macro; its `_MASK` appears in the next chunk.

## Purpose

The macros define how AMD display code packs and extracts fields in DPCS 4.2.3 indirect registers for CR4 lane programming. The paired `dpcs_4_2_3_offset.h` file supplies the `ix...` register indices, while this header supplies the bit positions and masks for fields inside each register. Together they let AMDGPU/DC code use generated names for link PHY programming instead of hard-coded bit numbers.

The hardware areas represented here are:

- RAWLANE2 tail: fast RX calibration/adaptation FSM bits, common calibration status, continuous calibration flags, CR register/memory lock bits, TX DCC status, OCLA debug selection, TX equalization update flag, IRQ status/clear/mask fields, PMA transfer bridge fields, TX/RX controller controls, and ATE/PCS override registers.
- RAWLANE3 full digital lane pattern for the same CR4 instance: PCS TX/RX request and override registers, lane number and termination/equalization controls, phase-2 calibration, FSM control/status and fast calibration flags, IRQ status/clear/mask fields, PMA bridge registers, TX/RX controller fields, and ATE/PCS test override registers.
- RAWAONLANE0 always-on analog/calibration block: adaptation readbacks, DFE/CTLE/VGA/ATT offset values, RX phase and IQ adjustment, MPLL coarse tune, power-up done state, fast calibration flags, adaptation control words, signal-detect and DCC calibration codes, TX DCC bank access, firmware configuration words, and lane transceiver mode fields.
- RAWAONLANE1 beginning: the same always-on analog/adaptation readback pattern through lane common MPLL calibration status and the first `ADPT_CTL_0` shift.

## Important APIs, Types, and Macros

There are no callable APIs. The exported surface is the macro namespace:

- `DPCSSYS_CR4_RAWLANE2_DIG_FSM_*`: lane 2 FSM fast-path calibration/adaptation controls and status. Single-bit registers cover `FAST_RX_IQ_CAL`, `FAST_RX_AFE_ADAPT`, `FAST_RX_DFE_ADAPT`, `FAST_SUP`, `FAST_TX_CMN_MODE`, `FAST_TX_RXDET`, `FAST_RX_PWRUP`, `FAST_RX_VCO_WAIT`, `FAST_RX_VCO_CAL`, and continuous RX calibration/adaptation phases. Aggregate `FAST_FLAGS` exposes TX/RX fast DCC, VPHUD, VREF, signal-detect, continuous calibration, and `TX_SKIP_SUP_CAL` bits.
- `DPCSSYS_CR4_RAWLANE2_DIG_IRQ_CTL_*` and `DPCSSYS_CR4_RAWLANE3_DIG_IRQ_CTL_*`: per-lane interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation, phase-2 calibration request/disable, lane transceiver-mode changes, RX-to-TX serial loopback, DCC on-demand, and TX reset/request.
- `DPCSSYS_CR4_RAWLANE2_DIG_PMA_XF_*` and `DPCSSYS_CR4_RAWLANE3_DIG_PMA_XF_*`: transfer fields between digital lane control and PMA. They include lane override in/out bits, supervisor PMA input, TX/RX request and reset handshakes, data enable and beacon fields, RTUNE control, MPHY overrides, and RX adaptation override output.
- `DPCSSYS_CR4_RAWLANE2_DIG_TX_CTL_*` / `RX_CTL_*` and matching RAWLANE3 macros: lane-local TX/RX controller fields. These define TX FSM control, TX clock control, continuous TX DCC status, OCLA/UPCS debug enables, RX FSM behavior, LOS masking, RX data-enable override timing, off-cancel status, and adaptation continuous status.
- `DPCSSYS_CR4_RAWLANE2_DIG_PCS_XF_*` and `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_*`: PCS-facing override, test, ATE, and transfer fields. RAWLANE3 starts at the beginning of this group in this chunk, including TX request/reset/pstate/rate/MPLL controls, RX reset/request/rate/pstate/equalization/adaptation controls, loopback and termination override fields, raw PCS input/output fields, RX adaptation acknowledge/FOM, TX pre/main/post direction fields, lane number, phase-2 calibration, and extra ATE override registers.
- `DPCSSYS_CR4_RAWAONLANE0_DIG_*` and `DPCSSYS_CR4_RAWAONLANE1_DIG_*`: always-on analog lane readbacks and calibration controls. Important fields include adaptation values (`RX_ADPT_IQ`, `ATT`, `VGA`, `CTLE`, `DFE_TAP1` through `DFE_TAP5`), DFE reference/offset values, phase adjust values, MPLL coarse tune and calibration status, signal detect calibration/codes, VREF generation and calibration codes, RX/TX DCC calibration storage, firmware configuration words, and lane transceiver mode override/input fields.

Most masks are narrow 16-bit constants such as `0x0001L`, `0x00FFL`, `0x03FFL`, `0x0FFFL`, `0x1FFFL`, or reserved masks like `0xFFFEL`/`0xFF00L`. A few fields expose full-register 16-bit payloads with `VAL` or `DATA` at shift zero. The generated header does not define legal value enums, sequencing rules, or composed register values.

## Control Flow

This chunk has no software control flow, but the field names describe hardware handshakes that driver code must sequence correctly:

- Request/acknowledge and reset paths are represented by TX/RX `REQ`, `ACK`, `RESET`, pstate, rate, data-enable, beacon, phase-2 calibration, and adaptation fields.
- Override registers commonly separate value and enable fields, for example `*_OVRD_VAL` with `*_OVRD_EN`. Programming code must set both when forcing a lane state and clear enable bits when returning control to hardware FSMs.
- Interrupt handling uses distinct status, clear, and mask registers. RX and TX events have separate clear macros, so clear writes must target the clear register rather than the status or mask register.
- FSM controls expose debug/manual paths such as fast calibration flags, lock bits, command/status monitors, and OCLA/UPCS visibility. The sequencing for using those paths lives in hardware programming flows outside this generated header.

## State and Persistence

The state described by these macros lives in DPCS hardware registers. It is not persisted by this header and does not allocate memory. Register values persist according to hardware lifetime: they may remain until a later write, link retrain, power-gate transition, display engine reset, or ASIC reset.

State categories visible in this chunk include:

- Link and lane configuration: lane number, width/rate, pstate, low-power detect, MPLL selection/enables, TX/RX termination, loopback, data enable, beacon, and transceiver mode.
- Calibration and adaptation state: RX AFE/DFE/CTLE/VGA/ATT values, DFE taps and offsets, IQ and phase adjustment, reference levels, signal-detect thresholds/codes, VREF and DCC calibration codes, MPLL/RCAL status, and fast/continuous calibration flags.
- Handshake and interrupt state: reset/request/acknowledge bits, adaptation request/disable bits, IRQ mask/clear/status bits, and DCC on-demand events.
- Debug/test state: ATE overrides, OCLA/UPCS enables, firmware configuration words, raw PCS/PMA override fields, and reserved/debug registers.

Reserved field masks are emitted for many registers. Callers should preserve reserved bits unless a hardware programming guide explicitly requires a whole-register write.

## Dependencies and Integration Points

The direct include site in this source tree is `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`. This ties the generated DPCS 4.2.3 register definitions to the DCN 3.1.6 display resource path.

This chunk depends on:

- The matching offset header. Examples from the paired file include `ixDPCSSYS_CR4_RAWLANE2_DIG_FSM_FAST_RX_REFLVL_CAL` at `0x3228`, `ixDPCSSYS_CR4_RAWLANE2_DIG_FSM_FAST_FLAGS` at `0x3238`, and `ixDPCSSYS_CR4_RAWAONLANE1_DIG_ADPT_CTL_0` at `0x4124`.
- AMD DC register access conventions that combine generated offsets, shifts, and masks through `REG_SET`, `REG_GET`, `REG_FIELD`, table-driven register definitions, or equivalent helpers outside this header.
- Hardware generator input for DPCS 4.2.3. The comments and macros are generated register descriptions; semantic constraints such as allowed values, delays, and polling timeouts must come from the display PHY programming sequences.
- Neighboring generated DPCS headers for related ASIC revisions, such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_2_sh_mask.h`, which contain very similar CR4 lane symbols. They are useful for comparison but should not be mixed with the 4.2.3 offset/mask pair.

## Risks and Maintenance Notes

- The chunk boundaries split two register definitions. `FAST_RX_REFLVL_CAL` starts before the chunk, and `RAWAONLANE1_DIG_ADPT_CTL_0` completes after it. The later merge lane should reconcile these partial registers with adjacent chunk research.
- These constants are generated hardware ABI. A one-bit shift or mask error can misprogram display PHY calibration, link training, low-power transitions, or interrupt handling.
- RAWLANE2 and RAWLANE3 have near-identical field groups. Copying a lane 2 macro into lane 3 programming, or vice versa, could produce failures only on connectors using that physical lane mapping.
- RAWAONLANE0 and RAWAONLANE1 analog calibration fields are also repetitive and visually similar. Lane-index mistakes may corrupt per-lane calibration readbacks or overrides.
- Many fields are override or test-oriented (`ATE`, `OCLA`, raw PCS/PMA override, DCC banks, firmware config). Those fields may require the link to be idle or a hardware FSM to be stopped even though the header cannot encode that ordering.
- Interrupt clear and mask fields are separate from interrupt status fields. Incorrect writes can lose events, leave a stale interrupt asserted, or mask a real link-training problem.
- Reserved masks are present and easy to include accidentally in generated whole-register writes. Software should use the field masks intentionally and avoid writing reserved bits without hardware documentation.

## Test Signals

Useful validation for changes touching this area includes:

- Build coverage for the AMD display/DCN 3.1.6 path that includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static consistency checks that every referenced `DPCSSYS_CR4_RAWLANE2_*`, `DPCSSYS_CR4_RAWLANE3_*`, and `DPCSSYS_CR4_RAWAONLANE*` shift/mask macro has a corresponding `ix...` offset in `dpcs_4_2_3_offset.h`.
- Cross-generation diffing against `dpcs_4_2_0` and `dpcs_4_2_2` to distinguish intentional generated changes, such as mask width formatting, from accidental drift.
- Hardware smoke tests on an affected AMD ASIC: boot, connector enumeration, DisplayPort/USB-C link training across rates and lane counts, hotplug/replug, suspend/resume, repeated modesets, and link retraining.
- PHY diagnostic signals around RX adaptation and calibration: adaptation done/ack/FOM, DFE tap values, signal detect codes, DCC continuous status, phase-2 calibration interrupts, and IRQ mask/clear behavior during retrain and low-power transitions.
