# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 148449-150912

## Scope

This chunk is a generated AMD NBIO 7.2.0 register field mask header section. It does not implement executable logic; it defines `__SHIFT` and `_MASK` constants for extracting and composing fields in PCIe configuration-space registers exposed through the NBIO register access layer. The assigned range starts near the tail of `BIF_CFG_DEV2_EPF0_1` endpoint-function 0 extended capability fields and then enters the `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp` address block for `BIF_CFG_DEV2_EPF1_1`, covering the beginning of endpoint-function 1 PCI configuration and its early extended capabilities through TPH steering-table entry 13.

The matching register addresses and `BASE_IDX` values live in `nbio_7_2_0_offset.h`; this header supplies only field positions and masks. `amdgpu/nbio_v7_2.c` includes both `nbio_7_2_0_offset.h` and this mask header, and driver code uses these symbols with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

## Purpose

The constants in this slice encode the hardware ABI for device 2, endpoint functions 0 and 1 behind NBIO 7.2.0. They allow AMDGPU code to address PCIe capability fields by symbolic names instead of literal bit numbers. The covered fields describe:

- PCIe virtual channel 1 resource control/status for `BIF_CFG_DEV2_EPF0_1`.
- Advanced Error Reporting (AER), header/TLP-prefix logs, BAR enhanced capability control, power budget, dynamic power allocation, PCIe secondary/link training, ACS, PASID, LTR, ARI, TPH, data-link feature, 16 GT/s PHY, and lane margining capability fields for `BIF_CFG_DEV2_EPF0_1`.
- The start of a new address block for `BIF_CFG_DEV2_EPF1_1`, including standard PCI configuration header fields, power-management capability, PCIe device/link capabilities and controls, MSI/MSI-X, vendor-specific extended capability, AER, BAR control, power budget, DPA, ACS, PASID, ARI, TPH requester capability/control, and TPH steering-table entries 0-13.

## Important APIs, Types, And Macros

There are no C types or functions in this chunk. The important exported interface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's right-shift value.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted mask used by AMDGPU bitfield helpers.
- Register comment anchors such as `//BIF_CFG_DEV2_EPF1_1_DEVICE_CNTL` group all field macros for one register.
- The companion offset header uses `reg<REGISTER>` and `reg<REGISTER>_BASE_IDX` for the MMIO/config address. Code combines those offset symbols with this file's field symbols by passing the shared register stem to `REG_SET_FIELD` or `REG_GET_FIELD`.

The chunk's most operationally important register groups are:

- `BIF_CFG_DEV2_EPF0_1_PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY`: AER uncorrectable error bits for DLP, surprise-down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, MC blocked TLP, AtomicOp egress block, TLP prefix block, and poisoned-TLP egress block.
- `BIF_CFG_DEV2_EPF0_1_PCIE_CORR_ERR_STATUS` and `_MASK`: correctable receive, bad TLP/DLLP, replay rollover/timer timeout, advisory non-fatal, internal correctable, and header-log-overflow bits.
- `BIF_CFG_DEV2_EPF0_1_PCIE_ADV_ERR_CAP_CNTL` plus `PCIE_HDR_LOG0-3` and `PCIE_TLP_PREFIX_LOG0-3`: AER first-error pointer, ECRC check, multi-header receive, TLP-prefix log presence, completion-timeout logging, and captured fault header/prefix dwords.
- `BIF_CFG_DEV2_EPF0_1_PCIE_BAR[1-6]_CAP` and `_CNTL`: per-BAR fixed-size/address-assignment controls and BAR disable/invalidate/reset controls.
- `BIF_CFG_DEV2_EPF0_1_PCIE_DPA_*`: dynamic power allocation capability, latency indicator, substate status/control, and eight substate power allocation entries.
- `BIF_CFG_DEV2_EPF0_1_PCIE_LANE_[0-15]_EQUALIZATION_CNTL`: per-lane downstream/upstream transmit presets and equalization state for the base PCIe capability.
- `BIF_CFG_DEV2_EPF0_1_PCIE_TPH_REQR_*` and `TPH_ST_TABLE_0-63`: TPH requester capability/control and steering table entries, each table register containing lower and upper 8-bit entries.
- `BIF_CFG_DEV2_EPF0_1_PCIE_PHY_16GT_*`, `LINK_STATUS_16GT`, and per-lane `EQUALIZATION_CNTL_16GT`: PCIe 16 GT/s enhanced capability and 16-lane preset/status fields.
- `BIF_CFG_DEV2_EPF0_1_MARGINING_*`: link margining port readiness plus per-lane control/status fields for receiver number, margin type, usage model, and payload.
- `BIF_CFG_DEV2_EPF1_1_COMMAND`, `STATUS`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`: the function 1 core PCIe control surface for memory/bus mastering, errors, payload/read request sizes, FLR, ASPM/link training, negotiated speed/width, completion timeout, atomic operations, ID-based ordering, LTR, 10-bit tags, OBFF, 8 GT/s equalization, and DRS/crosslink status.
- `BIF_CFG_DEV2_EPF1_1_MSI_*` and `MSIX_*`: MSI/MSI-X enable, vector count, 64-bit address/data, per-vector mask/pending, MSI-X table, and PBA fields.
- `BIF_CFG_DEV2_EPF1_1_PCIE_ACS_*`, `PASID_*`, `ARI_*`, and `TPH_REQR_*`: virtualization and routing capability controls for source validation, translation blocking, peer-to-peer redirect/egress, PASID enable/width, ARI function grouping, and TPH steering.

## Control Flow

This header has no runtime control flow. Its compile-time flow is indirect:

1. An NBIO implementation such as `amdgpu/nbio_v7_2.c` includes the offset and mask headers for the ASIC generation.
2. Driver code reads a register value with an NBIO/SOC15/PCIe-port accessor.
3. The value is decoded with `REG_GET_FIELD(value, REGISTER, FIELD)` or modified with `REG_SET_FIELD(value, REGISTER, FIELD, new_value)`.
4. The updated value is written back through the same access path.

For this specific chunk, the generated fields are primarily PCIe configuration-space fields rather than actively manipulated common-path doorbell or HDP fields. They are still part of the exported NBIO register contract and may be used by diagnostic, reset, power-management, SR-IOV/virtualization, or future PCIe feature code.

## State And Persistence Behavior

The macros themselves are stateless and persistent only as source definitions compiled into the driver. The hardware fields they describe represent several state classes:

- Latched or clear-on-write status: AER status bits, PCIe device/link status, data-link feature status, 8/16 GT/s equalization status, margining status, MSI pending bits, and DPA substate status reflect hardware events or negotiated state.
- Driver/firmware-programmed controls: command register memory and bus-master enables, device control error enables, payload and read-request size, FLR initiation, link control retrain/link-disable/common-clock/ASPM controls, MSI/MSI-X enables and masks, ACS/PASID/ARI/TPH controls, BAR reset/disable/invalidate controls, DPA control, and power budget selection.
- Descriptor or capability values: vendor/device/class IDs, PCIe capability and extended-capability headers, BAR capabilities, link/device capability registers, power budget data/capability, DPA capability, ACS/PASID/ARI/TPH capability fields, and VSEC headers.
- Log registers: AER header logs and TLP-prefix logs preserve captured fault context until cleared or overwritten by hardware policy.

Because the header only defines masks, it does not persist user data. Persistence across suspend/resume, reset, FLR, or GPU recovery depends on the hardware register class and on surrounding AMDGPU save/restore or initialization code.

## Dependencies And Integration Points

This generated file depends on the AMD register-header convention used across `drivers/gpu/drm/amd/include/asic_reg`. It is tightly coupled to:

- `nbio_7_2_0_offset.h`, which provides the `reg...` address constants for the same register stems.
- AMDGPU register helper macros in the driver include stack, especially `REG_SET_FIELD` and `REG_GET_FIELD`, which require the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` spelling used here.
- NBIO accessors in `amdgpu/nbio_v7_2.c`, where the ASIC-specific register map is selected for NBIO 7.2-class hardware.
- Linux PCIe semantics for AER, MSI/MSI-X, ACS, PASID, ARI, LTR, DPA, TPH, link equalization, link margining, and BAR capabilities. Even if Linux core PCI code owns many standard config flows, these NBIO symbols are the low-level device-specific mirror used by AMDGPU when it must inspect or program the GPU-side view.

The `addressBlock: nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp` marker is important for reconciliation with the offset header and hardware register generation source. It indicates that the following `BIF_CFG_DEV2_EPF1_1_*` macros belong to a separate endpoint-function block, not to the preceding `EPF0` block.

## Risks

- Bitfield drift from hardware documentation is high impact. A wrong `_MASK` or `__SHIFT` can silently enable the wrong PCIe feature, miss a real error bit, clear an unrelated latch, corrupt BAR/MSI programming, or misreport link capabilities.
- Several registers share one dword but expose different logical halves, such as vendor/device ID, command/status, MSI data variants, DPA status/control, ACS cap/control, PASID cap/control, ARI cap/control, and paired TPH steering entries. Callers must use the matching field width and not assume each comment anchor implies a separate 32-bit address.
- AER status/mask/severity names are very similar. Confusing status, mask, and severity macros would change error handling behavior rather than simply reading a status bit.
- Function-prefix mistakes are easy in this generated file. `BIF_CFG_DEV2_EPF0_1_*` and `BIF_CFG_DEV2_EPF1_1_*` often define equivalent fields with identical bit layouts but different register addresses. Using an `EPF0` mask with an `EPF1` register is usually harmless only when layouts match; it is still brittle and can fail when a field diverges.
- Capability table repetitions, especially `TPH_ST_TABLE_0-63`, lane equalization/margining controls, and DPA substate allocations, are prone to off-by-one generation or copy mistakes. The offset header shows paired TPH entries sharing addresses; masks here must match those packed lower/upper byte layouts.
- Some capability controls can affect virtualization/isolation (`ACS`, `PASID`, `ARI`), interrupt delivery (`MSI/MSI-X`), reset (`INITIATE_FLR`), and PCIe link training. Misprogramming them can cause security isolation gaps, lost interrupts, device disappearance, or link instability.

## Test Signals

Useful validation is mostly compile-time and hardware/PCIe integration oriented:

- Build coverage for AMDGPU with NBIO 7.2 enabled verifies that all macro names expected by `nbio_v7_2.c` and related code still resolve.
- Static comparison against the generator source or AMD register XML should verify each `_MASK` and `__SHIFT`, especially around block boundaries and repeated table/lane entries.
- Runtime PCIe sanity checks should confirm expected vendor/device/class IDs, command/status bits, link speed/width, MSI/MSI-X capability layout, and AER capability traversal for NBIO 7.2 devices.
- Error-injection or fault-log tests should validate that AER status, mask, severity, header log, and TLP-prefix log fields decode correctly.
- Resume, reset, and FLR testing should watch command, device control, link control, MSI/MSI-X, ACS/PASID/ARI, BAR, and DPA fields for correct restoration or expected hardware defaults.
- Link-training diagnostics should compare 8 GT/s and 16 GT/s equalization status, per-lane preset controls, and margining ready/status fields with observed PCIe link behavior.
