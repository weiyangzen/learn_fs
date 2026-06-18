# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 65944-68351

## Purpose

This chunk is a generated AMDGPU NBIO 7.7.0 register field map for the `BIFPLR1_0` PCI/PCIe logical root-port/bridge configuration space. It contains C preprocessor constants only: each register block is introduced by a comment and then exposes `__SHIFT` and `MASK` macros for individual bitfields. Kernel code that needs to compose, decode, or update NBIO/PCIe configuration registers includes this header together with address-register headers and AMDGPU register access helpers.

The chunk starts inside the `BIFPLR1_0_HEADER` definitions and then covers classic PCI bridge config registers, PCI power-management and PCIe capabilities, MSI, PCIe extended capabilities, AER/DPC/error logging, ACS and multicast controls, L1 PM substate controls, data-link and PHY capabilities, lane equalization/margining, CCIX/ESM fields, and 20 GT lane presets.

## Important APIs, Types, and Data Definitions

There are no functions, structs, enums, or runtime APIs in this section. The public surface is macro constants of the form:

- `BIFPLR1_0_<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `BIFPLR1_0_<REGISTER>__<FIELD>_MASK`: bit mask for the field.

Major register families in this chunk:

- PCI bridge/config header fields: BIST, bus numbers and latency, I/O and memory base/limit windows, prefetchable memory upper/base/limit, capability pointer, ROM base address, interrupt line/pin, extension bridge control, subsystem IDs, and vendor capability list.
- PCI PM capability: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` define power state, PME enable/status, D-state support, auxiliary current, B2/B3 support, bus power enable, and PM data fields.
- PCIe core capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_*`, `ROOT_*`, and second-generation `DEVICE_CAP2/CNTL2/STATUS2`, `LINK_CAP2/CNTL2/STATUS2`, and `SLOT_*2` fields.
- MSI and subsystem capability: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, address/data registers, `SSID_CAP_LIST`, `SSID_CAP`, and MSI mapping capability fields.
- PCIe vendor-specific and virtual-channel capabilities: enhanced capability list headers, vendor-specific registers, port VC capability/control/status, and VC0/VC1 resource capability/control/status.
- Device serial number and AER: serial-number dwords, advanced error reporting capability list, uncorrectable/correctable error status, masks, severity controls, AER capability/control, TLP header/prefix logs, root error command/status, and error source IDs.
- Secondary PCIe capability and equalization: link control 3, lane error status, and lane 0-15 PCIe equalization controls with downstream/upstream TX presets and RX preset hints.
- ACS and multicast: access-control services capability/control bits and multicast group, address, receive, block, untranslated-block, and overlay BAR fields.
- L1 PM substates: capability/control registers for PCI-PM L1.1/L1.2, ASPM L1.1/L1.2, common-mode restore time, LTR threshold, and power-on timing.
- Downstream Port Containment and root-port PIO: DPC capability/control/status/error-source fields, RP PIO status/mask/severity/system-error/exception fields, and PIO header/prefix logs.
- ESM/DLF/PHY/margining/CCIX: PCIe ESM capability/status/control and rate-capability bitmaps, data-link feature capability/status, 16 GT PHY capability/link/equalization/parity controls, PCIe lane margining port/lane controls and statuses, CCIX capability headers/status/control, required/optional ESM capability fields, and 20 GT ESM per-lane TX preset controls.

## Control Flow and Behavior

This header chunk has no executable control flow. Its behavior is indirect: C code reads a hardware register, applies a `MASK`, shifts by the paired `SHIFT`, and interprets or writes the field value. Write paths usually preserve unrelated bits by masking, then OR in `(value << SHIFT) & MASK`.

The field layout encodes hardware state-machine interactions visible to drivers:

- Link training and link management are represented by `LINK_CNTL`/`LINK_STATUS`, `LINK_CNTL2`/`LINK_STATUS2`, `PCIE_LINK_CNTL3`, lane error status, and lane equalization registers.
- Power transitions are represented by PM capability/status fields, ASPM fields, and L1 PM substate controls.
- Error handling is represented by PCIe device status, AER uncorrectable/correctable status/mask/severity, root error reporting, DPC status/control, and RP PIO logs.
- Per-lane operations are repetitive register layouts for lanes 0-15, allowing code to index lane-specific register addresses elsewhere while using identical field layouts for presets or margining payloads.

## State and Persistence

The macros themselves have no state. The state lives in NBIO/PCIe hardware registers and, for some status/log registers, persists until firmware, hardware, or the kernel clears it according to the register semantics.

Important state categories exposed here:

- Configuration windows: I/O, memory, prefetchable memory, ROM base, bus number, and subsystem fields describe bridge-visible address routing and identity.
- Runtime enable bits: PM/PME, MSI, ACS, multicast, DPC, L1 substate, link equalization, CCIX ESM, and lane margining controls alter hardware behavior when written.
- Latched status and logs: PCI/PCIe device status, link status, slot status, root status, AER logs, DPC/RP PIO status, parity mismatch status, data-link status, margining status, and CCIX ESM calibration status are diagnostic state surfaces.
- Capability descriptors: `*_CAP`, `*_CAP_LIST`, and `*_ENH_CAP_LIST` fields describe hardware support and capability-chain placement, normally treated as read-only by generic PCI/PCIe code.

## Dependencies and Integration Points

This chunk depends on consumers using the matching NBIO 7.7.0 address definitions and AMDGPU register helpers. In the broader driver tree it integrates with:

- AMDGPU NBIO code that programs PCIe/bridge behavior for AMD ASICs.
- PCI/PCIe capability handling paths that need ASIC-specific bit positions beyond generic Linux PCI constants.
- Interrupt setup through MSI message control/address/data fields.
- Power management and runtime suspend/resume flows through PM, ASPM, L1 PM substate, and ESM controls.
- Error detection/recovery paths through AER, DPC, root-port PIO, parity mismatch, and lane error status fields.
- Link bring-up, retraining, equalization, lane margining, and high-speed PHY tuning through link-control, lane-preset, 16 GT, 20 GT, and CCIX ESM definitions.

Because the section is generated register metadata, its main contract is naming and bit-accuracy. Callers rely on these exact macro names when building register values; there is no type checking around field width or valid enumeration values.

## Risks and Edge Cases

- Bitfield drift is high-impact: a wrong shift or mask can silently program the wrong PCIe control bit, affecting link stability, power states, interrupt routing, or error containment.
- Many fields are status/log or write-one-to-clear in real hardware even though the header does not encode access semantics. Callers must know whether a bit is read-only, RW, RW1C, sticky, or reserved from the hardware spec or surrounding driver code.
- Repeated lane definitions invite copy/paste or generator errors. Lanes 0-15 should remain structurally identical except for the lane number; incomplete coverage would break x16 links or diagnostics.
- Some macro names intentionally contain repeated words, for example mask fields such as `...__DLP_ERR_MASK_MASK`, because the register field itself is named `*_MASK`. Consumers should not "simplify" these names.
- Capability-list `NEXT_PTR` and `CAP_ID` fields are part of PCI/PCIe capability chains. Incorrect values or wrong decoding can make downstream code skip or misidentify capabilities.
- Advanced link features such as DPC, ACS, multicast, L1 PM substates, ESM, CCIX, margining, and 16/20 GT presets are hardware- and platform-sensitive; writing unsupported values can produce link retraining failures or hidden performance regressions.
- The constants use `L` suffixed integer literals. Consumers should ensure register operations use appropriately sized unsigned types to avoid sign or width surprises with high-bit masks such as `0x80000000L`.

## Test and Validation Signals

Useful validation for this chunk is mostly static plus hardware-observable:

- Build coverage: compile AMDGPU targets that include `nbio_7_7_0_sh_mask.h` and verify all referenced `BIFPLR1_0_*` macros resolve.
- Generator consistency: compare the macro set against the authoritative NBIO 7.7.0 register database, especially contiguous repeated lane blocks and capability-chain headers.
- Static pattern checks: for every field, verify `MASK` width and `SHIFT` agree; for lane 0-15 blocks, verify identical field layouts and masks.
- Runtime smoke tests on matching ASICs: enumerate PCI/PCIe capabilities, train links at expected width/speed, enable MSI, exercise suspend/resume, and confirm no AER/DPC regressions.
- Diagnostics: read AER/DPC/link/margining status registers under stress or fault injection and confirm decoded fields match kernel logs and PCIe expectations.

## Chunk-Specific Notes for Merge

This chunk is only one section of the full header. The final file-level report should merge it with surrounding chunks that likely define earlier/later NBIO registers and the address macros that pair with these field masks. No final per-file report was written here by design.
