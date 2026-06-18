# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 118753-121323

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 1,965 `#define` field-layout macros and 606 register comment markers across 2,571 source lines. There are no C functions, structs, enums, global objects, locks, allocations, or executable statements in this range.

The range covers a late portion of the Synopsys/DesignWare-style `DWC_E12MP_PHY_X4_NS_X4_3` PCIe PHY register namespace. It starts in the middle of common PHY RAM field definitions, covers the tail of `RAWCMN_DIG_MEM_CMN5`, most of `RAWCMN_DIG_MEM_CMN6`, common control and MPLL spread-spectrum override fields, a complete RAWLANE0 digital PCS/FSM/AON/IRQ/PMA/TX/RX slice, and the beginning of the corresponding RAWLANE1 slice through early always-on adaptation result fields. The line boundary is artificial: the previous chunk owns the beginning of the common memory block, and the next chunk is needed for the rest of RAWLANE1 and later lane/shared PHY definitions.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of AMD's generated NBIO 6.1 hardware register interface. For each named register, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit index used to position a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update that field.

The companion `nbio_6_1_offset.h` supplies matching register offsets, and `nbio_6_1_default.h` supplies reset/default values for many generated register names. Runtime AMDGPU code combines these constants with register access helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/NBIO MMIO or SMN access paths.

This chunk describes the layout for low-level PCIe PHY common memory, common PLL/SSC override controls, and lane-local PCS, FSM, analog adaptation, interrupt, PMA, TX, and RX controls. These definitions are hardware metadata for the AMD GPU NBIO/PCIe stack, not Ceph or filesystem logic despite the repository mirror path.

## Important Macro Families

The common block at the beginning contains generated `DATA` field masks for common PHY memory rows:

- `RAWCMN_DIG_MEM_CMN5_B2_R4` through `RAWCMN_DIG_MEM_CMN5_B7_R31`, plus the chunk-leading tail mask for `B2_R3`.
- `RAWCMN_DIG_MEM_CMN6_B0_R0` through `RAWCMN_DIG_MEM_CMN6_B6_R31`.
- Each row exposes a 16-bit `DATA` field at shift `0x0` with mask `0xFFFFL`, indicating raw common-memory words rather than named semantic subfields.

The common digital control and PLL override portion includes:

- `RAWCMN_DIG_CMN_CTL`, with common PMA datapath enable, BIST enable, and common initialization skip controls.
- `RAWCMN_DIG_MPLLA_BW_OVRD_IN` and `RAWCMN_DIG_MPLLB_BW_OVRD_IN`, each splitting PLL bandwidth override values into low/high fields and enable bits.
- `RAWCMN_DIG_MPLLA_SSC_CTL_OVRD_IN`, `RAWCMN_DIG_MPLLA_SSC_EN_OVRD_IN`, and their MPLLB equivalents, covering spread-spectrum clocking override controls such as SSC step size, peak value, enable, and override enable.

The RAWLANE0 block is complete in this chunk and covers:

- PCS TX cross-function controls: `TX_OVRD_IN`, `TX_OVRD_IN_1`, `TX_PCS_IN`, `TX_OVRD_OUT`, and `TX_PCS_OUT`, including TX rate/width/elecidle/detect/boost/deemphasis/preset handoff fields and corresponding override enables.
- PCS RX cross-function controls: `RX_OVRD_IN`, `RX_OVRD_IN_1` through `_3`, `RX_PCS_IN` through `_4`, `RX_OVRD_OUT`, `RX_PCS_OUT`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, TX pre/main/post direction feedback, and `LANE_NUMBER`.
- Lane FSM controls and status: `FSM_OVRD_CTL`, `MEM_ADDR_MON`, `STATUS_MON`, fast-path enables for RX startup, adaptation, AFE/DFE/bypass/ref-level/IQ calibration, supervisor steps, TX common mode, TX receiver detect, RX power-up, RX VCO wait/calibration, and `CMNCAL_STATUS`.
- Always-on analog calibration and adaptation state: AFE attenuator/CTLE/VGA IDAC offsets, DFE summer/phase/data/bypass/error offsets for even and odd paths, RX phase-adjust controls, IQ phase adjust, MPLLA/MPLLB coarse tune, RTUNE RX/TX values, initial power-up done, RX adaptation values for ATT/VGA/CTLE and DFE taps 1-5, adaptation done, fast flags, slicer controls, lane common-calibration status, and generic `ADPT_CTL_0` through `ADPT_CTL_7`.
- Lane interrupt controls: reset return request, RX reset/request/rate/power-state/adaptation request/adaptation-disable IRQ status bits, matching clear bits, and `IRQ_MASK` fields.
- PMA and lane datapath handoff fields: lane/supervisor override inputs and outputs, TX/RX override outputs and PMA inputs, lane RTUNE control, TX FSM/clock control, RX FSM control, loss-of-signal mask control, RX data-enable override control, off-channel continuous status, and adaptation continuous status.

The RAWLANE1 block starts a repeat of the same lane-local pattern for `RAWLANE1`. This chunk includes its PCS TX/RX cross-function groups, FSM controls and status, fast-path calibration controls, common-calibration status, and early always-on fields through `RX_ADPT_VGA`. The next chunk is needed for the remainder of RAWLANE1 AON adaptation, interrupt, PMA, TX, and RX definitions.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace. Consumers depend on the generated register names, field names, shifts, and masks remaining synchronized with AMD's NBIO 6.1 register database, sibling offset/default headers, and the actual GPU hardware.

The constants are untyped preprocessor integer literals, usually with an `L` suffix on masks. They encode bit positions and masks only. They do not describe register access width, read/write permission, reset value, volatility, write-one-to-clear behavior, required sequencing, firmware ownership, or side effects. Those semantics must come from the hardware specification and the driver access path.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU NBIO, PCIe, power-management, virtualization, reset, or diagnostics code selects a register offset from `nbio_6_1_offset.h`.
2. The code reads or writes the hardware register through AMD register access helpers.
3. Field values are decoded with this chunk's `SHIFT` and `MASK` macros, or updated by preserving unrelated bits and inserting a new field value.
4. The resulting register operation participates in PCIe PHY initialization, link training, lane calibration/adaptation, PLL/SSC programming, interrupt acknowledgement, power-state transition, reset handling, SR-IOV policy, or debug collection.

Likely flows using this chunk include programming common memory words, enabling/disabling PMA datapath or BIST paths, overriding MPLLA/MPLLB SSC behavior, controlling RAWLANE0 TX/RX PCS handshakes, monitoring lane FSM progress, forcing or accelerating calibration steps, collecting RX adaptation results, clearing/masking lane IRQs, and observing PMA/TX/RX lane status.

## State And Persistence Behavior

The header itself stores no state. It names state held in NBIO 6.1 PCIe PHY registers. Persistence is determined by GPU reset domains, PCIe link reset, PHY reset, suspend/resume save-restore, firmware/SMU initialization, SR-IOV partitioning, and explicit driver writes.

Represented state includes raw common-memory data, common control enables, MPLLA/MPLLB bandwidth and SSC override state, PCS TX/RX handoff state, RX equalization and adaptation inputs/results, FSM override and status bits, fast calibration enables, common-calibration status, analog trim/offset values, RTUNE values, initial power-up state, lane IRQ status/clear/mask bits, PMA override state, TX FSM and clock controls, RX FSM/data-enable/loss-of-signal controls, and continuous adaptation/off-channel status.

Several fields are not passive storage. PLL/SSC fields affect shared clocking; PMA datapath and BIST controls can change PHY operating mode; FSM override and fast-calibration bits can alter lane microsequencing; interrupt clear fields acknowledge latched events; PMA/PCS override fields can bypass normal hardware or firmware ownership; and adaptation result fields are meaningful only after corresponding done/status bits show valid data.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 6.1 register data and must stay aligned with sibling generated headers:

- `nbio_6_1_offset.h` supplies matching offsets for the `DWC_E12MP_PHY_X4_NS_X4_3_*` register names.
- `nbio_6_1_default.h` supplies reset/default values for many common, lane, PLL, RTUNE, adaptation, and control registers.
- AMDGPU field helper macros consume these shift/mask constants for extraction and update.

Direct include users in this tree include AMDGPU NBIO, virtualization, and power-management code such as `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega powerplay include bundles. The broader integration surface is PCIe link bring-up, GPU reset, runtime power management, SR-IOV/mxGPU operation, hardware diagnostics, and register dumps.

The generated `X4_3` instance naming indicates this is one physical x4 PHY instance's register namespace. RAWLANE0 and RAWLANE1 definitions are lane-local within that instance, while the RAWCMN definitions are shared by the instance. Call sites must respect that shared-vs-lane ownership distinction.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while programming the wrong hardware bit. This is especially risky for PLL/SSC, reset, PMA datapath, FSM override, interrupt clear, and adaptation-control fields.
- The chunk starts and ends mid-family. The previous chunk is needed for the complete `RAWCMN_DIG_MEM_CMN5_B2_R3` context, and the next chunk is needed for the rest of RAWLANE1.
- Common memory rows expose opaque 16-bit `DATA` words. A correct mask does not validate the semantic payload written into those words.
- RAWLANE0 and RAWLANE1 field families are intentionally repetitive. A lane-specific generator error or typo can be hard to spot but may affect only one physical lane.
- PLL bandwidth and SSC override fields are shared resources. Incorrect writes can destabilize all lanes on the PHY instance, not just the lane currently being debugged.
- Override fields can conflict with hardware FSMs, firmware/SMU ownership, or normal PCIe link training if used without sequencing, polling, and timeouts.
- Interrupt clear fields must match hardware clear semantics. Treating them like ordinary writable state can drop events or leave stale events latched.
- Adaptation and calibration result fields should be consumed only in a suitable lane power/link state and after done/status bits indicate validity.
- Reserved masks are present for full register preservation, but driver code should avoid intentionally changing reserved bits unless the hardware programming guide requires preserving read values.

## Test Signals

- Build AMDGPU with NBIO 6.1 support enabled. Direct macro users should catch missing, renamed, or malformed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: offset-to-field pairing, shift/mask width checks, non-overlap checks within registers, reserved-field coverage, and RAWLANE0/RAWLANE1 repetition checks.
- Compare `nbio_6_1_sh_mask.h`, `nbio_6_1_offset.h`, and `nbio_6_1_default.h` for matching `DWC_E12MP_PHY_X4_NS_X4_3_*` register families and default-compatible field widths.
- Runtime probe on affected NBIO 6.1 GPUs should show stable PCIe link training, negotiated width/speed, PLL lock behavior, and absence of unexpected PHY reset, clock instability, or link flapping.
- PHY diagnostics should decode RAWLANE0 and RAWLANE1 lane number, FSM status, RX adaptation values, RTUNE values, and common-calibration status consistently.
- Interrupt validation should exercise RAWLANE0 reset/request/rate/power-state/adaptation events, mask behavior, clear behavior, and absence of repeated stale events.
- Suspend/resume, GPU reset, and SR-IOV/PF-VF tests should verify that common PLL/SSC/control state and lane-local PCS/FSM/AON/PMA state are restored or reinitialized in the expected ownership domain.
