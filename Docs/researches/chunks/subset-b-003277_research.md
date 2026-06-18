# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 44043-46350

## Purpose

This chunk is an auto-generated AMD NBIO 7.7.0 shift/mask header slice. It contains no executable code; it publishes preprocessor constants that describe bit positions and bit masks for NBIO/BIF registers used by the AMDGPU driver. The matching register addresses live in `nbio_7_7_0_offset.h`; this file supplies the field-level contract consumed by register access macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15`.

The assigned range starts at the tail of `SMN_MST_CNTL1`, then covers endpoint SMN error-response controls, self-ring interrupt vector metadata, strap-write gating, INTx/D-state behavior, GMI request weighting, atomic/PASID/DMA error logging, urgent interrupt capability fields, virtual-wire change/reset/trigger controls, clock/light-sleep controls, SMN master controls, SDP response/credit fields, BIF reset controls, reset/FLR/D3/power interrupt status and masks, PF FLR trigger bits, D-state value fields, D3hot-to-D0 reset controls, and the beginning of `DEV1_PF1_FLR_RST_CTRL`.

## Public Surface In This Chunk

The public surface is 2,192 `#define` macros in the assigned range. Each field normally has a `__SHIFT` macro and a matching `_MASK` macro. The macro naming convention is:

- `<REGISTER>__<FIELD>__SHIFT` for the starting bit position.
- `<REGISTER>__<FIELD>_MASK` for the bit mask in the 32-bit register dword.

There are no functions, structs, enums, static variables, or inline helpers. The API contract is the exact macro spelling and numeric value. Consumers combine these constants with register-address macros from `nbio_7_7_0_offset.h` and AMDGPU's register helpers. A typical consumer pattern is to read a register, set or extract a named field through `REG_SET_FIELD` or `REG_GET_FIELD`, and write the updated dword back through the SOC15 or PCIe-port accessor selected by the offset macro.

## Register Coverage

The chunk covers these broad groups:

- SMN error-response and master controls: tail fields for `SMN_MST_CNTL1`, full `SMN_MST_EP_CNTL5`, `SMN_MST_CNTL0`, `SMN_MST_EP_CNTL1`, and `SMN_MST_EP_CNTL2`. These fields gate all-ones SMN error-response data behavior for upstream/downstream devices and endpoint PFs, configure retry/timeout/drop behavior, and expose endpoint-specific control bits.
- Self-ring and interrupt-vector controls: `BIF_SELFRING_BUFFER_VID`, `BIF_SELFRING_VECTOR_CNTL`, and `EP*_INTR_URGENT_CAP` describe client IDs and urgent interrupt mode fields for doorbell monitoring, RAS controller interrupts, ATHUB error-event interrupts, and endpoint functions.
- Strap, INTx, pending, and power-break controls: `NBIF_STRAP_WRITE_CTRL`, `NBIF_INTX_DSTATE_MISC_CNTL`, `NBIF_PENDING_MISC_CNTL`, and `NBIF_PWRBRK_REQUEST` control one-time strap writes, INTx deassertion/PMI behavior across D-states, FLR pending-check bypasses, and NBIF power-break request signaling.
- GMI arbitration and credits: `BIF_GMI_WRR_WEIGHT`, `BIF_GMI_WRR_WEIGHT2`, `BIF_GMI_WRR_WEIGHT3`, and multiple `BIFC_*_POOLCRED_ALLOC` registers define weighted round-robin mode/entry weights and HRP/GMI/SDP/SST response/data pool credit allocation fields.
- Error logging and clearing: repeated `BIF_ATOMIC_ERR_LOG_DEV*_F*` blocks report unsupported atomic conditions per device/function and provide clear bits; `BIF_DMA_MP4_ERR_LOG` reports MP4 SDP VC/non-DVM and atomic request errors; `BIF_PASID_ERR_LOG` and `BIF_PASID_ERR_CLR` track and clear PASID errors for DEV0 PF0-PF7, DEV1 PF0-PF1, and DEV2 PF0-PF6; `BIFC_BME_ERR_LOG_HB` records bus-master-enable error state and clear bits.
- Virtual-wire controls: `NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL`, `NBIF_SMN_VWR_VCHG_RST_CTRL0`, `NBIF_SMN_VWR_VCHG_TRIG`, `NBIF_SMN_VWR_WTRIG_CNTL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL_1`, their `_HI` variants, and the SDP virtual-wire registers define change-detect disable, reset, trigger, write-trigger, and high-word controls for SMN/SDP virtual-wire signaling.
- Clock and light-sleep controls: `NBIF_MGCG_CTRL_LCLK` and `NBIF_DS_CTRL_LCLK` expose LCLK medium-grain clock-gating and deep-sleep/light-sleep behavior fields for the NBIF side of the BIF block.
- BDF, hysteresis, wakeup, and performance counters: `DISCON_HYSTERESIS_HEAD_CTRL`, `BIFC_PCIE_BDF_CNTL0`, `BIFC_PCIE_BDF_CNTL1`, `BIFC_EARLY_WAKEUP_CNTL`, and `BIFC_PERF_CNT_*_H16BIT` publish fields for disconnect hysteresis, PCIe bus/device/function mapping, early wakeup, and high 16-bit read/write performance counter values.
- BIF reset register block: an explicit comment marks `addressBlock: nbio_nbif0_bif_rst_bif_rst_regblk`, followed by `HARD_RST_CTRL`, `SELF_SOFT_RST`, `SELF_SOFT_RST_2`, `BIF_GFX_DRV_VPU_RST`, `BIF_RST_MISC_CTRL`, `BIF_RST_MISC_CTRL2`, and `BIF_RST_MISC_CTRL3`.
- Function-level reset controls: `DEV0_PF0_FLR_RST_CTRL` through `DEV0_PF7_FLR_RST_CTRL`, `DEV1_PF0_FLR_RST_CTRL`, and the beginning of `DEV1_PF1_FLR_RST_CTRL` expose PF/VF config reset, private reset, sticky reset, soft-PF reset, VF-to-VF reset, FLR-twice, FLR grace, timeout, dummy-response status, and PF-copy private reset fields. The chunk ends before `DEV1_PF1_FLR_RST_CTRL` is complete.
- Interrupt status and masks: `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, `BIF_PF_DSTATE_INTR_STS`, and matching mask registers define per-device/per-function bits for instance reset, PF FLR, D3hot-to-D0, PME/power, port D-state, and PF D-state events.
- FLR triggers and D-state values: `BIF_PF_FLR_RST` provides trigger bits for DEV0 PF0-PF7, DEV1 PF0-PF1, and DEV2 PF0-PF6. `BIF_DEV0_PF0_DSTATE_VALUE` through `BIF_DEV0_PF7_DSTATE_VALUE` expose target D-state, D3-to-D0 reset-needed, and acknowledged D-state fields for DEV0 PFs.
- D3hot-to-D0 reset controls: `DEV0_PF0_D3HOTD0_RST_CTRL` through `DEV0_PF7_D3HOTD0_RST_CTRL` define PF config/private reset enable, FLR exception enable, and sticky reset behavior for D3hot-to-D0 transitions.

## Important Macro Patterns

Device/function repetition is the dominant pattern. DEV0 usually spans PF0-PF7, DEV1 commonly spans PF0-PF1 in this range, and DEV2 often spans PF0-PF6 or PF0-PF7 depending on register purpose. Fields are packed by function index: DEV0 PF bits occupy low bits, DEV1 PF bits often start around bit 8, and DEV2 PF bits often start around bit 16. That layout appears in PASID error logging, FLR status/masks, D3hot-to-D0 status/masks, D-state interrupt masks, PF FLR reset triggers, and SMN error-response endpoint controls.

The atomic error-log blocks are highly regular. Each `BIF_ATOMIC_ERR_LOG_DEVx_Fy` register has status fields for unsupported atomic opcode, requester-enable-low, length, and non-relaxed ordering cases in low bits, plus corresponding clear fields starting at bit 16. This is a write/clear sensitive pattern: readers can inspect low status bits, while writers use the high clear masks to acknowledge logged conditions.

Reset control registers split reset domains into configuration reset, private reset, sticky reset, soft-PF reset, VF reset, and FLR grace/dummy-response behavior. Some DEV0 PF FLR controls include the broader PF/VF/soft-PF field set; the D3hot-to-D0 reset controls are smaller and focus on PF config/private reset behavior. The chunk boundary matters because `DEV1_PF1_FLR_RST_CTRL` starts here but continues in the next chunk.

Virtual-wire registers appear in low and high halves. The `_HI` groups mirror the non-HI SMN virtual-wire change/trigger controls for upper signal ranges. Consumers must not infer that only the low register exists when handling VWR indices beyond the first 32-bit word.

`_MASK` macro names sometimes contain a doubled `_MASK_MASK` suffix when the field itself ends in `_MASK`, for example interrupt-mask field names. This is generated naming, not a typo. Code using `REG_SET_FIELD` must pass the register and field token names expected by AMDGPU's macros rather than trying to normalize these names manually.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. Driver code selects a register offset such as a BIF reset, interrupt-mask, clock-control, doorbell, or error-log register.
3. The driver uses generated mask/shift macros directly or through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`.
4. The hardware read/write sequence is performed by AMDGPU register accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, or `WREG32_PCIE_PORT`.

The header stores no software state and persists nothing by itself. State lives in NBIO hardware registers, PCIe configuration/control state, firmware-owned reset state, RAS/error-log latches, virtual-wire state machines, interrupt status latches, and power-management state. Many fields are control bits that persist until reset or reprogramming. Others are status bits, sticky error bits, write-one-to-clear bits, interrupt masks, reset request bits, or hardware-updated D-state acknowledgements. The generated header does not encode reset values, ownership rules, ordering constraints, timing requirements, or side effects beyond the bit positions and masks.

## Dependencies And Integration Points

The direct NBIO 7.7 implementation is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That file wires NBIO 7.7 into AMDGPU through `nbio_v7_7_funcs`, including callbacks for HDP flush offsets, PCIe index/data offsets, PCIe port index/data offsets, revision ID, memory-controller access, doorbell apertures, interrupt-handler doorbell ranges, interrupt control, clock gating, light sleep, initialization, HDP remapping, and register remap setup.

This exact chunk is mostly lower-level field inventory rather than fields heavily manipulated in `nbio_v7_7.c` today. It is nevertheless part of the same generated hardware ABI and is available to NBIO, PCIe, RAS, virtualization, reset, power-management, and debug code paths. It must remain synchronized with the companion offset header so `reg*` addresses and `<REGISTER>__<FIELD>` masks describe the same dword.

Semantic dependencies include AMD's NBIO 7.7.0 register database, the Linux DRM AMDGPU SOC15 register-access framework, PCI Express FLR and D-state behavior, SR-IOV/PF/VF reset isolation rules, PASID/IOMMU process-address-space semantics, PCIe atomic-operation handling, RAS/error reporting, MSI/interrupt routing, and AMD firmware or platform ownership of straps, virtual wires, and reset sequencing.

The adjacent generated NBIF/NBIO headers for other IP versions contain similar field names with different coverage. That similarity is useful for cross-checking generated consistency, but it is also a maintenance hazard: code must include the NBIO 7.7.0 header selected for the active ASIC and cannot blindly copy masks from another generation.

## Risks And Maintenance Notes

- This chunk begins and ends mid-topic. It starts with only the tail of `SMN_MST_CNTL1`, and it ends partway through `DEV1_PF1_FLR_RST_CTRL`. Adjacent chunks are required for complete documentation of those registers.
- Prefix mistakes are easy because many DEV/PF blocks differ only by a digit. A wrong DEV0/DEV1/DEV2 or PF number can compile cleanly while clearing, masking, or resetting the wrong hardware function.
- Error-log clear fields are side-effecting. Confusing low status masks with high clear masks can either fail to acknowledge an error or clear evidence before software has reported it.
- PASID error bits connect to process-address-space and IOMMU isolation behavior. Incorrect clear, mask, or interpretation logic can hide translation/security failures or misattribute faults to the wrong PF.
- FLR and D3hot-to-D0 controls are reset-critical. Misprogramming grace timeouts, sticky reset behavior, dummy responses, or PF/VF reset enables can break PCIe reset recovery, SR-IOV guests, host PF ownership, or firmware assumptions.
- Interrupt mask/status fields use generated names with `_MASK_MASK` forms where the field name is itself a mask. Handwritten field-name transformations can silently select nonexistent or wrong macros.
- Virtual-wire change/reset/trigger registers interact with firmware/platform sideband signaling. Drivers should avoid treating them as generic scratch controls.
- Clock-gating and light-sleep fields can affect link responsiveness and register accessibility. Changes need power-management validation, especially across suspend/resume and runtime power transitions.
- Generated masks must be kept in lockstep with the hardware register database. Hand edits to this file are high risk because the numeric constants are the contract.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for AMDGPU NBIO 7.7 include sites, especially `amdgpu/nbio_v7_7.c`, with warnings enabled for missing or misspelled macros.
- Generated-header diffing against AMD's authoritative NBIO 7.7.0 register database, with special attention to repeated DEV/PF blocks and the mid-chunk `DEV1_PF1_FLR_RST_CTRL` boundary.
- Cross-header checks that every register field in this chunk has the matching register offset in `nbio_7_7_0_offset.h` and that field masks do not overlap unexpectedly within a dword.
- Static checks for paired status/clear fields in `BIF_ATOMIC_ERR_LOG_*`, `BIF_DMA_MP4_ERR_LOG`, `BIF_PASID_ERR_LOG`, `BIF_PASID_ERR_CLR`, and `BIFC_BME_ERR_LOG_HB`.
- Hardware or simulator tests that inject PCIe atomic, PASID, DMA, BME, and RAS-related errors, confirm the expected log bit is set for the correct DEV/PF, and verify only the intended clear bit acknowledges it.
- FLR and reset validation for DEV0 PF0-PF7, DEV1 PF0-PF1, and DEV2 PFs, including interrupt status/mask behavior, `BIF_PF_FLR_RST` triggering, sticky reset behavior, and recovery after reset.
- SR-IOV guest/host tests that exercise PF and VF reset paths without cross-function state leakage.
- D-state and D3hot-to-D0 tests that confirm target/ack state fields, reset-needed indication, D-state interrupts, and D3hot-to-D0 reset controls behave through suspend/resume and runtime power management.
- Clock-gating/light-sleep validation that toggles `NBIF_MGCG_CTRL_LCLK` and `NBIF_DS_CTRL_LCLK` related behavior while checking register access, PCIe link stability, and wake latency.
- Interrupt-path tests for urgent interrupt capabilities, self-ring vector controls, PF FLR/D3/power/D-state masks, and RAS/ATHUB event routing.
