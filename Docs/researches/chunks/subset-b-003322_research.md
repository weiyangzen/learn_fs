# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 152375-154426

## Scope

This chunk is the tail of the generated AMD NBIO 7.7.0 shift/mask header. It contains 1,789 preprocessor definitions for register bit positions and masks, and it ends the file with the closing include guard. There is no executable C logic here; the public surface is the macro set consumed by AMDGPU register helpers.

The range starts at the final `BIF_CFG_DEV2_EPF0_1` PCIe lane-margining fields for lanes 11-15, then contains two complete address blocks:

- `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp`, exported as `BIF_CFG_DEV2_EPF1_1_*`.
- `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp`, exported as `BIF_CFG_DEV2_EPF2_1_*`.

Both EPF blocks are endpoint-function PCI/PCIe configuration-space layouts for device 2. The matching register offsets are in `nbio_7_7_0_offset.h`; this file supplies only `__SHIFT` and `_MASK` definitions for fields inside those registers.

## Purpose

The constants encode the hardware ABI for PCIe configuration fields on NBIO 7.7-class AMD GPUs. They let driver code use symbolic field names with helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD` instead of hard-coded bit arithmetic.

The chunk covers:

- End of `BIF_CFG_DEV2_EPF0_1` per-lane margining controls/status for lanes 11-15, with receiver number, margin type, usage model, and margin payload fields.
- Standard PCI header fields for EPF1 and EPF2: vendor/device ID, command/status, revision/class, cache line, latency, header/BIST, BAR1-BAR6, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCI power-management fields: PM capability headers, `PMI_CAP`, `PMI_STATUS_CNTL`, SBRN, FLADJ, and DBESL/DBESLD fields.
- Base PCIe capability fields: device/link capability, control, status, and second-generation capability/control/status registers for completion timeout, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, FLR, link disable/retrain/common clock, ASPM, negotiated speed/width, 8 GT/s equalization, DRS, and crosslink/downstream-presence status.
- MSI and MSI-X fields: capability headers, MSI enable/count/64-bit/per-vector masking/extended data bits, message address/data, masks, pending bits, MSI-X table/PBA selectors, function mask, and MSI-X enable.
- PCIe extended capabilities: vendor-specific, AER, resizable/enhanced BAR capability/control, power budget, dynamic power allocation, ACS, PASID, and ARI.
- The final `#endif` for the header guard.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this chunk. The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` is the right-shift count for a field.
- `<REGISTER>__<FIELD>_MASK` is the unshifted bit mask for a field.
- Comment anchors such as `//BIF_CFG_DEV2_EPF2_1_DEVICE_CNTL2` group fields belonging to a single register.
- `addressBlock:` comments identify generated register blocks and prevent confusion at EPF boundaries.

The most important register groups in this chunk are:

- `BIF_CFG_DEV2_EPF0_1_LANE_[11-15]_MARGINING_LANE_CNTL` and `_STATUS`: lane-level margining request/status fields. These are the continuation of earlier EPF0 lane margining definitions and retain the same 3-bit receiver number, 3-bit margin type, 1-bit usage model, and 8-bit payload layout.
- `BIF_CFG_DEV2_EPF1_1_COMMAND` / `BIF_CFG_DEV2_EPF2_1_COMMAND`: standard PCI command bits for I/O, memory, bus mastering, parity/SERR, fast back-to-back, and interrupt disable.
- `STATUS`, `DEVICE_STATUS`, `LINK_STATUS`, `LINK_STATUS2`, and `DEVICE_STATUS2`: status decode surfaces for PCI/PCIe readiness, error, link, transaction, equalization, DRS, and reserved status fields.
- `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_CAP2`, and `DEVICE_CNTL2`: payload/read-request sizing, error-reporting enables, relaxed ordering, no-snoop, aux power PM, phantom/extended tags, FLR, completion timeout, atomic operations, ID-based ordering, LTR, OBFF, emergency power reduction, and TLP-prefix controls.
- `LINK_CAP`, `LINK_CNTL`, `LINK_CAP2`, and `LINK_CNTL2`: supported/current link speed, link width, ASPM/PM support, link retrain/disable, common clock, hardware autonomous speed/width disable, compliance controls, and 8 GT/s training controls.
- `MSI_*` and `MSIX_*`: interrupt capability fields, including MSI 32/64-bit layout variants, per-vector masking and pending state, and MSI-X table/PBA BAR indicators and offsets.
- `PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY`: AER uncorrectable error fields for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receive overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable, multicast blocked TLP, AtomicOp egress blocked, TLP-prefix blocked, and poisoned-TLP egress blocked.
- `PCIE_CORR_ERR_STATUS` and `_MASK`: correctable error fields for receiver error, bad TLP/DLLP, replay rollover/timer timeout, advisory non-fatal, internal correctable, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0-3`, and `PCIE_TLP_PREFIX_LOG0-3`: AER capability/control and captured fault context logs.
- `PCIE_BAR[1-6]_CAP` and `_CNTL`: per-BAR supported-size and control fields, including BAR index, total number, active size, and upper supported size bits.
- `PCIE_PWR_BUDGET_*` and `PCIE_DPA_*`: power budget capability/data and dynamic power allocation capability/status/control/substate allocation fields.
- `PCIE_ACS_*`, `PCIE_PASID_*`, and `PCIE_ARI_*`: virtualization, isolation, address-space, and function-routing control/capability fields.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time substitution:

1. `amdgpu/nbio_v7_7.c` includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. Driver code selects a register offset from the offset header and a field from this mask header.
3. Register helper macros such as `REG_GET_FIELD(value, REGISTER, FIELD)` and `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` expand to shifts and masks using the exact macro names exported here.
4. Actual hardware access happens elsewhere through AMDGPU SOC15, PCIe-port, or NBIO register accessors.

For this specific chunk, the fields are mostly PCIe configuration-space capabilities and status/control surfaces. The current NBIO 7.7 C file directly uses this header for NBIO register bitfields in general; these EPF1/EPF2 PCIe config fields may be used by diagnostics, reset/power-management paths, virtualization support, AER handling, or future feature code rather than common doorbell setup paths.

## State And Persistence Behavior

The macros are stateless compile-time constants. The hardware fields they describe fall into several state classes:

- Identity and descriptor state: vendor/device IDs, class/revision values, capability IDs, capability versions, next pointers, BAR capability descriptors, link/device capability fields, ACS/PASID/ARI capabilities, power-budget data, DPA capability, and vendor-specific headers.
- Driver/firmware-programmed controls: PCI command bits, BAR size/control fields, device control error enables and payload sizing, FLR initiation, link retrain/disable/common-clock/ASPM settings, MSI/MSI-X enable/mask/table selectors, ACS/PASID/ARI enables, power-management control, DPA substate control, and AER masks/severity bits.
- Latched or event status: PCI status, device and link status, AER correctable/uncorrectable status, MSI pending bits, DPA substate status, 8 GT/s equalization status, DRS messages, and lane-margining status.
- Fault logs: AER header logs and TLP-prefix logs hold captured error context until cleared, overwritten, or reset according to hardware behavior.

Persistence across suspend/resume, GPU reset, FLR, PCIe hot reset, or power state changes is not defined in this header. It depends on the register class and the save/restore behavior in surrounding AMDGPU and platform PCIe code.

## Dependencies And Integration Points

This chunk depends on the AMD generated register-header convention under `drivers/gpu/drm/amd/include/asic_reg`. It is tightly coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which provides matching register offsets and base-index constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both the offset and mask headers for NBIO 7.7 ASIC support.
- AMDGPU register helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, which rely on exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` spelling.
- AMDGPU low-level accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`, which perform the actual reads/writes after code selects the register offsets.
- PCI/PCIe architectural semantics for PM, PCIe capability, MSI/MSI-X, AER, BARs, power budget, DPA, ACS, PASID, and ARI.

The two `addressBlock` transitions are important integration points. EPF1 starts at line 152468 and EPF2 starts at line 153447. The field layouts are highly repetitive, but their register stems must remain distinct so consumers combine EPF1 masks with EPF1 offsets and EPF2 masks with EPF2 offsets.

## Risks

- Bitfield drift is high impact. If a mask or shift differs from the hardware register database, callers can read the wrong status, clear or mask the wrong AER bit, misprogram BAR sizing, or enable the wrong PCIe feature.
- The EPF1 and EPF2 blocks are nearly parallel. Prefix mixups are easy to miss in review and can direct code at the wrong endpoint function even when the field layout looks identical.
- AER status, mask, and severity groups use similar names but have different behavior. Confusing them can suppress errors, misclassify severity, or falsely report hardware faults.
- Some fields represent write-one-to-clear or latched hardware status in PCIe configuration space. Generic read-modify-write code must preserve unrelated status bits and follow the hardware access rules; this header only gives masks and shifts.
- Interrupt fields are layout-sensitive. MSI 32-bit, MSI 64-bit, extended data, per-vector mask, pending bits, and MSI-X table/PBA fields are adjacent and similarly named, so using the wrong variant can break interrupt delivery.
- ACS, PASID, and ARI fields affect isolation, address-space tagging, and function routing. Misprogramming them can create virtualization/security isolation issues or device enumeration failures.
- BAR capability/control fields encode packed size and index metadata. Wrong masks can corrupt resource sizing and MMIO aperture setup.
- The chunk starts mid-EPF0 lane-margining sequence with one carried-over lane-10 status macro before lane 11. Any merged whole-file report must reconcile this chunk with the previous chunk to describe the complete lane 0-15 margining block.

## Test Signals

Useful validation signals are mostly build, generated-header, and hardware integration checks:

- Compile AMDGPU with NBIO 7.7 support and ensure `nbio_v7_7.c` and any other NBIO 7.7 consumers resolve all generated mask symbols.
- Compare this chunk against AMD's authoritative NBIO 7.7 register-generation source, especially the EPF0-to-EPF1 and EPF1-to-EPF2 boundaries and the repeated AER/BAR/DPA/ACS/PASID/ARI blocks.
- Cross-check every register stem in this mask header against `nbio_7_7_0_offset.h` so field masks are paired with matching offsets.
- Use PCIe config-space dumps from NBIO 7.7 hardware to validate vendor/device/class IDs, command/status bits, PM capability traversal, PCIe capability fields, MSI/MSI-X layout, AER capability, BAR capability/control fields, power budget, DPA, ACS, PASID, and ARI.
- Exercise interrupt setup and teardown paths and verify MSI/MSI-X enable, table/PBA, mask, and pending fields decode as expected.
- Run AER/error-injection or fault-observation tests to verify uncorrectable/correctable status, mask, severity, header log, and TLP-prefix log fields.
- Test reset, FLR, suspend/resume, and GPU recovery paths while checking command, device control, link control, BAR, MSI/MSI-X, ACS/PASID/ARI, and power-management fields for expected defaults or restoration.
- For lane-margining fields, compare per-lane margining control/status decoding against PCIe link diagnostics and ensure lanes 11-15 align with the preceding lane definitions.
