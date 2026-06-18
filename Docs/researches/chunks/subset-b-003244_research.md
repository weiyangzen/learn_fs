# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 43897-46474

## Scope

This chunk is part of AMDGPU's generated NBIO 7.4 register field mask header. It contains C preprocessor constants for bit shifts and masks, not executable functions. The companion NBIO 7.4 driver includes this file from `amdgpu/nbio_v7_4.c` together with `nbio_7_4_offset.h` and SMN address headers, then uses these definitions through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, and `WREG32_SOC15`.

The line range covers:

- PCIe performance counter control fields for TX, master/slave request/completion clocks, event port selection, and counter values.
- PCIe HIP address-translation aperture fields and PRBS link-test status/counter fields.
- Software reset command, reset-control, reset-enable, and endpoint reset fields.
- NBIO clock/power-management, SMN aperture, RSMU, link-near counter, interrupt sharing, and PCIe power-gating fields.
- Repeated SR-IOV per-VF field maps for VF0 through the beginning of VF7: per-VF MM index/data windows, RCC error/config/IOV fields, BIF BME/atomic/doorbell/HDP flush/mailbox fields, and MSI-X vector/PBA fields for VF0-VF6.

## Purpose

The purpose of this section is to give the driver exact bit layouts for NBIO 7.4 PCIe/NBIF registers. The header separates register address knowledge from field layout knowledge: address macros live in the matching `*_offset.h`/SMN headers, while this file supplies each register's `__FIELD__SHIFT` and `__FIELD_MASK` constants.

The constants let driver code update specific hardware fields without hard-coding bit positions at each call site. This is important for NBIO because the same register programming idioms are used across ASIC generations while field positions can drift. Examples from the NBIO 7.4 integration path include reading `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK` to report clock-gating state and using related masks when programming BIF clock/light-sleep behavior.

## Important APIs, Types, and Macro Families

This chunk defines macros only. The effective API surface is the naming convention consumed by AMDGPU register helpers:

- `REGISTER__FIELD__SHIFT`: bit offset used when extracting or inserting a field.
- `REGISTER__FIELD_MASK`: field mask at its final register position.
- Repeated per-VF register prefixes such as `BIF_BX_DEV0_EPF0_VF0_*` through `BIF_BX_DEV0_EPF0_VF7_*`, where the VF number selects a virtual-function register aperture.
- RCC-side per-VF prefixes such as `RCC_DEV0_EPF0_VF0_*` through `RCC_DEV0_EPF0_VF6_*` for VF error/config/MSI-X fields.

Major register groups in this chunk:

- `PCIE_PERF_COUNT_CNTL`, `PCIE_PERF_CNTL_*`, `PCIE_PERF_COUNT*_*`, `PCIE_PERF_CNTL_EVENT*_PORT_SEL`: global enable/reset/shadow controls, event selectors, counter-upper fields, 32-bit counter values, and performance-event port routing.
- `PCIE_HIP_REG0` through `PCIE_HIP_REG8`: HIP aperture base/limit/enable/PASID/ReqAT/ReqIO configuration fields for two address-translation windows plus a HIP mask register.
- `PCIE_PRBS_*`: PRBS clear/polarity, lock/error status, bit-count completion, freerun mode, generator/checker controls, user pattern, bit counters, and per-lane error counters 0-15.
- `SWRST_COMMAND_STATUS`, `SWRST_GENERAL_CONTROL`, `SWRST_COMMAND_0/1`, `SWRST_CONTROL_0` through `SWRST_CONTROL_6`, `SWRST_EP_COMMAND_0`, `SWRST_EP_CONTROL_0`: NBIO software reset status, policy, command bits, reset cause enables, atomic reset enables, write-reset enables, lane-training holds, and endpoint reset controls.
- `CPM_CONTROL`, `PCIE_PGMST_CNTL`, `PCIE_PGSLV_CNTL`: BIF clock and power management controls including LCLK/TXCLK/refclk gating, L1/L1.1/L1.2 power gates, idleness indicators, early wake, and power-gate hysteresis.
- `SMN_APERTURE_ID_A/B`, `RSMU_*`, `SMU_PCIE_DF_Address`: SMN aperture IDs, RSMU message/invalid-access/power-gating/timer fields, and an SMU-visible Data Fabric RAS interrupt-control address field.
- `LNCNT_*`, `LNC_*_WACC_REGISTER`: link-near counter enable, quantization, weighting, and accumulated total/BW/common counters.
- `SMU_INT_PIN_SHARING_PORT_INDICATOR`: packed link-management, LTR, and DPC interrupt status per port.
- `BIF_BX_DEV0_EPF0_VF*_MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`: per-VF indirect MMIO index/data windows.
- `RCC_DEV0_EPF0_VF*_RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, `RCC_IOV_FUNC_IDENTIFIER`: per-VF invalid SR-IOV access logging, doorbell aperture enable, config sizing/reserved values, and IOV function identity/enable fields.
- `BIF_BX_DEV0_EPF0_VF*_BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, `DOORBELL_SELFRING_GPA_APER_*`, `HDP_*_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ/DONE`, `BIF_TRANS_PENDING`, `NBIF_GFX_ADDR_LUT_BYPASS`: per-VF bus-master, atomic-error, doorbell self-ring, HDP coherency flush, transaction-pending, and address-LUT bypass fields.
- `BIF_BX_DEV0_EPF0_VF*_MAILBOX_*`, `BIF_VMHV_MAILBOX`, `MAILBOX_INT_CNTL`: per-VF VM/HV transmit/receive message buffers, valid/ack handshake bits, compact VMHV mailbox data/valid/ack bits, and mailbox interrupt enables.
- `RCC_DEV0_EPF0_VF*_GFXMSIX_*`, `GFXMSIX_PBA`: per-VF MSI-X vector address/data/control fields and pending-bit-array fields for three graphics MSI-X vectors.

## Control Flow and Data Flow

There is no runtime control flow in this header. Runtime behavior emerges when the driver combines these masks with register access helpers:

- A driver reads a 32-bit register value from the PCIe, SMN, SOC15, or MMIO aperture.
- It extracts fields with masks/shifts or updates fields through AMDGPU helper macros.
- It writes the modified value back to the same hardware register.

For this chunk's most directly visible integration, `amdgpu/nbio_v7_4.c` includes the header and reads `smnCPM_CONTROL`; if `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK` is set, it reports `AMD_CG_SUPPORT_BIF_MGCG` in the clock-gating state. The same field family is used by nearby NBIO generations to enable/disable BIF clock gating with read-modify-write sequences. That makes the mask values part of the power-management control path even though this file itself is generated metadata.

The per-VF groups describe repeated hardware windows. Data flow is expected to be indexed by VF-specific addresses from the companion address header, with these masks applied to each VF's register contents. The register names indicate separate state paths for:

- Host/guest mailbox data transfer and acknowledgement.
- Doorbell aperture base/size/mode programming.
- HDP coherency flush request/done handshakes for CP0-CP9 and SDMA0-SDMA1.
- Error-status capture and clear-on-write style fields for BME and unsupported atomic operations.
- MSI-X vector routing and masking.

## State and Persistence Behavior

The macros are compile-time constants and hold no state. The state they describe lives in hardware registers and is generally volatile across device reset, suspend/resume, GPU reset, VF reset, PCIe link reset, power gating, or firmware reinitialization.

Important state classes represented by this chunk:

- Counter state: PCIe performance counters, PRBS bit/error counters, and LNC accumulated counters are hardware-maintained values. Some are sampled via shadow writes or global count controls.
- Sticky/status state: reset completion/wait-state bits, invalid SR-IOV access logs, BME-low and atomic error logs, transaction-pending bits, PRBS lock/error status, and MSI-X pending bits reflect hardware events and often require explicit clear bits or reset sequences.
- Configuration state: clock gating, power gating, reset enable masks, doorbell aperture configuration, self-ring GPA aperture base/size, mailbox interrupt enables, HIP apertures, RSMU invalid-access behavior, and IOV enable/function identity persist only as long as the register block retains context.
- Per-VF state: VF0-VF7 fields isolate virtual function control/status surfaces so SR-IOV guest-visible behavior can be programmed and diagnosed independently.

Because this file only defines bit positions, persistence correctness depends on call sites preserving unrelated bits during read-modify-write operations and replaying necessary programming after reset paths.

## Dependencies and Integration Points

Direct dependencies are implicit:

- C preprocessor inclusion from AMDGPU NBIO code.
- Companion register address headers, especially `nbio_7_4_offset.h` and `nbio_7_4_0_smn.h`.
- AMDGPU register helper macros that expect the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- Hardware/firmware documentation or generated register database that produced the values.

Runtime integration points in the driver tree include:

- NBIO v7.4 setup and query code in `amdgpu/nbio_v7_4.c`, especially clock-gating state and NBIO register access setup.
- Common AMDGPU PCIe performance counter code paths in older/generic ASIC files, which use identically named `PCIE_PERF_*` fields to program events and read counter overflow bits.
- Doorbell and HDP flush setup paths that program base/size registers and use request/done masks to synchronize CP/SDMA memory coherency.
- SR-IOV virtualization paths that need VF-specific RCC/BIF register layouts for guest-visible errors, doorbells, mailbox handshakes, and MSI-X programming.
- RAS/SMU-related paths that may use SMU interrupt address/status fields and RSMU behavior controls.

## Risks and Edge Cases

- Generated-header drift: if the hardware register database changes but this header does not, `REG_SET_FIELD` can silently program the wrong bits. These failures often appear as device hangs, failed link training, missing interrupts, or broken SR-IOV VF behavior rather than compile errors.
- Name collision across ASIC generations: many field names such as `CPM_CONTROL__*`, `PCIE_PERF_*`, and `SWRST_*` exist in multiple headers. Including the wrong generation-specific header or mixing address macros from another generation can compile but target incompatible layouts.
- Partial VF coverage in this chunk: VF0-VF6 include MSI-X blocks in this range, while VF7 begins and continues beyond the chunk. Reconciliation must merge adjacent chunks before producing per-file conclusions about complete VF7 coverage.
- Status versus clear bits: registers such as BME/atomic error logs expose both status and `CLEAR_*` fields. Incorrect read-modify-write logic can clear diagnostics prematurely or fail to clear sticky errors.
- Reset and power-gating hazards: `SWRST_*` and `CPM_CONTROL` fields affect link state, clock domains, and power gates. Bad masks can strand the device in reset, gate clocks while active transactions are pending, or misreport clock-gating state.
- Counter sampling hazards: performance and PRBS counters use enable/reset/shadow/upper-counter fields. Reads without the expected shadowing or reset sequence can report inconsistent diagnostics.
- SR-IOV isolation risk: per-VF mailbox, MSI-X, doorbell, and invalid-access fields are security-sensitive. A wrong VF prefix/address pairing can cross wires between virtual functions.

## Test and Validation Signals

Useful validation is mostly integration and hardware focused:

- Build signal: compile AMDGPU with NBIO 7.4 support and ensure all `REG_SET_FIELD`/`REG_GET_FIELD` references resolve with this header and the matching address headers.
- Boot/probe signal: NBIO v7.4 ASICs should probe without PCIe, doorbell, interrupt, or RAS initialization failures.
- Clock-gating signal: reading clock-gating state should accurately reflect `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK`; toggling BIF clock/light-sleep features should not produce hangs or link errors.
- PCIe diagnostics signal: perf counter paths should produce sane counts and counter-overflow fields; PRBS status should show lock/error behavior expected by link-test procedures.
- Reset signal: software reset and endpoint reset sequences should set completion/wait-state/status bits as expected and recover link/device operation.
- Doorbell/HDP signal: doorbell aperture programming should deliver interrupts/work submissions correctly, and HDP flush request/done handshakes should complete for CP and SDMA engines.
- SR-IOV signal: VF0-VF7 guest operation should preserve per-VF isolation, mailbox valid/ack handshakes, MSI-X delivery/masking, invalid-access logging, and BME/atomic error reporting.
- Static review signal: verify every mask is a shifted version of its documented field width, masks do not unintentionally overlap within a register unless fields are aliases/status-vs-command pairs, and per-VF repeated blocks remain structurally identical except for VF number and chunk boundary truncation.
