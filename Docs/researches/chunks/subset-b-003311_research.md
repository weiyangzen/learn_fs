# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 125594-127985

## Scope

This chunk covers lines 125594-127985 of AMDGPU's generated NBIO 7.7.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, persistence code, or direct register accesses.

The range starts in the middle of `BIFPLR2_2_PCIE_ESM_CAP_5`, continues through `BIFPLR2_2_PCIE_ESM_CAP_6`, `BIFPLR2_2_PCIE_ESM_CAP_7`, and the 16 GT/s and 32 GT/s link capability/control/status extension fields for `BIFPLR2_2`. It then covers the complete `addressBlock: nbio_pcie0_bifplr3_cfgdecp` register-field map from `BIFPLR3_2_VENDOR_ID` through `BIFPLR3_2_LINK_STATUS_32GT`. The final section begins `addressBlock: nbio_pcie0_bifplr4_cfgdecp` and reaches the middle of `BIFPLR4_2_PMI_STATUS_CNTL`.

Although this repository path sits under a `ceph-client` source tree mirror, the content is AMD GPU NBIO/PCIe register metadata. It has no Ceph or distributed-filesystem runtime behavior.

## Purpose

`nbio_7_7_0_sh_mask.h` is the bitfield-definition companion to the NBIO 7.7.0 register map. Each macro provides one of two pieces of hardware field geometry:

- `REGISTER__FIELD__SHIFT`: the least-significant bit index of the field.
- `REGISTER__FIELD_MASK`: the field mask in the containing register.

The definitions let AMDGPU code use symbolic PCIe/NBIO field names instead of literal bit positions while reading, decoding, or updating ASIC registers through generated offset headers and driver register helpers. This chunk is focused on PCIe root-port/bridge-style configuration decode blocks named `BIFPLR*_2`, with `BIFPLR3_2` fully represented and `BIFPLR2_2`/`BIFPLR4_2` partial at the range boundaries.

## Important Definitions

The opening `BIFPLR2_2` portion completes part of the PCIe Enhanced Speed Mode capability bitmap and link extension fields:

- `BIFPLR2_2_PCIE_ESM_CAP_5`, `_CAP_6`, and `_CAP_7` define bitmaps for advertised ESM rates. The chunk begins at `ESM_19P0G` fields and continues through rates up to `ESM_28P0G`.
- `BIFPLR2_2_LINK_CAP_16GT`, `LINK_CNTL_16GT`, and `LINK_STATUS_16GT` expose Gen4/16 GT/s style fields such as equalization-complete status, equalization phase success, link-equalization request, and downstream/upstream component presence.
- `BIFPLR2_2_LINK_CAP_32GT`, `LINK_CNTL_32GT`, and `LINK_STATUS_32GT` expose Gen5/32 GT/s fields for equalization bypass, modified TS usage, lane equalization control, equalization complete/phase status, link-flap status, precoding status, retimer presence, and downstream/upstream component presence.

The central `BIFPLR3_2` address block is a full PCIe bridge/root-port-style configuration-space map:

- Standard PCI/bridge header fields: vendor/device ID, command/status, revision/class code, cache line, latency, header type, BIST, primary/secondary/subordinate bus numbers, I/O and memory base/limit fields, prefetchable base/limit upper/lower fields, capability pointer, interrupt line/pin, and extended bridge control.
- Power management capability: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` cover capability IDs, next pointers, power state, PME enable/status, D-state support, data select/scale, auxiliary current, bus-power enable, and PMI data.
- PCIe capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS`.
- PCIe capability 2 / Gen2+ fields: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`.
- Interrupt and identification capabilities: MSI capability list/control/address/data fields, subsystem ID capability, MSI map capability, and vendor-specific enhanced capability fields.
- Virtual Channel support: VC enhanced capability header, port VC capability/control/status, and VC0/VC1 resource capability/control/status fields including TC-to-VC maps, arbitration controls, VC IDs, and enable/status bits.
- Device serial number and AER: serial-number enhanced capability, AER uncorrectable/correctable status/mask/severity fields, AER capability/control, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe and lane training: secondary PCIe capability header, link control 3, lane error status, and lane 0-15 equalization controls with downstream/upstream TX preset and RX preset-hint fields.
- Isolation, multicast, and low-power/error containment extensions: ACS capability/control, multicast capability/control/address/receive/block/overlay fields, L1 PM substate capability/control fields, Downstream Port Containment capability/control/status/error-source fields, and Root Port PIO status/mask/severity/system-error/exception/log fields.
- PCIe ESM and high-speed link extensions: ESM capability list/header/status/control, ESM rate bitmaps from `PCIE_ESM_CAP_1` through `_CAP_7`, and 16 GT/s / 32 GT/s link capability/control/status fields.

The closing `BIFPLR4_2` portion begins the next PCIe bridge/root-port-style configuration block:

- It covers the standard identity/header/resource-window fields from `VENDOR_ID` through `EXT_BRIDGE_CNTL`.
- It includes PM capability list and PM capability fields.
- It ends inside `BIFPLR4_2_PMI_STATUS_CNTL`; later fields in that register and the rest of the `BIFPLR4_2` capability chain are outside this chunk.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this range. The exported interface is the generated macro namespace. Consumers combine these macros with matching NBIO 7.7.0 generated register-address/default headers and AMDGPU register access helpers such as field extraction/composition macros and MMIO, SMN, or PCI configuration accessors.

The macros encode only bit positions and masks. They do not encode reset values, read/write permissions, volatility, write-one-to-clear behavior, firmware ownership, required ordering, or whether a field has side effects when written.

## Control Flow

This header has no local runtime control flow. Runtime use is external and generally follows this pattern:

1. Driver code selects the appropriate NBIO 7.7.0 register offset or address for a `BIFPLR*_2` block.
2. It reads the register through the AMDGPU register access path selected for that block.
3. It decodes a field with the corresponding `__SHIFT` and `_MASK`, or composes a read-modify-write value while preserving unrelated bits.
4. Hardware applies the PCIe/NBIO semantics: bridge-window programming, link training, interrupt delivery, AER reporting, ACS policy, virtual-channel routing, DPC handling, L1 PM substates, multicast routing, ESM capability exposure, or high-speed link status.

The order in the file follows the generated register database rather than an execution sequence. Similar field names in status, mask, severity, and control registers can represent different operations even when they share bit positions.

## State And Persistence Behavior

The chunk owns no software state and persists nothing. It names fields whose state lives in NBIO hardware registers and PCIe configuration-space decode/shadow registers. Persistence is determined by PCIe reset rules, GPU/NBIO reset domains, firmware initialization, function-level reset, runtime power transitions, suspend/resume restore, and explicit driver writes.

Represented hardware state includes:

- Configuration state: PCI command bits, bus-master/memory/I/O enables, bridge bus numbers, resource windows, interrupt disable, PM state, PME enable, link control, slot/root controls, MSI controls, VC controls, ACS controls, multicast controls, L1 PM controls, DPC controls, RP PIO masks, ESM controls, and 16 GT/s/32 GT/s link controls.
- Capability and identity state: vendor/device/class IDs, capability IDs and next pointers, device/link/slot/root capabilities, serial number, AER capability, ACS and multicast capabilities, L1 PM support, DPC support, ESM rate bitmaps, and high-speed link capability bits.
- Status and diagnostic state: PCI status, secondary status, PM status, device/link/slot/root status, VC status, AER error status, header/TLP prefix logs, lane error status, DPC status/error source, RP PIO status and logs, ESM status, and 16 GT/s/32 GT/s link equalization status.

Because this file supplies only masks and shifts, callers must use hardware documentation and local AMDGPU policy to distinguish read-only fields from writable fields, sticky status from ordinary status, and reserved bits from programmable bits.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.7.0 register-header set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h` supplies the matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_default.h` supplies reset/default values where generated.
- AMDGPU NBIO/SOC platform code includes the generated NBIO headers and uses the common shift/mask naming convention through register helper macros.

Practical integration points are PCIe/GPU platform behavior rather than filesystem behavior: GPU enumeration, PCI bridge/resource setup, power management, MSI delivery, AER and DPC error recovery, ACS/IOMMU isolation, virtual-channel configuration, PCIe multicast, L1 PM substates, root-port PIO diagnostics, link training/equalization, Gen4/Gen5 status reporting, ESM capability advertisement, reset recovery, and debug register dumps.

## Risks And Edge Cases

- The range starts and ends mid-register-family. `BIFPLR2_2_PCIE_ESM_CAP_5` begins before this chunk, and `BIFPLR4_2_PMI_STATUS_CNTL` continues after it. The final per-file merge must reconcile adjacent chunks before drawing whole-register conclusions.
- A wrong generated shift or mask can compile cleanly while reading or writing the wrong PCIe configuration bit, corrupting adjacent status, disabling decode, breaking interrupts, changing error policy, or misreporting link capability.
- PCI status, secondary status, device/link/slot/root status, AER status, DPC status, RP PIO status, lane error status, and similar fields may be sticky or write-one-to-clear. Generic read-modify-write code can accidentally clear diagnostics if it writes status registers without W1C-aware handling.
- AER status, mask, and severity registers intentionally reuse many bit names. Copying code between those groups can change reporting, suppression, fatality classification, or clearing behavior.
- ACS controls affect peer-to-peer routing and isolation. Incorrect use can affect IOMMU grouping, VFIO/passthrough assumptions, peer DMA policy, or virtualization boundaries.
- DPC, RP PIO, root-error command/status, and link retrain/equalization fields are operationally sensitive. Misprogramming can turn recoverable PCIe errors into link resets, suppress required notifications, or destabilize active links.
- `BIFPLR2_2`, `BIFPLR3_2`, and `BIFPLR4_2` have repeated, similar register names. Prefix mix-ups may not be caught by the compiler if both prefixes exist, but can target the wrong root port or bridge decode block.
- ESM and 16 GT/s/32 GT/s link-extension fields are speed-generation specific. Treating them like older PCIe link fields can misread equalization, retimer, precoding, or link-flap state.
- Reserved masks appear in several capability/control groups. Writers should preserve reserved bits unless authoritative hardware documentation explicitly permits a write.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.7.0 support. Compile failures catch malformed generated symbols or mismatches between generated headers and driver users.
- Run generated-header consistency checks against the authoritative NBIO 7.7.0 register database: each field should have the expected shift/mask, each register should have a matching offset, and defaults should match where present.
- Cross-check repeated `BIFPLR*_2` families, especially `BIFPLR3_2` versus `BIFPLR4_2`, for consistent standard PCI, PM, PCIe, AER, ACS, DPC, ESM, and high-speed link layouts where the hardware specification says they should match.
- Validate PCIe enumeration on matching hardware with diagnostics such as `lspci -vv`: vendor/device/class IDs, bridge windows, bus numbers, capability chain pointers, PM/PCIe/MSI/AER/ACS/DPC/L1 PM/ESM capabilities, and link capabilities should decode coherently.
- Exercise MSI setup, interrupt disable paths, PM state transitions, suspend/resume, and GPU reset recovery to confirm fields represented here are preserved, restored, or reinitialized as expected.
- Exercise PCIe link behavior at supported speeds: negotiated width/speed, Gen4/Gen5 equalization status, retimer and precoding status, link retraining, lane error reporting, ESM rate advertisement, and recovery after link flap.
- Exercise AER, DPC, and RP PIO paths where available: correctable/uncorrectable status, masks, severity, header logs, TLP prefix logs, root error source IDs, containment status, and clearing behavior should match PCIe semantics.
- Validate ACS/IOMMU and peer-to-peer DMA behavior on systems exposing these root-port blocks, especially for passthrough or virtualization scenarios.
