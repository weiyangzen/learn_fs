# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 39157-41595

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header segment. It contains 2,138 `#define` macros over 2,439 source lines, all describing register bit positions (`__SHIFT`) and bit masks (`_MASK`) rather than executable driver logic.

The range starts inside the PCIe capability register layout for `BIF_CFG_DEV2_RC0`, then covers the rest of that root-complex/function configuration block through lane margining. It then covers BIF indexed access and scratch/CAM registers, NBIO RCC strap fields for BIF and device 0 endpoint functions, endpoint-side RCC PCIe controls for device 0, and the beginning of the downstream-device RCC PCIe control block. The range ends at `RCC_DWN_DEV0_1_DN_PCIE_STRAP_MISC__STRAP_MST_ADR64_EN_MASK`; `RCC_DWN_DEV0_1_DN_PCIE_STRAP_MISC2` and the downstream-port block continue after this chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata and has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_sh_mask.h` gives driver code symbolic field encodings for NBIO 7.2.0 registers. Consumers combine these `__SHIFT` and `_MASK` macros with register offsets from `nbio_7_2_0_offset.h` and AMDGPU register helpers to read, write, or construct fields without embedding raw bit positions.

This chunk is focused on PCIe-facing NBIO behavior: PCIe capability advertisement/control, MSI, AER, virtual channels, secondary and 16 GT/s link features, lane equalization and margining, indexed MMIO/PCIe access windows, BIOS scratch state, interrupt control bits for graphics/video engines, strap-selected device/function identity and capabilities, endpoint LTR/DPA/TPH/error policy, and downstream hidden-register/strap controls.

## Important Macro Families

The opening `BIF_CFG_DEV2_RC0_*` block defines the bit layout of PCIe capability space for device 2 root complex 0. It includes standard PCIe capability fields for device, link, slot, root, second-generation device/link capabilities, MSI capability registers, subsystem ID, MSI mapping, vendor-specific enhanced capabilities, virtual-channel capability/control/status, device serial number, advanced error reporting, secondary PCIe, lane equalization, ACS, data-link feature, 16 GT/s PHY, and margining capability/status.

The device/link/slot/root capability macros cover payload and read-request sizes, relaxed ordering, extended tags, no-snoop, phantom functions, ASPM and power-management support, link speed/width, link retraining, common-clock and extended-sync configuration, data-link active status, hotplug and attention/power indicators, root error enables, CRS visibility, atomic operation routing, LTR enablement, OBFF, emergency power reduction, IDO, EETLP, 10-bit tag support, and completion-timeout controls.

The AER macros cover uncorrectable error status/mask/severity fields, correctable error status/mask fields, AER capability/control, header logs, root error command/status, error source IDs, and TLP prefix logs. Error names include DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.

The link training and PHY macros cover secondary PCIe link control, lane error status, per-lane equalization control for lanes 0-15, 16 GT/s link capability/control/status, local/RTM parity mismatch status, and per-lane 16 GT/s equalization control. The margining section repeats per lane 0-15 and provides receiver number, margin type, usage model, payload, and matching status fields.

The `BIF_BX_PF1_*` and `BIF_BX1_*` blocks define indexed access and scratch register fields. These include PF1 MM index/data/index-high fields, PCIe index/data windows, SBIOS and BIOS scratch dwords, interrupt-control bits for RLC/VCE/UVD command completion, hang self-recovery, FLR-needed, VM busy transitions, and UVD instance select, plus graphics MMIO register CAM address/remap/enable/completion fields.

The `RCC_STRAP1_*` block describes strap-selected NBIO and device-function configuration. BIF-level straps include link generation disable/kill controls, VGA/BIOS ROM/memory aperture pins, PX capability, MSI payload behavior, error-ignore policy, PME compliance, quick-sim mode, P2P relaxed-ordering policy, VF bus-number checking, Big APU mode, link-down reset, SR-IOV enable, IOV BAR mapping, PASID page-request support, BDF and revision identifiers, power-budget data, and downstream vendor/device/function identity. Device 0 port straps cover target link speed/width, ASPM, clock PM, lane reversal, lane equalization presets, extended sync, hotplug, slot power and physical slot fields, AER/ACS/ARI/ATS/LTR/DPA/OBFF/atomic support, Max Payload/Read Request limits, DRS, VC/TPH/IDO support, multicast, 10-bit tag support, power budget data, and root-port bus/device/function identity. Endpoint function straps for F0 and F1 cover device/vendor/class/subsystem IDs, function enable, D1/D2 and power/PME support, resizable BAR, PASID width/features, MSI/MSI-X, AER/ACS/ATS/DPA/DSN/VC, poisoned advisory behavior, clock PM, atomic/FLR, BAR aperture sizing, VGA and ROM behavior, VF aperture sizing, SR-IOV VF mapping, outstanding page-request capacity, GPUIOV VSEC revision, and aperture enable/prefetch/64-bit BAR properties.

The `RCC_EP_DEV0_1_*` block defines endpoint-side PCIe control fields for device 0. It includes scratch, unsupported-request reporting disable, malformed atomic operation handling, LTR-message UR handling, interrupt control/status bits for FLR done and VM updated events across functions, RX invalid PASID handling, immediate PMI and AER completion-timeout relaxed-ordering policy, hidden-register decode enables for Gen2/Gen3/Gen4 windows, private TX LTR timing/requirement controls, DPA power-allocation fields for F0/F1 substates, TPH strap support, DPA latency and compliance fields, PME service timer, TX snoop/relaxed-order override, per-function TPH disable bits, requester ID bus/device/function fields, AER header-log timer/error-reporting control, RX error-ignore/timeout/TPH policy, and Gen2/Gen3/Gen4 link-speed strap enables.

The final `RCC_DWN_DEV0_1_*` portion begins downstream-device control fields. It defines reserved and scratch dwords, hardware-initialization write lock, downstream unsupported-request reporting disable, downstream LTR-message UR handling, extended-tag override, FLR extend mode, immediate PMI disable, downstream AER completion-timeout relaxed-ordering disable, hidden-register decode enables, function-0 enable/multicast/MSI multi-message capability, clock power-management strap, and 64-bit master-address strap.

## APIs, Types, And Functions

There are no callable APIs, C types, functions, variables, allocations, locks, or executable statements in this chunk. The public interface is the preprocessor namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the raw field mask in the register value.

Consumers are expected to use these macros with sibling generated offset/default headers and AMDGPU register helpers. This header does not encode access permissions, reset values, read side effects, write-one-to-clear semantics, required delays, firmware ownership, or whether a field is safe to modify after boot.

## Control Flow

The header has no local runtime control flow. Runtime flow is external:

1. AMDGPU or firmware-facing code selects the NBIO 7.2.0 register symbol for the active ASIC and hardware block.
2. It reads or prepares a dword value using the companion register offset and the field mask/shift macros from this file.
3. It performs a read-modify-write or direct write through AMDGPU MMIO/indexed-register helpers, or decodes a sampled hardware value with the same masks.
4. Hardware then reflects or acts on the configured PCIe, strap, interrupt, reset, link, error, or power-management behavior.

The implied hardware flows include PCIe capability enumeration, link training and speed/width negotiation, ASPM/LTR/OBFF policy, MSI programming and masking, AER logging/reporting, virtual-channel setup, ACS/ATS/PASID exposure, 16 GT/s equalization and lane margining diagnostics, BIOS/driver scratch handoff, engine interrupt notification, endpoint FLR and VM update signaling, DPA substate/power allocation, TPH steering policy, hidden-register decode, downstream request/error handling, and strap-driven endpoint/root-port identity.

## State And Persistence Behavior

This header owns no software state and persists nothing. It describes bitfields for hardware state held in NBIO registers, PCIe configuration space, strap latches, scratch registers, and error/status logs.

State represented by this chunk includes PCIe capability and control bits, status and pending bits, link training state, slot/root status, MSI address/data/mask/pending state, AER status/masks/severity/logs/source IDs, lane equalization and margining controls/status, indexed access registers, BIOS/SBIOS scratch dwords, RLC/VCE/UVD interrupt controls, strap-derived identity and capability state, endpoint interrupt status, LTR/DPA/TPH policy, requester ID, RX/TX error-policy controls, downstream hidden-decode enables, and function/port strap fields.

Persistence is hardware-domain dependent. Strap fields are normally latched from hardware straps or firmware/BIOS initialization and may not be freely mutable after initialization. PCIe configuration fields can be changed by firmware, Linux PCI core, AMDGPU, hot reset, FLR, D-state changes, suspend/resume restore, or full GPU reset. Status and error fields may be sticky or write-one-to-clear, but this mask header does not specify those semantics. Scratch registers intentionally preserve handoff state only within the reset/power domain that owns them.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must remain synchronized with `nbio_7_2_0_offset.h`, any reset/default metadata, and related NBIF/NBIO headers for nearby IP versions. The matching offset chunk maps many of these same register names to SOC15-style register offsets and base indices; this chunk only defines the fields inside those registers.

Primary integration points are AMDGPU NBIO initialization, PCIe capability setup, Linux PCI enumeration expectations, MSI and interrupt setup, AER/RAS diagnostics, GPU reset and FLR recovery, runtime power management, ASPM/LTR/OBFF tuning, virtualization and SR-IOV/GPUIOV exposure, PASID/ATS/ACS-related IOMMU interactions, BIOS/firmware strap handoff, link training diagnostics, 16 GT/s equalization, lane margining debug flows, and suspend/resume register restoration.

The source search for representative names in this chunk did not reveal direct non-generated driver call sites outside the register-header tree. That suggests these symbols are mostly consumed indirectly through generated include selection and ASIC-specific register access code, or reserved for hardware/debug paths rather than ordinary driver logic.

## Risks And Edge Cases

- Generated mask drift can compile cleanly but make callers set or decode the wrong bit, causing subtle PCIe capability advertisement, link, MSI, AER, reset, or virtualization failures.
- This chunk starts and ends mid-register-family. The preceding chunk is needed for the beginning of `BIF_CFG_DEV2_RC0_PCIE_CAP`, and the following chunk completes `RCC_DWN_DEV0_1_DN_PCIE_STRAP_MISC2` and downstream-port controls.
- Many register names in this range map to PCIe configuration-space concepts with shared dwords. Read-modify-write code must preserve adjacent fields and use the right access width.
- AER status and log fields may be latched or write-one-to-clear. Treating `_MASK` as permission to do generic read-modify-write can clear diagnostic evidence or leave stale severity/mask state.
- Strap fields often reflect boot-time hardware/firmware policy. Late software writes, if even allowed, can desynchronize Linux PCI-visible capabilities from the underlying hardware configuration.
- Link speed, equalization, 16 GT/s, and lane margining fields are sequencing-sensitive and topology-sensitive. Incorrect values can appear as intermittent training failures, bandwidth downgrades, or unstable resume behavior.
- MSI/MSI-X, TPH, PASID, ATS, ACS, LTR, OBFF, and DPA fields interact with platform firmware, Linux PCI/IOMMU policy, and upstream root-complex behavior. Misprogramming can show up as DMA faults, interrupt loss, power regressions, or protocol errors rather than simple local failures.
- Endpoint and downstream unsupported-request/error-ignore controls can mask real PCIe errors. They are useful for hardware policy or workarounds but risky if used without matching errata context.
- Scratch and indexed-access registers expose broad access paths. Incorrect index/data ordering or stale index values can affect unrelated registers.
- Repeated per-lane and per-function macro patterns are mechanically generated. Single-lane or single-function mistakes can escape broad smoke tests and fail only under x16 links, a specific function, or a particular virtualization mode.

## Test Signals

- Build AMDGPU code paths that include NBIO 7.2.0 headers; compile coverage catches missing or malformed symbols used by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have the expected matching `_MASK`, field masks should align with shifts and widths, and register names should match the companion `nbio_7_2_0_offset.h` names.
- Cross-check repeated per-lane groups for lanes 0-15 and per-function F0/F1 strap groups for consistent field positions where the hardware specification expects symmetry.
- On NBIO 7.2.0 hardware, validate PCIe enumeration, capability list walking, BAR sizing, MSI delivery/masking, AER reporting/logging, ACS/ATS/PASID exposure, LTR/OBFF behavior, and D-state/suspend/resume restoration.
- Exercise GPU reset and FLR paths and confirm endpoint interrupt status, downstream control, and PCI configuration state remain coherent after recovery.
- Validate link training across supported speeds and widths, including Gen4/16 GT/s equalization, lane error reporting, and lane margining status where diagnostics expose it.
- For virtualization-capable configurations, test SR-IOV/GPUIOV function exposure, VF aperture sizing, PASID/page-request capabilities, requester IDs, and per-function reset/interrupt behavior.
- For firmware/BIOS handoff, compare strap-derived identity/capability fields and scratch registers against expected PCI-visible values after cold boot, warm reset, and resume.
