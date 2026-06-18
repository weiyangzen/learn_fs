# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 106431-108926

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 2,010 `#define` entries across 2,496 source lines: 1,006 `__SHIFT` constants, 1,004 `_MASK` constants, and 478 register comment markers. There are no C functions, structs, enums, global objects, locks, allocations, or executable statements in this range.

The range starts inside the raw common-memory table for the `DWC_E12MP_PHY_X4_NS_X4_2` PCIe PHY instance at `RAWCMNX_DIG_MEM_CMN5_B6_R6`, continues through raw common-memory banks up to `CMN6_B6_R31`, then covers common and lane raw digital control for the same `X4_2` PHY lane namespace. It also covers the `KPFIFO2` and `KPNP_SNPS2` LCU/KPNP register blocks, then begins the next `DWC_E12MP_PHY_X4_NS_X4_3` PHY instance with supervisor digital PLL/reference-clock fields and the first supervisor analog MPLLA fields. The source boundary is artificial: the previous chunk is needed for the comment marker and prior words of `CMN5_B6_R6`, and the next chunk is needed for the remaining `SUP_ANA_MPLLA_ATB1` fields and later analog definitions.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of AMD's generated NBIO 6.1 hardware register interface. Each generated field exposes:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to compose or decode that field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update that field.

The companion `nbio_6_1_offset.h` supplies matching register offsets, and `nbio_6_1_default.h` supplies reset/default values for many matching register names. AMDGPU runtime code combines these constants with register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15, SMN, and PCIe accessors when programming NBIO, PCIe PHY, link-management, reset, virtualization, and diagnostics paths.

This chunk specifically documents bit layouts for low-level PCIe PHY common memory, raw lane PCS/PMA/FSM/AON/IRQ control, link controller FIFO and KPNP lane request/reset blocks, and shared supervisor PLL/reference-clock controls. These definitions are hardware metadata; they are not filesystem or Ceph logic despite the mirror path under `ceph-client`.

## Important Macro Families

The first 281 register markers are `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_*` common-memory words. They run from the tail of `CMN5_B6_R6` through `CMN5_B7_R31`, all of `CMN6_B0` through `CMN6_B5`, and `CMN6_B6_R0` through `CMN6_B6_R31`. Every one has a single `DATA` field at shift `0x0` with mask `0xFFFFL`. These are opaque 16-bit PHY common-memory payload words rather than named semantic subfields.

The `X4_2_RAWCMNX_DIG_*` common digital registers after the memory block define shared raw common controls:

- `CMN_CTL` exposes common disable/powerdown-style control bits.
- `MPLLA_BW_OVRD_IN`, `MPLLA_SSC_CTL_OVRD_IN`, and `MPLLA_SSC_EN_OVRD_IN` define MPLLA bandwidth and spread-spectrum override fields.
- `MPLLB_BW_OVRD_IN`, `MPLLB_SSC_CTL_OVRD_IN`, and `MPLLB_SSC_EN_OVRD_IN` mirror the same controls for MPLLB.

The `X4_2_RAWLANEX_DIG_PCS_XF_*` lane PCS cross-function registers cover transmit and receive handoff fields between PCS-facing logic and raw lane control. Important groups include TX override/input/output fields, RX override inputs, RX PCS input fields, RX PCS/override outputs, RX adaptation acknowledge and figure-of-merit registers, TX pre/main/post direction feedback, and lane-number reporting.

The `X4_2_RAWLANEX_DIG_FSM_*` lane FSM registers define override controls, memory address/status monitors, fast-path controls for RX startup/adaptation/AFE/DFE/bypass/reference-level/IQ calibration, supervisor fast controls, TX common-mode and RX-detect shortcuts, RX power-up/VCO wait/VCO calibration shortcuts, and common-calibration status fields. These macros describe the bit layout for steering or observing lane microsequencing, but the required ordering and polling behavior live in hardware documentation and call sites.

The `X4_2_RAWLANEX_DIG_AON_*` always-on lane registers cover calibration trim storage and live adaptation results. They include AFE attenuator/CTLE/VGA IDAC offsets, DFE summer/phase/data/bypass/error VDAC offsets for even and odd paths, RX phase-adjust linear/map registers, IQ phase adjustment, MPLLA/MPLLB coarse tune captures, RX and TX RTUNE values, initial power-up done status, adapted ATT/VGA/CTLE/DFE tap values, adaptation done state, fast flags, slicer controls, lane common-calibration status, and `ADPT_CTL_0` through `ADPT_CTL_7`.

The `X4_2_RAWLANEX_DIG_IRQ_CTL_*` registers define lane interrupt state, clear, and mask bits for reset-return request, RX reset/request/rate/power-state events, RX adaptation request, and RX adaptation disable events. The clear-register names indicate acknowledgment side effects even though this header only provides masks.

The `X4_2_RAWLANEX_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` groups define PMA handoff and lane control fields: lane/supervisor override inputs and outputs, TX/RX PMA input and override output fields, lane RTUNE control, TX FSM and clock controls, RX FSM control, LOS mask control, RX data-enable override control, and continuous off-cancellation/adaptation status.

The `KPFIFO2_*` address block covers `KPFIFO2_PRI_TX_FIFO_HSCID`, per-lane `KPFIFO2_PRI_TX_FIFO_CONTROL_LANE_0` through `_3`, and `KPFIFO2_PCS_PMA_SOFT_RESET`. These fields describe primary TX FIFO HSC ID selection/control, per-lane FIFO behavior, and PCS/PMA soft reset layout for the second KPFIFO block.

The `KPNP_SNPS2_*` address block covers KPNP hardware/version and PHY-info registers, lane ID, lane request control/status, PMA control registers, PHY and lane soft reset registers, and reset control. These macros define the bit layout for lane request/acknowledge/status and PHY/PMA reset or control handshakes around the Synopsys KPNP interface.

The `X4_3_SUP_DIG_*` supervisor digital block starts a new PHY instance. It includes ID code registers, reference-clock override input, MPLLA B-div clock override, MPLLA/MPLLB override inputs, supervisor and level override fields, MPLLA/MPLLB ASIC input fields, ASIC input/level ASIC input registers, analog override outputs for MPLLA/MPLLB/RTUNE/RX termination, analog status, MPLLA/MPLLB power-control calibration/override/status/timing/coarse-tune registers, and spread-spectrum clocking phase/frequency fields.

The final supervisor analog entries start `X4_3_SUP_ANA_MPLLA_*`: `MISC`, `OVRD`, and the first two shift definitions for `ATB1`. They describe MPLLA analog miscellaneous bits, analog override enable/calibration/feedback-clock/reset bits, and the beginning of analog test-bus or regulator override field layout.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. Consumers depend on exact register names, field names, shifts, and masks remaining synchronized with AMD's generated NBIO 6.1 register database, sibling offset/default headers, and the actual GPU hardware.

The constants are untyped preprocessor integer literals, usually with an `L` suffix on masks. They encode bit placement only. They do not encode access width, reset value, read/write permission, volatility, write-one-to-clear behavior, sequencing rules, firmware ownership, lane ownership, or side effects. Call sites and hardware programming guides must supply those semantics.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU NBIO, PCIe, power-management, virtualization, or diagnostics code selects a register offset from `nbio_6_1_offset.h` or an SMN/PCIe access path.
2. The code reads a hardware register and decodes fields using this header's masks and shifts, or composes an updated value while preserving unrelated bits.
3. The decoded or updated value participates in PHY common-memory programming, lane bring-up, link training, reset handling, interrupt acknowledgment, PLL/SSC programming, RTUNE handshakes, adaptation/calibration, SR-IOV policy, or debug collection.

Likely flows represented by this chunk include loading or validating opaque common PHY memory words, lane PCS/PMA handoff during PCIe link training, lane FSM fast-start and calibration paths, RX adaptation result capture, lane-local interrupt clear/mask handling, KPFIFO/KPNP lane request and reset sequencing, shared reference-clock and MPLL setup for the next x4 PHY instance, and analog MPLLA override or measurement flows.

## State And Persistence Behavior

The header itself stores no state. It names state held in NBIO 6.1 PCIe PHY, LCU/KPFIFO, and KPNP hardware registers. Persistence is determined by GPU reset domains, PHY soft reset, PCIe link reset, suspend/resume restore paths, firmware or SMU initialization, PF/VF ownership in SR-IOV, and explicit driver writes.

Represented state includes opaque common-memory data words, common MPLL bandwidth and SSC override settings, PCS TX/RX override and handshake state, RX adaptation acknowledge/FOM data, lane FSM command and monitor state, always-on analog calibration offsets, DFE/AFE adaptation results, RTUNE values, lane interrupt status/clear/mask bits, PMA cross-function override state, TX/RX FSM and clock controls, KPFIFO per-lane FIFO controls, KPNP lane request/status/reset controls, shared PHY ID and reference-clock selection, MPLLA/MPLLB override and ASIC input state, supervisor reset/RTUNE/level controls, analog status, MPLL calibration/power/timing status, SSC phase/frequency values, and MPLLA analog override/test fields.

Several fields are active controls rather than passive storage. Reset, powerdown, FIFO control, lane request, interrupt clear, FSM override, fast calibration, reference-clock, PLL, SSC, RTUNE, and analog override bits can affect live PCIe link availability or signal integrity. Status fields may be transient or latched. Opaque `DATA` common-memory words may be part of a generated PHY configuration image and should be treated as hardware-table contents.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 6.1 register data and must stay aligned with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` for matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` for reset/default values, especially the raw common-memory words and PHY supervisor defaults.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` where SMN-addressed access is used.
- AMDGPU register helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, plus SOC15/PCIe/SMN read-write helpers in the driver.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega power-management include bundles such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. The surrounding AMDGPU stack integrates these generated definitions with NBIO initialization, PCIe link and ASPM/LTR behavior, GPU reset, clock gating, SR-IOV/mxGPU mailbox support, power management, and hardware diagnostics.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing the driver to program or decode the wrong hardware bit. In this chunk that is most dangerous for common-memory `DATA` words, reset, lane request, KPFIFO controls, interrupt clear/mask fields, PLL/reference-clock/SSC controls, RTUNE, and analog override fields.
- The chunk begins and ends inside real register families. Adjacent chunks are needed for complete context around `RAWCMNX_DIG_MEM_CMN5_B6_R6` and `SUP_ANA_MPLLA_ATB1`.
- The raw common-memory registers are highly repetitive and opaque. A single missing or renamed `DATA` macro may indicate generator drift, but manual review must account for the artificial line boundary.
- Lane PCS/PMA/FSM/AON definitions are hardware-sequencing sensitive. Incorrect values can break PCIe link training, leave a lane stuck in calibration, or make adaptation results invalid.
- Interrupt clear registers should not be treated as ordinary storage. Misusing clear masks can drop events or leave stale latched status asserted.
- KPNP lane request/reset fields can conflict with firmware, PF/VF ownership, or in-flight power/reset transitions if written without proper handshakes and timeouts.
- Shared `X4_3_SUP_DIG` PLL/reference-clock fields can affect all lanes on that x4 PHY instance, not only one lane under debug.
- Reserved masks are generated for layout completeness and read-modify-write preservation. Driver code should avoid intentionally setting reserved bits unless the hardware sequence explicitly requires it.

## Test Signals

- Build AMDGPU with NBIO 6.1/Vega support enabled. Direct macro users should catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: offset/default/shift/mask name alignment, mask-width checks, non-overlap checks inside registers, and repeated-lane/register-family checks.
- Verify that every `RAWCMNX_DIG_MEM_*` register in this chunk has exactly one `DATA` field at shift `0x0` and mask `0xFFFFL`, and that matching defaults exist in `nbio_6_1_default.h`.
- Compare `KPFIFO2_*` and `KPNP_SNPS2_*` masks with their offset/default entries and any hardware accessors that perform lane request, FIFO control, or soft reset sequences.
- On affected NBIO 6.1 GPUs, boot, suspend/resume, GPU reset, and runtime power-management tests should show stable PCIe link training, correct negotiated width/speed, no unexpected AER or link retraining storms, and no stuck PHY reset/request states.
- PHY diagnostics should decode lane FSM status, adaptation done/results, RTUNE values, interrupt status, KPNP lane status, MPLL calibration status, and PLL/SSC settings consistently with hardware behavior.
- SR-IOV/mxGPU smoke tests should verify that generated NBIO include users still build and that PF/VF mailbox, reset, and link-management paths remain unaffected.
