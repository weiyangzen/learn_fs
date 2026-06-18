# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 109841-112318

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,132 preprocessor definitions: 1,066 `__SHIFT` constants and 1,066 matching `_MASK` constants. There are no C functions, structs, typedefs, enums, variables, allocations, locks, or executable statements in this range.

The segment starts in the endpoint-function 4 (`EPF4`) PCIe BAR capability tail, then covers complete endpoint-function 5 and endpoint-function 6 (`EPF5`/`EPF6`) PCI configuration layouts, and ends in the endpoint-function 7 (`EPF7`) layout after MSI-X PBA fields. The `EPF7` SATA, vendor-specific, AER, BAR, power-budget, DPA, ACS, and ARI capability fields continue in the following source lines and are not owned by this chunk.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield-definition half of AMDGPU's generated NBIO 7.0 register interface. This slice gives symbolic field geometry for NBIF device 0 endpoint functions 4 through 7. The macros let driver code and register helpers encode or decode PCI configuration, PCIe capability, MSI/MSI-X, AER, BAR, power-budget, DPA, ACS, and ARI fields without embedding numeric bit positions at call sites.

The file is hardware metadata, not active logic. It only says where each field lives within a register. Register addresses, reset/default values, access paths, and runtime sequencing are supplied by companion generated headers and AMDGPU NBIO/SOC15 code.

## Important APIs, Types, And Macros

The public interface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for the field.
- `<REGISTER>__<FIELD>_MASK`: field mask at its encoded position.

Important register families in the chunk include:

- `BIF_CFG_DEV0_EPF4_2_PCIE_BAR4_CNTL` through `BIF_CFG_DEV0_EPF4_2_PCIE_ARI_CNTL`: the tail of the EPF4 enhanced-capability area, including BAR5/BAR6 sizing and control, power-budget capability/data selection, dynamic power allocation (DPA), access control services (ACS), and alternative routing-ID interpretation (ARI).
- `BIF_CFG_DEV0_EPF5_2_*`: a full endpoint-function PCI configuration and PCIe extended capability layout. It includes identity and command/status fields, revision/class/header/BIST fields, six base-address registers, adapter and ROM IDs, interrupt pins, vendor and PM capability headers, PCIe device/link capability/control/status registers, device/link capability 2 registers, MSI and MSI-X tables/PBA fields, SATA capability/index/data fields, vendor-specific enhanced capabilities, AER uncorrectable/correctable status/mask/severity and header/TLP-prefix logs, enhanced BAR capability/control registers, power-budget data, DPA state, ACS capability/control, and ARI capability/control.
- `BIF_CFG_DEV0_EPF6_2_*`: a second full endpoint-function layout with the same broad structure as EPF5. The repeated namespace lets hardware expose separate endpoint functions while preserving per-function PCIe, interrupt, BAR, AER, DPA, ACS, and ARI state.
- `BIF_CFG_DEV0_EPF7_2_*`: the beginning of a third endpoint-function layout. This chunk covers standard PCI identity, command/status, BARs, PM capability, PCIe device/link capability/control/status, device/link capability 2, slot placeholders, MSI, and MSI-X fields through `BIF_CFG_DEV0_EPF7_2_MSIX_PBA`.

There are no callable APIs or C types. Consumers typically use these constants through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`, combined with register offsets from `nbio_7_0_offset.h` and reset/default metadata from `nbio_7_0_default.h`.

## Control Flow

This header chunk has no local control flow. Runtime behavior is external:

1. AMDGPU or platform code selects a PCIe/NBIO register address for an endpoint function.
2. It reads or composes a register value using the matching `__SHIFT` and `_MASK` constants.
3. It writes the value through the appropriate PCI config, MMIO, SMN, or SOC15 access path.
4. NBIO/PCIe hardware performs the resulting action, such as enabling bus mastering, configuring BAR size, routing MSI/MSI-X interrupts, changing link policy, reporting AER status, selecting DPA substates, applying ACS policy, or advertising ARI capability.

The implied hardware flows include PCI enumeration, BAR sizing, power-management negotiation, PCIe link training and retrain, completion timeout/atomic/LTR/OBFF feature control, MSI/MSI-X setup, AER logging and masking, DPA substate power allocation, ACS peer-to-peer isolation control, and ARI function grouping.

## State And Persistence Behavior

The chunk owns no software state and persists nothing. It describes bit positions for state held in NBIO 7.0 hardware registers.

Represented state includes:

- Static or firmware-initialized identity fields: vendor/device IDs, class/revision, header type, capability pointers, adapter IDs, and PCIe capability headers.
- Writable PCI function configuration: command enables, interrupt disable, BAR controls, ROM base, power-management status/control, PCIe device/link control, completion timeout control, LTR/OBFF enables, and MSI/MSI-X control fields.
- Interrupt routing state: MSI address/data/mask/pending fields, 64-bit MSI variants, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- Error and diagnostic state: AER uncorrectable/correctable status, masks, severity, capability/control, header logs, and TLP prefix logs in EPF5 and EPF6.
- Capability advertisement and policy state: enhanced BAR sizing, power-budget data, DPA capability/status/control/substate allocations, ACS capability/control, and ARI capability/control.

Persistence across GPU reset, PCI reset, power gating, suspend/resume, hot reset, or firmware reinitialization is not defined by this header. Those semantics depend on hardware reset domains, PCIe config-space rules, firmware ownership, and AMDGPU restore paths.

## Dependencies And Integration Points

The primary dependencies are sibling generated register headers:

- `nbio_7_0_offset.h` for register offsets matching these names.
- `nbio_7_0_default.h` for generated reset/default values.
- `nbio_7_0_smn.h` for SMN-addressed NBIO registers outside ordinary config offset space.
- Adjacent chunks of `nbio_7_0_sh_mask.h`, because this chunk starts after earlier EPF4 BAR definitions and stops before the rest of EPF7.

Direct in-tree include sites for this header are `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. The practical integration areas are AMDGPU NBIO initialization, SOC15 common setup, PCIe register programming, power management, interrupt setup, endpoint-function enumeration, BAR aperture handling, AER/RAS observability, ACS isolation policy, ARI function discovery, and any hardware diagnostics that inspect capability/status registers.

Although this source tree is under a Ceph-client mirror, this chunk is GPU driver register metadata. It has no Ceph filesystem or distributed-storage control path.

## Risks And Edge Cases

- Generated shift/mask drift can compile successfully while programming the wrong bit, causing PCI enumeration failures, broken BAR sizing, MSI/MSI-X routing bugs, link instability, missing AER reporting, unsafe ACS isolation, or incorrect DPA/power-management behavior.
- The chunk boundaries split logical endpoint-function coverage. EPF4 begins before this range, while EPF7 continues after it; whole-file research and validators must reconcile adjacent chunks before treating either endpoint function as complete.
- EPF5 and EPF6 are highly repetitive. A generator or copy error may affect only one function instance and remain hidden if validation exercises another endpoint function.
- Many status, mask, severity, and control registers use similar field names. Confusing AER status with mask/severity fields, or MSI mask with MSI pending fields, can silently alter interrupt/error behavior.
- Full-width masks such as `0xFFFFFFFFL` appear for MSI address high dwords, MSI masks/pending bits, SATA IDP data, AER header logs, and TLP prefix logs. A full mask does not imply arbitrary writes are harmless; access type and side effects are hardware-defined elsewhere.
- Reserved placeholder registers (`DEVICE_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, `SLOT_STATUS2`) expose masks for reserved bits. Consumers should not infer meaningful writable functionality from reserved-field macros.
- DPA, power-budget, LTR, OBFF, completion-timeout, and link-control fields interact with platform power policy and PCIe state machines. Misprogramming can create hard-to-reproduce suspend/resume, runtime PM, or link-training failures.
- ACS and ARI fields influence function routing and peer-to-peer isolation. Incorrect masks can affect security/isolation assumptions for DMA and multifunction endpoint behavior.

## Test And Validation Signals

- Build AMDGPU with NBIO 7.0/SOC15 support enabled. Compile-time coverage catches missing, renamed, or syntactically malformed macros referenced by consumers.
- Run generated-header consistency checks so each field in this chunk has a paired `__SHIFT` and `_MASK`, masks do not overlap unexpectedly inside a register, and repeated EPF5/EPF6/EPF7 patterns match the hardware database where they overlap.
- Cross-check register names against `nbio_7_0_offset.h`, `nbio_7_0_default.h`, and `nbio_7_0_smn.h` so address/default metadata stays aligned with field metadata.
- Validate chunk-boundary reconciliation: EPF4 capability definitions must be joined with earlier chunks, and EPF7 must be joined with the next chunk before generating final per-file conclusions.
- On NBIO 7.0 hardware, smoke-test PCI enumeration, BAR probing, bus-master/memory-enable handling, MSI and MSI-X interrupt delivery, link speed/width negotiation, completion-timeout behavior, LTR/OBFF behavior, reset/resume restore, AER status/mask reporting, ACS policy, ARI discovery, and DPA/power-budget readback.
- For AER-heavy fields in EPF5/EPF6, compare decoded status, mask, severity, header-log, and TLP-prefix-log values against PCIe error-injection or platform error-reporting traces.

## Chunk Boundary Notes

Line 109841 starts directly with `BIF_CFG_DEV0_EPF4_2_PCIE_BAR4_CNTL` field definitions; the preceding source chunk owns the nearby EPF4 BAR4 capability context. This chunk then completes the EPF4 enhanced-capability tail, owns full EPF5 and EPF6 endpoint-function layouts, and owns EPF7 only through `BIF_CFG_DEV0_EPF7_2_MSIX_PBA`. The following chunk must supply the remaining EPF7 SATA, vendor-specific, AER, BAR, power-budget, DPA, ACS, and ARI definitions.
