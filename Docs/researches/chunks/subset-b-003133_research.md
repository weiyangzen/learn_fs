# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 27117-29591

## Scope

This chunk covers a generated AMD NBIO 7.11.0 register shift/mask slice for NBIF PCIe configuration fields. It starts mid-register at `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP`, continues through the tail of the `DEV0_EPF0` PCIe extended capability space, then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and defines most of the `DEV0_EPF1` PCI/PCIe configuration-space field layout through the beginning of 16 GT/s lane equalization. The range contains 2,103 `#define` entries and 370 generated register/comment records.

The file section is data only. It exports preprocessor constants for field bit positions and masks; it has no C functions, structs, runtime variables, allocation, locking, persistence code, or executable control flow.

## Purpose

The chunk supplies the bit-level ABI between AMDGPU NBIO 7.11 code and PCIe/NBIF hardware registers. Each generated field follows the normal AMD register-header convention:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the raw mask used to isolate, clear, or compose that field.

Consumers combine these constants with matching register offsets from `nbio_7_11_0_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`. The macros in this slice describe PCIe endpoint function configuration spaces, capability records, error-reporting state, link-training controls, I/O virtualization capabilities, and GPU I/O virtualization/vendor-specific records.

## Important Macro Families

### DEV0 EPF0 Extended Capability Tail

The first part of the chunk finishes the `BIF_CFG_DEV0_EPF0_0` enhanced capability area. It starts after the `PCIE_BAR1_CAP__BAR_SIZE_SUPPORTED__SHIFT` definition from the previous chunk, so this range owns only the BAR1 mask plus the following BAR control fields. The BAR and VF resizable-BAR groups expose supported BAR sizes, BAR index, total BAR count, active size, and upper supported-size bits for BAR1 through BAR6.

Power and latency capability groups include Power Budgeting, Dynamic Power Allocation, Latency Tolerance Reporting, and L1-related endpoint capability fields. DPA fields cover substate maximums, transition latency unit/value fields, power allocation scale, selected substate status/control, and per-substate power allocations. LTR fields expose snoop and non-snoop latency values and scales.

The secondary PCIe capability group defines `PCIE_LINK_CNTL3`, lane error status, and per-lane 8 GT/s equalization controls for lanes 0 through 15. Each lane has downstream/upstream TX preset fields and RX preset-hint fields. The later 16 GT/s capability block adds link status, parity mismatch status, and per-lane 16 GT/s DSP/USP TX preset controls.

Isolation, address translation, and virtualization capability groups include ACS, ATS, Page Request Interface, PASID, ARI, SR-IOV, multicast, data link feature exchange, lane margining, VF resizable BARs, RTR data registers, and a GPU IOV vendor-specific enhanced capability header. Important fields include ACS source validation and peer-to-peer redirect controls, ATS enable and smallest translation unit, PRI response failure/reset/status bits, PASID execution and privileged-mode support/enables, SR-IOV VF enable/MSE/ARI/ten-bit tag controls, VF counts/stride/device ID/page sizes/VF BARs, and multicast receive/block vectors.

Lane margining definitions cover the PCIe margining enhanced capability plus lane 0 through lane 15 control/status pairs. These fields report receiver number, margin type, payload/usage mode, sampling reporting method, voltage/timing offset support, maximum lanes, independent error sampler support, margin software ready status, and per-lane control/status values such as margin payload, software ready, error count, sampler active, setup error, margining voltage/timing status, and lane number.

### DEV0 EPF1 Standard PCI Header And Capabilities

The chunk switches to `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and begins a new `BIF_CFG_DEV0_EPF1_0` function block. The initial registers model a conventional PCI endpoint header: vendor and device IDs, command/status bits, revision and class code bytes, cache line, latency, header type, BIST, base address registers 1 through 6, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability entries.

Power management and PCIe capability fields cover PM capability/status-control, PCIe capability header/type, device capability/control/status, link capability/control/status, and PCIe 2.0 device/link fields. The definitions include payload/read-request sizes, relaxed ordering, no-snoop, error reporting enables, FLR, link speed/width, ASPM, retraining, common clock, extended sync, target link speed, compliance, hardware autonomous speed disable, equalization request/status, supported link speeds, and completion-timeout controls.

MSI and MSI-X groups define capability-list headers, message control, 32-bit and 64-bit message address/data fields, per-vector masks, pending bits, MSI-X table/PBA BAR indicators and offsets, and MSI-X function mask/enable controls. Vendor-specific capability groups expose capability IDs, versions, next pointers, VSEC ID/revision/length, and two vendor data registers.

### DEV0 EPF1 Error Reporting And BAR/Power Extensions

The EPF1 AER group defines enhanced capability headers, uncorrectable error status/mask/severity fields, correctable error status/mask fields, AER capability/control bits, TLP header logs, and TLP prefix logs. The error bit names cover data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.

The EPF1 BAR, power-budgeting, DPA, secondary PCIe, ACS, ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV, data link feature, and 16 GT/s PHY capability families repeat the same layout pattern as EPF0 for a second endpoint function. This repetition is intentional and function-scoped: identical field names after the prefix refer to different PCIe function register images.

The chunk ends at the comment for `BIF_CFG_DEV0_EPF1_0_LANE_4_EQUALIZATION_CNTL_16GT`. The shifts and masks for EPF1 16 GT/s lanes 4 through 15 are outside this range and belong to the adjacent next chunk.

## Control Flow And State Behavior

There is no software control flow in this header slice. Its behavior is compile-time substitution:

1. A translation unit includes `nbio_7_11_0_sh_mask.h`.
2. Driver code reads or prepares an NBIO/PCIe register value through a matching address macro.
3. The caller applies `*_MASK` and `*_SHIFT` constants, usually through AMDGPU field helpers, to decode or update a specific hardware field.

The header itself stores no state. Persistent and sticky state lives in the GPU's NBIF PCIe configuration registers and is changed only by hardware, firmware, the PCI core, or driver code outside this header. Some fields describe durable configuration, such as command enables, BAR sizes, MSI/MSI-X programming, PASID/ATS/PRI/SR-IOV controls, ACS routing controls, multicast tables, LTR latency values, DPA substate controls, link controls, and VF BAR sizing. Other fields are hardware status or logs, such as PCI status bits, device/link status, AER status and header logs, lane error status, 16 GT/s equalization status, parity mismatch status, margining status, DPA status, PRI status, and data-link feature status.

Several fields are action-like or side-effect-sensitive when written by owning code. Examples include link retrain, FLR, PRI reset, SR-IOV VF enable, MSI/MSI-X enable/mask bits, DPA substate control, ATS/PASID enables, data-link feature exchange enable, and margining software-ready/control bits. The masks only define bit positions; they do not encode PCIe sequencing, polling, write-one-to-clear behavior, or firmware coordination rules.

## Dependencies And Integration Points

The direct generated-header dependency is `nbio_7_11_0_offset.h`, which supplies the matching register offsets and identifiers for these fields. Unlike some older NBIO generations in this tree, this NBIO 7.11.0 header set only has offset and shift/mask headers visible under `include/asic_reg/nbio`; no sibling `nbio_7_11_0_default.h` or `nbio_7_11_0_smn.h` file was present in this checkout.

The concrete source-tree integration point is `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both `nbio_7_11_0_offset.h` and this shift/mask header. That NBIO implementation uses SOC15 and PCIe-port register access helpers to program HDP remaps, memory-controller access, SDMA/VPE/VCN/IH doorbell ranges, doorbell apertures, interrupt controls, PCIe/USB4 master controls, and related NBIO state. Display resource code for DCN 3.5/3.5.1 includes the companion offset header, tying this register namespace into display bring-up even when it does not directly include the mask header.

The semantic dependencies are PCI and PCI Express capability layouts: standard endpoint configuration header, PM capability, PCIe device/link capability, MSI/MSI-X, vendor-specific capabilities, device serial number, Advanced Error Reporting, resizable BAR, Power Budgeting, Dynamic Power Allocation, Secondary PCIe/equalization, ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, data link feature, 16 GT/s PHY capability, lane margining, and AMD GPU IOV/RTR vendor-specific records.

## Risks And Maintenance Notes

- The range is mechanically generated and highly repetitive. EPF0 and EPF1 contain many parallel capability families where only the function prefix changes, making generation drift or copy/paste review errors difficult to spot.
- Chunk boundaries split complete definitions. The first line is only the `BAR1_CAP` mask after its shift appeared in the previous chunk, and the last line is only the comment for EPF1 lane 4 16 GT/s equalization before its fields appear in the next chunk.
- Wrong masks in command, BAR, MSI/MSI-X, SR-IOV, ATS, PASID, ACS, PRI, or VF BAR fields can affect DMA reachability, interrupt delivery, virtualization isolation, IOMMU translation behavior, and guest-visible PCI configuration.
- Status, mask, severity, enable, and control fields have different hardware semantics even when their field names are similar. AER status/mask/severity registers are especially easy to confuse.
- Some hardware status bits may be sticky, write-one-to-clear, firmware-owned, or updated asynchronously by PCIe link logic. Generic read-modify-write code must respect the owning register's hardware rules instead of relying on the mask name alone.
- Link management fields for 8 GT/s and 16 GT/s equalization, lane error status, parity mismatch status, target link speed, retraining, and data link feature exchange can affect link stability and performance if programmed out of sequence.
- Lane margining and 16 GT/s equalization fields are compliance/debug oriented. Using the masks outside tested diagnostic flows can disturb the link partner or produce misleading signal-integrity results.
- Integer constants use the existing AMD style with `L` suffixes and full-width masks such as `0xFFFFFFFFL`; consumers should keep the established 32-bit register helper types to avoid signedness or truncation issues.
- These definitions are NBIO 7.11.0-specific and should not be mechanically reused for other NBIO versions without comparing the version-specific generated offset and mask headers.

## Test And Validation Signals

Useful validation signals for this chunk include:

- Build coverage for translation units that include `nbio_7_11_0_sh_mask.h`, especially `amdgpu/nbio_v7_11.c`.
- Static generated-header checks that every complete register field in the slice has consistent `*_SHIFT` and `*_MASK` pairs, masks are aligned with shifts, and repeated lane/function families have the expected per-lane or per-function coverage.
- Cross-header checks that `BIF_CFG_DEV0_EPF0_0_*` and `BIF_CFG_DEV0_EPF1_0_*` register names in this slice have matching register offset definitions in `nbio_7_11_0_offset.h`.
- PCI enumeration and config-space dumps on NBIO 7.11 hardware comparing decoded vendor/device IDs, class/header fields, BARs, PM, PCIe link/device state, MSI/MSI-X, serial number, AER, resizable BAR, ACS, ATS, PASID, PRI, SR-IOV, LTR, DPA, multicast, DLF, 16 GT/s, and margining capability records against `lspci -vvxxx` or AMDGPU debug register reads.
- Interrupt tests covering MSI and MSI-X enable/mask/table/PBA fields, plus AMDGPU IH behavior after NBIO initialization.
- Virtualization and IOMMU tests covering ATS, PASID, PRI, ARI, SR-IOV VF counts/stride/device IDs/VF BARs, ACS isolation controls, and GPU IOV vendor-specific capability exposure.
- PCIe error-path tests or platform AER injection validating uncorrectable/correctable error status, masks, severity, AER capability/control, TLP header logs, and prefix logs without touching unrelated bits.
- Link validation covering target speed, retrain behavior, 8 GT/s and 16 GT/s equalization state, lane error status, parity mismatch status, data link feature exchange, and lane margining diagnostics across all available lanes.
- Power-management validation around Power Budgeting, DPA substates, LTR latency values, PM capability state, ASPM-related link controls, suspend/resume, and runtime power transitions.

## Unresolved Cross-Chunk References

The previous chunk owns the `BIF_CFG_DEV0_EPF0_0_PCIE_BAR_ENH_CAP_LIST` definitions and the `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP__BAR_SIZE_SUPPORTED__SHIFT` line immediately before this range. The next chunk owns `BIF_CFG_DEV0_EPF1_0_LANE_4_EQUALIZATION_CNTL_16GT` and the remaining EPF1 16 GT/s lane equalization controls. The merge/reconciliation lane should stitch those boundaries when creating the final per-file research document.
