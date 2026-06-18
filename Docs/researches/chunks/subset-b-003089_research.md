# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 51557-54232

## Scope

This chunk covers 2,676 lines from the generated AMD NBIO 7.0 shift/mask header. It starts in the middle of the `PCIEMSIX_USB3_1` MSI-X table, at vector 10, and ends in the first few masks for `BIFPLR0_1_PCIE_L1_PM_SUB_CAP`. The covered source contains only preprocessor `#define` constants and register-name comments. There are no C functions, structs, enums, variables, branches, locks, allocations, or direct MMIO/SMN reads or writes in this range.

The chunk has two major regions:

- MSI-X table and pending-bit-array field masks for NBIF0 functions: USB3.1 vectors 10-31, complete MP2 vectors 0-31, complete GBE0 vectors 0-31, complete GBE1 vectors 0-31, and PBA masks for AMDGFX, PSP, USB3.0, USB3.1, MP2, GBE0, and GBE1.
- PCIe root-port/bridge configuration-space masks for `BIFPLR0_1`, beginning at standard PCI IDs and bridge command/status fields and continuing through PCI PM, PCIe, MSI, SSID, MSI map, vendor-specific, virtual-channel, device serial number, advanced error reporting, secondary PCIe, ACS, multicast, and L1 PM substate capability fields.

The last register family is split by the chunk boundary. Lines 54220-54232 include the shifts and the first four masks for `BIFPLR0_1_PCIE_L1_PM_SUB_CAP`; additional masks for that same register continue after this chunk.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 register interface. For each hardware register field, it provides a `__SHIFT` macro and a matching `_MASK` macro that AMDGPU register helpers can use to extract, compose, or update field values. The matching register addresses live in `nbio_7_0_offset.h`, and reset/default constants live in `nbio_7_0_default.h`.

In this chunk, the MSI-X definitions describe the layout of per-vector message address, data, and mask-bit registers for non-display NBIF functions. The PCIe `BIFPLR0_1` definitions describe PCI configuration-space fields exposed by the NBIO PCIe root port or bridge logic. The header itself is data, not behavior: it does not enable interrupts, retrain links, clear errors, or configure power management. It supplies the symbolic bit layout used by code that performs those actions elsewhere.

Although the repository path is under a Ceph/distributed-filesystem mirror, this source is part of the mirrored Linux AMD GPU driver tree and is unrelated to Ceph filesystem logic.

## Register Families Covered

The MSI-X table section uses a regular four-register pattern per vector:

- `*_ADDR_LO`: low message address bits, with `MSG_ADDR_LO` shifted by 2 and masked by `0xFFFFFFFC`, preserving PCI MSI/MSI-X 4-byte alignment.
- `*_ADDR_HI`: high 32 message address bits, full-width mask `0xFFFFFFFF`.
- `*_MSG_DATA`: full-width message payload mask `0xFFFFFFFF` for the MSI-X table entries in this header.
- `*_CONTROL`: `MASK_BIT` at bit 0 with mask `0x00000001`.

The covered vector table ranges are:

- `PCIEMSIX_USB3_1_PCIEMSIX_VECT10` through `VECT31`; vectors 0-9 are in the previous chunk.
- `PCIEMSIX_MP2_PCIEMSIX_VECT0` through `VECT31`.
- `PCIEMSIX_GBE0_PCIEMSIX_VECT0` through `VECT31`.
- `PCIEMSIX_GBE1_PCIEMSIX_VECT0` through `VECT31`.

The MSI-X PBA section provides a single `PENDING_BITS` field for each function's pending-bit array:

- `PCIEMSIX_AMDGFX_PCIEMSIX_PBA`
- `PCIEMSIX_PSP_PCIEMSIX_PBA`
- `PCIEMSIX_USB3_0_PCIEMSIX_PBA`
- `PCIEMSIX_USB3_1_PCIEMSIX_PBA`
- `PCIEMSIX_MP2_PCIEMSIX_PBA`
- `PCIEMSIX_GBE0_PCIEMSIX_PBA`
- `PCIEMSIX_GBE1_PCIEMSIX_PBA`

Each PBA field starts at bit 0 and uses a full 32-bit mask. This exposes pending interrupt status words, not per-vector table programming fields.

The `BIFPLR0_1` section starts at `addressBlock: nbio_pcie0_bifplr0_cfgdecp` and covers a large PCIe bridge/root-port configuration-space map:

- Standard PCI identity and bridge fields: vendor/device ID, command/status, revision/class, cache-line/latency/header/BIST, primary/secondary/subordinate bus numbers, I/O and memory base/limit windows, secondary status, bridge control, extended bridge control, capability pointer, and interrupt line/pin.
- PCI power-management capability: PM capability list, PM capability bits, and PM status/control.
- PCIe capability: capability header, device/link/slot/root capability, control, and status registers, including Max Payload Size, Max Read Request Size, link speed/width, retrain/disable/common-clock bits, slot interrupt/presence/power controls, PME/root error controls, and PCIe Capability 2 fields.
- MSI capability and MSI mapping: MSI enable, multiple-message controls, 64-bit support, per-vector masking capability, message address/data fields, MSI map capability, and MSI map base address fields.
- Subsystem ID and vendor-specific enhanced capability scratch registers.
- Virtual Channel enhanced capability: port VC capability/control/status, VC0 and VC1 resource capability/control/status, TC-to-VC maps, arbitration load/select fields, VC IDs, and enable/status bits.
- Device serial number enhanced capability: low and high 32-bit serial number fields.
- Advanced Error Reporting: uncorrectable status, mask, and severity bitfields; correctable status and mask; AER capability/control; header log and TLP prefix log registers; root error command/status; and error source ID.
- Secondary PCIe capability: link control 3, lane error status, and per-lane equalization control registers for lanes 0-15.
- Access Control Services capability/control: source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, and direct translated P2P fields.
- Multicast enhanced capability: maximum/enabled group count, ECRC regeneration support, multicast base address, receive/block vectors, untranslated-block vectors, and overlay BAR fields.
- L1 PM Substates capability list and the beginning of L1 PM substate capability fields.

## Important APIs, Types, and Functions

There are no callable APIs or C types in this range. The public interface is the macro naming convention consumed by AMDGPU register helpers:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Callers typically pair these masks with register offsets from `nbio_7_0_offset.h` and helper macros such as field extraction or read-modify-write helpers. The macros in this chunk are especially sensitive to register width and access type because many fields represent architected PCI configuration-space semantics:

- `BIFPLR0_1_COMMAND` controls I/O, memory, bus mastering, SERR, parity response, and legacy interrupt disable behavior.
- `BIFPLR0_1_STATUS` and `BIFPLR0_1_SECONDARY_STATUS` expose sticky/error status bits that may be clear-on-write-one in PCI config semantics.
- `BIFPLR0_1_IRQ_BRIDGE_CNTL` includes `SECONDARY_BUS_RESET`, a bit with destructive reset implications for downstream devices.
- `BIFPLR0_1_LINK_CNTL` and `BIFPLR0_1_LINK_CNTL2` expose link retraining, link disable, target speed, compliance, deemphasis, and autonomous speed control fields.
- `BIFPLR0_1_DEVICE_CNTL`, `DEVICE_CNTL2`, `ROOT_CNTL`, and AER registers control error reporting, atomic operations, LTR, OBFF, TLP prefix blocking, and PME/root error handling.
- `BIFPLR0_1_PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY` share similar field names but have different meanings: live/sticky status, reporting mask, and fatal/nonfatal classification.
- `BIFPLR0_1_PCIE_LANE_*_EQUALIZATION_CNTL` repeats the same four 4-bit/3-bit preset fields across lanes 0-15 for downstream/upstream TX presets and RX preset hints.
- `BIFPLR0_1_PCIE_ACS_CNTL` and multicast control/vector registers can affect peer-to-peer routing and isolation assumptions used by IOMMU/VFIO/SR-IOV style consumers.

For MSI-X, the critical interface is the per-vector `CONTROL__MASK_BIT` and the address/data tuple. Programming flows must use the correct function prefix (`USB3_1`, `MP2`, `GBE0`, `GBE1`) and the correct vector number; the bit layout itself is uniform across the covered vectors.

## Control Flow

This header segment has no local control flow. It participates in external driver and firmware-facing flows that look like:

1. Code selects an NBIO 7.0 register offset from the matching offset header.
2. Code uses the shift/mask macro from this header to extract or update a field.
3. AMDGPU, power-management, display-resource, or platform initialization code performs the actual MMIO/SMN/config-space access.
4. Hardware state changes according to PCIe, MSI-X, NBIF, or NBIO semantics.

Likely external flows include:

- MSI-X setup, masking, and interrupt migration for USB3, MP2, and GBE functions integrated behind NBIF0.
- Pending interrupt inspection through PBA words.
- PCI bridge enumeration and resource-window programming for bus numbers, I/O windows, memory windows, and prefetchable memory windows.
- PCIe link initialization, speed selection, retraining, ASPM/L1 substate negotiation, and link diagnostics.
- Error reporting setup and handling through PCIe device status, root status, and AER status/mask/severity registers.
- ACS and multicast capability discovery/configuration for platform isolation and peer-to-peer routing.
- Power-management capability discovery and PME/LTR/OBFF policy programming.

Because the header provides only constants, ordering, polling, locking, and delay requirements are defined by the caller and by PCIe/NBIO hardware documentation.

## State and Persistence Behavior

The file stores no software state. It names hardware-visible register fields whose persistence depends on PCI configuration-space rules, NBIO reset domains, firmware ownership, and function power state.

The MSI-X table entries represent runtime interrupt state. Message address/data fields are normally programmed by OS PCI/MSI-X infrastructure or device-specific setup paths, and `MASK_BIT` controls whether a vector is masked. These values can be lost or reset across function reset, device reset, GPU reset, D3 transitions, or suspend/resume unless restored by the owning stack. The PBA fields expose pending interrupt bits; they should be treated as hardware status, not persistent configuration.

The PCIe bridge/root-port fields include a mix of:

- Immutable or firmware-initialized identity/capability fields such as vendor/device ID, class code, capability IDs, supported link speeds, ACS capability, multicast capability, and L1 PM substate support bits.
- OS-programmed configuration fields such as bus numbers, memory windows, command bits, bridge control, MSI settings, link control, device control, AER masks/severity, ACS control, multicast control, and L1 PM policy fields.
- Sticky status/error fields such as PCI status, secondary status, device status, link status, slot/root status, AER status, lane error status, and root error status.
- Command-like bits such as link retrain, secondary bus reset, arbitration-table load bits, PME/status clear behavior, and potential error-status clear-on-write-one bits.

The generated masks do not encode which fields are read-only, write-one-to-clear, self-clearing, reserved, firmware-owned, or hazardous to write during active traffic. Those semantics must come from PCIe specs, AMD hardware documentation, and the code paths that use the macros.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.0 register header set:

- `nbio_7_0_offset.h` for the corresponding register addresses and base-index constants.
- `nbio_7_0_default.h` for reset/default constants, including defaults for the MSI-X table entries and `BIFPLR0_1` registers.
- AMDGPU register helper macros that understand the `__SHIFT`/`_MASK` convention.

Direct include integration found in this tree:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c` includes `nbio_7_0_default.h`, `nbio_7_0_offset.h`, and `nbio_7_0_sh_mask.h` for generation-specific NBIO behavior.
- `drivers/gpu/drm/amd/amdgpu/soc15.c` includes the same NBIO 7.0 generated header trio during SOC15 platform setup.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h` includes the NBIO 7.0 generated headers for SMU10-era power-management code.
- Display resource files include `nbio_7_0_offset.h` for NBIO offsets; even when they do not include this mask header directly, offset/mask/default consistency still matters for cross-subsystem register access.

The macros may also be used indirectly by generated tables, register-dump tooling, debug paths, or helper macros where direct textual searches for a specific field name do not capture every consumer.

## Risks and Edge Cases

- The MSI-X vector table layout is highly repetitive. A generator or manual edit that shifts one vector's offset while leaving masks unchanged can compile cleanly but route interrupts to the wrong vector or function.
- The chunk starts at `PCIEMSIX_USB3_1_PCIEMSIX_VECT10_ADDR_LO`; vectors 0-9 for USB3.1 are outside this work item. Any per-function summary must be reconciled with the previous chunk.
- MSI-X `MSG_ADDR_LO` intentionally masks off the low two bits. Code that treats the field as a raw 32-bit value can incorrectly preserve or compare alignment bits.
- MSI-X table programming must coordinate with vector masking. Updating address/data while a vector is unmasked can race with live interrupts if callers do not follow PCI/MSI-X ordering rules.
- PBA words are pending status, not mask or enable words. Confusing PBA `PENDING_BITS` with vector `MASK_BIT` would lead to broken interrupt handling.
- PCI bridge resource-window fields split address bits across low and upper registers. Wrong mask pairing can truncate 64-bit prefetchable windows or 32-bit I/O base/limit values.
- PCI status and AER status fields may use sticky or write-one-to-clear behavior. Generic read-modify-write helpers can accidentally clear errors if they write status fields without preserving W1C semantics.
- `SECONDARY_BUS_RESET`, link disable, link retrain, compliance mode, VC load bits, and similar command fields can disrupt active devices or links if written casually.
- `BIFPLR0_1_PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY` have similar bit positions but different semantics. Copying a mask from one family into another may silently change whether an error is reported, classified, or cleared.
- Lane equalization controls repeat over lanes 0-15. Off-by-one lane indexing can be difficult to detect in source review and may appear only as link training instability on specific lane widths.
- ACS and multicast fields affect isolation/routing. Incorrect ACS capability or control masks can affect peer-to-peer DMA assumptions, IOMMU grouping, VFIO assignment, or SR-IOV-style isolation.
- The L1 PM substate capability definition is incomplete in this chunk. The merge lane must include line 54233 and later to avoid reporting only four of the capability masks.
- Cross-generation similarity is not identity. Nearby NBIO 7.2/7.7 headers contain matching `BIFPLR0_1` names, but some later generations add fields such as `LINK_ACTIVATION_SUPPORTED`; consumers must use the header for the actual ASIC generation.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.0, SOC15, SMU10 power management, MSI/MSI-X, PCIe AER, ASPM, ACS, and display resource paths. This catches missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: every field should have the expected shift/mask, every covered register should have a matching offset entry, and defaults should exist where the database defines them.
- Validate MSI-X table sequence continuity for USB3.1, MP2, GBE0, and GBE1: four registers per vector, vectors 0-31 where complete, `MSG_ADDR_LO` mask `0xFFFFFFFC`, full-width address/data masks, and bit-0 mask control.
- Validate PBA definitions for AMDGFX, PSP, USB3.0, USB3.1, MP2, GBE0, and GBE1: `PENDING_BITS` at shift 0 with a full 32-bit mask.
- Exercise interrupt setup and teardown on hardware using the NBIO 7.0 generation: MSI-X enable/disable, vector masking/unmasking, interrupt delivery under load, suspend/resume restore, GPU reset restore, and error paths where pending bits are visible.
- Exercise PCIe link behavior on affected hardware: negotiated width/speed, Gen speed changes, link retrain, ASPM/L1 substate enablement, warm reset, hot reset, and recovery after GPU reset.
- Exercise PCIe error reporting: inject or observe correctable and uncorrectable errors where supported, verify AER status/mask/severity handling, root error command/status behavior, and status clearing semantics.
- Check bridge enumeration and resource programming through `lspci -vv` or equivalent diagnostics: bus numbers, memory and prefetchable windows, command/status bits, MSI capability, PCIe capability, ACS capability, VC capability, multicast capability, and L1 PM substate capability should decode coherently.
- Validate ACS/IOMMU grouping and peer-to-peer behavior on platforms that expose these root-port fields, especially for virtualization or passthrough use cases.
- Include cross-chunk validation at boundaries: USB3.1 vectors 0-9 are before this chunk, and the remaining `BIFPLR0_1_PCIE_L1_PM_SUB_CAP` masks continue after this chunk.

## Unresolved Cross-Chunk References

The previous chunk is needed for the beginning of the `PCIEMSIX_USB3_1` MSI-X table, including vectors 0-9. This chunk contains vectors 10-31.

The next chunk is needed to complete `BIFPLR0_1_PCIE_L1_PM_SUB_CAP`; this chunk ends after the masks for `PCI_PM_L1_2_SUPPORTED`, `PCI_PM_L1_1_SUPPORTED`, `ASPM_L1_2_SUPPORTED`, and `ASPM_L1_1_SUPPORTED`, while later masks such as `L1_PM_SUB_SUPPORTED`, restore time, power-on scale, and power-on value continue after line 54232.
