# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 7403-9846

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts in the tail of `BIF_CFG_DEV0_EPF1_0_LINK_CAP`, covers a large PCIe configuration-space and extended-capability block for endpoint function 1 (`BIF_CFG_DEV0_EPF1_0_*`), then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and covers the beginning of endpoint function 2 (`BIF_CFG_DEV0_EPF2_0_*`). It ends inside `BIF_CFG_DEV0_EPF2_0_DEVICE_STATUS`; the remaining status masks continue after this assigned range. Although the repository path is under a local `ceph-client` mirror, this file is AMD GPU PCIe/NBIO hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this header chunk is to publish the bit layout contract for NBIO 2.3 PCI/PCIe config decoder registers. Each field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or preserve the field in the register value.

AMDGPU NBIO/BIF code combines these masks with companion register-address headers for the same ASIC generation and register access helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`. The header itself only names fields; it does not define access policy or side-effect semantics.

## Important Macro Families

The first part of the chunk finishes PCIe link capability/control/status coverage for endpoint function 1. It includes link power management, retrain and disable controls, common clock and extended sync, autonomous width/speed controls, bandwidth-management/autonomous-bandwidth interrupt status, data rate signaling, negotiated speed/width, data-link active, Gen2+ link capability/control/status fields, equalization completion and phase status, crosslink/presence reporting, and downstream-component presence.

The function-1 device capability/control block includes PCIe capabilities such as completion timeout support and disable, ARI forwarding, atomic operations, ID-based ordering, latency tolerance reporting, OBFF, end-to-end TLP prefix support/blocking, emergency power reduction, fast role swap, ten-bit tags, max payload/read request sizing, relaxed ordering, no-snoop, auxiliary power management, FLR initiation, and ordinary device status/error bits.

Interrupt capability macros cover MSI and MSI-X for function 1. The MSI block defines capability-list IDs and next pointers, MSI enable and multi-message controls, 32-bit and 64-bit message address/data words, per-vector masks, and pending bits. The MSI-X block defines table size, function mask, enable, table BIR/offset, and PBA BIR/offset fields.

Several PCIe extended-capability families are present for function 1: vendor-specific headers and data dwords, virtual channel capability/control/status and VC0/VC1 resource registers, device serial number dwords, advanced error reporting status/mask/severity/capability/header-log/TLP-prefix-log registers, resizable BAR capability/control for BAR1 through BAR6, power budget data selection/data/capability, dynamic power allocation capability/status/control and substate power allocation registers, secondary PCIe/link-control/lane-error/lane-equalization registers, ACS, ATS, page request interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data link feature, PHY 16 GT/s, lane margining, VF resizable BAR, and AMD vendor-specific GPUIOV blocks.

The GPUIOV vendor-specific region is especially virtualization-oriented. It defines VSEC metadata, an SR-IOV shadow field, interrupt enable/status, reset control, HVVM mailbox dwords, context, total framebuffer and offset/region fields, peer-to-peer over XGMI enable, per-VF framebuffer offset/size fields for VF0 through VF30, and scheduling/resource dwords for UVD, VCE, GFX, and UVD1 engines. These masks are part of the PF-visible contract used to partition or report GPU resources to virtual functions.

The second part of the range begins endpoint function 2. It covers standard PCI header fields: vendor/device IDs, command/status, revision and class codes, cache-line and latency fields, header/BIST, BAR1-BAR6, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, a vendor capability list, power-management capability/status-control, USB-related SBRN/FLADJ/DBESL fields, PCIe capability list/header, PCIe device capability/control, and the start of PCIe device status.

## Control Flow

There is no runtime control flow in this chunk. The effective use pattern is driven by consuming driver code:

1. Select the matching register offset from the NBIO 2.3 offset header or an ASIC-specific register table.
2. Read a PCIe config/MMIO register value through AMDGPU register access helpers.
3. Use the `__SHIFT` and `_MASK` constants, commonly through `REG_GET_FIELD` or `REG_SET_FIELD`, to decode or update a field.
4. Write the updated value back, or poll/status-check the decoded bits according to the PCIe/NBIO programming sequence.

The repeated lane, BAR, VF, and capability blocks imply table-like hardware layout, but this header does not implement iteration. Any loop over lanes, BARs, VFs, or functions lives in the AMDGPU NBIO/SR-IOV/PCIe code that selects the corresponding register offset and macro family.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware and PCI configuration state owned by the GPU, PCIe fabric, firmware, and driver.

Some represented fields are configuration that may persist until reset, FLR, suspend/resume, power transition, or explicit reprogramming: PCI command enables, BAR values, MSI/MSI-X message data and masks, link/device controls, AER masks and severity bits, DPA allocations, ACS/ATS/PASID/PRI controls, SR-IOV counts and VF BARs, resizable BAR settings, power-management controls, and GPUIOV framebuffer/resource partitioning.

Other fields are hardware-owned observations, command strobes, sticky logs, or write-one-to-clear status: device/link status, AER error status and header logs, TLP prefix logs, lane error and equalization status, margining status, MSI pending bits, PME status, SR-IOV status, data-link feature status, and GPUIOV interrupt/reset/mailbox status. The macro names do not encode read/write side effects; consumers must use PCIe and AMDGPU programming rules for the actual access semantics.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must stay synchronized with the matching offset/default headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`; offsets identify the register addresses while this file identifies the fields within those registers.

Primary integration is with AMDGPU NBIO, PCIe, interrupt, reset, RAS/AER, power-management, and virtualization paths. The function-1 and function-2 PCI config macros are consumed when driver code configures or diagnoses PCI command/status, link training, link speed/width, MSI/MSI-X delivery, AER masking/logging, resizable BARs, DPA and power budgeting, ATS/PRI/PASID address-translation features, ACS isolation, SR-IOV VF enumeration, VF BAR layout, GPUIOV resource accounting, and function-level reset behavior.

The macros are untyped integer constants. A renamed or missing macro generally fails at compile time, but a wrong shift or mask can compile cleanly and cause the driver to program an adjacent field or decode the wrong status bit. Because this is generated ASIC metadata, manual edits should be treated as hardware ABI changes and checked against the authoritative register source.

## Risks And Edge Cases

- Chunk boundaries are partial. The first line is already inside `BIF_CFG_DEV0_EPF1_0_LINK_CAP`, and the final line stops inside `BIF_CFG_DEV0_EPF2_0_DEVICE_STATUS`. The merge lane must combine adjacent chunks before making whole-register or whole-file coverage claims.
- Width and access-size assumptions matter. The range mixes 8-bit PCI header fields, 16-bit capability/control/status words, and 32-bit extended-capability dwords. Using the wrong access width or offset family can silently corrupt neighboring PCIe fields.
- Status and clear fields are not type-distinguished. AER status, device status, MSI pending, PME status, lane error, and GPUIOV interrupt/status fields may have sticky or write-one-to-clear behavior in hardware; ordinary read-modify-write handling can be unsafe.
- Interrupt definitions are delivery-critical. Incorrect MSI/MSI-X enable, function mask, table/PBA offset, message address/data, or vector mask fields can cause lost interrupts, spurious interrupts, or broken isolation under virtualization.
- Link control and equalization fields are interoperability-sensitive. Incorrect target speed, autonomous speed/width disable, retrain, common clock, DRS, margining, or 16 GT/s equalization masks can cause link training failures, bandwidth regressions, or unstable resume behavior.
- Virtualization blocks are dense and repetitive. Per-VF framebuffer fields, SR-IOV counts/strides/device IDs, VF BAR controls, ACS/ATS/PASID/PRI, and GPUIOV mailbox/resource registers are easy places for off-by-one VF or lane mistakes that grant, deny, or report the wrong resource.
- AER and error-log masks affect diagnostics and recovery. Wrong masks or severities can hide real PCIe errors, trigger unnecessary fatal handling, or make logged headers/TLP prefixes decode incorrectly.
- Full-width fields such as BARs, message addresses, mailbox dwords, scheduler dwords, and log dwords are not self-validating. Pairing a full-width mask with the wrong register offset can overwrite unrelated hardware/firmware coordination state.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers, with PCIe, MSI/MSI-X, AER, SR-IOV, ATS/PRI/PASID, and resizable BAR support enabled; missing macros should surface as compile failures.
- Run generated-header consistency checks against the NBIO 2.3 register database and sibling offset headers, including shift/mask pair width checks and non-overlap checks within each register.
- Boot/enumeration tests confirming the GPU and its endpoint functions expose expected PCI headers, capability-list traversal, BARs, class codes, command/status bits, and power-management capabilities.
- PCIe link tests covering speed/width reporting, retraining, Gen2+/16 GT/s equalization, lane error status, margining, data-link active reporting, DRS, and suspend/resume transitions.
- MSI/MSI-X interrupt tests under physical and virtualized configurations, including vector masking, pending bits, table/PBA placement, and function mask behavior.
- AER/error-injection or fault-observation tests validating uncorrectable/correctable status, mask, severity, header logs, TLP prefix logs, and recovery handling.
- SR-IOV/GPUIOV tests validating VF counts, VF BAR sizing, per-VF framebuffer offset/size assignment, PF-to-HV mailbox behavior, GPUIOV interrupt/reset fields, and scheduler/resource dword programming for every represented VF/resource family.

## Chunk-Specific Notes For Merge

This chunk should be merged with adjacent chunks for `nbio_2_3_sh_mask.h` before producing the final source-tree-aligned per-file research document. Preserve that this slice specifically covers the function-1 PCIe capability tail through GPUIOV resource definitions, then the beginning of function-2 PCI/PCIe configuration definitions through the start of device status.
