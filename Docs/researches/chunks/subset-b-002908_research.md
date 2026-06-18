# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 9847-12321

## Scope

This chunk is a generated AMD NBIO 2.3 register field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, allocation, locking, or executable control flow.

The range starts in the middle of `BIF_CFG_DEV0_EPF2_0_DEVICE_CNTL`, after that register's shift definitions and after the first few mask definitions. It then covers the rest of PCI configuration-space and enhanced-capability field layouts for endpoint function 2 (`BIF_CFG_DEV0_EPF2_0_*`), the full standard/header and most extended capability layout for endpoint function 3 (`BIF_CFG_DEV0_EPF3_0_*`), and begins the `nbio_nbif0_syshub_mmreg_syshubdirect` block. The chunk ends mid-register inside `SYSHUB_TRANS_IDLE_SOCCLK` after the first five VF idle masks; the remaining VF/PF idle masks are in the following chunk.

Although this repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bitfield ABI for NBIO 2.3 PCIe endpoint configuration and SYSHUB SOC clock controls. Each named hardware field generally appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

The matching register address metadata lives in `nbio_2_3_offset.h`, with `cfgBIF_CFG_DEV0_EPF2_0_*`, `cfgBIF_CFG_DEV0_EPF3_0_*`, and SYSHUB symbols mapping these field names to PCI config-space or MMIO offsets. Runtime AMDGPU code includes this header and combines the constants with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The `BIF_CFG_DEV0_EPF2_0_*` portion describes endpoint function 2 PCIe capability registers from device control/status onward. It names the standard PCIe device and link control/status fields: correctable, non-fatal, fatal, unsupported-request, auxiliary-power, pending-transaction, emergency power reduction, negotiated link speed/width, link training, link bandwidth notification, ASPM/clock power management, FLR initiation, max payload size, max read request size, relaxed ordering, no-snoop, extended tags, and completion timeout controls.

The same EPF2 block defines MSI and MSI-X capabilities. These include capability IDs and next pointers, MSI enable/multiple-message/64-bit/per-vector-mask controls, 32-bit and 64-bit MSI address/data/mask/pending fields, MSI-X table size/function mask/enable bits, and table/PBA BIR and offset fields. These constants support interrupt capability exposure and programming through the endpoint's PCI config image.

EPF2 also covers SATA capability and indirect data port registers, vendor-specific PCIe enhanced capability headers and payload words, AER enhanced capability registers, header/TLP-prefix logs, resizable BAR-like BAR capability/control registers for BAR1 through BAR6, power budget data selection/data/capability fields, dynamic power allocation capability/status/control/substate power allocation fields, ACS capability/control fields, PASID capability/control fields, ARI capability/control fields, and TPH requester capability/control plus 64 steering-tag table entries.

The `BIF_CFG_DEV0_EPF3_0_*` block starts at the beginning of endpoint function 3's PCI configuration image. It includes vendor/device ID, command/status, revision/class code bytes, cache line/latency/header/BIST, BAR1-BAR6, CIS pointer, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant/max latency, vendor and power-management capabilities, SATA adjustment registers, PCIe capability registers, MSI/MSI-X, SATA, vendor-specific, AER, BAR, power budget, DPA, ACS, PASID, ARI, and TPH requester fields. Most EPF3 field layouts mirror EPF2, but this chunk carries EPF3 from the standard header rather than beginning mid-capability.

The TPH steering tables are highly repetitive for both EPF2 and EPF3. `BIF_CFG_DEV0_EPF[23]_0_PCIE_TPH_ST_TABLE_0` through `_63` each define lower and upper 8-bit entries. These fields are used to expose or program requester steering-tag mappings, so table index/order correctness matters even though the constants are mechanically regular.

The final SYSHUB block switches from endpoint PCI config space to the `nbio_nbif0_syshub_mmreg_syshubdirect` address block. `SYSHUB_DS_CTRL_SOCCLK` defines host client, DMA client, and top-level SYSHUB SOCCLK deep-sleep allow/enable bits. `SYSHUB_DS_CTRL2_SOCCLK` provides the deep-sleep timer field. The `SYSHUB_BGEN_ENHANCEMENT_*_SOCCLK` registers expose bypass and immediate-enable controls for host and DMA switch clock-generation behavior. `SYSHUB_TRANS_IDLE_SOCCLK` is a one-bit-per-function idle bitmap for VF0 and upward plus PF, but this chunk stops before the full bitmap is present.

## Control Flow

There is no runtime control flow in this header. Runtime sequencing belongs to AMDGPU NBIO, PCIe, SMU, interrupt, SR-IOV, and power-management code that includes it:

1. Driver code selects a register offset from `nbio_2_3_offset.h`.
2. It reads or prepares a 16-bit or 32-bit config/MMIO value with PCIe or SOC15 access helpers.
3. It uses these `__SHIFT` and `_MASK` constants directly or through register helper macros to update or decode individual fields.
4. It writes the value back, polls a status bit, clears sticky status, or leaves hardware/firmware to update status-owned fields.

For this chunk, common runtime flows include PCIe capability enumeration/programming, interrupt capability control, AER status collection/clearing, BAR capability setup, PASID/ACS/ARI/TPH virtualization capability handling, DPA/power-budget reporting, and SYSHUB clock/deep-sleep policy programming.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes MMIO and PCI config-space state owned by the GPU, firmware, host PCIe fabric, and driver.

The represented hardware state includes PCI command/status bits, PCIe device and link capabilities, interrupt address/data/mask/pending state, AER error masks/severity/status and logs, BAR sizing/control data, power budget and DPA substate values, ACS/PASID/ARI/TPH enablement, TPH steering-tag table contents, endpoint identity/header fields, and SYSHUB SOCCLK deep-sleep and idle status/control bits. Some fields are static capability descriptions, some are driver-programmed controls, some are hardware-updated status, some are sticky error logs, and some behave as command or write-one-to-clear fields. The generated constants do not encode those side effects.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database and must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`. The offset header provides address symbols such as `cfgBIF_CFG_DEV0_EPF2_0_DEVICE_CNTL`, while this shift/mask header provides the field layout for values read from or written to those addresses.

Direct integration is through AMDGPU code that includes `nbio/nbio_2_3_sh_mask.h`, including `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU power-management files such as `pm/swsmu/smu11/navi10_ppt.c` and `pm/swsmu/smu11/sienna_cichlid_ppt.c`. Those consumers rely on the generated names rather than duplicating bit positions.

The EPF2/EPF3 PCI configuration macros integrate with PCIe endpoint exposure, function-level reset, AER/error handling, MSI/MSI-X interrupts, SR-IOV and virtual function capability surfaces, PASID/ACS/ARI isolation and addressing features, TPH steering, resizable BAR/power capability reporting, and power-management policy. The SYSHUB macros integrate with clock gating, deep sleep, transaction-idle detection, and suspend/resume or runtime power paths.

## Risks And Edge Cases

- The chunk boundaries are artificial. The first line is already inside `BIF_CFG_DEV0_EPF2_0_DEVICE_CNTL`, and the final line stops inside `SYSHUB_TRANS_IDLE_SOCCLK`. Adjacent chunks are required before making whole-register claims for those two registers.
- These macros are untyped integer constants. A wrong mask value can compile cleanly while updating the wrong hardware bit; a renamed or missing macro is more likely to fail at build time.
- PCIe control fields such as FLR, max payload, max read request, completion timeout, relaxed ordering, no-snoop, ASPM/link control, ARI, PASID, ACS, TPH, and AER are interoperability-sensitive. Incorrect values can break enumeration, DMA ordering, virtualization isolation, interrupt delivery, error reporting, or link recovery.
- MSI/MSI-X address/data/mask/pending fields have interrupt-delivery side effects. Width or alignment mistakes can cause lost, misrouted, or unexpectedly unmasked interrupts.
- AER status, severity, mask, header log, and TLP-prefix log fields include sticky or clear-on-write behavior. Treating status/clear bits as ordinary retained configuration can hide errors or clear diagnostic evidence.
- BAR capability/control and DPA/power-budget fields can affect resource sizing and power policy. Incorrect masks may expose invalid apertures, wrong BAR sizes, or misleading power capabilities.
- TPH steering tables are dense and repetitive. Off-by-one table indexing or lower/upper-entry confusion can silently steer traffic with the wrong tag.
- SYSHUB SOCCLK deep-sleep and idle bits are power and liveness sensitive. Enabling deep sleep without respecting host/DMA/PF/VF idle state can cause hangs, lost wakeups, or power-management regressions.

## Test Signals

Useful validation is mostly build, boot, and hardware-integration oriented:

- Build AMDGPU for ASICs using NBIO 2.3 headers; direct macro drift should surface as compile failures in NBIO, SMU, MXGPU, PCIe, or interrupt code.
- Boot affected hardware and confirm PCI enumeration shows stable device/function IDs, BARs, PCIe capabilities, MSI/MSI-X capabilities, AER capability, PASID/ACS/ARI/TPH capabilities, and expected link speed/width.
- Exercise MSI and MSI-X interrupt delivery under graphics, compute, display, and reset workloads; lost interrupts or stuck pending bits point to config mask/offset issues.
- Run PCIe error handling and reset paths covering AER status/logging, FLR initiation/completion, completion timeout behavior, link retraining, and suspend/resume.
- In SR-IOV or multi-function configurations, validate EPF2/EPF3 capability exposure, VF isolation features, PASID/ARI/ACS controls, and TPH steering behavior.
- Exercise runtime power management, clock gating, and suspend/resume while monitoring SYSHUB deep-sleep enablement and transaction-idle status; hangs, failed wakeups, or unexpected power use are strong signals of field-layout drift.
