# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 51608-54034

## Scope

This chunk is a generated AMD NBIO 6.1 shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, enums, variables, loops, branches, locks, allocations, or direct register accesses in this range.

The assigned range starts at `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MPLLA_SSC_CTL_OVRD_IN` and ends at `DWC_E12MP_PHY_X4_NS_X4_0_RAWLANE2_DIG_RX_CTL_OFFCAN_CONT_STATUS`. It covers 2,427 source lines, 358 register comment blocks, and 2,069 `#define` lines. The chunk is a partial view of a much larger file: the previous chunk contains earlier common PHY memory/control definitions, and the next chunk begins lane 3 definitions.

Although this file is under a local `ceph-client` source mirror, the path is AMDGPU hardware metadata for the NBIO 6.1 register database. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions and masks for a Synopsys DWC E12MP PCIe/PHY register block exposed through AMD NBIO 6.1. Each hardware field is represented by two macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for isolating or composing the field.

Runtime AMDGPU code combines these masks with matching register offsets from `nbio_6_1_offset.h` and default/reset values from `nbio_6_1_default.h`. Typical consumers use AMDGPU register helpers and field helpers such as `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`, depending on the address aperture and driver path.

This chunk specifically describes common MPLL spread-spectrum and bandwidth override fields plus lane-local digital PCS, PMA, FSM, always-on calibration/adaptation, interrupt, TX control, and RX control fields for lanes 0, 1, and most of lane 2 in an x4 PHY instance.

## Important Macro Families

The opening common-register block defines `RAWCMN_DIG_MPLLA_*` and `RAWCMN_DIG_MPLLB_*` override fields. These include MPLLA/MPLLB bandwidth override values and enables, spread-spectrum range, fractional-N control, spread-spectrum clock selection, and spread-spectrum enable override bits. These fields are common to the PHY rather than lane-specific and control PLL behavior shared by the x4 block.

The `RAWLANE0_DIG_*`, `RAWLANE1_DIG_*`, and `RAWLANE2_DIG_*` blocks repeat the same generated lane layout with the lane number embedded in each macro name. Lane 0 and lane 1 are complete in this chunk. Lane 2 is present through `RX_CTL_OFFCAN_CONT_STATUS`; its following `RX_CTL_ADAPT_CONT_STATUS` and lane 3 blocks are outside this range.

The PCS transmit interface blocks, such as `PCS_XF_TX_OVRD_IN`, `PCS_XF_TX_OVRD_IN_1`, `PCS_XF_TX_PCS_IN`, `PCS_XF_TX_OVRD_OUT`, and `PCS_XF_TX_PCS_OUT`, describe TX-side request/reset handshakes and operating state. Important fields include `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, master MPLLA/MPLLB state, override enable, reset/request override values and enables, receiver-detect request override, VBOOST enable override, IBOOST level override, ACK, receiver-detect result, and enable control.

The PCS receive interface blocks, such as `PCS_XF_RX_OVRD_IN`, `PCS_XF_RX_OVRD_IN_1`, `PCS_XF_RX_OVRD_IN_2`, `PCS_XF_RX_OVRD_IN_3`, and `PCS_XF_RX_PCS_IN*`, describe RX rate/width/power state, reset/request handshakes, adaptation controls, and calibration inputs. Fields include `RATE`, `WIDTH`, `PSTATE`, `LPD`, `OVRD_EN`, `ADAPT_AFE_EN`, `ADAPT_DFE_EN`, reset/request override bits, VCO load and low-frequency override fields, RX loss-of-signal threshold override, reference load override, adaptation request and continuous adaptation/off-cancellation controls, and PMA/PCS inputs for EQ evaluation, done/fail flags, calibration start/done flags, and associated diagnostic values.

The PCS RX status and direction blocks expose receive-side outputs and transmitter-adjustment feedback. Examples include `PCS_XF_RX_OVRD_OUT`, `PCS_XF_RX_PCS_OUT`, `PCS_XF_RX_ADAPT_ACK`, `PCS_XF_RX_ADAPT_FOM`, `PCS_XF_RX_TXPRE_DIR`, `PCS_XF_RX_TXMAIN_DIR`, `PCS_XF_RX_TXPOST_DIR`, and `PCS_XF_LANE_NUMBER`. These fields surface ACK, enabling, adaptation completion, figure-of-merit values, TX pre/main/post cursor direction requests, and lane identity.

The `FSM_*` blocks expose finite-state-machine override and monitor controls. `FSM_FSM_OVRD_CTL` contains scan-enable, FSM override, clock enable, raw-mode bypass, state-in, and FSM enable fields. `FSM_MEM_ADDR_MON` and `FSM_STATUS_MON` expose current FSM memory address and status outputs. The `FSM_FAST_*` blocks define fast-path control bits for RX startup calibration, RX adaptation, AFE calibration, DFE calibration, bypass calibration, reference-level calibration, IQ calibration, AFE/DFE adaptation, supervisor control, TX common mode, TX receiver detect, RX power-up, VCO wait, VCO calibration, and common calibration status.

The `AON_*` blocks describe always-on lane calibration and adaptation data. They include AFE/CTLE/VGA/DFE IDAC and VDAC offsets, phase-adjust linear/map values, data/bypass/error slicer offsets, IQ phase adjustment, MPLLA/MPLLB coarse tuning, RX/TX RTUNE values, initial power-up done, adapted ATT/VGA/CTLE and DFE tap values, RX adaptation done, fast flags, slicer controls, lane common-calibration status, and adaptation-control registers 0 through 7. Several of these are full 16-bit `DATA` style payloads or compact control/status fields.

The `IRQ_CTL_*` blocks expose receive-side interrupt status, clear, and mask fields for each lane. They cover reset return request, RX reset IRQ, RX request IRQ, RX rate IRQ, RX pstate IRQ, RX adaptation request IRQ, RX adaptation disable IRQ, corresponding clear bits, and an IRQ mask register with per-source mask bits.

The `PMA_XF_*` blocks describe PMA interface override and handshake fields. They include lane MPLLA/MPLLB enable in/out, lane override enable, supervisor MPLLA/MPLLB state override, PMA supervisor input state and RTUNE ACK, TX/RX request and reset override out fields, TX/RX PMA ACK inputs, and lane RTUNE request.

The lane-local `TX_CTL_*` and `RX_CTL_*` blocks describe control FSM timing and clocking. TX fields include wait time before MPLL off and per-power-state receiver-detect allowance bits, plus TX clock enable and clock select. RX fields include RX control FSM enable, rate-change-in-P1 behavior, RX LOS mask count, RX data-enable override count, internal reference tracking count, and off-cancellation continuous status. Lane 0 and lane 1 also include `RX_CTL_ADAPT_CONT_STATUS`; lane 2's corresponding field starts in the next chunk.

## APIs, Types, And Functions

There are no C APIs, types, or functions in this chunk. The exported interface is the macro namespace in `nbio_6_1_sh_mask.h`.

The macros are intended to be used with matching register offset definitions in `nbio_6_1_offset.h`. Include users in the AMDGPU tree commonly include generated ASIC register headers through NBIO, virtualization, PSP, display, and PowerPlay paths. Direct inclusion of this header by a source file does not mean every field in this chunk is actively referenced; generated hardware headers intentionally expose the vendor register database more broadly than current driver code uses.

## Control Flow

There is no executable control flow in this header. Runtime behavior is created by including code:

1. Driver code selects a register offset from the matching NBIO 6.1 offset header.
2. It reads a register through AMDGPU's register access layer or prepares a write value.
3. It extracts, clears, or composes fields using this chunk's `__SHIFT` and `_MASK` macros.
4. It writes the value back or uses the decoded status to drive PHY setup, link management, calibration, interrupt handling, diagnostics, reset, or power-state policy.

The hardware-level flow implied by the field names is the PCIe PHY lane state machine: common PLL configuration feeds per-lane PCS/PMA handshakes; TX and RX request/reset/ack bits coordinate lane transitions; RX calibration/adaptation bits report progress and quality; IRQ bits signal state changes; and TX/RX control registers tune clocking, receiver detect, LOS masking, data-enable timing, and continuous adaptation/off-cancellation behavior.

## State And Persistence Behavior

This header stores no software state and persists nothing. It describes hardware-backed state owned by the GPU PHY/NBIO block, firmware initialization code, and runtime AMDGPU paths.

The represented state includes common MPLL bandwidth and spread-spectrum override controls, per-lane TX/RX rate/width/power-state settings, reset/request handshakes, RX VCO/reference/LOS/adaptation controls, FSM override and monitor state, calibration and adaptation outputs, RTUNE data, interrupt pending/clear/mask state, PMA request/reset ACK handshakes, TX clock settings, RX LOS/data-enable timing, and continuous off-cancellation/adaptation status.

Some fields are control bits programmed by software or firmware, some are read-only hardware status, some are clear bits for interrupt state, and some are analog/PHY calibration data that may be latched or updated by hardware state machines. The masks do not encode reset defaults, access permissions, side effects, timing constraints, write-one-to-clear behavior, or sequencing requirements; those details must come from the hardware specification, firmware contract, defaults header, and driver code.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` provides matching offsets for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` provides reset/default values for the same register families where defaults are generated.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` provides related NBIO SMN address definitions.
- AMDGPU register helper macros provide the read/modify/write and field extraction mechanics that make these constants useful.

Integration points are AMDGPU NBIO setup, PCIe link and lane management, SR-IOV/MxGPU virtualization where guest-visible or host-controlled link state can matter, firmware/PSP-assisted initialization, power-management paths that adjust link state and PHY clocks, and diagnostic paths that inspect interrupts, calibration status, or PHY training state.

At the hardware boundary, these macros integrate with the DWC E12MP PHY x4 block: common PLLs, per-lane PCS/PMA crossings, lane FSMs, RX adaptation/calibration logic, interrupt logic, TX/RX control state machines, and analog front-end tuning state.

## Risks And Edge Cases

- Chunk boundaries are artificial. This range starts after earlier common PHY memory/control definitions and stops before lane 2's final RX adaptation-continuous status plus lane 3. The per-file merge must reconcile adjacent chunks for the complete PHY layout.
- The macros are untyped preprocessor constants. A stale mask, wrong shift, or wrong lane-number macro can compile cleanly while changing the wrong hardware bits.
- Lane 0, lane 1, and lane 2 blocks are highly repetitive. Copy/generation drift can create subtle lane-specific differences that are hard to find by visual inspection.
- Register offsets and masks must be paired from the same generated database. Using a `RAWLANE1` mask with a `RAWLANE2` offset, or mixing NBIO revisions, can produce plausible bit arithmetic against the wrong register.
- PLL bandwidth and spread-spectrum override fields are link-stability sensitive. Incorrect MPLL/SSC programming can affect PCIe clocking, link training, jitter tolerance, or compliance behavior.
- TX/RX reset, request, ACK, power-state, rate, width, and MPLL-enable fields are sequencing-sensitive. A read/modify/write in the wrong order can leave a lane stuck in reset, prevent ACK, race hardware state machines, or break link recovery.
- RX adaptation, VCO, LOS, RTUNE, slicer, DFE, AFE, CTLE, VGA, and IQ tuning fields are analog PHY controls/status. Wrong interpretation can degrade signal integrity without producing an immediate software failure.
- IRQ status, clear, and mask bits may have write-one-to-clear or sticky behavior in hardware. Treating clear fields like ordinary read/write bits can lose events or leave interrupt sources masked.
- FSM override and raw-mode bypass fields can bypass normal hardware sequencing. They are risky outside tightly controlled debug, firmware, or bring-up flows.
- Reserved masks are present throughout the chunk. Driver code must preserve reserved bits when doing read/modify/write unless the hardware specification says otherwise.

## Test Signals

Useful validation is mostly generated-header consistency, build coverage, and hardware/bring-up testing:

- Build AMDGPU code paths that include NBIO 6.1 headers. Missing or renamed macros should surface in NBIO, PSP, display, PowerPlay, or virtualization users.
- Compare this chunk against `nbio_6_1_offset.h` and `nbio_6_1_default.h` to confirm the common MPLL and lane 0/1/2 register names remain synchronized across shift/mask, offset, and default declarations.
- Run generated-register consistency checks that verify every field mask matches its shift and width expectations, does not overlap unexpected fields, and preserves reserved ranges.
- On NBIO 6.1 hardware, exercise PCIe link initialization, retraining, suspend/resume, runtime power transitions, and reset paths while monitoring lane ACK/status, PSTATE, RATE, WIDTH, MPLL enable/state, and IRQ bits.
- Stress SR-IOV or multi-function scenarios if supported, because per-lane/link state and NBIO virtualization paths may interact with guest-visible PCIe behavior.
- Use PHY diagnostics or firmware logs to validate RX adaptation, AFE/DFE/CTLE/VGA, VCO calibration, LOS masking, RTUNE, and slicer/phase adjustment state during link bring-up and error recovery.
- Inject or induce lane state changes where possible and verify IRQ pending, clear, and mask fields behave as expected for RX reset, request, rate, pstate, adaptation request, and adaptation disable events.
- Compare register dumps before and after driver initialization to confirm reserved bits are preserved and only expected override, control, and status fields change.

## Chunk Notes

- Lines 51608-51642 define common MPLLA/MPLLB spread-spectrum and bandwidth override masks.
- Lines 51643-52441 cover lane 0 PCS, FSM, AON calibration/adaptation, IRQ, PMA, TX control, and RX control field masks.
- Lines 52442-53240 repeat the same generated lane layout for lane 1.
- Lines 53241-54034 repeat lane 2 through `RAWLANE2_DIG_RX_CTL_OFFCAN_CONT_STATUS`; the next chunk continues lane 2 and starts lane 3.
